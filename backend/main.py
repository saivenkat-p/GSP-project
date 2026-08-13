from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from database import engine, Base
from seed_data import seed_database
from routers import services, ai, auth_router, partners, requests, admin

# Initialize database schema & seed data
Base.metadata.create_all(bind=engine)
try:
    seed_database()
except Exception as e:
    print(f"Startup database seeding note: {e}")

app = FastAPI(
    title="Government Services Navigator API",
    description="Intelligent AI-powered navigation, discovery, eligibility evaluation, and verified assistance layer for government services.",
    version="1.0.0"
)

# Configure CORS for React frontend (Vite default localhost ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(services.router)
app.include_router(ai.router)
app.include_router(auth_router.router)
app.include_router(partners.router)
app.include_router(requests.router)
app.include_router(admin.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "app": "Government Services Navigator API",
        "version": "1.0.0",
        "database": "SQLite (Development) / PostgreSQL Ready",
        "verified_sources": "Andhra Pradesh MeeSeva, Meebhoomi, IGRS, Parivahan",
        "last_verified_audit": "2026-08-10"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
