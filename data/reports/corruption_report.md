# Báo Cáo Đối Chiếu 3 Trạng Thái — Data Pipeline, Observability & RAG Resilience

> **Mục tiêu:** Chứng minh năng lực phát hiện sớm sự suy giảm chất lượng dữ liệu (Data Observability), phân tích hiện tượng **Silent Failure** của RAG Agent khi dữ liệu bị lỗi, và kiểm chứng cơ chế tự phục hồi an toàn (**Idempotent Repair**).

---

## 1. Bảng Đối Chiếu Định Lượng 3 Trạng Thái (Benchmark Comparison)

| Chỉ số / Metric | 1. Baseline (Sạch) | 2. Corrupted (Lỗi) | 3. Repaired (Phục hồi) | Tác Động Khi Lỗi (Corrupted vs Base) | Mức Độ Khôi Phục (Repaired vs Base) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Data Quality Gate (GX 1.x)** | **PASSED ✅** | **FAILED ❌** | **PASSED ✅** | Vi phạm schema & uniqueness | Khôi phục 100% checks |
| **Freshness SLA (age ≤ 180d)** | **ĐẠT SLA ✅** | **VI PHẠM ⚠️** | **ĐẠT SLA ✅** | Tỷ lệ stale > 25% | Tươi mới trở lại |
| **Retrieval Hit Rate** | **100.0%** | **60.0%** | **100.0%** | **-40.0%** | **+0.0%** |
| **Mean Token F1** | **1.0000** | **0.5741** | **1.0000** | **-0.4259** | **+0.0000** |
| **Judge Accuracy** | **100.0%** | **60.0%** | **100.0%** | **-40.0%** | **+0.0%** |
| **Mean Judge Score (1-5)** | **5.00** | **3.20** | **5.00** | **-1.80** | **+0.00** |

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
  - Retrieval Hit Rate sụt giảm nghiêm trọng từ **100.0%** xuống **60.0%**.
  - Token F1 giảm từ **1.0000** xuống **0.5741**, phản ánh hiện tượng hallucination hoặc câu trả lời không đầy đủ.
  - Judge Accuracy giảm mạnh từ **100.0%** xuống **60.0%**.
- **Ý nghĩa của Data Observability:** Nhờ có **Great Expectations 1.x Quality Gate** và **Freshness SLA Monitoring**, hệ thống đã lập tức phát hiện các bất thường về tính duy nhất, tính toàn vẹn và độ tươi mới, ngăn chặn dữ liệu bẩn tiếp tục âm thầm phục vụ người dùng.

---

## 4. Cơ Chế Tự Phục Hồi An Toàn (Idempotent Repair)

- **Nguyên tắc Idempotency:** Quá trình phục hồi có thể chạy nhiều lần mà vẫn tạo ra cùng một kết quả nhất quán duy nhất.
- **Quy trình phục hồi:**
  1. Truy vết nguồn gốc (Data Lineage) về bản lưu trữ thô bất biến `data/raw/crossref_records.json`.
  2. Thực hiện lại toàn bộ quy trình làm sạch chuẩn hóa (Cleaning & Pre-embed Modeling).
  3. Xóa và tái tạo lại ChromaDB collection sạch (`papers-repaired`).
  4. Tái đánh giá trên cùng tập benchmark test set 10 câu hỏi để đảm bảo tính khách quan.
- **Kết quả nghiệm thu:** Toàn bộ các chỉ số hiệu năng RAG (Hit Rate: **100.0%**, Token F1: **1.0000**) và chốt kiểm dịch chất lượng dữ liệu được phục hồi hoàn toàn về trạng thái chuẩn tương đương Baseline ban đầu.
