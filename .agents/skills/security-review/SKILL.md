---
name: security-review
description: "Use when assessing authentication, authorization, injection, XSS, CSRF, password hashing, secrets, or donor-data privacy in Mạch Đỏ."
---

# Security Review

## Checklist
- SQL injection: ensure every user value is passed as a bound parameter; inspect dynamic query fragments and sort/filter input.
- XSS: audit every dynamic HTML interpolation, escaping helper, URL/attribute context, and AI response rendering.
- CSRF/session: document bearer-token transport and storage, token entropy/revocation, process-local session limitations, cookie policy if introduced, and cross-origin behavior. Assess CSRF according to the actual credential transport.
- Authentication/authorization: test unauthenticated access, role escalation, donor ownership, registration role assignment, logout, and endpoint-level enforcement.
- Passwords: verify PBKDF2-HMAC-SHA256, unique salt, iteration count, constant-time comparison, minimum password length, and demo credential risks.
- Secrets: search tracked files, logs, environment examples, and history for real credentials; report hardcoded demo values separately from provider secrets.
- CORS: confirm whether middleware/policy is configured; do not report it enabled without evidence.
- Privacy/AI: ensure medical questions are blocked before provider calls, retrieval is restricted to approved documents, PII is minimized, and fallback is safe.
- Reliability: review upstream timeout, error handling, SQLite foreign-key enforcement, and destructive operations.

Classify findings with evidence and severity. Distinguish implemented controls, test evidence, and remediation recommendations. A passing demo test suite is not a production security certification.
