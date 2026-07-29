#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parity_v7.py — DOI CHIEU TUNG TIN HIEU: engine Python (cbr_v6) vs logic C# (ParityHarness).

GD9 cam "tuyen bo parity dua tren doc code". File nay so TUNG tin hieu: thoi gian, phia, entry,
SL, risk. Ra bang khop / chi-co-Python / chi-co-C# / lech gia tri.

CACH CHAY (2 che do):

  A) PARITY OFFLINE (thuat toan C# vs Python, chay duoc ngay tren Linux):
       cd research/wyckoff/parity && dotnet build -c Release
       dotnet bin/Release/net10.0/ParityHarness.dll "<dxfeed.csv>" parity/cs_signals.csv
       python3 parity_v7.py parity/cs_signals.csv

  B) PARITY LIVE (DLL that trong Quantower vs Python — viec cua GD10):
       Lay file CSV tin hieu do indicator ghi ra tren may Windows (input "Xuat CSV toan bo tin
       hieu", mac dinh o thu muc Documents), roi:
       python3 parity_v7.py <duong-dan-csv-live> --live

  ⚠ Che do A KHONG kiem duoc: Quantower loc nen rac, nen thieu, volume tu VolumeAnalysis khac
  dxFeed, timezone cua feed. Chi che do B kiem duoc nhung thu do.
"""
import sys, os, csv
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))          # research/
sys.path.insert(0, HERE)                            # research/wyckoff/
import entry_dxfeed as E
import cbr_v6 as V6

TICK = 0.1
MONTHS = ('2026-05', '2026-06', '2026-07')


def python_signals():
    """Chay engine Python voi CAU HINH DONG BANG (AUDIT_V7 §14)."""
    B = E.load_m1()
    vf = E.VOLFLOOR_FROZEN
    E.VOLFLOOR_AUTO = vf
    V6.prepare(B)
    C = V6.cfg(CLEAN=True, PMAX=1.00, RR=4.0)
    S = V6.scan(B, C, vf, None)
    out = []
    for s in S:
        out.append(dict(dt=s['dt'], side=s['side'], entry=round(s['entry'], 4),
                        sl=round(s['sl'], 4), risk=round(s['risk_t'], 2), ym=s['ym'], r=s['r']))
    out.sort(key=lambda x: x['dt'])
    return out, B


def load_cs(path, live=False):
    """Doc CSV tin hieu C#. Che do harness: time,side,entry,sl,risk_t,idx.
    Che do live: file do WyckoffRunner ghi (co cot 'nhanh'), chi lay nhanh CBR."""
    rows = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        rd = csv.DictReader(f)
        cols = {c.lower().strip(): c for c in (rd.fieldnames or [])}

        def pick(*names):
            for n in names:
                if n in cols:
                    return cols[n]
            return None

        # ten cot: 'time/side/entry/sl' = harness offline;
        #          'ngay_gio/huong/entry/SL/risk_gia/nhanh' = CSV that do WyckoffRunner.ExportSignals() ghi
        cT = pick('time', 'ngay_gio', 'thoi gian', 'datetime', 'time_utc')
        cS = pick('side', 'huong', 'phia')
        cE = pick('entry', 'gia vao')
        cL = pick('sl')
        cR = pick('risk_t', 'risk_gia', 'risk')
        cB = pick('nhanh', 'branch', 'scenario')
        if not (cT and cS and cE):
            raise SystemExit(f"CSV thieu cot bat buoc. Header: {rd.fieldnames}")
        for x in rd:
            if live and cB and 'CBR' not in (x.get(cB) or '').upper():
                continue                              # che do live: chi doi chieu nhanh CBR (KB1)
            ts = (x[cT] or '').strip()
            dt = None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M",
                        "%m/%d/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
                try:
                    dt = datetime.strptime(ts[:19], fmt); break
                except ValueError:
                    continue
            if dt is None:
                continue
            sd = (x[cS] or '').strip().upper()
            side = 'LONG' if sd in ('LONG', 'MUA', 'BUY', '1', '+1') else 'SHORT'
            def f(c):
                if not c:
                    return None
                v = (x.get(c) or '').strip().replace(',', '.')
                try:
                    return round(float(v), 4)
                except ValueError:
                    return None
            rows.append(dict(dt=dt, side=side, entry=f(cE), sl=f(cL), risk=f(cR)))
    rows.sort(key=lambda r: r['dt'])
    return rows


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    cs_path = sys.argv[1]
    live = '--live' in sys.argv
    if not os.path.exists(cs_path):
        raise SystemExit(f"Khong thay file: {cs_path}")

    py, B = python_signals()
    cs = load_cs(cs_path, live=live)

    print("=" * 118)
    print(f"PARITY V7 — {'LIVE (DLL Quantower)' if live else 'OFFLINE (thuat toan C# harness)'} vs Python cbr_v6")
    print("=" * 118)
    print(f"Python : {len(py):3} tin hieu | {py[0]['dt']} -> {py[-1]['dt']}" if py else "Python: 0")
    print(f"C#     : {len(cs):3} tin hieu | {cs[0]['dt']} -> {cs[-1]['dt']}" if cs else "C#: 0")

    # che do live: chi so trong khoang thoi gian GIAO nhau (live ngan hon nhieu)
    if live and cs:
        lo, hi = cs[0]['dt'], cs[-1]['dt']
        n0 = len(py)
        py = [p for p in py if lo <= p['dt'] <= hi]
        print(f"\n⚠ Che do live: thu hep Python ve khoang giao [{lo} .. {hi}] -> {len(py)}/{n0} tin hieu.")

    # ghep theo (thoi gian, phia) — cho phep lech <=1 phut de chiu duoc lech nhan thoi gian
    used = set()
    match, only_py, val_diff = [], [], []
    for p in py:
        best = None
        for k, c in enumerate(cs):
            if k in used or c['side'] != p['side']:
                continue
            d = abs((c['dt'] - p['dt']).total_seconds())
            if d <= 60 and (best is None or d < best[0]):
                best = (d, k, c)
        if best is None:
            only_py.append(p)
        else:
            _, k, c = best
            used.add(k)
            de = abs((c['entry'] - p['entry']) / TICK) if c['entry'] is not None else 0.0
            dl = abs((c['sl'] - p['sl']) / TICK) if c['sl'] is not None else 0.0
            match.append((p, c, de, dl))
            if de > 0.5 or dl > 0.5:
                val_diff.append((p, c, de, dl))
    only_cs = [c for k, c in enumerate(cs) if k not in used]

    print()
    print("-" * 118)
    print(f"{'thoi gian (Python)':<20} {'phia':<6} {'entry py':>10} {'entry C#':>10} {'SL py':>9} "
          f"{'SL C#':>9} {'d entry':>8} {'d SL':>7}  ket qua")
    print("-" * 118)
    for p, c, de, dl in match:
        flag = "KHOP" if (de <= 0.5 and dl <= 0.5) else f"LECH GIA TRI"
        print(f"{str(p['dt']):<20} {p['side']:<6} {p['entry']:>10.2f} "
              f"{(c['entry'] if c['entry'] is not None else float('nan')):>10.2f} {p['sl']:>9.2f} "
              f"{(c['sl'] if c['sl'] is not None else float('nan')):>9.2f} {de:>7.1f}t {dl:>6.1f}t  {flag}")
    for p in only_py:
        print(f"{str(p['dt']):<20} {p['side']:<6} {p['entry']:>10.2f} {'—':>10} {p['sl']:>9.2f} "
              f"{'—':>9} {'—':>8} {'—':>7}  CHI CO O PYTHON")
    for c in only_cs:
        e = c['entry'] if c['entry'] is not None else float('nan')
        print(f"{str(c['dt']):<20} {c['side']:<6} {'—':>10} {e:>10.2f} {'—':>9} "
              f"{'—':>9} {'—':>8} {'—':>7}  CHI CO O C#")

    n = max(len(py), len(cs), 1)
    nlech = len(only_py) + len(only_cs) + len(val_diff)
    print("-" * 118)
    print(f"TONG KET: khop {len(match)}  |  chi Python {len(only_py)}  |  chi C# {len(only_cs)}  |  "
          f"lech gia tri {len(val_diff)}  |  tong lech {nlech}/{n} = {nlech/n:.1%}")

    # tieu chi GD9
    print()
    if nlech == 0:
        verdict = "DAT — 0 tin hieu lech, 0 lech gia tri"
    elif nlech <= 2 and nlech / n <= 0.10:
        verdict = f"DAT CO DIEU KIEN — {nlech} lech (<=2), PHAI giai thich tung cai o PARITY_V7.md"
    elif nlech / n > 0.10:
        verdict = f"KHONG DAT — lech {nlech/n:.1%} > 10%, KHONG duoc ship"
    else:
        verdict = f"XEM LAI — {nlech} lech"
    print(f"PHAN QUYET (tieu chi GD9): {verdict}")
    if not live:
        print()
        print("⚠ Day la parity THUAT TOAN (C# harness vs Python), CHUA phai parity DLL-trong-Quantower.")
        print("  Nhung thu chua kiem duoc: Quantower loc nen rac / nen thieu / volume VolumeAnalysis")
        print("  khac dxFeed / timezone feed. Phai kiem o GD10 bang CSV live: parity_v7.py <csv> --live")
    return 0 if nlech == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
