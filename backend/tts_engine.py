"""VoxCraft TTS Engine — Professional-grade Supertonic wrapper.

Features:
- Multiple voice styles with preview
- 31 language support
- Speed and quality control
- Expression tags (laugh, breath, sigh)
- Batch text processing
- Audio caching for repeated phrases
- Progress tracking for long generations
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from supertonic import TTS

from . import config

DATA_DIR = Path(config.DATA_DIR)
EXPORTS_DIR = DATA_DIR / "exports"
HISTORY_DIR = DATA_DIR / "history"
VOICES_DIR = DATA_DIR / "voices"

for d in [EXPORTS_DIR, HISTORY_DIR, VOICES_DIR]:
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


class TTSEngine:
    """Enterprise-grade TTS engine with Supertonic."""

    def __init__(self, auto_download: bool = True):
        self._tts: TTS | None = None
        self._voice_cache: dict[str, Any] = {}
        self._ready = False

        try:
            self._tts = TTS(auto_download=auto_download)
            self._ready = True
            # Pre-cache default voice
            self._get_voice("M1")
        except Exception as e:
            print(f"TTS Engine init warning: {e}")

    @property
    def is_ready(self) -> bool:
        return self._ready

    def _get_voice(self, voice_name: str):
        if voice_name not in self._voice_cache:
            if self._tts is None:
                raise RuntimeError("TTS engine not initialized")
            self._voice_cache[voice_name] = self._tts.get_voice_style(voice_name=voice_name)
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
            raise RuntimeError("TTS engine is not ready. Install supertonic: pip install supertonic")

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        voice_style = self._get_voice(voice)
        quality = max(5, min(12, quality))
        speed = max(0.7, min(2.0, speed))

        wav, duration = self._tts.synthesize(
            text=text,
            lang=lang,
            voice_style=voice_style,
            total_steps=quality,
            speed=speed,
        )
        return wav, float(duration[0])

    def synthesize_batch(
        self,
        texts: list[str],
        voice: str = "M1",
        lang: str = "en",
        speed: float = 1.05,
        quality: int = 8,
    ) -> list[dict]:
        """Synthesize multiple texts and return combined results."""
        results = []
        for text in texts:
            if not text.strip():
                continue
            wav, duration = self.synthesize(text, voice, lang, speed, quality)
            results.append({"wav": wav, "duration": duration, "text": text})
        return results

    def save_audio(self, wav: np.ndarray, path: str | Path, sample_rate: int = 44100) -> str:
        """Save audio to a WAV file. Returns the absolute path."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Ensure mono
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
        duration_seconds: float | None = None,
        format: str = "wav",
    ) -> dict:
        """Export audio with metadata for content platforms.

        Args:
            wav: Audio array from synthesize()
            text: Original text that was synthesized
            voice: Voice style name used
            lang: Language code used
            duration_seconds: Actual duration from synthesize (preferred).
                             Falls back to computing from array length.
            format: Output format (default: wav)

        Returns:
            Metadata dict with id, filename, audio_path, etc.
        """
        # Use provided duration or compute from array shape
        if duration_seconds is not None:
            actual_duration = duration_seconds
        else:
            actual_duration = float(wav.shape[-1]) / 44100

        generation_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"voxcraft_{generation_id}_{timestamp}"

        export_path = EXPORTS_DIR / f"{filename}.{format}"
        audio_path = self.save_audio(wav, export_path)

        meta = {
            "id": generation_id,
            "filename": filename,
            "text": text,
            "voice": voice,
            "language": lang,
            "duration_seconds": round(actual_duration, 2),
            "format": format,
            "created_at": timestamp,
            "audio_path": audio_path,
        }

        # Save metadata file alongside audio
        meta_path = EXPORTS_DIR / f"{filename}.json"
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)

        # Add to history
        history_path = HISTORY_DIR / f"{filename}.json"
        with open(history_path, "w") as f:
            json.dump(meta, f, indent=2)

        return meta

    def get_history(self, limit: int = 50) -> list[dict]:
        """Get recent generation history."""
        history = []
        files = sorted(HISTORY_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
        for f in files[:limit]:
            try:
                with open(f) as fp:
                    history.append(json.load(fp))
            except (json.JSONDecodeError, OSError):
                continue
        return history

    def get_audio_data(self, path: str) -> bytes:
        """Read audio file and return raw bytes."""
        with open(path, "rb") as f:
            return f.read()


# Global engine singleton
_engine: TTSEngine | None = None


def get_engine() -> TTSEngine:
    global _engine
    if _engine is None:
        _engine = TTSEngine()
    return _engine
