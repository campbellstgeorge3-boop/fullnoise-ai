"""
Answer client questions about their report data. Used by the reply-by-email flow.
Loads the client's CSV, computes metrics, and uses OpenAI to answer in plain language.
"""
import os
import subprocess
import sys
from pathlib import Path

# Load .env so OPENAI_API_KEY is available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

from clients import get_client, load_clients
from data_loader import load_from_12month_csv
from boss_report import compute_metrics
from utils import format_aud


def _build_context(client_id: str) -> str:
    """Load client's CSV and build a short context string for the LLM."""
    clients = load_clients()
    client = get_client(clients, client_id)
    if not client:
        return "No client data."
    csv_path = client.get("csv_path")
    if not csv_path:
        return "No CSV path for this client."
    path = Path(csv_path)
    if not path.is_file():
        return f"CSV not found: {csv_path}"
    try:
        inp = load_from_12month_csv(path)
        metrics = compute_metrics(inp)
    except Exception as e:
        return f"Error loading data: {e}"
    rev = metrics.revenue_this
    costs = getattr(inp, "costs_this_month", 0.0) or 0.0
    profit = rev - costs if costs else None
    lines = [
        f"Revenue this month: {format_aud(rev)}",
        f"Revenue last month: {format_aud(metrics.revenue_last)}",
        f"Budget this month: {format_aud(metrics.budget)}",
        f"Revenue vs budget (gap): {format_aud(metrics.budget_gap_abs)}",
        f"Jobs this month: {metrics.jobs_this}, last month: {metrics.jobs_last}",
        f"Costs this month: {format_aud(costs)}",
    ]
    if profit is not None:
        lines.append(f"Profit this month: {format_aud(profit)}")
    lines.append(f"Avg revenue per job this month: {format_aud(metrics.avg_revenue_per_job_this_month)}")
    return "\n".join(lines)


def _trigger_send_report(client_id: str) -> None:
    """Run main.py --run-client <id> to send the report email."""
    root = Path(__file__).resolve().parent
    main_py = root / "main.py"
    if not main_py.is_file():
        return
    try:
        subprocess.run(
            [sys.executable, str(main_py), "--run-client", client_id],
            cwd=str(root),
            capture_output=True,
            timeout=120,
        )
    except Exception:
        pass


def answer(client_id: str, message: str) -> str:
    """
    Answer the user's question about their report data.
    If the message is a request to resend the report, trigger it and return a short reply.
    Otherwise build context from the client's CSV and call OpenAI.
    """
    if not (message or "").strip():
        return "You didn't ask anything. Reply with a question about your numbers (e.g. What was my profit? How many jobs?) and I'll answer from your latest data."
    msg_lower = (message or "").strip().lower()
    # Simple heuristic: "send report", "resend", "send again", "send my report"
    if any(
        phrase in msg_lower
        for phrase in (
            "send my report",
            "send the report",
            "resend",
            "send again",
            "send report again",
            "email me the report",
        )
    ):
        _trigger_send_report(client_id)
        return "I've triggered a fresh report — you'll get it by email shortly. If you don't see it, check your spam or reply again."
    context = _build_context(client_id)
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        return "I can't answer right now (API not configured). You can ask things like: What was my profit? How did revenue compare to budget?"
    try:
        from openai import OpenAI
    except ImportError:
        return "OpenAI package not installed. Reply with a question and we'll fix this."
    client = OpenAI(api_key=api_key)
    system = (
        "You are a helpful assistant answering questions about a client's monthly business numbers. "
        "Use only the context below. Answer in one short paragraph, plain language, no jargon. "
        "If the question can't be answered from the context, say so briefly."
    )
    user = f"Context:\n{context}\n\nQuestion: {message.strip()}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user[:8000]},
            ],
            max_tokens=500,
        )
        content = (response.choices or [{}])[0].message.content if response.choices else ""
        return (content or "I couldn't generate an answer.").strip()
    except Exception as e:
        return f"Something went wrong: {str(e)[:200]}. Try asking again or request 'send my report again' to get a fresh report by email."
