"""Đo stacked imbalance trên GCZ26 M1 90 ngày (nguồn dày). Chỉ đọc dữ liệu."""
import sys, time, collections
import numpy as np, pandas as pd

D = r"C:/Users/anhla/OneDrive/Documents/footprint-tpo/data-export/data-footprint/"
F = D + "fp_GCZ26_XCEC_Time_20260723-20261021_90d.csv"
FB = D + "fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv"
TICK = 0.1
START = "2026-08-03"   # GCZ26 thành hợp đồng chính sau roll ~07-29

t0 = time.time()
bars = pd.read_csv(FB, usecols=["bar_idx", "datetime", "open", "high", "low", "close"])
bars = bars[bars.datetime >= START].reset_index(drop=True)
lv = pd.read_csv(F, usecols=["bar_idx", "price", "bid_vol", "ask_vol", "volume"])
lv = lv[lv.bar_idx >= bars.bar_idx.iloc[0]]
lv["k"] = np.round(lv.price / TICK).astype(np.int64)
print("load", round(time.time() - t0, 1), "s; bars", len(bars), "levels", len(lv), file=sys.stderr)

# gom per-level theo bar
g = {b: (k.values, a.values, bi.values, v.values) for b, k, a, bi, v in
     ((b, d.k, d.ask_vol, d.bid_vol, d.volume) for b, d in lv.groupby("bar_idx"))}
bars["day"] = bars.datetime.str[:10]
ndays = bars.day.nunique()

# baseline cổng cũ: median top-3 vol/ô của 100 nến trước, max với 5
top3 = []
for b in bars.bar_idx:
    if b in g:
        v = np.sort(g[b][3])[::-1][:3]
    else:
        v = np.array([])
    top3.append(v)
oldgate = np.full(len(bars), np.inf)
for i in range(len(bars)):
    if i >= 40:
        allv = np.concatenate(top3[max(0, i - 100):i])
        oldgate[i] = max(5.0, np.median(allv)) if len(allv) else 5.0

def arrays(i):
    r = bars.iloc[i]
    lo, hi = int(round(r.low / TICK)), int(round(r.high / TICK))
    n = hi - lo + 1
    A = np.zeros(n); B = np.zeros(n)
    b = r.bar_idx
    if b in g:
        k, a, bi, _ = g[b]
        m = (k >= lo) & (k <= hi)
        A[k[m] - lo] += a[m]; B[k[m] - lo] += bi[m]
    return lo, A, B

ARR = [arrays(i) for i in range(len(bars))]
print("arrays", round(time.time() - t0, 1), "s", file=sys.stderr)

def flags(A, B, R, M, gate=0.0, strict=False):
    n = len(A)
    buy = np.zeros(n, bool); sell = np.zeros(n, bool)
    if n < 2: return buy, sell
    r = R / 100.0
    a, bl = A[1:], B[:-1]          # buy: ask[i] vs bid[i-1]
    cb = (a > r * bl) if strict else (a >= r * bl)
    buy[1:] = cb & (a >= max(M, 1e-9)) & (a > gate)
    bb, au = B[:-1], A[1:]         # sell: bid[i] vs ask[i+1]
    cs = (bb > r * au) if strict else (bb >= r * au)
    sell[:-1] = cs & (bb >= max(M, 1e-9)) & (bb > gate)
    return buy, sell

def runs(f, N):
    out = []; s = None
    for i, x in enumerate(list(f) + [False]):
        if x and s is None: s = i
        if not x and s is not None:
            if i - s >= N: out.append((s, i - 1))
            s = None
    return out

def zones(R, N, M, use_old_gate=False, strict=False):
    Z = []
    for i, (lo, A, B) in enumerate(ARR):
        gate = 0.0
        if use_old_gate:
            if not np.isfinite(oldgate[i]): continue
            gate = oldgate[i]
        fb, fs = flags(A, B, R, M, gate, strict)
        for s, e in runs(fb, N): Z.append((i, +1, (lo + s) * TICK, (lo + e) * TICK, e - s + 1))
        for s, e in runs(fs, N): Z.append((i, -1, (lo + s) * TICK, (lo + e) * TICK, e - s + 1))
    return Z

mode = sys.argv[1] if len(sys.argv) > 1 else "grid"
NB = len(bars)
if mode == "grid":
    print(f"bars={NB} days={ndays} bars/day={NB/ndays:.0f}")
    print("R,N,M,zones/day,bars_per_zone")
    for R in (200, 250, 300, 400):
        for N in (2, 3, 4):
            for M in (1, 2, 3, 5):
                z = zones(R, N, M)
                print(f"{R},{N},{M},{len(z)/ndays:.1f},{NB/max(1,len(z)):.1f}")
    for R, N in ((250, 3), (300, 3)):
        z = zones(R, N, 1, use_old_gate=True)
        print(f"OLDGATE R={R} N={N} M=5/median: zones/day={len(z)/ndays:.1f} bars/zone={NB/max(1,len(z)):.1f}")
        z2 = zones(R, N, 1, strict=True)
        print(f"STRICT> R={R} N={N} M=1: zones/day={len(z2)/ndays:.1f}")
    print("median oldgate", np.median(oldgate[np.isfinite(oldgate)]))
elif mode == "life":
    R, N, M = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    Z = zones(R, N, M)
    H, L, C, O = bars.high.values, bars.low.values, bars.close.values, bars.open.values
    rows = []
    for (i, d, zlo, zhi, n) in Z:
        touch = brk = None
        for j in range(i + 1, min(NB, i + 600)):
            if touch is None and L[j] <= zhi + 1e-9 and H[j] >= zlo - 1e-9: touch = j - i
            if brk is None and ((d > 0 and C[j] < zlo - 1e-9) or (d < 0 and C[j] > zhi + 1e-9)): brk = j - i
            if touch is not None and brk is not None: break
        bt, bb = max(O[i], C[i]), min(O[i], C[i])
        mid = (zlo + zhi) / 2
        pos = "than" if bb - 1e-9 <= mid <= bt + 1e-9 else ("rau_tren" if mid > bt else "rau_duoi")
        # "xấu" theo CORVEN: buy ở râu trên (bị rút râu) / sell ở râu dưới
        bad = (d > 0 and pos == "rau_tren") or (d < 0 and pos == "rau_duoi")
        # giữ khi chạm: chạm rồi trong 10 nến sau chạm KHÔNG đóng xuyên
        held = None
        if touch is not None:
            held = not (brk is not None and brk <= touch + 10)
        rows.append(dict(d=d, n=n, touch=touch, brk=brk, pos=pos, bad=bad, held=held))
    df = pd.DataFrame(rows)
    print(f"R={R} N={N} M={M} zones={len(df)} /day={len(df)/ndays:.1f}")
    t = df.touch.dropna()
    print("touched within 600 bars:", f"{len(t)/len(df):.3f}")
    for q in (0.25, 0.5, 0.75, 0.9, 0.95):
        print(f" touch delay q{int(q*100)} = {t.quantile(q):.0f} bars")
    print(" touch at next bar (d=1):", f"{(t==1).mean():.3f}")
    b = df.brk.dropna()
    print("close-through within 600:", f"{len(b)/len(df):.3f}", "median", b.median())
    print("pos share:", df.pos.value_counts(normalize=True).round(3).to_dict())
    print("bad share:", round(df.bad.mean(), 3))
    sub = df[df.held.notna()]
    for name, s in (("tat ca", sub), ("than/khong xau", sub[~sub.bad]), ("xau (rau nguoc)", sub[sub.bad])):
        print(f" held-after-touch {name}: {s.held.mean():.3f} (n={len(s)})")
    # chạm muộn (xa) vs gần
    for lo_, hi_ in ((1, 5), (6, 30), (31, 120), (121, 600)):
        s = sub[(sub.touch >= lo_) & (sub.touch <= hi_)]
        if len(s): print(f" held when touch in [{lo_},{hi_}]: {s.held.mean():.3f} (n={len(s)})")
    print(" n-levels dist:", df.n.value_counts().sort_index().head(8).to_dict())

if mode == "dens":
    hr = bars.datetime.str[11:13].astype(int).values
    lon = (hr >= 8) & (hr < 13); us = (hr >= 13) & (hr < 20); asia = (hr >= 23) | (hr < 7)
    print("bars/zone by session (UTC): London 08-13 | US 13-20 | Asia 23-07 | all")
    for N in (3, 4):
        for M in (1, 2, 3, 4, 5, 6, 8, 10):
            z = zones(250, N, M)
            zi = np.array([q[0] for q in z]) if z else np.array([], int)
            def bpz(mask):
                c = mask[zi].sum() if len(zi) else 0
                return mask.sum() / max(1, c)
            zero = 0
            for (i, d, zlo, zhi, n) in z:
                lo, A, B = ARR[i]; s = int(round(zlo/TICK)) - lo; e = int(round(zhi/TICK)) - lo
                opp = [B[j-1] for j in range(s, e+1)] if d > 0 else [A[j+1] for j in range(s, e+1)]
                if min(opp) == 0: zero += 1
            print(f"R=250 N={N} M={M}: {bpz(lon):.1f} | {bpz(us):.1f} | {bpz(asia):.1f} | {NB/max(1,len(z)):.1f}  (zones co muc ben kia=0: {zero/max(1,len(z)):.0%})")
