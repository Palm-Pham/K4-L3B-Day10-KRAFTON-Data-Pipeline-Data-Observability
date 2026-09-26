# Báo cáo cá nhân — Nguyễn Thị Thùy Linh

> Bản nháp theo phân công nhóm. Người đứng tên cần rà phần việc thực tế, bổ sung commit/minh chứng cá nhân và xác nhận trước khi nộp.

## Thông tin và vai trò

- Họ và tên: **Nguyễn Thị Thùy Linh**
- MSSV: **2A202602909**
- Nhóm/lớp: KRAFTON · K4-L3B
- Vai trò được phân công: **Orchestration, dashboard và live demo**
- Tỷ trọng phân công đề xuất: **20%**

## Phạm vi được phân công

**Đầu vào:** Raw/clean artifacts, ba Chroma collections, quality reports và metrics.

1. Kiểm tra thứ tự ingest → clean → index → evaluate → report trong src/pipelines/phase1.py.
2. Chạy luồng corruption/repair và đối chiếu artifact cuối cùng; kết nối các phần việc qua script/.
3. Chuẩn bị dashboard/ và kịch bản trình bày baseline, corrupted, repaired cùng live retrieval.

**Bàn giao:** Tích hợp các artifact đã khóa từ bốn luồng còn lại để demo nhất quán.

## Artifact hiện có để đối chiếu

- [script/run_phase1.py](../script/run_phase1.py)
- [script/run_corruption_flow.py](../script/run_corruption_flow.py)
- [script/run_dashboard.py](../script/run_dashboard.py)
- [dashboard/index.html](../dashboard/index.html)
- [data/reports/phase1_report.md](../data/reports/phase1_report.md)
- [data/reports/corruption_report.md](../data/reports/corruption_report.md)

Các artifact trên chứng minh trạng thái repository; chỉ riêng sự tồn tại của chúng không chứng minh ai đã viết mã hoặc chạy thí nghiệm.

## Cách kiểm chứng phần việc

Kiểm tra hai pipeline chạy exit 0 trên máy nộp bài, dashboard localhost hiển thị số liệu từ artifact, không nhập số liệu thủ công.

## Tự xác nhận trước khi nộp

- [ ] Tôi đã thực hiện hoặc review đúng các mục được ghi trong báo cáo này.
- [ ] Tôi đã đối chiếu commit của mình trên nhánh nộp bài.
- [ ] Tôi có thể giải thích input, output, giới hạn và cách kiểm chứng của phần việc.
- [ ] Tôi đã sửa các mục không đúng với đóng góp thực tế của mình.

Báo cáo kết quả chung và các số liệu cập nhật nằm ở [group_report.md](group_report.md).
