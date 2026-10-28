---
name: user-guide
description: "Hướng dẫn xây dựng tài liệu Hướng dẫn sử dụng (User Guide) chuẩn mẫu 07_GenAI_SoftwareDevelopment_user-guide cho hệ thống Mạch Đỏ, bao gồm cấu hình phần cứng/phần mềm (Web Responsive SPA), hướng dẫn thao tác chi tiết theo 3 vai trò (Tình nguyện viên, Điều phối viên, Quản trị viên) và tương tác với AI Engine (Chatbot RAG và Dịch vụ Thông báo tự động)."
---

# Kỹ năng Xây dựng Tài liệu Hướng dẫn Sử dụng (User Guide Specification)

Skill này cung cấp cấu trúc, quy chuẩn kỹ thuật và hướng dẫn chi tiết để biên soạn tài liệu **Hướng dẫn sử dụng (User Guide)** chuẩn theo mẫu báo cáo **`07_GenAI_SoftwareDevelopment_user-guide`**, phục vụ hệ thống **"Mạch Đỏ - Quản lý hiến máu tình nguyện tích hợp AI"**.

---

## 1. Mục tiêu & Phạm vi áp dụng

- **Mục tiêu:**
  1. Cung cấp tài liệu hướng dẫn vận hành trực quan, dễ hiểu, theo định hướng tác vụ (Task-oriented) cho toàn bộ người dùng cuối (End-users) và quản trị viên của hệ thống Mạch Đỏ.
  2. Xác định rõ ràng các yêu cầu về môi trường phần cứng, phần mềm, thiết bị đầu cuối và kết nối mạng để hệ thống vận hành tối ưu.
  3. Bao quát đầy đủ **07 Use Case** chuẩn (`UC001` – `UC007`) phân định theo **03 vai trò người dùng chính**:
     - **Tình nguyện viên (TNV / Donors):** Đăng ký tài khoản, đăng nhập, tìm kiếm chiến dịch, đăng ký khung giờ hiến máu, khai báo sàng lọc y tế, quản lý lịch hẹn, nhận thông báo nhắc lịch tự động và hỏi đáp AI.
     - **Điều phối viên (Coordinators / Staff):** Quản lý thông tin chiến dịch, cấu hình điểm hiến máu, thiết lập các khung giờ ca hiến kèm sức chứa tối đa (slot capacity), theo dõi báo cáo thống kê và tra cứu quy trình y tế qua AI.
     - **Quản trị viên (Admins):** Quản lý tài khoản và phân quyền người dùng, phê duyệt chiến dịch hiến máu, xem báo cáo tổng thể toàn hệ thống, quản lý và phê duyệt kho tri thức quy trình chuẩn (`QUY_TRINH_HIEN_MAU`) làm nguồn Grounding cho AI Chatbot.
     - **Tác nhân AI (AI Engine):** Đóng vai trò trợ lý thông minh hỗ trợ hỏi đáp quy trình chuẩn (UC006) và tự động sinh thông báo nhắc lịch cá nhân hóa (UC007).
- **Phạm vi kiến trúc kỹ thuật:**
  - Nền tảng **Web Single Page Application (SPA)** phát triển trên FastAPI backend và Vanilla HTML5/CSS3/JavaScript.
  - Tương thích Responsive hoàn toàn trên cả máy tính (Desktop) và trình duyệt di động (Mobile Web trên iOS/Android), không yêu cầu tải ứng dụng từ kho ứng dụng (App Store / Google Play).

---

## 2. Bố cục Chuẩn của Báo cáo 07

Báo cáo Hướng dẫn sử dụng mẫu 07 gồm 3 phần trọng tâm:

```
HỆ THỐNG QUẢN LÝ HIẾN MÁU TÌNH NGUYỆN CÓ TÍCH HỢP AI (MẠCH ĐỎ)
TÀI LIỆU HƯỚNG DẪN SỬ DỤNG – V1.0

1. GIỚI THIỆU ỨNG DỤNG
   1.1 Tổng quan về hệ thống Mạch Đỏ
   1.2 Các nhóm người dùng & Phân hệ truy cập (Web Admin, Mobile Web TNV, AI Engine)
2. CẤU HÌNH PHẦN CỨNG - PHẦN MỀM
   2.1 Yêu cầu phần cứng (Máy tính cá nhân, Smartphone/Tablet, Băng thông mạng Internet)
   2.2 Môi trường phần mềm (Trình duyệt web Chrome/Safari/Edge, Tài khoản & Quyền truy cập)
3. CÁC CHỨC NĂNG CHÍNH THEO VAI TRÒ (TASK-ORIENTED GUIDELINES)
   3.1 Chức năng của Tình nguyện viên (TNV)
       3.1.1 Đăng ký tài khoản mới (UC001)
       3.1.2 Đăng nhập hệ thống (UC002)
       3.1.3 Đăng ký tham gia hiến máu (UC004)
       3.1.4 Xem và quản lý lịch đã đăng ký (UC004)
       3.1.5 Hỏi đáp với AI Assistant (UC006)
       3.1.6 Nhận thông báo nhắc lịch tự động (UC007)
   3.2 Chức năng của Điều phối viên (Coordinator)
       3.2.1 Đăng nhập & Điều hướng Dashboard
       3.2.2 Quản lý chiến dịch hiến máu (UC003)
       3.2.3 Quản lý điểm hiến & Khung giờ (Slot Capacity)
       3.2.4 Xem báo cáo & Thống kê chiến dịch (UC005)
       3.2.5 Hỏi đáp AI hỗ trợ nghiệp vụ (UC006)
   3.3 Chức năng của Quản trị viên (Admin)
       3.3.1 Đăng nhập & Dashboard Quản trị
       3.3.2 Quản lý tài khoản & Phân quyền người dùng
       3.3.3 Xem báo cáo & Thống kê toàn hệ thống (UC005)
       3.3.4 Hỏi đáp AI & Kiểm toán an toàn (UC006)
       3.3.5 Phê duyệt chiến dịch hiến máu (UC003)
       3.3.6 Quản lý tài liệu quy trình chuẩn cho AI (UC006 / Grounding Knowledge)
```

---

## 3. Quy chuẩn Soạn thảo Hướng dẫn Chi tiết

### 3.1 Cấu trúc một bước hướng dẫn (Standard Step Format)
Mỗi chức năng nghiệp vụ bắt buộc phải được mô tả tuần tự theo cấu trúc sau:
1. **Tiêu đề mục:** Đánh số phân cấp rõ ràng kèm mã Use Case, ví dụ: `3.1.3. Đăng ký tham gia hiến máu (UC004)`.
2. **Các bước thao tác (Numbered Steps):**
   - *Bước 1 (Điểm bắt đầu):* Chỉ rõ màn hình xuất phát và nút bấm/liên kết cần nhấp.
   - *Bước 2 (Nhập liệu / Lựa chọn):* Mô tả chính xác các trường dữ liệu cần điền, dữ liệu bắt buộc và định dạng hợp lệ.
   - *Bước 3 (Thao tác kích hoạt):* Nút bấm xác nhận (Lưu, Xác nhận đăng ký, Gửi câu hỏi...).
   - *Bước 4 (Phản hồi của hệ thống):* Mô tả cách hệ thống báo hiệu thành công (thông báo Toast/Modal, chuyển màn hình, cập nhật số liệu).
3. **Mục Lưu ý (Preconditions & Constraints):**
   - Chỉ rõ các ràng buộc nghiệp vụ (Business Rules).
   - Hướng dẫn cách xử lý khi gặp thông báo lỗi (Validation Error Messages).

### 3.2 Nội dung chuẩn cho 3 Phân hệ Vai trò

#### Phân hệ 1: Tình nguyện viên (TNV)
- **Đăng ký (UC001):** Hướng dẫn nhập Họ tên, Email, Số điện thoại và Mật khẩu; xác thực email chưa tồn tại trong hệ thống.
- **Đăng nhập (UC002):** Nhập email và mật khẩu; cơ chế xử lý khi quên thông tin hoặc tài khoản bị khóa.
- **Đăng ký hiến máu (UC004):**
  - Mở danh sách chiến dịch ➔ xem chi tiết địa điểm, thời gian, số chỗ còn trống trong từng khung giờ.
  - Chọn khung giờ (slot) ➔ điền phiếu khai báo sàng lọc sơ bộ (xác nhận tuổi từ 18–60, cân nặng $\ge 42\text{ kg}$, không mắc bệnh truyền nhiễm, đảm bảo khoảng cách $\ge 84\text{ ngày}$ so với lần hiến máu gần nhất).
  - Bấm "Xác nhận đăng ký" ➔ nhận mã phiếu hẹn và kích hoạt thông báo nhắc lịch tự động.
- **Quản lý lịch hẹn (UC004):** Tra cứu phiếu hẹn, kiểm tra trạng thái (*Chờ hiến*, *Đã hiến*, *Đã hủy*), thao tác hủy hẹn nếu có lý do đột xuất trước ngày ca hiến.
- **Hỏi đáp AI (UC006):** Mở hộp thoại chat AI ở góc màn hình, đặt câu hỏi về điều kiện hiến máu, lưu ý trước/sau khi hiến máu; nhận câu trả lời có trích dẫn nguồn tài liệu chuẩn.
- **Nhận thông báo nhắc lịch (UC007):** Hướng dẫn mở mục "Thông báo" để xem thư nhắc lịch tự động do AI gửi trước ngày diễn ra ca hiến.

#### Phân hệ 2: Điều phối viên (Coordinator)
- **Quản lý chiến dịch (UC003):** Tạo mới chiến dịch, nhập tên chương trình, ngày bắt đầu – kết thúc, địa điểm, chỉ tiêu số túi máu; lưu ở trạng thái "Chờ duyệt" gửi Quản trị viên.
- **Quản lý điểm hiến & khung giờ:** Tạo các khung giờ cụ thể (ví dụ 07:30–09:30, 09:30–11:30) kèm giới hạn số lượng tiếp nhận tối đa (`max_capacity`) nhằm kiểm soát lưu lượng, tránh ùn tắc.
- **Báo cáo & Thống kê chiến dịch (UC005):** Lọc số liệu theo chiến dịch phụ trách, theo dõi tỉ lệ người đăng ký, số người có mặt thực tế và số đơn vị máu tiếp nhận.
- **Hỏi đáp AI (UC006):** Tra cứu quy chuẩn tổ chức ca hiến, tiêu chuẩn tiếp nhận máu hoặc cách xử trí sơ cấp cứu tại chỗ.

#### Phân hệ 3: Quản trị viên (Admin)
- **Quản lý tài khoản & phân quyền:** Xem danh sách người dùng, tìm kiếm theo email/vai trò, cấp quyền *Điều phối viên* hoặc khóa tài khoản vi phạm.
- **Phê duyệt chiến dịch (UC003):** Thẩm định kế hoạch chiến dịch do Điều phối viên gửi lên; bấm "Phê duyệt" để mở công khai cho TNV đăng ký hoặc "Từ chối" kèm lý do.
- **Báo cáo & Thống kê toàn hệ thống (UC005):** Phân tích biểu đồ tiếp nhận máu toàn diện theo thời gian, theo đơn vị tổ chức và cơ cấu nhóm máu.
- **Quản lý tri thức AI chuẩn (UC006):** Quản lý kho văn bản quy trình chuẩn trong bảng `QUY_TRINH_HIEN_MAU`, thêm mới/sửa đổi tài liệu y tế được cơ quan thẩm quyền ban hành để làm cơ sở dữ liệu tra cứu duy nhất cho AI Chatbot.

---

## 4. Tiêu chuẩn Kỹ thuật Môi trường & An toàn AI

1. **Kiến trúc Web Responsive:**
   - Người dùng truy cập trực tiếp qua đường dẫn Web (môi trường phát triển: `http://127.0.0.1:8000`).
   - Giao diện tự động co giãn tối ưu theo kích thước màn hình (Desktop/Laptop $\ge 1366\times768$, Smartphone/Tablet hiển thị giao diện dọc tiện dụng).
2. **Quy tắc An toàn Dữ liệu & AI:**
   - **Grounding nghiêm ngặt:** AI Chatbot chỉ giải đáp các thắc mắc hành chính và quy trình hiến máu dựa trên văn bản đã được duyệt, **tuyệt đối không chẩn đoán bệnh hay kê đơn thuốc**.
   - **Bảo mật thông tin y tế:** Không nhập thông tin bệnh án nhạy cảm của người dùng vào các câu hỏi gửi lên AI.

---

## 5. Checklist Thẩm định Báo cáo 07 (Quality Checklist)

Trước khi nghiệm thu hoặc nộp Báo cáo 07, kiểm tra đầy đủ các tiêu chí sau:
- [x] **Trang bìa & Tên hệ thống:** Ghi đúng tên "Mạch Đỏ - Hệ thống Quản lý Hiến máu Tình nguyện có Tích hợp AI", phiên bản V1.0.
- [x] **Không còn placeholder:** Đã thay thế toàn bộ `<Tên Actor>` và các tag mẫu trong Mục lục và nội dung.
- [x] **Môi trường chính xác:** Không đề cập đến việc tải app từ App Store / Google Play; xác định đúng là ứng dụng Web Responsive.
- [x] **Đủ 07 Use Case:** Không bỏ sót bất kỳ Use Case nào, đặc biệt là bước Đăng ký hiến máu (UC004) và Phê duyệt chiến dịch (UC003).
- [x] **Không có câu văn cụt lửng:** Tất cả các mục hướng dẫn AI (3.2.5, 3.3.4) đều được viết hoàn chỉnh các bước thao tác và lưu ý.
- [x] **Định dạng văn bản chuẩn:** Font Times New Roman, cỡ chữ tiêu đề và nội dung phân cấp rõ ràng, các bước thụt đầu dòng (indent) ngay ngắn.

