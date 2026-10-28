---
name: screenflow-db
description: "Hướng dẫn thiết kế phân luồng màn hình (Screen Flow / Wireframe) theo vai trò người dùng (Admin, Điều phối viên, TNV) và thiết kế cơ sở dữ liệu quan hệ (ERD, 9 bảng dữ liệu, ràng buộc toàn vẹn, khóa chính/ngoại, index tối ưu) chuẩn mẫu 06_GenAI_SoftwareDevelopment_screenflow_db cho dự án Mạch Đỏ có tích hợp AI."
---

# Kỹ năng Thiết kế Luồng Màn hình & Cơ sở Dữ liệu (Screen Flow & Database Design)

Skill này cung cấp quy trình, cấu trúc, tiêu chuẩn kỹ thuật và bộ quy tắc kiểm tra để xây dựng tài liệu **Phân luồng màn hình (Screen Flow)** và **Thiết kế Cơ sở dữ liệu quan hệ (Database Design)** chuẩn theo mẫu báo cáo **`06_GenAI_SoftwareDevelopment_screenflow_db`**, phục vụ hệ thống **"Mạch Đỏ - Quản lý hiến máu tình nguyện tích hợp AI"**.

---

## 1. Mục tiêu & Phạm vi áp dụng

- **Mục tiêu:**
  1. **Thiết kế luồng màn hình (Screen Flow):** Ánh xạ trực quan hành trình người dùng (User Journey) từ 07 Use Case đặc tả (UC001 - UC007) sang hệ thống màn hình chức năng phân theo 3 phân hệ vai trò: Quản trị viên (Admin), Điều phối viên (Coordinator/Staff), và Tình nguyện viên/Người hiến máu (Donor/Volunteer), cùng các thành phần dùng chung (Đăng nhập, Đăng ký, Chatbot AI).
  2. **Thiết kế Cơ sở dữ liệu quan hệ:** Xây dựng mô hình thực thể liên kết (ERD) và từ điển dữ liệu (Data Dictionary) cho **09 bảng dữ liệu chuẩn**, bao gồm đầy đủ thuộc tính, kiểu dữ liệu, kích thước, khóa chính (PK), khóa ngoại (FK) và mô tả ngữ nghĩa.
  3. **Đặc tả 4 tầng ràng buộc toàn vẹn:** Ràng buộc thực thể (Entity), tham chiếu (Referential), miền giá trị (Domain), và nghiệp vụ chuyên sâu (Business/Semantic Constraints).
  4. **Tối ưu hóa CSDL & Vận hành AI:** Cấu hình Index, SQLite WAL mode, kiểm soát giao dịch ACID và bảo đảm tri thức chuẩn (Grounding Knowledge Base) cho AI Chatbot không bị ảo giác (hallucination).

- **Phạm vi áp dụng:**
  - Dự án Mạch Đỏ (FastAPI, SQLite, Vanilla JS/CSS Single Page Application).
  - Báo cáo giai đoạn thiết kế UI/UX luồng nghiệp vụ và kiến trúc CSDL quan hệ.

---

## 2. Cấu trúc chuẩn của Báo cáo 06

Báo cáo gồm 2 phần trọng tâm:

```
SCREEN FLOW & TÀI LIỆU THIẾT KẾ CƠ SỞ DỮ LIỆU
1. SCREEN FLOW: PHÂN LUỒNG MÀN HÌNH CỦA ỨNG DỤNG
   1.1 Danh sách màn hình (Phân nhóm theo vai trò, mô tả chức năng, ánh xạ Use Case)
   1.2 Diễn giải luồng chính (User Journey: Khách vãng lai, Đăng nhập phân quyền, Điều phối viên, TNV hiến máu, AI Chatbot)
2. CƠ SỞ DỮ LIỆU (DATABASE DESIGN)
   2.1 Cơ sở dữ liệu quan hệ (Mô hình ERD & Đặc tả chi tiết 09 bảng)
       2.1.1 Bảng NGUOI_DUNG (users)
       2.1.2 Bảng TINH_NGUYEN_VIEN (donors)
       2.1.3 Bảng DIEM_HIEN_MAU (donation locations)
       2.1.4 Bảng CHIEN_DICH (campaigns)
       2.1.5 Bảng LICH_HIEN_MAU (campaign_slots / schedules)
       2.1.6 Bảng DANG_KY_HIEN_MAU (appointments / registrations)
       2.1.7 Bảng THONG_BAO (notifications)
       2.1.8 Bảng CAU_HOI_AI (chat_logs / ai_queries)
       2.1.9 Bảng QUY_TRINH_HIEN_MAU (procedures / approved medical guidelines)
   2.2 Các ràng buộc toàn vẹn trong cơ sở dữ liệu
       2.2.1 Ràng buộc toàn vẹn thực thể (Entity Integrity)
       2.2.2 Ràng buộc toàn vẹn tham chiếu (Referential Integrity & Cascading Rules)
       2.2.3 Ràng buộc miền giá trị (Domain Constraints & Check Rules)
       2.2.4 Ràng buộc nghiệp vụ (Business Rules: Khoảng cách hiến máu, độ tuổi, sức khỏe, hạn mức khung giờ)
   2.3 Bảng tổng hợp khóa chính và khóa ngoại
   2.4 Chiến lược tối ưu hóa chỉ mục (Indexes) & An toàn dữ liệu
```

---

## 3. Chi tiết Phân luồng Màn hình (Screen Flow)

### 3.1 Ma trận Màn hình theo Vai trò & Use Case

| Nhóm vai trò | Tên màn hình | Mô tả / Chức năng chính | Ánh xạ Use Case |
|---|---|---|---|
| **Chung** | Màn hình khởi động / Splash | Tải ứng dụng, kiểm tra trạng thái phiên (JWT/Session). | Hệ thống |
| **Chung** | Đăng ký tài khoản | Nhập thông tin tài khoản, mật khẩu, họ tên, email, SĐT. | UC001 |
| **Chung** | Đăng nhập | Xác thực danh tính, trả về token và điều hướng giao diện theo vai trò. | UC002 |
| **Chung** | Hỏi đáp AI (AI Assistant) | Giao diện trò chuyện trực tiếp với AI; tra cứu quy trình chuẩn y tế, từ chối câu hỏi chẩn đoán bệnh. | UC006 |
| **Quản trị viên** | Dashboard Quản trị viên | Tổng quan số liệu toàn hệ thống, danh sách cảnh báo, truy cập nhanh. | Tổng hợp |
| **Quản trị viên** | Quản lý tài khoản & Phân quyền | Thêm, sửa thông tin, khóa tài khoản, cấp quyền Quản trị / Điều phối / TNV. | Quản trị |
| **Quản trị viên** | Phê duyệt chiến dịch | Thẩm định các chiến dịch do Điều phối viên gửi lên; chuyển trạng thái Hoạt động hoặc Từ chối. | UC003 |
| **Quản trị viên** | Báo cáo & Thống kê nâng cao | Phân tích tỉ lệ tham gia, lượng máu tiếp nhận, hiệu suất chiến dịch theo tháng/quý. | UC005 |
| **Quản trị viên** | Quản lý tri thức AI | Cập nhật, phê duyệt các văn bản quy trình hiến máu chuẩn (`procedures`) làm tri thức grounding. | UC006 |
| **Điều phối viên** | Dashboard Điều phối viên | Giám sát các chiến dịch phụ trách, theo dõi tỉ lệ lấp đầy khung giờ hiến. | Tổng hợp |
| **Điều phối viên** | Quản lý chiến dịch | Khởi tạo, chỉnh sửa thông tin, mục tiêu túi máu, thời gian bắt đầu/kết thúc. | UC003 |
| **Điều phối viên** | Quản lý điểm hiến & Khung giờ | Cấu hình địa điểm (bệnh viện, hội trường), tạo các khung giờ hiến máu kèm sức chứa tối đa. | UC003 |
| **Điều phối viên** | Điểm danh & Cập nhật kết quả | Ghi nhận tình nguyện viên có mặt, hoàn thành hiến máu, lượng máu hiến (ml). | UC004, UC005 |
| **Tình nguyện viên** | Trang chủ Tình nguyện viên | Banner truyền thông, trạng thái sức khỏe, lịch sử hiến máu gần nhất, nút tác vụ nhanh. | Tổng hợp |
| **Tình nguyện viên** | Danh sách chiến dịch | Xem danh sách chiến dịch đang mở tiếp nhận; bộ lọc theo khu vực, thời gian. | UC004 |
| **Tình nguyện viên** | Chi tiết chiến dịch & Chọn giờ | Xem địa chỉ, chỉ đường, điều kiện tham gia; chọn khung giờ còn chỗ trống. | UC004 |
| **Tình nguyện viên** | Xác nhận đăng ký lịch | Khai báo phiếu sàng lọc sơ bộ (cân nặng, tiền sử bệnh, khoảng cách 84 ngày) và xác nhận. | UC004 |
| **Tình nguyện viên** | Quản lý lịch đã đăng ký | Xem mã phiếu hẹn, trạng thái (Chờ hiến / Đã hiến / Hủy hẹn); tải phiếu xác nhận. | UC004 |
| **Tình nguyện viên** | Trung tâm thông báo | Nhận các thông báo do AI tạo tự động (nhắc lịch trước 24h, cảm ơn sau hiến, nhắc hiến lại). | UC007 |

### 3.2 Đặc tả các Luồng di chuyển chính (Navigation Paths)

1. **Luồng Khách vãng lai & Đăng ký (UC001):**
   `Khởi động` ➔ `Đăng nhập` ➔ Nhấn "Đăng ký ngay" ➔ `Form Đăng ký` ➔ Xác thực hợp lệ ➔ Lưu vào CSDL ➔ Điều hướng về `Đăng nhập` kèm thông báo thành công.
2. **Luồng Đăng nhập & Điều phối theo Vai trò (UC002):**
   `Đăng nhập` ➔ Xác thực Email/Password ➔ Kiểm tra `role`:
   - Nếu `role == 'admin'` ➔ Điều hướng sang `Dashboard Quản trị viên`.
   - Nếu `role == 'coordinator'` ➔ Điều hướng sang `Dashboard Điều phối viên`.
   - Nếu `role == 'donor'` ➔ Điều hướng sang `Trang chủ Tình nguyện viên`.
3. **Luồng Đăng ký hiến máu (UC004):**
   `Trang chủ TNV` ➔ `Danh sách chiến dịch` ➔ Chọn chiến dịch ➔ `Chi tiết & Chọn khung giờ` ➔ Chọn slot còn chỗ (`registered < max_capacity`) ➔ `Xác nhận đăng ký` ➔ Lưu bảng `appointments` ➔ Tự động sinh bản ghi `notifications` (UC007) ➔ Chuyển đến `Lịch đã đăng ký`.
4. **Luồng Hỏi đáp AI Grounding (UC006):**
   Có thể truy cập từ Icon Widget nổi ở tất cả các trang ➔ Mở modal/màn hình `Hỏi đáp AI` ➔ Nhập câu hỏi ➔ Hệ thống kiểm duyệt từ khóa y tế nguy hiểm (nếu vi phạm ➔ từ chối an toàn) ➔ Tra cứu tri thức chuẩn trong bảng `procedures` ➔ Trả về câu trả lời có trích dẫn nguồn văn bản y tế.

---

## 4. Đặc tả Chi tiết 09 Bảng Cơ sở Dữ liệu

### 4.1 Bảng `NGUOI_DUNG` (users)
Lưu trữ tài khoản xác thực và phân quyền người dùng trong hệ thống.
- `maNguoiDung` (VARCHAR(20), PK, NOT NULL): Mã định danh duy nhất (VD: USR001, USR002).
- `hoTen` (NVARCHAR(100), NOT NULL): Họ và tên đầy đủ của người dùng.
- `email` (VARCHAR(100), UNIQUE, NOT NULL): Email dùng để đăng nhập và nhận thông báo.
- `soDienThoai` (VARCHAR(15), UNIQUE, NOT NULL): Số điện thoại liên hệ xác thực.
- `matKhauHash` (VARCHAR(255), NOT NULL): Mật khẩu được mã hóa an toàn (PBKDF2/bcrypt).
- `vaiTro` (VARCHAR(20), NOT NULL): Vai trò hệ thống (`admin`, `coordinator`, `donor`).
- `trangThai` (VARCHAR(20), NOT NULL, DEFAULT 'active'): Trạng thái tài khoản (`active`, `locked`).
- `ngayTao` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP): Thời điểm khởi tạo tài khoản.

### 4.2 Bảng `TINH_NGUYEN_VIEN` (donors)
Lưu thông tin hồ sơ y tế, sinh trắc học và lịch sử hiến máu của người hiến.
- `maTNV` (VARCHAR(20), PK, NOT NULL): Mã hồ sơ tình nguyện viên (VD: TNV001).
- `maNguoiDung` (VARCHAR(20), FK, NOT NULL, UNIQUE): Khóa ngoại liên kết 1-1 tới `NGUOI_DUNG.maNguoiDung`.
- `nhomMau` (VARCHAR(5), NOT NULL): Nhóm máu ABO/Rh (`A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, `ChuaRoo`).
- `ngaySinh` (DATE, NOT NULL): Ngày tháng năm sinh (xác thực độ tuổi từ 18 - 60).
- `gioiTinh` (NVARCHAR(10), NOT NULL): Giới tính sinh học (`Nam`, `Nữ`).
- `canNang` (DECIMAL(4,1), NOT NULL): Cân nặng tính bằng kg (phải đạt >= 42kg với nữ, >= 45kg với nam).
- `lanHienCuoi` (DATE, NULL): Ngày hiến máu thành công gần nhất (kiểm tra quy tắc cách nhau >= 84 ngày).
- `soLanHien` (INTEGER, NOT NULL, DEFAULT 0): Tổng số lần đã hiến máu thành công.

### 4.3 Bảng `DIEM_HIEN_MAU` (donation_locations)
Lưu thông tin các cơ sở tiếp nhận, bệnh viện hoặc điểm hiến máu lưu động.
- `maDiemHien` (VARCHAR(20), PK, NOT NULL): Mã định danh địa điểm (VD: DHM001).
- `tenDiemHien` (NVARCHAR(150), NOT NULL): Tên cơ sở (Viện Huyết học, Bệnh viện Bạch Mai...).
- `diaChi` (NVARCHAR(255), NOT NULL): Địa chỉ chi tiết điểm tổ chức.
- `khuVuc` (NVARCHAR(50), NOT NULL): Quận/Huyện/Tỉnh thành phục vụ bộ lọc tìm kiếm.
- `lienHe` (VARCHAR(50), NOT NULL): Số điện thoại hỗ trợ hoặc người liên hệ tại điểm hiến.

### 4.4 Bảng `CHIEN_DICH` (campaigns)
Lưu thông tin các sự kiện/chiến dịch hiến máu tình nguyện.
- `maChienDich` (VARCHAR(20), PK, NOT NULL): Mã chiến dịch (VD: CD001, CD002).
- `tenChienDich` (NVARCHAR(200), NOT NULL): Tên chương trình (VD: "Giọt hồng trao hy vọng").
- `ngayBatDau` (DATE, NOT NULL): Ngày bắt đầu chiến dịch.
- `ngayKetThuc` (DATE, NOT NULL): Ngày kết thúc chiến dịch (`ngayKetThuc >= ngayBatDau`).
- `maDiemHien` (VARCHAR(20), FK, NOT NULL): Tham chiếu tới `DIEM_HIEN_MAU.maDiemHien`.
- `maNguoiTao` (VARCHAR(20), FK, NOT NULL): Tham chiếu tới `NGUOI_DUNG.maNguoiDung` (người lập chiến dịch).
- `chiTieuMau` (INTEGER, NOT NULL): Mục tiêu số đơn vị máu tiếp nhận (VD: 300 túi).
- `trangThai` (VARCHAR(20), NOT NULL): Trạng thái (`draft`, `pending`, `active`, `completed`, `cancelled`).

### 4.5 Bảng `LICH_HIEN_MAU` (campaign_slots)
Phân chia các khung giờ cụ thể trong chiến dịch để giãn cách và kiểm soát lưu lượng.
- `maLich` (VARCHAR(20), PK, NOT NULL): Mã khung giờ (VD: LHM001).
- `maChienDich` (VARCHAR(20), FK, NOT NULL): Khóa ngoại tham chiếu `CHIEN_DICH.maChienDich`.
- `ngayHien` (DATE, NOT NULL): Ngày diễn ra ca hiến.
- `khungGio` (VARCHAR(50), NOT NULL): Khoảng thời gian cụ thể (VD: "07:30 - 09:30", "09:30 - 11:30").
- `soLuongToiDa` (INTEGER, NOT NULL): Sức chứa tối đa trong khung giờ (VD: 40 người).
- `soLuongDaDangKy` (INTEGER, NOT NULL, DEFAULT 0): Số người đã đặt lịch thành công (`<= soLuongToiDa`).

### 4.6 Bảng `DANG_KY_HIEN_MAU` (appointments)
Lưu thông tin chi tiết từng lượt đăng ký tham gia hiến máu của tình nguyện viên.
- `maDangKy` (VARCHAR(20), PK, NOT NULL): Mã phiếu hẹn đăng ký (VD: DK001).
- `maNguoiDung` (VARCHAR(20), FK, NOT NULL): Khóa ngoại tham chiếu `NGUOI_DUNG.maNguoiDung`.
- `maLich` (VARCHAR(20), FK, NOT NULL): Khóa ngoại tham chiếu `LICH_HIEN_MAU.maLich`.
- `ngayDangKy` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP): Thời gian bấm xác nhận đăng ký.
- `trangThai` (VARCHAR(20), NOT NULL): Trạng thái (`registered`, `checked_in`, `completed`, `cancelled`).
- `luongMauHien` (INTEGER, NULL): Thể tích máu hiến thực tế (250ml, 350ml, 450ml).
- `ghiChu` (NVARCHAR(255), NULL): Ghi chú sức khỏe hoặc lý do không đủ điều kiện (nếu có).

### 4.7 Bảng `THONG_BAO` (notifications)
Lưu thông báo nhắc lịch và truyền thông, hỗ trợ dịch vụ thông báo tự động AI.
- `maThongBao` (VARCHAR(20), PK, NOT NULL): Mã thông báo duy nhất (VD: TB001).
- `maNguoiNhan` (VARCHAR(20), FK, NOT NULL): Tham chiếu tới `NGUOI_DUNG.maNguoiDung`.
- `tieuDe` (NVARCHAR(200), NOT NULL): Tiêu đề thông báo.
- `noiDung` (TEXT, NOT NULL): Nội dung chi tiết (sinh tự động qua mẫu AI thông minh).
- `loaiThongBao` (VARCHAR(30), NOT NULL): Loại tin (`reminder`, `urgent`, `health_tip`, `system`).
- `daDoc` (BOOLEAN, NOT NULL, DEFAULT 0): Trạng thái đã đọc (0: Chưa đọc, 1: Đã đọc).
- `ngayGui` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP): Thời điểm gửi thông báo.

### 4.8 Bảng `CAU_HOI_AI` (chat_logs)
Lưu trữ nhật ký đối thoại hỏi đáp với AI Chatbot phục vụ phân tích chất lượng và kiểm toán an toàn.
- `maCauHoi` (VARCHAR(20), PK, NOT NULL): Mã lượt hội thoại (VD: CH001).
- `maNguoiDung` (VARCHAR(20), FK, NOT NULL): Tham chiếu tới `NGUOI_DUNG.maNguoiDung`.
- `noiDungCauHoi` (TEXT, NOT NULL): Câu hỏi do người dùng gửi lên.
- `cauTraLoiAI` (TEXT, NOT NULL): Câu trả lời do hệ thống AI tổng hợp từ quy trình chuẩn.
- `phanLoai` (VARCHAR(50), NOT NULL): Phân loại chủ đề (`dieu_kien_hien`, `quy_trinh`, `sau_khi_hien`).
- `thoiGianHoi` (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP): Thời gian phát sinh hội thoại.

### 4.9 Bảng `QUY_TRINH_HIEN_MAU` (procedures)
Lưu trữ kho văn bản, quy trình kỹ thuật hiến máu được phê duyệt làm cơ sở tri thức chuẩn (Grounding Knowledge Base) cho AI Chatbot tra cứu (phục vụ UC006).
- `maQuyTrinh` (VARCHAR(20), PK, NOT NULL): Mã định danh quy trình chuẩn (VD: PROC001, PROC002).
- `tieuDe` (NVARCHAR(200), NOT NULL): Tiêu đề quy trình (Khám sàng lọc, Hướng dẫn trước hiến máu, Chăm sóc sau hiến máu...).
- `noiDung` (TEXT, NOT NULL): Toàn văn hướng dẫn y tế chính thức được phê duyệt.
- `ngayPheDuyet` (DATETIME, NOT NULL): Thời gian tài liệu được ban hành hoặc cập nhật.
- `nguoiPheDuyet` (VARCHAR(20), FK, NOT NULL): Tham chiếu tới `NGUOI_DUNG.maNguoiDung` (Admin/Cán bộ y tế duyệt văn bản).

---

## 5. Ràng buộc Toàn vẹn & Tối ưu hóa Cơ sở Dữ liệu

### 5.1 Ràng buộc Thực thể & Tham chiếu (PK & FK)

| Bảng nguồn | Khóa chính (PK) | Khóa ngoại (FK) | Bảng đích tham chiếu | Hành vi ON DELETE |
|---|---|---|---|---|
| `NGUOI_DUNG` | `maNguoiDung` | — | — | — |
| `TINH_NGUYEN_VIEN` | `maTNV` | `maNguoiDung` | `NGUOI_DUNG.maNguoiDung` | `CASCADE` |
| `DIEM_HIEN_MAU` | `maDiemHien` | — | — | — |
| `CHIEN_DICH` | `maChienDich` | `maDiemHien`<br>`maNguoiTao` | `DIEM_HIEN_MAU.maDiemHien`<br>`NGUOI_DUNG.maNguoiDung` | `RESTRICT`<br>`RESTRICT` |
| `LICH_HIEN_MAU` | `maLich` | `maChienDich` | `CHIEN_DICH.maChienDich` | `CASCADE` |
| `DANG_KY_HIEN_MAU` | `maDangKy` | `maNguoiDung`<br>`maLich` | `NGUOI_DUNG.maNguoiDung`<br>`LICH_HIEN_MAU.maLich` | `RESTRICT`<br>`RESTRICT` |
| `THONG_BAO` | `maThongBao` | `maNguoiNhan` | `NGUOI_DUNG.maNguoiDung` | `CASCADE` |
| `CAU_HOI_AI` | `maCauHoi` | `maNguoiDung` | `NGUOI_DUNG.maNguoiDung` | `CASCADE` |
| `QUY_TRINH_HIEN_MAU`| `maQuyTrinh` | `nguoiPheDuyet` | `NGUOI_DUNG.maNguoiDung` | `RESTRICT` |

### 5.2 Ràng buộc Miền giá trị & Nghiệp vụ chuyên sâu
1. **Ràng buộc khoảng cách hiến máu (Quy tắc 84 ngày):**
   - Khoảng cách giữa 2 lần hiến máu toàn phần liên tiếp của một tình nguyện viên phải đạt tối thiểu **84 ngày** (12 tuần):
   $$\text{ngayHienMoi} - \text{lanHienCuoi} \ge 84 \text{ ngày}$$
2. **Ràng buộc sức khỏe & thể trạng:**
   - Tuổi tại thời điểm hiến máu: $18 \le \text{Tuoi} \le 60$.
   - Cân nặng: $\text{canNang} \ge 42\text{ kg}$ (nữ) và $\ge 45\text{ kg}$ (nam).
3. **Ràng buộc kiểm soát tải slot (Concurrency Control):**
   - Số lượng đăng ký thành công trong mỗi khung giờ không được vượt quá chỉ tiêu tiếp nhận:
   $$\text{soLuongDaDangKy} \le \text{soLuongToiDa}$$
   - Sử dụng Transaction với mức cô lập phù hợp (`PRAGMA busy_timeout = 5000`) để ngăn Race Condition khi nhiều người cùng đăng ký 1 chỗ cuối.
4. **Ràng buộc an toàn thông tin & AI:**
   - Bảng `CAU_HOI_AI` chỉ lưu nội dung trao đổi thông thường; hệ thống backend áp dụng bộ lọc ngăn chặn lưu trữ dữ liệu bệnh án nhạy cảm của người dùng vào prompt logs.
   - Bảng `QUY_TRINH_HIEN_MAU` là nguồn dữ liệu duy nhất được cung cấp cho AI Chatbot thực hiện RAG/tra cứu câu trả lời chuẩn.

### 5.3 Chỉ mục (Indexes) để tăng tốc truy vấn
```sql
-- Tăng tốc tra cứu tài khoản đăng nhập
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_phone ON users(phone);

-- Tăng tốc truy vấn chiến dịch theo trạng thái và thời gian
CREATE INDEX IF NOT EXISTS idx_campaigns_status_dates ON campaigns(status, start_date, end_date);

-- Tăng tốc tra cứu lịch hẹn của tình nguyện viên và kiểm tra xung đột slot
CREATE INDEX IF NOT EXISTS idx_appointments_donor_slot ON appointments(donor_id, slot_id);

-- Tăng tốc lấy thông báo chưa đọc của người dùng
CREATE INDEX IF NOT EXISTS idx_notifications_recipient_unread ON notifications(recipient_id, is_read);

-- Tăng tốc tìm kiếm từ khóa trong kho tri thức y tế chuẩn của AI
CREATE INDEX IF NOT EXISTS idx_procedures_title ON procedures(title);
```

---

## 6. Checklist Tự kiểm tra Báo cáo 06 (Quality Checklist)

Trước khi nghiệm thu hoặc nộp Báo cáo 06, kiểm tra các tiêu chí sau:
- [x] **Trang bìa & Thông tin nhóm:** Ghi đúng "Nhóm 3 SV", danh sách đầy đủ 3 thành viên (Thành Đạt, Quỳnh Nga, Bích Ngọc).
- [x] **Phân cấp đề mục:** Mục 2.1 đánh số chuẩn xác từ `2.1.1` đến `2.1.9` (không bị sót hay nhảy cóc số thứ tự).
- [x] **Đủ 09 bảng dữ liệu:** Bao gồm đầy đủ `QUY_TRINH_HIEN_MAU` (`procedures`) - thành phần cốt lõi của tính năng AI (UC006).
- [x] **Khóa ngoại & Bảng tổng hợp:** Bảng 9 (Khóa chính) và Bảng 10 (Khóa ngoại) đã bao hàm đầy đủ trường khóa của cả 9 bảng.
- [x] **Ánh xạ Screen Flow:** Mỗi màn hình trong mục 1.1 đều chỉ rõ Use Case liên kết (từ UC001 đến UC007) và luồng phân quyền rõ ràng giữa 3 vai trò.
- [x] **Định dạng Word chuẩn:** Font Times New Roman, dãn dòng 1.15 - 1.5, tiêu đề in đậm, bảng biểu căn lề ngay ngắn có header lặp lại.

