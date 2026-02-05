import json
import re
import uvicorn
from asyncio import TimeoutError
from aiohttp import ClientSession, ClientError


async def app(scope, receive, send):
    path = scope.get("path", "/")

    if match := re.match(r"^/([A-Z][a-z]{3})$", path):
        currency = match.group(1).upper()

        try:
            async with ClientSession() as session:
                async with session.get(
                    f"https://open.er-api.com/v6/latest/{currency}", timeout=10
                ) as response:
                    data = await response.read()

                    await send(
                        {
                            "type": "http.response.start",
                            "status": 200,
                            "headers": [
                                (b"content-type", b"application/json"),
                                (b"cache-control", b"max-age=3600"),
                            ],
                        }
                    )

                    await send({"type": "http.response.body", "body": data})

        except ClientError as e:
            await send_response(send, 502, {"error": f"Network error: {str(e)}"})
        except TimeoutError:
            await send_response(send, 504, {"error": "Request timeout"})
        except Exception as e:
            await send_response(send, 500, {"error": str(e)})

    else:
        await send_response(send, 404, {"error": "Use: /USD, /EUR, etc."})


async def send_response(send, status, data):
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send({"type": "http.response.body", "body": json.dumps(data).encode("utf-8")})


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
