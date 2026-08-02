#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REV_BODYDIR_AB2 — kiem dinh y nghia thong ke + tinh chinh luat thuan mau cho nhanh QUAY_DAU.

Vong 1 (rev_bodydir_ab.py) cho: nguoc mau EV +0.154 vs thuan mau EV +0.607 (RR1.5).
Nhung n=13/14 => phai kiem xem chenh lech co phai NHIEU khong truoc khi ship.
  (a) hoan vi (permutation): xao nhan thuan/nguoc, xem chenh EV that nam o dau trong phan phoi.
  (b) bien the mem hon: thay vi BO het nguoc mau, chi bo nen co THAN NGUOC LON (>x% range),
      giu lai doji/than nguoc nho.
  (c) do lai tren toan bo lich su (khong chi 5-7) de xem huong co on dinh khong.
"""
import sys, os, random, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imp_reversal_sweep as S
import rev_bodydir_ab as A

TICK = S.TICK
LIVE = S.LIVE
random.seed(11)


def outcomes(B, sigs, rr):
    """tra ve list R cua tung lenh da dong (amb tinh la SL — bi quan, khop score())."""
    import reversal_vwap as rv
    out = []
    for s in sigs:
        r = s['risk_t'] * TICK
        tgt = s['entry'] + rr * r if s['side'] == 'LONG' else s['entry'] - rr * r
        o = rv.hit(B, s['i'], s['side'], s['sl'], tgt)
        if o not in ('TP', 'SL', 'amb'): continue
        out.append((rr if o == 'TP' else -1.0, s['same']))
    return out


def perm_test(pairs, iters=100000):
    same = [r for r, sm in pairs if sm]
    diff = [r for r, sm in pairs if not sm]
    if not same or not diff: return None
    obs = st.mean(same) - st.mean(diff)
    allr = [r for r, _ in pairs]
    n = len(same); ge = 0
    for _ in range(iters):
        random.shuffle(allr)
        d = st.mean(allr[:n]) - st.mean(allr[n:])
        if d >= obs: ge += 1
    return obs, ge / iters, len(same), len(diff)


def main():
    B = S.bars()
    sig = S.in_window(B, A.detect2(B))

    print("=" * 104)
    print("(a) KIEM DINH HOAN VI — chenh lech EV (thuan mau - nguoc mau) co phai nhieu khong?")
    for rr in (1.0, 1.5, 2.0, 3.0):
        res = perm_test(outcomes(B, sig, rr))
        if not res: continue
        obs, p, ns, nd = res
        verdict = "CO Y NGHIA" if p < 0.05 else ("gan nguong" if p < 0.15 else "KHONG y nghia (nhieu)")
        print(f"  RR={rr:<4} chenh EV = {obs:+.3f}R  (n thuan={ns}, n nguoc={nd})   p 1-duoi = {p:.3f}  -> {verdict}")

    print("\n" + "=" * 104)
    print("(b) BIEN THE MEM — chi bo nen co THAN NGUOC LON (giu doji/than nguoc nho)")
    print("    (than nguoc do bang |c-o|/range cua nen kich hoat)")

    def detect_soft(B, max_counter_body, **kw):
        out = []
        for s in A.detect2(B, **kw):
            if s['same']:
                out.append(s); continue
            b = B[s['arm_i']]
            cb = abs(b['c'] - b['o']) / b['rng'] if b['rng'] > 0 else 0
            if cb <= max_counter_body: out.append(s)
        return out

    for rr in (1.5, 3.0):
        print(f"  --- RR={rr} ---")
        S.fmt(S.score(B, sig, rr), "V0 LIVE (giu het)")
        for mcb in (0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40):
            s2 = S.in_window(B, detect_soft(B, mcb))
            S.fmt(S.score(B, s2, rr), f"bo than nguoc > {mcb:.2f}")

    print("\n" + "=" * 104)
    print("(c) ON DINH THEO THANG — V0 vs A1 (bo nguoc mau) tren MOI RR")
    for rr in (1.0, 1.5, 2.0, 3.0):
        v0 = S.score(B, sig, rr)
        a1 = S.score(B, [x for x in sig if x['same']], rr)
        print(f"  RR={rr:<4} V0 EV {v0['ev']:+.3f} net {v0['net']:+5.1f}R  |  A1 EV {a1['ev']:+.3f} net {a1['net']:+5.1f}R"
              f"   (chenh EV {a1['ev']-v0['ev']:+.3f})")

    print("\n" + "=" * 104)
    print("(d) NHANH CBR co bi anh huong khong? (CBR da co san `c>o`/`c<o` trong dieu kien resume)")
    print("    -> KHONG doi. Fix chi cham nhanh QUAY_DAU.")


if __name__ == "__main__":
    main()
