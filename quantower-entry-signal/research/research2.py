#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIEM CHONG OVERFIT cho phat hien "confluence >=2 co edge".
1. Don dieu theo bac confluence (1 / >=2 / >=3): edge phai TANG theo confluence moi dang tin.
2. Chia doi 28 ngay (nua dau vs nua sau): confluence>=2 phai DUONG o CA 2 nua.
3. MFE/MAE cua confluence>=2 vs baseline (phai >1 va > baseline).
4. Trong confluence>=2: scen1 vs scen2, va do rong SL.
"""
import sys, random, statistics as st
sys.path.insert(0,"/tmp/claude-1000/-home-asl86-Documents-footprint-tpo/55fa089c-afb3-4cf9-bca4-58241a901028/scratchpad")
import entry_month as em, research as R
TICK=em.TICK; random.seed(7)

def wr_exp(sigs,B,rmult):
    tp=sl=0
    for s in sigs:
        r=s['risk_t']*TICK
        tpp=s['entry']+rmult*r if s['side']=='LONG' else s['entry']-rmult*r
        o=R.hit_target(B,s['i'],s['side'],s['sl'],tpp)
        if o=='TP':tp+=1
        elif o=='SL':sl+=1
    n=tp+sl
    return n,(tp/n if n else 0),((tp*rmult-sl)/n if n else 0)

def main():
    B=em.load_m1(); pool=em.build_zones(B)
    raw=em.run(B,pool); sig=em.dedup(raw)
    for s in sig:
        s['mfe'],s['mae']=R.mfe_mae(B,s['i'],s['side'])
    mid=B[len(B)//2]['dt']
    print("="*96)
    print(f"n tin hieu={len(sig)} | moc chia doi = {mid:%m/%d %H:%M}")

    # 1) don dieu theo confluence
    print("\n[1] Don dieu theo bac confluence (SL da dat):")
    print(f"  {'confluence':<14}{'n':>5} | {'2R WR':>6}{'2R exp':>8} | {'3R WR':>6}{'3R exp':>8}")
    for nm,f in [("=1",lambda s:s['confl']==1),(">=2",lambda s:s['confl']>=2),(">=3",lambda s:s['confl']>=3)]:
        sub=[s for s in sig if f(s)]
        if len(sub)>=6:
            n2,w2,e2=wr_exp(sub,B,2.0); n3,w3,e3=wr_exp(sub,B,3.0)
            print(f"  {nm:<14}{len(sub):>5} | {w2:>6.0%}{e2:>+8.2f} | {w3:>6.0%}{e3:>+8.2f}")
        else: print(f"  {nm:<14}{len(sub):>5}  (qua it)")

    # 2) chia doi
    print("\n[2] Chia doi 28 ngay — confluence>=2 co giu o CA 2 nua?")
    c2=[s for s in sig if s['confl']>=2]
    h1=[s for s in c2 if s['dt']<mid]; h2=[s for s in c2 if s['dt']>=mid]
    print(f"  {'nua':<10}{'n':>5} | {'2R WR':>6}{'2R exp':>8} | {'3R WR':>6}{'3R exp':>8}")
    for nm,sub in [("nua dau",h1),("nua sau",h2)]:
        if sub:
            n2,w2,e2=wr_exp(sub,B,2.0); n3,w3,e3=wr_exp(sub,B,3.0)
            print(f"  {nm:<10}{len(sub):>5} | {w2:>6.0%}{e2:>+8.2f} | {w3:>6.0%}{e3:>+8.2f}")
    # doi chung: confluence==1 chia doi
    print("  (doi chung confluence==1:)")
    c1=[s for s in sig if s['confl']==1]
    for nm,sub in [("nua dau",[s for s in c1 if s['dt']<mid]),("nua sau",[s for s in c1 if s['dt']>=mid])]:
        n2,w2,e2=wr_exp(sub,B,2.0); print(f"  {nm:<10}{len(sub):>5} | {w2:>6.0%}{e2:>+8.2f} |")

    # 3) MFE/MAE confluence>=2 vs baseline
    print("\n[3] MFE/MAE confluence>=2 vs baseline:")
    def avg(a):return sum(a)/len(a) if a else 0
    mf=avg([s['mfe'] for s in c2]); ma=avg([s['mae'] for s in c2])
    pL=sum(s['side']=='LONG' for s in c2)/len(c2)
    base=[]
    for i in random.sample(range(30,len(B)-R.H_MFE),3000):
        side='LONG' if random.random()<pL else 'SHORT'; base.append(R.mfe_mae(B,i,side))
    bmf=avg([x[0] for x in base]); bma=avg([x[1] for x in base])
    print(f"  confluence>=2 : MFE {mf:.0f} MAE {ma:.0f} ratio {mf/ma:.2f}")
    print(f"  baseline      : MFE {bmf:.0f} MAE {bma:.0f} ratio {bmf/bma:.2f}")

    # 4) trong confluence>=2: scen + SL width
    print("\n[4] Trong confluence>=2:")
    for nm,sub in [("scen1 (pha&hoi)",[s for s in c2 if s['scen'].startswith('1')]),
                   ("scen2 (cham&dao)",[s for s in c2 if s['scen'].startswith('2')])]:
        if len(sub)>=6:
            n2,w2,e2=wr_exp(sub,B,2.0); n3,w3,e3=wr_exp(sub,B,3.0)
            print(f"  {nm:<18}{len(sub):>4} | 2R WR{w2:.0%} exp{e2:+.2f} | 3R WR{w3:.0%} exp{e3:+.2f}")
        else: print(f"  {nm:<18}{len(sub):>4}  (qua it)")
    print("  SL width (confluence>=2, TP=3xSL):")
    for w in [20,30,40,60]:
        n,wr,e=R.wr_exp_fixedSL(c2,B,w); print(f"    SL {w/10:.0f}d  n={n:>3} WR{wr:.0%} exp{e:+.2f}")

    # 5) confluence>=2 lich su gio phien + so lenh/ngay
    days=len(set(s['dt'].date() for s in sig))
    print(f"\n[5] Tan suat: confluence>=2 = {len(c2)} lenh / {days} ngay = {len(c2)/days:.1f} lenh/ngay (chon loc hon nhieu)")
    print("="*96);print("DONE")

main()
