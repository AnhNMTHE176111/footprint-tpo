#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB4-C3 co edge THAT khong? 2 test:
 (1) NULL MODEL: 500 lan lay 304 diem vao NGAU NHIEN (cung phia, cung phan phoi risk,
     cung cua so, cung Gate thanh khoan) -> phan phoi net R. Xem +41R nam o percentile nao.
 (2) DO ON DINH THAM SO: quet quanh C3. Dinh don doc = overfit; cao nguyen = co the that.
"""
import random, statistics as st
import reversal_vwap as rv, entry_dxfeed as ed, probe_kb4_zone as K
TICK = K.TICK
C3 = dict(one_arm=True, one_per_day=True, leg_min=5.0, trend=True)
B = rv.load_dxfeed(K.DX); Z = ed.build_zones(B)

def inwin(s): return s['dt'].year == 2026 and 5 <= s['dt'].month <= 7
sig = [s for s in K.detect(B, Z, mode='AB', **C3) if inwin(s)]
risks = [s['risk_t'] for s in sig]
nlong = sum(1 for s in sig if s['side'] == 'LONG')
print(f"KB4-C3: n={len(sig)}  LONG {nlong}/{len(sig)}  risk TB {sum(risks)/len(risks):.1f} tick")

def net_of(entries, rr):
    tot = 0.0; closed = 0
    for i, side, rt in entries:
        e = B[i]['c']; r = rt * TICK
        sl = e - r if side == 'LONG' else e + r
        tgt = e + rr * r if side == 'LONG' else e - rr * r
        o = rv.hit(B, i, side, sl, tgt)
        if o not in ('TP', 'SL', 'amb'): continue
        closed += 1; tot += rr if o == 'TP' else -1
    return tot, closed

real = net_of([(s['i'], s['side'], s['risk_t']) for s in sig], 2.0)
print(f"THAT (dung SL cua signal): net {real[0]:+.1f}R tren {real[1]} lenh")

# pool cac nen hop le trong cua so
pool = [i for i, b in enumerate(B) if inwin(b) and b['v'] >= 20 and b['since_gap'] >= 20 and b['vma'] >= 12]
print(f"pool nen hop le = {len(pool)}")
random.seed(7)
sims = []
for _ in range(500):
    ent = [(random.choice(pool), 'LONG' if random.random() < nlong/len(sig) else 'SHORT',
            random.choice(risks)) for _ in range(len(sig))]
    sims.append(net_of(ent, 2.0)[0])
sims.sort()
mu = st.mean(sims); sd = st.pstdev(sims)
pct = sum(1 for x in sims if x < real[0]) / len(sims)
print(f"\nNULL (500 lan, vao ngau nhien): net TB {mu:+.1f}R  sd {sd:.1f}R  "
      f"p5 {sims[24]:+.1f}R  p50 {sims[250]:+.1f}R  p95 {sims[474]:+.1f}R")
print(f"=> KB4-C3 (+{real[0]:.1f}R) nam o percentile {pct*100:.1f}% cua ngau nhien  "
      f"(z = {(real[0]-mu)/sd:+.2f})")

print("\n" + "="*100)
print("DO ON DINH THAM SO quanh C3 (net R @2R, cua so 5-7/2026):")
def netcfg(**kw):
    s = [x for x in K.detect(B, Z, mode='AB', **{**C3, **kw}) if inwin(x)]
    r = K.score(B, s, 2.0)
    return r['n'], r['net'], r['wr']
for name, vals in (('leg_min', [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]),
                   ('w', [4, 6, 8, 10, 12]),
                   ('ztol_t', [4, 7, 10, 14]),
                   ('body_c', [0.35, 0.45, 0.55]),
                   ('vsa_c', [1.0, 1.2, 1.5, 2.0]),
                   ('pen_t', [10, 20, 30]),
                   ('cap_t', [40, 55, 70])):
    out = []
    for v in vals:
        n, net, wr = netcfg(**{name: v})
        out.append(f"{v}:{net:+.0f}R(n{n})")
    print(f"  {name:9s} " + "  ".join(out))
