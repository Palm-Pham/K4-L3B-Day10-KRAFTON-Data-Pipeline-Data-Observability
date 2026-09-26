# Báo cáo cá nhân — Phan Đình Bảo Khôi

**MSSV:** 2A202602434 · **Nhóm:** KRAFTON · **Lớp:** K4-L3B
**Vai trò theo phân công:** Embedding, Chroma index và QA retrieval · **Tỷ trọng phân công:** 20%

Báo cáo này trình bày đầy đủ phạm vi vai trò và kết quả kỹ thuật có thể kiểm tra trong repository. Phần ai trực tiếp viết mã, chạy thí nghiệm và các commit cá nhân cần được người đứng tên đối chiếu trước khi nộp.

## 1. Mục tiêu và đầu vào

Mục tiêu của vai trò là embedding, chroma index và qa retrieval. Đầu vào: Cleaned rows có paper_id, metadata và text_for_embedding.

## 2. Công việc và cách triển khai

1. Biến text_for_embedding thành vector bằng all-MiniLM-L6-v2; thử model đã cache, ONNX MiniLM của Chroma, rồi mới dùng tải weights khi cần.
2. Quản lý các collection papers-baseline, papers-corrupted và papers-repaired trong ChromaDB; manifest giữ metadata và đường dẫn persist tương đối.
3. Ưu tiên DOI/tiêu đề khớp chính xác; kết hợp cosine similarity với BM25 trên title/summary để rerank ứng viên dense.
4. QA metadata trích summary, authors, date hoặc categories từ kết quả đầu; chế độ LLM tạo câu trả lời theo context và yêu cầu dẫn DOI khi provider có key.

**Quyết định kỹ thuật:** Đánh trọng số title trong chỉ mục sparse để phân biệt các paper có abstract gần giống nhau. Kết quả top-1 được kiểm tra trên golden set; các câu hỏi về tiêu đề không tồn tại được từ chối thay vì đưa nguồn không liên quan.

## 3. Kết quả kiểm chứng

Collection baseline chứa 24 tài liệu. Golden set hiện cho Hit@1 100.0% và Hit@4 100.0%; corrupted lần lượt 40.0% và 60.0%. Hai câu challenge không có đáp án đều được từ chối đúng.

Artifact liên quan:

- [src/retrieval/embeddings.py](../src/retrieval/embeddings.py)
- [src/retrieval/index.py](../src/retrieval/index.py)
- [src/retrieval/qa.py](../src/retrieval/qa.py)
- [src/retrieval/llm.py](../src/retrieval/llm.py)
- [data/embeddings/papers_embeddings.json](../data/embeddings/papers_embeddings.json)
- [data/embeddings/papers_embeddings_corrupted.json](../data/embeddings/papers_embeddings_corrupted.json)
- [data/embeddings/papers_embeddings_repaired.json](../data/embeddings/papers_embeddings_repaired.json)
- [data/results/baseline_answers.json](../data/results/baseline_answers.json)

Sự tồn tại của artifact là bằng chứng về trạng thái dự án, không tự động chứng minh quyền tác giả của một thành viên.

## 4. Bàn giao và phối hợp

Bàn giao ba persisted indexes, manifest và hàm search/QA cho evaluation, pipeline và dashboard.

## 5. Cách tái hiện

- Nạp manifest baseline và kiểm tra collection count bằng 24.
- Chạy 10 golden questions và đối chiếu retrieved_doc_ids với ground_truth_doc_ids.
- Dùng script/run_rag.py để kiểm tra truy vấn DOI/tiêu đề và câu không có tài liệu nguồn.

## 6. Giới hạn và câu hỏi thuyết trình

**Giới hạn:** Golden set nhỏ và đã tham gia quá trình cải thiện retrieval; cần tập holdout độc lập hoặc corpus lớn hơn để kiểm tra khả năng tổng quát. Chế độ Gemini chưa có artifact do chưa cấu hình API key trong .env.

**Câu hỏi có thể gặp:** Nếu được hỏi lý do dùng hybrid retrieval: dense search bắt ngữ nghĩa, còn BM25 và exact match giúp phân biệt DOI/tiêu đề gần nhau trong corpus có nhiều paper cùng chủ đề.

## 7. Xác nhận nội dung cá nhân

Trước khi nộp, người đứng tên cần đối chiếu mô tả công việc với phần mình thực hiện và lịch sử commit trên nhánh nộp bài. Nếu phân công khác đóng góp thực tế, sửa báo cáo này và TEAM.md cho khớp.

Số liệu toàn nhóm được đối chiếu tại [group_report.md](group_report.md).
