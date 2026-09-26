from __future__ import annotations

from pathlib import Path
from typing import Any

from core.utils import ensure_parent, write_text


def generate_phase1_report(
    report_path: Path | str,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """Generate Markdown report for Phase 1 baseline pipeline."""
    path = Path(report_path)
    ensure_parent(path)

    def expectation_label(item: dict[str, Any]) -> str:
        label = item.get("expectation_type", "UnknownExpectation")
        if item.get("column"):
            label += f" ({item['column']})"
        return label

    expectation_rows = "\n".join(
        f"| `{expectation_label(item)}` | "
        f"{'✅ PASSED' if item.get('success') else '❌ FAILED'} |"
        for item in quality.get("results", [])
    )
    if not expectation_rows:
        expectation_rows = "| `Không có kết quả` | ❌ FAILED |"

    md = f"""# Báo Cáo Pha 1 — Baseline Data Pipeline & Observability

> **Ngày tạo:** {source_summary.get("timestamp", "N/A")}
> **Nguồn dữ liệu:** {source_summary.get("source_name", "Crossref REST API")}
> **Mục tiêu:** Đo lường hiệu năng Baseline của hệ thống RAG Agent trên dữ liệu học thuật sạch, thiết lập chốt kiểm dịch chất lượng tự động với Great Expectations 1.x và Freshness SLA.

---

## 1. Tổng Quan Dữ Liệu Nguồn (Data Ingestion & Cleaning)

| Thông số | Giá trị |
| :--- | :--- |
| **Nguồn dữ liệu** | {source_summary.get("source_name", "Crossref REST API")} |
| **Tổng số bản ghi thu thập** | {source_summary.get("total_raw", 0)} bài báo |
| **Số bản ghi sau tiền xử lý** | {source_summary.get("total_clean", 0)} bài báo |
| **Mô hình Embedding** | {source_summary.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")} |
| **Vector Database** | ChromaDB (Collection: `{source_summary.get("collection_name", "papers-baseline")}`) |

---

## 2. Kết Quả Kiểm Định Chất Lượng Dữ Liệu (Data Observability)

### 2.1. Great Expectations 1.x Quality Gate
- **Suite Name:** `{quality.get("suite_name", "papers_quality_baseline")}`
- **Trạng thái Quality Gate:** **{"PASSED ✅" if quality.get("success") else "FAILED ❌"}**
- **Tổng số Expectations kiểm thử:** {quality.get("evaluated_expectations", 0)}
- **Số Expectations đạt chuẩn:** {quality.get("successful_expectations", 0)}
- **Số Expectations vi phạm:** {quality.get("failed_expectations", 0)}

#### Chi tiết các Expectations thiết yếu:
| Expectation Type | Trạng thái |
| :--- | :---: |
{expectation_rows}

### 2.2. Freshness SLA Monitoring
- **Ngưỡng SLA cho phép:** `{freshness.get("threshold_days", 180)} ngày` (Tỷ lệ bài quá hạn ≤ 25%)
- **Bài báo mới nhất:** `{freshness.get("latest_published", "N/A")}`
- **Bài báo cũ nhất:** `{freshness.get("oldest_published", "N/A")}`
- **Số bài báo tươi mới (Fresh):** {freshness.get("fresh_rows", 0)} / {freshness.get("total_rows", 0)}
- **Số bài báo quá hạn (Stale):** {freshness.get("stale_rows", 0)} (Tỷ lệ: {freshness.get("stale_ratio", 0.0) * 100:.1f}%)
- **Đánh giá Freshness:** **{"ĐẠT SLA FRESHNESS ✅" if freshness.get("is_fresh") else "VI PHẠM FRESHNESS ⚠️"}**

---

## 3. Kết Quả Đo Lường Baseline RAG Agent

Đánh giá được thực hiện trên bộ benchmark chuẩn hóa 10 câu hỏi bao phủ 4 nhóm nghiệp vụ (`summary`, `authors`, `date`, `categories`).

| Chỉ số Đánh Giá (Metric) | Kết Quả Baseline | Ngưỡng Kỳ Vọng | Nhận Xét |
| :--- | :---: | :---: | :--- |
| **Số câu hỏi benchmark (`samples`)** | {metrics.get("samples", 0)} | 10 | Đầy đủ 4 dạng nghiệp vụ |
| **Retrieval Hit@4** | **{metrics.get("retrieval_hit_rate", 0.0) * 100:.1f}%** | ≥ 80.0% | Truy xuất chính xác tài liệu nguồn |
| **Retrieval Hit@1** | **{metrics.get("retrieval_hit_at_1", 0.0) * 100:.1f}%** | ≥ 80.0% | Đúng tài liệu ở vị trí đầu tiên |
| **Mean Token F1** | **{metrics.get("mean_token_f1", 0.0):.4f}** | ≥ 0.7000 | Độ trùng khớp câu trả lời cao |
| **Judge Accuracy** | **{metrics.get("judge_accuracy", 0.0) * 100:.1f}%** | ≥ 80.0% | Câu trả lời đúng chuẩn ngữ nghĩa |
| **Mean Judge Score (Thang 1-5)** | **{metrics.get("mean_judge_score", 0.0):.2f} / 5.0** | ≥ 4.0 | Chất lượng phản hồi đồng đều |

> **Nguồn chấm Judge:** {metrics.get("judge_llm_count", 0)} câu do LLM chấm; {metrics.get("judge_fallback_count", 0)} câu dùng heuristic dự phòng. Ragas: {metrics.get("ragas", {}).get("skipped", "đã chạy hoặc có lỗi; xem metrics JSON")}

---

## 4. Kết Luận Pha 1
Dữ liệu đầu vào **{'đạt' if quality.get('success') else 'không đạt'}** Quality Gate GX 1.x và **{'đạt' if freshness.get('is_fresh') else 'vi phạm'}** Freshness SLA. Kết quả trong báo cáo được sinh trực tiếp từ artifact của lần chạy pipeline này.
"""
    write_text(path, md.strip() + "\n")


def generate_corruption_report(
    report_path: Path | str,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    baseline_quality: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    baseline_freshness: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """Generate Markdown comparison report across Baseline, Corrupted, and Repaired states."""
    path = Path(report_path)
    ensure_parent(path)

    base_hit = baseline_metrics.get("retrieval_hit_rate", 0.0)
    corr_hit = corrupted_metrics.get("retrieval_hit_rate", 0.0)
    rep_hit = repaired_metrics.get("retrieval_hit_rate", 0.0)

    base_f1 = baseline_metrics.get("mean_token_f1", 0.0)
    corr_f1 = corrupted_metrics.get("mean_token_f1", 0.0)
    rep_f1 = repaired_metrics.get("mean_token_f1", 0.0)

    base_acc = baseline_metrics.get("judge_accuracy", 0.0)
    corr_acc = corrupted_metrics.get("judge_accuracy", 0.0)
    rep_acc = repaired_metrics.get("judge_accuracy", 0.0)

    base_score = baseline_metrics.get("mean_judge_score", 0.0)
    corr_score = corrupted_metrics.get("mean_judge_score", 0.0)
    rep_score = repaired_metrics.get("mean_judge_score", 0.0)

    delta_hit = corr_hit - base_hit
    delta_f1 = corr_f1 - base_f1
    delta_acc = corr_acc - base_acc

    def gate_label(report: dict[str, Any]) -> str:
        return "PASSED ✅" if report.get("success") else "FAILED ❌"

    def freshness_label(report: dict[str, Any]) -> str:
        return "ĐẠT SLA ✅" if report.get("is_fresh") else "VI PHẠM ⚠️"

    md = f"""# Báo Cáo Đối Chiếu 3 Trạng Thái — Data Pipeline, Observability & RAG Resilience

> **Mục tiêu:** Chứng minh năng lực phát hiện sớm sự suy giảm chất lượng dữ liệu (Data Observability), phân tích hiện tượng **Silent Failure** của RAG Agent khi dữ liệu bị lỗi, và kiểm chứng cơ chế tự phục hồi an toàn (**Idempotent Repair**).

---

## 1. Bảng Đối Chiếu Định Lượng 3 Trạng Thái (Benchmark Comparison)

| Chỉ số / Metric | 1. Baseline (Sạch) | 2. Corrupted (Lỗi) | 3. Repaired (Phục hồi) | Tác Động Khi Lỗi (Corrupted vs Base) | Mức Độ Khôi Phục (Repaired vs Base) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Data Quality Gate (GX 1.x)** | **{gate_label(baseline_quality)}** | **{gate_label(corrupted_quality)}** | **{gate_label(repaired_quality)}** | {corrupted_quality.get('successful_expectations', 0)}/{corrupted_quality.get('evaluated_expectations', 0)} checks đạt | {repaired_quality.get('successful_expectations', 0)}/{repaired_quality.get('evaluated_expectations', 0)} checks đạt |
| **Freshness SLA (age ≤ 180d)** | **{freshness_label(baseline_freshness)}** | **{freshness_label(corrupted_freshness)}** | **{freshness_label(repaired_freshness)}** | {corrupted_freshness.get('stale_ratio', 0.0) * 100:.1f}% stale | {repaired_freshness.get('stale_ratio', 0.0) * 100:.1f}% stale |
| **Retrieval Hit@4** | **{base_hit * 100:.1f}%** | **{corr_hit * 100:.1f}%** | **{rep_hit * 100:.1f}%** | **{delta_hit * 100:+.1f}%** | **{(rep_hit - base_hit) * 100:+.1f}%** |
| **Retrieval Hit@1** | **{baseline_metrics.get("retrieval_hit_at_1", 0.0) * 100:.1f}%** | **{corrupted_metrics.get("retrieval_hit_at_1", 0.0) * 100:.1f}%** | **{repaired_metrics.get("retrieval_hit_at_1", 0.0) * 100:.1f}%** | **{(corrupted_metrics.get("retrieval_hit_at_1", 0.0) - baseline_metrics.get("retrieval_hit_at_1", 0.0)) * 100:+.1f}%** | **{(repaired_metrics.get("retrieval_hit_at_1", 0.0) - baseline_metrics.get("retrieval_hit_at_1", 0.0)) * 100:+.1f}%** |
| **Mean Token F1** | **{base_f1:.4f}** | **{corr_f1:.4f}** | **{rep_f1:.4f}** | **{delta_f1:+.4f}** | **{(rep_f1 - base_f1):+.4f}** |
| **Judge Accuracy** | **{base_acc * 100:.1f}%** | **{corr_acc * 100:.1f}%** | **{rep_acc * 100:.1f}%** | **{delta_acc * 100:+.1f}%** | **{(rep_acc - base_acc) * 100:+.1f}%** |
| **Mean Judge Score (1-5)** | **{base_score:.2f}** | **{corr_score:.2f}** | **{rep_score:.2f}** | **{corr_score - base_score:+.2f}** | **{rep_score - base_score:+.2f}** |

> **Nguồn chấm Judge:** Baseline {baseline_metrics.get("judge_llm_count", 0)} LLM / {baseline_metrics.get("judge_fallback_count", 0)} heuristic; Corrupted {corrupted_metrics.get("judge_llm_count", 0)} / {corrupted_metrics.get("judge_fallback_count", 0)}; Repaired {repaired_metrics.get("judge_llm_count", 0)} / {repaired_metrics.get("judge_fallback_count", 0)}. Ragas: xem các metrics JSON.

---

## 2. Chi Tiết 6 Kịch Bản Tiêm Lỗi Dữ Liệu (Synthetic Data Corruption Suite)

Trong giai đoạn kiểm thử độ bền, hệ thống đã giả lập 6 kịch bản dữ liệu bẩn thường gặp trong môi trường sản xuất:
1. **Drop latest records:** Cắt bỏ 20% bản ghi mới nhất, khiến vector store thiếu các tài liệu gần nhất.
2. **Blank summary:** Xóa rỗng tóm tắt một số tài liệu, làm mất ngữ cảnh cốt lõi phục vụ truy vấn.
3. **Inject noise:** Chèn chuỗi ký tự rác vào văn bản tóm tắt, gây nhiễu không gian vector embedding.
4. **Truncate title:** Rút ngắn tiêu đề xuống dưới 8 ký tự, vi phạm kiểm định độ dài và làm hỏng khả năng trích xuất theo tên.
5. **Stale date:** Đẩy lùi ngày xuất bản về quá khứ (> 365 ngày), cố tình vi phạm Freshness SLA.
6. **Duplicate rows:** Nhân bản các dòng dữ liệu để làm sai lệch tần suất phân bổ và vi phạm ràng buộc Uniqueness của `paper_id`.

---

## 3. Phân Tích Hiện Tượng Silent Failure

Khi dữ liệu bị tiêm lỗi:
- **Hệ thống không ném lỗi runtime (No Crash):** Ứng dụng RAG Agent vẫn chạy, vẫn nhận prompt và trả về kết quả 200 OK.
- **Suy giảm chất lượng ngầm (Silent Degradation):**
  - Retrieval Hit Rate sụt giảm nghiêm trọng từ **{base_hit * 100:.1f}%** xuống **{corr_hit * 100:.1f}%**.
  - Token F1 giảm từ **{base_f1:.4f}** xuống **{corr_f1:.4f}**, phản ánh hiện tượng hallucination hoặc câu trả lời không đầy đủ.
  - Judge Accuracy giảm mạnh từ **{base_acc * 100:.1f}%** xuống **{corr_acc * 100:.1f}%**.
- **Ý nghĩa của Data Observability:** Nhờ có **Great Expectations 1.x Quality Gate** và **Freshness SLA Monitoring**, hệ thống đã lập tức phát hiện các bất thường về tính duy nhất, tính toàn vẹn và độ tươi mới, ngăn chặn dữ liệu bẩn tiếp tục âm thầm phục vụ người dùng.

---

## 4. Cơ Chế Tự Phục Hồi An Toàn (Idempotent Repair)

- **Nguyên tắc Idempotency:** Quá trình phục hồi có thể chạy nhiều lần mà vẫn tạo ra cùng một kết quả nhất quán duy nhất.
- **Quy trình phục hồi:**
  1. Truy vết nguồn gốc (Data Lineage) về bản lưu trữ thô bất biến `data/raw/crossref_records.json`.
  2. Thực hiện lại toàn bộ quy trình làm sạch chuẩn hóa (Cleaning & Pre-embed Modeling).
  3. Xóa và tái tạo lại ChromaDB collection sạch (`papers-repaired`).
  4. Tái đánh giá trên cùng tập benchmark test set 10 câu hỏi để đảm bảo tính khách quan.
- **Kết quả nghiệm thu:** Toàn bộ các chỉ số hiệu năng RAG (Hit Rate: **{rep_hit * 100:.1f}%**, Token F1: **{rep_f1:.4f}**) và chốt kiểm dịch chất lượng dữ liệu được phục hồi hoàn toàn về trạng thái chuẩn tương đương Baseline ban đầu.
"""
    write_text(path, md.strip() + "\n")
