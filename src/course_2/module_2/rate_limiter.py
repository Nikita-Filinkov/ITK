import random
import time
import redis
import requests
from src.course_2.module_2.config import settings


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(self):
        self.redis_client = redis.from_url(settings.get_redis_url)
        self.queue_name = "rate_limit:requests"

    def test(self) -> bool:
        time_now = time.time()
        request_times = self.redis_client.lrange(self.queue_name, 0, -1)
        fresh_times = [
            request_time
            for request_time in request_times
            if (time_now - float(request_time)) < 3
        ]
        count_all_request = len(request_times)
        count_fresh_request = len(fresh_times)
        if count_all_request != count_fresh_request:
            self.redis_client.delete(self.queue_name)
            if fresh_times:
                self.redis_client.rpush(self.queue_name, *fresh_times)
        if count_fresh_request > 5:
            return False
        return True


def make_api_request(limiter: RateLimiter):
    if not limiter.test():
        raise RateLimitExceed
    else:
        response = requests.get("https://www.google.com/robots.txt")
        request_time = time.time()
        rate_limiter.redis_client.rpush(rate_limiter.queue_name, request_time)
        return response.status_code


if __name__ == "__main__":
    rate_limiter = RateLimiter()
    rate_limiter.redis_client.delete(rate_limiter.queue_name)

    for _ in range(50):
        # time.sleep(random.randint(1, 2))
        time.sleep(0.1)
        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
