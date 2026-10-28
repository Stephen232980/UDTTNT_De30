# Hướng dẫn sử dụng

## Đăng nhập
Mở trang ứng dụng và đăng nhập bằng email/mật khẩu được cấp. Với môi trường demo mới, tài khoản mẫu dùng mật khẩu `HienMau2026!`; tài khoản hiển thị trong giao diện/README. Chỉ dùng credential này khi chạy local với dữ liệu giả.

## Quản trị viên
- Xem dashboard về hồ sơ, lượt hẹn, chiến dịch và nhóm máu dữ liệu demo.
- Quản lý chiến dịch: tạo/sửa ngày, điểm hiến, trạng thái, khung giờ/sức chứa; không thể xóa campaign/slot đã gắn lịch hẹn hoặc thông báo.
- Mở **Quản lý tài khoản** để xem email, vai trò, ngày tạo và trạng thái; đổi vai trò, khóa/mở khóa hoặc xóa tài khoản sau khi xác nhận.
- Tạo nhắc lịch demo, xem lịch sử; thao tác chỉ ghi nhận trong hệ thống, không gửi SMS/email.
- Dùng Trợ lý AI để hỏi về quy trình hiến máu; câu trả lời chỉ dựa trên nội dung đã được duyệt.

## Điều phối viên
Có các màn hình nghiệp vụ quản lý campaign, donor, appointment và reminder tương tự admin. Sidebar có hai mục AI riêng: **Hỏi đáp AI** dành cho tra cứu quy trình và **Báo cáo thống kê** dành cho tóm tắt chiến dịch/báo cáo tháng năm. Mở avatar ở góc phải để vào hồ sơ điều phối viên: cập nhật họ tên, điện thoại, đơn vị/cơ sở công tác và chức vụ; email đăng nhập chỉ đọc. Code hiện tại không phân biệt thêm quyền giữa admin và coordinator trên các chức năng nghiệp vụ khác.

## Tình nguyện viên
- Đăng ký tài khoản bằng email, họ tên, mật khẩu tối thiểu 8 ký tự; hiện hệ thống tạo vai trò volunteer.
- Xem chiến dịch và chọn khung giờ còn chỗ. Chỉ đặt lịch cho hồ sơ liên kết; không xem danh sách donor chung.
- Xem lượt hẹn/thông báo của mình và hỏi quy trình trong trợ lý.
- Trợ lý không đánh giá sức khỏe cá nhân. Câu hỏi về điều kiện hiến máu cần trao đổi trực tiếp với nhân viên y tế.

## Hồ sơ và cài đặt
Mở avatar ở góc phải thanh trên cùng, chọn **Hồ sơ cá nhân** để cập nhật profile tương ứng với vai trò; email đăng nhập chỉ đọc. Volunteer cập nhật donor profile; admin cập nhật profile user; coordinator cập nhật họ tên, số điện thoại, đơn vị/cơ sở công tác và chức vụ.

Chọn **Cài đặt** để đổi mật khẩu bằng mật khẩu hiện tại và xác nhận mật khẩu mới, hoặc chuyển giao diện Sáng/Tối. Mật khẩu được lưu dạng PBKDF2; các phiên đăng nhập khác sẽ bị thu hồi, phiên đang dùng được giữ lại. Lựa chọn giao diện được lưu cục bộ trên trình duyệt. Cài đặt tài khoản không có lựa chọn ngôn ngữ.

Để đăng xuất, chọn **Đăng xuất** ở menu tài khoản hoặc thanh bên.

## Trợ lý AI

### Hỏi đáp AI
Volunteer thấy mục **Hỏi đáp AI** trong sidebar; admin và điều phối viên cũng có mục này riêng. Chọn câu hỏi gợi ý để điền nhanh hoặc nhập câu hỏi rồi bấm **Gửi câu hỏi**. Câu trả lời dựa trên tài liệu quy trình được duyệt; nếu không có tài liệu phù hợp, trợ lý báo chưa tìm thấy thông tin.

### Báo cáo thống kê (admin và điều phối viên)
Mở mục **Báo cáo thống kê** để xem lượt đăng ký và chỉ tiêu theo từng chiến dịch. Chọn **Tạo tóm tắt AI** trên một chiến dịch để nhận phân tích của AI hoặc nội dung dự phòng. Chọn tháng/năm rồi bấm **Tạo báo cáo AI** để xem thống kê tổng hợp của kỳ đó. Mục báo cáo không hiển thị cho volunteer.

Trợ lý chỉ hướng dẫn quy trình hiến máu, không đánh giá sức khỏe hoặc điều kiện hiến máu cá nhân. Khi cấu hình `OPENAI_API_KEY`, câu hỏi phù hợp có thể được gửi tới provider tương thích; không nhập thông tin cá nhân hoặc thông tin sức khỏe nhạy cảm.

Admin có thêm mục **Quản lý tài khoản** ở sidebar. Trang này liệt kê email, họ tên, vai trò, thời điểm tạo và trạng thái. Admin có thể đổi role giữa `volunteer`, `coordinator`, `admin`; khóa/mở khóa hoặc xóa tài khoản sau khi xác nhận. Không thể tự khóa/xóa tài khoản đang dùng; thao tác khóa thu hồi các phiên đăng nhập hiện có. Xóa tài khoản giữ nguyên hồ sơ donor và lịch sử hiến máu, đồng thời xóa thông báo thuộc tài khoản đó. API quản trị chỉ dành cho admin.
