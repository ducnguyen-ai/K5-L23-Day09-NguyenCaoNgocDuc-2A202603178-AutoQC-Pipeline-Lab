# Day09 — kiến thức cần nắm và kiểm tra phần thưởng

## Hai tài liệu bổ sung có liên quan gì?

- `Day09_AutoQC_Pipeline_Lab(1).pptx`: 14 trang PowerPoint chứa ảnh chụp các trang chọn từ bài giảng gốc 36 trang (số gốc in ở chân ảnh). Cùng nội dung repo: năm bước thực hành, bốn module, calibration, pipeline, train, report, checklist và thưởng. Không phải đề bài khác. Trang PowerPoint thứ 13, tương ứng trang gốc 33/36, nêu bonus +3 và +2.
- `hold-example.html`: ví dụ giảng dạy 22 ảnh → còn 20 sau intake, ngân sách duyệt 8, còn 5 ảnh WARN chưa duyệt; 5/20=25% nên Hold. Các số này không phải số chạy trên lô raw của bài nộp.
- Slide là sơ đồ tổng quan. Pipeline thực tế kiểm QC ba vòng: nhãn thô, sau autofix, sau duyệt; gate dùng kết quả vòng cuối.

## Kiến thức cần tự giải thích được

| Chủ đề | Cần hiểu | Áp dụng vào bài |
|---|---|---|
| Chất lượng dữ liệu và chất lượng code | Test xanh chứng minh các ca đã kiểm, không chứng minh mọi nhãn đúng. | 79 test đạt nhưng bộ dữ liệu vẫn Hold; quan sát của người ở img_0005/0007 còn chỉ ra ca checker không cờ. |
| Định dạng YOLO và hình học | `id cx cy w h`, tọa độ chuẩn hóa; biên trái/phải là cx±w/2, trên/dưới là cy±h/2. | cx=.95, w=.2 có biên phải 1.05, cần cắt theo quy tắc. Box có số hợp lệ vẫn có thể bao nhầm vật. |
| Phân công máy/người | Máy kiểm cú pháp/hình học và sửa theo quy tắc; model chỉ cảnh báo ý nghĩa; người quyết định ca mơ hồ. | Thiếu file nhãn → needs_label, không tạo file rỗng; rỗng nghĩa là ảnh nền/chưa rõ, khác với chưa có file. |
| Calibration checker | Đo TP/FP/FN trên lỗi đã biết; precision=TP/(TP+FP), recall=TP/(TP+FN). Đây không phải xác suất conf đã được hiệu chỉnh thống kê. | Chỉ chỉnh phash_dist và second_opinion.conf; chọn 4 và .6 có đánh đổi, không đổi ngưỡng gate/budget để ép Release. |
| Hai loại precision/recall | Calibration đo checker bắt lỗi nhãn. Train/test đo detector tìm vật. Không trộn hai phép đo. | P/R trong calibration.json không phải P/R trong comparison.json. |
| Trùng ảnh và rò rỉ dữ liệu | Hash byte tìm bản giống hệt; pHash tìm gần giống nhưng có thể gộp nhầm. Test phải giữ độc lập. | Raw có 4 ca trùng với test bị intake phát hiện; ngưỡng phash quá rộng làm số ảnh bị loại tăng mạnh. |
| Hàng đợi và gate | Ưu tiên theo loại lỗi/conf và ngân sách; tính tỷ lệ theo ảnh WARN chưa duyệt, không theo số issue hoặc chiều dài hàng. | 125 ảnh trong hàng, 80 duyệt mô phỏng, 45 chưa duyệt nhưng chỉ 38 còn WARN; 7 ca còn lại đã hết issue. |
| Autofix và truy vết | Chỉ sửa bản sao, giữ số dòng gốc, log before/after, xóa ưu tiên hơn clip; chạy lại không sửa thêm khi đã hết lỗi. | Dòng 3 vừa trùng vừa tràn chỉ bị xóa một lần, kể cả có dòng trống trước đó. |
| Thí nghiệm công bằng | Cùng model/checkpoint, epoch, seed, batch, val/test; không điều chỉnh theo kết quả test. | Raw/clean × seed 0/1, 20 epoch, YOLO26n; raw thực dùng 213/224, clean 205/205. |
| Đọc kết quả trung thực | So trung bình với dao động giữa seed; hai seed không tạo bảo đảm thống kê tổng quát. mAP không thay thế gate dữ liệu. | Raw mAP50=.7232±.0064, clean=.7055±.0066; Δ=-.0177. Kết quả không ủng hộ claim clean tốt hơn raw. |

## Vì sao bài này Hold dù đã calibrate?

- Nhận 224 ảnh, loại 19, mẫu số gate còn 205.
- Hàng đợi 125 ảnh; duyệt mô phỏng 80. Không coi 80 lượt này là 80 ảnh học viên đã tự xem.
- Gate cuối còn 0 ERROR và 38 ảnh WARN chưa duyệt: 38/205=.1854=18.54% ≥ 10% → Hold, exit 10.
- 45 ảnh chưa duyệt trong hàng không đồng nghĩa 45 ảnh còn cảnh báo: 7 ảnh không còn WARN không đi vào tử số.
- Release cần ít hơn 10%, tức tối đa 20/205 ảnh cảnh báo. Đúng 10% vẫn Hold. Cần xử lý thêm ít nhất 18 trong nhóm 38 ở vòng quy trình tiếp theo; không sửa budget=80 trong bài để né gate.
- Rework khi còn ERROR, kể cả ảnh đã duyệt. Hold được xuất bản nháp để train; Rework mặc định không xuất. Có file clean_v1 chưa có nghĩa được phát hành.
- Calibrate làm checker hữu ích hơn; không bảo đảm hết cảnh báo hoặc đủ ngân sách người duyệt.

## Bonus và phần tùy chọn

Theo RUBRIC.md và docs/CVAT_FILTER.md, thưởng tối đa +5, tổng điểm không vượt 100:

| Phần | Điểm tối đa | Điều kiện/bằng chứng | Trạng thái hiện tại |
|---|---:|---|---|
| Check mới | +3 | Một phép kiểm mới (ví dụ tỷ lệ khung hình bất thường) có test, quy tắc giải thích được. | Chưa triển khai. Ba ca bổ sung trong verify_additional_cases.py là kiểm code bắt buộc, không phải check mới. |
| CVAT lọc box nhỏ | +2 | Lọc width<20 trên ≥1 ảnh, ghi tên ảnh/số box, đối chiếu BOX_TINY, giải thích can_review và có ảnh chụp; làm kỹ hơn trên ≥5 ảnh. | Chưa có minh chứng CVAT cho Day09; không nhận là đã hoàn thành. |
| Train raw/clean | 15 trong thang 100 | Hai seed mỗi biến thể, so sánh cùng điều kiện, kết luận trung thực. | Đã hoàn thành. Đây là phần tùy chọn của điểm chính, không phải +15 bonus. |

CVAT width<20 và pipeline BOX_TINY khác nhau: pipeline dùng min(width,height)<12 px. Vì vậy hai tập box không bắt buộc trùng nhau; phải so theo đúng tiêu chí, không xóa mọi box nhỏ theo cảm tính. can_review dùng để chuyển ca khó/chưa chắc cho người kiểm; ý nghĩa tương tự hàng đợi cảnh báo trong pipeline, không phải công cụ xóa lỗi bắt buộc.

## Tự kiểm sau bài

1. Tại sao 79 test xanh mà Hold vẫn đúng? → Test kiểm code; gate xét lỗi dữ liệu còn lại và phạm vi người đã duyệt.
2. Tại sao tử số là 38, không phải 71 issue hay 125−80=45? → Đếm ảnh riêng biệt còn WARN chưa duyệt, bỏ ảnh không còn issue và ảnh đã duyệt.
3. Tại sao không nâng conf tới khi Release? → Có thể khiến checker bỏ sót lỗi, tạo hàng đợi nhỏ giả; phải chọn theo bằng chứng calibration.
4. Tại sao clean mAP thấp hơn không có nghĩa bài làm thất bại? → Bài yêu cầu kiểm chứng và báo trung thực; dữ liệu hợp lệ cú pháp không bảo đảm model tốt hơn, còn confound về rò rỉ, số lượng, nhãn người và chỉ hai seed.
5. Tại sao phải giữ log và manifest? → Để biết đã thay đổi gì, dataset nào được dùng train và có tái lập được không.

Báo cáo nộp chính: [`submission/REPORT.md`](../submission/REPORT.md). Tài liệu này phục vụ học tập, không thay thế report sáu mục của đề. Các tài liệu người dùng gửi giữ nguyên tại Downloads, không tự đưa lên repo công khai.
