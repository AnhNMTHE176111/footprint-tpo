"""Thư viện chung vòng 1 (Opus, 2026-11-25) — PLAN.md mục 3, 4, 6.1.

Đầu vào duy nhất: nhật ký lệnh đơn C:\\Users\\anhla\\AppData\\Roaming\\OrderFlowBubbles\\bigtrade-log\\*.csv
(time_ticks,time_iso,price,mot,buy,sell). Bỏ dòng trùng (time_ticks, price) giữ dòng cuối; quy giá về tick = rhu(price / cỡ tick);
trùng tick trong một nến giữ lệnh lớn hơn (như BigTradeLog.CellsOf), volume ô = buy + sell (cộng dồn khi trùng tick).

Quy ước (PLAN.md mục 3):
  - giá trị xét = mot > 0; ngưỡng chỉ từ nến đã đóng TRƯỚC (vòng lặp chung: nguong(i) rồi nop(i));
  - nổ khi mot > ngưỡng (lớn hơn hẳn);
  - "số phút nến" = số nến có >= 1 ô mot > 0 nhân m; một ngày nến = 1380 phút;
  - hạng theo thời gian: K = max(1, rhu(R x phút nến / 1380)); ngưỡng = giá trị lớn thứ K (mảng đếm 4096 ô, > 4095 dồn ô cuối);
  - gộp vòng: g = max(2, rhu(biên độ TB / 8)) khi đã có >= 5 nến trong hàng đợi biên độ BarsFor(m) nến, ngược lại 2;
    chọn tham lam lệnh lớn trước (bằng nhau: tick thấp trước), bỏ ô cách ô đã giữ <= g tick; không giới hạn số vòng;
  - ngày giao dịch bắt đầu 17:00 Chicago (StatClock); phiên Á 17:00-02:00, Âu 02:00-08:30, Mỹ 08:30-17:00;
  - ngày đủ = ngày giao dịch có >= 1170 phút nến.
"""
import os, sys, math, glob, pickle, datetime as dt
from collections import deque
import numpy as np, pandas as pd

LOGDIR = r'C:\Users\anhla\AppData\Roaming\OrderFlowBubbles\bigtrade-log'
SCRATCH = r'C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\bw1'
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(SCRATCH, exist_ok=True)
CAP = 4095
DAYMIN = 1380
FULLMIN = 1170

# khóa -> (file, phút một nến, cỡ tick, mã)
LOGS = {
    'GCX_M1': ('_GC_XCEC_Time_1Minute.csv', 1, 0.1, 'GC'),
    'GCX_M5': ('_GC_XCEC_Time_5Minute.csv', 5, 0.1, 'GC'),
    'NQ_M1': ('_NQZ26_XCME_Time_1Minute.csv', 1, 0.25, 'NQ'),
    'NQ_M15': ('_NQZ26_XCME_Time_15Minute.csv', 15, 0.25, 'NQ'),
    'GCZ_M1': ('_GCZ26_XCEC_Time_1Minute.csv', 1, 0.1, 'GC'),
    'GCZ_M5': ('_GCZ26_XCEC_Time_5Minute.csv', 5, 0.1, 'GC'),
    'GCZ_M15': ('_GCZ26_XCEC_Time_15Minute.csv', 15, 0.1, 'GC'),
    'GCZ_M30': ('_GCZ26_XCEC_Time_30Minute.csv', 30, 0.1, 'GC'),
}
# đoạn chọn / kiểm (ngày giao dịch), PLAN.md mục 4
D = dt.date
SEGMENTS = {
    'GC': {'chon': (D(2026, 9, 1), D(2026, 9, 11)), 'kiem': (D(2026, 9, 14), D(2026, 9, 23))},
    'NQ': {'chon': (D(2026, 10, 26), D(2026, 10, 28)), 'kiem_list': [D(2026, 10, 29), D(2026, 10, 30), D(2026, 11, 2)]},
}


def rhu(x):
    return int(math.floor(x + 0.5))


def bars_for(m, window=120.0):
    return int(min(20, max(5, math.floor(window / m + 0.5))))


# ---------- giờ Chicago (StatClock) ----------
def _nth_sunday(y, mo, nth):
    d = dt.datetime(y, mo, 1)
    add = (6 - d.weekday()) % 7  # weekday: Mon=0 .. Sun=6
    return d + dt.timedelta(days=add + 7 * (nth - 1))


def ct_offset(utc):
    """utc: pd.Series datetime64 (naive UTC) -> Series số giờ lệch (-5 / -6)."""
    off = pd.Series(-6, index=utc.index)
    for y in utc.dt.year.unique():
        a = _nth_sunday(int(y), 3, 2) + dt.timedelta(hours=8)
        b = _nth_sunday(int(y), 11, 1) + dt.timedelta(hours=7)
        off[(utc >= a) & (utc < b)] = -5
    return off


def session_of(h):
    """h = giờ Chicago dạng số thực -> 'A' / 'Au' / 'My'."""
    return np.select([(h >= 17) | (h < 2), (h >= 2) & (h < 8.5)], ['A', 'Au'], 'My')


# ---------- nạp ----------
class Log:
    """Nhật ký đã gom theo nến. Mảng ô sắp theo (nến, tick); off[i]:off[i+1] là ô của nến i.
    Mọi nến ở đây đều có >= 1 ô mot > 0 (nhật ký chỉ ghi ô mot > 0)."""

    def __init__(self, key, m, tick, sym, t, cell_bar, cell_tick, cell_mot, cell_vol):
        self.key, self.m, self.tick, self.sym = key, m, tick, sym
        self.t = t                                    # np.datetime64 UTC của từng nến
        self.nb = len(t)
        self.cb, self.ctk, self.cmot, self.cvol = cell_bar, cell_tick, cell_mot, cell_vol
        self.off = np.searchsorted(cell_bar, np.arange(self.nb + 1))
        tt = pd.Series(pd.to_datetime(t))
        off = ct_offset(tt)
        ct = tt + pd.to_timedelta(off, unit='h')
        self.ct = ct.values
        self.day = (ct + pd.Timedelta(hours=7)).dt.date.values      # ngày giao dịch
        h = ct.dt.hour + ct.dt.minute / 60.0
        self.ses = session_of(h.values)
        self.slot = ((ct.dt.hour * 60 + ct.dt.minute) // max(30, m)).values.astype(int)
        self.nslot = -(-1440 // max(30, m))
        # mỗi nến: max mot, volume, biên độ (tick cao - thấp các ô mot > 0)
        self.bmax = np.maximum.reduceat(cell_mot, self.off[:-1]) if self.nb else np.zeros(0, int)
        self.bvol = np.add.reduceat(cell_vol, self.off[:-1]) if self.nb else np.zeros(0)
        self.brange = (np.maximum.reduceat(cell_tick, self.off[:-1]) - np.minimum.reduceat(cell_tick, self.off[:-1])) if self.nb else np.zeros(0)
        # ngày đủ
        dd = pd.Series(self.day).value_counts() * m
        self.daymin = dd.to_dict()
        self.full_days = sorted(d for d, v in self.daymin.items() if v >= FULLMIN)
        self._g = None

    def cells(self, i):
        a, b = self.off[i], self.off[i + 1]
        return self.ctk[a:b], self.cmot[a:b]

    def gvec(self):
        """g của từng nến, chỉ từ biên độ các nến đóng TRƯỚC (hàng đợi BarsFor(m) nến; >= 5 nến mới dùng TB)."""
        if self._g is None:
            n = bars_for(self.m)
            g = np.full(self.nb, 2, int)
            q = deque()
            s = 0.0
            for i in range(self.nb):
                if len(q) >= 5:
                    avg = s / len(q)
                    if avg > 0: g[i] = max(2, rhu(avg / 8.0))
                q.append(float(self.brange[i])); s += self.brange[i]
                if len(q) > n: s -= q.popleft()
            self._g = g
        return self._g

    def subset_days(self, keep):
        """Log con chỉ gồm các nến có ngày giao dịch trong keep (dùng cho ca biên)."""
        mask = np.isin(self.day, list(keep))
        return self.subset_bars(np.nonzero(mask)[0])

    def subset_bars(self, idx):
        idx = np.asarray(idx)
        newpos = -np.ones(self.nb, int); newpos[idx] = np.arange(len(idx))
        cm = np.isin(self.cb, idx)
        return Log(self.key, self.m, self.tick, self.sym, self.t[idx], newpos[self.cb[cm]], self.ctk[cm], self.cmot[cm], self.cvol[cm])


def load(key, refresh=False):
    fn, m, tick, sym = LOGS[key]
    p = os.path.join(LOGDIR, fn)
    cache = os.path.join(SCRATCH, f'log_{key}.pkl')
    st = os.stat(p)
    if not refresh and os.path.exists(cache):
        with open(cache, 'rb') as f:
            c = pickle.load(f)
        if c.get('mtime') == st.st_mtime and c.get('size') == st.st_size:
            return c['log']
    d = pd.read_csv(p).drop_duplicates(['time_ticks', 'price'], keep='last')
    d = d[d.mot > 0].copy()
    d['tk'] = np.floor(d.price.values / tick + 0.5).astype(np.int64)
    d['vol'] = d.buy + d.sell
    g = d.groupby(['time_ticks', 'tk'], sort=True).agg(mot=('mot', 'max'), vol=('vol', 'sum')).reset_index()
    times = np.sort(g.time_ticks.unique())
    bar = np.searchsorted(times, g.time_ticks.values)
    t = (pd.to_datetime((times - 621355968000000000) // 10, unit='us')).values
    log = Log(key, m, tick, sym, t, bar, g.tk.values.astype(np.int64), np.floor(g.mot.values).astype(np.int64), g.vol.values.astype(float))
    with open(cache, 'wb') as f:
        pickle.dump({'mtime': st.st_mtime, 'size': st.st_size, 'log': log}, f)
    return log


# ---------- gộp ----------
def gop(ticks, mots, thr, g):
    """BigTradeAdaptive.Select(strict=True, cap=0): ô mot > thr, mot giảm dần (bằng nhau tick thấp trước, rồi chỉ số), bỏ ô cách ô đã giữ <= g tick.
    Trả CHỈ SỐ trong mảng ô theo thứ tự giữ."""
    idx = [i for i in range(len(mots)) if mots[i] > 0 and mots[i] > thr]
    idx.sort(key=lambda i: (-mots[i], ticks[i], i))
    kept = []
    for i in idx:
        if g > 0 and any(abs(int(ticks[i]) - int(ticks[j])) <= g for j in kept): continue
        kept.append(i)
    return kept


def gop_nonstrict_cap(ticks, mots, thr, g, cap):
    """BigTradeAdaptive.Select(strict=False): ô mot >= thr; cap > 0: tối đa cap vòng."""
    idx = [i for i in range(len(mots)) if mots[i] > 0 and mots[i] >= thr]
    idx.sort(key=lambda i: (-mots[i], ticks[i], i))
    kept = []
    for i in idx:
        if cap > 0 and len(kept) >= cap: break
        if g > 0 and any(abs(int(ticks[i]) - int(ticks[j])) <= g for j in kept): continue
        kept.append(i)
    return kept


def select_rounds(log, thr, merge=True, strict=True, cap=0):
    """thr: mảng ngưỡng theo nến (nan = chưa có ngưỡng). Trả DataFrame vòng: bar, tick, mot, thr."""
    g = log.gvec() if merge else np.zeros(log.nb, int)
    thr = np.asarray(thr, float)
    ok = ~np.isnan(thr)
    cand = np.nonzero(ok & ((log.bmax > thr) if strict else (log.bmax >= thr)))[0]
    rows = []
    for i in cand:
        a, b = log.off[i], log.off[i + 1]
        tk, mt = log.ctk[a:b], log.cmot[a:b]
        if strict:
            kept = gop(tk, mt, thr[i], g[i])
        else:
            kept = gop_nonstrict_cap(tk, mt, thr[i], g[i], cap)
        for j in kept: rows.append((i, int(tk[j]), int(mt[j]), thr[i]))
    return pd.DataFrame(rows, columns=['bar', 'tick', 'mot', 'thr'])


# ---------- hàng đợi + mảng đếm (khung chung cho ứng viên) ----------
class WinHist:
    """Hàng đợi tối đa cap nến có số liệu + mảng đếm 4096 ô. add(i) nộp nến i của log."""

    def __init__(self, log, cap_bars):
        self.log, self.cap = log, max(1, cap_bars)
        self.H = np.zeros(CAP + 1, np.int64)
        self.q = deque(); self.n = 0

    def add(self, i):
        a, b = self.log.off[i], self.log.off[i + 1]
        v = np.minimum(self.log.cmot[a:b], CAP)
        self.q.append(v); np.add.at(self.H, v, 1); self.n += len(v)
        while len(self.q) > self.cap:
            o = self.q.popleft(); np.add.at(self.H, o, -1); self.n -= len(o)

    @property
    def minutes(self):
        return len(self.q) * self.log.m

    def cum(self):
        """c[j] = số mẫu có giá trị >= CAP - j."""
        return np.cumsum(self.H[::-1])

    @staticmethod
    def kth(c, K):
        """Giá trị lớn thứ K (K >= 1) từ c; nan nếu chưa đủ K mẫu."""
        if K < 1 or c[-1] < K: return np.nan
        return float(CAP - int(np.searchsorted(c, K)))


def rank_K(R, minutes):
    return max(1, rhu(R * minutes / DAYMIN))


# ---------- ứng viên ----------
class Cand:
    """Giao diện: nguong(i) -> (ngưỡng hoặc nan, phút nến tham chiếu, đủ cửa sổ đầy hay chưa); nop(i).
    Vòng lặp chung run_cand gọi nguong(i) rồi nop(i) cho từng nến theo thời gian."""
    code = '?'
    full_minutes = 0

    def params(self): return ''


class CandA(Cand):
    """A. Hạng nhiều ngày: lớn thứ K của D ngày nến gần nhất. Nhiều R cùng một lần chạy (rs)."""
    code = 'A'

    def __init__(self, log, Dd, rs):
        self.log, self.Dd, self.rs = log, Dd, list(rs)
        self.cap = rhu(Dd * DAYMIN / log.m)
        self.w = WinHist(log, self.cap)
        self.full_minutes = self.cap * log.m

    def nguong_multi(self, i):
        if not self.w.q: return [np.nan] * len(self.rs), 0, False
        c = self.w.cum(); mn = self.w.minutes
        return [WinHist.kth(c, rank_K(R, mn)) for R in self.rs], mn, len(self.w.q) >= self.cap

    def nop(self, i): self.w.add(i)


class CandC(Cand):
    """C. ngưỡng = rhu(k x L), L = lớn thứ max(1, rhu(phút nến / q)) của D=5 ngày nến. Nhiều (q, k) cùng lúc."""
    code = 'C'

    def __init__(self, log, qk, Dd=5):
        self.log, self.qk, self.Dd = log, list(qk), Dd
        self.cap = rhu(Dd * DAYMIN / log.m)
        self.w = WinHist(log, self.cap)
        self.full_minutes = self.cap * log.m

    def nguong_multi(self, i):
        if not self.w.q: return [np.nan] * len(self.qk), 0, False
        c = self.w.cum(); mn = self.w.minutes
        out = []
        for q, k in self.qk:
            L = WinHist.kth(c, max(1, rhu(mn / q)))
            out.append(np.nan if np.isnan(L) else float(rhu(k * L)))
        return out, mn, len(self.w.q) >= self.cap

    def nop(self, i): self.w.add(i)


def stat_threshold(c, n, pbp=100):
    """StatRank.Threshold: n*p < 50000 -> chưa có; K = p*n/10000; lớn thứ K+1."""
    if n * pbp < 50000: return np.nan
    K = (pbp * n) // 10000
    return WinHist.kth(c, K + 1)


class CandCwrong(Cand):
    """C sai (cố ý): ngưỡng = rhu(k x mức 1% số ô của 240 phút) — mức 1% theo StatRank (như luật hiện tại)."""
    code = 'Cx'

    def __init__(self, log, ks):
        self.log, self.ks = log, list(ks)
        self.cap = max(5, rhu(240 / log.m))
        self.w = WinHist(log, self.cap)
        self.full_minutes = self.cap * log.m

    def nguong_multi(self, i):
        c = self.w.cum(); p1 = stat_threshold(c, self.w.n)
        return [np.nan if np.isnan(p1) else float(rhu(k * p1)) for k in self.ks], self.w.minutes, len(self.w.q) >= self.cap

    def nop(self, i): self.w.add(i)


class CandHill(Cand):
    """D. Ngoại suy Hill: k0 lệnh lớn nhất của D=5 ngày nến; alpha = k0 / sum ln(x_i / x_k0) (i = 1..k0);
    ngưỡng = x_k0 x (k0 / K)^(1/alpha), K như A. Ngưỡng để số thực (không làm tròn). Nhiều (k0, R) cùng lúc."""
    code = 'D'

    def __init__(self, log, k0R, Dd=5):
        self.log, self.k0R, self.Dd = log, list(k0R), Dd
        self.cap = rhu(Dd * DAYMIN / log.m)
        self.w = WinHist(log, self.cap)
        self.full_minutes = self.cap * log.m
        self.vals = np.arange(CAP, -1, -1, dtype=float)
        self.lv = np.log(np.maximum(self.vals, 1e-9))

    def hill(self, k0):
        H = self.w.H[::-1]
        c = np.cumsum(H)
        if c[-1] < k0: return np.nan, np.nan
        j = int(np.searchsorted(c, k0))
        xk = self.vals[j]
        if xk <= 0: return np.nan, np.nan
        cnt = H[:j + 1].astype(float).copy()
        cnt[j] -= (c[j] - k0)          # chỉ lấy đủ k0 mẫu
        s = float(np.sum(cnt * (self.lv[:j + 1] - math.log(xk))))
        alpha = np.inf if s <= 0 else k0 / s
        return xk, alpha

    def nguong_multi(self, i):
        if not self.w.q: return [np.nan] * len(self.k0R), 0, False
        mn = self.w.minutes; out = []; cache = {}
        for k0, R in self.k0R:
            if k0 not in cache: cache[k0] = self.hill(k0)
            xk, a = cache[k0]
            if np.isnan(xk): out.append(np.nan); continue
            K = rank_K(R, mn)
            out.append(float(xk) if np.isinf(a) else float(xk * (k0 / K) ** (1.0 / a)))
        return out, mn, len(self.w.q) >= self.cap

    def nop(self, i): self.w.add(i)


class CandE(Cand):
    """E. Sàn cố định."""
    code = 'E'

    def __init__(self, log, fl):
        self.log, self.fl = log, list(fl); self.full_minutes = 0

    def nguong_multi(self, i): return [float(x) for x in self.fl], 0, True

    def nop(self, i): pass


class CandF(Cand):
    """F. V = trung vị (volume nến / m) của rhu(T / m) nến có số liệu gần nhất; ngưỡng = rhu(f x V). Trả V (nhân f sau)."""
    code = 'F'

    def __init__(self, log, T):
        self.log, self.T = log, T
        self.cap = max(1, rhu(T / log.m))
        self.q = deque()
        self.full_minutes = self.cap * log.m

    def nguong_multi(self, i):
        if not self.q: return [np.nan], 0, False
        return [float(np.median(self.q))], len(self.q) * self.log.m, len(self.q) >= self.cap

    def nop(self, i):
        self.q.append(self.log.bvol[i] / self.log.m)
        while len(self.q) > self.cap: self.q.popleft()


class CandG(Cand):
    """G. Kỷ lục trượt: lớn thứ K (cố định) của T phút nến gần nhất. Nhiều K cùng lúc."""
    code = 'G'

    def __init__(self, log, T, ks):
        self.log, self.T, self.ks = log, T, list(ks)
        self.cap = max(1, rhu(T / log.m))
        self.w = WinHist(log, self.cap)
        self.full_minutes = self.cap * log.m

    def nguong_multi(self, i):
        if not self.w.q: return [np.nan] * len(self.ks), 0, False
        c = self.w.cum()
        return [WinHist.kth(c, K) for K in self.ks], self.w.minutes, len(self.w.q) >= self.cap

    def nop(self, i): self.w.add(i)


class CandB(Cand):
    """B. Hạng theo khung giờ 30 phút Chicago +/- 1 khung, D ngày giao dịch trước (ngày < ngày nến).
    Khung chính phải có >= 2 ngày; tập tham chiếu = khung chính + 2 khung lân cận (mỗi khung D phần tử cuối có ngày < ngày nến).
    Phút nến tham chiếu = tổng số nến có số liệu trong tập x m; K = max(1, rhu(R x phút / 1380)). Chưa đủ 2 ngày -> dùng A (cùng D, R).
    Trả thêm cờ đủ: khung chính có đủ D ngày."""
    code = 'B'

    def __init__(self, log, Dd, rs):
        self.log, self.Dd, self.rs = log, Dd, list(rs)
        self.A = CandA(log, Dd, rs)
        self.slots = {}   # slot -> list of [day, hist(dict val->cnt) as np array, nbars]
        self.cache = {}
        self.full_minutes = self.A.full_minutes

    def _ref(self, day, s):
        els = [e for e in self.slots.get(s, []) if e[0] < day][-self.Dd:]
        return els

    def nguong_multi(self, i):
        day, s = self.log.day[i], int(self.log.slot[i])
        key = (day, s)
        if key not in self.cache:
            main = self._ref(day, s)
            if len(main) < 2:
                self.cache[key] = None
            else:
                ns = self.log.nslot
                nb = [(s - 1 + ns) % ns, (s + 1) % ns]
                nb = [x for j, x in enumerate(nb) if x != s and x not in nb[:j]]
                H = np.zeros(CAP + 1, np.int64); bars = 0
                for e in main + sum((self._ref(day, x) for x in nb), []):
                    H += e[1]; bars += e[2]
                c = np.cumsum(H[::-1]); mn = bars * self.log.m
                self.cache[key] = ([WinHist.kth(c, rank_K(R, mn)) for R in self.rs], mn, len(main) >= self.Dd)
        r = self.cache[key]
        a, amn, afull = self.A.nguong_multi(i)
        if r is None:
            return a, amn, False, 'A'
        return r[0], r[1], r[2], 'B'

    def nop(self, i):
        day, s = self.log.day[i], int(self.log.slot[i])
        L = self.slots.setdefault(s, [])
        if not L or L[-1][0] != day:
            L.append([day, np.zeros(CAP + 1, np.int64), 0])
            if len(L) > self.Dd + 1: L.pop(0)
        a, b = self.log.off[i], self.log.off[i + 1]
        np.add.at(L[-1][1], np.minimum(self.log.cmot[a:b], CAP), 1); L[-1][2] += 1
        self.A.nop(i)


def run_multi(cand, log):
    """Vòng lặp chung: với từng nến i: ngưỡng = nguong(i) (chỉ trạng thái nến < i), rồi nop(i).
    Trả (thr[nP, nb], refmin[nb], full[nb], src[nb])."""
    out = None; refmin = np.zeros(log.nb); full = np.zeros(log.nb, bool); src = np.empty(log.nb, object)
    for i in range(log.nb):
        r = cand.nguong_multi(i)
        th, mn, fu = r[0], r[1], r[2]
        if out is None: out = np.full((len(th), log.nb), np.nan)
        out[:, i] = th; refmin[i] = mn; full[i] = fu; src[i] = r[3] if len(r) > 3 else cand.code
        cand.nop(i)
    return out, refmin, full, src


# ---------- mốc so sánh ----------
def thr_current(log):
    """Luật hiện tại (chế độ thống kê): StatBigTrade, 1% (StatRank) của max(5, rhu(240/m)) nến có số liệu."""
    w = WinHist(log, max(5, rhu(240 / log.m)))
    thr = np.full(log.nb, np.nan)
    for i in range(log.nb):
        thr[i] = stat_threshold(w.cum(), w.n); w.add(i)
    return thr


def thr_adaptive(log, density=1.0, floor=5.0, fixed=10.0):
    """BigTradeAdaptive mặc định (Theo CORVEN): N = BarsFor(m), K = rhu(density x N); mỗi nến giữ top-K lệnh;
    ngưỡng = max(sàn, lớn thứ K của N nến trước); < 5 nến -> cố định 10. Chọn >=, tối đa 3 vòng mỗi nến (dùng gop_nonstrict_cap)."""
    N = bars_for(log.m); K = max(1, rhu(density * N))
    q = deque(); thr = np.full(log.nb, np.nan)
    for i in range(log.nb):
        if len(q) < 5: thr[i] = fixed
        else:
            v = np.sort(np.concatenate(list(q)))[::-1]
            thr[i] = max(floor, float(v[K - 1]) if len(v) >= K else 0.0)
        a, b = log.off[i], log.off[i + 1]
        q.append(np.sort(log.cmot[a:b])[::-1][:K].astype(float))
        if len(q) > N: q.popleft()
    return thr


# ---------- mức 1% M1 cùng khung giờ 30 phút của 5 ngày trước (T2) ----------
def p1_slot_table(m1log, ndays=5):
    """(ngày, khung 30') -> mức 1% (StatRank-style: K = n // 100, lớn thứ K+1) của ô M1 cùng khung, ndays ngày giao dịch trước có số liệu.
    Cần >= 2 ngày trước; ngược lại không có."""
    assert m1log.m == 1
    slot30 = m1log.slot  # m=1 -> khung 30'
    per = {}
    cb = m1log.cb
    days = m1log.day[cb]; sl = slot30[cb]
    df = pd.DataFrame({'day': days, 'slot': sl, 'mot': m1log.cmot})
    for (d_, s_), g in df.groupby(['day', 'slot']):
        per.setdefault(s_, []).append((d_, np.sort(g.mot.values)[::-1]))
    tab = {}
    for s_, L in per.items():
        L.sort(key=lambda x: x[0])
        for j in range(len(L)):
            prev = L[max(0, j - ndays):j]
            if len(prev) < 2: continue
            v = np.sort(np.concatenate([x[1] for x in prev]))[::-1]
            K = len(v) // 100
            tab[(L[j][0], s_)] = float(v[min(K, len(v) - 1)])
        # cũng cho ngày chưa có số liệu ở khung đó (vòng có thể nằm ở nến khung lớn) -> tra theo ngày < d
    return tab, per


def p1_lookup(per, day, slot, ndays=5):
    L = per.get(slot)
    if not L: return np.nan
    prev = [x for x in L if x[0] < day][-ndays:]
    if len(prev) < 2: return np.nan
    v = np.sort(np.concatenate([x[1] for x in prev]))[::-1]
    return float(v[min(len(v) // 100, len(v) - 1)])


def level1pct(vals):
    v = np.sort(np.asarray(vals))[::-1]
    if len(v) == 0: return np.nan
    return float(v[min(len(v) // 100, len(v) - 1)])


def fmt_day(d):
    return f'{d.day}/{d.month}'
