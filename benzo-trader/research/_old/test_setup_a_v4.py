# -*- coding: utf-8 -*-
"""Test setup A-v4 (plan BENZO-A-V4 mục 3.6). Chạy: python3 -m pytest test_setup_a_v4.py -q
1. Tái tạo gốc: máy chung ở chế độ (band cũ, logic V3, cấm 18:00–19:20) ra ĐÚNG lệnh setup_a_pha_hoi.detect(expire=30): n=20, WR 10%, R −0,68.
2. Ca tổng hợp: phá dài 40 nến rồi hồi (A-v4 vào, V3 không); M5 đóng trong 0,5 giá không hủy / 1,5 giá hủy; cực trị 1,5 giá chưa
   trang bị / 2,5 giá trang bị; VWAP động: E = giá trị tại nến vào; HVN dải: phá lên dùng mép trên, SL qua mép dưới; L cập nhật theo
   nến đà sau nến phá; hết hạn rồi M5 ngoài lần nữa ⇒ brk_no = 2; hai vùng cùng nến ⇒ chọn vùng gần hơn.
3. Không nhìn trước: cắt dữ liệu ở >= 5 vị trí, detect(df[:i+1]) cho đúng các lệnh idx <= i của bản đầy đủ; bảng vùng khớp trên [0, i].
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import setup_a_v4 as A4  # noqa: E402
import zones_a_v4 as ZA  # noqa: E402

_cache = {}


def full():
    if not _cache:
        raw = pd.read_csv(A4.D90 + '_bars.csv', parse_dates=['datetime'])
        lv = pd.read_csv(A4.D90 + '.csv', usecols=['bar_idx', 'price', 'volume'])
        df = K._enrich(raw)
        prof = K.build_profiles(df, lv)
        P = A4.Prep(df, prof, lv)
        _cache.update(raw=raw, lv=lv, P=P)
    return _cache


# ------------------------------------------------------------------------------------------ 1. tái tạo gốc
def test_reproduce_v3_baseline():
    import setup_a_pha_hoi as SA
    P = full()['P']
    e = A4.detect(P, P.zones('old'), logic='v3', ban=True)
    D = SA.Data(SA.D90)
    e0 = SA.detect(D.df, D.zc, D.m5, 3, 0.5, expire=30)
    key = lambda x: (x['idx'], x['side'], x['entry'], x['sl'], x['tp'])  # noqa: E731
    assert [key(x) for x in e] == [key(x) for x in e0]
    s = K._stats(K.simulate(P.df, e))
    assert s['n'] == 20 and abs(s['wr'] - 0.10) < 1e-9 and round(s['avg_r'], 2) == -0.68


# ------------------------------------------------------------------------------------------ 2. ca tổng hợp
class SynthP(A4.Prep):
    pass


def make_P(rows, start='2026-09-01 14:00'):
    """rows: list (o, h, l, c[, delta]); 1 phiên M1 liền nhau từ start (UTC; 14:00 UTC = 21:00 VN, pha Mỹ)."""
    t = pd.date_range(start, periods=len(rows), freq='min')
    d = pd.DataFrame({'bar_idx': range(len(rows)), 'datetime': t,
                      'open': [r[0] for r in rows], 'high': [r[1] for r in rows], 'low': [r[2] for r in rows],
                      'close': [r[3] for r in rows], 'volume': 10, 'delta': [r[4] if len(r) > 4 else 5 for r in rows]})
    df = K._enrich(d)
    return A4.Prep(df, K.build_profiles(df, None))


def pz(n, E, name='VAH_D', ztype='VAH_D', dyn=False, rank=5):
    v = np.full(n, float(E)) if np.isscalar(E) else np.asarray(E, float)
    return dict(name=name, ztype=ztype, lo=v.copy(), hi=v.copy(), dyn=dyn, band=False, sl_far=False, rank=rank)


def path(ext, pb_bars=25, pb_step=None, big_mom=1.0, cf=True, tail=40, inside=99.5, brk_close=101.4):
    """Phiên mẫu quanh vùng điểm E = 100: 30 nến trong (≈ 99,5), 5 nến phá (M5 thứ 7 đóng 101,4 — > 1 giá trên E để hủy trạng thái
    xuống mở từ đầu phiên), 40 nến đà lên tới cực trị ≈ ext (một nến đà dài big_mom + 0,2), rồi pb_bars nến hồi đều về ≈ 100,3, rồi nến
    CF (thân 0,65 / biên độ 0,8, delta lớn), rồi tail nến đi ngang."""
    R = [(inside, 102.0, 97.0, inside)]                       # nến 0 dài nhất phiên (loại "3 nến sau nến dài nhất" không dính)
    R += [(inside, inside + 0.2, inside - 0.2, inside)] * 29
    c = inside
    for k, x in enumerate(np.linspace(100.0, brk_close, 5)):  # nến 30..34
        R.append((c, max(c, x) + 0.1, min(c, x) - 0.1, x))
        c = x
    n_mom = 40
    inc = (ext - 0.1 - c - big_mom) / (n_mom - 1)
    for k in range(n_mom):                                    # nến 35..74
        x = c + (big_mom if k == 15 else inc)
        R.append((c, x + 0.1, c - 0.1, x))
        c = x
    step = pb_step if pb_step is not None else ((c - 100.3) / pb_bars if pb_bars else 0.0)
    for k in range(pb_bars):
        x = c - step
        R.append((c, c + 0.05, x - 0.05, x, -5))
        c = x
    if cf:
        R.append((c - 0.05, c + 0.6, c - 0.15, c + 0.6, 100))
        c = c + 0.6
    R += [(c, c + 0.1, c - 0.1, c)] * tail
    return R


def test_long_break_then_pullback_v4_enters_v3_not():
    R = path(108.3)
    P = make_P(R)
    Z = [pz(len(R), 100.0)]
    e4 = A4.detect(P, Z, logic='mom')
    e3 = A4.detect(P, Z, logic='v3')
    assert len(e4) == 1 and e4[0]['side'] == 1
    e = e4[0]
    assert e['p0'] == 34 and e['bars_mom'] >= 39 and e['idx'] == 34 + 40 + 25 + 1
    assert abs(e['L'] - 1.2) < 1e-9                             # L gồm nến đà dài sau nến phá (1,0 + 0,2)
    assert e['sl'] == round(99.0 - 0.3, 1)                      # struct = E − 1 (vùng điểm)
    assert e3 == []                                             # V3: CF ở > 30 nến sau nến phá ⇒ hết hạn


def test_armed_threshold():
    for ext, want in ((101.5, 0), (102.5, 1)):
        R = path(ext, pb_bars=20, brk_close=100.6, big_mom=0.3)
        P = make_P(R)
        e = A4.detect(P, [pz(len(R), 100.0)], logic='mom')
        assert len(e) == want, (ext, e)


def test_cancel_depth():
    # sau đà lên 105, một nến M5 đóng 0,5 giá DƯỚI E ⇒ không hủy; 1,5 giá dưới ⇒ hủy
    for depth, alive in ((0.5, True), (1.5, False)):
        R = path(105.0, pb_bars=15, cf=False, tail=0)
        P0 = make_P(R)
        c = R[-1][3]
        n = len(R)
        # đẩy tới hết M5 hiện tại rồi đóng M5 kế tiếp ở 100 − depth
        while (n % 5) != 0:
            R.append((c, c + 0.05, c - 0.05, c))
            n += 1
        tgt = 100.0 - depth
        for k in range(5):
            x = c + (tgt - c) * (k + 1) / 5
            R.append((c, max(c, x) + 0.05, min(c, x) - 0.05, x))
            c = x
        R += [(c, c + 0.05, c - 0.05, c)] * 3
        P = make_P(R)
        log = []
        A4.detect(P, [pz(len(R), 100.0)], logic='mom', states_log=log)
        up = [x for x in log if x['S'] == 1 and x['p0'] == 34]
        assert len(up) == 1
        assert (up[0]['why'] == 'end') == alive, (depth, up[0]['why'])
        assert (up[0]['why'] == 'cancel') == (not alive)


def test_vwap_dynamic_E():
    R = path(108.3)
    n = len(R)
    vw = np.linspace(99.6, 100.4, n)                             # "VWAP" trôi chậm
    P = make_P(R)
    z = pz(n, vw, name='VWAP_D', ztype='VWAP_D', dyn=True, rank=2)
    e = A4.detect(P, [z], logic='mom')
    assert len(e) == 1
    i = e[0]['idx']
    assert abs(e[0]['E'] - vw[i]) < 1e-12


def test_hvn_band_edges():
    R = path(108.3, brk_close=102.0)
    n = len(R)
    P = make_P(R)
    z = dict(name='HVN_W1', ztype='HVN_W', lo=np.full(n, 98.8), hi=np.full(n, 100.0), dyn=False, band=True, sl_far=True, rank=3)
    e = A4.detect(P, [z], logic='mom')
    assert len(e) == 1 and e[0]['E'] == 100.0                  # phá lên ⇒ E = mép trên
    i = e[0]['idx']
    struct = min(P.lo[i], 98.8 - 1.0)
    assert e[0]['sl'] == round(np.floor((struct - 0.3) / 0.1 + 1e-9) * 0.1, 6)   # SL qua mép DƯỚI − 1 − 0,3


def test_expire_then_rebreak_brk_no_2():
    # đà lên 104 rồi đi ngang > 30 nến KHÔNG về E ⇒ hết hạn; M5 ngoài kế tiếp mở lại với brk_no = 2
    R = path(104.0, pb_bars=0, cf=False, tail=0)
    c = R[-1][3]
    R += [(c, c + 0.05, c - 0.05, c)] * 45
    P = make_P(R)
    log = []
    A4.detect(P, [pz(len(R), 100.0)], logic='mom', states_log=log)
    up = sorted([x for x in log if x['S'] == 1], key=lambda x: x['p0'])
    assert up[0]['why'] == 'expire' and up[0]['brk_no'] == 1
    assert len(up) >= 2 and up[1]['brk_no'] == 2 and up[1]['reopen']
    # độ nhạy after_inside: không mở lại khi giá chưa về trong
    log2 = []
    A4.detect(P, [pz(len(R), 100.0)], logic='mom', states_log=log2, after_inside=True)
    assert len([x for x in log2 if x['S'] == 1]) == 1


def test_two_zones_same_bar_pick_nearer():
    R = path(108.3)
    n = len(R)
    P = make_P(R)
    z1 = pz(n, 100.0, name='VAH_D', ztype='VAH_D', rank=5)
    z2 = pz(n, 100.4, name='HVN_D1', ztype='HVN_D', rank=4)
    e = A4.detect(P, [z1, z2], logic='mom')
    i = e[0]['idx']
    c = P.cl[i]
    want = 'VAH_D' if abs(c - 100.0) < abs(c - 100.4) else 'HVN_D1'
    assert e[0]['zone'] == want


# ------------------------------------------------------------------------------------------ 3. không nhìn trước
def _cut_pos(df, sno, lo, hi):
    m = (df['session_no'].to_numpy() == sno) & (df['sm'].to_numpy() >= lo) & (df['sm'].to_numpy() < hi)
    return int(np.flatnonzero(m)[0])


def test_no_lookahead_cut():
    c = full()
    P, raw, lv = c['P'], c['raw'], c['lv']
    df = P.df
    Zf = P.zones('plus')
    ef = A4.detect(P, Zf, logic='mom')
    tf = ZA.zone_table(Zf)
    st = P.st
    cuts = [_cut_pos(df, 30, 300, 301),                          # giữa phiên (10:00 VN)
            _cut_pos(df, 45, 841, 846),                          # ngay sau 19:00 VN (VA Âu vừa chốt)
            int(st['start_pos'].loc[st.index[st['week_no'] == 8][0]]) + 40,   # ngay sau đổi tuần
            _cut_pos(df, 58, 1000, 1010)]
    mid = [e for e in ef if e['idx'] - e['pk_pos'] >= 6]
    cuts.append(int(mid[len(mid) // 2]['pk_pos']) + 3)          # giữa một nhịp hồi có lệnh sau đó
    for i in cuts:
        dfc = K._enrich(raw.iloc[:i + 1])
        dfc['thin'] = df['thin'].to_numpy()[:i + 1]              # cờ lọc phiên mỏng/chỗ nối của kernel dùng tổng phiên (đã biết) — lấy theo bản đầy đủ
        dfc['splice'] = df['splice'].to_numpy()[:i + 1]
        lvc = lv[lv['bar_idx'] <= raw['bar_idx'].iloc[i]]
        Pc = A4.Prep(dfc, K.build_profiles(dfc, lvc), lvc)
        Zc = Pc.zones('plus')
        tc = ZA.zone_table(Zc)
        for col in tf.columns:
            assert np.allclose(tc[col].to_numpy(), tf[col].to_numpy()[:i + 1], equal_nan=True), (col, i)
        ec = A4.detect(Pc, Zc, logic='mom')
        a = [(e['idx'], e['side'], e['zone'], e['entry'], e['sl'], e['tp']) for e in ef if e['idx'] <= i]
        b = [(e['idx'], e['side'], e['zone'], e['entry'], e['sl'], e['tp']) for e in ec]
        assert a == b, (i, set(a) ^ set(b))


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-q']))
