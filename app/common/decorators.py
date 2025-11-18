import logging
import inspect
from functools import wraps
from fastapi import HTTPException


logger = logging.getLogger(__name__)


def log_exceptions(func):
    """Log unhandled exceptions and convert to HTTP 500 with Chinese message.

    - Keeps existing HTTPException (e.g., 404) behavior unchanged.
    - Logs stacktrace for unexpected errors.
    - Returns 500 with detail "服务器异常" to be picked by response wrapper.
    """

    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception:  # noqa: BLE001
                logger.exception("Unhandled error in %s", func.__name__)
                raise HTTPException(status_code=200, detail="服务器异常")

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception:  # noqa: BLE001
            logger.exception("Unhandled error in %s", func.__name__)
            raise HTTPException(status_code=200, detail="服务器异常")

    return sync_wrapper

