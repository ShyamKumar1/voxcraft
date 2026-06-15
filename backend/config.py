"""VoxCraft backend configuration — all values overridable via environment."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = os.getenv("VOXCRAFT_DATA_DIR", str(PROJECT_ROOT / "data"))
HOST = os.getenv("VOXCRAFT_HOST", "127.0.0.1")
PORT = int(os.getenv("VOXCRAFT_PORT", "8765"))
LOG_LEVEL = os.getenv("VOXCRAFT_LOG_LEVEL", "INFO")
MAX_CONCURRENCY = int(os.getenv("VOXCRAFT_MAX_CONCURRENCY", "4"))
SUPERTONIC_AUTO_DOWNLOAD = os.getenv("SUPERTONIC_AUTO_DOWNLOAD", "true").lower() == "true"

# Database path (relative to DATA_DIR)
DB_PATH = str(Path(DATA_DIR) / "voxcraft.db")
