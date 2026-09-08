"""Do tan so 3 kich ban sau cum BAN THAO (delta cuc doan + khoi luong cuc lon) o day moi.

K1 = dao chieu len ngay, KHONG quay ve thu lai day
K2 = quay ve thu lai day (khong xuyen) roi moi len
K3 = xuyen xuong duoi day -> that bai
K0 = khong len duoc, cung khong xuyen -> di ngang / khong ro

Nguon: data-export/data-footprint/fp_GC_XCEC_Time_*_bars.csv (M1)
"""
import csv, sys, statistics as st

PATH = "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv"

def days_from_civil(y, m, d):
    y -= m <= 2
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468

def load(path):
    t, o, h, l, c, v, dl = [], [], [], [], [], [], []
    with open(path, newline="") as f:
        r = csv.reader(f)
        hd = next(r)
        ix = {k: i for i, k in enumerate(hd)}
        for row in r:
            s = row[ix["datetime"]]
            mins = days_from_civil(int(s[0:4]), int(s[5:7]), int(s[8:10])) * 1440 \
                   + int(s[11:13]) * 60 + int(s[14:16])
            t.append(mins)
            o.append(float(row[ix["open"]])); h.append(float(row[ix["high"]]))
            l.append(float(row[ix["low"]]));  c.append(float(row[ix["close"]]))
            v.append(float(row[ix["volume"]])); dl.append(float(row[ix["delta"]]))
    return t, o, h, l, c, v, dl

def run(t, o, h, l, c, v, dl, vol_mult, dlt_mult, up_R, W=50, LOOK=20, FWD=30,
        break_th=0.3, retest_th=0.5, side="sell"):
    n = len(t)
    res = {"K1": 0, "K2": 0, "K3": 0, "K0": 0}
    events = []
    i = W + LOOK
    while i < n - FWD - 1:
        # 1. phai la day moi (hoac dinh moi) trong LOOK nen
        if side == "sell":
            if l[i] > min(l[i - LOOK:i]):
                i += 1; continue
        else:
            if h[i] < max(h[i - LOOK:i]):
                i += 1; continue
        # 2. cua so lien tuc, khong vat qua nghi phien / cho noi hop dong
        seg = t[i - W:i + FWD + 1]
        if seg[-1] - seg[0] != len(seg) - 1:
            i += 1; continue
        # 3. khoi luong + delta cuc doan so voi nen 50 nen
        win_v = v[i - W:i]; win_d = [abs(x) for x in dl[i - W:i]]
        mv = st.median(win_v); md = st.median(win_d)
        if mv <= 0 or md <= 0:
            i += 1; continue
        if v[i] < vol_mult * mv:
            i += 1; continue
        if side == "sell" and dl[i] > -dlt_mult * md:
            i += 1; continue
        if side == "buy" and dl[i] < dlt_mult * md:
            i += 1; continue
        # 4. phan loai ket qua trong FWD nen ke tiep
        risk = h[i] - l[i]
        if risk <= 0:
            i += 1; continue
        if side == "sell":
            L = l[i]; tgt = L + up_R * risk
            broke = retested = False; out = "K0"
            for j in range(i + 1, i + 1 + FWD):
                if l[j] <= L - break_th:
                    out = "K3"; break
                if h[j] >= tgt:
                    out = "K2" if retested else "K1"; break
                if l[j] <= L + retest_th:
                    retested = True
        else:
            H = h[i]; tgt = H - up_R * risk
            broke = retested = False; out = "K0"
            for j in range(i + 1, i + 1 + FWD):
                if h[j] >= H + break_th:
                    out = "K3"; break
                if l[j] <= tgt:
                    out = "K2" if retested else "K1"; break
                if h[j] >= H - retest_th:
                    retested = True
        res[out] += 1
        events.append((i, out))
        i += FWD  # khong dem trung
    return res, events

if __name__ == "__main__":
    print("dang doc", PATH, flush=True)
    t, o, h, l, c, v, dl = load(PATH)
    print("so nen:", len(t), flush=True)
    for side in ("sell", "buy"):
        print("\n=== phia", side, "===")
        for vm, dm, up in ((3.0, 4.0, 2.0), (3.0, 4.0, 1.5), (2.5, 3.0, 2.0),
                           (4.0, 5.0, 2.0), (3.0, 4.0, 3.0)):
            res, ev = run(t, o, h, l, c, v, dl, vm, dm, up, side=side)
            tot = sum(res.values())
            if tot == 0:
                print(f"vol x{vm} delta x{dm} muc tieu {up}R -> n=0"); continue
            pct = {k: 100.0 * res[k] / tot for k in res}
            print(f"vol x{vm} delta x{dm} muc tieu {up}R  n={tot:5d} | "
                  f"K1 {res['K1']:4d} ({pct['K1']:4.1f}%)  K2 {res['K2']:4d} ({pct['K2']:4.1f}%)  "
                  f"K3 {res['K3']:4d} ({pct['K3']:4.1f}%)  K0 {res['K0']:4d} ({pct['K0']:4.1f}%)"
                  f" | K1 vs K2: {100.0*res['K1']/max(1,res['K1']+res['K2']):.1f}% / "
                  f"{100.0*res['K2']/max(1,res['K1']+res['K2']):.1f}%", flush=True)
