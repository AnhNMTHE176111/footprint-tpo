"""Ghi nhật ký lệnh đơn đã dựng khung (to_tf) thành file cùng định dạng bigtrade-log để chạy C# (perf/Golden stophunt --btlog --zeromot) so với bt_golden_*.csv.
python bt_cs_log.py <thư mục ra> <thư mục CSV footprint từ ../nq_calib_2026-11-24/tf_csv.py>"""
import sys, os, numpy as np, pandas as pd
from bt_common import load_m1, to_tf, TICK
out, fpdir = sys.argv[1], sys.argv[2]
UNIX_TICKS = 621355968000000000   # .NET ticks của 1970-01-01
for key, m in (('NQ', 1), ('NQ', 15), ('GC', 5), ('GC', 30)):
    c = to_tf(load_m1(key), m)
    t = pd.to_datetime(c.t)
    ticks = t.astype('datetime64[ns]').astype(np.int64) // 100 + UNIX_TICKS
    df = pd.DataFrame({'time_ticks': ticks, 'time_iso': t.dt.strftime('%Y-%m-%dT%H:%M:%S.0000000Z'),
                       'price': (c.tk * TICK[key]).round(4), 'mot': c.mot, 'buy': c.buy, 'sell': c.sell})
    f = os.path.join(out, f'btlog_{key}_M{m}.csv'); df.to_csv(f, index=False)
    fb = pd.read_csv(os.path.join(fpdir, f'fp_{key}_m{m}_bars.csv'), usecols=['datetime'])
    have = set(pd.to_datetime(fb.datetime)); bt = set(t.unique())
    print(f, len(df), 'dòng', len(bt), 'nến; nến nhật ký KHÔNG có trong footprint:', len(bt - have))
