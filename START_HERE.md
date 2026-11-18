# Day09 — hướng dẫn làm và xác thực

Nguyễn Cao Ngọc Đức · 2A202603178 · L2 · 26ai.ducncn@vinuni.edu.vn

## Trạng thái

Đã triển khai 4 module, 79 test chính thức đạt, kiểm đầy đủ gồm train 0 lỗi, 0 cảnh báo (xem docs/VERIFICATION.md); chạy 2 sweep, pipeline chính và thử nghiệm ngân sách duyệt bằng 0. Pipeline kết luận **Hold**. Duyệt 80 ảnh trong kết quả là **mô phỏng theo đề**, không phải xác nhận bạn đã xem 80 ảnh.

Repo có sẵn dữ liệu và dự đoán checker. Venv Windows nhẹ dùng lại thư viện hệ thống, chỉ bổ sung ImageHash/PyWavelets. Trình kiểm bài của đề có lỗi đường dẫn Windows và khác biệt checksum CRLF, nên launcher chính dùng Ubuntu hiện có + venv `/root/.venvs/day09-qc` để chạy nguyên bản; không sửa script kiểm. Không cần tải model, bật CVAT hoặc hoàn thành Day08 trước.

## Bạn cần làm ngay

1. **Đã hoàn thành:** kiểm 10 ảnh và gửi ba ghi chú ở img_0001, img_0005, img_0007; bản gốc lưu tại `submission/observations/day09-observations.json`, đã đưa vào REPORT mục 4.
2. **Đã hoàn thành:** đã đọc phần giải thích và ví dụ của bốn module, xác nhận hiểu code.
3. Quan sát và đọc hiểu đã xác nhận. Đã train raw/clean hai seed cùng cấu hình; bảng kết quả trong `submission/results/comparison.md`. Kết luận QC vẫn là Hold.

Ảnh chỉ xử lý tại máy bằng script trực quan hóa của đề; không tải ảnh COCO lên dịch vụ AI bên ngoài. Màu box: car xanh dương, person đỏ, truck cam, bus tím. Nhãn không parse được có thể không hiển thị.

## Bốn module làm gì?

### 1. `pipeline/checks/label_format.py`

Mỗi dòng YOLO là `class cx cy w h`, tọa độ chuẩn hóa 0–1. Ví dụ `1 .5 .5 .2 .3`: lớp person, tâm giữa ảnh, rộng 20%, cao 30% ảnh. Module đọc lần lượt từng dòng, giữ số dòng gốc, kiểm đủ cột và số hữu hạn, ID lớp, kích thước dương, tràn biên, box trùng cùng lớp, box quá nhỏ/quá lớn. Một dòng hỏng được báo lại rồi tiếp tục kiểm dòng khác. Đây là kiểm quy tắc, không chứng minh vật trong ảnh là người hay xe.

### 2. `pipeline/steps/gate.py`

Còn bất kỳ lỗi bắt buộc nào → Rework. Hết lỗi bắt buộc nhưng tỷ lệ ảnh còn cảnh báo chưa duyệt đạt 10% → Hold; thấp hơn → Release. Tỷ lệ tính theo ảnh khác nhau, không theo số cảnh báo. Ảnh đã duyệt chỉ được bỏ cảnh báo khỏi tỷ lệ, không được che lỗi bắt buộc. Ví dụ 38/205 = 18.54% → Hold.

### 3. `pipeline/steps/autofix.py`

Chỉ sửa bản sao làm việc. Xóa dòng sai cấu trúc/ID/kích thước rỗng/trùng; cắt box tràn vào ảnh; sửa tên lớp trong YAML; loại ảnh không đạt ở bước intake. Mỗi thay đổi có trước/sau trong log. Gom lỗi theo số dòng gốc để xóa nhiều dòng không làm lệch vị trí. Một dòng vừa trùng vừa tràn thì xóa một lần. Ảnh thiếu file nhãn được chuyển người gán, không tạo file rỗng giả vờ ảnh nền. Cảnh báo ngữ nghĩa không tự sửa.

### 4. `pipeline/checks/second_opinion.py`

So box nhãn với dự đoán checker YOLO26l đã lưu. Lọc dự đoán theo điểm tin cậy và diện tích rồi đo IoU. Không có box nhãn tương ứng → nghi thiếu; có cùng lớp nhưng lệch → nghi box lỏng; box trùng vị trí nhưng khác lớp → nghi nhầm lớp. Theo chiều ngược lại, nhãn không khớp dự đoán nào → nghi box thừa. Tất cả đều là WARN vì model có thể sai; cần người kiểm. Một ảnh có thể có nhiều cảnh báo.

## Chạy lại

PowerShell trong repo:

```powershell
.\run-day09.ps1 test
.\run-day09.ps1 calibrate
.\run-day09.ps1 run
.\run-day09.ps1 check-core
.\.venv\Scripts\python.exe scripts/verify_additional_cases.py
.\.venv\Scripts\python.exe scripts/prepare_review_gallery.py
```

`run` giữ mã thoát thật: 0 Release, 10 Hold, 20 Rework, 30 chờ người duyệt. Mã 10 trong bài hiện tại là kết luận chất lượng, không phải script bị hỏng.

Train raw/clean hai seed là phần tùy chọn riêng 15 điểm; đã hoàn thành trên RTX 4060 với YOLO26n và runtime 8.4.214. Xem `docs/TRAINING.md`. Repo giữ tên học viên trước MSHV theo yêu cầu: https://github.com/ducnguyen-ai/K5-L23-Day09-NguyenCaoNgocDuc-2A202603178-AutoQC-Pipeline-Lab. Tên thư mục local tạm giữ nguyên để không làm hỏng đường dẫn công cụ.

## Sau bài và phần bonus

Xem [kiến thức cần nắm, ví dụ Hold và trạng thái bonus](docs/LEARNING_NOTES.md). Bài chính và train đã có đầu ra; hai mục thưởng +3 check mới và +2 CVAT hiện chưa làm.
