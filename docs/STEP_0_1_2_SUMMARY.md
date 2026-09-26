# Báo cáo thực hiện lab: bước 0, 1 và 2

Ngày kiểm chứng: **2026-09-26**. Báo cáo này ghi lại phần việc đã thực hiện và kiểm chứng trong bộ nhớ; chưa chạy pipeline end-to-end.

## Bước 0 — Khảo sát, không sửa file

- Đọc `README.md`, toàn bộ `docs/`, các module ingestion, observability, evaluation, retrieval index, cấu hình và pipeline liên quan.
- `data/raw/crossref_response.json` có **24** Crossref items; `data/raw/crossref_records.json` có **24** records với **24 DOI duy nhất**. Hai snapshot có cùng tập DOI. Cả 24 abstract trong API payload có thẻ JATS.
- `PaperRecord` gồm 11 trường: `paper_id`, `title`, `summary`, `authors`, `categories`, `primary_category`, `published`, `updated`, `abs_url`, `pdf_url`, `comment`.
- `src/retrieval/index.py` cần `paper_id`, `title`, `text_for_embedding` và metadata `published`, `authors_joined`, `categories_joined`, `summary`, `abs_url`, `pdf_url` từ bảng sạch.
- Lúc bắt đầu, hai file của bước 1 đã có thay đổi chưa commit; hai file của bước 2 vẫn là `TODO(student)`.

## Bước 1 — Ingestion và cleaning

| File và hàm | Công việc |
| --- | --- |
| [`crossref.py`](../src/ingestion/crossref.py): `parse_crossref_payload` | Chuyển Crossref items thành `PaperRecord`; lấy DOI, tiêu đề, abstract, tác giả, chủ đề, ngày và URL; bỏ item thiếu dữ liệu bắt buộc. Logic này đã có trong working tree khi bắt đầu và được kiểm chứng. |
| `crossref.py`: `load_raw_records` | Đọc được cả snapshot API dạng object và snapshot records dạng array. Logic đã có và được kiểm chứng. |
| `crossref.py`: `fetch_source_records` | Dùng snapshot khi không yêu cầu refresh; khi refresh, thử Crossref API và fallback về snapshot nếu lỗi mạng hoặc HTTP 429/503. Nhánh thành công có logic ghi hai raw JSON. Logic đã có; các nhánh được kiểm chứng bằng mock, không ghi file. |
| `crossref.py`: `_plain_text`, `_crossref_date` | Sửa trong lượt này: giải mã HTML trước khi loại JATS tag; kiểm tra `date-time` hợp lệ trước khi nhận ngày. Ngày Crossref chỉ có năm/tháng được quy về ngày đầu năm/tháng. |
| [`cleaning.py`](../src/ingestion/cleaning.py): `build_clean_dataframe` | Chuẩn hóa DOI và văn bản, loại record thiếu DOI/tiêu đề/summary/ngày, bỏ DOI trùng, tính `age_days`, tạo `authors_joined`, `categories_joined`, `summary_chars` và `text_for_embedding` gồm 5 phần: title, summary, authors, published, categories. Logic đã có trong working tree và được kiểm chứng. |
| `cleaning.py`: `_clean_text`, `_date` | Sửa trong lượt này: loại được cả JATS tag mã hóa HTML; xem `NaT` là ngày không hợp lệ. |

**Kiểm chứng:** API snapshot parse 24/24; records snapshot đọc 24/24; bảng sạch có **24 dòng**, **0 dòng bị loại** từ snapshot hiện có và đủ cột index cần. Không còn JATS tag trong summary. Phép thử biên 3 records cho 1 dòng đầu ra: loại 1 DOI trùng và 1 ngày sai. Mock API thành công cho 24 records; mock lỗi mạng và HTTP 429 đều fallback về 24 records (429 thử 3 lần).

| Mẫu bảng sạch | `published` | `age_days` |
| --- | --- | ---: |
| Continuous Benchmark Evaluation for Enterprise Retrieval Pipelines | 2026-07-22 | 66 |
| Multi-Agent Consensus for High-Stakes Fact Verification | 2026-07-19 | 69 |
| Freshness SLAs for Real-Time LLM Knowledge Augmentation | 2026-07-05 | 83 |

## Bước 2 — Quality gate và test set

| File và hàm | Công việc |
| --- | --- |
| [`quality.py`](../src/observability/quality.py): `_freshness_metrics` | Tính số dòng quá hạn theo `age_days > 180`, tỷ lệ quá hạn, ngày xuất bản mới nhất/cũ nhất và số tuổi bài báo không hợp lệ. `is_fresh=False` khi tỷ lệ quá hạn **vượt** 25%, dữ liệu tuổi không hợp lệ hoặc bảng rỗng. |
| `quality.py`: `run_data_quality_checks` | Dùng Great Expectations 1.x với ephemeral context và pandas batch. Suite có 7 checks thuộc 4 loại: row count, not null, unique và độ dài chuỗi. `success` kết hợp kết quả GX với Freshness SLA. `report_name=None` trả kết quả trong bộ nhớ; khi có tên mới ghi quality report. |
| `quality.py`: `build_freshness_report` | Trả Freshness payload; `report_path=None` không ghi file, còn đường dẫn được truyền vào sẽ ghi JSON. |
| [`testset.py`](../src/evaluation/testset.py): `build_test_set` | Chọn 10 tài liệu đầy đủ, khác DOI và rải đều theo thứ tự ngày xuất bản. Tạo 10 câu hỏi thuộc `summary`, `authors`, `date`, `categories`; mỗi câu có `id`, `question`, `ground_truth`, `ground_truth_doc_ids`. `output_path=None` chỉ trả dữ liệu trong bộ nhớ. |

**Kiểm chứng:** Great Expectations **1.23.2** chạy 7 checks trên 24 dòng sạch và trả `success=True`. Freshness có **1/24** bài quá hạn (**4,17%**). Bộ test có **10** câu: 3 `summary`, 3 `authors`, 2 `date`, 2 `categories`; 10 ID câu hỏi và 10 DOI nguồn đều duy nhất. Phép thử dữ liệu lỗi trả `success=False`: GX phát hiện DOI trùng, title ngắn, summary rỗng; Freshness phát cảnh báo khi **8/24** bài quá hạn (**33,33%**). Kết quả quality có thể serialize thành JSON trong bộ nhớ.

## Giả định và giới hạn kiểm chứng

- Row count kỳ vọng bằng `settings.max_results` (**24**). Title tối thiểu **8** ký tự vì kịch bản corruption của lab cắt title xuống dưới 8; summary tối thiểu **1** ký tự để bắt chuỗi rỗng. Tài liệu không quy định các ngưỡng độ dài cụ thể hơn.
- `ground_truth` cho câu `summary` là câu đầu tiên của summary, phù hợp cách trả lời hiện có trong `src/retrieval/qa.py`.
- Không gọi API thật, không lưu hoặc ghi đè raw JSON, không tạo cleaned data, quality report, test set hay ChromaDB artifacts. Chưa kiểm chứng ghi file, indexing và pipeline end-to-end.
- Để kiểm chứng artifact ở lượt sau cần được cho phép tạo: `data/clean/papers_clean.csv`, `data/clean/papers_clean.json`, `data/quality/baseline_quality_report.json`, `data/quality/freshness_report.json`, `data/eval/test_set.json`; nếu chạy indexing còn có `data/embeddings/papers_embeddings.json` và các file do Chroma sinh dưới `data/chroma/`. Nhánh API thật có thể ghi đè hai raw JSON hiện có.

Trong lượt thực hiện bước 0–2, chỉ bốn file mã nguồn nêu trên được sửa. File báo cáo này được tạo theo yêu cầu tiếp theo của người dùng.
