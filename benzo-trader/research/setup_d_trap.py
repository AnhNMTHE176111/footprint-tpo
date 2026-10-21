"""Setup D - TRAP (Benzo Trader). Dinh nghia: plan muc 3-D. Chay: python setup_d_trap.py  -> report/RESULTS-D.md

Y tuong: co move ro theo chieu S (cung chieu bias), gia hoi nguoc toi mot vung Z (VWAP ngay, VA hom qua, canh VA Au), o cuc tri
nhip hoi phe hoi 'thu va that bai', roi nen xac nhan CF theo S -> vao theo S, SL sau cuc tri nhip hoi, TP 2R.

Hai cach nhan biet 'phe hoi that bai' (do rieng):
  method='delta' : nen cuc tri co delta thuan chieu hoi nhung dong o nua phia chieu S cua bien do (thu va that bai)
  method='cell'  : per-level tai gia cuc tri cua nen cuc tri co o volume >= 2 x trung vi o cua nen do (>= 3 muc gia)
Khong nhin truoc: moi quyet dinh tai nen vao i chi dung nen <= i (zigzag chi dung tu confirm_pos; vung/VWAP/che do tu kernel).

Hang so co dinh (KHONG phai tham so tu do, ghi o day): LEG_MAX_BARS=30 (move ro phai hinh thanh trong 30 nen), PULL_MAX_BARS=30,
PULL_MIN_DEPTH=1.0 gia (nhip hoi toi thieu), CF_WINDOW=3 (CF trong 3 nen sau nen cuc tri), ZONE_TOL=1.0 gia, CELL_MULT=2.0.
Hai tham so tu do: min_move {4,5,7} x max_retr {0.5,0.7,0.9}.
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
REPORT = os.path.join(HERE, 'report', 'RESULTS-D.md')

LEG_MAX_BARS = 30
PULL_MAX_BARS = 30
PULL_MIN_DEPTH = 1.0
CF_WINDOW = 3
ZONE_TOL = 1.0
CELL_MULT = 2.0
# Vong 1 = delta, cell (plan). Bien the co che (toi da 2, chot TRUOC khi xem ket qua bien the):
#   V1 'delta+CFmem': thay CF chat (|delta| >= trung vi) bang 'nen dong theo S vuot dinh/day nen bay' (phe hoi bi nhot khi gia vuot noi ho vua thu)
#   V2 'either+CFmem': nhu V1 nhung nhan biet 'thu va that bai' bang delta HOAC o volume lon (hai cach nhin cung mot hien tuong)
VARIANTS = [('delta', dict(method='delta')), ('cell', dict(method='cell')),
            ('V1 delta+CFmem', dict(method='delta', cf_mode='soft')), ('V2 either+CFmem', dict(method='either', cf_mode='soft'))]
GRID_MOVE = (4.0, 5.0, 7.0)
GRID_RETR = (0.5, 0.7, 0.9)
# vung duoc phep lam Z (plan 3-D): VWAP ngay, POC/VAH/VAL hom qua, canh VA Au
ZONES = [('VWAP_D', 'vwap_d'), ('POC_Y', 'yd_poc'), ('VAH_Y', 'yd_vah'), ('VAL_Y', 'yd_val'), ('VAH_EU', 'eu_vah'), ('VAL_EU', 'eu_val')]


# ----------------------------------------------------------------------------------------------
# CHUAN BI DU LIEU (dung chung moi cau hinh)
# ----------------------------------------------------------------------------------------------
def level_feats(levels_path: str, df: pd.DataFrame) -> dict:
    """Moi nen: volume o muc gia CAO NHAT (top), THAP NHAT (bot), trung vi o (med), so muc (nlev). Doc chunk, khong nhin truoc
    (chi dung du lieu trong chinh nen do)."""
    n = len(df)
    imap = pd.Index(df['bar_idx'].to_numpy())
    out = {k: np.full(n, np.nan) for k in ('top', 'bot', 'med', 'nlev')}
    carry = None

    def proc(body):
        body = body.sort_values(['bar_idx', 'price'], kind='stable')
        g = body.groupby('bar_idx', sort=True)['volume']
        res = pd.DataFrame({'top': g.last(), 'bot': g.first(), 'med': g.median(), 'nlev': g.size()})
        pos = imap.get_indexer(res.index.to_numpy())
        ok = pos >= 0
        for k in out:
            out[k][pos[ok]] = res[k].to_numpy(float)[ok]

    for ch in pd.read_csv(levels_path, usecols=['bar_idx', 'price', 'volume'], chunksize=2_000_000):
        if carry is not None:
            ch = pd.concat([carry, ch], ignore_index=True)
        last = ch['bar_idx'].iloc[-1]
        m = ch['bar_idx'].to_numpy() == last
        carry = ch[m]
        if (~m).any():
            proc(ch[~m])
    if carry is not None and len(carry):
        proc(carry)
    return out


class Prep:
    """Tat ca mang numpy can cho detect (tinh 1 lan cho moi bo du lieu)."""

    def __init__(self, bars_path: str, levels_path: str):
        t0 = time.time()
        self.df = K.load_bars(bars_path)
        df = self.df
        self.prof = K.build_profiles(df, levels_path)
        ctx = K._Ctx(df, self.prof)
        self.zc = K.zone_columns(df, self.prof, ctx)
        self.mode = K.mode_series(df, self.zc)
        self.mad = K.med_abs_delta(df)
        self.cf = {1: K.confirm_bars(df, 1, self.mad).to_numpy(), -1: K.confirm_bars(df, -1, self.mad).to_numpy()}
        self.since_big = K.bars_since_biggest_bar(df).to_numpy()
        self.pivots = K.zigzag(df)
        self.feats = level_feats(levels_path, df)
        self.hi, self.lo = df['high'].to_numpy(float), df['low'].to_numpy(float)
        self.op, self.cl = df['open'].to_numpy(float), df['close'].to_numpy(float)
        self.delta = df['delta'].to_numpy(float)
        self.sno = df['session_no'].to_numpy()
        self.phase = df['phase'].to_numpy()
        self.mode_a = self.mode.to_numpy()
        self.ok_bar = (~df['splice'].to_numpy()) & (~df['thin'].to_numpy())
        self.zarr = {nm: self.zc[col].to_numpy(float) for nm, col in ZONES}
        # bias: dau (close - VWAP tuan) tai nen DAU TIEN cua moi (phien, phase) -> co dinh cho ca phase
        vw = K.vwap_series(df)['vwap_w'].to_numpy()
        raw = np.sign(self.cl - vw)
        key = pd.Series(self.sno.astype(str)).str.cat(pd.Series(self.phase), sep='|')
        first = key.ne(key.shift(1)).to_numpy()
        grp = np.cumsum(first)
        self.bias = pd.Series(np.where(first, raw, np.nan)).groupby(grp).transform('first').to_numpy()
        # V3: 'co move ro' = bien do 60 nen gan nhat (gom nen i) >= 2 x u (u = trung vi bien do 50 nen); khong dat => coi la BALANCE
        r60 = df['high'].rolling(60, min_periods=60).max() - df['low'].rolling(60, min_periods=60).min()
        self.move_clear = (r60 >= 2.0 * K.median_range(df)).to_numpy()
        self.st = K.session_table(df)
        clean = (~self.st['splice'].to_numpy()) & (~self.st['thin'].to_numpy()) & (self.st['n'].to_numpy() >= K.CONST['min_bars_prof'])
        self.n_days = int(clean.sum())
        self.clean_sessions = self.st.loc[clean, 'session_id'].tolist()
        self.load_s = time.time() - t0


# ----------------------------------------------------------------------------------------------
# DETECT
# ----------------------------------------------------------------------------------------------
def detect(P: Prep, min_move: float = 5.0, max_retr: float = 0.7, method: str = 'delta', rr: float = 2.0,
           sides=(1, -1), no_bias: bool = False, extra_zones=(), diag=None, cf_mode: str = 'strict', use_zone: bool = True, sideway: bool = False) -> list:
    """Tra list entry cho kernel.simulate: dict(idx, side, entry, sl, tp, setup, zone, note).
    method 'delta' | 'cell' | 'either'. no_bias=True bo dieu kien bias (de bien the).
    cf_mode 'strict' = kernel.is_confirm_bar (plan); 'soft' = nen dong theo S va dong VUOT dinh/day nen cuc tri (phe hoi bi nhot).
    Entry chi duoc vao khi i >= confirm_pos cua dinh/day zigzag cua move (khong nhin truoc)."""
    df, hi, lo, cl, op, dl = P.df, P.hi, P.lo, P.cl, P.op, P.delta
    out = []
    piv = P.pivots
    n = len(df)
    zn = [z for z in ZONES] + list(extra_zones)

    def dg(k):
        if diag is not None:
            diag[k] = diag.get(k, 0) + 1
    for a, b in zip(piv[:-1], piv[1:]):
        if a['kind'] == b['kind']:
            continue
        S = 1 if (a['kind'] == 'L' and b['kind'] == 'H') else -1     # buy: len roi hoi xuong; sell: xuong roi hoi len
        if S not in sides:
            continue
        p1, p2 = a['pos'], b['pos']
        if P.sno[p1] != P.sno[p2]:
            continue
        move = abs(b['price'] - a['price'])
        if move < min_move or p2 - p1 > LEG_MAX_BARS:
            continue
        top = b['price']
        end = min(n - 1, p2 + PULL_MAX_BARS)
        ext = np.inf if S > 0 else -np.inf       # cuc tri nhip hoi (S>0: day thap nhat)
        j = p2
        while j < end:
            j += 1
            if P.sno[j] != P.sno[p2]:
                break
            if (S > 0 and hi[j] > top) or (S < 0 and lo[j] < top):
                break                              # gia vuot dinh move => khong con la nhip hoi
            if not ((S > 0 and lo[j] <= ext) or (S < 0 and hi[j] >= ext)):
                continue                           # chi xet nen lap cuc tri nhip hoi moi
            ext = lo[j] if S > 0 else hi[j]
            depth = (top - ext) * S
            if depth / move > max_retr:
                break                              # hoi qua sau => loai (va moi nen sau con sau hon)
            if depth < PULL_MIN_DEPTH:
                continue
            # --- phe hoi thu va that bai tai nen cuc tri j ---
            rng = hi[j] - lo[j]
            ok_delta = rng > 0 and (-S * dl[j] > 0) and (S * (cl[j] - (hi[j] + lo[j]) / 2.0) > 0)
            f = P.feats
            nl = f['nlev'][j]
            cell_v = f['bot'][j] if S > 0 else f['top'][j]
            ok_cell = nl == nl and nl >= 3 and f['med'][j] > 0 and cell_v >= CELL_MULT * f['med'][j]
            ok = (ok_delta if method == 'delta' else ok_cell if method == 'cell' else (ok_delta or ok_cell))
            if not ok:
                continue
            # --- Z: vung gan cuc tri (rau cham hoac cach <= 1 gia) ---
            best = None
            for nm, _ in zn:
                zv = P.zarr[nm][j]
                if zv != zv:
                    continue
                d = abs(ext - zv)
                touched = lo[j] <= zv <= hi[j]
                if touched or d <= ZONE_TOL:
                    if best is None or d < best[1]:
                        best = (nm, d, zv)
            if not use_zone:
                best = ('NONE', 0.0, float('nan'))
            if best is None:
                continue
            dg('trap_zone')
            # --- CF theo S trong CF_WINDOW nen sau j, khong nen nao pha cuc tri ---
            ent = None
            for i in range(j + 1, min(n, j + CF_WINDOW + 1)):
                if P.sno[i] != P.sno[j]:
                    break
                if (S > 0 and lo[i] < ext) or (S < 0 and hi[i] > ext):
                    break
                if (S > 0 and hi[i] > top) or (S < 0 and lo[i] < top):
                    break
                if i < b['confirm_pos']:
                    continue                       # dinh/day cua move chua duoc zigzag xac nhan tai nen i
                if cf_mode == 'strict':
                    okcf = P.cf[S][i]
                else:
                    okcf = S * (cl[i] - op[i]) > 0 and S * (cl[i] - (hi[j] if S > 0 else lo[j])) > 0
                if not okcf:
                    continue
                dg('cf')
                if not P.ok_bar[i] or P.phase[i] == 'OFF':
                    dg('x_bar'); break
                if P.mode_a[i] == 'BALANCE':
                    dg('x_balance'); break
                if 1 <= P.since_big[i] <= 3:
                    dg('x_big'); break
                if sideway and P.phase[i] in ('A', 'EU') and not P.move_clear[i]:
                    dg('x_sideway'); break
                if not no_bias and P.bias[i] != S:
                    dg('x_bias'); break
                r = K.risk(df, i, S, ext, rr=rr)
                if r is None:
                    dg('x_risk'); break
                dg('entry')
                ent = dict(idx=int(i), side=S, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='D-' + method, zone=best[0],
                           note='move %.1f retr %.0f%% Z %s %.1f ext %.1f (j=%d)' % (move, 100 * depth / move, best[0], best[2], ext, j))
                break
            if ent is not None:
                out.append(ent)
                break                              # 1 lenh toi da moi cap (L,H)
    return out


# ----------------------------------------------------------------------------------------------
# CHAY + THONG KE
# ----------------------------------------------------------------------------------------------
def run(P: Prep, **kw):
    e = detect(P, **kw)
    t = K.simulate(P.df, e)
    return e, t


def st_of(t, side=None):
    if t is None or len(t) == 0:
        return K._stats(pd.DataFrame(columns=['outcome', 'r', 'pts']))
    if side is not None:
        t = t[t['side'] == side]
    if len(t) == 0:
        return K._stats(pd.DataFrame(columns=['outcome', 'r', 'pts']))
    return K._stats(t)


def f(x, p=2):
    return ('%.*f' % (p, x)) if x == x else '-'


def srow(label, s):
    return '| %s | %d | %s%% | %s | %s | %s | %d |' % (label, s['n'], f(100 * s['wr'], 1), f(s['avg_r']), f(s['exp_pts']), f(s['sum_r'], 1), s['max_loss_streak'])


HDR = '| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |\n|---|---|---|---|---|---|---|'


def control_reps(P: Prep, trades: pd.DataFrame, n_reps: int = 200, seed: int = 0):
    """200 lan doi chung: moi lenh that rut 1 nen ngau nhien cung vung/che do/chieu, cung R:R. Tra (mean R cua tung lan, so lenh doi chung)."""
    tr = trades[trades['outcome'].isin(['TP', 'SL'])]
    if len(tr) == 0:
        return np.array([]), 0
    ents = tr[['idx', 'side', 'entry', 'sl', 'tp', 'setup', 'zone']].to_dict('records')
    ctrl = K.control_sample(P.df, P.zc, P.mode, entries=ents, n_random=n_reps, seed=seed)
    if not ctrl:
        return np.array([]), 0
    ct = K.simulate(P.df, ctrl, one_at_a_time=False)
    ct = ct[ct['outcome'].isin(['TP', 'SL'])]
    ct = ct.assign(src=ct['note'].str.extract(r'idx (\d+)')[0].astype(int))
    rng = np.random.default_rng(seed + 1)
    per = {k: g['r'].to_numpy() for k, g in ct.groupby('src')}
    means = []
    for _ in range(n_reps):
        vals = [rng.choice(v) for v in per.values()]
        means.append(float(np.mean(vals)))
    return np.array(means), len(ct)


def section_cfg(P: Prep, name: str, method: str, grid: dict, base: pd.DataFrame, rr3: pd.DataFrame, L: list, full=True):
    """base = trades cua cau hinh (5, 70%, 2R)."""
    m = K.metrics(base, P.df)
    L += ['### %s - %s (min_move 5, retr <= 70%%, TP 2R)' % (name, method), '']
    if m['n'] == 0:
        L += ['Khong co lenh.', '']
        return
    L += ['Lenh da dong: **%d** (con mo %d). Lenh/ngay (tren %d phien sach): **%s**. Theo phase: A %s - EU %s - US %s (US 19:00-23:00 VN: %s)' % (
        m['n'], m['n_open'], P.n_days, f(m['per_day']),
        *(f(len(base[base['phase'] == p]) / max(P.n_days, 1), 3) for p in K.PHASES),
        f(len(base[(base['phase'] == 'US') & (base['t_vn'].dt.hour >= 19) & (base['t_vn'].dt.hour < 23)]) / max(P.n_days, 1), 3)), '']
    L += [HDR, srow('Tong', m)]
    L += [srow('BUY', st_of(base, 1)), srow('SELL', st_of(base, -1))]
    r3 = rr3
    L += [srow('Tong @TP 3R', st_of(r3))] if r3 is not None else []
    L += ['', '**Theo thang**', '', HDR] + [srow(k, s) for k, s in m['by_month'].items()]
    L += ['', '**Theo phase**', '', HDR] + [srow(k, s) for k, s in m['by_phase'].items()]
    L += ['', '**TRAIN (<= 2026-09-15) / TEST (>= 2026-09-16)**', '', HDR]
    for sp in ('TRAIN', 'TEST'):
        L += [srow(sp, m['by_split'][sp]), srow(sp + ' BUY', st_of(base[base['split'] == sp], 1)), srow(sp + ' SELL', st_of(base[base['split'] == sp], -1))]
    nt = m['by_split']['TEST']['n']
    if nt < 30:
        L += ['', '> **TEST chi co n=%d < 30: CHUA KET LUAN duoc o nua TEST.**' % nt]
    L += ['', '**Theo vung Z**', '', HDR] + [srow(z, st_of(base[base['zone'] == z])) for z in sorted(base['zone'].unique())]
    L += ['']


def examples(base: pd.DataFrame, L: list):
    cl = base[base['outcome'].isin(['TP', 'SL'])]
    for lab, g in (('THANG', cl[cl['r'] > 0]), ('THUA', cl[cl['r'] <= 0])):
        # lay deu theo thoi gian (khong chon loc): 5 lenh cach deu
        g = g.iloc[np.linspace(0, len(g) - 1, min(5, len(g))).astype(int)] if len(g) else g
        L += ['**5 vi du %s (rai deu theo thoi gian, khong chon loc)**' % lab, '',
              '| UTC | VN | side | vao | SL | TP | Z | ket qua | R | ghi chu |', '|---|---|---|---|---|---|---|---|---|---|']
        for x in g.itertuples():
            L += ['| %s | %s | %s | %.1f | %.1f | %.1f | %s | %s | %s | %s |' % (str(x.t_utc)[:16], str(x.t_vn)[:16], 'BUY' if x.side > 0 else 'SELL',
                                                                          x.entry, x.sl, x.tp, x.zone, x.outcome, f(x.r), x.note)]
        L += ['']


def grid_table(P, kw0, rr=2.0):
    cell = {}
    for mv in GRID_MOVE:
        for rt in GRID_RETR:
            e, t = run(P, min_move=mv, max_retr=rt, rr=rr, **kw0)
            cell[(mv, rt)] = t
    return cell


def grid_md(cell, label, which='exp'):
    L = ['**%s**' % label, '', '| min_move \\ retr max | 50% | 70% | 90% |', '|---|---|---|---|']
    for mv in GRID_MOVE:
        row = []
        for rt in GRID_RETR:
            s = st_of(cell[(mv, rt)])
            row.append('n=%d WR %s%% R %s' % (s['n'], f(100 * s['wr'], 0), f(s['avg_r'])))
        L.append('| %g gia | %s |' % (mv, ' | '.join(row)))
    return L + ['']


def split_grid_md(cell, label):
    L = ['**%s** (R TB; TRAIN / TEST; n TEST)' % label, '', '| min_move \\ retr max | 50% | 70% | 90% |', '|---|---|---|---|']
    for mv in GRID_MOVE:
        row = []
        for rt in GRID_RETR:
            t = cell[(mv, rt)]
            a, b = (st_of(t[t['split'] == 'TRAIN']) if len(t) else st_of(t)), (st_of(t[t['split'] == 'TEST']) if len(t) else st_of(t))
            row.append('%s / %s (n %d)' % (f(a['avg_r']), f(b['avg_r']), b['n']))
        L.append('| %g gia | %s |' % (mv, ' | '.join(row)))
    return L + ['']


def funnel_md(P, kw0):
    d = {}
    detect(P, min_move=5.0, max_retr=0.7, diag=d, **kw0)
    nm = [('trap_zone', 'bay + o Z (move>=5, hoi<=70%)'), ('cf', 'co nen CF trong 3 nen'), ('x_bar', 'loai splice/thin/OFF'), ('x_balance', 'loai BALANCE'),
          ('x_big', 'loai 3 nen sau nen dai nhat'), ('x_bias', 'loai nguoc bias'), ('x_risk', 'loai SL > 4 gia'), ('entry', 'vao lenh (truoc luat 1 lenh mo)')]
    return ['Pheu (5/70%): ' + ' -> '.join('%s %d' % (b, d.get(a, 0)) for a, b in nm), '']


def boot_md(trades, label, n_boot=10000, seed=0):
    tr = trades[trades['outcome'].isin(['TP', 'SL'])] if len(trades) else trades
    if len(tr) < 2:
        return ['- Bootstrap %s: n < 2, khong tinh.' % label]
    r = tr['r'].to_numpy(float)
    rng = np.random.default_rng(seed)
    m = r[rng.integers(0, len(r), size=(n_boot, len(r)))].mean(axis=1)
    return ['- Bootstrap 95%% (%d lan) R TB %s: **%s** [%s .. %s], n=%d' % (n_boot, label, f(r.mean()), f(np.percentile(m, 2.5)), f(np.percentile(m, 97.5)), len(r))]


def control_md(P, trades, label):
    means, nc = control_reps(P, trades)
    tr = trades[trades['outcome'].isin(['TP', 'SL'])]
    if len(means) == 0:
        return ['- %s: khong dung duoc doi chung.' % label]
    real = float(tr['r'].mean())
    p = float((means >= real).mean())
    return ['- %s: that R TB **%s** (n=%d) | doi chung 200 lan: R TB %s (5-95%%: %s .. %s); P(doi chung >= that) = **%s**' % (
        label, f(real), len(tr), f(means.mean()), f(np.percentile(means, 5)), f(np.percentile(means, 95)), f(p))]


def full_eval(P: Prep, title: str, L: list, variants=(('delta', dict(method='delta')), ('cell', dict(method='cell'))), do_ctrl=True, ex=True):
    L += ['## ' + title, '',
          'Phien: %d (sach %d). Nen M1: %d.' % (len(P.st), P.n_days, len(P.df)), '']
    out = {}
    for mth, kw0 in variants:
        cell = grid_table(P, kw0)
        base = cell[(5.0, 0.7)]
        _, r3 = run(P, min_move=5.0, max_retr=0.7, rr=3.0, **kw0)
        section_cfg(P, title, mth, cell, base, r3, L)
        L += grid_md(cell, 'Luoi 3x3 (%s, TP 2R, toan bo thoi gian)' % mth)
        L += split_grid_md(cell, 'Luoi 3x3 theo TRAIN/TEST (%s)' % mth)
        L += funnel_md(P, kw0)
        L += boot_md(base, mth + ' 5/70%') + ['']
        if do_ctrl:
            L += ['**Doi chung (%s)**' % mth, ''] + control_md(P, base, 'cau hinh 5/70%') + ['']
        if ex:
            examples(base, L)
        out[mth] = (cell, base)
    return out


def cell_table(P, kw0, moves, retrs, rr=2.0):
    return {(mv, rt): run(P, min_move=mv, max_retr=rt, rr=rr, **kw0)[1] for mv in moves for rt in retrs}


def grid2(cell, moves, retrs, f_cell, label):
    L = ['**%s**' % label, '', '| min_move \ retr max | ' + ' | '.join('%d%%' % round(100 * r) for r in retrs) + ' |', '|---|' + '---|' * len(retrs)]
    for mv in moves:
        L.append('| %g gia | %s |' % (mv, ' | '.join(f_cell(cell[(mv, rt)]) for rt in retrs)))
    return L + ['']


def round2_block(P, name, kw0, moves, retrs, base_key, L, two_year=False):
    cell = cell_table(P, kw0, moves, retrs)
    cut = pd.Timestamp('2025-08-01')

    def halves(t):
        if not len(t):
            return st_of(t), st_of(t)
        if two_year:
            tt = pd.to_datetime(t['t_utc'])
            return st_of(t[tt < cut]), st_of(t[tt >= cut])
        return st_of(t[t['split'] == 'TRAIN']), st_of(t[t['split'] == 'TEST'])
    h1, h2 = ('nua 1', 'nua 2') if two_year else ('TRAIN', 'TEST')

    def fc(t):
        s_ = st_of(t); a, b = halves(t)
        return 'n=%d R %s ; %s %s (n%d) / %s %s (n%d)' % (s_['n'], f(s_['avg_r']), h1, f(a['avg_r']), a['n'], h2, f(b['avg_r']), b['n'])
    L += grid2(cell, moves, retrs, fc, 'Luoi %s (R TB tong ; %s / %s)' % (name, h1, h2))
    base = cell[base_key]
    a, b = halves(base)
    days = P.n_days
    L += ['Chi tiet cau hinh (move %g, hoi <= %d%%): ' % (base_key[0], round(100 * base_key[1])), '', HDR, srow('Tong', st_of(base)), srow('BUY', st_of(base, 1)), srow('SELL', st_of(base, -1)),
          srow(h1, a), srow(h2, b)]
    if len(base):
        L += [srow('Phase ' + p + ' (%.3f lenh/ngay)' % (len(base[base['phase'] == p]) / days), st_of(base[base['phase'] == p])) for p in K.PHASES]
        L += [srow(h1 + ' BUY', st_of(halves_df(base, two_year, cut, 0), 1)), srow(h1 + ' SELL', st_of(halves_df(base, two_year, cut, 0), -1)),
              srow(h2 + ' BUY', st_of(halves_df(base, two_year, cut, 1), 1)), srow(h2 + ' SELL', st_of(halves_df(base, two_year, cut, 1), -1))]
    L += ['', 'Lenh/ngay tong: %s (%d phien sach). TEST/nua 2 n=%d%s' % (f(len(base) / days, 3), days, b['n'], ' (< 30: CHUA KET LUAN)' if b['n'] < 30 else ''), '']
    L += funnel_md2(P, kw0, base_key)
    L += boot_md(base, 'cau hinh chinh') + ['']
    L += ['**Doi chung**', ''] + control_md(P, base, 'cung vung(khong co)/che do/chieu, 200 lan') + ['']
    return cell


def halves_df(t, two_year, cut, k):
    if two_year:
        tt = pd.to_datetime(t['t_utc'])
        return t[tt < cut] if k == 0 else t[tt >= cut]
    return t[t['split'] == ('TRAIN' if k == 0 else 'TEST')]


def funnel_md2(P, kw0, key):
    d = {}
    detect(P, min_move=key[0], max_retr=key[1], diag=d, **kw0)
    nm = [('trap_zone', 'bay (move+hoi+delta that bai)'), ('cf', 'co nen CF chat trong 3 nen'), ('x_bar', 'loai splice/thin/OFF'), ('x_balance', 'loai BALANCE (che do)'),
          ('x_big', 'loai 3 nen sau nen dai nhat'), ('x_sideway', 'loai sideway A/Au (60 nen < 2u)'), ('x_bias', 'loai nguoc bias'), ('x_risk', 'loai SL > 4 gia'), ('entry', 'vao lenh (truoc luat 1 lenh mo)')]
    return ['Pheu: ' + ' -> '.join('%s %d' % (b, d.get(a, 0)) for a, b in nm), '']


def round2(P90, P2, L):
    L += ['## VONG 2 - bo yeu cau vung Z (V3, V4)', '',
          'V3 = delta, CF chat, KHONG can Z, them loc sideway phase A/Au (bien do 60 nen gan nhat < 2 x u, u = trung vi bien do 50 nen => loai). Luoi 3x3 nhu cu. '
          'V4 = V3 voi luoi move {3,4,5} x hoi {50,70%}. Cung seed 0, doi chung 200 lan. Chi tiet in cho cau hinh: V3 5/70%, V4 3/70% (o co n lon nhat - chon vi muc tieu V4 la xem n).', '']
    V3, V4 = dict(method='delta', use_zone=False, sideway=True), dict(method='delta', use_zone=False, sideway=True)
    for nm, kw0, mv, rt, key in (('V3', V3, GRID_MOVE, GRID_RETR, (5.0, 0.7)), ('V4', V4, (3.0, 4.0, 5.0), (0.5, 0.7), (3.0, 0.7))):
        L += ['### %s - file 90d' % nm, '']
        round2_block(P90, nm + ' 90d', kw0, mv, rt, key, L)


def main():
    t0 = time.time()
    L = ['# RESULTS-D - Setup D Trap (sinh boi setup_d_trap.py, deterministic)', '',
         '**QD-6: chi do tren file 90d GCZ26. Bang 2 nam cu nam o `RESULTS-D-2y-cu-tham-khao.md` va chi de tham khao (sai ma hop dong), khong dung quyet dinh.** Dinh nghia: plan 3-D. Hang so co dinh: move ro hinh thanh <= %d nen; nhip hoi <= %d nen, sau >= %.1f gia; CF trong %d nen sau nen cuc tri; '
         'Z cach cuc tri <= %.1f gia hoac rau cham; o volume >= %gx trung vi o (>= 3 muc). Chi phi 0,2 gia/lenh, 1 lenh mo cung luc, SL = kernel.risk (cau truc = cuc tri nhip hoi). '
         'Gio UTC / VN = UTC+7. 2 tham so tu do: min_move x retr max (luoi 3x3).' % (LEG_MAX_BARS, PULL_MAX_BARS, PULL_MIN_DEPTH, CF_WINDOW, ZONE_TOL, CELL_MULT), '']
    P90 = Prep(D90 + '_bars.csv', D90 + '.csv')
    res90 = full_eval(P90, 'File 90d (GCZ26, 2026-07-23 -> 2026-10-21)', L, variants=VARIANTS, ex=True)
    round2(P90, None, L)
    ass = os.path.join(HERE, 'report', '_assessment_D.md')
    if os.path.exists(ass):
        L += [open(ass, encoding='utf-8').read()]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('xong %.0fs -> %s' % (time.time() - t0, REPORT))


if __name__ == '__main__':
    main()
