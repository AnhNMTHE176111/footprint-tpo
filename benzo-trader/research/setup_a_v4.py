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
              'armed_drift', 'conflict', 'blocked_reopen'):
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
                entries.append(dict(idx=i, side=S, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='A', zone=NAME[zi],
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


if __name__ == '__main__' and '--engine-only' in sys.argv:
    P = load()
    e = detect(P, P.zones('old'), logic='v3', ban=True)
    print(len(e))
