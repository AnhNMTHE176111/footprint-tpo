"""Năm phương án chấm Bid/Ask "Không theo CORVEN" + hai mốc đối chứng (PLAN.md mục 2).

Mỗi phương án có:
  - BẢN CHUẨN từng nến (ref_*): vòng lặp thẳng theo thời gian, mảng đếm 0..4095 + hàng đợi nến (đúng cấu trúc C# sẽ dùng);
  - BẢN NHANH (evaluate): numpy/numba trên cả bảng, phải ra y hệt bản chuẩn (sa_dot_selftest.py).
Quy ước (PLAN mục 1): mẫu = giá trị bên > 0, gộp Bid + Ask; tập tham chiếu chỉ gồm nến đã đóng trước;
ngưỡng = giá trị lớn thứ K+1 (sắp giảm dần), ô vượt khi LỚN HƠN HẲN ngưỡng.
  kiểu p (tính bằng phần vạn để khỏi lỗi số thực): K = floor(p x số mẫu), cần số mẫu x p >= 5;
  kiểu λ (tính bằng phần tư): K = floor(λ x số nến tham chiếu), cần >= 5 nến và K >= 1;
  cần thêm số mẫu >= K + 1, nếu không thì "chưa có ngưỡng".
Chấm sau gộp = vượt thô và lớn hơn hẳn cùng bên trong ±w tick cùng nến. Không che, không sàn.

Các chỗ PLAN chưa nói rõ, đã chọn (ghi trong R1-KET-QUA.md):
  - cung_gio: "cần ít nhất 3 lần xuất hiện" tính trên khung giờ CHÍNH (không tính hai khung lân cận);
    lân cận ±1 quay vòng qua nửa đêm UTC (khung 0 và khung cuối là lân cận).
  - lai cùng giờ: không có biến thể lân cận (PLAN không liệt kê). lai cuốn 1.380 phút: n = floor(1380/phút + 0,5) nến.
  - z_log: cửa sổ n = max(5, floor(T/phút + 0,5)) nến như cuon, cần >= 5 nến và d > 0.
  - ky_luc cuốn: n = max(8, floor(T/phút + 0,5)); cần đủ 8 nến; r tính theo số nến thật có (<= n).
  - ky_luc cùng giờ: không lân cận, cần >= 3 lần xuất hiện; n = số nến trong các lần xuất hiện đó.
"""
import numpy as np, pandas as pd
from collections import defaultdict
from sa_common import (CAP, rhu, nb_window_kth, nb_window_median_mad, kth1_counts, kth1_float, nbase)
from numba import njit

P_LEVELS = [('p', 200), ('p', 100), ('p', 50), ('p', 20)]        # phần vạn: 2% 1% 0,5% 0,2%
L_LEVELS = [('lam', 1), ('lam', 2), ('lam', 4), ('lam', 8)]       # phần tư: 0,25 0,5 1 2
LEVELS = P_LEVELS + L_LEVELS
FAM_LEVELS = LEVELS + [('p', 10)]                                 # + 0,1% (chỉ Big Trade dùng); họ ngưỡng tính cho mọi mức này
Z_NOM = {2.5: 0.0062, 3.0: 0.00135, 3.5: 0.00023}


def lvl_name(kind, x):
    return f'p{x / 100:g}' if kind == 'p' else f'lam{x / 4:g}'


def lvl_nominal(kind, x):
    return x / 10000.0 if kind == 'p' else x / 4.0


def all_configs():
    C = []
    for T in (60, 120, 240, 480):
        for k, x in LEVELS:
            C.append(dict(pa='cuon', T=T, lk=k, lx=x, name=f'cuon_T{T}_{lvl_name(k, x)}'))
    for K in (5, 10, 20):
        for lc in (0, 1):
            for k, x in LEVELS:
                C.append(dict(pa='cung_gio', K=K, lc=lc, lk=k, lx=x, name=f'cung_gio_K{K}{"_lc" if lc else ""}_{lvl_name(k, x)}'))
    for L in ('med', 'mean'):
        for ref in (5, 10, 20, 'r1380'):
            for k, x in LEVELS:
                C.append(dict(pa='lai', L=L, ref=ref, lk=k, lx=x, name=f'lai_{L}_{"K" + str(ref) if ref != "r1380" else "cuon1380"}_{lvl_name(k, x)}'))
    for T in (120, 240):
        for z in (2.5, 3.0, 3.5):
            C.append(dict(pa='z_log', T=T, z0=z, name=f'z_log_T{T}_z{z:g}'))
    for ref in (('T', 120), ('T', 240), ('T', 480), ('K', 10), ('K', 20)):
        for q in (0.5, 0.25, 0.1):
            C.append(dict(pa='ky_luc', rk=ref[0], rv=ref[1], q=q, name=f'ky_luc_{ref[0]}{ref[1]}_q{q:g}'))
    C += BASELINES
    return C


BASELINES = [dict(pa='dc_dang_chay', preset='khong_sot', floor=9, name='dc_dang_chay_khong_sot'),
             dict(pa='dc_dang_chay', preset='it_nhieu', floor=9, name='dc_dang_chay_it_nhieu'),
             dict(pa='dc_pct', x=5, name='dc_pct5'), dict(pa='dc_pct', x=10, name='dc_pct10'), dict(pa='dc_pct', x=15, name='dc_pct15')]
PRESET = {'khong_sot': (2.0, 0.0, 2), 'it_nhieu': (2.8, 0.75, 6)}


def kind_of(cfg):
    if cfg['pa'] in ('cuon', 'cung_gio', 'lai'): return cfg['lk']
    return {'z_log': 'z', 'ky_luc': 'rec'}.get(cfg['pa'], 'base')


def K_of(kind, x, nsamp, nbars):
    """K hoặc -1 nếu chưa đủ tập tham chiếu (trước điều kiện số mẫu >= K+1)."""
    if kind == 'p':
        return (x * nsamp) // 10000 if nsamp * x >= 50000 else -1
    K = (x * nbars) // 4
    return K if (nbars >= 5 and K >= 1) else -1


def K_vec(kind, x, nsamp, nbars):
    nsamp = np.asarray(nsamp, np.int64); nbars = np.asarray(nbars, np.int64)
    if kind == 'p':
        return np.where(nsamp * x >= 50000, (x * nsamp) // 10000, -1)
    K = (x * nbars) // 4
    return np.where((nbars >= 5) & (K >= 1), K, -1)


class Res:
    """Kết quả một cấu hình trên một DotData: has (nến có ngưỡng), thr (ngưỡng hiển thị theo volume), nom (mức danh nghĩa đạt được theo nến),
    exc (mẫu vượt thô), kind, nom_decl (mức danh nghĩa khai báo), dot (mẫu là chấm sau gộp)."""

    def __init__(self, ds, cfg, has, thr, nom, exc, extra_dot_mask=None):
        self.cfg = cfg; self.kind = kind_of(cfg)
        self.has = np.asarray(has, bool); self.thr = np.asarray(thr, float); self.nom = np.asarray(nom, float)
        exc = np.asarray(exc, bool) & self.has[ds.sbar]
        self.exc = exc
        dot = exc & ds.lmax
        if extra_dot_mask is not None: dot &= extra_dot_mask
        self.dot = dot
        self.nom_decl = (lvl_nominal(cfg['lk'], cfg['lx']) if self.kind in ('p', 'lam') else Z_NOM.get(cfg.get('z0'), np.nan) if self.kind == 'z' else np.nan)


# =====================================================================================
#                                    BẢN NHANH
# =====================================================================================
_memo = {}


def _mkey(ds, *a):
    return (ds.uid,) + a


def _cuon_family(ds, T):
    """Ngưỡng cho cả 8 mức của cửa sổ T: thr[nb, 8], gt[nb, 8], nsamp, nbars."""
    k = _mkey(ds, 'cuon', T)
    if k in _memo: return _memo[k]
    n = max(5, rhu(T / ds.m))
    b = np.arange(ds.nb); lo = np.maximum(0, b - n); hi = b
    cs = np.r_[0, np.cumsum(ds.npos)]
    nsamp = cs[hi] - cs[lo]; nbars = hi - lo
    Km = np.stack([K_vec(kd, x, nsamp, nbars) for kd, x in FAM_LEVELS], 1).astype(np.int64)
    thr, gt = nb_window_kth(ds.sval, ds.s0, ds.s1, lo.astype(np.int64), hi.astype(np.int64), Km, CAP)
    _memo[k] = (thr, gt, nsamp, nbars)
    return _memo[k]


def _occ_index(ds, values_per_bar_slot=None):
    """Các lần xuất hiện (ngày giao dịch, khung giờ): nhóm nến liền nhau. Trả dict theo khung: list (chỉ số ngày, nến đầu, nến cuối+1)."""
    k = _mkey(ds, 'occ')
    if k in _memo: return _memo[k]
    gkey = ds.dayi.astype(np.int64) * 1000 + ds.slot
    starts = np.r_[0, np.nonzero(np.diff(gkey))[0] + 1]; ends = np.r_[starts[1:], ds.nb]
    occ = defaultdict(list)
    gid = np.zeros(ds.nb, np.int64)
    for g, (a, e) in enumerate(zip(starts, ends)):
        occ[int(ds.slot[a])].append((int(ds.dayi[a]), a, e))
        gid[a:e] = g
    G = pd.DataFrame(dict(a=starts, e=ends, day=ds.dayi[starts], slot=ds.slot[starts]))
    _memo[k] = (occ, G, gid)
    return _memo[k]


def _occ_refs(ds, K, lc):
    """Với mỗi nhóm (ngày, khung giờ) g: danh sách các lần xuất hiện tham chiếu (nến đầu, nến cuối+1) và số lần của khung chính."""
    k = _mkey(ds, 'occref', K, lc)
    if k in _memo: return _memo[k]
    occ, G, gid = _occ_index(ds)
    days_of = {s: np.array([o[0] for o in L], np.int64) for s, L in occ.items()}
    refs = []; ncen = np.zeros(len(G), np.int64)
    for g in range(len(G)):
        d, s = int(G.day[g]), int(G.slot[g])
        rr = []
        for j, ss in enumerate([s] + ([(s - 1) % ds.nslot, (s + 1) % ds.nslot] if lc else [])):
            if ss not in occ: continue
            pos = int(np.searchsorted(days_of[ss], d, 'left'))       # số lần xuất hiện trước hôm nay
            sel = occ[ss][max(0, pos - K):pos]
            if j == 0: ncen[g] = len(sel)
            rr += [(a, e) for _, a, e in sel]
        refs.append(rr)
    _memo[k] = (refs, ncen)
    return _memo[k]


def _hist_of_bars(vals, s0, s1, a, e):
    x = vals[s0[a]:s1[e - 1]] if e > a else np.zeros(0, np.int64)
    return np.bincount(np.minimum(x, CAP), minlength=CAP + 1)


def _cung_gio_family(ds, K, lc):
    k = _mkey(ds, 'cg', K, lc)
    if k in _memo: return _memo[k]
    refs, ncen = _occ_refs(ds, K, lc)
    occ, G, gid = _occ_index(ds)
    ng = len(G)
    # mảng đếm của từng nhóm, rồi cộng theo danh sách tham chiếu
    H = np.zeros((ng, CAP + 1), np.int32)
    for g in range(ng):
        H[g] = _hist_of_bars(ds.sval, ds.s0, ds.s1, int(G.a[g]), int(G.e[g]))
    nb_g = (G.e - G.a).values
    thr = np.full((ng, len(FAM_LEVELS)), -1.0); gt = np.zeros((ng, len(FAM_LEVELS)), np.int64)
    nsamp = np.zeros(ng, np.int64); nbars = np.zeros(ng, np.int64)
    gstart = {}
    for g in range(len(G)): gstart[int(G.a[g])] = g
    for g in range(ng):
        if ncen[g] < 3: continue
        ids = [gstart[a] for a, e in refs[g]]
        h = H[ids].sum(0, dtype=np.int64)
        tot = int(h.sum()); nbars[g] = int(nb_g[ids].sum()); nsamp[g] = tot
        suf = np.cumsum(h[::-1])[::-1]                      # suf[v] = số mẫu >= v
        for j, (kd, x) in enumerate(FAM_LEVELS):
            KK = K_of(kd, x, tot, nbars[g])
            if KK < 0 or tot < KK + 1: continue
            t = int((suf >= KK + 1).sum()) - 1
            thr[g, j] = t; gt[g, j] = int(suf[t + 1]) if t + 1 <= CAP else 0
    out = (thr[gid], gt[gid], nsamp[gid], nbars[gid])
    _memo[k] = out
    return out


def _L_of(ds, L):
    return ds.Bmed if L == 'med' else ds.Bmean


@njit(cache=True)
def _bit_add(tree, i, d):
    n = len(tree) - 1; i += 1
    while i <= n:
        tree[i] += d; i += i & (-i)


@njit(cache=True)
def _bit_kth(tree, k, LOG):
    """vị trí (0-based) của phần tử nhỏ thứ k (1-based)."""
    pos = 0; n = len(tree) - 1; step = LOG
    while step > 0:
        if pos + step <= n and tree[pos + step] < k:
            pos += step; k -= tree[pos]
        step >>= 1
    return pos


@njit(cache=True)
def _bit_prefix(tree, i):
    s = 0; i += 1
    while i > 0:
        s += tree[i]; i -= i & (-i)
    return s


@njit(cache=True)
def _nb_ratio_window(rank, s0, s1, ok_bar, lo, hi, Kmat, usorted):
    """Cửa sổ trượt trên tỉ số (số thực) bằng cây Fenwick trên thứ hạng toàn cục.
    Chỉ mẫu của nến ok_bar (đã có mặt bằng) được nộp. Trả thr[b, j] (NaN nếu thiếu), gt[b, j], tot[b], nbok[b] (số nến đã nộp trong cửa sổ)."""
    nb, nj = Kmat.shape
    n = len(usorted)
    tree = np.zeros(n + 1, np.int64)
    LOG = 1
    while LOG * 2 <= n: LOG *= 2
    thr = np.full((nb, nj), np.nan); gt = np.zeros((nb, nj), np.int64)
    cl = 0; ch = 0; tot = 0
    for b in range(nb):
        while ch < hi[b]:
            if ok_bar[ch]:
                for i in range(s0[ch], s1[ch]):
                    _bit_add(tree, rank[i], 1)
                tot += s1[ch] - s0[ch]
            ch += 1
        while cl < lo[b]:
            if ok_bar[cl]:
                for i in range(s0[cl], s1[cl]):
                    _bit_add(tree, rank[i], -1)
                tot -= s1[cl] - s0[cl]
            cl += 1
        for j in range(nj):
            K = Kmat[b, j]
            if K < 0 or tot < K + 1: continue
            p = _bit_kth(tree, tot - K, LOG)
            t = usorted[p]
            # số phần tử <= t: vị trí cuối có giá trị == t
            lo2 = p; hi2 = n - 1
            while lo2 < hi2:
                md = (lo2 + hi2 + 1) // 2
                if usorted[md] <= t: lo2 = md
                else: hi2 = md - 1
            le = _bit_prefix(tree, lo2)
            thr[b, j] = t; gt[b, j] = tot - le
    return thr, gt


def _ratios(ds, L):
    k = _mkey(ds, 'ratio', L)
    if k in _memo: return _memo[k]
    Lb = _L_of(ds, L)
    okb = np.isfinite(Lb) & (Lb > 0)
    u = np.full(ds.ns, np.nan)
    sm = okb[ds.sbar]
    u[sm] = ds.sval[sm] / Lb[ds.sbar[sm]]
    _memo[k] = (u, okb)
    return _memo[k]


def _lai_family(ds, L, ref):
    k = _mkey(ds, 'lai', L, ref)
    if k in _memo: return _memo[k]
    u, okb = _ratios(ds, L)
    npos_ok = np.where(okb, ds.npos, 0)
    if ref == 'r1380':
        n = rhu(1380 / ds.m)
        b = np.arange(ds.nb); lo = np.maximum(0, b - n); hi = b
        cs = np.r_[0, np.cumsum(npos_ok)]; cb = np.r_[0, np.cumsum(okb.astype(np.int64))]
        nsamp = cs[hi] - cs[lo]; nbars = cb[hi] - cb[lo]
        Km = np.stack([K_vec(kd, x, nsamp, nbars) for kd, x in FAM_LEVELS], 1).astype(np.int64)
        uu = np.where(np.isfinite(u), u, np.inf)
        order = np.argsort(uu, kind='stable')
        rank = np.empty(ds.ns, np.int64); rank[order] = np.arange(ds.ns)
        usorted = uu[order]
        thr, gt = _nb_ratio_window(rank, ds.s0, ds.s1, okb, lo.astype(np.int64), hi.astype(np.int64), Km, usorted)
        out = (thr, gt, nsamp, nbars)
    else:
        refs, ncen = _occ_refs(ds, ref, 0)
        occ, G, gid = _occ_index(ds)
        ng = len(G)
        thr = np.full((ng, len(FAM_LEVELS)), np.nan); gt = np.zeros((ng, len(FAM_LEVELS)), np.int64)
        nsamp = np.zeros(ng, np.int64); nbars = np.zeros(ng, np.int64)
        for g in range(ng):
            if ncen[g] < 3: continue
            parts = []; nbk = 0
            for a, e in refs[g]:
                for bb in range(a, e):
                    if okb[bb]:
                        parts.append(u[ds.s0[bb]:ds.s1[bb]]); nbk += 1
            x = np.concatenate(parts) if parts else np.zeros(0)
            tot = len(x); nsamp[g] = tot; nbars[g] = nbk
            if tot == 0: continue
            xs = np.sort(x)[::-1]
            for j, (kd, xx) in enumerate(FAM_LEVELS):
                KK = K_of(kd, xx, tot, nbk)
                if KK < 0 or tot < KK + 1: continue
                t = xs[KK]; thr[g, j] = t; gt[g, j] = int(np.searchsorted(-xs, -t, 'left'))
        out = (thr[gid], gt[gid], nsamp[gid], nbars[gid])
    _memo[k] = out
    return out


def _zlog_family(ds, T):
    k = _mkey(ds, 'z', T)
    if k in _memo: return _memo[k]
    n = max(5, rhu(T / ds.m))
    b = np.arange(ds.nb); lo = np.maximum(0, b - n); hi = b
    M, D, NN = nb_window_median_mad(ds.sval, ds.s0, ds.s1, lo.astype(np.int64), hi.astype(np.int64), CAP)
    nbars = hi - lo
    _memo[k] = (M, D, NN, nbars, lo, hi)
    return _memo[k]


@njit(cache=True)
def _nb_count_ge_window(vals, s0, s1, lo, hi, vstar, cap):
    """Số mẫu trong cửa sổ có giá trị >= vstar[b] (vstar < 0: bỏ qua)."""
    nb = len(lo); hist = np.zeros(cap + 1, np.int64); out = np.zeros(nb, np.int64)
    cl = 0; ch = 0
    for b in range(nb):
        while ch < hi[b]:
            for i in range(s0[ch], s1[ch]): hist[min(vals[i], cap)] += 1
            ch += 1
        while cl < lo[b]:
            for i in range(s0[cl], s1[cl]): hist[min(vals[i], cap)] -= 1
            cl += 1
        if vstar[b] < 0: continue
        c = 0
        for v in range(vstar[b], cap + 1): c += hist[v]
        out[b] = c
    return out


def zlog_pass(v, m, d, z0):
    return (np.log(v) - m) / (1.4826 * d) >= z0


def _kyluc_family(ds, rk, rv):
    k = _mkey(ds, 'ky', rk, rv)
    if k in _memo: return _memo[k]
    one = np.arange(ds.nb + 1, dtype=np.int64)
    if rk == 'T':
        n = max(8, rhu(rv / ds.m))
        b = np.arange(ds.nb); lo = np.maximum(0, b - n); hi = b
        nbars = hi - lo
        out = ('T', lo, hi, nbars)
    else:
        refs, ncen = _occ_refs(ds, rv, 0)
        occ, G, gid = _occ_index(ds)
        out = ('K', refs, ncen, gid)
    _memo[k] = out
    return out


def kyluc_r(q, n):
    return np.maximum(1, np.floor(q * (np.asarray(n) + 1) + 0.5)).astype(np.int64)


def evaluate(ds, cfg):
    pa = cfg['pa']
    if pa in ('cuon', 'cung_gio'):
        thr, gt, nsamp, nbars = _cuon_family(ds, cfg['T']) if pa == 'cuon' else _cung_gio_family(ds, cfg['K'], cfg['lc'])
        j = FAM_LEVELS.index((cfg['lk'], cfg['lx']))
        t = thr[:, j]; has = t >= 0
        den = nsamp if cfg['lk'] == 'p' else nbars
        nom = np.where(has, gt[:, j] / np.maximum(den, 1), np.nan)
        exc = ds.sval > np.where(has, t, np.inf)[ds.sbar]
        return Res(ds, cfg, has, np.where(has, t, np.nan), nom, exc)
    if pa == 'lai':
        thr, gt, nsamp, nbars = _lai_family(ds, cfg['L'], cfg['ref'])
        j = FAM_LEVELS.index((cfg['lk'], cfg['lx']))
        t = thr[:, j]; u, okb = _ratios(ds, cfg['L'])
        has = np.isfinite(t) & okb
        den = nsamp if cfg['lk'] == 'p' else nbars
        nom = np.where(has, gt[:, j] / np.maximum(den, 1), np.nan)
        tt = np.where(has, t, np.inf)[ds.sbar]
        exc = np.where(np.isfinite(u), u, -np.inf) > tt
        Lb = _L_of(ds, cfg['L'])
        return Res(ds, cfg, has, np.where(has, t * Lb, np.nan), nom, exc)
    if pa == 'z_log':
        M, D, NN, nbars, lo, hi = _zlog_family(ds, cfg['T'])
        has = (nbars >= 5) & np.isfinite(D) & (D > 0)
        z0 = cfg['z0']
        thrv = np.where(has, np.exp(M + z0 * 1.4826 * np.where(has, D, 1)), np.nan)
        mm = np.where(has, M, 0)[ds.sbar]; dd = np.where(has, D, 1)[ds.sbar]
        exc = zlog_pass(ds.sval.astype(float), mm, dd, z0)
        # v* = số nguyên nhỏ nhất đạt z >= z0 (để đo mức danh nghĩa đạt được trên tập tham chiếu)
        vstar = np.full(ds.nb, -1, np.int64)
        c = np.where(has, np.ceil(np.minimum(thrv, CAP + 1) - 1e-9), -1).astype(np.int64)
        vs = np.clip(c, 1, CAP + 1)
        # chỉnh ±1 cho đúng công thức
        okm = has.copy()
        ok_prev = zlog_pass(np.maximum(vs - 1, 1).astype(float), np.where(has, M, 0), np.where(has, D, 1), z0) & (vs - 1 >= 1)
        vs = np.where(okm & ok_prev, vs - 1, vs)
        ok_now = zlog_pass(vs.astype(float), np.where(has, M, 0), np.where(has, D, 1), z0)
        vs = np.where(okm & ~ok_now, vs + 1, vs)
        vstar = np.where(has & (vs <= CAP), vs, -1).astype(np.int64)
        cge = _nb_count_ge_window(ds.sval, ds.s0, ds.s1, lo.astype(np.int64), hi.astype(np.int64), vstar, CAP)
        nom = np.where(has, cge / np.maximum(NN, 1), np.nan)
        return Res(ds, cfg, has, thrv, nom, exc)
    if pa == 'ky_luc':
        fam = _kyluc_family(ds, cfg['rk'], cfg['rv'])
        q = cfg['q']
        if fam[0] == 'T':
            # chỉ nến có ít nhất một giá trị bên > 0 mới nộp (nến rỗng không nộp số 0)
            n = max(8, rhu(cfg['rv'] / ds.m))
            valid = ds.bmax > 0; vv = ds.bmax[valid].astype(np.int64)
            cv = np.r_[0, np.cumsum(valid)][:-1]
            lo = np.maximum(0, cv - n); hi = cv; nbars = hi - lo
            r = kyluc_r(q, nbars)
            Km = np.where(nbars >= 8, r - 1, -1).astype(np.int64)[:, None]
            s0 = np.arange(len(vv), dtype=np.int64); s1 = s0 + 1
            thr, gt = nb_window_kth(vv, s0, s1, lo.astype(np.int64), hi.astype(np.int64), Km, CAP)
            t = thr[:, 0]; has = t >= 0; g = gt[:, 0]; nn = nbars
        else:
            _, refs, ncen, gid = fam
            ng = len(refs)
            tg = np.full(ng, -1.0); gg = np.zeros(ng, np.int64); ngn = np.zeros(ng, np.int64)
            for gi in range(ng):
                if ncen[gi] < 3: continue
                x = np.concatenate([ds.bmax[a:e] for a, e in refs[gi]]); x = x[x > 0]
                n = len(x); r = int(kyluc_r(q, n)); ngn[gi] = n
                if n < r: continue
                xs = np.sort(x)[::-1]; tg[gi] = xs[r - 1]; gg[gi] = int((x > xs[r - 1]).sum())
            t = tg[gid]; has = t >= 0; g = gg[gid]; nn = ngn[gid]
        nom = np.where(has, (g + 1) / (nn + 1), np.nan)
        exc = ds.sval > np.where(has, t, np.inf)[ds.sbar]
        r_all = kyluc_r(q, nn)
        res = Res(ds, cfg, has, np.where(has, t, np.nan), nom, exc)
        res.nom_decl_bar = np.where(has, r_all / (nn + 1), np.nan)
        return res
    if pa == 'dc_dang_chay':
        return running_rule(ds, cfg['preset'], cfg['floor'], hide=True)
    if pa == 'dc_pct':
        thr = cfg['x'] / 100.0 * ds.tot
        exc = ds.sval >= thr[ds.sbar]
        return Res(ds, cfg, np.ones(ds.nb, bool), thr, np.full(ds.nb, np.nan), exc)
    raise ValueError(pa)


def running_rule(ds, preset, floor, hide=True, cfg=None):
    """Luật đang chạy (UnifiedDots): ngưỡng = max(k x B, sàn), vượt khi v >= ngưỡng; lớn nhất ±w; che chấm xanh cách chấm đỏ <= h."""
    k, hr, hm = PRESET[preset]
    has = np.isfinite(ds.Bmed) & (ds.Bmed > 0)
    thr = np.where(has, np.maximum(k * np.where(has, ds.Bmed, 0), floor), np.nan)
    exc = ds.sval >= np.where(has, thr, np.inf)[ds.sbar]
    cfg = cfg or dict(pa='dc_dang_chay', preset=preset, floor=floor, name=f'dc_dang_chay_{preset}')
    res = Res(ds, cfg, has, thr, np.full(ds.nb, np.nan), exc)
    if hide:
        h = np.maximum(hm, np.floor(hr * ds.w + 0.5)).astype(np.int64)
        di = np.nonzero(res.dot)[0]
        red = di[ds.sside[di] == 0]; blue = di[ds.sside[di] == 1]
        if len(blue) and len(red):
            rk = ds.sbar[red] * (1 << 32) + ds.stk[red]
            bb = ds.sbar[blue]; hb = h[bb]
            lo = np.searchsorted(rk, bb * (1 << 32) + ds.stk[blue] - hb, 'left')
            hi = np.searchsorted(rk, bb * (1 << 32) + ds.stk[blue] + hb, 'right')
            hidden = blue[hi > lo]
            res.dot[hidden] = False
    return res


# =====================================================================================
#                          BẢN CHUẨN TỪNG NẾN (cấu trúc C#)
# =====================================================================================
def bars_from(ds):
    """Danh sách nến: (thời điểm, chỉ số ngày giao dịch, khung giờ, [(tick, bid, ask, vol)] ), giống dữ liệu C# đọc."""
    out = []
    for b in range(ds.nb):
        cells = defaultdict(lambda: [0, 0])
        for i in range(ds.s0[b], ds.s1[b]):
            cells[int(ds.stk[i])][int(ds.sside[i])] = int(ds.sval[i])
        out.append((int(ds.dayi[b]), int(ds.slot[b]), sorted((t, c[0], c[1]) for t, c in cells.items()), float(ds.med[b]), float(ds.mean[b]), float(ds.rng[b])))
    return out


class Hist:
    """Mảng đếm 0..4095 (giá trị lớn hơn dồn vào ô cuối) + tổng số mẫu."""

    def __init__(self):
        self.h = [0] * (CAP + 1); self.n = 0

    def add(self, vals, sgn=1):
        for v in vals:
            self.h[min(v, CAP)] += sgn
        self.n += sgn * len(vals)

    def kth1(self, K):
        return kth1_counts(self.h, K)


def side_values(cells):
    return [b for _, b, a in cells if b > 0] + [a for _, b, a in cells if a > 0]


def dots_of_bar(cells, w, exceed):
    """cells: [(tick, bid, ask)]; exceed(v) -> bool. Trả set (tick, bên) của chấm sau gộp (lớn hơn hẳn cùng bên trong ±w)."""
    out = set()
    for side in (0, 1):
        d = {t: (b if side == 0 else a) for t, b, a in cells}
        for t, v in d.items():
            if v > 0 and exceed(v) and all(d.get(t + o, 0) < v and d.get(t - o, 0) < v for o in range(1, w + 1)):
                out.add((t, side))
    return out


class RangeQ:
    """Hàng đợi biên độ N nến trước -> w (UnifiedDots.Window), và mặt bằng trung vị / TB mỗi ô (CellBigBaseline)."""

    def __init__(self, N):
        self.N = N; self.r = []; self.med = []; self.mean = []

    def w(self):
        if len(self.r) < 5: return 4
        R = sum(self.r) / len(self.r)
        return max(4, rhu(R / 6.0)) if R > 0 else 4

    def L(self, which):
        q = self.med if which == 'med' else self.mean
        if len(q) < 5: return None
        x = sum(q) / len(q)
        return x if x > 0 else None

    def push(self, med, mean, rng):
        self.r.append(rng); self.med.append(med); self.mean.append(mean)
        if len(self.r) > self.N:
            self.r.pop(0); self.med.pop(0); self.mean.pop(0)


def ref_run(bars, cfg, m):
    """BẢN CHUẨN cho mọi phương án mới. Trả list theo nến: (ngưỡng hiển thị hoặc None, set chấm (tick, bên), số mẫu vượt thô)."""
    pa = cfg['pa']; N = nbase(m); rq = RangeQ(N); out = []
    if pa in ('cuon', 'z_log'):
        n = max(5, rhu(cfg['T'] / m)); q = []; H = Hist()
    if pa == 'ky_luc' and cfg['rk'] == 'T':
        n = max(8, rhu(cfg['rv'] / m)); qm = []
    if pa in ('cung_gio', 'lai', 'ky_luc'):
        occ = defaultdict(list)          # khung giờ -> list (ngày, list giá trị / tỉ số / max nến, số nến)
        cur = None
    if pa == 'lai' and cfg['ref'] == 'r1380':
        n = rhu(1380 / m); qr = []        # mỗi phần tử: list tỉ số của 1 nến (None nếu nến chưa có mặt bằng)
    nslot = 1440 // max(30, m)
    for (day, slot, cells, med, mean, rng) in bars:
        vals = side_values(cells)
        thr = None; exceed = None; disp = None
        if pa == 'cuon':
            nbars = len(q)
            K = K_of(cfg['lk'], cfg['lx'], H.n, nbars)
            if K >= 0:
                t, _ = H.kth1(K)
                if t is not None:
                    thr = t; disp = t; exceed = (lambda v, t=t: v > t)
        elif pa == 'z_log':
            if len(q) >= 5:
                x = sorted(np.log(v) for b_ in q for v in b_)
                if x:
                    mm = float(np.median(x)); dd = float(np.median([abs(y - mm) for y in x]))
                    if dd > 0:
                        z0 = cfg['z0']; disp = float(np.exp(mm + z0 * 1.4826 * dd)); thr = disp
                        exceed = (lambda v, mm=mm, dd=dd, z0=z0: (np.log(v) - mm) / (1.4826 * dd) >= z0)
        elif pa in ('cung_gio', 'lai', 'ky_luc') and not (pa == 'lai' and cfg['ref'] == 'r1380') and not (pa == 'ky_luc' and cfg['rk'] == 'T'):
            K_occ = cfg['K'] if pa == 'cung_gio' else (cfg['ref'] if pa == 'lai' else cfg['rv'])
            lc = cfg.get('lc', 0) if pa == 'cung_gio' else 0
            prev = [o for o in occ[slot] if o[0] < day][-K_occ:]
            if len(prev) >= 3:
                ref = list(prev)
                if lc:
                    for ss in ((slot - 1) % nslot, (slot + 1) % nslot):
                        ref += [o for o in occ[ss] if o[0] < day][-K_occ:]
                allv = [v for o in ref for v in o[1]]; nb_ = sum(o[2] for o in ref)
                if pa == 'cung_gio':
                    H2 = Hist(); H2.add(allv)
                    K = K_of(cfg['lk'], cfg['lx'], H2.n, nb_)
                    if K >= 0:
                        t, _ = H2.kth1(K)
                        if t is not None: thr = t; disp = t; exceed = (lambda v, t=t: v > t)
                elif pa == 'lai':
                    K = K_of(cfg['lk'], cfg['lx'], len(allv), nb_)
                    Lc = rq.L(cfg['L'])
                    if K >= 0 and Lc is not None:
                        t, _ = kth1_float(allv, K)
                        if t is not None: thr = t; disp = t * Lc; exceed = (lambda v, t=t, Lc=Lc: v / Lc > t)
                else:  # ky_luc cùng giờ
                    nn = len(allv); r = int(kyluc_r(cfg['q'], nn))
                    if nn >= r:
                        t = sorted(allv, reverse=True)[r - 1]; thr = t; disp = t; exceed = (lambda v, t=t: v > t)
        elif pa == 'lai':   # cuốn 1.380 phút
            sub = [x for x in qr if x is not None]
            allv = [v for x in sub for v in x]
            K = K_of(cfg['lk'], cfg['lx'], len(allv), len(sub))
            Lc = rq.L(cfg['L'])
            if K >= 0 and Lc is not None:
                t, _ = kth1_float(allv, K)
                if t is not None: thr = t; disp = t * Lc; exceed = (lambda v, t=t, Lc=Lc: v / Lc > t)
        elif pa == 'ky_luc':   # cuốn
            if len(qm) >= 8:
                r = int(kyluc_r(cfg['q'], len(qm)))
                t = sorted(qm, reverse=True)[r - 1]; thr = t; disp = t; exceed = (lambda v, t=t: v > t)
        w = rq.w()
        if exceed is not None and cells:
            dots = dots_of_bar(cells, w, exceed); nexc = sum(1 for v in vals if exceed(v))
        else:
            dots = set(); nexc = 0
        out.append((disp, dots, nexc))
        # ---- nến đóng: nộp đúng một lần ----
        Lc_close = rq.L(cfg.get('L', 'med')) if pa == 'lai' else None
        if pa in ('cuon', 'z_log'):
            q.append(vals); H.add(vals)
            if len(q) > n: H.add(q.pop(0), -1)
        elif pa == 'ky_luc' and cfg['rk'] == 'T':
            if vals:
                qm.append(max(vals))
                if len(qm) > n: qm.pop(0)
        elif pa == 'lai' and cfg['ref'] == 'r1380':
            qr.append([v / Lc_close for v in vals] if Lc_close is not None else None)
            if len(qr) > n: qr.pop(0)
        if pa in ('cung_gio', 'lai', 'ky_luc'):
            if pa == 'cung_gio': item = vals; nbk = 1
            elif pa == 'lai': item = [v / Lc_close for v in vals] if Lc_close is not None else []; nbk = 1 if Lc_close is not None else 0
            else: item = [max(vals)] if vals else []; nbk = 1
            L_ = occ[slot]
            if L_ and L_[-1][0] == day:
                L_[-1] = (day, L_[-1][1] + item, L_[-1][2] + nbk)
            else:
                L_.append((day, list(item), nbk))
        rq.push(med, mean, rng)
    return out


def forget(ds):
    """Xóa bộ nhớ đệm của một DotData (đỡ tốn RAM khi chạy lưới)."""
    for k in [k for k in _memo if k[0] == ds.uid]:
        del _memo[k]
