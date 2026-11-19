import numpy as np, pandas as pd
from common import *
GT_DOT=gt_marks('dot')   # (bar,tk_mid,col,y0,y1,n_est)
DOT_D=9.5
def y_of_tk(tk): return (3792.8228-tk/10.0)/0.0723329
def merge(ints,gap=2):
    ints=sorted(ints); out=[]
    for a,b in ints:
        if out and a-out[-1][1]<=gap: out[-1][1]=max(out[-1][1],b)
        else: out.append([a,b])
    return out
def blobs_of(ours):
    from collections import defaultdict
    d=defaultdict(list)
    for (t,tk,c) in ours: y=y_of_tk(tk); d[(t,c)].append((y-DOT_D/2,y+DOT_D/2))
    return {k:merge(v) for k,v in d.items()}
def score_dots(S,tol=2):
    tolpx=tol*1.38
    ours=list(zip(S.datetime,S.tk,S.col))
    ob=blobs_of(ours)
    gb={}
    for (t,tk,c,y0,y1,n) in GT_DOT: gb.setdefault((t,c),[]).append([y0,y1+1,n])
    # blob level
    nb_o=sum(len(v) for v in ob.values()); nb_g=sum(len(v) for v in gb.values())
    hit_g=0; hit_o=set()
    for key,gl in gb.items():
        for g in gl:
            ov=[i for i,o in enumerate(ob.get(key,[])) if o[0]<=g[1]+tolpx and o[1]>=g[0]-tolpx]
            if ov: hit_g+=1; hit_o.update((key,i) for i in ov)
    extra_b=nb_o-len(hit_o)
    # pixel level
    cov=0; tot=0; ours_len=0; ours_in=0
    for key,gl in gb.items():
        olist=ob.get(key,[])
        for g in gl:
            ys=np.arange(int(g[0]),int(g[1])+1); tot+=len(ys)
            cov+=sum(any(o[0]-tolpx<=y<=o[1]+tolpx for o in olist) for y in ys)
    for key,olist in ob.items():
        for o in olist:
            ys=np.arange(int(o[0]),int(o[1])+1); ours_len+=len(ys)
            ours_in+=sum(any(g[0]-tolpx<=y<=g[1]+tolpx for g in gb.get(key,[])) for y in ys)
    rec=cov/tot; prec=ours_in/ours_len if ours_len else 0
    pf=2*rec*prec/(rec+prec) if rec+prec else 0
    # dot level: our dot inside GT centre range +-2 ticks
    dh=0
    for (t,tk,c) in ours:
        for (t2,tkm,c2,y0,y1,n) in GT_DOT:
            if t==t2 and c==c2:
                lo=tk_of_y(y1+1-DOT_D/2) if (y1-y0)>DOT_D else tk_of_y((y0+y1)/2)
                hi=tk_of_y(y0+DOT_D/2) if (y1-y0)>DOT_D else tk_of_y((y0+y1)/2)
                if lo-tol<=tk<=hi+tol: dh+=1; break
    gest=sum(g[5] for g in GT_DOT)
    return dict(n=len(ours),gt_est=gest,dot_hit=dh,dot_extra=len(ours)-dh,blobs=nb_o,gt_blobs=nb_g,blob_hit=hit_g,blob_miss=nb_g-hit_g,blob_extra=extra_b,pix_rec=round(rec,3),pix_prec=round(prec,3),pix_f1=round(pf,3))
