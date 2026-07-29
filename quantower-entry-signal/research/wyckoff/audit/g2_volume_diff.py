#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
g2_volume_diff.py — MUC G (tiep): dinh luong CHENH LECH VOLUME giua fp-m1 va dxFeed.

g_fpm1.py phat hien: close khop 0 tick tren CA 99.678 nen, nhung VOLUME lech tren 22.297 nen
(22%), max lech 3.655 hop dong. DATA_CAPABILITY §4.1 chi kiem 1 NGAY (2026-07-10) va chi ket
luan "cung mot chuoi gia" — dung cho GIA, nhung KHONG dung cho VOLUME tren toan cua so.

Quan trong vi: `vratio = v / SMA20(v)` la GATE TRUNG TAM cua ca KB1 (BVSA=2.0) va KB2
(vsa_conf=1.8), va `volfloor`/`liqratio` cung tu volume. Volume lech => tin hieu lech.
"""
import sys, os, statistics as st
from datetime import timedelta
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib as L
import entry_dxfeed as E
import loaders


def main():
    Bdx = E.load_m1()
    raw_fp = loaders.load_fp_m1_full("fp-m1-6-month.csv")
    src = [dict(dt=b['dt'] - timedelta(hours=7), v=b['v'], c=b['c']) for b in raw_fp]
    dxm = {b['dt']: b for b in Bdx}

    print("=" * 110)
    print("G.5 — chenh lech VOLUME theo thang (close da khop 0 tick tren toan bo)")
    print("=" * 110)
    agg = defaultdict(lambda: [0, 0, 0.0, 0.0, 0.0, 0])   # n, n_diff, sum_fp, sum_dx, maxdiff, n_fp_gt
    for b in src:
        d = dxm.get(b['dt'])
        if d is None:
            continue
        m = b['dt'].strftime('%Y-%m')
        a = agg[m]
        a[0] += 1
        a[2] += b['v']; a[3] += d['v']
        if abs(b['v'] - d['v']) > 1e-9:
            a[1] += 1
            a[4] = max(a[4], abs(b['v'] - d['v']))
            if b['v'] > d['v']:
                a[5] += 1
    print(f"  {'thang':9s} {'n_nen':>7s} {'n_lech':>7s} {'%lech':>7s} {'tong V fp':>12s} "
          f"{'tong V dx':>12s} {'fp/dx':>7s} {'max lech':>9s} {'fp>dx':>7s}")
    for m in sorted(agg):
        a = agg[m]
        print(f"  {m:9s} {a[0]:7d} {a[1]:7d} {100*a[1]/a[0]:6.1f}% {a[2]:12.0f} {a[3]:12.0f} "
              f"{a[2]/max(1,a[3]):7.3f} {a[4]:9.0f} {a[5]:7d}")
    tn = sum(a[0] for a in agg.values()); td = sum(a[1] for a in agg.values())
    tfp = sum(a[2] for a in agg.values()); tdx = sum(a[3] for a in agg.values())
    print(f"  {'TONG':9s} {tn:7d} {td:7d} {100*td/tn:6.1f}% {tfp:12.0f} {tdx:12.0f} "
          f"{tfp/tdx:7.3f}")

    print("\n  --- vi du 8 nen lech nhieu nhat ---")
    ds = sorted(((abs(b['v'] - dxm[b['dt']]['v']), b) for b in src if b['dt'] in dxm),
                key=lambda x: -x[0])[:8]
    print(f"  {'dt':>20s} {'V fp':>8s} {'V dx':>8s} {'lech':>8s} {'close (khop)':>13s}")
    for d, b in ds:
        print(f"  {str(b['dt']):>20s} {b['v']:8.0f} {dxm[b['dt']]['v']:8.0f} {d:8.0f} "
              f"{b['c']:13.1f}")

    print("\n" + "=" * 110)
    print("G.6 — anh huong len GATE VSA (vratio) — gate trung tam cua ca KB1 va KB2")
    print("=" * 110)
    Bfp = L.derive([dict(dt=b['dt'], o=x['o'], hi=x['hi'], lo=x['lo'], c=x['c'], v=x['v'])
                    for b, x in zip(src, [dict(o=r['o'], hi=r['hi'], lo=r['lo'], c=r['c'], v=r['v'])
                                          for r in raw_fp])])
    fpm = {b['dt']: b for b in Bfp}
    ins = [b for b in Bdx if b['ym'] in ('2026-05', '2026-06', '2026-07') and b['dt'] in fpm]
    for thr, lbl in [(2.0, "KB1 BVSA>=2.0"), (1.8, "KB2 vsa_conf>=1.8")]:
        both = sum(1 for b in ins if b['vratio'] >= thr and fpm[b['dt']]['vratio'] >= thr)
        only_dx = sum(1 for b in ins if b['vratio'] >= thr and fpm[b['dt']]['vratio'] < thr)
        only_fp = sum(1 for b in ins if b['vratio'] < thr and fpm[b['dt']]['vratio'] >= thr)
        print(f"  {lbl:<20s} (5-7/2026, {len(ins)} nen): ca 2 dat={both:6d}  chi dxFeed={only_dx:5d}  "
              f"chi fp-m1={only_fp:5d}  -> khong nhat quan {100*(only_dx+only_fp)/max(1,both+only_dx+only_fp):.1f}%")
    print("\n  ==> volume la NGUON DUY NHAT cua vratio/volfloor/liqratio. 2 export cua CUNG mot")
    print("      hop dong cho volume KHAC nhau => con so tuyet doi (n, tong R) KHONG tai lap duoc")
    print("      giua 2 nguon; chi HUONG (dau cua EV) la tai lap duoc.")


if __name__ == '__main__':
    main()
