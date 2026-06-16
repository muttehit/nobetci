import logging
from typing import Any, Dict, List, Optional, Union
import redis 
from redis.exceptions import ConnectionError, RedisError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RedisManager")

class RedisManager:
    """
    A context-safe manager for handling common Redis operations 
    using a centralized connection pool.
    """
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: Optional[str] = None):
        try:
            self.pool = redis.ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                max_connections=50
            )
            self.client = redis.Redis(connection_pool=self.pool)
            logger.info(f"Redis Connection Pool initialized at {host}:{port}, DB: {db}")
        except RedisError as e:
            logger.error(f"Failed to initialize Redis Pool: {e}")
            raise

    def ping(self) -> bool:
        """Check if the Redis server is alive."""
        try:
            return self.client.ping()
        except ConnectionError:
            logger.error("Redis server is down or unreachable.")
            return False

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key with an optional Time-To-Live (TTL) in seconds."""
        try:
            return self.client.set(name=key, value=value, ex=ttl)
        except RedisError as e:
            logger.error(f"Error setting key {key}: {e}")
            return False

    def get(self, key: str) -> Optional[str]:
        """Get the value of a key."""
        try:
            return self.client.get(key)
        except RedisError as e:
            return None

    def scan_iter(self, pattern: str) -> Optional[str]:
        """Get the value of a key."""
        try:
            return self.client.scan_iter(pattern)
        except RedisError as e:
            return None

    def delete(self, *keys: str) -> int:
        """Delete one or many keys. Returns the number of keys deleted."""
        try:
            return self.client.delete(*keys)
        except RedisError as e:
            return 0

    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        try:
            return bool(self.client.exists(key))
        except RedisError as e:
            logger.error(f"Error checking existence for {key}: {e}")
            return False

    def hset(self, name: str, mapping: Dict[str, Any]) -> int:
        """Set multiple fields in a Redis Hash."""
        try:
            return self.client.hset(name, mapping=mapping)
        except RedisError as e:
            logger.error(f"Error setting hash {name}: {e}")
            return 0

    def hgetall(self, name: str) -> Dict[str, str]:
        """Get all fields and values from a Redis Hash."""
        try:
            return self.client.hgetall(name)
        except RedisError as e:
            return {}

    def push_queue(self, queue_name: str, value: str) -> int:
        """Push an item to the end of a list (Queue push)."""
        try:
            return self.client.rpush(queue_name, value)
        except RedisError as e:
            logger.error(f"Error pushing to queue {queue_name}: {e}")
            return 0

    def pop_queue(self, queue_name: str) -> Optional[str]:
        """Pop an item from the front of a list (Queue pop - FIFO)."""
        try:
            return self.client.lpop(queue_name)
        except RedisError as e:
            logger.error(f"Error popping from queue {queue_name}: {e}")
            return None

    def close(self):
        """Disconnect all connections in the pool."""
        self.pool.disconnect()