#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A/B FIX A tren toan bo du lieu footprint M1 (Data_Footprint_Export*, 02->07/2026).

V0  = hien tai (khong kiem mau nen entry)
A1  = bo han lenh co nen kich hoat nguoc mau/doji  (ConfirmWindow=0)
A2  = nguoc mau -> ARM, cho <=W nen xac nhan       (ConfirmWindow=W)

Toi uu: MIN_CONFLUENCE chi anh huong buoc dedup, KHONG anh huong scan
=> moi bien the chi quet 1 lan, roi dedup o ca 2 muc gate.
"""
import sys, copy
from collections import defaultdict
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_replay_july as R

def report(label, B, raw, pool):
    for gate in (2, 1):
        R.MIN_CONFLUENCE = gate
        sig = R.dedup(copy.deepcopy(raw))
        for s in sig: s["out"], s["r"], s["outt"] = R.simulate(B, s)
        dec = [s for s in sig if s["out"] in ("TP", "SL")]
        if not dec:
            print(f"  [cum>={gate}] {label:<34} n={len(sig)} (chua co lenh nao xong)"); continue
        tot = sum(s["r"] for s in dec)
        wr = sum(s["out"] == "TP" for s in dec)/len(dec)
        bym = defaultdict(list)
        for s in dec: bym[s["time"].strftime("%Y-%m")].append(s["r"])
        mm = "  ".join(f"{m[5:]}:{sum(v):+.0f}R/{len(v)}" for m, v in sorted(bym.items()))
        print(f"  [cum>={gate}] {label:<34} n={len(sig):3} xong={len(dec):3} WR {wr:5.1%} "
              f"tong {tot:+6.1f}R exp {tot/len(dec):+5.2f}R")
        print(f"              thang: {mm}")

if __name__ == "__main__":
    B = R.load_bars(); lv = R.load_levels()
    print(f"bars={len(B)}  {B[0]['time']} -> {B[-1]['time']}")
    pool0, _ = R.build_pool(B, lv)
    print(f"vung={len(pool0)}")
    VARIANTS = [("V0 hien tai", dict(REQUIRE_ENTRY_BODY_DIR=False)),
                ("A1 bo lenh nguoc mau", dict(REQUIRE_ENTRY_BODY_DIR=True, CONFIRM_WINDOW=0)),
                ("A2 cho xac nhan W=2", dict(REQUIRE_ENTRY_BODY_DIR=True, CONFIRM_WINDOW=2)),
                ("A2 cho xac nhan W=3", dict(REQUIRE_ENTRY_BODY_DIR=True, CONFIRM_WINDOW=3)),
                ("A2 cho xac nhan W=6", dict(REQUIRE_ENTRY_BODY_DIR=True, CONFIRM_WINDOW=6))]
    for label, kw in VARIANTS:
        for k, v in kw.items(): setattr(R, k, v)
        pool = copy.deepcopy(pool0); vw = [z for z in pool if z["is_vwap"]][0]
        raw = R.scan(B, pool, lv, vw)
        print("="*104)
        report(label, B, raw, pool)
        sys.stdout.flush()
