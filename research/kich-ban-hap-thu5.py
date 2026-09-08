"""Ban 5: chay CA HAI CHIEU bang cach lat guong du lieu (gia va delta doi dau).

- chieu BAN BI HAP THU (day, cum delta am cuc doan)  -> lenh MUA
- chieu MUA BI HAP THU (dinh, cum delta duong cuc doan) -> lenh BAN
Cung mot bo code, chi lat guong => so sanh duoc truc tiep.
"""
import os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
W, LOOK, FWD = 50, 20, 30

def mirror(o,h,l,c,dl):
    return [-x for x in o], [-x for x in l], [-x for x in h], [-x for x in c], [-x for x in dl]

def context(t,o,h,l,c,v):
    sid=[(x+120)//1440 for x in t]; n=len(t)
    vwap=[0.0]*n; slo=[0.0]*n
    pv=pvol=0.0; lo=1e18; cur=sid[0]
    for i in range(n):
        if sid[i]!=cur: cur=sid[i]; pv=pvol=0.0; lo=1e18
        tp=(h[i]+l[i]+c[i])/3.0; pv+=tp*v[i]; pvol+=v[i]
        vwap[i]=pv/pvol if pvol>0 else c[i]
        lo=min(lo,l[i]); slo[i]=lo
    return vwap,slo

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

def trade(entry,stop,i,h,l,c,jstart,horizon=60,rr=2.0):
    risk=entry-stop
    if risk<=0: return None
    tgt=entry+rr*risk
    for j in range(jstart,min(i+horizon,len(h)-1)):
        if l[j]<=stop: return -1.0
        if h[j]>=tgt: return rr
    j=min(i+horizon,len(h)-1)
    return (c[j]-entry)/risk

def report(tag,t,o,h,l,c,v,dl):
    vwap,slo=context(t,o,h,l,c,v)
    ev=find_events(t,o,h,l,c,v,dl)
    conf=[i for i in ev if dl[i+1]>=0.5*abs(dl[i])]
    soft=[i for i in ev if dl[i+1]>0]
    print(f"\n########## {tag} ##########")
    print(f"so ca: {len(ev)} | co xac nhan manh: {len(conf)} ({100.0*len(conf)/len(ev):.1f}%) | "
          f"xac nhan nhe: {len(soft)} ({100.0*len(soft)/len(ev):.1f}%)")
    for lab,subset,start in (("KHONG loc xac nhan",ev,1),("CO xac nhan manh",conf,2)):
        r={"K1":0,"K2":0,"K3":0,"K0":0}
        for i in subset: r[classify(i,h,l,start=start)]+=1
        tot=sum(r.values()) or 1
        print(f"  {lab:22s} n={tot:5d} | " + "  ".join(f"{k} {100.0*r[k]/tot:4.1f}%" for k in ("K1","K2","K3","K0")))
    # vung
    for nm,fn in (("duoi VWAP",lambda i: c[i]<vwap[i]),("la day/dinh PHIEN moi",lambda i: l[i]<=slo[i]+1e-9)):
        for lab,subset,start in (("khong loc",ev,1),("co xac nhan",conf,2)):
            r={True:{"K1":0,"K2":0,"K3":0,"K0":0},False:{"K1":0,"K2":0,"K3":0,"K0":0}}
            for i in subset: r[bool(fn(i))][classify(i,h,l,start=start)]+=1
            for b in (True,False):
                tot=sum(r[b].values())
                if tot<25: continue
                print(f"    [{nm}={'CO' if b else 'KHONG'}] {lab:12s} n={tot:5d} | "
                      + "  ".join(f"{k} {100.0*r[b][k]/tot:4.1f}%" for k in ("K1","K2","K3","K0")))
    # vao lenh
    res={}
    def add(k,x):
        if x is not None: res.setdefault(k,[]).append(x)
    for i in ev:
        L=l[i]; R=h[i]-l[i]
        if dl[i+1]>=0.5*abs(dl[i]):
            add("V0  vao ngay nen xac nhan | lo duoi day su kien",trade(c[i+1],L-0.5*R,i,h,l,c,i+2))
        if min(l[i+1:i+3])>L:
            e=None
            for j in range(i+3,i+11):
                if j>=len(h)-1: break
                if l[j]<=L: e=None; break
                if c[j]>o[j] and dl[j]>0: e=j; break
            if e:
                add("V2  cho 2 nen di ngang | lo duoi day su kien",trade(c[e],L-0.5*R,i,h,l,c,e+1))
                add("V2t cho 2 nen di ngang | lo SAT cum di ngang",trade(c[e],min(l[i+1:e])-0.3,i,h,l,c,e+1))
    for k in sorted(res):
        a=res[k]; n=len(a)
        win=sum(1 for x in a if x>=1.99); loss=sum(1 for x in a if x<=-0.99)
        print(f"  {k:48s} n={n:5d} thang {100.0*win/n:4.1f}% thua {100.0*loss/n:4.1f}% ky vong {st.mean(a):+.3f}R")

if __name__=="__main__":
    t,o,h,l,c,v,dl=load(PATH)
    report("CHIEU 1: BAN bi hap thu o DAY -> lenh MUA", t,o,h,l,c,v,dl)
    mo,mh,ml,mc,mdl=mirror(o,h,l,c,dl)
    report("CHIEU 2: MUA bi hap thu o DINH -> lenh BAN (lat guong)", t,mo,mh,ml,mc,v,mdl)
