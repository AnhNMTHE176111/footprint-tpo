import numpy as np, sys
from extract_circles import *
from scipy.ndimage import uniform_filter
def force(col,k,n,ylo,yhi,rr=range(8,27)):
    xc=22+33*k; x0=xc-30; x1=xc+31
    q=uniform_filter(Q[col][:,x0:x1],3); v=~inval[:,x0:x1]
    qq=q[ylo:yhi]; vv=v[ylo:yhi]; yy,xx=np.mgrid[ylo:yhi,x0:x1]
    cache={}
    def m(cy,r):
        key=(cy,r)
        if key not in cache: cache[key]=((xx-xc)**2+(yy-cy)**2<=r*r).astype(float)
        return cache[key]
    def sse(cs):
        nn=sum(m(*c) for c in cs); return (((qq-Q1[col]*(1-(1-A)**nn)/A)**2)*vv).sum()
    best=None
    import itertools
    cands=[(cy,r) for cy in range(ylo,yhi,2) for r in rr]
    # greedy then refine
    cs=[]
    for _ in range(n):
        bb=min(cands,key=lambda c:sse(cs+[c])); cs.append(bb)
    for it in range(3):
        for i in range(n):
            others=cs[:i]+cs[i+1:]
            loc=[(cy,r) for cy in range(cs[i][0]-4,cs[i][0]+5) for r in range(max(7,cs[i][1]-3),cs[i][1]+4)]
            cs[i]=min(loc,key=lambda c:sse(others+[c]))
    return cs,sse(cs)
if __name__=='__main__':
    k=int(sys.argv[1]); col=sys.argv[2]; n=int(sys.argv[3]); ylo=int(sys.argv[4]); yhi=int(sys.argv[5])
    for nn in range(1,n+1):
        cs,s=force(col,k,nn,ylo,yhi); print(nn,cs,s,[round(price(c[0]),2) for c in cs])
