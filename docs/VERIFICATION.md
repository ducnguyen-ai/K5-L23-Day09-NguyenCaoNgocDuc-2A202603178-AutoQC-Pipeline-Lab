# Kiểm chứng phần lõi Day09 — 18/11/2026

- Repo: https://github.com/ducnguyen-ai/K5-L23-Day09-NguyenCaoNgocDuc-2A202603178-AutoQC-Pipeline-Lab
- Môi trường kiểm cuối: Ubuntu hiện có, Python 3.12, dependency tại `requirements-core.lock.txt`.
- Các file được bảo vệ, tests và dữ liệu của đề giữ nguyên; checker chính thức chạy nguyên bản trong Linux.
- Baseline: 55 failed, 24 passed. Sau triển khai: Windows 79 passed; Linux lượt kiểm đầy đủ cuối **79 passed trong 157.52 giây**.
- `scripts/verify_additional_cases.py`: cả 3 ca bổ sung đạt trên Windows và Linux.
- `./run-day09.ps1 run`: **Hold**, exit 10, nhận 205/224 ảnh, 0 lỗi bắt buộc cuối, 38/205 ảnh cảnh báo chưa duyệt, tỷ lệ 0.1854.
- Thử nghiệm budget=0: **Rework**, exit 20, 6 lỗi thiếu file nhãn, không có manifest xuất ở thư mục thử nghiệm riêng.
- `./run-day09.ps1 check`: **0 lỗi, 0 cảnh báo**, bao gồm phần train.
- Bốn lượt train bằng script gốc: raw/clean × seed 0/1, cùng YOLO26n, 20 epoch, batch 16, ảnh 640, val 40/test 100. Đã kiểm đủ epoch và checksum cấu hình/manifest/trọng số.
- mAP50: raw 0.7232 ± 0.0064, clean 0.7055 ± 0.0066; Δ=-0.0177. Kết quả không ủng hộ claim clean cải thiện mAP; báo cáo giữ Hold và phân tích giới hạn.
- Log chi tiết trên máy: `work/setup/baseline-tests.txt`, `pipeline-linux.log`, `check-core-linux.log`, `check-full.log`, `train.log`, `additional_cases.txt`, `no-review.log` (work không commit).

Đã xác nhận kiểm 10 ảnh và tiếp nhận ba ghi chú gốc tại `submission/observations/day09-observations.json`; đã cập nhật REPORT mục 4. Đã xác nhận hiểu bốn module sau khi được giải thích bằng ví dụ. 80 lượt duyệt của pipeline vẫn là mô phỏng, không đổi thành 80 ảnh học viên đã duyệt.
