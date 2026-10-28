# PROJECT_STATE — R02_RESULT_FINALIZE v1.0

- Đã xác minh: R02 đủ4run, đúng1REUSE B00/43+3TRAIN_FRESH. 90checksum reports và94checksum FULL Output khớp; metrics/per-class/confusion/history/LR/init và bootstrap hai cặp được tính lại. 519kiểm có kết quả trongAUDIT.json.
- Checkpoint: FULL Output đính kèm có đủ4.pt; đã kiểm trực tiếp4SHA256, không còn giới hạn thiếu3checkpoint mới từreports. Chưa GPU-reinference checkpoint.
- Cấu hình: ResNet50/ImageNetV1,224×224, CE không trọng số, AdamW LR1e-4/wd1e-4, batch32/workers2, max16/patience4/min_delta1e-5; T02B chỉ thêmD4 train; khôngAMP/TTA.
- Bảng thí nghiệm:8run seed42 lịch sử R01/L01+4run R02=12hàng; phân biệt thăm dò42/xác nhận43,44 và comparator cùngseed.
- Kết quả xác nhận: Δmacro-F1 mean+2.182405điểm%, sampleSD2.419690điểm%; haiCIgroup chứa0. Accuracy43 giảm; không bỏ kết quả bất lợi.
- Quyết định: giữT02B_D4_R50; L01 chưa chứng minh cải thiện; chưa mở thí nghiệm mới, khôngtrainthêm.
- Lịch sử lỗi: TypeError duplicate method đã giải quyết qua recovery; STOP cũ giữ nguyên. CácNOT_RUN trongaudit preflight là snapshot trướctrain, không đổi thànhPASS hiện tại.
- Còn mở: chưa đánh giá test cuối; chỉ2seed xác nhận mới trên cùngvalidation; không xemCIgroup là biếnthiênseed. Các số lịch sử carry từgói đãhash, không tính lại toàn bộrawseed42 trong lầnchốt này.
