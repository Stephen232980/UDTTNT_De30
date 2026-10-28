---
name: implementation
description: "Use when implementing or modifying Mạch Đỏ Python/FastAPI, SQLite, or vanilla JavaScript SPA code."
---

# Implementation

## Conventions
- Keep the current small-project structure: `main.py`, `static/`, `data/`, `test_app.py`, and `docs/`; avoid unnecessary frameworks or layers.
- Use typed Pydantic request models and explicit FastAPI dependencies for authentication and role checks.
- Use parameterized SQLite queries, short context-managed connections, explicit transactions for multi-step booking/edit operations, and enable foreign keys per connection.
- Normalize login email with `strip().lower()`. Validate inputs at the API boundary and return appropriate HTTP status codes without leaking internal details.
- Escape untrusted strings in HTML templates; use `textContent` for AI output. Do not interpolate untrusted values into executable markup without escaping.
- Handle missing API keys, upstream failures, and network errors with bounded timeouts and safe fallbacks.

## Security
- Hash passwords with PBKDF2-HMAC-SHA256, a unique random salt, and constant-time digest comparison. Keep parameters configurable through a reviewed migration plan; never store plaintext passwords.
- Do not commit real credentials. Treat demo credentials as local-only and disclose their status. Read provider secrets from environment configuration.
- Enforce permissions on the server, not only by hiding UI controls. Avoid sending donor PII to AI providers.
- Keep public APIs and existing behavior stable unless the task explicitly requires a change; add focused regression tests for behavior changes.
