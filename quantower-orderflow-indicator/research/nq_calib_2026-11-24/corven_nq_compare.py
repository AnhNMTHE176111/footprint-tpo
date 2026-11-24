"""So chấm CORVEN (chart Sierra M1, Meet 07/11) với luật chấm của indicator, trên NQ và trên GC.
NQ: corven_nq_raw.csv + corven_nq_calib.json (corven_nq_extract.py). GC: ../corven_bubbles.csv + ../corven_bars_control.csv (đo cũ, 580 nến, 885 chấm).
Luật của mình chạy trên footprint M1 thật (F_*_m1.pkl của load.py)."""
import json, numpy as np, pandas as pd
from dots import dots
TICK = {'NQ': 0.25, 'GC': 0.1}
GOOD = 2.5   # bỏ khung khớp nến kém (cost > 2,5 px)

def corven_nq():
    cal = json.load(open('corven_nq_calib.json')); raw = pd.read_csv('corven_nq_raw.csv')
    bars = pd.read_csv('../../../data-export/data-footprint/fp_NQZ26_XCME_Time_20260826-20261124_90d_bars.csv', parse_dates=['datetime'])
    bars = bars[(bars.datetime >= '2026-11-03 22:00') & (bars.datetime < '2026-11-06 22:00')].reset_index(drop=True)
    t0 = bars.datetime.iloc[0]
    good = [n for n, c in cal.items() if c['cost'] <= GOOD]
    cover = set()
    for n in good:
        c = cal[n]
        for k in range(0, 80):
            x = c['x0'] + c['s'] * k
            if x < 62 or x > 1355: continue
            t = t0 + pd.Timedelta(minutes=c['n0'] + k - c['kmin'])
            r = bars[bars.datetime == t]
            if r.empty: continue
            yh = c['a'] + c['bb'] * r.high.iloc[0]; yl = c['a'] + c['bb'] * r.low.iloc[0]
            if yh > 270 and yl < 750: cover.add(t)          # cả nến nằm trong khung giá nhìn thấy
    raw = raw[raw.frame.isin(good)].copy()
    raw['t'] = pd.to_datetime(raw.utc); raw = raw[raw.t.isin(cover)]
    raw['tk'] = np.round(raw.price / TICK['NQ']).astype(int)
    # gộp cùng một chấm thấy ở nhiều khung: cùng nến, cùng màu, cách <= 2 tick
    out = []
    for (t, col), g in raw.groupby(['t', 'color']):
        for tk in sorted(g.tk):
            if out and out[-1][0] == t and out[-1][1] == col and tk - out[-1][2] <= 2: continue
            out.append((t, col, tk))
    C = pd.DataFrame(out, columns=['t', 'color', 'tk'])
    return C, sorted(cover), good

def corven_gc():
    c = pd.read_csv('../corven_bubbles.csv'); k = pd.read_csv('../corven_bars_control.csv')
    c['t'] = pd.to_datetime(c.time_utc); c['tk'] = np.round(c.price / TICK['GC']).astype(int)
    cover = sorted(pd.to_datetime(k.time_utc).unique())
    c = c[c.t.isin(cover)]
    return c[['t', 'color', 'tk']].drop_duplicates(), cover

def match(C, R, tol):
    """CORVEN chấm khớp nếu cùng nến, màu tương ứng (tím = xanh hoặc đỏ), cách <= tol tick. Trả recall, precision, F1."""
    Rg = {t: g for t, g in R.groupby('t')}
    hit = 0
    for r in C.itertuples():
        g = Rg.get(r.t)
        if g is None: continue
        ok = g if r.color == 'tim' else g[g.col == ('B' if r.color == 'xanh' else 'S')]
        if ((ok.tk - r.tk).abs() <= tol).any(): hit += 1
    Cg = {t: g for t, g in C.groupby('t')}
    hit2 = 0
    for r in R.itertuples():
        g = Cg.get(r.t)
        if g is None: continue
        ok = g[g.color.isin(['tim', 'xanh' if r.col == 'B' else 'do'])]
        if ((ok.tk - r.tk).abs() <= tol).any(): hit2 += 1
    rec = hit / max(len(C), 1); prec = hit2 / max(len(R), 1)
    return rec, prec, (2 * rec * prec / (rec + prec) if rec + prec else 0)

def ours(sym, cover, k, w, h, floor=9):
    F = pd.read_pickle(f'F_{sym}_m1.pkl'); F = F[F.t.isin(cover)]
    return dots(F, k, w, floor, h)

if __name__ == '__main__':
    rows = []
    Cn, cov_n, good = corven_nq(); Cg, cov_g = corven_gc()
    print(f'NQ: {len(good)} khung tốt, {len(cov_n)} nến M1 phủ trọn, CORVEN {len(Cn)} chấm ({Cn.color.value_counts().to_dict()})')
    print(f'GC: {len(cov_g)} nến M1, CORVEN {len(Cg)} chấm ({Cg.color.value_counts().to_dict()})')
    for sym, C, cov, tol in (('GC', Cg, cov_g, 3), ('NQ', Cn, cov_n, 3)):
        rows.append(dict(sym=sym, luat='CORVEN', cham_nen=round(len(C) / len(cov), 2), do=round((C.color == 'do').sum() / len(cov), 2), xanh=round((C.color == 'xanh').sum() / len(cov), 2), tim=round((C.color == 'tim').sum() / len(cov), 2)))
        sets = [('bộ GC 2,8/±4/che6', 2.8, 4, 6), ('bộ NQ 3,5/±8/che12', 3.5, 8, 12)]
        for k in (1.4, 1.6, 1.8, 2.0, 2.2, 2.4):
            sets.append((f'k={k} ±4 che6', k, 4, 6)); sets.append((f'k={k} ±8 che12', k, 8, 12))
        for name, k, w, h in sets:
            for fl in (9, 5):
                R = ours(sym, cov, k, w, h, fl)
                rec, prec, f1 = match(C, R, tol)
                rows.append(dict(sym=sym, luat=f'{name} sàn{fl}', cham_nen=round(len(R) / len(cov), 2), do=round((R.col == 'S').sum() / len(cov), 2), xanh=round((R.col == 'B').sum() / len(cov), 2),
                                 recall=round(rec, 2), precision=round(prec, 2), F1=round(f1, 3)))
    print(pd.DataFrame(rows).to_string(index=False))
