# Danh Sách Thành Viên & Báo Cáo Phân Công Nhóm

- **Tên Nhóm:** `KRAFTON`
- **Mã Nhóm / Lớp:** `K4-L3B-DAY10`
- **Tên Repository Nộp Bài:** `K4-L3B-Day10-KRAFTON-Data-Pipeline-Data-Observability`

---

## 1. Danh Sách Thành Viên & Vai Trò

| STT | Họ và tên | MSSV | Email | Vai trò & Phân công công việc | Báo cáo cá nhân |
|---:|---|---|---|---|---|
| 1 | Nguyễn Hoàng Nam | 20210001 | nam.nh@vinuni.edu.vn | Trưởng nhóm / Pipeline Integrator (`core/`, `phase1.py`, `corruption_flow.py`) | `report/20210001_NguyenHoangNam.md` |
| 2 | Trần Quang Minh | 20210002 | minh.tq@vinuni.edu.vn | Data Foundation & Recovery (`crossref.py`, `cleaning.py`, raw data) | `report/20210002_TranQuangMinh.md` |
| 3 | Lê Thu Hà | 20210003 | ha.lt@vinuni.edu.vn | RAG & Vector Index (`retrieval/index.py`, `embeddings.py`, ChromaDB) | `report/20210003_LeThuHa.md` |
| 4 | Võ Đức Tài | 2A202603007 | tai.vd@vinuni.edu.vn | Observability & Evaluation (`quality.py` GX 1.x, `testset.py`, reporting) | `report/individual_report.md` / `report/2A202603007_VoDucTai.md` |

---

## 2. Phần Tự Khai Báo Đóng Góp Chi Tiết Từng Thành Viên

### 2.1. Nguyễn Hoàng Nam — MSSV: 20210001
- **Vai trò:** Trưởng nhóm & Điều phối Pipeline (Pipeline Integrator).
- **Công việc chi tiết đã hoàn thành:**
  - Thiết lập kiến trúc dự án, cấu hình hệ thống `core/config.py` và đường dẫn artifacts `core/utils.py`.
  - Kết nối luồng thực thi trong `src/pipelines/phase1.py` và `src/pipelines/corruption_flow.py`.
  - Kiểm tra tính nhất quán của toàn bộ artifacts dữ liệu và điều phối thực thi chạy end-to-end trên môi trường Conda `e`.
- **Điều học được / Đóng góp chính:**
  - Hiểu sâu sắc về thiết kế **Idempotent Pipeline** và cơ chế bảo toàn dữ liệu đa tầng trong hệ thống sản xuất.

### 2.2. Trần Quang Minh — MSSV: 20210002
- **Vai trò:** Phụ trách Ingestion, Làm sạch & Phục hồi dữ liệu (Data Foundation & Recovery).
- **Công việc chi tiết đã hoàn thành:**
  - Xây dựng module thu thập Crossref API với cơ chế Fallback offline trong `src/ingestion/crossref.py`.
  - Chuẩn hóa schema, tính toán trường `age_days` và cấu trúc `text_for_embedding` 5 phần trong `src/ingestion/cleaning.py`.
  - Triển khai kịch bản làm bẩn dữ liệu trong `src/ingestion/corruption.py` và cơ chế Idempotent Repair phục hồi từ raw snapshot.
- **Điều học được / Đóng góp chính:**
  - Kỹ thuật truy vết nguồn gốc dữ liệu (**Data Lineage**) và nguyên tắc bảo toàn Raw Snapshot bất biến trước mọi phép biến đổi.

### 2.3. Lê Thu Hà — MSSV: 20210003
- **Vai trò:** Phụ trách RAG, Vector Database & Embedding (Vector Store Specialist).
- **Công việc chi tiết đã hoàn thành:**
  - Quản lý mô hình embedding `sentence-transformers/all-MiniLM-L6-v2` với cơ chế local ONNX fallback siêu tốc.
  - Quản lý và cô lập 3 collection riêng biệt trong ChromaDB (`papers-baseline`, `papers-corrupted`, `papers-repaired`).
  - Tích hợp QA Agent và LLM Router hỗ trợ Ollama local `qwen2.5:latest`.
- **Điều học được / Đóng góp chính:**
  - Cách cô lập không gian vector để đo lường khách quan sự suy giảm ngữ nghĩa giữa dữ liệu sạch và dữ liệu lỗi.

### 2.4. Võ Đức Tài — MSSV: 2A202603007
- **Vai trò:** Phụ trách Data Observability & Benchmark Evaluation (Observability & Evaluation Owner).
- **Công việc chi tiết đã hoàn thành:**
  - Thiết lập Quality Gate theo chuẩn mới **Great Expectations 1.x** (`ephemeral mode`) và giám sát Freshness SLA trong `src/observability/quality.py`.
  - Xây dựng bộ câu hỏi đánh giá chuẩn gồm 10 câu hỏi bao phủ 4 nhóm nghiệp vụ trong `src/evaluation/testset.py`.
  - Xây dựng engine xuất báo cáo tự động Markdown (`reporting.py`) và tạo bảng đối chiếu định lượng 3 trạng thái.
- **Điều học được / Đóng góp chính:**
  - Nhận thức rõ hiện tượng **Silent Failure** và cách thức thiết lập hệ thống cảnh báo sớm chặn đứng dữ liệu bẩn trước khi vào serving layer.
