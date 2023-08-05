
class BaseResource(object):
    BASE_PATH = ''
    URLS = {}

    def __init__(self, tmdb):
        self.client = tmdb

    def _get_path(self, key):
        return self.BASE_PATH + self.URLS[key]

    def _get_id_path(self, key):
        return self._get_path(key).format(id=self.id)

    def _get_complete_url(self, path):
        return '{base}/{path}'.format(base=self.client._base, path=path)

    async def _get(self, path, **params):
        url = self._get_complete_url(path)
        return await self.client._request(url, method="get", params=params)

    async def _post(self, path, data, **params):
        url = self._get_complete_url(path)
        return await self.client._request(url, method="post", params=params, data=data)
