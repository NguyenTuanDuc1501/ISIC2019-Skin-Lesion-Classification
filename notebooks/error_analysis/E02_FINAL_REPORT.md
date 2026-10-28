# BÁO CÁO CUỐI E02 — Tổng hợp bảng quan sát thị giác (E02_FINALIZE v1.1 — sửa diễn đạt khác biệt định dạng)

## Phạm vi và cách đọc
- 52 ảnh validation chọn **có chủ đích** theo lớp × trạng thái B00/T02B (seed 42), **không đại diện** validation hay toàn dataset. Tần suất dưới đây không phải ước lượng tỷ lệ artifact.
- Quan sát do một người (người dùng) đánh giá trên gallery E02 ngày 2026-10-08. Gallery hiển thị nhãn và dự đoán nên việc đánh giá không mù.
- Báo cáo này chỉ **đếm** nhãn thủ công; **không phải kiểm chứng độc lập** nhận xét thị giác. Không tính hiệu năng trên 52 ảnh; hiệu năng vẫn lấy từ E01 trên 2.539 ảnh.
- Nguồn mọi số đếm: `visual_review_summary.csv` (cột scope/stratum/field/value/count/denominator). Kiểm tra đầu vào: `review_validation.json` (53/53 kiểm tra PASS).

## Kiểm tra đầu vào (tóm tắt)
- visual_review_completed.csv SHA256 khớp 6d8fdf07f7bacde88eee92ed46f899396e3d23cc27e84e2b87c9feda7ced50ce. ZIP Kaggle E02 SHA256 thực tế 4833caf450ef38d6b54fc1bca336e3940da4aacc1f8e041b7a8d2c4209147893; đọc trực tiếp input_audit.json, selection_manifest.csv, visual_review_template.csv trong ZIP; hai CSV khớp hash ghi trong audit E02; audit PASS, 52 ảnh hash đã xác minh, 0 ảnh test.
- 52 dòng, 21 cột, review_id/image/group duy nhất; ghép review_id + image 1-1 với template và manifest; cột A–K khớp; nhãn, dự đoán, group, kích thước, trạng thái khớp manifest; trạng thái tính lại từ dự đoán đã lưu khớp.
- Khác biệt định dạng: cột resize_anisotropy_x_over_y có 50 dòng mà chuỗi số trong bảng người dùng khác chuỗi trong template nhưng giá trị số bằng nhau (sai khác tối đa 5.0e-10 ≤ 1e-8): 30 dòng “1” so với “1.0”; 19 dòng “0.75” so với “0.7500000000000001”; 1 dòng “0.665039063” so với “0.6650390625”. Không phải cả 50 dòng đều là “1” so với “1.0”.
- Mọi ô quan sát đã điền, nằm trong quy ước (có/không/không chắc; sharpness “nét”). visual_review_final.csv chỉ đổi review_date 10/8/2026 → 2026-10-08 (52 ô); file người dùng gửi giữ nguyên.

## Quan sát (đếm nhãn thủ công, nguồn `visual_review_summary.csv`)
| Đặc điểm | có | không | không chắc |
|---|---|---|---|
| Lông (hair) | 25/52 | 27/52 | 0/52 |
| Thước/mực | 15/52 | 36/52 | 1/52 |
| Viền đen/vignette | 21/52 | 31/52 | 0/52 |
| Chói/phản xạ | 0/52 | 48/52 | 4/52 |
| Tổn thương sát mép | 1/52 | 50/52 | 1/52 |
| Biến dạng tỷ lệ sau resize | 22/52 | 30/52 | 0/52 |

- Độ nét: “nét” 52/52 (filter scope=overall, field=sharpness).

Theo trạng thái (filter scope=transition; mẫu số: B00 đúng/T02B sai 15, B00 sai/T02B đúng 15, cả hai sai 14, cả hai đúng 8):
| Đặc điểm = có | B00 đúng/T02B sai | B00 sai/T02B đúng | Cả hai sai | Cả hai đúng |
|---|---|---|---|---|
| Lông | 6/15 | 11/15 | 4/14 | 4/8 |
| Thước/mực | 2/15 | 7/15 | 6/14 | 0/8 |
| Viền đen | 4/15 | 5/15 | 9/14 | 3/8 |
| Biến dạng tỷ lệ | 5/15 | 8/15 | 5/14 | 4/8 |

Theo lớp, biến dạng tỷ lệ = có (filter scope=class, field=aspect_distortion_after_resize): MEL 2/7, NV 5/7, BCC 2/7, AK 1/7, BKL 2/7, DF 4/6, VASC 3/4, SCC 3/7.

Đối chiếu mô tả với hình học trong manifest (nguồn `review_validation.json` → aspect_label_vs_geometry; selection_manifest.csv cột resize_anisotropy_x_over_y): 22 ảnh không vuông đều được ghi “có” biến dạng, 30 ảnh vuông đều ghi “không”. Nhãn này vì vậy trùng với một đại lượng hình học đo được, không mang thông tin thị giác riêng.

## Giới hạn diễn giải
- E02_016 (BCC; B00 BCC, T02B BKL; 1024×1024): nhận xét “ảnh bị thiếu sáng” chỉ cho thấy người quan sát thấy ảnh tối trên gallery; chưa xác định nguyên nhân và không liên hệ với lỗi T02B.
- “Nét” cho cả 52 ảnh chỉ mô tả ảnh hiển thị trong gallery (ảnh gốc thu nhỏ để hiển thị, preview 224), không phải đo độ nét ảnh gốc.
- “Không chắc” giữ nguyên và đếm riêng; không gộp vào có/không.
- Mẫu số từng ô nhỏ (4–15); khác biệt giữa các ô không được kiểm định và không nên coi là tín hiệu.

## Giả thuyết để CHA xem xét (chưa triển khai, không chọn phương pháp từ tần suất 52 ảnh)
1. **Resize không giữ tỷ lệ.** Quan sát: 22/52 ảnh không vuông bị co không đều khi về 224×224 (manifest), tỷ lệ khác nhau theo lớp (trên). Giả thuyết: biến dạng hình học có thể ảnh hưởng một số lớp. Lưu ý: kích thước ảnh có thể gắn với nguồn thu thập nên dễ bị nhiễu. Bước mô tả trước: đo kích thước trên toàn validation và đối chiếu hiệu năng E01 theo nhóm hình học.
2. **Viền đen/vignette.** Quan sát: 21/52 ảnh có viền đen; cả hai sai 9/14, cả hai đúng 3/8. Giả thuyết: viền đen có thể liên quan với lỗi chung của hai mô hình. Cần ước lượng trên mẫu đại diện hoặc toàn validation trước khi cân nhắc crop/mask.
3. **Lông và thước/mực.** Quan sát: lông 25/52, thước/mực 15/52; ở nhóm B00 sai/T02B đúng lông 11/15, thước/mực 7/15. Giả thuyết: phần cải thiện của T02B có thể khác nhau giữa ảnh có và không có artifact. Chưa đủ cơ sở để chọn xử lý lông.

## Điều chưa biết
- Tỷ lệ các đặc điểm trên toàn validation; mức đồng thuận giữa người quan sát (chỉ có 1 người, không mù); nguồn thu thập ảnh (không có trong metadata); nguyên nhân lỗi; tác động của bất kỳ kỹ thuật tiền xử lý nào.
- Không train, không đọc test, không đổi split/nhãn, không sửa nhận xét, không gộp ResNet18.
