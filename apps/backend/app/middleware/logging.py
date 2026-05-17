import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Set up a dedicated file handler for request logging
logger = logging.getLogger("server_logger")
logger.setLevel(logging.INFO)

# Avoid adding multiple handlers if already configured
if not logger.handlers:
    file_handler = logging.FileHandler("logs/server.log", encoding="utf-8")
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Also log to stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get request details
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        logger.info(f"Incoming Request: {method} {path} | Client: {client_host}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            logger.info(f"Response: {method} {path} | Status: {response.status_code} | Duration: {process_time:.2f}ms")
            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(f"Request Failed: {method} {path} | Error: {str(e)} | Duration: {process_time:.2f}ms")
            raise e
