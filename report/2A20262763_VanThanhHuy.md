# Báo cáo cá nhân — Văn Thành Huy

> Bản nháp theo phân công nhóm. Người đứng tên cần rà phần việc thực tế, bổ sung commit/minh chứng cá nhân và xác nhận trước khi nộp.

## Thông tin và vai trò

- Họ và tên: **Văn Thành Huy**
- MSSV: **2A20262763**
- Nhóm/lớp: KRAFTON · K4-L3B
- Vai trò được phân công: **Ingestion, raw lineage và cleaning**
- Tỷ trọng phân công đề xuất: **20%**

## Phạm vi được phân công

**Đầu vào:** Crossref API payload hoặc snapshot data/raw/crossref_response.json.

1. Kiểm tra parse DOI, tiêu đề, abstract, tác giả, chủ đề và ngày xuất bản trong src/ingestion/crossref.py.
2. Duy trì hai raw artifacts và fallback local khi không tải được payload mới.
3. Chuẩn hóa JATS/whitespace, bỏ DOI trùng, tính age_days và tạo text_for_embedding trong src/ingestion/cleaning.py.

**Bàn giao:** Bàn giao schema sạch và raw snapshot cho index, quality checks và repair.

## Artifact hiện có để đối chiếu

- [data/raw/crossref_response.json](../data/raw/crossref_response.json)
- [data/raw/crossref_records.json](../data/raw/crossref_records.json)
- [data/clean/papers_clean.csv](../data/clean/papers_clean.csv)
- [data/clean/papers_clean.json](../data/clean/papers_clean.json)

Các artifact trên chứng minh trạng thái repository; chỉ riêng sự tồn tại của chúng không chứng minh ai đã viết mã hoặc chạy thí nghiệm.

## Cách kiểm chứng phần việc

Đối chiếu 24 raw records với 24 clean records; xác nhận paper_id không rỗng và không trùng.

## Tự xác nhận trước khi nộp

- [ ] Tôi đã thực hiện hoặc review đúng các mục được ghi trong báo cáo này.
- [ ] Tôi đã đối chiếu commit của mình trên nhánh nộp bài.
- [ ] Tôi có thể giải thích input, output, giới hạn và cách kiểm chứng của phần việc.
- [ ] Tôi đã sửa các mục không đúng với đóng góp thực tế của mình.

Báo cáo kết quả chung và các số liệu cập nhật nằm ở [group_report.md](group_report.md).
