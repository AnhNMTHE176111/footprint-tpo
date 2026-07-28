#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RESEARCH WINRATE — tim tran WR that su dat duoc o RR co dinh, va duong bien WR<->so lenh.
User muon: TANG CA winrate LAN so lenh, target 80% WR @ RR1.5.
Cach: chay vai BASE config nang (run+dedup), roi HAU-LOC (climax/kich ban/zone-strength/vwap)
bang Python (re) de ra NHIEU to hop, sap xep theo WR."""
import entry_dxfeed as E
import statistics as st

E.B=E.load_m1();E.VOLFLOOR_AUTO=E.calc_volfloor(E.B);pool=E.build_zones(E.B);E.USE_DELTA=False
MONTHS=('2026-05','2026-06','2026-07')

def base_sigs(C):
    C=E.prep(dict(C))
    raw=E.run(E.B,pool,C)
    if C['SWEEP_ON']:raw=raw+E.scan_sweep(E.B,pool,C)
    sig=E.dedup(raw,pool,C)
    sig=[s for s in sig if s['ym'] in MONTHS]
    for s in sig:
        s['o'],s['r']=E.sim(E.B,s,'tp3',C['RR'])
    return sig

def stat(SS):
    settled=[s for s in SS if s['o'] in ('TP','SL')]
    if not settled:return (len(SS),0,0.0,0.0)
    tp=sum(s['o']=='TP' for s in settled)
    R=sum(s['r'] for s in SS)
    return (len(settled),tp,tp/len(settled),R)

print("Chay cac BASE (nang)...");
BASES={
 'confl2'         : base_sigs(E.make(MIN_CONFL=2)),
 'confl3'         : base_sigs(E.make(MIN_CONFL=3)),
 'confl4'         : base_sigs(E.make(MIN_CONFL=4)),
 'confl2+vwapMom' : base_sigs(E.make(MIN_CONFL=2,VWAP_ON=True,VWAP_KB1ONLY=True,VWAP_MARGIN=2.0)),
 'confl3+vwapMom' : base_sigs(E.make(MIN_CONFL=3,VWAP_ON=True,VWAP_KB1ONLY=True,VWAP_MARGIN=2.0)),
}

# hau-loc
def flt(sigs,**k):
    out=list(sigs)
    if k.get('climax'):out=[s for s in out if s['climax']]
    if k.get('scen'):out=[s for s in out if any(s['scen'].startswith(p) for p in k['scen'])]
    if k.get('zstr'):out=[s for s in out if s['zstr']>=k['zstr']]
    if k.get('side'):out=[s for s in out if s['side']==k['side']]
    return out

rows=[]
for bname,bsig in BASES.items():
    combos={
      'all':{}, 'climax':{'climax':1}, 'zoneMANH(>=66)':{'zstr':66},
      'chi cham&dao':{'scen':['2']}, 'chi pha&hoi':{'scen':['1']},
      'cham&dao+climax':{'scen':['2'],'climax':1},
      'climax+zoneMANH':{'climax':1,'zstr':66},
      'cham&dao xuong':{'scen':['2 cham&dao xuong']},
    }
    for cname,kw in combos.items():
        n,tp,wr,R=stat(flt(bsig,**kw))
        rows.append((bname,cname,n,wr,R))

print("\n"+"="*90)
print(f"{'BASE':<16}{'LOC':<20}{'n':>4}{'WR':>7}{'tongR':>8}{'exp':>7}")
print("-"*90)
# sap xep theo WR giam dan, chi giu n>=8 cho co nghia
for r in sorted([x for x in rows if x[2]>=8], key=lambda x:-x[3]):
    b,c,n,wr,R=r
    print(f"{b:<16}{c:<20}{n:>4}{wr*100:>6.0f}%{R:>+8.0f}{R/n if n else 0:>+7.2f}")

print("\n### DUONG BIEN WR<->so lenh (loc dan): confl2 all -> loc manh dan")
for kw,lbl in [({}, 'confl2 tat ca'),({'zstr':66},'+zone manh'),({'climax':1},'+climax tim'),
               ({'climax':1,'zstr':66},'+climax+zone manh')]:
    n,tp,wr,R=stat(flt(BASES['confl2'],**kw))
    print(f"  {lbl:<26} n={n:>3} WR {wr*100:>3.0f}% tong {R:+.0f}R")
for kw,lbl in [({}, 'confl3 tat ca'),({'climax':1},'confl3+climax')]:
    n,tp,wr,R=stat(flt(BASES['confl3'],**kw))
    print(f"  {lbl:<26} n={n:>3} WR {wr*100:>3.0f}% tong {R:+.0f}R")

print("\n### RR THAP HON co keo WR len 80% khong? (confl2 all)")
for rr in (0.6,0.8,1.0,1.2,1.5):
    C=E.prep(dict(E.make(RR=rr)))
    raw=E.run(E.B,pool,C);sig=[s for s in E.dedup(raw,pool,C) if s['ym'] in MONTHS]
    for s in sig:s['o'],s['r']=E.sim(E.B,s,'tp3',rr)
    n,tp,wr,R=stat(sig)
    print(f"  RR {rr:>3}: n={n:>3} WR {wr*100:>3.0f}% tong {R:+.0f}R exp {R/n if n else 0:+.2f}R")
