"""Review vòng 3 (Fable): cài lại ĐỘC LẬP luật "Không theo CORVEN" (không dùng sa2_/sa3_), so với số chuẩn của Opus.
Khác bản chuẩn về cấu trúc: giờ Chicago lấy từ zoneinfo (America/Chicago) thay vì luật tự viết; ngưỡng tính bằng sắp xếp danh sách
thay vì mảng đếm; không có giới hạn 4095.
python rv3_chk1.py  ->  out_rv3_chk1.txt"""
import os, sys, math, collections
import pandas as pd, numpy as np
from zoneinfo import ZoneInfo
SCR = r'C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad'
CT = ZoneInfo('America/Chicago'); UTC = ZoneInfo('UTC')
OUT = []


def say(s):
    print(s); OUT.append(s)


def rhu(x): return int(math.floor(x + 0.5))


def kth(vals, pbp):
    """ngưỡng = giá trị lớn thứ floor(p*n)+1; None nếu n*p < 5."""
    n = len(vals)
    if n * pbp < 50000: return None
    k = (pbp * n) // 10000
    if n < k + 1: return None
    return sorted(vals, reverse=True)[k]


def load(path):
    B = pd.read_csv(path.replace('.csv', '_bars.csv'), usecols=['bar_idx', 'datetime'])
    L = pd.read_csv(path)
    g = {k: v for k, v in L.groupby('bar_idx', sort=False)}
    return [(pd.Timestamp(t), g.get(i)) for i, t in zip(B.bar_idx, B.datetime)]


def dots(path, m, tick, K=5, mind=2, T=120, pbp=200, lc=True):
    bars = load(path)
    N = min(20, max(5, rhu(120 / m))); W = max(30, m); nsl = -(-1440 // W); nfb = max(5, rhu(T / m))
    hist = collections.defaultdict(dict)          # slot -> {day: [giá trị]}
    fb = collections.deque(); rq = collections.deque()
    red = blue = 0; src = collections.Counter(); maxv = 0
    for bi, (t, df) in enumerate(bars):
        if df is None or not (df.volume > 0).any(): continue
        loc = t.tz_localize(UTC).astimezone(CT).replace(tzinfo=None)
        day = (loc + pd.Timedelta(hours=7)).normalize(); slot = (loc.hour * 60 + loc.minute) // W
        tk = np.round(df.price.values / tick).astype(np.int64)
        thr = None
        prev = [d for d in sorted(hist[slot]) if d < day][-K:]
        if len(prev) >= mind:
            pool = [v for d in prev for v in hist[slot][d]]
            if lc:
                for s2 in dict.fromkeys([(slot - 1) % nsl, (slot + 1) % nsl]):
                    if s2 == slot: continue
                    for d in [d for d in sorted(hist[s2]) if d < day][-K:]: pool += hist[s2][d]
            thr = kth(pool, pbp)
        if thr is not None: src['chinh'] += 1
        else:
            thr = kth([v for b in fb for v in b], pbp); src['du_phong' if thr is not None else 'chua'] += 1
        if thr is not None:
            w = 4
            if len(rq) >= 5:
                a = sum(rq) / len(rq)
                if a > 0: w = max(4, rhu(a / 6))
            for col in ('bid_vol', 'ask_vol'):
                v = df[col].values.astype(np.int64)
                c = sorted([(-int(v[i]), int(tk[i])) for i in range(len(v)) if v[i] > thr])
                kept = []
                for _, k0 in c:
                    if all(abs(k0 - q) > w for q in kept): kept.append(k0)
                if col == 'bid_vol': red += len(kept)
                else: blue += len(kept)
        if bi == len(bars) - 1: break                     # nến đang chạy: không nộp
        vals = [int(x) for x in np.r_[df.bid_vol.values, df.ask_vol.values] if x > 0]
        maxv = max(maxv, max(vals) if vals else 0)
        hist[slot].setdefault(day, []).extend(vals)
        fb.append(vals)
        while len(fb) > nfb: fb.popleft()
        tv = tk[df.volume.values > 0]; rq.append(int(tv.max() - tv.min()))
        while len(rq) > N: rq.popleft()
    return red, blue, dict(src), maxv


def bigtrade(path, log, m, tick, T=240, pbp=100):
    bars = load(path)
    d = pd.read_csv(log)
    by = collections.defaultdict(dict)
    for tt, p, mo in zip(d.time_ticks, d.price, d.mot):
        k = int(round(p / tick)); by[int(tt)][k] = max(by[int(tt)].get(k, 0), float(mo))
    N = min(20, max(5, rhu(120 / m))); n = max(5, rhu(T / m))
    q = collections.deque(); rq = collections.deque(); tot = 0
    for bi, (t, _) in enumerate(bars):
        cells = by.get(int(t.value // 100 + 621355968000000000))
        if not cells: continue
        cells = {k: v for k, v in cells.items() if v > 0}
        if not cells: continue
        thr = kth([int(v) for b in q for v in b], pbp)
        if thr is not None:
            g = 2
            if len(rq) >= 5:
                a = sum(rq) / len(rq)
                if a > 0: g = max(2, rhu(a / 8))
            kept = []
            for v, k0 in sorted([(-v, k) for k, v in cells.items() if v > thr]):
                if all(abs(k0 - x) > g for x in kept): kept.append(k0)
            tot += len(kept)
        if bi == len(bars) - 1: break
        q.append(list(cells.values()))
        while len(q) > n: q.popleft()
        rq.append(max(cells) - min(cells))
        while len(rq) > N: rq.popleft()
    return tot


EXP = {('GC', 60, 'nen_moi'): (1646, 1662), ('NQ', 15, 'nen_moi'): (5512, 5494), ('GC', 15, 'nen_moi'): (4342, 4425),
       ('GC', 5, 'nap8'): (956, 959), ('NQ', 15, 'nap8'): (1097, 1028), ('NQ', 60, 'p1'): (1295, 1329), ('GC', 60, 'khong_lan_can'): (1771, 1805)}
ok = True
for (ma, m, cfg), exp in EXP.items():
    f = os.path.join(SCR, 'tf', f'fp_{ma}_m{m}{"_nap8" if cfg == "nap8" else ""}.csv')
    kw = dict(pbp=100) if cfg == 'p1' else dict(lc=False) if cfg == 'khong_lan_can' else {}
    r, b, src, mx = dots(f, m, 0.1 if ma == 'GC' else 0.25, **kw)
    good = (r, b) == exp; ok &= good
    say(f'{"ĐẠT " if good else "LỆCH"} {ma} M{m} {cfg}: cài độc lập đỏ {r} / xanh {b}; Opus {exp[0]} / {exp[1]}; nến {src}; giá trị bên lớn nhất {mx}')
for ma, m, tick, exp in (('GC', 30, 0.1, 788), ('NQ', 15, 0.25, 864), ('GC', 5, 0.1, 1913)):
    v = bigtrade(os.path.join(SCR, 'tf', f'fp_{ma}_m{m}.csv'), os.path.join(SCR, f'btlog_{ma}_M{m}.csv'), m, tick)
    good = v == exp; ok &= good
    say(f'{"ĐẠT " if good else "LỆCH"} Big Trade {ma} M{m}: cài độc lập {v}; Opus {exp}')
say('TỔNG: ' + ('ĐẠT' if ok else 'CÓ LỆCH'))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_rv3_chk1.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
