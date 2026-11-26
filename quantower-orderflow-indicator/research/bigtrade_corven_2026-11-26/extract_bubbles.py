"""Trich bong (cham xanh/do/tim + co) cua CORVEN tu khung Meet 07/11 (GC M1 + NQ M1). -> raw_bubbles.csv + dbg/bub_*.png
Toa do calib tinh tren khung 1920x1080; jpg la 1600x900 (SC=1.2)."""
import json, os, sys, numpy as np, pandas as pd
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
FR = HERE + '/../../../corven-meet/2026-11-07/frames/'; DF = HERE + '/../../../data-export/data-footprint/'
SC = 1.2
PROTO = {'B': (100, 100, 250), 'R': (214, 4, 0), 'V': (204, 98, 236)}
def bars(sym):
    if sym == 'GC':
        b = pd.read_csv(DF + 'fp_GCZ26_XCEC_Time_20260811-20261109_90d_bars.csv', parse_dates=['datetime']); b = b[(b.datetime >= '2026-11-04') & (b.datetime < '2026-11-08')]
    else:
        b = pd.read_csv(DF + 'fp_NQZ26_XCME_Time_20260826-20261124_90d_bars.csv', parse_dates=['datetime']); b = b[(b.datetime >= '2026-11-05') & (b.datetime < '2026-11-07 12:00')]
    return b.reset_index(drop=True).set_index('datetime')
CAL = {}
for k, v in json.load(open(HERE + '/../calib.json')).items(): CAL[k] = ('GC', v)
for k, v in json.load(open(HERE + '/../exh_2026-11-26/nq_calib.json')).items(): CAL[k] = ('NQ', v)
SKIP = {'0-05-05', '1-07-55'}
UP = 3
def blobs(a, color, roi, tol=75, rmin=1.5):
    x0, y0, x1, y1 = roi; sub = Image.fromarray(a[y0:y1, x0:x1].astype(np.uint8)); sub = np.asarray(sub.resize((sub.width * UP, sub.height * UP), Image.BICUBIC)).astype(int)
    res = _blobs(sub, color, tol, rmin * UP)
    return [(cx / UP + x0 - 0.5 + 0.5 / UP, cy / UP + y0 - 0.5 + 0.5 / UP, r / UP, w / UP) for cx, cy, r, w in res]
def _blobs(a, color, tol, rmin):
    p = np.array(PROTO[color]); d = np.sqrt(((a - p) ** 2).sum(axis=2)); m = d < tol
    x0, y0, x1, y1 = 0, 0, a.shape[1], a.shape[0]; mm = np.zeros_like(m); mm[y0:y1, x0:x1] = m[y0:y1, x0:x1]; m = mm
    dt = ndi.distance_transform_edt(m); mx = ndi.maximum_filter(dt, size=5 * UP); pk = (dt == mx) & (dt >= rmin)
    lab, n = ndi.label(pk); out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i); cx, cy, r = xs.mean(), ys.mean(), dt[ys[0], xs[0]]
        row = m[int(round(cy)), :]; xi = int(round(cx)); l = xi; rr = xi
        while l > 0 and row[l - 1]: l -= 1
        while rr < len(row) - 1 and row[rr + 1]: rr += 1
        col_ = m[:, xi]; u = int(round(cy)); dn = u
        while u > 0 and col_[u - 1]: u -= 1
        while dn < len(col_) - 1 and col_[dn + 1]: dn += 1
        w = rr - l + 1; h = dn - u + 1
        if w > 3.0 * max(h, 6): continue
        out.append((cx, cy, r, w))
    out.sort(key=lambda t: -t[2]); keep = []
    for q in out:
        if all((q[0] - k[0]) ** 2 + (q[1] - k[1]) ** 2 > (0.9 * max(q[2], k[2])) ** 2 for k in keep): keep.append(q)
    return keep
def drawn(a, x, yh, yl):
    """Nen co that su duoc ve o cot x khong: >= 50% so dong giua dinh va day co diem toi (rau / than den / vien than trang) trong x +-3."""
    y0 = int(round(min(yh, yl))); y1 = int(round(max(yh, yl))) + 1; xi = int(round(x))
    if y0 < 0 or y1 >= a.shape[0] or xi < 4 or xi >= a.shape[1] - 4: return False
    blk = a[y0:y1 + 1, xi - 3:xi + 4]; dark = (blk.max(axis=2) < 110).any(axis=1)
    return dark.mean() >= 0.5
def run():
    os.makedirs(HERE + '/dbg', exist_ok=True); rows = []; vis = []
    BB = {s: bars(s) for s in ('GC', 'NQ')}
    for fr, (sym, c) in sorted(CAL.items()):
        if fr in SKIP or not os.path.exists(FR + fr + '.jpg'): continue
        B = BB[sym]; t0 = B.index[0]
        im = Image.open(FR + fr + '.jpg').convert('RGB'); a = np.asarray(im).astype(int)
        ybot = int(c['y1'] / SC) if sym == 'GC' else int(c['y1'] / SC) + 20
        roi = (50, 226, 1140, ybot)
        X = lambda t: (c['x0'] + c['s'] * (int((t - t0).total_seconds() // 60) - c['n0'] + c['kmin'])) / SC
        Yp = lambda p: (c['a'] + c['bb'] * p) / SC
        T = lambda x: t0 + pd.Timedelta(minutes=int(round((x * SC - c['x0']) / c['s'])) - c['kmin'] + c['n0'])
        z = 3; big = im.crop((40, 215, 1150, ybot + 12)).resize((1110 * z, (ybot + 12 - 215) * z), Image.LANCZOS); dr = ImageDraw.Draw(big)
        for t in pd.date_range(T(roi[0] + 4), T(roi[2] - 4), freq='1min'):
            if t not in B.index: continue
            x = X(t)
            vis.append((fr, sym, t, drawn(a, x, Yp(B.high[t]), Yp(B.low[t]))))
            for yy in (Yp(B.high[t]), Yp(B.low[t])): dr.line(((x - 40) * z - 6, (yy - 215) * z, (x - 40) * z + 6, (yy - 215) * z), fill=(0, 200, 0), width=1)
        for col in PROTO:
            for cx, cy, r, w in blobs(a, col, roi):
                t = T(cx); off = cx - X(t)
                if t not in B.index or abs(off) > 0.35 * c['s'] / SC: continue
                price = (cy * SC - c['a']) / c['bb']
                if price > B.high[t] + 3 * abs(1 / c['bb']) * SC * 2 + (0.3 if sym == 'GC' else 3) or price < B.low[t] - (0.3 if sym == 'GC' else 3): continue
                rows.append(dict(frame=fr, sym=sym, t_utc=t, vn=(t + pd.Timedelta(hours=7)).strftime('%H:%M'), color=col, x=round(cx, 1), y=round(cy, 1), r=round(r, 2), w=w,
                                 price=round(price, 3), px_per_unit=abs(c['bb']) / SC, s=c['s'] / SC))
                Xc = (cx - 40) * z; Yc = (cy - 215) * z; rr = (r + 2.5) * z
                dr.ellipse((Xc - rr, Yc - rr, Xc + rr, Yc + rr), outline={'B': (0, 180, 255), 'R': (255, 160, 0), 'V': (0, 160, 0)}[col], width=2)
        big.save(HERE + '/dbg/bub_%s.png' % fr)
    # anh NQ M1 06/11 14:39-16:01 VN (images/13.png), quy doi nhu nq_rows_2026-11-26/corven_nq_dots.py
    IMG = r'C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/ce3fca11-3030-4b09-9b13-33a6dd7ee683/images/13.png'
    if os.path.exists(IMG):
        im = Image.open(IMG).convert('RGB'); a = np.asarray(im).astype(int); B = BB['NQ']; pitch = (1108 - 78) / 81.0; t00 = pd.Timestamp('2026-11-06 07:39')
        z = 3; big = im.crop((10, 60, 1125, 590)).resize((1115 * z, 530 * z), Image.LANCZOS); dr = ImageDraw.Draw(big)
        for m in range(0, 83):
            t = t00 + pd.Timedelta(minutes=m)
            if t in B.index:
                x = 78 + m * pitch
                vis.append(('IMG13', 'NQ', t, True))
                for p_ in (B.high[t], B.low[t]): yy = 283 - (p_ - 27000) * 2.734; dr.line(((x - 10) * z - 6, (yy - 60) * z, (x - 10) * z + 6, (yy - 60) * z), fill=(0, 200, 0), width=1)
        for col in PROTO:
            for cx, cy, r, w in blobs(a, col, (10, 60, 1125, 590)):
                if cx > 1125 and cy > 320: continue
                m = int(round((cx - 78) / pitch)); t = t00 + pd.Timedelta(minutes=m)
                if t not in B.index or m < 0 or m > 82 or abs(cx - (78 + m * pitch)) > 0.35 * pitch: continue
                price = 27000 - (cy - 283) / 2.734
                if price > B.high[t] + 3 or price < B.low[t] - 3: continue
                rows.append(dict(frame='IMG13', sym='NQ', t_utc=t, vn=(t + pd.Timedelta(hours=7)).strftime('%H:%M'), color=col, x=round(cx, 1), y=round(cy, 1), r=round(r, 2), w=w, price=round(price, 3), px_per_unit=2.734, s=pitch))
                Xc = (cx - 10) * z; Yc = (cy - 60) * z; rr = (r + 2.5) * z
                dr.ellipse((Xc - rr, Yc - rr, Xc + rr, Yc + rr), outline={'B': (0, 180, 255), 'R': (255, 160, 0), 'V': (0, 160, 0)}[col], width=2)
        big.save(HERE + '/dbg/bub_IMG13.png')
    R = pd.DataFrame(rows); R.to_csv(HERE + '/raw_bubbles.csv', index=False)
    Vd = pd.DataFrame(vis, columns=['frame', 'sym', 't_utc', 'drawn']); keep = []
    for fr, g in Vd.groupby('frame'):   # khoang nhin thay = tu nen dau toi nen cuoi THAT SU duoc ve (bo le phai trong cua chart)
        d = g[g.drawn]
        if len(d): keep.append(g[(g.t_utc >= d.t_utc.min()) & (g.t_utc <= d.t_utc.max())])
    pd.concat(keep)[['frame', 'sym', 't_utc']].to_csv(HERE + '/raw_visible.csv', index=False)
    return R
if __name__ == '__main__':
    R = run(); print(R.groupby(['frame', 'sym', 'color']).size().unstack(fill_value=0)); print(R.r.describe())
    print(np.histogram(R.r, bins=[1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 10, 12, 15, 30]))
