"""Câu 1 (phần CORVEN): recall / precision theo sàn x bộ số x "nổ ở mọi mức giá", trên ba mẫu CORVEN:
  GC M1 (580 nến, 885 chấm), NQ M1 (534 nến, chart gộp hàng 8 tick -> chỉ tham khảo), GC M5 18/11 (26 nến, 16 cụm).
Khớp như ../adaptive_2026-11-24/dot_recall3.py: M1 cùng nến, cùng màu (tím = cả hai), cách <= 3 tick; M5 cụm có chấm cùng nến, cùng màu, cách tâm <= 5 tick.
Thêm: volume thật tại ô mà CORVEN vẽ chấm (GC M1) -> trần recall của từng sàn, không phụ thuộc k.
Chạy: python floor_corven.py"""
from floor_lib import *
from corven_nq_compare import corven_nq, corven_gc, match
pd.set_option('display.width', 300); pd.set_option('display.max_rows', 500)
os.chdir(NQDIR); Cn, cov_n, _ = corven_nq(); Cg, cov_g = corven_gc(); os.chdir(HERE)
cov_n = pd.DatetimeIndex(cov_n); cov_g = pd.DatetimeIndex(cov_g)
print(f'CORVEN GC M1: {len(Cg)} chấm / {len(cov_g)} nến = {len(Cg)/len(cov_g):.2f}; phiên của nến: {pd.Series(ses_of(cov_g)).value_counts().to_dict()}; ngày: {sorted(set(cov_g.date))}')
print(f'CORVEN NQ M1: {len(Cn)} chấm / {len(cov_n)} nến = {len(Cn)/len(cov_n):.2f}; phiên: {pd.Series(ses_of(cov_n)).value_counts().to_dict()}; ngày: {sorted(set(cov_n.date))}')
# M5 GC 18/11
F0 = pd.read_pickle(os.path.join(HERE, '..', 'corven_m5_2026-11-18', 'F_m5.pkl'))
F5 = pd.DataFrame(dict(t=pd.to_datetime(F0.datetime), tk=np.round(F0.price / 0.1).astype(np.int64), bid=F0.bid, ask=F0.ask, vol=F0.vol)); F5 = F5[F5.vol > 0]
S5 = F5.groupby('t').agg(med=('vol', 'median'), hi=('tk', 'max'), lo=('tk', 'min')); S5['rng'] = S5.hi - S5.lo
gt = pd.read_csv(os.path.join(HERE, '..', 'corven_m5_2026-11-18', 'gt_corven_m5.csv')); gt = gt[gt.type == 'dot'].copy(); gt['t'] = pd.to_datetime(gt.bar_time); gt['tk'] = np.round(gt.price_centre / 0.1).astype(int)
def m5hit(D):
    D = D[(D.t >= '2026-11-18 12:15') & (D.t <= '2026-11-18 14:20')]
    return len(D), sum(((D.t == r.t) & (D.col == ('S' if r.colour == 'red' else 'B')) & ((D.tk - r.tk).abs() <= 5)).any() for r in gt.itertuples())

Fg, Sg = load('GC', 1); Fn, Sn = load('NQ', 1)
rows = []
for pn in PRESETS:
    for al in (False, True):
        Dg, tg = cands(Fg[Fg.t.isin(cov_g)], Sg, 1, pn, al); Dn, tn = cands(Fn[Fn.t.isin(cov_n)], Sn, 1, pn, al); D5, t5 = cands(F5, S5, 5, pn, al)
        for f in FLOORS:
            Xg = apply_floor(Dg, f); Xn = apply_floor(Dn, f); X5 = apply_floor(D5, f)
            rg = match(Cg, Xg, 3); rn = match(Cn, Xn, 3); n5, h5 = m5hit(X5)
            sg = ses_of(pd.DatetimeIndex(Cg.t)); rs = {}
            for s in SES:
                c = Cg[sg == s]; x = Xg[ses_of(pd.DatetimeIndex(Xg.t)) == s]
                rs[s] = match(c, x, 3)[:2] if len(c) else (np.nan, np.nan)
            rows.append(dict(bo=pn, moi_muc_gia=int(al), san=f, GC_M1_cham_nen=round(len(Xg) / len(cov_g), 2), GC_M1_recall=round(rg[0], 3), GC_M1_precision=round(rg[1], 3), GC_M1_F1=round(rg[2], 3),
                             **{f'GC_rec_{s}': round(rs[s][0], 2) for s in SES}, **{f'GC_prec_{s}': round(rs[s][1], 2) for s in SES},
                             NQ_M1_cham_nen=round(len(Xn) / len(cov_n), 2), NQ_M1_recall=round(rn[0], 3), NQ_M1_precision=round(rn[1], 3), GC_M5_cham=n5, GC_M5_cum=h5))
R = pd.DataFrame(rows); R.to_csv('out_floor_corven.csv', index=False); print(R.to_string(index=False))
print(f'số chấm CORVEN GC M1 theo phiên: {pd.Series(ses_of(pd.DatetimeIndex(Cg.t))).value_counts().to_dict()}; ngưỡng k x B trung vị trong mẫu GC (không sót): {np.nanmedian((2.0 * base(Sg, 1)[0]).reindex(cov_g)):.1f}; NQ: {np.nanmedian((2.0 * base(Sn, 1)[0]).reindex(cov_n)):.1f}')

# ---- volume thật tại ô CORVEN vẽ chấm (GC M1): lấy volume cùng bên lớn nhất trong ±tol tick quanh chấm
print('\n=== Volume cùng bên tại ô CORVEN vẽ chấm, GC M1 (đỏ = Bid, xanh = Ask, tím = lớn hơn trong hai bên)')
G = {t: g.set_index('tk') for t, g in Fg[Fg.t.isin(cov_g)].groupby('t')}
for tol in (0, 1, 3):
    vs = []
    for r in Cg.itertuples():
        g = G.get(r.t)
        if g is None: vs.append(0); continue
        x = g[(g.index >= r.tk - tol) & (g.index <= r.tk + tol)]
        if x.empty: vs.append(0); continue
        vs.append(x.bid.max() if r.color == 'do' else x.ask.max() if r.color == 'xanh' else max(x.bid.max(), x.ask.max()))
    vs = np.array(vs, float)
    print(f'±{tol} tick: phân vị 5/10/25/50/75/90 = {np.percentile(vs, [5, 10, 25, 50, 75, 90]).round(0).tolist()};  tỉ lệ chấm CORVEN có volume < sàn: ' + ', '.join(f'{f}: {100 * (vs < f).mean():.0f}%' for f in FLOORS[1:]))
    if tol == 3:
        sg = ses_of(pd.DatetimeIndex(Cg.t))
        for s in SES:
            if (sg == s).any(): print(f'   phiên {SES_VN[s]} ({(sg == s).sum()} chấm): ' + ', '.join(f'{f}: {100 * (vs[sg == s] < f).mean():.0f}%' for f in FLOORS[1:]))
