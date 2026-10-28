# Code Review

## Phạm vi
Đọc `main.py`, `static/app.js`, `static/index.html`, test suite và schema SQLite hiện tại. Đây là rà soát tài liệu/source tĩnh, không phải review diff production hay chứng nhận chất lượng.

## Điểm tốt
- SQL dùng parameter binding cho dữ liệu đầu vào.
- Password hash có random salt và constant-time comparison.
- Server-side role dependencies và kiểm tra ownership volunteer.
- Booking dùng `BEGIN IMMEDIATE` để tuần tự hóa cập nhật sức chứa; có test đồng thời.
- Có fallback khi thiếu/lỗi AI; câu hỏi sức khỏe bị chặn trước provider.
- UI escape phần lớn dữ liệu HTML động và đưa câu trả lời AI vào `textContent`.

## Findings và ưu tiên

| Mức | Finding | Tác động / khuyến nghị |
|---|---|---|
| Cao trước production | `DEMO_PASSWORD` cố định, seed sẵn tài khoản demo; mật khẩu ban đầu công khai trong README/UI. | Chỉ dùng dữ liệu local demo; bắt buộc loại bỏ/đổi credential và luồng bootstrap trước production. |
| Cao trước production | `SESSIONS` chỉ lưu RAM, không có expiry; không chia sẻ giữa worker. | Restart mất session; nhiều worker cho lỗi xác thực không nhất quán. Chọn session store/expiry trước scale. |
| Trung bình | Nhiều cột enum/FK/capacity không có `NOT NULL`/`CHECK` ở DB. | API validate một phần; script/import trực tiếp có thể tạo trạng thái không hợp lệ. Đề xuất migration có kiểm chứng. |
| Trung bình | CORS policy không được cấu hình. | Same-origin hiện tại phù hợp demo; triển khai cross-origin cần allowlist chính xác, không wildcard tùy tiện. |
| Trung bình | `POST /api/register` nhận trường role nhưng luôn gán volunteer. | Contract dễ gây hiểu nhầm; bỏ field hoặc xác định rõ policy và thêm test. |
| Thấp | Suite 12 test tập trung luồng quan trọng nhưng dashboard, summary, appointment status, lỗi upstream và migration chưa kiểm thử. | Bổ sung theo risk trước release. |
| Thấp | Chỉ có unique autoindexes; query list/join có thể tốn kém khi dữ liệu lớn. | Đo `EXPLAIN QUERY PLAN`/workload trước khi thêm index. |

## Kết luận
Phù hợp làm demo học tập/cục bộ với dữ liệu giả. Không khuyến nghị triển khai dữ liệu donor thật hoặc production trước khi xử lý các finding cao và có security/privacy approval.
