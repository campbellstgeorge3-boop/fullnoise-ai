"""
Reply-by-email server: receives Resend webhooks for inbound emails,
answers using the chat agent, and sends the reply back by email.
Also serves the landing page (/) and admin dashboard (/dashboard).
Run: uvicorn chat_server:app --host 0.0.0.0 --port 8001
"""
import os
import re
import subprocess
import sys
from pathlib import Path


def _log(msg: str) -> None:
    print(f"[reply] {msg}", flush=True)
    sys.stderr.write(f"[reply] {msg}\n")
    sys.stderr.flush()

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

import hmac
import hashlib
import base64
from urllib.parse import quote

from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from chat_agent import answer, _trigger_send_report
from client_auth import create_magic_link_token, verify_magic_link_token
from clients import get_client, get_client_by_email, load_clients
from emailer import send_contact_lead, send_magic_link_email, send_reply_email
from report_saver import get_latest_report

app = __import__("fastapi").FastAPI(title="Boss Assistant Reply-by-Email")

# Dashboard auth: set DASHBOARD_PASSWORD in .env to protect /dashboard and /api/clients, /api/run-client
_security = HTTPBasic()
_ROOT = Path(__file__).resolve().parent


def _check_dashboard_auth(credentials: HTTPBasicCredentials | None = Depends(HTTPBasic(auto_error=False))) -> None:
    password = (os.environ.get("DASHBOARD_PASSWORD") or os.environ.get("CHAT_PASSWORD") or "").strip()
    if not password:
        return  # no password set => no auth
    if credentials is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Dashboard password required", headers={"WWW-Authenticate": "Basic"})
    import secrets
    if not secrets.compare_digest(credentials.password.encode("utf-8"), password.encode("utf-8")):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid password")


# Client portal session (signed cookie). Set SESSION_SECRET in .env.
_CLIENT_SESSION_COOKIE = "client_session"
_CLIENT_SESSION_MAX_AGE = 7 * 24 * 3600  # 7 days


def _session_secret() -> bytes:
    s = (os.environ.get("SESSION_SECRET") or "change-me-in-production").strip()
    return s.encode("utf-8")


def _sign_session(client_id: str) -> str:
    import time
    payload = f"{client_id}|{int(time.time()) + _CLIENT_SESSION_MAX_AGE}"
    sig = hmac.new(_session_secret(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{sig}".encode("utf-8")).decode("ascii")


def _verify_session(cookie_val: str) -> str | None:
    import time
    if not cookie_val or not cookie_val.strip():
        return None
    try:
        raw = base64.urlsafe_b64decode(cookie_val.strip().encode("ascii")).decode("utf-8")
        parts = raw.rsplit("|", 1)
        if len(parts) != 2:
            return None
        payload, sig = parts[0], parts[1]
        expected = hmac.new(_session_secret(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        client_id, exp = payload.rsplit("|", 1)
        if int(exp) < int(time.time()):
            return None
        return (client_id or "").strip() or None
    except Exception:
        return None


def _get_client_from_session(request: Request) -> str | None:
    cookie = request.cookies.get(_CLIENT_SESSION_COOKIE)
    return _verify_session(cookie or "")


@app.post("/api/inbound-email")
async def inbound_email(request: Request):
    """
    Resend webhook: when someone replies to the report email, we answer with the
    chat agent and send the reply back by email. No auth so Resend can POST.
    """
    try:
        body = await request.json()
        if not body:
            _log("webhook: empty body")
            return JSONResponse({"ok": False}, status_code=400)
        event_type = (body.get("type") or "").strip()
        _log(f"webhook: type={event_type!r}")
        if event_type != "email.received":
            return JSONResponse({"ok": True})

        data = body.get("data") or {}
        email_id = (data.get("email_id") or "").strip()
        if not email_id:
            _log("webhook: no email_id")
            return JSONResponse({"ok": True})

        api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
        if not api_key:
            _log("webhook: no RESEND_API_KEY")
            return JSONResponse({"ok": True})

        import resend
        resend.api_key = api_key
        _log(f"fetching email_id={email_id[:20]}...")
        received = resend.Emails.Receiving.get(email_id)
        if isinstance(received, dict):
            from_str = (received.get("from") or "").strip()
            subject = (received.get("subject") or "").strip()
            message_id = (received.get("message_id") or "").strip()
            text = (received.get("text") or "").strip()
            if not text and received.get("html"):
                html = received.get("html") or ""
                text = re.sub(r"<[^>]+>", " ", html).strip()
        else:
            from_str = getattr(received, "from", "") or ""
            subject = getattr(received, "subject", "") or ""
            message_id = getattr(received, "message_id", "") or ""
            text = (getattr(received, "text", None) or "").strip()
            if not text and getattr(received, "html", None):
                text = re.sub(r"<[^>]+>", " ", (received.html or "")).strip()
        text = (text or "No question.").strip()[:4000]
        _log(f"from={from_str!r} subject={subject!r} text_len={len(text)}")

        clients = load_clients()
        client = get_client_by_email(clients, from_str)
        if not client:
            _log(f"no client for from={from_str!r} (check clients.json email_to)")
            return JSONResponse({"ok": True})

        client_id = (client.get("id") or "").strip()
        if not client_id:
            _log("client has no id")
            return JSONResponse({"ok": True})

        _log(f"answering for client_id={client_id!r}")
        reply_text = answer(client_id, text)
        reply_subject = f"Re: {subject}" if subject else "Re: Report"
        to_addr = from_str
        if "<" in to_addr and ">" in to_addr:
            match = re.search(r"<([^>]+)>", to_addr)
            if match:
                to_addr = match.group(1).strip()
        err = send_reply_email(to_addr, reply_subject, reply_text, in_reply_to=message_id or None)
        if err:
            _log(f"send_reply_email failed: {err}")
        else:
            _log(f"reply sent to {to_addr!r}")
        return JSONResponse({"ok": True})
    except Exception as e:
        _log(f"error: {e}")
        return JSONResponse({"ok": True})


def _serve_landing() -> HTMLResponse:
    """Serve the landing page from web/index.html."""
    path = _ROOT / "web" / "index.html"
    if path.is_file():
        html = path.read_text(encoding="utf-8")
        return HTMLResponse(html)
    return HTMLResponse("<h1>Boss Assistant</h1><p>Landing page not found (web/index.html).</p>", status_code=404)


@app.get("/styles.css")
async def landing_css():
    """Serve landing page CSS."""
    path = _ROOT / "web" / "styles.css"
    if path.is_file():
        return PlainTextResponse(path.read_text(encoding="utf-8"), media_type="text/css")
    return PlainTextResponse("", status_code=404)


@app.post("/api/contact")
async def api_contact(request: Request):
    """
    Contact form: receive name, email, message and email them to CONTACT_EMAIL_TO.
    No auth so the public landing page can submit.
    """
    try:
        body = await request.json()
        name = (body.get("name") or "").strip()[:200]
        email = (body.get("email") or "").strip()[:200]
        message = (body.get("message") or "").strip()[:2000]
        if not name or not email:
            return JSONResponse({"ok": False, "message": "Name and email are required."}, status_code=400)
        to_email = (os.environ.get("CONTACT_EMAIL_TO") or os.environ.get("REPORT_EMAIL_TO") or "").strip()
        if "," in to_email:
            to_email = to_email.split(",")[0].strip()
        if not to_email:
            return JSONResponse(
                {"ok": False, "message": "Contact form not configured (set CONTACT_EMAIL_TO in .env)."},
                status_code=503,
            )
        err = send_contact_lead(to_email, name, email, message)
        if err:
            return JSONResponse({"ok": False, "message": err}, status_code=500)
        return {"ok": True, "message": "Thanks — we'll be in touch."}
    except Exception as e:
        return JSONResponse({"ok": False, "message": str(e)[:200]}, status_code=500)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page."""
    return _serve_landing()


@app.get("/health")
async def health():
    """Health check for monitoring."""
    return {"status": "ok", "service": "boss-assistant-reply-by-email"}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(_: None = Depends(_check_dashboard_auth)):
    """Admin dashboard: list clients and trigger reports."""
    clients = load_clients()
    rows = []
    for c in clients:
        cid = (c.get("id") or "").strip()
        name = (c.get("name") or cid or "—").strip()
        email = (c.get("email_to") or "").strip()
        rows.append(
            f'<tr><td>{name}</td><td><code>{email}</code></td>'
            f'<td><button type="button" class="btn-send" data-client-id="{cid}">Send report</button></td></tr>'
        )
    table_rows = "\n".join(rows)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><title>Boss Assistant — Dashboard</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0f0f0f; color: #e8e8e8; }}
  h1 {{ font-size: 1.5rem; }}
  table {{ border-collapse: collapse; margin-top: 1rem; }}
  th, td {{ padding: 0.5rem 1rem; text-align: left; border: 1px solid #2a2a2a; }}
  th {{ background: #1a1a1a; }}
  .btn-send {{ padding: 0.4rem 0.8rem; background: #c9a227; color: #0f0f0f; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }}
  .btn-send:hover {{ background: #ddb83a; }}
  .btn-send:disabled {{ opacity: 0.6; cursor: not-allowed; }}
  .status {{ margin-top: 1rem; font-size: 0.9rem; color: #9a9a9a; }}
  .error {{ color: #e55; }}
</style>
</head>
<body>
  <h1>Boss Assistant — Dashboard</h1>
  <p>Send the monthly report to a client. Report runs in the background; check the server log for errors.</p>
  <table>
    <thead><tr><th>Client</th><th>Email</th><th>Action</th></tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
  <div class="status" id="status"></div>
  <script>
    document.querySelectorAll('.btn-send').forEach(function(btn) {{
      btn.addEventListener('click', function() {{
        var id = this.getAttribute('data-client-id');
        var status = document.getElementById('status');
        status.textContent = 'Sending report for ' + id + '…';
        status.classList.remove('error');
        this.disabled = true;
        fetch('/api/run-client/' + encodeURIComponent(id), {{ method: 'POST' }})
          .then(function(r) {{ return r.json(); }})
          .then(function(d) {{
            status.textContent = d.ok ? 'Report sent for ' + id + '.' : ('Error: ' + (d.message || 'Unknown'));
            if (!d.ok) status.classList.add('error');
          }})
          .catch(function(e) {{
            status.textContent = 'Error: ' + e.message;
            status.classList.add('error');
          }})
          .finally(function() {{ btn.disabled = false; }});
      }});
    }});
  </script>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/api/clients")
async def api_clients(_: None = Depends(_check_dashboard_auth)):
    """List clients (id, name, email_to) for the dashboard."""
    clients = load_clients()
    out = []
    for c in clients:
        out.append({
            "id": (c.get("id") or "").strip(),
            "name": (c.get("name") or "").strip(),
            "email_to": (c.get("email_to") or "").strip(),
        })
    return {"clients": out}


@app.post("/api/run-client/{client_id}")
async def api_run_client(client_id: str, _: None = Depends(_check_dashboard_auth)):
    """Trigger report send for the given client (runs main.py --run-client <id>)."""
    clients = load_clients()
    client = get_client(clients, client_id)
    if not client:
        return JSONResponse({"ok": False, "message": f"Client not found: {client_id}"}, status_code=404)
    main_py = _ROOT / "main.py"
    if not main_py.is_file():
        return JSONResponse({"ok": False, "message": "main.py not found"}, status_code=500)
    try:
        result = subprocess.run(
            [sys.executable, str(main_py), "--run-client", client_id],
            cwd=str(_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return {"ok": True, "message": "Report sent."}
        err = (result.stderr or result.stdout or "").strip() or f"Exit code {result.returncode}"
        return JSONResponse({"ok": False, "message": err[:500]}, status_code=200)
    except subprocess.TimeoutExpired:
        return JSONResponse({"ok": False, "message": "Report run timed out."}, status_code=200)
    except Exception as e:
        return JSONResponse({"ok": False, "message": str(e)[:500]}, status_code=200)


# ---------- Client portal (Option B: proper app) ----------

def _client_login_html(msg: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Sign in — Boss Assistant</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0f0f0f; color: #e8e8e8; max-width: 360px; }}
  h1 {{ font-size: 1.25rem; }}
  input {{ width: 100%; padding: 0.5rem; margin: 0.5rem 0; box-sizing: border-box; background: #1a1a1a; border: 1px solid #2a2a2a; color: #e8e8e8; border-radius: 6px; }}
  button {{ padding: 0.5rem 1rem; background: #c9a227; color: #0f0f0f; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 0.5rem; }}
  .msg {{ color: #9a9a9a; font-size: 0.9rem; margin-top: 1rem; }}
  .err {{ color: #e55; }}
</style>
</head>
<body>
  <h1>Sign in to your report</h1>
  <p>Enter the email address where you receive your monthly report.</p>
  <form method="post" action="/client/login">
    <input type="email" name="email" placeholder="you@company.com" required />
    <button type="submit">Send sign-in link</button>
  </form>
  <p class="msg {'' if not msg else 'err'}">{msg or 'We\'ll email you a link to sign in.'}</p>
</body>
</html>"""


def _client_dashboard_html(client_id: str, client_name: str, report_html: str, ask_reply: str = "") -> str:
    report_block = f"<pre style=\"white-space: pre-wrap; background: #1a1a1a; padding: 1rem; border-radius: 6px; overflow-x: auto;\">{report_html}</pre>" if report_html else "<p>No report yet. Your next report will appear here.</p>"
    reply_block = f"<div class=\"reply\"><strong>Reply:</strong><pre style=\"white-space: pre-wrap;\">{ask_reply}</pre></div>" if ask_reply else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Your report — Boss Assistant</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0f0f0f; color: #e8e8e8; max-width: 720px; }}
  h1 {{ font-size: 1.25rem; }}
  a {{ color: #c9a227; }}
  .reply {{ margin-top: 1rem; padding: 1rem; background: #1a1a1a; border-radius: 6px; }}
  textarea {{ width: 100%; min-height: 80px; padding: 0.5rem; box-sizing: border-box; background: #1a1a1a; border: 1px solid #2a2a2a; color: #e8e8e8; border-radius: 6px; }}
  button {{ padding: 0.5rem 1rem; background: #c9a227; color: #0f0f0f; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 0.5rem; }}
</style>
</head>
<body>
  <p><a href="/client/logout">Sign out</a></p>
  <h1>{client_name or "Your report"}</h1>
  <h2>Latest report</h2>
  {report_block}
  <p><button type="button" id="request-report-btn">Send my report again</button> <span id="request-report-msg"></span></p>
  <h2>Ask a question</h2>
  <p>Ask anything about your numbers. We'll answer here and you can also reply to your report email.</p>
  <form id="ask-form">
    <textarea name="message" placeholder="e.g. What was last quarter's revenue?" required></textarea>
    <button type="submit">Ask</button>
  </form>
  <div id="ask-replies">{reply_block}</div>
  <script>
    document.getElementById('request-report-btn').onclick = function() {{
      var btn = this;
      var msg = document.getElementById('request-report-msg');
      btn.disabled = true;
      msg.textContent = 'Sending…';
      fetch('/api/client/request-report', {{ method: 'POST' }})
        .then(function(r) {{ return r.json(); }})
        .then(function(d) {{ msg.textContent = d.ok ? 'Report on its way. Check your email.' : (d.message || 'Failed.'); }})
        .catch(function() {{ msg.textContent = 'Error.'; }})
        .finally(function() {{ btn.disabled = false; }});
    }};
    document.getElementById('ask-form').onsubmit = function(e) {{
      e.preventDefault();
      var form = this;
      var btn = form.querySelector('button');
      var text = form.querySelector('textarea').value;
      btn.disabled = true;
      fetch('/api/client/ask', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ message: text }}) }})
        .then(function(r) {{ return r.json(); }})
        .then(function(d) {{
          if (d.reply) {{
            var div = document.createElement('div');
            div.className = 'reply';
            div.innerHTML = '<strong>Reply:</strong><pre style=\"white-space: pre-wrap;\">' + (d.reply || '').replace(/</g, '&lt;').replace(/&/g, '&amp;') + '</pre>';
            document.getElementById('ask-replies').appendChild(div);
          }}
          btn.disabled = false;
        }});
    }};
  </script>
</body>
</html>"""


@app.get("/client")
async def client_index(request: Request):
    """Redirect to dashboard if signed in, else login."""
    client_id = _get_client_from_session(request)
    if client_id:
        return RedirectResponse(url="/client/dashboard", status_code=302)
    return RedirectResponse(url="/client/login", status_code=302)


@app.get("/client/login", response_class=HTMLResponse)
async def client_login_page():
    return HTMLResponse(_client_login_html())


@app.post("/client/login", response_class=HTMLResponse)
async def client_login_submit(request: Request):
    body = await request.form()
    email = (body.get("email") or "").strip().lower()
    if not email:
        return HTMLResponse(_client_login_html("Please enter your email."), status_code=400)
    clients = load_clients()
    client = get_client_by_email(clients, email)
    if not client:
        return HTMLResponse(_client_login_html("No account found for that email. Use the address where you receive your report."))
    client_id = (client.get("id") or "").strip()
    if not client_id:
        return HTMLResponse(_client_login_html("Configuration error."), status_code=500)
    token = create_magic_link_token(client_id)
    base_url = str(request.base_url).rstrip("/")
    login_url = f"{base_url}/client/verify?token={quote(token)}"
    err = send_magic_link_email(email, login_url)
    if err:
        return HTMLResponse(_client_login_html(f"Could not send email: {err}"))
    return HTMLResponse(_client_login_html("Check your email and click the link to sign in."))


@app.get("/client/verify")
async def client_verify(request: Request, token: str = ""):
    """Magic link: verify token, set session cookie, redirect to dashboard."""
    client_id = verify_magic_link_token(token or "")
    if not client_id:
        return RedirectResponse(url="/client/login?error=invalid", status_code=302)
    response = RedirectResponse(url="/client/dashboard", status_code=302)
    response.set_cookie(key=_CLIENT_SESSION_COOKIE, value=_sign_session(client_id), max_age=_CLIENT_SESSION_MAX_AGE, httponly=True, samesite="lax")
    return response


@app.get("/client/dashboard", response_class=HTMLResponse)
async def client_dashboard(request: Request):
    client_id = _get_client_from_session(request)
    if not client_id:
        return RedirectResponse(url="/client/login", status_code=302)
    clients = load_clients()
    client = get_client(clients, client_id)
    if not client:
        return RedirectResponse(url="/client/login", status_code=302)
    client_name = (client.get("name") or client_id).strip()
    report_text = get_latest_report(client_id) or ""
    report_escaped = report_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") if report_text else ""
    html = _client_dashboard_html(client_id, client_name, report_escaped, "")
    return HTMLResponse(html)


@app.post("/client/logout")
async def client_logout():
    response = RedirectResponse(url="/client/login", status_code=302)
    response.delete_cookie(_CLIENT_SESSION_COOKIE)
    return response


@app.post("/api/client/ask")
async def api_client_ask(request: Request):
    """Authenticated: answer the client's question from the portal."""
    client_id = _get_client_from_session(request)
    if not client_id:
        return JSONResponse({"ok": False, "reply": "", "message": "Not signed in."}, status_code=401)
    try:
        body = await request.json()
        message = (body.get("message") or "").strip()[:2000]
        if not message:
            return JSONResponse({"ok": False, "reply": "", "message": "Empty message."}, status_code=400)
        reply_text = answer(client_id, message)
        return {"ok": True, "reply": reply_text}
    except Exception as e:
        return JSONResponse({"ok": False, "reply": "", "message": str(e)[:200]}, status_code=500)


@app.post("/api/client/request-report")
async def api_client_request_report(request: Request):
    """Authenticated: trigger sending the report email again (same as 'send my report again' by email)."""
    client_id = _get_client_from_session(request)
    if not client_id:
        return JSONResponse({"ok": False, "message": "Not signed in."}, status_code=401)
    try:
        _trigger_send_report(client_id)
        return {"ok": True, "message": "Report is on its way. Check your email."}
    except Exception as e:
        return JSONResponse({"ok": False, "message": str(e)[:200]}, status_code=500)
