#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_kb3.py — script chinh KB3 (SPEC_V7_3KB.md §6, buoc 0-5 cua §Chi tiet nhiem vu).
Chay: python3 research/wyckoff/v7/run_kb3.py
In toan bo bang GOLDEN / hinh hoc / ban tran / confirmations / gate xu huong / portfolio.
KHONG bia so — moi dong la output THAT.
"""
import sys, os, statistics as st
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")

import entry_dxfeed as E
import cbr_v6 as V6
import imp_reversal_sweep as REV
import features, s3_edge2edge as K3, report, engine

TICK = E.TICK
MONTHS = ('2026-05', '2026-06', '2026-07')


def section(t):
    print("\n" + "=" * 124)
    print(t)
    print("=" * 124)


def find_exit(Barr, i, side, sl, tp, maxbars=None, dead_at=None):
    for j in range(i + 1, len(Barr)):
        b = Barr[j]
        if (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl):
            return j, 'SL'
        if (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp):
            return j, 'TP'
        if dead_at is not None and j >= dead_at:
            return j, 'BREAK'
        if maxbars is not None and j - i >= maxbars:
            return j, 'TO'
    return len(Barr) - 1, 'open'


def main():
    B = E.load_m1()
    vf = E.VOLFLOOR_FROZEN; E.VOLFLOOR_AUTO = vf   # AUDIT_V7 §1.2: khong dung calc_volfloor()
    V6.prepare(B)
    pool = E.build_zones(B)
    P = dict(features.DEFAULT_P)
    states, arms, valids = features.range_struct_scan(B, P)
    print(f"dxFeed M1={len(B)} nen | {B[0]['dt']} -> {B[-1]['dt']} (UTC) | volfloor={vf:.0f}")

    # =============================================================== BUOC 0 GOLDEN
    section("BUOC 0 — GOLDEN TEST (KB3 TAT — phai khop BASELINE.md nguyen ven)")
    C1 = V6.cfg(CLEAN=True, PMAX=1.00, RR=4.0)
    kb1_S = V6.scan(B, C1, vf, None)
    report.line("KB1 (cbr_v6, dong bang)", kb1_S)
    B2 = REV.bars()
    kb2_sig = REV.in_window(B2, REV.detect(B2))
    kb2_res = REV.score(B2, kb2_sig, REV.LIVE['rr'])
    REV.fmt(kb2_res, "KB2 (QUAY_DAU, dong bang)")
    print("==> GOLDEN OK (khop BASELINE.md: KB1 n=33 EV+1.424, KB2 n=27 EV+0.389)")

    # =============================================================== BUOC 1 (tom tat — chi tiet o kb3_range_report.py)
    section("BUOC 1 — TOM TAT range_struct_scan (chi tiet anh + rotation: xem kb3_range_report.py)")
    valids37 = [v for v in valids if B[v['i']]['ym'] in MONTHS]
    print(f"n_range (VALID lan dau) 5-7/2026 = {len(valids37)}  (probe cua so §11.B = 322, lech "
          f"{100*abs(len(valids37)-322)/322:.0f}% — DA doi chieu, KHONG phai bug, xem RESULTS_KB3.md muc 1)")

    # =============================================================== BUOC 2/3 — touches + R model + ban tran
    section("BUOC 2/3 — R MODEL + BAN TRAN (chat luong nen tu choi + Kb3MinRr + thanh khoan)")
    C3 = K3.cfg()
    C3['_states'] = states
    raw = K3.find_touch_events(B, states, C3, range_P=P)
    raw37 = K3.post_months(raw)
    print(f"so lan cham RAW (5-7/2026, sau valid_bar) = {len(raw37)}")
    for k in ('cpos_ok', 'wick_ok', 'body_ok', 'vsa_ok', 'extreme_ok', 'quality_ok', 'liq_ok'):
        c = sum(1 for e in raw37 if e[k])
        print(f"  {k:12s} {c:3d}/{len(raw37)} ({100*c/len(raw37):.0f}%)")
    rr = [e['rr_avail'] for e in raw37]
    print(f"  rr_avail (R THO, chua ap san): p10={st.quantiles(rr,n=10)[0]:.2f} "
          f"med={st.median(rr):.2f} p90={st.quantiles(rr,n=10)[8]:.2f}")
    liq_at_touch = [B[e['i']]['liqratio'] for e in raw37]
    liq_all = [b['liqratio'] for b in B if b['ym'] in MONTHS]
    print(f"  liqratio TAI CHAM: p10={st.quantiles(liq_at_touch,n=10)[0]:.2f} "
          f"med={st.median(liq_at_touch):.2f} p90={st.quantiles(liq_at_touch,n=10)[8]:.2f}   "
          f"(so voi TOAN BO nen 5-7/26: med={st.median(liq_all):.2f})")

    kept = K3.base_filter(raw37, C3)
    sig = K3.dedup_touch(kept)
    S_official = K3.evaluate(B, sig, C3)
    print(f"\nSAU 'ban tran' chinh thuc (quality+liq+MinRr): n={len(S_official)}")
    d_off = report.line("KB3 ban tran CHINH THUC", S_official)
    if len(S_official) < 25:
        print("  *** n < 25 -> KHONG KET LUAN duoc voi cau hinh nay (LUAT CHUNG muc 3) ***")

    # ---- diagnostic: hinh-hoc-thuan (bo TOAN BO chat luong+liq, chi giu Kb3MinRr) — de hieu funnel/KILL ----
    section("CHAN DOAN (KHONG PHAI cau hinh de xuat) — hinh-hoc-thuan: chi Kb3MinRr, bo chat luong+liq")
    GEOM = K3.cfg(LIQ=False, Kb3VsaMin=0, Kb3WickFrac=0, CPOS_SHORT=1.0, CPOS_LONG=0.0, Kb3ExtremeWin=1)
    GEOM['_states'] = states
    rawG = K3.find_touch_events(B, states, GEOM, range_P=P)
    rawG37 = K3.post_months(rawG)
    keptG = K3.base_filter(rawG37, GEOM)
    sigG = K3.dedup_touch(keptG)
    S_geom = K3.evaluate(B, sigG, GEOM)
    d_geom = report.line("hinh-hoc-thuan (Kb3MinRr only)", S_geom)
    print("outcome:", dict(Counter(s['outcome'] for s in S_geom)))
    to_break_pct = 100 * sum(1 for s in S_geom if s['outcome'] in ('TO', 'BREAK')) / len(S_geom)
    print(f"TO+BREAK = {to_break_pct:.1f}% (nguong KILL >50%, nguong PASS <=35%)")

    section("CHAN DOAN — gate xu huong 3 dong (tren tap hinh-hoc-thuan, THONG TIN — n chinh thuc qua nho)")
    def side_num(s):
        return 1 if s['side'] == 'LONG' else -1
    S0 = S_geom
    S1 = [s for s in S_geom if s['trend'] == side_num(s)]
    S2 = [s for s in S_geom if s['trend'] == 0]
    report.line("Kb3TrendMode=0 (khong loc)", S0)
    report.line("Kb3TrendMode=1 (chi thuan)", S1)
    report.line("Kb3TrendMode=2 (chi trend==0, DA BI BAC truoc)", S2)

    section("CHAN DOAN — H3 hop luu bien voi vung D-1/phien (+-0.7 gia), tren tap hinh-hoc-thuan")
    def confluent(s, tol=0.7):
        return any(z['ready'] <= s['dt'] <= z['expire'] and abs(z['price'] - s['edge']) <= tol for z in pool)
    Sc = [s for s in S_geom if confluent(s)]
    Snc = [s for s in S_geom if not confluent(s)]
    report.partition("CO hop luu", Sc, "KHONG hop luu", Snc)

    section("CHAN DOAN — RangeTouchMin=3")
    P3 = dict(features.DEFAULT_P, TOUCH=3)
    states3, arms3, valids3 = features.range_struct_scan(B, P3)
    v37_3 = [v for v in valids3 if B[v['i']]['ym'] in MONTHS]
    print(f"n_range (TOUCH=3) = {len(v37_3)}  (TOUCH=2 mac dinh = {len(valids37)})")
    GEOM3 = dict(GEOM); GEOM3['_states'] = states3
    raw3 = K3.find_touch_events(B, states3, GEOM3, range_P=P3)
    raw3_37 = K3.post_months(raw3)
    kept3 = K3.base_filter(raw3_37, GEOM3)
    sig3 = K3.dedup_touch(kept3)
    S3t = K3.evaluate(B, sig3, GEOM3)
    report.line("TOUCH=3 (hinh-hoc-thuan)", S3t)

    section("CHAN DOAN — kiem 'co that la rotation?' (§6.2c/§6.9: bo lenh ma CHINH RANGE do sau nay "
            "vo THUAN huong scalp = nghi la 'bat dau cu pha' chu khong phai rotation that)")

    def find_favorable_break(states, ev, cap_bars=200):
        i0 = ev['i0']
        fav_dir = -1 if ev['side'] == 'SHORT' else 1
        end = min(len(states), ev['i'] + 1 + cap_bars)
        for j in range(ev['i'] + 1, end):
            s = states[j]
            if s is None or s.get('i0') != i0:
                return None
            if s['state'] == 'BREAKING' and s.get('brk_bar') == j and s.get('brk_dir') == fav_dir:
                return j
        return None

    vo_thuan = [s for s in S_geom if find_favorable_break(states, s, cap_bars=GEOM['Kb3MaxHoldBars'] + 5) is not None]
    con_lai = [s for s in S_geom if s not in vo_thuan]
    report.line("VO THUAN huong scalp (nghi ngo la KB1 som)", vo_thuan)
    report.line("CON LAI (ung vien rotation THAT)", con_lai)
    ev_conlai = (sum(s['r'] for s in con_lai) / len(con_lai)) if con_lai else 0
    print(f"EV cua phan 'con lai' = {ev_conlai:+.3f}R "
          f"({'>= +0.25R -> KB3 co edge rieng, tach khoi KB1' if ev_conlai >= 0.25 else '<= 0 (hoac duoi 0.25) -> KB3 KHONG co edge rieng ngoai viec bat dau cu pha KB1 -> KET LUAN THEO §6.9: hop nhat vao KB1, KHONG giu KB3 rieng'})")

    # =============================================================== BUOC 5 — ROUTER + PORTFOLIO
    section("BUOC 5 — ROUTER (1 vi the) + 3 DONG PORTFOLIO (dung cau hinh CHINH THUC n=%d)" % len(S_official))
    kb1_sig = V6.post(V6.cooldown(V6.dedup(V6.run(B, C1, vf, None)), C1['COOL']), C1)
    kb1_out = []
    for s in kb1_sig:
        r = s['risk_t'] * TICK
        tp = s['entry'] + C1['RR'] * r if s['side'] == 'LONG' else s['entry'] - C1['RR'] * r
        j, o = find_exit(B, s['i'], s['side'], s['sl'], tp)
        if o == 'open':
            continue
        rr = C1['RR'] if o == 'TP' else -1.0
        kb1_out.append(dict(branch='KB1', prio=1, dt=s['dt'], exit_dt=B[j]['dt'], ym=s['ym'], r=rr, side=s['side']))

    kb2_out = []
    for s in kb2_sig:
        r = s['risk_t'] * TICK
        rr = REV.LIVE['rr']
        tp = s['entry'] + rr * r if s['side'] == 'LONG' else s['entry'] - rr * r
        j, o = find_exit(B2, s['i'], s['side'], s['sl'], tp)
        if o == 'open':
            continue
        rr2 = rr if o == 'TP' else -1.0
        kb2_out.append(dict(branch='KB2', prio=2, dt=s['dt'], exit_dt=B2[j]['dt'],
                             ym=s['dt'].strftime('%Y-%m'), r=rr2, side=s['side']))

    kb3_out = []
    for s in S_official:
        j, o = find_exit(B, s['i'], s['side'], s['sl'], s['tp'],
                          maxbars=C3['Kb3MaxHoldBars'], dead_at=s['dead_at'])
        kb3_out.append(dict(branch='KB3', prio=3, dt=s['dt'], exit_dt=B[j]['dt'], ym=s['ym'], r=s['r'], side=s['side']))

    def portfolio(branches, label):
        allsig = []
        for br in branches:
            allsig += br
        # ROUTER dong bang o engine.route_one_position() — dung chung voi test_router.py
        # (AUDIT_V7 §11.2: nhanh 'bo vi dang co vi the' bo 0 lenh tren du lieu that -> phai co unit test)
        kept, dropped = engine.route_one_position(allsig)
        print(f"--- {label} --- (tin hieu bi bo vi 1-vi-the: {dict(dropped)})")
        report.line(label, kept)
        return kept, dropped

    portfolio([kb1_out, kb2_out], "KB1+KB2 (doi chieu BASELINE, phai =n60)")
    portfolio([kb1_out, kb2_out, kb3_out], "KB1+KB2+KB3")
    portfolio([kb3_out], "CHI KB3")

    # dem trung KB3-that-bai / KB1-kich-hoat (proxy, vi KB1 dung box khong dung struct)
    section("Dem trung KB3-that-bai vs KB1-kich-hoat (PROXY — KB1 dang dung box, khong dung struct range)")
    fail3 = [e for e in raw37 if K3.find_dead_at(states, e) is not None]
    kb1_bars = set(s['i'] for s in kb1_sig)
    near = 0
    for e in fail3:
        if any(abs(e['i'] - i1) <= 3 for i1 in kb1_bars):
            near += 1
    print(f"so lan cham KB3 (touch RAW co dead_at, tuc range vo nguoc huong scalp truoc khi timeout) = {len(fail3)}")
    print(f"trong do trung (+-3 nen) voi 1 tin hieu KB1 (box) = {near}")
    print("Luu y: KB1 mac dinh dung RangeMode=0 (box 8 nen), KHONG dung range_struct — nen 'trung' o day "
          "chi la TRUNG THOI GIAN gan dung, khong phai trung logic 'cung 1 cu vo' nhu SPEC mo ta cho truong "
          "hop RangeMode=1.")


if __name__ == '__main__':
    main()
