---
name: architecture-design
description: "Use when documenting or changing Mạch Đỏ architecture, FastAPI routes, SPA boundaries, SQLite persistence, or AI assistant flows."
---

# Architecture Design

## Required Representation
- Describe the deployed demo as one FastAPI process serving a static JavaScript/CSS SPA and JSON API, with SQLite persistence at `data/blood_donation.db` by default.
- Show browser, API/auth dependencies, SQLite tables, and the optional external OpenAI-compatible chat-completions endpoint.
- Model the assistant as retrieval over approved `procedures` rows using title-token overlap, optional LLM generation, and a local document fallback. Do not call this vector search or a separate RAG service unless implemented.
- Include role-based access, session-token flow, booking transaction, and medical-question refusal paths.
- Use Mermaid for diagrams and label optional, external, and demo-only components.

## Decision Records
For each material choice record context, decision, alternatives, consequences, risks, and status. Distinguish existing decisions from recommendations. Include security/privacy implications, concurrency, failure modes, and operational ownership.

## Review Checklist
- Diagram routes/data boundaries actually present in `main.py` and `static/app.js`.
- Document stateful process limitations (`SESSIONS` is in-memory) and SQLite WAL/foreign-key setup.
- Describe AI provider failure and absent-key behavior.
- Never imply SMS/email delivery, durable sessions, vector embeddings, or medical assessment where none exists.
- Keep architecture docs updated with API, schema, deployment, and tests.
