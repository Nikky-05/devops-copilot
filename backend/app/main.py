from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, routes
from app.utils.config import get_settings

settings = get_settings()

app = FastAPI(
    title="AI DevOps Copilot",
    description="LLM-powered DevOps assistant with RAG and MCP tool integrations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(routes.router, prefix="/api/v1", tags=["copilot"])


@app.get("/")
def root():
    return {
        "name": "AI DevOps Copilot",
        "version": "0.1.0",
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
    }
