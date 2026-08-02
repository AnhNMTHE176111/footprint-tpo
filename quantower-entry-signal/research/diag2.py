#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DIAG 2 — them GATE HOP LUU >=2 (giong C# ClusterCount, tol 7 tick, khong ke VWAP),
roi tach theo mau nen entry. Cau hinh giong live: SL floor 35 tick, cap 60, RR=3."""
import sys, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
CONFL_TOL = 7

def cluster_count(pool, t, price):
    seen = set()
    for z in pool:
        if not (z['ready'] <= t <= z['expire']): continue
        if abs(z['price'] - price) / TICK <= CONFL_TOL:
            seen.add(round(z['price'] / TICK))
    return len(seen)

def color_of(b, side):
    c = 'up' if b['c'] > b['o'] else ('dn' if b['c'] < b['o'] else 'flat')
    if side == 'LONG':  return 'THUAN' if c=='up' else ('NGUOC' if c=='dn' else 'DOJI')
    return 'THUAN' if c=='dn' else ('NGUOC' if c=='up' else 'DOJI')

def stat(B, S):
    for s in S: s['o'], s['r'], _ = em.sim(B, s, 'tp3')
    dec = [s for s in S if s['o'] in ('TP','SL')]
    if not dec: return None
    tp = sum(s['o']=='TP' for s in dec)
    return len(dec), tp/len(dec), sum(s['r'] for s in S), sum(s['r'] for s in S)/len(dec)

def line(tag, B, S):
    r = stat(B, S)
    print(f"  {tag:<34} n={len(S):3} dec={r[0]:3} WR {r[1]:5.1%} tong {r[2]:+6.1f}R exp {r[3]:+5.2f}R" if r else f"  {tag:<34} n={len(S)} (khong du)")

if __name__ == '__main__':
    em.SL_MIN_T = 35; em.SL_MAX_T = 60; em.RR = 3.0
    B = em.load_m1(); pool = em.build_zones(B)
    sig = em.dedup(em.run(B, pool))
    print(f"raw sau dedup = {len(sig)}")
    G = [s for s in sig if cluster_count(pool, s['dt'], s['zp_break']) >= 2]
    print(f"sau gate hop luu>=2 = {len(G)}   (live 7/17-7/31 co ~11 lenh -> co ve khop bac do)")
    print("="*95)
    line("TAT CA", B, G)
    for k in ['THUAN','NGUOC','DOJI']:
        line(f"mau nen entry = {k}", B, [s for s in G if color_of(B[s['i']], s['side'])==k])
    line("BO NGUOC+DOJI (chi giu THUAN)", B, [s for s in G if color_of(B[s['i']], s['side'])=='THUAN'])
    print("-"*95)
    for sc in sorted(set(s['scen'] for s in G)):
        sub = [s for s in G if s['scen']==sc]
        line(f"{sc}", B, sub)
        for k in ['THUAN','NGUOC','DOJI']:
            g = [s for s in sub if color_of(B[s['i']], s['side'])==k]
            if g: line(f"   -> {k}", B, g)
    print("-"*95)
    # chi climax
    C = [s for s in G if s['climax']]
    line("CHI climax(tim)", B, C)
    line("   climax & THUAN", B, [s for s in C if color_of(B[s['i']], s['side'])=='THUAN'])
    line("   climax & NGUOC", B, [s for s in C if color_of(B[s['i']], s['side'])=='NGUOC'])
