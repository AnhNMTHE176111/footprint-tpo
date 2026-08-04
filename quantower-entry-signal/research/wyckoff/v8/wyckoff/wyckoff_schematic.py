#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wyckoff_schematic.py — prototype PYTHON (chay truoc khi port C#) cho tinh nang tu dong nhan dien
Trading Range + Phase A-E + cac su kien Wyckoff (SC/BCLX, AR, ST[A], UA/UT/DA, mSOS/mSOW,
Spring/Shakeout/UTAD, SOS/SOW, LPS[C]/LPSY[C], LPS[D]/LPSY[D]) tren du lieu M1 THAT (dxFeed GCQ26),
roi ve len anh de kiem truc quan TRUOC khi dua vao WyckoffRunner.cs.

Nguon quy tac:
  - quantower-entry-signal/WYCKOFF_DRAW_SPEC.md (spec goc, tong hop THEORY.md + CHART_CASES.md)
  - data-export/wyckoff/THEORY.md, CHART_CASES.md, WYCKOFF_RULES.md
  - rule-entry/wyckoff-thuat-toan-ve-giai-thich.md (ban giai thich bang loi, dung de review)
  - .claude/agents/wyckoff-giao-vien.md (agent GIANG VIEN cham chart — nguon cua vong sua v5)

================================================================================================
v5 — VONG CHAM CHART (2026-08-03): 10 agent giang vien cham DU 49 range, diem trung vi 3/10.
================================================================================================
Cac nhom loi HE THONG lap lai tren phan lon bai (khong phai loi le tung nhan), va cach va:

  LOI A — CLIMAX KHONG PHAI CUC TRI THAT (bat o gan nhu moi bai; nang nhat: cuc tri that cach cay
    climax 2-8 nen, ca biet 93 nen). Dieu kien mo range chi kiem cay climax la cuc tri cua cua so
    NHIN LAI 240 nen, khong kiem gi ve sau -> BIEN CHINH bi dat vao GIUA vung gia, roi moi thu phia
    sau (bien phu, do sau shock, dieu kien pha) deu lech theo.
    Va: (1) cao trao la mot CUM vai nen — trong CLIMAX_EXT_BARS nen dau, cuc tri moi cung phia thi
    DOI MO climax sang do (doi ca nhan SC/BCLX lan moc bat dau range);
        (2) sau cua so cum, neu gia con vuot muc climax qua CLIMAX_FAIL_ATR lan bien do TB thi climax
    do KHONG chan duoc move -> bo ung vien (truoc day van co ve range).

  LOI B — NHAN SOS/SOW NEO SAI NEN (bat o 4/5 bai moi lo). Nhan duoc dong dau tai nen XAC NHAN THU 3
    (hoac tai nen het han cho BREAK_MAX_WAIT), nen luon roi vao nen volume tam thuong sau khi da het:
    do duoc VSA 0.30x / 0.37x / 0.47x / 0.69x trong khi cay pha that co VSA 4.2x-9.6x.
    Va: van doi du BREAK_HOLD_BARS nen moi CHOT cu pha, nhung nhan duoc dat HOI TO vao dung cay pha
    (nen co VSA cao nhat trong doan, DUNG HUONG, dong cua vuot bien) — xem _anchor_break_bar().

  LOI C — PHASE C = 121 NEN = ARTEFACT CUA TIMEOUT (bat o >10 bai). Het SHOCK_MAX_WAIT thi shock bi
    ghi "(that bai)" nhung doan da son C VAN NAM LAI trong timeline -> phase NGAN NHAT thanh phase DAI
    NHAT, tu phu dinh ca L8 va L9.
    Va (nguoi hoc chot 2026-08-03): cu shock het han "tao thanh UT, UA hoac la mSOS, mSOW (minor, tuc
    la bi fail), va phase nay VAN LA PHASE B" -> _demote_shock() doi nhan, _revert_to_B() XOA han doan
    C khoi timeline.

  LOI D — PHASE A BI SAN CUNG 41 NEN, ST[A] ROI GIUA RANGE. AR chi duoc chot tai dung nen
    climax_i + AR_LOOKBACK + 1 (co dinh 40 nen) nen moi cu test trong 40 nen dau bi bo mu; con ST[A]
    dung nguong "hoi >= 40% chieu cao climax<->AR" nen roi vao 1/3 giua range (do duoc 41%-179%).
    Va (nguoi hoc chot: "khong do bang %, do bang CAU TRUC"): ca AR va ST[A] deu la SWING PIVOT dau
    tien duoc xac nhan (PIVOT_CONFIRM_BARS nen khong tao cuc tri moi), voi mot SAN CHONG NHIEU tuyet
    doi (>= PIVOT_MIN_ATR lan bien do TB 20 nen) — KHONG con nguong % nao. Them TRAN cho ST[A]:
    vuot han qua muc climax hon STA_MAX_OVERSHOOT lan chieu cao range thi khong con la test -> bo.

  LOI E — NHAN AR KHONG DOI KHI MUC AR BI DOI (bat 6 bai, lech toi 110.8 gia). Nhanh doi AR trong
    state A_st cap nhat r.ar_price nhung khong cap nhat dict su kien -> nhan AR nam le hang chuc gia
    so voi chinh bien chinh do no tao ra. Va: giu r.ar_ev va cap nhat ca hai.

  LOI F — GIA TRI TRA VE CUA _try_lps_and_phase_e() BI BO O CALL SITE. Ham nay PHAT HIEN cu pha hong
    va tra False, nhung _fire_break() van dong range va van DAT TEN pattern -> co range mang nhan
    "Phan phoi" ma khong he co mot cu pha nao thanh cong.
    Va: cu pha bi vo hieu -> ha cap nhan thanh mSOS/mSOW, tra dai phase ve B, KHONG dat ten range,
    va cu pha sau phai vuot qua chinh cuc tri da that (r.fail_floor). Sau MAX_VOID_BREAKS lan vo hieu
    thi dong range o trang thai "chua ro huong" (chan vong lap D->B->D vo tan cua v4).

  LOI G — CU RU DO BANG BIEN CHINH THAY VI CUC TRI THAT CUA TR (loi giang vien sua nhieu nhat trong
    CHART_CASES: 4/22 ca nguon 2.pdf). Va + nguoi hoc chot 2026-08-03: mot cu tham do chi tro thanh
    Spring/Shakeout/UTAD khi no VUOT QUA BIEN PHU (cuc tri xa nhat da co), va MOI RANGE CHI CO DUNG
    MOT Spring/UTAD — cu sau sau hon thi ha cap cu truoc, cu nong hon thi tu ha cap.

  LOI H — UA/DA GAN BAT KE DO SAU/VOLUME. Mot cu thoc 5.5 gia VSA 2.44x co nen dong duoi bien bi ha
    thanh "DA test nhe", roi chinh no noi bien phu va lam hong dieu kien xac nhan SOW.
    Va: tham do MANH (sau >= max(MINOR_POKE_TICKS, SHOCK_DEPTH_FRAC x chieu cao) hoac VSA >= climax)
    nhung khong du tu cach shock -> nhan mSOS/mSOW; chi cu that NHE moi la UA/UT/DA.

  LOI I — MOVE TRUOC CLIMAX TINH CA CHINH CAY CLIMAX (bai #40: 80% "move 78.3 gia" nam trong dung cay
    climax; bai #32: ca move = cay tin). Va: do move tren doan [chan .. climax-1], loai han bien do cua
    cay climax; doan do phai TU MINH du dai va du hieu suat huong.

  LOI J — PHASE E LUON DAI 1 NEN. Moc chot E la nen cuoi cua so cho nen end_i trung luon voi no.
    Va: sau khi vao Phase E, keo tiep toi khi gia dong cua lui han vao trong bien da pha (hoac het
    PHASE_E_MAX_BARS) — Phase E co do dai that.

  LOI K — CUA SO CHO DEM BANG SO NEN tren du lieu chi co nen khi co giao dich -> 54 nen trai 4.8 ngay
    lich (bac qua khe cuoi tuan 73 gio). Nguoi hoc chot: "Cat range tai khe cuoi tuan, noi qua nghi
    phien 1h" -> gap > GAP_CUT_MIN phut thi dong/bo range dang chay.

Nguoi hoc chot them (tra loi truc tiep, ap dung o day):
  - KHONG dat san do dai toi thieu cho range (range ngan van hop le neu du cau truc).
  - Chi ve range o M1, CHUA can range long nhau.
  - KHONG dung san khoi luong tuyet doi (giu VSA tuong doi) — nen phien A thanh khoan thap van duoc
    xet; loc bang cau truc chu khong bang so lot.

Dung lai KHONG SUA: entry_dxfeed.py (load_m1, VSA_CLIMAX, TICK).
Chay: python3 wyckoff_schematic.py            -> in thong ke toan bo lich su
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
VSA_GATE = E.VSA_GATE

# ============================================================================
# Tham so
# ============================================================================
CLIMAX_RANGE_MULT = 1.4      # rong nen climax >= x lan TB range N nen truoc (loai climax gia)
CLIMAX_RANGE_LOOKBACK = 20
ST_TOL_TICKS = 10            # dung sai "cham lai bien" (khong tinh la tham do ra ngoai)
SOS_BODY_MIN = 0.45          # WY05: nen pha than >= 45% bien do
LPS_WAIT_BARS = 25           # so nen cho hoi sau SOS/SOW truoc khi xet Phase E
PHASE_E_MULT = 1.0           # gia phai di xa hon RangeHeight*mult khoi bien pha de tinh la Phase E
SHOCK_PROGRESS_MULT = 0.5    # tien do toi thieu de shock coi la dang tot (spec §1.15/§3.5)
PHASE_E_MIN_PROGRESS_MULT = 0.5   # CR-K: het cua so cho thi can >=50%*PHASE_E_MULT moi ep E

# --- guard chong range "vo han" (KHONG co trong tai lieu goc — tu dat) ---
MAX_RANGE_HEIGHT_PCT = 0.035   # bien CHINH cao hon ~3.5% gia -> bo range
MAX_BARS_PHASE_AB = 2500       # qua ngan nay ma chua chot duoc Phase D -> bo

# --- v3: MOVE xu huong truoc climax (dieu kien CAN de mo range) ---
MOVE_LOOKBACK = 240        # so nen toi da nhin lai de tim CHAN cua move
MOVE_MIN_BARS = 20         # move phai keo dai it nhat bao nhieu nen
MOVE_MIN_ATR = 8.0         # do dai move >= x lan bien do TB 20 nen
MOVE_MIN_EFF = 0.35        # hieu suat huong = |net| / tong quang duong close-to-close

AR_MAX_WAIT = 300          # cho toi ngan nay ma AR van chua thanh hinh -> bo ung vien
STA_MAX_WAIT = 400         # khong tim thay ST[A] trong ngan nay (tinh tu AR) -> bo ung vien

# --- v5: AR va ST[A] do bang CAU TRUC (swing pivot), khong bang % (LOI D) ---
PIVOT_CONFIRM_BARS = 5     # so nen khong tao cuc tri moi -> coi la swing DA doi huong
PIVOT_MIN_ATR = 1.5        # nhip hoi phai lon hon nhieu 1 nen (x lan bien do TB 20 nen)
STA_MAX_OVERSHOOT = 1.0    # ST[A] vuot qua muc climax hon x lan chieu cao range -> khong phai test

# --- v6 muc 1.8: AR/ST[A] them RANG BUOC TUONG DOI (nguyen ly CHoCH: "doan hoi khong du lon so
# voi boi canh" — giang vien bac CHoCH vi ly do nay, khong phai vi ngan hon mot so tuyet doi).
# DA DO tren du lieu that (103,857 nen M1 GCQ26): mult=1.0/frac=0.4 giet 12/52 range dung; ha xuong
# 0.5/0.2 chi mat 3/52 ma van siet duoc cac ca AR/ST[A] roi vao nhip hoi 4 nen tren VSA 0.25x. ---
AR_RETRACE_MULT = 0.5      # AR phai VUOT QUA x% nhip hoi lon nhat DA XAY RA trong long move truoc do
STA_MIN_AR_FRAC = 0.2      # ST[A] phai hoi toi thieu x% khoang AR<->climax (ngoai san PIVOT_MIN_ATR)
# muc 1.2(c): bien phu / bien chinh > nguong nay -> huy range. DA DO (sau khi fix 1.2b het tu noi):
# median 1.53x, p90 3.27x, max that 6.45x (chi 2-3 ca) -> 1.8 (chon truoc khi do) qua thap, cat oan
# ca median; 4.0 giu duoc gan het, chi cat cac ca ngoai le thuc su.
MAX_OUTER_RATIO = 4.0

# --- v5: cum climax (LOI A) ---
CLIMAX_EXT_BARS = 8        # cao trao = vung vai nen, cho phep doi mo climax trong ngan nay
# v6 muc 1.4: guard nay gio chay SUOT ca A_st (toi 400 nen) thay vi chi 8 nen dau -> DO LAI tren du
# lieu that (thay 3.0 giu nguyen thi mat 9-14 range dung, 4.0 giu duoc gan het ma van bat duoc cac
# ca climax thuc su khong chan duoc move).
CLIMAX_FAIL_ATR = 4.0      # sau cua so cum, gia vuot muc climax qua nay -> climax khong chan duoc move

# --- v4/v5: theo doi cu pha bien ---
SPRING_MAX_BARS = 4        # <= bao nhieu nen thi cu pha duoc coi la Spring (nhanh); lau hon = Shakeout
BREAK_HOLD_BARS = 3        # so nen LIEN TIEP dong cua han ngoai bien phu -> pha THAT
BREAK_MAX_WAIT = 40        # o ngoai bien lau hon nay -> xet bang ty le nen dong ngoai
BREAK_OUT_FRAC = 0.60      # ... >= 60% nen trong doan dong cua ngoai bien thi coi la pha that
MINOR_POKE_TICKS = 15      # san tuyet doi cua "tham do MANH" (1.5 gia)
SHOCK_DEPTH_FRAC = 0.15    # ... hoac >= 15% chieu cao bien chinh (LOI H: nguong tuyet doi qua nho)
RETRO_C_LOOKBACK = 60      # nhin lai bao nhieu nen de gan NGUOC Phase C (case kho)
SHOCK_MAX_WAIT = 120       # "Phase C la phase NGAN NHAT" — het han thi ha cap shock, ve Phase B
MAX_VOID_BREAKS = 3        # so lan cu pha bi vo hieu truoc khi dong range o trang thai "chua ro"
PHASE_E_MAX_BARS = 120     # LOI J: Phase E keo dai toi da bao nhieu nen (Phase E nam NGOAI range,
                           # keo qua dai thi no thanh phase dai nhat -> vi pham L9)
PHASE_E_TARGET_MULT = 2.0  # ... hoac dung khi gia da di xa x lan chieu cao range = tim duoc vung gia moi

# --- v5: khe thoi gian (LOI K, nguoi hoc chot) ---
GAP_CUT_MIN = 240          # khe > 4 gio (cuoi tuan/nghi le) -> cat range; nghi phien 1h thi noi


# Ung vien range da MO nhung bi BO giua chung. Chi de CHAN DOAN/review.
DISCARDED = []


def _avg_range(B, i, lookback):
    lo = max(0, i - lookback)
    win = B[lo:i]
    if not win:
        return B[i]['rng']
    return sum(b['rng'] for b in win) / len(win)


def _find_move(B, i, acc):
    """Truoc nen climax i co mot MOVE xu huong that khong?
    acc=True  -> can move GIAM (climax SC chan day) | acc=False -> can move TANG (BCLX chan dinh)

    LOI I (v5): do move tren doan [chan .. i-1], KHONG tinh bien do cua chinh cay climax — truoc day
    mot cay tin 60 gia tu no da thoa MOVE_MIN_ATR nen gia dang di ngang van mo duoc range.
    v6 muc 1.7: khong bac qua khe cuoi tuan/nghi le khi nhin lai tim chan move.
    v6 muc 1.8: do them max_pullback = nhip hoi lon nhat DA XAY RA trong long move, dung de AR/ST[A]
    so sanh TUONG DOI (nguyen ly CHoCH) thay vi mot san tuyet doi co dinh.
    Tra (ok, chan_i, do_dai, hieu_suat, max_pullback)."""
    if i < 2:
        return (False, None, 0.0, 0.0, 0.0)
    lo_i = max(0, i - MOVE_LOOKBACK)
    for k in range(i, lo_i, -1):
        gap_min = (B[k]['dt'] - B[k - 1]['dt']).total_seconds() / 60.0
        if gap_min > GAP_CUT_MIN:
            lo_i = k
            break
    if i - lo_i < MOVE_MIN_BARS:
        return (False, None, 0.0, 0.0, 0.0)
    # climax phai la CUC TRI cua ca cua so — no dang CHAN move, khong phai nam giua move
    if acc:
        if B[i]['lo'] > min(B[k]['lo'] for k in range(lo_i, i)):
            return (False, None, 0.0, 0.0, 0.0)
        pk = max(range(lo_i, i), key=lambda k: B[k]['hi'])   # chan move = dinh cao nhat
        length = B[pk]['hi'] - min(B[k]['lo'] for k in range(pk, i))   # loai cay climax
    else:
        if B[i]['hi'] < max(B[k]['hi'] for k in range(lo_i, i)):
            return (False, None, 0.0, 0.0, 0.0)
        pk = min(range(lo_i, i), key=lambda k: B[k]['lo'])   # chan move = day thap nhat
        length = max(B[k]['hi'] for k in range(pk, i)) - B[pk]['lo']
    worst = B[pk]['lo'] if acc else B[pk]['hi']
    max_pullback = 0.0
    for j in range(pk, i):
        if acc:
            if B[j]['lo'] < worst:
                worst = B[j]['lo']
            pullback = B[j]['hi'] - worst
        else:
            if B[j]['hi'] > worst:
                worst = B[j]['hi']
            pullback = worst - B[j]['lo']
        if pullback > max_pullback:
            max_pullback = pullback
    if i - pk < MOVE_MIN_BARS:
        return (False, pk, length, 0.0, max_pullback)
    avgr = _avg_range(B, i, CLIMAX_RANGE_LOOKBACK)
    if avgr <= 0 or length < MOVE_MIN_ATR * avgr:
        return (False, pk, length, 0.0, max_pullback)
    path = sum(abs(B[k]['c'] - B[k - 1]['c']) for k in range(pk + 1, i))
    eff = length / path if path > 1e-9 else 0.0
    return (eff >= MOVE_MIN_EFF, pk, length, eff, max_pullback)


class WyRange:
    __slots__ = ('start_i', 'end_i', 'origin', 'dir', 'low', 'high', 'solid_low', 'solid_high',
                 'events', 'phases', 'status', 'state', 'pending_shock', 'brk',
                 'climax_price', 'climax_ev', 'ar_i', 'ar_price', 'ar_ev', 'ar_ext', 'ar_ext_i',
                 'sta_i', 'sta_price', 'move_i', 'move_len', 'move_eff', 'move_max_pullback',
                 'st_ext', 'st_ext_i', 'shock_ev', 'shock_depth', 'fail_floor', 'void_breaks',
                 'climax_vsa', 'ar_vsa', 'sta_vsa')

    def __init__(self, start_i, origin):
        self.start_i = start_i
        self.end_i = None
        self.origin = origin      # 'DOWN' = move giam bi SC chan | 'UP' = move tang bi BCLX chan
        self.dir = 0              # 0 chua biet | +1 pha LEN | -1 pha XUONG (chot khi SOS/SOW GIU duoc)
        # --- bien PHU (net dut): cuc tri xa nhat da tung cham ---
        self.low = None
        self.high = None
        # --- bien CHINH (net lien): CO DINH sau Phase A, tao tu climax + AR ---
        self.solid_low = None
        self.solid_high = None
        self.climax_price = None
        self.climax_ev = None
        self.ar_i = None
        self.ar_price = None
        self.ar_ev = None         # LOI E: giu tham chieu de doi CA NHAN khi doi muc AR
        self.ar_ext = None        # cuc tri tam trong luc cho AR thanh hinh
        self.ar_ext_i = None
        self.sta_i = None
        self.sta_price = None
        self.move_i = None
        self.move_len = 0.0
        self.move_eff = 0.0
        self.move_max_pullback = 0.0   # v6 muc 1.8: nhip hoi lon nhat da xay ra trong long move
        self.st_ext = None
        self.st_ext_i = None
        self.shock_ev = None      # LOI G: MOI RANGE CHI MOT Spring/Shakeout/UTAD
        self.shock_depth = 0.0
        self.fail_floor = None    # LOI F: cu pha sau phai vuot qua cuc tri da that nay
        self.void_breaks = 0
        self.climax_vsa = 0.0     # v6 muc 1.1/1.9: VSA cua cay MANG NHAN (khong phai cuc tri gia)
        self.ar_vsa = 0.0         # v6 muc 1.9: VSA cua cay AR (chi DO, chua gate)
        self.sta_vsa = 0.0        # v6 muc 1.9: VSA cua cay ST[A] (chi DO, chua gate)
        self.events = []
        self.phases = []
        self.status = 'active'
        self.state = 'A'          # A | A_st | B | B_brk | C_pending | END
        self.pending_shock = None
        self.brk = None

    @property
    def kind(self):
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

    @property
    def height(self):
        if self.solid_low is not None:
            return self.solid_high - self.solid_low
        if self.low is not None and self.high is not None:
            return self.high - self.low
        return 0.0

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


# ============================================================================
# Helper
# ============================================================================
def _mark_outer(r, i, label, price, up_side):
    """Moi ben chi giu MOT nhan test/that-bai o cuc tri xa nhat ("bien phu cu bien mat, bien phu moi
    tiep tuc noi ra"). Cham nong hon cuc tri cu thi khong ghi gi ca."""
    fam = ('UT[B]', 'ST[B]', 'mSOS', 'mSOW')
    old = [e for e in r.events if e['label'] in fam
           and ((e['price'] > r.solid_high) if up_side else (e['price'] < r.solid_low))]
    for e in old:
        if (price <= e['price']) if up_side else (price >= e['price']):
            return
        r.events.remove(e)
    r.add_event(i, label, price, r.phases[-1][0] if r.phases else 'B')


def _minor_label(r, up_side, strong):
    """Nhan cho mot cu tham do KHONG du tu cach shock (v6 muc 3.1, nguoi hoc chot 2026-08-04):
    moi ben chi con DUNG HAI nhan — 'UT[B]' (test/tho nhe BIEN TREN roi doi) va 'ST[B]' (test/tho nhe
    BIEN DUOI roi doi). Bo han UA/DA (gan nham vi khong con phan biet theo canh AR/canh climax).
    strong=True (da PHA HAN ra ngoai nhung hoi ve THU HAN vao trong range) -> mSOS/mSOW (v6 muc 3.2)."""
    if strong:
        return 'mSOS' if up_side else 'mSOW'
    return 'UT[B]' if up_side else 'ST[B]'


def _demote_shock(r):
    """LOI C + nguoi hoc chot: shock het han/that bai thi "tao thanh UT, UA hoac la mSOS, mSOW
    (minor, tuc la bi fail)". Khong con nhan "(that bai)" treo lai.
    Mot pending shock luon da VUOT QUA bien phu (dieu kien exceeded_outer khi tao — xem is_shock),
    nen theo dinh nghia moi (v6 muc 3.2) no LUON la mSOS/mSOW, khong con la UT[B]/ST[B] nhe.
    v6 muc 1.2(b): CHI BAY GIO (da biet ket cuc THAT BAI) moi noi bien phu bang cuc tri thuc te cua
    cu tham do — khong noi lien tuc trong luc con dang cho (fix "tu noi bien roi tu vuot chinh no")."""
    sh = r.pending_shock
    if sh is None:
        return
    ev = sh['event']
    up_poke = sh['dir'] < 0     # dir<0 = UTAD (tham do canh TREN) | dir>0 = Spring (canh DUOI)
    if up_poke:
        r.high = max(r.high, sh['peak'])
    else:
        r.low = min(r.low, sh['peak'])
    ev['label'] = _minor_label(r, up_poke, strong=True)
    ev['status'] = None
    ev['phase'] = 'B'
    if r.shock_ev is ev:
        r.shock_ev = None
        r.shock_depth = 0.0
    r.pending_shock = None


def _revert_to_B(r, i):
    """XOA moi doan C/D o duoi cung khoi timeline va mo lai Phase B dang chay (LOI C).
    Truoc day chi goi set_phase(i,'B') nen mot doan "Phase C" dai bang ca tran timeout con nam lai.
    v6 muc 1.6: XOA LUON cac nhan LPS[C]/LPSY[C]/LPS[D]/LPSY[D]/SOS/SOW da phat sinh trong doan
    C/D/E vua bi xoa — truoc day chi xoa DOAN PHASE, nhan van treo mo coi lai giua Phase B.
    Nhan shock (Spring/Shakeout/UTAD/mSOS/mSOW) KHONG dung toi: _demote_shock() da tu lo rieng."""
    orphan_fam = ('LPS[C]', 'LPSY[C]', 'LPS[D]', 'LPSY[D]', 'SOS', 'SOW')
    while r.phases and r.phases[-1][0] in ('C', 'D', 'E'):
        r.phases.pop()
    r.events = [e for e in r.events if not (e['phase'] in ('C', 'D', 'E') and e['label'] in orphan_fam)]
    if r.phases:
        r.phases[-1][2] = None
    else:
        r.phases.append(['B', i, None])
    r.state = 'B'


def _anchor_break_bar(B, lo_i, hi_i, up, level):
    """LOI B: nhan SOS/SOW phai nam o CAY PHA that — nen co VSA cao nhat trong doan, DUNG HUONG,
    va dong cua vuot bien. Khong tim duoc thi lay nen dau doan (khong lay nen cuoi: chinh viec lay
    nen cuoi la nguyen nhan nhan roi vao nen volume tam thuong)."""
    best = None
    for j in range(max(0, lo_i), hi_i + 1):
        b = B[j]
        if up:
            if not (b['c'] > level and b['c'] > b['o']):
                continue
        else:
            if not (b['c'] < level and b['c'] < b['o']):
                continue
        if best is None or b['vratio'] > B[best]['vratio']:
            best = j
    return best if best is not None else max(0, lo_i)


def _add_unique(r, i, label, price, phase):
    """Moi range chi giu MOT nhan moi ho LPS[C]/LPSY[C] va MOT nhan LPS[D]/LPSY[D] (nguoi hoc chot
    2026-08-03: "LPSY, LPS cua phase [C] va [D] cung chi can 1 diem thoi"). Nhan moi thay nhan cu."""
    fam = ('LPS[C]', 'LPSY[C]') if label in ('LPS[C]', 'LPSY[C]') else \
          ('LPS[D]', 'LPSY[D]') if label in ('LPS[D]', 'LPSY[D]') else (label,)
    for e in [e for e in r.events if e['label'] in fam]:
        r.events.remove(e)
    return r.add_event(i, label, price, phase)


def _last_pivot(B, lo_i, hi_i, up):
    """Swing pivot GAN NHAT truoc cu pha (cuc tri cuc bo, PIVOT_CONFIRM_BARS nen moi ben khong vuot).
    Dung cho Phase C gan nguoc: lay CUC TRI cua ca cua so 60 nen thi Phase C an gan het range (do duoc
    C=48-60n trong khi D=1n), trai voi L8 "Phase C la phase NGAN NHAT"."""
    n = PIVOT_CONFIRM_BARS
    for j in range(hi_i - n, lo_i - 1, -1):
        if j - n < lo_i:
            break
        w = range(j - n, min(hi_i, j + n) + 1)
        if up:
            if all(B[j]['lo'] <= B[k]['lo'] for k in w):
                return j
        else:
            if all(B[j]['hi'] >= B[k]['hi'] for k in w):
                return j
    return None


def _retro_phase_c(B, r, sos_i, up):
    """muc 6, case KHO: khong co Spring/Shakeout/UTAD nao de nhan ra Phase C ngay luc do -> cho SOS/SOW
    ban ra roi NHIN NGUOC lai, nhip test cuoi cung truoc cu pha chinh la LPS[C]/LPSY[C], Phase C bat
    dau tu do ("co Phase D roi moi xac dinh duoc Phase C"). Chi 1 diem duy nhat.
    Cua so nhin lai bi chan boi CA HAI: RETRO_C_LOOKBACK va MOT NUA do dai Phase B (de Phase B van la
    phase dai nhat va Phase C van la phase ngan nhat).
    v6 muc 1.5: pivot phai (a) nam TRONG range (+-dung sai) va (b) nam DUNG NUA range — LPS[C] (pha
    len) o NUA DUOI, LPSY[C] (pha xuong) o NUA TREN. Khong tim duoc pivot hop le -> KHONG ve Phase C
    (Phase B chay thang sang Phase D), thay vi ep mot diem sai vi tri."""
    b_start = r.phases[-1][1] if r.phases else r.start_i
    win = min(RETRO_C_LOOKBACK, max(1, (sos_i - b_start) // 2))
    lo_i = max(b_start + 1, sos_i - win)
    if sos_i - lo_i < 3:
        return
    tol = ST_TOL_TICKS * TICK
    mid = (r.solid_low + r.solid_high) / 2.0
    def _in_range(k):
        px = B[k]['lo'] if up else B[k]['hi']
        return r.solid_low - tol <= px <= r.solid_high + tol
    def _right_half(k):
        return B[k]['lo'] <= mid if up else B[k]['hi'] >= mid
    cands = [k for k in range(lo_i, sos_i) if _in_range(k) and _right_half(k)]
    if not cands:
        return
    piv = _last_pivot(B, lo_i, sos_i, up)
    if piv is None or piv not in cands:
        piv = min(cands, key=lambda k: B[k]['lo']) if up else max(cands, key=lambda k: B[k]['hi'])
    price = B[piv]['lo'] if up else B[piv]['hi']
    r.set_phase(piv, 'C')
    _add_unique(r, piv, 'LPS[C]' if up else 'LPSY[C]', price, 'C')


def _emit_lps(B, r, pull_bars, ACC):
    """LPS[D]/LPSY[D] CHI danh dau 1 DIEM (nguoi hoc chot): day sau nhat (pha len) / dinh cao nhat
    (pha xuong) cua nhip hoi."""
    if not pull_bars:
        return
    label = 'LPS[D]' if ACC else 'LPSY[D]'
    k = min(pull_bars, key=lambda x: B[x]['lo']) if ACC else max(pull_bars, key=lambda x: B[x]['hi'])
    _add_unique(r, k, label, B[k]['lo'] if ACC else B[k]['hi'], 'D')


def _try_lps_and_phase_e(B, r, sos_i, up, level, solid_edge):
    """muc 7: Phase D + E chinh la CBR — PHA bien, HOI ve retest nhung GIU duoc ben ngoai bien
    (nhip hoi do = LPS[D]/LPSY[D]), roi gia THUAN LUC di tiep tim vung gia moi (Phase E).
    `level` = bien vua bi pha (bien PHU, dung de tinh tien do/muc tieu Phase E).
    `solid_edge` = bien CHINH — v6 muc 3.2: vung giua bien chinh va bien phu la CHUA KET LUAN, gia
    lui qua bien phu (level) van con co the la retest binh thuong; CHI khi lui qua HAN bien chinh
    moi tinh la cu pha bi VO HIEU (truoc day dung `level` nen SOS/SOW that de bi vo hieu oan).
    Tra (ok, end_i): ok=False nghia la cu pha BI VO HIEU (call site phai ha cap nhan — LOI F)."""
    ACC = up
    N = len(B)
    end = min(N - 1, sos_i + LPS_WAIT_BARS)
    fail_tol = 3.0 * ST_TOL_TICKS * TICK
    peak = B[sos_i]['hi'] if ACC else B[sos_i]['lo']
    range_height = max(1e-9, r.height)
    avgr = _avg_range(B, sos_i, CLIMAX_RANGE_LOOKBACK)
    # v5: LPS[D]/LPSY[D] = nhip HOI dau tien do bang CAU TRUC (swing pivot nguoc huong pha), khong
    # phai "nen nao dong cua trong 2 gia quanh bien". Truoc day dieu kien qua chat nen 17/47 range
    # khong co nhip retest nao -> Phase D dai dung 1 nen (D ngan hon C, tu phu dinh L8).
    ret_ext = ret_i = None      # cuc tri cua nhip hoi dang hinh thanh
    lps_i = None                # nhip hoi da duoc XAC NHAN (giu PIVOT_CONFIRM_BARS nen)
    target_j = None             # nen dau tien gia da di du xa (>= PHASE_E_MULT x chieu cao)
    for j in range(sos_i + 1, end + 1):
        bj = B[j]
        if ACC:
            if bj['hi'] > peak:
                peak, ret_ext, ret_i = bj['hi'], None, None
            if ret_ext is None or bj['lo'] < ret_ext:
                ret_ext, ret_i = bj['lo'], j
            failed = bj['c'] < solid_edge - fail_tol
            pull = peak - ret_ext
        else:
            if bj['lo'] < peak:
                peak, ret_ext, ret_i = bj['lo'], None, None
            if ret_ext is None or bj['hi'] > ret_ext:
                ret_ext, ret_i = bj['hi'], j
            failed = bj['c'] > solid_edge + fail_tol
            pull = ret_ext - peak
        moved_far = (peak - level) if ACC else (level - peak)
        if failed and moved_far < PHASE_E_MIN_PROGRESS_MULT * PHASE_E_MULT * range_height:
            return (False, j)      # dong nen lui han vao trong range truoc khi di duoc dau -> vo hieu
        if (lps_i is None and ret_i is not None and pull >= PIVOT_MIN_ATR * avgr
                and (j - ret_i) >= PIVOT_CONFIRM_BARS):
            lps_i = ret_i
        if target_j is None and moved_far >= PHASE_E_MULT * range_height:
            target_j = j
        if target_j is not None and (lps_i is not None or j >= end):
            break
    if lps_i is not None:
        _emit_lps(B, r, [lps_i], ACC)
    if target_j is None:
        final_moved = (peak - level) if ACC else (level - peak)
        if final_moved < PHASE_E_MIN_PROGRESS_MULT * PHASE_E_MULT * range_height:
            return (False, end)
        target_j = end
    # Phase D phai BAO TRON nhip retest (muc 7: pha -> hoi ve retest GIU duoc ngoai bien -> roi moi
    # thuan luc di tiep). Khong co nhip retest thi Phase D ngan that (CHART_CASES Ca #21: "khong phai
    # TR nao cung co BU o Phase D").
    e_start = target_j if lps_i is None else max(target_j, lps_i + PIVOT_CONFIRM_BARS)
    e_start = min(N - 1, e_start)
    r.set_phase(e_start, 'E')
    # LOI J: Phase E co do dai THAT — keo toi khi mot trong ba dieu xay ra: gia dong cua lui han vao
    # trong bien da pha, hoac da tim duoc vung gia moi (di xa PHASE_E_TARGET_MULT lan chieu cao range),
    # hoac het PHASE_E_MAX_BARS. (Khong keo vo han: Phase E dai hon Phase B thi vi pham L9.)
    e_end = e_start
    for j in range(e_start + 1, min(N - 1, e_start + PHASE_E_MAX_BARS) + 1):
        bj = B[j]
        if (bj['c'] < level) if ACC else (bj['c'] > level):
            break
        peak = max(peak, bj['hi']) if ACC else min(peak, bj['lo'])
        e_end = j
        if ((peak - level) if ACC else (level - peak)) >= PHASE_E_TARGET_MULT * range_height:
            break
    return (True, e_end)


def _fire_break(B, r, i, up, out_edge, poke_start_i):
    """Mot cu pha bien da du dieu kien chot. Nhan dat HOI TO vao cay pha that (LOI B).
    Neu Phase D/E khong giu duoc thi cu pha BI VO HIEU: ha cap nhan, tra dai phase ve B, KHONG dat
    ten range (LOI F).
    v6 muc 1.3: `poke_start_i` = nen DAU TIEN tho ra khoi bien (khong phai nen xac nhan thu 3), va
    moc so sanh cua anchor la BIEN CHINH (solid) — cay pha that thuong nam TRUOC ca luc dong cua
    vuot duoc bien phu."""
    solid_edge = r.solid_high if up else r.solid_low
    anchor = _anchor_break_bar(B, poke_start_i, i, up, solid_edge)
    r.brk = None
    r.pending_shock = None
    if not any(p[0] == 'C' for p in r.phases):
        _retro_phase_c(B, r, anchor, up)
    ev = r.add_event(anchor, 'SOS' if up else 'SOW', B[anchor]['c'], 'D')
    r.set_phase(anchor, 'D')
    ok, e_end = _try_lps_and_phase_e(B, r, anchor, up, out_edge, solid_edge)
    if ok:
        r.dir = 1 if up else -1
        r.end_i = e_end
        r.state = 'END'
        return True
    # --- cu pha bi vo hieu: da lui han qua BIEN CHINH (vung giua chinh-phu la CHUA KET LUAN) ---
    # v6 muc 3.2: mSOS/mSOW chi CHOT khi gia da di duoc >=50% chieu cao range VE HUONG BIEN DOI DIEN;
    # chua di duoc thi de trang thai 'provisional' — Phase B se tiep tuc theo doi qua _mark_outer.
    range_height = max(1e-9, r.height)
    progress_opp = ((r.solid_high - B[e_end]['c']) / range_height) if up \
        else ((B[e_end]['c'] - r.solid_low) / range_height)
    ev['label'] = 'mSOS' if up else 'mSOW'
    ev['phase'] = 'B'
    ev['status'] = None if progress_opp >= 0.5 else 'provisional'
    r.void_breaks += 1
    ext = max(B[j]['hi'] for j in range(poke_start_i, i + 1)) if up \
        else min(B[j]['lo'] for j in range(poke_start_i, i + 1))
    r.fail_floor = ext
    if up:
        r.high = max(r.high, ext)
    else:
        r.low = min(r.low, ext)
    if r.void_breaks >= MAX_VOID_BREAKS:
        # khong xoay vong vo tan: dong range o trang thai chua ro huong pha
        r.state = 'END'
        r.end_i = min(len(B) - 1, i)
        return False
    _revert_to_B(r, i)
    return False


# ============================================================================
# detect
# ============================================================================
def detect(B):
    """Tra list[WyRange] da phat hien (ca active lan completed) tren toan bo B."""
    ranges = []
    active = None
    DISCARDED.clear()

    for i in range(CLIMAX_RANGE_LOOKBACK + 5, len(B)):
        b = B[i]

        # ------------------------------------------------ LOI K: khe thoi gian lon -> cat range
        gap_min = (b['dt'] - B[i - 1]['dt']).total_seconds() / 60.0
        if gap_min > GAP_CUT_MIN and active is not None:
            r = active
            if r.solid_low is not None:
                if r.phases:
                    r.phases[-1][2] = i - 1
                r.end_i = i - 1
                r.status = 'completed'
                ranges.append(r)
            else:
                DISCARDED.append((r, 'bi cat boi khe thoi gian (>4 gio)', i))
            active = None

        # ---------------------------------------------- khong co range active: tim climax
        if active is None:
            avgr = _avg_range(B, i, CLIMAX_RANGE_LOOKBACK)
            if avgr <= 0:
                continue
            if not (b['rng'] >= CLIMAX_RANGE_MULT * avgr and b['vratio'] >= VSA_CLIMAX):
                continue
            if b['dn']:
                ok, pk, ln, eff, max_pb = _find_move(B, i, acc=True)
                if not ok:
                    continue
                r = WyRange(i, 'DOWN')
                r.low = r.climax_price = b['lo']
                r.move_i, r.move_len, r.move_eff, r.move_max_pullback = pk, ln, eff, max_pb
                r.climax_ev = r.add_event(i, 'SC', b['lo'], 'A')
                r.climax_vsa = b['vratio']
                r.set_phase(i, 'A')
                active = r
            elif b['up']:
                ok, pk, ln, eff, max_pb = _find_move(B, i, acc=False)
                if not ok:
                    continue
                r = WyRange(i, 'UP')
                r.high = r.climax_price = b['hi']
                r.move_i, r.move_len, r.move_eff, r.move_max_pullback = pk, ln, eff, max_pb
                r.climax_ev = r.add_event(i, 'BCLX', b['hi'], 'A')
                r.climax_vsa = b['vratio']
                r.set_phase(i, 'A')
                active = r
            continue

        r = active
        climax_i = r.start_i
        tol = ST_TOL_TICKS * TICK
        fail_tol = 3.0 * ST_TOL_TICKS * TICK
        avgr = _avg_range(B, i, CLIMAX_RANGE_LOOKBACK)

        # ------------------------------------------------------------ guard: bo range thoai hoa
        too_tall = r.height > MAX_RANGE_HEIGHT_PCT * b['c']
        too_long = r.state != 'END' and (i - climax_i) > MAX_BARS_PHASE_AB
        # v6 muc 1.2(c): bien phu phinh qua bien chinh (do duoc 2x-6.4x o v5) -> huy, dung de tu noi
        # vo han (bien phu chi duoc phep noi bang DUNG cu tham do that bai, khong hon).
        too_wide = (r.solid_low is not None and r.height > 0
                    and (r.high - r.low) > MAX_OUTER_RATIO * r.height)
        if too_tall or too_long or too_wide:
            reason = ('qua cao (>3.5% gia)' if too_tall else
                       'qua dai (>2500 nen)' if too_long else
                       f'bien phu phinh qua bien chinh (>{MAX_OUTER_RATIO}x)')
            DISCARDED.append((r, reason, i))
            active = None
            continue

        # ============================================================ state A: cum climax + cho AR
        if r.state == 'A':
            # (1) LOI A: cao trao la mot CUM vai nen — GIU DUNG co che mo rong cua so cum cua v5 (moi
            # cuc tri gia moi cung phia thi doi mo r.start_i, cho phep cum keo dai qua nhieu dot song
            # gia van con dang tao dinh/day moi), CHI SUA cach chon NHAN hien thi.
            # v6 muc 1.1 (nguoi hoc chot "doi MUC bien, giu NHAN o cay volume cao nhat"): MUC BIEN
            # (climax_price, dung de dung bien chinh/phu) doi theo cuc tri gia nhu cu; rieng VI TRI
            # NHAN (climax_ev) chi doi khi gap cay co VSA CAO HON nhan hien tai — tranh nhan roi vao
            # cay VSA 0.2x-1.5x trong khi cay 4x-14x nam ngay canh (day la loi nang nhat vong cham v5).
            if (i - climax_i) <= CLIMAX_EXT_BARS:
                moved = False
                if r.origin == 'DOWN' and b['lo'] < r.climax_price:
                    r.climax_price = r.low = b['lo']
                    moved = True
                elif r.origin == 'UP' and b['hi'] > r.climax_price:
                    r.climax_price = r.high = b['hi']
                    moved = True
                if b['vratio'] > r.climax_vsa:
                    r.climax_ev['i'], r.climax_ev['price'] = i, (b['lo'] if r.origin == 'DOWN' else b['hi'])
                    r.climax_vsa = b['vratio']
                if moved:
                    r.start_i = i
                    r.phases[0][1] = i
                    r.ar_ext = r.ar_ext_i = None
                    continue
            else:
                # (2) LOI A: climax phai CHAN duoc move
                beyond = (r.climax_price - b['lo']) if r.origin == 'DOWN' else (b['hi'] - r.climax_price)
                if beyond > CLIMAX_FAIL_ATR * avgr:
                    DISCARDED.append((r, 'climax khong chan duoc move', i))
                    active = None
                    continue
                if r.origin == 'DOWN':
                    r.low = min(r.low, b['lo'])
                else:
                    r.high = max(r.high, b['hi'])

            # (3) LOI D: AR = SWING NGUOC dau tien duoc xac nhan (khong con cua so co dinh 40 nen)
            if r.origin == 'DOWN':
                if r.ar_ext is None or b['hi'] > r.ar_ext:
                    r.ar_ext, r.ar_ext_i = b['hi'], i
                span = r.ar_ext - r.climax_price
            else:
                if r.ar_ext is None or b['lo'] < r.ar_ext:
                    r.ar_ext, r.ar_ext_i = b['lo'], i
                span = r.climax_price - r.ar_ext
            # v6 muc 1.8 (nguyen ly CHoCH — giang vien bac CHoCH vi "doan hoi khong du lon so voi boi
            # canh"): AR phai VUOT QUA chinh nhip hoi lon nhat DA XAY RA trong long move, khong chi
            # mot san tuyet doi co dinh (PIVOT_MIN_ATR truoc day rieng minh de AR roi vao nhip hoi 4
            # nen tren cay VSA 0.25x).
            ar_min = max(PIVOT_MIN_ATR * avgr, AR_RETRACE_MULT * r.move_max_pullback)
            if span >= ar_min and (i - r.ar_ext_i) >= PIVOT_CONFIRM_BARS:
                r.ar_i, r.ar_price = r.ar_ext_i, r.ar_ext
                lab = 'AR (yếu)' if (r.ar_i - climax_i) <= 2 else 'AR'
                r.ar_ev = r.add_event(r.ar_i, lab, r.ar_price, 'A')
                r.ar_vsa = B[r.ar_i]['vratio']
                if r.origin == 'DOWN':
                    r.high = r.ar_price if r.high is None else max(r.high, r.ar_price)
                else:
                    r.low = r.ar_price if r.low is None else min(r.low, r.ar_price)
                r.state = 'A_st'
                r.st_ext = r.st_ext_i = None
            elif (i - climax_i) > AR_MAX_WAIT:
                DISCARDED.append((r, 'Phase A: khong thanh hinh AR (khong co swing nguoc)', i))
                active = None
            continue

        # ================================================ state A_st: cho ST[A] = doi huong lan 3
        if r.state == 'A_st':
            span = abs(r.ar_price - r.climax_price)
            if span < 1e-9:
                DISCARDED.append((r, 'Phase A: climax va AR trung nhau', i))
                active = None
                continue
            # v6 muc 1.4: guard "climax khong chan duoc move" (LOI A phan 2) phai chay SUOT ca A_st,
            # khong chi trong state 'A' — truoc day tat han sau CLIMAX_EXT_BARS nen dau tien.
            beyond = (r.climax_price - b['lo']) if r.origin == 'DOWN' else (b['hi'] - r.climax_price)
            if beyond > CLIMAX_FAIL_ATR * avgr:
                DISCARDED.append((r, 'climax khong chan duoc move (phat hien o A_st)', i))
                active = None
                continue
            if r.origin == 'DOWN':
                if b['hi'] > r.ar_price:      # AR bi day cao hon -> doi CA MUC LAN NHAN (LOI E)
                    r.ar_price, r.ar_i = b['hi'], i
                    r.ar_ev['i'], r.ar_ev['price'] = i, b['hi']
                    r.ar_vsa = b['vratio']
                    r.high = max(r.high, b['hi'])
                    r.st_ext = r.st_ext_i = None
                if r.st_ext is None or b['lo'] < r.st_ext:
                    r.st_ext, r.st_ext_i = b['lo'], i
                swing = r.ar_price - r.st_ext
                overshoot = (r.climax_price - r.st_ext) / max(1e-9, span)
            else:
                if b['lo'] < r.ar_price:
                    r.ar_price, r.ar_i = b['lo'], i
                    r.ar_ev['i'], r.ar_ev['price'] = i, b['lo']
                    r.ar_vsa = b['vratio']
                    r.low = min(r.low, b['lo'])
                    r.st_ext = r.st_ext_i = None
                if r.st_ext is None or b['hi'] > r.st_ext:
                    r.st_ext, r.st_ext_i = b['hi'], i
                swing = r.st_ext - r.ar_price
                overshoot = (r.st_ext - r.climax_price) / max(1e-9, span)

            # LOI D (phan TRAN): vuot han qua muc climax thi khong con la mot cu TEST
            if overshoot > STA_MAX_OVERSHOOT:
                DISCARDED.append((r, 'ST[A] vuot han qua climax (khong phai test)', i))
                active = None
                continue
            # v6 muc 1.8: ST[A] cung phai hoi toi thieu mot TY LE cua khoang AR<->climax (khong chi
            # san tuyet doi PIVOT_MIN_ATR) — ho tro cung nguyen ly CHoCH nhu AR.
            sta_min = max(PIVOT_MIN_ATR * avgr, STA_MIN_AR_FRAC * span)
            if swing >= sta_min and (i - r.st_ext_i) >= PIVOT_CONFIRM_BARS:
                r.sta_i, r.sta_price = r.st_ext_i, r.st_ext
                r.sta_vsa = B[r.sta_i]['vratio']
                r.add_event(r.sta_i, 'ST[A]', r.sta_price, 'A')
                # DONG BANG 2 bien CHINH tai day = muc climax + muc AR
                r.solid_low = min(r.climax_price, r.ar_price)
                r.solid_high = max(r.climax_price, r.ar_price)
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

        # ==================================================== state B: cho mot cu tham do ra ngoai
        if r.state == 'B':
            pen_lo = (r.solid_low - b['lo']) / TICK
            pen_hi = (b['hi'] - r.solid_high) / TICK
            side = 0
            if max(pen_lo, pen_hi) > ST_TOL_TICKS:
                side = -1 if pen_lo >= pen_hi else 1
            # bien PHU chi noi rong bang cu tham do THAT BAI -> khong noi o day, doi ket cuc B_brk
            if side != -1 and b['lo'] < r.low:
                r.low = b['lo']
            if side != 1 and b['hi'] > r.high:
                r.high = b['hi']
            if side != 0:
                r.brk = dict(side=side, start_i=i, hold=0, first_i=None, vmax=b['vratio'],
                             ext=b['lo'] if side < 0 else b['hi'], ext_i=i,
                             out0=r.low if side < 0 else r.high, n_out=0, n_bars=0)
                r.state = 'B_brk'

        # ========================================= state B_brk: theo doi cu pha den khi ro ket cuc
        if r.state == 'B_brk':
            k = r.brk
            up_side = k['side'] > 0
            edge = r.solid_high if up_side else r.solid_low
            out_edge = max(k['out0'], edge) if up_side else min(k['out0'], edge)
            k['vmax'] = max(k['vmax'], b['vratio'])
            k['n_bars'] += 1
            if up_side:
                if b['hi'] > k['ext']:
                    k['ext'], k['ext_i'] = b['hi'], i
                back_in = b['c'] < edge - 1e-9
                outside = b['c'] > out_edge + tol
                decisive = b['c'] > out_edge + fail_tol and b['brat'] >= SOS_BODY_MIN
            else:
                if b['lo'] < k['ext']:
                    k['ext'], k['ext_i'] = b['lo'], i
                back_in = b['c'] > edge + 1e-9
                outside = b['c'] < out_edge - tol
                decisive = b['c'] < out_edge - fail_tol and b['brat'] >= SOS_BODY_MIN
            if outside:
                k['n_out'] += 1
            bars_out = i - k['start_i']

            if back_in:
                # cu pha THAT BAI -> gio moi noi BIEN PHU bang cuc tri cua cu tham do nay
                if up_side:
                    r.high = max(r.high, k['ext'])
                else:
                    r.low = min(r.low, k['ext'])
                depth = abs(k['ext'] - edge)
                # LOI G: chi VUOT QUA BIEN PHU cu moi co the la shock
                exceeded_outer = (k['ext'] > k['out0'] + tol) if up_side else (k['ext'] < k['out0'] - tol)
                # LOI H: nguong "tham do MANH" theo CA san tuyet doi va % chieu cao range
                strong = (depth >= max(MINOR_POKE_TICKS * TICK, SHOCK_DEPTH_FRAC * r.height)
                          or k['vmax'] >= VSA_CLIMAX)
                climax_side = up_side == (r.origin == 'UP')
                r.brk = None
                r.state = 'B'
                is_shock = (exceeded_outer and strong and climax_side
                            and (r.shock_ev is None or depth > r.shock_depth))
                if is_shock:
                    if r.shock_ev is not None:
                        # LOI G: moi range CHI MOT Spring/UTAD — cu cu bi ha cap
                        old = r.shock_ev
                        old['label'], old['status'], old['phase'] = \
                            _minor_label(r, up_side, strong=True), None, 'B'
                    if up_side:
                        label, tgt, sdir = 'UTAD', r.solid_low, -1
                    else:
                        label = 'Spring' if bars_out <= SPRING_MAX_BARS else 'Shakeout'
                        tgt, sdir = r.solid_high, 1
                    ev = r.add_event(k['ext_i'], label, k['ext'], 'C', status='pending')
                    r.shock_ev, r.shock_depth = ev, depth
                    r.pending_shock = dict(price=k['ext'], target_edge=tgt, peak=k['ext'],
                                           peak_i=k['ext_i'], event=ev, dir=sdir,
                                           out_edge=(r.low if sdir < 0 else r.high),
                                           lps_done=False, start_i=k['ext_i'])
                    r.set_phase(k['ext_i'], 'C')
                    r.state = 'C_pending'
                else:
                    lab = _minor_label(r, up_side, strong)
                    if lab is not None:
                        _mark_outer(r, k['ext_i'], lab, k['ext'], up_side)
                continue

            if decisive:
                if k['hold'] == 0:
                    k['first_i'] = i
                k['hold'] += 1
            else:
                k['hold'] = 0
            timed_out = bars_out > BREAK_MAX_WAIT and k['n_out'] >= BREAK_OUT_FRAC * max(1, k['n_bars'])
            # LOI F: cu pha sau phai vuot qua cuc tri da tung that
            floor_ok = True
            if r.fail_floor is not None:
                floor_ok = (k['ext'] > r.fail_floor) if up_side else (k['ext'] < r.fail_floor)
            if (k['hold'] >= BREAK_HOLD_BARS or timed_out) and floor_ok:
                # v6 muc 1.3: quet ANCHOR tu nen DAU TIEN tho ra (k['start_i']), khong phai tu nen
                # xac nhan thu 3 — cay pha THAT (VSA cao nhat) thuong nam som hon trong doan.
                _fire_break(B, r, i, up_side, out_edge, k['start_i'])
            elif bars_out > BREAK_MAX_WAIT and not timed_out:
                # o ngoai lau nhung phan lon nen van dong TRONG bien -> khong phai pha that
                if up_side:
                    r.high = max(r.high, k['ext'])
                else:
                    r.low = min(r.low, k['ext'])
                lab = _minor_label(r, up_side, strong=True)
                if lab is not None:
                    _mark_outer(r, k['ext_i'], lab, k['ext'], up_side)
                r.brk = None
                r.state = 'B'
                continue
            else:
                continue

        # ==================================== state C_pending: xac nhan/that bai cu rung chuyen
        if r.state == 'C_pending':
            shock = r.pending_shock
            span = max(1e-9, abs(shock['target_edge'] - shock['price']))
            up = shock['dir'] > 0
            # v6 muc 1.2(b): CHI noi bien phu o PHIA DOI DIEN (chua bi test) trong luc cho ket cuc.
            # Phia dang bi test (up=True -> canh DUOI dang test, tuc r.low) KHONG duoc tu noi theo
            # chinh cuc tri cua no — se noi mot lan duy nhat, SAU KHI biet ket cuc, trong _demote_shock.
            if up:
                if b['hi'] > r.high:
                    r.high = b['hi']
            else:
                if b['lo'] < r.low:
                    r.low = b['lo']
            if up:
                if b['hi'] > shock['peak']:
                    shock['peak'], shock['peak_i'] = b['hi'], i
                progress = (shock['peak'] - shock['price']) / span
                failed_now = b['c'] < shock['price'] - tol
            else:
                if b['lo'] < shock['peak']:
                    shock['peak'], shock['peak_i'] = b['lo'], i
                progress = (shock['price'] - shock['peak']) / span
                failed_now = b['c'] > shock['price'] + tol

            if (i - shock['start_i']) > SHOCK_MAX_WAIT:
                _demote_shock(r)
                _revert_to_B(r, i)
                continue
            if failed_now and progress < SHOCK_PROGRESS_MULT:
                _demote_shock(r)
                _revert_to_B(r, i)
                continue
            if progress >= SHOCK_PROGRESS_MULT and shock['event']['status'] == 'pending':
                shock['event']['status'] = 'confirmed'

            # LOI C: theo doi cu pha bien NGAY TRONG Phase C, dung dieu kien nhu B_brk
            oe = shock['out_edge']
            if up:
                decisive = b['c'] > oe + fail_tol and b['brat'] >= SOS_BODY_MIN
            else:
                decisive = b['c'] < oe - fail_tol and b['brat'] >= SOS_BODY_MIN
            if decisive:
                if shock.get('hold', 0) == 0:
                    shock['first_i'] = i
                shock['hold'] = shock.get('hold', 0) + 1
            else:
                shock['hold'] = 0
            if shock['hold'] >= BREAK_HOLD_BARS:
                _fire_break(B, r, i, up, oe, shock['start_i'])
            elif (not shock['lps_done'] and abs(b['c'] - shock['price']) <= 2.0 * tol
                  and (i - shock['start_i']) >= PIVOT_CONFIRM_BARS):
                _add_unique(r, i, 'LPS[C]' if up else 'LPSY[C]', b['c'], 'C')
                shock['lps_done'] = True

        # -------------------------------------------------------------- da pha xong -> dong range
        if r.state == 'END':
            e_end = r.end_i if r.end_i is not None else i
            e_end = max(r.phases[-1][1], min(len(B) - 1, e_end))
            r.phases[-1][2] = e_end
            r.end_i = e_end
            r.status = 'completed'
            ranges.append(r)
            active = None

    if active is not None:
        if active.solid_low is None:
            DISCARDED.append((active, 'chua chot xong Phase A khi het du lieu', len(B) - 1))
        else:
            if active.phases:
                active.phases[-1][2] = len(B) - 1
            ranges.append(active)
    return ranges


# ============================================================================
# Thong ke nhanh
# ============================================================================
def main():
    B = E.load_m1()
    print(f"M1={len(B)} nen  {B[0]['dt']} -> {B[-1]['dt']} (UTC)")
    ranges = detect(B)
    print(f"\nTong so range ve ra: {len(ranges)}   (bo: {len(DISCARDED)})")
    print(f"  completed={sum(1 for r in ranges if r.status=='completed')}  "
          f"active={sum(1 for r in ranges if r.status=='active')}")

    for tag in ('ACC', 'RE-ACC', 'DIST', 'RE-DIST', 'ACC?', 'DIST?'):
        group = [r for r in ranges if r.kind == tag]
        if not group:
            continue
        print(f"\n=== {tag} ({group[0].kind_vn}): {len(group)} range ===")
        for k, r in enumerate(group[:15], 1):
            dur = (r.end_i or len(B) - 1) - r.start_i
            evs = ";".join(f"{e['label']}@{B[e['i']]['dt'].strftime('%m-%d %H:%M')}"
                           for e in sorted(r.events, key=lambda e: e['i']))
            phs = ";".join(f"{p[0]}[{(p[2] or (r.end_i or len(B)-1)) - p[1] + 1}n]" for p in r.phases)
            sl = f"{r.solid_low:.1f}-{r.solid_high:.1f}" if r.solid_low is not None else "chua chot"
            print(f"  #{k} [{r.status}] {B[r.start_i]['dt']} -> "
                  f"{B[r.end_i]['dt'] if r.end_i else '(dang chay)'} ({dur} nen) "
                  f"chinh={sl} phu={r.low:.1f}-{r.high:.1f}")
            print(f"     su_kien: {evs}")
            print(f"     phase:   {phs}")

    # kiem tra hai luat ty le phase (L8 Phase C ngan nhat, L9 Phase B dai nhat)
    badB = badC = 0
    for r in ranges:
        lens = {}
        for ph, ps, pe in r.phases:
            pe2 = pe if pe is not None else (r.end_i or len(B) - 1)
            lens[ph] = lens.get(ph, 0) + (pe2 - ps + 1)
        if lens and lens.get('B', 0) != max(lens.values()):
            badB += 1
        # L8 do trong pham vi A/B/C/D: Phase E nam NGOAI range, do dai ve ra cua no la lua chon
        # hien thi (cat khi gia lui vao trong bien / khi da di 2x chieu cao), khong phai cau truc TR.
        inner = {k: v for k, v in lens.items() if k != 'E'}
        if 'C' in inner and inner['C'] != min(inner.values()):
            badC += 1
    print(f"\nL9 Phase B dai nhat: sai {badB}/{len(ranges)} range")
    print(f"L8 Phase C ngan nhat (trong A/B/C/D): sai {badC}/{len(ranges)} range")

    print("\n--- ly do BO ung vien ---")
    reasons = {}
    for _r, why, _i in DISCARDED:
        reasons[why] = reasons.get(why, 0) + 1
    for why, n in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"  {n:4d}  {why}")


if __name__ == '__main__':
    main()
