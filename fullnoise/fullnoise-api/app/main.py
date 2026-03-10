"""
FullNoise AI — FastAPI backend.
Endpoints: health, clients, send-report, ask, resend-report, webhooks/resend/inbound.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin, require_client
from app.database import get_db
from app.db_init import init_db
from app.models import Client, Lead, Question, Report
from app.queue import enqueue_send_report
from app.services.ask import answer_question
from app.services.email import send_report_email, send_reply_email
from app.config import FRONTEND_URL

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="FullNoise AI API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Schemas ---

class ClientCreate(BaseModel):
    name: str
    email: EmailStr


class AskBody(BaseModel):
    message: str


class ContactBody(BaseModel):
    name: str
    email: EmailStr
    message: str = ""


class InboundTestBody(BaseModel):
    """Simulate reply-to-email for local testing (no Resend email_id needed)."""
    from_email: EmailStr
    subject: str = "Report"
    text: str = ""


# --- Health ---

@app.get("/health")
async def health():
    return {"status": "ok", "service": "fullnoise-api"}


# --- Contact (public) ---

@app.post("/contact")
async def contact(body: ContactBody, db: AsyncSession = Depends(get_db)):
    """Store lead and optionally email to CONTACT_EMAIL_TO."""
    from app.config import CONTACT_EMAIL_TO
    lead = Lead(name=body.name.strip()[:200], email=body.email.strip().lower()[:200], message=(body.message or "")[:2000])
    db.add(lead)
    await db.flush()
    if CONTACT_EMAIL_TO:
        from app.services.email import send_report_email
        send_report_email(
            CONTACT_EMAIL_TO,
            f"FullNoise AI — Lead: {lead.name}",
            f"Name: {lead.name}\nEmail: {lead.email}\n\nMessage:\n{lead.message}",
        )
    return {"ok": True}




# --- Admin login (returns JWT for NextAuth) ---

class AdminLoginBody(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/admin-login")
async def admin_login(body: AdminLoginBody):
    from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
    from jose import jwt
    from app.config import NEXTAUTH_SECRET
    if body.email.strip().lower() != ADMIN_EMAIL or body.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    payload = {"role": "admin", "sub": "admin", "email": body.email}
    token = jwt.encode(payload, NEXTAUTH_SECRET, algorithm="HS256")
    return {"token": token}


# --- Magic link (client login) ---

class SendMagicLinkBody(BaseModel):
    email: EmailStr

@app.post("/auth/send-magic-link")
async def send_magic_link(body: SendMagicLinkBody, db: AsyncSession = Depends(get_db)):
    """Send magic link email to client. No auth required."""
    from app.magic_link import create_token
    from app.config import FRONTEND_URL
    result = await db.execute(select(Client).where(Client.email == body.email.strip().lower()))
    client = result.scalars().first()
    if not client:
        return {"ok": True}  # Don't leak existence
    token = create_token(client.id, client.email)
    link = f"{FRONTEND_URL.rstrip('/')}/app/verify?token={token}"
    body_text = f"Sign in to FullNoise AI:\n\n{link}\n\nThis link expires in 1 hour."
    err = send_report_email(client.email, "Sign in to FullNoise AI", body_text)
    if err:
        raise HTTPException(status_code=500, detail="Failed to send email")
    return {"ok": True}

@app.get("/auth/verify")
async def verify_magic_link(token: str, db: AsyncSession = Depends(get_db)):
    """Verify magic link token; return JWT for NextAuth (role=client, client_id)."""
    from app.magic_link import verify_token
    from jose import jwt
    from app.config import NEXTAUTH_SECRET
    data = verify_token(token)
    if not data:
        raise HTTPException(status_code=400, detail="Invalid or expired link")
    result = await db.execute(select(Client).where(Client.id == data["client_id"]))
    client = result.scalars().first()
    name = client.name if client else ""
    payload = {"role": "client", "client_id": data["client_id"], "email": data["email"], "sub": data["client_id"]}
    jwt_token = jwt.encode(payload, NEXTAUTH_SECRET, algorithm="HS256")
    return {"token": jwt_token, "client_id": data["client_id"], "name": name}


# --- Client lookup by email (for NextAuth JWT callback; server-only with secret) ---

@app.get("/clients/by-email")
async def get_client_by_email(
    email: str,
    x_server_secret: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
):
    """Return client_id and name for the given email. Used by Next.js to build JWT. Require X-Server-Secret = NEXTAUTH_SECRET."""
    from app.config import NEXTAUTH_SECRET
    if not email or x_server_secret != NEXTAUTH_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    result = await db.execute(select(Client).where(Client.email == email.strip().lower()))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="No client with this email")
    return {"client_id": client.id, "name": client.name}


# --- Admin: clients ---

@app.get("/clients")
async def list_clients(
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).order_by(Client.name))
    clients = result.scalars().all()
    return {
        "clients": [
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "last_report_sent_at": c.last_report_sent_at.isoformat() if c.last_report_sent_at else None,
            }
            for c in clients
        ]
    }


@app.post("/clients")
async def create_client(
    body: ClientCreate,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).where(Client.email == body.email.strip().lower()))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Client with this email already exists")
    client = Client(name=body.name.strip(), email=body.email.strip().lower())
    db.add(client)
    await db.flush()
    await db.refresh(client)
    return {"id": client.id, "name": client.name, "email": client.email}


# --- Admin: send report (enqueue job) ---

class SendReportBody(BaseModel):
    client_id: str

@app.post("/send-report")
async def send_report(
    body: SendReportBody,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    client_id = body.client_id
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    ok = await enqueue_send_report(client_id)
    if not ok:
        raise HTTPException(status_code=503, detail="Queue unavailable")
    return {"ok": True, "message": "Report job queued"}


# --- Client: ask question ---

@app.post("/ask")
async def ask(
    body: AskBody,
    payload: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    client_id = payload["client_id"]
    question_text = (body.message or "").strip()[:2000]
    if not question_text:
        raise HTTPException(status_code=400, detail="Empty message")

    result = await db.execute(select(Report).where(Report.client_id == client_id).order_by(Report.created_at.desc()).limit(1))
    latest = result.scalars().first()
    context = f"Month: {latest.month}, Revenue: ${latest.revenue}, Costs: ${latest.costs}, Profit: ${latest.profit}, Jobs: {latest.jobs}. Summary: {latest.summary}" if latest else "No report yet."
    answer_text = answer_question(context, question_text)

    q = Question(client_id=client_id, question=question_text, answer=answer_text)
    db.add(q)
    await db.flush()
    return {"ok": True, "reply": answer_text}


# --- Client: resend latest report email ---

@app.post("/resend-report")
async def resend_report(
    payload: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    client_id = payload["client_id"]
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    result = await db.execute(select(Report).where(Report.client_id == client_id).order_by(Report.created_at.desc()).limit(1))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="No report to resend")

    body = f"""FullNoise AI — Monthly Report ({report.month})

Summary:
{report.summary}

Numbers:
• Revenue: ${report.revenue:,.2f}
• Costs: ${report.costs:,.2f}
• Profit: ${report.profit:,.2f}
• Jobs: {report.jobs}

Reply to this email with any question.

—
FullNoise AI
"""
    err = send_report_email(client.email, f"Your monthly report — {report.month}", body)
    if err:
        raise HTTPException(status_code=500, detail=err)
    return {"ok": True, "message": "Report sent"}


# --- Client: get latest report (for portal) ---

@app.get("/report")
async def get_latest_report(
    payload: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    client_id = payload["client_id"]
    result = await db.execute(select(Report).where(Report.client_id == client_id).order_by(Report.created_at.desc()).limit(1))
    report = result.scalars().first()
    if not report:
        return {"report": None}
    return {
        "report": {
            "id": report.id,
            "month": report.month,
            "revenue": float(report.revenue),
            "costs": float(report.costs),
            "profit": float(report.profit),
            "jobs": report.jobs,
            "summary": report.summary,
            "created_at": report.created_at.isoformat(),
        }
    }


# --- Webhook: Resend inbound email ---

@app.post("/webhooks/resend/inbound")
async def webhook_resend_inbound(request: Request):
    """Resend sends inbound emails here. We answer the question and reply by email."""
    import re
    try:
        body = await request.json()
        if body.get("type") != "email.received":
            return JSONResponse({"ok": True})

        data = body.get("data") or {}
        email_id = (data.get("email_id") or "").strip()
        if not email_id:
            return JSONResponse({"ok": True})

        import resend
        from app.config import RESEND_API_KEY
        from app.database import AsyncSessionLocal
        resend.api_key = RESEND_API_KEY
        received = resend.Emails.Receiving.get(email_id)
        if isinstance(received, dict):
            from_str = (received.get("from") or "").strip()
            subject = (received.get("subject") or "").strip()
            text = (received.get("text") or "").strip()
            message_id = (received.get("message_id") or "").strip()
        else:
            from_str = getattr(received, "from", "") or ""
            subject = getattr(received, "subject", "") or ""
            text = (getattr(received, "text", None) or "").strip()
            message_id = getattr(received, "message_id", "") or ""

        if not text and getattr(received, "html", None):
            text = re.sub(r"<[^>]+>", " ", (received.html or "")).strip()
        text = (text or "")[:4000]

        async with AsyncSessionLocal() as session:
            # Extract email from "Name <email@x.com>" if present
            email_lower = from_str.lower()
            if "<" in email_lower and ">" in email_lower:
                m = re.search(r"<([^>]+)>", email_lower)
                if m:
                    email_lower = m.group(1).strip()
            result = await session.execute(select(Client).where(Client.email == email_lower))
            client = result.scalars().first()
            if not client:
                return JSONResponse({"ok": True})

            result = await session.execute(select(Report).where(Report.client_id == client.id).order_by(Report.created_at.desc()).limit(1))
            latest = result.scalars().first()
            context = f"Month: {latest.month}, Revenue: ${latest.revenue}, Costs: ${latest.costs}, Profit: ${latest.profit}, Jobs: {latest.jobs}. Summary: {latest.summary}" if latest else "No report yet."
            reply_text = answer_question(context, text)
            to_addr = from_str
            if "<" in to_addr and ">" in to_addr:
                m = re.search(r"<([^>]+)>", to_addr)
                if m:
                    to_addr = m.group(1).strip()
            send_reply_email(to_addr, f"Re: {subject or 'Report'}", reply_text, in_reply_to=message_id or None)

        return JSONResponse({"ok": True})
    except Exception as e:
        import logging
        logging.getLogger("fullnoise.webhook").warning("inbound webhook error: %s", e, exc_info=True)
        return JSONResponse({"ok": True})


# --- Test: simulate reply-to-email (no Resend inbound needed) ---

@app.post("/webhooks/resend/inbound-test")
async def webhook_inbound_test(
    body: InboundTestBody,
    db: AsyncSession = Depends(get_db),
):
    """
    Test reply-to-email flow: same logic as real webhook but accepts from_email/subject/text
    in the request body (no Resend email_id). Use with a client email that exists and has a report.
    """
    import re
    from_str = body.from_email.strip()
    subject = (body.subject or "Report").strip()
    text = (body.text or "").strip()[:4000]
    if not text:
        return JSONResponse({"ok": False, "error": "text is required"}, status_code=400)

    email_lower = from_str.lower()
    if "<" in email_lower and ">" in email_lower:
        m = re.search(r"<([^>]+)>", email_lower)
        if m:
            email_lower = m.group(1).strip()

    result = await db.execute(select(Client).where(Client.email == email_lower))
    client = result.scalars().first()
    if not client:
        return JSONResponse({"ok": False, "error": "no client with that email"}, status_code=404)

    result = await db.execute(select(Report).where(Report.client_id == client.id).order_by(Report.created_at.desc()).limit(1))
    latest = result.scalars().first()
    context = f"Month: {latest.month}, Revenue: ${latest.revenue}, Costs: ${latest.costs}, Profit: ${latest.profit}, Jobs: {latest.jobs}. Summary: {latest.summary}" if latest else "No report yet."
    reply_text = answer_question(context, text)

    to_addr = from_str
    if "<" in to_addr and ">" in to_addr:
        m = re.search(r"<([^>]+)>", to_addr)
        if m:
            to_addr = m.group(1).strip()

    err = send_reply_email(to_addr, f"Re: {subject}", reply_text, in_reply_to=None)
    if err:
        return JSONResponse({"ok": False, "error": err}, status_code=500)
    return JSONResponse({"ok": True, "message": "reply sent"})
