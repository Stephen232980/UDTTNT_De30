# Yêu cầu khách hàng: Mạch Đỏ

## Bối cảnh
Mạch Đỏ là ứng dụng demo điều phối hoạt động hiến máu tình nguyện. Điều phối viên cần quản lý chiến dịch, sức chứa từng khung giờ và lượt đăng ký; tình nguyện viên cần tự xem chiến dịch, đặt lịch và tra cứu quy trình. Quản trị viên cần theo dõi số liệu và quản lý dữ liệu.

## Mục tiêu
- Tập trung hồ sơ người đăng ký, chiến dịch, khung giờ, lượt hẹn và thông báo trong một ứng dụng.
- Ngăn giữ chỗ vượt sức chứa và lịch trùng của cùng một người.
- Giới hạn dữ liệu tình nguyện viên theo hồ sơ của chính họ.
- Hỗ trợ hỏi đáp quy trình hiến máu bằng nội dung được duyệt, không thay thế nhân viên y tế.
- Cung cấp thống kê và hỗ trợ soạn thông báo; nội dung AI phải được con người kiểm tra trước khi sử dụng.

## Người dùng và phạm vi
- **Quản trị viên:** tổng quan, hồ sơ, chiến dịch, lượt hẹn, nhắc lịch, trợ lý chiến dịch.
- **Điều phối viên:** các chức năng quản lý nghiệp vụ tương tự quản trị viên, ngoại trừ không có phân quyền khác được thể hiện trong code hiện tại.
- **Tình nguyện viên:** xem chiến dịch, hồ sơ của mình, lượt hẹn/thông báo của mình và hỏi quy trình; chỉ được đặt lịch cho hồ sơ liên kết.

Đăng ký công khai hiện tạo tài khoản vai trò `volunteer` cùng hồ sơ `donor`, bất kể trường `role` gửi lên. Đây là hành vi code hiện tại, không phải quyết định nghiệp vụ đã được khách hàng xác nhận.

## Phạm vi bản demo
Có email/password, dashboard, CRUD chiến dịch và khung giờ, đặt lịch, cập nhật trạng thái, thông báo ghi nhận nội bộ, trợ lý quy trình theo từ khóa, sinh nội dung AI tùy cấu hình. Chưa tích hợp gửi SMS/email, không có đánh giá sức khỏe, và không có dịch vụ vector-RAG riêng.

## Ràng buộc và giả định
- Dữ liệu demo không phải hồ sơ y tế dùng trong vận hành thật.
- Nhân viên y tế quyết định điều kiện hiến máu sau sàng lọc trực tiếp.
- SQLite và phiên đăng nhập trong RAM phù hợp chạy demo một tiến trình; triển khai thật cần xem xét lưu trữ phiên bền vững, HTTPS, quản lý secrets, sao lưu, lưu giữ/xóa dữ liệu và kiểm soát truy cập.
- Nội dung quy trình phải được đơn vị chuyên môn duyệt trước khi phát hành.

## Tiêu chí nghiệm thu cấp khách hàng
1. Vai trò và quyền hạn được xác nhận rõ, bao gồm việc tự đăng ký có được tự chọn vai trò hay không.
2. Đăng ký/đăng nhập email và xử lý email trùng hoạt động nhất quán.
3. Không đặt vượt sức chứa, đặt trùng giờ, hoặc thay đổi/xóa khung đã có lượt hẹn trái quy tắc.
4. Tình nguyện viên chỉ truy cập hồ sơ và dữ liệu lịch của mình.
5. Trợ lý không tư vấn y tế cá nhân và cho biết khi không tìm được tài liệu phù hợp.
6. Thông báo nêu rõ chỉ ghi nhận trong demo, không gửi tới người nhận.
7. Các Human Gate trong [human-verification.md](human-verification.md) được người có thẩm quyền xác nhận trước khi phát hành.
