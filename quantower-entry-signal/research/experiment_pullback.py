#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRACK B — kiem chung y tuong user: "nhip hoi phai ro rang, vua du, PHU HOP voi nhip pha;
entry vao tin hieu SAU nhip hoi thi gia di rat xa" -> loc theo DO SAU HOI (retracement).

Do cho MOI signal KB1 (pha&hoi):
  chan_pha = tu vung (zp) toi dinh pha (break_peak trong <=12 nen truoc entry)
  retrace  = (dinh_pha - day_hoi) / chan_pha       (LONG; SHORT doi xung)
    <=100%: gia GIU tren goc pha (hoi lanh manh) ; >100%: xuyen nguoc goc pha (pha HONG/dao chieu)
  xuyen_vung = gia hoi dam bao khong slice qua sau duoi/ tren vung
So WR + ky vong @1.5R va @3R giua cac nhom loc. Kiem tra 2 lenh user review co bi loc dung khong.
Cau hinh: SL floor 4 gia (shipped), cum>=2 (khop live).
"""
import sys, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
em.SL_MIN_T = 40; em.SL_MAX_T = 60; em.RR = 1.5; em.NEXTZONE_MINR = 2.0
CONFL_TOL = 7


def hit_target(B, i, side, sl_px, tp_px):
    for j in range(i + 1, len(B)):
        b = B[j]
        sl = (b['lo'] <= sl_px) if side == 'LONG' else (b['hi'] >= sl_px)
        tp = (b['hi'] >= tp_px) if side == 'LONG' else (b['lo'] <= tp_px)
        if sl: return 'SL'
        if tp: return 'TP'
    return 'open'


def cluster_of(pool, t, zp):
    seen = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= CONFL_TOL:
            seen.add(round(z['price'] / TICK))
    return len(seen)


def pullback_metrics(B, s, zp):
    i = s['i']; w = B[max(0, i - em.RETEST_BARS):i + 1]
    if s['side'] == 'LONG':
        peak = max(x['hi'] for x in w)
        low = B[i]['lo']
        leg = peak - zp
        retrace = (peak - low) / leg if leg > 0 else 9.9
        slice_beyond = (zp - low) / TICK          # >0: hoi xuyen DUOI vung (xau)
    else:
        trough = min(x['lo'] for x in w)
        hi = B[i]['hi']
        leg = zp - trough
        retrace = (hi - trough) / leg if leg > 0 else 9.9
        slice_beyond = (hi - zp) / TICK           # >0: hoi xuyen TREN vung (xau)
    return leg, retrace, slice_beyond


def evalsub(B, sub, rm):
    tp = sl = 0
    for s in sub:
        r = s['risk_t'] * TICK
        tpp = s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r
        o = hit_target(B, s['i'], s['side'], s['sl'], tpp)
        if o == 'TP': tp += 1
        elif o == 'SL': sl += 1
    n = tp + sl
    return n, tp, (tp / n if n else 0), ((tp * rm - sl) / n if n else 0)


B = em.load_m1(); pool = em.build_zones(B)
raw = em.run(B, pool)
for s in raw:
    s['cluster'] = cluster_of(pool, s['dt'], float(s['zone'].split()[-1]))
sig = em.dedup(raw)
for s in sig: s.setdefault('cluster', 1)
sig = [s for s in sig if s['cluster'] >= 2]              # khop live (cum>=2)
kb1 = [s for s in sig if s['scen'].startswith('1')]
for s in kb1:
    zp = float(s['zone'].split()[-1])
    s['leg'], s['retrace'], s['slice'] = pullback_metrics(B, s, zp)

print("=" * 100)
print(f"TRACK B — loc KB1 pha&hoi theo do sau hoi (cum>=2, SL floor 4 gia). n(KB1)={len(kb1)}")
print(f"  {'nhom loc':<40}{'n':>4} | {'1.5R WR/exp':>16} | {'3R WR/exp':>16}")
groups = [
    ("TAT CA KB1 (hien tai)", kb1),
    ("hoi <=100% chan pha (giu goc pha)", [s for s in kb1 if s['retrace'] <= 1.00]),
    ("hoi 38-100% (ro rang + khong dao)", [s for s in kb1 if 0.38 <= s['retrace'] <= 1.00]),
    ("hoi khong xuyen qua vung >3t", [s for s in kb1 if s['slice'] <= 3]),
    ("hoi<=100% VA khong xuyen vung>3t", [s for s in kb1 if s['retrace'] <= 1.00 and s['slice'] <= 3]),
    ("hoi>100% (pha HONG/dao) -> nen BO", [s for s in kb1 if s['retrace'] > 1.00]),
]
for lbl, sub in groups:
    if not sub:
        print(f"  {lbl:<40}{0:>4} | (rong)"); continue
    n1, t1, w1, e1 = evalsub(B, sub, 1.5)
    n3, t3, w3, e3 = evalsub(B, sub, 3.0)
    print(f"  {lbl:<40}{len(sub):>4} | {w1:>5.0%} {e1:>+6.2f}R    | {w3:>5.0%} {e3:>+6.2f}R")

# 2 lenh user review
print("\n  -- 2 lenh user review (retrace/slice) --")
for tag, day, hh, mm in [("LENH1", "07/23", 8, 3), ("LENH2", "07/23", 18, 20)]:
    m = [s for s in kb1 if s['dt'].strftime('%m/%d') == day and s['dt'].hour == hh and abs(s['dt'].minute - mm) <= 1]
    if m:
        s = m[0]
        keep = "GIU (hoi lanh manh)" if (s['retrace'] <= 1.0 and s['slice'] <= 3) else "BO (hoi xuyen goc pha/vung)"
        print(f"  {tag} {s['dt']:%H:%M} {s['side']} entry{s['entry']:.1f} zone{s['zone']}: "
              f"chan_pha {s['leg']:.1f} gia | retrace {100*s['retrace']:.0f}% | xuyen_vung {s['slice']:.1f}t -> {keep}")
    else:
        print(f"  {tag}: khong nam trong KB1 cum>=2")
print("=" * 100)

# ===== XUAT CSV doi chieu chart: moi KB1 + do sau hoi + ket qua =====
import csv


def mfe_R(B, s):
    i = s['i']; side = s['side']; e = s['entry']; r = s['risk_t'] * TICK; best = 0.0
    for j in range(i + 1, min(i + 601, len(B))):
        b = B[j]
        if side == 'LONG':
            best = max(best, b['hi'] - e)
            if b['lo'] <= s['sl']: break
        else:
            best = max(best, e - b['lo'])
            if b['hi'] >= s['sl']: break
    return best / r


path = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/trades_kb1_pullback.csv"
with open(path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['datetime', 'side', 'entry', 'zone', 'chan_pha_gia', 'retrace_%', 'xuyen_vung_tick',
                'giu/bo', 'MFE_R', 'out@1.5R', 'out@3R'])
    for s in sorted(kb1, key=lambda x: x['dt']):
        r = s['risk_t'] * TICK
        o15 = hit_target(B, s['i'], s['side'], s['sl'], s['entry'] + 1.5 * r if s['side'] == 'LONG' else s['entry'] - 1.5 * r)
        o30 = hit_target(B, s['i'], s['side'], s['sl'], s['entry'] + 3.0 * r if s['side'] == 'LONG' else s['entry'] - 3.0 * r)
        keep = 'GIU' if (s['retrace'] <= 1.0 and s['slice'] <= 3) else 'BO'
        w.writerow([s['dt'].strftime('%Y-%m-%d %H:%M'), s['side'], f"{s['entry']:.1f}", s['zone'],
                    f"{s['leg']:.1f}", f"{100*s['retrace']:.0f}", f"{s['slice']:.1f}", keep,
                    f"{mfe_R(B, s):.2f}", o15, o30])
print(f"  -> CSV doi chieu chart: {path}\n")

# ===== them mau tu 6 THANG (Jun-Jul thanh khoan that; Jan-Apr HD xa gan chet) =====
import types
stub = types.ModuleType('research')
stub.hit_target = hit_target; stub.mfe_mae = lambda *a, **k: (0, 0); stub.H_MFE = 120
sys.modules['research'] = stub
src = open("/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/backtest_6month.py").read().replace("\nmain()\n", "\n")
bt = types.ModuleType("bt6"); bt.__dict__.update(sys=sys, em=em, TICK=TICK)
exec(compile(src, "bt6", "exec"), bt.__dict__)
B6 = bt.load_m1_6m(); pool6 = bt.build_zones_6m(B6)
raw6 = em.run(B6, pool6)
for s in raw6: s['cluster'] = cluster_of(pool6, s['dt'], float(s['zone'].split()[-1]))
sig6 = em.dedup(raw6)
for s in sig6: s.setdefault('cluster', 1)
sig6 = [s for s in sig6 if s['cluster'] >= 2]
kb1_6 = [s for s in sig6 if s['scen'].startswith('1')]
for s in kb1_6:
    zp = float(s['zone'].split()[-1]); s['leg'], s['retrace'], s['slice'] = pullback_metrics(B6, s, zp)
print(f"6 THANG (chu yeu Jun-Jul long) — KB1 cum>=2, n={len(kb1_6)}")
print(f"  {'nhom loc':<40}{'n':>4} | {'1.5R WR/exp':>16} | {'3R WR/exp':>16}")
for lbl, sub in [("TAT CA KB1", kb1_6),
                 ("hoi<=100% + khong xuyen vung>3t", [s for s in kb1_6 if s['retrace'] <= 1.0 and s['slice'] <= 3]),
                 ("hoi>100% (pha hong) -> BO", [s for s in kb1_6 if s['retrace'] > 1.0])]:
    if not sub:
        print(f"  {lbl:<40}{0:>4} | (rong)"); continue
    n1, t1, w1, e1 = evalsub(B6, sub, 1.5); n3, t3, w3, e3 = evalsub(B6, sub, 3.0)
    print(f"  {lbl:<40}{len(sub):>4} | {w1:>5.0%} {e1:>+6.2f}R    | {w3:>5.0%} {e3:>+6.2f}R")
print("=" * 100)
