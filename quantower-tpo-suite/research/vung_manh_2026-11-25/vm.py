#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vm.py — thư viện lõi cho nghiên cứu "vùng kháng cự / hỗ trợ mạnh" (SessionZones).

Mọi thứ tính trên NẾN M30 + khối lượng từng mức giá của nến M30 (đúng thứ SessionZones.cs có),
nên kết quả không phụ thuộc khung chart. Nến M1 chỉ dùng để CHẤM kết quả (đường đi sau khi chạm).

Các hàm port nguyên từ ProfileEngine.cs: value_area (luật 2 hàng 70%), find_hvn,
group_by_gap (75 phút), week_spans (30 giờ), splice (nghỉ 30–150 phút + nhảy >= 20 giá).
"""
import os, pickle, sys, tempfile
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CACHE = os.environ.get('VM_CACHE', os.path.join(tempfile.gettempdir(), 'vung_manh_cache.pkl'))
TICK = 0.1
ROW = 0.2            # RowTicks = 2
GAP_MIN = 75         # GapMinutes
WEEK_GAP_H = 30      # WeekGapHours
SPLICE_JUMP = 20.0   # MinSpliceJumpPrices
MIN_DAY_BARS = 20    # phiên ngắn hơn (nghỉ lễ) không được làm "ngày hôm qua"
UNIT_DAYS = 5        # đơn vị biến động U = TB (High-Low) nến M30 của 5 phiên đã đóng gần nhất


class Data:
    def __init__(self, cache=CACHE, d=None):
        if d is None:
            with open(cache, 'rb') as f:
                d = pickle.load(f)
        self.m1, self.m30 = d['m1'], d['m30']
        self.lv_i, self.lv_tick, self.lv_vol = d['lv']
        self.lv_vol = self.lv_vol.astype(np.float64)
        n = len(self.m30['t'])
        self.n = n
        self.lv_ptr = np.searchsorted(self.lv_i, np.arange(n + 1))
        t = self.m30['t'].astype('datetime64[s]').astype(np.int64)
        self.ts = t
        gap = np.diff(t) / 60.0
        # phiên (ngày CME) — GroupByGap
        cut = np.where(gap > GAP_MIN)[0] + 1
        st = np.r_[0, cut]; en = np.r_[cut - 1, n - 1]
        self.days = list(zip(st.tolist(), en.tolist()))
        self.day_of = np.zeros(n, np.int32)
        for k, (a, b) in enumerate(self.days):
            self.day_of[a:b + 1] = k
        # tuần — WeekSpans
        cut = np.where(gap > WEEK_GAP_H * 60)[0] + 1
        st = np.r_[0, cut]; en = np.r_[cut - 1, n - 1]
        self.weeks = list(zip(st.tolist(), en.tolist()))
        self.week_of = np.zeros(n, np.int32)
        for k, (a, b) in enumerate(self.weeks):
            self.week_of[a:b + 1] = k
        # chỗ nối hợp đồng — LastSpliceIndex
        o, c = self.m30['o'], self.m30['c']
        sp = np.where((gap >= 30) & (gap <= 150) & (np.abs(o[1:] - c[:-1]) >= SPLICE_JUMP))[0] + 1
        self.splices = sp.tolist()
        self.seg_of = np.searchsorted(sp, np.arange(n), side='right').astype(np.int32)
        # U theo ngày: TB (High-Low) nến M30 của UNIT_DAYS phiên đã đóng gần nhất
        rng = self.m30['h'] - self.m30['l']
        self.unit_day = np.full(len(self.days), np.nan)
        for k in range(len(self.days)):
            lo = max(0, k - UNIT_DAYS)
            if k - lo < 2: continue
            a, b = self.days[lo][0], self.days[k - 1][1]
            self.unit_day[k] = rng[a:b + 1].mean()
        self.U = self.unit_day[self.day_of]
        # con trỏ M1 theo nến M30 (bộ dữ liệu fixture không có M1)
        self.m1_ptr = np.searchsorted(self.m1['i30'], np.arange(n + 1)) if self.m1 is not None else None

    # ---- profile ----------------------------------------------------------
    def ticks_over(self, a, b):
        """(tick[int], vol) cộng dồn trên nến M30 [a..b], theo từng tick."""
        s, e = self.lv_ptr[a], self.lv_ptr[b + 1]
        tk, v = self.lv_tick[s:e], self.lv_vol[s:e]
        if len(tk) == 0: return np.array([], np.int64), np.array([])
        u, inv = np.unique(tk, return_inverse=True)
        return u.astype(np.int64), np.bincount(inv, weights=v)

    def rows_over(self, a, b, row=ROW):
        """Hàng giá như ProfileEngine.VolumeRows: Snap = round(p/row)*row (nửa-về-chẵn như Math.Round của C#)."""
        tk, v = self.ticks_over(a, b)
        if len(tk) == 0: return np.array([]), np.array([])
        rid = np.round((tk / 10.0) / row).astype(np.int64)
        u, inv = np.unique(rid, return_inverse=True)
        return u * row, np.bincount(inv, weights=v)

    def vwap_sigma(self, a, b):
        """VWAP và độ lệch chuẩn có trọng số khối lượng, tính từ khối lượng TỪNG MỨC GIÁ (chính xác, độc lập khung)."""
        tk, v = self.ticks_over(a, b)
        if len(tk) == 0 or v.sum() <= 0: return np.nan, np.nan
        p = tk / 10.0
        m = (p * v).sum() / v.sum()
        return m, float(np.sqrt(((p - m) ** 2 * v).sum() / v.sum()))

    def vwap_typical(self, a, b):
        """VWAP kiểu cũ (ProfileEngine.VwapAt): giá điển hình nến M30 × khối lượng — để so sai khác."""
        m = self.m30
        tp = (m['h'][a:b + 1] + m['l'][a:b + 1] + m['c'][a:b + 1]) / 3
        v = m['v'][a:b + 1]
        mu = (tp * v).sum() / v.sum()
        return mu, float(np.sqrt(((tp - mu) ** 2 * v).sum() / v.sum()))


def value_area(prices, w, frac=0.70):
    """Port ProfileEngine.ValueArea (luật 2 hàng). Trả (poc, vah, val)."""
    n = len(w)
    if n == 0 or w.sum() <= 0: return np.nan, np.nan, np.nan
    poc = int(np.argmax(w))            # hàng đầu tiên đạt max — như vòng for 'w[i] > w[poc]'
    acc, target, lo, hi = w[poc], w.sum() * frac, poc, poc
    while acc < target and (lo > 0 or hi < n - 1):
        up = (w[hi + 1] if hi < n - 1 else 0) + (w[hi + 2] if hi < n - 2 else 0)
        dn = (w[lo - 1] if lo > 0 else 0) + (w[lo - 2] if lo > 1 else 0)
        if hi >= n - 1: acc += dn; lo = max(0, lo - 2)
        elif lo <= 0: acc += up; hi = min(n - 1, hi + 2)
        elif up >= dn: acc += up; hi = min(n - 1, hi + 2)
        else: acc += dn; lo = max(0, lo - 2)
    return prices[poc], prices[hi], prices[lo]


def smooth(w, k=5):
    n = len(w)
    cs = np.r_[0, np.cumsum(w)]
    i = np.arange(n)
    a = np.maximum(0, i - k); z = np.minimum(n - 1, i + k)
    return (cs[z + 1] - cs[a]) / (z - a + 1)


def find_hvn(prices, w, tick=TICK, smooth_k=5, min_ratio=1.5):
    """Port ProfileEngine.FindHvn. Trả (list (chỉ_số_hàng, giá, tỉ lệ so TB) mạnh trước, mảng đã làm mượt)."""
    n = len(w)
    if n < 3: return [], None
    avg = w.mean()
    if avg <= 0: return [], None
    min_sep = float(np.clip((prices[-1] - prices[0]) / tick * 0.08, 20, 120))
    sm = smooth(w, smooth_k)
    pk = [(i, sm[i]) for i in range(1, n - 1) if sm[i] >= sm[i - 1] and sm[i] >= sm[i + 1] and sm[i] >= min_ratio * avg]
    res = []
    for i, wt in sorted(pk, key=lambda x: -x[1]):       # sorted ổn định như OrderByDescending
        if all(abs(prices[i] - prices[k]) / tick >= min_sep for k, _, _ in res):
            res.append((i, prices[i], wt / avg))
    return res, sm


def node_band(prices, sm, i, frac=0.70):
    """Dải của một cụm khối lượng: nới LIÊN TỤC từ đỉnh (trên phân bố ĐÃ LÀM MƯỢT) tới khi < frac × đỉnh."""
    thr = frac * sm[i]
    lo = hi = i
    n = len(sm)
    while lo > 0 and sm[lo - 1] >= thr and abs(prices[lo] - prices[lo - 1] - ROW) < 1e-6: lo -= 1
    while hi < n - 1 and sm[hi + 1] >= thr and abs(prices[hi + 1] - prices[hi] - ROW) < 1e-6: hi += 1
    return lo, hi


def pivots(D, k=2, m=6, r=1.0):
    """
    Điểm "va đập" trên nến M30: đỉnh/đáy cục bộ mà giá ĐI TỚI rồi BẬT LẠI ít nhất r×U.
      đỉnh tại i: h[i] > max(h[i-k..i-1]) và h[i] >= max(h[i+1..i+k]);
                  đi tới: h[i] - min(l[i-m..i]) >= r×U;
                  bật lại: có j trong (i, i+m] với h[i] - l[j] >= r×U trước khi h vượt h[i].
      xác nhận tại nến conf = max(i+k, j) — chỉ được dùng từ khi nến conf ĐÓNG.
    Trả mảng cấu trúc: idx, conf, price, kind(+1 đỉnh, -1 đáy).
    """
    h, l, U, seg = D.m30['h'], D.m30['l'], D.U, D.seg_of
    n = D.n
    out = []
    for i in range(m, n - 1):
        u = U[i]
        if not np.isfinite(u): continue
        if seg[i - m] != seg[i]: continue
        e = min(n - 1, i + m)
        if i + k >= n: continue
        if h[i] > h[i - k:i].max() and h[i] >= h[i + 1:i + k + 1].max() and h[i] - l[i - m:i + 1].min() >= r * u:
            for j in range(i + 1, e + 1):
                if h[j] > h[i] or seg[j] != seg[i]: break
                if h[i] - l[j] >= r * u:
                    out.append((i, max(i + k, j), h[i], 1)); break
        if l[i] < l[i - k:i].min() and l[i] <= l[i + 1:i + k + 1].min() and h[i - m:i + 1].max() - l[i] >= r * u:
            for j in range(i + 1, e + 1):
                if l[j] < l[i] or seg[j] != seg[i]: break
                if h[j] - l[i] >= r * u:
                    out.append((i, max(i + k, j), l[i], -1)); break
    return np.array(out, dtype=[('idx', 'i4'), ('conf', 'i4'), ('price', 'f8'), ('kind', 'i1')])


def cluster(prices, wc):
    """
    Gom điểm va đập thành cụm: lặp — chọn điểm neo p có NHIỀU điểm nhất trong [p, p+wc] (hoà: neo giá thấp hơn),
    lấy cả nhóm, bỏ ra, làm tiếp. Trả list các mảng chỉ số (theo thứ tự đầu vào).
    """
    idx = np.argsort(prices, kind='stable')
    p = prices[idx]
    alive = np.ones(len(p), bool)
    res = []
    while alive.any():
        best, bi = 0, -1
        for a in range(len(p)):
            if not alive[a]: continue
            c = int((alive & (p >= p[a]) & (p <= p[a] + wc + 1e-9)).sum())
            if c > best: best, bi = c, a
        mem = alive & (p >= p[bi]) & (p <= p[bi] + wc + 1e-9)
        res.append(idx[mem])
        alive &= ~mem
    return res
