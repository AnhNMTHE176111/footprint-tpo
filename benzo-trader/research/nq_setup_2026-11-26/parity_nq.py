# -*- coding: utf-8 -*-
"""Parity Python (nq_setup.py) ↔ C# (tools/ReplayNq): cùng danh sách lệnh ĐÃ ĐÓNG từ 2026-09-14 tới hết dữ liệu.
  python parity_nq.py <trades_cs.csv> [--failbreak]
So từng lệnh: giờ nến tín hiệu, loại, hướng, entry, SL, TP, khoảng SL, tín hiệu thứ hai, bias, nhãn mốc lớn, phiên, giờ thoát, giá thoát, kết cục, R."""
import csv, sys
from nq_setup import *

START = datetime(2026, 9, 14, tzinfo=timezone.utc)


def py_rows(failbreak):
    bars, sig = build(START)
    m = Machine(bars, sig, dict(FAIL_BREAK=failbreak))
    m.run(START)
    last = len(bars.t) - 1
    out = []
    for t in m.trades:
        if t.exit_i >= last:      # Python đóng TIME ở nến cuối file; C# còn mở → bỏ
            continue
        out.append([bars.key[t.sig], t.kind, "buy" if t.side > 0 else "sell", t.entry, t.sl, t.tp, t.dist, t.second, t.bias, t.big,
                    t.big_lv, t.session, bars.key[t.exit_i], t.exit_px, t.how, t.r])
    return out


def norm(r):
    o = list(r)
    for k in (3, 4, 5, 6, 13, 15):
        o[k] = round(float(o[k]), 6)
    return o


if __name__ == "__main__":
    fb = "--failbreak" in sys.argv
    with open(sys.argv[1], encoding="utf-8") as f:
        cs = [norm(r) for r in list(csv.reader(f))[1:]]
    py = [norm(r) for r in py_rows(fb)]
    bad = 0
    for k in range(max(len(cs), len(py))):
        a = py[k] if k < len(py) else None
        b = cs[k] if k < len(cs) else None
        if a != b:
            bad += 1
            if bad <= 10:
                print("LỆCH #%d\n  py %s\n  cs %s" % (k, a, b))
    print(f"Python {len(py)} lệnh, C# {len(cs)} lệnh, lệch {bad} → {'KHỚP 100 %' if bad == 0 else 'LỆCH'}")
    sys.exit(1 if bad else 0)
