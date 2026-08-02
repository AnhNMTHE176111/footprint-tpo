#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPLAY EntrySignal.cs tren data M1 CO FOOTPRINT TUNG MUC (data-export/Data_Footprint_Export*.csv,
UTC, 03/07 -> 31/07/2026). Muc tieu: TAI HIEN dung 11 lenh live trong
data-export/signals/ENTRY SIGNAL (M1)_2026-08-02.csv truoc khi sua bat ky logic nao.

Dung 1:1 theo EntrySignal.cs (khong theo entry_month.py vi ban do thieu gate hop luu):
  BuildBars      -> vwap (reset gap>30'), vma=SMA20 GOM nen hien tai, vratio, since_gap, trend
  BuildPool      -> phien (label theo gio VN = UTC+7, tach gap>40') POC/VAH/VAL/Dinh/Day
                    + ngay (tach gap>45') D-1 VAH/VAL/POC/Dinh/Day  + VWAP dong
                    Profile dung VOLUME ROWS THAT tu file per-level (giong live), fallback TPO.
  Scan           -> KB1 pha&hoi / KB2 cham&dao
  Emit + Dedup   -> gate Cluster >= MinConfluence

Cau hinh LIVE (nguoi hoc xac nhan 2026-08-02): RR=3, SlFloor=3.5 gia, SlCap=6.0.
"""
import csv, sys, math
from collections import deque, defaultdict
from datetime import datetime, timedelta

DIR = "/home/asl86/Documents/footprint-tpo/data-export/"
TICK = 0.1

# ---- Input Parameters khop EntrySignal.cs ----
TZ_OFFSET = 7; ASIA_START = 300; EUROPE_START = 750; US_START = 1140
SESSION_GAP = 40; DAY_GAP = 45; ZONE_EXPIRE_DAYS = 3; ROW_TICKS = 1
CONFLUENCE_TOL = 7; DEDUP_TOL = 6; MIN_CONFLUENCE = 2; ARM_DIST_T = 20
VSA_PERIOD = 20; VSA_GATE = 1.2; VSA_CLIMAX = 2.2
BODY_STRONG = 0.55; DELTA_DOM = 0.25; DELTA_ABS_MIN = 15; WICK_FRAC = 0.50
RETEST_BARS = 12; RETEST_TOL = 4; RETEST_HOLD_BUF = 0
SL_FLOOR = 3.5; SL_CAP = 6.0; SL_BUF = 2; RR = 3.0
EXTEND_NEXT_ZONE = True; NEXT_ZONE_MIN_R = 2.0
VOL_FLOOR = 20; WARMUP_BARS = 20; COOLDOWN = 15; TREND_LOOKBACK = 480
ABS_DOM = 0.60; REQUIRE_WALL_S2 = True; S2_CLIMAX_OVERRIDE = True
ENABLE_S2 = True

# ================== NAP DU LIEU ==================
def load_bars():
    B = []
    with open(DIR + "Data_Footprint_Export_bars.csv", encoding="utf-8-sig") as f:
        for x in csv.DictReader(f):
            B.append(dict(
                idx=len(B), time=datetime.fromisoformat(x["datetime"]),
                o=float(x["open"]), h=float(x["high"]), l=float(x["low"]), c=float(x["close"]),
                vol=float(x["volume"]), delta=float(x["delta"]), bar_idx=int(x["bar_idx"])))
    csPV = csV = 0.0; q = deque(); roll = 0.0
    for i, b in enumerate(B):
        gap = i > 0 and (b["time"] - B[i-1]["time"]).total_seconds() / 60 > 30
        if gap: csPV = csV = 0.0
        tp = (b["h"] + b["l"] + b["c"]) / 3.0
        csPV += tp * b["vol"]; csV += b["vol"]
        b["vwap"] = csPV / csV if csV > 0 else b["c"]
        q.append(b["vol"]); roll += b["vol"]
        if len(q) > VSA_PERIOD: roll -= q.popleft()
        b["vma"] = roll / len(q) if q else b["vol"]
        b["vratio"] = b["vol"] / b["vma"] if b["vma"] > 1e-9 else 0.0
        b["since_gap"] = 0 if gap else (B[i-1]["since_gap"] + 1 if i > 0 else 999)
        rng = b["h"] - b["l"]; b["rng"] = rng
        b["body"] = abs(b["c"] - b["o"])
        b["uw"] = b["h"] - max(b["o"], b["c"]); b["lw"] = min(b["o"], b["c"]) - b["l"]
        b["brat"] = b["body"] / rng if rng > 0 else 0.0
        b["cpos"] = (b["c"] - b["l"]) / rng if rng > 0 else 0.5
        b["ddom"] = b["delta"] / b["vol"] if b["vol"] > 0 else 0.0
    for i, b in enumerate(B):
        b["trend"] = (0 if i < TREND_LOOKBACK else
                      (1 if b["c"] > B[i-TREND_LOOKBACK]["c"] else -1 if b["c"] < B[i-TREND_LOOKBACK]["c"] else 0))
    return B

def load_levels():
    """bar_idx -> {price: (bid, ask, vol, delta)}"""
    lv = defaultdict(dict)
    with open(DIR + "Data_Footprint_Export.csv", encoding="utf-8-sig") as f:
        for x in csv.DictReader(f):
            lv[int(x["bar_idx"])][round(float(x["price"]), 4)] = (
                float(x["bid_vol"]), float(x["ask_vol"]), float(x["volume"]), float(x["delta"]))
    return lv

# ================== VUNG ==================
def label_of(t):
    m = (t + timedelta(hours=TZ_OFFSET)).hour * 60 + (t + timedelta(hours=TZ_OFFSET)).minute
    if ASIA_START <= m < EUROPE_START: return "A"
    if EUROPE_START <= m < US_START: return "AU"
    return "MY"

def value_area(rows, frac=0.70):
    if not rows: return (None, None, None)
    prices = sorted(rows); w = [rows[p] for p in prices]; tot = sum(w)
    if tot <= 0: return (None, None, None)
    poc = max(range(len(w)), key=lambda i: w[i]); acc = w[poc]; lo = hi = poc; target = tot * frac
    while acc < target and (lo > 0 or hi < len(w) - 1):
        up = (w[hi+1] if hi < len(w)-1 else 0) + (w[hi+2] if hi < len(w)-2 else 0)
        dn = (w[lo-1] if lo > 0 else 0) + (w[lo-2] if lo > 1 else 0)
        if hi >= len(w)-1: acc += dn; lo = max(0, lo-2)
        elif lo <= 0: acc += up; hi = min(len(w)-1, hi+2)
        elif up >= dn: acc += up; hi = min(len(w)-1, hi+2)
        else: acc += dn; lo = max(0, lo-2)
    return (prices[poc], prices[hi], prices[lo])

def profile(B, lv, a, z):
    """volume rows that (giong ProfileEngine.VolumeRows); fallback TPO neu rong."""
    rows = defaultdict(float)
    for i in range(a, z+1):
        for p, (bd, ak, v, d) in lv.get(B[i]["bar_idx"], {}).items():
            rows[round(round(p / TICK) * TICK, 4)] += v
    if not rows:
        for i in range(a, z+1):
            k0 = round(B[i]["l"]/TICK); k1 = round(B[i]["h"]/TICK)
            for k in range(k0, k1+1): rows[round(k*TICK, 4)] += 1
    poc, vah, val = value_area(dict(rows))
    hi = max(B[i]["h"] for i in range(a, z+1)); lo = min(B[i]["l"] for i in range(a, z+1))
    return poc, vah, val, hi, lo

def split_blocks(B, gap_min):
    res = []; start = 0; cur = None; prev = None
    for i, b in enumerate(B):
        lab = label_of(b["time"])
        split = cur is None or lab != cur or (b["time"] - prev).total_seconds()/60 > gap_min
        if split:
            if cur is not None: res.append((start, i-1))
            start = i; cur = lab
        prev = b["time"]
    res.append((start, len(B)-1)); return res

def group_by_gap(B, gap_min):
    res = []; start = 0
    for i in range(1, len(B)):
        if (B[i]["time"] - B[i-1]["time"]).total_seconds()/60 > gap_min:
            res.append((start, i-1)); start = i
    res.append((start, len(B)-1)); return res

def build_pool(B, lv):
    pool = []
    def add(price, kind, strength, ready, exp):
        if price is None or price != price or price <= 0: return
        pool.append(dict(price=price, kind=kind, strength=strength, ready=ready, expire=exp, is_vwap=False))
    sb = split_blocks(B, SESSION_GAP)
    for a, z in sb[:-1]:                                    # bo block dang chay
        lab = label_of(B[a]["time"])
        poc, vah, val, hi, lo = profile(B, lv, a, z)
        if poc is None: continue
        ready = B[z]["time"]; exp = ready + timedelta(days=ZONE_EXPIRE_DAYS)
        for p, k, s in [(poc, f"POC {lab}", 70), (vah, f"VAH {lab}", 58), (val, f"VAL {lab}", 58),
                        (hi, f"Dinh {lab}", 52), (lo, f"Day {lab}", 52)]:
            add(p, k, s, ready, exp)
    db = group_by_gap(B, DAY_GAP)
    for i in range(1, len(db)):
        a0, z0 = db[i-1]
        poc, vah, val, hi, lo = profile(B, lv, a0, z0)
        if poc is None: continue
        ready = B[db[i][0]]["time"]; exp = ready + timedelta(days=1, hours=6)
        for p, k, s in [(vah, "D-1 VAH", 66), (val, "D-1 VAL", 66), (poc, "D-1 POC", 72),
                        (hi, "D-1 Dinh", 60), (lo, "D-1 Day", 60)]:
            add(p, k, s, ready, exp)
    vw = dict(price=0.0, kind="VWAP", strength=64, ready=datetime.min, expire=datetime.max, is_vwap=True)
    pool.append(vw); return pool, vw

# ================== TIN HIEU NEN ==================
def long_sig(b):
    ur = b["lw"] >= WICK_FRAC*b["rng"] and b["cpos"] >= 0.55 and b["delta"] >= 0
    su = b["brat"] >= BODY_STRONG and b["ddom"] >= DELTA_DOM and abs(b["delta"]) >= DELTA_ABS_MIN and b["delta"] > 0 and b["cpos"] >= 0.6
    if b["vratio"] >= VSA_GATE and (ur or su):
        w = (["rut rau duoi"] if ur else []) + (["than manh"] if su else [])
        return True, w + [f"D{b['delta']:+.0f}", f"VSA {b['vratio']:.1f}x" + (" tim" if b["vratio"] >= VSA_CLIMAX else "")]
    return False, []

def short_sig(b):
    dr = b["uw"] >= WICK_FRAC*b["rng"] and b["cpos"] <= 0.45 and b["delta"] <= 0
    sd = b["brat"] >= BODY_STRONG and b["ddom"] <= -DELTA_DOM and abs(b["delta"]) >= DELTA_ABS_MIN and b["delta"] < 0 and b["cpos"] <= 0.4
    if b["vratio"] >= VSA_GATE and (dr or sd):
        w = (["rut rau tren"] if dr else []) + (["than manh"] if sd else [])
        return True, w + [f"D{b['delta']:+.0f}", f"VSA {b['vratio']:.1f}x" + (" tim" if b["vratio"] >= VSA_CLIMAX else "")]
    return False, []

def absorption(lv, b, extreme, side):
    """tuong hap thu per-level (khop EntrySignal.Absorption)."""
    pl = lv.get(b["bar_idx"])
    if not pl: return False
    mean = sum(v[2] for v in pl.values()) / len(pl)
    for p, (bd, ak, v, d) in pl.items():
        if abs(p - extreme) > 3*TICK: continue
        if v < mean*1.5: continue
        dom = abs(d)/v if v > 0 else 0
        if dom >= ABS_DOM and (d < 0 if side > 0 else d > 0): return True
    return False

# ================== MAY TRANG THAI ==================
def cluster_count(pool, t, price):
    seen = set()
    for z in pool:
        if z["is_vwap"] or not (z["ready"] <= t <= z["expire"]): continue
        if abs(z["price"] - price)/TICK > CONFLUENCE_TOL: continue
        seen.add(round(z["price"]/TICK))
    return len(seen)

def next_zone(pool, t, entry, side):
    best = None
    for z in pool:
        if z["is_vwap"] or not (z["ready"] <= t <= z["expire"]): continue
        p = z["price"]
        if side > 0 and p > entry + 5*TICK: best = p if best is None else min(best, p)
        if side < 0 and p < entry - 5*TICK: best = p if best is None else max(best, p)
    return best

def emit(raw, B, pool, i, side, scen, anchor, why, grade, zp):
    b = B[i]; entry = b["c"]; cap = max(SL_CAP, SL_FLOOR)
    if side > 0: sl = min(anchor - SL_BUF*TICK, entry - SL_FLOOR); risk = (entry-sl)/TICK
    else:        sl = max(anchor + SL_BUF*TICK, entry + SL_FLOOR); risk = (sl-entry)/TICK
    if risk <= 0 or risk*TICK > cap + 1e-9: return False
    rd = risk*TICK
    tp1 = entry + RR*rd if side > 0 else entry - RR*rd
    tp2 = tp1; rr2 = RR
    if EXTEND_NEXT_ZONE:
        nz = next_zone(pool, b["time"], entry, side)
        if nz is not None:
            cand = nz - 2*TICK if side > 0 else nz + 2*TICK
            rrc = abs(cand-entry)/rd
            if rrc >= NEXT_ZONE_MIN_R: tp2 = cand; rr2 = rrc
    raw.append(dict(i=i, time=b["time"], side=side, scen=scen, grade=grade, entry=entry, sl=sl,
                    tp1=tp1, tp2=tp2, risk_t=risk, rr2=rr2, vsa=b["vratio"],
                    climax=b["vratio"] >= VSA_CLIMAX, trend=b["trend"], why=why,
                    cluster=cluster_count(pool, b["time"], zp), zone=f"{'VWAP' if zp==0 else ''}{zp:.1f}"))
    return True

def scan(B, pool, lv, vwapz):
    raw = []; n_closed = len(B) - 1
    for z in pool: z.update(state="idle", brk=-999, cool=-999, prev=None)
    for i in range(VSA_PERIOD+2, n_closed):
        b = B[i]; px = b["c"]; vwapz["price"] = b["vwap"]
        gated = b["vol"] >= VOL_FLOOR and b["since_gap"] >= WARMUP_BARS and b["vma"] >= VOL_FLOOR*0.6
        if not gated:
            for z in pool:
                if not (z["ready"] <= b["time"] <= z["expire"]): continue
                if z["price"] <= 0: continue
                z["prev"] = "above" if px > z["price"] else "below"
            continue
        for z in pool:
            if not (z["ready"] <= b["time"] <= z["expire"]): continue
            zp = z["price"]
            if zp <= 0: continue
            rel = "above" if b["c"] > zp+SL_BUF*TICK else "below" if b["c"] < zp-SL_BUF*TICK else "in"
            dist = abs(px-zp)/TICK
            if (dist > ARM_DIST_T and z["state"] == "idle") or i - z["cool"] < COOLDOWN:
                z["prev"] = rel; continue
            zlo = zp - SL_BUF*TICK; zhi = zp + SL_BUF*TICK
            tagged = b["l"] <= zhi and b["h"] >= zlo
            up = z["prev"] == "below"; dn = z["prev"] == "above"
            bu = b["c"] > zhi and b["h"] > zp and b["brat"] >= 0.5 and b["delta"] > 0 and b["vratio"] >= VSA_GATE and z["prev"] in ("below", "in")
            bd = b["c"] < zlo and b["l"] < zp and b["brat"] >= 0.5 and b["delta"] < 0 and b["vratio"] >= VSA_GATE and z["prev"] in ("above", "in")
            if bu: z["state"] = "broke_up"; z["brk"] = i
            elif bd: z["state"] = "broke_dn"; z["brk"] = i
            em = False
            if z["state"] == "broke_up" and 0 < i - z["brk"] <= RETEST_BARS:
                if b["c"] < zp - SL_BUF*TICK: z["state"] = "idle"
                elif b["l"] <= zp + RETEST_TOL*TICK and b["l"] >= zp - RETEST_HOLD_BUF*TICK:
                    ok, w = long_sig(b)
                    if ok: em = emit(raw, B, pool, i, +1, "KB1 pha&hoi", min(b["l"], zp), w, "A", zp)
                if em: z["cool"] = i; z["state"] = "idle"
            elif z["state"] == "broke_dn" and 0 < i - z["brk"] <= RETEST_BARS:
                if b["c"] > zp + SL_BUF*TICK: z["state"] = "idle"
                elif b["h"] >= zp - RETEST_TOL*TICK and b["h"] <= zp + RETEST_HOLD_BUF*TICK:
                    ok, w = short_sig(b)
                    if ok: em = emit(raw, B, pool, i, -1, "KB1 pha&hoi", max(b["h"], zp), w, "A", zp)
                if em: z["cool"] = i; z["state"] = "idle"
            if not em and ENABLE_S2 and z["state"] in ("idle", "broke_up", "broke_dn"):
                if up and tagged and b["c"] < zhi:
                    ok, w = short_sig(b)
                    if ok and b["delta"] < 0:
                        wall = (not REQUIRE_WALL_S2) or absorption(lv, b, b["h"], -1) or (S2_CLIMAX_OVERRIDE and b["vratio"] >= VSA_CLIMAX)
                        if wall and emit(raw, B, pool, i, -1, "KB2 cham&dao", max(b["h"], zp),
                                         w + ["climax" if b["vratio"] >= VSA_CLIMAX else "hap thu"], "B", zp):
                            z["cool"] = i; z["state"] = "idle"
                elif dn and tagged and b["c"] > zlo:
                    ok, w = long_sig(b)
                    if ok and b["delta"] > 0:
                        wall = (not REQUIRE_WALL_S2) or absorption(lv, b, b["l"], +1) or (S2_CLIMAX_OVERRIDE and b["vratio"] >= VSA_CLIMAX)
                        if wall and emit(raw, B, pool, i, +1, "KB2 cham&dao", min(b["l"], zp),
                                         w + ["climax" if b["vratio"] >= VSA_CLIMAX else "hap thu"], "B", zp):
                            z["cool"] = i; z["state"] = "idle"
            z["prev"] = rel
    return raw

def dedup(raw):
    out = []
    for s in sorted(raw, key=lambda x: x["i"]):
        m = None
        for k in out:
            if k["side"] == s["side"] and abs(s["i"]-k["i"]) <= 6 and abs(s["entry"]-k["entry"])/TICK <= DEDUP_TOL:
                m = k; break
        if m: m["confl"] = m.get("confl", 1)+1; m["cluster"] = max(m["cluster"], s["cluster"])
        else: s["confl"] = 1; out.append(s)
    return [s for s in out if s["cluster"] >= MIN_CONFLUENCE]

def simulate(B, s, tpkey="tp1"):
    for j in range(s["i"]+1, len(B)):
        b = B[j]
        hit_sl = b["l"] <= s["sl"] if s["side"] > 0 else b["h"] >= s["sl"]
        hit_tp = b["h"] >= s[tpkey] if s["side"] > 0 else b["l"] <= s[tpkey]
        if hit_sl: return "SL", -1.0, b["time"]
        if hit_tp: return "TP", RR, b["time"]
    return "open", 0.0, B[-1]["time"]

# ================== MAIN ==================
if __name__ == "__main__":
    B = load_bars(); lv = load_levels()
    print(f"bars={len(B)}  {B[0]['time']} -> {B[-1]['time']}  levels_bars={len(lv)}")
    pool, vwapz = build_pool(B, lv)
    print(f"vung = {len(pool)}")
    sig = dedup(scan(B, pool, lv, vwapz))
    for s in sig: s["out"], s["r"], s["outt"] = simulate(B, s)
    print(f"tin hieu (sau gate hop luu>={MIN_CONFLUENCE}) = {len(sig)}")
    print("="*118)
    print(f"{'gio (UTC)':<17}{'KB':<13}{'huong':<6}{'entry':>8}{'SL':>8}{'risk':>6}{'TP1':>8}{'cum':>4}{'VSA':>6}  {'KQ':<5} {'ly do'}")
    for s in sig:
        print(f"{s['time']:%Y-%m-%d %H:%M}  {s['scen']:<13}{'LONG' if s['side']>0 else 'SHORT':<6}"
              f"{s['entry']:>8.1f}{s['sl']:>8.1f}{s['risk_t']*TICK:>6.1f}{s['tp1']:>8.1f}{s['cluster']:>4}"
              f"{s['vsa']:>6.1f}  {s['out']:<5} {' · '.join(s['why'])}")

    # ---- doi chieu voi CSV live ----
    live = []
    with open(DIR + "signals/ENTRY SIGNAL (M1)_2026-08-02.csv", encoding="utf-8-sig") as f:
        for x in csv.DictReader(f):
            live.append((datetime.strptime(x["ngay_gio"], "%Y-%m-%d %H:%M"), x["huong"], float(x["entry"]), x["KQ"]))
    mine = {(s["time"], "LONG" if s["side"] > 0 else "SHORT"): s for s in sig}
    print("="*118)
    print("DOI CHIEU VOI 11 LENH LIVE:")
    hit = 0
    for t, side, e, kq in live:
        m = mine.get((t, side))
        if m: hit += 1; print(f"  ✔ {t:%Y-%m-%d %H:%M} {side:<6} live entry {e:.1f} / replay {m['entry']:.1f}  (KQ live {kq} / replay {m['out']})")
        else: print(f"  ✘ {t:%Y-%m-%d %H:%M} {side:<6} live entry {e:.1f}  -- REPLAY KHONG BAN --")
    print(f"  => tai hien {hit}/{len(live)}")
    extra = [s for k, s in mine.items() if k not in {(t, sd) for t, sd, _, _ in live}]
    print(f"  => replay bắn THEM {len(extra)} lenh khong co trong live:")
    for s in sorted(extra, key=lambda x: x["time"])[:40]:
        print(f"     + {s['time']:%Y-%m-%d %H:%M} {'LONG' if s['side']>0 else 'SHORT':<6} {s['entry']:.1f} {s['scen']} cum{s['cluster']} {s['out']}")
