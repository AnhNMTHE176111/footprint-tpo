#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vi sao KHONG co lenh SHORT 19:20 (07/23) trong CSV? (data futures ro rang ROI 4088->4066)
Sao chep DUNG vong lap run() (ca 2 chieu KB1 + KB2) cho dai vung 4070-4092, log 19:08-19:30.
In: state, prev_rel, cac cong bd/retest short/short_sig, cooldown, het han.
"""
import sys
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
from datetime import timedelta
TICK = em.TICK
BUF, TOL, HOLD = em.BUF_T, em.RETEST_TOL_T, em.RETEST_HOLD_T
RB, CD, ARM = em.RETEST_BARS, em.COOLDOWN_BARS, em.ARM_DIST_T
em.RETEST_HOLD_T = 0
B = em.load_m1(); pool = em.build_zones(B)


def in_win(b):
    return b['dt'].strftime('%m/%d') == '07/23' and (19 * 60 + 8) <= b['dt'].hour * 60 + b['dt'].minute <= (19 * 60 + 30)


# chi trace vung SHORT lien quan (gia xuyen xuong qua chung)
BAND = [dict(z) for z in pool if 4070.0 <= z['price'] <= 4092.0]
for z in BAND:
    z.update(state='idle', brk_bar=-999, cool=-999, prev_rel=None)

print("=" * 100)
print("TRACE phe SHORT — vung 4070-4092, 19:08-19:30 (07/23). Vi sao khong bat cu roi?")
for i in range(em.VSA_MA + 2, len(B)):
    b = B[i]; px = b['c']
    if b['dt'] > B[-1]['dt']:
        break
    active = [z for z in BAND if z['ready'] <= b['dt'] <= z['expire']]
    if not em.gate(b):
        for z in active: z['prev_rel'] = 'above' if px > z['price'] else 'below'
        if in_win(b): print(f"  {b['dt']:%H:%M} GATE-OFF v={b['v']:.0f} (bo qua het)")
        continue
    for z in active:
        zp = z['price']; dist = abs(px - zp) / TICK
        rel = 'above' if b['c'] > zp + BUF * TICK else 'below' if b['c'] < zp - BUF * TICK else 'in'
        log = in_win(b)
        if (dist > ARM and z['state'] == 'idle') or i - z['cool'] < CD:
            if log and dist <= ARM + 15:
                why = 'xa ' + str(int(dist)) + 't' if (dist > ARM and z['state'] == 'idle') else 'COOLDOWN'
                print(f"  {b['dt']:%H:%M} z{zp:.1f} SKIP({why}) st={z['state']} c{b['c']:.1f}")
            z['prev_rel'] = rel; continue
        zlo = zp - BUF * TICK; zhi = zp + BUF * TICK
        tagged = b['lo'] <= zhi and b['hi'] >= zlo
        up = z['prev_rel'] == 'below'; dn = z['prev_rel'] == 'above'
        bd = b['c'] < zlo and b['lo'] < zp and b['brat'] >= 0.5 and b['delta'] < 0 and b['vratio'] >= em.VSA_BREAK and z['prev_rel'] in ('above', 'in')
        bu = b['c'] > zhi and b['hi'] > zp and b['brat'] >= 0.5 and b['delta'] > 0 and b['vratio'] >= em.VSA_BREAK and z['prev_rel'] in ('below', 'in')
        note = []
        if bu: z['state'] = 'broke_up'; z['brk_bar'] = i; note.append("PHA LEN")
        elif bd: z['state'] = 'broke_dn'; z['brk_bar'] = i; note.append("PHA XUONG")
        em_ = False
        if z['state'] == 'broke_dn' and 0 < i - z['brk_bar'] <= RB:
            if b['c'] > zp + BUF * TICK:
                z['state'] = 'idle'; note.append("huy(dong tren vung)")
            elif b['hi'] >= zp - TOL * TICK and b['hi'] <= zp + HOLD * TICK:
                ok, w = em.short_sig(b)
                note.append(f"RETEST-short hi{b['hi']:.1f}<=vung -> short_sig={'OK=>BAN' if ok else 'FAIL(VSA/cautruc)'}")
                if ok: em_ = True; z['cool'] = i; z['state'] = 'idle'
            else:
                if b['hi'] > zp + HOLD * TICK:
                    note.append(f"hoi VUOT vung (hi{b['hi']:.1f}>{zp+HOLD*TICK:.1f}) THUNG -> filter bo")
                else:
                    note.append(f"hi{b['hi']:.1f} chua len toi vung (can>={zp-TOL*TICK:.1f})")
        elif z['state'] == 'broke_dn' and i - z['brk_bar'] > RB:
            note.append(f"het han retest ({i-z['brk_bar']}>{RB})"); z['state'] = 'idle'
        if not em_ and z['state'] in ('idle', 'broke_up', 'broke_dn'):
            if up and tagged and b['c'] < zhi:
                ok, w = em.short_sig(b)
                note.append(f"KB2-cham&dao(tu duoi): short_sig={'OK' if ok else 'FAIL'} delta{'<0 OK' if b['delta']<0 else '>=0 FAIL'}")
                if ok and b['delta'] < 0: em_ = True; z['cool'] = i; z['state'] = 'idle'
        if log and (note or z['state'] == 'broke_dn'):
            print(f"  {b['dt']:%H:%M} z{zp:.1f} c{b['c']:.1f} hi{b['hi']:.1f} lo{b['lo']:.1f} D{b['delta']:+.0f} "
                  f"VSA{b['vratio']:.1f} prev={z['prev_rel']} st={z['state']}  {' | '.join(note) if note else ''}")
        z['prev_rel'] = rel
print("=" * 100)
