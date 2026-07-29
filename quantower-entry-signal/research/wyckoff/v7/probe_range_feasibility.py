#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROBE (GD4 — chi DEM, KHONG backtest chien luoc).
================================================================================
Muc dich duy nhat: tra loi "KB3 (scalp bien<->bien trong range) co du n de ket luan?"
  A. Phan bo DO RONG cua so M1 (30/60/90/120 nen) theo "gia" -> chon nguong minw/maxw
     bang du lieu, khong boc so.
  B. Dem so RANGE hop le (>=2 lan cham MOI bien, do rong trong [minw,maxw]) tren
     dxFeed 5-7/2026 va tren toan 9 thang -> n kha dung cho KB3.
  C. Dem so phien co IB / VA doc duoc tu TPO-chart-daily.csv.
KHONG co entry/SL/TP/WR o day. Read-only.
Chay: python3 probe_range_feasibility.py
"""
import sys, csv, statistics as st
from collections import defaultdict
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_dxfeed as E

W37 = ('2026-05', '2026-06', '2026-07')


# ------------------------------------------------------------------ A. do rong cua so
def probe_width(B, lens=(30, 60, 90, 120), step=10):
    print("A. PHAN BO DO RONG CUA SO M1 (don vi 'gia'; 1 gia = 10 tick)")
    print(f"   {'L':>4} {'bo':>7} {'n':>6} {'p10':>6} {'p25':>6} {'p50':>6} {'p75':>6} {'p90':>6}")
    for L in lens:
        for tag, sel in (('5-7/26', lambda b: b['ym'] in W37), ('9 thang', lambda b: True)):
            ws = []
            for i in range(0, len(B) - L, step):
                w = B[i:i + L]
                if not sel(w[0]):
                    continue
                if any(x['since_gap'] == 0 for x in w[1:]):
                    continue                     # cua so bat qua gap phien -> bo
                ws.append(max(x['hi'] for x in w) - min(x['lo'] for x in w))
            if not ws:
                continue
            ws.sort()
            q = lambda p: ws[min(len(ws) - 1, int(len(ws) * p))]
            print(f"   {L:>4} {tag:>7} {len(ws):>6} {q(.10):>6.1f} {q(.25):>6.1f} "
                  f"{q(.50):>6.1f} {q(.75):>6.1f} {q(.90):>6.1f}")
    print()


# ------------------------------------------------------------------ B. dem range
def touches(bars, edge, tol, up, sep=3):
    """So lan CHAM RIENG BIET mot bien: nen co cuc tri trong [edge-tol, edge] (bien tren)
    hoac [edge, edge+tol] (bien duoi); 2 lan cham cach nhau >= sep nen moi tinh la 2."""
    out = []
    for k, b in enumerate(bars):
        hitv = (b['hi'] >= edge - tol) if up else (b['lo'] <= edge + tol)
        if hitv and (not out or k - out[-1] >= sep):
            out.append(k)
    return out


def scan_ranges(B, minw, maxw, form=30, maxlen=120, buf=0.2, tolf=0.15, tolmin=0.3,
                sep=3, need=2):
    """Tim range KHONG chong lap: cua so hinh thanh `form` nen -> keo dai khi close con
    trong bien (+-buf gia) -> hop le khi du `need` lan cham MOI bien va do rong in [minw,maxw].
    Chi dung nen da dong (khong nhin tuong lai trong pham vi tung range)."""
    res = []
    i, n = 0, len(B)
    while i + form < n:
        w = B[i:i + form]
        if any(x['since_gap'] == 0 for x in w[1:]):
            i += 1
            continue
        rhi = max(x['hi'] for x in w)
        rlo = min(x['lo'] for x in w)
        if not (minw <= rhi - rlo <= maxw):
            i += 1
            continue
        j = i + form
        brk = None
        while j < n and (j - i) < maxlen:
            b = B[j]
            if b['since_gap'] == 0:
                brk = 'gap'
                break
            if b['c'] > rhi + buf:
                brk = 'up'
                break
            if b['c'] < rlo - buf:
                brk = 'dn'
                break
            nhi, nlo = max(rhi, b['hi']), min(rlo, b['lo'])
            if nhi - nlo > maxw:
                brk = 'wide'
                break
            rhi, rlo = nhi, nlo
            j += 1
        if brk is None:
            brk = 'timeout'
        seg = B[i:j]
        width = rhi - rlo
        tol = max(tolmin, tolf * width)
        tu = touches(seg, rhi, tol, True, sep)
        td = touches(seg, rlo, tol, False, sep)
        if len(seg) >= form and len(tu) >= need and len(td) >= need and minw <= width <= maxw:
            # nen XAC NHAN = nen dau tien du dieu kien (2 cham moi bien) -> tu do KB3 moi duoc arm
            vk = None
            for k in range(form, len(seg) + 1):
                s2 = seg[:k]
                if (len(touches(s2, rhi, tol, True, sep)) >= need
                        and len(touches(s2, rlo, tol, False, sep)) >= need):
                    vk = k
                    break
            post = 0
            if vk is not None:
                p = seg[vk:]
                post = len(touches(p, rhi, tol, True, sep)) + len(touches(p, rlo, tol, False, sep))
            res.append(dict(i=i, j=j, ym=B[i]['ym'], bars=len(seg), width=width,
                            tu=len(tu), td=len(td), brk=brk, valid_at=vk, post=post))
            i = j                       # khong chong lap: bat dau lai tu nen pha
        else:
            i += 1
    return res


def probe_ranges(B):
    print("B. SO RANGE HOP LE (>=2 cham MOI bien, khong chong lap, cua so 30-120 nen)")
    print(f"   {'minw':>5} {'maxw':>5} | {'5-7/26':>7} {'05':>3} {'06':>3} {'07':>3} "
          f"{'cham sau XN':>11} | {'9thg':>5} {'w~':>5} {'nen~':>5} {'pha up/dn':>10}")
    best = None
    for minw, maxw in ((1.5, 4.0), (2.0, 6.0), (2.0, 8.0), (3.0, 8.0), (3.0, 12.0), (2.0, 15.0)):
        R = scan_ranges(B, minw, maxw)
        r37 = [r for r in R if r['ym'] in W37]
        bym = defaultdict(int)
        for r in r37:
            bym[r['ym']] += 1
        post = sum(r['post'] for r in r37)
        wmed = st.median([r['width'] for r in r37]) if r37 else 0
        bmed = st.median([r['bars'] for r in r37]) if r37 else 0
        up = sum(1 for r in r37 if r['brk'] == 'up')
        dn = sum(1 for r in r37 if r['brk'] == 'dn')
        print(f"   {minw:>5.1f} {maxw:>5.1f} | {len(r37):>7} {bym['2026-05']:>3} "
              f"{bym['2026-06']:>3} {bym['2026-07']:>3} {post:>11} | {len(R):>5} "
              f"{wmed:>5.1f} {bmed:>5.0f} {f'{up}/{dn}':>10}")
        if best is None or len(r37) > best[0]:
            best = (len(r37), minw, maxw, R)
    print()
    _, minw, maxw, R = best
    r37 = [r for r in R if r['ym'] in W37]
    print(f"   Chi tiet bo tot nhat cho n (minw={minw} maxw={maxw}):")
    print(f"     ket cuc range 5-7/26: " + " ".join(
        f"{k}={sum(1 for r in r37 if r['brk'] == k)}" for k in ('up', 'dn', 'timeout', 'gap', 'wide')))
    if r37:
        ws = sorted(r['width'] for r in r37)
        print(f"     do rong (gia): min={ws[0]:.1f} p25={ws[len(ws)//4]:.1f} "
              f"med={ws[len(ws)//2]:.1f} p75={ws[3*len(ws)//4]:.1f} max={ws[-1]:.1f}")
        ps = sorted(r['post'] for r in r37)
        print(f"     so cham SAU khi range xac nhan (= so lan arm KB3/range): "
              f"min={ps[0]} med={ps[len(ps)//2]} max={ps[-1]} tong={sum(ps)}")
    print()


# ------------------------------------------------------------------ C. TPO daily
def probe_tpo():
    print("C. TPO-chart-daily.csv — so PHIEN doc duoc IB / VA")
    h, rows = E.load("TPO-chart-daily.csv")
    ix = {n: i for i, n in enumerate(h)}
    need = ['IB High', 'IB Low', 'VAH', 'VAL', 'POC', 'TPO']
    miss = [c for c in need if c not in ix]
    if miss:
        print(f"   THIEU cot: {miss}")
        return
    days = {}
    for x in rows:
        d = x[ix['DateTime']].split()[0]
        v = {c: E.fn(x[ix[c]]) for c in need}
        rec = days.setdefault(d, dict(n=0, ib=0, va=0, tpo=set()))
        rec['n'] += 1
        if v['IB High'] > 0 and v['IB Low'] > 0 and v['IB High'] > v['IB Low']:
            rec['ib'] += 1
        if v['VAH'] > 0 and v['VAL'] > 0 and v['VAH'] > v['VAL']:
            rec['va'] += 1
        rec['tpo'].add(v['TPO'])
    ib = sum(1 for d in days.values() if d['ib'] > 0)
    va = sum(1 for d in days.values() if d['va'] > 0)
    ks = sorted(days)
    print(f"   n dong={len(rows)}  so ngay phan biet={len(days)}  {ks[0]} -> {ks[-1]}")
    print(f"   ngay co IB doc duoc={ib}  ngay co VA doc duoc={va}  "
          f"=> so cap (D-1 -> D) dung duoc cho bias = {min(ib, va) - 1}")
    print()


if __name__ == '__main__':
    B = E.load_m1()
    print(f"dxFeed M1 = {len(B)} nen | {B[0]['dt']} -> {B[-1]['dt']} (UTC)\n")
    probe_width(B)
    probe_ranges(B)
    probe_tpo()
