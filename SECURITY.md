# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 1.x (main) | ✅ |

## Reporting a Vulnerability

**Do not open a public issue to report a security vulnerability.**

Instead, please report vulnerabilities privately via one of these channels:

- **GitHub Security Advisories:** Go to the [Security tab](https://github.com/ShyamKumar1/voxcraft/security/advisories) and click "Report a vulnerability"
- **Email:** If the advisory system is not available, contact the maintainers directly

### What to Include

- A clear description of the vulnerability
- Steps to reproduce
- Affected versions
- Potential impact
- Suggested fix (if you have one)

### What to Expect

- **Acknowledgment:** Within 48 hours
- **Assessment:** Within 5 business days
- **Fix timeline:** Critical vulnerabilities will be patched as quickly as possible
- **Disclosure:** We will coordinate public disclosure with you after the fix is released

## Security Design

VoxCraft is designed to run **100% locally** — no data leaves your machine. Key security properties:

- No telemetry, no analytics, no phoning home
- No API keys required for core functionality
- File paths validated against path traversal (see `backend/app.py:212`)
- Audio exports stored locally in `data/exports/`
- CORS is permissive (`*`) for local development convenience; if deploying to a server, lock down `allow_origins` to your domain

## Scope

Security reports about these areas are in scope:

- Path traversal attacks via the `/api/audio/{filename}` endpoint
- Server-side request forgery (SSRF)
- Denial of service via unauthenticated endpoints
- Any vulnerability that could expose data from the host machine

Out of scope:

- Attacks requiring physical access to the machine
- Social engineering
- Vulnerabilities in third-party dependencies (supertonic, FastAPI, etc.) — report those upstream
