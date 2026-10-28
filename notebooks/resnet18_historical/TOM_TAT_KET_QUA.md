# Báo cáo demo ISIC 2019 — ResNet18

Đọc 25331 ảnh; loại 4 ảnh trong 2 nhóm nhãn byte xung đột.
Huấn luyện/đánh giá trên 25327 ảnh; train/val/test: 15140/5102/5085 ảnh.
Đã chọn epoch 8 theo validation macro-F1 0.5818.

| Mô hình | Accuracy | Macro-F1 | Balanced accuracy |
|---|---:|---:|---:|
| majority: NV | 0.5054 | 0.0839 | 0.1250 |
| ResNet18 | 0.7050 | 0.5810 | 0.6010 |

Recall theo lớp:
- MEL: 0.6571 / 872 ảnh test.
- NV: 0.7907 / 2570 ảnh test.
- BCC: 0.7511 / 683 ảnh test.
- AK: 0.4253 / 174 ảnh test.
- BKL: 0.5019 / 538 ảnh test.
- DF: 0.5283 / 53 ảnh test.
- VASC: 0.7778 / 54 ảnh test.
- SCC: 0.3759 / 141 ảnh test.

Thiếu lesion_id: 2084 ảnh; nhóm gộp do hash: 9.
Xem conflicting_exact_duplicates.csv và folder_label_mismatch.csv để kiểm tra nguồn dữ liệu.
Sau lọc/gộp, split có thể khác lần EfficientNet-B0 cũ; không so điểm như phép đối chứng trên cùng test.
Ảnh byte trùng và lesion ID biết được giữ cùng split; chưa bảo đảm độc lập theo bệnh nhân hay phát hiện hết ảnh gần trùng.
Đây là test nội bộ từ ISIC train. Chưa đánh giá test chính thức, ảnh bệnh nhân Việt Nam hoặc tính hữu dụng lâm sàng.
Các thử nghiệm tiếp theo chỉ dùng validation để quyết định; xem class_report/confusion_matrix/ảnh sai trước khi đổi dữ liệu hoặc preprocessing.
Nguồn/giấy phép: https://challenge.isic-archive.com/data/ — CC BY-NC; ghi công BCN20000, HAM10000, MSK theo trang phát hành.