#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RUNNER v4 — CBR (Consolidation -> Break -> Retest/hold -> Resume). Thay entry_runner.py v3.
Dung MO HINH LITERAL cua user: "pha RANGE, cho HOI (giu tren range), VAO nen tiep dien".
Khac v3 (leg gia tho -> 397 nhieu): v4 chi ban khi co RANGE co that (vung co hep) bi PHA climax.

Neo = RANGE noi bo (khong phai zone build_zones — vi 07/22 08:01 khong co zone nao trong 6 gia):
  RANGE = RANGE_LEN nen truoc, span <= RANGE_MAX (vung co hep, "range" user ke).
  BREAK  = nen dong vuot canh range + VSA climax(>=2.0) + than manh + THUAN bias.
  HOLD   = trong RETEST_BARS nen, gia hoi ve canh range nhung GIU (dong khong tro lai trong range).
  RESUME = nen dong vuot cuc tri nhip hoi (tiep dien). Vao tai close nen do.
  SL     = cuc tri nhip hoi +- buf (san 3 gia = user dung 3.04, tran 6 gia). TP 3R (giu runner).
Doi chieu 6 setup ground-truth + do WR/exp/tran R.
"""
import sys, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK

RANGE_LEN = 8          # so nen tao "range" truoc break
RANGE_MAX_T = 75       # span range <= 7.5 gia (vung co hep)
BREAK_VSA = 2.0        # nen pha phai climax
BREAK_BODY = 0.50
WAIT_BARS = 12         # cho hoi + tiep dien trong 12 nen sau break
PULL_MIN = 0.10        # nhip hoi >=10% cua LEG (peak-edge)
PULL_MAX = 0.90        # <=90% — ca hoi NON (long) lan hoi SAU gan retest (short) deu vao
HOLD_TOL_T = 2         # day nhip hoi cho phep thung canh vung <=0.2 gia (rau)
RESUME_BODY = 0.35     # nen tiep dien: than >=35% (BO gate delta/VSA — bai hoc #2)
# BIAS_GATE dung EMA30/120 = bias TRE -> 1 thang cho thay LOC NHAM lenh tot (bias ON +5R vs OFF +28R
# @3R). Bias THAT cua user = TPO (khong co trong data nay). => mac dinh TAT; live dung TPO bias.
BIAS_GATE = False
SL_FLOOR_T = 30; SL_CAP_T = 70; BUF = 2   # tran 7 gia (20:39 co SL cau truc 6.8 gia — hop le)
COOLDOWN = 15
HORIZON = 1440
CONFL_TOL = 7


def cluster_of(pool, t, zp):
    seen = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= CONFL_TOL:
            seen.add(round(z['price'] / TICK))
    return len(seen)


def run_cbr(B):
    raw = []; N = len(B)
    for i in range(em.VSA_MA + 2, N):                # quet MOI nen (dedup gom trung) — khong nhay con tro
        b = B[i]
        if not em.gate(b):
            continue
        win = B[i - RANGE_LEN:i]                     # RANGE_LEN nen truoc (khong gom nen pha)
        rhi = max(x['hi'] for x in win); rlo = min(x['lo'] for x in win)
        span = (rhi - rlo) / TICK
        if span > RANGE_MAX_T:                       # khong phai vung co -> bo
            continue
        up = (b['c'] > rhi + BUF * TICK and b['vratio'] >= BREAK_VSA and b['brat'] >= BREAK_BODY
              and b['c'] > b['o'] and (b['bias'] >= 0 or not BIAS_GATE))
        dn = (b['c'] < rlo - BUF * TICK and b['vratio'] >= BREAK_VSA and b['brat'] >= BREAK_BODY
              and b['c'] < b['o'] and (b['bias'] <= 0 or not BIAS_GATE))
        if not (up or dn):
            continue
        side = 'LONG' if up else 'SHORT'; edge = rhi if up else rlo
        # --- theo doi LEG (peak) + nhip HOI (% leg) + RESUME (vao nen tiep dien) ---
        # KHONG doi hoi ve tan canh vung: hoi NON van vao (bai hoc S4/S5).
        peak = b['hi'] if up else b['lo']; since = i
        for j in range(i + 1, min(N, i + 1 + WAIT_BARS)):
            bj = B[j]
            if not em.gate(bj): break
            # dong tro lai HAN TRONG range -> huy (khong giu leg)
            if (bj['c'] < edge - HOLD_TOL_T * TICK) if up else (bj['c'] > edge + HOLD_TOL_T * TICK):
                break
            pseg = B[since + 1:j + 1]                       # cac nen SAU dinh leg = nhip hoi
            if pseg:
                pull_ext = min(x['lo'] for x in pseg) if up else max(x['hi'] for x in pseg)
                leg = (peak - edge) if up else (edge - peak)
                depth = (peak - pull_ext) if up else (pull_ext - peak)
                retr = depth / leg if leg > 0 else 0
                held = (pull_ext >= edge - HOLD_TOL_T * TICK) if up else (pull_ext <= edge + HOLD_TOL_T * TICK)
                resume = ((bj['c'] > B[j - 1]['hi'] and bj['c'] > bj['o']) if up
                          else (bj['c'] < B[j - 1]['lo'] and bj['c'] < bj['o'])) and bj['brat'] >= RESUME_BODY
                if (j >= since + 2 and PULL_MIN <= retr <= PULL_MAX and held and resume):
                    entry = bj['c']
                    if up:
                        sl = pull_ext - BUF * TICK; risk = (entry - sl) / TICK
                    else:
                        sl = pull_ext + BUF * TICK; risk = (sl - entry) / TICK
                    if risk < SL_FLOOR_T:
                        sl = entry - SL_FLOOR_T * TICK if up else entry + SL_FLOOR_T * TICK; risk = SL_FLOOR_T
                    if risk > SL_CAP_T: break
                    raw.append(dict(i=j, dt=bj['dt'], side=side, entry=entry, sl=sl, risk_t=risk,
                                    edge=edge, span_t=span, brk_vsa=b['vratio'], bias=bj['bias'],
                                    brk_dt=b['dt'], retr=retr, leg_t=leg / TICK))
                    break
            # cap nhat dinh leg (mo rong khi tao dinh/day moi)
            if (bj['hi'] > peak) if up else (bj['lo'] < peak):
                peak = bj['hi'] if up else bj['lo']; since = j
    return raw


def dedup(raw):
    out = []
    for s in sorted(raw, key=lambda x: x['i']):
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= em.DEDUP_BARS for m in out): continue
        out.append(s)
    return out


def cooldown_filter(sig, cd):
    out = []; last = {}
    for s in sorted(sig, key=lambda x: x['i']):
        if s['i'] - last.get(s['side'], -999) < cd: continue
        out.append(s); last[s['side']] = s['i']
    return out


def hit(B, i, side, sl, tp):
    for j in range(i + 1, len(B)):
        b = B[j]
        if (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl): return 'SL'
        if (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp): return 'TP'
    return 'open'


def ceiling(B, i, side, entry, sl):
    r = abs(sl - entry); best = 0.0
    for j in range(i + 1, min(len(B), i + 1 + HORIZON)):
        b = B[j]
        best = max(best, (entry - b['lo']) / r if side == 'SHORT' else (b['hi'] - entry) / r)
        if (b['hi'] >= sl) if side == 'SHORT' else (b['lo'] <= sl): break
    return best


def ev(B, S, rm):
    tp = sl = 0
    for s in S:
        r = s['risk_t'] * TICK
        o = hit(B, s['i'], s['side'], s['sl'], s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r)
        tp += o == 'TP'; sl += o == 'SL'
    n = tp + sl
    return (tp / n if n else 0), ((tp * rm - sl) / n if n else 0), (tp * rm - sl)


GT = [('07/20', 12, 7, 'SHORT'), ('07/21', 8, 1, 'LONG'), ('07/21', 12, 36, 'LONG'),
      ('07/22', 8, 1, 'LONG'), ('07/22', 20, 39, 'LONG'), ('07/23', 19, 20, 'SHORT')]


def catches(sig, day, hh, mm, side, tol=8):
    best = None
    for s in sig:
        if (s['dt'].strftime('%m/%d') == day and s['side'] == side
                and abs((s['dt'].hour * 60 + s['dt'].minute) - (hh * 60 + mm)) <= tol):
            best = s
    return best


def report(B, pool, sig, tag):
    for s in sig: s['cluster'] = cluster_of(pool, s['dt'], s['entry'])
    mrs = [ceiling(B, s['i'], s['side'], s['entry'], s['sl']) for s in sig]
    print(f"\n### {tag}: n={len(sig)}")
    if sig:
        print(f"   risk tv {st.median([s['risk_t'] for s in sig])/10:.1f}gia | span range tb {st.mean([s['span_t'] for s in sig])/10:.1f}gia | "
              f"co vung(cluster>=2): {sum(s['cluster']>=2 for s in sig)}/{len(sig)}")
        print(f"   TRAN R (cap 24h): trung vi {st.median(mrs):.1f}R | >=3R: {sum(m>=3 for m in mrs)}/{len(sig)} | >=6R: {sum(m>=6 for m in mrs)}/{len(sig)}")
    for rm in (1.5, 2.0, 3.0):
        wr, exp, tot = ev(B, sig, rm)
        print(f"     {rm:.1f}R: WR {wr:.0%} | exp {exp:+.2f}R | tong {tot:+.1f}R")
    hits = sum(1 for g in GT if catches(sig, *g))
    print(f"   BAT {hits}/6 setup ground-truth:")
    for day, hh, mm, side in GT:
        s = catches(sig, day, hh, mm, side)
        print(f"     {day} {hh:02d}:{mm:02d} {side}: " + (f"BAT ({s['dt']:%H:%M} risk{s['risk_t']/10:.1f}gia)" if s else "khong"))


if __name__ == '__main__':
    B = em.load_m1(); pool = em.build_zones(B)
    print("=" * 100)
    print(f"RUNNER v4 CBR — pha vung co + hoi NON giu leg + tiep dien. knobs: range {RANGE_LEN}nen span<={RANGE_MAX_T/10:.1f}gia, "
          f"breakVSA>={BREAK_VSA}, wait {WAIT_BARS}nen, retrace[{PULL_MIN:.0%}-{PULL_MAX:.0%}], SL {SL_FLOOR_T/10:.0f}-{SL_CAP_T/10:.0f}gia")
    sig = cooldown_filter(dedup(run_cbr(B)), COOLDOWN)          # BIAS_GATE=False (mac dinh)
    report(B, pool, sig, "CBR — mac dinh (bias EMA TAT)")
    globals()['BIAS_GATE'] = True
    sig_b = cooldown_filter(dedup(run_cbr(B)), COOLDOWN)
    globals()['BIAS_GATE'] = False
    report(B, pool, sig_b, "doi chieu: BAT bias EMA (loc nham -> te hon)")

    # --- xuat CSV tung lenh de user soi ---
    import csv as _csv
    DIRR = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/"
    HEAD = ['ngay_gio', 'huong', 'break_luc', 'vung_pha', 'span_range_gia', 'retrace%',
            'entry', 'SL', 'risk_gia', 'bias_EMA', 'co_vung', 'KQ_3R', 'tran_R_24h']
    rows = []
    for s in sorted(sig, key=lambda x: x['i']):
        r = s['risk_t'] * TICK
        tp = s['entry'] + 3 * r if s['side'] == 'LONG' else s['entry'] - 3 * r
        kq = hit(B, s['i'], s['side'], s['sl'], tp)
        cel = ceiling(B, s['i'], s['side'], s['entry'], s['sl'])
        rows.append([s['dt'].strftime('%Y-%m-%d %H:%M'), s['side'], s['brk_dt'].strftime('%H:%M'),
                     f"{s['edge']:.1f}", f"{s['span_t']/10:.1f}", f"{s.get('retr',0)*100:.0f}",
                     f"{s['entry']:.1f}", f"{s['sl']:.1f}", f"{s['risk_t']/10:.1f}", f"{s['bias']:+d}",
                     'co' if s['cluster'] >= 2 else '-',
                     'WIN' if kq == 'TP' else ('LOSS' if kq == 'SL' else 'open'), f"{cel:.1f}"])
    with open(DIRR + "trades_runner_cbr.csv", 'w', newline='', encoding='utf-8-sig') as f:
        w = _csv.writer(f); w.writerow(HEAD); w.writerows(rows)
    print(f"\n>> Xuat {len(rows)} lenh -> {DIRR}trades_runner_cbr.csv")
    print("=" * 100)
