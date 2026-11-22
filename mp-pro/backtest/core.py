"""Lõi backtest cho sách 'Thực chiến cùng Pro Market Profile' trên footprint GCZ26 M1 (UTC)."""
import numpy as np, pandas as pd, os
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, '..', '..', 'data-export', 'data-footprint')
BASE = 'fp_GCZ26_XCEC_Time_20260811-20261109_90d'
TICK = 0.1
SPLIT = pd.Timestamp('2026-10-12')          # TRAIN < SPLIT <= TEST (theo ngày phiên)


class Data:
    def __init__(self, base=BASE, cache_name='cache.npz', start=None, end=None):
        cache = os.path.join(ROOT, cache_name)
        keys = ['t', 'o', 'h', 'l', 'c', 'volume', 'delta', 'lv_bar', 'lv_tick', 'lv_vol']
        if os.path.exists(cache):
            z = np.load(cache, allow_pickle=True)
            for k in keys:
                setattr(self, k, z[k])
        else:
            b = pd.read_csv(os.path.join(DATA, base + '_bars.csv'), parse_dates=['datetime'])
            lv = pd.read_csv(os.path.join(DATA, base + '.csv'), usecols=['bar_idx', 'price', 'volume'],
                             dtype={'bar_idx': 'int32', 'price': 'float64', 'volume': 'int32'})
            assert (b.bar_idx.values == np.arange(len(b))).all()
            lv = lv.sort_values(['bar_idx', 'price'], kind='stable')
            self.t = b.datetime.values.astype('datetime64[m]')
            self.o, self.h, self.l, self.c = (b[k].values.astype(float) for k in ['open', 'high', 'low', 'close'])
            self.volume = b.volume.values.astype(float)
            self.delta = b.delta.values.astype(float)
            self.lv_bar = lv.bar_idx.values.astype(np.int64)
            self.lv_tick = np.round(lv.price.values / TICK).astype(np.int64)
            self.lv_vol = lv.volume.values.astype(np.int64)
            np.savez(cache, **{k: getattr(self, k) for k in keys})
        ts = pd.to_datetime(self.t)
        self.ts = ts
        # phiên Globex: 22:00 UTC -> 21:00 UTC hôm sau; mã phiên = ngày của (t + 2h)
        sd = (ts + pd.Timedelta(hours=2)).normalize()
        self.sess_day = sd.values
        _, self.sess = np.unique(self.sess_day, return_inverse=True)
        self.n = len(self.c)
        self.min_of_sess = ((ts - (sd - pd.Timedelta(hours=2))).total_seconds() // 60).values.astype(int)
        self.hour = ts.hour.values
        self.minute = ts.minute.values
        self.wd = ts.weekday.values
        self.sess_start = np.r_[0, np.flatnonzero(np.diff(self.sess)) + 1]
        self.sess_end = np.r_[self.sess_start[1:], self.n]
        self.nsess = len(self.sess_start)
        self.sess_dates = pd.to_datetime(self.sess_day[self.sess_start])
        self.full = (self.sess_end - self.sess_start) > 600
        self.lv_start = np.searchsorted(self.lv_bar, np.arange(self.n + 1))
        pc = np.r_[self.c[0], self.c[:-1]]
        tr = np.maximum(self.h - self.l, np.maximum(abs(self.h - pc), abs(self.l - pc)))
        self.atr1 = pd.Series(tr).rolling(60, min_periods=10).mean().values
        # pit COMEX 08:20 ET; DST Mỹ kết thúc 2026-11-01
        yrs = sorted(set(ts.year))
        edt = np.zeros(len(ts), bool)
        for y in yrs:   # DST Mỹ: CN thứ 2 tháng 3 -> CN đầu tháng 11 (07:00 UTC)
            mar = pd.Timestamp(f'{y}-03-01'); s2 = mar + pd.Timedelta(days=(6 - mar.weekday()) % 7 + 7)
            nov = pd.Timestamp(f'{y}-11-01'); s1 = nov + pd.Timedelta(days=(6 - nov.weekday()) % 7)
            edt |= (ts >= s2 + pd.Timedelta(hours=7)) & (ts < s1 + pd.Timedelta(hours=6))
        self.edt = edt
        self.pit_open_utc_min = np.where(self.edt, 12 * 60 + 20, 13 * 60 + 20)

    def profile(self, i, j):
        """Profile khối lượng cho nến M1 [i, j). Trả (tick0, vol)."""
        a, b = self.lv_start[i], self.lv_start[j]
        tk = self.lv_tick[a:b]
        if len(tk) == 0:
            return None, None
        t0 = tk.min()
        return t0, np.bincount(tk - t0, weights=self.lv_vol[a:b])


def poc_va(t0, vol, pct=0.70):
    """POC, VAH, VAL. VA mở rộng từ POC, mỗi bước so tổng 2 mức trên với 2 mức dưới."""
    p = int(np.argmax(vol)); tot = vol.sum(); lo = hi = p; acc = vol[p]; n = len(vol)
    while acc < pct * tot and (lo > 0 or hi < n - 1):
        up = vol[hi + 1:hi + 3].sum() if hi < n - 1 else -1
        dn = vol[max(lo - 2, 0):lo].sum() if lo > 0 else -1
        if up >= dn:
            hi = min(hi + 2, n - 1)
        else:
            lo = max(lo - 2, 0)
        acc = vol[lo:hi + 1].sum()
    return (t0 + p) * TICK, (t0 + hi) * TICK, (t0 + lo) * TICK


def resample(d, tf):
    """Gộp M1 thành nến tf phút căn theo đầu phiên. i0,i1 = chỉ số M1 [i0,i1)."""
    key = d.sess.astype(np.int64) * 10000 + d.min_of_sess // tf
    _, i0 = np.unique(key, return_index=True)
    i1 = np.r_[i0[1:], d.n]
    o = d.o[i0]; c = d.c[i1 - 1]
    h = np.maximum.reduceat(d.h, i0); l = np.minimum.reduceat(d.l, i0)
    v = np.add.reduceat(d.volume, i0)
    df = pd.DataFrame(dict(i0=i0, i1=i1, o=o, h=h, l=l, c=c, v=v, sess=d.sess[i0]))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    df['atr'] = pd.Series(tr).rolling(14, min_periods=5).mean().values
    return df


def in_news(d, i):
    """±10 phút quanh 08:30 ET và 10:00 ET (giờ tin Mỹ thường lệ) — sách: không vào trước/sau tin 10 phút."""
    m = d.hour[i] * 60 + d.minute[i]
    base = 12 * 60 + 30 if d.edt[i] else 13 * 60 + 30
    return abs(m - base) <= 10 or abs(m - (base + 90)) <= 10


def simulate(d, side, entry, sl, tp, i_start, i_expire, limit=True, cost=0.2, exit_min=1375, cancel_fn=None,
             news=True):
    """Mô phỏng 1 lệnh trên M1.
    limit: lệnh chờ tại entry, khớp khi giá giao dịch XUYÊN entry 1 tick (thận trọng).
    market: vào tại open nến i_start + 1 tick trượt.
    Cùng nến chạm cả SL lẫn TP -> tính SL. Thoát cuối phiên (phút 1375 = 20:55 UTC). Phí 0,2 giá/lệnh."""
    s = 1 if side == 'buy' else -1
    fill_i = None
    if limit:
        for i in range(i_start, min(i_expire, d.n)):
            if d.min_of_sess[i] >= exit_min - 30:
                return None
            if cancel_fn is not None and cancel_fn(i):
                return None
            if (s == 1 and d.l[i] <= entry - TICK) or (s == -1 and d.h[i] >= entry + TICK):
                if news and in_news(d, i):
                    return None
                fill_i = i; px = entry; break
        if fill_i is None:
            return None
    else:
        if i_start >= d.n or (news and in_news(d, i_start)):
            return None
        fill_i = i_start; px = d.o[i_start] + s * TICK
    risk = abs(px - sl)
    if risk <= 0 or s * (tp - px) <= 0:
        return None
    sess = d.sess[fill_i]
    i = fill_i
    if (s == 1 and d.l[i] <= sl) or (s == -1 and d.h[i] >= sl):
        pnl = -risk - cost
        return dict(i=fill_i, j=i, side=side, entry=px, sl=sl, tp=tp, pnl=pnl, R=pnl / risk, out='sl')
    for i in range(fill_i + 1, d.n):
        if d.sess[i] != sess or d.min_of_sess[i] >= exit_min:
            ex = d.c[i - 1]
            pnl = s * (ex - px) - cost
            return dict(i=fill_i, j=i, side=side, entry=px, sl=sl, tp=tp, pnl=pnl, R=pnl / risk, out='time')
        hit_sl = (s == 1 and d.l[i] <= sl) or (s == -1 and d.h[i] >= sl)
        hit_tp = (s == 1 and d.h[i] >= tp) or (s == -1 and d.l[i] <= tp)
        if hit_sl:
            gap = (s == 1 and d.o[i] < sl) or (s == -1 and d.o[i] > sl)
            ex = d.o[i] if gap else sl
            pnl = s * (ex - px) - cost
            return dict(i=fill_i, j=i, side=side, entry=px, sl=sl, tp=tp, pnl=pnl, R=pnl / risk, out='sl')
        if hit_tp:
            pnl = s * (tp - px) - cost
            return dict(i=fill_i, j=i, side=side, entry=px, sl=sl, tp=tp, pnl=pnl, R=pnl / risk, out='tp')
    return None


def stats(part):
    if len(part) == 0:
        return dict(n=0)
    byday = part.groupby('date').R.sum()
    rng = np.random.default_rng(0)
    bs = [rng.choice(byday.values, len(byday)).sum() / len(part) for _ in range(2000)]
    return dict(n=len(part), wr=round((part.pnl > 0).mean() * 100, 1), expR=round(part.R.mean(), 3),
                ci90=(round(np.percentile(bs, 5), 3), round(np.percentile(bs, 95), 3)),
                totR=round(part.R.sum(), 1), pts=round(part.pnl.sum(), 1))


def summarize(trades, d, label='', test=False):
    if not trades:
        return dict(label=label, TRAIN=dict(n=0))
    df = pd.DataFrame(trades)
    df['date'] = d.sess_dates[d.sess[df.i.values]]
    out = dict(label=label, TRAIN=stats(df[df.date < SPLIT]))
    if test:
        out['TEST'] = stats(df[df.date >= SPLIT])
    return out


def to_df(trades, d):
    df = pd.DataFrame(trades)
    if len(df):
        df['date'] = d.sess_dates[d.sess[df.i.values]]
        df['time'] = d.ts[df.i.values]
    return df
