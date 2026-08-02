#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROTOTYPE FIX A — "nen entry phai THUAN chieu; neu nen kich hoat NGUOC mau -> ARM, cho nen XAC NHAN".

So sanh 3 bien the tren cung bo tin hieu (gate hop luu>=2, SL floor 35t, cap 60t, RR=3):
  V0  = hien tai (vao ngay tai nen kich hoat, ke ca nen nguoc mau)
  V1  = BO thang cac lenh co nen kich hoat nguoc mau/doji
  V2  = nen nguoc mau -> ARM, cho toi W nen sau: nen THUAN mau + VSA>=1.2 + delta thuan chieu
        + chua pha vung  => vao tai close nen do (SL van neo theo day/dinh cua nen ARM)
"""
import sys, statistics as st
from datetime import timedelta
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK

USE_6M = True
if USE_6M:
    _o = em.load
    def L(p, sep=','):
        return _o('fp-m1-6-month.csv' if p == 'fp-m1-1-month-data.csv' else p, sep)
    em.load = L
em.SL_MIN_T = 35; em.SL_MAX_T = 60; em.RR = 3.0
CONFL_TOL = 7; W = 6

def col(b, side):
    c = 'up' if b['c'] > b['o'] else ('dn' if b['c'] < b['o'] else 'flat')
    if side == 'LONG': return 'THUAN' if c=='up' else ('NGUOC' if c=='dn' else 'DOJI')
    return 'THUAN' if c=='dn' else ('NGUOC' if c=='up' else 'DOJI')

def mk(B, pool, s, j):
    """dung lai signal moi tai nen j (nen xac nhan), giu anchor SL cu."""
    b = B[j]; side = s['side']; entry = b['c']
    anchor = s['anchor']
    if side == 'LONG':
        anchor = min(anchor, b['lo'])
        sl = min(anchor - em.SL_BUF_T*TICK, entry - em.SL_MIN_T*TICK); risk = (entry-sl)/TICK
    else:
        anchor = max(anchor, b['hi'])
        sl = max(anchor + em.SL_BUF_T*TICK, entry + em.SL_MIN_T*TICK); risk = (sl-entry)/TICK
    if risk <= 0 or risk > em.SL_MAX_T: return None
    r = risk*TICK
    n = dict(s); n.update(i=j, dt=b['dt'], entry=entry, sl=sl, risk_t=risk,
                          tp3=entry + em.RR*r if side=='LONG' else entry - em.RR*r,
                          tpx=entry + em.RR*r if side=='LONG' else entry - em.RR*r, rx=em.RR,
                          climax=b['vratio'] >= em.VSA_CLIMAX, vsa=b['vratio'])
    return n

def confirm(B, pool, s):
    """tim nen xac nhan trong W nen sau nen kich hoat."""
    side = s['side']; zp = s['zp_break']; i = s['i']
    for j in range(i+1, min(i+1+W, len(B))):
        b = B[j]
        if not em.gate(b): continue
        # huy neu dong xuyen qua vung nguoc huong lenh
        if side == 'LONG'  and b['c'] < zp - 2*TICK: return None
        if side == 'SHORT' and b['c'] > zp + 2*TICK: return None
        ok = (col(b, side) == 'THUAN' and b['vratio'] >= em.VSA_GATE
              and (b['delta'] > 0 if side == 'LONG' else b['delta'] < 0))
        if ok: return mk(B, pool, s, j)
    return None

def stat(B, S):
    for s in S: s['o'], s['r'], _ = em.sim(B, s, 'tp3')
    dec = [s for s in S if s['o'] in ('TP','SL')]
    if not dec: return None
    return len(dec), sum(s['o']=='TP' for s in dec)/len(dec), sum(s['r'] for s in S), sum(s['r'] for s in S)/len(dec)

def line(t, B, S):
    r = stat(B, S)
    print(f"  {t:<42} n={len(S):3} WR {r[1]:5.1%} tong {r[2]:+6.1f}R exp {r[3]:+5.2f}R" if r else f"  {t:<42} n={len(S)} -")

if __name__ == '__main__':
    B = em.load_m1(); pool = em.build_zones(B)
    sig = em.dedup(em.run(B, pool))
    def cc(t, p): return len({round(z['price']/TICK) for z in pool
                              if z['ready'] <= t <= z['expire'] and abs(z['price']-p)/TICK <= CONFL_TOL})
    G = [s for s in sig if cc(s['dt'], s['zp_break']) >= 2]
    for s in G:
        s['anchor'] = s['sl'] + em.SL_BUF_T*TICK if s['side']=='SHORT' else s['sl'] + em.SL_BUF_T*TICK
        # anchor thuc = sl +/- buf; tai tao dung dau
        s['anchor'] = (s['sl'] + em.SL_BUF_T*TICK) if s['side']=='LONG' else (s['sl'] - em.SL_BUF_T*TICK)
    good = [s for s in G if col(B[s['i']], s['side']) == 'THUAN']
    bad  = [s for s in G if col(B[s['i']], s['side']) != 'THUAN']
    print(f"tong {len(G)} | thuan {len(good)} | nguoc/doji {len(bad)}")
    print("="*100)
    line("V0 hien tai (tat ca)", B, G)
    line("V1 bo han nen nguoc/doji", B, good)
    conf = [c for c in (confirm(B, pool, s) for s in bad) if c]
    print(f"  ...trong {len(bad)} ca nguoc/doji, tim duoc nen xac nhan: {len(conf)}")
    line("     rieng phan cho-xac-nhan", B, conf)
    line("V2 = thuan + cho-xac-nhan", B, good + conf)
    print("-"*100)
    print("  [W quet]")
    for w in (2,3,4,6,8,12):
        globals()['W'] = w
        c2 = [c for c in (confirm(B, pool, s) for s in bad) if c]
        line(f"  W={w:<2} V2 tong", B, good + c2)
        line(f"     rieng xac nhan (n={len(c2)})", B, c2)
