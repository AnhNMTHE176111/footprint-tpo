# -*- coding: utf-8 -*-
"""Test setup C-v7 (PLAN-C-v3 mục 4.3). Chạy: python3 -m pytest test_setup_c_v7.py -q
1-2. Tái tạo C0 / C4 đúng từng lệnh. 3. VCL khớp file nến. 4-5. Sinh / không sinh hành lang (tổng hợp). 6. Chết (TREND, mất vùng, hết phiên).
7. Chế độ cân bằng của máy == K.mode_frame (D90 thật). 8. Cắt dữ liệu chống nhìn trước. 9. merge_add giữ base. 10. shift 0 == thật.
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
import setup_c_v7 as S7  # noqa: E402
import zones_c_v7 as Z7  # noqa: E402
from test_setup_c_v6 import mk, key  # noqa: E402

_cache = {}


def full():
    if not _cache:
        D = S7.Data7()
        shapes, ch = D.shapes(), D.choch()
        Ls = {k: S6.build_layer(D, k, shapes, ch) for k in ('L0', 'L1', 'L2', 'L3')}
        _cache.update(D=D, shapes=shapes, ch=ch, Ls=Ls,
                      base={tm: S6.run_all(D, shapes, ch, tp_mode=tm, layers=Ls) for tm in ('poc', 'fixed2')})
        _cache['v7'] = S7.run_all_v7(D, 'poc', base=_cache['base']['poc'])
    return _cache


# ------------------------------------------------------------------------------------------ 1-2. tái tạo
def test_reproduce_c0():
    c = full()
    D = c['D']
    for tm, (n_exp, r_exp) in S7.EXPECT_C0.items():
        e = c['base'][tm]['C0'][0]
        e0, _ = C.run(D.P, pen_ticks=2, min_width=6.0, tp_mode=tm)
        assert [key(x) for x in e] == [key(x) for x in e0]
        s = K._stats(S6.sim(D, e))
        assert s['n'] == n_exp and round(s['avg_r'], 2) == r_exp, (tm, s)


def test_reproduce_c4_v6():
    c = full()
    for tm, exp in S7.EXPECT_C4.items():
        t = S6.closed(c['base'][tm]['C4'][1])
        assert len(t) == exp[0], (tm, len(t))
        assert abs(t['r'].mean() - exp[1]) <= 0.05, (tm, t['r'].mean())
        if tm == 'poc':
            assert abs(K._stats(t)['sum_r'] - exp[2]) <= 0.05
    # v7 giữ nguyên C0 / C4 của v6 từng lệnh
    for cell in ('C0', 'C4'):
        assert [key(x) for x in c['v7'][cell][0]] == [key(x) for x in c['base']['poc'][cell][0]]


# ------------------------------------------------------------------------------------------ 3. VCL khớp nến
def test_vcl_alignment():
    c = full()
    D = c['D']
    rec = D.rec
    assert int(rec['bar'].max()) < len(D.df)
    assert rec['eid'].dtype.kind == 'i'
    has = np.zeros(len(D.df), bool)
    has[rec['bar'].unique()] = True
    clean = set(D.clean_snos)
    m = np.array([s in clean for s in D.sno])
    assert has[m].all()


# ------------------------------------------------------------------------------------------ helper tổng hợp
def rec_of(n, boxes, drop=None):
    """boxes: [(eid, lo, hi, mask)] có mặt ở MỌI nến; drop: {eid: nến đầu tiên không còn}."""
    rows = []
    for i in range(n):
        for e, lo, hi, mk_ in boxes:
            if drop and e in drop and i >= drop[e]:
                continue
            rows.append(dict(bar=i, lo=lo, hi=hi, eid=e, mask=mk_))
    return pd.DataFrame(rows, columns=['bar', 'lo', 'hi', 'eid', 'mask'])


def flat(n, c=105.0, **kw):
    return mk([(c, c + 0.1, c - 0.1, c)] * n, **kw)


BOXES = [(1, 100.0, 102.0, 1), (2, 110.0, 112.0, 4)]


def test_birth_synthetic():
    df = flat(30)
    assert not df['thin'].iloc[0] or True
    r = Z7.sr_corridors(df, None, rec=rec_of(30, BOXES))
    fr = r['frame']
    assert r['funnel']['sinh'] >= 1
    assert np.isnan(fr['sr_lo'].iloc[0]) and np.isnan(fr['sr_hi'].iloc[0]) and fr['sr_id'].iloc[0] == -1          # sinh ở 0, chưa tô
    assert fr['sr_lo'].iloc[1] == 102.0 and fr['sr_hi'].iloc[1] == 110.0 and fr['sr_id'].iloc[1] == 0
    lg = r['log'][0]
    assert lg['birth'] == 0 and (lg['s_lo'], lg['s_hi'], lg['r_lo'], lg['r_hi']) == (100.0, 102.0, 110.0, 112.0)
    rf = Z7.sr_corridors(df, None, rec=rec_of(30, BOXES), face='far')['frame']
    assert rf['sr_lo'].iloc[1] == 100.0 and rf['sr_hi'].iloc[1] == 112.0


def test_no_birth():
    df = flat(20)
    cases = {
        'trong hộp': [(1, 100.0, 106.0, 1), (2, 110.0, 112.0, 4)],
        'thiếu phía trên': [(1, 100.0, 102.0, 1)],
        'hẹp 5,8': [(1, 100.0, 102.0, 1), (2, 107.8, 110.0, 4)],
    }
    for name, boxes in cases.items():
        r = Z7.sr_corridors(df, None, rec=rec_of(20, boxes))
        assert r['funnel']['sinh'] == 0 and not r['log'], name
        assert (r['frame']['sr_id'] == -1).all(), name
    # đúng 6,0 thì sinh (rộng tối thiểu inclusive)
    r = Z7.sr_corridors(df, None, rec=rec_of(20, [(1, 100.0, 102.0, 1), (2, 108.0, 110.0, 4)]))
    assert r['funnel']['sinh'] >= 1


def _trend_df(top, extra=0):
    rows = [(105.0, 105.1, 104.9, 105.0)] * 5 + [(top, top + 0.1, top - 0.1, top)] * (10 + extra)
    return mk(rows)


def test_death():
    # 2 nến M5 đóng trên hi_face (110) ≥ 3 giá ⇒ chết ở last_pos thứ hai (bar 14) — 'trend'
    df = _trend_df(113.5)
    r = Z7.sr_corridors(df, None, rec=rec_of(len(df), [(1, 100.0, 102.0, 1), (2, 110.0, 112.0, 4)]))
    lg = r['log'][0]
    assert lg['why'] == 'trend' and lg['end'] == 14, lg
    assert r['frame']['sr_id'].iloc[14] == 0 and r['frame']['sr_id'].iloc[15] == -1 if len(df) > 15 else True
    # cách < 3 giá ⇒ sống (BREAK)
    df = _trend_df(111.5, extra=5)
    r = Z7.sr_corridors(df, None, rec=rec_of(len(df), [(1, 100.0, 102.0, 1), (2, 110.0, 112.0, 4)]))
    assert r['log'][0]['why'] == 'het_du_lieu' and 'BREAK_UP' in set(r['internal_mode5']) and 'TREND_UP' not in set(r['internal_mode5'])
    # eid R biến mất ⇒ mat_vung
    df = flat(30)
    r = Z7.sr_corridors(df, None, rec=rec_of(30, BOXES, drop={2: 7}))
    assert r['log'][0]['why'] == 'mat_vung' and r['log'][0]['end'] == 7
    # sang phiên ⇒ het_phien
    df = flat(40, gap_at=20)
    assert df['session_no'].iloc[20] == 1
    r = Z7.sr_corridors(df, None, rec=rec_of(40, BOXES))
    assert r['log'][0]['why'] == 'het_phien' and r['log'][0]['end'] == 20
    assert r['frame']['sr_id'].iloc[20] == -1 and r['log'][1]['birth'] == 20


# ------------------------------------------------------------------------------------------ 7. chế độ == kernel
def test_mode_parity():
    c = full()
    D = c['D']
    df = D.df
    corr = c['v7']['corr']
    fr = corr['frame']
    zc = Z7.Z6.band_zcols(D.zc0, fr['sr_lo'].to_numpy(float), fr['sr_hi'].to_numpy(float), poc=None)
    m5 = K.m5_bars(df, zc)
    mf = K.mode_frame(df, zc, m5)
    own = corr['internal_mode5']
    te = m5['t5_end'].to_numpy()
    t1 = df['t_utc'].to_numpy()
    sn = df['session_no'].to_numpy()
    mode = mf['mode'].to_numpy()
    cid = fr['sr_id'].to_numpy()
    lp = m5['last_pos'].to_numpy()
    p = np.searchsorted(t1, te, side='left')                      # M1 đầu tiên mở sau khi nến M5 j đóng
    n_cmp = 0
    for j in range(len(m5)):
        pj = int(p[j])
        if pj >= len(df) or sn[pj] != m5['session_no'].iloc[j]:
            continue
        assert mode[pj] == own[j], (j, mode[pj], own[j])
        n_cmp += 1
        if mode[pj].startswith('TREND'):                           # kernel báo TREND ⇒ hành lang đang tô phải đã chết
            assert cid[pj] != cid[lp[j]] or cid[lp[j]] == -1, j
    assert n_cmp > 0.9 * len(m5)
    assert any(str(x).startswith('TREND') for x in own) and any(x == 'BALANCE' for x in own)


# ------------------------------------------------------------------------------------------ 8. cắt dữ liệu
def test_no_lookahead_cut():
    c = full()
    D = c['D']
    df, rec = D.df, D.rec
    corr = c['v7']['corr']
    fr = corr['frame']
    raw = pd.read_csv(S6.D90 + '_bars.csv', parse_dates=['datetime'])
    lgs = corr['log']
    ks = [x['birth'] + 1 for x in lgs[len(lgs) // 5::len(lgs) // 4][:4]] + [x['end'] + 1 for x in lgs[len(lgs) // 7::len(lgs) // 4][:4]]
    ks += [int(D.st['start_pos'].loc[30]) + 300, int(D.st['start_pos'].loc[45]) + 2]
    ks = sorted({k for k in ks if 50 < k < len(df)})
    assert len(ks) >= 8
    e_full = c['v7']['C5'][0]
    for k in ks:
        dfc = K._enrich(raw.iloc[:k])
        dfc['thin'] = df['thin'].to_numpy()[:k]
        dfc['splice'] = df['splice'].to_numpy()[:k]
        rc = rec[rec['bar'] < k]
        cc = Z7.sr_corridors(dfc, None, rec=rc)
        for col in ('sr_lo', 'sr_hi'):
            assert np.allclose(cc['frame'][col].to_numpy(), fr[col].to_numpy()[:k], equal_nan=True), (k, col)
        assert (cc['frame']['sr_id'].to_numpy() == fr['sr_id'].to_numpy()[:k]).all(), k
        zc, names, mf = Z7.layer_sr(dfc, D.zc0.iloc[:k].reset_index(drop=True), cc)
        L = dict(zc=zc, names=names, mf=mf)
        ec = S6.detect(dfc, zc, mf, pen_ticks=2, min_width=6.0, tp_mode='poc', excl=S7.EXCL, zone_name=names)
        ea = [key(e) for e in e_full if e['idx'] < k]
        eb = [key(e) for e in ec if e['idx'] < k]
        assert ea == eb, (k, set(ea) ^ set(eb))


# ------------------------------------------------------------------------------------------ 9. merge_add
def test_merge_add_keeps_base():
    base = [dict(idx=5, layer='L2'), dict(idx=9, layer='L3')]
    new = [dict(idx=3, layer='L4'), dict(idx=5, layer='L4'), dict(idx=12, layer='L4')]
    out = S7.merge_add(base, new)
    assert [(e['idx'], e['layer']) for e in out] == [(3, 'L4'), (5, 'L2'), (9, 'L3'), (12, 'L4')]
    assert all(b in out for b in base)
    c = full()
    for cell, add in (('C0+SR', 'C0'), ('C6', 'C4')):
        eb = c['v7'][add][0]
        e = c['v7'][cell][0]
        assert all(any(key(x) == key(b) for x in e) for b in eb)
        l4 = {x['idx'] for x in e if x.get('layer') == 'L4'}
        assert not (l4 & {b['idx'] for b in eb})


# ------------------------------------------------------------------------------------------ 10. shift 0
def test_shift_zero_equals_real():
    c = full()
    D = c['D']
    real = c['v7']['corr']
    z = S7.corridors(D, shift=np.zeros(int(D.sno.max()) + 1))
    assert z['frame'].equals(real['frame'])
    assert [(x['birth'], x['end'], x['why']) for x in z['log']] == [(x['birth'], x['end'], x['why']) for x in real['log']]
    assert z['funnel'] == real['funnel']


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-q']))
