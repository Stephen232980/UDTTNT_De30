# Architecture Decision Records

Các quyết định hiện trạng dưới đây được suy ra từ code; chưa phải phê duyệt kiến trúc của stakeholder.

## ADR-001: FastAPI phục vụ API và SPA tĩnh
- **Trạng thái:** Đã triển khai.
- **Bối cảnh:** Ứng dụng demo nhỏ cần chạy với một lệnh.
- **Quyết định:** FastAPI phục vụ `index.html`, static assets và JSON API trong cùng process.
- **Hệ quả:** Triển khai đơn giản; frontend/API release gắn với nhau, chưa có CDN/build pipeline.

## ADR-002: SQLite cho persistence
- **Trạng thái:** Đã triển khai.
- **Quyết định:** Dùng SQLite file, foreign keys bật mỗi connection, WAL; transaction `BEGIN IMMEDIATE` cho booking và sửa campaign.
- **Hệ quả:** Demo cục bộ dễ chạy; giới hạn scale/HA và vận hành nhiều worker cần đánh giá.

## ADR-003: Session token trong process memory
- **Trạng thái:** Đã triển khai, chỉ phù hợp demo.
- **Quyết định:** Sinh token ngẫu nhiên và lưu user trong `SESSIONS` dictionary; logout xóa token.
- **Hệ quả:** Restart làm mất session; worker khác không nhận token; không có expiration/persistence. Production cần thiết kế lại.

## ADR-004: Mật khẩu PBKDF2
- **Trạng thái:** Đã triển khai.
- **Quyết định:** PBKDF2-HMAC-SHA256, random 16-byte salt, 180.000 iterations, constant-time compare.
- **Hệ quả:** Không lưu mật khẩu rõ; tham số/rehash policy cần quản trị theo threat model và benchmark.

## ADR-005: Assistant dùng tài liệu procedure và provider tùy chọn
- **Trạng thái:** Đã triển khai ở dạng keyword retrieval.
- **Quyết định:** Token giao với tiêu đề tài liệu để chọn nguồn; provider OpenAI-compatible chỉ dùng nếu cấu hình key; có fallback nội bộ.
- **Hệ quả:** Không phụ thuộc API key để chạy demo, nhưng chất lượng retrieval đơn giản; không có vector RAG/microservice. Câu hỏi y tế cá nhân bị chặn.

## ADR-006: Notification chỉ ghi nhận trong DB
- **Trạng thái:** Đã triển khai demo.
- **Quyết định:** Sinh nội dung và ghi notification; không gửi SMS/email.
- **Hệ quả:** Không phát sinh gửi ngoài; giao diện phải tiếp tục hiển thị rõ giới hạn này.

## Đề xuất cần phê duyệt
Trước production: durable shared session/auth, HTTPS, quản lý secrets và loại bỏ demo credentials, CORS allowlist nếu cần cross-origin, backups/retention, audit logs, kiểm soát dữ liệu cá nhân, provider review, delivery adapter có consent/retry, và schema migrations có backup. Đây là khuyến nghị, chưa triển khai.
