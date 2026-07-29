#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
f_oos.py — MUC F: OOS THAT tren cua so 2025-11 -> 2026-04 (chua tung dung de tinh chinh).

Chay cau hinh CHOT cua KB1 / KB2 / KB3 / portfolio, KHONG tinh chinh gi, in theo TUNG THANG.

3 bien the volfloor (vi day chinh la cho look-ahead da phat hien o muc A):
  (V1) vf = E.calc_volfloor(B) = 17.0  -> nguong nay tinh tu volume thang 5-7/2026, tuc
       TOAN BO tu TUONG LAI cua cua so OOS. Chay de bao dung "cau hinh chot khong doi".
  (V2) vf = 20.0 (so CUNG trong RunnerSignal.cs) -> khong look-ahead, la cai THUC SU ship.
  (V3) vf cuon nhan-qua (percentile-30 cua 1000 nen truoc) -> cho cua so OOS mot co hoi
       CONG BANG; day la CHAN DOAN (doi gate), khong phai cau hinh chot.

Kem theo: do do DAY cua du lieu OOS (so nen qua gate) de biet ket qua rong la do "khong co
edge" hay do "hop dong chua giao dich".
"""
import sys, os
from collections import defaultdict, deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib as L
import entry_dxfeed as E
import cbr_v6 as V6
import features, engine, report
import imp_reversal_sweep as REV
import s3_edge2edge as K3

OOS = ('2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-04')
INS = ('2026-05', '2026-06', '2026-07')


def hdr(t):
    print("\n" + "=" * 118); print(t); print("=" * 118)


def causal_vf(B, win=1000, warm=200):
    q = deque()
    for b in B:
        if len(q) >= warm:
            s = sorted(q); b['_vf'] = max(5.0, s[int(len(s) * 0.30)])
        else:
            b['_vf'] = 5.0
        q.append(b['v'])
        if len(q) > win:
            q.popleft()


def scan_kb1(B, C, vf, months, use_causal=False):
    L.months_patch(months)
    if not use_causal:
        return V6.scan(B, C, vf, None)
    orig = V6._gate
    V6._gate = lambda b, v: (b['v'] >= b['_vf'] and b['since_gap'] >= E.WARMUP_AFTER_GAP
                             and b['vma'] >= b['_vf'] * 0.6)
    try:
        return V6.scan(B, C, 0.0, None)
    finally:
        V6._gate = orig


def main():
    B = E.load_m1(); V6.prepare(B); causal_vf(B)
    vf_look = E.calc_volfloor(B)

    # ---------------------------------------------------------------- 0. do DAY du lieu
    hdr("F.0 — DO DAY DU LIEU cua cua so OOS (truoc khi ket luan bat ky dieu gi)")
    stt = defaultdict(lambda: [0, 0, 0, 0])
    days = defaultdict(set)
    for b in B:
        s = stt[b['ym']]; s[0] += 1
        days[b['ym']].add(b['dt'].date())
        if b['v'] >= vf_look: s[1] += 1
        if b['v'] >= 20: s[2] += 1
        if V6._gate(b, vf_look): s[3] += 1
    print(f"  {'thang':9s} {'n_nen':>7s} {'n_ngay':>7s} {'nen/ngay':>9s} {'v>=17':>7s} {'v>=20':>7s} {'_gate OK':>9s}")
    for m in list(OOS) + list(INS):
        s = stt[m]
        print(f"  {m:9s} {s[0]:7d} {len(days[m]):7d} {s[0]/max(1,len(days[m])):9.0f} "
              f"{s[1]:7d} {s[2]:7d} {s[3]:9d}")
    g_oos = sum(stt[m][3] for m in OOS)
    g_ins = sum(stt[m][3] for m in INS)
    print(f"\n  nen qua _gate: OOS(6 thang)={g_oos}   IN-SAMPLE(3 thang)={g_ins}   "
          f"ty le OOS/IS = {100*g_oos/max(1,g_ins):.2f}%")

    C1 = V6.cfg(CLEAN=True, PMAX=1.00, RR=4.0)

    # ---------------------------------------------------------------- 1. KB1
    hdr("F.1 — KB1 (cau hinh CHOT: CLEAN=True PMAX=1.00 RR=4.0, RangeMode=0, BIAS_ON=False)")
    print("  [moc so] IN-SAMPLE 5-7/2026:")
    S_is = scan_kb1(B, C1, vf_look, INS)
    d_is = L.line2("KB1 in-sample (vf=17)", S_is, INS)
    print("\n  [OOS] 2025-11 -> 2026-04:")
    res = {}
    for tag, vf, cau in [("V1 vf=17.0 (look-ahead tu tuong lai)", vf_look, False),
                          ("V2 vf=20.0 (C# hardcode, khong LA)", 20.0, False),
                          ("V3 vf cuon nhan-qua (CHAN DOAN)", None, True)]:
        S = scan_kb1(B, C1, vf, OOS, use_causal=cau)
        res[tag] = L.line2("KB1 OOS " + tag, S, OOS)

    # ---------------------------------------------------------------- 2. KB2
    hdr("F.2 — KB2 QUAY_DAU (cau hinh CHOT: LIVE params, vol_floor=20 hardcode, rr=1.5)")
    B2 = REV.bars()
    sig_all = REV.detect(B2)
    print(f"  tong tin hieu QUAY_DAU tren TOAN 9 thang (LIVE params) = {len(sig_all)}")
    for label, ms in [("IN-SAMPLE 5-7/2026", INS), ("OOS 2025-11->2026-04", OOS)]:
        ss = [s for s in sig_all if s['dt'].strftime('%Y-%m') in ms]
        r = REV.score(B2, ss, REV.LIVE['rr'])
        REV.fmt(r, f"KB2 {label}")
    print("\n  [CHAN DOAN] ha vol_floor cho OOS mot co hoi cong bang (vol_floor=2, warmup giu 20):")
    sig_lo = REV.detect(B2, vol_floor=2)
    for label, ms in [("IN-SAMPLE (vf=2)", INS), ("OOS (vf=2)", OOS)]:
        ss = [s for s in sig_lo if s['dt'].strftime('%Y-%m') in ms]
        r = REV.score(B2, ss, REV.LIVE['rr'])
        REV.fmt(r, f"KB2 {label}")

    # ---------------------------------------------------------------- 3. KB3
    hdr("F.3 — KB3 (da KILL o GD7; chay lai 'ban tran' + hinh-hoc-thuan tren OOS de doi chieu)")
    states, arms, valids = features.range_struct_scan(B)
    P = dict(features.DEFAULT_P)
    for label, ms in [("IN-SAMPLE", INS), ("OOS", OOS)]:
        C3 = K3.cfg(); C3['_states'] = states
        raw = [e for e in K3.find_touch_events(B, states, C3, range_P=P) if e['ym'] in ms]
        kept = K3.base_filter(raw, C3)
        S = K3.evaluate(B, K3.dedup_touch(kept), C3)
        print(f"  {label}: so lan cham RAW={len(raw)}  sau ban tran n={len(S)}")
        L.line2(f"KB3 ban tran {label}", S, ms)
        G = K3.cfg(LIQ=False, Kb3VsaMin=0, Kb3WickFrac=0, CPOS_SHORT=1.0, CPOS_LONG=0.0, Kb3ExtremeWin=1)
        G['_states'] = states
        rawG = [e for e in K3.find_touch_events(B, states, G, range_P=P) if e['ym'] in ms]
        SG = K3.evaluate(B, K3.dedup_touch(K3.base_filter(rawG, G)), G)
        L.line2(f"KB3 hinh-hoc-thuan {label}", SG, ms)
    nvr = defaultdict(int)
    for v in valids:
        nvr[B[v['i']]['ym']] += 1
    print(f"\n  so range VALID theo thang: " + " ".join(f"{m[2:]}={nvr.get(m,0)}" for m in list(OOS)+list(INS)))

    # ---------------------------------------------------------------- 4. PORTFOLIO
    hdr("F.4 — PORTFOLIO (KB1+KB2, 1 vi the) IN-SAMPLE vs OOS")
    for label, ms, vf in [("IN-SAMPLE", INS, vf_look), ("OOS (vf=20)", OOS, 20.0)]:
        S1 = scan_kb1(B, C1, vf, ms)
        s2 = [s for s in sig_all if s['dt'].strftime('%Y-%m') in ms]
        rows = []
        for s in S1:
            rows.append(dict(ym=s['ym'], dt=s['dt'], r=s['r'], risk_t=s['risk_t'], branch='KB1'))
        for s in s2:
            r = s['risk_t'] * L.TICK
            tgt = s['entry'] + REV.LIVE['rr'] * r if s['side'] == 'LONG' else s['entry'] - REV.LIVE['rr'] * r
            import reversal_vwap as rv
            o = rv.hit(B2, s['i'], s['side'], s['sl'], tgt)
            if o not in ('TP', 'SL', 'amb'):
                continue
            rows.append(dict(ym=s['dt'].strftime('%Y-%m'), dt=s['dt'],
                             r=(REV.LIVE['rr'] if o == 'TP' else -1.0), risk_t=s['risk_t'], branch='KB2'))
        rows.sort(key=lambda x: x['dt'])
        L.line2(f"PORTFOLIO {label}", rows, ms)

    hdr("F — KET LUAN VE TINH KHA THI CUA PHEP KIEM OOS")
    print(f"  OOS co {g_oos} nen qua _gate tren 6 thang; IN-SAMPLE co {g_ins} nen tren 3 thang.")
    print(f"  => cua so OOS chi co {100*g_oos/max(1,g_ins):.2f}% luong nen 'giao dich duoc' so voi in-sample.")
    print("  Doc ket qua o F.1-F.4 CUNG voi con so nay truoc khi phan xu.")


if __name__ == '__main__':
    main()
