#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THI NGHIEM SACH — vi tri "bong no" (bubble) trong nen co du bao gi khong?
================================================================================
Vi sao can file nay: ket qua X5 trong crow_run.py 'delta' la PARTITION tren tap lenh cua
mot LOI AM -> chi ket luan duoc "nhom nao it te hon". File nay do hieu ung THUAN, KHONG
phu thuoc setup nao, tren TOAN BO nen co footprint per-level (n ~ 50-76k).

Dac ta (chot truoc khi chay):
  Voi moi nen i co: per-level, rng>0, v>=VOLFLOOR(20), since_gap>=20, medrng(100 nen truoc) co san.
  - pos_aggr = (gia o co AGGRESSOR THUAN HUONG NEN lon nhat - lo)/rng
       nen tang -> o ask_vol lon nhat (mua chu dong);  nen giam -> o bid_vol lon nhat.
       Chuan hoa theo huong: pos_n = pos (nen tang) | 1-pos (nen giam)
       => pos_n ~ 1 nghia la "bong no SAT CUC TRI THUAN HUONG" (buy no sat high) = cai video CAM.
  - pos_poc  = tuong tu nhung lay o TONG VOLUME lon nhat (POC cua nen = HVN cell).
  - ddom     = delta/volume cua nen, chuan hoa theo huong nen.
  THI NGHIEM 1 (huong di tiep) — triple barrier doi xung, chuan hoa bien dong:
       tu close nen i, dat 2 moc: +H*medrng va -H*medrng (H=1.5). Trong 60 nen sau, moc nao
       bi cham TRUOC (kiem lo/hi tung nen; cung nen cham ca 2 -> bo phieu 'ambiguous', loai).
       Do P(di tiep THUAN huong nen i) theo bin cua pos_n. Base ~50% => lech la tin hieu.
  THI NGHIEM 2 (muc bubble giu hay vo) — tu nen i, trong 60 nen sau, gia co DONG vuot qua
       muc bubble THEO CHIEU NGUOC voi aggressor (buy bubble -> co dong duoi bubble-5t?) khong.
       Do ty le GIU theo bin pos_n. "Hap thu tao ho tro" => bubble o phia duoi + giu cao.
  Doi chung: bin theo pos_n {[0,.2) [.2,.4) [.4,.6) [.6,.8) [.8,1]} x {vratio<1.5, >=1.5}.
  Sai so: se (p) = sqrt(p(1-p)/n); chi coi la that khi lech >= 2se so voi base cua CUNG lop vratio.

Chay: python3 crow_bubble.py
"""
import sys, os, statistics as st
from collections import defaultdict, deque

R = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research"
sys.path.insert(0, R)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entry_dxfeed as E
import fp_merged
import crow_v1 as K

TICK = E.TICK
VF = E.VOLFLOOR_FROZEN
H = 1.5
FWD = 60
BINS = ((0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.01))


def se(p, n):
    return (p * (1 - p) / n) ** 0.5 if n > 0 else 9.9


def barrier(B, i, up, h):
    """Moc nao cham truoc: THUAN huong nen i hay NGUOC. Tra 1 (thuan), 0 (nguoc), None (mo ho/het data)."""
    c = B[i]['c']
    tgt = c + h if up else c - h
    stp = c - h if up else c + h
    for j in range(i + 1, min(len(B), i + 1 + FWD)):
        b = B[j]
        hitT = (b['hi'] >= tgt) if up else (b['lo'] <= tgt)
        hitS = (b['lo'] <= stp) if up else (b['hi'] >= stp)
        if hitT and hitS:
            return None
        if hitT:
            return 1
        if hitS:
            return 0
    return None


def hold(B, i, up, bub_px):
    """Muc bubble co GIU khong: trong FWD nen sau, KHONG co nen nao DONG vuot qua bub_px
    theo chieu nguoc voi aggressor (buy bubble -> khong dong duoi bub_px - 5 tick)."""
    lim = bub_px - 5 * TICK if up else bub_px + 5 * TICK
    for j in range(i + 1, min(len(B), i + 1 + FWD)):
        b = B[j]
        if (b['c'] < lim) if up else (b['c'] > lim):
            return 0
    return 1


def bub_price(b, up, mode):
    lv = b.get('levels') or {}
    if not lv:
        return None
    if mode == 'poc':
        return max(lv, key=lambda k: lv[k]['vol'])
    key = 'ask' if up else 'bid'
    if max(lv[k][key] for k in lv) <= 0:
        return None
    return max(lv, key=lambda k: lv[k][key])


def main():
    B = fp_merged.load_merged()
    K.prep(B)
    rows = []
    for i, b in enumerate(B):
        if not b.get('has_delta') or b['rng'] <= 0 or b['medrng'] is None:
            continue
        if b['v'] < VF or b['since_gap'] < E.WARMUP_AFTER_GAP or (b.get('v_fp') or 0) <= 0:
            continue
        if not (b['up'] or b['dn']):
            continue
        up = b['up']
        rec = dict(i=i, up=up, ym=b['ym'], vratio=b['vratio'],
                   ddom=(b['ddom'] if up else -b['ddom']))
        for mode in ('aggr', 'poc'):
            p = bub_price(b, up, mode)
            if p is None:
                rec['pos_' + mode] = None
                rec['px_' + mode] = None
            else:
                pos = (p - b['lo']) / b['rng']
                rec['pos_' + mode] = pos if up else 1 - pos
                rec['px_' + mode] = p
        h = H * b['medrng']
        rec['bar'] = barrier(B, i, up, h)
        rows.append(rec)
    print(f"[bubble] n_nen dung duoc = {len(rows)}  ({rows[0]['ym']} -> {rows[-1]['ym']})")

    for mode in ('aggr', 'poc'):
        print(f"\n================ THI NGHIEM 1 — huong di tiep (barrier +-{H}*medrng, {FWD} nen) "
              f"| bubble = o {'AGGRESSOR' if mode == 'aggr' else 'TONG VOLUME'} lon nhat")
        for vlab, vsel in (("moi nen", lambda r: True),
                           ("vratio<1.5", lambda r: r['vratio'] < 1.5),
                           ("vratio>=1.5 (nen 'co bubble that')", lambda r: r['vratio'] >= 1.5)):
            sub = [r for r in rows if vsel(r) and r['bar'] is not None and r['pos_' + mode] is not None]
            if len(sub) < 200:
                continue
            base = sum(r['bar'] for r in sub) / len(sub)
            print(f"  -- {vlab}: n={len(sub)}  P(di tiep thuan huong) BASE = {100*base:.1f}%")
            for lo, hi in BINS:
                s2 = [r for r in sub if lo <= r['pos_' + mode] < hi]
                if len(s2) < 50:
                    print(f"     pos_n [{lo:.1f},{hi:.1f})  n={len(s2):5d}  (qua it)")
                    continue
                p = sum(r['bar'] for r in s2) / len(s2)
                d = p - base
                sig = "***" if abs(d) >= 2 * se(p, len(s2)) else "   "
                print(f"     pos_n [{lo:.1f},{hi:.1f})  n={len(s2):5d}  P={100*p:.1f}%  "
                      f"lech={100*d:+.1f}pp ({d/se(p,len(s2)):+.1f}se) {sig}")

    print(f"\n================ THI NGHIEM 2 — muc bubble GIU hay VO ({FWD} nen, dong vuot 5t la vo)")
    for mode in ('aggr', 'poc'):
        sub = [r for r in rows if r['px_' + mode] is not None and r['vratio'] >= 1.5]
        for r in sub:
            r['hold'] = hold(B, r['i'], r['up'], r['px_' + mode])
        base = sum(r['hold'] for r in sub) / len(sub)
        print(f"  -- mode={mode} (vratio>=1.5): n={len(sub)}  P(GIU) BASE = {100*base:.1f}%")
        for lo, hi in BINS:
            s2 = [r for r in sub if lo <= r['pos_' + mode] < hi]
            if len(s2) < 50:
                continue
            p = sum(r['hold'] for r in s2) / len(s2)
            d = p - base
            sig = "***" if abs(d) >= 2 * se(p, len(s2)) else "   "
            print(f"     pos_n [{lo:.1f},{hi:.1f})  n={len(s2):5d}  P(giu)={100*p:.1f}%  "
                  f"lech={100*d:+.1f}pp ({d/se(p,len(s2)):+.1f}se) {sig}")

    print("\n================ DOI CHUNG — ddom (delta ap dao thuan huong nen)")
    sub = [r for r in rows if r['bar'] is not None]
    base = sum(r['bar'] for r in sub) / len(sub)
    print(f"  n={len(sub)} BASE={100*base:.1f}%")
    for lo, hi in ((-1.01, -0.3), (-0.3, -0.1), (-0.1, 0.1), (0.1, 0.3), (0.3, 0.6), (0.6, 1.01)):
        s2 = [r for r in sub if lo <= r['ddom'] < hi]
        if len(s2) < 50:
            continue
        p = sum(r['bar'] for r in s2) / len(s2)
        d = p - base
        sig = "***" if abs(d) >= 2 * se(p, len(s2)) else "   "
        print(f"     ddom_thuan [{lo:+.2f},{hi:+.2f})  n={len(s2):5d}  P={100*p:.1f}%  "
              f"lech={100*d:+.1f}pp ({d/se(p,len(s2)):+.1f}se) {sig}")

    print("\n================ ON DINH THEO THANG (pos_aggr >=0.8 vs <0.6, vratio>=1.5)")
    sub = [r for r in rows if r['bar'] is not None and r['pos_aggr'] is not None and r['vratio'] >= 1.5]
    bym = defaultdict(lambda: [[], []])
    for r in sub:
        if r['pos_aggr'] >= 0.8:
            bym[r['ym']][0].append(r['bar'])
        elif r['pos_aggr'] < 0.6:
            bym[r['ym']][1].append(r['bar'])
    for ym in sorted(bym):
        hi_, lo_ = bym[ym]
        if len(hi_) < 20 or len(lo_) < 20:
            continue
        print(f"     {ym}: sat cuc tri n={len(hi_):4d} P={100*sum(hi_)/len(hi_):.1f}%  |  "
              f"giua/duoi n={len(lo_):4d} P={100*sum(lo_)/len(lo_):.1f}%  "
              f"chenh={100*(sum(lo_)/len(lo_)-sum(hi_)/len(hi_)):+.1f}pp")


if __name__ == '__main__':
    main()
