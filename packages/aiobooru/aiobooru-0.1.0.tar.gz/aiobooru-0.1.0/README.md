# Aiobooru - A package for Danbooru API using aiohttp


Use like:

```python
import aiobooru
import asyncio

def run():
    async with aiobooru.Booru() as a:
        p = await a.post(1)
        await p.download('image.jpg')

asyncio.run(run())
```
