#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MO PHONG DUNG QUY TAC QUAN LY LENH CUA PRO TRADER (nguoi hoc cung cap 2026-07-31).
================================================================================
Nguyen van: "ngay vai chuc lenh, khung M1, RR 1:3. Cho setup du yeu to roi NHOI 5-7 lenh:
vd nhoi 5 -> 2 lenh TP 1:3 (chot nhanh chac tien), 2 lenh de chay 1:5, 1 lenh treo di xe den
diem cao nhat cua HVN NGAY hoac TUAN. Mat lenh do thi cac lenh khac da du lai. Lenh nao di
duoc 1R roi thi BE lenh lai."

CAU HOI 1 (quan trong nhat): con so "win rate 80%" nghia la gi? Voi BE-tai-1R, moi lenh co 3
ket cuc: TP / BE (hoa, khong lo) / SL. Neu dem "khong lo" la thang thi WR tu nhien rat cao MA
KHONG NOI GI VE LAI/LO. Do o day: WR_tho (chi TP) vs WR_khonglo (TP+BE) tren CUNG tap tin hieu.

CAU HOI 2: quy tac nhoi 5 lenh + BE co bien tap tin hieu AM thanh duong khong (va nguoc lai,
co lam giam R cua he dang co edge khong)?

Nguon tin hieu do song song:
  A. CBR v5 SHIPPED (cbr_v6 baseline) — he DANG CHAY, da co edge (+49R/55 lenh, RR3).
  B. CROW FADE+CONFIRM — nhanh duy nhat cua concept Crow con duong (+22R, z=1.14).
  C. CROW LOI (chase momentum) — nhanh AM (-73R) de kiem: BE co "cuu" duoc mot he am khong.
Runner (lenh thu 5): TP = D-1 High (LONG) / D-1 Low (SHORT) neu xa hon 5R, nguoc lai 8R;
  het phien (gap > 45') ma chua dat thi thoat o close (khong treo qua dem).
Bi quan nhat quan: trong CUNG nen kiem SL truoc TP; BE chi doi tu NEN SAU khi nen truoc dat 1R.

Chay: python3 crow_mgmt.py
"""
import sys, os, statistics as st
from collections import defaultdict, deque
from datetime import timedelta

R = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research"
sys.path.insert(0, R)
sys.path.insert(0, os.path.join(R, "wyckoff"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entry_dxfeed as E
import cbr_v6
import crow_v1 as K
from v7 import report

TICK = E.TICK
MONTHS = report.MONTHS
LEGS = ((2, 3.0), (2, 5.0), (1, None))     # (so lenh, RR) — None = runner den HVN ngay/tuan


def sim(B, i, side, entry, sl, tp, be_at=1.0, dead=None):
    """Tra ('TP'|'BE'|'SL'|'TO', r_theo_risk). BE => r=0. TO = thoat cuoi phien theo close."""
    risk = abs(entry - sl)
    if risk <= 0:
        return None, None
    moved = False
    cur_sl = sl
    for j in range(i + 1, len(B)):
        b = B[j]
        if (b['lo'] <= cur_sl) if side == 'LONG' else (b['hi'] >= cur_sl):
            return ('BE', 0.0) if moved else ('SL', -1.0)
        if tp is not None and ((b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp)):
            return 'TP', abs(tp - entry) / risk
        if not moved:
            reach = (b['hi'] - entry) if side == 'LONG' else (entry - b['lo'])
            if reach >= be_at * risk:
                cur_sl = entry
                moved = True
        if dead is not None and j >= dead:
            r = ((b['c'] - entry) if side == 'LONG' else (entry - b['c'])) / risk
            return 'TO', max(r, 0.0) if moved else r
    return None, None


def end_of_session(B, i):
    """Index nen cuoi phien chua nen i (gap > 45' la phien moi)."""
    for j in range(i + 1, len(B)):
        if (B[j]['dt'] - B[j - 1]['dt']) > timedelta(minutes=45):
            return j - 1
    return len(B) - 1


def prev_day_levels(B):
    """D-1 High/Low cho tung nen (chi dung phien DA DONG -> khong look-ahead)."""
    days = []
    cur = None
    for i, b in enumerate(B):
        if cur is None or (b['dt'] - B[i - 1]['dt']) > timedelta(minutes=45):
            cur = dict(i0=i, hi=b['hi'], lo=b['lo'])
            days.append(cur)
        cur['hi'] = max(cur['hi'], b['hi']); cur['lo'] = min(cur['lo'], b['lo'])
        cur['i1'] = i
    pd = [None] * len(B)
    for k in range(1, len(days)):
        d, p = days[k], days[k - 1]
        for i in range(d['i0'], d.get('i1', d['i0']) + 1):
            pd[i] = (p['hi'], p['lo'])
    return pd


def cluster(B, s, pd, be_at=1.0):
    """Mo phong 1 CUM nhoi 5 lenh tren 1 tin hieu. Tra dict thong ke cum."""
    side, entry, sl = s['side'], s['entry'], s['sl']
    risk = abs(entry - sl)
    dead = end_of_session(B, s['i'])
    out = []
    for cnt, rr in LEGS:
        if rr is not None:
            tp = entry + rr * risk if side == 'LONG' else entry - rr * risk
            dd = None
        else:
            lv = pd[s['i']]
            tgt = None
            if lv:
                tgt = lv[0] if side == 'LONG' else lv[1]
            far = entry + 8 * risk if side == 'LONG' else entry - 8 * risk
            if tgt is None or ((tgt - entry) / risk < 5 if side == 'LONG' else (entry - tgt) / risk < 5):
                tp = far
            else:
                tp = tgt
            dd = dead
        o, r = sim(B, s['i'], side, entry, sl, tp, be_at, dd)
        if o is None:
            continue
        for _ in range(cnt):
            out.append((o, r))
    if not out:
        return None
    n = len(out)
    return dict(dt=s['dt'], ym=s['ym'], legs=out, n=n,
                tp=sum(1 for o, _ in out if o == 'TP'),
                be=sum(1 for o, _ in out if o in ('BE', 'TO')),
                sl=sum(1 for o, _ in out if o == 'SL'),
                r_avg=sum(r for _, r in out) / n)


def show(tag, S, B, pd):
    """In: WR_tho / WR_khonglo o muc TUNG LENH + R/cum + WR o muc CUM."""
    C = [c for c in (cluster(B, s, pd) for s in S) if c]
    if not C:
        print(f"  {tag:<26} khong co cum"); return
    tot_legs = sum(c['n'] for c in C)
    tp = sum(c['tp'] for c in C); be = sum(c['be'] for c in C); sl = sum(c['sl'] for c in C)
    rs = [c['r_avg'] for c in C]
    win_cluster = sum(1 for c in C if c['r_avg'] > 0)
    bym = defaultdict(float)
    for c in C:
        bym[c['ym']] += c['r_avg']
    mm = " ".join(f"{m[-2:]}:{bym.get(m,0):+5.1f}" for m in MONTHS)
    print(f"  {tag:<26} cum={len(C):3d} lenh={tot_legs:4d} | "
          f"WR_tho(TP)={100*tp/tot_legs:4.1f}%  WR_KHONGLO(TP+BE)={100*(tp+be)/tot_legs:5.1f}%  "
          f"| R/cum={sum(rs)/len(rs):+.3f} tong={sum(rs):+6.1f}R  WR_cum={100*win_cluster/len(C):4.1f}% | {mm}")
    return C


def main():
    B = E.load_m1()
    vf = E.calc_volfloor(B); E.VOLFLOOR_AUTO = vf
    cbr_v6.prepare(B)
    K.prep(B)
    pd = prev_day_levels(B)
    pool = E.build_zones(B)

    print("\n===== A. CBR v5 SHIPPED (he dang chay) =====")
    SA = [s for s in cbr_v6.scan(B, cbr_v6.cfg(), vf, None) if s['ym'] in MONTHS]
    report.line("v5 goc: TP 3R cung, khong BE", SA)
    show("v5 + nhoi5 + BE 1R", SA, B, pd)

    print("\n===== B. CROW FADE+CONFIRM (nhanh duy nhat con duong) =====")
    CB = K.cfg(FADE=True, CONFIRM=True)
    SB = [s for s in K.evaluate(B, K.dedup(K.run(B, CB, pool)), CB) if s['ym'] in MONTHS]
    report.line("FADE+CONF goc: TP 2R", SB)
    show("FADE+CONF + nhoi5 + BE 1R", SB, B, pd)

    print("\n===== C. CROW LOI (nhanh AM -73R) — BE co cuu duoc he am khong? =====")
    CC = K.cfg()
    SC = [s for s in K.evaluate(B, K.dedup(K.run(B, CC, pool)), CC) if s['ym'] in MONTHS]
    report.line("LOI goc: TP 2R", SC)
    show("LOI + nhoi5 + BE 1R", SC, B, pd)

    print("\n===== D. BE_AT sweep tren v5 (BE som/muon) =====")
    for be in (0.5, 1.0, 1.5, 2.0, 99.0):
        C = [c for c in (cluster(B, s, pd, be) for s in SA) if c]
        legs = sum(c['n'] for c in C); tp = sum(c['tp'] for c in C); bee = sum(c['be'] for c in C)
        rs = [c['r_avg'] for c in C]
        lab = "khong BE" if be > 50 else f"BE tai {be}R"
        print(f"  {lab:<12} WR_tho={100*tp/legs:4.1f}%  WR_KHONGLO={100*(tp+bee)/legs:5.1f}%  "
              f"R/cum={sum(rs)/len(rs):+.3f}  tong={sum(rs):+6.1f}R")

    print("\n===== E. Phan ra tung chan (2x3R / 2x5R / 1x runner) tren v5 + BE 1R =====")
    agg = defaultdict(lambda: [0, 0, 0, 0.0])   # key -> [tp, be, sl, sum_r]
    for s in SA:
        side, entry, sl0 = s['side'], s['entry'], s['sl']
        risk = abs(entry - sl0); dead = end_of_session(B, s['i'])
        for lab, rr in (("2x TP 3R", 3.0), ("2x TP 5R", 5.0), ("1x runner HVN/8R", None)):
            if rr is not None:
                tp = entry + rr * risk if side == 'LONG' else entry - rr * risk
                dd = None
            else:
                lv = pd[s['i']]; tgt = (lv[0] if side == 'LONG' else lv[1]) if lv else None
                far = entry + 8 * risk if side == 'LONG' else entry - 8 * risk
                tp = far if (tgt is None or ((tgt - entry) / risk < 5 if side == 'LONG' else (entry - tgt) / risk < 5)) else tgt
                dd = dead
            o, r = sim(B, s['i'], side, entry, sl0, tp, 1.0, dd)
            if o is None:
                continue
            a = agg[lab]
            a[0] += (o == 'TP'); a[1] += (o in ('BE', 'TO')); a[2] += (o == 'SL'); a[3] += r
    for lab in ("2x TP 3R", "2x TP 5R", "1x runner HVN/8R"):
        tp, be, sl, sr = agg[lab]
        n = tp + be + sl
        print(f"  {lab:<18} n={n:3d}  TP={tp:3d} ({100*tp/n:4.1f}%)  BE/thoat={be:3d}  SL={sl:3d}  "
              f"| R trung binh={sr/n:+.3f}  tong={sr:+6.1f}R")


if __name__ == '__main__':
    main()


def alloc_test():
    """Thu tu do PHAN BO chan TP tren v5 (he dang co edge): nen dat bao nhieu lenh o 3R/5R/runner,
    va co nen BE khong. Moi dong = mot cach chia 5 lenh."""
    B = E.load_m1()
    vf = E.calc_volfloor(B); E.VOLFLOOR_AUTO = vf
    cbr_v6.prepare(B); K.prep(B)
    pd = prev_day_levels(B)
    SA = [s for s in cbr_v6.scan(B, cbr_v6.cfg(), vf, None) if s['ym'] in MONTHS]
    global LEGS
    plans = (("pro trader: 2x3R 2x5R 1xrunner", ((2, 3.0), (2, 5.0), (1, None))),
             ("deu: 1x2R 2x3R 1x5R 1xrunner", ((1, 2.0), (2, 3.0), (1, 5.0), (1, None))),
             ("nang runner: 1x3R 1x5R 3xrunner", ((1, 3.0), (1, 5.0), (3, None))),
             ("chi runner: 5xrunner", ((5, None),)),
             ("chi 3R: 5x3R (= v5 goc)", ((5, 3.0),)),
             ("chi 5R: 5x5R", ((5, 5.0),)),
             ("bo chot nhanh: 2x5R 3xrunner", ((2, 5.0), (3, None))))
    for be in (1.0, 99.0):
        print(f"\n--- {'BE tai 1R (nhu pro trader)' if be < 50 else 'KHONG BE'} ---")
        for lab, plan in plans:
            LEGS = plan
            C = [c for c in (cluster(B, s, pd, be) for s in SA) if c]
            legs = sum(c['n'] for c in C); tp = sum(c['tp'] for c in C); bee = sum(c['be'] for c in C)
            rs = [c['r_avg'] for c in C]
            bym = defaultdict(float)
            for c in C:
                bym[c['ym']] += c['r_avg']
            allpos = all(bym.get(m, 0) > 0 for m in MONTHS)
            print(f"  {lab:<34} WR_tho={100*tp/legs:4.1f}% WR_KHONGLO={100*(tp+bee)/legs:5.1f}% "
                  f"R/cum={sum(rs)/len(rs):+.3f} tong={sum(rs):+6.1f}R {'✓3thg' if allpos else '✗'}")
