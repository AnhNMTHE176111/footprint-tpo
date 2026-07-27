#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dung lai nen M5 tu M1 futures de doi chieu doc cua user:
  "pha o 18:20, hoi ve 19:15, vao lenh 19:20 (short)".
In M5 07/23 17:30-19:45 (O/H/L/C/range/delta/mau) + nen M1 chi tiet tai 18:20, 19:15, 19:20.
Luu y: day la GCQ26 futures, khong phai CFD user trade -> co the lech.
"""
import sys
from collections import OrderedDict
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
B = em.load_m1()


def m5key(dt):
    return dt.replace(minute=(dt.minute // 5) * 5, second=0)


groups = OrderedDict()
for b in B:
    m = b['dt'].hour * 60 + b['dt'].minute
    if b['dt'].strftime('%m/%d') == '07/23' and (17 * 60 + 30) <= m <= (19 * 60 + 45):
        groups.setdefault(m5key(b['dt']), []).append(b)

print("=" * 96)
print("NEN M5 (dung lai tu M1 futures) — 07/23 17:30-19:45")
print(f"  {'M5':<7}{'O':>8}{'H':>8}{'L':>8}{'C':>8}{'range':>7}{'delta':>8}  mau")
rows = list(groups.items())
for k, bars in rows:
    o = bars[0]['o']; h = max(x['hi'] for x in bars); l = min(x['lo'] for x in bars); c = bars[-1]['c']
    d = sum(x['delta'] for x in bars)
    mau = 'XANH' if c > o else ('do' if c < o else '--')
    mark = ""
    hh = k.hour * 60 + k.minute
    if hh == 18 * 60 + 20: mark = "  <== user: PHA"
    if hh == 19 * 60 + 15: mark = "  <== user: HOI (dinh?)"
    if hh == 19 * 60 + 20: mark = "  <== user: VAO short"
    print(f"  {k:%H:%M}{o:>8.1f}{h:>8.1f}{l:>8.1f}{c:>8.1f}{h-l:>6.1f}{d:>+8.0f}  {mau}{mark}")

# tom tat cau truc
his = [(k, max(x['hi'] for x in bars)) for k, bars in rows]
los = [(k, min(x['lo'] for x in bars)) for k, bars in rows]
peak = max(his, key=lambda t: t[1]); trough = min(los, key=lambda t: t[1])
print(f"\n  Dinh cao nhat khung: {peak[1]:.1f} luc {peak[0]:%H:%M} | Day thap nhat: {trough[1]:.1f} luc {trough[0]:%H:%M}")

# M1 chi tiet 3 moc
print("\n  --- M1 chi tiet 3 moc user neu ---")
for tag, hh, mm in [("18:20", 18, 20), ("19:15", 19, 15), ("19:20", 19, 20)]:
    b = next((x for x in B if x['dt'].strftime('%m/%d') == '07/23' and x['dt'].hour == hh and x['dt'].minute == mm), None)
    if b:
        print(f"    {tag}: O{b['o']:.1f} H{b['hi']:.1f} L{b['lo']:.1f} C{b['c']:.1f} D{b['delta']:+.0f} "
              f"VSA{b['vratio']:.1f} {'XANH' if b['c']>b['o'] else 'do'}")
print("=" * 96)
