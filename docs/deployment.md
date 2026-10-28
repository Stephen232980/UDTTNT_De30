# Deployment Guide

## Yêu cầu
Python tương thích với dependencies trong `requirements.txt`; truy cập ghi vào thư mục dự án (hoặc đường dẫn `BLOOD_DONATION_DB`). Không cần API key cho demo.

## Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Mở `http://127.0.0.1:8000`. Swagger UI: `/docs`. Test: `pytest -q`.

## Cấu hình
- `BLOOD_DONATION_DB`: đường dẫn file SQLite; mặc định `data/blood_donation.db`.
- `OPENAI_API_KEY`: tùy chọn, bật gọi dịch vụ chat-completions tương thích.
- `OPENAI_BASE_URL`: tùy chọn; mặc định OpenAI `/v1/chat/completions`.
- `OPENAI_MODEL`: tùy chọn; mặc định `gpt-4o-mini`.

Đặt secrets trong environment/secret manager, không ghi vào repo. Khởi động lần đầu tạo schema và dữ liệu demo; seed dùng chung mật khẩu demo, chỉ dùng local và tuyệt đối không triển khai công khai nguyên trạng.

## Vận hành và giới hạn
Ứng dụng chạy lệnh `uvicorn main:app --reload` phù hợp phát triển, không phải cấu hình production. Trước triển khai thật cần server ASGI phù hợp, HTTPS/reverse proxy, bỏ reload, credential bootstrap an toàn, durable session, CORS allowlist khi cần, logging/monitoring, backup và restore SQLite, retention/privacy policy, migration có backup, rate limiting và security review. SQLite/WAL và session RAM hiện tại giới hạn multi-worker/HA. Notification không gửi email/SMS. Không dùng dữ liệu người hiến máu thật trên demo.
