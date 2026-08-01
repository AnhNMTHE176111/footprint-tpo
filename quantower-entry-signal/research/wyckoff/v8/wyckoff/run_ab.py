#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_ab.py — P3-P6 cua PLAN_KB_ABC.md: KB-A (vung TUAN) + KB-B (vung NGAY), PLAY1+PLAY2,
ConfirmOn A/B, W_CLOSED vs W_RUNNING, doi chung ngau nhien (P4 — cong chan ca plan), quet
chi phi (P6). Dung lai report.line/partition (v7/report.py, dong bang, KHONG sua).

Chay: python3 run_ab.py
"""
import sys, os, random, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
V7 = os.path.join(WYCK, 'v7')
for p in (HERE, V8, WYCK, RESEARCH, V7):
    if p not in sys.path:
        sys.path.insert(0, p)

import entry_dxfeed as E
import zones_corven as Z
import play_touch as P1
import play_breakret as P2
import eval_intraday as EI
import report

RR = 3.0
MONTHS = ('2026-05', '2026-06', '2026-07')


def shift_lookup(lookup, delta):
    def f(dt):
        r = lookup(dt)
        if r is None:
            return None
        fr, to, hvn = r
        return fr, to, [(p + delta, c, ratio) for p, c, ratio in hvn]
    return f


def run_combo(B, lookup, sessions, starts, confirm_on=True, rr=RR, tag=""):
    s1 = P1.detect_play1(B, lookup, confirm_on=confirm_on)
    s2 = P2.detect_play2(B, lookup, confirm_on=confirm_on)
    s1 = [s for s in s1 if s['ym'] in MONTHS]
    s2 = [s for s in s2 if s['ym'] in MONTHS]
    e1 = EI.evaluate(B, s1, rr, sessions, starts)
    e2 = EI.evaluate(B, s2, rr, sessions, starts)
    for s in e1:
        s['play'] = 'PLAY1'
    for s in e2:
        s['play'] = 'PLAY2'
    return e1, e2


def combo_all(e1, e2):
    return sorted(e1 + e2, key=lambda x: x['dt'])


def print_long_short(tag, S):
    L = [s for s in S if s['side'] == 'LONG']
    Sh = [s for s in S if s['side'] == 'SHORT']
    report.line(f"{tag} :: LONG", L)
    report.line(f"{tag} :: SHORT", Sh)


def main():
    B = E.load_m1()
    sessions, starts = EI.session_ends(B)
    print(f"M1={len(B)} nen | in-sample thang: {MONTHS}")

    ser_w_closed = Z.build_zone_series(B, mode='week', causal='closed')
    ser_w_running = Z.build_zone_series(B, mode='week', causal='running')
    ser_d_closed = Z.build_zone_series(B, mode='day', causal='closed')
    ser_d_running = Z.build_zone_series(B, mode='day', causal='running')
    lk_w_closed = Z.zone_lookup_series(ser_w_closed)
    lk_w_running = Z.zone_lookup_series(ser_w_running)
    lk_d_closed = Z.zone_lookup_series(ser_d_closed)
    lk_d_running = Z.zone_lookup_series(ser_d_running)

    # ===================================================================== P3 — KB-A (vung TUAN)
    print("\n" + "=" * 124)
    print("P3 — KB-A (vung TUAN, HVN W_CLOSED), RR=3.0, ConfirmOn=True (mac dinh)")
    print("=" * 124)
    e1_wc, e2_wc = run_combo(B, lk_w_closed, sessions, starts, confirm_on=True)
    report.line("KB-A/PLAY1 (cham->dao, tuan, W_CLOSED)", e1_wc)
    print_long_short("  KB-A/PLAY1", e1_wc)
    report.line("KB-A/PLAY2 (pha->hoi->tiep, tuan, W_CLOSED)", e2_wc)
    print_long_short("  KB-A/PLAY2", e2_wc)
    kb_a_wc = combo_all(e1_wc, e2_wc)
    report.line("KB-A GOP (PLAY1+PLAY2), W_CLOSED", kb_a_wc)

    print("\n-- A/B ConfirmOn (True vs False), vung TUAN W_CLOSED --")
    e1_wc_f, e2_wc_f = run_combo(B, lk_w_closed, sessions, starts, confirm_on=False)
    kb_a_wc_noconf = combo_all(e1_wc_f, e2_wc_f)
    report.line("KB-A ConfirmOn=True ", kb_a_wc)
    report.line("KB-A ConfirmOn=False", kb_a_wc_noconf)

    print("\n-- A/B W_CLOSED vs W_RUNNING (vung TUAN, ConfirmOn=True) --")
    e1_wr, e2_wr = run_combo(B, lk_w_running, sessions, starts, confirm_on=True)
    kb_a_wr = combo_all(e1_wr, e2_wr)
    report.line("KB-A W_CLOSED ", kb_a_wc)
    report.line("KB-A W_RUNNING", kb_a_wr)

    # chon cau hinh chinh cho P4/P5/P7: ConfirmOn=True + W_CLOSED (an toan nhan qua tuyet doi)
    KBA_MAIN = kb_a_wc
    print(f"\n=> Chon cau hinh CHINH cho P4 tro di: KB-A ConfirmOn=True, W_CLOSED (n={len(KBA_MAIN)})")

    # ===================================================================== P4 — doi chung ngau nhien
    print("\n" + "=" * 124)
    print("P4 — DOI CHUNG NGAU NHIEN KB-A (dich HVN +-3 gia, 5 seed) — CONG CHAN CA PLAN")
    print("=" * 124)
    real_ev = (sum(s['r'] for s in KBA_MAIN) / len(KBA_MAIN)) if KBA_MAIN else 0.0
    report.line("KB-A THAT (W_CLOSED, ConfirmOn=True)", KBA_MAIN)
    rand_evs = []
    for seed in range(1, 6):
        rgen = random.Random(1000 + seed)
        delta = rgen.uniform(2.5, 3.5) * rgen.choice([-1, 1])
        lk_shift = shift_lookup(lk_w_closed, delta)
        e1_r, e2_r = run_combo(B, lk_shift, sessions, starts, confirm_on=True)
        kb_a_r = combo_all(e1_r, e2_r)
        d = report.line(f"KB-A NGAU NHIEN seed={seed} delta={delta:+.1f}gia", kb_a_r)
        rand_evs.append(d['ev'] if d else 0.0)
    rand_mean = st.mean(rand_evs) if rand_evs else 0.0
    gap = real_ev - rand_mean
    print(f"\nEV(that)={real_ev:+.3f}  EV(ngau nhien, TB 5 seed)={rand_mean:+.3f}  gap={gap:+.3f}")
    if gap >= 0.25:
        p4_verdict = "PASS (gap >= +0.25R) -> di tiep P5"
    elif gap < 0.10:
        p4_verdict = "KILL (gap < +0.10R) -> DUNG CA PLAN theo luat da chot truoc"
    else:
        p4_verdict = "VUNG GIUA (0.10 <= gap < 0.25) -> khong du manh de PASS, coi nhu KHONG QUA cong P4"
    print(f"==> P4 KET LUAN: {p4_verdict}")

    # ===================================================================== P5 — KB-B (vung NGAY)
    print("\n" + "=" * 124)
    print("P5 — KB-B (vung NGAY, HVN D_CLOSED), cung cau hinh voi KB-A")
    print("=" * 124)
    e1_dc, e2_dc = run_combo(B, lk_d_closed, sessions, starts, confirm_on=True)
    report.line("KB-B/PLAY1 (cham->dao, ngay, D_CLOSED)", e1_dc)
    print_long_short("  KB-B/PLAY1", e1_dc)
    report.line("KB-B/PLAY2 (pha->hoi->tiep, ngay, D_CLOSED)", e2_dc)
    print_long_short("  KB-B/PLAY2", e2_dc)
    KBB_MAIN = combo_all(e1_dc, e2_dc)
    d_a = report.line("KB-A GOP (mocso)", KBA_MAIN)
    d_b = report.line("KB-B GOP", KBB_MAIN)

    print("\n-- Kiem chung dac ta (PLAN_KB_ABC.md §6.3) --")
    n_weeks = 13
    freq_a = len(KBA_MAIN) / n_weeks
    print(f"  Tan suat KB-A: n={len(KBA_MAIN)} / {n_weeks} tuan = {freq_a:.1f} lenh/tuan "
          f"(moc CORVEN ~10/tuan; PASS neu 30<=n<=400) "
          f"=> {'PASS conformance' if 30 <= len(KBA_MAIN) <= 400 else 'LECH — dinh nghia vung/trigger co the sai'}")
    if d_a and d_b:
        order_ok = d_a['wr'] > d_b['wr']
        print(f"  Thu tu WR: WR(KB-A)={d_a['wr']:.1f}%  WR(KB-B)={d_b['wr']:.1f}%  "
              f"=> {'DUNG (WR(A)>WR(B))' if order_ok else 'NGUOC — bao ca hai kha nang (vung tuan dung sai / loi CORVEN khong dung tren cua so nay)'}")

    # ===================================================================== P6 — chi phi giao dich
    print("\n" + "=" * 124)
    print("P6 — Quet chi phi giao dich 0->8 tick/lenh (tren KB-A va KB-B, dR = cost_ticks/risk_t)")
    print("=" * 124)
    def cost_sweep(tag, S):
        print(f"  -- {tag} --")
        for cost in (0, 1, 2, 3, 4, 5, 8):
            rs = [s['r'] - (cost / s['risk_t'] if s['risk_t'] else 0) for s in S]
            ev = sum(rs) / len(rs) if rs else 0.0
            print(f"     cost={cost} tick   EV={ev:+.3f}   tong={sum(rs):+.1f}R")
    cost_sweep("KB-A", KBA_MAIN)
    cost_sweep("KB-B", KBB_MAIN)

    print("\n" + "=" * 124)
    print("HET run_ab.py — xem RESULTS_KB_AB.md de doc ket luan tong hop")
    print("=" * 124)


if __name__ == '__main__':
    main()
