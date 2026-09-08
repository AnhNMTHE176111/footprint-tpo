"""Nen XAC NHAN co suc du bao thuc su khong, hay chi la hieu ung hinh hoc?

Do bang RAO CHAN DOI XUNG tinh tu GIA DONG NEN XAC NHAN (diem vao lenh thuc te).
So voi 2 nen chuan:
  D  nen ngau nhien
  E  nen delta duong cuc doan BAT KY (khong can co cum hap thu truoc do) -> kiem soat "dong luong delta"
Ho:
  Ac ban thao PHA DAY + nen xac nhan
  Bc HAP THU dung nghia + nen xac nhan
"""
import os, sys, math, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH=os.path.join(ROOT,"data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
W,LOOK,FWD,HOR=50,20,30,60

def mirror(o,h,l,c,dl):
    return [-x for x in o],[-x for x in l],[-x for x in h],[-x for x in c],[-x for x in dl]

def scan(t,o,h,l,c,v,dl):
    n=len(t); fam={k:[] for k in ("Ac","Bc","E","D")}
    last={k:-10**9 for k in fam}
    for i in range(W+LOOK,n-HOR-4):
        seg=t[i-W:i+HOR+4]
        if seg[-1]-seg[0]!=len(seg)-1: continue
        mv=st.median(v[i-W:i]); md=st.median([abs(x) for x in dl[i-W:i]])
        u=st.median([h[j]-l[j] for j in range(i-W,i)])
        if mv<=0 or md<=0 or u<=0: continue
        R=h[i]-l[i]
        big_v=v[i]>=3.0*mv; big_d=dl[i]<=-4.0*md
        newlow=l[i]<=min(l[i-LOOK:i]); upper=(R>0 and c[i]>=l[i]+0.5*R)
        conf = dl[i+1]>=0.5*abs(dl[i]) and dl[i+1]>0
        def put(k,anchor):
            if i-last[k]>=FWD: fam[k].append((anchor,u)); last[k]=i
        if big_v and big_d and newlow and conf: put("Ac",i+1)
        if big_v and big_d and (not newlow) and R<=u and upper and conf: put("Bc",i+1)
        if dl[i]>=4.0*md and v[i]>=3.0*mv: put("E",i)   # nen delta duong cuc doan bat ky
        if i%30==0: put("D",i)
    return fam

def barrier(i,u,k,h,l,c):
    up=c[i]+k*u; dn=c[i]-k*u
    for j in range(i+1,min(i+HOR,len(h)-1)):
        a=h[j]>=up; b=l[j]<=dn
        if a and b: return "cung nen"
        if a: return "thuan"
        if b: return "nguoc"
    return "khong toi"

def zsc(p,p0,n):
    if n==0: return 0.0
    return (p-p0)/math.sqrt(p0*(1-p0)/n)

if __name__=="__main__":
    t,o,h,l,c,v,dl=load(PATH)
    print("quet chieu 1...",flush=True); f1=scan(t,o,h,l,c,v,dl)
    mo,mh,ml,mc,mdl=mirror(o,h,l,c,dl)
    print("quet chieu 2...",flush=True); f2=scan(t,mo,mh,ml,mc,v,mdl)
    for k in (1.0,2.0,3.0):
        print(f"\n===== rao chan +-{k}x trung vi bien do, tinh tu dong nen XAC NHAN =====")
        res={}
        for name in ("Ac","Bc","E","D"):
            r={"thuan":0,"nguoc":0,"cung nen":0,"khong toi":0}
            for (i,u) in f1[name]: r[barrier(i,u,k,h,l,c)]+=1
            for (i,u) in f2[name]: r[barrier(i,u,k,mh,ml,mc)]+=1
            res[name]=r
        dec0=res["D"]["thuan"]+res["D"]["nguoc"]; p0=res["D"]["thuan"]/dec0
        for name in ("Ac","Bc","E","D"):
            a=res[name]; tot=sum(a.values()); dec=a["thuan"]+a["nguoc"]
            if dec<30: print(f"  {name}: n={tot} qua it"); continue
            p=a["thuan"]/dec
            print(f"  {name:3s} n={tot:6d} | thuan {100.0*p:5.1f}%  (z = {zsc(p,p0,dec):+5.2f})")
        for name in ("Ac","Bc"):
            for tag,fs,hh,ll,cc in (("day/mua",f1,h,l,c),("dinh/ban",f2,mh,ml,mc)):
                r={"thuan":0,"nguoc":0,"cung nen":0,"khong toi":0}
                for (i,u) in fs[name]: r[barrier(i,u,k,hh,ll,cc)]+=1
                dec=r["thuan"]+r["nguoc"]
                if dec<30: continue
                print(f"    {name} {tag:9s} n={sum(r.values()):5d} thuan {100.0*r['thuan']/dec:5.1f}%")
