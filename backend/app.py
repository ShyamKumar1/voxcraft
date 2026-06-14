"""VoxCraft API — Professional TTS Studio Backend.

Endpoints:
  GET  /api/voices        — List all available voices with metadata
  GET  /api/languages     — List supported languages
  GET  /api/tags          — List expression tags
  POST /api/synthesize    — Generate speech from text
  POST /api/synthesize/batch — Batch text-to-speech
  GET  /api/history       — Generation history
  GET  /api/audio/{path}  — Serve generated audio files
  GET  /api/health        — Health check
  GET  /{path:path}       — Serve frontend SPA (catch-all fallback)
"""

from __future__ import annotations

import os
import mimetypes
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
    get_engine,
)

app = FastAPI(
    title="VoxCraft TTS Studio",
    description="Enterprise-grade text-to-speech studio powered by Supertonic 3",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    merge: bool = Field(default=False, description="Merge all audio into single file")


class SynthesizeResponse(BaseModel):
    success: bool
    audio_url: str
    duration_seconds: float
    id: str
    text: str
    voice: str
    language: str
    sample_rate: int = 44100


class ErrorResponse(BaseModel):
    success: bool = False
    error: str


# ─── API Endpoints ──────────────────────────────────────────────────────────

@app.get("/api/health")
async def health() -> dict:
    """Health check with engine status."""
    try:
        engine = get_engine()
        ready = engine.is_ready
    except Exception:
        ready = False
    return {
        "status": "healthy" if ready else "initializing",
        "engine_ready": ready,
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
async def synthesize(req: SynthesizeRequest) -> dict:
    """Generate speech from text with selected voice and parameters."""
    engine = get_engine()
    if not engine.is_ready:
        raise HTTPException(status_code=503, detail="TTS engine is not ready — model still downloading")

    try:
        wav, duration = engine.synthesize(
            text=req.text,
            voice=req.voice,
            lang=req.language,
            speed=req.speed,
            quality=req.quality,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    meta = engine.export_for_platform(wav, req.text, req.voice, req.language, duration_seconds=duration)
    return SynthesizeResponse(
        success=True,
        audio_url=f"/api/audio/{meta['filename']}.wav",
        duration_seconds=meta["duration_seconds"],
        id=meta["id"],
        text=req.text,
        voice=req.voice,
        language=req.language,
    )


@app.post("/api/synthesize/batch")
async def synthesize_batch(req: BatchSynthesizeRequest) -> dict:
    """Generate speech for multiple texts."""
    engine = get_engine()
    if not engine.is_ready:
        raise HTTPException(status_code=503, detail="TTS engine is not ready")

    results = []
    total_duration = 0.0
    for i, text in enumerate(req.texts):
        if not text.strip():
            continue
        try:
            wav, duration = engine.synthesize(
                text=text, voice=req.voice, lang=req.language,
                speed=req.speed, quality=req.quality,
            )
            meta = engine.export_for_platform(wav, text, req.voice, req.language, duration_seconds=duration)
            meta["index"] = i
            total_duration += duration
            results.append(meta)
        except Exception as e:
            results.append({"index": i, "text": text, "error": str(e), "success": False})

    return {
        "success": True,
        "total_items": len(results),
        "total_duration_seconds": round(total_duration, 2),
        "results": results,
    }


@app.get("/api/history")
async def get_history(limit: int = Query(default=50, ge=1, le=200)) -> list[dict]:
    """Get recent generation history."""
    return get_engine().get_history(limit=limit)


@app.get("/api/audio/{filename:path}")
async def serve_audio(filename: str) -> Response:
    """Serve a generated audio file."""
    safe_name = os.path.basename(unquote(filename))
    audio_path = EXPORTS_DIR / safe_name
    if not audio_path.exists():
        audio_path = EXPORTS_DIR / f"{safe_name}.wav"
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(str(audio_path), media_type="audio/wav")


@app.delete("/api/history/{generation_id}")
async def delete_history(generation_id: str) -> dict:
    """Delete a generation from history."""
    count = 0
    for f in Path(config.DATA_DIR).rglob(f"*{generation_id}*"):
        try:
            os.remove(f)
            count += 1
        except OSError:
            pass
    return {"success": True, "deleted": generation_id, "files_removed": count}


# ─── Frontend SPA Catch-all (must be LAST — matches after API routes) ───────

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str) -> Response:
    """Serve frontend static files or fall back to index.html (SPA)."""
    # Block any /api paths from reaching here (shouldn't happen, but safety)
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")

    # If empty path, serve index.html
    if not full_path:
        return HTMLResponse(INDEX_HTML.read_bytes() if INDEX_HTML.exists() else "<h1>Not found</h1>", status_code=200)

    requested = FRONTEND_DIR / full_path
    # Security: only serve files inside FRONTEND_DIR
    try:
        requested.relative_to(FRONTEND_DIR)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid path")

    if requested.exists() and requested.is_file():
        content_type, _ = mimetypes.guess_type(str(requested))
        return FileResponse(str(requested), media_type=content_type or "application/octet-stream")

    # SPA fallback: every unmatched path serves index.html
    if INDEX_HTML.exists():
        return HTMLResponse(INDEX_HTML.read_bytes(), status_code=200)
    return HTMLResponse("<h1>Frontend not built</h1>", status_code=200)


# ─── Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("╔══════════════════════════════════════════╗")
    print("║        VoxCraft TTS Studio v1.0          ║")
    print("║  Professional Text-to-Speech Studio      ║")
    print("╚══════════════════════════════════════════╝")
    print("")
    print(  "  Engine: Supertonic 3 (99M params, ONNX)")
    print(f"  Voices: {len(PRESET_VOICES)} styles available")
    print(f"  Languages: {len(LANGUAGES)} supported")
    print(f"  Server: http://{config.HOST}:{config.PORT}")
    print(f"  API Docs: http://{config.HOST}:{config.PORT}/docs")
    print("")
    uvicorn.run(app, host=config.HOST, port=config.PORT, log_level="info")
