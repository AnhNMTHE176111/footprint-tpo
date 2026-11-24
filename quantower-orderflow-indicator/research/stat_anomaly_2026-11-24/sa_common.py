"""Dùng chung cho vòng 1 "Không theo CORVEN" (bóng = volume bất thường đo bằng thống kê). Xem PLAN.md mục 1.

- Nạp bảng ô F_{GC,NQ}_m{1,5,15,30,60}.pkl / bảng nến S_... của ../nq_calib_2026-11-24 (KHÔNG dùng cột B_med có sẵn).
- Dựng "mẫu" = giá trị bên > 0 (Bid = bên 0 = đỏ, Ask = bên 1 = xanh), sắp theo (nến, bên, tick).
- Hàm chung: phiên, ngày giao dịch (giờ nến + 2 giờ), khung giờ trong ngày (W = max(30, phút)), đoạn chọn/kiểm,
  làm tròn nửa lên, cửa sổ gộp w, khoảng gộp g, ngưỡng "lớn thứ K+1, lớn hơn hẳn" (mảng đếm nguyên + bản số thực).
- Hàm numba: cửa sổ trượt bằng mảng đếm (giống C#), lớn nhất cục bộ ±w, đếm "≥ v" cho thước nhìn lại.
Không dùng giá ở bất cứ đâu; mọi ngưỡng chỉ dùng nến đã đóng trước nến đang xét."""
import os, sys, numpy as np, pandas as pd
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
AD = os.path.join(HERE, '..', 'adaptive_2026-11-24'); NQDIR = os.path.join(HERE, '..', 'nq_calib_2026-11-24')
sys.path.insert(0, AD)
from bt_common import ses_of as _ses_of_str  # noqa: E402  (Á 22:00-07:00, Âu 07:00-13:30, Mỹ 13:30-22:00 UTC)

DATA = os.path.join(HERE, '..', '..', '..', 'data-export', 'data-footprint')
TFS = (1, 5, 15, 30, 60)
SYMS = ('GC', 'NQ')
CAP = 4095                     # mảng đếm 0..4095, giá trị lớn hơn dồn vào ô cuối (dữ liệu hiện có: lớn nhất 2.299, không chạm)
SES_NAMES = ('A', 'Au', 'My'); SES_VN = {'A': 'Á', 'Au': 'Âu', 'My': 'Mỹ'}
# đoạn chọn / kiểm cho CHẤM (theo ngày giao dịch, gồm cả hai đầu)
SPLIT = {'GC': (('2026-08-11', '2026-10-04'), ('2026-10-05', '2026-11-09')),
         'NQ': (('2026-09-14', '2026-10-25'), ('2026-10-26', '2026-11-24'))}
DOANS = ('chon', 'kiem', 'tat_ca')


def rhu(x):
    """Làm tròn nửa lên floor(x + 0,5) (số hoặc mảng)."""
    return np.floor(np.asarray(x, dtype=float) + 0.5).astype(np.int64) if np.ndim(x) else int(np.floor(x + 0.5))


def nbase(m):
    """N nến nền = min(20, max(5, floor(120/phút + 0,5))) (BaselineWindow.BarsFor)."""
    return int(min(20, max(5, np.floor(120.0 / m + 0.5))))


def slot_width(m):
    return max(30, m)


def ses_code(ts):
    s = _ses_of_str(pd.DatetimeIndex(ts))
    return np.select([s == 'A', s == 'Au'], [0, 1], 2).astype(np.int8)


def trading_day(ts):
    return (pd.DatetimeIndex(ts) + pd.Timedelta(hours=2)).normalize()


def merge_w(avg_rng):
    """w = max(4, floor(R/6 + 0,5)); chưa có biên độ (NaN hoặc <= 0) -> 4 (UnifiedDots.Window)."""
    r = np.asarray(avg_rng, dtype=float)
    out = np.full(r.shape, 4, dtype=np.int64)
    ok = np.isfinite(r) & (r > 0)
    out[ok] = np.maximum(4, np.floor(r[ok] / 6.0 + 0.5)).astype(np.int64)
    return out


def merge_g(avg_rng):
    """g = max(2, floor(R/8 + 0,5)); chưa có biên độ -> 2 (BigTradeAdaptive / MergeTicks)."""
    r = np.asarray(avg_rng, dtype=float)
    out = np.full(r.shape, 2, dtype=np.int64)
    ok = np.isfinite(r) & (r > 0)
    out[ok] = np.maximum(2, np.floor(r[ok] / 8.0 + 0.5)).astype(np.int64)
    return out


def prev_mean(x, N, minp=5):
    """Trung bình của tối đa N giá trị TRƯỚC (không gồm chính nó), cần >= minp; NaN nếu chưa đủ.
    Cộng tuần tự từ cũ tới mới rồi chia (đúng cách CellBigBaseline.Avg của C#), để số thực trùng từng bit."""
    return _nb_prev_mean(np.asarray(x, dtype=np.float64), N, minp)


@njit(cache=True)
def _nb_prev_mean(x, N, minp):
    n = len(x); out = np.full(n, np.nan)
    for b in range(n):
        lo = max(0, b - N)
        if b - lo < minp: continue
        s = 0.0
        for i in range(lo, b): s += x[i]
        out[b] = s / (b - lo)
    return out


# ---------------- ngưỡng "lớn thứ K+1" (bản tham chiếu, Python thuần) ----------------
def kth1_counts(hist, K):
    """hist[v] = số mẫu có giá trị v (0..CAP). Trả (ngưỡng = giá trị lớn thứ K+1, số mẫu > ngưỡng) hoặc (None, 0) nếu < K+1 mẫu."""
    c = 0
    for v in range(len(hist) - 1, -1, -1):
        if hist[v] and c + hist[v] >= K + 1:
            return v, c
        c += hist[v]
    return None, 0


def kth1_float(values, K):
    """Bản số thực (tỉ số): sắp giảm dần, ngưỡng = phần tử thứ K+1; trả (ngưỡng, số mẫu > ngưỡng) hoặc (None, 0)."""
    v = sorted(values, reverse=True)
    if len(v) < K + 1:
        return None, 0
    t = v[K]
    return t, sum(1 for x in v if x > t)


# ---------------- numba ----------------
@njit(cache=True)
def nb_window_kth(vals, s0, s1, lo, hi, Kmat, cap):
    """Cửa sổ trượt bằng mảng đếm. Nến b dùng mẫu của các nến [lo[b], hi[b]) (lo, hi không giảm).
    Kmat[b, j] = K của mức j (âm = không tính). Trả thr[b, j] (giá trị lớn thứ K+1, -1 nếu thiếu mẫu) và gt[b, j] (số mẫu > thr)."""
    nb, nj = Kmat.shape
    hist = np.zeros(cap + 1, np.int64)
    thr = np.full((nb, nj), -1.0); gt = np.zeros((nb, nj), np.int64)
    cl = 0; ch = 0; tot = 0
    for b in range(nb):
        while ch < hi[b]:
            for i in range(s0[ch], s1[ch]):
                v = vals[i]
                if v > cap: v = cap
                hist[v] += 1
            tot += s1[ch] - s0[ch]; ch += 1
        while cl < lo[b]:
            for i in range(s0[cl], s1[cl]):
                v = vals[i]
                if v > cap: v = cap
                hist[v] -= 1
            tot -= s1[cl] - s0[cl]; cl += 1
        kmax = -1
        for j in range(nj):
            if Kmat[b, j] > kmax: kmax = Kmat[b, j]
        if kmax < 0 or tot == 0:
            continue
        c = 0
        v = cap
        while v >= 0:
            h = hist[v]
            if h > 0:
                for j in range(nj):
                    K = Kmat[b, j]
                    if K >= 0 and thr[b, j] < 0 and c < K + 1 and c + h >= K + 1:
                        thr[b, j] = v; gt[b, j] = c
                c += h
                if c >= kmax + 1:
                    break
            v -= 1
    return thr, gt


@njit(cache=True)
def nb_window_median_mad(vals, s0, s1, lo, hi, cap):
    """Cửa sổ trượt (như trên). Trả m = trung vị của ln(v), d = trung vị |ln v - m|, n = số mẫu (NaN nếu rỗng)."""
    nb = len(lo)
    hist = np.zeros(cap + 1, np.int64)
    lg = np.zeros(cap + 1)
    for v in range(1, cap + 1): lg[v] = np.log(v)
    M = np.full(nb, np.nan); D = np.full(nb, np.nan); NN = np.zeros(nb, np.int64)
    cl = 0; ch = 0; tot = 0
    for b in range(nb):
        while ch < hi[b]:
            for i in range(s0[ch], s1[ch]):
                v = min(vals[i], cap); hist[v] += 1
            tot += s1[ch] - s0[ch]; ch += 1
        while cl < lo[b]:
            for i in range(s0[cl], s1[cl]):
                v = min(vals[i], cap); hist[v] -= 1
            tot -= s1[cl] - s0[cl]; cl += 1
        NN[b] = tot
        if tot == 0:
            continue
        # trung vị của ln v: phần tử thứ (tot-1)//2 và tot//2 (0-based, tăng dần)
        a = (tot - 1) // 2; bb = tot // 2
        c = 0; va = -1; vb = -1
        for v in range(1, cap + 1):
            h = hist[v]
            if h == 0: continue
            if va < 0 and c + h > a: va = v
            if vb < 0 and c + h > bb: vb = v; break
            c += h
        m = 0.5 * (lg[va] + lg[vb])
        M[b] = m
        # trung vị độ lệch: trộn hai phía từ m ra ngoài (độ lệch tăng dần)
        # phía trái: v giảm dần từ v <= exp(m); phía phải: v tăng dần
        L = 1; R = cap
        # tìm điểm tách: v trái lớn nhất có lg[v] <= m
        sp = 0
        for v in range(1, cap + 1):
            if lg[v] <= m: sp = v
            else: break
        L = sp; R = sp + 1
        c = 0; da = -1.0; db = -1.0
        while True:
            # chọn phía có độ lệch nhỏ hơn
            while L >= 1 and hist[L] == 0: L -= 1
            while R <= cap and hist[R] == 0: R += 1
            if L < 1 and R > cap: break
            if L >= 1 and (R > cap or (m - lg[L]) <= (lg[R] - m)):
                dev = m - lg[L]; h = hist[L]; L -= 1
            else:
                dev = lg[R] - m; h = hist[R]; R += 1
            if da < 0 and c + h > a: da = dev
            if db < 0 and c + h > bb:
                db = dev; break
            c += h
        D[b] = 0.5 * (da + db)
    return M, D, NN


@njit(cache=True)
def nb_localmax(key, tk, vals, wseg):
    """key: mã đoạn (nến*2 + bên) không giảm; trong đoạn tk tăng dần. wseg[i] = w của mẫu i.
    Trả True nếu vals[i] lớn hơn hẳn mọi mẫu cùng đoạn cách <= w tick."""
    n = len(vals); out = np.ones(n, np.bool_)
    for i in range(n):
        w = wseg[i]; v = vals[i]
        j = i - 1
        while j >= 0 and key[j] == key[i] and tk[i] - tk[j] <= w:
            if vals[j] >= v: out[i] = False; break
            j -= 1
        if not out[i]: continue
        j = i + 1
        while j < n and key[j] == key[i] and tk[j] - tk[i] <= w:
            if vals[j] >= v: out[i] = False; break
            j += 1
    return out


@njit(cache=True)
def nb_window_ge(vals, s0, s1, lo, hi, cap):
    """Thước nhìn lại: với mỗi nến b và mỗi mẫu i của b, ge[i] = số mẫu trong cửa sổ [lo[b], hi[b]) có giá trị >= vals[i]; n[b] = cỡ cửa sổ."""
    nb = len(lo)
    hist = np.zeros(cap + 2, np.int64); suf = np.zeros(cap + 2, np.int64)
    ge = np.zeros(len(vals), np.int64); NN = np.zeros(nb, np.int64)
    cl = 0; ch = 0; tot = 0
    for b in range(nb):
        while ch < hi[b]:
            for i in range(s0[ch], s1[ch]):
                hist[min(vals[i], cap)] += 1
            tot += s1[ch] - s0[ch]; ch += 1
        while cl < lo[b]:
            for i in range(s0[cl], s1[cl]):
                hist[min(vals[i], cap)] -= 1
            tot -= s1[cl] - s0[cl]; cl += 1
        NN[b] = tot
        if s1[b] == s0[b]: continue
        # chỉ cần hậu tố từ giá trị nhỏ nhất của nến b
        vmin = cap
        for i in range(s0[b], s1[b]):
            if vals[i] < vmin: vmin = vals[i]
        acc = 0
        for v in range(cap, vmin - 1, -1):
            acc += hist[v]; suf[v] = acc
        for i in range(s0[b], s1[b]):
            ge[i] = suf[min(vals[i], cap)]
    return ge, NN


# ---------------- dữ liệu chấm ----------------
import itertools
_uid = itertools.count(1)


class DotData:
    """Một (mã, khung): bảng nến + mẫu (giá trị bên > 0) sắp theo (nến, bên, tick)."""

    def __init__(self, sym, m, F=None, S=None, tag=None):
        self.uid = next(_uid)
        if F is None:
            F = pd.read_pickle(os.path.join(NQDIR, f'F_{sym}_m{m}.pkl')); S = pd.read_pickle(os.path.join(NQDIR, f'S_{sym}_m{m}.pkl'))
        self.sym, self.m, self.tag = sym, m, tag or sym
        S = S.sort_index()
        self.t = pd.DatetimeIndex(S.index)
        self.nb = len(S)
        self.med = S.med.values.astype(float); self.mean = S['mean'].values.astype(float)
        self.rng = S.rng.values.astype(float); self.tot = S.tot.values.astype(float); self.nl = S.nl.values.astype(np.int64)
        self.N = nbase(m)
        self.R = prev_mean(self.rng, self.N)                      # biên độ TB N nến trước (cần 5)
        self.w = merge_w(self.R)
        self.Bmed = prev_mean(self.med, self.N); self.Bmean = prev_mean(self.mean, self.N)
        self.ses = ses_code(self.t)
        self.tday = trading_day(self.t)
        ud, self.dayi = np.unique(self.tday.values, return_inverse=True)
        self.days = pd.DatetimeIndex(ud)
        mod = self.t.hour * 60 + self.t.minute
        self.W = slot_width(m); self.nslot = 1440 // self.W
        self.slot = (np.asarray(mod) // self.W).astype(np.int64)
        self.hour = np.asarray(self.t.hour).astype(np.int64)
        self.mod = np.asarray(mod).astype(np.int64)
        if sym in SPLIT:
            (a0, a1), (k0, k1) = SPLIT[sym]
            d = self.tday
            self.doan = np.where((d >= a0) & (d <= a1), 0, np.where((d >= k0) & (d <= k1), 1, -1)).astype(np.int8)
        else:
            self.doan = np.full(self.nb, -1, np.int8)
        # mẫu
        bar = np.searchsorted(self.t.values, F.t.values)
        tk = F.tk.values.astype(np.int64)
        parts = []
        for side, col in ((0, 'bid'), (1, 'ask')):
            v = F[col].values.astype(np.int64); k = v > 0
            parts.append((bar[k], np.full(k.sum(), side, np.int8), tk[k], v[k]))
        b = np.concatenate([p[0] for p in parts]); sd = np.concatenate([p[1] for p in parts])
        tkk = np.concatenate([p[2] for p in parts]); vv = np.concatenate([p[3] for p in parts])
        o = np.lexsort((tkk, sd, b))
        self.sbar = b[o].astype(np.int64); self.sside = sd[o]; self.stk = tkk[o]; self.sval = vv[o]
        self.ns = len(self.sval)
        self.s0 = np.searchsorted(self.sbar, np.arange(self.nb), 'left').astype(np.int64)
        self.s1 = np.searchsorted(self.sbar, np.arange(self.nb), 'right').astype(np.int64)
        self.npos = (self.s1 - self.s0).astype(np.int64)
        self.key = self.sbar * 2 + self.sside
        self.lmax = nb_localmax(self.key, self.stk, self.sval, self.w[self.sbar])   # lớn hơn hẳn cùng bên trong ±w
        # giá trị lớn nhất mỗi nến (cho kỷ lục)
        mx = np.zeros(self.nb, np.int64)
        np.maximum.at(mx, self.sbar, self.sval)
        self.bmax = mx

    def doan_mask(self, d):
        return np.ones(self.nb, bool) if d == 'tat_ca' else (self.doan == (0 if d == 'chon' else 1))

    def subset(self, keep_bars):
        """Bản cắt theo nến (mảng bool theo nến, giữ thứ tự): dựng lại như nạp chart chỉ có những nến đó."""
        keep_bars = np.asarray(keep_bars, bool)
        idx = np.nonzero(keep_bars)[0]
        o = DotData.__new__(DotData)
        o.uid = next(_uid)
        o.sym, o.m, o.tag = self.sym, self.m, self.tag
        o.t = self.t[idx]; o.nb = len(idx)
        for a in ('med', 'mean', 'rng', 'tot', 'nl', 'ses', 'slot', 'hour', 'mod', 'doan'):
            setattr(o, a, getattr(self, a)[idx])
        o.N, o.W, o.nslot = self.N, self.W, self.nslot
        o.R = prev_mean(o.rng, o.N); o.w = merge_w(o.R)
        o.Bmed = prev_mean(o.med, o.N); o.Bmean = prev_mean(o.mean, o.N)
        o.tday = self.tday[idx]
        ud, o.dayi = np.unique(o.tday.values, return_inverse=True); o.days = pd.DatetimeIndex(ud)
        ks = keep_bars[self.sbar]
        newb = np.cumsum(keep_bars) - 1
        o.sbar = newb[self.sbar[ks]].astype(np.int64); o.sside = self.sside[ks]; o.stk = self.stk[ks]; o.sval = self.sval[ks]
        o.ns = len(o.sval)
        o.s0 = np.searchsorted(o.sbar, np.arange(o.nb), 'left').astype(np.int64)
        o.s1 = np.searchsorted(o.sbar, np.arange(o.nb), 'right').astype(np.int64)
        o.npos = o.s1 - o.s0
        o.key = o.sbar * 2 + o.sside
        o.lmax = nb_localmax(o.key, o.stk, o.sval, o.w[o.sbar])
        o.bmax = self.bmax[idx]
        return o


_cache = {}


def load_dot(sym, m):
    if (sym, m) not in _cache:
        _cache[(sym, m)] = DotData(sym, m)
    return _cache[(sym, m)]


def build_nq_full(m):
    """Ca biên 6: NQ M1/M5 từ TOÀN BỘ file 26/08 (không cắt 14/09), đúng cách ../nq_calib_2026-11-24/load.py. Lưu pickle cạnh script."""
    fF = os.path.join(HERE, f'F_NQfull_m{m}.pkl'); fS = os.path.join(HERE, f'S_NQfull_m{m}.pkl')
    if os.path.exists(fF):
        return pd.read_pickle(fF), pd.read_pickle(fS)
    d = pd.read_csv(os.path.join(DATA, 'fp_NQZ26_XCME_Time_20260826-20261124_90d.csv'), usecols=['datetime', 'price', 'bid_vol', 'ask_vol', 'volume'])
    d['dt'] = pd.to_datetime(d.datetime)
    d['t'] = d.dt.dt.floor(f'{m}min')
    d['tk'] = np.round(d.price / 0.25).astype(np.int64)
    F = d.groupby(['t', 'tk'], sort=True).agg(bid=('bid_vol', 'sum'), ask=('ask_vol', 'sum'), vol=('volume', 'sum')).reset_index()
    F = F[F.vol > 0]
    st = F.groupby('t').agg(med=('vol', 'median'), mean=('vol', 'mean'), hi=('tk', 'max'), lo=('tk', 'min'), nl=('tk', 'size'), tot=('vol', 'sum'))
    st['rng'] = st.hi - st.lo
    F.to_pickle(fF); st.to_pickle(fS)
    return F, st


def load_nq_full(m):
    k = ('NQfull', m)
    if k not in _cache:
        F, S = build_nq_full(m)
        _cache[k] = DotData('NQ', m, F, S, tag='NQfull')
    return _cache[k]


def group_rate(num, den):
    return num / den if den > 0 else np.nan


if __name__ == '__main__':
    # tự kiểm nhỏ
    assert rhu(2.5) == 3 and rhu(3.5) == 4 and rhu(-0.5) == 0 and rhu(0.49) == 0
    assert [nbase(m) for m in TFS] == [20, 20, 8, 5, 5]
    assert list(merge_w([np.nan, 0, 23, 27, 30, 33])) == [4, 4, 4, 5, 5, 6]     # 27/6 = 4,5 -> 5
    assert list(merge_g([np.nan, 12, 20, 183])) == [2, 2, 3, 23]
    h = np.zeros(10, np.int64); h[[1, 2, 5, 9]] = [5, 3, 2, 1]                   # mẫu: 9, 5 5, 2 2 2, 1x5
    assert kth1_counts(h, 0) == (9, 0) and kth1_counts(h, 1) == (5, 1) and kth1_counts(h, 2) == (5, 1) and kth1_counts(h, 3) == (2, 3)
    assert kth1_counts(h, 10) == (1, 6) and kth1_counts(h, 11) == (None, 0)
    assert kth1_float([0.5, 3.2, 1.1, 3.2], 1) == (3.2, 0) and kth1_float([0.5, 3.2, 1.1, 3.2], 2) == (1.1, 2)
    # numba cửa sổ = bản thuần
    rs = np.random.RandomState(1)
    nb_ = 60; cnt = rs.randint(0, 8, nb_); vals = rs.geometric(0.3, cnt.sum()).astype(np.int64)
    s1 = np.cumsum(cnt); s0 = s1 - cnt
    lo = np.maximum(0, np.arange(nb_) - 7); hi = np.arange(nb_)
    Km = np.tile(np.array([0, 2, 5]), (nb_, 1)).astype(np.int64)
    thr, gt = nb_window_kth(vals, s0, s1, lo, hi, Km, CAP)
    for b in range(nb_):
        hh = np.bincount(vals[s0[lo[b]]:s1[hi[b] - 1]] if hi[b] > 0 else np.zeros(0, np.int64), minlength=CAP + 1) if hi[b] > lo[b] else np.zeros(CAP + 1, np.int64)
        for j, K in enumerate([0, 2, 5]):
            t, g = kth1_counts(hh, K)
            assert (t is None and thr[b, j] < 0) or (t == thr[b, j] and g == gt[b, j]), (b, K, t, thr[b, j])
    M, D, NN = nb_window_median_mad(vals, s0, s1, lo, hi, CAP)
    for b in range(nb_):
        x = np.log(vals[s0[lo[b]]:s1[hi[b] - 1]]) if hi[b] > lo[b] and s1[hi[b] - 1] > s0[lo[b]] else np.zeros(0)
        if len(x) == 0: assert np.isnan(M[b]); continue
        m_ = np.median(x); d_ = np.median(np.abs(x - m_))
        assert abs(M[b] - m_) < 1e-12 and abs(D[b] - d_) < 1e-12, (b, M[b], m_, D[b], d_)
    print('sa_common tự kiểm: ĐẠT')
