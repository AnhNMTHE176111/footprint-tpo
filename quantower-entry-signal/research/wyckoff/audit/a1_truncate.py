#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
a1_truncate.py — MUC A: phep kiem CAT CHUOI (phep kiem look-ahead manh nhat).

Y tuong: cat chuoi tai nen i (chi giu B[0..i]), tinh feature, so voi gia tri tinh tren
chuoi DAY DU tai dung nen i. KHAC NHAU = look-ahead.

Kiem 8 feature (yeu cau brief: >=5):
  1. volfloor  (entry_dxfeed.calc_volfloor)         <- NGHI PHAM CHINH
  2. liqratio  (cbr_v6.prepare, cuon 1000 nen)
  3. trend     (cbr_v6.prepare, close vs close[-480] + tol)
  4. vwap      (entry_dxfeed.load_m1, reset gap>30')
  5. vma/vratio(SMA20 volume)
  6. session_bias (features.session_bias_series)
  7. range_struct state (features.range_struct_scan) tai nen i
  8. build_zones (so zone 'ready<=t' tai thoi diem nen i)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib as L
import entry_dxfeed as E
import cbr_v6 as V6
import features


def hdr(t):
    print("\n" + "=" * 110); print(t); print("=" * 110)


def main():
    RAW = L.raw_rows()
    B_full = L.derive(RAW)
    V6.prepare(B_full)

    # --- sanity: derive() phai == E.load_m1() truoc khi dung lam bang chung ---
    B_ref = E.load_m1(); V6.prepare(B_ref)
    assert len(B_ref) == len(B_full), "derive() lech so nen"
    bad = 0
    for a, b in zip(B_ref, B_full):
        for k in ('dt', 'c', 'vwap', 'vma', 'vratio', 'brat', 'cpos', 'since_gap', 'trend', 'liqratio'):
            if a[k] != b[k]:
                bad += 1; break
    print(f"[sanity] derive() vs entry_dxfeed.load_m1(): {len(B_full)} nen, so nen lech = {bad}")
    assert bad == 0, "derive() KHONG tai lap duoc load_m1 -> khong dung lam bang chung"

    # chon 5 diem cat rai deu trong cua so IN-SAMPLE 5-7/2026
    idx_is = [i for i, b in enumerate(B_full) if b['ym'] in ('2026-05', '2026-06', '2026-07')]
    CUTS = [idx_is[int(len(idx_is) * f)] for f in (0.10, 0.30, 0.50, 0.70, 0.90)]

    hdr("A.1 — volfloor  (E.calc_volfloor: percentile-30 volume cua MOI nen ym>=2026-05)")
    print(f"  volfloor tren chuoi DAY DU (dung trong moi backtest) = {E.calc_volfloor(B_full)}")
    print(f"  {'cut tai i':>10s} {'dt':>20s} {'vf(chuoi cat)':>14s} {'vf(day du)':>11s} {'LECH?':>6s}")
    vf_full = E.calc_volfloor(B_full)
    n_diff = 0
    for i in CUTS:
        vf_cut = E.calc_volfloor(B_full[:i + 1])
        d = abs(vf_cut - vf_full) > 1e-9
        n_diff += d
        print(f"  {i:10d} {str(B_full[i]['dt']):>20s} {vf_cut:14.1f} {vf_full:11.1f} {'KHAC' if d else 'ok':>6s}")
    print(f"  ==> {n_diff}/{len(CUTS)} diem cat cho volfloor KHAC nhau => "
          f"{'LOOK-AHEAD XAC NHAN' if n_diff else 'khong look-ahead'}")

    hdr("A.2-A.5 — feature theo nen (liqratio / trend / vwap / vma / vratio / cpos)")
    print(f"  {'cut i':>8s} {'liqratio':>18s} {'trend':>10s} {'vwap':>18s} {'vma':>16s} {'vratio':>16s}")
    all_ok = True
    for i in CUTS:
        Bc = L.derive(RAW[:i + 1]); V6.prepare(Bc)
        a, b = Bc[i], B_full[i]
        row = []
        for k in ('liqratio', 'trend', 'vwap', 'vma', 'vratio'):
            same = abs(a[k] - b[k]) < 1e-12
            all_ok &= same
            row.append(f"{'ok' if same else 'KHAC'}({a[k]:.6g}/{b[k]:.6g})")
        print(f"  {i:8d} {row[0]:>18s} {row[1]:>10s} {row[2]:>18s} {row[3]:>16s} {row[4]:>16s}")
    print(f"  ==> {'TAT CA KHOP => khong look-ahead o 5 feature nay' if all_ok else 'CO LECH => look-ahead'}")

    hdr("A.6 — session_bias (features.session_bias_series) tai nen i")
    bias_full, _ = features.session_bias_series(B_full)
    ok6 = True
    print(f"  {'cut i':>8s} {'bias(cat)':>10s} {'bias(day du)':>13s} {'KQ':>6s}")
    for i in CUTS:
        Bc = L.derive(RAW[:i + 1]); V6.prepare(Bc)
        bc, _ = features.session_bias_series(Bc)
        same = bc[i] == bias_full[i]
        ok6 &= same
        print(f"  {i:8d} {bc[i]:10d} {bias_full[i]:13d} {'ok' if same else 'KHAC':>6s}")
    print(f"  ==> {'KHOP' if ok6 else 'LECH => look-ahead'}")

    hdr("A.7 — range_struct_scan: trang thai range tai nen i")
    st_full, arms_full, valids_full = features.range_struct_scan(B_full)
    ok7 = True
    print(f"  {'cut i':>8s} {'state(cat)':>12s} {'state(day du)':>14s} {'rhi/rlo cat':>16s} {'rhi/rlo day du':>16s} {'KQ':>6s}")
    for i in CUTS:
        Bc = L.derive(RAW[:i + 1]); V6.prepare(Bc)
        sc, _, _ = features.range_struct_scan(Bc)
        A, Bb = sc[i], st_full[i]
        same = (A.get('state') == Bb.get('state') and A.get('i0') == Bb.get('i0')
                and A.get('rhi') == Bb.get('rhi') and A.get('rlo') == Bb.get('rlo'))
        ok7 &= same
        f = lambda z: (f"{z.get('rhi'):.1f}/{z.get('rlo'):.1f}" if z.get('rhi') is not None else "-")
        print(f"  {i:8d} {A.get('state',''):>12s} {Bb.get('state',''):>14s} "
              f"{f(A):>16s} {f(Bb):>16s} {'ok' if same else 'KHAC':>6s}")
    print(f"  ==> {'KHOP' if ok7 else 'LECH => look-ahead'}")

    hdr("A.8 — build_zones: so zone da 'ready' tai thoi diem nen i")
    pool_full = E.build_zones(B_full)
    ok8 = True
    print(f"  {'cut i':>8s} {'n_zone ready(cat)':>18s} {'n_zone ready(day du)':>21s} {'KQ':>6s}")
    for i in CUTS:
        t = B_full[i]['dt']
        Bc = L.derive(RAW[:i + 1])
        pc = E.build_zones(Bc)
        nc = sum(1 for z in pc if z['ready'] <= t <= z['expire'])
        nf = sum(1 for z in pool_full if z['ready'] <= t <= z['expire'])
        same = nc == nf
        ok8 &= same
        print(f"  {i:8d} {nc:18d} {nf:21d} {'ok' if same else 'KHAC':>6s}")
    print(f"  ==> {'KHOP' if ok8 else 'LECH => look-ahead'}")

    hdr("A — anh huong THUC TE cua look-ahead volfloor len ket qua KB1")
    import engine, report
    vf_look = E.calc_volfloor(B_full)          # 17.0  <- nhin toan bo 5-7/2026
    C = V6.cfg(CLEAN=True, PMAX=1.00, RR=4.0)
    print("  KB1 voi volfloor NHIN TRUOC (nhu GD6 dang chay):")
    S_look = V6.scan(B_full, C, vf_look, None)
    d1 = report.line(f"  vf={vf_look} (look-ahead)", S_look)
    print("  KB1 voi volfloor CUON NHAN-QUA (percentile-30 cua 1000 nen truoc do, moi nen 1 nguong):")
    S_caus = scan_causal_vf(B_full, C)
    d2 = report.line("  vf cuon nhan-qua", S_caus)
    print("  KB1 voi volfloor = 20 (dung so CUNG cua C# RunnerSignal.cs — khong nhin truoc):")
    S_c20 = V6.scan(B_full, C, 20.0, None)
    d3 = report.line("  vf=20 (C# hardcode)", S_c20)


def scan_causal_vf(B, C):
    """Thay `vf` co dinh (percentile toan cua so) bang nguong CUON NHAN-QUA: tai nen i, vf =
    percentile-30 volume cua 1000 nen TRUOC do. Thuc hien bang cach ghi vf_i vao tung nen roi
    tam thay cbr_v6._gate — KHONG sua file cbr_v6.py (patch runtime trong pha audit)."""
    from collections import deque
    q = deque()
    for b in B:
        if len(q) >= 200:
            s = sorted(q); b['_vf'] = max(5.0, s[int(len(s) * 0.30)])
        else:
            b['_vf'] = 5.0
        q.append(b['v'])
        if len(q) > 1000:
            q.popleft()
    orig = V6._gate
    V6._gate = lambda b, vf: (b['v'] >= b['_vf'] and b['since_gap'] >= E.WARMUP_AFTER_GAP
                              and b['vma'] >= b['_vf'] * 0.6)
    try:
        return V6.scan(B, C, 0.0, None)
    finally:
        V6._gate = orig


if __name__ == '__main__':
    main()
