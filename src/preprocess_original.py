"""Deterministic experimental transforms. Not clinically validated. RGB uint8 -> PIL224.
P03..P09 deliberately act AFTER the same bilinear resize as B00.
Masks/boxes are algorithm proposals, not ground truth.
"""
import cv2
import numpy as np
from PIL import Image, ImageOps
SIZE=224
METHODS=['B00']+[f'P{i:02d}' for i in range(1,11)]
PARAMS={
'B00':{'size':224,'interpolation':'PIL_BILINEAR'},
'P01':{'fill':[124,116,104]},
'P02':{'black_max':12,'dark_fraction':0.99,'max_trim_fraction':0.15,'margin_fraction':0.02},
'P03':{'kernel':9,'blackhat_threshold':20,'max_mask_fraction':0.05,'inpaint_radius':2},
'P04':{'p':6,'valid_min':15,'valid_max':245,'gain_min':0.8,'gain_max':1.25},
'P05':{'clipLimit':1.5,'tileGridSize':[8,8]},
'P06':{'gamma':0.9},
'P07':{'d':5,'sigmaColor':20,'sigmaSpace':3},
'P08':{'value_min':250,'saturation_max':15,'max_component_pixels':50,'max_mask_fraction':0.01,'inpaint_radius':2},
'P09':{'sigma':35,'strength':0.25,'gain_min':0.8,'gain_max':1.25},
'P10':{'mask_size':224,'margin_fraction':0.2,'min_area':0.05,'max_area':0.8}}
def resize(im):return im.resize((SIZE,SIZE),Image.Resampling.BILINEAR)
def u8(a):return np.clip(np.rint(a),0,255).astype(np.uint8)
def process(im,method):
    if method not in METHODS:raise ValueError(method)
    im=im.convert('RGB'); base=resize(im);a=np.array(base);p=PARAMS.get(method,{})
    info={'method':method,'fallback':False,'reason':'','mask_fraction':0.0,'crop_box':None,'mask':None,'padding_fraction':0.0}
    if method=='B00':return base,info
    if method=='P01':
        fitted=ImageOps.contain(im,(SIZE,SIZE),Image.Resampling.BILINEAR)
        out=Image.new('RGB',(SIZE,SIZE),tuple(p['fill']));out.paste(fitted,((SIZE-fitted.width)//2,(SIZE-fitted.height)//2))
        info['padding_fraction']=1-fitted.width*fitted.height/SIZE**2
        return out,info
    if method=='P02':
        # Inspect dark strips on a <=512 thumbnail, map proposed bounds back to original.
        tiny=im.copy();tiny.thumbnail((512,512),Image.Resampling.BILINEAR)
        t=np.array(tiny);h,w=t.shape[:2];dark=t.max(2)<=p['black_max']
        top=0;bottom=h;left=0;right=w
        while top<int(h*p['max_trim_fraction']) and dark[top].mean()>=p['dark_fraction']:top+=1
        while bottom>h-int(h*p['max_trim_fraction']) and dark[bottom-1].mean()>=p['dark_fraction']:bottom-=1
        while left<int(w*p['max_trim_fraction']) and dark[:,left].mean()>=p['dark_fraction']:left+=1
        while right>w-int(w*p['max_trim_fraction']) and dark[:,right-1].mean()>=p['dark_fraction']:right-=1
        mx=int(np.ceil(w*p['margin_fraction']));my=int(np.ceil(h*p['margin_fraction']))
        box=(max(0,int((left-mx)*im.width/w)),max(0,int((top-my)*im.height/h)),min(im.width,int(np.ceil((right+mx)*im.width/w))),min(im.height,int(np.ceil((bottom+my)*im.height/h))))
        info['crop_box']=box;info['reason']='Only near-black full strips; circular corners may remain.'
        return resize(im.crop(box)),info
    if method=='P10':
        gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
        _,m=cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        m[a.max(2)<15]=0
        n,lab,stats,cent=cv2.connectedComponentsWithStats(m)
        candidates=[k for k in range(1,n) if np.linalg.norm(cent[k]-np.array([112,112]))<80]
        if not candidates:
            info.update(fallback=True,reason='No central Otsu component');return base,info
        k=max(candidates,key=lambda j:stats[j,cv2.CC_STAT_AREA]);m=(lab==k).astype(np.uint8)*255
        x,y,w,h,area=stats[k];frac=area/SIZE**2;info['mask']=m;info['mask_fraction']=float(frac)
        if not p['min_area']<=frac<=p['max_area'] or x==0 or y==0 or x+w==SIZE or y+h==SIZE:
            info.update(fallback=True,reason='Mask area/edge guard; heuristic is not lesion truth');return base,info
        dx=p['margin_fraction']*w;dy=p['margin_fraction']*h
        box=(max(0,int((x-dx)*im.width/SIZE)),max(0,int((y-dy)*im.height/SIZE)),min(im.width,int(np.ceil((x+w+dx)*im.width/SIZE))),min(im.height,int(np.ceil((y+h+dy)*im.height/SIZE))))
        info.update(crop_box=box,reason='UNVALIDATED Otsu proposal; inspect all lesion edges')
        return resize(im.crop(box)),info
    if method in ['P03','P08']:
        if method=='P03':
            gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
            bh=cv2.morphologyEx(gray,cv2.MORPH_BLACKHAT,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(p['kernel'],p['kernel'])))
            mask=(bh>p['blackhat_threshold']).astype(np.uint8)*255
        else:
            hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV)
            raw=((hsv[:,:,2]>=p['value_min'])&(hsv[:,:,1]<=p['saturation_max'])).astype(np.uint8)
            n,lab,stats,_=cv2.connectedComponentsWithStats(raw)
            mask=np.zeros(raw.shape,np.uint8)
            for k in range(1,n):
                if stats[k,cv2.CC_STAT_AREA]<=p['max_component_pixels']:mask[lab==k]=255
        info['mask']=mask;info['mask_fraction']=float((mask>0).mean())
        if info['mask_fraction']>p['max_mask_fraction']:
            info.update(fallback=True,reason='Mask too large; unchanged baseline');return base,info
        if not mask.any():info['reason']='Empty mask';return base,info
        a=cv2.inpaint(a,mask,p['inpaint_radius'],cv2.INPAINT_TELEA)
    elif method=='P04':
        x=a.astype(np.float32)/255;valid=(a.min(2)>p['valid_min'])&(a.max(2)<p['valid_max'])
        if valid.sum()<100:
            info.update(fallback=True,reason='Insufficient valid pixels');return base,info
        illuminant=np.mean(x[valid]**p['p'],axis=0)**(1/p['p'])
        gains=np.clip(illuminant.mean()/np.maximum(illuminant,1e-6),p['gain_min'],p['gain_max'])
        a=u8(a*gains);info['gains']=gains.tolist()
    elif method in ['P05','P06','P09']:
        lab=cv2.cvtColor(a,cv2.COLOR_RGB2LAB);L=lab[:,:,0]
        if method=='P05':L=cv2.createCLAHE(clipLimit=p['clipLimit'],tileGridSize=tuple(p['tileGridSize'])).apply(L)
        elif method=='P06':L=u8(255*(L.astype(float)/255)**p['gamma'])
        else:
            smooth=cv2.GaussianBlur(L.astype(np.float32),(0,0),p['sigma'])
            gain=np.clip((np.median(smooth)+1)/(smooth+1),p['gain_min'],p['gain_max'])**p['strength']
            L=u8(L*gain)
        lab[:,:,0]=L;a=cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)
    elif method=='P07':a=cv2.bilateralFilter(a,p['d'],p['sigmaColor'],p['sigmaSpace'])
    return Image.fromarray(a),info
class FixedPreprocess:
    def __init__(self,method):self.method=method
    def __call__(self,im):return process(im,self.method)[0]
