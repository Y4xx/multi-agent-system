from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routes import router
from api.oauth_routes import oauth_router
from services.config_validator import print_config_status

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Job Application System (CrewAI)",
    description="AI-powered system for intelligent job discovery and application automation using CrewAI",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
app.include_router(oauth_router)

@app.on_event("startup")
async def startup_event():
    """Run configuration validation on startup."""
    print_config_status()

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Multi-Agent Job Application System API (CrewAI-powered)",
        "status": "running",
        "version": "2.0.0",
        "architecture": "CrewAI Multi-Agent System"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
