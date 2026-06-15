"""VoxCraft TTS Engine — Professional-grade Supertonic wrapper.

Features:
- Multiple voice styles with preview
- 31 language support
- Speed and quality control
- Expression tags (laugh, breath, sigh)
- Concurrent batch text processing
- SQLite-backed persistence via data_store
- Progress tracking for long generations
"""

from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from . import config
from .data_store import save_export, get_history as db_get_history, init_db

logger = logging.getLogger("voxcraft.tts_engine")

DATA_DIR = Path(config.DATA_DIR)
EXPORTS_DIR = DATA_DIR / "exports"
VOICES_DIR = DATA_DIR / "voices"

for d in [EXPORTS_DIR, VOICES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class VoiceStyle:
    """Represents a TTS voice style with metadata."""

    def __init__(self, name: str, display_name: str, description: str, gender: str, tags: list[str] | None = None):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.gender = gender
        self.tags = tags or []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "gender": self.gender,
            "tags": self.tags,
        }


PRESET_VOICES: list[VoiceStyle] = [
    VoiceStyle("M1", "M1 — Warm Baritone", "Rich, deep male voice with natural warmth. Ideal for narration and storytelling.", "male", ["warm", "deep", "narration"]),
    VoiceStyle("M2", "M2 — Calm Tenor", "Smooth, even-toned male voice. Perfect for explainers and tutorials.", "male", ["calm", "smooth", "educational"]),
    VoiceStyle("M3", "M3 — Authoritative", "Strong, commanding male voice for announcements and promos.", "male", ["strong", "authoritative", "promo"]),
    VoiceStyle("M4", "M4 — Friendly", "Approachable, conversational male voice for casual content.", "male", ["friendly", "casual", "conversational"]),
    VoiceStyle("M5", "M5 — Deep Narrator", "Deep, resonant male voice for cinematic narration.", "male", ["deep", "cinematic", "narrator"]),
    VoiceStyle("F1", "F1 — Warm Alto", "Rich, expressive female voice. Great for stories and podcasts.", "female", ["warm", "expressive", "podcast"]),
    VoiceStyle("F2", "F2 — Bright Soprano", "Clear, energetic female voice for tutorials and ads.", "female", ["bright", "energetic", "tutorial"]),
    VoiceStyle("F3", "F3 — Professional", "Polished, corporate female voice for business content.", "female", ["polished", "corporate", "business"]),
    VoiceStyle("F4", "F4 — Gentle", "Soft, soothing female voice for meditation and relaxation.", "female", ["soft", "soothing", "meditation"]),
    VoiceStyle("F5", "F5 — Energetic", "Upbeat, lively female voice for social media and promos.", "female", ["upbeat", "lively", "social"]),
]

LANGUAGES: dict[str, str] = {
    "en": "English", "hi": "हिन्दी (Hindi)", "ar": "العربية (Arabic)",
    "fr": "Français (French)", "de": "Deutsch (German)", "es": "Español (Spanish)",
    "pt": "Português (Portuguese)", "ru": "Русский (Russian)", "ja": "日本語 (Japanese)",
    "ko": "한국어 (Korean)", "zh": "中文 (Chinese)", "it": "Italiano (Italian)",
    "nl": "Nederlands (Dutch)", "pl": "Polski (Polish)", "tr": "Türkçe (Turkish)",
    "vi": "Tiếng Việt (Vietnamese)", "th": "ไทย (Thai)", "id": "Bahasa Indonesia",
    "ms": "Bahasa Melayu", "cs": "Čeština (Czech)", "sv": "Svenska (Swedish)",
    "da": "Dansk (Danish)", "fi": "Suomi (Finnish)", "nb": "Norsk (Norwegian)",
    "ro": "Română (Romanian)", "hu": "Magyar (Hungarian)", "el": "Ελληνικά (Greek)",
    "he": "עברית (Hebrew)", "uk": "Українська (Ukrainian)", "bg": "Български (Bulgarian)",
    "hr": "Hrvatski (Croatian)",
}

EXPRESSION_TAGS: dict[str, str] = {
    "laugh": "<laugh>",
    "breath": "<breath>",
    "sigh": "<sigh>",
    "cough": "<cough>",
    "whisper": "<whisper>",
    "say": "<say>",
}


class VoiceNotFoundError(ValueError):
    """Raised when a voice style name is not recognized."""
    pass


class EngineNotReadyError(RuntimeError):
    """Raised when the TTS engine is not initialized."""
    pass


class TTSEngine:
    """Enterprise-grade TTS engine with Supertonic."""

    def __init__(self, auto_download: bool = True):
        self._tts: Any = None
        self._voice_cache: dict[str, Any] = {}
        self._voice_lock = threading.Lock()
        self._ready = False
        self._executor = ThreadPoolExecutor(max_workers=config.MAX_CONCURRENCY)
        self._synthesis_count = 0
        self._synthesis_lock = asyncio.Lock()

        try:
            from supertonic import TTS
            self._tts = TTS(auto_download=auto_download)
            self._ready = True
            self._get_voice("M1")
            logger.info("Supertonic engine initialized with %d voices", len(PRESET_VOICES))
        except Exception as e:
            logger.critical("Failed to initialize Supertonic engine: %s", e)
            raise EngineNotReadyError(
                f"TTS engine could not be initialized. "
                f"Ensure supertonic is installed and the model is available. "
                f"Error: {e}"
            ) from e

        # Initialize SQLite database
        try:
            init_db()
        except Exception as e:
            logger.warning("Database initialization failed (non-fatal): %s", e)

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def active_syntheses(self) -> int:
        return self._synthesis_count

    def _get_voice(self, voice_name: str) -> Any:
        """Get voice style object, caching results. Thread-safe."""
        # Fast path: cache hit outside lock
        if voice_name in self._voice_cache:
            return self._voice_cache[voice_name]

        if self._tts is None:
            raise EngineNotReadyError("TTS engine not initialized")

        with self._voice_lock:
            # Double-check: another thread may have loaded it while we waited
            if voice_name in self._voice_cache:
                return self._voice_cache[voice_name]
            try:
                self._voice_cache[voice_name] = self._tts.get_voice_style(voice_name=voice_name)
            except (AttributeError, KeyError, ValueError) as e:
                raise VoiceNotFoundError(f"Voice style '{voice_name}' is not available") from e
            except Exception as e:
                raise VoiceNotFoundError(f"Voice style '{voice_name}' could not be loaded: {e}") from e
            return self._voice_cache[voice_name]

    def synthesize(
        self,
        text: str,
        voice: str = "M1",
        lang: str = "en",
        speed: float = 1.05,
        quality: int = 8,
    ) -> tuple[np.ndarray, float]:
        """Synthesize text to audio.

        Args:
            text: Input text to synthesize
            voice: Voice style name (M1-M5, F1-F5)
            lang: Language code
            speed: Speech speed (0.7–2.0)
            quality: Generation quality (5–12, higher = better but slower)

        Returns:
            Tuple of (audio_array, duration_seconds)
        """
        if not self._ready or self._tts is None:
            raise EngineNotReadyError("TTS engine is not ready. Install supertonic: pip install supertonic")

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Get voice (raises VoiceNotFoundError if invalid)
        voice_style = self._get_voice(voice)

        quality = max(5, min(12, quality))
        speed = max(0.7, min(2.0, speed))

        logger.debug("Synthesizing: voice=%s lang=%s speed=%.2f quality=%d text_len=%d",
                      voice, lang, speed, quality, len(text))

        try:
            wav, duration = self._tts.synthesize(
                text=text,
                lang=lang,
                voice_style=voice_style,
                total_steps=quality,
                speed=speed,
            )
            return wav, float(duration[0])
        except ValueError:
            raise
        except RuntimeError:
            raise
        except Exception as e:
            logger.error("Synthesis failed for voice=%s lang=%s: %s", voice, lang, e)
            raise RuntimeError("Speech synthesis failed") from e

    async def synthesize_batch(
        self,
        texts: list[str],
        voice: str = "M1",
        lang: str = "en",
        speed: float = 1.05,
        quality: int = 8,
    ) -> list[dict]:
        """Synthesize multiple texts concurrently. Partial failures are captured per-item."""
        loop = asyncio.get_running_loop()

        async def process_one(index: int, text: str) -> dict:
            async with self._synthesis_lock:
                self._synthesis_count += 1
            try:
                wav, duration = await loop.run_in_executor(
                    self._executor,
                    self.synthesize, text, voice, lang, speed, quality,
                )
                return {"index": index, "text": text, "wav": wav, "duration": duration, "success": True}
            except Exception as e:
                logger.warning("Batch item %d failed: %s", index, e, exc_info=True)
                return {"index": index, "text": text, "error": str(e), "success": False}
            finally:
                async with self._synthesis_lock:
                    self._synthesis_count -= 1

        tasks = [process_one(i, t) for i, t in enumerate(texts) if t.strip()]
        raw_results = await asyncio.gather(*tasks)

        # Sort by original index
        raw_results.sort(key=lambda r: r.get("index", 0))
        return raw_results

    def save_audio(self, wav: np.ndarray, path: str | Path, sample_rate: int = 44100) -> str:
        """Save audio to a WAV file. Returns the absolute path."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if wav.ndim > 1:
            wav = wav.squeeze()
        sf.write(str(path), wav, sample_rate)
        return str(path.resolve())

    def export_for_platform(
        self,
        wav: np.ndarray,
        text: str,
        voice: str,
        lang: str,
        duration_seconds: float,
        speed: float = 1.05,
        quality: int = 8,
        fmt: str = "wav",
    ) -> dict:
        """Export audio with metadata for content platforms.

        Uses SQLite-backed storage for atomic writes and data integrity.
        No duplicate JSON files — single source of truth in the database.
        """
        generation_id = uuid.uuid4().hex[:12]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"voxcraft_{generation_id}_{timestamp}"

        export_path = EXPORTS_DIR / f"{filename}.{fmt}"
        audio_path = self.save_audio(wav, export_path)

        meta = {
            "id": generation_id,
            "filename": filename,
            "text": text,
            "voice": voice,
            "language": lang,
            "duration_seconds": round(duration_seconds, 2),
            "format": fmt,
            "sample_rate": 44100,
            "speed": speed,
            "quality": quality,
            "created_at": timestamp,
            "audio_path": audio_path,
        }

        # Atomic write to SQLite (single source of truth)
        save_export(meta)
        logger.info("Exported %s (voice=%s lang=%s %.2fs)", filename, voice, lang, duration_seconds)

        return meta

    def get_history(self, limit: int = 50, search: str | None = None) -> list[dict]:
        """Get recent generation history from database."""
        return db_get_history(limit=limit, search=search)

    def delete_export(self, export_id: str) -> int:
        """Delete an export by ID. Returns number of rows deleted."""
        from .data_store import delete_export as db_delete
        return db_delete(export_id)


# Global engine singleton
_engine: TTSEngine | None = None


def get_engine() -> TTSEngine:
    global _engine
    if _engine is None:
        _engine = TTSEngine(auto_download=config.SUPERTONIC_AUTO_DOWNLOAD)
    return _engine
