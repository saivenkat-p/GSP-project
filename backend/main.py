from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from database import engine, Base
from seed_data import seed_database
from routers import services, ai, auth_router, partners, requests, admin, locations, staff, training, freshness

# Initialize database schema & seed data
Base.metadata.create_all(bind=engine)
try:
    seed_database()
except Exception as e:
    print(f"Startup database seeding note: {e}")

app = FastAPI(
    title="Government Service Provider (GSP V2) API",
    description="AI-Powered Government Service Discovery, Guidance, Human Assistance & Verified Partner Network",
    version="2.0.0"
)

# Configure CORS for React frontend
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
app.include_router(locations.router)
app.include_router(services.router)
app.include_router(ai.router)
app.include_router(auth_router.router)
app.include_router(partners.router)
app.include_router(requests.router)
app.include_router(staff.router)
app.include_router(training.router)
app.include_router(freshness.router)
app.include_router(admin.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "app": "GSP V2 Intelligence API",
        "version": "2.0.0",
        "database": "SQLite (Development) / PostgreSQL Ready",
        "location_hierarchy": "Multi-State (State -> District -> Mandal -> Locality)",
        "service_records": "Service Intelligence Records (Grounded RAG)",
        "last_source_audit": "2026-08-20"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
