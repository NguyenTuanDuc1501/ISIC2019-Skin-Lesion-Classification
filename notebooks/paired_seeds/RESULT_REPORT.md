# R02_RESULT_FINALIZE — v1.0

## Kết luận đã chốt
- Đủ bốn run: tái sử dụng B00/43 đúng một lần và ba run train mới. Không huấn luyện thêm trong lần finalize.
- T02B có macro-F1 cao hơn B00 ở cả hai seed xác nhận mới: +0.471426 và +3.893384 điểm %. Mức tăng trung bình là +2.182405 điểm %, sample SD 2.419690 điểm % trên hai chênh lệch ghép cặp.
- Hai CI mới đều chứa0. Đây không phải bằng chứng D4 luôn cải thiện hoặc hai phương án tương đương. Giữ T02B_D4_R50 hiện hành; không mở thí nghiệm mới.
- Có kết quả bất lợi phải giữ: accuracy seed43 giảm 1.457267 điểm %, dù macro-F1 và balanced accuracy tăng.

## 1. Nguồn và trạng thái thực tế
Tên file đính kèm là R02_RECOVERY_v1_1_preflight02_Bat_Train.zip, không phải tên reports đứng riêng trong danh sách yêu cầu. Đây là FULL Output, SHA256 5ade28a98437e4a12eee001880a5fea8007dff5fb6b55590219839182ee81887; có reports ZIP nhúng, SHA256 daa6bc2fc22e0cf7948cefe3887fefc229035f93c0fc057d7dd4125b493e3626. Đã kiểm 90 checksum trong reports và 94 checksum trong FULL Output. Các file reports trùng byte với thành phần FULL Output.

Notebook đã chạy có source nhúng trùng implementation.py và source ba run mới. Nguồn train/eval/dataset/loader/RNG/model/D4/bootstrap không đổi so với nguồn lịch sử; chỉ orchestration/provenance khác. B00/43 giữ source/lock1.0; ba run mới dùng source phục hồi1.1. File B00/43 trong reports khớp hash lịch sử, không ghi lại acceptance audit.

**Khác với giới hạn dự kiến trong đề bài, FULL Output này có đủ bốn.pt:** đã tính hash trực tiếp và đối chiếu metadata cả bốn checkpoint. Điều này chỉ xác minh bytes, không phải load model rồi suy luận lại bằng GPU. Bảng CHECKPOINT_VERIFICATION.csv tách riêng sha_claimed và sha_direct.

Các số trong bảng seed42 được đọc từ gói R01/L01 thực tế có hash khóa và đối chiếu HISTORICAL_SEED42.csv, không lấy từ hội thoại. Lần finalize này không tính lại toàn bộ raw predictions của tám run lịch sử seed42; EXPERIMENT_TABLE ghi rõ mức carry-forward. Không có thiếu nguồn lõi ngăn chốt R02.

## 2. Kết quả từng run xác nhận
| Seed | Method | Accuracy % | Balanced accuracy % | Macro-F1 % | Best/stop |
| --- | --- | --- | --- | --- | --- |
| 43 | B00_R50 | 74.9902 | 55.2652 | 57.3231 | 11/15 |
| 43 | T02B_D4_R50 | 73.5329 | 57.1714 | 57.7945 | 7/11 |
| 44 | B00_R50 | 73.8874 | 53.0010 | 56.0809 | 13/16 |
| 44 | T02B_D4_R50 | 76.9200 | 59.2508 | 59.9743 | 7/11 |

Nguồn số từng hàng: SEED_RESULTS.csv ghi trực tiếp predictions, complete, lock và history tương ứng trong x/trained_output/R02_RECOVERY_v1_1_preflight02/seed_{seed}/{method}/. Tính lại bằng confusion matrix và đối chiếu độc lập TP/FP/FN, dung sai1e-8. Đủ2.539image ID ghép1–1 với manifest mỗi run. PER_CLASS_RESULTS.csv và CONFUSION_MATRICES_LONG.csv cung cấp đầy đủ breakdown kèm nguồn; không bỏ lớp/seed điểm thấp.

## 3. Chênh lệch ghép cặp và bất định
| Seed | Δ macro-F1 điểm % | CI95 group điểm % | Δ accuracy điểm % | Δ balanced accuracy điểm % |
| --- | --- | --- | --- | --- |
| 43 | +0.471426 | [-3.799050; 5.108781] | -1.457267 | +1.906132 |
| 44 | +3.893384 | [-0.855804; 8.646324] | +3.032690 | +6.249790 |

Bootstrap giữ nguyên mã khóa:2.000lượt, seed20261007; lấy lại group phân tầng theo8nhãn, giữ mọi ảnh trong sampledgroup. Hai phương án cùng seed dùng cùng lượt group. Tính lại toàn bộdraws, CI và support khớp nguồn;1392group. Không lấy trung bình CIbounds, không gộp ảnh lặp giữa seed thành quan sát độc lập.

Các CI này phản ánh lấy mẫu group validation với checkpoint đã fit, không đo biến thiên seed huấn luyện, không hiệu chỉnh chọn checkpoint hoặc tái dùng validation. CI chứa0 không chứng minh không có tác dụng hay tương đương.

## 4. Mean/sample SD trên đúng hai seed mới
| Method / chênh lệch | Macro-F1 mean % / điểm % | Sample SD điểm % | n seed |
| --- | --- | --- | --- |
| B00_R50 | 56.701988 | 0.878322 | 2 |
| T02B_D4_R50 | 58.884392 | 1.541368 | 2 |
| T02B_minus_B00 | 2.182405 | 2.419690 | 2 |

Nguồn NEW_SEEDS_MEAN_SD.csv: dùng ddof=1. SD của Δ lấy từ hai Δ cùng seed, không suy ra từ SD hai method. Mean/SD accuracy và balanced accuracy cũng có trong bảng đầy đủ. Chỉn=2, không báo CI qua trainingseed.

## 5. Seed42 lịch sử và cập nhật R01
Seed42 là thăm dò; seed43/44 là hai lần xác nhận trên cùng validation, không phải hai tập đánh giá độc lập mới. Biểu đồ charts/seed_comparison_notion_agent_chart.html phân biệt hai giai đoạn bằng nhãn, không nối các seed thành đường thời gian.
| Seed42 method | Macro-F1 % | Vai trò |
| --- | --- | --- |
| B00_R50 | 55.2115 | thăm dò lịch sử |
| T02B_D4_R50 | 60.3002 | thăm dò lịch sử |

T02B có macro-F1 cao hơn B00 ở cả ba seed đã quan sát, nhưng mức tăng dao động. Không diễn giải thành luôn thắng hoặc suy rộng chắc chắn ngoài dữ liệu này.

EXPERIMENT_TABLE.csv phiên bản mới giữ8run seed42 từ R01/L01 và thêm4run R02, tổng12hàng. Comparator được ghi rõ: các nhánh cải tiến seed42 so T02B seed42; trongR02, T02B so B00 cùngseed. Không so chéo seed để kết luận tác động phương pháp. L01 vẫn nhỉnh hơn điểm thô seed42 nhưng chưa chứng minh cải thiện. Không chọn thí nghiệm mới trong nhiệm vụ này.

## 6. Audit, lịch sử lỗi và giới hạn
- AUDIT.json liệt kê các kiểm tra thực sự đã chạy; kiểm checksum/source/notebook, init cùngcặp, best/patience/LR và metric/per-class/confusion đạt dung sai.
- B00/43 best11/stop15, T02B/43 best7/stop11; B00/44 best13/stop16 (chạm ngân sách), T02B/44 best7/stop11. Không tăng budget vì checkpoint muộn.
- Duplicate-method TypeError cũ được giữ nguyên trong source_evidence/HISTORICAL_STOP.json, không đổi thànhPASS. CURRENT_STATUS.json cùng đủ4complete/predictions và dispatch xác nhận phục hồi đã hoàn thành.
- preflight_audit.training=NOT_RUN và recovery_audit.training_remaining=NOT_RUN là snapshot trước khitrain; không sửa file gốc. Không dùng chúng thay trạng thái hoàn thành sau đó.
-2.539validation ảnh có2.537hashbytes và1.392group. Không duplicate row/imageID; các bytes trùng đã thuộc cấu trúc manifest khóa. Giữ nguyên, không deduplicate; bootstrapgroup thay vì giả định ảnh độc lập.
- Finalize không mở lại ảnh, không train và không suy luận lại model. Việc hash ảnh được ghi trong audit Kaggle đã chạy, không gọi là hash ảnh mới ởsandbox.
- Chưa đánh giá test cuối; chỉ hai seed xác nhận mới, cùngvalidation được tái dùng. Thiếu cácPDF/checkpoint lịch sử khác không ngăn kiểmR02 nhưng không tự gán đã kiểm mới.

## 7. Quyết định còn hiệu lực
Giữ T02B_D4_R50 là phương án hiện hành của chuỗi cải tiến. R02 đã chốt, không còn yêu cầu chạy lại bốnrun. Không chọn seed tốt nhất, không mở ConvNeXt/weightedloss/ensemble hoặc thí nghiệm mới; test cuối chưa dùng.
