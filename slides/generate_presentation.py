import os
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# 1. Paths & Constants
WORKSPACE = r"D:\Nhom8_Phan_Loai_Ton_Thuong_Tren_Da_ISIC2019"
ASSETS_DIR = os.path.join(WORKSPACE, "slides", "assets")
PPTX_OUTPUT = os.path.join(WORKSPACE, "slides", "ISIC2019_Thuyet_trinh_12_phut.pptx")

# 2. Color Palette (Cream, Deep Crimson, Charcoal, Soft Sand, Deep Teal)
COLOR_BG = RGBColor(250, 247, 242)          # Cream #FAF7F2
COLOR_CARD = RGBColor(255, 255, 255)        # Pure White #FFFFFF
COLOR_BORDER = RGBColor(228, 222, 212)      # Soft Sand #E4DED4
COLOR_PRIMARY = RGBColor(139, 30, 30)       # Deep Crimson / Đỏ trầm #8B1E1E
COLOR_PRIMARY_DARK = RGBColor(105, 20, 20)  # Very dark crimson
COLOR_TEXT_DARK = RGBColor(34, 34, 34)      # Dark Charcoal #222222
COLOR_TEXT_MUTED = RGBColor(90, 90, 90)     # Muted Gray #5A5A5A
COLOR_TEAL = RGBColor(27, 94, 85)           # Deep Teal #1B5E55
COLOR_PILL_RED_BG = RGBColor(253, 238, 238) # Light red pill #FDEEEE
COLOR_PILL_TEAL_BG = RGBColor(238, 248, 246)# Light teal pill #EEF8F6

prs = pptx.Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_slide_background(slide):
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5)
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = COLOR_BG
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, section_tag, title, takeaway, is_teal=False):
    # Category tag pill
    pill = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(3.2), Inches(0.32)
    )
    pill.fill.solid()
    pill.fill.fore_color.rgb = COLOR_PILL_TEAL_BG if is_teal else COLOR_PILL_RED_BG
    pill.line.color.rgb = COLOR_TEAL if is_teal else COLOR_PRIMARY
    pill.line.width = Pt(1)
    tf_pill = pill.text_frame
    tf_pill.word_wrap = True
    p_pill = tf_pill.paragraphs[0]
    p_pill.text = section_tag.upper()
    p_pill.font.size = Pt(10)
    p_pill.font.bold = True
    p_pill.font.color.rgb = COLOR_TEAL if is_teal else COLOR_PRIMARY
    p_pill.alignment = PP_ALIGN.CENTER

    # Title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.82), Inches(11.7), Inches(0.55))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.name = "Segoe UI"
    p_title.font.color.rgb = COLOR_PRIMARY

    # Takeaway / Subtitle
    tb_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.38), Inches(11.7), Inches(0.4))
    tf_sub = tb_sub.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "💡 Thông điệp: " + takeaway
    p_sub.font.size = Pt(12)
    p_sub.font.italic = True
    p_sub.font.name = "Segoe UI"
    p_sub.font.color.rgb = COLOR_TEXT_MUTED

def add_footer(slide, current_idx, total_slides=18):
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = f"Đồ Án Khai Phá Dữ Liệu | Đề Tài: Phân Loại Tổn Thương Da ISIC 2019 (Nhóm 8 - Nguyễn Tuấn Đức) | Slide {current_idx}/{total_slides}"
    p.font.size = Pt(9.5)
    p.font.name = "Segoe UI"
    p.font.color.rgb = COLOR_TEXT_MUTED
    p.alignment = PP_ALIGN.RIGHT

def add_card(slide, left, top, width, height, title=None, bg_color=COLOR_CARD, border_color=COLOR_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)
    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.45))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.name = "Segoe UI"
        p.font.color.rgb = COLOR_PRIMARY
    return card

# ==========================================
# SLIDE 1: TRANG BÌA (TITLE SLIDE)
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

# Decorative crimson header strip
dec_strip = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.2))
dec_strip.fill.solid()
dec_strip.fill.fore_color.rgb = COLOR_PRIMARY
dec_strip.line.fill.background()

# University Logo
logo_path = os.path.join(ASSETS_DIR, "image1.png")
if os.path.exists(logo_path):
    s1.shapes.add_picture(logo_path, Inches(0.9), Inches(0.65), height=Inches(1.1))

# Uni name text
tb_uni = s1.shapes.add_textbox(Inches(2.2), Inches(0.7), Inches(10), Inches(0.8))
tf_uni = tb_uni.text_frame
p_u1 = tf_uni.paragraphs[0]
p_u1.text = "PHÂN HIỆU TRƯỜNG ĐẠI HỌC THỦY LỢI - BỘ MÔN CÔNG NGHỆ THÔNG TIN"
p_u1.font.size = Pt(13)
p_u1.font.bold = True
p_u1.font.color.rgb = COLOR_PRIMARY
p_u2 = tf_uni.add_paragraph()
p_u2.text = "BÁO CÁO BẢO VỆ ĐỒ ÁN MÔN HỌC: KHAI PHÁ DỮ LIỆU"
p_u2.font.size = Pt(11)
p_u2.font.bold = True
p_u2.font.color.rgb = COLOR_TEXT_MUTED

# Big Title Card
card_main = add_card(s1, Inches(0.9), Inches(1.9), Inches(11.533), Inches(2.7), bg_color=RGBColor(255, 255, 255), border_color=COLOR_PRIMARY)
tb_title1 = s1.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(11.0), Inches(1.5))
tf_t1 = tb_title1.text_frame
tf_t1.word_wrap = True
p_t1 = tf_t1.paragraphs[0]
p_t1.text = "PHÂN LOẠI TÁM NHÓM TỔN THƯƠNG DA\nTRÊN BỘ DỮ LIỆU ISIC 2019"
p_t1.font.size = Pt(28)
p_t1.font.bold = True
p_t1.font.name = "Segoe UI"
p_t1.font.color.rgb = COLOR_PRIMARY

p_t2 = tf_t1.add_paragraph()
p_t2.text = "Nghiên cứu tiền xử lý ảnh và chiến lược huấn luyện trong quy trình đánh giá có đối chứng"
p_t2.font.size = Pt(14)
p_t2.font.italic = True
p_t2.font.name = "Segoe UI"
p_t2.font.color.rgb = COLOR_TEXT_DARK

# Student & Instructor Card
card_info = add_card(s1, Inches(0.9), Inches(4.8), Inches(11.533), Inches(1.8))
tb_info = s1.shapes.add_textbox(Inches(1.2), Inches(4.95), Inches(11.0), Inches(1.5))
tf_info = tb_info.text_frame
tf_info.word_wrap = True

p_i1 = tf_info.paragraphs[0]
p_i1.text = "👤 Sinh viên thực hiện:  Nguyễn Tuấn Đức    |    Mã số sinh viên: 2351067091    |    Lớp: S26-65CNTT (Nhóm 8)"
p_i1.font.size = Pt(13)
p_i1.font.bold = True
p_i1.font.color.rgb = COLOR_TEXT_DARK

p_i2 = tf_info.add_paragraph()
p_i2.text = "👩‍🏫 Giảng viên hướng dẫn: ThS. Vũ Thị Hạnh"
p_i2.font.size = Pt(13)
p_i2.font.bold = True
p_i2.font.color.rgb = COLOR_PRIMARY

p_i3 = tf_info.add_paragraph()
p_i3.text = "📅 Thời lượng thuyết trình: 12 Phút    •    Nền tảng thực nghiệm: Kaggle GPU Tesla T4 & PyTorch"
p_i3.font.size = Pt(11.5)
p_i3.font.color.rgb = COLOR_TEXT_MUTED

add_footer(s1, 1)

# ==========================================
# SLIDE 2: BÀI TOÁN & ĐỘNG LỰC Y TẾ
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "Phần 1: Giới thiệu bài toán", "Phân Loại Tổn Thương Da & Động Lực Y Tế", "Ứng dụng thị giác máy tính hỗ trợ sàng lọc sớm tổn thương da từ ảnh soi da dermoscopy")

# Left Card: Đặc thù bài toán
add_card(s2, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="🩺 Bài Toán Phân Loại Y Tế")
tb_c1 = s2.shapes.add_textbox(Inches(1.0), Inches(2.55), Inches(5.25), Inches(4.0))
tf_c1 = tb_c1.text_frame
tf_c1.word_wrap = True

def add_bullet(tf, title, desc):
    p = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
    p.text = f"• {title}: "
    p.font.bold = True
    p.font.size = Pt(12.5)
    p.font.color.rgb = COLOR_TEXT_DARK
    r = p.add_run()
    r.text = desc
    r.font.bold = False
    r.font.color.rgb = COLOR_TEXT_MUTED
    p.space_after = Pt(10)

add_bullet(tf_c1, "Đầu vào", "Ảnh màu soi da (dermoscopy) với độ phóng đại quang học, giúp thấy cấu trúc dưới lớp sừng của da.")
add_bullet(tf_c1, "Đầu ra", "Dự đoán 1 trong 8 nhóm bệnh lý (Melanoma ác tính, Ung thư tế bào đáy, Dày sừng, Nốt ruồi...).")
add_bullet(tf_c1, "Vai trò thực tế", "Hỗ trợ sàng lọc ban đầu, cảnh báo nguy cơ sớm; không phải tất cả 8 nhóm đều là ung thư.")
add_bullet(tf_c1, "Ranh giới chẩn đoán", "AI hỗ trợ sàng lọc chứ KHÔNG thay thế sinh thiết mô bệnh học hay kết luận của bác sĩ chuyên khoa da liễu.")

# Right Card: Thách thức thị giác
add_card(s2, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="⚡ Thách Thức Thị Giác Cốt Lõi")
tb_c2 = s2.shapes.add_textbox(Inches(7.0), Inches(2.55), Inches(5.3), Inches(4.0))
tf_c2 = tb_c2.text_frame
tf_c2.word_wrap = True

add_bullet(tf_c2, "Biến thiên nội lớp rất lớn", "Cùng một loại bệnh (ví dụ nốt ruồi NV) nhưng có thể phẳng, gồ ghề, màu đen nhạt hoặc sẫm tùy cơ địa.")
add_bullet(tf_c2, "Tương đồng liên lớp rất cao", "U hắc tố ác tính (MEL) ở giai đoạn sớm có hình thái cực kỳ giống nốt ruồi lành tính (NV) hoặc dày sừng (BKL).")
add_bullet(tf_c2, "Nhiễu thị giác phức tạp", "Ảnh chụp lâm sàng bị che phủ bởi lông rậm, vết mực đánh dấu, thước đo, bọt khí và viền đen tròn của ống kính.")
add_bullet(tf_c2, "Mất cân bằng mẫu", "Có bệnh gặp rất nhiều (NV > 50%), có bệnh cực kỳ hiếm gặp (VASC, DF < 1%), gây lệch chẩn đoán.")

add_footer(s2, 2)

# ==========================================
# SLIDE 3: MỤC TIÊU & 3 CÂU HỎI NGHIÊN CỨU
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "Phần 1: Giới thiệu bài toán", "Mục Tiêu & Ba Câu Hỏi Nghiên Cứu Cốt Lõi", "Xây dựng quy trình đánh giá có đối chứng khoa học, kiên quyết không chạy đua điểm số ảo")

# 3 Column cards
col_w = Inches(3.68)
gap = Inches(0.34)

# Col 1
add_card(s3, Inches(0.8), Inches(1.9), col_w, Inches(4.9), title="❓ Câu Hỏi 1: Augmentation")
tb_q1 = s3.shapes.add_textbox(Inches(0.95), Inches(2.55), col_w - Inches(0.3), Inches(4.0))
tf_q1 = tb_q1.text_frame
tf_q1.word_wrap = True
add_bullet(tf_q1, "Giả thuyết", "Ảnh soi da không có hướng cố định trên-dưới; tính đối xứng quay D4 có giúp mô hình phân loại tốt hơn?")
add_bullet(tf_q1, "Phương án", "So sánh đối chứng công bằng: B00 (không xoay lật) vs T02B (nhóm D4 - 8 phép quay/lật) trên cùng ResNet50.")
add_bullet(tf_q1, "Kỳ vọng", "Nâng cao khả năng tổng quát hóa, giảm phụ thuộc vào hướng chụp của máy soi da.")

# Col 2
add_card(s3, Inches(0.8) + col_w + gap, Inches(1.9), col_w, Inches(4.9), title="❓ Câu Hỏi 2: Tiền Xử Lý")
tb_q2 = s3.shapes.add_textbox(Inches(0.8) + col_w + gap + Inches(0.15), Inches(2.55), col_w - Inches(0.3), Inches(4.0))
tf_q2 = tb_q2.text_frame
tf_q2.word_wrap = True
add_bullet(tf_q2, "Giả thuyết", "Các kỹ thuật can thiệp pixel (tẩy lông, cân bằng sáng, cắt viền, lọc mịn) có thực sự tăng chất lượng?")
add_bullet(tf_q2, "Phương án", "Khảo sát độc lập 10 phương án tiền xử lý (P01 đến P10) trên cùng nền mô hình T02B đã khóa.")
add_bullet(tf_q2, "Kỳ vọng", "Xác định xem 'ảnh trông sạch hơn' có đồng nghĩa với việc mạng nơ-ron học tốt hơn hay không.")

# Col 3
add_card(s3, Inches(0.8) + (col_w + gap)*2, Inches(1.9), col_w, Inches(4.9), title="❓ Câu Hỏi 3: Độ Bền Vững")
tb_q3 = s3.shapes.add_textbox(Inches(0.8) + (col_w + gap)*2 + Inches(0.15), Inches(2.55), col_w - Inches(0.3), Inches(4.0))
tf_q3 = tb_q3.text_frame
tf_q3.word_wrap = True
add_bullet(tf_q3, "Giả thuyết", "Mức cải thiện quan sát được ở một lần chạy (seed 42) có lặp lại bền vững khi đổi sang các seed khác?")
add_bullet(tf_q3, "Phương án", "Huấn luyện lại độc lập trên Seed 43, Seed 44 và đo khoảng tin cậy Bootstrap 95% theo group.")
add_bullet(tf_q3, "Kỳ vọng", "Ngăn chặn kết luận vội vàng từ sự may mắn ngẫu nhiên của một seed khởi tạo.")

add_footer(s3, 3)

# ==========================================
# SLIDE 4: TẬP DỮ LIỆU & KIỂM TOÁN LÀM SẠCH
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "Phần 2: Dữ liệu và phân tích khám phá (EDA)", "Kiểm Toán Dữ Liệu & Làm Sạch Trước Khi Khóa", "Làm sạch và kiểm tra toàn vẹn trước khi huấn luyện để ngăn chặn rò rỉ dữ liệu (leakage)")

# Left Card: KPIs kiểm toán
add_card(s4, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="🔍 Kết Quả Kiểm Toán Dữ Liệu")
tb_aud = s4.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(5.25), Inches(4.1))
tf_aud = tb_aud.text_frame
tf_aud.word_wrap = True

add_bullet(tf_aud, "Tổng ảnh ban đầu", "25.331 ảnh được cung cấp từ ISIC 2019 (tổng hợp HAM10000, BCN20000, MSK).")
add_bullet(tf_aud, "48 Ảnh trùng dư", "Trùng lặp chính xác nội dung byte (exact duplicate) -> Phải gom chung vào cùng 1 nhóm.")
add_bullet(tf_aud, "4 Ảnh xung đột nhãn (Bị loại)", "Cùng một nội dung ảnh nhưng được gán 2 bệnh khác nhau! Loại bỏ hoàn toàn để không làm sai tín hiệu học.")
add_bullet(tf_aud, "25.327 Ảnh chốt", "Manifest chuẩn được khóa cứng, đối chiếu bằng mã băm SHA-256 từng file.")
add_bullet(tf_aud, "Kiểm tra rò rỉ (Crossing = 0)", "Đảm bảo không có định danh tổn thương hay mã băm nào xuất hiện đồng thời ở 2 tập.")

# Right Card: 8 Nhóm tổn thương
add_card(s4, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="📋 Tám Nhóm Nhãn Bệnh Học Mục Tiêu")
tb_lbl = s4.shapes.add_textbox(Inches(7.0), Inches(2.5), Inches(5.3), Inches(4.1))
tf_lbl = tb_lbl.text_frame
tf_lbl.word_wrap = True

labels_data = [
    ("MEL", "Melanoma", "U hắc tố ác tính (nguy hiểm nhất)"),
    ("NV", "Melanocytic nevus", "Nốt ruồi tế bào hắc tố lành tính"),
    ("BCC", "Basal cell carcinoma", "Ung thư biểu mô tế bào đáy"),
    ("AK", "Actinic keratosis", "Dày sừng quang hóa (tiền ung thư)"),
    ("BKL", "Benign keratosis", "Nhóm dày sừng lành tính"),
    ("DF", "Dermatofibroma", "U xơ da lành tính"),
    ("VASC", "Vascular lesion", "Nhóm tổn thương mạch máu"),
    ("SCC", "Squamous cell carcinoma", "Ung thư biểu mô tế bào vảy")
]
for code, eng, vi in labels_data:
    p = tf_lbl.add_paragraph() if len(tf_lbl.paragraphs[0].text) > 0 else tf_lbl.paragraphs[0]
    p.text = f"• {code}: "
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_PRIMARY
    r1 = p.add_run()
    r1.text = f"{eng} — "
    r1.font.bold = True
    r1.font.color.rgb = COLOR_TEXT_DARK
    r2 = p.add_run()
    r2.text = vi
    r2.font.bold = False
    r2.font.color.rgb = COLOR_TEXT_MUTED
    p.space_after = Pt(4)

add_footer(s4, 4)

# ==========================================
# SLIDE 5: MẤT CÂN BẰNG LỚP & GROUP SPLIT
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "Phần 2: Dữ liệu và phân tích khám phá (EDA)", "Mất Cân Bằng Cực Đoan & Phân Chia Tập (Group Split)", "Chênh lệch tới 59.7 lần giữa các lớp; phân chia theo nhóm tổn thương để chống học vẹt")

# Left Side: Biểu đồ phân bố
add_card(s5, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="📊 Phân Bố Lớp Dữ Liệu Train (Hình 3.1)")
img_dist = os.path.join(ASSETS_DIR, "image2.png")
if os.path.exists(img_dist):
    s5.shapes.add_picture(img_dist, Inches(0.95), Inches(2.6), width=Inches(5.35))

tb_c_callout = s5.shapes.add_textbox(Inches(0.95), Inches(5.1), Inches(5.35), Inches(1.5))
tf_cc = tb_c_callout.text_frame
tf_cc.word_wrap = True
p_cc1 = tf_cc.paragraphs[0]
p_cc1.text = "⚠️ Mất cân bằng lớp nghiêm trọng:"
p_cc1.font.bold = True
p_cc1.font.size = Pt(12)
p_cc1.font.color.rgb = COLOR_PRIMARY
p_cc2 = tf_cc.add_paragraph()
p_cc2.text = "• NV chiếm 50.89% (9.019 ảnh), trong khi VASC chỉ có 151 ảnh (0.85%)."
p_cc2.font.size = Pt(11.5)
p_cc2.font.color.rgb = COLOR_TEXT_DARK
p_cc3 = tf_cc.add_paragraph()
p_cc3.text = "• Tỷ lệ chênh lệch lên tới 59.73 lần! Nếu đoán bừa toàn bộ là NV, Accuracy vẫn đạt hơn 50% nhưng mô hình hoàn toàn vô dụng trong y tế."
p_cc3.font.size = Pt(11)
p_cc3.font.color.rgb = COLOR_TEXT_MUTED

# Right Side: Group Split 70/10/20
add_card(s5, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="🛡️ Phân Chia Group Split Chống Rò Rỉ")
tb_sp = s5.shapes.add_textbox(Inches(7.0), Inches(2.55), Inches(5.3), Inches(4.0))
tf_sp = tb_sp.text_frame
tf_sp.word_wrap = True

add_bullet(tf_sp, "Quy tắc Group Split", "Gom tất cả ảnh có cùng lesion_id (cùng 1 vết tổn thương chụp nhiều góc/nhiều lần) vào chung một tập.")
add_bullet(tf_sp, "Quy mô 3 tập", "• Train: 17.723 ảnh (70%)\n• Validation: 2.539 ảnh (10%)\n• Test nội bộ: 5.065 ảnh (20%)")
add_bullet(tf_sp, "Ví dụ đời sống minh họa", "Giống như thi học kỳ: không thể cho học sinh làm bài tập có câu hỏi và đáp án giống hệt đề thi chính thức được!")
add_bullet(tf_sp, "Tiêu chuẩn đánh giá", "Sử dụng Macro-F1 (trung bình F1 của 8 lớp, mỗi lớp trọng số ngang nhau) làm thước đo chính, không dùng Accuracy đơn thuần.")

add_footer(s5, 5)

# ==========================================
# SLIDE 6: PIPELINE TIỀN XỬ LÝ CHUẨN (T02B)
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "Phần 3: Tiền xử lý ảnh", "Pipeline Tiền Xử Lý Chuẩn Của Mô Hình T02B", "Đơn giản, chuẩn hóa và bảo toàn đặc trưng bệnh học gốc của ảnh soi da")

# Left Card: 4 Bước Pipeline
add_card(s6, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="⚙️ 4 Bước Xử Lý Tuần Tự")
tb_pipe = s6.shapes.add_textbox(Inches(1.0), Inches(2.55), Inches(5.25), Inches(4.0))
tf_pipe = tb_pipe.text_frame
tf_pipe.word_wrap = True

add_bullet(tf_pipe, "1. Đọc ảnh RGB", "Giải mã file ảnh JPEG gốc sang 3 kênh màu RGB chuẩn, loại bỏ các kênh alpha dư thừa.")
add_bullet(tf_pipe, "2. Resize Bilinear 224×224", "Đưa ảnh về kích thước đồng nhất phù hợp với đầu vào ResNet50.")
add_bullet(tf_pipe, "3. Chuyển Tensor [0, 1]", "Chuẩn hóa giá trị pixel từ thang nguyên [0, 255] về ma trận số thực [0.0, 1.0].")
add_bullet(tf_pipe, "4. Normalize ImageNet", "Trừ mean (0.485, 0.456, 0.406) và chia std (0.229, 0.224, 0.225) theo chuẩn pretrained weights.")
add_bullet(tf_pipe, "Nguyên tắc thiết kế", "Bảo toàn nguyên vẹn cấu trúc tế bào; kiên quyết không áp dụng bộ lọc tùy tiện khi chưa có đối chứng.")

# Right Card: Minh họa hình 4.1
add_card(s6, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="🖼️ Minh Họa Trước & Sau Resize (Hình 4.1)")
img_res = os.path.join(ASSETS_DIR, "image4.png")
if os.path.exists(img_res):
    s6.shapes.add_picture(img_res, Inches(7.0), Inches(2.6), width=Inches(5.3))

tb_res_note = s6.shapes.add_textbox(Inches(7.0), Inches(5.25), Inches(5.3), Inches(1.4))
tf_rn = tb_res_note.text_frame
tf_rn.word_wrap = True
p_rn1 = tf_rn.paragraphs[0]
p_rn1.text = "🔍 Quan sát thực nghiệm:"
p_rn1.font.bold = True
p_rn1.font.size = Pt(12)
p_rn1.font.color.rgb = COLOR_PRIMARY
p_rn2 = tf_rn.add_paragraph()
p_rn2.text = "• Resize trực tiếp có thể làm méo tỷ lệ nếu ảnh gốc không vuông, nhưng bù lại giữ được diện tích vùng tổn thương lớn nhất trong khung 224x224."
p_rn2.font.size = Pt(11.5)
p_rn2.font.color.rgb = COLOR_TEXT_DARK

add_footer(s6, 6)

# ==========================================
# SLIDE 7: KHẢO SÁT 10 PHƯƠNG ÁN TIỀN XỬ LÝ (P01 - P10)
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "Phần 3: Tiền xử lý ảnh", "Khảo Sát 10 Phương Án Tiền Xử Lý (P01 – P10)", "Tiền xử lý nhìn 'đẹp mắt' không đồng nghĩa với việc mô hình phân loại tốt hơn")

# Left Side: Image 6.2
add_card(s7, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="📉 Kết Quả 10 Phương Án So Với Mốc T02B (Hình 6.2)")
img_p10 = os.path.join(ASSETS_DIR, "image7.png")
if os.path.exists(img_p10):
    s7.shapes.add_picture(img_p10, Inches(0.95), Inches(2.6), width=Inches(5.35))

tb_p10_callout = s7.shapes.add_textbox(Inches(0.95), Inches(5.2), Inches(5.35), Inches(1.5))
tf_p10c = tb_p10_callout.text_frame
tf_p10c.word_wrap = True
p_pc1 = tf_p10c.paragraphs[0]
p_pc1.text = "❌ Không phương án nào vượt mốc T02B (60.30%)!"
p_pc1.font.bold = True
p_pc1.font.size = Pt(12)
p_pc1.font.color.rgb = COLOR_PRIMARY
p_pc2 = tf_p10c.add_paragraph()
p_pc2.text = "Tất cả 10 kỹ thuật can thiệp pixel đều cho kết quả Macro-F1 thấp hơn hoặc chỉ xấp xỉ ảnh gốc chuẩn hóa."
p_pc2.font.size = Pt(11)
p_pc2.font.color.rgb = COLOR_TEXT_MUTED

# Right Side: Phân tích nguyên nhân
add_card(s7, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="🔬 Phân Tích Cơ Chế & Rủi Ro Thực Tế")
tb_p_an = s7.shapes.add_textbox(Inches(7.0), Inches(2.55), Inches(5.3), Inches(4.0))
tf_pan = tb_p_an.text_frame
tf_pan.word_wrap = True

add_bullet(tf_pan, "P01 (Giữ tỷ lệ & Padding)", "Giảm mạnh nhất (-5.00 pp) do chèn viền xám làm tổn thương bị co nhỏ, mất độ phân giải hữu ích.")
add_bullet(tf_pan, "P03 (Tẩy lông bằng Inpainting)", "Giảm -2.91 pp vì thuật toán tẩy lông làm nhòe luôn các mạng sắc tố vi mô của tổn thương dạng lưới.")
add_bullet(tf_pan, "P04 (Shades of Gray)", "Giảm -1.76 pp do làm biến đổi sắc thái màu tự nhiên mà mô hình cần để nhận diện mạch máu.")
add_bullet(tf_pan, "P07 (Lọc Bilateral)", "Giảm -3.75 pp do làm mịn quá mức đường ranh giới rải rác của khối u ác tính.")
add_bullet(tf_pan, "Bài học khoa học đắt giá", "Can thiệp thị giác trông có vẻ 'sạch' đối với mắt người nhưng lại phá vỡ đặc trưng toán học mà ResNet học được!")

add_footer(s7, 7)

# ==========================================
# SLIDE 8: CƯỜNG HÓA NHÓM ĐỐI XỨNG D4 (T02B)
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "Phần 4: Pipeline và phương án nghiên cứu", "Cường Hóa Đối Xứng Nhóm D4 (T02B)", "Tận dụng tính bất biến quay tự nhiên của ảnh soi da; tăng vượt bậc +5.09 điểm % Macro-F1")

# Left Side: Image 4.2
add_card(s8, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="🔄 Tám Phép Đối Xứng Trên Cùng Một Ảnh (Hình 4.2)")
img_d4 = os.path.join(ASSETS_DIR, "image5.png")
if os.path.exists(img_d4):
    s8.shapes.add_picture(img_d4, Inches(0.95), Inches(2.55), width=Inches(5.35))

# Right Side: Cơ chế D4
add_card(s8, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="✨ Cơ Chế & Hiệu Quả Của D4")
tb_d4 = s8.shapes.add_textbox(Inches(7.0), Inches(2.55), Inches(5.3), Inches(4.0))
tf_d4 = tb_d4.text_frame
tf_d4.word_wrap = True

add_bullet(tf_d4, "Bản chất nhóm D4", "Gồm 8 phép biến đổi hình học của hình vuông: 4 góc quay (0°, 90°, 180°, 270°) kết hợp lật ngang/dọc.")
add_bullet(tf_d4, "Bảo toàn 100% pixel", "Trên lưới ảnh vuông đã resize, phép quay 90° và lật chỉ hoán vị chỉ số pixel, hoàn toàn không cần nội suy làm mờ ảnh.")
add_bullet(tf_d4, "Ví dụ đời sống dễ hiểu", "Một nốt ruồi trên da dù nhìn từ hướng nào thì bản chất bệnh lý vẫn không đổi; hướng cầm máy soi da không đổi chẩn đoán y khoa!")
add_bullet(tf_d4, "Chỉ áp dụng ở Train", "Validation và Test giữ nguyên góc chụp ban đầu để đánh giá khách quan năng lực tổng quát hóa.")
add_bullet(tf_d4, "Hiệu quả thực nghiệm", "Macro-F1 tăng từ 55.21% (B00) lên 60.30% (T02B) ở Seed 42, mức tăng cực lớn +5.09 điểm %!")

add_footer(s8, 8)

# ==========================================
# SLIDE 9: CHIẾN LƯỢC HUẤN LUYỆN & KIẾN TRÚC ĐỐI CHIẾU
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "Phần 4: Pipeline và phương án nghiên cứu", "Chiến Lược Huấn Luyện & Kiến Trúc Đối Chiếu", "Thử nghiệm có kiểm soát từng yếu tố kỹ thuật theo nguyên tắc đối chứng khoa học")

w_card2 = Inches(5.65)
h_card2 = Inches(2.35)

# Card 1: Loss L01
add_card(s9, Inches(0.8), Inches(1.9), w_card2, h_card2, title="⚖️ Hàm Mất Mát Có Trọng Số (L01 - Weighted CE)")
tb_l01 = s9.shapes.add_textbox(Inches(1.0), Inches(2.45), w_card2 - Inches(0.4), Inches(1.7))
tf_l01 = tb_l01.text_frame
tf_l01.word_wrap = True
add_bullet(tf_l01, "Cơ chế", "Trọng số tỷ lệ nghịch căn bậc 2 số mẫu lớp (nhẹ hơn tỷ lệ nghịch trực tiếp).")
add_bullet(tf_l01, "Kết quả", "Macro-F1 đạt 60.33% (+0.02 pp), Balanced Acc tăng (59.95%) nhưng Accuracy giảm xuống 74.95% do sinh thêm dương sai ở lớp hiếm.")

# Card 2: Sampler S01
add_card(s9, Inches(6.8), Inches(1.9), w_card2, h_card2, title="🔄 Lấy Mẫu Cân Bằng (S01 - Balanced Sampler)")
tb_s01 = s9.shapes.add_textbox(Inches(7.0), Inches(2.45), w_card2 - Inches(0.4), Inches(1.7))
tf_s01 = tb_s01.text_frame
tf_s01.word_wrap = True
add_bullet(tf_s01, "Cơ chế", "Lấy mẫu có hoàn lại, tăng tần suất xuất hiện của các lớp hiếm trong mỗi batch.")
add_bullet(tf_s01, "Kết quả", "Macro-F1 giảm xuống 58.48% (-1.82 pp). Lặp lại quá nhiều ảnh của lớp ít mẫu gây hiện tượng quá khớp (overfitting) nặng.")

# Card 3: Learning Rate F01
add_card(s9, Inches(0.8), Inches(4.45), w_card2, h_card2, title="🎯 Tối Ưu Learning Rate Phân Nhóm (F01)")
tb_f01 = s9.shapes.add_textbox(Inches(1.0), Inches(5.0), w_card2 - Inches(0.4), Inches(1.7))
tf_f01 = tb_f01.text_frame
tf_f01.word_wrap = True
add_bullet(tf_f01, "Cơ chế", "Học chậm ở Backbone (1e-5) để bảo vệ đặc trưng ImageNet, học nhanh ở FC Head (1e-4).")
add_bullet(tf_f01, "Kết quả", "Macro-F1 đạt 58.96% (-1.34 pp), tốc độ hội tụ chậm hơn tốc độ cần thiết trong ngân sách 16 epoch.")

# Card 4: Architecture M01
add_card(s9, Inches(6.8), Inches(4.45), w_card2, h_card2, title="🏗️ Kiến Trúc Đối Chiếu: EfficientNet-B0 (M01)")
tb_m01 = s9.shapes.add_textbox(Inches(7.0), Inches(5.0), w_card2 - Inches(0.4), Inches(1.7))
tf_m01 = tb_m01.text_frame
tf_m01.word_wrap = True
add_bullet(tf_m01, "Cơ chế", "Thay ResNet50 bằng EfficientNet-B0 trên cùng nền D4 và Cross-Entropy.")
add_bullet(tf_m01, "Kết quả", "Macro-F1 đạt 58.44% (-1.86 pp) so với ResNet50 (60.30%). ResNet50 vẫn là lựa chọn vững chắc nhất trong bài toán này.")

add_footer(s9, 9)

# ==========================================
# SLIDE 10: QUY TRÌNH HUẤN LUYỆN & DỪNG SỚM
# ==========================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "Phần 5: Thiết kế thực nghiệm và tái lập", "Quy Trình Huấn Luyện & Tiêu Chí Dừng Sớm", "Cấu hình protocol chặt chẽ, tối ưu hóa theo Macro-F1 thay vì Validation Loss")

# Left Card: Protocol khóa
add_card(s10, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="🔒 Protocol Huấn Luyện T02B Đã Khóa")
tb_prt = s10.shapes.add_textbox(Inches(1.0), Inches(2.55), Inches(5.25), Inches(4.0))
tf_prt = tb_prt.text_frame
tf_prt.word_wrap = True

add_bullet(tf_prt, "Backbone", "ResNet50 pretrained ImageNet V1, thay lớp phân loại cuối FC 2048 -> 8 logits.")
add_bullet(tf_prt, "Hàm mất mát", "Cross-Entropy tiêu chuẩn không trọng số.")
add_bullet(tf_prt, "Tối ưu hóa (Optimizer)", "AdamW với learning rate = 1e-4, weight decay = 1e-4.")
add_bullet(tf_prt, "Bộ điều chỉnh LR", "CosineAnnealingLR (T_max = 16 epoch, cập nhật cuối mỗi epoch).")
add_bullet(tf_prt, "Môi trường phần cứng", "NVIDIA Tesla T4 GPU (FP32), Batch size = 32, Workers = 2.")

# Right Card: Checkpoint & Early stopping
add_card(s10, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="⏱️ Tiêu Chí Chọn Checkpoint & Dừng Sớm")
tb_ck = s10.shapes.add_textbox(Inches(7.0), Inches(2.55), Inches(5.3), Inches(4.0))
tf_ck = tb_ck.text_frame
tf_ck.word_wrap = True

add_bullet(tf_ck, "Quy tắc dừng sớm", "Ngân sách tối đa 16 epoch, dừng nếu 4 epoch liên tiếp không cải thiện Macro-F1 (patience = 4).")
add_bullet(tf_ck, "Thời điểm chốt Checkpoint", "Checkpoint tốt nhất được lưu tại Epoch 14/16 (Macro-F1 đạt 60.3002%).")
add_bullet(tf_ck, "Vì sao KHÔNG chọn theo Loss?", "Validation Loss đạt đáy tại Epoch 4 (Loss = 0.73). Tuy nhiên, tại epoch 4 mô hình chỉ giỏi đoán lớp đông NV; đến epoch 14 Macro-F1 mới đạt đỉnh!")
add_bullet(tf_ck, "Bài học phương pháp", "Trong bài toán mất cân bằng, chỉ số Macro-F1 phản ánh đúng độ công bằng giữa các lớp hơn là hàm Loss tổng hợp.")

add_footer(s10, 10)

# ==========================================
# SLIDE 11: KIỂM ĐỊNH TÍNH BỀN VỮNG: ĐA SEED & BOOTSTRAP
# ==========================================
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11)
add_header(s11, "Phần 5: Thiết kế thực nghiệm và tái lập", "Kiểm Định Tính Bền Vững Đa Seed & Bootstrap", "Kiểm chứng lặp lại qua Seed 42, 43, 44 để bảo đảm kết luận khoa học không do ngẫu nhiên")

# Top Side: Bảng đa seed
add_card(s11, Inches(0.8), Inches(1.9), Inches(11.7), Inches(2.6), title="📊 Bảng So Sánh Ghép Cặp B00 vs T02B Qua 3 Seed (Bảng 6.5)")

# Table
rows, cols = 4, 5
table_shape = s11.shapes.add_table(rows, cols, Inches(1.0), Inches(2.5), Inches(11.3), Inches(1.8))
table = table_shape.table
table.columns[0].width = Inches(2.2)
table.columns[1].width = Inches(2.2)
table.columns[2].width = Inches(2.2)
table.columns[3].width = Inches(2.2)
table.columns[4].width = Inches(2.5)

headers = ["Lượt Chạy", "B00 (Không Aug)", "T02B (Có D4)", "Chênh Lệch (Δ pp)", "Khoảng Tin Cậy CI 95%"]
for i, h in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_PRIMARY
    p = cell.text_frame.paragraphs[0]
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

data_seeds = [
    ["Seed 42 (Thăm dò)", "55.2115%", "60.3002%", "+5.0887 pp", "[+0.1739; +9.3884]"],
    ["Seed 43 (Xác nhận)", "57.3231%", "57.7945%", "+0.4714 pp", "[-3.7990; +5.1088]"],
    ["Seed 44 (Xác nhận)", "56.0809%", "59.9743%", "+3.8934 pp", "[-0.8558; +8.6463]"]
]
for r_idx, row in enumerate(data_seeds):
    for c_idx, val in enumerate(row):
        cell = table.cell(r_idx + 1, c_idx)
        cell.text = val
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if r_idx % 2 == 0 else RGBColor(248, 245, 240)
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_PRIMARY if c_idx == 3 else COLOR_TEXT_DARK
        p.font.bold = True if c_idx in [0, 3] else False
        p.alignment = PP_ALIGN.CENTER

# Bottom Card: Nhận định khoa học
add_card(s11, Inches(0.8), Inches(4.65), Inches(11.7), Inches(2.2), title="🔬 Nhận Định Khoa Học Trung Thực & Khiêm Tốn")
tb_sd_note = s11.shapes.add_textbox(Inches(1.0), Inches(5.15), Inches(11.3), Inches(1.5))
tf_sn = tb_sd_note.text_frame
tf_sn.word_wrap = True

add_bullet(tf_sn, "D4 luôn có lợi thế", "Ở cả 3 seed quan sát, T02B đều đạt Macro-F1 cao hơn B00; trung bình 2 seed xác nhận tăng +2.1824 pp.")
add_bullet(tf_sn, "Biên độ dao động theo seed", "Mức tăng ở seed 43 khá nhỏ (+0.47 pp), trong khi seed 44 tăng rất mạnh (+3.89 pp), cho thấy sự khởi tạo ngẫu nhiên có tác động nhất định.")
add_bullet(tf_sn, "Khoảng tin cậy chứa 0", "CI95 của seed 43 và 44 đều chứa 0 -> Báo cáo khoa học ghi nhận lợi ích thực tế nhưng không cường điệu hóa thành kết luận bất biến!")

add_footer(s11, 11)

# ==========================================
# SLIDE 12: ĐÁNH GIÁ TRÊN TẬP TEST NỘI BỘ
# ==========================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12)
add_header(s12, "Phần 6: Kết quả, thảo luận và phân tích lỗi", "Đánh Giá Trên Tập Kiểm Thử Nội Bộ (5.065 Ảnh)", "Mô hình tổng quát hóa ổn định, không có hiện tượng rò rỉ dữ liệu hay học vẹt")

# Left Side: Đường cong học Hình 6.3
add_card(s12, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="📈 Đường Cong Học T02B Qua Các Epoch (Hình 6.3)")
img_hist = os.path.join(ASSETS_DIR, "image8.png")
if os.path.exists(img_hist):
    s12.shapes.add_picture(img_hist, Inches(0.95), Inches(2.6), width=Inches(5.35))

tb_hn = s12.shapes.add_textbox(Inches(0.95), Inches(5.1), Inches(5.35), Inches(1.5))
tf_hn = tb_hn.text_frame
tf_hn.word_wrap = True
p_hn = tf_hn.paragraphs[0]
p_hn.text = "• Train Loss giảm đều từ 0.87 về 0.05 (mô hình khớp tốt dữ liệu train)."
p_hn.font.size = Pt(11)
p_hn.font.color.rgb = COLOR_TEXT_DARK
p_hn2 = tf_hn.add_paragraph()
p_hn2.text = "• Validation Macro-F1 đạt đỉnh 60.30% tại Epoch 14 (vạch nét đứt) và được chọn làm checkpoint chính thức."
p_hn2.font.size = Pt(11)
p_hn2.font.color.rgb = COLOR_TEXT_MUTED

# Right Side: Bảng Test vs Validation
add_card(s12, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="🎯 Kết Quả Đánh Giá Trên Tập Test Nội Bộ")

# Table on Right
rows_t, cols_t = 6, 3
tb_t_shape = s12.shapes.add_table(rows_t, cols_t, Inches(7.0), Inches(2.6), Inches(5.3), Inches(2.4))
tb_t = tb_t_shape.table
tb_t.columns[0].width = Inches(2.3)
tb_t.columns[1].width = Inches(1.5)
tb_t.columns[2].width = Inches(1.5)

test_metrics = [
    ["Chỉ Số Đánh Giá", "Validation %", "Test Nội Bộ %"],
    ["Accuracy (Chính xác)", "77.00%", "76.43%"],
    ["Macro-F1 (Tiêu chí chính)", "60.30%", "60.54%"],
    ["Balanced Accuracy", "58.61%", "58.85%"],
    ["Macro-Precision", "64.33%", "63.18%"],
    ["Weighted-F1", "76.49%", "75.78%"]
]
for r_i, row in enumerate(test_metrics):
    for c_i, val in enumerate(row):
        cell = tb_t.cell(r_i, c_i)
        cell.text = val
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY if r_i == 0 else (RGBColor(255, 255, 255) if r_i % 2 == 1 else RGBColor(248, 245, 240))
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(10.5)
        p.font.color.rgb = RGBColor(255, 255, 255) if r_i == 0 else COLOR_TEXT_DARK
        p.font.bold = True if (r_i == 0 or r_i == 2 or c_i == 0) else False
        p.alignment = PP_ALIGN.CENTER if c_i > 0 else PP_ALIGN.LEFT

tb_t_callout = s12.shapes.add_textbox(Inches(7.0), Inches(5.2), Inches(5.3), Inches(1.4))
tf_tc = tb_t_callout.text_frame
tf_tc.word_wrap = True
p_tc1 = tf_tc.paragraphs[0]
p_tc1.text = "💡 Minh chứng tổng quát hóa vững chắc:"
p_tc1.font.bold = True
p_tc1.font.size = Pt(11.5)
p_tc1.font.color.rgb = COLOR_PRIMARY
p_tc2 = tf_tc.add_paragraph()
p_tc2.text = "• Có 3.871/5.065 ảnh test được dự đoán đúng.\n• Chênh lệch giữa Validation (60.30%) và Test (60.54%) dưới 0.25 pp, khẳng định không rò rỉ dữ liệu và không học vẹt."
p_tc2.font.size = Pt(10.5)
p_tc2.font.color.rgb = COLOR_TEXT_DARK

add_footer(s12, 12)

# ==========================================
# SLIDE 13: MA TRẬN NHẦM LẪN CHI TIẾT
# ==========================================
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13)
add_header(s13, "Phần 6: Kết quả, thảo luận và phân tích lỗi", "Ma Trận Nhầm Lẫn & Đánh Giá Từng Lớp Bệnh Lý", "Accuracy 76.4% che giấu khó khăn lớn ở các nhóm tổn thương ác tính và hiếm gặp")

# Left Side: Confusion Matrix Image 6.4
add_card(s13, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="🗂️ Ma Trận Nhầm Lẫn Tập Test (Hình 6.4)")
img_cm = os.path.join(ASSETS_DIR, "image9.png")
if os.path.exists(img_cm):
    s13.shapes.add_picture(img_cm, Inches(0.95), Inches(2.6), width=Inches(5.35))

# Right Side: Phân tích từng lớp
add_card(s13, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="🔍 Phân Tích Chẩn Đoán Từng Nhóm Bệnh")
tb_cm_an = s13.shapes.add_textbox(Inches(7.0), Inches(2.55), Inches(5.3), Inches(4.0))
tf_cma = tb_cm_an.text_frame
tf_cma.word_wrap = True

add_bullet(tf_cma, "Lớp đa số (NV)", "Recall đạt 90.56%, F1 đạt 87.38% (2.361/2.607 ảnh đúng). Mô hình nhận diện nốt ruồi rất chuẩn.")
add_bullet(tf_cma, "U hắc tố ác tính (MEL)", "Recall đạt 58.24% (562/965 ảnh). Có 281 ca MEL bị nhầm thành nốt ruồi lành tính (NV) -> Rủi ro lâm sàng lớn nhất!")
add_bullet(tf_cma, "Ung thư đáy & vảy (BCC, SCC)", "BCC nhận diện tốt (Recall 80.03%, F1 75.16%). Ngược lại, SCC chỉ đạt Recall 37.93% do thiếu mẫu.")
add_bullet(tf_cma, "Dày sừng quang hóa (AK)", "Recall chỉ đạt 31.40% (54/172 ảnh); 40 ca bị nhầm sang ung thư đáy (BCC) và 31 ca nhầm sang dày sừng (BKL).")
add_bullet(tf_cma, "Kết luận lâm sàng", "AI cần có cơ chế cảnh báo ranh giới ở các ca nghi ngờ ác tính để bác sĩ can thiệp trực tiếp.")

add_footer(s13, 13)

# ==========================================
# SLIDE 14: PHÂN TÍCH LỖI THỰC TẾ (E02)
# ==========================================
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14)
add_header(s14, "Phần 6: Kết quả, thảo luận và phân tích lỗi", "Phân Tích Thực Tế 52 Ca Chẩn Đoán Sai (E02)", "Nhận diện các yếu tố thị giác gây nhiễu để định hướng cải tiến hệ thống trong tương lai")

# Left Side: Error images Hình 6.5
add_card(s14, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="🖼️ Ảnh Nhầm Lẫn Điển Hình (Hình 6.5)")
img_err = os.path.join(ASSETS_DIR, "image10.png")
if os.path.exists(img_err):
    s14.shapes.add_picture(img_err, Inches(0.95), Inches(2.55), width=Inches(5.35))

# Right Side: Thống kê lỗi E02
add_card(s14, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="📊 Thống Kê 4 Hướng Nhầm Lẫn Chính")
tb_err_st = s14.shapes.add_textbox(Inches(7.0), Inches(2.55), Inches(5.3), Inches(4.0))
tf_est = tb_err_st.text_frame
tf_est.word_wrap = True

add_bullet(tf_est, "4 Hướng nhầm phổ biến nhất", "• MEL -> NV: 108 ảnh (nhầm ác tính sang lành tính)\n• NV -> MEL: 61 ảnh (cảnh báo quá mức)\n• BKL -> NV: 46 ảnh\n• MEL -> BKL: 32 ảnh")
add_bullet(tf_est, "Lông che phủ (25/52 ảnh)", "Mật độ lông dày đặc che lấp các đốm sắc tố ở tâm tổn thương.")
add_bullet(tf_est, "Viền đen & ống kính (21/52 ảnh)", "Khung viền tròn của kính soi da tạo độ tương phản giả đánh lừa mạng nơ-ron.")
add_bullet(tf_est, "Vết mực / Thước đo (15/52 ảnh)", "Thước đo milimet do bác sĩ đặt cạnh tổn thương vô tình trở thành đặc trưng giả.")
add_bullet(tf_est, "Bài học phương pháp", "Dù thấy các yếu tố này, khảo sát P01-P10 đã chứng minh không thể vội vàng cắt gọt hay xóa tự động nếu chưa có mô hình phát hiện chuyên biệt.")

add_footer(s14, 14)

# ==========================================
# SLIDE 15: DEMO SUY LUẬN & HIỆN TƯỢNG QUÁ TỰ TIN
# ==========================================
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15)
add_header(s15, "Phần 6: Kết quả, thảo luận và phân tích lỗi", "Demo Suy Luận Thực Tế & Cảnh Báo Lâm Sàng", "Softmax cao không đồng nghĩa với chẩn đoán đúng! Cảnh báo cực kỳ quan trọng cho hệ thống y tế")

# Left Side: Demo Đúng Hình 6.6
add_card(s15, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="✅ Demo Đúng: ISIC_0000000 (Hình 6.6)")
img_d_right = os.path.join(ASSETS_DIR, "image11.png")
if os.path.exists(img_d_right):
    s15.shapes.add_picture(img_d_right, Inches(0.95), Inches(2.55), width=Inches(5.35))

tb_dr = s15.shapes.add_textbox(Inches(0.95), Inches(5.3), Inches(5.35), Inches(1.3))
tf_dr = tb_dr.text_frame
tf_dr.word_wrap = True
p_dr = tf_dr.paragraphs[0]
p_dr.text = "• Nhãn thật: NV  |  Dự đoán: NV  |  Softmax: 99.997%"
p_dr.font.bold = True
p_dr.font.size = Pt(11.5)
p_dr.font.color.rgb = COLOR_TEAL
p_dr2 = tf_dr.add_paragraph()
p_dr2.text = "Tổn thương nốt ruồi điển hình, ranh giới rõ ràng, mô hình nhận diện chính xác tuyệt đối."
p_dr2.font.size = Pt(10.5)
p_dr2.font.color.rgb = COLOR_TEXT_MUTED

# Right Side: Demo Sai Hình 6.7
add_card(s15, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="⚠️ Demo Sai & Cảnh Báo: ISIC_0000195 (Hình 6.7)")
img_d_wrong = os.path.join(ASSETS_DIR, "image12.png")
if os.path.exists(img_d_wrong):
    s15.shapes.add_picture(img_d_wrong, Inches(7.0), Inches(2.55), width=Inches(5.3))

tb_dw = s15.shapes.add_textbox(Inches(7.0), Inches(5.3), Inches(5.3), Inches(1.3))
tf_dw = tb_dw.text_frame
tf_dw.word_wrap = True
p_dw = tf_dw.paragraphs[0]
p_dw.text = "• Nhãn thật: NV  |  Dự đoán: BKL  |  Softmax: 95.061%!"
p_dw.font.bold = True
p_dw.font.size = Pt(11.5)
p_dw.font.color.rgb = COLOR_PRIMARY
p_dw2 = tf_dw.add_paragraph()
p_dw2.text = "Cực kỳ nguy hiểm: Dù dự đoán sai, Softmax vẫn tự tin trên 95%! Minh chứng rằng Softmax chưa được hiệu chuẩn (calibrated) thành xác suất y khoa."
p_dw2.font.size = Pt(10.5)
p_dw2.font.color.rgb = COLOR_TEXT_MUTED

add_footer(s15, 15)

# ==========================================
# SLIDE 16: KẾT LUẬN & ĐÓNG GÓP CỐT LÕI
# ==========================================
s16 = prs.slides.add_slide(blank_layout)
set_slide_background(s16)
add_header(s16, "Phần 7: Kết luận và hướng phát triển", "Kết Luận & Đóng Góp Cốt Lõi Của Đề Tài", "Minh bạch, khoa học, có đối chứng chặt chẽ và truy vết số liệu 100%")

w_c4 = Inches(5.65)
h_c4 = Inches(2.35)

# 4 Cards
add_card(s16, Inches(0.8), Inches(1.9), w_c4, h_c4, title="1️⃣ Kiểm Toán & Làm Sạch Dữ Liệu")
tb_k1 = s16.shapes.add_textbox(Inches(1.0), Inches(2.45), w_c4 - Inches(0.4), Inches(1.7))
tf_k1 = tb_k1.text_frame
tf_k1.word_wrap = True
add_bullet(tf_k1, "Thực hiện", "Phát hiện 48 ảnh trùng, loại bỏ 4 ảnh xung đột nhãn; chia tập Group Split 70/10/20.")
add_bullet(tf_k1, "Giá trị", "Khóa manifest 25.327 ảnh, bảo đảm không rò rỉ dữ liệu (crossing = 0), tạo nền tảng đánh giá trung thực.")

add_card(s16, Inches(6.8), Inches(1.9), w_c4, h_c4, title="2️⃣ Hiệu Quả Cốt Lõi Của Nhóm Đối Xứng D4")
tb_k2 = s16.shapes.add_textbox(Inches(7.0), Inches(2.45), w_c4 - Inches(0.4), Inches(1.7))
tf_k2 = tb_k2.text_frame
tf_k2.word_wrap = True
add_bullet(tf_k2, "Thực hiện", "8 phép quay và lật ngẫu nhiên trên tập train mà không nội suy làm mờ ảnh.")
add_bullet(tf_k2, "Giá trị", "Tăng +5.09 pp Macro-F1 ở seed 42 và +2.18 pp trung bình qua các seed xác nhận, chứng minh tính bất biến quay.")

add_card(s16, Inches(0.8), Inches(4.45), w_c4, h_c4, title="3️⃣ Bằng Chứng Phản Biện Về Tiền Xử Lý")
tb_k3 = s16.shapes.add_textbox(Inches(1.0), Inches(5.0), w_c4 - Inches(0.4), Inches(1.7))
tf_k3 = tb_k3.text_frame
tf_k3.word_wrap = True
add_bullet(tf_k3, "Thực hiện", "Thử nghiệm có kiểm soát 10 phương án tiền xử lý (P01–P10) độc lập trên ResNet50.")
add_bullet(tf_k3, "Giá trị", "Chứng minh bằng thực nghiệm: không nên vội vã can thiệp pixel (tẩy lông, lọc sáng, padding) khi chưa có đối chứng.")

add_card(s16, Inches(6.8), Inches(4.45), w_c4, h_c4, title="4️⃣ Sản Phẩm Đóng Gói Tái Lập 100%")
tb_k4 = s16.shapes.add_textbox(Inches(7.0), Inches(5.0), w_c4 - Inches(0.4), Inches(1.7))
tf_k4 = tb_k4.text_frame
tf_k4.word_wrap = True
add_bullet(tf_k4, "Thực hiện", "Checkpoint T02B đạt Test Acc 76.43%, Macro-F1 60.54% trên tập test nội bộ 5.065 ảnh.")
add_bullet(tf_k4, "Giá trị", "Toàn bộ mã nguồn, cấu hình, manifest và kết quả được lưu trữ mở và kết nối qua bảng experiment_index.csv.")

add_footer(s16, 16)

# ==========================================
# SLIDE 17: HẠN CHẾ & HƯỚNG PHÁT TRIỂN
# ==========================================
s17 = prs.slides.add_slide(blank_layout)
set_slide_background(s17)
add_header(s17, "Phần 7: Kết luận và hướng phát triển", "Hạn Chế Nghiên Cứu & Hướng Phát Triển Tương Lai", "Nhìn nhận thẳng thắn ranh giới khoa học để định hướng nghiên cứu chuyên sâu tiếp theo")

# Left Card: Hạn chế
add_card(s17, Inches(0.8), Inches(1.9), Inches(5.65), Inches(4.9), title="⚠️ Hạn Chế Của Nghiên Cứu Hiện Tại")
tb_lim = s17.shapes.add_textbox(Inches(1.0), Inches(2.55), Inches(5.25), Inches(4.0))
tf_lim = tb_lim.text_frame
tf_lim.word_wrap = True

add_bullet(tf_lim, "Dữ liệu thiếu patient_id", "2.084 ảnh thiếu lesion_id và chưa có patient_id để cô lập hoàn toàn mức người bệnh.")
add_bullet(tf_lim, "Ngân sách môn học", "Giới hạn ở 16 epoch và chủ yếu khảo sát trên 1-2 seed do hạn chế về thời gian GPU.")
add_bullet(tf_lim, "Chưa kiểm thử ngoài miền", "Tập test vẫn cùng nguồn phân phối ISIC 2019; chưa đánh giá trên ảnh chụp từ điện thoại hay bệnh viện Việt Nam.")
add_bullet(tf_lim, "Chưa có cơ chế từ chối", "Mô hình luôn ép đầu ra vào 1 trong 8 lớp, chưa nhận diện được ảnh không phải da liễu.")

# Right Card: Hướng phát triển
add_card(s17, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.9), title="🚀 Hướng Nghiên Cứu Sau Môn Học")
tb_fut = s17.shapes.add_textbox(Inches(7.0), Inches(2.55), Inches(5.3), Inches(4.0))
tf_fut = tb_fut.text_frame
tf_fut.word_wrap = True

add_bullet(tf_fut, "Đa phương thức (Multimodal)", "Kết hợp ảnh soi da với thông tin metadata bệnh nhân (tuổi, giới tính, vị trí giải phẫu) để tăng độ nhạy lâm sàng.")
add_bullet(tf_fut, "Hiệu chuẩn xác suất (Calibration)", "Áp dụng kỹ thuật Temperature Scaling để đưa điểm Softmax về đúng xác suất chẩn đoán tin cậy.")
add_bullet(tf_fut, "Kiến trúc Vision Transformer", "Khảo sát Swin Transformer kết hợp tiền huấn luyện tự giám sát (DINO / MAE) để khai phá tốt hơn cấu trúc tổn thương.")
add_bullet(tf_fut, "Mô hình từ chối chẩn đoán", "Thiết lập ngưỡng tin cậy để tự động từ chối dự đoán khi gặp ảnh ngoài miền dữ liệu (Out-of-Distribution).")

add_footer(s17, 17)

# ==========================================
# SLIDE 18: LỜI CẢM ƠN & PHIÊN VẤN ĐÁP (Q&A)
# ==========================================
s18 = prs.slides.add_slide(blank_layout)
set_slide_background(s18)

# Big Banner
card_qa = add_card(s18, Inches(1.5), Inches(1.5), Inches(10.333), Inches(4.5), bg_color=RGBColor(255, 255, 255), border_color=COLOR_PRIMARY)

tb_qa_t = s18.shapes.add_textbox(Inches(2.0), Inches(1.9), Inches(9.333), Inches(1.2))
tf_qat = tb_qa_t.text_frame
tf_qat.word_wrap = True
p_qt = tf_qat.paragraphs[0]
p_qt.text = "XIN CHÂN THÀNH CẢM ƠN!"
p_qt.font.size = Pt(32)
p_qt.font.bold = True
p_qt.font.name = "Segoe UI"
p_qt.font.color.rgb = COLOR_PRIMARY
p_qt.alignment = PP_ALIGN.CENTER

p_qt2 = tf_qat.add_paragraph()
p_qt2.text = "Em xin chân thành cảm ơn GVHD ThS. Vũ Thị Hạnh và Quý Thầy Cô trong Hội đồng đã lắng nghe bài thuyết trình!"
p_qt2.font.size = Pt(14)
p_qt2.font.italic = True
p_qt2.font.color.rgb = COLOR_TEXT_MUTED
p_qt2.alignment = PP_ALIGN.CENTER

tb_qa_info = s18.shapes.add_textbox(Inches(2.0), Inches(3.4), Inches(9.333), Inches(2.2))
tf_qai = tb_qa_info.text_frame
tf_qai.word_wrap = True

p_qi1 = tf_qai.paragraphs[0]
p_qi1.text = "🎓 Sinh viên: Nguyễn Tuấn Đức  —  MSSV: 2351067091  (Nhóm 8)"
p_qi1.font.size = Pt(14)
p_qi1.font.bold = True
p_qi1.font.color.rgb = COLOR_TEXT_DARK
p_qi1.alignment = PP_ALIGN.CENTER

p_qi2 = tf_qai.add_paragraph()
p_qi2.text = "🔗 GitHub Repository chính thức: github.com/NguyenTuanDuc1501/ISIC2019-Skin-Lesion-Classification"
p_qi2.font.size = Pt(13)
p_qi2.font.bold = True
p_qi2.font.color.rgb = COLOR_TEAL
p_qi2.alignment = PP_ALIGN.CENTER

p_qi3 = tf_qai.add_paragraph()
p_qi3.text = "❓ SẴN SÀNG BƯỚC VÀO PHIÊN THẢO LUẬN & TRẢ LỜI CÂU HỎI VẤN ĐÁP (Q&A)"
p_qi3.font.size = Pt(14)
p_qi3.font.bold = True
p_qi3.font.color.rgb = COLOR_PRIMARY
p_qi3.alignment = PP_ALIGN.CENTER

add_footer(s18, 18)

# Save presentation
prs.save(PPTX_OUTPUT)
print(f"Presentation successfully generated and saved to: {PPTX_OUTPUT}")
