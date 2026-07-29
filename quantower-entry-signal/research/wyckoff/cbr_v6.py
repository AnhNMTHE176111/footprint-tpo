#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WYCKOFF RUNNER v6 — engine backtest CBR co TOGGLE cho tung luat cua pro trader (CORVEN).
================================================================================
BASELINE = CBR v5 SHIPPED (RunnerSignal.cs): range 8 nen span[3.0..7.5]gia, break VSA>=2.0
  + than>=0.50, loc THUAN xu huong (close vs close 480 nen) + dung phia VWAP + thanh khoan
  (vma>=0.75*TB), retrace[60%..90%], resume than>=0.35, SL[3..7]gia neo cuc tri hoi, RR3,
  cooldown 15, dedup 6, + LOC PHIEN CHET [02,08) (CBR-only).
  Doi chieu LIVE CSV (RunnerSignal_signals.csv, 5/22->7/28): CBR sau loc phien chet
  n=81, WR 43%, +43R  (tinh tu csv; xem baseline_live()).

MOI TOGGLE = 1 luat trong data-export/messages-with-pro-trader/RULES.md.
Chay: python3 cbr_v6.py            -> baseline + tung toggle rieng le
      python3 cbr_v6.py stack      -> chong cac toggle THANG lai voi nhau
TRUNG THUC: dxFeed = proxy YEU (khong delta). Toggle can delta chi chay tren merged feed
  (6/1->7/27) => bao rieng, n nho hon, khong tron voi ket qua dxFeed.
"""
import sys, os, statistics as st
from collections import defaultdict, Counter
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_dxfeed as E

TICK = E.TICK
MONTHS = ('2026-05', '2026-06', '2026-07')

# ---------------------------------------------------------------- config
def cfg(**kw):
    c = dict(
        # --- cau truc v5 (KHONG doi tru khi toggle) ---
        RANGE_LEN=8, RMIN=30, RMAX=75, BVSA=2.0, BBODY=0.50,
        WAIT=12, PMIN=0.60, PMAX=0.90, HOLD_TOL=2, RBODY=0.35,
        FLOOR=30, CAP=70, BUF=2, COOL=15, RR=3.0,
        TREND=True, VWAP=True, LIQ=True, LIQ_K=0.75,
        DEAD=True, DEAD_FROM=2, DEAD_TO=8,

        # --- W3a (GIA THUYET BAN DAU, DA BAC BO): bat buoc co PHA HUT truoc break ---
        PHASE_C=False, PC_LOOK=20, PC_W=5, PC_CLOSE=0.50,

        # --- W3b (LUAT DUOC CHAP NHAN): BREAK SACH = KHONG co quet nguoc gan do ---
        CLEAN=False, CL_LOOK=20, CL_W=5, CL_CLOSE=0.50,

        # --- R7: bop SL (2-4 gia) + neo duoi cay M1 vao lenh ---
        SL_MODE='pull',      # 'pull' = cuc tri nhip hoi (v5) | 'bar' = duoi cay entry | 'min' = chat hon trong 2
        # (FLOOR/CAP dat rieng khi test R7)

        # --- R9: chat luong nen thuan huong trong leg ---
        LEGQ=False, LEGQ_MIN=0.50, LEGQ_CPOS=0.55, LEGQ_WICK=0.35,

        # --- R3: loai leg do quet stoploss (spike roi tat) ---
        NOSTOP=False, NOSTOP_VSA=3.0, NOSTOP_CPOS=0.55,

        # --- R6: chon phien ---
        SESS=None,           # None = tat ca; hoac set gio duoc phep, vd set(range(8,19))

        # --- R1: leg phai do lenh CHU DONG day (CAN merged feed co delta) ---
        AGGR=False, AGGR_MIN=0.05,
    )
    c.update(kw)
    return c


# ---------------------------------------------------------------- parity prep
# BA LOI PARITY da phat hien & sua (2026-07-29). Doc ky truoc khi sua tiep:
#  (1) entry_dxfeed.load_m1 tinh b['trend'] voi tol=0, C# dung TrendTolPts=1.0 gia -> tinh lai.
#  (2) 'avg_vma toan chuoi' = LOOK-AHEAD. C# dung TB volume CUON LiquidityWindow=1000 nen TRUOC
#      (khong gom nen nay) roi so vma/TB >= 0.75 -> tinh b['liqratio'] cuon.
#  (3) Gate trend/VWAP/liquidity phai ap o NEN VAO (bj), KHONG phai nen pha (b) — khop C#:570.
TREND_LB, TREND_TOL, LIQ_WIN = 480, 1.0, 1000

def prepare(B):
    """Tinh lai trend (co tol) + liqratio (cuon) cho khop RunnerSignal.cs. GOI TRUOC khi scan."""
    for i, b in enumerate(B):
        if i >= TREND_LB:
            d = b['c'] - B[i - TREND_LB]['c']
            b['trend'] = 1 if d > TREND_TOL else (-1 if d < -TREND_TOL else 0)
        else:
            b['trend'] = 0
    from collections import deque
    q = deque(); tot = 0.0
    for b in B:
        mean = (tot / len(q)) if q else b['v']
        b['liqratio'] = (b['vma'] / mean) if mean > 1e-9 else 1.0
        q.append(b['v']); tot += b['v']
        if len(q) > LIQ_WIN: tot -= q.popleft()
    return B

# ---------------------------------------------------------------- helpers
def _gate(b, vf):
    return b['v'] >= vf and b['since_gap'] >= E.WARMUP_AFTER_GAP and b['vma'] >= vf * 0.6

def _phase_c(B, i, up, C):
    """W3 — trong PC_LOOK nen truoc nen break, phai co >=1 cu PHA HUT canh DOI DIEN:
    LONG  -> co nen quet xuong duoi day cuc bo (PC_W nen truoc no) roi DONG lai tren day do
             + dong o nua tren than nen  (spring / shakeout).
    SHORT -> guong lai (upthrust).
    Day chinh la 'dung danh UT som, sang D moi danh': cu pha dau tien phai la cu HUT."""
    lo_k = max(E.VSA_MA, i - C['PC_LOOK'])
    for k in range(lo_k + C['PC_W'], i):
        b = B[k]
        if b['rng'] <= 0:
            continue
        w = B[k - C['PC_W']:k]
        if not w:
            continue
        if up:
            loc = min(x['lo'] for x in w)
            if b['lo'] < loc - TICK and b['c'] > loc and b['cpos'] >= C['PC_CLOSE']:
                return True
        else:
            loc = max(x['hi'] for x in w)
            if b['hi'] > loc + TICK and b['c'] < loc and b['cpos'] <= 1 - C['PC_CLOSE']:
                return True
    return False

def counter_sweep(B, i, up, look, w, cl):
    """Trong `look` nen TRUOC nen pha (i), co cu QUET HUT canh DOI DIEN khong?
    LONG  -> co nen dam thung day cuc bo (thap nhat `w` nen ngay truoc no) roi DONG lai TREN day do
             va dong o nua tren than nen  => that bai o phia duoi = thi truong dang xoay 2 chieu.
    SHORT -> guong lai. Chi doc nen truoc i => KHONG nhin trom tuong lai."""
    lo_k = max(E.VSA_MA, i - look)
    for k in range(lo_k + w, i):
        b = B[k]
        if b['rng'] <= 0 or k - w < 0:
            continue
        win = B[k - w:k]
        if not win:
            continue
        if up:
            loc = min(x['lo'] for x in win)
            if b['lo'] < loc - TICK and b['c'] > loc and b['cpos'] >= cl:
                return True
        else:
            loc = max(x['hi'] for x in win)
            if b['hi'] > loc + TICK and b['c'] < loc and b['cpos'] <= 1 - cl:
                return True
    return False

def _leg_quality(B, i0, i1, up, C):
    """R9 — 'cay giam vol co ngon k / dong co dep k / rau duoi van rut kia'.
    Ti le nen THUAN huong trong leg co: dong dep (cpos dung phia) + rau nguoc nho + vol >= TB."""
    good = tot = 0
    for k in range(i0, i1 + 1):
        b = B[k]
        if b['rng'] <= 0:
            continue
        if up and not b['up']:
            continue
        if (not up) and not b['dn']:
            continue
        tot += 1
        wick = (b['lw'] if up else b['uw']) / b['rng']
        cpos_ok = (b['cpos'] >= C['LEGQ_CPOS']) if up else (b['cpos'] <= 1 - C['LEGQ_CPOS'])
        if cpos_ok and wick <= C['LEGQ_WICK'] and b['v'] >= b['vma']:
            good += 1
    return (good / tot) if tot else 0.0

def _leg_aggr(B, i0, i1, up):
    """R1 — leg do BUY MARKET (ASK) day hay do BUY LIMIT ke? Tra ddom cua ca leg.
    Chi dung duoc tren merged feed (co b['delta'], b['v_fp'])."""
    d = v = 0.0
    for k in range(i0, i1 + 1):
        b = B[k]
        if b.get('has_delta') and b.get('v_fp'):
            d += b['delta']; v += b['v_fp']
    if v <= 0:
        return None
    return d / v

# ---------------------------------------------------------------- engine
def run(B, C, vf, avg_vma):
    raw = []; N = len(B)
    for i in range(E.VSA_MA + 2, N):
        b = B[i]
        if not _gate(b, vf):
            continue
        win = B[i - C['RANGE_LEN']:i]
        rhi = max(x['hi'] for x in win); rlo = min(x['lo'] for x in win)
        span = (rhi - rlo) / TICK
        if span > C['RMAX'] or span < C['RMIN']:
            continue
        up = b['c'] > rhi + C['BUF'] * TICK and b['vratio'] >= C['BVSA'] and b['brat'] >= C['BBODY'] and b['up']
        dn = b['c'] < rlo - C['BUF'] * TICK and b['vratio'] >= C['BVSA'] and b['brat'] >= C['BBODY'] and b['dn']
        if not (up or dn):
            continue
        # --- R3: nen break la cu quet stoploss (VSA khong lo nhung dong yeu) -> bo ---
        if C['NOSTOP'] and b['vratio'] >= C['NOSTOP_VSA']:
            cp = b['cpos'] if up else 1 - b['cpos']
            if cp < C['NOSTOP_CPOS']:
                continue
        # --- W3a (da bac bo): phai co pha HUT truoc do ---
        if C['PHASE_C'] and not _phase_c(B, i, up, C):
            continue
        # --- W3b (CHAP NHAN): nen phai SACH — khong vua quet hut nguoc ---
        if C['CLEAN'] and counter_sweep(B, i, up, C['CL_LOOK'], C['CL_W'], C['CL_CLOSE']):
            continue

        side = 'LONG' if up else 'SHORT'; edge = rhi if up else rlo
        peak = b['hi'] if up else b['lo']; since = i
        for j in range(i + 1, min(N, i + 1 + C['WAIT'])):
            bj = B[j]
            if not _gate(bj, vf):
                break
            if (bj['c'] < edge - C['HOLD_TOL'] * TICK) if up else (bj['c'] > edge + C['HOLD_TOL'] * TICK):
                break
            pseg = B[since + 1:j + 1]
            if pseg:
                pext = min(x['lo'] for x in pseg) if up else max(x['hi'] for x in pseg)
                leg = (peak - edge) if up else (edge - peak)
                depth = (peak - pext) if up else (pext - peak)
                retr = depth / leg if leg > 0 else 0
                held = (pext >= edge - C['HOLD_TOL'] * TICK) if up else (pext <= edge + C['HOLD_TOL'] * TICK)
                resume = ((bj['c'] > B[j - 1]['hi'] and bj['up']) if up
                          else (bj['c'] < B[j - 1]['lo'] and bj['dn'])) and bj['brat'] >= C['RBODY']
                if j >= since + 2 and C['PMIN'] <= retr <= C['PMAX'] and held and resume:
                    # --- R9 chat luong leg (nen tu break -> dinh leg) ---
                    if C['LEGQ'] and _leg_quality(B, i, since, up, C) < C['LEGQ_MIN']:
                        break
                    # --- R1 leg phai do lenh chu dong day ---
                    if C['AGGR']:
                        a = _leg_aggr(B, i, since, up)
                        if a is None:
                            break
                        if (a < C['AGGR_MIN']) if up else (a > -C['AGGR_MIN']):
                            break
                    entry = bj['c']
                    # --- R7 neo SL ---
                    if C['SL_MODE'] == 'bar':
                        anchor = bj['lo'] if up else bj['hi']
                    elif C['SL_MODE'] == 'min':
                        anchor = max(pext, bj['lo']) if up else min(pext, bj['hi'])
                    else:
                        anchor = pext
                    sl = anchor - C['BUF'] * TICK if up else anchor + C['BUF'] * TICK
                    risk = (entry - sl) / TICK if up else (sl - entry) / TICK
                    if risk < C['FLOOR']:
                        sl = entry - C['FLOOR'] * TICK if up else entry + C['FLOOR'] * TICK
                        risk = C['FLOOR']
                    if risk > C['CAP']:
                        break
                    # ---- GATE tai NEN VAO (khop RunnerSignal.cs:570) ----
                    sd = 1 if up else -1
                    okT = (not C['TREND']) or bj['trend'] == sd
                    okV = (not C['VWAP']) or (bj['c'] >= bj['vwap'] if up else bj['c'] <= bj['vwap'])
                    okL = (not C['LIQ']) or bj['liqratio'] >= C['LIQ_K']
                    if okT and okV and okL:
                        raw.append(dict(i=j, dt=bj['dt'], ym=bj['ym'], side=side, entry=entry, sl=sl,
                                        risk_t=risk, retr=retr, span=span, brk_i=i, peak_i=since,
                                        brk_vsa=b['vratio'], hour=bj['dt'].hour))
                    break
            if (bj['hi'] > peak) if up else (bj['lo'] < peak):
                peak = bj['hi'] if up else bj['lo']; since = j
    return raw

def dedup(raw):
    out = []
    for s in sorted(raw, key=lambda x: x['i']):
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= E.DEDUP_BARS for m in out):
            continue
        out.append(s)
    return out

def cooldown(sig, cd):
    out = []; last = {}
    for s in sorted(sig, key=lambda x: x['i']):
        if s['i'] - last.get(s['side'], -999) < cd:
            continue
        out.append(s); last[s['side']] = s['i']
    return out

def post(sig, C):
    if C['DEAD']:
        sig = [s for s in sig if not (C['DEAD_FROM'] <= s['hour'] < C['DEAD_TO'])]
    if C['SESS'] is not None:
        sig = [s for s in sig if s['hour'] in C['SESS']]
    return [s for s in sig if s['ym'] in MONTHS]

def hit(B, i, side, sl, tp):
    for j in range(i + 1, len(B)):
        b = B[j]
        if (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl):
            return 'SL'
        if (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp):
            return 'TP'
    return 'open'

def evaluate(B, sig, C):
    out = []
    for s in sig:
        r = s['risk_t'] * TICK
        tp = s['entry'] + C['RR'] * r if s['side'] == 'LONG' else s['entry'] - C['RR'] * r
        o = hit(B, s['i'], s['side'], s['sl'], tp)
        if o == 'open':
            continue
        s2 = dict(s); s2['r'] = C['RR'] if o == 'TP' else -1.0
        out.append(s2)
    return out

def mdd(rs):
    eq = pk = worst = 0.0
    for r in rs:
        eq += r; pk = max(pk, eq); worst = max(worst, pk - eq)
    return worst

def scan(B, C, vf, avg_vma):
    return evaluate(B, post(cooldown(dedup(run(B, C, vf, avg_vma)), C['COOL']), C), C)

def line(tag, S, extra=""):
    if not S:
        print(f"  {tag:<34} n=  0   —"); return
    rs = [s['r'] for s in S]; w = sum(1 for r in rs if r > 0)
    bym = defaultdict(float)
    for s in S:
        bym[s['ym']] += s['r']
    mm = " ".join(f"{m[-2:]}:{bym[m]:+5.1f}" for m in MONTHS if m in bym)
    allpos = all(bym.get(m, 0) > 0 for m in MONTHS)
    med_risk = st.median([s['risk_t'] for s in S]) / 10
    print(f"  {tag:<34} n={len(S):3d} WR={100*w/len(S):5.1f}% tong={sum(rs):+7.1f}R "
          f"EV={sum(rs)/len(S):+.3f} MDD={mdd(rs):5.1f} SL~{med_risk:.1f}gia "
          f"| {mm} {'✓3thg' if allpos else '✗'} {extra}")

# ---------------------------------------------------------------- main
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'solo'
    B = E.load_m1()
    vf = E.calc_volfloor(B); E.VOLFLOOR_AUTO = vf
    prepare(B); avg_vma = None
    print(f"M1={len(B)} bars  volfloor={vf}  (trend tol {TREND_TOL}gia, liq cuon {LIQ_WIN} nen)")
    print("=" * 118)

    BASE = cfg()
    S0 = scan(B, BASE, vf, avg_vma)
    print("BASELINE — CBR v5 shipped (+loc phien chet)")
    line("v5 baseline RR3", S0)
    print("=" * 118)

    if mode == 'solo':
        print("TUNG LUAT RIENG LE (chi bat 1 thu so voi baseline)")
        tests = [
            ("W3 Phase-C (pha hut truoc)", cfg(PHASE_C=True)),
            ("W3 Phase-C look30", cfg(PHASE_C=True, PC_LOOK=30)),
            ("R9 chat luong leg 50%", cfg(LEGQ=True)),
            ("R9 chat luong leg 35%", cfg(LEGQ=True, LEGQ_MIN=0.35)),
            ("R3 bo break spike-fade", cfg(NOSTOP=True)),
            ("R7 SL duoi cay M1 (2-4gia)", cfg(SL_MODE='bar', FLOOR=20, CAP=40)),
            ("R7 SL chat hon (min) 2-4gia", cfg(SL_MODE='min', FLOOR=20, CAP=40)),
            ("R7 SL pull nhung cap 4gia", cfg(FLOOR=20, CAP=40)),
            ("R7+RR5 SL duoi cay M1", cfg(SL_MODE='bar', FLOOR=20, CAP=40, RR=5.0)),
            ("R7+RR6 SL duoi cay M1", cfg(SL_MODE='bar', FLOOR=20, CAP=40, RR=6.0)),
            ("RR5 (SL v5)", cfg(RR=5.0)),
            ("RR2 (SL v5)", cfg(RR=2.0)),
            ("R6 chi phien A+Au (08-19h)", cfg(SESS=set(range(8, 19)))),
            ("R6 chi phien My (19-02h)", cfg(SESS=set(list(range(19, 24)) + [0, 1]))),
        ]
        for tag, C in tests:
            line(tag, scan(B, C, vf, avg_vma))
        print("=" * 118)
        print("Ghi chu: '✓3thg' = duong o CA 3 thang (dieu kien chong overfit). Thieu no = KHONG nhan.")
    else:
        import stack_v6  # noqa

if __name__ == '__main__':
    main()
