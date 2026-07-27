#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RUNNER v3 — viet lai theo 6 setup ground-truth cua user (thay entry_impulse.py v2 net -11R).
Mo hinh user (da xac nhan tren 6 anh): PHA -> hoi GIU vung -> vao NEN TIEP DIEN -> giu 3R+.

3 bai hoc rut tu 6 setup (verify_6setups.py — doc so THAT tren futures):
  (1) CA 6 deu THUAN BIAS (EMA30/120). => bias gate = bo loc SO 1 (ban cu thieu -> an 17 nhieu).
  (2) Nen ENTRY thuong "xau": S5 VSA1.04, S1/S6 short delta DUONG (+40/+29), S4 cpos0. Suc manh
      o NEN XUNG LUC trong leg (VSA 2.5-8.7), KHONG o nen vao. => entry = CAU TRUC (dong vuot nhip
      hoi + than du manh), BO gate delta/VSA tren nen vao. Ban cu bat buoc delta dung dau -> loai
      sach chinh lenh thang cua user.
  (3) Bat buoc hop luu vung = SAI: 07/22 08:01 long KHONG co vung nao trong 6 gia. => vung chi la
      diem cong (tag), KHONG hard-gate.

Discipline moi = BIAS(thuan) + CLIMAX trong leg (VSA>=2.0) + HOLD (hoi khong xoa leg) + RESUME
(dong vuot cuc tri hoi). SL = cuc tri nhip hoi +-buf, san 3 gia (user dung 3.04), tran 6 gia.
"""
import sys, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK

# --- knobs (default; sweep o cuoi) ---
BIAS_GATE = True     # (1) chi thuan bias EMA30/120
LEG_WIN = 8          # leg toi da 8 nen
MIN_LEG_T = 35       # leg >= 3.5 gia
LEG_CLIMAX = 2.0     # (2) leg phai co >=1 nen VSA>=2.0 (xung luc that)
PULL_MIN = 0.20      # hoi >=20% leg
PULL_MAX = 0.80      # hoi <=80% leg (van giu leg — "dong tren range")
CONFIRM_W = 8        # so nen tu cuc tri hoi -> nen tiep dien
ENTRY_BODY = 0.45    # (2) nen vao: than >=45% (khong doji); BO gate delta/VSA/cpos chat
SL_FLOOR_T = 30; SL_CAP_T = 60; BUF = 2
COOLDOWN = 15
HORIZON = 1440       # 24h — cap MFE cho hop ly (khong uncapped: se doc drift nhieu ngay -> 27R ao)
CONFL_TOL = 7        # vung trong +-7 tick (chi de TAG, khong gate)


def cluster_of(pool, t, zp):
    seen = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= CONFL_TOL:
            seen.add(round(z['price'] / TICK))
    return len(seen)


def run_runner(B):
    raw = []; N = len(B); i = em.VSA_MA + 2
    st_ = None; legT = legB = pext = born = None
    while i < N:
        b = B[i]
        if not em.gate(b):
            st_ = None; i += 1; continue
        seg = B[max(0, i - LEG_WIN + 1):i + 1]
        top = max(x['hi'] for x in seg); bot = min(x['lo'] for x in seg)
        legt = (top - bot) / TICK
        climax = any(x['vratio'] >= LEG_CLIMAX for x in seg)
        if st_ is None:
            # xung luc XUONG (short): b tao/gan day leg, than manh, dong nua duoi, THUAN bias<=0
            if (b['lo'] <= bot + 0.5 * TICK and legt >= MIN_LEG_T and climax
                    and b['c'] < b['o'] and b['cpos'] <= 0.45 and (b['bias'] <= 0 or not BIAS_GATE)):
                st_ = 'dn'; legT = top; legB = b['lo']; pext = b['hi']; born = i
            elif (b['hi'] >= top - 0.5 * TICK and legt >= MIN_LEG_T and climax
                    and b['c'] > b['o'] and b['cpos'] >= 0.55 and (b['bias'] >= 0 or not BIAS_GATE)):
                st_ = 'up'; legT = b['hi']; legB = bot; pext = b['lo']; born = i
        elif st_ == 'dn':
            if i - born > LEG_WIN + CONFIRM_W: st_ = None; continue
            if b['lo'] < legB: legB = b['lo']; born = i; pext = b['hi']   # leg xuong tiep -> reset
            pext = max(pext, b['hi'])
            leg = legT - legB
            retr = (pext - legB) / leg if leg > 0 else 0
            # (2) RESUME cau truc: dong duoi day nen truoc + than du + dong nua duoi. BO gate delta.
            resume = b['c'] < B[i - 1]['lo'] and b['brat'] >= ENTRY_BODY and b['cpos'] <= 0.55
            bias_ok = (b['bias'] <= 0) or not BIAS_GATE
            if PULL_MIN <= retr <= PULL_MAX and resume and bias_ok:
                entry = b['c']; sl = pext + BUF * TICK; risk = (sl - entry) / TICK
                if risk < SL_FLOOR_T: sl = entry + SL_FLOOR_T * TICK; risk = SL_FLOOR_T
                if risk > SL_CAP_T: st_ = None; i += 1; continue   # cau truc qua rong -> bo (khong ep SL)
                raw.append(dict(i=i, dt=b['dt'], side='SHORT', entry=entry, sl=sl, risk_t=risk,
                                retr=retr, leg_t=leg / TICK, vsa=b['vratio'], bias=b['bias']))
                st_ = None
        elif st_ == 'up':
            if i - born > LEG_WIN + CONFIRM_W: st_ = None; continue
            if b['hi'] > legT: legT = b['hi']; born = i; pext = b['lo']
            pext = min(pext, b['lo'])
            leg = legT - legB
            retr = (legT - pext) / leg if leg > 0 else 0
            resume = b['c'] > B[i - 1]['hi'] and b['brat'] >= ENTRY_BODY and b['cpos'] >= 0.45
            bias_ok = (b['bias'] >= 0) or not BIAS_GATE
            if PULL_MIN <= retr <= PULL_MAX and resume and bias_ok:
                entry = b['c']; sl = pext - BUF * TICK; risk = (entry - sl) / TICK
                if risk < SL_FLOOR_T: sl = entry - SL_FLOOR_T * TICK; risk = SL_FLOOR_T
                if risk > SL_CAP_T: st_ = None; i += 1; continue
                raw.append(dict(i=i, dt=b['dt'], side='LONG', entry=entry, sl=sl, risk_t=risk,
                                retr=retr, leg_t=leg / TICK, vsa=b['vratio'], bias=b['bias']))
                st_ = None
        i += 1
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
    """Tran R (theo day/dinh) TRUOC khi cham SL, cap HORIZON nen."""
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
    return len(S), (tp / n if n else 0), ((tp * rm - sl) / n if n else 0), (tp * rm - sl)


# 6 setup ground-truth de doi chieu (date, hh, mm, side)
GT = [('07/20', 12, 7, 'SHORT'), ('07/21', 8, 1, 'LONG'), ('07/21', 12, 36, 'LONG'),
      ('07/22', 8, 1, 'LONG'), ('07/22', 20, 39, 'LONG'), ('07/23', 19, 20, 'SHORT')]


def catches(sig, day, hh, mm, side, tol=4):
    for s in sig:
        if (s['dt'].strftime('%m/%d') == day and s['side'] == side
                and abs((s['dt'].hour * 60 + s['dt'].minute) - (hh * 60 + mm)) <= tol):
            return s
    return None


def report(B, pool, sig, tag):
    for s in sig: s.setdefault('cluster', cluster_of(pool, s['dt'], s['entry']))
    mrs = [ceiling(B, s['i'], s['side'], s['entry'], s['sl']) for s in sig]
    print(f"\n### {tag}: n={len(sig)}")
    if sig:
        print(f"   risk tv {st.median([s['risk_t'] for s in sig])/10:.1f}gia | leg tb {st.mean([s['leg_t'] for s in sig])/10:.1f}gia | "
              f"retrace tb {st.mean([s['retr'] for s in sig]):.0%} | co vung(cluster>=2): {sum(s['cluster']>=2 for s in sig)}/{len(sig)}")
        print(f"   TRAN R (cap 24h): trung vi {st.median(mrs):.1f}R | >=3R: {sum(m>=3 for m in mrs)}/{len(sig)} | >=6R: {sum(m>=6 for m in mrs)}/{len(sig)}")
    for rm in (1.5, 2.0, 3.0):
        n, wr, exp, tot = ev(B, sig, rm)
        print(f"     {rm:.1f}R: WR {wr:.0%} | exp {exp:+.2f}R | tong {tot:+.1f}R")
    hits = sum(1 for g in GT if catches(sig, *g))
    print(f"   BAT {hits}/6 setup ground-truth:")
    for day, hh, mm, side in GT:
        s = catches(sig, day, hh, mm, side)
        print(f"     {day} {hh:02d}:{mm:02d} {side}: " + (f"BAT ({s['dt']:%H:%M} risk{s['risk_t']/10:.1f}gia retrace{s['retr']:.0%})" if s else "khong"))


if __name__ == '__main__':
    B = em.load_m1(); pool = em.build_zones(B)
    raw = run_runner(B)
    sig = cooldown_filter(dedup(raw), COOLDOWN)
    print("=" * 100)
    print(f"RUNNER v3 (bias-gated + resume cau truc). raw={len(raw)} -> dedup+cooldown => n={len(sig)}")
    print(f"knobs: leg>={MIN_LEG_T/10:.1f}gia/{LEG_WIN}nen climaxVSA>={LEG_CLIMAX}, retrace[{PULL_MIN:.0%}-{PULL_MAX:.0%}], "
          f"entry body>={ENTRY_BODY:.0%} (BO delta gate), SL {SL_FLOOR_T/10:.0f}-{SL_CAP_T/10:.0f}gia, bias_gate={BIAS_GATE}")
    report(B, pool, sig, "RUNNER v3 (bias ON)")
    # doi chieu: TAT bias gate -> chung minh bias la bo loc chinh
    BIAS_GATE_OLD = BIAS_GATE
    globals()['BIAS_GATE'] = False
    raw2 = run_runner(B); sig2 = cooldown_filter(dedup(raw2), COOLDOWN)
    globals()['BIAS_GATE'] = BIAS_GATE_OLD
    report(B, pool, sig2, "doi chieu: TAT bias gate")
    print("=" * 100)
