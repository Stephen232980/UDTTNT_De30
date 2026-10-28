# Human Verification Gates

Báo cáo này ghi nhận trạng thái hồ sơ trong workspace, không tự xác nhận phê duyệt. Hiện chưa tìm thấy biên bản, người ký hoặc bằng chứng approval; cả ba gate đang **Chờ xác nhận**.

| Gate | Nội dung cần con người duyệt | Trạng thái | Bằng chứng cần lưu |
|---|---|---|---|
| Requirements Approval | Phạm vi FR/NFR, role, policy đăng ký, privacy, nguồn procedure và tiêu chí nghiệm thu. | Chờ phê duyệt; chưa có tên/ngày/bằng chứng. | Người duyệt, vai trò, ngày, phiên bản requirements, quyết định và issue còn mở. |
| Architecture Approval | FastAPI/SPA/SQLite boundaries, session, AI/provider, dữ liệu truyền ra ngoài, vận hành. | Chờ phê duyệt; chưa có tên/ngày/bằng chứng. | ADR được duyệt, threat/privacy review, người duyệt và ngày. |
| Code Release Approval | Test report, code/security review, migration/backup, demo credentials, production readiness. | Chờ phê duyệt; chưa có tên/ngày/bằng chứng. | Release/commit, test run, unresolved findings, sign-off của người chịu trách nhiệm. |

## Quy tắc cập nhật
Chỉ đổi trạng thái sau khi có xác nhận thực tế. Không dùng kết quả pytest hoặc nội dung do AI tạo thay cho quyết định của product owner, architect, security reviewer hoặc release owner. Lưu evidence có thể kiểm toán và gắn phiên bản tài liệu/code.
