import collections


class LRU:

    def __init__(self, maxsize=100):
        self.cache = collections.OrderedDict()
        self.maxsize = maxsize

    def put(self, key, value):
        cache = self.cache
        if key in cache:
            cache.move_to_end(key)
            return cache[key]
        cache[key] = value
        if len(cache) > self.maxsize:
            cache.popitem(last=False)
        return value

    def get(self, key):
        return self.cache.get(key)

    def pop(self, key):
        self.cache.pop(key, None)
