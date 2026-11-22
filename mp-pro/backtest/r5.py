"""Vòng 5: các ý còn lại của sách, chạy trên GC 2 năm (DEV 08/24-07/25, VALID 08/25-08/26).
K   : cụm nhiều POC phiên trùng nhau = vùng giá trị, giá rời đi rồi quay lại -> đánh đảo chiều (p56-57).
SPK : quy tắc spike - 30 phút cuối phiên pit nằm ngoài VA; giờ đầu hôm sau trên spike -> buy ở đáy spike,
      dưới spike -> đảo chiều (p87-88).
PIN : nến pin M30 + giá đóng phải vượt POC đang hình thành theo hướng đảo chiều (p98-99).
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, '.'); sys.stdout.reconfigure(encoding='utf-8')
from core import Data, stats, to_df, simulate, resample, poc_va, TICK
from setups_other import sess_stats, atr30_at

d = Data(base='fp_GC_XCEC_Time_20240801-20260819_748d9h', cache_name='cache_2y.npz')
jump = np.abs(d.o[1:] - d.c[:-1]) > np.maximum(15, 4 * np.nan_to_num(d.atr1[:-1], nan=1.0))
jidx = np.flatnonzero(jump) + 1
MID, CUT = pd.Timestamp('2025-08-01'), pd.Timestamp('2026-08-11')
r30 = resample(d, 30)
rows = []


def rep(name, tr, window_min=2 * 1440):
    df = to_df(tr, d)
    if len(df) == 0:
        rows.append(dict(setup=name, n_dev=0)); print(rows[-1]); return
    bad = np.array([np.any((jidx > i - window_min) & (jidx <= i)) for i in df.i.values])
    df = df[~bad & (df.date < CUT)]
    dv, va = stats(df[df.date < MID]), stats(df[df.date >= MID])
    rows.append(dict(setup=name, n_dev=dv.get('n'), wr_dev=dv.get('wr'), R_dev=dv.get('expR'), ci_dev=dv.get('ci90'),
                     n_val=va.get('n'), wr_val=va.get('wr'), R_val=va.get('expR'), ci_val=va.get('ci90')))
    print(rows[-1], flush=True)


G = sess_stats(d, 'globex')


def setup_K(lookback=10, minpoc=3, tol=0.3, SLm=1.3, TPm=1.1, off=0.1, away=1.0, mgmt=None):
    trades = []
    keys = sorted(G)
    for a in range(lookback, len(keys)):
        s = keys[a]
        pocs = np.array([G[k]['poc'] for k in keys[a - lookback:a]])
        i0 = d.sess_start[s]; i1 = d.sess_end[s]
        A = atr30_at(d, r30, i0)
        px = d.c[i0 - 1]
        done = set()
        for p in np.sort(pocs):
            grp = pocs[np.abs(pocs - p) <= tol * A]
            if len(grp) < minpoc:
                continue
            lvl = round(grp.mean() / TICK) * TICK
            if any(abs(lvl - x) < tol * A for x in done):
                continue
            done.add(lvl)
            if abs(px - lvl) < away * A:
                continue        # giá phải đang ở xa cụm (đã rời đi)
            sd = 1 if px > lvl else -1    # giá ở trên -> về cụm thì buy; ở dưới -> sell (p57)
            entry = round((lvl + sd * off * A) / TICK) * TICK
            sl = entry - sd * SLm * A; tp = entry + sd * TPm * A
            t = simulate(d, 'buy' if sd == 1 else 'sell', entry, sl, tp, i0, i1, cost=0.2)
            if t:
                t.update(setup='K'); trades.append(t)
    return trades


R = sess_stats(d, 'rth')


def setup_SPK(SLm=1.3, TPm=1.1, mode='both'):
    trades = []
    keys = sorted(R)
    for a in range(len(keys) - 1):
        s, nx = keys[a], keys[a + 1]
        p = R[s]; q = R[nx]
        j1 = p['i1']; j0 = j1 - 30
        sh, sl_ = d.h[j0:j1].max(), d.l[j0:j1].min()
        if sl_ > p['vah']:
            sd0 = 1            # spike tăng
        elif sh < p['val']:
            sd0 = -1
        else:
            continue
        k0 = q['i0']; ab_h, ab_l = d.h[k0:k0 + 60].max(), d.l[k0:k0 + 60].min()
        A = atr30_at(d, r30, k0 + 60)
        if sd0 == 1 and ab_l > sh or sd0 == -1 and ab_h < sl_:
            if mode in ('both', 'cont'):      # tiếp diễn: limit ở 'đáy' spike (spike tăng) / 'đỉnh' spike (giảm)
                lvl = sl_ if sd0 == 1 else sh
                t = simulate(d, 'buy' if sd0 == 1 else 'sell', lvl, lvl - sd0 * SLm * A, lvl + sd0 * TPm * A,
                             k0 + 60, q['i1'], cost=0.2)
                if t:
                    t.update(setup='SPK-cont'); trades.append(t)
        elif sd0 == 1 and ab_h < sl_ or sd0 == -1 and ab_l > sh:
            if mode in ('both', 'rev'):
                sd = -sd0; ie = k0 + 60; px = d.o[ie]
                t = simulate(d, 'buy' if sd == 1 else 'sell', None, px - sd * SLm * A, px + sd * TPm * A, ie, ie + 1,
                             limit=False, cost=0.2)
                if t:
                    t.update(setup='SPK-rev'); trades.append(t)
    return trades


def setup_PIN(tf=30, wick=0.6, SLbuf=0.1, TPm=None):
    """Pin bar bất kỳ: râu >= wick*range; sell nếu râu trên và đóng DƯỚI POC đang hình thành (p98-99); buy ngược lại.
    SL sau râu, TP = 1R (20/20 kiểu R:R 1:1, p49-50, p93) hoặc TPm*ATR."""
    r = resample(d, tf); trades = []
    o, h, l, c, atr, i0s, i1s, ss = (r[k].values for k in ['o', 'h', 'l', 'c', 'atr', 'i0', 'i1', 'sess'])
    for k in range(20, len(r)):
        s = ss[k]; st = d.sess_start[s]; ie = int(i1s[k])
        if i0s[k] - st < 120 or ie >= d.n or d.min_of_sess[ie] > 1340:
            continue
        rg = h[k] - l[k]
        if rg <= 0.8 * atr[k]:
            continue
        up_w = h[k] - max(o[k], c[k]); dn_w = min(o[k], c[k]) - l[k]
        if up_w >= wick * rg:
            sd = -1
        elif dn_w >= wick * rg:
            sd = 1
        else:
            continue
        t0, vol = d.profile(st, int(i1s[k]))
        poc = (t0 + int(np.argmax(vol))) * TICK
        if sd * (c[k] - poc) <= 0:
            continue
        sl = (h[k] + SLbuf * atr[k]) if sd == -1 else (l[k] - SLbuf * atr[k])
        px = d.o[ie]; risk = abs(px - sl)
        tp = px + sd * (TPm * atr[k] if TPm else risk)
        t = simulate(d, 'buy' if sd == 1 else 'sell', None, sl, tp, ie, ie + 1, limit=False, cost=0.2)
        if t:
            t.update(setup='PIN'); trades.append(t)
    return trades


for lb in (5, 10, 20):
    for mp in (2, 3, 4):
        rep(f'K lb{lb} minpoc{mp}', setup_K(lookback=lb, minpoc=mp), (lb + 1) * 1440)
rep('SPK both', setup_SPK())
rep('SPK cont', setup_SPK(mode='cont'))
rep('SPK rev', setup_SPK(mode='rev'))
for tf in (30, 15):
    for w in (0.5, 0.66):
        rep(f'PIN tf{tf} w{w} 1R', setup_PIN(tf=tf, wick=w))
pd.DataFrame(rows).to_csv('r5.csv', index=False)
