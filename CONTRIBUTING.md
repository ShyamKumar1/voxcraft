# Contributing to VoxCraft

Thanks for your interest in contributing. VoxCraft is a professional TTS studio built on Supertonic 3 — a lightning-fast, on-device, multilingual text-to-speech engine that runs 100% locally.

## Code of Conduct

Be respectful, constructive, and inclusive. Harassment or toxic behavior will not be tolerated.

## Quick Start

### Prerequisites

- Python 3.9+
- pip

### Setup

```bash
git clone https://github.com/ShyamKumar1/voxcraft.git
cd voxcraft
cd backend
pip install -r requirements.txt
```

The first run downloads the Supertonic 3 ONNX model (~400MB) from Hugging Face into `~/.cache/supertonic3/`. This is a one-time download.

### Running

```bash
python -m backend.app
```

Open http://localhost:8765 to use the studio. The API docs are at http://localhost:8765/docs.

## Project Structure

```
voxcraft/
├── backend/
│   ├── app.py           FastAPI server with all endpoints
│   ├── tts_engine.py    Supertonic wrapper (voices, synthesis, exports)
│   ├── config.py        Server configuration (env-var overridable)
│   └── requirements.txt
├── frontend/
│   └── index.html       Single-page application (no build step)
└── data/                Generated at runtime (gitignored)
    ├── exports/         Generated WAV + JSON metadata
    └── history/         Generation history
```

## How to Contribute

### 1. Pick an Issue

Check the [open issues](https://github.com/ShyamKumar1/voxcraft/issues). Issues tagged `good first issue` are ideal for new contributors. Comment on the issue to let others know you're working on it.

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Your Changes

- Follow the existing code style. The backend uses Python 3.14 with type hints (`from __future__ import annotations`).
- Keep the frontend vanilla JS — no frameworks, no build step. This is intentional.
- Test your changes locally before opening a PR.

### 4. Open a Pull Request

- Use the PR template (it loads automatically).
- Link the issue your PR addresses.
- Keep PRs focused — one feature or fix per PR.
- If your PR adds new Python dependencies, update `requirements.txt`.

### 5. Code Review

A maintainer will review your PR. Expect feedback. This is a collaboration — we want your contribution to land cleanly.

## What We're Looking For

**High-impact contributions:**

- **New voice styles** — Custom voice presets via Supertonic Voice Builder
- **UI polish** — Accessibility, responsive refinements, dark/light themes
- **Export formats** — MP3, OGG, FLAC support
- **SSML support** — Richer markup beyond expression tags
- **Performance** — Faster synthesis, better caching
- **Documentation** — Tutorials, examples, video demos
- **Testing** — Unit and integration tests

**What to avoid:**

- Replacing vanilla JS with React/Vue/Svelte (design decision — see below)
- Adding cloud API dependencies (the project is intentionally 100% local)
- Large refactors without prior discussion

## Design Philosophy

- **100% Local** — No API calls, no telemetry, no data leaves the machine
- **Zero Build Step** — The frontend is a single HTML file. No npm, no bundler
- **Python-First** — Backend in vanilla Python with FastAPI
- **Fast by Default** — The studio should feel instant, from launch to generation

## Questions?

Open a [discussion](https://github.com/ShyamKumar1/voxcraft/discussions) or ask in the issue tracker.
