# -*- coding: utf-8 -*-
"""
KỊCH BẢN NGƯỜI HỌC (2026-10-22): vẽ vùng hỗ trợ/kháng cự từ 15 NGÀY trước, rồi chạy NGÀY 16 xem:
  (1) giá chạm vùng thì vùng có được BẢO VỆ (giá bật) không;
  (2) vùng bị PHÁ thì giá có ĐI XA không.
Làm cuốn chiếu: bản đồ từ 15 phiên liền trước → test phiên kế tiếp (phiên 16, 17, ... 21 ⇒ 6 ngày test, ngày đầu là 09-07).
Bản đồ chỉ dùng dữ liệu QUÁ KHỨ (không nhìn trước).

Bản đồ vùng (cách trader kẻ tay, làm bằng máy):
  - Đỉnh/đáy sóng (swing) trên nến M15 (3 nến mỗi bên) và M5 (5 nến mỗi bên) trong 15 phiên.
  - Gộp các đỉnh/đáy cách nhau ≤ 1u thành 1 vùng; biên = min/max ± 0,5u; độ rộng kẹp [1u, 4u].
    u = trung vị biên độ nến M1 của 15 phiên đó.
  - "Số lần va đập" = số đỉnh/đáy gộp vào vùng. Chỉ giữ vùng ≥ 2 lần (đã được tôn trọng ít nhất 2 lần).
Sự kiện trong ngày test: giá ĐÓNG vào vùng từ một phía (nến trước đóng ngoài vùng). Phía tới quyết định vai:
  tới từ trên = HỖ TRỢ, tới từ dưới = KHÁNG CỰ (vai tự đảo khi giá đã ở phía kia — đúng ý "phá rồi đổi vai").
Kết cục (tối đa 120 nến, trong phiên):
  BẢO VỆ = giá đóng cách cạnh gần ≥ 2u về phía cũ trước khi đóng xuyên qua cạnh xa.
  PHÁ    = giá đóng xuyên qua cạnh xa trước. Với ca phá: "đi xa" = trong 60 nến sau khi phá, giá đi ≥ 5 / 10 giá
           vượt cạnh xa TRƯỚC KHI đóng quay lại vào vùng.
ĐỐI CHỨNG: dời NGUYÊN bản đồ đi một khoảng ngẫu nhiên 3–15 giá (lên hoặc xuống), 50 lần, chạy y hệt.
  Nếu vị trí vùng có ý nghĩa thì bản đồ thật phải BẢO VỆ nhiều hơn / phá đi xa hơn bản đồ dời.
Chạy: python3 map15.py → report/MAP15.md
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, '..', '..', 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260816-20260915_29d2h')
LOOK = 15
MAXF = 120
REPS = 50

df = pd.read_csv(BASE + '_bars.csv', parse_dates=['datetime'])
gap = df['datetime'].diff().dt.total_seconds().fillna(0).to_numpy() > 30 * 60
df['s'] = np.cumsum(gap)
H, L, C = df['high'].to_numpy(), df['low'].to_numpy(), df['close'].to_numpy()
S = df['s'].to_numpy()
sess = sorted(set(S))
first_bar = {s: int(np.flatnonzero(S == s)[0]) for s in sess}
last_bar = {s: int(np.flatnonzero(S == s)[-1]) for s in sess}
sess_len = {s: last_bar[s] - first_bar[s] + 1 for s in sess}


def pivots(sub, rule, k):
    """Đỉnh/đáy sóng trên nến gộp theo 'rule' (5min/15min), không gộp xuyên phiên."""
    g = sub.groupby(['s', sub['datetime'].dt.floor(rule)]).agg(h=('high', 'max'), l=('low', 'min')).reset_index()
    out = []
    for _, gg in g.groupby('s'):
        h, l = gg['h'].to_numpy(), gg['l'].to_numpy()
        for i in range(k, len(gg) - k):
            if h[i] == h[i - k:i + k + 1].max() and (h[i - k:i] < h[i]).all(): out.append(h[i])
            if l[i] == l[i - k:i + k + 1].min() and (l[i - k:i] > l[i]).all(): out.append(l[i])
    return out


def build_map(test_s):
    prev = [s for s in sess if s < test_s][-LOOK:]
    sub = df[df['s'].isin(prev)]
    u = float(np.median(sub['high'] - sub['low']))
    ps = np.sort(np.array(pivots(sub, '15min', 3) + pivots(sub, '5min', 5)))
    zones = []
    i = 0
    while i < len(ps):                                   # gộp đơn liên kết ≤ 1u
        j = i
        while j + 1 < len(ps) and ps[j + 1] - ps[j] <= u: j += 1
        grp = ps[i:j + 1]
        lo, hi = grp.min() - 0.5 * u, grp.max() + 0.5 * u
        if hi - lo < u: m = (lo + hi) / 2; lo, hi = m - u / 2, m + u / 2
        if hi - lo > 4 * u: m = np.median(grp); lo, hi = m - 2 * u, m + 2 * u
        zones.append((lo, hi, len(grp)))
        i = j + 1
    zones = [z for z in zones if z[2] >= 2]
    return zones, u


def events(zones, u, a, b, shift=0.0):
    """Mọi lần giá đóng vào vùng từ ngoài trong [a, b]. Trả list dict."""
    out = []
    for lo, hi, cnt in zones:
        lo, hi = lo + shift, hi + shift
        i = a + 1
        while i <= b:
            inside = lo <= C[i] <= hi
            if not inside: i += 1; continue
            if C[i - 1] > hi: side = +1          # tới từ trên ⇒ HỖ TRỢ
            elif C[i - 1] < lo: side = -1        # tới từ dưới ⇒ KHÁNG CỰ
            else: i += 1; continue
            res, k = None, i
            for k in range(i + 1, min(i + MAXF, b + 1)):
                if side > 0:
                    if C[k] < lo: res = 'pha'; break
                    if C[k] >= hi + 2 * u: res = 'bao_ve'; break
                else:
                    if C[k] > hi: res = 'pha'; break
                    if C[k] <= lo - 2 * u: res = 'bao_ve'; break
            ev = dict(cnt=cnt, side=side, res=res, far5=np.nan, far10=np.nan)
            if res == 'pha':
                far = 0.0; back = False
                for m in range(k, min(k + 60, b + 1)):
                    if side > 0:
                        if C[m] >= lo and m > k: back = True; break
                        far = max(far, lo - L[m])
                    else:
                        if C[m] <= hi and m > k: back = True; break
                        far = max(far, H[m] - hi)
                ev['far5'], ev['far10'] = float(far >= 5), float(far >= 10)
            out.append(ev)
            i = k + 1                                # chờ thoát khỏi lần này rồi mới đếm lần sau
    return out


def stats(evs):
    d = pd.DataFrame(evs)
    if d.empty: return dict(n=0)
    done = d[d['res'].notna()]
    br = done[done['res'] == 'pha']
    return dict(n=len(done), bv=(done['res'] == 'bao_ve').mean(), npha=len(br),
                f5=br['far5'].mean() if len(br) else np.nan, f10=br['far10'].mean() if len(br) else np.nan)


rng = np.random.default_rng(5)
test_sess = [s for s in sess if s >= LOOK and sess_len[s] >= 600]
rows = []
for ts in test_sess:
    zones, u = build_map(ts)
    a, b = first_bar[ts], last_bar[ts]
    real = events(zones, u, a, b)
    fake = []
    for _ in range(REPS):
        sh = rng.uniform(3, 15) * rng.choice([-1, 1])
        fake += events(zones, u, a, b, sh)
    rows.append((ts, df['datetime'].iloc[b].date(), len(zones), u, real, fake))


def pct(x): return '—' if x is None or not np.isfinite(x) else f'{100 * x:.0f}%'


def se(p, n): return 100 * np.sqrt(p * (1 - p) / n) if n else np.nan


md = ['# Bản đồ vùng 15 ngày → test ngày 16 (cuốn chiếu 6 ngày)', '',
      'Bản đồ: đỉnh/đáy sóng M15 + M5 của 15 phiên trước, gộp ≤1u, chỉ giữ vùng đã bị va đập ≥2 lần. '
      'Đối chứng: cùng bản đồ dời ngẫu nhiên 3–15 giá, 50 lần. Chi tiết định nghĩa ở docstring `map15.py`.', '',
      '## Từng ngày test', '',
      '| Ngày test | số vùng | u (giá) | lần chạm | BẢO VỆ % (thật / dời) | số lần phá | phá rồi đi ≥5 giá (thật / dời) | đi ≥10 giá (thật / dời) |',
      '|---|---|---|---|---|---|---|---|']
allr, allf = [], []
for ts, day, nz, u, real, fake in rows:
    r, f = stats(real), stats(fake)
    allr += real; allf += fake
    md.append(f"| {day} | {nz} | {u:.2f} | {r['n']} | {pct(r.get('bv'))} / {pct(f.get('bv'))} | {r.get('npha', 0)} | "
              f"{pct(r.get('f5'))} / {pct(f.get('f5'))} | {pct(r.get('f10'))} / {pct(f.get('f10'))} |")
r, f = stats(allr), stats(allf)
md += ['', '## Gộp 6 ngày', '',
       f"- Lần chạm: {r['n']} · **BẢO VỆ {pct(r['bv'])}** (±{se(r['bv'], r['n']):.0f}) · bản đồ dời {pct(f['bv'])}",
       f"- Lần phá: {r['npha']} · **phá rồi đi ≥5 giá {pct(r['f5'])}** (±{se(r['f5'], r['npha']):.0f}) · dời {pct(f['f5'])}",
       f"- Phá rồi đi ≥10 giá {pct(r['f10'])} (±{se(r['f10'], r['npha']):.0f}) · dời {pct(f['f10'])}", '',
       '## Theo số lần đã va đập trong 15 ngày (gộp 6 ngày)', '',
       '| Va đập | lần chạm | BẢO VỆ % (thật / dời) | lần phá | phá rồi đi ≥5 giá (thật / dời) |', '|---|---|---|---|---|']
R, F = pd.DataFrame(allr), pd.DataFrame(allf)
for lab, lo_, hi_ in (('2 lần', 2, 2), ('3–4 lần', 3, 4), ('≥5 lần', 5, 999)):
    a = stats(R[(R['cnt'] >= lo_) & (R['cnt'] <= hi_)].to_dict('records'))
    b = stats(F[(F['cnt'] >= lo_) & (F['cnt'] <= hi_)].to_dict('records'))
    md.append(f"| {lab} | {a['n']} | {pct(a.get('bv'))} (±{se(a.get('bv', 0), a['n']):.0f}) / {pct(b.get('bv'))} | {a.get('npha', 0)} | "
              f"{pct(a.get('f5'))} / {pct(b.get('f5'))} |")
md += ['', '## Theo vai (gộp 6 ngày)', '', '| Vai | lần chạm | BẢO VỆ % (thật / dời) |', '|---|---|---|']
for lab, sd in (('Hỗ trợ (giá tới từ trên)', 1), ('Kháng cự (giá tới từ dưới)', -1)):
    a = stats(R[R['side'] == sd].to_dict('records')); b = stats(F[F['side'] == sd].to_dict('records'))
    md.append(f"| {lab} | {a['n']} | {pct(a.get('bv'))} (±{se(a.get('bv', 0), a['n']):.0f}) / {pct(b.get('bv'))} |")
out = '\n'.join(md) + '\n'
open(os.path.join(HERE, 'report', 'MAP15.md'), 'w', encoding='utf-8').write(out)
print(out)
