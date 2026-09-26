# TEAM — KRAFTON

- Lớp: K4-L3B-DAY10
- Repository: K4-L3B-Day10-KRAFTON-Data-Pipeline-Data-Observability
- Phân công: 5 luồng chính, tỷ trọng đề xuất 20% mỗi người.

## Danh sách và phân công

| STT | Họ và tên          | MSSV        | Tỷ trọng đề xuất | Phụ trách chính                                         | Bằng chứng cần đối chiếu                                                                               |
| --: | :----------------- | :---------- | ---------------: | :------------------------------------------------------ | :----------------------------------------------------------------------------------------------------- |
|   1 | Văn Thành Huy      | 2A20262763  |              20% | Ingestion, raw lineage, cleaning                        | src/ingestion/crossref.py, cleaning.py; data/raw/, data/clean/                                         |
|   2 | Võ Đức Tài         | 2A202603007 |              20% | GX quality, Freshness SLA, golden evaluation, reporting | src/observability/quality.py, reporting.py, src/evaluation/; data/quality/, data/eval/, data/results/  |
|   3 | Phan Đình Bảo Khôi | 2A202602434 |              20% | Embedding, Chroma, QA retrieval                         | src/retrieval/embeddings.py, index.py, qa.py, llm.py; data/chroma/, data/embeddings/                   |
|   4 | Nguyễn Thùy Linh   | 2A202602497 |              20% | Corruption suite và repair từ raw snapshot              | src/ingestion/corruption.py, src/pipelines/corruption_flow.py; corruption_log.json, repaired artifacts |
|   5 | Phạm Thị Thùy Linh | 2A202602909 |              20% | Orchestration, dashboard và live demo                   | src/pipelines/phase1.py, script/, dashboard/; kiểm tra end-to-end                                      |

Hai thành viên tên gần giống nhau được phân biệt bằng đầy đủ họ tên và MSSV ở mọi artifact nộp bài.

## Ranh giới công việc và bàn giao

1. Huy bàn giao raw snapshot và clean schema cho Tài, Bảo Khôi và Nguyễn Thùy Linh.
2. Bảo Khôi bàn giao ba Chroma collections và API truy xuất cho Tài và Phạm Thị Thùy Linh.
3. Nguyễn Thùy Linh bàn giao corruption log và repaired artifacts cho Tài đánh giá.
4. Tài khóa golden set 10 câu, quality/freshness reports và bảng metrics.
5. Phạm Thị Thùy Linh tích hợp pipeline baseline và dashboard trình chiếu từ các artifact đã bàn giao.

Mỗi luồng cần có review chéo ít nhất một lần để giảm nghẽn khi bàn giao. Người phụ trách báo cáo cần lấy số liệu trực tiếp từ artifact, không tự nhập lại kết quả cũ.

## Nội dung tự khai theo phân công

Nội dung dưới đây đã được điền theo tên và công việc của từng thành viên. Đây là phạm vi được giao, không phải bằng chứng rằng cá nhân đã tự viết mã. Mỗi người cần kiểm tra và sửa bản báo cáo cá nhân trước khi nộp.

### Văn Thành Huy — 2A20262763

- Vai trò: Ingestion, raw lineage và cleaning (20% phân công đề xuất).
- Phần việc: Kiểm tra parse DOI, tiêu đề, abstract, tác giả, chủ đề và ngày xuất bản trong src/ingestion/crossref.py.
- Phần việc: Duy trì hai raw artifacts và fallback local khi không tải được payload mới.
- Phần việc: Chuẩn hóa JATS/whitespace, bỏ DOI trùng, tính age_days và tạo text_for_embedding trong src/ingestion/cleaning.py.
- Bàn giao: Bàn giao schema sạch và raw snapshot cho index, quality checks và repair.
- Báo cáo cá nhân đã điền: [report/2A20262763_VanThanhHuy.md](../report/2A20262763_VanThanhHuy.md).

### Võ Đức Tài — 2A202603007

- Vai trò: GX quality, Freshness SLA, golden evaluation và reporting (20% phân công đề xuất).
- Phần việc: Kiểm tra 5 Great Expectations và Freshness SLA trong src/observability/quality.py.
- Phần việc: Giữ golden set 10 câu, challenge set 2 câu và tính Hit@1, Hit@4, Token F1 trong src/evaluation/.
- Phần việc: Đối chiếu báo cáo pha 1, corruption report và bảng số liệu trong src/observability/reporting.py.
- Bàn giao: Bàn giao quality/freshness signal, golden set và metrics cho dashboard/demo.
- Báo cáo cá nhân đã điền: [report/2A202603007_VoDucTai.md](../report/2A202603007_VoDucTai.md).

### Phan Đình Bảo Khôi — 2A202602434

- Vai trò: Embedding, Chroma index và QA retrieval (20% phân công đề xuất).
- Phần việc: Kiểm tra MiniLM embeddings và fallback local trong src/retrieval/embeddings.py.
- Phần việc: Quản lý ba Chroma collections, đối sánh DOI/tiêu đề và BM25 rerank trong src/retrieval/index.py.
- Phần việc: Kiểm tra QA metadata và chế độ LLM có trích dẫn DOI trong src/retrieval/qa.py, llm.py.
- Bàn giao: Bàn giao hàm truy xuất và ba index cho evaluation và live demo.
- Báo cáo cá nhân đã điền: [report/2A202602434_PhanDinhBaoKhoi.md](../report/2A202602434_PhanDinhBaoKhoi.md).

### Nguyễn Thùy Linh — 2A202602497

- Vai trò: Corruption suite và repair từ raw snapshot (20% phân công đề xuất).
- Phần việc: Rà 6 kịch bản drop records, blank summary, inject noise, truncate title, stale date và duplicate rows trong src/ingestion/corruption.py.
- Phần việc: Đối chiếu corruption log, dữ liệu lỗi và quality/freshness alerts.
- Phần việc: Kiểm tra luồng tái tạo cleaned data và Chroma repaired từ raw snapshot trong src/pipelines/corruption_flow.py.
- Bàn giao: Bàn giao corrupted/repaired artifacts để chấm trên cùng golden set và tạo bảng so sánh.
- Báo cáo cá nhân đã điền: [report/2A202602497_NguyenThuyLinh.md](../report/2A202602497_NguyenThuyLinh.md).

### Phạm Thị Thùy Linh — 2A202602909

- Vai trò: Orchestration, dashboard và live demo (20% phân công đề xuất).
- Phần việc: Kiểm tra thứ tự ingest → clean → index → evaluate → report trong src/pipelines/phase1.py.
- Phần việc: Chạy luồng corruption/repair và đối chiếu artifact cuối cùng; kết nối các phần việc qua script/.
- Phần việc: Chuẩn bị dashboard/ và kịch bản trình bày baseline, corrupted, repaired cùng live retrieval.
- Bàn giao: Tích hợp các artifact đã khóa từ bốn luồng còn lại để demo nhất quán.
- Báo cáo cá nhân đã điền: [report/2A202602909_PhamThiThuyLinh.md](../report/2A202602909_PhamThiThuyLinh.md).

## Xác nhận trước khi nộp

| Thành viên         | Nội dung theo phân công | Báo cáo cá nhân  | Commit/đóng góp thực tế |
| :----------------- | :---------------------: | :--------------: | :---------------------: |
| Văn Thành Huy      |         Đã điền         | Đã điền nội dung |  Chờ cá nhân xác nhận   |
| Võ Đức Tài         |         Đã điền         | Đã điền nội dung |  Chờ cá nhân xác nhận   |
| Phan Đình Bảo Khôi |         Đã điền         | Đã điền nội dung |  Chờ cá nhân xác nhận   |
| Nguyễn Thùy Linh   |         Đã điền         | Đã điền nội dung |  Chờ cá nhân xác nhận   |
| Phạm Thị Thùy Linh |         Đã điền         | Đã điền nội dung |  Chờ cá nhân xác nhận   |
