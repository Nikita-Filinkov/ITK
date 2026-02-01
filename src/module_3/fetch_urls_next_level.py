import asyncio
import os
from asyncio import TimeoutError
import json
import aiofiles
import ijson
from aiohttp import ClientSession, ClientTimeout, ClientConnectorError


async def fetch_urls(input_file: str):
    output_file = "./results2.jsonl"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    timeout = ClientTimeout(total=300, connect=5)
    response_data_queue = asyncio.Queue(maxsize=20)
    url_queue = asyncio.Queue(maxsize=20)

    async with ClientSession(timeout=timeout) as session:

        async def url_producer():
            async with aiofiles.open(input_file, "r") as f:
                async for line in f:
                    url = line.strip()
                    if url:
                        await url_queue.put(url)

        async def worker():
            while True:
                try:
                    url = await asyncio.wait_for(url_queue.get(), timeout=3.0)
                    try:
                        async with session.get(url) as response:
                            status = response.status
                            if status == 200:
                                result_response = {"url": url, "content": {}}
                                parser = ijson.parse_async(response.content)

                                async for prefix, event, value in parser:
                                    if prefix.endswith(".name") and event == "string":
                                        result_response["content"].update(
                                            {"Имя": value}
                                        )
                                    elif (
                                        prefix.endswith(".email") and event == "string"
                                    ):
                                        result_response["content"].update(
                                            {"Email": value}
                                        )
                                    elif prefix.endswith(".body") and event == "string":
                                        result_response["content"].update(
                                            {"Текст": value}
                                        )

                                await response_data_queue.put(result_response)
                            else:
                                continue
                    except (ClientConnectorError, TimeoutError):
                        continue
                    finally:
                        url_queue.task_done()
                except asyncio.TimeoutError:
                    if url_queue.empty():
                        break
                    continue

        async def writer():
            async with aiofiles.open(output_file, mode="w", encoding="utf-8") as file:
                while True:
                    try:
                        response = await asyncio.wait_for(
                            response_data_queue.get(), timeout=5.0
                        )
                        json_line = json.dumps(response, indent=4, ensure_ascii=False)
                        await file.write(json_line)
                        await file.flush()
                        response_data_queue.task_done()
                    except asyncio.TimeoutError:
                        print("Все fetch завершены")
                        break

        task_url_producer = asyncio.create_task(url_producer())
        task_writer = asyncio.create_task(writer())
        worker_tasks = []
        for _ in range(5):
            worker_task = asyncio.create_task(worker())
            worker_tasks.append(worker_task)
        await task_url_producer
        await url_queue.join()
        await asyncio.gather(*worker_tasks, return_exceptions=True)
        await response_data_queue.join()
        await task_writer


if __name__ == "__main__":
    asyncio.run(fetch_urls("./input_file.jsonl"))
