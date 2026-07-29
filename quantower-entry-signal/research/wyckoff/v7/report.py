#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""report.py — in bang theo DUNG dinh dang co dinh (khop BASELINE.md/final_table.py) +
partition + sweep. Khong tinh toan chien luoc, chi format + vai phep tinh thong ke don gian."""
import statistics as st
from collections import defaultdict

MONTHS = ('2026-05', '2026-06', '2026-07')


def mdd(rs):
    eq = pk = worst = 0.0
    for r in rs:
        eq += r; pk = max(pk, eq); worst = max(worst, pk - eq)
    return worst


def _half_split(S):
    if not S:
        return [], []
    cut = sorted(s['dt'] for s in S)[len(S) // 2]
    return [s for s in S if s['dt'] < cut], [s for s in S if s['dt'] >= cut]


def line(tag, S, months=MONTHS, extra=""):
    """In 1 dong DUNG dinh dang co dinh:
    tag   n=NNN WR=NN.N% tong=+NN.NR EV=+N.NNN MDD=NN.NR | 05:+N.N 06:+N.N 07:+N.N v/x | nua1 +N.NR(nNN) nua2 +N.NR(nNN)
    Tra ve dict so lieu (de dung lai cho partition/pass-kill), hoac None neu S rong."""
    if not S:
        print(f"  {tag:<34} n=  0  (khong co lenh)")
        return None
    rs = [s['r'] for s in S]
    w = sum(1 for r in rs if r > 0)
    bym = defaultdict(float)
    for s in S:
        bym[s['ym']] += s['r']
    mm = " ".join(f"{m[-2:]}:{bym.get(m, 0.0):+5.1f}" for m in months)
    allpos = all(bym.get(m, 0) > 0 for m in months)
    h1, h2 = _half_split(S)
    n, wr, tot, ev, md = len(S), 100 * w / len(S), sum(rs), sum(rs) / len(S), mdd(rs)
    print(f"  {tag:<34} n={n:3d} WR={wr:5.1f}% tong={tot:+7.1f}R EV={ev:+.3f} MDD={md:5.1f}R "
          f"| {mm} {'✓' if allpos else '✗'} "
          f"| nua1 {sum(x['r'] for x in h1):+6.1f}R(n{len(h1):2d}) nua2 {sum(x['r'] for x in h2):+6.1f}R(n{len(h2):2d}) {extra}")
    return dict(n=n, wr=wr, tot=tot, ev=ev, mdd=md, allpos=allpos, bym=dict(bym),
                half1=sum(x['r'] for x in h1), half1_n=len(h1),
                half2=sum(x['r'] for x in h2), half2_n=len(h2))


def partition(tag_keep, S_keep, tag_drop, S_drop, months=MONTHS, min_n_drop=10, min_ev_gap=0.30):
    """In 2 dong (nhom GIU + nhom BI LOAI) va phan xu PASS/KILL cua BAN THAN bo loc theo
    quy tac chung (SPEC §4.9/§5.9/§6.9): can EV_giu - EV_loai >= min_ev_gap VA n_loai >= min_n_drop."""
    print(f"  -- partition: {tag_keep} vs {tag_drop} --")
    dk = line(tag_keep, S_keep, months)
    dd = line(tag_drop, S_drop, months)
    if dk is None or dd is None or dd['n'] < min_n_drop:
        verdict = f"KHONG KET LUAN (n_loai={dd['n'] if dd else 0} < {min_n_drop})"
    else:
        gap = dk['ev'] - dd['ev']
        verdict = f"PASS (EV_giu-EV_loai={gap:+.3f} >= {min_ev_gap})" if gap >= min_ev_gap \
            else f"KILL — bo loc la NHIEU (EV_giu-EV_loai={gap:+.3f} < {min_ev_gap})"
    print(f"     => {verdict}")
    return dk, dd, verdict


def sweep(label, rows):
    """rows: list[(tag, statsdict_or_None)] da tinh san bang line(). In cao nguyen check don gian:
    canh bao neu chi 1 diem dep con lang gieng am/kem han."""
    print(f"  -- sweep: {label} --")
    evs = [(t, d['ev'] if d else None) for t, d in rows]
    for t, e in evs:
        print(f"     {t:<28} EV={'n/a' if e is None else f'{e:+.3f}'}")
    vals = [e for _, e in evs if e is not None]
    if len(vals) >= 3:
        best = max(vals)
        neigh_ok = sum(1 for v in vals if v >= 0.6 * best) - 1  # tru chinh no
        if neigh_ok == 0:
            print("     ⚠ CHI 1 diem dep, lang gieng khong dat >=60% EV cua no -> nghi ngo overfit")
        else:
            print(f"     -> {neigh_ok} cau hinh khac dat >=60% EV cua diem tot nhat (co cao nguyen)")
