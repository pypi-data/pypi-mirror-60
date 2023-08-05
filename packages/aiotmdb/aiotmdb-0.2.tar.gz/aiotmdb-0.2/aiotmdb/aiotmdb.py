import logging
import aiohttp

from .exceptions import TMDbException

from .resources.discover import Discover
from .resources.genres import Genres
from .resources.search import Search
from .resources.tv import TV
from .resources.movies import Movies, Collections, Companies, Reviews

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

DEFAULT_OPTIONS = {
    "language": "en",
    "cache": True
}

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

    async def _request(self, url, append_to_response="", method="get", params={}, data={}):
        if self.api_key is None or self.api_key == '':
            raise TMDbException("No API key found.")

        params = {
            "api_key": self.api_key,
            "language": self.language,
            **params
        }

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
