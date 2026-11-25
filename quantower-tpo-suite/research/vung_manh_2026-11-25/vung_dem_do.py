#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vung_dem_do.py — đo "vùng đệm" quanh hộp HVN v2 (VUNG-DEM.md). Cần chạy vung_dem_events.py trước.

  python vung_dem_do.py gc|nq25

Bảng A: phân phối điểm đảo so với mép gần của hộp (thật và đối chứng dời), tách phía tiếp cận.
Bảng B: các cách dựng vùng đệm — tỉ lệ "bắt" điểm đảo, so với đệm cố định cùng bề rộng trung bình, với hộp dời,
        và với phép hoán vị bề rộng giữa các hộp (bề rộng theo râu có mang thông tin riêng của hộp không).
Bảng C: đặt lệnh limit ở mép ngoài vùng đệm (treo tới khi giá bật ngược 1 U), dừng lỗ sau mép xa của hộp 0,15 U:
        tỉ lệ khớp, thắng 1:1, R 1:2.
"""
import os, pickle, sys
import numpy as np, pandas as pd
import vung_dem_lib as L
import vung_dem_events as E

CAP = 0.5           # vùng đệm không rộng hơn dải tiếp cận (× U)
SL_PAD = 0.15       # dừng lỗ sau mép xa của hộp (× U)
H_TRADE = 1380      # số nến M1 theo dõi lệnh (≈ 1 phiên)
RS = np.random.RandomState(7)

# tên → hàm(df) trả bề rộng vùng đệm theo U (chưa cắt CAP)
VAR = [
    ("mép hộp trần (không đệm)", lambda d: 0 * d.u),
    ("cố định 0,10 U", lambda d: 0.10 + 0 * d.u),
    ("cố định 0,20 U", lambda d: 0.20 + 0 * d.u),
    ("cố định 0,30 U", lambda d: 0.30 + 0 * d.u),
    ("cố định 0,40 U", lambda d: 0.40 + 0 * d.u),
    ("râu M30, thân chạm hộp: trung vị đầu râu", lambda d: d.w_p50 / d.u),
    ("râu M30, thân chạm hộp: phân vị 75", lambda d: d.w_p75 / d.u),
    ("râu M30, đóng trong hộp: trung vị đầu râu", lambda d: d.w2_p50 / d.u),
    ("râu M30, đóng trong hộp: phân vị 75", lambda d: d.w2_p75 / d.u),
    ("**ĐỀ XUẤT: sườn ≥ 50 % đỉnh, trần 0,45 up**", lambda d: d.fin / d.u),
    ("sườn profile ≥ 50 % đỉnh", lambda d: d.pf50 / d.u),
    ("sườn profile ≥ 40 % đỉnh", lambda d: d.pf40 / d.u),
    ("sườn profile ≥ 30 % đỉnh", lambda d: d.pf30 / d.u),
    ("số nến M30 phủ ≥ 67 % của hộp", lambda d: d.tpo67 / d.u),
    ("số nến M30 phủ ≥ 50 % của hộp", lambda d: d.tpo50 / d.u),
]


def load_ev(sym):
    df = pd.DataFrame(pickle.load(open(E.out_path(sym), "rb")))
    df = df[df.done1].reset_index(drop=True)
    df["wd"] = (df.hi - df.lo) / df.u
    df["box"] = df.name + "_" + df.end.astype(str) + "_" + df.lo0.round(2).astype(str)
    return df


def boot(df, fn, n=600):
    """Khoảng 5–95 % bằng bootstrap theo HỘP (các lần quay lại cùng một hộp không độc lập)."""
    keys = df.box.unique(); idx = {k: np.where(df.box.values == k)[0] for k in keys}
    out = []
    for _ in range(n):
        ch = RS.choice(keys, len(keys))
        out.append(fn(df.iloc[np.concatenate([idx[k] for k in ch])]))
    return np.nanpercentile(out, [5, 95])


def tab_A(df, sym):
    print("\n## A. %s — điểm đảo so với mép gần của hộp (bật ngược ≥ 1 U; dải tiếp cận 0,5 U)" % sym.upper())
    print("| Loại | Phía tiếp cận | n (số hộp) | đảo TRƯỚC mép | … trong đó cách mép ≤ 0,05 U | 0,05–0,15 U | 0,15–0,25 U | 0,25–0,35 U | 0,35–0,5 U | đảo TRONG hộp | XUYÊN qua mép xa | khoảng cách đảo trước mép, p25 / 50 / 75 (U) |")
    print("|" + "---|" * 12)
    for typ, ten in (("that", "hộp thật"), ("doi", "hộp dời (đối chứng)")):
        for side, ts in ((1, "từ trên xuống"), (-1, "từ dưới lên"), (0, "cả hai")):
            g = df[(df.typ == typ) & ((df.side == side) | (side == 0))]
            d, w = g.depth1.values, g.wd.values
            fr = d < 0
            b = lambda a, z: 100 * ((d < -a) & (d >= -z)).mean()
            q = np.percentile(-d[fr], [25, 50, 75]) if fr.any() else [np.nan] * 3
            print("| %s | %s | %d (%d) | %.0f %% | %.0f %% | %.0f %% | %.0f %% | %.0f %% | %.0f %% | %.0f %% | %.0f %% | %.2f / %.2f / %.2f |"
                  % (ten, ts, len(g), g.box.nunique(), 100 * fr.mean(), 100 * ((d < 0) & (d >= -0.05)).mean(), b(0.05, 0.15), b(0.15, 0.25), b(0.25, 0.35), b(0.35, 0.51),
                     100 * ((d >= 0) & (d <= w)).mean(), 100 * (d > w).mean(), q[0], q[1], q[2]))
    t, c = df[df.typ == "that"], df[df.typ == "doi"]
    for nm, f in (("đảo trước mép", lambda g: (g.depth1 < 0).mean()), ("đảo trong hộp", lambda g: ((g.depth1 >= 0) & (g.depth1 <= g.wd)).mean()),
                  ("đảo trong hộp hoặc trước mép ≤ 0,25 U", lambda g: ((g.depth1 >= -0.25) & (g.depth1 <= g.wd)).mean()), ("xuyên", lambda g: (g.depth1 > g.wd).mean())):
        lo, hi = boot(t, f); base = f(c)
        print("- %s: thật %.1f %% [%.1f; %.1f] · đối chứng %.1f %%" % (nm, 100 * f(t), 100 * lo, 100 * hi, 100 * base))
    for B in (0.5, 1.5):
        k = "depth%g" % B
        print("- kiểm độ nhạy, bật ngược ≥ %g U: thật trước mép / trong hộp / xuyên = %.0f / %.0f / %.0f %% · đối chứng %.0f / %.0f / %.0f %%"
              % (B, *(100 * x for x in ((t[k] < 0).mean(), ((t[k] >= 0) & (t[k] <= t.wd)).mean(), (t[k] > t.wd).mean(),
                                         (c[k] < 0).mean(), ((c[k] >= 0) & (c[k] <= c.wd)).mean(), (c[k] > c.wd).mean()))))


def tab_B(df, sym):
    print("\n## B. %s — vùng đệm phía tiếp cận: có bắt điểm đảo tốt hơn không" % sym.upper())
    print("| Cách dựng | % hộp dựng được | bề rộng đệm (U): trung bình · p25 / 50 / 75 | điểm đảo rơi vào ĐỆM (thật) | hộp dời | đệm cố định cùng bề rộng TB (thật) | hoán vị bề rộng giữa các hộp: trung bình [5; 95 %] | điểm đảo rơi vào ĐỆM + HỘP (thật · dời) |")
    print("|" + "---|" * 8)
    t, c = df[df.typ == "that"], df[df.typ == "doi"]
    for ten, fn in VAR:
        bt, bc = np.minimum(fn(t).values, CAP), np.minimum(fn(c).values, CAP)
        dt, dc = t.depth1.values, c.depth1.values
        hit = lambda d, b: ((d < 0) & (d >= -b)).mean()
        k = bt.mean()
        per = []
        if bt.std() > 1e-9:
            # hoán vị ở mức HỘP (mỗi hộp một bề rộng cho mỗi phía)
            keys = (t.box + "_" + t.side.astype(str)).values
            uk = np.unique(keys); wmap = {q: bt[keys == q][0] for q in uk}
            vals = np.array([wmap[q] for q in uk])
            for _ in range(400):
                pm = dict(zip(uk, RS.permutation(vals)))
                per.append(hit(dt, np.array([pm[q] for q in keys])))
        ps = ("%.1f %% [%.1f; %.1f]" % (100 * np.mean(per), *(100 * np.percentile(per, [5, 95])))) if per else "—"
        q = np.percentile(bt, [25, 50, 75])
        print("| %s | %.0f | %.2f · %.2f / %.2f / %.2f | %.1f %% | %.1f %% | %.1f %% | %s | %.1f %% · %.1f %% |"
              % (ten, 100 * (bt > 0).mean(), k, q[0], q[1], q[2], 100 * hit(dt, bt), 100 * hit(dc, bc), 100 * hit(dt, np.full(len(dt), k)), ps,
                 100 * ((dt >= -bt) & (dt <= t.wd.values)).mean(), 100 * ((dc >= -bc) & (dc <= c.wd.values)).mean()))
    # tương quan: bề rộng đệm có đoán được KHOẢNG CÁCH đảo trước mép không
    fr = t[t.depth1 < 0]
    print("\nTrong %d lần hộp thật đảo trước mép — tương quan hạng (Spearman) giữa bề rộng đệm và khoảng cách đảo:" % len(fr))
    for ten, fn in VAR[5:]:
        b = np.minimum(fn(fr).values, CAP)
        r = pd.Series(b).corr(pd.Series(-fr.depth1.values), method="spearman")
        print("- %s: %+.2f" % (ten, r))


def tab_D(df, sym):
    t = df[df.typ == "that"]; c = df[df.typ == "doi"]
    print("\n## D. %s — mật độ điểm đảo theo từng dải 0,1 U (%% số lần quay lại; đều nhau = mép hộp không phải ranh giới)" % sym.upper())
    edges = [-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4]
    print("| Loại | " + " | ".join("%s" % ("trước mép %.1f–%.1f" % (-b, -a) if a < 0 else "trong hộp %.1f–%.1f" % (a, b)) for a, b in zip(edges, edges[1:] + [0.5])) + " |")
    print("|" + "---|" * 11)
    for ten, g in (("thật", t), ("dời", c)):
        print("| %s | " % ten + " | ".join("%.1f" % (100 * ((g.depth1 >= a) & (g.depth1 < b)).mean()) for a, b in zip(edges, edges[1:] + [0.5])) + " |")
    print("\nTương quan hạng giữa các cách dựng (bề rộng đệm phía tiếp cận, hộp thật):")
    cols = dict(fin="đề xuất", w_p50="râu thân chạm hộp p50", w2_p50="râu đóng trong hộp p50", pf40="sườn 40 %", tpo67="nến phủ 67 %")
    b = t.drop_duplicates(["box", "side"])
    print((b[list(cols)].rename(columns=cols).div(b.u, axis=0)).corr(method="spearman").round(2).to_string())


def trades(D, df, b_u, R=(1.0, 2.0)):
    """Limit ở mép ngoài vùng đệm (mép gần ± b), dừng lỗ sau mép xa SL_PAD × U. Trả DataFrame fill, w1, R2, risk."""
    m1 = D.m1; H, Lw = m1["h"], m1["l"]; N = len(H)
    out = []
    for (i0, side, lo, hi, u, iE), b in zip(df[["i0", "side", "lo", "hi", "u", "iE1"]].values, b_u):
        i0 = int(i0); iE = int(iE)
        ent = hi + b * u if side > 0 else lo - b * u
        sl = lo - SL_PAD * u if side > 0 else hi + SL_PAD * u
        risk = abs(ent - sl)
        en = min(N, i0 + H_TRADE)
        h, l = H[i0:en], Lw[i0:en]
        f = np.where(l <= ent)[0] if side > 0 else np.where(h >= ent)[0]
        f = f[f <= iE - i0]                      # lệnh chỉ treo tới điểm đảo: đảo trước mức đặt lệnh ⇒ LỠ
        if len(f) == 0: out.append((0, np.nan, np.nan, risk / u)); continue
        h, l = h[f[0]:], l[f[0]:]
        res = []
        for r in R:
            if side > 0: st, tp = np.where(l <= sl)[0], np.where(h >= ent + r * risk)[0]
            else: st, tp = np.where(h >= sl)[0], np.where(l <= ent - r * risk)[0]
            # nến khớp lệnh không được tính chốt lời (không biết thứ tự trong nến); cùng nến chạm cả hai ⇒ thua
            tp = tp[tp > 0]
            a, z = (st[0] if len(st) else 10 ** 9), (tp[0] if len(tp) else 10 ** 9)
            if a == z == 10 ** 9:
                last = (D.m1["c"][i0:en][f[0]:][-1] - ent) * (1 if side > 0 else -1) / risk
                res.append(float(np.clip(last, -1, r)))
            else: res.append(r if z < a else -1.0)
        out.append((1, 1.0 if res[0] > 0.999 else 0.0 if res[0] < -0.999 else np.nan, res[1], risk / u))
    return pd.DataFrame(out, columns=["fill", "w1", "R2", "risk"], index=df.index)


def tab_C(D, df, sym):
    print("\n## C. %s — limit ở mép ngoài vùng đệm, dừng lỗ sau mép xa của hộp %.2f U, theo dõi %d nến M1" % (sym.upper(), SL_PAD, H_TRADE))
    print("| Cách dựng | Loại | n lần quay lại | khớp | rủi ro TB (U) | thắng 1:1 (trên lệnh đã ngã ngũ) | R 1:2 mỗi lệnh khớp [5; 95 %] | R 1:2 mỗi lần quay lại |")
    print("|" + "---|" * 8)
    for ten, fn in [VAR[i] for i in (0, 1, 2, 3, 4, 5, 7, 9, 11)]:
        for typ, tt in (("that", "thật"), ("doi", "dời")):
            g = df[df.typ == typ]
            tr = trades(D, g, np.minimum(fn(g).values, CAP))
            gg = g.assign(**{k: tr[k] for k in tr})
            f = gg[gg.fill == 1]
            lo, hi = boot(f, lambda x: x.R2.mean(), 300) if typ == "that" else (np.nan, np.nan)
            print("| %s | %s | %d | %.0f %% | %.2f | %.1f %% (%d) | %+.3f %s | %+.3f |"
                  % (ten, tt, len(g), 100 * tr.fill.mean(), f.risk.mean(), 100 * f.w1.mean(), f.w1.notna().sum(), f.R2.mean(),
                     ("[%+.2f; %+.2f]" % (lo, hi)) if typ == "that" else "", f.R2.sum() / len(g)))


def main(sym):
    D, vm, V = L.load(sym)
    df = load_ev(sym)
    t = df[df.typ == "that"]
    print("# %s · %d lần quay lại hộp thật (%d hộp, %d phiên) · %d lần ở hộp dời" % (sym.upper(), len(t), t.box.nunique(), D.day_of[D.m1["i30"][t.i0.values]].max() - D.day_of[D.m1["i30"][t.i0.values]].min() + 1, (df.typ == "doi").sum()))
    print("hộp ngày %d lần · hộp tuần %d lần · bề rộng hộp (U) p10/50/90 %s" % ((t.name == "hvn_d").sum(), (t.name == "hvn_w").sum(), np.round(np.percentile(t.wd, [10, 50, 90]), 2).tolist()))
    tab_A(df, sym); tab_D(df, sym); tab_B(df, sym); tab_C(D, df, sym)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1])
