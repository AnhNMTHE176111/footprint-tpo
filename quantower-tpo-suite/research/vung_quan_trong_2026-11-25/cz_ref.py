#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cz_ref.py — MÔ HÌNH THAM CHIẾU của lớp "Vùng cụm vol" trong SessionZones (đúng thuật toán C# ClusterZones), Opus 2026-11-25.

Đầu vào giống hệt indicator: nến M15 (t, h, l, c) + profile khối lượng theo giá của từng phiên ngày (từ nến M30), GIÁ THẬT.
  1. Phiên M15 = tách khi 2 nến M15 liền nhau cách > 60 phút (giờ nghỉ CME 60 phút). U15 phiên k = TB (H − L) nến M15 của 5 phiên trước (cần ≥ 2 phiên).
  2. Nguồn: 3 phiên ngày ĐÃ ĐÓNG gần nhất (≥ 20 nến M30). Mỗi phiên: 1 cụm nặng nhất (làm mượt ± 0,1 U15, đỉnh ≥ 1,5 × TB hàng,
     dải = các hàng liên tục còn ≥ 70 % đỉnh đã mượt). Dải chồng / sát nhau (≤ 0,1 U15) ⇒ gộp.
  3. Bộ máy trạng thái trên nến M15 từ đầu phiên nguồn: giá trong dải ⇒ đặt lại. Ra khỏi dải: imp8 = đi xa nhất trong 8 nến M15
     sau nến cuối còn chạm dải; lần tới gần = vào trong 0,6 U15 ngoài mép gần sau khi đã cách ≥ 1,25 U15 (lần sau ≥ 1 U15).
  4. HIỆN khi imp8 ≥ 3 U15 và mới tới gần ≤ 1 lần (lần sắp tới là lần 1 hoặc 2); hoặc đang trong một lần chạm hợp lệ
     (kết thúc khi giá cách dải ≥ 1 U15). Rời lên = hỗ trợ, rời xuống = kháng cự.
  5. Thuận xu hướng: hỗ trợ khi giá đóng > TB giá đóng 92 nến M15 gần nhất (≈ 1 ngày), kháng cự khi <.
Kèm: measure() kiểm lại lợi thế bằng đúng thuật toán này (mốc ngẫu nhiên, chấm trên M1); fixture() xuất ca cho test C#.
"""
import os, sys, json, zlib
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd

CP = dict(SM=0.10, RATIO=1.5, SEP=1.0, FRAC=0.70, NDAYS=3, MINBARS=20, GAPM=0.10, GAP_MIN=60, UDAYS=5,
          IMP=3.0, KBARS=8, TRIG=0.6, AWAY=1.25, REARM=1.0, MAXTOUCH=2, TRENDBARS=92)


def sessions(t, gap_min):
    """t: giây (int). Trả mảng chỉ số phiên cho từng nến."""
    t = np.asarray(t, np.int64)
    s = np.zeros(len(t), np.int64)
    if len(t) > 1: s[1:] = np.cumsum(np.diff(t) > gap_min * 60)
    return s


def u15_of(h, l, sess, k, nd):
    lo = max(0, k - nd)
    if k - lo < 2: return np.nan
    m = (sess >= lo) & (sess < k)
    return float((np.asarray(h)[m] - np.asarray(l)[m]).mean()) if m.any() else np.nan


def cluster(prices, vols, u, row, p=CP):
    """1 cụm nặng nhất. prices: giá hàng (bội số row), vols. Trả (lo, hi, peak, ratio) hoặc None."""
    if len(prices) < 5 or not np.isfinite(u) or u <= 0: return None
    idx = np.round(np.asarray(prices) / row).astype(np.int64)
    base = idx.min()
    W = np.zeros(idx.max() - base + 1)
    np.add.at(W, idx - base, np.asarray(vols, float))
    n = len(W)
    kk = max(1, int(np.floor(p['SM'] * u / row + 0.5)))
    cs = np.r_[0, np.cumsum(W)]
    ii = np.arange(n); a = np.maximum(0, ii - kk); z = np.minimum(n - 1, ii + kk)
    sm = (cs[z + 1] - cs[a]) / (z - a + 1)
    nz = W[W > 0]
    if len(nz) == 0: return None
    avg = nz.mean()
    best = -1
    for i in range(1, n - 1):
        if sm[i] >= sm[i - 1] and sm[i] >= sm[i + 1] and sm[i] >= p['RATIO'] * avg:
            if best < 0 or sm[i] > sm[best]: best = i
    if best < 0: return None
    thr = p['FRAC'] * sm[best]; l2 = h2 = best
    while l2 > 0 and sm[l2 - 1] >= thr: l2 -= 1
    while h2 < n - 1 and sm[h2 + 1] >= thr: h2 += 1
    ipk = l2 + int(np.argmax(W[l2:h2 + 1]))
    return ((base + l2) * row, (base + h2) * row, (base + ipk) * row, float(sm[best] / avg))


def run_state(h, l, lo, hi, s0, e, u, p=CP):
    """Chạy nến M15 [s0..e]. Trả dict trạng thái cuối."""
    last_in, side, imp, nt, aw, ready, ep, ep_nt, ep_i = -1, 0, 0.0, 0, 0.0, False, 0, 0, -1
    touches = []
    for i in range(s0, e + 1):
        if l[i] <= hi and h[i] >= lo:
            last_in, side, imp, nt, aw, ready = i, 0, 0.0, 0, 0.0, False
            continue
        cs = 1 if l[i] > hi else -1
        if side != cs:
            if side != 0: last_in = i
            side, imp, nt, aw, ready = cs, 0.0, 0, 0.0, False
        near = (l[i] - hi) if cs > 0 else (lo - h[i])
        far = (h[i] - hi) if cs > 0 else (lo - l[i])
        if ep != 0 and far >= p['REARM'] * u: ep = 0
        if near <= p['TRIG'] * u:
            if ready:
                if last_in >= 0 and imp >= p['IMP'] * u and nt < p['MAXTOUCH']:
                    ep, ep_nt, ep_i = cs, nt + 1, i
                    touches.append(i)
                nt += 1
            ready, aw = False, 0.0
            continue
        aw = max(aw, far)
        if last_in >= 0 and i - last_in <= p['KBARS']: imp = max(imp, far)
        if not ready and aw >= (p['AWAY'] if nt == 0 else p['REARM']) * u: ready = True
    armed = last_in >= 0 and side != 0 and imp >= p['IMP'] * u and nt < p['MAXTOUCH']
    return dict(side=side, imp=imp / u, nt=nt, armed=armed, ep=ep, ep_nt=ep_nt, ep_i=ep_i if ep != 0 else -1, last_in=last_in)


def compute(bars, days, row, p=CP, shift=None):
    """bars: dict t,h,l,c (M15, giá thật, t giây); days: list dict(t0 = giây nến M30 đầu, n30, prices, vols) theo thời gian.
    Trả list vùng hiện tại nến cuối. shift: hàm (zone_idx) → độ dời (đối chứng)."""
    t, h, l, c = bars['t'], bars['h'], bars['l'], bars['c']
    e = len(t) - 1
    if e < 1: return [], np.nan
    sess = sessions(t, p['GAP_MIN'])
    k = int(sess[e])
    u = u15_of(h, l, sess, k, p['UDAYS'])
    if not np.isfinite(u): return [], u
    cur_t0 = t[np.argmax(sess == k)]
    src = []; got = 0
    for d in reversed(days):
        if d['t0'] >= cur_t0 or d['n30'] < p['MINBARS']: continue
        got += 1
        cl = cluster(d['prices'], d['vols'], u, row, p)
        s0 = int(np.searchsorted(t, d['t0']))
        if cl and s0 <= e: src.append(dict(lo=cl[0], hi=cl[1], peak=cl[2], ratio=cl[3], s0=s0, days=[d['t0']]))
        if got >= p['NDAYS']: break
    src.sort(key=lambda z: (z['lo'], z['hi']))
    mg = []
    for z in src:
        if mg and z['lo'] <= mg[-1]['hi'] + p['GAPM'] * u:
            m = mg[-1]; m['hi'] = max(m['hi'], z['hi']); m['s0'] = min(m['s0'], z['s0']); m['days'] += z['days']
            m['ratio'] = max(m['ratio'], z['ratio']); m['nm'] += 1
        else: mg.append(dict(z, nm=1, days=list(z['days'])))
    j0 = max(0, e - p['TRENDBARS'] + 1)
    mean_c = float(np.mean(c[j0:e + 1]))
    out = []
    for zi, z in enumerate(mg):
        dl = shift(zi, u) if shift else 0.0
        lo, hi = z['lo'] + dl, z['hi'] + dl
        st = run_state(h, l, lo, hi, z['s0'], e, u, p)
        if st['ep'] != 0: side, touch, live = st['ep'], st['ep_nt'], True
        elif st['armed']: side, touch, live = st['side'], st['nt'] + 1, False
        else: continue
        thuan = (c[e] > mean_c) if side > 0 else (c[e] < mean_c)
        out.append(dict(lo=lo, hi=hi, side=side, touch=touch, live=live, thuan=bool(thuan), nm=z['nm'],
                        imp=st['imp'], days=sorted(z['days']), ep_t=int(t[st['ep_i']]) if live else None))
    return out, u


# ------------------------------------------------------------------ dữ liệu từ bộ đệm nghiên cứu
class RefData:
    def __init__(self, sym):
        import vs
        S = vs.Sym(sym)
        self.S, self.sym = S, sym
        k = 2.5 if sym.startswith('nq') else 1.0
        self.k = k; self.row = 0.2 * k; self.tick = 0.25 if k != 1 else 0.1
        D = S.D
        H = np.asarray(S.H); L = np.asarray(S.L); C = np.asarray(S.C)
        self.q_t = (S.t[S.q_s] // 900) * 900
        self.q_h = S.q_h * k; self.q_l = S.q_l * k
        self.q_c = C[S.q_e - 1] * k
        self.m1_h, self.m1_l, self.m1_c = H * k, L * k, C * k
        self.q_s, self.q_e = S.q_s, S.q_e
        t30 = D.m30['t'].astype('datetime64[s]').astype(np.int64)
        self.days = []
        for a, b in D.days:
            pr, w = D.rows_over(a, b)
            pr = np.round(pr * k / self.row) * self.row
            self.days.append(dict(t0=int(t30[a]), n30=b - a + 1, prices=pr, vols=w))

    def at(self, qi, shift=None):
        bars = dict(t=self.q_t[:qi + 1], h=self.q_h[:qi + 1], l=self.q_l[:qi + 1], c=self.q_c[:qi + 1])
        t_end = self.q_t[qi]
        days = [d for d in self.days if d['t0'] <= t_end]
        return compute(bars, days, self.row, shift=shift)


def first_touch(R, i_from, i_end, lo, hi, side, u, B=1.0, TOL=0.10, TRIG=0.6):
    """Lần tới gần đầu tiên trên M1 sau i_from (trong [i_from, i_end)); chấm đảo/sớm/xuyên như vs.py."""
    H, L, C = R.m1_h, R.m1_l, R.m1_c
    for i in range(i_from, i_end):
        near = (L[i] - hi) if side > 0 else (lo - H[i])
        if near <= TRIG * u:
            ext = L[i] if side > 0 else H[i]; iE = i; done = False
            for k in range(i, min(len(H), i + 1380)):
                if side > 0:
                    if L[k] < ext: ext, iE = L[k], k
                    if (H[k] - ext >= B * u and k > iE) or (k == iE and C[k] - ext >= B * u): done = True; break
                else:
                    if H[k] > ext: ext, iE = H[k], k
                    if (ext - L[k] >= B * u and k > iE) or (k == iE and ext - C[k] >= B * u): done = True; break
            ref = hi if side > 0 else lo
            depth = ((ref - ext) if side > 0 else (ext - ref)) / u
            w = (hi - lo) / u
            return 'pha' if not done else ('som' if depth < -TOL else ('tai' if depth <= w + TOL else 'pha'))
    return None


def measure(sym, n_moc=1500, seed=5, B=1.0):
    R = RefData(sym); rs = np.random.RandomState(seed)
    nq = len(R.q_t); rows = []
    sess = sessions(R.q_t, CP['GAP_MIN'])
    nd = len(R.days)
    for _ in range(n_moc):
        qi = rs.randint(400, nq - 2)
        sh = {}
        def shift(zi, u, rep=None):
            return sh[zi]
        k = int(sess[qi]); i_end = int(R.q_e[np.where(sess == k)[0][-1]])
        i_from = int(R.q_e[qi])
        real, u = R.at(qi)
        for z in real:
            if z['live']: continue
            near_now = (R.q_c[qi] - z['hi']) if z['side'] > 0 else (z['lo'] - R.q_c[qi])
            if near_now <= 0.6 * u: continue
            cls = first_touch(R, i_from, i_end, z['lo'], z['hi'], z['side'], u, B)
            if cls: rows.append(dict(typ='that', cls=cls, w=(z['hi']-z['lo'])/u, thuan=z['thuan'], touch=z['touch'], qi=qi, day=k, sym=sym))
        for rep in range(3):
            r2 = np.random.RandomState(zlib.crc32(repr((sym, qi, rep)).encode()) & 0x7fffffff)
            dls = {zi: float(r2.choice([-1, 1]) * r2.uniform(1.5, 4.0)) for zi in range(10)}
            ctrl, _ = R.at(qi, shift=lambda zi, u: dls[zi] * u)
            for z in ctrl:
                if z['live']: continue
                near_now = (R.q_c[qi] - z['hi']) if z['side'] > 0 else (z['lo'] - R.q_c[qi])
                if near_now <= 0.6 * u: continue
                cls = first_touch(R, i_from, i_end, z['lo'], z['hi'], z['side'], u, B)
                if cls: rows.append(dict(typ='doi', cls=cls, w=(z['hi']-z['lo'])/u, thuan=z['thuan'], touch=z['touch'], qi=qi, day=k, sym=sym))
    df = pd.DataFrame(rows)
    df['tap'] = np.where(df['day'] < int(sess.max() * 0.6), 'TRAIN', 'TEST')
    return df


def fixture(sym, cases, path):
    """Xuất ca cho test C#: nến M15 từ phiên nguồn sớm nhất của ca đầu tới ca cuối + profile các ngày + kết quả Python."""
    R = RefData(sym)
    qmax = max(cases)
    t_lo = R.q_t[min(cases)] - 12 * 86400
    i0 = int(np.searchsorted(R.q_t, t_lo))
    days = [d for d in R.days if t_lo - 86400 <= d['t0'] <= R.q_t[qmax]]
    out = dict(sym=sym, tick=R.tick, row=R.row,
               bars=dict(t=R.q_t[i0:qmax + 1].tolist(), h=R.q_h[i0:qmax + 1].tolist(), l=R.q_l[i0:qmax + 1].tolist(), c=R.q_c[i0:qmax + 1].tolist()),
               days=[dict(t0=d['t0'], n30=int(d['n30']), prices=d['prices'].tolist(), vols=np.asarray(d['vols'], float).tolist()) for d in days],
               cases=[])
    for qi in cases:
        bars = dict(t=R.q_t[i0:qi + 1], h=R.q_h[i0:qi + 1], l=R.q_l[i0:qi + 1], c=R.q_c[i0:qi + 1])
        zs, u = compute(bars, [d for d in days if d['t0'] <= R.q_t[qi]], R.row)
        out['cases'].append(dict(last=int(qi - i0), u=u, zones=zs))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f)
    return out


if __name__ == '__main__':
    import vs
    if sys.argv[1] == 'do':
        dfs = {s: measure(s) for s in ('nqy', 'gc')}
        print(vs.HDR)
        vs.line('A', 'THUẬT TOÁN INDICATOR (M15), mốc ngẫu nhiên · mọi vùng hiện', dfs)
        vs.line('B', '  · chạm thuận xu hướng', dfs, 'thuan')
        vs.line('C', '  · chạm ngược xu hướng', dfs, 'not thuan')
        vs.line('D', '  · lần 1', dfs, 'touch==1')
        vs.line('E', '  · lần 2', dfs, 'touch==2')
