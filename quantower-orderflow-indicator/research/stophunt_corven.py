"""Stop hunt theo dinh nghia CORVEN (prototype Python de port sang C#).

stop hunt = gia QUET qua mot dinh/day QUAN TRONG (>= 1 tick) + co BONG no (bat ky mau) o phan rau vuot qua
            + FAIL BREAK (dong nen quay lai <= muc; bien the: trong 1-2 nen sau).
Muc quan trong: L0 (kiem soat: swing 8 nen cu), L1 (pivot k nen moi ben, chua bi quet, tuoi >= 2k),
                L2 (canh range di ngang), L3 (dinh/day phien, ngay, phien truoc, ngay truoc).
Moi thu dung cong thuc "huong dinh": day = lat dau (gia -> -gia), nen mot code cho ca hai phia.

Chay:  PYTHONIOENCODING=utf-8 python stophunt_corven.py            (cache pickle trong SCRATCH)
Ket qua in ra stdout, dong thoi ghi stophunt_corven_results.txt canh scratch.
"""
import os, sys, bisect, pickle, math, itertools
import numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view as swv

ROOT = r"C:\Users\anhla\OneDrive\Documents\footprint-tpo"
BARS = ROOT + r"\data-export\data-footprint\fp_GCZ26_XCEC_Time_20260811-20261109_90d_bars.csv"
LVL = ROOT + r"\data-export\data-footprint\fp_GCZ26_XCEC_Time_20260811-20261109_90d.csv"
SCR = r"C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\14112285-cd5a-4717-90f2-b4fe405421be\scratchpad\sh"
os.makedirs(SCR, exist_ok=True)
TICK = 0.1
EPS = 1e-9

# ---------------------------------------------------------------- tham so (pre-registered) ----------------
RATIO, FLOOR, WEAK_FLOOR, NB = 1.3, 9, 3, 20      # luat bong hien tai (CellBigLogic)
COOLDOWN = 5                                      # bo tin hieu cung phia trong 5 nen sau tin hieu truoc
HORIZ_REV, HORIZ_R, TP_R = 20, 60, 2.0
FEES = (0, 1, 2)                                  # tick khu hoi
SPLIT = pd.Timestamp('2026-09-25')                # nua dau < moc, nua sau >= moc (UTC)
MIN_N_SELECT = 40

# ---------------------------------------------------------------- du lieu ---------------------------------
def load():
    pk = SCR + r"\sh_data.pkl"
    if os.path.exists(pk):
        return pickle.load(open(pk, 'rb'))
    b = pd.read_csv(BARS, parse_dates=['datetime'],
                    usecols=['bar_idx', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'delta'])
    L = pd.read_csv(LVL, usecols=['bar_idx', 'price', 'bid_vol', 'ask_vol', 'volume'])
    L = L[L.volume > 0].copy()
    L['tk'] = (L.price * 10).round().astype(int)
    L['row'] = (L.tk - 1) // 2                         # hang 2 tick, pha 1 (nhu indicator)
    R = L.groupby(['bar_idx', 'row'], as_index=False).agg(bid=('bid_vol', 'sum'), ask=('ask_vol', 'sum'), vol=('volume', 'sum'))
    g = R.groupby('bar_idx').vol.agg(['sum', 'count'])
    bm = (g['sum'] / g['count']).reindex(b.bar_idx).values                    # TB vol moi hang co giao dich cua tung nen
    Bv = pd.Series(bm).shift(1).rolling(NB, min_periods=5).mean().values      # B = TB 20 nen DONG truoc
    pos = pd.Series(np.arange(len(b)), index=b.bar_idx.values)
    R['p'] = pos.reindex(R.bar_idx).values
    R['B'] = Bv[R.p.values]
    R['cen'] = (R.row * 2 + 1.5) / 10.0
    R['side'] = R[['bid', 'ask']].max(axis=1)
    R['weak'] = R[['bid', 'ask']].min(axis=1)
    Bb = R[(R.B > 0) & (R.side >= RATIO * R.B) & (R.side >= FLOOR)].copy()
    Bb['col'] = np.where((Bb.weak >= RATIO * Bb.B) & (Bb.weak >= WEAK_FLOOR), 'tim', np.where(Bb.ask >= Bb.bid, 'xanh', 'do'))
    Bb = Bb[['p', 'cen', 'bid', 'ask', 'col']]
    pickle.dump((b, Bb), open(pk, 'wb'))
    return b, Bb

class Side:
    """Du lieu da lat theo huong: s=+1 xet DINH (ban), s=-1 xet DAY (mua, lat dau gia)."""
    def __init__(self, b, Bb, s):
        self.s = s
        hi, lo, cl = b.high.values, b.low.values, b.close.values
        if s == 1: self.hi, self.lo, self.cl = hi, lo, cl
        else: self.hi, self.lo, self.cl = -lo, -hi, -cl
        self.n = len(b)
        self.bub = {}
        self.bubx = {}
        for p, c, col, bd, ak in zip(Bb.p.values, Bb.cen.values, Bb.col.values, Bb.bid.values, Bb.ask.values):
            self.bub.setdefault(int(p), []).append((s * c, col))      # tam bong trong khong gian lat
            self.bubx.setdefault(int(p), []).append((s * c, col, float(bd), float(ak)))

# ---------------------------------------------------------------- ho muc quan trong -----------------------
def lv_L0(S, k=8):
    sw = {}
    mx = pd.Series(S.hi).shift(1).rolling(k).max().values
    for i in np.where(S.hi >= mx + TICK - EPS)[0]:
        if not np.isnan(mx[i]): sw[int(i)] = [float(mx[i])]
    return sw

def lv_L1(S, k, age_min=None):
    """pivot dinh k nen moi ben (>= ca hai phia, cho phep dinh doi), xac nhan sau k nen, kich hoat khi tuoi >= age_min = 2k, chua bi quet."""
    n, hi = S.n, S.hi
    age_min = age_min or 2 * k
    lmax = pd.Series(hi).shift(1).rolling(k).max().values            # max k nen truoc
    rmax = pd.Series(hi[::-1]).shift(1).rolling(k).max().values[::-1]  # max k nen sau
    piv = np.where((hi >= lmax) & (hi >= rmax))[0]   # cho phep bang nhau (dinh doi)
    act = {}
    for j in piv: act.setdefault(int(j + age_min), []).append(int(j))
    active = []; sw = {}
    for i in range(n):
        for j in act.get(i, ()):
            if i - 1 > j and hi[j + 1:i].max() > hi[j] + EPS: continue     # da bi quet truoc khi kich hoat
            bisect.insort(active, float(hi[j]))
        if active:
            cut = bisect.bisect_right(active, hi[i] - TICK + EPS)
            if cut:
                sw[i] = active[:cut][::-1]; del active[:cut]               # nhieu muc -> lay muc cao truoc
    return sw

def box_arrays(S, N, X):
    hi, lo = S.hi, S.lo
    top = pd.Series(hi).shift(1).rolling(N).max().values
    bot = pd.Series(lo).shift(1).rolling(N).min().values
    med = pd.Series(hi - lo).shift(1).rolling(100).median().values
    h = top - bot
    zone = 0.25 * h
    # touches cluster (bat dau cum): bar trong cua so co hi >= top - zone, cach cum truoc >= 3 nen
    n = len(hi)
    pad = np.concatenate([np.full(N, np.nan), hi])
    W = swv(pad, N)[:n]                       # W[i] = hi[i-N .. i-1]
    Wl = swv(np.concatenate([np.full(N, np.nan), lo]), N)[:n]
    ct = W >= (top - zone)[:, None]
    cb = Wl <= (bot + zone)[:, None]
    def starts(c):
        c = c.astype(np.int8)
        prev = np.zeros_like(c)
        prev[:, 1:] += c[:, :-1]; prev[:, 2:] += c[:, :-2]
        return ((c == 1) & (prev == 0)).sum(axis=1)
    return top, bot, med, h, starts(ct), starts(cb)

def lv_L2_build(S, other, N, X, tt):
    """S = huong dang xet; other = huong doi dien (de co day/dinh hop). Hop co dinh trong khong gian S: top_S = max hi_S, bot_S = min lo_S."""
    top, bot, med, h, ntop, nbot = box_arrays(S, N, X)
    ok = (h <= X * med) & (ntop >= 2) & (nbot >= 2)
    span = np.full(S.n, np.inf); span[N:] = tt[N:] - tt[:-N]
    ok &= span <= N * 1.5
    sw = {}
    idx = np.where(ok & (S.hi >= top + TICK - EPS))[0]
    for i in idx: sw[int(i)] = [float(top[i])]
    return sw

def lv_union(S, tt, boxes=((20, 8), (60, 8))):
    """SPEC C# (StopHuntLogic.cs): hop cac muc L2 cua hop N=20 va N=60 (X=8); moi nen quet -> danh sach muc khac nhau, cao truoc."""
    parts = [lv_L2_build(S, None, N_, X, tt) for N_, X in boxes]
    sw = {}
    for d in parts:
        for i, lv in d.items(): sw.setdefault(i, set()).update(lv)
    return {i: sorted(v, reverse=True) for i, v in sw.items()}

def sessions(b):
    t = b.datetime
    h = t.dt.hour.values
    sess = np.where((h >= 22) | (h < 7), 0, np.where(h < 13, 1, 2))
    day = (t - pd.Timedelta(hours=22)).dt.floor('D').values.astype('datetime64[D]').astype(np.int64)
    sg = np.cumsum(np.r_[1, ((sess[1:] != sess[:-1]) | (day[1:] != day[:-1])).astype(int)])
    dg = np.cumsum(np.r_[1, (day[1:] != day[:-1]).astype(int)])
    return sg, dg

def lv_L3(S, sg, dg, kinds, min_sess=30, min_day=60, min_prior_bars=120):
    """kinds subset {'S','D','P'}: S = dinh phien so far + phien truoc ; D = dinh ngay so far + ngay truoc ; P = chi muc tinh truoc."""
    n, hi = S.n, S.hi
    sw = {}
    # thong ke theo nhom
    def grp_stats(g):
        df = pd.DataFrame({'g': g, 'hi': hi})
        mx = df.groupby('g').hi.max(); cnt = df.groupby('g').hi.count()
        return mx, cnt
    smx, scnt = grp_stats(sg); dmx, dcnt = grp_stats(dg)
    sprev = {g: (smx.get(g - 1, np.nan) if scnt.get(g - 1, 0) >= min_prior_bars else np.nan) for g in smx.index}
    dprev = {g: (dmx.get(g - 1, np.nan) if dcnt.get(g - 1, 0) >= 3 * min_prior_bars else np.nan) for g in dmx.index}
    cm_s = pd.Series(hi).groupby(sg).cummax().shift(1).values; pos_s = pd.Series(np.zeros(n)).groupby(sg).cumcount().values
    cm_d = pd.Series(hi).groupby(dg).cummax().shift(1).values; pos_d = pd.Series(np.zeros(n)).groupby(dg).cumcount().values
    consumed = set(); last_s = last_d = -1
    for i in range(n):
        if sg[i] != last_s: last_s = sg[i]; consumed = {c for c in consumed if c[0] == 'D'}
        if dg[i] != last_d: last_d = dg[i]; consumed = {c for c in consumed if c[0] == 'S'}
        c = []
        if 'S' in kinds and pos_s[i] >= min_sess and cm_s[i] == cm_s[i]: c.append(('so', cm_s[i]))
        if 'D' in kinds and pos_d[i] >= min_day and cm_d[i] == cm_d[i]: c.append(('do', cm_d[i]))
        if 'S' in kinds or 'P' in kinds:
            v = sprev.get(sg[i], np.nan)
            if v == v: c.append(('S_pr', v))
        if 'D' in kinds or 'P' in kinds:
            v = dprev.get(dg[i], np.nan)
            if v == v: c.append(('D_pr', v))
        lst = []
        for name, v in c:
            if hi[i] >= v + TICK - EPS:
                if name.endswith('_pr'):
                    key = (name[0], round(v, 2))
                    if key in consumed: continue
                    consumed.add(key)
                lst.append(float(v))
        if lst: sw[i] = sorted(set(lst), reverse=True)
    return sw

# ---------------------------------------------------------------- su kien -------------------------------------
def build_events(S, sw, mode, bub_tol=0):
    """Tra ve (with_bubble, no_bubble) = list dict(i, j, L, cols, ...) da loc cooldown."""
    cl, hi, n = S.cl, S.hi, S.n
    W, N_ = [], []
    for i, levels in sorted(sw.items()):
        best_w = best_n = None
        for L in levels:                                   # cao truoc
            if mode == 'same': j = i if cl[i] <= L + EPS else None
            else:
                j = None
                for jj in range(i, min(i + 3, n)):
                    if cl[jj] <= L + EPS: j = jj; break
            if j is None: continue
            bs = [(c, col) for (c, col) in S.bub.get(i, ()) if c >= L - bub_tol * TICK - EPS]
            if bs and best_w is None:
                bx = [t for t in S.bubx.get(i, ()) if t[0] >= L - bub_tol * TICK - EPS]
                st = bx[0]
                for t in bx[1:]:                      # manh nhat = max(Bid, Ask); hoa -> gan cuc tri hon (tam lon hon trong khong gian lat)
                    if max(t[2], t[3]) > max(st[2], st[3]) or (max(t[2], t[3]) == max(st[2], st[3]) and t[0] > st[0]): st = t
                best_w = dict(i=i, j=j, L=L, cols=sorted({col for _, col in bs}), nb=len(bs), strong=st)
            if not bs and best_n is None:
                best_n = dict(i=i, j=j, L=L, cols=[], nb=0)
        if best_w: W.append(best_w)
        elif best_n: N_.append(best_n)
    def cd(ev):
        out = []; last = -10**9
        for e in sorted(ev, key=lambda e: e['j']):
            if e['j'] - last > COOLDOWN: out.append(e); last = e['j']
        return out
    return cd(W), cd(N_)

# ---------------------------------------------------------------- ket qua ------------------------------------
class Outcome:
    def __init__(self, S, tt):
        self.S, self.tt, n = S, tt, S.n
        hi, lo, cl = S.hi, S.lo, S.cl
        self.med100 = pd.Series(hi - lo).rolling(100).median().values
        # first-hit +-1 x med100 trong 20 nen
        v20 = np.full(n, False); v20[:n - HORIZ_REV] = (tt[HORIZ_REV:] - tt[:-HORIZ_REV]) <= HORIZ_REV * 2.2
        self.v20 = v20
        H = swv(hi[1:], HORIZ_REV)[:n - HORIZ_REV]; Lw = swv(lo[1:], HORIZ_REV)[:n - HORIZ_REV]
        c = cl[:n - HORIZ_REV]; b = self.med100[:n - HORIZ_REV]
        up = H >= (c + b)[:, None]; dn = Lw <= (c - b)[:, None]
        iu = np.where(up.any(1), up.argmax(1), 99); idn = np.where(dn.any(1), dn.argmax(1), 99)
        df = np.full(n, np.nan)                     # 1 = day truoc (dao chieu dung huong cua tin hieu 'ban')
        r = np.where((iu == 99) & (idn == 99), np.nan, np.where(idn < iu, 1.0, np.where(iu < idn, 0.0, 0.5)))
        df[:n - HORIZ_REV] = r
        df[~v20] = np.nan; df[np.isnan(self.med100)] = np.nan
        self.df = df
    def rev(self, js):
        return self.df[np.array(js, int)] if len(js) else np.array([])
    def er(self, evs, fees=FEES):
        S, tt = self.S, self.tt
        hi, lo, cl, n = S.hi, S.lo, S.cl, S.n
        out = {f: [] for f in fees}; risk_t = []
        for e in evs:
            i, j = e['i'], e['j']
            if j + HORIZ_R >= n or tt[j + HORIZ_R] - tt[j] > HORIZ_R * 2.2: continue
            ent = cl[j]; sl = hi[i:j + 1].max() + TICK; risk = sl - ent
            if risk <= 0: continue
            tp = ent - TP_R * risk; R = None
            for m in range(1, HORIZ_R + 1):
                if hi[j + m] >= sl - EPS: R = -1.0; break
                if lo[j + m] <= tp + EPS: R = TP_R; break
            if R is None: R = (ent - cl[j + HORIZ_R]) / risk
            risk_t.append(risk / TICK)
            for f in fees: out[f].append(R - f * TICK / risk)
        return {f: np.array(v) for f, v in out.items()}, np.array(risk_t)

def ms(x):
    x = np.asarray(x, float)
    if len(x) < 2: return float('nan'), float('nan'), float('nan')
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(len(x))
    return m, se, (m / se if se > 0 else float('nan'))

# ---------------------------------------------------------------- ground truth --------------------------------
GT = [  # (ten, phia, cua so UTC (bat dau, ket thuc, gom ca hai dau), muc gan dung, nguon)
    ('GT1 0:22:41 dinh range 4090 (chum bong TIM + 1 DO)', 'top', '2026-11-06 09:20', '2026-11-06 09:22', 4090.2, 'zoom 0-22-52 + 0-24-15; delta -11/-14/-18 khop 09:20-09:22'),
    ('GT2 0:46:03 day range ~4108.5, bong DO', 'bot', '2026-11-05 20:43', '2026-11-05 20:47', 4108.5, '0-46-05 x643 y405 -> 20:45 / 4108.7'),
    ('GT3 0:27:36-59 nen to quet buy-SL (-96), dao len', 'bot', '2026-11-06 08:49', '2026-11-06 08:52', 4079.0, '0-28-00 x688 -> 08:51 / 4078.9'),
    ('GT4a 1:04:25 rau nhu xuong canh duoi range 4143 (-87)', 'bot', '2026-11-05 11:25', '2026-11-05 11:28', 4143.4, '1-04-00 x365 -> 11:26'),
    ('GT4b 1:04:25 rau nhu xuong (11:29)', 'bot', '2026-11-05 11:28', '2026-11-05 11:31', 4142.9, '1-04-00 x403 -> 11:29'),
    ('GT4c 1:04:25 rau nhu xuong (11:39)', 'bot', '2026-11-05 11:38', '2026-11-05 11:41', 4143.0, '1-04-00 x513 -> 11:39'),
    ('GT4d 1:04:25 rau xuong + bong tim (11:54)', 'bot', '2026-11-05 11:53', '2026-11-05 11:56', 4142.5, '1-04-00 x681 -> 11:54'),
]

# ---------------------------------------------------------------- chay -----------------------------------------
def pooled(res_list):
    return np.concatenate([r for r in res_list if len(r)]) if res_list else np.array([])

SPEC = '--spec' in sys.argv      # chay RIENG bien the C# (hop 20+60, fb=next2, tol=3, cooldown 5) + xuat danh sach tin hieu

def main():
    b, Bb = load()
    n = len(b); tt = (b.datetime.values.astype('datetime64[m]').astype(np.int64))
    times = b.datetime.values
    half = np.where(b.datetime >= SPLIT, 2, 1)
    # so ngay giao dich (de tinh tin hieu/ngay)
    sg, dg = sessions(b)
    cnt = pd.Series(np.zeros(n)).groupby(dg).count()
    ndays = {1: (cnt[np.unique(dg[half == 1])] >= 600).sum(), 2: (cnt[np.unique(dg[half == 2])] >= 600).sum()}
    out = []
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s); out.append(s)
    P(f'Du lieu: {n} nen M1 GCZ26, {b.datetime.min()} -> {b.datetime.max()} (UTC). Bong B20={NB}, ratio {RATIO}, san {FLOOR}.')
    P(f'Bong nho: {len(Bb)} hang bong tong. Nua 1 < {SPLIT.date()} ({ndays[1]} ngay), nua 2 ({ndays[2]} ngay). Cooldown {COOLDOWN} nen.')
    sides = {1: Side(b, Bb, 1), -1: Side(b, Bb, -1)}
    outc = {s: Outcome(sides[s], tt) for s in sides}
    # muc quan trong
    fam = {}   # ten -> {s: sw}
    def add(name, fn):
        fam[name] = {s: fn(sides[s]) for s in (1, -1)}
        P(f'  muc {name}: quet/dinh {len(fam[name][1])}, quet/day {len(fam[name][-1])} nen')
    P('Dang dung muc quan trong...')
    if SPEC:
        add('L2U hop 20+60 X=8', lambda S: lv_union(S, tt))
    else:
        add('L0 swing8', lambda S: lv_L0(S, 8))
        for k in (5, 10, 20, 40): add(f'L1 pivot k={k}', lambda S, k=k: lv_L1(S, k))
        for N_, X in ((20, 4), (20, 8), (40, 4), (40, 8), (60, 4), (60, 8)):
            add(f'L2 range N={N_} X={X}', lambda S, N_=N_, X=X: lv_L2_build(S, None, N_, X, tt))
        for nm, kd in (('L3S phien', {'S'}), ('L3D ngay', {'D'}), ('L3P truoc', {'P'}), ('L3U tat ca', {'S', 'D', 'P'})):
            add(nm, lambda S, kd=kd: lv_L3(S, sg, dg, kd))
    # su kien
    variants = {}
    for name in fam:
        for mode in (('next2',) if SPEC else ('same', 'next2')):
          for tol in ((3,) if SPEC else (0, 3)):
            key = f'{name} | fb={mode} | tol={tol}'
            ev = {}
            for s in (1, -1):
                w, nb = build_events(sides[s], fam[name][s], mode, tol)
                ev[s] = {'with': w, 'nob': nb}
            variants[key] = ev
    # co so (nen)
    base = {}
    for s in (1, -1):
        d = outc[s].df
        for h in (1, 2):
            m = (half == h)
            base[(s, h)] = np.nanmean(d[m])
        base[(s, None)] = np.nanmean(d)
    ndays[None] = ndays[1] + ndays[2]
    P('')
    P('Co so dao chieu truoc (rao +-1 x median range 100 nen, 20 nen) - moi nen, theo phia/nua: '
      + ', '.join(f'{"dinh" if s==1 else "day"}{h}={base[(s,h)]:.3f}' for s in (1, -1) for h in (1, 2)))

    def stat(ev_by_s, cat, which_s, h):
        """gop cac su kien phia which_s (list) o nua h"""
        revs, Rs, riskt, nev, barl = [], {f: [] for f in FEES}, [], 0, []
        bases = []
        for s in which_s:
            E = [e for e in ev_by_s[s][cat] if h is None or half[e['j']] == h]
            nev += len(E)
            if not E: continue
            js_ = np.array([e['j'] for e in E], int); r_all = outc[s].df[js_]; ok_ = ~np.isnan(r_all)
            r = r_all[ok_]; barl.append(outc[s].med100[js_][ok_] / TICK)
            revs.append(r); bases += [base[(s, h)]] * len(r)
            R, rk = outc[s].er(E)
            for f in FEES: Rs[f].append(R[f])
            riskt.append(rk)
        rv = pooled(revs)
        res = dict(n=nev, perday=nev / ndays[h], nrev=len(rv),
                   rev=(rv.mean() if len(rv) else np.nan), base=(np.mean(bases) if bases else np.nan))
        res['z'] = ((res['rev'] - res['base']) / math.sqrt(max(res['base'] * (1 - res['base']), 1e-9) / len(rv))) if len(rv) > 1 else np.nan
        for f in FEES:
            res[f] = ms(pooled(Rs[f]))
        res['risk'] = np.median(pooled(riskt)) if riskt else np.nan
        res['bar'] = np.mean(pooled(barl)) if barl else np.nan
        return res

    def fmt(r):
        e = lambda f: f'{r[f][0]:+.3f}±{r[f][1]:.3f}(t{r[f][2]:+.1f})' if r[f][0] == r[f][0] else '   -   '
        return (f"n={r['n']:4d} /ngay={r['perday']:.2f} | dao chieu {r['rev']*100:5.1f}% (co so {r['base']*100:4.1f}%, z={r['z']:+.1f}) | "
                f"E[R] phi0 {e(0)}  phi1 {e(1)}  phi2 {e(2)} | rui ro TV {r['risk']:.0f} tick")
    R_ALL = {}
    P('')
    P('=' * 100)
    P('BANG 1 - GOP DINH+DAY, tung bien the, hai nua (E[R] TP 2R SL=cuc tri+-1tick, timeout 60 nen)')
    P('=' * 100)
    for key, ev in variants.items():
        for cat, lab in (('with', 'CO BONG'), ('nob', 'KHONG BONG (doi chung)')):
            for h in (1, 2):
                r = stat(ev, cat, (1, -1), h); R_ALL[(key, cat, 'both', h)] = r
                P(f'{key:40s} {lab:22s} nua{h}: ' + fmt(r))
    P('')
    P('=' * 100)
    P('BANG 2 - TACH DINH / DAY (chi CO BONG)')
    P('=' * 100)
    for key, ev in variants.items():
        for s, lab in ((1, 'DINH'), (-1, 'DAY ')):
            for h in (1, 2):
                r = stat(ev, 'with', (s,), h); R_ALL[(key, 'with', s, h)] = r
                P(f'{key:40s} {lab} nua{h}: ' + fmt(r))
    P('')
    P('=' * 100)
    P('BANG 3 - GOP CA KY (ca hai nua) CO BONG vs KHONG BONG, va CHENH (rev: z hai ty le; E[R]@1: hieu hai trung binh)')
    P('=' * 100)
    for key, ev in variants.items():
        w = stat(ev, 'with', (1, -1), None); nb_ = stat(ev, 'nob', (1, -1), None)
        R_ALL[(key, 'with', 'both', None)] = w; R_ALL[(key, 'nob', 'both', None)] = nb_
        for s in (1, -1): R_ALL[(key, 'with', s, None)] = stat(ev, 'with', (s,), None)
        p1, p2 = w['rev'], nb_['rev']; n1, n2 = w['nrev'], nb_['nrev']
        pp = (w['rev'] * n1 + nb_['rev'] * n2) / max(n1 + n2, 1)
        zd = (p1 - p2) / math.sqrt(max(pp * (1 - pp), 1e-9) * (1 / max(n1, 1) + 1 / max(n2, 1))) if n1 > 1 and n2 > 1 else float('nan')
        dE = w[1][0] - nb_[1][0]; seE = math.sqrt(w[1][1] ** 2 + nb_[1][1] ** 2)
        P(f'{key:40s} CO BONG: ' + fmt(w))
        P(f'{"":40s} KHONG BONG: ' + fmt(nb_))
        sym = lambda f_: (2 * w['rev'] - 1) * w['bar'] - f_
        P(f'{"":40s} (a) rao doi xung +-{w["bar"]:.0f} tick: lai gop trung binh {(2*w["rev"]-1)*w["bar"]:+.2f} tick/lenh; sau phi 1 tick {sym(1):+.2f}, phi 2 tick {sym(2):+.2f}')
        dE0 = w[0][0] - nb_[0][0]; seE0 = math.sqrt(w[0][1] ** 2 + nb_[0][1] ** 2)
        P(f'{"":40s} CHENH E[R]@0 {dE0:+.3f}±{seE0:.3f} (t={dE0/seE0 if seE0 else float("nan"):+.1f}); E[R] khong phi CO BONG {w[0][0]:+.3f}, KHONG BONG {nb_[0][0]:+.3f}')
        P(f'{"":40s} CHENH dao chieu {(p1-p2)*100:+.1f}pp (z={zd:+.1f}); chenh E[R]@1 {dE:+.3f}±{seE:.3f} (t={dE/seE if seE else float("nan"):+.1f})')
    # chon bien the TREN NUA DAU: t cua E[R] phi 1 tick, gop dinh+day, CO BONG, n>=MIN_N_SELECT
    P('')
    P('=' * 100)
    P(f'CHON TREN NUA DAU (pre-registered): max t cua E[R]@1 tick (gop dinh+day, co bong, n>={MIN_N_SELECT}); bao cao nua sau')
    P('=' * 100)
    cands = [(R_ALL[(k, 'with', 'both', 1)][1][2], k) for k in variants
             if R_ALL[(k, 'with', 'both', 1)]['n'] >= MIN_N_SELECT and R_ALL[(k, 'with', 'both', 1)][1][2] == R_ALL[(k, 'with', 'both', 1)][1][2]]
    cands.sort(reverse=True)
    for t, k in cands[:6]:
        r1, r2 = R_ALL[(k, 'with', 'both', 1)], R_ALL[(k, 'with', 'both', 2)]
        P(f'{k:40s} nua1 t={t:+.2f} | nua2: ' + fmt(r2))
    P('')
    P(f'CHON CACH B (pre-registered thu hai): max z dao chieu so voi co so tren NUA DAU, n_dao_chieu>=100, co bong, gop dinh+day')
    cb = [(R_ALL[(k, 'with', 'both', 1)]['z'], k) for k in variants if R_ALL[(k, 'with', 'both', 1)]['nrev'] >= 100]
    cb.sort(reverse=True)
    for z1, k in cb[:6]:
        P(f'{k:40s} nua1 z={z1:+.2f} | nua2: ' + fmt(R_ALL[(k, 'with', 'both', 2)]))
    picks = []
    if cands: picks.append(('A (E[R] t)', cands[0][1]))
    if cb: picks.append(('B (dao chieu z)', cb[0][1]))
    for tag, best in picks:
        P(f'>>> [{tag}] ' )
        P('')
        P(f'>>> BIEN THE CHON (nua 1): {best}')
        for s, lab in ((1, 'DINH'), (-1, 'DAY ')):
            for h in (1, 2):
                P(f'    {lab} nua{h}: ' + fmt(R_ALL[(best, 'with', s, h)]))
        for h in (1, 2):
            P(f'    DOI CHUNG khong bong gop nua{h}: ' + fmt(R_ALL[(best, 'nob', 'both', h)]))
        # mau bong
        for s, lab in ((1, 'DINH'), (-1, 'DAY ')):
            cs = {}
            for e in variants[best][s]['with']:
                key = '+'.join(e['cols']); cs[key] = cs.get(key, 0) + 1
            P(f'    mau bong {lab}: {dict(sorted(cs.items(), key=lambda x: -x[1]))}')
        # theo mau (gop) tren toan ky
        P('    E[R]@1tick theo mau bong (gop ca ky, ca hai phia):')
        for lab, test in (('co TIM', lambda c: 'tim' in c), ('khong tim (xanh/do)', lambda c: 'tim' not in c)):
            Rs = []
            for s in (1, -1):
                E = [e for e in variants[best][s]['with'] if test(e['cols'])]
                R, _ = outc[s].er(E); Rs.append(R[1])
            m, se, t = ms(pooled(Rs)); P(f'      {lab}: n={len(pooled(Rs))} E[R]={m:+.3f}±{se:.3f} (t{t:+.1f})')
    # ---------------- ground truth
    P('')
    P('=' * 100)
    P('BANG GT - co bat duoc vi du CORVEN khong? (HIT = co su kien CO BONG o phia dung, nen quet nam trong cua so)')
    P('=' * 100)
    tstr = b.datetime.astype(str).values
    tpos = {t[:16]: i for i, t in enumerate(tstr)}
    gt_hit = {}
    for name_gt, side, t0, t1, lvl, src in GT:
        s = 1 if side == 'top' else -1
        i0, i1 = tpos[t0], tpos[t1]
        P(f'{name_gt} [{src}]')
        for i in range(i0, i1 + 1):
            P(f'     {tstr[i][5:16]} O{b.open[i]:.1f} H{b.high[i]:.1f} L{b.low[i]:.1f} C{b.close[i]:.1f} V{b.volume[i]} d{b.delta[i]} '
              f'bong(tam,mau)={[(round(s*c,2),col) for c,col in sides[s].bub.get(i, ()) if (c>= (sides[s].hi[i]-0.6))]}')
        for key, ev in variants.items():
            W = [e for e in ev[s]['with'] if i0 <= e['i'] <= i1]
            N2 = [e for e in ev[s]['nob'] if i0 <= e['i'] <= i1]
            name = key.split(' | ')[0]
            sw = fam[name][s]
            swept = [i for i in range(i0, i1 + 1) if i in sw]
            if W: why = f'HIT  L={s*W[0]["L"]:.2f} bong={W[0]["cols"]}'
            elif N2: why = 'MISS: quet+fail break nhung KHONG co bong o/phia tren muc'
            elif swept: why = 'MISS: quet muc nhung gia khong dong lai <= muc (khong fail break)'
            else: why = 'MISS: khong quet muc quan trong nao (muc khong ton tai / da bi quet / chua du dieu kien)'
            gt_hit[(name_gt, key)] = why
        sm = {}
        for key in variants:
            sm[key] = gt_hit[(name_gt, key)]
        hits = [k for k, v in sm.items() if v.startswith('HIT')]
        P(f'   -> HIT {len(hits)}/{len(sm)} bien the: ' + '; '.join(hits[:30]))
        reasons = {}
        for k, v in sm.items():
            if not v.startswith('HIT'): reasons[v] = reasons.get(v, 0) + 1
        for r_, c_ in reasons.items(): P(f'      {c_:3d} bien the: {r_}')
    if SPEC:
        key = next(iter(variants))
        tstr_ = b.datetime.dt.strftime('%Y-%m-%d %H:%M').values
        rows = []
        for s_ in (1, -1):
            for e in variants[key][s_]['with']:
                col = {'xanh': 'Xanh', 'do': 'Do', 'tim': 'Tim'}[e['strong'][1]]
                rows.append((e['j'], 'dinh' if s_ == 1 else 'day', tstr_[e['j']], tstr_[e['i']], round(s_ * e['L'], 1), col, int(e['strong'][2]), int(e['strong'][3])))
        rows.sort(key=lambda r: (r[0], r[1]))
        fn = os.environ.get('SH_SIGNALS_OUT', SCR + r'\sh_py_signals.csv')
        with open(fn, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('fail_time,side,sweep_time,level,colour,bid,ask\n')
            for r_ in rows: fh.write(f'{r_[2]},{r_[1]},{r_[3]},{r_[4]:.1f},{r_[5]},{r_[6]},{r_[7]}\n')
        P(f'>>> ghi {len(rows)} tin hieu CO BONG vao {fn}')
    open(SCR + r'\stophunt_corven_results.txt', 'w', encoding='utf-8').write('\n'.join(out))
    pickle.dump((R_ALL,), open(SCR + r'\sh_res.pkl', 'wb'))

if __name__ == '__main__':
    main()
