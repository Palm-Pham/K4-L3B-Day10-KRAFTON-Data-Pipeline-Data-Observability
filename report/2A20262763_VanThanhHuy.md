# Báo cáo cá nhân — Văn Thành Huy

**MSSV:** 2A20262763 · **Nhóm:** KRAFTON · **Lớp:** K4-L3B
**Vai trò theo phân công:** Ingestion, raw lineage và cleaning · **Tỷ trọng phân công:** 20%

Báo cáo này trình bày đầy đủ phạm vi vai trò và kết quả kỹ thuật có thể kiểm tra trong repository. Phần ai trực tiếp viết mã, chạy thí nghiệm và các commit cá nhân cần được người đứng tên đối chiếu trước khi nộp.

## 1. Mục tiêu và đầu vào

Mục tiêu của vai trò là ingestion, raw lineage và cleaning. Đầu vào: Crossref API payload hoặc raw snapshot lưu trong data/raw/.

## 2. Công việc và cách triển khai

1. Phân tích response Crossref thành PaperRecord; giữ DOI, tiêu đề, abstract, tác giả, chủ đề, ngày công bố và URL.
2. Khi REFRESH_SOURCE được bật, mã thử tải API tối đa ba lần với timeout 10 giây. Nếu không có response mới, pipeline đọc snapshot local.
3. Làm sạch JATS/XML và khoảng trắng, loại bản ghi thiếu DOI/tiêu đề, khử trùng lặp theo paper_id, tính age_days và ghép text_for_embedding từ 5 thành phần.

**Quyết định kỹ thuật:** Giữ raw response và parsed records riêng để có thể truy ngược nguồn; tạo clean dataset từ raw thay vì sửa trực tiếp snapshot. Cleaned rows được sắp theo ngày công bố giảm dần, tạo đầu vào ổn định cho index và corruption.

## 3. Kết quả kiểm chứng

Repository có 24 raw records và 24 clean records. Clean schema chứa paper_id, title, summary, authors_joined, categories_joined, published, age_days và text_for_embedding. Số liệu này mô tả artifact hiện có, chưa tự chứng minh tác giả của các commit.

Artifact liên quan:

- [src/ingestion/crossref.py](../src/ingestion/crossref.py)
- [src/ingestion/cleaning.py](../src/ingestion/cleaning.py)
- [data/raw/crossref_response.json](../data/raw/crossref_response.json)
- [data/raw/crossref_records.json](../data/raw/crossref_records.json)
- [data/clean/papers_clean.json](../data/clean/papers_clean.json)
- [data/clean/papers_clean.csv](../data/clean/papers_clean.csv)

Sự tồn tại của artifact là bằng chứng về trạng thái dự án, không tự động chứng minh quyền tác giả của một thành viên.

## 4. Bàn giao và phối hợp

Bàn giao raw snapshot cho luồng repair; bàn giao clean CSV/JSON và schema cho embedding, quality checks và golden evaluation.

## 5. Cách tái hiện

- Đếm 24 raw records và 24 clean rows; so sánh tập DOI giữa hai file.
- Kiểm tra paper_id/title không rỗng, DOI duy nhất và text_for_embedding có đủ Title, Authors, Published, Categories, Summary.
- Chạy Phase 1 với REFRESH_SOURCE=0 để tái hiện từ local snapshot, tránh thay đổi corpus trước lúc demo.

## 6. Giới hạn và câu hỏi thuyết trình

**Giới hạn:** Chế độ tải API mới phụ thuộc mạng và có thể trả về corpus khác; golden set hiện được cố định theo snapshot 24 bài. Cần tạo benchmark mới nếu refresh dữ liệu nguồn.

**Câu hỏi có thể gặp:** Nếu được hỏi vì sao phải giữ raw snapshot: nó là mốc lineage và nguồn tái tạo sau corruption; cleaned data có thể tính lại từ raw mà không cần đoán ngược giá trị đã bị sửa.

## 7. Xác nhận nội dung cá nhân

Trước khi nộp, người đứng tên cần đối chiếu mô tả công việc với phần mình thực hiện và lịch sử commit trên nhánh nộp bài. Nếu phân công khác đóng góp thực tế, sửa báo cáo này và TEAM.md cho khớp.

Số liệu toàn nhóm được đối chiếu tại [group_report.md](group_report.md).
