from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import app  # This imports app/__init__.py which loads .env
from app.routes.pages import router as pages_router
from app.db import init_db
import os

app = FastAPI(title="AI Landing Page Builder")

# CORS Configuration
cors_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "https://ai-landing-page-frontend.vercel.app",
]

if os.getenv("ENVIRONMENT") == "production":
    cors_origins = [
        "https://yourdomain.com",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routes
app.include_router(pages_router, prefix="/api", tags=["pages"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)