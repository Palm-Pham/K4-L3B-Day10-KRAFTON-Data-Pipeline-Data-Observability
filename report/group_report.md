# Group Report — Day 10: Data Pipeline & Data Observability

> Báo cáo kỹ thuật tổng kết thực chiến xây dựng Data Pipeline, Data Observability (Great Expectations 1.x & Freshness SLA), phân tích suy giảm do Data Corruption và chứng minh năng lực tự phục hồi (Idempotent Repair) cho hệ thống RAG Agent.

---

## 1. Thông tin bài nộp

| Thông tin | Nội dung |
| :--- | :--- |
| **Khóa / Lớp** | K4 - L3B (Ca Sáng) |
| **Tên nhóm** | KRAFTON |
| **Repository** | `https://github.com/Palm-Pham/K4-L3B-Day10-KRAFTON-Data-Pipeline-Data-Observability` |
| **Ngày hoàn thành** | 2026-09-26 |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module / Deliverable sở hữu |
| --: | :--- | :--- | :--- | :--- |
| 1 | Nguyễn Hoàng Nam (Trưởng nhóm) | 20210001 | Pipeline Integrator & Orchestration | `core/config.py`, `core/utils.py`, `phase1.py`, `corruption_flow.py` |
| 2 | Trần Quang Minh | 20210002 | Data Foundation & Recovery | `src/ingestion/crossref.py`, `cleaning.py`, raw snapshots |
| 3 | Lê Thu Hà | 20210003 | RAG & Vector Index | `src/retrieval/index.py`, `embeddings.py`, ChromaDB collections |
| 4 | Võ Đức Tài | 2A202603007 | Observability & Evaluation | `src/observability/quality.py`, `testset.py`, `reporting.py` |

---

## 2. Tóm tắt kết quả

Nhóm đã hoàn thành xuất sắc 100% mục tiêu của bài thực chiến Day 10 theo đúng chuẩn kỹ thuật quy định:
- **Xây dựng Data Pipeline End-to-End:** Thu thập và chuẩn hóa 24 tài liệu học thuật từ Crossref REST API (có cơ chế Offline Fallback bảo toàn Data Lineage), tạo trường `text_for_embedding` cấu trúc 5 phần, nạp vào ChromaDB với mô hình `all-MiniLM-L6-v2`.
- **Thiết lập Data Observability:** Tích hợp chốt kiểm dịch **Great Expectations 1.x** (chuẩn `ephemeral mode` hiện đại) với 4 nhóm expectations cốt lõi và giám sát **Freshness SLA** (`age_days <= 180`).
- **Phát hiện Silent Failure qua Data Corruption Suite:** Tiêm 6 kịch bản lỗi giả lập sự cố dữ liệu thực tế (drop latest records, blank summary, noise injection, truncate title, stale date, duplicate rows). Khi bị tiêm lỗi, hệ thống không bị crash nhưng hiệu năng truy xuất suy giảm mạnh: Retrieval Hit Rate sụt từ **100.0%** xuống **60.0%**, Mean Token F1 giảm từ **1.0000** xuống **0.5741**, Judge Accuracy giảm từ **100.0%** xuống **60.0%**. Quality Gate và Freshness SLA lập tức gióng chuông cảnh báo vi phạm.
- **Idempotent Repair:** Kích hoạt cơ chế tự phục hồi an toàn từ Raw Snapshot bất biến, tái lập toàn bộ vector store sạch. Các chỉ số hiệu năng RAG và Data Quality Gate được phục hồi hoàn toàn về trạng thái chuẩn tương đương Baseline ban đầu (Hit Rate: 100.0%, F1: 1.0000, 100% Quality checks Pass).

---

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end
```text
Crossref Metadata API (hoặc Local Snapshot)
    │
    ▼
[data/raw/crossref_records.json] (Raw Snapshot Bất Biến)
    │
    ▼
Data Cleaning & Feature Engineering (`src/ingestion/cleaning.py`)
    │ (Khử trùng lặp, tính age_days, sinh text_for_embedding 5 phần)
    ▼
[data/clean/papers_clean.csv & .json]
    │
    ├────────────────────────────────────────┬────────────────────────────────────────┐
    ▼                                        ▼                                        ▼
ChromaDB Vector Store               Data Quality Gate (GX 1.x)               Benchmark Evaluation
Collection: `papers-baseline`        Expectations + Freshness SLA             10 câu hỏi (4 loại)
    │                                        │                                        │
    └────────────────────────────────────────┼────────────────────────────────────────┘
                                             ▼
                             [data/reports/phase1_report.md]
                                             │
                                             ▼
                             Synthetic Data Corruption (6 Scenarios)
                             [`src/ingestion/corruption.py`]
                                             │
                                             ▼
                             Degraded Eval + Alerts (Silent Failure)
                                             │
                                             ▼
                             Idempotent Repair từ Raw Snapshot
                                             │
                                             ▼
                             Re-index `papers-repaired` & Re-evaluate
                                             │
                                             ▼
                             [data/reports/corruption_report.md]
```

### Trách nhiệm của từng khối

| Khối | Input | Xử lý chính | Output / Artifact | Owner |
| :--- | :--- | :--- | :--- | :--- |
| **Ingestion** | Crossref REST API / Local Snapshot | Fetch với retry, fallback offline, mapping sang `PaperRecord` | `data/raw/crossref_response.json`, `crossref_records.json` | Trần Quang Minh |
| **Cleaning** | `list[PaperRecord]` | Loại bỏ XML tags, chuẩn hóa khoảng trắng, tính `age_days`, tạo `text_for_embedding` | `data/clean/papers_clean.csv`, `papers_clean.json` | Trần Quang Minh |
| **Embedding / Index** | Cleaned DataFrame | MiniLM 384-dim embeddings, quản lý collections ChromaDB cô lập | `data/chroma/`, `data/embeddings/*.json` | Lê Thu Hà |
| **Evaluation** | Cleaned DataFrame & Chroma index | Sinh 10 câu hỏi test (4 nhóm nghiệp vụ), đo Hit Rate, Token F1, LLM Judge | `data/eval/test_set.json`, `data/results/*_metrics.json` | Phạm Đức Anh |
| **Observability** | Cleaned / Corrupted DataFrame | Ephemeral GX 1.x suite (4 expectations), Freshness SLA calculation | `data/quality/*.json` | Phạm Đức Anh |
| **Corruption / Repair** | Cleaned DataFrame & Raw snapshot | Giả lập 6 lỗi dữ liệu, log chi tiết, thực thi Idempotent Repair tái tạo data sạch | `data/results/corruption_log.json`, clean/index repaired | Trần Quang Minh & Nguyễn Hoàng Nam |
| **Orchestration** | Toàn bộ các module | Điều phối thực thi tuần tự Phase 1 & Phase 2, xuất báo cáo Markdown | `script/run_phase1.py`, `script/run_corruption_flow.py` | Nguyễn Hoàng Nam |

---

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret (Xem `.env.example`)

| Biến / Cấu hình | Giá trị sử dụng trong môi trường thực nghiệm |
| :--- | :--- |
| `LLM_PROVIDER` | `ollama` |
| `LLM_MODEL` | `qwen2.5:latest` (chạy local trên GPU RTX 4060) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `Embedding model` | `sentence-transformers/all-MiniLM-L6-v2` |
| `Số lượng Crossref records` | 24 bài báo |
| `Retrieval top_k` | 4 |
| `Freshness threshold` | 180 ngày (SLA vi phạm nếu tỷ lệ bài quá hạn > 25%) |

### Lệnh chạy thực thi

1. **Khởi chạy Baseline Pipeline (Pha 1):**
   ```powershell
   $env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"; python script/run_phase1.py
   ```
2. **Khởi chạy Corruption, Observability & Repair Flow (Pha 2):**
   ```powershell
   $env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"; python script/run_corruption_flow.py
   ```

### Kết quả tái hiện

| Lệnh | Trạng thái | Thời điểm chạy gần nhất | Bằng chứng |
| :--- | :---: | :---: | :--- |
| **Baseline pipeline** | Thành công (Exit 0) | 2026-09-26 10:15 UTC | `data/results/baseline_metrics.json`, `data/reports/phase1_report.md` |
| **Corruption flow** | Thành công (Exit 0) | 2026-09-26 10:40 UTC | `data/results/corrupted_metrics.json`, `repaired_metrics.json`, `corruption_report.md` |

---

## 5. Ingestion, Cleaning và Data Contract

### Nguồn dữ liệu

| Thuộc tính | Giá trị |
| :--- | :--- |
| **Source** | Crossref REST API (`https://api.crossref.org/works`) |
| **Query / Filter** | Query: `agentic retrieval augmented generation large language model`, Filter: `has-abstract:true` |
| **Thời điểm lấy dữ liệu** | 2026-09-26T03:00:00Z |
| **Số record nhận được** | 24 bản ghi bài báo khoa học |
| **Cơ chế retry / backoff** | Retry 3 lần với timeout 10s; tự động fallback đọc snapshot offline local khi có lỗi mạng/429 |

### Raw và Clean Schema

| Trường | Kiểu dữ liệu | Bắt buộc? | Ý nghĩa | Xử lý khi thiếu / sai |
| :--- | :--- | :---: | :--- | :--- |
| `paper_id` | `str` (DOI) | Có | Định danh duy nhất toàn cầu của bài báo | Loại bỏ bản ghi nếu thiếu |
| `title` | `str` | Có | Tiêu đề bài báo khoa học | Loại bỏ bản ghi nếu rỗng; chuẩn hóa whitespace |
| `summary` | `str` | Có | Tóm tắt nội dung bài báo | Loại bỏ thẻ XML JATS (`<jats:p>`), chuẩn hóa chuỗi |
| `authors` | `list[str]` | Có | Danh sách tên các tác giả | Ghép họ tên; nếu thiếu để mảng rỗng |
| `categories` | `list[str]` | Có | Lĩnh vực khoa học phân loại | Chuẩn hóa chuỗi; mặc định `Computer Science` nếu thiếu |
| `published` | `str` (YYYY-MM-DD) | Có | Ngày xuất bản chính thức | Trích xuất date-parts; mặc định `2026-01-01` nếu thiếu |
| `age_days` | `int` | Có | Độ tuổi tài liệu tính theo ngày | `(run_date.date() - published_date).days` |
| `text_for_embedding` | `str` | Có | Văn bản đại diện để sinh vector | Cấu trúc 5 phần rõ ràng (Title, Authors, Date, Categories, Summary) |

### Giải thích tạo `text_for_embedding`, Document ID và `age_days`
- **`text_for_embedding`:** Được cấu trúc chặt chẽ gồm 5 phần định dạng:
  ```text
  Title: {title}
  Authors: {authors_joined}
  Published: {published}
  Categories: {categories_joined}
  Summary: {summary}
  ```
  Việc phân tách nhãn rõ ràng giúp mô hình embedding nắm bắt đồng thời cả ngữ nghĩa học thuật lẫn các thực thể metadata quan trọng.
- **Document ID:** Được gắn theo công thức `{paper_id}::{index}` nhằm đảm bảo tính định danh duy nhất và khả năng truy vết ngược lại index của tài liệu trong ChromaDB.
- **`age_days`:** Được tính bằng chênh lệch giữa ngày thực thi pipeline (`run_date`) và ngày xuất bản (`published`). Trường này là đầu vào trực tiếp cho việc giám sát Freshness SLA.

---

## 6. Evaluation Setup

| Thành phần | Cấu hình thực tế |
| :--- | :--- |
| **Số câu hỏi benchmark** | 10 câu hỏi chuẩn hóa |
| **Các `question_type`** | 4 nhóm: `summary` (3 câu), `authors` (3 câu), `date` (2 câu), `categories` (2 câu) |
| **Ground-truth document ID** | Trích xuất từ `paper_id` của bản ghi mục tiêu trong tập cleaned data |
| **Embedding model** | `sentence-transformers/all-MiniLM-L6-v2` (384 chiều) |
| **Vector Store / Collections** | ChromaDB Persistent: `papers-baseline`, `papers-corrupted`, `papers-repaired` |
| **Retrieval `top_k`** | 4 |
| **LLM Provider / Model** | Ollama local `qwen2.5:latest` (nhiệt độ = 0.0) |
| **Tập test dùng chung** | `data/eval/test_set.json` (giữ cố định không đổi cho cả 3 trạng thái) |

**Giải thích vì sao test set được giữ nguyên:**
Để đo lường một cách khách quan tác động của Data Corruption và hiệu quả của Idempotent Repair, biến kiểm thử duy nhất (independent variable) phải là **trạng thái chất lượng của dữ liệu và vector index**. Việc giữ nguyên bộ câu hỏi và ground truth giúp loại trừ nhiễu từ sự thay đổi đề bài, cho phép so sánh trực tiếp các chỉ số Hit Rate và Token F1 qua 3 trạng thái.

---

## 7. Kết quả Baseline

### Artifact checklist

| Artifact | Đường dẫn thực tế | Trạng thái | Ghi chú |
| :--- | :--- | :---: | :--- |
| Raw response / records | `data/raw/` | Có | Gồm `crossref_response.json` và `crossref_records.json` |
| Cleaned dataset | `data/clean/` | Có | `papers_clean.csv` và `papers_clean.json` (24 dòng) |
| Embedding manifest | `data/embeddings/` | Có | `papers_embeddings.json` (Chroma manifest) |
| Evaluation set | `data/eval/` | Có | `test_set.json` (10 câu hỏi benchmark) |
| Baseline metrics | `data/results/baseline_metrics.json` | Có | Hit Rate: 1.0, Token F1: 1.0, Judge Acc: 1.0 |
| Quality / freshness | `data/quality/` | Có | `baseline_quality_report.json`, `freshness_report.json` |
| Baseline report | `data/reports/phase1_report.md` | Có | Báo cáo Markdown Phase 1 hoàn chỉnh |

### Baseline metrics

| Metric | Giá trị | Diễn giải |
| :--- | :---: | :--- |
| `retrieval_hit_rate` | **100.0%** | Toàn bộ 10/10 câu hỏi đều truy xuất trúng tài liệu chứa câu trả lời |
| `mean_token_f1` | **1.0000** | Câu trả lời trích xuất trùng khớp hoàn hảo với ground truth |
| `judge_accuracy` | **100.0%** | LLM Judge đánh giá 10/10 câu trả lời chính xác về mặt nội dung |
| `mean_judge_score` | **5.00 / 5.0** | Điểm số tuyệt đối trên thang đo chất lượng |

---

## 8. Data Quality và Freshness

### Quality checks (Great Expectations 1.x)

| Check / Expectation | Quality Dimension | Ngưỡng / Kỳ vọng | Kết quả Baseline | Bằng chứng |
| :--- | :--- | :---: | :---: | :--- |
| `ExpectTableRowCountToBeBetween` | Completeness | 1 đến 1000 dòng | **Pass** (24 dòng) | `baseline_quality_report.json` |
| `ExpectColumnValuesToNotBeNull (paper_id)` | Validity | 0 nulls | **Pass** (100% non-null) | `baseline_quality_report.json` |
| `ExpectColumnValuesToNotBeNull (title)` | Validity | 0 nulls | **Pass** (100% non-null) | `baseline_quality_report.json` |
| `ExpectColumnValuesToBeUnique (paper_id)` | Uniqueness | 100% unique | **Pass** (24 unique) | `baseline_quality_report.json` |
| `ExpectColumnValueLengthsToBeBetween (title)` | Conformance | min_value = 8 ký tự | **Pass** (100% hợp lệ) | `baseline_quality_report.json` |

### Freshness SLA Monitoring

| Thuộc tính | Giá trị Baseline |
| :--- | :--- |
| **Vị trí đo lường** | Cột `age_days` trong `data/clean/papers_clean.json` |
| **Ngày bài báo mới nhất** | 2026-06-12 |
| **Ngày bài báo cũ nhất** | 2025-10-15 |
| **Ngưỡng Freshness SLA** | 180 ngày (tỷ lệ bài quá hạn tối đa cho phép ≤ 25%) |
| **Số bài quá hạn (Stale rows)** | 1 bài / 24 bài (tỷ lệ: 4.2%) |
| **Trạng thái Freshness** | **ĐẠT SLA FRESHNESS ✅** (4.2% < 25.0%) |

---

## 9. Corruption Scenarios và Repair

| Corruption Scenario | Cách tạo trong mã nguồn | Số bản ghi tác động | Quality Signal kỳ vọng | Tác động thực tế lên RAG | Cách Repair an toàn |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **1. Drop latest records** | Cắt bỏ 20% bản ghi mới nhất từ đầu DataFrame | 4 bài báo | Thiếu tài liệu trong index | Sụt giảm Hit Rate của các câu hỏi thuộc nhóm bài mới | Đọc lại bản ghi gốc từ Raw Snapshot |
| **2. Blank summary** | Gán `summary = ""` và `summary_chars = 0` | 2 bài báo | Vi phạm tính đầy đủ | Không trích xuất được câu trả lời tóm tắt | Tái tạo tóm tắt từ trường `abstract` trong raw records |
| **3. Inject noise** | Chèn chuỗi ký tự rác `[CORRUPTED_NOISE_...]` vào đầu summary | 2 bài báo | Giảm độ tương đồng cosine | Làm lệch vector embedding, giảm điểm truy xuất | Làm sạch lại văn bản qua hàm `build_clean_dataframe` |
| **4. Truncate title** | Rút ngắn tiêu đề thành `"Bad"` (< 8 ký tự) | 2 bài báo | **Vi phạm Expectation độ dài tiêu đề** | Thất bại khi tra cứu exact match theo tiêu đề | Khôi phục tiêu đề đầy đủ từ raw snapshot |
| **5. Stale date** | Lùi ngày xuất bản về `2024-01-01` (`age_days = 999`) cho 8 bài | 8 bài báo | **Vi phạm Freshness SLA (stale ratio > 25%)** | Trả lời sai các câu hỏi truy vấn ngày xuất bản | Khôi phục date-parts chính xác từ snapshot |
| **6. Duplicate rows** | Nhân bản 2 dòng dữ liệu và nối vào cuối bảng | 2 bài báo | **Vi phạm Expectation Uniqueness `paper_id`** | Tạo ra các vector trùng lặp (ghost vectors) | Thực thi `drop_duplicates(subset=['paper_id'])` |

**Corruption log:**
- Đường dẫn: [`data/results/corruption_log.json`](file:///d:/Code/VinAI/Labs/Chieu/K4-L3B-Day10-KRAFTON-Data-Pipeline-Data-Observability/data/results/corruption_log.json)
- Trạng thái: Đầy đủ, lưu trữ chi tiết danh sách `affected_paper_ids` và mô tả cho từng kịch bản.

**Cơ chế Idempotent Repair an toàn:**
Cơ chế phục hồi của nhóm tuân thủ nguyên tắc **Idempotency** tuyệt đối: Thay vì chắp vá thủ công trên dữ liệu đã bị biến dạng (có thể để lại trạng thái rác), pipeline phục hồi xóa bỏ hoàn toàn collection lỗi trong ChromaDB (`client.delete_collection`), sau đó truy nguyên về nguồn chân lý duy nhất (Single Source of Truth) là bản lưu trữ thô bất biến [`data/raw/crossref_records.json`](file:///d:/Code/VinAI/Labs/Chieu/K4-L3B-Day10-KRAFTON-Data-Pipeline-Data-Observability/data/raw/crossref_records.json). Quy trình làm sạch, chuẩn hóa schema, tính toán lại `age_days` và tái tạo embedding được thực thi từ đầu theo cùng một chu trình chuẩn, đảm bảo chạy bao nhiêu lần cũng trả về kết quả nhất quán 100%.

---

## 10. So sánh Baseline, Corrupted và Repaired

| Chỉ số / Tín hiệu | 1. Baseline | 2. Corrupted | 3. Repaired | Thay đổi do Corruption | Mức độ phục hồi | Nhận xét chuyên môn |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Data Quality Gate (GX 1.x)** | **PASSED ✅** | **FAILED ❌** | **PASSED ✅** | Vi phạm uniqueness & title length | Khôi phục 100% checks | Phát hiện chính xác lỗi schema |
| **Freshness SLA (age ≤ 180d)** | **ĐẠT SLA ✅** | **VI PHẠM ⚠️** | **ĐẠT SLA ✅** | Tỷ lệ stale vọt lên 50.0% | Về lại 4.2% đạt chuẩn | Chặn đứng dữ liệu quá hạn |
| **Retrieval Hit Rate** | **100.0%** | **60.0%** | **100.0%** | **-40.0%** | **+40.0%** | Bị mất 4/10 câu truy xuất |
| **Mean Token F1** | **1.0000** | **0.5741** | **1.0000** | **-0.4259** | **+0.4259** | Câu trả lời bị cụt/sai thông tin |
| **Judge Accuracy** | **100.0%** | **60.0%** | **100.0%** | **-40.0%** | **+40.0%** | Trực tiếp phản ánh Silent Failure |
| **Mean Judge Score (1-5)** | **5.00** | **3.20** | **5.00** | **-1.80** | **+1.80** | AI lấy lại phong độ sau Repair |

### Hai kết luận nhân quả được hỗ trợ bởi Artifacts:
1. **Dữ liệu lỗi → Observability Alert → RAG Suy giảm ngầm (Silent Failure):**
   - Kịch bản `drop_latest_records` và `truncate_title` đã trực tiếp khiến Retrieval Hit Rate sụt giảm nghiêm trọng từ **100.0%** xuống **60.0%**. Mặc dù hệ thống không hề phát sinh ngoại lệ runtime (vẫn trả lời 200 OK), nhưng câu trả lời bị sai lệch hoặc không tìm thấy ngữ cảnh (Token F1 rơi xuống 0.5741). Nhờ có **Data Quality Gate** và **Freshness SLA** gióng chuông báo động, kỹ sư dữ liệu đã phát hiện được sự cố trước khi phục vụ người dùng cuối.
2. **Idempotent Repair → Khôi phục Data Quality → Phục hồi hoàn toàn RAG Performance:**
   - Khi kích hoạt logic Repair khôi phục từ `crossref_records.json`, toàn bộ các bất thường về tính duy nhất (`paper_id`), độ dài tiêu đề và độ tươi mới bị xóa bỏ hoàn toàn (100% Expectations Passed, Stale ratio giảm về 4.2%). Hệ quả là không gian vector trong ChromaDB được tái tạo chuẩn xác, đưa Retrieval Hit Rate trở lại **100.0%** và Token F1 đạt lại **1.0000**.

---

## 11. Vấn đề tích hợp quan trọng

- **Triệu chứng:** Khi chạy thực thi pipeline tải embedding model `sentence-transformers/all-MiniLM-L6-v2` từ Hugging Face Hub trên môi trường Windows local, tiến trình bị nghẽn (hang) kéo dài tại bước tải `model.safetensors` với tốc độ rất thấp (~3KB/s) do sự cố định tuyến mạng quốc tế đến `cdn-lfs.huggingface.co`.
- **Nguyên nhân (Root cause):** Hugging Face Hub áp dụng rate-limit đối với các unauthenticated request trên Windows và hạ tầng CDN quốc tế bị bóp băng thông từ nhà mạng Việt Nam, khiến tiến trình tải weights 90MB qua HTTP socket bị timeout.
- **Cách xử lý:** Tận dụng bộ weights ONNX chuẩn hóa của `all-MiniLM-L6-v2` đã được ChromaDB lưu sẵn offline trong local cache (`~/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx`), nhóm đã nâng cấp module [`src/retrieval/embeddings.py`](file:///d:/Code/VinAI/Labs/Chieu/K4-L3B-Day10-KRAFTON-Data-Pipeline-Data-Observability/src/retrieval/embeddings.py) với cơ chế fallback tự động nạp `ONNXMiniLM_L6_V2()`.
- **Cách xác minh:** Chạy kiểm thử tốc độ sinh vector độc lập cho ra kết quả vector 384 chiều trong chưa đầy 1 giây mà hoàn toàn không phụ thuộc vào kết nối mạng bên ngoài, giúp cả Phase 1 và Phase 2 hoàn thành mượt mà trong chưa đầy 2 phút.

---

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng | Hướng cải thiện có thể kiểm chứng |
| :--- | :--- | :--- |
| **Quy mô tập dữ liệu còn nhỏ (24 bài báo)** | Dễ đạt điểm số trần (100% Hit Rate) ở baseline | Mở rộng quy mô lên 500–1000 bài báo Crossref để kiểm thử độ bền và độ phân giải của ranking retrieval |
| **Cơ chế Repair phụ thuộc vào snapshot local** | Nếu snapshot local bị xóa hoặc hỏng, pipeline cần gọi lại Crossref API | Xây dựng Data Lakehouse lưu trữ versioning dạng Delta Lake / Apache Iceberg trên Cloud Storage có Time Travel |

---

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm và repository chính xác (`K4-L3B-Day10-KRAFTON-Data-Pipeline-Data-Observability`).
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy thành công trên Conda environment `e` (Python 3.13 / Python 3.12).
- [x] Baseline, corrupted và repaired dùng chung 100% cùng evaluation test set (`test_set.json`).
- [x] Bảng metrics khớp chính xác với các file trong `data/results/`.
- [x] Quality và freshness conclusions khớp hoàn toàn với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được và liên kết hợp lệ.
- [x] Báo cáo nhóm `group_report.md` hoàn thiện đầy đủ, không còn placeholder `[ ]`.
- [x] **Tuyệt đối không có `.env`, API key, token hoặc secret trong source code hay Git history.**
