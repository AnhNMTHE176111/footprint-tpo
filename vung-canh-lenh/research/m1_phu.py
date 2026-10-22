# -*- coding: utf-8 -*-
"""
ĐỈNH/ĐÁY M1 LÀM MỐC PHỤ (người học hỏi 2026-10-22): vùng v4 (B, B15, C, D — KHÔNG có M1) mà có thêm 1 đỉnh/đáy M1 nằm
bên trong biên vùng thì có được BẢO VỆ nhiều hơn vùng không có M1 không?
  - Đỉnh/đáy M1: cao/thấp nhất 5 nến mỗi bên, xác nhận sau 5 nến (không nhìn trước), sống 2 phiên (2760 nến).
  - Cờ "có M1" của vùng đóng băng tại nến vùng lần đầu hiện. M1 không tham gia tạo vùng ⇒ độ rộng vùng không phụ thuộc cờ.
  - Sự kiện: giá ĐÓNG vào vùng từ ngoài (biên đóng băng), trong phiên của lúc vùng hiện + tối đa 1380 nến.
    BẢO VỆ = giá đóng cách cạnh gần ≥ 2u về phía cũ trước khi đóng xuyên qua cạnh xa (tối đa 120 nến); PHÁ = ngược lại.
  - ĐỐI CHỨNG: dời toàn bộ đỉnh/đáy M1 một khoảng ngẫu nhiên 3–8 giá (lên/xuống), 100 lần, gắn cờ y hệt.
    Nếu M1 thật có ích thì (bảo vệ có cờ − bảo vệ không cờ) của M1 thật phải LỚN HƠN của M1 dời.
Chạy: python3 m1_phu.py → report/M1-PHU.md
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, '..', '..', 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260816-20260915_29d2h')
K_SW, LIFE, MAXF, REPS = 5, 2760, 120, 100
N_TRAIN = 14

df = pd.read_csv(BASE + '_bars.csv', parse_dates=['datetime'])
H, L, C = df['high'].to_numpy(), df['low'].to_numpy(), df['close'].to_numpy()
n = len(df)
gap = df['datetime'].diff().dt.total_seconds().fillna(0).to_numpy() > 30 * 60
S = np.cumsum(gap)
u_all = pd.Series(H - L).rolling(50, min_periods=10).median().to_numpy()

# đỉnh/đáy M1 (giá, nến xác nhận)
sw_p, sw_b = [], []
for j in range(K_SW, n - K_SW):
    if H[j] == H[j - K_SW:j + K_SW + 1].max() and (H[j - K_SW:j] < H[j]).all(): sw_p.append(H[j]); sw_b.append(j + K_SW)
    if L[j] == L[j - K_SW:j + K_SW + 1].min() and (L[j - K_SW:j] > L[j]).all(): sw_p.append(L[j]); sw_b.append(j + K_SW)
sw_p, sw_b = np.array(sw_p), np.array(sw_b)

rec = pd.read_csv(os.path.join(HERE, 'report', 'vcl4_records.csv.gz'))
fz = rec.sort_values('bar').groupby('eid', as_index=False).first()
fz['key'] = ((fz['lo'] + fz['hi']) / 2 / 0.5).round().astype(int)
fz = fz.sort_values('bar').drop_duplicates('key', keep='first').reset_index(drop=True)


def zone_events(lo, hi, b0, u):
    out = []
    end = min(int(np.flatnonzero(S == S[b0])[-1]), b0 + 1380)
    i = b0 + 1
    while i <= end:
        if lo <= C[i] <= hi:
            if C[i - 1] > hi: side = 1
            elif C[i - 1] < lo: side = -1
            else: i += 1; continue
            res, k = None, i
            for k in range(i + 1, min(i + MAXF, end + 1)):
                if side > 0:
                    if C[k] < lo: res = 0; break
                    if C[k] >= hi + 2 * u: res = 1; break
                else:
                    if C[k] > hi: res = 0; break
                    if C[k] <= lo - 2 * u: res = 1; break
            if res is not None: out.append(res)
            i = k + 1
        else:
            i += 1
    return out


# sự kiện mỗi vùng (tính 1 lần), kèm tách TRAIN/TEST theo phiên lúc vùng hiện
ev, zsplit = [], []
for r in fz.itertuples():
    u = u_all[r.bar]
    ev.append(zone_events(r.lo, r.hi, int(r.bar), u) if u == u else [])
    zsplit.append('TRAIN' if S[r.bar] < N_TRAIN else 'TEST')
zsplit = np.array(zsplit)


def flags(prices):
    f = np.zeros(len(fz), bool)
    for z, r in enumerate(fz.itertuples()):
        m = (sw_b <= r.bar) & (r.bar - sw_b < LIFE) & (prices >= r.lo) & (prices <= r.hi)
        f[z] = m.any()
    return f


def rate(mask):
    e = [x for z in np.flatnonzero(mask) for x in ev[z]]
    return (np.mean(e) if e else np.nan), len(e)


def diff_of(f, sel):
    a, na = rate(f & sel); b, nb = rate(~f & sel)
    return a, na, b, nb, a - b


rng = np.random.default_rng(3)
real_f = flags(sw_p)
fake_f = [flags(sw_p + rng.uniform(3, 8) * rng.choice([-1, 1], len(sw_p))) for _ in range(REPS)]


def pct(x): return '—' if not np.isfinite(x) else f'{100 * x:.0f}%'


md = ['# Đỉnh/đáy M1 làm mốc phụ — có làm vùng được bảo vệ nhiều hơn không?', '',
      f'Dữ liệu `{os.path.basename(BASE)}`. {len(fz)} vùng v4 (B, B15, C, D). Cờ "có M1" = có ≥1 đỉnh/đáy M1 (k={K_SW}, sống 2 phiên) trong biên vùng lúc vùng hiện. '
      f'Có M1: **{real_f.sum()}** vùng ({100 * real_f.mean():.0f}%). BẢO VỆ = giá đóng quay ≥2u về phía cũ trước khi xuyên qua cạnh xa. '
      f'Đối chứng: dời toàn bộ đỉnh/đáy M1 ngẫu nhiên 3–8 giá, {REPS} lần.', '',
      '| Tách | vùng CÓ M1: bảo vệ % (n lần chạm) | vùng KHÔNG M1: bảo vệ % (n) | hiệu (thật) | hiệu với M1 dời: trung bình [5%–95%] | thật vượt đối chứng? |',
      '|---|---|---|---|---|---|']
for sp in ('TRAIN', 'TEST', 'GỘP'):
    sel = np.ones(len(fz), bool) if sp == 'GỘP' else (zsplit == sp)
    a, na, b, nb, d = diff_of(real_f, sel)
    ds = np.array([diff_of(f, sel)[4] for f in fake_f])
    ds = ds[np.isfinite(ds)]
    lo5, hi5 = np.percentile(ds, [5, 95])
    verdict = 'CÓ (>95%)' if d > hi5 else ('thấp hơn' if d < lo5 else 'không (≈ M1 dời)')
    md.append(f"| {sp} | {pct(a)} ({na}) | {pct(b)} ({nb}) | {100 * d:+.1f} điểm | {100 * ds.mean():+.1f} [{100 * lo5:+.1f}; {100 * hi5:+.1f}] | {verdict} |")
out = '\n'.join(md) + '\n'
open(os.path.join(HERE, 'report', 'M1-PHU.md'), 'w', encoding='utf-8').write(out)
print(out)
