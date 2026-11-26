# -*- coding: utf-8 -*-
"""Chép marks.csv / sh.csv (OrderFlowBubbles C# thật, golden harness 'stophunt --marks') vào signals/ và
tính phía của từng vòng Big Trade (Ask > Bid ở mức giá đó → +1, ngược lại −1) từ file mức giá → signals/bt_side.csv.
Lệnh tạo marks/sh (từ quantower-orderflow-indicator):
  dotnet run -c Release --project perf/Golden -- stophunt --levels <fp_NQZ26_..._293d16h.csv> --tick 0.25 --symbol NQZ26 --minutes 1 \
      --work <W> --out <W>/sh.csv --marks <W>/marks.csv
"""
import csv, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
src = sys.argv[1]
out = os.path.join(HERE, "signals"); os.makedirs(out, exist_ok=True)
for f in ("marks.csv", "sh.csv"):
    shutil.copy(os.path.join(src, f), os.path.join(out, f))
lv = os.path.join(ROOT, "data-export", "data-footprint", "fp_NQZ26_XCME_Time_20260204-20261125_293d16h.csv")
bars = lv.replace(".csv", "_bars.csv")
want = {}
with open(os.path.join(out, "marks.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["kind"] == "bt":
            want.setdefault(r["t"], set()).add(round(float(r["price"]) / 0.25))
idx = {}
with open(bars, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        k = r["datetime"][:16]
        if k in want: idx[int(r["bar_idx"])] = k
rows = []
with open(lv, encoding="utf-8-sig") as f:
    rd = csv.reader(f); next(rd)
    for p in rd:
        bi = int(p[0])
        if bi in idx:
            tk = round(float(p[2]) / 0.25)
            if tk in want[idx[bi]]:
                rows.append((idx[bi], p[2], 1 if float(p[4]) > float(p[3]) else -1))
n = sum(len(v) for v in want.values())
assert len(rows) == n, (len(rows), n)
with open(os.path.join(out, "bt_side.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["t", "price", "side"]); w.writerows(rows)
print("bt", n, "-> bt_side.csv")
