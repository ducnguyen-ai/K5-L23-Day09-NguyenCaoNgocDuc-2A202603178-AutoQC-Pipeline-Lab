# Thí nghiệm raw và clean của Day09

Chạy tại GPU RTX 4060 Laptop 8 GB, dùng script train_compare.py nguyên bản. Phiên bản runtime và SHA256 trọng số ở `training_runtime.json`.

## Thiết kế

- Hai biến thể: raw (224 ảnh nguồn được materialize), clean (205 ảnh theo manifest pipeline, trạng thái Hold — bản nháp thử nghiệm).
- Mỗi biến thể chạy hai seed 0 và 1, 20 epoch, YOLO26n cùng checkpoint ban đầu, ảnh 640, batch 16, deterministic=True, patience=0.
- Cùng validation 40 ảnh để chọn best checkpoint; test 100 ảnh chỉ được đánh giá cuối mỗi lượt theo script chính thức. Không dùng điểm test để chọn ngưỡng QC, seed hoặc cấu hình train.
- Ultralytics 8.4.214 đúng requirements-train.txt; dùng lại torch CUDA hiện có. Trọng số yolo26n.pt là tệp cần cho thí nghiệm, không commit; không tải thêm các cỡ khác.
- Materializer chỉ sao chép dữ liệu vào work/train. Không sửa data/raw, gold_val, test hoặc nhãn tham chiếu để cải thiện điểm.
- Thực tế loader bỏ qua 11 ảnh/nhãn raw hỏng: 224 ảnh materialize, 213 ảnh được nhận; clean nhận đủ 205/205. train_images trong JSON chính thức vẫn là số ảnh materialize (224 hoặc 205), không sửa tay trường này. Cache của loader và log lưu bằng chứng số ảnh thực dùng.

## Lệnh trên máy hiện tại

```powershell
$env:PYTHONUTF8='1'
$env:YOLO_CONFIG_DIR=Join-Path (Get-Location).Path 'work/setup/ultralytics_config'
.\.venv-train\Scripts\python.exe scripts/train_compare.py --variants raw clean --seeds 0 1 --epochs 20 --batch 16 --imgsz 640 --device 0
.\.venv-train\Scripts\python.exe scripts/summarize_results.py
.\run-day09.ps1 check
```

Nếu chạy tiếp sau gián đoạn, thêm `--skip-existing`; không dùng cờ này để trộn các lượt có cấu hình khác nhau. Trọng số huấn luyện và log epoch nằm trong work/train/runs, không commit; JSON và bảng so sánh do script sinh trong submission/results được commit.

## Tái lập trên máy khác

Dùng hướng dẫn docs/COLAB.md và notebook gốc, hoặc tạo môi trường GPU riêng, cài requirements-train.txt rồi chạy cùng lệnh ở trên (đổi đường dẫn python/device phù hợp). Không cần những đường dẫn thư viện dùng lại riêng của máy hiện tại. Phần QC lõi dùng requirements-core.lock.txt/requirements.txt, tách khỏi môi trường train.

Khi đọc kết quả cần so chênh lệch trung bình với độ lệch giữa hai seed. Hai seed và test 100 ảnh không đủ để khẳng định ưu thế tổng quát; giữ nguyên kết luận Hold của QC dù mAP có cải thiện.

Launcher trên máy: `./run-day09.ps1 train` (chạy tiếp các lượt chưa có kết quả). Cấu hình logging riêng tắt sync và các dịch vụ theo dõi ngoài.
