# Tái lập CPU

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
