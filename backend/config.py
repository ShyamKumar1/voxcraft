"""VoxCraft backend configuration."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = os.getenv("VOXCRAFT_DATA_DIR", str(PROJECT_ROOT / "data"))
HOST = os.getenv("VOXCRAFT_HOST", "0.0.0.0")
PORT = int(os.getenv("VOXCRAFT_PORT", "8765"))
