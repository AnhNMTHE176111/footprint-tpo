# -*- coding: utf-8 -*-
"""Test setup B-v3 (plan `plans/BENZO-B-v3-plan.md` mục 4). Chạy: python3 -m pytest test_b_v3.py -q
 1. Tái tạo B cũ (11 / 27,3 % / 0,00; idx khớp _b_old_idx.json).      2. Tái tạo B v2 (25 / 32,0 % / 0,19; khớp _b_v2_idx.json; 2-tuple và 4-tuple).
 3. Chuỗi tập con cũ ⊆ v2 ⊆ v3 + trần 2/(loại, phiên).               4. Gán khe VCL theo eid (tổng hợp).
 5. Khoá chiều mdirs.                                                  6. Ưu tiên giữa họ + trần chung loại VCL.
 7. Không nhìn trước (cắt dữ liệu, engine VCL chạy lại).              8. PDH/PDL tổng hợp.
 9. Dời bản đồ vùng (warm, mdirs không đổi).                           10. ĐC2 VCL_R_ANY.
11. Căn hàng rec ↔ df.                                                 12. Hồi quy (test_kernel, test_b_v2, P dựng tay không có 'mdir').
"""
import os
import sys
import json
import subprocess

import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import setup_b_hap_thu as SB  # noqa: E402
import zones_b_v2 as ZB  # noqa: E402
import zones_b_v3 as Z3  # noqa: E402
import setup_b_v2 as B2  # noqa: E402
import benzo_vcl as BV  # noqa: E402
import test_b_v2 as T2  # noqa: E402  (dùng _pattern, key)

REPORT = os.path.join(HERE, 'report')
FIX_OLD = os.path.join(REPORT, '_b_old_idx.json')
FIX_V2 = os.path.join(REPORT, '_b_v2_idx.json')
_cache = {}


def full():
    if not _cache:
        raw = pd.read_csv(SB.D90 + '_bars.csv', parse_dates=['datetime'])
        lv = pd.read_csv(SB.D90 + '.csv', usecols=['bar_idx', 'price', 'volume'])
        df = K._enrich(raw)
        prof = K.build_profiles(df, lv)
        ctx = K._Ctx(df, prof)
        lev = ZB.session_table_b(df, prof, ctx)
        extra2 = ZB.build_extra(df, prof, ctx, lev)
        rec = BV.load_rec(df)
        slots = Z3.vcl_slots(rec, len(df))
        extra3 = Z3.build_extra3(df, prof, ctx, lev, rec, slots)
        _cache.update(raw=raw, lv=lv, df=df, prof=prof, ctx=ctx, lev=lev, extra2=extra2, rec=rec, slots=slots, extra3=extra3,
                      P2=SB.prepare(df, prof, extra2), P3=SB.prepare(df, prof, extra3), P0=SB.prepare(df, prof))
    return _cache


def key6(e):
    return [int(e['idx']), int(e['side']), float(e['entry']), float(e['sl']), float(e['tp']), e['zone']]


def stats(df, ents):
    return K._stats(K.simulate(df, ents))


# ------------------------------------------------------------------------------------------ 1. B cũ
def test_reproduce_old_b():
    c = full()
    fx = json.load(open(FIX_OLD))
    e = SB.detect(c['P3'], 0.5, 3, zones=Z3.ZONES_OLD)
    s = stats(c['df'], e)
    assert s['n'] == 11 and abs(s['wr'] - 0.273) < 0.0015 and abs(s['avg_r'] - 0.00) <= 0.005
    assert [x['idx'] for x in e] == fx['idx']
    assert tuple(c['P3']['Z']) == Z3.ZONE_ORDER_V3 and list(c['P3']['Z'])[:2] == ['VWAP_W', 'VWAP_D']


# ------------------------------------------------------------------------------------------ 2. B v2
def test_reproduce_v2():
    c = full()
    fx = json.load(open(FIX_V2))
    for P in (c['P2'], c['P3']):                         # 2-tuple (code v2) và 4-tuple (extra3) cho cùng kết quả
        e = SB.detect(P, 0.5, 3, zones=Z3.ZONES_V2)
        s = stats(c['df'], e)
        assert s['n'] == 25 and abs(s['wr'] - 0.320) < 0.0015 and abs(s['avg_r'] - 0.19) <= 0.005
        assert [key6(x) for x in e] == fx['entries_raw']


# ------------------------------------------------------------------------------------------ 3. chuỗi tập con + trần
def test_subset_chain_and_cap():
    c = full()
    P = c['P3']
    eo, e2, e3 = (SB.detect(P, 0.5, 3, zones=z) for z in (Z3.ZONES_OLD, Z3.ZONES_V2, Z3.ZONES_V3))
    io, i2, i3 = ({x['idx']: x for x in e} for e in (eo, e2, e3))
    assert set(io) <= set(i2) <= set(i3) and len(i3) > len(i2)
    for a, b in ((io, i2), (i2, i3)):
        for i, e in a.items():
            assert T2.key(b[i]) == T2.key(e) and b[i]['zone'] == e['zone']
    g = pd.DataFrame([(e['ztype'], int(c['df']['session_no'].iloc[e['idx']])) for e in e3], columns=['zt', 's']).groupby(['zt', 's']).size()
    assert g.max() <= SB.MAX_PER_ZONE_SESSION
    for e in e3:
        assert e['zone'] == e['zones_hit'][0] and e['ztype'] == Z3.ZTYPE_OF_V3[e['zone']]
        if e['zone'].startswith('VCL_'):
            assert e['ztype'] == 'VCL'
        assert len(set(e['zones_hit'])) == len(e['zones_hit'])
        if e['zone'].startswith('VCL_R'):
            assert e['side'] == -1                       # kháng cự ⇒ SELL
        if e['zone'].startswith('VCL_S'):
            assert e['side'] == 1


# ------------------------------------------------------------------------------------------ 4. gán khe (tổng hợp)
def _rec(rows):
    return pd.DataFrame(rows, columns=['bar', 'lo', 'hi', 'eid'])


def _mk(spec):
    rows = []
    for eid, (a, b, lo) in spec.items():
        for t in range(a, b + 1):
            rows.append((t, lo + 0.01 * t, lo + 2, eid))
    return _rec(rows)


def test_slot_assignment_synthetic():
    spec = {0: (0, 9, 10.0), 1: (2, 12, 5.0), 2: (4, 7, 20.0), 3: (8, 15, 1.0), 4: (10, 14, 30.0)}
    n = 20
    sl = Z3.vcl_slots(_mk(spec), n)
    assert sl['K'] == 3
    eid = sl['eid']
    for e, (a, b, _) in spec.items():
        ks = {int(k) for k in range(3) for t in range(a, b + 1) if eid[k, t] == e}
        assert len(ks) == 1, e                           # mỗi eid đúng một khe suốt đời
        k = ks.pop()
        assert all(eid[k, t] == e for t in range(a, b + 1))
        assert all(eid[k, t] != e for t in range(n) if not (a <= t <= b))
    for t in range(n):
        live = eid[:, t][eid[:, t] >= 0]
        assert len(live) == len(set(live.tolist()))      # không hai eid cùng khe cùng nến (mỗi eid một khe)
    # chỗ đã đo bằng tay: eid0→khe0, eid1→khe1, eid2→khe2; khe 2 giải phóng sau nến 7, eid3 (sinh nến 8) dùng lại; eid4 (nến 10) dùng khe 0 (eid0 hết nến 9)
    assert eid[0, 0] == 0 and eid[1, 2] == 1 and eid[2, 4] == 2 and eid[2, 8] == 3 and eid[0, 10] == 4
    assert np.isnan(sl['lo'][1, 1]) and eid[1, 1] == -1 and np.isnan(sl['hi'][2, 3]) and eid[2, 3] == -1   # khe trống = NaN / −1
    assert np.isnan(sl['lo'][0, 16:]).all()
    # runlen đúng tay
    assert list(sl['runlen'][2, 4:8]) == [1, 2, 3, 4] and list(sl['runlen'][2, 8:12]) == [1, 2, 3, 4] and sl['runlen'][2, 3] == 0
    # warm sau đổi eid: False ở 3 nến đầu (VCL_WARM − 1) rồi True
    warm = sl['runlen'][2] >= Z3.VCL_WARM
    assert list(warm[8:12]) == [False, False, False, True] and not warm[4] and warm[7]
    # eid xuất hiện lại sau khi biến mất ⇒ raise
    with pytest.raises(ValueError):
        Z3.vcl_slots(pd.concat([_mk({0: (0, 3, 10.0), 1: (0, 7, 5.0)}), _rec([(5, 10.0, 12.0, 0)])]), 12)
    # nến không có vùng nào ở giữa rồi eid quay lại ⇒ cũng raise
    with pytest.raises(ValueError):
        Z3.vcl_slots(_rec([(0, 1.0, 3.0, 7), (1, 1.0, 3.0, 7), (3, 1.0, 3.0, 7)]), 5)
    # > 7 khe ⇒ dừng
    with pytest.raises(ValueError):
        Z3.vcl_slots(_rec([(0, float(k), k + 2.0, k) for k in range(8)]), 3)


def test_slot_online_real_and_no_lookahead_on_slots():
    """Gán khe trực tuyến: cắt rec ở nến t rồi gán lại ⇒ y hệt [0, t] của bản đầy đủ (trên dữ liệu thật)."""
    c = full()
    rec, n = c['rec'], len(c['df'])
    for t in (30000, 51234, 70001):
        sub = rec[rec['bar'] <= t]
        s2 = Z3.vcl_slots(sub, n)
        for k in ('lo', 'hi'):
            assert np.allclose(s2[k][:, :t + 1], c['slots'][k][:, :t + 1], equal_nan=True)
        for k in ('eid', 'runlen'):
            assert (s2[k][:, :t + 1] == c['slots'][k][:, :t + 1]).all()


# ------------------------------------------------------------------------------------------ 5. khoá chiều
def _synth_P4(extra, zs=(100.0,)):
    rows = [(115, 125, 115, 120, 0)] + [(120, 120.1, 119.9, 120, 0)] * 40
    for z in zs:
        rows += T2._pattern(z)
    t = pd.date_range('2026-09-01 14:00', periods=len(rows), freq='min')
    d = pd.DataFrame({'bar_idx': range(len(rows)), 'datetime': t, 'open': [r[0] for r in rows], 'high': [r[1] for r in rows],
                      'low': [r[2] for r in rows], 'close': [r[3] for r in rows], 'volume': 10, 'delta': [r[4] for r in rows]})
    df = K._enrich(d)
    n = len(df)
    ex = {}
    for nm, (v, zt, warm, md) in extra.items():
        ex[nm] = (np.full(n, float(v)), zt, None if warm is None else np.full(n, bool(warm)) if np.isscalar(warm) else warm(n), md)
    return SB.prepare(df, K.build_profiles(df, None), ex), tuple(extra)


def test_direction_lock():
    P, zs = _synth_P4({'VCL_S1': (100.0, 'VCL', None, (-1,))})
    e = SB.detect(P, 0.5, 3, zones=zs)
    assert len(e) == 1 and e[0]['zone'] == 'VCL_S1' and e[0]['side'] == 1 and e[0]['ztype'] == 'VCL'
    P, zs = _synth_P4({'VCL_R1': (100.0, 'VCL', None, (1,))})
    assert SB.detect(P, 0.5, 3, zones=zs) == []          # mẫu BUY (giá đi xuống tới Z) bị khoá ⇒ 0 lệnh
    P, zs = _synth_P4({'VCL_R1': (100.0, 'VCL', None, None)})
    assert len(SB.detect(P, 0.5, 3, zones=zs)) == 1       # không khoá ⇒ có lệnh: chính mdirs là thứ chặn
    # warm False ở một nến của cụm ⇒ 0 lệnh
    P, zs = _synth_P4({'VCL_S1': (100.0, 'VCL', None, (-1,))})
    i = SB.detect(P, 0.5, 3, zones=zs)[0]['idx']
    for j in (i - 3, i - 2, i - 1):
        def w(n, j=j):
            a = np.ones(n, bool)
            a[j] = False
            return a
        P, zs = _synth_P4({'VCL_S1': (100.0, 'VCL', w, (-1,))})
        assert SB.detect(P, 0.5, 3, zones=zs) == [], j


# ------------------------------------------------------------------------------------------ 6. ưu tiên giữa họ + trần
def test_priority_across_families_and_cap():
    P, zs = _synth_P4({'POC_D': (100.0, 'POC_D', None, None), 'PDH': (100.0, 'PDHL', None, None), 'VCL_S1': (100.0, 'VCL', None, (-1,))})
    e = SB.detect(P, 0.5, 3, zones=zs)
    assert len(e) == 1 and e[0]['ztype'] == 'POC_D' and e[0]['zones_hit'] == ['POC_D', 'PDH', 'VCL_S1']
    lv = {'VCL_S1': (100.0, 'VCL', None, (-1,)), 'VCL_S2': (90.0, 'VCL', None, (-1,)), 'VCL_S3': (80.0, 'VCL', None, (-1,))}
    P, zs = _synth_P4(lv, zs=(100.0, 90.0, 80.0))
    assert [x['zone'] for x in SB.detect(P, 0.5, 3, zones=zs)] == ['VCL_S1', 'VCL_S2']      # trần chung loại VCL
    lv2 = {'VCL_S1': (100.0, 'VCL', None, (-1,)), 'VCL_S2': (90.0, 'VCL', None, (-1,)), 'PDL': (80.0, 'PDHL', None, None)}
    P, zs = _synth_P4(lv2, zs=(100.0, 90.0, 80.0))
    assert [x['ztype'] for x in SB.detect(P, 0.5, 3, zones=zs)] == ['VCL', 'VCL', 'PDHL']    # PDL khác loại ⇒ lệnh thứ 3


# ------------------------------------------------------------------------------------------ 7. không nhìn trước (cắt dữ liệu)
def _cut_pos(df, sno, lo, hi):
    m = (df['session_no'].to_numpy() == sno) & (df['sm'].to_numpy() >= lo) & (df['sm'].to_numpy() < hi)
    return int(np.flatnonzero(m)[0])


def test_no_lookahead_cut():
    import vcl5 as V5
    import test_lan_cham as TL
    b, l = TL._slice()
    ctxf = V5.prepare(b, l)
    recf = V5.run_engine(ctxf)['rec']
    dff = ctxf['df']
    raw = b
    proff = K.build_profiles(dff, l)
    cf = K._Ctx(dff, proff)
    levf = ZB.session_table_b(dff, proff, cf)
    slf = Z3.vcl_slots(recf, len(dff))
    exf = Z3.build_extra3(dff, proff, cf, levf, recf, slf)
    tf = Z3.zone_table3(exf, dff)
    Pf = SB.prepare(dff, proff, exf)
    ef = SB.detect(Pf, 0.5, 3, zones=Z3.ZONES_V3)
    vcl_e = [e for e in ef if e['ztype'] == 'VCL']
    st = K.session_table(dff)
    snos = list(st.index)
    s_mid = snos[2]
    sm = dff['sm'].to_numpy()
    sno = dff['session_no'].to_numpy()
    cuts = [int(st['start_pos'].loc[s_mid]) + 300]                                             # giữa phiên
    w = dff['week_no'].to_numpy()
    chg = np.flatnonzero(np.diff(w) != 0)
    cuts.append(int(chg[0]) + 1 + 4 if len(chg) else int(st['start_pos'].loc[snos[3]]) + 4)   # nến thứ 5 sau đổi tuần (không có ⇒ sau đổi phiên)
    cuts.append(_cut_pos(dff, snos[3], 841, 846))                                              # ngay sau 19:00 VN
    if vcl_e:
        cuts.append(int(vcl_e[len(vcl_e) // 2]['idx']) - 2)                                    # giữa cụm của một lệnh VCL thật
    else:
        k4 = np.argwhere(slf['runlen'] == Z3.VCL_WARM)
        cuts.append(int(k4[len(k4) // 2][1]))
    assert len(cuts) >= 4
    for i in cuts:
        bb, ll = TL._cut(b, l, i)
        recc = V5.run_engine(V5.prepare(bb, ll))['rec']
        dfc = K._enrich(raw.iloc[:i + 1].copy())
        dfc['thin'] = dff['thin'].to_numpy()[:i + 1]
        dfc['splice'] = dff['splice'].to_numpy()[:i + 1]
        lvc = l[l['bar_idx'] <= raw['bar_idx'].iloc[i]]
        profc = K.build_profiles(dfc, lvc)
        cc = K._Ctx(dfc, profc)
        levc = ZB.session_table_b(dfc, profc, cc)
        slc = Z3.vcl_slots(recc, len(dfc))
        for k in ('eid', 'runlen'):
            assert (slc[k] == slf[k][:, :i + 1]).all(), (k, i)
        for k in ('lo', 'hi'):
            assert np.allclose(slc[k], slf[k][:, :i + 1], equal_nan=True), (k, i)
        exc = Z3.build_extra3(dfc, profc, cc, levc, recc, slc)
        tc = Z3.zone_table3(exc, dfc)
        for col in tf.columns:
            assert np.allclose(tc[col].to_numpy(), tf[col].to_numpy()[:i + 1], equal_nan=True), (col, i)
        Pc = SB.prepare(dfc, profc, exc)
        ec = SB.detect(Pc, 0.5, 3, zones=Z3.ZONES_V3)
        a = [key6(e) + [tuple(e['zones_hit'])] for e in ef if e['idx'] <= i]
        bq = [key6(e) + [tuple(e['zones_hit'])] for e in ec]
        assert a == bq, (i, a, bq)


# ------------------------------------------------------------------------------------------ 8. PDH/PDL tổng hợp
def test_pdhl_synthetic():
    spec = [(110.0, 310), (120.0, 100), (130.0, 310), (140.0, 310)]       # phiên 2 ngắn (< 300 nến)
    rows, t = [], pd.Timestamp('2026-09-01 00:00')
    for k, (p, nb) in enumerate(spec):
        for j in range(nb):
            rows.append((t, p, p + 1 + (j == 7) * (k + 1), p - 1 - (j == 9) * (k + 1), p))      # đỉnh/đáy riêng mỗi phiên
            t += pd.Timedelta(minutes=1)
        t += pd.Timedelta(minutes=60)
    d = pd.DataFrame({'bar_idx': range(len(rows)), 'datetime': [r[0] for r in rows], 'open': [r[1] for r in rows], 'high': [r[2] for r in rows],
                      'low': [r[3] for r in rows], 'close': [r[4] for r in rows], 'volume': 100, 'delta': 0})
    df = K._enrich(d)
    prof = K.build_profiles(df, None)
    ctx = K._Ctx(df, prof)
    st = ctx.st
    assert len(st) == 4 and int(st['n'].loc[1]) < 300
    pdh, pdl = Z3.pdhl(df, prof, ctx)
    sno = df['session_no'].to_numpy()
    h, lo_ = df['high'].to_numpy(), df['low'].to_numpy()
    assert np.isnan(pdh[sno == 0]).all() and np.isnan(pdl[sno == 0]).all()                 # phiên đầu: không có phiên trước
    for s, q in ((1, 0), (2, 0), (3, 2)):                                                   # phiên idx 2: phiên idx 1 ngắn bị bỏ ⇒ lấy phiên idx 0
        m = sno == s
        assert (pdh[m] == h[sno == q].max()).all() and (pdl[m] == lo_[sno == q].min()).all(), s
    assert len({float(x) for x in (h[sno == 0].max(), h[sno == 2].max(), h[sno == 3].max())}) == 3    # đỉnh mỗi phiên khác nhau ⇒ test có nghĩa


# ------------------------------------------------------------------------------------------ 9. dời
def test_shift3():
    c = full()
    df, prof, ex3, P = c['df'], c['prof'], c['extra3'], c['P3']
    sno = df['session_no'].to_numpy()
    nS = int(sno.max()) + 1
    S0 = Z3.shifted3(ex3, P['zc'], np.zeros(nS), sno)
    assert tuple(S0) == Z3.ZONE_ORDER_V3
    P0 = SB.prepare(df, prof, S0)
    assert [key6(e) for e in SB.detect(P0, 0.5, 3, zones=Z3.ZONES_V3)] == [key6(e) for e in SB.detect(P, 0.5, 3, zones=Z3.ZONES_V3)]
    d = ZB.shift_matrix(nS, B2.REPS, B2.SHIFT_LO, B2.SHIFT_HI, B2.SHIFT_SEED)[:, 7]
    S1 = Z3.shifted3(ex3, P['zc'], d, sno)
    Pk = SB.prepare(df, prof, S1)
    for nm in Z3.ZONE_ORDER_V3:
        assert np.allclose(Pk['Z'][nm], P['Z'][nm] + d[sno], equal_nan=True), nm
        assert Pk['ztype'][nm] == P['ztype'][nm]
        assert Pk['mdir'][nm] == P['mdir'][nm], nm
        assert np.array_equal(Pk['warm'][nm], P['warm'][nm]), nm
    for nm in Z3.R_NAMES + Z3.S_NAMES:
        assert S1[nm][2] is ex3[nm][2] and S1[nm][3] is ex3[nm][3]
    assert Pk['mdir']['VCL_R3'] == (1,) and Pk['mdir']['VCL_S3'] == (-1,) and Pk['mdir']['PDH'] == (1, -1)


# ------------------------------------------------------------------------------------------ 10. ĐC2
def test_control_vcl_any():
    c = full()
    df, ex3, P = c['df'], c['extra3'], c['P3']
    tab = Z3.zone_table3(ex3, df)
    zcols = pd.concat([P['zc'], tab.set_index(P['zc'].index)], axis=1)
    before = dict(K.ZONE_NAME2COL)
    cl, hi, lo = P['cl'], P['hi'], P['lo']
    # tính lại bằng tay: có ít nhất một cạnh R ấm mà chạm
    touch = np.zeros(len(df), bool)
    for nm in Z3.R_NAMES:
        z, _, w, _ = ex3[nm]
        with np.errstate(invalid='ignore'):
            touch |= ((np.abs(cl - z) <= 1.0) | ((lo <= z) & (z <= hi))) & w
    r_any = tab['VCL_R_ANY'].to_numpy()
    assert (np.isnan(r_any) == ~touch).all()
    i0 = int(np.flatnonzero(touch & P['okbar'])[len(np.flatnonzero(touch & P['okbar'])) // 2])
    ent = [dict(idx=i0, side=-1, entry=float(cl[i0]), sl=float(cl[i0]) + 2, tp=float(cl[i0]) - 6, setup='B', zone='VCL_R_ANY')]
    with B2._patched_map({nm: None for nm in tab.columns}):
        assert K.ZONE_NAME2COL['VCL_R_ANY'] == 'VCL_R_ANY'
        ce = K.control_sample(df, zcols, P['modecode'], entries=ent, n_random=60, seed=5)
    assert K.ZONE_NAME2COL == before and 'VCL_R_ANY' not in K.ZONE_NAME2COL
    assert len(ce) > 0
    for x in ce:
        assert touch[x['idx']] and x['side'] == -1


# ------------------------------------------------------------------------------------------ 11. căn hàng
def test_align():
    c = full()
    Z3.check_align(c['df'])
    with pytest.raises(AssertionError):
        Z3.check_align(c['df'].iloc[1:].reset_index(drop=True))
    bad = c['df'].copy()
    bad['datetime'] = bad['datetime'].shift(1, fill_value=bad['datetime'].iloc[0])
    with pytest.raises(AssertionError):
        Z3.check_align(bad)
    assert int(c['rec']['bar'].max()) < len(c['df']) and c['slots']['K'] <= Z3.VCL_SLOTS_MAX


# ------------------------------------------------------------------------------------------ 12. hồi quy
def test_regression_hand_built_p_and_suites():
    c = full()
    P = dict(c['P0'])
    P.pop('mdir', None)                                   # P dựng tay (test cũ) không có 'mdir' ⇒ hai chiều như cũ
    e1 = SB.detect(P, 0.5, 3)
    e2 = SB.detect(c['P0'], 0.5, 3)
    assert [key6(x) for x in e1] == [key6(x) for x in e2]
    r = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-x', os.path.join(HERE, 'test_kernel.py'), os.path.join(HERE, 'test_b_v2.py')],
                       capture_output=True, text=True, cwd=HERE)
    assert r.returncode == 0, r.stdout[-1500:]


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-q']))
