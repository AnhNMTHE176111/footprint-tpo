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


def detect(df, zcols, m5=None, n_min=3, body=0.5, delta_break=False, cands=None, hold_edge=False,
           expire=None, zone_half=None, rr=None, conf_min=0, conf_r=0.7, time_filter=False, zobj=None, extra=None):
    """Tra list entries. cands (list) neu cho: nhan them cac nen 'ung vien doi chung' (trong trang thai pha, cham E, hop le) -
    chua kiem nhip hoi / CF. delta_break (bien the V1): nen M5 pha phai co delta cung chieu S.
    hold_edge (bien the V2): nen CF phai dong o phia NGOAI E (buy: close >= E; sell: close <= E)."""
    zone_half = ZONE_HALF if zone_half is None else zone_half
    rr = RR if rr is None else rr
    sno_a = df['session_no'].to_numpy()
    vw_w = zcols['vwap_w'].to_numpy(float)
    bcount = {}

    def nconf(i, S, E, zname):
        """So vung KHAC (ten khac nhau) nam trong conf_r gia quanh E tai nen i (khong nhin truoc: as_of=i)."""
        z = K.zones_for_session(df, int(sno_a[i]), zobj.prof, as_of=i, ctx=zobj.ctx)
        names = set()
        for d in K.flat_zones(z, vw_d[i], vw_w[i], pos=i):
            if d['name'] != zname and abs(d['price'] - E) <= conf_r:
                names.add(d['name'])
        return len(names)
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
        if time_filter and not (state['after2030'] or state['brk_no'] >= 2):
            return
        if expire is not None:
            q = min(q, p0 + expire + 1)
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
            ok = (not bad[i]) and phase[i] != 'OFF' and not (1 <= sbig[i] <= 3) and (not time_filter or phase[i] == 'US')
            near = abs(cl[i] - E) <= 1.0 or (lo[i] <= E <= hi[i])
            if ok and near:
                if cands is not None:
                    nc = nconf(i, S, E, zname) if conf_min > 0 else 0
                    if nc >= conf_min:
                        cands.append(dict(idx=i, side=S, E=E, zone=zname, key=key))
                npb = i - 1 - pk_pos
                if (npb >= n_min and pbmax < L and cf[S][i] and count.get(key, 0) < 2
                        and (not hold_edge or (cl[i] - E) * S >= 0)
                        and (extra is None or extra(i, S, E, pk_pos))):
                    struct = min(lo[i], E - zone_half) if S > 0 else max(hi[i], E + zone_half)
                    r = K.risk(df, i, S, struct, rr=rr)
                    nc = nconf(i, S, E, zname) if zobj is not None else -1
                    if r is not None and (conf_min == 0 or nc >= conf_min):
                        entries.append(dict(idx=i, side=S, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='A', zone=zname,
                                            E=E, L=L, npb=npb, p0=p0, n_conf=nc, brk_no=state['brk_no'],
                                            after2030=state['after2030'], since_break=i - p0,
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
        kb = (int(s), srcn, out)
        bcount[kb] = bcount.get(kb, 0) + 1
        return dict(S=out, E=float(E), p0=lp, L=L, src=srcn, s=int(s), pk_pos=pk_pos,
                    brk_no=bcount[kb], after2030=bool(sm[lp] >= 930),
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
    ent = detect(D.df, D.zc, D.m5, n_min=n_min, body=body, zobj=D, **kw)
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


def control_state(D, ent, cands, n_draw=200, seed0=1000, zone_half=None, rr=None):
    """Doi chung cung trang thai pha: nen ngau nhien trong trang thai pha, cham E, cung chieu, SL/TP y het (khong dung nhip hoi / CF)."""
    real = {e['idx'] for e in ent}
    pool = []
    for c in cands:
        if c['idx'] in real:
            continue
        i, S = c['idx'], c['side']
        zh = ZONE_HALF if zone_half is None else zone_half
        struct = min(D.df['low'].iat[i], c['E'] - zh) if S > 0 else max(D.df['high'].iat[i], c['E'] + zh)
        r = K.risk(D.df, i, S, struct, rr=RR if rr is None else rr)
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


# ---------------------------------------------------------------------------------------------
# VONG 2: bien the tich luy V3 (het han 30 nen) -> V4 (+hop luu) -> V5 (+thoi gian), TP 3R va 2R
# ---------------------------------------------------------------------------------------------
R2_VARIANTS = [
    ('V3 het han 30 nen, mep xa E +-1,0', dict(expire=30)),
    ('V3b nhu V3 nhung mep xa E +-0,5 (do nhay)', dict(expire=30, zone_half=0.5)),
    ('V4 = V3 + hop luu >= 1 vung khac trong 0,7 gia', dict(expire=30, conf_min=1)),
    ('V4x (do nhay, KHONG phai bien the) hop luu ban kinh 1,5 gia', dict(expire=30, conf_min=1, conf_r=1.5)),
    ('V5 = V4 + chi phase My, pha sau 20:30 VN hoac pha lan 2', dict(expire=30, conf_min=1, time_filter=True)),
]


def grid_trades(D, kw, rr):
    out = {}
    for nm in GRID_N:
        for bd in GRID_BODY:
            out[(nm, bd)] = run(D, nm, bd, rr=rr, **kw)[1]
    return out


def split_stats(tr, cut):
    if len(tr) == 0:
        return stat(tr), stat(tr)
    if cut is None:
        return stat(tr[tr['split'] == 'TRAIN']), stat(tr[tr['split'] == 'TEST'])
    return halves(tr, cut)


def mini_hdr(cut):
    return '| | n | WR | R TB | ky vong (gia) | chuoi thua | %s | %s |\n|---|---|---|---|---|---|---|---|' % (
        'TRAIN n / R' if cut is None else 'Nua1 n / R', 'TEST n / R' if cut is None else 'Nua2 n / R')


def mini_row(lab, tr, cut):
    s = stat(tr)
    a, b = split_stats(tr, cut)
    return '| %s | %d | %s%% | %s | %s | %d | %d / %s | %d / %s |' % (
        lab, s['n'], f(100 * s['wr'], 1), f(s['avg_r']), f(s['exp_pts']), s['max_loss_streak'], a['n'], f(a['avg_r']), b['n'], f(b['avg_r']))


def variant_block(name, kw, Ds, verdict):
    L = ['## ' + name, '']
    for ds, (D, cut) in Ds.items():
        for rr in (3.0, 2.0):
            G = grid_trades(D, kw, rr)
            main = G[(3, 0.5)]
            L += ['### %s, TP %dR - o chinh (n_hoi 3, than 0,5); lenh/ngay = %s' % (ds, rr, f(len(main) / D.days)), '', mini_hdr(cut), mini_row('Tong', main, cut), '']
            if len(main):
                rs = main[main['outcome'].isin(['TP', 'SL', 'TIME'])]['r'].to_numpy()
                bs = np.random.default_rng(7).choice(rs, size=(5000, len(rs))).mean(axis=1)
                L += ['Bootstrap 5000 lan (seed 7) R TB o chinh: **%s**, khoang tin cay 95%% **[%s ; %s]** (n=%d)' % (f(rs.mean()), f(np.percentile(bs, 2.5)), f(np.percentile(bs, 97.5)), len(rs)), '']
            L += ['Theo phase (khong dung de loc):', '', mini_hdr(cut)]
            L += [mini_row(ph, main[main['phase'] == ph] if len(main) else main, cut) for ph in K.PHASES] + ['']
            if len(main):
                nc = main['n_conf']
                L += ['Tach theo so vung KHAC them o E:', '', mini_hdr(cut), mini_row('0 vung', main[nc == 0], cut), mini_row('1 vung', main[nc == 1], cut),
                      mini_row('2 vung', main[nc == 2], cut), mini_row('>=3 vung', main[nc >= 3], cut), '']
                if kw.get('time_filter'):
                    L += ['Tach V5 (hai dieu kien co the chong nhau):', '', mini_hdr(cut), mini_row('pha sau 20:30', main[main['after2030']], cut),
                          mini_row('pha lan 2+ cung canh', main[main['brk_no'] >= 2], cut), '']
            L += ['Luoi 3x3:', '', '| n_hoi | than | n | WR | R TB | %s | %s |' % ('TRAIN n / R' if cut is None else 'Nua1 n / R', 'TEST n / R' if cut is None else 'Nua2 n / R'),
                  '|---|---|---|---|---|---|---|']
            best = None
            for (nm, bd), t in G.items():
                s_ = stat(t)
                a, b = split_stats(t, cut)
                L.append('| %d | %.1f | %d | %s%% | %s | %d / %s | %d / %s |' % (nm, bd, s_['n'], f(100 * s_['wr'], 1), f(s_['avg_r']), a['n'], f(a['avg_r']), b['n'], f(b['avg_r'])))
                verdict.setdefault((name, rr, nm, bd), {})[ds] = (s_['n'], a, b)
                if s_['n'] >= 10 and (best is None or s_['avg_r'] > best[1]):
                    best = ((nm, bd), s_['avg_r'])
            L.append('')
            ctl_lines = []
            for lab, cell, nd in (('o chinh', (3, 0.5), 200), ('o tot nhat theo R TB' + (' %s' % (best[0],) if best else ''), best[0] if best else None, 200)):
                if cell is None or not len(G[cell]):
                    continue
                cc = []
                ent_c = detect(D.df, D.zc, D.m5, cell[0], cell[1], cands=cc, zobj=D, rr=rr, **kw)
                ctl, npool = control_state(D, ent_c, cc, n_draw=nd, zone_half=kw.get('zone_half'), rr=rr)
                if len(ctl):
                    m_ = stat(G[cell])['avg_r']
                    ctl_lines.append('- %s (%d lan, ho %d nen): R TB doi chung **%s** (5-95%%: %s .. %s); lenh that %s; ti le lan doi chung >= that **%s%%**.' % (
                        lab, nd, npool, f(np.nanmean(ctl)), f(np.nanpercentile(ctl, 5)), f(np.nanpercentile(ctl, 95)), f(m_), f(100 * np.mean(ctl >= m_), 1)))
            L += ['Doi chung cung trang thai pha (cung chieu, cung E, cung SL/TP, cung het han/hop luu/thoi gian, bo nhip hoi + CF); o tot nhat chon SAU khi nhin so nen chi tham khao:'] + (ctl_lines or ['- khong du lenh']) + ['']
    return L


def round2():
    D = Data(D90)
    Ds = {'90d': (D, None)}   # QD-6: chi file 90d (file 2 nam bi bo: sai ma hop dong)
    verdict = {}
    L = ['# VONG 2 - sua 2 lo hong co che (het han, hop luu, thoi gian)', '',
         '**QD-6 (nguoi hoc chot): CHI do tren file 90d GCZ26. Moi bang 2 nam (vong 1, o cuoi file) chi con de THAM KHAO, khong dung de quyet dinh (du lieu footprint truoc do sai ma hop dong).** Sinh boi `setup_a_pha_hoi.py --round2` (deterministic). Cac bien the TICH LUY: V3 -> V4 -> V5; moi bien the bao rieng. TP 3R va 2R chay song song, cung seed. '
         'Het han: CF phai nam trong 30 nen M1 sau nen cuoi cua M5 dong ngoai (nhip hoi bat dau va ket thuc trong khoang do). '
         'Hop luu: so vung KHAC (ten khac nhau, tinh theo as_of tai nen vao, khong nhin truoc) nam trong 0,7 gia quanh E, trong cac vung VWAP ngay/tuan, POC/VAH/VAL hom qua va Au, HVN ngay/tuan, naked POC, IB; '
         '"tach 0 / 1 / 2 / >=3" la so vung KHAC them o E. Pha lan 2 = trang thai pha thu >= 2 cung canh (cung nguon band) trong phien. Phase Au KHONG dung loc.', '']
    for name, kw in R2_VARIANTS:
        L += variant_block(name, kw, Ds, verdict)
    L += ['## Phan quyet vong 2 (QD-6: chi file 90d)', '',
          'Dat khi: n TEST(90d) >= 30 VA R TEST(90d) > 0, cung mot o/variant/TP (them: R TRAIN > 0 de khong chi dung do may mat nua).', '']
    ok_full, ok_sign = [], []
    for (name, rr, nm, bd), d in verdict.items():
        n9, a9, b9 = d['90d']
        if b9['n'] and b9['avg_r'] > 0:
            r = (name.split(' ')[0], rr, nm, bd, a9['n'], a9['avg_r'], b9['n'], b9['avg_r'])
            ok_sign.append(r)
            if b9['n'] >= 30 and a9['avg_r'] > 0:
                ok_full.append(r)
    L += ['- O dat DU tieu chi (n TEST >= 30, TEST > 0, TRAIN > 0): **%d**' % len(ok_full),
          '- O co R TEST > 0 nhung n TEST < 30 hoac TRAIN <= 0 (chi tham khao, khong ket luan): **%d** tren tong %d o (5 muc x 2 TP x 9 o luoi)' % (len(ok_sign) - len(ok_full), len(verdict))]
    if ok_sign:
        L += ['', '| variant | TP | n_hoi | than | n TRAIN | R TRAIN | n TEST | R TEST |', '|---|---|---|---|---|---|---|---|']
        for r in ok_sign:
            L.append('| %s | %dR | %d | %.1f | %d | %s | %d | %s |' % (r[0], r[1], r[2], r[3], r[4], f(r[5]), r[6], f(r[7])))
    L.append('')
    ev = os.path.join(HERE, 'report', '_eval_a_r2.txt')
    if os.path.exists(ev):
        with open(ev, encoding='utf-8') as fh:
            L.append(fh.read())
    r1 = os.path.join(HERE, 'report', '_round1_A.md')
    with open(r1, encoding='utf-8') as fh:
        old = '# VONG 1 (giu nguyen; phan 2 nam CHI THAM KHAO theo QD-6, khong dung quyet dinh)\n\n' + fh.read()
    with open(os.path.join(HERE, 'report', 'RESULTS-A.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n\n---\n\n' + old)
    print('ghi RESULTS-A.md vong 2 + vong 1')


# ---------------------------------------------------------------------------------------------
# VONG 3: (1) mo xe 18 lenh SL cua V3 (2) V6 = V3 + "tuong limit" tu footprint tung muc gia
# ---------------------------------------------------------------------------------------------
class Wall:
    """Footprint tung muc gia theo nen. Tuong limit tai cuc tri rau hoi: 3 muc sat cuc tri; tong volume >= kV x trung vi volume/muc cua
    50 nen (gom nen dang xet); delta nguoc chieu hoi: pha len/hoi xuong => ask >= kD x bid tai 3 muc day rau; pha xuong gương ngược."""

    def __init__(self, D, levels):
        pos = pd.Index(D.df['bar_idx'].to_numpy()).get_indexer(levels['bar_idx'].to_numpy())
        ok = pos >= 0
        lv = levels[ok].copy()
        lv['pos'] = pos[ok]
        lv = lv.sort_values(['pos', 'price'], kind='stable')
        self.pos = lv['pos'].to_numpy()
        self.price = lv['price'].to_numpy(float)
        self.vol = lv['volume'].to_numpy(float)
        self.bid = lv['bid_vol'].to_numpy(float)
        self.ask = lv['ask_vol'].to_numpy(float)
        n = len(D.df)
        self.lo_i = np.searchsorted(self.pos, np.arange(n), 'left')
        self.hi_i = np.searchsorted(self.pos, np.arange(n), 'right')
        self.cl = D.df['close'].to_numpy(float)
        self.hi = D.df['high'].to_numpy(float)
        self.lo = D.df['low'].to_numpy(float)
        self.med_cache = {}

    def med(self, i):
        if i not in self.med_cache:
            a, b = self.lo_i[max(0, i - 49)], self.hi_i[i]
            self.med_cache[i] = float(np.median(self.vol[a:b])) if b > a else float('nan')
        return self.med_cache[i]

    def info(self, i, S, E, pk_pos):
        """(j, vol3, ask3, bid3, med) o nen hoi cham E co cuc tri xa nhat (day cho S>0, dinh cho S<0); None neu khong co."""
        best = None
        for j in range(pk_pos + 1, i):
            if abs(self.cl[j] - E) <= 1.0 or (self.lo[j] <= E <= self.hi[j]):
                key = -self.lo[j] if S > 0 else self.hi[j]
                if best is None or key > best[0]:
                    best = (key, j)
        if best is None:
            return None
        j = best[1]
        a, b = self.lo_i[j], self.hi_i[j]
        if b <= a:
            return None
        sl = slice(a, a + 3) if S > 0 else slice(max(a, b - 3), b)
        return j, float(self.vol[sl].sum()), float(self.ask[sl].sum()), float(self.bid[sl].sum()), self.med(j)

    def check(self, i, S, E, pk_pos, kV, kD):
        r = self.info(i, S, E, pk_pos)
        if r is None:
            return False
        j, v3, a3, b3, md = r
        if not (md == md) or v3 < kV * md:
            return False
        return (a3 >= kD * b3 and a3 > 0) if S > 0 else (b3 >= kD * a3 and b3 > 0)


def dissect_sl(D, tr, win_back=20, win_sweep=60):
    """Phan loai lenh SL: HOI XUYEN = trong win_back nen M1 sau SL co nen dong lai trong range >= 1u qua canh E;
    QUET = trong win_sweep nen sau SL (cung phien) gia cham TP cu."""
    df = D.df
    u = K.median_range(df).to_numpy(float)
    cl, hi, lo = (df[c].to_numpy(float) for c in ('close', 'high', 'low'))
    sn = df['session_no'].to_numpy()
    rows = []
    for x in tr[tr['outcome'] == 'SL'].itertuples():
        i, ex, S, E = int(x.idx), int(x.exit_idx), int(x.side), float(x.E)
        uu = u[i]
        end = min(len(df) - 1, ex + win_back)
        w = np.arange(ex + 1, end + 1)
        w = w[sn[w] == sn[ex]] if len(w) else w
        a = bool(len(w) and ((cl[w] <= E - uu).any() if S > 0 else (cl[w] >= E + uu).any()))
        end2 = min(len(df) - 1, ex + win_sweep)
        w2 = np.arange(ex + 1, end2 + 1)
        w2 = w2[sn[w2] == sn[ex]] if len(w2) else w2
        b = bool(len(w2) and ((hi[w2] >= x.tp).any() if S > 0 else (lo[w2] <= x.tp).any()))
        seg = np.arange(i + 1, ex + 1)
        mfe = float(((hi[seg].max() - x.entry) if S > 0 else (x.entry - lo[seg].min())) / x.risk_pts) if len(seg) else 0.0
        lab = 'ca hai' if (a and b) else ('HOI XUYEN' if a else ('QUET' if b else 'khong ro'))
        rows.append(dict(t_vn=str(x.t_vn)[:16], side='BUY' if S > 0 else 'SELL', phase=x.phase, zone=x.zone, E=E, entry=x.entry, sl=x.sl,
                         bars=ex - i, mfe=mfe, u=uu, a=a, b=b, lab=lab))
    return pd.DataFrame(rows)


def boot_ci(r, n=5000, seed=7):
    r = np.asarray(r, float)
    if len(r) == 0:
        return float('nan'), float('nan')
    bs = np.random.default_rng(seed).choice(r, size=(n, len(r))).mean(axis=1)
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def round3():
    D = Data(D90)
    levels = K.load_levels(D90 + '.csv')
    W = Wall(D, levels)
    L = ['# VONG 3 - mo xe SL cua V3 va V6 (tuong limit footprint)', '',
         '**QD-6: chi file 90d GCZ26.** Cung seed. V3 = het han 30 nen, mep xa E +-1,0, o chinh (n_hoi 3, than CF 0,5). Moi so lieu bang 2 nam o phan duoi la tham khao.', '']
    # ---- 1. mo xe
    _, t3 = run(D, 3, 0.5, expire=30, rr=3.0)
    ds = dissect_sl(D, t3)
    L += ['## 1. Phan loai %d lenh SL cua V3 (TP 3R, n=%d lenh)' % (len(ds), len(t3)), '',
          'HOI XUYEN = trong 20 nen M1 sau SL co nen dong lai trong range >= 1u (u = trung vi bien do 50 nen) qua canh E. QUET = trong 60 nen sau SL gia cham TP cu. Hai loai co the chong nhau.', '',
          '| loai | so lenh | ti le |', '|---|---|---|']
    for lab in ('HOI XUYEN', 'QUET', 'ca hai', 'khong ro'):
        c = int((ds['lab'] == lab).sum())
        L.append('| %s | %d | %.0f%% |' % (lab, c, 100 * c / max(1, len(ds))))
    L += ['', '- Co nen dong xuyen lai (a) tinh ca hai: **%d / %d**; co cham TP cu (b) tinh ca hai: **%d / %d**.' % (int(ds['a'].sum()), len(ds), int(ds['b'].sum()), len(ds)),
          '- So nen den SL: trung vi %.0f; da di >= 1R truoc khi SL: %d / %d; SL trung vi %.2f u.' % (
              ds['bars'].median(), int((ds['mfe'] >= 1).sum()), len(ds), float((ds['sl'] * 0 + (ds['entry'] - ds['sl']).abs() / ds['u']).median())), '',
          '| gio VN | chieu | phase | vung | E | vao | SL | nen den SL | MFE (R) | xuyen lai | quet | loai |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for x in ds.itertuples():
        L.append('| %s | %s | %s | %s | %.1f | %.1f | %.1f | %d | %.2f | %s | %s | %s |' % (x.t_vn, x.side, x.phase, x.zone, x.E, x.entry, x.sl, x.bars, x.mfe, 'x' if x.a else '', 'x' if x.b else '', x.lab))
    L.append('')
    # ---- 2. V6
    L += ['## 2. V6 = V3 + tuong limit tai cuc tri rau hoi', '',
          'Nen hoi cham E co cuc tri xa nhat (day cho pha len) trong nhip hoi; 3 muc gia sat cuc tri rau do: (i) tong volume 3 muc >= kV x trung vi volume/muc cua 50 nen; '
          '(ii) pha len/hoi xuong: ask >= kD x bid tai 3 muc (pha xuong: bid >= kD x ask tai 3 muc dinh). Luoi kV {1,5; 2,0} x kD {2; 3}; n_hoi 3, than CF 0,5 co dinh. '
          'Do ro: (i) so sanh tong 3 muc voi trung vi MOT muc (dung nguyen van de bai), nen de qua; (ii) la dieu kien chinh.', '']
    verdict = []
    for rr in (3.0, 2.0):
        _, base = run(D, 3, 0.5, expire=30, rr=rr)
        bst = stat(base)
        cc = []
        ent_b = detect(D.df, D.zc, D.m5, 3, 0.5, cands=cc, zobj=D, expire=30, rr=rr)
        lo_b, hi_b = boot_ci(base[base['outcome'].isin(['TP', 'SL'])]['r']) if len(base) else (float('nan'),) * 2
        L += ['### TP %dR (V3 tham chieu: n=%d, WR %s%%, R TB %s, CI95 [%s ; %s])' % (rr, bst['n'], f(100 * bst['wr'], 1), f(bst['avg_r']), f(lo_b), f(hi_b)), '',
              '| kV | kD | n | WR | R TB | CI95 bootstrap | TRAIN n / R | TEST n / R | doi chung state (200) | doi chung thinning V3 (200) | do duoc? |', '|---|---|---|---|---|---|---|---|---|---|---|']
        rbase = base['r'].to_numpy() if len(base) else np.array([])
        for kV in (1.5, 2.0):
            for kD in (2.0, 3.0):
                ex = (lambda i, S, E, pk, kV=kV, kD=kD: W.check(i, S, E, pk, kV, kD))
                ent, t6 = run(D, 3, 0.5, expire=30, rr=rr, extra=ex)
                s6 = stat(t6)
                a, b = split_stats(t6, None)
                lo6, hi6 = boot_ci(t6[t6['outcome'].isin(['TP', 'SL'])]['r']) if len(t6) else (float('nan'),) * 2
                ctl_s = 'n/a'
                ctl_t = 'n/a'
                if len(t6):
                    ctl, npool = control_state(D, ent, cc, n_draw=200, rr=rr)
                    if len(ctl):
                        ctl_s = '%s (%s%% >= that)' % (f(np.nanmean(ctl)), f(100 * np.mean(ctl >= s6['avg_r']), 0))
                    g = np.random.default_rng(31)
                    th = np.array([g.choice(rbase, size=min(len(t6), len(rbase)), replace=False).mean() for _ in range(200)])
                    ctl_t = '%s (%s%% >= that)' % (f(th.mean()), f(100 * np.mean(th >= s6['avg_r']), 0))
                ok = 'KHONG DO DUOC (n TEST < 15)' if b['n'] < 15 else ('du n' + (', TEST > 0' if b['avg_r'] > 0 else ', TEST <= 0'))
                L.append('| %.1f | %.0f | %d | %s%% | %s | [%s ; %s] | %d / %s | %d / %s | %s | %s | %s |' % (
                    kV, kD, s6['n'], f(100 * s6['wr'], 1), f(s6['avg_r']), f(lo6), f(hi6), a['n'], f(a['avg_r']), b['n'], f(b['avg_r']), ctl_s, ctl_t, ok))
                verdict.append((rr, kV, kD, s6['n'], a, b))
        L.append('')
    # chan doan: ti le tung dieu kien tren 20 lenh V3 (tai nen vao)
    cap = {}

    def _cap(i, S, E, pk):
        cap[i] = W.info(i, S, E, pk)
        return True
    ent3, _t = run(D, 3, 0.5, expire=30, rr=3.0, extra=_cap)
    infos = [(e['side'], cap.get(e['idx'])) for e in ent3]
    nn = len(infos)
    have = [(S, r) for S, r in infos if r is not None]
    L += ['### Chan doan V6 tren cac lenh V3 (%d lenh vao; %d co nen hoi cham E trong nhip hoi de do footprint)' % (nn, len(have)), '',
          '| dieu kien | so lenh dat |', '|---|---|']
    for kV in (1.5, 2.0):
        L.append('| tong volume 3 muc >= %.1f x trung vi/muc | %d / %d |' % (kV, sum(1 for S, r in have if r[4] == r[4] and r[1] >= kV * r[4]), len(have)))
    for kD in (2.0, 3.0):
        c = sum(1 for S, r in have if ((r[2] >= kD * r[3] and r[2] > 0) if S > 0 else (r[3] >= kD * r[2] and r[3] > 0)))
        L.append('| delta dung chieu hoi-dao (ask >= %.0f x bid o day / bid >= %.0f x ask o dinh) | %d / %d |' % (kD, kD, c, len(have)))
    c = sum(1 for S, r in have if ((r[3] >= 2 * r[2] and r[3] > 0) if S > 0 else (r[2] >= 2 * r[3] and r[2] > 0)))
    L.append('| (tham khao) delta CUNG chieu hoi: bid >= 2 x ask o day / ask >= 2 x bid o dinh | %d / %d |' % (c, len(have)))
    L.append('')
    # ti le qua tuong tren cac lenh V3
    ok15 = [v for v in verdict if v[5]['n'] >= 15]
    L += ['## Phan quyet vong 3', '',
          '- So o V6 co n TEST >= 15: **%d / %d**. So o co n TEST >= 30 va TEST > 0 va TRAIN > 0: **%d**.' % (
              len(ok15), len(verdict), sum(1 for v in verdict if v[5]['n'] >= 30 and v[5]['avg_r'] > 0 and v[4]['avg_r'] > 0)), '']
    ev = os.path.join(HERE, 'report', '_eval_a_r3.txt')
    if os.path.exists(ev):
        with open(ev, encoding='utf-8') as fh:
            L.append(fh.read())
    with open(os.path.join(HERE, 'report', '_round12_A.md'), encoding='utf-8') as fh:
        old = fh.read()
    with open(os.path.join(HERE, 'report', 'RESULTS-A.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n\n---\n\n' + old)
    print('ghi RESULTS-A.md vong 3 + vong 2 + vong 1')


if __name__ == '__main__':
    if '--round3' in sys.argv:
        round3()
        sys.exit(0)
    if '--round2' in sys.argv:
        round2()
        sys.exit(0)
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
