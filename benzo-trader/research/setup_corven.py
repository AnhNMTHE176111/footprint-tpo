# -*- coding: utf-8 -*-
"""
setup_corven.py — setup "follow theo footprint" của CORVEN (plans/BENZO-CORVEN-plan.md).

GIAI ĐOẠN 0: chạy tới HẾT BƯỚC ② trên TRAIN (phiên ≤ 2026-09-15). KHÔNG đọc nến TEST: file nến được cắt tại nến cuối
TRAIN TRƯỚC khi đưa vào bất kỳ máy nào (chỉ đọc cột thời gian của toàn file để biết chỗ cắt).

  ① bối cảnh = range_proto.RangeEngine nguyên trạng (import, không copy, không đổi tham số)
     thế A = FailBreak (range về ACTIVE) ; thế B = BreakConfirmed, chưa ReEntry, tuổi ≤ 30 nến ; 1c cấu trúc thế B
  ② mốc "gần" (2a) + test không quá sâu (2b) + cửa sổ test (2c) ; ngoại lệ "xác nhận lần 2" của thế A (chỉ ĐẾM ứng viên —
     điều kiện ≥ 2 dấu hiệu thuộc ③, làm ở GĐ1)

Chạy:  PYTHONIOENCODING=utf-8 python setup_corven.py        → in tóm tắt + ghi report/_corven_gd0.json
Mọi giá trong máy trạng thái là SỐ TICK nguyên (như range_proto); mbr/tol cũng theo tick.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'quantower-range', 'research'))

import kernel as K                                    # noqa: E402
import of_signals as OF                               # noqa: E402
from range_proto import Params, RangeEngine, ACTIVE, PENDING, BROKEN, DEAD   # noqa: E402

D90 = os.path.join(ROOT, 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260723-20261021_90d')
REPORT = os.path.join(HERE, 'report')
TICK = 0.1


# =====================================================================================================
# THAM SỐ (plan mục 1–3). Chỉ những cái plan cho quét mới có tên ở đây; còn lại đóng băng.
# =====================================================================================================
@dataclass
class CP:
    near_mbr: float = 1.0          # 2a "gần" (quét {0,5; 1,0; 1,5})
    win_b: int = 3                 # 2c cửa sổ test thế B (quét {2,3,4})
    win_a_max: int = 5             # 2c thế A: từ nến đóng ngoài tới CF tối đa 5 nến
    cf_after_fb: int = 2           # thế A: CF = nến FailBreak hoặc 1–2 nến sau
    age_b: int = 30                # tuổi thế B / tuổi vùng stacked làm mốc
    si_ratio: float = 250.0
    si_run: int = 3                # (quét {3,4})
    si_minvol: float = 1.0
    b_from_exhausted: bool = True  # Q4: lập thế B cả khi BreakConfirmed làm range DEAD ngay (hết lượt ReEntry); cờ riêng, GĐ2 bật/tắt
    same_session: bool = True      # cửa sổ / CF không vắt qua khoảng trống phiên (> 30′)
    exc_max_age: int = 30          # Q12: "lần 2" trong ≤ 30 nến từ nến đóng ngoài
    a2_on: bool = False            # GĐ2 v1 (G1): ngoại lệ "lần 2" TẮT mặc định — chỉ còn là nhóm báo cáo trong Python
    a2_cf_after: int = 2           # G2: CF "lần 2" = x hoặc 1–2 nến sau x
    sl_anchor: str = 'cu_thung'    # GĐ2 v1 (7.3): 'cu_thung' = cực trị cú thủng / mốc (4b) ; 'pivot' = sau pivot 1 nến ngược S gần nhất
    piv_back: int = 10             # 7.3.3: tìm pivot trong [nến đóng ngoài − 10, CF]
    # ---- ③ ----
    delta_mult: float = 2.0        # ③a to (quét {2,3})
    bubble_mult: float = 3.0       # ③b (quét {3,4}); trap dùng 3 × nền_ô cố định (plan ③e)
    bubble_min: float = 10.0       # ③b/③e sàn hợp đồng (Q10)
    div_min_len: int = 2
    div_max_len: int = 8
    need_signs: int = 2
    # ---- ④ ----
    cf_body: float = 0.4
    cf_close_ext: float = 0.3
    cf_min_rng_mbr: float = 0.5
    cf_min_delta: float = 0.5
    sl_buf_ticks: float = 3.0      # đệm SL (quét {2,3,5}); đệm = max(đệm, 0,2 mbr)
    sl_buf_mbr: float = 0.2
    sl_floor_mbr: float = 1.0
    sl_cap_mbr: float = 4.0
    r_min: float = 1.7
    tp_r: float = 2.0
    dead_look: int = 300           # 4c: range đã chết trong 300 nến
    block_us_open: bool = True     # 4d: chặn 19:20–20:30 VN (sm 860–930) — công tắc
    block_first_bars: int = 15     # 4d: 15 nến đầu phiên
    veto_window: int = 5           # ⛔ kiệt sức chống hướng: 5 nến tới CF
    stop_run_k: int = 3            # ⛔ nhịp quét stop: K nến sau cực trị
    overlap_bars: int = 30         # ⛔ range chồng range
    overlap_frac: float = 0.5
    overlap_max_drop: float = 0.30 # nếu luật chồng range loại > 30 % thế A ⇒ bỏ luật (plan)
    # ---- corven-2 (4 sửa đổi người học chốt 2026-11-09, report/VARIANTS-NGUOI-HOC-2026-11-09.md). Mặc định TẮT = corven-1;
    # bộ chạy live = cp_live(). ----
    hoi_khong_cham: bool = False   # thế B: nhịp hồi không cần chạm cạnh (≥ 1 nến hồi, mọi nến đóng ngoài, CF đóng vượt nến hồi)
    bo_quet_stop: bool = False     # bỏ ⛔ nhịp đẩy do quét stop
    b_bo_rmin: bool = False        # thế B: bỏ 4c R sẵn ≥ 1,7 (TP vẫn 2R)
    trap_hoi: bool = False         # thế B: thêm dấu hiệu "trap trong nhịp hồi"
    sl_b_canh_sat: bool = False    # corven-3: thế B mốc cạnh — SL = min(đáy cửa sổ, cạnh) − đệm (bỏ trừ dung sai cạnh)
    hoi_trong_n_nen: bool = False  # corven-4: nhịp hồi (không chạm cạnh) phải thuộc cú phá — nến hồi đầu tiên cách nến phá (b.ref) ≤ hoi_max_nen (=5) nến
    hoi_max_nen: int = 5
    b_bo_moc_stacked: bool = False  # corven-5: Break bỏ nhánh 'vùng stacked làm mốc' (chỉ còn mốc cạnh vừa phá); stacked làm DẤU HIỆU giữ nguyên
    sl_b_canh_3tick: bool = False  # corven-6: SL Break mốc cạnh = cạnh vừa phá ∓ 3 tick cố định (bỏ râu nhịp hồi, bỏ đệm theo biên độ); sàn 1 biên độ giữ
    sl_cap_gia: float = None       # corven-6: trần SL theo GIÁ (None = trần 4 biên độ cũ); có giá trị ⇒ không xét trần biên độ. Cổng vẫn tên 'tran_sl'
    bat_fail_break: bool = True    # corven-6: công tắc Settings — tắt ⇒ ứng viên Fail Break không được vào và không chiếm chỗ 1 lệnh mở
    bat_break: bool = True
    gan_range_gan_nhat: bool = False  # corven-5: nhiều Break cùng nến xác nhận ⇒ xét range có nến đóng ngoài (ref) MUỘN nhất trước


LIVE_VERSION = 'corven-6'


def cp_live(sl_kieu_cu: bool = False) -> 'CP':
    """Bộ tham số đang chạy trong indicator (LogicVersion corven-6). sl_kieu_cu=True (Settings "SL kiểu cũ"): SL Break + trần SL như corven-5."""
    return CP(hoi_khong_cham=True, bo_quet_stop=True, b_bo_rmin=True, trap_hoi=True, sl_b_canh_sat=True, hoi_trong_n_nen=True,
              b_bo_moc_stacked=True, gan_range_gan_nhat=True, sl_b_canh_3tick=not sl_kieu_cu, sl_cap_gia=None if sl_kieu_cu else 5.0)


# =====================================================================================================
# NẠP DỮ LIỆU (chỉ TRAIN)
# =====================================================================================================
def train_cut(prefix: str = D90) -> int:
    """Vị trí nến cuối của phiên TRAIN cuối cùng. Chỉ đọc cột datetime + volume (để tách phiên), không đọc giá."""
    raw = pd.read_csv(prefix + '_bars.csv', usecols=['bar_idx', 'datetime', 'open', 'close', 'volume'],
                      parse_dates=['datetime'])
    t = raw['datetime']
    gap = t.diff().dt.total_seconds().div(60.0).fillna(0).to_numpy()
    sno = np.cumsum(gap > K.CONST['gap_min'])
    last_date = t.dt.strftime('%Y-%m-%d').groupby(sno).last()
    train_sessions = [s for s, d in last_date.items() if d <= K.CONST['split_train_end']]
    cut = int(np.flatnonzero(sno == max(train_sessions))[-1])
    return cut


def load_train(prefix: str = D90, cut: Optional[int] = None):
    """Trả (bars: list[FpBar], df) chỉ gồm nến bar_idx ≤ cut. df = kernel._enrich trên phần TRAIN (cột thin tính
    theo trung vị phiên TRAIN — không dùng volume TEST)."""
    if cut is None:
        cut = train_cut(prefix)
    raw = pd.read_csv(prefix + '_bars.csv', parse_dates=['datetime'], float_precision='round_trip')
    raw = raw[raw['bar_idx'] <= cut].reset_index(drop=True)
    assert (raw['bar_idx'].to_numpy() == np.arange(len(raw))).all()
    df = K._enrich(raw)
    t = TICK
    o = np.round(raw['open'].to_numpy() / t).astype(np.int64)
    h = np.round(raw['high'].to_numpy() / t).astype(np.int64)
    l = np.round(raw['low'].to_numpy() / t).astype(np.int64)
    c = np.round(raw['close'].to_numpy() / t).astype(np.int64)
    d = raw['delta'].to_numpy(float)
    mx = raw['max_delta'].to_numpy(float)
    mn = raw['min_delta'].to_numpy(float)
    bars = [OF.FpBar(i, int(o[i]), int(h[i]), int(l[i]), int(c[i]), d[i], mx[i], mn[i], []) for i in range(len(raw))]
    for ch in K.iter_levels(prefix + '.csv', 0, cut, usecols=('bar_idx', 'price', 'bid_vol', 'ask_vol', 'volume')):
        bi = ch['bar_idx'].to_numpy()
        k = np.round(ch['price'].to_numpy() / t).astype(np.int64)
        b = ch['bid_vol'].to_numpy(float)
        a = ch['ask_vol'].to_numpy(float)
        v = ch['volume'].to_numpy(float)
        for j in range(len(bi)):
            bars[bi[j]].levels.append((int(k[j]), b[j], a[j], v[j]))
    return bars, df


# =====================================================================================================
# CÁC THẾ (instance) — kết quả bước ①–②
# =====================================================================================================
@dataclass
class InstA:
    rid: int
    E: int                 # +1 cạnh trên, −1 cạnh dưới (cạnh vừa fail break)
    S: int                 # hướng vào = −E
    ref: int               # nến đóng ngoài
    fb: int                # nến FailBreak
    top: int
    bottom: int
    tol: float
    cands: list = field(default_factory=list)    # [(cf, dist_mbr, pass_2a)]
    passed: list = field(default_factory=list)   # các CF qua ②
    fail: str = ''


@dataclass
class InstB:
    rid: int
    D: int
    ref: int               # nến đóng ngoài
    bc: int                # nến BreakConfirmed
    E: int                 # cạnh vừa phá (tick)
    top: int
    bottom: int
    tol: float
    exhausted: bool = False
    alive: bool = True
    end: str = ''          # reentry / het_tuoi / het_phien / merge / het_file
    end_bar: int = -1
    suspended: bool = False
    n_suspend: int = 0
    push_ext: int = 0
    broken_at: int = -1
    zones: list = field(default_factory=list)       # vùng stacked cùng hướng D (dict)
    touched_edge: bool = False                      # có nến chạm dải cạnh ± tol trong đời thế
    far_edge: int = 0                               # số CF có chạm dải nhưng đóng xa > near
    passed_edge: list = field(default_factory=list)
    passed_zone: list = field(default_factory=list) # [(cf, zone_bar, lo, hi)]
    zone_ct: int = 0                                # số vùng bị loại vì đóng xuyên (2b)
    zone_touched_before: int = 0                    # số lần vùng bị loại vì đã chạm trước nhịp test
    piv_at: dict = field(default_factory=dict)      # pivot cấu trúc (1c) tại mỗi CF được xét — mốc trap thế B


@dataclass
class ExcA:
    rid: int
    p: int                 # hướng cú thủng (−1 thủng xuống ⇒ vào buy, S = −p)
    breach_start: int      # nến đóng ngoài của cú thủng
    bar: int               # nến x ("lần 2")
    ext: int               # cực trị của nến y (lần 1) mà x quét qua
    close: int
    y: int = -1            # nến "lần 1"
    top: int = 0
    bottom: int = 0
    tol: float = 0.0


class Step2Machine:
    """Nuôi RangeEngine từng nến đã đóng, theo dõi thế A/B tới hết bước ②."""

    def __init__(self, cp: CP = None, rp: Params = None, sess: Optional[np.ndarray] = None,
                 good: Optional[np.ndarray] = None):
        self.cp = cp or CP()
        self.good = good          # chỉ để ĐẾM (cnt) trên phiên dày; không ảnh hưởng logic
        self.eng = RangeEngine(rp or Params(), TICK)
        self.sess = sess
        self.A: List[InstA] = []
        self.B: List[InstB] = []
        self.EXC: List[ExcA] = []
        self.a_whipsaw = 0
        self.b_exhausted_seen = 0
        self.b_exh_bars: List[int] = []
        self.liveA: List[InstA] = []
        self.liveB: List[InstB] = []
        self.ph: List[tuple] = []      # pivot đỉnh (idx, tick) — luật 1 nến của Range Box
        self.pl: List[tuple] = []
        self.mbr: List[float] = []
        self.zones_by_bar: Dict[int, list] = {}
        self._exc_done = set()
        self.death: Dict[int, int] = {}      # rid → nến range chuyển DEAD
        self.birth: Dict[int, int] = {}
        self.fb_count: Dict[int, int] = {}   # rid → số FailBreak đã có (gồm whipsaw)
        self.fb_bars: Dict[int, list] = {}   # rid → các nến FailBreak
        self.a_nth: Dict[int, int] = {}      # id(InstA) → FailBreak thứ mấy của range
        self.O: List[int] = []         # giá mở từng nến (corven-2: nến hồi ngược màu)
        self.cnt = dict(b_eval=0, b_pass=0, b_pass_edge=0, b_pass_zone=0, b_edge_khong_cham=0, b_edge_xa=0,
                        b_khong_vung=0, b_vung_dong_xuyen=0, b_vung_da_cham_truoc=0, b_vung_khong_cham_cua_so=0,
                        b_bar_tam_huy_1c=0)

    # ------------------------------------------------------------------ tiện ích
    def _same(self, a: int, b: int) -> bool:
        if not self.cp.same_session or self.sess is None:
            return True
        return self.sess[a] == self.sess[b]

    def tol_now(self, i: int) -> float:
        return max(self.eng.p.MinTolTicks, self.eng.p.TolK * self.mbr[i])

    # ------------------------------------------------------------------ một nến
    def on_bar(self, bar: OF.FpBar):
        e = self.eng
        i = bar.idx
        assert i == len(e.H)
        self.O.append(bar.o)
        # trạng thái các range TRƯỚC nến i (cho ngoại lệ "xác nhận lần 2")
        pre = [(r.id, r.state, r.pend_side if r.state == PENDING else r.break_side,
                r.pend_start if r.state == PENDING else r.break_idx) for r in e.live if r.state in (PENDING, BROKEN)]
        n_ev = len(e.events)
        live_before = list(e.live)
        e.feed_ticks(bar.o, bar.h, bar.l, bar.c)
        for r in live_before:
            if r.state == DEAD and r.id not in self.death:
                self.death[r.id] = i
        self.mbr.append(e.mbr)
        evs = e.events[n_ev:]
        H, L, C = e.H, e.L, e.C
        if i >= 2:
            j = i - 1
            if H[j] > H[j - 1] and H[j] >= H[i]:
                self.ph.append((j, H[j]))
            if L[j] < L[j - 1] and L[j] <= L[i]:
                self.pl.append((j, L[j]))
        zs = OF.stacked_zones(bar, self.cp.si_ratio, self.cp.si_run, self.cp.si_minvol)
        self.zones_by_bar[i] = zs
        self.zones_by_bar.pop(i - 200, None)

        ev_by_rid: Dict[int, list] = {}
        for ev in evs:
            ev_by_rid.setdefault(ev.rid, []).append(ev)

        # ---------- cập nhật thế A đang sống (CF = fb+1, fb+2) ----------
        for a in list(self.liveA):
            if i == a.fb:
                continue
            r = e.ranges[a.rid]
            ok_seq = (i - a.fb <= self.cp.cf_after_fb and i - a.ref <= self.cp.win_a_max - 1 and self._same(i, a.fb)
                      and r.state == ACTIVE and not any(x.kind == 'CloseOutside' for x in ev_by_rid.get(a.rid, [])))
            if not ok_seq:
                self._close_a(a)
                continue
            self._a_candidate(a, i, r.top, r.bottom)
            if i - a.fb >= self.cp.cf_after_fb or i - a.ref >= self.cp.win_a_max - 1:
                self._close_a(a)

        # ---------- cập nhật thế B đang sống ----------
        for b in list(self.liveB):
            if i == b.bc:
                continue
            self._b_step(b, i, ev_by_rid.get(b.rid, []))

        # ---------- sự kiện mới ----------
        for ev in evs:
            r = e.ranges[ev.rid]
            if ev.kind == 'Birth':
                self.birth[ev.rid] = i
            if ev.kind == 'BreakConfirmed' and r.state == DEAD and ev.rid not in self.death:
                self.death[ev.rid] = i
            if ev.kind == 'FailBreak':
                self.fb_count[ev.rid] = self.fb_count.get(ev.rid, 0) + 1
                self.fb_bars.setdefault(ev.rid, []).append(i)
                back_active = r.state == ACTIVE and not any(x.kind == 'CloseOutside' and x.bar == i for x in ev_by_rid[ev.rid])
                if not back_active:
                    self.a_whipsaw += 1
                    continue
                a = InstA(rid=ev.rid, E=ev.side, S=-ev.side, ref=ev.ref, fb=i, top=ev.top, bottom=ev.bottom, tol=r.tol)
                self.a_nth[id(a)] = self.fb_count[ev.rid]
                self.A.append(a)
                self._a_candidate(a, i, r.top, r.bottom)
                if self.cp.cf_after_fb > 0 and i - a.ref < self.cp.win_a_max - 1:
                    self.liveA.append(a)
                else:
                    self._finish_a(a)
            elif ev.kind == 'BreakConfirmed':
                exhausted = r.state == DEAD and r.exhausted
                if exhausted:
                    self.b_exhausted_seen += 1
                    self.b_exh_bars.append(i)
                    if not self.cp.b_from_exhausted:
                        continue
                D = ev.side
                b = InstB(rid=ev.rid, D=D, ref=ev.ref, bc=i, E=ev.top if D > 0 else ev.bottom, top=ev.top,
                          bottom=ev.bottom, tol=r.tol, exhausted=exhausted)
                b.push_ext = max(H[ev.ref:i + 1]) if D > 0 else min(L[ev.ref:i + 1])
                for z in range(ev.ref, i + 1):
                    self._b_add_zones(b, z)
                for z in b.zones:
                    for k in range(z['bar'] + 1, i + 1):
                        self._zone_track(z, k)
                self.B.append(b)
                self.liveB.append(b)
                piv = self.ph if D < 0 else self.pl
                b.piv_at[i] = piv[-1][1] if piv and piv[-1][0] >= b.ref else None
                self._b_eval(b, i)

        # ---------- ngoại lệ "xác nhận lần 2" — định nghĩa siết G1 (GĐ2 v1) ----------
        # y = nến lập cực trị cú thủng (start..i−1; hoà ⇒ nến SỚM nhất) và y phải là "lần 1" (râu phía −S ≥ 1 tick, đóng lùi
        # về phía S ≥ tol so với cực trị của nó); x = nến i quét qua cực trị y ≥ 1 tick và ĐÓNG về phía S ≥ tol so với cực trị
        # của y, vẫn ngoài range. Chỉ 1 lần mỗi cú thủng, ≤ 30 nến từ nến đóng ngoài.
        for (rid, st, p, start) in pre:
            if p == 0 or start < 0 or (rid, start) in self._exc_done or i - start > self.cp.exc_max_age:
                continue
            r = e.ranges[rid]
            if i - 1 < start:
                continue
            S = -p
            outside = bar.c < r.bottom if p < 0 else bar.c > r.top
            if not outside:
                continue
            seg = range(start, i)
            y = min(seg, key=lambda k: (L[k], k)) if S > 0 else min(seg, key=lambda k: (-H[k], k))
            if S > 0:
                first = min(e.O[y], C[y]) - L[y] >= 1 and C[y] - L[y] >= r.tol
                hit = first and bar.l <= L[y] - 1 and bar.c >= L[y] + r.tol
                ext = L[y]
            else:
                first = H[y] - max(e.O[y], C[y]) >= 1 and H[y] - C[y] >= r.tol
                hit = first and bar.h >= H[y] + 1 and bar.c <= H[y] - r.tol
                ext = H[y]
            if hit:
                self.EXC.append(ExcA(rid, p, start, i, ext, bar.c, y, r.top, r.bottom, r.tol))
                self._exc_done.add((rid, start))

    # ------------------------------------------------------------------ thế A
    def _a_candidate(self, a: InstA, i: int, top: int, bottom: int):
        c = self.eng.C[i]
        if not (bottom <= c <= top):
            return
        dist = (top - c) if a.E > 0 else (c - bottom)
        m = self.mbr[i]
        ok = m > 0 and dist <= self.cp.near_mbr * m + 1e-9
        a.cands.append((i, round(dist / m, 3) if m else None, ok))
        if ok:
            a.passed.append(i)

    def _close_a(self, a: InstA):
        if a in self.liveA:
            self.liveA.remove(a)
        self._finish_a(a)

    def _finish_a(self, a: InstA):
        if not a.passed:
            a.fail = '2a_xa' if a.cands else 'khong_cf'

    # ------------------------------------------------------------------ thế B
    def _b_add_zones(self, b: InstB, z: int):
        for zz in self.zones_by_bar.get(z, []):
            if zz.side != b.D:
                continue
            if zz.position != OF.POS_BODY or zz.weak:      # Q3: mốc stacked chỉ Body, không Weak
                continue
            lo, hi = round(zz.lo / TICK), round(zz.hi / TICK)
            b.zones.append(dict(bar=z, D=b.D, lo=lo, hi=hi, lo_p=zz.lo, hi_p=zz.hi, first_touch=None, first_ct=None,
                                pos=zz.position, weak=zz.weak))

    def _zone_track(self, z: dict, k: int):
        """Ghi lần chạm ĐÚNG vùng đầu tiên (High ≥ Lo và Low ≤ Hi) và lần đóng xuyên mép xa đầu tiên (CheckEnd CloseThrough)."""
        H, L, C = self.eng.H, self.eng.L, self.eng.C
        if z['first_touch'] is None and H[k] >= z['lo'] and L[k] <= z['hi']:
            z['first_touch'] = k
        if z['first_ct'] is None:
            e = OF.check_end(z['D'], z['lo_p'], z['hi_p'], H[k] * TICK, L[k] * TICK, C[k] * TICK, OF.MODE_CLOSE)
            if e == OF.END_CLOSED:
                z['first_ct'] = k

    def _b_end(self, b: InstB, why: str, i: int):
        b.alive = False
        b.end = why
        b.end_bar = i
        if b in self.liveB:
            self.liveB.remove(b)

    def _b_step(self, b: InstB, i: int, evs: list):
        H, L, C = self.eng.H, self.eng.L, self.eng.C
        if any(x.kind == 'ReEntry' for x in evs) or (b.exhausted and b.bottom <= C[i] <= b.top):
            return self._b_end(b, 'reentry', i)
        if any(x.kind == 'Merge' for x in evs):
            return self._b_end(b, 'merge', i)
        if i - b.ref > self.cp.age_b:
            return self._b_end(b, 'het_tuoi', i)
        if not self._same(i, b.bc):
            return self._b_end(b, 'het_phien', i)
        # vùng mới cùng hướng trong cú đẩy / nhịp sau
        self._b_add_zones(b, i)
        for z in b.zones:
            if z['bar'] < i:
                self._zone_track(z, i)
        # 1c cấu trúc gần nhất chưa gãy ngược
        piv = self.ph if b.D < 0 else self.pl
        lvl = None
        for p in reversed(piv):                     # pivot ngược hướng D gần nhất, sau nến đóng ngoài (và sau lần gãy trước)
            if p[0] < b.ref or p[0] <= b.broken_at:
                break
            lvl = p[1]
            break
        if b.suspended:
            new_ext = (H[i] > b.push_ext) if b.D > 0 else (L[i] < b.push_ext)
            if new_ext:
                b.suspended = False
                lvl = None
        elif lvl is not None:
            if (b.D < 0 and C[i] > lvl) or (b.D > 0 and C[i] < lvl):
                b.suspended = True
                b.n_suspend += 1
                b.broken_at = i
        b.push_ext = max(b.push_ext, H[i]) if b.D > 0 else min(b.push_ext, L[i])
        if not b.suspended:
            b.piv_at[i] = lvl
            self._b_eval(b, i)
        elif self.good is None or self.good[i]:
            self.cnt['b_bar_tam_huy_1c'] += 1

    def _hoi_ok(self, b: InstB, j: int, w0: int) -> bool:
        """corven-2: các nến [w0, j−1] đều đóng ngoài range phía D, có ≥ 1 nến hồi (đóng ngược D so với nến trước, hoặc nến
        ngược màu), CF j đóng ngoài range và vượt giá đóng cực trị của các nến hồi."""
        C, O, D, E = self.eng.C, self.O, b.D, b.E
        ks = range(w0, j)
        if len(ks) == 0 or (C[j] - E) * D <= 0:
            return False
        if any((C[k] - E) * D <= 0 for k in ks):
            return False
        pb = [k for k in ks if (C[k] - C[k - 1]) * D < 0 or (C[k] - O[k]) * D < 0]
        if not pb:
            return False
        if self.cp.hoi_trong_n_nen and min(pb) - b.ref > self.cp.hoi_max_nen:
            return False
        lim = max(C[k] for k in pb) if D > 0 else min(C[k] for k in pb)
        return (C[j] - lim) * D > 0

    def _b_eval(self, b: InstB, j: int):
        """CF ứng viên = nến j: kiểm 2a (cạnh / stacked) + 2b (vùng chưa đóng xuyên)."""
        H, L, C = self.eng.H, self.eng.L, self.eng.C
        W = self.cp.win_b
        w0 = max(j - W + 1, b.ref + 1)
        m = self.mbr[j]
        # --- mốc cạnh ---
        E, tol = b.E, b.tol
        touch = any(H[k] >= E - tol and L[k] <= E + tol for k in range(w0, j + 1))
        cnt = self.cnt if (self.good is None or self.good[j]) else dict.fromkeys(self.cnt, 0)
        cnt['b_eval'] += 1
        pe = False
        if touch:
            b.touched_edge = True
            dist = (E - C[j]) if b.D < 0 else (C[j] - E)
            if 0 < dist <= self.cp.near_mbr * m + 1e-9:
                b.passed_edge.append(j)
                pe = True
            else:
                b.far_edge += 1
                cnt['b_edge_xa'] += 1
        else:
            cnt['b_edge_khong_cham'] += 1
        if not pe and self.cp.hoi_khong_cham and self._hoi_ok(b, j, w0):
            b.passed_edge.append(j)
            pe = True
        # --- mốc stacked mới cùng hướng D ---
        tz = self.tol_now(j)
        pz = False
        why = []
        for z in ([] if self.cp.b_bo_moc_stacked else b.zones):
            if j - z['bar'] > self.cp.age_b or z['bar'] >= j:
                continue
            if z['first_ct'] is not None and z['first_ct'] <= j:
                if not z.get('ct_counted'):
                    z['ct_counted'] = True
                    b.zone_ct += 1
                why.append('ct')
                continue
            ws = max(w0, z['bar'] + 1)
            if z['first_touch'] is not None and z['first_touch'] < ws:
                why.append('cham_truoc')
                continue
            if any(H[k] >= z['lo'] - tz and L[k] <= z['hi'] + tz for k in range(ws, j + 1)):
                # Q5: CF đóng cách mép gần của vùng ≤ near × mbr về phía D (đóng TRONG vùng cũng tính là gần — chưa xuyên mép xa)
                dz = (C[j] - z['hi']) if b.D > 0 else (z['lo'] - C[j])
                if dz <= self.cp.near_mbr * m + 1e-9:
                    b.passed_zone.append((j, z['bar'], z['lo'], z['hi']))
                    pz = True
                else:
                    why.append('xa')
            else:
                why.append('khong_cham')
        if pe:
            cnt['b_pass_edge'] += 1
        if pz:
            cnt['b_pass_zone'] += 1
        if pe or pz:
            cnt['b_pass'] += 1
        elif not why:
            cnt['b_khong_vung'] += 1
        elif 'xa' in why:
            cnt['b_vung_cf_xa'] = cnt.get('b_vung_cf_xa', 0) + 1
        elif 'khong_cham' in why:
            cnt['b_vung_khong_cham_cua_so'] += 1
        elif 'cham_truoc' in why:
            cnt['b_vung_da_cham_truoc'] += 1
        else:
            cnt['b_vung_dong_xuyen'] += 1


def run_step2(bars: List[OF.FpBar], sess: Optional[np.ndarray] = None, cp: CP = None, rp: Params = None,
              good: Optional[np.ndarray] = None) -> Step2Machine:
    m = Step2Machine(cp, rp, sess, good)
    for b in bars:
        m.on_bar(b)
    for a in list(m.liveA):
        m._close_a(a)
    for b in list(m.liveB):
        m._b_end(b, 'het_file', len(bars) - 1)
    return m


# =====================================================================================================
# THỐNG KÊ TẦN SUẤT DẤU HIỆU (so với plan mục 0) — trên nến của phiên TRAIN dày
# =====================================================================================================
def _pct(x):
    return round(100.0 * float(np.mean(x)), 1) if len(x) else None


def signal_frequencies(bars: List[OF.FpBar], df: pd.DataFrame, good: np.ndarray, mbr: List[float]) -> dict:
    n = len(bars)
    H = np.array([b.h for b in bars]); L = np.array([b.l for b in bars])
    O = np.array([b.o for b in bars]); C = np.array([b.c for b in bars])
    rng = (H - L) * TICK
    out = {}
    g = good
    out['n_bars'] = int(g.sum())
    out['mbr_median_price'] = round(float(np.median(np.array(mbr)[g])) * TICK, 2)
    out['bar_range_p25_50_75_90'] = [round(float(np.percentile(rng[g], q)), 2) for q in (25, 50, 75, 90)]
    pos = g & (H > L)
    body = np.abs(C - O) / np.where(H > L, H - L, 1)
    out['body_frac_p25_50_75'] = [round(float(np.percentile(body[pos], q)), 2) for q in (25, 50, 75)]
    up = pos & (C > O)
    hc = (H - C) / np.where(H > L, H - L, 1)
    out['up_close_to_high_p50_p75'] = [round(float(np.percentile(hc[up], q)), 2) for q in (50, 75)]
    mad = K.med_abs_delta(df).to_numpy()
    ratio = np.abs(df['delta'].to_numpy()) / np.where(mad > 0, mad, np.nan)
    rg = g & np.isfinite(ratio)
    out['delta_ge2x_pct'] = _pct(ratio[rg] >= 2)
    out['delta_ge3x_pct'] = _pct(ratio[rg] >= 3)
    md = df['max_delta'].to_numpy(); dd = df['delta'].to_numpy(); mn = df['min_delta'].to_numpy()
    out['max_delta_eq_delta_pct'] = _pct((md == dd) & (mn == dd))
    # ---- nền_ô: 3 cách ----
    cv = [OF.cell_value(b) for b in bars]
    # (a) plan: trung vị cuốn chiếu 100 nến của cell_value, TRƯỚC nến hiện tại ; (b) GỒM nến hiện tại
    base_before = np.full(n, np.nan); base_incl = np.full(n, np.nan)
    cb = OF.CellBaseline(100)
    for i, b in enumerate(bars):
        if cb.ready():
            base_before[i] = cb.value()
        cb.push(b)
        if cb.ready():
            base_incl[i] = cb.value()
    # (c) kiểu OrderFlowBubbles: top-3 ô theo TỔNG volume, gộp side-volume của chúng (300 giá trị) rồi lấy trung vị, trước nến
    base_ofb = np.full(n, np.nan)
    from collections import deque
    q = deque(); pool = []
    import bisect
    for i, b in enumerate(bars):
        if len(q) >= 100:
            base_ofb[i] = OF._median(pool)
        cells = sorted(b.levels, key=lambda t: -t[3])[:3]
        vals = [max(t[1], t[2]) for t in cells]
        q.append(vals)
        for v in vals:
            bisect.insort(pool, v)
        if len(q) > 100:
            for v in q.popleft():
                del pool[bisect.bisect_left(pool, v)]
    maxcell = np.array([max([max(t[1], t[2]) for t in b.levels], default=0) for b in bars], float)
    allcells = np.array([max(t[1], t[2]) for b, gg in zip(bars, g) if gg for t in b.levels], float)
    out['cell_sidevol_p90_all_cells'] = float(np.percentile(allcells, 90))
    out['cell_sidevol_p90_nonzero'] = float(np.percentile(allcells[allcells > 0], 90))
    for name, base in (('truoc_nen', base_before), ('gom_nen', base_incl), ('kieu_OFB', base_ofb)):
        ok = g & np.isfinite(base) & (base > 0)
        r = maxcell[ok] / base[ok]
        out[f'nen_o_{name}'] = dict(median_base=float(np.median(base[ok])), ge3x=_pct(r >= 3), ge4x=_pct(r >= 4),
                                    bong_3x_va_10=_pct((r >= 3) & (maxcell[ok] >= 10)))
    # ---- bóng theo phía (cách (a) — mặc định) ----
    bb = np.zeros(n, bool); bs = np.zeros(n, bool)
    for i, b in enumerate(bars):
        if np.isfinite(base_before[i]):
            bb[i] = bool(OF.bubbles(b, +1, base_before[i]))
            bs[i] = bool(OF.bubbles(b, -1, base_before[i]))
    out['bong_buy_pct'] = _pct(bb[g]); out['bong_sell_pct'] = _pct(bs[g]); out['bong_any_pct'] = _pct((bb | bs)[g])
    # ---- stacked ----
    def si_rate(pct, run, mv, side_out=None):
        has = np.zeros(n, bool); d3 = np.zeros(n, bool); hb = np.zeros(n, bool); hs = np.zeros(n, bool)
        for i, b in enumerate(bars):
            zs = OF.stacked_zones(b, pct, run, mv)
            has[i] = bool(zs)
            hb[i] = any(z.side > 0 for z in zs); hs[i] = any(z.side < 0 for z in zs)
            d3[i] = any((z.position == OF.POS_BODY) and not z.weak and ((z.side > 0 and b.c * TICK >= z.hi - 1e-9) or
                                                                     (z.side < 0 and b.c * TICK <= z.lo + 1e-9)) for z in zs)
        if side_out is not None:
            side_out.update(buy=_pct(hb[g]), sell=_pct(hs[g]))
        return has, d3
    s3, s4 = {}, {}
    h3, d3 = si_rate(250, 3, 1, s3)
    h4, d4 = si_rate(250, 4, 1, s4)
    h35, _ = si_rate(250, 3, 5)
    out['stacked_250_3_mv1_theo_phia_pct'] = s3; out['stacked_250_4_mv1_theo_phia_pct'] = s4
    out['stacked_250_3_mv1_pct'] = _pct(h3[g]); out['stacked_250_4_mv1_pct'] = _pct(h4[g])
    out['stacked_250_3_mv5_pct'] = _pct(h35[g])
    out['stacked_3d_hople_pct'] = _pct(d3[g]); out['stacked_3d_hople_run4_pct'] = _pct(d4[g])
    # ---- kiệt sức ----
    et = np.zeros(n, bool); eb = np.zeros(n, bool)
    for i, b in enumerate(bars):
        t, bo = OF.exhaustion(b)
        et[i] = t.hit; eb[i] = bo.hit
    out['kiet_suc_dinh_pct'] = _pct(et[g]); out['kiet_suc_day_pct'] = _pct(eb[g])
    mot = df['max_one_trade'].to_numpy()
    out['max_one_trade_eq0_pct'] = _pct(mot[g] == 0)
    out['_series'] = dict(base_before=base_before, ratio=ratio, exh_top=et, exh_bot=eb)
    return out


# =====================================================================================================
# BÁO CÁO GĐ0
# =====================================================================================================
def summarize(m: Step2Machine, df: pd.DataFrame, good: np.ndarray) -> dict:
    sid = df['session_id'].to_numpy()
    good_sess = sorted(set(sid[good]))
    nd = len(good_sess)

    def in_good(i):
        return bool(good[i])

    A = [a for a in m.A if in_good(a.fb)]
    B = [b for b in m.B if in_good(b.bc)]
    X = [x for x in m.EXC if in_good(x.bar)]
    births = [ev for ev in m.eng.events if ev.kind == 'Birth' and in_good(ev.bar)]
    fails = [ev for ev in m.eng.events if ev.kind == 'FailBreak' and in_good(ev.bar)]
    bcs = [ev for ev in m.eng.events if ev.kind == 'BreakConfirmed' and in_good(ev.bar)]
    s = {}
    s['phien_train_day'] = nd
    s['range_sinh_moi_ngay'] = round(len(births) / nd, 2)
    s['failbreak_su_kien'] = len(fails)
    s['a_whipsaw_bo'] = m.a_whipsaw
    s['breakconfirmed_su_kien'] = len(bcs)
    s['b_breakconfirmed_het_luot_reentry_dead_ngay'] = sum(1 for x in m.b_exh_bars if in_good(x))
    ndates = len(set(df['datetime'].dt.strftime('%Y-%m-%d').to_numpy()[good]))
    s['so_ngay_lich_co_nen'] = ndates
    s['range_sinh_moi_ngay_lich'] = round(len(births) / ndates, 2)
    # ---- thế A ----
    a_pass = [a for a in A if a.passed]
    s['A'] = dict(n=len(A), per_day=round(len(A) / nd, 2), qua_2=len(a_pass), qua_2_per_day=round(len(a_pass) / nd, 2),
                  loai_2a_xa=sum(1 for a in A if a.fail == '2a_xa'), loai_khong_cf=sum(1 for a in A if a.fail == 'khong_cf'),
                  ty_le_loai_2a_pct=round(100 * sum(1 for a in A if a.fail == '2a_xa') / max(1, len(A)), 1),
                  so_cf_ung_vien_qua_2=sum(len(a.passed) for a in A),
                  dist_mbr_cf_dau_p50=float(np.median([a.cands[0][1] for a in A if a.cands and a.cands[0][1] is not None])) if A else None)
    s['dem_theo_nen_B_phien_day'] = dict(m.cnt)
    s['A_ngoai_le_lan2_ung_vien_gia'] = dict(n=len(X), per_day=round(len(X) / nd, 2))
    # ---- thế B ----
    b_edge = [b for b in B if b.passed_edge]
    b_zone = [b for b in B if b.passed_zone]
    b_any = [b for b in B if b.passed_edge or b.passed_zone]
    ends = {}
    for b in B:
        ends[b.end] = ends.get(b.end, 0) + 1
    never = [b for b in B if not (b.passed_edge or b.passed_zone)]
    s['B'] = dict(n=len(B), per_day=round(len(B) / nd, 2), qua_2=len(b_any), qua_2_per_day=round(len(b_any) / nd, 2),
                  qua_2_moc_canh=len(b_edge), qua_2_moc_stacked=len(b_zone),
                  ket_thuc=ends,
                  bi_1c_tam_huy_it_nhat_1_lan=sum(1 for b in B if b.n_suspend > 0),
                  khong_qua_2=len(never),
                  khong_qua__khong_test_canh=sum(1 for b in never if not b.touched_edge),
                  khong_qua__test_nhung_xa=sum(1 for b in never if b.touched_edge and b.far_edge > 0),
                  khong_qua__chet_vi_reentry_2b=sum(1 for b in never if b.end == 'reentry'),
                  vung_stacked_lam_moc_tong=sum(len(b.zones) for b in B),
                  vung_bi_loai_dong_xuyen_2b=sum(b.zone_ct for b in B),
                  so_cf_ung_vien_qua_2=sum(len(set(b.passed_edge) | {p[0] for p in b.passed_zone}) for b in B))
    # ---- theo ngày ----
    per = {}
    for d in good_sess:
        per[d] = dict(A=0, A2=0, B=0, B2=0)
    for a in A:
        d = sid[a.fb]; per[d]['A'] += 1; per[d]['A2'] += bool(a.passed)
    for b in B:
        d = sid[b.bc]; per[d]['B'] += 1; per[d]['B2'] += bool(b.passed_edge or b.passed_zone)
    s['theo_ngay'] = per
    return s


# =====================================================================================================
# GĐ1 — ③ dấu hiệu · ④ lệnh · ⛔ · chọn lệnh (4d) · mô phỏng kernel.simulate
# =====================================================================================================
SIGN_TYPES = ('delta', 'bong', 'kiet_suc', 'stacked', 'trap')
GATES = ('g4a_cf', 'v_kiet_suc_chong', 'v_quet_stop', 'v_chong_range', 'tran_sl', 'r_nho', 'chan_1920', 'dau_phien',
         'cuoi_phien')
GATE_VN = dict(g4a_cf='4a nến xác nhận', v_kiet_suc_chong='⛔ kiệt sức chống hướng', v_quet_stop='⛔ nhịp đẩy do quét stop',
               v_chong_range='⛔ range chồng range', tran_sl='4b trần SL 4 mbr', r_nho='4c R sẵn < 1,7',
               chan_1920='4d chặn 19:20–20:30 VN', dau_phien='4d 15 nến đầu phiên', cuoi_phien='nến cuối phiên (không vào được)')
THE_ORDER = {'A': 0, 'A2': 1, 'B': 2}


class Feat:
    """Đặc trưng từng nến, tính một lần, không nhìn trước.
    Quy ước (Q11): nền_ô tính trên 100 nến TRƯỚC nến hiện tại (như OrderFlowBubbles); mbr (Range Box) và medΔ (kernel,
    50 nến) GỒM nến hiện tại."""

    def __init__(self, bars: List[OF.FpBar], df: pd.DataFrame, mbr, cp: CP, good: Optional[np.ndarray] = None):
        n = len(bars)
        self.bars = bars
        self.H = np.array([b.h for b in bars], np.int64)
        self.L = np.array([b.l for b in bars], np.int64)
        self.O = np.array([b.o for b in bars], np.int64)
        self.C = np.array([b.c for b in bars], np.int64)
        self.Dl = np.array([b.delta for b in bars], float)
        self.mbr = np.asarray(mbr, float)
        self.medd = K.med_abs_delta(df).to_numpy()
        base = np.full(n, np.nan)
        cb = OF.CellBaseline(100)
        for i, b in enumerate(bars):
            if cb.ready():
                base[i] = cb.value()
            cb.push(b)
        self.base = base
        self.exh = [OF.exhaustion(b) for b in bars]
        self.zones = [OF.stacked_zones(b, cp.si_ratio, cp.si_run, cp.si_minvol) for b in bars]
        self.sm = df['sm'].to_numpy()
        sno = df['session_no'].to_numpy()
        starts = np.r_[0, np.flatnonzero(np.diff(sno)) + 1]
        ends = np.r_[starts[1:] - 1, n - 1]
        self.sstart = np.repeat(starts, ends - starts + 1)
        self.send = np.repeat(ends, ends - starts + 1)
        self.good = np.ones(n, bool) if good is None else good


@dataclass
class Cand:
    cf: int
    the: str                 # 'A' | 'A2' (xác nhận lần 2) | 'B'
    S: int
    rid: int
    inst: object
    key: tuple               # (range, cạnh, nhóm thế) — 4d "mỗi (range, cạnh E, thế) tối đa 1 lệnh"
    ref: int
    w0: int                  # đầu cửa sổ test (2c)
    mocs: list               # [dict(kind, level, tol, band, zid)]
    trap_levels: list
    exhausted: bool = False
    signs: dict = field(default_factory=dict)    # loại → (mô tả có số, nến neo, giá tick)
    gates: list = field(default_factory=list)    # mọi cổng ④/⛔ bị trượt (theo thứ tự GATES)
    entry: int = 0
    sl: int = 0
    tp: float = 0.0
    risk: float = 0.0
    r_avail: float = 0.0
    target: float = 0.0
    moc_used: str = ''
    anchor: str = ''
    piv: tuple = ()

    @property
    def types(self):
        return tuple(t for t in SIGN_TYPES if t in self.signs)


def build_candidates(m: Step2Machine, feat: Feat, cp: CP) -> List[Cand]:
    out = []
    for a in m.A:
        E = a.top if a.E > 0 else a.bottom
        for cf in a.passed:
            out.append(Cand(cf, 'A', a.S, a.rid, a, (a.rid, a.E, 'A'), a.ref, a.ref,
                            [dict(kind='canh', level=E, tol=a.tol, band=(E - a.tol, E + a.tol), zid=None)], [E]))
    n = len(feat.C)
    for x in m.EXC:
        S = -x.p
        for cf in range(x.bar, min(n, x.bar + cp.a2_cf_after + 1)):
            if feat.sstart[cf] != feat.sstart[x.bar]:
                break
            out.append(Cand(cf, 'A2', S, x.rid, x, (x.rid, x.p, 'A'), x.breach_start, max(x.breach_start, x.bar - 4),
                            [dict(kind='cuc_tri', level=x.ext, tol=x.tol, band=(x.ext - x.tol, x.ext + x.tol), zid=None)],
                            [x.ext]))
    for b in m.B:
        js = sorted(set(b.passed_edge) | {p[0] for p in b.passed_zone})
        for j in js:
            mocs = []
            if j in b.passed_edge:
                mocs.append(dict(kind='canh', level=b.E, tol=b.tol, band=(b.E - b.tol, b.E + b.tol), zid=None))
            tz = m.tol_now(j)
            for (jj, zb, lo, hi) in b.passed_zone:
                if jj == j:
                    lvl = lo if b.D < 0 else hi
                    mocs.append(dict(kind='stacked', level=lvl, tol=tz, band=(lo - tz, hi + tz), zid=(zb, lo, hi)))
            tl = [b.E] + ([b.piv_at[j]] if b.piv_at.get(j) is not None else [])
            out.append(Cand(j, 'B', b.D, b.rid, b, (b.rid, b.D, 'B'), b.ref, max(j - m.cp.win_b + 1, b.ref + 1), mocs, tl,
                            exhausted=b.exhausted))
    if cp.gan_range_gan_nhat:   # corven-5: Break — range có nến đóng ngoài muộn nhất trước; Fail Break giữ thứ tự cũ (rid)
        out.sort(key=lambda c: (c.cf, THE_ORDER[c.the], -c.ref if c.the == 'B' else c.rid))
    else:
        out.sort(key=lambda c: (c.cf, THE_ORDER[c.the], c.rid))
    return out


def _px(t):
    return f"{t * TICK:.1f}".replace('.', ',')


def find_signs(c: Cand, f: Feat, cp: CP) -> dict:
    """③ — mọi dấu hiệu có nến neo trong cửa sổ [w0, cf], cùng phe S. Trả {loại: (mô tả, nến neo, giá tick)}."""
    S, cf = c.S, c.cf
    H, L, O, C, Dl = f.H, f.L, f.O, f.C, f.Dl
    W = range(c.w0, cf + 1)
    sg = {}
    # ③a delta: to (CF hoặc nến trước CF) hoặc ngược giá — tính tối đa 1
    for k in (cf, cf - 1):
        if k < c.w0 or not (f.medd[k] > 0):
            continue
        if Dl[k] * S > 0 and abs(Dl[k]) >= cp.delta_mult * f.medd[k] - 1e-9 and (C[k] - O[k]) * S > 0:
            sg['delta'] = (f"Δ to {Dl[k]:+.0f} = {abs(Dl[k]) / f.medd[k]:.1f}× medΔ".replace('.', ','), k, C[k])
            break
    if 'delta' not in sg:
        for x in W:
            for mo in c.mocs:
                reach = H[x] >= mo['level'] - mo['tol'] if S < 0 else L[x] <= mo['level'] + mo['tol']
                if not reach:
                    continue
                ok, s0, sd = OF.delta_divergence(H, L, Dl, x, S, f.mbr[x], cp.div_min_len, cp.div_max_len)
                if ok:
                    sg['delta'] = (f"Δ ngược giá ΣΔ {sd:+.0f}/{x - s0} nến", x, H[x] if S < 0 else L[x])
                    break
            if 'delta' in sg:
                break
    # ③b bóng đúng phe: nửa nến phía S hoặc trong dải mốc
    best = None
    for k in W:
        bs = f.base[k]
        if not np.isfinite(bs) or bs <= 0:
            continue
        for (tk, v) in OF.bubbles(f.bars[k], S, bs, cp.bubble_mult, cp.bubble_min):
            if any(OF.bubble_in_place(f.bars[k], S, tk, mo['band']) for mo in c.mocs) or OF.bubble_in_place(f.bars[k], S, tk):
                if best is None or v > best[0]:
                    best = (v, k, tk, bs)
    if best:
        v, k, tk, bs = best
        sg['bong'] = (f"bóng {'xanh' if S > 0 else 'đỏ'} {v:.0f} @{_px(tk)} ({v / bs:.1f}× nền)".replace('.', ','), k, tk)
    # ③c kiệt sức phe ngược ở râu, chưa bị quét tới CF
    for k in W:
        r = f.exh[k][0] if S < 0 else f.exh[k][1]
        if not r.hit:
            continue
        if any(OF.is_swept(r.top, r.tick, H[j], L[j], 1) for j in range(k + 1, cf + 1)):
            continue
        side_txt = 'đỉnh (Ask' if r.top else 'đáy (Bid'
        sg['kiet_suc'] = (f"kiệt sức {side_txt} {r.extreme_vol:.0f}) @{_px(r.tick)}", k, r.tick)
        break
    # ③d stacked mới cùng hướng S: Body, không Weak, nến tạo vùng đóng phía S; loại vùng đang làm mốc
    excl = {mo['zid'] for mo in c.mocs if mo['zid'] is not None}
    for k in W:
        for z in f.zones[k]:
            if z.side != S or z.position != OF.POS_BODY or z.weak:
                continue
            lo, hi = round(z.lo / TICK), round(z.hi / TICK)
            if (k, lo, hi) in excl:
                continue
            if (S > 0 and C[k] >= hi) or (S < 0 and C[k] <= lo):
                sg['stacked'] = (f"stacked {'buy' if S > 0 else 'sell'} {z.levels} mức {_px(lo)}–{_px(hi)}", k, lo if S > 0 else hi)
                break
        if 'stacked' in sg:
            break
    # ③e trap phe ngược: quét mốc quan trọng ≥ 1 tick, đóng lại phía S, ô −S trong râu ≥ 3 × nền_ô và ≥ 10
    for k in W:
        bs = f.base[k]
        if not np.isfinite(bs) or bs <= 0:
            continue
        for lvl in c.trap_levels:
            ok, tk, v = OF.trap(f.bars[k], S, lvl, bs, 3.0, 1, cp.bubble_min)
            if ok:
                sg['trap'] = (f"trap quét {_px(lvl)}, bóng {'đỏ' if S > 0 else 'xanh'} {v:.0f} @{_px(tk)}", k, tk)
                break
        if 'trap' in sg:
            break
    # ③f (corven-2, chỉ thế B) trap trong nhịp hồi: ô −S ≥ 3 × nền_ô và ≥ 10 ở nến trước CF trong cửa sổ, CF đóng vượt giá ô đó.
    # Chọn ô lớn nhất; hoà ⇒ nến sớm hơn, rồi giá xa hướng S hơn (buy: giá cao hơn).
    if cp.trap_hoi and c.the == 'B' and 'trap' not in sg:
        best = None
        for k in range(c.w0, cf):
            bs = f.base[k]
            if not np.isfinite(bs) or bs <= 0:
                continue
            for (tk, bv, av, _v) in f.bars[k].levels:
                vol = bv if S > 0 else av
                if vol >= 3.0 * bs - 1e-9 and vol >= cp.bubble_min - 1e-9 and (C[cf] - tk) * S > 0:
                    key = (vol, -k, tk * S)
                    if best is None or key > best[0]:
                        best = (key, k, tk, vol)
        if best:
            _, k, tk, vol = best
            sg['trap'] = (f"trap hồi, bóng {'đỏ' if S > 0 else 'xanh'} {vol:.0f} @{_px(tk)}", k, tk)
    return sg


def eval_order(c: Cand, f: Feat, cp: CP, m: Step2Machine, chong: dict, use_chong: bool = True) -> None:
    """④ + ⛔ cho một CF ứng viên (độc lập với ③). Ghi c.gates (mọi cổng trượt) + entry/SL/TP/R."""
    S, cf = c.S, c.cf
    H, L, O, C, Dl = f.H, f.L, f.O, f.C, f.Dl
    g = []
    mbr = f.mbr[cf]
    # 4a nến xác nhận
    o, h, l, cc = O[cf], H[cf], L[cf], C[cf]
    rng = h - l
    ok = (rng > 0 and (cc - o) * S > 0 and abs(cc - o) >= cp.cf_body * rng - 1e-9
          and ((h - cc) if S > 0 else (cc - l)) <= cp.cf_close_ext * rng + 1e-9
          and rng >= cp.cf_min_rng_mbr * mbr - 1e-9
          and Dl[cf] * S >= 0 and f.medd[cf] == f.medd[cf] and abs(Dl[cf]) >= cp.cf_min_delta * f.medd[cf] - 1e-9)
    if not ok:
        g.append('g4a_cf')
    # ⛔ kiệt sức chống hướng: 5 nến tới CF có kiệt sức phía S (sell: đáy) chưa bị quét tới CF
    for k in range(max(0, cf - cp.veto_window + 1), cf + 1):
        r = f.exh[k][1] if S < 0 else f.exh[k][0]
        if r.hit and not any(OF.is_swept(r.top, r.tick, H[j], L[j], 1) for j in range(k + 1, cf + 1)):
            g.append('v_kiet_suc_chong')
            break
    # ⛔ nhịp đẩy do quét stop (thế B)
    if c.the == 'B' and not cp.bo_quet_stop:
        D = S
        seg = range(c.ref, cf + 1)
        e = max(seg, key=lambda j: (H[j], -j)) if D > 0 else min(seg, key=lambda j: (L[j], j))
        sd = Dl[c.ref:e + 1].sum()
        bad = sd * D <= 0
        if not bad and cf >= e + cp.stop_run_k and np.isfinite(f.base[e]) and f.base[e] > 0:
            cells = OF.bubbles(f.bars[e], -D, f.base[e], cp.bubble_mult, cp.bubble_min)
            if any(OF.bubble_in_place(f.bars[e], -D, tk) for tk, _ in cells):
                bad = True
        if bad:
            g.append('v_quet_stop')
    # ⛔ range chồng range (thế A, A2): chỉ đánh từ FailBreak thứ 2 của range mới
    if use_chong and c.the in ('A', 'A2') and chong.get(c.rid):
        nfb = sum(1 for x in m.fb_bars.get(c.rid, []) if x <= (c.inst.fb if c.the == 'A' else cf))
        if nfb < 2:
            g.append('v_chong_range')
    # 4b SL
    buf = max(cp.sl_buf_ticks, cp.sl_buf_mbr * mbr)
    if c.the == 'A':
        raw = (min(L[c.ref:cf + 1]) - buf) if S > 0 else (max(H[c.ref:cf + 1]) + buf)
        c.moc_used = 'canh'
    elif c.the == 'A2':
        # 7.3.2: cực trị TOÀN BỘ cú thủng (nến đóng ngoài → CF) — bản GĐ1 neo ở râu x (sai với 4b)
        raw = (min(L[c.ref:cf + 1]) - buf) if S > 0 else (max(H[c.ref:cf + 1]) + buf)
        c.moc_used = 'cuc_tri'
    else:
        edge = [mo for mo in c.mocs if mo['kind'] == 'canh']
        if edge:
            mo = edge[0]
            if cp.sl_b_canh_3tick:
                raw = mo['level'] - S * 3     # corven-6: ngay sau cạnh vừa phá ∓ 3 tick, bỏ râu hồi + đệm biên độ
            elif cp.sl_b_canh_sat:
                raw = (min(min(L[c.w0:cf + 1]), mo['level']) - buf) if S > 0 else (max(max(H[c.w0:cf + 1]), mo['level']) + buf)
            elif S > 0:
                raw = min(min(L[c.w0:cf + 1]), mo['level'] - mo['tol']) - buf
            else:
                raw = max(max(H[c.w0:cf + 1]), mo['level'] + mo['tol']) + buf
            c.moc_used = 'canh'
        else:
            mo = max((x for x in c.mocs if x['kind'] == 'stacked'), key=lambda x: x['zid'][0])
            zb, lo, hi = mo['zid']
            raw = (lo - buf) if S > 0 else (hi + buf)
            c.moc_used = f"stacked {_px(lo)}–{_px(hi)}"
    ent = C[cf]
    c.anchor = 'cu_thung'
    if cp.sl_anchor == 'pivot':
        # 7.3.3 "đặt dưới cái đáy mới quét" (CORVEN 0:50:25): pivot 1 nến ngược S gần nhất trong [ref − 10, CF], nằm phía −S
        # của giá vào (sell: đỉnh pivot > giá vào). Không có ⇒ giữ neo cú thủng (ghi c.anchor = 'pivot_fallback').
        piv = m.ph if S < 0 else m.pl
        lo_i = c.ref - cp.piv_back
        pv = None
        for (j, pp) in reversed(piv):
            if j > cf - 1:
                continue
            if j < lo_i:
                break
            if (S < 0 and pp > ent) or (S > 0 and pp < ent):
                pv = (j, pp)
                break
        if pv is not None:
            raw = pv[1] + buf if S < 0 else pv[1] - buf
            c.anchor = 'pivot'
            c.piv = pv
        else:
            c.anchor = 'pivot_fallback'
    risk = (ent - raw) * S
    if risk < cp.sl_floor_mbr * mbr:
        risk = cp.sl_floor_mbr * mbr
    sl = ent - S * risk
    sl = int(np.floor(sl + 1e-9)) if S > 0 else int(np.ceil(sl - 1e-9))
    risk = (ent - sl) * S
    c.entry, c.sl, c.risk = int(ent), sl, float(risk)
    if cp.sl_cap_gia is not None:
        if risk > round(cp.sl_cap_gia / TICK, 6) + 1e-9:
            g.append('tran_sl')
    elif risk > cp.sl_cap_mbr * mbr + 1e-9:
        g.append('tran_sl')
    # 4c mục tiêu
    if c.the in ('A', 'A2'):
        top, bot = c.inst.top, c.inst.bottom
        tgt = bot if S < 0 else top
    else:
        b = c.inst
        hgt = b.top - b.bottom
        t1 = b.E + S * hgt
        t2 = None
        best_d = -1
        for rid2, d in m.death.items():
            if rid2 == b.rid or d > cf or cf - d > cp.dead_look:
                continue
            r2 = m.eng.ranges[rid2]
            if S > 0 and r2.bottom > ent and d > best_d:
                best_d, t2 = d, r2.bottom
            if S < 0 and r2.top < ent and d > best_d:
                best_d, t2 = d, r2.top
        tgt = t1 if t2 is None else (max(t1, t2) if S > 0 else min(t1, t2))
    c.target = float(tgt)
    c.r_avail = (tgt - ent) * S / risk if risk > 0 else -1
    if c.r_avail < cp.r_min - 1e-9 and not (cp.b_bo_rmin and c.the == 'B'):
        g.append('r_nho')
    c.tp = ent + S * cp.tp_r * risk
    # 4d giờ
    if 860 <= f.sm[cf] < 930:
        g.append('chan_1920')
    if cf - f.sstart[cf] < cp.block_first_bars:
        g.append('dau_phien')
    if cf >= f.send[cf]:
        g.append('cuoi_phien')
    c.gates = g


def compute_chong(m: Step2Machine, cp: CP) -> dict:
    """⛔ range chồng range: range sinh trong ≤ 30 nến sau khi một range khác chết và chồng ≥ 50 % chiều cao (range mới)."""
    out = {}
    for rid, bi in m.birth.items():
        r = m.eng.ranges[rid]
        h = r.top0 - r.bottom0
        for rid2, d in m.death.items():
            if rid2 == rid or d > bi or bi - d > cp.overlap_bars:
                continue
            r2 = m.eng.ranges[rid2]
            ov = min(r.top0, r2.top) - max(r.bottom0, r2.bottom)
            if h > 0 and ov >= cp.overlap_frac * h:
                out[rid] = True
                break
    return out


def sign_ok(c: Cand, mode, cp: CP) -> bool:
    if mode == 'main':
        return len(c.types) >= cp.need_signs
    if mode == 'C1':
        return c.the != 'A2'             # bỏ ③; "lần 2" vốn đòi ≥ 2 dấu hiệu nên không có ở C1
    if isinstance(mode, tuple) and mode[0] == 'C3':
        return mode[1] in c.signs and c.the != 'A2'
    raise ValueError(mode)


def sim_one(df: pd.DataFrame, f: Feat, e: dict) -> Optional[pd.Series]:
    """kernel.simulate cho MỘT lệnh, giới hạn tới nến cuối phiên (4d: lệnh còn mở qua khoảng trống > 30′ đóng TIME)."""
    i = int(e['idx'])
    hold = int(f.send[i] - i)
    if hold <= 0:
        return None
    t = K.simulate(df, [e], one_at_a_time=False, max_hold_bars=hold)
    return t.iloc[0] if len(t) else None


def to_entry(c: Cand) -> dict:
    return dict(idx=c.cf, side=c.S, entry=round(c.entry * TICK, 6), sl=round(c.sl * TICK, 6), tp=round(c.tp * TICK, 6),
                setup=c.the, zone=c.moc_used, note=' | '.join(v[0] for t, v in c.signs.items()))


def select_and_simulate(cands: List[Cand], df: pd.DataFrame, f: Feat, cp: CP, mode='main', block_us: Optional[bool] = None,
                        keep=None):
    """4d: 1 lệnh mở; mỗi thế (FailBreak/BreakConfirmed/cú thủng) 1 lệnh; mỗi (range, cạnh, nhóm thế) 1 lệnh.
    Ứng viên xét theo thời gian; ứng viên đầu tiên không bị chặn của một thế được vào. Trả (trades, lý do bị bỏ)."""
    block_us = cp.block_us_open if block_us is None else block_us
    busy = -1
    used_inst, used_key = set(), set()
    rows, chosen, why = [], [], {}
    for c in cands:
        if not f.good[c.cf] or (keep is not None and not keep(c)):
            continue
        if c.the == 'A2' and not cp.a2_on:
            continue
        if (c.the == 'A' and not cp.bat_fail_break) or (c.the == 'B' and not cp.bat_break):
            continue      # công tắc tắt: không vào, không chiếm chỗ lệnh mở
        if not sign_ok(c, mode, cp):
            continue
        gs = [x for x in c.gates if not (x == 'chan_1920' and not block_us)]
        if gs:
            continue
        if c.cf < busy:
            why['dang_co_lenh'] = why.get('dang_co_lenh', 0) + 1
            continue
        if id(c.inst) in used_inst or c.key in used_key:
            why['the_da_co_lenh'] = why.get('the_da_co_lenh', 0) + 1
            continue
        t = sim_one(df, f, to_entry(c))
        if t is None:
            continue
        used_inst.add(id(c.inst))
        used_key.add(c.key)
        busy = int(t['exit_idx'])
        rows.append(t)
        chosen.append(c)
    tr = pd.DataFrame(rows).reset_index(drop=True)
    return tr, chosen, why


def run_gd1(bars, df, good, cp: CP = None):
    """①→④ trên TRAIN. Trả dict(m, feat, cands, chong, use_chong, trades, chosen, why)."""
    cp = cp or CP()
    sess = df['session_no'].to_numpy()
    m = run_step2(bars, sess, cp, good=good)
    feat = Feat(bars, df, m.mbr, cp, good)
    cands = build_candidates(m, feat, cp)
    chong = compute_chong(m, cp)
    # tỷ lệ thế A bị luật chồng range loại (theo thế, phiên dày) — > 30 % ⇒ bỏ luật (plan)
    A = [a for a in m.A if good[a.fb]]
    n_veto = sum(1 for a in A if chong.get(a.rid) and sum(1 for x in m.fb_bars.get(a.rid, []) if x <= a.fb) < 2)
    chong_rate = n_veto / max(1, len(A))
    use_chong = chong_rate <= cp.overlap_max_drop
    for c in cands:
        c.signs = find_signs(c, feat, cp)
        eval_order(c, feat, cp, m, chong, use_chong)
    tr, chosen, why = select_and_simulate(cands, df, feat, cp)
    return dict(m=m, feat=feat, cands=cands, chong=chong, chong_rate=chong_rate, use_chong=use_chong,
                trades=tr, chosen=chosen, why=why, cp=cp, df=df, good=good)


def main_gd0():
    cut = train_cut()
    bars, df = load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    sess = df['session_no'].to_numpy()
    m = run_step2(bars, sess, good=good)
    s = summarize(m, df, good)
    f = signal_frequencies(bars, df, good, m.mbr)
    series = f.pop('_series')
    # dấu hiệu theo ngữ cảnh trên các CF qua ② (delta ngược giá, trap) — chỉ là tần suất, chưa đếm ③
    H = m.eng.H; L = m.eng.L; Dl = [b.delta for b in bars]
    ctx = dict(n_cf=0, div=0, trap=0)
    base = series['base_before']
    for a in m.A:
        if not good[a.fb]:
            continue
        for cf in a.passed:
            ctx['n_cf'] += 1
            ok = False
            for x in range(a.ref, cf + 1):
                hit, _, _ = OF.delta_divergence(H, L, Dl, x, a.S, m.mbr[cf])
                lvl_ok = (H[x] >= a.top - a.tol) if a.S < 0 else (L[x] <= a.bottom + a.tol)
                if hit and lvl_ok:
                    ok = True
                    break
            ctx['div'] += ok
            lvl = a.top if a.E > 0 else a.bottom
            ctx['trap'] += any(OF.trap(bars[x], a.S, lvl, base[x] if np.isfinite(base[x]) else 0)[0] for x in range(a.ref, cf + 1))
    s['dau_hieu_ngu_canh_tren_cf_the_A'] = ctx
    s['tan_suat'] = f
    s['tham_so'] = asdict(CP())
    s['cut_bar_idx'] = cut
    s['cut_datetime'] = str(df['datetime'].iloc[-1])
    os.makedirs(REPORT, exist_ok=True)
    with open(os.path.join(REPORT, '_corven_gd0.json'), 'w', encoding='utf-8') as fh:
        json.dump(s, fh, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    # danh sách thế (để Fable soi chart)
    rows = []
    for a in m.A:
        if good[a.fb]:
            rows.append(dict(the='A', rid=a.rid, canh='tren' if a.E > 0 else 'duoi', huong='sell' if a.S < 0 else 'buy',
                             ref=a.ref, su_kien=a.fb, t_utc=str(df['datetime'].iloc[a.fb]), top=a.top * TICK, bottom=a.bottom * TICK,
                             qua_2=';'.join(str(x) for x in a.passed), loai=a.fail, moc=''))
    for b in m.B:
        if good[b.bc]:
            mo = ';'.join(sorted({f"stacked@{z[1]}:{z[2] * TICK:.1f}-{z[3] * TICK:.1f}" for z in b.passed_zone}))
            rows.append(dict(the='B', rid=b.rid, canh='tren' if b.D > 0 else 'duoi', huong='buy' if b.D > 0 else 'sell',
                             ref=b.ref, su_kien=b.bc, t_utc=str(df['datetime'].iloc[b.bc]), top=b.top * TICK, bottom=b.bottom * TICK,
                             qua_2=';'.join(str(x) for x in sorted(set(b.passed_edge) | {p[0] for p in b.passed_zone})),
                             loai=b.end, moc=('canh' if b.passed_edge else '') + ('+' if b.passed_edge and mo else '') + mo))
    pd.DataFrame(rows).to_csv(os.path.join(REPORT, '_corven_gd0_the.csv'), index=False, encoding='utf-8')
    print(json.dumps({k: v for k, v in s.items() if k != 'theo_ngay'}, ensure_ascii=False, indent=1,
                     default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
    return m, s


if __name__ == '__main__':
    if '--gd0' in sys.argv:
        main_gd0()
    else:
        import results_corven
        results_corven.main()
