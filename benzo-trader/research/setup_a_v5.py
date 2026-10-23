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
