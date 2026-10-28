# Kiến trúc hiện tại

## Tổng quan

```mermaid
flowchart LR
  Browser[Browser: SPA JavaScript/CSS] -->|JSON + Bearer token| API[FastAPI process]
  API --> Auth[Session + role dependencies]
  API --> DB[(SQLite: 7 tables)]
  API -->|Optional HTTPS chat-completions| LLM[OpenAI-compatible provider]
  DB --> Proc[procedures: approved content]
  Proc --> Retrieve[Title-token retrieval]
  Retrieve --> API
  API -->|Fallback when key absent/failure| Browser
```

Đây là một ứng dụng FastAPI duy nhất, không có frontend build step. `GET /` trả `static/index.html`; `/static` phục vụ JS/CSS. Cùng process cung cấp API `/api/*` và SQLite. Mặc định DB nằm tại `data/blood_donation.db`, có thể thay bằng `BLOOD_DONATION_DB`.

## Thành phần và dữ liệu
- **SPA:** `static/app.js` dựng giao diện theo vai trò, lưu token/user trong `sessionStorage`, gửi bearer token và escape nội dung template qua `esc`; nội dung AI đưa vào `textContent`.
- **API:** `main.py` định nghĩa Pydantic input models, login/register, dependencies `signed_in`/`roles`, nghiệp vụ campaign/slots/appointments, thống kê, notification và assistant.
- **Persistence:** `connect()` bật SQLite foreign keys và WAL. Đặt chỗ dùng `BEGIN IMMEDIATE`, kiểm tra quyền sở hữu, trạng thái campaign, lịch trùng và sức chứa trước insert.
- **AI:** `ai_call()` là lời gọi outbound tùy chọn tới URL OpenAI-compatible, key/model/base URL cấu hình qua environment. `answer` truy xuất tối đa hai procedure dựa trên token trùng title; nếu không có nguồn phù hợp thì trả thông báo không tìm thấy. Khi không dùng được provider, dùng nội dung procedure. Không có embedding/vector store hoặc microservice RAG riêng.
- **Thông báo:** được ghi vào bảng `notifications`; không có tích hợp SMS/email.

## Luồng đặt lịch

```mermaid
sequenceDiagram
  participant V as Volunteer SPA
  participant F as FastAPI
  participant S as SQLite
  V->>F: POST /api/appointments (Bearer, donor_id, slot_id)
  F->>S: BEGIN IMMEDIATE
  F->>F: Verify donor ownership, campaign, overlap, capacity
  alt Valid and capacity available
    F->>S: INSERT appointment + COMMIT
    F-->>V: 201 appointment
  else Rejected
    F->>S: ROLLBACK
    F-->>V: 403/404/409
  end
```

## Giới hạn vận hành
Token session ở dictionary trong RAM, mất khi process restart và không chia sẻ giữa nhiều workers. SQLite phù hợp demo đơn tiến trình; WAL không thay thế backup/HA. API không cấu hình CORS middleware trong source hiện tại. Không dùng dữ liệu cá nhân/y tế thật trong demo.
