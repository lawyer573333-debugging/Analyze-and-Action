from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth import JWTAuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import auth, documents, insights, actions, websocket, urban

app = FastAPI(
    title="Insight-to-Action Engine",
    version="1.0.0",
    docs_url="/api/docs"
)

# Middleware stack (order matters - auth BEFORE rate limit)
app.add_middleware(LoggingMiddleware)
app.add_middleware(JWTAuthMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:3001",
        "http://localhost:5000",
        "https://AnalyzeAndAction.com",
        "https://www.AnalyzeAndAction.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(urban.router, prefix="/api/urban", tags=["urban"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(actions.router, prefix="/api/actions", tags=["actions"])
app.include_router(websocket.router, prefix="/api/ws", tags=["websocket"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Antigravity Insight-to-Action Engine",
        "docs": "/api/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
