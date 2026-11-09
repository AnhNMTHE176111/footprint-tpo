# -*- coding: utf-8 -*-
"""Test setup B-v2 (plan `plans/BENZO-B-v2-plan.md` mục 4). Chạy: python3 -m pytest test_b_v2.py -q
1. Tái tạo gốc B cũ (n=11, WR 27,3 %, R 0,00; idx khớp fixture) — cả khi prepare có/không vùng thêm.
2. Tập con: lệnh B-cũ ⊆ lệnh B-v2 (cùng chiều/entry/SL/TP/Z); trần ≤ 2 lệnh / (ztype, phiên).
3. Không nhìn trước: cắt dữ liệu ở 5 vị trí — bảng vùng và lệnh khớp bản đầy đủ trên [0, i].
4. POC_W tổng hợp: tuần W−1, loại phiên thin, cần ≥ 3 phiên.
5. Dedup + trần tổng hợp: hai mức khác loại cùng giá ⇒ 1 lệnh, ztype theo ưu tiên, zones_hit đủ; 3 ca HVN_D cùng phiên ⇒ giữ 2.
6. Dời vùng: δ = 0 ⇒ y hệt thật; δ ≠ 0 ⇒ mảng = thật + δ[phiên] (gồm VWAP); ma trận δ = benzo_vcl.Data().dsh[:, 1:].
7. ĐC2: nến đối chứng của lệnh zone='HVN_D2' chạm đúng HVN_D2; sau `with` K.ZONE_NAME2COL trở về như cũ.
8. Hồi quy: test_kernel.py chạy riêng (kernel không đổi).
"""
import os
import sys
import json

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import setup_b_hap_thu as SB  # noqa: E402
import zones_b_v2 as ZB  # noqa: E402
import setup_b_v2 as B2  # noqa: E402

_cache = {}


def full():
    if not _cache:
        raw = pd.read_csv(SB.D90 + '_bars.csv', parse_dates=['datetime'])
        lv = pd.read_csv(SB.D90 + '.csv', usecols=['bar_idx', 'price', 'volume'])
        df = K._enrich(raw)
        prof = K.build_profiles(df, lv)
        extra = ZB.build_extra(df, prof)
        P = SB.prepare(df, prof, extra)
        P0 = SB.prepare(df, prof)
        _cache.update(raw=raw, lv=lv, df=df, prof=prof, extra=extra, P=P, P0=P0)
    return _cache


def key(e):
    return (e['idx'], e['side'], e['entry'], e['sl'], e['tp'], e['zprice'])


# ------------------------------------------------------------------------------------------ 1. tái tạo gốc
def test_reproduce_old_b():
    c = full()
    fx = json.load(open(B2.FIXTURE_OLD))
    e0 = SB.detect(c['P0'], 0.5, 3)
    s = K._stats(K.simulate(c['df'], e0))
    assert s['n'] == 11 and abs(s['wr'] - 0.273) < 0.0015 and abs(s['avg_r'] - 0.00) <= 0.005
    assert [e['idx'] for e in e0] == fx['idx']
    e1 = SB.detect(c['P'], 0.5, 3, zones=ZB.ZONES_OLD)          # thêm vùng không được đổi bản cũ
    assert [key(e) for e in e1] == [key(e) for e in e0]
    assert list(c['P']['Z'])[:2] == ['VWAP_W', 'VWAP_D'] and tuple(c['P']['Z']) == ZB.ZONE_ORDER


# ------------------------------------------------------------------------------------------ 2. tập con + trần
def test_subset_and_cap():
    c = full()
    eo = SB.detect(c['P'], 0.5, 3, zones=ZB.ZONES_OLD)
    ev = SB.detect(c['P'], 0.5, 3, zones=ZB.ZONES_V2)
    io = {e['idx']: e for e in eo}
    iv = {e['idx']: e for e in ev}
    assert set(io) <= set(iv) and len(iv) > len(io)
    for i, e in io.items():
        assert key(iv[i]) == key(e)
    g = pd.DataFrame([(e['ztype'], int(c['df']['session_no'].iloc[e['idx']])) for e in ev], columns=['zt', 's']).groupby(['zt', 's']).size()
    assert g.max() <= SB.MAX_PER_ZONE_SESSION
    for e in ev:
        assert e['zone'] == e['zones_hit'][0] and e['ztype'] == ZB.ZTYPE_OF[e['zone']]
        assert len(set(e['zones_hit'])) == len(e['zones_hit'])
    # POC_D = cột yd_poc của kernel (không viết lại công thức)
    assert np.allclose(c['extra']['POC_D'][0], c['P']['zc']['yd_poc'].to_numpy(), equal_nan=True)
    assert np.allclose(c['extra']['VAH_D'][0], c['P']['zc']['yd_vah'].to_numpy(), equal_nan=True)


# ------------------------------------------------------------------------------------------ 3. không nhìn trước
def _cut_pos(df, sno, lo, hi):
    m = (df['session_no'].to_numpy() == sno) & (df['sm'].to_numpy() >= lo) & (df['sm'].to_numpy() < hi)
    return int(np.flatnonzero(m)[0])


def test_no_lookahead_cut():
    c = full()
    df, raw, lv, P = c['df'], c['raw'], c['lv'], c['P']
    ef = SB.detect(P, 0.5, 3, zones=ZB.ZONES_V2)
    tf = ZB.zone_table(c['extra'])
    st = K.session_table(df)
    w8 = int(st['start_pos'].loc[st.index[st['week_no'] == 8][0]])
    only_new = [e for e in ef if e['ztype'] not in ZB.ZONES_OLD]
    cuts = [_cut_pos(df, 30, 300, 301),                 # giữa phiên
            w8 + 4,                                     # nến thứ 5 của tuần mới
            _cut_pos(df, 45, 841, 846),                 # ngay sau 19:00 VN
            int(st['end_pos'].loc[58]),                 # cuối phiên
            int(only_new[len(only_new) // 2]['idx']) - 2]   # giữa cụm hấp thụ của một lệnh vùng mới
    for i in cuts:
        dfc = K._enrich(raw.iloc[:i + 1])
        dfc['thin'] = df['thin'].to_numpy()[:i + 1]     # cờ hậu cần (plan 0.1): sao chép từ bản đầy đủ, không tính lại
        dfc['splice'] = df['splice'].to_numpy()[:i + 1]
        lvc = lv[lv['bar_idx'] <= raw['bar_idx'].iloc[i]]
        profc = K.build_profiles(dfc, lvc)
        exc = ZB.build_extra(dfc, profc)
        tc = ZB.zone_table(exc)
        for col in tf.columns:
            assert np.allclose(tc[col].to_numpy(), tf[col].to_numpy()[:i + 1], equal_nan=True), (col, i)
        Pc = SB.prepare(dfc, profc, exc)
        for nm in ('VWAP_W', 'VWAP_D'):
            assert np.allclose(Pc['Z'][nm], P['Z'][nm][:i + 1])
        ec = SB.detect(Pc, 0.5, 3, zones=ZB.ZONES_V2)
        a = [key(e) + (tuple(e['zones_hit']),) for e in ef if e['idx'] <= i]
        b = [key(e) + (tuple(e['zones_hit']),) for e in ec]
        assert a == b, (i, set(a) ^ set(b))


# ------------------------------------------------------------------------------------------ 4. POC_W tổng hợp
def _synth_weeks(spec):
    """spec = list tuần, mỗi tuần list phiên, mỗi phiên = (giá chính, số nến). Phiên cách nhau 60 phút, tuần cách nhau 48 giờ.
    Mỗi phiên: 2/3 số nến ở giá chính, 1/3 ở giá chính + 3 (để POC không tầm thường). volume 100 / nến."""
    rows, t = [], pd.Timestamp('2026-09-01 00:00')
    for wk in spec:
        for (p, nb) in wk:
            for k in range(nb):
                q = p if k < 2 * nb // 3 else p + 3
                rows.append((t, q))
                t += pd.Timedelta(minutes=1)
            t += pd.Timedelta(minutes=60)
        t += pd.Timedelta(hours=48)
    d = pd.DataFrame({'bar_idx': range(len(rows)), 'datetime': [r[0] for r in rows], 'open': [r[1] for r in rows],
                      'high': [r[1] for r in rows], 'low': [r[1] for r in rows], 'close': [r[1] for r in rows],
                      'volume': 100, 'delta': 0})
    return K._enrich(d)


def test_poc_w_synthetic():
    X, Y, Z = 100.0, 120.0, 130.0
    spec = [[(110.0, 310)] * 2,                         # tuần 1: chỉ 2 phiên ⇒ POC_W tuần 2 = NaN
            [(X, 310)] * 4,                             # tuần 2: dồn ở X
            [(Y, 310)] * 4 + [(Z, 310)],                # tuần 3: dồn ở Y + 1 phiên (sẽ gắn thin) dồn ở Z
            [(Y, 310)] * 2]                             # tuần 4
    df = _synth_weeks(spec)
    assert df['week_no'].nunique() == 4 and not df['splice_jump'].any()
    # phiên cuối tuần 3: gắn cờ thin bằng tay + volume x10 ⇒ nếu KHÔNG loại thin thì POC_W tuần 4 phải là Z
    st = K.session_table(df)
    s_thin = int(st.index[st['week_no'] == 2][-1])
    m = df['session_no'].to_numpy() == s_thin
    df.loc[m, 'volume'] = 1000
    df.loc[m, 'thin'] = True
    prof = K.build_profiles(df, None)
    ctx = K._Ctx(df, prof)
    st = ctx.st
    pw = {int(s): ZB.week_poc(ctx, int(s), ctx.last_splice(int(s))) for s in st.index}
    wk = st['week_no'].to_numpy()
    for s in st.index:
        w = int(st['week_no'].loc[s])
        if w in (0, 1):
            assert np.isnan(pw[int(s)]), (s, pw[int(s)])
        elif w == 2:
            assert pw[int(s)] == X
        else:
            assert pw[int(s)] == Y                      # thin bị loại
    # không loại thin thì đã là Z (kiểm chính cái test có nghĩa)
    a = K._agg_profiles([prof.full[int(s)] for s in st.index[wk == 2]])
    assert K.value_area(K.Profiles.row_price(a[0]), a[1])[0] == Z
    # mảng theo nến (build_extra) khớp
    ex = ZB.build_extra(df, prof, ctx)
    sno = df['session_no'].to_numpy()
    want = np.array([pw[int(s)] for s in sno])
    assert np.allclose(ex['POC_W'][0], want, equal_nan=True)


# ------------------------------------------------------------------------------------------ 5. dedup + trần tổng hợp
def _pattern(Z):
    R = [(Z + 6, Z + 6.1, Z + 5.9, Z + 6, 0)] * 3
    for k in range(5):                                  # đi xuống Z+6 → Z+1, delta âm (move = 6 giá)
        o = Z + 6 - k
        R.append((o, o + 0.1, o - 1.1, o - 1, -20))
    R.append((Z + 1.0, Z + 1.1, Z + 0.0, Z + 0.2, -10))  # cụm 3 nến chạm Z, thân/|delta| giảm
    R.append((Z + 0.2, Z + 0.4, Z - 0.1, Z + 0.7, -6))
    R.append((Z + 0.5, Z + 0.6, Z - 0.2, Z + 0.3, -3))
    R.append((Z + 0.0, Z + 1.1, Z - 0.1, Z + 1.0, 15))   # nến xác nhận BUY
    R += [(Z + 1, Z + 1.1, Z + 0.9, Z + 1, 0)] * 10
    return R


def _synth_P(levels, zs=(100.0,)):
    rows = [(115, 125, 115, 120, 0)] + [(120, 120.1, 119.9, 120, 0)] * 40
    for z in zs:
        rows += _pattern(z)
    t = pd.date_range('2026-09-01 14:00', periods=len(rows), freq='min')     # 21:00 VN, pha Mỹ
    d = pd.DataFrame({'bar_idx': range(len(rows)), 'datetime': t, 'open': [r[0] for r in rows], 'high': [r[1] for r in rows],
                      'low': [r[2] for r in rows], 'close': [r[3] for r in rows], 'volume': 10, 'delta': [r[4] for r in rows]})
    df = K._enrich(d)
    n = len(df)
    ex = {nm: (np.full(n, float(v)), ZB.ZTYPE_OF[nm]) for nm, v in levels}
    return SB.prepare(df, K.build_profiles(df, None), ex), tuple(nm for nm, _ in levels)


def test_dedup_same_price():
    P, zs = _synth_P([('POC_D', 100.0), ('HVN_D1', 100.0)])
    e = SB.detect(P, 0.5, 3, zones=zs)
    assert len(e) == 1
    assert e[0]['ztype'] == 'POC_D' and e[0]['zone'] == 'POC_D' and e[0]['zones_hit'] == ['POC_D', 'HVN_D1'] and e[0]['side'] == 1
    # đảo thứ tự chèn (HVN_D1 trước) ⇒ ưu tiên đổi theo thứ tự P['Z']
    P2, zs2 = _synth_P([('HVN_D1', 100.0), ('POC_D', 100.0)])
    e2 = SB.detect(P2, 0.5, 3, zones=zs2)
    assert e2[0]['ztype'] == 'HVN_D' and e2[0]['zones_hit'] == ['HVN_D1', 'POC_D']


def test_cap_per_ztype_session():
    lv = [('HVN_D1', 100.0), ('HVN_D2', 90.0), ('HVN_D3', 80.0)]
    P, zs = _synth_P(lv, zs=(100.0, 90.0, 80.0))
    e = SB.detect(P, 0.5, 3, zones=zs)
    assert [x['zone'] for x in e] == ['HVN_D1', 'HVN_D2']          # 3 ca hợp lệ cùng loại cùng phiên ⇒ giữ 2 đầu
    # khác loại thì không bị trần chung: POC_D ở 80 ⇒ có lệnh thứ 3
    P3, zs3 = _synth_P([('HVN_D1', 100.0), ('HVN_D2', 90.0), ('POC_D', 80.0)], zs=(100.0, 90.0, 80.0))
    assert [x['ztype'] for x in SB.detect(P3, 0.5, 3, zones=zs3)] == ['HVN_D', 'HVN_D', 'POC_D']


# ------------------------------------------------------------------------------------------ 6. dời vùng
def test_shift_zero_and_nonzero():
    c = full()
    df, prof, extra, P = c['df'], c['prof'], c['extra'], c['P']
    sno = df['session_no'].to_numpy()
    nS = int(sno.max()) + 1
    S0 = ZB.shifted(extra, P['zc'], np.zeros(nS), sno)
    assert tuple(S0) == ZB.ZONE_ORDER
    P0 = SB.prepare(df, prof, S0)
    assert [key(e) for e in SB.detect(P0, 0.5, 3, zones=ZB.ZONES_V2)] == [key(e) for e in SB.detect(P, 0.5, 3, zones=ZB.ZONES_V2)]
    d = ZB.shift_matrix(nS, B2.REPS, B2.SHIFT_LO, B2.SHIFT_HI, B2.SHIFT_SEED)[:, 7]
    S1 = ZB.shifted(extra, P['zc'], d, sno)
    Pk = SB.prepare(df, prof, S1)
    for nm in ZB.ZONE_ORDER:
        assert np.allclose(Pk['Z'][nm], P['Z'][nm] + d[sno], equal_nan=True), nm
        assert Pk['ztype'][nm] == ZB.ZTYPE_OF[nm]
    assert (Pk['warm']['VWAP_D'] == P['warm']['VWAP_D']).all() and (Pk['warm']['VWAP_W'] == P['warm']['VWAP_W']).all()
    assert np.abs(d).min() >= 3.0 and np.abs(d).max() <= 15.0


def test_shift_matrix_same_as_vcl():
    import benzo_vcl as BV
    D = BV.Data()
    m = ZB.shift_matrix(D.dsh.shape[0], B2.REPS, B2.SHIFT_LO, B2.SHIFT_HI, B2.SHIFT_SEED)
    assert np.allclose(m, D.dsh[:, 1:])


# ------------------------------------------------------------------------------------------ 7. ĐC2
def test_control_patched_map():
    c = full()
    df, extra, P = c['df'], c['extra'], c['P']
    before = dict(K.ZONE_NAME2COL)
    zcols = pd.concat([P['zc'], ZB.zone_table(extra)], axis=1)
    lvl = extra['HVN_D2'][0]
    i0 = int(np.flatnonzero(~np.isnan(lvl))[0])
    ent = [dict(idx=i0, side=1, entry=float(P['cl'][i0]), sl=float(P['cl'][i0]) - 2, tp=float(P['cl'][i0]) + 6, setup='B', zone='HVN_D2')]
    with B2._patched_map(extra):
        assert K.ZONE_NAME2COL['HVN_D2'] == 'HVN_D2' and K.ZONE_NAME2COL['VWAP_W'] == 'vwap_w'
        ce = K.control_sample(df, zcols, P['modecode'], entries=ent, n_random=50, seed=3)
    assert K.ZONE_NAME2COL == before and 'HVN_D2' not in K.ZONE_NAME2COL
    assert len(ce) > 0
    cl, hi, lo = P['cl'], P['hi'], P['lo']
    for x in ce:
        i = x['idx']
        assert abs(cl[i] - lvl[i]) <= 1.0 or (lo[i] <= lvl[i] <= hi[i]), x
        assert P['modecode'].iloc[i] == P['modecode'].iloc[i0]
    # dict được khôi phục cả khi có lỗi trong khối with
    try:
        with B2._patched_map(extra):
            raise RuntimeError('x')
    except RuntimeError:
        pass
    assert K.ZONE_NAME2COL == before


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-q']))
