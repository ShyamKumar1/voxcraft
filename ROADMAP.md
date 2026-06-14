# Roadmap

VoxCraft is a professional TTS studio built on Supertonic 3. This roadmap outlines where we're headed and where you can contribute.

## Vision

Make studio-quality text-to-speech accessible to everyone — zero cost, zero cloud, zero friction. VoxCraft should be the default tool anyone reaches for when they need a voiceover.

## v1.1 — Polish & Polish (target: community-driven)

- [ ] **MP3 & OGG export** — WAV is great; compressed formats are practical for web and social media
- [ ] **Dark/light theme toggle** — The dark theme is gorgeous, but some people prefer light
- [ ] **Audio trimming in the waveform** — Select a region in the waveform and export just that segment
- [ ] **Keyboard shortcut reference** — A `?` shortcut that shows all available shortcuts in a modal
- [ ] **Undo/redo for text editor** — Ctrl+Z/Y for the script textarea
- [ ] **Drag & drop text files** — Drop a `.txt` file onto the textarea to load it

## v1.2 — Power User Features

- [ ] **SSML support** — Richer markup beyond expression tags: `<break>`, `<emphasis>`, `<prosody>`
- [ ] **Voice preview samples** — Click a voice card to hear a 3-second sample before generating
- [ ] **Presets system** — Save and load named presets (voice + speed + quality + language combos)
- [ ] **Queue system** — Add multiple texts to a queue, process them in sequence, with progress bar
- [ ] **Export directly to video editor formats** — Timestamped SRT/CSV for subtitle sync
- [ ] **API key auth (optional)** — For server deployments; disabled by default for local use

## v1.3 — Ecosystem

- [ ] **Custom voice import UI** — Load Supertonic Voice Builder JSON files directly from the UI
- [ ] **Obsidian plugin** — Generate voiceovers directly from Obsidian notes
- [ ] **Raycast extension** — Select text anywhere on macOS, generate audio via keyboard shortcut
- [ ] **CLI tool** — `voxcraft generate "text" --voice M1 --output out.wav` for scripting
- [ ] **Docker image** — One-command deployment: `docker run -p 8765:8765 shyamkumar1/voxcraft`
- [ ] **GitHub Pages demo** — A live demo with pre-generated samples for people to hear before installing

## v2.0 — Beyond the Desktop

- [ ] **Web version** — Run the engine in-browser via ONNX Runtime Web (WebGPU)
- [ ] **Mobile PWA** — Install as a standalone app on iOS/Android
- [ ] **Multi-language project mode** — One project, multiple languages, unified export
- [ ] **Collaboration** — Share voice presets and scripts via GitHub Gists

## How to Contribute

Every item marked with `[ ]` is an opportunity. Pick one, comment on the issue (or open one if it doesn't exist yet), and start building.

High-impact areas for new contributors:

1. **Frontend polish** — HTML, CSS, vanilla JS. No framework. No build step. Just open `frontend/index.html` and edit.
2. **Backend features** — Python + FastAPI. Add an endpoint, write a test, ship it.
3. **Documentation & tutorials** — Wiki pages, video demos, blog posts.
4. **Testing** — Edge cases, integration tests, performance benchmarks.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.
