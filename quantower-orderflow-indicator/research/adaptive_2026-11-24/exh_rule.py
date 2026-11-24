"""Kiệt sức: bản CHUẨN từng nến (để so C# = Python).
Luật đề xuất (mọi mã, mọi khung):
  râu phía đang xét >= 3 tick;
  S = tổng bên soi (Ask ở đỉnh, Bid ở đáy) trên 6 tick từ cực trị đi vào trong (tick trống = 0);
  (1) S <= 1,1 x volume TB mỗi ô có giao dịch của 20 nến ĐÃ ĐÓNG trước          [luật cũ, giữ nguyên, cần >= 5 nến]
  (2) S <= c x trung vị của S trên N nến ĐÃ ĐÓNG trước, gộp cả đỉnh lẫn đáy (2N giá trị), N = nbase(phút nến), cần >= 5 nến; c = 0,8
      (mọi nến đã đóng có giao dịch và high > low đều nộp 2 giá trị S vào hàng đợi, kể cả khi râu ngắn)
  Chưa đủ nền của (2) thì chỉ áp (1)."""
import numpy as np
MIN_BARS = 5

def tail_sum(levels, ext, top, n=6):
    """levels: dict tick -> (bid, ask). Tổng bên soi trên n tick từ cực trị ext đi vào trong."""
    step = -1 if top else 1
    return sum((levels.get(ext + step * j, (0, 0))[1 if top else 0]) for j in range(n))

def median(v):
    v = sorted(v); n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0

def run_reference(bars, N, c=0.8, ratio=1.1, wick_min=3, n=6, hist_bars=20):
    """bars: list theo thời gian; mỗi nến = (o, h, l, c theo tick, cells) với cells = list (tick, bid, ask, vol) (vol > 0).
    Trả list theo nến: (đỉnh có dấu, đáy có dấu)."""
    qmean, qtail, out = [], [], []
    for o, h, l, cl, cells in bars:
        lv = {t: (b, a) for t, b, a, v in cells if v > 0}
        top = bot = False
        if lv and h > l and len(qmean) >= MIN_BARS:
            base1 = ratio * sum(qmean[-hist_bars:]) / len(qmean[-hist_bars:])
            base2 = c * median([x for pair in qtail[-N:] for x in pair]) if (c > 0 and len(qtail) >= MIN_BARS) else float('inf')
            for is_top in (True, False):
                wick = (h - max(o, cl)) if is_top else (min(o, cl) - l)
                S = tail_sum(lv, h if is_top else l, is_top, n)
                hit = wick >= wick_min and S <= base1 and S <= base2
                if is_top: top = hit
                else: bot = hit
        out.append((top, bot))
        if lv:
            vols = [v for _, _, _, v in cells if v > 0]; qmean.append(sum(vols) / len(vols))
            if h > l: qtail.append((tail_sum(lv, h, True, n), tail_sum(lv, l, False, n)))
            qmean = qmean[-hist_bars:]; qtail = qtail[-max(N, 1):]
    return out
