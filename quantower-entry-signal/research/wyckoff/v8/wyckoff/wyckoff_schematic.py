#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wyckoff_schematic.py — prototype PYTHON (chay truoc khi port C#) cho tinh nang MOI: tu dong
nhan dien Trading Range + Phase A-E + cac su kien Wyckoff (SC/BCLX, AR, ST, UA/DA, Spring/Shakeout,
UT/UTAD, SOS/SOW, LPS[C]/LPSY[C], LPS[D]/LPSY[D]) tren du lieu M1 THAT (dxFeed GCQ26), roi VE thu
len anh de kiem truc quan TRUOC khi dua vao WyckoffRunner.cs.

Nguon quy tac dung de code hoa (v2 — theo WYCKOFF_DRAW_SPEC.md, khong bay dat):
  - quantower-entry-signal/WYCKOFF_DRAW_SPEC.md  (spec DUY NHAT, tong hop THEORY.md + CHART_CASES.md
    ~70 ca bai chua hoc vien that + doi chieu code C# — day la nguon CHUAN cho file nay, moi thay doi
    thuat toan phai truy ve dung muc trong spec, khong tu suy dien them)
  - data-export/wyckoff/THEORY.md, CHART_CASES.md, WYCKOFF_RULES.md (nguon goc, xem trich dan trong spec)

Cac fix chinh so voi v1 (xem WYCKOFF_DRAW_SPEC.md §2 bang CR-*, §4 bang diff):
  - CR-H (uu tien CAO): Phase B theo doi DOC LAP ca 2 canh cua range — mot cu breakout QUYET DINH o
    canh chua tung co Spring/UTAD duoc phep ban SOS/SOW TRUC TIEP tu Phase B (bo qua Phase C).
  - CR-I (uu tien CAO, co che WY10/WY12): sau khi Spring/Shakeout/UTAD duoc gan nhan, theo doi
    PendingShock moi nen toi khi XAC NHAN (tien do >=50% quang duong toi bien doi dien) hoac THAT BAI
    (dong cua pha nguoc qua chinh cuc tri shock truoc khi dat 50%) — that bai thi lui ve Phase B.
  - CR-K (uu tien CAO): Phase E khong con ep buoc VO DIEU KIEN khi het LPS_WAIT_BARS — phai dat toi
    thieu 50% x PHASE_E_MULT tien do, khong thi lui ve Phase B.
  - CR-Y (uu tien CAO): moi nhanh lui state ve 'B' phai goi ca set_phase(i,'B') (truoc day chi doi
    bien noi bo r.state, timeline Phase hien thi bi sai).
  - CR-M (uu tien TRUNG BINH): tach nhan LPS[C]/LPSY[C] (test trong luc cho xac nhan shock, TRUOC
    SOS/SOW — thuoc Phase C) khoi LPS[D]/LPSY[D] (pullback SAU SOS/SOW — thuoc Phase D, giu nguyen
    logic diem/vung cu).
  - Them nhan UA (Upper-Area test, Phase B cua ACC — test canh tren KHONG quyet dinh) va DA (Down-
    Area test, Phase B cua DIST — test canh duoi KHONG quyet dinh), doi xung nhau (THEORY §5 + spec §1.10).
  - AR qua sat climax (<=2 nen) -> gan co hien thi "(yếu)" (CR-U, chi hien thi, khong doi nguong).

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
LPS_WAIT_BARS = 25           # so nen cho hoi sau SOS/SOW truoc khi xet Phase E / lui Phase B
LPS_AREA_MIN_BARS = 3        # >=3 nen dao dong hep quanh vung -> ve AREA (Loi#1 CHART_CASES.md)
PHASE_E_MULT = 1.0           # gia phai di xa hon RangeHeight*mult khoi bien pha de tinh la Phase E (100%)
SHOCK_PROGRESS_MULT = 0.5    # [MOI, spec §1.15/§3.5] tien do toi thieu (50%) de shock coi la dang tot;
                              # that bai neu dong cua pha nguoc qua cuc tri shock TRUOC khi dat muc nay
PHASE_E_MIN_PROGRESS_MULT = 0.5  # [MOI, CR-K] khi het LPS_WAIT_BARS: can >=50%*PHASE_E_MULT moi ep E,
                                  # khong thi lui Phase B (thay vi ep vo dieu kien nhu truoc)

# --- guard chong range "vo han" (KHONG co trong tai lieu goc — tu dat de tranh thoai hoa thuat
# toan khi gia trend that manh xuyen suot nhieu thang; TR Wyckoff that la vung CAN BANG hep,
# khong phai the hien ca mot xu huong dai) ---
MAX_RANGE_HEIGHT_PCT = 0.035   # bien do toi da ~3.5% gia hien tai — vuot nguong nay -> bo range
MAX_BARS_PHASE_AB = 2500       # qua ngan nay ma chua chot duoc Phase D (SOS/SOW that) -> bo, tim climax moi
MAX_BARS_PHASE_D = 2000        # qua ngan nay o Phase D ma khong chot duoc E -> bo


# Ung vien range da MO nhung bi BO giua chung (khong bao gio duoc ve). Chi de CHAN DOAN/review —
# detect() xoa sach moi lan chay, khong anh huong ket qua tra ve. Moi phan tu: (WyRange, ly_do, bar_bo).
DISCARDED = []


def _avg_range(B, i, lookback):
    lo = max(0, i - lookback)
    win = B[lo:i]
    if not win:
        return B[i]['rng']
    return sum(b['rng'] for b in win) / len(win)


class WyRange:
    __slots__ = ('start_i', 'end_i', 'kind', 'low', 'high', 'events', 'phases', 'status', 'state',
                 'pending_shock')

    def __init__(self, start_i, kind):
        self.start_i = start_i
        self.end_i = None
        self.kind = kind          # 'ACC' | 'DIST'
        self.low = None
        self.high = None
        self.events = []          # list of dict(i, label, price, phase, status)
        self.phases = []          # list of [phase_char, start_i, end_i(None=dang mo)]
        self.status = 'active'    # active | completed
        self.state = 'A'          # A(cho AR) | B | C_pending(cho xac nhan/that bai shock) | D
        self.pending_shock = None  # dict(price, target_edge, peak, event) — chi khi state=='C_pending'

    def add_event(self, i, label, price, phase, status=None):
        ev = dict(i=i, label=label, price=price, phase=phase, status=status)
        self.events.append(ev)
        return ev

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
    DISCARDED.clear()

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
            # Loi#3 (CHART_CASES.md, spec §1.8): SC/BCLX chi hop le neu TRUOC do la downtrend/uptrend
            # THAT. Dung field 'trend' (BASE TREND_LB, proxy TPO/close-vs-close) da co san trong B.
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
        too_long_ab = r.state in ('A', 'B', 'C_pending') and (i - climax_i) > MAX_BARS_PHASE_AB
        too_long_d = r.state == 'D' and (i - climax_i) > MAX_BARS_PHASE_D
        if too_tall or too_long_ab or too_long_d:
            DISCARDED.append((r, 'qua cao (>3.5% gia)' if too_tall else 'qua dai (>2500/2000 nen)', i))
            active = None   # bo, KHONG ghi vao ranges (gia thuyet khong tru thanh TR hop le)
            continue

        # ---------------------------------------------------------------- state A: cho AR
        if r.state == 'A':
            # BUG tim thay qua vong cham (giang vien-agent phat hien mot nen vuot Range High trong luc
            # con o Phase A, tu kiem tra lai xac nhan dung): AR chi cap nhat CANH DOI DIEN (r.low cho
            # DIST, r.high cho ACC) — canh CUNG PHIA voi climax (r.high cho DIST, r.low cho ACC) truoc
            # day KHONG duoc cap nhat gi trong suot ca cua so AR_LOOKBACK=40 nen, du gia co the con
            # day cao/thap hon chinh nen climax truoc khi that su dao chieu. Them cap nhat thu dong o
            # day (giong cach Phase B/C/D deu da lam) de r.high/r.low luon la cuc tri that.
            if r.kind == 'ACC':
                if b['lo'] < r.low:
                    r.low = b['lo']
            else:
                if b['hi'] > r.high:
                    r.high = b['hi']
            if i - climax_i > AR_LOOKBACK:
                # khong bat duoc AR ro rang trong cua so -> lay diem cuc tri da co lam AR tam
                if r.kind == 'ACC':
                    ar_i = max(range(climax_i + 1, i + 1), key=lambda k: B[k]['hi'])
                    r.high = B[ar_i]['hi']
                    ar_price = r.high
                else:
                    ar_i = min(range(climax_i + 1, i + 1), key=lambda k: B[k]['lo'])
                    r.low = B[ar_i]['lo']
                    ar_price = r.low
                # CR-U (uu tien THAP, chi hien thi): AR qua sat climax (<=2 nen) -> co the chi la 1 cay
                # bac nhieu, khong giong 1 cu Automatic Rally that. KHONG doi nguong/luong xu ly.
                ar_label = 'AR (yếu)' if (ar_i - climax_i) <= 2 else 'AR'
                r.add_event(ar_i, ar_label, ar_price, 'A')
                # BUG tim thay qua vong cham (giang vien-agent, khong co trong spec): truoc day dung
                # `i` (luon la climax_i+AR_LOOKBACK+1 CO DINH) lam moc bat dau Phase B, trong khi AR
                # (ar_i) thuong xay ra SOM HON nhieu trong cua so 40 nen — khien Phase A hien thi VE
                # DAI TOI TAN cuoi cua so co dinh thay vi dung ket thuc tai AR (§1.3: "Phase A = tu
                # climax den AR, bao gom ca 2 moc"). Danh gia tren 6 anh mau: xay ra CA 6/6 anh.
                r.set_phase(ar_i + 1, 'B')
                r.state = 'B'
            continue

        abandon_b = False

        # ==================================================== state B: theo doi CA HAI CANH DOC LAP (FIX CR-H)
        if r.state == 'B':
            fail_tol_b = 3.0 * ST_TOL_TICKS * TICK

            # ---- canh duoi ----
            if b['lo'] < r.low - 1e-9 and b['c'] > r.low and gap_ok:
                depth_t = (r.low - b['lo']) / TICK
                is_shake = depth_t >= 15 or b['vratio'] >= 1.5 * VSA_CLIMAX
                r.low = b['lo']
                if r.kind == 'ACC':
                    label = 'Shakeout' if is_shake else 'Spring'
                    ev = r.add_event(i, label, b['lo'], 'C', status='pending')
                    r.pending_shock = dict(price=b['lo'], target_edge=r.high, peak=b['lo'], event=ev)
                    r.set_phase(i, 'C')
                    r.state = 'C_pending'
                else:
                    # DIST: test canh duoi KHONG quyet dinh (khong phai UTAD ben tren) -> DA, o lai B
                    label = 'DA (sâu)' if is_shake else 'DA'
                    r.add_event(i, label, b['lo'], r.phases[-1][0])
            elif abs(b['lo'] - r.low) <= tol and gap_ok:
                r.add_event(i, 'ST', b['lo'], r.phases[-1][0])
                r.low = min(r.low, b['lo'])
            elif b['c'] < r.low - fail_tol_b and b['brat'] >= SOS_BODY_MIN and gap_ok:
                if r.kind == 'ACC':
                    # dong nen lui HAN qua duoi (khong dao nguoc = khong phai Spring) -> gia thuyet
                    # Tich luy SAI (that su la breakdown) -> bo range (THEORY §9 "cau truc that bai")
                    abandon_b = True
                else:
                    # FIX CR-H: SOW hop le ban TRUC TIEP tu Phase B (canh nay chua tung co UTAD)
                    r.low = b['lo']
                    r.add_event(i, 'SOW', b['c'], 'D')
                    r.set_phase(i, 'D')
                    r.state = 'D'
                    closed = _try_lps_and_phase_e(B, r, i, ACC=False)
                    if not closed:
                        r.state = 'B'
                        r.set_phase(i, 'B')   # FIX CR-Y
            elif b['lo'] < r.low:
                r.low = b['lo']   # mo rong bien am tham, chua du dieu kien gan nhan (thieu gap_ok)

            if abandon_b:
                DISCARDED.append((r, 'Phase B: dong cua pha SAI huong -> bo gia thuyet', i))
                active = None
                continue

            # ---- canh tren (chi xet neu van con o Phase B — canh duoi co the da chuyen C_pending/D) ----
            if r.state == 'B':
                if b['hi'] > r.high + 1e-9 and b['c'] < r.high and gap_ok:
                    depth_t = (b['hi'] - r.high) / TICK
                    is_utad = depth_t >= 15 or b['vratio'] >= 1.5 * VSA_CLIMAX
                    r.high = b['hi']
                    if r.kind == 'DIST':
                        label = 'UTAD' if is_utad else 'UT'
                        ev = r.add_event(i, label, b['hi'], 'C' if is_utad else r.phases[-1][0],
                                          status='pending' if is_utad else None)
                        if is_utad:
                            r.pending_shock = dict(price=b['hi'], target_edge=r.low, peak=b['hi'], event=ev)
                            r.set_phase(i, 'C')
                            r.state = 'C_pending'
                        # UT thuong (khong du sau/du volume): chi ghi nhan, o lai Phase B
                    else:
                        # ACC: test canh tren KHONG quyet dinh (khong phai Spring/Shakeout ben duoi) -> UA
                        label = 'UA (mạnh)' if is_utad else 'UA'
                        r.add_event(i, label, b['hi'], r.phases[-1][0])
                elif abs(b['hi'] - r.high) <= tol and gap_ok:
                    r.add_event(i, 'ST', b['hi'], r.phases[-1][0])
                    r.high = max(r.high, b['hi'])
                elif b['c'] > r.high + fail_tol_b and b['brat'] >= SOS_BODY_MIN and gap_ok:
                    if r.kind == 'DIST':
                        abandon_b = True   # pha THAT len (khong dao nguoc) -> gia thuyet Phan phoi sai
                    else:
                        # FIX CR-H: SOS hop le ban TRUC TIEP tu Phase B
                        r.high = b['hi']
                        r.add_event(i, 'SOS', b['c'], 'D')
                        r.set_phase(i, 'D')
                        r.state = 'D'
                        closed = _try_lps_and_phase_e(B, r, i, ACC=True)
                        if not closed:
                            r.state = 'B'
                            r.set_phase(i, 'B')   # FIX CR-Y
                elif b['hi'] > r.high:
                    r.high = b['hi']

            if abandon_b:
                DISCARDED.append((r, 'Phase B: dong cua pha SAI huong -> bo gia thuyet', i))
                active = None
                continue

        # ==================================================== state C_pending: xac nhan/that bai shock (FIX CR-I)
        elif r.state == 'C_pending':
            shock = r.pending_shock
            span = max(1e-9, abs(shock['target_edge'] - shock['price']))
            # Tu phat hien khi test (NGOAI spec, khong co trong pseudocode goc §3.5): r.low/r.high
            # phai duoc cap nhat THU DONG bang cuc tri that trong luc cho shock (giong cach Phase B/D
            # da lam) — neu khong, mot SOS/SOW ban sau co the so sanh voi bien CU (khong con la cuc
            # tri that cua toan range), vi pham dung ràng buoc CR-C ("phai pha DINH/DAY CAO/THAP NHAT
            # tuyet doi"). Da bat qua truong hop nay tren du lieu that: mot cu UTAD (DIST) tiep tuc dao
            # xuong sau khi da "confirmed" ma r.low khong duoc cap nhat theo.
            if r.kind == 'ACC':
                if b['hi'] > shock['peak']:
                    shock['peak'] = b['hi']
                if b['hi'] > r.high:
                    r.high = b['hi']
                progress = (shock['peak'] - shock['price']) / span
                failed_now = b['c'] < shock['price'] - tol
            else:
                if b['lo'] < shock['peak']:
                    shock['peak'] = b['lo']
                if b['lo'] < r.low:
                    r.low = b['lo']
                progress = (shock['price'] - shock['peak']) / span
                failed_now = b['c'] > shock['price'] + tol

            if failed_now and progress < SHOCK_PROGRESS_MULT:
                # "nga re truoc khi toi khu vuc doi dien" = cau truc that bai dung THEORY §9 — lui ve
                # Phase B (khong huy toan bo range), tiep tuc do Spring/UT moi.
                shock['event']['status'] = 'failed'
                shock['event']['label'] = shock['event']['label'] + ' (thất bại)'
                r.pending_shock = None
                if r.kind == 'ACC':
                    r.low = min(r.low, b['lo'])
                else:
                    r.high = max(r.high, b['hi'])
                r.set_phase(i, 'B')
                r.state = 'B'
            else:
                if progress >= SHOCK_PROGRESS_MULT and shock['event']['status'] == 'pending':
                    shock['event']['status'] = 'confirmed'

                if r.kind == 'ACC' and b['c'] > r.high + tol and b['brat'] >= SOS_BODY_MIN and gap_ok:
                    r.high = max(r.high, b['hi'])
                    r.add_event(i, 'SOS', b['c'], 'D')
                    r.pending_shock = None
                    r.set_phase(i, 'D')
                    r.state = 'D'
                    closed = _try_lps_and_phase_e(B, r, i, ACC=True)
                    if not closed:
                        r.state = 'B'
                        r.set_phase(i, 'B')   # FIX CR-Y
                elif r.kind == 'DIST' and b['c'] < r.low - tol and b['brat'] >= SOS_BODY_MIN and gap_ok:
                    r.low = min(r.low, b['lo'])
                    r.add_event(i, 'SOW', b['c'], 'D')
                    r.pending_shock = None
                    r.set_phase(i, 'D')
                    r.state = 'D'
                    closed = _try_lps_and_phase_e(B, r, i, ACC=False)
                    if not closed:
                        r.state = 'B'
                        r.set_phase(i, 'B')   # FIX CR-Y
                elif gap_ok and abs(b['c'] - shock['price']) <= 2.0 * tol:
                    # CR-M: test trong luc CHO xac nhan shock (truoc SOS/SOW) = LPS[C]/LPSY[C],
                    # khac voi LPS[D]/LPSY[D] (pullback SAU SOS/SOW, xem _emit_lps).
                    r.add_event(i, 'LPS[C]' if r.kind == 'ACC' else 'LPSY[C]', b['c'], 'C')

        # ==================================================== state D: CHI tim SOS/SOW cung phia (khong doi)
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
                r.state = 'B'   # breakout chua "di xa" duoc (that bai/chua xac nhan) -> ve lai Phase B
                r.set_phase(i, 'B')   # FIX CR-Y
            elif not fired:
                # gia pha them cuc tri nhung KHONG du than/VSA de tinh la SOS that -> chi mo rong bien am tham
                if r.kind == 'ACC' and b['lo'] < r.low:
                    r.low = b['lo']
                elif r.kind == 'DIST' and b['hi'] > r.high:
                    r.high = b['hi']

        # ---------------------------------------------------------------- da vao Phase E -> dong range
        # BUG tim thay khi test (KHONG co trong spec, tu phat hien): _try_lps_and_phase_e() nhin-truoc
        # toi da LPS_WAIT_BARS nen va co the chot Phase E tai nen j > i (bar dang xu ly). Dung `i` o day
        # (thay vi e_start=j da duoc set_phase() ghi nhan dung) lam end_i/EndIdx cua ca range lui VE
        # TRUOC ca luc Phase D/E thuc su dien ra -> Range High/Low ve ngan hon Phase D/E that (da quan
        # sat truc tiep tren anh preview: end_i trung voi nen SOS, trong khi Phase D/E hien thi xa hon).
        if r.phases and r.phases[-1][0] == 'E':
            e_start = r.phases[-1][1]
            e_end = max(e_start, min(len(B) - 1, i))
            r.phases[-1][2] = e_end
            r.end_i = e_end
            r.status = 'completed'
            ranges.append(r)
            active = None

    if active is not None:
        if active.phases:
            active.phases[-1][2] = len(B) - 1
        ranges.append(active)
    return ranges


def _try_lps_and_phase_e(B, r, sos_i, ACC):
    """Sau SOS/SOW: tim nhip hoi GIU bien (LPS[D]/LPSY[D]). Neu hoi >=3 nen dao dong hep -> AREA
    (Loi#1 CHART_CASES.md), neu 1-2 nen -> POINT. FIX CR-K: neu khong hoi va gia CHUA di du xa khi
    het LPS_WAIT_BARS, chi ep Phase E neu da dat >= PHASE_E_MIN_PROGRESS_MULT*PHASE_E_MULT tien do —
    khong con ep VO DIEU KIEN nhu truoc; khong du thi tra False (lui Phase B, cho test/SOS moi).
    "Giu bien" chi tinh THAT BAI khi dong nen lui han qua ben trong range (khong phai 1 rau nen cham
    nhe) — tranh vo hieu hoa vi nhieu 1 nen.
    Tra True neu da chot Phase E (dong range), False neu chua (lui Phase B de thu lai)."""
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
        final_moved_far = (peak - level) if ACC else (level - peak)
        if final_moved_far >= PHASE_E_MIN_PROGRESS_MULT * PHASE_E_MULT * range_height:
            r.set_phase(end, 'E')
            return True
        return False   # FIX CR-K: SOS/SOW qua yeu (chua di du xa) -> lui Phase B, khong ep E
    return False


def _emit_lps(B, r, pull_bars, ACC):
    label = 'LPS[D]' if ACC else 'LPSY[D]'   # CR-M: doi ten so voi 'LPS'/'LPSY' cu — phan biet voi LPS[C]/LPSY[C]
    if len(pull_bars) >= LPS_AREA_MIN_BARS:
        # BUG tim thay khi cham (giang vien-agent): nhan cu ghi CHI SO NEN (pull_bars[0]-pull_bars[-1],
        # vd "47637-47648") thay vi GIA — nguoi xem tuong nham la khoang gia, hoan toan sai don vi va
        # gay hieu lam nghiem trong. Doi thanh "(vùng)" don gian; gia that da co san o vi tri diem ve
        # (trung binh lo_p/hi_p, hien thi dung tren truc gia cua chart).
        lo_p = min(B[k]['lo'] for k in pull_bars)
        hi_p = max(B[k]['hi'] for k in pull_bars)
        r.add_event(pull_bars[len(pull_bars) // 2], f'{label}(vùng)',
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
