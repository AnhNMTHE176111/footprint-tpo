# -*- coding: utf-8 -*-
"""Test vòng "lần chạm": (1) máy trạng thái từng ca (neo nhiều nến, râu quét, phá giả, gộp khi chạm lại, chốt đúng nến thứ G,
hết phiên, vùng rời bộ, không rõ phía, xuyên phá, nến nhảy qua vùng, hết dữ liệu, nhiều bản = chạy riêng), (2) kẹp [2, 5] giá,
(3) KHÔNG NHÌN TRƯỚC cho engine v5 và cho máy trạng thái (cắt dữ liệu tại i).
Chạy: python3 -m pytest test_lan_cham.py   hoặc   python3 test_lan_cham.py"""
import numpy as np
import pandas as pd
import vcl5 as V5
import lan_cham as LC

LO, HI = 100.0, 102.0          # vùng mẫu: rộng 2 giá ⇒ lân cận [98, 104]


def mk(bars, sess=None):
    """bars = [(O, H, L, C)], sess = chỉ số nến bắt đầu phiên mới (ngoài nến 0)."""
    a = np.array(bars, float)
    sno = np.zeros(len(a), int)
    for s in (sess or []):
        sno[s:] += 1
    df = pd.DataFrame(dict(open=a[:, 0], high=a[:, 1], low=a[:, 2], close=a[:, 3], session_no=sno))
    return LC.bar_arrays(df)


def rec_of(n_bars, eid=7, lo=LO, hi=HI, start=0, end=None):
    end = n_bars - 1 if end is None else end
    b = np.arange(start, end + 1)
    return pd.DataFrame(dict(bar=b, lo=lo, hi=hi, eid=eid, score=1.0))


def flat(c, h=None, l=None):
    return (c, c + 0.3 if h is None else h, c - 0.3 if l is None else l, c)


def run(bars, rec=None, sess=None, **kw):
    B = mk(bars, sess)
    rec = rec_of(len(bars)) if rec is None else rec
    ep, r, tr = LC.episodes(B, rec, trace=True, **kw)
    ep['_o'] = np.where(ep['chot'] < 0, 10 ** 9, ep['chot'])                       # ca hết dữ liệu (chot = −1) xếp cuối
    return ep.sort_values(['_o', 'bat_dau']).drop(columns='_o').reset_index(drop=True), r, tr


# ------------------------------------------------------------------ máy trạng thái
def test_neo_nhieu_nen_roi_dao():
    bars = [flat(96), flat(97), (97, 100.3, 96.8, 99.5)] + [flat(100.5)] * 7 + [(100.5, 101, 97, 97.5)] + [flat(97)] * 6
    ep, _, tr = run(bars)
    assert len(ep) == 1
    e = ep.iloc[0]
    assert e['vai'] == LC.KC and e['ket'] == LC.DAO and e['bat_dau'] == 2
    # nến 10 đi từ trong vùng xuống 97,5: "cầu" C₋→nến vẫn chạm vùng ⇒ thoát tính từ nến 11; chốt ở nến 15 (5 nến yên)
    assert e['thoat_cuoi'] == 11 and e['chot'] == 15 and e['dwell'] == 9 and e['ly_do'] == LC.LD_G
    assert list(tr['dem_thoat'][10:16]) == [0, 1, 2, 3, 4, 0] and tr['ep_open'][14] == 1 and tr['ep_open'][15] == 0
    assert tr['n'][15] == 1 and tr['dao'][15] == 1


def test_rau_quet_dong_xa_2_gia_la_1_lan_dao():
    bars = [flat(96), (96, 100.2, 95.8, 96.5)] + [(96.5, 97, 96, 96.2)] * 5
    ep, _, _ = run(bars)
    assert len(ep) == 1 and ep['ket'][0] == LC.DAO and ep['vai'][0] == LC.KC and ep['bat_dau'][0] == 1
    assert ep['chot'][0] == 6 and ep['dwell'][0] == 1


def test_pha_gia_la_1_lan_dao():
    bars = [flat(96), (96, 100.5, 96, 100.5)] + [flat(101)] * 3 + [flat(105.0)] * 3 + [flat(101)] * 2 + \
           [(101, 101.5, 97, 97.4)] + [flat(97)] * 6
    ep, _, _ = run(bars)
    assert len(ep) == 1 and ep['ket'][0] == LC.DAO and ep['vai'][0] == LC.KC


def test_thoat_roi_cham_lai_nen_thu_3_thi_gop():
    bars = [flat(96), (96, 100.5, 96, 100.5), flat(101), (101, 101, 97, 97.5), flat(97), flat(97),
            (97, 100.1, 96.9, 97.2)] + [flat(97)] * 6
    ep, _, tr = run(bars)
    assert len(ep) == 1 and ep['ket'][0] == LC.DAO
    assert tr['dem_thoat'][5] == 2 and tr['dem_thoat'][6] == 0                     # nến 6 râu chạm lại ⇒ bộ đếm về 0


def test_chot_dung_nen_thu_G():
    bars = [flat(96), (96, 100.2, 95.8, 96.5)] + [flat(96.2)] * 4
    ep, _, tr = run(bars)
    assert len(ep) == 1 and ep['ket'][0] == LC.HDL                                  # mới 4 nến yên + hết dữ liệu ⇒ bỏ
    ep, _, _ = run(bars + [flat(96.2)])
    assert ep['ket'][0] == LC.DAO and ep['chot'][0] == 6
    ep, _, _ = run(bars + [flat(96.2)] * 5, G=10)                                   # G = 10 ⇒ 9 nến yên chưa chốt
    assert ep['ket'][0] == LC.HDL


def test_het_phien_khi_neo_la_chua_ro_va_khi_da_thoat_la_chot_theo_phia():
    bars = [flat(96), (96, 100.5, 96, 100.5), flat(101), flat(101), flat(101.2)]
    ep, _, _ = run(bars, sess=[4])
    assert ep['ket'][0] == LC.CHUA_RO and ep['ly_do'][0] == LC.LD_HP and ep['chot'][0] == 4
    # đã thoát tạm 2 nến (lên trên 104 ⇒ vai kháng cự tới từ dưới ⇒ XUYÊN) rồi hết phiên
    bars = [flat(96), (96, 100.5, 96, 100.5), flat(101), (101, 105, 101, 105), flat(105.5), flat(105.5), flat(105.0)]
    ep, _, _ = run(bars, sess=[6])
    assert ep['ket'][0] == LC.XUYEN and ep['ly_do'][0] == LC.LD_HP and ep['thoat_cuoi'][0] == 4
    # nến đầu phiên mới: C₋ := O của chính nó (không dùng giá đóng phiên trước)
    bars = [flat(96)] * 3 + [(101, 101.5, 100.5, 101)]
    ep, _, _ = run(bars, sess=[3])
    assert len(ep) == 1 and ep['vai'][0] == LC.KR and ep['ket'][0] == LC.HDL


def test_vung_roi_bo():
    bars = [flat(96), (96, 100.5, 96, 100.5), flat(101), (101, 101, 97, 97.4), flat(97), flat(97), flat(97), flat(97)]
    ep, _, _ = run(bars, rec=rec_of(len(bars), end=5))                             # vùng mất khỏi bộ sau nến 5 (đã thoát 2 nến)
    assert ep['ket'][0] == LC.DAO and ep['ly_do'][0] == LC.LD_RB and ep['chot'][0] == 6
    ep, _, _ = run(bars, rec=rec_of(len(bars), end=2))                             # mất khi đang neo
    assert ep['ket'][0] == LC.CHUA_RO and ep['ly_do'][0] == LC.LD_RB and ep['chot'][0] == 3


def test_khong_ro_phia():
    bars = [flat(101), flat(101.2), flat(101.1)] + [flat(110)] * 6
    ep, _, _ = run(bars)
    assert len(ep) == 1 and ep['vai'][0] == LC.KR and ep['ket'][0] == LC.KRP
    # vai KHÔNG RÕ chốt do hết phiên khi đang neo vẫn là "không rõ phía" (4 nhóm rời nhau)
    ep, _, _ = run([flat(101)] * 3 + [flat(90)], sess=[3])
    assert ep['ket'][0] == LC.KRP


def test_xuyen_pha_va_doi_vai():
    # tới từ trên (hỗ trợ), xuyên xuống dưới 98 ⇒ XUYÊN; lần sau tới từ dưới ⇒ vai kháng cự (tự đổi vai)
    bars = [flat(106), (106, 106, 101.5, 101.5), flat(101), (101, 101, 97, 97.4)] + [flat(97)] * 6 + \
           [(97, 100.4, 97, 99.8)] + [flat(99.5)] * 2 + [flat(95)] * 6
    ep, _, _ = run(bars)
    assert len(ep) == 2
    assert ep['vai'][0] == LC.HT and ep['ket'][0] == LC.XUYEN
    assert ep['vai'][1] == LC.KC and ep['ket'][1] == LC.DAO


def test_nen_nhay_qua_vung():
    bars = [flat(97), (97, 106.5, 96.9, 106)] + [flat(107)] * 5
    ep, _, _ = run(bars)
    assert len(ep) == 1 and ep['vai'][0] == LC.KC and ep['ket'][0] == LC.XUYEN and ep['dwell'][0] == 1 and ep['chot'][0] == 6


def test_nhieu_ban_bang_chay_rieng():
    rng = np.random.default_rng(3)
    c = 100 + np.cumsum(rng.normal(0, 0.8, 600))
    bars = [(c[i - 1] if i else c[0], max(c[i - 1] if i else c[0], c[i]) + 0.3, min(c[i - 1] if i else c[0], c[i]) - 0.3, c[i])
            for i in range(600)]
    B = mk(bars, sess=[300])
    rec = pd.concat([rec_of(600, eid=1, lo=99, hi=101.5), rec_of(600, eid=2, lo=104, hi=107, start=50, end=420)], ignore_index=True)
    off = rng.uniform(-6, 6, (len(rec), 3))
    ep, _, _ = LC.episodes(B, rec, off=off)
    for k in range(3):
        r2 = rec.copy()
        r2['lo'] += off[:, k]
        r2['hi'] += off[:, k]
        e1, _, _ = LC.episodes(B, r2)
        a = ep[ep['rep'] == k].drop(columns='rep').sort_values(['eid', 'chot', 'bat_dau']).reset_index(drop=True)
        b = e1.drop(columns='rep').sort_values(['eid', 'chot', 'bat_dau']).reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b, check_dtype=False)


def test_bat_bien_tong_100():
    rng = np.random.default_rng(5)
    c = 100 + np.cumsum(rng.normal(0, 1.0, 3000))
    bars = [(c[i - 1] if i else c[0], max(c[i - 1] if i else c[0], c[i]) + 0.4, min(c[i - 1] if i else c[0], c[i]) - 0.4, c[i])
            for i in range(3000)]
    rec = rec_of(3000, lo=float(np.median(c)), hi=float(np.median(c)) + 3)
    ep, _, _ = run(bars, rec=rec, sess=[1000, 2000])
    assert len(ep) > 5 and set(ep['ket']) <= {LC.DAO, LC.XUYEN, LC.CHUA_RO, LC.KRP, LC.HDL}


# ------------------------------------------------------------------ kẹp [2, 5] giá
def test_kep_2_5_gia():
    rng = np.random.default_rng(1)
    for u in (1.0, 3.1, 0.6, 4.4):
        for _ in range(200):
            p = np.round(4400 + rng.uniform(-30, 30, rng.integers(1, 40)), 1)
            lab, lo, hi = V5.build_zones(p, u, 1.0)
            w = hi - lo
            assert np.all(w >= 2 - 1e-9) and np.all(w <= 5 + 1e-9), (u, w.min(), w.max())
            assert np.all(hi[:-1] <= lo[1:] + 1e-9)                                    # không chồng lấn
            assert lab.min() == 0 and lab.max() == len(lo) - 1
    # u = 6 (> 5): một mức ⇒ kẹp trần về đúng 5 giá quanh mức; nhiều mức TRÙNG giá ⇒ không tách, một vùng 5 giá
    _, lo, hi = V5.build_zones(np.array([100.0]), 6.0, 1.0)
    assert np.isclose(lo[0], 97.5) and np.isclose(hi[0], 102.5)
    lab, lo, hi = V5.build_zones(np.array([100.0, 100.0, 100.0]), 6.0, 1.0)
    assert len(lo) == 1 and np.isclose(hi[0] - lo[0], 5.0) and list(lab) == [0, 0, 0]
    # mức đơn với u = 1 ⇒ nới tới 2 giá; với u = 3,1 ⇒ rộng đúng 3,1 (đệm 0,5u mỗi phía)
    _, lo, hi = V5.build_zones(np.array([50.0]), 1.0, 1.0)
    assert np.isclose(hi[0] - lo[0], 2.0)
    _, lo, hi = V5.build_zones(np.array([50.0]), 3.1, 1.0)
    assert np.isclose(hi[0] - lo[0], 3.1)
    # hai mức cách 1,2 với u = 1: hai vùng 2 giá chồng nhau, hợp = 3,2 < 4 ⇒ GỘP thành 1 vùng
    lab, lo, hi = V5.build_zones(np.array([100.0, 101.2]), 1.0, 1.0)
    assert len(lo) == 1 and np.isclose(lo[0], 99.0) and np.isclose(hi[0], 102.2) and list(lab) == [0, 0]
    # bản "cắt giữa như v4" có thể ra vùng < 2 giá (lý do tự quyết)
    _, lo, hi = V5.build_zones(np.array([100.0, 101.2]), 1.0, 1.0, chong='giua')
    assert len(lo) == 2 and (hi - lo).min() < 2
    # chuỗi dày rộng 10 giá ⇒ tách tại khe lớn nhất, mọi vùng ≤ 5
    p = np.r_[np.arange(0, 5, 0.5), np.arange(5.9, 10.01, 0.5)]
    lab, lo, hi = V5.build_zones(p, 1.0, 1.0)
    assert len(lo) >= 2 and np.all(hi - lo <= 5 + 1e-9) and np.all(hi - lo >= 2 - 1e-9)


# ------------------------------------------------------------------ không nhìn trước (dữ liệu thật 90 ngày)
_D = {}


def _slice():
    """9000 nến từ đầu phiên 2026-08-17 (phiên bình thường, không thin) của file 90 ngày."""
    if not _D:
        bars, lv = V5.load(V5.BASE90)
        d = bars['datetime']
        a = int(np.flatnonzero(d >= '2026-08-16 22:00:00')[0])
        b = bars.iloc[a:a + 9000].reset_index(drop=True)
        l = lv[(lv['bar_idx'] >= b['bar_idx'].iloc[0]) & (lv['bar_idx'] <= b['bar_idx'].iloc[-1])]
        _D['b'], _D['l'] = b, l
    return _D['b'], _D['l']


def _cut(b, l, pos):
    bb = b.iloc[:pos + 1].copy()
    return bb, l[l['bar_idx'] <= bb['bar_idx'].iloc[-1]]


def test_v5_va_lan_cham_khong_nhin_truoc():
    b, l = _slice()
    ctx = V5.prepare(b, l)
    rec_full = V5.run_engine(ctx)['rec']
    B = LC.bar_arrays(ctx['df'])
    ep_full, r_full, tr_full = LC.episodes(B, rec_full, trace=True)
    cols = ['bar', 'lo', 'hi', 'score', 'mask', 'eid', 'side', 'slot']
    for c in (2500, 5521, 7777):
        ctx_c = V5.prepare(*_cut(b, l, c))
        rec_cut = V5.run_engine(ctx_c)['rec']
        a = rec_full[rec_full['bar'] <= c][cols].reset_index(drop=True)
        assert (a['bar'] == c).any()
        pd.testing.assert_frame_equal(a, rec_cut[cols].reset_index(drop=True), check_exact=False, rtol=1e-12, atol=1e-9)
        Bc = LC.bar_arrays(ctx_c['df'])
        ep_cut, r_cut, tr_cut = LC.episodes(Bc, rec_cut, trace=True)
        # mọi lần chạm đã CHỐT tới nến c (gồm ca rời bộ/hết phiên, chốt = nến phát hiện) giống hệt
        k = ['eid', 'vai', 'bat_dau', 'thoat_cuoi', 'chot', 'dwell', 'ket', 'ly_do']
        x = ep_full[(ep_full['ket'] != LC.HDL) & (ep_full['chot'] <= c)][k].sort_values(['eid', 'chot']).reset_index(drop=True)
        y = ep_cut[ep_cut['ket'] != LC.HDL][k].sort_values(['eid', 'chot']).reset_index(drop=True)
        assert len(x) > 20
        pd.testing.assert_frame_equal(x, y, check_dtype=False)
        # trạng thái từng nến từng vùng (đang mở, vai, đếm thoát, lịch sử riêng) tới nến c giống hệt
        mf = r_full['bar'].to_numpy() <= c
        for key in tr_full:
            fa = pd.DataFrame(dict(eid=r_full['eid'][mf], bar=r_full['bar'][mf], v=tr_full[key][mf])).sort_values(['eid', 'bar'])
            fb = pd.DataFrame(dict(eid=r_cut['eid'], bar=r_cut['bar'], v=tr_cut[key])).sort_values(['eid', 'bar'])
            assert (fa['v'].to_numpy() == fb['v'].to_numpy()).all(), key


if __name__ == '__main__':
    for f in [v for k_, v in list(globals().items()) if k_.startswith('test_')]:
        f()
        print('OK', f.__name__)
