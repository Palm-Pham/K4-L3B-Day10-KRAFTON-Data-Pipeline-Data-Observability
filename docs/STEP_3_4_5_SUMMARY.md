# Báo cáo thực hiện lab: bước 3, 4 và 5

Ngày kiểm chứng: **2026-09-26**. Các số liệu dưới đây đọc từ artifact do pipeline tạo; không chỉnh sửa metrics hoặc báo cáo bằng tay. Bước 0–2 được ghi riêng tại [STEP_0_1_2_SUMMARY.md](STEP_0_1_2_SUMMARY.md).

## Mã nguồn đã chỉnh sửa

| Bước | File và hàm | Thay đổi |
| --- | --- | --- |
| 3 | [`src/pipelines/phase1.py`](../src/pipelines/phase1.py): `main` | Nối raw snapshot tại chỗ → cleaning → quality/freshness → test set → collection `papers-baseline` → evaluation → báo cáo. Chỉ cho phép `LLM_PROVIDER=mock`; kiểm tra đầu ra tồn tại để tránh ghi đè. Mọi artifact lấy từ cùng DataFrame sạch và cùng test set. |
| 3 | [`src/observability/reporting.py`](../src/observability/reporting.py): `generate_phase1_report` | Xuất nguồn, số records, collection, metrics, GX và Freshness từ kết quả thực; từ chối ghi đè báo cáo. |
| 4 | [`src/ingestion/corruption.py`](../src/ingestion/corruption.py): `_embedding_text`, `corrupt_clean_dataframe` | Làm lỗi trên bản sao DataFrame, chọn DOI xác định, ghi trước/sau trong log, cập nhật `summary_chars` và dựng lại `text_for_embedding`. Có thể kiểm chứng với log trong `DataFrame.attrs` mà không tạo file. |
| 5 | [`src/pipelines/corruption_flow.py`](../src/pipelines/corruption_flow.py): `main` | Dùng lại đúng `data/eval/test_set.json`; đánh giá corrupted dù quality fail; repair hai lần từ raw snapshot với ngày chạy baseline, đối chiếu nội dung với clean baseline; đánh giá repaired và lặp lại truy vấn để kiểm tra nhất quán. Hai collection mới được tạo trong `data/chroma/comparison/`, không sửa DB baseline. |
| 5 | `src/observability/reporting.py`: `generate_corruption_report` | Lập bảng Baseline / Corrupted / Repaired trực tiếp từ ba bộ metrics, quality và freshness; nêu từng expectation vi phạm và giới hạn của benchmark DOI. |

Không sửa module index, evaluation, test set, quality hay raw snapshot trong bước 3–5. Không commit, push, cài dependency hoặc gọi Crossref/API trả phí.

## Bước 3 — Baseline

`script/run_phase1.py` chạy **exit code 0** với `LLM_PROVIDER=mock`, `RUN_RAGAS=0` và raw snapshot có sẵn. Đầu vào **24** records, clean **24**, loại **0**. Collection `papers-baseline` có **24** tài liệu; test set có **10** câu.

| Chỉ số | Baseline |
| --- | ---: |
| Retrieval Hit Rate | 100,00% |
| Mean Token F1 | 1,0000 |
| Judge accuracy | 100,00% |
| Mean judge score | 5,00/5 |
| GX / Freshness | 7/7 checks đạt; 1/24 bài quá 180 ngày (4,17%) |

Bằng chứng chính: [baseline_metrics.json](../data/results/baseline_metrics.json), [baseline_answers.json](../data/results/baseline_answers.json), [phase1_report.md](../data/reports/phase1_report.md), [baseline_quality_report.json](../data/quality/baseline_quality_report.json) và [test_set.json](../data/eval/test_set.json). Bảng sạch có tại `data/clean/papers_clean.csv` và `data/clean/papers_clean.json`; embedding manifest tại `data/embeddings/papers_embeddings.json`.

## Bước 4 — Sáu lỗi dữ liệu

Chọn **5** bài mới nhất để bỏ (`ceil(24 × 20%)`), sau đó chọn năm DOI nhỏ nhất còn lại cho các lỗi khác. Cách chọn độc lập với test set và lặp lại cho cùng kết quả.

| Lỗi | DOI bị tác động / kết quả |
| --- | --- |
| Bỏ bài mới | `...1812`, `...1808`, `...1804`, `...1807`, `...1802` |
| Xóa summary | `...1801` |
| Chèn noise vào summary | `...1803` |
| Cắt title xuống dưới 8 ký tự | `...1805` |
| Lùi `published` 365 ngày, tăng `age_days` tương ứng | `...1806` |
| Nhân bản dòng tạo DOI trùng | `...1809` |

Các hậu tố DOI trong bảng thuộc tiền tố `10.1145/3637528.367`. Đầu ra có **20 dòng, 19 DOI duy nhất**. Phép thử trong bộ nhớ xác nhận cả sáu thay đổi, log có giá trị trước/sau, `text_for_embedding` khớp các trường sau sửa, input DataFrame không đổi và hai lần chạy cho cùng output. Log thực tế được lưu tại [corruption_log.json](../data/results/corruption_log.json) khi chạy bước 5.

## Bước 5 — Đánh giá, repair và đối chiếu

Lần gọi đầu của `script/run_corruption_flow.py` dừng ở bước import `scipy` với lỗi Windows **“The paging file is too small”**, exit code **1**, chưa tạo artifact của bước 5. Chạy lại với `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1` hoàn tất với **exit code 0**. Lần chạy thành công dùng `mock`, tắt Ragas và chạy embedding từ cache offline.

| Chỉ số thực tế | Baseline | Corrupted | Repaired |
| --- | ---: | ---: | ---: |
| Số tài liệu | 24 | 20 | 24 |
| Số câu hỏi chung | 10 | 10 | 10 |
| Retrieval Hit Rate | 100,00% | 80,00% | 100,00% |
| Mean Token F1 | 1,0000 | 0,9741 | 1,0000 |
| Judge accuracy | 100,00% | 100,00% | 100,00% |
| Mean judge score | 5,00 | 4,80 | 5,00 |
| GX expectations đạt | 7/7 | 3/7 | 7/7 |
| Quality gate | đạt | không đạt | đạt |
| Bài quá hạn / Freshness | 1/24, đạt | 2/20, đạt | 1/24, đạt |

Quality của corrupted fail ở row count, DOI uniqueness, title length và summary length. Freshness **vẫn đạt** vì 10% bài quá hạn chưa vượt ngưỡng 25%; không điều chỉnh lỗi để ép chỉ số này fail.

Repair từ `data/raw/crossref_records.json` cho JSON **khớp hoàn toàn** clean baseline; xây lại lần hai cho cùng nội dung. Metrics repaired bằng baseline. Truy vấn repaired được lặp lại trong cùng collection và trả cùng câu trả lời cùng danh sách DOI. Chroma SQLite của comparison có hai collection `papers-corrupted` (**20** embeddings) và `papers-repaired` (**24** embeddings). Hash của raw snapshot, clean baseline, test set, baseline metrics/answers và SQLite baseline không đổi sau bước 5.

Bằng chứng: [corrupted_metrics.json](../data/results/corrupted_metrics.json), [repaired_metrics.json](../data/results/repaired_metrics.json), [corruption_report.md](../data/reports/corruption_report.md), các quality/freshness JSON trong `data/quality/` và hai collection trong `data/chroma/comparison/`.

### Giới hạn của benchmark

Cả **10/10** câu hỏi trích dẫn DOI. Hàm QA ưu tiên kết quả tra cứu DOI chính xác, nên Hit Rate không đo riêng khả năng tìm kiếm ngữ nghĩa. Dữ liệu lỗi làm mất hai DOI trong test set: `q001` và `q002` không retrieval hit, nhưng `q002` vẫn có câu trả lời trùng ground truth. Judge trong chế độ mock dùng heuristic fallback cho cả 10 câu; `judge_accuracy=100%` không phải kết quả chấm bằng LLM. Ragas được bỏ qua. Các chỉ số trong bảng là kết quả đo thật, không suy diễn rằng mọi dạng corruption đều làm giảm metrics.

## Artifact mới ở bước 5

- `data/clean/papers_clean_corrupted.csv`, `papers_clean_corrupted.json`, `papers_clean_repaired.csv`, `papers_clean_repaired.json`.
- `data/embeddings/papers_embeddings_corrupted.json`, `papers_embeddings_repaired.json`; DB và index của hai collection tại `data/chroma/comparison/`.
- `data/quality/corrupted_quality_report.json`, `repaired_quality_report.json`, `corrupted_freshness_report.json`, `repaired_freshness_report.json`.
- `data/results/corruption_log.json`, `corrupted_metrics.json`, `corrupted_answers.json`, `repaired_metrics.json`, `repaired_answers.json`.
- `data/reports/corruption_report.md`.

Hai script từ chối ghi đè artifact đã có; muốn tái chạy phải dùng workspace/đầu ra riêng theo quyết định của nhóm, không xóa dữ liệu hiện tại.

## Checklist nghiệm thu theo `docs/SUBMISSION.md`

| Mục | Trạng thái hiện tại |
| --- | --- |
| `script/run_phase1.py` exit code 0 | **Đạt** — đã chạy ở bước 3. |
| `script/run_corruption_flow.py` exit code 0 | **Đạt** — lần chạy với giới hạn luồng số học exit code 0. |
| `corruption_report.md` có bảng ba trạng thái | **Đạt** — số trong bảng khớp metrics JSON. |
| Có `baseline_metrics.json`, `corrupted_metrics.json`, `repaired_metrics.json` | **Đạt** — cả ba file tồn tại và có 10 samples. |
| `TEAM.md` điền thông tin, MSSV, đóng góp từng người | **Chưa đạt** — còn placeholder và ô thành viên trống. Nhóm phải tự điền, xác nhận đóng góp. |
| Không commit `.env` | **Đạt theo lịch sử Git local đã kiểm tra** — `.env` không nằm trong tracked files hoặc lịch sử truy vấn; nhóm vẫn cần rà soát secret trước khi push. |
| 100% thành viên có commit trên `main` / GitHub Insights | **Chưa xác minh** — chưa commit/push; nhóm tự kiểm tra trên GitHub. |
| Mỗi cá nhân nộp link repo trên LMS trước hạn | **Chưa xác minh** — từng thành viên phải tự nộp. |

Nhóm còn phải tự hoàn thiện `report/group_report.md` và báo cáo cá nhân (các file hiện vẫn là mẫu), kiểm tra quy ước tên repo, chuẩn bị **live demo** và giải thích được GX 1.x, Freshness SLA, tác động của hai DOI bị mất cùng giới hạn benchmark. Không có hành động nộp bài, commit hoặc push nào được thực hiện trong lượt làm việc này.
