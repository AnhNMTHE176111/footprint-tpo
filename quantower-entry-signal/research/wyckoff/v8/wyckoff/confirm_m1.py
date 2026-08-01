#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
confirm_m1.py — nen xac nhan M1, dung chung PLAY1 (cham->dao) va PLAY2 (pha->hoi->tiep)
(CORVEN_SPEC_V1.md §1 "A5+R8", PLAN_KB_ABC.md §4.3).

Dinh nghia DE XUAT — CAN KIEM (chua co trong tai lieu goc, tu suy tu "nen xac nhan"):
  LONG : close>open  VA  cpos>=CPOS_MIN (dong nua tren)  VA  brat>=BODY_MIN (than du day)
         VA  rau NGUOC (rau tren, uw) <= WICK_MAX * range
  SHORT: guong lai (cpos<=1-CPOS_MIN, rau duoi lw <= WICK_MAX*range)

Doi hoi doc truc tiep tren dict-bar cua entry_dxfeed.load_m1 (co san 'rng','brat','cpos','uw','lw').
"""
CPOS_MIN = 0.60
BODY_MIN = 0.30
WICK_MAX = 0.35


def confirm_long(b, cpos_min=CPOS_MIN, body_min=BODY_MIN, wick_max=WICK_MAX):
    if b['rng'] <= 0:
        return False
    return (b['c'] > b['o'] and b['cpos'] >= cpos_min and b['brat'] >= body_min
            and (b['uw'] / b['rng']) <= wick_max)


def confirm_short(b, cpos_min=CPOS_MIN, body_min=BODY_MIN, wick_max=WICK_MAX):
    if b['rng'] <= 0:
        return False
    return (b['c'] < b['o'] and b['cpos'] <= (1 - cpos_min) and b['brat'] >= body_min
            and (b['lw'] / b['rng']) <= wick_max)
