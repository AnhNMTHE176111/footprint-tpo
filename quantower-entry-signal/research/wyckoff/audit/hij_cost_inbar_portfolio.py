#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hij_cost_inbar_portfolio.py — MUC H (chi phi), MUC I (gia dinh trong nen), MUC J (portfolio).

H: them chi phi CO DINH 1/2/3 tick moi lenh (round-trip spread+slippage), quy ve R cua chinh
   lenh do (dR = cost_tick / risk_t). Tim nguong chi phi ma edge chet.
I: dem so lenh ma CA SL VA TP nam trong CUNG mot nen (engine gia dinh SL truoc = bi quan);
   chay lai voi gia dinh NGUOC (TP truoc) de biet BIEN DO BAT DINH.
J: kiem portfolio — chong thoi gian, dem 2 lan, tong R.
"""
import sys, os
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib as L
import entry_dxfeed as E
import cbr_v6 as V6
import features, engine, report
import imp_reversal_sweep as REV
import reversal_vwap as rv
import s3_edge2edge as K3

INS = ('2026-05', '2026-06', '2026-07')
TICK = E.TICK


def hdr(t):
    print("\n" + "=" * 118); print(t); print("=" * 118)


# ------------------------------------------------------------------ I: gia dinh trong nen
def hit_dir(B, i, side, sl, tp, sl_first=True, maxbars=None, dead_at=None, entry_px=None):
    """Ban sao hit_v7 nhung DAO duoc thu tu SL/TP + tra ve co 'ambiguous' (ca 2 trong 1 nen)."""
    for j in range(i + 1, len(B)):
        b = B[j]
        hs = (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl)
        ht = (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp)
        if hs and ht:
            return ('SL' if sl_first else 'TP'), None, True
        if hs:
            return 'SL', -1.0, False
        if ht:
            return 'TP', None, False
        if dead_at is not None and j >= dead_at:
            r = (b['c'] - entry_px) if side == 'LONG' else (entry_px - b['c'])
            return 'BREAK', r / abs(entry_px - sl), False
        if maxbars is not None and j - i >= maxbars:
            r = (b['c'] - entry_px) if side == 'LONG' else (entry_px - b['c'])
            return 'TO', r / abs(entry_px - sl), False
    return 'open', 0.0, False


def kb1_sig(B, C, vf):
    return V6.post(V6.cooldown(V6.dedup(V6.run(B, C, vf, None)), C['COOL']), C)


def eval_kb1(B, sig, C, sl_first=True):
    out = []
    for s in sig:
        r = s['risk_t'] * TICK
        tp = s['entry'] + C['RR'] * r if s['side'] == 'LONG' else s['entry'] - C['RR'] * r
        o, rx, amb = hit_dir(B, s['i'], s['side'], s['sl'], tp, sl_first=sl_first, entry_px=s['entry'])
        if o == 'open':
            continue
        s2 = dict(s); s2['r'] = C['RR'] if o == 'TP' else (-1.0 if o == 'SL' else rx)
        s2['amb'] = amb; s2['outcome'] = o
        out.append(s2)
    return out


def eval_kb2(B2, sigs, rr, sl_first=True):
    out = []
    for s in sigs:
        r = s['risk_t'] * TICK
        tp = s['entry'] + rr * r if s['side'] == 'LONG' else s['entry'] - rr * r
        o, rx, amb = hit_dir(B2, s['i'], s['side'], s['sl'], tp, sl_first=sl_first, entry_px=s['entry'])
        if o == 'open':
            continue
        s2 = dict(s); s2['ym'] = s['dt'].strftime('%Y-%m')
        s2['r'] = rr if o == 'TP' else -1.0
        s2['amb'] = amb; s2['outcome'] = o
        out.append(s2)
    return out


def eval_kb3(B, events, C, sl_first=True):
    out = []
    states = C['_states']
    for ev in events:
        da = K3.find_dead_at(states, ev, cap_bars=C['Kb3MaxHoldBars'] + 5)
        o, rx, amb = hit_dir(B, ev['i'], ev['side'], ev['sl'], ev['tp'], sl_first=sl_first,
                             maxbars=C['Kb3MaxHoldBars'], dead_at=da, entry_px=ev['entry'])
        if o == 'open':
            continue
        e2 = dict(ev); e2['outcome'] = o; e2['amb'] = amb
        e2['r'] = ev['rr_avail'] if o == 'TP' else (-1.0 if o == 'SL' else rx)
        out.append(e2)
    return out


def main():
    B = E.load_m1(); V6.prepare(B)
    vf = E.calc_volfloor(B)
    L.months_patch(INS)
    C1 = V6.cfg(CLEAN=True, PMAX=1.00, RR=4.0)
    sig1 = kb1_sig(B, C1, vf)
    S1 = eval_kb1(B, sig1, C1, sl_first=True)

    B2 = REV.bars()
    sig2 = REV.in_window(B2, REV.detect(B2))
    S2 = eval_kb2(B2, sig2, REV.LIVE['rr'], sl_first=True)

    states, arms, valids = features.range_struct_scan(B)
    P = dict(features.DEFAULT_P)
    C3 = K3.cfg(); C3['_states'] = states
    raw3 = K3.post_months(K3.find_touch_events(B, states, C3, range_P=P))
    S3 = eval_kb3(B, K3.dedup_touch(K3.base_filter(raw3, C3)), C3, sl_first=True)
    G = K3.cfg(LIQ=False, Kb3VsaMin=0, Kb3WickFrac=0, CPOS_SHORT=1.0, CPOS_LONG=0.0, Kb3ExtremeWin=1)
    G['_states'] = states
    rawG = K3.post_months(K3.find_touch_events(B, states, G, range_P=P))
    S3g = eval_kb3(B, K3.dedup_touch(K3.base_filter(rawG, G)), G, sl_first=True)

    print(f"[doi chieu] KB1 n={len(S1)} EV={L.ev(S1):+.3f}  KB2 n={len(S2)} EV={L.ev(S2):+.3f}  "
          f"KB3 ban tran n={len(S3)}  KB3 hinh-hoc n={len(S3g)} EV={L.ev(S3g):+.3f}")

    # ================================================================ H
    hdr("H — DO NHAY CHI PHI (spread+slippage co dinh moi lenh, tinh ca vong)")
    print("  dR = cost_tick / risk_t  (risk_t = |entry-SL| bang tick, khac nhau tung lenh)")
    rows = [("KB1 (RR4)", S1), ("KB2 QUAY_DAU (RR1.5)", S2),
            ("KB3 hinh-hoc-thuan (CHAN DOAN)", S3g), ("PORTFOLIO KB1+KB2", S1 + S2)]
    print(f"\n  {'nhanh':<32s} {'med risk_t':>10s} {'EV 0t':>8s} {'EV 1t':>8s} {'EV 2t':>8s} "
          f"{'EV 3t':>8s} {'EV 5t':>8s} {'chet tai':>9s}")
    for tag, S in rows:
        if not S:
            print(f"  {tag:<32s}  (n=0)"); continue
        import statistics as st
        mr = st.median([s['risk_t'] for s in S])
        evs = [L.ev(L.apply_cost(S, c)) for c in (0, 1, 2, 3, 5)]
        dead = next((c for c in range(0, 41) if L.ev(L.apply_cost(S, c)) <= 0), None)
        print(f"  {tag:<32s} {mr:10.1f} " + " ".join(f"{e:+8.3f}" for e in evs) +
              f" {(str(dead)+'t') if dead is not None else '>40t':>9s}")
    print("\n  Tong R sau phi (cung cua so 5-7/2026):")
    for tag, S in rows:
        if not S:
            continue
        tots = [sum(x['r'] for x in L.apply_cost(S, c)) for c in (0, 1, 2, 3, 5)]
        print(f"  {tag:<32s} " + "  ".join(f"{c}t:{t:+7.1f}R" for c, t in zip((0, 1, 2, 3, 5), tots)))
    print("\n  ⚠ SPEC §9 #4 YEU CAU moi bang KB3 phai co cot 'EV sau khi tru 2 tick/lenh'. "
          "RESULTS_KB3.md KHONG co cot nay — xem muc K.")
    print(f"  KB3 hinh-hoc-thuan: EV(0t)={L.ev(S3g):+.3f} -> EV(2t)={L.ev(L.apply_cost(S3g,2)):+.3f} "
          f"(nguong SPEC 'khong dang ship' = <+0.15R)")

    # ================================================================ I
    hdr("I — GIA DINH TRONG NEN (SL truoc TP). Bao nhieu lenh bi anh huong?")
    print(f"  {'nhanh':<32s} {'n':>4s} {'n_amb':>6s} {'%amb':>7s} {'EV SL-truoc':>12s} "
          f"{'EV TP-truoc':>12s} {'bien do':>9s}")
    band = {}
    for tag, S, ev_fn in [("KB1 (RR4)", S1, lambda: eval_kb1(B, sig1, C1, sl_first=False)),
                           ("KB2 QUAY_DAU (RR1.5)", S2, lambda: eval_kb2(B2, sig2, REV.LIVE['rr'], sl_first=False)),
                           ("KB3 ban tran (n=1)", S3, lambda: eval_kb3(B, K3.dedup_touch(K3.base_filter(raw3, C3)), C3, sl_first=False)),
                           ("KB3 hinh-hoc-thuan", S3g, lambda: eval_kb3(B, K3.dedup_touch(K3.base_filter(rawG, G)), G, sl_first=False))]:
        if not S:
            print(f"  {tag:<32s}  (n=0)"); continue
        na = sum(1 for s in S if s.get('amb'))
        S_opt = ev_fn()
        e1, e2 = L.ev(S), L.ev(S_opt)
        band[tag] = (e1, e2)
        print(f"  {tag:<32s} {len(S):4d} {na:6d} {100*na/len(S):6.1f}% {e1:+12.3f} {e2:+12.3f} "
              f"{e2-e1:+9.3f}")
    print("\n  Nguong SPEC §9 #5: >15% lenh bi anh huong => ket qua RAT NHAY voi gia dinh nay.")
    print("  (KB2 da co san outcome 'amb' trong reversal_vwap.hit(); KB1/KB3 truoc gio KHONG dem.)")

    # ================================================================ J
    hdr("J — PORTFOLIO: chong thoi gian / dem 2 lan / tong R")
    # exit bar cho tung lenh
    def exit_dt(Barr, s, tp, maxbars=None, dead_at=None):
        for j in range(s['i'] + 1, len(Barr)):
            b = Barr[j]
            if (b['lo'] <= s['sl']) if s['side'] == 'LONG' else (b['hi'] >= s['sl']):
                return Barr[j]['dt']
            if (b['hi'] >= tp) if s['side'] == 'LONG' else (b['lo'] <= tp):
                return Barr[j]['dt']
            if dead_at is not None and j >= dead_at:
                return Barr[j]['dt']
            if maxbars is not None and j - i >= maxbars:
                return Barr[j]['dt']
        return Barr[-1]['dt']

    iv = []
    for s in S1:
        r = s['risk_t'] * TICK
        tp = s['entry'] + C1['RR'] * r if s['side'] == 'LONG' else s['entry'] - C1['RR'] * r
        iv.append(dict(br='KB1', dt=s['dt'], ex=exit_dt(B, s, tp), r=s['r'], ym=s['ym'], side=s['side']))
    for s in S2:
        r = s['risk_t'] * TICK
        rr = REV.LIVE['rr']
        tp = s['entry'] + rr * r if s['side'] == 'LONG' else s['entry'] - rr * r
        iv.append(dict(br='KB2', dt=s['dt'], ex=exit_dt(B2, s, tp), r=s['r'],
                       ym=s['dt'].strftime('%Y-%m'), side=s['side']))
    iv.sort(key=lambda x: x['dt'])
    print(f"  tong lenh 2 nhanh (chua router) = {len(iv)}  (KB1 {len(S1)} + KB2 {len(S2)})")

    # J.1 chong thoi gian
    ovl = []
    for a in range(len(iv)):
        for b_ in range(a + 1, len(iv)):
            if iv[b_]['dt'] > iv[a]['ex']:
                break
            ovl.append((iv[a], iv[b_]))
    print(f"\n  J.1 so CAP lenh CHONG THOI GIAN (lenh sau vao truoc khi lenh truoc thoat) = {len(ovl)}")
    if ovl:
        cc = Counter((a['br'], b_['br']) for a, b_ in ovl)
        print(f"      phan bo theo cap nhanh: {dict(cc)}")
        print(f"      {'vao':<20s} {'nhanh':<6s} {'thoat':<20s} | {'vao (lenh chong)':<20s} {'nhanh':<6s}")
        for a, b_ in ovl[:12]:
            print(f"      {str(a['dt']):<20s} {a['br']:<6s} {str(a['ex']):<20s} | "
                  f"{str(b_['dt']):<20s} {b_['br']:<6s}")
        if len(ovl) > 12:
            print(f"      ... con {len(ovl)-12} cap nua")
    hold = [(x['ex'] - x['dt']).total_seconds() / 60 for x in iv]
    import statistics as st
    print(f"      thoi gian giu lenh (phut): med={st.median(hold):.0f} p90={sorted(hold)[int(len(hold)*.9)]:.0f} max={max(hold):.0f}")

    # J.2 router 1-vi-the
    busy = None; kept = []; drop = Counter()
    for s in iv:
        if busy is not None and s['dt'] <= busy:
            drop[s['br']] += 1; continue
        kept.append(s); busy = s['ex']
    print(f"\n  J.2 router 1-vi-the: giu {len(kept)}  bo {dict(drop)}  (BASELINE.md/RESULTS_KB3.md bao n=60, bo {{}})")
    L.line2("PORTFOLIO sau router (audit tu tinh)", kept, INS)
    L.line2("PORTFOLIO cong gop khong router", iv, INS)

    # J.3 dem 2 lan
    key = Counter((x['br'], x['dt'], x['side']) for x in iv)
    dup = {k: v for k, v in key.items() if v > 1}
    print(f"\n  J.3 lenh bi dem 2 lan (cung nhanh+dt+side) = {len(dup)}")
    same_ts = Counter(x['dt'] for x in iv)
    print(f"      moc thoi gian co >1 lenh (khac nhanh) = {sum(1 for v in same_ts.values() if v>1)}")

    # J.4 tong R
    print(f"\n  J.4 tong R: KB1={sum(s['r'] for s in S1):+.1f}  KB2={sum(s['r'] for s in S2):+.1f}  "
          f"cong={sum(s['r'] for s in S1)+sum(s['r'] for s in S2):+.1f}  "
          f"portfolio-baseline(bao cao)=+57.5  sau router(audit)={sum(x['r'] for x in kept):+.1f}")


if __name__ == '__main__':
    main()
