#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bang.py — in bảng: python bang.py <tên bộ>[:tag1,tag2] ...   (vd v1_hien_tai:manh v1_hien_tai:hop_hvn)
   python bang.py tung_tag v2_loi_tat_ca   → mỗi loại lõi một dòng"""
import os, sys, pickle
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import vz

if sys.argv[1] == 'tung_tag':
    nm = sys.argv[2]
    tags = set()
    for s in ('nqy', 'gc'):
        p = os.path.join(vz.CDIR, 'vz_%s_%s.pkl' % (s, nm))
        if os.path.exists(p):
            d = pickle.load(open(p, 'rb'))['df']
            if len(d): tags |= set(d.tag.unique())
    for t in sorted(tags):
        vz.table([(t, nm)], tags=[t], title='%s · %s' % (nm, t)) if False else None
    print('\n### %s — từng loại lõi (độ phủ & rộng là của cả bộ)' % nm)
    print('| lõi | rộng | n thật | NQ TRAIN Δ | NQ TEST Δ | GC Δ | gộp tại vùng thật / đ.c / Δ [5–95 %] | sớm | phá | phủ |')
    print('|' + '---|' * 10)
    for t in sorted(tags):
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): vz.table([(t, nm)], tags=[t])
        print(buf.getvalue().strip().splitlines()[-1])
else:
    names = []
    for a in sys.argv[1:]:
        nm, _, tg = a.partition(':')
        names.append((a, nm, tg.split(',') if tg else None))
    for lab, nm, tg in names:
        import io, contextlib
        vz.table([(lab, nm)], tags=tg, title=lab)
