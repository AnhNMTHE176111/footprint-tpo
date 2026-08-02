#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBR_ENTRY_VSA — kiem tra to cao cua nguoi hoc (2026-08-02):
  "runner signal vao lenh o rat nhieu nen co VSA < high, rat nhieu lenh SL vi cac entry nay".

Doc code truoc khi do:
  RunnerSignal.cs / WyckoffRunner.cs, nhanh CBR:
    - NEN PHA (bar i)  : BAT BUOC `b.Vratio >= BreakVsa (2.0)`   -> luon la nen manh
    - NEN VAO (bar j)  : chi doi `bj.Brat >= ResumeBody (0.35)` + Gate(vol>=VolFloor).
                         KHONG co MOT dieu kien VSA nao.
    - `AddSig(raw, j, ..., b.Vratio, ...)`  <-- truyen VSA cua NEN PHA nhung gan cho tin hieu
                         o NEN VAO j. => cot "VSA" trong CSV/panel/Telegram la cua NEN PHA,
                         KHONG phai nen vao lenh. Vi vay tren CSV thay toan 2.2-5.6 "tim",
                         con tren CHART nen vao lenh lai nho.
  => to cao dung ca 2 mat: (1) thieu gate VSA o nen vao, (2) so VSA bao ra sai cho.

File nay do: phan bo VSA nen vao, WR/EV theo bucket, va A/B khi them gate.
"""
import sys, os, statistics as st
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cbr_v6 as V6
import entry_dxfeed as E

TICK = V6.TICK
MONTHS = V6.MONTHS


def run_rvsa(B, C, vf, rvsa=0.0, mode='abandon'):
    """Ban sao V6.run() + gate VSA tai NEN VAO.
    mode='abandon': nen hoi khong du VSA -> bo luon leg (khop cach C# dang `break`).
    mode='wait'   : bo qua nen do, tiep tuc cho nen hoi khac trong cua so WAIT.
    """
    raw = []; N = len(B)
    for i in range(E.VSA_MA + 2, N):
        b = B[i]
        if not V6._gate(b, vf): continue
        win = B[i - C['RANGE_LEN']:i]
        rhi = max(x['hi'] for x in win); rlo = min(x['lo'] for x in win)
        span = (rhi - rlo) / TICK
        if span > C['RMAX'] or span < C['RMIN']: continue
        up = b['c'] > rhi + C['BUF'] * TICK and b['vratio'] >= C['BVSA'] and b['brat'] >= C['BBODY'] and b['up']
        dn = b['c'] < rlo - C['BUF'] * TICK and b['vratio'] >= C['BVSA'] and b['brat'] >= C['BBODY'] and b['dn']
        if not (up or dn): continue
        if C['CLEAN'] and V6.counter_sweep(B, i, up, C['CL_LOOK'], C['CL_W'], C['CL_CLOSE']): continue

        side = 'LONG' if up else 'SHORT'; edge = rhi if up else rlo
        peak = b['hi'] if up else b['lo']; since = i
        for j in range(i + 1, min(N, i + 1 + C['WAIT'])):
            bj = B[j]
            if not V6._gate(bj, vf): break
            if (bj['c'] < edge - C['HOLD_TOL'] * TICK) if up else (bj['c'] > edge + C['HOLD_TOL'] * TICK): break
            pseg = B[since + 1:j + 1]
            if pseg:
                pext = min(x['lo'] for x in pseg) if up else max(x['hi'] for x in pseg)
                leg = (peak - edge) if up else (edge - peak)
                depth = (peak - pext) if up else (pext - peak)
                retr = depth / leg if leg > 0 else 0
                held = (pext >= edge - C['HOLD_TOL'] * TICK) if up else (pext <= edge + C['HOLD_TOL'] * TICK)
                resume = ((bj['c'] > B[j - 1]['hi'] and bj['up']) if up
                          else (bj['c'] < B[j - 1]['lo'] and bj['dn'])) and bj['brat'] >= C['RBODY']
                if j >= since + 2 and C['PMIN'] <= retr <= C['PMAX'] and held and resume:
                    # ===== GATE MOI: VSA cua NEN VAO =====
                    if rvsa > 0 and bj['vratio'] < rvsa:
                        if mode == 'abandon': break
                        else:
                            if (bj['hi'] > peak) if up else (bj['lo'] < peak):
                                peak = bj['hi'] if up else bj['lo']; since = j
                            continue
                    entry = bj['c']
                    anchor = pext
                    sl = anchor - C['BUF'] * TICK if up else anchor + C['BUF'] * TICK
                    risk = (entry - sl) / TICK if up else (sl - entry) / TICK
                    if risk < C['FLOOR']:
                        sl = entry - C['FLOOR'] * TICK if up else entry + C['FLOOR'] * TICK
                        risk = C['FLOOR']
                    if risk > C['CAP']: break
                    sd = 1 if up else -1
                    okT = (not C['TREND']) or bj['trend'] == sd
                    okV = (not C['VWAP']) or (bj['c'] >= bj['vwap'] if up else bj['c'] <= bj['vwap'])
                    okL = (not C['LIQ']) or bj['liqratio'] >= C['LIQ_K']
                    if okT and okV and okL:
                        raw.append(dict(i=j, dt=bj['dt'], ym=bj['ym'], side=side, entry=entry, sl=sl,
                                        risk_t=risk, retr=retr, span=span, brk_i=i, peak_i=since,
                                        brk_vsa=b['vratio'], ent_vsa=bj['vratio'],
                                        ent_brat=bj['brat'], hour=bj['dt'].hour))
                    break
            if (bj['hi'] > peak) if up else (bj['lo'] < peak):
                peak = bj['hi'] if up else bj['lo']; since = j
    return raw


def scan(B, C, vf, rvsa=0.0, mode='abandon'):
    return V6.evaluate(B, V6.post(V6.cooldown(V6.dedup(run_rvsa(B, C, vf, rvsa, mode)), C['COOL']), C), C)


def main():
    B = E.load_m1()
    vf = E.calc_volfloor(B); E.VOLFLOOR_AUTO = vf
    V6.prepare(B)
    print(f"M1={len(B)} bars  volfloor={vf}   (BreakVsa=2.0 cho NEN PHA, nen VAO khong co gate)")
    C = V6.cfg()
    S0 = scan(B, C, vf, 0.0)

    print("=" * 118)
    print("BASELINE — CBR v5 dang ship")
    V6.line("v5 baseline RR3", S0)

    # ---------- (1) NEN VAO LENH manh hay yeu? ----------
    print("\n" + "=" * 118)
    print("(1) PHAN BO VSA cua NEN VAO LENH (so nguoi hoc nhin thay tren chart)")
    ev = sorted(s['ent_vsa'] for s in S0)
    bv = sorted(s['brk_vsa'] for s in S0)
    def pct(a, p): return a[min(len(a) - 1, int(len(a) * p))]
    print(f"  NEN VAO : trung vi {st.median(ev):.2f}x   p10 {pct(ev,.10):.2f}  p90 {pct(ev,.90):.2f}")
    print(f"  NEN PHA : trung vi {st.median(bv):.2f}x   p10 {pct(bv,.10):.2f}  p90 {pct(bv,.90):.2f}   (day la so BAO RA CSV)")
    for th, name in ((1.2, "high"), (2.2, "climax")):
        n = sum(1 for x in ev if x < th)
        print(f"  -> nen vao co VSA < {th} ({name}): {n}/{len(ev)} = {n/len(ev)*100:.0f}%")

    # ---------- (2) VSA nen vao co du bao ket qua khong? ----------
    print("\n" + "=" * 118)
    print("(2) KET QUA THEO BUCKET VSA cua NEN VAO")
    buckets = [(0, 0.8), (0.8, 1.0), (1.0, 1.2), (1.2, 1.5), (1.5, 2.2), (2.2, 99)]
    for lo, hi in buckets:
        g = [s for s in S0 if lo <= s['ent_vsa'] < hi]
        if not g: continue
        rs = [s['r'] for s in g]; w = sum(1 for r in rs if r > 0)
        print(f"  VSA nen vao [{lo:4.1f},{hi:4.1f}) : n={len(g):3d}  WR {100*w/len(g):5.1f}%  "
              f"tong {sum(rs):+7.1f}R  EV {sum(rs)/len(g):+.3f}")

    # ---------- (3) A/B them gate ----------
    print("\n" + "=" * 118)
    print("(3) A/B — THEM GATE VSA o NEN VAO")
    print("  che do ABANDON (nen hoi yeu -> bo luon leg, giong cach code dang `break`)")
    for th in (0.0, 0.8, 1.0, 1.1, 1.2, 1.3, 1.5, 1.8, 2.2):
        V6.line(f"ResumeVsa >= {th:.1f}" if th else "khong gate (v5)", scan(B, C, vf, th, 'abandon'))
    print("\n  che do WAIT (bo qua nen yeu, CHO nen hoi khac trong cua so 12 nen)")
    for th in (0.8, 1.0, 1.2, 1.5, 1.8, 2.2):
        V6.line(f"ResumeVsa >= {th:.1f} (cho tiep)", scan(B, C, vf, th, 'wait'))

    # ---------- (4) doi chung: gate bang THAN nen thay vi VSA ----------
    print("\n" + "=" * 118)
    print("(4) DOI CHUNG — VSA co that su la thu co tac dung, hay chi la 'bo bot lenh'?")
    print("  so sanh voi viec siet THAN nen vao (ResumeBody) de cat cung so luong lenh")
    for rb in (0.35, 0.45, 0.55, 0.65):
        V6.line(f"ResumeBody >= {rb:.2f}", scan(B, V6.cfg(RBODY=rb), vf, 0.0))


if __name__ == '__main__':
    main()
