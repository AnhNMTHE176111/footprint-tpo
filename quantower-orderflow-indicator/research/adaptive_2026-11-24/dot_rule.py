"""Luật chấm Bid/Ask: bản CHUẨN từng nến (giống CellBigLogic.Evaluate) + bản nhanh numpy để quét tham số.

Công thức chung đề xuất (mọi mã, mọi khung), chỉ dùng N = 20 nến ĐÃ ĐÓNG trước (cần >= 5):
  B   = trung bình của (trung vị volume mỗi ô có giao dịch) trên 20 nến trước          (đã có: CellBigBaseline.TryGetMedian)
  R   = trung bình của (tick cao nhất - tick thấp nhất có giao dịch) trên 20 nến trước  (đã có: CellBigBaseline.TryGetRange)
  w   = max(4, round(R / 6))             cửa sổ "lớn nhất trong ±w tick"
  bộ "ưu tiên không sót": ngưỡng = max(2,0 x B, sàn 5), che chấm xanh cách chấm đỏ <= 2 tick
  bộ "ít nhiễu"         : ngưỡng = max(2,8 x B, sàn 9), che h = max(6, round(0,75 x w))
  N (số nến nền) = min(20, max(5, round(120 / số phút một nến)))   (common_window.nbase)
round = làm tròn nửa lên: floor(x + 0,5).
"""
import numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

MIN_BARS = 5


def round_half_up(x):
    return int(np.floor(x + 0.5))


def window_for(R, D, wmin):
    return max(wmin, round_half_up(R / D)) if (D > 0 and R > 0) else wmin


def evaluate_bar(levels, thr, w, h):
    """levels: list (tick, bid, ask) các ô có volume > 0. Trả (xanh, đỏ): list tick tăng dần. Giống CellBigLogic.Evaluate."""
    bid = {t: b for t, b, a in levels}; ask = {t: a for t, b, a in levels}

    def localmax(side, t, v):
        for o in range(1, w + 1):
            if side.get(t - o, 0) >= v or side.get(t + o, 0) >= v:
                return False
        return True
    reds = [t for t, b, a in sorted(levels) if b > 0 and b >= thr and localmax(bid, t, b)]
    blues = [t for t, b, a in sorted(levels) if a > 0 and a >= thr and localmax(ask, t, a)]
    if h >= 0:
        blues = [t for t in blues if not any(abs(t - r) <= h for r in reds)]
    return blues, reds


def dots_fast(F, thr_bar, w_bar, h_bar):
    """F: bảng ô (t, tk, bid, ask), mọi ô volume > 0. thr_bar / w_bar / h_bar: Series theo t (NaN = nến chưa đủ nền -> bỏ).
    Trả DataFrame chấm (t, tk, col: 'S' đỏ / 'B' xanh, v) sau luật che."""
    F = F[['t', 'tk', 'bid', 'ask']].copy()
    F['thr'] = F.t.map(thr_bar).values; F['w'] = F.t.map(w_bar).values; F['h'] = F.t.map(h_bar).values
    F = F[F.thr.notna() & F.w.notna()].sort_values(['t', 'tk']).reset_index(drop=True)
    F['w'] = F.w.astype(int); F['h'] = F.h.astype(int)
    out = []
    for w, G in F.groupby('w'):
        G = G.reset_index(drop=True)
        first = np.r_[True, G.t.values[1:] != G.t.values[:-1]]
        bar_id = np.cumsum(first) - 1
        lo = G.tk.values[first][bar_id]
        span = np.r_[G.tk.values[np.r_[first[1:], True]] - G.tk.values[first] + 1]
        off = np.concatenate([[0], np.cumsum(span + w + 1)[:-1]])
        pos = off[bar_id] + (G.tk.values - lo)
        Ntot = int(pos.max()) + 1
        for col, c in (('ask', 'B'), ('bid', 'S')):
            v = G[col].values.astype(float)
            if w > 0:
                A = np.zeros(Ntot); A[pos] = v
                pad = np.concatenate([np.zeros(w), A, np.zeros(w + 1)])
                mx = sliding_window_view(pad, w).max(1)
                nm = np.maximum(mx[pos], mx[pos + w + 1])
            else:
                nm = np.zeros(len(G))
            m = (v > 0) & (v >= G.thr.values) & (v > nm)
            H = G.loc[m, ['t', 'tk', 'h']].copy(); H['v'] = v[m]; H['col'] = c
            out.append(H)
    R = pd.concat(out, ignore_index=True)
    red = R[R.col == 'S'][['t', 'tk']].rename(columns={'tk': 'rtk'})
    b = R[R.col == 'B'].reset_index().merge(red, on='t', how='left')
    hidden = b[(b.h >= 0) & ((b.rtk - b.tk).abs() <= b.h)]['index'].unique()
    return R.drop(index=hidden).drop(columns='h').sort_values(['t', 'col', 'tk']).reset_index(drop=True)


def params_for(S, k, D, wmin, hmult=1.5, floor=9.0, hfix=None, N=20):
    """S: bảng theo nến (cột med, rng). Trả (thr, w, h, B, R) theo nến; chỉ dùng N nến trước."""
    B = S.med.shift(1).rolling(N, min_periods=MIN_BARS).mean()
    R = S.rng.shift(1).rolling(N, min_periods=MIN_BARS).mean()
    ok = B.notna() & (B > 0)
    thr = np.maximum(k * B, floor).where(ok)
    w = R.apply(lambda r: window_for(r, D, wmin) if r == r else np.nan).where(ok)
    h = (np.floor(hmult * w + 0.5) if hfix is None else w * 0 + hfix).where(ok)
    return thr, w, h, B, R


# ---------- CÔNG THỨC CHUNG (chốt) ----------
RANGE_PER_WINDOW, W_MIN = 6.0, 4
# hai bộ số: (bội số trung vị k, sàn, tỉ lệ che theo w, che tối thiểu)
PRESET_RECALL = dict(k=2.0, floor=5.0, hide_ratio=0.0, hide_min=2)     # "ưu tiên không sót" (mặc định đề xuất)
PRESET_QUIET = dict(k=2.8, floor=9.0, hide_ratio=0.75, hide_min=6)     # "ít nhiễu" (mật độ gần bằng luật cũ ở M1/M5)


def unified(B, R, k=2.0, floor=5.0, hide_ratio=0.0, hide_min=2):
    """B, R: mức nền và biên độ TB của N nến trước (None / <= 0 = chưa đủ nền). Trả (ngưỡng, w, h) hoặc None nếu chưa có nền.
    ngưỡng = max(k x B, sàn); w = max(4, round(R / 6)); h = max(hide_min, round(hide_ratio x w))."""
    if not (B and B > 0):
        return None
    w = window_for(R if R and R > 0 else 0, RANGE_PER_WINDOW, W_MIN)
    h = max(hide_min, round_half_up(hide_ratio * w))
    return max(k * B, floor), w, h


def run_reference(bars, N, **preset):
    """bars: list theo thứ tự thời gian, mỗi nến = list (tick, bid, ask, vol) (ô vol > 0). Trả list theo nến: None hoặc (ngưỡng, w, h, xanh, đỏ)."""
    qmed, qrng, out = [], [], []
    for cells in bars:
        cells = [c for c in cells if c[3] > 0]
        prm = unified(sum(qmed) / len(qmed), sum(qrng) / len(qrng), **preset) if len(qmed) >= MIN_BARS else None
        if prm is None or not cells:
            out.append(None)
        else:
            blues, reds = evaluate_bar([(t, b, a) for t, b, a, v in cells], *prm)
            out.append((prm[0], prm[1], prm[2], blues, reds))
        if cells:
            vols = sorted(v for _, _, _, v in cells); n = len(vols)
            qmed.append(vols[n // 2] if n % 2 else (vols[n // 2 - 1] + vols[n // 2]) / 2.0)
            qrng.append(max(c[0] for c in cells) - min(c[0] for c in cells))
            if len(qmed) > N:
                qmed.pop(0); qrng.pop(0)
    return out
