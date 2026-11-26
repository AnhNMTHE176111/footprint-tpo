"""Trích tam giác kiệt sức CORVEN từ khung hình Meet 07/11 (GC M1 + NQ M1). Ghi raw_marks.csv + ảnh soát (thư mục dbg/).
Toạ độ hiệu chỉnh (calib) tính trên khung phóng 1,2 lần (1920x1080); ảnh jpg là 1600x900."""
import json, os, sys, numpy as np, pandas as pd
from PIL import Image, ImageDraw
import tri
FR = '../../../corven-meet/2026-11-07/frames/'; DF = '../../../data-export/data-footprint/'
SC = 1.2
def bars(sym):
    if sym == 'GC':
        b = pd.read_csv(DF + 'fp_GCZ26_XCEC_Time_20260811-20261109_90d_bars.csv', parse_dates=['datetime']); b = b[(b.datetime >= '2026-11-04') & (b.datetime < '2026-11-08')]
    else:
        b = pd.read_csv(DF + 'fp_NQZ26_XCME_Time_20260826-20261124_90d_bars.csv', parse_dates=['datetime']); b = b[(b.datetime >= '2026-11-05') & (b.datetime < '2026-11-07 12:00')]
    return b.reset_index(drop=True).set_index('datetime')
CAL = {}
for k, v in json.load(open('../calib.json')).items(): CAL[k] = ('GC', v)
for k, v in json.load(open('nq_calib.json')).items(): CAL[k] = ('NQ', v)
SKIP = {'0-05-05', '1-07-55'}
# vùng xét (toạ độ jpg): x0, y0, x1, y1 ; và các ô loại trừ (cửa sổ Meet che...)
ROI = {'default': (50, 226, 1140, 0)}
def run(dbg=True):
    os.makedirs('dbg', exist_ok=True); rows = []; vis = []
    BB = {s: bars(s) for s in ('GC', 'NQ')}
    for fr, (sym, c) in sorted(CAL.items()):
        if fr in SKIP: continue
        B = BB[sym]; t0 = B.index[0]
        im = Image.open(FR + fr + '.jpg').convert('RGB'); a = np.asarray(im)
        ybot = int(c['y1'] / SC) if sym == 'GC' else int(c['y1'] / SC) + 20
        roi = (50, 226, 1140, ybot)
        det = tri.detect(a, roi, amin=5, wmin=3, hmin=2)
        X = lambda t: (c['x0'] + c['s'] * (int((t - t0).total_seconds() // 60) - c['n0'] + c['kmin'])) / SC
        Yp = lambda p: (c['a'] + c['bb'] * p) / SC
        T = lambda x: t0 + pd.Timedelta(minutes=int(round((x * SC - c['x0']) / c['s'])) - c['kmin'] + c['n0'])
        if dbg:
            z = 2; big = im.crop((40, 215, 1150, ybot + 12)).resize((1110 * z, (ybot + 12 - 215) * z), Image.LANCZOS); dr = ImageDraw.Draw(big)
        tmin, tmax = T(roi[0] + 4), T(roi[2] - 4)
        for t in pd.date_range(tmin, tmax, freq='1min'):
            if t not in B.index: continue
            x = X(t); yh = Yp(B.high[t]); yl = Yp(B.low[t])
            vis.append((fr, sym, t, x, yh, yl))
            if dbg:
                for yy in (yh, yl): dr.line(((x - 40) * z - 5, (yy - 215) * z, (x - 40) * z + 5, (yy - 215) * z), fill=(0, 200, 0), width=1)
        for k, cx, yt, yb, w, ar in det:
            t = T(cx); off = cx - X(t); ok = t in B.index
            pc = ((yt + yb) / 2 * SC - c['a']) / c['bb']
            ext = (B.high[t] if k == 'T' else B.low[t]) if ok else np.nan
            rows.append(dict(frame=fr, sym=sym, t_utc=t, vn=(t + pd.Timedelta(hours=7)).strftime('%H:%M'), side=k, x=round(cx, 1), y=(yt + yb) / 2, w=w, area=ar, xoff=round(off, 1), mark_price=round(pc, 2), bar_ext=ext, d_price=round(pc - ext, 2) if ok else np.nan))
            if dbg:
                Xc = (cx - 40) * z; Yc = ((yt + yb) / 2 - 215) * z
                dr.rectangle((Xc - 13, Yc - 13, Xc + 13, Yc + 13), outline=(255, 0, 255) if k == 'T' else (0, 130, 0), width=2)
                dr.text((Xc - 14, Yc + (-26 if k == 'T' else 15)), t.strftime('%H:%M'), fill=(0, 0, 0))
        if dbg: big.save('dbg/%s.png' % fr)
    R = pd.DataFrame(rows); R.to_csv('raw_marks.csv', index=False)
    pd.DataFrame(vis, columns=['frame', 'sym', 't_utc', 'x', 'yh', 'yl']).to_csv('raw_visible.csv', index=False)
    return R
if __name__ == '__main__':
    R = run(); pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
    print(R.groupby(['frame', 'sym', 'side']).size().unstack(fill_value=0))
    print(R[(R.xoff.abs() > 2.5)])
