"""VoxCraft API — Professional TTS Studio Backend.

Endpoints:
  GET  /api/health           — Health check with engine status
  GET  /api/voices           — List all available voices with metadata
  GET  /api/languages        — List supported languages
  GET  /api/tags             — List expression tags
  POST /api/synthesize       — Generate speech from text
  POST /api/synthesize/batch — Concurrent batch text-to-speech
  GET  /api/history          — Generation history (supports ?search=)
  DELETE /api/history/{id}   — Delete a generation
  GET  /api/audio/{path}     — Serve generated audio files
  GET  /{path:path}          — Serve frontend SPA (catch-all fallback)
"""

from __future__ import annotations

import logging
import mimetypes
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from pydantic import BaseModel, Field

from . import config
from .tts_engine import (
    EXPRESSION_TAGS,
    LANGUAGES,
    PRESET_VOICES,
    EXPORTS_DIR,
    EngineNotReadyError,
    VoiceNotFoundError,
    get_engine,
)

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("voxcraft.api")

# ─── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("VoxCraft starting on %s:%s", config.HOST, config.PORT)
    logger.info("Data directory: %s", config.DATA_DIR)
    logger.info("Voices: %d, Languages: %d", len(PRESET_VOICES), len(LANGUAGES))
    yield
    logger.info("VoxCraft shutting down")


# ─── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="VoxCraft TTS Studio",
    description="Enterprise-grade text-to-speech studio powered by Supertonic 3",
    version="1.0.1",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)

# CORS: allow same-origin only when binding to localhost.
# For advanced network deployments, override VOXCRAFT_CORS_ORIGINS env var.
_cors_origins = os.getenv("VOXCRAFT_CORS_ORIGINS", "").split(",") if os.getenv("VOXCRAFT_CORS_ORIGINS") else []
if not _cors_origins and config.HOST in ("127.0.0.1", "localhost"):
    _cors_origins = [f"http://localhost:{config.PORT}", f"http://127.0.0.1:{config.PORT}"]
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )
    logger.info("CORS enabled for origins: %s", _cors_origins)
else:
    logger.info("CORS disabled (no origins configured)")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
INDEX_HTML = FRONTEND_DIR / "index.html"
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")


# ─── Request / Response Models ──────────────────────────────────────────────

class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    voice: str = Field(default="M1", description="Voice style (M1-M5, F1-F5)")
    language: str = Field(default="en", description="Language code")
    speed: float = Field(default=1.05, ge=0.7, le=2.0, description="Speech speed")
    quality: int = Field(default=8, ge=5, le=12, description="Generation quality (5-12)")

    model_config = {"json_schema_extra": {
        "example": {
            "text": "Welcome to VoxCraft. This is a professional text-to-speech studio.",
            "voice": "M1",
            "language": "en",
            "speed": 1.05,
            "quality": 8,
        }
    }}


class BatchSynthesizeRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=50, description="List of texts to synthesize")
    voice: str = Field(default="M1")
    language: str = Field(default="en")
    speed: float = Field(default=1.05, ge=0.7, le=2.0)
    quality: int = Field(default=8, ge=5, le=12)


class SynthesizeResponse(BaseModel):
    success: bool
    audio_url: str
    duration_seconds: float
    id: str
    text: str
    voice: str
    language: str
    sample_rate: int = 44100


class BatchItemResponse(BaseModel):
    index: int
    text: str
    success: bool
    id: str | None = None
    audio_url: str | None = None
    duration_seconds: float | None = None
    error: str | None = None


class BatchSynthesizeResponse(BaseModel):
    success: bool
    total_success: int
    total_failed: int
    total_duration_seconds: float
    results: list[BatchItemResponse]


# ─── Helpers ─────────────────────────────────────────────────────────────────

_ID_PATTERN = re.compile(r"^[0-9a-f]{8,12}$")


def _validate_generation_id(generation_id: str) -> None:
    """Validate that a generation ID is a hex string. Raises HTTPException on failure."""
    if not _ID_PATTERN.match(generation_id):
        raise HTTPException(status_code=400, detail="Invalid generation ID format")


def _sanitize_error(exc: Exception) -> str:
    """Return a safe error message, logging the full traceback."""
    logger.error("Request failed: %s", exc, exc_info=True)
    return "An internal error occurred. Please check the server logs for details."


# ─── API Endpoints ──────────────────────────────────────────────────────────

@app.get("/api/health")
async def health() -> dict:
    """Health check with engine status and active synthesis count."""
    try:
        engine = get_engine()
        ready = engine.is_ready
        active = engine.active_syntheses
    except Exception:
        ready = False
        active = 0
    return {
        "status": "healthy" if ready else "initializing",
        "engine_ready": ready,
        "active_syntheses": active,
        "voices_available": len(PRESET_VOICES),
        "languages_available": len(LANGUAGES),
    }


@app.get("/api/voices")
async def list_voices() -> list[dict]:
    """List all available voice styles with metadata."""
    return [v.to_dict() for v in PRESET_VOICES]


@app.get("/api/languages")
async def list_languages() -> dict[str, str]:
    """List supported languages (code → name)."""
    return LANGUAGES


@app.get("/api/tags")
async def list_tags() -> dict[str, str]:
    """List expression tags for natural speech."""
    return EXPRESSION_TAGS


@app.post("/api/synthesize", response_model=SynthesizeResponse)
async def synthesize(req: SynthesizeRequest) -> SynthesizeResponse:
    """Generate speech from text with selected voice and parameters."""
    engine = get_engine()
    if not engine.is_ready:
        raise HTTPException(status_code=503, detail="TTS engine is initializing — please wait")

    try:
        wav, duration = engine.synthesize(
            text=req.text,
            voice=req.voice,
            lang=req.language,
            speed=req.speed,
            quality=req.quality,
        )
    except VoiceNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EngineNotReadyError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=_sanitize_error(e))

    meta = engine.export_for_platform(
        wav, req.text, req.voice, req.language,
        duration_seconds=duration, speed=req.speed, quality=req.quality,
    )
    return SynthesizeResponse(
        success=True,
        audio_url=f"/api/audio/{meta['filename']}.wav",
        duration_seconds=meta["duration_seconds"],
        id=meta["id"],
        text=req.text,
        voice=req.voice,
        language=req.language,
    )


@app.post("/api/synthesize/batch", response_model=BatchSynthesizeResponse)
async def synthesize_batch(req: BatchSynthesizeRequest) -> BatchSynthesizeResponse:
    """Generate speech for multiple texts concurrently."""
    engine = get_engine()
    if not engine.is_ready:
        raise HTTPException(status_code=503, detail="TTS engine is initializing")

    try:
        raw_results = await engine.synthesize_batch(
            texts=req.texts, voice=req.voice, lang=req.language,
            speed=req.speed, quality=req.quality,
        )
    except VoiceNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EngineNotReadyError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=_sanitize_error(e))

    results: list[BatchItemResponse] = []
    total_duration = 0.0
    success_count = 0
    failed_count = 0

    for r in raw_results:
        if r["success"]:
            wav, duration = r["wav"], r["duration"]
            meta = engine.export_for_platform(
                wav, r["text"], req.voice, req.language,
                duration_seconds=duration, speed=req.speed, quality=req.quality,
            )
            total_duration += duration
            success_count += 1
            results.append(BatchItemResponse(
                index=r["index"],
                text=r["text"],
                success=True,
                id=meta["id"],
                audio_url=f"/api/audio/{meta['filename']}.wav",
                duration_seconds=meta["duration_seconds"],
            ))
        else:
            failed_count += 1
            results.append(BatchItemResponse(
                index=r["index"],
                text=r["text"],
                success=False,
                error=r.get("error", "Unknown error"),
            ))

    return BatchSynthesizeResponse(
        success=failed_count == 0,
        total_success=success_count,
        total_failed=failed_count,
        total_duration_seconds=round(total_duration, 2),
        results=results,
    )


@app.get("/api/history")
async def get_history(
    limit: int = Query(default=50, ge=1, le=200),
    search: str = Query(default=None, description="Search by text or voice"),
) -> list[dict]:
    """Get recent generation history with optional search."""
    return get_engine().get_history(limit=limit, search=search)


@app.get("/api/audio/{filename:path}")
async def serve_audio(filename: str) -> Response:
    """Serve a generated audio file. Uses basename to prevent path traversal."""
    safe_name = os.path.basename(unquote(filename))
    audio_path = EXPORTS_DIR / safe_name
    if not audio_path.exists():
        audio_path = EXPORTS_DIR / f"{safe_name}.wav"
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(str(audio_path), media_type="audio/wav")


@app.delete("/api/history/{generation_id}")
async def delete_history(generation_id: str) -> dict:
    """Delete a generation from history by exact ID. Uses SQLite — no glob injection."""
    _validate_generation_id(generation_id)
    try:
        deleted = get_engine().delete_export(generation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=_sanitize_error(e))

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Generation not found")
    return {"success": True, "deleted": generation_id, "records_removed": deleted}


# ─── Frontend SPA Catch-all (must be LAST — matches after API routes) ───────

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str) -> Response:
    """Serve frontend static files or fall back to index.html (SPA)."""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")

    if not full_path:
        return HTMLResponse(
            INDEX_HTML.read_bytes() if INDEX_HTML.exists() else "<h1>Not found</h1>",
            status_code=200,
        )

    requested = FRONTEND_DIR / full_path
    try:
        requested.resolve().relative_to(FRONTEND_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid path")

    if requested.exists() and requested.is_file():
        content_type, _ = mimetypes.guess_type(str(requested))
        return FileResponse(str(requested), media_type=content_type or "application/octet-stream")

    if INDEX_HTML.exists():
        return HTMLResponse(INDEX_HTML.read_bytes(), status_code=200)
    return HTMLResponse("<h1>Frontend not built</h1>", status_code=200)


# ─── Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("╔══════════════════════════════════════════╗")
    print("║        VoxCraft TTS Studio v1.0.1        ║")
    print("║  Professional Text-to-Speech Studio      ║")
    print("╚══════════════════════════════════════════╝")
    print("")
    print("  Engine: Supertonic 3 (99M params, ONNX)")
    print(f"  Voices: {len(PRESET_VOICES)} styles available")
    print(f"  Languages: {len(LANGUAGES)} supported")
    print(f"  Server: http://{config.HOST}:{config.PORT}")
    print(f"  API Docs: http://{config.HOST}:{config.PORT}/docs")
    print("")
    uvicorn.run(app, host=config.HOST, port=config.PORT, log_level=config.LOG_LEVEL.lower())
