from .base import BaseResource


class Discover(BaseResource):
    """Discover
    See: http://docs.themoviedb.apiary.io/#discover
    """
    BASE_PATH = 'discover/'
    URLS = {
        'movie': 'movie',
        'tv': 'tv',
    }

    def _replace_underscore(self, dictionary):
        """Replace the last '_' (underscore) with a '.'' (dot)."""
        for key in dictionary:
            if 'gte' in key or 'lte' in key:
                new_key = '.'.join(key.rsplit('_', 1))
                dictionary[new_key] = dictionary.pop(key)


    async def movie(self, **kwargs):
        """Discover movies by different types of data like average rating,
        number of votes, genres and certifications.
        TMDB doc: http://docs.themoviedb.apiary.io/#get-%2F3%2Fdiscover%2Fmovie
        """
        
        path = self._get_path('movie')
        self._replace_underscore(kwargs)
        response = await self._get(path, **kwargs)

        return response

    async def tv(self, **kwargs):
        """Discover TV shows by different types of data like average rating,
        number of votes, genres, the network they aired on and air dates.
        TMDB doc: http://docs.themoviedb.apiary.io/#get-%2F3%2Fdiscover%2Ftv
        """
        
        path = self._get_path('tv')
        self._replace_underscore(kwargs)
        response = await self._get(path, **kwargs)
        return response
