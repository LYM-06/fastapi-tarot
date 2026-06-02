"""
Redis Cache Module
"""

import os
import redis
from typing import Optional

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

CACHE_PREFIX = "tarot:"
redis_client: Optional[redis.Redis] = None

def init_redis():
    global redis_client
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5
        )
        redis_client.ping()
        print("[OK] Redis connected successfully")
    except Exception as e:
        print("[FAIL] Redis connection failed:", str(e))
        print("[WARN] Running without cache")
        redis_client = None

def get_cache(key: str) -> Optional[str]:
    if not redis_client:
        return None
    try:
        return redis_client.get(f"{CACHE_PREFIX}{key}")
    except Exception as e:
        print("Redis get error:", str(e))
        return None

def set_cache(key: str, value: str, expire: int = 3600) -> bool:
    if not redis_client:
        return False
    try:
        redis_client.set(f"{CACHE_PREFIX}{key}", value, ex=expire)
        return True
    except Exception as e:
        print("Redis set error:", str(e))
        return False

def delete_cache(key: str) -> bool:
    if not redis_client:
        return False
    try:
        redis_client.delete(f"{CACHE_PREFIX}{key}")
        return True
    except Exception as e:
        print("Redis delete error:", str(e))
        return False

def clear_all_cache() -> bool:
    if not redis_client:
        return False
    try:
        keys = redis_client.keys(f"{CACHE_PREFIX}*")
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        print("Redis clear error:", str(e))
        return False