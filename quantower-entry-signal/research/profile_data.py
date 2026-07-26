#!/usr/bin/env python3
# Mo du lieu 3 CSV: cot nao co so that, cot nao chet, range thoi gian, gap, semantics Max/Min delta.
import csv, statistics as st
from datetime import datetime, timedelta

DIR = "/home/asl86/Documents/footprint-tpo/data-export/"

def load(path):
    with open(DIR+path, encoding='utf-8-sig') as f:
        r = csv.reader(f); header = next(r)
        rows = [x for x in r if x and x[0].strip()]
    return header, rows

def fnum(x):
    try: return float(x)
    except: return None

def pdt(s): return datetime.strptime(s.strip(), "%m/%d/%Y %I:%M:%S %p")

def profile_file(path):
    print("="*90)
    print(f"FILE: {path}")
    h, rows = load(path)
    print(f"  cot = {len(h)} | dong du lieu = {len(rows)}")
    # time range
    try:
        dts = [pdt(x[0]) for x in rows]
        print(f"  thoi gian: {dts[0]}  ->  {dts[-1]}  ({(dts[-1]-dts[0]).total_seconds()/3600:.1f}h)")
    except Exception as e:
        dts=None; print(f"  (khong doc duoc datetime cot 0: {e})")
    # per-column: nonzero count, min, max, distinct(<=6)
    print(f"  {'idx':>3} {'ten cot':<34} {'#num':>5} {'#nonzero':>8} {'min':>10} {'max':>10}")
    for j,name in enumerate(h):
        vals=[fnum(x[j]) if j<len(x) else None for x in rows]
        nums=[v for v in vals if v is not None]
        nz=[v for v in nums if v!=0]
        mn=min(nums) if nums else None
        mx=max(nums) if nums else None
        flag = "  <-- CHET (toan 0/rong)" if not nz else ""
        nm=(name[:32]+'..') if len(name)>34 else name
        print(f"  {j:>3} {nm:<34} {len(nums):>5} {len(nz):>8} {str(round(mn,2) if mn is not None else ''):>10} {str(round(mx,2) if mx is not None else ''):>10}{flag}")
    return h, rows, dts

# ---- FP M1 chi tiet ----
def fp_detail():
    h, rows = load("fp-m1.csv")
    idx = {name:i for i,name in enumerate(h)}
    def col(nm): return idx[nm]
    iO,iH,iL,iC = col('Open'),col('High'),col('Low'),col('Close')
    iVol=col('Volume'); iBuy=col('Buy (Ask) volume'); iSell=col('Sell (Bid) volume')
    iDelta=col('Delta'); iMaxD=col('Max delta'); iMinD=col('Min delta'); iFin=col('Finish delta')
    iCum=col('Cumulative delta'); iVSA=col('VSA Volume_scale (ẩn)'); iDMA=col('Delta Moving Average (DMA)_DMA')
    print("="*90)
    print("FP-M1 — kiem tra semantics Max/Min delta + Buy+Sell=Vol + vai dong mau")
    # kiem tra Buy+Sell==Vol va Delta==Buy-Sell
    bad_bs=0; bad_d=0; maxd_ge_d=0; mind_le_d=0; maxd_ge_mind=0; n=0
    for x in rows:
        vol=fnum(x[iVol]); buy=fnum(x[iBuy]); sell=fnum(x[iSell]); d=fnum(x[iDelta])
        md=fnum(x[iMaxD]); nd=fnum(x[iMinD])
        if None in (vol,buy,sell,d,md,nd): continue
        n+=1
        if abs((buy+sell)-vol)>0.5: bad_bs+=1
        if abs((buy-sell)-d)>0.5: bad_d+=1
        if md>=d-0.001: maxd_ge_d+=1
        if nd<=d+0.001: mind_le_d+=1
        if md>=nd-0.001: maxd_ge_mind+=1
    print(f"  n={n}")
    print(f"  Buy+Sell==Volume : {n-bad_bs}/{n}")
    print(f"  Buy-Sell==Delta  : {n-bad_d}/{n}")
    print(f"  MaxDelta>=Delta  : {maxd_ge_d}/{n}   (neu ~100% => MaxDelta la dinh running-delta trong nen)")
    print(f"  MinDelta<=Delta  : {mind_le_d}/{n}   (neu ~100% => MinDelta la day running-delta trong nen)")
    print(f"  MaxDelta>=MinDelta: {maxd_ge_mind}/{n}")
    # in 8 dong mau
    print("  --- 8 dong mau (O H L C | Vol Buy Sell | Delta Max Min Fin Cum | VSA DMA) ---")
    for x in rows[:8]:
        print("   ", x[0][:19],
              f"| {fnum(x[iO])} {fnum(x[iH])} {fnum(x[iL])} {fnum(x[iC])}",
              f"| V{fnum(x[iVol]):.0f} B{fnum(x[iBuy]):.0f} S{fnum(x[iSell]):.0f}",
              f"| D{fnum(x[iDelta]):+.0f} Mx{fnum(x[iMaxD]):+.0f} Mn{fnum(x[iMinD]):+.0f} F{fnum(x[iFin]):+.0f} Cum{fnum(x[iCum]):+.0f}",
              f"| VSA{fnum(x[iVSA]):.0f} DMA{fnum(x[iDMA]):+.2f}")
    # phan phoi Volume, |Delta|, VSA, range(ticks)
    vols=[fnum(x[iVol]) for x in rows if fnum(x[iVol]) is not None]
    ad=[abs(fnum(x[iDelta])) for x in rows if fnum(x[iDelta]) is not None]
    vsa=[fnum(x[iVSA]) for x in rows if fnum(x[iVSA]) is not None]
    rng=[round((fnum(x[iH])-fnum(x[iL]))/0.1) for x in rows if fnum(x[iH]) is not None]
    exc_up=[fnum(x[iMaxD])-fnum(x[iDelta]) for x in rows if fnum(x[iMaxD]) is not None]  # dinh vuot qua close-delta
    exc_dn=[fnum(x[iDelta])-fnum(x[iMinD]) for x in rows if fnum(x[iMinD]) is not None]
    def pct(a,p): a=sorted(a); return a[min(len(a)-1,int(p*len(a)))]
    print("  --- phan phoi ---")
    for nm,a in [("Volume",vols),("|Delta|",ad),("VSA scale",vsa),("Range(t)",rng),
                 ("excursion_up(Max-D)",exc_up),("excursion_dn(D-Min)",exc_dn)]:
        print(f"    {nm:<20} med={st.median(a):>7.1f}  p25={pct(a,.25):>7.1f}  p75={pct(a,.75):>7.1f}  p90={pct(a,.90):>7.1f}  max={max(a):>7.1f}")
    # gaps giua cac nen
    dts=[pdt(x[0]) for x in rows]
    gaps=[(dts[i]-dts[i-1]).total_seconds()/60 for i in range(1,len(dts))]
    big=[(dts[i-1],dts[i],(dts[i]-dts[i-1]).total_seconds()/60) for i in range(1,len(dts)) if (dts[i]-dts[i-1]).total_seconds()/60>5]
    print(f"  --- gaps > 5' (nghi phien/bao tri): {len(big)} ---")
    for a,b,g in big: print(f"    {a.strftime('%m/%d %H:%M')} -> {b.strftime('%m/%d %H:%M')}  = {g:.0f} phut")
    miss=sum(1 for g in gaps if abs(g-1)<0.01)
    print(f"  nen lien tiep cach dung 1': {miss}/{len(gaps)}  (con lai la gap/missing minute)")

for f in ["fp-m1.csv","tpo-chart-m30.csv","TPO-chart-daily.csv"]:
    profile_file(f)
fp_detail()
print("="*90); print("DONE")
