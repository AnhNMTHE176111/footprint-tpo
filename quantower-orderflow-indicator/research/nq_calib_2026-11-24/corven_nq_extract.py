"""Đo chấm của CORVEN trên chart NQZ26 M1 (Sierra, Meet 07/11, phút 2:45-10:30 của buổi), đổi sang (nến UTC, giá).
Tái dùng bộ đo của research/ (bubble_common.candles/slots/fit, detect_bubbles.blobs) — cùng layout Meet 1920x1080.
Ảnh: trích từ video D:/record_video 15 giây/khung (a_012..a_040, b_001..b_002) vào thư mục --img.
Chạy: python corven_nq_extract.py --img <thư mục ảnh>"""
import sys, json, numpy as np, pandas as pd
from PIL import Image
sys.path.insert(0, '..')
import bubble_common as bc
import detect_bubbles as db
IMG = sys.argv[sys.argv.index('--img') + 1]
BARS = '../../../data-export/data-footprint/fp_NQZ26_XCME_Time_20260826-20261124_90d_bars.csv'
b = pd.read_csv(BARS, parse_dates=['datetime'])
b = b[(b.datetime >= '2026-11-03 22:00') & (b.datetime < '2026-11-06 22:00')].reset_index(drop=True)
db.PROTO['tim'] = (200, 51, 239)      # tím của chart NQ hơi khác chart GC; xanh/đỏ giữ nguyên
X0, X1, Y0, Y1 = 60, 1360, 268, 752
names = [f'a_{i:03d}' for i in range(12, 41)] + ['b_001', 'b_002']
_, _, _, ROW = bc.minute_grid(b)
cal, rows = {}, []
for n in names:
    im = Image.open(f'{IMG}/{n}.png')
    c = bc.candles(im, X0, X1, Y0, Y1, minlen=6)
    try:
        x0, s, d = bc.slots(c, 12, 26)
        best, kmin = bc.fit(d, b, Y0, Y1)
    except Exception as e:
        print(n, 'ERR', e); continue
    cost, m0, a_, bb = best[0]
    nxt = best[1][0] if len(best) > 1 else 99
    cal[n] = dict(cost=cost, next=nxt, x0=x0, s=s, n0=int(m0), kmin=int(kmin), a=a_, bb=bb, first=str(b.datetime.iloc[0] + pd.Timedelta(minutes=int(m0))))
    print(n, 'cost %.2f next %.2f s=%.2f nslot=%d first=%s px/tick=%.2f' % (cost, nxt, s, len(d), cal[n]['first'], abs(bb) * 0.25))
    a = np.asarray(im.convert('RGB')).astype(int)
    for col in db.PROTO:
        for x, y, r in db.blobs(a, col, x0=X0, x1=X1, y0=Y0, y1=Y1):
            k = int(round((x - x0) / s))
            if abs(x - (x0 + s * k)) > s * 0.35: continue
            idx = bc.slot_row(cal[n], k, ROW)
            if idx is None: continue
            price = (y - a_) / bb
            rows.append(dict(frame=n, color=col, x=round(x, 1), y=round(y, 1), r=round(r, 2), idx=idx, utc=str(b.datetime[idx]), price=round(price, 2)))
json.dump(cal, open('corven_nq_calib.json', 'w'), indent=1)
df = pd.DataFrame(rows); df.to_csv('corven_nq_raw.csv', index=False)
print(len(df)); print(df.groupby(['frame', 'color']).size().unstack(fill_value=0).to_string())
