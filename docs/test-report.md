# Test Report

## Kết quả

| Thuộc tính | Giá trị |
|---|---|
| Lệnh | `.venv/Scripts/python.exe -m pytest -q` (Windows/Git Bash), 2026-09-27 |
| Kết quả xác minh revision hiện tại | 22 passed, 0 failed |
| Test framework | pytest + FastAPI `TestClient` đồng bộ |
| Dữ liệu DB | File tạm riêng theo test; DB dự án không bị dùng làm fixture test |
| External AI | Được mock hoặc tắt trong test liên quan |
| Cảnh báo | 1 `StarletteDeprecationWarning`: `httpx` với `starlette.testclient` đã deprecated; warning gợi ý cài `httpx2`. Không làm test thất bại. |

## Phạm vi đạt
Đăng ký/email trùng/login và seed role; donor/system-user/coordinator profile, email read-only và migration; đổi mật khẩu PBKDF2 và thu hồi session khác (gồm coordinator); đặt chỗ đồng thời; chat yêu cầu xác thực, chặn câu hỏi đánh giá sức khỏe, fallback/retrieval tài liệu; notification gửi một lần, auto reminder, phân quyền inbox/read và migration; liên kết tài khoản-donor; quản lý campaign/slot và thông báo khi lịch đổi.

## Khoảng trống
22/22 pass không chứng minh toàn bộ API hay production readiness. Chưa có test riêng cho dashboard, cập nhật status appointment, mọi route 401/403, provider timeout/HTTP error, XSS, hay tải lớn. Chưa có automated UI test cho avatar/settings; giao diện được kiểm tra thủ công trong browser. Test API đang dùng `TestClient` đồng bộ.

## Ghi chú tính tái lập
Lệnh `pytest -q` không có trên PATH của shell; chạy thành công qua interpreter của môi trường dự án bằng lệnh trong bảng. Cảnh báo dependency cần được xử lý theo ma trận tương thích FastAPI/Starlette trước khi nâng phiên bản; không tự cài `httpx2` khi chưa xác minh tương thích. Chạy lại lệnh trên sau các thay đổi tiếp theo.
