# -*- coding: utf-8 -*-
"""Test VCL vòng 1: (1) không nhìn trước, (2) gộp/kẹp độ rộng, (3) chuyển vai.
Chạy: python3 -m pytest test_vcl.py   hoặc   python3 test_vcl.py"""
import numpy as np
import pandas as pd
import vcl

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


if __name__ == '__main__':
    for f in (test_gop_va_kep_do_rong, test_chuyen_vai, test_chon_vung_chong_nhap_nhay, test_ung_vien_khong_nhin_truoc,
              test_khong_nhin_truoc):
        f()
        print('OK', f.__name__)
