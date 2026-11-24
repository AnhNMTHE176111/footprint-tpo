"""Câu 1: sàn x bộ số x mã x khung x phiên x ("nổ ở mọi mức giá" tắt/bật): chấm/nến, tỉ lệ nến mà sàn quyết định (k x B < sàn),
tỉ lệ chấm bị sàn cắt (so với không sàn). Ghi out_floor_grid.csv. Chạy: python floor_grid.py"""
from floor_lib import *
rows = []
for sym in ('GC', 'NQ'):
    for m in TFS:
        F, S = load(sym, m)
        for pn in PRESETS:
            for al in (False, True):
                D, thr = cands(F, S, m, pn, al)
                idx = S.index[thr.notna()]; ses = ses_of(idx); kB = thr.reindex(idx).values
                n0 = len(apply_floor(D, 0))
                for f in FLOORS:
                    X = apply_floor(D, f); ps = per_session(X, idx)
                    r = dict(ma=sym, khung=f'M{m}', bo=pn, moi_muc_gia=int(al), san=f, A=round(ps['A'], 3), Au=round(ps['Au'], 3), My=round(ps['My'], 3), tat_ca=round(ps['all'], 3),
                             do=round((X.col == 'S').sum() / len(idx), 3), cat_pct=round(100 * (1 - len(X) / n0), 1),
                             san_qd_A=round(100 * (kB[ses == 'A'] < f).mean(), 0), san_qd_Au=round(100 * (kB[ses == 'Au'] < f).mean(), 0), san_qd_My=round(100 * (kB[ses == 'My'] < f).mean(), 0),
                             san_qd=round(100 * (kB < f).mean(), 0), kB_A=round(np.median(kB[ses == 'A']), 1), kB_Au=round(np.median(kB[ses == 'Au']), 1), kB_My=round(np.median(kB[ses == 'My']), 1),
                             cham_duoi_kB_pct=round(100 * (X.v < 0).mean(), 1), n=len(X), nen=len(idx))
                    rows.append(r)
                print(sym, m, pn, al, 'xong', flush=True)
R = pd.DataFrame(rows).drop(columns='cham_duoi_kB_pct'); R.to_csv('out_floor_grid.csv', index=False)
pd.set_option('display.width', 300); pd.set_option('display.max_rows', 2000)
for al in (0, 1):
    for pn in PRESETS:
        print(f'\n=== bộ {pn}, nổ ở mọi mức giá = {"BẬT" if al else "tắt"}: chấm/nến (tất cả phiên) theo sàn')
        P = R[(R.bo == pn) & (R.moi_muc_gia == al)].pivot_table(index=['ma', 'khung'], columns='san', values='tat_ca', sort=False); print(P.round(2).to_string())
        print(f'--- tỉ lệ nến mà sàn quyết định (k x B < sàn), %')
        P = R[(R.bo == pn) & (R.moi_muc_gia == al)].pivot_table(index=['ma', 'khung'], columns='san', values='san_qd', sort=False); print(P.round(0).to_string())
