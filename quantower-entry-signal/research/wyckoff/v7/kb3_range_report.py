#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kb3_range_report.py — KB3 Buoc 1: thong ke phat hien range + kiem chung bang mat + ty le xoay
bien nen. Dung LAI features.range_struct_scan (ha tang GD6 dung chung KB1/KB3, SPEC §4.3) —
KHONG viet lai state machine (da doi chieu voi probe o RESULTS_KB12.md: n=74 vs 322, lech 77%,
KHONG phai bug — xem RESULTS_KB12.md muc 5/8 va RESULTS_KB3.md muc 1).
"""
import sys, os, random, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_dxfeed as E
import features

W37 = ('2026-05', '2026-06', '2026-07')
IMG_DIR = os.path.join(HERE, '..', 'img')


def episodes_from_states(states, valids):
    """Gom cac nen states[i] theo 'i0' (rieng biet moi instance range) -> episode: i0, end_bar,
    rhi/rlo CUOI CUNG cua chinh instance do, bars. Chi giu episode nao TUNG dat VALID (co trong
    valids)."""
    last = {}   # i0 -> dict(end_bar, rhi, rlo, state)
    for i, s in enumerate(states):
        if s is None:
            continue
        i0 = s['i0']
        last[i0] = dict(end_bar=i, rhi=s['rhi'], rlo=s['rlo'], state=s['state'])
    by_i0 = {}
    for v in valids:
        if v['i0'] not in by_i0:
            by_i0[v['i0']] = v['i']     # valid_bar dau tien cua instance nay
    out = []
    for i0, valid_bar in by_i0.items():
        L = last.get(i0)
        if L is None:
            continue
        out.append(dict(i0=i0, valid_bar=valid_bar, end_bar=L['end_bar'],
                         bars=L['end_bar'] - i0 + 1, width=L['rhi'] - L['rlo'],
                         rhi=L['rhi'], rlo=L['rlo'], end_state=L['state']))
    return out


def report_detection(B, states, valids, P):
    eps = episodes_from_states(states, valids)
    eps37 = [e for e in eps if B[e['i0']]['ym'] in W37]
    print("=== 1(a) THONG KE PHAT HIEN RANGE (5-7/2026, features.range_struct_scan — ha tang GD6) ===")
    print(f"n_range (VALID it nhat 1 lan) = {len(eps37)}")
    bym = defaultdict(int)
    for e in eps37:
        bym[B[e['i0']]['ym']] += 1
    print("theo thang: " + " ".join(f"{m[-2:]}={bym[m]}" for m in W37))
    if len(eps37) < 30:
        print("  *** CANH BAO: n_range < 30, moi ket luan thong ke deu YEU ***")
    ws = sorted(e['width'] for e in eps37)
    bs = sorted(e['bars'] for e in eps37)

    def qs(v):
        if not v:
            return "n/a"
        qq = st.quantiles(v, n=10) if len(v) >= 2 else [v[0]] * 9
        return f"p10={qq[0]:.1f} med={st.median(v):.1f} p90={qq[8]:.1f}"
    print(f"do rong (gia):    {qs(ws)}")
    print(f"thoi luong (nen): {qs(bs)}")
    reasons = defaultdict(int)
    for e in eps37:
        reasons[e['end_state']] += 1
    print("trang thai nen cuoi cua instance (xap xi 'ket cuc'): "
          + " ".join(f"{k}={v}" for k, v in sorted(reasons.items(), key=lambda x: -x[1])))
    print()
    return eps37


def draw_range(B, ep, path):
    from PIL import Image, ImageDraw
    i0, i1 = ep['i0'], ep['end_bar']
    pad_bars = 15
    lo_i = max(0, i0 - pad_bars)
    hi_i = min(len(B) - 1, i1 + pad_bars)
    seg = B[lo_i:hi_i + 1]
    W, H = 1400, 700
    ML, MR, MT, MB = 60, 20, 20, 40
    img = Image.new('RGB', (W, H), (18, 18, 20))
    d = ImageDraw.Draw(img)
    pmax = max(x['hi'] for x in seg)
    pmin = min(x['lo'] for x in seg)
    pad = (pmax - pmin) * 0.08 + 1e-6
    pmax += pad; pmin -= pad
    n = len(seg)
    cw = (W - ML - MR) / n

    def y_of(p):
        return MT + (pmax - p) / (pmax - pmin) * (H - MT - MB)

    def x_of(k):
        return ML + k * cw + cw / 2

    for gy in range(6):
        p = pmin + (pmax - pmin) * gy / 5
        yy = y_of(p)
        d.line([(ML, yy), (W - MR, yy)], fill=(45, 45, 50), width=1)
        d.text((2, yy - 6), f"{p:.1f}", fill=(150, 150, 150))
    for k, b in enumerate(seg):
        x = x_of(k)
        up = b['c'] >= b['o']
        col = (60, 170, 100) if up else (200, 70, 70)
        d.line([(x, y_of(b['hi'])), (x, y_of(b['lo']))], fill=col, width=1)
        yo, yc = y_of(b['o']), y_of(b['c'])
        d.rectangle([x - cw * 0.35, min(yo, yc), x + cw * 0.35, max(yo, yc)], fill=col)
    rhi, rlo = ep['rhi'], ep['rlo']
    x0, x1 = x_of(max(0, i0 - lo_i)), x_of(min(n - 1, i1 - lo_i))
    d.line([(x0, y_of(rhi)), (x1, y_of(rhi))], fill=(255, 200, 40), width=2)
    d.line([(x0, y_of(rlo)), (x1, y_of(rlo))], fill=(80, 180, 255), width=2)
    if ep['valid_bar'] is not None and lo_i <= ep['valid_bar'] <= hi_i:
        xv = x_of(ep['valid_bar'] - lo_i)
        d.line([(xv, MT), (xv, H - MB)], fill=(160, 160, 60), width=1)
        d.text((xv + 2, MT + 2), "XAC NHAN", fill=(220, 220, 140))
    xb = x_of(min(n - 1, i1 - lo_i))
    d.line([(xb, MT), (xb, H - MB)], fill=(255, 120, 255), width=1)
    d.text((xb + 2, MT + 16), f"nen cuoi: {ep['end_state']}", fill=(255, 160, 255))
    title = (f"range i0={ep['i0']} valid={ep['valid_bar']} end={ep['end_bar']}  "
             f"width={ep['width']:.1f}gia  bars={ep['bars']}  "
             f"{B[ep['i0']]['dt']:%Y-%m-%d %H:%M} -> {B[ep['end_bar']]['dt']:%Y-%m-%d %H:%M} UTC")
    d.text((ML, 2), title, fill=(230, 230, 230))
    img.save(path)


def report_visual(B, eps37, n_pick=10, seed=20260729):
    print(f"=== 1(b) KIEM CHUNG BANG MAT ({n_pick} range ngau nhien) ===")
    os.makedirs(IMG_DIR, exist_ok=True)
    rnd = random.Random(seed)
    pick = eps37[:] if len(eps37) <= n_pick else rnd.sample(eps37, n_pick)
    pick.sort(key=lambda e: e['i0'])
    links = []
    for k, ep in enumerate(pick, 1):
        fn = f"range_{k:02d}.png"
        path = os.path.join(IMG_DIR, fn)
        draw_range(B, ep, path)
        sz = os.path.getsize(path)
        links.append((fn, ep, sz))
        print(f"  [{k:02d}] {fn}  i0={ep['i0']} width={ep['width']:.1f}gia bars={ep['bars']} "
              f"end={ep['end_state']}  {sz/1024:.0f}KB")
    print()
    return links


def report_rotation(B, states, eps37, P):
    print("=== 1(c) TY LE XOAY BIEN NEN (baseline rotation rate) ===")
    ev = []
    for ep in eps37:
        vb, i0, end = ep['valid_bar'], ep['i0'], ep['end_bar']
        rhi, rlo = ep['rhi'], ep['rlo']
        width = rhi - rlo
        tol = max(P['TOLMIN'], P['TOLF'] * width)
        last_up = last_dn = -999
        for i in range(vb + 1, end + 1):
            b = B[i]
            if b['hi'] >= rhi - tol and i - last_up >= P['SEP']:
                last_up = i
                ev.append(_resolve(B, i, end, rlo, rhi, tol, P['BUF'], True, width))
            if b['lo'] <= rlo + tol and i - last_dn >= P['SEP']:
                last_dn = i
                ev.append(_resolve(B, i, end, rlo, rhi, tol, P['BUF'], False, width))
    n = len(ev)
    print(f"so lan cham (post-valid, 5-7/2026, dung range_struct_scan cua GD6) = {n}")
    if n < 25:
        print("  *** n < 25 -> KHONG KET LUAN duoc (LUAT CHUNG muc 3) ***")
    rot = sum(1 for e in ev if e['outcome'] == 'rotation')
    fail = sum(1 for e in ev if e['outcome'] == 'broke_same_side')
    cens = sum(1 for e in ev if e['outcome'] == 'censored')
    resolved = rot + fail
    print(f"rotation={rot}  broke_same_side={fail}  censored={cens}")
    if resolved:
        print(f"ty le xoay / da co ket qua ro rang = {100*rot/resolved:.1f}% ({rot}/{resolved})")
    if n:
        print(f"ty le xoay / TOAN BO (bi quan, censored=fail) = {100*rot/n:.1f}% ({rot}/{n})")
    p_nulls = [P['BUF'] / (P['BUF'] + e['width']) for e in ev]
    if p_nulls:
        print(f"NGAU NHIEN theo khoang cach (gambler's ruin p=BUF/(BUF+width)): "
              f"tb={100*st.mean(p_nulls):.1f}% med={100*st.median(p_nulls):.1f}%")
    if n and resolved:
        edge_rate = rot / resolved
        null_rate = st.mean(p_nulls)
        verdict = ('CO edge cau truc ro ret' if (edge_rate > null_rate * 1.5 and resolved >= 25)
                   else ('CO the co edge nhung n con mong' if edge_rate > null_rate
                         else 'KHONG hon ro ret muc ngau nhien -> KHONG co edge cau truc'))
        print(f"KET LUAN: quan sat {100*edge_rate:.1f}% vs null {100*null_rate:.1f}% -> {verdict}")
    print()
    return ev


def _resolve(B, i, end_bar, rlo, rhi, tol, buf, up_edge, width):
    for j in range(i + 1, end_bar + 1):
        b = B[j]
        if up_edge:
            if b['lo'] <= rlo + tol:
                return dict(i=i, side='up', width=width, outcome='rotation', hold=j - i)
            if b['c'] > rhi + buf:
                return dict(i=i, side='up', width=width, outcome='broke_same_side', hold=j - i)
        else:
            if b['hi'] >= rhi - tol:
                return dict(i=i, side='dn', width=width, outcome='rotation', hold=j - i)
            if b['c'] < rlo - buf:
                return dict(i=i, side='dn', width=width, outcome='broke_same_side', hold=j - i)
    return dict(i=i, side='up' if up_edge else 'dn', width=width, outcome='censored', hold=end_bar - i)


if __name__ == '__main__':
    B = E.load_m1()
    print(f"dxFeed M1={len(B)} nen | {B[0]['dt']} -> {B[-1]['dt']} (UTC)\n")
    P = dict(features.DEFAULT_P)
    states, arms, valids = features.range_struct_scan(B, P)
    eps37 = report_detection(B, states, valids, P)
    report_visual(B, eps37, n_pick=10)
    report_rotation(B, states, eps37, P)
