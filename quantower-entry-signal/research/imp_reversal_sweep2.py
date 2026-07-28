#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused follow-up: verify the cpos-band expansion mechanism + best combos around it."""
import imp_reversal_sweep as S

B=S.bars()

def keyset(sigs): return {(s['dt'].strftime('%Y-%m-%d %H:%M'), s['side']) for s in sigs}

base = S.in_window(B, S.detect(B))                       # LIVE
wide = S.in_window(B, S.detect(B, cpos_h=0.0))           # cpos band -> midpoint
added = [s for s in wide if (s['dt'].strftime('%Y-%m-%d %H:%M'), s['side']) not in keyset(base)]

print("MECHANISM CHECK — cpos band 0.45/0.55 -> 0.50/0.50")
print("  ADDED trades = those with close on correct HALF but NOT in outer 45/55 band")
S.fmt(S.score(B, base,  1.5), "base(27)")
S.fmt(S.score(B, wide,  1.5), "wide cpos_h=0")
S.fmt(S.score(B, added, 1.5), "ADDED only")
print("  cpos of ADDED trades (should sit in 0.45..0.55 midband):")
for s in sorted(added, key=lambda x:x['dt']):
    b=B[s['i']]
    print(f"    {s['dt']:%Y-%m-%d %H:%M} {s['side']:5s} cpos={b['cpos']:.3f} uw/rng={b['uw']/b['rng']:.2f} lw/rng={b['lw']/b['rng']:.2f} vsa={b['vratio']:.2f}")

print("\nBEST COMBOS around cpos_h=0 (push count higher, need ALL+ every month):")
def run(label, **kw):
    return S.fmt(S.score(B, S.in_window(B, S.detect(B, **kw)), 1.5), label)
run("cpos0", cpos_h=0.0)
run("cpos0+vsa1.6", cpos_h=0.0, vsa_conf=1.6)
run("cpos0+wick0.45", cpos_h=0.0, wick_frac=0.45)
run("cpos0+tol16", cpos_h=0.0, vwap_tol_t=16)
run("cpos0+vsa1.6+wick0.45", cpos_h=0.0, vsa_conf=1.6, wick_frac=0.45)

print("\nRR sensitivity at cpos_h=0 (does looser set still like 1.5R?):")
for rr in (1.0,1.25,1.5,2.0):
    run(f"cpos0 rr={rr}", cpos_h=0.0, rr=rr)
