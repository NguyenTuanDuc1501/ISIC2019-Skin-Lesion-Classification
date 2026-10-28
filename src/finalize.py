from pathlib import Path
import json,hashlib,ast,zipfile,csv,shutil,argparse
import numpy as np,pandas as pd
parser=argparse.ArgumentParser();parser.add_argument('--root',default='/data/r02final');args=parser.parse_args()
R=Path(args.root)
for name in ['trained_output','preflight','r01','l01_addendum']:
    if not (R/'x'/name).exists():
        with zipfile.ZipFile(R/'raw'/('trained_output.zip' if name=='trained_output' else name+'.zip')) as archive:archive.extractall(R/'x'/name)
ROOT=R/'x/trained_output/R02_RECOVERY_v1_1_preflight02';PRE=R/'x/preflight/R02_RECOVERY_v1_1_preflight02';O=R/'deliverables/R02_RESULT_FINALIZE_v1_0';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();checks=[];tol=1e-8
LABELS=['MEL','NV','BCC','AK','BKL','DF','VASC','SCC'];lid={l:i for i,l in enumerate(LABELS)}
def ck(name,ok,detail=''):
 checks.append(dict(check=name,status='PASS' if bool(ok) else 'FAIL',detail=detail));assert ok,name+' '+str(detail)
def j(p):return json.loads(Path(p).read_text())
def rel(p):return str(Path(p).relative_to(R))
def ck_close(name,a,b,eps=tol):ck(name,np.allclose(np.asarray(a,float),np.asarray(b,float),atol=eps,rtol=0))
def fn(text,name):
 n=next(n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name);return ''.join(text.splitlines(True)[n.lineno-1:n.end_lineno])
full_count=0
for root in [ROOT,PRE]:
 lines=(root/'SHA256SUMS.txt').read_text().splitlines()
 for line in lines:
  h,n=line.split('  ',1);ck('checksum:'+rel(root/n),sha(root/n)==h)
 if root==ROOT:full_count=len(lines)
reportzip=R/'x/trained_output/R02_RECOVERY_v1_1_preflight02_reports.zip';reports=zipfile.ZipFile(reportzip);report_count=0
for line in reports.read('SHA256SUMS.txt').decode().splitlines():
 h,n=line.split('  ',1);ck('reports_checksum:'+n,hashlib.sha256(reports.read(n)).hexdigest()==h and (ROOT/n).read_bytes()==reports.read(n));report_count+=1
ck('reports90_full94',report_count==90 and full_count==94)
# Inputs R01 and L01 are version-locked; no numbers copied from dialogue.
ck('R01_hash',sha(R/'raw/r01.zip')=='bb33c7116db7e2f8953f8c5888f00679530c52584d03c779cec72463a27031c9')
ck('L01_addendum_hash',sha(R/'raw/l01_addendum.zip')=='f67c877306cb305ee38c63ac88f9d8f5b4188a41a136abe4594d69ae96e3d687')
for scope in ['r01','l01_addendum']:
 ch=next((R/'x'/scope).rglob('SHA256SUMS.txt'));base=ch.parent
 for line in ch.read_text().splitlines():
  h,n=line.split('  ',1);ck('package_checksum:'+scope+':'+n,sha(base/n)==h)
source=(ROOT/'implementation.py').read_text();source_sha=sha(ROOT/'implementation.py');ck('recovery_source_pinned',source_sha=='f29ef58e695da9c55f267bdfb94f9d9871fd5c0f0ef2918d359fb1b5bd0f4863')
notebook=j(R/'raw/trained.ipynb');embedded=[];flags={};errors=[]
for i,c in enumerate(notebook['cells']):
 if c['cell_type']=='code':
  for n in ast.parse(''.join(c['source'])).body:
   if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant):
    if isinstance(n.value.value,str) and len(n.value.value)>20000:embedded.append(n.value.value)
    if isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['RUN_TRAIN','RUN_TEST']:flags[n.targets[0].id]=n.value.value
  errors += [x for x in c.get('outputs',[]) if x.get('output_type')=='error']
ck('notebook_embedded_source_equals_executed',embedded==[source]);ck('notebook_flags_train_true_test_false',flags==dict(RUN_TRAIN=True,RUN_TEST=False));ck('notebook_no_error_outputs',not errors)
ck('external_executed_source_equal',(R/'x/trained_output/r02_recovery_v1_1_implementation.py').read_text()==source)
oldsrc=(ROOT/'history/R02_v1_0/implementation.py').read_text();old_sha=sha(ROOT/'history/R02_v1_0/implementation.py');ck('historical_source_pinned',old_sha=='6fbcb1dea193248cd2b6e4346dc2b9dec1cbbfd610334843ebb08bdd721f9c18')
for name in ['train_experiment','evaluate','R02Dataset','make_loader','seed_worker','reset_seed','build_model','finite','t02_geometry','t02_bootstrap','summarize_new_seeds','export_evaluation']:ck('algorithm_unchanged:'+name,fn(source,name)==fn(oldsrc,name))
expected_old=j(ROOT/'history/R02_v1_0/EXPECTED_OLD_FILES.json');old_B00_count=0
for n,h in expected_old.items():
 if n.startswith('seed_43/'):
  ck('reused_hash_matches_history:'+n,sha(ROOT/n)==h)
  if n in reports.namelist():ck('reused_reports_hash_history:'+n,hashlib.sha256(reports.read(n)).hexdigest()==h);old_B00_count+=1
ck('old_STOP_retained',j(ROOT/'history/R02_v1_0/STOP.json')['type']=='TypeError' and sha(ROOT/'history/R02_v1_0/STOP.json')==expected_old['STOP.json'])
dispatch=j(ROOT/'recovery_dispatch.json')['events'];expected_events=[dict(seed=s,method=m,action=a) for s,m,a in [(43,'B00_R50','REUSE_VERIFIED'),(43,'T02B_D4_R50','TRAIN_FRESH'),(44,'B00_R50','TRAIN_FRESH'),(44,'T02B_D4_R50','TRAIN_FRESH')]];ck('one_REUSE_three_TRAIN_FRESH',dispatch==expected_events)
ck('current_complete',j(ROOT/'CURRENT_STATUS.json')==dict(status='COMPLETE_FOUR_RUNS',reused=1,trained_fresh=3,seed42_retrained=False))
ck('preflight_not_train_only',j(PRE/'CURRENT_STATUS.json')['status']=='PREFLIGHT_ONLY_THREE_RUNS_NOT_RUN')
ck('preflight_source_equal',sha(PRE/'implementation.py')==source_sha)
manifest_path=ROOT/'split_manifest.csv';manifest=pd.read_csv(manifest_path,keep_default_na=False);ck('split_sha_locked',sha(manifest_path)=='38a5a9aca907d56685bddfcd874e162d8bf2c141a7247025410eeeee6bcf522a')
ck('manifest_25327_unique',len(manifest)==25327 and manifest.image.is_unique)
for col in ['image','group','file_sha256']:ck('no_split_leak:'+col,manifest.groupby(col).split.nunique().max()==1)
val=manifest[manifest.split.eq('val')].sort_values('image').reset_index(drop=True);ck('validation2539groups1392',len(val)==2539 and val.group.nunique()==1392)
ck('labels_encode_match',np.array_equal(manifest.label,manifest.label_name.map(lid)))
def conf(y,p,labels=range(8)):
 a=np.zeros((8,8),int);np.add.at(a,(np.asarray(y,int),np.asarray(p,int)),1);return a
# Frozen function only: never execute notebook training code.
bootstrap_code=fn(source,'t02_bootstrap');ns=dict(np=np,pd=pd,LABELS=LABELS,label_to_id=lid,confusion_matrix=conf);exec(compile(bootstrap_code,'bootstrap_locked.py','exec'),ns)
(S:=O/'src').mkdir(exist_ok=True);(S/'bootstrap_locked.py').write_text(bootstrap_code)
allruns=[];perclass=[];cms=[];checkpoints=[];preds={};configs={};histories=[]
for seed,method in [(43,'B00_R50'),(43,'T02B_D4_R50'),(44,'B00_R50'),(44,'T02B_D4_R50')]:
 folder=ROOT/f'seed_{seed}'/method;tag=f'{method}/{seed}';complete=j(folder/'complete.json');lockpath=ROOT/f'seed_{seed}'/f'{method}_protocol_lock.json';lock=j(lockpath);configs[(seed,method)]=lock
 ck('lock_hash:'+tag,complete['lock_sha']==sha(lockpath));ck('config_bytes:'+tag,(folder/'configuration.json').read_bytes()==lockpath.read_bytes())
 codehash=sha(folder/'source.py');ck('source_lock:'+tag,codehash==lock['source_sha']==(old_sha if (seed,method)==(43,'B00_R50') else source_sha))
 pt=folder/'best_resnet50.pt';direct=sha(pt) if pt.exists() else None
 if direct:ck('checkpoint_direct_bytes:'+tag,direct==complete['checkpoint_sha'])
 checkpoints.append(dict(seed=seed,method=method,checkpoint_source=rel(pt),sha_claimed=complete['checkpoint_sha'],sha_direct=direct,direct_bytes_verified=direct is not None,verification='BYTE_SHA256_ONLY_NO_MODEL_REINFERENCE'))
 p=pd.read_csv(folder/'val_predictions.csv',keep_default_na=False).sort_values('image').reset_index(drop=True)
 ck('prediction1to1:'+tag,len(p)==2539 and p.image.is_unique)
 for a,b in [('image','image'),('group','group'),('file_sha256','file_sha256'),('true_label','label_name')]:ck('prediction_manifest:'+tag+':'+a,np.array_equal(p[a],val[b]))
 ck('prediction_labels:'+tag,p.pred_label.isin(LABELS).all())
 probs=p[['p_'+l for l in LABELS]].to_numpy();ck('probabilities:'+tag,np.isfinite(probs).all() and (probs>=0).all() and (probs<=1).all() and np.allclose(probs.sum(1),1,atol=1e-5) and np.array_equal(probs.argmax(1),p.pred_label.map(lid)))
 a=conf(p.true_label.map(lid),p.pred_label.map(lid));tp=np.diag(a);support=a.sum(1);predsupport=a.sum(0);precision=np.divide(tp,predsupport,out=np.zeros(8),where=predsupport>0);recall=tp/support;f1=np.divide(2*tp,support+predsupport,out=np.zeros(8),where=support+predsupport>0)
 score=dict(accuracy=float(tp.sum()/a.sum()),balanced_accuracy=float(recall.mean()),macro_f1=float(f1.mean()))
 for k,x in score.items():ck_close('complete_metrics:'+tag+':'+k,x,complete[k]);ck_close('val_metrics:'+tag+':'+k,x,j(folder/'val_metrics.json')[k])
 direct_f1=np.mean([2*((p.true_label==l)&(p.pred_label==l)).sum()/((p.true_label==l).sum()+(p.pred_label==l).sum()) for l in LABELS]);ck_close('independent_F1:'+tag,direct_f1,score['macro_f1']);ck_close('independent_accuracy:'+tag,p.true_label.eq(p.pred_label).mean(),score['accuracy'])
 ck('confusion:'+tag,np.array_equal(a,pd.read_csv(folder/'val_confusion.csv',index_col=0).to_numpy()))
 stored=pd.read_csv(folder/'val_per_class.csv',index_col=0).reindex(LABELS);ck_close('perclass:'+tag,np.array([precision,recall,f1,support]).T,stored[['precision','recall','f1-score','support']])
 for i,l in enumerate(LABELS):
  perclass.append(dict(seed=seed,method=method,label=l,support=int(support[i]),precision=precision[i],recall=recall[i],f1=f1[i],source=rel(folder/'val_predictions.csv')))
  for z,predlabel in enumerate(LABELS):cms.append(dict(seed=seed,method=method,true_label=l,pred_label=predlabel,n=int(a[i,z]),source=rel(folder/'val_predictions.csv')))
 h=pd.read_csv(folder/'history.csv');ck('history_finite_contiguous:'+tag,len(h)<=16 and np.isfinite(h.to_numpy()).all() and h.epoch.tolist()==list(range(1,len(h)+1)))
 ck_close('LR_cosine_before_scheduler:'+tag,h.lr,1e-4*(1+np.cos(np.pi*(h.epoch.to_numpy()-1)/16))/2,1e-14)
 best=-1.;wait=0;best_epoch=0
 for row in h.itertuples():
  if row.macro_f1>best+1e-5:best=row.macro_f1;best_epoch=row.epoch;wait=0
  else:wait+=1
  ck('patience_no_extra:'+tag+':'+str(row.epoch),not(wait>=4 and row.epoch<len(h)))
 ck('best_stop:'+tag,best_epoch==complete['best_epoch'] and len(h)==complete['completed_epochs'] and (len(h)==16 or wait==4));ck_close('best_metric_matches_checkpoint_predictions:'+tag,best,score['macro_f1'])
 ck('init_lock_audit:'+tag,complete['initial_sha']==lock['expected_initial_sha']==j(folder/'initial_audit.json')['initial_sha'])
 start=j(folder/'run_start.json');ck('fresh_optimizer_loader_seed:'+tag,start['fresh_optimizer'] and start['fresh_loaders'] and start['seed']==start['train_generator_seed']==start['val_generator_seed']==seed)
 ck('acceptance_audit:'+tag,j(folder/'acceptance_audit.json')==dict(status='PASS_COMPLETED_RUN',method=method,seed=seed,checkpoint_hash_checked=True,metrics_recomputed=True,history_checked=True))
 ck('no_test_AMP_TTA:'+tag,lock['test_used'] is False and lock['amp'] is False and lock['tta'] is False and lock['fresh_ImageNet'] is True)
 preds[(seed,method)]=p
 allruns.append(dict(seed=seed,method=method,**score,best_epoch=best_epoch,completed_epochs=len(h),seconds=complete['seconds'],initial_sha=complete['initial_sha'],checkpoint_sha_claimed=complete['checkpoint_sha'],checkpoint_sha_direct=direct,checkpoint_bytes_verified=direct is not None,source=rel(folder/'val_predictions.csv'),complete_source=rel(folder/'complete.json'),config_source=rel(lockpath),history_source=rel(folder/'history.csv'),source_sha=codehash,phase='confirmation_same_validation',action='REUSE_VERIFIED' if (seed,method)==(43,'B00_R50') else 'TRAIN_FRESH'))
 histories.extend([dict(seed=seed,method=method,**row,source=rel(folder/'history.csv')) for row in h.to_dict('records')])
run=pd.DataFrame(allruns);pc=pd.DataFrame(perclass);run.to_csv(O/'SEED_RESULTS.csv',index=False);pc.to_csv(O/'PER_CLASS_RESULTS.csv',index=False);pd.DataFrame(cms).to_csv(O/'CONFUSION_MATRICES_LONG.csv',index=False);pd.DataFrame(checkpoints).to_csv(O/'CHECKPOINT_VERIFICATION.csv',index=False);pd.DataFrame(histories).to_csv(O/'HISTORY_RECONCILED.csv',index=False)
for metric in ['accuracy','balanced_accuracy','macro_f1']:
 orig=pd.read_csv(ROOT/'NEW_SEEDS_RUNS.csv');ck_close('run_table_source:'+metric,run[metric],orig[metric])
base_config=configs[(43,'B00_R50')]['baseline_config'].copy();base_config.pop('seed')
for (seed,method),lock in configs.items():
 b=lock['baseline_config'].copy();ck('config_seed:'+str((seed,method)),b.pop('seed')==seed and lock['seed']==seed);ck('full_scientific_baseline_same:'+str((seed,method)),b==base_config)
 ck('augmentation_only_expected:'+str((seed,method)),lock['augmentation']==('none' if method=='B00_R50' else 'uniform rot90(code%4), HFlip if code>=4; torch.randint(8)'))
ck('science_fixed_fields',all(base_config[k]==v for k,v in dict(labels=LABELS,size=224,batch=32,epochs=16,patience=4,workers=2,lr=1e-4,weight_decay=1e-4,model='resnet50',weights='IMAGENET1K_V1',loss='CrossEntropyLoss(weight=None,label_smoothing=0)',sampler='shuffle, no weighting',amp=False).items()))
paired=[];stats=[];class_delta=[]
cha={43:[.5732305489713939,.5779448080836374,.4714259112243435,-3.799049843839399,5.108781197733394],44:[.5608092024243576,.599743040712567,3.89338382882094,-.8558037750225558,8.646323902295924]}
for seed in [43,44]:
 rr=run[run.seed.eq(seed)].set_index('method');ck('pair_init_same:'+str(seed),rr.loc['B00_R50','initial_sha']==rr.loc['T02B_D4_R50','initial_sha'])
 ci,draws,support=ns['t02_bootstrap']({'B00_R50':preds[(seed,'B00_R50')],'T02B_D4_R50':preds[(seed,'T02B_D4_R50')]},n_boot=2000,seed=20261007)
 saved_ci=pd.read_csv(ROOT/f'seed_{seed}_bootstrap_delta.csv');ck_close('bootstrap_CI:'+str(seed),ci[['delta_macro_f1_pp','ci95_low_pp','ci95_high_pp']],saved_ci[['delta_macro_f1_pp','ci95_low_pp','ci95_high_pp']]);ck_close('bootstrap_all_draws:'+str(seed),draws,pd.read_csv(ROOT/f'seed_{seed}_bootstrap_draws.csv'),1e-12)
 pd.testing.assert_frame_equal(support,pd.read_csv(ROOT/f'seed_{seed}_group_support.csv'));ck('group_support:'+str(seed),len(support)==8 and support.n_groups.sum()==1392)
 row=ci.iloc[0].to_dict();row.update(seed=seed,phase='confirmation_same_validation',B00_macro_f1=rr.loc['B00_R50','macro_f1'],T02B_macro_f1=rr.loc['T02B_D4_R50','macro_f1'],source_B00=rr.loc['B00_R50','source'],source_T02B=rr.loc['T02B_D4_R50','source'],bootstrap_source=rel(ROOT/f'seed_{seed}_bootstrap_draws.csv'))
 for metric in ['accuracy','balanced_accuracy']:row['delta_'+metric+'_pp']=100*(rr.loc['T02B_D4_R50',metric]-rr.loc['B00_R50',metric])
 paired.append(row);ck_close('CHA_numbers_comparison:'+str(seed),[row['B00_macro_f1'],row['T02B_macro_f1'],row['delta_macro_f1_pp'],row['ci95_low_pp'],row['ci95_high_pp']],cha[seed])
 draws.to_csv(O/f'BOOTSTRAP_DRAWS_seed{seed}.csv',index=False);support.to_csv(O/f'GROUP_SUPPORT_seed{seed}.csv',index=False)
 for label in LABELS:
  x=pc[pc.seed.eq(seed)&pc.label.eq(label)].set_index('method');a=preds[(seed,'B00_R50')];b=preds[(seed,'T02B_D4_R50')];mask=a.true_label.eq(label);correct_a=a.true_label.eq(a.pred_label);correct_b=b.true_label.eq(b.pred_label)
  class_delta.append(dict(seed=seed,label=label,support=int(x.loc['B00_R50','support']),delta_precision_pp=100*(x.loc['T02B_D4_R50','precision']-x.loc['B00_R50','precision']),delta_recall_pp=100*(x.loc['T02B_D4_R50','recall']-x.loc['B00_R50','recall']),delta_f1_pp=100*(x.loc['T02B_D4_R50','f1']-x.loc['B00_R50','f1']),contribution_macro_pp=100*(x.loc['T02B_D4_R50','f1']-x.loc['B00_R50','f1'])/8,wrong_to_right=int((mask&~correct_a&correct_b).sum()),right_to_wrong=int((mask&correct_a&~correct_b).sum()),source_B00=rel(ROOT/f'seed_{seed}/B00_R50/val_predictions.csv'),source_T02B=rel(ROOT/f'seed_{seed}/T02B_D4_R50/val_predictions.csv')))
for metric in ['accuracy','balanced_accuracy','macro_f1']:
 pivot=run.pivot(index='seed',columns='method',values=metric);series={'B00_R50':pivot.B00_R50,'T02B_D4_R50':pivot.T02B_D4_R50,'T02B_minus_B00':pivot.T02B_D4_R50-pivot.B00_R50}
 for method,vals in series.items():
  stats.append(dict(method=method,metric=metric,n_seeds=2,seeds='43,44',mean=float(vals.mean()),sample_SD=float(vals.std(ddof=1)),mean_percent_or_pp=float(100*vals.mean()),sample_SD_pp=float(100*vals.std(ddof=1)),source='SEED_RESULTS.csv; matched training seed',scope='descriptive only, no CI across training seeds'))
paired=pd.DataFrame(paired);stat=pd.DataFrame(stats);paired.to_csv(O/'PAIRED_DELTA_BY_SEED.csv',index=False);stat.to_csv(O/'NEW_SEEDS_MEAN_SD.csv',index=False);pd.DataFrame(class_delta).to_csv(O/'PER_CLASS_PAIRED_DELTA.csv',index=False)
original_stats=pd.read_csv(ROOT/'NEW_SEEDS_MEAN_SD.csv');ck_close('mean_SD_source',stat[['mean','sample_SD']],original_stats[['mean','sample_SD']]);delta_stat=stat[(stat.method=='T02B_minus_B00')&stat.metric.eq('macro_f1')].iloc[0];ck_close('CHA_mean_SD',[delta_stat.mean_percent_or_pp,delta_stat.sample_SD_pp],[2.1824048700226417,2.4196896484675504])
# Historical seed42: use actual supplied locked package, not chat numbers.
lpath=next((R/'x/l01_addendum').rglob('EXPERIMENT_TABLE.csv'));historical=pd.read_csv(lpath);hist42=pd.read_csv(ROOT/'HISTORICAL_SEED42.csv')
for method,alias in [('B00_R50','B00_R50_CE'),('T02B_D4_R50','T02B_D4_R50')]:
 x=hist42[hist42.method.eq(method)].iloc[0];z=historical[historical.method.eq(alias)].iloc[0]
 ck_close('historical42_source_consistency:'+method,[x.accuracy,x.balanced_accuracy,x.macro_f1],[z.accuracy,z.balanced_accuracy,z.macro_f1])
 hist42.loc[hist42.method.eq(method),'source']=rel(ROOT/'HISTORICAL_SEED42.csv')+'; '+rel(lpath)
hist42['phase']='exploratory_historical';hist42.to_csv(O/'HISTORICAL_SEED42.csv',index=False)
# Preserve seed42 rows/provenance and append four confirmations with explicitly different comparator.
historical['phase']='exploratory_historical';historical['comparator']='T02B_D4_R50_seed42';historical['carried_from']=rel(lpath);historical['verification_this_finalize']='CARRIED_FROM_HASH_VERIFIED_R01_L01; NOT_RECOMPUTED_HISTORICAL_RAW_PREDICTIONS';new=[]
for row in allruns:
 record=dict(row);record.update(n_val=2539,n_groups=1392,verification='RECOMPUTED_MATCH_1e-8_CHECKPOINT_BYTES_HASHED',predictions_source=row['source'],predictions_sha256=sha(R/row['source']),complete_sha256=sha(R/row['complete_source']),checkpoint_bytes_verified=True,comparator='B00_R50_same_seed',delta_vs_T02B_pp=None,CI95_low_pp=None,CI95_high_pp=None,carried_from='',verification_this_finalize='DIRECT_RECOMPUTED')
 if row['method']=='T02B_D4_R50':
  z=paired[paired.seed.eq(row['seed'])].iloc[0];record.update(delta_vs_B00_same_seed_pp=z.delta_macro_f1_pp,CI95_low_pp=z.ci95_low_pp,CI95_high_pp=z.ci95_high_pp)
 else:record['delta_vs_B00_same_seed_pp']=0.
 new.append(record)
pd.concat([historical,pd.DataFrame(new)],ignore_index=True).to_csv(O/'EXPERIMENT_TABLE.csv',index=False)
# Every result points to actual input; all files inventoried with source role and verification scope.
original_names={'trained.ipynb':'r02-recovery-v1-1 (3).ipynb','trained_output.zip':'R02_RECOVERY_v1_1_preflight02_Bat_Train.zip','preflight.zip':'R02_RECOVERY_v1_1_preflight02_Chua _Train.zip','r01.zip':'R01_EXPERIMENT_SYNTHESIS_v1_0_deliverables.zip','l01_addendum.zip':'R01_L01_ADDENDUM_v1_1.zip'}
inventory=[]
for p in (R/'raw').iterdir():inventory.append(dict(file=rel(p),original_name=original_names[p.name],sha256=sha(p),bytes=p.stat().st_size,role='immutable input attachment',verification='ACTUAL_HASH_CRC_IF_ZIP; components checked separately'))
for p in sorted((R/'x').rglob('*')):
 if p.is_file():inventory.append(dict(file=rel(p),original_name='',sha256=sha(p),bytes=p.stat().st_size,role='source component',verification='ACTUAL_HASH; see AUDIT.json for recomputation scope'))
pd.DataFrame(inventory).to_csv(O/'INPUT_INVENTORY.csv',index=False)
copy=O/'source_evidence';copy.mkdir(exist_ok=True)
for name in ['CURRENT_STATUS.json','recovery_dispatch.json','recovery_audit.json','preflight_audit.json','RECOVERY_PROTOCOL.json']:(copy/name).write_bytes((ROOT/name).read_bytes())
(copy/'HISTORICAL_STOP.json').write_bytes((ROOT/'history/R02_v1_0/STOP.json').read_bytes())
ck('seed43_accuracy_reversal',float(paired[paired.seed.eq(43)].delta_accuracy_pp.iloc[0])<0 and float(paired[paired.seed.eq(43)].delta_balanced_accuracy_pp.iloc[0])>0)
ck('both_new_CIs_contain_zero',paired.contains_zero.all());ck('both_new_macro_deltas_positive',paired.delta_macro_f1_pp.gt(0).all())
evidence=dict(task='R02_RESULT_FINALIZE',version='1.0',runs=allruns,paired=paired.to_dict('records'),stats=stats,historical_seed42=hist42.to_dict('records'),checkpoint_verification=checkpoints,source_zip_sha=sha(R/'raw/trained_output.zip'),reports_zip_sha=sha(reportzip),full_checksums=full_count,report_checksums=report_count,reused_report_files_checked=old_B00_count,profile_findings=dict(grain='one validation prediction per image per fitted checkpoint; repeated validation across seeds NOT independent',unique_val_images=2539,unique_val_byte_hashes=2537,unique_val_groups=1392,duplicate_rows=0,resolution='Preserve frozen manifest; duplicate byte hashes are grouped inside split, never deduplicate or treat as independent per-image bootstrap units'),visual_plan=[dict(question='Macro-F1 B00 versus T02B within observed seed',grain='method x seed',population='same2539val,1392groups',unit='percent',finding='D4 higher observed macro-F1 at42,43,44;42 exploratory,43/44 confirmation sameval',derivation='macroF1 from confusion; multiply100 for display',disposition='chart',reason='requested comparison and variable gain byseed'),dict(question='Accuracy43 adverse direction',grain='method x trainingseed43',population='same2539val',unit='percentage points',finding='accuracy43 decreases while BA and macroF1 increase',derivation='100*(T02B-B00)',disposition='table and prose',reason='must not hide adverse result'),dict(question='Uncertainty',grain='paired cluster bootstrap withinseed',population='1392validationgroups',unit='percentage points',finding='both new CIs cross0; no crossseed CI',disposition='table',reason='exact bounds, no averaging endpoints')],limits=['No test evaluation','Only two new training seeds; same reused validation, not independent evaluation set','Checkpoint hashes verified directly, not GPU reinference','Historical seed42 metrics carried from actual hash-verified R01/L01 packages, not all raw historical runs recomputed here','Image bytes not reopened in finalize; image verification recorded in executed preflight audits'])
(O/'EVIDENCE.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2,default=lambda z:z.item() if isinstance(z,np.generic) else str(z)))
(O/'AUDIT.json').write_text(json.dumps(dict(status='PASS_LISTED_CHECKS',checks=checks,n_checks=len(checks),not_performed=evidence['limits']),ensure_ascii=False,indent=2))
# One chart, two methods, three categorical seeds, explicit exploratory vs confirmatory labels. No line implies temporal trajectory.
spec=dict(version=1,form='categorical-bars',title='Macro-F1 của T02B cao hơn B00 ở cả ba seed đã quan sát',aside='Seed42 thăm dò; seed43/44 xác nhận trên cùng validation',mode='grouped',labels=['42 · thăm dò','43 · xác nhận','44 · xác nhận'],axis=dict(zero=True,cap=100),colorMap={'B00':'blue','T02B — D4':'orange'},series=[dict(label='B00',valueKind='percent',role='base',data=[100*float(hist42[hist42.method.eq('B00_R50')].macro_f1.iloc[0])]+[100*float(run[run.seed.eq(s)&run.method.eq('B00_R50')].macro_f1.iloc[0]) for s in [43,44]]),dict(label='T02B — D4',valueKind='percent',role='subject',data=[100*float(hist42[hist42.method.eq('T02B_D4_R50')].macro_f1.iloc[0])]+[100*float(run[run.seed.eq(s)&run.method.eq('T02B_D4_R50')].macro_f1.iloc[0]) for s in [43,44]])])
(O/'charts').mkdir(exist_ok=True);(O/'charts/seed_comparison_spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2))
print('CHECKS',len(checks));print(run[['seed','method','accuracy','balanced_accuracy','macro_f1','best_epoch','completed_epochs']].to_string(index=False));print(paired[['seed','delta_macro_f1_pp','ci95_low_pp','ci95_high_pp','delta_accuracy_pp','delta_balanced_accuracy_pp']].to_string(index=False));print('CHECKPOINTS_DIRECT',sum(x['direct_bytes_verified'] for x in checkpoints));print('MEAN_DELTA',delta_stat.mean_percent_or_pp,'SD',delta_stat.sample_SD_pp)
