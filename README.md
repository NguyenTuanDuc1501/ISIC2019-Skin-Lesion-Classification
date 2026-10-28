# Phân Loại Tổn Thương Da ISIC 2019 - Nhóm 8

Dự án nghiên cứu và phân loại 8 nhóm tổn thương da trên tập dữ liệu chuẩn **ISIC 2019** sử dụng mô hình học sâu ResNet50 kết hợp các chiến lược tiền xử lý, tăng cường dữ liệu và tối ưu hóa huấn luyện.

---

##  Thông tin đề tài
- **Đề tài**: Phân loại tổn thương da ISIC 2019
- **Tác giả / Nhóm thực hiện**: Nhóm 8
  - **Nguyễn Tuấn Đức** - MSSV: `2351067091`

---

##  8 Nhóm tổn thương mục tiêu
1. **MEL**: Melanoma (U hắc tố ác tính)
2. **NV**: Melanocytic nevus (Nốt ruồi sắc tố lành tính)
3. **BCC**: Basal cell carcinoma (Ung thư tế bào đáy)
4. **AK**: Actinic keratosis (Dày sừng quang hóa)
5. **BKL**: Benign keratosis (Dày sừng lành tính)
6. **DF**: Dermatofibroma (U xơ da)
7. **VASC**: Vascular lesion (Tổn thương mạch máu)
8. **SCC**: Squamous cell carcinoma (Ung thư tế bào vảy)

---

##  Cấu trúc dự án
ISIC2019-Skin-Lesion-Classification/
├── README.md                            # Hướng dẫn chi tiết, link dataset, tóm tắt kết quả
├── requirements.txt                     # Danh sách thư viện Python cần thiết
├── .gitignore                           # Loại trừ tự động dataset nặng 10GB và file *.pt
│
├── reports/                             # Báo cáo học thuật
│   └── Bao_cao_ISIC2019_Nhom8.docx      # Báo cáo chi tiết đồ án (>=25 trang)
│
├── slides/                              # Slide thuyết trình
│   └── ISIC2019_Nhom8_Thuyet_trinh_final.pptx # Slide trình bày bảo vệ
│
├── notebooks/                           # Toàn bộ mã nguồn thực nghiệm
│   ├── 00_Bao_cao_va_demo.ipynb         # Notebook chính tổng hợp và demo
│   ├── data_audit/                      # Kiểm toán dữ liệu và phân chia
│   ├── baseline_augmentation/           # Baseline B00 & Augmentation D4
│   ├── preprocessing_r50/               # 10 phương án tiền xử lý (P01 đến P10)
│   ├── training_strategies/             # L01 (Weighted CE) và S01 (Balanced Sampler)
│   ├── paired_seeds/                    # Kiểm định mở rộng Seed 43, Seed 44
│   ├── error_analysis/                  # Phân loại lỗi và quan sát 52 ca thực tế (E02)
│   ├── final_evaluation/                # Đánh giá độc lập trên tập test nội bộ
│   └── resnet18_historical/             # Khảo sát kiến trúc tiền đề ResNet18
│
├── src/                                 # Module Python dùng chung (runner.py, locked_functions.py,...)
├── configs/                             # Cấu hình thí nghiệm và protocol lock đã khóa
├── manifests/                           # split_manifest.csv (danh sách chia tập dữ liệu chuẩn)
└── results/                             # Kết quả đo lường và bảng experiment_index.csv
