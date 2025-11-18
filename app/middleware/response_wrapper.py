import json
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


DOC_PATH_PREFIXES = ("/docs", "/redoc")
DOC_PATH_CONTAINS = ("/openapi",)


class UnifiedResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):  # type: ignore[override]
        response: Response = await call_next(request)

        path = request.url.path
        # Skip docs and non-JSON responses
        if path.startswith(DOC_PATH_PREFIXES) or any(k in path for k in DOC_PATH_CONTAINS):
            return response

        ctype = (response.headers.get("content-type") or "").lower()
        if "application/json" not in ctype:
            return response

        # Read response body
        body = b""
        async for chunk in response.body_iterator:  # type: ignore[attr-defined]
            body += chunk

        # Try parse JSON; if failed, return original response
        try:
            text = body.decode("utf-8") if body else "null"
            payload = json.loads(text)
        except Exception:
            # Return original response content if not JSON
            return Response(
                content=body,
                status_code=response.status_code,
                media_type=response.media_type,
                headers=dict(response.headers),
            )

        status_code = response.status_code
        message = ""
        data: Any = None

        if isinstance(payload, dict):
            # Prefer explicit fields, fallback gracefully
            if isinstance(payload.get("message"), str):
                message = payload.get("message", "")
            elif isinstance(payload.get("detail"), str):
                message = payload.get("detail", "")

            if isinstance(payload.get("status_code"), int):
                status_code = int(payload.get("status_code"))

            content = payload.get("content") if isinstance(payload.get("content"), dict) else None
            # Pagination-style: content.rows [+ content.total]
            if content and isinstance(content.get("rows"), list) and ("total" in content):
                data = {"list": content.get("rows"), "total": content.get("total")}
            elif content and isinstance(content.get("rows"), list):
                data = content.get("rows")
            # Top-level rows/total
            elif isinstance(payload.get("rows"), list) and ("total" in payload):
                data = {"list": payload.get("rows"), "total": payload.get("total")}
            elif isinstance(payload.get("rows"), list):
                data = payload.get("rows")
            elif "list" in payload and "total" in payload:
                data = {"list": payload.get("list"), "total": payload.get("total")}
            elif "data" in payload:
                data = payload.get("data")
            else:
                # For error-like dicts with only detail/message
                if "detail" in payload and not (content or "rows" in payload or "data" in payload):
                    data = None
                else:
                    data = payload
        elif isinstance(payload, list):
            data = payload
        else:
            # primitives/null
            data = payload

        unified = {"data": data, "message": message, "status_code": status_code}
        return JSONResponse(content=unified, status_code=status_code)
