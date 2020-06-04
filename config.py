import os

# Redis Config
REDIS_HOST = os.getenv("REDIS_HOST", "192.168.1.69")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
