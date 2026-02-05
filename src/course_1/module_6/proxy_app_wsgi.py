import json
import urllib.request
import urllib.error
import re
from wsgiref.simple_server import make_server


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")

    if match := re.match(r"^/([A-Z][a-z]{3})$", path):
        currency = match.group(1).upper()
        try:
            with urllib.request.urlopen(
                f"https://open.er-api.com/v6/latest/{currency}", timeout=10
            ) as response:
                data = response.read()
                start_response(
                    "200 OK",
                    [
                        ("Content-Type", "application/json"),
                        ("Cache-Control", "max-age=3600"),
                    ],
                )
                return [data]

        except urllib.error.HTTPError as e:
            start_response("502 Bad Gateway", [("Content-Type", "application/json")])
            return [json.dumps({"error": str(e)}).encode()]
        except Exception as e:
            start_response("500 Internal Error", [("Content-Type", "application/json")])
            return [json.dumps({"error": str(e)}).encode()]
    else:
        start_response("404 Not Found", [("Content-Type", "application/json")])
        return [json.dumps({"error": "Use: /USD, /EUR, etc."}).encode()]


if __name__ == "__main__":
    server = make_server("localhost", 8000, app)
    server.serve_forever()
