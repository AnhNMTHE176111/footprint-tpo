# -*- coding: utf-8 -*-
"""
follow_combo.py — đo các combo "Follow sau cú phá" (plans/BENZO-FOLLOW-COMBO-plan.md, bản đăng ký trước ee8b252).

GĐ-F0 + GĐ-F1: máy trạng thái move → nhịp hồi → CF Follow (2a–2c), cờ dấu hiệu (2d), lệnh (2e), 10 combo (3),
đối chứng C1/C2 + kiểm hoán vị thống kê cực đại (4), xuất RESULTS-FOLLOW.md + CSV (6).

⛔ CHỈ TRAIN: dữ liệu nạp qua setup_corven.load_train — file nến bị cắt tại nến cuối phiên 2026-09-15 TRƯỚC khi tính bất cứ
gì; không có cờ nào mở TEST trong file này.
Không sửa setup_corven.py / of_signals.py / controls_corven.py — chỉ import.

Chạy:  PYTHONIOENCODING=utf-8 python follow_combo.py        (≈ 3–5 phút)
Mọi giá trong máy là SỐ TICK nguyên (0,1); mbr / tol theo tick.
"""
from __future__ import annotations

import os
import sys
from collections import Counter
from dataclasses import dataclass, field, replace
from types import SimpleNamespace
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'quantower-range', 'research'))

import of_signals as OF                                # noqa: E402

REPORT = os.path.join(HERE, 'report')
TICK = 0.1
EPS = 1e-9

FLAGS = ('T', 'Bc', 'K', 'S', 'Dh', 'Dc', 'Sh', 'Mv')
COMBOS = ('F0', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10')
SEL_COMBOS = COMBOS[1:]                                # 10 combo có sức chọn
COMBO_NAME = dict(F0='nền = C1', F1='nguyên thủy (T)', F2='bóng CF (Bc)', F3='kiệt sức hồi (K)', F4='trap + bóng CF (T∧Bc)',
                  F5='trap + kiệt sức (T∧K)', F6='stacked giữ (S)', F7='Δ ngược hồi (Dh)', F8='hồi nông + lực CF (Sh∧(Bc∨Dc))',
                  F9='move mạnh + 1 dấu hiệu (Mv∧(T∨Bc∨K∨S))', F10='≥ 2 dấu hiệu khác loại {T,Bc,K,S,Dh}')


# =====================================================================================================
# THAM SỐ — đóng băng theo plan; biến thể báo cáo chỉ đổi cf_within / cf_mode / neo SL / gate17
# =====================================================================================================
@dataclass
class FP:
    cf_within: int = 3            # 2b: CF ở nến ≤ x + 3 (biến thể {4} chỉ báo cáo)
    cf_mode: str = 'loose'        # 2c: 'loose' (chính) | 'strict' (đóng > high nhịp hồi) | '4a' (CF thoả 4a đầy đủ)
    move_mbr: float = 1.0         # 2a: high[x] − E ≥ 1,0 mbr
    max_legs: int = 2             # 2a: tối đa 2 leg / cú phá
    age: int = 30                 # 2a: tuổi 30 nến kể từ nến đóng ngoài
    k_fail: int = 3               # K của RangeEngine (chỉ để gắn nhãn FailBreak / ReEntry khi đếm)
    shallow: float = 0.5          # 2b nhãn Sh
    deep: float = 0.7             # 2b nhãn deep
    bub_mult: float = 3.0         # T / Bc: ô ≥ 3 × nền_ô …
    bub_min: float = 10.0         # … và ≥ 10 hợp đồng
    dc_mult: float = 2.0          # Dc: Δ[c] ≥ 2 medΔ
    mv_sum: float = 3.0           # Mv: ΣΔ(ref…x) ≥ 3 medΔ
    mv_body: float = 0.7          # Mv: hoặc nến thân ≥ 0,7 biên độ …
    mv_delta: float = 2.0         # … và |Δ| ≥ 2 medΔ
    cf4a_body: float = 0.4        # nhãn cf_4a (= 4a plan chính)
    cf4a_ext: float = 0.3
    cf4a_rng: float = 0.5
    cf4a_delta: float = 0.5
    sl_buf_ticks: float = 3.0     # 2e: đệm = max(3 tick, 0,2 mbr)
    sl_buf_mbr: float = 0.2
    sl_floor_mbr: float = 1.0
    sl_cap_mbr: float = 4.0
    tp_r: float = 2.0
    r17: float = 1.7              # biến thể gate17
    block_us: bool = True         # chặn 19:20–20:30 VN (sm 860–930)
    first_bars: int = 15


# =====================================================================================================
# MÁY TRẠNG THÁI 2a–2c
# =====================================================================================================
@dataclass
class Brk:
    rid: int
    D: int
    E: int
    top: int
    bottom: int
    tol: float
    ref: int
    exhausted: bool = False       # cú phá này nếu giữ được sẽ là lần phá thật thứ 3 (range DEAD ngay — b_from_exhausted)
    leg: int = 1
    x: int = -1
    active: bool = True           # leg hiện tại còn chờ CF
    chain: bool = True            # các nến x+1… đều là nến hồi
    pb: list = field(default_factory=list)
    trig: Optional[int] = None    # cực trị của leg đã xong — leg 2 phải vượt mức này
    valid_seen: bool = False
    pb_seen: bool = False
    alive: bool = True
    end: str = ''


class FollowMachine:
    """Nuôi từng nến đã đóng. `f` = đặc trưng (H, L, O, C, Dl, mbr, medd, base, exh, zones, sstart).
    on_bar(i, evs, info): evs = sự kiện RangeEngine của nến i; info[(i, rid)] = dict(tol, exhausted) cho CloseOutside."""

    def __init__(self, f, fp: FP = None):
        self.f = f
        self.fp = fp or FP()
        self.live: List[Brk] = []
        self.all: List[Brk] = []
        self.rows: List[dict] = []
        self.cnt = Counter()
        self.legs: List[dict] = []          # mỗi leg: dict(brk, leg, valid, pb, cf, end, ref_bar)

    # ---------------- tiện ích
    def _X(self, D, i):
        return int(self.f.H[i]) if D > 0 else int(self.f.L[i])

    def _more(self, D, a, b):
        """a cực trị hơn b theo hướng D."""
        return (a - b) * D > 0

    def _same(self, a, b):
        return self.f.sstart[a] == self.f.sstart[b]

    def _move_ok(self, b: Brk) -> bool:
        f = self.f
        mh = (self._X(b.D, b.x) - b.E) * b.D
        sd = float(np.sum(f.Dl[b.ref:b.x + 1])) * b.D
        return mh >= self.fp.move_mbr * f.mbr[b.x] - EPS and sd > 0

    def _is_pb(self, b: Brk, i: int) -> bool:
        f = self.f
        return (not self._more(b.D, self._X(b.D, i), self._X(b.D, b.x))) and (int(f.C[i]) - int(f.C[b.x])) * b.D < 0

    def _cf_ok(self, b: Brk, c: int) -> bool:
        f = self.f
        D = b.D
        o, h, l, cl = int(f.O[c]), int(f.H[c]), int(f.L[c]), int(f.C[c])
        pbc = [int(f.C[j]) for j in b.pb]
        lim = max(pbc) if D > 0 else min(pbc)
        ok = (cl - o) * D > 0 and f.Dl[c] * D > 0 and (cl - lim) * D > 0
        if not ok:
            return False
        if self.fp.cf_mode == 'strict':
            ext = max(int(f.H[j]) for j in b.pb) if D > 0 else min(int(f.L[j]) for j in b.pb)
            return (cl - ext) * D > 0
        if self.fp.cf_mode == '4a':
            return self._cf4a(c, D)
        return True

    def _cf4a(self, c: int, D: int) -> bool:
        f, p = self.f, self.fp
        o, h, l, cl = int(f.O[c]), int(f.H[c]), int(f.L[c]), int(f.C[c])
        rng = h - l
        md = f.medd[c]
        return bool(rng > 0 and (cl - o) * D > 0 and abs(cl - o) >= p.cf4a_body * rng - EPS
                    and ((h - cl) if D > 0 else (cl - l)) <= p.cf4a_ext * rng + EPS
                    and rng >= p.cf4a_rng * f.mbr[c] - EPS and f.Dl[c] * D >= 0 and md == md
                    and abs(f.Dl[c]) >= p.cf4a_delta * md - EPS)

    def _deep_dead(self, b: Brk) -> bool:
        f = self.f
        if b.D > 0:
            return min(int(f.L[j]) for j in b.pb) < b.E - b.tol - EPS
        return max(int(f.H[j]) for j in b.pb) > b.E + b.tol + EPS

    def _leg_rec(self, b: Brk, end: str, cf: int = -1):
        self.legs.append(dict(rid=b.rid, D=b.D, ref=b.ref, leg=b.leg, x=b.x, valid=b.valid_seen, pb=b.pb_seen,
                              cf=cf, end=end))

    def _start_leg(self, b: Brk, i: int, leg: int):
        b.leg, b.x, b.active, b.chain, b.pb = leg, i, True, True, []
        b.valid_seen = self._move_ok(b)
        b.pb_seen = False

    def _consume(self, b: Brk, i: int, why: str, cf: int = -1):
        self._leg_rec(b, why, cf)
        b.active = False
        b.trig = self._X(b.D, b.x)

    def _end(self, b: Brk, why: str):
        if b.active:
            self._leg_rec(b, 'huy_' + why)
            b.active = False
        b.alive = False
        b.end = why
        if b in self.live:
            self.live.remove(b)

    # ---------------- một nến
    def on_bar(self, i: int, evs: list, info: Optional[dict] = None):
        f = self.f
        info = info or {}
        merged = {ev.rid for ev in evs if ev.kind == 'Merge'}
        for b in list(self.live):
            if not self._same(i, b.ref):
                self._end(b, 'het_phien'); continue
            if i - b.ref > self.fp.age:
                self._end(b, 'het_tuoi'); continue
            if (int(f.C[i]) - b.E) * b.D <= 0:          # đóng lại trong range (FailBreak trong K nến / ReEntry sau đó)
                self._end(b, 'failbreak' if i - b.ref <= self.fp.k_fail else 'reentry'); continue
            if b.rid in merged:
                self._end(b, 'merge'); continue
            self._step(b, i)
        for ev in evs:
            if ev.kind != 'CloseOutside':
                continue
            inf = info.get((i, ev.rid), {})
            D = ev.side
            E = int(ev.top) if D > 0 else int(ev.bottom)
            b = Brk(rid=ev.rid, D=D, E=E, top=int(ev.top), bottom=int(ev.bottom), tol=float(inf.get('tol', 0.0)), ref=i,
                    exhausted=bool(inf.get('exhausted', False)))
            self._start_leg(b, i, 1)
            self.all.append(b)
            self.live.append(b)

    def _step(self, b: Brk, i: int):
        X = self._X(b.D, i)
        if b.active:
            k = i - b.x
            if b.chain and b.pb and 2 <= k <= self.fp.cf_within and self._cf_ok(b, i):
                ok = self._move_ok(b)
                if ok:
                    self.rows.append(self._emit(b, i))
                self._consume(b, i, 'cf' if ok else 'cf_move_khong_hop_le', i)
                if b.leg < self.fp.max_legs and self._more(b.D, X, b.trig):
                    self._start_leg(b, i, b.leg + 1)
                return
            if self._more(b.D, X, self._X(b.D, b.x)):     # cực trị mới trước khi có CF ⇒ cú đẩy kéo dài, cùng leg
                b.x, b.chain, b.pb = i, True, []
                b.valid_seen = b.valid_seen or self._move_ok(b)
                return
            if b.chain and self._is_pb(b, i):
                b.pb.append(i)
                if self._move_ok(b):
                    b.pb_seen = True
                if self._deep_dead(b):
                    self._consume(b, i, 'hoi_qua_sau')
                    return
            else:
                b.chain = False
            if k >= self.fp.cf_within:
                self._consume(b, i, 'het_han')
            return
        # leg đã xong: chờ cực trị mới vượt cực trị leg trước ⇒ leg 2
        if b.leg >= self.fp.max_legs:
            self._end(b, 'het_leg')
            return
        if self._more(b.D, X, b.trig):
            self._start_leg(b, i, b.leg + 1)

    # ---------------- 2d cờ + 2e lệnh
    def _emit(self, b: Brk, c: int) -> dict:
        f, p = self.f, self.fp
        D, x, pb = b.D, b.x, list(b.pb)
        H, L, O, C, Dl = f.H, f.L, f.O, f.C, f.Dl
        bars = f.bars
        move_h = (self._X(D, x) - b.E) * D
        ext_pb = min(int(L[j]) for j in pb) if D > 0 else max(int(H[j]) for j in pb)
        depth = (self._X(D, x) - ext_pb) * D
        r = dict(idx_ref=b.ref, idx_x=x, idx_c=c, leg=b.leg, D=D, E=b.E, top=b.top, bottom=b.bottom, range_id=b.rid,
                 b_from_exhausted=int(b.exhausted), n_hoi=len(pb), move_h=move_h, depth=depth,
                 move_h_mbr=round(move_h / f.mbr[c], 3), depth_frac=round(depth / move_h, 3) if move_h > 0 else np.nan,
                 deep=int(depth > p.deep * move_h + EPS))
        # ---- Hc (plan 10.2-1 / 10.3-1, hậu kiểm): nhịp hồi x+1…c−1 chạm cạnh E trong tol = max(2 tick, 0,5 mbr) tại c
        tol_hc = max(2.0, 0.5 * f.mbr[c])
        r['Hc'] = int((ext_pb - b.E) * D <= tol_hc + EPS)
        r['hc_ext_mbr'] = round((b.E - ext_pb) * D / f.mbr[c], 3) if f.mbr[c] > 0 else np.nan
        # ---- cột giả thuyết H1 / H3 (plan 10.3-2; H2 = risk_gia ghi sau phần lệnh)
        r['cf_body'] = round(abs(int(C[c]) - int(O[c])) / max(int(H[c]) - int(L[c]), 1), 4)
        r['move_x_rng'] = round(move_h / max(b.top - b.bottom, 1), 4)
        # ---- T: trap phe ngược ở nhịp hồi (ô −D ở nửa phía D của nến hồi, CF đóng vượt ô)
        best = None
        for j in pb:
            bs = f.base[j]
            if not np.isfinite(bs) or bs <= 0:
                continue
            mid = (int(H[j]) + int(L[j])) / 2.0
            for (tk, v) in OF.bubbles(bars[j], -D, bs, p.bub_mult, p.bub_min):
                half = tk >= mid - EPS if D > 0 else tk <= mid + EPS
                if half and (int(C[c]) - tk) * D > 0 and (best is None or v / bs > best[0]):
                    best = (v / bs, j, tk, v)
        r['T'] = int(best is not None)
        r['T_nen'], r['T_gia'], r['T_vol'], r['T_x_nen'] = (best[1], best[2] * TICK, best[3], round(best[0], 2)) if best else (-1, np.nan, np.nan, np.nan)
        # ---- Bc: bóng phe D ở nửa phía ngược của CF
        best = None
        bs = f.base[c]
        if np.isfinite(bs) and bs > 0:
            for (tk, v) in OF.bubbles(bars[c], D, bs, p.bub_mult, p.bub_min):
                if OF.bubble_in_place(bars[c], D, tk) and (best is None or v > best[1]):
                    best = (tk, v)
        r['Bc'] = int(best is not None)
        r['Bc_gia'], r['Bc_vol'], r['Bc_x_nen'] = (best[0] * TICK, best[1], round(best[1] / bs, 2)) if best else (np.nan, np.nan, np.nan)
        # ---- K: kiệt sức phe ngược ở đáy hồi (D>0: kiệt sức ĐÁY) tại nến hồi hoặc c, chưa bị quét tới c
        kk = None
        for j in pb + [c]:
            ex = f.exh[j][1] if D > 0 else f.exh[j][0]
            if ex.hit and not any(OF.is_swept(ex.top, ex.tick, int(H[q]), int(L[q]), 1) for q in range(j + 1, c + 1)):
                kk = (j, ex)
                break
        r['K'] = int(kk is not None)
        r['K_nen'], r['K_gia'], r['K_vol'] = (kk[0], kk[1].tick * TICK, kk[1].extreme_vol) if kk else (-1, np.nan, np.nan)
        # ---- S: stacked phe D sinh trong move, nhịp hồi chạm [Lo − tol, Hi + tol], không nến nào đóng xuyên mép
        tol_c = max(2.0, 0.5 * f.mbr[c])
        sz = None
        for k in range(b.ref, x + 1):
            for z in f.zones[k]:
                if z.side != D or z.position != OF.POS_BODY or z.weak:
                    continue
                lo, hi = round(z.lo / TICK), round(z.hi / TICK)
                touch = any(int(H[j]) >= lo - tol_c - EPS and int(L[j]) <= hi + tol_c + EPS for j in pb)
                thru = any((int(C[j]) < lo) if D > 0 else (int(C[j]) > hi) for j in pb + [c])
                if touch and not thru:
                    sz = (k, lo, hi, z.levels)
        r['S'] = int(sz is not None)
        r['S_nen'], r['S_lo'], r['S_hi'] = (sz[0], sz[1] * TICK, sz[2] * TICK) if sz else (-1, np.nan, np.nan)
        # ---- Dh / Dc / Sh / Mv
        sd_pb = float(np.sum(Dl[pb]))
        r['sumD_hoi'] = sd_pb
        r['Dh'] = int(sd_pb * D > 0)
        md = f.medd[c]
        r['dc_x_med'] = round(abs(Dl[c]) / md, 2) if md > 0 else np.nan
        r['Dc'] = int(md > 0 and Dl[c] * D >= p.dc_mult * md - EPS)
        r['Sh'] = int(depth <= p.shallow * move_h + EPS)
        sd_mv = float(np.sum(Dl[b.ref:x + 1])) * D
        mdx = f.medd[x]
        strong = mdx > 0 and sd_mv >= p.mv_sum * mdx - EPS
        if not strong:
            for k in range(b.ref, x + 1):
                rg = int(H[k]) - int(L[k])
                if rg > 0 and abs(int(C[k]) - int(O[k])) >= p.mv_body * rg - EPS and f.medd[k] > 0 \
                        and abs(Dl[k]) >= p.mv_delta * f.medd[k] - EPS:
                    strong = True
                    break
        r['sumD_move'] = sd_mv * D
        r['Mv'] = int(bool(strong))
        # ---- Vk (veto): kiệt sức phe D ở đỉnh move (D>0: kiệt sức ĐỈNH) tại x hoặc nến hồi, chưa bị quét tới c
        vk = None
        for j in [x] + pb:
            ex = f.exh[j][0] if D > 0 else f.exh[j][1]
            if ex.hit and not any(OF.is_swept(ex.top, ex.tick, int(H[q]), int(L[q]), 1) for q in range(j + 1, c + 1)):
                vk = (j, ex)
                break
        r['Vk'] = int(vk is not None)
        r['Vk_nen'] = vk[0] if vk else -1
        # ---- nhãn CF
        r['cf_4a'] = int(self._cf4a(c, D))
        ext_hi = max(int(H[j]) for j in pb) if D > 0 else min(int(L[j]) for j in pb)
        r['cf_strict'] = int((int(C[c]) - ext_hi) * D > 0)
        # ---- 2e lệnh: S2 (chính), S1 (báo cáo)
        mbr = f.mbr[c]
        buf = max(p.sl_buf_ticks, p.sl_buf_mbr * mbr)
        ent = int(C[c])
        seg = pb + [c]
        ext_seg = min(int(L[j]) for j in seg) if D > 0 else max(int(H[j]) for j in seg)
        raw2 = (min(b.E, ext_seg) - buf) if D > 0 else (max(b.E, ext_seg) + buf)
        raw1 = (ext_seg - buf) if D > 0 else (ext_seg + buf)
        # S3 (biến thể báo cáo, plan 9.1-4, hậu kiểm): leg 1 = S2; leg 2 = neo cực trị leg 1 (b.trig, chốt khi leg 1 kết thúc)
        if b.leg >= 2 and b.trig is not None:
            raw3 = (min(int(b.trig), ext_seg) - buf) if D > 0 else (max(int(b.trig), ext_seg) + buf)
        else:
            raw3 = raw2
        hgt = b.top - b.bottom
        tgt = b.E + D * hgt
        for nm, raw in (('S2', raw2), ('S1', raw1), ('S3', raw3)):
            risk = (ent - raw) * D
            if risk < p.sl_floor_mbr * mbr:
                risk = p.sl_floor_mbr * mbr
            sl = ent - D * risk
            sl = int(np.floor(sl + EPS)) if D > 0 else int(np.ceil(sl - EPS))
            risk = (ent - sl) * D
            r[f'sl_{nm}'] = sl
            r[f'risk_{nm}'] = float(risk)
            r[f'tp_{nm}'] = ent + D * p.tp_r * risk
            r[f'cap_{nm}'] = int(risk > p.sl_cap_mbr * mbr + EPS)
            r[f'r17_{nm}'] = int(risk > 0 and (tgt - ent) * D / risk >= p.r17 - EPS)
        r['risk_gia'] = r['risk_S2'] / 10.0
        r['entry'] = ent
        r['mbr_c'] = float(mbr)
        r['chan_1920'] = int(860 <= f.sm[c] < 930)
        r['dau_phien'] = int(c - f.sstart[c] < p.first_bars)
        r['cuoi_phien'] = int(c >= f.send[c])
        return r


def combo_mask(d: pd.DataFrame) -> Dict[str, np.ndarray]:
    """Bảng combo mục 3 trên các F0 (người gọi tự lọc Vk)."""
    g = {k: d[k].to_numpy().astype(bool) for k in FLAGS}
    n2 = g['T'].astype(int) + g['Bc'] + g['K'] + g['S'] + g['Dh']
    return dict(F0=np.ones(len(d), bool), F1=g['T'], F2=g['Bc'], F3=g['K'], F4=g['T'] & g['Bc'], F5=g['T'] & g['K'], F6=g['S'],
                F7=g['Dh'], F8=g['Sh'] & (g['Bc'] | g['Dc']), F9=g['Mv'] & (g['T'] | g['Bc'] | g['K'] | g['S']), F10=n2 >= 2)


# ---- plan mục 10 (hậu kiểm sau mổ SL vòng 1): F7b = Dh ∧ ¬Hc (có sức chọn ⇒ vào family hoán vị 11); 3 dòng còn lại chỉ báo cáo
POST_SEL = ('F7b',)
POST_REP = ('F7Hc', 'F10nHc', 'F0nHc')
FAM11 = SEL_COMBOS + POST_SEL
ALL_POST = COMBOS + POST_SEL + POST_REP
COMBO_NAME.update(F7b='Dh ∧ ¬Hc (hậu kiểm)', F7Hc='F7 ∧ Hc (đối chiếu cơ chế)', F10nHc='F10 ∧ ¬Hc (báo cáo)', F0nHc='F0 ∧ ¬Hc (báo cáo)')
HYP = (('H1', 'cf_body', '<', 0.4, 'thân CF < 0,4'), ('H2', 'risk_gia', '>=', 7.0, 'rủi ro S2 ≥ 7 giá'),
       ('H3', 'move_x_rng', '>=', 2.0, 'move_h ≥ 2 × chiều cao range'))


def post_mask(d: pd.DataFrame) -> Dict[str, np.ndarray]:
    m = dict(combo_mask(d))
    hc = d['Hc'].to_numpy().astype(bool)
    m.update(F7b=m['F7'] & ~hc, F7Hc=m['F7'] & hc, F10nHc=m['F10'] & ~hc, F0nHc=~hc)
    return m


# =====================================================================================================
# CHẠY TRÊN DỮ LIỆU
# =====================================================================================================
def feed_engine(bars):
    """Chạy RangeEngine nguyên trạng; trả (eng, evs_by_bar, info, mbr)."""
    from range_proto import Params, RangeEngine, PENDING
    eng = RangeEngine(Params(), TICK)
    evs_by_bar, info, mbr = [], {}, []
    for b in bars:
        n0 = len(eng.events)
        nb_before = {r.id: r.n_break for r in eng.live}
        eng.feed_ticks(b.o, b.h, b.l, b.c)
        mbr.append(eng.mbr)
        evs = eng.events[n0:]
        evs_by_bar.append(evs)
        for ev in evs:
            if ev.kind == 'CloseOutside':
                r = eng.ranges[ev.rid]
                nb = nb_before.get(ev.rid, r.n_break)
                info[(b.idx, ev.rid)] = dict(tol=r.tol, exhausted=(eng.p.MaxReEntry >= 0 and nb + 1 > eng.p.MaxReEntry))
    return eng, evs_by_bar, info, mbr


def run_machine(f, evs_by_bar, info, fp: FP) -> FollowMachine:
    m = FollowMachine(f, fp)
    for i, evs in enumerate(evs_by_bar):
        m.on_bar(i, evs, info)
    for b in list(m.live):
        m._end(b, 'het_file')
    return m


def to_entry(r: dict, nm: str = 'S2') -> dict:
    return dict(idx=int(r['idx_c']), side=int(r['D']), entry=round(r['entry'] * TICK, 6), sl=round(r[f'sl_{nm}'] * TICK, 6),
                tp=round(r[f'tp_{nm}'] * TICK, 6), setup='Follow', zone='', note='')


def sfx(nm: str) -> str:
    return '' if nm == 'S2' else '_' + nm


def simulate_alone(d: pd.DataFrame, df, f, sim_one, nm: str = 'S2') -> pd.DataFrame:
    """Mô phỏng ĐỘC LẬP từng F0 (không one_at_a_time) — cột r_alone/outcome_alone/exit_alone theo neo nm."""
    rr, oo, xx = [], [], []
    for _, r in d.iterrows():
        t = sim_one(df, f, to_entry(r, nm))
        if t is None:
            rr.append(np.nan); oo.append('NONE'); xx.append(-1)
        else:
            rr.append(float(t['r'])); oo.append(t['outcome']); xx.append(int(t['exit_idx']))
    d = d.copy()
    suf = sfx(nm)
    d['r_alone' + suf] = rr
    d['outcome_alone' + suf] = oo
    d['exit_alone' + suf] = xx
    return d


def tradeable(d: pd.DataFrame, nm='S2', block_us=True, gate17=False) -> np.ndarray:
    ok = (d['good'].to_numpy().astype(bool) & (d['Vk'].to_numpy() == 0) & (d[f'cap_{nm}'].to_numpy() == 0)
          & (d['dau_phien'].to_numpy() == 0) & (d['cuoi_phien'].to_numpy() == 0))
    if block_us:
        ok &= d['chan_1920'].to_numpy() == 0
    if gate17:
        ok &= d[f'r17_{nm}'].to_numpy() == 1
    suf = sfx(nm)
    ok &= np.isin(d['outcome_alone' + suf].to_numpy(), ['TP', 'SL', 'TIME'])
    return ok


def select(d: pd.DataFrame, mask: np.ndarray, nm='S2') -> pd.DataFrame:
    """2e: 1 lệnh mở (vào được khi idx ≥ exit của lệnh trước) · 1 lệnh / (range, cạnh, leg). d đã sắp theo idx_c."""
    suf = sfx(nm)
    busy = -1
    used = set()
    keep = []
    for k, r in enumerate(d.itertuples(index=False)):
        if not mask[k]:
            continue
        c = int(r.idx_c)
        if c < busy:
            continue
        key = (int(r.range_id), int(r.D), int(r.leg))
        if key in used:
            continue
        used.add(key)
        busy = int(getattr(r, 'exit_alone' + suf))
        keep.append(k)
    return d.iloc[keep].copy()


# =====================================================================================================
# THỐNG KÊ + HOÁN VỊ
# =====================================================================================================
def stats_r(r: np.ndarray, n_days: int, seed: int = 0) -> dict:
    r = np.asarray(r, float)
    n = len(r)
    if n == 0:
        return dict(n=0)
    rng = np.random.default_rng(seed)
    bs = rng.choice(r, size=(10000, n), replace=True).mean(axis=1)
    cum = np.cumsum(r)
    dd = float(np.max(np.maximum.accumulate(np.r_[0, cum]) - np.r_[0, cum]))
    streak = best = 0
    for x in r:
        streak = streak + 1 if x <= 0 else 0
        best = max(best, streak)
    return dict(n=n, per_day=n / n_days, wr=float((r > 0).mean()), avg=float(r.mean()), lo=float(np.percentile(bs, 2.5)),
                hi=float(np.percentile(bs, 97.5)), sum=float(r.sum()), dd=dd, streak=best)


def perm_test(M: np.ndarray, r: np.ndarray, groups: np.ndarray, n_perm: int = 2000, seed: int = 0):
    """4.4 — hoán vị NGUYÊN DÒNG cờ (≡ dòng thành viên combo M, N×k) trong từng phiên; thống kê = mean_r(combo) − mean_r(tất cả).
    Trả (obs[k], perm[n_perm, k] (nan nếu combo rỗng), maxs[n_perm])."""
    M = np.asarray(M, bool)
    r = np.asarray(r, float)
    base = r.mean()
    cnt = M.sum(0)
    with np.errstate(invalid='ignore', divide='ignore'):
        obs = (M.T.astype(float) @ r) / np.where(cnt > 0, cnt, np.nan) - base
    rng = np.random.default_rng(seed)
    idx_groups = [np.flatnonzero(groups == g) for g in np.unique(groups)]
    perm = np.full((n_perm, M.shape[1]), np.nan)
    for t in range(n_perm):
        idx = np.empty(len(r), int)
        for ig in idx_groups:
            idx[ig] = rng.permutation(ig)
        Mp = M[idx]                    # dòng cờ của F0 idx[i] gán cho F0 i
        with np.errstate(invalid='ignore', divide='ignore'):
            perm[t] = (Mp.T.astype(float) @ r) / np.where(cnt > 0, cnt, np.nan) - base
    maxs = np.nanmax(perm, axis=1)
    return obs, perm, maxs


def perm_pvalues(obs, perm, maxs):
    p_raw = np.array([float(np.mean(perm[:, k] >= obs[k] - EPS)) if obs[k] == obs[k] else np.nan for k in range(len(obs))])
    p_max = np.array([float(np.mean(maxs >= obs[k] - EPS)) if obs[k] == obs[k] else np.nan for k in range(len(obs))])
    return p_raw, p_max


def judge(s: dict, c1: float, c2: Optional[float], half1: float, half2: float, obs: float, thr: float) -> dict:
    """4.5 vòng trong · 4.6 ĐẠT. Trả dict(inner, dat, ly_do)."""
    n = s.get('n', 0)
    if n < 30:
        return dict(inner=False, dat=False, ly_do='n < 30 — không đo được')
    c2v = -np.inf if c2 is None else c2
    inner = s['avg'] >= c1 - EPS and s['avg'] >= c2v - EPS
    why = []
    if s['avg'] < c1 + 0.15 - EPS:
        why.append('< C1+0,15')
    if s['avg'] < c2v + 0.15 - EPS:
        why.append('< C2+0,15')
    if not s['lo'] > -0.10:
        why.append('KTC dưới ≤ −0,10')
    if not (half1 > 0 and half2 > 0):
        why.append('không dương cả 2 nửa')
    if not (obs == obs and obs > thr):
        why.append('không vượt ngưỡng hoán vị')
    return dict(inner=bool(inner), dat=not why, ly_do='; '.join(why) if why else 'ĐẠT')


def add_halves(d: pd.DataFrame, sess_good) -> pd.DataFrame:
    """Nửa 1 / nửa 2 theo phiên dày (TRAIN 35 phiên ⇒ 18 / 17, đúng như main)."""
    sess_good = sorted(sess_good)
    k1 = (len(sess_good) + 1) // 2
    half_of = {s: (1 if k < k1 else 2) for k, s in enumerate(sess_good)}
    d = d.copy()
    d['half'] = d['phien'].map(half_of).fillna(0).astype(int)
    return d


def eval_post(d: pd.DataFrame, f, df, fp: FP, nd: int, n_perm: int = 2000, seed: int = 0) -> dict:
    """Plan 10.3-1/2 — đúng pipeline bảng chính (S2 · TP 2R · one_at_a_time · 1 lệnh/(range, cạnh, leg) · C1 · C1 F0∖combo · C2' ·
    nửa 1/2 · hoán vị) cho F0…F10 + F7b (family hoán vị 11 combo) + 3 dòng báo cáo; bảng H1–H3; kiểm F7b theo 10.2-1.
    Dùng chung cho follow_combo.main (TRAIN) và follow_newdata.py (dữ liệu ≥ 22/10)."""
    ok = tradeable(d, 'S2')
    masks = post_mask(d)
    sub = np.flatnonzero(ok)
    cols = FAM11 + POST_REP
    M = np.column_stack([masks[k][sub] for k in cols])
    rr = d['r_alone'].to_numpy()[sub]
    grp = d['phien'].to_numpy()[sub]
    obs, perm, _ = perm_test(M, rr, grp, n_perm=n_perm, seed=seed)
    nf = len(FAM11)
    n_alone = M.sum(0)
    big = n_alone[:nf] >= 30
    maxs = np.nanmax(perm[:, :nf], axis=1) if len(sub) else np.full(n_perm, np.nan)
    thr = float(np.nanpercentile(maxs, 95)) if np.isfinite(maxs).any() else np.nan
    maxs30 = np.nanmax(perm[:, :nf][:, big], axis=1) if big.any() else np.full(n_perm, np.nan)
    thr30 = float(np.percentile(maxs30, 95)) if big.any() else np.nan
    p_raw = np.array([float(np.mean(perm[:, k] >= obs[k] - EPS)) if obs[k] == obs[k] else np.nan for k in range(len(cols))])
    p_max30 = np.array([float(np.mean(maxs30 >= obs[k] - EPS)) if (k < nf and obs[k] == obs[k] and big[k]) else np.nan
                        for k in range(len(cols))])
    trades = {k: select(d, ok & masks[k], 'S2') for k in ALL_POST}
    s_c1 = stats_r(trades['F0']['r_alone'].to_numpy(), nd)
    c1 = s_c1.get('avg', np.nan)
    res = {}
    for k in ALL_POST:
        t = trades[k]
        s = stats_r(t['r_alone'].to_numpy(), nd)
        rest = select(d, ok & ~masks[k], 'S2') if k != 'F0' else t.iloc[0:0]
        c2p, n2p = c2_for(t, f, df, fp, after_only=True)
        h1 = t[t['half'] == 1]['r_alone'].mean() if len(t) else np.nan
        h2 = t[t['half'] == 2]['r_alone'].mean() if len(t) else np.nan
        if k in cols:
            j = cols.index(k)
            o, pr, pm30 = obs[j], p_raw[j], p_max30[j]
        else:
            o, pr, pm30 = np.nan, np.nan, np.nan
        if k in FAM11:
            jd = judge(s, c1, c2p, h1, h2, o, thr30)
            jd['ly_do'] = jd['ly_do'].replace('C2+0,15', "C2'+0,15")
        else:
            jd = dict(inner=False, dat=False, ly_do='đối chứng' if k == 'F0' else 'báo cáo — không có sức chọn')
        res[k] = dict(s=s, rest=stats_r(rest['r_alone'].to_numpy(), nd), c2p=c2p, n2p=n2p, h1=h1, h2=h2, obs=o, p_raw=pr,
                      p_max30=pm30, jd=jd, n_alone=int(masks[k][ok].sum()))
    # ---- 10.2-1: điều kiện cơ chế R TB(F7 ∧ ¬Hc) − R TB(F7 ∧ Hc) ≥ +0,20 (cả hai theo pipeline); thêm cách lọc của Fable (tách lệnh F7)
    a, b = res['F7b']['s'].get('avg', np.nan), res['F7Hc']['s'].get('avg', np.nan)
    t7 = trades['F7']
    hc7 = t7['Hc'].to_numpy().astype(bool) if len(t7) else np.zeros(0, bool)
    split7 = dict(nhc=stats_r(t7['r_alone'].to_numpy()[~hc7], nd), hc=stats_r(t7['r_alone'].to_numpy()[hc7], nd))
    if len(t7):
        split7['nhc_h1'] = float(t7[~hc7 & (t7['half'].to_numpy() == 1)]['r_alone'].mean())
        split7['nhc_h2'] = float(t7[~hc7 & (t7['half'].to_numpy() == 2)]['r_alone'].mean())
        split7['n_nhc_h1'] = int((~hc7 & (t7['half'].to_numpy() == 1)).sum())
        split7['n_nhc_h2'] = int((~hc7 & (t7['half'].to_numpy() == 2)).sum())
    mech = dict(diff=a - b if (a == a and b == b) else np.nan, nhc=a, hc=b)
    jd7 = res['F7b']['jd']
    s7 = res['F7b']['s']
    cond = []
    n7 = s7.get('n', 0)
    cond.append(('n ≥ 30', n7 >= 30, f'{n7}'))
    if n7:
        cond.append(('R TB ≥ C1 + 0,15', s7['avg'] >= c1 + 0.15 - EPS, f"{f2(s7['avg'])} vs {f2(c1 + 0.15)}"))
        c2p = res['F7b']['c2p']
        cond.append(("R TB ≥ C2' + 0,15", c2p is not None and s7['avg'] >= c2p + 0.15 - EPS,
                     f"{f2(s7['avg'])} vs {f2(c2p + 0.15) if c2p is not None else '–'}"))
        cond.append(('KTC dưới > −0,10', s7['lo'] > -0.10, f2(s7['lo'])))
        h1, h2 = res['F7b']['h1'], res['F7b']['h2']
        cond.append(('dương cả hai nửa', bool(h1 > 0 and h2 > 0), f'{f2(h1)} / {f2(h2)}'))
        o = res['F7b']['obs']
        cond.append(('vượt ngưỡng hoán vị ≥ 30 (family 11)', bool(o == o and o > thr30), f'Δ {f2(o, 3)} vs ngưỡng {f2(thr30, 3)}'))
    cond.append(('R TB(F7∧¬Hc) − R TB(F7∧Hc) ≥ +0,20', bool(mech['diff'] == mech['diff'] and mech['diff'] >= 0.20 - EPS),
                 f"{f2(mech['nhc'])} − {f2(mech['hc'])} = {f2(mech['diff'])}"))
    f7b_dat = bool(n7 >= 30 and all(c[1] for c in cond))
    # ---- H1–H3: R TB hai phía trên lệnh pipeline của từng combo
    hyp = {}
    for k in ('F0', 'F7', 'F7b', 'F10'):
        t = trades[k]
        for hn, col, op, th, _ in HYP:
            if len(t) == 0:
                hyp[(k, hn)] = (stats_r(np.zeros(0), nd), stats_r(np.zeros(0), nd))
                continue
            x = t[col].to_numpy(float)
            m_ = x < th if op == '<' else x >= th - EPS
            r_ = t['r_alone'].to_numpy()
            hyp[(k, hn)] = (stats_r(r_[m_], nd), stats_r(r_[~m_], nd))
    return dict(res=res, thr=thr, thr30=thr30, trades=trades, c1=c1, mech=mech, split7=split7, cond=cond, f7b_dat=f7b_dat,
                hyp=hyp, n_sub=len(sub), n_perm=n_perm, jd7=jd7)


def render_post(E: dict, nd: int) -> List[str]:
    """Bảng chính F0…F10 + F7b + 3 dòng báo cáo, kiểm F7b (10.2-1), bảng H1–H3 — Markdown."""
    res = E['res']
    L = [f"Hoán vị thống kê cực đại: {E['n_perm']} lần trên {E['n_sub']} F0 đã qua Vk + cổng; **family 11 combo = F1…F10 + F7b** "
         f"(F7b hậu kiểm). Ngưỡng phân vị 95: max trên 11 combo = {f2(E['thr'], 3)}R · **max chỉ trên combo có ≥ 30 F0 = "
         f"{f2(E['thr30'], 3)}R (ngưỡng chấm)**. Ba dòng F7∧Hc / F10∧¬Hc / F0∧¬Hc chỉ báo cáo (có p thô, không vào max).", '',
         "| Combo | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD | chuỗi thua | C1 toàn F0 | C1 F0∖combo | **C2'** | R nửa 1 / nửa 2 | "
         "Δ r_alone vs F0 (n F0) | p thô / p cực đại (≥ 30, 11 combo) | vòng trong (C2') | ĐẠT (C2') |",
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for k in ALL_POST:
        u = res[k]
        s = u['s']
        nm = f"**{k}** {COMBO_NAME[k]}"
        if s.get('n', 0) == 0:
            L.append(f"| {nm} | 0 | – | – | – | – | – | – | – | {f2(E['c1'])} | – | – | – | – | – | – | không đo được |")
            continue
        jd = u['jd']
        inner = '**có**' if jd['inner'] else ('–' if k not in FAM11 else 'không')
        dat = '**ĐẠT**' if jd['dat'] else jd['ly_do']
        L.append(f"| {nm} | {s['n']} | {f2(s['per_day'])} | {f2(100 * s['wr'], 1)} % | **{f2(s['avg'])}** | [{f2(s['lo'])}; {f2(s['hi'])}] | "
                 f"{f2(s['sum'], 1)} | {f2(s['dd'], 1)} | {s['streak']} | {f2(E['c1'])} | "
                 f"{f2(u['rest'].get('avg')) if k != 'F0' else '–'} | **{f2(u['c2p'])}** | {f2(u['h1'])} / {f2(u['h2'])} | "
                 f"{f2(u['obs'], 3) if k != 'F0' else '–'} ({u['n_alone']}) | {f2(u['p_raw'], 3)} / {f2(u['p_max30'], 3)} | {inner} | {dat} |")
    L += ['', '**Kiểm F7b theo 10.2-1** (đủ mọi điều kiện mới ĐẠT):', '', '| điều kiện | đạt? | số |', '|---|---|---|']
    for name, okc, txt in E['cond']:
        L.append(f"| {name} | {'có' if okc else '**không**'} | {txt} |")
    sp = E['split7']
    L += ['', f"⇒ **F7b: {'ĐẠT' if E['f7b_dat'] else 'KHÔNG ĐẠT'}**.", '',
          f"Cách lọc của Fable (tách {sp['nhc'].get('n', 0) + sp['hc'].get('n', 0)} lệnh F7 đã chọn theo Hc, KHÔNG chọn lại one_at_a_time): "
          f"F7 ∧ ¬Hc n {sp['nhc'].get('n', 0)} · R TB {f2(sp['nhc'].get('avg'))} · nửa 1/2 {f2(sp.get('nhc_h1'))} ({sp.get('n_nhc_h1', 0)}) / "
          f"{f2(sp.get('nhc_h2'))} ({sp.get('n_nhc_h2', 0)}); F7 ∧ Hc n {sp['hc'].get('n', 0)} · R TB {f2(sp['hc'].get('avg'))}.", '',
          '**Giả thuyết H1–H3 (chỉ đo, không có sức chọn) — R TB (n) hai phía trên lệnh pipeline của từng combo:**', '',
          '| giả thuyết | ' + ' | '.join(f'{k} đạt | {k} không' for k in ('F0', 'F7', 'F7b', 'F10')) + ' |',
          '|---|' + '---|' * 8]
    for hn, _, _, _, lab in HYP:
        cells = []
        for k in ('F0', 'F7', 'F7b', 'F10'):
            a, b = E['hyp'][(k, hn)]
            cells += [f"{f2(a.get('avg'))} ({a.get('n', 0)})", f"{f2(b.get('avg'))} ({b.get('n', 0)})"]
        L.append(f'| {hn} {lab} | ' + ' | '.join(cells) + ' |')
    L.append('')
    return L


# =====================================================================================================
# MAIN — GĐ-F0 + GĐ-F1 trên TRAIN
# =====================================================================================================
def f2(x, p=2):
    return ('%.*f' % (p, x)).replace('.', ',') if (x is not None and x == x) else '–'


def build(bars, df, good, fp: FP, f=None, eng_out=None):
    import setup_corven as SC
    if eng_out is None:
        eng_out = feed_engine(bars)
    eng, evs_by_bar, info, mbr = eng_out
    if f is None:
        f = SC.Feat(bars, df, mbr, SC.CP(), good)
    m = run_machine(f, evs_by_bar, info, fp)
    d = pd.DataFrame(m.rows)
    if len(d):
        d = d.sort_values(['idx_c', 'range_id', 'D']).reset_index(drop=True)
        d['good'] = good[d['idx_c'].to_numpy()].astype(int)
        d['phien'] = df['session_id'].to_numpy()[d['idx_c'].to_numpy()]
        d['t_utc'] = df['t_utc'].astype(str).str[:16].to_numpy()[d['idx_c'].to_numpy()]
        d['t_vn'] = df['t_vn'].astype(str).str[:16].to_numpy()[d['idx_c'].to_numpy()]
        d['phase'] = df['phase'].to_numpy()[d['idx_c'].to_numpy()]
        d['month'] = df['month'].to_numpy()[d['idx_c'].to_numpy()] if 'month' in df else pd.to_datetime(d['t_utc']).dt.strftime('%Y-%m')
        d = simulate_alone(d, df, f, SC.sim_one, 'S2')
        d = simulate_alone(d, df, f, SC.sim_one, 'S1')
        d = simulate_alone(d, df, f, SC.sim_one, 'S3')
    return m, d, f, eng_out


def c2_for(trades: pd.DataFrame, f, df, fp: FP, nm='S2', after_only: bool = False):
    """controls_corven.c2 bọc cho Follow (chosen = .cf/.S/.risk; trades có cột r). after_only=True ⇒ C2' (plan 9.1-3)."""
    import controls_corven as CC
    if len(trades) == 0:
        return None, 0
    suf = sfx(nm)
    chosen = [SimpleNamespace(cf=int(r.idx_c), S=int(r.D), risk=float(getattr(r, f'risk_{nm}'))) for r in trades.itertuples()]
    tr = pd.DataFrame({'r': trades['r_alone' + suf].to_numpy()})
    d2, allr = CC.c2(dict(feat=f, df=df, cp=SimpleNamespace(tp_r=fp.tp_r), chosen=chosen, trades=tr), after_only=after_only)
    if len(d2) == 0:
        return None, 0
    return float(d2['r_c2_tb'].mean()), len(allr)


def main(n_perm: int = 2000):
    import setup_corven as SC
    cut = SC.train_cut()
    bars, df = SC.load_train(cut=cut)                  # ⛔ đã cắt TEST
    assert str(df['datetime'].iloc[-1])[:10] <= '2026-09-15'
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    sess_good = sorted(set(df['session_id'].to_numpy()[good]))
    nd = len(sess_good)
    half_of = {s: (1 if k < 18 else 2) for k, s in enumerate(sess_good)}
    fp = FP()
    m, d, f, eng_out = build(bars, df, good, fp)
    eng = eng_out[0]
    d['half'] = d['phien'].map(half_of).fillna(0).astype(int)
    os.makedirs(REPORT, exist_ok=True)
    cols_first = ['idx_ref', 'idx_x', 'idx_c', 'leg', 'D', 'E', 'range_id', 'move_h', 'depth'] + list(FLAGS) + ['Vk']
    d[cols_first + [c for c in d.columns if c not in cols_first]].to_csv(os.path.join(REPORT, '_follow_cands.csv'), index=False,
                                                                           encoding='utf-8')
    G = d['good'].to_numpy().astype(bool)
    dg = d[G]
    # ------------------------------------------------------------ (i) tần suất + (vi) phễu
    co = [ev for i, evs in enumerate(eng_out[1]) if good[i] for ev in evs if ev.kind == 'CloseOutside']
    legs = pd.DataFrame(m.legs)
    legs_g = legs[[good[min(int(x), len(good) - 1)] for x in legs['ref']]] if len(legs) else legs
    L = []
    L += ['# Benzo FOLLOW-COMBO — kết quả GĐ-F0 + GĐ-F1 trên TRAIN (+ chấm lại C2’ theo plan 9.3-A)', '',
          f'> Opus, 2026-11-09, theo `plans/BENZO-FOLLOW-COMBO-plan.md` (đăng ký trước, commit ee8b252). **Chỉ TRAIN**: {nd} phiên dày, '
          f'nến 0…{cut} (tới {str(df["datetime"].iloc[-1])[:16]} UTC). **TEST (≥ 2026-09-16) không nạp, không đọc.** '
          '`kernel.simulate` (phí 0,2 giá/lệnh, chạm SL+TP cùng nến = SL, vào giá đóng CF), lệnh còn mở tới nến cuối phiên đóng `TIME`.',
          '> ⚠️ Mẫu TRAIN, chưa kiểm định ngoài mẫu — không dùng để vào lệnh thật.', '']
    n_f0 = len(dg)
    vk = int(dg['Vk'].sum())
    L += ['## 1. GĐ-F0 — tần suất (mục 6.i) và phễu (mục 6.vi)', '',
          f'- `CloseOutside` (cú phá bắt đầu): **{len(co)}** = {f2(len(co) / nd)} /ngày.',
          f'- Leg được xét: {len(legs_g)}; leg có move hợp lệ (đẩy ≥ 1 mbr ra ngoài + ΣΔ cùng hướng) ở một thời điểm nào đó: '
          f'**{int(legs_g["valid"].sum()) if len(legs_g) else 0}** = {f2((legs_g["valid"].sum() if len(legs_g) else 0) / nd)} /ngày.',
          f'- **F0** (move + nhịp hồi + CF Follow): **{n_f0}** = **{f2(n_f0 / nd)} /ngày** (kỳ vọng sơ bộ của plan 2–6/ngày'
          + ('; > 10/ngày ⇒ 2a quá lỏng — xem câu hỏi' if n_f0 / nd > 10 else '') + ').',
          f'- F0 bị veto Vk (kiệt sức phe mình ở đỉnh move chưa bị quét): {vk} = {f2(100 * vk / max(1, n_f0), 1)} %.', '',
          '| Cờ | có trên F0 | % F0 | % F0 đã qua Vk |', '|---|---|---|---|']
    dv = dg[dg['Vk'] == 0]
    for k in FLAGS:
        L.append(f'| {k} | {int(dg[k].sum())} | {f2(100 * dg[k].mean(), 1)} % | {f2(100 * dv[k].mean(), 1)} % |')
    L += ['', f'Nhãn đo thêm trên F0: CF thoả 4a đầy đủ `cf_4a` {f2(100 * dg["cf_4a"].mean(), 1)} % · `cf_strict` '
          f'{f2(100 * dg["cf_strict"].mean(), 1)} % · nhịp hồi `deep` (> 0,7 move) {f2(100 * dg["deep"].mean(), 1)} % · '
          f'leg 2 {f2(100 * (dg["leg"] == 2).mean(), 1)} % · `b_from_exhausted` {f2(100 * dg["b_from_exhausted"].mean(), 1)} % · '
          f'số nến hồi 1/2 = {int((dg["n_hoi"] == 1).sum())}/{int((dg["n_hoi"] == 2).sum())}.', '']
    # phễu
    ends = Counter(legs_g['end']) if len(legs_g) else Counter()
    tr_ok = tradeable(d, 'S2')
    t_f0 = select(d, tr_ok, 'S2')
    n_cap = int(((dv['cap_S2'] == 0)).sum())
    n_time = int(((dv['cap_S2'] == 0) & (dv['chan_1920'] == 0) & (dv['dau_phien'] == 0) & (dv['cuoi_phien'] == 0)).sum())
    L += ['**Phễu** (phiên dày; đơn vị = leg, từ bước CF = F0):', '',
          '| Bước | số | ghi chú |', '|---|---|---|',
          f'| CloseOutside | {len(co)} | mỗi cú phá ≤ 2 leg |',
          f'| leg được xét | {len(legs_g)} | |',
          f'| move hợp lệ | {int(legs_g["valid"].sum()) if len(legs_g) else 0} | |',
          f'| có nhịp hồi (move hợp lệ) | {int(legs_g["pb"].sum()) if len(legs_g) else 0} | |',
          f'| có CF ≤ x + 3 (= F0) | {n_f0} | leg kết thúc: ' + ', '.join(f'{k} {v}' for k, v in ends.most_common()) + ' |',
          f'| qua Vk | {len(dv)} | |',
          f'| qua trần SL 4 mbr (S2) | {n_cap} | |',
          f'| qua giờ (chặn 19:20–20:30, 15 nến đầu phiên, nến cuối phiên) | {n_time} | |',
          f'| lệnh F0 (1 lệnh mở, 1 lệnh/(range, cạnh, leg)) | {len(t_f0)} | |', '']
    # ------------------------------------------------------------ (ii) bảng chính 11 dòng
    def run_cfg(dd: pd.DataFrame, nm='S2', block_us=True, gate17=False, extra=None):
        ok = tradeable(dd, nm, block_us, gate17)
        if extra is not None:
            ok &= extra
        masks = combo_mask(dd)
        out = {}
        for k in COMBOS:
            out[k] = select(dd, ok & masks[k], nm)
        out['_ok'] = ok
        out['_masks'] = masks
        return out
    main_cfg = run_cfg(d)
    ok = main_cfg['_ok']
    masks = main_cfg['_masks']
    # hoán vị trên F0 tradeable (đã qua Vk + cổng), r_alone
    sub = np.flatnonzero(ok)
    M = np.column_stack([masks[k][sub] for k in SEL_COMBOS])
    rr = d['r_alone'].to_numpy()[sub]
    grp = d['phien'].to_numpy()[sub]
    obs, perm, maxs = perm_test(M, rr, grp, n_perm=n_perm, seed=0)
    thr = float(np.percentile(maxs, 95))
    p_raw, p_max = perm_pvalues(obs, perm, maxs)
    pd.DataFrame({'max_diff': maxs}).to_csv(os.path.join(REPORT, '_follow_perm.csv'), index=False)
    n_sel = M.sum(0)
    big = n_sel >= 30
    maxs30 = np.nanmax(perm[:, big], axis=1) if big.any() else np.full(n_perm, np.nan)
    thr30 = float(np.percentile(maxs30, 95)) if big.any() else np.nan
    p_max30 = np.array([float(np.mean(maxs30 >= obs[k] - EPS)) if (obs[k] == obs[k] and big[k]) else np.nan for k in range(len(obs))])
    suf = ''
    s_c1 = stats_r(main_cfg['F0']['r_alone'].to_numpy(), nd)
    res = {}
    for kk, k in enumerate(COMBOS):
        t = main_cfg[k]
        s = stats_r(t['r_alone'].to_numpy(), nd)
        rest = select(d, ok & ~masks[k], 'S2') if k != 'F0' else t.iloc[0:0]
        s_rest = stats_r(rest['r_alone'].to_numpy(), nd)
        c2, n2 = c2_for(t, f, df, fp)
        c2p, n2p = c2_for(t, f, df, fp, after_only=True)          # C2' (plan 9.1-3)
        h1 = t[t['half'] == 1]['r_alone'].mean() if len(t) else np.nan
        h2 = t[t['half'] == 2]['r_alone'].mean() if len(t) else np.nan
        if k == 'F0':
            o, pr, pm, pm30 = np.nan, np.nan, np.nan, np.nan
            jd = jd2 = dict(inner=False, dat=False, ly_do='đối chứng')
        else:
            j = SEL_COMBOS.index(k)
            o, pr, pm, pm30 = obs[j], p_raw[j], p_max[j], p_max30[j]
            jd = judge(s, s_c1.get('avg', np.nan), c2, h1, h2, o, thr)              # cũ (GĐ-F1): C2 lệch + ngưỡng 10 combo
            jd2 = judge(s, s_c1.get('avg', np.nan), c2p, h1, h2, o, thr30)          # chấm (9.1-2/9.1-3): C2' + ngưỡng combo ≥ 30 F0
            jd2['ly_do'] = jd2['ly_do'].replace('C2+0,15', "C2'+0,15")
        res[k] = dict(s=s, rest=s_rest, c2=c2, n2=n2, c2p=c2p, n2p=n2p, h1=h1, h2=h2, obs=o, p_raw=pr, p_max=pm, p_max30=pm30,
                      jd=jd, jd2=jd2, n_alone=int(masks[k][ok].sum()))
        t.to_csv(os.path.join(REPORT, f'_follow_trades_{k}.csv'), index=False, encoding='utf-8')
    L += ['## 2. GĐ-F1 — bảng chính (cấu hình chính: S2 · TP 2R không cổng · cf_within 3 · CF lỏng)', '',
          "> **Cập nhật 2026-11-09 theo plan mục 9.3-A (hậu kiểm):** thêm cột **C2'** = `controls_corven.c2(after_only=True)` — chỉ nến SAU "
          "nến CF, 0 < Δphút ≤ 30, cùng phiên/hướng/rủi ro mbr, 20 nến, pool < 5 ⇒ bỏ lệnh (C2 cũ có thiên lệch dương vì nến trước cú phá "
          "\"biết trước\" hướng). Cột **vòng trong / ĐẠT (C2')** là cột chấm: C2' thay C2, ngưỡng hoán vị = max chỉ trên combo có ≥ 30 F0 "
          "(plan 9.1-2). Hai cột \"(C2 cũ)\" giữ để đối chiếu kết luận GĐ-F1.", '',
          f'Hoán vị thống kê cực đại (4.4): {n_perm} lần, hoán vị nguyên dòng cờ giữa các F0 cùng phiên (trên {len(sub)} F0 đã qua Vk + cổng, '
          f'dùng `r_alone`), thống kê = R TB(combo) − R TB(F0). Ngưỡng phân vị 95: max trên cả 10 combo = {f2(thr, 3)}R (GĐ-F1, cũ) · '
          f'**max chỉ trên combo có ≥ 30 F0 = {f2(thr30, 3)}R (ngưỡng CHẤM từ 9.1-2)**.', '',
          "| Combo | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD | chuỗi thua | C1 toàn F0 | C1 F0∖combo | C2 cũ | **C2'** | R nửa 1 / nửa 2 | "
          "Δ r_alone vs F0 (n F0) | p thô / p cực đại (10 combo) / p cực đại (≥ 30) | vòng trong (C2 cũ) | ĐẠT (C2 cũ) | "
          "**vòng trong (C2')** | **ĐẠT (C2')** |",
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for k in COMBOS:
        u = res[k]
        s = u['s']
        if s.get('n', 0) == 0:
            L.append(f"| **{k}** {COMBO_NAME[k]} | 0 | – | – | – | – | – | – | – | {f2(s_c1.get('avg'))} | – | – | – | – | – | – | – | không đo được | – | không đo được |")
            continue
        jd, jd2 = u['jd'], u['jd2']
        L.append(f"| **{k}** {COMBO_NAME[k]} | {s['n']} | {f2(s['per_day'])} | {f2(100 * s['wr'], 1)} % | **{f2(s['avg'])}** | "
                 f"[{f2(s['lo'])}; {f2(s['hi'])}] | {f2(s['sum'], 1)} | {f2(s['dd'], 1)} | {s['streak']} | {f2(s_c1.get('avg'))} | "
                 f"{f2(u['rest'].get('avg')) if k != 'F0' else '–'} | {f2(u['c2'])} | **{f2(u['c2p'])}** | {f2(u['h1'])} / {f2(u['h2'])} | "
                 f"{f2(u['obs'], 3) if k != 'F0' else '–'} ({u['n_alone']}) | {f2(u['p_raw'], 3)} / {f2(u['p_max'], 3)} / {f2(u['p_max30'], 3)} | "
                 f"{'có' if jd['inner'] else ('–' if k == 'F0' else 'không')} | {'**ĐẠT**' if jd['dat'] else jd['ly_do']} | "
                 f"{'**có**' if jd2['inner'] else ('–' if k == 'F0' else 'không')} | {'**ĐẠT**' if jd2['dat'] else jd2['ly_do']} |")
    n_dat = sum(1 for k in SEL_COMBOS if res[k]['jd']['dat'])
    inner_old = [k for k in SEL_COMBOS if res[k]['jd']['inner']]
    n_dat2 = sum(1 for k in SEL_COMBOS if res[k]['jd2']['dat'])
    inner = [k for k in SEL_COMBOS if res[k]['jd2']['inner']]
    L += ['', f"**Kết luận GĐ-F1 (C2 cũ): {n_dat} combo ĐẠT** · lọt vòng trong: {', '.join(inner_old) if inner_old else 'không combo nào'}.", '',
          f"**Chấm lại theo C2' (9.3-A, hậu kiểm): {n_dat2} combo ĐẠT** · lọt vòng trong (n ≥ 30, ≥ C1, ≥ C2'): "
          f"{', '.join(inner) if inner else 'không combo nào'} · "
          f"chưa đo được (n < 30): {', '.join(k for k in SEL_COMBOS if res[k]['s'].get('n', 0) < 30) or 'không'}."
          + (' ⚠️ Chấm lại SAU khi đã nhìn R trên TRAIN — không tự mở TEST; Fable quyết.' if n_dat2 else ''),
          '', 'Ghi chú cột: n/WR/R TB… là lệnh thật (1 lệnh mở, 1 lệnh/(range, cạnh, leg)). "C1 toàn F0" = mọi F0 cùng cấu hình; '
          '"C1 F0∖combo" = F0 không thuộc combo, chọn lệnh cùng cách. C2 cũ = `controls_corven.c2` (20 nến ngẫu nhiên cùng phiên ±30′, cùng '
          "hướng, cùng rủi ro theo mbr) cho các lệnh của combo; C2' = cùng hàm với `after_only=True` (chỉ nến trong 30′ SAU CF). "
          '"Δ r_alone" = R TB(combo) − R TB(F0) trên F0 mô phỏng độc lập (thống kê '
          'của kiểm hoán vị; n F0 trong ngoặc). p thô = so với phân bố hoán vị của chính combo; p cực đại (10 combo) = so với phân bố max '
          'của 10 combo; p cực đại (≥ 30) = so với phân bố max chỉ trên combo có ≥ 30 F0.', '']
    # ------------------------------------------------------------ (iii) biến thể báo cáo
    var_rows = []
    variants = [('S1 (SL sát nhịp hồi)', dict(nm='S1'), None), ('gate17 (đòi R sẵn ≥ 1,7 tới E + chiều cao range)', dict(gate17=True), None),
                ('cf_strict (CF đóng > high nhịp hồi)', None, replace(fp, cf_mode='strict')),
                ('cf_within 4', None, replace(fp, cf_within=4)), ('cf_4a (CF thoả 4a đầy đủ)', None, replace(fp, cf_mode='4a')),
                ('chặn 19:20–20:30 TẮT', dict(block_us=False), None),
                ('S3 (leg 2 neo cực trị leg 1; 9.1-4, hậu kiểm)', dict(nm='S3'), None),
                ('move_mbr 1,5 (9.1-1, hậu kiểm)', None, replace(fp, move_mbr=1.5))]
    L += ['## 3. Biến thể báo cáo — **không có sức chọn** (mục 4.2), chỉ để biết', '',
          '| Biến thể | Combo | n | WR | R TB | KTC 95 % | ΣR | C1 (F0 cùng biến thể) |', '|---|---|---|---|---|---|---|---|']
    for name, kw, fpv in variants:
        if fpv is not None:
            _, dv2, _, _ = build(bars, df, good, fpv, f=f, eng_out=eng_out)
            cfg = run_cfg(dv2)
        else:
            cfg = run_cfg(d, **kw)
        nm = (kw or {}).get('nm', 'S2')
        col = 'r_alone' + sfx(nm)
        c1v = stats_r(cfg['F0'][col].to_numpy(), nd)
        for k in COMBOS:
            s = stats_r(cfg[k][col].to_numpy(), nd)
            var_rows.append(dict(bien_the=name, combo=k, n=s.get('n', 0), avg=s.get('avg', np.nan)))
            if s.get('n', 0) == 0:
                L.append(f"| {name} | {k} | 0 | – | – | – | – | {f2(c1v.get('avg'))} |")
            else:
                L.append(f"| {name} | {k} | {s['n']} | {f2(100 * s['wr'], 1)} % | {f2(s['avg'])} | [{f2(s['lo'])}; {f2(s['hi'])}] | "
                         f"{f2(s['sum'], 1)} | {f2(c1v.get('avg'))} |")
    L.append('')
    # ------------------------------------------------------------ (iv) tách nhóm
    L += ['## 4. Tách nhóm (cấu hình chính, lệnh thật): R TB (n)', '',
          '| Combo | leg 1 | leg 2 | Á | Âu | Mỹ | OFF | b_from_exhausted | không exhausted |', '|---|---|---|---|---|---|---|---|---|']

    def cell(t, m_):
        x = t['r_alone'].to_numpy()[m_]
        return f"{f2(x.mean()) if len(x) else '–'} ({len(x)})"
    for k in COMBOS:
        t = main_cfg[k]
        if len(t) == 0:
            L.append(f'| {k} | – | – | – | – | – | – | – | – |')
            continue
        L.append(f"| {k} | {cell(t, t['leg'].to_numpy() == 1)} | {cell(t, t['leg'].to_numpy() == 2)} | {cell(t, t['phase'].to_numpy() == 'A')} | "
                 f"{cell(t, t['phase'].to_numpy() == 'EU')} | {cell(t, t['phase'].to_numpy() == 'US')} | {cell(t, t['phase'].to_numpy() == 'OFF')} | "
                 f"{cell(t, t['b_from_exhausted'].to_numpy() == 1)} | {cell(t, t['b_from_exhausted'].to_numpy() == 0)} |")
    L.append('')
    show = ['F0'] + inner
    for k in show:
        t = main_cfg[k]
        if len(t) == 0:
            continue
        hrs = pd.to_datetime(t['t_vn']).dt.hour.to_numpy()
        L += [f'**{k} theo giờ VN (giờ mở nến CF):** ' + ' · '.join(f"{h:02d}h {cell(t, hrs == h)}" for h in sorted(set(hrs))), '',
              f'**{k} theo tháng:** ' + ' · '.join(f"{mo} {cell(t, t['month'].to_numpy() == mo)}" for mo in sorted(set(t['month']))), '']
    # ------------------------------------------------------------ (v) 5 thắng + 5 thua mỗi combo lọt vòng trong
    L += ['## 5. 5 thắng + 5 thua (rải đều theo thời gian) — combo lọt vòng trong', '']
    if not inner:
        L += ['Không combo nào lọt vòng trong ⇒ không có danh sách (mục 5 plan chỉ áp cho combo lọt vòng trong). '
              'Để Fable soi chart, liệt kê 5 thắng + 5 thua của **F0** thay thế:', '']
    for k in (inner or ['F0']):
        t = main_cfg[k]
        w = t[t['r_alone'] > 0]
        lo_ = t[t['r_alone'] <= 0]

        def spread(x, kk=5):
            if len(x) <= kk:
                return x
            return x.iloc[np.linspace(0, len(x) - 1, kk).round().astype(int)]
        L += [f'### {k}', '', '| | UTC | VN | side | leg | E | vào | SL | TP | cờ | kết cục | R |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
        for tag, x in (('thắng', spread(w)), ('thua', spread(lo_))):
            for n_, r in enumerate(x.itertuples()):
                fl = '+'.join(fl_ for fl_ in FLAGS if getattr(r, fl_)) or '–'
                L.append(f"| {tag} {n_ + 1} | {r.t_utc} | {r.t_vn[11:16]} | {'buy' if r.D > 0 else 'sell'} | {r.leg} | {f2(r.E * TICK, 1)} | "
                         f"{f2(r.entry * TICK, 1)} | {f2(r.sl_S2 * TICK, 1)} | {f2(r.tp_S2 * TICK, 1)} | {fl} | {r.outcome_alone} | {f2(r.r_alone)} |")
        L.append('')
    with open(os.path.join(REPORT, '_follow_summary.json'), 'w', encoding='utf-8') as fh:
        import json
        json.dump({k: dict(n=res[k]['s'].get('n', 0), avg=res[k]['s'].get('avg'), c1=s_c1.get('avg'), c2=res[k]['c2'],
                           c2p=res[k]['c2p'], n2p=res[k]['n2p'], inner_c2p=res[k]['jd2']['inner'], dat_c2p=res[k]['jd2']['dat'],
                           ly_do_c2p=res[k]['jd2']['ly_do'],
                           p_max30=None if res[k]['p_max30'] != res[k]['p_max30'] else float(res[k]['p_max30']),
                           dat=res[k]['jd']['dat'], inner=res[k]['jd']['inner'], ly_do=res[k]['jd']['ly_do'],
                           p_raw=None if res[k]['p_raw'] != res[k]['p_raw'] else float(res[k]['p_raw']),
                           p_max=None if res[k]['p_max'] != res[k]['p_max'] else float(res[k]['p_max']))
                   for k in COMBOS} | dict(thr=thr, thr30=thr30, n_f0=n_f0, nd=nd), fh, ensure_ascii=False, indent=1, default=float)
    # ------------------------------------------------------------ mục 10 plan — hậu kiểm vòng mổ 1: F7b (Dh ∧ ¬Hc)
    E = eval_post(d, f, df, fp, nd, n_perm=n_perm)
    for k in COMBOS:          # cùng pipeline ⇒ n / R TB / C1 / C2' của F0…F10 phải trùng bảng chính
        a, b = E['res'][k], res[k]
        assert a['s'].get('n', 0) == b['s'].get('n', 0), k
        if b['s'].get('n', 0):
            assert abs(a['s']['avg'] - b['s']['avg']) < 1e-12, k
        assert (a['c2p'] is None and b['c2p'] is None) or abs(a['c2p'] - b['c2p']) < 1e-12, k
    assert abs(E['c1'] - s_c1['avg']) < 1e-12
    for k in POST_SEL + POST_REP:
        E['trades'][k].to_csv(os.path.join(REPORT, f'_follow_trades_{k}.csv'), index=False, encoding='utf-8')
    L10 = section10(E, nd)
    return L, res, thr, d, L10


def section10(E: dict, nd: int) -> List[str]:
    s7b = E['res']['F7b']['s']
    sp = E['split7']
    dn = (s7b.get('n', 0) - 62)
    dr = (s7b.get('avg', np.nan) - 0.40)
    L = ['## 10. Hậu kiểm vòng mổ 1 — F7b (Opus, 2026-11-09, plan mục 10.3; chỉ TRAIN)', '',
         '> **Hậu kiểm**: F7b = Dh ∧ ¬Hc sinh ra SAU khi đã nhìn R trên TRAIN (mổ SL vòng 1). Số TRAIN dưới đây **chỉ để báo**, không mở TEST; '
         'F7b chỉ được xác nhận trên dữ liệu ≥ 22/10 bằng `follow_newdata.py` (cấu hình đóng băng, cùng hàm `eval_post`). '
         '**Hc** (D = +1) = `min(low[x+1 … c−1]) ≤ E + tol`, tol = max(2 tick, 0,5 mbr tại c); cột `Hc`, `hc_ext_mbr` = (E − min low)·D / mbr '
         'trong `_follow_cands.csv`. Cấu hình chính không đổi; F0…F10 bên dưới trùng bảng mục 2 về n / R TB / C1 / C2\' (script tự assert), '
         'chỉ p cực đại khác vì family hoán vị giờ là 11 combo.', '']
    L += render_post(E, nd)
    L += ['> ⚠️ Chữ "ĐẠT" của F7b ở trên là **trên chính dữ liệu đã sinh ra luật** (Hc chọn sau khi nhìn R TRAIN) ⇒ **không phải bằng chứng**, '
          'chỉ cho biết F7b không chết ngay trong mẫu. Kết luận ĐẠT / KHÔNG duy nhất được tính là lần chạy `follow_newdata.py` trên dữ liệu ≥ 22/10. '
          'Bảng H1–H3 tính trên mọi lệnh pipeline (kể cả TIME) nên dòng F0 lệch nhẹ so với `MO-SL-FOLLOW.md` 4.2 (chỉ SL/TP).', '']
    L += ['**Đối chiếu số lọc của Fable** (`MO-SL-FOLLOW.md` mục 3: F7 ∧ ¬Hc n 62, R TB +0,40, nửa 1/2 +0,45 (36) / +0,33 (26); F7 ∧ Hc n 33, −0,17):', '',
          f"- Pipeline (chọn lại one_at_a_time trên mask F7b): n **{s7b.get('n', 0)}** (lệch {dn:+d}), R TB **{f2(s7b.get('avg'))}** "
          f"(lệch {('%+.2f' % dr).replace('.', ',')}R). F7 ∧ Hc pipeline n {E['res']['F7Hc']['s'].get('n', 0)}, R TB {f2(E['mech']['hc'])}.",
          f"- Cách lọc của Fable tái hiện từ lệnh F7: ¬Hc n {sp['nhc'].get('n', 0)} · {f2(sp['nhc'].get('avg'))}; Hc n {sp['hc'].get('n', 0)} · "
          f"{f2(sp['hc'].get('avg'))}.",
          '- ' + ('Lệch vượt ngưỡng 10.3-5 (> 0,10R hoặc n > 10) ⇒ xem `MO-SL-FOLLOW.md` mục 7.' if (abs(dn) > 10 or abs(dr) > 0.10)
                  else 'Lệch trong ngưỡng 10.3-5 (≤ 0,10R và n ≤ 10) ⇒ không cần mục 7 `MO-SL-FOLLOW.md`.'), '']
    return L


if __name__ == '__main__':
    L, res, thr, d, L10 = main()
    notes = os.path.join(REPORT, '_follow_notes.md')
    if os.path.exists(notes):
        L += open(notes, encoding='utf-8').read().splitlines()
    L += [''] + L10
    with open(os.path.join(REPORT, 'RESULTS-FOLLOW.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('\n'.join(L[:60]))
