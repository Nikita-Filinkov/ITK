import asyncio
import os
from asyncio import TimeoutError
import json
from aiohttp import ClientSession, ClientTimeout, ClientConnectorError

urls = [
    "https://www.google.com/robots.txt",
    "https://www.google.com",
    "https://pypi.org/project/aiohttp/",
    "https://pikabu.ru/tag/%D0%AE%D0%BC%D0%BE%D1%80/hot",
    "https://www.google.com/example",
    "http://192.0.2.1",
]


async def fetch_urls(urls: list[str], file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    timeout = ClientTimeout(total=8)
    semaphore = asyncio.Semaphore(5)
    queue = asyncio.Queue(maxsize=20)
    data = {}

    async with ClientSession(timeout=timeout) as session:

        async def fetch(url: str):
            async with semaphore:
                try:
                    async with session.get(url) as response:
                        status = response.status
                        result_response = {url: status}
                        await queue.put(result_response)
                except (ClientConnectorError, TimeoutError):
                    result_response = {url: 0}
                    await queue.put(result_response)

        async def writer():
            with open(file_path, mode="w", encoding="utf-8") as file:
                while True:
                    try:
                        response = await asyncio.wait_for(queue.get(), timeout=10.0)
                        data.update(response)
                        queue.task_done()
                        json_line = json.dumps(response, ensure_ascii=False)
                        file.write(json_line + "\n")
                        file.flush()
                    except asyncio.TimeoutError:
                        print("Все fetch завершены")
                        break

        task_writer = asyncio.create_task(writer())
        tasks = [asyncio.create_task(fetch(url)) for url in urls]
        await asyncio.gather(*tasks)
        await queue.join()
        await task_writer

        return data


if __name__ == "__main__":
    asyncio.run(fetch_urls(urls, "./results.jsonl"))
