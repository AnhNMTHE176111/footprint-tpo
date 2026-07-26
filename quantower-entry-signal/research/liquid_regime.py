#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiem confluence>=2 tren cac VUNG THANH KHOAN cua GCQ26 (loc theo ngay).
Ly do: Jan-Apr la hop dong xa gan nhu chet (vol median 1-2) -> khong dai dien cho live.
Chi Jun-Jul (front/near month) moi dai dien. Muc tieu: doc edge SACH tren data thanh khoan.
"""
import sys, types
from datetime import datetime
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
import research as R
TICK = em.TICK

# nap ham load/zones tu backtest_6month.py (bo dong main())
src = open("/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/backtest_6month.py").read()
src = src.replace("\nmain()\n", "\n")
bt = types.ModuleType("bt6")
bt.__dict__.update(sys=sys, em=em, R=R, TICK=TICK)
exec(compile(src, "bt6", "exec"), bt.__dict__)

B = bt.load_m1_6m(); pool = bt.build_zones_6m(B)
sig = em.dedup(em.run(B, pool))


def wr(sigs, rm):
    tp = sl = 0
    for s in sigs:
        r = s['risk_t'] * TICK
        tpp = s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r
        o = R.hit_target(B, s['i'], s['side'], s['sl'], tpp)
        if o == 'TP': tp += 1
        elif o == 'SL': sl += 1
    n = tp + sl
    return n, (tp / n if n else 0), ((tp * rm - sl) / n if n else 0)


hdr_win = "cua so"; hdr = f"  {hdr_win:<24}{'n_all':>6}{'n_c2':>6} | 2R WR  2R exp | 3R WR  3R exp | c1 2Rexp"
print("=" * 92)
print("CONFLUENCE>=2 tren cac VUNG THANH KHOAN (loc theo ngay bat dau):")
print(hdr)
wins = [("Tat ca 6 thang", datetime(2026, 1, 1)), (">= 05/15 (bat dau lỏng)", datetime(2026, 5, 15)),
        (">= 06/01 (Jun-Jul)", datetime(2026, 6, 1)), (">= 07/01 (Jul front-month)", datetime(2026, 7, 1))]
for lbl, cut in wins:
    s2 = [s for s in sig if s['dt'] >= cut]
    c2 = [s for s in s2 if s['confl'] >= 2]; c1 = [s for s in s2 if s['confl'] == 1]
    if len(c2) >= 6:
        n2, w2, e2 = wr(c2, 2.0); n3, w3, e3 = wr(c2, 3.0); _, _, ec1 = wr(c1, 2.0)
        print(f"  {lbl:<24}{len(s2):>6}{len(c2):>6} | {w2:>4.0%} {e2:>+6.2f} | {w3:>4.0%} {e3:>+6.2f} | {ec1:>+7.2f}")
    else:
        print(f"  {lbl:<24}{len(s2):>6}{len(c2):>6}  (c2 qua it)")

# tan suat + scenario tren Jun-Jul
jul = [s for s in sig if s['dt'] >= datetime(2026, 7, 1) and s['confl'] >= 2]
dj = len(set(s['dt'].date() for s in sig if s['dt'] >= datetime(2026, 7, 1)))
print(f"\n  Jul: confluence>=2 = {len(jul)} lenh / {dj} ngay = {len(jul)/max(dj,1):.1f} lenh/ngay")
jj = [s for s in sig if s['dt'] >= datetime(2026, 6, 1) and s['confl'] >= 2]
for nm, f in [("scen1 pha&hoi", lambda s: s['scen'].startswith('1')),
              ("scen2 cham&dao", lambda s: s['scen'].startswith('2'))]:
    sub = [s for s in jj if f(s)]
    if len(sub) >= 6:
        n2, w2, e2 = wr(sub, 2.0); n3, w3, e3 = wr(sub, 3.0)
        print(f"  Jun-Jul {nm:<16} n={len(sub):>3} | 2R WR{w2:.0%} exp{e2:+.2f} | 3R WR{w3:.0%} exp{e3:+.2f}")
    else:
        print(f"  Jun-Jul {nm:<16} n={len(sub):>3}  (it)")
print("=" * 92)
