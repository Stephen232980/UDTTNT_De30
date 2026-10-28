# Phân tích yêu cầu hệ thống (SRS)

- **Hệ thống:** Hệ thống Quản lý Hiến máu Tình nguyện “Mạch Đỏ”
- **Phiên bản tài liệu:** 1.0 · **Ngày cập nhật:** 2026-09-28
- **Cơ sở phân tích:** `main.py`, `static/app.js`, `static/index.html`, `database/schema.sql`, `test_app.py`.
**Quy ước:** `Implemented` = có triển khai trong source; `Partial` = mới đáp ứng một phần; `Proposed` = mục tiêu/đề xuất chưa được xác nhận hoặc chứng minh. Test được nêu riêng; trạng thái triển khai không đồng nghĩa đã có test.

## 1. Tổng quan dự án (Project Overview)

### 1.1 Mục tiêu và phạm vi

Mạch Đỏ kết nối Tình nguyện viên hiến máu, Điều phối viên chiến dịch và Quản trị viên hệ thống. Hệ thống cung cấp quản lý chiến dịch, khung giờ và lượt hẹn; hồ sơ và tài khoản; thông báo trong ứng dụng; trợ lý AI hỏi đáp dựa trên tài liệu quy trình được duyệt và hỗ trợ tóm tắt thống kê chiến dịch.

AI là tiện ích hỗ trợ thông tin quy trình và diễn giải thống kê. Trợ lý không đánh giá tình trạng sức khỏe hoặc quyết định người dùng có đủ điều kiện hiến máu; đánh giá đó thuộc nhân viên y tế tại điểm hiến. Retrieval hiện tại tìm tài liệu theo từ khóa tiêu đề trong SQLite, không phải vector search. Khi không có cấu hình AI hoặc upstream lỗi, code có nhánh fallback.

### 1.2 Ràng buộc kiến trúc và công nghệ

| Lớp | Ràng buộc / triển khai |
|---|---|
| Backend | Python, FastAPI; API và xác thực trong `main.py`. |
| Lưu trữ | SQLite; schema mới trong `database/schema.sql`, ứng dụng có migration khi khởi tạo. Bật foreign keys và WAL theo connection. |
| Frontend | SPA tĩnh dùng HTML5, CSS3, Vanilla JavaScript (`static/index.html`, `static/app.js`, `static/styles.css`); không cần Node.js/npm. |
| Mật khẩu | PBKDF2-HMAC-SHA256 qua `hashlib`, salt ngẫu nhiên 16 byte, 180.000 vòng; so sánh digest constant-time. |
| Kiểm thử | pytest; suite HTTP đồng bộ với FastAPI TestClient và SQLite cô lập trong các test hiện có. |
| AI | Provider tùy chọn qua cấu hình môi trường; tài liệu quy trình SQLite làm nguồn fallback/grounding. Không gửi SMS/email theo triển khai hiện tại. |

### 1.3 Tác nhân và thuật ngữ

- **Tình nguyện viên:** tài khoản `volunteer`, liên kết với hồ sơ donor để xem và đặt lượt hẹn của chính mình.
- **Điều phối viên:** tài khoản `coordinator`, quản lý chiến dịch, người đăng ký, lượt hẹn và nhắc lịch.
- **Quản trị viên:** tài khoản `admin`, có quyền quản lý toàn hệ thống và tài khoản.
- **Lượt hẹn:** bản ghi appointment nối donor với slot của chiến dịch.
- **Thông báo:** bản ghi inbox nội bộ, gồm `reminder` hoặc `system`; không đồng nghĩa SMS/email đã gửi.

## 2. Ma trận phân quyền và nguyên tắc truy cập (RBAC Matrix)

Tài khoản seed hệ thống dùng email `admin@gmail.com` (admin) và `dieuphoi@gmail.com` (coordinator). Đây là địa chỉ tài khoản khởi tạo trong code, không phải cơ chế đảm bảo email đó luôn thuộc về cá nhân cụ thể. Admin có thể cấp lại vai trò. Đăng ký tự phục vụ tạo vai trò `volunteer`; model chấp nhận trường role legacy nhưng API không cho người đăng ký tự cấp quyền.

| Khả năng | `volunteer` | `coordinator` | `admin` |
|---|:---:|:---:|:---:|
| Xem chiến dịch, khung giờ; xem và đặt lượt hẹn thuộc hồ sơ liên kết | ✓ | ✓ | ✓ |
| Xem/cập nhật hồ sơ của mình, đổi mật khẩu, cài đặt cục bộ | ✓ | ✓ | ✓ |
| Hỏi đáp quy trình hiến máu; xem thông báo riêng | ✓ | ✓ | ✓ |
| Dashboard quản lý, xem hồ sơ donor và toàn bộ lượt hẹn | — | ✓ | ✓ (API có quyền; mục Người đăng ký/Lượt hẹn bị ẩn khỏi sidebar admin) |
| Tạo/sửa/xóa chiến dịch, đổi trạng thái và trạng thái lượt hẹn | — | ✓ | ✓ |
| Gửi nhắc lịch nội bộ có nội dung tùy chỉnh; báo cáo tháng/năm | — | ✓ | ✓ |
| Xem/tạo tài khoản; đổi role; khóa/mở khóa; xóa tài khoản | — | — | ✓ |

Mọi quyền phải được kiểm tra ở backend. Ẩn mục giao diện không thay thế kiểm tra quyền phía server. Tài khoản bị khóa không thể đăng nhập và phiên đang hoạt động bị thu hồi. Code bảo vệ tài khoản admin đang thao tác khỏi tự khóa/tự xóa; không khẳng định có bảo vệ riêng cho một “admin chính” cố định.

## 3. Yêu cầu chức năng (Functional Requirements)

### 3.1 Xác thực, hồ sơ và cài đặt

| ID | Yêu cầu có thể kiểm chứng | Trạng thái / kiểm chứng |
|---|---|---|
| FR-AUTH-01 | Người đăng ký nhập email, mật khẩu và họ tên; email hợp lệ và không trùng/không thuộc địa chỉ hệ thống. Server chuẩn hóa email và tạo tài khoản `volunteer` cùng hồ sơ donor liên kết. Form đăng nhập dùng placeholder hướng dẫn, không hiển thị hoặc điền sẵn tài khoản demo. | Implemented. `POST /api/register`, `/api/auth/login`; `test_register_account_and_reject_duplicate_email`, `test_register_rejects_reserved_system_emails`, `test_seeded_system_accounts_can_login_with_expected_roles`. UI chưa có test tự động riêng. |
| FR-AUTH-02 | Người dùng đăng nhập nhận bearer token; sai thông tin trả lỗi xác thực. Đăng xuất thu hồi phiên. | Implemented. `POST /api/auth/login` (alias `/api/login`), `POST /api/auth/logout`; `test_logout_revokes_session_token`. |
| FR-AUTH-03 | Người dùng gửi mật khẩu hiện tại, mật khẩu mới và xác nhận; server từ chối mật khẩu hiện tại sai hoặc xác nhận không khớp, lưu mật khẩu mới dạng PBKDF2. Phiên hiện tại tiếp tục dùng được, phiên khác bị thu hồi theo code. | Implemented; `POST /api/auth/change-password`; `test_change_password_validates_and_stores_pbkdf2_hash`. |
| FR-PROF-01 | Người dùng mở menu avatar để xem/chỉnh hồ sơ phù hợp role. Volunteer cập nhật thông tin donor; coordinator chỉnh họ tên, điện thoại, đơn vị và chức vụ. Email đăng nhập chỉ đọc; server chỉ cho sửa hồ sơ của chính người dùng. | Implemented; `/api/donors/me`, `/api/users/me`, `/api/coordinators/me`; `test_donor_can_update_own_profile_but_not_login_email`, `test_system_user_can_update_own_profile_without_donor`, `test_coordinator_can_update_profile_and_change_password`. |
| FR-SETT-01 | Volunteer, coordinator và admin mở Cài đặt tài khoản để đổi mật khẩu hoặc chuyển giao diện Sáng/Tối. Giao diện được lưu trên trình duyệt qua `localStorage`; modal không có tùy chọn ngôn ngữ hay nút đăng xuất. | Implemented trong `settingsForm()`; đổi mật khẩu qua `POST /api/auth/change-password`, theme lưu bằng `md-theme`; chưa có test trình duyệt riêng. |

### 3.2 Không gian Tình nguyện viên

| ID | Yêu cầu có thể kiểm chứng | Trạng thái / kiểm chứng |
|---|---|---|
| FR-VOL-01 | Volunteer xem chiến dịch và khung giờ, chọn slot còn sức chứa để đặt; chỉ được đặt cho donor liên kết; server từ chối slot hết chỗ, lịch trùng hoặc đặt trùng. | Implemented; `GET/POST /api/campaigns`, `GET/POST /api/appointments`; `test_slot_capacity_is_enforced_concurrently`, `test_volunteer_only_sees_and_books_their_own_donor_record`. |
| FR-VOL-02 | Người dùng đã đăng nhập chọn mục **Hỏi đáp AI** và hỏi về quy trình hiến máu qua workspace hỏi đáp tập trung với câu hỏi gợi ý, khung nhập và vùng trả lời rộng; nội dung dựa trên tài liệu được duyệt, có fallback và không đưa ra chẩn đoán/đánh giá sức khỏe cá nhân. Volunteer chỉ có view hỏi đáp. | Implemented; view `#ai-qa-section`; `POST /api/chat` (alias tương thích `/api/ai/answer`), `GET /api/procedures`; các test hỏi đáp hiện có. |

### 3.3 Không gian Điều phối viên

| ID | Yêu cầu có thể kiểm chứng | Trạng thái / kiểm chứng |
|---|---|---|
| FR-COORD-01 | Điều phối viên xem, tạo, sửa và đổi trạng thái chiến dịch; quản lý slot và lượt hẹn, không xóa slot/chiến dịch đã có dữ liệu ràng buộc. | Implemented; `/api/campaigns`, `/api/appointments`; `test_campaign_custom_slots_edit_status_and_safe_delete`, `test_campaign_with_bookings_cannot_remove_slot_or_be_deleted`. |
| FR-COORD-02 | Admin và điều phối viên có hai mục sidebar độc lập: **Hỏi đáp AI** chỉ hiện view `#ai-qa-section`; **Báo cáo thống kê** chỉ hiện view `#ai-reports-section`. View báo cáo hiển thị tóm tắt lượt đăng ký/chỉ tiêu từng chiến dịch và cho chọn tháng/năm để nhận thống kê tổng hợp cùng nhận xét AI/fallback. | Implemented; `POST /api/ai/campaign-summary`, `POST /api/ai/monthly-report`; test API `test_ai_campaign_summary_reports_counts_and_requires_manager_role`, `test_ai_monthly_report_returns_campaign_statistics`; tách view được kiểm tra bởi `test_ai_views_have_separate_routes_and_containers`. |
| FR-COORD-04 | Admin/Coordinator chọn năm để xem tổng số chiến dịch, lượt đăng ký, tỷ lệ hoàn thành trung bình theo chiến dịch, đủ 12 dòng thống kê tháng và nhận xét xu hướng AI/fallback. | Implemented; `POST /api/ai/yearly-report`; `test_ai_yearly_report_returns_annual_and_monthly_statistics_as_utf8`. |
| FR-COORD-03 | Điều phối viên chọn chiến dịch và nội dung nhắc tùy chỉnh; hệ thống ghi thông báo cho volunteer có lượt hẹn chiến dịch đó và báo số bản ghi tạo thành công. | Implemented dưới dạng inbox nội bộ; `POST /api/reminders`; `test_custom_reminder_message_is_recorded_for_campaign_volunteers`, `test_reminder_is_recorded_once_without_external_delivery`. Không có gửi SMS/email. |

### 3.4 Không gian Quản trị viên

| ID | Yêu cầu có thể kiểm chứng | Trạng thái / kiểm chứng |
|---|---|---|
| FR-ADM-01 | Sidebar admin chỉ hiện Tổng quan, Chiến dịch, Quản lý tài khoản, Hỏi đáp AI, Báo cáo thống kê, Nhắc lịch; mục Người đăng ký và Lượt hẹn không xuất hiện trong menu admin. Coordinator cũng thấy hai mục AI độc lập. | Implemented trong `navigation()` của `static/app.js`; mục Báo cáo thống kê không được render cho volunteer. Tách view được kiểm tra bởi `test_ai_views_have_separate_routes_and_containers`. |
| FR-ADM-02 | Admin xem tài khoản kèm `created_at`; tạo tài khoản role `volunteer`/`coordinator`/`admin`; đổi role; khóa/mở khóa; xóa tài khoản. Email trùng/không hợp lệ bị từ chối, mật khẩu được hash; admin không thể tự khóa hoặc tự xóa. | Implemented; `/api/admin/users` GET/POST/PUT/DELETE; `test_admin_can_list_update_lock_unlock_and_delete_accounts`, `test_admin_user_management_endpoints_reject_non_admin_roles`, `test_admin_can_create_all_account_roles_with_hashed_password`, `test_admin_create_user_rejects_non_admin_and_unauthenticated`. |

### 3.5 Thông báo và tự động hóa

| ID | Yêu cầu có thể kiểm chứng | Trạng thái / kiểm chứng |
|---|---|---|
| FR-NOTIF-01 | Người dùng mở chuông trên top bar để xem thông báo của mình, đánh dấu một hoặc tất cả là đã đọc. Backend không trả thông báo của người dùng khác. | Implemented; `GET /api/notifications`, `PUT /api/notifications/{notification_id}/read`, `PUT /api/notifications/read-all`; `test_notifications_generate_upcoming_reminders_once_and_enforce_user_scope`. |
| FR-NOTIF-02 | Khi đặt lịch thành công, server tạo thông báo xác nhận `system` cho tài khoản volunteer liên kết (và thông báo vận hành cho coordinator). Inbox cũng tạo nhắc lịch `reminder` cho lịch trong 24–48 giờ và không tạo trùng cho cùng user/appointment. | Implemented; `POST /api/appointments` tạo confirmation `system`; `GET /api/notifications` sinh nhắc `reminder`; unique partial index chống trùng reminder. Kiểm chứng: `test_notifications_generate_upcoming_reminders_once_and_enforce_user_scope`; `test_reminder_is_recorded_once_without_external_delivery` lọc riêng `type == "reminder"`. Không tuyên bố có AI tham gia xác nhận tự động. |
| FR-NOTIF-03 | Thay đổi lịch/địa điểm/trạng thái chiến dịch liên quan tới người đã đặt được ghi nhận dưới dạng thông báo hệ thống; nhắc lịch gửi không tạo bản ghi trùng. | Implemented; `test_campaign_schedule_changes_notify_booked_volunteers`, `test_reminder_is_recorded_once_without_external_delivery`. Kênh gửi là ứng dụng. |

### 3.6 Các chức năng quản lý liên quan

| ID | Yêu cầu có thể kiểm chứng | Trạng thái / kiểm chứng |
|---|---|---|
| FR-MGMT-01 | Coordinator/admin xem dashboard, hồ sơ donor và danh sách lượt hẹn; volunteer chỉ đọc hồ sơ/lượt hẹn của mình. Trạng thái lượt hẹn có thể được quản lý theo các trạng thái hệ thống hỗ trợ. | Implemented; `GET /api/dashboard`, `/api/donors`, `/api/appointments`, `PATCH /api/appointments/{aid}`; test phân quyền volunteer trong `test_volunteer_only_sees_and_books_their_own_donor_record`. Chưa có test riêng cho từng chuyển trạng thái. |
| FR-MGMT-02 | Admin/coordinator có thể tạo hồ sơ donor; tùy chọn tạo tài khoản volunteer liên kết. | Implemented; `POST /api/donors`; `test_admin_can_create_donor_and_link_volunteer_account`. |

## 4. Yêu cầu phi chức năng (Non-Functional Requirements)

| ID | Yêu cầu / mục tiêu | Trạng thái / tiêu chí xác minh |
|---|---|---|
| NFR-SEC-01 | Không lưu mật khẩu dạng rõ; dùng PBKDF2-HMAC-SHA256 với salt ngẫu nhiên, constant-time comparison. Endpoint admin/coordinator kiểm tra quyền ở server. | Implemented; xem FR-AUTH-03/FR-ADM-02 và các test quyền/hash nêu trên. Cấu hình demo hardcode trong code phải được thay thế/loại bỏ trước production. |
| NFR-SEC-02 | Truy vấn SQL dùng binding tham số; foreign key được bật; phạm vi dữ liệu donor được giới hạn theo role. | Implemented theo source/schema; test quyền và sức chứa có nhưng không bao phủ mọi route. |
| NFR-PRIV-01 | Không đưa tên/số điện thoại donor vào prompt nhắc lịch; câu hỏi sức khỏe cá nhân không được chuyển tới AI. | Đã có kiểm chứng ở `test_reminder_is_recorded_once_without_external_delivery`, `test_ai_fallback_refuses_personal_health_advice`; cần rà soát logging/retention trước production. |
| NFR-PERF-01 | Mục tiêu phản hồi API dưới 200 ms và tải SPA mượt trên môi trường mục tiêu. | Proposed/Chưa đo. Không có benchmark, cấu hình tải hoặc ngưỡng percentile trong source/test; cần xác định môi trường và đo trước khi nghiệm thu. |
| NFR-TEST-01 | Mục tiêu phát hành: toàn bộ pytest cases pass; kiểm tra notification xác nhận lọc chính xác `type == "reminder"` và không bị bản ghi tự động `system` làm sai assertion. | Đã xác minh bằng `\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.codex-pytest-final-run`: 31 passed, 1 deprecation warning. Fixture reminder đặt slot ở +36 giờ để kiểm thử đúng cửa sổ tự sinh 24–48 giờ. |
| NFR-ARCH-01 | Chạy backend FastAPI + SQLite và frontend SPA không cần Node.js/npm; việc khởi tạo/migration phù hợp database đã tồn tại. | Implemented. Migration legacy có test; SQLite/WAL và session lưu RAM giới hạn khả năng scale/HA. |
| NFR-INT-01 | Source Python, HTML và JavaScript được lưu/đọc UTF-8; response các API AI dùng `application/json; charset=utf-8`, nhãn chế độ dự phòng hiển thị đúng dấu tiếng Việt. | Implemented; kiểm tra header ở `test_ai_campaign_summary_reports_counts_and_requires_manager_role`, `test_ai_monthly_report_returns_campaign_statistics`, `test_ai_yearly_report_returns_annual_and_monthly_statistics_as_utf8`, cùng kiểm tra chuỗi fallback campaign summary. |

## 5. Ma trận truy vết yêu cầu (Requirements Traceability Matrix — RTM)

Các test case dưới đây là tên hàm trong `test_app.py`. “—” có nghĩa chưa có test chuyên biệt, không có nghĩa tính năng chưa triển khai. UI hiện chủ yếu được xác minh qua source; suite không có browser automation.

| Requirement | API backend (`main.py`) | Test case tương ứng |
|---|---|---|
| FR-AUTH-01 | `POST /api/register`; `POST /api/auth/login` | `test_register_account_and_reject_duplicate_email`; `test_register_rejects_reserved_system_emails`; `test_seeded_system_accounts_can_login_with_expected_roles` |
| FR-AUTH-02 | `POST /api/auth/login`; `POST /api/auth/logout` | `test_logout_revokes_session_token`; `test_seeded_system_accounts_can_login_with_expected_roles` |
| FR-AUTH-03 | `POST /api/auth/change-password` | `test_change_password_validates_and_stores_pbkdf2_hash`; `test_coordinator_can_update_profile_and_change_password` |
| FR-PROF-01 | `GET/PUT /api/donors/me`; `GET/PUT /api/users/me`; `GET/PUT /api/coordinators/me` | `test_donor_can_update_own_profile_but_not_login_email`; `test_system_user_can_update_own_profile_without_donor`; `test_coordinator_can_update_profile_and_change_password` |
| FR-SETT-01 | UI `static/app.js`; không cần API | Chưa có UI test |
| FR-VOL-01 | `GET/POST /api/campaigns`; `GET/POST /api/appointments` | `test_slot_capacity_is_enforced_concurrently`; `test_volunteer_only_sees_and_books_their_own_donor_record` |
| FR-VOL-02 | `POST /api/chat` (`/api/ai/answer` alias); `GET /api/procedures` | `test_ai_fallback_refuses_personal_health_advice`; `test_chat_requires_authentication`; `test_procedure_chat_uses_approved_document_fallback`; `test_procedure_chat_retrieves_relevant_approved_documents` |
| FR-COORD-01 | `GET/POST/PUT/PATCH/DELETE /api/campaigns`; `GET/PATCH /api/appointments` | `test_campaign_custom_slots_edit_status_and_safe_delete`; `test_campaign_with_bookings_cannot_remove_slot_or_be_deleted` |
| FR-COORD-02 | UI routes `ai` / `ai-reports`; `POST /api/ai/campaign-summary` (`/api/ai/summarize-campaign` alias); `POST /api/ai/monthly-report` | `test_ai_campaign_summary_reports_counts_and_requires_manager_role`; `test_ai_monthly_report_returns_campaign_statistics`; `test_ai_views_have_separate_routes_and_containers` |
| FR-COORD-04 | `POST /api/ai/yearly-report` | `test_ai_yearly_report_returns_annual_and_monthly_statistics_as_utf8` |
| FR-COORD-03 | `POST /api/reminders` | `test_custom_reminder_message_is_recorded_for_campaign_volunteers`; `test_reminder_is_recorded_once_without_external_delivery` |
| FR-ADM-01 | UI `navigation()` trong `static/app.js`; API không áp dụng | `test_ai_views_have_separate_routes_and_containers` |
| FR-ADM-02 | `GET/POST /api/admin/users`; `PUT /api/admin/users/{user_id}/role`; `PUT /api/admin/users/{user_id}/status`; `DELETE /api/admin/users/{user_id}` | `test_admin_can_list_update_lock_unlock_and_delete_accounts`; `test_admin_user_management_endpoints_reject_non_admin_roles`; `test_admin_can_create_all_account_roles_with_hashed_password`; `test_admin_create_user_rejects_non_admin_and_unauthenticated` |
| FR-NOTIF-01 | `GET /api/notifications`; `PUT /api/notifications/{notification_id}/read`; `PUT /api/notifications/read-all` | `test_notifications_generate_upcoming_reminders_once_and_enforce_user_scope` |
| FR-NOTIF-02 | `POST /api/appointments`; `GET /api/notifications` | `test_notifications_generate_upcoming_reminders_once_and_enforce_user_scope`; `test_reminder_is_recorded_once_without_external_delivery` |
| FR-NOTIF-03 | `POST /api/reminders`; campaign `PUT/PATCH` | `test_campaign_schedule_changes_notify_booked_volunteers`; `test_reminder_is_recorded_once_without_external_delivery` |
| FR-MGMT-01 | `GET /api/dashboard`; `GET /api/donors`; `GET/POST /api/appointments`; `PATCH /api/appointments/{aid}` | `test_volunteer_only_sees_and_books_their_own_donor_record` |
| FR-MGMT-02 | `POST /api/donors` | `test_admin_can_create_donor_and_link_volunteer_account` |

### 5.1 Khoảng trống truy vết

- Chưa có kiểm thử trình duyệt cho placeholder/form đăng nhập, avatar menu, sidebar admin, cài đặt theme, chuông thông báo hoặc luồng đặt lịch UI.
- Chưa có kiểm thử riêng cho từng trạng thái appointment và toàn bộ ma trận role × endpoint.
- NFR-PERF-01 chưa có benchmark; pytest suite được ghi nhận theo lần chạy cuối ở NFR-TEST-01.
- AI provider, chất lượng phản hồi và fallback upstream không thể được nghiệm thu chỉ bằng mock test; cần kiểm thử tích hợp có kiểm soát trước khi phát hành.

## 6. Giả định, giới hạn và vấn đề cần xác nhận

| Mã | Nội dung |
|---|---|
| RI-001 | API đăng ký luôn tạo `volunteer`, dù model còn chấp nhận role legacy `donor`; chưa có quyết định sản phẩm về role tự đăng ký. |
| RI-002 | Retrieval AI hiện là keyword matching theo tiêu đề procedure; semantic/vector search chưa được triển khai. |
| RI-003 | Nhắc lịch chỉ tạo bản ghi inbox; kênh SMS/email, consent, retry và nhà cung cấp chưa nằm trong phạm vi code. |
| RI-004 | `admin@gmail.com` và `dieuphoi@gmail.com` là account seed; email cố định không chứng minh danh tính ngoài hệ thống. Quy trình cấp quyền production cần được quyết định. |
| RI-005 | `DEMO_PASSWORD` và tài khoản demo chỉ phục vụ môi trường demo/local; cần quy trình secret và bootstrap an toàn cho production. |
| RI-006 | Các yêu cầu về thời gian phản hồi <200 ms và 100% pytest pass là mục tiêu cần kiểm chứng; tài liệu không ghi nhận chúng đã đạt ở revision hiện tại. |

Các vấn đề lịch sử/kiến trúc khác được theo dõi trong [requirements-issues.md](requirements-issues.md). Chưa có bằng chứng phê duyệt stakeholder trong source tài liệu.

## 7. Nguồn và kiểm soát thay đổi

- Backend/API và logic bảo mật: `main.py`.
- Giao diện, phân trang theo role, cài đặt và tương tác: `static/app.js`, `static/index.html`, `static/styles.css`.
- DDL SQLite fresh initialization: `database/schema.sql`; runtime migration nằm trong `main.py`.
- Bằng chứng test tự động: `test_app.py`; tài liệu này không thay thế báo cáo chạy test.
- Mọi thay đổi API, schema, role hoặc luồng AI cần cập nhật yêu cầu liên quan và RTM trong cùng thay đổi.
