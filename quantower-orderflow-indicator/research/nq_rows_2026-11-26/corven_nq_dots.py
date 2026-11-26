import numpy as np
from PIL import Image
from scipy import ndimage
im=np.asarray(Image.open(r'C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/ce3fca11-3030-4b09-9b13-33a6dd7ee683/images/13.png').convert('RGB')).astype(int)
R,G,B=im[...,0],im[...,1],im[...,2]
masks={'B':(B>190)&(R<150)&(G<170)&(B-R>70),'R':(R>180)&(G<90)&(B<90),'V':(R>170)&(B>180)&(G<150)&(R-G>50)}
roi=np.zeros(R.shape,bool); roi[60:590,10:1125]=True; roi[320:,1125:]=False
out=[]
for k,m in masks.items():
  lab,n=ndimage.label(m&roi)
  for i,sl in enumerate(ndimage.find_objects(lab)):
    ys,xs=sl; h=ys.stop-ys.start; w=xs.stop-xs.start; a=(lab[sl]==i+1).sum()
    if a<10 or w<3 or h<3: continue
    fill=a/(w*h); asp=h/w
    if fill<0.5: continue
    cx=(xs.start+xs.stop-1)/2; cy=(ys.start+ys.stop-1)/2
    # stacked dots of same colour: split tall blobs by width
    nst=max(1,round(h/w)) if asp>1.4 else 1
    for j in range(nst):
      yy=ys.start+(j+0.5)*h/nst
      out.append((k,cx,yy,w,a/nst))
pitch=(1108-78)/81.0
def t(x): m=round((x-78)/pitch); mm=39+m; return '%02d:%02d'%(14+mm//60,mm%60)
def p(y): return 27000-(y-283)/2.734
import csv
with open(r'%s/corven_nq_dots.csv'%r'C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/ce3fca11-3030-4b09-9b13-33a6dd7ee683/scratchpad','w',newline='') as f:
  wr=csv.writer(f); wr.writerow(['vn','kind','price','w'])
  for k,x,y,w,a in sorted(out,key=lambda o:o[1]):
    wr.writerow([t(x),k,round(p(y),1),w])
from collections import Counter
print(len(out),Counter(o[0] for o in out))
