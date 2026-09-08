"""Ban 2: do nhay nguong xuyen day + loc theo XAC NHAN (nen ke tiep delta dao chieu manh)."""
import os,sys,statistics as st
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATH=os.path.join(ROOT,"data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
W,LOOK,FWD=50,20,30

def events(t,o,h,l,c,v,dl,vol_mult=3.0,dlt_mult=4.0):
    n=len(t); out=[]; i=W+LOOK
    while i<n-FWD-1:
        if l[i]>min(l[i-LOOK:i]): i+=1; continue
        seg=t[i-W:i+FWD+1]
        if seg[-1]-seg[0]!=len(seg)-1: i+=1; continue
        mv=st.median(v[i-W:i]); md=st.median([abs(x) for x in dl[i-W:i]])
        if mv<=0 or md<=0: i+=1; continue
        if v[i]<vol_mult*mv or dl[i]>-dlt_mult*md: i+=1; continue
        if h[i]-l[i]<=0: i+=1; continue
        out.append((i,md)); i+=FWD
    return out

def classify(ev,t,o,h,l,c,v,dl,up_R=2.0,break_mode="tick",break_val=0.3,
             retest_th=0.5,confirm=None):
    res={"K1":0,"K2":0,"K3":0,"K0":0}
    for i,md in ev:
        if confirm=="flip" and dl[i+1]<0.5*abs(dl[i]): continue
        if confirm=="flip_soft" and dl[i+1]<=0: continue
        risk=h[i]-l[i]; L=l[i]
        bt=break_val if break_mode=="tick" else break_val*risk
        tgt=L+up_R*risk; retested=False; outc="K0"
        start=i+2 if confirm else i+1
        for j in range(start,i+1+FWD):
            if l[j]<=L-bt: outc="K3"; break
            if h[j]>=tgt: outc="K2" if retested else "K1"; break
            if l[j]<=L+retest_th: retested=True
        res[outc]+=1
    return res

def show(tag,res):
    tot=sum(res.values())
    if tot==0: print(f"{tag:52s} n=0"); return
    p=lambda k:100.0*res[k]/tot
    k12=res["K1"]+res["K2"]
    print(f"{tag:52s} n={tot:5d} | K1 {p('K1'):5.1f}%  K2 {p('K2'):5.1f}%  K3 {p('K3'):5.1f}%  K0 {p('K0'):5.1f}%"
          f" | K1:K2 = {100.0*res['K1']/max(1,k12):.0f}:{100.0*res['K2']/max(1,k12):.0f}")

if __name__=="__main__":
    t,o,h,l,c,v,dl=load(PATH); print("so nen:",len(t),flush=True)
    ev=events(t,o,h,l,c,v,dl); print("so ca ban thao (chua loc xac nhan):",len(ev),flush=True)
    print("\n--- A. KHONG loc xac nhan, do nhay nguong xuyen day ---")
    for m,bv,lab in (("tick",0.3,"xuyen 3 tick"),("tick",0.6,"xuyen 6 tick"),
                     ("tick",1.0,"xuyen 1.0 gia"),("rel",0.5,"xuyen 0.5x bien nen"),
                     ("rel",1.0,"xuyen 1.0x bien nen")):
        show(f"A {lab}, muc tieu 2R", classify(ev,t,o,h,l,c,v,dl,2.0,m,bv))
    print("\n--- B. CO loc xac nhan: nen ke tiep delta >= 50% do lon delta nen ban thao ---")
    for m,bv,lab in (("tick",0.3,"xuyen 3 tick"),("tick",0.6,"xuyen 6 tick"),
                     ("rel",0.5,"xuyen 0.5x bien nen"),("rel",1.0,"xuyen 1.0x bien nen")):
        show(f"B {lab}, muc tieu 2R", classify(ev,t,o,h,l,c,v,dl,2.0,m,bv,confirm="flip"))
    print("\n--- C. loc xac nhan nhe (nen ke tiep delta > 0) ---")
    for m,bv,lab in (("rel",0.5,"xuyen 0.5x bien nen"),("rel",1.0,"xuyen 1.0x bien nen")):
        show(f"C {lab}, muc tieu 2R", classify(ev,t,o,h,l,c,v,dl,2.0,m,bv,confirm="flip_soft"))
