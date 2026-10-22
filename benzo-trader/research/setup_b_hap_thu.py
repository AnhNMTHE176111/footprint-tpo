"""Setup B - HAP THU tai VWAP tuan / VWAP ngay (Benzo Trader, plan muc 3-B).

Chay: python setup_b_hap_thu.py [--no2y] [--seeds N]   -> ghi report/RESULTS-B.md
Deterministic (seed co dinh). KHONG nhin truoc: moi dieu kien tai nen i chi dung nen <= i, vung = cot kernel (cong don den nen da dong).

Dinh nghia (bien the 'base'):
  M = chieu cua move den Z (+1 gia di LEN toi Z => vao SELL; -1 => vao BUY). Chieu vao s = -M.
  1. Move: tu cuc tri xa (low thap nhat / high cao nhat trong <= LOOKBACK nen truoc cum) toi Z >= MOVE_MIN gia.
  2. Cum N nen ngay truoc nen xac nhan: moi nen cham Z (|close-Z|<=1 hoac rau cham), than va |delta| GIAM DAN NGHIEM NGAT,
     khong cuc tri nao vuot Z + 0,5 gia theo chieu M.
  3. Nen xac nhan CF (nen i): dong theo chieu s, than >= 50% bien do, delta cung dau s, |delta_CF| >= theta * |delta| lon nhat cua move
     (nen lon nhat trong doan move, uu tien nen cung chieu M). Vao o close CF.
  4. SL = kernel.risk voi struct = cuc tri cum N nen (+0,3, san/tran cua kernel). TP 3R.
  5. Loai: dang pha VA Au/IB theo chieu M (break_side == M hoac close vuot canh band) | che do TREND cung chieu M |
     nen lon nhat phien nam trong 3 nen cuoi (bars_since_biggest <= 3) | phien splice/thin | phase OFF | VWAP chua du 30 nen.
  Them: toi da 2 lenh / (vung, phien) (ngat mach muc 2.1.5).
Bien the cau truc (bao rieng): 'retest' (da co lan cham Z truoc do roi roi xa >= 2 gia = test lai), 'cell' (o volume lon per-level tai Z).
"""
from __future__ import annotations

import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
DD = os.path.join(ROOT, 'data-export', 'data-footprint')
D90 = os.path.join(DD, 'fp_GCZ26_XCEC_Time_20260723-20261021_90d')
D2Y = os.path.join(DD, 'fp_GC_XCEC_Time_20240801-20260819_748d9h')

# hang so rieng cua setup B (khong dua vao kernel.CONST)
MOVE_MIN = 3.0        # move toi Z >= 3 gia
LOOKBACK = 20         # tim cuc tri xa trong 20 nen truoc cum
TOUCH_TOL = 1.0       # |close - Z| <= 1 gia
EXT_TOL = 0.5         # cuc tri khong vuot Z + 0,5
WARM = 30             # VWAP can >= 30 nen tu moc neo
BIG_EXCL = 3          # nen lon nhat phien trong 3 nen cuoi => loai
RR = 3.0
MAX_PER_ZONE_SESSION = 2
CELL_MULT = 2.0       # bien the 'cell': o volume lon nhat gan Z >= 2 x trung vi o-lon-nhat 50 nen
RETEST_LOOK = 40      # bien the 'retest'
RETEST_AWAY = 2.0
THETAS = (0.3, 0.5, 0.7)
NS = (2, 3, 4)
MAIN = (0.5, 3)


# ------------------------------------------------------------------ chuan bi du lieu
def prepare(df: pd.DataFrame, prof, extra_zones: dict = None) -> dict:
    """Tinh 1 lan: cot vung, che do, mang numpy dung cho detect.
    extra_zones (B-v2, plans/BENZO-B-v2-plan.md muc 2.1): dict ten_muc -> (mang gia theo nen, ztype), them vao SAU 2 VWAP theo dung
    thu tu chen (= thu tu uu tien trong detect). Vung co dinh => warm = True moi nen. Ten 'VWAP_W'/'VWAP_D' trong extra_zones = THAY
    mang VWAP (dung cho doi chung doi vung), giu nguyen dieu kien warm 30 nen. extra_zones=None => hanh vi cu y nguyen."""
    zc = K.zone_columns(df, prof)
    mdf = K.mode_frame(df, zc)
    n = len(df)
    sno = df['session_no'].to_numpy()
    st = K.session_table(df)
    start = st['start_pos'].to_numpy()[sno]
    wk = df['week_no'].to_numpy()
    wstart = pd.Series(np.arange(n)).groupby(wk).transform('min').to_numpy()
    # tuan co cho noi hop dong => VWAP tuan rac, loai ca tuan
    bad_w = np.unique(wk[df['splice_jump'].to_numpy()]) if df['splice_jump'].any() else np.array([], int)
    okbar = (~df['splice'].to_numpy()) & (~df['thin'].to_numpy()) & (df['phase'].to_numpy() != 'OFF') & (~np.isin(wk, bad_w))
    P = dict(df=df, zc=zc, mdf=mdf, mode=mdf['mode'], n=n, sno=sno,
             hi=df['high'].to_numpy(float), lo=df['low'].to_numpy(float), op=df['open'].to_numpy(float),
             cl=df['close'].to_numpy(float), dl=df['delta'].to_numpy(float),
             body=np.abs(df['close'].to_numpy(float) - df['open'].to_numpy(float)), rng=df['rng'].to_numpy(float),
             posin=np.arange(n) - start, wposin=np.arange(n) - wstart, okbar=okbar,
             bs=K.bars_since_biggest_bar(df).to_numpy(), modeA=mdf['mode'].to_numpy(),
             bside=mdf['break_side'].to_numpy(), bhi=mdf['band_hi'].to_numpy(float), blo=mdf['band_lo'].to_numpy(float),
             Z={'VWAP_W': zc['vwap_w'].to_numpy(float), 'VWAP_D': zc['vwap_d'].to_numpy(float)})
    P['adl'] = np.abs(P['dl'])
    P['ph'] = df['phase'].to_numpy()
    P['vww'] = zc['vwap_w'].to_numpy(float)
    P['u'] = K.median_range(df).to_numpy(float)
    P['modecode'] = pd.Series(pd.factorize(mdf['mode'])[0], index=df.index)
    P['ztype'] = {'VWAP_W': 'VWAP_W', 'VWAP_D': 'VWAP_D'}
    fixed = set()
    for name, (arr, zt) in (extra_zones or {}).items():
        P['Z'][name] = np.asarray(arr, float)
        P['ztype'][name] = zt
        if name not in ('VWAP_W', 'VWAP_D'):
            fixed.add(name)
    P['touch'], P['warm'] = {}, {}
    for name, zv in P['Z'].items():
        with np.errstate(invalid='ignore'):
            P['touch'][name] = (np.abs(P['cl'] - zv) <= TOUCH_TOL) | ((P['lo'] <= zv) & (zv <= P['hi']))
        P['warm'][name] = np.ones(n, bool) if name in fixed else (P['posin'] if name == 'VWAP_D' else P['wposin']) >= WARM
    return P


def add_cell_feature(P: dict, levels_path: str):
    """Bien the 'cell': voi moi nen, o per-level lon nhat (volume) trong +-1 gia quanh Z (2 loai Z) va o lon nhat ca nen."""
    df = P['df']
    lv = K.load_levels(levels_path, usecols=('bar_idx', 'price', 'volume'))
    lv = lv[lv['bar_idx'].isin(df['bar_idx'])]
    imap = pd.Series(np.arange(len(df)), index=df['bar_idx'].to_numpy())
    pos = imap.reindex(lv['bar_idx']).to_numpy()
    price, vol = lv['price'].to_numpy(float), lv['volume'].to_numpy(float)
    out = {}
    allmax = pd.Series(vol).groupby(pos).max()
    base = np.zeros(len(df))
    base[allmax.index.to_numpy().astype(int)] = allmax.to_numpy()
    med = pd.Series(base).rolling(50, min_periods=10).median().to_numpy()
    for name, zv in P['Z'].items():
        near = np.abs(price - zv[pos]) <= 1.0
        s = pd.Series(vol[near]).groupby(pos[near]).max()
        a = np.zeros(len(df))
        a[s.index.to_numpy().astype(int)] = s.to_numpy()
        out[name] = a
    P['cell_near'], P['cell_med'] = out, med


# ------------------------------------------------------------------ detect
def detect(P: dict, theta: float = 0.5, N: int = 3, zones=('VWAP_W', 'VWAP_D'), variant: str = 'base', mono: str = 'ends', funnel: dict = None, rr: float = RR, bias: bool = False, phases=None) -> list:
    """Tra list entry cho kernel.simulate. variant: 'base' | 'retest' | 'cell'.
    mono: 'strict' = than VA |delta| giam nghiem ngat tung nen lien tiep (dung chu plan) | 'ends' = nen cuoi cum < nen dau cum ca than lan |delta|
    (giam rong; lam vi 'strict' cho n ~ 0). funnel: dict dem so ung vien qua tung buoc (de bao cao)."""
    fn = funnel if funnel is not None else {}
    def cnt(k, v):
        fn[k] = fn.get(k, 0) + int(v)
    df = P['df']
    hi, lo, op, cl, dl, body, rng, adl = P['hi'], P['lo'], P['op'], P['cl'], P['dl'], P['body'], P['rng'], P['adl']
    n, sno = P['n'], P['sno']
    found = {}   # (i) -> entry (uu tien theo thu tu P['Z']: VWAP_W, VWAP_D, roi vung them cua B-v2)
    idx = np.arange(n)
    for name in P['Z']:
        if name not in zones:
            continue
        zv, touch, warm = P['Z'][name], P['touch'][name], P['warm'][name]
        for M in (1, -1):
            s = -M
            ok = np.zeros(n, bool)
            ok[N + 1:] = True
            cs = (cl - op) * s
            ok &= (cs > 0) & (cs >= K.CONST['cf_body_frac'] * rng) & (dl * s > 0) & P['okbar']
            if phases:
                ok &= np.isin(P['ph'], list(phases))
            if bias:
                ok &= (cl > P['vww']) if s > 0 else (cl < P['vww'])
            for j in range(1, N + 1):          # nen i-j: cung phien, cham Z, VWAP du nen, nen o gio ok
                sh = lambda a, k=j: np.r_[np.zeros(k, a.dtype), a[:-k]]
                ok &= sh(touch) & (sno == sh(sno)) & sh(warm) & sh(P['okbar'])
            cnt('1 CF dung + cum cham Z', ok.sum())
            if mono == 'strict':
                for j in range(1, N):               # giam dan nghiem ngat: nen i-j-1 > nen i-j (cu -> moi)
                    a1 = np.r_[np.zeros(j + 1), body[:-(j + 1)]]
                    a2 = np.r_[np.zeros(j), body[:-j]]
                    d1 = np.r_[np.zeros(j + 1), adl[:-(j + 1)]]
                    d2 = np.r_[np.zeros(j), adl[:-j]]
                    ok &= (a1 > a2) & (d1 > d2)
            else:
                f0 = np.r_[np.zeros(N), body[:-N]]        # nen dau cum (i-N)
                l0 = np.r_[np.zeros(1), body[:-1]]        # nen cuoi cum (i-1)
                fd = np.r_[np.zeros(N), adl[:-N]]
                ld = np.r_[np.zeros(1), adl[:-1]]
                ok &= (f0 > l0) & (fd > ld)
            cnt('2 + than/delta giam dan', ok.sum())
            # cuc tri cum
            ext = np.full(n, np.nan)
            ser = pd.Series(hi if M > 0 else lo)
            roll = (ser.rolling(N).max() if M > 0 else ser.rolling(N).min()).shift(1).to_numpy()
            ext = roll
            zlast = np.r_[np.nan, zv[:-1]]
            with np.errstate(invalid='ignore'):
                ok &= (ext <= zlast + EXT_TOL) if M > 0 else (ext >= zlast - EXT_TOL)
            # loai theo che do / nen lon nhat
            mo = P['modeA']
            trend_bad = (mo == ('TREND_UP' if M > 0 else 'TREND_DN'))
            with np.errstate(invalid='ignore'):
                edge_bad = (P['bside'] == M) | ((M > 0) & (np.r_[np.nan, cl[:-1]] > P['bhi'])) | ((M < 0) & (np.r_[np.nan, cl[:-1]] < P['blo']))
            cnt('3 + cuc tri <= Z+0,5', ok.sum())
            ok &= (~trend_bad) & (~edge_bad) & (P['bs'] > BIG_EXCL)
            cnt('4 + khong TREND/pha VA/nen lon nhat', ok.sum())
            if variant == 'cell':
                cn, cm = P['cell_near'][name], P['cell_med']
                mx = pd.Series(cn).rolling(N).max().shift(1).to_numpy()
                with np.errstate(invalid='ignore'):
                    ok &= mx >= CELL_MULT * cm
            for i in idx[ok]:
                i = int(i)
                a = i - N
                z = float(zv[i - 1])
                s0 = max(a - LOOKBACK, int(i - P['posin'][i]))
                if s0 >= a:
                    continue
                if M > 0:
                    e = s0 + int(np.argmin(lo[s0:a]))
                    move = z - lo[e]
                else:
                    e = s0 + int(np.argmax(hi[s0:a]))
                    move = hi[e] - z
                if move < MOVE_MIN:
                    continue
                cnt('5 + move >= 3 gia', 1)
                seg = slice(e, a)
                same = dl[seg] * M > 0
                mad = adl[seg][same].max() if same.any() else adl[seg].max()
                if mad <= 0 or adl[i] < theta * mad:
                    continue
                cnt('6 + |delta_CF| >= theta*max', 1)
                if variant == 'retest':
                    # da co lan cham Z (>= 4 nen truoc cum) roi roi xa >= 2 gia theo chieu nguoc M
                    lo_b = max(a - RETEST_LOOK, int(i - P['posin'][i]))
                    prev = np.flatnonzero(touch[lo_b:a - 3]) + lo_b
                    if len(prev) == 0:
                        continue
                    j0 = int(prev[0])
                    away = (z - lo[j0:a].min()) if M > 0 else (hi[j0:a].max() - z)
                    if away < RETEST_AWAY:
                        continue
                struct = float(hi[a:i].max() if M > 0 else lo[a:i].min())
                r = K.risk(df, i, s, struct, rr=rr)
                if r is None:
                    continue
                cnt('7 + risk() hop le (SL<=4 gia)', 1)
                if i in found:
                    found[i]['zones_hit'].append(name)     # B-v2: ghi moi muc cung khop tai i, lenh dau van giu
                    continue
                found[i] = dict(idx=i, side=s, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='B', zone=name, zprice=z,
                                ztype=P['ztype'][name], zones_hit=[name],
                                note='B %s M=%+d move=%.1f N=%d th=%.1f' % (name, M, move, N, theta))
    out = sorted(found.values(), key=lambda e: e['idx'])
    cnt, keep = {}, []
    for e in out:
        k = (e['ztype'], int(P['sno'][e['idx']]))       # tran theo LOAI vung (VWAP: ztype == ten => nhu cu)
        if cnt.get(k, 0) >= MAX_PER_ZONE_SESSION:
            continue
        cnt[k] = cnt.get(k, 0) + 1
        keep.append(e)
    return keep


# ------------------------------------------------------------------ thong ke
def run_cell(P, theta, N, zones=('VWAP_W', 'VWAP_D'), variant='base', mono='ends'):
    ents = detect(P, theta, N, zones, variant, mono)
    tr = K.simulate(P['df'], ents)
    return ents, tr


def S(tr):
    return K._stats(tr) if len(tr) else dict(n=0, wr=float('nan'), avg_r=float('nan'), exp_pts=float('nan'), sum_r=0.0, max_loss_streak=0)


def f(x, p=2):
    return ('%.*f' % (p, x)) if x == x else '-'


def pct(x):
    return f(100 * x, 1) + '%' if x == x else '-'


def control_dist(P, ents_taken, seeds):
    """Doi chung: moi seed rut 1 nen ngau nhien / lenh that (cung vung, che do, chieu, R:R). Tra mang (wr, avgR) theo seed."""
    df = P['df']
    res = []
    for sd in range(seeds):
        c = K.control_sample(df, P['zc'], P['mode'], entries=ents_taken, n_random=1, seed=sd)
        if not c:
            continue
        t = K.simulate(df, c, one_at_a_time=False)
        st = S(t)
        res.append((st['wr'], st['avg_r'], st['n']))
    return np.array(res)


def days_in(P, mask=None):
    st = K.session_table(P['df'])
    ok = (~st['splice'].to_numpy()) & (st['n'].to_numpy() >= K.CONST['min_bars_prof']) & (~st['thin'].to_numpy())
    if mask is not None:
        ok &= mask
    return int(ok.sum())


def table_rows(tr, days):
    L = ['| | n | WR | R TB | ky vong gia/lenh | tong R | chuoi thua | lenh/ngay |', '|---|---|---|---|---|---|---|---|']
    def row(k, t, d):
        s = S(t)
        return '| %s | %d | %s | %s | %s | %s | %d | %s |' % (k, s['n'], pct(s['wr']), f(s['avg_r']), f(s['exp_pts']), f(s['sum_r'], 1), s['max_loss_streak'], f(s['n'] / max(d, 1)))
    L.append(row('Tong', tr, days))
    return L, row


def main_r1():
    seeds = 200
    do2y = '--no2y' not in sys.argv
    if '--seeds' in sys.argv:
        seeds = int(sys.argv[sys.argv.index('--seeds') + 1])
    t0 = time.time()
    df = K.load_bars(D90 + '_bars.csv')
    prof = K.build_profiles(df, D90 + '.csv')
    P = prepare(df, prof)
    L = []
    A = L.append
    st90 = K.session_table(df)
    days90 = days_in(P)
    A('# RESULTS-B - Setup B Hap thu tai VWAP tuan / ngay')
    A('')
    A('Sinh boi `setup_b_hap_thu.py` (deterministic). Gio UTC (VN = UTC+7). R tinh sau chi phi 0,2 gia/lenh, TP 3R, vao o close nen xac nhan, '
      'mo phong tu nen ke tiep, cung nen SL+TP => SL, 1 lenh mo cung luc, toi da 2 lenh/(vung, phien).')
    A('')
    A('**Mon bai doc truoc:** voi TP 3R va chi phi, WR hoa von xap xi 25-28% (xem doi chung). Muc tieu 60-70% WR o 3R khong the do bang setup nay neu doi chung da ~25%.')
    A('')
    A('Du lieu chinh: file 90d (GCZ26), %d nen M1, %d phien (%d phien sach dung de chia "lenh/ngay"). TRAIN <= 2026-09-15, TEST >= 2026-09-16.' % (len(df), len(st90), days90))
    A('')

    # ---------- luoi 3x3 (ca hai vung)
    cells = {}
    for th in THETAS:
        for N in NS:
            cells[(th, N)] = {}
            for zname, zs in (('ALL', ('VWAP_W', 'VWAP_D')), ('W', ('VWAP_W',)), ('D', ('VWAP_D',))):
                cells[(th, N)][zname] = run_cell(P, th, N, zs)
    for zname, lab in (('ALL', 'Z = VWAP tuan + VWAP ngay'), ('W', 'Z = chi VWAP tuan'), ('D', 'Z = chi VWAP ngay')):
        A('## Luoi 3x3 - %s (90d)' % lab)
        A('')
        A('Moi o: `n / WR / R TB` toan bo | `TRAIN n, R TB` | `TEST n, R TB`. Hang = nguong |delta_CF|/|delta| lon nhat (theta), cot = so nen cum giam dan (N).')
        A('')
        A('| theta \\ N | ' + ' | '.join(str(N) for N in NS) + ' |')
        A('|---|' + '---|' * len(NS))
        for th in THETAS:
            row = []
            for N in NS:
                tr = cells[(th, N)][zname][1]
                s, a, b = S(tr), S(tr[tr['split'] == 'TRAIN']) if len(tr) else S(tr), S(tr[tr['split'] == 'TEST']) if len(tr) else S(tr)
                row.append('%d / %s / %s<br>TR %d, %s<br>TE %d, %s' % (s['n'], pct(s['wr']), f(s['avg_r']), a['n'], f(a['avg_r']), b['n'], f(b['avg_r'])))
            A('| %.1f | ' % th + ' | '.join(row) + ' |')
        A('')

    # ---------- dinh nghia chu plan (strict) + phan tich phễu
    A('## Dinh nghia DUNG CHU plan (than VA |delta| giam nghiem ngat tung nen) - 90d, ca hai vung')
    A('')
    A('`n / R TB` (n < 30 => khong ket luan). Cac bang luoi o tren dung "giam dan RONG" (nen cuoi cum < nen dau cum, ca than lan |delta|) vi ban chu cho n ~ 0.')
    A('')
    A('| theta \ N | ' + ' | '.join(str(N) for N in NS) + ' |')
    A('|---|' + '---|' * len(NS))
    for th in THETAS:
        row_ = []
        for N in NS:
            t_ = run_cell(P, th, N, mono='strict')[1]
            row_.append('%d / %s' % (S(t_)['n'], f(S(t_)['avg_r'])))
        A('| %.1f | ' % th + ' | '.join(row_) + ' |')
    A('')
    A('### Pheu loc o chinh (theta=%.1f, N=%d, ca hai vung, so ung vien con lai sau moi buoc; chua gom one-at-a-time / tran 2 lenh)' % MAIN)
    A('')
    fa, fb = {}, {}
    detect(P, MAIN[0], MAIN[1], mono='strict', funnel=fa)
    detect(P, MAIN[0], MAIN[1], mono='ends', funnel=fb)
    A('| buoc | giam dan RONG | giam dan NGHIEM NGAT (chu plan) |')
    A('|---|---|---|')
    for k in sorted(set(fa) | set(fb)):
        A('| %s | %s | %s |' % (k, fb.get(k, 0), fa.get(k, 0)))
    A('')
    # ---------- o chinh
    ents, tr = cells[MAIN]['ALL']
    A('## O chinh (theta=%.1f, N=%d; dung dinh nghia khoi diem trong plan - KHONG chon o tot nhat)' % MAIN)
    A('')
    m = K.metrics(tr, df)
    z0 = dict(n=0, wr=float('nan'), avg_r=float('nan'), exp_pts=float('nan'), sum_r=0.0, max_loss_streak=0)
    m.setdefault('n_days', days90); m.setdefault('per_day', 0.0)
    if m['n'] == 0:
        m.update(wr=float('nan'), avg_r=float('nan'), exp_pts=float('nan'), sum_r=0.0, max_loss_streak=0, by_phase={k: z0 for k in K.PHASES}, by_split={k: z0 for k in ('TRAIN', 'TEST')})
    A('Lenh da dong **%d** (con mo %d), lenh/ngay **%s** (tren %d phien sach).' % (m['n'], m['n_open'], f(m['per_day']), m['n_days']))
    A('')
    hdr = '| | n | WR | R TB | ky vong gia/lenh | tong R | chuoi thua dai nhat |\n|---|---|---|---|---|---|---|'
    def row(k, s):
        return '| %s | %d | %s | %s | %s | %s | %d |' % (k, s['n'], pct(s['wr']), f(s['avg_r']), f(s['exp_pts']), f(s['sum_r'], 1), s['max_loss_streak'])
    A(hdr)
    A(row('Tong', m))
    A('')
    A('### Lenh/ngay theo phase (A 05:00-12:30 / EU 12:30-19:00 / US 19:00-04:00 VN)')
    A('')
    A('| phase | n | lenh/ngay | WR | R TB |')
    A('|---|---|---|---|---|')
    for ph in K.PHASES:
        s = m['by_phase'][ph]
        A('| %s | %d | %s | %s | %s |' % (ph, s['n'], f(s['n'] / max(m['n_days'], 1)), pct(s['wr']), f(s['avg_r'])))
    A('')
    A('So voi muc tieu 10-20 lenh/ngay: B cho **%s lenh/ngay** toan ngay (US rieng: %s).' % (f(m['per_day']), f(m['by_phase']['US']['n'] / max(m['n_days'], 1))))
    A('')
    for key, lab in (('by_month', 'Theo thang'), ('by_split', 'TRAIN / TEST')):
        A('### ' + lab)
        A('')
        A(hdr)
        for k, s in m[key].items():
            A(row(k, s))
        A('')
    A('### Tach theo vung (o chinh)')
    A('')
    A(hdr)
    for zname, lab in (('W', 'VWAP tuan'), ('D', 'VWAP ngay')):
        tz = cells[MAIN][zname][1]
        A(row(lab, S(tz)))
        A(row(lab + ' - TRAIN', S(tz[tz['split'] == 'TRAIN']) if len(tz) else S(tz)))
        A(row(lab + ' - TEST', S(tz[tz['split'] == 'TEST']) if len(tz) else S(tz)))
    A('')

    # ---------- doi chung
    taken = [dict(idx=int(r.idx), side=int(r.side), entry=r.entry, sl=r.sl, tp=r.tp, setup='B', zone=r.zone) for r in tr.itertuples()]
    A('### Doi chung (%d lan rut; moi lan 1 nen ngau nhien / lenh that, cung vung, che do, chieu, R:R 3)' % seeds)
    A('')
    cd = control_dist(P, taken, seeds)
    real = S(tr)
    if len(cd):
        A('| | WR | R TB |')
        A('|---|---|---|')
        A('| Setup B (that) | %s | %s |' % (pct(real['wr']), f(real['avg_r'])))
        A('| Doi chung trung binh | %s | %s |' % (pct(np.nanmean(cd[:, 0])), f(np.nanmean(cd[:, 1]))))
        A('| Doi chung do lech chuan | %s | %s |' % (f(100 * np.nanstd(cd[:, 0]), 1) + ' diem', f(np.nanstd(cd[:, 1]))))
        A('| Doi chung moc 5%% / 95%% (R TB) | - | %s / %s |' % (f(np.nanpercentile(cd[:, 1], 5)), f(np.nanpercentile(cd[:, 1], 95))))
        A('| Ty le lan rut co R TB >= that | - | %s |' % pct(float((cd[:, 1] >= real['avg_r']).mean())))
        A('')
        A('Doi chung tren toan ban TRAIN/TEST xem bang tach o duoi.')
        ctrl_main = cd
    else:
        ctrl_main = cd
        A('Khong co lenh doi chung.')
    A('')
    # doi chung theo TEST
    tt = [e for e in taken if df['split'].iloc[e['idx']] == 'TEST']
    ttr = tr[tr['split'] == 'TEST']
    if len(tt):
        cdt = control_dist(P, tt, min(seeds, 100))
        A('Doi chung rieng TEST (n that = %d): that WR %s, R TB %s | doi chung WR %s, R TB %s (100 lan rut).' % (
            len(tt), pct(S(ttr)['wr']), f(S(ttr)['avg_r']), pct(np.nanmean(cdt[:, 0])), f(np.nanmean(cdt[:, 1]))))
        A('')

    # ---------- vi du
    A('### 5 vi du THANG + 5 vi du THUA (gio UTC / VN; Z = gia VWAP luc vao)')
    A('')
    cl_ = tr[tr['outcome'].isin(['TP', 'SL'])]
    for lab, g in (('THANG', cl_[cl_['r'] > 0]), ('THUA', cl_[cl_['r'] <= 0])):
        A('**%s**' % lab)
        A('')
        A('| UTC | VN | chieu | Z | vung | entry | SL | TP | ket qua | R |')
        A('|---|---|---|---|---|---|---|---|---|---|')
        # chon rai deu theo thoi gian de khong chi lay 5 lenh dau (cung deterministic)
        g = g.iloc[np.unique(np.linspace(0, len(g) - 1, 5).astype(int))] if len(g) > 5 else g
        for x in g.itertuples():
            A('| %s | %s | %s | %.1f | %s | %.1f | %.1f | %.1f | %s | %.2f |' % (str(x.t_utc)[:16], str(x.t_vn)[:16], 'BUY' if x.side > 0 else 'SELL', x.zprice, x.zone, x.entry, x.sl, x.tp, x.outcome, x.r))
        A('')

    # ---------- bien the
    A('## Bien the cau truc (bao rieng, chi 90d)')
    A('')
    var_res = {}
    levels_ok = os.path.exists(D90 + '.csv')
    if levels_ok:
        add_cell_feature(P, D90 + '.csv')
    for vname, desc in (('retest', 'V1 "test lai": da co mot lan cham Z trong 40 nen truoc cum roi roi xa >= 2 gia, nay quay lai lan hai (hinh U/test lai truoc khi dao chieu).'),
                        ('cell', 'V2 "o volume lon": trong cum, co o per-level (bid+ask) lon nhat trong +-1 gia quanh Z >= 2 x trung vi o-lon-nhat 50 nen (luong lon tai Z, dung nghia "bong bong tai vung").')):
        if vname == 'cell' and not levels_ok:
            continue
        A('### %s' % desc)
        A('')
        A('| theta \\ N | ' + ' | '.join(str(N) for N in NS) + ' |')
        A('|---|' + '---|' * len(NS))
        for th in THETAS:
            row_ = []
            for N in NS:
                e2, t2 = run_cell(P, th, N, variant=vname)
                var_res[(vname, th, N)] = t2
                s = S(t2)
                a = S(t2[t2['split'] == 'TRAIN']) if len(t2) else s
                b = S(t2[t2['split'] == 'TEST']) if len(t2) else s
                row_.append('%d / %s / %s<br>TR %d, %s<br>TE %d, %s' % (s['n'], pct(s['wr']), f(s['avg_r']), a['n'], f(a['avg_r']), b['n'], f(b['avg_r'])))
            A('| %.1f | ' % th + ' | '.join(row_) + ' |')
        A('')
        tv = var_res[(vname,) + MAIN]
        e2 = detect(P, MAIN[0], MAIN[1], variant=vname)
        tk = [dict(idx=int(r.idx), side=int(r.side), entry=r.entry, sl=r.sl, tp=r.tp, setup='B', zone=r.zone) for r in tv.itertuples()]
        cdv = control_dist(P, tk, min(seeds, 100)) if len(tk) else np.zeros((0, 3))
        A('O chinh bien the: n=%d, WR %s, R TB %s, ky vong %s gia, tong R %s%s.' % (
            S(tv)['n'], pct(S(tv)['wr']), f(S(tv)['avg_r']), f(S(tv)['exp_pts']), f(S(tv)['sum_r'], 1),
            (' | doi chung cung vung/che do: WR %s, R TB %s' % (pct(np.nanmean(cdv[:, 0])), f(np.nanmean(cdv[:, 1]))) if len(cdv) else '')))
        A('')

    # ---------- 2 nam
    if do2y and os.path.exists(D2Y + '_bars.csv'):
        t1 = time.time()
        d2 = K.load_bars(D2Y + '_bars.csv')
        pr2 = K.build_profiles(d2, D2Y + '.csv')
        P2 = prepare(d2, pr2)
        sd = d2['session_id'].str[:10].to_numpy()
        half_cut = '2025-08-19'
        st2 = K.session_table(d2)
        sess_half = np.array([str(x)[:10] <= half_cut for x in st2['session_id']])
        A('## File 2 nam `fp_GC_XCEC_Time_20240801-20260819_748d9h` (loai splice +-2 phien va ca TUAN co cho noi; profile per-level that)')
        A('')
        A('Nua 1 = phien <= %s, nua 2 = sau do. "n phien" = phien sach (khong splice/thin/tuan-splice) cua moi nua; so lenh/ngay chia cho so do.' % half_cut)
        A('')
        wk_bad = np.unique(d2['week_no'].to_numpy()[d2['splice_jump'].to_numpy()])
        sess_week = st2['week_no'].to_numpy()
        clean = (~st2['splice'].to_numpy()) & (st2['n'].to_numpy() >= K.CONST['min_bars_prof']) & (~st2['thin'].to_numpy()) & (~np.isin(sess_week, wk_bad))
        dh = (int((clean & sess_half).sum()), int((clean & ~sess_half).sum()))
        A('Phien sach: nua 1 = %d, nua 2 = %d (tong %d / %d phien).' % (dh[0], dh[1], int(clean.sum()), len(st2)))
        A('')
        cells2 = {}
        for zname, lab, zs in (('ALL', 'Z = VWAP tuan + ngay', ('VWAP_W', 'VWAP_D')), ('W', 'chi VWAP tuan', ('VWAP_W',)), ('D', 'chi VWAP ngay', ('VWAP_D',))):
            A('### Luoi 3x3 - %s (2 nam): `n / R TB nua1 | n / R TB nua2`' % lab)
            A('')
            A('| theta \\ N | ' + ' | '.join(str(N) for N in NS) + ' |')
            A('|---|' + '---|' * len(NS))
            for th in THETAS:
                row_ = []
                for N in NS:
                    e2, t2 = run_cell(P2, th, N, zs)
                    cells2[(zname, th, N)] = t2
                    if len(t2):
                        h1 = t2[t2['session_id'].str[:10] <= half_cut]
                        h2 = t2[t2['session_id'].str[:10] > half_cut]
                    else:
                        h1 = h2 = t2
                    a, b = S(h1), S(h2)
                    row_.append('%d, WR %s, %s<br>%d, WR %s, %s' % (a['n'], pct(a['wr']), f(a['avg_r']), b['n'], pct(b['wr']), f(b['avg_r'])))
                A('| %.1f | ' % th + ' | '.join(row_) + ' |')
            A('')
        t2 = cells2[('ALL',) + MAIN]
        h1 = t2[t2['session_id'].str[:10] <= half_cut] if len(t2) else t2
        h2 = t2[t2['session_id'].str[:10] > half_cut] if len(t2) else t2
        A('### O chinh 2 nam (theta=%.1f, N=%d)' % MAIN)
        A('')
        A('| | n | WR | R TB | ky vong gia/lenh | tong R | chuoi thua | lenh/ngay |')
        A('|---|---|---|---|---|---|---|---|')
        for lab, g, d in (('Nua 1', h1, dh[0]), ('Nua 2', h2, dh[1]), ('Ca 2 nam', t2, sum(dh))):
            s = S(g)
            A('| %s | %d | %s | %s | %s | %s | %d | %s |' % (lab, s['n'], pct(s['wr']), f(s['avg_r']), f(s['exp_pts']), f(s['sum_r'], 1), s['max_loss_streak'], f(s['n'] / max(d, 1))))
        A('')
        if len(t2):
            A('Theo phase (ca 2 nam): ' + '; '.join('%s n=%d R TB %s' % (ph, S(t2[t2['phase'] == ph])['n'], f(S(t2[t2['phase'] == ph])['avg_r'])) for ph in K.PHASES))
            A('')
            tk2 = [dict(idx=int(r.idx), side=int(r.side), entry=r.entry, sl=r.sl, tp=r.tp, setup='B', zone=r.zone) for r in t2.itertuples()]
            ns2 = 20
            cd2 = control_dist(P2, tk2, ns2)
            if len(cd2):
                A('Doi chung 2 nam (%d lan rut, cung vung/che do/chieu): WR %s, R TB %s (do lech %s) | that WR %s, R TB %s.' % (
                    ns2, pct(np.nanmean(cd2[:, 0])), f(np.nanmean(cd2[:, 1])), f(np.nanstd(cd2[:, 1])), pct(S(t2)['wr']), f(S(t2)['avg_r'])))
                A('')
            A('Theo thang (2 nam, o chinh):')
            A('')
            A(hdr)
            for k, g in t2.groupby('month'):
                A(row(k, S(g)))
            A('')
        # bien the retest tren 2 nam (khong can per-level)
        A('### Bien the V1 "test lai" tren 2 nam: `n, R TB nua1 | n, R TB nua2`')
        A('')
        A('| theta \\ N | ' + ' | '.join(str(N) for N in NS) + ' |')
        A('|---|' + '---|' * len(NS))
        for th in THETAS:
            row_ = []
            for N in NS:
                e2, tv = run_cell(P2, th, N, variant='retest')
                if len(tv):
                    h1v, h2v = tv[tv['session_id'].str[:10] <= half_cut], tv[tv['session_id'].str[:10] > half_cut]
                else:
                    h1v = h2v = tv
                a, b = S(h1v), S(h2v)
                row_.append('%d, %s, %s<br>%d, %s, %s' % (a['n'], pct(a['wr']), f(a['avg_r']), b['n'], pct(b['wr']), f(b['avg_r'])))
            A('| %.1f | ' % th + ' | '.join(row_) + ' |')
        A('')
        # do ben cua o chinh 2 nam: khoang tin cay bootstrap + bo 2 thang tot nhat
        if len(t2) >= 5:
            r_ = t2['r'].to_numpy()
            rg = np.random.default_rng(12345)
            bs_ = np.array([rg.choice(r_, len(r_)).mean() for _ in range(4000)])
            A('Do ben o chinh 2 nam: R TB %s, khoang tin cay bootstrap 95%% [%s ; %s]; WR hoa von xap xi %s (3R, chi phi 0,2 gia).' % (
                f(r_.mean()), f(np.percentile(bs_, 2.5)), f(np.percentile(bs_, 97.5)), pct((1 + 0.2 / t2['risk_pts'].mean()) / 4)))
            mo = t2.groupby('month')['r'].sum().sort_values(ascending=False)
            rest = t2[~t2['month'].isin(mo.index[:2])]
            A('Bo 2 thang tot nhat (%s): n=%d, WR %s, R TB %s.' % (', '.join(mo.index[:2]), len(rest), pct(S(rest)['wr']), f(S(rest)['avg_r'])))
            A('')
        # bien the V2 (o volume lon) tren 2 nam: can per-level 2 nam
        t3 = time.time()
        add_cell_feature(P2, D2Y + '.csv')
        A('### Bien the V2 "o volume lon" tren 2 nam: `n, WR, R TB nua1 | n, WR, R TB nua2`')
        A('')
        A('| theta \ N | ' + ' | '.join(str(N) for N in NS) + ' |')
        A('|---|' + '---|' * len(NS))
        for th in THETAS:
            row_ = []
            for N in NS:
                e2, tv = run_cell(P2, th, N, variant='cell')
                if len(tv):
                    h1v, h2v = tv[tv['session_id'].str[:10] <= half_cut], tv[tv['session_id'].str[:10] > half_cut]
                else:
                    h1v = h2v = tv
                a, b = S(h1v), S(h2v)
                row_.append('%d, %s, %s<br>%d, %s, %s' % (a['n'], pct(a['wr']), f(a['avg_r']), b['n'], pct(b['wr']), f(b['avg_r'])))
            A('| %.1f | ' % th + ' | '.join(row_) + ' |')
        A('')
        A('(2 nam: %.0f giay.)' % (time.time() - t1))
        A('')
    A('(Tong thoi gian chay: %.0f giay.)' % (time.time() - t0))
    return chr(10).join(L)


# ====================================================================================================
# VONG 2: H1 (bias VWAP tuan) + H2 (no luc co, ket qua khong) + H3 (TP 2R song song 3R)
# ====================================================================================================
K2S = (2, 3, 4)
TH2 = (0.3, 0.5)
MAIN2 = (0.5, 3)
CFG = [('BASE', 'dinh nghia vong 1 ("giam dan rong")', 'old', False),
       ('H1', 'BASE + bias (chi Z=VWAP ngay, huong theo VWAP tuan)', 'old', True),
       ('H2', '"no luc co, ket qua khong" (khong bias)', 'new', False),
       ('H1+H2', 'H2 + bias', 'new', True)]
PHS = (('EU+US', ('EU', 'US')), ('A', ('A',)))
HALF_CUT = '2025-08-19'


def detect2(P, Kc, theta, zones=('VWAP_W', 'VWAP_D'), bias=False, rr=3.0, phases=None, funnel=None):
    """H2: cum Kc nen cuoi truoc CF: tong |delta| cac nen CUNG chieu M >= |delta| nen lon nhat cua move; bien do cum <= 1,5u;
    cuc tri cum <= Z + 0,5u (u = trung vi bien do 50 nen tai nen cuoi cum); nen cuoi cum cham Z (|close-Z|<=1 hoac rau cham).
    CF: |delta_CF| >= theta * |delta| lon nhat cua move. Moi loai/loc khac nhu 'base' (che do, nen lon nhat, move >= 3 gia, phase OFF...)."""
    fn = funnel if funnel is not None else {}

    def cnt(k, v):
        fn[k] = fn.get(k, 0) + int(v)
    df = P['df']
    hi, lo, op, cl, dl, rng, adl, u = P['hi'], P['lo'], P['op'], P['cl'], P['dl'], P['rng'], P['adl'], P['u']
    n, sno = P['n'], P['sno']
    found = {}
    idx = np.arange(n)
    for name in ('VWAP_W', 'VWAP_D'):
        if name not in zones:
            continue
        zv, touch, warm = P['Z'][name], P['touch'][name], P['warm'][name]
        for M in (1, -1):
            s = -M
            ok = np.zeros(n, bool)
            ok[Kc + 1:] = True
            cs = (cl - op) * s
            ok &= (cs > 0) & (cs >= K.CONST['cf_body_frac'] * rng) & (dl * s > 0) & P['okbar']
            if phases:
                ok &= np.isin(P['ph'], list(phases))
            sh = lambda a, k: np.r_[np.zeros(k, a.dtype), a[:-k]]
            for j in range(1, Kc + 1):
                ok &= (sno == sh(sno, j)) & sh(warm, j) & sh(P['okbar'], j)
            ok &= sh(touch, 1)
            cnt('1 CF dung (than>=50%, delta cung chieu) + cum hop le + nen cuoi cum cham Z', ok.sum())
            if M > 0:
                ext = pd.Series(hi).rolling(Kc).max().shift(1).to_numpy()
                ext2 = pd.Series(lo).rolling(Kc).min().shift(1).to_numpy()
            else:
                ext = pd.Series(lo).rolling(Kc).min().shift(1).to_numpy()
                ext2 = pd.Series(hi).rolling(Kc).max().shift(1).to_numpy()
            crange = np.abs(ext - ext2)
            u1 = np.r_[np.nan, u[:-1]]
            zlast = np.r_[np.nan, zv[:-1]]
            with np.errstate(invalid='ignore'):
                ok &= crange <= 1.5 * u1
                cnt('2 + bien do cum <= 1,5u', ok.sum())
                ok &= (ext <= zlast + 0.5 * u1) if M > 0 else (ext >= zlast - 0.5 * u1)
            cnt('3 + cuc tri cum <= Z + 0,5u', ok.sum())
            mo = P['modeA']
            trend_bad = (mo == ('TREND_UP' if M > 0 else 'TREND_DN'))
            with np.errstate(invalid='ignore'):
                edge_bad = (P['bside'] == M) | ((M > 0) & (np.r_[np.nan, cl[:-1]] > P['bhi'])) | ((M < 0) & (np.r_[np.nan, cl[:-1]] < P['blo']))
            ok &= (~trend_bad) & (~edge_bad) & (P['bs'] > BIG_EXCL)
            cnt('4 + khong TREND cung chieu / pha VA-IB / nen lon nhat phien <=3 nen', ok.sum())
            if bias:
                ok &= (cl > P['vww']) if s > 0 else (cl < P['vww'])
                cnt('4b + bias: BUY tren / SELL duoi VWAP tuan', ok.sum())
            for i in idx[ok]:
                i = int(i)
                a = i - Kc
                z = float(zv[i - 1])
                s0 = max(a - LOOKBACK, int(i - P['posin'][i]))
                if s0 >= a:
                    continue
                if M > 0:
                    e = s0 + int(np.argmin(lo[s0:a]))
                    move = z - lo[e]
                else:
                    e = s0 + int(np.argmax(hi[s0:a]))
                    move = hi[e] - z
                if move < MOVE_MIN:
                    continue
                cnt('5 + move >= 3 gia', 1)
                seg = slice(e, a)
                same = dl[seg] * M > 0
                mad = adl[seg][same].max() if same.any() else adl[seg].max()
                clu = slice(a, i)
                eff = adl[clu][dl[clu] * M > 0].sum()
                if mad <= 0 or eff < mad:
                    continue
                cnt('6 + no luc cum >= |delta| lon nhat cua move', 1)
                if adl[i] < theta * mad:
                    continue
                cnt('7 + |delta_CF| >= theta*max', 1)
                struct = float(hi[a:i].max() if M > 0 else lo[a:i].min())
                r = K.risk(df, i, s, struct, rr=rr)
                if r is None:
                    continue
                cnt('8 + risk() hop le (SL<=4 gia)', 1)
                if i in found:
                    continue
                found[i] = dict(idx=i, side=s, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='B', zone=name, zprice=z,
                                note='B2 %s M=%+d move=%.1f K=%d th=%.1f' % (name, M, move, Kc, theta))
    out = sorted(found.values(), key=lambda e: e['idx'])
    cn, keep = {}, []
    for e in out:
        k = (e['zone'], int(P['sno'][e['idx']]))
        if cn.get(k, 0) >= MAX_PER_ZONE_SESSION:
            continue
        cn[k] = cn.get(k, 0) + 1
        keep.append(e)
    return keep


def run_cfg(P, cfg, th, Nn, rr, phases, funnel=None):
    name, _, kind, bias = cfg
    zones = ('VWAP_D',) if bias else ('VWAP_W', 'VWAP_D')
    if kind == 'old':
        ents = detect(P, th, Nn, zones, 'base', 'ends', funnel, rr=rr, bias=bias, phases=phases)
    else:
        ents = detect2(P, Nn, th, zones, bias, rr, phases, funnel)
    return K.simulate(P['df'], ents)


def ctrl2(P, tr, seeds):
    """Doi chung cung vung/che do/chieu/R:R (che do ma hoa so cho nhanh). Tra mang [wr, avgR, n] theo seed."""
    if len(tr) < 3:
        return np.zeros((0, 3))
    taken = [dict(idx=int(r.idx), side=int(r.side), entry=r.entry, sl=r.sl, tp=r.tp, setup='B', zone=r.zone) for r in tr.itertuples()]
    res = []
    for sd in range(seeds):
        c = K.control_sample(P['df'], P['zc'], P['modecode'], entries=taken, n_random=1, seed=sd)
        if not c:
            continue
        st_ = S(K.simulate(P['df'], c, one_at_a_time=False))
        res.append((st_['wr'], st_['avg_r'], st_['n']))
    return np.array(res)


def split_tr(tr, ds):
    if not len(tr):
        return tr, tr
    if ds == '90':
        return tr[tr['split'] == 'TRAIN'], tr[tr['split'] == 'TEST']
    d = tr['session_id'].str[:10]
    return tr[d <= HALF_CUT], tr[d > HALF_CUT]


def main():
    t0 = time.time()
    r1_txt = main_r1()
    A_ = []
    A = A_.append
    df = K.load_bars(D90 + '_bars.csv')
    P1 = prepare(df, K.build_profiles(df, D90 + '.csv'))
    d2 = K.load_bars(D2Y + '_bars.csv')
    P2 = prepare(d2, K.build_profiles(d2, D2Y + '.csv'))
    days90 = days_in(P1)
    st2 = K.session_table(d2)
    sess_half = np.array([str(x)[:10] <= HALF_CUT for x in st2['session_id']])
    wk_bad = np.unique(d2['week_no'].to_numpy()[d2['splice_jump'].to_numpy()])
    clean = (~st2['splice'].to_numpy()) & (st2['n'].to_numpy() >= K.CONST['min_bars_prof']) & (~st2['thin'].to_numpy()) & (~np.isin(st2['week_no'].to_numpy(), wk_bad))
    dh = (int((clean & sess_half).sum()), int((clean & ~sess_half).sum()))
    st90 = K.session_table(df)
    d90tr = int(((~st90['splice'].to_numpy()) & (st90['n'].to_numpy() >= 300) & (~st90['thin'].to_numpy()) & np.array([str(x)[:10] <= K.CONST['split_train_end'] for x in st90['session_id']])).sum())
    d90te = days90 - d90tr
    RES = {}
    for ds, P in (('90', P1), ('2y', P2)):
        for cfg in CFG:
            for rr in (2.0, 3.0):
                for pn, ph in PHS:
                    for th in TH2:
                        for Nn in K2S:
                            RES[(ds, cfg[0], rr, pn, th, Nn)] = run_cfg(P, cfg, th, Nn, rr, ph)
    print('grid xong %.0fs' % (time.time() - t0), flush=True)

    def cell(cfg, rr, pn, th, Nn):
        a, b = RES[('90', cfg, rr, pn, th, Nn)], RES[('2y', cfg, rr, pn, th, Nn)]
        tr90, te90 = split_tr(a, '90')
        h1, h2 = split_tr(b, '2y')
        return S(tr90), S(te90), S(h1), S(h2), S(a), S(b)

    A('# RESULTS-B (VONG 2) - Setup B Hap thu tai VWAP tuan / ngay')
    A('')
    A('Sinh boi `setup_b_hap_thu.py` (deterministic). Bang vong 1 giu nguyen o CUOI file de so sanh. Gio UTC (VN = UTC+7). R sau chi phi 0,2 gia/lenh; vao o close CF, mo phong tu nen ke tiep; cung nen SL+TP => SL; 1 lenh mo; toi da 2 lenh / (vung, phien).')
    A('')
    A('**WR hoa von sau chi phi:** TP 2R ~ 33-34%, TP 3R ~ 26-27% (chi phi 0,2 gia / SL ~2,5 gia ~ 0,08R). **Phase A (05:00-12:30 VN) bao RIENG**, khong tron vao EU+US (phase A khong co che do nen bo loc TREND/pha VA khong ap dung).')
    A('')
    A('Du lieu: 90d (%d phien sach; TRAIN %d / TEST %d phien) va 2 nam (nua 1 <= %s: %d phien sach; nua 2: %d phien).' % (days90, d90tr, d90te, HALF_CUT, dh[0], dh[1]))
    A('')
    A('Cau hinh: **BASE** = dinh nghia vong 1 (than/|delta| giam dan RONG, cum N nen, theta); **H1** = BASE + bias (chi Z = VWAP ngay; BUY chi khi close nen vao > VWAP tuan, SELL chi khi < VWAP tuan); '
      '**H2** = thay "giam dan" bang "no luc co, ket qua khong" (cum K nen: tong |delta| cac nen cung chieu M >= |delta| nen lon nhat cua move, bien do cum <= 1,5u, cuc tri cum <= Z+0,5u, nen cuoi cum cham Z); **H1+H2**. '
      'Moi cau hinh chay TP 2R va 3R (H3). Luoi = theta {0,3; 0,5} x K (BASE/H1: N) {2,3,4}. O chinh = theta 0,5, K/N 3 (khong chon theo ket qua).')
    A('')
    A('Ghi chu thiet ke H2 (minh bach): "tong |delta| cung chieu M" = tong |delta| cua cac nen trong cum co delta cung dau voi M; chi nen cuoi cum phai cham Z (bien do cum <= 1,5u va cuc tri <= Z+0,5u da giu cum sat Z).')
    A('')
    A('## 0. Cac o DUONG o ca 90d-TEST lan hai nua 2 nam (R TB > 0)')
    A('')
    hits = []
    for key in RES:
        ds, cfg, rr, pn, th, Nn = key
        if ds != '90':
            continue
        trn, te, h1, h2, a90, a2y = cell(cfg, rr, pn, th, Nn)
        if te['n'] > 0 and te['avg_r'] > 0 and h1['n'] > 0 and h1['avg_r'] > 0 and h2['n'] > 0 and h2['avg_r'] > 0:
            hits.append((cfg, rr, pn, th, Nn, trn, te, h1, h2, a90, a2y))
    nall = sum(1 for k in RES if k[0] == '90')
    if hits:
        A('%d / %d o duong o ca 3 phep do. n o TEST 90d nho => **chi la ung vien, khong phai ket luan** (n TEST < 30 => chua ket luan).' % (len(hits), nall))
        A('')
        A('| cau hinh | TP | phase | theta | K/N | 90d TRAIN n, R | 90d TEST n, R | 2y nua1 n, R | 2y nua2 n, R |')
        A('|---|---|---|---|---|---|---|---|---|')
        for h in hits:
            A('| %s | %.0fR | %s | %.1f | %d | %d, %s | %d, %s | %d, %s | %d, %s |' % (h[0], h[1], h[2], h[3], h[4], h[5]['n'], f(h[5]['avg_r']), h[6]['n'], f(h[6]['avg_r']), h[7]['n'], f(h[7]['avg_r']), h[8]['n'], f(h[8]['avg_r'])))
    else:
        A('**Khong o nao duong o ca ba phep do** (trong %d o).' % nall)
    A('')
    A('## 1. Luoi theo cau hinh (moi o: `90d: TRAIN n,R | TEST n,R` va `2y: nua1 n,R | nua2 n,R`; R = R TB sau chi phi)')
    A('')
    for cfg in CFG:
        for rr in (2.0, 3.0):
            for pn, _ in PHS:
                A('### %s - %s - TP %.0fR - phase %s' % (cfg[0], cfg[1], rr, pn))
                A('')
                A('| theta \\ %s | ' % ('N' if cfg[2] == 'old' else 'K') + ' | '.join(str(k) for k in K2S) + ' |')
                A('|---|' + '---|' * len(K2S))
                for th in TH2:
                    row = []
                    for Nn in K2S:
                        trn, te, h1, h2, a90, a2y = cell(cfg[0], rr, pn, th, Nn)
                        row.append('90d: %d,%s \\| %d,%s<br>2y: %d,%s \\| %d,%s' % (trn['n'], f(trn['avg_r']), te['n'], f(te['avg_r']), h1['n'], f(h1['avg_r']), h2['n'], f(h2['avg_r'])))
                    A('| %.1f | ' % th + ' | '.join(row) + ' |')
                A('')
    A('## 2. O chinh (theta 0,5; K/N = 3): tong hop, lenh/ngay, ky vong, doi chung')
    A('')
    A('Doi chung = rut 1 nen ngau nhien / lenh that, cung vung, che do, chieu, R:R; **200 lan tren 90d, 60 lan tren 2 nam**. "p" = ty le lan rut co R TB >= R TB that.')
    A('')
    A('| cau hinh | TP | phase | 90d: n, WR, R TB, ky vong (gia/lenh) | 90d doi chung R TB (sd), p | 2y: n, WR, R TB, ky vong | 2y lenh/ngay | 2y doi chung R TB (sd), p |')
    A('|---|---|---|---|---|---|---|---|')
    for cfg in CFG:
        for rr in (2.0, 3.0):
            for pn, _ in PHS:
                a, b = RES[('90', cfg[0], rr, pn) + MAIN2], RES[('2y', cfg[0], rr, pn) + MAIN2]
                sa, sb = S(a), S(b)
                ca = ctrl2(P1, a, 200)
                cb = ctrl2(P2, b, 60)

                def cs(c, s_):
                    if not len(c):
                        return '-'
                    return '%s (%s), p=%s' % (f(np.nanmean(c[:, 1])), f(np.nanstd(c[:, 1])), pct(float((c[:, 1] >= s_['avg_r']).mean())))
                A('| %s | %.0fR | %s | %d, %s, %s, %s | %s | %d, %s, %s, %s | %s | %s |' % (
                    cfg[0], rr, pn, sa['n'], pct(sa['wr']), f(sa['avg_r']), f(sa['exp_pts']), cs(ca, sa),
                    sb['n'], pct(sb['wr']), f(sb['avg_r']), f(sb['exp_pts']), f(sb['n'] / max(sum(dh), 1)), cs(cb, sb)))
        print('ctrl', cfg[0], '%.0fs' % (time.time() - t0), flush=True)
    A('')
    A('Lenh/ngay 90d o chinh (TP 3R): ' + '; '.join('%s %s = %s' % (c[0], pn, f(S(RES[('90', c[0], 3.0, pn) + MAIN2])['n'] / max(days90, 1))) for c in CFG for pn, _ in PHS))
    A('')
    A('## 3. Tach BUY / SELL (o chinh, EU+US)')
    A('')
    A('| cau hinh | TP | huong | 90d n, WR, R TB | 2y nua1 n, R | 2y nua2 n, R |')
    A('|---|---|---|---|---|---|')
    for cname in ('BASE', 'H1', 'H2', 'H1+H2'):
        for rr in (2.0, 3.0):
            a, b = RES[('90', cname, rr, 'EU+US') + MAIN2], RES[('2y', cname, rr, 'EU+US') + MAIN2]
            h1, h2 = split_tr(b, '2y')
            for sd, lab in ((1, 'BUY'), (-1, 'SELL')):
                fa = a[a['side'] == sd] if len(a) else a
                f1 = h1[h1['side'] == sd] if len(h1) else h1
                f2 = h2[h2['side'] == sd] if len(h2) else h2
                A('| %s | %.0fR | %s | %d, %s, %s | %d, %s | %d, %s |' % (cname, rr, lab, S(fa)['n'], pct(S(fa)['wr']), f(S(fa)['avg_r']), S(f1)['n'], f(S(f1)['avg_r']), S(f2)['n'], f(S(f2)['avg_r'])))
    A('')
    A('## 4. Phieu loc cua H2 o chinh (theta 0,5, K=3, TP 3R, moi phase; so ung vien con lai sau tung dieu kien)')
    A('')
    fh90, fh2y, fh90b, fh2yb = {}, {}, {}, {}
    detect2(P1, 3, 0.5, funnel=fh90)
    detect2(P2, 3, 0.5, funnel=fh2y)
    detect2(P1, 3, 0.5, bias=True, zones=('VWAP_D',), funnel=fh90b)
    detect2(P2, 3, 0.5, bias=True, zones=('VWAP_D',), funnel=fh2yb)
    A('| buoc | 90d | 2 nam | 90d (H1+H2) | 2 nam (H1+H2) |')
    A('|---|---|---|---|---|')
    for k in sorted(set(fh90) | set(fh2y) | set(fh90b) | set(fh2yb)):
        A('| %s | %d | %d | %d | %d |' % (k, fh90.get(k, 0), fh2y.get(k, 0), fh90b.get(k, 0), fh2yb.get(k, 0)))
    A('')
    A('(Dem cong ca hai vung va hai chieu M, chua gom one-at-a-time va tran 2 lenh/vung/phien. Dong 1-4b dem nen; dong 5-8 dem ung vien duyet tuan tu.)')
    A('')
    A('(Thoi gian chay: %.0f giay.)' % (time.time() - t0))
    out = os.path.join(HERE, 'report', 'RESULTS-B.md')
    R1E, R2E, SEP = '\n## Danh gia trung thuc (vong 1)', '\n## Danh gia trung thuc (vong 2)', '\n\n---\n\n# VONG 1 (giu nguyen de so sanh)\n\n'
    prev = open(out, encoding='utf-8').read() if os.path.exists(out) else ''
    e1 = prev[prev.find(R1E):] if R1E in prev else ''
    e2 = ''
    if R2E in prev:
        k0 = prev.find(R2E)
        k1 = prev.find(SEP, k0)
        e2 = prev[k0:k1] if k1 > 0 else prev[k0:]
    open(out, 'w', encoding='utf-8').write('\n'.join(A_) + '\n' + e2 + SEP + r1_txt + '\n' + e1)
    print('\n'.join(A_))

if __name__ == '__main__':
    main()
