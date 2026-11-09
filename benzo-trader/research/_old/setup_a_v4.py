# -*- coding: utf-8 -*-
"""SETUP A-v4 "Phá hồi" — tập vùng mới + cú phá có ĐÀ (momentum) + bỏ cấm 18:00–19:20 VN.
Đặc tả: `plans/BENZO-A-V4-plan.md` (Fable). KHÔNG sửa setup_a_pha_hoi.py / kernel.py (chỉ import).

Chạy:  python3 setup_a_v4.py            → report/RESULTS-A-V4.md + report/img/a_v4_*.png
Test:  python3 -m pytest test_setup_a_v4.py -q

Một máy chung `detect()` chạy được cả 2 logic (M = 'v3' | 'mom') trên mọi tập vùng (Z = 'old' | 'new' | 'plus') và có/không cấm
mở cú phá 18:00–19:20 VN (H) ⇒ bảng 2×2×2 tách đóng góp. Ô (Z='old', M='v3', H=cấm) phải ra ĐÚNG lệnh của
setup_a_pha_hoi.detect(expire=30) (test).

Thuật ngữ: đà (momentum) = lực đẩy còn tiếp sau cú phá · nhịp hồi (pullback) = giá quay về cạnh · "đã trang bị" (armed) =
cực trị đã cách cạnh >= D_MIN nên mới được canh · CF = nến xác nhận (kernel.confirm_bars) · bootstrap = lấy mẫu lại có hoàn lại.

CÁC CHỖ TỰ QUYẾT (plan không nói rõ) — ghi lại ở report mục "Chỗ tự quyết":
  Q1 Thứ tự trong một nến M1 i là nến cuối của M5: xử lý sự kiện M5 (mở / hủy) TRƯỚC, rồi mới quét nến i (giống V3 và C#):
     trạng thái vừa mở ở i không xét vào lệnh ở i; trạng thái vừa hủy ở i không vào ở i.
  Q2 Vùng điểm + độ sâu hủy 1 giá: M5 đóng phía bên kia điểm <= 1 giá thì (z,+1) vẫn sống; KHÔNG mở (z,−1) song song
     (giữ bất biến "hai chiều của cùng z không cùng PHA" của plan). Đếm số lần bị chặn kiểu này.
  Q3 Band VA cũ (Z='old') trong logic đà: canh lên = VAH, canh xuống = VAL như V3; SL qua E ∓ 1 (như V3), KHÔNG qua mép xa
     của band (VA rộng 10–30 giá ⇒ mọi lệnh bị trần 4 giá loại); M5 đóng ngoài phía đối diện ⇒ hủy.
  Q4 Chân cú phá (leg) với vùng động: "nến đóng phía trong" so với giá trị vùng TẠI nến đó (VWAP thô, chưa áp Warm).
  Q5 "armed" là cờ dính, chỉ xét lại khi lập cực trị mới (đúng mã giả 2.2 bước 3). Đếm số lệnh mà lúc vào cực trị đã
     không còn cách E(i) >= D_MIN (cạnh động trôi lại gần) — chỉ báo.
  Q6 Hai vùng cùng nến: vùng không được chọn coi như không vào lệnh (đi tiếp bước 3–4 bình thường).
  Q7 Vùng cố định đổi giá trị / nguồn (band cũ đổi EU↔Y↔IB; VA Âu/IB bắt đầu/hết) ⇒ trạng thái về NGỦ ở sự kiện M5 kế tiếp
     (giống V3: V3 hủy khi đổi nguồn ở nến M5 kế tiếp).
  Q9 Plan 2.2 bước 4 viết "hết hạn ⇒ NGỦ; cú M5 ngoài kế tiếp sẽ mở PHA mới". Làm ĐÚNG CHỮ (bản chính): giá vẫn ở ngoài
     thì M5 kế tiếp mở lại ngay (chân lùi 60 nến, cực trị = cực trị trong 60 nến đó). Hệ quả: số "trạng thái PHA" phình lên
     (mở lại liên tục khi giá nằm xa vùng cả phiên) và lệnh có thể vào ở lần hồi về vùng sau một đoạn đi ngang dài. Đăng ký
     TRƯỚC khi chạy một độ nhạy `after_inside=True` (phải có M5 không đóng ngoài rồi mới mở lại) và tách lệnh theo cờ reopen.
  Q8 Nến M5 chỉ tính "đã đóng" khi còn nến sau nó trong dữ liệu hoặc nó là phút thứ 5 (zones_a_v4.m5_close_mask) — để
     chạy trên dữ liệu cắt ra đúng kết quả chạy đầy đủ.
"""
from __future__ import annotations

import os
import sys
import math
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import zones_a_v4 as ZA  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
D90 = os.path.join(ROOT, 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260723-20261021_90d')
REPORT = os.path.join(HERE, 'report')
IMG = os.path.join(REPORT, 'img')

# =============================== HẰNG SỐ ĐĂNG KÝ TRƯỚC (chốt trước lần chạy đầu) ===============================
RR = 3.0                  # TP 3R (QĐ-3); 2R chỉ là độ nhạy
RR2 = 2.0
ZONE_HALF = 1.0           # vùng chạm E ± 1 giá
N_MIN = 3                 # >= 3 nến không lập cực trị mới (đà chậm dần)
BODY = 0.5                # thân CF >= 50% biên độ (kernel)
LEG_LOOKBACK = 60
EXPIRE_V3 = 30            # V3: CF trong 30 nến sau nến phá
SM_NOPHA = (780, 860)     # 18:00–19:20 VN (sm)
SM_VOPEN = (860, 930)     # 19:20–20:30 VN — luật cứng engine C# InVirtualOpen
# --- 2 tham số tự do MỚI (plan 2.2) + 1 tái dùng
D_MIN = 2.0               # cực trị cách cạnh >= 2 giá mới "đã trang bị"
T_HOI = 30                # hết hạn: 30 nến tính từ CỰC TRỊ CUỐI
CANCEL_DEPTH = ZONE_HALF  # hủy khi M5 đóng phía trong sâu hơn 1 giá
SENS = (('D_MIN', 1.5), ('D_MIN', 3.0), ('T_HOI', 20), ('T_HOI', 60), ('CANCEL_DEPTH', 0.5), ('CANCEL_DEPTH', 1.5))
# --- đối chứng / thống kê
SHIFT_LO, SHIFT_HI, REPS, SHIFT_SEED = 3.0, 15.0, 100, 20261024
CTRL_DRAWS = 200
BOOT, BOOT_SEED = 10000, 0
MIN_N = 10
# --- tiêu chí port (plan mục 4), đăng ký trước
T1_N = 40                 # n(A-v4) >= 40 trên 61 phiên
T1_TEST_REF = -0.08       # R TB TEST của A-V3 gốc (n=8) — kiểm lại khi chạy
T1_N_TEST = 15
T1_TRAIN_MIN = -0.30
T1_EVE_GAP = 0.5          # khung 18:00–19:20 không âm nặng hơn phần còn lại quá 0,5R (n >= 10)
T2_N_TEST = 30
EXPECT_V3 = (20, 0.100, -0.68)
# --- các lựa chọn báo cáo (chốt trước khi chạy)
MAIN_VBLOCK = False       # bảng chính KHÔNG chặn CF trong 19:20–20:30 (giống A-V3 gốc của Python); bản có chặn báo kèm từng ô
WIN_LEN, WIN_STEP, WIN_RANGE = 70, 10, (580, 1200)   # đối chứng luật 19:20–20:30: mọi cửa sổ 70' bắt đầu 580..1130 bước 10',
                                                     # bỏ cửa sổ CHỒNG lên [860, 930) (chồng thì đối chứng lẫn chính nó)
CTRL1_STRATA = ('side', 'ztype', 'split')            # ĐC1: mỗi lệnh thật rút 1 nến cùng chiều, cùng LOẠI vùng, cùng TRAIN/TEST
DIST_BINS = ((2.0, 3.0), (3.0, 5.0), (5.0, 1e9))     # tách mô tả theo khoảng cách cực trị–E (giá)
CLOSED = ('TP', 'SL', 'TIME')


# =============================================================================================
# 1. DỮ LIỆU
# =============================================================================================
class Prep:
    """Mọi mảng cần cho detect(), tính 1 lần cho (df, prof). Dùng được cho dữ liệu cắt (test không nhìn trước)."""

    def __init__(self, df, prof, levels=None):
        self.df, self.prof, self.levels = df, prof, levels
        self.ctx = K._Ctx(df, prof)
        self.zc = K.zone_columns(df, prof, self.ctx)
        self.slev = ZA.session_levels(df, prof, self.ctx)
        self.m5c = ZA.m5_close_mask(df)
        self.cl, self.op, self.hi, self.lo = (df[c].to_numpy(float) for c in ('close', 'open', 'high', 'low'))
        self.rng = self.hi - self.lo
        self.sm = df['sm'].to_numpy()
        self.phase = df['phase'].to_numpy()
        self.sno = df['session_no'].to_numpy()
        self.bad = df['splice'].to_numpy() | df['thin'].to_numpy()
        self.mad = K.med_abs_delta(df)
        old = K.CONST['cf_body_frac']
        K.CONST['cf_body_frac'] = BODY
        try:
            self.cf = {1: K.confirm_bars(df, 1, self.mad).to_numpy(), -1: K.confirm_bars(df, -1, self.mad).to_numpy()}
        finally:
            K.CONST['cf_body_frac'] = old
        self.sbig = K.bars_since_biggest_bar(df).to_numpy()
        self.st = K.session_table(df)
        self.sessions = [(int(s), int(a), int(b)) for s, a, b in zip(self.st.index, self.st['start_pos'], self.st['end_pos'])]
        self.mode = K.mode_series(df, self.zc)
        st = self.st
        clean = (~st['splice'].to_numpy()) & (~st['thin'].to_numpy()) & (st['n'].to_numpy() >= K.CONST['min_bars_prof'])
        self.days = int(clean.sum())
        sp = np.where(st['session_id'].str[:10] <= K.CONST['split_train_end'], 'TRAIN', 'TEST')
        self.days_split = {k: int((clean & (sp == k)).sum()) for k in ('TRAIN', 'TEST')}
        self._zones = {}

    def zones(self, zset='new', hvn_w_band=True, va_dev=False):
        k = (zset, hvn_w_band, va_dev)
        if k not in self._zones:
            vd = None
            if va_dev:
                if self.levels is None:
                    raise ValueError('can levels de tinh VA dang hinh thanh')
                vd = ZA.dev_va(self.df, self.levels)
            Z = ZA.build_zones(self.df, self.zc, self.slev, zset, hvn_w_band, vd)
            # mảng THÔ cho chân cú phá (Q4): VWAP chưa áp Warm
            for z in Z:
                if z['ztype'] == 'VWAP_W':
                    z['lo_raw'] = z['hi_raw'] = self.zc['vwap_w'].to_numpy(float)
                elif z['ztype'] == 'VWAP_D':
                    z['lo_raw'] = z['hi_raw'] = self.zc['vwap_d'].to_numpy(float)
            self._zones[k] = Z
        return self._zones[k]


def load(base=D90, with_levels=False):
    df = K.load_bars(base + '_bars.csv')
    lv = pd.read_csv(base + '.csv', usecols=['bar_idx', 'price', 'volume']) if with_levels else None
    prof = K.build_profiles(df, lv if lv is not None else base + '.csv')
    return Prep(df, prof, lv)


# =============================================================================================
# 2. MÁY TRẠNG THÁI (V3 và ĐÀ) — một bản cho mỗi cặp (vùng z, chiều S)
# =============================================================================================
class St:
    __slots__ = ('zi', 'S', 'p0', 'E', 'zlo', 'zhi', 'lab', 'L', 'pk_pos', 'pk_val', 'pbmax', 'armed', 'brk_no', 'uid',
                 'n_ent', 'was_armed', 'reopen')


def detect(P, Z, logic='mom', ban=False, vblock=False, d_min=D_MIN, t_hoi=T_HOI, cancel=CANCEL_DEPTH, n_min=N_MIN,
           rr=RR, expire=EXPIRE_V3, shift=None, cands=None, funnel=None, trace=None, states_log=None, after_inside=False):
    """Trả list entry (dict) cho kernel.simulate.
    logic 'v3' = A V3 (mở khi M5 đóng ngoài 1 tick, hủy khi M5 đóng lại trong 1 tick, CF trong `expire` nến sau nến phá,
                 L của chân trước nến phá, không có 'đã trang bị').
    logic 'mom' = A-v4 mục 2.2 (trang bị D_MIN, L cập nhật theo đà, hết hạn T_HOI từ cực trị cuối, hủy khi M5 đóng trong > cancel).
    ban = cấm MỞ cú phá khi nến M5 phá đóng trong 18:00–19:20 VN (như V3). vblock = không vào lệnh khi nến CF trong 19:20–20:30 VN
    (luật engine C#; trạng thái vẫn chạy). shift = mảng δ theo session_no (đối chứng dời vùng) hoặc None.
    cands (list) = hồ đối chứng ĐC1 (nến trong trạng thái PHA [đã trang bị, chưa quá T_HOI], chạm E, hợp lệ).
    funnel (dict) = phễu đếm. trace (dict idx->None) = ghi ảnh trạng thái mọi vùng tại các nến đó (trước bước 2).
    states_log (list) = ghi mỗi trạng thái PHA khi kết thúc.
    after_inside (độ nhạy Q9): sau khi (z,S) HẾT HẠN, chỉ mở lại khi đã có ít nhất một nến M5 KHÔNG đóng ngoài phía S
    (mặc định False = đúng chữ plan 2.2 bước 4: 'cú M5 ngoài kế tiếp sẽ mở PHA mới'). Mỗi trạng thái mang cờ reopen = mở lại
    sau hết hạn mà giá chưa từng về trong."""
    mom = logic == 'mom'
    cl, hi, lo, rng, sm, ph = P.cl, P.hi, P.lo, P.rng, P.sm, P.phase
    bad, cf, sbig, m5c = P.bad, P.cf, P.sbig, P.m5c
    df = P.df
    nz = len(Z)
    if shift is not None:
        dl = shift[P.sno]
        LO = [z['lo'] + dl for z in Z]
        HI = [z['hi'] + dl for z in Z]
        LOR = [z.get('lo_raw', z['lo']) + dl for z in Z]
        HIR = [z.get('hi_raw', z['hi']) + dl for z in Z]
    else:
        LO = [z['lo'] for z in Z]
        HI = [z['hi'] for z in Z]
        LOR = [z.get('lo_raw', z['lo']) for z in Z]
        HIR = [z.get('hi_raw', z['hi']) for z in Z]
    LAB = [z.get('lab') for z in Z]
    DYN = [z['dyn'] for z in Z]
    BAND = [z['band'] for z in Z]
    SLF = [z['sl_far'] for z in Z]
    RANK = [z['rank'] for z in Z]
    NAME = [z['name'] for z in Z]
    ZT = [z['ztype'] for z in Z]
    OLD = [z['ztype'] == 'BAND_CU' for z in Z]
    fn = funnel if funnel is not None else {}
    for k in ('open', 'open_fresh', 'armed', 'with_entry', 'cancel', 'expire', 'end', 'blocked_opp', 'reset_value', 'no_risk',
              'armed_drift', 'conflict', 'blocked_reopen', 'armed_fresh', 'entry_fresh'):
        fn.setdefault(k, 0)
    fn.setdefault('open_by', {})
    fn.setdefault('armed_by', {})
    fn.setdefault('entry_by', {})
    entries = []
    count = {}
    bcount = {}
    uid = [0]

    def lab_of(zi, i):
        return LAB[zi][i] if LAB[zi] is not None else NAME[zi]

    def finish(stt, why):
        fn[why] = fn.get(why, 0) + 1
        if not stt.reopen:
            fn['armed_fresh'] += int(stt.was_armed)
            fn['entry_fresh'] += int(stt.n_ent > 0)
        if stt.was_armed:
            fn['armed'] += 1
            fn['armed_by'][ZT[stt.zi]] = fn['armed_by'].get(ZT[stt.zi], 0) + 1
        if stt.n_ent:
            fn['with_entry'] += 1
            fn['entry_by'][ZT[stt.zi]] = fn['entry_by'].get(ZT[stt.zi], 0) + 1
        if states_log is not None:
            states_log.append(dict(zi=stt.zi, ztype=ZT[stt.zi], S=stt.S, p0=stt.p0, pk_pos=stt.pk_pos, pk_val=stt.pk_val, E=stt.E,
                                   why=why, armed=stt.was_armed, n_ent=stt.n_ent, brk_no=stt.brk_no, reopen=stt.reopen))

    def open_state(zi, out, i, a, s):
        lo_v, hi_v = LO[zi][i], HI[zi][i]
        canh = hi_v if out > 0 else lo_v
        k = i
        lim = max(a, i - LEG_LOOKBACK)
        if DYN[zi]:
            ref = HIR[zi] if out > 0 else LOR[zi]
            while k > lim and ((cl[k] > ref[k]) if out > 0 else (cl[k] < ref[k])):
                k -= 1
        else:
            while k > lim and ((cl[k] > canh) if out > 0 else (cl[k] < canh)):
                k -= 1
        f = k + 1 if k < i else i
        seg_r = rng[f:i + 1]
        L = float(seg_r.max())
        if out > 0:
            pk = f + int(np.argmax(hi[f:i + 1]))
            pkv = float(hi[pk])
        else:
            pk = f + int(np.argmin(lo[f:i + 1]))
            pkv = float(lo[pk])
        pbmax = float(rng[pk + 1:i + 1].max()) if pk < i else 0.0
        stt = St()
        stt.zi, stt.S, stt.p0, stt.E, stt.zlo, stt.zhi, stt.lab = zi, out, i, float(canh), float(lo_v), float(hi_v), lab_of(zi, i)
        stt.L, stt.pk_pos, stt.pk_val, stt.pbmax = L, pk, pkv, pbmax
        stt.armed = bool(mom and out * (pkv - canh) >= d_min)
        stt.was_armed = stt.armed
        kb = (s, stt.lab, out)
        bcount[kb] = bcount.get(kb, 0) + 1
        stt.brk_no = bcount[kb]
        uid[0] += 1
        stt.uid = uid[0]
        stt.n_ent = 0
        stt.reopen = bool(need_in.get((zi, out), False))
        need_in[(zi, out)] = False
        fn['open'] += 1
        if not stt.reopen:
            fn['open_fresh'] += 1
        fn['open_by'][ZT[zi]] = fn['open_by'].get(ZT[zi], 0) + 1
        return stt

    for s, a, b in P.sessions:
        states = {}
        need_in = {}
        for i in range(a, b + 1):
            # ---------------- sự kiện M5 (Q1: trước khi quét nến i)
            if m5c[i]:
                C = cl[i]
                for zi in range(nz):
                    lo_v, hi_v = LO[zi][i], HI[zi][i]
                    if lo_v != lo_v:
                        for S in (1, -1):
                            x = states.pop((zi, S), None)
                            if x is not None:
                                finish(x, 'reset_value')
                        continue
                    if not DYN[zi]:
                        lb = lab_of(zi, i)
                        for S in (1, -1):
                            x = states.get((zi, S))
                            if x is not None and (x.zlo != lo_v or x.zhi != hi_v or x.lab != lb):
                                finish(states.pop((zi, S)), 'reset_value')
                    out = 1 if C > hi_v else (-1 if C < lo_v else 0)
                    for S in (1, -1):
                        if out != S and need_in.get((zi, S)):
                            need_in[(zi, S)] = False
                    if not mom:
                        cur = states.get((zi, 1)) or states.get((zi, -1))
                        if out == 0:
                            if cur is not None:
                                finish(states.pop((zi, cur.S)), 'cancel')
                            continue
                        if cur is not None and cur.S == out:
                            continue
                        if cur is not None:
                            finish(states.pop((zi, cur.S)), 'cancel')
                        if ban and SM_NOPHA[0] <= sm[i] < SM_NOPHA[1]:
                            continue
                        states[(zi, out)] = open_state(zi, out, i, a, s)
                    else:
                        for S in (1, -1):
                            x = states.get((zi, S))
                            if x is None:
                                continue
                            canh = (hi_v if S > 0 else lo_v) if DYN[zi] else x.E
                            if S * (C - canh) < -cancel or (BAND[zi] and out == -S):
                                finish(states.pop((zi, S)), 'cancel')
                        if out != 0:
                            if (zi, out) in states:
                                continue
                            if (zi, -out) in states:
                                fn['blocked_opp'] += 1
                                continue
                            if ban and SM_NOPHA[0] <= sm[i] < SM_NOPHA[1]:
                                continue
                            if after_inside and need_in.get((zi, out)):
                                fn['blocked_reopen'] += 1
                                continue
                            states[(zi, out)] = open_state(zi, out, i, a, s)
            if not states:
                continue
            # ---------------- quét nến i
            okbar = (not bad[i]) and ph[i] != 'OFF' and not (1 <= sbig[i] <= 3)
            if vblock and SM_VOPEN[0] <= sm[i] < SM_VOPEN[1]:
                okbar = False
            ci = cl[i]
            if trace is not None and i in trace:
                trace[i] = [dict(zone=NAME[x.zi], S=x.S, p0=x.p0, pk_pos=x.pk_pos, pk_val=x.pk_val, L=x.L, pbmax=x.pbmax,
                                 armed=x.armed, E=((HI[x.zi][i] if x.S > 0 else LO[x.zi][i]) if DYN[x.zi] else x.E),
                                 age=i - x.pk_pos) for x in states.values()]
            cand_ent = []
            Ecache = {}
            for key, x in list(states.items()):
                if x.p0 >= i:
                    continue
                zi, S = x.zi, x.S
                E = (HI[zi][i] if S > 0 else LO[zi][i]) if DYN[zi] else x.E
                Ecache[key] = E
                if not mom and i > x.p0 + expire:
                    continue
                near = abs(ci - E) <= ZONE_HALF or (lo[i] <= E <= hi[i])
                if not (okbar and near):
                    continue
                age = i - x.pk_pos
                if mom:
                    if not (x.armed and age <= t_hoi):
                        continue
                if cands is not None:
                    cands.append((i, S, zi, E))
                npb = i - 1 - x.pk_pos
                if npb < n_min or not (x.pbmax < x.L) or not cf[S][i]:
                    continue
                ckey = (s, x.lab, S, round(E, 1)) if OLD[zi] else (s, NAME[zi], S)
                if count.get(ckey, 0) >= 2:
                    continue
                if SLF[zi]:
                    far = (LO[zi][i] if S > 0 else HI[zi][i])
                else:
                    far = E
                struct = min(lo[i], far - ZONE_HALF) if S > 0 else max(hi[i], far + ZONE_HALF)
                r = K.risk(df, i, S, struct, rr=rr)
                if r is None:
                    fn['no_risk'] += 1
                    continue
                cand_ent.append((abs(ci - E), RANK[zi], zi, S, key, E, r, ckey, npb))
            chosen = None
            if cand_ent:
                cand_ent.sort(key=lambda t: (t[0], t[1], t[2]))
                if len(cand_ent) > 1:
                    fn['conflict'] += 1
                chosen = cand_ent[0]
                _, _, zi, S, key, E, r, ckey, npb = chosen
                x = states[key]
                dist = S * (x.pk_val - E)
                if mom and dist < d_min:
                    fn['armed_drift'] += 1
                entries.append(dict(idx=i, side=S, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='A', zone=NAME[zi], zbase=ZT[zi],
                                    ztype=ZT[zi] if not OLD[zi] else ('BAND_' + str(x.lab)), E=float(E), L=float(x.L),
                                    pbmax=float(x.pbmax), npb=int(npb), p0=int(x.p0), pk_pos=int(x.pk_pos), pk_val=float(x.pk_val),
                                    dist_pk=float(dist), bars_mom=int(x.pk_pos - x.p0), brk_no=int(x.brk_no),
                                    sm_p0=int(sm[x.p0]), sm_cf=int(sm[i]), zlo=float(LO[zi][i]), zhi=float(HI[zi][i]),
                                    uid=int(x.uid), ent_no=int(x.n_ent + 1), floor=bool(r['floor_applied']), reopen=bool(x.reopen),
                                    note='pha %s %s E=%.1f cuc tri %.1f gia sau %d nen, hoi %d nen' % (
                                        'len' if S > 0 else 'xuong', NAME[zi], E, dist, x.pk_pos - x.p0, npb)))
                count[ckey] = count.get(ckey, 0) + 1
                x.n_ent += 1
                x.pk_pos, x.pk_val, x.pbmax = i, (hi[i] if S > 0 else lo[i]), 0.0
            # bước 3–4 cho các trạng thái còn lại
            for key, x in list(states.items()):
                if x.p0 >= i or (chosen is not None and key == chosen[4]):
                    continue
                if not mom and i > x.p0 + expire:
                    continue
                S = x.S
                ext = hi[i] if S > 0 else lo[i]
                if S * (ext - x.pk_val) > 0:
                    x.pk_pos, x.pk_val, x.pbmax = i, float(ext), 0.0
                    if mom:
                        x.L = max(x.L, float(rng[i]))
                        E = Ecache.get(key)
                        if E is None:
                            E = (HI[x.zi][i] if S > 0 else LO[x.zi][i]) if DYN[x.zi] else x.E
                        if not x.armed and S * (x.pk_val - E) >= d_min:
                            x.armed = True
                            x.was_armed = True
                else:
                    x.pbmax = max(x.pbmax, float(rng[i]))
                if mom and (i - x.pk_pos) > t_hoi:
                    finish(states.pop(key), 'expire')
                    need_in[key] = True
        for key in list(states):
            finish(states.pop(key), 'end')
    entries.sort(key=lambda e: e['idx'])
    return entries


# =============================================================================================
# 3. CHẨN ĐOÁN CỦA FABLE (plan mục 1) — chạy lại trên band cũ, in số
# =============================================================================================
def diag_v3_states(P):
    """Port nguyên logic scratchpad/diag_a_momentum.py của Fable: mỗi lần M5 đóng ngoài band cũ khi chưa có trạng thái = 1
    trạng thái; theo dõi cực trị, lần chạm E đầu, kết thúc (M5 đóng lại trong / đóng ngược phía / hết phiên). Bỏ phiên thin/splice."""
    import setup_a_pha_hoi as SA
    df, zc = P.df, P.zc
    m5 = K.m5_bars(df)
    bh, bl, src = SA.band_arrays(df, zc, m5)
    cl, hi, lo = P.cl, P.hi, P.lo
    sm = P.sm
    st = P.st
    end_of = dict(zip(st.index.to_numpy(), st['end_pos'].to_numpy()))
    m5_sno, m5_lp, m5_close = m5['session_no'].to_numpy(), m5['last_pos'].to_numpy(), m5['close'].to_numpy(float)
    rows = []
    for s in st.index.to_numpy():
        if P.bad[int(st['start_pos'].loc[s])]:
            continue
        state = None
        for j in np.flatnonzero(m5_sno == s):
            lp = int(m5_lp[j])
            if bh[j] != bh[j]:
                state = None
                continue
            c = m5_close[j]
            out = 1 if c > bh[j] else (-1 if c < bl[j] else 0)
            if state is not None:
                S, E, p0 = state['S'], state['E'], state['p0']
                for i in range(state['last'] + 1, lp + 1):
                    ext = hi[i] if S > 0 else lo[i]
                    if (S > 0 and ext > state['pk_val']) or (S < 0 and ext < state['pk_val']):
                        state['pk_val'], state['pk_pos'] = ext, i
                    if (abs(cl[i] - E) <= 1.0 or (lo[i] <= E <= hi[i])) and state['ft'] is None and i > p0:
                        state['ft'] = i
                state['last'] = lp
                if out != S:
                    state['end'], state['why'] = lp, ('M5 dong lai trong' if out == 0 else 'M5 dong nguoc phia')
                    rows.append(state)
                    state = None
            if out != 0 and state is None:
                E = bh[j] if out > 0 else bl[j]
                state = dict(S=out, E=float(E), p0=lp, last=lp, pk_val=float(hi[lp] if out > 0 else lo[lp]), pk_pos=lp, ft=None,
                             end=None, why=None, nopha=bool(SM_NOPHA[0] <= sm[lp] < SM_NOPHA[1]))
        if state is not None:
            state['end'], state['why'] = int(end_of[s]), 'het phien'
            rows.append(state)
    t = pd.DataFrame(rows)
    t['bars_to_peak'] = t['pk_pos'] - t['p0']
    t['peak_dist'] = (t['pk_val'] - t['E']) * t['S']
    t['alive'] = t['end'] - t['p0']
    t['touched'] = t['ft'].notna()
    t['to_touch'] = t['ft'] - t['p0']
    t['touch_after_peak'] = t['touched'] & (t['ft'] > t['pk_pos'])
    n = len(t)
    q = lambda x, p: float(np.nanpercentile(x, p))  # noqa: E731
    d = dict(n=n, nopha=int(t['nopha'].sum()),
             pk_med=q(t['bars_to_peak'], 50), pk_p75=q(t['bars_to_peak'], 75), pk_p90=q(t['bars_to_peak'], 90),
             pk_gt30=int((t['bars_to_peak'] > 30).sum()),
             dist_med=q(t['peak_dist'], 50), dist_p75=q(t['peak_dist'], 75), dist_lt2=float((t['peak_dist'] < 2).mean()),
             dist_ge2=float((t['peak_dist'] >= 2).mean()),
             end_in=int((t['why'] == 'M5 dong lai trong').sum()), end_sess=int((t['why'] == 'het phien').sum()),
             end_opp=int((t['why'] == 'M5 dong nguoc phia').sum()), alive_med=q(t['alive'], 50),
             touched=int(t['touched'].sum()), touch_med=q(t.loc[t['touched'], 'to_touch'], 50),
             touch_after_peak=int(t['touch_after_peak'].sum()),
             touch_gt30=int((t['touched'] & (t['to_touch'] > 30)).sum()),
             cancel_no_touch=int(((t['why'] == 'M5 dong lai trong') & ~t['touched']).sum()))
    return d


# =============================================================================================
# 4. MÔ PHỎNG + THỐNG KÊ
# =============================================================================================
CFGS = [  # (khoá, tên hiển thị, Z, M, H=cấm 18:00–19:20?)
    ('goc', 'A-V3 gốc', 'old', 'v3', True),
    ('a', '(a) chỉ đổi vùng', 'new', 'v3', True),
    ('b', '(b) chỉ đổi logic đà', 'old', 'mom', True),
    ('c', '(c) chỉ bỏ cấm giờ', 'old', 'v3', False),
    ('d', '(d) A-v4', 'new', 'mom', False),
    ('plus', 'A-v4+ (thêm VA Âu/IB)', 'plus', 'mom', False),
    ('p1', '(phụ) vùng mới + V3 + bỏ cấm', 'new', 'v3', False),
    ('p2', '(phụ) vùng cũ + đà + bỏ cấm', 'old', 'mom', False),
    ('p3', '(phụ) vùng mới + đà + cấm', 'new', 'mom', True),
]
CFG = {k: dict(name=n, zset=z, logic=m, ban=h) for k, n, z, m, h in CFGS}
GROUPS = (('TRAIN', 'split', 'TRAIN'), ('TEST', 'split', 'TEST'), ('GỘP', None, None),
          ('T8', 'thang', 'T8'), ('T9', 'thang', 'T9'), ('T10', 'thang', 'T10'))
ZT_ORDER = ('VWAP_W', 'VWAP_D', 'HVN_W', 'HVN_D', 'VAH_D', 'VAL_D', 'VAH_EU', 'VAL_EU', 'IB_H', 'IB_L', 'BAND_CU')


def _bv():
    import benzo_vcl as BV
    return BV


def thang(sid):
    m = int(str(sid)[5:7])
    return 'T8' if m <= 8 else ('T9' if m == 9 else 'T10')


def closed(t):
    return t[t['outcome'].isin(CLOSED)] if len(t) else t


def sim(P, ents, one=True):
    t = K.simulate(P.df, ents, one_at_a_time=one)
    if len(t):
        t['thang'] = [thang(x) for x in t['session_id']]
    return t


def run(P, key=None, zset=None, logic=None, ban=None, vblock=MAIN_VBLOCK, rr=RR, zkw=None, cands=None, funnel=None, **kw):
    if key is not None:
        c = CFG[key]
        zset, logic, ban = c['zset'], c['logic'], c['ban']
    Z = P.zones(zset, **(zkw or {}))
    ents = detect(P, Z, logic=logic, ban=ban, vblock=vblock, rr=rr, cands=cands, funnel=funnel, **kw)
    return ents, sim(P, ents), Z


def rs(r):
    return _bv().rstat(np.asarray(r, float))


def streak(r):
    b = s_ = 0
    for x in r:
        s_ = s_ + 1 if x <= 0 else 0
        b = max(b, s_)
    return b


def gmask(t, col, val):
    return np.ones(len(t), bool) if col is None else (t[col] == val).to_numpy()


def summ(P, ents, tr):
    c = closed(tr)
    r = c['r'].to_numpy(float) if len(c) else np.array([])
    s = rs(r)
    out = dict(n=s['n'], pday=s['n'] / P.days, wr=s['wr'], m=s['m'], lo=s['lo'], hi=s['hi'], se=s['se'],
               pts=float(c['pts'].mean()) if len(c) else np.nan, streak=streak(r), raw=len(ents), n_open=int((tr['outcome'] == 'OPEN').sum()) if len(tr) else 0,
               sd=float(r.std(ddof=1)) if len(r) > 1 else np.nan)
    for g, col, val in GROUPS:
        if g == 'GỘP':
            continue
        m = gmask(c, col, val) if len(c) else np.zeros(0, bool)
        out[g] = rs(r[m]) if len(c) else rs([])
    for ph in K.PHASES:
        out['ph_' + ph] = rs(r[(c['phase'] == ph).to_numpy()]) if len(c) else rs([])
    if len(c):
        eve = (((c['sm_p0'] >= SM_NOPHA[0]) & (c['sm_p0'] < SM_NOPHA[1])) | ((c['sm_cf'] >= SM_NOPHA[0]) & (c['sm_cf'] < SM_NOPHA[1]))).to_numpy()
        vo = ((c['sm_cf'] >= SM_VOPEN[0]) & (c['sm_cf'] < SM_VOPEN[1])).to_numpy()
    else:
        eve = vo = np.zeros(0, bool)
    out['eve'], out['not_eve'] = rs(r[eve]), rs(r[~eve])
    out['vo'], out['not_vo'] = rs(r[vo]), rs(r[~vo])
    return out


def f(x, p=2, sign=True):
    if x is None or x != x:
        return '—'
    return ('%+.*f' % (p, x)) if sign else ('%.*f' % (p, x))


def pc(x):
    return '—' if x != x else '%.1f%%' % (100 * x)


def nr(s):
    return '%d / %s' % (s['n'], f(s['m']))


# =============================================================================================
# 5. ĐỐI CHỨNG
# =============================================================================================
def judge(c, bands):
    """So R TB thật (theo nhóm) với dải đối chứng; ngưỡng NGUYÊN PLAN-LAN-CHAM mục 5 (benzo_vcl.verdict)."""
    BV = _bv()
    r = c['r'].to_numpy(float) if len(c) else np.array([])
    cmp, ns = {}, {}
    for g, col, val in GROUPS:
        m = gmask(c, col, val) if len(c) else np.zeros(0, bool)
        s = rs(r[m]) if len(c) else rs([])
        ns[g] = s['n']
        b = bands.get(g, (np.nan,) * 3)
        cmp[g] = (s['m'], s['se'], s['n'], *b)
    ok = ns['TRAIN'] >= MIN_N and ns['TEST'] >= MIN_N
    return BV.verdict(cmp, ok), cmp


def _struct(P, Z, zi, i, S, E):
    z = Z[zi]
    far = (z['lo'][i] if S > 0 else z['hi'][i]) if z['sl_far'] else E
    return min(P.lo[i], far - ZONE_HALF) if S > 0 else max(P.hi[i], far + ZONE_HALF)


def ctrl1(P, Z, c, cands, rr=RR, ndraw=CTRL_DRAWS, seed0=1000):
    """ĐC1 — vào NGẪU NHIÊN trong cùng trạng thái: hồ = nến trong trạng thái PHA (logic đà: đã trang bị, chưa quá T_HOI), chạm E,
    hợp lệ; KHÔNG cần nhịp hồi >= 3, pbmax < L, CF. Mỗi lệnh thật rút 1 nến cùng chiều, cùng LOẠI vùng, cùng TRAIN/TEST; SL/TP y công thức."""
    if not len(c):
        return {}, 0
    real = set(int(x) for x in c['idx'])
    split = P.df['split'].to_numpy()
    seen = set()
    pool = {}
    for (i, S, zi, E) in cands:
        if i in real or (i, S, zi) in seen:
            continue
        seen.add((i, S, zi))
        r = K.risk(P.df, i, S, _struct(P, Z, zi, i, S, E), rr=rr)
        if r is None:
            continue
        key = (S, Z[zi]['ztype'], split[i])
        pool.setdefault(key, []).append(dict(idx=int(i), side=int(S), entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='CTRL1', zone=Z[zi]['name']))
    npool = sum(len(v) for v in pool.values())
    recs = [(int(x.side), str(x.zbase), str(x.split), str(x.thang)) for x in c.itertuples()]
    per = {g: [] for g, _, _ in GROUPS}
    for d in range(ndraw):
        g_ = np.random.default_rng(seed0 + d)
        ents, grp = [], []
        for S, zt, sp, th in recs:
            pl = pool.get((S, zt, sp))
            if not pl:
                continue
            e = dict(pl[int(g_.integers(len(pl)))])
            e['k'] = len(ents)
            ents.append(e)
            grp.append((sp, th))
        if not ents:
            continue
        t = K.simulate(P.df, ents, one_at_a_time=False)
        t = closed(t)
        if not len(t):
            continue
        rv = t['r'].to_numpy(float)
        spv = np.array([grp[k][0] for k in t['k']])
        thv = np.array([grp[k][1] for k in t['k']])
        for g, col, val in GROUPS:
            m = np.ones(len(t), bool) if col is None else (spv == val if col == 'split' else thv == val)
            per[g].append(rv[m].mean() if m.any() else np.nan)
    return {g: _bv().band(v) for g, v in per.items()}, npool


class _SwapMap:
    def __init__(self, m):
        self.m = m

    def __enter__(self):
        self.old = K.ZONE_NAME2COL
        K.ZONE_NAME2COL = self.m

    def __exit__(self, *a):
        K.ZONE_NAME2COL = self.old


def control_sample_map(df, zcols, mode, entries, name2col, **kw):
    """Bọc kernel.control_sample (KHÔNG đổi chữ ký cũ): truyền bảng tên vùng → cột qua tham số, thay tạm ZONE_NAME2COL."""
    with _SwapMap(name2col):
        return K.control_sample(df, zcols, mode, entries=entries, **kw)


def ctrl2(P, Z, c, ndraw=CTRL_DRAWS):
    """ĐC2 — kernel.control_sample: mỗi lệnh thật rút 1 nến 'ở vùng' (|close − E| <= 1 hoặc râu chạm E, E = cạnh của ĐÚNG vùng đó theo
    chiều lệnh, tại từng nến), cùng chế độ kernel, cùng chiều; SL = râu nến đó + 0,3; cùng R:R. 200 lần."""
    if not len(c):
        return {}
    zi_of = {z['name']: k for k, z in enumerate(Z)}
    cols, name2col = {}, {}
    recs = []
    grp = {}
    for x in c.itertuples():
        key = '%s|%d' % (x.zone, x.side)
        if key not in cols:
            z = Z[zi_of[x.zone]]
            cols[key] = z['hi'] if x.side > 0 else z['lo']
            name2col[key] = key
        recs.append(dict(idx=int(x.idx), side=int(x.side), entry=float(x.entry), sl=float(x.sl), tp=float(x.tp), setup='A', zone=key))
        grp[int(x.idx)] = (x.split, x.thang)
    zcols = pd.DataFrame(cols, index=P.df.index)
    per = {g: [] for g, _, _ in GROUPS}
    for sd in range(ndraw):
        ce = control_sample_map(P.df, zcols, P.mode, recs, name2col, n_random=1, seed=sd, tol=1.0)
        if not ce:
            continue
        t = closed(K.simulate(P.df, ce, one_at_a_time=False))
        if not len(t):
            continue
        src = t['note'].str.extract(r'idx (\d+)')[0].astype(int).map(grp)
        spv = np.array([v[0] for v in src])
        thv = np.array([v[1] for v in src])
        rv = t['r'].to_numpy(float)
        for g, col, val in GROUPS:
            m = np.ones(len(t), bool) if col is None else (spv == val if col == 'split' else thv == val)
            per[g].append(rv[m].mean() if m.any() else np.nan)
    return {g: _bv().band(v) for g, v in per.items()}


def shift_matrix(P):
    """Cùng cách sinh như benzo_vcl.Data (hạt 20261024): δ ~ U[3,15] × dấu ngẫu nhiên, (phiên, bản)."""
    rng = np.random.default_rng(SHIFT_SEED)
    nS = int(P.sno.max()) + 1
    return rng.uniform(SHIFT_LO, SHIFT_HI, (nS, REPS)) * rng.choice([-1.0, 1.0], (nS, REPS))


_G = {}


def _rep(k):
    P, key, dsh = _G['P'], _G['key'], _G['dsh']
    ents, tr, _ = run(P, key, shift=dsh[:, k])
    c = closed(tr)
    rv = c['r'].to_numpy(float) if len(c) else np.array([])
    out = {'_n': len(c)}
    for g, col, val in GROUPS:
        m = gmask(c, col, val) if len(c) else np.zeros(0, bool)
        out[g] = float(rv[m].mean()) if m.any() else np.nan
    return out


def ctrl3(P, key, workers=12):
    """ĐC3 — dời CẢ bản đồ vùng của mỗi phiên δ (100 bản, cùng ma trận cho mọi cấu hình), chạy nguyên máy trạng thái."""
    import multiprocessing as mp
    _G.update(P=P, key=key, dsh=shift_matrix(P))
    ctx = mp.get_context('fork')
    with ctx.Pool(workers) as pool:
        res = pool.map(_rep, range(REPS))
    bands = {g: _bv().band([x[g] for x in res]) for g, _, _ in GROUPS}
    pday = _bv().band([x['_n'] / P.days for x in res])
    return bands, pday


def mde(sd, n1, n2=None):
    if n1 < 2 or sd != sd:
        return np.nan
    return 2.8 * sd * math.sqrt(1.0 / n1 + (1.0 / n2 if n2 else 0.0))


# =============================================================================================
# 6. LUẬT 19:20–20:30 (chỉ báo) — A-v4, A gốc và B/C/D (detect cũ, ô chính như benzo_vcl.MAIN)
# =============================================================================================
def windows():
    w = []
    for s0 in range(WIN_RANGE[0], WIN_RANGE[1] - WIN_LEN + 1, WIN_STEP):
        if s0 < SM_VOPEN[1] and s0 + WIN_LEN > SM_VOPEN[0]:
            continue
        w.append((s0, s0 + WIN_LEN))
    return w


def window_test(c, sm_cf):
    """Hiệu R TB (CF trong cửa sổ − ngoài) cho 19:20–20:30 và cho các cửa sổ đối chứng."""
    r = c['r'].to_numpy(float)

    def d(a, b):
        m = (sm_cf >= a) & (sm_cf < b)
        if m.sum() == 0 or (~m).sum() == 0:
            return np.nan, int(m.sum()), np.nan, np.nan
        return float(r[m].mean() - r[~m].mean()), int(m.sum()), float(r[m].mean()), float((r[m] > 0).mean())
    tgt = d(*SM_VOPEN)
    oth = [d(a, b)[0] for a, b in windows()]
    oth = np.array([x for x in oth if x == x])
    q5, q95 = (np.quantile(oth, 0.05), np.quantile(oth, 0.95)) if len(oth) else (np.nan, np.nan)
    if tgt[1] < MIN_N:
        v = 'không áp dụng (n = %d < 10 trong khung)' % tgt[1]
    else:
        v = 'NGOÀI dải 5–95%' if (tgt[0] < q5 or tgt[0] > q95) else 'trong dải 5–95%'
    rest = r[~((sm_cf >= SM_VOPEN[0]) & (sm_cf < SM_VOPEN[1]))]
    return dict(n_in=tgt[1], r_in=tgt[2], wr_in=tgt[3], r_out=float(rest.mean()) if len(rest) else np.nan,
                wr_out=float((rest > 0).mean()) if len(rest) else np.nan, n_out=len(rest), diff=tgt[0], q5=q5, q95=q95, nwin=len(oth), v=v)


def other_setups(P):
    """Lệnh đã đóng của B, C, D (ô chính đúng các RESULTS cũ, gọi detect không sửa)."""
    import setup_b_hap_thu as SB
    import setup_c_fade_canh as SC
    import setup_d_trap as SD
    BV = _bv()
    out = {}
    PB = SB.prepare(P.df, P.prof)
    out['B Hấp thụ'] = SB.detect(PB, BV.MAIN['B']['theta'], BV.MAIN['B']['N'])
    PC = SC.prepare(D90)
    out['C Fade cạnh'] = SC.detect(PC['df'], PC['zc'], PC['mf'], mad=PC['mad'], **BV.MAIN['C'])
    PD = SD.Prep(D90 + '_bars.csv', D90 + '.csv')
    out['D Trap'] = SD.detect(PD, **BV.MAIN['D'])
    res = {}
    for k, e in out.items():
        t = closed(sim(P, e))
        res[k] = t
    return res


# =============================================================================================
# 7. VẼ
# =============================================================================================
def plot_session(P, Z, trades, sid, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    t = trades[trades['session_id'] == sid].sort_values('idx')
    t = t[t['outcome'].isin(['TP', 'SL'])].head(3)
    if not len(t):
        return None
    zi_of = {z['name']: k for k, z in enumerate(Z)}
    fig, axes = plt.subplots(len(t), 1, figsize=(15, 5.2 * len(t)), squeeze=False)
    df = P.df
    for ax, x in zip(axes[:, 0], t.itertuples()):
        a = max(int(x.p0) - 25, int(P.st.loc[P.sno[x.idx], 'start_pos']))
        b = min(len(df) - 1, int(x.exit_idx) + 12, a + 200)
        rr = np.arange(a, b + 1)
        up = P.cl[rr] >= P.op[rr]
        ax.vlines(rr, P.lo[rr], P.hi[rr], color=np.where(up, '#2a7a3b', '#b23a3a'), lw=0.8)
        ax.bar(rr, np.abs(P.cl[rr] - P.op[rr]) + 0.02, bottom=np.minimum(P.op[rr], P.cl[rr]), width=0.6,
               color=np.where(up, '#2a7a3b', '#b23a3a'), edgecolor='none')
        z = Z[zi_of[x.zone]]
        if z['band'] and z['lo'][x.idx] != z['hi'][x.idx]:
            ax.fill_between(rr, z['lo'][rr], z['hi'][rr], color='#e8a33c', alpha=0.25, lw=0, label='dải vùng %s' % x.zone)
        e_line = (z['hi'] if x.side > 0 else z['lo'])[rr]
        ax.plot(rr, e_line, color='#e8a33c', lw=1.6, label='cạnh E (%s)' % x.zone)
        ax.axvline(x.p0, color='#555555', lw=1, ls=':')
        ax.annotate('M5 phá đóng', (x.p0, np.nanmax(P.hi[rr])), fontsize=8, color='#555555', ha='left', va='top')
        ax.plot([x.pk_pos], [x.pk_val], marker='v' if x.side > 0 else '^', ms=10, color='#6a3d9a', ls='none',
                label='cực trị cuối (cách E %.1f giá; vị trí so với nến phá %+d nến)' % (x.dist_pk, x.bars_mom))
        ax.axvspan(x.pk_pos + 0.5, x.idx - 0.5, color='#6a3d9a', alpha=0.07, label='nhịp hồi %d nến' % x.npb)
        ex = int(x.exit_idx)
        ax.hlines(x.entry, x.idx, ex, color='#1f5fa8', lw=1.6, label='vào %.1f' % x.entry)
        ax.hlines(x.sl, x.idx, ex, color='#b23a3a', lw=1.6, ls='--', label='SL %.1f' % x.sl)
        ax.hlines(x.tp, x.idx, ex, color='#2a7a3b', lw=1.6, ls='--', label='TP %.1f (3R)' % x.tp)
        ax.plot([x.idx], [x.entry], marker='o', ms=8, color='#1f5fa8', ls='none')
        tk = list(range(a, b + 1, 10))
        ax.set_xticks(tk)
        ax.set_xticklabels([str(df['t_vn'].iloc[k])[11:16] for k in tk], fontsize=8)
        ax.set_xlim(a - 1, b + 1)
        ax.grid(alpha=0.15)
        ax.set_ylabel('giá')
        ax.set_title('%s %s — vào %s VN (%s UTC) — %s — R = %+.2f' % (
            'MUA' if x.side > 0 else 'BÁN', x.zone, str(x.t_vn)[:16], str(x.t_utc)[11:16], 'chạm TP' if x.outcome == 'TP' else 'chạm SL', x.r), fontsize=10)
        ax.legend(fontsize=8, loc='best', framealpha=0.85)
    fig.suptitle('A-v4 — phiên %s (giờ trục x = giờ VN)' % sid, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=90)
    plt.close(fig)
    return path


# =============================================================================================
# 8. BÁO CÁO
# =============================================================================================
def even_pick(g, k=5):
    if len(g) <= k:
        return g
    return g.iloc[np.unique(np.linspace(0, len(g) - 1, k).round().astype(int))]


def ex_table(g):
    L = ['| giờ VN (UTC) | chiều | vùng | E | cực trị (cách E) | nến đà | nến hồi | L | pbmax | vào | SL | TP | kết quả | R |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for x in g.itertuples():
        L.append('| %s (%s) | %s | %s | %.1f | %.1f (%.1f) | %d | %d | %.1f | %.1f | %.1f | %.1f | %.1f | %s | %+.2f |' % (
            str(x.t_vn)[:16], str(x.t_utc)[11:16], 'MUA' if x.side > 0 else 'BÁN', x.zone, x.E, x.pk_val, x.dist_pk, x.bars_mom, x.npb,
            x.L, x.pbmax, x.entry, x.sl, x.tp, x.outcome, x.r))
    return L


def main(fast=False):
    t0 = time.time()
    BV = _bv()
    P = load(with_levels=True)
    out = []
    W = out.append
    R = {}
    for k in CFG:
        fn, cands = {}, []
        ents, tr, Z = run(P, k, funnel=fn, cands=cands)
        R[k] = dict(ents=ents, tr=tr, c=closed(tr), Z=Z, fn=fn, cands=cands, s=summ(P, ents, tr))
        e2, t2, _ = run(P, k, vblock=True)
        R[k]['s_vb'] = summ(P, e2, t2)
        e3, t3, _ = run(P, k, rr=RR2)
        R[k]['s_2r'] = summ(P, e3, t3)
    g = R['goc']['s']
    assert g['n'] == EXPECT_V3[0] and abs(g['wr'] - EXPECT_V3[1]) < 1e-9 and round(g['m'], 2) == EXPECT_V3[2], g
    d = R['d']['s']
    # ---------------------------------------------------------------- 0
    W('# RESULTS-A-V4 — Setup A "Phá hồi": vùng mới + cú phá có đà + bỏ cấm 18:00–19:20')
    W('')
    W('Sinh bởi `setup_a_v4.py` (tất định, hạt cố định) theo đặc tả `plans/BENZO-A-V4-plan.md`. Dữ liệu (QĐ-6): CHỈ `fp_GCZ26_XCEC_Time_20260723-20261021_90d`, '
      'giờ UTC (VN = UTC+7). TRAIN = phiên ≤ 2026-09-15, TEST từ 2026-09-16. **%d phiên sạch** (TRAIN %d / TEST %d) — "lệnh/ngày" chia cho %d. '
      'Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ tính SL (`kernel.simulate`); 1 lệnh mở cùng lúc (A đứng riêng, KHÔNG gộp với B/C/D). '
      'TP 3R (hoà vốn sau phí ≈ 27%% WR); 2R chỉ là độ nhạy.' % (P.days, P.days_split['TRAIN'], P.days_split['TEST'], P.days))
    W('')
    W('## 0. Đăng ký trước (hằng số commit `4e76f63` TRƯỚC khi chạy lần đầu)')
    W('')
    W('- **Ba tham số tự do mới / tái dùng:** D_MIN = %.1f giá (cực trị phải cách cạnh ≥ 2 giá mới "đã trang bị" — được canh), T_HOI = %d nến tính từ CỰC TRỊ CUỐI (hết hạn), '
      'độ sâu hủy = %.1f giá (= vùng chạm, tái dùng). Giữ nguyên: vùng chạm E ± 1, ≥ 3 nến hồi, thân CF 0,5, SL = max(râu CF, mép xa ± 1) + 0,3, sàn 5 nến, trần 4 giá, TP 3R, ≤ 2 lệnh/(phiên, vùng, chiều), '
      'bỏ 3 nến sau nến dài nhất phiên, bỏ pha OFF và phiên thin/splice.' % (D_MIN, T_HOI, CANCEL_DEPTH))
    W('- **Vùng A-v4:** VWAP tuần, VWAP ngày (chỉ khi tuần/phiên ≥ 30 nến), HVN tuần ≤ 3 (gộp 3 tuần CME đã đóng; DẢI = PeakSharpness 90%% kẹp ≤ 2 giá), HVN ngày ≤ 3 (phiên đầy đủ trước; điểm), '
      'VAH/VAL ngày = VA 70%% của phiên đầy đủ TRƯỚC (cách hiểu (a) của plan; cách (b) "VA đang hình thành" chạy như độ nhạy). A-v4+ thêm VAH/VAL Âu (chốt 19:00) hoặc IB (chốt 20:20) ở pha Mỹ.')
    W('- **Đối chứng:** ĐC1 = vào ngẫu nhiên trong cùng trạng thái phá đã trang bị (chạm E, hợp lệ, bỏ nhịp hồi/CF), mỗi lệnh thật 1 nến cùng chiều + loại vùng + TRAIN/TEST, 200 lần; '
      'ĐC2 = `kernel.control_sample` (cùng vùng, cùng chế độ kernel, cùng chiều; SL râu + 0,3), 200 lần; ĐC3 = dời cả bản đồ vùng δ ~ U[3, 15] giá dấu ngẫu nhiên theo (phiên, bản), '
      '100 bản, hạt 20261024 (cùng ma trận với BENZO-VCL), chạy lại nguyên máy trạng thái.')
    W('- **Ngưỡng "khác đối chứng"** (NGUYÊN `PLAN-LAN-CHAM.md` mục 5): thật ngoài dải 5–95%% đối chứng ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở ≥ 2/3 tháng, |hiệu| > 2 sai số ở cả hai; '
      'chỉ áp dụng khi ≥ 10 lệnh ở CẢ TRAIN và TEST, nếu không ghi "không áp dụng". KTC 95%% = bootstrap 10 000 lần hạt 0 (đánh giá thấp vì lệnh cùng phiên không độc lập).')
    W('- **Tiêu chí port (plan mục 4):** T1 = n ≥ 40 · R TEST ≥ R TEST gốc và n TEST ≥ 15 · R TRAIN ≥ −0,30 · không đối chứng nào nói "thật KÉM hơn" · test xanh · khung 18:00–19:20 '
      'không tệ hơn phần còn lại quá 0,5R (n ≥ 10). T2 ("có lợi thế đo được") = TRAIN > 0 và TEST > 0, n TEST ≥ 30, vượt CẢ BA đối chứng.')
    W('- **Bảng chính KHÔNG chặn** CF trong 19:20–20:30 VN (giống A-V3 gốc của Python); bản CÓ chặn (đúng engine C#) in kèm ở 4.2.')
    W('')
    W('### Chỗ tự quyết (plan không nói rõ — chọn hướng hợp lý nhất, ghi lại)')
    W('')
    doc = sys.modules[__name__].__doc__
    for line in doc.split('CÁC CHỖ TỰ QUYẾT')[1].split('\n')[1:]:
        if line.strip():
            W(line.rstrip() if not line.strip().startswith('Q') else '- ' + line.strip())
    W('- Q10 Tên file test là `test_setup_a_v4.py` (theo yêu cầu giao việc; plan ghi `test_a_v4.py`). Không tạo `zones` trong kernel: hàm vùng mới ở `zones_a_v4.py`, kernel không đổi.')
    W('- Q11 Đối chứng luật 19:20–20:30: plan ghi "24 cửa sổ dời ±10 phút (sm 580..1200)" — không ra đúng 24 cửa sổ được; dùng MỌI cửa sổ 70 phút bắt đầu 580..1130 bước 10 phút, bỏ cửa sổ chồng lên 19:20–20:30 ⇒ %d cửa sổ.' % len(windows()))
    W('')
    # ---------------------------------------------------------------- 1
    W('## 1. Tái tạo gốc')
    W('')
    W('Máy chung `detect()` ở chế độ (band cũ, logic V3, cấm 18:00–19:20) ra **đúng từng lệnh** của `setup_a_pha_hoi.detect(expire=30)` (test `test_reproduce_v3_baseline`): '
      '**n = %d, WR %s, R TB %s** (KTC 95%% [%s; %s]); TRAIN %s · TEST %s. ⇒ khớp báo cáo cũ (n=20, WR 10%%, −0,68).' % (
          g['n'], pc(g['wr']), f(g['m']), f(g['lo']), f(g['hi']), nr(g['TRAIN']), nr(g['TEST'])))
    W('')
    # ---------------------------------------------------------------- 2
    dg = diag_v3_states(P)
    W('## 2. Chẩn đoán của Fable (plan mục 1) — chạy lại bằng script này')
    W('')
    W('Band cũ (VA Âu/IB/VA hôm qua), 61 phiên sạch; mỗi lần M5 đóng ngoài khi chưa có trạng thái = 1 trạng thái.')
    W('')
    W('| số đo | Fable ghi | chạy lại |')
    W('|---|---|---|')
    rows = [('số trạng thái phá', '532', '%d' % dg['n']),
            ('cực trị cuối sau nến phá: trung vị / p75 / p90 (nến)', '7 / 28 / 124', '%.0f / %.0f / %.0f' % (dg['pk_med'], dg['pk_p75'], dg['pk_p90'])),
            ('cực trị sau nến phá > 30 nến (bị expire=30 cắt)', '130 (24%)', '%d (%.0f%%)' % (dg['pk_gt30'], 100 * dg['pk_gt30'] / dg['n'])),
            ('khoảng cách cực trị–cạnh: trung vị / p75 (giá)', '7,1 / 16', '%.1f / %.1f' % (dg['dist_med'], dg['dist_p75'])),
            ('tỉ lệ cực trị < 2 giá', '12%', '%.0f%%' % (100 * dg['dist_lt2'])),
            ('kết thúc vì M5 đóng lại trong', '482 (91%)', '%d (%.0f%%)' % (dg['end_in'], 100 * dg['end_in'] / dg['n'])),
            ('tuổi thọ trung vị (nến)', '20', '%.0f' % dg['alive_med']),
            ('hết phiên / đảo phía', '46 / 4', '%d / %d' % (dg['end_sess'], dg['end_opp'])),
            ('có chạm lại E trước khi hủy', '92%', '%d (%.0f%%)' % (dg['touched'], 100 * dg['touched'] / dg['n'])),
            ('lần chạm đầu: trung vị nến sau nến phá', '2', '%.0f' % dg['touch_med']),
            ('chạm lại SAU cực trị cuối', '256', '%d' % dg['touch_after_peak']),
            ('chạm lần đầu > 30 nến sau nến phá', '16% số ca có chạm', '%d (%.0f%%)' % (dg['touch_gt30'], 100 * dg['touch_gt30'] / max(1, dg['touched']))),
            ('bị hủy mà chưa từng chạm E (phá hụt thật)', '15', '%d' % dg['cancel_no_touch'])]
    for a_, b_, c_ in rows:
        W('| %s | %s | %s |' % (a_, b_, c_))
    W('')
    # ---------------------------------------------------------------- 3 power
    cd = R['d']['c']
    sd = d['sd']
    W('## 3. Công suất thống kê — ĐỌC TRƯỚC bảng chính')
    W('')
    W('Hiệu nhỏ nhất phát hiện được với xác suất 80%% (mức 5%%, hai phía) ≈ 2,8 × độ lệch chuẩn R × √(1/n₁ + 1/n₂). Với A-v4: độ lệch chuẩn R = **%s**, n = %d (TRAIN %d / TEST %d).' % (
        f(sd, 2, False), d['n'], d['TRAIN']['n'], d['TEST']['n']))
    W('')
    W('| so sánh | hiệu nhỏ nhất phát hiện được |')
    W('|---|---|')
    W('| R TB A-v4 so với 0 (một mẫu, 2,8·σ/√n) | **%s R** |' % f(2.8 * sd / math.sqrt(max(d['n'], 1)), 2, False))
    W('| A-v4 so với A-V3 gốc (n = %d vs 20) | **%s R** |' % (d['n'], f(mde(sd, d['n'], 20), 2, False)))
    W('| A-v4 so với một lần rút đối chứng cùng cỡ (n vs n) | **%s R** |' % f(mde(sd, d['n'], d['n']), 2, False))
    W('| riêng TEST so với đối chứng (n TEST = %d) | **%s R** |' % (d['TEST']['n'], f(mde(sd, d['TEST']['n'], d['TEST']['n']), 2, False)))
    W('')
    W('⇒ Chênh nhỏ hơn các con số này KHÔNG thể phân biệt với may rủi trên 90 ngày.')
    W('')
    # ---------------------------------------------------------------- 4 main
    W('## 4. BẢNG CHÍNH (TP 3R, sau phí, 1 lệnh mở cùng lúc)')
    W('')
    W('R TB [KTC 95%]. "thô" = số tín hiệu trước luật 1 lệnh mở. T8 gồm 29–31/7.')
    W('')
    W('| cấu hình | Z vùng | M logic | H 18:00–19:20 | n (lệnh/ngày) | WR | R TB [KTC 95%] | kỳ vọng giá/lệnh | chuỗi thua | TRAIN n / R | TEST n / R | T8 | T9 | T10 | thô |')
    W('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    zname = {'old': 'cũ', 'new': 'mới', 'plus': 'mới+'}
    for k in CFG:
        s = R[k]['s']
        c = CFG[k]
        W('| %s | %s | %s | %s | %d (%.2f) | %s | **%s** [%s; %s] | %s | %d | %s | %s | %s | %s | %s | %d |' % (
            c['name'], zname[c['zset']], 'V3' if c['logic'] == 'v3' else 'đà', 'cấm' if c['ban'] else 'không cấm', s['n'], s['pday'], pc(s['wr']),
            f(s['m']), f(s['lo']), f(s['hi']), f(s['pts']), s['streak'], nr(s['TRAIN']), nr(s['TEST']), nr(s['T8']), nr(s['T9']), nr(s['T10']), s['raw']))
    W('')
    # 4.1 đóng góp
    W('### 4.1 Tách đóng góp (2×2×2)')
    W('')
    W('Một yếu tố đổi từ A-V3 gốc (giữ hai yếu tố kia như gốc), và hiệu TRUNG BÌNH của yếu tố đó trên cả 4 cặp ô của khối 2×2×2 (vùng cũ/mới × V3/đà × cấm/không). '
      '"phần tương tác" = (d) − gốc − tổng ba hiệu một yếu tố.')
    W('')
    cell = {(CFG[k]['zset'], CFG[k]['logic'], CFG[k]['ban']): R[k]['s'] for k in CFG if CFG[k]['zset'] != 'plus'}

    def eff(i_):
        vals = []
        for z_ in ('old', 'new'):
            for m_ in ('v3', 'mom'):
                for h_ in (True, False):
                    key = [z_, m_, h_]
                    if i_ == 0 and z_ == 'old':
                        hi_ = ('new', m_, h_)
                    elif i_ == 1 and m_ == 'v3':
                        hi_ = (z_, 'mom', h_)
                    elif i_ == 2 and h_:
                        hi_ = (z_, m_, False)
                    else:
                        continue
                    vals.append((cell[hi_], cell[tuple(key)]))
        return vals
    W('| yếu tố | Δ n (từ gốc) | Δ lệnh/ngày | Δ WR (điểm %) | Δ R TB | Δ n TB 4 cặp | Δ WR TB 4 cặp | Δ R TB TB 4 cặp |')
    W('|---|---|---|---|---|---|---|---|')
    single = {0: R['a']['s'], 1: R['b']['s'], 2: R['c']['s']}
    tot = dict(n=0, wr=0.0, m=0.0)
    for i_, lab in ((0, 'đổi vùng (cũ → 6 loại mới)'), (1, 'logic đà (V3 → đà)'), (2, 'bỏ cấm 18:00–19:20')):
        s1 = single[i_]
        pr = eff(i_)
        dn = np.mean([a_['n'] - b_['n'] for a_, b_ in pr])
        dw = np.nanmean([a_['wr'] - b_['wr'] for a_, b_ in pr])
        dm = np.nanmean([a_['m'] - b_['m'] for a_, b_ in pr])
        tot['n'] += s1['n'] - g['n']
        tot['wr'] += s1['wr'] - g['wr']
        tot['m'] += s1['m'] - g['m']
        W('| %s | %+d | %+.2f | %+.1f | %s | %+.1f | %+.1f | %s |' % (lab, s1['n'] - g['n'], (s1['n'] - g['n']) / P.days, 100 * (s1['wr'] - g['wr']),
                                                               f(s1['m'] - g['m']), dn, 100 * dw, f(dm)))
    W('| phần tương tác ((d) − gốc − tổng 3 dòng trên) | %+d | %+.2f | %+.1f | %s | | | |' % (
        d['n'] - g['n'] - tot['n'], (d['n'] - g['n'] - tot['n']) / P.days, 100 * (d['wr'] - g['wr'] - tot['wr']), f(d['m'] - g['m'] - tot['m'])))
    W('| **tổng: (d) A-v4 − gốc** | **%+d** | **%+.2f** | **%+.1f** | **%s** | | | |' % (d['n'] - g['n'], (d['n'] - g['n']) / P.days, 100 * (d['wr'] - g['wr']), f(d['m'] - g['m'])))
    W('')
    # 4.2
    W('### 4.2 Theo pha, khung giờ, phễu trạng thái, bản có chặn 19:20–20:30')
    W('')
    W('Khung 18:00–19:20 = nến M5 phá HOẶC nến CF rơi trong sm 780..859. Khung 19:20–20:30 = nến CF trong sm 860..929. Phễu: "mở" = số lần mở trạng thái PHA '
      '(logic đà: kể cả mở lại ngay sau hết hạn — xem Q9), "trang bị" = trạng thái từng đạt D_MIN, "có lệnh" = trạng thái cho ≥ 1 tín hiệu; cột sau dấu ‖ là riêng trạng thái MỞ MỚI '
      '(không phải mở lại): mở / trang bị / có lệnh — con số so được với 532 trạng thái của chẩn đoán mục 2.')
    W('')
    W('| cấu hình | Á n / R | Âu n / R | Mỹ n / R | 18:00–19:20 n · WR · R | phần còn lại R | 19:20–20:30 n · R | phễu mở / trang bị / có lệnh ‖ MỞ MỚI: mở / trang bị / có lệnh | CÓ chặn 19:20–20:30: n · WR · R | TEST |')
    W('|---|---|---|---|---|---|---|---|---|---|')
    for k in CFG:
        s, fn, sv = R[k]['s'], R[k]['fn'], R[k]['s_vb']
        W('| %s | %s | %s | %s | %d · %s · %s | %s | %d · %s | %d / %s / %d ‖ %d / %s / %d | %d · %s · %s | %s |' % (
            CFG[k]['name'], nr(s['ph_A']), nr(s['ph_EU']), nr(s['ph_US']), s['eve']['n'], pc(s['eve']['wr']), f(s['eve']['m']), f(s['not_eve']['m']),
            s['vo']['n'], f(s['vo']['m']), fn['open'], (str(fn['armed']) if CFG[k]['logic'] == 'mom' else '—'), fn['with_entry'],
            fn['open_fresh'], (str(fn['armed_fresh']) if CFG[k]['logic'] == 'mom' else '—'), fn['entry_fresh'],
            sv['n'], pc(sv['wr']), f(sv['m']), nr(sv['TEST'])))
    W('')
    W('### 4.3 Độ nhạy TP 2R (cùng tín hiệu, chỉ đổi TP — không dùng để kết luận)')
    W('')
    W('| cấu hình | n | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R |')
    W('|---|---|---|---|---|---|')
    for k in CFG:
        s = R[k]['s_2r']
        W('| %s | %d | %s | %s [%s; %s] | %s | %s |' % (CFG[k]['name'], s['n'], pc(s['wr']), f(s['m']), f(s['lo']), f(s['hi']), nr(s['TRAIN']), nr(s['TEST'])))
    W('')
    print('bang chinh xong %.0fs' % (time.time() - t0), flush=True)
    # ---------------------------------------------------------------- 5 đối chứng
    W('## 5. Đối chứng')
    W('')
    W('Mỗi ô: R TB thật · TB đối chứng [5%; 95%]. Phán quyết theo ngưỡng mục 0.')
    W('')
    W('| cấu hình | đối chứng | GỘP | TRAIN | TEST | T8 | T9 | T10 | phán quyết |')
    W('|---|---|---|---|---|---|---|---|---|')
    VER = {}
    ctl_keys = ['goc', 'a', 'b', 'c', 'd', 'plus']
    for k in ctl_keys:
        Z = R[k]['Z']
        c = R[k]['c']
        jobs = [('ĐC1 cùng trạng thái', lambda: ctrl1(P, Z, c, R[k]['cands']))]
        if k in ('d', 'plus'):
            jobs.append(('ĐC2 control_sample', lambda: (ctrl2(P, Z, c), None)))
            if not fast:
                jobs.append(('ĐC3 dời vùng 3–15 giá', lambda: ctrl3(P, k)))
        for lab, fnc in jobs:
            bands, extra = fnc()
            v, cmp = judge(c, bands)
            VER[(k, lab)] = (v, cmp, extra)
            cells = []
            for g_ in ('GỘP', 'TRAIN', 'TEST', 'T8', 'T9', 'T10'):
                x = cmp[g_]
                cells.append('%s · %s [%s; %s]' % (f(x[0]), f(x[3]), f(x[4]), f(x[5])))
            W('| %s | %s | %s | %s |' % (CFG[k]['name'], lab, ' | '.join(cells), v))
        print('doi chung %s xong %.0fs' % (k, time.time() - t0), flush=True)
    W('')
    for k in ('d', 'plus'):
        x = VER.get((k, 'ĐC3 dời vùng 3–15 giá'))
        if x:
            W('- %s, vùng DỜI 3–15 giá: số lệnh/ngày TB %s [%s; %s] (thật %.2f).' % (CFG[k]['name'], f(x[2][0], 2, False), f(x[2][1], 2, False), f(x[2][2], 2, False), R[k]['s']['pday']))
        x = VER.get((k, 'ĐC1 cùng trạng thái'))
        if x:
            W('- %s, hồ ĐC1 = %d nến.' % (CFG[k]['name'], x[2]))
    W('')
    # ---------------------------------------------------------------- 6 tách
    W('## 6. A-v4 và A-v4+ — tách mô tả (CHỈ MÔ TẢ, không lọc; nhóm n < 10 không nói gì)')
    W('')
    for k in ('d', 'plus'):
        c = R[k]['c']
        W('### %s' % CFG[k]['name'])
        W('')
        W('| nhóm | n | lệnh/ngày | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R | 18:00–19:20 n / R |')
        W('|---|---|---|---|---|---|---|---|')

        def line(lab, sub):
            s = summ(P, list(range(len(sub))), sub)
            W('| %s | %d | %.2f | %s | %s [%s; %s] | %s | %s | %s |' % (lab, s['n'], s['n'] / P.days, pc(s['wr']), f(s['m']), f(s['lo']), f(s['hi']),
                                                                    nr(s['TRAIN']), nr(s['TEST']), nr(s['eve'])))
        for zt in ZT_ORDER:
            sub = c[c['zbase'] == zt]
            if len(sub):
                line('vùng ' + zt, sub)
        line('phá lần 1 (brk_no = 1)', c[c['brk_no'] == 1])
        line('phá lần ≥ 2', c[c['brk_no'] >= 2])
        for a_, b_ in DIST_BINS:
            line('cực trị cách E %s–%s giá' % (f(a_, 0, False), ('∞' if b_ > 1e8 else f(b_, 0, False))), c[(c['dist_pk'] >= a_) & (c['dist_pk'] < b_)])
        line('cực trị cách E < 2 giá (cạnh động trôi lại gần, Q5)', c[c['dist_pk'] < 2.0])
        line('trạng thái mở MỚI', c[~c['reopen']])
        line('trạng thái MỞ LẠI sau hết hạn (Q9)', c[c['reopen']])
        line('lệnh thứ 1 của trạng thái', c[c['ent_no'] == 1])
        line('lệnh thứ ≥ 2 của trạng thái', c[c['ent_no'] >= 2])
        line('nến đà (cực trị − nến phá) > 30', c[c['bars_mom'] > 30])
        W('')
    # ---------------------------------------------------------------- 7 rủi ro
    W('## 7. Các rủi ro plan mục 5 — số kiểm')
    W('')
    for k in ('d', 'plus'):
        fn, ents, c, Z = R[k]['fn'], R[k]['ents'], R[k]['c'], R[k]['Z']
        ob = fn['open_by']
        vw_open = (ob.get('VWAP_W', 0) + ob.get('VWAP_D', 0)) / max(1, fn['open'])
        vw_tr = float(c['zbase'].isin(['VWAP_W', 'VWAP_D']).mean()) if len(c) else np.nan
        # vùng trùng ±1 giá tại nến vào
        ov = 0
        for e in ents:
            i = e['idx']
            for z in Z:
                if z['name'] == e['zone']:
                    continue
                for v in (z['lo'][i], z['hi'][i]):
                    if v == v and abs(v - e['E']) <= 1.0:
                        ov += 1
                        break
                else:
                    continue
                break
        pl = c['pbmax'] / c['L'] if len(c) else pd.Series(dtype=float)
        W('- **%s:** VWAP chiếm **%.0f%%** số lần mở trạng thái và **%s** số lệnh (plan cảnh báo nếu > 70%% trạng thái nhưng < 30%% lệnh). '
          'Tín hiệu thô %d → %d lệnh sau luật 1 lệnh mở (chặn **%.0f%%**). Lệnh có vùng KHÁC trong ±1 giá quanh E: **%d/%d (%.0f%%)**. '
          'Hai vùng hợp lệ cùng nến (chọn gần hơn): %d lần. Mở chiều ngược bị chặn vì chiều kia còn sống (Q2): %d lần. '
          'Lệnh vào khi cực trị đã KHÔNG còn cách E(i) ≥ D_MIN (cạnh động trôi, Q5): %d. pbmax/L của lệnh vào: trung vị %.2f, p90 %.2f, max %.2f. '
          'Tín hiệu bị trần SL 4 giá loại: %d.' % (
              CFG[k]['name'], 100 * vw_open, pc(vw_tr), len(ents), d['n'] if k == 'd' else R[k]['s']['n'],
              100 * (1 - (R[k]['s']['n'] + R[k]['s']['n_open']) / max(1, len(ents))), ov, len(ents), 100 * ov / max(1, len(ents)),
              fn['conflict'], fn['blocked_opp'], fn['armed_drift'], pl.median(), pl.quantile(0.9), pl.max(), fn['no_risk']))
        W('  Mở trạng thái theo loại vùng: %s. Trang bị: %s. Có lệnh: %s.' % (
            ', '.join('%s %d' % (z, ob[z]) for z in ZT_ORDER if z in ob), ', '.join('%s %d' % (z, fn['armed_by'][z]) for z in ZT_ORDER if z in fn['armed_by']),
            ', '.join('%s %d' % (z, fn['entry_by'][z]) for z in ZT_ORDER if z in fn['entry_by'])))
    # HVN tuần
    st = P.st
    clean = [int(s_) for s_ in st.index if not (st.loc[s_, 'splice'] or st.loc[s_, 'thin']) and st.loc[s_, 'n'] >= K.CONST['min_bars_prof']]
    part = sum(1 for s_ in clean if P.slev[s_]['hvn_w_partial'])
    nohw = sum(1 for s_ in clean if not P.slev[s_]['hvn_w'])
    dist = []
    for s_ in clean:
        hw = P.slev[s_]['hvn_w']
        if hw:
            c0 = P.cl[int(st.loc[s_, 'start_pos'])]
            dist.append(min(abs(c0 - x[0]) for x in hw))
    widths = [x[2] - x[1] for s_ in clean for x in P.slev[s_]['hvn_w']]
    raw_w = [x[4] - x[3] for s_ in clean for x in P.slev[s_]['hvn_w']]
    W('- **HVN tuần:** %d/%d phiên sạch có HVN tuần dựng trên cửa sổ `partial` (thiếu tuần do đầu file); %d phiên không có HVN tuần nào qua cổng ×2,5. '
      'Khoảng cách giá mở phiên → HVN tuần gần nhất: trung vị **%.1f giá**, p75 %.1f, p90 %.1f. Bề rộng dải PeakSharpness trước kẹp: trung vị %.1f giá, max %.1f; sau kẹp ≤ 2: trung vị %.1f.' % (
          part, len(clean), nohw, np.median(dist), np.quantile(dist, .75), np.quantile(dist, .9), np.median(raw_w), max(raw_w), np.median(widths)))
    cv = R['d']['c']
    two = cv[cv['zbase'] == 'VWAP_D'].groupby('session_id')['E'].agg(['count', 'min', 'max'])
    two = two[two['count'] >= 2]
    W('- **Hai lệnh/vùng/phiên với vùng động (VWAP_D, (d)):** %d phiên có 2 lệnh VWAP_D; chênh E giữa hai lệnh: %s giá.' % (
        len(two), ', '.join('%.1f' % (r_['max'] - r_['min']) for _, r_ in two.iterrows()) or '—'))
    W('- A mô phỏng đứng riêng; khi gộp 4 setup với 1 lệnh mở chung thì số lệnh thực tế THẤP hơn (chưa chạy ở đây).')
    W('')
    print('tach + rui ro xong %.0fs' % (time.time() - t0), flush=True)
    # ---------------------------------------------------------------- 8 độ nhạy
    W('## 8. Độ nhạy quanh (d) A-v4 — đổi MỘT thứ một lần, IN RA, KHÔNG chọn lại')
    W('')
    W('| biến thể | n | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R |')
    W('|---|---|---|---|---|---|')

    def srow(lab, s):
        W('| %s | %d | %s | %s [%s; %s] | %s | %s |' % (lab, s['n'], pc(s['wr']), f(s['m']), f(s['lo']), f(s['hi']), nr(s['TRAIN']), nr(s['TEST'])))
    srow('**(d) ô chính** (D_MIN 2, T_HOI 30, hủy 1,0)', d)
    for nm, v in SENS:
        kw = {'d_min': v} if nm == 'D_MIN' else ({'t_hoi': v} if nm == 'T_HOI' else {'cancel': v})
        e_, t_, _ = run(P, 'd', **kw)
        srow('%s = %s' % (nm, v), summ(P, e_, t_))
    e_, t_, _ = run(P, 'd', zkw=dict(hvn_w_band=False))
    srow('HVN tuần là ĐIỂM (không dải)', summ(P, e_, t_))
    e_, t_, _ = run(P, 'd', zkw=dict(va_dev=True))
    sv_ = summ(P, e_, t_)
    srow('VA ngày ĐANG HÌNH THÀNH thay VA hôm qua (cách hiểu (b))', sv_)
    cvd = closed(t_)
    sub = cvd[cvd['zbase'].isin(['VAH_DEV', 'VAL_DEV'])]
    srow('— riêng lệnh ở VAH/VAL đang hình thành', summ(P, list(range(len(sub))), sub))
    e_, t_, _ = run(P, 'd', after_inside=True)
    srow('mở lại sau hết hạn CHỈ khi M5 đã về trong (Q9)', summ(P, e_, t_))
    srow('CÓ chặn 19:20–20:30 (đúng engine C#)', R['d']['s_vb'])
    srow('TP 2R', R['d']['s_2r'])
    W('')
    print('do nhay xong %.0fs' % (time.time() - t0), flush=True)
    # ---------------------------------------------------------------- 9 luật 19:20–20:30
    W('## 9. Luật cứng engine 19:20–20:30 VN — chỉ báo (KHÔNG đổi engine)')
    W('')
    W('Hiệu R TB (lệnh có CF trong 19:20–20:30) − (ngoài) so với cùng hiệu của %d cửa sổ 70 phút khác (bắt đầu sm 580..1130, bước 10\', không chồng khung). '
      'File 90d toàn mùa hè Mỹ ⇒ nhánh mùa đông (20:20–21:30 VN) CHƯA kiểm.' % len(windows()))
    W('')
    W('| setup | n trong khung | WR · R trong | WR · R ngoài | hiệu | dải 5–95% các cửa sổ khác | phán |')
    W('|---|---|---|---|---|---|---|')
    sets = [('A-v4 (d), không chặn', R['d']['c']), ('A-V3 gốc', R['goc']['c'])]
    for nm, t_ in other_setups(P).items():
        sets.append((nm, t_))
    for nm, c in sets:
        smc = P.sm[c['idx'].to_numpy()]
        x = window_test(c, smc)
        W('| %s | %d | %s · %s | %s · %s | %s | [%s; %s] | %s |' % (nm, x['n_in'], pc(x['wr_in']), f(x['r_in']), pc(x['wr_out']), f(x['r_out']), f(x['diff']),
                                                             f(x['q5']), f(x['q95']), x['v']))
    W('')
    # ---------------------------------------------------------------- 10 ví dụ
    W('## 10. Ví dụ để soi chart (giờ VN, kèm giờ UTC)')
    W('')
    c = R['d']['c']
    W('"nến đà" = vị trí cực trị cuối − nến M5 phá; âm/0 = cực trị nằm trong chân cú phá (trước/đúng nến phá). Với lệnh thứ 2 của một trạng thái, cực trị được đặt lại ở nến vào lệnh 1.')
    W('')
    W('### 10.1 (d) A-v4 — 5 lệnh THẮNG (cách đều theo thời gian)')
    W('')
    out += ex_table(even_pick(c[c['r'] > 0]))
    W('')
    W('### 10.2 (d) A-v4 — 5 lệnh THUA')
    W('')
    out += ex_table(even_pick(c[c['r'] <= 0]))
    W('')
    W('### 10.3 "V3 bỏ sót mà A-v4 bắt" — lệnh (d) có cực trị > 30 nến sau nến phá (V3 hết hạn 30 nến tính từ nến phá ⇒ không thể vào)')
    W('')
    out += ex_table(even_pick(c[c['bars_mom'] > 30]))
    W('')
    W('### 10.4 "V3 vào mà A-v4 từ chối" — lệnh A-V3 gốc không có trong (b) (cùng vùng cũ, cùng cấm giờ, chỉ đổi logic) và lý do theo trạng thái của logic đà tại nến đó')
    W('')
    bidx = set(int(x) for x in R['b']['c']['idx'])
    miss = R['goc']['c'][~R['goc']['c']['idx'].isin(bidx)]
    tr_ = {int(i): None for i in miss['idx']}
    detect(P, P.zones('old'), logic='mom', ban=True, trace=tr_)
    W('| giờ VN | chiều | E | kết quả V3 | R V3 | lý do A-v4 không vào |')
    W('|---|---|---|---|---|---|')
    braw = R['b']['ents']
    braw_idx = set(e['idx'] for e in braw)
    for x in even_pick(miss).itertuples():
        snap = [y for y in (tr_.get(int(x.idx)) or []) if y['S'] == x.side]
        prev = [e for e in braw if e['idx'] < x.idx and P.sno[e['idx']] == P.sno[x.idx] and e['side'] == x.side and round(e['E'], 1) == round(x.E, 1)]
        if int(x.idx) in braw_idx:
            why = 'A-v4 CŨNG ra tín hiệu ở nến này, nhưng đang có lệnh khác của chính nó mở (luật 1 lệnh mở)'
        elif snap and len(prev) >= 2:
            why = 'đã đủ 2 lệnh ở cạnh này trong phiên (A-v4 vào sớm hơn lúc %s)' % ', '.join(str(P.df['t_vn'].iloc[e['idx']])[11:16] for e in prev)
        elif not snap:
            why = 'không có trạng thái phá còn sống (đã hủy vì M5 đóng sâu > 1 giá, hết hạn T_HOI, hoặc chưa mở)'
        else:
            y = snap[0]
            ws = []
            if not y['armed']:
                ws.append('CHƯA trang bị (cực trị chỉ cách E %.1f giá < 2)' % (x.side * (y['pk_val'] - y['E'])))
            if y['age'] > T_HOI:
                ws.append('hồi quá T_HOI (%d nến từ cực trị)' % y['age'])
            if not (y['pbmax'] < y['L']):
                ws.append('nến hồi dài ≥ L (pbmax %.1f ≥ L %.1f)' % (y['pbmax'], y['L']))
            if x.idx - 1 - y['pk_pos'] < N_MIN:
                ws.append('hồi < 3 nến (cực trị ở nến %d trước)' % (x.idx - y['pk_pos']))
            why = '; '.join(ws) or 'khác (ưu tiên vùng / đếm 2 lệnh)'
        W('| %s | %s | %.1f | %s | %+.2f | %s |' % (str(x.t_vn)[:16], 'MUA' if x.side > 0 else 'BÁN', x.E, x.outcome, x.r, why))
    W('')
    # ảnh
    os.makedirs(IMG, exist_ok=True)
    imgs = []
    wins = c[c['outcome'] == 'TP']
    loss = c[c['outcome'] == 'SL']
    picks = []
    if len(wins):
        picks.append(wins.iloc[len(wins) // 2]['session_id'])
    if len(loss):
        sid = loss.iloc[len(loss) // 2]['session_id']
        if sid in picks and len(loss) > 1:
            sid = loss.iloc[len(loss) // 2 + 1]['session_id']
        picks.append(sid)
    for sid in picks:
        pth = os.path.join(IMG, 'a_v4_%s.png' % sid)
        if plot_session(P, R['d']['Z'], R['d']['c'], sid, pth):
            imgs.append(pth)
    W('### 10.5 Ảnh minh hoạ')
    W('')
    for pth in imgs:
        W('- [%s](img/%s): vạch cam = cạnh E (VWAP thì là đường cong), dải cam = dải HVN tuần, tam giác tím = cực trị cuối, vùng tím nhạt = nhịp hồi, '
          'xanh dương = vào, đỏ đứt = SL, xanh lá đứt = TP; vạch chấm xám = nến M5 phá đóng.' % (os.path.basename(pth), os.path.basename(pth)))
    W('')
    # ---------------------------------------------------------------- 11 T1/T2
    W('## 11. Tiêu chí port (đăng ký trước, plan mục 4) — chấm tự động')
    W('')
    vers = {lab: VER[('d', lab)][0] for lab in ('ĐC1 cùng trạng thái', 'ĐC2 control_sample', 'ĐC3 dời vùng 3–15 giá') if ('d', lab) in VER}
    worse = [lab for lab, v in vers.items() if v.startswith('KHÁC đối chứng ▼')]
    eve_bad = d['eve']['n'] >= MIN_N and (d['eve']['m'] - d['not_eve']['m']) < -T1_EVE_GAP
    import subprocess
    tp = subprocess.run([sys.executable, '-m', 'pytest', os.path.join(HERE, 'test_setup_a_v4.py'), '-q'], capture_output=True, text=True, cwd=HERE)
    tests_ok = tp.returncode == 0
    t1 = [('(1) n ≥ %d' % T1_N, d['n'] >= T1_N, 'n = %d' % d['n']),
          ('(2) R TEST ≥ R TEST gốc (%s, n=%d) và n TEST ≥ %d' % (f(g['TEST']['m']), g['TEST']['n'], T1_N_TEST),
           (d['TEST']['m'] >= g['TEST']['m']) and d['TEST']['n'] >= T1_N_TEST, 'R TEST = %s, n TEST = %d' % (f(d['TEST']['m']), d['TEST']['n'])),
          ('(3) R TRAIN ≥ %.2f' % T1_TRAIN_MIN, d['TRAIN']['m'] >= T1_TRAIN_MIN, 'R TRAIN = %s' % f(d['TRAIN']['m'])),
          ('(4) không đối chứng nào "thật KÉM hơn"', not worse, '; '.join('%s: %s' % kv for kv in vers.items())),
          ('(5) test 3.6 xanh', tests_ok, tp.stdout.strip().splitlines()[-1] if tp.stdout.strip() else tp.stderr[-200:]),
          ('(6) 18:00–19:20 không tệ hơn phần còn lại > 0,5R (n ≥ 10)', not eve_bad,
           'n = %d, R %s vs phần còn lại %s' % (d['eve']['n'], f(d['eve']['m']), f(d['not_eve']['m'])))]
    W('| điều kiện T1 | đạt? | số |')
    W('|---|---|---|')
    for lab, ok, txt in t1:
        W('| %s | %s | %s |' % (lab, 'ĐẠT' if ok else '**KHÔNG**', txt))
    T1 = all(ok for _, ok, _ in t1)
    better = [lab for lab, v in vers.items() if v.startswith('KHÁC đối chứng ▲')]
    T2 = d['TRAIN']['m'] > 0 and d['TEST']['m'] > 0 and d['TEST']['n'] >= T2_N_TEST and len(better) == 3
    W('')
    W('- **T1: %s.** **T2: %s** (TRAIN %s, TEST %s, n TEST %d, vượt đối chứng: %d/3).' % (
        'ĐẠT' if T1 else 'KHÔNG ĐẠT', 'ĐẠT' if T2 else 'KHÔNG ĐẠT', f(d['TRAIN']['m']), f(d['TEST']['m']), d['TEST']['n'], len(better)))
    W('')
    ev = os.path.join(REPORT, '_eval_a_v4.txt')
    if os.path.exists(ev):
        W('## 12. Đánh giá (viết tay sau khi đọc số — `report/_eval_a_v4.txt`)')
        W('')
        with open(ev, encoding='utf-8') as fh:
            W(fh.read())
    W('')
    W('_Thời gian chạy toàn bộ: %.0f giây._' % (time.time() - t0))
    with open(os.path.join(REPORT, 'RESULTS-A-V4.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out) + '\n')
    print('ghi report/RESULTS-A-V4.md (%.0fs); T1=%s T2=%s' % (time.time() - t0, T1, T2))
    return R, T1, T2


if __name__ == '__main__':
    main(fast='--fast' in sys.argv)
