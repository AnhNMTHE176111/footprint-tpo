# -*- coding: utf-8 -*-
"""
range_proto.py — máy trạng thái RANGE theo cụm pivot (BRAINSTORM.md mục 4, ghi đè bởi mục 7b).

Bản Python MẪU. RangeLogic.cs phải cho ra ĐÚNG danh sách sự kiện này (đối chiếu 100 %).
Chỉ dùng OHLC. Mọi giá đổi sang SỐ TICK NGUYÊN ngay khi vào (round(price/tick)) để Python và C#
tính giống hệt nhau; median của số nguyên là x.0 hoặc x.5 nên so sánh double không lệch.

Thứ tự xử lý MỖI NẾN ĐÃ ĐÓNG i (C# làm đúng thứ tự này):
  1. mbr  = median(high-low) 100 nến gần nhất, TÍNH CẢ nến i (cuốn chiếu, không nhìn tương lai).
  2. pivot nến j=i-1: đỉnh nếu H[j] > H[j-1] và H[j] >= H[i]; đáy nếu L[j] < L[j-1] và L[j] <= L[i].
  3. mỗi range chưa chết: (Active) cập nhật cạnh bằng pivot mới → xét sự kiện của nến i.
  4. nếu KHÔNG có range nào Active/Pending: tìm range ứng viên kết thúc tại i → gộp hoặc sinh mới.
"""
from __future__ import annotations
import csv
from dataclasses import dataclass, field

ACTIVE, PENDING, BROKEN, DEAD = 0, 1, 2, 3


@dataclass
class Params:
    MinBars: int = 8          # lõi tối thiểu (nến sau cây chạy vào → nến hiện tại)
    HminK: float = 1.6        # chiều cao tối thiểu × mbr (MEASURE.md: = tỷ lệ nhỏ nhất CORVEN B04/B08)
    HmaxK: float = 6.0        # chiều cao tối đa × mbr
    TolK: float = 0.5         # dung sai cụm cạnh × mbr (sàn 2 tick)
    K: int = 3                # số nến chờ sau nến đóng ngoài
    G: int = 30               # số nến cho phép quay lại (ReEntry) sau khi phá thật
    PivotRule: str = "A"      # "A": mỗi cạnh ≥1, tổng ≥3, ≥1 cạnh có ≥2 ; "B": mỗi cạnh ≥2
    InsideRatio: float = 0.0  # tỷ lệ nến lõi ĐÓNG trong [bottom, top] (0 = tắt)
    MaxLook: int = 60         # cửa sổ pivot để tìm range (≥ lõi dài nhất CORVEN 54 nến)
    MbrLen: int = 100         # số nến tính mbr
    MinTolTicks: float = 2.0  # sàn dung sai (tick)
    MaxReEntry: int = 2       # số lần ReEntry tối đa; lần phá thật thứ MaxReEntry+1 ⇒ Dead NGAY (không chờ G, không Merge hồi sinh).
                              # < 0 = không giới hạn. Nguồn: CORVEN chỉ nói "confirm lần 2" (B05); hộp CORVEN dài nhất 73 nến,
                              # không giới hạn thì 26,5 % hộp máy dài hơn và có range 21 lần ReEntry (REVIEW-1, tester mục 11).

    def key(self):
        return (self.MinBars, self.HminK, self.HmaxK, self.TolK, self.K, self.G, self.PivotRule, self.InsideRatio, self.MaxReEntry)


def median(vals):
    a = sorted(vals)
    n = len(a)
    if n == 0:
        return 0.0
    if n % 2 == 1:
        return float(a[n // 2])
    return (a[n // 2 - 1] + a[n // 2]) / 2.0


def best_cluster(piv, tol):
    """piv: list (idx, price_ticks) theo thời gian. Trả (members, median) của cụm đông nhất.
    Hạt giống từng pivot → lấy pivot trong ±tol hạt giống → median → lọc lại ±tol quanh median.
    Khoá so sánh (số thành viên, idx thành viên muộn nhất); hoà thì giữ hạt giống SỚM hơn."""
    best = None
    bkey = None
    for (_, sp) in piv:
        m1 = [p for (_, p) in piv if abs(p - sp) <= tol]
        med1 = median(m1)
        m2 = [(ix, p) for (ix, p) in piv if abs(p - med1) <= tol]
        k = (len(m2), m2[-1][0])
        if bkey is None or k > bkey:
            bkey = k
            best = m2
    return best, median([p for (_, p) in best])


@dataclass
class Range:
    id: int
    start: int
    birth: int
    top: float
    bottom: float
    top0: float
    bottom0: float
    tol: float
    mbr: float
    top_m: list
    bot_m: list
    state: int = ACTIVE
    pend_side: int = 0        # +1 lên, -1 xuống
    pend_start: int = -1
    break_idx: int = -1       # nến đóng ngoài đầu tiên của lần phá thật gần nhất
    break_side: int = 0
    first_break: int = -1     # nến đóng ngoài của lần phá thật ĐẦU TIÊN (chỉ để đo)
    last_idx: int = -1        # nến cuối range còn hiệu lực (để đo bề rộng)
    n_hunt: int = 0
    n_fail: int = 0
    n_break: int = 0
    exhausted: bool = False   # đã Dead vì hết lượt ReEntry (MaxReEntry) — không bao giờ sống lại


@dataclass
class Event:
    bar: int
    kind: str      # StopHunt / CloseOutside / FailBreak / BreakConfirmed / ReEntry / Birth / Merge
    side: int      # +1 cạnh trên, -1 cạnh dưới, 0
    top: float     # tick
    bottom: float  # tick
    start: int
    ref: int       # nến tham chiếu (nến đóng ngoài đầu tiên với FailBreak/BreakConfirmed), không thì = bar
    rid: int


class RangeEngine:
    def __init__(self, p: Params, tick: float = 0.1):
        self.p = p
        self.tick = tick
        self.H, self.L, self.C, self.O = [], [], [], []
        self.ph, self.pl = [], []       # pivot (idx, price)
        self.win = []                   # biên độ 100 nến gần nhất (FIFO)
        self.sorted_win = []
        self.mbr = 0.0
        self.ranges: list[Range] = []
        self.live: list[Range] = []     # range chưa chết, theo thứ tự sinh
        self.events: list[Event] = []
        self.scan_start = 0

    # ---------- mbr cuốn chiếu ----------
    def _push_range(self, r):
        import bisect
        self.win.append(r)
        bisect.insort(self.sorted_win, r)
        if len(self.win) > self.p.MbrLen:
            old = self.win.pop(0)
            del self.sorted_win[bisect.bisect_left(self.sorted_win, old)]
        a = self.sorted_win
        n = len(a)
        self.mbr = float(a[n // 2]) if n % 2 else (a[n // 2 - 1] + a[n // 2]) / 2.0

    def feed(self, o, h, l, c):
        t = self.tick
        self.feed_ticks(round(o / t), round(h / t), round(l / t), round(c / t))

    def feed_ticks(self, o, h, l, c):
        i = len(self.H)
        self.O.append(o); self.H.append(h); self.L.append(l); self.C.append(c)
        self._push_range(h - l)
        newph = newpl = None
        if i >= 2:
            j = i - 1
            H, L = self.H, self.L
            if H[j] > H[j - 1] and H[j] >= H[i]:
                newph = (j, H[j]); self.ph.append(newph)
            if L[j] < L[j - 1] and L[j] <= L[i]:
                newpl = (j, L[j]); self.pl.append(newpl)
        # dọn pivot quá cũ (giữ đủ cho MaxLook)
        lim = i - self.p.MaxLook - 2
        while self.ph and self.ph[0][0] < lim: self.ph.pop(0)
        while self.pl and self.pl[0][0] < lim: self.pl.pop(0)

        busy = False
        for r in self.live:
            self._step_range(r, i, newph, newpl)
            if r.state in (ACTIVE, PENDING):
                busy = True
        if any(r.state == DEAD for r in self.live):
            self.live = [r for r in self.live if r.state != DEAD]
        if not busy:
            self._scan(i)

    # ---------- range đang sống ----------
    def _ev(self, i, kind, side, r, ref=None):
        self.events.append(Event(i, kind, side, r.top, r.bottom, r.start, i if ref is None else ref, r.id))

    def _step_range(self, r: Range, i, newph, newpl):
        p = self.p
        H, L, C = self.H[i], self.L[i], self.C[i]
        if r.state == ACTIVE:
            if newph is not None and abs(newph[1] - r.top) <= r.tol:
                r.top_m.append(newph[1])
                r.top = min(max(median(r.top_m), r.top0 - r.tol), r.top0 + r.tol)
            if newpl is not None and abs(newpl[1] - r.bottom) <= r.tol:
                r.bot_m.append(newpl[1])
                r.bottom = min(max(median(r.bot_m), r.bottom0 - r.tol), r.bottom0 + r.tol)
            if C > r.top:
                r.state, r.pend_side, r.pend_start = PENDING, +1, i
                self._ev(i, "CloseOutside", +1, r)
            elif C < r.bottom:
                r.state, r.pend_side, r.pend_start = PENDING, -1, i
                self._ev(i, "CloseOutside", -1, r)
            else:
                r.last_idx = i
                if H - r.top >= 1:
                    r.n_hunt += 1; self._ev(i, "StopHunt", +1, r)
                if r.bottom - L >= 1:
                    r.n_hunt += 1; self._ev(i, "StopHunt", -1, r)
        elif r.state == PENDING:
            s = r.pend_side
            if r.bottom <= C <= r.top:
                r.n_fail += 1
                self._ev(i, "FailBreak", s, r, r.pend_start)
                r.state, r.pend_side = ACTIVE, 0
                r.last_idx = i
            elif (s > 0 and C < r.bottom) or (s < 0 and C > r.top):
                r.n_fail += 1
                self._ev(i, "FailBreak", s, r, r.pend_start)
                r.pend_side, r.pend_start = -s, i
                self._ev(i, "CloseOutside", -s, r)
            elif i - r.pend_start >= p.K:
                r.n_break += 1
                r.state, r.break_idx, r.break_side = BROKEN, r.pend_start, s
                if r.first_break < 0:
                    r.first_break = r.pend_start
                self._ev(i, "BreakConfirmed", s, r, r.pend_start)
                self.scan_start = max(self.scan_start, r.pend_start)
                if p.MaxReEntry >= 0 and r.n_break > p.MaxReEntry:
                    r.state, r.exhausted = DEAD, True
                elif p.G <= 0 or i - r.break_idx >= p.G:
                    r.state = DEAD
        elif r.state == BROKEN:
            if r.bottom <= C <= r.top:
                self._ev(i, "ReEntry", r.break_side, r, r.break_idx)
                r.state = ACTIVE
                r.last_idx = i
            elif i - r.break_idx >= p.G:
                r.state = DEAD

    # ---------- tìm range mới ----------
    def _candidate(self, i):
        p = self.p
        if i + 1 < p.MbrLen:
            return None
        mbr = self.mbr
        tol = max(p.MinTolTicks, p.TolK * mbr)
        lo_lim = max(self.scan_start, i - p.MaxLook + 1)
        lo = lo_lim
        C = self.C
        for _it in range(3):
            H = [x for x in self.ph if x[0] >= lo]
            Lw = [x for x in self.pl if x[0] >= lo]
            if not H or not Lw:
                return None
            tm, top = best_cluster(H, tol)
            bm, bot = best_cluster(Lw, tol)
            if top <= bot:
                return None
            first = min(tm[0][0], bm[0][0])
            hi_b, lo_b = top + tol, bot - tol
            k = -1
            for j in range(i, first - 1, -1):
                if C[j] > hi_b or C[j] < lo_b:
                    k = j
                    break
            if k < 0:
                break
            lo = k + 1
        else:
            return None
        nt, nb = len(tm), len(bm)
        if p.PivotRule == "B":
            if nt < 2 or nb < 2:
                return None
        else:
            if nt < 1 or nb < 1 or nt + nb < 3 or max(nt, nb) < 2:
                return None
        # đan xen: dãy loại pivot theo thời gian đổi chiều ≥ 2 lần
        seq = sorted([(ix, 1) for ix, _ in tm] + [(ix, -1) for ix, _ in bm])
        ch = sum(1 for a, b in zip(seq, seq[1:]) if a[1] != b[1])
        if ch < 2:
            return None
        h = top - bot
        if h < p.HminK * mbr or h > p.HmaxK * mbr:
            return None
        # nến bắt đầu = cây "chạy vào vùng": lùi về trước khi close còn trong dải
        start = first
        j = first - 1
        while j >= lo_lim and lo_b <= C[j] <= hi_b:
            j -= 1
        start = j + 1
        core = i - start
        if core < p.MinBars:
            return None
        if p.InsideRatio > 0:
            n_in = sum(1 for jj in range(start + 1, i + 1) if bot <= C[jj] <= top)
            if n_in < p.InsideRatio * core:
                return None
        return dict(start=start, top=top, bot=bot, tol=tol, mbr=mbr,
                    tm=[x[1] for x in tm], bm=[x[1] for x in bm])

    def _scan(self, i):
        cnd = self._candidate(i)
        if cnd is None:
            return
        # gộp: chỉ khi CẢ HAI cạnh trong ±tol của range gần nhất còn trong cửa sổ G sau phá
        if self.ranges:
            r = self.ranges[-1]
            if (r.state in (BROKEN, DEAD) and not r.exhausted and r.break_idx >= 0 and cnd["start"] <= r.break_idx + self.p.G
                    and abs(cnd["top"] - r.top) <= r.tol and abs(cnd["bot"] - r.bottom) <= r.tol):
                if r.state == DEAD:
                    self.live.append(r)
                r.state = ACTIVE
                r.last_idx = i
                self._ev(i, "Merge", 0, r, r.break_idx)
                return
        r = Range(id=len(self.ranges), start=cnd["start"], birth=i, top=cnd["top"], bottom=cnd["bot"],
                  top0=cnd["top"], bottom0=cnd["bot"], tol=cnd["tol"], mbr=cnd["mbr"],
                  top_m=list(cnd["tm"]), bot_m=list(cnd["bm"]), last_idx=i)
        self.ranges.append(r)
        self.live.append(r)
        self._ev(i, "Birth", 0, r)


def load_bars(path):
    """Đọc *_bars.csv → list (datetime_str, o, h, l, c)."""
    out = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        rd = csv.reader(f)
        hdr = next(rd)
        ix = {n: k for k, n in enumerate(hdr)}
        io, ih, il, ic, it = ix["open"], ix["high"], ix["low"], ix["close"], ix["datetime"]
        for row in rd:
            out.append((row[it], float(row[io]), float(row[ih]), float(row[il]), float(row[ic])))
    return out


def run(bars, p: Params, tick=0.1):
    e = RangeEngine(p, tick)
    for (_, o, h, l, c) in bars:
        e.feed(o, h, l, c)
    return e


def write_events(path, eng: RangeEngine, bars, offset=0):
    t = eng.tick
    side = {1: "top", -1: "bottom", 0: ""}
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["bar_idx", "datetime", "type", "side", "top", "bottom", "start_idx", "ref_idx", "range_id"])
        for ev in eng.events:
            w.writerow([ev.bar + offset, bars[ev.bar][0], ev.kind, side[ev.side],
                        f"{ev.top * t:.4f}", f"{ev.bottom * t:.4f}", ev.start + offset, ev.ref + offset, ev.rid])


if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    bars = load_bars(path)
    eng = run(bars, Params())
    print(len(bars), "nến;", len(eng.ranges), "range;", len(eng.events), "sự kiện")
