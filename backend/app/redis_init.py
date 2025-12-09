import redis.asyncio as redis_async
from app.core.config import settings

REDIS = redis_async.from_url(str(settings.REDIS_URL), decode_responses=True)
