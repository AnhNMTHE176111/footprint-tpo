#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KB2_ZONES — thay/them neo VUNG CANH (M30SessionZones v2) cho nhanh QUAY_DAU (KB2).

Cau hoi cua nguoi hoc (2026-07-31): KB2 hien chi neo vao VWAP (n=27, EV+0.389, FAIL audit vi
mong). M30SessionZones v2 da loc ra "VUNG CANH" co cham diem (HVN tuan 70-95, HVN ngay 64-88,
naked POC 72, cum POC 78, bang gia tri 55) va gop hop luu da khung. Neo reversal vao CAC VUNG DO
thay vi/them vao VWAP thi co tang so lenh + giu EV khong?

Cach lam (bam ky luat AUDIT_V7 — moi so la output that, co doi chung ngau nhien):
  1. GOLDEN: tai lap dung KB2 baseline VWAP-only (n=27 EV+0.389) truoc khi doi bat ky gi.
  2. Dung LAI nguyen ham cua verify_zones_v2.py (port 1-1 tu C#) — khong viet lai logic vung.
  3. Vung tinh CAUSAL: chot tai moi lan DONG PHIEN, chi dung du lieu qua khu, dung suot phien sau.
  4. Detector zone = ban copy y het detect() cua imp_reversal_sweep.py, CHI thay `vwap` -> `zone`.
  5. DOI CHUNG NGAU NHIEN: lap lai toan bo voi vung bi dich ngau nhien (giu so luong/phan bo
     khoang cach) — bat buoc, vi BACKTEST-ZONES-V2.md da cho thay v2 KHONG hon ngau nhien.

Chay: python3 quantower-entry-signal/research/wyckoff/kb2_zones.py
"""
import os
import sys
import random
from collections import defaultdict
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'quantower-entry-signal', 'research'))
sys.path.insert(0, os.path.join(ROOT, 'quantower-tpo-suite'))

import reversal_vwap as rv                 # loader + hit()  (dung chung voi imp_reversal_sweep)
import imp_reversal_sweep as KB2           # LIVE dict + detect() baseline (GOLDEN)
import verify_zones_v2 as Z                # port 1-1 M30SessionZones v2

TICK = rv.TICK
VN_OFFSET = timedelta(hours=7)             # dxFeed 'Time left' la UTC (AUDIT/WYCKOFF_V6_PLAN Buoc 1)

# nhom "VUNG CANH" chinh theo mo ta cua nguoi hoc (manh -> yeu)
MAIN_TYPES = ('hvn_week', 'hvn_day', 'naked_poc', 'poc_cluster', 'value_band')
NOISE_TYPES = ('va_edge', 'priorhl')       # VAH/VAL/dinh-day tung phien = nhom bi coi la nhieu


# ============================================================================
# 1. M30 bars + phien (label theo gio VN, du lieu la UTC)
# ============================================================================
def to_m30(B1):
    """Gop nen M1 -> M30 theo moc :00/:30. Giu index nen M1 cuoi cua moi M30."""
    out = []
    cur = None
    for i, b in enumerate(B1):
        key = (b['dt'].date(), b['dt'].hour, b['dt'].minute // 30)
        if cur is None or cur['key'] != key:
            if cur is not None:
                out.append(cur)
            cur = dict(key=key, dt=b['dt'], o=b['o'], h=b['hi'], l=b['lo'], c=b['c'],
                       vol=b['v'], i1=i)
        else:
            cur['h'] = max(cur['h'], b['hi'])
            cur['l'] = min(cur['l'], b['lo'])
            cur['c'] = b['c']
            cur['vol'] += b['v']
            cur['i1'] = i
    if cur is not None:
        out.append(cur)
    return out


def label_vn(dt_utc, asia=300, europe=750, us=1140):
    """Z.label_of nhung doi UTC -> gio VN truoc khi phan phien."""
    d = dt_utc + VN_OFFSET
    m = d.hour * 60 + d.minute
    if asia <= m < europe:
        return 'A'
    if europe <= m < us:
        return 'AU'
    return 'MY'


def sessions_of_m30(M):
    out, cur, start, prev = [], None, 0, None
    for i, b in enumerate(M):
        lab = label_vn(b['dt'])
        split = prev is None or lab != cur or (b['dt'] - prev).total_seconds() / 60 > 75
        if split:
            if prev is not None:
                out.append((cur, start, i - 1))
            cur, start = lab, i
        prev = b['dt']
    if prev is not None:
        out.append((cur, start, len(M) - 1))
    return out


# ============================================================================
# 2. Chuoi vung CAUSAL: chot tai moi lan dong phien
# ============================================================================
def build_zone_series(M, sessions, jitter=None, rng=None):
    """
    Tra ve list (dt_hieu_luc, zones_all, zones_top5).
    Chot tai nen cuoi cua tung phien -> hieu luc tu nen M30 ke tiep. Chi dung sessions[:k+1]
    (phien da dong) + bars[:to+1] => khong nhin tuong lai.

    jitter: None = vung that. So thuc = doi chung ngau nhien: moi tam vung bi dich
            +/- U(0.5, 1.5) x jitter (gia), giu nguyen SO LUONG va do phan tan.
    """
    series = []
    for k, (lab, fr, to) in enumerate(sessions):
        if k < 4:                                   # can it nhat vai phien de co profile
            continue
        prefix = M[:to + 1]
        now = M[to]['c']
        try:
            zs_all = Z.find_zones(prefix, sessions[:k + 1], now, version='v2',
                                  max_zones=999, zone_range_atr=1e9)
            zs_top = Z.find_zones(prefix, sessions[:k + 1], now, version='v2')
        except Exception:
            continue
        zs_all = [z for z in zs_all if z.type != 'lvn']
        zs_top = [z for z in zs_top if z.type != 'lvn']
        if jitter:
            def shift(zl):
                out = []
                for z in zl:
                    d = jitter * rng.uniform(0.5, 1.5) * rng.choice((-1, 1))
                    nz = Z.Zone(z.center + d, z.lo + d, z.hi + d, z.type,
                                z.side, z.strength, z.label, z.frames)
                    out.append(nz)
                return out
            zs_all, zs_top = shift(zs_all), shift(zs_top)
        series.append((M[to]['dt'], zs_all, zs_top))
    return series


def zone_lookup(series):
    """Ham tra vung dang hieu luc tai thoi diem dt (vung chot gan nhat TRUOC dt)."""
    dts = [s[0] for s in series]

    def get(dt, which):
        import bisect
        k = bisect.bisect_right(dts, dt) - 1
        if k < 0:
            return []
        return series[k][1] if which == 'all' else series[k][2]
    return get


# ============================================================================
# 3. Detector: copy detect() cua imp_reversal_sweep, thay VWAP -> ZONE
# ============================================================================
def detect_zone(B, getz, which='all', min_str=0.0, types=None, mode='zone',
                zone_tol_t=12, **kw):
    """
    mode: 'zone'  = chi neo vung (bo VWAP)
          'union' = VWAP HOAC vung (tang so lenh)
          'both'  = doi hoi CA VWAP VA vung (bo loc hop luu)
    Moi gate khac (vol/warmup/rau/cpos/body/VSA/trend/SL/cooldown/RR) giu Y HET LIVE.
    """
    P = dict(KB2.LIVE)
    P.update(kw)
    vol_floor = P['vol_floor']; warmup = P['warmup']
    vtol = P['vwap_tol_t'] * TICK
    ztol = zone_tol_t * TICK
    appro = P['approach_bars']
    wick = P['wick_frac']; h = P['cpos_h']; body = P['body_min']; vsac = P['vsa_conf']
    tf = P['trend_filter']; tN = P['trend_bars']; ttol = P['trend_tol_t']
    buf = P['sl_buf_t'] * TICK; cap = P['sl_cap_t']; rmin = P['risk_min']; cd = P['cooldown']
    cpos_lo, cpos_hi = 0.5 - h, 0.5 + h
    N = len(B); raw = []
    start = max(rv.VSA_MA + 2, tN if tf else 0)
    for i in range(start, N):
        b = B[i]
        if not (b['v'] >= vol_floor and b['since_gap'] >= warmup and b['vma'] >= vol_floor * 0.6):
            continue
        rng_ = b['rng']
        if rng_ <= 0:
            continue
        # --- can dung chung (khong phu thuoc moc gia) ---
        rej_short_core = (b['uw'] >= wick * rng_ and b['cpos'] <= cpos_lo
                          and b['brat'] >= body and b['vratio'] >= vsac)
        rej_long_core = (b['lw'] >= wick * rng_ and b['cpos'] >= cpos_hi
                         and b['brat'] >= body and b['vratio'] >= vsac)
        if not (rej_short_core or rej_long_core):
            continue

        def test_ref(ref, tol):
            """tra (side, anchor) neu nen i la reversal tai moc gia `ref`."""
            up = b['hi'] >= ref - tol
            dn = b['lo'] <= ref + tol
            au = ad = False
            for k in range(max(0, i - appro), i):
                if B[k]['c'] < ref:
                    au = True
                if B[k]['c'] > ref:
                    ad = True
            if up and rej_short_core and b['c'] < ref and au:
                return -1, max(b['hi'], ref)
            if dn and rej_long_core and b['c'] > ref and ad:
                return +1, min(b['lo'], ref)
            return 0, 0.0

        vw_side, vw_anchor = test_ref(b['vwap'], vtol)

        z_side, z_anchor, z_hit = 0, 0.0, None
        zl = getz(b['dt'], which)
        for z in zl:
            if z.strength < min_str:
                continue
            if types is not None and z.type not in types:
                continue
            s, a = test_ref(z.center, ztol)
            if s != 0:
                # uu tien vung diem cao nhat neu nhieu vung cung thoa
                if z_hit is None or z.strength > z_hit.strength:
                    z_side, z_anchor, z_hit = s, a, z

        if mode == 'zone':
            side, anchor = z_side, z_anchor
        elif mode == 'union':
            if z_side != 0:
                side, anchor = z_side, z_anchor
            else:
                side, anchor = vw_side, vw_anchor
        elif mode == 'both':
            side, anchor = (vw_side, vw_anchor) if (vw_side != 0 and vw_side == z_side) else (0, 0.0)
        elif mode == 'vwap':
            side, anchor = vw_side, vw_anchor
        else:
            raise ValueError(mode)
        if side == 0:
            continue

        if tf and KB2.trend_at(B, i, tN, ttol) != side:
            continue
        entry = b['c']
        if side > 0:
            sl = anchor - buf; risk = (entry - sl) / TICK
        else:
            sl = anchor + buf; risk = (sl - entry) / TICK
        if risk <= rmin or risk > cap:
            continue
        raw.append(dict(i=i, dt=b['dt'], side=('LONG' if side > 0 else 'SHORT'),
                        entry=entry, sl=sl, risk_t=risk, vsa=b['vratio'],
                        ztype=(z_hit.type if z_hit else 'vwap'),
                        zstr=(z_hit.strength if z_hit else 0.0),
                        zframes=(z_hit.frames if z_hit else 0),
                        zlabel=(z_hit.label if z_hit else 'VWAP')))
    out, last = [], {}
    for s in sorted(raw, key=lambda x: x['i']):
        if s['i'] - last.get(s['side'], -999) < cd:
            continue
        out.append(s)
        last[s['side']] = s['i']
    return out


# ============================================================================
# 4. Do luong
# ============================================================================
def score(B, sigs, rr=1.5):
    return KB2.score(B, sigs, rr)


def line(label, res, extra=''):
    b = res['bym']
    cells = "  ".join(f"{k[-2:]}:{v[2]:+.0f}R({v[1]}/{v[0]})" for k, v in sorted(b.items()))
    ap = " ALL+" if KB2.allpos(res) else ""
    print(f"  {label:34s} n={res['n_sig']:3d} closed={res['closed']:3d} "
          f"WR {res['wr']*100:3.0f}% EV {res['ev']:+.3f} net {res['net']:+6.1f}R{ap}"
          f"  [{cells}] {extra}")


def partition(B, sigs, keyfn, rr=1.5, title=''):
    g = defaultdict(list)
    for s in sigs:
        g[keyfn(s)].append(s)
    print(f"  -- {title} --")
    for k in sorted(g, key=lambda x: -len(g[x])):
        r = score(B, g[k], rr)
        if r['closed'] == 0:
            continue
        print(f"     {str(k):22s} n={r['closed']:3d} WR {r['wr']*100:3.0f}% EV {r['ev']:+.3f} "
              f"net {r['net']:+6.1f}R")


# ============================================================================
def main():
    B = rv.load_dxfeed(KB2.DX)
    print(f"M1 bars={len(B)}  {B[0]['dt']} .. {B[-1]['dt']}")
    M = to_m30(B)
    S = sessions_of_m30(M)
    print(f"M30 bars={len(M)}  phien={len(S)}")
    print("=" * 118)

    # ---------- (0) GOLDEN ----------
    print("(0) GOLDEN — tai lap KB2 baseline VWAP-only (phai khop BASELINE.md: n=27 EV+0.389)")
    base_sigs = KB2.in_window(B, KB2.detect(B))
    base = score(B, base_sigs)
    line("KB2 baseline (imp_reversal_sweep)", base)
    mine = KB2.in_window(B, detect_zone(B, lambda *a: [], mode='vwap'))
    line("KB2 qua detect_zone(mode=vwap)", score(B, mine))
    same = {(s['dt'], s['side']) for s in base_sigs} == {(s['dt'], s['side']) for s in mine}
    print(f"  ==> GOLDEN {'OK' if same and abs(base['ev'] - 0.389) < 0.002 else 'FAIL'}"
          f" (trung khop tung lenh: {same})")
    print("=" * 118)

    # ---------- (1) chuoi vung ----------
    ser = build_zone_series(M, S)
    getz = zone_lookup(ser)
    nall = [len(x[1]) for x in ser]
    ntop = [len(x[2]) for x in ser]
    print(f"(1) Chuoi vung CAUSAL: {len(ser)} lan chot (moi lan dong phien)")
    print(f"    so vung/lan: ALL med={sorted(nall)[len(nall)//2]}  TOP5 med={sorted(ntop)[len(ntop)//2]}")
    tc = defaultdict(int)
    for _, za, _ in ser:
        for z in za:
            tc[z.type] += 1
    print("    phan bo loai vung (ALL): " + "  ".join(f"{k}={v}" for k, v in sorted(tc.items(), key=lambda x: -x[1])))
    print("=" * 118)

    # ---------- (2) cac bien the ----------
    print("(2) BIEN THE — cua so 5-7/2026, RR=1.5, moi gate khac giu y het LIVE")
    runs = OrderedRuns = []
    def run(label, **kw):
        sg = KB2.in_window(B, detect_zone(B, getz, **kw))
        r = score(B, sg)
        line(label, r)
        runs.append((label, sg, r))
        return sg, r

    run("Z1 zone-only ALL (moi vung)", which='all', mode='zone')
    run("Z1b zone-only, nhom CHINH", which='all', mode='zone', types=MAIN_TYPES)
    run("Z1c zone-only, nhom NHIEU(va/hl)", which='all', mode='zone', types=NOISE_TYPES)
    run("Z1d zone-only, diem>=70", which='all', mode='zone', min_str=70)
    run("Z1e zone-only, diem>=85", which='all', mode='zone', min_str=85)
    run("Z2 UNION vwap+zone(ALL)", which='all', mode='union')
    run("Z2b UNION vwap+zone(CHINH)", which='all', mode='union', types=MAIN_TYPES)
    run("Z2c UNION vwap+zone(diem>=70)", which='all', mode='union', min_str=70)
    run("Z3 CA vwap VA zone (hop luu)", which='all', mode='both')
    run("Z4 zone-only TOP5 (dung nhu chart)", which='top', mode='zone')
    run("Z4b UNION vwap+TOP5", which='top', mode='union')
    print("=" * 118)

    # ---------- (3) partition ----------
    print("(3) PHAN HOACH — Z1 zone-only ALL")
    z1 = KB2.in_window(B, detect_zone(B, getz, which='all', mode='zone'))
    partition(B, z1, lambda s: s['ztype'], title='theo LOAI vung')
    partition(B, z1, lambda s: ('diem>=85' if s['zstr'] >= 85 else
                                'diem 70-85' if s['zstr'] >= 70 else
                                'diem 55-70' if s['zstr'] >= 55 else 'diem<55'),
              title='theo DIEM vung')
    partition(B, z1, lambda s: f"hop luu x{min(s['zframes'],3)}khung", title='theo SO KHUNG hop luu')
    partition(B, z1, lambda s: s['side'], title='theo PHIA (SPEC §9 #1a)')
    print("=" * 118)

    # ---------- (4) DOI CHUNG NGAU NHIEN ----------
    print("(4) DOI CHUNG NGAU NHIEN — vung bi dich ngau nhien, giu so luong (5 seed)")
    print("    Neu vung that KHONG hon ro doi chung => vung khong mang thong tin.")
    for mode, which, types, lab in (('zone', 'all', None, 'Z1 zone-only ALL'),
                                    ('zone', 'all', MAIN_TYPES, 'Z1b nhom CHINH'),
                                    ('union', 'all', None, 'Z2 UNION ALL')):
        real = score(B, KB2.in_window(B, detect_zone(B, getz, which=which, mode=mode, types=types)))
        evs, ns = [], []
        for seed in range(5):
            rg = random.Random(1000 + seed)
            sr = build_zone_series(M, S, jitter=3.0, rng=rg)
            gz = zone_lookup(sr)
            r = score(B, KB2.in_window(B, detect_zone(B, gz, which=which, mode=mode, types=types)))
            evs.append(r['ev']); ns.append(r['closed'])
        mev = sum(evs) / len(evs)
        print(f"  {lab:24s} THAT: n={real['closed']:3d} EV={real['ev']:+.3f}   "
              f"NGAU NHIEN: n~{sum(ns)/len(ns):.0f} EV={mev:+.3f} "
              f"(min {min(evs):+.3f} max {max(evs):+.3f})  chenh={real['ev']-mev:+.3f}")
    print("=" * 118)


if __name__ == '__main__':
    main()
