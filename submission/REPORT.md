# Báo cáo Day 09 — Nguyễn Cao Ngọc Đức, 2A202603178

Lớp L2 · Email: 26ai.ducncn@vinuni.edu.vn

## 1. Kết luận trước

Pipeline hiện kết luận **Hold**: nhận 205/224 ảnh, loại 19/224 ảnh ở intake. Sau sửa tự động và 80 lượt duyệt **mô phỏng theo script của đề**, không còn lỗi bắt buộc nhưng còn 38/205 ảnh cảnh báo chưa duyệt (18.54%), vượt ngưỡng 10%. `submission/export/clean_v1` chứa 205 ảnh trong manifest; đây là bản nháp phục vụ thử nghiệm, chưa đủ điều kiện phát hành. Nguồn: `reports/01_intake.csv`, `08_summary.json` và manifest.

## 2. Lỗi và phân việc

Nguồn: `reports/02_error_list_v1.csv` có 204 issue: 19 ở intake và 185 sau intake (36 error, 149 warn). Cột “Ảnh” là số stem riêng biệt cho từng mã; lỗi tên lớp dùng `data.yaml`, không phải một ảnh. Một ảnh có thể có nhiều issue nên không cộng cột ảnh thành tổng dataset.

| Mã lỗi | Issue/dòng | Ảnh/stem | Ai sửa | Xử lý |
|---|---:|---:|---|---|
| `BAD_CLASS_ID` | 6 | 6 | Máy | Xóa dòng có ID ngoài danh mục |
| `BAD_CLASS_NAME` | 2 | 1 | Máy | Chuẩn hóa names trong YAML |
| `BAD_FORMAT` | 3 | 3 | Máy | Xóa dòng không parse được |
| `BAD_SIZE` | 3 | 3 | Máy | Loại ảnh dưới kích thước tối thiểu |
| `BOX_HUGE` | 3 | 3 | Người | Cảnh báo cần đối chiếu, không tự sửa ngữ nghĩa |
| `BOX_OUT_OF_IMAGE` | 8 | 8 | Máy | Cắt box, kiểm lại diện tích |
| `BOX_TINY` | 6 | 4 | Người | Cảnh báo cần đối chiếu, không tự sửa ngữ nghĩa |
| `BOX_ZERO` | 4 | 4 | Máy | Xóa dòng có kích thước không dương |
| `CLASS_RARE` | 4 | 1 | Người | Cảnh báo cần đối chiếu, không tự sửa ngữ nghĩa |
| `CORRUPT_IMAGE` | 2 | 2 | Máy | Loại ảnh hỏng ở intake |
| `DUP_BOX` | 7 | 7 | Máy | Xóa dòng box lặp cùng lớp |
| `DUP_IMAGE_EXACT` | 8 | 8 | Máy | Loại bản trùng byte |
| `DUP_IMAGE_NEAR` | 2 | 2 | Máy | Loại cặp gần trùng theo ngưỡng đã chọn |
| `EMPTY_LABEL` | 12 | 12 | Người | Cảnh báo cần đối chiếu, không tự sửa ngữ nghĩa |
| `LEAK_TEST` | 4 | 4 | Máy | Loại ảnh rò rỉ sang kho test/val |
| `MISSING_LABEL_FILE` | 6 | 6 | Người | Chuyển người gán, không tạo nhãn rỗng |
| `POSSIBLE_FALSE_POS` | 25 | 24 | Người | Cảnh báo cần đối chiếu, không tự sửa ngữ nghĩa |
| `POSSIBLE_LOOSE_BOX` | 28 | 24 | Người | Cảnh báo cần đối chiếu, không tự sửa ngữ nghĩa |
| `POSSIBLE_MISSING` | 53 | 52 | Người | Cảnh báo cần đối chiếu, không tự sửa ngữ nghĩa |
| `POSSIBLE_WRONG_CLASS` | 18 | 18 | Người | Cảnh báo cần đối chiếu, không tự sửa ngữ nghĩa |

`03_fixes.csv` ghi 35 hành động: 20 drop_line, 8 clip_box, 1 rename_classes, 6 needs_label. needs_label là chuyển việc, chưa phải nhãn đã được sửa. Hàng đợi có 125 ảnh; chỉ 80/125 được mô phỏng duyệt. `img_0020` đứng đầu với priority 11.524 vì cộng trọng số FIXED_DROP_LINE, POSSIBLE_MISSING, POSSIBLE_WRONG_CLASS và conf; `img_0031` tiếp theo có NEEDS_LABEL, priority 10. Không thay đổi trọng số/ngân sách để ép Release.

## 3. Calibration (2 ngưỡng)

Nguồn: `calibration/calibration_report.md`, `calibration.json`, bộ calib 39 ảnh. Mỗi cặp số là precision / recall.

| Tham số | Khởi đầu | Đã chọn | Trước → sau | Lý do |
|---|---:|---:|---|---|
| duplicates.phash_dist | 2 | 4 | NEAR: 1.00/0.50 → 1.00/0.67 (3/6 → 4/6); EXACT: 1.00/1.00 giữ nguyên | Chọn ngưỡng nhỏ nhất cải thiện recall, ưu tiên precision vì ảnh bị loại tự động. |
| second_opinion.conf | 0.25 | 0.6 | WRONG_CLASS: 0.56/0.83 → 0.62/0.83; MISSING: 0.50/1.00 → 0.57/1.00 | Giảm báo động giả nhưng giữ recall nhầm lớp và thiếu nhãn trên calib; chấp nhận đánh đổi LOOSE 0.29/0.40 → 0.20/0.20. |

FALSE_POS vẫn 0.36/1.00 vì nhánh này dùng fp_conf=0.1 cố định, không dùng conf đang calibrate. Không chọn 0.8 chỉ để bớt hàng đợi: recall MISSING giảm còn 0.75. Đây là quyết định kỹ thuật cần được đọc và xác thực cùng kết quả thực tế.

Điểm dễ bị đánh lừa: phash=16 vẫn đạt precision NEAR 1.00 và recall 5/6 trên calib, nhưng trên raw số cờ duplicates/leak tăng từ 14 (ngưỡng 4) lên 26; ngưỡng 20 tăng tới 134/224. Đây là độ nhạy, **không chứng minh các cặp tăng thêm đều sai**: cần người mở cặp ảnh để xác nhận. Calib không có LEAK_TEST và chỉ 6 ca NEAR, nên không suy rộng precision của calib thành bảo đảm xóa đúng trên raw. Kết quả kiểm độ nhạy lưu ở `work/setup/duplicate_sensitivity.json`.

## 4. Cửa chặn và điều pipeline không bắt được

Thử nghiệm: `python -m pipeline.run --budget 0 --work work/no-review --reports work/rep_nb --export-dir work/exp_nb`. Kết quả **Rework**, 6 error MISSING_LABEL_FILE còn lại, mã thoát **20**, không có `work/exp_nb/clean_v1/manifest.json`. Không tăng ngân sách hoặc bỏ ảnh thiếu nhãn để né cửa chặn.

Các giới hạn có bằng chứng: (1) checker bỏ sót 1/6 ca WRONG_CLASS và 4/5 ca LOOSE_BOX chèn trong calib ở conf=0.6; hai model thống nhất không đồng nghĩa nhãn đúng. (2) phash=4 bỏ sót 2/6 ca NEAR trên calib; biến đổi mạnh có thể lọt. (3) 71 cảnh báo vẫn có mặt ở v3, gồm cả ảnh người mô phỏng đã duyệt; không coi model checker là ground truth để tự sửa tiếp.

**Quan sát cá nhân:** đã kiểm 10 ảnh trong trang `work/viz/index.html` và ghi ba trường hợp dưới đây. Nguồn ghi chú gốc: [`observations/day09-observations.json`](observations/day09-observations.json).

| Ảnh | Quan sát khi xem nhãn raw | Hướng xử lý đề xuất |
|---|---|---|
| `img_0001` | Thiếu người mặc quân phục ở giữa box 2 và 3. | Bổ sung box `person` ôm phần người nhìn thấy. |
| `img_0005` | Người lái xe bus chưa có nhãn. | Bổ sung box `person` cho người lái theo phần nhìn thấy. |
| `img_0007` | Còn ô tô chưa được gán nhãn. | Kiểm từng ô tô còn thiếu và bổ sung box `car`. |

Đối chiếu log tự động: `img_0001` có POSSIBLE_MISSING ở v1 và được đưa vào 80 lượt duyệt mô phỏng; v3 không còn issue của ảnh này. `img_0005` và `img_0007` không bị loại ở intake và không có cảnh báo trong v1: quan sát của người chỉ ra các ca cần kiểm thêm dù checker im lặng. Chưa có box sửa/đối chiếu chuẩn riêng cho hai ca này, nên không suy thành tỷ lệ bỏ sót của checker. Ba ghi chú là đánh giá nhãn raw, chưa phải bằng chứng đã sửa nhãn của bản export; không thay đổi số reviewed hoặc kết luận Hold.

**Đọc hiểu code:** chưa xác nhận đã đọc hiểu toàn bộ bốn module; cần hoàn thành riêng yêu cầu này trước khi chốt báo cáo.

## 5. Train: raw vs clean (tùy chọn, chấm riêng)

**Chưa chạy.** Hiện hoàn thiện phần pipeline lõi trước; chưa tải thêm trọng số hoặc tạo kết quả train. Không có căn cứ kết luận clean giúp mAP tốt hơn raw. Muốn đánh giá cần cùng model, 20 epoch, val/test, batch và hai seed 0/1 cho cả raw/clean, rồi so mức chênh với độ lệch giữa seed bằng script chính thức.

## 6. Quyết định và ghi chú AI

Giữ **Hold**. Điều kiện đổi sang Release: hết error và tỷ lệ ảnh cảnh báo chưa duyệt dưới 10% theo quy tắc cố định; trên mẫu số 205 cần còn tối đa 20 ảnh cảnh báo, tức xử lý thêm ít nhất 18 ảnh trong nhóm 38. Đây là nhu cầu quy trình ở vòng tiếp theo, không phải quyền tăng budget=80 trong bài hoặc tự đánh dấu reviewed. Phần duyệt hiện tại là mô phỏng, không thay thế xác thực cá nhân ở mục 4.

- Prompt chính: triển khai 4 stub theo docstring/test; đầu vào Dataset YOLO `id cx cy w h` và cache `[id,conf,cx,cy,w,h]`; trả Issue hoặc log sửa; checks/gate chỉ đọc, autofix chỉ sửa bản sao, không sửa data/tests/file đã viết sẵn, không đọc đáp án raw và không cố định tên ảnh trong code.
- Kiểm chứng đã thực hiện bằng công cụ: baseline 55 failed/24 passed → **79 passed**; chạy ba ca tổng hợp bổ sung (một dòng có hai lỗi + dòng trống, ID vô hạn, nhiều prediction); hai sweep; pipeline chính; thí nghiệm gate budget=0. Đã tự xem 10 ảnh và ghi ba ca ở mục 4; phần đọc hiểu bốn module vẫn cần xác nhận.
- Một lần AI sai: đoạn trợ giúp in summary được chạy trước khi bật PYTHONUTF8, gây UnicodeEncodeError ở console Windows. Đã bật PYTHONUTF8=1 và thêm vào launcher PowerShell; không chỉnh số liệu sinh tự động để che lỗi. Các file báo cáo chính sinh bởi script của đề, không sửa tay. Kiểm core trên Windows bộc lộ lỗi đường dẫn bảo vệ và CRLF trong script đề; chuyển chạy nguyên bản qua Ubuntu có sẵn thay vì sửa trình kiểm.
