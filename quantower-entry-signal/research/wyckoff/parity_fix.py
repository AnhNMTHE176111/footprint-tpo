#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIEM PARITY — sua 2 lo hong phuong phap trong cbr_v6:
  (1) b['trend'] cua entry_dxfeed dung tol=0, C# dung TrendTolPts=1.0 gia -> tinh lai.
  (2) avg_vma lay trung binh TOAN CHUOI = LOOK-AHEAD. C# dung TB cuon 1000 nen TRUOC
      (khong gom nen nay) -> tinh lai b['liqratio'] cuon, roi LiqOk = liqratio>=0.75.
Neu ket luan v6 doi dau sau khi sua => plan phai viet lai."""
import sys, statistics as st
from collections import defaultdict, deque
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
sys.path.insert(0, ".")
import entry_dxfeed as E, cbr_v6 as V
from round3_v6 import has_counter_sweep

TICK = V.TICK
B = E.load_m1(); vf = E.calc_volfloor(B); E.VOLFLOOR_AUTO = vf

# (1) trend voi tol 1.0 gia (khop RunnerSignal.cs:450-451)
LB, TOL = 480, 1.0
for i, b in enumerate(B):
    if i >= LB:
        d = b['c'] - B[i - LB]['c']
        b['trend'] = 1 if d > TOL else (-1 if d < -TOL else 0)
    else:
        b['trend'] = 0

# (2) liqratio cuon 1000 nen TRUOC (khop RunnerSignal.cs:427,441-445)
W = 1000
q = deque(); s = 0.0
for b in B:
    mean = (s / len(q)) if q else b['v']
    b['liqratio'] = (b['vma'] / mean) if mean > 1e-9 else 1.0
    q.append(b['v']); s += b['v']
    if len(q) > W: s -= q.popleft()

# vá LiqOk: dung liqratio cuon thay vi vma >= k*avg_vma toan chuoi
_run = V.run
def run_fixed(Bx, C, vfx, _ignored):
    class _C(dict):
        pass
    return _run(Bx, C, vfx, None)
# thay truc tiep trong V.run: LIQ dung b['liqratio']
import re
src_note = "LIQ dung b['liqratio'] >= LIQ_K"
def patched_run(Bx, C, vfx, avg_unused):
    raw = []; N = len(Bx)
    for i in range(E.VSA_MA + 2, N):
        b = Bx[i]
        if not V._gate(b, vfx): continue
        win = Bx[i - C['RANGE_LEN']:i]
        rhi = max(x['hi'] for x in win); rlo = min(x['lo'] for x in win)
        span = (rhi - rlo) / TICK
        if span > C['RMAX'] or span < C['RMIN']: continue
        up = b['c'] > rhi + C['BUF']*TICK and b['vratio'] >= C['BVSA'] and b['brat'] >= C['BBODY'] and b['up']
        dn = b['c'] < rlo - C['BUF']*TICK and b['vratio'] >= C['BVSA'] and b['brat'] >= C['BBODY'] and b['dn']
        if not (up or dn): continue
        if C['PHASE_C'] and not V._phase_c(Bx, i, up, C): continue
        side = 'LONG' if up else 'SHORT'; edge = rhi if up else rlo
        peak = b['hi'] if up else b['lo']; since = i
        for j in range(i+1, min(N, i+1+C['WAIT'])):
            bj = Bx[j]
            if not V._gate(bj, vfx): break
            if (bj['c'] < edge - C['HOLD_TOL']*TICK) if up else (bj['c'] > edge + C['HOLD_TOL']*TICK): break
            pseg = Bx[since+1:j+1]
            if pseg:
                pext = min(x['lo'] for x in pseg) if up else max(x['hi'] for x in pseg)
                leg = (peak-edge) if up else (edge-peak)
                depth = (peak-pext) if up else (pext-peak)
                retr = depth/leg if leg > 0 else 0
                held = (pext >= edge - C['HOLD_TOL']*TICK) if up else (pext <= edge + C['HOLD_TOL']*TICK)
                resume = ((bj['c'] > Bx[j-1]['hi'] and bj['up']) if up else (bj['c'] < Bx[j-1]['lo'] and bj['dn'])) and bj['brat'] >= C['RBODY']
                if j >= since+2 and C['PMIN'] <= retr <= C['PMAX'] and held and resume:
                    if C['LEGQ'] and V._leg_quality(Bx, i, since, up, C) < C['LEGQ_MIN']: break
                    entry = bj['c']
                    anchor = pext
                    sl = anchor - C['BUF']*TICK if up else anchor + C['BUF']*TICK
                    risk = (entry-sl)/TICK if up else (sl-entry)/TICK
                    if risk < C['FLOOR']:
                        sl = entry - C['FLOOR']*TICK if up else entry + C['FLOOR']*TICK; risk = C['FLOOR']
                    if risk > C['CAP']: break
                    # ---- GATE tai NEN VAO (khop C#:570) : trend tol1.0 + vwap + liq CUON ----
                    sd = 1 if up else -1
                    okT = (not C['TREND']) or bj['trend'] == sd
                    okV = (not C['VWAP']) or (bj['c'] >= bj['vwap'] if up else bj['c'] <= bj['vwap'])
                    okL = (not C['LIQ']) or bj['liqratio'] >= C['LIQ_K']
                    if okT and okV and okL:
                        raw.append(dict(i=j, dt=bj['dt'], ym=bj['ym'], side=side, entry=entry, sl=sl,
                                        risk_t=risk, retr=retr, span=span, brk_i=i, peak_i=since,
                                        brk_vsa=b['vratio'], hour=bj['dt'].hour))
                    break
            if (bj['hi'] > peak) if up else (bj['lo'] < peak):
                peak = bj['hi'] if up else bj['lo']; since = j
    return raw
V.run = patched_run

def line(tag, S):
    if not S: print(f"  {tag:<44} n=0"); return
    rs=[s['r'] for s in S]; w=sum(1 for r in rs if r>0)
    bym=defaultdict(float)
    for s in S: bym[s['ym']]+=s['r']
    mm=" ".join(f"{m[-2:]}:{bym[m]:+5.1f}" for m in V.MONTHS if m in bym)
    ok=all(bym.get(m,0)>0 for m in V.MONTHS)
    cut=sorted(s['dt'] for s in S)[len(S)//2]
    h1=[s['r'] for s in S if s['dt']<cut]; h2=[s['r'] for s in S if s['dt']>=cut]
    print(f"  {tag:<44} n={len(S):3d} WR={100*w/len(S):5.1f}% tong={sum(rs):+7.1f}R EV={sum(rs)/len(S):+.3f} "
          f"MDD={V.mdd(rs):5.1f} | {mm} {'✓' if ok else '✗'} | nua {sum(h1):+.0f}/{sum(h2):+.0f}")

print("="*126)
print("SAU KHI SUA PARITY (trend tol=1.0 gia, thanh khoan CUON 1000 nen — HET look-ahead)")
print(" [A] v5 baseline, cac gia thuyet khung gio chet:")
line("khong cat gio",              V.scan(B, V.cfg(DEAD=False), vf, None))
line("cat UTC 19-01 (C# dang ship)", V.scan(B, V.cfg(DEAD=True, DEAD_FROM=19, DEAD_TO=1), vf, None))
line("cat UTC 02-08 (dung)",       V.scan(B, V.cfg(DEAD=True), vf, None))
print(" [B] v6 = sach(look20 w5) + retrace60-100:")
V._phase_c = lambda Bx,i,up,C: not has_counter_sweep(Bx,i,up,20,5,0.50)
for rr in (3.0, 4.0, 5.0):
    line(f"v6 RR{rr} + cat UTC 02-08", V.scan(B, V.cfg(PHASE_C=True, PMAX=1.00, RR=rr), vf, None))
line("v6 RR4 + TAT thanh khoan",  V.scan(B, V.cfg(PHASE_C=True, PMAX=1.00, RR=4.0, LIQ=False), vf, None))
line("v6 RR4 + TAT loc gio",      V.scan(B, V.cfg(PHASE_C=True, PMAX=1.00, RR=4.0, DEAD=False), vf, None))
print(" [C] chia 2 nhom roi nhau (bang chung bo loc 'sach'):")
line("nhom SACH (RR3)",           V.scan(B, V.cfg(PHASE_C=True), vf, None))
V._phase_c = lambda Bx,i,up,C: has_counter_sweep(Bx,i,up,20,5,0.50)
line("nhom CO QUET NGUOC (RR3)",  V.scan(B, V.cfg(PHASE_C=True), vf, None))
print("="*126)
