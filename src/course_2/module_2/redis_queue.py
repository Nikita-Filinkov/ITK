import json

import redis
from src.course_2.module_2.config import settings


class RedisQueue:
    def __init__(self):
        self.redis_client = redis.from_url(settings.get_redis_url)
        self.queue_name = "queue"

    def publish(self, msg: dict):
        msg_json = json.dumps(msg)
        self.redis_client.rpush(self.queue_name, msg_json)

    def consume(self) -> dict | None:
        msg_json = self.redis_client.lpop(self.queue_name)
        if msg_json is None:
            return None

        return json.loads(msg_json)


if __name__ == "__main__":
    q = RedisQueue()
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})

    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
