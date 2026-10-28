# Test Plan

## Mục tiêu
Xác nhận luồng tài khoản, phân quyền, đặt chỗ và giới hạn đồng thời, an toàn Hỏi đáp quy trình, notification demo và tính toàn vẹn chiến dịch.

## Phương pháp hiện tại
- Framework: pytest + FastAPI `TestClient` đồng bộ.
- DB: mỗi test chuyển `main.DB_PATH` sang file riêng trong `tmp_path`, sau đó gọi `initialize_database()`.
- Tích hợp AI: provider được monkeypatch hoặc API key bị gỡ; không gọi dịch vụ ngoài.
- Concurrency: hai request đặt cùng slot capacity 1 chạy qua `ThreadPoolExecutor`.
- Async convention cho test mới: `httpx.AsyncClient` + `ASGITransport` sau khi dependency/pytest plugin được xác nhận; suite hiện tại chưa dùng pattern async.

## Test cases hiện hữu

| # | Test function | Mục tiêu |
|---:|---|---|
| 1 | `test_register_account_and_reject_duplicate_email` | Register, duplicate email, login. |
| 2 | `test_register_rejects_reserved_system_emails` | Chặn đăng ký bằng email hệ thống. |
| 3 | `test_seeded_system_accounts_can_login_with_expected_roles` | Seed idempotent, role và PBKDF2. |
| 4 | `test_slot_capacity_is_enforced_concurrently` | Không vượt sức chứa đồng thời. |
| 5 | `test_ai_fallback_refuses_personal_health_advice` | Chặn câu hỏi đánh giá sức khỏe trước provider. |
| 6 | `test_chat_requires_authentication` | Chat yêu cầu session hợp lệ. |
| 7 | `test_reminder_is_recorded_once_without_external_delivery` | Ghi system notification một lần, không gửi ngoài, giảm PII prompt. |
| 8 | `test_notifications_generate_upcoming_reminders_once_and_enforce_user_scope` | Auto reminder 24–48 giờ, idempotency, quyền owner và read APIs. |
| 9 | `test_initialize_migrates_legacy_notification_rows` | Backfill notification legacy. |
| 10 | `test_campaign_schedule_changes_notify_booked_volunteers` | Gửi system notification khi lịch/trạng thái đổi. |
| 11 | `test_volunteer_only_sees_and_books_their_own_donor_record` | Ownership hồ sơ/lượt hẹn. |
| 12 | `test_logout_revokes_session_token` | Thu hồi session token. |
| 13 | `test_procedure_chat_uses_approved_document_fallback` | Fallback tài liệu khi không có API key; kiểm tra alias tương thích. |
| 14 | `test_procedure_chat_retrieves_relevant_approved_documents` | Retrieval phù hợp, không gọi provider khi không có nguồn. |
| 15 | `test_admin_can_create_donor_and_link_volunteer_account` | Tạo donor/account và liên kết profile. |
| 16 | `test_campaign_custom_slots_edit_status_and_safe_delete` | CRUD campaign, custom slots, overlap, status, delete. |
| 17 | `test_campaign_with_bookings_cannot_remove_slot_or_be_deleted` | Bảo vệ lịch đã đặt khi edit/delete. |
| 18 | `test_donor_can_update_own_profile_but_not_login_email` | Cập nhật profile owner-only, không đổi login email. |
| 19 | `test_change_password_validates_and_stores_pbkdf2_hash` | Xác minh current password, confirmation, PBKDF2 và thu hồi session khác. |
| 20 | `test_initialize_migrates_legacy_donor_profile_fields` | Thêm trường profile vào donor DB cũ mà giữ dữ liệu. |
| 21 | `test_system_user_can_update_own_profile_without_donor` | Profile cá nhân cho admin/coordinator không có donor liên kết. |
| 22 | `test_coordinator_can_update_profile_and_change_password` | Coordinator profile fields, RBAC, immutable email và đổi mật khẩu. |

## Thực thi
```powershell
pytest -q
```

Thêm coverage cho các gap đã nêu trong [acceptance-criteria.md](acceptance-criteria.md), đặc biệt là mọi route không xác thực, lỗi provider/timeout, validation biên, appointment status và dữ liệu hỏng. UI avatar/profile/settings đã được kiểm tra thủ công; chưa có automated browser test. Không sử dụng dữ liệu người hiến thật.
