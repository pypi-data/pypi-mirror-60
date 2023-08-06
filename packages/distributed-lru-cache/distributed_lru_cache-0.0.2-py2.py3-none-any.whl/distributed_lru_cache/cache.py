#!/usr/bin/python
import logging
from collections import deque
from threading import Timer

from src.distributed_lru_cache.utils import RedisCache

NOT_STRING_ERROR = 'Please provide string for key and value'
NONE_TYPE_ERROR = "'NoneType' value is not allowed"

log = logging.getLogger("my-logger")


class LRUCache(object):
    def __init__(self, capacity=128, ttl=0, redis_host='localhost', redis_port=6379, redis_db=0, cache_name='ch'):
        self.capacity = capacity
        self.cache = {}
        self.queue = deque()
        self.ttl = ttl
        # Instantiate redis cache
        self.redis_conn = RedisCache(cache_name, redis_host, redis_port, redis_db)
        # Get all the cache items from redis
        self.get_items_from_cache()

    def set_redis_conn(self, redis, cache_name):
        self.redis_conn = RedisCache(cache_name=cache_name)
        self.redis_conn.set_redis_conn(redis)

    def clear_cache_instance(self):
        self.redis_conn.clear()

    def get(self, key: str) -> any:
        # Get all the items from redis
        self.get_items_from_cache()
        if key not in self.cache:
            # if the key is not found
            return -1
        else:
            return self._get_cache_value(key)

    def peek(self, key: str) -> any:
        if key in self.cache:
            return self.cache[key]['value']
        else:
            return -1

    def _get_cache_value(self, key: str) -> str:
        node = self.cache[key]
        # Remove the node from the queue
        self.queue.remove(node)
        # Remove the key from redis hash
        self.redis_conn.remove(key)
        # Append the node again on the queue
        self.queue.append(node)
        # Create the key on redis hash again
        self.redis_conn.set(key, node.get('value'))
        # Obtain the value from the node/key
        return node.get('value')

    def set_capacity(self, n: int) -> None:
        self.capacity = n
        while len(self.queue) > self.capacity:
            deleted = self.queue.popleft()['key']
            del self.cache[deleted]
            self.redis_conn.remove(deleted)

    def get_items_from_cache(self):
        self._clear_nodes()
        for key, value in self.redis_conn.get_all_keys().items():
            node = {'key': key, 'value': value}
            self.cache[key] = node
            self.queue.append(node)

    def put(self, key: str, value: str, ttl=0) -> str:
        # Fail first if an invalid argument is given
        if key is None or value is None:
            raise ValueError(NONE_TYPE_ERROR)
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError(NOT_STRING_ERROR)
        node = {'key': key, 'value': value}
        # Validates the capacity of the cache and remove the Last Recently Used key if no more space is found
        self._validate_capacity()
        # Validates if the key is in the cache instance and remove that key in order to create it again
        self._validate_key(key)
        # Create the key again on the local instance and redis
        self.cache[key] = node
        self.queue.append(node)
        self.redis_conn.set(key, str(value))
        # Set an expiration time for the key
        self._expire_cache(key, ttl)
        return node.get('value')

    def _validate_capacity(self):
        if len(self.queue) == self.capacity:
            removed = self.queue.popleft()['key']
            del self.cache[removed]
            self.redis_conn.remove(removed)

    def _validate_key(self, key):
        if key in self.cache:
            self.queue.remove(self.cache[key])
            self.redis_conn.remove(key)

    def _expire_cache(self, key, ttl):
        if self.ttl > 0:
            # Add the default expiration time for this record
            Timer(self.ttl, self._remove_cache, [key]).start()
        if ttl > 0:
            # Add an specific expiration time for this record
            Timer(ttl, self._remove_cache, [key]).start()

    def _clear_nodes(self):
        self.queue.clear()
        self.cache.clear()

    def _remove_cache(self, *args):
        if args[0] in self.cache:
            log.info('cache {} expired'.format(args[0]))
            self.redis_conn.remove(args[0])
