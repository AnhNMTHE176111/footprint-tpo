#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BAN B v2 — mo hinh user chon: "vao cay XUNG LUC sau nhip HOI" (khong cham vung).
Khac ban B v1 (retest ve vung): day la MEASURED-MOVE PULLBACK / flag:
  1) XUNG LUC: 1 leg di manh >= MIN_LEG gia trong <=LEG_WIN nen, co it nhat 1 nen VSA cao.
  2) HOI: gia hoi nguoc MOT PHAN leg, ti le retrace trong [PULL_MIN, PULL_MAX] ('vua du,
     phu hop nhip pha'). KHONG doi hoi ve tan vung goc.
  3) VAO: nen tiep dien thuan da (than manh, delta thuan, dong qua cuc tri nen truoc) trong
     <=CONFIRM_W nen sau dinh/day hoi -> vao tai close.
  4) SL: ngoai cuc tri nhip hoi (tren dinh hoi / duoi day hoi), san 4 gia, tran 6 gia.
So 1.5/2/3R vs ban B v1 (retest). Kiem ca 19:20/07/23 short co bat khong.
"""
import sys, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK

LEG_WIN = 6          # so nen toi da cua leg xung luc
MIN_LEG_T = 35       # leg toi thieu 3.5 gia (loc nhieu)
PULL_MIN = 0.25      # hoi it nhat 25% leg
PULL_MAX = 0.70      # hoi toi da 70% leg (qua 70% = mat da)
CONFIRM_W = 8        # so nen tu dinh/day hoi den nen xac nhan
VSA_IMP = 1.8        # leg phai co it nhat 1 nen VSA>=1.8 (co luc)
SL_FLOOR_T = 40; SL_CAP_T = 60; BUF = 2
CONFL_TOL = 7        # hop luu: vung trong +-7 tick
CONFL_MIN = 2        # entry phai co >= 2 vung hop luu (nhu ban A/B)
COOLDOWN = 15        # khong ban lai cung chieu trong 15 nen


def cluster_of(pool, t, zp):
    seen = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= CONFL_TOL:
            seen.add(round(z['price'] / TICK))
    return len(seen)


def hit(B, i, side, sl, tp):
    for j in range(i + 1, len(B)):
        b = B[j]
        if (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl): return 'SL'
        if (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp): return 'TP'
    return 'open'


def run_impulse(B):
    raw = []; N = len(B); i = em.VSA_MA + 2
    st_ = None; legT = legB = pivot = pext = born = None
    while i < N:
        b = B[i]
        if not em.gate(b):
            st_ = None; i += 1; continue
        seg = B[max(0, i - LEG_WIN + 1):i + 1]
        top = max(x['hi'] for x in seg); bot = min(x['lo'] for x in seg)
        legt = (top - bot) / TICK
        strong = any(x['vratio'] >= VSA_IMP for x in seg)
        if st_ is None:
            # xung luc XUONG: b tao day leg, close nua duoi
            if b['lo'] <= bot + 0.5 * TICK and legt >= MIN_LEG_T and strong and b['c'] < b['o'] and b['cpos'] <= 0.45:
                st_ = 'dn'; legT = top; legB = b['lo']; pivot = i; pext = b['hi']; born = i
            elif b['hi'] >= top - 0.5 * TICK and legt >= MIN_LEG_T and strong and b['c'] > b['o'] and b['cpos'] >= 0.55:
                st_ = 'up'; legT = b['hi']; legB = bot; pivot = i; pext = b['lo']; born = i
        elif st_ == 'dn':
            if i - born > LEG_WIN + CONFIRM_W: st_ = None; continue
            if b['lo'] < legB: legB = b['lo']; born = i; pext = b['hi']  # leg xuong tiep -> reset moc hoi
            pext = max(pext, b['hi'])
            leg = legT - legB
            retr = (pext - legB) / leg if leg > 0 else 0
            cont = b['brat'] >= em.BODY_STRONG and b['delta'] < 0 and b['cpos'] <= 0.40 and b['vratio'] >= em.VSA_GATE and b['c'] < B[i - 1]['lo']
            if PULL_MIN <= retr <= PULL_MAX and cont:
                entry = b['c']; sl = pext + BUF * TICK; risk = (sl - entry) / TICK
                if risk < SL_FLOOR_T: sl = entry + SL_FLOOR_T * TICK; risk = SL_FLOOR_T
                if risk > SL_CAP_T: sl = entry + SL_CAP_T * TICK; risk = SL_CAP_T
                raw.append(dict(i=i, dt=b['dt'], side='SHORT', entry=entry, sl=sl, risk_t=risk,
                                retr=retr, leg_t=leg / TICK, vsa=b['vratio']))
                st_ = None
        elif st_ == 'up':
            if i - born > LEG_WIN + CONFIRM_W: st_ = None; continue
            if b['hi'] > legT: legT = b['hi']; born = i; pext = b['lo']
            pext = min(pext, b['lo'])
            leg = legT - legB
            retr = (legT - pext) / leg if leg > 0 else 0
            cont = b['brat'] >= em.BODY_STRONG and b['delta'] > 0 and b['cpos'] >= 0.60 and b['vratio'] >= em.VSA_GATE and b['c'] > B[i - 1]['hi']
            if PULL_MIN <= retr <= PULL_MAX and cont:
                entry = b['c']; sl = pext - BUF * TICK; risk = (entry - sl) / TICK
                if risk < SL_FLOOR_T: sl = entry - SL_FLOOR_T * TICK; risk = SL_FLOOR_T
                if risk > SL_CAP_T: sl = entry - SL_CAP_T * TICK; risk = SL_CAP_T
                raw.append(dict(i=i, dt=b['dt'], side='LONG', entry=entry, sl=sl, risk_t=risk,
                                retr=retr, leg_t=leg / TICK, vsa=b['vratio']))
                st_ = None
        i += 1
    return raw


def dedup(raw):
    out = []
    for s in sorted(raw, key=lambda x: x['i']):
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= em.DEDUP_BARS for m in out): continue
        out.append(s)
    return out


def ev(B, S, rm):
    tp = sl = 0
    for s in S:
        r = s['risk_t'] * TICK
        o = hit(B, s['i'], s['side'], s['sl'], s['entry'] + rm * r if s['side'] == 'LONG' else s['entry'] - rm * r)
        tp += o == 'TP'; sl += o == 'SL'
    n = tp + sl
    return len(S), (tp / n if n else 0), ((tp * rm - sl) / n if n else 0), (tp * rm - sl)


def cooldown_filter(sig, cd):
    out = []; last = {}
    for s in sorted(sig, key=lambda x: x['i']):
        if s['i'] - last.get(s['side'], -999) < cd: continue
        out.append(s); last[s['side']] = s['i']
    return out


def maxR(B, i, side, entry, sl):
    """Tran R that su (theo day/dinh) TRUOC khi cham SL — KHONG cap thoi gian."""
    r = abs(sl - entry); best = 0.0
    for j in range(i + 1, len(B)):
        b = B[j]
        fav = (entry - b['lo']) / r if side == 'SHORT' else (b['hi'] - entry) / r
        best = max(best, fav)
        if (b['hi'] >= sl) if side == 'SHORT' else (b['lo'] <= sl): break
    return best


B = em.load_m1(); pool = em.build_zones(B)
raw = run_impulse(B)
for s in raw: s['cluster'] = cluster_of(pool, s['dt'], s['entry'])
sig0 = dedup(raw)
sig = [s for s in sig0 if s['cluster'] >= CONFL_MIN]     # loc hop luu >=2
sig = cooldown_filter(sig, COOLDOWN)                     # cooldown per-side
print("=" * 92)
print(f"BAN B v2 — xung luc + hoi ti le + vao tiep dien (M1, 1 thang).")
print(f"  raw={len(raw)} -> dedup={len(sig0)} -> loc hop luu>={CONFL_MIN} + cooldown{COOLDOWN} => n={len(sig)}")
print(f"  knobs: leg>={MIN_LEG_T/10:.1f}gia/{LEG_WIN}nen, retrace [{PULL_MIN:.0%}-{PULL_MAX:.0%}], VSA_leg>={VSA_IMP}")
if sig:
    print(f"  leg tb {st.mean([s['leg_t'] for s in sig])/10:.1f}gia | retrace tb {st.mean([s['retr'] for s in sig]):.0%} | "
          f"risk tv {st.median([s['risk_t'] for s in sig])/10:.1f}gia | cluster tb {st.mean([s['cluster'] for s in sig]):.1f}")
    mrs = [maxR(B, s['i'], s['side'], s['entry'], s['sl']) for s in sig]
    print(f"  TRAN R (khong cap gio): trung vi {st.median(mrs):.1f}R | cham>=3R: {sum(m>=3 for m in mrs)}/{len(sig)} | "
          f"cham>=6R: {sum(m>=6 for m in mrs)}/{len(sig)}")
for rm in (1.5, 2.0, 3.0, 6.0):
    n, wr, exp, tot = ev(B, sig, rm)
    print(f"    {rm:.1f}R: n={n} WR {wr:.0%} | exp {exp:+.2f}R | tong {tot:+.1f}R")
print("\n  (so chieu ban B v1 retest @cum>=2: 1.5R 78%/+0.94R ; 2R 44%/+0.33R ; 3R 22%/-0.11R, n=9)")

print("\n  --- Co bat cu 19:20/07/23 short khong? tin hieu 07/23 18:00-20:00: ---")
hit_any = False
for s in sig:
    if s['dt'].strftime('%m/%d') == '07/23' and 18 <= s['dt'].hour < 20:
        hit_any = True
        print(f"    {s['dt']:%H:%M} {s['side']} entry {s['entry']:.1f} SL {s['sl']:.1f} retrace {s['retr']:.0%} leg {s['leg_t']/10:.1f}gia")
if not hit_any:
    print("    (khong co tin hieu nao 07/23 18:00-20:00)")
print("=" * 92)
