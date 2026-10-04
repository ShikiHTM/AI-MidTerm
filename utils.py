
import time
from functools import wraps


def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Hàm [{func.__name__}] chạy mất: {end - start:.6f} giây")
        return result
    return wrapper
