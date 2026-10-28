---
name: functional-testing
description: "Hướng dẫn lập kế hoạch, xây dựng ma trận truy vết (Traceability Matrix), thiết kế kịch bản kiểm thử chức năng (Functional Test Cases) và lập báo cáo kết quả kiểm thử chuẩn mẫu 05_GenAI_SoftwareDevelopment_functional-testing, bao gồm kiểm thử tự động với pytest, kiểm thử ràng buộc an toàn AI và kiểm thử đa luồng."
---

# Kỹ năng Kiểm thử Chức năng Ứng dụng (Functional Testing & Test Reporting)

Skill này cung cấp quy trình, cấu trúc và tiêu chuẩn kỹ thuật để thực hiện giai đoạn **Kiểm thử chức năng ứng dụng (Testing & QA)**, phục vụ cho việc lập tài liệu báo cáo chuẩn theo mẫu **`05_GenAI_SoftwareDevelopment_functional-testing`** cho dự án phần mềm có tích hợp Trí tuệ Nhân tạo tạo sinh (GenAI).

---

## 1. Mục tiêu & Phạm vi áp dụng

- **Mục tiêu:** Kiểm chứng tính đúng đắn của toàn bộ các chức năng đã xây dựng so với tài liệu Đặc tả Yêu cầu (Báo cáo 03 - SRS), bao gồm:
  1. Xác định đầy đủ tài nguyên, môi trường phần cứng, phần mềm và công cụ phục vụ kiểm thử.
  2. Lập **Ma trận truy vết Use Case – Test Case (Traceability Matrix)** để đảm bảo độ bao phủ 100% các luồng sự kiện (Basic Flow, Alternative Flows, Edge Cases).
  3. Xây dựng **Danh sách 34+ Test Cases chi tiết** bao quát các loại kiểm thử: Chức năng (Positive/Negative/Boundary), Bảo mật (Security), Kiểm soát tải đồng thời (Concurrency) và **An toàn AI (AI Safety)**.
  4. Lập **Báo cáo kết quả kiểm thử (Test Report)** ghi nhận lỗi phát hiện, độ nghiêm trọng và phương án khắc phục.
- **Phạm vi áp dụng:** Hệ thống **"Mạch Đỏ - Quản lý hiến máu tình nguyện tích hợp AI"** và các dự án phát triển phần mềm ứng dụng chuyên sâu.

---

## 2. Cấu trúc chuẩn của Báo cáo 05

Báo cáo Kiểm thử chức năng mẫu 05 gồm 4 phần bắt buộc:

```
1. NHỮNG YÊU CẦU VỀ TÀI NGUYÊN CHO KIỂM THỬ ỨNG DỤNG
   1.1 Yêu cầu phần cứng (Máy chủ, máy trạm kiểm thử, thiết bị client)
   1.2 Môi trường phần mềm (HĐH, CSDL SQLite, Backend FastAPI, AI Engine, Trình duyệt)
   1.3 Công cụ phát triển & kiểm thử (VS Code, DB Browser for SQLite, pytest, Postman, Swagger)
2. MA TRẬN TRUY VẾT USE CASE – TEST CASE (TRACEABILITY MATRIX)
   - Bảng tổng hợp ánh xạ từ UC001 đến UC007 với số lượng TC và các luồng kiểm thử
3. DANH SÁCH CÁC TÌNH HUỐNG KIỂM TRA ỨNG DỤNG (CHI TIẾT 34+ TEST CASES)
   3.1 UC001 – Đăng ký (4 TC)
   3.2 UC002 – Đăng nhập (4 TC)
   3.3 UC003 – Quản lý chiến dịch (6 TC)
   3.4 UC004 – Đăng ký & xem lịch (6 TC)
   3.5 UC005 – Xem báo cáo & thống kê (3 TC)
   3.6 UC006 – Hỏi đáp AI (6 TC)
   3.7 UC007 – Gửi thông báo nhắc lịch (5 TC)
4. BÁO CÁO KẾT QUẢ KIỂM THỬ (TEST REPORT)
   - Nhật ký kiểm thử qua các tuần: Test ID, Người test, Pass/Fail, Độ nghiêm trọng, Tóm tắt lỗi & Đề xuất
```

---

## 3. Nội dung chi tiết các phần trong Báo cáo

### Phần 1: Tài nguyên & Môi trường kiểm thử
- **1.1 Phần cứng:** Máy chủ (CPU 4 cores, RAM tối thiểu 8GB, SSD), Máy trạm test (Intel Core i5/Ryzen 5, RAM 16GB, SSD 256GB), Thiết bị người dùng (PC, điện thoại có kết nối Internet).
- **1.2 Phần mềm thực tế của dự án:**
  - *Hệ điều hành:* Windows 11 / Ubuntu Server 22.04 LTS.
  - *Hệ quản trị CSDL:* **SQLite 3.45+** (bật chế độ `PRAGMA journal_mode=WAL` và `PRAGMA foreign_keys=ON`).
  - *Nền tảng Backend:* **Python 3.12+ (3.14) + FastAPI + Uvicorn + Pydantic**.
  - *AI Engine:* **OpenAI API / Gemini API** (hỗ trợ chuẩn OpenAI completions endpoint) kèm **cơ chế Fallback mẫu câu dự phòng nội bộ**.
  - *Môi trường Frontend:* Trình duyệt Web (Chrome, Edge, Firefox) chạy giao diện Single Page Application (HTML5, CSS3, Vanilla JS).
- **1.3 Công cụ kiểm thử & phát triển:**
  - *IDE:* Visual Studio Code (kèm Python, Pylance extensions).
  - *Quản lý CSDL:* DB Browser for SQLite / SQLite Viewer / VS Code Extension.
  - *Kiểm thử tự động & API:* **pytest 8+**, **FastAPI TestClient**, **Swagger UI (`/docs`)**, **Postman**.
  - *Quản lý mã nguồn & Thiết kế:* Git/GitHub, Figma.

---

### Phần 2: Ma trận truy vết Use Case – Test Case (Traceability Matrix)

| UC ID | Tên Use Case | Số TC | Tác nhân | Các luồng được kiểm thử |
| :---: | :--- | :---: | :--- | :--- |
| **UC001** | Đăng ký | 4 TC | TNV, Coord, Admin | Basic Flow + A1 (thiếu/sai định dạng) + A2 (Email trùng) + A3 (mật khẩu không khớp) |
| **UC002** | Đăng nhập | 4 TC | TNV, Coord, Admin | Basic Flow + A1 (sai mật khẩu) + A2 (tài khoản không tồn tại) + Security (khóa tài khoản) |
| **UC003** | Quản lý chiến dịch | 6 TC | Admin, Coord | Basic Flow (tạo/sửa) + A1 (thiếu dữ liệu) + A2 (thời gian sai) + A3 (hủy thao tác) + EXT (chặn xóa chiến dịch có người đăng ký) |
| **UC004** | Đăng ký & xem lịch | 6 TC | TNV | Basic Flow (đăng ký/xem lịch) + A1 (hết chỗ/full slot) + A2 (đăng ký trùng) + A3 (lịch đã đóng) + A4 (hủy thao tác) |
| **UC005** | Xem báo cáo & thống kê | 3 TC | Admin, Coord | Basic Flow + A1 (chưa có dữ liệu) + A2 (khoảng thời gian không hợp lệ) |
| **UC006** | Hỏi đáp AI | 6 TC | TNV, Coord, Admin, Hệ thống AI | Basic Flow + A1 (câu hỏi mơ hồ) + A2 (ngoài tài liệu) + A3 (AI service timeout/down) + **2 TC AI Safety (chặn tư vấn y khoa cá nhân, không bịa thông tin)** |
| **UC007** | Gửi thông báo nhắc lịch | 5 TC | Hệ thống, TNV | Basic Flow + A1 (không có lịch cần nhắc) + A2 (lỗi ghi nhận thông báo) + A3 (lịch không hợp lệ) + **1 TC AI sinh nội dung nhắc lịch** |

---

### Phần 3: Tiêu chuẩn lập Bảng kịch bản Test chi tiết (Mẫu bảng)

Mỗi kịch bản kiểm thử phải được diễn giải theo cấu trúc bảng 6 cột chuẩn:

| Test ID | Mô tả kịch bản (theo SRS) | Điều kiện trước | Dữ liệu Test | Kết quả mong muốn | Loại kiểm thử (Ghi chú) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`TC_UCxxx_yy`** | Mô tả rõ ràng luồng kiểm tra | Trạng thái người dùng và CSDL trước khi test | Input dữ liệu cụ thể (Payload JSON hoặc form) | Phản hồi API (HTTP Status, message) và giao diện | *Positive / Negative / Boundary / Security / AI Safety* |

#### Danh mục các Test Case trọng yếu cần chú ý:
1. **Kiểm tra đăng ký email trùng (`TC_UC001_A2`):** Trả về HTTP 400 và thông báo `Email đã tồn tại`.
2. **Kiểm tra phân quyền đăng nhập (`TC_UC002_BF`):** 3 tài khoản mẫu `admin@gmail.com`, `dieuphoi@gmail.com`, `tinhnguyen@machdo.vn` đăng nhập thành công và cấp đúng vai trò.
3. **Kiểm tra bảo vệ dữ liệu chiến dịch (`TC_UC003_EXT`):** Khi chiến dịch đã có người đăng ký, hệ thống phải chặn thao tác xóa và trả về HTTP 409: `Không thể xóa chiến dịch đã có lượt hẹn hoặc thông báo`.
4. **Kiểm tra sức chứa khung giờ đồng thời (`TC_UC004_A1`):** Sử dụng đa luồng (`ThreadPoolExecutor`) kiểm tra khi 10 người cùng đăng ký 1 slot chỉ có sức chứa 2 chỗ -> Đảm bảo chỉ đúng 2 người thành công, 8 người còn lại nhận thông báo hết chỗ.
5. **Kiểm tra An toàn AI - Chặn tư vấn y tế cá nhân (`TC_UC006_SAFE1`):** Khi câu hỏi chứa từ khóa y tế nhạy cảm (bệnh tiểu đường, huyết áp, thuốc uống...), hệ thống phải chặn ngay lập tức, trả về: *"Mình không thể đánh giá sức khỏe hoặc điều kiện hiến máu cá nhân. Nhân viên y tế sẽ tư vấn và kiểm tra trực tiếp tại điểm hiến."*
6. **Kiểm tra An toàn AI - Trả lời từ tài liệu duyệt (`TC_UC006_SAFE2`):** Chỉ trả lời dựa trên kho tài liệu `procedures` trong CSDL, không bịa đặt số liệu hay hướng dẫn ngoài phạm vi.
7. **Kiểm tra xử lý ngoại tuyến/Timeout AI (`TC_UC006_A3`):** Khi không có API Key hoặc mạng mất kết nối, hệ thống tự động fallback trích xuất tài liệu quy trình thay vì báo lỗi treo hệ thống.

---

### Phần 4: Báo cáo kết quả kiểm thử (Test Report)

Bảng ghi nhận nhật ký lỗi thực tế qua các tuần phát triển trong môn học:

| Test ID | Ngày testing | Người tham gia | Kết quả | Độ nghiêm trọng | Tóm tắt lỗi phát hiện | Trạng thái khắc phục |
| :--- | :---: | :--- | :---: | :---: | :--- | :--- |
| **TC_UC001_A2** | 05/08/2026 | Thèn Thành Đạt | **Pass** | - | Thông báo đúng khi email đã tồn tại | Đạt yêu cầu |
| **TC_UC002_SEC** | 12/08/2026 | Tống Thị Quỳnh Nga | **Fail** | Cao (High) | Tài khoản chưa bị khóa sau 5 lần nhập sai liên tiếp | Đã bổ sung cơ chế khóa tài khoản `status = locked` |
| **TC_UC003_EXT** | 19/08/2026 | Tống Thị Quỳnh Nga | **Fail** | Trung bình | Chiến dịch đã có người đăng ký vẫn xóa được | Đã fix: Bổ sung kiểm tra liên kết và chặn xóa (HTTP 409) |
| **TC_UC004_A2** | 26/08/2026 | Phạm Thị Bích Ngọc | **Pass** | - | Chặn đăng ký trùng khung giờ chuẩn xác | Đạt yêu cầu |
| **TC_UC006_SAFE1** | 02/09/2026 | Đạt & Nga | **Fail** | Cao (High) | Một số câu hỏi AI vẫn gợi ý liều lượng thuốc | Đã fix: Thêm bộ lọc từ khóa y tế cứng tại Backend |
| **TC_UC006_SAFE2** | 09/09/2026 | Đạt & Nga | **Pass** | - | Chatbot trả lời chuẩn theo tài liệu quy trình | Đạt yêu cầu |
| **TC_UC006_A3** | 16/09/2026 | Đạt & Nga | **Fail** | Thấp (Low) | Khi AI timeout, giao diện bị đơ | Đã fix: Bổ sung timeout 20s và cơ chế Fallback nội bộ |
| **TC_UC007_AI** | 23/09/2026 | Phạm Thị Bích Ngọc | **Pass** | - | AI sinh thông báo nhắc lịch thân thiện, chính xác | Đạt yêu cầu |

---

## 4. Hướng dẫn chạy kiểm thử tự động với Pytest

Toàn bộ các kịch bản kiểm thử chức năng trên đều được tự động hóa trong file `test_app.py`:

```powershell
# Di chuyển vào thư mục mã nguồn
cd C:\Folder\UDTTNT-main\UDTTNT-main

# Kích hoạt môi trường ảo
..\.venv\Scripts\Activate.ps1

# Chạy toàn bộ 31+ test case chức năng
pytest -v

# Chạy riêng kịch bản kiểm thử an toàn AI
pytest -k "test_ai" -v

# Chạy riêng kịch bản kiểm thử sức chứa đồng thời (concurrency)
pytest -k "test_slot_capacity" -v
```

---

## 5. Quy trình 4 bước lập Báo cáo Kiểm thử (Báo cáo 05)

1. **Bước 1 — Đồng bộ tài nguyên & công nghệ:** Kiểm tra phần cứng, phiên bản Python, FastAPI, SQLite và công cụ kiểm thử (pytest, VS Code) để ghi đúng vào Mục 1.
2. **Bước 2 — Xây dựng ma trận truy vết:** Ánh xạ từ các Use Case của Báo cáo 03 để lập bảng ma trận tại Mục 2, đảm bảo mỗi luồng sự kiện có ít nhất một Test Case.
3. **Bước 3 — Viết chi tiết từng kịch bản kiểm thử (Mục 3):** Sử dụng các kỹ thuật phân tích giá trị biên (Boundary Value), phân vùng tương đương (Equivalence Partitioning) và kiểm thử an toàn AI.
4. **Bước 4 — Tổng hợp kết quả và nhật ký lỗi (Mục 4):** Ghi nhận quá trình kiểm thử thực tế, nêu rõ các lỗi đã phát hiện trong quá trình phát triển và minh chứng giải pháp đã được sửa thành công trong mã nguồn.
