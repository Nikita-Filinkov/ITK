import unittest.mock
from collections import OrderedDict


def lru_cache(_func=None, maxsize=None):
    def decorator(func):
        cache_dict = OrderedDict()

        def wrapper(*args, **kwargs):
            list_elements = sorted(list(args) + list(kwargs.values()))
            cache_key = tuple(list_elements)
            if cache_key in cache_dict:
                cache_dict.move_to_end(cache_key)
                return cache_dict[cache_key]
            else:
                result = func(*args, **kwargs)
                cache_dict[cache_key] = result
                cache_dict.move_to_end(cache_key)
                if maxsize is not None and len(cache_dict) > maxsize:
                    cache_dict.popitem(last=False)
            return result

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


@lru_cache
def sum(a: int, b: int) -> int:
    return a + b


@lru_cache
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply(a: int, b: int) -> int:
    return a * b


if __name__ == "__main__":
    assert sum(1, 2) == 3
    assert sum(3, 4) == 7

    assert multiply(1, 2) == 2
    assert multiply(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4
