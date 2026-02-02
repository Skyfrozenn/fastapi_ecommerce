import redis.asyncio as redis


redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global redis_client
    if not redis_client:
        redis_client = redis.Redis(
            host='redis',
            port=6379,
            db=0,
            decode_responses=True
        )
    return redis_client
