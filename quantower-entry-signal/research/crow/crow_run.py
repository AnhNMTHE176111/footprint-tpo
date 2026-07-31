#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Driver cho crow_v1: core / gates / delta / null. Xem dac ta trong crow_v1.py docstring."""
import sys, os, random, statistics as st
R = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research"
sys.path.insert(0, R); sys.path.insert(0, os.path.join(R, "wyckoff")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entry_dxfeed as E
import crow_v1 as K
from v7 import report

MONTHS = K.MONTHS


def load_dx():
    B = K.prep(E.load_m1())
    print(f"[dxFeed] {len(B)} nen {B[0]['dt']} -> {B[-1]['dt']}")
    return B


def load_merged():
    import fp_merged
    B = K.prep(fp_merged.load_merged())
    return B


def core(B, pool=None):
    print("\n===== LOI CROW (X1 impulse + X2 retrace nong + X9 RR2) =====")
    base = K.cfg()
    K.pipe(B, base, "LOI mac dinh (PMAX.50 RR2)", pool)
    print("\n-- sweep PMAX (do sau nhip hoi toi da; X2 'khong test qua sau') --")
    rows = []
    for pm in (0.30, 0.40, 0.50, 0.62, 0.75, 0.90):
        S, d = K.pipe(B, K.cfg(PMAX=pm), f"PMAX={pm:.2f}", pool)
        rows.append((f"PMAX={pm:.2f}", d))
    report.sweep("PMAX", rows)
    print("\n-- sweep IMP_K (nen impulse to gap may lan range trung vi) --")
    rows = []
    for k in (1.2, 1.5, 2.0, 2.5, 3.0):
        S, d = K.pipe(B, K.cfg(IMP_K=k), f"IMP_K={k}", pool)
        rows.append((f"IMP_K={k}", d))
    report.sweep("IMP_K", rows)
    print("\n-- sweep IMP_BODY / IMP_VSA --")
    rows = []
    for bd in (0.50, 0.60, 0.70, 0.80):
        S, d = K.pipe(B, K.cfg(IMP_BODY=bd), f"IMP_BODY={bd}", pool)
        rows.append((f"BODY={bd}", d))
    report.sweep("IMP_BODY", rows)
    rows = []
    for v in (1.0, 1.5, 2.0, 2.5):
        S, d = K.pipe(B, K.cfg(IMP_VSA=v), f"IMP_VSA={v}", pool)
        rows.append((f"VSA={v}", d))
    report.sweep("IMP_VSA", rows)
    print("\n-- sweep RR (X9 noi 1:2; kiem xem 2 co that la diem tot) --")
    rows = []
    for rr in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
        S, d = K.pipe(B, K.cfg(RR=rr), f"RR={rr}", pool)
        rows.append((f"RR={rr}", d))
    report.sweep("RR", rows)
    print("\n-- sweep SL cap/floor --")
    for fl, cp in ((10, 30), (20, 40), (20, 50), (30, 70)):
        K.pipe(B, K.cfg(FLOOR=fl, CAP=cp), f"SL[{fl}..{cp}]t", pool)
    print("\n-- sweep WAIT --")
    for w in (6, 12, 20, 30):
        K.pipe(B, K.cfg(WAIT=w), f"WAIT={w}", pool)


def gates(B, pool):
    print("\n===== GATE tren dxFeed (X7 keylevel, X8 widebreak, TREND) =====")
    base = K.cfg()
    S0, d0 = K.pipe(B, base, "LOI (doi chung)", pool)
    for name, c in (("+TREND (thuan xu huong v5)", K.cfg(TREND=True)),
                    ("+X8 WIDEBRK (bien rong->doi break)", K.cfg(WIDE=True)),
                    ("+X7 KEY veto 7t", K.cfg(KEY=True)),
                    ("+X7 KEY veto 12t", K.cfg(KEY=True, KEY_T=12)),
                    ("+TREND +X8", K.cfg(TREND=True, WIDE=True)),
                    ("+TREND +X8 +X7", K.cfg(TREND=True, WIDE=True, KEY=True))):
        K.pipe(B, c, name, pool)
    # partition cho tung gate: nhom BI LOAI co EV thap hon that khong?
    print("\n-- partition TREND --")
    keep = [s for s in S0 if B[s['i']]['trend'] == (1 if s['side'] == 'LONG' else -1)]
    drop = [s for s in S0 if B[s['i']]['trend'] != (1 if s['side'] == 'LONG' else -1)]
    report.partition("thuan xu huong", keep, "nguoc/ngang", drop)
    print("\n-- partition X8 (nen impulse co pha bien rong hay khong) --")
    keep = [s for s in S0 if K.wide_ok(B, s['imp'], s['side'] == 'LONG', base)]
    drop = [s for s in S0 if not K.wide_ok(B, s['imp'], s['side'] == 'LONG', base)]
    report.partition("khong-vi-pham X8", keep, "bien rong chua break", drop)
    print("\n-- partition X7 (entry co sat vung/VWAP hay khong) --")
    keep = [s for s in S0 if not K.near_key(s['entry'], s['dt'], pool, B[s['i']]['vwap'], 7)]
    drop = [s for s in S0 if K.near_key(s['entry'], s['dt'], pool, B[s['i']]['vwap'], 7)]
    report.partition("xa vung", keep, "sat vung/VWAP", drop)
    print("\n-- partition do sau nhip hoi (retr) --")
    for lo, hi in ((0.15, 0.30), (0.30, 0.50), (0.50, 0.75), (0.75, 1.01)):
        sub = [s for s in S0 if lo <= s['retr'] < hi]
        report.line(f"retr [{lo:.2f},{hi:.2f})", sub, MONTHS)


def delta(BM):
    print("\n===== FEED MERGED (co delta + per-level): X3 DMA, X5 BUBBLE =====")
    print("⚠ n nho hon dxFeed (chi nhung ngay co footprint). KHONG tron ket qua voi bang dxFeed.")
    base = K.cfg()
    S0, d0 = K.pipe(BM, base, "LOI tren merged (doi chung)")
    print("\n-- X3 DMA --")
    for name, c in (("+DMA(9) luon ap", K.cfg(DMA=True)),
                    ("+DMA(20) luon ap", K.cfg(DMA=True, DMA_N=20)),
                    ("+DMA(9) chi khi bien hep", K.cfg(DMA=True, DMA_NARROW=True)),
                    ("+DMA(20) chi khi bien hep", K.cfg(DMA=True, DMA_N=20, DMA_NARROW=True))):
        K.pipe(BM, c, name)
    print("\n-- X5 BUBBLE (vi tri o aggressor lon nhat) --")
    for name, c in (("+BUB<=0.60 nen entry (aggr)", K.cfg(BUB=True)),
                    ("+BUB<=0.50 nen entry (aggr)", K.cfg(BUB=True, BUB_MAX=0.50)),
                    ("+BUB<=0.70 nen entry (aggr)", K.cfg(BUB=True, BUB_MAX=0.70)),
                    ("+BUB<=0.60 nen impulse (aggr)", K.cfg(BUB=True, BUB_BAR='impulse')),
                    ("+BUB<=0.60 nen entry (POC-vol)", K.cfg(BUB=True, BUB_SIDE='vol')),
                    ("+BUB<=0.60 nen impulse (POC-vol)", K.cfg(BUB=True, BUB_BAR='impulse', BUB_SIDE='vol'))):
        K.pipe(BM, c, name)
    # partition: chinh xac cai video noi — bubble sat high thi TE hon that khong?
    print("\n-- partition X5: bubble tren nen ENTRY, aggressor --")
    def bp(s, bar, mode):
        b = BM[s['i'] if bar == 'entry' else s['imp']]
        return K.bubble_pos(b, s['side'], mode)
    for bar in ('entry', 'impulse'):
        for mode in ('aggr', 'vol'):
            print(f"   >> bar={bar} mode={mode}")
            for lo, hi in ((0.0, 0.34), (0.34, 0.67), (0.67, 1.01)):
                sub = []
                for s in S0:
                    p = bp(s, bar, mode)
                    if p is None:
                        continue
                    pn = p if s['side'] == 'LONG' else 1 - p    # chuan hoa: 1 = sat cuc tri "thuan huong"
                    if lo <= pn < hi:
                        sub.append(s)
                report.line(f"   pos_norm [{lo:.2f},{hi:.2f})", sub, MONTHS)
    print("\n-- partition ddom nen entry (delta ap dao) --")
    for lo, hi in ((-1.01, -0.1), (-0.1, 0.1), (0.1, 1.01)):
        sub = []
        for s in S0:
            b = BM[s['i']]
            dd = b.get('ddom')
            if dd is None:
                continue
            ddn = dd if s['side'] == 'LONG' else -dd
            if lo <= ddn < hi:
                sub.append(s)
        report.line(f"ddom_thuan [{lo:+.2f},{hi:+.2f})", sub, MONTHS)


def null(B, pool, C, tag, ntrial=400):
    """Null model kieu kb4_null: giu nguyen phia/risk/thoi diem-phan-phoi nhung random hoa
    thoi diem vao lenh trong cung ngay -> so tong R that voi phan phoi ngau nhien."""
    S = K.evaluate(B, K.dedup(K.run(B, C, pool)), C)
    S = [s for s in S if s['ym'] in MONTHS]
    real = sum(s['r'] for s in S)
    byday = {}
    for i, b in enumerate(B):
        if b['ym'] in MONTHS:
            byday.setdefault(b['dt'].strftime('%Y-%m-%d'), []).append(i)
    rnd = random.Random(20260731)
    tot = []
    for _ in range(ntrial):
        acc = 0.0
        for s in S:
            day = s['dt'].strftime('%Y-%m-%d')
            cand = byday.get(day) or []
            if not cand:
                continue
            i2 = rnd.choice(cand)
            b2 = B[i2]
            r = s['risk_t'] * TICKV
            sl = b2['c'] - r if s['side'] == 'LONG' else b2['c'] + r
            tp = b2['c'] + C['RR'] * r if s['side'] == 'LONG' else b2['c'] - C['RR'] * r
            o = K.hit(B, i2, s['side'], sl, tp)
            if o == 'open':
                continue
            acc += C['RR'] if o == 'TP' else -1.0
        tot.append(acc)
    tot.sort()
    pct = 100.0 * sum(1 for x in tot if x < real) / len(tot)
    mu = st.mean(tot); sd = st.pstdev(tot) or 1e-9
    print(f"\n[NULL {tag}] that={real:+.1f}R  ngau nhien: trung binh {mu:+.1f}R sd {sd:.1f} "
          f"| percentile {pct:.1f}%  z={(real - mu) / sd:+.2f}  (n_lenh={len(S)}, {ntrial} lan)")


def core2(B, pool):
    """VONG 2 — 3 kha nang lech dac ta (xem crow_v1.cfg VONG 2)."""
    print("\n===== VONG 2: impulse tu VUNG NEN / doi nen XAC NHAN / kiem DAU =====")
    K.pipe(B, K.cfg(), "LOI vong 1 (doi chung)", pool)
    print("\n-- COMPRESS: impulse phai pha bien vung nen --")
    for cn, cs in ((8, 50), (12, 75), (12, 100), (20, 100), (30, 150)):
        K.pipe(B, K.cfg(COMPRESS=True, CN=cn, CSPAN=cs), f"COMPRESS CN={cn} span<={cs}t", pool)
    print("\n-- CONFIRM: doi nen dong vuot cuc tri nen hoi --")
    for cf in (3, 6, 10):
        K.pipe(B, K.cfg(CONFIRM=True, CF_WAIT=cf), f"CONFIRM wait={cf}", pool)
    print("\n-- COMPRESS + CONFIRM --")
    for cn, cs in ((12, 75), (12, 100), (20, 100)):
        K.pipe(B, K.cfg(COMPRESS=True, CN=cn, CSPAN=cs, CONFIRM=True), f"COMPR({cn},{cs}) + CONFIRM", pool)
    print("\n-- + TREND / + X7 tren cau hinh COMPRESS+CONFIRM --")
    for name, c in (("COMPR+CONF +TREND", K.cfg(COMPRESS=True, CONFIRM=True, TREND=True)),
                    ("COMPR+CONF +KEY12", K.cfg(COMPRESS=True, CONFIRM=True, KEY=True, KEY_T=12)),
                    ("COMPR+CONF +TREND+KEY12", K.cfg(COMPRESS=True, CONFIRM=True, TREND=True, KEY=True, KEY_T=12))):
        K.pipe(B, c, name, pool)
    print("\n-- KIEM DAU (FADE = vao nguoc huong impulse; khong phai de ship) --")
    for name, c in (("FADE loi", K.cfg(FADE=True)),
                    ("FADE + COMPRESS", K.cfg(FADE=True, COMPRESS=True)),
                    ("FADE + CONFIRM", K.cfg(FADE=True, CONFIRM=True))):
        K.pipe(B, c, name, pool)
    print("\n-- RR tren cau hinh COMPRESS+CONFIRM (X9 noi 1:2) --")
    rows = []
    for rr in (1.0, 1.5, 2.0, 2.5, 3.0):
        S, d = K.pipe(B, K.cfg(COMPRESS=True, CONFIRM=True, RR=rr), f"COMPR+CONF RR={rr}", pool)
        rows.append((f"RR={rr}", d))
    report.sweep("RR tren COMPR+CONF", rows)


def core3(BM):
    """VONG 3 — MODEL HAP THU (X6) lam entry + quan ly lenh BE. Chay tren merged (can delta)."""
    print("\n===== VONG 3: entry = NEN HAP THU trong nhip hoi (X6) =====")
    K.pipe(BM, K.cfg(), "LOI (doi chung, entry nen thuan huong)")
    for name, c in (("ABS dd.15 wick.30", K.cfg(ABS=True)),
                    ("ABS dd.25 wick.30", K.cfg(ABS=True, ABS_DD=0.25)),
                    ("ABS dd.15 wick.50", K.cfg(ABS=True, ABS_WICK=0.50)),
                    ("ABS dd.25 wick.50", K.cfg(ABS=True, ABS_DD=0.25, ABS_WICK=0.50)),
                    ("ABS + PMAX.75", K.cfg(ABS=True, PMAX=0.75)),
                    ("ABS + PMAX.90", K.cfg(ABS=True, PMAX=0.90)),
                    ("ABS + TREND", K.cfg(ABS=True, TREND=True)),
                    ("ABS + COMPRESS", K.cfg(ABS=True, COMPRESS=True))):
        K.pipe(BM, c, name)
    print("\n-- RR tren ABS --")
    rows = []
    for rr in (1.0, 1.5, 2.0, 2.5, 3.0):
        S, d = K.pipe(BM, K.cfg(ABS=True, RR=rr), f"ABS RR={rr}")
        rows.append((f"RR={rr}", d))
    report.sweep("RR tren ABS", rows)
    print("\n-- quan ly lenh BE (dua SL ve entry sau x*risk) tren LOI va tren ABS --")
    for be in (0.0, 0.5, 1.0, 1.5):
        K.pipe(BM, K.cfg(BE_AT=be), f"LOI BE={be}")
    for be in (0.0, 0.5, 1.0, 1.5):
        K.pipe(BM, K.cfg(ABS=True, BE_AT=be), f"ABS BE={be}")
    print("\n-- FADE+CONFIRM tren merged (doi chieu voi dxFeed) + BE --")
    for be in (0.0, 1.0):
        K.pipe(BM, K.cfg(FADE=True, CONFIRM=True, BE_AT=be), f"FADE+CONF BE={be}")
    print("\n-- phi 2 tick tren cac cau hinh duong --")
    for name, c in (("ABS", K.cfg(ABS=True)), ("ABS RR2.5", K.cfg(ABS=True, RR=2.5)),
                    ("FADE+CONF", K.cfg(FADE=True, CONFIRM=True))):
        K.pipe(BM, c, f"{name} phi=2t", cost_t=2)


TICKV = E.TICK

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'core'
    if mode in ('core', 'core2', 'gates', 'null'):
        B = load_dx()
        pool = E.build_zones(B)
        print(f"[pool] {len(pool)} vung")
        if mode == 'core':
            core(B, pool)
        elif mode == 'core2':
            core2(B, pool)
        elif mode == 'gates':
            gates(B, pool)
        else:
            null(B, pool, K.cfg(), "LOI")
            null(B, pool, K.cfg(TREND=True, WIDE=True), "LOI+TREND+X8")
            null(B, pool, K.cfg(FADE=True, CONFIRM=True), "FADE+CONFIRM")
            null(B, pool, K.cfg(FADE=True), "FADE loi")
            print("\n-- phi giao dich tren FADE+CONFIRM --")
            for ct in (0, 1, 2, 3):
                K.pipe(B, K.cfg(FADE=True, CONFIRM=True), f"FADE+CONF phi={ct}t", pool, cost_t=ct)
            print("\n-- cao nguyen tham so quanh FADE+CONFIRM --")
            for cf in (3, 6, 10):
                K.pipe(B, K.cfg(FADE=True, CONFIRM=True, CF_WAIT=cf), f"CF_WAIT={cf}", pool)
            for pm in (0.30, 0.40, 0.50, 0.62, 0.75):
                K.pipe(B, K.cfg(FADE=True, CONFIRM=True, PMAX=pm), f"PMAX={pm}", pool)
            for rr in (1.0, 1.5, 2.0, 2.5, 3.0):
                K.pipe(B, K.cfg(FADE=True, CONFIRM=True, RR=rr), f"RR={rr}", pool)
            for ik in (1.2, 1.5, 2.0, 2.5):
                K.pipe(B, K.cfg(FADE=True, CONFIRM=True, IMP_K=ik), f"IMP_K={ik}", pool)
            print("\n-- OOS tho: 2026-01..04 (thanh khoan thap, doc than trong) --")
            K.pipe(B, K.cfg(FADE=True, CONFIRM=True), "FADE+CONF 01-04", pool, months=('2026-01','2026-02','2026-03','2026-04'))
            K.pipe(B, K.cfg(FADE=True, CONFIRM=True), "FADE+CONF 11-12/2025", pool, months=('2025-11','2025-12'))
    elif mode == 'delta':
        delta(load_merged())
    elif mode == 'core3':
        core3(load_merged())
    else:
        print(__doc__)




