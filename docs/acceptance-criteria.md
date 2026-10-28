# Acceptance Criteria

Mỗi tiêu chí dưới đây phản ánh hành vi được kiểm tra bởi test tương ứng; chưa được xem là bao phủ toàn bộ requirement.

| AC | Given | When | Then | Automated test |
|---|---|---|---|---|
| AC-001 | Email chưa tồn tại và payload hợp lệ, kể cả gửi role `donor` | Đăng ký, sau đó đăng ký lại và đăng nhập | Lần đầu 201 với role `volunteer` và donor profile lưu email; lần hai 400 `Email đã tồn tại`; tài khoản đầu đăng nhập được | `test_register_account_and_reject_duplicate_email` |
| AC-013 | Người chưa đăng nhập gửi đăng ký bằng `admin@machdo.com` hoặc `dieuphoi@machdo.com` | Gọi `/api/register` | Cả hai request bị từ chối 400; không tạo/tái sử dụng tài khoản hệ thống | `test_register_rejects_reserved_system_emails` |
| AC-014 | DB mới hoặc đã khởi tạo trước đó | Khởi tạo DB lặp lại rồi đăng nhập bằng hai tài khoản hệ thống với mật khẩu demo | Mỗi email có đúng một account; admin nhận role `admin`, điều phối nhận `coordinator`; password được lưu dạng salt:digest PBKDF2 | `test_seeded_system_accounts_can_login_with_expected_roles` |
| AC-002 | Một slot còn đúng một chỗ và hai donor khác nhau | Hai request đặt slot chạy đồng thời | Có đúng một 201, một 409 và một appointment được ghi | `test_slot_capacity_is_enforced_concurrently` |
| AC-003 | Volunteer đã đăng nhập và API AI được mock để phát hiện gọi | Hỏi điều kiện khi đang uống thuốc | Trả lời chuyển nhân viên y tế; không gọi AI | `test_ai_fallback_refuses_personal_health_advice` |
| AC-004 | Chiến dịch có một lượt đăng ký và AI mock | Gửi nhắc hai lần | Lần đầu ghi một notification, lần sau ghi 0; nêu rõ không gửi SMS/email; prompt không chứa tên/số điện thoại | `test_reminder_is_recorded_once_without_external_delivery` |
| AC-005 | Người dùng chưa đăng nhập | Gọi `POST /api/chat` | Trả 401, không truy xuất tài liệu hoặc gọi AI | `test_chat_requires_authentication` |
| AC-006 | Volunteer có donor liên kết và có donor khác | Xem donors, đặt cho donor khác/rồi cho mình, xem appointments | Danh sách chung 403; donor khác 403; donor mình 201; chỉ thấy lượt của mình | `test_volunteer_only_sees_and_books_their_own_donor_record` |
| AC-007 | Người dùng có token hợp lệ | Logout rồi dùng lại token | Logout 200; request cần quyền sau đó 401 | `test_logout_revokes_session_token` |
| AC-008 | Không có `OPENAI_API_KEY` và tài liệu quy trình đã seed | Hỏi hướng dẫn sau khi hiến | Trả nội dung tài liệu đã duyệt, có chỉ dẫn nghỉ tại điểm hiến | `test_procedure_chat_uses_approved_document_fallback` |
| AC-009 | Có tài liệu procedure, AI mock và câu hỏi phù hợp/không phù hợp | Gửi hai câu hỏi | Prompt có tài liệu liên quan, không đưa tài liệu Điều kiện; câu hỏi không khớp không gọi AI và nói chưa tìm thấy | `test_procedure_chat_retrieves_relevant_approved_documents` |
| AC-010 | Admin đã đăng nhập | Tạo donor kèm tài khoản volunteer rồi đăng nhập tài khoản mới | 201, account_created true, created_at có giá trị, profile mới trỏ đúng donor | `test_admin_can_create_donor_and_link_volunteer_account` |
| AC-011 | Coordinator đã đăng nhập | Tạo custom slots, gửi slot chồng lấn, sửa trạng thái/slot, xóa chiến dịch chưa đặt | Slots hợp lệ được lưu; overlap 422; sửa và đóng thành công; xóa 204 | `test_campaign_custom_slots_edit_status_and_safe_delete` |
| AC-012 | Chiến dịch có slot đã đặt | Thử xóa slot, đổi ngày/giờ, xóa campaign | Hệ thống từ chối thao tác phá vỡ lượt hẹn (422/409) | `test_campaign_with_bookings_cannot_remove_slot_or_be_deleted` |

## Tiêu chí bổ sung cần kiểm thử
- Dùng endpoint khi chưa đăng nhập và thử role không được phép trên toàn bộ route.
- Kiểm tra email không hợp lệ, password length, payload rỗng/biên và duplicate qua race condition.
- Appointment duplicate cùng slot, hủy rồi đặt lại, ngày chiến dịch và capacity biên.
- Kiểm tra XSS trong tên chiến dịch/tên donor và provider timeout/HTTP lỗi.
- Kiểm tra CRUD dashboard, status appointment, lỗi provider/timeout, DB migration và dữ liệu hỏng.
- Bổ sung automated UI test cho suggestion fill, gửi form và hiển thị an toàn kết quả trên desktop/mobile.
