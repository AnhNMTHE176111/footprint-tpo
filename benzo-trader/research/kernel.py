"""KERNEL cua Benzo Trader - thu vien dung chung cho 4 agent setup (A pha hoi, B hap thu, C fade canh, D trap).

Nguyen tac cung: KHONG NHIN TRUOC o bat ky ham nao. Moi gia tri tai nen i chi dung du lieu cua cac nen <= i
(nen i da dong), tru cac cot ghi ro la 'chi de loc' (splice).

Quy uoc:
  * 1 'gia' = 1 USD = 10 tick (tick GC = 0,1). Gio trong file: UTC. Gio VN = UTC+7.
  * 'datetime' cua nen M1 = gio MO nen (nen 13:44 dong luc 13:45).
  * idx / pos trong moi ham = VI TRI (iloc, 0..n-1) cua nen trong DataFrame do load_bars tra ve.
  * Phien CME: tach khi khoang trong giua 2 nen > 30 phut; ten phien = ngay (UTC) cua nen CUOI phien.
  * 'sm' = so phut ke tu 05:00 VN (gio 'neo My': khi My dung gio mua dong thi cac moc neo My lui +1h theo gio VN,
    xem CONST['us_dst_shift']).
  * Profile volume: hang (row) = 2 tick = 0,2 gia, snap bang round(gia/0,2) giong ProfileEngine.Snap.

API chinh (xem docstring tung ham):
  load_bars, load_levels / iter_levels, build_profiles, session_table,
  zones_for_session, zones_by_session, zone_columns, flat_zones,
  vwap_series, m5_bars, mode_frame / mode_series,
  median_range, med_abs_delta, biggest_bar_so_far_in_session, bars_since_biggest_bar, zigzag,
  is_confirm_bar / confirm_bars, risk, simulate, metrics, render_markdown, control_sample, split_of.
"""
from __future__ import annotations

import math
import datetime as _dt
from typing import Optional

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------------------------
# HANG SO - moi hang so cua kernel nam o day (QD-1: khong co nguong so trong Settings cua indicator)
# ----------------------------------------------------------------------------------------------
CONST = dict(
    tick=0.1,                 # 1 tick GC = 0,1 gia
    row_ticks=2,              # 1 hang profile = 2 tick = 0,2 gia (SessionZones.RowTicks)
    gap_min=30,               # khoang trong > 30 phut giua 2 nen M1 => phien moi
    week_gap_h=30,            # khoang trong > 30 gio => tuan CME moi (cuoi tuan ~46h)
    splice_jump=20.0,         # |open - close_truoc| >= 20 gia trong gio nghi => cho noi hop dong
    splice_gap_min=(30, 150), # chi xet khoang nghi 30..150 phut (loai cuoi tuan)
    splice_ex_sessions=2,     # loai +-2 phien quanh cho noi
    va_frac=0.70,             # Value Area 70%
    hvn_smooth=5,             # lam muot +-5 hang
    hvn_min_ratio=1.5,        # FindHvn mac dinh
    hvn_gate=2.5,             # cong ti le HVN (SessionZones.MinHvnRatio)
    hvn_max=3,                # toi da 3 HVN (SessionZones.MaxHvn)
    lvn_max_ratio=0.5,        # FindLvn mac dinh
    lvn_max=2,                # toi da 2 LVN ngay
    week_lookback=3,          # HVN tuan = gop 3 tuan CME da dong
    min_bars_prof=300,        # phien < 300 nen M1 khong lam 'phien hom qua' (manh vun, vd nghi le)
    min_eu_bars=60,           # can >= 60 nen trong cua so Au de chot VA Au
    min_ib_bars=30,           # can >= 30 nen trong 19:20-20:20 de chot IB
    naked_lookback=30,        # POC cu xet trong 30 phien truoc
    naked_max=3,              # giu toi da 3 POC tran gan nhat
    thin_frac=0.20,           # phien co volume < 20% trung vi = 'thin' (du lieu mong, vd tuan dau file 90d)
    vwap_price='typical',     # VWAP = sum(typical*volume)/sum(volume), typical=(H+L+C)/3 (giong ProfileEngine.VwapAt)
    # moc gio theo 'sm' (phut ke tu 05:00 VN, da bu gio My): A 05:00-12:30, EU 12:30-19:00, US 19:00-04:00
    sm_eu_start=450, sm_us_start=840, sm_off_start=1380,
    sm_ib_start=860, sm_ib_end=920,       # IB = 19:20-20:20 VN
    us_dst_shift=True,        # True: khi My dung gio mua dong (EST), cac moc neo My (05:00, 19:00, IB) lui +1h theo gio VN.
                              #       File 90d toan mua he => khong anh huong. Dat False = moc VN co dinh nhu plan.
    u_n=50,                   # cua so trung vi u va trung vi |delta|
    cf_body_frac=0.5,         # than nen xac nhan >= 50% bien do
    m5_trend_runs=2,          # TREND: >= 2 nen M5 lien tiep dong ngoai
    m5_trend_dist=3.0,        # ... va cach canh >= 3 gia
    cost=0.2,                 # chi phi 0,2 gia/lenh (spread + truot)
    one_at_a_time=True,       # 1 lenh mo cung luc
    sl_buffer=0.3,            # SL = cau truc + 0,3 gia
    sl_floor_bars=5,          # san SL = bien do nen cao nhat 5 nen
    sl_cap=4.0,               # tran SL 4 gia
    zz_threshold=2.0,         # zigzag mac dinh 2 gia
    split_train_end='2026-09-15',  # TRAIN: ngay phien <= 2026-09-15 ; TEST: tu 2026-09-16
    # hang vung: 1 = tin nhat. fade=True: duoc fade; fade=False: nen / muc tieu, KHONG fade
    zone_roles={
        'VWAP_W': dict(rank=1, fade=True, kind='vwap'),
        'VWAP_D': dict(rank=2, fade=True, kind='vwap'),
        'VAH_EU': dict(rank=3, fade=True, kind='range_edge'),
        'VAL_EU': dict(rank=3, fade=True, kind='range_edge'),
        'POC_EU': dict(rank=4, fade=False, kind='target'),
        'IB_H': dict(rank=3, fade=True, kind='range_edge'),
        'IB_L': dict(rank=3, fade=True, kind='range_edge'),
        'VAH_Y': dict(rank=3, fade=True, kind='yday'),
        'VAL_Y': dict(rank=3, fade=True, kind='yday'),
        'POC_Y': dict(rank=4, fade=False, kind='target'),
        'HVN_D': dict(rank=5, fade=False, kind='base'),
        'HVN_W': dict(rank=5, fade=False, kind='base'),
        'LVN_D': dict(rank=9, fade=False, kind='lvn'),
        'NPOC': dict(rank=5, fade=False, kind='target'),
    },
)

PHASES = ('A', 'EU', 'US')
ZONE_COLS = ['yd_poc', 'yd_vah', 'yd_val', 'eu_poc', 'eu_vah', 'eu_val', 'ib_hi', 'ib_lo', 'vwap_d', 'vwap_w']
# ten vung dung cho entry['zone'] (control_sample map ten -> cot cua zone_columns)
ZONE_NAME2COL = {'VWAP_W': 'vwap_w', 'VWAP_D': 'vwap_d', 'VAH_EU': 'eu_vah', 'VAL_EU': 'eu_val', 'POC_EU': 'eu_poc',
                 'IB_H': 'ib_hi', 'IB_L': 'ib_lo', 'VAH_Y': 'yd_vah', 'VAL_Y': 'yd_val', 'POC_Y': 'yd_poc'}


# ----------------------------------------------------------------------------------------------
# 1. LOAD + TACH PHIEN
# ----------------------------------------------------------------------------------------------
def _us_dst_mask(t: pd.Series) -> np.ndarray:
    """True khi My dang dung gio mua he (EDT). Quy tac: CN thu 2 thang 3 07:00 UTC -> CN dau thang 11 06:00 UTC."""
    yrs = t.dt.year.to_numpy()
    tv = t.to_numpy()
    out = np.zeros(len(t), bool)
    for y in np.unique(yrs):
        d = _dt.date(int(y), 3, 8)
        d += _dt.timedelta((6 - d.weekday()) % 7)
        e = _dt.date(int(y), 11, 1)
        e += _dt.timedelta((6 - e.weekday()) % 7)
        s = np.datetime64(_dt.datetime(int(y), 3, d.day, 7))
        z = np.datetime64(_dt.datetime(int(y), 11, e.day, 6))
        out |= (yrs == y) & (tv >= s) & (tv < z)
    return out


def split_of(session_id: str) -> str:
    """'TRAIN' neu ngay phien <= 2026-09-15, nguoc lai 'TEST'."""
    return 'TRAIN' if str(session_id)[:10] <= CONST['split_train_end'] else 'TEST'


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Them cot phien/gio/phase/splice vao DataFrame M1 tho (da sort theo thoi gian). Dung chung cho load_bars va test cat df."""
    df = df.reset_index(drop=True).copy()
    t = df['datetime']
    df['t_utc'] = t
    df['t_vn'] = t + pd.Timedelta(hours=7)
    gap = t.diff().dt.total_seconds().div(60.0).to_numpy()
    gap = np.where(np.isnan(gap), 0.0, gap)
    sno = np.cumsum(gap > CONST['gap_min']).astype(np.int64)
    df['session_no'] = sno
    df['week_no'] = np.cumsum(gap > CONST['week_gap_h'] * 60).astype(np.int64)
    # ten phien = ngay cua nen cuoi; trung ten thi them hau to b, c...
    last_date = t.dt.strftime('%Y-%m-%d').groupby(sno).last()
    names, seen = [], {}
    for d in last_date.tolist():
        k = seen.get(d, 0)
        names.append(d if k == 0 else d + '-' + chr(ord('a') + k))
        seen[d] = k + 1
    df['session_id'] = np.asarray(names, dtype=object)[sno]
    # cho noi hop dong
    prev_close = df['close'].shift(1).to_numpy()
    jump = (np.abs(df['open'].to_numpy() - prev_close) >= CONST['splice_jump']) & \
           (gap >= CONST['splice_gap_min'][0]) & (gap <= CONST['splice_gap_min'][1])
    df['splice_jump'] = jump
    nS = int(sno[-1]) + 1 if len(df) else 0
    flag = np.zeros(nS, bool)
    k = CONST['splice_ex_sessions']
    for s in np.unique(sno[jump]):
        flag[max(0, s - k): min(nS, s + k + 1)] = True
    df['splice'] = flag[sno] if nS else np.zeros(0, bool)
    # gio
    vm = ((t.dt.hour * 60 + t.dt.minute + 420) % 1440).to_numpy()
    if CONST['us_dst_shift']:
        vm_adj = (vm - 60 * (~_us_dst_mask(t)).astype(int)) % 1440
    else:
        vm_adj = vm
    sm = (vm_adj - 300) % 1440
    df['vm'] = vm                      # phut trong ngay theo gio VN thuc
    df['sm'] = sm                      # phut ke tu 05:00 VN (da bu gio My)
    ph = np.where(sm < CONST['sm_eu_start'], 'A',
         np.where(sm < CONST['sm_us_start'], 'EU',
         np.where(sm < CONST['sm_off_start'], 'US', 'OFF')))
    df['phase'] = ph
    df['is_eu'] = (sm >= CONST['sm_eu_start']) & (sm < CONST['sm_us_start'])
    df['is_ib'] = (sm >= CONST['sm_ib_start']) & (sm < CONST['sm_ib_end'])
    df['is_us_open_window'] = df['is_ib']          # 19:20-20:20 VN
    df['rng'] = df['high'] - df['low']
    df['split'] = np.where(df['session_id'].str[:10] <= CONST['split_train_end'], 'TRAIN', 'TEST')
    # phien mong (volume qua thap so voi trung vi)
    n = np.bincount(sno)
    vol = np.bincount(sno, weights=df['volume'].to_numpy(float))
    good = n >= CONST['min_bars_prof']
    med = np.median(vol[good]) if good.any() else 0.0
    df['thin'] = (vol < CONST['thin_frac'] * med)[sno]
    return df


def load_bars(path: str) -> pd.DataFrame:
    """Doc file *_bars.csv (nen M1) va them cot: t_utc, t_vn, session_no (so thu tu phien), session_id (ngay cua nen cuoi),
    week_no, splice (phien dinh cho noi +-2, DUNG DE LOC, nhin 2 phien sau), splice_jump (nen ngay sau cho noi),
    phase ('A' 05:00-12:30 VN | 'EU' 12:30-19:00 | 'US' 19:00-04:00 | 'OFF'), is_us_open_window (19:20-20:20 VN),
    sm, vm, is_eu, is_ib, rng, split (TRAIN/TEST), thin (phien volume mong). Index = 0..n-1 (= pos)."""
    df = pd.read_csv(path, parse_dates=['datetime'])
    if not df['datetime'].is_monotonic_increasing:
        raise ValueError('nen khong tang theo thoi gian')
    return _enrich(df)


def session_table(df: pd.DataFrame) -> pd.DataFrame:
    """Bang moi phien: session_id, start_pos, end_pos, n, volume, week_no, t_start, t_end, splice_start (cho noi ngay DAU phien),
    splice (+-2), thin. Index = session_no."""
    sno = df['session_no'].to_numpy()
    if len(sno) == 0:
        return pd.DataFrame()
    starts = np.r_[0, np.flatnonzero(np.diff(sno)) + 1]
    ends = np.r_[starts[1:] - 1, len(sno) - 1]
    vol = np.add.reduceat(df['volume'].to_numpy(float), starts)
    return pd.DataFrame({
        'session_id': df['session_id'].to_numpy()[starts], 'start_pos': starts, 'end_pos': ends,
        'n': ends - starts + 1, 'volume': vol, 'week_no': df['week_no'].to_numpy()[starts],
        't_start': df['t_utc'].to_numpy()[starts], 't_end': df['t_utc'].to_numpy()[ends],
        'splice_start': df['splice_jump'].to_numpy()[starts], 'splice': df['splice'].to_numpy()[starts],
        'thin': df['thin'].to_numpy()[starts],
    }, index=pd.Index(sno[starts], name='session_no'))


# ----------------------------------------------------------------------------------------------
# 2. PER-LEVEL (chi load khi can) + PROFILE
# ----------------------------------------------------------------------------------------------
def iter_levels(path: str, bar_lo: Optional[int] = None, bar_hi: Optional[int] = None,
                chunksize: int = 2_000_000, usecols=('bar_idx', 'price', 'bid_vol', 'ask_vol', 'volume', 'delta')):
    """Doc file per-level theo chunk, loc bar_idx trong [bar_lo, bar_hi]. File sap theo bar_idx nen dung som khi vuot bar_hi."""
    for ch in pd.read_csv(path, usecols=list(usecols), chunksize=chunksize):
        b = ch['bar_idx'].to_numpy()
        if bar_hi is not None and b.min() > bar_hi:
            break
        m = np.ones(len(ch), bool)
        if bar_lo is not None:
            m &= b >= bar_lo
        if bar_hi is not None:
            m &= b <= bar_hi
        if m.any():
            yield ch[m]
        if bar_hi is not None and b.max() > bar_hi:
            break


def load_levels(path: str, bar_lo: Optional[int] = None, bar_hi: Optional[int] = None, **kw) -> pd.DataFrame:
    """Doc per-level cho khoang bar_idx [bar_lo, bar_hi] (gop cac chunk). Tranh goi khong tham so tren file 2 nam (583 MB)."""
    parts = list(iter_levels(path, bar_lo, bar_hi, **kw))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


class Profiles:
    """Profile volume theo (phien, hang). full[sno] = (rows_int, vol) ca phien; eu[sno] = rieng cua so Au (12:30-19:00 VN).
    rows_int * 0,2 = gia. approx=True neu dung xap xi tu nen (khong co file per-level)."""

    def __init__(self, full, eu, approx=False):
        self.full, self.eu, self.approx = full, eu, approx

    @staticmethod
    def row_price(rows):
        return np.round(np.asarray(rows, dtype=float) * (CONST['tick'] * CONST['row_ticks']), 6)


def _split_groups(s, r, v):
    """s,r,v da sap theo (s,r): tach thanh dict s -> (r, v)."""
    out = {}
    if len(s) == 0:
        return out
    cut = np.flatnonzero(np.diff(s)) + 1
    for a, b in zip(np.r_[0, cut], np.r_[cut, len(s)]):
        out[int(s[a])] = (r[a:b].copy(), v[a:b].astype(float).copy())
    return out


def build_profiles(df: pd.DataFrame, levels=None, chunksize: int = 2_000_000) -> Profiles:
    """Dung profile volume moi phien tu per-level. levels = duong dan CSV per-level (doc chunk) hoac DataFrame da load.
    levels=None => xap xi tu nen M1 (rai deu volume nen tren cac hang tu low den high) va approx=True."""
    step = CONST['tick'] * CONST['row_ticks']
    sno = df['session_no'].to_numpy()
    is_eu = df['is_eu'].to_numpy()
    full_p, eu_p = [], []

    def acc(pos, price, vol):
        row = np.rint(price / step).astype(np.int64)
        d = pd.DataFrame({'s': sno[pos], 'r': row, 'v': vol})
        full_p.append(d.groupby(['s', 'r'], sort=False)['v'].sum())
        e = is_eu[pos]
        if e.any():
            eu_p.append(d[e].groupby(['s', 'r'], sort=False)['v'].sum())

    if levels is None:
        lo = np.rint(df['low'].to_numpy() / step).astype(np.int64)
        hi = np.rint(df['high'].to_numpy() / step).astype(np.int64)
        k = hi - lo + 1
        pos = np.repeat(np.arange(len(df)), k)
        off = np.arange(k.sum()) - np.repeat(np.cumsum(k) - k, k)
        rows = lo[pos] + off
        vol = (df['volume'].to_numpy(float) / k)[pos]
        acc_rows = pd.DataFrame({'s': sno[pos], 'r': rows, 'v': vol})
        full_p.append(acc_rows.groupby(['s', 'r'], sort=False)['v'].sum())
        e = is_eu[pos]
        eu_p.append(acc_rows[e].groupby(['s', 'r'], sort=False)['v'].sum())
        approx = True
    else:
        approx = False
        imap = pd.Index(df['bar_idx'].to_numpy())
        if isinstance(levels, str):
            chunks = pd.read_csv(levels, usecols=['bar_idx', 'price', 'volume'], chunksize=chunksize)
            hi_bar = df['bar_idx'].max()
        else:
            chunks = [levels]
            hi_bar = None
        for ch in chunks:
            if hi_bar is not None and ch['bar_idx'].min() > hi_bar:
                break
            pos = imap.get_indexer(ch['bar_idx'].to_numpy())
            ok = pos >= 0
            if not ok.any():
                continue
            acc(pos[ok], ch['price'].to_numpy()[ok], ch['volume'].to_numpy(float)[ok])

    def fin(parts):
        if not parts:
            return {}
        s = pd.concat(parts).groupby(level=[0, 1]).sum().sort_index()
        idx = s.index
        return _split_groups(idx.get_level_values(0).to_numpy(), idx.get_level_values(1).to_numpy(), s.to_numpy())

    return Profiles(fin(full_p), fin(eu_p), approx)


def _agg_profiles(parts):
    """Cong nhieu profile (rows, vol) thanh mot."""
    parts = [p for p in parts if p is not None and len(p[0])]
    if not parts:
        return None
    r = np.concatenate([p[0] for p in parts])
    v = np.concatenate([p[1] for p in parts])
    u, inv = np.unique(r, return_inverse=True)
    return u, np.bincount(inv, weights=v)


# ----------------------------------------------------------------------------------------------
# 3. VUNG: VA / HVN / LVN (port ProfileEngine)
# ----------------------------------------------------------------------------------------------
def value_area(prices, w, frac: float = None):
    """Port ProfileEngine.ValueArea: bat dau tu POC (hang volume lon nhat, hang thap nhat neu hoa), moi buoc mo rong 2 hang
    moi ben, chon ben co tong 2 hang lon hon (hoa => ben tren), dung khi >= frac tong volume. Tra (poc, vah, val).
    Chay tren cac hang DANG CO (khong lap hang trong)."""
    frac = CONST['va_frac'] if frac is None else frac
    w = [float(x) for x in w]
    n = len(w)
    if n == 0:
        return (math.nan,) * 3
    tot = sum(w)
    if tot <= 0:
        return (math.nan,) * 3
    poc = max(range(n), key=lambda i: (w[i], -i))
    acc, target, lo, hi = w[poc], tot * frac, poc, poc
    while acc < target and (lo > 0 or hi < n - 1):
        up = (w[hi + 1] if hi < n - 1 else 0) + (w[hi + 2] if hi < n - 2 else 0)
        dn = (w[lo - 1] if lo > 0 else 0) + (w[lo - 2] if lo > 1 else 0)
        if hi >= n - 1:
            acc += dn; lo = max(0, lo - 2)
        elif lo <= 0:
            acc += up; hi = min(n - 1, hi + 2)
        elif up >= dn:
            acc += up; hi = min(n - 1, hi + 2)
        else:
            acc += dn; lo = max(0, lo - 2)
    return float(prices[poc]), float(prices[hi]), float(prices[lo])


def _smooth(w, k):
    n = len(w)
    cs = np.concatenate([[0.0], np.cumsum(w)])
    a = np.maximum(0, np.arange(n) - k)
    z = np.minimum(n - 1, np.arange(n) + k)
    return (cs[z + 1] - cs[a]) / (z - a + 1)


def find_hvn(prices, w, tick=None, smooth=None, min_ratio=None, min_sep_ticks=0):
    """Port ProfileEngine.FindHvn: dinh cuc bo cua phan bo da lam muot (+-5 hang), giu dinh >= min_ratio*trung binh, gop dinh qua
    gan (giu dinh manh hon; khoang cach toi thieu = 8% do rong profile, kep 20..120 tick). Tra [(gia, ti le)] manh truoc."""
    tick = CONST['tick'] if tick is None else tick
    smooth = CONST['hvn_smooth'] if smooth is None else smooth
    min_ratio = CONST['hvn_min_ratio'] if min_ratio is None else min_ratio
    prices = np.asarray(prices, float); w = np.asarray(w, float)
    n = len(w)
    if n < 3:
        return []
    avg = w.mean()
    if avg <= 0:
        return []
    if min_sep_ticks <= 0:
        min_sep_ticks = min(120.0, max(20.0, (prices[-1] - prices[0]) / tick * 0.08))
    sm = _smooth(w, smooth)
    i = np.arange(1, n - 1)
    ok = (sm[i] >= sm[i - 1]) & (sm[i] >= sm[i + 1]) & (sm[i] >= min_ratio * avg)
    pk = i[ok]
    pk = pk[np.argsort(-sm[pk], kind='stable')]
    res = []
    for j in pk:
        if all(abs(prices[j] - p) / tick >= min_sep_ticks for p, _ in res):
            res.append((float(prices[j]), float(sm[j] / avg)))
    return res


def find_lvn(prices, w, tick=None, smooth=None, max_ratio=None, min_sep_ticks=0):
    """Port ProfileEngine.FindLvn: day cuc bo cua phan bo lam muot, giu day <= max_ratio*trung binh, yeu nhat truoc.
    Tra [(gia, ti le)]."""
    tick = CONST['tick'] if tick is None else tick
    smooth = CONST['hvn_smooth'] if smooth is None else smooth
    max_ratio = CONST['lvn_max_ratio'] if max_ratio is None else max_ratio
    prices = np.asarray(prices, float); w = np.asarray(w, float)
    n = len(w)
    if n < 3:
        return []
    avg = w.mean()
    if avg <= 0:
        return []
    if min_sep_ticks <= 0:
        min_sep_ticks = min(120.0, max(20.0, (prices[-1] - prices[0]) / tick * 0.08))
    sm = _smooth(w, smooth)
    i = np.arange(1, n - 1)
    ok = (sm[i] <= sm[i - 1]) & (sm[i] <= sm[i + 1]) & (sm[i] <= max_ratio * avg)
    tr = i[ok]
    tr = tr[np.argsort(sm[tr], kind='stable')]
    res = []
    for j in tr:
        if all(abs(prices[j] - p) / tick >= min_sep_ticks for p, _ in res):
            res.append((float(prices[j]), float(sm[j] / avg)))
    return res


class _Ctx:
    """Du lieu dung chung de tinh vung (mang numpy + bang phien + cache). Tao 1 lan cho moi (df, prof)."""

    def __init__(self, df, prof: Profiles):
        self.df, self.prof = df, prof
        self.st = session_table(df)
        self.hi = df['high'].to_numpy(float)
        self.lo = df['low'].to_numpy(float)
        self.sm = df['sm'].to_numpy()
        self.sno = df['session_no'].to_numpy()
        self.sid2no = {s: int(k) for k, s in zip(self.st.index, self.st['session_id'])}
        self.splice_starts = self.st.index[self.st['splice_start'].to_numpy()].to_numpy()
        self.cache = {}
        self.touch = {}

    def resolve(self, session_id):
        if isinstance(session_id, (int, np.integer)):
            return int(session_id)
        return self.sid2no[session_id]

    def last_splice(self, sno):
        s = self.splice_starts[self.splice_starts <= sno]
        return int(s.max()) if len(s) else -1

    def va(self, q):
        k = ('va', q)
        if k not in self.cache:
            r, v = self.prof.full.get(q, (None, None))
            self.cache[k] = None if r is None else value_area(Profiles.row_price(r), v)
        return self.cache[k]

    def day_nodes(self, q):
        k = ('dn', q)
        if k not in self.cache:
            r, v = self.prof.full[q]
            p = Profiles.row_price(r)
            hv = [x for x in find_hvn(p, v)[:CONST['hvn_max']] if x[1] >= CONST['hvn_gate']]
            lv = find_lvn(p, v)[:CONST['lvn_max']]
            self.cache[k] = (hv, lv)
        return self.cache[k]

    def week_hvn(self, sno, sp):
        W = int(self.st['week_no'].loc[sno])
        k = ('wk', W, sp)
        if k not in self.cache:
            st = self.st
            wk = st['week_no'].to_numpy()
            inwin = (wk >= W - CONST['week_lookback']) & (wk <= W - 1)
            m = inwin & (st.index.to_numpy() >= max(sp, 0)) & (st['n'].to_numpy() >= CONST['min_bars_prof'])
            snos = [int(x) for x in st.index[m] if int(x) in self.prof.full]
            first_win = st.index[wk >= W - CONST['week_lookback']].min()
            partial = bool(sp > first_win)
            a = _agg_profiles([self.prof.full[x] for x in snos])
            if a is None:
                self.cache[k] = None
            else:
                p = Profiles.row_price(a[0])
                hv = [x for x in find_hvn(p, a[1])[:CONST['hvn_max']] if x[1] >= CONST['hvn_gate']]
                self.cache[k] = dict(hvn=hv, n_sessions=len(snos), partial=partial)
        return self.cache[k]

    def touch_pos(self, q):
        """Vi tri nen DAU TIEN sau phien q ma gia cham POC cua q (None neu chua)."""
        if q in self.touch:
            return self.touch[q]
        va = self.va(q)
        res = None
        if va is not None:
            poc = va[0]
            a = int(self.st['end_pos'].loc[q]) + 1
            n = len(self.hi)
            win = 4000
            while a < n:
                b = min(n, a + win)
                m = (self.lo[a:b] <= poc) & (self.hi[a:b] >= poc)
                if m.any():
                    res = a + int(np.argmax(m))
                    break
                a = b
                win *= 2
        self.touch[q] = res
        return res


def _zones(ctx: _Ctx, sno: int, as_of: Optional[int], naked: bool = True):
    st = ctx.st
    srow = st.loc[sno]
    sp0, ep = int(srow['start_pos']), int(srow['end_pos'])
    if as_of is not None:
        if as_of < sp0:
            raise ValueError('as_of nam truoc phien')
        as_of = min(as_of, ep)
    sp = ctx.last_splice(sno)
    z = dict(session_no=int(sno), session_id=srow['session_id'], as_of=as_of, splice_in_window=bool(sp > 0),
             yday=None, va_eu=None, ib=None, hvn_day=[], lvn_day=[], hvn_week=None, naked=[],
             rank={k: v['rank'] for k, v in CONST['zone_roles'].items()},
             roles={k: ('fade' if v['fade'] else 'base') for k, v in CONST['zone_roles'].items()})
    # --- VA hom qua + HVN/LVN ngay: phien truoc DU (>= min_bars), khong bi cho noi chen giua ---
    q = sno - 1
    while q >= 0 and (int(st['n'].loc[q]) < CONST['min_bars_prof'] or q not in ctx.prof.full):
        q -= 1
    if q >= 0 and q >= sp:
        poc, vah, val = ctx.va(q)
        z['yday'] = dict(poc=poc, vah=vah, val=val, session_no=int(q), session_id=st['session_id'].loc[q])
        z['hvn_day'], z['lvn_day'] = ctx.day_nodes(q)
    # --- HVN tuan (3 tuan CME da dong) ---
    w = ctx.week_hvn(sno, sp)
    if w is not None:
        z['hvn_week'] = w
    # --- VA Au: chot khi sm >= 840 (19:00 VN) ---
    smv = ctx.sm[sp0:ep + 1]
    ready = np.flatnonzero(smv >= CONST['sm_us_start'])
    ready_pos = sp0 + int(ready[0]) if len(ready) else None
    if ready_pos is not None and sno in ctx.prof.eu:
        r, v = ctx.prof.eu[sno]
        n_eu = int(((smv >= CONST['sm_eu_start']) & (smv < CONST['sm_us_start'])).sum())
        if n_eu >= CONST['min_eu_bars'] and (as_of is None or as_of >= ready_pos):
            poc, vah, val = value_area(Profiles.row_price(r), v)
            z['va_eu'] = dict(poc=poc, vah=vah, val=val, ready_pos=ready_pos)
    # --- IB 19:20-20:20 VN: chot khi sm >= 920 ---
    ib_m = (smv >= CONST['sm_ib_start']) & (smv < CONST['sm_ib_end'])
    rd = np.flatnonzero(smv >= CONST['sm_ib_end'])
    ib_ready = sp0 + int(rd[0]) if len(rd) else None
    if ib_ready is not None and int(ib_m.sum()) >= CONST['min_ib_bars'] and (as_of is None or as_of >= ib_ready):
        z['ib'] = dict(high=float(ctx.hi[sp0:ep + 1][ib_m].max()), low=float(ctx.lo[sp0:ep + 1][ib_m].min()), ready_pos=ib_ready)
    # --- naked POC ---
    if naked:
        cand = []
        for qq in range(max(sp, sno - CONST['naked_lookback'], 0), sno):
            if int(st['n'].loc[qq]) < CONST['min_bars_prof'] or qq not in ctx.prof.full:
                continue
            tp = ctx.touch_pos(qq)
            if tp is not None and tp < sp0:
                continue                                  # da bi cham truoc dau phien nay
            if as_of is not None and tp is not None and tp <= as_of:
                continue                                  # bi cham truoc thoi diem as_of
            if as_of is not None:
                tp = None                                 # chua thay cham tai as_of (khong lo vi tri cham tuong lai)
            cand.append(dict(price=ctx.va(qq)[0], session_no=int(qq), session_id=st['session_id'].loc[qq], touch_pos=tp))
        z['naked'] = cand[-CONST['naked_max']:] if as_of is not None else cand
    return z


def zones_for_session(df, session_id, prof: Profiles, as_of: Optional[int] = None, ctx: Optional[_Ctx] = None) -> dict:
    """Cac vung cua mot phien, CHI tu du lieu truoc thoi diem can.
    session_id: ten phien (str 'YYYY-MM-DD') hoac session_no (int).
    as_of: vi tri (pos) cua nen DONG cuoi cung duoc phep dung. Vung chua chot tai as_of => None.
           as_of=None => tra gia tri cuoi phien kem 'ready_pos' (vi tri nen dau tien duoc phep dung) de nguoi goi tu loc.
    Tra dict:
      yday      {poc,vah,val,...} VA phien hom qua (profile volume row 2 tick, VA 70%)       | None neu thieu/dinh cho noi
      va_eu     {poc,vah,val,ready_pos} VA cua so Au 12:30-19:00 VN, CHOT luc 19:00 VN         | None truoc do
      ib        {high,low,ready_pos} IB 19:20-20:20 VN, chot sau 20:20                         | None truoc do
      hvn_day   [(gia, ti_le)] toi da 3, cong ti le >= 2,5 (tu profile hom qua)
      lvn_day   [(gia, ti_le)] toi da 2
      hvn_week  {hvn:[(gia,ti_le)], n_sessions, partial} gop 3 tuan CME da dong (loai phan truoc cho noi)
      naked     [{price, touch_pos,...}] POC cu chua bi cham (as_of: toi da 3 gan nhat; as_of=None: tat ca ung vien,
                nguoi goi tu loc touch_pos > vi_tri_hien_tai)
      rank/roles hang vung: VWAP tuan 1, VWAP ngay 2, canh VA Au/IB = canh range (fade), HVN = nen/muc tieu (KHONG fade).
    VWAP ngay/tuan o ham vwap_series (cong don theo tung nen)."""
    ctx = ctx or _Ctx(df, prof)
    return _zones(ctx, ctx.resolve(session_id), as_of)


def zones_by_session(df, prof: Profiles, naked: bool = True) -> dict:
    """{session_no: zones_for_session(as_of=None)} cho moi phien."""
    ctx = _Ctx(df, prof)
    return {int(s): _zones(ctx, int(s), None, naked) for s in ctx.st.index}


def zone_columns(df, prof: Profiles, ctx: Optional[_Ctx] = None) -> pd.DataFrame:
    """Vung dang cot, canh hang voi df, KHONG nhin truoc: yd_poc/yd_vah/yd_val (suot phien), eu_poc/eu_vah/eu_val (NaN truoc
    19:00 VN), ib_hi/ib_lo (NaN truoc 20:20 VN), vwap_d, vwap_w (cong don den nen hien tai, gom nen hien tai)."""
    ctx = ctx or _Ctx(df, prof)
    n = len(df)
    out = {c: np.full(n, np.nan) for c in ZONE_COLS}
    for s in ctx.st.index:
        z = _zones(ctx, int(s), None, naked=False)
        a, b = int(ctx.st['start_pos'].loc[s]), int(ctx.st['end_pos'].loc[s]) + 1
        if z['yday']:
            out['yd_poc'][a:b], out['yd_vah'][a:b], out['yd_val'][a:b] = z['yday']['poc'], z['yday']['vah'], z['yday']['val']
        if z['va_eu']:
            r = z['va_eu']['ready_pos']
            out['eu_poc'][r:b], out['eu_vah'][r:b], out['eu_val'][r:b] = z['va_eu']['poc'], z['va_eu']['vah'], z['va_eu']['val']
        if z['ib']:
            r = z['ib']['ready_pos']
            out['ib_hi'][r:b], out['ib_lo'][r:b] = z['ib']['high'], z['ib']['low']
    vw = vwap_series(df)
    out['vwap_d'], out['vwap_w'] = vw['vwap_d'].to_numpy(), vw['vwap_w'].to_numpy()
    return pd.DataFrame(out, index=df.index)


def flat_zones(z: dict, vwap_d: float, vwap_w: float, pos: Optional[int] = None) -> list:
    """Danh sach phang cac vung tai mot thoi diem: [{name, price, rank, fade, kind}] sap theo rank. z = zones_for_session(as_of=pos).
    pos duoc dung de loc naked POC (touch_pos > pos) khi z lay voi as_of=None."""
    R = CONST['zone_roles']
    out = []

    def add(name, price):
        if price is not None and price == price:
            r = R[name]
            out.append(dict(name=name, price=float(price), rank=r['rank'], fade=r['fade'], kind=r['kind']))
    add('VWAP_W', vwap_w); add('VWAP_D', vwap_d)
    if z.get('va_eu'):
        add('VAH_EU', z['va_eu']['vah']); add('VAL_EU', z['va_eu']['val']); add('POC_EU', z['va_eu']['poc'])
    if z.get('ib'):
        add('IB_H', z['ib']['high']); add('IB_L', z['ib']['low'])
    if z.get('yday'):
        add('VAH_Y', z['yday']['vah']); add('VAL_Y', z['yday']['val']); add('POC_Y', z['yday']['poc'])
    for p, _ in z.get('hvn_day') or []:
        add('HVN_D', p)
    if z.get('hvn_week'):
        for p, _ in z['hvn_week']['hvn']:
            add('HVN_W', p)
    for p, _ in z.get('lvn_day') or []:
        add('LVN_D', p)
    nk = z.get('naked') or []
    if pos is not None and z.get('as_of') is None:
        nk = [x for x in nk if x['touch_pos'] is None or x['touch_pos'] > pos][-CONST['naked_max']:]
    for x in nk:
        add('NPOC', x['price'])
    return sorted(out, key=lambda d: d['rank'])


# ----------------------------------------------------------------------------------------------
# 4. VWAP
# ----------------------------------------------------------------------------------------------
def vwap_series(df: pd.DataFrame) -> pd.DataFrame:
    """VWAP ngay (reset moi phien CME) va VWAP tuan (neo phien dau tien sau khoang trong > 30 gio), cong don tu nen
    dau moc DEN NEN HIEN TAI (gom nen hien tai, nen da dong). Gia = typical price (H+L+C)/3 x volume (giong ProfileEngine.VwapAt).
    Neu tich luy volume = 0 => dung close. Tra DataFrame cot vwap_d, vwap_w."""
    tp = ((df['high'] + df['low'] + df['close']) / 3.0).to_numpy(float)
    v = df['volume'].to_numpy(float)
    cl = df['close'].to_numpy(float)

    def cum(key):
        k = df[key].to_numpy()
        pv = pd.Series(tp * v).groupby(k).cumsum().to_numpy()
        vv = pd.Series(v).groupby(k).cumsum().to_numpy()
        return np.where(vv > 0, pv / np.where(vv > 0, vv, 1.0), cl)
    return pd.DataFrame({'vwap_d': cum('session_no'), 'vwap_w': cum('week_no')}, index=df.index)


# ----------------------------------------------------------------------------------------------
# 5. M5 + CHE DO
# ----------------------------------------------------------------------------------------------
def m5_bars(df: pd.DataFrame, zcols: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Gop M1 -> M5 theo moc phut chia het cho 5 (UTC), khong gop xuyen phien. Cot: session_no, t5_start, t5_end (= luc nen dong),
    open/high/low/close, volume, delta, n1, first_pos, last_pos. Neu co zcols (zone_columns): them band_hi/band_lo/band_src
    (VA Au neu da chot, nguoc lai IB, nguoc lai NaN), out (+1 dong tren canh tren, -1 dong duoi canh duoi, 0 trong/khong co band),
    out_dist (khoang cach close vuot canh, >=0). Nen M5 chi 'da dong' khi t5_end <= gio mo nen M1 dang xet."""
    t5 = df['t_utc'].dt.floor('5min')
    key = [df['session_no'].to_numpy(), t5.to_numpy()]
    g = df.groupby(key, sort=True)
    m = pd.DataFrame({
        'open': g['open'].first(), 'high': g['high'].max(), 'low': g['low'].min(), 'close': g['close'].last(),
        'volume': g['volume'].sum(), 'delta': g['delta'].sum(), 'n1': g['open'].size(),
    })
    m.index.names = ['session_no', 't5_start']
    gp = pd.Series(np.arange(len(df))).groupby(key, sort=True)
    m['first_pos'], m['last_pos'] = gp.first().to_numpy(), gp.last().to_numpy()
    m = m.reset_index()
    m['t5_end'] = m['t5_start'] + pd.Timedelta(minutes=5)
    if zcols is not None:
        lp = m['last_pos'].to_numpy()
        eh, el = zcols['eu_vah'].to_numpy()[lp], zcols['eu_val'].to_numpy()[lp]
        ih, il = zcols['ib_hi'].to_numpy()[lp], zcols['ib_lo'].to_numpy()[lp]
        use_eu = ~np.isnan(eh)
        bh = np.where(use_eu, eh, ih)
        bl = np.where(use_eu, el, il)
        m['band_hi'], m['band_lo'] = bh, bl
        m['band_src'] = np.where(use_eu, 'va_eu', np.where(~np.isnan(ih), 'ib', ''))
        c = m['close'].to_numpy()
        with np.errstate(invalid='ignore'):
            up = c > bh
            dn = c < bl
        m['out'] = np.where(up, 1, np.where(dn, -1, 0))
        m['out_dist'] = np.where(up, c - bh, np.where(dn, bl - c, 0.0))
    return m


def mode_frame(df: pd.DataFrame, zcols: pd.DataFrame, m5: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Che do theo tung nen M1 (plan 2.1 khoi 2), chi dung nen M5 DA DONG truoc gio mo nen M1 hien tai va cung phien.
    Band = VA Au (sau 19:00 VN), chua co thi IB (sau 20:20 VN); chua co ca hai => 'NA'.
      BALANCE  : chua co nen M5 nao dong ngoai band (hoac nen M5 dong NGOAI roi dong LAI TRONG band => cu pha hut, ve BALANCE)
      BREAK_UP / BREAK_DN : nen M5 gan nhat dong ngoai band phia tren/duoi, chua du dieu kien TREND (= 'vua pha')
      TREND_UP / TREND_DN : >= 2 nen M5 LIEN TIEP dong ngoai CUNG phia va nen gan nhat cach canh >= 3 gia
    Cot tra ve: mode, band_hi, band_lo, band_src, run (so nen M5 lien tiep dong ngoai), had_break (da tung dong ngoai trong phien),
    break_side (+1/-1/0), last_out_t (gio dong cua nen M5 ngoai gan nhat)."""
    m = m5 if m5 is not None and 'out' in m5 else m5_bars(df, zcols)
    k = len(m)
    mode = np.empty(k, object)
    run = np.zeros(k, int)
    hb = np.zeros(k, bool)
    side = np.zeros(k, int)
    lot = np.full(k, np.datetime64('NaT'), 'datetime64[ns]')
    s_prev, r, prev_side, had, lt = -1, 0, 0, False, np.datetime64('NaT')
    sn, bsrc = m['session_no'].to_numpy(), m['band_src'].to_numpy()
    out, dist, te = m['out'].to_numpy(), m['out_dist'].to_numpy(), m['t5_end'].to_numpy()
    TR, TD = CONST['m5_trend_runs'], CONST['m5_trend_dist']
    for j in range(k):
        if sn[j] != s_prev:
            s_prev, r, prev_side, had, lt = sn[j], 0, 0, False, np.datetime64('NaT')
        if bsrc[j] == '':
            mode[j] = 'NA'
            r = 0
            prev_side = 0
        elif out[j] == 0:
            mode[j] = 'BALANCE'
            r = 0
            prev_side = 0
        else:
            r = r + 1 if out[j] == prev_side else 1
            prev_side = out[j]
            had = True
            lt = te[j]
            sfx = 'UP' if out[j] > 0 else 'DN'
            mode[j] = ('TREND_' if (r >= TR and dist[j] >= TD) else 'BREAK_') + sfx
        run[j], hb[j], side[j], lot[j] = r, had, prev_side, lt
    mf = pd.DataFrame({'mode': mode, 'band_hi': m['band_hi'].to_numpy(), 'band_lo': m['band_lo'].to_numpy(),
                       'band_src': bsrc, 'run': run, 'had_break': hb, 'break_side': side, 'last_out_t': lot})
    # anh xa sang M1: nen M5 cuoi cung co t5_end <= t_mo_nen M1 va cung phien
    t1 = df['t_utc'].to_numpy()
    j = np.searchsorted(te, t1, side='right') - 1
    ok = (j >= 0) & (sn[np.maximum(j, 0)] == df['session_no'].to_numpy())
    jj = np.where(ok, j, 0)
    res = mf.iloc[jj].reset_index(drop=True)
    res['mode'] = np.where(ok, res['mode'], 'NA')
    res['run'] = np.where(ok, res['run'], 0).astype(int)
    res['had_break'] = np.where(ok, res['had_break'], False).astype(bool)
    res['break_side'] = np.where(ok, res['break_side'], 0).astype(int)
    res['band_src'] = np.where(ok, res['band_src'], '')
    res.loc[~ok, ['band_hi', 'band_lo']] = np.nan
    res.index = df.index
    return res


def mode_series(df: pd.DataFrame, zones: pd.DataFrame, m5: Optional[pd.DataFrame] = None) -> pd.Series:
    """Series che do moi nen M1: 'BALANCE','BREAK_UP','BREAK_DN','TREND_UP','TREND_DN','NA'. zones = zone_columns(...). Xem mode_frame."""
    return mode_frame(df, zones, m5)['mode']


# ----------------------------------------------------------------------------------------------
# 6. HELPERS
# ----------------------------------------------------------------------------------------------
def median_range(df: pd.DataFrame, n: Optional[int] = None) -> pd.Series:
    """u = trung vi bien do (high-low) cua n nen gan nhat, GOM nen hien tai (da dong). Can toi thieu 10 nen. Chay xuyen phien."""
    n = n or CONST['u_n']
    return (df['high'] - df['low']).rolling(n, min_periods=10).median()


def med_abs_delta(df: pd.DataFrame, n: Optional[int] = None) -> pd.Series:
    """Trung vi |delta| cua n nen gan nhat (gom nen hien tai)."""
    n = n or CONST['u_n']
    return df['delta'].abs().rolling(n, min_periods=10).median()


def _biggest(df):
    r = (df['high'] - df['low']).to_numpy(float)
    s = df['session_no'].to_numpy()
    pos = np.arange(len(r))
    cm = pd.Series(r).groupby(s).cummax().to_numpy()
    prev = np.r_[-np.inf, cm[:-1]]
    first = np.r_[True, s[1:] != s[:-1]]
    new = first | (r > prev)
    p = pd.Series(np.where(new, pos, np.nan)).groupby(s).ffill().to_numpy()
    return cm, p.astype(int)


def biggest_bar_so_far_in_session(df: pd.DataFrame) -> pd.DataFrame:
    """Nen M1 co bien do lon nhat TINH DEN NEN HIEN TAI trong phien (nen dau tien neu hoa). Cot: big_range, big_pos."""
    cm, p = _biggest(df)
    return pd.DataFrame({'big_range': cm, 'big_pos': p}, index=df.index)


def bars_since_biggest_bar(df: pd.DataFrame) -> pd.Series:
    """So nen ke tu nen dai nhat phien (tinh den nen hien tai): 0 = chinh nen hien tai la nen dai nhat. 'Trong 3 nen sau nen dai
    nhat' <=> 1 <= gia_tri <= 3."""
    _, p = _biggest(df)
    return pd.Series(np.arange(len(df)) - p, index=df.index)


def zigzag(df: pd.DataFrame, threshold_price: Optional[float] = None, by_session: bool = True) -> list:
    """Zigzag KHONG nhin truoc: dinh/day chi duoc xac nhan khi gia da di nguoc >= nguong tu cuc tri. Tra list dict
    {pos, price, kind ('H'|'L'), confirm_pos}; chi duoc dung tu nen confirm_pos tro di (nen confirm_pos dong). Reset moi phien."""
    thr = CONST['zz_threshold'] if threshold_price is None else threshold_price
    hi, lo = df['high'].to_numpy(float), df['low'].to_numpy(float)
    sn = df['session_no'].to_numpy()
    out = []
    n = len(hi)
    state = 0
    hv = hp = lv = lp = 0
    for j in range(n):
        if j == 0 or (by_session and sn[j] != sn[j - 1]):
            state = 0
            hv, hp, lv, lp = hi[j], j, lo[j], j
            continue
        if state == 0:
            if hi[j] > hv:
                hv, hp = hi[j], j
            if lo[j] < lv:
                lv, lp = lo[j], j
            if hv - lv >= thr:
                if lp <= hp:      # day truoc dinh => xac nhan day, dang len
                    out.append(dict(pos=lp, price=float(lv), kind='L', confirm_pos=j))
                    state = 1
                    hv, hp = (hi[j] if lp < j else -np.inf), j     # day+dinh cung 1 nen: khong biet thu tu => bat dau tu nen sau
                else:
                    out.append(dict(pos=hp, price=float(hv), kind='H', confirm_pos=j))
                    state = -1
                    lv, lp = (lo[j] if hp < j else np.inf), j
        elif state == 1:          # dang len, theo doi dinh
            if hi[j] > hv:
                hv, hp = hi[j], j
            if hv - lo[j] >= thr:
                out.append(dict(pos=hp, price=float(hv), kind='H', confirm_pos=j))
                state = -1
                lv, lp = (lo[j] if hp < j else np.inf), j
        else:                     # dang xuong, theo doi day
            if lo[j] < lv:
                lv, lp = lo[j], j
            if hi[j] - lv >= thr:
                out.append(dict(pos=lp, price=float(lv), kind='L', confirm_pos=j))
                state = 1
                hv, hp = (hi[j] if lp < j else -np.inf), j
    return out


def is_confirm_bar(row, side: int, med_abs_delta_value: float) -> bool:
    """Nen xac nhan CF theo chieu side (+1 buy / -1 sell), plan muc 3: dong theo chieu side, than >= 50% bien do,
    delta cung dau, |delta| >= trung vi |delta| 50 nen."""
    rng = row['high'] - row['low']
    if rng <= 0 or med_abs_delta_value != med_abs_delta_value:
        return False
    body = (row['close'] - row['open']) * side
    return bool(body > 0 and body >= CONST['cf_body_frac'] * rng and row['delta'] * side > 0
                and abs(row['delta']) >= med_abs_delta_value)


def confirm_bars(df: pd.DataFrame, side: int, mad: Optional[pd.Series] = None) -> pd.Series:
    """Ban vector hoa cua is_confirm_bar cho ca df (bool Series)."""
    mad = med_abs_delta(df) if mad is None else mad
    rng = (df['high'] - df['low']).to_numpy(float)
    body = (df['close'] - df['open']).to_numpy(float) * side
    with np.errstate(invalid='ignore'):
        ok = (rng > 0) & (body > 0) & (body >= CONST['cf_body_frac'] * rng) & (df['delta'].to_numpy(float) * side > 0) \
            & (df['delta'].abs().to_numpy(float) >= mad.to_numpy(float))
    return pd.Series(ok, index=df.index)


# ----------------------------------------------------------------------------------------------
# 7. RISK + SIMULATE
# ----------------------------------------------------------------------------------------------
def risk(df: pd.DataFrame, idx: int, side: int, struct_price: float, rr: float = 2.0, entry: Optional[float] = None):
    """SL lai (plan 2.1 khoi 4): SL = struct_price -/+ 0,3 gia (struct_price = cuc tri cau truc: max(rau nen CF, mep xa vung);
    buy: gia THAP hon, sell: gia CAO hon). SAN: khoang SL >= bien do nen M1 cao nhat 5 nen gan nhat (gom idx). TRAN: khoang SL
    > 4 gia => None (bo lenh). Entry mac dinh = close[idx]. TP = entry +/- rr * khoang SL. SL lam tron ra xa theo tick 0,1.
    Tra dict {entry, sl, tp, risk, floor_applied} hoac None."""
    ent = float(df['close'].iloc[idx]) if entry is None else float(entry)
    tick = CONST['tick']
    raw = struct_price - side * CONST['sl_buffer']
    d = (ent - raw) * side
    k = CONST['sl_floor_bars']
    seg = df.iloc[max(0, idx - k + 1): idx + 1]
    floor = float((seg['high'] - seg['low']).max())
    fl = False
    if d < floor:
        d, fl = floor, True
    if d <= 0:
        return None
    sl = ent - side * d
    sl = (math.floor(sl / tick + 1e-9) if side > 0 else math.ceil(sl / tick - 1e-9)) * tick
    sl = round(sl, 6)
    d = (ent - sl) * side
    if d > CONST['sl_cap'] + 1e-9 or d <= 0:
        return None
    return dict(entry=ent, sl=sl, tp=round(ent + side * rr * d, 6), risk=d, floor_applied=fl)


def simulate(df: pd.DataFrame, entries: list, one_at_a_time: Optional[bool] = None, cost: Optional[float] = None,
             max_hold_bars: Optional[int] = None) -> pd.DataFrame:
    """Mo phong SL/TP tren M1. entries = [dict(idx, side(+1/-1), entry, sl, tp, setup, zone, note)]; idx = pos nen vao (vao o gia
    entry, thuong la close[idx]); xet tu nen idx+1. Nen cham CA SL va TP => tinh SL. R thuc = (side*(exit-entry) - cost)/|entry-sl|
    (cost 0,2 gia/lenh). outcome: TP / SL / OPEN (het du lieu chua cham) / TIME (neu max_hold_bars). Thoat tai dung muc SL/TP.
    one_at_a_time (mac dinh CONST): bo lenh moi neu con lenh mo (lenh moi chi duoc vao khi idx >= exit_idx cua lenh truoc).
    Tra DataFrame moi lenh da chay (lenh bi bo khong co mat) + cot: outcome, exit_idx, exit_price, r, pts, hold_bars,
    t_utc, t_vn, session_id, phase, month, split."""
    one = CONST['one_at_a_time'] if one_at_a_time is None else one_at_a_time
    cost = CONST['cost'] if cost is None else cost
    hi, lo, cl = df['high'].to_numpy(float), df['low'].to_numpy(float), df['close'].to_numpy(float)
    n = len(hi)
    rows = []
    busy_until = -1
    for e in sorted(entries, key=lambda x: x['idx']):
        i, s = int(e['idx']), int(e['side'])
        ent, sl, tp = float(e['entry']), float(e['sl']), float(e['tp'])
        if one and i < busy_until:
            continue
        risk_pts = (ent - sl) * s
        if risk_pts <= 0 or (tp - ent) * s <= 0:
            raise ValueError('SL/TP sai phia: %r' % (e,))
        out, ex_i, ex_p = 'OPEN', n - 1, float(cl[-1])
        lim = i + 1 + max_hold_bars if max_hold_bars else n
        a = i + 1
        win = 512
        while a < min(n, lim):
            b = min(n, a + win, lim)
            if s > 0:
                hs, ht = lo[a:b] <= sl, hi[a:b] >= tp
            else:
                hs, ht = hi[a:b] >= sl, lo[a:b] <= tp
            hit = hs | ht
            if hit.any():
                k = int(np.argmax(hit))
                ex_i = a + k
                if hs[k]:
                    out, ex_p = 'SL', sl          # cung nen => SL
                else:
                    out, ex_p = 'TP', tp
                break
            if max_hold_bars and b >= lim:
                out, ex_i, ex_p = 'TIME', b - 1, float(cl[b - 1])
                break
            a = b
            win *= 2
        pts = s * (ex_p - ent) - cost
        r = dict(e)
        r.update(outcome=out, exit_idx=int(ex_i), exit_price=float(ex_p), pts=pts, r=pts / risk_pts,
                 hold_bars=int(ex_i - i), risk_pts=risk_pts)
        rows.append(r)
        busy_until = ex_i if out != 'OPEN' else n + 1
    t = pd.DataFrame(rows)
    if len(t):
        idx = t['idx'].to_numpy()
        t['t_utc'] = df['t_utc'].to_numpy()[idx]
        t['t_vn'] = df['t_vn'].to_numpy()[idx]
        t['session_id'] = df['session_id'].to_numpy()[idx]
        t['phase'] = df['phase'].to_numpy()[idx]
        t['split'] = df['split'].to_numpy()[idx]
        t['month'] = pd.to_datetime(t['t_utc']).dt.strftime('%Y-%m')
    return t


# ----------------------------------------------------------------------------------------------
# 8. METRICS
# ----------------------------------------------------------------------------------------------
def _stats(t: pd.DataFrame) -> dict:
    c = t[t['outcome'].isin(['TP', 'SL', 'TIME'])]
    n = len(c)
    if n == 0:
        return dict(n=0, wr=float('nan'), avg_r=float('nan'), exp_pts=float('nan'), sum_r=0.0, max_loss_streak=0)
    r = c['r'].to_numpy()
    streak = best = 0
    for x in r:                       # theo thu tu thoi gian (simulate da sap theo idx)
        streak = streak + 1 if x <= 0 else 0
        best = max(best, streak)
    return dict(n=n, wr=float((r > 0).mean()), avg_r=float(r.mean()), exp_pts=float(c['pts'].mean()),
                sum_r=float(r.sum()), max_loss_streak=int(best))


def metrics(trades: pd.DataFrame, df: Optional[pd.DataFrame] = None) -> dict:
    """Thong ke lenh da mo phong. n, per_day (= n / so phien sach trong df, hoac so phien co lenh neu df=None),
    wr (R>0 / lenh da dong, loai OPEN), avg_r (R TB thuc, da tru chi phi), exp_pts (ky vong gia/lenh, da tru chi phi),
    sum_r, max_loss_streak; kem: by_month, by_phase (A/EU/US), by_split (TRAIN/TEST cat 2026-09-16), n_open, examples."""
    if trades is None or len(trades) == 0:
        return dict(n=0, per_day=0.0, n_open=0, by_month={}, by_phase={}, by_split={}, examples={'win': [], 'loss': []})
    if df is not None:
        st = session_table(df)
        days = int((~st['splice'].to_numpy() & (st['n'].to_numpy() >= CONST['min_bars_prof'])).sum())
    else:
        days = int(trades['session_id'].nunique())
    m = _stats(trades)
    m['per_day'] = m['n'] / max(days, 1)
    m['n_days'] = days
    m['n_open'] = int((trades['outcome'] == 'OPEN').sum())
    m['by_month'] = {k: _stats(g) for k, g in trades.groupby('month')}
    m['by_phase'] = {k: _stats(trades[trades['phase'] == k]) for k in PHASES}
    m['by_split'] = {k: _stats(trades[trades['split'] == k]) for k in ('TRAIN', 'TEST')}
    cl = trades[trades['outcome'].isin(['TP', 'SL', 'TIME'])]

    def ex(g):
        return [dict(t_utc=str(x.t_utc)[:16], t_vn=str(x.t_vn)[:16], side=int(x.side), setup=getattr(x, 'setup', ''),
                     entry=x.entry, sl=x.sl, tp=x.tp, outcome=x.outcome, r=round(float(x.r), 2)) for x in g.itertuples()]
    m['examples'] = {'win': ex(cl[cl['r'] > 0].head(5)), 'loss': ex(cl[cl['r'] <= 0].head(5))}
    return m


def render_markdown(trades: pd.DataFrame, df: Optional[pd.DataFrame] = None, title: str = 'Ket qua') -> str:
    """Bang Markdown tu metrics(): tong, theo thang, theo phase, TRAIN/TEST, 5 vi du thang/thua (gio UTC + VN)."""
    m = metrics(trades, df)

    def f(x, p=2):
        return ('%.*f' % (p, x)) if x == x else '-'

    def row(k, s):
        return '| %s | %d | %s%% | %s | %s | %s | %d |' % (k, s['n'], f(100 * s['wr'], 1), f(s['avg_r']), f(s['exp_pts']), f(s['sum_r'], 1), s['max_loss_streak'])
    hdr = '| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |\n|---|---|---|---|---|---|---|'
    L = ['## ' + title, '']
    if m['n'] == 0:
        return '\n'.join(L + ['Khong co lenh.'])
    L += ['Lenh da dong: **%d** (con mo: %d) | lenh/ngay: **%s** (tren %d phien)' % (m['n'], m['n_open'], f(m['per_day']), m['n_days']), '',
          hdr, row('Tong', m), '']
    for name, d in (('Theo thang', m['by_month']), ('Theo phase (A 05:00-12:30 / EU 12:30-19:00 / US 19:00-04:00 VN)', m['by_phase']),
                    ('Hai nua thoi gian (TRAIN <= 2026-09-15, TEST >= 2026-09-16)', m['by_split'])):
        L += ['### ' + name, '', hdr] + [row(k, s) for k, s in d.items()] + ['']
    for k, lab in (('win', 'Vi du THANG'), ('loss', 'Vi du THUA')):
        L += ['### ' + lab + ' (gio UTC / gio VN)', '', '| UTC | VN | side | setup | entry | SL | TP | ket qua | R |',
              '|---|---|---|---|---|---|---|---|---|']
        L += ['| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (e['t_utc'], e['t_vn'], 'BUY' if e['side'] > 0 else 'SELL', e['setup'], e['entry'], e['sl'], e['tp'], e['outcome'], e['r']) for e in m['examples'][k]]
        L += ['']
    return '\n'.join(L)


# ----------------------------------------------------------------------------------------------
# 9. DOI CHUNG
# ----------------------------------------------------------------------------------------------
def control_sample(df: pd.DataFrame, zcols: pd.DataFrame, mode: pd.Series, entries: Optional[list] = None,
                   side_filter: Optional[int] = None, n_random: int = 5, seed: int = 0, tol: float = 1.0, rr: float = 2.0,
                   zone: Optional[str] = None, mode_value: Optional[str] = None, n_total: int = 200) -> list:
    """Doi chung (plan 4.7): vao o nen NGAU NHIEN cung vung, cung che do, cung chieu.
    Cach 1 (entries=list lenh that): moi lenh that rut n_random nen doi chung co (a) 'o vung' cung vung entry['zone'] (|close - vung| <= tol
    hoac rau cham vung; ten vung trong ZONE_NAME2COL), (b) cung che do (mode) voi nen vao that, (c) khong dinh cho noi/phien mong,
    (d) khong phai nen vao that. Chieu = chieu lenh that (hoac side_filter neu co). SL = risk() voi cau truc = rau nen doi chung,
    TP = cung R:R voi lenh that. Cach 2 (entries=None): can zone [, mode_value], rut n_total nen, chieu = side_filter (bat buoc),
    R:R = rr. Tra list entry de dua vao simulate(..., one_at_a_time=False). Zone la ten vung khong co cot (HVN, ...) => bo qua
    dieu kien vung."""
    rng = np.random.default_rng(seed)
    cl, hi, lo = df['close'].to_numpy(float), df['high'].to_numpy(float), df['low'].to_numpy(float)
    okbar = (~df['splice'].to_numpy()) & (~df['thin'].to_numpy())
    mv = mode.to_numpy()
    cache = {}

    def zmask(name):
        col = ZONE_NAME2COL.get(name)
        if col is None:
            return np.ones(len(df), bool)
        if col not in cache:
            z = zcols[col].to_numpy(float)
            with np.errstate(invalid='ignore'):
                cache[col] = (np.abs(cl - z) <= tol) | ((lo <= z) & (z <= hi))
        return cache[col]

    def make(i, side, rrv, zname, setup, note):
        struct = lo[i] if side > 0 else hi[i]
        r = risk(df, i, side, struct, rr=rrv)
        if r is None:
            return None
        return dict(idx=int(i), side=side, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='CTRL-' + str(setup), zone=zname, note=note)

    out = []
    if entries:
        for e in entries:
            side = side_filter or int(e['side'])
            m = zmask(e.get('zone')) & okbar & (mv == mv[int(e['idx'])])
            m[int(e['idx'])] = False
            c = np.flatnonzero(m)
            if len(c) == 0:
                continue
            rrv = abs(float(e['tp']) - float(e['entry'])) / abs(float(e['entry']) - float(e['sl']))
            pick = rng.choice(c, size=min(n_random, len(c)), replace=False)
            for i in sorted(pick):
                x = make(i, side, rrv, e.get('zone'), e.get('setup', ''), 'ctrl cua idx %d' % e['idx'])
                if x:
                    out.append(x)
    else:
        if zone is None or side_filter is None:
            raise ValueError('entries=None can zone va side_filter')
        m = zmask(zone) & okbar
        if mode_value is not None:
            m &= mv == mode_value
        c = np.flatnonzero(m)
        if len(c):
            for i in sorted(rng.choice(c, size=min(n_total, len(c)), replace=False)):
                x = make(i, side_filter, rr, zone, 'RAND', 'ngau nhien')
                if x:
                    out.append(x)
    return out
