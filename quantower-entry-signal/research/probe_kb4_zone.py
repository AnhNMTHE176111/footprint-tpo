#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROBE KB4 — QUAY DAU TAI VUNG MANH (khong chi VWAP) + ARM->CONFIRM
================================================================================
Yeu cau user (2026-07-30):
  1. Kich ban quay dau KHONG chi tinh o VWAP ma o CAC VUNG MANH.
  2. Nen quay dau chua du dieu kien -> CHO nen tin hieu roi vao (khong bat buoc vao
     ngay tai nen quay dau). Neu nen quay dau DEP thi vao luon.
  => do xem cai thien bao nhieu R so voi KB2 (quay dau tai VWAP) dang ship.

DAC TA CHOT TRUOC KHI CHAY (chong nan ket qua):
  VUNG   = build_zones() cua entry_dxfeed.py = DUNG pool ma indicator dang VE:
           POC/VAH/VAL/Dinh/Day tung phien (A/AU/MY) + D-1 VAH/VAL/POC/High/Low.
           strength: POC sess 70, VAH/VAL 58, Dinh/Day 52, D-1 POC 72/VA 66/HL 60.
           Zone chi active tu 'ready' (het block => KHONG look-ahead) den 'expire'.
  CHAM   = LONG: b.lo <= Z + ZTOL  va  b.lo >= Z - PEN  (cham/xuyen nhe, khong pha sau)
           va da den TU TREN (co nen trong APPRO nen truoc dong > Z)
           va dong lai DUNG PHIA vung (b.c > Z).            SHORT: guong lai.
  KB4-A  (vao luon, "nen quay dau dep"): chinh nen cham thoa
           rau >= WICK*range, cpos >= 0.55 (LONG), body >= BODY_A, VSA >= VSA_A.
  KB4-B  (arm -> confirm): nen cham thoa dieu kien LONG hon (rau >= WICK_ARM, dong dung phia)
           -> ARM. Trong <= W nen sau, cho nen TIN HIEU:
             LONG: close > high cua nen arm, than >= BODY_C, nen tang, VSA >= VSA_C.
           Huy arm neu co nen dong xuyen qua vung (close < Z - INVAL) hoac het W nen.
  KB4-AB (router user mo ta): nen cham dep -> vao luon (A); khong thi ARM cho confirm (B).
  SL     = cuc tri cua cua so arm..confirm (LONG: min low) - BUF. KHONG neo VWAP nua
           (bug ban cu: anchor=min(low,vwap) => risk 153 tick => bi cap SL loai).
  TP     = RR * risk. RR mac dinh 1.5 (bang RevRR dang ship) + bao them 2R/3R.
  Cooldown 15 nen/phia (khop Cooldown_ C#). Loc thanh khoan: Gate() nhu C#.
  Trend filter: BAO CA 2 (ON/OFF) — KB2 dang ship bat, nhung fade nguoc trend la ban chat
           cua quay dau nen phai do that.
CUA SO DO: 2026-05..07 (GCQ26 chi thanh khoan tu thang 5). Tach IS (05+06) / OOS (07).
Baseline so sanh: imp_reversal_sweep.detect() = replica CHINH XAC KB2 dang ship.
"""
import sys, os
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reversal_vwap as rv
import entry_dxfeed as ed
import imp_reversal_sweep as IRS

TICK = rv.TICK
DX = IRS.DX

# ---------------- tham so KB4 (mac dinh = diem xuat phat, KHONG phai da toi uu) ----------------
P0 = dict(
    ztol_t=7,        # cham vung: dung sai (ConfluenceTol shipped = 7)
    pen_t=20,        # xuyen sau toi da qua vung (2 gia) — qua nua la PHA vung, khong phai quay dau
    appro=6,         # so nen tiep can (khop RevApproachBars)
    minstr=52,       # strength toi thieu cua vung (52 = nhan tat ca)
    mincl=1,         # so vung hop luu toi thieu quanh diem cham
    cl_tol=7,        # dung sai dem hop luu
    incl_vwap=True,  # coi VWAP la 1 "vung" => KB4 bao trum KB2
    # --- nhanh A: vao luon ---
    wick=0.50, cpos_h=0.05, body_a=0.30, vsa_a=1.8,   # = y nguyen gate KB2 dang ship
    # --- nhanh B: arm -> confirm ---
    wick_arm=0.30, w=8, body_c=0.45, vsa_c=1.2, inval_t=10,
    # --- risk ---
    buf_t=2, cap_t=70, risk_min=5, cooldown=15, rr=1.5,
    trend=False, trend_bars=480, trend_tol_t=10,
    vol_floor=20, warmup=20,
    # --- VONG 2: bo loc CHON LOC (mac dinh TAT de vong 1 giu nguyen ket qua) ---
    kinds=None,        # None = moi loai vung; hoac set ten loai duoc phep
    max_cl=99,         # so vung hop luu TOI DA quanh diem cham (vung "don doc" = 1)
    fresh=False,       # chi lay LAN CHAM DAU TIEN cua moi vung
    one_per_day=False, # toi da 1 tin hieu / vung / ngay
    one_arm=False,     # toi da 1 arm dang mo moi phia (arm moi thay arm cu)
    vsa_min=0.0,       # VSA toi thieu cua NEN VAO LENH (ca 2 nhanh)
    leg_min=0.0,       # nhip di vao vung phai >= X gia trong leg_look nen
    leg_look=15,
)

# ---------------- helper ----------------
def trend_at(B, i, N, tol_t):
    if i < N: return 0
    d = B[i]['c'] - B[i - N]['c']; t = tol_t * TICK
    return 1 if d > t else -1 if d < -t else 0


def zone_index(zones):
    """zones sap theo ready -> tra ve ham lay active list theo thoi gian (O(1) amortized)."""
    zs = sorted(zones, key=lambda z: z['ready'])
    state = dict(p=0, act=[])
    def active(t):
        while state['p'] < len(zs) and zs[state['p']]['ready'] <= t:
            state['act'].append(zs[state['p']]); state['p'] += 1
        state['act'] = [z for z in state['act'] if z['expire'] > t]
        return state['act']
    return active


def pick_zone(act, price, side, P, vwap):
    """vung gan nhat ma nen cham duoc; tra (Z, n_confluence, kind) hoac None."""
    tol = P['ztol_t'] * TICK; pen = P['pen_t'] * TICK
    cands = []
    for z in act:
        if z['strength'] < P['minstr']: continue
        if P['kinds'] is not None and z['kind'].split()[0] not in P['kinds']: continue
        if P['fresh'] and z.get('_used'): continue
        Z = z['price']
        if side > 0:
            if price <= Z + tol and price >= Z - pen: cands.append((abs(price - Z), Z, z['kind'], z))
        else:
            if price >= Z - tol and price <= Z + pen: cands.append((abs(price - Z), Z, z['kind'], z))
    if P['incl_vwap']:
        Z = vwap
        if side > 0:
            if price <= Z + tol and price >= Z - pen: cands.append((abs(price - Z), Z, 'VWAP', None))
        else:
            if price >= Z - tol and price <= Z + pen: cands.append((abs(price - Z), Z, 'VWAP', None))
    if not cands: return None
    cands.sort(key=lambda x: x[0])
    _, Z, kind, zobj = cands[0]
    ncl = len({round(z['price'] / TICK) for z in act
               if z['strength'] >= P['minstr'] and abs(z['price'] - Z) / TICK <= P['cl_tol']})
    if P['incl_vwap'] and abs(vwap - Z) / TICK <= P['cl_tol']: ncl += 1
    if ncl < P['mincl'] or ncl > P['max_cl']: return None
    return Z, ncl, kind, zobj


# ---------------- detector ----------------
def detect(B, zones, mode='AB', **kw):
    """mode: 'A' = chi vao luon, 'B' = chi arm->confirm, 'AB' = router (dep thi vao luon)."""
    P = dict(P0); P.update(kw)
    for z in zones: z.pop('_used', None)     # reset state giua cac lan chay
    active = zone_index(zones)
    cpos_hi = 0.5 + P['cpos_h']; cpos_lo = 0.5 - P['cpos_h']
    raw = []
    arms = []          # (side, Z, i_arm, ext, bar_hi_or_lo_to_break)
    start = max(rv.VSA_MA + 2, P['trend_bars'] if P['trend'] else 0)

    used_day = set()

    def emit(i, side, entry, ext, Z, ncl, kind, tag, vsa, zobj):
        if B[i]['vratio'] < P['vsa_min']: return
        if P['one_per_day']:
            key = (round(Z / TICK), side, B[i]['dt'].date())
            if key in used_day: return
        sl = ext - P['buf_t'] * TICK if side > 0 else ext + P['buf_t'] * TICK
        risk = (entry - sl) / TICK if side > 0 else (sl - entry) / TICK
        if risk <= P['risk_min'] or risk > P['cap_t']: return
        if P['one_per_day']: used_day.add((round(Z / TICK), side, B[i]['dt'].date()))
        if zobj is not None: zobj['_used'] = True
        raw.append(dict(i=i, dt=B[i]['dt'], side='LONG' if side > 0 else 'SHORT', entry=entry,
                        sl=sl, risk_t=risk, zone=Z, ncl=ncl, kind=kind, tag=tag, vsa=vsa))

    for i in range(start, len(B)):
        b = B[i]
        act = active(b['dt'])
        # --- 1) xu ly cac arm dang mo (confirm / huy) ---
        if mode in ('B', 'AB') and arms:
            keep = []
            for a in arms:
                side, Z, ia, ext = a['side'], a['Z'], a['i'], a['ext']
                if i - ia > P['w']: continue                                   # het cua so
                if side > 0 and b['c'] < Z - P['inval_t'] * TICK: continue      # pha vung
                if side < 0 and b['c'] > Z + P['inval_t'] * TICK: continue
                ext = min(ext, b['lo']) if side > 0 else max(ext, b['hi'])
                a['ext'] = ext
                ok = (b['c'] > a['brk'] and b['c'] > b['o'] and b['brat'] >= P['body_c']
                      and b['vratio'] >= P['vsa_c']) if side > 0 else \
                     (b['c'] < a['brk'] and b['c'] < b['o'] and b['brat'] >= P['body_c']
                      and b['vratio'] >= P['vsa_c'])
                if ok and (not P['trend'] or trend_at(B, i, P['trend_bars'], P['trend_tol_t']) == side):
                    emit(i, side, b['c'], ext, Z, a['ncl'], a['kind'], f"confirm+{i-ia}",
                         b['vratio'], a['zobj'])
                    continue                                                   # arm da dung
                keep.append(a)
            arms = keep
        # --- 2) tim cham vung moi tai bar i ---
        if not (b['v'] >= P['vol_floor'] and b['since_gap'] >= P['warmup']
                and b['vma'] >= P['vol_floor'] * 0.6): continue
        rng = b['rng']
        if rng <= 0: continue
        for side in (+1, -1):
            price = b['lo'] if side > 0 else b['hi']
            pz = pick_zone(act, price, side, P, b['vwap'])
            if pz is None: continue
            Z, ncl, kind, zobj = pz
            # den tu dung phia
            appro = False
            for k in range(max(0, i - P['appro']), i):
                if side > 0 and B[k]['c'] > Z: appro = True
                if side < 0 and B[k]['c'] < Z: appro = True
            if not appro: continue
            # nhip di VAO vung phai du dai (khong phai bo ngang cham lien tuc)
            if P['leg_min'] > 0:
                lo = max(0, i - P['leg_look'])
                ext_before = max(B[k]['c'] for k in range(lo, i)) if side > 0 else \
                             min(B[k]['c'] for k in range(lo, i))
                leg = (ext_before - price) if side > 0 else (price - ext_before)
                if leg < P['leg_min']: continue
            # dong lai dung phia vung
            if side > 0 and not b['c'] > Z: continue
            if side < 0 and not b['c'] < Z: continue
            wick = b['lw'] if side > 0 else b['uw']
            cpos_ok = (b['cpos'] >= cpos_hi) if side > 0 else (b['cpos'] <= cpos_lo)
            # A: nen quay dau DEP -> vao luon
            nice = (wick >= P['wick'] * rng and cpos_ok and b['brat'] >= P['body_a']
                    and b['vratio'] >= P['vsa_a'])
            if mode in ('A', 'AB') and nice:
                if not P['trend'] or trend_at(B, i, P['trend_bars'], P['trend_tol_t']) == side:
                    emit(i, side, b['c'], price, Z, ncl, kind, 'instant', b['vratio'], zobj)
                    continue
            # B: chua du -> ARM
            if mode in ('B', 'AB') and wick >= P['wick_arm'] * rng:
                if P['one_arm']: arms = [x for x in arms if x['side'] != side]
                arms.append(dict(side=side, Z=Z, i=i, ext=price, ncl=ncl, kind=kind, zobj=zobj,
                                 brk=(b['hi'] if side > 0 else b['lo'])))
    # cooldown/dedup theo phia (khop Cooldown_)
    out = []; last = {}
    for s in sorted(raw, key=lambda x: x['i']):
        if s['i'] - last.get(s['side'], -999) < P['cooldown']: continue
        out.append(s); last[s['side']] = s['i']
    return out


# ---------------- eval ----------------
def window(sigs, m0=5, m1=7, y=2026):
    return [s for s in sigs if s['dt'].year == y and m0 <= s['dt'].month <= m1]


def score(B, sigs, rr):
    bym = defaultdict(lambda: [0, 0, 0.0]); tot = [0, 0, 0.0]
    for s in sigs:
        r = s['risk_t'] * TICK
        tgt = s['entry'] + rr * r if s['side'] == 'LONG' else s['entry'] - rr * r
        o = rv.hit(B, s['i'], s['side'], s['sl'], tgt)
        if o not in ('TP', 'SL', 'amb'): continue
        win = (o == 'TP'); dr = rr if win else -1
        for agg in (bym[s['dt'].strftime('%Y-%m')], tot):
            agg[0] += 1; agg[1] += win; agg[2] += dr
    closed, tp, net = tot
    return dict(n=len(sigs), closed=closed, tp=tp, wr=(tp / closed if closed else 0),
                ev=(net / closed if closed else 0), net=net,
                bym={k: tuple(v) for k, v in bym.items()})


def fmt(res, label, rr=None):
    cells = "  ".join(f"{k[-2:]}:{v[2]:+.0f}R({v[1]}/{v[0]})" for k, v in sorted(res['bym'].items()))
    ap = " ALL+" if res['bym'] and all(v[2] >= 0 for v in res['bym'].values()) else ""
    rrs = f"@{rr}R " if rr else ""
    print(f"  {label:34s} {rrs}n={res['n']:4d} closed={res['closed']:4d} WR {res['wr']*100:3.0f}% "
          f"EV {res['ev']:+.3f} net {res['net']:+7.1f}R{ap}  [{cells}]")
    return res


def main():
    B = rv.load_dxfeed(DX)
    zones = ed.build_zones(B)
    print(f"bars={len(B)}  {B[0]['dt']} .. {B[-1]['dt']}   zones={len(zones)}")
    print("=" * 118)
    print("BASELINE — KB2 quay dau tai VWAP (replica CHINH XAC ban dang ship):")
    base = window(IRS.detect(B))
    b15 = fmt(score(B, base, 1.5), "KB2 VWAP (dang ship)", 1.5)
    print("=" * 118)
    print("KB4 — quay dau tai VUNG MANH  (mac dinh: gate A = y nguyen KB2, trend OFF)")
    for mode, lab in (('A', 'KB4-A  vao luon'), ('B', 'KB4-B  arm->confirm'), ('AB', 'KB4-AB router')):
        s = window(detect(B, zones, mode=mode))
        fmt(score(B, s, 1.5), lab, 1.5)
    print("-" * 118)
    print("KB4-AB: quet 1 tham so moi lan (do do nhay, KHONG phai chon best):")
    for kw, lab in (
        (dict(trend=True), "trend ON"),
        (dict(mincl=2), "hop luu >=2 vung"),
        (dict(minstr=58), "chi vung strength>=58"),
        (dict(minstr=66), "chi vung strength>=66"),
        (dict(incl_vwap=False), "BO VWAP khoi pool vung"),
        (dict(body_a=0.10), "noi than nen A >=10% (pin bar)"),
        (dict(vsa_a=1.2), "noi VSA nen A >=1.2"),
        (dict(w=4), "cua so confirm 4 nen"),
        (dict(w=12), "cua so confirm 12 nen"),
        (dict(ztol_t=4), "dung sai cham 4 tick"),
        (dict(ztol_t=12), "dung sai cham 12 tick"),
        (dict(pen_t=10), "xuyen toi da 1 gia"),
        (dict(cap_t=40), "tran SL 4 gia"),
    ):
        s = window(detect(B, zones, mode='AB', **kw))
        fmt(score(B, s, 1.5), lab, 1.5)
    print("-" * 118)
    print("KB4-AB mac dinh o cac RR khac:")
    s = window(detect(B, zones, mode='AB'))
    for rr in (1.0, 1.5, 2.0, 3.0):
        fmt(score(B, s, rr), "KB4-AB", rr)
    print("=" * 118)
    print("IS (2026-05,06) vs OOS (2026-07) — KB4-AB mac dinh vs KB2:")
    for lab, sg in (("KB2 VWAP", base), ("KB4-AB", s)):
        isw = [x for x in sg if x['dt'].month in (5, 6)]; oos = [x for x in sg if x['dt'].month == 7]
        a = score(B, isw, 1.5); c = score(B, oos, 1.5)
        print(f"  {lab:12s} IS n={a['closed']:3d} WR {a['wr']*100:3.0f}% net {a['net']:+6.1f}R "
              f"| OOS n={c['closed']:3d} WR {c['wr']*100:3.0f}% net {c['net']:+6.1f}R")


if __name__ == '__main__':
    main()


# ============================================================================
# VONG 2 — them bo loc CHON LOC theo tung buoc (moi buoc co ly do, khong phai grid)
# ============================================================================
def main2():
    B = rv.load_dxfeed(DX)
    zones = ed.build_zones(B)
    print(f"bars={len(B)}  zones={len(zones)}")
    print("=" * 122)
    base = window(IRS.detect(B))
    fmt(score(B, base, 1.5), "BASELINE KB2 VWAP (dang ship)", 1.5)
    print("-" * 122)
    steps = [
        ("KB4-AB tho (vong 1)", {}),
        ("+ 1 arm/phia", dict(one_arm=True)),
        ("+ 1 lenh/vung/ngay", dict(one_arm=True, one_per_day=True)),
        ("+ nhip vao vung >=3 gia", dict(one_arm=True, one_per_day=True, leg_min=3.0)),
        ("+ vung don doc (cl=1)", dict(one_arm=True, one_per_day=True, leg_min=3.0, max_cl=1)),
        ("+ chi cham LAN DAU", dict(one_arm=True, one_per_day=True, leg_min=3.0, fresh=True)),
        ("+ nen vao VSA>=1.5", dict(one_arm=True, one_per_day=True, leg_min=3.0, vsa_min=1.5)),
        ("+ nen vao VSA>=2.2 (climax)", dict(one_arm=True, one_per_day=True, leg_min=3.0, vsa_min=2.2)),
        ("+ chi vung POC", dict(one_arm=True, one_per_day=True, leg_min=3.0, kinds={'POC', 'D-1'})),
        ("+ trend ON", dict(one_arm=True, one_per_day=True, leg_min=3.0, trend=True)),
        ("+ cooldown 60 nen", dict(one_arm=True, one_per_day=True, leg_min=3.0, cooldown=60)),
    ]
    keep = {}
    for lab, kw in steps:
        s = window(detect(B, zones, mode='AB', **kw))
        r = fmt(score(B, s, 1.5), lab, 1.5)
        keep[lab] = (s, r)
    print("-" * 122)
    print("KET HOP cac buoc co ich + tach IS/OOS:")
    combos = [
        ("C1 arm+day+leg+trend", dict(one_arm=True, one_per_day=True, leg_min=3.0, trend=True)),
        ("C2 C1 + VSA>=1.5", dict(one_arm=True, one_per_day=True, leg_min=3.0, trend=True, vsa_min=1.5)),
        ("C3 C1 + leg>=5 gia", dict(one_arm=True, one_per_day=True, leg_min=5.0, trend=True)),
        ("C4 C1 + cooldown 60", dict(one_arm=True, one_per_day=True, leg_min=3.0, trend=True, cooldown=60)),
        ("C5 C1 + chi nhanh A", dict(one_arm=True, one_per_day=True, leg_min=3.0, trend=True)),
    ]
    for lab, kw in combos:
        mode = 'A' if 'nhanh A' in lab else 'AB'
        s = window(detect(B, zones, mode=mode, **kw))
        for rr in (1.5, 2.0):
            r = score(B, s, rr)
            isw = [x for x in s if x['dt'].month in (5, 6)]; oos = [x for x in s if x['dt'].month == 7]
            a = score(B, isw, rr); c = score(B, oos, rr)
            print(f"  {lab:24s} @{rr}R n={r['n']:4d} WR {r['wr']*100:3.0f}% EV {r['ev']:+.3f} net {r['net']:+7.1f}R"
                  f" | IS n={a['closed']:3d} {a['net']:+6.1f}R | OOS n={c['closed']:3d} {c['net']:+6.1f}R")
    print("=" * 122)
    print("Chia theo nhanh (A=vao luon vs B=cho confirm), cau hinh C1:")
    s = window(detect(B, zones, mode='AB', one_arm=True, one_per_day=True, leg_min=3.0, trend=True))
    for tag in ('instant', 'confirm'):
        sub = [x for x in s if x['tag'].startswith(tag)]
        fmt(score(B, sub, 1.5), f"  nhanh {tag}", 1.5)


if __name__ == '__main__':
    import sys
    main2() if '2' in sys.argv else main()
