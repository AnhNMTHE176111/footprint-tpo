#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tra loi: vi sao 19:20 (07/23) KHONG co entry LONG (ban 3R hay bat ky ban nao)?
1) Liet ke MOI signal full-run 07/23 17:00-20:00.
2) Liet ke vung active tai 19:20 quanh gia.
3) TRACE trang thai may cho vung vung ~4088 (cu pha lenh 2) tung nen 18:10-19:30:
   armed luc nao, het han retest luc nao, cooldown, va tai sao 19:20 khong ban.
Sao chep DUNG logic run() (chi loc vung + them log).
"""
import sys
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
em.RETEST_HOLD_T = 0
B = em.load_m1(); pool = em.build_zones(B)
raw = em.run(B, pool); sig = em.dedup(raw)

print("=" * 96)
print("1) MOI signal full-run 07/23 17:00-20:00:")
for s in sorted(sig, key=lambda x: x['i']):
    if s['dt'].strftime('%m/%d') == '07/23' and 17 <= s['dt'].hour < 20:
        print(f"   {s['dt']:%H:%M}  {s['side']:<5} {s['scen']:<18} {s['zone']:<16} entry {s['entry']:.1f} SL {s['sl']:.1f}")

t1920 = [b['dt'] for b in B if b['dt'].strftime('%m/%d') == '07/23' and b['dt'].hour == 19 and b['dt'].minute == 20][0]
print(f"\n2) Vung active tai {t1920:%H:%M} trong dai 4060-4095:")
for z in sorted([z for z in pool if z['ready'] <= t1920 <= z['expire'] and 4060 <= z['price'] <= 4095], key=lambda z: z['price']):
    print(f"   {z['kind']:<12} {z['price']:>7.1f}   ready {z['ready']:%m/%d %H:%M}  expire {z['expire']:%m/%d %H:%M}")

# 3) trace state cho vung [4085,4092]
print(f"\n3) TRACE trang thai may — vung ~4088 (cu pha lenh 2), 18:10 -> 19:30:")
ZBAND = [dict(z) for z in pool if 4085.0 <= z['price'] <= 4092.0]
for z in ZBAND:
    z.update(state='idle', brk_bar=-999, cool=-999, prev_rel=None)
BUF = em.BUF_T; TOL = em.RETEST_TOL_T; HOLD = em.RETEST_HOLD_T
RB = em.RETEST_BARS; CD = em.COOLDOWN_BARS; ARM = em.ARM_DIST_T

# warm prev_rel toi 18:09
i0 = next(i for i, b in enumerate(B) if b['dt'].strftime('%m/%d') == '07/23' and b['dt'].hour == 18 and b['dt'].minute == 10)
for i in range(em.VSA_MA + 2, len(B)):
    b = B[i]; px = b['c']
    for z in ZBAND:
        if not (z['ready'] <= b['dt'] <= z['expire']):
            continue
        zp = z['price']; dist = abs(px - zp) / TICK
        rel = 'above' if b['c'] > zp + BUF * TICK else 'below' if b['c'] < zp - BUF * TICK else 'in'
        log = (i >= i0 and i <= i0 + 80)
        if not em.gate(b):
            if log: print(f"   {b['dt']:%H:%M} z{zp:.1f} GATE-OFF (v{b['v']:.0f}) state={z['state']}")
            z['prev_rel'] = 'above' if px > zp else 'below'; continue
        if (dist > ARM and z['state'] == 'idle') or i - z['cool'] < CD:
            if log: print(f"   {b['dt']:%H:%M} z{zp:.1f} SKIP ({'xa '+str(int(dist))+'t' if dist>ARM and z['state']=='idle' else 'cooldown'}) state={z['state']} c{b['c']:.1f}")
            z['prev_rel'] = rel; continue
        zlo = zp - BUF * TICK; zhi = zp + BUF * TICK
        bu = b['c'] > zhi and b['hi'] > zp and b['brat'] >= 0.5 and b['delta'] > 0 and b['vratio'] >= em.VSA_BREAK and z['prev_rel'] in ('below', 'in')
        bd = b['c'] < zlo and b['lo'] < zp and b['brat'] >= 0.5 and b['delta'] < 0 and b['vratio'] >= em.VSA_BREAK and z['prev_rel'] in ('above', 'in')
        note = ""
        if bu: z['state'] = 'broke_up'; z['brk_bar'] = i; note = "-> PHA LEN (broke_up)"
        elif bd: z['state'] = 'broke_dn'; z['brk_bar'] = i; note = "-> PHA XUONG (broke_dn)"
        fired = False
        if z['state'] == 'broke_up' and 0 < i - z['brk_bar'] <= RB:
            if b['c'] < zp - BUF * TICK:
                z['state'] = 'idle'; note += " | huy (dong duoi vung)"
            elif b['lo'] <= zp + TOL * TICK and b['lo'] >= zp - HOLD * TICK:
                ok, w = em.long_sig(b)
                note += f" | RETEST cham vung, long_sig={'OK' if ok else 'FAIL'}"
                if ok: fired = True; z['cool'] = i; z['state'] = 'idle'; note += " => BAN LONG"
            else:
                note += f" | trong cua retest nhung low {b['lo']:.1f} chua cham vung (can<= {zp+TOL*TICK:.1f})"
        elif z['state'] == 'broke_up' and i - z['brk_bar'] > RB:
            note += f" | het han retest ({i-z['brk_bar']} nen > {RB}) -> reset"
            z['state'] = 'idle'
        if log and (note or z['state'] != 'idle'):
            print(f"   {b['dt']:%H:%M} z{zp:.1f} c{b['c']:.1f} lo{b['lo']:.1f} D{b['delta']:+.0f} VSA{b['vratio']:.1f} state={z['state']} {note}")
        z['prev_rel'] = rel
    if i > i0 + 80:
        break
print("=" * 96)
