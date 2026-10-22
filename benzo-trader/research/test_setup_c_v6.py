# -*- coding: utf-8 -*-
"""Test setup C-v6 (plan PLAN-C-v2 mục 4.3). Chạy: python3 -m pytest test_setup_c_v6.py -q
1. Tái tạo C0: lớp L0 ra ĐÚNG từng lệnh setup_c_fade_canh.run (TP poc n=103 R −0,43; fixed2 n=121 R −0,26).
2. Profile TPO từ M1 = dựng tay từ bracket 30'. 3. Phân loại D / P / b / thin / B / close-ngoài-VA trên profile tổng hợp.
4–6. Máy CHoCH trên chuỗi tổng hợp: sinh đúng [50, 75] tại confirm_pos(L2); ST thủng sâu ⇒ không sinh + nến thủng thành ứng viên mới;
     nới 0,2·h / chết 0,3·h / TREND chết / hết phiên chết.
7. Không nhìn trước: cắt dữ liệu ở nhiều vị trí, nhãn / band / VA_C / lệnh khớp bản đầy đủ tới nến cắt.
8. Rộng tối thiểu: T < 6 ⇒ 0 lệnh. 9. Gộp C4: trùng nến ⇒ cạnh gần close hơn, hoà ⇒ L3.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import setup_c_fade_canh as C  # noqa: E402
import setup_c_v6 as S6  # noqa: E402
import zones_c_v6 as Z  # noqa: E402

_cache = {}


def full():
    if not _cache:
        _cache['D'] = S6.Data()
    return _cache['D']


def key(e):
    return (e['idx'], e['side'], e['entry'], e['sl'], e['tp'], e['zone'])


# ------------------------------------------------------------------------------------------ 1. tái tạo C0
def test_reproduce_c0():
    D = full()
    L0 = S6.build_layer(D, 'L0')
    for tm, (n_exp, r_exp) in S6.EXPECT_C0.items():
        e = S6.entries_of(D, L0, tm)
        e0, t0 = C.run(D.P, pen_ticks=2, min_width=6.0, tp_mode=tm)
        assert [key(x) for x in e] == [key(x) for x in e0]
        s = K._stats(S6.sim(D, e))
        assert s['n'] == n_exp and round(s['avg_r'], 2) == r_exp, (tm, s)
    # prep_from (dùng cho test cắt) khớp prepare
    P2 = S6.prep_from(D.df, D.P['prof'])
    assert P2['zc'].equals(D.P['zc']) and P2['mf'].equals(D.P['mf'])


# ------------------------------------------------------------------------------------------ helper tổng hợp
def mk(rows, start='2026-09-01 02:00', gap_at=None, gap_min=60):
    """rows: (o, h, l, c[, vol[, delta]]). gap_at: chỉ số nến bắt đầu phiên mới (cách gap_min phút)."""
    t = list(pd.date_range(start, periods=len(rows), freq='min'))
    if gap_at is not None:
        t = t[:gap_at] + [x + pd.Timedelta(minutes=gap_min) for x in t[gap_at:]]
    d = pd.DataFrame({'bar_idx': range(len(rows)), 'datetime': t, 'open': [r[0] for r in rows], 'high': [r[1] for r in rows],
                      'low': [r[2] for r in rows], 'close': [r[3] for r in rows], 'volume': [r[4] if len(r) > 4 else 10 for r in rows],
                      'delta': [r[5] if len(r) > 5 else 1 for r in rows]})
    return K._enrich(d)


def move(R, c, target, k, vol=10, last_h=None, last_l=None):
    """k nến đi đều từ close c tới close target; râu 0,1. last_h / last_l: ép high / low của nến cuối. Trả close cuối."""
    for j, x in enumerate(np.linspace(c, target, k + 1)[1:]):
        o = c
        h, l = max(o, x) + 0.1, min(o, x) - 0.1
        if j == k - 1 and last_h is not None:
            h = last_h
        if j == k - 1 and last_l is not None:
            l = last_l
        R.append((o, h, l, x, vol))
        c = x
    return c


def base_dn(st_low=55.0, st_vol=10):
    """100 đi ngang → rơi về 52 (bước 1 giá) → nến climax (đáy 50, vol 3×, đóng 51,5) → AR lên đỉnh 75 → ST về st_low.
    Trả (R, chỉ số climax, chỉ số đáy ST)."""
    R = [(100.0, 100.95, 99.05, 100.0, 10)] * 80
    c = move(R, 100.0, 52.0, 48)
    R.append((52.0, 52.1, 50.0, 51.5, 30))
    ci = len(R) - 1
    c = move(R, 51.5, 74.9, 24, last_h=75.0)
    c = move(R, c, st_low + 0.1, int(round(75 - st_low)), last_l=st_low)
    R[-1] = R[-1][:4] + (st_vol,)
    return R, ci, len(R) - 1


def machine(df, **p):
    return Z.choch_machine(df, K.median_range(df).to_numpy(float), Z.vma_series(df).to_numpy(float), p or None)


# ------------------------------------------------------------------------------------------ 2. profile TPO
def test_tpo_profile_exact():
    R = []
    for k in range(90):
        if k < 30:
            R.append((100.5, 101.0 if k == 3 else 100.8, 100.0 if k == 7 else 100.2, 100.5))
        elif k < 60:
            R.append((101.3, 102.0 if k == 40 else 101.6, 100.6 if k == 50 else 101.0, 101.3))
        else:
            R.append((99.7, 100.4 if k == 70 else 100.0, 99.0 if k == 80 else 99.4, 99.7))
    df = mk(R, start='2026-09-01 00:00')
    rows, cnt, L, H, close = Z.tpo_profile(df, 0)
    want = {}
    for a, b in ((500, 505), (503, 510), (495, 502)):          # bracket 1: 100,0–101,0 ; 2: 100,6–102,0 ; 3: 99,0–100,4
        for r in range(a, b + 1):
            want[r] = want.get(r, 0) + 1
    assert dict(zip(rows.tolist(), cnt.tolist())) == want
    assert (L, H, close) == (99.0, 102.0, 99.7)


# ------------------------------------------------------------------------------------------ 3. phân loại
def _prof(cnt, base=5000):
    rows = np.arange(base, base + len(cnt))
    pr = K.Profiles.row_price(rows)
    return rows, np.asarray(cnt, float), float(pr[0]), float(pr[-1])


def test_classify_shapes():
    r = np.arange(101)
    bell = np.round(1 + 9 * np.exp(-((r - 50) / 20.0) ** 2))
    rows, cnt, L, H = _prof(bell)
    d = Z.classify_shape(rows, cnt, L, H, close=1010.0)
    assert d['label'] == 'D' and abs((d['t_lo'] - L) - (H - d['t_hi'])) < 1e-9          # T đối xứng khi profile đối xứng
    assert Z.classify_shape(rows, cnt, L, H, close=H)['label'] == 'KHÁC-close'            # close ngoài VA
    p = np.where(r < 60, 1.0, np.round(1 + 9 * np.exp(-((r - 80) / 14.0) ** 2)))
    rows, cnt, L, H = _prof(p)
    dp = Z.classify_shape(rows, cnt, L, H, close=1016.0)
    assert dp['label'] == 'P' and dp['asym'] > 0.25 and dp['t_lo'] <= 1016.0 <= dp['t_hi']
    rows, cnt, L, H = _prof(p[::-1])
    db = Z.classify_shape(rows, cnt, L, H, close=1004.0)
    assert db['label'] == 'b' and abs(db['asym'] + dp['asym']) < 1e-9
    thin = np.full(101, 2.0)
    thin[49:52] = 10.0
    rows, cnt, L, H = _prof(thin)
    assert Z.classify_shape(rows, cnt, L, H, close=1010.0)['label'] == 'KHÁC-thin'
    two = 1 + 9 * np.exp(-((r - 25) / 8.0) ** 2) + 9 * np.exp(-((r - 75) / 8.0) ** 2)
    rows, cnt, L, H = _prof(np.round(two))
    dd = Z.classify_shape(rows, cnt, L, H, close=1005.0)
    assert dd['label'] == 'KHÁC-B' and dd['two_peaks']


# ------------------------------------------------------------------------------------------ 4. CHoCH sinh
def test_choch_birth():
    R, ci, si = base_dn()
    c = move(R, R[-1][3], 65.0, 10)
    R += [(65.0, 65.3, 64.7, 65.0, 10)] * 40
    df = mk(R)
    vas, cands, fu = machine(df)
    dn = [v for v in vas if v.dir == 'DN']
    assert len(dn) == 1, fu
    v = dn[0]
    zz = K.zigzag(df, Z.ZZ)
    l2 = [x for x in zz if x['kind'] == 'L' and x['pos'] == si]
    assert len(l2) == 1 and v.birth == l2[0]['confirm_pos']                               # sinh ĐÚNG tại confirm_pos(L2)
    assert (v.L1, v.H1, v.L2) == (50.0, 75.0, 55.0) and (v.lo, v.hi) == (50.0, 75.0)
    assert v.climax == ci
    res = Z.choch_va(df, K.median_range(df), Z.vma_series(df))
    fr = res['frame']
    assert np.isnan(fr['choch_lo'].iloc[v.birth - 1]) and np.isnan(fr['choch_hi'].iloc[:v.birth]).all()   # không sớm hơn
    assert fr['choch_lo'].iloc[v.birth] == 50.0 and fr['choch_hi'].iloc[v.birth] == 75.0
    assert fr['choch_src'].iloc[v.birth] == 'CHOCH_DN'


# ------------------------------------------------------------------------------------------ 5. ST thủng sâu
def test_choch_fail_deep_undercut():
    R, ci, _ = base_dn(st_low=46.0)
    R.append((46.1, 46.2, 45.0, 45.9, 30))                                                 # nến đáy thủng: vol 3×, bị chặn
    si = len(R) - 1
    c = move(R, 45.9, 49.0, 4)
    R += [(49.0, 49.3, 48.7, 49.0, 10)] * 30
    df = mk(R)
    u = K.median_range(df).to_numpy(float)
    assert 45.0 < 50.0 - Z.UNDERCUT_U * u[si]                                               # đúng là thủng > 1,0·u
    vas, cands, fu = machine(df)
    assert not any(v.dir == 'DN' and abs(v.lo - 50.0) < 1e-9 for v in vas)
    assert fu['DN']['ST_thung'] >= 1
    assert ('DN', si) in cands                                                             # nến thủng thành ứng viên climax mới


# ------------------------------------------------------------------------------------------ 6. nới / chết
def _after_birth(top, tail=20):
    R, ci, si = base_dn()
    c = move(R, R[-1][3], 65.0, 10)
    R += [(65.0, 65.3, 64.7, 65.0, 10)] * 10
    c = move(R, 65.0, top - 0.1, int(round(top - 65)), last_h=top)
    c = move(R, c, top - 3.0, 3)
    R += [(c, c + 0.3, c - 0.3, c, 10)] * tail
    return R


def test_choch_extend_and_die():
    for top, alive in ((80.0, True), (82.5, False)):                                       # vượt 0,2·25 = 5 ⇒ nới ; 0,3·25 = 7,5 ⇒ chết
        df = mk(_after_birth(top))
        vas, _, _ = machine(df)
        v = [x for x in vas if x.dir == 'DN'][0]
        if alive:
            assert v.n_ext == 1 and v.hi == 80.0 and v.lo == 50.0 and v.why == 'het_du_lieu'
        else:
            assert v.why == 'pha_bien' and v.n_ext == 0
    # độ nhạy không nới: 0,2·h ⇒ giữ cạnh
    v = [x for x in machine(mk(_after_birth(80.0)), extend=False)[0] if x.dir == 'DN'][0]
    assert v.n_ext == 0 and v.hi == 75.0 and v.why == 'het_du_lieu'
    # TREND ⇒ chết (đi lên 95 và nằm đó, không có pivot H ⇒ chỉ chế độ M5 giết)
    R, ci, si = base_dn()
    c = move(R, R[-1][3], 65.0, 10)
    R += [(65.0, 65.3, 64.7, 65.0, 10)] * 10
    c = move(R, 65.0, 95.0, 30)
    R += [(95.0, 95.2, 94.8, 95.0, 10)] * 30
    df = mk(R)
    res = Z.choch_va(df, K.median_range(df), Z.vma_series(df))
    lg = [x for x in res['log'] if x['dir'] == 'DN']
    assert len(lg) == 1 and lg[0]['why'] == 'trend'
    k = lg[0]['end']
    assert np.isnan(res['frame']['choch_lo'].iloc[k:]).all() and res['mf']['mode'].iloc[k].startswith('TREND')
    # hết phiên ⇒ chết
    R, ci, si = base_dn()
    c = move(R, R[-1][3], 62.0, 7)
    R += [(62.0, 62.3, 61.7, 62.0, 10)] * 20
    g = len(R)
    R += [(62.0, 62.3, 61.7, 62.0, 10)] * 20
    df = mk(R, gap_at=g)
    assert df['session_no'].iloc[g] == 1
    res = Z.choch_va(df, K.median_range(df), Z.vma_series(df))
    lg = [x for x in res['log'] if x['dir'] == 'DN'][0]
    assert lg['why'] == 'het_phien' and lg['end'] == g and np.isnan(res['frame']['choch_lo'].iloc[g:]).all()


# ------------------------------------------------------------------------------------------ 7. không nhìn trước
def test_no_lookahead_cut():
    D = full()
    raw = pd.read_csv(S6.D90 + '_bars.csv', parse_dates=['datetime'])
    lv = pd.read_csv(S6.D90 + '.csv', usecols=['bar_idx', 'price', 'volume'])
    df = D.df
    sh = D.shapes()
    ch = D.choch()
    R = S6.run_all(D, sh, ch)
    st = D.st
    births = [x['birth'] for x in ch['log']]
    cands = [i for _, i in ch['cands']]
    m = (df['session_no'].to_numpy() == 45) & (df['sm'].to_numpy() >= 841)
    cuts = [int(np.flatnonzero(m)[0]) + 2,                                    # ngay sau 19:00 VN
            int(st['start_pos'].loc[30]) + 300,                                # giữa phiên (pha A)
            births[len(births) // 3] + 1,                                      # ngay sau một lần sinh VA_C
            births[2 * len(births) // 3] + 40,                                 # trong đời một VA_C
            cands[len(cands) // 2] + 3]                                        # đang trong cụm climax
    cuts += [cands[k] for k in np.linspace(0, len(cands) - 1, 6).round().astype(int)]      # ĐÚNG nến climax
    cuts += [births[k] for k in np.linspace(0, len(births) - 1, 4).round().astype(int)]    # ĐÚNG nến sinh
    for i in cuts:
        dfc = K._enrich(raw.iloc[:i + 1])
        dfc['thin'] = df['thin'].to_numpy()[:i + 1]
        dfc['splice'] = df['splice'].to_numpy()[:i + 1]
        lvc = lv[lv['bar_idx'] <= raw['bar_idx'].iloc[i]]
        Dc = S6.Data(P=S6.prep_from(dfc, K.build_profiles(dfc, lvc)))
        shc = Dc.shapes()
        sc = int(dfc['session_no'].iloc[i])
        for s in range(sc + 1):
            assert shc.get(s) == sh.get(s), (i, s)
        chc = Dc.choch()
        for col in ('choch_lo', 'choch_hi'):
            assert np.allclose(chc['frame'][col].to_numpy(), ch['frame'][col].to_numpy()[:i + 1], equal_nan=True), (i, col)
        assert (chc['frame']['choch_src'].to_numpy() == ch['frame']['choch_src'].to_numpy()[:i + 1]).all()
        a = [(x['birth'], x['lo0'], x['hi0'], x['climax']) for x in ch['log'] if x['birth'] <= i]
        b = [(x['birth'], x['lo0'], x['hi0'], x['climax']) for x in chc['log']]
        assert a == b, i
        assert [x for x in ch['cands'] if x[1] <= i] == chc['cands'], i                    # ứng viên climax tới nến cắt
        Rc = S6.run_all(Dc, shc, chc)
        for kind in ('L1', 'L2', 'L3'):
            tf = Z.zone_table(R['L'][kind]['zc'], R['L'][kind]['names'])
            tc = Z.zone_table(Rc['L'][kind]['zc'], Rc['L'][kind]['names'])
            for col in ('eu_vah', 'eu_val', 'eu_poc'):
                assert np.allclose(tc[col].to_numpy(), tf[col].to_numpy()[:i + 1], equal_nan=True), (i, kind, col)
            assert (tc['hn'].to_numpy() == tf['hn'].to_numpy()[:i + 1]).all()
            assert Rc['L'][kind]['mf']['mode'].equals(R['L'][kind]['mf']['mode'].iloc[:i + 1])
        for cell in ('C1', 'C2', 'C3', 'C4'):
            ea = [key(e) for e in R[cell][0] if e['idx'] <= i]
            eb = [key(e) for e in Rc[cell][0]]
            assert ea == eb, (i, cell, set(ea) ^ set(eb))


def test_choch_machine_cut_many():
    """Máy CHoCH riêng (rẻ, không cần profile): cắt tại 40 nến climax / nến sinh, ứng viên + VA (tới nến cắt) khớp bản đầy đủ."""
    D = full()
    raw = pd.read_csv(S6.D90 + '_bars.csv', parse_dates=['datetime'])
    ch = D.choch()
    pts = sorted(set([i for _, i in ch['cands']][::max(1, len(ch['cands']) // 30)] + [x['birth'] for x in ch['log']][::max(1, len(ch['log']) // 10)]))
    for i in pts:
        dfc = K._enrich(raw.iloc[:i + 1])
        vas, cands, _ = Z.choch_machine(dfc, K.median_range(dfc).to_numpy(float), Z.vma_series(dfc).to_numpy(float))
        assert [x for x in ch['cands'] if x[1] <= i] == cands, i
        a = [(v.birth, v.dir, v.segs[0], v.climax) for v in ch['vas'] if v.birth <= i]
        b = [(v.birth, v.dir, v.segs[0], v.climax) for v in vas]
        assert a == b, i


# ------------------------------------------------------------------------------------------ 8. rộng tối thiểu
def test_min_width_blocks():
    for width, want in ((5.5, 0), (6.5, 1)):
        bh = 100.0 + width
        R = [(103.0, 110.0, 90.0, 103.0, 10, 1)]
        R += [(103.0, 103.2, 102.8, 103.0, 10, 1)] * 59
        R.append((bh + 0.1, bh + 0.4, bh - 0.7, bh - 0.6, 10, -50))                         # râu xuyên cạnh trên, đóng lại trong, delta âm
        R += [(bh - 0.6, bh - 0.5, bh - 0.7, bh - 0.6, 10, 1)] * 30
        df = mk(R, start='2026-09-01 01:00')                                                 # 08:00 VN — pha A
        assert (df['phase'] == 'A').all()
        zc2 = pd.DataFrame({c: np.full(len(df), np.nan) for c in K.ZONE_COLS})
        shp = {0: dict(label='P', t_lo=100.0, t_hi=bh, poc=101.0, vah=bh, val=100.0)}
        zc, names = Z.layer_zcols(df, zc2, 'L2', shp)
        mf = K.mode_frame(df, zc, K.m5_bars(df, zc))
        e = S6.detect(df, zc, mf, pen_ticks=2, min_width=6.0, tp_mode='poc', zone_name=names)
        assert len(e) == want, (width, e)
        if want:
            assert e[0]['zone'] == 'T_HI_P' and e[0]['side'] == -1 and e[0]['tp'] == 101.0


# ------------------------------------------------------------------------------------------ 9. gộp C4
def test_merge_tie_prefers_l3():
    class _D:
        pass
    D = _D()
    D.df = pd.DataFrame({'close': [10.0] * 5 + [11.0] + [10.0] * 4})
    e2 = [dict(idx=5, edge=10.0, layer='L2'), dict(idx=7, edge=10.0, layer='L2')]
    e3 = [dict(idx=5, edge=12.0, layer='L3'), dict(idx=8, edge=10.0, layer='L3')]
    out = S6.merge(D, e2, e3)
    assert [(x['idx'], x['layer']) for x in out] == [(5, 'L3'), (7, 'L2'), (8, 'L3')]
    e3b = [dict(idx=5, edge=11.5, layer='L3')]
    assert [(x['idx'], x['layer']) for x in S6.merge(D, e2, e3b)] == [(5, 'L3'), (7, 'L2')]
    e3c = [dict(idx=5, edge=12.5, layer='L3')]
    assert [(x['idx'], x['layer']) for x in S6.merge(D, e2, e3c)] == [(5, 'L2'), (7, 'L2')]


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-q']))
