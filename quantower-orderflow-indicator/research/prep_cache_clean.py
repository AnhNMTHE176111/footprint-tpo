#!/usr/bin/env python3
"""Gộp footprint per-level + OHLC thành cache pickle để mọi thí nghiệm load trong ~1s.

Chạy:  python3 prep_cache.py
Ra:    data-export/27-7/perlevel_m1.pkl   (list các nến, đã lọc từ 2026-05-01)

Mỗi nến: dict(t, o, h, l, c, vol, delta, lo_t, hi_t, lvls=[(tick_idx, price, bid, ask, vol), ...])
"""
import csv, pickle, sys
from collections import defaultdict

TICK = 0.1
FROM = '2026-06-01'
SRC = 'data-export/27-7/sample.csv'
OHLC_SRC = ('data-export/27-7/_GCQ26XCEC dxFeed, Time - Time - 1m, '
            '11_3_2025 120000 AM-7_27_2026 105600 PM_8b750702-5f00-4836-bf74-81e2a0c4495f.csv')
OUT = 'data-export/27-7/perlevel_m1_clean.pkl'


def norm(s):
    s = s.strip()
    if '.' in s: s = s.split('.')[0]
    ampm = ''
    for tag in (' AM', ' PM'):
        if s.upper().endswith(tag): ampm = tag.strip(); s = s[:-3].strip()
    p = s.split()
    if len(p) < 2: return s
    d, t = p[0], p[1]
    tp = t.split(':'); hh = int(tp[0]); mm = int(tp[1]) if len(tp) > 1 else 0
    if ampm == 'PM' and hh < 12: hh += 12
    if ampm == 'AM' and hh == 12: hh = 0
    if '/' in d:
        a, b, c = d.split('/'); d = f"{int(c):04d}-{int(a):02d}-{int(b):02d}"
    return f"{d} {hh:02d}:{mm:02d}"


ohlc = {}
rd = csv.DictReader(open(OHLC_SRC, encoding='utf-8-sig'), delimiter=';')
for r in rd:
    try:
        ohlc[norm(r['Time left'])] = (float(r['Open']), float(r['High']), float(r['Low']), float(r['Close']))
    except (KeyError, TypeError, ValueError):
        pass
print(f"OHLC: {len(ohlc)} nến")

bars = defaultdict(lambda: {'lvls': [], 't': ''})
order = []
for r in csv.DictReader(open(SRC, encoding='utf-8-sig')):
    k = r['bar_idx']
    if k not in bars: order.append(k)
    b = bars[k]; b['t'] = r['datetime']
    try:
        pr = float(r['price']); bid = float(r['bid_vol']); ask = float(r['ask_vol']); v = float(r['volume'])
    except (TypeError, ValueError):
        continue
    if v <= 0: v = bid + ask
    b['lvls'].append((round(pr / TICK), pr, bid, ask, v))

out = []
for k in order:
    b = bars[k]
    if not b['lvls'] or b['t'][:10] < FROM: continue
    q = ohlc.get(norm(b['t']))
    if not q: continue
    o, h, l, c = q
    pts = [x[0] for x in b['lvls']]
    out.append(dict(t=b['t'], o=o, h=h, l=l, c=c, lo_t=min(pts), hi_t=max(pts),
                    lvls=b['lvls'], vol=sum(x[4] for x in b['lvls']),
                    delta=sum(x[3] - x[2] for x in b['lvls'])))
pickle.dump(out, open(OUT, 'wb'), protocol=4)
print(f"→ {OUT}: {len(out)} nến, {sum(len(b['lvls']) for b in out)} ô")
