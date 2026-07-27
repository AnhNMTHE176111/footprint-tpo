#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
6 SETUP ground-truth cua user (5 anh moi + 19:20 da xac nhan). Soi tung MOC THOI GIAN
trong data futures xem SHAPE co that khong: pha range -> hoi GIU vung -> nen tiep dien.
Gia CFD != futures -> KHONG khop gia, chi khop THOI GIAN + HINH DANG (user da chot dung the).
In moi setup:
  - cua so nen quanh entry (O/H/L/C/delta/VSA/body%/cpos/bias)
  - zone (build_zones) gan vung gia luc do -> co "range" bi pha khong
  - MFE khong cap: neu vao tai moc do voi SL cau truc (day/dinh nhip hoi) -> may R?
"""
import sys
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
B = em.load_m1(); pool = em.build_zones(B)

# (ngay, gio, phut, side, SL_gia_user) — gia entry CFD bo qua, chi dung mo ta
SETUPS = [
    ('07/20', 12, 7, 'SHORT', 3.04),
    ('07/21', 8, 1, 'LONG', 4.00),
    ('07/21', 12, 36, 'LONG', 4.25),
    ('07/22', 8, 1, 'LONG', 5.95),
    ('07/22', 20, 39, 'LONG', 4.73),
    ('07/23', 19, 20, 'SHORT', 5.80),
]


def idx_at(day, hh, mm):
    return next((i for i, b in enumerate(B) if b['dt'].strftime('%m/%d') == day
                 and b['dt'].hour == hh and b['dt'].minute == mm), None)


def struct_sl_risk(i, side, look=8):
    """SL cau truc = cuc tri nhip hoi (day/dinh 'look' nen truoc entry) + 2 tick buf."""
    seg = B[max(0, i - look):i + 1]
    if side == 'LONG':
        ext = min(x['lo'] for x in seg); sl = ext - em.BUF_T * TICK; risk = (B[i]['c'] - sl)
    else:
        ext = max(x['hi'] for x in seg); sl = ext + em.BUF_T * TICK; risk = (sl - B[i]['c'])
    return sl, risk


def max_R(i, side, entry, sl):
    """Tran R that su (theo day/dinh) TRUOC khi cham SL — khong cap thoi gian."""
    risk = abs(sl - entry); best = 0.0; slat = None
    for j in range(i + 1, len(B)):
        b = B[j]
        fav = (entry - b['lo']) / risk if side == 'SHORT' else (b['hi'] - entry) / risk
        best = max(best, fav)
        if (b['hi'] >= sl) if side == 'SHORT' else (b['lo'] <= sl):
            slat = b['dt']; break
    return best, slat


def near_zones(t, px, tol_gia=6.0):
    out = []
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - px) <= tol_gia:
            out.append((abs(z['price'] - px), z['price'], z['kind']))
    out.sort()
    return out[:6]


print("=" * 108)
for day, hh, mm, side, sl_user in SETUPS:
    i = idx_at(day, hh, mm)
    print(f"\n{'#'*4} {day} {hh:02d}:{mm:02d} {side}  (user: SL {sl_user:.2f} gia)")
    if i is None:
        print("   !! khong tim thay nen tai moc nay trong data"); continue
    b = B[i]
    print(f"   nen entry futures: O{b['o']:.1f} H{b['hi']:.1f} L{b['lo']:.1f} C{b['c']:.1f} "
          f"D{b['delta']:+.0f} VSA{b['vratio']:.2f} body{b['brat']*100:.0f}% cpos{b['cpos']:.2f} "
          f"bias{b['bias']:+d} {'(thuan)' if (b['bias']>=0)==(side=='LONG') else '(NGUOC)'}")
    # cua so -15 .. +3 nen
    print("   --- cua so M1 (entry = *) ---")
    for j in range(max(0, i - 15), min(len(B), i + 4)):
        x = B[j]; mk = ' *' if j == i else '  '
        print(f"   {mk}{x['dt']:%H:%M} O{x['o']:7.1f} H{x['hi']:7.1f} L{x['lo']:7.1f} C{x['c']:7.1f}"
              f" D{x['delta']:+5.0f} VSA{x['vratio']:4.2f} b{x['brat']*100:3.0f}% cp{x['cpos']:.2f}")
    zs = near_zones(b['dt'], b['c'])
    print(f"   zone gan gia {b['c']:.1f}: " + (", ".join(f"{p:.1f}({k})" for _, p, k in zs) if zs else "(khong co trong 6 gia)"))
    for look in (6, 10):
        sl, risk = struct_sl_risk(i, side, look)
        R, slat = max_R(i, side, b['c'], sl)
        tag = f"SL bi quet {slat:%m/%d %H:%M}" if slat else "SL KHONG bi quet"
        print(f"   SL cau truc ({look}nen): {sl:.1f} risk {risk/TICK/10:.1f}gia -> TRAN {R:.1f}R ({tag})")
print("\n" + "=" * 108)
