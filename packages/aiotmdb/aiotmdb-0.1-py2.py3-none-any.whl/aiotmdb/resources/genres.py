from .base import BaseResource


class Genres(BaseResource):
    """ 
    See: http://docs.themoviedb.apiary.io/#genres
    """
    BASE_PATH = 'genre/'
    URLS = {
        'movie_list': 'movie/list',
        'tv_list': 'tv/list',
        'movies': '{id}/movies',
    }

    async def movie_list(self, **kwargs):
        """Get the list of genres for movies.
        """
        path = self._get_path('movie_list')

        response = await self._get(path, **kwargs)
        
        return response

    async def tv_list(self, **kwargs):
        """Get the list of genres for TV shows.
        """
        path = self._get_path('tv_list')

        response = await self._get(path, **kwargs)
        
        return response

    async def movies(self, **kwargs):
        """Get the list of movies for a particular genre by id.
        By default, only movies with 10 or more votes are included.
        """
        path = self._get_path('movies').format(id=kwargs['id'])

        response = await self._get(path, **kwargs)
        
        return response
