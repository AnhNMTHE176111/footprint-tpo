#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Log tung buoc may trang thai tai POC A(4051.5)+POC MY(4051.7) tu 20:28->20:36, ngay 7/24.
   Chi ra CHINH XAC luat nao chan entry 20:31/4051.8."""
import sys
from datetime import timedelta
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
BUF = em.BUF_T; RB = em.RETEST_BARS; RTOL = em.RETEST_TOL_T
B = em.load_m1(); pool = em.build_zones(B)

# 2 zone POC quanh 4051.6
zA = None; zMY = None
for z in pool:
    if z['kind'] == 'POC A' and abs(z['price'] - 4051.5) < 0.2: zA = dict(z)
    if z['kind'] == 'POC MY' and abs(z['price'] - 4051.7) < 0.2: zMY = dict(z)
print("Zones:", zA['kind'], zA['price'], "|", zMY['kind'], zMY['price'])


def long_sig_dbg(b):
    rng = b['rng']
    ur_wick = b['lw'] >= em.WICK_FRAC * rng
    ur = ur_wick and b['cpos'] >= em.CLOSEPOS_HI and b['delta'] >= 0
    su_body = b['brat'] >= em.BODY_STRONG
    su_dom = b['ddom'] >= em.DDOM_STRONG
    su = su_body and su_dom and abs(b['delta']) >= em.DELTA_ABS_MIN and b['cpos'] >= 0.6
    vsa_ok = b['vratio'] >= em.VSA_GATE
    return dict(long_sig=(vsa_ok and (ur or su)), vsa_ok=vsa_ok, ur=ur,
                ur_wick=f"lw{b['lw']:.1f}>=0.5*rng{rng:.1f}({0.5*rng:.1f})?{ur_wick}",
                su=su, su_body=f"brat{b['brat']:.2f}>=0.55?{su_body}",
                su_dom=f"ddom{b['ddom']:.3f}>=0.25?{su_dom}")


# chay may trang thai tu dau ngay toi 20:36, log tu 20:28
for z in (zA, zMY): z.update(state='idle', brk_bar=-999, cool=-999, prev_rel=None)
for i in range(em.VSA_MA + 2, len(B)):
    b = B[i]
    if b['dt'].strftime('%m/%d') != '07/24':
        # van phai cap nhat prev_rel de trang thai dung
        pass
    log = b['dt'].strftime('%m/%d') == '07/24' and 20 * 60 + 28 <= b['dt'].hour * 60 + b['dt'].minute <= 20 * 60 + 36
    for z in (zA, zMY):
        if not (z['ready'] <= b['dt'] <= z['expire']):
            continue
        zp = z['price']; px = b['c']; dist = abs(px - zp) / TICK
        rel = 'above' if b['c'] > zp + BUF * TICK else 'below' if b['c'] < zp - BUF * TICK else 'in'
        armed_block = (dist > em.ARM_DIST_T and z['state'] == 'idle') or i - z['cool'] < em.COOLDOWN_BARS
        if log:
            zhi = zp + BUF * TICK; zlo = zp - BUF * TICK
            bu = b['c'] > zhi and b['hi'] > zp and b['brat'] >= 0.5 and b['delta'] > 0 and b['vratio'] >= em.VSA_BREAK and z['prev_rel'] in ('below', 'in')
            ls = long_sig_dbg(b)
            print(f"\n{b['dt']:%H:%M} {z['kind']}{zp:.1f} | C{b['c']:.1f} Δ{b['delta']:+.0f} vsa{b['vratio']:.1f} "
                  f"| prev_rel={z['prev_rel']} rel={rel} state={z['state']} dist{dist:.0f}t armed_block={armed_block}")
            print(f"      break_up? C>{zhi:.1f}={b['c']>zhi} H>{zp:.1f}={b['hi']>zp} brat>=.5={b['brat']>=0.5} Δ>0={b['delta']>0} vsa>=1.2={b['vratio']>=em.VSA_BREAK} prev∈(below,in)={z['prev_rel'] in ('below','in')} => bu={bu}")
            print(f"      long_sig={ls['long_sig']}  (ur={ls['ur']}:{ls['ur_wick']} | su={ls['su']}:{ls['su_body']},{ls['su_dom']})")
        # cap nhat trang thai (rut gon logic run())
        if armed_block:
            z['prev_rel'] = rel; continue
        zhi = zp + BUF * TICK; zlo = zp - BUF * TICK
        bu = b['c'] > zhi and b['hi'] > zp and b['brat'] >= 0.5 and b['delta'] > 0 and b['vratio'] >= em.VSA_BREAK and z['prev_rel'] in ('below', 'in')
        bd = b['c'] < zlo and b['lo'] < zp and b['brat'] >= 0.5 and b['delta'] < 0 and b['vratio'] >= em.VSA_BREAK and z['prev_rel'] in ('above', 'in')
        if bu: z['state'] = 'broke_up'; z['brk_bar'] = i
        elif bd: z['state'] = 'broke_dn'; z['brk_bar'] = i
        if z['state'] == 'broke_up' and 0 < i - z['brk_bar'] <= RB:
            if b['c'] < zp - BUF * TICK:
                if log: print(f"      >> RESET: C{b['c']:.1f} < {zp-BUF*TICK:.1f} (roi lai duoi cum) -> broke_up HUY")
                z['state'] = 'idle'
            elif b['lo'] <= zp + RTOL * TICK:
                ok, _ = em.long_sig(b)
                if log: print(f"      >> RETEST cham cum, long_sig={ok}")
        z['prev_rel'] = rel
    if b['dt'].strftime('%m/%d') == '07/24' and b['dt'].hour == 20 and b['dt'].minute > 36:
        break
print("\n" + "=" * 80)
print("KET: 20:31 = nen PHA (broke_up) nhung long_sig=False; 20:32 dong 4050.0 -> RESET broke_up;")
print("     cac nen retest sau (20:34 vsa0.7) qua yeu. Move 4R that su chi bat dau 20:35+.")
