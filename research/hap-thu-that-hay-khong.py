"""HAP THU THAT SU LA GI? So sanh 5 ho su kien tren THUOC DO DOI XUNG.

Van de cua phep do truoc: su kien buoc phai la DAY MOI 20 nen => dieu kien 3 cua nguoi hoc
("no luc co, ket qua khong") bi LAM NGUOC. Va "K3 = thung 0,5 bien nen duoi day" thi mot nen
vua tao day moi rat de thung => K3 bi thoi phong bang hinh hoc.

Ban nay do lai bang RAO CHAN DOI XUNG: tu gia dong nen su kien, dat +u va -u
(u = trung vi bien do 50 nen), xem ben nao cham TRUOC trong 60 nen.
Nen ngau nhien phai cho ~50/50; su kien co that thi phai lech khoi 50%.

Ho su kien (chieu ban bi hap thu; chay guong cho chieu mua):
  A  ban thao PHA DAY      : vol>=3x, delta<=-4x, DAY MOI 20 nen               (cai da do truoc)
  B  HAP THU dung nghia    : vol>=3x, delta<=-4x, KHONG day moi, bien do <= trung vi, dong nua tren
  B2 no luc lon/ket qua nho: vol>=3x, delta<=-4x, bien do <= 0,7x trung vi     (khong rang buoc day)
  C  chi KHOI LUONG lon    : vol>=3x                                           (nen so sanh)
  D  nen ngau nhien        : moi nen thu 30                                     (nen chuan)
"""
import os, sys, math, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
W, LOOK, FWD, HOR = 50, 20, 30, 60

def mirror(o,h,l,c,dl):
    return [-x for x in o],[-x for x in l],[-x for x in h],[-x for x in c],[-x for x in dl]

def scan(t,o,h,l,c,v,dl):
    """tra ve dict ho -> list (i, u) ; u = trung vi bien do 50 nen truoc"""
    n=len(t); fam={k:[] for k in "A B B2 C D".split()}
    last={k:-10**9 for k in fam}
    for i in range(W+LOOK, n-HOR-2):
        seg=t[i-W:i+HOR+2]
        if seg[-1]-seg[0]!=len(seg)-1: continue
        win_v=v[i-W:i]; win_d=[abs(x) for x in dl[i-W:i]]; win_r=[h[j]-l[j] for j in range(i-W,i)]
        mv=st.median(win_v); md=st.median(win_d); u=st.median(win_r)
        if mv<=0 or md<=0 or u<=0: continue
        R=h[i]-l[i]
        big_v = v[i]>=3.0*mv
        big_d = dl[i]<=-4.0*md
        newlow = l[i]<=min(l[i-LOOK:i])
        upper_close = (R>0 and c[i]>=l[i]+0.5*R)
        def put(k):
            if i-last[k]>=FWD: fam[k].append((i,u)); last[k]=i
        if big_v and big_d and newlow: put("A")
        if big_v and big_d and (not newlow) and R<=u and upper_close: put("B")
        if big_v and big_d and R<=0.7*u: put("B2")
        if big_v: put("C")
        if i%30==0: put("D")
    return fam

def barrier(i,u,k,h,l,c):
    """ben nao cham truoc: +k*u (theo huong hap thu mong doi) hay -k*u"""
    up=c[i]+k*u; dn=c[i]-k*u
    for j in range(i+1, min(i+HOR, len(h)-1)):
        hitu = h[j]>=up; hitd = l[j]<=dn
        if hitu and hitd: return "cung nen"
        if hitu: return "thuan"
        if hitd: return "nguoc"
    return "khong toi"

def measure(fam,h,l,c,k):
    out={}
    for name,ev in fam.items():
        r={"thuan":0,"nguoc":0,"cung nen":0,"khong toi":0}
        for i,u in ev: r[barrier(i,u,k,h,l,c)]+=1
        out[name]=r
    return out

def zsc(p,p0,n):
    if n==0 or p0<=0 or p0>=1: return 0.0
    return (p-p0)/math.sqrt(p0*(1-p0)/n)

if __name__=="__main__":
    t,o,h,l,c,v,dl=load(PATH); print("so nen:",len(t),flush=True)
    print("dang quet chieu 1...",flush=True)
    f1=scan(t,o,h,l,c,v,dl)
    mo,mh,ml,mc,mdl=mirror(o,h,l,c,dl)
    print("dang quet chieu 2 (guong)...",flush=True)
    f2=scan(t,mo,mh,ml,mc,v,mdl)
    for k in (1.0,2.0):
        print(f"\n===== RAO CHAN +-{k}x trung vi bien do, toi da {HOR} nen =====")
        m1=measure(f1,h,l,c,k); m2=measure(f2,mh,ml,mc,k)
        # nen chuan gop 2 chieu
        base={x:m1["D"][x]+m2["D"][x] for x in m1["D"]}
        bt=base["thuan"]+base["nguoc"]
        p0=base["thuan"]/bt if bt else 0.5
        print(f"  nen chuan D (gop 2 chieu, n={sum(base.values())}): thuan {p0*100:.1f}% "
              f"(tren tong so ca ra ket qua ro)")
        for name in ("A","B","B2","C","D"):
            a={x:m1[name][x]+m2[name][x] for x in m1[name]}
            tot=sum(a.values()); dec=a["thuan"]+a["nguoc"]
            if dec<30: print(f"  {name}: n={tot} qua it"); continue
            p=a["thuan"]/dec
            print(f"  {name:3s} n={tot:6d} | thuan {100.0*a['thuan']/tot:5.1f}%  nguoc {100.0*a['nguoc']/tot:5.1f}%"
                  f"  cung nen {100.0*a['cung nen']/tot:4.1f}%  khong toi {100.0*a['khong toi']/tot:4.1f}%"
                  f" | ty le thuan/(thuan+nguoc) = {100*p:5.1f}%  z so voi nen chuan = {zsc(p,p0,dec):+5.2f}")
        # tach rieng 2 chieu cho ho A va B
        for name in ("A","B"):
            for tag,m in (("day/mua",m1),("dinh/ban",m2)):
                a=m[name]; tot=sum(a.values()); dec=a["thuan"]+a["nguoc"]
                if dec<30: continue
                print(f"    {name} {tag:9s} n={tot:6d} thuan/(thuan+nguoc) = {100.0*a['thuan']/dec:5.1f}%")
