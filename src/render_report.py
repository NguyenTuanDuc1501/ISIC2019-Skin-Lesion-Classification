from pathlib import Path
import json,hashlib,zipfile,shutil
import pandas as pd
R=Path('/data/r02final');O=R/'deliverables/R02_RESULT_FINALIZE_v1_0';E=json.load(open(O/'EVIDENCE.json'));A=json.load(open(O/'AUDIT.json'));runs=E['runs'];paired=E['paired'];stats=E['stats'];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mdtable(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(str(v) for v in row)+' |\n' for row in rows)
def pct(x):return f'{100*x:.4f}'
def getstat(method,metric='macro_f1'):return next(x for x in stats if x['method']==method and x['metric']==metric)
d=getstat('T02B_minus_B00');seed43=next(p for p in paired if p['seed']==43)
report=f'''# R02_RESULT_FINALIZE — v1.0

## Kết luận đã chốt
- Đủ bốn run: tái sử dụng B00/43 đúng một lần và ba run train mới. Không huấn luyện thêm trong lần finalize.
- T02B có macro-F1 cao hơn B00 ở cả hai seed xác nhận mới: +{paired[0]['delta_macro_f1_pp']:.6f} và +{paired[1]['delta_macro_f1_pp']:.6f} điểm %. Mức tăng trung bình là +{d['mean_percent_or_pp']:.6f} điểm %, sample SD {d['sample_SD_pp']:.6f} điểm % trên hai chênh lệch ghép cặp.
- Hai CI mới đều chứa0. Đây không phải bằng chứng D4 luôn cải thiện hoặc hai phương án tương đương. Giữ T02B_D4_R50 hiện hành; không mở thí nghiệm mới.
- Có kết quả bất lợi phải giữ: accuracy seed43 giảm {abs(seed43['delta_accuracy_pp']):.6f} điểm %, dù macro-F1 và balanced accuracy tăng.

## 1. Nguồn và trạng thái thực tế
Tên file đính kèm là R02_RECOVERY_v1_1_preflight02_Bat_Train.zip, không phải tên reports đứng riêng trong danh sách yêu cầu. Đây là FULL Output, SHA256 {E['source_zip_sha']}; có reports ZIP nhúng, SHA256 {E['reports_zip_sha']}. Đã kiểm {E['report_checksums']} checksum trong reports và {E['full_checksums']} checksum trong FULL Output. Các file reports trùng byte với thành phần FULL Output.

Notebook đã chạy có source nhúng trùng implementation.py và source ba run mới. Nguồn train/eval/dataset/loader/RNG/model/D4/bootstrap không đổi so với nguồn lịch sử; chỉ orchestration/provenance khác. B00/43 giữ source/lock1.0; ba run mới dùng source phục hồi1.1. File B00/43 trong reports khớp hash lịch sử, không ghi lại acceptance audit.

**Khác với giới hạn dự kiến trong đề bài, FULL Output này có đủ bốn.pt:** đã tính hash trực tiếp và đối chiếu metadata cả bốn checkpoint. Điều này chỉ xác minh bytes, không phải load model rồi suy luận lại bằng GPU. Bảng CHECKPOINT_VERIFICATION.csv tách riêng sha_claimed và sha_direct.

Các số trong bảng seed42 được đọc từ gói R01/L01 thực tế có hash khóa và đối chiếu HISTORICAL_SEED42.csv, không lấy từ hội thoại. Lần finalize này không tính lại toàn bộ raw predictions của tám run lịch sử seed42; EXPERIMENT_TABLE ghi rõ mức carry-forward. Không có thiếu nguồn lõi ngăn chốt R02.

## 2. Kết quả từng run xác nhận
'''
report+=mdtable(['Seed','Method','Accuracy %','Balanced accuracy %','Macro-F1 %','Best/stop'],[[x['seed'],x['method'],pct(x['accuracy']),pct(x['balanced_accuracy']),pct(x['macro_f1']),f"{x['best_epoch']}/{x['completed_epochs']}"] for x in runs])
report+='\nNguồn số từng hàng: SEED_RESULTS.csv ghi trực tiếp predictions, complete, lock và history tương ứng trong x/trained_output/R02_RECOVERY_v1_1_preflight02/seed_{seed}/{method}/. Tính lại bằng confusion matrix và đối chiếu độc lập TP/FP/FN, dung sai1e-8. Đủ2.539image ID ghép1–1 với manifest mỗi run. PER_CLASS_RESULTS.csv và CONFUSION_MATRICES_LONG.csv cung cấp đầy đủ breakdown kèm nguồn; không bỏ lớp/seed điểm thấp.\n\n## 3. Chênh lệch ghép cặp và bất định\n'
report+=mdtable(['Seed','Δ macro-F1 điểm %','CI95 group điểm %','Δ accuracy điểm %','Δ balanced accuracy điểm %'],[[x['seed'],f"{x['delta_macro_f1_pp']:+.6f}",f"[{x['ci95_low_pp']:.6f}; {x['ci95_high_pp']:.6f}]",f"{x['delta_accuracy_pp']:+.6f}",f"{x['delta_balanced_accuracy_pp']:+.6f}"] for x in paired])
report+='''
Bootstrap giữ nguyên mã khóa:2.000lượt, seed20261007; lấy lại group phân tầng theo8nhãn, giữ mọi ảnh trong sampledgroup. Hai phương án cùng seed dùng cùng lượt group. Tính lại toàn bộdraws, CI và support khớp nguồn;1392group. Không lấy trung bình CIbounds, không gộp ảnh lặp giữa seed thành quan sát độc lập.

Các CI này phản ánh lấy mẫu group validation với checkpoint đã fit, không đo biến thiên seed huấn luyện, không hiệu chỉnh chọn checkpoint hoặc tái dùng validation. CI chứa0 không chứng minh không có tác dụng hay tương đương.

## 4. Mean/sample SD trên đúng hai seed mới
'''
report+=mdtable(['Method / chênh lệch','Macro-F1 mean % / điểm %','Sample SD điểm %','n seed'],[[m,f"{getstat(m)['mean_percent_or_pp']:.6f}",f"{getstat(m)['sample_SD_pp']:.6f}",2] for m in ['B00_R50','T02B_D4_R50','T02B_minus_B00']])
report+='''
Nguồn NEW_SEEDS_MEAN_SD.csv: dùng ddof=1. SD của Δ lấy từ hai Δ cùng seed, không suy ra từ SD hai method. Mean/SD accuracy và balanced accuracy cũng có trong bảng đầy đủ. Chỉn=2, không báo CI qua trainingseed.

## 5. Seed42 lịch sử và cập nhật R01
Seed42 là thăm dò; seed43/44 là hai lần xác nhận trên cùng validation, không phải hai tập đánh giá độc lập mới. Biểu đồ charts/seed_comparison_notion_agent_chart.html phân biệt hai giai đoạn bằng nhãn, không nối các seed thành đường thời gian.
'''
h42=pd.DataFrame(E['historical_seed42']);report+=mdtable(['Seed42 method','Macro-F1 %','Vai trò'],[[x['method'],pct(x['macro_f1']),'thăm dò lịch sử'] for x in E['historical_seed42']])
report+='''
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
'''
(O/'RESULT_REPORT.md').write_text(report,encoding='utf-8')
(O/'PRESENTATION_TO_CO_HANH.md').write_text(f'''# Đoạn trình bày với cô Hạnh

“Thưa cô, em kiểm tra lại D4 bằng cách so B00 và T02B trên cùng split, cùng seed và cùng cấu hình; chỉ khác D4 ở ảnh train. Ngoài seed42 thăm dò, em chạy xác nhận thêm seed43 và44, giữ nguyên tất cả kết quả. Macro-F1 của D4 cao hơn B00 ở cả ba seed đã quan sát. Trên hai seed mới, chênh lệch lần lượt là+{paired[0]['delta_macro_f1_pp']:.4f} và+{paired[1]['delta_macro_f1_pp']:.4f}điểm phần trăm; trung bình+{d['mean_percent_or_pp']:.4f}, sample SD{d['sample_SD_pp']:.4f}điểm phần trăm. Tuy nhiên, hai khoảng tin cậy bootstrap theo group đều chứa0 và mức tăng dao động, nên em chưa kết luận D4 luôn cải thiện. Riêng seed43, accuracy giảm dù macro-F1 và balanced accuracy tăng. Em giữ T02B hiện hành, chưa mở thí nghiệm mới. Các seed vẫn dùng chung validation, nên đây không phải các tập đánh giá độc lập; test cuối chưa được sử dụng.”
''',encoding='utf-8')
(O/'PROJECT_STATE.md').write_text(f'''# PROJECT_STATE — R02_RESULT_FINALIZE v1.0

- Đã xác minh: R02 đủ4run, đúng1REUSE B00/43+3TRAIN_FRESH. {E['report_checksums']}checksum reports và{E['full_checksums']}checksum FULL Output khớp; metrics/per-class/confusion/history/LR/init và bootstrap hai cặp được tính lại. {A['n_checks']}kiểm có kết quả trongAUDIT.json.
- Checkpoint: FULL Output đính kèm có đủ4.pt; đã kiểm trực tiếp4SHA256, không còn giới hạn thiếu3checkpoint mới từreports. Chưa GPU-reinference checkpoint.
- Cấu hình: ResNet50/ImageNetV1,224×224, CE không trọng số, AdamW LR1e-4/wd1e-4, batch32/workers2, max16/patience4/min_delta1e-5; T02B chỉ thêmD4 train; khôngAMP/TTA.
- Bảng thí nghiệm:8run seed42 lịch sử R01/L01+4run R02=12hàng; phân biệt thăm dò42/xác nhận43,44 và comparator cùngseed.
- Kết quả xác nhận: Δmacro-F1 mean+{d['mean_percent_or_pp']:.6f}điểm%, sampleSD{d['sample_SD_pp']:.6f}điểm%; haiCIgroup chứa0. Accuracy43 giảm; không bỏ kết quả bất lợi.
- Quyết định: giữT02B_D4_R50; L01 chưa chứng minh cải thiện; chưa mở thí nghiệm mới, khôngtrainthêm.
- Lịch sử lỗi: TypeError duplicate method đã giải quyết qua recovery; STOP cũ giữ nguyên. CácNOT_RUN trongaudit preflight là snapshot trướctrain, không đổi thànhPASS hiện tại.
- Còn mở: chưa đánh giá test cuối; chỉ2seed xác nhận mới trên cùngvalidation; không xemCIgroup là biếnthiênseed. Các số lịch sử carry từgói đãhash, không tính lại toàn bộrawseed42 trong lầnchốt này.
''',encoding='utf-8')
(O/'CHANGELOG.md').write_text('''# CHANGELOG — R02_RESULT_FINALIZE v1.0

- Tạo mới báo cáo finalize và bảng12run từ R01v1.0+L01addendumv1.1+R02 xác nhận; không thay bytes nguồn.
- Tính lại4run, bootstrap2000 từngcặp, mean/sampleSD ghépcặp43/44; bổ sung dữliệulớp/confusion/history đầyđủ cósource.
- Đối chiếu notebook với source thực thi; giữsource/lock1.0 B00/43 vàprovenance1.1 ba run mới. Giữlịch sửSTOP; khôngchuyểntrạng thái lịch sử.
- Làm rõ gói người dùng cung cấp làFULL Output với reportsnhúng và4.pt, vìvậy kiểm trực tiếpcả4checkpoint thay vì ghi thiếu3checkpoint mới.
- GiữT02B hiệnhành; đóng nhiệm vụ xácnhận, không đềxuất thínghiệm mới hoặc dùngtest.
''',encoding='utf-8')
(O/'CPU_REPRODUCE.md').write_text('''# Tái lập CPU

Cần Python3, numpy vàpandas; khôngcần Torch/GPU, ảnhISIC hoặcInternet. Không chạy notebookhuấn luyện.

1. Tạo thưmụcWORK/raw, chép đúng5nguồnđầu vào vàđổi tên bảnchép:
   - FULL Output đãtrain→trained_output.zip
   - notebook(3)→trained.ipynb
   - OutputchưaTrain→preflight.zip
   - R01deliverables→r01.zip
   - L01addendum→l01_addendum.zip
2. Chạy: python src/finalize.py --root WORK
   Script giải nén nếuWORK/x chưa có, kiểm checksum/hashes, trích riêng bootstrapnumpy khóa bằngAST, khôngthực thi notebooktrain. Gặp mismatch sẽassertSTOP, không sửanguồn.
3. Kết quả ởWORK/deliverables/R02_RESULT_FINALIZE_v1_0. Đường dẫnsource trongbảng làrelative WORK. ScriptCPU tái tạo metrics/bảng/audit/spec; chartHTML đãđónggói. Dựng lại chart cầncanonicalinline-charts builder; không cần đểkiểm số.
4. src/render_report.py đọc EVIDENCE.json đểsoạnbáo cáo, không tính lại theođường khác. SửaR đầu script khi chạy ởmáy khác. SHA256SUMS của gói dùngkiểm bytesbàngiao, không áp cho một bản report mới được chỉnh đường dẫn.

Inputinventory giữ tênattachment thực tế vàhash mỗi thànhphần; nguồnZIP reports têntrongđề khônggửiđứngriêng nhưng có reportsZIPnhúng đượckiểm90checksum. Rawsourcekhôngđónggóilại trongdeliverable đểtránhnhân bản405MB; giữ cácfileđầu vào bênngoài.
''',encoding='utf-8')
shutil.copyfile(R/'finalize.py',O/'src/finalize.py');shutil.copyfile(R/'render_report.py',O/'src/render_report.py')
shutil.copytree(R/'profiles',O/'profile_logs',dirs_exist_ok=True)
print('REPORTS_WRITTEN',O)
