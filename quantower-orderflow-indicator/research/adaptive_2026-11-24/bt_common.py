"""Dùng chung cho phần Big Trade: nạp nhật ký lệnh đơn M1, dựng khung lớn hơn, gán phiên.
Nhật ký: %APPDATA%/OrderFlowBubbles/bigtrade-log/*.csv (time_ticks,time_iso,price,mot,buy,sell); mỗi dòng = (nến, mức giá) có lệnh đơn > 0.
Phiên (giờ UTC, cố định): Á 22:00-07:00, Âu 07:00-13:30, Mỹ 13:30-22:00.
(Mỹ đổi giờ 01/11/2026: từ đó giờ mở cửa cổ phiếu Mỹ là 14:30 UTC; ranh giới ở đây giữ cố định cho đơn giản.)"""
import os, numpy as np, pandas as pd
LOG = os.path.join(os.environ.get('APPDATA', ''), 'OrderFlowBubbles', 'bigtrade-log')
TICK = {'NQ': 0.25, 'GC': 0.1}
# nguồn M1 dùng để đo: (file, từ, đến, ghi chú)
SRC = {
    'NQ': ('_NQZ26_XCME_Time_1Minute.csv', '2026-10-25 22:00', '2026-11-03 00:00'),   # chạy lại (replay) liền mạch 6 phiên
    'GC': ('_GC_XCEC_Time_1Minute.csv', '2026-08-31 22:00', '2026-09-23 15:29'),      # liền mạch 16 phiên, cùng hợp đồng GCZ26 (không vắt chỗ nối)
    'GClive': ('_GCZ26_XCEC_Time_1Minute.csv', '2026-11-09', '2026-11-25'),           # sống, đứt quãng
    'NQlive': ('_NQZ26_XCME_Time_1Minute.csv', '2026-11-24', '2026-11-25'),           # sống 24/11, 204 nến
}
SES = ['A', 'Au', 'My']
SES_VN = {'A': 'Á', 'Au': 'Âu', 'My': 'Mỹ'}
def ses_of(ts):
    """ts: DatetimeIndex/Series UTC -> mảng 'A' / 'Au' / 'My'."""
    h = np.asarray(ts.hour + ts.minute / 60.0)
    return np.where((h >= 13.5) & (h < 22), 'My', np.where((h >= 7) & (h < 13.5), 'Au', 'A'))
def load_m1(key):
    f, a, b = SRC[key]
    d = pd.read_csv(os.path.join(LOG, f))
    d['t'] = pd.to_datetime(d.time_iso, utc=True).dt.tz_localize(None)
    d = d[(d.t >= a) & (d.t < b)].drop_duplicates(['t', 'price'])
    d['tk'] = np.round(d.price / TICK[key[:2]]).astype(np.int64)
    return d[['t', 'tk', 'mot', 'buy', 'sell']].sort_values(['t', 'tk']).reset_index(drop=True)
def to_tf(d, mins):
    """Dựng khung M phút từ M1: lệnh đơn lớn nhất theo (nến khung lớn, mức giá) = max; buy/sell = tổng."""
    if mins == 1: return d.copy()
    x = d.copy(); x['t'] = x.t.dt.floor(f'{mins}min')
    return x.groupby(['t', 'tk'], sort=True).agg(mot=('mot', 'max'), buy=('buy', 'sum'), sell=('sell', 'sum')).reset_index()
def bars_of(c):
    """Danh sách nến (có ít nhất một ô có lệnh đơn) theo thứ tự thời gian + phiên."""
    b = c.groupby('t').agg(ncell=('tk', 'size'), lo=('tk', 'min'), hi=('tk', 'max'), mmax=('mot', 'max'), vol=('buy', 'sum'), vol2=('sell', 'sum')).reset_index()
    b['vol'] = b.vol + b.vol2; b['rng'] = b.hi - b.lo; b['ses'] = ses_of(pd.DatetimeIndex(b.t))
    return b.drop(columns='vol2')
