"""BẢN CHUẨN từng nến của Big Trade "lệnh cá mập" (SPEC.md) — Fable viết độc lập với bw1_*.py, 2026-11-25.

python bw2_ref.py <csv footprint> <phút> <tick> --btlog <nhật ký> --marks <file dấu> [--set D=5 R=8 W=1380] [--trace <file ngưỡng>]
python bw2_ref.py --logonly <nhật ký> <phút> <tick> --marks <file dấu>        (nến = các nến có trong nhật ký; dùng để review)

Đọc dữ liệu như `Golden.dll stophunt --levels <csv> --zeromot --btlog <nhật ký>`:
  - Nến lấy từ <csv>_bars.csv (cột datetime = giờ UTC), đúng thứ tự dòng. Nến cuối file = nến đang chạy: được xét, không nộp.
  - Ô lệnh đơn của nến = BigTradeLog.CellsOf(giờ mở nến): quy giá về tick bằng round(price / tick), trùng tick giữ lệnh lớn hơn
    (bằng nhau giữ dòng trước), sắp tick tăng dần. (--zeromot: CSV không cấp lệnh đơn, nên mọi ô đều từ nhật ký.)

Luật (SPEC.md mục 2):
  n   = max(1, rhu(D x 1380 / m))            số nến có số liệu giữ trong hàng đợi (m = phút một nến, D = 5)
  phút = số nến trong hàng đợi x m
  phút < W (1380)  -> CHƯA CÓ ngưỡng, không vẽ vòng nào
  K   = max(1, rhu(R x phút / 1380))         (R = 8)
  ngưỡng = giá trị lớn thứ K của mọi lệnh đơn > 0 trong hàng đợi (mảng đếm 4096 ô, giá trị > 4095 dồn ô 4095)
  vòng: ô có lệnh đơn > ngưỡng (lớn hơn hẳn); duyệt lệnh giảm dần (bằng nhau: tick thấp trước), bỏ ô cách ô đã giữ <= g tick
  g   = max(2, rhu(biên độ TB / 8)) khi hàng đợi biên độ (N = min(20, max(5, rhu(120 / m))) nến) có >= 5 số và TB > 0; ngược lại 2
  Nộp (nến đóng, có ít nhất một ô lệnh đơn > 0): mọi lệnh đơn > 0 của nến + biên độ (tick cao nhất - thấp nhất các ô đó).
"""
import sys, argparse, math, csv
from collections import deque
from datetime import datetime, timedelta

CAP = 4095
DAY = 1380
UNIX_TICKS = 621355968000000000
EPOCH = datetime(1970, 1, 1)


def rhu(x):
    return int(math.floor(x + 0.5))


def nbase(m):
    return int(min(20, max(5, math.floor(120.0 / m + 0.5)))) if m > 0 else 20


def fmt_price(x):
    return str(int(x)) if float(x).is_integer() else repr(float(x))


def load_btlog(path):
    """time_ticks -> list (price, mot) theo thứ tự dòng (BigTradeLog._byBar; bỏ mot <= 0; KHÔNG bỏ dòng trùng — CellsOf tự giữ lệnh lớn hơn)."""
    by = {}
    with open(path, encoding='utf-8') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 6: continue
            mot = float(row[3])
            if not mot > 0: continue
            by.setdefault(int(row[0]), []).append((float(row[2]), mot))
    return by


def cs_round(x):
    """Math.Round của .NET (làm tròn nửa về số chẵn) = round() của Python."""
    return int(round(x))


def cells_of(lst, tick):
    res = {}; order = []
    for p, m in lst:
        k = cs_round(p / tick)
        if k in res:
            if m > res[k][1]: res[k] = (p, m)
        else:
            res[k] = (p, m); order.append(k)
    return sorted(((k, res[k][1], res[k][0]) for k in order), key=lambda x: x[0])


def bar_ticks(t):
    d = t - EPOCH
    return (d.days * 86400 + d.seconds) * 10000000 + UNIX_TICKS


def load_bars(levels_csv):
    out = []
    with open(levels_csv.replace('.csv', '_bars.csv'), encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            out.append(datetime.strptime(row['datetime'][:19], '%Y-%m-%d %H:%M:%S'))
    return out


class Whale:
    """Trạng thái đúng như lớp C# BigTradeWhale: hàng đợi nến có số liệu + mảng đếm + hàng đợi biên độ."""

    def __init__(self, m, D=5, R=8, W=1380):
        self.m = m if m > 0 else 1.0
        self.D, self.R, self.W = D, R, W
        self.n = max(1, rhu(D * DAY / self.m))
        self.nr = nbase(self.m)
        self.q = deque(); self.h = [0] * (CAP + 1); self.cnt = 0
        self.rq = deque()

    def minutes(self):
        return len(self.q) * self.m

    def threshold(self):
        """Trả ngưỡng (int) hoặc None khi chưa có."""
        mn = self.minutes()
        if mn < self.W: return None
        K = max(1, rhu(self.R * mn / DAY))
        if self.cnt < K: return None
        c = 0
        for v in range(CAP, 0, -1):
            c += self.h[v]
            if c >= K: return v
        return None

    def merge_ticks(self):
        if len(self.rq) < 5: return 2
        s = 0.0
        for r in self.rq: s += r
        avg = s / len(self.rq)
        return max(2, rhu(avg / 8.0)) if avg > 0 else 2

    def select(self, cells, thr, g):
        order = sorted([i for i, c in enumerate(cells) if c[1] > 0 and c[1] > thr], key=lambda i: (-cells[i][1], cells[i][0], i))
        kept = []
        for i in order:
            if all(abs(cells[i][0] - cells[j][0]) > g for j in kept): kept.append(i)
        return sorted(kept, key=lambda i: cells[i][0])

    def add_closed(self, cells):
        vals = [min(int(math.floor(c[1])), CAP) for c in cells if c[1] > 0]
        if not vals: return
        self.q.append(vals); self.cnt += len(vals)
        for v in vals: self.h[v] += 1
        while len(self.q) > self.n:
            old = self.q.popleft(); self.cnt -= len(old)
            for v in old: self.h[v] -= 1
        tk = [c[0] for c in cells if c[1] > 0]
        self.rq.append(max(tk) - min(tk))
        while len(self.rq) > self.nr: self.rq.popleft()


def run(bars, m, tick, by, D=5, R=8, W=1380, last_running=True):
    """bars: list datetime (UTC). Trả (marks, trace, stat). marks: (t, tick, mot, price, thr, g); trace: (t, thr hoặc None, số nến hàng đợi) của nến có số liệu."""
    w = Whale(m, D, R, W)
    marks = []; trace = []
    st = dict(co=0, chua=0, khong_so_lieu=0)
    nb = len(bars)
    for bi, t in enumerate(bars):
        closed = (bi < nb - 1) or not last_running
        lst = by.get(bar_ticks(t))
        cells = cells_of(lst, tick) if lst else []
        if not cells:
            st['khong_so_lieu'] += 1
            continue
        thr = w.threshold()
        trace.append((t, thr, len(w.q)))
        if thr is None: st['chua'] += 1
        else:
            st['co'] += 1
            g = w.merge_ticks()
            for i in w.select(cells, thr, g):
                marks.append((t, cells[i][0], cells[i][1], cells[i][2], thr, g))
        if closed: w.add_closed(cells)
    return marks, trace, st


def write_marks(path, marks):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('t,kind,price\n')
        for t, _, _, p, _, _ in marks:
            f.write(f'{t:%Y-%m-%d %H:%M},bt,{fmt_price(p)}\n')


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('levels'); ap.add_argument('minutes', type=float); ap.add_argument('tick', type=float)
    ap.add_argument('--btlog'); ap.add_argument('--logonly', action='store_true')
    ap.add_argument('--marks', required=True); ap.add_argument('--trace'); ap.add_argument('--set', nargs='*', default=[])
    a = ap.parse_args(argv)
    S = dict(D=5, R=8, W=1380)
    for kv in a.set:
        k, v = kv.split('='); S[k] = float(v) if '.' in v else int(v)
    if a.logonly:
        by = load_btlog(a.levels)
        bars = [EPOCH + timedelta(microseconds=(tt - UNIX_TICKS) // 10) for tt in sorted(by)]
        marks, trace, st = run(bars, a.minutes, a.tick, by, last_running=False, **S)
    else:
        by = load_btlog(a.btlog)
        bars = load_bars(a.levels)
        marks, trace, st = run(bars, a.minutes, a.tick, by, **S)
    write_marks(a.marks, marks)
    if a.trace:
        with open(a.trace, 'w', encoding='utf-8', newline='\n') as f:
            f.write('t,thr,queue_bars\n')
            for t, thr, n in trace: f.write(f'{t:%Y-%m-%d %H:%M},{"" if thr is None else thr},{n}\n')
    thrs = sorted(x[1] for x in trace if x[1] is not None)
    med = thrs[len(thrs) // 2] if thrs else None
    print(f'{len(bars)} nến; Big Trade {len(marks)} vòng; nến có số liệu: có ngưỡng {st["co"]}, chưa có {st["chua"]}; nến không có số liệu {st["khong_so_lieu"]}; '
          f'ngưỡng nhỏ nhất / giữa / lớn nhất {thrs[0] if thrs else None} / {med} / {thrs[-1] if thrs else None}; '
          f'vòng nhỏ nhất {min((x[2] for x in marks), default=None)} -> {a.marks}')
    return marks, trace, st


if __name__ == '__main__':
    main()
