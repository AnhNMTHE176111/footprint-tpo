#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRACK B (nham 3R) — KB1 kieu MOI: PHA -> cho NHIP HOI hoan chinh giu vung -> vao nen XUNG LUC SAU hoi.
Khac Track A: Track A vao NGAY tren nen hoi (bat day). Track B tach 2 pha:
  1) PHA len qua vung (bu).
  2) HOI: gia keo ve cham vung (low <= zp+RetestTol) VA GIU vung (low >= zp-Hold). Ghi pull_low.
  3) XAC NHAN: trong <=W nen sau day hoi, xuat hien nen tang manh (body>=0.55, delta>0, cpos>=0.6,
     VSA>=High) dong TREN dinh nhip hoi (c > pull_high) -> VAO tai close nen xac nhan.
  4) SL = DUOI day hoi (pull_low - buf), san 4 gia, tran 6 gia (cap, khong reject).
So 1.5R/2R/3R vs Track A KB1. SHORT doi xung.
"""
import sys
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
CONFL_TOL = 7
SL_FLOOR_T = 40; SL_CAP_T = 60; BUF = 2; HOLD = 0
CONFIRM_W = 6           # so nen toi da tu day hoi den nen xac nhan
PULL_MINDEPTH_T = 0     # hoi it nhat cham vung (low<=zp+RetestTol da dam bao)


def hit(B, i, side, sl, tp):
    for j in range(i + 1, len(B)):
        b = B[j]
        if (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl): return 'SL'
        if (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp): return 'TP'
    return 'open'


def clu(pool, t, zp):
    s = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= CONFL_TOL: s.add(round(z['price'] / TICK))
    return len(s)


def run_b(B, pool):
    raw = []
    Z = [dict(z) for z in pool]
    for z in Z:
        z.update(state='idle', brk=-999, prev=None, pull_low=None, pull_hi=None, pull_bar=-999,
                 pull_hiS=None, pull_lowS=None)
    for i in range(em.VSA_MA + 2, len(B)):
        b = B[i]
        active = [z for z in Z if z['ready'] <= b['dt'] <= z['expire']]
        if not em.gate(b):
            for z in active: z['prev'] = 'above' if b['c'] > z['price'] else 'below'
            continue
        for z in active:
            zp = z['price']
            rel = 'above' if b['c'] > zp + BUF * TICK else 'below' if b['c'] < zp - BUF * TICK else 'in'
            # --- PHA ---
            bu = b['c'] > zp + BUF * TICK and b['hi'] > zp and b['brat'] >= 0.5 and b['delta'] > 0 and b['vratio'] >= em.VSA_BREAK and z['prev'] in ('below', 'in')
            bd = b['c'] < zp - BUF * TICK and b['lo'] < zp and b['brat'] >= 0.5 and b['delta'] < 0 and b['vratio'] >= em.VSA_BREAK and z['prev'] in ('above', 'in')
            if bu:
                z['state'] = 'up'; z['brk'] = i; z['pull_low'] = None; z['pull_hi'] = None; z['pull_bar'] = -999
            elif bd:
                z['state'] = 'dn'; z['brk'] = i; z['pull_hiS'] = None; z['pull_lowS'] = None; z['pull_bar'] = -999

            # --- LONG: HOI + XAC NHAN ---
            if z['state'] == 'up' and 0 < i - z['brk'] <= em.RETEST_BARS + CONFIRM_W:
                if b['c'] < zp - BUF * TICK:
                    z['state'] = 'idle'                                   # pha hong
                else:
                    # 1) XAC NHAN truoc (dung day hoi tu cac nen TRUOC): nen tang manh dong tren vung, dong tren dinh nen truoc
                    prevhi = B[i - 1]['hi']
                    if (z['pull_low'] is not None and 0 < i - z['pull_bar'] <= CONFIRM_W
                            and b['brat'] >= em.BODY_STRONG and b['delta'] > 0 and b['cpos'] >= 0.6
                            and b['vratio'] >= em.VSA_GATE and b['c'] > zp + BUF * TICK and b['c'] > prevhi):
                        entry = b['c']; sl = min(z['pull_low'] - BUF * TICK, entry - SL_FLOOR_T * TICK)
                        risk = (entry - sl) / TICK
                        if risk > SL_CAP_T: sl = entry - SL_CAP_T * TICK; risk = SL_CAP_T
                        if risk > 0:
                            raw.append(dict(i=i, dt=b['dt'], side='LONG', scen='1B pha-hoi-xacnhan', entry=entry,
                                            sl=sl, risk_t=risk, zone=f"{z['kind']} {zp:.1f}", vsa=b['vratio'],
                                            gap=i - z['pull_bar']))
                        z['state'] = 'idle'
                    # 2) ghi nhan nhip hoi cham vung + giu vung (sau khi da xet confirm)
                    elif b['lo'] <= zp + em.RETEST_TOL_T * TICK and b['lo'] >= zp - HOLD * TICK:
                        if z['pull_low'] is None or b['lo'] < z['pull_low']:
                            z['pull_low'] = b['lo']; z['pull_bar'] = i
            elif z['state'] == 'dn' and 0 < i - z['brk'] <= em.RETEST_BARS + CONFIRM_W:
                if b['c'] > zp + BUF * TICK:
                    z['state'] = 'idle'
                else:
                    prevlo = B[i - 1]['lo']
                    if (z['pull_hiS'] is not None and 0 < i - z['pull_bar'] <= CONFIRM_W
                            and b['brat'] >= em.BODY_STRONG and b['delta'] < 0 and b['cpos'] <= 0.4
                            and b['vratio'] >= em.VSA_GATE and b['c'] < zp - BUF * TICK and b['c'] < prevlo):
                        entry = b['c']; sl = max(z['pull_hiS'] + BUF * TICK, entry + SL_FLOOR_T * TICK)
                        risk = (sl - entry) / TICK
                        if risk > SL_CAP_T: sl = entry + SL_CAP_T * TICK; risk = SL_CAP_T
                        if risk > 0:
                            raw.append(dict(i=i, dt=b['dt'], side='SHORT', scen='1B pha-hoi-xacnhan', entry=entry,
                                            sl=sl, risk_t=risk, zone=f"{z['kind']} {zp:.1f}", vsa=b['vratio'],
                                            gap=i - z['pull_bar']))
                        z['state'] = 'idle'
                    elif b['hi'] >= zp - em.RETEST_TOL_T * TICK and b['hi'] <= zp + HOLD * TICK:
                        if z['pull_hiS'] is None or b['hi'] > z['pull_hiS']:
                            z['pull_hiS'] = b['hi']; z['pull_bar'] = i
            z['prev'] = rel
    return raw


def dedup(raw):
    out = []
    for s in sorted(raw, key=lambda x: x['i']):
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= em.DEDUP_BARS and abs(s['entry'] - m['entry']) / TICK <= em.DEDUP_TICKS for m in out):
            continue
        out.append(s)
    return out


def evalsub(B, sub, rm):
    tp = sl = 0
    for s in sub:
        r = s['risk_t'] * TICK
        o = hit(B, s['i'], s['side'], s['sl'], s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r)
        tp += o == 'TP'; sl += o == 'SL'
    n = tp + sl
    return len(sub), (tp / n if n else 0), ((tp * rm - sl) / n if n else 0), (tp * rm - sl)


if __name__ == '__main__':
    B = em.load_m1(); pool = em.build_zones(B)
    raw = run_b(B, pool)
    for s in raw: s['cluster'] = clu(pool, s['dt'], float(s['zone'].split()[-1]))
    sig = dedup(raw)
    sig2 = [s for s in sig if s['cluster'] >= 2]
    import statistics as st
    print("=" * 96)
    print(f"TRACK B — KB1 pha->hoi->XAC NHAN (vao nen xung luc sau hoi; SL duoi day hoi). 1 thang")
    for tag, S in [("don-vung (cum>=1)", sig), ("cum>=2 (khop lai)", sig2)]:
        print(f"\n[{tag}] n={len(S)}  (risk tv {st.median([s['risk_t']/10 for s in S]) if S else 0:.1f} gia, "
              f"gap tb {st.mean([s['gap'] for s in S]):.1f} nen neu co)" if S else f"\n[{tag}] n=0")
        for rm in (1.5, 2.0, 3.0):
            n, wr, exp, totR = evalsub(B, S, rm)
            print(f"    {rm:.1f}R: WR {wr:>3.0%} | exp {exp:>+5.2f}R | tong {totR:>+5.1f}R")
    print("\n  (so chieu Track A @cum>=2: KB1 1.5R +0.44R / 3R -0.08R ; ca he 1.5R +0.52R)")
    print("=" * 96)
