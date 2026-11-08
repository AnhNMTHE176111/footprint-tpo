# -*- coding: utf-8 -*-
"""
measure.py — đo 5 chỉ số BRAINSTORM mục 5 cho range_proto.py, quét tham số mục 7b.

Dữ liệu:
  * chính : fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv, chia đôi theo thời gian (H1/H2)
  * chéo  : fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv (mã liên tục nối thô)
            → cắt thành ĐOẠN tại mọi nến |close − close trước| > 20 điểm và tại chỗ nối
              2026-07-29 20:59→22:00 UTC; chạy máy trạng thái riêng từng đoạn (không cửa sổ nào vắt qua).
  * thêm M5/M15 resample từ M1 (theo từng đoạn).

Chạy:  python measure.py            (ghi kết quả JSON vào research/measure_out/)
       python measure.py --events   (chỉ ghi events_90d.csv cho bộ tham số chọn)
"""
from __future__ import annotations
import json, os, sys, statistics as st
from dataclasses import asdict, replace
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from range_proto import Params, RangeEngine, load_bars, write_events, BROKEN, DEAD

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "data-export", "data-footprint"))
F90 = os.path.join(DATA, "fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv")
F748 = os.path.join(DATA, "fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
OUT = os.path.join(HERE, "measure_out")
TICK = 0.1
T_FWD = 240          # số nến tối đa theo dõi sau sự kiện
COST_TICKS = 2       # phí + trượt giá khứ hồi (tick) — như KB3 trong RESEARCH mục 5
CHOSEN = Params()    # = mặc định trong range_proto.Params (7b, riêng HminK 1.3→1.6 — xem MEASURE.md)


# ---------------------------------------------------------------- dữ liệu
def segments(bars, max_jump=20.0, cut=("2026-07-29 20:59", "2026-07-29 22:00")):
    segs, cur = [], []
    prev = None
    for b in bars:
        bad = prev is not None and (abs(b[4] - prev[4]) > max_jump or (prev[0][:16] <= cut[0] and b[0][:16] >= cut[1] and prev[0][:10] == cut[0][:10]))
        if bad and cur:
            segs.append(cur); cur = []
        cur.append(b)
        prev = b
    if cur:
        segs.append(cur)
    return [s for s in segs if len(s) >= 300]


def resample(seg, minutes):
    out = []
    key = None
    for (dt, o, h, l, c) in seg:
        mm = int(dt[14:16])
        k = dt[:14] + f"{mm - mm % minutes:02d}"
        if k != key:
            out.append([k + ":00", o, h, l, c]); key = k
        else:
            r = out[-1]
            r[2] = max(r[2], h); r[3] = min(r[3], l); r[4] = c
    return [tuple(r) for r in out]


# ---------------------------------------------------------------- đo
def analyse(seg, p: Params):
    eng = RangeEngine(p, TICK)
    for (_, o, h, l, c) in seg:
        eng.feed(o, h, l, c)
    H, L, C = eng.H, eng.L, eng.C
    n = len(C)
    days = len({b[0][:10] for b in seg})
    rr = []
    for r in eng.ranges:
        end = r.break_idx if (r.state in (BROKEN, DEAD) and r.break_idx >= 0) else r.last_idx
        core = max(1, end - r.start)
        mean_bar = sum(H[j] - L[j] for j in range(r.start, end + 1)) / (end - r.start + 1)
        rr.append(dict(h=r.top - r.bottom, w=end - r.start, w1=(r.first_break - r.start) if r.first_break >= 0 else None, h_mbr=(r.top - r.bottom) / r.mbr if r.mbr else 0,
                       h_mean=(r.top - r.bottom) / mean_bar if mean_bar else 0,
                       hunt=r.n_hunt, fail=r.n_fail, brk=r.n_break))
    # chỉ số 3: sau fail break
    fb = []
    brk_conf = {}
    for ev in eng.events:
        if ev.kind == "BreakConfirmed":
            brk_conf.setdefault((ev.rid, ev.side), []).append(ev.bar)
    for ev in eng.events:
        if ev.kind != "FailBreak":
            continue
        f, s, b = ev.bar, ev.side, ev.ref
        c = C[f]
        if s > 0:
            ext = max(H[b:f + 1]); stop = ext + 1; risk = stop - c; tgt = ev.bottom; reward = c - tgt
        else:
            ext = min(L[b:f + 1]); stop = ext - 1; risk = c - stop; tgt = ev.top; reward = tgt - c
        if risk <= 0:
            continue
        R = reward / risk
        later_brk = [x for x in brk_conf.get((ev.rid, s), []) if x > f]
        brk_at = later_brk[0] if later_brk else 10 ** 9
        touch = None; outcome = None; mtm = None
        for j in range(f + 1, min(n, f + 1 + T_FWD)):
            hit_t = (L[j] <= tgt) if s > 0 else (H[j] >= tgt)
            hit_s = (H[j] >= stop) if s > 0 else (L[j] <= stop)
            if touch is None and hit_t:
                touch = j
            if outcome is None:
                if hit_s:
                    outcome = "loss"
                elif hit_t:
                    outcome = "win"
            if touch is not None and outcome is not None:
                break
        if outcome is None:
            j = min(n - 1, f + T_FWD)
            mtm = ((c - C[j]) if s > 0 else (C[j] - c)) / risk
        fb.append(dict(R=R, risk=risk, opp_before_break=(touch is not None and touch < brk_at),
                       outcome=outcome, mtm=mtm))
    # chỉ số 4: sau phá thật
    bk = []
    for ev in eng.events:
        if ev.kind != "BreakConfirmed":
            continue
        b, s = ev.ref, ev.side
        h = ev.top - ev.bottom
        res = None
        for j in range(b + 1, min(n, b + 1 + T_FWD)):
            if ev.bottom <= C[j] <= ev.top:
                res = False; break
            if (s > 0 and H[j] >= ev.top + h) or (s < 0 and L[j] <= ev.bottom - h):
                res = True; break
        bk.append(res)
    return dict(n_bars=n, days=days, ranges=rr, fb=fb, bk=bk)


def merge(parts):
    out = dict(n_bars=0, days=0, ranges=[], fb=[], bk=[])
    for p in parts:
        for k in out:
            out[k] += p[k]
    return out


def pct(a, q):
    if not a:
        return None
    a = sorted(a)
    k = (len(a) - 1) * q
    lo = int(k); hi = min(lo + 1, len(a) - 1)
    return a[lo] + (a[hi] - a[lo]) * (k - lo)


def summarize(res):
    rr, fb, bk = res["ranges"], res["fb"], res["bk"]
    nr = len(rr)
    s = dict(days=res["days"], n_range=nr, per_day=round(nr / max(1, res["days"]), 2))
    if nr:
        s.update(h_p25=pct([r["h"] for r in rr], .25), h_med=pct([r["h"] for r in rr], .5), h_p75=pct([r["h"] for r in rr], .75),
                 w_p25=pct([r["w"] for r in rr], .25), w_med=pct([r["w"] for r in rr], .5), w_p75=pct([r["w"] for r in rr], .75),
                 w1_med=pct([r["w1"] for r in rr if r["w1"] is not None], .5),
                 h_mean_med=round(pct([r["h_mean"] for r in rr], .5), 2), h_mbr_med=round(pct([r["h_mbr"] for r in rr], .5), 2),
                 hunt_per=round(sum(r["hunt"] for r in rr) / nr, 2), fail_per=round(sum(r["fail"] for r in rr) / nr, 2),
                 brk_per=round(sum(r["brk"] for r in rr) / nr, 2))
    nf = len(fb)
    s["n_fail"] = nf
    if nf:
        s["p_opp_before_break"] = round(sum(f["opp_before_break"] for f in fb) / nf, 3)
        s["R_med"] = round(pct([f["R"] for f in fb], .5), 2)
        good = [f for f in fb if f["R"] >= 1.7]
        s["share_R17"] = round(len(good) / nf, 3)
        s["n_R17"] = len(good)

        def ev_of(lst, cost):
            vals = []
            for f in lst:
                c = cost / f["risk"]
                if f["outcome"] == "win":
                    vals.append(f["R"] - c)
                elif f["outcome"] == "loss":
                    vals.append(-1 - c)
                else:
                    vals.append(f["mtm"] - c)
            return round(sum(vals) / len(vals), 3) if vals else None, len(vals)
        if good:
            wins = sum(1 for f in good if f["outcome"] == "win")
            s["win_R17"] = round(wins / len(good), 3)
            s["breakeven_R17"] = round(st.mean(1 / (1 + f["R"]) for f in good), 3)
            s["EV_R17_gross"], _ = ev_of(good, 0)
            s["EV_R17_net2t"], _ = ev_of(good, COST_TICKS)
        s["EV_all_gross"], _ = ev_of(fb, 0)
        s["EV_all_net2t"], _ = ev_of(fb, COST_TICKS)
    known = [x for x in bk if x is not None]
    s["n_break"] = len(bk)
    s["p_break_1h"] = round(sum(known) / len(known), 3) if known else None
    return s


# ---------------------------------------------------------------- tác vụ song song
_DS = {}


def _load_all():
    b90 = load_bars(F90)
    half = len(b90) // 2
    h1, h2 = b90[:half], b90[half:]
    b748 = segments(load_bars(F748))
    return dict(
        H1=[h1], H2=[h2],
        H1_M5=[resample(h1, 5)], H2_M5=[resample(h2, 5)],
        H1_M15=[resample(h1, 15)], H2_M15=[resample(h2, 15)],
        G748=b748, G748_M5=[resample(s, 5) for s in b748], G748_M15=[resample(s, 15) for s in b748],
    )


def _init():
    global _DS
    _DS = _load_all()


def _job(arg):
    name, pd, ds = arg
    p = Params(**pd)
    res = merge([analyse(seg, p) for seg in _DS[ds]])
    return name, ds, pd, summarize(res)


def grid():
    base = CHOSEN
    var = dict(MinBars=[6, 8, 10, 12], HminK=[1.0, 1.3, 1.6, 2.0], HmaxK=[5.0, 6.0, 8.0], TolK=[0.3, 0.5, 0.8],
               K=[2, 3, 4], G=[0, 15, 30], PivotRule=["A", "B"], InsideRatio=[0.0, 0.7, 0.85], MaxReEntry=[-1, 1, 3])
    sets = [("base", asdict(base))]
    for k, vals in var.items():
        for v in vals:
            if getattr(base, k) == v:
                continue
            sets.append((f"{k}={v}", asdict(replace(base, **{k: v}))))
    # tổ hợp nhỏ 3 tham số tác động lớn nhất tới cụm/cạnh
    for mb in (8, 12):
        for tk in (0.3, 0.8):
            for rule in ("A", "B"):
                nm = f"MB{mb}_T{tk}_{rule}"
                sets.append((nm, asdict(replace(base, MinBars=mb, TolK=tk, PivotRule=rule))))
    return sets


def main():
    os.makedirs(OUT, exist_ok=True)
    sets = grid()
    jobs = [(nm, pd, ds) for nm, pd in sets for ds in ("H1", "H2")]
    jobs += [(nm, pd, "G748") for nm, pd in sets]
    base_pd = asdict(CHOSEN)
    for ds in ("H1_M5", "H2_M5", "H1_M15", "H2_M15", "G748_M5", "G748_M15"):
        jobs.append(("base", base_pd, ds))
    with Pool(min(18, os.cpu_count() or 4), initializer=_init) as pool:
        rows = []
        for i, r in enumerate(pool.imap_unordered(_job, jobs)):
            rows.append(r)
            print(f"[{i + 1}/{len(jobs)}] {r[0]} {r[1]}", flush=True)
    with open(os.path.join(OUT, "grid.json"), "w", encoding="utf-8") as f:
        json.dump([dict(name=a, ds=b, params=c, m=d) for a, b, c, d in rows], f, ensure_ascii=False, indent=1)


def events_90d():
    bars = load_bars(F90)
    eng = RangeEngine(CHOSEN, TICK)
    for (_, o, h, l, c) in bars:
        eng.feed(o, h, l, c)
    write_events(os.path.join(HERE, "events_90d.csv"), eng, bars)
    print(len(eng.ranges), "range,", len(eng.events), "sự kiện → events_90d.csv")




def report():
    """In bảng Markdown từ measure_out/grid.json (dán vào MEASURE.md)."""
    rows = json.load(open(os.path.join(OUT, "grid.json"), encoding="utf-8"))
    d = {(r["name"], r["ds"]): r["m"] for r in rows}
    names = []
    for r in rows:
        if r["name"] not in names:
            names.append(r["name"])
    names.sort(key=lambda x: (x != "base", x))
    cols = [("per_day", "range/ngày"), ("h_med", "cao trung vị (tick)"), ("w1_med", "lõi tới phá đầu (nến)"),
            ("h_mean_med", "cao/biên độ nến TB"), ("hunt_per", "râu quét/range"), ("fail_per", "fail/range"),
            ("brk_per", "phá thật/range"), ("n_fail", "số fail"), ("p_opp_before_break", "P chạm cạnh đối diện trước phá"),
            ("R_med", "R trung vị"), ("share_R17", "tỷ lệ R≥1,7"), ("win_R17", "thắng (R≥1,7)"),
            ("breakeven_R17", "hoà vốn cần"), ("EV_R17_gross", "EV R≥1,7 (R)"), ("EV_R17_net2t", "EV sau 2 tick phí"),
            ("p_break_1h", "P đi ≥1× cao sau phá")]
    print("| bộ | dữ liệu | " + " | ".join(c[1] for c in cols) + " |")
    print("|" + "---|" * (len(cols) + 2))
    def row(nm, ds):
        m = d.get((nm, ds))
        if m:
            print(f"| {nm} | {ds} | " + " | ".join("" if m.get(c) is None else str(m.get(c)) for c, _ in cols) + " |")
    for nm in names:
        for ds in ("H1", "H2", "G748"):
            row(nm, ds)
    for ds in ("H1_M5", "H2_M5", "G748_M5", "H1_M15", "H2_M15", "G748_M15"):
        row("base", ds)


if __name__ == "__main__":
    if "--events" in sys.argv:
        events_90d()
    elif "--report" in sys.argv:
        report()
    else:
        main()
