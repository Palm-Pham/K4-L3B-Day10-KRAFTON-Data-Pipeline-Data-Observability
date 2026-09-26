# K4-L3B-Day10 — Data Pipeline & Data Observability for RAG

> **Hình thức:** Teamwork | **Thời lượng:** 240 phút  
> **Lịch học (Lớp B - Ca Sáng):** Thứ 7 (26/09/2026) 09:00 – 13:00  
> ⏰ **Hạn nộp LMS:** 23:59:59 cùng ngày

---

## 🧭 Đọc gì, theo thứ tự nào?

| # | Tài liệu | Mô tả |
|:---:|---|---|
| 1️⃣ | **Codelab trên VLearn LMS** | Hướng dẫn từng bước + nộp bài (mở trên trình duyệt) |
| 2️⃣ | [CHECKPOINTS.md](docs/CHECKPOINTS.md) | Phân bổ thời gian 240 phút & deliverables từng mốc |
| 3️⃣ | [RUBRIC.md](docs/RUBRIC.md) | Tiêu chí chấm điểm (100 chuẩn + 10 bonus) |
| 4️⃣ | [SUBMISSION.md](docs/SUBMISSION.md) | Nội quy, deadline, bảo mật & checklist nộp bài |
| 5️⃣ | [TEAM.md](docs/TEAM.md) | Điền thông tin nhóm & báo cáo cá nhân |

---

## Repo có sẵn gì? (Scaffolded Baseline)

- `data/raw/` — Snapshot offline Crossref API (`crossref_response.json`)
- `src/` — Khung pipeline thu thập, embedding MiniLM, đánh giá metrics (có `TODO(student)`)
- `script/` — Entrypoints: `run_phase1.py`, `run_corruption_flow.py`

## Học viên cần làm gì?

1. Hoàn thiện **Data Quality Gate** (Great Expectations 1.x) trong `src/observability/quality.py`
2. Tích hợp **Freshness Check** (`age_days`) vào Quality Gate
3. Chạy **Baseline → Corruption → Repair** → xuất bảng đối chiếu 3 trạng thái
4. **Live Demo** trên bảng & nộp link repo lên VLearn LMS

## Chạy thử retrieval/RAG độc lập

Có thể chạy trước khi hoàn thiện hai pipeline tổng:

```powershell
.\.venv\Scripts\python.exe script\run_rag.py --rebuild
.\.venv\Scripts\python.exe script\run_rag.py --question "Who authored 'Data Observability and Quality Gates for Production RAG Systems'?" --top-k 2
```

Lệnh đầu dựng collection `papers-baseline` từ raw snapshot, các lần sau đọc lại index đã lưu. Thêm `--llm` để tạo câu trả lời từ ngữ cảnh truy xuất bằng provider cấu hình trong `.env`; chế độ mặc định trả lời theo metadata để có thể thử mà không cần API key.

## Đánh giá với golden dataset

`data/eval/test_set.json` có 10 câu hỏi cố định, đủ 4 dạng và bao phủ 10 bài báo. `data/eval/challenge_set.json` có 2 câu không có đáp án; Phase 1 chấm riêng và ghi `data/results/challenge_metrics.json`.

Chạy lại trên PowerShell từ thư mục dự án:

```powershell
$env:PYTHONPATH = "src"
$env:PYTHONIOENCODING = "utf-8"
$env:LLM_PROVIDER = "mock"
$env:RUN_RAGAS = "0"
$env:REFRESH_SOURCE = "0"
$env:REFRESH_TEST_SET = "1"
.\.venv\Scripts\python.exe script\run_phase1.py
$env:REFRESH_TEST_SET = "0"
.\.venv\Scripts\python.exe script\run_corruption_flow.py
```

`mock` chỉ kiểm tra luồng offline; cột `judge_fallback_count` trong metrics cho biết bao nhiêu câu được chấm bằng heuristic thay vì LLM.

### Gemini golden evaluation

Đặt `GOOGLE_API_KEY` trong `.env` của dự án và giữ `LLM_PROVIDER=gemini`.
Sau khi tạo baseline index và golden dataset, chạy:

```powershell
$env:PYTHONPATH = "src"
$env:PYTHONIOENCODING = "utf-8"
$env:RUN_RAGAS = "0"
.\.venv\Scripts\python.exe script/run_llm_evaluation.py
```

Kết quả câu trả lời do Gemini tạo nằm trong `data/results/llm_baseline_answers.json`;
metrics ở `data/results/llm_baseline_metrics.json`. Chỉ số judge ghi rõ số câu
được LLM chấm và số câu phải dùng heuristic dự phòng. Kết quả này không ghi đè
baseline metadata ở `baseline_*.json`.

## Dashboard thuyết trình cục bộ

Dashboard đọc trực tiếp các metrics, quality reports và corruption log đang có.
Chạy từ thư mục dự án bằng Python trong virtual environment:

```powershell
$env:PYTHONPATH = "src"
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python.exe script/run_dashboard.py
```

Mở [http://127.0.0.1:8765](http://127.0.0.1:8765). Phần Live retrieval
dùng QA metadata trên ba Chroma collections và hoạt động không cần API key.
Để có số liệu mới trước khi thuyết trình, chạy lại Phase 1 và corruption flow
theo lệnh phía trên rồi tải lại trang. Dashboard chỉ nghe trên localhost.
