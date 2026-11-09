"""Setup C - Fade canh (che do CAN BANG, muc tieu >= 2R). Benzo Trader.

Chay:  python setup_c_fade_canh.py [--reps 200] [--reps2y 60]   -> ghi report/RESULTS-C.md (deterministic, seed co dinh)

Dinh nghia (plan 3-C, khong sua kernel.py):
  * Range: phase A/EU (05:00-19:00 VN) = VA hom qua (yd_vah/yd_val); phase US (19:00-04:00) = VA Au; chua co VA Au thi IB.
  * Che do = kernel.mode_frame tren cac band tren (BALANCE = chua co nen M5 dong ngoai band, hoac da dong lai trong).
  * Pha hut: nen M1 co rau xuyen canh E >= pen_ticks tick va DONG LAI TRONG range (dong < E canh tren / > E canh duoi);
    delta nen ngu chieu vao (sell: delta<0, buy: delta>0). Vao o gia dong nen do.
  * SL = kernel.risk(struct = rau pha hut: high nen (sell) / low nen (buy)).
  * TP 'poc': gan nhat (theo chieu loi) trong {canh doi dien, POC range}; phai >= 2R, neu < 2R thi bo.  TP 'fixed2': 2R co dinh.
  * Loai: nen xuyen la nen dai nhat phien (range >= max range cac nen truoc trong phien); rau NGUOC (rau phia chieu vao: rau duoi
    nen sell, rau tren nen buy) dai hon than; da 2 tin hieu o cung E trong phien; 18:00-19:20 VN (theo sm, bu gio My); splice/thin.
Bien the (vong 2): confirm=True (doi 1 nen M1 nua dong lai trong range, khong cuc tri moi) ; second_touch=True (chi fade lan cham
  thu 2+ cua canh, cach lan cham truoc >= 5 nen).
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
TICK = K.CONST['tick']
HALF_CUT = '2025-08-01'          # 2 nua cua file 2 nam
PEN_GRID = (1, 2, 4)
WIDTH_GRID = (4.0, 6.0, 8.0)
CENTER = (2, 6.0)                # o khoi diem, khai bao TRUOC khi do


# ----------------------------------------------------------------------------------------------
def prepare(base: str) -> dict:
    """Load bars + profile + zone + che do (band: yday cho A/EU, VA Au/IB cho US). Tra dict P."""
    df = K.load_bars(base + '_bars.csv')
    prof = K.build_profiles(df, base + '.csv')
    ctx = K._Ctx(df, prof)
    zc = K.zone_columns(df, prof, ctx)
    zc2 = zc.copy()
    pre = (df['sm'].to_numpy() < K.CONST['sm_us_start'])        # A + EU (truoc 19:00 My)
    for a, b in (('eu_vah', 'yd_vah'), ('eu_val', 'yd_val'), ('eu_poc', 'yd_poc')):
        zc2.loc[pre, a] = zc.loc[pre, b].to_numpy()               # A/EU: band = VA hom qua
    m5 = K.m5_bars(df, zc2)
    mf = K.mode_frame(df, zc2, m5)
    st = K.session_table(df)
    ok = (~st['splice'].to_numpy()) & (~st['thin'].to_numpy()) & (st['n'].to_numpy() >= K.CONST['min_bars_prof'])
    P = dict(df=df, zc=zc2, zc0=zc, mf=mf, st=st, days=int(ok.sum()), mad=K.med_abs_delta(df), prof=prof, ctx=ctx, u=K.median_range(df))
    return P


def detect(df: pd.DataFrame, zones: pd.DataFrame, mode: pd.DataFrame, pen_ticks: int = 2, min_width: float = 6.0,
           tp_mode: str = 'poc', confirm: bool = False, second_touch: bool = False, strong_delta: bool = False,
           mad: pd.Series | None = None, conf=None, min_conf: int = 0, v4: bool = False, u: pd.Series | None = None,
           excl: tuple = (780, 860), gate=None) -> list:
    """Tra list entry cho kernel.simulate. zones = zone_columns da doi band (xem prepare), mode = mode_frame."""
    n = len(df)
    hi, lo, cl, op, dl = (df[c].to_numpy(float) for c in ('high', 'low', 'close', 'open', 'delta'))
    rng = hi - lo
    sm, sno = df['sm'].to_numpy(), df['session_no'].to_numpy()
    phase = df['phase'].to_numpy()
    bh, bl = mode['band_hi'].to_numpy(float), mode['band_lo'].to_numpy(float)
    bsrc = mode['band_src'].to_numpy()
    poc = zones['eu_poc'].to_numpy(float)
    pen = pen_ticks * TICK - 1e-9
    with np.errstate(invalid='ignore'):
        width = bh - bl
        base = (mode['mode'].to_numpy() == 'BALANCE') & (width >= min_width - 1e-9) & (~df['splice'].to_numpy()) & \
               (~df['thin'].to_numpy()) & ~((sm >= excl[0]) & (sm < excl[1])) & np.isin(phase, ['A', 'EU', 'US'])
    cm = pd.Series(rng).groupby(sno).cummax().to_numpy()
    prev = np.r_[-np.inf, cm[:-1]]
    first = np.r_[True, sno[1:] != sno[:-1]]
    prev = np.where(first, -np.inf, prev)
    notbig = rng < prev                                   # khong phai nen dai nhat phien (hoa => coi la dai nhat => loai)
    body = np.abs(cl - op)
    with np.errstate(invalid='ignore'):
        sell = base & notbig & (hi >= bh + pen) & (cl < bh) & (dl < 0) & ((np.minimum(op, cl) - lo) <= body)
        buy = base & notbig & (lo <= bl - pen) & (cl > bl) & (dl > 0) & ((hi - np.maximum(op, cl)) <= body)
    if strong_delta:
        md = (mad if mad is not None else K.med_abs_delta(df)).to_numpy(float)
        with np.errstate(invalid='ignore'):
            sd = np.abs(dl) >= md
        sell &= sd
        buy &= sd
    sstart = df.groupby('session_no').cumcount().to_numpy()
    sstart = np.arange(n) - sstart                        # vi tri nen dau phien
    cands = []                                            # (entry_idx, poke_idx, side, E)
    for j in np.flatnonzero(sell | buy):
        side = -1 if sell[j] else 1
        E = bh[j] if side < 0 else bl[j]
        if second_touch:
            s0 = sstart[j]
            if j - 5 < s0:
                continue
            seg_b = bh[s0:j - 4] if side < 0 else bl[s0:j - 4]
            seg_x = hi[s0:j - 4] >= E - TICK + 1e-9 if side < 0 else lo[s0:j - 4] <= E + TICK - 1e-9
            if not np.any((np.abs(seg_b - E) < 1e-6) & seg_x):
                continue
        i = j
        if confirm:
            i = j + 1
            if i >= n or sno[i] != sno[j] or not base[i] or not notbig[i] or abs((bh[i] if side < 0 else bl[i]) - E) > 1e-6:
                continue
            if side < 0 and not (cl[i] < E and hi[i] <= hi[j]):
                continue
            if side > 0 and not (cl[i] > E and lo[i] >= lo[j]):
                continue
        cands.append((i, j, side, E))
    cands.sort()
    out, count = [], {}
    for i, j, side, E in cands:
        key = (int(sno[j]), round(float(E), 1))
        if count.get(key, 0) >= 2:
            continue
        struct = max(hi[j], hi[i]) if side < 0 else min(lo[j], lo[i])
        r = K.risk(df, i, side, float(struct), rr=2.0)
        if r is None:
            continue
        ent, d = r['entry'], r['risk']
        opp = bl[i] if side < 0 else bh[i]
        if tp_mode == 'poc':
            lv = [opp] + ([poc[i]] if poc[i] == poc[i] else [])
            lv = [x for x in lv if (ent - x) * side * -1 > 0]          # nam ve phia loi
            if not lv:
                continue
            tp = max(lv) if side < 0 else min(lv)
            if abs(tp - ent) < 2.0 * d - 1e-9:
                continue
            tp = round(float(tp), 6)
        else:
            tp = r['tp']
        if phase[i] == 'US':
            nm = ('IB_H' if side < 0 else 'IB_L') if bsrc[i] == 'ib' else ('VAH_EU' if side < 0 else 'VAL_EU')
        else:
            nm = 'VAH_Y' if side < 0 else 'VAL_Y'
        if gate is not None and not gate(int(i), int(j), int(side)):
            continue
        nconf = 1
        if conf is not None:
            nconf = conf.count(int(i), float(E))
            if nconf < min_conf:
                continue
        if v4:
            vd, vw = zones['vwap_d'].to_numpy(float)[i], zones['vwap_w'].to_numpy(float)[i]
            yv, yl = conf.zc0['yd_vah'].to_numpy(float)[i], conf.zc0['yd_val'].to_numpy(float)[i]
            ui = float(u.iloc[i]) if u is not None else float('nan')
            if not (abs(vd - vw) <= 2 * ui and yl <= cl[i] <= yv):          # NaN => False => bo
                continue
        count[key] = count.get(key, 0) + 1
        out.append(dict(nconf=nconf, idx=int(i), side=int(side), entry=ent, sl=r['sl'], tp=tp, setup='C', zone=nm, edge=float(E),
                        poke_idx=int(j), width=float(width[i]), note='fade %s E=%.1f' % (nm, E)))
    return out



class Conf:
    """Dem so vung hop luu quanh canh E (ban kinh 0,7 gia), chi dung vung da biet tai nen i (khong nhin truoc)."""
    R = 0.7

    def __init__(self, P):
        if 'zones_all' not in P:
            P['zones_all'] = K.zones_by_session(P['df'], P['prof'])
        self.z = P['zones_all']
        self.zc0 = P['zc0']
        self.sno = P['df']['session_no'].to_numpy()
        self.cols = {c: self.zc0[c].to_numpy(float) for c in K.ZONE_COLS}

    def count(self, i, E):
        z = self.z[int(self.sno[i])]
        lv = [self.cols[c][i] for c in K.ZONE_COLS]
        lv += [p for p, _ in (z.get('hvn_day') or [])]
        if z.get('hvn_week'):
            lv += [p for p, _ in z['hvn_week']['hvn']]
        nk = [x for x in (z.get('naked') or []) if x['touch_pos'] is None or x['touch_pos'] > i][-K.CONST['naked_max']:]
        lv += [x['price'] for x in nk]
        n = 1
        for p in lv:
            if p == p and abs(p - E) >= 1e-6 and abs(p - E) <= self.R + 1e-9:
                n += 1
        return n

# ----------------------------------------------------------------------------------------------
def run(P: dict, **kw):
    if kw.get('min_conf', 0) or kw.get('annotate') or kw.get('v4'):
        kw = dict(kw); kw.pop('annotate', None)
        kw['conf'] = Conf(P); kw['u'] = P['u']
    kw.pop('annotate', None)
    ent = detect(P['df'], P['zc'], P['mf'], mad=P['mad'], **kw)
    t = K.simulate(P['df'], ent)
    if len(t):
        t['half'] = np.where(pd.to_datetime(t['t_utc']) < pd.Timestamp(HALF_CUT), 'H1', 'H2')
    return ent, t


def closed(t):
    return t[t['outcome'].isin(['TP', 'SL', 'TIME'])] if len(t) else t


def S(t):
    return K._stats(t) if len(t) else dict(n=0, wr=float('nan'), avg_r=float('nan'), exp_pts=float('nan'), sum_r=0.0, max_loss_streak=0)


def f(x, p=2):
    return ('%.*f' % (p, x)) if x == x else '-'


def pct(x):
    return f(100 * x, 1) + '%' if x == x else '-'


def srow(label, s):
    return '| %s | %d | %s | %s | %s | %s | %d |' % (label, s['n'], pct(s['wr']), f(s['avg_r']), f(s['exp_pts']), f(s['sum_r'], 1), s['max_loss_streak'])


HDR = '| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |\n|---|---|---|---|---|---|---|'


def control(P, trades, reps, seed0=1000):
    """Doi chung: moi lan rut 1 nen ngau nhien / lenh that (cung vung, cung che do, cung chieu, cung R:R); lap reps lan."""
    c = closed(trades)
    if len(c) == 0:
        return None
    recs = c.drop(columns=[x for x in c.columns if x in ('outcome', 'exit_idx', 'exit_price', 'pts', 'r', 'hold_bars', 'risk_pts')]).to_dict('records')
    mode = P['mf']['mode']
    ar, wr = [], []
    for k in range(reps):
        ce = K.control_sample(P['df'], P['zc'], mode, entries=recs, n_random=1, seed=seed0 + k)
        tc = closed(K.simulate(P['df'], ce, one_at_a_time=False))
        if len(tc):
            ar.append(float(tc['r'].mean()))
            wr.append(float((tc['r'] > 0).mean()))
    ar, wr = np.array(ar), np.array(wr)
    real = float(c['r'].mean())
    return dict(reps=len(ar), real=real, real_wr=float((c['r'] > 0).mean()), ctrl_mean=float(ar.mean()), ctrl_p5=float(np.percentile(ar, 5)),
                ctrl_p95=float(np.percentile(ar, 95)), ctrl_wr=float(wr.mean()), pctile=float((ar >= real).mean()))


def ctrl_md(c):
    if c is None:
        return 'Khong co lenh de doi chung.'
    return ('Doi chung %d lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung '
            '**%s** (5-95%%: %s .. %s), WR doi chung %s. Setup that: R TB **%s**, WR %s. Ti le lan doi chung >= setup that: **%s**.'
            % (c['reps'], f(c['ctrl_mean']), f(c['ctrl_p5']), f(c['ctrl_p95']), pct(c['ctrl_wr']), f(c['real']), pct(c['real_wr']),
               pct(c['pctile'])))


def examples(t, df, win: bool):
    c = closed(t)
    c = c[c['r'] > 0] if win else c[c['r'] <= 0]
    if len(c) == 0:
        return ['(khong co)']
    idx = np.unique(np.linspace(0, len(c) - 1, min(5, len(c))).round().astype(int))
    L = ['| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |', '|---|---|---|---|---|---|---|---|---|---|']
    for x in c.iloc[idx].itertuples():
        L.append('| %s | %s | %s | %s | %.1f (%s) | %.1f | %.1f | %.1f | %s | %s |' % (
            str(x.t_utc)[:16], str(x.t_vn)[:16], x.phase, 'BUY' if x.side > 0 else 'SELL', x.edge, x.zone, x.entry, x.sl, x.tp,
            x.outcome, f(x.r)))
    return L


def per_phase_day(t, days):
    c = closed(t)
    return ' | '.join('%s %s' % (p, f(len(c[c['phase'] == p]) / max(days, 1), 2)) for p in K.PHASES)


def grid(P, tp_mode, halves=None, widths=WIDTH_GRID, pens=PEN_GRID):
    """Luoi 3x3. halves=None => TRAIN/TEST (cat 09-16); halves=('H1','H2') => 2 nua file 2 nam."""
    L = []
    cols = ('TRAIN', 'TEST') if halves is None else halves
    key = 'split' if halves is None else 'half'
    L += ['| xuyen (tick) | rong range >= | n tong | WR | R TB | n %s | R TB %s | n %s | R TB %s | ky vong gia/lenh |' % (cols[0], cols[0], cols[1], cols[1]),
          '|---|---|---|---|---|---|---|---|---|---|']
    res = {}
    for pen in pens:
        for w in widths:
            _, t = run(P, pen_ticks=pen, min_width=w, tp_mode=tp_mode)
            c = closed(t)
            a = S(t)
            s1 = S(c[c[key] == cols[0]]) if len(c) else S(c)
            s2 = S(c[c[key] == cols[1]]) if len(c) else S(c)
            res[(pen, w)] = (a, s1, s2)
            mark = ' (o khoi diem)' if (pen, w) == CENTER else ''
            L.append('| %d%s | %.0f | %d | %s | %s | %d | %s | %d | %s | %s |' % (pen, mark, w, a['n'], pct(a['wr']), f(a['avg_r']),
                                                                         s1['n'], f(s1['avg_r']), s2['n'], f(s2['avg_r']), f(a['exp_pts'])))
    return L, res


def full_section(title, P, base_kw, reps, half_mode=False, with_ctrl=True):
    df = P['df']
    ent, t = run(P, **base_kw)
    c = closed(t)
    L = ['## ' + title, '', 'Tham so: %s. So phien sach (khong splice/thin, >=300 nen): **%d**.' % (base_kw, P['days']), '']
    if len(c) == 0:
        return L + ['Khong co lenh.', ''], t
    a = S(t)
    L += ['Lenh da dong **%d** (con mo %d); lenh/ngay **%s** (tong 3 phase) = %s' % (a['n'], int((t['outcome'] == 'OPEN').sum()), f(a['n'] / P['days'], 3), per_phase_day(t, P['days'])),
          '', HDR, srow('Tong', a), '']
    L += ['### Theo thang', '', HDR] + [srow(k, S(g)) for k, g in c.groupby('month')] + ['']
    L += ['### Theo phase (A 05:00-12:30 / EU 12:30-19:00 / US 19:00-04:00 VN)', '', HDR] + [srow(p, S(c[c['phase'] == p])) for p in K.PHASES] + ['']
    if half_mode:
        L += ['### Hai nua file 2 nam (cat %s)' % HALF_CUT, '', HDR] + [srow(k, S(c[c['half'] == k])) for k in ('H1', 'H2')] + ['']
    else:
        L += ['### TRAIN (phien <= 2026-09-15) / TEST (>= 2026-09-16)', '', HDR] + [srow(k, S(c[c['split'] == k])) for k in ('TRAIN', 'TEST')] + ['']
    if with_ctrl:
        L += ['### Doi chung', '', ctrl_md(control(P, t, reps)), '']
    L += ['### 5 vi du THANG (chon dan deu theo thoi gian, khong chon dep)', ''] + examples(t, df, True) + ['', '### 5 vi du THUA (dan deu theo thoi gian)', ''] + examples(t, df, False) + ['']
    return L, t


def main():
    reps, reps2 = 200, 60
    if '--round2' in sys.argv:
        q = [int(x) for x in sys.argv[sys.argv.index('--round2') + 1:sys.argv.index('--round2') + 2] if x.isdigit()]
        return round2(q[0] if q else reps)
    if '--reps' in sys.argv:
        reps = int(sys.argv[sys.argv.index('--reps') + 1])
    if '--reps2y' in sys.argv:
        reps2 = int(sys.argv[sys.argv.index('--reps2y') + 1])
    t0 = time.time()
    P = prepare(D90)
    print('prepare 90d %.1fs' % (time.time() - t0), flush=True)
    L = ['# RESULTS-C: Setup C Fade canh (sinh boi setup_c_fade_canh.py, deterministic)', '',
         'Gio trong file = UTC, cot VN = UTC+7. Chi phi 0,2 gia/lenh. 1 lenh mo cung luc. TRAIN <= 2026-09-15, TEST tu 2026-09-16.',
         'O khoi diem (khai bao truoc khi do): xuyen >= 2 tick, range rong >= 6 gia, TP = gan nhat trong {canh doi dien, POC} va >= 2R.', '']
    KW = dict(pen_ticks=CENTER[0], min_width=CENTER[1], tp_mode='poc')
    sec, t90 = full_section('1. File 90d, o khoi diem, TP canh/POC (>= 2R)', P, KW, reps)
    L += sec
    sec, t90f = full_section('2. File 90d, o khoi diem, TP co dinh 2R', P, dict(KW, tp_mode='fixed2'), reps)
    L += sec
    # --- luoi
    L += ['## 3. Luoi 3x3 (xuyen toi thieu x rong range toi thieu), file 90d', '']
    for tm, lab in (('poc', 'TP canh/POC >= 2R'), ('fixed2', 'TP co dinh 2R')):
        gl, _ = grid(P, tm)
        L += ['### ' + lab, ''] + gl + ['']
    L += ['### Phu luc luoi: VA hom qua o file 90d luon rong >= 10 gia nen cot 4/6/8 khong chan lenh nao (cac o giong het nhau). Quet them rong >= 12/16/20/30 (xuyen 2 tick)', '']
    for tm, lab in (('poc', 'TP canh/POC >= 2R'), ('fixed2', 'TP co dinh 2R')):
        gl, _ = grid(P, tm, widths=(12.0, 16.0, 20.0, 30.0), pens=(2,))
        L += ['#### ' + lab, ''] + gl + ['']
    # --- delta manh
    L += ['## 4. Chi giu lenh co delta nen ung ho manh (|delta| >= trung vi |delta| 50 nen truoc do, khong nhin truoc)', '']
    for tm in ('poc', 'fixed2'):
        _, ta = run(P, **dict(KW, tp_mode=tm))
        _, tb = run(P, **dict(KW, tp_mode=tm, strong_delta=True))
        ca, cb = closed(ta), closed(tb)
        L += ['TP %s:' % tm, '', HDR, srow('moi lenh', S(ta)), srow('delta manh', S(tb))]
        for k in ('TRAIN', 'TEST'):
            L += [srow('moi lenh %s' % k, S(ca[ca['split'] == k]) if len(ca) else S(ca)), srow('delta manh %s' % k, S(cb[cb['split'] == k]) if len(cb) else S(cb))]
        L += ['']
    # --- bien the
    L += ['## 5. Hai bien the co che (vong 2), o khoi diem, file 90d', '']
    for name, kw in (('V1 doi 1 nen M1 nua dong lai trong range (confirm)', dict(confirm=True)),
                     ('V2 chi fade lan cham thu 2+ cua canh (second_touch)', dict(second_touch=True))):
        L += ['### ' + name, '']
        for tm in ('poc', 'fixed2'):
            _, tv = run(P, **dict(KW, tp_mode=tm, **kw))
            cv = closed(tv)
            L += ['TP %s:' % tm, '', HDR, srow('tong', S(tv))]
            if len(cv):
                L += [srow(k, S(cv[cv['split'] == k])) for k in ('TRAIN', 'TEST')] + [srow('phase ' + p, S(cv[cv['phase'] == p])) for p in K.PHASES]
                L += ['', ctrl_md(control(P, tv, max(20, reps // 4)))]
            L += ['']
    # --- 2 nam
    print('90d xong %.1fs' % (time.time() - t0), flush=True)
    P2 = prepare(D2Y)
    print('prepare 2y %.1fs' % (time.time() - t0), flush=True)
    L += ['# PHAN 2 NAM: `fp_GC_XCEC_Time_20240801-20260819_748d9h` (ma lien tuc GC, loc +-2 phien quanh cho noi; 2 nua cat %s)' % HALF_CUT, '',
          'Luu y: file nay trung ~1 thang (07-23 -> 08-19/2026) voi file 90d nhung la ma lien tuc GC (khac hop dong GCZ26); doi chung chay %d lan.' % reps2, '']
    sec, _ = full_section('6. 2 nam, o khoi diem, TP canh/POC', P2, KW, reps2, half_mode=True)
    L += sec
    sec, _ = full_section('7. 2 nam, o khoi diem, TP co dinh 2R', P2, dict(KW, tp_mode='fixed2'), reps2, half_mode=True)
    L += sec
    L += ['## 8. Luoi 3x3 tren 2 nam (H1 = 2024-08..2025-07, H2 = 2025-08..2026-08)', '']
    for tm, lab in (('poc', 'TP canh/POC >= 2R'), ('fixed2', 'TP co dinh 2R')):
        gl, _ = grid(P2, tm, halves=('H1', 'H2'))
        L += ['### ' + lab, ''] + gl + ['']
    L += ['### Phu luc luoi 2 nam: rong >= 12/16/20/30 (xuyen 2 tick)', '']
    for tm, lab in (('poc', 'TP canh/POC >= 2R'), ('fixed2', 'TP co dinh 2R')):
        gl, _ = grid(P2, tm, halves=('H1', 'H2'), widths=(12.0, 16.0, 20.0, 30.0), pens=(2,))
        L += ['#### ' + lab, ''] + gl + ['']
    L += ['## 9. Delta manh + bien the tren 2 nam (o khoi diem)', '']
    for tm in ('poc', 'fixed2'):
        L += ['TP %s:' % tm, '', HDR]
        for lab, kw in (('co ban', {}), ('delta manh', dict(strong_delta=True)), ('V1 confirm', dict(confirm=True)), ('V2 cham thu 2+', dict(second_touch=True))):
            _, tv = run(P2, **dict(KW, tp_mode=tm, **kw))
            cv = closed(tv)
            L += [srow(lab, S(tv))]
            if len(cv):
                L += [srow('  ' + lab + ' H1', S(cv[cv['half'] == 'H1'])), srow('  ' + lab + ' H2', S(cv[cv['half'] == 'H2']))]
        L += ['']
    # --- danh gia viet tay (neu co)
    ev = os.path.join(HERE, 'report', 'RESULTS-C.danhgia.md')
    if os.path.exists(ev):
        L += ['', open(ev, encoding='utf-8').read()]
    with open(os.path.join(HERE, 'report', 'RESULTS-C.round1.md'), 'w', encoding='utf-8') as fh:
        fh.write(chr(10).join(L) + chr(10))
    compose()
    print('ghi RESULTS-C.md')


def compose():
    rd = os.path.join(HERE, 'report')
    parts = []
    for fn in ('RESULTS-C.round3.md', 'RESULTS-C.round2.md', 'RESULTS-C.round1.md'):
        fp = os.path.join(rd, fn)
        if os.path.exists(fp):
            txt = open(fp, encoding='utf-8').read()
            if fn.endswith('round1.md'):
                txt = ('**LUU Y (QD-6): VONG 1 duoi day. Cac bang `file 2 nam` (muc 6-9 va phan "PHAN 2 NAM") chi con THAM KHAO, KHONG dung de quyet dinh '
                       '(du lieu footprint truoc do sai ma hop dong). Chi file 90d co gia tri quyet dinh.**') + chr(10) + chr(10) + txt
            parts.append(txt)
    with open(os.path.join(rd, 'RESULTS-C.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n\n---\n\n'.join(parts))


def bucket_rows(t_all, t_filt):
    """Tach theo so vung hop luu: 1 = chi E (lan chay KHONG loc), 2, >=3 (lan chay da loc)."""
    ca, cf = closed(t_all), closed(t_filt)
    rows = [srow('nconf = 1 (chi E, khong hop luu; lan chay khong loc)', S(ca[ca['nconf'] == 1]) if len(ca) else S(ca))]
    rows.append(srow('nconf = 2', S(cf[cf['nconf'] == 2]) if len(cf) else S(cf)))
    rows.append(srow('nconf >= 3', S(cf[cf['nconf'] >= 3]) if len(cf) else S(cf)))
    return rows


def boot_ci(r, n_boot=10000, seed=0):
    """Khoang tin cay bootstrap 95% cho R TB (percentile, seed co dinh)."""
    r = np.asarray(r, float)
    if len(r) < 2:
        return (float('nan'), float('nan'))
    rng = np.random.default_rng(seed)
    m = rng.choice(r, size=(n_boot, len(r)), replace=True).mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def ci_txt(t, label):
    c = closed(t)
    if len(c) == 0:
        return '%s: khong co lenh' % label
    lo, hi = boot_ci(c['r'].to_numpy())
    return '%s: R TB %s, KTC bootstrap 95%% [%s ; %s], n = %d' % (label, f(c['r'].mean()), f(lo), f(hi), len(c))


def round2(reps):
    """Vong 2 (QD-6): CHI file 90d. V3 hop luu, V4 = V3 + ngay khong xu huong."""
    t0 = time.time()
    P = prepare(D90)
    L = ['# VONG 2 - Setup C: hop luu (V3) va ngay khong xu huong (V4) - CHI file 90d (QD-6)', '',
         '**QD-6: chi do tren file 90d GCZ26. File 2 nam (`fp_GC_XCEC_*`) bi bo vi du lieu footprint truoc do sai ma hop dong; moi bang 2 nam trong phan Vong 1 ben duoi chi de tham khao, KHONG dung de quyet dinh.**', '',
         'TRAIN <= 2026-09-15, TEST tu 2026-09-16. Cung seed, o khoi diem (xuyen 2 tick, rong >= 6). V3 = chi fade canh E khi trong ban kinh 0,7 gia quanh E co them >= 1 vung khac '
         '(VWAP ngay/tuan, POC/VAH/VAL hom qua, POC/VAH/VAL Au, IB, HVN ngay/tuan, naked POC; vung trung gia E bi bo). V4 = V3 + |VWAP ngay - VWAP tuan| <= 2u (u = trung vi bien do 50 nen) '
         'va close nen vao nam trong VA hom qua. Doi chung %d lan. Vi n nho, bao them khoang tin cay bootstrap 95%% (10.000 lan, seed 0) cho R TB.' % reps, '']
    base_kw = dict(pen_ticks=CENTER[0], min_width=CENTER[1])
    L += ['## 0. Moc so sanh: o khoi diem vong 1 (khong loc hop luu), file 90d', '']
    for tm in ('poc', 'fixed2'):
        _, tb0 = run(P, **dict(base_kw, tp_mode=tm))
        c0 = closed(tb0)
        L += ['- TP %s: n %d, WR %s, %s; TEST: %s' % (tm, len(c0), pct(S(tb0)['wr']), ci_txt(tb0, 'tong'), ci_txt(tb0[tb0['split'] == 'TEST'] if len(tb0) else tb0, 'TEST'))]
    L += ['']
    cells = []
    for vname, vkw in (('V3 hop luu', dict(min_conf=2)), ('V4 = V3 + ngay khong xu huong', dict(min_conf=2, v4=True))):
        for tm in ('poc', 'fixed2'):
            title = '%s, TP %s' % (vname, 'canh/POC >= 2R' if tm == 'poc' else 'co dinh 2R')
            L += ['## ' + title, '']
            kw = dict(base_kw, tp_mode=tm)
            _, tall = run(P, annotate=True, **kw)
            _, tt = run(P, **dict(kw, **vkw))
            c = closed(tt)
            L += ['Lenh/ngay: **%s** (%s) tren %d phien sach' % (f(S(tt)['n'] / P['days'], 3), per_phase_day(tt, P['days']), P['days']), '', HDR, srow('Tong', S(tt))]
            if len(c):
                for k in ('TRAIN', 'TEST'):
                    L.append(srow(k, S(c[c['split'] == k])))
                L.append(srow('rieng phase US', S(c[c['phase'] == 'US'])))
                for k in ('TRAIN', 'TEST'):
                    L.append(srow('US ' + k, S(c[(c['phase'] == 'US') & (c['split'] == k)])))
                L += [srow('phase ' + p, S(c[c['phase'] == p])) for p in ('A', 'EU')]
            L += bucket_rows(tall, tt) + ['']
            L += ['- ' + ci_txt(tt, 'tong'), '- ' + ci_txt(tt[tt['split'] == 'TEST'] if len(tt) else tt, 'TEST'), '']
            L += [ctrl_md(control(P, tt, reps)) if len(c) else 'Khong co lenh.', '']
            if len(c):
                L += ['Vi du (toi da 5 thang + 5 thua, dan deu):', ''] + examples(tt, P['df'], True) + [''] + examples(tt, P['df'], False) + ['']
            te = S(c[c['split'] == 'TEST']) if len(c) else S(c)
            cells.append((title, S(tt)['n'], te['n'], te['avg_r']))
            print(title, 'xong %.0fs' % (time.time() - t0), flush=True)
    L += ['## Ket luan vong 2', '', '| o | n tong 90d | n TEST | R TB TEST | du tieu chuan (n TEST >= 30 va R TB TEST > 0)? |', '|---|---|---|---|---|']
    passed = False
    for t, nt, n, rt in cells:
        ok = (n >= 30) and rt == rt and rt > 0
        passed |= ok
        L.append('| %s | %d | %d | %s | %s |' % (t, nt, n, f(rt), 'CO' if ok else 'khong'))
    L += ['', ('Co o dat tieu chuan: xem bang (van phai kiem khoang tin cay).' if passed else
               '**Khong o nao co n TEST >= 30 va R TB TEST duong => ket luan cuoi: C tat mac dinh.**')]
    ev = os.path.join(HERE, 'report', 'RESULTS-C.round2.danhgia.md')
    if os.path.exists(ev):
        L += ['', open(ev, encoding='utf-8').read()]
    with open(os.path.join(HERE, 'report', 'RESULTS-C.round2.md'), 'w', encoding='utf-8') as fh:
        fh.write(chr(10).join(L) + chr(10))
    compose()
    print('round2 xong %.0fs' % (time.time() - t0))





if __name__ == '__main__':
    main()
