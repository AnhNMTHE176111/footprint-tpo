# -*- coding: utf-8 -*-
"""
of_signals.py — các dấu hiệu order flow cho setup CORVEN (plans/BENZO-CORVEN-plan.md mục 1.③, mục 2).

Hai phần:
  (1) PORT Y CHỮ từ C# (phải khớp 100 % — kiểm bằng parity_of_signals.py + tools/OfSignalsDump):
      * StackedImbalanceCalc  (quantower-orderflow-indicator/StackedImbalance.cs):
            detect_stacked, is_imb, locate, classify, check_end, follow
      * ExhaustionLogic       (quantower-orderflow-indicator/ExhaustionLogic.cs):
            ExhSettings, ExhResult, mean_level_volume, detect_exhaustion, is_swept
  (2) MỚI theo plan (chưa có C#, sẽ port sang BenzoOrderFlow.cs ở GĐ3):
      * nền_ô  (cell_value / CellBaseline) — trung vị 100 nến của (trung vị 3 ô side-volume lớn nhất mỗi nến)
      * bóng   (bubbles)       — ô side-volume phía S ≥ 3 × nền_ô VÀ ≥ 10 hợp đồng
      * delta  (delta_strong, delta_divergence)
      * trap   (trap)

Quy ước: giá → số tick nguyên bằng round(giá / tick) (banker's rounding, = Math.Round của C#).
Một "mức" (level) của nến = tuple (tick, bid, ask, volume); bid = sell chủ động khớp ở Bid, ask = buy chủ động khớp ở Ask.
Mọi hàm ở đây THUẦN: không đọc file, không nhìn tương lai — người gọi tự đưa đúng các nến đã đóng.
"""
from __future__ import annotations

import bisect
import math
from collections import deque
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

TICK = 0.1
EPS = 1e-9

Level = Tuple[int, float, float, float]      # (tick, bid, ask, volume)


# =====================================================================================================
# (1a) PORT StackedImbalanceCalc
# =====================================================================================================
POS_BODY, POS_UPPER, POS_LOWER = 0, 1, 2                       # SiPosition
END_ACTIVE, END_TOUCHED, END_CLOSED, END_EXPIRED = 0, 1, 2, 3  # SiEnd
MODE_TOUCH, MODE_CLOSE = 0, 1                                  # SiEndMode


@dataclass
class SiZone:
    side: int              # +1 buy, −1 sell
    lo_idx: int            # chỉ số mức trong mảng của nến (0 = mức thấp nhất)
    hi_idx: int
    lo: float              # giá mức imbalance thấp nhất / cao nhất
    hi: float
    levels: int
    min_ratio: float       # tỷ lệ chéo yếu nhất (inf nếu mọi mức bên kia = 0)
    dom_volume: float
    opp_volume: float
    position: int = POS_BODY
    weak: bool = False


def is_imb(dominant: float, opposite: float, ratio: float, min_volume: float) -> bool:
    return dominant > 0 and dominant >= min_volume and dominant >= ratio * opposite - EPS


def _make_zone(side, s, e, low_price, tick, ask, bid) -> SiZone:
    min_r, dom, opp = math.inf, 0.0, 0.0
    for i in range(s, e + 1):
        d = ask[i] if side > 0 else bid[i]
        o = bid[i - 1] if side > 0 else ask[i + 1]
        dom += d
        opp += o
        if o > 0:
            min_r = min(min_r, d / o)
    return SiZone(side=side, lo_idx=s, hi_idx=e,
                  lo=round((low_price + s * tick) / tick) * tick,
                  hi=round((low_price + e * tick) / tick) * tick,
                  levels=e - s + 1, min_ratio=min_r, dom_volume=dom, opp_volume=opp)


def _collect(res, f, side, run, low_price, tick, ask, bid):
    n, s = len(f), -1
    for i in range(n + 1):
        on = i < n and f[i]
        if on and s < 0:
            s = i
        if not on and s >= 0:
            e = i - 1
            if e - s + 1 >= run:
                res.append(_make_zone(side, s, e, low_price, tick, ask, bid))
            s = -1


def detect_stacked(low_price: float, tick: float, ask: Sequence[float], bid: Sequence[float],
                   ratio_pct: float, min_run: int, min_volume: float) -> List[SiZone]:
    """= StackedImbalanceCalc.Detect. ask[i]/bid[i]: các mức LIÊN TIẾP từng tick từ Low lên High (mức trống = 0).
    Trả vùng buy trước rồi vùng sell (đúng thứ tự C#)."""
    res: List[SiZone] = []
    if ask is None or bid is None:
        return res
    n = min(len(ask), len(bid))
    if n < 2 or tick <= 0:
        return res
    r = ratio_pct / 100.0
    run = max(1, min_run)
    mv = max(min_volume, 0)
    buy = [False] * n
    sell = [False] * n
    for i in range(1, n):
        buy[i] = is_imb(ask[i], bid[i - 1], r, mv)
    for i in range(0, n - 1):
        sell[i] = is_imb(bid[i], ask[i + 1], r, mv)
    _collect(res, buy, +1, run, low_price, tick, ask, bid)
    _collect(res, sell, -1, run, low_price, tick, ask, bid)
    return res


def locate(lo: float, hi: float, open_: float, close: float) -> int:
    mid = (lo + hi) / 2.0
    top, bot = max(open_, close), min(open_, close)
    if mid > top + EPS:
        return POS_UPPER
    if mid < bot - EPS:
        return POS_LOWER
    return POS_BODY


def classify(z: SiZone, open_: float, close: float) -> None:
    z.position = locate(z.lo, z.hi, open_, close)
    z.weak = (z.side > 0 and z.position == POS_UPPER) or (z.side < 0 and z.position == POS_LOWER)


def check_end(side: int, lo: float, hi: float, high: float, low: float, close: float, mode: int) -> int:
    through = close < lo - EPS if side > 0 else close > hi + EPS
    if mode == MODE_TOUCH:
        if through:
            return END_CLOSED
        if high >= lo - EPS and low <= hi + EPS:
            return END_TOUCHED
        return END_ACTIVE
    return END_CLOSED if through else END_ACTIVE


def follow(side: int, lo: float, hi: float, after: Sequence[Tuple[float, float, float]], mode: int,
           max_bars: int) -> Tuple[int, int]:
    """= StackedImbalanceCalc.Follow. after = [(high, low, close)] các nến SAU nến tạo vùng.
    Trả (offset nến kết thúc tính từ 1, lý do); (-1, END_ACTIVE) nếu chưa kết thúc."""
    for j, (h, l, c) in enumerate(after):
        off = j + 1
        e = check_end(side, lo, hi, h, l, c, mode)
        if e != END_ACTIVE:
            return off, e
        if max_bars > 0 and off >= max_bars:
            return off, END_EXPIRED
    return -1, END_ACTIVE


# =====================================================================================================
# (1b) PORT ExhaustionLogic
# =====================================================================================================
EXH_NONE, EXH_SMALL, EXH_FADE = 0, 1, 2


@dataclass
class ExhSettings:
    small_rel: float = 0.10
    fade_levels: int = 3
    fade_end_rel: float = 0.25
    require_wick: bool = True


@dataclass
class ExhResult:
    kind: int
    top: bool
    tick: int
    extreme_vol: float
    mean_level_vol: float
    seq: tuple = ()

    @property
    def hit(self) -> bool:
        return self.kind != EXH_NONE


def mean_level_volume(levels: Sequence[Level]) -> float:
    s, cnt = 0.0, 0
    if levels:
        for l in levels:
            if l[3] > 0:
                s += l[3]
                cnt += 1
    return s / cnt if cnt > 0 else 0.0


def detect_exhaustion(top: bool, open_t: int, high_t: int, low_t: int, close_t: int,
                      levels: Sequence[Level], s: Optional[ExhSettings]) -> ExhResult:
    """= ExhaustionLogic.Detect. Các giá là SỐ TICK nguyên."""
    ext = high_t if top else low_t
    none = ExhResult(EXH_NONE, top, ext, 0.0, 0.0, ())
    if s is None or not levels or high_t <= low_t:
        return none
    body_edge = max(open_t, close_t) if top else min(open_t, close_t)
    wick = high_t - body_edge if top else body_edge - low_t
    if s.require_wick and wick < 1:
        return none
    by_tick = {}
    for l in levels:
        by_tick[l[0]] = l
    mean = mean_level_volume(levels)
    step = -1 if top else 1
    span = (high_t - low_t) + 1
    want = min(max(1, s.fade_levels), span)
    from_ext = []
    for j in range(want):
        l = by_tick.get(ext + step * j)
        if l is None:
            from_ext.append(0.0)
        else:
            from_ext.append(float(l[2] if top else l[1]))
    ext_vol = from_ext[0]
    in_wick = min(want, wick if s.require_wick else want)
    if in_wick < 1:
        in_wick = 1
    seq = tuple(from_ext[in_wick - 1 - j] for j in range(in_wick))
    if ext_vol <= s.small_rel * mean + 1e-9:
        return ExhResult(EXH_SMALL, top, ext, ext_vol, mean, seq)
    n = s.fade_levels
    if n >= 2 and span >= n and (not s.require_wick or wick >= n):
        strictly = True
        for j in range(n - 1):
            if not (from_ext[j] < from_ext[j + 1]):
                strictly = False
                break
        if strictly and ext_vol <= s.fade_end_rel * mean + 1e-9:
            return ExhResult(EXH_FADE, top, ext, ext_vol, mean, seq)
    return none


def is_swept(top: bool, level_tick: int, later_high_t: int, later_low_t: int, sweep_ticks: int) -> bool:
    t = max(0, sweep_ticks)
    return later_high_t >= level_tick + t if top else later_low_t <= level_tick - t


# =====================================================================================================
# Tiện ích một nến footprint
# =====================================================================================================
@dataclass
class FpBar:
    """Một nến M1 đã đóng + các mức giá. o/h/l/c là SỐ TICK; levels sắp theo tick tăng dần."""
    idx: int
    o: int
    h: int
    l: int
    c: int
    delta: float = 0.0
    max_delta: float = 0.0
    min_delta: float = 0.0
    levels: List[Level] = field(default_factory=list)
    tick: float = TICK


def ladder(bar: FpBar) -> Tuple[List[float], List[float]]:
    """Mảng ask/bid liên tiếp từ Low lên High (mức trống = 0), như OrderFlowBubbles dựng cho Detect."""
    n = bar.h - bar.l + 1
    ask = [0.0] * max(n, 0)
    bid = [0.0] * max(n, 0)
    for (k, b, a, _v) in bar.levels:
        if bar.l <= k <= bar.h:
            ask[k - bar.l] += a
            bid[k - bar.l] += b
    return ask, bid


def stacked_zones(bar: FpBar, ratio_pct: float = 250, run: int = 3, min_vol: float = 1) -> List[SiZone]:
    """Vùng stacked của nến (đã Classify theo open/close)."""
    if bar.h <= bar.l:
        return []
    ask, bid = ladder(bar)
    t = bar.tick
    zs = detect_stacked(bar.l * t, t, ask, bid, ratio_pct, run, min_vol)
    for z in zs:
        classify(z, bar.o * t, bar.c * t)
    return zs


def exhaustion(bar: FpBar, s: Optional[ExhSettings] = None) -> Tuple[ExhResult, ExhResult]:
    """(kiệt sức đỉnh, kiệt sức đáy) với cấu hình mặc định ExhaustionLogic."""
    s = s or ExhSettings()
    return (detect_exhaustion(True, bar.o, bar.h, bar.l, bar.c, bar.levels, s),
            detect_exhaustion(False, bar.o, bar.h, bar.l, bar.c, bar.levels, s))


# =====================================================================================================
# (2) MỚI — nền_ô, bóng, delta, trap  (plan mục 1 "Ký hiệu", ③a, ③b, ③e)
# =====================================================================================================
def _median(a: Sequence[float]) -> float:
    s = sorted(a)
    n = len(s)
    if n == 0:
        return 0.0
    return float(s[n // 2]) if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def cell_value(bar: FpBar, top_n: int = 3) -> Optional[float]:
    """Giá trị nạp nền_ô của MỘT nến = trung vị của top_n ô side-volume lớn nhất (side-volume = max(bid, ask)).
    Nến không có ô nào có volume ⇒ None (không nạp)."""
    sv = [max(b, a) for (_k, b, a, v) in bar.levels if (b > 0 or a > 0)]
    if not sv:
        return None
    sv.sort(reverse=True)
    return _median(sv[:top_n])


class CellBaseline:
    """Trung vị cuốn chiếu của cell_value trên `window` nến gần nhất (nến không có ô bị bỏ qua, không chiếm chỗ).
    Cách dùng (mặc định của plan, xem report CORVEN-GD0 mục 'nền_ô'): gọi value() TRƯỚC push(bar) ⇒ nền KHÔNG gồm nến
    hiện tại (như OrderFlowBubbles: 'tính tín hiệu bằng baseline TRƯỚC bar rồi mới nạp')."""

    def __init__(self, window: int = 100, top_n: int = 3):
        self.window = window
        self.top_n = top_n
        self.q: deque = deque()
        self.sorted: List[float] = []

    def push(self, bar: FpBar) -> None:
        v = cell_value(bar, self.top_n)
        if v is None:
            return
        self.q.append(v)
        bisect.insort(self.sorted, v)
        if len(self.q) > self.window:
            old = self.q.popleft()
            del self.sorted[bisect.bisect_left(self.sorted, old)]

    def ready(self) -> bool:
        return len(self.q) >= self.window

    def value(self) -> float:
        return _median(self.sorted)


def bubbles(bar: FpBar, side: int, base: float, mult: float = 3.0, min_contracts: float = 10.0) -> List[Tuple[int, float]]:
    """③b — các ô 'bóng' phía `side` (+1: ask/buy chủ động, −1: bid/sell chủ động):
    side-volume ≥ mult × nền_ô VÀ ≥ min_contracts. Trả [(tick, volume)] theo tick tăng dần.
    Lọc vị trí (nửa nến phía S / dải mốc ± tol) do setup làm — xem bubble_in_place()."""
    thr = max(mult * base, min_contracts)
    out = []
    for (k, b, a, _v) in bar.levels:
        x = a if side > 0 else b
        if x > 0 and x >= thr - EPS:
            out.append((k, float(x)))
    return out


def bubble_in_place(bar: FpBar, side: int, cell_tick: int, band: Optional[Tuple[float, float]] = None) -> bool:
    """Ô bóng nằm ở nửa nến phía S (buy: ô ≤ trung điểm nến; sell: ô ≥ trung điểm) HOẶC trong dải mốc [lo, hi] (tick)."""
    mid = (bar.h + bar.l) / 2.0
    half_ok = cell_tick <= mid + EPS if side > 0 else cell_tick >= mid - EPS
    band_ok = band is not None and band[0] - EPS <= cell_tick <= band[1] + EPS
    return half_ok or band_ok


def delta_strong(bar: FpBar, side: int, med_abs_delta: float, mult: float = 2.0, straight: float = 0.8) -> bool:
    """③a dạng 1 — delta đồng thuận, to-thẳng: Δ·S > 0, |Δ| ≥ mult × medΔ, và 'thẳng':
    buy: delta ≥ straight × max_delta ; sell: delta ≤ straight × min_delta.
    ⚠️ Trong file export lịch sử max_delta = min_delta = delta ở ~100 % nến ⇒ điều kiện 'thẳng' luôn đúng
    (xem report CORVEN-GD0, điểm cần Fable quyết)."""
    d = bar.delta
    if d * side <= 0 or med_abs_delta <= 0:
        return False
    if abs(d) < mult * med_abs_delta - EPS:
        return False
    if side > 0:
        return d >= straight * bar.max_delta - EPS
    return d <= straight * bar.min_delta + EPS


def delta_divergence(H: Sequence[int], L: Sequence[int], D: Sequence[float], x: int, side: int, mbr_ticks: float,
                     min_len: int = 2, max_len: int = 8, amp_mbr: float = 1.0):
    """③a dạng 2 — delta ngược giá. Hướng vào `side`; nhịp test đi NGƯỢC side (sell: giá lên).
    Cơ khí hoá (Opus, chờ Fable duyệt): nến neo x là cực trị của nhịp (sell: H[x] = max H của nhịp);
    điểm xuất phát s = nến có đáy thấp nhất (sell) trong [x−max_len, x−min_len] (hoà ⇒ lấy nến MUỘN nhất);
    nhịp = các nến s+1..x (số nến = x − s ∈ [min_len, max_len]); biên độ = H[x] − L[s] ≥ amp_mbr × mbr;
    ΣΔ(s+1..x) có dấu ngược chiều giá (sell: ≤ 0; buy: ≥ 0). Trả (ok, s, ΣΔ) hoặc (False, -1, 0)."""
    lo = x - max_len
    hi = x - min_len
    if lo < 0:
        lo = 0
    if hi < lo:
        return False, -1, 0.0
    if side < 0:          # sell: nhịp lên
        s = min(range(lo, hi + 1), key=lambda j: (L[j], -j))
        if max(H[s:x + 1]) != H[x]:
            return False, -1, 0.0
        amp = H[x] - L[s]
    else:                 # buy: nhịp xuống
        s = min(range(lo, hi + 1), key=lambda j: (-H[j], -j))
        if min(L[s:x + 1]) != L[x]:
            return False, -1, 0.0
        amp = H[s] - L[x]
    if amp < amp_mbr * mbr_ticks - EPS:
        return False, -1, 0.0
    sd = float(sum(D[s + 1:x + 1]))
    ok = sd <= 0 if side < 0 else sd >= 0
    return ok, s, sd


def trap(bar: FpBar, side: int, level_tick: int, base: float, mult: float = 3.0, sweep_ticks: int = 1,
         min_contracts: float = 0.0):
    """③e — trap / stop hunt phe ngược tại mốc quan trọng `level_tick`. Hướng vào `side`.
    sell: râu trên quét qua mốc ≥ sweep_ticks (H ≥ mốc + 1) và đóng lại dưới mốc (C < mốc), và trong phần râu
          TRÊN (tick > max(O, C)) có ô ASK (phía −S) ≥ mult × nền_ô và ≥ min_contracts (Q10: setup dùng 10).
    buy : đối xứng (L ≤ mốc − 1, C > mốc, râu dưới có ô BID ≥ mult × nền_ô).
    Trả (ok, tick ô, volume ô lớn nhất trong râu) — ok False ⇒ (False, -1, 0)."""
    if side < 0:
        if not (bar.h >= level_tick + sweep_ticks and bar.c < level_tick):
            return False, -1, 0.0
        edge = max(bar.o, bar.c)
        cells = [(k, a) for (k, b, a, v) in bar.levels if k > edge]
    else:
        if not (bar.l <= level_tick - sweep_ticks and bar.c > level_tick):
            return False, -1, 0.0
        edge = min(bar.o, bar.c)
        cells = [(k, b) for (k, b, a, v) in bar.levels if k < edge]
    if not cells or base <= 0:
        return False, -1, 0.0
    k, v = max(cells, key=lambda t: (t[1], -t[0] if side < 0 else t[0]))
    if v >= mult * base - EPS and v >= min_contracts - EPS and v > 0:
        return True, k, float(v)
    return False, -1, 0.0
