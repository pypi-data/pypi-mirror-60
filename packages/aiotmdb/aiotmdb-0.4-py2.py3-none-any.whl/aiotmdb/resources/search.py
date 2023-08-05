from .base import BaseResource


class Search(BaseResource):
    """Search movies, TV shows, collections, persons, lists, companies and
    keywords.
    See: http://docs.themoviedb.apiary.io/#search
    """
    BASE_PATH = 'search/'
    URLS = {
        'movie': 'movie',
        'collection': 'collection',
        'tv': 'tv',
        'person': 'person',
        'list': 'list',
        'company': 'company',
        'keyword': 'keyword',
        'multi': 'multi',
    }

    async def movies(self, query, **kwargs):
        """Search for movies by title.
        TMDB doc: http://docs.themoviedb.apiary.io/#get-%2F3%2Fsearch%2Fmovie
        """
        path = self._get_path('movie')
        kwargs.update({'query': query})

        response = await self._get(path, **kwargs)
        return response

    async def collections(self, query, **kwargs):
        """Search for collections by name.
        TMDB doc: http://docs.themoviedb.apiary.io/#get-%2F3%2Fsearch%2Fcollection
        """
        path = self._get_path('collection')
        kwargs.update({'query': query})

        response = await self._get(path, **kwargs)
        
        return response

    async def tv(self, query, **kwargs):
        """Search for TV shows by title.
        TMDB doc: http://docs.themoviedb.apiary.io/#get-%2F3%2Fsearch%2Ftv
        """
        path = self._get_path('tv')
        kwargs.update({'query': query})

        response = await self._get(path, **kwargs)
        
        return response

    async def persons(self, query, **kwargs):
        """Search for people by name.
        TMDB doc: http://docs.themoviedb.apiary.io/#get-%2F3%2Fsearch%2Fperson
        """
        path = self._get_path('person')
        kwargs.update({'query': query})

        response = await self._get(path, **kwargs)
        
        return response

    async def companies(self, query, **kwargs):
        """Search for companies by name.
        TMDB doc: http://docs.themoviedb.apiary.io/#get-%2F3%2Fsearch%2Fcompany
        """
        path = self._get_path('company')
        kwargs.update({'query': query})

        response = await self._get(path, **kwargs)
        
        return response

    async def keywords(self, query, **kwargs):
        """Search for keywords by name.
        TMDB doc: http://docs.themoviedb.apiary.io/#get-%2F3%2Fsearch%2Fkeyword
        """
        path = self._get_path('keyword')
        kwargs.update({'query': query})

        response = await self._get(path, **kwargs)
        
        return response

    async def multi(self, query, **kwargs):
        """Search the movie, tv show and person collections with a single query.
        Each item returned in the result array has a media_type field that maps to
        either movie, tv or person. Each mapped result is the same response you
        would get from each independent search.
        """
        path = self._get_path('multi')
        kwargs.update({'query': query})

        response = await self._get(path, **kwargs)
        
        return response