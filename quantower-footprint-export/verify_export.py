#!/usr/bin/env python3
"""
Kiem tra file CSV do indicator Footprint Export xuat ra (chay SAU khi xuat tren Windows).
    python3 verify_export.py <duong-dan>/fp_MGC_1m_20260728_101500.csv

Kiem 8 dieu — dung/sai in ro, khong doan:
  1. So cot moi dong == header (CSV khong rach)
  2. Khong co gia tri dang E+/E- (gia tri MOI cua MaxDelta/MinDelta bi lot)
  3. (bar_idx, price) DUY NHAT — khong co dong trung
  4. Trong 1 nen, gia TANG DAN
  5. delta == ask_vol - bid_vol tren tung muc gia
  6. bid_vol + ask_vol <= volume  (phan chenh = lenh feed khong gan duoc phe chu dong)
  7. Neu co file _bars.csv: tong theo muc gia == so tong hop cua nen (volume/delta/trades)
  8. poc_price cua file _bars.csv co that trong file muc gia, va dung la muc volume lon nhat
"""
import csv
import os
import sys
from collections import defaultdict

TOL = 1e-6


def sniff(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        head = fh.readline()
    for s in (",", ";", "\t", "|"):
        if s in head:
            return s
    return ","


def read(path):
    sep = sniff(path)
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh, delimiter=sep))
    return rows[0], rows[1:], sep


def num(s):
    return float(s) if s not in ("", None) else 0.0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    lv_path = sys.argv[1]
    if not os.path.exists(lv_path):
        print("KHONG THAY FILE:", lv_path)
        return 2

    hdr, rows, sep = read(lv_path)
    print(f"File muc gia : {lv_path}")
    print(f"  sep='{sep!r}'  {len(rows):,} dong  {len(hdr)} cot")
    print(f"  cot: {hdr}")
    fails = []

    def check(cond, msg):
        print(("  OK   " if cond else "  FAIL ") + msg)
        if not cond:
            fails.append(msg)

    # 1. so cot
    bad = [i for i, r in enumerate(rows, 2) if len(r) != len(hdr)]
    check(not bad, f"1. moi dong du {len(hdr)} cot" + (f" — lech o dong {bad[:5]}" if bad else ""))

    # 2. khong co E+/E-
    ebad = [i for i, r in enumerate(rows, 2) if any("E+" in c or "E-" in c for c in r)]
    check(not ebad, "2. khong co so dang E+/E- (gia tri MOI da duoc don)"
                    + (f" — dong {ebad[:5]}" if ebad else ""))

    ix = {n: i for i, n in enumerate(hdr)}
    need = ["bar_idx", "datetime", "price", "bid_vol", "ask_vol", "volume", "delta", "trades"]
    miss = [n for n in need if n not in ix]
    if miss:
        print("  FAIL  thieu cot:", miss)
        return 1

    per_bar = defaultdict(list)
    for r in rows:
        per_bar[int(r[ix["bar_idx"]])].append(r)

    # 3. (bar_idx, price) duy nhat
    dup = 0
    for b, rs in per_bar.items():
        ps = [r[ix["price"]] for r in rs]
        dup += len(ps) - len(set(ps))
    check(dup == 0, f"3. (bar_idx, price) duy nhat — so dong trung: {dup}")

    # 4. gia tang dan trong 1 nen
    notsorted = [b for b, rs in per_bar.items()
                 if any(num(rs[i + 1][ix["price"]]) <= num(rs[i][ix["price"]]) for i in range(len(rs) - 1))]
    check(not notsorted, "4. trong 1 nen gia TANG DAN"
                         + (f" — sai o nen {notsorted[:5]}" if notsorted else ""))

    # 5. delta == ask - bid
    bad5 = sum(1 for r in rows
               if abs((num(r[ix["ask_vol"]]) - num(r[ix["bid_vol"]])) - num(r[ix["delta"]])) > TOL)
    check(bad5 == 0, f"5. delta == ask_vol - bid_vol — sai {bad5}/{len(rows)} dong")

    # 6. bid+ask <= volume
    bad6 = sum(1 for r in rows
               if num(r[ix["bid_vol"]]) + num(r[ix["ask_vol"]]) > num(r[ix["volume"]]) + TOL)
    gap = sum(1 for r in rows
              if num(r[ix["volume"]]) - num(r[ix["bid_vol"]]) - num(r[ix["ask_vol"]]) > TOL)
    check(bad6 == 0, f"6. bid_vol+ask_vol <= volume — vi pham {bad6}/{len(rows)} dong")
    print(f"       (ghi chu: {gap:,}/{len(rows):,} dong co volume > bid+ask — "
          f"phan chenh la lenh feed khong gan duoc phe chu dong. Tinh delta%% thi chia cho 'volume'.)")

    print(f"\n  Tom tat: {len(per_bar):,} nen · trung binh {len(rows)/max(1,len(per_bar)):.1f} muc gia/nen")

    # ---- file nen
    root, ext = os.path.splitext(lv_path)
    bars_path = root + "_bars" + ext
    if not os.path.exists(bars_path):
        print(f"\n(Khong co {os.path.basename(bars_path)} — bo qua kiem 7 & 8)")
    else:
        bh, brows, bsep = read(bars_path)
        print(f"\nFile nen     : {bars_path}\n  {len(brows):,} dong  {len(bh)} cot")
        bad = [i for i, r in enumerate(brows, 2) if len(r) != len(bh)]
        check(not bad, f"   moi dong du {len(bh)} cot" + (f" — dong {bad[:5]}" if bad else ""))
        bx = {n: i for i, n in enumerate(bh)}

        n7 = v7 = d7 = t7 = 0
        n8 = p8 = 0
        for r in brows:
            b = int(r[bx["bar_idx"]])
            rs = per_bar.get(b)
            if not rs:
                continue
            n7 += 1
            v7 += abs(sum(num(x[ix["volume"]]) for x in rs) - num(r[bx["volume"]])) <= max(TOL, 1e-6 * abs(num(r[bx["volume"]])))
            d7 += abs(sum(num(x[ix["delta"]]) for x in rs) - num(r[bx["delta"]])) <= TOL
            t7 += abs(sum(num(x[ix["trades"]]) for x in rs) - num(r[bx["trades"]])) <= TOL
            if "poc_price" in bx and r[bx["poc_price"]]:
                n8 += 1
                poc = num(r[bx["poc_price"]])
                mx = max(num(x[ix["volume"]]) for x in rs)
                hit = any(abs(num(x[ix["price"]]) - poc) < TOL and abs(num(x[ix["volume"]]) - mx) < TOL for x in rs)
                p8 += hit
        check(v7 == n7, f"7a. tong volume theo muc gia == volume cua nen — dung {v7}/{n7}")
        check(d7 == n7, f"7b. tong delta theo muc gia == delta cua nen — dung {d7}/{n7}")
        check(t7 == n7, f"7c. tong trades theo muc gia == trades cua nen — dung {t7}/{n7}")
        check(p8 == n8, f"8.  poc_price = muc volume lon nhat trong file muc gia — dung {p8}/{n8}")
        print("       (7a/7b/7c sai => Total cua platform KHONG bang tong PriceLevels — "
              "bao lai de xem lai, dung tu suy dien.)")

    print("\n" + "=" * 60)
    if fails:
        print(f"CO {len(fails)} MUC SAI:")
        for f in fails:
            print("  -", f)
    else:
        print("TAT CA KIEM TRA DAT.")
    print("=" * 60)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
