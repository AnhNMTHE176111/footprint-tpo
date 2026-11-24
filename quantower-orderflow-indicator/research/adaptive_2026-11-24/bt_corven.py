"""Big Trade so với 25 vòng mờ CORVEN trên chart M5 GC 18/11 (12:15-14:20 UTC, ../corven_m5_2026-11-18/gt_corven_m5.csv).
Nhật ký lệnh đơn SỐNG GCZ26 M1 có phủ khoảng này -> dựng M5 (max theo giá), xem lệnh đơn tại vị trí vòng CORVEN và recall của từng luật.
Khớp: cùng nến M5, cách tâm vòng CORVEN <= TOL tick. Chạy: python bt_corven.py"""
import numpy as np, pandas as pd
from bt_common import *
from bt_rule import simulate
from common_window import nbase
pd.set_option('display.width', 250)
TOL = 4
gt = pd.read_csv('../corven_m5_2026-11-18/gt_corven_m5.csv'); gt = gt[gt.type == 'big'].copy()
gt['t'] = pd.to_datetime(gt.bar_time); gt['tk'] = np.round(gt.price_centre / 0.1).astype(int)
d = load_m1('GClive'); day = d[(d.t >= '2026-11-18 06:00') & (d.t < '2026-11-18 16:00')]
n1 = day.groupby(day.t.dt.floor('5min')).t.nunique()
win = n1[(n1.index >= '2026-11-18 12:15') & (n1.index <= '2026-11-18 14:20')]
print(f'nhật ký M1 trong 12:15-14:24: {int(win.sum())}/130 nến; nến M5 đủ 5 nến M1: {(win == 5).sum()}/26; thiếu: {dict(win[win < 5])}')
c = to_tf(day, 5); b = bars_of(c); cw = c[(c.t >= '2026-11-18 12:15') & (c.t <= '2026-11-18 14:20')]
# lệnh đơn lớn nhất quanh mỗi vòng CORVEN
rows = []
for r in gt.itertuples():
    g = cw[(cw.t == r.t) & ((cw.tk - r.tk).abs() <= TOL)]
    rows.append(dict(nen=r.t.strftime('%H:%M'), gia=r.price_centre, ban_kinh_px=r.radius_px, mot_max_quanh=int(g.mot.max()) if len(g) else 0, mot_dung_tick=int(g[g.tk == r.tk].mot.max()) if (g.tk == r.tk).any() else 0,
                     mot_max_ca_nen=int(cw[cw.t == r.t].mot.max()) if (cw.t == r.t).any() else 0))
G = pd.DataFrame(rows); print(G.to_string(index=False))
print('lệnh đơn lớn nhất quanh vòng CORVEN (±%d tick): trung vị %.0f, nhỏ nhất %d, phân vị 25 = %.0f; số vòng có lệnh >= 10: %d/25, >= 5: %d/25, >= 3: %d/25' % (
    TOL, G.mot_max_quanh.median(), G.mot_max_quanh.min(), G.mot_max_quanh.quantile(.25), (G.mot_max_quanh >= 10).sum(), (G.mot_max_quanh >= 5).sum(), (G.mot_max_quanh >= 3).sum()))
print('tương quan bán kính vòng CORVEN với lệnh đơn lớn nhất quanh nó:', round(np.corrcoef(G.ban_kinh_px, G.mot_max_quanh)[0, 1], 2))
def score(name, H):
    H = H[(H.t >= '2026-11-18 12:15') & (H.t <= '2026-11-18 14:20')]
    hit = sum(((H.t == r.t) & ((H.tk - r.tk).abs() <= TOL)).any() for r in gt.itertuples())
    ok = sum(((gt.t == r.t) & ((gt.tk - r.tk).abs() <= TOL)).any() for r in H.itertuples())
    return dict(luat=name, vong=len(H), vong_nen=round(len(H) / 26, 2), recall=f'{hit}/25', precision=f'{ok}/{len(H)}')
rows = [score(f'cố định >= {T}', c[c.mot >= T]) for T in (3, 5, 8, 10, 15, 20)]
for name, kw in (('thích nghi 0,75 · sàn 5 · gộp R/8 · tối đa 3', dict(density=0.75, floor=5, cap=3, div=8, gmin=2)),
                 ('thích nghi 0,75 · sàn 5 · không gộp/giới hạn', dict(density=0.75, floor=5, cap=0, div=0, gmin=0)),
                 ('thích nghi 1,0 · sàn 5 · gộp R/8 · tối đa 3', dict(density=1.0, floor=5, cap=3, div=8, gmin=2)),
                 ('thích nghi 1,5 · sàn 5 · gộp R/8 · tối đa 4', dict(density=1.5, floor=5, cap=4, div=8, gmin=2)),
                 ('thích nghi 1,5 · sàn 5 · gộp 2 tick · tối đa 5', dict(density=1.5, floor=5, cap=5, div=0, gmin=2)),
                 ('thích nghi 2,0 · sàn 5 · gộp 2 tick · không giới hạn', dict(density=2.0, floor=5, cap=0, div=0, gmin=2)),
                 ('thích nghi 2,0 · sàn 3 · gộp 2 tick · không giới hạn', dict(density=2.0, floor=3, cap=0, div=0, gmin=2))):
    H, thr = simulate(c, b, N=nbase(5), **kw); r = score(name, H); r['nguong_tv'] = np.median(thr[(thr.index >= pd.Timestamp('2026-11-18 12:15')) & (thr.index <= pd.Timestamp('2026-11-18 14:20'))]); rows.append(r)
print(pd.DataFrame(rows).to_string(index=False))
