# Báo cáo Day 09 — Nguyễn Cao Ngọc Đức, 2A202603178

Lớp L2 · Email: 26ai.ducncn@vinuni.edu.vn

## 1. Kết luận trước

**Hold**: nhận 205/224 ảnh, loại 19 ở intake. Sau sửa tự động và 80 lượt duyệt **mô phỏng**, còn 0 error nhưng 38/205 ảnh cảnh báo chưa duyệt (18.54%), vượt ngưỡng 10%. Export clean_v1 gồm 205 ảnh là bản nháp để thử nghiệm, chưa phát hành. Nguồn: `reports/08_summary.json`, `export/clean_v1/manifest.json`. Train hai seed chưa cho thấy lợi ích mAP của clean (§5).

## 2. Lỗi và phân việc

`reports/02_error_list_v1.csv`: 204 issue = 19 intake + 185 sau intake (36 error, 149 warn). Mỗi ảnh có thể có nhiều issue; “Ảnh/stem” của BAD_CLASS_NAME và CLASS_RARE là data.yaml hoặc cấp dataset, không phải ảnh.

| Mã lỗi | Issue/dòng | Ảnh/stem | Ai sửa | Vì sao/cách sửa |
|---|---:|---:|---|---|
| `BAD_CLASS_ID` | 6 | 6 | Máy | Bỏ ID lạ |
| `BAD_CLASS_NAME` | 2 | 1 | Máy | Sửa names |
| `BAD_FORMAT` | 3 | 3 | Máy | Bỏ dòng hỏng |
| `BAD_SIZE` | 3 | 3 | Máy | Loại ảnh nhỏ |
| `BOX_HUGE` | 3 | 3 | Người | Kiểm ý nghĩa |
| `BOX_OUT_OF_IMAGE` | 8 | 8 | Máy | Cắt về biên |
| `BOX_TINY` | 6 | 4 | Người | Kiểm ý nghĩa |
| `BOX_ZERO` | 4 | 4 | Máy | Bỏ box rỗng |
| `CLASS_RARE` | 4 | 1 | Người | Kiểm ý nghĩa |
| `CORRUPT_IMAGE` | 2 | 2 | Máy | Loại ảnh hỏng |
| `DUP_BOX` | 7 | 7 | Máy | Bỏ box lặp |
| `DUP_IMAGE_EXACT` | 8 | 8 | Máy | Loại trùng byte |
| `DUP_IMAGE_NEAR` | 2 | 2 | Máy | Loại gần trùng |
| `EMPTY_LABEL` | 12 | 12 | Người | Kiểm ý nghĩa |
| `LEAK_TEST` | 4 | 4 | Máy | Loại rò rỉ test |
| `MISSING_LABEL_FILE` | 6 | 6 | Người | Gán nhãn thật |
| `POSSIBLE_FALSE_POS` | 25 | 24 | Người | Kiểm ý nghĩa |
| `POSSIBLE_LOOSE_BOX` | 28 | 24 | Người | Kiểm ý nghĩa |
| `POSSIBLE_MISSING` | 53 | 52 | Người | Kiểm ý nghĩa |
| `POSSIBLE_WRONG_CLASS` | 18 | 18 | Người | Kiểm ý nghĩa |

`03_fixes.csv`: 20 drop_line, 8 clip_box, 1 rename_classes, 6 needs_label; needs_label chỉ chuyển việc, chưa sửa nhãn. Máy chỉ sửa lỗi có quy tắc; người quyết định cảnh báo ngữ nghĩa. Hàng đợi có 125 ảnh, mô phỏng duyệt 80. img_0020 đầu hàng (11.524) do cộng trọng số sửa dòng, thiếu vật, nhầm lớp và conf; img_0031 có NEEDS_LABEL (10). Không tăng budget hoặc đổi weights để đạt Release.

## 3. Calibration hai ngưỡng

Nguồn: `calibration/calibration_report.md`, `calibration.json` (39 ảnh); P/R = precision/recall.

| Tham số | Khởi đầu → chọn | P/R trước → sau | Đánh đổi |
|---|---|---|---|
| phash_dist | 2 → 4 | NEAR: 1.00/0.50 → 1.00/0.67 (3/6 → 4/6); EXACT giữ 1.00/1.00 | Ngưỡng nhỏ nhất cải thiện recall; ưu tiên precision vì cờ sai sẽ loại nhầm ảnh. |
| second_opinion.conf | 0.25 → 0.6 | WRONG_CLASS: 0.56/0.83 → 0.62/0.83; MISSING: 0.50/1.00 → 0.57/1.00 | Bớt báo động giả, giữ recall hai nhóm này; chấp nhận recall LOOSE giảm 0.40 → 0.20. |

FALSE_POS vẫn 0.36/1.00 vì dùng fp_conf=0.1 cố định. Không chọn 0.8 để làm nhỏ hàng đợi: recall MISSING giảm còn 0.75.

**Điểm dễ bị đánh lừa:** phash=16 đạt NEAR P=1.00, R=5/6 trên calib nhưng số cờ duplicate/leak raw tăng 14 → 26; ngưỡng 20 tăng tới 134/224. Đây là độ nhạy, chưa chứng minh cặp tăng thêm đều sai; cần mở cặp ảnh. Calib chỉ có 6 ca NEAR và không có LEAK_TEST, nên không bảo đảm precision trên raw. Kiểm độ nhạy lưu ở `work/setup/duplicate_sensitivity.json`.

## 4. Gate, điểm mù và quan sát cá nhân

Thử `python -m pipeline.run --budget 0 --work work/no-review --reports work/rep_nb --export-dir work/exp_nb`: **Rework**, còn 6 MISSING_LABEL_FILE, exit **20**, không xuất manifest. Gate chặn thật, không tạo nhãn rỗng để né lỗi.

Điểm mù đo được: checker bỏ sót 1/6 WRONG_CLASS và 4/5 LOOSE_BOX trên calib ở conf=0.6; phash=4 bỏ sót 2/6 NEAR. Hai model thống nhất không chứng minh nhãn đúng. V3 còn 71 cảnh báo, gồm cả ảnh đã duyệt mô phỏng.

Đã tự kiểm 10 ảnh, ghi ba ca trong [`observations/day09-observations.json`](observations/day09-observations.json):

| Ảnh | Quan sát nhãn raw | Cách sửa đề xuất |
|---|---|---|
| img_0001 | Thiếu người mặc quân phục giữa box 2 và 3 | Thêm person |
| img_0005 | Thiếu người lái bus | Thêm person |
| img_0007 | Thiếu ô tô | Thêm car còn thiếu |

img_0001 được checker cờ POSSIBLE_MISSING, duyệt mô phỏng và hết issue ở v3. img_0005/0007 không bị loại intake, không có cờ v1: cần kiểm thêm dù checker im lặng, chưa coi là tỷ lệ FN được đo chuẩn. Ghi chú raw chưa phải chứng cứ sửa bản export; không cộng chúng vào số reviewed. Đã được giải thích bằng ví dụ và xác nhận hiểu bốn module.

## 5. Train raw vs clean

Script `train_compare.py` nguyên bản: YOLO26n, Ultralytics 8.4.214, 20 epoch, seed 0/1, batch 16, ảnh 640; cùng val 40 và test 100 ảnh, RTX 4060. Chi tiết: `docs/TRAINING.md`, `docs/training_runtime.json`. Loader nhận raw **213/224**, clean **205/205**; #ảnh trong bảng là số materialize do script ghi.

| biến thể | #ảnh train | số seed | map50 (TB ± độ lệch) | map50_95 (TB ± độ lệch) | precision (TB ± độ lệch) | recall (TB ± độ lệch) |
|---|---|---|---|---|---|---|
| raw | 224 | 2 | 0.723 ± 0.006 | 0.523 ± 0.012 | 0.822 ± 0.072 | 0.602 ± 0.036 |
| clean | 205 | 2 | 0.706 ± 0.007 | 0.516 ± 0.002 | 0.703 ± 0.013 | 0.612 ± 0.030 |

Chênh mAP50 (clean − raw) = **-0.018**.

Số chính xác: mAP50 raw **0.7232 ± 0.0064**, clean **0.7055 ± 0.0066**, Δ=**−0.0177** (−1.77 điểm phần trăm), lớn hơn từng độ lệch giữa seed; clean thấp ở cả hai seed. mAP50-95 giảm 0.0076, nhỏ hơn SD raw 0.0116. **Thí nghiệm này không ủng hộ kết luận clean tốt hơn raw**; hai seed/test 100 ảnh chưa đủ khẳng định tổng quát.

Hai giả thuyết cần kiểm tiếp: (1) raw có 4 ảnh rò rỉ vào test theo 01_intake.csv, có thể làm điểm raw lạc quan; cần test độc lập mới để kiểm. (2) clean thay đổi lượng/phân bố dữ liệu và thêm nhãn người ở 80 ảnh, trong khi loader raw đã tự bỏ 11 ca hỏng; hiệu ứng không chỉ là autofix. Cần ablation từng bước/auto-vs-human trên holdout mới. Không đổi ngưỡng, seed hoặc epoch dựa vào test vừa đo.

## 6. Quyết định và ghi chú AI

Giữ **Hold**. Muốn Release phải hết error và còn tối đa 20/205 ảnh cảnh báo chưa duyệt, tức xử lý thêm ít nhất 18 trong nhóm 38; đây là việc vòng sau, không tăng budget=80 hoặc tự đánh dấu reviewed trong bài. mAP không thay thế gate QC.

- **Prompt:** 4 stub theo docstring/test; đầu vào YOLO `id cx cy w h` và cache dự đoán; đầu ra Issue/log sửa. Checks/gate chỉ đọc, autofix sửa bản sao; không sửa data/tests/file bảo vệ, không đọc đáp án raw hoặc cố định tên ảnh trong code.
- **Kiểm:** baseline 55 failed/24 passed → 79 passed; ba ca bổ sung; hai sweep; pipeline; gate budget=0; tự xem 10 ảnh; xác nhận hiểu module; bốn lượt train cùng cấu hình. File số liệu do script sinh, không sửa tay.
- **AI sai và sửa:** tái dùng môi trường GPU thiếu Polars khiến lượt train đầu dừng khi lưu checkpoint; bổ sung thư viện, giữ log lỗi và chạy lại từ đầu, không dùng kết quả dở. Lỗi đường dẫn/CRLF của checker Windows được xử lý bằng chạy nguyên bản trên Ubuntu; không sửa trình chấm.
