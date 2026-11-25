"""Hồ sơ đuôi lệnh đơn (PLAN.md mục 6.3). python bw1_profile.py -> out_bw1_profile.txt, out_bw1_tail.csv
Với _GCZ26 (không có ngày đủ) dùng ngày phần >= 400 phút nến, ghi rõ."""
import os, sys, io, math
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bw1_common as C

pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500); pd.set_option('display.max_columns', 50)
out = io.StringIO()


def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.write(s + '\n')


def hill(v, k0):
    v = np.sort(v)[::-1]
    if len(v) < k0: return np.nan
    x = v[:k0].astype(float); xk = x[-1]
    s = np.sum(np.log(x / xk))
    return k0 / s if s > 0 else np.inf


tail_rows = []
LOGS = ['GCX_M1', 'GCX_M5', 'NQ_M1', 'NQ_M15', 'GCZ_M1', 'GCZ_M5']
for key in LOGS:
    log = C.load(key)
    cday = log.day[log.cb]; cses = log.ses[log.cb]
    partial = key.startswith('GCZ')
    days = [d for d, v in sorted(log.daymin.items()) if v >= 400] if partial else log.full_days
    P('=' * 120)
    P(f'{key} (M{log.m}) {len(log.cmot)} o, {log.nb} nen, {str(log.t[0])[:16]} -> {str(log.t[-1])[:16]} UTC; '
      + (f'KHONG co ngay du; dung {len(days)} ngay phan >= 400 phut nen: ' if partial else f'{len(days)} ngay du: ')
      + ', '.join(f'{C.fmt_day(d)}({log.daymin[d]})' for d in days))
    m = np.isin(cday, days)
    qs = [.5, .9, .99, .999, .9999]
    for s in ('tat ca', 'A', 'Au', 'My'):
        mm = m if s == 'tat ca' else m & (cses == s)
        v = log.cmot[mm]
        if not len(v): continue
        pq = np.quantile(v, qs)
        cnt = {}
        for th in (10, 20, 30, 50, 100, 200):
            per = [int(np.sum((log.cmot >= th) & mm & (cday == d))) for d in days]
            cnt[th] = f'{min(per)}/{int(np.median(per))}/{max(per)}'
        P(f'  phien {s:6s} o {len(v):7d}  phan vi 50/90/99/99,9/99,99 = ' + '/'.join(f'{x:.1f}' for x in pq)
          + '  | so o >= nguong moi ngay (nho nhat/trung vi/lon nhat): ' + '  '.join(f'>={k}: {x}' for k, x in cnt.items()))
    # lệnh lớn thứ k mỗi ngày
    ks = [1, 3, 5, 10, 20, 50]
    P('  lenh lon thu 1/3/5/10/20/50 moi ngay (ca ngay) | thu 1 theo phien A/Au/My:')
    for d in days:
        v = np.sort(log.cmot[m & (cday == d)])[::-1]
        tops = [int(v[k - 1]) if len(v) >= k else 0 for k in ks]
        sm = [int(log.cmot[m & (cday == d) & (cses == s)].max()) if np.any(m & (cday == d) & (cses == s)) else 0 for s in ('A', 'Au', 'My')]
        P(f'    {C.fmt_day(d):6s} ' + ' '.join(f'{x:4d}' for x in tops) + f'   | A {sm[0]:4d} Au {sm[1]:4d} My {sm[2]:4d}')
        tail_rows.append(dict(nhat_ky=key, ngay=str(d), phut_nen=log.daymin[d], **{f'top{k}': t for k, t in zip(ks, tops)},
                              max_A=sm[0], max_Au=sm[1], max_My=sm[2], **{f'o_ge{th}': int(np.sum((log.cmot >= th) & m & (cday == d))) for th in (10, 20, 30, 50, 100, 200)}))
    # Hill theo đoạn 5 ngày
    P('  so mu Hill (alpha, k0 = 100 / 200 / 500) tren tung doan 5 ngay:')
    for j in range(0, len(days), 5):
        ch = days[j:j + 5]
        v = log.cmot[np.isin(cday, ch)]
        hs = [hill(v, k0) for k0 in (100, 200, 500)]
        P(f'    {C.fmt_day(ch[0])}-{C.fmt_day(ch[-1])} ({len(ch)} ngay, {len(v)} o): ' + ' / '.join(f'{h:.2f}' for h in hs)
          + f'   x_k0 = ' + ' / '.join(str(int(np.sort(v)[::-1][k0 - 1])) if len(v) >= k0 else '-' for k0 in (100, 200, 500)))
    # lệnh tròn số
    v = log.cmot[m]; big = v[v >= 25]
    rnd = {r: int(np.sum(big == r)) for r in (25, 50, 100, 200)}
    nb = {r: (int(np.sum(big == r - 1)) + int(np.sum(big == r + 1))) / 2 for r in (25, 50, 100, 200)}
    share = sum(rnd.values()) / max(1, len(big))
    P(f'  lenh tron so trong nhom >= 25 ({len(big)} lenh): ' + ', '.join(f'{r}: {rnd[r]} (TB hai so ke {nb[r]:.1f})' for r in rnd)
      + f'  -> ti le tron so {share:.1%}')
    v99 = {r: int(np.sum(big == r)) for r in (99, 199)}
    P(f'     (99: {v99[99]}, 199: {v99[199]})')

# bảng 24 giờ Chicago cho nhật ký M1
for key in ('GCX_M1', 'NQ_M1'):
    log = C.load(key)
    cday = log.day[log.cb]; m = np.isin(cday, log.full_days)
    hour = pd.to_datetime(log.ct[log.cb]).hour.values
    P('=' * 120)
    P(f'{key}: bang 24 gio Chicago tren {len(log.full_days)} ngay du — muc 1% (K = n//100, lon thu K+1), lenh lon nhat trung vi moi ngay, so lenh >= 50 (tong), so lenh >= 100 (tong)')
    for h in list(range(17, 24)) + list(range(0, 17)):
        mm = m & (hour == h)
        v = log.cmot[mm]
        if not len(v): P(f'   {h:02d}h  khong co'); continue
        mx = [log.cmot[mm & (cday == d)].max() for d in log.full_days if np.any(mm & (cday == d))]
        P(f'   {h:02d}h  o {len(v):6d}  muc1% {C.level1pct(v):5.0f}  max trung vi {np.median(mx):6.1f}  >=50: {int(np.sum(v >= 50)):4d}  >=100: {int(np.sum(v >= 100)):3d}')

# so khung: 50 lệnh lớn nhất của M1 có mặt ở khung lớn
for small, large in (('GCX_M1', 'GCX_M5'), ('NQ_M1', 'NQ_M15'), ('GCZ_M1', 'GCZ_M5')):
    a, b = C.load(small), C.load(large)
    ta = pd.to_datetime(a.t[a.cb]); tb = pd.to_datetime(b.t)
    order = np.argsort(-a.cmot, kind='stable')[:50]
    lm = b.m
    bt_index = {pd.Timestamp(t): i for i, t in enumerate(tb)}
    hit = 0; nocover = 0; miss = []
    for j in order:
        t = ta[j]; start = t.floor(f'{lm}min')
        i = bt_index.get(start)
        if i is None: nocover += 1; continue
        tk, mt = b.cells(i)
        ok = np.any((tk == a.ctk[j]) & (mt == a.cmot[j]))
        if ok: hit += 1
        else:
            same = mt[tk == a.ctk[j]]
            miss.append(f'{str(t)[:16]} tick {a.ctk[j]} mot {a.cmot[j]} -> o khung lon {same.tolist()}')
    P('=' * 120)
    P(f'{small} -> {large}: 50 lenh lon nhat cua {small}: co mat o {large} (cung tick, cung co, gio nam trong nen) {hit}/{50 - nocover}; '
      f'khong co nen {large} tuong ung (nhat ky khung lon khong phu): {nocover}')
    for x in miss[:10]: P('    lech: ' + x)

pd.DataFrame(tail_rows).to_csv(os.path.join(C.HERE, 'out_bw1_tail.csv'), index=False)
with open(os.path.join(C.HERE, 'out_bw1_profile.txt'), 'w', encoding='utf-8') as f:
    f.write(out.getvalue())
