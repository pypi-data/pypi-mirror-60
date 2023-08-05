import logging
import aiohttp
from functools import lru_cache,wraps
from frozendict import frozendict

from .exceptions import TMDbException
from .resources.discover import Discover
from .resources.genres import Genres
from .resources.search import Search
from .resources.tv import TV
from .resources.movies import Movies, Collections, Companies, Reviews

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

REQUEST_CACHE_MAXSIZE=128

DEFAULT_OPTIONS = {
    "language": "en",
    "cache": True,
}

def freezeargs(func):
    """Transform mutable dictionnary
    Into immutable
    Useful to be compatible with cache
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([frozendict(arg) if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: frozendict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped

class TMDb(object):
    def __init__(self, api_key, **options):
        options = {
            **DEFAULT_OPTIONS,
            **options
        }

        self._base = 'http://api.themoviedb.org/3'
        self._remaining = 40
        self._reset = None
        self.api_key = api_key
        self.cache = options['cache']
        self.language = options['language']

        # Resources
        self.discover = Discover(self)
        self.genres = Genres(self)
        self.search = Search(self)
        self.tv = TV(self)
        self.movies = Movies(self)
        self.collections = Collections(self)
        self.companies = Companies(self)
        self.reviews = Reviews(self)

    async def _request(self, url, method="get", params={}, data={}):
        if self.api_key is None or self.api_key == '':
            raise TMDbException("No API key found.")

        params = {
            "api_key": self.api_key,
            "language": self.language,
            **params
        }

        if self.cache:
            return await self._make_cached_request(url, method, params, data)

        return await self._make_request(url, method, params, data)
    
    async def _make_request(self, url, method, params, data):
        async with aiohttp.ClientSession() as session:
            async with getattr(session, method)(url, params=params) as resp:
                if 'X-RateLimit-Remaining' in resp.headers:
                    _remaining = int(headers['X-RateLimit-Remaining'])

                if 'X-RateLimit-Reset' in resp.headers:
                    _reset = int(headers['X-RateLimit-Reset'])

                data = await resp.json(content_type=None)

                if resp.status >= 300:
                    raise TMDbException(data)

                return data

        await session.close()
    
    @freezeargs
    @lru_cache(maxsize=REQUEST_CACHE_MAXSIZE)
    async def _make_cached_request(self, url, method, params, data):
        return await self._make_request(url, method, params, data)
