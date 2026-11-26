"""Gộp tam giác đã soát thành đáp án: gt_sides.csv (mỗi dòng = một phía của một nến NHÌN THẤY trên ít nhất một khung hình; y = 1 nếu CORVEN có tam giác).
Mẫu: NQ_A = ảnh 13.png (NQ 06/11 14:39-16:01 VN, soát mắt, 8 dấu); NQ_B = các khung Meet NQ khác; GC = 18 khung Meet GC M1 05-06/11."""
import pandas as pd, numpy as np
R = pd.read_csv('raw_marks.csv', parse_dates=['t_utc']); V = pd.read_csv('raw_visible.csv', parse_dates=['t_utc'])
DROP_ROWS = [94, 95, 96]                       # đường vẽ tay màu vàng trên khung 0-58-35
DROP_FRAMES = {'0-04-00', '0-07-55'}           # 0-04-00: khung đang cuộn (bóng mờ), dấu trùng 0-09-42; 0-07-55: trùng ảnh 13.png
XMAX = {'0-03-20': 1040, '0-09-42': 1040, '0-10-25': 1050}     # bên phải là volume profile che
EXCL = {'0-03-20': (975, 395, 1200, 700)}      # cửa sổ Meet che
R = R.drop(index=DROP_ROWS); R = R[~R.frame.isin(DROP_FRAMES)]
V = V[~V.frame.isin(DROP_FRAMES)]
YTOP = 230
def inside(fr, x, y, ybot):
    if x < 54 or x > XMAX.get(fr, 1134) or y < YTOP or y > ybot: return False
    e = EXCL.get(fr)
    return not (e and e[0] <= x <= e[2] and e[1] <= y <= e[3])
import json
cal = {**json.load(open('../calib.json')), **json.load(open('nq_calib.json'))}
rows = []
for r in V.itertuples():
    ybot = cal[r.frame]['y1'] / 1.2 - 4 + (20 if r.sym == 'NQ' else 0)
    off = 4 if r.sym == 'GC' else 10          # tâm tam giác lệch vào trong so với cực trị (px)
    for side, y in (('T', r.yh + off), ('B', r.yl - off)):
        if inside(r.frame, r.x, y, ybot): rows.append((r.sym, r.t_utc, side, r.frame))
Vs = pd.DataFrame(rows, columns=['sym', 't_utc', 'side', 'frame'])
M = R[[inside(f, x, y, 9999) for f, x, y in zip(R.frame, R.x, R.y)]][['sym', 't_utc', 'side', 'frame']]
# 0-10-25 dấu lệch khe 3,8 px (14:05 T): tam giác bị che một nửa, soát mắt là của nến 14:05
key = ['sym', 't_utc', 'side']
nv = Vs.groupby(key).frame.nunique().rename('n_vis'); nm = M.groupby(key).frame.nunique().rename('n_mark')
G = pd.concat([nv, nm], axis=1).fillna(0).reset_index(); G = G[G.n_vis > 0]
G['y'] = (G.n_mark > 0).astype(int); G['sample'] = np.where(G.sym == 'GC', 'GC', 'NQ_B')
print('nhìn thấy >= 2 khung:', (G.n_vis >= 2).sum(), '| có dấu ở mọi khung:', ((G.n_vis >= 2) & (G.n_mark == G.n_vis)).sum(), '| có dấu ở một phần khung:', ((G.n_vis >= 2) & (G.n_mark > 0) & (G.n_mark < G.n_vis)).sum())
print(G[(G.n_vis >= 2) & (G.n_mark > 0) & (G.n_mark < G.n_vis)])
# NQ_A: ảnh 13.png
TOP = ['14:40', '15:03', '15:08', '15:35', '15:59']; BOT = ['15:20', '15:24', '15:51']
A = []
for t in pd.date_range('2026-11-06 07:39', '2026-11-06 09:01', freq='1min'):
    vn = (t + pd.Timedelta(hours=7)).strftime('%H:%M')
    A.append(('NQ', t, 'T', 1, int(vn in TOP), int(vn in TOP), 'NQ_A')); A.append(('NQ', t, 'B', 1, int(vn in BOT), int(vn in BOT), 'NQ_A'))
A = pd.DataFrame(A, columns=['sym', 't_utc', 'side', 'n_vis', 'n_mark', 'y', 'sample'])
G = G[~((G.sym == 'NQ') & G.t_utc.isin(A.t_utc))]
G = pd.concat([A, G]).sort_values(['sample', 't_utc', 'side'])
G.to_csv('gt_sides.csv', index=False)
print(G.groupby('sample').agg(sides=('y', 'size'), marks=('y', 'sum'), bars=('t_utc', 'nunique')))
print(G[G.y == 1].groupby(['sample', 'side']).size())
