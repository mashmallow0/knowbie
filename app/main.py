"""
Knowbie - Knowledge Manager
FastAPI Application Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.api import knowledge, search
except ImportError:
    from api import knowledge, search

app = FastAPI(
    title="Knowbie",
    description="Personal Knowledge Manager with Semantic Search",
    version="1.0.0"
)

# Setup rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - restrict to specific origins in production
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Determine base path for static/templates
base_path = os.path.dirname(os.path.abspath(__file__))

# Static files
app.mount("/static", StaticFiles(directory=os.path.join(base_path, "static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(base_path, "templates"))

# Include API routers
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(search.router, prefix="/api/search", tags=["search"])


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main SPA"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    # Detect if running from app directory or project root
    if os.path.basename(os.getcwd()) == "app":
        module_path = "main:app"
    else:
        module_path = "app.main:app"
    
    uvicorn.run(
        module_path,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )