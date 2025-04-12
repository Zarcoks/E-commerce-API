import os
import redis

redis_url = os.getenv("REDIS_URL", "redis://localhost")
redis_client = redis.from_url(redis_url)