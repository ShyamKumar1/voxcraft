# VoxCraft Roadmap

VoxCraft is a professional TTS studio powered by Supertonic 3 — 100% local, 10 voices, 31 languages, free forever.

This roadmap is a living document. Priorities shift based on community interest and contributions.

---

## v1.0 (Current)

- [x] FastAPI backend with 7 endpoints
- [x] 10 voice styles (M1–M5, F1–F5)
- [x] 31 language support
- [x] 6 expression tags (laugh, breath, sigh, whisper, cough, say)
- [x] Speed control (0.7×–2.0×)
- [x] Quality control (5–12 denoising steps)
- [x] WaveSurfer.js waveform preview
- [x] Batch mode
- [x] Generation history with search
- [x] 44.1kHz 16-bit WAV export
- [x] Keyboard shortcuts
- [x] MIT license

---

## v1.1 — Polish & Ecosystem

**Target:** Make VoxCraft feel like a polished product, not a prototype.

### MP3 & Additional Export Formats
Add MP3 (via pydub/ffmpeg), OGG, and FLAC export options alongside WAV. Different platforms have different format requirements — Instagram wants MP4, podcasts want MP3, audiobooks need chapter markers.

**Complexity:** Easy · **Tags:** `good first issue`, `backend`, `frontend`

### Dark/Light Theme Toggle
Add a theme switcher with a polished light mode. The current dark theme is beautiful but some users prefer light mode for daytime editing.

**Complexity:** Easy · **Tags:** `good first issue`, `frontend`

### Voice Preview Buttons
Add a small play button on each voice card in the selector that plays a 3-second preview of that voice speaking a standard phrase. Currently you have to generate full audio just to audition a voice.

**Complexity:** Medium · **Tags:** `frontend`, `backend`, `voice`

### Undo/Redo in Text Editor
Simple undo/redo support for the script textarea. Currently Ctrl+Z works natively, but a dedicated button + extended history would improve the editing experience.

**Complexity:** Easy · **Tags:** `good first issue`, `frontend`

### Download History as ZIP
Allow downloading all history items or selected items as a ZIP archive from the server.

**Complexity:** Medium · **Tags:** `backend`, `frontend`

### Text Statistics
Show word count, estimated duration, and reading time alongside the character count in the editor.

**Complexity:** Easy · **Tags:** `good first issue`, `frontend`

---

## v1.2 — Power Features

**Target:** Features that professional content creators actually need.

### SSML Support
Full or partial SSML (Speech Synthesis Markup Language) support beyond the current expression tags. Includes `<prosody>`, `<break>`, `<emphasis>`, and `<phoneme>`.

**Complexity:** Hard · **Tags:** `tts-engine`, `backend`

### Custom Voice Import UI
A UI flow for importing custom voice JSON files from Supertonic Voice Builder. Currently requires manual code changes.

**Complexity:** Medium · **Tags:** `frontend`, `backend`, `voice`

### Audio Trimming & Normalization
Basic post-processing: trim silence from start/end, normalize volume, fade in/out.

**Complexity:** Medium · **Tags:** `backend`, `performance`

### Chapter Marks for Audiobooks
Add chapter markers to exports. Generate a single WAV with embedded chapter metadata for audiobook platforms.

**Complexity:** Medium · **Tags:** `backend`, `tts-engine`

### Real-time Streaming Preview
Stream audio as it's being generated instead of waiting for the full file. Reduces perceived latency for long texts.

**Complexity:** Hard · **Tags:** `tts-engine`, `backend`, `frontend`

---

## v2.0 — Collaborative & Multi-Platform

**Target:** VoxCraft as a platform, not just a tool.

### Multi-Voice Script Editor
Assign different voices to different paragraphs or sentences within a single script. Generate a multi-voice dialogue scene in one go.

**Complexity:** Hard · **Tags:** `frontend`, `backend`, `voice`

### Project Files
Save/load complete studio sessions as `.voxcraft` project files — text, voice selections, parameters, and generated audio references all in one file.

**Complexity:** Medium · **Tags:** `frontend`, `backend`

### Docker Deployment
Official Docker image for one-command deployment on any server. Includes the Supertonic model pre-cached for faster startup.

**Complexity:** Medium · **Tags:** `backend`, `dependencies`

### REST API Authentication
Optional API key authentication for server deployments. Currently the API is wide open (designed for localhost).

**Complexity:** Medium · **Tags:** `backend`

### Plugin System
A hooks-based plugin system for the backend — custom preprocessors, postprocessors, and exporters. Community voices, effects, and integrations.

**Complexity:** Hard · **Tags:** `backend`

---

## Community Wishlist

These are ideas from the community that haven't been prioritized yet:

- **Pronunciation dictionary** — Custom word pronunciations per language
- **Emotion presets** — One-click emotional tone (happy, sad, urgent, calm)
- **Auto-punctuation** — Smart punctuation insertion for raw text
- **YouTube caption import** — Paste a YouTube URL and auto-extract transcript for voiceover
- **Mobile PWA** — Progressive Web App for mobile use
- **Voice morphing** — Blend between two voice styles
- **Background music mixing** — Add royalty-free background tracks
- **Subtitle export** — Generate SRT/VTT alongside audio
- **Accessibility checker** — WCAG compliance for the frontend

---

## How to Contribute

Pick an issue tagged `good first issue` from the [issue tracker](https://github.com/ShyamKumar1/voxcraft/issues). Read [CONTRIBUTING.md](https://github.com/ShyamKumar1/voxcraft/blob/main/CONTRIBUTING.md) for the full workflow.

Want to suggest a feature? Open a [Feature Request](https://github.com/ShyamKumar1/voxcraft/issues/new?template=feature_request.md) or start a [Discussion](https://github.com/ShyamKumar1/voxcraft/discussions).

---

*Last updated: June 2026*
