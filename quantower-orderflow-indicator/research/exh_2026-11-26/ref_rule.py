"""Luật kiệt sức ĐỀ XUẤT 2026-11-26 — bản Python tham chiếu, tính tuần tự từng nến (để đối chiếu C# = Python).

Đơn vị là HÀNG giá như chart CORVEN: hàng r gồm các tick [r*G + off, r*G + off + G - 1].
    GC / MGC : G = 2, off = 1   (hàng 0,2 giá, mốc lẻ)        NQ / MNQ : G = 8, off = 4   (hàng 2 điểm, mốc điểm lẻ = NqRows hiện có)
    mã khác  : G = 1, off = 0   (từng tick, CHƯA có chart CORVEN để đối chiếu)
Với mỗi nến đã có footprint (cells = list (tick, bid, ask, vol), vol > 0), o/h/l/c theo tick:
  1. Gộp cells theo hàng: Ask, Bid, Vol của hàng = tổng các tick trong hàng. rowH = hàng chứa High, rowL = hàng chứa Low.
  2. Nền (chỉ từ các nến ĐÃ ĐÓNG TRƯỚC, có giao dịch; cần >= MIN_BARS nến, lấy tối đa N nến gần nhất):
        rowBase = trung bình của [volume TB mỗi hàng CÓ giao dịch của nến]      (cùng công thức với nền chấm theo hàng)
        volBase = trung bình tổng volume nến
  3. Đỉnh (kiệt sức buy, soi Ask):  S_j = Ask của hàng rowH - j, j = 0..ROWS-1 (hàng trống hoặc nằm dưới rowL tính 0)
     Đáy  (kiệt sức sell, soi Bid): S_j = Bid của hàng rowL + j
     Có dấu khi đủ cả ba:
        (a) max(S_0..S_{ROWS-1}) <= A * rowBase          -- 3 hàng sát cực trị đều nhỏ
        (b) tổng volume nến >= C * volBase                 -- nến không quá vắng
        (c) râu >= WICK_ROWS hàng: đỉnh: rowH - hàng chứa max(open, close) >= WICK_ROWS; đáy: hàng chứa min(open, close) - rowL >= WICK_ROWS
  4. Sau khi xét xong, nến (đã đóng) nộp volume TB mỗi hàng và tổng volume vào hàng đợi nền.
Mặc định: ROWS = 3, A = 0.35, C = 0.80, WICK_ROWS = 2, N = 20 (C#: DesiredBaseBars() — M1/M5 = 20, M15 = 8, M30+ = 5), MIN_BARS = 5.
Chạy tay: python ref_rule.py --levels <fp_*.csv> --tick 0.25 --symbol NQ [--minutes 1] --out marks.csv   (ghi t,kind,price như perf/Golden --marks: exhT / exhB)
"""
import math
ROWS, A, C, WICK_ROWS, N, MIN_BARS = 3, 0.35, 0.80, 2, 20, 5
GRID = {'GC': (2, 1), 'MGC': (2, 1), 'NQ': (8, 4), 'MNQ': (8, 4)}

def row_of(tick, G, off): return (tick - off) // G          # chia lấy phần nguyên làm tròn XUỐNG (đúng cả với số âm)

def detect_bar(o, h, l, c, cells, G, off, row_base, vol_base, rows=ROWS, a=A, cmin=C, wick_rows=WICK_ROWS):
    """Trả (top_hit, bot_hit, chi tiết). row_base / vol_base = None khi chưa đủ nền."""
    ask, bid, tot = {}, {}, 0.0
    for tk, b, k, v in cells:
        if v <= 0: continue
        r = row_of(tk, G, off); ask[r] = ask.get(r, 0.0) + k; bid[r] = bid.get(r, 0.0) + b; tot += v
    if not ask or h <= l or row_base is None or vol_base is None or not (row_base > 0): return False, False, None
    rH, rL = row_of(h, G, off), row_of(l, G, off)
    sT = [ask.get(rH - j, 0.0) if rH - j >= rL else 0.0 for j in range(rows)]
    sB = [bid.get(rL + j, 0.0) if rL + j <= rH else 0.0 for j in range(rows)]
    wT = rH - row_of(max(o, c), G, off); wB = row_of(min(o, c), G, off) - rL
    vol_ok = tot >= cmin * vol_base
    top = vol_ok and wT >= wick_rows and max(sT) <= a * row_base
    bot = vol_ok and wB >= wick_rows and max(sB) <= a * row_base
    return top, bot, dict(sT=sT, sB=sB, wT=wT, wB=wB, vol=tot, row_base=row_base, vol_base=vol_base)

def bar_stats(cells, G, off):
    """(volume TB mỗi hàng có giao dịch, tổng volume) của nến; None nếu nến không có giao dịch."""
    rv = {}
    for tk, b, k, v in cells:
        if v > 0: r = row_of(tk, G, off); rv[r] = rv.get(r, 0.0) + v
    if not rv: return None
    tot = sum(rv.values()); return tot / len(rv), tot

def run(bars, G, off, n=N, **kw):
    """bars: list (o, h, l, c, cells) theo thời gian. Trả list (top_hit, bot_hit) từng nến."""
    qm, qv, out = [], [], []
    for o, h, l, c, cells in bars:
        rb = sum(qm) / len(qm) if len(qm) >= MIN_BARS else None
        vb = sum(qv) / len(qv) if len(qv) >= MIN_BARS else None
        t, b, _ = detect_bar(o, h, l, c, cells, G, off, rb, vb, **kw); out.append((t, b))
        st = bar_stats(cells, G, off)
        if st: qm.append(st[0]); qv.append(st[1]); qm = qm[-n:]; qv = qv[-n:]
    return out

def to_tuples(bars):
    """Chuyển nến của data.load sang dạng (o, h, l, c, cells)."""
    return [(b['o'], b['h'], b['l'], b['c'], list(zip(b['tk'].tolist(), b['bid'].tolist(), b['ask'].tolist(), b['vol'].tolist()))) for b in bars]

def load_csv(levels_csv, tick):
    """Đọc file footprint fp_*.csv (+ _bars.csv cùng tên) -> list (thời gian, o, h, l, c, cells) theo thời gian. Chỉ dùng thư viện chuẩn."""
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
    ap.add_argument('--minutes', type=float, default=1); ap.add_argument('--out', required=True); a = ap.parse_args()
    key = next((k for k in ('MGC', 'MNQ', 'GC', 'NQ') if a.symbol.upper().lstrip('/').startswith(k)), None); G, off = GRID.get(key, (1, 0))
    B = load_csv(a.levels, a.tick); res = run([b[1:] for b in B], G, off, n=nbase(a.minutes))
    n = 0
    with open(a.out, 'w') as f:
        f.write('t,kind,price' + chr(10))
        for b, (tp, bt) in zip(B, res):
            if tp: f.write('%s,exhT,%s' %  (b[0][:16], repr(round(b[2] * a.tick, 10))) + chr(10)); n += 1
            if bt: f.write('%s,exhB,%s' %  (b[0][:16], repr(round(b[3] * a.tick, 10))) + chr(10)); n += 1
    print('hang %d tick lech %d | %d nen | %d dau kiet suc -> %s' % (G, off, len(B), n, a.out))
