#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vong15.py — các vòng đo cụm khối lượng (profile cố định ngày/tuần) kiểu Trader Dale, đơn vị M15.
   python vong15.py <vòng>"""
import sys
import vc

R = {}
def vong(k):
    def deco(f): R[k] = f; return f
    return deco

@vong('1')
def v1():
    vc.go('V1 cụm hôm qua · mọi lần chạm', MODE='all')
    vc.go('V1 cụm hôm qua · mọi lần chạm · TOP1', MODE='all', TOP=1)

@vong('2')
def v2():
    vc.go('V2 cụm hôm qua · Dale X3 K4 · lần đầu')
    vc.go('V2 cụm hôm qua · rời đi bất kỳ (X1.25 K∞) · lần đầu', X=1.25, K=10000)

@vong('3')
def v3():
    for X in (2, 3, 4, 5):
        for K in (2, 4, 8):
            vc.go('V3 X%g K%d' % (X, K), X=X, K=K)

@vong('4')
def v4():
    for fr in (0.5, 0.7, 0.85):
        vc.go('V4 FRAC %.2f' % fr, FRAC=fr)
    vc.go('V4 chỉ đường đỉnh ±0,1U', LINE=True)
    for r in (1.2, 2.0, 2.5):
        vc.go('V4 RATIO %.1f' % r, RATIO=r)
    for t in (1, 2, 5):
        vc.go('V4 TOP %d' % t, TOP=t)

@vong('5')
def v5():
    vc.go('V5 chỉ tuần trước · mọi lần chạm', LBD=0, WEEK=True, MODE='all')
    vc.go('V5 chỉ tuần trước · Dale', LBD=0, WEEK=True)
    vc.go('V5 hôm qua + tuần · Dale', WEEK=True)

@vong('6')
def v6():
    for lb in (1, 3, 5):
        _, dfs = vc.go('V6 gộp %d ngày + tuần · Dale' % lb, LBD=lb, WEEK=True, MERGE=True)
        for tg in ('hl1', 'hl1w', 'hl2', 'hl2w', 'hl3', 'hl3w'):
            vc.line('  · %s' % tg, {s: (x[x.tag == tg] if len(x) else x) for s, x in dfs.items()})
    _, dfs = vc.go('V6 gộp 3 ngày + tuần · mọi lần chạm', LBD=3, WEEK=True, MERGE=True, MODE='all')
    for tg in ('hl1', 'hl1w', 'hl2', 'hl2w', 'hl3', 'hl3w'):
        vc.line('  · %s' % tg, {s: (x[x.tag == tg] if len(x) else x) for s, x in dfs.items()})

@vong('2b')
def v2b():
    for lb in (3, 5):
        vc.go('V2b cụm %d ngày (riêng) · mọi lần chạm' % lb, LBD=lb, MODE='all')
        vc.go('V2b cụm %d ngày (riêng) · rời đi bất kỳ · lần đầu' % lb, LBD=lb, X=1.25, K=10000)
        for X, K in ((3, 4), (3, 8), (4, 8), (5, 8)):
            vc.go('V2b cụm %d ngày · Dale X%g K%d' % (lb, X, K), LBD=lb, X=X, K=K)

BASE = dict(LBD=3, X=3, K=4)

@vong('4b')
def v4b():
    vc.go('V4 nền: 3 ngày · X3 K4 · FRAC 0,70', **BASE)
    for fr in (0.5, 0.85):
        vc.go('V4 FRAC %.2f' % fr, **dict(BASE, FRAC=fr))
    vc.go('V4 chỉ đường đỉnh ±0,1U', **dict(BASE, LINE=True))
    for r in (1.2, 2.0, 2.5):
        vc.go('V4 RATIO %.1f' % r, **dict(BASE, RATIO=r))
    for t in (1, 2, 5):
        vc.go('V4 TOP %d' % t, **dict(BASE, TOP=t))

@vong('5b')
def v5b():
    vc.go('V5 chỉ tuần trước · mọi lần chạm', LBD=0, WEEK=True, MODE='all')
    vc.go('V5 chỉ tuần trước · Dale X3 K4', LBD=0, WEEK=True)
    vc.go('V5 chỉ tuần trước · Dale X4 K8', LBD=0, WEEK=True, X=4, K=8)
    vc.go('V5 3 ngày + tuần (riêng) · Dale X3 K4', **dict(BASE, WEEK=True))

B2 = dict(LBD=3, X=3, K=4, TOP=2)
TAGS = ('hl1', 'hl1w', 'hl2', 'hl2w', 'hl3', 'hl3w')

def by_tag(dfs):
    for tg in TAGS:
        sub = {s: x[x.tag == tg] for s, x in dfs.items() if len(x)}
        if sum(len(x) for x in sub.values()): vc.line('  · %s' % tg, sub)

@vong('6b')
def v6b():
    vc.go('V6 nền: 3 ngày riêng · TOP2', **B2)
    for lb in (2, 3, 5):
        _, dfs = vc.go('V6 gộp %d ngày · TOP2' % lb, **dict(B2, LBD=lb, MERGE=True)); by_tag(dfs)
    _, dfs = vc.go('V6 gộp 3 ngày + tuần · TOP2', **dict(B2, WEEK=True, MERGE=True)); by_tag(dfs)
    _, dfs = vc.go('V6 gộp 3 ngày · mọi lần chạm', **dict(B2, MERGE=True, MODE='all')); by_tag(dfs)

@vong('7')
def v7():
    for pad in (0.0, 0.1, 0.2, 0.3):
        vc.go('V7 nới mỗi mép %.1f U15' % pad, **dict(B2, PAD=pad))

@vong('8')
def v8():
    for b in (0.5, 1.0, 1.5, 2.0):
        vc.go('V8 bật %.1f U15' % b, **dict(B2, B=b))

@vong('9')
def v9():
    _, dfs = vc.go('V9 lần chạm 1–3 sau cú rời đi', **dict(B2, NT=3))
    for k in (1, 2, 3):
        vc.line('  · lần %d' % k, {s: x[x.nt == k] for s, x in dfs.items() if len(x)})

if __name__ == '__main__':
    print(vc.HDR)
    for k in sys.argv[1:]: R[k]()

