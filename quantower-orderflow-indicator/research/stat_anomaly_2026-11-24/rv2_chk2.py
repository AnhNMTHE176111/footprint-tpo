"""Review vòng 2 (Fable): (1) vì sao có ô vượt ngưỡng mà cả (nến, bên) không có chấm nào — do bằng nhau hay do chuỗi che;
(2) thử chọn chấm kiểu tham lam (giá trị giảm dần, bằng nhau tick thấp trước, bỏ ô cách ô đã giữ <= w) xem số chấm tăng bao nhiêu;
(3) "5 ô lớn nhất phiên" NQ M15 đoạn chọn sót ở giờ nào."""
import numpy as np, pandas as pd
from sa_common import load_dot
from sa_oracle_lib import near_dot
import sa2_lib as L
cfg = dict(L.BASE); cfg.update(K=5, mind=2, name='K5_m2_T120', pa='thong_ke')
def greedy(ds, exc):
    keep = np.zeros(ds.ns, bool)
    ex = np.nonzero(exc)[0]
    key = ds.key[ex]
    st = np.r_[0, np.nonzero(np.diff(key))[0] + 1]; en = np.r_[st[1:], len(ex)]
    for a, b in zip(st, en):
        idx = ex[a:b]
        if b - a == 1: keep[idx[0]] = True; continue
        w = ds.w[ds.sbar[idx[0]]]
        o = sorted(range(b - a), key=lambda i: (-ds.sval[idx[i]], ds.stk[idx[i]]))
        kept = []
        for i in o:
            tk = ds.stk[idx[i]]
            if all(abs(tk - k) > w for k in kept): kept.append(tk); keep[idx[i]] = True
    return keep
class R2: pass
for sym, m in (('GC', 1), ('GC', 5), ('GC', 15), ('NQ', 1), ('NQ', 5), ('NQ', 15)):
    ds = load_dot(sym, m); res = L.eval_dot(ds, cfg)
    for doan in ('chon', 'kiem'):
        sm = ds.doan_mask(doan)[ds.sbar]
        ex = res.exc & sm; dot = res.dot & sm
        g = greedy(ds, ex)
        # (nến, bên) có vượt mà không chấm: giá trị lớn nhất có lặp lại không
        df = pd.DataFrame(dict(k=ds.key[ex], v=ds.sval[ex], d=res.dot[ex]))
        gg = df.groupby('k').agg(nd=('d', 'sum'), vmax=('v', 'max'), n=('v', 'size'))
        nod = gg[gg.nd == 0]
        vm = df.merge(nod[['vmax']], left_on='k', right_index=True)
        tied = (vm[vm.v == vm.vmax].groupby('k').size() >= 2).sum()
        t20, t5 = L.top_sets_f(ds, ds.doan_mask(doan))
        r2 = R2(); r2.dot = g
        def vis(idx, rr): return near_dot(ds, rr, idx, ds.w).mean()
        nb = ds.doan_mask(doan).sum()
        print(f'{sym} M{m} {doan}: vượt {ex.sum()}, chấm lớn-hơn-hẳn {dot.sum()} ({dot.sum()/nb:.3f}/nến), chấm tham lam {g.sum()} ({g.sum()/nb:.3f}/nến, +{(g.sum()/dot.sum()-1)*100:.1f}%); '
              f'(nến,bên) có vượt không chấm {len(nod)} trong {len(gg)}, trong đó do bằng nhau ở giá trị lớn nhất {tied}; '
              f'NHÌN THẤY top20 ngày: lớn-hơn-hẳn {vis(t20, res):.4f} / tham lam {vis(t20, r2):.4f}; top5 phiên {vis(t5, res):.4f} / {vis(t5, r2):.4f}; '
              f'chấm 1 nến lớn nhất {np.bincount(ds.sbar[dot]).max()} / {np.bincount(ds.sbar[g]).max()}', flush=True)
        if sym == 'NQ' and m == 15 and doan == 'chon':
            hit = res.exc[t5] | near_dot(ds, res, t5, ds.w)
            hh = pd.Series(ds.t[ds.sbar[t5[~hit]]].strftime('%H:%M')).value_counts().sort_index()
            print('   giờ UTC của ô top5 phiên bị sót:', dict(hh))
    L.forget(ds)
