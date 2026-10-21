"""SETUP A - PHA HOI (Benzo Trader). Dung kernel.py (khong sua kernel).

Chay: python setup_a_pha_hoi.py            (in bang cho file 90d)
      python setup_a_pha_hoi.py --all      (90d + 2 nam + bien the, ghi report/RESULTS-A.md)

detect(df, zcols, ...) -> list entries cho kernel.simulate. Deterministic (seed co dinh).

Dinh nghia (plan muc 3-A), ghi ro cac lua chon cua agent:
  * E = canh VA Au hom nay (US, sau 19:00 VN; chua co thi IB); phase A/EU/OFF dung VA hom qua.
  * Cu pha = 1 nen M5 DONG ngoai band theo chieu S, nen M5 khong nam trong 18:00-19:20 VN (sm 780..859).
  * 'Move pha' = cac nen M1 tu nen dong cuoi cung o phia trong band (toi da 60 nen lui) den nen cuoi M5 pha. L = bien do dai nhat.
  * Nhip hoi = cac nen M1 SAU dinh (cuc tri) cua move toi nen ngay truoc CF. Dem >= n_min, khong nen nao bien do >= L (loai hinh V).
  * Huy trang thai khi co nen M5 dong LAI TRONG band (hoac doi nguon band, hoac het phien); CF phai o truoc nen M1 dong M5 do.
  * Cham E: |close - E| <= 1 hoac rau cham E.   CF = kernel.confirm_bars(than >= body).
  * SL: struct = xa nhat cua (rau CF, E -/+ 1,0 [mep xa vung E, vung = E +-1 theo 'cach vung <= 1 gia']); kernel.risk (+0,3, san, tran 4). TP 3R.
  * Loai: 3 nen sau nen dai nhat phien, phien splice/thin, da 2 lenh o cung E trong phien, phase OFF.
"""
from __future__ import annotations

import os
import sys
import contextlib

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
DD = os.path.join(ROOT, 'data-export', 'data-footprint')
D90 = os.path.join(DD, 'fp_GCZ26_XCEC_Time_20260723-20261021_90d')
D2Y = os.path.join(DD, 'fp_GC_XCEC_Time_20240801-20260819_748d9h')

RR = 3.0
ZONE_HALF = 1.0          # nua be rong vung E (= 'cach vung <= 1 gia')
LEG_LOOKBACK = 60
SM_NOPHA = (780, 860)    # 18:00-19:20 VN
GRID_N = (2, 3, 4)
GRID_BODY = (0.4, 0.5, 0.6)
HALF_SPLIT_2Y = '2025-08-01'


@contextlib.contextmanager
def cf_body(frac):
    old = K.CONST['cf_body_frac']
    K.CONST['cf_body_frac'] = frac
    try:
        yield
    finally:
        K.CONST['cf_body_frac'] = old


def band_arrays(df, zc, m5):
    """Band E theo tung nen M5 (tai nen M1 cuoi cua M5): US -> VA Au (chua co -> IB); A/EU/OFF -> VA hom qua."""
    lp = m5['last_pos'].to_numpy()
    ph = df['phase'].to_numpy()[lp]
    us = ph == 'US'
    eh, el = zc['eu_vah'].to_numpy()[lp], zc['eu_val'].to_numpy()[lp]
    ih, il = zc['ib_hi'].to_numpy()[lp], zc['ib_lo'].to_numpy()[lp]
    yh, yl = zc['yd_vah'].to_numpy()[lp], zc['yd_val'].to_numpy()[lp]
    use_eu = us & ~np.isnan(eh)
    use_ib = us & np.isnan(eh) & ~np.isnan(ih)
    use_y = (~us) & ~np.isnan(yh)
    bh = np.where(use_eu, eh, np.where(use_ib, ih, np.where(use_y, yh, np.nan)))
    bl = np.where(use_eu, el, np.where(use_ib, il, np.where(use_y, yl, np.nan)))
    src = np.where(use_eu, 'EU', np.where(use_ib, 'IB', np.where(use_y, 'Y', '')))
    return bh, bl, src


def detect(df, zcols, m5=None, n_min=3, body=0.5, delta_break=False, cands=None, hold_edge=False):
    """Tra list entries. cands (list) neu cho: nhan them cac nen 'ung vien doi chung' (trong trang thai pha, cham E, hop le) -
    chua kiem nhip hoi / CF. delta_break (bien the V1): nen M5 pha phai co delta cung chieu S.
    hold_edge (bien the V2): nen CF phai dong o phia NGOAI E (buy: close >= E; sell: close <= E)."""
    extra_filter = None
    m5 = K.m5_bars(df) if m5 is None else m5
    bh, bl, src = band_arrays(df, zcols, m5)
    cl, op, hi, lo = (df[c].to_numpy(float) for c in ('close', 'open', 'high', 'low'))
    rng = hi - lo
    sm = df['sm'].to_numpy()
    phase = df['phase'].to_numpy()
    bad = df['splice'].to_numpy() | df['thin'].to_numpy()
    mad = K.med_abs_delta(df)
    with cf_body(body):
        cf = {1: K.confirm_bars(df, 1, mad).to_numpy(), -1: K.confirm_bars(df, -1, mad).to_numpy()}
    sbig = K.bars_since_biggest_bar(df).to_numpy()
    st = K.session_table(df)
    end_of = dict(zip(st.index.to_numpy(), st['end_pos'].to_numpy()))
    start_of = dict(zip(st.index.to_numpy(), st['start_pos'].to_numpy()))
    m5_sno = m5['session_no'].to_numpy()
    m5_lp = m5['last_pos'].to_numpy()
    m5_close = m5['close'].to_numpy(float)
    m5_delta = m5['delta'].to_numpy(float)
    vw_d = zcols['vwap_d'].to_numpy(float)
    entries = []
    count = {}

    def scan(state, q):
        """Quet nen M1 i trong (p0, q) cua trang thai."""
        S, E, p0, L, srcn, s = state['S'], state['E'], state['p0'], state['L'], state['src'], state['s']
        pk_pos, pk_val = state['pk_pos'], state['pk_val']
        pbmax = 0.0
        for k in range(pk_pos + 1, p0 + 1):
            pbmax = max(pbmax, rng[k])
        if srcn == 'IB':
            zname = 'IB_H' if S > 0 else 'IB_L'
        elif srcn == 'VW':
            zname = 'VWAP_D'
        else:
            zname = ('VAH' if S > 0 else 'VAL') + ('_Y' if srcn == 'Y' else '_EU')
        key = (s, srcn, S, round(E, 1))
        for i in range(p0 + 1, q):
            ok = (not bad[i]) and phase[i] != 'OFF' and not (1 <= sbig[i] <= 3)
            near = abs(cl[i] - E) <= 1.0 or (lo[i] <= E <= hi[i])
            if ok and near:
                if cands is not None:
                    cands.append(dict(idx=i, side=S, E=E, zone=zname, key=key))
                npb = i - 1 - pk_pos
                if (npb >= n_min and pbmax < L and cf[S][i] and count.get(key, 0) < 2
                        and (not hold_edge or (cl[i] - E) * S >= 0)):
                    struct = min(lo[i], E - ZONE_HALF) if S > 0 else max(hi[i], E + ZONE_HALF)
                    r = K.risk(df, i, S, struct, rr=RR)
                    if r is not None:
                        entries.append(dict(idx=i, side=S, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='A', zone=zname,
                                            E=E, L=L, npb=npb, p0=p0,
                                            note='pha %s E=%.1f hoi %d nen' % ('len' if S > 0 else 'xuong', E, npb)))
                        count[key] = count.get(key, 0) + 1
                        pk_pos, pk_val, pbmax = i, (hi[i] if S > 0 else lo[i]), 0.0
                        continue
            if (S > 0 and hi[i] > pk_val) or (S < 0 and lo[i] < pk_val):
                pk_pos, pk_val, pbmax = i, (hi[i] if S > 0 else lo[i]), 0.0
            else:
                pbmax = max(pbmax, rng[i])

    def make_state(out, E, lp, a, srcn, s):
        k = lp
        lim = max(a, lp - LEG_LOOKBACK)
        while k > lim and ((cl[k] > E) if out > 0 else (cl[k] < E)):
            k -= 1
        leg = np.arange(k + 1, lp + 1) if k < lp else np.array([lp])
        L = float(rng[leg].max())
        pk_pos = int(leg[np.argmax(hi[leg])] if out > 0 else leg[np.argmin(lo[leg])])
        return dict(S=out, E=float(E), p0=lp, L=L, src=srcn, s=int(s), pk_pos=pk_pos,
                    pk_val=float(hi[pk_pos] if out > 0 else lo[pk_pos]))

    for s in st.index.to_numpy():
        rows = np.flatnonzero(m5_sno == s)
        state = None
        a = int(start_of[s])
        for j in rows:
            lp = int(m5_lp[j])
            if bh[j] != bh[j]:
                if state:
                    scan(state, lp)
                    state = None
                continue
            if state and state['src'] != src[j]:
                scan(state, lp)
                state = None
            c = m5_close[j]
            out = 1 if c > bh[j] else (-1 if c < bl[j] else 0)
            if out == 0:
                if state:
                    scan(state, lp)
                    state = None
                continue
            if state and state['S'] == out:
                continue
            if state:
                scan(state, lp)
                state = None
            if SM_NOPHA[0] <= sm[lp] < SM_NOPHA[1]:
                continue
            if delta_break and m5_delta[j] * out <= 0:
                continue
            E = bh[j] if out > 0 else bl[j]
            state = make_state(out, E, lp, a, src[j], s)
        if state:
            scan(state, int(end_of[s]) + 1)
    entries.sort(key=lambda e: e['idx'])
    return entries


# ---------------------------------------------------------------------------------------------
# Pipeline + do dem
# ---------------------------------------------------------------------------------------------
class Data:
    def __init__(self, base):
        self.df = K.load_bars(base + '_bars.csv')
        self.prof = K.build_profiles(self.df, base + '.csv')
        self.ctx = K._Ctx(self.df, self.prof)
        self.zc = K.zone_columns(self.df, self.prof, self.ctx)
        self.m5 = K.m5_bars(self.df)
        self.mode = K.mode_series(self.df, self.zc)
        st = K.session_table(self.df)
        self.days = int((~st['splice'].to_numpy() & ~st['thin'].to_numpy() & (st['n'].to_numpy() >= K.CONST['min_bars_prof'])).sum())


def run(D, n_min=3, body=0.5, **kw):
    ent = detect(D.df, D.zc, D.m5, n_min=n_min, body=body, **kw)
    tr = K.simulate(D.df, ent)
    return ent, tr


def stat(tr):
    if len(tr) == 0:
        return dict(n=0, wr=float('nan'), avg_r=float('nan'), exp_pts=float('nan'), sum_r=0.0, max_loss_streak=0)
    return K._stats(tr)


def control_kernel(D, ent, n_draw=200, seed0=0):
    """kernel.control_sample cach 1: moi lenh that rut 1 nen cung vung/che do/chieu; lap n_draw lan. Tra mang avg R moi lan."""
    res = []
    for d in range(n_draw):
        ce = K.control_sample(D.df, D.zc, D.mode, entries=ent, n_random=1, seed=seed0 + d, tol=1.0)
        t = K.simulate(D.df, ce, one_at_a_time=False)
        c = t[t['outcome'].isin(['TP', 'SL', 'TIME'])] if len(t) else t
        res.append(float(c['r'].mean()) if len(c) else float('nan'))
    return np.array(res)


def control_state(D, ent, cands, n_draw=200, seed0=1000):
    """Doi chung cung trang thai pha: nen ngau nhien trong trang thai pha, cham E, cung chieu, SL/TP y het (khong dung nhip hoi / CF)."""
    real = {e['idx'] for e in ent}
    pool = []
    for c in cands:
        if c['idx'] in real:
            continue
        i, S = c['idx'], c['side']
        struct = min(D.df['low'].iat[i], c['E'] - ZONE_HALF) if S > 0 else max(D.df['high'].iat[i], c['E'] + ZONE_HALF)
        r = K.risk(D.df, i, S, struct, rr=RR)
        if r:
            pool.append(dict(idx=i, side=S, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='CTRL-A', zone=c['zone']))
    res = []
    if not pool or not ent:
        return np.array(res), len(pool)
    for d in range(n_draw):
        rng = np.random.default_rng(seed0 + d)
        pick = rng.choice(len(pool), size=min(len(ent), len(pool)), replace=False)
        t = K.simulate(D.df, [pool[p] for p in sorted(pick)], one_at_a_time=False)
        res.append(float(t['r'].mean()) if len(t) else float('nan'))
    return np.array(res), len(pool)


def f(x, p=2):
    return ('%.*f' % (p, x)) if x == x else '-'


def grid_table(D, **kw):
    rows = {}
    for nm in GRID_N:
        for bd in GRID_BODY:
            ent, tr = run(D, nm, bd, **kw)
            sp = {k: stat(tr[tr['split'] == k]) if len(tr) else stat(tr) for k in ('TRAIN', 'TEST')}
            rows[(nm, bd)] = (stat(tr), sp, len(ent))
    return rows


def print_grid(rows, title=''):
    print(title)
    print('n_hoi body |   n   WR%   avgR | TRAIN n  avgR | TEST n  avgR')
    for (nm, bd), (s, sp, _) in rows.items():
        print('%4d  %.1f | %4d %5s %6s | %5d %6s | %5d %6s' % (nm, bd, s['n'], f(100 * s['wr'], 1), f(s['avg_r']), sp['TRAIN']['n'],
                                                         f(sp['TRAIN']['avg_r']), sp['TEST']['n'], f(sp['TEST']['avg_r'])))


VARIANTS = {
    'V1 delta nen M5 pha cung chieu': dict(delta_break=True),
    'V2 giu canh (CF dong phia ngoai E)': dict(hold_edge=True),
}


def row(name, s):
    return '| %s | %d | %s%% | %s | %s | %s | %d |' % (name, s['n'], f(100 * s['wr'], 1), f(s['avg_r']), f(s['exp_pts']), f(s['sum_r'], 1), s['max_loss_streak'])


HDR = '| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |\n|---|---|---|---|---|---|---|'


def halves(tr, cut):
    ts = pd.to_datetime(tr['t_utc'])
    return stat(tr[ts < cut]), stat(tr[ts >= cut])


def examples_md(tr, k=5):
    c = tr[tr['outcome'].isin(['TP', 'SL'])]
    out = []
    for lab, g in (('THANG', c[c['r'] > 0]), ('THUA', c[c['r'] <= 0])):
        if len(g) > k:
            g = g.iloc[np.unique(np.linspace(0, len(g) - 1, k).round().astype(int))]
        out += ['#### Vi du %s (chon cach deu theo thoi gian)' % lab, '',
                '| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |',
                '|---|---|---|---|---|---|---|---|---|---|---|---|']
        for x in g.itertuples():
            out.append('| %s | %s | %s | %s | %s | %.1f | %.1f | %.1f | %.1f | %s | %.2f | %d |' % (
                str(x.t_utc)[:16], str(x.t_vn)[:16], 'BUY' if x.side > 0 else 'SELL', x.phase, x.zone, x.E, x.entry, x.sl, x.tp, x.outcome, x.r, x.npb))
        out.append('')
    return out


def full_block(title, D, kw, cut=None, n_ctrl=200, kernel_ctrl=True):
    """Tra (list dong markdown, trades) cho mot dataset (+ bien the kw)."""
    L = ['## ' + title, '']
    cands = []
    ent = detect(D.df, D.zc, D.m5, 3, 0.5, cands=cands, **kw)
    tr = K.simulate(D.df, ent)
    m = K.metrics(tr, D.df)
    L += ['Phien sach (khong splice/thin, >= 300 nen): **%d**. Cell chinh = (n_hoi 3, than CF 0,5). Hoa von o 3R sau chi phi ~27%% WR (0,2 gia ~ 0,1R).' % D.days, '']
    if m['n'] == 0:
        return L + ['Khong co lenh.', ''], tr
    L += ['Lenh da dong **%d** (con mo %d) | **%s lenh/ngay** tong 3 phase | theo phase: %s' % (
        m['n'], m['n_open'], f(m['per_day']),
        ', '.join('%s %s/ngay (n=%d)' % (ph, f(m['by_phase'][ph]['n'] / D.days), m['by_phase'][ph]['n']) for ph in K.PHASES)), '',
        HDR, row('Tong', m), '']
    L += ['### Theo phase', '', HDR] + [row(k, v) for k, v in m['by_phase'].items()] + ['']
    L += ['### Theo vung E', '', HDR] + [row(k, stat(tr[tr['zone'] == k])) for k in sorted(tr['zone'].unique())] + ['']
    if cut is None:
        L += ['### TRAIN (<= 2026-09-15) / TEST (>= 2026-09-16)', '', HDR] + [row(k, v) for k, v in m['by_split'].items()] + ['']
        if m['by_split']['TEST']['n'] < 30:
            L += ['> **TEST co n=%d < 30: CHUA KET LUAN DUOC tren nua TEST cua file 90d.**' % m['by_split']['TEST']['n'], '']
    else:
        h1, h2 = halves(tr, cut)
        L += ['### Hai nua (cat %s)' % str(cut)[:10], '', HDR, row('Nua 1 (truoc cat)', h1), row('Nua 2 (sau cat)', h2), '']
    L += ['### Theo thang', '', HDR] + [row(k, v) for k, v in m['by_month'].items()] + ['']
    L += ['### Luoi 3x3 (so nen hoi toi thieu x ti le than CF)', '',
          '| n_hoi | than CF | n | WR | R TB | ' + ('TRAIN n / R | TEST n / R |' if cut is None else 'Nua1 n / R | Nua2 n / R |'),
          '|---|---|---|---|---|---|---|']
    for nm in GRID_N:
        for bd in GRID_BODY:
            e2 = detect(D.df, D.zc, D.m5, nm, bd, **kw)
            t2 = K.simulate(D.df, e2)
            s = stat(t2)
            a, b = (stat(t2[t2['split'] == 'TRAIN']), stat(t2[t2['split'] == 'TEST'])) if cut is None else halves(t2, cut)
            L.append('| %d | %.1f | %d | %s%% | %s | %d / %s | %d / %s |' % (nm, bd, s['n'], f(100 * s['wr'], 1), f(s['avg_r']), a['n'], f(a['avg_r']), b['n'], f(b['avg_r'])))
    L.append('')
    ctl, npool = control_state(D, ent, cands, n_draw=n_ctrl)
    L += ['### Doi chung (%d lan lay mau)' % n_ctrl, '']
    if len(ctl):
        L += ['- **Cung trang thai pha** (nen ngau nhien trong trang thai pha, cham E, cung chieu, SL/TP y het, bo nhip hoi + CF; ho %d nen): '
              'R TB doi chung = **%s** (5-95%%: %s .. %s); lenh that = **%s**; ti le lan doi chung >= lenh that: **%s%%**.' % (
                  npool, f(np.nanmean(ctl)), f(np.nanpercentile(ctl, 5)), f(np.nanpercentile(ctl, 95)), f(m['avg_r']), f(100 * np.mean(ctl >= m['avg_r']), 1))]
    if kernel_ctrl:
        ck = control_kernel(D, ent, n_draw=n_ctrl)
        L += ['- **kernel.control_sample** (cung vung E, cung che do, cung chieu, 1 nen ngau nhien/lenh that, khong can trang thai pha): '
              'R TB = **%s** (5-95%%: %s .. %s); ti le lan doi chung >= lenh that: **%s%%**.' % (
                  f(np.nanmean(ck)), f(np.nanpercentile(ck, 5)), f(np.nanpercentile(ck, 95)), f(100 * np.mean(ck >= m['avg_r']), 1))]
    L.append('')
    L += examples_md(tr)
    return L, tr


def main_all():
    out = ['# RESULTS-A - Setup A Pha hoi (Benzo Trader)', '',
           'Sinh boi `setup_a_pha_hoi.py --all` (deterministic, seed co dinh). Chi phi 0,2 gia/lenh, TP 3R, gio UTC va VN (UTC+7). '
           'Dinh nghia chi tiet o docstring cua script.', '']
    D = Data(D90)
    L, _ = full_block('1. File 90d (GCZ26, 2026-07-23 -> 2026-10-21), TRAIN <= 09-15, TEST >= 09-16', D, {})
    out += L
    D2 = Data(D2Y)
    cut = pd.Timestamp(HALF_SPLIT_2Y)
    L, _ = full_block('2. File 2 nam (GC lien tuc 2024-08 -> 2026-08, loc splice/thin), 2 nua cat 2025-08-01', D2, {}, cut=cut)
    out += L
    out += ['# Bien the co che (moi bien the bao rieng, khong tron)', '']
    for name, vkw in VARIANTS.items():
        for lab, DD_, ct in (('90d', D, None), ('2 nam', D2, cut)):
            L, _ = full_block('%s - %s' % (name, lab), DD_, vkw, cut=ct, kernel_ctrl=False)
            out += L
    ev = os.path.join(HERE, 'report', '_eval_a_source.txt')
    if os.path.exists(ev):
        with open(ev, encoding='utf-8') as fh:
            out.append(fh.read())
    return out


if __name__ == '__main__':
    if '--all' in sys.argv:
        lines = main_all()
        with open(os.path.join(HERE, 'report', 'RESULTS-A.md'), 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines))
        print('ghi report/RESULTS-A.md')
        sys.exit(0)
    D = Data(D90)
    print('90d: %d nen, %d phien sach' % (len(D.df), D.days))
    rows = grid_table(D)
    print_grid(rows, 'LUOI 3x3 (file 90d)')
    ent, tr = run(D)
    m = K.metrics(tr, D.df)
    print('Cell chinh (3, 0.5): n=%d WR=%s avgR=%s ky vong=%s gia/lenh, %s lenh/ngay' % (m['n'], f(100 * m['wr'], 1), f(m['avg_r']), f(m['exp_pts']), f(m['per_day'])))
    print(tr['phase'].value_counts().to_dict() if len(tr) else '')
