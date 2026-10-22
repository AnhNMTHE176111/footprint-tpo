# -*- coding: utf-8 -*-
"""Test hop_luu_sz: (1) hợp lưu đúng trên ca dựng tay (điểm/dải, dung sai, bán kính 12 giá, mức chưa chốt), (2) dời mức đúng,
(3) "thắng 1:1" đúng trên ca dựng tay, (4) KHÔNG NHÌN TRƯỚC: cắt dữ liệu tại nến c ⇒ mức SessionZones đang dùng được ở mọi nến ≤ c,
VWAP và cờ của mọi vùng hiện ≤ c không đổi.
Chạy: python3 -m pytest test_hop_luu_sz.py   hoặc   python3 test_hop_luu_sz.py"""
import pickle, os
import numpy as np
import pandas as pd
import vcl5 as V5
import lan_cham as LC
import hop_luu_sz as H


def lev_of(rows):
    return pd.DataFrame(rows, columns=['grp', 'start', 'end', 'lo', 'hi', 'c', 'src'])


def flag1(zlo, zhi, lev, grp='VA_EU', b0=10, c0=101.0, sh=0.0, tol=H.TOL):
    return bool(H.static_flag(np.array([b0]), np.array([zlo]), np.array([zhi]), np.array([c0]), np.array([sh]), lev, grp, tol)[0])


# ------------------------------------------------------------------ hợp lưu dựng tay
def test_hop_luu_diem_dung_sai():
    lev = lev_of([('VA_EU', 0, 100, 102.4, 102.4, 102.4, 0)])
    assert flag1(100, 102, lev)                      # 102,4 cách biên trên 0,4 ≤ 0,5
    assert not flag1(100, 102, lev, tol=0.0)         # dung sai 0: không chạm
    assert flag1(100, 102, lev, tol=1.5)
    lev2 = lev_of([('VA_EU', 0, 100, 102.6, 102.6, 102.6, 0)])
    assert not flag1(100, 102, lev2)                 # 0,6 > 0,5
    lev3 = lev_of([('VA_EU', 0, 100, 99.5, 99.5, 99.5, 0)])
    assert flag1(100, 102, lev3) and not flag1(100, 102, lev3, tol=0.4)   # phía dưới, đúng 0,5
    lev4 = lev_of([('VA_EU', 0, 100, 101.0, 101.0, 101.0, 0)])
    assert flag1(100, 102, lev4, tol=0.0)            # mức nằm trong vùng


def test_hop_luu_dai_hvn():
    lev = lev_of([('HVN_D', 0, 100, 102.3, 105.0, 103.0, 0)])
    assert not flag1(100, 102, lev, 'HVN_D', tol=0.0)       # dải bắt đầu 102,3 > 102
    assert flag1(100, 102, lev, 'HVN_D')                     # 102,3 − 0,5 ≤ 102
    lev2 = lev_of([('HVN_D', 0, 100, 95.0, 100.2, 99.0, 0)])
    assert flag1(100, 102, lev2, 'HVN_D', tol=0.0)           # dải phủ biên dưới
    assert not flag1(100, 102, lev2, 'VA_EU')                # nhóm khác ⇒ không


def test_hop_luu_ban_kinh_va_thoi_diem():
    lev = lev_of([('VA_EU', 20, 100, 102.0, 102.0, 102.0, 0)])
    assert not flag1(100, 102, lev, b0=10)                   # mức chưa chốt (start 20 > b0 10)
    assert flag1(100, 102, lev, b0=20) and flag1(100, 102, lev, b0=100)
    assert not flag1(100, 102, lev, b0=101)                  # hết hạn
    assert flag1(100, 102, lev, b0=50, c0=114.0)                  # tâm cách giá 12 giá: còn vẽ
    assert not flag1(100, 102, lev, b0=50, c0=114.5)              # > 12 giá: SessionZones không vẽ ⇒ không cờ


def test_vwap_flag():
    vw = np.array([100.0, 101.0, 102.4, 103.0])
    t = np.array([0, 1, 2, 3])
    lo, hi = np.full(4, 100.0), np.full(4, 102.0)
    assert list(H.vwap_flag(t, lo, hi, vw, 0.0)) == [True, True, True, False]
    assert list(H.vwap_flag(t, lo, hi, vw, 0.0, tol=0.0)) == [True, True, False, False]
    assert list(H.vwap_flag(t, lo, hi, vw, np.array([5.0, 0, 0, -3.0]))) == [False, True, True, True]


# ------------------------------------------------------------------ dời mức
def test_doi_muc():
    d = H.shifts(40, reps=100, seed=1)
    assert d.shape == (40, 100)
    a = np.abs(d)
    assert (a >= 3).all() and (a <= 15).all() and (d > 0).any() and (d < 0).any()
    assert np.array_equal(d, H.shifts(40, reps=100, seed=1))
    # dời qua tham số sh0 == dời tay mọi giá của mức
    rng = np.random.default_rng(0)
    lev = lev_of([('HVN_W', 0, 500, x, x + w, x + w / 2, 0) for x, w in zip(rng.uniform(90, 120, 30), rng.uniform(0, 3, 30))])
    b0 = rng.integers(0, 500, 200)
    zlo = rng.uniform(90, 120, 200)
    zhi = zlo + rng.uniform(2, 5, 200)
    c0 = zlo + rng.uniform(-8, 8, 200)
    sh = rng.choice([-1, 1], 200) * rng.uniform(3, 15, 200)
    f1 = H.static_flag(b0, zlo, zhi, c0, sh, lev, 'HVN_W')
    f2 = np.array([H.static_flag(b0[i:i + 1], zlo[i:i + 1], zhi[i:i + 1], c0[i:i + 1], np.zeros(1),
                                 lev.assign(lo=lev['lo'] + sh[i], hi=lev['hi'] + sh[i], c=lev['c'] + sh[i]), 'HVN_W')[0] for i in range(200)])
    assert np.array_equal(f1, f2) and f1.any() and (~f1).any()


def test_peak_band():
    rows = np.array([10, 11, 12, 13, 14, 16])
    vol = np.array([50, 95, 100, 92, 80, 99])
    assert H.peak_band(rows, vol, 12 * 0.2) == (round(11 * 0.2, 6), round(13 * 0.2, 6))     # 92 ≥ 90, 80 < 90; dừng
    assert H.peak_band(rows, vol, 16 * 0.2) == (3.2, 3.2)                                   # hàng 15 vắng ⇒ không nhảy khe
    assert H.peak_band(rows, vol, 7.0) == (7.0, 7.0)                                        # đỉnh không có trong hàng


# ------------------------------------------------------------------ thắng 1:1
def B_of(bars, sess=None):
    a = np.array(bars, float)
    sno = np.zeros(len(a), int)
    for s in (sess or []):
        sno[s:] += 1
    return LC.bar_arrays(pd.DataFrame(dict(open=a[:, 0], high=a[:, 1], low=a[:, 2], close=a[:, 3], session_no=sno)))


def w1(bars, vai=LC.KC, lo=100.0, hi=102.0, t=1, sess=None):
    return int(H.win11(B_of(bars, sess), np.array([t]), np.array([vai]), np.array([lo]), np.array([hi]))[0])


def f(c, h=None, l=None):
    return (c, c + 0.3 if h is None else h, c - 0.3 if l is None else l, c)


def test_thang_1_1():
    touch = (98, 100.2, 97.8, 99)                          # kháng cự [100, 102] chạm từ dưới, biên gần = 100
    assert w1([f(98), touch, f(98), f(96.5, l=95.9)]) == H.WIN            # xuống 96 trước
    assert w1([f(98), touch, f(101), f(103.5, h=104.0)]) == H.LOSS        # lên 104 trước
    assert w1([f(98), touch, (98, 104.1, 95.5, 99)]) == H.LOSS            # cùng nến chạm cả hai ⇒ thua
    assert w1([f(98), (98, 104.0, 97.8, 99), f(95, l=94)]) == H.LOSS      # ngay nến bắt đầu đã ngược 4 giá
    assert w1([f(98), (98, 100.5, 95.0, 99), f(98)] + [f(98)] * 30) == H.TIMEOUT   # đi đúng hướng TRONG nến t: không tính
    assert w1([f(98), touch] + [f(98)] * 30 + [f(95, l=95.5)]) == H.TIMEOUT      # sau 30 nến: hết giờ
    assert w1([f(98), touch, f(98), f(95, l=94)], sess=[3]) == H.TIMEOUT        # phiên mới: dừng
    sup = (104, 104.2, 101.8, 103)                          # hỗ trợ [100, 102] chạm từ trên, biên gần = 102
    assert w1([f(104), sup, f(105), f(106, h=106.0)], vai=LC.HT) == H.WIN
    assert w1([f(104), sup, f(99, l=98.0)], vai=LC.HT) == H.LOSS
    assert w1([f(101), (101, 101.5, 100.5, 101), f(110)], vai=LC.KR) == H.NOSIDE


# ------------------------------------------------------------------ KHÔNG NHÌN TRƯỚC
def _active(lev, c):
    a = lev[(lev['start'] <= c)]
    return a


def test_khong_nhin_truoc():
    bars, lv = V5.load(V5.BASE90)
    ctx = V5.prepare(bars, lv)
    lev, vw = H.sz_levels(ctx)
    df = ctx['df']
    with open(os.path.join(LC.CACHE, 'v5.pkl'), 'rb') as fh:
        rec = pickle.load(fh)['rec'].reset_index(drop=True)
    sm = df['sm'].to_numpy()
    # 3 nến: ngay trước 19:00 VN, ngay sau 19:00 VN (VA Âu vừa chốt), và đầu một tuần mới (HVN tuần vừa đổi)
    s_ = int(np.flatnonzero((df['session_id'] == '2026-09-23').to_numpy())[0])
    i19 = s_ + int(np.flatnonzero(sm[s_:] >= 840)[0])
    wk = df['week_no'].to_numpy()
    iw = int(np.flatnonzero(wk == wk[-1] - 1)[0]) + 30
    seen = set()
    for c in (i19 - 1, i19, iw):
        b, l = bars.iloc[:c + 1].copy(), lv[lv['bar_idx'] <= bars['bar_idx'].iloc[c]]
        ctx_c = V5.prepare(b, l)
        lev_c, vw_c = H.sz_levels(ctx_c)
        for g in ('VWAP_D', 'VWAP_W'):
            assert np.allclose(vw[g][:c + 1], vw_c[g], rtol=0, atol=1e-9), g
        # mọi mức đang dùng được ở mọi nến ≤ c: giống hệt (so theo từng nến của 600 nến cuối)
        for t in range(max(0, c - 600), c + 1, 7):
            A = lev[(lev['start'] <= t) & (lev['end'] >= t)][['grp', 'lo', 'hi', 'c']].sort_values(['grp', 'c']).reset_index(drop=True)
            Bc = lev_c[(lev_c['start'] <= t) & (lev_c['end'] >= t)][['grp', 'lo', 'hi', 'c']].sort_values(['grp', 'c']).reset_index(drop=True)
            pd.testing.assert_frame_equal(A, Bc, check_exact=False, atol=1e-9)
            seen |= set(A['grp'])
        # cờ của mọi vùng hiện ≤ c
        Z = H.zone_table(rec[rec['bar'] <= c], df)
        for g in H.STATIC:
            args = (Z['b0'].to_numpy(), Z['lo0'].to_numpy(), Z['hi0'].to_numpy(), Z['c0'].to_numpy(), np.zeros(len(Z)))
            assert np.array_equal(H.static_flag(*args, lev, g), H.static_flag(*args, lev_c, g)), g
        # VA Âu: trước 19:00 VN của phiên chưa có VA Âu của chính phiên đó; từ 19:00 thì có
        if c == i19 - 1:
            assert not ((lev_c['grp'] == 'VA_EU') & (lev_c['start'] >= s_)).any()
        if c == i19:
            assert ((lev_c['grp'] == 'VA_EU') & (lev_c['start'] == i19)).sum() == 2
    assert seen == set(H.STATIC), seen                       # các lát cắt thật sự so đủ 4 nhóm mức tĩnh


if __name__ == '__main__':
    for k_, fn in list(globals().items()):
        if k_.startswith('test_'):
            fn()
            print('OK', k_)
