import time

_CACHE = {}

def get_cache(key: str, ttl_seconds: int):
    item = _CACHE.get(key)
    if not item:
        return None
    created, value = item
    if time.time() - created > ttl_seconds:
        _CACHE.pop(key, None)
        return None
    return value

def set_cache(key: str, value):
    _CACHE[key] = (time.time(), value)
    return value
