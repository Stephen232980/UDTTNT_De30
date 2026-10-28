# Mạch Đỏ

Hệ thống demo điều phối hiến máu tình nguyện: hồ sơ người đăng ký, chiến dịch và điểm hiến, khung giờ có giới hạn chỗ, trạng thái tham gia, nhắc lịch, thống kê và trợ lý nội dung AI.

## Phạm vi chức năng

- Phân quyền quản trị viên, điều phối viên và tình nguyện viên; tình nguyện viên chỉ xem hồ sơ, lượt hẹn và nhắc lịch gắn với tài khoản demo của mình.
- Quản lý hồ sơ, tạo/đóng chiến dịch, giữ chỗ, chống đăng ký trùng giờ và cập nhật trạng thái tham gia.
- Thống kê tổng lượt, tỷ lệ tham gia và nhóm máu mẫu; trợ lý tạo lời mời, hỏi đáp tài liệu quy trình, tóm tắt và nhắc lịch.
- SQLite lưu người dùng, người đăng ký, chiến dịch, khung giờ, lượt hẹn, thông báo và tài liệu quy trình. Khung giờ được giữ bằng giao dịch SQLite để giới hạn sức chứa khi có đăng ký đồng thời.

## Chạy tại máy

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Mở `http://127.0.0.1:8000`. Hệ thống tự tạo SQLite tại `data/blood_donation.db` và nạp dữ liệu demo khi chạy lần đầu.

Tài khoản demo (mật khẩu chung `HienMau2026!`):

| Vai trò | Email đăng nhập | Tên đăng nhập rút gọn |
| --- | --- | --- |
| Quản trị viên | `admin@machdo.com` | `admin` |
| Điều phối viên | `dieuphoi@machdo.com` | `dieuphoi` |
| Tình nguyện viên | `tinhnguyen@machdo.com` | `tinhnguyen` |

*Hệ thống hỗ trợ đăng nhập linh hoạt bằng cả Email đầy đủ hoặc Tên đăng nhập rút gọn.*

## Tích hợp AI

Không cần API key để chạy các luồng demo. Mặc định ứng dụng dùng tài liệu quy trình đã nạp và mẫu dự phòng cho lời mời, nhắc lịch, tóm tắt. Để bật sinh nội dung qua API tương thích OpenAI, đặt `OPENAI_API_KEY`; có thể tùy chỉnh `OPENAI_MODEL` và `OPENAI_BASE_URL`.

Trợ lý chỉ nhận tài liệu quy trình được duyệt. Câu hỏi có dấu hiệu liên quan sức khỏe cá nhân sẽ bị chặn trước khi gửi tới nhà cung cấp AI. Tóm tắt chỉ gửi số liệu tổng hợp; lời mời và nhắc lịch chỉ gửi thông tin chiến dịch. Không nhập thông tin sức khỏe hoặc giấy tờ cá nhân vào ứng dụng. AI không tư vấn y khoa; điều kiện hiến máu do nhân viên y tế đánh giá trực tiếp.

## AI trong SDLC

- KT1: dùng AI phác thảo use case, vai trò, bảng dữ liệu và luồng đăng ký; đối chiếu lại quy tắc sức chứa, dữ liệu cá nhân và quy trình được đơn vị duyệt.
- KT2: dùng AI hỗ trợ CRUD/API, giao diện và phân tích lỗi; kiểm thử giới hạn khung giờ với các yêu cầu đồng thời.
- KT3: giới hạn chatbot bằng tài liệu được duyệt; kiểm thử câu hỏi sức khỏe, phân quyền và dữ liệu gửi tới AI trước khi chấp nhận nội dung.
- Cuối kỳ: dùng AI hỗ trợ README, báo cáo, slide và rà soát quyền riêng tư; con người kiểm chứng số liệu, nguồn hướng dẫn và nội dung trước khi công bố.

## Phạm vi demo và quyền riêng tư

- Tin nhắc chỉ được ghi nhận trong ứng dụng; chưa kết nối SMS hoặc email.
- Nhóm máu và hồ sơ trong dữ liệu mẫu chỉ phục vụ trình diễn, không phải hồ sơ y tế.
- Tài khoản mẫu và phiên đăng nhập trong bộ nhớ chỉ phù hợp chạy thử trên máy cá nhân. Trước khi triển khai thật cần thay xác thực, quản lý bí mật, lưu trữ phiên, HTTPS, chính sách lưu/xóa dữ liệu và kiểm soát truy cập phù hợp.
- Không dùng dữ liệu sức khỏe cá nhân thật trong bản demo.

## Kiểm thử

```powershell
pytest -q
```