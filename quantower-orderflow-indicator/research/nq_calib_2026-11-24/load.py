"""Nạp footprint M1 -> gộp theo từng tick lên khung M (phút). Lưu pickle để các script khác dùng."""
import sys, pandas as pd, numpy as np
DATA = '../../../data-export/data-footprint/'
SYM = {
    'GC': dict(f='fp_GCZ26_XCEC_Time_20260811-20261109_90d', tick=0.1, since='2026-08-11'),
    'NQ': dict(f='fp_NQZ26_XCME_Time_20260826-20261124_90d', tick=0.25, since='2026-09-14'),  # NQZ26 thành hợp đồng chính từ ~14/09
}
def build(sym, mins):
    c = SYM[sym]
    d = pd.read_csv(DATA + c['f'] + '.csv', usecols=['datetime', 'price', 'bid_vol', 'ask_vol', 'volume'])
    d['dt'] = pd.to_datetime(d.datetime)
    d = d[d.dt >= c['since']]
    d['t'] = d.dt.dt.floor(f'{mins}min')
    d['tk'] = np.round(d.price / c['tick']).astype(np.int64)
    F = d.groupby(['t', 'tk'], sort=True).agg(bid=('bid_vol', 'sum'), ask=('ask_vol', 'sum'), vol=('volume', 'sum')).reset_index()
    F = F[F.vol > 0]
    st = F.groupby('t').agg(med=('vol', 'median'), mean=('vol', 'mean'), hi=('tk', 'max'), lo=('tk', 'min'), nl=('tk', 'size'), tot=('vol', 'sum'))
    st['B_med'] = st.med.shift(1).rolling(20, min_periods=5).mean()
    st['B_mean'] = st['mean'].shift(1).rolling(20, min_periods=5).mean()
    st['rng'] = st.hi - st.lo
    F = F.merge(st[['B_med']], left_on='t', right_index=True)
    F.to_pickle(f'F_{sym}_m{mins}.pkl'); st.to_pickle(f'S_{sym}_m{mins}.pkl')
    print(sym, mins, len(st), 'nến')
if __name__ == '__main__':
    for s in ('GC', 'NQ'):
        for m in (1, 5): build(s, m)
