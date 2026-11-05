import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seed import seed_database

# Routers
from app.routers import (
    auth_routes,
    course_routes,
    experiment_routes,
    manual_routes,
    compiler_routes,
    virtuallab_routes,
    copilot_routes,
    submission_routes,
    analytics_routes,
    pdf_routes,
    monitoring_routes
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    Base.metadata.create_all(bind=engine)
    # Seed initial demo data
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Laboratory Ecosystem for Engineering Colleges combining AI lab manuals, online compilers, virtual labs, and assessment verification.",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth_routes.router, prefix=settings.API_V1_STR)
app.include_router(course_routes.router, prefix=settings.API_V1_STR)
app.include_router(experiment_routes.router, prefix=settings.API_V1_STR)
app.include_router(manual_routes.router, prefix=settings.API_V1_STR)
app.include_router(compiler_routes.router, prefix=settings.API_V1_STR)
app.include_router(virtuallab_routes.router, prefix=settings.API_V1_STR)
app.include_router(copilot_routes.router, prefix=settings.API_V1_STR)
app.include_router(submission_routes.router, prefix=settings.API_V1_STR)
app.include_router(analytics_routes.router, prefix=settings.API_V1_STR)
app.include_router(pdf_routes.router, prefix=settings.API_V1_STR)
app.include_router(monitoring_routes.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "status": "operational"
    }

@app.get("/api/health")
def health_check():
    from app.services.watsonx_service import watsonx_service
    return {
        "status": "healthy",
        "watsonx_configured": watsonx_service.is_configured,
        "watsonx_model": settings.WATSONX_MODEL_ID,
        "mode": "Live IBM watsonx.ai" if watsonx_service.is_configured else "Demo Simulation Mode (IBM Granite)"
    }

