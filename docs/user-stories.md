# User Stories

Stories sau liên kết với các test hồi quy tiêu biểu; bảng không đại diện toàn bộ 17 test functions hoặc toàn bộ requirements.

| ID | User story | Test liên quan |
|---|---|---|
| US-001 | Là tình nguyện viên mới, tôi muốn tạo tài khoản bằng email để đăng nhập và tham gia chiến dịch. | `test_register_account_and_reject_duplicate_email` |
| US-002 | Là người quản lý điểm hiến, tôi muốn chỉ nhận số đăng ký không vượt sức chứa khi có nhiều người đặt đồng thời. | `test_slot_capacity_is_enforced_concurrently` |
| US-003 | Là tình nguyện viên, tôi muốn câu hỏi đánh giá sức khỏe được chuyển tới nhân viên y tế, không gửi cho AI. | `test_ai_fallback_refuses_personal_health_advice` |
| US-004 | Là điều phối viên, tôi muốn nhắc lịch được ghi nhận duy nhất mà không giả vờ đã gửi SMS/email. | `test_reminder_is_recorded_once_without_external_delivery` |
| US-005 | Là người dùng, tôi chỉ muốn truy vấn tài liệu quy trình sau khi đăng nhập. | `test_chat_requires_authentication` |
| US-006 | Là tình nguyện viên, tôi muốn chỉ xem/đặt lịch bằng hồ sơ của mình. | `test_volunteer_only_sees_and_books_their_own_donor_record` |
| US-007 | Là người dùng, tôi muốn đăng xuất làm token cũ không còn truy cập được. | `test_logout_revokes_session_token` |
| US-008 | Là tình nguyện viên, tôi muốn nhận câu trả lời từ tài liệu quy trình đã duyệt khi không cấu hình dịch vụ AI. | `test_procedure_chat_uses_approved_document_fallback` |
| US-009 | Là tình nguyện viên, tôi muốn trợ lý lấy nội dung quy trình phù hợp và không bịa khi tài liệu không phù hợp. | `test_procedure_chat_retrieves_relevant_approved_documents` |
| US-010 | Là quản trị viên, tôi muốn tạo hồ sơ và tài khoản volunteer liên kết để người đó truy cập đúng hồ sơ. | `test_admin_can_create_donor_and_link_volunteer_account` |
| US-011 | Là điều phối viên, tôi muốn tạo/sửa/đóng và xóa chiến dịch an toàn, hỗ trợ khung giờ riêng không chồng lấn. | `test_campaign_custom_slots_edit_status_and_safe_delete` |
| US-012 | Là quản trị viên, tôi muốn bảo vệ khung giờ và chiến dịch đã có lượt hẹn khỏi thay đổi/xóa làm mất lịch. | `test_campaign_with_bookings_cannot_remove_slot_or_be_deleted` |

Các nhu cầu chưa có test chuyên biệt gồm dashboard, toàn bộ nhánh cập nhật trạng thái, validation từng trường, unauthenticated access trên mọi route, migrations từ từng phiên bản DB và tương tác UI gợi ý câu hỏi.
