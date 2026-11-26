"""Vong lon "Big Volume theo hang" DE XUAT 2026-11-26 - ban Python tham chieu, tinh tuan tu tung nen (de doi chieu C# = Python).

Don vi la HANG gia nhu chart CORVEN (cung luoi voi kiet suc ExhRowGrid): hang r gom cac tick [r*G + off, r*G + off + G - 1].
    GC / MGC : G = 2, off = 1        NQ / MNQ : G = 8, off = 4        ma khac : G = 1, off = 0 (chua co chart CORVEN de doi chieu)
Voi moi nen co footprint (cells = list (tick, bid, ask, vol), vol > 0):
  1. Gop cells theo hang: Bid, Ask, Vol cua hang = tong cac tick trong hang.
  2. Nen (chi tu cac nen DA DONG TRUOC co giao dich; can >= MIN_BARS nen, lay toi da N nen gan nhat):
        rowBase = trung binh cua [tong volume nen / so hang co giao dich cua nen]        (dung y cong thuc rowBase cua kiet suc)
  3. Moi hang co  ratio = Vol hang / rowBase >= K  -> MOT vong lon tai hang do. Khong gop hang ke nhau, khong gioi han so vong moi nen.
        gia ve  = tam hang = (r*G + off + (G-1)/2) * tick, kep trong [low, high] cua nen
        phia    = buy neu Ask > Bid, nguoc lai sell        (hai_ben = min(Bid, Ask) >= TWO_SIDED * rowBase: CORVEN to TIM)
        co vong = duong kinh cham thuong x clamp(ratio / SIZE_DIV, SIZE_MIN, SIZE_MAX)
  4. Sau khi xet xong, nen (da dong) nop [tong volume / so hang] vao hang doi nen.
Mac dinh: K = 4.25, SIZE_DIV = 3.2, SIZE_MIN = 1.33, SIZE_MAX = 4.7, TWO_SIDED = 1.3, N = 20 (C#: DesiredBaseBars() - M1/M5 = 20, M15 = 8, M30+ = 5), MIN_BARS = 5.
Chay tay: python ref_rule.py --levels <fp_*.csv> --tick 0.25 --symbol NQ [--minutes 1] --out marks.csv [--detail chi_tiet.csv]
          (--out ghi t,kind,price nhu perf/Golden --marks, kind = bt)
"""
import math
K, SIZE_DIV, SIZE_MIN, SIZE_MAX, TWO_SIDED, N, MIN_BARS = 4.25, 3.2, 1.33, 4.7, 1.3, 20, 5
GRID = {'GC': (2, 1), 'MGC': (2, 1), 'NQ': (8, 4), 'MNQ': (8, 4)}

def row_of(tick, G, off): return (tick - off) // G          # chia lay phan nguyen lam tron XUONG (dung ca voi so am)

def group(cells, G, off):
    bid, ask, vol = {}, {}, {}
    for tk, b, a, v in cells:
        if v <= 0: continue
        r = row_of(tk, G, off); bid[r] = bid.get(r, 0.0) + b; ask[r] = ask.get(r, 0.0) + a; vol[r] = vol.get(r, 0.0) + v
    return bid, ask, vol

def detect_bar(h, l, cells, G, off, row_base, k=K):
    """-> list (hang, tick ve (so thuc, da kep), phia 'B'/'S', ratio, co, hai_ben) theo hang tang dan. row_base None = chua du nen."""
    if row_base is None or not (row_base > 0): return []
    bid, ask, vol = group(cells, G, off); out = []
    for r in sorted(vol):
        ratio = vol[r] / row_base
        if ratio >= k:
            c = min(float(h), max(float(l), r * G + off + (G - 1) / 2.0))
            out.append((r, c, 'B' if ask[r] > bid[r] else 'S', ratio, min(SIZE_MAX, max(SIZE_MIN, ratio / SIZE_DIV)), min(bid[r], ask[r]) >= TWO_SIDED * row_base))
    return out

def bar_stat(cells, G, off):
    _, _, vol = group(cells, G, off)
    return sum(vol.values()) / len(vol) if vol else None

def run(bars, G, off, n=N, k=K):
    """bars: list (o, h, l, c, cells) theo thoi gian. Tra list [vong...] tung nen."""
    q, out = [], []
    for o, h, l, c, cells in bars:
        rb = sum(q) / len(q) if len(q) >= MIN_BARS else None
        out.append(detect_bar(h, l, cells, G, off, rb, k))
        st = bar_stat(cells, G, off)
        if st is not None: q.append(st); q = q[-n:]
    return out

def to_tuples(bars):
    """Chuyen nen cua exh_2026-11-26/data.load sang dang (o, h, l, c, cells)."""
    return [(b['o'], b['h'], b['l'], b['c'], list(zip(b['tk'].tolist(), b['bid'].tolist(), b['ask'].tolist(), b['vol'].tolist()))) for b in bars]

def load_csv(levels_csv, tick):
    import csv
    cells = {}
    with open(levels_csv, newline='') as f:
        for r in csv.DictReader(f):
            v = float(r['volume'])
            if v > 0: cells.setdefault(r['datetime'], []).append((int(round(float(r['price']) / tick)), float(r['bid_vol']), float(r['ask_vol']), v))
    out = []
    with open(levels_csv.replace('.csv', '_bars.csv'), newline='') as f:
        for r in csv.DictReader(f):
            t = r['datetime']
            if t in cells: out.append((t, *(int(round(float(r[k]) / tick)) for k in ('open', 'high', 'low', 'close')), cells[t]))
    out.sort(key=lambda x: x[0]); return out

def nbase(minutes): return 20 if not minutes or minutes <= 0 else int(min(20, max(5, math.floor(120 / minutes + 0.5))))

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('--levels', required=True); ap.add_argument('--tick', type=float, required=True); ap.add_argument('--symbol', default='')
    ap.add_argument('--minutes', type=float, default=1); ap.add_argument('--out', required=True); ap.add_argument('--detail'); a = ap.parse_args()
    key = next((x for x in ('MGC', 'MNQ', 'GC', 'NQ') if a.symbol.upper().lstrip('/').startswith(x)), None); G, off = GRID.get(key, (1, 0))
    B = load_csv(a.levels, a.tick); res = run([b[1:] for b in B], G, off, n=nbase(a.minutes))
    n = nb = 0; det = ['t,price,side,ratio,size,two_sided']
    with open(a.out, 'w') as f:
        f.write('t,kind,price' + chr(10))
        for b, marks in zip(B, res):
            nb += bool(marks)
            for r, c, side, ratio, size, two in marks:
                p = repr(round(c * a.tick, 10)); f.write('%s,bt,%s' % (b[0][:16], p) + chr(10)); n += 1
                det.append('%s,%s,%s,%.4f,%.4f,%d' % (b[0][:16], p, side, ratio, size, two))
    if a.detail: open(a.detail, 'w').write(chr(10).join(det) + chr(10))
    print('hang %d tick lech %d | %d nen | %d vong lon | %d nen co vong | %.4f vong/nen -> %s' % (G, off, len(B), n, nb, n / max(1, len(B)), a.out))
