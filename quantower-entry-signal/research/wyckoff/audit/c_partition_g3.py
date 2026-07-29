#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
c_partition_g3.py — MUC C (tu tinh lai moi partition) + MUC G ket luan (loai thang 6 hong).

C: GD6/GD7 KHONG tuyen bo bo loc nao PASS. Nen viec cua muc C la:
   (a) kiem tinh TOAN VEN cua tung phan hoach (2 nhom roi nhau, hop lai = dung pool goc);
   (b) kiem lai chinh phan xu KILL — co bo loc nao bi KILL OAN (that ra PASS) khong;
   (c) them SAI SO CHUAN cho moi chenh lech EV — de biet "sat nguong 0.30" la that hay la nhieu.

G3: chay lai doi chung 2 nguon SAU KHI LOAI THANG 6 (thang co cot Volume cua fp-m1 hong 74%,
    xem g2_volume_diff.py) va dung CUNG volfloor=20 -> phep doi chung SACH.
"""
import sys, os, math, statistics as st
from datetime import timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib as L
import entry_dxfeed as E
import cbr_v6 as V6
import features, engine, report
import imp_reversal_sweep as REV
import s3_edge2edge as K3
import loaders

INS = ('2026-05', '2026-06', '2026-07')
CLEAN2 = ('2026-05', '2026-07')


def hdr(t):
    print("\n" + "=" * 118); print(t); print("=" * 118)


def se_gap(A, B):
    """Sai so chuan cua (EV_A - EV_B) cho 2 mau doc lap."""
    def v(S):
        rs = [s['r'] for s in S]
        return (st.variance(rs) if len(rs) > 1 else 0.0), len(rs)
    va, na = v(A); vb, nb = v(B)
    return math.sqrt(va / max(1, na) + vb / max(1, nb))


def show(tag_k, K, tag_d, D, pool_n, thr=0.30):
    ek, ed = L.ev(K), L.ev(D)
    gap = ek - ed
    se = se_gap(K, D)
    t = gap / se if se > 1e-9 else 0.0
    union_ok = (len(K) + len(D) == pool_n)
    print(f"  {tag_k:<30s} n={len(K):3d} EV={ek:+.3f}   |  {tag_d:<26s} n={len(D):3d} EV={ed:+.3f}")
    print(f"     gap={gap:+.3f}  SE={se:.3f}  t={t:+.2f}  "
          f"KTC95=[{gap-1.96*se:+.3f},{gap+1.96*se:+.3f}]  "
          f"| roi-nhau&hop-du: {'OK' if union_ok else f'SAI ({len(K)}+{len(D)} != {pool_n})'}"
          f"  | phan xu: {'PASS' if (gap >= thr and len(D) >= 10) else 'KILL'}"
          f"  | co the phan biet voi 0? {'CO' if abs(t) >= 1.96 else 'KHONG'}")


def main():
    B = E.load_m1(); V6.prepare(B); vf = E.calc_volfloor(B)
    L.months_patch(INS)
    Cb = dict(CLEAN=True, PMAX=1.00, RR=4.0)

    hdr("C.1 — KB1 / bias TPO (pool A3: TREND=False, BIAS_ON=False)")
    bias_at, blog = features.session_bias_series(B)
    C3 = V6.cfg(TREND=False, BIAS_ON=False, **Cb)
    sig3 = V6.post(V6.cooldown(V6.dedup(engine.run_box(B, C3, vf, bias_at=None)), C3['COOL']), C3)
    keep = [s for s in sig3 if bias_at[s['i']] == (1 if s['side'] == 'LONG' else -1)]
    drop = [s for s in sig3 if bias_at[s['i']] != (1 if s['side'] == 'LONG' else -1)]
    K = engine.evaluate_v7(B, keep, C3); D = engine.evaluate_v7(B, drop, C3)
    pool = engine.evaluate_v7(B, sig3, C3)
    print(f"  pool A3 = {len(pool)} lenh")
    show("GIU (bias dung side)", K, "LOAI (bias sai/0)", D, len(pool))

    hdr("C.2 — KB1 / WY04 No Supply-No Demand (tren dung 33 lenh incumbent)")
    C1 = V6.cfg(**Cb)
    S1 = engine.scan_box(B, C1, vf, bias_at=None)
    ok = engine.wy04_ok(B, S1)
    K = [s for s, k in zip(S1, ok) if k]; D = [s for s, k in zip(S1, ok) if not k]
    show("CO WY04", K, "KHONG CO WY04", D, len(S1))

    hdr("C.3 — KB2 / Kb2ExtremeWin (3 window)")
    B2 = REV.bars()
    sg = REV.in_window(B2, REV.detect(B2))
    for win in (10, 20, 60):
        kp, dp = [], []
        for s in sg:
            i = s['i']; w = B2[max(0, i - win):i + 1]
            isx = (B2[i]['hi'] >= max(x['hi'] for x in w) - 1e-9) if s['side'] == 'SHORT' \
                else (B2[i]['lo'] <= min(x['lo'] for x in w) + 1e-9)
            (kp if isx else dp).append(s)

        def ev2(SS):
            out = []
            for s in SS:
                r = s['risk_t'] * L.TICK
                tp = s['entry'] + REV.LIVE['rr'] * r if s['side'] == 'LONG' else s['entry'] - REV.LIVE['rr'] * r
                import reversal_vwap as rv
                o = rv.hit(B2, s['i'], s['side'], s['sl'], tp)
                if o not in ('TP', 'SL', 'amb'):
                    continue
                out.append(dict(r=(REV.LIVE['rr'] if o == 'TP' else -1.0), ym=s['dt'].strftime('%Y-%m')))
            return out
        show(f"GIU cuc tri {win}", ev2(kp), f"LOAI (khong cuc tri {win})", ev2(dp), len(sg))

    hdr("C.4 — KB3 / hop luu vung + 'vo thuan huong' (tren tap hinh-hoc-thuan)")
    states, arms, valids = features.range_struct_scan(B)
    P = dict(features.DEFAULT_P)
    G = K3.cfg(LIQ=False, Kb3VsaMin=0, Kb3WickFrac=0, CPOS_SHORT=1.0, CPOS_LONG=0.0, Kb3ExtremeWin=1)
    G['_states'] = states
    rawG = K3.post_months(K3.find_touch_events(B, states, G, range_P=P))
    Sg = K3.evaluate(B, K3.dedup_touch(K3.base_filter(rawG, G)), G)
    pool_z = E.build_zones(B)

    def confl(s, tol=0.7):
        return any(z['ready'] <= s['dt'] <= z['expire'] and abs(z['price'] - s['edge']) <= tol
                   for z in pool_z)
    show("CO hop luu", [s for s in Sg if confl(s)], "KHONG hop luu",
         [s for s in Sg if not confl(s)], len(Sg))

    def fav(ev):
        i0 = ev['i0']; fd = -1 if ev['side'] == 'SHORT' else 1
        for j in range(ev['i'] + 1, min(len(states), ev['i'] + 1 + G['Kb3MaxHoldBars'] + 5)):
            s = states[j]
            if s is None or s.get('i0') != i0:
                return False
            if s['state'] == 'BREAKING' and s.get('brk_bar') == j and s.get('brk_dir') == fd:
                return True
        return False
    vt = [s for s in Sg if fav(s)]; cl = [s for s in Sg if not fav(s)]
    show("VO THUAN (KB1 som)", vt, "CON LAI (rotation that)", cl, len(Sg))
    print(f"  *** LUU Y: phan hoach nay dung THONG TIN TUONG LAI (range vo theo huong nao SAU khi vao).")
    print(f"      => KHONG trien khai duoc live. Nhung vi no dan toi KILL, huong look-ahead nay")
    print(f"      LAM MANH ket luan: phan co the giao dich duoc (n={len(cl)}) co EV={L.ev(cl):+.3f}.")

    # ------------------------------------------------------------------ G3
    hdr("G.7 — DOI CHUNG 2 NGUON SACH: loai thang 6 (fp-m1 hong Volume 74%), cung volfloor=20")
    raw_fp = loaders.load_fp_m1_full("fp-m1-6-month.csv")
    src = [dict(dt=b['dt'] - timedelta(hours=7), o=b['o'], hi=b['hi'], lo=b['lo'], c=b['c'], v=b['v'])
           for b in raw_fp]
    src.sort(key=lambda b: b['dt'])
    Bfp = L.derive(src); V6.prepare(Bfp)
    L.months_patch(CLEAN2)
    S_dx = V6.scan(B, V6.cfg(**Cb), 20.0, None)
    S_fp = V6.scan(Bfp, V6.cfg(**Cb), 20.0, None)
    print("  KB1, chi thang 05 + 07/2026, volfloor=20 tren CA HAI nguon:")
    L.line2("KB1 dxFeed", S_dx, CLEAN2)
    L.line2("KB1 fp-m1 (-7h)", S_fp, CLEAN2)
    a = {(s['dt'], s['side']) for s in S_dx}; b = {(s['dt'], s['side']) for s in S_fp}
    print(f"  khop tung lenh (dt,side): {len(a & b)}/{len(a)} dxFeed, {len(a & b)}/{len(b)} fp-m1  "
          f"| chi dx={len(a-b)} chi fp={len(b-a)}")
    sg_dx = [s for s in REV.detect(B2) if s['dt'].strftime('%Y-%m') in CLEAN2]
    sg_fp = [s for s in REV.detect(Bfp) if s['dt'].strftime('%Y-%m') in CLEAN2]
    REV.fmt(REV.score(B2, sg_dx, REV.LIVE['rr']), "KB2 dxFeed (05+07)")
    REV.fmt(REV.score(Bfp, sg_fp, REV.LIVE['rr']), "KB2 fp-m1 (05+07)")
    a2 = {(s['dt'], s['side']) for s in sg_dx}; b2 = {(s['dt'], s['side']) for s in sg_fp}
    print(f"  khop tung lenh: {len(a2 & b2)} | chi dx={len(a2-b2)} chi fp={len(b2-a2)}")
    same = (len(a - b) == 0 and len(b - a) == 0 and len(a2 - b2) == 0 and len(b2 - a2) == 0)
    print(f"  ==> {'2 NGUON TRUNG KHOP TUYET DOI o cac thang du lieu con nguyen' if same else 'VAN CON LECH — xem so tren'}")


if __name__ == '__main__':
    main()
