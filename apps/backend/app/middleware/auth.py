from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # STUB: Just passing through for local preview
        response = await call_next(request)
        return response
