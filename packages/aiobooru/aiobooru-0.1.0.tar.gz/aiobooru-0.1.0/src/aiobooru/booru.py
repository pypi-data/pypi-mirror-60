import asyncio
from dataclasses import dataclass, field

import aiohttp
try:
    import aiofiles
    _has_aiofiles = True
except ImportError:
    _has_aiofiles = False


def requires_aiofiles(func):
    async def wrapper(*args, **kwargs):
        if not _has_aiofiles:
            raise ImportError('aiofiles is required to save posts')
        return await func(*args, **kwargs)
    return wrapper

class RemovedException(Exception):
    def __init__(self, id: int):
        self.id = id

    def __str__(self):
        return f'The post {self.id} has been removed'


@dataclass
class Post:
    id: int
    url: str

    _session: aiohttp.ClientSession

    async def bytes(self) -> bytes:
        async with self._session.get(self.url) as resp:
            if resp.status == 200:
                return await resp.read()

    @requires_aiofiles
    async def download(self, filename: str):
        async with aiofiles.open(filename, mode='wb') as f:
            await f.write(await self.bytes())


class Booru:
    site_url = 'danbooru.donmai.us'

    def __init__(self, username=None, api_key=None, loop=None, site_url=None):
        self.loop = loop

        if site_url:
            self.site_url = site_url

        self._auth = aiohttp.BasicAuth(username, api_key) if username and api_key else None
        self._session = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(auth=self._auth)
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()

    async def post(self, id: int) -> Post:
        if not self._session:
            self._session = aiohttp.ClientSession(auth=self._auth)
        async with self._session.get(f'https://{self.site_url}/posts/{id}.json') as resp:
            if resp.status == 200:
                json = await resp.json()
                if json["is_banned"]:
                    raise RemovedException(id)
                post = Post(id=id, url=json["file_url"], _session=self._session)
                return post
