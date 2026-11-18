# Kiểm chứng phần lõi Day09 — 18/11/2026

- Repo: https://github.com/ducnguyen-ai/K5-L23-DAY09-2A202603178-AutoQCPipeline
- Môi trường kiểm cuối: Ubuntu hiện có, Python 3.12, dependency tại `requirements-core.lock.txt`.
- Các file được bảo vệ, tests và dữ liệu của đề giữ nguyên; checker chính thức chạy nguyên bản trong Linux.
- Baseline: 55 failed, 24 passed. Sau triển khai: Windows 79 passed; Linux **79 passed trong 144.70 giây**.
- `scripts/verify_additional_cases.py`: cả 3 ca bổ sung đạt trên Windows và Linux.
- `./run-day09.ps1 run`: **Hold**, exit 10, nhận 205/224 ảnh, 0 lỗi bắt buộc cuối, 38/205 ảnh cảnh báo chưa duyệt, tỷ lệ 0.1854.
- Thử nghiệm budget=0: **Rework**, exit 20, 6 lỗi thiếu file nhãn, không có manifest xuất ở thư mục thử nghiệm riêng.
- `./run-day09.ps1 check-core`: **0 lỗi, 1 cảnh báo**. Cảnh báo là bỏ qua train tùy chọn; chưa có kết quả train để chấm phần 15 điểm này.
- Log chi tiết trên máy: `work/setup/baseline-tests.txt`, `pipeline-linux.log`, `check-core-linux.log`, `additional_cases.txt`, `no-review.log` (work không commit).

Chưa xác nhận hoàn thành quan sát/đọc hiểu cá nhân. Học viên cần xem trang `work/viz/index.html`, ghi ít nhất ba lỗi và đọc bốn module trước khi chốt báo cáo. Không gọi 80 lượt duyệt mô phỏng là 80 ảnh học viên đã duyệt.
