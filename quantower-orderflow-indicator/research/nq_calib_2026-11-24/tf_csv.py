"""Gộp footprint NQ M1 lên khung M (phút) thành cặp CSV cùng định dạng data-export (để chạy perf/Golden stophunt so C# với Python).
python tf_csv.py <phút> <thư mục ra>"""
import sys, os, pandas as pd, numpy as np
m, out = int(sys.argv[1]), sys.argv[2]
D = '../../../data-export/data-footprint/fp_NQZ26_XCME_Time_20260826-20261124_90d'
L = pd.read_csv(D + '.csv'); B = pd.read_csv(D + '_bars.csv')
L['dt'] = pd.to_datetime(L.datetime); B['dt'] = pd.to_datetime(B.datetime)
L = L[L.dt >= '2026-09-14']; B = B[B.dt >= '2026-09-14']
L['t'] = L.dt.dt.floor(f'{m}min'); B['t'] = B.dt.dt.floor(f'{m}min')
g = B.sort_values('dt').groupby('t')
bars = pd.DataFrame({'open': g.open.first(), 'high': g.high.max(), 'low': g.low.min(), 'close': g.close.last(), 'bar_volume': g.bar_volume.sum(),
                     'bar_ticks': g.bar_ticks.sum(), 'bid_vol': g.bid_vol.sum(), 'ask_vol': g.ask_vol.sum(), 'volume': g.volume.sum(), 'delta': g.delta.sum(),
                     'delta_finish': g.delta.sum(), 'max_delta': 0, 'min_delta': 0, 'cum_delta': 0, 'trades': g.trades.sum(), 'buy_trades': g.buy_trades.sum(),
                     'sell_trades': g.sell_trades.sum(), 'max_one_trade': g.max_one_trade.max(), 'avg_size': 0, 'avg_buy_size': 0, 'avg_sell_size': 0,
                     'levels': 0, 'poc_price': 0, 'poc_volume': 0, 'open_interest': 0}).reset_index()
bars.insert(0, 'bar_idx', range(len(bars))); idx = dict(zip(bars.t, bars.bar_idx))
bars.insert(1, 'datetime', bars.pop('t').dt.strftime('%Y-%m-%d %H:%M:%S'))
lv = L.groupby(['t', 'price']).agg(bid_vol=('bid_vol', 'sum'), ask_vol=('ask_vol', 'sum'), volume=('volume', 'sum'), delta=('delta', 'sum'), trades=('trades', 'sum'),
                                    buy_trades=('buy_trades', 'sum'), sell_trades=('sell_trades', 'sum'), max_one_trade=('max_one_trade', 'max')).reset_index()
lv.insert(0, 'bar_idx', lv.t.map(idx)); lv.insert(1, 'datetime', lv.pop('t').dt.strftime('%Y-%m-%d %H:%M:%S'))
lv['price'] = lv.price.map(lambda p: f'{p:.2f}')
os.makedirs(out, exist_ok=True); f = os.path.join(out, f'fp_NQ_m{m}')
lv.to_csv(f + '.csv', index=False); bars.to_csv(f + '_bars.csv', index=False)
print(f, len(bars), 'nến', len(lv), 'dòng')
