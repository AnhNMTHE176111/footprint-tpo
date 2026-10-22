# -*- coding: utf-8 -*-
"""
GIÁ RỜI VÙNG 10-20 GIÁ RỒI CÓ QUAY LẠI CHẠM KHÔNG? (câu hỏi người học 2026-10-22)

Sự kiện: vùng Vùng Canh Lệnh (v4, biên đóng băng lúc vùng lần đầu hiện trên chart) bị giá CHẠM (râu chạm biên),
sau đó giá ĐÓNG cách cạnh gần của vùng >= X giá (X = 10, 15, 20) ⇒ "đã rời". Đo:
  - % quay lại chạm vùng trong 60 / 240 / 1380 nến (1380 ≈ 1 ngày giao dịch) kể từ lúc rời;
  - khi quay lại: % BẬT (Chung&Bellotti: vào dải bằng giá đóng rồi thoát cùng phía, tối đa 120 nến).
ĐỐI CHỨNG: mức giá bất kỳ mà giá từng đi qua (bốc ngẫu nhiên 1 nến + 1 giá trong biên nến đó, cùng độ rộng trung vị vùng thật),
áp y hệt quy trình chạm → rời ≥ X → quay lại. Câu hỏi đối chứng trả lời: vùng có "kéo giá quay lại" hơn một mức giá bất kỳ không.
Chạy: python3 quay_lai.py → report/QUAY-LAI.md
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
BASE = os.path.join(ROOT, 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260816-20260915_29d2h')
N_TRAIN_SESS = 14
XS = (10.0, 15.0, 20.0)
HS = (60, 240, 1380)
CHUNG_MAX = 120
N_CTRL = 20000

df = pd.read_csv(BASE + '_bars.csv', parse_dates=['datetime'])
H, L, C = df['high'].to_numpy(), df['low'].to_numpy(), df['close'].to_numpy()
n = len(df)
gap = df['datetime'].diff().dt.total_seconds().fillna(0).to_numpy() > 30 * 60
sno = np.cumsum(gap)
split = np.where(sno < N_TRAIN_SESS, 'TRAIN', 'TEST')
u = pd.Series(H - L).rolling(50, min_periods=10).median().to_numpy()

rec = pd.read_csv(os.path.join(HERE, 'report', 'vcl4_records.csv.gz'))
first = rec.sort_values('bar').groupby('eid', as_index=False).first()      # biên lúc vùng lần đầu hiện
# bỏ trùng: cùng mức (làm tròn 0,5 giá) xuất hiện lại nhiều lần với mã mới ⇒ giữ lần đầu
first['key'] = ((first['lo'] + first['hi']) / 2 / 0.5).round().astype(int)
first = first.sort_values('bar').drop_duplicates('key', keep='first')


def follow(lo, hi, b0, X):
    """Từ nến b0: chạm đầu → rời ≥ X (giá đóng) → quay lại chạm. Trả dict hoặc None nếu không có chạm/rời."""
    seg = np.flatnonzero((H[b0:] >= lo) & (L[b0:] <= hi))
    if not len(seg): return None
    t1 = b0 + seg[0]
    away = np.flatnonzero((C[t1 + 1:] > hi + X) | (C[t1 + 1:] < lo - X))
    if not len(away): return None
    t2 = t1 + 1 + away[0]
    up = C[t2] > hi                                   # rời lên trên ⇒ khi quay lại vùng làm HỖ TRỢ
    back = np.flatnonzero((H[t2 + 1:] >= lo) & (L[t2 + 1:] <= hi))
    t3 = t2 + 1 + back[0] if len(back) else None
    room = n - 1 - t2
    out = dict(t2=t2, split=split[t2], up=up, room=room, wait=(t3 - t2) if t3 is not None else np.inf, bounce=np.nan)
    if t3 is not None and np.isfinite(u[t3]):
        # bật khi quay lại: giá ĐÓNG cách cạnh gần ≥ 2u về phía cũ TRƯỚC KHI đóng xuyên qua cạnh xa; tối đa 120 nến
        g2 = 2 * u[t3]
        for k in range(t3, min(t3 + CHUNG_MAX, n)):
            if up:
                if C[k] < lo: out['bounce'] = 0; break
                if C[k] > hi + g2: out['bounce'] = 1; break
            else:
                if C[k] > hi: out['bounce'] = 0; break
                if C[k] < lo - g2: out['bounce'] = 1; break
    return out


def run(levels, X):
    rows = []
    for lo, hi, b0 in levels:
        r = follow(lo, hi, int(b0), X)
        if r is not None: rows.append(r)
    return pd.DataFrame(rows)


real = list(zip(first['lo'], first['hi'], first['bar']))
w = float(np.median(first['hi'] - first['lo']))
rng = np.random.default_rng(11)
bb = rng.integers(60, n - 60, N_CTRL)
pp = L[bb] + rng.random(N_CTRL) * (H[bb] - L[bb])
ctrl = [(p - w / 2, p + w / 2, b) for p, b in zip(pp, bb)]


def pct(x): return f"{100 * x:.0f}%" if np.isfinite(x) else '—'


def summarize(d, h):
    ok = d[d['room'] >= h]                            # chỉ tính ca còn đủ h nến dữ liệu phía sau
    return (ok['wait'] <= h).mean() if len(ok) else np.nan, len(ok)


md = ['# Giá rời vùng 10-20 giá rồi có quay lại chạm không?', '',
      f'Dữ liệu `{os.path.basename(BASE)}` ({n} nến M1). Vùng = vùng Vùng Canh Lệnh v4 (biên lúc vùng lần đầu hiện, bỏ trùng mức): '
      f'{len(real)} vùng. Đối chứng: {N_CTRL} mức giá bất kỳ giá từng đi qua, rộng {w:.1f} giá (trung vị vùng thật).',
      'Chỉ tính ca còn đủ dữ liệu phía sau cho mỗi cửa sổ. 1380 nến ≈ 1 ngày giao dịch.', '',
      '| Rời ≥ | Tách | n vùng | quay lại ≤60 nến (vùng / đối chứng) | ≤240 nến | ≤1380 nến | bật khi quay lại (vùng / đối chứng) |',
      '|---|---|---|---|---|---|---|']
for X in XS:
    R, G = run(real, X), run(ctrl, X)
    for sp in ('TRAIN', 'TEST', 'GỘP'):
        r = R if sp == 'GỘP' else R[R['split'] == sp]
        g = G if sp == 'GỘP' else G[G['split'] == sp]
        cells = []
        for h in HS:
            a, na = summarize(r, h); b, _ = summarize(g, h)
            cells.append(f"{pct(a)} / {pct(b)} (n={na})")
        rb, gb = r['bounce'].dropna(), g['bounce'].dropna()
        cells.append(f"{pct(rb.mean())} / {pct(gb.mean())} (n={len(rb)})")
        md.append(f"| {X:.0f} giá | {sp} | {len(r)} | " + ' | '.join(cells) + ' |')
out = '\n'.join(md) + '\n'
open(os.path.join(HERE, 'report', 'QUAY-LAI.md'), 'w', encoding='utf-8').write(out)
print(out)
