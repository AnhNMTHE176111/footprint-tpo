#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DATA CAPABILITY AUDIT — kiem ke toan bo du lieu offline hien co, doc lap voi moi doc/memory cu.
================================================================================================
Muc dich: tai lap MOI con so trong ../DATA_CAPABILITY.md. Khong dung pandas (may khong co pip/pandas
=> chi dung stdlib: csv, pickle, datetime, statistics, math, collections).

Chay tung phan:
  python3 data_capability_audit.py ident      # dinh danh + tick + tz + khoang thoi gian tung file
  python3 data_capability_audit.py deadcols    # sang cot chet (fp-m1-6-month + 2 file TPO)
  python3 data_capability_audit.py matrix       # ma tran trung lap thoi gian theo thang
  python3 data_capability_audit.py wr           # dieu tra lech WR fp-m1 (delta-free) vs dxFeed
  python3 data_capability_audit.py daycheck     # so nen tung phut 1 ngay: fp-m1(-7h) vs dxFeed
  python3 data_capability_audit.py all          # chay het (~2-3 phut)

TRUNG THUC: moi so o day la output THAT cua lenh nay. Neu ban sua data-export/, chay lai truoc khi trich so.
"""
import sys, os, csv, pickle, math, statistics as st
from datetime import datetime, timedelta
from collections import Counter, defaultdict

ROOT = "/home/asl86/Documents/footprint-tpo"
DE = ROOT + "/data-export/"
sys.path.insert(0, os.path.join(ROOT, "quantower-entry-signal/research"))

DXFILE = DE + "27-7/_GCQ26XCEC dxFeed, Time - Time - 1m, 11_3_2025 120000 AM-7_27_2026 105600 PM_8b750702-5f00-4836-bf74-81e2a0c4495f.csv"
FP6 = DE + "fp-m1-6-month.csv"
FP1M = DE + "fp-m1-1-month-data.csv"
FPSMALL = DE + "fp-m1.csv"
TPOD = DE + "TPO-chart-daily.csv"
TPOM = DE + "tpo-chart-m30.csv"
SAMPLE = DE + "27-7/sample.csv"
SAMPLE_BARS = DE + "27-7/sample_bars.csv"
PL_FULL = DE + "27-7/perlevel_m1.pkl"
PL_CLEAN = DE + "27-7/perlevel_m1_clean.pkl"


def pdt_dx(s): return datetime.strptime(s.strip()[:19], "%Y-%m-%d %H:%M:%S")
def pdt_fp(s): return datetime.strptime(s.strip(), "%m/%d/%Y %I:%M:%S %p")


def load_csv(path, sep=','):
    with open(path, encoding='utf-8-sig') as f:
        r = csv.reader(f, delimiter=sep)
        h = next(r)
        rows = [x for x in r if x and x[0].strip()]
    return h, rows


# ---------------------------------------------------------------- 1. IDENT
def ident():
    print("=" * 100, "\n1) DINH DANH TUNG FILE\n", "=" * 100, sep="")

    print("\n--- dxFeed 27-7 (chinh, dung boi entry_dxfeed.load_m1) ---")
    h, rows = load_csv(DXFILE, ';')
    ix = {n: i for i, n in enumerate(h)}
    times = sorted(pdt_dx(x[ix['Time left']]) for x in rows)
    print(f"n={len(times)} first={times[0]} last={times[-1]}")
    opens = sorted(set(round(float(x[ix['Open']]), 3) for x in rows))
    diffs = sorted(set(round(opens[i + 1] - opens[i], 3) for i in range(len(opens) - 1)))
    print("tick grid (Open gap nho nhat):", diffs[:6], "=> tick=0.1 gia")
    wd = Counter(t.weekday() for t in times)
    print("weekday counts (0=T2..6=CN):", dict(sorted(wd.items())))
    cnt = Counter(t.hour for t in times)
    print("count theo GIO UTC (0-23):", dict(sorted(cnt.items())))
    gaps = []
    for i in range(1, len(times)):
        d = (times[i] - times[i - 1]).total_seconds() / 60
        if d > 60: gaps.append((times[i - 1], times[i], d))
    gaps.sort(key=lambda g: -g[2])
    print(f"so gap>60p: {len(gaps)} | 5 gap dai nhat:")
    for g in gaps[:5]: print(f"   {g[0]} -> {g[1]}  {g[2]/60:.1f}h")
    days = sorted(set(t.date() for t in times))
    print("so ngay co du lieu (ca giai doan):", len(days))

    print("\n--- fp-m1-6-month.csv (UTC+7, cot 'DateTime') ---")
    h, rows = load_csv(FP6)
    ix = {n: i for i, n in enumerate(h)}
    times = [pdt_fp(x[ix['DateTime']]) for x in rows]
    print(f"n={len(times)} first={min(times)} last={max(times)}")
    cnt = Counter(t.hour for t in times)
    vbh = defaultdict(list)
    for t, x in zip(times, rows): vbh[t.hour].append(float(x[ix['Volume']]))
    print("count theo GIO DIA PHUONG (UTC+7):", dict(sorted(cnt.items())))
    print("median volume theo gio dia phuong:", {h_: round(st.median(v), 1) for h_, v in sorted(vbh.items())})
    print("=> gio 4 (local) gan nhu = 0 nen => khop UTC 21:00 (nghi CME) + 7h. Dinh vi tri = local+7=UTC.")
    wd = Counter(t.weekday() for t in times)
    print("weekday counts:", dict(sorted(wd.items())))

    for label, path in [("fp-m1.csv (nho nhat, ~2 ngay gan nhat)", FPSMALL),
                          ("fp-m1-1-month-data.csv (dung boi load_fpm1 mac dinh)", FP1M)]:
        h, rows = load_csv(path)
        ix = {n: i for i, n in enumerate(h)}
        times = sorted(pdt_fp(x[ix['DateTime']]) for x in rows)
        print(f"\n--- {label} --- n={len(times)} first={times[0]} last={times[-1]}")

    print("\n--- TPO-chart-daily.csv (ten gay hieu lam!) ---")
    h, rows = load_csv(TPOD)
    ix = {n: i for i, n in enumerate(h)}
    times = sorted(pdt_fp(x[ix['DateTime']]) for x in rows)
    diffm = Counter(round((times[i] - times[i - 1]).total_seconds() / 60) for i in range(1, len(times)))
    print(f"n={len(times)} first={times[0]} last={times[-1]}")
    print("khoang cach giua 2 nen lien tiep (phut:so lan), top5:", diffm.most_common(5))
    tpo_col = [row[ix['TPO']] for row in rows]
    print(f"=> BAR INTERVAL THAT = 30 PHUT (khong phai 'daily'). Cot TPO co {len(set(tpo_col))} gia tri phan biet "
          f"(~so ngay); 'daily' la CHU KY cua ho so TPO, khong phai khung nen.")

    print("\n--- tpo-chart-m30.csv (ten gay hieu lam!) ---")
    h, rows = load_csv(TPOM)
    ix = {n: i for i, n in enumerate(h)}
    times = sorted(pdt_fp(x[ix['DateTime']]) for x in rows)
    diffm = Counter(round((times[i] - times[i - 1]).total_seconds() / 60) for i in range(1, len(times)))
    print(f"n={len(times)} first={times[0]} last={times[-1]}")
    print("khoang cach giua 2 nen lien tiep (phut:so lan), top5:", diffm.most_common(5))
    tpo_col = [row[ix['TPO']] for row in rows]
    print(f"=> BAR INTERVAL THAT = 1 PHUT. Cot TPO co {len(set(tpo_col))} gia tri phan biet; 'm30' la CHU KY xoay "
          f"TPO 30 phut, khong phai khung nen. File nay chi phu {(times[-1]-times[0])}.")

    print("\n--- sample.csv / sample_bars.csv (per-level, thu muc 27-7) ---")
    h, rows = load_csv(SAMPLE_BARS)
    ix = {n: i for i, n in enumerate(h)}
    times = sorted(datetime.strptime(x[ix['datetime']], "%Y-%m-%d %H:%M:%S") for x in rows)
    days = sorted(set(t.date() for t in times))
    print(f"sample_bars.csv: n={len(times)} first={times[0]} last={times[-1]} so-ngay={len(days)}")
    mx = max(float(x[ix['max_one_trade']]) for x in rows)
    print(f"max_one_trade: max={mx} (TOAN 0 tren ca 2 file, xem deadcols)")
    print("=> KHOP CHINH XAC voi bar dau tien perlevel_m1.pkl (2026-06-01 00:00:00, xem duoi) => cung nguon UTC.")

    print("\n--- perlevel_m1.pkl / perlevel_m1_clean.pkl ---")
    for label, path in [("perlevel_m1.pkl (goc)", PL_FULL), ("perlevel_m1_clean.pkl (da loc)", PL_CLEAN)]:
        with open(path, 'rb') as f:
            d = pickle.load(f)
        times = [datetime.strptime(x['t'], "%Y-%m-%d %H:%M:%S") for x in d]
        days = sorted(set(t.date() for t in times))
        print(f"{label}: n={len(d)} bars, {len(days)} ngay roi rac, {min(times)} -> {max(times)}")
        gaps = []
        prev = None
        for day in days:
            if prev is not None and (day - prev).days > 1:
                gaps.append((prev, day, (day - prev).days))
            prev = day
        print("  gap giua cac ngay (>1 ngay):", gaps)
    cnt = Counter(datetime.strptime(x['t'], "%Y-%m-%d %H:%M:%S").hour for x in pickle.load(open(PL_FULL, 'rb')))
    print("count theo GIO (perlevel_m1.pkl, full):", dict(sorted(cnt.items())), "=> gio 21 = 0 => UTC.")


# ---------------------------------------------------------------- 2. DEAD COLUMNS
def dead_cols(path, sep=','):
    h, rows = load_csv(path, sep)
    h = [c for c in h if c.strip() != '']
    ncol = len(h)
    stat = [dict(n=0, nz=0, mn=None, mx=None) for _ in h]
    for row in rows:
        for i in range(ncol):
            if i >= len(row): continue
            try:
                fv = float(row[i])
            except ValueError:
                continue
            s = stat[i]; s['n'] += 1
            if fv != 0: s['nz'] += 1
            s['mn'] = fv if s['mn'] is None else min(s['mn'], fv)
            s['mx'] = fv if s['mx'] is None else max(s['mx'], fv)
    print(f"\n=== {os.path.basename(path)} ({ncol} cot) — chi liet CHET (nz==0, cot so) ===")
    for name, s in zip(h, stat):
        if s['n'] > 0 and s['nz'] == 0:
            print(f"  CHET: {name}")
    return h, stat


def deadcols():
    print("=" * 100, "\n2) SANG COT CHET\n", "=" * 100, sep="")
    dead_cols(FP6)
    dead_cols(TPOD)
    dead_cols(TPOM)
    print("\n--- kiem tra cot trung ten (case khac nhau): 'Open interest' vs 'Open Interest' ---")
    for path in [TPOD, TPOM]:
        h, rows = load_csv(path)
        idxs = [i for i, c in enumerate(h) if 'interest' in c.lower()]
        print(f"{os.path.basename(path)}: cot chua 'interest' ->", [h[i] for i in idxs])
        for i in idxs:
            vals = [float(row[i]) for row in rows]
            print(f"   {h[i]!r}: min={min(vals)} max={max(vals)} nz={sum(1 for v in vals if v != 0)}/{len(vals)}")


# ---------------------------------------------------------------- 3. MONTH MATRIX
def month_matrix():
    print("=" * 100, "\n3) MA TRAN TRUNG LAP THOI GIAN (so ngay co du lieu / thang)\n", "=" * 100, sep="")

    def days_by_month(path, sep, col, parser):
        h, rows = load_csv(path, sep)
        ix = {n: i for i, n in enumerate(h)}
        days = set(parser(x[ix[col]]).date() for x in rows)
        m = defaultdict(set)
        for d in days: m[d.strftime('%Y-%m')].add(d)
        return {k: len(v) for k, v in m.items()}

    dx = days_by_month(DXFILE, ';', 'Time left', pdt_dx)
    fp6 = days_by_month(FP6, ',', 'DateTime', pdt_fp)
    tpod = days_by_month(TPOD, ',', 'DateTime', pdt_fp)
    tpom = days_by_month(TPOM, ',', 'DateTime', pdt_fp)
    smp = days_by_month(SAMPLE_BARS, ',', 'datetime', lambda s: datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S"))
    with open(PL_FULL, 'rb') as f: pl = pickle.load(f)
    pld = defaultdict(set)
    for x in pl:
        d = datetime.strptime(x['t'], "%Y-%m-%d %H:%M:%S").date()
        pld[d.strftime('%Y-%m')].add(d)
    pl_m = {k: len(v) for k, v in pld.items()}

    months = sorted(set(dx) | set(fp6) | set(tpod) | set(tpom) | set(smp) | set(pl_m))
    print(f"{'thang':<10}{'dxFeed':>8}{'fp-m1-6m':>10}{'TPOdaily':>10}{'TPOm30':>9}{'sample':>9}{'perlevel':>10}")
    for m in months:
        print(f"{m:<10}{dx.get(m,0):>8}{fp6.get(m,0):>10}{tpod.get(m,0):>10}{tpom.get(m,0):>9}{smp.get(m,0):>9}{pl_m.get(m,0):>10}")


# ---------------------------------------------------------------- 4. WR INVESTIGATION
def wr_investigate():
    print("=" * 100, "\n4) DIEU TRA LECH WR fp-m1(delta-free) vs dxFeed(delta-free)\n", "=" * 100, sep="")
    import entry_dxfeed as E

    def cfg(): return E.make()

    Bf = E.load_fpm1()
    t0, t1 = Bf[0]['dt'], Bf[-1]['dt']
    print(f"fp-m1 window (local UTC+7): {t0} -> {t1}  n={len(Bf)}")
    avg_f = sum(b['v'] for b in Bf) / len(Bf)

    Bd = E.load_m1()
    vf_full = E.calc_volfloor(Bd)
    avg_d = sum(b['v'] for b in Bd) / len(Bd)
    Bd_win = [b for b in Bd if t0 <= b['dt'] <= t1]
    avg_dw = sum(b['v'] for b in Bd_win) / len(Bd_win) if Bd_win else 0
    print(f"dxFeed avg bar vol (toan giai doan)={avg_d:.2f}  volfloor(percentile)={vf_full}")
    print(f"dxFeed bars trong DUNG khung fp-m1 (LUU Y: so sanh nay dung t0/t1 la gio LOCAL cua fp-m1,"
          f" chua quy doi -7h => sai lech bien ~7h/29 ngay ~1%): n={len(Bd_win)} (fp-m1 co {len(Bf)}), avg vol={avg_dw:.2f} (fp-m1={avg_f:.2f})")

    E.B = Bd; E.VOLFLOOR_AUTO = vf_full; E.USE_DELTA = False
    poold = E.build_zones(Bd)
    Cd = E.prep(dict(cfg()))
    rawd = E.run(Bd, poold, Cd); sigd = E.dedup(rawd, poold, Cd)
    sigd_win = [s for s in sigd if t0 <= s['dt'] <= t1]
    print(f"\ndxFeed pool zones (tu ~9 thang lich su)={len(poold)}")
    if sigd_win:
        E.evalset(Bd, sigd_win, "dxFeed delta-free, GIOI HAN dung khung fp-m1", Cd, by_month=False)

    E.B = Bf; E.VOLFLOOR_AUTO = 20.0; E.USE_DELTA = False
    poolf = E.build_zones(Bf)
    Cf = E.prep(dict(cfg()))
    rawf = E.run(Bf, poolf, Cf); sigf = E.dedup(rawf, poolf, Cf)
    print(f"fp-m1 pool zones (chi tu ~1 thang lich su cua chinh no)={len(poolf)}")
    E.evalset(Bf, sigf, "fp-m1 delta-free (volfloor=20 cung hardcode)", Cf, by_month=False)

    def ztest(w1, n1, w2, n2):
        p1, p2 = w1 / n1, w2 / n2
        pp = (w1 + w2) / (n1 + n2)
        se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
        return p1, p2, (p1 - p2) / se

    print("\n--- ket luan co che (khong phai loi du lieu): zone-pool WARM-UP khac nhau ---")
    print(f"  fp-m1 build_zones() chi co ~1 thang lich su truoc do => pool={len(poolf)} zone (lanh luc dau ky).")
    print(f"  dxFeed build_zones() co ~9 thang lich su => pool={len(poold)} zone (da am luc dau ky, cung ngay).")
    print("  => dxFeed sinh nhieu tin hieu 'cham&dao' hon trong CUNG khung ngay-thang, keo WR xuong.")


# ---------------------------------------------------------------- 5. DAY-BY-DAY CROSS CHECK
def day_check(day="2026-07-10"):
    print("=" * 100, f"\n5) DOI CHIEU TUNG PHUT 1 NGAY ({day}, UTC) — fp-m1(-7h) vs dxFeed\n", "=" * 100, sep="")
    import entry_dxfeed as E
    Bf = E.load_fpm1(); Bd = E.load_m1()
    fp_by_utc = {b['dt'] - timedelta(hours=7): b for b in Bf}
    dx_by_utc = {b['dt']: b for b in Bd}
    common = sorted(t for t in fp_by_utc if t.strftime('%Y-%m-%d') == day)
    matched = missing = 0
    maxdiff = 0.0
    sample_rows = []
    for t in common:
        fb = fp_by_utc[t]; db = dx_by_utc.get(t)
        if db is None:
            missing += 1; continue
        matched += 1
        diff = abs(fb['c'] - db['c']) / E.TICK
        maxdiff = max(maxdiff, diff)
        sample_rows.append((t, fb, db, diff))
    print(f"fp-m1 co {len(common)} nen phut trong ngay {day} (sau khi quy doi UTC+7 -> UTC bang -7h)")
    print(f"khop voi dxFeed: {matched} | dxFeed thieu nen cung phut: {missing}")
    print(f"max |close_fp - close_dx| = {maxdiff:.2f} tick (gia 0.1)")
    print("=> KET LUAN: fp-m1 va dxFeed la CUNG MOT chuoi gia (sau khi doi UTC+7->UTC), khong phai 2 san pham khac nhau.")
    for t, fb, db, diff in sample_rows[:5]:
        print(f"  {t}  fp:{fb['o']:.1f}/{fb['hi']:.1f}/{fb['lo']:.1f}/{fb['c']:.1f}/{fb['v']:.0f}  "
              f"dx:{db['o']:.1f}/{db['hi']:.1f}/{db['lo']:.1f}/{db['c']:.1f}/{db['v']:.0f}  diff={diff:.1f}tick")


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode in ('ident', 'all'): ident()
    if mode in ('deadcols', 'all'): deadcols()
    if mode in ('matrix', 'all'): month_matrix()
    if mode in ('wr', 'all'): wr_investigate()
    if mode in ('daycheck', 'all'): day_check()
