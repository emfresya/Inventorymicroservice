import redis
import json
import os
from datetime import datetime

r = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

def get_top5_from_cache():
    key = f"top5_products:{datetime.now().strftime('%Y-%m')}"
    cached = r.get(key)
    return json.loads(cached) if cached else None

def set_top5_to_cache(data, ttl=900):  # 15 минут
    key = f"top5_products:{datetime.now().strftime('%Y-%m')}"
    r.setex(key, ttl, json.dumps(data))