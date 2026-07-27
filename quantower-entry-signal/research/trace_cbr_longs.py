#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vi sao CBR khong bat 4 long? In tung dieu kien BREAK-up tai moi nen quanh 4 moc long."""
import sys
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
import entry_cbr as C
TICK = em.TICK
B = em.load_m1()

LONGS = [('07/21', 8, 1), ('07/21', 12, 36), ('07/22', 8, 1), ('07/22', 20, 39)]


def idx(day, hh, mm):
    return next((k for k, b in enumerate(B) if b['dt'].strftime('%m/%d') == day and b['dt'].hour == hh and b['dt'].minute == mm), None)


print("=" * 110)
for day, hh, mm in LONGS:
    i0 = idx(day, hh, mm)
    print(f"\n#### {day} {hh:02d}:{mm:02d} LONG — tim nen PHA-UP hop le (range<= {C.RANGE_MAX_T/10}gia, VSA>={C.BREAK_VSA}, body>={C.BREAK_BODY}, bias>=0):")
    for i in range(i0 - 12, i0 + 3):
        b = B[i]
        win = B[i - C.RANGE_LEN:i]
        rhi = max(x['hi'] for x in win); rlo = min(x['lo'] for x in win)
        span = (rhi - rlo) / TICK
        g = em.gate(b)
        cond_break = b['c'] > rhi + C.BUF * TICK
        fails = []
        if not g: fails.append('GATE')
        if span > C.RANGE_MAX_T: fails.append(f'span{span/10:.1f}>7.5')
        if not cond_break: fails.append(f'c{b["c"]:.1f}<=rhi{rhi:.1f}')
        if b['vratio'] < C.BREAK_VSA: fails.append(f'VSA{b["vratio"]:.1f}<2')
        if b['brat'] < C.BREAK_BODY: fails.append(f'body{b["brat"]*100:.0f}%<50')
        if b['c'] <= b['o']: fails.append('do')
        if b['bias'] < 0: fails.append(f'bias{b["bias"]}')
        ok = not fails
        mk = '>>> PHA-UP OK' if ok else ''
        print(f"   {b['dt']:%H:%M} c{b['c']:7.1f} rhi{rhi:7.1f} span{span:4.0f}t VSA{b['vratio']:4.1f} body{b['brat']*100:3.0f}% bias{b['bias']:+d}"
              + (f"  {mk}" if ok else f"  x {','.join(fails)}"))
print("\n" + "=" * 110)
