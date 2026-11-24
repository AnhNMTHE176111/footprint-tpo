"""BẢN CHUẨN từng nến của chế độ "Không theo CORVEN" (vòng 3, r2_review.md mục 6.1; chép từ sa2_ref.py) — đọc ĐÚNG file mà `Golden.dll stophunt --levels` đọc.

python sa3_ref.py <csv footprint> <phút> <tick> [--btlog <nhật ký>] [--zeromot] [--set ten=gia_tri ...] --marks <file> [--from YYYY-MM-DD]

Cách đọc dữ liệu khớp perf/Golden/Program.cs:
  - Nến lấy từ <csv>_bars.csv (cột datetime = giờ UTC, không đổi múi giờ), theo đúng thứ tự dòng; ô lấy từ <csv> theo bar_idx.
    Bid = bid_vol (SellVolume), Ask = ask_vol (BuyVolume), Volume = volume, lệnh đơn = max_one_trade (0 nếu --zeromot).
    Ô quy về tick bằng làm tròn price / tick. Một nến cuối file = nến đang chạy: được xét (dùng nền của các nến đóng), không nộp gì.
  - Nhật ký lệnh đơn (--btlog, cột time_ticks,time_iso,price,mot,buy,sell): như BigTradeLog.CellsOf — ô của nến có time_ticks đúng giờ mở nến,
    quy về tick, trùng tick giữ lệnh lớn hơn. Chỉ dùng khi các ô CSV của nến không có lệnh đơn > 0 (như ComputeBar).
Dấu ghi ra (định dạng --marks của Golden): t,kind,price với t = 'yyyy-MM-dd HH:mm' của nến, kind dotS (chấm bên Bid, đỏ) / dotB (bên Ask, xanh) / bt.
  price của chấm = tick x cỡ tick (như Solid(m.Tick * tick)); của Big Trade = giá ghi trong nhật ký. So sánh nên so theo tick.

Cấu trúc chỉ dùng thứ C# sẽ có:
  - chấm: mỗi (ngày luật, khung giờ) một mảng đếm giá trị bên > 0 (gộp lúc nến đóng), hàng đợi n nến cho dự phòng (mảng đếm cuốn),
    hàng đợi biên độ N nến (CellBigBaseline) cho w. Ngưỡng chính tính một lần khi bước sang (ngày, khung) mới.
  - Big Trade: hàng đợi các nến có số liệu (giá trị lệnh đơn + giờ mở nến), tối đa max(n, floor(1380/phút + 0,5)) nến; hàng đợi biên độ N nến cho g.
--set (mặc định = NỀN MỚI vòng 3): tz=ct|utc K=5 lc=1 mind=2 T=120 pbp=200 (phần vạn: 200 = 2%) sel=nms|lmax|all bt_w=A|B|C bt_T=240 bt_pbp=100 dots=1 bt=1
Vòng 3: (1) nến không có ô nào volume > 0 bị bỏ hẳn với chấm (không xét, không nộp hàng đợi dự phòng, không đánh dấu khung giờ, không đếm vào
số nến ngưỡng chính / dự phòng / chưa có) — như AddToBaseline của C# thoát sớm; (2) khung lân cận bỏ trùng; (3) cách chọn chấm sel."""
import os, sys, argparse, math, numpy as np, pandas as pd
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sa2_lib import ct_offset_hours  # noqa: E402
from sa3_lib import neighbors  # noqa: E402

CAP = 4095
UNIX_TICKS = 621355968000000000


def rhu(x):
    return int(math.floor(x + 0.5))


def nbase(m):
    return int(min(20, max(5, math.floor(120.0 / m + 0.5))))


def fmt_price(x):
    """double.ToString(InvariantCulture) của .NET (khứ hồi ngắn nhất): số nguyên không có '.0'."""
    return str(int(x)) if float(x).is_integer() else repr(float(x))


DEFAULT = dict(tz='ct', K=5, lc=1, mind=2, T=120, pbp=200, sel='nms', bt_w='A', bt_T=240, bt_pbp=100, dots=1, bt=1)


def parse_set(pairs):
    s = dict(DEFAULT)
    for kv in pairs or []:
        k, v = kv.split('=', 1)
        if k not in s: raise SystemExit('không có tham số ' + k)
        s[k] = v if k in ('tz', 'bt_w', 'sel') else int(v)
    if s['sel'] not in ('nms', 'lmax', 'all'): raise SystemExit('sel phải là nms|lmax|all')
    return s


def load_csv(levels_csv, zeromot=False, from_day=None):
    """Trả list nến: (t: pd.Timestamp, tick-array, bid, ask, vol, mot, price-array), theo thứ tự dòng của _bars.csv."""
    B = pd.read_csv(levels_csv.replace('.csv', '_bars.csv'), usecols=['bar_idx', 'datetime'])
    L = pd.read_csv(levels_csv, usecols=['bar_idx', 'price', 'bid_vol', 'ask_vol', 'volume', 'max_one_trade'])
    B['t'] = pd.to_datetime(B.datetime)
    if from_day is not None:
        B = B[B.t >= pd.Timestamp(from_day)]
    L = L[L.bar_idx.isin(B.bar_idx)]
    L = L.sort_values('bar_idx', kind='stable')
    bi = L.bar_idx.values
    st = np.searchsorted(bi, B.bar_idx.values, 'left'); en = np.searchsorted(bi, B.bar_idx.values, 'right')
    P = L.price.values.astype(float); bid = L.bid_vol.values.astype(float); ask = L.ask_vol.values.astype(float)
    vol = L.volume.values.astype(float); mot = np.zeros(len(L)) if zeromot else L.max_one_trade.values.astype(float)
    nonint = int(((bid % 1) != 0).sum() + ((ask % 1) != 0).sum())
    bars = [(t, P[a:e], bid[a:e], ask[a:e], vol[a:e], mot[a:e]) for t, a, e in zip(B.t, st, en)]
    return bars, nonint


def load_btlog(path):
    """time_ticks -> list (price, mot) theo thứ tự dòng (BigTradeLog._byBar)."""
    d = pd.read_csv(path, usecols=['time_ticks', 'price', 'mot'])
    by = {}
    for tt, p, m in zip(d.time_ticks.values, d.price.values, d.mot.values):
        by.setdefault(int(tt), []).append((float(p), float(m)))
    return by


def cells_of(by, t, tick):
    l = by.get(int((t.value // 100) + UNIX_TICKS))
    if not l: return []
    res = {}; order = []
    for p, m in l:
        k = int(round(p / tick))
        if k in res:
            if m > res[k][1]: res[k] = (p, m)
        else:
            res[k] = (p, m); order.append(k)
    return sorted(((k, res[k][1], res[k][0]) for k in order), key=lambda x: x[0])


def kth1(h, KK):
    """h: mảng đếm (numpy). Giá trị lớn thứ KK+1 hoặc None."""
    suf = np.cumsum(h[::-1])[::-1]
    idx = np.nonzero(suf >= KK + 1)[0]
    return int(idx[-1]) if len(idx) else None


def K_p(n, pbp):
    return (pbp * n) // 10000 if n * pbp >= 50000 else -1


def day_slot(t, m, tz):
    W = max(30, m); nsl = -(-1440 // W)
    if tz == 'ct':
        loc = t + pd.Timedelta(hours=int(ct_offset_hours(pd.DatetimeIndex([t]))[0]))
        day = (loc + pd.Timedelta(hours=7)).normalize()
    else:
        loc = t; day = (loc + pd.Timedelta(hours=2)).normalize()
    return day, (loc.hour * 60 + loc.minute) // W, nsl


def run(bars, m, tick, S, by=None):
    """Đi từng nến. Trả list dấu (t, kind, tick, price) và thống kê nhỏ."""
    N = nbase(m)
    marks = []
    # ---- chấm
    rangeq = deque()                                   # biên độ (tick) của N nến đóng có giao dịch
    nfb = max(5, rhu(S['T'] / m)); fbq = deque(); fbh = np.zeros(CAP + 1, np.int64); fbn = 0
    slots = {}                                         # khung -> list [ngày, mảng đếm (np), số nến]
    cur_key = None; cur_main = None
    # ---- Big Trade
    btn = max(5, rhu(S['bt_T'] / m)); btmax = max(btn, rhu(1380 / m)); btq = deque(); btrq = deque()
    need = -(-50000 // S['bt_pbp'])
    st = dict(chinh=0, du_phong=0, chua=0, bt_co=0, bt_chua=0)
    nbars = len(bars)
    for bi, (t, P, bid, ask, vol, mot) in enumerate(bars):
        closed = bi < nbars - 1
        tks = np.array([int(round(p / tick)) for p in P], np.int64)
        bid_i = np.floor(bid).astype(np.int64); ask_i = np.floor(ask).astype(np.int64)
        vals = np.r_[bid_i[bid_i > 0], ask_i[ask_i > 0]]
        has_vol = bool((vol > 0).any())
        if not has_vol: st['nen_rong'] = st.get('nen_rong', 0) + 1
        # ============ chấm: ngưỡng của nến này (chỉ từ nến đã đóng); nến rỗng bỏ hẳn
        if S['dots'] and has_vol:
            day, slot, nsl = day_slot(t, m, S['tz'])
            if (day, slot) != cur_key:
                cur_key = (day, slot); cur_main = None
                lst = [e for e in slots.get(slot, []) if e[0] < day][-S['K']:]
                if len(lst) >= S['mind']:
                    parts = list(lst)
                    for ss in neighbors(slot, nsl, S['lc'])[1:]:
                        parts += [e for e in slots.get(ss, []) if e[0] < day][-S['K']:]
                    L = max(len(e[1]) for e in parts)
                    h = np.zeros(L, np.int64)
                    for e in parts: h[:len(e[1])] += e[1]
                    n = int(h.sum()); KK = K_p(n, S['pbp'])
                    if KK >= 0 and n >= KK + 1:
                        cur_main = kth1(h, KK)
            thr = cur_main
            if thr is not None:
                st['chinh'] += 1
            else:
                KK = K_p(fbn, S['pbp'])
                if KK >= 0 and fbn >= KK + 1:
                    thr = kth1(fbh, KK)
                st['du_phong' if thr is not None else 'chua'] += 1
            if thr is not None and len(tks):
                w = 4
                if len(rangeq) >= 5:
                    Rv = 0.0
                    for r in rangeq: Rv += r
                    Rv /= len(rangeq)
                    w = max(4, rhu(Rv / 6.0)) if Rv > 0 else 4
                for side, arr, kind in ((0, bid_i, 'dotS'), (1, ask_i, 'dotB')):
                    cand = np.nonzero(arr > thr)[0]
                    if not len(cand): continue
                    if S['sel'] == 'lmax':
                        dct = {int(k): int(v) for k, v in zip(tks, arr) if v > 0}
                        for i in cand:
                            k0, v0 = int(tks[i]), int(arr[i])
                            if all(dct.get(k0 + o, 0) < v0 and dct.get(k0 - o, 0) < v0 for o in range(1, w + 1)):
                                marks.append((t, kind, k0, fmt_price(k0 * tick)))
                    else:
                        # ô vượt (tick, giá trị); trùng tick (không xảy ra với CSV đã gộp) giữ giá trị lớn hơn
                        cc = {}
                        for i in cand:
                            k0, v0 = int(tks[i]), int(arr[i])
                            if v0 > cc.get(k0, -1): cc[k0] = v0
                        order = sorted(cc.items(), key=lambda x: (-x[1], x[0]))
                        kept = []
                        for k0, v0 in order:
                            if S['sel'] == 'all' or all(abs(k0 - kk) > w for kk in kept):
                                kept.append(k0)
                        for k0 in sorted(kept):
                            marks.append((t, kind, k0, fmt_price(k0 * tick)))
        # ============ Big Trade
        if S['bt']:
            cells = [(int(round(p / tick)), float(mo), float(p)) for p, mo in zip(P, mot) if mo > 0]
            cells.sort(key=lambda x: x[0])
            if not cells and by is not None:
                cells = cells_of(by, t, tick)
            if cells:
                sel = list(btq)[-btn:]
                if S['bt_w'] in ('B', 'C'):
                    tot = sum(len(x[1]) for x in sel)
                    k = len(btq) - len(sel)
                    while tot < need and len(sel) < btmax and k > 0:
                        k -= 1; sel.insert(0, btq[k]); tot += len(btq[k][1])
                if S['bt_w'] == 'C':
                    sel = [x for x in sel if x[0] >= t - pd.Timedelta(minutes=720)]
                h = np.zeros(CAP + 1, np.int64)
                for _, vs in sel:
                    for v in vs: h[min(int(v), CAP)] += 1
                n = int(h.sum()); KK = K_p(n, S['bt_pbp'])
                thr = kth1(h, KK) if (KK >= 0 and n >= KK + 1) else None
                st['bt_co' if thr is not None else 'bt_chua'] += 1
                if thr is not None:
                    g = 2
                    if len(btrq) >= 5:
                        s_ = 0.0
                        for r in btrq: s_ += r
                        avg = s_ / len(btrq)
                        g = max(2, rhu(avg / 8.0)) if avg > 0 else 2
                    order = sorted([i for i, c in enumerate(cells) if c[1] > thr], key=lambda i: (-cells[i][1], cells[i][0], i))
                    kept = []
                    for i in order:
                        if all(abs(cells[i][0] - cells[j][0]) > g for j in kept): kept.append(i)
                    for i in kept:
                        marks.append((t, 'bt', cells[i][0], fmt_price(cells[i][2])))
        # ============ nến đóng: nộp đúng một lần
        if not closed: continue
        if S['dots'] and has_vol:
            if True:
                tv = tks[vol > 0]
                rangeq.append(int(tv.max() - tv.min()))
                while len(rangeq) > N: rangeq.popleft()
            fbq.append(vals); np.add.at(fbh, np.minimum(vals, CAP), 1); fbn += len(vals)
            if len(fbq) > nfb:
                old = fbq.popleft(); np.add.at(fbh, np.minimum(old, CAP), -1); fbn -= len(old)
            lst = slots.setdefault(slot, [])
            hv = np.bincount(np.minimum(vals, CAP), minlength=1).astype(np.int64) if len(vals) else np.zeros(1, np.int64)
            if lst and lst[-1][0] == day:
                a = lst[-1][1]
                if len(hv) > len(a): a = np.r_[a, np.zeros(len(hv) - len(a), np.int64)]
                a[:len(hv)] += hv; lst[-1][1] = a; lst[-1][2] += 1
            else:
                lst.append([day, hv, 1])
        if S['bt'] and cells:
            btq.append((t, [c[1] for c in cells]))
            while len(btq) > btmax: btq.popleft()
            btrq.append(max(c[0] for c in cells) - min(c[0] for c in cells))
            while len(btrq) > N: btrq.popleft()
    return marks, st


def write_marks(path, marks):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('t,kind,price\n')
        for t, k, _, p in marks:
            f.write(f'{t:%Y-%m-%d %H:%M},{k},{p}\n')


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('levels'); ap.add_argument('minutes', type=int); ap.add_argument('tick', type=float)
    ap.add_argument('--btlog'); ap.add_argument('--zeromot', action='store_true'); ap.add_argument('--set', action='append')
    ap.add_argument('--marks', required=True); ap.add_argument('--from', dest='from_day')
    a = ap.parse_args(argv)
    S = parse_set(a.set)
    bars, nonint = load_csv(a.levels, a.zeromot, a.from_day)
    by = load_btlog(a.btlog) if a.btlog else None
    marks, st = run(bars, a.minutes, a.tick, S, by)
    write_marks(a.marks, marks)
    nS = sum(1 for x in marks if x[1] == 'dotS'); nB = sum(1 for x in marks if x[1] == 'dotB'); nbt = sum(1 for x in marks if x[1] == 'bt')
    print(f'{len(bars)} nến; chấm đỏ (Bid) {nS}, chấm xanh (Ask) {nB}, Big Trade {nbt}; nến có ngưỡng chính {st["chinh"]}, dự phòng {st["du_phong"]}, chưa có {st["chua"]}; '
          f'nến Big Trade có ngưỡng {st["bt_co"]}, chưa có {st["bt_chua"]}; giá trị bên không nguyên {nonint} -> {a.marks}')
    return dict(n=len(bars), dotS=nS, dotB=nB, bt=nbt, **st, nonint=nonint)


if __name__ == '__main__':
    main()
