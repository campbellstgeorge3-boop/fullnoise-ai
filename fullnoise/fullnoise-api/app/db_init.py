"""Create tables on startup if they do not exist."""
from app.database import Base, engine
from app.models import Client, Lead, Question, Report


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
