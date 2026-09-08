"""Neu khong bao HUONG thi co bao BIEN DONG khong? (gia thuyet: cum hap thu bao 'sap co move')

Do: bien do 30 nen ke tiep (cao nhat - thap nhat) chia cho u = trung vi bien do 50 nen truoc.
So voi nen ngau nhien. Neu > nen chuan => cum do bao truoc mot doan chay, du khong biet huong.
"""
import os,sys,statistics as st
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH=os.path.join(ROOT,"data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
W,LOOK,FWD,FW=50,20,30,30

if __name__=="__main__":
    t,o,h,l,c,v,dl=load(PATH); n=len(t)
    fam={k:[] for k in ("A","B","B2","C","D")}; last={k:-10**9 for k in fam}
    for i in range(W+LOOK,n-FW-3):
        seg=t[i-W:i+FW+3]
        if seg[-1]-seg[0]!=len(seg)-1: continue
        mv=st.median(v[i-W:i]); md=st.median([abs(x) for x in dl[i-W:i]])
        u=st.median([h[j]-l[j] for j in range(i-W,i)])
        if mv<=0 or md<=0 or u<=0: continue
        R=h[i]-l[i]
        bv=v[i]>=3.0*mv; bd=abs(dl[i])>=4.0*md
        nl=(l[i]<=min(l[i-LOOK:i])) or (h[i]>=max(h[i-LOOK:i]))
        small=R<=u
        fut=(max(h[i+1:i+1+FW])-min(l[i+1:i+1+FW]))/u
        def put(k):
            if i-last[k]>=FWD: fam[k].append(fut); last[k]=i
        if bv and bd and nl: put("A")
        if bv and bd and (not nl) and small: put("B")
        if bv and bd and R<=0.7*u: put("B2")
        if bv: put("C")
        if i%30==0: put("D")
    print("bien do 30 nen ke tiep / trung vi bien do 50 nen truoc")
    for k in ("A","B","B2","C","D"):
        a=fam[k]
        if len(a)<30: print(f"  {k}: n={len(a)} qua it"); continue
        print(f"  {k:3s} n={len(a):6d} | trung vi {st.median(a):5.2f}  trung binh {st.mean(a):5.2f}"
              f"  phan vi 25/75 {sorted(a)[len(a)//4]:4.2f}/{sorted(a)[3*len(a)//4]:5.2f}")
