"""Review vòng 2 (Fable): kiểm tổ hợp cuối (K=5 + số ngày tối thiểu + T) vì vòng 2 chỉ đổi MỘT yếu tố mỗi lần.
 (a) số lần trượt 8 tiêu chí trên 6 ô x 2 đoạn; (b) nạp 8 ngày cuối với K=5; (c) vượt ngưỡng mà không có chấm nào gần (bằng nhau trong ±w);
 (d) "5 ô lớn nhất phiên" NQ M15 đoạn chọn sót ở phiên nào."""
import sys, time, numpy as np, pandas as pd
from sa_common import load_dot, _cache
from sa_eval_lib import calib_and_density, verdicts
from sa_oracle_lib import rulers, near_dot
import sa2_lib as L
t0 = time.time()
CRIT = ['khop_chung', 'khop_phien', 'khop_gio']
def mk(name, **ch):
    c = dict(L.BASE); c.update(ch); c['name'] = name; c['pa'] = 'thong_ke'; return c
CF = [mk('goc'), mk('K5', K=5), mk('K5_m1_T120', K=5, mind=1), mk('K5_m1_T240', K=5, mind=1, T=240), mk('K5_m2_T120', K=5, mind=2), mk('K5_m3_T240', K=5, T=240)]
rows = []; short = []; tie = []; t5 = []
def keys(ds, res, keep=None):
    k = res.dot if keep is None else (res.dot & keep[ds.sbar]); i = np.nonzero(k)[0]
    return set(zip(ds.t.values[ds.sbar[i]].astype('datetime64[m]').astype(np.int64), ds.sside[i], ds.stk[i]))
for sym in ('GC', 'NQ'):
    for m in (1, 5, 15, 60):
        ds = load_dot(sym, m); Rr = rulers(ds)
        tops = {d: L.top_sets_f(ds, ds.doan_mask(d)) for d in ('chon', 'kiem')}
        for cfg in CF:
            res = L.eval_dot(ds, cfg)
            for doan in ('chon', 'kiem'):
                mask = ds.doan_mask(doan)
                c, d, s = calib_and_density(ds, res, cfg['name'], doan); v = verdicts(s, res.kind)
                o = L.oracle2(ds, res, Rr, mask, ds.w, tops[doan])
                f = [k for k in CRIT if v[k].startswith('TRƯỢT')]
                if o['top20'] < .99: f.append('top20 %.3f' % o['top20'])
                if o['top5'] < .97: f.append('top5 %.3f' % o['top5'])
                if not (o['cuc_tri'] >= .97): f.append('cuc_tri %.3f' % o['cuc_tri'])
                if not (o['nhieu'] <= .05): f.append('nhieu')
                if not (o['le3'] <= .02): f.append('le3')
                ndot = np.bincount(ds.sbar[res.dot], minlength=ds.nb); hs = mask & res.has
                rows.append(dict(cfg=cfg['name'], ma=sym, m=m, doan=doan, truot=len(f), gi=';'.join(f), khop=round(s['khop_chung'], 3), top20=round(o['top20'], 4), top5=round(o['top5'], 4),
                                 cuc_tri=round(o['cuc_tri'], 4), nhieu=round(o['nhieu'], 4), cham_nen=round(ndot[hs].mean(), 3)))
                if cfg['name'] in ('goc', 'K5_m1_T120'):
                    sm = mask[ds.sbar]; ex = np.nonzero(res.exc & sm)[0]
                    nd = near_dot(ds, res, ex, ds.w)
                    # (nến, bên) có vượt nhưng KHÔNG có chấm nào
                    kb = ds.key[ex]; kd = ds.key[np.nonzero(res.dot & sm)[0]]
                    ub = np.unique(kb); nod = ~np.isin(ub, kd)
                    t20 = tops[doan][0]; t20x = t20[res.exc[t20]]
                    tie.append(dict(cfg=cfg['name'], ma=sym, m=m, doan=doan, vuot=len(ex), vuot_khong_cham_gan=int((~nd).sum()), ti_le=round((~nd).mean(), 4),
                                    nen_ben_co_vuot=len(ub), nen_ben_khong_cham=int(nod.sum()), top20_vuot=len(t20x), top20_vuot_khong_cham_gan=int((~near_dot(ds, res, t20x, ds.w)).sum())))
                if cfg['name'] == 'K5_m1_T120' and sym == 'NQ' and m == 15 and doan == 'chon':
                    idx = tops[doan][1]; hit = res.exc[idx] | near_dot(ds, res, idx, ds.w)
                    df = pd.DataFrame(dict(day=ds.tday.values[ds.sbar[idx]], ses=ds.ses[ds.sbar[idx]], hit=hit, v=ds.sval[idx], thr=res.thr[ds.sbar[idx]]))
                    g = df.groupby(['day', 'ses']).agg(sot=('hit', lambda x: int((~x).sum())), vmax=('v', 'max'), vmin=('v', 'min'), thr_med=('thr', 'median')).reset_index()
                    # volume phiên so với trung vị 5 lần trước của cùng phiên
                    sv = pd.DataFrame(dict(day=ds.tday.values, ses=ds.ses, tot=ds.tot)).groupby(['ses', 'day']).tot.sum().reset_index()
                    sv['rel'] = sv.groupby('ses').tot.transform(lambda x: x / x.shift(1).rolling(5, min_periods=1).median())
                    g = g.merge(sv[['day', 'ses', 'rel']], on=['day', 'ses'])
                    t5 = g
            L.forget(ds)
        if m in (1, 5, 15):
            day, _, _ = L.rule_day_slot(ds.t, m, 'ct'); ud = np.unique(day); keep = day >= ud[-8]; sub = ds.subset(keep)
            dmap = dict(zip(ds.t.values.astype('datetime64[m]').astype(np.int64), day))
            for K in (5, 10):
                for mind in (1, 2, 3):
                    for T in (120, 240):
                        cfg = mk('x', K=K, mind=mind, T=T)
                        A = keys(ds, L.eval_dot(ds, cfg), keep); B = keys(sub, L.eval_dot(sub, cfg))
                        per = {}
                        for x in A | B:
                            c = per.setdefault(dmap[x[0]], [0, 0]); c[1] += 1; c[0] += (x in A and x in B)
                        short.append(dict(ma=sym, m=m, K=K, mind=mind, T=T, chung=len(A & B), hop=len(A | B), theo_ngay=' '.join('%.2f' % (c[0] / c[1]) for _, c in sorted(per.items()))))
                        L.forget(sub)
        _cache.pop((sym, m), None); L.forget(ds)
        print(sym, m, 'xong %.0f s' % (time.time() - t0), flush=True)
R = pd.DataFrame(rows); R.to_csv('out_rv2_combo.csv', index=False)
S = pd.DataFrame(short); S.to_csv('out_rv2_short.csv', index=False)
T_ = pd.DataFrame(tie); T_.to_csv('out_rv2_tie.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500); pd.set_option('display.max_colwidth', 80)
print('\n== (a) tổng trượt 6 ô (M1,M5,M15) x 2 đoạn')
R6 = R[R.m.isin([1, 5, 15])]
print(R6.groupby('cfg').truot.sum())
print(R[R.truot > 0][['cfg', 'ma', 'm', 'doan', 'gi']].to_string(index=False))
print('\n== chấm/nến, khớp (đoạn kiểm)'); print(R[(R.doan == 'kiem')].pivot_table(index=['cfg'], columns=['ma', 'm'], values='cham_nen').to_string())
print(R[(R.cfg == 'K5_m1_T120')].to_string(index=False))
print('\n== (b) nạp 8 ngày: trùng gộp 6 ô'); g = S.groupby(['K', 'mind', 'T'])[['chung', 'hop']].sum(); g['trung'] = g.chung / g.hop; print(g.to_string())
print(S[(S.K == 5) & (S.T == 120)].to_string(index=False))
print('\n== (c) vượt mà không có chấm gần'); print(T_.to_string(index=False))
print('\n== (d) NQ M15 chọn: top5 phiên sót'); print(t5[t5.sot > 0].to_string(index=False)); print('số phiên', len(t5), 'tổng sót', t5.sot.sum())
