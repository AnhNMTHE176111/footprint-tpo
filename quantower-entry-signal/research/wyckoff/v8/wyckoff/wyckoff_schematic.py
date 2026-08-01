#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wyckoff_schematic.py — prototype PYTHON (chay truoc khi port C#) cho tinh nang MOI: tu dong
nhan dien Trading Range + Phase A-E + cac su kien Wyckoff (SC/BCLX, AR, ST, Spring/Shakeout,
UT/UTAD, SOS/SOW, LPS/LPSY) tren du lieu M1 THAT (dxFeed GCQ26), roi VE thu len anh de kiem
truc quan TRUOC khi dua vao WyckoffRunner.cs.

Nguon quy tac dung de code hoa (KHONG bay dat, tat ca lay tu tai lieu da chung cat):
  - data-export/wyckoff/THEORY.md       (dinh nghia goc Phase A-E, PS/SC/AR/ST/Spring/SOS/LPS,
    doi xung PSY/BCLX/AR/ST/UT/UTAD/SOW/LPSY, "cau truc that bai")
  - data-export/wyckoff/CHART_CASES.md  (9 loi gan nhan hay gap tu bai chua hoc vien THAT —
    dung lam RANG BUOC thiet ke, xem comment tung buoc ben duoi trich dan so dong)
  - data-export/wyckoff/WYCKOFF_RULES.md (WY01-WY17, cot "Kiem offline duoc?")

Dung lai KHONG SUA: entry_dxfeed.py (load_m1, VSA_CLIMAX, TICK).

Chay: python3 wyckoff_schematic.py            -> in thong ke + ve 1 anh mau moi range dai nhat
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, RESEARCH)

import entry_dxfeed as E  # noqa: E402

TICK = E.TICK
VSA_CLIMAX = E.VSA_CLIMAX

# ============================================================================
# Tham so (giu 1 cho, de A/B khi can — TAT CA co the sweep o GD sau)
# ============================================================================
CLIMAX_RANGE_MULT = 1.4      # rong nen climax >= x lan TB range N nen truoc (loai climax gia)
CLIMAX_RANGE_LOOKBACK = 20
AR_LOOKBACK = 40             # so nen toi da cho AR hinh thanh sau climax
ST_TOL_TICKS = 10            # dung sai "cham lai bien" tinh la ST/UT (khong phai pha that)
ST_MIN_GAP_BARS = 5          # khoang cach toi thieu giua 2 nhan ST/UT lien tiep (tranh spam)
SOS_BODY_MIN = 0.45          # WY05: SOS-bar than >= 45% range (tai lieu khong cho so — de xuat)
SOS_VSA_HINT = 1.3           # CHỈ la nhan hien thi bonus (WY08: volume thap van hop le), KHONG gate cung
LPS_WAIT_BARS = 25           # so nen cho hoi sau SOS/SOW truoc khi coi la "khong hoi, sang E luon"
LPS_AREA_MIN_BARS = 3        # >=3 nen dao dong hep quanh vung -> ve AREA (Loi#1 CHART_CASES.md)
PHASE_E_MULT = 1.0           # gia phai di xa hon RangeHeight*mult khoi bien pha de tinh la Phase E

# --- guard chong range "vo han" (KHONG co trong tai lieu goc — tu dat de tranh thoai hoa thuat
# toan khi gia trend that manh xuyen suot nhieu thang; TR Wyckoff that la vung CAN BANG hep,
# khong phai the hien ca mot xu huong dai) ---
MAX_RANGE_HEIGHT_PCT = 0.035   # bien do toi da ~3.5% gia hien tai — vuot nguong nay -> bo range
MAX_BARS_PHASE_AB = 2500       # qua ngan nay ma chua toi Phase C (Spring/UT) -> bo, tim climax moi
MAX_BARS_PHASE_D = 2000        # qua ngan nay o Phase D ma khong chot duoc E -> bo


def _avg_range(B, i, lookback):
    lo = max(0, i - lookback)
    win = B[lo:i]
    if not win:
        return B[i]['rng']
    return sum(b['rng'] for b in win) / len(win)


class WyRange:
    __slots__ = ('start_i', 'end_i', 'kind', 'low', 'high', 'events', 'phases', 'status', 'state')

    def __init__(self, start_i, kind):
        self.start_i = start_i
        self.end_i = None
        self.kind = kind          # 'ACC' | 'DIST'
        self.low = None
        self.high = None
        self.events = []          # list of dict(i, label, price, phase)
        self.phases = []          # list of [phase_char, start_i, end_i(None=dang mo)]
        self.status = 'active'    # active | completed
        self.state = 'A'          # A(cho AR) | B | C | D | E

    def add_event(self, i, label, price, phase):
        self.events.append(dict(i=i, label=label, price=price, phase=phase))

    def set_phase(self, i, phase):
        if self.phases and self.phases[-1][0] == phase:
            return
        if self.phases:
            self.phases[-1][2] = i - 1
        self.phases.append([phase, i, None])


def detect(B):
    """Tra list[WyRange] da phat hien (ca active lan completed) tren toan bo B."""
    ranges = []
    active = None

    for i in range(CLIMAX_RANGE_LOOKBACK + 5, len(B)):
        b = B[i]

        # ---------------------------------------------------------------- khong co range active: tim climax
        if active is None:
            avgr = _avg_range(B, i, CLIMAX_RANGE_LOOKBACK)
            if avgr <= 0:
                continue
            is_wide = b['rng'] >= CLIMAX_RANGE_MULT * avgr
            is_climax_vol = b['vratio'] >= VSA_CLIMAX
            if not (is_wide and is_climax_vol):
                continue
            # Loi#3 (CHART_CASES.md dong 549): SC chi hop le neu TRUOC do la downtrend that.
            # Dung field 'trend' (BASE TREND_LB, proxy TPO/close-vs-close) da co san trong B.
            if b['dn'] and b['trend'] == -1:
                r = WyRange(i, 'ACC')
                r.low = b['lo']
                r.add_event(i, 'SC', b['lo'], 'A')
                r.set_phase(i, 'A')
                active = r
            elif b['up'] and b['trend'] == 1:
                r = WyRange(i, 'DIST')
                r.high = b['hi']
                r.add_event(i, 'BCLX', b['hi'], 'A')
                r.set_phase(i, 'A')
                active = r
            continue

        r = active
        climax_i = r.start_i
        last_evt_i = r.events[-1]['i'] if r.events else climax_i
        gap_ok = (i - last_evt_i) >= ST_MIN_GAP_BARS
        tol = ST_TOL_TICKS * TICK

        # ---------------------------------------------------------------- guard: bo range thoai hoa
        height = (r.high - r.low) if (r.high is not None and r.low is not None) else 0.0
        too_tall = height > MAX_RANGE_HEIGHT_PCT * b['c']
        too_long_ab = r.state in ('A', 'B') and (i - climax_i) > MAX_BARS_PHASE_AB
        too_long_d = r.state == 'D' and (i - climax_i) > MAX_BARS_PHASE_D
        if too_tall or too_long_ab or too_long_d:
            active = None   # bo, KHONG ghi vao ranges (gia thuyet khong tru thanh TR hop le)
            continue

        # ---------------------------------------------------------------- state A: cho AR
        if r.state == 'A':
            if i - climax_i > AR_LOOKBACK:
                # khong bat duoc AR ro rang trong cua so -> lay diem cuc tri da co lam AR tam
                if r.kind == 'ACC':
                    ar_i = max(range(climax_i + 1, i + 1), key=lambda k: B[k]['hi'])
                    r.high = B[ar_i]['hi']
                else:
                    ar_i = min(range(climax_i + 1, i + 1), key=lambda k: B[k]['lo'])
                    r.low = B[ar_i]['lo']
                r.add_event(ar_i, 'AR', B[ar_i]['hi'] if r.kind == 'ACC' else B[ar_i]['lo'], 'A')
                r.set_phase(i, 'B')
                r.state = 'B'
            continue

        # ------------------------------------------------- state B: tim Spring/UT (Phase C) + ST, KHONG tim SOS
        abandon_b = False
        if r.state == 'B':
            fail_tol = 3.0 * ST_TOL_TICKS * TICK
            if r.kind == 'ACC':
                if b['lo'] < r.low - 1e-9 and b['c'] > r.low and gap_ok:
                    depth_t = (r.low - b['lo']) / TICK
                    is_shake = depth_t >= 15 or b['vratio'] >= 1.5 * VSA_CLIMAX
                    label = 'Shakeout' if is_shake else 'Spring'
                    r.low = b['lo']
                    r.add_event(i, label, b['lo'], 'C')
                    r.set_phase(i, 'C')
                    r.set_phase(min(len(B) - 1, i + 1), 'D')
                    r.state = 'D'
                elif abs(b['lo'] - r.low) <= tol and gap_ok:
                    r.add_event(i, 'ST', b['lo'], r.phases[-1][0])
                    r.low = min(r.low, b['lo'])
                elif b['c'] < r.low - fail_tol and b['brat'] >= SOS_BODY_MIN:
                    # pha THAT xuong (dong nen lui han qua duoi, KHONG dao nguoc = khong phai Spring) ->
                    # gia thuyet Tich luy sai (that su la breakdown) -> bo range (§9 THEORY.md "cau truc
                    # that bai", huong nguoc: o day la pha SAI huong ngay tu Phase B, chua kip Phase C)
                    abandon_b = True
                elif b['lo'] < r.low:
                    r.low = b['lo']   # mo rong bien am tham, chua du dieu kien gan nhan Spring (thieu gap_ok)
            else:  # DIST — guong lai
                if b['hi'] > r.high + 1e-9 and b['c'] < r.high and gap_ok:
                    depth_t = (b['hi'] - r.high) / TICK
                    label = 'UTAD' if depth_t >= 15 or b['vratio'] >= 1.5 * VSA_CLIMAX else 'UT'
                    r.high = b['hi']
                    r.add_event(i, label, b['hi'], 'C' if label == 'UTAD' else r.phases[-1][0])
                    if label == 'UTAD':
                        r.set_phase(i, 'C')
                        r.set_phase(min(len(B) - 1, i + 1), 'D')
                        r.state = 'D'
                elif abs(b['hi'] - r.high) <= tol and gap_ok:
                    r.add_event(i, 'ST', b['hi'], r.phases[-1][0])
                    r.high = max(r.high, b['hi'])
                elif b['c'] > r.high + fail_tol and b['brat'] >= SOS_BODY_MIN:
                    abandon_b = True  # pha THAT len (khong dao nguoc) -> gia thuyet Phan phoi sai
                elif b['hi'] > r.high:
                    r.high = b['hi']
            if abandon_b:
                active = None
                continue

        # ------------------------------------------------- state D: CHI tim SOS/SOW (khong tim Spring/UT nua)
        elif r.state == 'D':
            fired = False
            if r.kind == 'ACC' and b['c'] > r.high + tol and b['brat'] >= SOS_BODY_MIN and gap_ok:
                r.add_event(i, 'SOS', b['c'], 'D')
                r.high = max(r.high, b['hi'])
                fired = True
                closed = _try_lps_and_phase_e(B, r, i, ACC=True)
            elif r.kind == 'DIST' and b['c'] < r.low - tol and b['brat'] >= SOS_BODY_MIN and gap_ok:
                r.add_event(i, 'SOW', b['c'], 'D')
                r.low = min(r.low, b['lo'])
                fired = True
                closed = _try_lps_and_phase_e(B, r, i, ACC=False)
            if fired and not closed:
                r.state = 'B'   # breakout chua "di xa" duoc (that bai/chua xac nhan) -> ve lai Phase B, cho test moi
            elif not fired:
                # gia pha them cuc tri nhung KHONG du than/VSA de tinh la SOS that -> chi mo rong bien am tham
                if r.kind == 'ACC' and b['lo'] < r.low:
                    r.low = b['lo']
                elif r.kind == 'DIST' and b['hi'] > r.high:
                    r.high = b['hi']

        # ---------------------------------------------------------------- da vao Phase E -> dong range
        if r.phases and r.phases[-1][0] == 'E':
            r.phases[-1][2] = min(len(B) - 1, i)
            r.end_i = i
            r.status = 'completed'
            ranges.append(r)
            active = None

    if active is not None:
        if active.phases:
            active.phases[-1][2] = len(B) - 1
        ranges.append(active)
    return ranges


def _try_lps_and_phase_e(B, r, sos_i, ACC):
    """Sau SOS/SOW: tim nhip hoi GIU bien (LPS/LPSY). Neu hoi >=3 nen dao dong hep -> AREA
    (Loi#1 CHART_CASES.md dong 547), neu 1-2 nen -> POINT. Neu khong hoi trong LPS_WAIT_BARS
    va gia da di xa hon PHASE_E_MULT*rong_range -> Phase E ngay (Ca#21 CHART_CASES.md dong 554:
    Phase D KHONG bat buoc phai co BU/LPS). "Giu bien" chi tinh THAT BAI khi dong nen lui hang
    ro rang qua ben trong range (khong phai 1 rau nen cham nhe) — tranh vo hieu hoa vi nhieu 1 nen.
    Tra True neu da chot Phase E (dong range), False neu chua (giu Phase B/D de thu lai)."""
    N = len(B)
    end = min(N - 1, sos_i + LPS_WAIT_BARS)
    level = r.high if ACC else r.low
    fail_tol = 3.0 * ST_TOL_TICKS * TICK   # nguong "that bai that su" (khong phai nhieu 1 nen)
    pull_bars = []
    peak = B[sos_i]['hi'] if ACC else B[sos_i]['lo']
    range_height = max(1e-9, r.high - r.low)
    for j in range(sos_i + 1, end + 1):
        bj = B[j]
        if ACC:
            if bj['hi'] > peak:
                peak = bj['hi']
            failed = bj['c'] < level - fail_tol
            near_level = abs(bj['c'] - level) <= 2.0 * ST_TOL_TICKS * TICK
        else:
            if bj['lo'] < peak:
                peak = bj['lo']
            failed = bj['c'] > level + fail_tol
            near_level = abs(bj['c'] - level) <= 2.0 * ST_TOL_TICKS * TICK
        if failed:
            return False   # SOS/SOW that bai ro rang (dong nen lui han vao trong range)
        if near_level:
            pull_bars.append(j)
        moved_far = (peak - level) if ACC else (level - peak)
        if moved_far >= PHASE_E_MULT * range_height:
            if pull_bars:
                _emit_lps(B, r, pull_bars, ACC)
            r.set_phase(j, 'E')
            return True
    if pull_bars:
        _emit_lps(B, r, pull_bars, ACC)
    if (end - sos_i) >= LPS_WAIT_BARS:
        r.set_phase(end, 'E')
        return True
    return False


def _emit_lps(B, r, pull_bars, ACC):
    label = 'LPS' if ACC else 'LPSY'
    if len(pull_bars) >= LPS_AREA_MIN_BARS:
        lo_p = min(B[k]['lo'] for k in pull_bars)
        hi_p = max(B[k]['hi'] for k in pull_bars)
        r.add_event(pull_bars[len(pull_bars) // 2], f'{label}(vùng {pull_bars[0]}-{pull_bars[-1]})',
                    (lo_p + hi_p) / 2, 'D')
    else:
        k = pull_bars[-1]
        r.add_event(k, label, B[k]['lo'] if ACC else B[k]['hi'], 'D')


# ============================================================================
# Thong ke nhanh (khong ve anh) — chay truc tiep de kiem tra logic tren du lieu that
# ============================================================================
def main():
    B = E.load_m1()
    print(f"M1={len(B)} nen  {B[0]['dt']} -> {B[-1]['dt']} (UTC)")
    ranges = detect(B)
    acc = [r for r in ranges if r.kind == 'ACC']
    dist = [r for r in ranges if r.kind == 'DIST']
    print(f"\nTong so range phat hien: {len(ranges)}  (ACC={len(acc)}  DIST={len(dist)})")
    print(f"  completed (toi Phase E)={sum(1 for r in ranges if r.status=='completed')}  "
          f"active (chua xong)={sum(1 for r in ranges if r.status=='active')}")

    for tag, group in (('TICH LUY (ACC)', acc), ('PHAN PHOI (DIST)', dist)):
        print(f"\n=== {tag}: {len(group)} range ===")
        for k, r in enumerate(group[:15], 1):
            dur = (r.end_i or len(B) - 1) - r.start_i
            evs = ";".join(f"{e['label']}@{B[e['i']]['dt'].strftime('%m-%d %H:%M')}"
                           for e in sorted(r.events, key=lambda e: e['i']))
            phs = ";".join(f"{p[0]}[{B[p[1]]['dt'].strftime('%m-%d %H:%M')}.."
                           f"{B[p[2]]['dt'].strftime('%m-%d %H:%M') if p[2] else '...'}]" for p in r.phases)
            print(f"  #{k} [{r.status}] {B[r.start_i]['dt']} -> "
                  f"{B[r.end_i]['dt'] if r.end_i else '(dang chay)'} ({dur} nen) "
                  f"low={r.low:.1f} high={r.high:.1f}")
            print(f"     su_kien: {evs}")
            print(f"     phase:   {phs}")


if __name__ == '__main__':
    main()
