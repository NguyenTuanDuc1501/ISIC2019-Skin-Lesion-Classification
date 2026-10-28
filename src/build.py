from pathlib import Path
import json,hashlib,ast,shutil
import pandas as pd
import nbformat
R=Path(__file__).resolve().parent
if R.name == 'src': R=R.parent
DATA=R/'data'
L=['MEL','NV','BCC','AK','BKL','DF','VASC','SCC']
# Preserve original catalog; create an explicitly updated status table.
options=pd.read_csv(DATA/'PREPROCESSING_OPTIONS.csv')
fixed=options[options.kind.eq('fixed')].copy()
fixed['current_R50_status']='Chưa có kết quả R50 trong hồ sơ tổng hợp'
fixed.loc[fixed.id.eq('P04'),'current_R50_status']='Đã train SoG trên T02B: F1 58,5396%; không cải thiện seed42'
fixed['evidence_level']='Danh mục lịch sử; trạng thái/điểm R18 chưa tính lại từ raw predictions tại lần đóng gói này'
fixed.loc[fixed.id.eq('P02'),'evidence_level']='Danh mục này ghi quét phạm vi chưa train; mã P02 crop từng xuất hiện ở chuỗi R18 khác. Không mặc định cùng phiên bản.'
fixed.to_csv(DATA/'preprocessing_status_current.csv',index=False)
(DATA/'ISIC2019_REPORT_PACKAGE.json').write_text(json.dumps({'task':'ISIC2019_REPORT_NOTEBOOK','version':'1.0','created':'2026-10-18','selected_model':'T02B_D4_R50 seed42','test_already_evaluated':True},indent=2))
expected={str(p.relative_to(DATA)):hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.rglob('*') if p.is_file() and p.name != 'REPORT_INPUT_HASHES.json'}
(R/'INPUT_HASHES.json').write_text(json.dumps(expected,indent=2))
(DATA/'REPORT_INPUT_HASHES.json').write_text(json.dumps(expected,indent=2))
hashes_sha = hashlib.sha256((DATA/'REPORT_INPUT_HASHES.json').read_bytes()).hexdigest()
nb=nbformat.v4.new_notebook();cells=[]
def md(t):cells.append(nbformat.v4.new_markdown_cell(t))
def code(t):cells.append(nbformat.v4.new_code_cell(t))
md('''# Phân loại tổn thương da ISIC 2019
## Notebook trình bày toàn bộ nghiên cứu
**Nguyễn Tuấn Đức — báo cáo cô Hạnh — bản 1.0, 18/10/2026**

Câu hỏi nghiên cứu: giữ dữ liệu và quy trình đánh giá cố định, một thay đổi về xử lý ảnh hoặc huấn luyện có giúp phân loại cân bằng giữa tám lớp không?

**Kết quả chốt:** T02B = ResNet50 + D4 trên train + CE không trọng số. Test nội bộ: macro-F1 60,54%; balanced accuracy 58,85%; accuracy 76,43%.

Notebook này là **cửa vào để trình bày**, nối mã giải thích với hồ sơ thực nghiệm. Các notebook huấn luyện gốc vẫn là bằng chứng nguồn; không gộp và chạy lại mọi thí nghiệm ở đây.

- Phần CPU: kiểm nguồn, dữ liệu, bảng thực nghiệm, history và tính lại metrics từ predictions đã lưu.
- Gallery: mở ảnh ISIC thật khi gắn dataset, kiểm hash; chỉ dùng ảnh train/validation.
- Suy luận trực tiếp một ảnh validation: tùy chọn tắt mặc định, cần checkpoint chính xác.
- Không huấn luyện, không suy luận mới trên test, không đổi quyết định theo test đã xem.

**Trình tự:** import → cấu hình → split đã khóa → EDA → ảnh minh họa → preprocessing/D4 → dataset/loader → transfer learning → đánh giá → optimizer/training đã dùng → kết quả → thực nghiệm → D4 nhiều seed → test → giới hạn.

Tên lớp là nhãn dataset; ảnh minh họa không tự đại diện đầy đủ đặc điểm y học của cả lớp.''')
md('''### 1 Import thư viện
Phần mặc định chỉ cần thư viện xử lý bảng và vẽ hình. PyTorch chỉ nạp khi bật suy luận trực tiếp. Mỗi cell có một vai trò; nhấn Run All không khởi động huấn luyện.''')
code('''from pathlib import Path
from datetime import datetime
import json, hashlib, zipfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from IPython.display import display, Markdown
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, f1_score,
                             precision_recall_fscore_support, confusion_matrix)

LABELS = ['MEL', 'NV', 'BCC', 'AK', 'BKL', 'DF', 'VASC', 'SCC']
pd.set_option('display.max_colwidth', 95)
plt.rcParams.update({'font.size': 10, 'figure.dpi': 90})
''')
md('''### 2 Cấu hình đường dẫn và kiểm nguồn
Add Input: dataset của gói báo cáo mới (thư mục `data`) và dataset ảnh ISIC nếu muốn gallery. Checkpoint chỉ cần cho cell suy luận trực tiếp cuối.

`REPORT_DATA=None` tự tìm marker của gói mới; không lẫn với `Data_demo` cũ. `IMAGE_ROOT=None` tự tìm ảnh đã chọn dưới `/kaggle/input`. Nếu có nhiều bản bộ ảnh, đặt rõ đường dẫn một bản. Thiếu hoàn toàn ảnh thì gallery ghi NOT_RUN; tìm được một phần hoặc sai hash thì dừng để sửa Input.''')
code('''REPORT_DATA = None            # Path('/kaggle/input/.../data') nếu cần đặt rõ
IMAGE_ROOT = None             # Thư mục một bộ ảnh ISIC gốc
SHOW_GALLERIES = True          # Có ảnh thì mở; không có sẽ báo NOT_RUN
RUN_LIVE_VALIDATION = False   # Không tự bật suy luận mới
CHECKPOINT_PATH = None        # Chỉ dùng khi RUN_LIVE_VALIDATION=True
RUN_TRAIN = False              # Notebook báo cáo không có lời gọi huấn luyện
assert RUN_TRAIN is False, 'Dùng notebook huấn luyện gốc cho nghiên cứu mới.'

CFG = dict(seed=42, image_size=224, batch_size=32, workers=2,
           epochs=16, patience=4, min_delta=1e-5,
           lr=1e-4, weight_decay=1e-4, scheduler='CosineAnnealingLR T_max=16',
           model='ResNet50 ImageNet V1', loss='CE không trọng số',
           augmentation='D4 chỉ train', fine_tune='Toàn mạng, gồm BatchNorm')

# Kết quả demo ghi thư mục riêng, không ghi vào nguồn đã khóa.
base_out = Path('/kaggle/working') if Path('/kaggle/working').exists() else Path.cwd()
OUT = base_out / ('ISIC2019_PRESENTATION_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
OUT.mkdir(parents=True, exist_ok=False)
STATUS = {'training': 'NOT_RUN', 'new_test_inference': 'NOT_RUN',
          'gallery': 'NOT_RUN', 'live_validation': 'NOT_RUN'}

def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

if REPORT_DATA is None:
    roots = [Path.cwd() / 'data']
    if Path('/kaggle/input').exists():
        roots += [p.parent for p in Path('/kaggle/input').rglob('ISIC2019_REPORT_PACKAGE.json')]
    roots = sorted(set(p.resolve() for p in roots if (p/'ISIC2019_REPORT_PACKAGE.json').is_file()))
    assert len(roots) == 1, f'Đặt REPORT_DATA tới đúng data của gói mới: {roots}'
    REPORT_DATA = roots[0]
REPORT_DATA = Path(REPORT_DATA)
assert sha_file(REPORT_DATA/'REPORT_INPUT_HASHES.json') == '''+repr(hashes_sha)+''', 'Sai bảng hash nguồn'
EXPECTED = json.loads((REPORT_DATA/'REPORT_INPUT_HASHES.json').read_text())
for name, wanted_hash in EXPECTED.items():
    assert sha_file(REPORT_DATA/name) == wanted_hash, f'Sai/thiếu nguồn: {name}'

def read_csv(name):
    return pd.read_csv(REPORT_DATA/name)

def read_json(name):
    return json.loads((REPORT_DATA/name).read_text(encoding='utf-8'))

def show_figure(filename):
    plt.tight_layout()
    plt.savefig(OUT/filename, dpi=120, bbox_inches='tight')
    plt.show()
    plt.close()

lock = read_json('reference/candidate_protocol_lock.json')
complete = read_json('reference/complete.json')
assert lock['method'] == complete['method'] == 'T02B_D4_R50'
for key, value in [('seed',42),('size',224),('batch',32),('epochs',16),('patience',4)]:
    assert lock['baseline_config'][key] == value
assert complete['checkpoint_sha'] == read_json('test_report/final_test/config.json')['checkpoint_sha']
display(pd.DataFrame(CFG.items(), columns=['Thành phần','Cấu hình đã dùng']))
print('Nguồn khớp hash; kết quả báo cáo ghi tại:', OUT)
''')
md('''### 3 Chia train validation test trước khi augmentation
Đọc lại split đã khóa, **không gọi train_test_split và không chia lại**. Train cập nhật trọng số; validation chọn checkpoint/phương án; test đánh giá cuối sau khi chốt.

Group dựa trên lesion_id và ảnh trùng byte. Kiểm ảnh hoặc group không nằm ở hai tập. Vẫn còn thiếu lesion_id, không có patient_id và chưa loại trừ đầy đủ ảnh gần trùng khác byte; không tuyên bố patient-disjoint.''')
code('''manifest = pd.read_csv(REPORT_DATA/'split_manifest.csv', keep_default_na=False)
assert manifest.image.is_unique and len(manifest) == 25327
parts = {s: manifest[manifest.split.eq(s)].copy() for s in ['train','val','test']}
assert {s: len(d) for s,d in parts.items()} == {'train':17723,'val':2539,'test':5065}
assert (manifest.label_name.map(dict(zip(LABELS, range(8)))) == manifest.label).all()

leakage_checks = []
for key in ['image', 'group', 'file_sha256', 'lesion_id']:
    known = manifest[key].astype(str).str.strip().ne('')
    crossing = (manifest.loc[known].groupby(key).split.nunique() > 1).sum()
    assert crossing == 0, f'Có {key} vượt split'
    leakage_checks.append({'định danh':key,'số giá trị vượt split':int(crossing),
                           'số dòng thiếu':int((~known).sum())})
display(pd.DataFrame(leakage_checks))
print('Không có patient_id trong manifest:', 'patient_id' not in manifest.columns)
''')
md('''### 4 EDA và vấn đề của dữ liệu
Đọc phân bố để thấy mức mất cân bằng. Thống kê dùng cho loss/sampler của các thí nghiệm chỉ tính từ train. Bảng test dưới đây thuộc báo cáo sau khi test đã hoàn tất, không dùng để thiết kế phương pháp.

ISIC gốc có 25.331 ảnh; audit giữ 25.327 sau loại bốn ảnh trùng byte xung đột nhãn. Tỷ lệ lớp trong dataset không phải tỷ lệ bệnh trong cộng đồng. Phạm vi đồ án là tám lớp của tập training công khai; cuộc thi gốc còn xét lớp ngoài phân bố trên test và dùng balanced accuracy để xếp hạng. Đồ án đã khóa macro-F1 làm tiêu chí chính, không đồng nhất hai protocol.''')
code('''names_vi = ['U hắc tố ác tính','Nốt ruồi tế bào hắc tố','Ung thư biểu mô tế bào đáy',
            'Dày sừng ánh sáng','Nhóm dày sừng lành tính','U xơ da',
            'Nhóm tổn thương mạch máu','Ung thư biểu mô tế bào vảy']
counts = pd.crosstab(manifest.label_name, manifest.split).reindex(LABELS)[['train','val','test']]
counts.insert(0, 'Tên nhãn', names_vi)
display(counts)
counts.to_csv(OUT/'class_counts.csv')
counts['train'].plot.bar(figsize=(8,2.8),color='#197c89',rot=0)
plt.ylabel('Số ảnh train'); plt.title('Train lệch lớp rõ rệt')
show_figure('train_class_distribution.png')
display(pd.DataFrame([read_json('reference/historical_data_audit.json')]))
''')
md('''### 5 Chọn ảnh minh họa và lỗi validation theo quy tắc cố định
**Ảnh lớp:** chọn ngẫu nhiên cố định một ảnh train mỗi lớp, mỗi group tối đa một ảnh; không chọn theo dự đoán đúng hay ảnh đẹp. Đây là minh họa mẫu dữ liệu, không phải bộ ảnh chuẩn chẩn đoán.

**Ảnh lỗi:** lấy bốn hướng nhầm có số lượng lớn nhất trên validation T02B, hòa thì theo thứ tự LABELS; chọn tối đa hai ảnh mỗi hướng bằng seed cố định, tránh trùng group. Không dùng ảnh test. Các nhãn dự đoán ở gallery lấy từ predictions lịch sử, không phải suy luận mới.''')
code('''val_pred = read_csv('test_report/validation_replay/predictions.csv')
assert val_pred.image.is_unique and len(val_pred) == len(parts['val'])
val_rows = val_pred.merge(parts['val'], on=['image','group','file_sha256'],
                          how='inner', validate='one_to_one')
assert len(val_rows) == 2539 and (val_rows.true_label == val_rows.label_name).all()
assert val_rows.split.eq('val').all()

# Bộ sinh riêng: không làm thay đổi seed hoặc trạng thái mô hình lịch sử.
def select_unique_rows(pool, number, rng, used_groups):
    selected = []
    ordered = pool.sort_values('image').reset_index(drop=True)
    for i in rng.permutation(len(ordered)):
        row = ordered.iloc[int(i)]
        if row.group not in used_groups:
            selected.append(row.to_dict()); used_groups.add(row.group)
        if len(selected) == number:
            break
    return selected

rng = np.random.default_rng(42)
used = set(); representatives = []
for label in LABELS:
    representatives += select_unique_rows(parts['train'][parts['train'].label_name.eq(label)],1,rng,used)
representatives = pd.DataFrame(representatives)
assert len(representatives) == 8 and representatives.group.is_unique

cm_val = confusion_matrix(val_rows.true_label,val_rows.pred_label,labels=LABELS)
ranked_pairs = sorted([(int(cm_val[i,j]),i,j) for i in range(8) for j in range(8)
                       if i!=j and cm_val[i,j]>0], key=lambda x:(-x[0],x[1],x[2]))[:4]
rng = np.random.default_rng(20261018); used = set(); errors = []; pair_info = []
for count,i,j in ranked_pairs:
    a,b = LABELS[i],LABELS[j]
    pool = val_rows[val_rows.true_label.eq(a) & val_rows.pred_label.eq(b)]
    chosen = select_unique_rows(pool,2,rng,used)
    for item in chosen: item['error_pair'] = a+' → '+b
    errors.extend(chosen)
    pair_info.append({'nhãn thật':a,'dự đoán':b,'số lỗi trên val':count,
                      'ảnh minh họa chọn được':len(chosen)})
errors = pd.DataFrame(errors)
assert representatives.split.eq('train').all() and errors.split.eq('val').all()
assert errors.group.is_unique
representatives.to_csv(OUT/'representative_train_selection.csv',index=False)
errors.to_csv(OUT/'validation_error_selection.csv',index=False)
display(pd.DataFrame(pair_info))
print('Đã chọn',len(representatives),'ảnh train và',len(errors),'ảnh lỗi validation; chưa mở ảnh.')
''')
md('''### 6 Đọc ảnh thật có kiểm hash và tạo gallery
Chỉ mở các ID đã chọn. Nếu không gắn ảnh, cell thông báo rõ chưa chạy và tiếp tục phần số liệu. Khi có ảnh, mọi ảnh thiếu, trùng đường dẫn hoặc lệch hash đều làm dừng; không thay bằng ảnh khác.

Khi trình bày, nói “đây là ảnh mang nhãn MEL trong dataset”; không khẳng định đặc điểm thị giác hoặc nguyên nhân sai khi chưa có đánh giá chuyên môn.''')
code('''def locate_selected_images(selection, root):
    assert selection.split.isin(['train','val']).all(), 'Không cho mở ảnh test'
    assert selection.image.is_unique
    if root is None or not Path(root).exists():
        return None
    wanted = set(selection.image)
    paths = {name: [] for name in wanted}
    for path in Path(root).rglob('*'):
        if path.is_file() and path.suffix.lower() in {'.jpg','.jpeg','.png'} and path.stem in wanted:
            paths[path.stem].append(path)
    if not any(paths.values()):
        return None
    for row in selection.itertuples():
        assert len(paths[row.image]) == 1, f'Thiếu/trùng đường dẫn ảnh: {row.image}; đặt IMAGE_ROOT'
        path = paths[row.image][0]
        assert sha_file(path) == row.file_sha256, f'Sai hash ảnh: {row.image}'
        if path.parent.name in LABELS:
            assert path.parent.name == row.label_name, f'Sai thư mục lớp: {row.image}'
    return {name: files[0] for name, files in paths.items()}

selected = pd.concat([representatives,errors],ignore_index=True)
assert selected.image.is_unique
PATHS = None
if SHOW_GALLERIES:
    root = Path(IMAGE_ROOT) if IMAGE_ROOT is not None else Path('/kaggle/input')
    PATHS = locate_selected_images(selected,root)
    if IMAGE_ROOT is not None and PATHS is None:
        raise FileNotFoundError('Đã đặt IMAGE_ROOT nhưng không tìm được ảnh đã chọn.')

RGB_IMAGES = {}
if PATHS is None:
    print('GALLERY NOT_RUN: chưa gắn ảnh hoặc SHOW_GALLERIES=False. Không dùng ảnh giả thay ISIC.')
else:
    image_audit = []
    for row in selected.itertuples():
        with Image.open(PATHS[row.image]) as image:
            rgb = image.convert('RGB'); rgb.load()
        RGB_IMAGES[row.image] = rgb
        image_audit.append({'image':row.image,'split':row.split,'path':str(PATHS[row.image]),
                            'sha256':sha_file(PATHS[row.image]),'width':rgb.width,'height':rgb.height})
    pd.DataFrame(image_audit).to_csv(OUT/'opened_images_audit.csv',index=False)
    STATUS['gallery'] = 'REAL_IMAGES_HASH_VERIFIED'


def gallery(frame, kind, filename):
    if not RGB_IMAGES:
        return
    ncols = 4; nrows = int(np.ceil(len(frame)/ncols))
    fig,axes = plt.subplots(nrows,ncols,figsize=(11,3*nrows),squeeze=False)
    for ax in axes.ravel(): ax.axis('off')
    for ax,row in zip(axes.ravel(),frame.itertuples()):
        # Giữ tỉ lệ khi hiển thị ảnh gốc, không biến gallery thành preprocessing mới.
        ax.imshow(RGB_IMAGES[row.image])
        title = row.label_name if kind=='class' else row.error_pair
        ax.set_title(title+'\\n'+row.image,fontsize=9)
    show_figure(filename)

gallery(representatives,'class','eight_train_classes.png')
gallery(errors,'error','validation_error_gallery.png')
''')
md('''### 7 Tiền xử lý cố định và augmentation D4
Pipeline cuối: RGB → PIL bilinear 224×224 → D4 nếu train → ToTensor → ImageNet normalize. Normalize là trừ mean/chia std theo kênh; không phải cân bằng màu SoG.

D4 dùng quay bội số 90° rồi lật, không nội suy lại ảnh vuông. Mã dưới dùng đúng hàm `t02_geometry` từ notebook T02AB; gallery vẽ đủ tám phép để giải thích, nhưng lúc train chỉ rút **một** mã mỗi lượt lấy ảnh.''')
source=json.loads((DATA/'reference/source_excerpts.json').read_text())
code("IMG_SIZE = CFG['image_size']\n"+source['t02_geometry']+'''
# Hàm chỉ thay hướng trên một ảnh; không tự đọc file hay thay đổi split.
D4_NAMES = ['Quay 0°','Quay 90°','Quay 180°','Quay 270°',
            'Quay 0° rồi lật ngang','Quay 90° rồi lật ngang',
            'Quay 180° rồi lật ngang','Quay 270° rồi lật ngang']
if RGB_IMAGES:
    chosen_id = representatives.iloc[0].image
    original = RGB_IMAGES[chosen_id]
    resized = original.resize((224,224),Image.Resampling.BILINEAR)
    fig,axes = plt.subplots(1,2,figsize=(7,3))
    axes[0].imshow(original); axes[0].set_title(f'Gốc {original.width}×{original.height}')
    axes[1].imshow(resized); axes[1].set_title('Resize 224×224')
    for ax in axes: ax.axis('off')
    show_figure('resize_example.png')
    fig,axes = plt.subplots(2,4,figsize=(10,5))
    for k,ax in enumerate(axes.ravel()):
        ax.imshow(t02_geometry(np.asarray(resized),'T02B_D4_R50',k))
        ax.set_title(D4_NAMES[k],fontsize=8); ax.axis('off')
    show_figure('d4_eight_transforms.png')
else:
    print('Chưa có ảnh thật: chỉ trình bày mã và danh sách tám phép D4.')
display(pd.DataFrame({'mã':range(8),'phép biến đổi':D4_NAMES}))
''')
md('''### 8 Dataset và DataLoader đã dùng khi huấn luyện
`Dataset` trả về một ảnh và nhãn; `DataLoader` ghép batch và quản lý thứ tự lấy mẫu. Chỉ train mới D4 và shuffle. Seed của worker/generator được quản lý trong notebook nguồn.

**Mã nguồn trích nguyên văn dưới đây để đọc và giải thích, không thực thi huấn luyện trong notebook báo cáo.** Biến toàn cục và các hàm phụ nằm trong `data/reference/locked_t02ab.ipynb`. Không lấy đoạn trích này như một script train độc lập.

```python
'''+source['T02Dataset']+'\n'+source['t02_loader']+'''```

Đường đi: `row.path` → đọc ảnh → resize → D4 nếu train → normalize → trả về tensor và nhãn. Label và split lấy từ manifest; không học nhãn bằng tên thư mục lúc dự đoán.''')
md('''### 9 Transfer learning và fine tuning
**Huấn luyện lịch sử:** khởi tạo ResNet50 bằng ImageNet V1, thay `fc` thành 8 đầu ra, fine-tune toàn bộ mạng gồm BatchNorm. Không có giai đoạn đóng băng backbone rồi mở dần trong protocol này; không thêm một giai đoạn chưa thực hiện vào câu chuyện báo cáo.

Mã tạo model nguyên bản:
```python
'''+source['build_model']+'''```

**Demo từ checkpoint:** `weights=None` chỉ tránh tải lại ImageNet; checkpoint đã huấn luyện ghi đè toàn bộ state. Đây không phải huấn luyện từ đầu với trọng số ngẫu nhiên.''')
code('''def load_final_model_for_demo(checkpoint):
    # Import torch muộn để phần bảng/biểu đồ vẫn chạy trên CPU không có torch.
    import torch
    from torch import nn
    from torchvision import models
    wanted = complete['checkpoint_sha']  # Không lấy hash B00 ở lock.reference
    assert sha_file(checkpoint) == wanted, 'Sai checkpoint T02B seed42'
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(LABELS))
    model.load_state_dict(torch.load(checkpoint,map_location='cpu',weights_only=True),strict=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    return model.to(device).eval(), device

print('Model cuối:',lock['method'],'| seed:',lock['baseline_config']['seed'],
      '| best epoch:',complete['best_epoch'])
print('Chưa nạp model. Chỉ nạp khi bật RUN_LIVE_VALIDATION ở phần cuối.')
''')
md('''### 10 Hàm đánh giá và cách đọc chỉ số
CE là loss để tối ưu trọng số. Macro-F1 là trung bình F1 tám lớp, dùng chọn checkpoint. Balanced accuracy là trung bình recall. Accuracy là tỷ lệ ảnh đúng toàn tập.

Hàm dưới tính số liệu từ nhãn và dự đoán đã lưu. Nó không suy luận ảnh và không tính lại CE từ logits. Chúng ta chỉ báo CE từ file đánh giá nguồn.''')
code('''def classification_report_from_predictions(predictions):
    # Cố định thứ tự đủ tám nhãn để tránh đổi ý nghĩa hàng/cột.
    y = predictions['true_label']
    pred = predictions['pred_label']
    assert set(y).issubset(LABELS) and set(pred).issubset(LABELS)
    scores = {'accuracy':accuracy_score(y,pred),
              'balanced_accuracy':balanced_accuracy_score(y,pred),
              'macro_f1':f1_score(y,pred,labels=LABELS,average='macro',zero_division=0)}
    precision,recall,f1,support = precision_recall_fscore_support(
        y,pred,labels=LABELS,zero_division=0)
    per_class = pd.DataFrame({'label':LABELS,'precision':precision,
                             'recall':recall,'f1':f1,'support':support})
    matrix = confusion_matrix(y,pred,labels=LABELS)
    return scores,per_class,matrix

val_scores,val_per_class,val_matrix = classification_report_from_predictions(val_pred)
display(pd.DataFrame([val_scores],index=['T02B validation']).mul(100).round(4))
''')
md('''### 11 Optimizer và training loop lịch sử
AdamW có một LR 10⁻⁴ cho toàn mạng; weight decay 10⁻⁴. Cosine scheduler giảm LR theo 16 epoch. Tối đa 16 epoch, patience 4; epoch cải thiện khi macro-F1 > best + 10⁻⁵. `scheduler.step()` ở cuối epoch.

Không cần huấn luyện lại để trình bày. Đoạn dưới là trích trực tiếp phần vòng lặp của `train_experiment` trong notebook T02AB; các hàm/biến phụ được định nghĩa trong notebook gốc. Mã ở khối Markdown để Run All không tạo thí nghiệm mới.

**Đọc các bước:** xóa gradient → forward → CE → backward → optimizer.step → đánh giá validation → lưu checkpoint nếu cải thiện → cập nhật scheduler → xét dừng.

```python
'''+source['train_experiment'][source['train_experiment'].index('    optimizer ='):source['train_experiment'].index("    model.load_state_dict")]+'''```

Không có weighted sampler hoặc weighted CE trong T02B. L01/S01 là các thí nghiệm riêng, không gộp vào pipeline cuối. Hàm gốc đầy đủ và history nằm trong `data/reference/locked_t02ab.ipynb` và `data/T02B_history.csv`.''')
code('''history = read_csv('T02B_history.csv')
best,wait,best_epoch = -1.0,0,None
for row in history.itertuples():
    if row.macro_f1 > best + CFG['min_delta']:
        best,wait,best_epoch = row.macro_f1,0,int(row.epoch)
    else:
        wait += 1
assert best_epoch == complete['best_epoch'] == 14
assert len(history) == complete['completed_epochs'] == 16
fig,axes = plt.subplots(1,2,figsize=(10,3))
axes[0].plot(history.epoch,history.train_loss,label='Train CE')
axes[0].plot(history.epoch,history.val_loss,label='Val CE'); axes[0].legend()
axes[1].plot(history.epoch,history.macro_f1*100,label='Val macro-F1')
axes[1].axvline(best_epoch,color='gray',linestyle='--',label='Checkpoint'); axes[1].legend()
for ax in axes: ax.set_xlabel('Epoch')
show_figure('training_history.png')
print('Epoch val loss thấp nhất:',int(history.loc[history.val_loss.idxmin(),'epoch']))
print('Epoch được chọn theo macro-F1:',best_epoch)
print('Loss train giảm mạnh không đủ chứng minh tổng quát hóa tốt.')
''')
md('''### 12 Tổng hợp mười phương án tiền xử lý và quan sát ảnh
Đây là **danh mục nghiên cứu**, không tuyên bố mười phương án đều đã train trên split R50. P04 SoG có kết quả R50 hiện hành; các trạng thái cũ được giữ riêng. P02 mang tên crop ở những hồ sơ khác nhau nên chưa coi là cùng phiên bản nếu thiếu đối chiếu mã.

Bằng chứng gồm cơ chế, giả thuyết, rủi ro và mức kiểm nguồn. R18 khác split/loss/augmentation nên không ghép vào bảng xếp hạng R50.

E01 đã được dùng trong quá trình nghiên cứu để ghép metadata với lỗi dự đoán và tìm các nhóm cần quan sát; notebook này không tính lại toàn bộ phân tích E01. E02 là bước quan sát 52 ảnh validation có chủ đích, giúp hình thành giả thuyết; không dùng tỷ lệ artifact của 52 ảnh để suy ra tỷ lệ toàn bộ dữ liệu hoặc nguyên nhân mô hình sai.''')
code('''options = read_csv('preprocessing_status_current.csv')
display(options[['id','name','problem','mechanism','detail_risk']])
print('Mức bằng chứng: trạng thái lịch sử và trạng thái R50 được tách riêng.')
display(options[['id','status','prior_evidence','current_R50_status']])
options.to_csv(OUT/'preprocessing_options_current.csv',index=False)
# Bảng chi tiết reference/reference_check/status/prior_evidence ở CSV nguồn.
review = read_csv('reference/visual_review_final.csv')
assert len(review)==52 and review.image.is_unique
assert set(review.image).issubset(set(parts['val'].image))
observations = []
for field in ['hair','ruler_or_ink','black_border_or_vignette','glare_or_reflection']:
    observations.append({'quan sát':field,'số ghi có':int(review[field].eq('có').sum()),'mẫu số':len(review)})
display(pd.DataFrame(observations))
print('E02 là 52 ảnh chọn có chủ đích, đánh giá không mù; đếm lại nhãn người quan sát, không kiểm chẩn đoán.')
''')
md('''### 13 Các thí nghiệm trong cùng một bảng báo cáo
Mỗi dòng liên kết với method, seed và nguồn dự đoán. B00 là đối chứng gốc; T02B là đối chứng trực tiếp cho SoG/L01/S01/F01/M01. T02A/B so với B00 thay augmentation.

- SoG: thêm chuẩn hóa màu, áp cả train/validation.
- L01: CE train trọng số 1/√n_train; validation CE vẫn không trọng số.
- S01: sampler cân bằng kỳ vọng theo lớp, có hoàn lại; loss vẫn CE thường.
- F01: LR backbone 10⁻⁵, fc 10⁻⁴.
- M01: EfficientNet-B0 và pretrained tương ứng; giữ D4 và CE. Đây là so sánh dưới cùng ngân sách, không phải mọi kiến trúc đều đã được tối ưu riêng.

Các bảng dưới lấy từ hồ sơ tổng hợp đã kiểm; cell không tính lại raw predictions của mọi run.''')
code('''experiments = read_csv('experiments_seed42.csv')
show = experiments[['run','macro_f1','balanced_accuracy','accuracy',
                    'delta_vs_T02B_pp','CI95_low_pp','CI95_high_pp','best_epoch','completed_epochs']].copy()
for col in ['macro_f1','balanced_accuracy','accuracy']:
    show[col] *= 100
show = show.rename(columns={'macro_f1':'Macro-F1 %','balanced_accuracy':'BA %','accuracy':'Accuracy %'})
display(show.round(4).fillna('—'))
experiments.to_csv(OUT/'experiments_seed42.csv',index=False)
plt.figure(figsize=(8,3))
plt.bar(experiments.run,experiments.macro_f1*100,
        color=['#197c89' if run=='T02B' else '#a9b6bf' for run in experiments.run])
plt.ylim(0,70); plt.ylabel('Validation macro-F1 (%)')
show_figure('experiments_seed42.png')
print('L01 cao hơn T02B 0,0249 pp; CI chứa 0, chưa đủ bằng chứng thay đối chứng.')
print('SoG, S01, F01, M01 không ghi nhận cải thiện macro-F1 ở lượt seed42 đã chạy.')
''')
md('''### 14 Xác nhận D4 với hai seed mới
Seed 42 dùng khám phá; 43/44 dùng kiểm thêm độ ổn định, vẫn cùng validation. So sánh ghép cặp B00 và T02B trong mỗi seed. Bootstrap theo group đánh giá bất định lấy mẫu validation; SD của Δ giữa seed là một đại lượng khác.''')
code('''pairs = read_csv('r02/PAIRED_DELTA_BY_SEED.csv')
show = pairs[['seed','B00_macro_f1','T02B_macro_f1','delta_macro_f1_pp',
              'ci95_low_pp','ci95_high_pp','delta_accuracy_pp']].copy()
show[['B00_macro_f1','T02B_macro_f1']] *= 100
display(show.round(4))
mean_delta = pairs.delta_macro_f1_pp.mean(); sd_delta = pairs.delta_macro_f1_pp.std(ddof=1)
summary = read_csv('r02/NEW_SEEDS_MEAN_SD.csv')
r = summary[(summary.method=='T02B_minus_B00') & (summary.metric=='macro_f1')].iloc[0]
assert abs(mean_delta-r.mean_percent_or_pp)<1e-10 and abs(sd_delta-r.sample_SD_pp)<1e-10
print(f'Hai seed mới: Δ trung bình {mean_delta:.4f} pp; sample SD {sd_delta:.4f} pp.')
print('D4 tăng F1 ở cả ba seed quan sát, nhưng mức tăng dao động; hai CI mới chứa 0.')
print('Seed43 accuracy giảm 1,4573 pp: giữ cả kết quả bất lợi trong báo cáo.')
''')
md('''### 15 Metrics cuối và confusion matrix
Mô hình T02B seed42 đã chốt trước test. Tính lại metrics từ predictions được lưu khi đánh giá chính thức của đồ án; **không mở ảnh test hoặc suy luận test mới**.

Test nội bộ 5.065 ảnh, không phải test cuộc thi. Chỉ T02B được test ở bước chốt nên không nói T02B thắng B00 trên test. Macro-F1 test nhỉnh hơn validation không phải cải thiện mô hình vì hai tập khác nhau.''')
code('''all_scores = {}; all_per_class = {}; all_cm = {}; frames = {}
for name,split in [('validation_replay','val'),('final_test','test')]:
    pred = read_csv(f'test_report/{name}/predictions.csv').sort_values('image').reset_index(drop=True)
    ref = parts[split].sort_values('image').reset_index(drop=True)
    assert pred.image.is_unique and len(pred)==len(ref)
    for a,b in [('image','image'),('true_label','label_name'),('group','group'),('file_sha256','file_sha256')]:
        assert pred[a].tolist()==ref[b].tolist()
    prob = pred[['p_'+l for l in LABELS]].to_numpy()
    assert np.isfinite(prob).all() and ((prob>=0)&(prob<=1)).all()
    assert np.allclose(prob.sum(1),1,atol=1e-6,rtol=0)
    assert np.array_equal(np.array(LABELS)[prob.argmax(1)],pred.pred_label)
    scores,per_class,cm = classification_report_from_predictions(pred)
    stored = read_json(f'test_report/{name}/metrics.json')
    assert all(abs(scores[k]-stored[k])<=1e-8 for k in scores)
    old_pc = read_csv(f'test_report/{name}/per_class.csv').set_index('label').loc[LABELS]
    assert np.allclose(per_class.drop(columns='label'),old_pc[per_class.columns[1:]],atol=1e-8,rtol=0)
    assert np.array_equal(cm,pd.read_csv(REPORT_DATA/f'test_report/{name}/confusion_matrix.csv',index_col=0).values)
    all_scores[name],all_per_class[name],all_cm[name],frames[name] = scores,per_class,cm,pred
    per_class.to_csv(OUT/f'{name}_per_class.csv',index=False)
    pd.DataFrame(cm,index=LABELS,columns=LABELS).to_csv(OUT/f'{name}_confusion.csv')
STATUS['saved_predictions_metrics'] = 'RECOMPUTED_MATCH'
display(pd.DataFrame(all_scores).T.mul(100).round(4))
display(all_per_class['final_test'])

fig,axes = plt.subplots(1,2,figsize=(12,4.5))
for ax,name in zip(axes,['validation_replay','final_test']):
    cm = all_cm[name]
    # Màu theo recall từng hàng, chữ vẫn là số ảnh để đọc support.
    row_fraction = cm / cm.sum(axis=1,keepdims=True)
    ax.imshow(row_fraction,cmap='Blues',vmin=0,vmax=1)
    ax.set_xticks(range(8),LABELS); ax.set_yticks(range(8),LABELS)
    ax.set_xlabel('Nhãn dự đoán'); ax.set_ylabel('Nhãn thật'); ax.set_title(name)
    for i in range(8):
        for j in range(8):
            ax.text(j,i,str(cm[i,j]),ha='center',va='center',fontsize=8,
                    color='white' if row_fraction[i,j]>.55 else 'black')
show_figure('confusion_matrices.png')
print('Màu chuẩn hóa theo hàng; con số trong ô là số ảnh.')
''')
md('''### 16 Tùy chọn dự đoán mới một ảnh validation
Cell mặc định bỏ qua. Nếu muốn trình bày model thật, gắn FULL Output T02AB có checkpoint T02B seed42, đặt `CHECKPOINT_PATH` (hoặc để tự tìm), bật `RUN_LIVE_VALIDATION=True`. Gallery phải có ảnh thật.

Chọn **ảnh validation đầu tiên theo image trước khi xem đúng/sai**, không chọn ca dự đoán đẹp. So với dự đoán lịch sử chỉ để kiểm demo; suy luận batch một ảnh ở môi trường khác không thay cho replay validation toàn tập đã nghiệm thu. Không thay checkpoint hoặc chỉnh model nếu demo sai.''')
code('''if not RUN_LIVE_VALIDATION:
    print('LIVE_VALIDATION NOT_RUN. Các kết quả ở trên lấy từ dự đoán đã lưu.')
else:
    import torch
    from torchvision import transforms
    import torchvision, PIL
    # Tự tìm đúng hash; không chọn file chỉ vì tên best_resnet50.pt.
    if CHECKPOINT_PATH is None:
        candidates = list(Path('/kaggle/input').rglob('best_resnet50.pt'))
        matches = [p for p in candidates if sha_file(p)==complete['checkpoint_sha']]
        assert matches, 'Thiếu đúng checkpoint T02B seed42 trong FULL Output'
        CHECKPOINT_PATH = sorted(matches)[0]
    model,device = load_final_model_for_demo(Path(CHECKPOINT_PATH))
    one = parts['val'].sort_values('image').head(1)
    root = Path(IMAGE_ROOT) if IMAGE_ROOT is not None else Path('/kaggle/input')
    live_paths = locate_selected_images(one,root)
    assert live_paths is not None, 'Thiếu ảnh validation cho suy luận'
    row = one.iloc[0]
    with Image.open(live_paths[row.image]) as im:
        rgb = im.convert('RGB').resize((224,224),Image.Resampling.BILINEAR)
    transform = transforms.Compose([transforms.ToTensor(),
        transforms.Normalize([.485,.456,.406],[.229,.224,.225])])
    with torch.inference_mode():
        scores = model(transform(rgb).unsqueeze(0).to(device)).softmax(1)[0].cpu().numpy()
    assert np.isfinite(scores).all()
    old = val_pred.set_index('image').loc[row.image]
    result = dict(image=row.image,split='val',true_label=row.label_name,
                  pred_label=LABELS[int(scores.argmax())],historical_pred=old.pred_label,
                  max_abs_probability_diff=float(np.max(np.abs(scores-old[['p_'+l for l in LABELS]].to_numpy(dtype=float)))),
                  checkpoint_sha=sha_file(CHECKPOINT_PATH),image_sha=sha_file(live_paths[row.image]),
                  torch=str(torch.__version__),torchvision=str(torchvision.__version__),pillow=PIL.__version__,device=str(device))
    display(rgb); display(pd.DataFrame({'label':LABELS,'softmax':scores}))
    print('Nhãn thật:',result['true_label'],'| dự đoán mới:',result['pred_label'],
          '| lịch sử:',result['historical_pred'])
    print('Softmax chưa hiệu chuẩn thành xác suất chẩn đoán.')
    (OUT/'live_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    STATUS['live_validation'] = 'ONE_VALIDATION_IMAGE_INFERRED; not full replay'
''')
md('''### 17 Kết luận và hồ sơ nguồn để trả lời cô
Có bằng chứng thực nghiệm cho việc giữ T02B trong phạm vi đồ án, nhưng chưa chứng minh D4 luôn tốt hơn. Phần lớn phương án mới chỉ một seed; ngân sách 16 epoch không đảm bảo tối ưu từng kiến trúc. Validation tái dùng để lựa chọn; test đã xem nên các nghiên cứu tiếp cần nguồn đánh giá cuối chưa tham gia lựa chọn cho kết luận độc lập.

**Câu chốt:** “Em không chỉ thử mô hình rồi chọn điểm cao. Em khóa cách đánh giá, nghiên cứu phương án, giữ cả kết quả chưa cải thiện, xác nhận D4 bằng seed mới và đánh giá một checkpoint đã chốt trên test nội bộ.”

Nguồn chính:
- `data/reference/locked_t02ab.ipynb`: mã huấn luyện B00/T02 gốc; notebook báo cáo không thay thế nguồn này.
- `data/r02/EXPERIMENT_TABLE.csv`: tám run seed42 và bốn run seed43/44, có tên/hash nguồn.
- `data/test_report/`: đánh giá cuối, predictions/metrics/audit và cấu hình.
- `data/PREPROCESSING_OPTIONS.csv`: danh mục cũ; xem bảng trạng thái cập nhật để tránh nhầm P04 chưa chạy.
- `data/reference/visual_review_final.csv`: quan sát E02 do người dùng điền, không phải nhận xét y học độc lập.

Tên nhóm theo ISIC: https://challenge.isic-archive.com/landing/2019/ . Gessert gần phạm vi nhưng không cùng protocol: https://arxiv.org/abs/1910.03910 . Đọc bảng tài liệu lịch sử trong `data/LITERATURE_NOTE_HISTORICAL.md` kèm giới hạn nguồn; đề xuất cũ trong tài liệu không thay hiện trạng đã chốt.''')
code('''STATUS['selected_method'] = 'T02B_D4_R50 seed42'
STATUS['test_status'] = 'Previously evaluated; displayed from saved predictions'
STATUS['source_hash_checks'] = len(EXPECTED)
(OUT/'presentation_status.json').write_text(json.dumps(STATUS,ensure_ascii=False,indent=2))
(OUT/'source_hashes.json').write_text(json.dumps(EXPECTED,indent=2))
zip_path = OUT.with_suffix('.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for path in sorted(OUT.rglob('*')):
        if path.is_file(): z.write(path,path.relative_to(OUT))
print('Trạng thái:',STATUS)
print('Gửi CHA notebook đã chạy và ZIP output này nếu cần kiểm gallery:',zip_path)
''')
nb.cells=cells;nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'},'report_version':'1.0'}
nbformat.write(nb,R/'ISIC2019_Bao_cao_tong_hop_v1_0.ipynb')
print('Built',len(cells),'cells,',sum(c.cell_type=='code' for c in cells),'code cells')
