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
    b_include_exhausted: bool = False   # BreakConfirmed làm range DEAD ngay (hết lượt ReEntry) có tính thế B không — CHỜ FABLE
    same_session: bool = True      # cửa sổ / CF không vắt qua khoảng trống phiên (> 30′) — CHỜ FABLE


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


@dataclass
class ExcA:
    rid: int
    p: int                 # hướng cú thủng (−1 thủng xuống ⇒ vào buy)
    breach_start: int
    bar: int
    ext: int
    close: int


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
        # trạng thái các range TRƯỚC nến i (cho ngoại lệ "xác nhận lần 2")
        pre = [(r.id, r.state, r.pend_side if r.state == PENDING else r.break_side,
                r.pend_start if r.state == PENDING else r.break_idx) for r in e.live if r.state in (PENDING, BROKEN)]
        n_ev = len(e.events)
        e.feed_ticks(bar.o, bar.h, bar.l, bar.c)
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
            if ev.kind == 'FailBreak':
                back_active = r.state == ACTIVE and not any(x.kind == 'CloseOutside' and x.bar == i for x in ev_by_rid[ev.rid])
                if not back_active:
                    self.a_whipsaw += 1
                    continue
                a = InstA(rid=ev.rid, E=ev.side, S=-ev.side, ref=ev.ref, fb=i, top=ev.top, bottom=ev.bottom, tol=r.tol)
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
                    if not self.cp.b_include_exhausted:
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
                self._b_eval(b, i)

        # ---------- ngoại lệ "xác nhận lần 2" (chỉ ĐẾM ứng viên giá; ≥ 2 dấu hiệu là ③) ----------
        for (rid, st, p, start) in pre:
            if p == 0 or start < 0 or (rid, start) in self._exc_done:
                continue
            r = e.ranges[rid]
            if i - 1 < start:
                continue
            if p < 0:
                ext = min(L[start:i])
                if bar.l <= ext - 1 and bar.c >= ext + r.tol and bar.c < r.bottom:
                    self.EXC.append(ExcA(rid, p, start, i, ext, bar.c))
                    self._exc_done.add((rid, start))
            else:
                ext = max(H[start:i])
                if bar.h >= ext + 1 and bar.c <= ext - r.tol and bar.c > r.top:
                    self.EXC.append(ExcA(rid, p, start, i, ext, bar.c))
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
            push_wick = OF.POS_UPPER if b.D > 0 else OF.POS_LOWER
            if zz.position not in (OF.POS_BODY, push_wick):
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
        if any(x.kind == 'ReEntry' for x in evs):
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
        elif lvl is not None:
            if (b.D < 0 and C[i] > lvl) or (b.D > 0 and C[i] < lvl):
                b.suspended = True
                b.n_suspend += 1
                b.broken_at = i
        b.push_ext = max(b.push_ext, H[i]) if b.D > 0 else min(b.push_ext, L[i])
        if not b.suspended:
            self._b_eval(b, i)
        elif self.good is None or self.good[i]:
            self.cnt['b_bar_tam_huy_1c'] += 1

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
        # --- mốc stacked mới cùng hướng D ---
        tz = self.tol_now(j)
        pz = False
        why = []
        for z in b.zones:
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
                b.passed_zone.append((j, z['bar'], z['lo'], z['hi']))
                pz = True
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


def main():
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
    main()
