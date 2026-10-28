# API Reference

Base URL local: `http://127.0.0.1:8000`. JSON endpoints dùng UTF-8 (`Content-Type: application/json; charset=utf-8` cho các API AI). Các endpoint ghi `Bearer` yêu cầu header `Authorization: Bearer <token>`. Lỗi FastAPI thường trả JSON `{ "detail": "..." }`.

| Method | Path | Auth | Tóm tắt |
|---|---|---|---|
| GET | `/` | Không | SPA index. |
| POST | `/api/register` | Không | Tạo donor lưu email + volunteer login; 201, email trùng hoặc email hệ thống 400. Role gửi trong body không quyết định quyền. |
| POST | `/api/login` hoặc `/api/auth/login` | Không | Đăng nhập; trả token/user gồm role lấy từ DB; lỗi 401, tài khoản bị khóa 403. Auth View để trống các ô và dùng placeholder; không điền sẵn credential demo. |
| POST | `/api/auth/logout` | Bearer | Thu hồi token hiện tại. |
| GET | `/api/dashboard` | Admin/coordinator | Stats, nhóm máu, recent, campaigns. |
| GET | `/api/donors` | Admin/coordinator | Danh sách donor. |
| GET | `/api/donors/me` | Bearer | Hồ sơ gắn với tài khoản. |
| PUT | `/api/donors/me` | Bearer | Cập nhật họ tên, điện thoại, nhóm máu, ngày sinh, địa chỉ cho donor profile của chính user; email login không đổi; không có donor profile trả 404. |
| GET | `/api/users/me` | Bearer | Hồ sơ tài khoản hiện tại; donor-linked user nhận donor profile, account không liên kết donor nhận hồ sơ user. Email login chỉ đọc. |
| PUT | `/api/users/me` | Bearer | Cập nhật profile của chính user; ghi donor nếu có liên kết, nếu không ghi user account. |
| GET | `/api/coordinators/me` | Coordinator | Đọc hồ sơ điều phối viên; role khác trả 403. |
| PUT | `/api/coordinators/me` | Coordinator | Cập nhật `full_name`, `phone`, `organization`, `job_title`; email không đổi; cập nhật display name trên header. |
| POST | `/api/donors` | Admin/coordinator | Tạo donor; tùy chọn tạo volunteer login. 201; validation 422, conflict 409. |
| POST | `/api/auth/change-password` | Bearer | `{current_password,new_password,confirm_password}`; kiểm tra mật khẩu hiện tại, lưu PBKDF2, thu hồi session khác; sai mật khẩu hiện tại 400, xác nhận lệch 422. |
| GET | `/api/campaigns` | Bearer | Danh sách campaign kèm slots/booked. |
| GET | `/api/campaigns/{cid}` | Bearer | Chi tiết một chiến dịch (thông tin chung, người tạo `created_by`, danh sách slots và danh sách đăng ký appointments). |
| POST | `/api/campaigns` | Admin/coordinator | Tạo campaign và slots; tự động ghi nhận `created_by` theo tài khoản tạo (Quản trị viên / Điều phối viên). 201; slot invalid/overlap 422. |
| PUT | `/api/campaigns/{cid}` | Admin/coordinator | Sửa campaign/slots; not found 404, slot đã đặt conflict 409. |
| PATCH | `/api/campaigns/{cid}/status` | Admin/coordinator | Cập nhật status. |
| DELETE | `/api/campaigns/{cid}` | Admin/coordinator | Xóa nếu chưa có appointment/notification; 204, 404/409. |
| GET | `/api/appointments` | Bearer | Admin/coordinator xem tất cả; volunteer chỉ xem của mình. |
| POST | `/api/appointments` | Bearer | Đặt `{donor_id, slot_id}`; 201, ownership 403, thiếu 404, conflict/capacity 409. |
| PATCH | `/api/appointments/{aid}` | Admin/coordinator | Cập nhật status; 404 nếu không có lượt. |
| GET | `/api/procedures` | Bearer | Danh sách tài liệu hướng dẫn. |
| POST | `/api/chat` | Bearer | `{question}`; truy vấn tài liệu quy trình, trả `{text, mode}`; chặn câu hỏi đánh giá sức khỏe cá nhân. `/api/ai/answer` còn là alias tương thích, không hiển thị trong OpenAPI. |
| POST | `/api/notifications/send?campaign_id={id}` | Admin/coordinator | Ghi system notification cho account có lịch trong chiến dịch; tối đa một lần/người/chiến dịch; **không gửi SMS/email**. |
| GET | `/api/notifications` | Bearer | Inbox riêng, mới nhất trước; tự sinh nhắc cho lịch 24–48 giờ tới. Trả `id,user_id,title,message,type,is_read,created_at`. |
| PUT | `/api/notifications/read-all` | Bearer | Đánh dấu tất cả thông báo của người dùng là đã đọc; trả số lượng cập nhật. |
| PUT | `/api/notifications/{id}/read` | Bearer | Đánh dấu một tin của chính người dùng đã đọc; tin không thuộc inbox trả 404. |
| POST | `/api/ai/campaign-summary` | Admin/coordinator | Body `{campaign_id}`. Trả thống kê chiến dịch và tóm tắt AI/fallback; alias ẩn khỏi OpenAPI: `/api/ai/summarize-campaign`. Chỉ gửi số liệu tổng hợp, không gửi PII. |
| POST | `/api/ai/monthly-report` | Admin/coordinator | Body `{month,year}` (month 1 through 12; year 2000 through 2100). Trả số chiến dịch, lượt đăng ký, tỷ lệ hoàn thành chỉ tiêu, nhận xét và chế độ tạo. AI nhận số liệu chiến dịch và khung giờ tổng hợp, không nhận dữ liệu định danh tình nguyện viên. |
| POST | `/api/ai/yearly-report` | Admin/coordinator | Body `{year}` (2000 through 2100). Trả số chiến dịch, tổng lượt đăng ký, tỷ lệ hoàn thành trung bình theo chiến dịch, thống kê 12 tháng và nhận xét xu hướng AI/fallback. Response dùng `application/json; charset=utf-8`; chỉ gửi số liệu tổng hợp, không gửi PII. |
| POST | `/api/reminders` | Admin/coordinator | Body `{campaign_id,message}`. Records the supplied message for volunteers with registered appointments; message is limited to 2000 characters. Does not send SMS/email. |
| GET | `/api/admin/users` | Admin | Danh sách tài khoản với `id,email,full_name,role,status,phone,blood_group,organization,job_title,created_at`. |
| GET | `/api/admin/users/{user_id}` | Admin | Chi tiết tài khoản người dùng kèm lịch sử hẹn (với tình nguyện viên) hoặc đơn vị/chức vụ (với điều phối/quản trị). |
| POST | `/api/admin/users` | Admin | Tạo tài khoản theo vai trò (`volunteer`, `coordinator`, `admin`) kèm các thông tin tùy chọn `phone`, `blood_group`, `organization`, `job_title`. |
| PUT | `/api/admin/users/{user_id}/role` | Admin | Body `{role}`; role là `volunteer`, `coordinator` hoặc `admin`; 404 nếu không có user, 422 nếu role không hợp lệ. |
| PUT | `/api/admin/users/{user_id}/status` | Admin | Body `{status}`; status là `active` hoặc `locked`; khóa tài khoản thu hồi session hiện có; admin không thể tự khóa. |
| DELETE | `/api/admin/users/{user_id}` | Admin | Xóa tài khoản và thông báo gắn với user; 204 thành công, 400 nếu tự xóa, 404 không tồn tại, 409 nếu xóa admin cuối cùng. Hồ sơ donor và lịch sử appointment được giữ lại. |

## Data notes
Login body: `{"email":"...","password":"..."}`. DB initialization seeds `admin@machdo.com` (role `admin`) and `dieuphoi@machdo.com` (role `coordinator`) using the local demo password `HienMau2026!`; change demo credentials before production. Register body: `email`, `password` (8-100 chars), `full_name`; optional legacy `role` input is ignored and new users always receive `volunteer`. The two system emails cannot register. Profile PUT body gồm `full_name`, `phone`, `blood_group`, `birth_date` (ISO date hoặc bỏ trống), `address`; email không được cập nhật. Coordinator profile body gồm `full_name`, `phone`, `organization`, `job_title`; email không được cập nhật. Change-password body: `current_password`, `new_password`, `confirm_password`; mật khẩu mới tối thiểu 8 ký tự, hash bằng PBKDF2 và thu hồi phiên đăng nhập khác. Notification `type` is `reminder` or `system`; inbox/read APIs chỉ tác động đến user đang đăng nhập. Campaign body gồm `title`, `venue`, `campaign_date`, `description`, `status`, và `slots` `{start_time,end_time,capacity,id?}`. Appointment status: `Đã đăng ký`, `Đã tham gia`, `Vắng mặt`, `Đã hủy`.

Swagger/OpenAPI UI mặc định tại `/docs`; OpenAPI JSON tại `/openapi.json`.

### AI campaign reports

Các endpoint báo cáo yêu cầu bearer token của Admin hoặc Coordinator. Request JSON phải dùng UTF-8; các response thành công đặt `Content-Type: application/json; charset=utf-8`. Nếu AI không khả dụng, API trả thống kê với `mode: "Mẫu dự phòng"`.

`POST /api/ai/monthly-report` nhận `{"month":9,"year":2026}`. Response gồm `summary.campaign_count`, `summary.registrations`, `summary.completion_rate`, `report` và `mode`.

`POST /api/ai/yearly-report` nhận `{"year":2026}`. Response gồm `summary.campaign_count`, `summary.registrations`, `summary.average_completion_rate`, `monthly` (đủ 12 mục với số chiến dịch, lượt đăng ký, sức chứa và tỷ lệ hoàn thành từng tháng), `report` và `mode`. Tỷ lệ trung bình năm là trung bình số học tỷ lệ hoàn thành theo từng chiến dịch; chiến dịch không có sức chứa đóng góp 0%.

### POST /api/admin/users

Requires `Authorization: Bearer <token>` for an admin account. Creates an active account; the password is stored using PBKDF2-HMAC-SHA256. Email is trimmed and lowercased before duplicate checking/storage.

Request body:

```json
{"full_name":"Nguyen Van An","email":"an@example.com","password":"InitialPass123","role":"volunteer","phone":"0987654321","blood_group":"O+","organization":"","job_title":""}
```

`full_name` is 2-100 characters, `email` must have a valid email format and be at most 254 characters, `password` is 8-100 characters, and `role` is `volunteer`, `coordinator`, or `admin`.

Success: HTTP 201 with `{ "id": 42, "email": "an@example.com", "full_name": "Nguyen Van An", "role": "volunteer", "status": "active", "phone": "0987654321", "blood_group": "O+", "created_at": "2026-09-27 12:00:00" }`. Password/hash are never returned.

Errors: 401 when unauthenticated, 403 for a non-admin, 400 when the email already exists, and 422 for invalid fields or role.

