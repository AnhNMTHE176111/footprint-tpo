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

# ============================================================================
# v3 — nguoi hoc review 2026-08-03 (sua 2 loi NEN TANG)
# ============================================================================
# LOI 1: climax MOT MINH khong du de mo range. Phai co MOT MOVE XU HUONG RO RANG ngay
#   truoc do bi cay climax chan lai. Truoc day chi dung b['trend'] (close vs close 480 nen,
#   tol 1.0 gia) — qua yeu, gia dang di ngang van thoa -> ve range tum lum.
#   Nay do MOVE THAT: do dai chan->climax, so nen, va HIEU SUAT HUONG (loai di ngang).
MOVE_LOOKBACK = 240        # so nen toi da nhin lai de tim CHAN cua move
MOVE_MIN_BARS = 20         # move phai keo dai it nhat bao nhieu nen (loai cu nhay 2-3 nen)
MOVE_MIN_ATR = 8.0         # do dai move >= x lan bien do TB 20 nen
MOVE_MIN_EFF = 0.35        # hieu suat huong = |net| / tong quang duong close-to-close.
                            # di thang -> ~1.0; di ngang loanh quanh -> ~0.05. 0.35 loai di ngang.

# LOI 2: Phase A thieu ST[A]. Phase A la mot CHoCH = DUNG 3 lan doi huong:
#   (1) move bi climax chan  -> bien thu nhat
#   (2) hoi nguoc len/xuong AR -> bien thu hai
#   (3) quay lai phia climax roi bi chan lan nua = ST[A] -> LUC NAY Phase A moi xong.
#   Khong co ST[A] thi chua thanh vung di ngang -> BO ung vien.
# He qua cua LOI 2, TU PHAT HIEN khi soi lai chart sau khi vá (KHONG co trong review cua nguoi hoc,
# co the go bo neu khong dong y): neu AR chi la mot cai ngo nguay vai gia sau mot move 35 gia thi
# "doi huong lan 2" khong co that, va nguong retrace 40% cua ST[A] tro nen vo nghia (40% cua mot
# khoang ti hon). Buoc AR phai hoi lai it nhat 30% do dai MOVE thi moi tinh la Automatic Rally.
AR_MIN_RETRACE_OF_MOVE = 0.30
AR_MAX_WAIT = 300          # cho toi ngan nay ma AR van chua du 30% move -> bo ung vien

STA_MAX_WAIT = 400         # khong tim thay ST[A] trong ngan nay (tinh tu AR) -> bo ung vien
STA_MIN_RETRACE = 0.40     # phai hoi >= 40% chieu cao (climax<->AR) ve phia climax
STA_CONFIRM_BARS = 5       # so nen khong tao cuc tri moi de coi la DA doi huong lan 3

# ============================================================================
# v4 — nguoi hoc review muc 5, 5.1, 5.2, 6, 7 (2026-08-03)
# ============================================================================
# LOI 3 (muc 5): thieu TAI TICH LUY / TAI PHAN PHOI. Huong cua MOVE truoc climax chi quyet dinh
#   LOAI CLIMAX (move giam -> SC, move tang -> BCLX), KHONG quyet dinh range se pha ve huong nao.
#   Co DU 4 pattern:
#       move giam + SC  -> pha LEN     = Tich luy        (ACC)
#       move giam + SC  -> pha XUONG   = Tai phan phoi   (RE-DIST)
#       move tang + BCLX-> pha XUONG   = Phan phoi       (DIST)
#       move tang + BCLX-> pha LEN     = Tai tich luy    (RE-ACC)
#   Truoc day pha "sai huong" bi coi la gia thuyet SAI va BO CA RANGE (61 range bi bo oan tren
#   toan lich su). Nay khong bo: chi DOI TEN range theo huong pha that.
#   => r.origin ('DOWN'|'UP') co dinh tu climax; r.dir (0/+1/-1) chot khi SOS/SOW that su xay ra.
#
# LOI 4 (muc 5): 2 bien chinh phai CO DINH sau Phase A; moi cu tham do ra ngoai chi noi rong
#   BIEN PHU (net dut), khong duoc keo bien chinh. Moi ben nhieu nhat 1 bien phu = cuc tri xa nhat;
#   co the co 0, 1 hoac 2 bien phu. SOS/SOW muon manh phai dong cua BUT QUA bien phu, khong chi
#   qua bien chinh.
#
# LOI 5 (muc 5.1): Spring vs Shakeout phan biet bang THOI GIAN quay lai, khong phai do sau.
#   Spring   = pha ra roi rut vao trong range RAT NHANH (<= SPRING_MAX_BARS nen).
#   Shakeout = pha ra, lung bung ngoai bien mot luc roi moi quay lai (mot SOW/SOS that bai).
#   Con neu dong cua han ngoai bien va cac nen sau du manh giu no o ngoai -> pha THAT (SOS/SOW).
#
# LOI 6 (muc 5): bo han nhan ST[B] ("no cha dung lam gi ca"). Cac test nhe o bien chi con
#   UA (canh AR khi origin=DOWN), DA (canh AR khi origin=UP), UT (tham do nhe canh climax khi
#   origin=UP) — deu chi noi rong bien phu, khong day range sang Phase C.
#
# LOI 7 (muc 6): Phase C case KHO (khong co Spring/Shakeout/UTAD) truoc day khong bao gio duoc ve.
#   Nay khi SOS/SOW ban truc tiep tu Phase B, gan NGUOC Phase C tu diem LPS[C]/LPSY[C] (nhip test
#   cuoi cung truoc cu pha) — "co Phase D roi moi xac dinh duoc Phase C".
SPRING_MAX_BARS = 4        # <= bao nhieu nen thi cu pha bien duoc coi la Spring (nhanh); lau hon = Shakeout
BREAK_HOLD_BARS = 3        # so nen LIEN TIEP dong cua han ngoai bien phu -> pha THAT (SOS/SOW)
BREAK_MAX_WAIT = 40        # o ngoai bien lau hon nay ma khong quay lai -> coi nhu da pha that
MINOR_POKE_TICKS = 15      # tham do nong hon nay + volume thuong = test NHE (UA/UT/DA), khong vao Phase C
RETRO_C_LOOKBACK = 60      # nhin lai bao nhieu nen de gan NGUOC Phase C (case kho)
SHOCK_MAX_WAIT = 120       # muc 6: "Phase C la phase NGAN NHAT" — cho lau hon nay ma khong ra
                            # SOS/SOW thi coi nhu shock chet, lui ve Phase B


def _find_move(B, i, acc):
    """Truoc nen climax i co mot MOVE xu huong that khong?
    acc=True  -> can move GIAM (climax SC chan day)
    acc=False -> can move TANG (climax BCLX chan dinh)
    Tra (ok, chan_i, do_dai, hieu_suat)."""
    lo_i = max(0, i - MOVE_LOOKBACK)
    if i - lo_i < MOVE_MIN_BARS:
        return (False, None, 0.0, 0.0)
    # climax phai la CUC TRI cua ca cua so — no dang CHAN move, khong phai nam giua move
    if acc:
        if B[i]['lo'] > min(B[k]['lo'] for k in range(lo_i, i)):
            return (False, None, 0.0, 0.0)
        pk = max(range(lo_i, i), key=lambda k: B[k]['hi'])   # chan move = dinh cao nhat
        length = B[pk]['hi'] - B[i]['lo']
    else:
        if B[i]['hi'] < max(B[k]['hi'] for k in range(lo_i, i)):
            return (False, None, 0.0, 0.0)
        pk = min(range(lo_i, i), key=lambda k: B[k]['lo'])   # chan move = day thap nhat
        length = B[i]['hi'] - B[pk]['lo']
    if i - pk < MOVE_MIN_BARS:
        return (False, pk, length, 0.0)
    avgr = _avg_range(B, i, CLIMAX_RANGE_LOOKBACK)
    if avgr <= 0 or length < MOVE_MIN_ATR * avgr:
        return (False, pk, length, 0.0)
    path = sum(abs(B[k]['c'] - B[k - 1]['c']) for k in range(pk + 1, i + 1))
    eff = length / path if path > 1e-9 else 0.0
    return (eff >= MOVE_MIN_EFF, pk, length, eff)


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
    __slots__ = ('start_i', 'end_i', 'origin', 'dir', 'low', 'high', 'solid_low', 'solid_high',
                 'events', 'phases', 'status', 'state', 'pending_shock', 'brk',
                 'climax_price', 'ar_i', 'ar_price', 'sta_i', 'sta_price',
                 'move_i', 'move_len', 'move_eff', 'st_ext', 'st_ext_i')

    def __init__(self, start_i, origin):
        self.start_i = start_i
        self.end_i = None
        self.origin = origin      # 'DOWN' = move giam bi SC chan | 'UP' = move tang bi BCLX chan
        self.dir = 0              # v4: 0 chua biet | +1 pha LEN | -1 pha XUONG (chot khi SOS/SOW)
        # --- bien PHU (net dut): cuc tri xa nhat da tung cham, luon bao trum bien chinh ---
        self.low = None
        self.high = None
        # --- bien CHINH (net lien): CO DINH sau Phase A, tao tu climax + AR ---
        self.solid_low = None
        self.solid_high = None
        self.climax_price = None  # day SC (origin DOWN) / dinh BCLX (origin UP)
        self.ar_i = None
        self.ar_price = None      # bien doi dien, tao boi AR
        self.sta_i = None
        self.sta_price = None     # ST[A] — lan doi huong thu 3, ket thuc Phase A
        self.move_i = None        # chan cua move truoc climax
        self.move_len = 0.0
        self.move_eff = 0.0
        self.st_ext = None        # cuc tri tam trong luc cho ST[A]
        self.st_ext_i = None
        self.events = []          # list of dict(i, label, price, phase, status)
        self.phases = []          # list of [phase_char, start_i, end_i(None=dang mo)]
        self.status = 'active'    # active | completed
        self.state = 'A'          # A(cho AR) | A_st | B | B_brk | C_pending | D
        self.pending_shock = None  # dict(price, target_edge, peak, event, dir, out_edge)
        self.brk = None           # v4: dict theo doi mot cu pha bien dang dien ra (state B_brk)

    @property
    def kind(self):
        """Ten range theo DU 4 pattern — chi chot duoc khi da biet huong pha (r.dir)."""
        if self.dir > 0:
            return 'ACC' if self.origin == 'DOWN' else 'RE-ACC'
        if self.dir < 0:
            return 'RE-DIST' if self.origin == 'DOWN' else 'DIST'
        return 'ACC?' if self.origin == 'DOWN' else 'DIST?'

    @property
    def kind_vn(self):
        return {'ACC': 'Tích lũy', 'RE-ACC': 'Tái tích lũy', 'DIST': 'Phân phối',
                'RE-DIST': 'Tái phân phối', 'ACC?': 'Chưa rõ (SC)',
                'DIST?': 'Chưa rõ (BCLX)'}[self.kind]

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
            # v3: dieu kien CAN la mot MOVE XU HUONG THAT bi cay climax nay chan lai.
            # (Thay hoan toan cho b['trend'] cu — xem chu thich _find_move.)
            if b['dn']:
                ok, pk, ln, eff = _find_move(B, i, acc=True)
                if not ok:
                    continue
                r = WyRange(i, 'DOWN')
                r.low = b['lo']
                r.climax_price = b['lo']
                r.move_i, r.move_len, r.move_eff = pk, ln, eff
                r.add_event(i, 'SC', b['lo'], 'A')
                r.set_phase(i, 'A')
                active = r
            elif b['up']:
                ok, pk, ln, eff = _find_move(B, i, acc=False)
                if not ok:
                    continue
                r = WyRange(i, 'UP')
                r.high = b['hi']
                r.climax_price = b['hi']
                r.move_i, r.move_len, r.move_eff = pk, ln, eff
                r.add_event(i, 'BCLX', b['hi'], 'A')
                r.set_phase(i, 'A')
                active = r
            continue

        r = active
        climax_i = r.start_i
        last_evt_i = r.events[-1]['i'] if r.events else climax_i
        gap_ok = (i - last_evt_i) >= ST_MIN_GAP_BARS
        tol = ST_TOL_TICKS * TICK
        fail_tol = 3.0 * ST_TOL_TICKS * TICK   # nguong "dong cua han ra ngoai", khong phai nhieu 1 nen

        # ---------------------------------------------------------------- guard: bo range thoai hoa
        # v4: do bang bien CHINH (co dinh) — bien phu noi rong ra ngoai khong lam range "qua cao".
        if r.solid_low is not None:
            height = r.solid_high - r.solid_low
        else:
            height = (r.high - r.low) if (r.high is not None and r.low is not None) else 0.0
        too_tall = height > MAX_RANGE_HEIGHT_PCT * b['c']
        too_long_ab = r.state in ('A', 'A_st', 'B', 'B_brk', 'C_pending') and (i - climax_i) > MAX_BARS_PHASE_AB
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
            if r.origin == 'DOWN':
                if b['lo'] < r.low:
                    r.low = b['lo']
            else:
                if b['hi'] > r.high:
                    r.high = b['hi']
            if i - climax_i > AR_LOOKBACK:
                # khong bat duoc AR ro rang trong cua so -> lay diem cuc tri da co lam AR tam
                if r.origin == 'DOWN':
                    ar_i = max(range(climax_i + 1, i + 1), key=lambda k: B[k]['hi'])
                    r.high = B[ar_i]['hi']
                    ar_price = r.high
                else:
                    ar_i = min(range(climax_i + 1, i + 1), key=lambda k: B[k]['lo'])
                    r.low = B[ar_i]['lo']
                    ar_price = r.low
                # AR phai la mot cu bat nguoc THAT (>=30% do dai move), khong phai cai ngo nguay
                if abs(ar_price - r.climax_price) < AR_MIN_RETRACE_OF_MOVE * max(1e-9, r.move_len):
                    if (i - climax_i) > AR_MAX_WAIT:
                        DISCARDED.append((r, 'Phase A: khong co AR that (bat nguoc <30% move)', i))
                        active = None
                    continue
                # CR-U (uu tien THAP, chi hien thi): AR qua sat climax (<=2 nen) -> co the chi la 1 cay
                # bac nhieu, khong giong 1 cu Automatic Rally that. KHONG doi nguong/luong xu ly.
                ar_label = 'AR (yếu)' if (ar_i - climax_i) <= 2 else 'AR'
                r.add_event(ar_i, ar_label, ar_price, 'A')
                r.ar_i, r.ar_price = ar_i, ar_price
                # BUG tim thay qua vong cham (giang vien-agent, khong co trong spec): truoc day dung
                # `i` (luon la climax_i+AR_LOOKBACK+1 CO DINH) lam moc bat dau Phase B, trong khi AR
                # (ar_i) thuong xay ra SOM HON nhieu trong cua so 40 nen — khien Phase A hien thi VE
                # DAI TOI TAN cuoi cua so co dinh thay vi dung ket thuc tai AR (§1.3: "Phase A = tu
                # climax den AR, bao gom ca 2 moc"). Danh gia tren 6 anh mau: xay ra CA 6/6 anh.
                # v3: CHUA duoc sang Phase B. Phase A chi xong khi co ST[A] (lan doi huong thu 3).
                r.state = 'A_st'
                r.st_ext = B[i]['lo'] if r.origin == 'DOWN' else B[i]['hi']
                r.st_ext_i = i
            continue

        # ------------------------------------------------- state A_st: cho ST[A] = lan doi huong thu 3
        # Sau AR, gia phai quay lai phia climax du sau (>=40% chieu cao) roi BI CHAN lan nua. Khi da
        # doi huong (STA_CONFIRM_BARS nen khong tao cuc tri moi) thi Phase A ket thuc DUNG tai do.
        # Khong co ST[A] -> chua thanh vung di ngang -> bo ung vien (dung ly thuyet CHoCH 3 lan doi dau).
        if r.state == 'A_st':
            span = abs(r.ar_price - r.climax_price)
            if span < 1e-9:
                DISCARDED.append((r, 'Phase A: climax va AR trung nhau', i))
                active = None
                continue
            if r.origin == 'DOWN':
                if b['hi'] > r.high:      # AR duoc day cao hon -> cap nhat bien doi dien
                    r.high = b['hi']
                    r.ar_i, r.ar_price = i, b['hi']
                    r.st_ext, r.st_ext_i = b['lo'], i
                if b['lo'] < r.st_ext:
                    r.st_ext, r.st_ext_i = b['lo'], i
                retrace = (r.ar_price - r.st_ext) / max(1e-9, r.ar_price - r.climax_price)
            else:
                if b['lo'] < r.low:
                    r.low = b['lo']
                    r.ar_i, r.ar_price = i, b['lo']
                    r.st_ext, r.st_ext_i = b['hi'], i
                if b['hi'] > r.st_ext:
                    r.st_ext, r.st_ext_i = b['hi'], i
                retrace = (r.st_ext - r.ar_price) / max(1e-9, r.climax_price - r.ar_price)

            if retrace >= STA_MIN_RETRACE and (i - r.st_ext_i) >= STA_CONFIRM_BARS:
                r.sta_i, r.sta_price = r.st_ext_i, r.st_ext
                r.add_event(r.sta_i, 'ST[A]', r.sta_price, 'A')
                # v4: DONG BANG 2 bien CHINH (net lien) tai day = muc climax + muc AR.
                r.solid_low = min(r.climax_price, r.ar_price)
                r.solid_high = max(r.climax_price, r.ar_price)
                # ST[A] vuot QUA climax -> tao BIEN PHU (net dut) rong hon
                if r.origin == 'DOWN':
                    r.low = min(r.low, r.sta_price)
                else:
                    r.high = max(r.high, r.sta_price)
                r.low = min(r.low, r.solid_low)
                r.high = max(r.high, r.solid_high)
                r.set_phase(r.sta_i + 1, 'B')
                r.state = 'B'
            elif (i - r.ar_i) > STA_MAX_WAIT:
                DISCARDED.append((r, 'Phase A: khong co ST[A] (chua du 3 lan doi huong)', i))
                active = None
            continue

        # ==================================================== state B: cho MOT cu pha bien (bat ky canh nao)
        # v4: 2 bien CHINH da co dinh. Moi nen chi hoi mot cau: gia co tham do RA NGOAI bien chinh khong?
        # Neu co -> chuyen sang theo doi cu pha do (state B_brk) de biet no la Spring/Shakeout/UT...
        # (quay lai trong range) hay la SOS/SOW that (o han ben ngoai).
        if r.state == 'B':
            pen_lo = (r.solid_low - b['lo']) / TICK
            pen_hi = (b['hi'] - r.solid_high) / TICK
            side = 0
            if max(pen_lo, pen_hi) > ST_TOL_TICKS:
                side = -1 if pen_lo >= pen_hi else 1
            # Bien PHU chi noi rong bang cu tham do THAT BAI (gia rut ve trong range). Neu day la
            # khoi dau mot cu pha that thi doan gia di ra ngoai thuoc XU HUONG MOI, khong phai bien
            # cua vung can bang -> KHONG noi bien o day, doi ket cuc trong state B_brk.
            if side != -1 and b['lo'] < r.low:
                r.low = b['lo']
            if side != 1 and b['hi'] > r.high:
                r.high = b['hi']
            if side != 0:
                r.brk = dict(side=side, start_i=i, hold=0, vmax=b['vratio'],
                             ext=b['lo'] if side < 0 else b['hi'], ext_i=i,
                             out0=r.low if side < 0 else r.high)
                r.state = 'B_brk'
            # (khong `continue`: neu vua mo B_brk thi xu ly luon chinh cay nen nay ben duoi)

        # ============================== state B_brk: theo doi cu pha bien den khi ro ket cuc (v4, muc 5.1)
        if r.state == 'B_brk':
            k = r.brk
            up_side = k['side'] > 0
            edge = r.solid_high if up_side else r.solid_low
            out_edge = max(k['out0'], edge) if up_side else min(k['out0'], edge)
            k['vmax'] = max(k['vmax'], b['vratio'])
            if up_side:
                if b['hi'] > k['ext']:
                    k['ext'], k['ext_i'] = b['hi'], i
                back_in = b['c'] < edge - 1e-9
                decisive = b['c'] > out_edge + fail_tol and b['brat'] >= SOS_BODY_MIN
            else:
                if b['lo'] < k['ext']:
                    k['ext'], k['ext_i'] = b['lo'], i
                back_in = b['c'] > edge + 1e-9
                decisive = b['c'] < out_edge - fail_tol and b['brat'] >= SOS_BODY_MIN
            bars_out = i - k['start_i']

            if back_in:
                # cu pha THAT BAI — gia da rut ve trong range. Gio moi noi BIEN PHU bang cuc tri
                # cua cu tham do nay (xem chu thich o state B).
                if up_side:
                    r.high = max(r.high, k['ext'])
                else:
                    r.low = min(r.low, k['ext'])
                depth_t = abs(k['ext'] - edge) / TICK
                minor = depth_t < MINOR_POKE_TICKS and k['vmax'] < 1.5 * VSA_CLIMAX
                climax_side = up_side == (r.origin == 'UP')
                r.brk = None
                r.state = 'B'
                if not climax_side:
                    # tham do canh AR: luon la su kien Phase B (khong quyet dinh), chi noi bien phu
                    _mark_outer(r, k['ext_i'], 'UA' if up_side else 'DA', k['ext'], up_side)
                elif minor:
                    # tham do NHE canh climax. origin UP -> UT (upthrust nhe). origin DOWN -> day chinh
                    # la ST[B], nguoi hoc yeu cau BO han nhan nay -> chi noi bien phu, khong ghi su kien.
                    if r.origin == 'UP':
                        _mark_outer(r, k['ext_i'], 'UT', k['ext'], up_side)
                else:
                    # cu shock THAT o canh climax -> Phase C (muc 6: "de nhat de xac dinh Phase C")
                    if up_side:
                        label, tgt, sdir = 'UTAD', r.solid_low, -1
                    else:
                        # muc 5.1: phan biet bang THOI GIAN quay lai, khong phai do sau
                        label = 'Spring' if bars_out <= SPRING_MAX_BARS else 'Shakeout'
                        tgt, sdir = r.solid_high, 1
                    ev = r.add_event(k['ext_i'], label, k['ext'], 'C', status='pending')
                    r.pending_shock = dict(price=k['ext'], target_edge=tgt, peak=k['ext'], event=ev,
                                           dir=sdir, out_edge=(r.low if sdir < 0 else r.high),
                                           lps_done=False, start_i=k['ext_i'])
                    r.set_phase(k['ext_i'], 'C')
                    r.state = 'C_pending'
                continue

            k['hold'] = k['hold'] + 1 if decisive else 0
            if k['hold'] >= BREAK_HOLD_BARS or bars_out > BREAK_MAX_WAIT:
                # muc 5.1/5.2: dong cua han ngoai bien + cac nen sau du manh giu no o ngoai = pha THAT.
                # KHONG bo range nua — chi chot xem no thuoc pattern nao trong 4 pattern.
                _fire_break(B, r, i, up_side, out_edge)
            else:
                continue

        # ==================================================== state C_pending: xac nhan/that bai shock (FIX CR-I)
        if r.state == 'C_pending':
            shock = r.pending_shock
            span = max(1e-9, abs(shock['target_edge'] - shock['price']))
            # Tu phat hien khi test (NGOAI spec, khong co trong pseudocode goc §3.5): r.low/r.high
            # phai duoc cap nhat THU DONG bang cuc tri that trong luc cho shock (giong cach Phase B/D
            # da lam) — neu khong, mot SOS/SOW ban sau co the so sanh voi bien CU (khong con la cuc
            # tri that cua toan range), vi pham dung ràng buoc CR-C ("phai pha DINH/DAY CAO/THAP NHAT
            # tuyet doi"). Da bat qua truong hop nay tren du lieu that: mot cu UTAD (DIST) tiep tuc dao
            # xuong sau khi da "confirmed" ma r.low khong duoc cap nhat theo.
            up = shock['dir'] > 0
            if up:
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

            # muc 6: Phase C la phase NGAN NHAT — cho qua lau khong ra SOS/SOW thi shock da chet
            if (i - shock['start_i']) > SHOCK_MAX_WAIT:
                shock['event']['status'] = 'failed'
                shock['event']['label'] += ' (thất bại)'
                r.pending_shock = None
                r.set_phase(i, 'B')
                r.state = 'B'
            elif failed_now and progress < SHOCK_PROGRESS_MULT:
                # "nga re truoc khi toi khu vuc doi dien" = cau truc that bai dung THEORY §9 — lui ve
                # Phase B (khong huy toan bo range), tiep tuc do Spring/UT moi.
                shock['event']['status'] = 'failed'
                shock['event']['label'] = shock['event']['label'] + ' (thất bại)'
                r.pending_shock = None
                if up:
                    r.low = min(r.low, b['lo'])
                else:
                    r.high = max(r.high, b['hi'])
                r.set_phase(i, 'B')
                r.state = 'B'
            else:
                if progress >= SHOCK_PROGRESS_MULT and shock['event']['status'] == 'pending':
                    shock['event']['status'] = 'confirmed'

                # muc 5: SOS/SOW phai but qua BIEN PHU (out_edge) moi tinh la manh
                oe = shock['out_edge']
                broke = (b['c'] > oe + tol) if up else (b['c'] < oe - tol)
                if broke and b['brat'] >= SOS_BODY_MIN and gap_ok:
                    r.pending_shock = None
                    _fire_break(B, r, i, up, oe)
                elif (gap_ok and not shock['lps_done']
                        and abs(b['c'] - shock['price']) <= 2.0 * tol):
                    # CR-M: test trong luc CHO xac nhan shock (truoc SOS/SOW) = LPS[C]/LPSY[C].
                    # v4 (nguoi hoc 2026-08-03): CHI danh dau 1 diem duy nhat.
                    r.add_event(i, 'LPS[C]' if up else 'LPSY[C]', b['c'], 'C')
                    shock['lps_done'] = True

        # ---------------------------------------------------------------- da pha xong -> dong range
        # BUG tim thay khi test (KHONG co trong spec, tu phat hien): _try_lps_and_phase_e() nhin-truoc
        # toi da LPS_WAIT_BARS nen va co the chot Phase E tai nen j > i (bar dang xu ly). Dung `i` o day
        # (thay vi e_start=j da duoc set_phase() ghi nhan dung) lam end_i/EndIdx cua ca range lui VE
        # TRUOC ca luc Phase D/E thuc su dien ra -> Range High/Low ve ngan hon Phase D/E that (da quan
        # sat truc tiep tren anh preview: end_i trung voi nen SOS, trong khi Phase D/E hien thi xa hon).
        if r.state == 'END':
            last = r.phases[-1]
            if last[0] == 'E':
                e_end = max(last[1], min(len(B) - 1, i))
            else:
                # Phase D nhung chua chay du xa de goi la E — van dong range, chi ve het cua so hoi
                e_end = max(last[1], min(len(B) - 1, i + LPS_WAIT_BARS))
            last[2] = e_end
            r.end_i = e_end
            r.status = 'completed'
            ranges.append(r)
            active = None

    if active is not None:
        if active.phases:
            active.phases[-1][2] = len(B) - 1
        ranges.append(active)
    return ranges


def _mark_outer(r, i, label, price, up_side):
    """muc 5: moi ben chi co MOT bien phu — "bien phu cu bien mat, bien phu moi tiep tuc noi ra".
    Nhan UA/DA/UT vi vay cung chi giu DUY NHAT mot cai o cuc tri xa nhat cua ben do; cham nong hon
    cuc tri cu thi khong ghi gi ca."""
    old = [e for e in r.events if e['label'] in ('UA', 'DA', 'UT')
           and ((e['price'] > r.solid_high) if up_side else (e['price'] < r.solid_low))]
    for e in old:
        if (price <= e['price']) if up_side else (price >= e['price']):
            return    # chua vuot duoc bien phu cu -> khong tao nhan moi
        r.events.remove(e)
    r.add_event(i, label, price, r.phases[-1][0])


def _fire_break(B, r, i, up, out_edge):
    """v4 (muc 5.1/5.2): mot cu pha bien da duoc XAC NHAN. Khong con chuyen "gia thuyet sai -> bo
    range" — huong pha chi quyet dinh range thuoc pattern nao trong 4 pattern (xem LOI 3).
    Neu range chua tung co Phase C (case KHO cua muc 6) thi gan NGUOC Phase C tai day."""
    r.dir = 1 if up else -1
    r.brk = None
    r.pending_shock = None
    if not any(p[0] == 'C' for p in r.phases):
        _retro_phase_c(B, r, i, up)
    r.add_event(i, 'SOS' if up else 'SOW', B[i]['c'], 'D')
    r.set_phase(i, 'D')
    _try_lps_and_phase_e(B, r, i, up, out_edge)   # co the chot them Phase E
    # v4: cu pha da duoc XAC NHAN (3 nen lien tiep dong han ngoai bien phu) -> vung dau gia nay
    # KET THUC. Truoc day neu Phase E khong dat thi lui ve Phase B, nhung luc do gia van con o
    # ngoai bien nen nen ke tiep lai ban SOS/SOW moi -> vong lap D->B->D vo tan (da do: mot range
    # ngay 16/07 ban 20 cai SOW lien tiep cach nhau dung 42 nen). Nay dong range luon.
    r.state = 'END'


def _retro_phase_c(B, r, sos_i, up):
    """muc 6, case KHO: khong co Spring/Shakeout/UTAD nao de nhan ra Phase C ngay luc do. Doi den
    khi SOS/SOW that su ban ra roi NHIN NGUOC lai — nhip test cuoi cung truoc cu pha chinh la
    LPS[C] (pha len) / LPSY[C] (pha xuong), va Phase C bat dau tu do ("co Phase D roi moi xac dinh
    duoc Phase C"). Chi 1 diem duy nhat (nguoi hoc 2026-08-03).

    Cua so nhin lai bi chan boi CA HAI: RETRO_C_LOOKBACK va MOT NUA do dai Phase B hien tai.
    Ly do (tu phat hien khi soi chart, khong co trong review): lay cuc tri cua ca 60 nen thi ngay
    sau ST[A] cuc tri thuong CHINH LA vung ST[A] -> Phase C an gan het range, Phase B chi con 2 nen,
    trai voi ca hai muc cua nguoi hoc ("Phase B la phase dai nhat", "Phase C la phase ngan nhat")."""
    b_start = r.phases[-1][1] if r.phases else r.start_i
    win = min(RETRO_C_LOOKBACK, max(1, (sos_i - b_start) // 2))
    lo_i = max(b_start + 1, sos_i - win)
    if sos_i - lo_i < 3:
        return
    if up:
        piv = min(range(lo_i, sos_i), key=lambda k: B[k]['lo'])
        price, label = B[piv]['lo'], 'LPS[C]'
    else:
        piv = max(range(lo_i, sos_i), key=lambda k: B[k]['hi'])
        price, label = B[piv]['hi'], 'LPSY[C]'
    r.set_phase(piv, 'C')
    r.add_event(piv, label, price, 'C')


def _try_lps_and_phase_e(B, r, sos_i, up, level):
    """muc 7: Phase D + E chinh la CBR — PHA bien, HOI ve retest nhung GIU duoc ben ngoai bien
    (nhip hoi do = LPS[D] / LPSY[D]), roi gia THUAN LUC di tiep de tim vung gia moi (Phase E).
    `level` = bien vua bi pha (bien PHU neu co, vi SOS/SOW phai but qua no).
    FIX CR-K: neu khong hoi va gia CHUA di du xa khi het LPS_WAIT_BARS, chi ep Phase E neu da dat
    >= PHASE_E_MIN_PROGRESS_MULT*PHASE_E_MULT tien do; khong du thi tra False (lui Phase B).
    "Giu bien" chi tinh THAT BAI khi dong nen lui han vao TRONG range (khong phai 1 rau nen cham nhe).
    Tra True neu da chot Phase E (dong range), False neu chua (lui Phase B de thu lai)."""
    ACC = up
    N = len(B)
    end = min(N - 1, sos_i + LPS_WAIT_BARS)
    fail_tol = 3.0 * ST_TOL_TICKS * TICK   # nguong "that bai that su" (khong phai nhieu 1 nen)
    pull_bars = []
    peak = B[sos_i]['hi'] if ACC else B[sos_i]['lo']
    range_height = max(1e-9, (r.solid_high - r.solid_low) if r.solid_low is not None
                       else (r.high - r.low))
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
    """v4 (nguoi hoc 2026-08-03): LPS[D]/LPSY[D] CHI danh dau 1 DIEM duy nhat — bo han kieu ve
    "(vùng)" cu. Diem chon = day sau nhat (pha len) / dinh cao nhat (pha xuong) cua nhip hoi."""
    label = 'LPS[D]' if ACC else 'LPSY[D]'   # CR-M: phan biet voi LPS[C]/LPSY[C]
    if not pull_bars:
        return
    k = min(pull_bars, key=lambda x: B[x]['lo']) if ACC else max(pull_bars, key=lambda x: B[x]['hi'])
    r.add_event(k, label, B[k]['lo'] if ACC else B[k]['hi'], 'D')


# ============================================================================
# Thong ke nhanh (khong ve anh) — chay truc tiep de kiem tra logic tren du lieu that
# ============================================================================
def main():
    B = E.load_m1()
    print(f"M1={len(B)} nen  {B[0]['dt']} -> {B[-1]['dt']} (UTC)")
    ranges = detect(B)
    print(f"\nTong so range phat hien: {len(ranges)}")
    print(f"  completed (toi Phase E)={sum(1 for r in ranges if r.status=='completed')}  "
          f"active (chua xong)={sum(1 for r in ranges if r.status=='active')}")

    for tag in ('ACC', 'RE-ACC', 'DIST', 'RE-DIST', 'ACC?', 'DIST?'):
        group = [r for r in ranges if r.kind == tag]
        if not group:
            continue
        print(f"\n=== {tag} ({group[0].kind_vn}): {len(group)} range ===")
        for k, r in enumerate(group[:15], 1):
            dur = (r.end_i or len(B) - 1) - r.start_i
            evs = ";".join(f"{e['label']}@{B[e['i']]['dt'].strftime('%m-%d %H:%M')}"
                           for e in sorted(r.events, key=lambda e: e['i']))
            phs = ";".join(f"{p[0]}[{B[p[1]]['dt'].strftime('%m-%d %H:%M')}.."
                           f"{B[p[2]]['dt'].strftime('%m-%d %H:%M') if p[2] else '...'}]" for p in r.phases)
            sl = f"{r.solid_low:.1f}-{r.solid_high:.1f}" if r.solid_low is not None else "chua chot"
            print(f"  #{k} [{r.status}] {B[r.start_i]['dt']} -> "
                  f"{B[r.end_i]['dt'] if r.end_i else '(dang chay)'} ({dur} nen) "
                  f"chinh={sl} phu={r.low:.1f}-{r.high:.1f}")
            print(f"     su_kien: {evs}")
            print(f"     phase:   {phs}")

    print("\n--- ly do BO ung vien ---")
    reasons = {}
    for _r, why, _i in DISCARDED:
        reasons[why] = reasons.get(why, 0) + 1
    for why, n in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"  {n:4d}  {why}")


if __name__ == '__main__':
    main()
