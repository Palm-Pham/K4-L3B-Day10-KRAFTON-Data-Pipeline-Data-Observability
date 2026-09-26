# TEAM — KRAFTON

- Lớp: K4-L3B-DAY10
- Repository: K4-L3B-Day10-KRAFTON-Data-Pipeline-Data-Observability
- Phân công: 5 luồng chính, tỷ trọng đề xuất 20% mỗi người.

## Danh sách và phân công

| STT | Họ và tên | MSSV | Tỷ trọng đề xuất | Phụ trách chính | Bằng chứng cần đối chiếu |
| ---: | :--- | :--- | ---: | :--- | :--- |
| 1 | Văn Thành Huy | 2A20262763 | 20% | Ingestion, raw lineage, cleaning | src/ingestion/crossref.py, cleaning.py; data/raw/, data/clean/ |
| 2 | Võ Đức Tài | 2A202603007 | 20% | GX quality, Freshness SLA, golden evaluation, reporting | src/observability/quality.py, reporting.py, src/evaluation/; data/quality/, data/eval/, data/results/ |
| 3 | Phan Đình Bảo Khôi | 2A202602434 | 20% | Embedding, Chroma, QA retrieval | src/retrieval/embeddings.py, index.py, qa.py, llm.py; data/chroma/, data/embeddings/ |
| 4 | Nguyễn Thùy Linh | 2A202602497 | 20% | Corruption suite và repair từ raw snapshot | src/ingestion/corruption.py, src/pipelines/corruption_flow.py; corruption_log.json, repaired artifacts |
| 5 | Nguyễn Thị Thùy Linh | 2A202602909 | 20% | Orchestration, dashboard và live demo | src/pipelines/phase1.py, script/, dashboard/; kiểm tra end-to-end |

Hai thành viên tên gần giống nhau được phân biệt bằng đầy đủ họ tên và MSSV ở mọi artifact nộp bài.

## Ranh giới công việc và bàn giao

1. Huy bàn giao raw snapshot và clean schema cho Tài, Bảo Khôi và Nguyễn Thùy Linh.
2. Bảo Khôi bàn giao ba Chroma collections và API truy xuất cho Tài và Nguyễn Thị Thùy Linh.
3. Nguyễn Thùy Linh bàn giao corruption log và repaired artifacts cho Tài đánh giá.
4. Tài khóa golden set 10 câu, quality/freshness reports và bảng metrics.
5. Nguyễn Thị Thùy Linh tích hợp pipeline baseline và dashboard trình chiếu từ các artifact đã bàn giao.

Mỗi luồng cần có review chéo ít nhất một lần để giảm nghẽn khi bàn giao. Người phụ trách báo cáo cần lấy số liệu trực tiếp từ artifact, không tự nhập lại kết quả cũ.

## Tự xác nhận đóng góp trước khi nộp

Bảng trên là phân công cân bằng theo yêu cầu nhóm, chưa thay thế bản tự khai đóng góp thực tế. Mỗi thành viên cần bổ sung báo cáo cá nhân, đối chiếu commit của mình trên nhánh nộp bài và xác nhận phần việc đã hoàn thành. Không dùng thông tin cá nhân hoặc kết quả thử nghiệm mẫu từ bản TEAM cũ.

| Thành viên | Xác nhận phần việc thực tế | Báo cáo cá nhân | Commit trên nhánh nộp bài |
| :--- | :---: | :---: | :---: |
| Văn Thành Huy | Chờ xác nhận | Chờ bổ sung | Chờ đối chiếu |
| Võ Đức Tài | Chờ xác nhận | Chờ đối chiếu | Chờ đối chiếu |
| Phan Đình Bảo Khôi | Chờ xác nhận | Chờ bổ sung | Chờ đối chiếu |
| Nguyễn Thùy Linh | Chờ xác nhận | Chờ bổ sung | Chờ đối chiếu |
| Nguyễn Thị Thùy Linh | Chờ xác nhận | Chờ bổ sung | Chờ đối chiếu |
