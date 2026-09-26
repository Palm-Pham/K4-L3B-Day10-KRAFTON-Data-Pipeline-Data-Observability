# Báo cáo nhóm — Day 10: Data Pipeline & Data Observability

> Nhóm KRAFTON · K4-L3B · Ngày cập nhật: 2026-09-26
> Báo cáo đối chiếu trực tiếp với artifact trong repository. Phần phân công 5 người là phương án cân bằng cần được từng thành viên xác nhận trước khi nộp.

## 1. Tóm tắt

Pipeline đọc snapshot Crossref, chuẩn hóa 24 bản ghi thành 24 tài liệu sạch, tạo MiniLM embeddings và lưu ba collection ChromaDB. Great Expectations 1.x và Freshness SLA kiểm tra chất lượng dữ liệu. Cùng một golden set 10 câu hỏi được dùng cho baseline, corrupted và repaired.

- Baseline: Hit@1 100.0%, Hit@4 100.0%, Token F1 1.0000; GX đạt 5/5 checks.
- Corrupted: Hit@1 40.0%, Hit@4 60.0%, Token F1 0.7788; GX đạt 3/5 checks, freshness vi phạm.
- Repaired: Hit@1 100.0%, Hit@4 100.0%, Token F1 1.0000; GX đạt 5/5 checks.
- Challenge set gồm 2 câu không có đáp án; tỷ lệ từ chối đúng: 100.0%.

Các số liệu QA trên được tạo bằng câu trả lời từ metadata. Mỗi trạng thái có 10/10 lượt judge dùng heuristic dự phòng; chưa có bằng chứng LLM judge hoặc Gemini evaluation thật trong artifact đang nộp.

## 2. Phân công cân bằng cho 5 thành viên

Mỗi người sở hữu một luồng chính, có đầu vào, đầu ra và minh chứng riêng. Mức 20% là phân bổ công việc đề xuất, chưa phải xác nhận đóng góp đã thực hiện. Tên và MSSV đã được điền theo danh sách nhóm cung cấp. Từng thành viên cần xác nhận phần việc thực tế trước khi nộp.

| Thành viên | Tên / MSSV | Tỷ trọng đề xuất | Luồng phụ trách | Deliverable và minh chứng |
| :--- | :--- | :---: | :--- | :--- |
| 1 | Văn Thành Huy / 2A20262763 | 20% | Ingestion, raw lineage và cleaning | src/ingestion/crossref.py, cleaning.py; data/raw/, data/clean/ |
| 2 | Võ Đức Tài / 2A202603007 | 20% | GX quality, Freshness SLA, golden evaluation và reporting | src/observability/quality.py, reporting.py, src/evaluation/; data/quality/, data/eval/, data/results/ |
| 3 | Phan Đình Bảo Khôi / 2A202602434 | 20% | Embedding, Chroma index và QA retrieval | src/retrieval/embeddings.py, index.py, qa.py, llm.py; data/chroma/, data/embeddings/ |
| 4 | Nguyễn Thùy Linh / 2A202602497 | 20% | Corruption suite và repair từ raw snapshot | src/ingestion/corruption.py, src/pipelines/corruption_flow.py; corruption_log.json, repaired artifacts |
| 5 | Nguyễn Thị Thùy Linh / 2A202602909 | 20% | Orchestration, dashboard và live demo | src/pipelines/phase1.py, script/, dashboard/; kiểm tra end-to-end và trình bày |

### Điểm bàn giao giữa các luồng

1. Huy bàn giao raw snapshot và clean schema cho Tài, Bảo Khôi và Nguyễn Thùy Linh.
2. Bảo Khôi bàn giao ba Chroma collections và API truy xuất cho Tài và Nguyễn Thị Thùy Linh.
3. Nguyễn Thùy Linh bàn giao corruption log và repaired artifacts cho Tài đánh giá.
4. Tài khóa golden set, quality/freshness reports và bảng metrics; Nguyễn Thị Thùy Linh dùng chính các artifact đó cho dashboard/demo.
5. Cả 5 người cùng rà bảng kết quả, lịch sử commit và báo cáo cá nhân trước khi nộp.

## 3. Kiến trúc và lineage

Crossref API khi bật refresh, hoặc data/raw/crossref_response.json khi chạy offline
→ parse thành data/raw/crossref_records.json
→ cleaning: bỏ JATS tags, chuẩn hóa khoảng trắng, khử trùng lặp DOI, tính age_days
→ data/clean/papers_clean.csv và papers_clean.json
→ MiniLM all-MiniLM-L6-v2 + ChromaDB
→ QA và golden evaluation
→ báo cáo baseline.

Corruption flow lấy dữ liệu sạch, tiêm 6 lỗi và đánh giá lại. Sau đó pipeline đọc raw snapshot, làm sạch, tái tạo collection repaired rồi chạy cùng golden set. Việc repair nằm trong luồng chạy thủ công; hiện chưa có cơ chế tự kích hoạt repair từ tín hiệu GX.

Bằng chứng nguồn: [raw response](../data/raw/crossref_response.json), [raw records](../data/raw/crossref_records.json), [clean dataset](../data/clean/papers_clean.json), [Chroma manifest](../data/embeddings/papers_embeddings.json).

## 4. Chất lượng dữ liệu

| Trạng thái | Số bản ghi | GX checks đạt | Freshness | Tỷ lệ quá hạn |
| :--- | ---: | ---: | :--- | ---: |
| Baseline | 24 | 5/5 | Đạt | 4.2% |
| Corrupted | 22 | 3/5 | Vi phạm | 50.0% |
| Repaired | 24 | 5/5 | Đạt | 4.2% |

SLA: tài liệu có age_days lớn hơn 180 được tính là quá hạn; cảnh báo khi tỷ lệ quá hạn vượt 25%. Snapshot hiện tại có ngày xuất bản mới nhất 2026-07-22 và cũ nhất 2026-03-28. GX kiểm tra số dòng, paper_id/title không null, DOI duy nhất và độ dài title.

Bằng chứng: [baseline quality](../data/quality/baseline_quality_report.json), [corrupted quality](../data/quality/corrupted_quality_report.json), [freshness](../data/quality/freshness_report.json).

## 5. Golden evaluation và tác động của corruption

Golden set cố định gồm 10 câu trên 10 DOI khác nhau, bao phủ summary (3), authors (3), date (2), categories (2). Hit@1 yêu cầu DOI đúng ở vị trí đầu; Hit@4 yêu cầu DOI đúng trong bốn kết quả đầu. Token F1 so sánh token giữa câu trả lời metadata và đáp án chuẩn. Bộ challenge 2 câu hỏi về tiêu đề không có trong corpus được chấm riêng.

| Metric | Baseline | Corrupted | Repaired |
| :--- | ---: | ---: | ---: |
| Hit@1 | 100.0% | 40.0% | 100.0% |
| Hit@4 | 100.0% | 60.0% | 100.0% |
| Mean Token F1 | 1.0000 | 0.7788 | 1.0000 |
| Heuristic Judge Accuracy | 100.0% | 80.0% | 100.0% |
| Mean Judge Score (1–5) | 5.00 | 4.00 | 5.00 |

Khi dữ liệu bị lỗi, Hit@1 giảm 60.0 điểm phần trăm và Hit@4 giảm 40.0 điểm phần trăm. Sau repair, hai chỉ số trở về mức baseline. Đây là bằng chứng về suy giảm retrieval và phục hồi trên snapshot hiện tại; không suy rộng thành độ chính xác ở corpus lớn hay câu trả lời LLM thật.

Sáu lỗi được ghi trong [corruption log](../data/results/corruption_log.json): drop latest records, blank summary, inject noise, truncate title, stale date và duplicate rows. Corrupted quality vi phạm 2/5 checks; Freshness SLA cũng vi phạm. [Bảng đối chiếu chi tiết](../data/reports/corruption_report.md) được sinh bởi pipeline.

## 6. RAG và giới hạn đánh giá

Baseline QA hiện trả lời tất định từ metadata của tài liệu top-1. Retrieval kết hợp Chroma dense search, đối sánh DOI/tiêu đề và rerank BM25. Câu trả lời LLM qua Gemini có script riêng ở script/run_llm_evaluation.py nhưng chưa có file kết quả thật. Ragas đang tắt trong metrics đã lưu. Vì vậy không gọi các giá trị heuristic judge là kết quả LLM judge.

Dashboard cục bộ trong dashboard/ trình bày ba trạng thái, GX/freshness và live retrieval. Live retrieval dùng metadata QA, không cần API key. Bộ dữ liệu 24 bài nhỏ và golden set đã dùng trong quá trình cải thiện retrieval; cần tập kiểm thử độc lập lớn hơn để đánh giá khả năng tổng quát.

## 7. Cách tái hiện

Cài dependencies theo requirements.txt hoặc pyproject.toml. Từ thư mục gốc dự án trên PowerShell, đặt PYTHONPATH=src, PYTHONIOENCODING=utf-8, LLM_PROVIDER=mock, RUN_RAGAS=0 và REFRESH_SOURCE=0; sau đó chạy script/run_phase1.py rồi script/run_corruption_flow.py bằng Python trong .venv. Hướng dẫn lệnh chi tiết nằm trong [README](../README.md).

Để trình chiếu, chạy script/run_dashboard.py và mở http://127.0.0.1:8765. Mỗi thành viên cần xác nhận việc chạy lại trên máy nộp bài và đối chiếu kết quả với [baseline metrics](../data/results/baseline_metrics.json), [corrupted metrics](../data/results/corrupted_metrics.json), [repaired metrics](../data/results/repaired_metrics.json).

## 8. Checklist trước khi nộp

- [x] Artifact raw, clean, Chroma, quality, metrics và hai báo cáo pipeline có trong repository.
- [x] Ba trạng thái dùng chung golden set cố định; số liệu bảng trên khớp artifact hiện tại.
- [x] Điền tên và MSSV của đủ 5 người, đồng bộ với docs/TEAM.md.
- [ ] Từng người xác nhận đóng góp thực tế và hoàn thiện báo cáo cá nhân.
- [ ] Chạy lại hai pipeline trên máy nộp bài, lưu log/ảnh minh chứng.
- [ ] Kiểm tra mỗi người có commit trên nhánh nộp bài và tự nộp link repository lên LMS.
- [ ] Chạy Gemini evaluation nếu thuyết trình kết quả LLM thật; tuyệt đối không commit .env hoặc API key.
