#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vung_dem_prep.py — bộ đệm NQZ26 tới 2026-11-25 08:47 UTC cho phép đo "vùng đệm" (VUNG-DEM.md).
Ghép file 90 ngày (tới hết tuần 15→20/11) với file mới fp_NQZ26_..._20261115-20261125_9d9h (từ 2026-11-22).
Ra vm1_nq25.pkl cùng định dạng prep1.py. KHÔNG đụng vm1_nq.pkl (fixture v2 sinh từ đó).
  python vung_dem_prep.py
"""
import prep1
prep1.CFG['nq25'] = dict(scale=2.5, tick=0.25, t_min='2026-09-13 21:30:00', src=[
    ('fp_NQZ26_XCME_Time_20260826-20261124_90d', None, '2026-11-22 00:00:00'),
    ('fp_NQZ26_XCME_Time_20261115-20261125_9d9h', '2026-11-22 00:00:00', None)])
if __name__ == '__main__':
    prep1.main('nq25')
