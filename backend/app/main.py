"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="DocumentIQ API",
    description="AI-powered document intelligence system for technical standards",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "DocumentIQ API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import routers
from app.routers import chat, documents, generate, analytics

app.include_router(chat.router, prefix=f"{settings.api_v1_prefix}/chat", tags=["chat"])
app.include_router(documents.router, prefix=f"{settings.api_v1_prefix}/documents", tags=["documents"])
app.include_router(generate.router, prefix=f"{settings.api_v1_prefix}/generate", tags=["generate"])
app.include_router(analytics.router, prefix=f"{settings.api_v1_prefix}/analytics", tags=["analytics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
