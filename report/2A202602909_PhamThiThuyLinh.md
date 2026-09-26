# Báo cáo cá nhân — Phạm Thị Thùy Linh

**MSSV:** 2A202602909 · **Nhóm:** KRAFTON · **Lớp:** K4-L3B
**Vai trò theo phân công:** Orchestration, dashboard và live demo · **Tỷ trọng phân công:** 20%

Báo cáo này trình bày đầy đủ phạm vi vai trò và kết quả kỹ thuật có thể kiểm tra trong repository. Phần ai trực tiếp viết mã, chạy thí nghiệm và các commit cá nhân cần được người đứng tên đối chiếu trước khi nộp.

## 1. Mục tiêu và đầu vào

Mục tiêu của vai trò là orchestration, dashboard và live demo. Đầu vào: Raw/clean artifacts, Chroma collections, golden set, quality/freshness reports và metrics.

## 2. Công việc và cách triển khai

1. Điều phối Phase 1: ingest, clean, index, chuẩn bị golden set, evaluate, chạy GX/freshness và xuất baseline report.
2. Đảm bảo corruption flow dùng cùng test set và kết quả repaired được so với baseline trước khi trình bày.
3. Dùng dashboard cục bộ để trình bày so sánh ba trạng thái, 6 corruption modes, quality/freshness signals và live retrieval.

**Quyết định kỹ thuật:** Dashboard đọc trực tiếp artifact JSON nên số liệu trình bày thay đổi theo lần chạy pipeline, không nhập tay. Live QA gọi metadata retrieval trên từng collection và chỉ nghe ở localhost.

## 3. Kết quả kiểm chứng

Dashboard hiển thị 24 clean papers, 10 golden questions và 6 corruption scenarios. Trên snapshot hiện tại, baseline/repaired đạt Hit@1 100.0%; corrupted còn 40.0%. Hit@4 lần lượt là 100.0%, 60.0%, 100.0%. Token F1 lần lượt là 1.0000, 0.7788, 1.0000. Hai script pipeline và dashboard đã có entrypoint riêng; Gemini key không cần cho live retrieval metadata.

Artifact liên quan:

- [src/pipelines/phase1.py](../src/pipelines/phase1.py)
- [script/run_phase1.py](../script/run_phase1.py)
- [script/run_corruption_flow.py](../script/run_corruption_flow.py)
- [script/run_dashboard.py](../script/run_dashboard.py)
- [dashboard/index.html](../dashboard/index.html)
- [dashboard/app.js](../dashboard/app.js)
- [data/reports/phase1_report.md](../data/reports/phase1_report.md)
- [data/reports/corruption_report.md](../data/reports/corruption_report.md)

Sự tồn tại của artifact là bằng chứng về trạng thái dự án, không tự động chứng minh quyền tác giả của một thành viên.

## 4. Bàn giao và phối hợp

Bàn giao lệnh chạy và kịch bản trình bày: mở dashboard, giải thích quality alert, chuyển ba trạng thái, chạy một câu golden và chỉ ra repaired phục hồi.

## 5. Cách tái hiện

- Chạy Phase 1 rồi corruption flow từ thư mục gốc với PYTHONPATH=src, PYTHONIOENCODING=utf-8, LLM_PROVIDER=mock, RUN_RAGAS=0.
- Mở dashboard tại http://127.0.0.1:8765; kiểm tra dữ liệu trên màn hình khớp data/results và data/quality.
- Trình diễn cùng một câu hỏi ở baseline/corrupted/repaired; nêu rõ câu trả lời là metadata QA, không phải Gemini.

## 6. Giới hạn và câu hỏi thuyết trình

**Giới hạn:** Dashboard là công cụ demo cục bộ, không phải hệ thống giám sát liên tục. Kết quả Gemini thật chưa có; quality gate hiện báo lỗi nhưng chưa tự kích hoạt repair.

**Câu hỏi có thể gặp:** Nếu được hỏi vì sao cần orchestration: thứ tự và schema artifact phải ổn định để baseline, corrupted và repaired dùng cùng golden set; nếu đổi câu hỏi giữa các trạng thái thì không còn phép so sánh công bằng.

## 7. Xác nhận nội dung cá nhân

Trước khi nộp, người đứng tên cần đối chiếu mô tả công việc với phần mình thực hiện và lịch sử commit trên nhánh nộp bài. Nếu phân công khác đóng góp thực tế, sửa báo cáo này và TEAM.md cho khớp.

Số liệu toàn nhóm được đối chiếu tại [group_report.md](group_report.md).
