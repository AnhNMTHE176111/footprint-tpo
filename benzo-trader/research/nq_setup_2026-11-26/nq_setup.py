# -*- coding: utf-8 -*-
"""
nq_setup.py — bản Python THAM CHIẾU của chuẩn setup CORVEN cho NQ M1 (SPEC-SETUP-NQ.md, chốt 2026-11-26).

Nguồn luật: chỉ lời CORVEN + quan sát chart CORVEN (THU-THAP-1/2). Số trong CFG có nhãn trong SPEC.
Đầu vào:
  - nến: data-export/data-footprint/fp_NQZ26_XCME_Time_*_bars.csv (UTC, datetime = giờ MỞ nến)
  - tín hiệu OrderFlowBubbles (C# thật, golden harness chế độ stophunt):
      marks.csv  (t,kind,price): dotB/dotS/bt/exhT/exhB/zoneB/zoneS
      sh.csv     (sweep_time,side,level,bid,ask,orig_side): stop hunt
      bt_side.csv (t,price,side): phía của vòng Big Trade (Ask > Bid → +1, ngược lại −1), trích từ file mức giá
Mọi quyết định tại nến i dùng nến ≤ i (nến đã đóng). Lệnh khớp ở Open[i+1].
"""
from __future__ import annotations

import csv
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "quantower-range", "research"))
import range_proto as rp  # noqa: E402

NY = ZoneInfo("America/New_York")
TICK = 0.25

CFG = dict(
    W=3,                 # cửa sổ phản ứng [i-2, i]                       (luật 11–13, số agent chọn)
    ZONE_MAX_AGE=30,     # vùng stacked "gần" ≤ 30 nến                      (7d-2)
    ZONE_BODY=0.5,       # ≥ 50 % vùng nằm trong thân nến sinh              (7b)
    DELTA_K=1.0,         # |delta| ≥ 1,0 × TB |delta| 20 nến trước          (15)
    DELTA_N=20,
    EXH_BLOCK=5,         # kiệt sức ngược phe trong 5 nến chưa bị quét      (17)
    RETRY_LOOK=30,       # "xác nhận lần 2": lần thò trước trong 30 nến     (18)
    SH_POKE_BUB=0.75,    # bóng trong 0,75 điểm quanh cạnh                  (16b)
    SL_PAD=2.0,          # SL sau mốc + 2 điểm                              (20)
    SL_MIN=5.0,          # sàn 5 điểm
    SL_MAX_MBR=3.0,      # > 3 × mbr thì bỏ lệnh
    RR_TP=2.0,           # TP 2R                                            (21)
    RR_FB_ROOM=1.7,      # Fail Break: ≥ 1,7R tới cạnh đối diện
    BIAS_WARM=30,        # 30 nến đầu phiên chưa có bias                    (8)
    BIG_NEAR=10.0,       # nhãn mốc lớn ≤ 10 điểm                           (9)
    COST=1.0,            # chi phí điểm/lệnh khứ hồi                        (4.3)
    NO_ENTRY_NY=(16, 45),
    CLOSE_NY=(16, 59),
    USE_D=True,          # False = đối chứng "bỏ tầng D" (luật 15–18)
    USE_BIAS=True,       # False = cột phụ "không lọc bias"
    FAIL_BREAK=False,    # 2026-11-26 người học: "bỏ fail break, chỉ đánh break cấu trúc và follow trend" (bản 2)
)


# ------------------------------------------------------------------ nạp dữ liệu
@dataclass
class Bars:
    t: list = field(default_factory=list)      # datetime UTC (giờ mở nến)
    key: list = field(default_factory=list)    # "YYYY-MM-DD HH:MM"
    o: list = field(default_factory=list)
    h: list = field(default_factory=list)
    l: list = field(default_factory=list)
    c: list = field(default_factory=list)
    d: list = field(default_factory=list)      # delta
    v: list = field(default_factory=list)
    idx: list = field(default_factory=list)    # bar_idx gốc của file


def load_bars(path, start_utc: datetime) -> Bars:
    b = Bars()
    with open(path, newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        for r in rd:
            t = datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            if t < start_utc:
                continue
            b.t.append(t); b.key.append(r["datetime"][:16]); b.idx.append(int(r["bar_idx"]))
            b.o.append(float(r["open"])); b.h.append(float(r["high"])); b.l.append(float(r["low"])); b.c.append(float(r["close"]))
            b.d.append(float(r["delta"])); b.v.append(float(r["volume"]))
    return b


@dataclass
class Sig:
    dotB: dict = field(default_factory=lambda: defaultdict(list))   # i -> [giá]
    dotS: dict = field(default_factory=lambda: defaultdict(list))
    bt: dict = field(default_factory=lambda: defaultdict(list))     # i -> [(giá, phía)]
    exhT: set = field(default_factory=set)
    exhB: set = field(default_factory=set)
    zones: dict = field(default_factory=lambda: defaultdict(list))  # i -> [(phía, lo, hi)]
    sh: dict = field(default_factory=lambda: defaultdict(set))      # i -> {(phía, level)}


def load_signals(bars: Bars, marks, shf, btside) -> Sig:
    pos = {k: i for i, k in enumerate(bars.key)}
    s = Sig()
    side_of = {}
    if btside and os.path.exists(btside):
        with open(btside, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                side_of[(r["t"], round(float(r["price"]) / TICK))] = int(r["side"])
    with open(marks, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            i = pos.get(r["t"])
            if i is None:
                continue
            k = r["kind"]
            if k == "dotB":
                s.dotB[i].append(float(r["price"]))
            elif k == "dotS":
                s.dotS[i].append(float(r["price"]))
            elif k == "bt":
                p = float(r["price"])
                sd = side_of.get((r["t"], round(p / TICK)))
                if sd is None:
                    raise RuntimeError("thiếu phía Big Trade " + r["t"] + " " + r["price"])
                s.bt[i].append((p, sd))
            elif k == "exhT":
                s.exhT.add(i)
            elif k == "exhB":
                s.exhB.add(i)
            elif k in ("zoneB", "zoneS"):
                lo, hi = r["price"].split("-")
                s.zones[i].append((1 if k == "zoneB" else -1, float(lo), float(hi)))
    with open(shf, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            i = pos.get(r["sweep_time"])
            if i is None:
                continue
            s.sh[i].add((-1 if r["side"] == "day" else 1, float(r["level"])))   # day = quét đáy (buy), dinh = quét đỉnh (sell)
    return s


# ------------------------------------------------------------------ giờ / phiên
def ny(t):
    return t.astimezone(NY)


def session_of(t):
    """Á 18:00–03:00, Âu 03:00–09:30, Mỹ 09:30–17:00 (giờ New York). Trả (tên, khoá phiên)."""
    n = ny(t)
    m = n.hour * 60 + n.minute
    if m >= 18 * 60:
        return "A", (n.date() + timedelta(days=1), "A")
    if m < 3 * 60:
        return "A", (n.date(), "A")
    if m < 9 * 60 + 30:
        return "E", (n.date(), "E")
    return "U", (n.date(), "U")


def trade_day(t):
    """Ngày giao dịch CME: bắt đầu 18:00 NY."""
    n = ny(t)
    return n.date() + timedelta(days=1) if n.hour >= 18 else n.date()


# ------------------------------------------------------------------ bối cảnh mốc lớn (chỉ gắn nhãn, luật 9)
class BigLevels:
    """VWAP ngày (neo 18:00 NY), VWAP tuần (neo 18:00 NY Chủ nhật), POC TPO hôm trước / tuần trước (TPO 30', hàng 2 điểm)."""
    ROW = 2.0

    def __init__(self):
        self.day = None; self.week = None
        self.vd = [0.0, 0.0]; self.vw = [0.0, 0.0]
        self.tpo_day = defaultdict(set); self.tpo_week = defaultdict(set)
        self.poc_prev_day = None; self.poc_prev_week = None
        self.left_day = False; self.left_week = False

    @staticmethod
    def _poc(tpo):
        if not tpo:
            return None
        cnt = {r: len(p) for r, p in tpo.items()}
        mx = max(cnt.values())
        rows = sorted(cnt)
        mid = (rows[0] + rows[-1]) / 2.0
        best = min((r for r in rows if cnt[r] == mx), key=lambda r: (abs(r - mid), r))
        return (best + 0.5) * BigLevels.ROW

    def update(self, t, h, l, c, v):
        td = trade_day(t)
        wk = td.isocalendar()[:2]
        if td != self.day:
            if self.day is not None:
                self.poc_prev_day = self._poc(self.tpo_day)
            self.day = td; self.vd = [0.0, 0.0]; self.tpo_day = defaultdict(set); self.left_day = False
        if wk != self.week:
            if self.week is not None:
                self.poc_prev_week = self._poc(self.tpo_week)
            self.week = wk; self.vw = [0.0, 0.0]; self.tpo_week = defaultdict(set); self.left_week = False
        tp = (h + l + c) / 3.0
        self.vd[0] += tp * v; self.vd[1] += v; self.vw[0] += tp * v; self.vw[1] += v
        n = ny(t)
        per = (n.date(), n.hour, n.minute // 30)
        for r in range(int(l // self.ROW), int(h // self.ROW) + 1):
            self.tpo_day[r].add(per); self.tpo_week[r].add(per)
        if self.poc_prev_day is not None and not (l <= self.poc_prev_day <= h):
            self.left_day = True
        if self.poc_prev_week is not None and not (l <= self.poc_prev_week <= h):
            self.left_week = True

    def label(self, price, near):
        wk = []; dy = []
        if self.vw[1] > 0 and abs(price - self.vw[0] / self.vw[1]) <= near:
            wk.append("VWAP tuần")
        if self.poc_prev_week is not None and self.left_week and abs(price - self.poc_prev_week) <= near:
            wk.append("POC tuần trước")
        if self.vd[1] > 0 and abs(price - self.vd[0] / self.vd[1]) <= near:
            dy.append("VWAP ngày")
        if self.poc_prev_day is not None and self.left_day and abs(price - self.poc_prev_day) <= near:
            dy.append("POC hôm trước")
        if wk:
            return "kịch bản 1", "+".join(wk + dy)
        if dy:
            return "kịch bản 2.1", "+".join(dy)
        return "kịch bản 2.2", ""


# ------------------------------------------------------------------ máy chính
@dataclass
class Zone:
    side: int
    lo: float
    hi: float
    birth: int
    ok_at: int = -1        # nến mà vùng đạt 7b (birth hoặc birth+1)
    ready_at: int = -1     # nến đầu tiên nằm hẳn ngoài vùng (7c)
    touch: int = -1        # nến chạm lần đầu
    dead: bool = False
    used: bool = False


@dataclass
class Trade:
    sig: int
    kind: str              # Fail Break / Break / Test vùng stacked
    side: int
    entry: float
    sl: float
    tp: float
    dist: float
    second: str            # tín hiệu thứ hai
    bias: str
    big: str
    big_lv: str
    session: str
    exit_i: int = -1
    exit_px: float = 0.0
    how: str = ""
    r: float = 0.0
    r_gross: float = 0.0
    r4: float = 0.0        # cột phụ TP 4R
    note: str = ""
    edge: float = 0.0      # mép xa của mốc (cạnh range / mép vùng)
    room: float = 0.0      # cạnh đối diện (Fail Break), 0 nếu không có
    touch: int = -1        # nến chạm mốc


class Machine:
    def __init__(self, bars: Bars, sig: Sig, cfg=None):
        self.b = bars; self.s = sig; self.cfg = dict(CFG); self.cfg.update(cfg or {})
        self.eng = rp.RangeEngine(rp.Params(), TICK)
        self.ph = []; self.pl = []          # pivot cấu trúc (giá)
        self.dir = []                        # hướng cấu trúc sau nến i (+1/-1/0)
        self.zones: list[Zone] = []
        self.big = BigLevels()
        self.sess_key = None; self.sess_start = 0; self.sess_open = 0.0; self.cumd = 0.0
        self.bias = []                       # +1/-1/0 sau nến i
        self.trades: list[Trade] = []
        self.cands = []                      # ứng viên đủ mốc + lý do bị loại
        self.open_until = -1                 # nến thoát của lệnh đang mở
        self.snap = []                       # ảnh range sau nến i

    # ---------- tầng A: cấu trúc
    def _structure(self, i):
        b = self.b
        d = self.dir[-1] if self.dir else 0
        if i >= 2:
            j = i - 1
            newp = False
            if b.h[j] > b.h[j - 1] and b.h[j] >= b.h[i]:
                self.ph.append(b.h[j]); newp = True
            if b.l[j] < b.l[j - 1] and b.l[j] <= b.l[i]:
                self.pl.append(b.l[j]); newp = True
            if newp and len(self.ph) >= 2 and len(self.pl) >= 2:
                if self.ph[-1] > self.ph[-2] and self.pl[-1] > self.pl[-2]:
                    d = 1
                elif self.ph[-1] < self.ph[-2] and self.pl[-1] < self.pl[-2]:
                    d = -1
            if self.ph and b.c[i] > self.ph[-1]:
                d = 1
            elif self.pl and b.c[i] < self.pl[-1]:
                d = -1
            if len(self.ph) > 50: self.ph = self.ph[-10:]
            if len(self.pl) > 50: self.pl = self.pl[-10:]
        self.dir.append(d)

    # ---------- bias phiên (luật 8)
    def _bias(self, i):
        b = self.b
        _, key = session_of(b.t[i])
        if key != self.sess_key or (i > 0 and (b.t[i] - b.t[i - 1]) > timedelta(minutes=30)):
            self.sess_key = key; self.sess_start = i; self.sess_open = b.o[i]; self.cumd = 0.0
        self.cumd += b.d[i]
        v = 0
        if i - self.sess_start + 1 > self.cfg["BIAS_WARM"]:
            dp = b.c[i] - self.sess_open
            if self.cumd > 0 and dp > 0:
                v = 1
            elif self.cumd < 0 and dp < 0:
                v = -1
        self.bias.append(v)

    # ---------- vùng stacked (7a–7d)
    def _zones(self, i):
        b = self.b; cfg = self.cfg
        for (sd, lo, hi) in self.s.zones.get(i, []):
            z = Zone(sd, lo, hi, i)
            bl, bh = min(b.o[i], b.c[i]), max(b.o[i], b.c[i])
            ov = max(0.0, min(hi, bh) - max(lo, bl))
            hgt = hi - lo
            inside = (ov >= cfg["ZONE_BODY"] * hgt - 1e-9) if hgt > 0 else (bl <= lo <= bh)
            if inside:
                z.ok_at = i
            self.zones.append(z)
        for z in self.zones:
            if z.dead or z.birth == i:
                continue
            # 7b nhánh "nến kế đi tiếp"
            if z.ok_at < 0:
                if i == z.birth + 1 and ((z.side > 0 and b.c[i] > z.hi) or (z.side < 0 and b.c[i] < z.lo)):
                    z.ok_at = i
                else:
                    z.dead = True; continue
            # 7d-1 đóng qua mép xa
            if (z.side > 0 and b.c[i] < z.lo) or (z.side < 0 and b.c[i] > z.hi):
                z.dead = True; continue
            # 7d-2 tuổi
            if i - z.birth > cfg["ZONE_MAX_AGE"]:
                z.dead = True; continue
            # 7d-3 cấu trúc khác hướng vùng (từ lúc sinh)
            if self.dir[i] != z.side:
                z.dead = True; continue
            # 7c rời vùng → sẵn sàng; rồi lần chạm đầu
            if z.ready_at < 0:
                if i >= z.ok_at and ((z.side > 0 and b.l[i] > z.hi) or (z.side < 0 and b.h[i] < z.lo)):
                    z.ready_at = i
            elif z.touch < 0:
                if (z.side > 0 and b.l[i] <= z.hi) or (z.side < 0 and b.h[i] >= z.lo):
                    z.touch = i
            # 7d-4 hết lần test đầu
            if z.touch >= 0 and i > z.touch + cfg["W"] - 1:
                z.dead = True
        # 7d-3 tại chính nến sinh
        for z in self.zones:
            if z.birth == i and self.dir[i] != z.side:
                z.dead = True
        if len(self.zones) > 400:
            self.zones = [z for z in self.zones if not z.dead]

    # ---------- tín hiệu order flow
    def _bubble_side(self, i, side):
        if side > 0:
            return bool(self.s.dotB.get(i)) or any(sd > 0 for _, sd in self.s.bt.get(i, []))
        return bool(self.s.dotS.get(i)) or any(sd < 0 for _, sd in self.s.bt.get(i, []))

    def _any_bubble_prices(self, i):
        return list(self.s.dotB.get(i, [])) + list(self.s.dotS.get(i, [])) + [p for p, _ in self.s.bt.get(i, [])]

    def _exh_valid(self, m, i, side):
        """kiệt sức đáy (side +1) / đỉnh (−1) ở nến m còn hiệu lực tới i: chưa nến nào sau m quét qua cực trị (râu)."""
        b = self.b
        if side > 0:
            return all(b.l[k] >= b.l[m] for k in range(m + 1, i + 1))
        return all(b.h[k] <= b.h[m] for k in range(m + 1, i + 1))

    def _delta_ok(self, i, side):
        b = self.b; n = self.cfg["DELTA_N"]
        if i < n:
            return False
        avg = sum(abs(x) for x in b.d[i - n:i]) / n
        return (b.d[i] * side > 0) and abs(b.d[i]) >= self.cfg["DELTA_K"] * avg

    def _candle_ok(self, i, side):
        b = self.b
        rng = b.h[i] - b.l[i]
        if rng <= 0:
            return False
        if side > 0:
            return b.c[i] > b.o[i] and (b.c[i] - b.l[i]) / rng >= 0.5
        return b.c[i] < b.o[i] and (b.h[i] - b.c[i]) / rng >= 0.5

    def _second(self, i, side, edge=None, zone_test=False):
        """luật 16: trả danh sách tín hiệu thứ hai cùng phe."""
        b = self.b; s = self.s; cfg = self.cfg
        W = range(max(0, i - cfg["W"] + 1), i + 1)
        out = []
        # (a) kiệt sức cùng phe còn hiệu lực
        ex = s.exhB if side > 0 else s.exhT
        if any(m in ex and self._exh_valid(m, i, side) for m in W):
            out.append("kiệt sức")
        # (b) stop hunt
        shs = -1 if side > 0 else 1
        hit = False
        for m in W:
            for (sd, lv) in s.sh.get(m, ()):
                if sd == shs and ((side > 0 and b.c[i] > lv) or (side < 0 and b.c[i] < lv)):
                    hit = True
        if not hit and edge is not None:
            for m in W:
                if side > 0 and b.l[m] <= edge - TICK + 1e-9:
                    if any(p <= edge + cfg["SH_POKE_BUB"] + 1e-9 for p in self._any_bubble_prices(m)):
                        hit = True
                if side < 0 and b.h[m] >= edge + TICK - 1e-9:
                    if any(p >= edge - cfg["SH_POKE_BUB"] - 1e-9 for p in self._any_bubble_prices(m)):
                        hit = True
        if hit:
            out.append("stop hunt")
        # (c) stacked mới cùng phe, đạt 7b tới nến i
        for z in self.zones:
            if z.side == side and z.birth in W and z.ok_at >= 0 and z.ok_at <= i:
                out.append("stacked mới"); break
        if zone_test:
            out.append("vùng đang test")
        return out

    def _exh_block(self, i, side):
        """luật 17: buy bị chặn bởi kiệt sức ĐỈNH chưa bị quét trong 5 nến; sell bởi kiệt sức ĐÁY."""
        ex = self.s.exhT if side > 0 else self.s.exhB
        for m in range(max(0, i - self.cfg["EXH_BLOCK"] + 1), i + 1):
            if m in ex and self._exh_valid(m, i, -side):
                return True
        return False

    # ---------- mốc (tầng C)
    def _cands(self, i):
        """Trả list (kind, side, touch_bar, edge_far, room_edge, zone) cho nến i."""
        b = self.b; cfg = self.cfg; out = []
        W0 = max(0, i - cfg["W"] + 1)
        busy = [r for r in self.snap if r[1] in (rp.ACTIVE, rp.PENDING)]
        for (rid, st, top, bot, tol, bside) in self.snap:
            if st in (rp.ACTIVE, rp.PENDING) and cfg["FAIL_BREAK"]:
                # luật 11 Fail Break buy ở cạnh dưới / sell ở cạnh trên (+ luật 18)
                for side in (1, -1):
                    if side > 0:
                        tb = next((m for m in range(W0, i + 1) if b.l[m] <= bot + tol + 1e-9), -1)
                        inside = bot < b.c[i] < top
                    else:
                        tb = next((m for m in range(W0, i + 1) if b.h[m] >= top - tol - 1e-9), -1)
                        inside = bot < b.c[i] < top
                    if tb < 0:
                        continue
                    retry = False
                    if not inside:
                        retry = self._retry2(i, side, top, bot)
                        if not retry:
                            continue
                    edge = bot if side > 0 else top
                    room = top if side > 0 else bot
                    out.append(("Fail Break", side, tb, edge, room, None, "xác nhận lần 2" if retry else ""))
            elif st == rp.BROKEN and bside != 0:
                side = bside
                edge = top if side > 0 else bot
                if side > 0:
                    tb = next((m for m in range(W0, i + 1) if b.l[m] <= top + tol + 1e-9), -1)
                    ok = b.c[i] > top
                else:
                    tb = next((m for m in range(W0, i + 1) if b.h[m] >= bot - tol - 1e-9), -1)
                    ok = b.c[i] < bot
                if tb >= 0 and ok:
                    out.append(("Break", side, tb, edge, None, None, ""))
        if not busy:
            for z in self.zones:
                if z.dead or z.touch < 0 or z.used:
                    continue
                if not (z.touch <= i <= z.touch + cfg["W"] - 1):
                    continue
                if (z.side > 0 and b.c[i] >= z.hi) or (z.side < 0 and b.c[i] <= z.lo):
                    out.append(("Test vùng stacked", z.side, z.touch, z.lo if z.side > 0 else z.hi, None, z, ""))
        return out

    def _retry2(self, i, side, top, bot):
        """luật 18: lần thò trước (trong 30 nến trước W) + nến trong W tạo đáy thấp hơn và mang kiệt sức đáy còn hiệu lực."""
        b = self.b; cfg = self.cfg
        W0 = max(0, i - cfg["W"] + 1)
        lo0 = max(0, W0 - cfg["RETRY_LOOK"])
        prev = None
        for m in range(W0 - 1, lo0 - 1, -1):
            if side > 0 and b.l[m] <= bot - TICK + 1e-9:
                prev = b.l[m]; break
            if side < 0 and b.h[m] >= top + TICK - 1e-9:
                prev = b.h[m]; break
        if prev is None:
            return False
        ex = self.s.exhB if side > 0 else self.s.exhT
        for m in range(W0, i + 1):
            if side > 0 and b.l[m] < prev and m in ex and self._exh_valid(m, i, side):
                return True
            if side < 0 and b.h[m] > prev and m in ex and self._exh_valid(m, i, side):
                return True
        return False

    # ---------- chạy
    def run(self, count_from: datetime, until: datetime | None = None):
        b = self.b; cfg = self.cfg; n = len(b.t)
        for i in range(n):
            self.eng.feed(b.o[i], b.h[i], b.l[i], b.c[i])
            self.snap = [(r.id, r.state, r.top * TICK, r.bottom * TICK, r.tol * TICK, r.break_side) for r in sorted(self.eng.live, key=lambda r: r.id)]   # theo id (C# duyệt Ranges theo id)
            self._structure(i)
            self._bias(i)
            self._zones(i)
            self.big.update(b.t[i], b.h[i], b.l[i], b.c[i], b.v[i])
            if b.t[i] < count_from or (until is not None and b.t[i] >= until) or i + 1 >= n:
                continue
            for (kind, side, tb, edge, room, zone, note) in self._cands(i):
                self._consider(i, kind, side, tb, edge, room, zone, note)

    def _consider(self, i, kind, side, tb, edge, room, zone, note):
        b = self.b; cfg = self.cfg
        why = []
        if i < self.open_until:
            why.append("đang có lệnh")
        mbr = self.eng.mbr * TICK
        if kind != "Fail Break":
            if self.dir[i] != side:
                why.append("ngược cấu trúc")
            if cfg["USE_BIAS"] and self.bias[i] == -side:
                why.append("ngược bias")
        if not self._candle_ok(i, side):
            why.append("nến không đẹp")
        sec = []
        if cfg["USE_D"]:
            if not self._delta_ok(i, side):
                why.append("delta nhỏ/ngược")
            if not self._bubble_side(i, side):
                why.append("không bóng cùng phe")
            sec = self._second(i, side, edge if kind != "Test vùng stacked" else None, kind == "Test vùng stacked")
            if not sec:
                why.append("thiếu tín hiệu thứ hai")
            if self._exh_block(i, side):
                why.append("kiệt sức ngược phe")
        # giờ vào
        if (b.t[i + 1] - b.t[i]) > timedelta(minutes=5):
            why.append("nến kế sau khoảng trống")
        ne = ny(b.t[i + 1]); hm = (ne.hour, ne.minute)
        if cfg["NO_ENTRY_NY"] <= hm < (18, 0):
            why.append("sau 16:45 NY")
        entry = b.o[i + 1]
        lowest = min(b.l[tb:i + 1]) if side > 0 else max(b.h[tb:i + 1])
        if side > 0:
            sl = min(lowest, edge) - cfg["SL_PAD"]
            dist = entry - sl
        else:
            sl = max(lowest, edge) + cfg["SL_PAD"]
            dist = sl - entry
        if dist <= 0:
            why.append("giá vào đã qua SL")
        else:
            if dist < cfg["SL_MIN"]:
                dist = cfg["SL_MIN"]; sl = entry - side * dist
            if dist > cfg["SL_MAX_MBR"] * mbr:
                why.append("SL xa quá")
            if kind == "Fail Break" and room is not None and (room - entry) * side < cfg["RR_FB_ROOM"] * dist - 1e-9:
                why.append("không đủ 1,7R tới cạnh đối diện")
        self.cands.append((i, kind, side, ";".join(why), note))
        if why:
            return
        tp = entry + side * cfg["RR_TP"] * dist
        lab, lv = self.big.label(entry, cfg["BIG_NEAR"])
        sess, _ = session_of(b.t[i])
        t = Trade(i, kind, side, entry, sl, tp, dist, "+".join(sec), {1: "buy", -1: "sell", 0: "chưa có"}[self.bias[i]],
                  lab, lv, sess, note=note, edge=edge, room=room or 0.0, touch=tb)
        self._simulate(t)
        if zone is not None:
            zone.used = True
        self.trades.append(t)
        self.open_until = t.exit_i

    def _simulate(self, t: Trade, tp_rr=None):
        b = self.b; cfg = self.cfg
        res = simulate(b, t.sig + 1, t.side, t.entry, t.sl, t.tp, cfg)
        t.exit_i, t.exit_px, t.how = res
        pnl = (t.exit_px - t.entry) * t.side
        t.r_gross = pnl / t.dist
        t.r = (pnl - cfg["COST"]) / t.dist
        tp4 = t.entry + t.side * 4.0 * t.dist
        e4 = simulate(b, t.sig + 1, t.side, t.entry, t.sl, tp4, cfg)
        t.r4 = ((e4[1] - t.entry) * t.side - cfg["COST"]) / t.dist


def simulate(b: Bars, k0, side, entry, sl, tp, cfg):
    """Từ nến k0 (nến vào, khớp Open[k0]). Cùng nến chạm SL và TP → SL. Mở nhảy qua SL → khớp Open. Đóng 16:59 NY / trước khoảng trống."""
    n = len(b.t)
    for k in range(k0, n):
        o, h, l, c = b.o[k], b.h[k], b.l[k], b.c[k]
        if k > k0:
            if (side > 0 and o <= sl) or (side < 0 and o >= sl):
                return k, o, "SL"
            if (side > 0 and o >= tp) or (side < 0 and o <= tp):
                return k, tp, "TP"
        hit_sl = (l <= sl) if side > 0 else (h >= sl)
        hit_tp = (h >= tp) if side > 0 else (l <= tp)
        if hit_sl:
            return k, sl, "SL"
        if hit_tp:
            return k, tp, "TP"
        nk = ny(b.t[k])
        if (nk.hour, nk.minute) == cfg["CLOSE_NY"] or k + 1 >= n or (b.t[k + 1] - b.t[k]) > timedelta(minutes=30):
            return k, c, "TIME"
    return n - 1, b.c[-1], "TIME"


# ------------------------------------------------------------------ CLI
def default_paths():
    D = os.path.join(ROOT, "data-export", "data-footprint")
    S = os.environ.get("NQ_SIG_DIR", os.path.join(HERE, "signals"))
    return (os.path.join(D, "fp_NQZ26_XCME_Time_20260204-20261125_293d16h_bars.csv"),
            os.path.join(S, "marks.csv"), os.path.join(S, "sh.csv"), os.path.join(S, "bt_side.csv"))


def build(start=datetime(2026, 9, 14, tzinfo=timezone.utc), cfg=None):
    bp, mp, sp, btp = default_paths()
    bars = load_bars(bp, start)
    sig = load_signals(bars, mp, sp, btp)
    return bars, sig


if __name__ == "__main__":
    bars, sig = build()
    m = Machine(bars, sig)
    m.run(datetime(2026, 9, 14, tzinfo=timezone.utc))
    print(len(bars.t), "nến;", len(m.trades), "lệnh")
