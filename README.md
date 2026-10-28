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
- `Phan_loai_ton_thuong_da_ISIC_2019.ipynb`: Jupyter Notebook thực hiện kiểm toán dữ liệu (EDA), phân chia tập train/val/test, cấu hình mô hình ResNet50, đánh giá độ chính xác và demo dự đoán.
- `Bao_cao_ISIC2019_Nhom8.docx`: Báo cáo học thuật chi tiết của đồ án.
- `ISIC2019_Nhom8_Thuyet_trinh_final.pptx`: Slide thuyết trình báo cáo tổng kết.
- `.gitignore`: Cấu hình loại trừ các file cache, checkpoint trọng số nặng (`.pt`, `.pth`), môi trường ảo và dữ liệu raw.
