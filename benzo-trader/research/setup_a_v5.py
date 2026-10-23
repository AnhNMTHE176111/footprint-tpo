# -*- coding: utf-8 -*-
"""SETUP A-v5 "Phá hồi" = A-v4 (giữ nguyên) + tập vùng hỗ trợ/kháng cự của Vùng Canh Lệnh (VCL v5).
Đặc tả: `plans/BENZO-A-V5-plan.md` (Opus). Chỉ IMPORT setup_a_v4 / zones_a_v4 / kernel / benzo_vcl — KHÔNG sửa.

Chạy:  python3 setup_a_v5.py          → report/RESULTS-A-V5.md + report/_eval_a_v5.txt + report/img/a_v5_*.png
Test:  python3 -m pytest test_setup_a_v5.py -q

`detect5` = bản COPY của `setup_a_v4.detect` + đúng 4 thứ (plan 2.9): vùng thưa VCL, luật CÚ PHÁ THẬT (2.4), lý do `roi_bo` (2.5),
khoá mức giá (2.7, cùng nhãn "trùng"). Khi `vcl=None` nó phải ra ĐÚNG từng lệnh của `setup_a_v4.detect` (test).

Thuật ngữ: VCL = Vùng Canh Lệnh · eid = mã vùng ổn định · bộ hiển thị = các vùng VCL đang vẽ tại nến i · cú phá thật = trong chân cú phá
có một nến M1 mà vùng đang hiển thị và giá đóng ở phía trong · rời bộ (roi_bo) = eid không còn trong bộ hiển thị · khoá mức = chống đếm
trùng một mức giá · đối chứng (ĐC) = cách vào lệnh "bừa" để so · công suất thống kê = chênh nhỏ nhất đo ra được.

CÁC CHỖ TỰ QUYẾT CỦA SONNET (plan không nói rõ) — in lại ở RESULTS-A-V5.md mục "Chỗ tự quyết":
  V1 Luật cú phá thật khi vòng lùi dừng vì chạm giới hạn `lim` (k == lim): vẫn kiểm nến k — nếu tại k vùng có giá trị và giá đóng phía trong
     thì MỞ (chân cú phá có nến trong đúng ở nến giới hạn); nếu giá vẫn ngoài thì trượt, ghi `het60` (lim = i − 60 > đầu phiên)
     hoặc `dau_phien` (đầu phiên a ≥ i − 60).
  V2 "Số lần M5 đóng ngoài vùng VCL" của phễu = số lần ĐẾN bước thử mở trạng thái (M5 đóng ngoài, chưa có trạng thái cùng chiều,
     không bị chặn vì chiều kia còn sống). Số M5 đóng ngoài kể cả khi đã có trạng thái in riêng (`m5_ngoai_tat_ca`).
  V3 Thứ tự trong khâu ứng viên của VCL: chạm vùng → hồi/CF → trần 2 lệnh theo mã vùng → trần SL 4 giá → khoá mức (và S5: bỏ trùng) →
     tranh cùng nến. Khoá mức đếm chỉ các tín hiệu ĐÃ GHI (thắng tranh cùng nến), cùng (phiên, chiều), |E cũ − E| ≤ ZONE_HALF.
  V4 `roi_bo` có eid mới chồng: eid MỚI có nến đầu trong [L+1, L+5] (L = nến cuối của eid cũ) và dải giao dải CUỐI của eid cũ (lo' < hi_cũ và hi' > lo_cũ).
  V5 Nhãn "trùng" tính ở nến VÀO lệnh (nến của tín hiệu) với dải v4 tại chính nến đó (đã dời nếu ĐC3).
  V6 Phép so 'lệnh VCL so lệnh v4 trong A-v5' (mục 3.1 và T1-(8)) dùng độ lệch chuẩn R của MỌI lệnh A-v5 và n của hai nhóm ở đúng tập đang xét
     (TRAIN / TEST); hiệu nhỏ nhất phát hiện được = 2,8 · σ · √(1/n_VCL + 1/n_v4).
  V7 Bảng chính và mọi lệnh dùng chế độ 1 lệnh mở CHUNG cho v4 + VCL (A đứng riêng, không gộp với B/C/D) — như v4.
  V8 ĐC2 cho A-v5 toàn bộ: lệnh vùng v4 dùng cột vùng như v4; lệnh VCL dùng 2 cột chung (MUA = hi, BÁN = lo của vùng VCL trong bộ có
     cạnh gần giá đóng nhất tại từng nến).
"""
from __future__ import annotations

import math
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import setup_a_v4 as A4  # noqa: E402
import zones_a_v4 as ZA  # noqa: E402
import zones_a_v5 as ZV  # noqa: E402

ROOT = A4.ROOT
REPORT = A4.REPORT
IMG = A4.IMG

# =============================== HẰNG SỐ — TOÀN BỘ TÁI DÙNG TỪ v4 (tham số tự do mới = 0) ===============================
RR, RR2 = A4.RR, A4.RR2
ZONE_HALF, N_MIN, BODY, LEG_LOOKBACK = A4.ZONE_HALF, A4.N_MIN, A4.BODY, A4.LEG_LOOKBACK
D_MIN, T_HOI, CANCEL_DEPTH = A4.D_MIN, A4.T_HOI, A4.CANCEL_DEPTH
EXPIRE_V3 = A4.EXPIRE_V3
SM_NOPHA, SM_VOPEN = A4.SM_NOPHA, A4.SM_VOPEN
VCL_RANK = 7                  # thấp nhất, sau mọi loại v4 (plan 2.3)
MAIN_VBLOCK = False
REPS, CTRL_DRAWS, MIN_N = A4.REPS, A4.CTRL_DRAWS, A4.MIN_N
GROUPS = A4.GROUPS
CLOSED = A4.CLOSED
# --- tiêu chí port (plan mục 4), đăng ký trước
T1_N = 40
T1_TEST_REF = -0.08
T1_N_TEST = 15
T1_TRAIN_MIN = -0.30
T1_EVE_GAP = 0.5
T1_VCL_NET = 31               # VCL thêm ròng >= +0,5 lệnh/ngày ⇒ >= 31 lệnh trên 61 phiên
T2_N_TEST = 30
EXPECT_V4 = (218, 0.197, -0.30)
EXPECT_OLD = (20, 0.100, -0.68)
ROI_OVERLAP_BARS = 5
V4_TYPES = ('VWAP_W', 'VWAP_D', 'HVN_W', 'HVN_D', 'VAH_D', 'VAL_D')


# =============================================================================================
# 1. DỮ LIỆU
# =============================================================================================
def load5(with_levels=True):
    """(P, V): Prep của v4 + VclSet (đã kiểm khớp chuỗi nến, plan 2.2)."""
    P = A4.load(with_levels=with_levels)
    rec = ZV.load_rec_checked(P)
    return P, ZV.VclSet(rec, len(P.df))


class St(A4.St):
    __slots__ = ('kpos',)


# =============================================================================================
# 2. MÁY TRẠNG THÁI — copy của setup_a_v4.detect + 4 thứ của plan 2.9
# =============================================================================================
def detect5(P, Z, vcl=None, logic='mom', ban=False, vblock=False, d_min=D_MIN, t_hoi=T_HOI, cancel=CANCEL_DEPTH, n_min=N_MIN,
            rr=RR, expire=EXPIRE_V3, shift=None, vshift=None, cands=None, funnel=None, vfunnel=None, trace=None, states_log=None,
            after_inside=False, real_break=True, vcl_slfar=True, lock=True, drop_overlap=False, vlog=None, only=None, dense=False):
    """Như setup_a_v4.detect (xem docstring đó) cộng:
    vcl (zones_a_v5.VclSet | None) = bộ vùng VCL; None ⇒ chạy y hệt v4.  shift = δ theo phiên cho vùng v4, vshift = δ theo phiên cho VCL (ĐC3).
    funnel = phễu của vùng v4 (khoá như v4), vfunnel = phễu của vùng VCL, vlog (dict) = ghi lẻ cho báo cáo (độ rộng bị trần SL loại, roi_bo…).
    real_break=False: bỏ luật cú phá thật (độ nhạy S1).  vcl_slfar=False: SL của VCL qua cạnh gần E ∓ 1 (S2).  lock=False: bỏ khoá mức (S3).
    drop_overlap=True: bỏ hẳn tín hiệu VCL 'trùng' vùng v4 trước luật 1 lệnh mở (S5).
    only = tập session_no cần chạy (None = tất cả; chỉ để test).  dense=True = vòng lặp ĐẦY ĐỦ mọi eid ở mỗi sự kiện M5 (chỉ để test
    chứng minh vòng thưa tương đương vòng dày; chậm)."""
    mom = logic == 'mom'
    if vcl is not None and not mom:
        raise ValueError('VCL chi chay voi logic mom')
    cl, hi, lo, rng, sm, ph = P.cl, P.hi, P.lo, P.rng, P.sm, P.phase
    bad, cf, sbig, m5c = P.bad, P.cf, P.sbig, P.m5c
    df = P.df
    nz = len(Z)                      # số vùng v4; VCL: zi = nz + thứ tự eid
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
    vv = None
    if vcl is not None:
        vv = vcl.view(None if vshift is None else vshift[P.sno])
        v_lo, v_hi, v_off, v_b0, v_ln = vv.lo, vv.hi, vv.off, vv.b0, vv.ln

    def lo_at(zi, i):
        if zi < nz:
            return LO[zi][i]
        e = zi - nz
        j = i - v_b0[e]
        return v_lo[v_off[e] + j] if 0 <= j < v_ln[e] else math.nan

    def hi_at(zi, i):
        if zi < nz:
            return HI[zi][i]
        e = zi - nz
        j = i - v_b0[e]
        return v_hi[v_off[e] + j] if 0 <= j < v_ln[e] else math.nan

    def name_of(zi):
        return NAME[zi] if zi < nz else 'VCL_%d' % int(vv.eid_of[zi - nz])

    def ztype_of(zi):
        return ZT[zi] if zi < nz else 'VCL'

    fn = funnel if funnel is not None else {}
    vf = vfunnel if vfunnel is not None else {}
    for D_ in (fn, vf):
        for k in ('open', 'open_fresh', 'armed', 'with_entry', 'cancel', 'expire', 'end', 'blocked_opp', 'reset_value', 'no_risk',
                  'armed_drift', 'conflict', 'blocked_reopen', 'armed_fresh', 'entry_fresh'):
            D_.setdefault(k, 0)
        D_.setdefault('open_by', {})
        D_.setdefault('armed_by', {})
        D_.setdefault('entry_by', {})
    for k in ('m5_ngoai_thu', 'm5_ngoai_tat_ca', 'khong_pha_that', 'kpt_vang', 'kpt_het60', 'kpt_dau_phien', 'cancel_sau', 'cancel_doi',
              'roi_bo', 'roi_bo_armed', 'cf_ok', 'khoa_muc', 'thua_tranh', 'chon', 's5_bo_trung', 'open_reopen'):
        vf.setdefault(k, 0)
    if vlog is None:
        vlog = {}
    vlog.setdefault('norisk', [])        # (uid, độ rộng vùng) mỗi lần tín hiệu VCL bị trần SL loại
    vlog.setdefault('roi_bo', [])        # (eid, armed, nến M5)
    entries = []
    count = {}
    bcount = {}
    sig_log = {}                         # (phiên, chiều) -> list E của các tín hiệu ĐÃ GHI (khoá mức)
    uid = [0]

    def F(zi):
        return fn if zi < nz else vf

    def lab_of(zi, i):
        return LAB[zi][i] if (zi < nz and LAB[zi] is not None) else name_of(zi)

    def finish(stt, why):
        zi = stt.zi
        D_ = F(zi)
        D_[why] = D_.get(why, 0) + 1
        if not stt.reopen:
            D_['armed_fresh'] += int(stt.was_armed)
            D_['entry_fresh'] += int(stt.n_ent > 0)
        zt = ztype_of(zi)
        if stt.was_armed:
            D_['armed'] += 1
            D_['armed_by'][zt] = D_['armed_by'].get(zt, 0) + 1
        if stt.n_ent:
            D_['with_entry'] += 1
            D_['entry_by'][zt] = D_['entry_by'].get(zt, 0) + 1
        if states_log is not None:
            states_log.append(dict(zi=zi, ztype=zt, S=stt.S, p0=stt.p0, pk_pos=stt.pk_pos, pk_val=stt.pk_val, E=stt.E,
                                   why=why, armed=stt.was_armed, n_ent=stt.n_ent, brk_no=stt.brk_no, reopen=stt.reopen))

    def open_state(zi, out, i, a, s):
        lo_v, hi_v = lo_at(zi, i), hi_at(zi, i)
        canh = hi_v if out > 0 else lo_v
        k = i
        lim = max(a, i - LEG_LOOKBACK)
        if zi >= nz:
            # ---- VCL: vòng lùi tìm chân cú phá trên vùng ĐANG HIỂN THỊ (NaN ⇒ dừng = "vùng vắng")
            e = zi - nz
            b0e, lne, offe = v_b0[e], v_ln[e], v_off[e]
            arr = v_hi if out > 0 else v_lo
            while k > lim:
                j = k - b0e
                if not (0 <= j < lne):
                    break
                rv = arr[offe + j]
                if (cl[k] > rv) if out > 0 else (cl[k] < rv):
                    k -= 1
                else:
                    break
            if real_break:                                  # luật 2.4 — kiểm TRƯỚC khi đụng bất kỳ biến trạng thái nào
                j = k - b0e
                if not (0 <= j < lne):
                    why = 'kpt_vang'
                else:
                    inside = (cl[k] <= v_hi[offe + j]) if out > 0 else (cl[k] >= v_lo[offe + j])
                    if inside:
                        why = None
                    else:
                        why = 'kpt_dau_phien' if (lim == a and a > i - LEG_LOOKBACK) else 'kpt_het60'
                if why is not None:
                    vf['khong_pha_that'] += 1
                    vf[why] += 1
                    return None
        elif DYN[zi]:
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
        stt.kpos = int(k)
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
        D_ = F(zi)
        D_['open'] += 1
        if not stt.reopen:
            D_['open_fresh'] += 1
        elif zi >= nz:
            vf['open_reopen'] += 1
        zt = ztype_of(zi)
        D_['open_by'][zt] = D_['open_by'].get(zt, 0) + 1
        return stt

    for s, a, b in P.sessions:
        if only is not None and s not in only:
            continue
        states = {}
        need_in = {}
        for i in range(a, b + 1):
            # ---------------- sự kiện M5 (Q1: trước khi quét nến i)
            if m5c[i]:
                C = cl[i]
                if vv is not None:
                    pa, pb = vv.bptr[i], vv.bptr[i + 1]
                    act = {nz + int(e_): (l_, h_) for e_, l_, h_ in zip(vv.B_eord[pa:pb], vv.B_lo[pa:pb], vv.B_hi[pa:pb])}
                    if dense:
                        zl = list(range(nz + vv.ne))
                    else:
                        zl = list(range(nz)) + sorted(set(act) | {kk[0] for kk in states if kk[0] >= nz})
                else:
                    act = {}
                    zl = range(nz)
                for zi in zl:
                    if zi < nz:
                        lo_v, hi_v = LO[zi][i], HI[zi][i]
                    else:
                        lh = act.get(zi)
                        lo_v, hi_v = lh if lh is not None else (math.nan, math.nan)
                    if lo_v != lo_v:
                        for S in (1, -1):
                            x = states.pop((zi, S), None)
                            if x is not None:
                                if zi < nz:
                                    finish(x, 'reset_value')
                                else:
                                    vf['roi_bo_armed'] += int(x.armed)    # (đếm roi_bo do finish())
                                    vlog['roi_bo'].append((int(vv.eid_of[zi - nz]), bool(x.armed), int(i)))
                                    finish(x, 'roi_bo')
                        continue
                    if zi < nz and not DYN[zi]:
                        lb = lab_of(zi, i)
                        for S in (1, -1):
                            x = states.get((zi, S))
                            if x is not None and (x.zlo != lo_v or x.zhi != hi_v or x.lab != lb):
                                finish(states.pop((zi, S)), 'reset_value')
                    isv = zi >= nz
                    dyn_z = True if isv else DYN[zi]
                    band_z = True if isv else BAND[zi]
                    out = 1 if C > hi_v else (-1 if C < lo_v else 0)
                    if isv and out != 0:
                        vf['m5_ngoai_tat_ca'] += 1
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
                            canh = (hi_v if S > 0 else lo_v) if dyn_z else x.E
                            deep = S * (C - canh) < -cancel
                            opp = band_z and out == -S
                            if deep or opp:
                                if isv:        # 'đối diện' (M5 đóng ngoài mép xa) ưu tiên; còn lại là hủy sâu (đóng trong > cancel qua cạnh)
                                    vf['cancel_doi' if opp else 'cancel_sau'] += 1
                                finish(states.pop((zi, S)), 'cancel')
                        if out != 0:
                            if (zi, out) in states:
                                continue
                            if (zi, -out) in states:
                                F(zi)['blocked_opp'] += 1
                                continue
                            if ban and SM_NOPHA[0] <= sm[i] < SM_NOPHA[1]:
                                continue
                            if after_inside and need_in.get((zi, out)):
                                F(zi)['blocked_reopen'] += 1
                                continue
                            if isv:
                                vf['m5_ngoai_thu'] += 1
                            stt_new = open_state(zi, out, i, a, s)
                            if stt_new is not None:
                                states[(zi, out)] = stt_new
            if not states:
                continue
            # ---------------- quét nến i
            okbar = (not bad[i]) and ph[i] != 'OFF' and not (1 <= sbig[i] <= 3)
            if vblock and SM_VOPEN[0] <= sm[i] < SM_VOPEN[1]:
                okbar = False
            ci = cl[i]
            if trace is not None and i in trace:
                trace[i] = [dict(zone=name_of(x.zi), S=x.S, p0=x.p0, pk_pos=x.pk_pos, pk_val=x.pk_val, L=x.L, pbmax=x.pbmax,
                                 armed=x.armed, E=((hi_at(x.zi, i) if x.S > 0 else lo_at(x.zi, i)) if (x.zi >= nz or DYN[x.zi]) else x.E),
                                 age=i - x.pk_pos) for x in states.values()]
            cand_ent = []
            Ecache = {}
            for key, x in list(states.items()):
                if x.p0 >= i:
                    continue
                zi, S = x.zi, x.S
                isv = zi >= nz
                E = (hi_at(zi, i) if S > 0 else lo_at(zi, i)) if (isv or DYN[zi]) else x.E
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
                if isv:
                    vf['cf_ok'] += 1
                ckey = (s, x.lab, S, round(E, 1)) if (not isv and OLD[zi]) else (s, name_of(zi), S)
                if count.get(ckey, 0) >= 2:
                    continue
                slf = (SLF[zi] if not isv else vcl_slfar)
                if slf:
                    far = (lo_at(zi, i) if S > 0 else hi_at(zi, i))
                else:
                    far = E
                struct = min(lo[i], far - ZONE_HALF) if S > 0 else max(hi[i], far + ZONE_HALF)
                r = K.risk(df, i, S, struct, rr=rr)
                if r is None:
                    F(zi)['no_risk'] += 1
                    if isv:
                        vlog['norisk'].append((int(x.uid), float(hi_at(zi, i) - lo_at(zi, i))))
                    continue
                trung = None
                if isv:
                    zl_, zh_ = lo_at(zi, i), hi_at(zi, i)
                    tl = []
                    for zj in range(nz):
                        l_, h_ = LO[zj][i], HI[zj][i]
                        if l_ == l_ and l_ <= zh_ + 1.0 and h_ >= zl_ - 1.0:
                            tl.append(ZT[zj])
                    trung = tuple(sorted(set(tl)))
                    if drop_overlap and trung:
                        vf['s5_bo_trung'] += 1
                        continue
                    if lock:
                        olds = sig_log.get((s, S), ())
                        if sum(1 for e0 in olds if abs(e0 - E) <= ZONE_HALF) >= 2:
                            vf['khoa_muc'] += 1
                            continue
                cand_ent.append((abs(ci - E), RANK[zi] if not isv else VCL_RANK, zi, S, key, E, r, ckey, npb, trung))
            chosen = None
            if cand_ent:
                cand_ent.sort(key=lambda t: (t[0], t[1], t[2]))
                if len(cand_ent) > 1:
                    fn['conflict'] += 1
                    vf['thua_tranh'] += sum(1 for t in cand_ent[1:] if t[2] >= nz)
                chosen = cand_ent[0]
                _, _, zi, S, key, E, r, ckey, npb, trung = chosen
                x = states[key]
                isv = zi >= nz
                dist = S * (x.pk_val - E)
                if mom and dist < d_min:
                    F(zi)['armed_drift'] += 1
                ent = dict(idx=i, side=S, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='A', zone=name_of(zi), zbase=ztype_of(zi),
                           ztype=ztype_of(zi) if (isv or not OLD[zi]) else ('BAND_' + str(x.lab)), E=float(E), L=float(x.L),
                           pbmax=float(x.pbmax), npb=int(npb), p0=int(x.p0), pk_pos=int(x.pk_pos), pk_val=float(x.pk_val),
                           dist_pk=float(dist), bars_mom=int(x.pk_pos - x.p0), brk_no=int(x.brk_no),
                           sm_p0=int(sm[x.p0]), sm_cf=int(sm[i]), zlo=float(lo_at(zi, i)), zhi=float(hi_at(zi, i)),
                           uid=int(x.uid), ent_no=int(x.n_ent + 1), floor=bool(r['floor_applied']), reopen=bool(x.reopen),
                           note='pha %s %s E=%.1f cuc tri %.1f gia sau %d nen, hoi %d nen' % (
                               'len' if S > 0 else 'xuong', name_of(zi), E, dist, x.pk_pos - x.p0, npb))
                if isv:
                    e_ = zi - nz
                    j_ = x.kpos - v_b0[e_]
                    ent.update(vcl=True, eid=int(vv.eid_of[e_]), kpos=int(x.kpos),
                               slot_k=(int(vv.slot[v_off[e_] + j_]) if 0 <= j_ < v_ln[e_] else -1),
                               d10=(bool(vv.d10[v_off[e_] + j_]) if 0 <= j_ < v_ln[e_] else False),
                               width=float(hi_at(zi, i) - lo_at(zi, i)), trung_list='+'.join(trung) if trung else '', trung=bool(trung))
                    vf['chon'] += 1
                else:
                    ent['vcl'] = False
                entries.append(ent)
                sig_log.setdefault((s, S), []).append(float(E))
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
                            E = (hi_at(x.zi, i) if S > 0 else lo_at(x.zi, i)) if (x.zi >= nz or DYN[x.zi]) else x.E
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
# 3. MÔ PHỎNG + THỐNG KÊ (dùng lại hàm của v4)
# =============================================================================================
def run5(P, V, Z=None, vcl=True, vblock=MAIN_VBLOCK, rr=RR, want_cands=False, **kw):
    """Chạy detect5 + mô phỏng 1 lệnh mở chung. Trả dict(ents, tr, c, fn, vf, vl, cands)."""
    Z = P.zones('new') if Z is None else Z
    fn, vf, vl = {}, {}, {}
    cands = [] if want_cands else None
    ents = detect5(P, Z, V if vcl else None, vblock=vblock, rr=rr, funnel=fn, vfunnel=vf, vlog=vl, cands=cands, **kw)
    tr = A4.sim(P, ents)
    return dict(ents=ents, tr=tr, c=A4.closed(tr), fn=fn, vf=vf, vl=vl, cands=cands, Z=Z)


def sub_summ(P, sub):
    return A4.summ(P, list(range(len(sub))), sub)


def vword(v):
    """Chữ cho người học: ▲ = hơn, ▼ = kém hơn, ≈ = không hơn, không áp dụng = n quá nhỏ."""
    if v.startswith('KHÁC đối chứng ▲'):
        return 'hơn'
    if v.startswith('KHÁC đối chứng ▼'):
        return 'kém hơn'
    if v.startswith('không áp dụng'):
        return 'n quá nhỏ'
    return 'không hơn'


# ------------------------------------------------------------------------------ đối chứng
def _lohi_eid(view, e, i):
    j = i - view.b0[e]
    if 0 <= j < view.ln[e]:
        return float(view.lo[view.off[e] + j]), float(view.hi[view.off[e] + j])
    return math.nan, math.nan


def _struct5(P, Z, view, zi, i, S, E):
    nz = len(Z)
    if zi < nz:
        return A4._struct(P, Z, zi, i, S, E)
    lo_, hi_ = _lohi_eid(view, zi - nz, i)
    far = lo_ if S > 0 else hi_                         # bản chính: SL qua mép xa
    return min(P.lo[i], far - ZONE_HALF) if S > 0 else max(P.hi[i], far + ZONE_HALF)


def ctrl1_5(P, Z, V, c, cands, rr=RR, ndraw=CTRL_DRAWS, seed0=1000):
    """ĐC1 (như v4 ctrl1): hồ = nến trong trạng thái đã trang bị, chưa quá T_HOI, chạm E, hợp lệ; bỏ nhịp hồi/CF. Mỗi lệnh thật rút 1 nến
    cùng chiều, cùng LOẠI vùng (thêm 'VCL'), cùng TRAIN/TEST. Truyền c = chỉ lệnh VCL ⇒ ĐC1-VCL (hồ chỉ còn nến của trạng thái VCL)."""
    if not len(c):
        return {}, 0
    view = V.view(None)
    nz = len(Z)
    real = set(int(x) for x in c['idx'])
    split = P.df['split'].to_numpy()
    seen, pool = set(), {}
    for (i, S, zi, E) in cands:
        if i in real or (i, S, zi) in seen:
            continue
        seen.add((i, S, zi))
        r = K.risk(P.df, i, S, _struct5(P, Z, view, zi, i, S, E), rr=rr)
        if r is None:
            continue
        zt = Z[zi]['ztype'] if zi < nz else 'VCL'
        key = (S, zt, split[i])
        pool.setdefault(key, []).append(dict(idx=int(i), side=int(S), entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='CTRL1', zone=str(zi)))
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
        t = A4.closed(K.simulate(P.df, ents, one_at_a_time=False))
        if not len(t):
            continue
        rv = t['r'].to_numpy(float)
        spv = np.array([grp[k][0] for k in t['k']])
        thv = np.array([grp[k][1] for k in t['k']])
        for g, col, val in GROUPS:
            m = np.ones(len(t), bool) if col is None else (spv == val if col == 'split' else thv == val)
            per[g].append(rv[m].mean() if m.any() else np.nan)
    return {g: A4._bv().band(v) for g, v in per.items()}, npool


def vcl_edge_cols(P, V):
    """Hai cột theo nến cho ĐC2: MUA = `hi` của vùng VCL trong bộ có hi gần giá đóng nhất; BÁN = `lo` gần nhất (plan 3.4)."""
    vw = V.view(None)
    C = P.cl
    n = len(C)
    cnt = np.diff(V.bptr)
    b = np.flatnonzero(cnt > 0)
    out = {}
    for side, arr in ((1, vw.B_hi), (-1, vw.B_lo)):
        d = np.abs(arr - C[V.B_bar])
        o = np.lexsort((d, V.B_bar))
        col = np.full(n, np.nan)
        col[b] = arr[o[V.bptr[b]]]
        out[side] = col
    return out


def ctrl2_5(P, Z, V, c, ndraw=CTRL_DRAWS):
    """ĐC2 = kernel.control_sample. Lệnh vùng v4: cột vùng như v4. Lệnh VCL: 2 cột chung (vcl_edge_cols). 200 lần."""
    if not len(c):
        return {}
    zi_of = {z['name']: k for k, z in enumerate(Z)}
    edge = vcl_edge_cols(P, V) if (c['zbase'] == 'VCL').any() else None
    cols, name2col, recs, grp = {}, {}, [], {}
    for x in c.itertuples():
        if x.zbase == 'VCL':
            key = 'VCL|%d' % x.side
            if key not in cols:
                cols[key] = edge[int(x.side)]
        else:
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
        ce = A4.control_sample_map(P.df, zcols, P.mode, recs, name2col, n_random=1, seed=sd, tol=1.0)
        if not ce:
            continue
        t = A4.closed(K.simulate(P.df, ce, one_at_a_time=False))
        if not len(t):
            continue
        src = t['note'].str.extract(r'idx (\d+)')[0].astype(int).map(grp)
        spv = np.array([v[0] for v in src])
        thv = np.array([v[1] for v in src])
        rv = t['r'].to_numpy(float)
        for g, col, val in GROUPS:
            m = np.ones(len(t), bool) if col is None else (spv == val if col == 'split' else thv == val)
            per[g].append(rv[m].mean() if m.any() else np.nan)
    return {g: A4._bv().band(v) for g, v in per.items()}


_G5 = {}


def _rep5(k):
    P, V, Z, mode, dsh = _G5['P'], _G5['V'], _G5['Z'], _G5['mode'], _G5['dsh']
    d = dsh[:, k]
    if mode == 'whole':
        ents = detect5(P, Z, V, shift=d, vshift=d)
    else:                                                # 'vcl': chỉ dời bản đồ VCL, vùng v4 để nguyên
        ents = detect5(P, Z, V, shift=None, vshift=d)
    c = A4.closed(A4.sim(P, ents))
    if mode == 'vcl':
        c = c[c['zbase'] == 'VCL']
    rv = c['r'].to_numpy(float) if len(c) else np.array([])
    out = {'_n': len(c)}
    for g, col, val in GROUPS:
        m = A4.gmask(c, col, val) if len(c) else np.zeros(0, bool)
        out[g] = float(rv[m].mean()) if m.any() else np.nan
    return out


def ctrl3_5(P, V, Z, mode, workers=12, reps=REPS):
    """ĐC3: mode 'whole' = dời CẢ vùng v4 và VCL cùng δ; mode 'vcl' = dời CHỈ bản đồ VCL (vùng v4 để nguyên) và lấy R của lệnh VCL.
    Cùng ma trận δ hạt 20261024 như v4/VCL (A4.shift_matrix)."""
    import multiprocessing as mp
    dsh = A4.shift_matrix(P)[:, :reps]
    _G5.update(P=P, V=V, Z=Z, mode=mode, dsh=dsh)
    with mp.get_context('fork').Pool(workers) as pool:
        res = pool.map(_rep5, range(dsh.shape[1]))
    bands = {g: A4._bv().band([x[g] for x in res]) for g, _, _ in GROUPS}
    pday = A4._bv().band([x['_n'] / P.days for x in res])
    return bands, pday


# ------------------------------------------------------------------------------ mô tả / phễu
def roi_overlap(V, rows, within=ROI_OVERLAP_BARS):
    """rows = [(eid, armed, nến M5 hủy)] → số trạng thái có eid MỚI chồng lên dải cũ trong <= within nến (V4). Chỉ báo, không dùng để quyết."""
    order = np.argsort(V.b0, kind='stable')
    sb0 = V.b0[order]
    res = dict(total=0, armed=0, ov=0, armed_ov=0)
    for eid, armed, i in rows:
        e = int(np.searchsorted(V.eid_of, eid))
        L = int(V.b1[e])
        lo_old, hi_old = V.E_lo[V.off[e] + V.ln[e] - 1], V.E_hi[V.off[e] + V.ln[e] - 1]
        a = np.searchsorted(sb0, L + 1, 'left')
        b = np.searchsorted(sb0, L + within, 'right')
        ov = False
        for e2 in order[a:b]:
            if e2 != e and V.E_lo[V.off[e2]] < hi_old and V.E_hi[V.off[e2]] > lo_old:
                ov = True
                break
        res['total'] += 1
        res['armed'] += int(armed)
        res['ov'] += int(ov)
        res['armed_ov'] += int(armed and ov)
    return res


def level_over(P, ents):
    from collections import defaultdict
    seen = defaultdict(list)
    out = dict(v4=0, vcl=0)
    for e in ents:
        key = (int(P.sno[e['idx']]), int(e['side']))
        n_old = sum(1 for x in seen[key] if abs(x - e['E']) <= ZONE_HALF)
        if n_old >= 2:
            out['vcl' if e.get('vcl') else 'v4'] += 1
        seen[key].append(e['E'])
    return out


def width_bin(w):
    for a, b, lab in ((0, 2.0, '< 2'), (2.0, 2.5, '2–2,5'), (2.5, 3.5, '2,5–3,5'), (3.5, 5.0 + 1e-9, '3,5–5'), (5.0 + 1e-9, 1e9, '> 5')):
        if a - 1e-9 <= w < b:
            return lab
    return '?'


WIDTH_LABS = ('< 2', '2–2,5', '2,5–3,5', '3,5–5', '> 5')


def ex_vcl_table(g):
    L = ['| giờ VN (UTC) | chiều | eid [lo; hi] | E | cực trị (cách E) | nến đà | nến hồi | L | pbmax | vào | SL | TP | kết quả | R | trùng / riêng |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for x in g.itertuples():
        L.append('| %s (%s) | %s | %d [%.2f; %.2f] | %.2f | %.1f (%.1f) | %d | %d | %.1f | %.1f | %.1f | %.1f | %.1f | %s | %+.2f | %s |' % (
            str(x.t_vn)[:16], str(x.t_utc)[11:16], 'MUA' if x.side > 0 else 'BÁN', x.eid, x.zlo, x.zhi, x.E, x.pk_val, x.dist_pk, x.bars_mom,
            x.npb, x.L, x.pbmax, x.entry, x.sl, x.tp, x.outcome, x.r, ('trùng ' + x.trung_list) if x.trung else 'riêng'))
    return L


def plot_vcl_session(P, V, trades, sid, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    t = trades[(trades['session_id'] == sid) & (trades['zbase'] == 'VCL')].sort_values('idx')
    t = t[t['outcome'].isin(['TP', 'SL'])].head(2)
    if not len(t):
        return None
    vw = V.view(None)
    df = P.df
    fig, axes = plt.subplots(len(t), 1, figsize=(15, 5.4 * len(t)), squeeze=False)
    for ax, x in zip(axes[:, 0], t.itertuples()):
        a = max(int(x.p0) - 25, int(P.st.loc[P.sno[x.idx], 'start_pos']))
        b = min(len(df) - 1, int(x.exit_idx) + 12, a + 200)
        rr = np.arange(a, b + 1)
        up = P.cl[rr] >= P.op[rr]
        ax.vlines(rr, P.lo[rr], P.hi[rr], color=np.where(up, '#2a7a3b', '#b23a3a'), lw=0.8)
        ax.bar(rr, np.abs(P.cl[rr] - P.op[rr]) + 0.02, bottom=np.minimum(P.op[rr], P.cl[rr]), width=0.6,
               color=np.where(up, '#2a7a3b', '#b23a3a'), edgecolor='none')
        ylo, yhi = float(P.lo[rr].min()) - 2, float(P.hi[rr].max()) + 2
        drawn = 0
        for e in range(V.ne):                                                    # mọi vùng VCL sống trong cửa sổ: tím nhạt
            if V.b1[e] < a or V.b0[e] > b:
                continue
            lo_a, hi_a = np.full(len(rr), np.nan), np.full(len(rr), np.nan)
            for k, bb in enumerate(rr):
                j = bb - V.b0[e]
                if 0 <= j < V.ln[e]:
                    lo_a[k], hi_a[k] = vw.lo[vw.off[e] + j], vw.hi[vw.off[e] + j]
            if np.nanmax(hi_a) < ylo or np.nanmin(lo_a) > yhi:
                continue
            main = int(vw.eid_of[e]) == int(x.eid)
            ax.fill_between(rr, lo_a, hi_a, color='#7b4fb3', alpha=0.34 if main else 0.10, lw=0,
                            label=('vùng VCL %d (vùng của lệnh)' % x.eid) if main else ('các vùng VCL khác đang hiển thị' if drawn == 0 else None))
            drawn += 0 if main else 1
        e_o = int(np.searchsorted(V.eid_of, x.eid))
        e_line = np.full(len(rr), np.nan)
        for k, bb in enumerate(rr):
            j = bb - V.b0[e_o]
            if 0 <= j < V.ln[e_o]:
                e_line[k] = vw.hi[vw.off[e_o] + j] if x.side > 0 else vw.lo[vw.off[e_o] + j]
        ax.plot(rr, e_line, color='#e8a33c', lw=1.6, label='cạnh E (%s)' % ('mép trên' if x.side > 0 else 'mép dưới'))
        ax.axvline(x.p0, color='#555555', lw=1, ls=':')
        ax.annotate('M5 phá đóng', (x.p0, yhi - 0.5), fontsize=8, color='#555555', ha='left', va='top')
        ax.plot([x.pk_pos], [x.pk_val], marker='v' if x.side > 0 else '^', ms=10, color='#6a3d9a', ls='none',
                label='cực trị cuối (cách E %.1f giá)' % x.dist_pk)
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
        ax.set_ylim(ylo, yhi)
        ax.grid(alpha=0.15)
        ax.set_ylabel('giá')
        ax.set_title('%s vùng VCL %d — vào %s VN (%s UTC) — %s — R = %+.2f — %s' % (
            'MUA' if x.side > 0 else 'BÁN', x.eid, str(x.t_vn)[:16], str(x.t_utc)[11:16], 'chạm TP' if x.outcome == 'TP' else 'chạm SL', x.r,
            ('trùng vùng v4: ' + x.trung_list) if x.trung else 'VCL-riêng'), fontsize=10)
        ax.legend(fontsize=8, loc='best', framealpha=0.85)
    fig.suptitle('A-v5 — phiên %s (giờ trục x = giờ VN) — ảnh MINH HOẠ, không phải ca điển hình' % sid, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=90)
    plt.close(fig)
    return path


# =============================================================================================
# 4. BÁO CÁO
# =============================================================================================
def f(x, p=2, sign=True):
    return A4.f(x, p, sign)


def pc(x):
    return A4.pc(x)


def nr(s):
    return A4.nr(s)


def full_row(lab, sub, sub_vb, P):
    s = sub_summ(P, sub)
    sv = sub_summ(P, sub_vb)
    return '| %s | %d (%.2f) | %s | %s [%s; %s] | %s | %s | %s | %s | %s | %s | %s | %s | %d · %s · %s | %d · %s | %d · %s · %s |' % (
        lab, s['n'], s['pday'], pc(s['wr']), f(s['m']), f(s['lo']), f(s['hi']), nr(s['TRAIN']), nr(s['TEST']), nr(s['T8']), nr(s['T9']), nr(s['T10']),
        nr(s['ph_A']), nr(s['ph_EU']), nr(s['ph_US']), s['eve']['n'], pc(s['eve']['wr']), f(s['eve']['m']), s['vo']['n'], f(s['vo']['m']),
        sv['n'], pc(sv['wr']), f(sv['m']))


FULL_HEAD = ['| nhóm | n (lệnh/ngày) | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R | T8 n / R | T9 n / R | T10 n / R | Á n / R | Âu n / R | Mỹ n / R | '
             '18:00–19:20 n · WR · R | 19:20–20:30 n · R | CÓ chặn 19:20–20:30 n · WR · R |',
             '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']


def main(fast=False):
    t0 = time.time()
    P, V = load5(True)
    Z = P.zones('new')
    out = []
    W = out.append
    # ------------------------------------------------------------ chạy các bản
    g_ents, g_tr, _ = A4.run(P, 'goc')
    g_c = A4.closed(g_tr)
    g = A4.summ(P, g_ents, g_tr)
    assert g['n'] == EXPECT_OLD[0] and abs(g['wr'] - EXPECT_OLD[1]) < 1e-9 and round(g['m'], 2) == EXPECT_OLD[2], g
    d4 = run5(P, V, vcl=False, want_cands=True)                       # A-v4 qua máy mới (VCL tắt)
    ents4, tr4, _ = A4.run(P, 'd')
    assert [(e['idx'], e['side'], e['entry'], e['sl'], e['tp'], e['zone']) for e in ents4] == \
           [(e['idx'], e['side'], e['entry'], e['sl'], e['tp'], e['zone']) for e in d4['ents']], 'A-v4 qua may moi KHONG khop tung lenh'
    s4 = A4.summ(P, ents4, tr4)
    assert s4['n'] == EXPECT_V4[0] and abs(s4['wr'] - EXPECT_V4[1]) < 0.0006 and round(s4['m'], 2) == EXPECT_V4[2], s4
    R5 = run5(P, V, want_cands=True)
    R5vb = run5(P, V, vblock=True)
    c5, c4 = R5['c'], d4['c']
    s5 = A4.summ(P, R5['ents'], R5['tr'])
    cv = c5[c5['zbase'] == 'VCL'].copy()
    cx = c5[c5['zbase'] != 'VCL'].copy()
    cv['trung'] = cv['trung'].astype(bool)
    cv['d10'] = cv['d10'].astype(bool)
    cv['trung_list'] = cv['trung_list'].fillna('')
    cv['slot_k'] = cv['slot_k'].astype(int)
    cv['eid'] = cv['eid'].astype(int)
    vb_c = R5vb['c']
    print('chay xong 3 ban %.0fs: A-v5 n=%d' % (time.time() - t0, s5['n']), flush=True)
    sv_all, sx_all = sub_summ(P, cv), sub_summ(P, cx)
    sd5 = s5['sd']
    vf, vl = R5['vf'], R5['vl']
    # ------------------------------------------------------------ 0 đầu
    W('# RESULTS-A-V5 — Setup A "Phá hồi": A-v4 + vùng hỗ trợ/kháng cự của Vùng Canh Lệnh (VCL v5)')
    W('')
    W('Sinh bởi `setup_a_v5.py` (tất định, hạt cố định) theo đặc tả `plans/BENZO-A-V5-plan.md` (Opus). Dữ liệu: CHỈ `fp_GCZ26_XCEC_Time_20260723-20261021_90d`, giờ UTC '
      '(VN = UTC+7). TRAIN = phiên ≤ 2026-09-15, TEST từ 2026-09-16. **%d phiên sạch** (TRAIN %d / TEST %d) — "lệnh/ngày" chia cho %d. Chi phí 0,2 giá/lệnh; '
      'nến chạm cả SL lẫn TP ⇒ tính SL; **1 lệnh mở cùng lúc chung cho vùng v4 và VCL** (A đứng riêng, không gộp B/C/D); TP 3R (hoà vốn sau phí ≈ 27%% WR). '
      'Tham số tự do MỚI = 0 (mọi số dùng lại từ v4).' % (P.days, P.days_split['TRAIN'], P.days_split['TEST'], P.days))
    W('')
    W('Thuật ngữ: **VCL** = indicator Vùng Canh Lệnh · **eid** = mã vùng ổn định · **bộ hiển thị** = các vùng VCL đang vẽ tại nến i · **cú phá thật** = trong chân cú phá có một '
      'nến M1 mà vùng đang hiển thị và giá đóng ở phía trong · **rời bộ** = eid không còn trong bộ hiển thị · **khoá mức** = chống đếm hai lần một mức giá · '
      '**đối chứng** = cách vào lệnh "bừa" để so · **công suất thống kê** = chênh nhỏ nhất đo ra được.')
    W('')
    # ------------------------------------------------------------ 1 công suất
    W('## 1. Công suất thống kê — ĐỌC TRƯỚC bảng chính (plan 3.1)')
    W('')
    W('Hiệu nhỏ nhất phát hiện được (xác suất 80%%, mức 5%%, hai phía) ≈ 2,8 × σ_R × √(1/n₁ + 1/n₂). σ_R của A-v5 = **%s**; n = %d (TRAIN %d / TEST %d); '
      'lệnh VCL n = %d (TRAIN %d / TEST %d), lệnh vùng v4 trong A-v5 n = %d (TRAIN %d / TEST %d).' % (
          f(sd5, 2, False), s5['n'], s5['TRAIN']['n'], s5['TEST']['n'], sv_all['n'], sv_all['TRAIN']['n'], sv_all['TEST']['n'],
          sx_all['n'], sx_all['TRAIN']['n'], sx_all['TEST']['n']))
    W('')
    mde_vx = {k: A4.mde(sd5, sv_all[k]['n'], sx_all[k]['n']) for k in ('TRAIN', 'TEST')}
    mde_vx['ALL'] = A4.mde(sd5, sv_all['n'], sx_all['n'])
    W('| so sánh | hiệu nhỏ nhất phát hiện được |')
    W('|---|---|')
    W('| R TB A-v5 so với 0 (một mẫu) | **%s R** |' % f(2.8 * sd5 / math.sqrt(max(s5['n'], 1)), 2, False))
    W('| A-v5 so với A-v4 (n = %d vs %d) | **%s R** |' % (s5['n'], s4['n'], f(A4.mde(sd5, s5['n'], s4['n']), 2, False)))
    W('| **lệnh VCL so lệnh vùng v4 trong A-v5** (cả hai đợt / TRAIN / TEST) | **%s / %s / %s R** |' % (
        f(mde_vx['ALL'], 2, False), f(mde_vx['TRAIN'], 2, False), f(mde_vx['TEST'], 2, False)))
    W('| riêng TEST so với đối chứng (n TEST = %d vs %d) | **%s R** |' % (s5['TEST']['n'], s5['TEST']['n'], f(A4.mde(sd5, s5['TEST']['n'], s5['TEST']['n']), 2, False)))
    W('| riêng lệnh VCL, TEST so với đối chứng (n TEST = %d) | **%s R** |' % (sv_all['TEST']['n'], f(A4.mde(sd5, sv_all['TEST']['n'], sv_all['TEST']['n']), 2, False)))
    W('')
    W('⇒ **Chênh nhỏ hơn các con số này không phân biệt được với may rủi trên 90 ngày.**')
    W('')
    # ------------------------------------------------------------ 2 bảng chính
    W('## 2. BẢNG CHÍNH (TP 3R, sau phí, 1 lệnh mở, không chặn 19:20–20:30)')
    W('')
    W('R TB [KTC 95%] = bootstrap 10 000 lần hạt 0 (đánh giá THẤP độ bất định vì lệnh cùng phiên không độc lập).')
    W('')
    W('| bản | số lệnh (tổng · /ngày) | WR | R TB sau phí [KTC 95%] |')
    W('|---|---|---|---|')
    for lab, s in (('A cũ (V3 gốc)', g), ('A-v4', s4), ('**A-v5 (A-v4 + vùng VCL)**', s5)):
        W('| %s | %d · %.2f | %s | %s [%s; %s] |' % (lab, s['n'], s['pday'], pc(s['wr']), f(s['m']), f(s['lo']), f(s['hi'])))
    W('')
    # dòng 1-4 điền sau (cần đối chứng) — dùng placeholder để chèn
    idx_lines = len(out)
    out += ['@@LINE1@@', '@@LINE2@@', '@@LINE3@@', '@@LINE4@@']
    W('')
    W('Lệnh VCL (%d lệnh) tách thành VCL-riêng / trùng vùng v4 ở mục 5.2. Số lệnh/ngày dùng mẫu số %d phiên sạch.' % (sv_all['n'], P.days))
    W('')
    # ------------------------------------------------------------ chỗ tự quyết
    W('## 3. Chỗ tự quyết của Sonnet (plan không nói rõ — chọn hướng hợp lý nhất, ghi lại)')
    W('')
    doc = sys.modules[__name__].__doc__
    items = []
    for line in doc.split('CÁC CHỖ TỰ QUYẾT')[1].split('\n')[1:]:
        t_ = line.strip()
        if not t_:
            continue
        if t_[0] == 'V' and len(t_) > 1 and t_[1].isdigit():
            items.append(t_)
        elif items:
            items[-1] += ' ' + t_
    for it in items:
        W('- ' + it)
    W('- V9 Thứ tự mục: plan 3.1 đòi in công suất TRƯỚC bảng chính, plan mục 7 đòi bảng chính đầu tiên ⇒ để mục công suất (ngắn, 5 dòng) ngay sau tiêu đề rồi tới bảng chính.')
    W('- V10 Trước lần commit test, tôi đã chạy thử `detect5` MỘT lần để bắt lỗi (in số lệnh/phễu); KHÔNG đổi luật hay hằng số nào theo số đó. '
      'Hai sửa sau lần chạy thử chỉ là cách ĐẾM phễu (`roi_bo` bị đếm đôi; "hủy phía đối diện" bị che bởi "hủy sâu" vì M5 đóng ngoài mép xa luôn sâu hơn 1 giá '
      '⇒ nay ưu tiên nhãn "đối diện"). Lịch sử git (`eed1c6d` test + máy, trước kết quả) là bằng chứng.')
    W('- V11 Ca "hủy +1 mở −1 cùng nến" của plan 2.6: khi M5 đóng dưới `lo`, trạng thái +1 luôn bị hủy ở nhãn "đối diện" (không bao giờ ở nhãn "hủy sâu"); '
      'trạng thái −1 mở cùng nến nếu qua luật cú phá thật.')
    W('- V12 Mỗi lần thử mở trạng thái bị luật cú phá thật chặn được đếm MỘT lần cho MỖI nến M5 (cùng một eid có thể bị đếm lại ở nến M5 sau) — phễu 3.3(4) là số lần thử, không phải số cú phá khác nhau.')
    W('- V13 Vùng VCL ĐÃ có độ rộng 2–5 giá (engine kẹp), nhưng test tổng hợp dùng vùng hẹp hơn (1,5 giá) cho vừa trần SL 4 giá — chỉ là dữ liệu giả, không ảnh hưởng kết quả thật.')
    W('')
    # ------------------------------------------------------------ 4 chi tiết
    W('## 4. Điều kiện tiên quyết (plan 3.0) — đã đạt')
    W('')
    import subprocess
    tp = subprocess.run([sys.executable, '-m', 'pytest', os.path.join(HERE, 'test_setup_a_v5.py'), '-q'], capture_output=True, text=True, cwd=HERE)
    tests_ok = tp.returncode == 0
    W('- (1) A cũ qua máy mới (band cũ, logic V3, cấm 18:00–19:20): **n = %d, WR %s, R TB %s** [%s; %s] — khớp từng lệnh `setup_a_pha_hoi.detect(expire=30)` (test).' % (
        g['n'], pc(g['wr']), f(g['m']), f(g['lo']), f(g['hi'])))
    W('- (2) `detect5` với VCL TẮT khớp từng trường của từng lệnh `setup_a_v4.detect` cấu hình (d): **n = %d, WR %s, R TB %s**, TRAIN %s · TEST %s (test, cả `None` lẫn bộ VCL rỗng).' % (
        s4['n'], pc(s4['wr']), f(s4['m']), nr(s4['TRAIN']), nr(s4['TEST'])))
    W('- (3) Phiên 2026-09-08 và 2026-10-02: vòng lặp THƯA == vòng lặp DÀY (cùng lệnh, cùng phễu, cùng danh sách `roi_bo`) — test.')
    W('- Test toàn bộ `test_setup_a_v5.py` chạy lại lúc sinh báo cáo: **%s**. Khớp chuỗi nến cache VCL ↔ dữ liệu: độ dài %d và datetime từng phần tử (`zones_a_v5.load_rec_checked`).' % (
        tp.stdout.strip().splitlines()[-1] if tp.stdout.strip() else tp.stderr[-200:], len(P.df)))
    W('')
    # 3.3 (1) phân rã
    W('## 5. Chi tiết (plan 3.3)')
    W('')
    W('### 5.1 Phân rã số lệnh')
    W('')
    k4 = {(int(x.idx), int(x.side), x.zone) for x in c4.itertuples()}
    k5x = {(int(x.idx), int(x.side), x.zone) for x in cx.itertuples()}
    lost = c4[[(int(x.idx), int(x.side), x.zone) not in k5x for x in c4.itertuples()]]
    new4 = cx[[(int(x.idx), int(x.side), x.zone) not in k4 for x in cx.itertuples()]]
    raw_v = [e for e in R5['ents'] if e['vcl']]
    vraw_idx = {e['idx'] for e in raw_v}
    vtr = [(int(x.idx), int(x.exit_idx)) for x in cv.itertuples()]
    why_c = {'thua tranh cùng nến (VCL gần hơn)': 0, 'bị lệnh VCL đang mở chặn': 0, 'khác (trạng thái v4 đổi dây chuyền)': 0}
    for x in lost.itertuples():
        i = int(x.idx)
        if i in vraw_idx:
            why_c['thua tranh cùng nến (VCL gần hơn)'] += 1
        elif any(a_ < i < b_ for a_, b_ in vtr):
            why_c['bị lệnh VCL đang mở chặn'] += 1
        else:
            why_c['khác (trạng thái v4 đổi dây chuyền)'] += 1
    raw_x = [e for e in R5['ents'] if not e['vcl']]
    W('n(A-v5) = n(A-v4) − mất + v4 mới xuất hiện + VCL:  **%d = %d − %d + %d + %d**  (kiểm: %d).' % (
        s5['n'], s4['n'], len(lost), len(new4), sv_all['n'], s4['n'] - len(lost) + len(new4) + sv_all['n']))
    W('')
    W('- Lệnh A-v4 bị MẤT trong A-v5: **%d** — %s.' % (len(lost), '; '.join('%s: %d' % kv for kv in why_c.items())))
    W('- "v4 mới xuất hiện" (tín hiệu v4 trước bị lệnh v4 khác chặn, nay được vào): **%d**.' % len(new4))
    W('- Tín hiệu THÔ (trước luật 1 lệnh mở): A-v4 = %d; A-v5 phần v4 = %d, phần VCL = %d.' % (len(ents4), len(raw_x), len(raw_v)))
    W('- Lệnh mất tính điểm: R TB của %d lệnh v4 bị mất = %s; R TB của %d lệnh v4 mới = %s (đó là phần "đổi lệnh" mà luật 1 lệnh mở gây ra, ngoài lệnh VCL thêm).' % (
        len(lost), f(lost['r'].mean()) if len(lost) else '—', len(new4), f(new4['r'].mean()) if len(new4) else '—'))
    W('')
    # 5.2 riêng / trùng
    W('### 5.2 Lệnh VCL: VCL-riêng vs trùng vùng v4')
    W('')
    W('"Trùng" = tại nến vào có ≥ 1 vùng v4 (6 loại, có giá trị, VWAP đã qua Warm) mà dải giao [lo_VCL − 1, hi_VCL + 1]. CHỈ MÔ TẢ, không lọc.')
    W('')
    W('| nhóm | n | lệnh/ngày | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R |')
    W('|---|---|---|---|---|---|---|')

    def line(lab, sub):
        s = sub_summ(P, sub)
        W('| %s | %d | %.2f | %s | %s [%s; %s] | %s | %s |' % (lab, s['n'], s['n'] / P.days, pc(s['wr']), f(s['m']), f(s['lo']), f(s['hi']), nr(s['TRAIN']), nr(s['TEST'])))
    line('tất cả lệnh VCL', cv)
    line('**VCL-riêng** (không trùng vùng v4)', cv[~cv['trung']])
    line('**trùng** vùng v4', cv[cv['trung']])
    rest = np.zeros(len(cv), bool)
    for zt in V4_TYPES:
        m = cv['trung_list'].str.split('+').apply(lambda L_, zt=zt: zt in L_).to_numpy()
        if m.sum() >= MIN_N:
            line('· trùng %s (một lệnh có thể trùng nhiều loại)' % zt, cv[m])
        else:
            rest |= m
    if rest.any():
        line('· trùng loại khác (mỗi loại n < 10, gộp)', cv[rest])
    W('')
    # 5.3 bảng lớn
    W('### 5.3 A-v5 · lệnh vùng v4 · lệnh VCL theo TRAIN / TEST / tháng / pha / khung giờ / bản có chặn')
    W('')
    W('T8 gồm 29–31/7. Khung 18:00–19:20 = nến M5 phá HOẶC nến CF rơi trong sm 780..859; 19:20–20:30 = nến CF trong sm 860..929. '
      '"CÓ chặn" = chạy lại cả máy với luật cấm CF trong 19:20–20:30 (đúng engine C#), rồi tách theo nhóm.')
    W('')
    out += FULL_HEAD
    W(full_row('A-v5 (tất cả)', c5, vb_c, P))
    W(full_row('· lệnh vùng v4', cx, vb_c[vb_c['zbase'] != 'VCL'], P))
    W(full_row('· lệnh VCL', cv, vb_c[vb_c['zbase'] == 'VCL'], P))
    W(full_row('(tham chiếu) A-v4', c4, A4.closed(A4.sim(P, A4.detect(P, Z, logic='mom', vblock=True))), P))
    W('')
    # 5.4 phễu
    W('### 5.4 Phễu VCL')
    W('')
    ro = roi_overlap(V, vl['roi_bo'])
    frac_roi = vf['roi_bo_armed'] / max(1, vf['armed'])
    nrisk_states = len({u for u, _ in vl['norisk']})
    W('| bước | số |')
    W('|---|---|')
    funnel_rows = [
        ('lần M5 đóng ngoài một vùng VCL (tất cả, kể cả đã có trạng thái)', vf['m5_ngoai_tat_ca']),
        ('lần THỬ mở trạng thái (chưa có trạng thái cùng chiều)', vf['m5_ngoai_thu']),
        ('· bị luật CÚ PHÁ THẬT chặn — tổng', vf['khong_pha_that']),
        ('   · vùng vắng ở nến chân cú phá (sinh ra trong/sau cú phá)', vf['kpt_vang']),
        ('   · chạy hết 60 nến mà giá vẫn ngoài (giá chưa từng ở trong)', vf['kpt_het60']),
        ('   · chạm đầu phiên', vf['kpt_dau_phien']),
        ('· MỞ trạng thái — tổng', vf['open']),
        ('   · mở mới / mở lại sau hết hạn (Q9)', '%d / %d' % (vf['open_fresh'], vf['open_reopen'])),
        ('· ĐÃ TRANG BỊ (cực trị cách cạnh ≥ 2 giá, một lúc nào đó)', vf['armed']),
        ('· hủy sâu (M5 đóng trong sâu > 1 giá)', vf['cancel_sau']),
        ('· hủy phía đối diện (M5 đóng ngoài mép xa)', vf['cancel_doi']),
        ('· hết hạn T_HOI', vf['expire']),
        ('· hết phiên', vf['end']),
        ('· rời bộ (`roi_bo`)', vf['roi_bo']),
        ('   · trong đó ĐÃ TRANG BỊ', vf['roi_bo_armed']),
        ('   · có eid MỚI chồng lên dải cũ trong ≤ 5 nến (tổng / đã trang bị)', '%d / %d' % (ro['ov'], ro['armed_ov'])),
        ('· lần ứng viên có CF hợp lệ (theo nến)', vf['cf_ok']),
        ('· bị trần SL 4 giá loại (theo nến / số trạng thái)', '%d / %d' % (vf['no_risk'], nrisk_states)),
        ('· bị khoá mức', vf['khoa_muc']),
        ('· thua tranh cùng nến (VCL xa hơn / hạng kém)', vf['thua_tranh']),
        ('· TÍN HIỆU ghi nhận (thắng tranh cùng nến)', vf['chon']),
        ('· LỆNH sau luật 1 lệnh mở (đã đóng)', sv_all['n']),
    ]
    for a_, b_ in funnel_rows:
        W('| %s | %s |' % (a_, b_))
    W('')
    W('**Rủi ro "mất lệnh vì đổi mã" (plan 2.5):** %d / %d trạng thái ĐÃ TRANG BỊ chết vì `roi_bo` = **%.1f%%** (ngưỡng cảnh báo 30%%) — %s. Trong số trạng thái bị `roi_bo`, %d/%d (%.0f%%) '
      'có eid mới chồng lên dải cũ trong ≤ 5 nến.' % (
          vf['roi_bo_armed'], vf['armed'], 100 * frac_roi, 'VƯỢT ngưỡng ⇒ ghi rủi ro, đề xuất vòng sau khoá theo mức giá (KHÔNG tự sửa vòng này)' if frac_roi > 0.30 else 'không vượt ngưỡng',
          ro['ov'], ro['total'], 100 * ro['ov'] / max(1, ro['total'])))
    W('')
    # 5.5 mô tả
    W('### 5.5 Mô tả lệnh VCL (CHỈ MÔ TẢ, không lọc; nhóm n < 10 ghi "n nhỏ")')
    W('')
    W('| nhóm | n | lệnh/ngày | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R |')
    W('|---|---|---|---|---|---|---|')

    def line2(lab, sub):
        if len(sub) < MIN_N:
            W('| %s | %d | n nhỏ | | | | |' % (lab, len(sub)))
        else:
            line(lab, sub)
    wb = cv['width'].apply(width_bin)
    nr_w = {lab: 0 for lab in WIDTH_LABS}
    nr_u = {lab: set() for lab in WIDTH_LABS}
    for u, w_ in vl['norisk']:
        lb = width_bin(w_)
        nr_w[lb] += 1
        nr_u[lb].add(u)
    for lab in WIDTH_LABS:
        sub = cv[wb == lab]
        if len(sub) or nr_w[lab]:
            line2('bề rộng vùng %s giá (kèm: tín hiệu bị trần SL loại %d theo nến, %d trạng thái)' % (lab, nr_w[lab], len(nr_u[lab])), sub)
    line2('slot K ở nến chân cú phá (giá ở trong vùng rồi phá)', cv[cv['slot_k'] == 0])
    line2('slot N/F ở nến chân cú phá (giá xuyên từ phía kia sang)', cv[cv['slot_k'] >= 1])
    line2('vùng chỉ có số tròn 10 USD (d10)', cv[cv['d10']])
    line2('vùng có mốc khác (không chỉ số tròn)', cv[~cv['d10']])
    line2('phá lần 1 (brk_no = 1)', cv[cv['brk_no'] == 1])
    line2('phá lần ≥ 2', cv[cv['brk_no'] >= 2])
    for a_, b_ in A4.DIST_BINS:
        line2('cực trị cách E %s–%s giá' % (f(a_, 0, False), ('∞' if b_ > 1e8 else f(b_, 0, False))), cv[(cv['dist_pk'] >= a_) & (cv['dist_pk'] < b_)])
    line2('trạng thái mở MỚI', cv[~cv['reopen']])
    line2('trạng thái MỞ LẠI sau hết hạn (Q9)', cv[cv['reopen']])
    line2('lệnh thứ 1 của trạng thái', cv[cv['ent_no'] == 1])
    line2('lệnh thứ ≥ 2 của trạng thái', cv[cv['ent_no'] >= 2])
    W('')
    # 5.6 ví dụ + ảnh
    W('### 5.6 Ví dụ để soi chart (lệnh VCL; giờ VN, kèm giờ UTC)')
    W('')
    W('"nến đà" = vị trí cực trị cuối − nến M5 phá. Với lệnh thứ 2 của một trạng thái, cực trị được đặt lại ở nến vào lệnh 1. Chọn cách đều theo thời gian, không chọn lọc.')
    W('')
    W('**5 lệnh VCL THẮNG**')
    W('')
    out += ex_vcl_table(A4.even_pick(cv[cv['r'] > 0]))
    W('')
    W('**5 lệnh VCL THUA**')
    W('')
    out += ex_vcl_table(A4.even_pick(cv[cv['r'] <= 0]))
    W('')
    os.makedirs(IMG, exist_ok=True)
    imgs = []
    wins = cv[cv['outcome'] == 'TP']
    loss = cv[cv['outcome'] == 'SL']
    picks = []
    if len(wins):
        picks.append(wins.iloc[len(wins) // 2]['session_id'])
    if len(loss):
        sid = loss.iloc[len(loss) // 2]['session_id']
        if sid in picks and len(loss) > 1:
            sid = loss.iloc[len(loss) // 2 + 1]['session_id']
        picks.append(sid)
    for sid in picks[:2]:
        pth = os.path.join(IMG, 'a_v5_%s.png' % sid)
        if plot_vcl_session(P, V, R5['tr'], sid, pth):
            imgs.append(pth)
    W('Ảnh minh hoạ (KHÔNG phải ca điển hình, chỉ để soi tay):')
    W('')
    for pth in imgs:
        W('- [%s](img/%s): dải tím đậm = vùng VCL của lệnh, tím nhạt = các vùng VCL khác đang hiển thị, vạch cam = cạnh E, tam giác tím = cực trị cuối, vùng tím nhạt dọc = nhịp hồi, '
          'xanh dương = vào, đỏ đứt = SL, xanh lá đứt = TP; chấm xám = nến M5 phá đóng.' % (os.path.basename(pth), os.path.basename(pth)))
    W('')
    # 5.7 rủi ro số kiểm
    lv = level_over(P, R5['ents'])
    lv4 = level_over(P, ents4)
    ntr = int(cv['trung'].sum())
    W('### 5.7 Số kiểm các rủi ro (plan mục 5)')
    W('')
    W('- **Tỉ lệ `roi_bo`:** %.1f%% trạng thái đã trang bị chết vì rời bộ (xem 5.4).' % (100 * frac_roi))
    W('- **Mức có > 2 tín hiệu / (phiên, chiều):** số tín hiệu là tín hiệu thứ ≥ 3 ở cùng mức (|ΔE| ≤ 1) — A-v4 một mình: %d; A-v5: phần v4 %d, phần VCL %d '
      '(khoá mức chặn phần VCL; phần v4 không xét khoá nên vẫn có thể thứ ≥ 3).' % (lv4['v4'], lv['v4'], lv['vcl']))
    W('- **Tỉ lệ lệnh VCL trùng vùng v4:** %d / %d = %.0f%%.' % (ntr, len(cv), 100 * ntr / max(1, len(cv))))
    pairs = 0
    for L_ in cv.groupby(['session_id', 'side'])['idx'].apply(lambda s_: sorted(s_)).tolist():
        pairs += sum(1 for u_, w_ in zip(L_, L_[1:]) if w_ - u_ <= 5)
    W('- **Hai trạng thái trên hai vùng VCL kề:** giữ cả hai (plan mục 5-7); cặp lệnh VCL cùng phiên cùng chiều cách nhau ≤ 5 nến: %d.' % pairs)
    W('- **Lệnh VCL mở lại (Q9):** %d / %d lệnh VCL; trạng thái VCL mở lại = %d / %d lần mở.' % (int(cv['reopen'].sum()), len(cv), vf['open_reopen'], vf['open']))
    W('')
    print('chi tiet xong %.0fs' % (time.time() - t0), flush=True)
    # ------------------------------------------------------------ 6 đối chứng
    W('## 6. Đối chứng (6 phép so có phán quyết; ngưỡng NGUYÊN PLAN-LAN-CHAM mục 5)')
    W('')
    W('Mỗi ô: R TB thật · TB đối chứng [5%; 95%]. "khác ▲" = **hơn**, "khác ▼" = **kém hơn**, "≈" = **không hơn**, "không áp dụng" = **n quá nhỏ** (cần ≥ 10 lệnh ở CẢ TRAIN và TEST). '
      'Tổng 6 phép ⇒ với ~5%% mỗi phép, ~0,3 ô "khác" có thể do ngẫu nhiên.')
    W('')
    W('| nhóm lệnh | đối chứng | GỘP | TRAIN | TEST | T8 | T9 | T10 | phán quyết | chữ |')
    W('|---|---|---|---|---|---|---|---|---|---|')
    VER = {}
    jobs = [('A-v5 toàn bộ', c5, 'ĐC1 cùng trạng thái', lambda: ctrl1_5(P, Z, V, c5, R5['cands'])),
            ('A-v5 toàn bộ', c5, 'ĐC2 control_sample', lambda: (ctrl2_5(P, Z, V, c5), None)),
            ('A-v5 toàn bộ', c5, 'ĐC3 dời cả bản đồ 3–15 giá', None),
            ('riêng lệnh VCL', cv, 'ĐC1-VCL', lambda: ctrl1_5(P, Z, V, cv, R5['cands'])),
            ('riêng lệnh VCL', cv, 'ĐC2-VCL', lambda: (ctrl2_5(P, Z, V, cv), None)),
            ('riêng lệnh VCL', cv, 'ĐC3-chỉ-dời-VCL', None)]
    for who, cc, lab, fnc in jobs:
        if fnc is None:
            if fast:
                continue
            bands, extra = ctrl3_5(P, V, Z, 'whole' if who.startswith('A-v5') else 'vcl')
        else:
            bands, extra = fnc()
        v, cmp = A4.judge(cc, bands)
        VER[(who, lab)] = (v, cmp, extra)
        cells = []
        for g_ in ('GỘP', 'TRAIN', 'TEST', 'T8', 'T9', 'T10'):
            x = cmp[g_]
            cells.append('%s · %s [%s; %s]' % (f(x[0]), f(x[3]), f(x[4]), f(x[5])))
        W('| %s | %s | %s | %s | **%s** |' % (who, lab, ' | '.join(cells), v, vword(v)))
        print('doi chung %s / %s xong %.0fs' % (who, lab, time.time() - t0), flush=True)
    W('')
    x = VER.get(('A-v5 toàn bộ', 'ĐC3 dời cả bản đồ 3–15 giá'))
    if x:
        W('- ĐC3 (dời cả bản đồ): số lệnh/ngày TB %s [%s; %s] (thật %.2f).' % (f(x[2][0], 2, False), f(x[2][1], 2, False), f(x[2][2], 2, False), s5['pday']))
    x = VER.get(('riêng lệnh VCL', 'ĐC3-chỉ-dời-VCL'))
    if x:
        W('- ĐC3-chỉ-dời-VCL: số lệnh VCL/ngày TB %s [%s; %s] (thật %.2f).' % (f(x[2][0], 2, False), f(x[2][1], 2, False), f(x[2][2], 2, False), sv_all['pday']))
    for who, lab in (('A-v5 toàn bộ', 'ĐC1 cùng trạng thái'), ('riêng lệnh VCL', 'ĐC1-VCL')):
        if (who, lab) in VER:
            W('- %s — %s: hồ ĐC1 = %d nến.' % (who, lab, VER[(who, lab)][2]))
    W('')
    # ------------------------------------------------------------ 7 độ nhạy
    W('## 7. Độ nhạy quanh A-v5 — đổi MỘT thứ một lần, IN RA, KHÔNG chọn lại')
    W('')
    W('| biến thể | n | lệnh/ngày | WR | R TB [KTC 95%] | TRAIN n / R | TEST n / R | số lệnh VCL |')
    W('|---|---|---|---|---|---|---|---|')

    def srow(lab, r_):
        s = A4.summ(P, r_['ents'], r_['tr'])
        nv = int((r_['c']['zbase'] == 'VCL').sum()) if len(r_['c']) else 0
        W('| %s | %d | %.2f | %s | %s [%s; %s] | %s | %s | %d |' % (lab, s['n'], s['pday'], pc(s['wr']), f(s['m']), f(s['lo']), f(s['hi']), nr(s['TRAIN']), nr(s['TEST']), nv))
    srow('**A-v5 ô chính**', R5)
    srow('S1 bỏ luật cú phá thật (máy v4 nguyên xi trên VCL)', run5(P, V, real_break=False))
    srow('S2 SL vùng VCL qua cạnh gần (E ∓ 1 + 0,3)', run5(P, V, vcl_slfar=False))
    srow('S3 bỏ khoá mức giá', run5(P, V, lock=False))
    srow('S4 TP 2R (không gộp vào kết luận)', run5(P, V, rr=RR2))
    srow('S5 chỉ vùng VCL KHÔNG trùng vùng v4 (bỏ tín hiệu VCL trùng trước luật 1 lệnh mở)', run5(P, V, drop_overlap=True))
    srow('(tham chiếu) A-v4 — VCL tắt', d4)
    W('')
    print('do nhay xong %.0fs' % (time.time() - t0), flush=True)
    # ------------------------------------------------------------ 8 T1/T2
    W('## 8. Tiêu chí "đáng port C#" (đăng ký trước, plan mục 4) — chấm tự động')
    W('')
    vers = {lab: VER[(who, lab)][0] for (who, lab) in VER}
    worse = [lab for lab, v in vers.items() if v.startswith('KHÁC đối chứng ▼')]
    better_all = [lab for (who, lab), x in VER.items() if who == 'A-v5 toàn bộ' and x[0].startswith('KHÁC đối chứng ▲')]
    eve_bad = s5['eve']['n'] >= MIN_N and (s5['eve']['m'] - s5['not_eve']['m']) < -T1_EVE_GAP
    net = s5['n'] - s4['n']
    c8_tr = sv_all['TRAIN']['m'] >= sx_all['TRAIN']['m'] - mde_vx['TRAIN']
    c8_te = sv_all['TEST']['m'] >= sx_all['TEST']['m'] - mde_vx['TEST']
    t1 = [('(1) n(A-v5) ≥ %d' % T1_N, s5['n'] >= T1_N, 'n = %d' % s5['n']),
          ('(2) R TB TEST(A-v5) ≥ %.2f và n TEST ≥ %d' % (T1_TEST_REF, T1_N_TEST), s5['TEST']['m'] >= T1_TEST_REF and s5['TEST']['n'] >= T1_N_TEST,
           'R TEST = %s, n TEST = %d (R TEST của A cũ đo lại = %s, n = %d)' % (f(s5['TEST']['m']), s5['TEST']['n'], f(g['TEST']['m']), g['TEST']['n'])),
          ('(3) R TB TRAIN(A-v5) ≥ %.2f' % T1_TRAIN_MIN, s5['TRAIN']['m'] >= T1_TRAIN_MIN, 'R TRAIN = %s' % f(s5['TRAIN']['m'])),
          ('(4) không đối chứng nào (6 phép) ra "thật kém hơn"', (not worse) and len(vers) == 6, '; '.join('%s: %s' % (k, vword(v)) for k, v in vers.items()) + ('' if len(vers) == 6 else ' (thiếu phép, chạy --fast)')),
          ('(5) test 3.6 xanh, tái tạo 3.0 đúng', tests_ok, tp.stdout.strip().splitlines()[-1] if tp.stdout.strip() else tp.stderr[-200:]),
          ('(6) 18:00–19:20 không tệ hơn phần còn lại > %.1fR (n ≥ 10)' % T1_EVE_GAP, not eve_bad, 'n = %d, R %s vs phần còn lại %s' % (s5['eve']['n'], f(s5['eve']['m']), f(s5['not_eve']['m']))),
          ('(7) VCL thêm ròng ≥ +%d lệnh (≥ +0,5/ngày)' % T1_VCL_NET, net >= T1_VCL_NET, 'n(A-v5) − n(A-v4) = %+d (%+.2f/ngày); lệnh VCL = %d' % (net, net / P.days, sv_all['n'])),
          ('(8) R TB lệnh VCL ≥ R TB lệnh v4 trừ hiệu nhỏ nhất phát hiện được, ở CẢ TRAIN và TEST', c8_tr and c8_te,
           'TRAIN: VCL %s vs v4 %s (hiệu nhỏ nhất %s); TEST: VCL %s vs v4 %s (hiệu nhỏ nhất %s)' % (
               f(sv_all['TRAIN']['m']), f(sx_all['TRAIN']['m']), f(mde_vx['TRAIN'], 2, False), f(sv_all['TEST']['m']), f(sx_all['TEST']['m']), f(mde_vx['TEST'], 2, False)))]
    W('| điều kiện T1-v5 | đạt? | số |')
    W('|---|---|---|')
    for lab, ok, txt in t1:
        W('| %s | %s | %s |' % (lab, 'ĐẠT' if ok else '**KHÔNG**', txt))
    T1 = all(ok for _, ok, _ in t1)
    T2 = s5['TRAIN']['m'] > 0 and s5['TEST']['m'] > 0 and s5['TEST']['n'] >= T2_N_TEST and len(better_all) == 3
    fails = [lab for lab, ok, _ in t1 if not ok]
    W('')
    W('- **T1-v5: %s.** %s' % ('ĐẠT' if T1 else 'KHÔNG ĐẠT', ('Điều kiện trượt: ' + '; '.join(fails) + '.') if fails else 'Đủ điều kiện ĐỀ XUẤT port (C# chỉ làm khi người học xác nhận).'))
    W('- **T2: %s** (TRAIN %s, TEST %s, n TEST %d, vượt đối chứng A-v5: %d/3). %s' % (
        'ĐẠT' if T2 else 'KHÔNG ĐẠT', f(s5['TRAIN']['m']), f(s5['TEST']['m']), s5['TEST']['n'], len(better_all),
        '' if T2 else '**Chưa có lợi thế đo được** trên %d phiên.' % P.days))
    W('')
    # ------------------------------------------------------------ 9 so dự đoán
    W('## 9. So với DỰ ĐOÁN ĐĂNG KÝ TRƯỚC của Opus (plan 3.7)')
    W('')
    pred = [('Số lệnh tăng rõ: A-v5 ≈ 300–450 (≈ 5–7,5/ngày), VCL thêm ≈ +80…+230 sau khi trừ lệnh A-v4 bị chen', '%d lệnh (%.2f/ngày); VCL thêm ròng %+d (lệnh VCL %d, A-v4 mất %d, v4 mới %d)' % (
        s5['n'], s5['pday'], net, sv_all['n'], len(lost), len(new4)), 300 <= s5['n'] <= 450 and 80 <= net <= 230),
        ('WR không tăng: A-v5 17–22% (A-v4 19,7%)', '%s (%+.1f điểm so A-v4)' % (pc(s5['wr']), 100 * (s5['wr'] - s4['wr'])), 0.17 <= s5['wr'] <= 0.22),
        ('R TB −0,20 … −0,45', f(s5['m']), -0.45 <= s5['m'] <= -0.20),
        ('lệnh VCL và lệnh vùng v4 chênh nhỏ hơn mức phát hiện được', 'VCL %s · v4 %s · hiệu nhỏ nhất phát hiện được %s' % (f(sv_all['m']), f(sx_all['m']), f(mde_vx['ALL'], 2, False)),
         abs(sv_all['m'] - sx_all['m']) < mde_vx['ALL']),
        ('cả 6 phép so ≈ (không hơn)', ', '.join('%s: %s' % (k, vword(v)) for k, v in vers.items()), len(vers) == 6 and all(vword(v) == 'không hơn' for v in vers.values())),
        ('T1 không đạt', 'T1 %s' % ('ĐẠT' if T1 else 'KHÔNG ĐẠT'), not T1)]
    W('| dự đoán | đo được | đúng? |')
    W('|---|---|---|')
    for a_, b_, ok in pred:
        W('| %s | %s | %s |' % (a_, b_, 'ĐÚNG' if ok else '**SAI**'))
    W('')
    ev = os.path.join(REPORT, '_eval_a_v5.txt')
    if os.path.exists(ev):
        W('## 10. Đánh giá (viết tay sau khi đọc số — `report/_eval_a_v5.txt`)')
        W('')
        with open(ev, encoding='utf-8') as fh:
            W(fh.read())
    W('')
    W('_Thời gian chạy toàn bộ: %.0f giây._' % (time.time() - t0))
    # ------------------------------------------------------------ 4 dòng dưới bảng chính
    dv = VER.get(('A-v5 toàn bộ', 'ĐC1 cùng trạng thái'))
    three = [vword(VER[('A-v5 toàn bộ', l_)][0]) if ('A-v5 toàn bộ', l_) in VER else 'chưa chạy' for l_ in ('ĐC1 cùng trạng thái', 'ĐC2 control_sample', 'ĐC3 dời cả bản đồ 3–15 giá')]
    threev = [vword(VER[('riêng lệnh VCL', l_)][0]) if ('riêng lệnh VCL', l_) in VER else 'chưa chạy' for l_ in ('ĐC1-VCL', 'ĐC2-VCL', 'ĐC3-chỉ-dời-VCL')]
    out[idx_lines] = ('1. Lệnh VCL thêm: **%+d** lệnh (%+.2f/ngày) so với A-v4 (%+d so với A cũ); lệnh VCL riêng: %d lệnh, WR %s, R TB %s; lệnh A-v4 bị chen mất: %d.' % (
        net, net / P.days, s5['n'] - g['n'], sv_all['n'], pc(sv_all['wr']), f(sv_all['m']), len(lost)))
    out[idx_lines + 1] = '2. Đối chứng A-v5 (ĐC1 / ĐC2 / ĐC3): **%s / %s / %s**.' % tuple(three)
    out[idx_lines + 2] = '3. Đối chứng riêng lệnh VCL (ĐC1-VCL / ĐC2-VCL / ĐC3-chỉ-dời-VCL): **%s / %s / %s**.' % tuple(threev)
    out[idx_lines + 3] = '4. T1-v5: **%s**%s; T2: **%s**.' % ('đạt' if T1 else 'không đạt', (' (trượt: ' + '; '.join(fails) + ')') if fails else '', 'đạt' if T2 else 'không đạt')
    with open(os.path.join(REPORT, 'RESULTS-A-V5.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out) + '\n')
    print('ghi report/RESULTS-A-V5.md (%.0fs); T1=%s T2=%s' % (time.time() - t0, T1, T2))
    return dict(P=P, V=V, R5=R5, d4=d4, s5=s5, s4=s4, g=g, VER=VER, T1=T1, T2=T2, lost=lost, new4=new4, sv=sv_all, sx=sx_all, vf=vf)


if __name__ == '__main__':
    main(fast='--fast' in sys.argv)
