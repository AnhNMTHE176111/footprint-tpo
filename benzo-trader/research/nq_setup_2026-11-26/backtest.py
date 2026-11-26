# -*- coding: utf-8 -*-
"""Backtest tháng kiểm tra (SPEC mục 4): 2026-10-26 → hết dữ liệu. Chạy MỘT lần, không chỉnh số sau khi xem.
Ra: trades_test.csv, KET-QUA-THANG-KIEM-TRA.md"""
import csv, os, random, statistics as st
from collections import defaultdict
from nq_setup import *

TEST_FROM = datetime(2026, 10, 26, tzinfo=timezone.utc)
START = datetime(2026, 9, 14, tzinfo=timezone.utc)


def run(cfg=None):
    m = Machine(BARS, SIG, cfg); m.run(TEST_FROM); return m


def stats(rs, trades=None, b=None):
    n = len(rs)
    if n == 0:
        return dict(n=0)
    wins = sum(1 for r in rs if r > 0)
    cum = pk = dd = 0.0; streak = mx = 0
    for r in rs:
        cum += r; pk = max(pk, cum); dd = max(dd, pk - cum)
        streak = streak + 1 if r <= 0 else 0; mx = max(mx, streak)
    return dict(n=n, wr=wins / n, avg=sum(rs) / n, tot=sum(rs), streak=mx, dd=dd)


def fmt(s):
    if s["n"] == 0:
        return "0 | – | – | – | – | –"
    return f"{s['n']} | {s['wr']*100:.0f} % | {s['avg']:+.3f} | {s['tot']:+.1f} | {s['streak']} | {s['dd']:.1f}"


def random_control(m, trades, pool=200, sets=1000, seed=7):
    """Mỗi lệnh thật: 200 lệnh ngẫu nhiên cùng hướng / khoảng SL-TP / phí / luật cuối phiên, vào ở Open một nến M1
    trong cùng giờ NY ±30 phút của ngày giao dịch bất kỳ trong tháng kiểm tra."""
    b = m.b; rnd = random.Random(seed)
    cand_by_min = defaultdict(list)
    for k in range(1, len(b.t) - 1):
        if b.t[k] < TEST_FROM or (b.t[k] - b.t[k - 1]) > timedelta(minutes=5):
            continue
        n = ny(b.t[k]); hm = (n.hour, n.minute)
        if CFG["NO_ENTRY_NY"] <= hm < (18, 0):
            continue
        cand_by_min[n.hour * 60 + n.minute].append(k)
    pools = []
    for t in trades:
        n = ny(b.t[t.sig + 1]); mm = n.hour * 60 + n.minute
        ks = [k for d in range(-30, 31) for k in cand_by_min.get((mm + d) % 1440, [])]
        rs = []
        for _ in range(pool):
            k = rnd.choice(ks); e = b.o[k]
            sl = e - t.side * t.dist; tp = e + t.side * CFG["RR_TP"] * t.dist
            _, px, _ = simulate(b, k, t.side, e, sl, tp, CFG)
            rs.append(((px - e) * t.side - CFG["COST"]) / t.dist)
        pools.append(rs)
    means = []
    for _ in range(sets):
        means.append(sum(rnd.choice(p) for p in pools) / len(pools))
    means.sort()
    return means


def pct_of(x, dist):
    return sum(1 for v in dist if v < x) / len(dist)


if __name__ == "__main__":
    BARS, SIG = build(START)
    V = os.environ.get("NQ_VER", "3")
    BASE = dict(VERSIONS[V])
    _run = run
    run = lambda cfg=None: _run({**BASE, **(cfg or {})})
    main = run()
    T = main.trades
    days = sorted({trade_day(t) for t in BARS.t if t >= TEST_FROM})
    out = []
    w = out.append
    w("# Kết quả backtest tháng kiểm tra — chuẩn setup CORVEN NQ M1")
    w("")
    w(f"- Dữ liệu: NQZ26 M1, tháng kiểm tra {days[0]} → {days[-1]} ({len(days)} ngày giao dịch). Máy trạng thái chạy từ 2026-09-14.")
    w("- Spec: [SPEC-SETUP-NQ.md](SPEC-SETUP-NQ.md), chốt trước khi chạy; chạy một lần, không chỉnh số sau khi xem.")
    if V == "2":
        w("- **Bản 2** (người học 2026-11-26, sau khi xem bản 1): bỏ Fail Break, chỉ còn Break và Test vùng stacked (follow trend). "
          "Quyết định này có sau khi đã nhìn tháng kiểm tra ⇒ số dưới đây **không còn là kiểm tra mù**; cần dữ liệu mới (sau 25/11) để kiểm.")
    if V == "3":
        w("- **Bản 3** (người học 2026-11-26): Break + Follow trend = theo move đang đi (không cần vùng stacked: move ≥ 2 × mbr trong 30 nến, "
          "hồi 1–10 nến, không sâu quá 50 % move); **bỏ bias phiên**. Có sau khi đã nhìn tháng kiểm tra ⇒ **không còn là kiểm tra mù**.")
    w(f"- Chi phí {CFG['COST']} điểm/lệnh; cùng nến chạm SL và TP tính SL; đóng lệnh 16:59 NY.")
    w("")
    w("## Tổng")
    w("")
    w("| Nhóm | Lệnh | WR | R/lệnh sau phí | Tổng R | Chuỗi thua dài nhất | Sụt giảm lớn nhất (R) |")
    w("|---|---|---|---|---|---|---|")
    w(f"| Tất cả | {fmt(stats([t.r for t in T]))} |")
    w(f"| (trước phí) | {fmt(stats([t.r_gross for t in T]))} |")
    def grp(name, keyf):
        g = defaultdict(list)
        for t in T:
            for k in keyf(t):
                g[k].append(t.r)
        for k in sorted(g):
            w(f"| {name}: {k} | {fmt(stats(g[k]))} |")
    grp("Loại", lambda t: [t.kind])
    grp("Phiên", lambda t: [{"A": "Á", "E": "Âu", "U": "Mỹ"}[t.session]])
    grp("Hướng", lambda t: ["buy" if t.side > 0 else "sell"])
    grp("Tín hiệu thứ hai", lambda t: t.second.split("+") if t.second else ["(không)"])
    grp("Mốc lớn", lambda t: [t.big])
    grp("Bias", lambda t: ["có bias" if t.bias != "chưa có" else "chưa có bias"])
    w("")
    nd = len(days)
    w(f"- Lệnh/ngày: {len(T)/nd:.2f}. Khoảng SL trung vị: {st.median([t.dist for t in T]) if T else 0:.2f} điểm. "
      f"Thời gian giữ trung vị: {st.median([t.exit_i - t.sig for t in T]) if T else 0:.0f} nến. "
      f"Kết cục: TP {sum(t.how=='TP' for t in T)} · SL {sum(t.how=='SL' for t in T)} · đóng cuối phiên {sum(t.how=='TIME' for t in T)}.")
    w("")
    # đối chứng ngẫu nhiên
    w("## Đối chứng vào ngẫu nhiên (200 lệnh / lệnh thật, 1.000 bộ)")
    w("")
    w("| Nhóm | Lệnh | R/lệnh thật | Ngẫu nhiên trung vị | Ngẫu nhiên phần trăm 95 | Vị trí của lệnh thật |")
    w("|---|---|---|---|---|---|")
    for name, sel in [("Tất cả", T)] + [(k, [t for t in T if t.kind == k]) for k in sorted({t.kind for t in T})]:
        if not sel:
            w(f"| {name} | 0 | – | – | – | – |"); continue
        dist = random_control(main, sel)
        real = sum(t.r for t in sel) / len(sel)
        w(f"| {name} | {len(sel)} | {real:+.3f} | {dist[len(dist)//2]:+.3f} | {dist[int(len(dist)*.95)]:+.3f} | {pct_of(real, dist)*100:.0f} % |")
    w("")
    # cột phụ
    w("## Cột phụ (chốt trước, chỉ tham khảo, không dùng để chọn)")
    w("")
    w("| Biến thể | Lệnh | WR | R/lệnh sau phí | Tổng R | Chuỗi thua | Sụt giảm (R) |")
    w("|---|---|---|---|---|---|---|")
    w(f"| TP 4R (cùng lệnh) | {fmt(stats([t.r4 for t in T]))} |")
    w(f"| Chi phí 1,5 điểm (cùng lệnh) | {fmt(stats([(t.r_gross*t.dist-1.5)/t.dist for t in T]))} |")
    nb = run(dict(USE_BIAS=not BASE.get("USE_BIAS", CFG["USE_BIAS"]))).trades
    w(f"| {'Không lọc' if BASE.get('USE_BIAS', CFG['USE_BIAS']) else 'Có lọc'} bias | {fmt(stats([t.r for t in nb]))} |")
    nd_ = run(dict(USE_D=False)).trades
    w(f"| Bỏ tầng xác nhận order flow (luật 15–18) | {fmt(stats([t.r for t in nd_]))} |")
    w("")
    # ứng viên bị loại
    g = defaultdict(int)
    for c in main.cands:
        for x in c[3].split(";"):
            if x: g[(c[1], x)] += 1
    w("## Ứng viên bị loại theo cổng (một ứng viên có thể trượt nhiều cổng)")
    w("")
    w("| Loại | Cổng | Số lần |"); w("|---|---|---|")
    for (k, x), v in sorted(g.items(), key=lambda z: (z[0][0], -z[1])):
        w(f"| {k} | {x} | {v} |")
    open(os.path.join(HERE, "KET-QUA-THANG-KIEM-TRA.md" if V == "1" else f"KET-QUA-THANG-KIEM-TRA-ban{V}.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    with open(os.path.join(HERE, "trades_test.csv" if V == "1" else f"trades_test_ban{V}.csv"), "w", newline="", encoding="utf-8") as f:
        cw = csv.writer(f)
        cw.writerow(["signal_utc", "entry_utc", "kind", "side", "entry", "sl", "tp", "sl_pts", "second", "bias", "big", "big_levels",
                     "session", "exit_utc", "exit", "how", "r_gross", "r", "r_tp4", "note"])
        for t in T:
            cw.writerow([BARS.key[t.sig], BARS.key[t.sig + 1], t.kind, "buy" if t.side > 0 else "sell", t.entry, round(t.sl, 2),
                         round(t.tp, 2), round(t.dist, 2), t.second, t.bias, t.big, t.big_lv, t.session, BARS.key[t.exit_i],
                         t.exit_px, t.how, round(t.r_gross, 3), round(t.r, 3), round(t.r4, 3), t.note])
    print("\n".join(out[:40]))
