"""SETUP A — 'Lần theo dòng tiền lớn' (sách trang 25-28, quy tắc p50, p52-53, POC đảo vai p55-56).
Sách:
 1. Tìm vùng tích lũy thanh khoản cao (đi ngang).
 2. POC của vùng đó.
 3. Chờ giá rời vùng (phe mua/bán 'đua lệnh') rồi quay về POC.
 4. Đặt limit tại POC, 'lệch vào trong một chút' để dễ khớp; theo hướng giá đã rời vùng.
 5. SL 12 pip / TP 10 pip trên M30 EURUSD (~1,3 / 1,1 ATR M30) — quy đổi theo ATR khung dùng.
 Quy tắc p50: mức đã test (chạm 0-3 pip rồi quay 8 pip) thì bỏ; giá tới mức bằng nến dài thì bỏ.
 p52: mức cũ hơn 30 ngày bỏ. p33: chỉ đánh thuận xu hướng.
 p55-56: bị SL tại POC -> đặt lệnh ngược lại ngay tại mức đó ('90% đảo chiều').
"""
import numpy as np
from core import resample, simulate, TICK


def find_zones(d, tf, Lmin, H, D, M):
    """Trả list zone: dict(k0,k1,dir,arm_i (M1 index bắt đầu đặt lệnh), poc, atr, hi, lo)."""
    r = resample(d, tf)
    h, l, c, atr = r.h.values, r.l.values, r.c.values, r.atr.values
    N = len(r); zones = []; k = 15
    while k < N - 1:
        a = atr[k - 1]
        if not np.isfinite(a) or a <= 0:
            k += 1; continue
        hi, lo, m = h[k], l[k], k
        while m + 1 < N and max(hi, h[m + 1]) - min(lo, l[m + 1]) <= H * a:
            m += 1; hi = max(hi, h[m]); lo = min(lo, l[m])
        if m - k + 1 >= Lmin:
            # rời vùng: trong M nến sau vùng, giá đi xa mép >= D*ATR, và trước đó không chạm mép đối diện
            dirn = 0; q = None
            for qq in range(m + 1, min(m + 1 + M, N)):
                up = h[qq] - hi; dn = lo - l[qq]
                if up >= D * a and dn <= 0:
                    dirn, q = 1, qq; break
                if dn >= D * a and up <= 0:
                    dirn, q = -1, qq; break
                if up > 0 and dn > 0:
                    break
            if dirn:
                i0, i1 = r.i0[k], r.i1[m]
                t0, vol = d.profile(i0, i1)
                if t0 is not None:
                    poc = (t0 + int(np.argmax(vol))) * TICK
                    zones.append(dict(k0=k, k1=m, dir=dirn, arm_i=int(r.i1[q]), poc=poc, atr=a, hi=hi, lo=lo,
                                      zone_i0=int(i0), zone_i1=int(i1)))
            k = m + 1
        else:
            k += 1
    return zones, r


def trend_ok(d, r, zone, mode):
    if mode == 'none':
        return True
    i = zone['arm_i'] - 1
    if mode == 'day':      # thuận xu hướng: giá hiện tại so với giá 1 phiên trước (1380 nến M1)
        j = max(i - 1380, 0)
        return np.sign(d.c[i] - d.c[j]) == zone['dir']
    if mode == 'day2':
        j = max(i - 2760, 0)
        return np.sign(d.c[i] - d.c[j]) == zone['dir']
    raise ValueError(mode)


def run(d, tf=30, Lmin=6, H=2.0, D=1.5, M=6, SLm=1.3, TPm=1.1, off=0.1, expire_days=30, trend='day',
        near=0.3, bounce=0.9, fast=1.8, flip=False, cost=0.2, max_wait=None):
    zones, r = find_zones(d, tf, Lmin, H, D, M)
    trades = []
    # dải range của tf nến M1 gần nhất (để luật 'nến dài tới mức')
    rng_hi = None
    for z in zones:
        if not trend_ok(d, r, z, trend):
            continue
        s = z['dir']; a = z['atr']
        entry = round((z['poc'] + s * off * a) / TICK) * TICK
        sl = entry - s * SLm * a; tp = entry + s * TPm * a
        i_start = z['arm_i']
        # giá lúc đặt lệnh phải còn ở phía ngoài (đã rời vùng)
        if s * (d.c[i_start - 1] - entry) <= 0:
            continue
        i_exp = i_start + (max_wait if max_wait else expire_days * 1380)
        state = dict(near=False)

        def cancel(i, entry=entry, s=s, a=a, state=state):
            # p50 #2: đã gần chạm (0-3 pip ~ near*ATR) rồi quay xa (8 pip ~ bounce*ATR) -> mức đã dùng
            dist_lo = s * (d.l[i] - entry) if s == 1 else s * (d.h[i] - entry)
            if dist_lo <= near * a:
                state['near'] = True
            if state['near'] and s * ((d.h[i] if s == 1 else d.l[i]) - entry) >= bounce * a and dist_lo > 0:
                return True
            # p50 #3: giá lao tới mức bằng nến dài -> bỏ
            if fast and i - tf >= 0:
                w0 = i - tf
                seg_h = d.h[w0:i].max(); seg_l = d.l[w0:i].min()
                if seg_h - seg_l > fast * a and s * (d.c[i - 1] - d.c[w0]) < 0:
                    return True
            return False

        t = simulate(d, 'buy' if s == 1 else 'sell', entry, sl, tp, i_start, i_exp, limit=True, cost=cost,
                     cancel_fn=cancel)
        if t is None:
            continue
        t.update(setup='A', zone_dir=s)
        trades.append(t)
        if flip and t['out'] == 'sl':
            # p55-56: lệnh ngược lại tại chính mức vừa bị phá
            s2 = -s
            e2 = entry
            t2 = simulate(d, 'buy' if s2 == 1 else 'sell', e2, e2 - s2 * SLm * a, e2 + s2 * TPm * a, t['j'] + 1,
                          t['j'] + 1 + expire_days * 1380, limit=True, cost=cost)
            if t2 is not None:
                t2.update(setup='A-flip', zone_dir=s2)
                trades.append(t2)
    return trades, zones
