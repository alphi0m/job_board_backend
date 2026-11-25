import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine, Base
from .routers import auth_router, jobs_router, applications_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inizializza le tabelle del database SQLite se non esistono
    Base.metadata.create_all(bind=engine)
    # Assicura che la directory di upload esista
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "cvs")
    os.makedirs(upload_dir, exist_ok=True)
    yield


app = FastAPI(
    title="Bacheca Annunci di Lavoro API",
    description="Backend REST API per il progetto di Enterprise Mobile Application Development (UNISA)",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurazione CORS aperta per consentire chiamate da Flutter mobile, web ed emulatori
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusione dei Router con prefisso /api
app.include_router(auth_router.router, prefix="/api")
app.include_router(jobs_router.router, prefix="/api")
app.include_router(applications_router.router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Bacheca Annunci API",
        "docs": "/docs",
        "version": "1.0.0",
    }
