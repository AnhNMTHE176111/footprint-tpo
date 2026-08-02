#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REV_BODYDIR_AB — dua luat "NEN VAO LENH PHAI THUAN MAU" (Fix A cua EntrySignal, 2026-08-02)
sang nhanh QUAY_DAU (reversal-at-VWAP) cua RunnerSignal.cs / WyckoffRunner.cs.

Nhanh CBR (pha->hoi->tiep dien) DA co san luat nay (`bj.C > bj.O` / `bj.C < bj.O` trong `resume`),
nen KHONG can sua. Nhanh QUAY_DAU thi KHONG kiem than nen:
    rejShort = UW>=WickFrac*rng && Cpos<=0.45 && C<vw && Brat>=0.30 && Vratio>=RevVsaConf
=> nen TRANG (c>o) van ban SHORT, nen DO van ban LONG — dung loi da vach ra o EntrySignal.

Replicator: imp_reversal_sweep.detect() (khop tung hang so C#, LIVE dict).
BUOC 0 (quan trong nhat): do RIENG nhom nguoc mau vs thuan mau. Neu nguoc mau KHONG te hon
thi luat nay KHONG co co so o runner — bao that, khong ship.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imp_reversal_sweep as S
import reversal_vwap as rv
from collections import defaultdict

TICK = S.TICK
LIVE = S.LIVE


def body_dir(b):
    return 1 if b['c'] > b['o'] else -1 if b['c'] < b['o'] else 0


def detect2(B, require_body=False, confirm_w=0, confirm_vsa=1.2,
            kill_vwap_cross=False, **kw):
    """Ban sao detect() + luat thuan mau + cua so cho xac nhan (ARM->CONFIRM).

    require_body=False, confirm_w=0  -> y het LIVE.
    require_body=True,  confirm_w=0  -> A1: bo han lenh nguoc mau.
    require_body=True,  confirm_w=W  -> A2: cho toi da W nen, nen nao thuan mau + VSA>=confirm_vsa
                                        thi nen DO moi la nen vao. Neo SL gop ca 2 nen. Cap van ap.
    """
    P = dict(LIVE); P.update(kw)
    vol_floor = P['vol_floor']; warmup = P['warmup']
    tol = P['vwap_tol_t'] * TICK; appro = P['approach_bars']
    wick = P['wick_frac']; h = P['cpos_h']; body = P['body_min']; vsac = P['vsa_conf']
    tf = P['trend_filter']; tN = P['trend_bars']; ttol = P['trend_tol_t']
    buf = P['sl_buf_t'] * TICK; cap = P['sl_cap_t']; rmin = P['risk_min']; cd = P['cooldown']
    cpos_lo = 0.5 - h; cpos_hi = 0.5 + h
    N = len(B); raw = []
    start = max(rv.VSA_MA + 2, tN if tf else 0)

    def gate_ok(b):
        return b['v'] >= vol_floor and b['since_gap'] >= warmup and b['vma'] >= vol_floor * 0.6

    for i in range(start, N):
        b = B[i]
        if not gate_ok(b): continue
        rng = b['rng']
        if rng <= 0: continue
        vw = b['vwap']
        touch_up = b['hi'] >= vw - tol
        rej_short = (b['uw'] >= wick * rng and b['cpos'] <= cpos_lo and b['c'] < vw
                     and b['brat'] >= body and b['vratio'] >= vsac)
        touch_dn = b['lo'] <= vw + tol
        rej_long = (b['lw'] >= wick * rng and b['cpos'] >= cpos_hi and b['c'] > vw
                    and b['brat'] >= body and b['vratio'] >= vsac)
        appro_up = appro_dn = False
        for k in range(max(0, i - appro), i):
            if B[k]['c'] < vw: appro_up = True
            if B[k]['c'] > vw: appro_dn = True
        side = 0; anchor = 0.0
        if touch_up and rej_short and appro_up: side = -1; anchor = max(b['hi'], vw)
        elif touch_dn and rej_long and appro_dn: side = +1; anchor = min(b['lo'], vw)
        if side == 0: continue
        if tf and S.trend_at(B, i, tN, ttol) != side: continue

        same = (body_dir(b) == side)
        ci = i                       # nen vao lenh
        nwait = 0
        if require_body and not same:
            if confirm_w <= 0:
                continue
            ci = -1
            for j in range(i + 1, min(N, i + 1 + confirm_w)):
                bj = B[j]
                if kill_vwap_cross and (bj['c'] > bj['vwap'] if side < 0 else bj['c'] < bj['vwap']):
                    break
                if not gate_ok(bj): continue
                if body_dir(bj) != side: continue
                if bj['vratio'] < confirm_vsa: continue
                ci = j; nwait = j - i
                anchor = max(anchor, bj['hi']) if side < 0 else min(anchor, bj['lo'])
                break
            if ci < 0: continue

        bc = B[ci]
        entry = bc['c']
        if side > 0: sl = anchor - buf; risk = (entry - sl) / TICK
        else: sl = anchor + buf; risk = (sl - entry) / TICK
        if risk <= rmin or risk > cap: continue
        raw.append(dict(i=ci, dt=bc['dt'], side=('LONG' if side > 0 else 'SHORT'),
                        entry=entry, sl=sl, risk_t=risk, vsa=b['vratio'],
                        same=same, nwait=nwait, arm_i=i))
    out = []; last = {}
    for s in sorted(raw, key=lambda x: x['i']):
        if s['i'] - last.get(s['side'], -999) < cd: continue
        out.append(s); last[s['side']] = s['i']
    return out


def run(B, label, **kw):
    s = S.in_window(B, detect2(B, **kw))
    if LIVE['dead']:
        s = S.apply_dead(s, LIVE['dead_lo'], LIVE['dead_hi'])
    r = S.score(B, s, kw.get('rr', LIVE['rr']))
    S.fmt(r, label)
    return r


def main():
    B = S.bars()
    print(f"bars={len(B)}  {B[0]['dt']} -> {B[-1]['dt']}   RR={LIVE['rr']}  (cua so do: 5-7/2026)")

    # ---------- BUOC 0: nguoc mau co THUC SU te hon khong? ----------
    print("\n" + "=" * 104)
    print("(0) TACH NHOM — nen kich hoat THUAN mau vs NGUOC mau (cung 1 bo tin hieu LIVE)")
    sig = S.in_window(B, detect2(B))
    for name, sub in (("THUAN mau (c thuan side)", [x for x in sig if x['same']]),
                      ("NGUOC mau / doji", [x for x in sig if not x['same']])):
        S.fmt(S.score(B, sub, LIVE['rr']), name)
    ns, nd = sum(x['same'] for x in sig), sum(not x['same'] for x in sig)
    print(f"   -> ty le nguoc mau: {nd}/{len(sig)} = {nd/max(1,len(sig))*100:.0f}%")

    # ---------- A/B ----------
    print("\n" + "=" * 104)
    print("(1) A/B — RR 1.5 (RevRR dang ship)")
    run(B, "V0 LIVE (khong kiem than)")
    run(B, "A1 bo lenh nguoc mau", require_body=True, confirm_w=0)
    for w in (2, 3, 4, 6):
        run(B, f"A2 cho xac nhan W={w}", require_body=True, confirm_w=w)
    print("   -- bien the: nen xac nhan doi VSA cao hon --")
    for cv in (1.5, 1.8):
        run(B, f"A2 W=3 VSAxn>={cv}", require_body=True, confirm_w=3, confirm_vsa=cv)
    print("   -- bien the: huy cho khi dong xuyen nguoc VWAP --")
    run(B, "A2 W=3 +huy xuyen VWAP", require_body=True, confirm_w=3, kill_vwap_cross=True)

    # ---------- kiem tra ben ngoai RR ----------
    print("\n" + "=" * 104)
    print("(2) KIEM CHEO — RR khac (co phai chi dung o 1.5?)")
    for rr in (1.0, 2.0, 3.0):
        print(f"  --- RR={rr} ---")
        run(B, "V0 LIVE", rr=rr)
        run(B, "A1 bo nguoc mau", require_body=True, confirm_w=0, rr=rr)
        run(B, "A2 W=3", require_body=True, confirm_w=3, rr=rr)

    # ---------- kiem tra ngoai cua so toi uu ----------
    print("\n" + "=" * 104)
    print("(3) KIEM CHEO — mo rong cua so ra toan bo du lieu (2025-11 .. 2026-07)")
    for label, kw in (("V0 LIVE", {}),
                      ("A1 bo nguoc mau", dict(require_body=True, confirm_w=0)),
                      ("A2 W=3", dict(require_body=True, confirm_w=3))):
        s = detect2(B, **kw)
        S.fmt(S.score(B, s, LIVE['rr']), label)


if __name__ == "__main__":
    main()
