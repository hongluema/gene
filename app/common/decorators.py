import logging
import inspect
from functools import wraps
from fastapi import HTTPException
from starlette.responses import JSONResponse


logger = logging.getLogger(__name__)


def log_exceptions(func):
    """Log unhandled exceptions and return HTTP 200 with error payload.

    - Keeps existing HTTPException (e.g., 404) behavior unchanged.
    - Logs stacktrace for unexpected errors.
    - Returns 200 with body: { "data": { "code": 500, "message": "服务器异常", "data": null } }
      The unified response middleware will wrap it to
      { data, message: '', status_code: 200 }.
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
                payload = {"data": {"code": 500, "message": "服务器异常", "data": None}}
                return JSONResponse(content=payload, status_code=200)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception:  # noqa: BLE001
            logger.exception("Unhandled error in %s", func.__name__)
            payload = {"data": {"code": 500, "message": "服务器异常", "data": None}}
            return JSONResponse(content=payload, status_code=200)

    return sync_wrapper
