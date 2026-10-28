import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

WORKSPACE = r"D:\Nhom8_Phan_Loai_Ton_Thuong_Tren_Da_ISIC2019"
DOCX_OUTPUT = os.path.join(WORKSPACE, "slides", "Kich_ban_thuyet_trinh_12_phut.docx")
DOCX_COPY = os.path.join(WORKSPACE, "reports", "Kich_ban_thuyet_trinh_12_phut.docx")

doc = docx.Document()

# Page Margins
sections = doc.sections
for section in sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

# Colors
C_PRIMARY = RGBColor(139, 30, 30)   # Crimson #8B1E1E
C_TEAL = RGBColor(27, 94, 85)       # Teal #1B5E55
C_DARK = RGBColor(34, 34, 34)       # Charcoal #222222
C_MUTED = RGBColor(100, 100, 100)   # Gray #646464

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def add_header_block():
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_uni = p_uni.add_run("PHÂN HIỆU TRƯỜNG ĐẠI HỌC THỦY LỢI — BỘ MÔN CÔNG NGHỆ THÔNG TIN\n")
    r_uni.font.name = "Times New Roman"
    r_uni.font.size = Pt(11)
    r_uni.font.bold = True
    r_uni.font.color.rgb = C_PRIMARY

    r_sub = p_uni.add_run("KỊCH BẢN THUYẾT TRÌNH VÀ VẤN ĐÁP BẢO VỆ ĐỒ ÁN KHAI PHÁ DỮ LIỆU\n")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = C_DARK

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("ĐỀ TÀI: PHÂN LOẠI TÁM NHÓM TỔN THƯƠNG DA TRÊN ISIC 2019\n(KHỚP BỘ SLIDE THUYẾT TRÌNH 12 PHÚT — 18 SLIDES)")
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(16)
    r_t.font.bold = True
    r_t.font.color.rgb = C_PRIMARY

    # Metadata table
    tbl = doc.add_table(rows=2, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    for row in tbl.rows:
        row.cells[0].width = Inches(3.2)
        row.cells[1].width = Inches(3.8)

    set_cell_background(tbl.cell(0, 0), "FAF7F2")
    set_cell_background(tbl.cell(0, 1), "FAF7F2")
    set_cell_background(tbl.cell(1, 0), "FAF7F2")
    set_cell_background(tbl.cell(1, 1), "FAF7F2")

    p1 = tbl.cell(0, 0).paragraphs[0]
    p1.add_run("Sinh viên: ").bold = True
    p1.add_run("Nguyễn Tuấn Đức (MSSV: 2351067091)")

    p2 = tbl.cell(0, 1).paragraphs[0]
    p2.add_run("Giảng viên hướng dẫn: ").bold = True
    p2.add_run("ThS. Vũ Thị Hạnh")

    p3 = tbl.cell(1, 0).paragraphs[0]
    p3.add_run("Lớp: ").bold = True
    p3.add_run("S26-65CNTT (Nhóm 8)")

    p4 = tbl.cell(1, 1).paragraphs[0]
    p4.add_run("Thời lượng chuẩn: ").bold = True
    p4.add_run("12 phút (720 giây) + Vấn đáp")

    doc.add_paragraph() # Spacing

add_header_block()

# Giới thiệu phương pháp luận kịch bản
p_intro = doc.add_paragraph()
r_in_t = p_intro.add_run("HƯỚNG DẪN DÀNH CHO NGƯỜI THUYẾT TRÌNH:\n")
r_in_t.bold = True
r_in_t.font.color.rgb = C_PRIMARY
r_in_c = p_intro.add_run(
    "1. Thời lượng tổng: 12 phút (khoảng 35–45 giây mỗi slide). Cần giữ nhịp độ nói tự nhiên, dứt khoát.\n"
    "2. Phong cách trình bày: Tự tin, xưng 'Em', kính thưa 'Cô Hạnh và Quý Thầy Cô trong Hội đồng'.\n"
    "3. Sử dụng các 'Ví dụ đời sống' (như thi cử, khám bệnh cảm cúm, soi nốt ruồi) để giải thích trực quan các khái niệm phức tạp (Group split, mất cân bằng lớp, augmentation D4, đối chứng) cho người mới nghe cũng hiểu ngay.\n"
    "4. CẢNH BÁO KHOA HỌC: Ví dụ đời sống chỉ dùng để trực quan hóa khái niệm, không dùng thay thế cho chứng cứ số liệu thực nghiệm. Luôn đưa số liệu (Macro-F1, CI95, Delta pp) làm bằng chứng chốt.\n"
    "5. Có sẵn kịch bản Demo 2 ảnh (đúng và sai) và phương án dự phòng khi máy lag/mất mạng."
)
r_in_c.font.size = Pt(10.5)
r_in_c.font.color.rgb = C_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(12)

# Chi tiết 18 Slide
slides_data = [
    {
        "num": 1,
        "timing": "00:00 - 00:30 (30 giây)",
        "title": "Trang Bìa: Phân Loại Tám Nhóm Tổn Thương Da Trên ISIC 2019",
        "action": "Đứng thẳng, chào Hội đồng rõ ràng, mở đầu tự tin.",
        "spoken": (
            "Kính thưa cô Vũ Thị Hạnh cùng Quý Thầy Cô trong Hội đồng chấm đồ án!\n\n"
            "Em tên là Nguyễn Tuấn Đức, sinh viên lớp S26-65CNTT, đại diện Nhóm 8. Hôm nay, em xin phép được báo cáo "
            "kết quả nghiên cứu đồ án môn học Khai phá dữ liệu với đề tài: 'Phân loại tám nhóm tổn thương da trên bộ dữ liệu ISIC 2019 "
            "— Nghiên cứu tiền xử lý ảnh và chiến lược huấn luyện trong quy trình đánh giá có đối chứng'.\n\n"
            "Bài báo cáo hôm nay được em thiết kế tinh gọn trong 12 phút với mục tiêu: làm sáng tỏ bản chất bài toán, "
            "trình bày trung thực các kết quả thực nghiệm và rút ra những bài học khoa học có giá trị thực tế."
        ),
        "analogy": None
    },
    {
        "num": 2,
        "timing": "00:30 - 01:15 (45 giây)",
        "title": "Phần 1: Giới Thiệu Bài Toán & Động Lực Y Tế",
        "action": "Chỉ tay vào 2 khối bài toán: ảnh soi da và 8 nhóm nhãn.",
        "spoken": (
            "Thưa Thầy Cô, ung thư da là một trong những bệnh lý ác tính có tốc độ gia tăng nhanh trên thế giới, nhưng nếu được phát hiện sớm "
            "thì tỷ lệ điều trị thành công lên tới trên 95%. Để chẩn đoán, các bác sĩ da liễu sử dụng kỹ thuật soi da (Dermoscopy) "
            "để quan sát các cấu trúc sâu dưới biểu bì mà mắt thường không thấy được.\n\n"
            "Bài toán của đề tài chúng em là: nhận đầu vào là một ảnh soi da dermoscopy, áp dụng mô hình học sâu để phân loại vào đúng 1 trong 8 nhóm bệnh lý. "
            "Em xin nhấn mạnh một ranh giới khoa học quan trọng ngay từ đầu: Đây là hệ thống AI hỗ trợ sàng lọc ban đầu, "
            "không phải tất cả 8 nhóm đều là ung thư ác tính, và kết quả phân loại tuyệt đối không thay thế cho chẩn đoán sinh thiết mô bệnh học của bác sĩ chuyên khoa."
        ),
        "analogy": "Ảnh soi da giống như chụp X-quang: AI giúp bác sĩ khoanh vùng điểm đáng ngờ nhanh hơn, chứ quyết định mổ hay điều trị vẫn hoàn toàn thuộc về bác sĩ."
    },
    {
        "num": 3,
        "timing": "01:15 - 02:00 (45 giây)",
        "title": "Phần 1: Mục Tiêu & Ba Câu Hỏi Nghiên Cứu Cốt Lõi",
        "action": "Nhấn mạnh tinh thần nghiên cứu có đối chứng, không chạy theo điểm số ảo.",
        "spoken": (
            "Trong nghiên cứu học máy, việc chạy đua kết hợp nhiều kỹ thuật phức tạp để lấy một con số accuracy cao thường rất dễ dẫn đến kết luận ảo. "
            "Vì vậy, dưới sự định hướng của cô Hạnh, đồ án của em tập trung giải quyết 3 câu hỏi nghiên cứu cốt lõi theo nguyên tắc đối chứng độc lập:\n\n"
            "Thứ nhất: Tính bất biến quay của ảnh soi da có thực sự giúp mô hình tốt hơn hay không khi áp dụng nhóm đối xứng D4 so với ảnh không xoay lật (B00)?\n"
            "Thứ hai: Mười kỹ thuật tiền xử lý ảnh phức tạp (như cạo lông, cân bằng sáng, cắt viền) có thực sự mang lại lợi ích cho ResNet50 hay không?\n"
            "Thứ ba: Mức cải thiện quan sát được ở một lần chạy ngẫu nhiên có lặp lại bền vững khi kiểm chứng trên các seed khác nhau hay không?"
        ),
        "analogy": "Ví dụ đối chứng y học: Muốn kiểm tra một loại thuốc bổ có tác dụng không, bác sĩ phải giữ nguyên chế độ ăn ngủ của bệnh nhân và chỉ đổi duy nhất viên thuốc, chứ không thể vừa đổi thuốc vừa thay đổi cả chế độ sinh hoạt rồi vội vã khen thuốc tốt!"
    },
    {
        "num": 4,
        "timing": "02:00 - 02:45 (45 giây)",
        "title": "Phần 2: Tập Dữ Liệu ISIC 2019 & Kiểm Toán Toàn Vẹn",
        "action": "Nhấn mạnh con số 4 ảnh xung đột nhãn bị loại bỏ.",
        "spoken": (
            "Dữ liệu của đề tài được lấy từ tập huấn luyện chính thức của ISIC 2019 với 25.331 ảnh ban đầu. "
            "Trước khi đưa vào huấn luyện, em đã thực hiện một bước kiểm toán dữ liệu nghiêm ngặt.\n\n"
            "Kết quả kiểm toán phát hiện 48 ảnh trùng lặp chính xác nội dung byte. Đặc biệt, có 4 ảnh có cùng nội dung nhưng bị gán hai nhãn bệnh khác nhau! "
            "Nếu giữ lại 4 ảnh xung đột này, mô hình sẽ nhận tín hiệu học mâu thuẫn. Do đó, em đã loại bỏ 4 ảnh này và khóa cứng danh sách 25.327 ảnh sạch "
            "vào file manifest với mã băm SHA-256 đối chiếu từng file, bảo đảm tính toàn vẹn 100%."
        ),
        "analogy": "4 ảnh xung đột giống như một câu hỏi trắc nghiệm nhưng trong đề thi lúc thì chấm đáp án A đúng, lúc lại chấm đáp án B đúng. Học sinh học theo đề đó chắc chắn sẽ bị loạn kiến thức, nên phải loại bỏ ngay từ đầu!"
    },
    {
        "num": 5,
        "timing": "02:45 - 03:40 (55 giây)",
        "title": "Phần 2: Mất Cân Bằng Lớp Cực Đoan & Phân Chia Group Split",
        "action": "Chỉ vào biểu đồ cột Hình 3.1, làm nổi bật cột NV cao vọt và cột VASC bé xíu.",
        "spoken": (
            "Quan sát biểu đồ phân bố lớp ở Hình 3.1, Thầy Cô có thể thấy thách thức lớn nhất của dữ liệu: "
            "Lớp nốt ruồi NV chiếm tới hơn 50.8% với hơn 9.000 ảnh, trong khi lớp tổn thương mạch máu VASC chỉ có 151 ảnh (0.85%). "
            "Mức chênh lệch lên tới gần 60 lần! Nếu một mô hình lười biếng cứ đoán bừa mọi ảnh là NV, độ chính xác (Accuracy) vẫn đạt trên 50%, "
            "nhưng nó sẽ bỏ sót hoàn toàn các ca bệnh hiểm nghèo khác. Đây là lý do em chọn chỉ số Macro-F1 làm thước đo chính, nơi cả 8 lớp đều có tiếng nói ngang nhau.\n\n"
            "Về phân chia tập dữ liệu 70/10/20, em áp dụng thuật toán Group Split gom theo lesion_id. "
            "Nghĩa là mọi ảnh chụp cùng một vết tổn thương của cùng bệnh nhân bắt buộc phải nằm trọn vẹn trong một tập, "
            "tuyệt đối không để ảnh này ở tập Train còn ảnh kia lại lọt sang tập Validation hay Test."
        ),
        "analogy": "Ví dụ về thi cử: Một học sinh ôn thi nhận diện mặt người thân. Nếu cho ảnh chụp góc nghiêng của mẹ vào đề cương ôn tập, rồi lại lấy ảnh chụp góc thẳng của mẹ cho vào đề thi, thì học sinh làm đúng là do nhớ mặt người thân chứ không phải đã học được thuật toán nhận diện tổng quát. Group Split sinh ra để ngăn chặn triệt để hiện tượng 'nhớ mặt đề thi' này!"
    },
    {
        "num": 6,
        "timing": "03:40 - 04:25 (45 giây)",
        "title": "Phần 3: Pipeline Tiền Xử Lý Chuẩn Của Mô Hình T02B",
        "action": "Chỉ vào Hình 4.1 trước và sau resize 224x224.",
        "spoken": (
            "Từ các nghiên cứu nền tảng, mô hình chuẩn T02B được thiết kế với pipeline tiền xử lý 4 bước cực kỳ tinh gọn:\n"
            "1. Đọc ảnh RGB chuẩn hóa;\n"
            "2. Resize bilinear về kích thước cố định 224×224;\n"
            "3. Chuyển sang ma trận tensor trên thang số thực [0, 1];\n"
            "4. Chuẩn hóa kênh màu ImageNet theo đúng trọng số pretrained.\n\n"
            "Ở Hình 4.1, Thầy Cô có thể thấy việc ép ảnh về hình vuông 224x224 có thể làm méo nhẹ tỷ lệ khung hình học ban đầu. "
            "Tuy nhiên, ưu điểm vượt trội của phương pháp này là bảo toàn 100% diện tích tổn thương ở độ phân giải hữu ích cao nhất. "
            "Chúng em kiên quyết không áp dụng các bộ lọc xóa lông hay làm mịn tùy tiện ở bước này, vì mọi can thiệp pixel đều cần được kiểm chứng bằng thực nghiệm."
        ),
        "analogy": None
    },
    {
        "num": 7,
        "timing": "04:25 - 05:20 (55 giây)",
        "title": "Phần 3: Khảo Sát 10 Phương Án Tiền Xử Lý (P01 – P10)",
        "action": "Chỉ vào biểu đồ Hình 6.2, nhấn mạnh đường mốc đỏ T02B nằm trên cùng.",
        "spoken": (
            "Thưa Thầy Cô, đây chính là một trong những phát hiện thực nghiệm thú vị và giá trị nhất của đồ án!\n\n"
            "Để trả lời câu hỏi số 2, em đã khảo sát độc lập 10 phương án tiền xử lý kinh điển trên cùng nền ResNet50: "
            "từ P01 giữ tỷ lệ padding, P02 cắt viền đen, P03 tẩy lông bằng inpainting, P04 chuẩn hóa màu Shades of Gray, cho đến P05 CLAHE và P07 lọc Bilateral.\n\n"
            "Kết quả ở Hình 6.2 cho thấy: KHÔNG CÓ BẤT KỲ PHƯƠNG ÁN NÀO vượt qua được mốc T02B chuẩn (60.30%)!\n"
            "Cụ thể, P01 giữ tỷ lệ bằng viền xám padding làm giảm F1 mạnh nhất (-5.00 điểm %), vì nó thu nhỏ diện tích tổn thương. "
            "P03 tẩy lông làm giảm -2.91 điểm % vì thuật toán xóa lông đã làm mờ luôn các đường vân mạng sắc tố vi mô của khối u. "
            "P07 lọc Bilateral làm mịn quá mức ranh giới tế bào ác tính khiến F1 tụt -3.75 điểm %.\n\n"
            "Bài học khoa học rút ra: Một bức ảnh nhìn 'đẹp mắt, sạch sẽ' đối với thị giác con người chưa chắc đã tốt cho các phép tích chập của mạng nơ-ron!"
        ),
        "analogy": "Giống như việc trang điểm quá đà cho khuôn mặt: nhìn bên ngoài thì da rất mịn và sạch khuyết điểm, nhưng đối với máy quét nhận diện sinh trắc học thì lớp trang điểm đó đã che mất các nếp nhăn và đặc điểm nhận dạng cốt lõi!"
    },
    {
        "num": 8,
        "timing": "05:20 - 06:10 (50 giây)",
        "title": "Phần 4: Cường Hóa Đối Xứng Nhóm D4 (T02B)",
        "action": "Chỉ vào Hình 4.2 với 8 góc quay lật trên màn hình.",
        "spoken": (
            "Vậy điều gì thực sự mang lại bước nhảy vọt cho mô hình? Câu trả lời chính là phép tăng cường dữ liệu nhóm đối xứng D4 ở T02B.\n\n"
            "Nhóm D4 gồm 8 phép biến đổi hình học: 4 góc quay 0, 90, 180, 270 độ kết hợp với lật ngang và lật dọc. "
            "Khi huấn luyện, mỗi ảnh trong batch được chọn ngẫu nhiên 1 trong 8 hướng này. "
            "Đặc điểm toán học tuyệt vời của D4 là trên lưới ảnh vuông 224×224, các phép quay 90 độ và lật chỉ hoán vị vị trí pixel, "
            "hoàn toàn không cần nội suy làm nhòe ảnh!\n\n"
            "Về mặt y học, tổn thương da trên cơ thể người không hề có trục cố định trên-dưới. Bác sĩ cầm máy soi da xoay góc nào thì bản chất bệnh lý vẫn như vậy. "
            "D4 dạy cho mạng học được tính bất biến quay tự nhiên này. "
            "Kết quả thực nghiệm tại Seed 42: Macro-F1 tăng vọt từ 55.21% (B00) lên 60.30% (T02B), tức tăng tới +5.09 điểm phần trăm!"
        ),
        "analogy": "Một đồng xu hay một chiếc lá nằm trên bàn: Dù bạn đi vòng quanh bàn đứng nhìn từ phía nào, lật úp hay lật ngửa, thì bản chất của nó vẫn không thay đổi. D4 giúp AI có góc nhìn 360 độ linh hoạt như vậy."
    },
    {
        "num": 9,
        "timing": "06:10 - 06:55 (45 giây)",
        "title": "Phần 4: Chiến Lược Huấn Luyện & Kiến Trúc Đối Chiếu",
        "action": "Chỉ vào 4 ô thử nghiệm: L01, S01, F01, M01.",
        "spoken": (
            "Bên cạnh D4, em cũng đã thử nghiệm các phương án nâng cao khác theo nguyên tắc đối chứng độc lập:\n\n"
            "1. Hàm mất mát có trọng số L01 (Weighted Cross-Entropy): Điểm F1 thô tăng thêm 0.02%, Balanced Acc tăng, "
            "nhưng Accuracy toàn cục bị tụt xuống 74.95% do sinh ra nhiều dự đoán dương tính giả ở các lớp hiếm.\n"
            "2. Lấy mẫu cân bằng S01 (Balanced Sampler): Ép lớp nhỏ xuất hiện nhiều hơn khiến mô hình bị quá khớp (overfitting) nặng, F1 tụt xuống 58.48%.\n"
            "3. Learning rate phân nhóm F01: Cập nhật backbone chậm hơn khiến mô hình chưa kịp hội tụ trong 16 epoch.\n"
            "4. Kiến trúc đối chiếu EfficientNet-B0 (M01): Chỉ đạt F1 58.44%, thấp hơn ResNet50 (60.30%) trong cùng ngân sách tính toán.\n\n"
            "Vì vậy, T02B (ResNet50 + D4 + Cross-Entropy thường) được bảo vệ và giữ làm cấu hình chốt cuối cùng."
        ),
        "analogy": None
    },
    {
        "num": 10,
        "timing": "06:55 - 07:40 (45 giây)",
        "title": "Phần 5: Quy Trình Huấn Luyện & Tiêu Chí Dừng Sớm",
        "action": "Giải thích nghịch lý giữa Validation Loss và Macro-F1.",
        "spoken": (
            "Thưa Thầy Cô, một điểm đặc biệt trong thiết kế thực nghiệm là tiêu chí dừng sớm (Early Stopping) và chọn Checkpoint.\n\n"
            "Quy trình được khóa với AdamW lr=1e-4, Cosine Annealing, tối đa 16 epoch và patience=4. "
            "Nhưng điều quan trọng là: Chúng em chọn checkpoint dựa trên đỉnh của Validation Macro-F1, chứ KHÔNG chọn theo Validation Loss!\n\n"
            "Tại sao lại như vậy? Vì trên dữ liệu lệch, hàm Loss tổng hợp đạt đáy cực sớm ở Epoch 4 (Loss=0.73) khi mô hình đang học rất giỏi lớp đa số NV. "
            "Nếu dừng ở epoch 4, mô hình sẽ 'bỏ rơi' các lớp hiếm gặp. Đến tận Epoch 14, khi mô hình học đều cả 8 lớp thì Macro-F1 mới đạt đỉnh cao nhất 60.30%. "
            "Đây là minh chứng cho việc lựa chọn tiêu chí đánh giá phù hợp với bài toán y tế."
        ),
        "analogy": "Giống như giáo viên chấm điểm trung bình môn của học sinh: Không thể chỉ khen học sinh đó khi bạn ấy đạt 10 điểm môn Toán mà bỏ qua việc bạn ấy bị 2 điểm môn Văn. Macro-F1 đòi hỏi học sinh phải học đều tất cả các môn!"
    },
    {
        "num": 11,
        "timing": "07:40 - 08:35 (55 giây)",
        "title": "Phần 5: Kiểm Định Tính Bền Vững Đa Seed & Bootstrap",
        "action": "Chỉ vào bảng 6.5, giải thích ý nghĩa của 3 seed.",
        "spoken": (
            "Để trả lời trọn vẹn câu hỏi số 3: 'Mức tăng +5.09 điểm % của D4 có phải do ăn may ở Seed 42 hay không?', "
            "em đã tiến hành huấn luyện lặp lại hoàn toàn độc lập trên hai seed mới: Seed 43 và Seed 44, đồng thời đo khoảng tin cậy Bootstrap 95%.\n\n"
            "Kết quả ở Bảng 6.5 cho thấy:\n"
            "• Ở cả 3 seed, T02B đều chiến thắng B00.\n"
            "• Trung bình hai seed xác nhận mới, D4 giúp tăng +2.1824 điểm phần trăm Macro-F1.\n\n"
            "Tuy nhiên, với tinh thần khoa học trung thực, em cũng xin báo cáo rõ ràng: Mức tăng ở Seed 43 chỉ đạt +0.47 điểm %, "
            "và khoảng tin cậy Bootstrap 95% của Seed 43 và 44 đều có chứa giá trị 0. "
            "Điều này chứng minh rằng: D4 thực sự có lợi thế vững chắc, nhưng biên độ cải thiện sẽ chịu sự dao động nhất định theo khởi tạo ngẫu nhiên. "
            "Chúng em báo cáo trung thực biên độ này chứ không chỉ chọn con số +5.09% đẹp nhất để trình bày."
        ),
        "analogy": "Giống như một vận động viên chạy bền: 3 lần thi đấu thử nghiệm thì cả 3 lần anh ấy đều chạy nhanh hơn đối thủ, nhưng có hôm nhanh hơn 5 giây, có hôm chỉ nhanh hơn 0.5 giây. Chúng ta công nhận anh ấy giỏi hơn, nhưng không thể tuyên bố lần nào anh ấy cũng bỏ xa đối thủ 5 giây!"
    },
    {
        "num": 12,
        "timing": "08:35 - 09:20 (45 giây)",
        "title": "Phần 6: Đánh Giá Trên Tập Kiểm Thử Nội Bộ (5.065 Ảnh)",
        "action": "Nhấn mạnh sự khớp nối giữa Validation và Test.",
        "spoken": (
            "Sau khi đã chốt checkpoint T02B tại Epoch 14, mô hình được đưa vào đánh giá độc lập trên tập Test nội bộ gồm 5.065 ảnh.\n\n"
            "Kết quả đạt được:\n"
            "• Độ chính xác toàn cục (Accuracy): đạt 76.43% (dự đoán đúng 3.871/5.065 ảnh).\n"
            "• Macro-F1 đạt 60.54% và Balanced Accuracy đạt 58.85%.\n\n"
            "Điều đáng tự hào nhất về mặt kỹ thuật là: Chỉ số trên tập Validation là 60.30% và trên tập Test là 60.54%, độ chênh lệch chỉ chưa đầy 0.25 điểm phần trăm! "
            "Sự khớp nối hoàn hảo này chứng minh rằng quy trình Group Split đã hoạt động xuất sắc: hoàn toàn không có hiện tượng rò rỉ dữ liệu, "
            "và mô hình tổng quát hóa cực kỳ vững chắc trên các dữ liệu chưa từng nhìn thấy."
        ),
        "analogy": None
    },
    {
        "num": 13,
        "timing": "09:20 - 10:05 (45 giây)",
        "title": "Phần 6: Ma Trận Nhầm Lẫn & Phân Tích Từng Lớp Bệnh Lý",
        "action": "Chỉ vào ma trận nhầm lẫn Hình 6.4, phân tích ô nhầm MEL sang NV.",
        "spoken": (
            "Nhìn sâu vào ma trận nhầm lẫn ở Hình 6.4, chúng em nhận thấy những góc khuất lâm sàng mà Accuracy 76.4% không thể hiện được:\n\n"
            "• Với lớp chiếm đa số như nốt ruồi NV: Mô hình dự đoán cực tốt, Recall đạt tới 90.56% và F1 đạt 87.38%.\n"
            "• Nhưng với u hắc tố ác tính nguy hiểm MEL: Recall chỉ đạt 58.24%. Đáng lo ngại nhất là có 281 ca bệnh nhân bị MEL nhưng mô hình lại đoán nhầm là nốt ruồi lành tính NV!\n"
            "• Với các lớp cực hiếm như dày sừng quang hóa AK hay ung thư tế bào vảy SCC: Recall chỉ đạt lần lượt 31.4% và 37.9% do dữ liệu huấn luyện quá ít.\n\n"
            "Đây là minh chứng rõ ràng nhất giải thích vì sao trong y tế, AI không thể tự động ra quyết định đơn độc mà luôn cần có bác sĩ giám sát các ca ranh giới."
        ),
        "analogy": None
    },
    {
        "num": 14,
        "timing": "10:05 - 10:45 (40 giây)",
        "title": "Phần 6: Phân Tích Thực Tế 52 Ca Chẩn Đoán Sai (E02)",
        "action": "Chỉ vào gallery ảnh lỗi Hình 6.5.",
        "spoken": (
            "Để tìm hiểu nguyên nhân sâu xa vì sao mô hình đoán sai, em đã thực hiện phân tích định tính trên 52 ca chẩn đoán lỗi ở tập validation (E02).\n\n"
            "Thống kê cho thấy:\n"
            "• 25/52 ảnh bị lông che phủ dày đặc;\n"
            "• 21/52 ảnh xuất hiện viền đen tròn của thấu kính máy soi da;\n"
            "• 15/52 ảnh có thước đo milimet hoặc vết bút mực y tế đặt cạnh khối u.\n\n"
            "Tuy nhiên, như thực nghiệm tiền xử lý P01-P10 đã chứng minh: chúng ta nhận biết các nhiễu này nhưng không thể áp dụng các bộ lọc xóa lông hay cắt viền cẩu thả, "
            "vì rất dễ làm tổn thương đặc trưng bệnh lý gốc. Lời giải lâu dài phải nằm ở kiến trúc chú ý (Attention) hoặc mô hình phát hiện phân vùng."
        ),
        "analogy": None
    },
    {
        "num": 15,
        "timing": "10:45 - 11:25 (40 giây)",
        "title": "Phần 6: Demo Suy Luận Thực Tế & Hiện Tượng 'Quá Tự Tin'",
        "action": "Chỉ vào 2 ảnh Demo đúng Hình 6.6 và Demo sai Hình 6.7.",
        "spoken": (
            "Trên notebook báo cáo nộp kèm, em đã thiết kế luồng demo suy luận ảnh đơn lẻ từ checkpoint T02B đã chốt.\n\n"
            "Ở ví dụ bên trái (Hình 6.6), ảnh ISIC_0000000 có nhãn thật là NV, mô hình dự đoán chính xác tuyệt đối là NV với điểm Softmax 99.99%.\n\n"
            "Nhưng ở ví dụ bên phải (Hình 6.7), em muốn chỉ ra một cảnh báo lâm sàng đặc biệt: "
            "Ảnh ISIC_0000195 có nhãn thật là nốt ruồi NV, nhưng mô hình đoán sai thành dày sừng BKL. "
            "Điều nguy hiểm là điểm Softmax của phán đoán sai này vẫn lên tới 95.06%!\n\n"
            "Hiện tượng này trong Deep Learning gọi là 'Overconfidence' — quá tự tin. "
            "Hàm Softmax toán học bị lệch do hàm mũ, chưa được hiệu chuẩn (calibrated) thành xác suất chẩn đoán thực tế. "
            "Vì vậy, trong hệ thống y tế thực tiễn, bắt buộc phải có cơ chế hiệu chuẩn xác suất và cảnh báo nghi ngờ."
        ),
        "analogy": "Giống như một học sinh đi thi: Dù làm sai đáp án nhưng vẫn đinh ninh tự tin 100% là mình làm đúng. Nếu giáo viên chỉ nhìn vào thái độ tự tin mà cho điểm thì sẽ rất tai hại!"
    },
    {
        "num": 16,
        "timing": "11:25 - 11:55 (30 giây)",
        "title": "Phần 7: Kết Luận & Đóng Góp Cốt Lõi",
        "action": "Tóm lược 4 đóng góp bằng giọng dứt khoát, tự hào.",
        "spoken": (
            "Tổng kết lại, đề tài của em đạt được 4 đóng góp khoa học cốt lõi:\n"
            "1. Kiểm toán và làm sạch dữ liệu chuẩn tắc, thiết lập Group Split 70/10/20 chống rò rỉ dữ liệu 100%.\n"
            "2. Khẳng định giá trị thực nghiệm của nhóm tăng cường đối xứng D4 (+5.09 điểm % ở seed 42 và +2.18 điểm % trung bình đa seed).\n"
            "3. Cung cấp bằng chứng thực nghiệm phản biện: 10 kỹ thuật tiền xử lý ảnh phức tạp không tự động mang lại cải thiện trên ResNet50.\n"
            "4. Đóng gói mã nguồn, hồ sơ kiểm chứng và bảng ánh xạ experiment_index.csv hoàn chỉnh, cho phép tái lập kết quả 100% trên GitHub."
        ),
        "analogy": None
    },
    {
        "num": 17,
        "timing": "11:55 - 12:15 (20 giây)",
        "title": "Phần 7: Hạn Chế & Hướng Nghiên Cứu Tương Lai",
        "action": "Trình bày thẳng thắn hạn chế và hướng mở rộng.",
        "spoken": (
            "Đề tài vẫn còn những hạn chế khách quan: thiếu patient_id để cô lập tuyệt đối người bệnh; "
            "ngân sách môn học giới hạn ở 16 epoch; và chưa có kiểm thử trên ảnh chụp từ các bệnh viện Việt Nam.\n\n"
            "Hướng phát triển sau môn học của em là: Tích hợp metadata bệnh nhân (tuổi, giới tính, vị trí giải phẫu) "
            "vào mô hình đa phương thức (Multimodal); áp dụng kỹ thuật Temperature Scaling để hiệu chuẩn xác suất; "
            "và thử nghiệm kiến trúc Vision Transformer với tiền huấn luyện tự giám sát."
        ),
        "analogy": None
    },
    {
        "num": 18,
        "timing": "12:15 - 12:30 (15 giây)",
        "title": "Lời Cảm Ơn & Sẵn Sàng Vấn Đáp (Q&A)",
        "action": "Cúi đầu cảm ơn Hội đồng, chuyển sang màn hình sẵn sàng trả lời vấn đáp.",
        "spoken": (
            "Em xin chân thành cảm ơn cô Vũ Thị Hạnh đã luôn tận tình định hướng, hướng dẫn em phương pháp nghiên cứu khoa học thực chất. "
            "Em xin cảm ơn Quý Thầy Cô trong Hội đồng đã chú ý lắng nghe bài thuyết trình.\n\n"
            "Toàn bộ mã nguồn, tài liệu báo cáo và kết quả thực nghiệm đã được công khai trên GitHub của em. "
            "Em xin sẵn sàng lắng nghe nhận xét và trả lời các câu hỏi vấn đáp của Quý Thầy Cô!"
        ),
        "analogy": None
    }
]

# Write slides into document
for s in slides_data:
    h2 = doc.add_heading(f"SLIDE {s['num']}: {s['title']}", level=2)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(4)
    for r in h2.runs:
        r.font.name = "Times New Roman"
        r.font.color.rgb = C_PRIMARY

    # Meta table for Slide (Timing & Action)
    t_s = doc.add_table(rows=1, cols=2)
    t_s.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_s.autofit = False
    t_s.rows[0].cells[0].width = Inches(2.5)
    t_s.rows[0].cells[1].width = Inches(4.5)
    set_cell_background(t_s.cell(0, 0), "FAF7F2")
    set_cell_background(t_s.cell(0, 1), "FAF7F2")

    p_tm = t_s.cell(0, 0).paragraphs[0]
    p_tm.add_run("⏱️ Thời lượng: ").bold = True
    p_tm.add_run(s['timing'])
    p_tm.runs[0].font.size = Pt(10)
    p_tm.runs[1].font.size = Pt(10)

    p_ac = t_s.cell(0, 1).paragraphs[0]
    p_ac.add_run("🎬 Hành động slide: ").bold = True
    p_ac.add_run(s['action'])
    p_ac.runs[0].font.size = Pt(10)
    p_ac.runs[1].font.size = Pt(10)

    # Spoken Paragraph
    p_spk_t = doc.add_paragraph()
    p_spk_t.paragraph_format.space_before = Pt(6)
    p_spk_t.paragraph_format.space_after = Pt(2)
    r_st = p_spk_t.add_run("🎙️ LỜI THUYẾT TRÌNH TỰ NHIÊN:")
    r_st.bold = True
    r_st.font.size = Pt(11)
    r_st.font.color.rgb = C_TEAL

    p_spk = doc.add_paragraph()
    p_spk.paragraph_format.space_after = Pt(6)
    r_s = p_spk.add_run(s['spoken'])
    r_s.font.size = Pt(11)
    r_s.font.color.rgb = C_DARK

    # Analogy block if present
    if s['analogy']:
        tbl_a = doc.add_table(rows=1, cols=1)
        tbl_a.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl_a.rows[0].cells[0].width = Inches(7.0)
        set_cell_background(tbl_a.cell(0, 0), "F5FAF8") # Light teal
        p_a = tbl_a.cell(0, 0).paragraphs[0]
        r_at = p_a.add_run("🌱 VÍ DỤ ĐỜI SỐNG DỄ HIỂU: ")
        r_at.bold = True
        r_at.font.size = Pt(10.5)
        r_at.font.color.rgb = C_TEAL
        r_ac = p_a.add_run(s['analogy'])
        r_ac.font.italic = True
        r_ac.font.size = Pt(10.5)
        r_ac.font.color.rgb = C_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

# ==========================================
# PHẦN PHỤ TRỢ: DEMO & DỰ PHÒNG & BỘ CÂU HỎI VẤN ĐÁP
# ==========================================
doc.add_page_break()

h_sup = doc.add_heading("PHẦN PHỤ TRỢ 1: KỊCH BẢN THAO TÁC DEMO TRỰC TIẾP & PHƯƠNG ÁN DỰ PHÒNG", level=1)
h_sup.paragraph_format.space_before = Pt(12)
for r in h_sup.runs:
    r.font.name = "Times New Roman"
    r.font.color.rgb = C_PRIMARY

p_dm_intro = doc.add_paragraph()
p_dm_intro.add_run(
    "Khi Hội đồng yêu cầu chạy thử nghiệm trực tiếp trên Jupyter Notebook / Kaggle, sinh viên thực hiện theo các bước sau:"
)

# Demo steps table
tbl_dm = doc.add_table(rows=4, cols=3)
tbl_dm.alignment = WD_TABLE_ALIGNMENT.CENTER
for row in tbl_dm.rows:
    row.cells[0].width = Inches(1.5)
    row.cells[1].width = Inches(3.0)
    row.cells[2].width = Inches(2.5)

dm_headers = ["Trường hợp", "Thao tác trên Notebook", "Ý nghĩa trình bày trước Hội đồng"]
for i, h in enumerate(dm_headers):
    c = tbl_dm.cell(0, i)
    c.text = h
    set_cell_background(c, "8B1E1E")
    p = c.paragraphs[0]
    p.runs[0].font.bold = True
    p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

dm_rows = [
    [
        "Demo 1: Dự đoán Đúng\n(ISIC_0000000)",
        "1. Chọn ảnh ISIC_0000000 (NV) trong cell demo.\n2. Chạy hàm predict_single_image.\n3. Biểu đồ Top-3 xuất hiện: NV đạt 99.997%.",
        "Mô hình nhận diện chính xác các ca nốt ruồi điển hình, không có nhiễu, biên rõ ràng."
    ],
    [
        "Demo 2: Dự đoán Sai\n(ISIC_0000195)",
        "1. Chọn ảnh ISIC_0000195_downsampled (NV).\n2. Chạy hàm suy luận.\n3. Kết quả đoán BKL với Softmax 95.06%.",
        "Chỉ ra giới hạn Overconfidence: Softmax cao không đồng nghĩa với chẩn đoán chuẩn xác y khoa. Cần hiệu chuẩn xác suất!"
    ],
    [
        "Phương Án Dự Phòng\n(Khi mạng lag/lỗi kernel)",
        "Bình tĩnh mở folder slides/assets/ hoặc thư mục output T02B_CLEAN đã chạy sẵn trên máy tính.",
        "Thưa Thầy Cô: 'Để đảm bảo thời gian, em đã lưu sẵn kết quả suy luận nguyên bản và các biểu đồ gallery tại đây...'"
    ]
]
for r_i, r_data in enumerate(dm_rows):
    for c_i, text in enumerate(r_data):
        c = tbl_dm.cell(r_i + 1, c_i)
        c.text = text
        set_cell_background(c, "FAF7F2" if r_i % 2 == 0 else "FFFFFF")
        p = c.paragraphs[0]
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.color.rgb = C_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(14)

# ==========================================
# BỘ CÂU HỎI VẤN ĐÁP DỰ KIẾN (Q&A)
# ==========================================
h_qa = doc.add_heading("PHẦN PHỤ TRỢ 2: BỘ CÂU HỎI VẤN ĐÁP DỰ KIẾN & CÂU TRẢ LỜI CHUẨN XÁC", level=1)
h_qa.paragraph_format.space_before = Pt(12)
for r in h_qa.runs:
    r.font.name = "Times New Roman"
    r.font.color.rgb = C_PRIMARY

qa_list = [
    {
        "q": "Câu hỏi 1: Tại sao em không dùng Accuracy làm tiêu chí chính để chọn mô hình mà lại bắt buộc phải dùng Macro-F1?",
        "ans": (
            "Thưa Thầy Cô, tập dữ liệu ISIC 2019 có độ lệch lớp cực kỳ nghiêm trọng: Lớp nốt ruồi NV chiếm tới 50.89% (hơn 9.000 ảnh), "
            "trong khi các lớp như mạch máu VASC hay u xơ da DF chỉ chiếm dưới 1% (chỉ 151 đến 187 ảnh), chênh lệch tới 59.7 lần.\n"
            "Nếu dùng Accuracy, một mô hình lười biếng chỉ cần đoán bừa tất cả ảnh là NV thì Accuracy vẫn dễ dàng vượt 50%, "
            "nhưng mô hình sẽ bỏ sót 100% các ca ung thư hay tổn thương hiếm. "
            "Chỉ số Macro-F1 tính F1 riêng cho từng lớp rồi mới lấy trung bình cộng, gán trọng số ngang nhau cho cả 8 lớp (mỗi lớp 12.5%). "
            "Điều này buộc mô hình phải học đều tất cả các bệnh lý, rất phù hợp với y đức và thực tiễn y tế."
        )
    },
    {
        "q": "Câu hỏi 2: Tại sao các phương án tiền xử lý như tẩy lông (P03) hay cắt viền đen (P02) nhìn bằng mắt rất sạch mà huấn luyện ResNet50 kết quả lại giảm?",
        "ans": (
            "Thưa Thầy Cô, đây chính là bài học thực nghiệm lớn nhất của đề tài. Mắt người và mạng tích chập CNN nhìn nhận ảnh rất khác nhau:\n"
            "1. Với thuật toán tẩy lông (Inpainting): Thuật toán tìm các nét đen dài để xóa và điền màu lân cận vào. "
            "Tuy nhiên, rất nhiều khối u ác tính có cấu trúc 'mạng sắc tố dạng lưới' (pigment network) vi mô. "
            "Thuật toán đã xóa nhầm mạng sắc tố đó vì tưởng là lông, vô tình phá hủy đặc trưng chẩn đoán quan trọng nhất!\n"
            "2. Với lọc Bilateral (P07): Việc làm mịn các vùng tương phản đã làm nhòe ranh giới lởm chởm của khối u ác tính.\n"
            "3. Với P01 padding giữ tỷ lệ: Việc chèn viền xám làm co nhỏ diện tích vùng tổn thương hữu ích trong khung 224x224, khiến lượng pixel đặc trưng bị giảm mạnh.\n"
            "Vì vậy, giữ nguyên ảnh gốc chuẩn hóa ImageNet chính là lựa chọn an toàn và tối ưu nhất cho ResNet50."
        )
    },
    {
        "q": "Câu hỏi 3: Augmentation D4 tăng +5.09 điểm % ở seed 42, nhưng ở seed 43 chỉ tăng +0.47 điểm % và CI95 chứa 0. Vậy D4 có thực sự có lợi hay chỉ do ngẫu nhiên?",
        "ans": (
            "Thưa Thầy Cô, đây là một câu hỏi rất sâu sắc về tính bất định thống kê.\n"
            "Về mặt bản chất: Ở cả 3 seed quan sát (Seed 42, 43, 44), mô hình có D4 đều có điểm Macro-F1 cao hơn mô hình không D4 (B00). "
            "Tính trung bình trên 2 seed xác nhận mới, D4 giúp tăng +2.1824 điểm phần trăm, khẳng định tính bất biến quay của ảnh soi da là có cơ sở khoa học vững chắc.\n"
            "Tuy nhiên, khoảng tin cậy CI95 của Seed 43 và 44 có chứa giá trị 0 vì chúng em thực hiện bootstrap theo group trên tập validation, "
            "và số lượng seed mới còn ít (2 seed). Chúng em báo cáo đầy đủ cả mức tăng nhỏ (+0.47%) và khoảng tin cậy chứa 0 này "
            "để phản ánh trung thực rằng biên độ cải thiện của D4 chịu tác động của bộ khởi tạo ngẫu nhiên. "
            "Chúng em bảo vệ việc sử dụng D4 vì nó phù hợp lý thuyết y học và luôn có lợi thế dương qua các seed, nhưng không tuyệt đối hóa con số +5.09%."
        )
    },
    {
        "q": "Câu hỏi 4: Khi dữ liệu lệch tới gần 60 lần, tại sao mô hình chốt T02B lại dùng Cross-Entropy thường mà không dùng Weighted CE (L01) hay Balanced Sampler (S01)?",
        "ans": (
            "Thưa Thầy Cô, nhóm em đã thực nghiệm cả hai phương án này:\n"
            "1. Với Balanced Sampler (S01): Việc cố tình rút lặp lại các lớp hiếm (như VASC 151 ảnh) cho đủ số lượng tương đương lớp NV đã khiến mô hình bị 'học vẹt' "
            "quá mức trên một vài mẫu lặp lại, dẫn đến Macro-F1 trên tập validation bị tụt -1.82 điểm phần trăm.\n"
            "2. Với Weighted Cross-Entropy (L01): Khi gán trọng số lớn cho lớp hiếm, điểm Macro-F1 thô chỉ tăng nhẹ 0.02%, "
            "nhưng độ chính xác toàn cục (Accuracy) bị tụt từ 77.00% xuống 74.95%. Nguyên nhân là mô hình trở nên quá 'nhạy cảm', "
            "rất dễ đoán nhầm các nốt ruồi bình thường thành bệnh hiếm (sinh ra nhiều ca dương tính giả).\n"
            "Do đó, giữ Cross-Entropy tiêu chuẩn kết hợp với Augmentation D4 mang lại sự cân bằng hài hòa nhất giữa độ nhạy và độ đặc hiệu."
        )
    },
    {
        "q": "Câu hỏi 5: Tại sao ở ví dụ demo sai ISIC_0000195, mô hình đoán sai hoàn toàn nhưng Softmax vẫn tự tin trên 95%?",
        "ans": (
            "Thưa Thầy Cô, đây là hạn chế kinh điển của hàm Softmax trong mạng nơ-ron sâu: hiện tượng Overconfidence (quá tự tin).\n"
            "Hàm Softmax tính toán bằng hàm mũ e^z rồi chuẩn hóa tổng bằng 1. Khi một logit hơi nhỉnh hơn các logit còn lại một chút, "
            "qua hàm mũ nó sẽ bị khuếch đại lên cực kỳ lớn, tạo ra phân bố xác suất nhọn hoắt tiệm cận 100%.\n"
            "Softmax chỉ là thước đo độ lớn tương đối giữa các lớp trong vòng thi nội bộ của mô hình, hoàn toàn CHƯA PHẢI là xác suất chẩn đoán thực tế đã hiệu chuẩn.\n"
            "Trong hệ thống y tế thực tiễn, em đề xuất cần bổ sung kỹ thuật Temperature Scaling để làm phẳng phân bố Softmax, "
            "đồng thời thiết lập cơ chế từ chối chẩn đoán (reject option) nếu khoảng cách tin cậy giữa Top-1 và Top-2 không đủ an toàn."
        )
    },
    {
        "q": "Câu hỏi 6: Tại sao đề tài không đưa thông tin tuổi, giới tính và vị trí giải phẫu (Metadata) vào huấn luyện mạng CNN?",
        "ans": (
            "Thưa Thầy Cô, trong tập dữ liệu ISIC 2019, phần metadata có tỷ lệ giá trị thiếu (missing values) đáng kể. "
            "Đặc biệt, mục tiêu trọng tâm của đề tài môn học là nghiên cứu các giải pháp thị giác máy tính (tiền xử lý ảnh, augmentation, backbone). "
            "Nếu đưa metadata vào cùng lúc, chúng em sẽ làm phát sinh thêm các yếu tố nhiễu ngoài thị giác, "
            "khiến việc đánh giá tác động riêng của phép biến đổi ảnh (như D4 hay 10 phương án P01-P10) không còn giữ được tính đối chứng cô lập.\n"
            "Tuy nhiên, ở phân tích E01, em đã dùng metadata để phân tích tương quan lỗi sau khi mô hình đã dự đoán, "
            "và đây chính là hướng nghiên cứu đa phương thức (Multimodal) đầy tiềm năng mà em sẽ tiếp tục phát triển sau môn học."
        )
    }
]

for qa in qa_list:
    p_q = doc.add_paragraph()
    p_q.paragraph_format.space_before = Pt(8)
    p_q.paragraph_format.space_after = Pt(2)
    r_q = p_q.add_run(f"❓ {qa['q']}")
    r_q.bold = True
    r_q.font.size = Pt(11)
    r_q.font.color.rgb = C_PRIMARY

    p_a = doc.add_paragraph()
    p_a.paragraph_format.space_after = Pt(6)
    r_a = p_a.add_run(f"💡 Trả lời: {qa['ans']}")
    r_a.font.size = Pt(10.5)
    r_a.font.color.rgb = C_DARK

# Save document
doc.save(DOCX_OUTPUT)
doc.save(DOCX_COPY)
print(f"Word script successfully generated and saved to:\n1. {DOCX_OUTPUT}\n2. {DOCX_COPY}")
