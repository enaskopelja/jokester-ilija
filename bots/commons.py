from collections.abc import Callable


def with_prefix_and_suffix(prefix: str, suffix: str) -> Callable:
    def decorator(fun):
        def wrapper(*args, **kwargs):
            return f"{prefix}{fun(*args, **kwargs)}{suffix}"

        return wrapper

    return decorator
