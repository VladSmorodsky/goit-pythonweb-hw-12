from redis.asyncio import Redis
import hashlib
import os
from dotenv import load_dotenv
load_dotenv()


class Cache:
    def __init__(self, host: str, port: int, db: int = 0):
        self.redis_client = Redis(host=host, port=port, db=db)

    async def set(self, key: str, value: str, expire: int = 3600):
        """
        Set a value in the cache with an optional expiration time.

        Args:
            key (str): The cache key.
            value (str): The value to store.
            expire (int): Expiration time in seconds (default: 3600 seconds).
        """
        await self.redis_client.set(hashlib.md5(key.encode('utf-8')).hexdigest(), value, ex=expire)

    async def get(self, key: str) -> str | None:
        """
        Get a value from the cache by key.

        Args:
            key (str): The cache key.
        Returns:
            str | None: The cached value or None if not found.
        """
        value = await self.redis_client.get(hashlib.md5(key.encode('utf-8')).hexdigest())
        if value:
            return value.decode('utf-8')
        return None


cache = Cache(os.getenv("REDIS_HOST"), int(os.getenv("REDIS_PORT")))
