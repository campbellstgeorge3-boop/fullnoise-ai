"""Answer client question using latest report data + OpenAI."""
from openai import OpenAI

from app.config import OPENAI_API_KEY

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def answer_question(context: str, question: str) -> str:
    """Generate an answer based on report context and the user's question."""
    prompt = f"""You are a business assistant. Answer the question based only on the following report data. Be concise and factual.

Report data:
{context}

Question: {question}

Answer (plain text, 1-3 sentences):"""
    try:
        r = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        return (r.choices[0].message.content or "").strip() or "I couldn't generate an answer. Please try rephrasing."
    except Exception as e:
        return f"I'm sorry, I couldn't process that: {e}."
