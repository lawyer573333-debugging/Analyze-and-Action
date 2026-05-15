from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from app.config import settings
from app.routers import documents, insights, actions, auth, websocket

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["Documents"])
app.include_router(insights.router, prefix=f"{settings.API_V1_STR}/insights", tags=["Insights"])
app.include_router(websocket.router, tags=["WebSockets"])
# app.include_router(actions.router, prefix=f"{settings.API_V1_STR}/actions", tags=["Actions"])
