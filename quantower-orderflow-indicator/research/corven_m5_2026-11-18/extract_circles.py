"""Fit big translucent circles per bar from the CORVEN image. Circle centre x = bar centre (22+33k)."""
from PIL import Image
import numpy as np, json
from scipy.ndimage import binary_dilation
from pathlib import Path
HERE=Path(__file__).resolve().parent
im=np.array(Image.open(HERE/'corven-m5-2026-11-18.png').convert('RGB')).astype(float)
H,W,_=im.shape
price=lambda y:3792.8228-0.0723329*y
r,g,b=im[...,0],im[...,1],im[...,2]
mx=im.max(-1); mn=im.min(-1)
# invalid: dark, white, strongly saturated (dots/triangles/text), grid? keep grid (faint)
inval=(mx<170)|(mn>240)|((mx-mn)>75)
inval=binary_dilation(inval,iterations=2)
qp=np.clip(r-g,0,None); qb=np.clip(b-r,0,None)
Q={'pink':qp,'lblue':qb}
Q1={'pink':44.0,'lblue':25.0}
A=0.30
def fit(col,k,maxn=3):
    xc=22+33*k; x0=max(0,xc-30); x1=min(W,xc+31)
    q=Q[col][:,x0:x1]; v=~inval[:,x0:x1]
    # smooth q lightly
    from scipy.ndimage import uniform_filter
    q=uniform_filter(q,3)
    ys=np.where(((q>0.5*Q1[col])&v).sum(1)>=3)[0]
    if len(ys)==0: return []
    ylo,yhi=max(0,ys.min()-12),min(H,ys.max()+12)
    qq=q[ylo:yhi]; vv=v[ylo:yhi]
    yy,xx=np.mgrid[ylo:yhi,x0:x1]
    circles=[]; cover=np.zeros(qq.shape)  # number of circles
    def pred(cs):
        n=np.zeros(qq.shape)
        for cy,rr in cs: n+=((xx-xc)**2+(yy-cy)**2<=rr*rr)
        return Q1[col]*(1-(1-A)**n)/A  # q at n=1 -> Q1*(1)... normalised below
    def pred2(cs):
        n=np.zeros(qq.shape)
        for cy,rr in cs: n+=((xx-xc)**2+(yy-cy)**2<=rr*rr)
        return Q1[col]*(1-(1-A)**n)/A
    def sse(cs): return (((qq-pred2(cs))**2)*vv).sum()
    cur=sse([]); 
    for _ in range(maxn):
        best=None
        for cy in np.arange(ylo,yhi,1.0):
            for rr in range(7,28):
                s=sse(circles+[(cy,rr)])
                if best is None or s<best[0]: best=(s,cy,rr)
        if best[0] < cur*0.93 and cur-best[0]>Q1[col]**2*25:
            circles.append((best[1],best[2])); cur=best[0]
        else: break
    return circles
if __name__=='__main__':
    out=[]
    for k in range(27):
        for col in ('pink','lblue'):
            for cy,rr in fit(col,k):
                out.append((k,col,cy,rr)); print(k,f"{12+(15+5*k)//60}:{(15+5*k)%60:02d}",col,f"cy={cy:.0f} r={rr} price={price(cy):.2f}")
    json.dump(out,open(HERE/'circles_fit.json','w'))
