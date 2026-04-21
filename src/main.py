from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.v1 import router as api_router
from src.core.config import settings

app = FastAPI(title="Reword API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

media_dir = Path(settings.MEDIA_DIR)
media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
