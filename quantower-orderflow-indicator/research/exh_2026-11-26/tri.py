"""Dò tam giác kiệt sức trên ảnh chart Sierra của CORVEN (khung video 1600x900 hoặc ảnh chụp): vàng mũi xuống (đỉnh) và xanh nhạt mũi lên (đáy).
Tam giác bị râu nến đen cắt đôi nên nối ngang 5 px trước khi gắn nhãn."""
import numpy as np
from scipy import ndimage

def masks(a):
    R, G, B = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    Y = (R > 185) & (G > 150) & (G < 215) & (B < 125) & (R - B > 90)
    C = (R < 140) & (G > 160) & (B > 200) & (B - R > 95)
    return Y, C

def detect(a, roi, amin=12, wmin=6, wmax=18, hmin=3, hmax=14):
    """a: mảng RGB; roi = (x0, y0, x1, y1). Trả list (kind 'T'/'B', cx, y_top, y_bot, w, area)."""
    Y, C = masks(a); x0, y0, x1, y1 = roi; out = []
    for kind, m in (('T', Y), ('B', C)):
        mm = np.zeros_like(m); mm[y0:y1, x0:x1] = m[y0:y1, x0:x1]
        lab, n = ndimage.label(ndimage.binary_closing(mm, structure=np.ones((1, 5))) | mm)
        for i, sl in enumerate(ndimage.find_objects(lab)):
            sub = mm[sl] & (lab[sl] == i + 1); ar = int(sub.sum())
            if ar < amin: continue
            ys, xs = np.nonzero(sub); h = ys.max() - ys.min() + 1; w = xs.max() - xs.min() + 1
            if not (wmin <= w <= wmax and hmin <= h <= hmax): continue
            cx = sl[1].start + (xs.min() + xs.max()) / 2
            out.append((kind, float(cx), int(sl[0].start + ys.min()), int(sl[0].start + ys.max()), int(w), ar))
    return sorted(out, key=lambda o: o[1])
