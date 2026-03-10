"""
Background worker: process send-report jobs from Redis queue.
Run: arq app.worker.WorkerSettings
"""
from decimal import Decimal

from arq.connections import RedisSettings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import DATABASE_URL, REDIS_URL
from app.models import Client, Report
from app.services.email import send_report_email
from app.services.report import generate_report_summary

# DB for worker
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def send_report_task(ctx: dict, client_id: str) -> dict:
    """
    Job: load client, create report from placeholder data (or future: load from CSV/API),
    save to DB, send email, update client.last_report_sent_at.
    """
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Client).where(Client.id == client_id))
        client = result.scalars().first()
        if not client:
            return {"ok": False, "error": "Client not found"}

        # Placeholder: use simple numbers for MVP. Replace with real data source (CSV, API) later.
        now = datetime.now(timezone.utc)
        month = now.strftime("%Y-%m")
        revenue = Decimal("50000.00")
        costs = Decimal("32000.00")
        profit = revenue - costs
        jobs = 12

        summary = generate_report_summary(month, revenue, costs, profit, jobs)

        report = Report(
            client_id=client.id,
            month=month,
            revenue=revenue,
            costs=costs,
            profit=profit,
            jobs=jobs,
            summary=summary,
        )
        session.add(report)
        await session.flush()

        body = f"""FullNoise AI — Monthly Report ({month})

Summary:
{summary}

Numbers:
• Revenue: ${revenue:,.2f}
• Costs: ${costs:,.2f}
• Profit: ${profit:,.2f}
• Jobs: {jobs}

Reply to this email with any question about your numbers.

—
FullNoise AI
"""
        err = send_report_email(client.email, f"Your monthly report — {month}", body)
        if err:
            return {"ok": False, "error": err}

        client.last_report_sent_at = now
        await session.commit()
        return {"ok": True, "report_id": report.id}


class WorkerSettings:
    functions = [send_report_task]
    redis_settings = RedisSettings.from_dsn(REDIS_URL)
