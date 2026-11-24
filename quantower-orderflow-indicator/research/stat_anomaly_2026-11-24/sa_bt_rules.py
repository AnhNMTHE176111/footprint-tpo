"""Big Trade (vòng mờ) "Không theo CORVEN": bốn phương án + hai mốc đối chứng (PLAN mục 3).
Giá trị của ô = lệnh đơn lớn nhất của ô (mot > 0). Nguồn: nhật ký lệnh đơn của indicator (../adaptive_2026-11-24/bt_common.py).
Nến không có số liệu lệnh đơn KHÔNG nộp gì và không tính vào số nến của cửa sổ (bộ dữ liệu chỉ gồm nến có số liệu).
Vượt thô: mot lớn hơn hẳn ngưỡng. Vòng sau gộp: duyệt mot giảm dần (bằng nhau thì tick thấp trước), bỏ ô cách ô đã giữ <= g tick,
g = max(2, floor(biên độ TB N nến có số liệu trước / 8 + 0,5)) (chưa đủ 5 nến -> 2). Không giới hạn số vòng, không sàn.

Phương án: cuon (T 60/120/240/480; p 1/0,5/0,2/0,1%; λ 0,25/0,5/1), cung_gio (GC K 5/10, NQ K 3/5; lân cận không/±1),
ky_luc (T 120/240/480, tối thiểu 8 nến; q 0,5/0,25/0,1/0,05), lai (u = mot / L(b), L từ footprint lịch sử của các nến TRƯỚC b;
tập tỉ số = toàn bộ nhật ký trước đó hoặc một ngày cuốn 1.380 phút). Đối chứng: cố định 10 (mot >= 10, không gộp, như indicator cũ);
luật thích nghi đang chạy (bt_rule.simulate: mật độ 1,0 · sàn 5 · gộp · tối đa 3)."""
import os, sys, itertools, numpy as np, pandas as pd
from numba import njit
from sa_common import (AD, rhu, nbase, slot_width, ses_code, trading_day, merge_g, prev_mean, CAP, load_dot, _uid, kth1_counts, kth1_float)
import sa_dot_rules as R
sys.path.insert(0, AD)
from bt_common import load_m1, to_tf, bars_of  # noqa: E402
import bt_rule  # noqa: E402

BT_P = [('p', 100), ('p', 50), ('p', 20), ('p', 10)]
BT_L = [('lam', 1), ('lam', 2), ('lam', 4)]
BT_LEVELS = BT_P + BT_L
LAI_L = ('med', 'mean', 'sqrtvol', 'p90_120')


def bt_configs(sym, lai_L=()):
    C = []
    for T in (60, 120, 240, 480):
        for k, x in BT_LEVELS:
            C.append(dict(pa='cuon', T=T, lk=k, lx=x, name=f'cuon_T{T}_{R.lvl_name(k, x)}'))
    for K in ((5, 10) if sym.startswith('GC') else (3, 5)):
        for lc in (0, 1):
            for k, x in BT_LEVELS:
                C.append(dict(pa='cung_gio', K=K, lc=lc, lk=k, lx=x, name=f'cung_gio_K{K}{"_lc" if lc else ""}_{R.lvl_name(k, x)}'))
    for T in (120, 240, 480):
        for q in (0.5, 0.25, 0.1, 0.05):
            C.append(dict(pa='ky_luc', rk='T', rv=T, q=q, name=f'ky_luc_T{T}_q{q:g}'))
    for L in lai_L:
        for ref in ('cum', 'day'):
            for k, x in BT_LEVELS:
                C.append(dict(pa='lai', L=L, ref=ref, lk=k, lx=x, name=f'lai_{L}_{"tichluy" if ref == "cum" else "ngay"}_{R.lvl_name(k, x)}'))
    C += [dict(pa='dc_codinh', thr=10, name='dc_codinh10'), dict(pa='dc_dang_chay', name='dc_dang_chay_thich_nghi')]
    return C


class BtData:
    """Một (nhật ký, khung): chỉ các nến có số liệu lệnh đơn. Giao diện giống DotData (một bên)."""

    def __init__(self, key, m, c=None):
        self.uid = next(_uid)
        self.key = key; self.sym = key[:2]; self.tag = key; self.m = m
        if c is None:
            c = to_tf(load_m1(key), m)
        c = c[c.mot > 0].sort_values(['t', 'tk']).reset_index(drop=True)
        self.cells = c
        b = bars_of(c)
        self.t = pd.DatetimeIndex(b.t); self.nb = len(b)
        self.rng = b.rng.values.astype(float); self.tot = b.vol.values.astype(float)
        self.N = nbase(m); self.R = prev_mean(self.rng, self.N); self.g = merge_g(self.R); self.w = self.g
        self.ses = ses_code(self.t); self.tday = trading_day(self.t)
        ud, self.dayi = np.unique(self.tday.values, return_inverse=True); self.days = pd.DatetimeIndex(ud)
        mod = np.asarray(self.t.hour * 60 + self.t.minute).astype(np.int64)
        self.mod = mod; self.hour = np.asarray(self.t.hour).astype(np.int64)
        self.W = slot_width(m); self.nslot = 1440 // self.W; self.slot = mod // self.W
        nd = len(self.days)
        if key == 'GC':
            self.doan = np.where(self.dayi < 10, 0, 1).astype(np.int8)          # 10 phiên đầu chọn, 6 phiên cuối kiểm
        elif key == 'GClive':
            self.doan = np.ones(self.nb, np.int8)                               # đoạn kiểm thứ hai
        else:
            self.doan = np.full(self.nb, -1, np.int8)                           # NQ: 6 phiên, không có đoạn kiểm
        self.sbar = np.searchsorted(self.t.values, c.t.values).astype(np.int64)
        self.stk = c.tk.values.astype(np.int64); self.sval = c.mot.values.astype(np.int64); self.ns = len(self.sval)
        self.s0 = np.searchsorted(self.sbar, np.arange(self.nb), 'left').astype(np.int64)
        self.s1 = np.searchsorted(self.sbar, np.arange(self.nb), 'right').astype(np.int64)
        self.npos = self.s1 - self.s0
        self.bmax = np.zeros(self.nb, np.int64); np.maximum.at(self.bmax, self.sbar, self.sval)
        self.lmax = np.ones(self.ns, bool)
        self.Lb = {}

    def doan_mask(self, d):
        return np.ones(self.nb, bool) if d == 'tat_ca' else (self.doan == (0 if d == 'chon' else 1))


# ---------------- mặt bằng L từ footprint (chỉ nến footprint TRƯỚC giờ nến Big Trade) ----------------
@njit(cache=True)
def _nb_p90_window(vals, s0, s1, lo, hi, cap, minn):
    """p90 kiểu hạng gần nhất (phần tử thứ ceil(0,9 n), tăng dần) của các giá trị bên trong nến [lo, hi). Thiếu (< minn) -> NaN."""
    nq = len(lo); out = np.full(nq, np.nan)
    hist = np.zeros(cap + 1, np.int64)
    cl = 0; ch = 0; tot = 0
    for q in range(nq):
        while ch < hi[q]:
            for i in range(s0[ch], s1[ch]): hist[min(vals[i], cap)] += 1
            tot += s1[ch] - s0[ch]; ch += 1
        while cl < lo[q]:
            for i in range(s0[cl], s1[cl]): hist[min(vals[i], cap)] -= 1
            tot -= s1[cl] - s0[cl]; cl += 1
        if tot < minn: continue
        r = int(np.ceil(0.9 * tot))
        c = 0
        for v in range(cap + 1):
            c += hist[v]
            if c >= r:
                out[q] = v; break
    return out


def attach_L(bt, fp):
    """Gắn bt.Lb[L] (theo nến Big Trade) từ footprint fp (DotData cùng mã, cùng khung). L chỉ dùng nến footprint có giờ < giờ nến."""
    j = np.searchsorted(fp.t.values, bt.t.values, 'left')
    N = fp.N

    def pm(x):
        cs = np.r_[0.0, np.cumsum(x)]
        out = np.full(bt.nb, np.nan)
        for i, jj in enumerate(j):
            lo = max(0, jj - N)
            if jj - lo >= 5:
                s = 0.0
                for k in range(lo, jj): s += x[k]
                out[i] = s / (jj - lo)
        return out
    bt.Lb['med'] = pm(fp.med); bt.Lb['mean'] = pm(fp.mean)
    bt.Lb['sqrtvol'] = np.sqrt(pm(fp.tot))
    lo = np.searchsorted(fp.t.values, bt.t.values - np.timedelta64(120, 'm'), 'left').astype(np.int64)
    bt.Lb['p90_120'] = _nb_p90_window(fp.sval, fp.s0, fp.s1, lo, j.astype(np.int64), CAP, 20)
    for k in list(bt.Lb):
        v = bt.Lb[k]; v[~(v > 0)] = np.nan


# ---------------- gộp vòng ----------------
@njit(cache=True)
def _nb_greedy(exc, s0, s1, tk, val, gbar):
    keep = np.zeros(len(exc), np.bool_)
    for b in range(len(s0)):
        idx = [i for i in range(s0[b], s1[b]) if exc[i]]
        if len(idx) == 0: continue
        arr = np.array(idx, np.int64)
        # sắp: mot giảm dần, bằng nhau thì tick thấp trước
        keyv = np.empty(len(arr), np.float64)
        for k in range(len(arr)): keyv[k] = -val[arr[k]] * 1e9 + tk[arr[k]] - tk[s0[b]]
        o = np.argsort(keyv, kind='mergesort')
        kept = np.empty(len(arr), np.int64); nk = 0
        g = gbar[b]
        for k in range(len(arr)):
            i = arr[o[k]]; ok = True
            for kk in range(nk):
                if abs(tk[i] - tk[kept[kk]]) <= g: ok = False; break
            if ok:
                kept[nk] = i; nk += 1; keep[i] = True
    return keep


def merge_greedy(bt, exc):
    return _nb_greedy(exc, bt.s0, bt.s1, bt.stk, bt.sval, bt.g)


# ---------------- lai ----------------
def _lai_bt(bt, L, ref):
    k = R._mkey(bt, 'btlai', L, ref)
    if k in R._memo: return R._memo[k]
    Lb = bt.Lb[L]; okb = np.isfinite(Lb) & (Lb > 0)
    u = np.full(bt.ns, np.nan); sm = okb[bt.sbar]; u[sm] = bt.sval[sm] / Lb[bt.sbar[sm]]
    npos_ok = np.where(okb, bt.npos, 0)
    b = np.arange(bt.nb)
    lo = np.zeros(bt.nb, np.int64) if ref == 'cum' else np.maximum(0, b - rhu(1380 / bt.m)); hi = b
    cs = np.r_[0, np.cumsum(npos_ok)]; cb = np.r_[0, np.cumsum(okb.astype(np.int64))]
    nsamp = cs[hi] - cs[lo]; nbars = cb[hi] - cb[lo]
    Km = np.stack([R.K_vec(kd, x, nsamp, nbars) for kd, x in R.FAM_LEVELS], 1).astype(np.int64)
    uu = np.where(np.isfinite(u), u, np.inf)
    order = np.argsort(uu, kind='stable'); rank = np.empty(bt.ns, np.int64); rank[order] = np.arange(bt.ns)
    thr, gt = R._nb_ratio_window(rank, bt.s0, bt.s1, okb, lo.astype(np.int64), hi.astype(np.int64), Km, uu[order])
    R._memo[k] = (thr, gt, nsamp, nbars, u, okb)
    return R._memo[k]


def evaluate_bt(bt, cfg):
    pa = cfg['pa']
    if pa in ('cuon', 'cung_gio', 'ky_luc'):
        res = R.evaluate(bt, cfg)
    elif pa == 'lai':
        thr, gt, nsamp, nbars, u, okb = _lai_bt(bt, cfg['L'], cfg['ref'])
        j = R.FAM_LEVELS.index((cfg['lk'], cfg['lx'])); t = thr[:, j]
        has = np.isfinite(t) & okb
        den = nsamp if cfg['lk'] == 'p' else nbars
        nom = np.where(has, gt[:, j] / np.maximum(den, 1), np.nan)
        exc = np.where(np.isfinite(u), u, -np.inf) > np.where(has, t, np.inf)[bt.sbar]
        res = R.Res(bt, cfg, has, np.where(has, t * bt.Lb[cfg['L']], np.nan), nom, exc)
    elif pa == 'dc_codinh':
        res = R.Res(bt, cfg, np.ones(bt.nb, bool), np.full(bt.nb, float(cfg['thr'])), np.full(bt.nb, np.nan), bt.sval >= cfg['thr'])
        res.dot = res.exc.copy()          # indicator cũ: mọi ô >= 10, không gộp
        return res
    elif pa == 'dc_dang_chay':
        c = bt.cells; b = bars_of(c)
        kept, thr_s = bt_rule.simulate(c, b, N=bt.N, density=1.0, floor=5, ceil=0, fixed=10, cap=3, div=8, gmin=2)
        thr = thr_s.values.astype(float)
        res = R.Res(bt, cfg, np.ones(bt.nb, bool), thr, np.full(bt.nb, np.nan), bt.sval >= thr[bt.sbar])
        kk = set(zip(kept.t.values, kept.tk.values))
        tt = bt.t.values[bt.sbar]
        res.dot = np.array([(a, b_) in kk for a, b_ in zip(tt, bt.stk)], bool)
        return res
    else:
        raise ValueError(pa)
    res.dot = merge_greedy(bt, res.exc)
    return res


# ---------------- bản chuẩn từng nến (có cả nến không có số liệu) ----------------
def ref_run_bt(bars, cfg, m, Lseq=None):
    """bars: list (chỉ số ngày, khung giờ, [(tick, mot)]) theo thời gian, CÓ THỂ có nến rỗng / mot = 0 (không có số liệu).
    Lseq: list L theo nến (None = chưa có) cho phương án lai. Trả list theo nến: (ngưỡng hiển thị hoặc None, list (tick, mot) vòng giữ lại theo thứ tự giữ, số ô vượt)."""
    pa = cfg['pa']; N = nbase(m); rq = []; out = []
    nslot = 1440 // max(30, m)
    q = []; H = R.Hist(); qm = []; occ = {}; qr = []
    if pa == 'cuon': n = max(5, rhu(cfg['T'] / m))
    if pa == 'ky_luc': n = max(8, rhu(cfg['rv'] / m))
    if pa == 'lai': n = rhu(1380 / m)
    for bi, (day, slot, cells) in enumerate(bars):
        live = [(t, v) for t, v in cells if v > 0]
        vals = [v for _, v in live]
        exceed = None; disp = None
        if pa == 'cuon':
            K = R.K_of(cfg['lk'], cfg['lx'], H.n, len(q))
            if K >= 0:
                t, _ = H.kth1(K)
                if t is not None: disp = t; exceed = (lambda v, t=t: v > t)
        elif pa == 'cung_gio':
            prev = [o for o in occ.get(slot, []) if o[0] < day][-cfg['K']:]
            if len(prev) >= 3:
                ref = list(prev)
                if cfg['lc']:
                    for ss in ((slot - 1) % nslot, (slot + 1) % nslot):
                        ref += [o for o in occ.get(ss, []) if o[0] < day][-cfg['K']:]
                H2 = R.Hist(); H2.add([v for o in ref for v in o[1]]); nb_ = sum(o[2] for o in ref)
                K = R.K_of(cfg['lk'], cfg['lx'], H2.n, nb_)
                if K >= 0:
                    t, _ = H2.kth1(K)
                    if t is not None: disp = t; exceed = (lambda v, t=t: v > t)
        elif pa == 'ky_luc':
            if len(qm) >= 8:
                r = int(R.kyluc_r(cfg['q'], len(qm))); t = sorted(qm, reverse=True)[r - 1]; disp = t; exceed = (lambda v, t=t: v > t)
        elif pa == 'lai':
            sub = [x for x in qr if x is not None]
            allv = [v for x in sub for v in x]
            K = R.K_of(cfg['lk'], cfg['lx'], len(allv), len(sub))
            Lc = Lseq[bi]
            if K >= 0 and Lc is not None:
                t, _ = kth1_float(allv, K)
                if t is not None: disp = t * Lc; exceed = (lambda v, t=t, Lc=Lc: v / Lc > t)
        g = (max(2, rhu((sum(rq) / len(rq)) / 8.0)) if sum(rq) > 0 else 2) if len(rq) >= 5 else 2
        hit = [(t, v) for t, v in live if exceed is not None and exceed(v)]
        out.append((disp, bt_rule.merge_cap(hit, g, 0), len(hit)) if live else (None, [], 0))
        if not live:
            continue                       # nến không có số liệu: không nộp gì
        if pa == 'cuon':
            q.append(vals); H.add(vals)
            if len(q) > n: H.add(q.pop(0), -1)
        elif pa == 'ky_luc':
            qm.append(max(vals))
            if len(qm) > n: qm.pop(0)
        elif pa == 'cung_gio':
            L_ = occ.setdefault(slot, [])
            if L_ and L_[-1][0] == day: L_[-1] = (day, L_[-1][1] + vals, L_[-1][2] + 1)
            else: L_.append((day, list(vals), 1))
        elif pa == 'lai':
            Lc = Lseq[bi]
            qr.append([v / Lc for v in vals] if Lc is not None else None)
            if cfg['ref'] == 'day' and len(qr) > n: qr.pop(0)
        rq.append(max(t for t, _ in live) - min(t for t, _ in live))
        if len(rq) > N: rq.pop(0)
    return out
