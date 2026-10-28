# Security Review

## Phạm vi và kết luận
Rà soát tĩnh `main.py`, `static/app.js`, schema và test hiện có. Kết luận: có một số kiểm soát hữu ích cho demo; **không phải security certification** và chưa đủ để chứa dữ liệu cá nhân/y tế thật.

## Checklist

| Chủ đề | Quan sát | Đánh giá |
|---|---|---|
| SQL injection | Query với dữ liệu request dùng placeholder; một số SQL fragment được nối là constant nội bộ. | Có kiểm soát tốt theo source đã rà soát. |
| XSS | `app.js` có `esc()` khi dựng nhiều HTML động; AI response render qua `textContent`. | Giảm rủi ro; cần kiểm thử payload XSS qua mọi field/UI context. |
| Authentication | Email/password; token entropy do `secrets.token_urlsafe(32)`; logout xóa token. | Session process-local, không expiry/persistence. |
| Authorization | `roles()` và `signed_in`; volunteer bị giới hạn profile/booking/list. | Có kiểm thử một số đường; cần phủ role trên toàn bộ route. |
| PBKDF2 | PBKDF2-HMAC-SHA256, 16-byte random salt, 180.000 rounds, `hmac.compare_digest`. | Đúng kỹ thuật cơ bản; hardcoded demo password vẫn là rủi ro lớn. |
| Secrets | OpenAI key đọc từ `OPENAI_API_KEY`; base URL/model configurable. Có `DEMO_PASSWORD = "HienMau2026!"` và tài khoản demo seed. | Không có key provider hardcoded; demo password là credential cố định, không dùng production. |
| CORS | Không thấy cấu hình CORS middleware trong `main.py`. | API hiện dự kiến same-origin; cross-origin chưa được policy bảo vệ/cấp phép rõ ràng. |
| CSRF | Token gửi qua Authorization Bearer header, UI giữ trong `sessionStorage`; không dùng cookie auth trong code hiện tại. | Rủi ro CSRF cổ điển thấp hơn cookie tự gửi; XSS/session theft vẫn quan trọng. Không có CSRF token mechanism. |
| Validation | Pydantic có type/length/pattern/range; một số trường text như phone/venue không có format/domain check. | Validation một phần; DB thiếu nhiều CHECK constraints. |
| AI/privacy | Câu hỏi có từ khóa y tế bị chặn trước `ai_call`; reminder prompt không chứa tên/số phone theo test; answer chỉ dùng procedure lấy từ DB. | Có guardrails demo; keyword block không đầy đủ, cần red-team và privacy review. |
| Provider | Timeout 20s, một số lỗi được fallback. | Lỗi HTTP khác ngoài URLError/timeout có thể cần xử lý nhất quán; test lỗi provider chưa đủ. |
| Data integrity | Mỗi connection bật FK; DB có UNIQUE cho username, slot start, donor-slot. | Không cascade; status/capacity không có DB CHECK; backup/retention chưa cấu hình. |

## Ưu tiên trước production
1. Loại bỏ demo credentials, thay bootstrap account an toàn và quản lý secrets ngoài source.
2. Bổ sung session expiry, durable/shared store, HTTPS và chính sách lưu trữ token.
3. Chốt CORS allowlist nếu cần cross-origin; triển khai security headers/rate limits theo threat model.
4. Hoàn thiện authorization tests, validation, DB constraints/migrations, audit và backup.
5. Đánh giá legal/privacy cho donor data; rà soát provider, retention và consent.
6. Kiểm thử XSS và khả năng vượt medical keyword filter; giữ con người/y tế chịu trách nhiệm quyết định.
