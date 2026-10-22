# -*- coding: utf-8 -*-
"""Test VCL vòng 1: (1) không nhìn trước, (2) gộp/kẹp độ rộng, (3) chuyển vai.
Chạy: python3 -m pytest test_vcl.py   hoặc   python3 test_vcl.py"""
import numpy as np
import pandas as pd
import vcl
import vcl2

_DATA = {}


def _data():
    if not _DATA:
        _DATA['bars'], _DATA['lv'] = vcl.load_all()
    return _DATA['bars'], _DATA['lv']


def _cut(bars, lv, pos):
    b = bars.iloc[:pos + 1].copy()
    return b, lv[lv['bar_idx'] <= b['bar_idx'].iloc[-1]]


def test_khong_nhin_truoc():
    """Vùng hiển thị tại nến i giống hệt khi chạy trên dữ liệu bị CẮT tại i (không có nến > i)."""
    bars, lv = _data()
    full_n = 9000                                       # "toàn bộ" = 9000 nến đầu (~6,5 phiên) cho nhanh
    fb, fl = _cut(bars, lv, full_n - 1)
    ctx_full = vcl.prepare(fb, fl)
    rec_full = vcl.run_engine(ctx_full, 1.0)['rec']
    # điểm cắt: giữa phiên, ngay sau khi chốt VA Âu, gần cuối phiên, đầu phiên mới
    sm = ctx_full['df']['sm'].to_numpy()
    eu_ready = int(np.flatnonzero((sm >= 840) & (np.arange(len(sm)) > 4000))[0])
    cuts = [2500, eu_ready, eu_ready + 3, 5519, 5521, 7777]
    cols = ['lo', 'hi', 'score', 'mask', 'conf', 'ncand', 'eid', 'side', 'slot']
    for c in cuts:
        cb, cl = _cut(bars, lv, c)
        rec_cut = vcl.run_engine(vcl.prepare(cb, cl), 1.0)['rec']
        a = rec_full[rec_full['bar'] == c][cols].reset_index(drop=True)
        b = rec_cut[rec_cut['bar'] == c][cols].reset_index(drop=True)
        assert len(a) > 0, c
        pd.testing.assert_frame_equal(a, b, check_exact=False, rtol=1e-12, atol=1e-9, obj=f'vùng tại nến {c}')
        # toàn bộ lịch sử trước c cũng phải trùng
        pd.testing.assert_frame_equal(rec_full[rec_full['bar'] <= c].reset_index(drop=True),
                                      rec_cut.reset_index(drop=True), check_exact=False, rtol=1e-12, atol=1e-9)


def test_ung_vien_khong_nhin_truoc():
    """Mọi ứng viên sinh tại nến <= i khi chạy trên dữ liệu cắt tại i đều có trong bản toàn bộ, cùng giá/thời điểm."""
    bars, lv = _data()
    fb, fl = _cut(bars, lv, 8999)
    full = vcl.gen_candidates(vcl.prepare(fb, fl))
    for c in (3000, 6123):
        cb, cl = _cut(bars, lv, c)
        cut = vcl.gen_candidates(vcl.prepare(cb, cl))
        a = full[full['birth'] <= c][['price', 'kind', 'birth', 'half']].sort_values(['birth', 'kind', 'price']).reset_index(drop=True)
        b = cut[cut['birth'] <= c][['price', 'kind', 'birth', 'half']].sort_values(['birth', 'kind', 'price']).reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b)


def test_gop_va_kep_do_rong():
    u = 1.0
    # 3 mức cách 0,8u ⇒ một vùng (link 1u); đệm 0,5u mỗi bên
    lab, lo, hi = vcl.build_zones(np.array([100.0, 100.8, 101.6]), u, 1.0)
    assert len(lo) == 1 and np.allclose([lo[0], hi[0]], [99.5, 102.1])
    # link 0,7u ⇒ tách thành 3 vùng; mỗi vùng 1 mức ⇒ rộng tối thiểu 1u, chồng lấn cắt ở giữa
    lab, lo, hi = vcl.build_zones(np.array([100.0, 100.8, 101.6]), u, 0.7)
    assert len(lo) == 3 and np.all(hi[:-1] <= lo[1:] + 1e-12)
    # 1 mức đơn ⇒ rộng đúng 1u
    lab, lo, hi = vcl.build_zones(np.array([50.0]), u, 1.0)
    assert np.isclose(hi[0] - lo[0], 1.0)
    # chuỗi dày rộng 10u ⇒ bị tách tại khe lớn nhất cho tới khi mọi vùng <= 4u
    p = np.r_[np.arange(0, 5, 0.5), np.arange(5.9, 10.01, 0.5)]
    lab, lo, hi = vcl.build_zones(p, u, 1.0)
    assert len(lo) >= 3 and np.all(hi - lo <= 4.0 + 1e-9)
    # khe lớn nhất (5,9-4,5 = 1,4u > link) đã tách sẵn; mọi ứng viên thuộc đúng vùng chứa nó
    for k, x in enumerate(p):
        assert lo[lab[k]] - 1e-9 <= x <= hi[lab[k]] + 1e-9


def test_chuyen_vai():
    u = 1.0
    side = np.array([1, -1, 0, 1])
    brk = np.array([0, 0, 0, 1])
    zlo = np.array([100.0, 100.0, 100.0, 100.0])
    zhi = np.array([102.0, 102.0, 102.0, 102.0])
    # đóng 98,9: hỗ trợ bị xuyên >= 1u dưới biên dưới ⇒ thành kháng cự; kháng cự giữ nguyên; chưa rõ ⇒ thành kháng cự
    s2, b2, x = vcl.break_update(side, brk, 98.9, zlo, zhi, u)
    assert list(s2) == [-1, -1, -1, -1] and list(b2) == [1, 0, 0, 2] and list(x) == [True, False, False, True]
    # đóng 99,5: chưa xuyên đủ 1u ⇒ không đổi
    s3, b3, _ = vcl.break_update(side, brk, 99.5, zlo, zhi, u)
    assert list(s3) == [1, -1, -1, 1] and list(b3) == [0, 0, 0, 1]
    # kháng cự bị đóng trên biên trên +1u ⇒ thành hỗ trợ
    s4, b4, _ = vcl.break_update(np.array([-1]), np.array([0]), 103.1, zlo[:1], zhi[:1], u)
    assert s4[0] == 1 and b4[0] == 1


def test_chon_vung_chong_nhap_nhay():
    lo = np.array([90.0, 95.0, 104.0, 108.0, 115.0])
    hi = lo + 2
    score = np.array([1.0, 1.0, 1.0, 1.0, 5.0])
    out = vcl.select_display(lo, hi, score, 100.0, 1.0, 30.0, [])
    zs = sorted(z for z, _, _, _ in out)
    assert 2 in zs and 3 in zs and 4 in zs and 0 in zs and 1 in zs
    # vùng mới gần hơn nhưng điểm 1,1 ≤ 1,2 × 1,0 ⇒ giữ vùng cũ (108)
    lo2 = np.array([90.0, 95.0, 104.0, 106.0, 108.0, 115.0])
    sc2 = np.array([1.0, 1.0, 1.0, 1.1, 1.0, 5.0])
    prev = [(lo[z], hi[z], 100 + z, s) for z, s, _, _ in out]
    out2 = vcl.select_display(lo2, lo2 + 2, sc2, 100.0, 1.0, 30.0, prev)
    near_up = sorted(lo2[z] for z, s, _, sd in out2 if s == 'N' and sd == 1)
    assert near_up == [104.0, 108.0]


# ------------------------------- VÒNG 2 -------------------------------
def test_v2_khong_nhin_truoc():
    """Engine v2 (B/B15/C/D/E top-5/F + chọn theo ô): vùng tại i giống hệt khi dữ liệu bị cắt tại i."""
    bars, lv = _data()
    fb, fl = _cut(bars, lv, 8999)
    rec_full = vcl2.run_engine(vcl.prepare(fb, fl))['rec']
    cols = ['lo', 'hi', 'score', 'mask', 'conf', 'ncand', 'eid', 'side', 'slot', 'erole']
    for c in (2500, 4321, 5519, 5521, 7777):
        cb, cl = _cut(bars, lv, c)
        rec_cut = vcl2.run_engine(vcl.prepare(cb, cl))['rec']
        a = rec_full[rec_full['bar'] <= c][['bar'] + cols].reset_index(drop=True)
        b = rec_cut[['bar'] + cols].reset_index(drop=True)
        assert (a['bar'] == c).any(), c
        pd.testing.assert_frame_equal(a, b, check_exact=False, rtol=1e-12, atol=1e-9, obj=f'v2 tại nến {c}')


def test_v2_ung_vien_khong_nhin_truoc():
    bars, lv = _data()
    fb, fl = _cut(bars, lv, 8999)
    full = vcl2.gen_candidates(vcl.prepare(fb, fl))
    for c in (3000, 6123):
        cb, cl = _cut(bars, lv, c)
        cut = vcl2.gen_candidates(vcl.prepare(cb, cl))
        k = ['price', 'kind', 'birth', 'half', 'erole']
        a = full[full['birth'] <= c].copy()
        b = cut[cut['birth'] <= c].copy()
        # tuổi chết: chỉ so phần đã xảy ra tới c (mức E bị đẩy khỏi top-5 SAU c thì bản cắt chưa biết — đúng)
        a['dead_by_c'] = a['death'] <= c
        b['dead_by_c'] = b['death'] <= c
        a = a[k + ['dead_by_c']].sort_values(['birth', 'kind', 'price']).reset_index(drop=True)
        b = b[k + ['dead_by_c']].sort_values(['birth', 'kind', 'price']).reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b)


def test_v2_dinh_bang_nhau_F():
    n = 200
    H = np.full(n, 100.0)
    L = np.full(n, 90.0)
    u = np.full(n, 1.0)

    def sw(price, pivot, birth, hl=1):
        return dict(price=price, hl=hl, pivot=pivot, birth=birth, death=10 ** 6)
    # hai đỉnh 100,0 và 100,2 cách 40 nến, giữa không vượt ⇒ 1 F ở 100,1
    f = vcl2.find_equal([sw(100.0, 10, 15), sw(100.2, 50, 55)], H, L, u, n)
    assert len(f) == 1 and abs(f[0]['price'] - 100.1) < 1e-9 and f[0]['birth'] == 55 and f[0]['hl'] == 1
    # cách < 30 nến ⇒ không
    assert vcl2.find_equal([sw(100.0, 10, 15), sw(100.2, 35, 40)], H, L, u, n) == []
    # lệch > 0,3u ⇒ không
    assert vcl2.find_equal([sw(100.0, 10, 15), sw(100.4, 50, 55)], H, L, u, n) == []
    # giữa hai đỉnh giá đã vượt lên 101 ⇒ không phải đỉnh bằng nhau
    H2 = H.copy(); H2[30] = 101.0
    assert vcl2.find_equal([sw(100.0, 10, 15), sw(100.2, 50, 55)], H2, L, u, n) == []
    # đỉnh với đáy không ghép; đáy bằng nhau thì ghép
    assert vcl2.find_equal([sw(100.0, 10, 15), sw(100.1, 50, 55, -1)], H, L, u, n) == []
    L2 = np.full(n, 95.0)
    f = vcl2.find_equal([sw(90.0, 10, 15, -1), sw(90.1, 50, 55, -1)], np.full(n, 99.0), np.minimum(L2, 90.0), u, n)
    assert len(f) == 1 and f[0]['hl'] == -1


def test_v2_chon_theo_o():
    lo = np.array([90.0, 96.0, 99.0, 103.0, 106.0, 112.0])
    hi = lo + 2
    sc = np.ones(6)
    # vùng chứa giá (99-101) và vùng có cạnh dưới < c+0,5u (không có ở đây) không được chọn làm "gần nhất"
    sel = vcl2.fresh_select(lo, hi, sc, 100.0, 1.0, 30.0)
    near = sorted(lo[z] for z, s, sd in sel if s == 'N')
    assert 99.0 not in [lo[z] for z, _, _ in sel] and near == [90.0, 96.0, 103.0, 106.0]
    # vùng 100,3-102 phía trên: cạnh dưới 100,3 < 100 + 0,5 ⇒ không chọn
    lo2 = np.array([100.3, 104.0]); sel2 = vcl2.fresh_select(lo2, lo2 + 1, np.ones(2), 100.0, 1.0, 30.0)
    assert [lo2[z] for z, _, _ in sel2] == [104.0]
    # bộ đã chốt ở 100
    out, anc, rc = vcl2.cell_update(lo, hi, sc, 100.0, 1.0, 30.0, [], 0.0)
    assert rc and anc == 100.0
    prev = [(lo[z], hi[z], 10 + k, s, sd) for k, (z, s, _, sd) in enumerate(out)]
    # giá đi 1,5u, chưa chạm cạnh gần nào ⇒ KHÔNG tính lại, giữ đúng eid
    out2, anc2, rc2 = vcl2.cell_update(lo, hi, sc, 101.5, 1.0, 30.0, prev, anc)
    assert not rc2 and anc2 == 100.0 and sorted(e for _, _, e, _ in out2) == sorted(p[2] for p in prev)
    # giá đóng vượt cạnh dưới vùng 103 ⇒ tính lại, vùng 103 bị loại khỏi "gần nhất"
    out3, anc3, rc3 = vcl2.cell_update(lo, hi, sc, 103.2, 1.0, 30.0, prev, anc)
    assert rc3 and anc3 == 103.2 and 103.0 not in [lo[z] for z, _, _, _ in out3]
    # đi >= 2u (xuống 98) ⇒ tính lại
    _, _, rc4 = vcl2.cell_update(lo, hi, sc, 98.0, 1.0, 30.0, prev, anc)
    assert rc4
    # một vùng đang hiển thị chết (không còn vùng nào chồng lấn) ⇒ tính lại
    keep = np.array([0, 1, 2, 4, 5])
    _, _, rc5 = vcl2.cell_update(lo[keep], hi[keep], sc[keep], 100.5, 1.0, 30.0, prev, anc)
    assert rc5


if __name__ == '__main__':
    for f in (test_gop_va_kep_do_rong, test_chuyen_vai, test_chon_vung_chong_nhap_nhay, test_ung_vien_khong_nhin_truoc,
              test_khong_nhin_truoc, test_v2_dinh_bang_nhau_F, test_v2_chon_theo_o, test_v2_ung_vien_khong_nhin_truoc,
              test_v2_khong_nhin_truoc):
        f()
        print('OK', f.__name__)
