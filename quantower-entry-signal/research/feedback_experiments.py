#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THI NGHIEM theo 4 feedback user (2026-07-27). Doc so THAT, khong doan.
 (D) Bug "so entry chung o 4": pool session-zone bi cap LookbackSessions=12 trong C#
     -> lich su bi doi kho vung -> confluence starve. So sanh capped vs uncapped.
 (B) SL floor: user thay cham SL(2d) roi chay len TP. Test nang floor -> co bo?
     2 khung: (b1) TP co dinh theo diem (giu muc tieu, chi noi stop) ; (b2) RR co dinh.
 (C) Bug "sot tin hieu dep" (nen tim, tren hop luu+VWAP): confluence dinh nghia
     theo SO TRIGGER (>=2 vung cung ban) vs theo CUM-GAN (zone nam trong cum >=2).
     -> cum-gan co giu edge ma bat duoc nhieu bounce hon khong?
 Tan suat + chat luong moi cau hinh.
"""
import sys, statistics as st
from datetime import timedelta
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em, research as R
TICK = em.TICK


def simulate_pts(B, i, side, sl_px, tp_px):
    o = R.hit_target(B, i, side, sl_px, tp_px)
    return o  # 'TP' / 'SL' / None


def exp_points(sigs, B, sl_pts, tp_pts):
    """SL/TP co dinh theo DIEM tinh tu entry. Ky vong tinh bang DIEM."""
    tp = sl = 0
    for s in sigs:
        e = s['entry']
        if s['side'] == 'LONG':
            slp, tpp = e - sl_pts, e + tp_pts
        else:
            slp, tpp = e + sl_pts, e - tp_pts
        o = simulate_pts(B, s['i'], s['side'], slp, tpp)
        if o == 'TP': tp += 1
        elif o == 'SL': sl += 1
    n = tp + sl
    if n == 0: return 0, 0, 0
    wr = tp / n
    e_pts = wr * tp_pts - (1 - wr) * sl_pts
    return n, wr, e_pts


def wr_exp_R(sigs, B, rmult):
    """RR co dinh: TP = entry +- rmult*risk(cua chinh tin hieu do)."""
    tp = sl = 0
    for s in sigs:
        r = s['risk_t'] * TICK
        tpp = s['entry'] + rmult * r if s['side'] == 'LONG' else s['entry'] - rmult * r
        o = R.hit_target(B, s['i'], s['side'], s['sl'], tpp)
        if o == 'TP': tp += 1
        elif o == 'SL': sl += 1
    n = tp + sl
    return (n, tp / n if n else 0, (tp * rmult - sl) / n if n else 0)


# ================= dung du lieu 1 lan =================
B = em.load_m1()
UNCAP = em.build_zones(B)          # nhu Python backtest (moi session block)
sig_uncap = em.dedup(em.run(B, UNCAP))
ndays = len(set(s['dt'].date() for s in sig_uncap))


# ---- pool CAP giong C# (chi N session block cuoi co session-zone; D-1 giu het) ----
def build_zones_capped(B, cap):
    zones = []
    blocks = []; cur = None
    for b in B:
        lab = em.sess_of(b['dt'].hour * 60 + b['dt'].minute)
        new = (cur is None or lab != cur['lab'] or (b['dt'] - cur['bars'][-1]['dt']) > timedelta(minutes=40))
        if new: cur = dict(lab=lab, bars=[]); blocks.append(cur)
        cur['bars'].append(b)
    start = max(0, len(blocks) - cap)          # <-- CHI N block cuoi (giong C# LookbackSessions)
    for blk in blocks[start:]:
        bb = blk['bars']
        if len(bb) < 10: continue
        poc, vah, val = em.value_area(em.tpo_counts([(x['lo'], x['hi']) for x in bb]))
        if poc is None: continue
        hi = max(x['hi'] for x in bb); lo = min(x['lo'] for x in bb)
        end = bb[-1]['dt']; exp = end + timedelta(days=em.ZONE_EXPIRE_DAYS)
        for nm, v, sv in [(f"POC {blk['lab']}", poc, 70), (f"VAH {blk['lab']}", vah, 58),
                          (f"VAL {blk['lab']}", val, 58), (f"Dinh {blk['lab']}", hi, 52), (f"Day {blk['lab']}", lo, 52)]:
            zones.append(dict(price=v, kind=nm, strength=sv, ready=end, expire=exp))
    days = em.daily_levels()
    for i in range(1, len(days)):
        d = days[i]; p = days[i - 1]; rd = d['start']; exp = rd + timedelta(days=1, hours=6)
        for nm, v, sv in [("D-1 VAH", p['vah'], 66), ("D-1 VAL", p['val'], 66), ("D-1 POC", p['poc'], 72),
                          ("D-1 High", p['hi'], 60), ("D-1 Low", p['lo'], 60)]:
            zones.append(dict(price=v, kind=nm, strength=sv, ready=rd, expire=exp))
    return zones


print("=" * 96)
print("(D) BUG SO ENTRY CHUNG O ~4 — pool session-zone bi CAP LookbackSessions")
print(f"  Uncapped (dung nhu backtest): confl>=2 = {sum(s['confl']>=2 for s in sig_uncap)} lenh / {ndays} ngay"
      f" = {sum(s['confl']>=2 for s in sig_uncap)/ndays:.1f}/ngay")
for cap in [12, 24, 40, 9999]:
    sc = em.dedup(em.run(B, build_zones_capped(B, cap)))
    c2 = [s for s in sc if s['confl'] >= 2]
    lastday = max(s['dt'].date() for s in sig_uncap)
    n_last4 = sum(1 for s in c2 if (lastday - s['dt'].date()).days <= 4)
    print(f"  cap={cap:<5} block cuoi: confl>=2 tong={len(c2):<4} (trong 4 ngay cuoi={n_last4})")

print("\n" + "=" * 96)
print("(B) SL FLOOR — user thay cham SL(2d) roi chay TP. Nang floor co loi khong?")
c2u = [s for s in sig_uncap if s['confl'] >= 2]
print(f"  [b1] GIU MUC TIEU co dinh (TP theo diem), chi doi STOP. Ky vong = DIEM/lenh (confl>=2, n~{len(c2u)}):")
print(f"       {'SL(d)':>6} | " + " | ".join(f"TP{t}d" for t in [4, 5, 6, 8]))
for slp in [2, 3, 4, 5]:
    cells = []
    for tpp in [4, 5, 6, 8]:
        n, wr, ep = exp_points(c2u, B, slp, tpp)
        cells.append(f"{wr:>3.0%}/{ep:+4.1f}")
    print(f"       {slp:>4}d  | " + " | ".join(cells))
print("       (o moi o: WR / ky-vong-DIEM. Chon o co ky vong diem cao nhat.)")

print(f"\n  [b2] RR co dinh (TP scale theo SL) — doi floor roi re-run scan:")
orig = em.SL_MIN_T
for floor_t in [20, 30, 40, 50]:
    em.SL_MIN_T = floor_t
    sc = em.dedup(em.run(B, UNCAP)); c2 = [s for s in sc if s['confl'] >= 2]
    n2, w2, e2 = wr_exp_R(c2, B, 2.0); n3, w3, e3 = wr_exp_R(c2, B, 3.0)
    med = st.median([s['risk_t'] for s in c2]) / 10
    print(f"       floor={floor_t/10:.0f}d n={len(c2):<3} medSL={med:.1f}d | 2R WR{w2:.0%} exp{e2:+.2f}R | 3R WR{w3:.0%} exp{e3:+.2f}R")
em.SL_MIN_T = orig

print("\n" + "=" * 96)
print("(C) DINH NGHIA CONFLUENCE — trigger (>=2 vung ban) vs cum-gan (zone trong cum >=2)")


def run_with_cluster(B, pool):
    """Nhu em.run nhung dinh danh moi tin hieu voi CUM-GAN: so vung active nam trong
       ConfluenceTol quanh gia zone kich hoat (ke ca vung khong ban)."""
    raw = em.run(B, pool)
    TOLc = 7  # ConfluenceTol tick
    for s in raw:
        zp = float(s['zone'].split()[-1])
        t = s['dt']
        near = 0
        seen = set()
        for z in pool:
            if not (z['ready'] <= t <= z['expire']): continue
            key = round(z['price'] / TICK)
            if key in seen: continue
            if abs(z['price'] - zp) / TICK <= TOLc:
                near += 1; seen.add(key)
        s['cluster'] = near
    return raw


raw_cl = run_with_cluster(B, UNCAP)
sig_cl = em.dedup(raw_cl)   # dedup giu 'cluster' cua ban ghi dau
# gan lai cluster (dedup co the mat field) — lay max cluster trong nhom
for s in sig_cl:
    s.setdefault('cluster', 1)
print(f"  Tong tin hieu (sau dedup) = {len(sig_cl)}")
for nm, f in [("trigger>=2 (hien tai)", lambda s: s['confl'] >= 2),
              ("cum-gan>=2", lambda s: s.get('cluster', 1) >= 2),
              ("cum-gan>=3", lambda s: s.get('cluster', 1) >= 3),
              ("trigger>=2 HOAC cum>=3", lambda s: s['confl'] >= 2 or s.get('cluster', 1) >= 3)]:
    sub = [s for s in sig_cl if f(s)]
    if len(sub) >= 6:
        n2, w2, e2 = wr_exp_R(sub, B, 2.0); n3, w3, e3 = wr_exp_R(sub, B, 3.0)
        print(f"  {nm:<26} n={len(sub):<4} {len(sub)/ndays:.1f}/ngay | 2R WR{w2:.0%} exp{e2:+.2f} | 3R WR{w3:.0%} exp{e3:+.2f}")
    else:
        print(f"  {nm:<26} n={len(sub):<4} (it)")

print("\n" + "=" * 96)
print("(B+C) CHOT: SL floor tren tap cum-gan>=2 (dinh nghia confluence MOI)")
cg2 = [s for s in sig_cl if s.get('cluster', 1) >= 2]
print(f"  [b1] GIU MUC TIEU (TP diem), doi STOP — cum-gan>=2 n={len(cg2)} (WR / ky-vong-DIEM):")
print(f"       {'SL(d)':>6} | " + " | ".join(f"TP{t}d" for t in [4, 5, 6, 8]))
for slp in [2, 3, 4, 5]:
    cells = [f"{exp_points(cg2,B,slp,tpp)[1]:>3.0%}/{exp_points(cg2,B,slp,tpp)[2]:+4.1f}" for tpp in [4, 5, 6, 8]]
    print(f"       {slp:>4}d  | " + " | ".join(cells))
print(f"  [b2] RR co dinh (floor doi -> re-run + gate cum-gan>=2):")
orig = em.SL_MIN_T
for floor_t in [20, 30, 40, 50]:
    em.SL_MIN_T = floor_t
    rc = run_with_cluster(B, UNCAP); sc = em.dedup(rc)
    for s in sc: s.setdefault('cluster', 1)
    c2 = [s for s in sc if s.get('cluster', 1) >= 2]
    n2, w2, e2 = wr_exp_R(c2, B, 2.0); n3, w3, e3 = wr_exp_R(c2, B, 3.0)
    print(f"       floor={floor_t/10:.0f}d n={len(c2):<3} | 2R WR{w2:.0%} exp{e2:+.2f}R | 3R WR{w3:.0%} exp{e3:+.2f}R")
em.SL_MIN_T = orig
print("=" * 96)
