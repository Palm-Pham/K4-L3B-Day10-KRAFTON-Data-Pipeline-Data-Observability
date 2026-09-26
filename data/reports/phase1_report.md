# Báo Cáo Pha 1 — Baseline Data Pipeline & Observability

> **Ngày tạo:** 2026-09-26
> **Nguồn dữ liệu:** Crossref REST API
> **Mục tiêu:** Đo lường hiệu năng Baseline của hệ thống RAG Agent trên dữ liệu học thuật sạch, thiết lập chốt kiểm dịch chất lượng tự động với Great Expectations 1.x và Freshness SLA.

---

## 1. Tổng Quan Dữ Liệu Nguồn (Data Ingestion & Cleaning)

| Thông số | Giá trị |
| :--- | :--- |
| **Nguồn dữ liệu** | Crossref REST API |
| **Tổng số bản ghi thu thập** | 24 bài báo |
| **Số bản ghi sau tiền xử lý** | 24 bài báo |
| **Mô hình Embedding** | sentence-transformers/all-MiniLM-L6-v2 |
| **Vector Database** | ChromaDB (Collection: `papers-baseline`) |

---

## 2. Kết Quả Kiểm Định Chất Lượng Dữ Liệu (Data Observability)

### 2.1. Great Expectations 1.x Quality Gate
- **Suite Name:** `papers_quality_baseline`
- **Trạng thái Quality Gate:** **PASSED ✅**
- **Tổng số Expectations kiểm thử:** 5
- **Số Expectations đạt chuẩn:** 5
- **Số Expectations vi phạm:** 0

#### Chi tiết các Expectations thiết yếu:
| Expectation Type | Trạng thái |
| :--- | :---: |
| `ExpectTableRowCountToBeBetween` | ✅ PASSED |
| `ExpectColumnValuesToNotBeNull (paper_id)` | ✅ PASSED |
| `ExpectColumnValuesToNotBeNull (title)` | ✅ PASSED |
| `ExpectColumnValuesToBeUnique (paper_id)` | ✅ PASSED |
| `ExpectColumnValueLengthsToBeBetween (title)` | ✅ PASSED |

### 2.2. Freshness SLA Monitoring
- **Ngưỡng SLA cho phép:** `180 ngày` (Tỷ lệ bài quá hạn ≤ 25%)
- **Bài báo mới nhất:** `2026-07-22`
- **Bài báo cũ nhất:** `2026-03-28`
- **Số bài báo tươi mới (Fresh):** 23 / 24
- **Số bài báo quá hạn (Stale):** 1 (Tỷ lệ: 4.2%)
- **Đánh giá Freshness:** **ĐẠT SLA FRESHNESS ✅**

---

## 3. Kết Quả Đo Lường Baseline RAG Agent

Đánh giá được thực hiện trên bộ benchmark chuẩn hóa 10 câu hỏi bao phủ 4 nhóm nghiệp vụ (`summary`, `authors`, `date`, `categories`).

| Chỉ số Đánh Giá (Metric) | Kết Quả Baseline | Ngưỡng Kỳ Vọng | Nhận Xét |
| :--- | :---: | :---: | :--- |
| **Số câu hỏi benchmark (`samples`)** | 10 | 10 | Đầy đủ 4 dạng nghiệp vụ |
| **Retrieval Hit@4** | **100.0%** | ≥ 80.0% | Truy xuất chính xác tài liệu nguồn |
| **Retrieval Hit@1** | **100.0%** | ≥ 80.0% | Đúng tài liệu ở vị trí đầu tiên |
| **Mean Token F1** | **1.0000** | ≥ 0.7000 | Độ trùng khớp câu trả lời cao |
| **Judge Accuracy** | **100.0%** | ≥ 80.0% | Câu trả lời đúng chuẩn ngữ nghĩa |
| **Mean Judge Score (Thang 1-5)** | **5.00 / 5.0** | ≥ 4.0 | Chất lượng phản hồi đồng đều |

> **Nguồn chấm Judge:** 0 câu do LLM chấm; 10 câu dùng heuristic dự phòng. Ragas: Set RUN_RAGAS=1 to enable the slower Ragas pass.

---

## 4. Kết Luận Pha 1
Dữ liệu đầu vào hoàn toàn hợp lệ, thỏa mãn toàn bộ tiêu chí chốt kiểm dịch chất lượng (GX 1.x) và đạt cam kết độ tươi mới (Freshness SLA). Hệ thống RAG Agent hoạt động ổn định và sẵn sàng cho các bài kiểm thử độ bền (Stress-test & Corruption Simulation).
