# Community Launch Posts

Copy-paste ready. Replace `[your text]` placeholders.

---

## 1. Reddit — r/selfhosted

**Title:** VoxCraft — a 100% local, free TTS studio with 10 voices, 31 languages (no API, no cloud, no GPU)

**Body:**

I built a desktop TTS studio that runs entirely on your machine — no API keys, no cloud, no GPU needed. It wraps Supertonic 3 (99M-parameter ONNX model) in a FastAPI backend + vanilla JS frontend.

What it does:
- 10 voice styles (5 male, 5 female) each with distinct character
- 31 languages — English, Hindi, Japanese, Arabic, French, German, and more
- Expression tags like <laugh>, <breath>, <sigh>, <whisper> for natural speech
- Speed 0.7x–2.0x and quality 5–12 steps
- 44.1kHz WAV output, WaveSurfer.js waveform preview
- Batch mode, generation history, keyboard shortcuts
- Zero telemetry, zero phoning home

Stack: Python + FastAPI + ONNX Runtime. Frontend is a single HTML file.

GitHub: https://github.com/ShyamKumar1/voxcraft
Install: `pip install -r requirements.txt && python -m backend.app`

It's MIT licensed. Looking for contributors — have 6 "good first issue" tickets ready. Would love feedback from the self-hosted crowd.

---

## 2. Hacker News — Show HN

**Title:** Show HN: VoxCraft — Free, local TTS studio (no API, no GPU, 31 languages)

**Body:**

Built a desktop TTS studio around Supertonic 3, a 99M-parameter open-weight ONNX model from Supertone Inc. Runs entirely on CPU — my M1 MacBook Air handles it without breaking a sweat.

Why I built it: existing TTS tools are either expensive APIs (ElevenLabs, OpenAI TTS) or complex command-line tools. I wanted something I could open, type text, pick a voice, and get studio-quality audio — no accounts, no credits, no internet.

Technical details:
- Backend: Python 3.11+, FastAPI, Supertonic 3 via ONNX Runtime
- Frontend: Single HTML file, vanilla JS, WaveSurfer.js for waveform preview
- Output: 44.1kHz 16-bit WAV
- 10 voice presets (M1–M5 male, F1–F5 female)
- Expression tags: <laugh>, <breath>, <sigh>, <whisper>, <cough>, <say>

Comparison with ElevenLabs on a 1000-char text: VoxCraft generates in ~15s (local, free, private) vs ElevenLabs ~7s (cloud, paid, your text leaves your machine).

Open source (MIT), looking for contributors. Have 6 scoped "good first issue" tickets up.

https://github.com/ShyamKumar1/voxcraft

---

## 3. Supertonic GitHub — Discussion Post

**Title:** Built a desktop TTS studio GUI for Supertonic 3 — VoxCraft

**Body:**

Hey Supertonic team — love the v3 release. The 31-language support and expression tags are incredible.

I built a desktop studio around it to make it more accessible: https://github.com/ShyamKumar1/voxcraft

It's a FastAPI backend + vanilla JS single-page frontend. Features:
- Visual voice selection (10 presets with descriptions)
- Speed slider, quality slider, language dropdown
- WaveSurfer.js waveform preview with play/pause
- Batch mode for multiple texts
- Generation history with search
- Keyboard shortcuts (Cmd+Enter to generate, Space to play)

Everything is local, MIT licensed. Would love feedback from the Supertonic community — especially on voice quality tuning and any quirks I should know about with the ONNX runtime.

---

## 4. Reddit — r/Python

**Title:** I built a Python TTS studio with FastAPI + Supertonic 3 — 100% local, 31 languages

**Body:**

Sharing a project I built: VoxCraft — a text-to-speech studio powered by Supertonic 3.

Tech stack:
- Backend: FastAPI, Pydantic validation, ONNX Runtime (no GPU needed)
- Frontend: Single HTML file, vanilla JS, WaveSurfer.js
- TTS Engine: Supertonic 3 (99M params, ONNX)
- Testing: pytest with 42 tests, GitHub Actions CI

It's fully open source (MIT). Looking for Python devs who want to contribute — I've got 6 "good first issue" tickets up covering backend features, testing, and integrations.

GitHub: https://github.com/ShyamKumar1/voxcraft

---

## Posting Strategy

Best order (spaced 24-48h apart for max visibility):

1. **First:** Post on Supertonic GitHub Discussions — their 44k monthly PyPI users are your warmest audience
2. **Second:** r/selfhosted — they love local-first tools
3. **Third:** r/Python — Monday-Thursday mornings EST
4. **Fourth:** Hacker News Show HN — Friday morning PST for maximum weekend attention

Also: Star the Supertonic repo, then comment on their README or issues mentioning VoxCraft. Cross-pollination works.
