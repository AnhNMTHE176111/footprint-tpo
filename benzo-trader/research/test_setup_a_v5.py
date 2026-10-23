# -*- coding: utf-8 -*-
"""Test setup A-v5 (plan BENZO-A-V5 mục 3.0 và 3.6). Chạy: python3 -m pytest test_setup_a_v5.py -q
1. Điều kiện tiên quyết (3.0): (1) A cũ qua máy mới n=20, WR 10%, R −0,68, khớp từng lệnh setup_a_pha_hoi.detect(expire=30);
   (2) detect5 với tập VCL RỖNG (None và VclSet rỗng) ra ĐÚNG từng lệnh của setup_a_v4.detect cấu hình (d): n=218, WR 19,7%, R −0,30,
   TRAIN 119 / TEST 99; (3) phiên 2026-09-08 và 2026-10-02: vòng lặp thưa == vòng lặp dày (có VCL).
2. Không nhìn trước: cắt dữ liệu ở >= 5 vị trí (giữa phiên; ngay sau 19:00 VN; ngay sau đổi tuần; giữa nhịp hồi của một lệnh VCL; ngay sau
   nến M5 phá một vùng VCL) — detect5(cắt, rec[bar <= i]) cho ĐÚNG các lệnh idx <= i của bản đầy đủ.
3. Ca tổng hợp (vùng VCL dựng tay): giá ở trong rồi M5 đóng trên ⇒ mở; vùng sinh ra trong chân cú phá ⇒ không mở; giá ở dưới vùng
   rồi M5 đóng dưới ⇒ không mở (vùng v4: mở); eid vắng ở nến quét ⇒ không vào; eid vắng ở M5 ⇒ hủy roi_bo; phá lên E = hi, SL qua lo − 1 − 0,3;
   vùng rộng 4 giá ⇒ trần SL loại; phá lên rồi M5 đóng dưới lo ⇒ hủy +1 và mở −1 cùng nến; VCL và VWAP_D cùng khoảng cách ⇒ VWAP_D;
   mức đã có 2 tín hiệu ⇒ VCL thứ 3 bị khoá, v4 thứ 3 vẫn vào; khoá đếm theo VCL_<eid>; cạnh động (biên nhích) không hủy trạng thái.
Luật 'không nhìn trước' của chính bộ vùng VCL đã có test riêng `vung-canh-lenh/research/test_lan_cham.py::test_v5_va_lan_cham_khong_nhin_truoc`
(chạy lại, không viết lại).
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import setup_a_v4 as A4  # noqa: E402
import setup_a_v5 as A5  # noqa: E402
import zones_a_v5 as ZV  # noqa: E402
import test_setup_a_v4 as T4  # noqa: E402  (make_P, pz, path)

_cache = {}


def full():
    if not _cache:
        raw = pd.read_csv(A4.D90 + '_bars.csv', parse_dates=['datetime'])
        lv = pd.read_csv(A4.D90 + '.csv', usecols=['bar_idx', 'price', 'volume'])
        df = K._enrich(raw)
        prof = K.build_profiles(df, lv)
        P = A4.Prep(df, prof, lv)
        rec = ZV.load_rec_checked(P)
        V = ZV.VclSet(rec, len(df))
        _cache.update(raw=raw, lv=lv, P=P, rec=rec, V=V)
    return _cache


def key6(x):
    return (x['idx'], x['side'], x['entry'], x['sl'], x['tp'], x['zone'])


# ------------------------------------------------------------------------------------------ 1. tiên quyết 3.0
def test_prereq_1_a_cu_qua_may_moi():
    import setup_a_pha_hoi as SA
    P = full()['P']
    e = A5.detect5(P, P.zones('old'), None, logic='v3', ban=True)
    D = SA.Data(SA.D90)
    e0 = SA.detect(D.df, D.zc, D.m5, 3, 0.5, expire=30)
    k5 = lambda x: (x['idx'], x['side'], x['entry'], x['sl'], x['tp'])  # noqa: E731
    assert [k5(x) for x in e] == [k5(x) for x in e0]
    s = K._stats(K.simulate(P.df, e))
    assert s['n'] == 20 and abs(s['wr'] - 0.10) < 1e-9 and round(s['avg_r'], 2) == -0.68


def _empty_vset(n):
    rec = pd.DataFrame(dict(bar=np.zeros(0, int), lo=np.zeros(0), hi=np.zeros(0), score=np.zeros(0), mask=np.zeros(0, int),
                            conf=np.zeros(0, int), ncand=np.zeros(0, int), eid=np.zeros(0, int), side=np.zeros(0, int),
                            slot=np.array([], dtype=object), d10=np.zeros(0, bool)))
    return ZV.VclSet(rec, n)


def test_prereq_2_a_v4_khop_tung_lenh_khi_tat_vcl():
    c = full()
    P = c['P']
    Z = P.zones('new')
    e4 = A4.detect(P, Z, logic='mom')
    for vcl in (None, _empty_vset(len(P.df))):
        e5 = A5.detect5(P, Z, vcl, logic='mom')
        assert [key6(x) for x in e4] == [key6(x) for x in e5]
        # mọi trường của lệnh v4 giống hệt (trừ cờ vcl thêm)
        for a_, b_ in zip(e4, e5):
            assert all(a_[k] == b_[k] for k in a_), (a_, b_)
    tr = A4.sim(P, e4)
    cl_ = A4.closed(tr)
    r = cl_['r'].to_numpy(float)
    assert len(cl_) == 218 and abs((r > 0).mean() - 0.197) < 0.0006 and round(r.mean(), 2) == -0.30
    assert (cl_['split'] == 'TRAIN').sum() == 119 and (cl_['split'] == 'TEST').sum() == 99


def test_prereq_3_thua_bang_day_hai_phien():
    c = full()
    P, V = c['P'], c['V']
    Z = P.zones('new')
    sess = [int(P.st.index[P.st['session_id'].str[:10] == d][0]) for d in ('2026-09-08', '2026-10-02')]
    f1, f2, l1, l2 = {}, {}, {}, {}
    a_ = A5.detect5(P, Z, V, only=set(sess), vfunnel=f1, vlog=l1)
    b_ = A5.detect5(P, Z, V, only=set(sess), vfunnel=f2, vlog=l2, dense=True)
    assert len(a_) > 0 and sum(1 for x in a_ if x['vcl']) > 0, 'hai phien phai co lenh VCL de test co nghia'
    assert [key6(x) for x in a_] == [key6(x) for x in b_]
    assert a_ == b_                                              # mọi trường của từng lệnh
    for k in ('open', 'armed', 'with_entry', 'cancel', 'expire', 'end', 'roi_bo', 'khong_pha_that', 'm5_ngoai_thu', 'm5_ngoai_tat_ca',
              'kpt_vang', 'kpt_het60', 'kpt_dau_phien', 'cf_ok', 'khoa_muc', 'thua_tranh', 'chon'):
        assert f1[k] == f2[k], k
    assert l1['roi_bo'] == l2['roi_bo']


def test_vclset_bat_khop_chuoi_nen_va_eid_khong_lien_tuc():
    c = full()

    class Fake:
        df = c['P'].df.iloc[:-1]
    with pytest.raises(ValueError):
        ZV.load_rec_checked(Fake)
    rec = pd.DataFrame(dict(bar=[1, 2, 4], lo=[1.0] * 3, hi=[2.0] * 3, score=1.0, mask=0, conf=1, ncand=1, eid=[0, 0, 0], side=1,
                            slot=['N'] * 3, d10=False))
    with pytest.raises(ValueError):
        ZV.VclSet(rec, 10)


# ------------------------------------------------------------------------------------------ 2. không nhìn trước
def _cut_pos(df, sno, lo, hi):
    m = (df['session_no'].to_numpy() == sno) & (df['sm'].to_numpy() >= lo) & (df['sm'].to_numpy() < hi)
    return int(np.flatnonzero(m)[0])


def test_no_lookahead_cut():
    c = full()
    P, raw, lv, rec = c['P'], c['raw'], c['lv'], c['rec']
    df = P.df
    Z = P.zones('new')
    vf = A5.ZV.VclSet(rec, len(df))
    ef = A5.detect5(P, Z, vf)
    vclf = [e for e in ef if e['vcl']]
    assert len(vclf) > 20
    st = P.st
    cuts = [_cut_pos(df, 30, 300, 301),                                      # giữa phiên (10:00 VN)
            _cut_pos(df, 45, 841, 846),                                      # ngay sau 19:00 VN
            int(st['start_pos'].loc[st.index[st['week_no'] == 8][0]]) + 40,  # ngay sau đổi tuần
            ]
    mid = [e for e in vclf if e['idx'] - e['pk_pos'] >= 6]
    cuts.append(int(mid[len(mid) // 2]['pk_pos']) + 3)                      # giữa nhịp hồi của một lệnh VCL
    cuts.append(int(vclf[len(vclf) // 3]['p0']))                             # ngay sau nến M5 phá một vùng VCL (nến M5 phá vừa đóng)
    cuts.append(int(vclf[2 * len(vclf) // 3]['p0']) + 1)                     # ngay sau nến kế tiếp
    assert len(set(cuts)) >= 5
    for i in cuts:
        dfc = K._enrich(raw.iloc[:i + 1])
        dfc['thin'] = df['thin'].to_numpy()[:i + 1]
        dfc['splice'] = df['splice'].to_numpy()[:i + 1]
        lvc = lv[lv['bar_idx'] <= raw['bar_idx'].iloc[i]]
        Pc = A4.Prep(dfc, K.build_profiles(dfc, lvc), lvc)
        Zc = Pc.zones('new')
        Vc = ZV.VclSet(rec[rec['bar'] <= i], i + 1)
        ec = A5.detect5(Pc, Zc, Vc)
        a = [(e['idx'], e['side'], e['zone'], e['entry'], e['sl'], e['tp']) for e in ef if e['idx'] <= i]
        b = [(e['idx'], e['side'], e['zone'], e['entry'], e['sl'], e['tp']) for e in ec]
        assert a == b, (i, set(a) ^ set(b))


# ------------------------------------------------------------------------------------------ 3. ca tổng hợp
def vrec(n, zones):
    """zones = list of (eid, b_first, b_last, lo, hi) (lo, hi có thể là mảng theo nến); trả DataFrame rec giống VCL."""
    rows = []
    for eid, b0, b1, lo, hi in zones:
        for b in range(b0, b1 + 1):
            rows.append((b, float(lo[b - b0] if hasattr(lo, '__len__') else lo), float(hi[b - b0] if hasattr(hi, '__len__') else hi),
                         1.0, 8, 1, 1, eid, 0, 'K', False))
    return pd.DataFrame(rows, columns=['bar', 'lo', 'hi', 'score', 'mask', 'conf', 'ncand', 'eid', 'side', 'slot', 'd10'])


def run5(R, zones, **kw):
    P = T4.make_P(R)
    n = len(R)
    V = ZV.VclSet(vrec(n, zones), n)
    ents, fn, vf, vl, log = None, {}, {}, {}, []
    Zv4 = kw.pop('Z', [])
    ents = A5.detect5(P, Zv4, V, logic='mom', funnel=fn, vfunnel=vf, vlog=vl, states_log=log, **kw)
    return ents, vf, vl, log, P, V


def test_gia_o_trong_roi_M5_dong_tren_thi_mo_E_la_hi_SL_qua_lo():
    R = T4.path(108.3)
    n = len(R)
    ents, vf, vl, log, P, V = run5(R, [(7, 0, n - 1, 98.5, 100.0)])
    assert len(ents) == 1 and ents[0]['vcl'] and ents[0]['zone'] == 'VCL_7' and ents[0]['side'] == 1
    e = ents[0]
    assert e['p0'] == 34 and e['E'] == 100.0                       # phá lên ⇒ E = hi (mép trên)
    struct = min(P.lo[e['idx']], 98.5 - 1.0)                       # SL qua mép DƯỚI (xa) − 1 − 0,3
    assert e['sl'] == round(np.floor((struct - 0.3) / 0.1 + 1e-9) * 0.1, 6)
    assert e['kpos'] == 30                                         # chân cú phá: nến 30 đóng 100,0 ≤ hi ⇒ nến trong (mở được)
    assert any(x['p0'] == 34 and x['S'] == 1 for x in log)
    assert e['eid'] == 7 and e['slot_k'] == 0 and e['trung'] is False and abs(e['width'] - 1.5) < 1e-9


def test_vung_sinh_ra_trong_chan_cu_pha_thi_khong_mo():
    R = T4.path(108.3)
    n = len(R)
    # vùng chỉ xuất hiện từ nến 32 (giữa chân cú phá 30..34) ⇒ vòng lùi dừng vì vùng vắng
    ents, vf, vl, log, P, V = run5(R, [(7, 32, n - 1, 98.5, 100.0)])
    assert ents == [] and vf['khong_pha_that'] >= 1 and vf['kpt_vang'] >= 1
    assert not any(x['p0'] == 34 for x in log)
    # độ nhạy S1 (bỏ luật) ⇒ máy v4 nguyên xi mở được trạng thái
    ents1, vf1, _, log1, _, _ = run5(R, [(7, 32, n - 1, 98.5, 100.0)], real_break=False)
    assert any(x['p0'] == 34 for x in log1) and len(ents1) == 1


def test_gia_o_duoi_vung_60_nen_roi_M5_dong_duoi_thi_khong_mo_khac_vung_v4():
    # nền 99,5 suốt ~140 nến, vùng VCL [100,5; 102] nằm TRÊN giá ⇒ M5 đóng dưới vùng (out = −1) mà giá chưa từng ở trong
    R = [(99.5, 102.0, 97.0, 99.5)] + [(99.5, 99.7, 99.3, 99.5)] * 139
    n = len(R)
    ents, vf, vl, log, P, V = run5(R, [(3, 0, n - 1, 100.5, 102.0)])
    assert ents == [] and not log
    assert vf['kpt_dau_phien'] >= 1 and vf['kpt_het60'] >= 1 and vf['khong_pha_that'] == vf['kpt_dau_phien'] + vf['kpt_het60'] + vf['kpt_vang']
    # cùng nền nhưng vùng v4 (điểm 100,5 dyn=False): máy v4 MỞ trạng thái (phá xuống) bất kể giá có từng ở trong hay không
    P2 = T4.make_P(R)
    lg = []
    A5.detect5(P2, [T4.pz(n, 100.5)], None, logic='mom', states_log=lg)
    assert len(lg) > 0 and all(x['S'] == -1 for x in lg)


def test_eid_vang_o_nen_quet_khong_vao_va_roi_bo_o_M5():
    R = T4.path(108.3)
    n = len(R)
    ctrl, vf0, _, _, _, _ = run5(R, [(7, 0, n - 1, 98.5, 100.0)])
    assert len(ctrl) == 1
    i_cf = ctrl[0]['idx']
    # cùng dữ liệu nhưng eid biến mất đúng từ nến vào lệnh (liên tục ⇒ không quay lại)
    ents, vf, vl, log, P, V = run5(R, [(7, 0, i_cf - 1, 98.5, 100.0)])
    assert ents == []
    assert vf['roi_bo'] == 1 and any(x['why'] == 'roi_bo' for x in log)
    nxt_m5 = [k for k in range(i_cf, n) if P.m5c[k]][0]
    assert vl['roi_bo'][0][0] == 7 and vl['roi_bo'][0][2] == nxt_m5      # hủy ở nến M5 KẾ TIẾP sau khi vắng


def test_vung_rong_4_gia_bi_tran_SL_loai():
    R = T4.path(108.3)
    n = len(R)
    ents, vf, vl, log, P, V = run5(R, [(7, 0, n - 1, 96.0, 100.0)])
    assert ents == [] and vf['no_risk'] >= 1 and vf['cf_ok'] >= 1
    assert all(abs(w - 4.0) < 1e-9 for _, w in vl['norisk'])


def test_pha_len_roi_M5_dong_duoi_lo_huy_cong_mo_tru_cung_nen():
    base = 99.5
    R = [(base, 102.0, 97.0, base)] + [(base, base + 0.2, base - 0.2, base)] * 29
    c = base
    for x in np.linspace(100.0, 101.4, 5):                     # nến 30..34: phá lên (M5 đóng ở 34)
        R.append((c, max(c, x) + 0.1, min(c, x) - 0.1, x))
        c = x
    for x in np.linspace(101.4, 97.5, 6)[1:]:                  # nến 35..39: rơi nhanh xuống dưới lo (M5 đóng ở 39)
        R.append((c, max(c, x) + 0.1, min(c, x) - 0.1, x))
        c = x
    R += [(c, c + 0.1, c - 0.1, c)] * 8
    n = len(R)
    ents, vf, vl, log, P, V = run5(R, [(5, 0, n - 1, 98.5, 100.0)])
    up = [x for x in log if x['S'] == 1 and x['p0'] == 34]
    dn = [x for x in log if x['S'] == -1 and x['p0'] == 39]
    assert len(up) == 1 and up[0]['why'] == 'cancel'
    assert len(dn) == 1                                         # mở −1 ở CÙNG nến M5 (39) sau khi hủy +1
    assert vf['cancel_doi'] == 1


def test_VCL_va_VWAP_D_cung_khoang_cach_thi_VWAP_D_duoc_chon():
    R = T4.path(108.3)
    n = len(R)
    vw = T4.pz(n, 100.0, name='VWAP_D', ztype='VWAP_D', dyn=True, rank=2)
    ents, vf, vl, log, P, V = run5(R, [(7, 0, n - 1, 98.5, 100.0)], Z=[vw])
    assert len(ents) == 1 and ents[0]['zone'] == 'VWAP_D' and not ents[0]['vcl']
    assert vf['thua_tranh'] >= 1                                # VCL có tín hiệu nhưng thua tranh
    ents2, _, _, _, _, _ = run5(R, [(7, 0, n - 1, 98.5, 100.0)])
    assert len(ents2) == 1 and ents2[0]['zone'] == 'VCL_7'


def _cycles(n_cyc):
    R = T4.path(108.3, pb_bars=12, cf=True, tail=0)       # nhịp hồi ngắn để trạng thái VCL (cực trị cũ) chưa hết hạn T_HOI ở chu kỳ 3
    c = R[-1][3]
    for _ in range(n_cyc - 1):
        for k in range(5):
            x = c - 0.12
            R.append((c, c + 0.05, x - 0.05, x, -5))
            c = x
        R.append((c - 0.05, c + 0.6, c - 0.15, c + 0.6, 100))
        c = c + 0.6
    R += [(c, c + 0.1, c - 0.1, c)] * 20
    return R


def test_khoa_muc_VCL_thu_3_bi_khoa_v4_thu_3_van_vao_va_khoa_dem_theo_VCL_eid():
    R = _cycles(3)
    n = len(R)
    hv = T4.pz(n, 100.0, name='HVN_D1', ztype='HVN_D', rank=4)
    # (a) HVN_D1 vào 2 lần (đủ trần 2/(phiên, vùng, chiều)); lần 3 HVN_D1 bị trần theo vùng ⇒ ứng viên VCL (cùng E = 100) bị KHOÁ MỨC
    ents, vf, vl, log, P, V = run5(R, [(9, 0, n - 1, 98.5, 100.0)], Z=[hv])
    zs = [e['zone'] for e in ents]
    assert zs[:2] == ['HVN_D1', 'HVN_D1'] and 'VCL_9' not in zs and vf['khoa_muc'] >= 1, zs
    # tắt khoá (S3) ⇒ lần 3 là VCL_9
    ents3, vf3, _, _, _, _ = run5(R, [(9, 0, n - 1, 98.5, 100.0)], Z=[hv], lock=False)
    assert [e['zone'] for e in ents3][:3] == ['HVN_D1', 'HVN_D1', 'VCL_9'] and vf3['khoa_muc'] == 0
    # (b) tín hiệu v4 thứ 3 cùng mức VẪN vào (không xét khoá): hai vùng v4 cùng E = 100
    vah = T4.pz(n, 100.0, name='VAH_D', ztype='VAH_D', rank=5)
    ents4, _, _, _, _, _ = run5(R, [], Z=[hv, vah])
    z4 = [e['zone'] for e in ents4]
    assert z4[:3] == ['HVN_D1', 'HVN_D1', 'VAH_D'], z4
    # khoá đếm theo mã vùng: VCL_9 đã vào 2 lần (không có vùng v4) ⇒ lần 3 bị trần 2 lệnh theo VCL_9, KHÔNG phải khoá mức
    ents5, vf5, _, _, _, _ = run5(R, [(9, 0, n - 1, 98.5, 100.0)])
    assert [e['zone'] for e in ents5] == ['VCL_9', 'VCL_9'] and vf5['khoa_muc'] == 0
    # hai eid khác nhau cùng mức 100: VCL_9 vào 2 lần; ứng viên VCL_10 ở chu kỳ 3 bị KHOÁ MỨC (khoá nhìn theo mức giá, bất kể mã vùng)
    ents6, vf6, _, _, _, _ = run5(R, [(9, 0, n - 1, 98.5, 100.0), (10, 0, n - 1, 98.5, 100.0)])
    assert [e['zone'] for e in ents6] == ['VCL_9', 'VCL_9'] and vf6['khoa_muc'] >= 1


def test_canh_dong_bien_nhich_khong_huy_trang_thai():
    R = T4.path(108.3)
    n = len(R)
    wob = 100.0 + 0.025 * np.sin(np.arange(n))                  # hi nhích ± 0,025 mỗi nến
    ents, vf, vl, log, P, V = run5(R, [(7, 0, n - 1, 98.5, wob)])
    assert len(ents) == 1
    assert abs(ents[0]['E'] - wob[ents[0]['idx']]) < 1e-9       # E = hi TẠI nến vào (vùng động)
    assert vf['cancel'] == 0


def test_nhan_trung_va_S5_bo_tin_hieu_trung():
    R = T4.path(108.3)
    n = len(R)
    hv = T4.pz(n, 100.4, name='HVN_D1', ztype='HVN_D', rank=4)          # điểm 100,4 trong [lo − 1, hi + 1] của VCL ⇒ "trùng"
    ents, vf, vl, log, P, V = run5(R, [(7, 0, n - 1, 98.5, 100.0)], Z=[hv])
    v = [e for e in ents if e['vcl']]
    assert all(e['trung'] and e['trung_list'] == 'HVN_D' for e in v)
    ents5, vf5, _, _, _, _ = run5(R, [(7, 0, n - 1, 98.5, 100.0)], Z=[hv], drop_overlap=True)
    assert not any(e['vcl'] for e in ents5) and vf5['s5_bo_trung'] >= 1


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-q']))
