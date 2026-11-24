"""Câu A: quét luật Big Trade thích nghi (hạng K trong N nến trước) theo mã x khung x phiên.
Chạy: python bt_grid.py [NQ GC ...]   (in bảng: vòng/nến Á/Âu/Mỹ, ngưỡng trung vị Á/Âu/Mỹ, tỉ lệ nến có vòng, phân vị 95 và lớn nhất số vòng trong 1 nến)"""
import sys, numpy as np, pandas as pd
from bt_common import *
from bt_rule import simulate
from bt_measure import dens, TFS


def row(name, hits, thr, b, m):
    r = dens(hits, b, m)
    tm = {s: np.median(thr.values[b.ses.values == s]) for s in SES}
    return dict(khung=f'M{m}', luat=name, A=round(r['A'], 2), Au=round(r['Au'], 2), My=round(r['My'], 2), tat_ca=round(r['all'], 2),
                gio=f"{r['A_h']:.1f}/{r['Au_h']:.1f}/{r['My_h']:.1f}", nguong=f"{tm['A']:.0f}/{tm['Au']:.0f}/{tm['My']:.0f}",
                nen_co_vong=f"{r['A_p']:.2f}/{r['Au_p']:.2f}/{r['My_p']:.2f}", p95=int(r['all_p95']), mx=int(r['all_mx']))


VARIANTS = [
    # tên, tham số simulate
    ('N20 d0.5 sàn5 (không gộp, không giới hạn)', dict(N=20, density=0.5, floor=5, cap=0, div=0, gmin=0)),
    ('N20 d1.0 sàn5 (không gộp)', dict(N=20, density=1.0, floor=5, cap=0, div=0, gmin=0)),
    ('N20 d0.3 sàn5 (không gộp)', dict(N=20, density=0.3, floor=5, cap=0, div=0, gmin=0)),
    ('N50 d0.5 sàn5 (không gộp)', dict(N=50, density=0.5, floor=5, cap=0, div=0, gmin=0)),
    ('N20 d0.5 sàn3 (không gộp)', dict(N=20, density=0.5, floor=3, cap=0, div=0, gmin=0)),
    ('N20 d0.5 sàn10 (không gộp)', dict(N=20, density=0.5, floor=10, cap=0, div=0, gmin=0)),
    ('N20 d0.5 sàn5 gộp R/8 tối đa 3', dict(N=20, density=0.5, floor=5, cap=3, div=8, gmin=2)),
    ('N20 d1.0 sàn5 gộp R/8 tối đa 3', dict(N=20, density=1.0, floor=5, cap=3, div=8, gmin=2)),
    ('N20 d0.75 sàn5 gộp R/8 tối đa 3', dict(N=20, density=0.75, floor=5, cap=3, div=8, gmin=2)),
]

if __name__ == '__main__':
    keys = [a for a in sys.argv[1:] if not a.startswith('-')] or ['NQ', 'GC']
    for key in keys:
        d = load_m1(key)
        print(f'\n################ {key}: {d.t.nunique()} nến M1')
        rows = []
        for m in TFS:
            c = to_tf(d, m); b = bars_of(c)
            if len(b) < 60: continue
            fixed = c[c.mot >= 10]
            rows.append(row('CỐ ĐỊNH 10 (hiện tại)', fixed, pd.Series(10.0, index=b.t.values), b, m))
            for name, kw in VARIANTS:
                hits, thr = simulate(c, b, **kw)
                rows.append(row(name, hits, thr, b, m))
        pd.set_option('display.width', 250)
        print(pd.DataFrame(rows).to_string(index=False))
