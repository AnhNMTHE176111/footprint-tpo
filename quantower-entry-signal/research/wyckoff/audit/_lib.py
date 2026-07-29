#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_lib.py — ha tang DUNG RIENG cho pha AUDIT (khong sua code san pham).

Cung cap:
  raw_rows()          : doc CSV dxFeed 1 lan, tra list dict THO (chi dt/o/hi/lo/c/v) da sort.
  derive(rows)        : ap DUNG y het vong lap dan xuat cua entry_dxfeed.load_m1() len mot
                        DANH SACH BAT KY (co the la tien to bi cat) -> dung cho phep kiem CAT CHUOI.
  months_patch(ms)    : doi cbr_v6.MONTHS + report.MONTHS + imp_reversal_sweep window sang cua so khac
                        (CAN cho OOS — cbr_v6.post() hardcode 5-7/2026).
  line2(...)          : bang mot dong, thang tuy y (khong hardcode 3 thang nhu report.line).
  apply_cost(S, tick) : tru chi phi co dinh (tick) moi lenh, tinh lai R theo risk_t.
"""
import sys, os, statistics as st
from collections import defaultdict

R = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research"
sys.path.insert(0, R)
sys.path.insert(0, os.path.join(R, "wyckoff"))
sys.path.insert(0, os.path.join(R, "wyckoff", "v7"))

import entry_dxfeed as E
import cbr_v6 as V6

TICK = E.TICK

_RAW = None


def raw_rows():
    """Doc DXFILE 1 lan -> list dict tho (dt,o,hi,lo,c,v), sort theo dt. KHONG dan xuat gi."""
    global _RAW
    if _RAW is None:
        h, rows = E.load(E.DXFILE, sep=';')
        ix = {n: i for i, n in enumerate(h)}
        iTL, iO, iH, iL, iC, iV = (ix['Time left'], ix['Open'], ix['High'],
                                    ix['Low'], ix['Close'], ix['Volume'])
        Bs = [dict(dt=E.pdt_dx(x[iTL]), o=E.fn(x[iO]), hi=E.fn(x[iH]), lo=E.fn(x[iL]),
                   c=E.fn(x[iC]), v=E.fn(x[iV])) for x in rows]
        Bs.sort(key=lambda b: b['dt'])
        _RAW = Bs
    return _RAW


def derive(src):
    """Ban COPY 1-1 vong lap dan xuat cua entry_dxfeed.load_m1() (dong 98-118) + trend proxy.
    Chay duoc tren TIEN TO bat ky cua chuoi -> cho phep so 'tinh tren chuoi cat' vs 'chuoi day du'.
    (Doi chieu bang assert voi E.load_m1() trong a1_truncate.py truoc khi dung lam bang chung.)"""
    B = [dict(b) for b in src]
    csum_pv = csum_v = 0.0
    for i, b in enumerate(B):
        gap = i > 0 and (b['dt'] - B[i - 1]['dt']).total_seconds() / 60 > 30
        if gap:
            csum_pv = csum_v = 0.0
        tp = (b['hi'] + b['lo'] + b['c']) / 3.0
        csum_pv += tp * b['v']; csum_v += b['v']
        b['vwap'] = csum_pv / csum_v if csum_v > 0 else b['c']
        win = [B[j]['v'] for j in range(max(0, i - E.VSA_MA + 1), i + 1)]
        sma = sum(win) / len(win) if win else b['v']
        b['vma'] = sma; b['vratio'] = b['v'] / sma if sma > 1e-9 else 0.0
        rng = b['hi'] - b['lo']; b['rng'] = rng; b['body'] = abs(b['c'] - b['o'])
        b['uw'] = b['hi'] - max(b['o'], b['c']); b['lw'] = min(b['o'], b['c']) - b['lo']
        b['brat'] = b['body'] / rng if rng > 0 else 0.0
        b['cpos'] = (b['c'] - b['lo']) / rng if rng > 0 else 0.5
        b['up'] = b['c'] > b['o']; b['dn'] = b['c'] < b['o']
        b['since_gap'] = 0 if gap else (B[i - 1]['since_gap'] + 1 if i > 0 else 999)
        b['ym'] = b['dt'].strftime('%Y-%m')
    for i, b in enumerate(B):
        j = i - E.BASE['TREND_LB']
        b['trend'] = (1 if b['c'] > B[j]['c'] else -1 if b['c'] < B[j]['c'] else 0) if j >= 0 else 0
    return B


def months_patch(ms):
    """cbr_v6.post() loc `s['ym'] in cbr_v6.MONTHS` (hardcode 5-7/2026) => de chay cua so KHAC
    (OOS) buoc phai doi hang so nay tai runtime. KHONG sua file san pham."""
    import report
    V6.MONTHS = tuple(ms)
    report.MONTHS = tuple(ms)
    return tuple(ms)


def mdd(rs):
    eq = pk = worst = 0.0
    for r in rs:
        eq += r; pk = max(pk, eq); worst = max(worst, pk - eq)
    return worst


def line2(tag, S, months, ret=False):
    """Nhu report.line() nhung thang truyen vao (report.line hardcode 3 thang 5-7/2026)."""
    if not S:
        print(f"  {tag:<40} n=  0   (khong co lenh)")
        return None
    rs = [s['r'] for s in S]
    w = sum(1 for r in rs if r > 0)
    bym = defaultdict(float)
    nym = defaultdict(int)
    for s in S:
        bym[s['ym']] += s['r']; nym[s['ym']] += 1
    mm = " ".join(f"{m[2:]}:{bym.get(m, 0.0):+5.1f}(n{nym.get(m,0)})" for m in months)
    allpos = all(bym.get(m, 0) > 0 for m in months)
    n, wr, tot, ev = len(S), 100 * w / len(S), sum(rs), sum(rs) / len(S)
    print(f"  {tag:<40} n={n:3d} WR={wr:5.1f}% tong={tot:+7.1f}R EV={ev:+.3f} "
          f"MDD={mdd(rs):5.1f}R | {mm} {'OK' if allpos else 'x'}")
    d = dict(n=n, wr=wr, tot=tot, ev=ev, mdd=mdd(rs), allpos=allpos, bym=dict(bym), nym=dict(nym))
    return d


def apply_cost(S, cost_ticks):
    """Tru chi phi CO DINH `cost_ticks` tick moi lenh (spread+slippage), quy ve don vi R cua
    CHINH lenh do: dR = cost_ticks / risk_t  (risk_t = |entry-SL| bang tick).
    Tra ve list moi voi 'r' da tru phi. KHONG doi gi khac."""
    out = []
    for s in S:
        s2 = dict(s)
        rt = s.get('risk_t') or 0.0
        s2['r'] = s['r'] - (cost_ticks / rt if rt > 0 else 0.0)
        out.append(s2)
    return out


def ev(S):
    return (sum(s['r'] for s in S) / len(S)) if S else 0.0
