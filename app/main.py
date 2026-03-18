"""FastAPI application entry point."""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

# Load environment variables from .env file
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="AI-Powered Website Audit Tool",
    description="Extract factual metrics from websites for analysis",
    version="1.0.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI-Powered Website Audit Tool API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "audit": "/audit",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
