#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NGHIEN CUU OFFLINE SAU — 28 ngay M1. Tra loi 4 cau:
 1. Entry co gia tri du bao? (MFE/MAE tin hieu vs baseline ngau nhien cung phia)
 2. 3R co tham? (WR + ky vong o target 1R/1.5R/2R/3R, SL nhu thiet ke)
 3. Subset nao co edge? (scenario1, phan ky CVD, confluence, gio phien, climax)
 4. Do rong SL co doi cuc dien? (quet SL 2/3/4/6d, TP=3xSL)
Tai dung bo sinh tin hieu tu entry_month.py.
"""
import sys, random, statistics as st
sys.path.insert(0,"/tmp/claude-1000/-home-asl86-Documents-footprint-tpo/55fa089c-afb3-4cf9-bca4-58241a901028/scratchpad")
import entry_month as em
TICK=em.TICK; random.seed(42)
H_MFE=120  # chan trong 2h de do MFE/MAE

def cvd_div(B,i,side,K=20):
    w=B[max(0,i-K):i]
    if not w: return False
    if side=='LONG':
        pm=min(w,key=lambda b:b['lo'])
        return B[i]['lo']<pm['lo'] and B[i]['cum']>pm['cum']
    else:
        pm=max(w,key=lambda b:b['hi'])
        return B[i]['hi']>pm['hi'] and B[i]['cum']<pm['cum']

def mfe_mae(B,i,side,H=H_MFE):
    e=B[i]['c']; hi=lo=e
    for j in range(i+1,min(i+1+H,len(B))):
        hi=max(hi,B[j]['hi']); lo=min(lo,B[j]['lo'])
    if side=='LONG': return (hi-e)/TICK,(e-lo)/TICK   # MFE,MAE (tick, >=0)
    else:            return (e-lo)/TICK,(hi-e)/TICK

def hit_target(B,i,side,sl_px,tp_px):
    for j in range(i+1,len(B)):
        b=B[j]
        sl=(b['lo']<=sl_px) if side=='LONG' else (b['hi']>=sl_px)
        tp=(b['hi']>=tp_px) if side=='LONG' else (b['lo']<=tp_px)
        if sl and tp: return 'SL'   # bi quan
        if sl: return 'SL'
        if tp: return 'TP'
    return 'open'

def wr_exp(sigs,B,rmult):
    # SL = risk da dat; TP = rmult * risk
    tp=sl=0
    for s in sigs:
        r=s['risk_t']*TICK
        tp_px = s['entry']+rmult*r if s['side']=='LONG' else s['entry']-rmult*r
        o=hit_target(B,s['i'],s['side'],s['sl'],tp_px)
        if o=='TP':tp+=1
        elif o=='SL':sl+=1
    n=tp+sl
    if n==0:return 0,0,0,0
    wr=tp/n; exp=(tp*rmult - sl*1.0)/n
    return n,tp,wr,exp

def wr_exp_fixedSL(sigs,B,slW_t,rr=3.0):
    tp=sl=0
    for s in sigs:
        e=s['entry']; slp=e-slW_t*TICK if s['side']=='LONG' else e+slW_t*TICK
        tpp=e+rr*slW_t*TICK if s['side']=='LONG' else e-rr*slW_t*TICK
        o=hit_target(B,s['i'],s['side'],slp,tpp)
        if o=='TP':tp+=1
        elif o=='SL':sl+=1
    n=tp+sl
    return (n,tp/n if n else 0,(tp*rr-sl)/n if n else 0)

def main():
    B=em.load_m1(); pool=em.build_zones(B)
    raw=em.run(B,pool); sig=em.dedup(raw)
    # gan context
    for s in sig:
        s['mfe'],s['mae']=mfe_mae(B,s['i'],s['side'])
        s['div']=cvd_div(B,s['i'],s['side'])
        s['sess']=em.sess_of(s['dt'].hour*60+s['dt'].minute)
    print("="*100);print(f"NGHIEN CUU 28 ngay | tin hieu (sau gop) = {len(sig)}")

    # ---- Q1: MFE/MAE vs baseline ----
    print("\n[Q1] Entry co gia tri du bao? — MFE/MAE (tick, chan 2h)")
    pL=sum(s['side']=='LONG' for s in sig)/len(sig)
    def avg(a):return sum(a)/len(a) if a else 0
    print(f"  {'nhom':<26}{'n':>5}{'MFE':>7}{'MAE':>7}{'MFE/MAE':>9}")
    for nm,sub in [("TAT CA tin hieu",sig)]+[(f"scen {sc}",[s for s in sig if s['scen']==sc]) for sc in ['1 pha&hoi len','1 pha&hoi xuong','2 cham&dao xuong','2 cham&dao len']]:
        if sub:
            mf=avg([s['mfe'] for s in sub]);ma=avg([s['mae'] for s in sub])
            print(f"  {nm:<26}{len(sub):>5}{mf:>7.0f}{ma:>7.0f}{(mf/ma if ma else 0):>9.2f}")
    # baseline ngau nhien cung ty le phia
    base=[]
    idxs=random.sample(range(30,len(B)-H_MFE),3000)
    for i in idxs:
        side='LONG' if random.random()<pL else 'SHORT'
        mf,ma=mfe_mae(B,i,side); base.append((mf,ma))
    bmf=avg([x[0] for x in base]);bma=avg([x[1] for x in base])
    print(f"  {'BASELINE (3000 ngau nhien)':<26}{len(base):>5}{bmf:>7.0f}{bma:>7.0f}{(bmf/bma if bma else 0):>9.2f}")
    print(f"  -> tin hieu chi co edge NEU MFE>baseline VA/HOAC MAE<baseline VA MFE/MAE>1")

    # ---- Q2: multi-target ----
    print("\n[Q2] 3R co tham? — WR + ky vong o cac target (SL = da dat, med 2d)")
    print(f"  {'target':<8}{'n':>5}{'TP':>5}{'WR':>7}{'exp(R)':>9}")
    for rm in [1.0,1.5,2.0,3.0]:
        n,tp,wr,exp=wr_exp(sig,B,rm)
        need=1/(1+rm)
        print(f"  {rm:>4.1f}R  {n:>5}{tp:>5}{wr:>7.0%}{exp:>+9.2f}   (hoa von WR={need:.0%})")

    # ---- Q4: SL width sweep ----
    print("\n[Q4] Do rong SL (TP=3xSL co dinh):")
    print(f"  {'SL(d)':<7}{'n':>5}{'WR':>7}{'exp(R)':>9}")
    for w in [20,30,40,60]:
        n,wr,exp=wr_exp_fixedSL(sig,B,w)
        print(f"  {w/10:>4.1f}  {n:>5}{wr:>7.0%}{exp:>+9.2f}")

    # ---- Q3: subset cuts (o target tot nhat = tim sau Q2; tam dung 2R) ----
    TG=2.0
    print(f"\n[Q3] Subset nao co edge? (target {TG:.0f}R, SL da dat, hoa von WR={1/(1+TG):.0%})")
    print(f"  {'subset':<34}{'n':>5}{'WR':>7}{'exp(R)':>9}")
    cuts=[
        ("TAT CA",sig),
        ("Scenario 1 (pha&hoi)",[s for s in sig if s['scen'].startswith('1')]),
        ("Scenario 2 (cham&dao)",[s for s in sig if s['scen'].startswith('2')]),
        ("Scen1 + climax tim",[s for s in sig if s['scen'].startswith('1') and s['climax']]),
        ("Scen1 + bias-aligned",[s for s in sig if s['scen'].startswith('1') and ((s['side']=='LONG')==(s['bias']>=0))]),
        ("Scen2 + phan ky CVD",[s for s in sig if s['scen'].startswith('2') and s['div']]),
        ("Scen2 + climax tim",[s for s in sig if s['scen'].startswith('2') and s['climax']]),
        ("Confluence >=2",[s for s in sig if s['confl']>=2]),
        ("Confluence >=2 + climax",[s for s in sig if s['confl']>=2 and s['climax']]),
        ("Phien MY (US)",[s for s in sig if s['sess']=='MY']),
        ("Phien AU (Au)",[s for s in sig if s['sess']=='AU']),
        ("Phien A (A)",[s for s in sig if s['sess']=='A']),
        ("co phan ky CVD (moi phia)",[s for s in sig if s['div']]),
        ("VWAP zone",[s for s in sig if 'VWAP' in s['zone'] or any('VWAP' in z for z in s['zones'])]),
    ]
    for nm,sub in cuts:
        if len(sub)>=8:
            n,tp,wr,exp=wr_exp(sub,B,TG)
            flag=" <== duong" if exp>0.05 else ""
            print(f"  {nm:<34}{n:>5}{wr:>7.0%}{exp:>+9.2f}{flag}")
        else:
            print(f"  {nm:<34}{len(sub):>5}   (qua it)")

    # ---- Q3b: cross cac filter tot nhat o 2R va 3R ----
    print(f"\n[Q3b] Vai to hop chat (2R va 3R):")
    combos=[
        ("Scen1 + confluence>=2",[s for s in sig if s['scen'].startswith('1') and s['confl']>=2]),
        ("Scen1 + climax + bias",[s for s in sig if s['scen'].startswith('1') and s['climax'] and ((s['side']=='LONG')==(s['bias']>=0))]),
        ("Scen2 + div + confluence>=2",[s for s in sig if s['scen'].startswith('2') and s['div'] and s['confl']>=2]),
        ("Scen2 + div + climax",[s for s in sig if s['scen'].startswith('2') and s['div'] and s['climax']]),
        ("confluence>=2 + div",[s for s in sig if s['confl']>=2 and s['div']]),
    ]
    for nm,sub in combos:
        if len(sub)>=6:
            n2,_,wr2,e2=wr_exp(sub,B,2.0); n3,_,wr3,e3=wr_exp(sub,B,3.0)
            print(f"  {nm:<32} n={len(sub):>3} | 2R WR{wr2:.0%} exp{e2:+.2f} | 3R WR{wr3:.0%} exp{e3:+.2f}")
        else:
            print(f"  {nm:<32} n={len(sub):>3}  (qua it)")
    print("="*100);print("DONE")

main()
