"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Initialize Neon Database connection
try:
    from app.services.database import db_service
    if db_service.is_connected:
        print("[OK] Neon PostgreSQL database connected")
    else:
        print("[WARNING] Neon database not connected - using fallback storage")
except Exception as e:
    print(f"[WARNING] Could not initialize Neon database: {e}")

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


@app.get("/api/debug/status")
async def debug_status():
    """Debug endpoint to check service status."""
    status = {
        "api": "running",
        "supabase": {"configured": False, "connected": False, "error": None},
        "openai": {"configured": False},
        "packages": {}
    }
    
    # Check Supabase
    if settings.supabase_url and settings.supabase_anon_key:
        status["supabase"]["configured"] = True
        try:
            from supabase import create_client
            client = create_client(settings.supabase_url, settings.supabase_anon_key)
            # Test connection
            result = client.table("documents").select("document_id").limit(1).execute()
            status["supabase"]["connected"] = True
            status["supabase"]["test_query"] = "success"
        except Exception as e:
            status["supabase"]["error"] = str(e)
    
    # Check OpenAI
    if settings.openai_api_key:
        status["openai"]["configured"] = True
    
    # Check package versions
    try:
        import supabase
        status["packages"]["supabase"] = getattr(supabase, "__version__", "unknown")
    except:
        status["packages"]["supabase"] = "not installed"
    
    try:
        import httpx
        status["packages"]["httpx"] = httpx.__version__
    except:
        status["packages"]["httpx"] = "not installed"
    
    try:
        import gotrue
        status["packages"]["gotrue"] = getattr(gotrue, "__version__", "unknown")
    except:
        status["packages"]["gotrue"] = "not installed"
    
    return status


# Import routers
from app.routers import chat, documents, generate, analytics

app.include_router(chat.router, prefix=f"{settings.api_v1_prefix}/chat", tags=["chat"])
app.include_router(documents.router, prefix=f"{settings.api_v1_prefix}/documents", tags=["documents"])
app.include_router(generate.router, prefix=f"{settings.api_v1_prefix}/generate", tags=["generate"])
app.include_router(analytics.router, prefix=f"{settings.api_v1_prefix}/analytics", tags=["analytics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
