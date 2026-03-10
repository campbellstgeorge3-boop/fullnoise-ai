"""Enqueue background jobs (send-report) via Redis/ARQ."""
from arq import create_pool
from arq.connections import RedisSettings

from app.config import REDIS_URL


async def enqueue_send_report(client_id: str) -> bool:
    """Add a send-report job for the given client. Returns True if enqueued."""
    try:
        redis = await create_pool(RedisSettings.from_dsn(REDIS_URL))
        await redis.enqueue_job("send_report_task", client_id)
        await redis.close()
        return True
    except Exception:
        return False
