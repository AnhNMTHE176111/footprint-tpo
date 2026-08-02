#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIX A — "nen entry phai THUAN mau voi huong lenh". Do tren replay 03-31/07/2026
(entry_replay_july.py da tai hien 11/11 lenh live).

V0 = hien tai
A1 = BO han lenh co nen entry nguoc mau/doji
A2 = nen nguoc mau -> ARM, cho <=W nen: nen THUAN mau + VSA>=gate + delta thuan => vao
Do o ca 2 muc gate hop luu (>=2 nhu live, va >=1 de tang co mau).
"""
import sys, copy
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_replay_july as R
TICK = R.TICK

def body_dir(b): return 1 if b["c"] > b["o"] else (-1 if b["c"] < b["o"] else 0)

def stat(B, S):
    for s in S:
        if "out" not in s: s["out"], s["r"], s["outt"] = R.simulate(B, s)
    dec = [s for s in S if s["out"] in ("TP", "SL")]
    if not dec: return None
    tot = sum(s["r"] for s in dec)
    return len(S), len(dec), sum(s["out"] == "TP" for s in dec)/len(dec), tot, tot/len(dec)

def line(tag, B, S):
    r = stat(B, S)
    print(f"  {tag:<40} n={r[0]:3} (xong {r[1]:3}) WR {r[2]:5.1%} tong {r[3]:+6.1f}R exp {r[4]:+5.2f}R" if r
          else f"  {tag:<40} n={len(S)} (chua co lenh nao xong)")

def confirm_variant(B, S, W, need_delta=True, vsa=R.VSA_GATE, kill_anchor=True, kill_zone=True):
    """S = cac tin hieu nguoc mau. Tra ve tin hieu moi tai nen xac nhan."""
    out = []
    for s in S:
        side = s["side"]; i = s["i"]
        zp = float(s["zone"].replace("VWAP", "")) if s["zone"] else 0
        anchor = s["sl"] + R.SL_BUF*TICK if side > 0 else s["sl"] - R.SL_BUF*TICK
        for j in range(i+1, min(i+1+W, len(B)-1)):
            b = B[j]
            if not (b["vol"] >= R.VOL_FLOOR and b["since_gap"] >= R.WARMUP_BARS): continue
            if kill_zone and side > 0 and b["c"] < zp - R.SL_BUF*TICK: break
            if kill_zone and side < 0 and b["c"] > zp + R.SL_BUF*TICK: break
            if kill_anchor and side > 0 and b["l"] < anchor: break
            if kill_anchor and side < 0 and b["h"] > anchor: break
            if body_dir(b) != side: continue
            if b["vratio"] < vsa: continue
            if need_delta and (b["delta"] <= 0 if side > 0 else b["delta"] >= 0): continue
            a = min(anchor, b["l"]) if side > 0 else max(anchor, b["h"])
            entry = b["c"]
            sl = min(a - R.SL_BUF*TICK, entry - R.SL_FLOOR) if side > 0 else max(a + R.SL_BUF*TICK, entry + R.SL_FLOOR)
            risk = abs(entry-sl)/TICK
            if risk <= 0 or risk*TICK > max(R.SL_CAP, R.SL_FLOOR) + 1e-9: break
            n = dict(s); n.update(i=j, time=b["time"], entry=entry, sl=sl, risk_t=risk,
                                  tp1=entry + R.RR*risk*TICK if side > 0 else entry - R.RR*risk*TICK,
                                  vsa=b["vratio"])
            n.pop("out", None)
            out.append(n); break
    return out

if __name__ == "__main__":
    B = R.load_bars(); lv = R.load_levels(); pool, vw = R.build_pool(B, lv)
    raw = R.scan(B, pool, lv, vw)
    for gate in (2, 1):
        R.MIN_CONFLUENCE = gate
        sig = R.dedup(copy.deepcopy(raw))
        for s in sig: s["out"], s["r"], s["outt"] = R.simulate(B, s)
        good = [s for s in sig if body_dir(B[s["i"]]) == s["side"]]
        bad = [s for s in sig if body_dir(B[s["i"]]) != s["side"]]
        print("="*100)
        print(f"GATE HOP LUU >= {gate}   (tong {len(sig)} lenh: thuan mau {len(good)} / nguoc-doji {len(bad)})")
        line("V0 hien tai", B, sig)
        line("   -> rieng nhom THUAN mau", B, good)
        line("   -> rieng nhom NGUOC mau/doji", B, bad)
        line("A1 = bo han nhom nguoc mau", B, good)
        for ka, kz, nm in ((True, True, "huy khi thung neo HOAC xuyen vung"),
                           (False, True, "huy khi xuyen vung"),
                           (False, False, "khong huy, chi cho toi W nen")):
            print(f"  --- A2, quy tac huy ARM: {nm} ---")
            for W in (3, 6, 10):
                c = confirm_variant(B, [dict(s) for s in bad], W, kill_anchor=ka, kill_zone=kz)
                line(f"    A2 W={W}: thuan + xac nhan (tim {len(c)}/{len(bad)})", B, good + c)
