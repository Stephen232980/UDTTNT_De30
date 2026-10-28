# Requirements Issues and Assumptions

| ID | Vấn đề / điểm mơ hồ | Xử lý trong tài liệu | Cần xác nhận |
|---|---|---|---|
| RI-001 | Form gửi role `donor`, model chấp nhận `donor`/`volunteer`, nhưng API register luôn lưu `volunteer`. | Requirement ghi hành vi thực tế: đăng ký công khai tạo volunteer; UI gọi người dùng là tình nguyện viên. | Khách hàng xác nhận có được tự đăng ký donor/volunteer hay không. |
| RI-002 | Yêu cầu kiến trúc nói AI RAG Assistant, code không có service/vector DB/embedding. | Mô tả đúng là retrieval bằng giao nhau token trên tiêu đề bảng `procedures`, gọi LLM tùy chọn; tên RAG chỉ là nhãn khái niệm ở mức đơn giản. | Có cần semantic/vector retrieval hoặc service độc lập không? |
| RI-003 | Nhắc lịch dùng tên `send` nhưng code chỉ ghi `notifications`; không có gateway gửi. | Hướng dẫn và API mô tả là demo ghi nhận nội bộ, không gửi email/SMS. | Kênh gửi, consent, retry và quản lý nhà cung cấp cần được chốt trước tích hợp. |
| RI-004 | Yêu cầu tạo User Stories/AC tương ứng 12 test; test suite không bao phủ mọi tính năng. | Có 12 story/AC gắn một-một với test hiện tại; liệt kê rõ khoảng trống kiểm thử. | Chốt mức coverage cần có cho release. |
| RI-005 | Quy ước mong muốn nêu `httpx.ASGITransport` async nhưng tests hiện tại dùng `fastapi.testclient.TestClient` đồng bộ. | Giữ nguyên test hiện có; skill đề nghị ASGITransport cho test async mới nếu dependency phù hợp. | Có yêu cầu chuyển toàn bộ suite sang async không? |
| RI-006 | Báo cáo nêu 3 Human Gates nhưng không có biên bản/người duyệt trong repo. | Trạng thái từng gate là Chờ phê duyệt; không tự điền tên/chữ ký/ngày. | Người có thẩm quyền cung cấp bằng chứng phê duyệt. |
| RI-007 | Code có `DEMO_PASSWORD` hardcode và tài khoản demo seed. | Phân loại là credential demo, không phải secret production; phải thay/loại bỏ trước môi trường thật. | Quy trình cấp tài khoản ban đầu và quản lý secrets production. |
| RI-008 | User yêu cầu log lỗi AI đã từng gặp, nhưng workspace không có lịch sử issue/log xác minh. | Hai ví dụ trong brief được ghi là sự cố do yêu cầu cung cấp, chưa có timestamp/commit độc lập xác minh. | Bổ sung issue/commit/biên bản nếu cần coi là lịch sử chính thức. |
| RI-009 | 7 bảng là schema hiện tại, nhưng không có CHECK constraint và phần lớn cột FK nullable. | `schema.sql` tái tạo schema hiện tại; đề xuất constraint/index ghi riêng, không tự áp dụng. | Chấp thuận migration và chính sách xử lý dữ liệu cũ. |
| RI-010 | DB thực tế có thể khác DDL DB mới do migration `created_at`. | Tài liệu dùng schema fresh-init; ghi chú legacy có thể có default rỗng khi cột được ALTER. | Xác định baseline DB chính thức trước production migration. |
