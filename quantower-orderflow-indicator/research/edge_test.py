"""Chữ ký nào ở cực trị thực sự có EDGE dự báo đảo chiều? (dữ liệu THẬT, bar-level M1)

Mỗi ứng viên phát tín hiệu tại nến cực trị cục bộ; đo trong 20 nến sau:
  WIN  = giá đi ngược đà cũ ≥ TARGET trước khi đi tiếp theo đà cũ ≥ TARGET
So với BASE = mọi nến cực trị cục bộ (không lọc order flow).
"""
import csv, statistics as st

TICK = 0.1
TARGET = 1.0      # 1 USD = 10 tick = 1 "giá"
HORIZON = 20
LOOKBACK = 10     # cực trị cục bộ so với 10 nến trước

rows = []
for r in csv.DictReader(open('data-export/fp-m1-6-month.csv', encoding='utf-8-sig')):
    mm, dd, yy = r['DateTime'].split()[0].split('/')
    if yy != '2026' or int(mm) < 5:
        continue
    try:
        rows.append(dict(t=r['DateTime'], o=float(r['Open']), h=float(r['High']), l=float(r['Low']),
                         c=float(r['Close']), v=float(r['Volume']), d=float(r['Delta'])))
    except ValueError:
        pass
n = len(rows)

medv = [0.0] * n; medr = [0.0] * n
wv, wr = [], []
for i in range(n):
    if len(wv) >= 30:
        medv[i] = st.median(wv); medr[i] = st.median(wr)
    wv.append(rows[i]['v']); wr.append(rows[i]['h'] - rows[i]['l'])
    if len(wv) > 100: wv.pop(0); wr.pop(0)


def outcome(i, short):
    """short=True: thắng nếu giảm TARGET trước khi tăng TARGET"""
    ref = rows[i]['c']
    for j in range(i + 1, min(n, i + HORIZON + 1)):
        if short:
            if ref - rows[j]['l'] >= TARGET: return 1
            if rows[j]['h'] - ref >= TARGET: return 0
        else:
            if rows[j]['h'] - ref >= TARGET: return 1
            if ref - rows[j]['l'] >= TARGET: return 0
    return None


def is_ext(i, top):
    if i < LOOKBACK: return False
    if top: return rows[i]['h'] >= max(rows[j]['h'] for j in range(i - LOOKBACK, i))
    return rows[i]['l'] <= min(rows[j]['l'] for j in range(i - LOOKBACK, i))


def evaluate(name, cond):
    w = t = 0
    for i in range(LOOKBACK, n - HORIZON):
        if medv[i] <= 0: continue
        for top in (True, False):
            if not is_ext(i, top): continue
            if not cond(i, top): continue
            o = outcome(i, short=top)
            if o is None: continue
            t += 1; w += o
    print(f"  {name:52s} n={t:5d}  hit={100*w/max(t,1):5.1f}%")
    return t, w


b = lambda i: rows[i]
rng = lambda i: max(b(i)['h'] - b(i)['l'], TICK)
dp = lambda i: b(i)['d'] / b(i)['v'] if b(i)['v'] > 0 else 0
vr = lambda i: b(i)['v'] / medv[i]
# vị trí đóng cửa trong nến: 1 = đóng ở đỉnh
cp = lambda i: (b(i)['c'] - b(i)['l']) / rng(i)

print(f"tổng nến: {n} | TARGET={TARGET} USD | horizon={HORIZON} nến\n")
print("BASE (không lọc order flow):")
evaluate("mọi nến cực trị cục bộ", lambda i, top: True)

print("\nProxy cho BIG TRADE hiện tại (chỉ cần volume/mức cao ≈ volume nến cao):")
for k in (1.5, 3.0, 5.0):
    evaluate(f"volume ≥ {k}× median", lambda i, top, k=k: vr(i) >= k)

print("\nABSORPTION kiểu 'effort vs result' (phe thuận đà đập mạnh mà giá không giữ):")
for vg, dg, cg in ((1.5, 0.15, 0.5), (2.0, 0.20, 0.4), (2.0, 0.25, 0.35), (3.0, 0.25, 0.35)):
    evaluate(f"vol≥{vg}× & delta thuận≥{dg:.2f} & close lùi>{1-cg:.0%} range",
             lambda i, top, vg=vg, dg=dg, cg=cg: vr(i) >= vg and
             ((dp(i) >= dg and cp(i) <= cg) if top else (dp(i) <= -dg and cp(i) >= 1 - cg)))

print("\nABSORPTION kiểu EBOOK (volume lớn CẢ hai phe, delta ~0, giá đứng):")
for vg, dg, rg in ((2.0, 0.10, 1.0), (2.0, 0.15, 0.8), (3.0, 0.10, 0.8)):
    evaluate(f"vol≥{vg}× & |delta%|≤{dg:.2f} & range≤{rg}× median",
             lambda i, top, vg=vg, dg=dg, rg=rg: vr(i) >= vg and abs(dp(i)) <= dg and rng(i) <= rg * max(medr[i], TICK))

print("\nAGGRESSIVE ngược đà (phe ngược đập ngay tại cực trị):")
for vg, dg in ((1.5, 0.15), (2.0, 0.25)):
    evaluate(f"vol≥{vg}× & delta NGƯỢC ≥{dg:.2f}",
             lambda i, top, vg=vg, dg=dg: vr(i) >= vg and ((dp(i) <= -dg) if top else (dp(i) >= dg)))

print("\nABSORPTION ĐA NẾN (vùng: 3 nến liên tiếp volume cao mà giá không phá tiếp):")
def multi(i, top, vg=1.5):
    if i < 2: return False
    if not all(rows[j]['v'] >= vg * max(medv[j], 1e-9) for j in (i - 2, i - 1, i)): return False
    span = max(rows[j]['h'] for j in (i-2, i-1, i)) - min(rows[j]['l'] for j in (i-2, i-1, i))
    if span > 2.0 * max(medr[i], TICK): return False           # giá bị kẹp trong biên hẹp
    tot = sum(rows[j]['d'] for j in (i-2, i-1, i)); vol = sum(rows[j]['v'] for j in (i-2, i-1, i))
    return (tot / vol >= 0.10) if top else (tot / vol <= -0.10)
evaluate("3 nến vol≥1.5× & biên hẹp & delta thuận đà", multi)
