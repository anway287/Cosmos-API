from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.routers import stellar, constellation, exoplanet


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 {settings.app_title} v{settings.app_version} ready")
    yield


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=(
        "Astronomy analysis platform. "
        "Classify stars, identify constellations, and score exoplanet habitability — "
        "powered by real astrophysics formulas. No API keys required."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stellar.router)
app.include_router(constellation.router)
app.include_router(exoplanet.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse("app/static/index.html")


@app.get("/health")
def health():
    return {"status": "ok", "version": settings.app_version}
