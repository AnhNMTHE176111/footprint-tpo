# -*- coding: utf-8 -*-
"""Test benzo_vcl: (1) cờ "tại vùng VCL" đúng trên ca dựng tay (MUA ↔ hỗ trợ/chứa giá, BÁN ↔ kháng cự/chứa giá, ±1 giá, chọn vùng
gần nhất), (2) dời bản đồ đúng, (3) KHÔNG NHÌN TRƯỚC: cờ tại nến i không đổi khi bỏ mọi dòng vùng sau i; bias 19:00 tại nến i không đổi
khi cắt dữ liệu tại i, (4) neo SL theo vùng (làm tròn ra xa, bỏ SL > 4 giá), (5) ngưỡng phán quyết, (6) cờ theo nến = cờ theo lệnh.
Chạy: python3 -m pytest test_benzo_vcl.py   hoặc   python3 test_benzo_vcl.py"""
import os
import numpy as np
import pandas as pd
import benzo_vcl as BV
import kernel as K


class FakeD:
    """Đủ thuộc tính để gọi BV.flag: zm, dsh, sno, close."""

    def __init__(self, rows, n=10, shift=0.0):
        rec = pd.DataFrame(rows, columns=['bar', 'lo', 'hi', 'eid'])
        self.zm = BV.ZoneMap(rec)
        self.sno = np.zeros(n, int)
        self.dsh = np.array([[0.0, shift]])
        self.close = np.full(n, 100.0)


def m1(D, side, e, i=5, k=0):
    inz, lo, hi = BV.flag(D, np.array([i]), np.array([side]), np.array([e]), k)
    return bool(inz[0]), lo[0], hi[0]


def test_mua_ban_dung_phia():
    D = FakeD([(5, 100.0, 102.0, 1)])
    assert m1(D, 1, 101.0)[0]                 # chứa giá
    assert m1(D, 1, 102.9)[0]                 # vùng dưới giá (hỗ trợ), cách 0,9 ≤ 1
    assert m1(D, 1, 103.0)[0]                 # đúng 1 giá
    assert not m1(D, 1, 103.2)[0]             # cách 1,2 > 1
    assert not m1(D, 1, 99.9)[0]              # vùng TRÊN giá = kháng cự ⇒ không hợp lệ cho MUA
    assert m1(D, -1, 99.1)[0]                 # vùng trên giá (kháng cự), cách 0,9
    assert not m1(D, -1, 98.8)[0]
    assert m1(D, -1, 101.0)[0]                # chứa giá
    assert not m1(D, -1, 102.1)[0]            # vùng DƯỚI giá = hỗ trợ ⇒ không hợp lệ cho BÁN
    assert not m1(D, 1, 101.0, i=6)[0]        # nến khác: không có vùng


def test_chon_vung_gan_nhat():
    D = FakeD([(5, 100.0, 102.0, 1), (5, 101.5, 104.5, 2)])
    ok, lo, hi = m1(D, 1, 102.5)              # vùng 1 cách 0,5 ; vùng 2 chứa giá ⇒ vùng 2
    assert ok and lo == 101.5 and hi == 104.5
    D2 = FakeD([(5, 99.0, 104.0, 1), (5, 100.0, 102.5, 2)])
    ok, lo, hi = m1(D2, 1, 101.0)             # cả hai chứa giá ⇒ vùng hẹp hơn
    assert ok and lo == 100.0 and hi == 102.5


def test_doi_ban_do():
    D = FakeD([(5, 100.0, 102.0, 1)], shift=5.0)
    assert m1(D, 1, 101.0, k=0)[0]
    assert not m1(D, 1, 101.0, k=1)[0]        # vùng dời lên 105–107 ⇒ nằm trên giá
    ok, lo, hi = m1(D, 1, 106.0, k=1)
    assert ok and abs(lo - 105.0) < 1e-9 and abs(hi - 107.0) < 1e-9


def test_khong_nhin_truoc_co_vung():
    rows = [(5, 100.0, 102.0, 1), (6, 90.0, 110.0, 2), (9, 95.0, 105.0, 3)]
    full = FakeD(rows)
    cut = FakeD([r for r in rows if r[0] <= 5])  # bỏ mọi dòng vùng sau nến 5
    for side, e in ((1, 101.0), (1, 108.0), (-1, 94.0), (-1, 99.5)):
        assert m1(full, side, e) == m1(cut, side, e) or (np.isnan(m1(full, side, e)[1]) and np.isnan(m1(cut, side, e)[1]))


def test_neo_sl():
    t = pd.DataFrame(dict(side=[1, -1, 1], entry=[101.37, 99.0, 106.0], idx=[1, 2, 3], S=['A', 'A', 'A']))
    zlo = np.array([100.03, 97.0, 100.0])
    zhi = np.array([102.0, 99.42, 102.0])
    ents, keep = BV.anchor_entries(t, zlo, zhi, np.array([True, True, True]), 1.5)
    assert list(keep) == [0, 1]                       # lệnh 3: SL = 99,5 ⇒ 6,5 giá > 4 ⇒ bỏ
    e0, e1 = ents
    assert abs(e0['sl'] - 99.5) < 1e-9                # 100,03 − 0,5 = 99,53 ⇒ làm tròn XUỐNG theo tick 0,1
    assert abs(e0['tp'] - round(101.37 + 1.5 * (101.37 - 99.5), 6)) < 1e-9
    assert abs(e1['sl'] - 100.0) < 1e-9               # 99,42 + 0,5 = 99,92 ⇒ làm tròn LÊN 100,0
    assert abs(e1['tp'] - round(99.0 - 1.5 * 1.0, 6)) < 1e-9


def test_phan_quyet():
    def c(v, se, n, m, q5, q95):
        return (v, se, n, m, q5, q95)
    good = {'TRAIN': c(0.5, 0.1, 40, 0.0, -0.2, 0.2), 'TEST': c(0.6, 0.1, 30, 0.0, -0.2, 0.2), 'GỘP': c(0.55, 0.07, 70, 0, -.1, .1),
            'T8': c(0.4, 0.2, 20, 0, -.3, .3), 'T9': c(0.5, 0.2, 20, 0, -.3, .3), 'T10': c(-0.1, 0.2, 20, 0, -.3, .3)}
    assert BV.verdict(good, True).startswith('KHÁC')
    assert BV.verdict(good, False).startswith('không áp dụng')
    bad = dict(good, TEST=c(-0.6, 0.1, 30, 0.0, -0.2, 0.2))
    assert BV.verdict(bad, True).startswith('≈')
    wide = dict(good, TRAIN=c(0.5, 0.3, 40, 0.0, -0.2, 0.2))       # |hiệu| ≤ 2 sai số
    assert BV.verdict(wide, True).startswith('≈')
    inside = dict(good, TEST=c(0.15, 0.05, 30, 0.0, -0.2, 0.2))
    assert BV.verdict(inside, True).startswith('≈')


def _df():
    return K.load_bars(BV.D90 + '_bars.csv')


def test_bias_khong_nhin_truoc():
    df = _df()
    full = BV.bias_1900(df)
    raw = pd.read_csv(BV.D90 + '_bars.csv', parse_dates=['datetime'])
    sm = df['sm'].to_numpy()
    sno = df['session_no'].to_numpy()
    i19 = [int(np.flatnonzero((sno == s) & (sm >= 840))[0]) for s in (10, 30, 50)]
    for c in [5000, 30000, 60000] + [x - 1 for x in i19] + i19:
        cut = BV.bias_1900(K._enrich(raw.iloc[:c + 1]))
        assert np.array_equal(np.nan_to_num(cut, nan=9), np.nan_to_num(full[:c + 1], nan=9)), c
    # ảnh chụp đúng định nghĩa: dấu (close − VWAP tuần) tại nến 19:00
    vw = K.vwap_series(df)['vwap_w'].to_numpy()
    for i in i19:
        assert full[i] == np.sign(df['close'].iat[i] - vw[i])
        assert np.isnan(full[i - 1]) or full[i - 1] in (-1.0, 1.0)


def test_co_theo_nen_bang_co_theo_lenh():
    """bar_flags (dùng cho đối chứng ngẫu nhiên) phải trùng flag() khi vào ở giá đóng."""
    import lan_cham as LC
    if not os.path.exists(os.path.join(LC.CACHE, 'v5.pkl')):
        return
    df = _df()

    class D2:
        pass
    D = D2()
    D.df = df
    D.sno = df['session_no'].to_numpy()
    D.close = df['close'].to_numpy(float)
    D.rec = BV.load_rec(df)
    D.zm = BV.ZoneMap(D.rec)
    rng = np.random.default_rng(1)
    nS = int(D.sno.max()) + 1
    D.dsh = np.hstack([np.zeros((nS, 1)), rng.uniform(3, 15, (nS, 1)) * rng.choice([-1.0, 1.0], (nS, 1))])
    for k in (0, 1):
        fb, fs = BV.bar_flags(D, k)
        idx = rng.choice(len(df), 400, replace=False)
        for side, arr in ((1, fb), (-1, fs)):
            got = BV.flag(D, idx, np.full(len(idx), side), D.close[idx], k)[0]
            assert np.array_equal(got, arr[idx]), (k, side)


if __name__ == '__main__':
    for k_, fn in list(globals().items()):
        if k_.startswith('test_'):
            fn()
            print('OK', k_)
