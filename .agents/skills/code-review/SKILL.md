---
name: code-review
description: "Use when reviewing Mạch Đỏ changes for correctness, maintainability, performance, or error handling."
---

# Code Review

Review the diff and its callers/tests. Report actionable findings first, ordered by severity, with file and line references and a concise impact explanation.

## Criteria
- **Correctness:** API contracts, input boundaries, state transitions, race conditions, transaction rollback, timezone/date handling, and role behavior.
- **Maintainability:** cohesive functions, clear naming, compatibility, minimal duplication, readable docs, and traceability to tests.
- **Performance:** query counts, unbounded collections, indexes supported by actual access patterns, network timeouts, and concurrency behavior.
- **Error handling:** stable HTTP errors, rollback on failure, upstream/provider fallback, invalid/missing session handling, and useful user-facing feedback.
- Also inspect privacy and security for donor data, output escaping, authorization, password handling, and secrets.

Do not report style preferences as defects. Separate confirmed issues from assumptions, mention missing tests, and do not claim a review is a security certification.
