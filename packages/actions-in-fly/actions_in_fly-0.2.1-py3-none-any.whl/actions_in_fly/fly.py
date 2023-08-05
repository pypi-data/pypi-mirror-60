import json

import aiohttp


async def fly() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get('https://worldtimeapi.org/api/timezone/Europe/Moscow') as resp:
            data = await resp.json()
            print(json.dumps(data))
