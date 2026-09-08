"""Ban 4: (a) vung day phien truoc voi bien do rong hon, (b) them bien the DUNG LO SAT hon."""
import os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load
from importlib import import_module
m = import_module("kich-ban-hap-thu3".replace("-", "_")) if False else None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
W, LOOK, FWD = 50, 20, 30

def sessions(t): return [(x+120)//1440 for x in t]

def context(t,o,h,l,c,v):
    sid = sessions(t); n=len(t)
    vwap=[0.0]*n; slo=[0.0]*n; plo=[None]*n
    pv=pvol=0.0; lo=1e18; cur=sid[0]; done={}
    for i in range(n):
        if sid[i]!=cur:
            done[cur]=lo; cur=sid[i]; pv=pvol=0.0; lo=1e18
        tp=(h[i]+l[i]+c[i])/3.0; pv+=tp*v[i]; pvol+=v[i]
        vwap[i]=pv/pvol if pvol>0 else c[i]
        lo=min(lo,l[i]); slo[i]=lo; plo[i]=done.get(sid[i]-1)
    return sid,vwap,slo,plo

def find_events(t,o,h,l,c,v,dl,vol_mult=3.0,dlt_mult=4.0):
    n=len(t); out=[]; i=W+LOOK
    while i<n-FWD-61:
        if l[i]>min(l[i-LOOK:i]): i+=1; continue
        seg=t[i-W:i+FWD+61]
        if seg[-1]-seg[0]!=len(seg)-1: i+=1; continue
        mv=st.median(v[i-W:i]); md=st.median([abs(x) for x in dl[i-W:i]])
        if mv<=0 or md<=0: i+=1; continue
        if v[i]<vol_mult*mv or dl[i]>-dlt_mult*md: i+=1; continue
        if h[i]-l[i]<=0: i+=1; continue
        out.append(i); i+=FWD
    return out

def classify(i,h,l,up_R=2.0,brk_rel=0.5,retest=0.5,start=1):
    R=h[i]-l[i]; L=l[i]; bt=brk_rel*R; tgt=L+up_R*R; rt=False
    for j in range(i+start,i+1+FWD):
        if l[j]<=L-bt: return "K3"
        if h[j]>=tgt: return "K2" if rt else "K1"
        if l[j]<=L+retest: rt=True
    return "K0"

def trade(entry,stop,i,h,l,c,jstart,horizon=60,rr=2.0,longside=True):
    risk=(entry-stop) if longside else (stop-entry)
    if risk<=0: return None
    tgt=entry+rr*risk if longside else entry-rr*risk
    for j in range(jstart,min(i+horizon,len(h)-1)):
        if longside:
            if l[j]<=stop: return -1.0
            if h[j]>=tgt: return rr
        else:
            if h[j]>=stop: return -1.0
            if l[j]<=tgt: return rr
    j=min(i+horizon,len(h)-1)
    return ((c[j]-entry)/risk) if longside else ((entry-c[j])/risk)

if __name__=="__main__":
    t,o,h,l,c,v,dl=load(PATH); sid,vwap,slo,plo=context(t,o,h,l,c,v)
    ev=find_events(t,o,h,l,c,v,dl); print("so ca:",len(ev),flush=True)

    print("\n=== A2. TRUNG vung day phien truoc, bien do rong hon ===")
    for d in (3.0,5.0,10.0):
        for conf in (False,True):
            b={}
            for i in ev:
                if conf and dl[i+1]<0.5*abs(dl[i]): continue
                if plo[i] is None: continue
                k="TRUNG" if abs(l[i]-plo[i])<=d else "khong trung"
                b.setdefault(k,{"K1":0,"K2":0,"K3":0,"K0":0})
                b[k][classify(i,h,l,start=2 if conf else 1)]+=1
            for k in ("TRUNG","khong trung"):
                if k not in b: continue
                tot=sum(b[k].values())
                if tot<25: print(f"  +-{d} {'CO xac nhan' if conf else 'khong xac nhan'} {k}: n={tot} (<25, bo)"); continue
                p=lambda x:100.0*b[k][x]/tot
                print(f"  +-{d:<4} {'CO xac nhan ' if conf else 'khong xac nhan'} {k:12s} n={tot:5d} | "
                      f"K1 {p('K1'):4.1f}% K2 {p('K2'):4.1f}% K3 {p('K3'):4.1f}% K0 {p('K0'):4.1f}%")

    print("\n=== B2. cac kieu vao lenh, so sanh DUNG LO RONG (duoi day ban thao) vs SAT (duoi cum di ngang) ===")
    res={}
    def add(k,r):
        if r is not None: res.setdefault(k,[]).append(r)
    for i in ev:
        L=l[i]; R=h[i]-l[i]
        if dl[i+1]>=0.5*abs(dl[i]):
            add("V0  vao ngay nen xac nhan | lo duoi day", trade(c[i+1],L-0.5*R,i,h,l,c,i+2))
            add("V0t vao ngay nen xac nhan | lo duoi day nen xac nhan", trade(c[i+1],min(l[i+1],L)-0.3,i,h,l,c,i+2))
        for k in (2,3):
            if min(l[i+1:i+1+k])<=L: continue
            e=None
            for j in range(i+1+k,i+1+k+8):
                if j>=len(h)-1: break
                if l[j]<=L: e=None; break
                if c[j]>o[j] and dl[j]>0: e=j; break
            if not e: continue
            cl_lo=min(l[i+1:e])
            add(f"V{k} cho {k} nen di ngang | lo duoi day ban thao", trade(c[e],L-0.5*R,i,h,l,c,e+1))
            add(f"V{k}t cho {k} nen di ngang | lo SAT duoi cum di ngang", trade(c[e],cl_lo-0.3,i,h,l,c,e+1))
        if min(l[i+1:i+3])>L:
            hi=max(h[i+1:i+3]); e=None
            for j in range(i+3,i+11):
                if j>=len(h)-1: break
                if l[j]<=L-0.5*R: e=j; break
            if e: add("V3  di ngang roi xuyen day -> BAN", trade(c[e],hi+0.3,i,h,l,c,e+1,longside=False))
    for k in sorted(res):
        a=res[k]; n=len(a)
        win=sum(1 for x in a if x>=1.99); loss=sum(1 for x in a if x<=-0.99)
        print(f"  {k:58s} n={n:5d} thang {100.0*win/n:4.1f}% thua {100.0*loss/n:4.1f}% "
              f"ky vong {st.mean(a):+.3f}R")
