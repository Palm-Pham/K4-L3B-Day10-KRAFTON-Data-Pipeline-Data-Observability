# Báo cáo cá nhân — Nguyễn Thùy Linh

> Bản nháp theo phân công nhóm. Người đứng tên cần rà phần việc thực tế, bổ sung commit/minh chứng cá nhân và xác nhận trước khi nộp.

## Thông tin và vai trò

- Họ và tên: **Nguyễn Thùy Linh**
- MSSV: **2A202602497**
- Nhóm/lớp: KRAFTON · K4-L3B
- Vai trò được phân công: **Corruption suite và repair từ raw snapshot**
- Tỷ trọng phân công đề xuất: **20%**

## Phạm vi được phân công

**Đầu vào:** Cleaned dataset, raw snapshot và baseline metrics.

1. Rà 6 kịch bản drop records, blank summary, inject noise, truncate title, stale date và duplicate rows trong src/ingestion/corruption.py.
2. Đối chiếu corruption log, dữ liệu lỗi và quality/freshness alerts.
3. Kiểm tra luồng tái tạo cleaned data và Chroma repaired từ raw snapshot trong src/pipelines/corruption_flow.py.

**Bàn giao:** Bàn giao corrupted/repaired artifacts để chấm trên cùng golden set và tạo bảng so sánh.

## Artifact hiện có để đối chiếu

- [data/results/corruption_log.json](../data/results/corruption_log.json)
- [data/clean/papers_clean_corrupted.json](../data/clean/papers_clean_corrupted.json)
- [data/clean/papers_clean_repaired.json](../data/clean/papers_clean_repaired.json)
- [data/results/corrupted_metrics.json](../data/results/corrupted_metrics.json)
- [data/results/repaired_metrics.json](../data/results/repaired_metrics.json)

Các artifact trên chứng minh trạng thái repository; chỉ riêng sự tồn tại của chúng không chứng minh ai đã viết mã hoặc chạy thí nghiệm.

## Cách kiểm chứng phần việc

Đối chiếu 24 baseline, 22 corrupted và 24 repaired records; Freshness 4.2% → 50.0% → 4.2%.

## Tự xác nhận trước khi nộp

- [ ] Tôi đã thực hiện hoặc review đúng các mục được ghi trong báo cáo này.
- [ ] Tôi đã đối chiếu commit của mình trên nhánh nộp bài.
- [ ] Tôi có thể giải thích input, output, giới hạn và cách kiểm chứng của phần việc.
- [ ] Tôi đã sửa các mục không đúng với đóng góp thực tế của mình.

Báo cáo kết quả chung và các số liệu cập nhật nằm ở [group_report.md](group_report.md).
