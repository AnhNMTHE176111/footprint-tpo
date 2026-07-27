#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THONG KE cau hinh DANG CHAY (default shipped): cum>=2 (tol7, loai VWAP) + SL floor4/cap6 + RR1.5,
KB1 pha&hoi + KB2 cham&dao, KB3/KB4 TAT. Chay 1 thang + 6 thang. Xuat file danh sach lenh.
Win/Loss = cham TP1 (1.5R) truoc SL (khop panel indicator).
"""
import sys, csv, types, statistics as st
from datetime import datetime
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em, research as R
TICK = em.TICK
DIRR = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/"

# ---- ap cau hinh SHIPPED ----
em.SL_MIN_T = 40      # SL san 4d
em.SL_MAX_T = 60      # SL tran 6d
em.RR = 1.5           # RR muc tieu (TP1)
em.NEXTZONE_MINR = 2.0
CONFL_TOL = 7         # ConfluenceTol
RRV = 1.5


def cluster_of(pool, t, zprice):
    seen = set()
    for z in pool:            # pool KHONG gom VWAP (khop C# loai IsVwap)
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zprice) / TICK <= CONFL_TOL:
            seen.add(round(z['price'] / TICK))
    return len(seen)


def build_signals(B, pool):
    raw = em.run(B, pool)
    for s in raw:
        s['cluster'] = cluster_of(pool, s['dt'], float(s['zone'].split()[-1]))
    sig = em.dedup(raw)
    for s in sig:
        s.setdefault('cluster', 1)
    sig = [s for s in sig if s['cluster'] >= 2]     # GATE cum>=2 (shipped)
    # ket qua: cham TP1(1.5R) truoc SL
    for s in sig:
        r = s['risk_t'] * TICK
        tp1 = s['entry'] + RRV * r if s['side'] == 'LONG' else s['entry'] - RRV * r
        s['tp1'] = tp1
        o = R.hit_target(B, s['i'], s['side'], s['sl'], tp1)
        s['out'] = o if o else 'open'
        s['R'] = RRV if o == 'TP' else (-1.0 if o == 'SL' else 0.0)
        s['scenN'] = 'KB1 pha&hoi' if s['scen'].startswith('1') else 'KB2 cham&dao'
    return sig


def summarize(sig, label, ndays):
    closed = [s for s in sig if s['out'] in ('TP', 'SL')]
    tp = sum(s['out'] == 'TP' for s in sig)
    sl = sum(s['out'] == 'SL' for s in sig)
    op = sum(s['out'] == 'open' for s in sig)
    totR = sum(s['R'] for s in sig)
    wr = tp / len(closed) if closed else 0
    exp = totR / len(closed) if closed else 0
    print(f"\n{'='*78}\n{label}")
    print(f"  Tong tin hieu: {len(sig)}  ({len(sig)/max(ndays,1):.1f}/ngay, {ndays} ngay giao dich)")
    print(f"  Ket qua @TP1(1.5R):  WIN {tp}  |  LOSS {sl}  |  chua dong {op}")
    print(f"  Win-rate: {wr:.0%}   |   Tong: {totR:+.1f}R   |   Ky vong: {exp:+.2f}R/lenh")
    # theo kich ban
    print(f"  --- Theo kich ban ---")
    for sc in ['KB1 pha&hoi', 'KB2 cham&dao']:
        g = [s for s in sig if s['scenN'] == sc]; gc = [s for s in g if s['out'] in ('TP', 'SL')]
        gtp = sum(s['out'] == 'TP' for s in g)
        if g:
            print(f"    {sc:<14}: {len(g):>3} lenh | WIN {gtp} LOSS {sum(s['out']=='SL' for s in g)} | "
                  f"WR {gtp/len(gc)*100 if gc else 0:>3.0f}% | {sum(s['R'] for s in g):+.1f}R")
    # theo huong
    print(f"  --- Theo huong ---")
    for sd in ['LONG', 'SHORT']:
        g = [s for s in sig if s['side'] == sd]; gc = [s for s in g if s['out'] in ('TP', 'SL')]
        gtp = sum(s['out'] == 'TP' for s in g)
        if g:
            print(f"    {sd:<6}: {len(g):>3} lenh | WIN {gtp} LOSS {sum(s['out']=='SL' for s in g)} | WR {gtp/len(gc)*100 if gc else 0:>3.0f}%")
    # SL trung binh + cluster
    print(f"    SL trung vi: {st.median([s['risk_t'] for s in sig])/10:.1f}d | cluster tb: {st.mean([s['cluster'] for s in sig]):.1f}")
    return sig


def dump_csv(sig, path):
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['datetime', 'side', 'scenario', 'entry', 'SL', 'TP1(1.5R)', 'risk_d', 'cluster', 'VSA', 'outcome', 'R'])
        for s in sorted(sig, key=lambda x: x['dt']):
            w.writerow([s['dt'].strftime('%Y-%m-%d %H:%M'), s['side'], s['scenN'], f"{s['entry']:.1f}",
                        f"{s['sl']:.1f}", f"{s['tp1']:.1f}", f"{s['risk_t']/10:.1f}", s['cluster'],
                        f"{s['vsa']:.1f}", s['out'], f"{s['R']:+.1f}"])
    print(f"  -> danh sach day du: {path}")


def print_list(sig, maxrows=999):
    print(f"  {'ngay gio':<17}{'huong':<6}{'kich ban':<14}{'entry':>7}{'SL':>7}{'TP1':>7}{'risk':>5}{'cl':>3}{'VSA':>5}  {'KQ':<4}{'R':>5}")
    for s in sorted(sig, key=lambda x: x['dt'])[:maxrows]:
        mk = 'WIN ' if s['out'] == 'TP' else ('LOSS' if s['out'] == 'SL' else 'open')
        print(f"  {s['dt']:%m/%d %H:%M}    {s['side']:<6}{s['scenN']:<14}{s['entry']:>7.1f}{s['sl']:>7.1f}{s['tp1']:>7.1f}"
              f"{s['risk_t']/10:>4.1f}d{s['cluster']:>3}{s['vsa']:>5.1f}  {mk:<4}{s['R']:>+5.1f}")


# ============ 1 THANG ============
B1 = em.load_m1(); pool1 = em.build_zones(B1)
nd1 = len(set(b['dt'].date() for b in B1))
sig1 = build_signals(B1, pool1)
summarize(sig1, "1 THANG (fp-m1-1-month, 6/26 -> 7/25/2026)", nd1)
dump_csv(sig1, DIRR + "trades_1month.csv")
print("\n  --- DANH SACH DAY DU 1 THANG ---")
print_list(sig1)

# ============ 6 THANG ============
src = open(DIRR + "backtest_6month.py").read().replace("\nmain()\n", "\n")
bt = types.ModuleType("bt6"); bt.__dict__.update(sys=sys, em=em, R=R, TICK=TICK)
exec(compile(src, "bt6", "exec"), bt.__dict__)
B6 = bt.load_m1_6m(); pool6 = bt.build_zones_6m(B6)
nd6 = len(set(b['dt'].date() for b in B6))
sig6 = build_signals(B6, pool6)
summarize(sig6, "6 THANG (fp-m1-6-month, 27/1 -> 25/7/2026)", nd6)
dump_csv(sig6, DIRR + "trades_6month.csv")

# breakdown theo thang (vi Jan-Apr la hop dong xa gan chet -> it/khong dai dien)
print("\n  --- Theo THANG (luu y: GCQ26 Jan-Apr la HD xa gan chet, chi Jun-Jul thanh khoan that) ---")
print(f"  {'thang':<8}{'lenh':>5}{'WIN':>5}{'LOSS':>5}{'open':>6}{'WR':>6}{'R':>8}")
for m in range(1, 8):
    g = [s for s in sig6 if s['dt'].month == m]
    if not g: continue
    gc = [s for s in g if s['out'] in ('TP', 'SL')]; gtp = sum(s['out'] == 'TP' for s in g)
    print(f"  2026-{m:02d}{len(g):>7}{gtp:>5}{sum(s['out']=='SL' for s in g):>5}"
          f"{sum(s['out']=='open' for s in g):>6}{(gtp/len(gc)*100 if gc else 0):>5.0f}%{sum(s['R'] for s in g):>+7.1f}R")
print("=" * 78)
