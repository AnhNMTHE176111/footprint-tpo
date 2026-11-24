"""Câu A, phần phụ: (a) so N = 10 / 20 / 40; (b) luật thay thế "bội số của trung vị lệnh đơn lớn nhất mỗi nến";
(c) nến đầu phiên Mỹ (13:30 UTC) và nến mở lại 22:00 UTC; (d) kiểm ngoài mẫu trên nhật ký SỐNG (GClive, NQlive).
Chạy: python bt_alt.py"""
import numpy as np, pandas as pd
from bt_common import *
from bt_rule import simulate, merge_cap, MIN_BARS
from bt_measure import dens, TFS
from bt_grid import row

BEST = dict(N=20, density=0.75, floor=5, cap=3, div=8, gmin=2)
pd.set_option('display.width', 250)


def alt_median_max(c, b, N=20, mult=2.0, floor=5):
    """Ngưỡng = max(sàn, mult x trung vị của (lệnh đơn lớn nhất mỗi nến) trên N nến trước). Không gộp, không giới hạn."""
    thr = (b.mmax.shift(1).rolling(N, min_periods=MIN_BARS).median() * mult).clip(lower=floor).fillna(10)
    thr_s = pd.Series(thr.values, index=b.t.values)
    x = c.copy(); x['thr'] = x.t.map(thr_s).values
    return x[x.mot >= x.thr], thr_s


if __name__ == '__main__':
    for key in ('NQ', 'GC'):
        d = load_m1(key); rows = []
        for m in TFS:
            c = to_tf(d, m); b = bars_of(c)
            for N in (10, 20, 40):
                kw = dict(BEST, N=N); h, thr = simulate(c, b, **kw); rows.append(row(f'hạng K, N={N} d0.75 sàn5 gộp R/8 tối đa 3', h, thr, b, m))
            for mult in (1.5, 2.0, 3.0):
                h, thr = alt_median_max(c, b, mult=mult); rows.append(row(f'{mult} x trung vị (max mỗi nến), N=20, không gộp', h, thr, b, m))
        print(f'\n######## (a)(b) {key}'); print(pd.DataFrame(rows).to_string(index=False))

    print('\n######## (c) số vòng ở 3 nến đầu sau 13:30 UTC (mở cửa cổ phiếu Mỹ, 26-30/10) và sau 22:00 UTC (mở lại), TB mỗi nến')
    rows = []
    for key in ('NQ', 'GC'):
        d = load_m1(key)
        for m in (1, 5, 15, 30):
            c = to_tf(d, m); b = bars_of(c)
            for name, kw in (('cố định 10', None), ('thích nghi, không gộp/giới hạn', dict(BEST, cap=0, div=0, gmin=0)), ('thích nghi (mặc định)', BEST)):
                if kw is None: h = c[c.mot >= 10]
                else: h, _ = simulate(c, b, **kw)
                per = h.groupby('t').size().reindex(b.t.values, fill_value=0)
                per.index = pd.DatetimeIndex(per.index)
                mins = per.index.hour * 60 + per.index.minute
                r = dict(ma=key, khung=f'M{m}', luat=name)
                for lab, start in (('My_1330', 13 * 60 + 30), ('molai_2200', 22 * 60)):
                    for j in range(3):
                        r[f'{lab}_nen{j+1}'] = round(per[mins == start + j * m].mean(), 2)
                r['tat_ca'] = round(per.mean(), 2)
                rows.append(r)
    print(pd.DataFrame(rows).to_string(index=False))

    print('\n######## (d) nhật ký SỐNG (đứt quãng): hàng đợi = N nến có số liệu liền trước trong file (kể cả qua khoảng hở)')
    rows = []
    for key in ('GClive', 'NQlive'):
        d = load_m1(key)
        for m in (1, 5, 15):
            c = to_tf(d, m)
            if m > 1:   # chỉ giữ nến khung lớn đủ M nến M1
                n1 = d.groupby(d.t.dt.floor(f'{m}min')).t.nunique(); c = c[c.t.isin(n1[n1 == m].index)]
            b = bars_of(c)
            if len(b) < 30: continue
            rows.append(dict(ma=key, nen=len(b), **row('CỐ ĐỊNH 10', c[c.mot >= 10], pd.Series(10.0, index=b.t.values), b, m)))
            h, thr = simulate(c, b, **BEST); rows.append(dict(ma=key, nen=len(b), **row('thích nghi (mặc định)', h, thr, b, m)))
    print(pd.DataFrame(rows).to_string(index=False))
