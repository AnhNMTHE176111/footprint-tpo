"""Các setup khác trong sách (mỗi hàm ghi rõ trang)."""
import numpy as np
from core import resample, simulate, poc_va, TICK


def rth_bounds(d, s):
    """Phiên pit COMEX 08:20-13:30 ET trong phiên Globex s. Trả (i0, i1) M1."""
    i0, i1 = d.sess_start[s], d.sess_end[s]
    m = d.hour[i0:i1] * 60 + d.minute[i0:i1]
    po = d.pit_open_utc_min[i0]
    idx = np.flatnonzero((m >= po) & (m < po + 310)) + i0
    if len(idx) < 100:
        return None
    return idx[0], idx[-1] + 1


def sess_stats(d, kind='globex'):
    out = {}
    for s in range(d.nsess):
        if not d.full[s]:
            continue
        if kind == 'globex':
            i0, i1 = d.sess_start[s], d.sess_end[s]
        else:
            b = rth_bounds(d, s)
            if b is None:
                continue
            i0, i1 = b
        t0, vol = d.profile(i0, i1)
        poc, vah, val = poc_va(t0, vol)
        hi, lo = d.h[i0:i1].max(), d.l[i0:i1].min()
        out[s] = dict(i0=i0, i1=i1, poc=poc, vah=vah, val=val, hi=hi, lo=lo, t0=t0, vol=vol,
                      pos=(poc - lo) / max(hi - lo, TICK))
    return out


def atr30_at(d, r30, i):
    k = np.searchsorted(r30.i0.values, i, side='right') - 2
    return r30.atr.values[max(k, 0)]


# ---------------- B: mẫu hình P / b / D (p21-23, p30-34) ----------------
def setup_B(d, kind='globex', Pth=0.67, SLm=1.3, TPm=1.1, off=0.1, days=3, trend='none', mode='Pb', cost=0.2):
    """P -> buy tại POC phiên đó khi giá hồi về (p22, p31); b -> sell tại POC (p23, p30).
    mode='D': ngày D (POC giữa) -> sell ở VAH, buy ở VAL, TP về POC (p22, p32)."""
    st = sess_stats(d, kind); r30 = resample(d, 30); trades = []
    keys = sorted(st)
    for a, s in enumerate(keys[:-1]):
        p = st[s]; nxt = keys[a + 1]
        i_start = st[nxt]['i0'] if kind != 'globex' else d.sess_start[nxt]
        i_exp = d.sess_end[min(nxt + days - 1, d.nsess - 1)]
        A = atr30_at(d, r30, i_start)
        orders = []
        if mode == 'Pb':
            if p['pos'] >= Pth:
                orders.append((1, p['poc']))
            elif p['pos'] <= 1 - Pth:
                orders.append((-1, p['poc']))
        else:
            if 1 - Pth < p['pos'] < Pth:
                orders += [(-1, p['vah']), (1, p['val'])]
        for sd, lvl in orders:
            if trend == 'day':
                j = max(i_start - 1380, 0)
                if np.sign(d.c[i_start - 1] - d.c[j]) != sd:
                    continue
            entry = round((lvl + sd * off * A) / TICK) * TICK
            if sd * (d.c[i_start - 1] - entry) <= 0:
                continue          # giá đang ở phía sai -> không phải 'hồi về'
            sl = entry - sd * SLm * A
            tp = p['poc'] if mode == 'D' else entry + sd * TPm * A
            t = simulate(d, 'buy' if sd == 1 else 'sell', entry, sl, tp, i_start, i_exp, cost=cost)
            if t:
                t.update(setup='B-' + mode); trades.append(t)
    return trades


# ---------------- E: quy tắc 80% (p83-86) ----------------
def setup_E(d, kind='rth', SLm=1.3, sl_mode='atr', cost=0.2, need=2):
    """Mở cửa ngoài VA hôm trước, rồi 2 nến 30 phút liên tiếp đóng trong VA -> đi hết VA."""
    st = sess_stats(d, kind); r30 = resample(d, 30); trades = []
    keys = sorted(st)
    for a, s in enumerate(keys[1:]):
        prev = st[keys[a]]; cur = st[s]
        i0, i1 = cur['i0'], cur['i1']
        op = d.o[i0]
        if prev['val'] <= op <= prev['vah']:
            continue
        sd = 1 if op < prev['val'] else -1         # mở dưới VA -> buy lên VAH
        tgt = prev['vah'] if sd == 1 else prev['val']
        # nến 30 phút từ lúc mở
        cnt = 0
        for k in range(i0, i1 - 30, 30):
            c = d.c[k + 29]
            if prev['val'] <= c <= prev['vah']:
                cnt += 1
            else:
                cnt = 0
            if cnt >= need:
                ie = k + 30
                A = atr30_at(d, r30, ie)
                px = d.o[ie]
                sl = px - sd * SLm * A if sl_mode == 'atr' else (prev['val'] - 0.3 * A if sd == 1 else prev['vah'] + 0.3 * A)
                t = simulate(d, 'buy' if sd == 1 else 'sell', None, sl, tgt, ie, ie + 1, limit=False, cost=cost)
                if t:
                    t.update(setup='E-80'); trades.append(t)
                break
    return trades


# ---------------- D: phá vỡ qua LVN (p66-71) ----------------
def hvn_lvn(t0, vol, smooth=5, prom=0.3):
    """Đỉnh khối lượng (HVN) và đáy giữa hai đỉnh (LVN) trên profile làm mượt."""
    k = np.ones(smooth) / smooth
    v = np.convolve(vol, k, mode='same')
    peaks = [i for i in range(1, len(v) - 1) if v[i] >= v[i - 1] and v[i] > v[i + 1] and v[i] >= prom * v.max()]
    # gộp đỉnh quá gần (< 2*smooth)
    merged = []
    for p in peaks:
        if merged and p - merged[-1] < 2 * smooth:
            if v[p] > v[merged[-1]]:
                merged[-1] = p
        else:
            merged.append(p)
    lvns = []
    for a, b in zip(merged[:-1], merged[1:]):
        m = a + int(np.argmin(v[a:b + 1]))
        if v[m] <= 0.5 * min(v[a], v[b]):
            lvns.append(((t0 + m) * TICK, (t0 + a) * TICK, (t0 + b) * TICK))
    return lvns


def setup_D(d, nsess=3, tf=30, SLm=1.3, cost=0.2, entry='close', smooth=5):
    """Profile ghép nsess phiên trước. Nến tf đóng cửa xuyên LVN đi từ HVN này sang HVN kia
    -> vào theo hướng xuyên, TP = đỉnh HVN bên kia (p70: 'mục tiêu tại vùng HVN')."""
    r = resample(d, tf); r30 = resample(d, 30); trades = []
    for s in range(nsess, d.nsess):
        if not d.full[s]:
            continue
        i0 = d.sess_start[s - nsess]; i1 = d.sess_start[s]
        t0, vol = d.profile(i0, i1)
        lv = hvn_lvn(t0, vol, smooth=smooth)
        ks = np.flatnonzero(r.sess.values == s)
        used = set()
        for k in ks[1:]:
            pc, c = r.c.values[k - 1], r.c.values[k]
            for (lvn, lo_peak, hi_peak) in lv:
                if lvn in used:
                    continue
                if pc > lvn >= c and pc <= hi_peak:   # xuyên xuống
                    sd, tgt = -1, lo_peak
                elif pc < lvn <= c and pc >= lo_peak:
                    sd, tgt = 1, hi_peak
                else:
                    continue
                used.add(lvn)
                ie = int(r.i1.values[k])
                if ie >= d.sess_end[s]:
                    continue
                A = atr30_at(d, r30, ie)
                sl = lvn - sd * SLm * A
                if entry == 'close':
                    t = simulate(d, 'buy' if sd == 1 else 'sell', None, sl, tgt, ie, ie + 1, limit=False, cost=cost)
                else:   # 'retest': limit tại LVN (p70: 'SELL limit tại mức cao hơn')
                    t = simulate(d, 'buy' if sd == 1 else 'sell', lvn, sl, tgt, ie, d.sess_end[s], cost=cost)
                if t:
                    t.update(setup='D-lvn'); trades.append(t)
    return trades


# ---------------- I: fake out quanh Value Area (p90-93) ----------------
def setup_I(d, tf=30, kind='globex', wick=0.6, SLbuf=0.1, cost=0.2, tgt='poc'):
    """Nến pin râu dài thò qua VAH/VAL phiên trước rồi đóng lại vào trong VA -> đánh ngược, TP POC."""
    st = sess_stats(d, kind); r = resample(d, tf); trades = []
    keys = sorted(st)
    for a, s in enumerate(keys[1:]):
        prev = st[keys[a]]
        ks = np.flatnonzero(r.sess.values == s)
        done = {1: False, -1: False}
        for k in ks:
            o, h, l, c, A = r.o.values[k], r.h.values[k], r.l.values[k], r.c.values[k], r.atr.values[k]
            rngk = h - l
            if rngk <= 0 or not np.isfinite(A):
                continue
            ie = int(r.i1.values[k])
            if ie >= d.sess_end[s] - 30:
                break
            if not done[-1] and h > prev['vah'] and c < prev['vah'] and (h - max(o, c)) >= wick * rngk:
                sl = h + SLbuf * A
                t = simulate(d, 'sell', None, sl, prev['poc'], ie, ie + 1, limit=False, cost=cost)
                done[-1] = True
                if t:
                    t.update(setup='I-fake'); trades.append(t)
            if not done[1] and l < prev['val'] and c > prev['val'] and (min(o, c) - l) >= wick * rngk:
                sl = l - SLbuf * A
                t = simulate(d, 'buy', None, sl, prev['poc'], ie, ie + 1, limit=False, cost=cost)
                done[1] = True
                if t:
                    t.update(setup='I-fake'); trades.append(t)
    return trades


# ---------------- F: Open Drive (p77-78) ----------------
def setup_F(d, kind='rth', cost=0.2, tp_R=None):
    """Mở ngoài vùng giá hôm trước (ngoài range) và nến A (30 phút đầu) đi tiếp theo hướng mở
    -> theo hướng đó; mốc đầu A không bị phá trong phiên (sách). Vào đầu B, SL = cực trị đối diện của A."""
    st = sess_stats(d, kind); trades = []
    keys = sorted(st)
    for a, s in enumerate(keys[1:]):
        prev = st[keys[a]]; cur = st[s]
        i0 = cur['i0']; op = d.o[i0]
        Ah, Al, Ac = d.h[i0:i0 + 30].max(), d.l[i0:i0 + 30].min(), d.c[i0 + 29]
        if op > prev['hi'] and Ac > op and (Ac - Al) > 0.6 * (Ah - Al):
            sd, sl = 1, Al - TICK
        elif op < prev['lo'] and Ac < op and (Ah - Ac) > 0.6 * (Ah - Al):
            sd, sl = -1, Ah + TICK
        else:
            continue
        ie = i0 + 30
        risk = abs(d.o[ie] - sl)
        tp = d.o[ie] + sd * (tp_R * risk if tp_R else 1e6)
        t = simulate(d, 'buy' if sd == 1 else 'sell', None, sl, tp, ie, ie + 1, limit=False, cost=cost,
                     exit_min=(cur['i1'] - d.sess_start[s]) if kind == 'rth' else 1375)
        if t:
            t.update(setup='F-drive'); trades.append(t)
    return trades
