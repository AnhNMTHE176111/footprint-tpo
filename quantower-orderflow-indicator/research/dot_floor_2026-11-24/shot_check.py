"""Câu 2: đoạn chart người học chụp — NQ M1 ngày 24/11, 18:15-19:12 giờ chart (UTC+7) = 11:15-12:12 UTC.
Nguồn: fp_NQZ26_XCME_Time_20261115-20261124_8d13h_2.csv (đến 12:17 UTC; file 90 ngày chỉ đến 12:07).
Đếm chấm theo sàn x bộ số x "nổ ở mọi mức giá"; tìm chấm đỏ "6 Bid (Ask 1), ngưỡng 5,5". Chạy: python shot_check.py"""
from floor_lib import *
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
DATA = os.path.join(HERE, '..', '..', '..', 'data-export', 'data-footprint')
A, Bz = '2026-11-24 11:15', '2026-11-24 12:12'
for fn in ('fp_NQZ26_XCME_Time_20260826-20261124_90d.csv', 'fp_NQZ26_XCME_Time_20261115-20261124_8d13h_2.csv'):
    d = pd.read_csv(os.path.join(DATA, fn), usecols=['datetime', 'price', 'bid_vol', 'ask_vol', 'volume']); d['t'] = pd.to_datetime(d.datetime)
    x = d[(d.t >= A) & (d.t <= Bz)]
    print(f'{fn}: nến cuối {d.t.max()}, trong cửa sổ {A} -> {Bz} UTC có {x.t.nunique()} / 58 nến M1')
d = d[d.t >= '2026-11-23 22:00']; d['tk'] = np.round(d.price / 0.25).astype(np.int64)
F = d.groupby(['t', 'tk'], sort=True).agg(bid=('bid_vol', 'sum'), ask=('ask_vol', 'sum'), vol=('volume', 'sum')).reset_index(); F = F[F.vol > 0]
S = F.groupby('t').agg(med=('vol', 'median'), hi=('tk', 'max'), lo=('tk', 'min')); S['rng'] = S.hi - S.lo
B, R, w = base(S, 1); win = (S.index >= A) & (S.index <= Bz); nb = int(win.sum())
print(f'cửa sổ: {nb} nến; B trung vị {B[win].median():.2f} (nhỏ nhất {B[win].min():.2f}, lớn nhất {B[win].max():.2f}); 2,0 x B trung vị {2 * B[win].median():.1f}; biên độ TB {R[win].median():.0f} tick; w trung vị {w[win].median():.0f}')
print(f'tỉ lệ nến có 2,0 x B < 9: {(2 * B[win] < 9).mean() * 100:.0f}%; < 7: {(2 * B[win] < 7).mean() * 100:.0f}%; 2,8 x B < 9: {(2.8 * B[win] < 9).mean() * 100:.0f}%')
rows = []; keep = {}
for pn in PRESETS:
    for al in (False, True):
        D, thr = cands(F, S, 1, pn, al); D = D[(D.t >= A) & (D.t <= Bz)]; keep[(pn, al)] = D
        r = dict(bo=pn, moi_muc_gia='BẬT' if al else 'tắt')
        for f in FLOORS: X = apply_floor(D, f); r[f'san{f}'] = f'{len(X)} ({len(X) / nb:.2f})'
        rows.append(r)
print('\nSố chấm trong cửa sổ (trong ngoặc: chấm/nến):'); print(pd.DataFrame(rows).to_string(index=False))
# chấm như ảnh: đỏ, Bid 6, Ask 1, ngưỡng 5,5 (bộ Không sót, sàn 5 do bộ số ghi đè, nổ mọi mức giá)
D = apply_floor(keep[('Không sót', True)], 5).merge(F[['t', 'tk', 'bid', 'ask']], on=['t', 'tk'])
D['nguong'] = np.maximum(D.kB, 5).round(2); D['gia'] = D.tk * 0.25; D['gio_chart'] = D.t + pd.Timedelta(hours=7)
m = D[(D.col == 'S') & (D.bid == 6) & (D.ask == 1)]
print(f'\nChấm đỏ có Bid 6, Ask 1 (bộ Không sót, sàn 5, nổ mọi mức giá): {len(m)}'); print(m[['t', 'gio_chart', 'gia', 'bid', 'ask', 'nguong']].to_string(index=False))
sm = D[D.v < 9]
print(f'\nBộ Không sót + nổ mọi mức giá + sàn 5: {len(D)} chấm, trong đó {len(sm)} chấm ({100 * len(sm) / len(D):.0f}%) có volume < 9, {int((D.v < 7).sum())} chấm ({100 * (D.v < 7).mean():.0f}%) < 7; phân bố volume chấm: ' + str(D.v.value_counts().sort_index().head(12).to_dict()))
