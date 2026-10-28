"""P01–P10: một phương án mỗi phiên; giữ nguyên hàm train R50 gốc.
Chưa chạy ảnh thật/Torch/GPU tại lúc bàn giao. Không gọi test.
"""
from pathlib import Path
import json, hashlib, time, random, shutil, gc, zipfile, sys, platform
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, classification_report, confusion_matrix

def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def dump_json(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str),encoding='utf-8')

def state_sha(model):
    h=hashlib.sha256()
    for k,v in model.state_dict().items():h.update(k.encode());h.update(v.detach().cpu().numpy().tobytes())
    return h.hexdigest()

def checked_predictions(pred,truth,labels):
    p=pred.sort_values('image').reset_index(drop=True)
    t=truth.sort_values('image').reset_index(drop=True)
    assert p.image.is_unique and len(p)==len(t)==2539
    for a,b in [('image','image'),('group','group'),('file_sha256','file_sha256'),('true_label','label_name')]:
        assert p[a].tolist()==t[b].tolist(),a
    probs=p[['p_'+x for x in labels]].to_numpy()
    assert np.isfinite(probs).all() and ((probs>=0)&(probs<=1)).all()
    assert np.allclose(probs.sum(1),1,atol=1e-6,rtol=0)
    assert np.array_equal(np.array(labels)[probs.argmax(1)],p.pred_label)
    return p

def run(bundle_root,image_root,method='P01',run_train=False,review_csv=None):
    root=Path(bundle_root)
    out=Path('/kaggle/working')/('P10_R50_'+method+'_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    out.mkdir(parents=True,exist_ok=False)
    audit={'status':'STARTED','method':method,'train':'NOT_RUN','test':'NOT_RUN','checks':[]}
    try:
        assert method in [f'P{i:02}' for i in range(1,11)]
        assert not(run_train and method=='P04'),'P04 đã có run lịch sử; cần quyết định tái sử dụng riêng, không train trùng tự động.'
        # Giữ bản source và lock của chính lần thực thi này.
        hashes=json.loads((root/'bundle_hashes.json').read_text())
        for name,h in hashes.items():assert sha_file(root/name)==h,name
        for name in ['runner.py','locked_functions.py','preprocess_original.py','source_function_hashes.json']:
            shutil.copyfile(root/name,out/name)
        lock=json.loads((root/'reference/candidate_protocol_lock.json').read_text())
        complete=json.loads((root/'reference/complete.json').read_text())
        cfg=lock['baseline_config'];labels=cfg['labels']
        assert (cfg['seed'],cfg['size'],cfg['batch'],cfg['epochs'],cfg['patience'],cfg['workers'])==(42,224,32,16,4,2)
        assert sha_file(root/'reference/split_manifest.csv')==lock['reference']['split_sha']
        assert sha_file(root/'reference/candidate_protocol_lock.json')==complete['lock_sha']
        frame=pd.read_csv(root/'reference/split_manifest.csv',keep_default_na=False)
        assert frame.image.is_unique and len(frame)==25327
        assert set(frame.split)=={'train','val','test'}
        assert frame.label_name.eq(frame.label.map(dict(enumerate(labels)))).all()
        for col in ['image','file_sha256','group','lesion_id']:
            if col in frame:
                s=frame[frame[col].ne('')];assert s.groupby(col).split.nunique().max()==1,col
        parts={s:frame[frame.split.eq(s)].copy() for s in ['train','val']}
        assert len(parts['train'])==17723 and len(parts['val'])==2539
        control=checked_predictions(pd.read_csv(root/'reference/val_predictions.csv'),parts['val'],labels)
        assert abs(f1_score(control.true_label,control.pred_label,labels=labels,average='macro')-complete['macro_f1'])<1e-10
        audit['checks'].append('source_manifest_control_predictions')
        # Test chỉ được biết trong manifest để kiểm split; không lập đường dẫn hay mở ảnh test.
        assert image_root is not None,'Đặt IMAGE_ROOT đúng thư mục ảnh ISIC trong Input.'
        wanted=set(pd.concat(parts.values()).image);paths={k:[] for k in wanted}
        for p in Path(image_root).rglob('*'):
            if p.is_file() and p.suffix.lower() in {'.jpg','.jpeg','.png'} and p.stem in wanted:paths[p.stem].append(p)
        for name,data in parts.items():
            resolved=[]
            for row in data.itertuples():
                assert len(paths[row.image])==1,f'Missing/duplicate {row.image}'
                p=paths[row.image][0];assert sha_file(p)==row.file_sha256,row.image
                if p.parent.name in labels:assert p.parent.name==row.label_name,row.image
                resolved.append(str(p))
            data['path']=resolved
        audit['checks'].append('all_train_val_image_hashes')
        import cv2, torch, torchvision, sklearn, PIL
        from torch import nn
        from torch.utils.data import Dataset, DataLoader
        from torchvision import transforms, models
        import preprocess_original as prep
        import locked_functions as L
        import importlib
        assert Path(prep.__file__).resolve()==(root/'preprocess_original.py').resolve()
        assert Path(L.__file__).resolve()==(root/'locked_functions.py').resolve()
        importlib.reload(prep)
        importlib.reload(L)  # Không giữ wrapper của lần chạy trước trong cùng kernel.
        env=dict(torch=str(torch.__version__),torchvision=str(torchvision.__version__),numpy=np.__version__,
                 pandas=pd.__version__,sklearn=sklearn.__version__,cv2=cv2.__version__,pillow=PIL.__version__,
                 gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')
        audit['environment']=env;audit['python']=sys.version;audit['platform']=platform.platform()
        for k,v in lock['environment'].items():assert env[k]==v,f'Environment {k}: {env[k]} != {v}'
        device=torch.device('cuda')
        protocol=dict(task='P10_R50_EXTENSION',version='1.1',method=method,control='T02B_D4_R50',
                      cfg=cfg,params=prep.PARAMS[method],source_hashes=hashes,environment=env,
                      preprocessing_stage='P01/P02/P10 use original size; P03..P09 after bilinear 224; before D4 and normalization',
                      applied_splits=['train','val'],test_previously_seen=True,new_test_access=False,
                      train_from='ImageNet V1 fresh same seed42 initialization, NOT T02B checkpoint',
                      primary_metric='validation macro-F1',selection='exploratory; not multiplicity-adjusted',
                      augmentation=lock['candidate_augmentation'])
        dump_json(out/'candidate_protocol_lock.json',protocol)
        normalize=transforms.Compose([transforms.ToTensor(),transforms.Normalize([.485,.456,.406],[.229,.224,.225])])
        # Các hàm gốc tra biến toàn cục trong module L. Không exec notebook cũ.
        L.__dict__.update(np=np,pd=pd,plt=plt,torch=torch,nn=nn,models=models,Image=Image,
                         random=random,hashlib=hashlib,json=json,time=time,shutil=shutil,gc=gc,
                         accuracy_score=accuracy_score,balanced_accuracy_score=balanced_accuracy_score,
                         f1_score=f1_score,classification_report=classification_report,confusion_matrix=confusion_matrix,
                         Path=Path,Dataset=Dataset,DataLoader=DataLoader,SEED=42,IMG_SIZE=224,BATCH_SIZE=32,
                         EPOCHS=16,PATIENCE=4,NUM_WORKERS=2,LR=1e-4,WEIGHT_DECAY=1e-4,DEVICE=device,
                         LABELS=labels,label_to_id={v:i for i,v in enumerate(labels)},parts=parts,normalize=normalize,
                         OUT=out,resume=None,LOCK_SHA=sha_file(out/'candidate_protocol_lock.json'),
                         METHODS_T02=('T02A_HV_R50','T02B_D4_R50'),sha_file=sha_file,dump_json=dump_json)
        class CandidateDataset(Dataset):
            def __init__(self,data,train=False,preprocess_method=None):
                self.data=data.reset_index(drop=True);self.train=train;self.preprocess_method=preprocess_method or method
            def __len__(self):return len(self.data)
            def __getitem__(self,index):
                row=self.data.iloc[index]
                with Image.open(row.path) as im:rgb,_=prep.process(im,self.preprocess_method)
                if self.train:
                    code=int(torch.randint(8,()).item())
                    rgb=Image.fromarray(L.t02_geometry(np.asarray(rgb),'T02B_D4_R50',code))
                return normalize(rgb),int(row.label)
        def loader(data,unused,train=False):
            assert data.split.isin(['train','val']).all()
            return DataLoader(CandidateDataset(data,train),batch_size=32,shuffle=train,num_workers=2,
                              pin_memory=True,worker_init_fn=L.seed_worker,
                              generator=torch.Generator().manual_seed(42),drop_last=False)
        # Guard loss trước backward. Không thay công thức CE hoặc optimizer.
        class FiniteCE(nn.CrossEntropyLoss):
            def forward(self,x,y):
                assert torch.isfinite(x).all(),'Non-finite logits'
                value=super().forward(x,y)
                assert torch.isfinite(value).all(),'Non-finite loss'
                return value
        L.criterion=FiniteCE();L.make_loader=loader
        original_evaluate=L.evaluate
        def finite_evaluate(model,data_loader):
            ans=original_evaluate(model,data_loader)
            assert np.isfinite(ans[0]) and all(np.isfinite(v) for v in ans[1].values()) and np.isfinite(ans[4]).all()
            return ans
        L.evaluate=finite_evaluate
        original_build=L.build_model
        def checked_build():
            model=original_build();assert state_sha(model)==complete['initial_sha'],'Initialization differs from seed42'
            return model
        L.build_model=checked_build
        L.reset_seed();probe=L.build_model();del probe;gc.collect();torch.cuda.empty_cache()
        # Kiểm B00 của module tiền xử lý đúng resize nền T02B, không sử dụng nhánh hair trong lock.
        sample=parts['train'].groupby('label',sort=True).head(1)
        original_ds=L.T02Dataset(sample,'T02B_D4_R50',True)
        noop_ds=CandidateDataset(sample,True,'B00')
        for i in range(len(sample)):
            L.reset_seed();x,y=original_ds[i];after_original=torch.get_rng_state().clone()
            L.reset_seed();z,t=noop_ds[i];after_noop=torch.get_rng_state().clone()
            assert y==t and torch.equal(x,z) and torch.equal(after_original,after_noop),'No-op Dataset or D4 RNG differs'
        for row in sample.itertuples():
            with Image.open(row.path) as im:
                base=im.convert('RGB').resize((224,224),Image.Resampling.BILINEAR)
                got,_=prep.process(im,'B00')
            assert np.array_equal(base,got)
            py_state=random.getstate();np_state=np.random.get_state();torch_state=torch.get_rng_state().clone()
            with Image.open(row.path) as im:
                first,_=prep.process(im,method);second,_=prep.process(im,method)
            assert np.array_equal(first,second),'Non-deterministic transform'
            assert random.getstate()==py_state and torch.equal(torch_state,torch.get_rng_state())
            assert all(np.array_equal(a,b) for a,b in zip(np_state,np.random.get_state())),'Transform consumed NumPy RNG'
            for code in range(8):
                expected=np.rot90(np.asarray(base),code%4)
                if code>=4:expected=np.flip(expected,1)
                assert np.array_equal(L.t02_geometry(np.asarray(got),'T02B_D4_R50',code),expected)
        L.reset_seed();original_batch,original_y=next(iter(L.t02_loader(sample,'T02B_D4_R50',True)))
        noop_loader=DataLoader(CandidateDataset(sample,True,'B00'),batch_size=32,shuffle=True,num_workers=2,
                              pin_memory=True,worker_init_fn=L.seed_worker,
                              generator=torch.Generator().manual_seed(42),drop_last=False)
        L.reset_seed();noop_batch,noop_y=next(iter(noop_loader))
        assert torch.equal(original_y,noop_y) and torch.equal(original_batch,noop_batch),'Worker/no-op loader mismatch'
        del noop_loader,original_batch,original_y,noop_batch,noop_y
        # Smoke batch train thật gồm D4 và worker; không cập nhật tham số.
        L.reset_seed();batch,y=next(iter(loader(sample,method,True)))
        assert batch.shape==(8,3,224,224) and torch.isfinite(batch).all()
        L.reset_seed();probe=L.build_model();probe.train()
        loss=L.criterion(probe(batch.to(device)),y.to(device));loss.backward()
        assert all(torch.isfinite(p.grad).all() for p in probe.parameters() if p.grad is not None)
        del probe,batch,y,loss;gc.collect();torch.cuda.empty_cache();L.reset_seed()
        audit['checks'].append('init_resize_D4_loader_forward_backward_finite')
        # Audit từng ảnh và chọn gallery chỉ từ train; không điều chỉnh tham số từ thống kê.
        rows=[]
        for split,data in parts.items():
            for row in data.itertuples():
                with Image.open(row.path) as im:
                    base,_=prep.process(im,'B00');a,info=prep.process(im,method)
                a=np.asarray(a);b=np.asarray(base)
                assert a.shape==(224,224,3) and a.dtype==np.uint8 and np.isfinite(a).all()
                record={k:v for k,v in info.items() if k!='mask'}
                record.update(image=row.image,group=row.group,label_name=row.label_name,split=split,
                              file_sha256=row.file_sha256,changed_fraction=float(np.any(a!=b,axis=2).mean()),
                              mean_abs_change=float(np.abs(a.astype(float)-b).mean()))
                rows.append(record)
        qa=pd.DataFrame(rows);qa.to_csv(out/'transform_audit.csv',index=False)
        qa.groupby(['split','label_name'])[['fallback','changed_fraction','mean_abs_change']].mean().to_csv(out/'transform_summary.csv')
        train=qa[qa.split.eq('train')];rng=np.random.default_rng(42);chosen=[];used=set()
        for label in labels:
            pool=train[train.label_name.eq(label)].sort_values('image')
            for idx in rng.permutation(len(pool)):
                r=pool.iloc[int(idx)]
                if r.group not in used:chosen.append(r.image);used.add(r.group);break
        for r in train.sort_values(['mean_abs_change','image'],ascending=[False,True]).itertuples():
            if r.group not in used:chosen.append(r.image);used.add(r.group)
            if len(chosen)==12:break
        assert len(chosen)==12
        review=qa.set_index('image').loc[chosen].reset_index()[['image','group','label_name','split','file_sha256']]
        review['method']=method;review['preprocess_sha']=sha_file(root/'preprocess_original.py')
        review['decision']='pending';review['comment']='';review['reviewer']='';review['review_date']=''
        review.to_csv(out/'visual_review_template.csv',index=False)
        for page in range(3):
            fig,axes=plt.subplots(4,4,figsize=(13,12))
            for axrow,image in zip(axes,chosen[page*4:page*4+4]):
                row=parts['train'].set_index('image').loc[image]
                with Image.open(row.path) as im:
                    original=im.convert('RGB');base,_=prep.process(original,'B00');candidate,info=prep.process(original,method)
                overlay=original.copy()
                if info.get('crop_box') is not None:
                    ImageDraw.Draw(overlay).rectangle(tuple(info['crop_box']),outline='red',width=max(2,original.width//150))
                elif info.get('mask') is not None:
                    overlay=np.asarray(base).copy();overlay[np.asarray(info['mask'])>0]=[255,0,0]
                    overlay=Image.fromarray(overlay)
                for ax,pic,title in zip(axrow,[original,base,candidate,overlay],['Original','T02B resize',method,'Mask/box proposal']):
                    ax.imshow(pic);ax.set_title(title+'\n'+image,fontsize=8);ax.axis('off')
            fig.tight_layout();fig.savefig(out/f'gallery_{page+1}.png',dpi=110);plt.close(fig)
        audit['checks'].append('all_train_val_transforms_and_train_only_gallery')
        audit['status']='TECHNICAL_PREFLIGHT_PASS_VISUAL_PENDING'
        if not run_train:return {'output':str(out),'status':audit['status']}
        assert review_csv is not None,'Cần CSV quan sát ảnh thật; chưa được tự ghi PASS'
        review_path=Path(review_csv)
        done=pd.read_csv(review_path,keep_default_na=False).set_index('image').loc[chosen].reset_index()
        assert len(pd.read_csv(review_path))==12 and done.image.is_unique
        for col in ['image','group','label_name','split','file_sha256','method','preprocess_sha']:
            assert done[col].tolist()==review[col].tolist(),col
        assert done.decision.eq('accept_exploratory').all(),'Có ảnh chưa chấp nhận cho thử nghiệm'
        for col in ['comment','reviewer','review_date']:assert done[col].astype(str).str.strip().ne('').all(),col
        shutil.copyfile(review_path,out/'visual_review_used.csv')
        # P10 được phép thử trong protocol mới này sau review; mask heuristic KHÔNG phải mask tổn thương chuẩn.
        L.reset_seed();audit['train']='STARTED';audit['status']='TRAINING'
        result=L.train_experiment(method)
        assert result['initial_sha']==complete['initial_sha']
        folder=out/method
        pred=checked_predictions(pd.read_csv(folder/'val_predictions.csv'),parts['val'],labels)
        observed=L.metrics(pred.true_label.map(L.label_to_id),pred.pred_label.map(L.label_to_id))
        for k,v in observed.items():assert abs(v-result[k])<=1e-8,k
        history=pd.read_csv(folder/'history.csv');best=-1.;wait=0;best_epoch=None
        assert np.isfinite(history.select_dtypes('number')).all().all()
        for row in history.itertuples():
            assert wait<4
            if row.macro_f1>best+1e-5:best=row.macro_f1;best_epoch=row.epoch;wait=0
            else:wait+=1
            expected_lr=1e-4*(1+np.cos(np.pi*(row.epoch-1)/16))/2
            assert abs(row.lr-expected_lr)<1e-12
        assert best_epoch==result['best_epoch'] and len(history)==result['completed_epochs']
        assert len(history)==16 or wait==4
        assert sha_file(folder/'best_resnet50.pt')==result['checkpoint_sha']
        ci,draws,support=L.t02_bootstrap({'T02B':control,method:pred})
        assert support.n_groups.sum()==1392
        ci.to_csv(out/'comparison.csv',index=False);draws.to_csv(out/'bootstrap_draws.csv',index=False);support.to_csv(out/'bootstrap_group_support.csv',index=False)
        row=ci.iloc[0]
        conclusion=('candidate_for_fresh_seed_confirmation' if row.delta_macro_f1_pp>=1 and row.ci95_low_pp>0 else
                    'no_improvement_in_this_run' if row.delta_macro_f1_pp<=0 else 'inconclusive')
        dump_json(out/'decision.json',dict(conclusion=conclusion,**row.to_dict(),multiple_comparisons='exploratory unadjusted CI; not proof of superiority',test='NOT_RUN'))
        audit['train']='COMPLETED';audit['status']='TRAIN_COMPLETED_VALIDATION_CHECKED'
        return {'output':str(out),'status':audit['status'],'result':result}
    except Exception as exc:
        audit['status']='STOP_REPORT_TO_CHA';audit['exception']=repr(exc)
        (out/'STOP_REPORT_TO_CHA.md').write_text(str(exc)+'\nGiữ nguyên bằng chứng. Không nới kiểm tra.',encoding='utf-8')
        raise
    finally:
        dump_json(out/'audit.json',audit)
        files=sorted(p for p in out.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt')
        (out/'SHA256SUMS.txt').write_text(''.join(f'{sha_file(p)}  {p.relative_to(out)}\n' for p in files))
        with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for p in out.rglob('*'):
                if p.is_file():z.write(p,p.relative_to(out))
        print('FULL output và ZIP:',out,out.with_suffix('.zip'))
