# FINAL_EVAL_PREP v1.0 — chỉ validation mặc định, không có hàm huấn luyện.
from pathlib import Path
import json,hashlib,random,traceback,zipfile,os,time
import numpy as np
import pandas as pd
from PIL import Image
import PIL,cv2,torch,torchvision
from torch import nn
from torch.utils.data import Dataset,DataLoader,SequentialSampler
from torchvision import models,transforms

RUN_TRAIN=False
RUN_FINAL_TEST=False
CHA_APPROVAL_NOTE=''
INPUT_ROOT=Path('/kaggle/input')
SOURCE_ROOT=None
IMAGE_ROOT=None
OUTPUT_ROOT=Path('/kaggle/working/FINAL_EVAL_PREP_v1_0')
LABELS=['MEL','NV','BCC','AK','BKL','DF','VASC','SCC']
SEED=42
PROB_ATOL=1e-6
PROB_RTOL=0.0
METRIC_ATOL=1e-8
VAL_LOSS_ATOL=1e-6
BATCH=32
WORKERS=2
VALIDATION_PASS=False
FINAL_TEST_ARMED=False
TEST_IMAGE_OPEN_COUNT=0
IMAGE_OPEN_COUNTS={'val':0,'test':0}
normalize=transforms.Compose([transforms.ToTensor(),transforms.Normalize([.485,.456,.406],[.229,.224,.225])])

def sha_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def dump_json(path,data):
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def assert_flags():
    assert RUN_TRAIN is False,'STOP: không có quyền train'
    assert (PROB_ATOL,PROB_RTOL,METRIC_ATOL,VAL_LOSS_ATOL)==(1e-6,0.0,1e-8,1e-6),'STOP tolerance changed'
    assert (SEED,BATCH,WORKERS)==(42,32,2)

def assert_final_test_permission():
    assert RUN_FINAL_TEST is True,'STOP final test disabled'
    assert isinstance(CHA_APPROVAL_NOTE,str) and CHA_APPROVAL_NOTE.strip(),'STOP cần ghi xác nhận CHA đã duyệt'
    assert VALIDATION_PASS is True,'STOP validation chưa đạt trong lần chạy hiện tại'

def split_separation(manifest):
    assert set(manifest.split)=={'train','val','test'} and manifest.image.is_unique
    assert manifest[['image','file_sha256','group']].astype(str).apply(lambda s:s.str.strip().ne('').all()).all(),'STOP missing split identifier'
    result={}
    for col in ['image','file_sha256','group','lesion_id']:
        if col not in manifest:
            assert col=='lesion_id','STOP missing split key'
            result[col]={'available':False};continue
        usable=manifest[col].astype(str).str.strip().ne('')
        assert manifest.loc[usable].groupby(col).split.nunique().max()==1,f'STOP leakage {col}'
        result[col]=dict(available=True,nonempty=int(usable.sum()),missing=int((~usable).sum()),cross_split_values=0)
    # Patient metadata không có trong manifest thì không được gọi là patient-disjoint.
    if 'patient_id' in manifest:
        usable=manifest.patient_id.astype(str).str.strip().ne('')
        if usable.any():assert manifest.loc[usable].groupby('patient_id').split.nunique().max()==1,'STOP patient leakage'
        result['patient_id']=dict(available=True,missing=int((~usable).sum()))
    else:result['patient_id']=dict(available=False,limit='Không kiểm được patient-disjoint')
    return result

def verify_sources():
    global SOURCE_ROOT,manifest,source_complete,source_lock
    assert_flags()
    OUTPUT_ROOT.mkdir(parents=True,exist_ok=False)
    roots=[Path(SOURCE_ROOT)] if SOURCE_ROOT else [p.parent for p in INPUT_ROOT.rglob('B00_protocol_lock.json')]
    verified=[]
    for root in roots:
        if not (root/'T02B_D4_R50/T02B_D4_R50/best_resnet50.pt').is_file():continue
        for name,h in EXPECTED_FILES.items():
            assert (root/name).is_file(),f'STOP missing {root/name}'
            assert sha_file(root/name)==h,f'STOP source hash {root/name}'
        verified.append(root)
    assert verified,'Thiếu FULL Output T02AB seed42, không chọn checkpoint khác'
    SOURCE_ROOT=sorted(verified)[0]
    source_complete=json.loads((SOURCE_ROOT/'T02B_D4_R50/T02B_D4_R50/complete.json').read_text())
    source_lock=json.loads((SOURCE_ROOT/'T02B_D4_R50/candidate_protocol_lock.json').read_text())
    assert source_complete['method']==source_lock['method']=='T02B_D4_R50'
    assert source_complete['checkpoint_sha']==EXPECTED_CHECKPOINT_SHA
    assert source_complete['lock_sha']==sha_file(SOURCE_ROOT/'T02B_D4_R50/candidate_protocol_lock.json')
    # reference.checkpoint_sha thuộc B00; không nhầm nó với checkpoint T02B.
    baseline=json.loads((SOURCE_ROOT/'B00_complete.json').read_text())
    assert source_lock['reference']['checkpoint_sha']==baseline['checkpoint_sha']
    assert source_lock['reference']['baseline_lock_sha']==sha_file(SOURCE_ROOT/'B00_protocol_lock.json')
    assert source_lock['reference']['classifier_test_used'] is False
    config=source_lock['baseline_config']
    assert config['seed']==42 and config['labels']==LABELS and config['model']=='resnet50' and config['size']==224
    manifest=pd.read_csv(SOURCE_ROOT/'split_manifest.csv',keep_default_na=False)
    assert len(manifest)==25327 and sha_file(SOURCE_ROOT/'split_manifest.csv')==EXPECTED_MANIFEST_SHA
    separation=split_separation(manifest)
    # Không tính class counts/metrics test trong preparation; chỉ dùng metadata tách split.
    val=manifest[manifest.split.eq('val')].sort_values('image').reset_index(drop=True)
    assert len(val)==2539 and set(val.label_name)==set(LABELS)
    assert np.array_equal(val.label.to_numpy(),val.label_name.map({l:i for i,l in enumerate(LABELS)}))
    dump_json(OUTPUT_ROOT/'source_audit.json',dict(status='PASS_SOURCE_CHECKS',source_root=str(SOURCE_ROOT),checkpoint_sha=EXPECTED_CHECKPOINT_SHA,manifest_sha=EXPECTED_MANIFEST_SHA,split_separation=separation,test_images_opened=0,test_metrics_computed=False))
    return val

def verify_environment():
    actual=dict(torch=str(torch.__version__),torchvision=str(torchvision.__version__),numpy=np.__version__,pandas=pd.__version__,sklearn=__import__('sklearn').__version__,cv2=cv2.__version__,pillow=PIL.__version__,gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')
    dump_json(OUTPUT_ROOT/'environment_actual.json',actual)
    for k,v in source_lock['environment'].items():assert actual[k]==v,f'STOP environment {k}: {actual[k]} != {v}'
    assert actual['gpu']=='Tesla T4' and torch.cuda.is_available()
    random.seed(42);np.random.seed(42);torch.manual_seed(42);torch.cuda.manual_seed_all(42)
    torch.backends.cudnn.deterministic=True;torch.backends.cudnn.benchmark=False
    cv2.setNumThreads(1)
    return actual

def map_images(data,split):
    if split=='test':assert_final_test_permission()
    else:assert split=='val'
    assert data.split.eq(split).all()
    # Liệt kê tên đường dẫn có thể thấy test filenames, nhưng chỉ mở/hash wanted IDs.
    wanted=set(data.image);paths={};scan=Path(IMAGE_ROOT) if IMAGE_ROOT else INPUT_ROOT
    for p in scan.rglob('*'):
        if p.suffix.lower() in {'.jpg','.jpeg','.png'} and p.stem in wanted:
            assert p.stem not in paths,f'STOP duplicate image path {p.stem}; đặt IMAGE_ROOT'
            paths[p.stem]=p
    assert set(paths)==wanted,'STOP missing selected-split images'
    mapped=data.copy();mapped['path']=mapped.image.map(paths)
    for row in mapped.itertuples():assert sha_file(row.path)==row.file_sha256,f'STOP image bytes {row.image}'
    return mapped

class EvalDataset(Dataset):
    def __init__(self,data,split):
        if split=='test':assert_final_test_permission()
        else:assert split=='val'
        assert data.split.eq(split).all()
        self.data=data.reset_index(drop=True);self.split=split
        self.test_authorized=(split=='test' and RUN_FINAL_TEST and VALIDATION_PASS and bool(CHA_APPROVAL_NOTE.strip()))
    def __len__(self):return len(self.data)
    def __getitem__(self,index):
        row=self.data.iloc[index]
        assert row.split==self.split
        if self.split=='test':assert self.test_authorized,'STOP unauthorized test dataset'
        with Image.open(row.path) as im:
            image=im.convert('RGB').resize((224,224),Image.Resampling.BILINEAR)
        return normalize(image),int(row.label)

def seed_worker(worker_id):
    seed=torch.initial_seed()%(2**32)
    random.seed(seed);np.random.seed(seed)

def make_loader(data,split):
    loader=DataLoader(EvalDataset(data,split),batch_size=32,shuffle=False,num_workers=2,pin_memory=True,worker_init_fn=seed_worker,generator=torch.Generator().manual_seed(42),drop_last=False)
    assert isinstance(loader.sampler,SequentialSampler)
    assert loader.batch_size==32 and loader.num_workers==2 and loader.drop_last is False
    return loader

def load_selected_model():
    checkpoint=SOURCE_ROOT/'T02B_D4_R50/T02B_D4_R50/best_resnet50.pt'
    assert sha_file(checkpoint)==EXPECTED_CHECKPOINT_SHA
    # weights=None chỉ tránh tải ImageNet lần nữa; strict full checkpoint ghi đè toàn bộ state.
    model=models.resnet50(weights=None)
    model.fc=nn.Linear(model.fc.in_features,8)
    state=torch.load(checkpoint,map_location='cpu',weights_only=True)
    model.load_state_dict(state,strict=True)
    assert model.fc.out_features==8 and model.fc.in_features==2048
    model=model.to('cuda');model.eval()
    assert not model.training and all(not m.training for m in model.modules())
    return model

def numeric_metrics(y,p):
    cm=np.zeros((8,8),dtype=np.int64)
    np.add.at(cm,(np.asarray(y,dtype=int),np.asarray(p,dtype=int)),1)
    tp=np.diag(cm);support=cm.sum(1);pred_support=cm.sum(0)
    precision=np.divide(tp,pred_support,out=np.zeros(8),where=pred_support>0)
    recall=np.divide(tp,support,out=np.zeros(8),where=support>0)
    f1=np.divide(2*tp,support+pred_support,out=np.zeros(8),where=(support+pred_support)>0)
    scores=dict(accuracy=float(tp.sum()/cm.sum()),balanced_accuracy=float(recall[support>0].mean()),macro_f1=float(f1.mean()))
    report=pd.DataFrame(dict(label=LABELS,precision=precision,recall=recall,f1=f1,support=support))
    return scores,report,cm

def infer(model,data,split):
    if split=='test':assert_final_test_permission()
    else:assert split=='val'
    assert not model.training
    loader=make_loader(data,split);probs=[];ys=[];loss_sum=0.;n=0
    criterion=nn.CrossEntropyLoss(weight=None,reduction='mean',label_smoothing=0)
    with torch.inference_mode():
        for images,y in loader:
            images=images.to('cuda');y=y.to('cuda')
            assert torch.isfinite(images).all().item(),'STOP nonfinite image tensor'
            logits=model(images);assert torch.isfinite(logits).all().item(),'STOP nonfinite logits'
            loss=criterion(logits,y);assert torch.isfinite(loss).item(),'STOP nonfinite loss'
            probs.append(logits.softmax(1).cpu().numpy());ys.extend(y.cpu().tolist())
            loss_sum+=loss.item()*len(y);n+=len(y)
    probabilities=np.concatenate(probs);assert len(probabilities)==len(data)
    assert np.array_equal(np.array(ys),data.label.to_numpy()),'STOP loader order'
    predictions=probabilities.argmax(1)
    output=data[['image','group','file_sha256','label_name']].rename(columns={'label_name':'true_label'}).copy()
    output['pred_label']=[LABELS[i] for i in predictions]
    for i,l in enumerate(LABELS):output['p_'+l]=probabilities[:,i]
    scores,pc,cm=numeric_metrics(ys,predictions)
    return output,dict(loss=float(loss_sum/n),**scores),pc,cm

def compare_validation(actual,reference,scores):
    a=actual.sort_values('image').reset_index(drop=True);r=reference.sort_values('image').reset_index(drop=True)
    assert len(a)==len(r)==2539 and a.image.is_unique and r.image.is_unique
    for col in ['image','group','file_sha256','true_label','pred_label']:
        assert np.array_equal(a[col].astype(str),r[col].astype(str)),f'STOP validation {col} mismatch'
    cols=['p_'+l for l in LABELS];pa=a[cols].to_numpy();pr=r[cols].to_numpy()
    assert np.isfinite(pa).all() and np.isfinite(pr).all()
    delta=np.abs(pa-pr);max_abs=float(delta.max())
    audit=dict(probability_ATOL=PROB_ATOL,probability_RTOL=PROB_RTOL,max_probability_absolute_error=max_abs,n_pred_label_mismatches=int(a.pred_label.ne(r.pred_label).sum()),metric_ATOL=METRIC_ATOL,loss_ATOL=VAL_LOSS_ATOL)
    dump_json(OUTPUT_ROOT/'validation_comparison_attempt.json',audit)
    assert np.allclose(pa,pr,atol=PROB_ATOL,rtol=PROB_RTOL),'STOP validation probability tolerance'
    for k in ['accuracy','balanced_accuracy','macro_f1']:
        assert abs(scores[k]-source_complete[k])<=METRIC_ATOL,f'STOP validation metric {k}'
    return audit

def export_split(output,scores,pc,cm,split):
    if split=='test':assert_final_test_permission()
    else:assert split=='val'
    folder=OUTPUT_ROOT/('validation_replay' if split=='val' else 'final_test')
    folder.mkdir(exist_ok=False)
    output.to_csv(folder/'predictions.csv',index=False);pc.to_csv(folder/'per_class.csv',index=False)
    pd.DataFrame(cm,index=LABELS,columns=LABELS).to_csv(folder/'confusion_matrix.csv')
    dump_json(folder/'metrics.json',scores)
    dump_json(folder/'config.json',dict(method='T02B_D4_R50',seed=42,checkpoint_sha=EXPECTED_CHECKPOINT_SHA,labels=LABELS,split=split,resize='RGB bilinear224',normalization='ImageNet mean/std',augmentation=False,TTA=False,AMP=False,shuffle=False,batch=32,workers=2,model_eval=True,inference_mode=True,threshold='argmax; no calibration',train=False,CHA_approval_note=CHA_APPROVAL_NOTE if split=='test' else '',source_sha=SOURCE_CODE_SHA,split_manifest_sha=EXPECTED_MANIFEST_SHA))
    return folder

def replay_validation(model,val):
    global VALIDATION_PASS
    VALIDATION_PASS=False
    mapped=map_images(val,'val')
    out,scores,pc,cm=infer(model,mapped,'val')
    ref=pd.read_csv(SOURCE_ROOT/'T02B_D4_R50/T02B_D4_R50/val_predictions.csv',keep_default_na=False)
    folder=export_split(out,scores,pc,cm,'val')  # giữ predictions mới nếu compare STOP
    audit=compare_validation(out,ref,scores)
    source_metrics=json.loads((SOURCE_ROOT/'T02B_D4_R50/T02B_D4_R50/val_metrics.json').read_text())
    assert abs(scores['loss']-source_metrics['loss'])<=VAL_LOSS_ATOL,'STOP validation CE loss mismatch'
    source_pc=pd.read_csv(SOURCE_ROOT/'T02B_D4_R50/T02B_D4_R50/val_per_class.csv',index_col=0).reindex(LABELS)
    assert np.allclose(pc[['precision','recall','f1','support']],source_pc[['precision','recall','f1-score','support']],atol=METRIC_ATOL,rtol=0),'STOP per-class mismatch'
    source_cm=pd.read_csv(SOURCE_ROOT/'T02B_D4_R50/T02B_D4_R50/val_confusion.csv',index_col=0)
    assert np.array_equal(cm,source_cm.to_numpy()),'STOP confusion mismatch'
    assert sha_file(SOURCE_ROOT/'T02B_D4_R50/T02B_D4_R50/best_resnet50.pt')==EXPECTED_CHECKPOINT_SHA
    VALIDATION_PASS=True
    audit.update(status='PASS_KAGGLE_VALIDATION_REPLAY',checkpoint_sha=EXPECTED_CHECKPOINT_SHA,n_val=2539,test_evaluated=False)
    dump_json(OUTPUT_ROOT/'validation_audit.json',audit)
    return scores

def run_authorized_final_test(model):
    global FINAL_TEST_ARMED
    assert_final_test_permission()
    assert sha_file(SOURCE_ROOT/'split_manifest.csv')==EXPECTED_MANIFEST_SHA
    assert sha_file(SOURCE_ROOT/'T02B_D4_R50/T02B_D4_R50/best_resnet50.pt')==EXPECTED_CHECKPOINT_SHA
    FINAL_TEST_ARMED=True
    # Lần đầu chọn nhãn test cho scoring chỉ sau gate.
    data=manifest[manifest.split.eq('test')].sort_values('image').reset_index(drop=True)
    mapped=map_images(data,'test');out,scores,pc,cm=infer(model,mapped,'test')
    export_split(out,scores,pc,cm,'test')
    dump_json(OUTPUT_ROOT/'final_test_audit.json',dict(status='COMPLETED_AUTHORIZED_FINAL_TEST',CHA_approval_note=CHA_APPROVAL_NOTE,checkpoint_sha=EXPECTED_CHECKPOINT_SHA,selection_locked_before_test=True,no_training=True))
    return scores

def export_reports():
    files=[p for p in sorted(OUTPUT_ROOT.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt']
    (OUTPUT_ROOT/'SHA256SUMS.txt').write_text(''.join(f'{sha_file(p)}  {p.relative_to(OUTPUT_ROOT)}\n' for p in files))
    path=OUTPUT_ROOT.parent/(OUTPUT_ROOT.name+'_reports.zip')
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUTPUT_ROOT.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(OUTPUT_ROOT)))
    return str(path)

def run():
    global VALIDATION_PASS
    VALIDATION_PASS=False
    assert not OUTPUT_ROOT.exists(),'STOP output đã có; không ghi đè hoặc chọn checkpoint khác'
    try:
        assert sha_file(Path(__file__))==SOURCE_CODE_SHA,'STOP evaluation source changed'
        val=verify_sources();verify_environment()
        (OUTPUT_ROOT/'evaluation_source.py').write_bytes(Path(__file__).read_bytes())
        dump_json(OUTPUT_ROOT/'FINAL_EVAL_CONFIG.json',dict(task='FINAL_EVAL_PREP',version='1.0',RUN_TRAIN=RUN_TRAIN,RUN_FINAL_TEST=RUN_FINAL_TEST,checkpoint_sha=EXPECTED_CHECKPOINT_SHA,PROB_ATOL=PROB_ATOL,PROB_RTOL=PROB_RTOL,METRIC_ATOL=METRIC_ATOL,VAL_LOSS_ATOL=VAL_LOSS_ATOL,source_sha=SOURCE_CODE_SHA))
        model=load_selected_model();replay_validation(model,val)
        if RUN_FINAL_TEST:
            run_authorized_final_test(model)
            state='FINAL_TEST_COMPLETED_AFTER_APPROVAL'
        else:
            state='VALIDATION_REPLAY_PASS_FINAL_TEST_NOT_RUN'
            print('RUN_FINAL_TEST=False: không mở ảnh test, không tính metrics test.')
        dump_json(OUTPUT_ROOT/'CURRENT_STATUS.json',dict(status=state,validation_pass=VALIDATION_PASS,final_test_evaluated=RUN_FINAL_TEST,train=False))
    except Exception as e:
        if OUTPUT_ROOT.exists():
            dump_json(OUTPUT_ROOT/'STOP.json',dict(status='STOP_REPORT_TO_CHA',type=type(e).__name__,message=str(e),traceback=traceback.format_exc(),no_fallback=True,no_tolerance_relaxation=True))
        raise
    finally:
        if OUTPUT_ROOT.exists():print('Reports:',export_reports())

EXPECTED_FILES={'split_manifest.csv': '38a5a9aca907d56685bddfcd874e162d8bf2c141a7247025410eeeee6bcf522a', 'B00_protocol_lock.json': 'c598d6fb6835ea831c8c169233768f1c2ed860206356b5c09a7164dd8099edec', 'B00_complete.json': '8201f09b2d3b305cc1c2beb227652c8a249e6e6eb24ec12e0ab86be670949a2b', 'B00_val_predictions.csv': 'd002ba18195a95c8aa546d6c6c50a711a4343e91b9ecf56abf3223390a7be225', 'T02B_D4_R50/candidate_protocol_lock.json': '47eacd88da997d3df482a2682f515847e5acb442b1257fd34e65f80eefab3559', 'T02B_D4_R50/candidate_source.py': 'ce274d6b2dcb00dc3c1a2604a14e6920e4af5f549865ab1f04e56699fa93f9bc', 'T02B_D4_R50/T02B_D4_R50/complete.json': '1b3d0a01d8376d11206db78a7310f3e16dec41cf12d0925aca2b6b94ab6ac672', 'T02B_D4_R50/T02B_D4_R50/history.csv': 'a58f2b866d5bf81095d6d9d2904889840706b3869b4cbac32bc80811c0bf7bf5', 'T02B_D4_R50/T02B_D4_R50/val_predictions.csv': '41a406228c3654282b0710346e66c437837c8e1d92117db6ee6933eab6f6774b', 'T02B_D4_R50/T02B_D4_R50/val_metrics.json': 'bba570b85662784a26fa8f06797b152ac9d5c768fdb21f8c4a3dc46f901b368a', 'T02B_D4_R50/T02B_D4_R50/val_per_class.csv': 'd72e6f1891378ce16ef25d96f0aa110d0fbd0f71c27a1e93897aa7e4984041e2', 'T02B_D4_R50/T02B_D4_R50/val_confusion.csv': '98301d70d06aa4140bc6725c0f6013bb89b9a783d580e6856ef26a95d30fffbc', 'T02B_D4_R50/T02B_D4_R50/best_resnet50.pt': 'f7e9f6eace2c9e6dbf91326b7e2a891966687295b7ad726fd88d9682fa0199ad'}
EXPECTED_CHECKPOINT_SHA='f7e9f6eace2c9e6dbf91326b7e2a891966687295b7ad726fd88d9682fa0199ad'
EXPECTED_MANIFEST_SHA='38a5a9aca907d56685bddfcd874e162d8bf2c141a7247025410eeeee6bcf522a'
SOURCE_CODE_SHA=None  # Notebook đặt bằng hash implementation đã kiểm trước import.
