from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import app module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.routes.pages import router as pages_router
from app.db import init_db

app = FastAPI(title="AI Landing Page Builder")

# CORS Configuration
cors_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "https://ai-dlp-frontend.vercel.app",
    "https://ai-landing-page-frontend.vercel.app",
]

if os.getenv("ENVIRONMENT") == "production":
    cors_origins.extend([
        "https://yourdomain.com",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB (only run once on startup)
try:
    init_db()
except Exception as e:
    print(f"Database initialization warning: {e}")

# Include routes
app.include_router(pages_router, prefix="/api", tags=["pages"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Export handler for Vercel
# For serverless functions, export the ASGI app directly
__all__ = ['app']

