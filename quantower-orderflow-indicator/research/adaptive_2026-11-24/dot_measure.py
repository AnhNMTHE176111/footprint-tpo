"""Câu B: mật độ chấm Bid/Ask theo mã x khung x phiên, luật HIỆN TẠI và các công thức chung.
Dùng pickle F_/S_{GC,NQ}_m{1,5,15,30,60}.pkl của ../nq_calib_2026-11-24 (footprint lịch sử 90 ngày, một hợp đồng, không có chỗ nối).
Chạy: python dot_measure.py [now|grid|final]"""
import sys, numpy as np, pandas as pd
from bt_common import ses_of, SES, SES_VN
from dot_rule import dots_fast, params_for

P = '../nq_calib_2026-11-24/'
TFS = (1, 5, 15, 30, 60)
pd.set_option('display.width', 250)
_c = {}


def load(sym, m):
    if (sym, m) not in _c:
        F = pd.read_pickle(f'{P}F_{sym}_m{m}.pkl'); S = pd.read_pickle(f'{P}S_{sym}_m{m}.pkl')
        _c[(sym, m)] = (F, S)
    return _c[(sym, m)]


# luật hiện tại trong C#
def current(sym, S):
    if sym == 'GC': return params_for(S, 2.8, 0, 4, hfix=6)
    return params_for(S, 3.5, 14, 8, hfix=12)


def measure(sym, m, prm):
    F, S = load(sym, m)
    thr, w, h, B, R = prm(S) if callable(prm) else params_for(S, **prm)
    ok = thr.notna()
    Dt = dots_fast(F, thr, w, h)
    per = Dt.groupby('t').size().reindex(S.index[ok], fill_value=0)
    red = Dt[Dt.col == 'S'].groupby('t').size().reindex(S.index[ok], fill_value=0)
    ses = ses_of(per.index)
    r = dict(ma=sym, khung=f'M{m}')
    for s in SES: r[SES_VN[s]] = round(per.values[ses == s].mean(), 2)
    r['tat_ca'] = round(per.mean(), 2); r['do'] = round(red.mean(), 2); r['xanh'] = round(per.mean() - red.mean(), 2)
    r['nen_co_cham'] = '/'.join(f'{(per.values[ses == s] > 0).mean():.2f}' for s in SES)
    r['p95'] = int(per.quantile(.95)); r['mx'] = int(per.max())
    r['w'] = '/'.join(f'{np.median(w[ok].values[ses == s]):.0f}' for s in SES)
    r['nguong'] = '/'.join(f'{np.median(thr[ok].values[ses == s]):.0f}' for s in SES)
    return r, Dt


def floor_bind(sym, m, k, floor=9):
    """Tỉ lệ nến mà sàn là điều kiện quyết định (k x B < sàn), theo phiên."""
    F, S = load(sym, m); B = S.B_med.dropna(); ses = ses_of(B.index)
    return '/'.join(f'{(k * B.values[ses == s] < floor).mean() * 100:.0f}%' for s in SES), '/'.join(f'{np.median(B.values[ses == s]):.1f}' for s in SES)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'now'
    if mode == 'now':
        rows = []
        for sym in ('GC', 'NQ'):
            for m in TFS:
                r, _ = measure(sym, m, lambda S, sym=sym: current(sym, S))
                fb, bm = floor_bind(sym, m, 2.8 if sym == 'GC' else 3.5)
                r['B_trung_vi'] = bm; r['san9_quyet_dinh'] = fb
                rows.append(r)
        print('--- luật HIỆN TẠI (GC: 2,8 / ±4 / che 6 / sàn 9; NQ: 3,5 / ±max(8, R/14) / che 12 / sàn 9): chấm/nến theo phiên Á/Âu/Mỹ')
        print(pd.DataFrame(rows).to_string(index=False))
    elif mode == 'grid':
        rows = []
        for k in (2.4, 2.8, 3.2, 3.5):
            for D, wmin in ((4, 4), (5, 4), (6, 4), (8, 4), (10, 4)):
                for hm in (1.0, 1.5):
                    for fl in (9, 5):
                        rr = dict(k=k, D=D, wmin=wmin, hmult=hm, san=fl)
                        for sym in ('GC', 'NQ'):
                            for m in TFS:
                                r, _ = measure(sym, m, dict(k=k, D=D, wmin=wmin, hmult=hm, floor=fl))
                                rr[f'{sym}{m}'] = r['tat_ca']
                        v = np.array([rr[f'{s}{m}'] for s in ('GC', 'NQ') for m in TFS])
                        rr['min'] = v.min(); rr['max'] = v.max(); rr['max/min'] = round(v.max() / v.min(), 2)
                        rows.append(rr); print(rr, flush=True)
        pd.DataFrame(rows).to_csv('out_dot_grid.csv', index=False)
