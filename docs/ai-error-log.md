# AI Error Log

## Phạm vi tin cậy
Repo hiện không chứa issue tracker export, timestamps, commits, hay log chứng minh lịch sử lỗi AI. Hai sự cố dưới đây được nêu trong yêu cầu dự án; ghi nhận là **user-reported, chưa xác minh độc lập**, không khẳng định đã tái hiện ở phiên bản hiện tại.

| Ref | Lỗi được báo cáo | Cách xử lý / trạng thái hiện tại | Xác minh và phòng ngừa |
|---|---|---|---|
| AI-ERR-001 | Form Đăng nhập và Đăng ký từng render chồng lên nhau. | CSS hiện đặt `.auth-view { display: none !important }` và chỉ `.auth-view.active` hiển thị; JS `showAuthView()` bật đúng một view. Trạng thái hiện tại đã có cơ chế tránh overlap. | Đã đọc source hiện tại; chưa có test UI tự động/lịch sử commit chứng minh thời điểm fix. Thêm UI test chuyển qua lại và kiểm tra chỉ một form hiển thị. |
| AI-ERR-002 | Cảnh báo tương thích httpx/ASGI test từng được nêu trong brief; cảnh báo lịch sử `ASGITransport` cụ thể chưa có log gốc. | Suite hiện dùng `TestClient`, không `ASGITransport`. Lần chạy xác minh ngày 2026-09-27 tạo ra `StarletteDeprecationWarning`: httpx với `starlette.testclient` deprecated và warning gợi ý `httpx2`; 12 tests vẫn pass. | Cảnh báo hiện tại đã tái hiện, nhưng nguyên nhân/lịch sử ASGITransport chưa xác minh. Xác nhận ma trận phiên bản FastAPI/Starlette/client trước khi đổi dependencies; với test async mới, dùng `httpx.AsyncClient` + `ASGITransport` nếu dependency được hỗ trợ. |

## Theo dõi lỗi AI runtime
`ai_call()` có timeout 20 giây và fallback cho thiếu key/một số lỗi upstream. Cần bổ sung kiểm thử HTTP error/JSON không hợp lệ và logging an toàn (không ghi key/PII) trước production. Medical filter dựa trên từ khóa nên không đảm bảo phát hiện mọi cách diễn đạt.

## Quy trình ghi log tiếp theo
Mỗi lỗi cần ID, ngày/môi trường, prompt tối thiểu đã khử PII, expected/actual, nguồn/tài liệu liên quan, mức tác động, cách khắc phục, regression test và người xác minh. Không ghi nội dung sức khỏe nhận dạng được.
