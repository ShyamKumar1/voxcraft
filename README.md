# VoxCraft — Professional TTS Studio

Enterprise-grade text-to-speech studio powered by **Supertonic 3**. Generate
studio-quality 44.1kHz voiceovers for Instagram Reels, YouTube videos, podcasts,
and content creation — all running 100% locally on your machine.

## Features

- **10 Voice Styles** — M1–M5 (male), F1–F5 (female), each with distinct character
- **31 Languages** — Including English, Hindi, Arabic, French, German, Japanese & more
- **Expression Tags** — `<laugh>`, `<breath>`, `<sigh>`, `<whisper>`, `<cough>`, `<say>`
- **Speed Control** — 0.7× to 2.0× without pitch distortion
- **Quality Settings** — Draft (fast) to Studio (best) — 5–12 denoising steps
- **Waveform Preview** — Interactive audio player with visual waveform
- **Batch Mode** — Process multiple texts at once
- **Generation History** — Full history with search and replay
- **Studio-Grade Output** — 44.1kHz 16-bit WAV
- **100% Local** — No API calls, no data leaves your machine

## Quick Start

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Start the server
python -m app

# Open the studio
open http://localhost:8765
```

## Tech Stack

- **Backend**: Python 3.14 · FastAPI · Supertonic 3 (99M params ONNX)
- **Frontend**: Vanilla JS · WaveSurfer.js · Modern CSS
- **TTS Engine**: [Supertonic 3](https://github.com/supertone-inc/supertonic) — 11k⭐, 99M params, 31 languages, no GPU needed

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `Ctrl+Enter` / `Cmd+Enter` | Generate speech |
| `Space` (when not typing) | Play / Pause |

## Cost

- **Software**: $0 — Fully open-source (Apache-2.0 / MIT)
- **Compute**: Your existing machine — M1 MacBook Air runs it effortlessly
- **TTS Engine**: $0 — Supertonic is free and runs locally

## Project Structure

```
voxcraft/
├── backend/
│   ├── app.py           FastAPI server with all endpoints
│   ├── tts_engine.py    Supertonic wrapper (voices, export, history)
│   └── config.py        Server configuration
├── frontend/
│   └── index.html       Single-page application (no build step)
└── data/
    ├── exports/         Generated audio files
    └── history/         Generation metadata
```
