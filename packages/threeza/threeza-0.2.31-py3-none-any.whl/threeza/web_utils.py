# -------- Basic fetching and caching ---------------------------------
# TODO: Move aiohttp async stuff here
from cachetools import cached, TTLCache, LRUCache
import requests

def is_url(url):
    return is_url_cached(url)

def get_url(url):
    return get_url_cached(url)

@cached(TTLCache(1000,1))
def get_url_cached(url):
    r = requests.get(url)
    if r.status_code==200:
        return r.content
    else:
        raise Exception(url)

@cached(cache=LRUCache(maxsize=50))
def is_url_cached(s:str):
    import re
    url_regex = re.compile(r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',re.IGNORECASE)
    return re.match(url_regex, s) is not None
