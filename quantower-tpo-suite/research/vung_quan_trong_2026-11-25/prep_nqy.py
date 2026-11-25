#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prep_nqy.py — bộ đệm vm1_nqy.pkl: NQZ26 file 293 ngày, chỉ phần là hợp đồng chính (từ 2026-09-13 21:30 UTC).
Tháng 2–8 NQZ26 còn là hợp đồng phụ (nến thưa, lỗ thời gian hàng trăm lần) ⇒ không dùng."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vung_manh_2026-11-25'))
import prep1
prep1.CFG['nqy'] = dict(scale=2.5, tick=0.25, t_min='2026-09-13 21:30:00', src=[
    ('fp_NQZ26_XCME_Time_20260204-20261125_293d16h', None, None)])
if __name__ == '__main__':
    prep1.main('nqy')
