# Báo cáo cá nhân — Nguyễn Thùy Linh

**MSSV:** 2A202602497 · **Nhóm:** KRAFTON · **Lớp:** K4-L3B
**Vai trò theo phân công:** Corruption suite và repair từ raw snapshot · **Tỷ trọng phân công:** 20%

Báo cáo này trình bày đầy đủ phạm vi vai trò và kết quả kỹ thuật có thể kiểm tra trong repository. Phần ai trực tiếp viết mã, chạy thí nghiệm và các commit cá nhân cần được người đứng tên đối chiếu trước khi nộp.

## 1. Mục tiêu và đầu vào

Mục tiêu của vai trò là corruption suite và repair từ raw snapshot. Đầu vào: 24 clean rows, raw records snapshot và baseline metrics.

## 2. Công việc và cách triển khai

1. Mô phỏng 6 lỗi: bỏ 4 bản ghi mới nhất, xóa 2 summary, chèn noise vào 2 summary, cắt 2 title thành Bad, làm cũ ngày của 8 dòng và nhân bản 2 dòng.
2. Ghi corruption log cùng DOI bị ảnh hưởng, tái tạo text_for_embedding của dữ liệu lỗi và build corrupted collection.
3. Dùng raw records làm nguồn tin cậy để làm sạch lại, build repaired collection và chấm cùng golden set.

**Quyết định kỹ thuật:** Không sửa chắp vá trên corrupted DataFrame; tái tạo từ raw snapshot giúp các trường title, summary, date và DOI trở lại cùng quy tắc cleaning. Phép repair có thể chạy lại để cho cùng nội dung sạch trên cùng snapshot, dù timestamp/report có thể thay đổi.

## 3. Kết quả kiểm chứng

Corrupted dataset có 22 rows sau thao tác bỏ 4 rồi nhân bản 2; repaired trở lại 24 rows. Corrupted GX đạt 3/5, stale ratio 50.0%. Trên snapshot hiện tại, baseline/repaired đạt Hit@1 100.0%; corrupted còn 40.0%. Hit@4 lần lượt là 100.0%, 60.0%, 100.0%. Token F1 lần lượt là 1.0000, 0.7788, 1.0000.

Artifact liên quan:

- [src/ingestion/corruption.py](../src/ingestion/corruption.py)
- [src/pipelines/corruption_flow.py](../src/pipelines/corruption_flow.py)
- [data/results/corruption_log.json](../data/results/corruption_log.json)
- [data/clean/papers_clean_corrupted.json](../data/clean/papers_clean_corrupted.json)
- [data/clean/papers_clean_repaired.json](../data/clean/papers_clean_repaired.json)
- [data/quality/corrupted_quality_report.json](../data/quality/corrupted_quality_report.json)
- [data/results/corrupted_metrics.json](../data/results/corrupted_metrics.json)
- [data/results/repaired_metrics.json](../data/results/repaired_metrics.json)

Sự tồn tại của artifact là bằng chứng về trạng thái dự án, không tự động chứng minh quyền tác giả của một thành viên.

## 4. Bàn giao và phối hợp

Bàn giao corruption log, corrupted/repaired clean datasets, indexes và metrics cho observability/reporting và dashboard.

## 5. Cách tái hiện

- Kiểm tra corruption_log.json liệt kê đúng 6 scenarios và DOI bị tác động.
- Đối chiếu title length/uniqueness lỗi với corrupted quality report và stale ratio 50% với Freshness SLA.
- Chạy lại corruption flow, kiểm tra repaired GX 5/5 và Hit@1/Hit@4 bằng baseline.

## 6. Giới hạn và câu hỏi thuyết trình

**Giới hạn:** Repair cần raw snapshot còn nguyên. Script tự kích hoạt repair khi GX Quality Gate thất bại hoặc Freshness SLA bị vi phạm; timestamp của artifact có thể đổi giữa các lần chạy.

**Câu hỏi có thể gặp:** Nếu được hỏi tính idempotent: cùng raw snapshot và cùng quy tắc cleaning sẽ cho cùng tập DOI/nội dung sạch; collection được xóa và tái tạo thay vì cộng dồn vector cũ.

## 7. Xác nhận nội dung cá nhân

Trước khi nộp, người đứng tên cần đối chiếu mô tả công việc với phần mình thực hiện và lịch sử commit trên nhánh nộp bài. Nếu phân công khác đóng góp thực tế, sửa báo cáo này và TEAM.md cho khớp.

Số liệu toàn nhóm được đối chiếu tại [group_report.md](group_report.md).
