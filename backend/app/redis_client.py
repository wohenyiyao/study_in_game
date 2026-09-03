"""Redis 客户端（验证码存储用）。

连接参数：环境变量 LQ_REDIS_URL 覆盖，默认 redis://127.0.0.1:6379/0
"""
import os
import redis

_URL = os.environ.get("LQ_REDIS_URL", "redis://127.0.0.1:6379/0")
client = redis.Redis.from_url(_URL, decode_responses=True)
