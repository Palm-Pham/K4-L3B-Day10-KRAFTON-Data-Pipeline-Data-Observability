# Báo cáo cá nhân — Phan Đình Bảo Khôi

> Bản nháp theo phân công nhóm. Người đứng tên cần rà phần việc thực tế, bổ sung commit/minh chứng cá nhân và xác nhận trước khi nộp.

## Thông tin và vai trò

- Họ và tên: **Phan Đình Bảo Khôi**
- MSSV: **2A202602434**
- Nhóm/lớp: KRAFTON · K4-L3B
- Vai trò được phân công: **Embedding, Chroma index và QA retrieval**
- Tỷ trọng phân công đề xuất: **20%**

## Phạm vi được phân công

**Đầu vào:** Cleaned records và model all-MiniLM-L6-v2.

1. Kiểm tra MiniLM embeddings và fallback local trong src/retrieval/embeddings.py.
2. Quản lý ba Chroma collections, đối sánh DOI/tiêu đề và BM25 rerank trong src/retrieval/index.py.
3. Kiểm tra QA metadata và chế độ LLM có trích dẫn DOI trong src/retrieval/qa.py, llm.py.

**Bàn giao:** Bàn giao hàm truy xuất và ba index cho evaluation và live demo.

## Artifact hiện có để đối chiếu

- [data/chroma/chroma.sqlite3](../data/chroma/chroma.sqlite3)
- [data/embeddings/papers_embeddings.json](../data/embeddings/papers_embeddings.json)
- [data/embeddings/papers_embeddings_corrupted.json](../data/embeddings/papers_embeddings_corrupted.json)
- [data/embeddings/papers_embeddings_repaired.json](../data/embeddings/papers_embeddings_repaired.json)
- [data/results/baseline_answers.json](../data/results/baseline_answers.json)

Các artifact trên chứng minh trạng thái repository; chỉ riêng sự tồn tại của chúng không chứng minh ai đã viết mã hoặc chạy thí nghiệm.

## Cách kiểm chứng phần việc

Đối chiếu baseline Hit@1 10/10 trên golden set, challenge 2/2 từ chối đúng; cần thêm tập độc lập để kiểm tra tổng quát.

## Tự xác nhận trước khi nộp

- [ ] Tôi đã thực hiện hoặc review đúng các mục được ghi trong báo cáo này.
- [ ] Tôi đã đối chiếu commit của mình trên nhánh nộp bài.
- [ ] Tôi có thể giải thích input, output, giới hạn và cách kiểm chứng của phần việc.
- [ ] Tôi đã sửa các mục không đúng với đóng góp thực tế của mình.

Báo cáo kết quả chung và các số liệu cập nhật nằm ở [group_report.md](group_report.md).
