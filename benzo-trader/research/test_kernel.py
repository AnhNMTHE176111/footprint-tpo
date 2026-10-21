"""Test kernel.py. Chay: python -m pytest benzo-trader/research/test_kernel.py -q   (hoac python test_kernel.py)."""
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
D90 = os.path.join(ROOT, 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260723-20261021_90d')

_cache = {}


def real():
    """Nap 1 lan: df, prof, raw, levels cua file 90d."""
    if not _cache:
        raw = pd.read_csv(D90 + '_bars.csv', parse_dates=['datetime'])
        df = K._enrich(raw)
        lv = pd.read_csv(D90 + '.csv', usecols=['bar_idx', 'price', 'volume'])
        prof = K.build_profiles(df, lv)
        _cache.update(raw=raw, df=df, lv=lv, prof=prof)
    return _cache


def synth(rows, start='2026-09-01 12:00'):
    """rows = list (open, high, low, close[, volume, delta]); nen M1 lien tiep tu start (UTC)."""
    t = pd.date_range(start, periods=len(rows), freq='min')
    d = pd.DataFrame({'bar_idx': range(len(rows)), 'datetime': t,
                      'open': [r[0] for r in rows], 'high': [r[1] for r in rows], 'low': [r[2] for r in rows],
                      'close': [r[3] for r in rows], 'volume': [r[4] if len(r) > 4 else 10 for r in rows],
                      'delta': [r[5] if len(r) > 5 else 0 for r in rows]})
    return K._enrich(d)


# ---------------------------------------------------------------- (a) so phien
def test_a_session_count():
    c = real()
    n = c['df']['session_no'].nunique()
    assert abs(n - 65) <= 1, n
    st = K.session_table(c['df'])
    assert len(st) == n and st['n'].sum() == len(c['df'])
    # ten phien = ngay cua nen cuoi
    last = c['df'].groupby('session_no')['t_utc'].last().dt.strftime('%Y-%m-%d').tolist()
    assert last == st['session_id'].tolist() or all(a == b[:10] for a, b in zip(last, st['session_id']))
    assert int(st['volume'].median()) == 133471          # khop plan (trung vi hop dong/phien)


def test_phase_and_dst():
    df = synth([(1, 1, 1, 1)] * 3, '2026-09-01 12:00')           # 19:00 VN mua he
    assert df['phase'].iloc[0] == 'US' and df['sm'].iloc[0] == 840
    df = synth([(1, 1, 1, 1)] * 3, '2026-09-01 22:00')           # 05:00 VN
    assert df['phase'].iloc[0] == 'A' and df['sm'].iloc[0] == 0
    df = synth([(1, 1, 1, 1)] * 3, '2026-09-01 05:30')           # 12:30 VN
    assert df['phase'].iloc[0] == 'EU'
    df = synth([(1, 1, 1, 1)] * 3, '2026-12-01 13:00')           # mua dong: moc My lui +1h => 20:00 VN thuc = 19:00 'neo My'
    assert df['sm'].iloc[0] == 840 and df['phase'].iloc[0] == 'US'
    df = synth([(1, 1, 1, 1)] * 3, '2026-09-01 12:20')
    assert bool(df['is_us_open_window'].iloc[0])


def test_splice_detection():
    # 3 phien nho, giua phien 1 va 2 co khoang nghi 61 phut va nhay 60 gia
    rows = [(100, 101, 99, 100)] * 5
    t1 = pd.date_range('2026-09-01 12:00', periods=5, freq='min')
    t2 = pd.date_range('2026-09-01 13:05', periods=5, freq='min')
    d = pd.DataFrame({'bar_idx': range(10), 'datetime': list(t1) + list(t2),
                      'open': [100] * 5 + [160] * 5, 'high': [101] * 5 + [161] * 5, 'low': [99] * 5 + [159] * 5,
                      'close': [100] * 5 + [160] * 5, 'volume': 10, 'delta': 0})
    df = K._enrich(d)
    assert df['session_no'].nunique() == 2
    assert df['splice_jump'].sum() == 1 and df['splice'].all()
    # nhay lon nhung qua cuoi tuan (khoang nghi > 150 phut) KHONG phai cho noi
    t2 = pd.date_range('2026-09-04 22:00', periods=5, freq='min')
    d['datetime'] = list(t1) + list(t2)
    assert K._enrich(d)['splice_jump'].sum() == 0


# ---------------------------------------------------------------- (c) ValueArea / HVN
def test_c_value_area_by_hand():
    p = [100.0, 100.2, 100.4, 100.6, 100.8, 101.0, 101.2]
    # tong 25, muc tieu 17.5; POC=100.4 (10); ben tren 6+3=9 >= ben duoi 2+1=3 => acc 19 >= 17.5, hi len 2 hang
    poc, vah, val = K.value_area(p, [1, 2, 10, 6, 3, 2, 1])
    assert (poc, vah, val) == (100.4, 100.8, 100.4)
    # ben duoi manh hon: POC 100.4 (10), duoi 6+3=9, tren 2+1=3 => lo ve 100.0
    poc, vah, val = K.value_area(p, [3, 6, 10, 2, 1, 1, 1])
    assert (poc, vah, val) == (100.4, 100.4, 100.0)
    # can bang -> chon ben tren (up >= dn)
    poc, vah, val = K.value_area(p, [2, 3, 12, 3, 2, 1, 1])
    assert val == 100.4 and vah == 100.8
    # profile 1 hang
    assert K.value_area([100.0], [5]) == (100.0, 100.0, 100.0)
    # POC hoa => hang thap nhat (giong C# chi so dau tien)
    assert K.value_area(p, [1, 9, 1, 9, 1, 1, 1])[0] == 100.2
    # 70% bao toan: VA luon chua >= 70% volume tren profile ngau nhien
    rng = np.random.default_rng(1)
    for _ in range(50):
        w = rng.integers(1, 100, 40).astype(float)
        pr = 100 + 0.2 * np.arange(40)
        poc, vah, val = K.value_area(pr, w)
        m = (pr >= val) & (pr <= vah)
        assert w[m].sum() >= 0.70 * w.sum() - 1e-9 and val <= poc <= vah


def test_c_hvn_lvn():
    pr = 100 + 0.2 * np.arange(120)
    w = np.full(120, 10.0)
    w += 400 * np.exp(-((np.arange(120) - 30) / 3.0) ** 2) + 300 * np.exp(-((np.arange(120) - 90) / 3.0) ** 2)
    w[60] = 0.5
    hv = K.find_hvn(pr, w)
    assert abs(hv[0][0] - pr[30]) < 0.41 and abs(hv[1][0] - pr[90]) < 0.41
    assert hv[0][1] > hv[1][1] > 1.5
    lv = K.find_lvn(pr, w)
    assert any(abs(p - pr[60]) < 0.41 for p, _ in lv) or len(lv) >= 1


# ---------------------------------------------------------------- (e) VWAP
def test_e_vwap_week_resets():
    c = real()
    df = c['df']
    vw = K.vwap_series(df)
    tp = ((df['high'] + df['low'] + df['close']) / 3).to_numpy()
    st = K.session_table(df)
    # dau moi tuan CME (nen dau tien sau khoang trong > 30 gio): vwap_w = typical cua chinh nen do (neu volume > 0)
    wk_first = np.flatnonzero(np.r_[True, np.diff(df['week_no'].to_numpy()) != 0])
    assert len(wk_first) >= 12
    for i in wk_first:
        if df['volume'].iloc[i] > 0:
            assert abs(vw['vwap_w'].iloc[i] - tp[i]) < 1e-9
    # phien dau khong phai dau tuan: vwap_d reset nhung vwap_w tiep tuc
    for k in st.index[1:]:
        a = int(st['start_pos'].loc[k])
        if df['week_no'].iloc[a] == df['week_no'].iloc[a - 1] and df['volume'].iloc[a] > 0:
            assert abs(vw['vwap_d'].iloc[a] - tp[a]) < 1e-9
            assert abs(vw['vwap_w'].iloc[a] - tp[a]) > 1e-9 or df['volume'].iloc[a - 1] == 0
            break
    # doi chieu tinh tay cho 1 tuan
    w = df['week_no'].iloc[3000]
    m = (df['week_no'] == w).to_numpy()
    v = df['volume'].to_numpy(float)
    manual = np.cumsum((tp * v)[m]) / np.cumsum(v[m])
    ok = np.cumsum(v[m]) > 0
    assert np.allclose(vw['vwap_w'].to_numpy()[m][ok], manual[ok])
    # khong nhin truoc: cat df giua chung thi chuoi giu nguyen
    cut = K._enrich(c['raw'].iloc[:5000])
    v2 = K.vwap_series(cut)
    assert np.allclose(v2['vwap_w'].to_numpy(), vw['vwap_w'].to_numpy()[:5000])
    assert np.allclose(v2['vwap_d'].to_numpy(), vw['vwap_d'].to_numpy()[:5000])


# ---------------------------------------------------------------- (d)(f) simulate + chi phi
def _sim_df():
    #       o    h    l    c
    rows = [(100, 100.5, 99.5, 100),      # 0 nen vao
            (100, 101, 99.8, 100.8),      # 1
            (100.8, 102.2, 100.5, 102),   # 2 cham 102
            (102, 103.5, 99.0, 100),      # 3 rong: cham ca 103 va 99
            (100, 100.5, 97.5, 98),       # 4
            (98, 99, 96, 97)]
    return synth(rows)


def test_d_simulate_tp_sl():
    df = _sim_df()
    # BUY tai 100, SL 99, TP 102 (2R). nen 1 low 99.8 > 99; nen 2 high 102.2 >= 102 => TP
    t = K.simulate(df, [dict(idx=0, side=1, entry=100, sl=99, tp=102, setup='x', zone='z', note='')], cost=0.0)
    assert t['outcome'].iloc[0] == 'TP' and t['exit_idx'].iloc[0] == 2 and abs(t['r'].iloc[0] - 2.0) < 1e-9
    # BUY tai 102 (idx 2), SL 100.5, TP 103.5: nen 3 cham CA hai (high 103.5, low 99) => SL
    t = K.simulate(df, [dict(idx=2, side=1, entry=102, sl=100.5, tp=103.5, setup='x', zone='z', note='')], cost=0.0)
    assert t['outcome'].iloc[0] == 'SL' and t['exit_idx'].iloc[0] == 3 and abs(t['r'].iloc[0] + 1.0) < 1e-9
    # SELL tai 100 (idx 3), SL 101, TP 97: nen 4 low 97.5, nen 5 low 96 => TP o nen 5
    t = K.simulate(df, [dict(idx=3, side=-1, entry=100, sl=101, tp=97, setup='x', zone='z', note='')], cost=0.0)
    assert t['outcome'].iloc[0] == 'TP' and t['exit_idx'].iloc[0] == 5 and abs(t['r'].iloc[0] - 3.0) < 1e-9
    # het du lieu => OPEN
    t = K.simulate(df, [dict(idx=3, side=-1, entry=100, sl=110, tp=50, setup='x', zone='z', note='')], cost=0.0)
    assert t['outcome'].iloc[0] == 'OPEN'
    # SL/TP sai phia => loi
    try:
        K.simulate(df, [dict(idx=0, side=1, entry=100, sl=101, tp=102)])
        assert False
    except ValueError:
        pass


def test_d_one_at_a_time():
    df = _sim_df()
    e1 = dict(idx=0, side=1, entry=100, sl=99, tp=102)       # thoat o nen 2
    e2 = dict(idx=1, side=1, entry=100.8, sl=99.8, tp=102.8)  # vao khi lenh 1 con mo => bi bo
    e3 = dict(idx=2, side=1, entry=102, sl=100.5, tp=103.5)  # idx == exit_idx cua lenh 1 => duoc vao
    assert len(K.simulate(df, [e1, e2, e3])) == 2
    assert len(K.simulate(df, [e1, e2, e3], one_at_a_time=False)) == 3


def test_f_cost_deducted():
    df = _sim_df()
    e = dict(idx=0, side=1, entry=100, sl=99, tp=102)
    r0 = K.simulate(df, [e], cost=0.0)['r'].iloc[0]
    r1 = K.simulate(df, [e])['r'].iloc[0]                    # mac dinh 0,2 gia
    assert abs(r0 - 2.0) < 1e-9 and abs(r1 - (2.0 - 0.2 / 1.0)) < 1e-9
    assert K.CONST['cost'] == 0.2
    e = dict(idx=2, side=1, entry=102, sl=100.5, tp=103.5)   # SL: -1R va tru them 0,2/1,5
    assert abs(K.simulate(df, [e])['r'].iloc[0] - (-1 - 0.2 / 1.5)) < 1e-9
    t = K.simulate(df, [dict(idx=3, side=-1, entry=100, sl=101, tp=97)])
    assert abs(t['pts'].iloc[0] - (3 - 0.2)) < 1e-9


def test_risk():
    df = synth([(100, 100.4, 99.8, 100.2)] * 4 + [(100.2, 100.6, 99.4, 100.5)])   # nen cuoi: bien do 1.2
    # BUY o 100.5, cau truc 99.4 => SL = 99.1 (khoang 1.4 >= san 1.2)
    r = K.risk(df, 4, 1, 99.4, rr=3)
    assert abs(r['sl'] - 99.1) < 1e-6 and abs(r['tp'] - (100.5 + 3 * 1.4)) < 1e-6 and not r['floor_applied']
    # cau truc rat gan => ap san 1.2
    r = K.risk(df, 4, 1, 100.3, rr=2)
    assert r['floor_applied'] and abs((100.5 - r['sl']) - 1.2) < 1e-6
    # SELL: cau truc 101.0 => SL 101.3 (khoang 0.8 < san 1.2 => 1.2)
    r = K.risk(df, 4, -1, 101.0, rr=2)
    assert abs((r['sl'] - 100.5) - 1.2) < 1e-6 and r['tp'] < 100.5
    # tran 4 gia
    assert K.risk(df, 4, 1, 95.0) is None
    assert K.risk(df, 4, 1, 96.9) is not None and K.risk(df, 4, 1, 96.7) is None


# ---------------------------------------------------------------- helpers
def test_helpers():
    rows = [(100, 101, 100, 100.5)] * 12 + [(100, 103, 99, 102)] + [(100, 101, 100, 100.5)] * 4
    df = synth(rows)
    assert abs(K.median_range(df).iloc[-1] - 1.0) < 1e-9
    assert K.median_range(df).iloc[:9].isna().all()
    bs = K.bars_since_biggest_bar(df)
    assert bs.iloc[12] == 0 and bs.iloc[13] == 1 and bs.iloc[16] == 4 and bs.iloc[11] == 11 - 0
    b = K.biggest_bar_so_far_in_session(df)
    assert b['big_range'].iloc[11] == 1.0 and b['big_range'].iloc[12] == 4.0 and b['big_pos'].iloc[-1] == 12
    # CF
    row = dict(open=100, high=101, low=99.9, close=100.9, delta=30)
    assert K.is_confirm_bar(row, 1, 20) and not K.is_confirm_bar(row, -1, 20) and not K.is_confirm_bar(row, 1, 40)
    row2 = dict(open=100, high=101, low=99, close=100.2, delta=30)           # than 0.2 < 50% bien do
    assert not K.is_confirm_bar(row2, 1, 20)
    mad = pd.Series([20.0] * len(df), index=df.index)
    df2 = df.assign(delta=[0] * 12 + [50] + [0] * 4)
    assert K.confirm_bars(df2, 1, mad).tolist()[12] and K.confirm_bars(df2, 1, mad).sum() == 1


def test_zigzag_basic_and_nolook():
    ys = [100, 101, 102.5, 104, 103, 101.5, 100.5, 101, 103.2, 105]
    rows = [(y, y + 0.2, y - 0.2, y) for y in ys]
    df = synth(rows)
    zz = K.zigzag(df, 2.0)
    kinds = [(z['kind'], z['pos']) for z in zz]
    assert ('H', 3) in kinds and ('L', 6) in kinds
    for z in zz:
        assert z['confirm_pos'] >= z['pos']
    h = [z for z in zz if z['kind'] == 'H' and z['pos'] == 3][0]
    # dinh 104.2 chi duoc xac nhan khi low <= 102.2 (nen 5: low 101.3)
    assert h['confirm_pos'] == 5
    c = real()
    full = K.zigzag(c['df'])
    for i in (5000, 30000, 70000):
        part = K.zigzag(c['df'].iloc[:i + 1])
        assert [z for z in full if z['confirm_pos'] <= i] == [z for z in part if z['confirm_pos'] <= i]


# ---------------------------------------------------------------- che do (mode)
def test_mode_series_synthetic():
    # band VA Au [100, 110] co tu dau; 5 nen M5 bat dau 12:00 UTC (19:00 VN)
    closes = [105] * 5 + [111] * 5 + [114] * 5 + [108] * 5 + [105] * 5
    rows = [(c, c + 0.2, c - 0.2, c) for c in closes]
    df = synth(rows, '2026-09-01 12:00')
    z = pd.DataFrame({c: np.nan for c in K.ZONE_COLS}, index=df.index)
    z['eu_vah'], z['eu_val'] = 110.0, 100.0
    m5 = K.m5_bars(df, z)
    assert len(m5) == 5 and m5['out'].tolist() == [0, 1, 1, 0, 0] and abs(m5['out_dist'].iloc[1] - 1.0) < 1e-9
    md = K.mode_series(df, z)
    assert (md.iloc[0:5] == 'NA').all()                  # chua co M5 nao dong
    assert (md.iloc[5:10] == 'BALANCE').all()            # M5 1 (12:00-12:05) dong trong band
    assert (md.iloc[10:15] == 'BREAK_UP').all()          # M5 2 dong ngoai, dist 1 < 3
    assert (md.iloc[15:20] == 'TREND_UP').all()          # M5 3: 2 nen lien tiep ngoai, dist 4 >= 3
    assert (md.iloc[20:25] == 'BALANCE').all()           # M5 4 dong lai trong band => cu pha hut
    # xuong
    closes = [105] * 5 + [99] * 5 + [95] * 5 + [95] * 5
    df = synth([(c, c + 0.2, c - 0.2, c) for c in closes], '2026-09-01 12:00')
    z = pd.DataFrame({c: np.nan for c in K.ZONE_COLS}, index=df.index)
    z['eu_vah'], z['eu_val'] = 110.0, 100.0
    md = K.mode_series(df, z)
    assert (md.iloc[10:15] == 'BREAK_DN').all() and (md.iloc[15:20] == 'TREND_DN').all()
    # khong co band => NA
    z[['eu_vah', 'eu_val']] = np.nan
    assert (K.mode_series(df, z) == 'NA').all()
    # M5 dang chay KHONG duoc dung: nen M1 thu 5 cua M5 dong ngoai van chua thay no
    md = K.mode_series(synth([(c, c + 0.2, c - 0.2, c) for c in [105] * 5 + [111] * 5], '2026-09-01 12:00'),
                       pd.DataFrame({**{c: np.nan for c in K.ZONE_COLS}, 'eu_vah': 110.0, 'eu_val': 100.0}, index=range(10)))
    assert (md.iloc[5:10] == 'BALANCE').all()


# ---------------------------------------------------------------- (b) khong nhin truoc tren du lieu that
def _norm(x):
    if isinstance(x, dict):
        return {k: _norm(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_norm(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return round(float(x), 9)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def _cut_pos(df, sno, lo, hi):
    """vi tri dau tien trong phien sno co sm trong [lo, hi)"""
    m = (df['session_no'].to_numpy() == sno) & (df['sm'].to_numpy() >= lo) & (df['sm'].to_numpy() < hi)
    return int(np.flatnonzero(m)[0])


def test_b_no_lookahead_zones():
    c = real()
    df, lv, raw, prof = c['df'], c['lv'], c['raw'], c['prof']
    full_ctx = K._Ctx(df, prof)
    zc_full = K.zone_columns(df, prof, full_ctx)
    mf_full = K.mode_frame(df, zc_full)
    cuts = []
    for sno in (30, 45, 58):
        for lo, hi in ((300, 301), (845, 850), (925, 930), (1000, 1010)):    # truoc Au chot / sau Au / sau IB / muon
            cuts.append((sno, _cut_pos(df, sno, lo, hi)))
    cuts.append((45, _cut_pos(df, 45, 700, 710) + 3))
    for sno, i in cuts:
        dfc = K._enrich(raw.iloc[:i + 1])
        lvc = lv[lv['bar_idx'] <= raw['bar_idx'].iloc[i]]
        profc = K.build_profiles(dfc, lvc)
        a = K.zones_for_session(df, sno, prof, as_of=i, ctx=full_ctx)
        b = K.zones_for_session(dfc, sno, profc, as_of=i)
        assert _norm(a) == _norm(b), (sno, i)
        zc_cut = K.zone_columns(dfc, profc)
        for col in K.ZONE_COLS:
            assert np.allclose(zc_cut[col].to_numpy(), zc_full[col].to_numpy()[:i + 1], equal_nan=True), (col, sno, i)
        mfc = K.mode_frame(dfc, zc_cut)
        assert (mfc['mode'].to_numpy() == mf_full['mode'].to_numpy()[:i + 1]).all(), (sno, i)
        # cac ham helper
        assert np.allclose(K.median_range(dfc).to_numpy(), K.median_range(df).to_numpy()[:i + 1], equal_nan=True)
        assert (K.bars_since_biggest_bar(dfc).to_numpy() == K.bars_since_biggest_bar(df).to_numpy()[:i + 1]).all()
        # as_of=None kem ready_pos: gia tri chi duoc dung tu ready_pos tro di
        zf = K.zones_for_session(df, sno, prof, ctx=full_ctx)
        if a['va_eu'] is None and zf['va_eu'] is not None:
            assert zf['va_eu']['ready_pos'] > i
        if a['ib'] is None and zf['ib'] is not None:
            assert zf['ib']['ready_pos'] > i
    # VA Au truoc 19:00 VN phai la None; sau do co gia tri
    i0 = _cut_pos(df, 45, 700, 710)
    assert K.zones_for_session(df, 45, prof, as_of=i0, ctx=full_ctx)['va_eu'] is None
    assert K.zones_for_session(df, 45, prof, as_of=_cut_pos(df, 45, 845, 850), ctx=full_ctx)['va_eu'] is not None
    # IB: None truoc 20:20, co sau do
    assert K.zones_for_session(df, 45, prof, as_of=_cut_pos(df, 45, 845, 850), ctx=full_ctx)['ib'] is None
    assert K.zones_for_session(df, 45, prof, as_of=_cut_pos(df, 45, 925, 930), ctx=full_ctx)['ib'] is not None


def test_zones_content_sanity():
    c = real()
    df, prof = c['df'], c['prof']
    z = K.zones_for_session(df, 50, prof)
    y = z['yday']
    assert y['val'] <= y['poc'] <= y['vah']
    # VA hom qua phai khop tinh lai tu per-level truc tiep
    lv = c['lv']
    q = y['session_no']
    st = K.session_table(df)
    b0, b1 = int(st['start_pos'].loc[q]), int(st['end_pos'].loc[q])
    sub = lv[(lv['bar_idx'] >= df['bar_idx'].iloc[b0]) & (lv['bar_idx'] <= df['bar_idx'].iloc[b1])]
    rows = sub.assign(r=np.rint(sub['price'] / 0.2).astype(int)).groupby('r')['volume'].sum().sort_index()
    poc, vah, val = K.value_area(rows.index.to_numpy() * 0.2, rows.to_numpy())
    assert abs(poc - y['poc']) < 1e-6 and abs(vah - y['vah']) < 1e-6 and abs(val - y['val']) < 1e-6
    assert all(r >= K.CONST['hvn_gate'] for _, r in z['hvn_day'])
    assert len(z['hvn_day']) <= 3 and len(z['lvn_day']) <= 2
    fl = K.flat_zones(K.zones_for_session(df, 50, prof, as_of=int(st['end_pos'].loc[50])), 4000.0, 4001.0)
    assert fl[0]['name'] == 'VWAP_W' and fl[0]['rank'] == 1 and fl[1]['name'] == 'VWAP_D'
    assert all(not f['fade'] for f in fl if f['name'].startswith('HVN'))
    # phien sau cho noi khong co 'yday' neu cho noi nam giua (khong co cho noi trong file 90d => luon co)
    assert z['splice_in_window'] is False


def test_naked_poc_rules():
    c = real()
    df, prof = c['df'], c['prof']
    ctx = K._Ctx(df, prof)
    st = ctx.st
    z = K.zones_for_session(df, 50, prof, ctx=ctx)
    for x in z['naked']:
        q = x['session_no']
        assert q < 50
        tp = x['touch_pos']
        poc = x['price']
        end = int(st['end_pos'].loc[q])
        sp0 = int(st['start_pos'].loc[50])
        if tp is None:
            seg = slice(end + 1, len(df))
        else:
            assert tp >= sp0
            seg = slice(end + 1, tp)
            assert df['low'].iloc[tp] <= poc <= df['high'].iloc[tp]
        assert not ((df['low'].iloc[seg] <= poc) & (df['high'].iloc[seg] >= poc)).any()


# ---------------------------------------------------------------- hieu nang + metrics + doi chung
def test_performance_pipeline():
    t0 = time.time()
    df = K.load_bars(D90 + '_bars.csv')
    prof = K.build_profiles(df, D90 + '.csv')
    zc = K.zone_columns(df, prof)
    mode = K.mode_series(df, zc)
    assert time.time() - t0 < 60
    assert len(zc) == len(df) == len(mode)
    # simulate 2000 lenh < 30 giay
    rng = np.random.default_rng(0)
    idx = np.sort(rng.choice(np.arange(100, len(df) - 3000), 2000, replace=False))
    ent = []
    for i in idx:
        s = int(rng.choice([-1, 1]))
        e = float(df['close'].iloc[i])
        ent.append(dict(idx=int(i), side=s, entry=e, sl=e - s * 2.0, tp=e + s * 4.0, setup='R', zone='VWAP_W', note=''))
    t1 = time.time()
    tr = K.simulate(df, ent, one_at_a_time=False)
    assert time.time() - t1 < 30 and len(tr) == 2000
    m = K.metrics(tr, df)
    assert m['n'] == 2000 and m['n_open'] == 0
    md = K.render_markdown(tr, df, 'test')
    assert 'TRAIN' in md and 'Vi du THANG' in md
    # chi phi: ky vong ngau nhien 2R-vs-1R khong the duong qua lon; kiem R TB < 0.5
    assert m['avg_r'] < 0.5


def test_control_sample():
    c = real()
    df, prof = c['df'], c['prof']
    zc = K.zone_columns(df, prof)
    mode = K.mode_series(df, zc)
    near = np.flatnonzero((np.abs(df['close'].to_numpy() - zc['vwap_w'].to_numpy()) <= 1.0) & (mode.to_numpy() != 'NA')
                          & (~df['thin'].to_numpy()))
    e = []
    for i in near[::400][:10]:
        r = K.risk(df, int(i), 1, float(df['low'].iloc[i]), rr=2)
        if r:
            e.append(dict(idx=int(i), side=1, entry=r['entry'], sl=r['sl'], tp=r['tp'], setup='T', zone='VWAP_W'))
    ctrl = K.control_sample(df, zc, mode, entries=e, n_random=5, seed=1)
    assert len(ctrl) > 0
    real_idx = {x['idx'] for x in e}
    for x in ctrl:
        i = x['idx']
        assert i not in real_idx and x['side'] == 1
        assert abs(df['close'].iloc[i] - zc['vwap_w'].iloc[i]) <= 1.0 or (df['low'].iloc[i] <= zc['vwap_w'].iloc[i] <= df['high'].iloc[i])
    # cach 2
    c2 = K.control_sample(df, zc, mode, side_filter=-1, zone='VWAP_D', n_total=30, seed=2)
    assert len(c2) > 0 and all(x['side'] == -1 for x in c2)
    # tai lap
    assert [x['idx'] for x in K.control_sample(df, zc, mode, entries=e, n_random=5, seed=1)] == [x['idx'] for x in ctrl]


if __name__ == '__main__':
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            t = time.time()
            try:
                fn()
                print('OK   %-40s %.1fs' % (name, time.time() - t))
            except Exception as ex:  # noqa: BLE001
                fails += 1
                import traceback
                traceback.print_exc()
                print('FAIL %s: %r' % (name, ex))
    sys.exit(1 if fails else 0)
