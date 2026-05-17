from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from app.config import settings

class JWTAuthMiddleware(BaseHTTPMiddleware):
    # Public endpoints that don't require authentication
    EXCLUDED_PATHS = {
        "/",
        "/health",
        "/api/docs",
        "/api/openapi.json",
        "/api/auth/login",
        "/api/auth/signup",
        "/api/auth/refresh",
    }
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth check for public paths
        if request.url.path in self.EXCLUDED_PATHS or request.url.path.startswith("/api/docs"):
            response = await call_next(request)
            return response
        
        # Extract and validate token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            # Store user_id in request state for use in endpoints
            request.state.user_id = user_id
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        response = await call_next(request)
        return response
