#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROTOTYPE FIX B — KB1 pha&hoi: cho phep nhip hoi CHUI LAI VAO range ma khong huy setup.
Hien tai: dong nen tro lai qua vung (>2 tick) => state='idle' => mat setup.
User (anh 6): "pha range, hoi lai YEU van loanh quanh range, ko but han len" -> van la setup SHORT.

Quet KILL_BUF (tick): chi huy khi close vuot qua vung nguoc huong pha > KILL_BUF tick.
Cung quet RETEST_BARS.  Do rieng nhanh KB1.
"""
import sys
from datetime import timedelta
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
_o = em.load
em.load = lambda p, sep=',': _o('fp-m1-6-month.csv' if p == 'fp-m1-1-month-data.csv' else p, sep)
em.SL_MIN_T = 35; em.SL_MAX_T = 60; em.RR = 3.0
CONFL_TOL = 7

def run(B, pool, KILL_T, RETEST_BARS, HOLD_T, need_color):
    raw = []
    BUF_T = em.BUF_T
    vw = dict(price=0.0, kind="VWAP", strength=64, ready=B[0]['dt'],
              expire=B[-1]['dt']+timedelta(days=1), is_vwap=True)
    Z = [dict(z) for z in pool] + [vw]
    for z in Z: z.update(state='idle', brk_bar=-999, cool=-999, prev_rel=None)
    for i in range(em.VSA_MA+2, len(B)):
        b = B[i]; px = b['c']; vw['price'] = b['vwap']
        act = [z for z in Z if z['ready'] <= b['dt'] <= z['expire']]
        if not em.gate(b):
            for z in act: z['prev_rel'] = 'above' if px > z['price'] else 'below'
            continue
        for z in act:
            zp = z['price']; dist = abs(px-zp)/TICK
            rel = 'above' if b['c'] > zp+BUF_T*TICK else 'below' if b['c'] < zp-BUF_T*TICK else 'in'
            if (dist > em.ARM_DIST_T and z['state'] == 'idle') or i-z['cool'] < em.COOLDOWN_BARS:
                z['prev_rel'] = rel; continue
            zlo = zp-BUF_T*TICK; zhi = zp+BUF_T*TICK
            bu = b['c'] > zhi and b['hi'] > zp and b['brat'] >= 0.5 and b['delta'] > 0 and b['vratio'] >= em.VSA_BREAK and z['prev_rel'] in ('below','in')
            bd = b['c'] < zlo and b['lo'] < zp and b['brat'] >= 0.5 and b['delta'] < 0 and b['vratio'] >= em.VSA_BREAK and z['prev_rel'] in ('above','in')
            if bu: z['state'] = 'broke_up'; z['brk_bar'] = i
            elif bd: z['state'] = 'broke_dn'; z['brk_bar'] = i
            if z['state'] == 'broke_up' and 0 < i-z['brk_bar'] <= RETEST_BARS:
                if b['c'] < zp - KILL_T*TICK: z['state'] = 'idle'
                elif b['lo'] <= zp+em.RETEST_TOL_T*TICK and b['lo'] >= zp-HOLD_T*TICK:
                    ok, w = em.long_sig(b)
                    if ok and (not need_color or b['c'] > b['o']):
                        if em._emit(raw, B, i, z, 'LONG', '1 pha&hoi len', min(b['lo'], zp), w, pool):
                            z['cool'] = i; z['state'] = 'idle'
            elif z['state'] == 'broke_dn' and 0 < i-z['brk_bar'] <= RETEST_BARS:
                if b['c'] > zp + KILL_T*TICK: z['state'] = 'idle'
                elif b['hi'] >= zp-em.RETEST_TOL_T*TICK and b['hi'] <= zp+HOLD_T*TICK:
                    ok, w = em.short_sig(b)
                    if ok and (not need_color or b['c'] < b['o']):
                        if em._emit(raw, B, i, z, 'SHORT', '1 pha&hoi xuong', max(b['hi'], zp), w, pool):
                            z['cool'] = i; z['state'] = 'idle'
            z['prev_rel'] = rel
    return raw

def stat(B, S):
    for s in S: s['o'], s['r'], _ = em.sim(B, s, 'tp3')
    dec = [s for s in S if s['o'] in ('TP','SL')]
    if not dec: return None
    return len(dec), sum(s['o'] == 'TP' for s in dec)/len(dec), sum(s['r'] for s in S), sum(s['r'] for s in S)/len(dec)

if __name__ == '__main__':
    B = em.load_m1(); pool = em.build_zones(B)
    def cc(t, p): return len({round(z['price']/TICK) for z in pool
                              if z['ready'] <= t <= z['expire'] and abs(z['price']-p)/TICK <= CONFL_TOL})
    print("KILL_T = so tick close duoc phep chui NGUOC lai qua vung ma KHONG huy setup")
    print(f"{'KILL':>5} {'RTB':>4} {'HOLD':>5} {'color':>6} | {'n':>3} {'WR':>6} {'tongR':>7} {'exp':>6}")
    for kill in (2, 6, 10, 15, 20, 30):
        for rtb in (12, 20):
            for hold in (0, 4):
                for nc in (False, True):
                    raw = run(B, pool, kill, rtb, hold, nc)
                    S = [s for s in em.dedup(raw) if cc(s['dt'], s['zp_break']) >= 2]
                    r = stat(B, S)
                    if r: print(f"{kill:>5} {rtb:>4} {hold:>5} {str(nc):>6} | {len(S):>3} {r[1]:>6.1%} {r[2]:>+7.1f} {r[3]:>+6.2f}")
                    else:  print(f"{kill:>5} {rtb:>4} {hold:>5} {str(nc):>6} | {len(S):>3}   -")
