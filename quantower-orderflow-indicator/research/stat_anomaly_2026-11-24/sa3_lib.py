"""Vòng 3 "Không theo CORVEN" — thư viện (r2_review.md mục 6.1). Dựa trên sa2_lib.py, CHỈ nhìn quá khứ, không dùng giá.

Khác vòng 2:
  - Tham số cách chọn chấm `sel`:
      lmax = như vòng 2 (ô vượt ngưỡng và lớn hơn hẳn mọi tick khác cùng bên trong ±w),
      nms  = chọn tham lam (đúng CellBigLogic.MergeAdjacent): với từng (nến, bên), các ô vượt ngưỡng sắp giá trị giảm dần,
             bằng nhau thì tick thấp trước; giữ ô nếu chưa có ô đã giữ nào cách nó <= w tick,
      all  = mọi ô vượt ngưỡng ("Nổ ở mọi mức giá").
  - Khung lân cận = tập {khung - 1, khung + 1} quay vòng, bỏ khung trùng nhau và trùng khung chính (chỉ khác khi một ngày có dưới 3 khung).
  - Cấu hình NỀN MỚI: giờ Chicago, K = 5, có lân cận, tối thiểu 2 ngày, T = 120, p = 2%, sel = nms.
  - Thước "nhìn thấy": ô được tính khi cùng nến, cùng bên có CHẤM (sau bước chọn) cách <= w tick; không tính vượt ngưỡng thô.
(Bản nhanh không có nến rỗng: bảng nến chỉ gồm nến có ô volume > 0, đúng điều "nến rỗng bỏ hẳn" của bản chuẩn.)"""
import os, sys, numpy as np, pandas as pd
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sa2_lib as L2  # noqa: E402
from sa2_lib import SCR, rule_day_slot, K_p, fallback_threshold, Res, ct_offset_hours  # noqa: E402,F401
import sa_dot_rules as R1  # noqa: E402
from sa_oracle_lib import near_dot  # noqa: E402

NEW = dict(tz='ct', K=5, lc=1, mind=2, T=120, pbp=200, sel='nms')
VARIANTS = [('nen_moi', {}), ('sel_lmax', dict(sel='lmax')), ('khong_lan_can', dict(lc=0)), ('p1', dict(pbp=100)), ('p0.5', dict(pbp=50)),
            ('toi_thieu_1_ngay', dict(mind=1))]


def cfg_new(name='nen_moi', **ch):
    c = dict(NEW); c.update(ch); c['name'] = name; c['pa'] = 'thong_ke'; return c


def dot_configs():
    C = [cfg_new(nm, **ch) for nm, ch in VARIANTS]
    C += [dict(R1.BASELINES[0]), dict(R1.BASELINES[1])]
    return C


def neighbors(s, nsl, lc):
    """Danh sách khung dùng: khung chính trước, rồi lân cận {s-1, s+1} quay vòng, bỏ trùng nhau và trùng khung chính."""
    out = [s]
    if lc:
        for ss in ((s - 1) % nsl, (s + 1) % nsl):
            if ss not in out: out.append(ss)
    return out


_memo = {}


def main_threshold(ds, tz, K, lc, mind, pbp):
    """Như sa2_lib.main_threshold nhưng khung lân cận bỏ trùng (neighbors)."""
    k = (ds.uid, 'main3', tz, K, lc, mind, pbp)
    if k in _memo: return _memo[k]
    G = L2._groups(ds, tz)
    ng = len(G['st']); V = G['V']; nsl = G['nsl']
    gday, gslot, H = G['gday'], G['gslot'], G['H']
    per = {}
    for s in np.unique(gslot):
        idx = np.nonzero(gslot == s)[0]
        C = np.zeros((len(idx) + 1, V), np.int64); np.cumsum(H[idx], 0, out=C[1:])
        per[int(s)] = (idx, gday[idx], C)
    thr = np.full(ng, -1, np.int64); gt = np.zeros(ng, np.int64); nsamp = np.zeros(ng, np.int64); ncen = np.zeros(ng, np.int64)
    for g in range(ng):
        d, s = int(gday[g]), int(gslot[g])
        h = np.zeros(V, np.int64)
        for j, ss in enumerate(neighbors(s, nsl, lc)):
            if ss not in per: continue
            idx, dd, C = per[ss]
            pos = int(np.searchsorted(dd, d, 'left'))
            a = max(0, pos - K)
            if j == 0: ncen[g] = pos - a
            h += C[pos] - C[a]
        if ncen[g] < mind: continue
        n = int(h.sum()); nsamp[g] = n
        KK = int(K_p(n, pbp))
        if KK < 0 or n < KK + 1: continue
        suf = np.cumsum(h[::-1])[::-1]
        t = int((suf >= KK + 1).sum()) - 1
        thr[g] = t; gt[g] = int(suf[t + 1]) if t + 1 < V else 0
    gid = G['gid']
    out = (thr[gid], gt[gid], nsamp[gid], ncen[gid])
    _memo[k] = out
    return out


@njit(cache=True)
def nb_nms(key, tk, vals, wseg, exc):
    """Chọn tham lam trong từng đoạn key (nến*2 + bên; trong đoạn tk tăng dần): ô vượt (exc) sắp giá trị giảm dần,
    bằng nhau tick thấp trước (tk tăng dần trong đoạn + sắp ổn định); giữ nếu không có ô đã giữ nào cách <= w tick."""
    n = len(vals); keep = np.zeros(n, np.bool_)
    i = 0
    while i < n:
        j = i
        while j < n and key[j] == key[i]: j += 1
        cnt = 0
        for q in range(i, j):
            if exc[q]: cnt += 1
        if cnt > 0:
            idx = np.empty(cnt, np.int64); c = 0
            for q in range(i, j):
                if exc[q]:
                    idx[c] = q; c += 1
            o = np.argsort(-vals[idx], kind='mergesort')
            kept = np.empty(cnt, np.int64); nk = 0
            w = wseg[i]
            for q in range(cnt):
                s = idx[o[q]]; ok = True
                for r in range(nk):
                    if abs(tk[s] - tk[kept[r]]) <= w:
                        ok = False; break
                if ok:
                    kept[nk] = s; nk += 1; keep[s] = True
        i = j
    return keep


def select(ds, exc, sel):
    if sel == 'lmax': return exc & ds.lmax
    if sel == 'all': return exc.copy()
    if sel == 'nms': return nb_nms(ds.key, ds.stk, ds.sval, ds.w[ds.sbar], exc)
    raise ValueError(sel)


def eval_dot(ds, cfg):
    if cfg['pa'] != 'thong_ke':
        r = R1.evaluate(ds, cfg)
        return Res(ds, cfg, r.has, r.thr, r.nom, r.exc, r.dot, None, r.kind, r.nom_decl)
    tm, gm, nm, _ = main_threshold(ds, cfg['tz'], cfg['K'], cfg['lc'], cfg['mind'], cfg['pbp'])
    tf, gf, nf = fallback_threshold(ds, cfg['T'], cfg['pbp'])
    src = np.where(tm >= 0, 1, np.where(tf >= 0, 2, 0)).astype(np.int8)
    thr = np.where(src == 1, tm, np.where(src == 2, tf, -1))
    has = src > 0
    g = np.where(src == 1, gm, gf); n = np.where(src == 1, nm, nf)
    nom = np.where(has, g / np.maximum(n, 1), np.nan)
    exc = (ds.sval > np.where(has, thr, np.iinfo(np.int64).max)[ds.sbar]) & has[ds.sbar]
    dot = select(ds, exc, cfg.get('sel', 'lmax'))
    return Res(ds, cfg, has, np.where(has, thr, np.nan).astype(float), nom, exc, dot, src, 'p', cfg['pbp'] / 10000.0)


def forget(ds):
    for k in [k for k in _memo if k[0] == ds.uid]:
        del _memo[k]
    L2.forget(ds)


def oracle3(ds, res, Rr, mask_bars, wbar, tops):
    """oracle2 (số cũ: vượt thô hoặc gần chấm) + số "nhìn thấy" (chỉ gần chấm, cùng nến, cùng bên, cách <= w)."""
    o = L2.oracle2(ds, res, Rr, mask_bars, wbar, tops)
    ge_s, n_s, ge_a, n_a = Rr
    sm = mask_bars[ds.sbar]
    p = o['p_hat']
    strict_s = ge_s <= np.floor(p / 2 * n_s); strict_a = ge_a <= np.floor(p / 2 * n_a)
    t20, t5 = tops
    groups = {'top20': t20, 'top5': t5, 'cuc_tri': np.nonzero(sm & strict_s & strict_a)[0]}
    for g, idx in groups.items():
        if len(idx) == 0:
            o[f'{g}_nt'] = np.nan; o[f'{g}_nt_sot'] = 0; continue
        vis = near_dot(ds, res, idx, wbar)
        o[f'{g}_nt'] = vis.mean(); o[f'{g}_nt_sot'] = int((~vis).sum())
        o[f'{g}_nt_sot_vuot'] = int((~vis & res.exc[idx]).sum())      # vượt ngưỡng nhưng không có chấm gần
    o['_t5_vis'] = near_dot(ds, res, t5, wbar) if len(t5) else np.zeros(0, bool)
    return o


if __name__ == '__main__':
    # tự kiểm nhỏ: neighbors + nms tính tay
    assert neighbors(5, 48, 1) == [5, 4, 6] and neighbors(0, 48, 1) == [0, 47, 1]
    assert neighbors(0, 2, 1) == [0, 1] and neighbors(1, 2, 1) == [1, 0] and neighbors(0, 1, 1) == [0] and neighbors(3, 48, 0) == [3]
    key = np.zeros(2, np.int64); tk = np.array([10, 11]); v = np.array([12, 12]); w = np.array([4, 4]); e = np.ones(2, bool)
    assert list(nb_nms(key, tk, v, w, e)) == [True, False]
    key = np.zeros(3, np.int64); tk = np.array([0, 3, 6]); v = np.array([20, 15, 12]); w = np.array([4, 4, 4]); e = np.ones(3, bool)
    assert list(nb_nms(key, tk, v, w, e)) == [True, False, True]
    print('sa3_lib tự kiểm: ĐẠT')
