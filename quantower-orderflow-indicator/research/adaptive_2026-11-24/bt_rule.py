"""Luật Big Trade thích nghi (bản Python làm CHUẨN cho C#) + mô phỏng nhanh trên nhật ký.

Luật "hạng K trong N nến trước":
  - Mỗi nến ĐÃ ĐÓNG có số liệu lệnh đơn (ít nhất một ô mot > 0) nộp vào hàng đợi K giá trị mot lớn nhất của nó
    (K = round(mật độ đích x N), ít nhất 1).
  - Ngưỡng hạng K của nến đang xét = giá trị lớn thứ K trong gộp các giá trị của N nến có số liệu liền trước
    (chưa đủ K giá trị -> 0). Chưa đủ MIN_BARS nến có số liệu -> dùng ngưỡng cố định (10).
  - Ngưỡng dùng = max(sàn, ngưỡng hạng K); nếu trần > 0 thì min(trần, ...). Ô nổ khi mot >= ngưỡng dùng.
  - Gộp vòng gần nhau trong một nến: duyệt mot giảm dần (hòa -> tick thấp trước), bỏ ô cách ô đã giữ <= g tick.
    Rồi giữ nhiều nhất CAP vòng lớn nhất (cap <= 0 = không giới hạn).
"""
import numpy as np, pandas as pd

MIN_BARS = 5


def round_half_up(x):
    return int(np.floor(x + 0.5))


def kth_threshold(prev_tops, K):
    """prev_tops: list các list (top-K mot của từng nến trước, tối đa N nến). Trả giá trị lớn thứ K (0 nếu chưa đủ K giá trị)."""
    v = sorted((x for b in prev_tops for x in b), reverse=True)
    return float(v[K - 1]) if len(v) >= K else 0.0


def merge_cap(cells, g, cap):
    """cells: list (tick, mot) đã đạt ngưỡng. Trả list giữ lại (thứ tự: mot giảm dần, hòa -> tick tăng dần)."""
    order = sorted(cells, key=lambda c: (-c[1], c[0]))
    kept = []
    for c in order:
        if cap > 0 and len(kept) >= cap:
            break
        if g > 0 and any(abs(c[0] - k[0]) <= g for k in kept):
            continue
        kept.append(c)
    return kept


def merge_ticks(avg_range_ticks, div, gmin):
    """Khoảng gộp theo biên độ nến TB các nến trước: max(gmin, round(biên độ / div)); div <= 0 hoặc chưa có biên độ -> gmin."""
    if div <= 0 or not (avg_range_ticks > 0):
        return gmin
    return max(gmin, round_half_up(avg_range_ticks / div))


def run_reference(bars, N=20, density=0.5, floor=5, ceil=0, fixed=10, cap=3, div=8, gmin=2):
    """bars: list theo thứ tự thời gian; mỗi nến = list (tick, mot) các ô (mot có thể = 0).
    Nến không có ô nào mot > 0 = nến không có số liệu lệnh đơn: không nổ, không vào hàng đợi.
    Trả list theo nến: (ngưỡng dùng, khoảng gộp g, [(tick, mot) giữ lại])."""
    K = max(1, round_half_up(density * N))
    q, rq, out = [], [], []
    for cells in bars:
        if len(q) >= MIN_BARS:
            thr = max(floor, kth_threshold(q, K))
            if ceil > 0:
                thr = min(thr, ceil)
        else:
            thr = fixed
        g = merge_ticks(sum(rq) / len(rq), div, gmin) if len(rq) >= MIN_BARS else gmin
        hit = [(t, m) for t, m in cells if m > 0 and m >= thr]
        out.append((thr, g, merge_cap(hit, g, cap)))
        live = [(t, m) for t, m in cells if m > 0]
        if live:
            q.append(sorted((m for _, m in live), reverse=True)[:K])
            rq.append(max(t for t, _ in live) - min(t for t, _ in live))
            if len(q) > N:
                q.pop(0); rq.pop(0)
    return out


# ---------- bản nhanh (numpy) để quét tham số; kết quả phải trùng run_reference (bt_selftest.py) ----------
def thresholds(c, bars, N, K):
    """Ngưỡng hạng K (chưa áp sàn/trần) cho từng nến trong bars (NaN nếu chưa đủ MIN_BARS)."""
    nb = len(bars)
    bid = c.t.map(pd.Series(np.arange(nb), index=bars.t.values)).values
    o = np.lexsort((-c.mot.values, bid))
    b = bid[o]; m = c.mot.values[o].astype(float)
    rank = np.arange(len(b)) - np.searchsorted(b, b, 'left')
    top = np.zeros((nb, K)); keep = rank < K
    top[b[keep], rank[keep]] = m[keep]
    thr = np.full(nb, np.nan)
    for i in range(MIN_BARS, nb):
        w = top[max(0, i - N):i].ravel()
        thr[i] = np.partition(w, len(w) - K)[len(w) - K] if len(w) >= K else 0.0
    return thr


def simulate(c, bars, N=20, density=0.5, floor=5, ceil=0, fixed=10, cap=3, div=8, gmin=2):
    """Trả DataFrame các vòng giữ lại (t, tk, mot, thr, g) và Series ngưỡng dùng theo nến."""
    K = max(1, round_half_up(density * N))
    thr = np.maximum(thresholds(c, bars, N, K), floor)
    if ceil > 0:
        thr = np.minimum(thr, ceil)
    thr = np.where(np.isnan(thr), fixed, thr)
    thr_s = pd.Series(thr, index=bars.t.values)
    R = bars.rng.shift(1).rolling(N, min_periods=MIN_BARS).mean()
    g = np.full(len(bars), gmin)
    if div > 0:
        ok = (R > 0).values
        g[ok] = np.maximum(gmin, np.floor(R.values[ok] / div + 0.5)).astype(int)
    g_s = pd.Series(g, index=bars.t.values)
    x = c.copy(); x['thr'] = x.t.map(thr_s).values
    x = x[x.mot >= x.thr].copy()
    x['g'] = x.t.map(g_s).values
    if len(x) == 0:
        return x, thr_s
    cnt = x.groupby('t').tk.transform('size')
    one = x[cnt == 1]; many = x[cnt > 1]
    keep = [one]
    for t, G in many.groupby('t'):
        kk = merge_cap(list(zip(G.tk.values, G.mot.values)), int(G.g.iloc[0]), cap)
        keep.append(G[G.tk.isin([k[0] for k in kk])])
    return pd.concat(keep).sort_values(['t', 'tk']), thr_s
