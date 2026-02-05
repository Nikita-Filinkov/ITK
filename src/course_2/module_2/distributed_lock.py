import time
import datetime
from concurrent.futures import ThreadPoolExecutor

import redis
from functools import wraps
from src.course_2.module_2.config import settings


def single(max_processing_time):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            exp = int(max_processing_time.total_seconds())
            lock_key = f"lock:{func.__name__}"

            with redis.from_url(
                settings.get_redis_url, max_connections=99, decode_responses=True
            ) as redis_client:
                acquired = redis_client.set(lock_key, "locked", nx=True, ex=exp)
                if not acquired:
                    return None

                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(func, *args, **kwargs)

                    try:
                        return future.result(timeout=exp)
                    except TimeoutError:
                        print(f"Превышено время выполнения ({exp} сек)")
                        return None
                    finally:
                        redis_client.delete(lock_key)
                        print("Блокировка освобождена")

        return wrapper

    return decorator


@single(max_processing_time=datetime.timedelta(minutes=0.5))
def process_transaction():
    time.sleep(2)
