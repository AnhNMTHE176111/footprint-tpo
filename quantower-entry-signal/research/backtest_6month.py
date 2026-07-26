#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST 6 THANG (fp-m1-6-month.csv, 27/1 -> 25/7/2026, ~152 ngay).
Muc tieu: KIEM DINH LAI edge "confluence>=2" tren mau lon gap ~6x lan truoc.
Khac entry_month.py o 1 diem: D-1 levels dung tu CHINH M1 (gap>DayGap tach ngay) —
KHOP thiet ke EntrySignal.cs (khong doc file TPO 1 thang). Con lai tai dung nguyen
bo logic da validate: scan/run, dedup/confluence, sim, VSA, gate.

Kiem dinh:
 [0] Chat luong data 6 thang (delta song? volume 1-phia?).
 [1] Tong quan + scenario.
 [2] Don dieu theo bac confluence (1 / >=2 / >=3) — edge phai TANG theo bac.
 [3] Chia 6 MANH thoi gian — confluence>=2 phai duong o DA SO manh (chong overfit manh).
 [4] MFE/MAE confluence>=2 vs baseline ngau nhien.
 [5] SL width sweep. Tan suat.
Trung thuc: offline VAN thieu footprint tung-muc -> KB2 dung proxy (VSA>=High + delta nguoc),
tuong hap thu that chi co LIVE. Ket qua KB2 o day la CAN DUOI.
"""
import sys, random, statistics as st
from datetime import datetime, timedelta
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
import research as R
TICK = em.TICK
DAY_GAP_MIN = 45  # khop EntrySignal.cs DayGapMin (khe bao tri M1 ~61' > 45 -> tach ngay)
FILE = "fp-m1-6-month.csv"
random.seed(7)


def load_m1_6m():
    """Doc file 6 thang + tinh cac truong dan xuat — copy y het em.load_m1 tru ten file."""
    h, rows = em.load(FILE)
    ix = {n: i for i, n in enumerate(h)}
    B = [dict(dt=em.pdt(x[ix['DateTime']]), o=em.fn(x[ix['Open']]), hi=em.fn(x[ix['High']]),
              lo=em.fn(x[ix['Low']]), c=em.fn(x[ix['Close']]), v=em.fn(x[ix['Volume']]),
              delta=em.fn(x[ix['Delta']]), cum=em.fn(x[ix['Cumulative delta']]),
              buy=em.fn(x[ix['Buy (Ask) volume']]), sell=em.fn(x[ix['Sell (Bid) volume']]))
         for x in rows]
    B.sort(key=lambda b: b['dt'])
    ef = es = None; kf = 2 / (30 + 1); ks = 2 / (120 + 1); csum_pv = csum_v = 0.0
    for i, b in enumerate(B):
        gap = i > 0 and (b['dt'] - B[i - 1]['dt']).total_seconds() / 60 > 30
        if gap: csum_pv = csum_v = 0.0
        tp = (b['hi'] + b['lo'] + b['c']) / 3.0; csum_pv += tp * b['v']; csum_v += b['v']
        b['vwap'] = csum_pv / csum_v if csum_v > 0 else b['c']
        win = [B[j]['v'] for j in range(max(0, i - em.VSA_MA + 1), i + 1)]
        sma = sum(win) / len(win) if win else b['v']
        b['vma'] = sma; b['vratio'] = b['v'] / sma if sma > 1e-9 else 0.0
        ef = b['c'] if ef is None else ef + kf * (b['c'] - ef)
        es = b['c'] if es is None else es + ks * (b['c'] - es)
        b['bias'] = 1 if ef > es + 3 * TICK else -1 if ef < es - 3 * TICK else 0
        rng = b['hi'] - b['lo']; b['rng'] = rng; b['body'] = abs(b['c'] - b['o'])
        b['uw'] = b['hi'] - max(b['o'], b['c']); b['lw'] = min(b['o'], b['c']) - b['lo']
        b['brat'] = b['body'] / rng if rng > 0 else 0.0
        b['cpos'] = (b['c'] - b['lo']) / rng if rng > 0 else 0.5
        b['ddom'] = b['delta'] / b['v'] if b['v'] > 0 else 0.0
        b['since_gap'] = 0 if gap else (B[i - 1]['since_gap'] + 1 if i > 0 else 999)
    return B


def day_blocks(B):
    """Tach ngay bang gap>DAY_GAP_MIN (khop ProfileEngine.GroupByGap tren M1)."""
    blocks = []; cur = None
    for b in B:
        new = cur is None or (b['dt'] - cur[-1]['dt']) > timedelta(minutes=DAY_GAP_MIN)
        if new: cur = []; blocks.append(cur)
        cur.append(b)
    return blocks


def build_zones_6m(B):
    """Session zones + D-1 (ca hai tu M1) + VWAP dong — khop EntrySignal.BuildPool."""
    zones = []
    # --- session blocks (doi nhan A/AU/MY hoac gap>40') ---
    blocks = []; cur = None
    for b in B:
        lab = em.sess_of(b['dt'].hour * 60 + b['dt'].minute)
        new = (cur is None or lab != cur['lab'] or (b['dt'] - cur['bars'][-1]['dt']) > timedelta(minutes=40))
        if new: cur = dict(lab=lab, bars=[]); blocks.append(cur)
        cur['bars'].append(b)
    for blk in blocks:
        bb = blk['bars']
        if len(bb) < 10: continue
        end = bb[-1]['dt']; poc, vah, val = em.value_area(em.tpo_counts([(x['lo'], x['hi']) for x in bb]))
        if poc is None: continue
        hi = max(x['hi'] for x in bb); lo = min(x['lo'] for x in bb)
        exp = end + timedelta(days=em.ZONE_EXPIRE_DAYS)
        for nm, val_, strv in [(f"POC {blk['lab']}", poc, 70), (f"VAH {blk['lab']}", vah, 58),
                               (f"VAL {blk['lab']}", val, 58), (f"Dinh {blk['lab']}", hi, 52),
                               (f"Day {blk['lab']}", lo, 52)]:
            zones.append(dict(price=val_, kind=nm, strength=strv, ready=end, expire=exp))
    # --- D-1 tu M1 (day-block) ---
    dbs = day_blocks(B)
    for i in range(1, len(dbs)):
        prev = dbs[i - 1]
        if len(prev) < 30: continue
        poc, vah, val = em.value_area(em.tpo_counts([(x['lo'], x['hi']) for x in prev]))
        if poc is None: continue
        hi = max(x['hi'] for x in prev); lo = min(x['lo'] for x in prev)
        rd = dbs[i][0]['dt']; exp = rd + timedelta(days=1, hours=6)
        for nm, val_, strv in [("D-1 VAH", vah, 66), ("D-1 VAL", val, 66), ("D-1 POC", poc, 72),
                               ("D-1 High", hi, 60), ("D-1 Low", lo, 60)]:
            zones.append(dict(price=val_, kind=nm, strength=strv, ready=rd, expire=exp))
    return zones


def wr_exp(sigs, B, rmult):
    tp = sl = 0
    for s in sigs:
        r = s['risk_t'] * TICK
        tpp = s['entry'] + rmult * r if s['side'] == 'LONG' else s['entry'] - rmult * r
        o = R.hit_target(B, s['i'], s['side'], s['sl'], tpp)
        if o == 'TP': tp += 1
        elif o == 'SL': sl += 1
    n = tp + sl
    return n, (tp / n if n else 0), ((tp * rmult - sl) / n if n else 0)


def main():
    print("=" * 100)
    B = load_m1_6m()
    span = (B[-1]['dt'] - B[0]['dt']).days
    print(f"BACKTEST 6 THANG | M1={len(B)} nen | {B[0]['dt']:%m/%d} -> {B[-1]['dt']:%m/%d} ({span} ngay)")

    # [0] chat luong data
    print("\n[0] CHAT LUONG DATA 6 thang:")
    nz = [b for b in B if b['v'] > 0]
    d_ok = sum(abs((b['buy'] - b['sell']) - b['delta']) < 1 for b in nz)
    bs_eq = sum(abs((b['buy'] + b['sell']) - b['v']) < 1 for b in nz)
    print(f"  Delta==Buy-Sell: {d_ok}/{len(nz)} ({d_ok*100//len(nz)}%)  |  Buy+Sell==Volume: {bs_eq}/{len(nz)} ({bs_eq*100//len(nz)}%)")
    print(f"  vol median={st.median([b['v'] for b in nz]):.0f}  |  |delta| median={st.median([abs(b['delta']) for b in nz]):.0f}")

    pool = build_zones_6m(B)
    raw = em.run(B, pool); sig = em.dedup(raw)
    for s in sig:
        s['mfe'], s['mae'] = R.mfe_mae(B, s['i'], s['side'])
    print(f"\n  zones={len(pool)} | raw={len(raw)} | sau gop confluence={len(sig)}")

    # [1] tong quan + confluence>=2 la bo loc chinh
    c2 = [s for s in sig if s['confl'] >= 2]
    days = len(set(s['dt'].date() for s in sig))
    print("\n[1] TONG QUAN (confluence>=2 = bo loc chinh cua indicator):")
    for nm, sub in [("Tat ca (sau gop)", sig), ("Confluence>=2", c2)]:
        if sub:
            n2, w2, e2 = wr_exp(sub, B, 2.0); n3, w3, e3 = wr_exp(sub, B, 3.0)
            print(f"  {nm:<18} n={len(sub):>4} | 2R WR{w2:>4.0%} exp{e2:>+6.2f} | 3R WR{w3:>4.0%} exp{e3:>+6.2f}")
    print(f"  Tan suat confluence>=2: {len(c2)} lenh / {days} ngay = {len(c2)/days:.1f} lenh/ngay")

    # [2] don dieu theo confluence
    print("\n[2] DON DIEU theo bac confluence (edge phai TANG dan):")
    print(f"  {'bac':<8}{'n':>5} | {'2R WR':>6}{'2R exp':>8} | {'3R WR':>6}{'3R exp':>8}")
    for nm, f in [("=1", lambda s: s['confl'] == 1), (">=2", lambda s: s['confl'] >= 2), (">=3", lambda s: s['confl'] >= 3)]:
        sub = [s for s in sig if f(s)]
        if len(sub) >= 6:
            n2, w2, e2 = wr_exp(sub, B, 2.0); n3, w3, e3 = wr_exp(sub, B, 3.0)
            print(f"  {nm:<8}{len(sub):>5} | {w2:>6.0%}{e2:>+8.2f} | {w3:>6.0%}{e3:>+8.2f}")
        else:
            print(f"  {nm:<8}{len(sub):>5}  (qua it)")

    # [3] chia 6 manh thoi gian
    print("\n[3] CHIA 6 MANH thoi gian — confluence>=2 co giu deu? (chong overfit):")
    t0, t1 = B[0]['dt'], B[-1]['dt']; seg = (t1 - t0) / 6
    print(f"  {'manh':<20}{'n':>4} | {'2R WR':>6}{'2R exp':>8} | {'3R WR':>6}{'3R exp':>8}")
    pos2 = 0; segs_used = 0
    for k in range(6):
        a = t0 + seg * k; bnd = t0 + seg * (k + 1)
        sub = [s for s in c2 if a <= s['dt'] < bnd] if k < 5 else [s for s in c2 if a <= s['dt'] <= bnd]
        lbl = f"{a:%m/%d}-{bnd:%m/%d}"
        if len(sub) >= 4:
            n2, w2, e2 = wr_exp(sub, B, 2.0); n3, w3, e3 = wr_exp(sub, B, 3.0)
            segs_used += 1; pos2 += (e2 > 0)
            print(f"  {lbl:<20}{len(sub):>4} | {w2:>6.0%}{e2:>+8.2f} | {w3:>6.0%}{e3:>+8.2f}")
        else:
            print(f"  {lbl:<20}{len(sub):>4}  (qua it)")
    print(f"  => confluence>=2 duong@2R o {pos2}/{segs_used} manh co du mau")
    # doi chung confluence==1 tren cung 6 manh
    print("  (doi chung confluence==1 — ky vong nen KEM/am):")
    c1 = [s for s in sig if s['confl'] == 1]
    for k in range(6):
        a = t0 + seg * k; bnd = t0 + seg * (k + 1)
        sub = [s for s in c1 if a <= s['dt'] < bnd] if k < 5 else [s for s in c1 if a <= s['dt'] <= bnd]
        if len(sub) >= 4:
            n2, w2, e2 = wr_exp(sub, B, 2.0)
            print(f"  {a:%m/%d}-{bnd:%m/%d:<8}  n={len(sub):>3} 2R exp{e2:+.2f}")

    # [4] MFE/MAE vs baseline
    print("\n[4] MFE/MAE confluence>=2 vs baseline ngau nhien cung phia:")
    def avg(a): return sum(a) / len(a) if a else 0
    mf = avg([s['mfe'] for s in c2]); ma = avg([s['mae'] for s in c2])
    pL = sum(s['side'] == 'LONG' for s in c2) / len(c2) if c2 else 0.5
    base = []
    for i in random.sample(range(30, len(B) - R.H_MFE), 5000):
        side = 'LONG' if random.random() < pL else 'SHORT'; base.append(R.mfe_mae(B, i, side))
    bmf = avg([x[0] for x in base]); bma = avg([x[1] for x in base])
    print(f"  confluence>=2 : MFE {mf:>5.0f} MAE {ma:>5.0f} ratio {mf/ma:.2f}")
    print(f"  baseline(5000): MFE {bmf:>5.0f} MAE {bma:>5.0f} ratio {bmf/bma:.2f}")

    # [5] scenario + SL width
    print("\n[5] Trong confluence>=2:")
    for nm, sub in [("scen1 (pha&hoi)", [s for s in c2 if s['scen'].startswith('1')]),
                    ("scen2 (cham&dao)", [s for s in c2 if s['scen'].startswith('2')])]:
        if len(sub) >= 6:
            n2, w2, e2 = wr_exp(sub, B, 2.0); n3, w3, e3 = wr_exp(sub, B, 3.0)
            print(f"  {nm:<18}{len(sub):>4} | 2R WR{w2:.0%} exp{e2:+.2f} | 3R WR{w3:.0%} exp{e3:+.2f}")
        else:
            print(f"  {nm:<18}{len(sub):>4}  (qua it)")
    print("  SL width (confluence>=2, TP=3xSL):")
    for w in [20, 30, 40, 60]:
        n, wr, e = R.wr_exp_fixedSL(c2, B, w); print(f"    SL {w/10:.0f}d  n={n:>4} WR{wr:>4.0%} exp{e:+.2f}")

    print("=" * 100); print("DONE")


main()
