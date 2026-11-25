#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""flick5.py — vì sao vùng / hộp đang vẽ bị tắt rồi hiện lại: python flick5.py nqy|gc VONG"""
import os, sys, pickle, tempfile
import numpy as np
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import bt5
CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())
sym, vong = sys.argv[1], sys.argv[2]
o = pickle.load(open(os.path.join(CDIR, 'bt5_%s_%s_objs.pkl' % (sym, vong)), 'rb'))['objs']
D, vm, V = bt5.load(sym)
cfg = bt5.VONG[vong]
p = dict(V.P, HVN_MODE='cum2', HVN_HL='giao', D_ONLY=False, HVN_AWAY=2.0, REQ_HVN=False, HVN_BAND=0.0); p.update(cfg.get('P', {}))
eng = V.Engine(D, p)
gaps = []
for k, ob in o.items():
    v = ob['vis']
    for a, b in zip(v[:-1], v[1:]):
        if b - a > 1: gaps.append((k, ob, a, b))
print('số lần tắt-rồi-hiện:', len(gaps), ' vùng mạnh', sum(g[0][0] == 'z' for g in gaps), ' hộp', sum(g[0][0] == 'b' for g in gaps))
from collections import Counter
R = Counter(); L = Counter()
for k, ob, a, b in gaps:
    j = a  # nến M30 'a' là nến cuối còn vẽ; snapshot j = a (vẽ cho a+1) là lúc bị tắt
    now = float(D.m30['c'][j]); u = D.U[j + 1]
    L[min(b - a - 1, 99) // 4] += 1
    if k[0] == 'b':
        d = int(D.day_of[j + 1]); lv = eng.levels(d)
        Ls = [x for x in lv if x['name'].startswith('hvn') and (x['name'], x['end'], x['lo'], x['hi']) == k[1:]]
        if not Ls: R['hộp: không còn trong danh sách mức (quá 5 phiên / tuần mới)'] += 1; continue
        x = Ls[0]
        dist = now - x['hi'] if now > x['hi'] else x['lo'] - now if now < x['lo'] else 0
        if dist > p['HVN_RADIUS'] * u: R['hộp: ngoài bán kính 8U'] += 1
        else: R['hộp: bị hộp gần hơn đẩy ra (tối đa 2/phía) hoặc trùng'] += 1
    else:
        zs = eng.zones(j)
        if 'zones_post' in cfg: zs = cfg['zones_post'](D, eng, zs, j, p)
        m = [z for z in zs if (round(z['lo'], 4), round(z['hi'], 4)) == k[1:]]
        if not m: R['vùng: không còn (U/hợp lưu/cụm đổi)'] += 1; continue
        z = m[0]
        dist = now - z['hi'] if now > z['hi'] else z['lo'] - now if now < z['lo'] else 0
        if dist > p['RADIUS'] * z['u']: R['vùng: ngoài bán kính 4U'] += 1
        else: R['vùng: SEP / tối đa 3 mỗi phía'] += 1
for r, n in R.most_common(): print('  %-60s %d' % (r, n))
print('độ dài lần tắt (nến M30, nhóm 4):', sorted(L.items()))
