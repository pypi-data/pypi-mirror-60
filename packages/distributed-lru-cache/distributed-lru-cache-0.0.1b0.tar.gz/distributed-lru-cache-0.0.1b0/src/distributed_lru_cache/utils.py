import redis


class RedisCache(object):
    def __init__(self, cache_name, host='localhost', port=6379, db=0):
        self.redis = redis.StrictRedis(decode_responses=True, host=host, port=port, db=db)
        self.cache_name = cache_name

    def set_redis_conn(self, conn: redis) -> None:
        self.redis = conn

    def clear(self) -> any:
        return self.redis.flushdb()

    def get(self, key: str) -> str:
        return self.redis.hget(self.cache_name, key)

    def get_all_keys(self):
        return self.redis.hgetall(self.cache_name)

    def set(self, key: str, value: str) -> None:
        self.redis.hset(self.cache_name, key, value)

    def remove(self, key: any) -> None:
        self.redis.hdel(self.cache_name, key)
