#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day TP len 3R + thong ke day du + MO XE vi sao SL nhieu (do MFE: lenh di duoc bao xa truoc khi quay dau).
Cau hinh: cum>=2 (tol7, loai VWAP) + KB1+KB2. So sanh 1.5R/2R/3R. + phuong an SL2d cho 3R=6d.
Xuat CSV de doi chieu chart.
"""
import sys, csv, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em, research as R
TICK = em.TICK
DIRR = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/"
CONFL_TOL = 7


def cluster_of(pool, t, zp):
    seen = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= CONFL_TOL:
            seen.add(round(z['price'] / TICK))
    return len(seen)


def mfe_until_sl(B, i, side, entry, sl, horizon=600):
    """Max di THUAN LOI (tinh bang gia) truoc khi cham SL — de biet lenh di duoc bao xa."""
    best = 0.0
    for j in range(i + 1, min(i + 1 + horizon, len(B))):
        b = B[j]
        if side == 'LONG':
            best = max(best, b['hi'] - entry)
            if b['lo'] <= sl:
                break
        else:
            best = max(best, entry - b['lo'])
            if b['hi'] >= sl:
                break
    return best


def build(B, pool, floor_t):
    em.SL_MIN_T = floor_t; em.SL_MAX_T = 60; em.RR = 3.0; em.NEXTZONE_MINR = 2.0
    raw = em.run(B, pool)
    for s in raw:
        s['cluster'] = cluster_of(pool, s['dt'], float(s['zone'].split()[-1]))
    sig = em.dedup(raw)
    for s in sig:
        s.setdefault('cluster', 1)
    sig = [s for s in sig if s['cluster'] >= 2]
    for s in sig:
        r = s['risk_t'] * TICK
        s['risk_$'] = r
        s['mfe'] = mfe_until_sl(B, s['i'], s['side'], s['entry'], s['sl'])
        s['mfe_R'] = s['mfe'] / r
        s['scenN'] = 'KB1 pha&hoi' if s['scen'].startswith('1') else 'KB2 cham&dao'
        for rm in (1.5, 2.0, 3.0):
            tp = s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r
            o = R.hit_target(B, s['i'], s['side'], s['sl'], tp)
            s[f'o{rm}'] = o if o else 'open'
    return sig


def line(sig, rm):
    tp = sum(s[f'o{rm}'] == 'TP' for s in sig); sl = sum(s[f'o{rm}'] == 'SL' for s in sig)
    n = tp + sl; totR = tp * rm - sl
    return n, tp, sl, (tp / n if n else 0), (totR / n if n else 0), totR


B = em.load_m1(); pool = em.build_zones(B)
nd = len(set(b['dt'].date() for b in B))
sig = build(B, pool, 40)   # SL floor 4d (shipped)

print("=" * 84)
print(f"1 THANG — cum>=2, SL san 4d. So sanh muc chot TP ({len(sig)} lenh):")
print(f"  {'TP':>5} | {'WIN':>4}{'LOSS':>5} | {'WR':>5} | {'ky vong':>8} | {'tong R':>7}")
for rm in (1.5, 2.0, 3.0):
    n, tp, sl, wr, exp, totR = line(sig, rm)
    star = "  <== dang dung" if rm == 1.5 else ("  <== ban muon" if rm == 3.0 else "")
    print(f"  {rm:>4.1f}R | {tp:>4}{sl:>5} | {wr:>4.0%} | {exp:>+7.2f}R | {totR:>+6.1f}R{star}")

# phuong an: SL 2d de 3R = 6d (gan hon)
sig2 = build(B, pool, 20)
print(f"\n  Phuong an SL 2d (de 3R=6d, gan hon) — {len(sig2)} lenh:")
for rm in (1.5, 3.0):
    n, tp, sl, wr, exp, totR = line(sig2, rm)
    print(f"    SL2d @ {rm:.1f}R: WIN{tp} LOSS{sl} WR{wr:.0%} exp{exp:+.2f}R tong{totR:+.1f}R")

# ===== MO XE VI SAO SL NHIEU O 3R (SL floor 4d) =====
print("\n" + "=" * 84)
print("VI SAO NHIEU SL O 3R? — do MFE (lenh di duoc bao xa THUAN LOI truoc khi quay dau):")
losers3 = [s for s in sig if s['o3.0'] == 'SL']
print(f"  So lenh SL @3R = {len(losers3)} / {len(sig)}")
# trong so LOSER 3R: bao nhieu da tung di du xa de an muc thap hon?
for thr in (1.5, 2.0, 2.5):
    k = sum(1 for s in losers3 if s['mfe_R'] >= thr)
    print(f"    - {k:>2}/{len(losers3)} lenh SL@3R da tung di >= {thr}R roi MOI quay dau"
          f"  (neu chot {thr}R thi da WIN)")
gaveback = [s for s in losers3 if s['mfe_R'] >= 1.5]
print(f"  => {len(gaveback)}/{len(losers3)} lenh thua-3R that ra da co lai >=1.5R roi tra lai het.")
print(f"     MFE trung vi cua nhom SL@3R = {st.median([s['mfe_R'] for s in losers3]):.1f}R"
      f" (di trung binh ~{st.median([s['mfe_R'] for s in losers3]):.1f}R roi quay dau, chua toi 3R).")

# SL theo dac diem ENTRY
print("\n  SL@3R theo dac diem ENTRY:")
for key, groups in [
    ("Kich ban", [('KB1 pha&hoi', lambda s: s['scenN'] == 'KB1 pha&hoi'), ('KB2 cham&dao', lambda s: s['scenN'] == 'KB2 cham&dao')]),
    ("Huong", [('LONG', lambda s: s['side'] == 'LONG'), ('SHORT', lambda s: s['side'] == 'SHORT')]),
    ("VSA entry", [('VSA<1.5 (yeu)', lambda s: s['vsa'] < 1.5), ('VSA>=1.5', lambda s: s['vsa'] >= 1.5)]),
    ("Cluster", [('cluster=2', lambda s: s['cluster'] == 2), ('cluster>=3', lambda s: s['cluster'] >= 3)]),
]:
    print(f"    [{key}]")
    for lbl, f in groups:
        g = [s for s in sig if f(s)]; gsl = sum(s['o3.0'] == 'SL' for s in g); gtp = sum(s['o3.0'] == 'TP' for s in g)
        gc = gsl + gtp
        print(f"      {lbl:<16}: {len(g):>3} lenh | WR@3R {gtp/gc*100 if gc else 0:>3.0f}% ({gtp}W/{gsl}L)")

# ===== XUAT CSV doi chieu chart =====
path = DIRR + "trades_3R_1month.csv"
with open(path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['datetime', 'side', 'scenario', 'entry', 'SL', 'TP_1.5R', 'TP_3R', 'risk_d',
                'cluster', 'VSA', 'MFE_R (di xa nhat)', 'out@1.5R', 'out@3R', 'ghi_chu'])
    for s in sorted(sig, key=lambda x: x['dt']):
        tp15 = s['entry'] + 1.5 * s['risk_$'] if s['side'] == 'LONG' else s['entry'] - 1.5 * s['risk_$']
        tp3 = s['entry'] + 3.0 * s['risk_$'] if s['side'] == 'LONG' else s['entry'] - 3.0 * s['risk_$']
        note = ''
        if s['o3.0'] == 'SL' and s['mfe_R'] >= 1.5:
            note = f"da di {s['mfe_R']:.1f}R roi quay dau (chot 1.5R la WIN)"
        elif s['o3.0'] == 'SL':
            note = f"chi di {s['mfe_R']:.1f}R (yeu that su)"
        w.writerow([s['dt'].strftime('%Y-%m-%d %H:%M'), s['side'], s['scenN'], f"{s['entry']:.1f}",
                    f"{s['sl']:.1f}", f"{tp15:.1f}", f"{tp3:.1f}", f"{s['risk_t']/10:.1f}",
                    s['cluster'], f"{s['vsa']:.1f}", f"{s['mfe_R']:.2f}", s['o1.5'], s['o3.0'], note])
print(f"\n  -> file doi chieu chart: {path}")
print("=" * 84)
