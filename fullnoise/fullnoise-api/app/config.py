"""Load and expose environment configuration."""
import os
from pathlib import Path

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.is_file():
    from dotenv import load_dotenv
    load_dotenv(_env_path)


def get(key: str, default: str = "") -> str:
    return (os.environ.get(key) or default).strip()


# Required
DATABASE_URL = get("DATABASE_URL")
OPENAI_API_KEY = get("OPENAI_API_KEY")
# Resend: must be from the account where the domain is verified (and inbound webhook configured)
RESEND_API_KEY = get("RESEND_API_KEY")
REDIS_URL = get("REDIS_URL")
NEXTAUTH_SECRET = get("NEXTAUTH_SECRET")

# Optional
RESEND_FROM_EMAIL = get("RESEND_FROM_EMAIL") or "onboarding@resend.dev"
FRONTEND_URL = get("FRONTEND_URL") or "http://localhost:3000"
CONTACT_EMAIL_TO = get("CONTACT_EMAIL_TO")
ADMIN_EMAIL = get("ADMIN_EMAIL") or "admin@fullnoise.ai"
ADMIN_PASSWORD = get("ADMIN_PASSWORD") or "admin"
