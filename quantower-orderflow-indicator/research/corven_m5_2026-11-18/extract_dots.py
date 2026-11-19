"""Solid dot blobs (red=Bid, blue=Ask) from the CORVEN image: per bar y-ranges (pixels)."""
from PIL import Image
import numpy as np, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
im=np.array(Image.open(HERE/'corven-m5-2026-11-18.png').convert('RGB')).astype(int)
price=lambda y:3792.8228-0.0723329*y
def blobs():
    out=[]
    for k in range(27):
        xc=22+33*k
        for name,f in (('R',lambda p:(p[...,0]>160)&(p[...,1]<120)&(p[...,2]<120)),('B',lambda p:(p[...,2]>190)&(p[...,0]<110)&(p[...,1]>80)&(p[...,1]<190))):
            m=f(im[:,xc-6:xc+7])
            rows=np.where(m.sum(1)>=4)[0]
            if len(rows)==0: continue
            grp=[[rows[0],rows[0]]]
            for y in rows[1:]:
                if y-grp[-1][1]<=2: grp[-1][1]=y
                else: grp.append([y,y])
            for a,b in grp:
                if b-a<5: continue
                out.append(dict(k=k,col=name,y0=int(a),y1=int(b),h=int(b-a+1),w=int(m[a:b+1].sum(1).max())))
    return out
if __name__=='__main__':
    for o in blobs():
        k=o['k']; print(k,f"{12+(15+5*k)//60}:{(15+5*k)%60:02d}",o['col'],o['y0'],o['y1'],'h',o['h'],'w',o['w'],'edge prices',round(price(o['y1']),2),round(price(o['y0']),2))
