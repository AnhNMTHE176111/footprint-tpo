"""Vòng 2: ba cơ chế của sách ở khung scalp.
R2-flip  : POC bị phá dứt khoát -> lần retest đầu từ phía bên kia -> vào theo hướng phá (p53, p55-56).
R2-lvn   : giá đóng xuyên LVN -> chạy tới HVN kế (p68-71), hình học SL/TP sửa lại.
R2-fake  : nến pin râu dài thò qua mép VA rồi đóng lại vào trong -> đánh ngược về POC (p90-92).
"""
import numpy as np
from core import resample, simulate, poc_va, TICK
from setups_other import hvn_lvn
import setup_a as A


def poc_levels(d, src='sess', tf=5, max_age_days=30):
    """Danh sách mức POC: (giá, M1 index bắt đầu được dùng, M1 index hết hạn)."""
    lv = []
    if src in ('sess', 'both'):
        for s in range(d.nsess):
            if not d.full[s]:
                continue
            i0, i1 = d.sess_start[s], d.sess_end[s]
            t0, vol = d.profile(i0, i1)
            poc = (t0 + int(np.argmax(vol))) * TICK
            lv.append((poc, i1, min(i1 + max_age_days * 1380, d.n), 'sess'))
    if src in ('zone', 'both'):
        zones, r = A.find_zones(d, tf, 6, 2.0, 1.5, 6)
        for z in zones:
            lv.append((z['poc'], z['zone_i1'], min(z['zone_i1'] + 2 * 1380, d.n), 'zone'))
    return lv


def flip(d, src='sess', tf=5, brk=1.0, SLm=1.3, TPm=1.1, off=0.1, cost=0.2, max_age_days=30, trend='none'):
    r = resample(d, tf)
    c, atr, i1s = r.c.values, r.atr.values, r.i1.values
    trades = []
    for (lvl, ia, iz, kind) in poc_levels(d, src, tf, max_age_days):
        ka = np.searchsorted(i1s, ia)
        kz = np.searchsorted(i1s, iz)
        side0 = np.sign(c[ka - 1] - lvl) if ka > 0 else 0
        k = ka
        while k < kz:
            sgn = np.sign(c[k] - lvl)
            a = atr[k]
            # phá: nến tf đóng cửa ở phía bên kia, cách mức >= brk*ATR
            if side0 != 0 and sgn == -side0 and abs(c[k] - lvl) >= brk * a:
                sd = int(sgn)
                entry = round((lvl + sd * off * a) / TICK) * TICK
                sl = entry - sd * SLm * a; tp = entry + sd * TPm * a
                i_start = int(i1s[k])
                s_end = d.sess_end[d.sess[i_start - 1]]
                t = simulate(d, 'buy' if sd == 1 else 'sell', entry, sl, tp, i_start, s_end, cost=cost)
                if t:
                    t.update(setup='R2-flip-' + kind); trades.append(t)
                break          # mỗi mức chỉ dùng 1 lần
            if sgn != 0:
                side0 = sgn
            k += 1
    return trades


def lvn(d, hours=24, tf=5, SLm=1.0, min_rr=1.0, cost=0.2, smooth=5, refresh=60, sl_mode='atr'):
    """Profile 'visible range' = hours giờ gần nhất (tính lại mỗi refresh phút).
    Nến tf đóng xuyên LVN từ phía HVN này -> vào market, TP = đỉnh HVN kia, SL = SLm*ATR(tf) sau LVN."""
    r = resample(d, tf)
    c, atr, i1s = r.c.values, r.atr.values, r.i1.values
    trades = []; used = {}
    lvns = []; last_ref = -10 ** 9
    W = hours * 60
    for k in range(20, len(r)):
        ie = int(i1s[k])
        if ie >= d.n or ie - W < 0:
            continue
        if ie - last_ref >= refresh:
            t0, vol = d.profile(ie - W, ie)
            lvns = hvn_lvn(t0, vol, smooth=smooth) if t0 is not None else []
            last_ref = ie
        pc, cc, a = c[k - 1], c[k], atr[k]
        if d.min_of_sess[ie] > 1340:
            continue
        for (lv_, lo_p, hi_p) in lvns:
            key = round(lv_, 1)
            if used.get(key, -1) > ie - 1380:
                continue
            if pc > lv_ >= cc and pc <= hi_p:
                sd, tgt = -1, lo_p
            elif pc < lv_ <= cc and pc >= lo_p:
                sd, tgt = 1, hi_p
            else:
                continue
            used[key] = ie
            px = d.o[ie]
            sl = (lv_ - sd * SLm * a) if sl_mode == 'atr' else ((hi_p if sd == -1 else lo_p) + sd * 0)
            if sd * (tgt - px) < min_rr * abs(px - sl):
                continue
            t = simulate(d, 'buy' if sd == 1 else 'sell', None, sl, tgt, ie, ie + 1, limit=False, cost=cost)
            if t:
                t.update(setup='R2-lvn'); trades.append(t)
    return trades


def fake(d, tf=5, va='prev', wick=0.5, SLbuf=0.1, cost=0.2, tgt='poc', min_rr=1.0, max_per_side=1):
    """va='prev': VA phiên Globex trước. va='dev': VA đang hình thành của phiên hiện tại (tính tới nến trước)."""
    r = resample(d, tf)
    o, h, l, c, atr, i0s, i1s, ss = (r[k].values for k in ['o', 'h', 'l', 'c', 'atr', 'i0', 'i1', 'sess'])
    prevva = {}
    for s in range(1, d.nsess):
        if d.full[s - 1]:
            t0, vol = d.profile(d.sess_start[s - 1], d.sess_end[s - 1])
            prevva[s] = poc_va(t0, vol)
    trades = []; cnt = {}
    for k in range(20, len(r)):
        s = ss[k]; ie = int(i1s[k])
        if ie >= d.n or d.min_of_sess[ie] > 1340:
            continue
        if va == 'prev':
            if s not in prevva:
                continue
            poc, vah, val = prevva[s]
        else:
            st = d.sess_start[s]
            if i0s[k] - st < 120:
                continue
            t0, vol = d.profile(st, int(i0s[k]))
            poc, vah, val = poc_va(t0, vol)
        rg = h[k] - l[k]
        if rg <= 0:
            continue
        for sd in (-1, 1):
            if cnt.get((s, sd), 0) >= max_per_side:
                continue
            if sd == -1 and h[k] > vah and c[k] < vah and (h[k] - max(o[k], c[k])) >= wick * rg:
                sl = h[k] + SLbuf * atr[k]
            elif sd == 1 and l[k] < val and c[k] > val and (min(o[k], c[k]) - l[k]) >= wick * rg:
                sl = l[k] - SLbuf * atr[k]
            else:
                continue
            px = d.o[ie]
            risk = abs(px - sl)
            tp = poc if tgt == 'poc' else px + sd * tgt * risk
            if sd * (tp - px) < min_rr * risk:
                continue
            cnt[(s, sd)] = cnt.get((s, sd), 0) + 1
            t = simulate(d, 'buy' if sd == 1 else 'sell', None, sl, tp, ie, ie + 1, limit=False, cost=cost)
            if t:
                t.update(setup='R2-fake-' + va); trades.append(t)
    return trades
