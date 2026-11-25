#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vc.py — ĐO VÙNG CỤM KHỐI LƯỢNG kiểu Trader Dale trên profile CỐ ĐỊNH ngày/tuần, đơn vị nến M15 (scalp).
Chỉ đo PHẢN ỨNG GIÁ TẠI VÙNG, không lệnh. Opus, 2026-11-25.

Đơn vị U15 = TB (High − Low) nến M15 của 5 phiên đã đóng gần nhất.
Cụm khối lượng (cluster) của một profile ngày / tuần đã đóng:
  profile làm mượt ± SM × U15 → đỉnh cục bộ ≥ RATIO × TB hàng → cách nhau ≥ SEP × U15 → giữ TOP cụm nặng nhất
  dải cụm = nới liên tục từ đỉnh tới khi khối lượng (đã mượt) < FRAC × đỉnh.
Luật Trader Dale (chế độ 'dale'):
  giá RỜI dải cụm (nến M1 cuối cùng còn chạm dải) rồi đi xa ≥ X × U15 trong ≤ K nến M15 ⇒ vùng "tươi",
  rời lên = hỗ trợ, rời xuống = kháng cự. Chỉ chấm LẦN QUAY LẠI ĐẦU TIÊN (giá vào trong TRIG × U15 ngoài mép gần);
  sau đó vùng hết tươi cho tới khi giá vào lại dải và lại rời đi mạnh.
Chế độ 'all': mọi lần quay lại (đã cách mép ≥ AWAY, lần sau ≥ REARM) — như cách đo cũ.
Chấm (nến M1): điểm đảo = cực trị khi giá bật ngược ≥ B × U15; TẠI VÙNG (± TOL) / SỚM / PHÁ.
Đối chứng: cùng dải dời ± 1,5–4 U15 (3 bản), chạy ĐÚNG luật như vùng thật (cũng phải có cú rời đi mạnh…).
"""
import os, sys, zlib, pickle
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
import vz

ROW = 0.2
TRIG, AWAY, REARM, TOL, HOR, NSH = 0.6, 1.25, 1.0, 0.10, 1380, 3
P0 = dict(SM=0.10, RATIO=1.5, SEP=1.0, TOP=3, FRAC=0.70, X=3.0, K=4, B=1.0, MODE='dale', LBD=1, WEEK=False,
          MERGE=False, GAPM=0.10, LINE=False, PAD=0.0, NT=1)


class Sym:
    def __init__(self, sym):
        D, V = vz.load(sym)
        self.D, self.sym = D, sym
        m = D.m1
        self.H, self.L, self.C = D._H, D._L, D._C
        t = m['t'].astype('datetime64[s]').astype(np.int64)
        self.t = t
        i30 = np.asarray(m['i30'])
        self.dayi = D.day_of[i30]
        nd = len(D.days)
        # nến M15
        key = t // 900
        brk = np.r_[0, np.where(np.diff(key) != 0)[0] + 1]
        h = np.maximum.reduceat(np.asarray(m['h']), brk); l = np.minimum.reduceat(np.asarray(m['l']), brk)
        dd = self.dayi[brk]
        rng = h - l
        self.u15 = np.full(nd, np.nan)
        for k in range(nd):
            lo = max(0, k - 5)
            if k - lo < 2: continue
            sel = (dd >= lo) & (dd < k)
            self.u15[k] = rng[sel].mean()
        self.U = self.u15[self.dayi].tolist()
        self.dstart = [int(D.m1_ptr[a]) for a, b in D.days]
        self.dend = [int(D.m1_ptr[b + 1]) for a, b in D.days]
        self.wstart = [int(D.m1_ptr[a]) for a, b in D.weeks]
        self.wend = [int(D.m1_ptr[b + 1]) for a, b in D.weeks]
        self._cl = {}

    # ------------------------------------------------ cụm khối lượng của một profile
    def clusters(self, a, b, u, p):
        k = (a, b, round(u, 6), p['SM'], p['RATIO'], p['SEP'], p['TOP'], p['FRAC'])
        if k in self._cl: return self._cl[k]
        pr, w = self.D.rows_over(a, b)
        out = []
        if len(pr) >= 5 and np.isfinite(u):
            i0 = np.round(pr / ROW).astype(np.int64); base = i0.min()
            W = np.zeros(i0.max() - base + 1); W[i0 - base] = w
            P = (np.arange(len(W)) + base) * ROW
            kk = max(1, int(round(p['SM'] * u / ROW)))
            cs = np.r_[0, np.cumsum(W)]; ii = np.arange(len(W))
            lo_ = np.maximum(0, ii - kk); hi_ = np.minimum(len(W) - 1, ii + kk)
            sm = (cs[hi_ + 1] - cs[lo_]) / (hi_ - lo_ + 1)
            avg = W[W > 0].mean()
            pk = [i for i in range(1, len(sm) - 1) if sm[i] >= sm[i - 1] and sm[i] >= sm[i + 1] and sm[i] >= p['RATIO'] * avg]
            pk.sort(key=lambda i: -sm[i])
            sel = []
            for i in pk:
                if all(abs(P[i] - P[j]) >= p['SEP'] * u for j in sel): sel.append(i)
            for i in sel:
                if len(out) >= p['TOP']: break
                thr = p['FRAC'] * sm[i]; l2 = h2 = i
                while l2 > 0 and sm[l2 - 1] >= thr: l2 -= 1
                while h2 < len(sm) - 1 and sm[h2 + 1] >= thr: h2 += 1
                if any(P[l2] <= z['hi'] and P[h2] >= z['lo'] for z in out): continue   # trùng dải cụm nặng hơn ⇒ bỏ
                ipk = l2 + int(np.argmax(W[l2:h2 + 1]))          # hàng nặng nhất thật (chưa mượt) trong dải
                out.append(dict(lo=P[l2], hi=P[h2], peak=P[ipk], ratio=sm[i] / avg))
        self._cl[k] = out
        return out

    # ------------------------------------------------ bộ máy trạng thái trên M1
    def sim(self, lo, hi, s0, e0, e1, p):
        """Chạy từ nến M1 s0 tới e1; trả các lần chấm có i0 trong [e0, e1)."""
        H, L, C, U = self.H, self.L, self.C, self.U
        X, K15, mode = p['X'], p['K'] * 15, p['MODE']
        ev = []
        last_in, side, maxd, armed, used, nt = -1, 0, 0.0, 0, False, 0
        st, away, need = 0, 0.0, AWAY
        i = s0
        while i < e1:
            u = U[i]
            if u != u: i += 1; continue
            if mode == 'all':
                if L[i] > hi + TRIG * u:
                    if st != 1: st, away = 1, 0.0
                    away = max(away, (H[i] - hi) / u)
                elif H[i] < lo - TRIG * u:
                    if st != -1: st, away = -1, 0.0
                    away = max(away, (lo - L[i]) / u)
                else:
                    if st != 0 and away >= need and i >= e0:
                        ev.append(self.score(i, st, lo, hi, u, p))
                    if st != 0: need = REARM
                    st, away = 0, 0.0
                i += 1; continue
            # --- chế độ dale
            if L[i] <= hi and H[i] >= lo:
                last_in, side, maxd, armed, used, nt = i, 0, 0.0, 0, False, 0
                i += 1; continue
            cs = 1 if L[i] > hi else -1
            if side != cs:
                if side != 0: last_in = i          # nhảy qua dải không chạm (khoảng trống) ⇒ coi như vừa ở trong
                side, maxd, armed, used, nt = cs, 0.0, 0, False, 0
            near = (L[i] - hi) if cs > 0 else (lo - H[i])
            if armed == cs and near <= TRIG * u:
                nt += 1
                if i >= e0 and nt <= p['NT']:
                    e = self.score(i, cs, lo, hi, u, p); e['nt'] = nt; ev.append(e)
                armed, used, maxd = 0, True, 0.0
                i += 1; continue
            far = (H[i] - hi) if cs > 0 else (lo - L[i])
            maxd = max(maxd, far)
            if armed == 0 and not used and last_in >= 0 and maxd >= X * u and i - last_in <= K15:
                armed = cs
            elif armed == 0 and used and maxd >= REARM * u:      # lần chạm thứ 2+ (chỉ chấm nếu NT > 1)
                armed = cs
            i += 1
        return ev

    def score(self, i0, side, lo, hi, u, p):
        H, L, C = self.H, self.L, self.C
        B = p['B']; N = len(H); end = min(N, i0 + HOR)
        ext = L[i0] if side > 0 else H[i0]; iE = i0; done = False
        for k in range(i0, end):
            if side > 0:
                if L[k] < ext: ext, iE = L[k], k
                if (H[k] - ext >= B * u and k > iE) or (k == iE and C[k] - ext >= B * u): done = True; break
            else:
                if H[k] > ext: ext, iE = H[k], k
                if (ext - L[k] >= B * u and k > iE) or (k == iE and ext - C[k] >= B * u): done = True; break
        near = hi if side > 0 else lo
        depth = ((near - ext) if side > 0 else (ext - near)) / u
        w = (hi - lo) / u
        c = 'pha' if not done else ('som' if depth < -TOL else ('tai' if depth <= w + TOL else 'pha'))
        return dict(i0=i0, iE=iE, side=side, u=u, depth=depth, w=w, cls=c, done=done)

    # ------------------------------------------------ danh sách vùng theo ngày đánh giá
    def zones_for_day(self, d, p):
        """Các vùng hiện trong phiên d: [(tag, lo, hi, s_start, u0, nsrc)]."""
        D = self.D; u = self.u15[d]
        if not np.isfinite(u): return []
        src = []
        y, got = d - 1, 0
        while y >= 0 and got < p['LBD']:
            a, b = D.days[y]
            if b - a + 1 >= 20:
                for c in self.clusters(a, b, u, p): src.append(('ngay%d' % (got + 1), c, self.dstart[y]))
                got += 1
            y -= 1
        if p['WEEK']:
            w = D.week_of[D.days[d][0]]
            if w >= 1:
                a, b = D.weeks[w - 1]
                if b - a + 1 >= 60:
                    for c in self.clusters(a, b, u, p): src.append(('tuan', c, self.wstart[w - 1]))
        bands = []
        for tag, c, s in src:
            if p['LINE']: lo, hi = c['peak'] - 0.1 * u, c['peak'] + 0.1 * u
            else: lo, hi = c['lo'], c['hi']
            lo -= p['PAD'] * u; hi += p['PAD'] * u
            bands.append([lo, hi, s, {tag}])
        if p['MERGE']:
            bands.sort(key=lambda z: z[0]); mg = []
            for z in bands:
                if mg and z[0] <= mg[-1][1] + p['GAPM'] * u:
                    m = mg[-1]; m[1] = max(m[1], z[1]); m[2] = min(m[2], z[2]); m[3] |= z[3]
                else: mg.append([z[0], z[1], z[2], set(z[3])])
            bands = mg
        out = []
        for lo, hi, s, tags in bands:
            n = len(tags) if p['MERGE'] else 1
            has_w = any(t == 'tuan' for t in tags)
            tag = ('hl%d' % min(n, 3) + ('w' if has_w else '')) if p['MERGE'] else next(iter(tags))
            out.append((tag, lo, hi, s, u, n))
        return out


def run(sym, p, name):
    S = SYMS.get(sym) or SYMS.setdefault(sym, Sym(sym))
    D = S.D; rows = []
    nd = len(D.days)
    for d in range(6, nd):
        e0, e1 = S.dstart[d], S.dend[d]
        for tag, lo, hi, s0, u0, n in S.zones_for_day(d, p):
            var = [('that', 0.0, -1)]
            for rep in range(NSH):
                rs = np.random.RandomState(zlib.crc32(repr((sym, d, round(lo, 2), rep)).encode()) & 0x7fffffff)
                var.append(('doi', float(rs.choice([-1, 1]) * rs.uniform(1.5, 4.0) * u0), rep))
            for typ, dl, rep in var:
                for e in S.sim(lo + dl, hi + dl, s0, e0, e1, p):
                    e.update(typ=typ, rep=rep, tag=tag, n=n, day=d, lo=lo + dl, hi=hi + dl)
                    rows.append(e)
    df = pd.DataFrame(rows)
    if len(df):
        df = df.sort_values(['i0']).drop_duplicates(['typ', 'rep', 'side', 'iE'])
        df['tap'] = np.where(df['day'] < int(nd * 0.6), 'TRAIN', 'TEST')
        df['sym'] = sym
    with open(os.path.join(vz.CDIR, 'vc_%s_%s.pkl' % (sym, name)), 'wb') as f:
        pickle.dump(df, f, protocol=4)
    return df


SYMS = {}


def stat(df, B_=400, seed=3):
    if df is None or not len(df): return None
    r = df[df.typ == 'that']; c = df[df.typ == 'doi']
    if len(r) < 5 or len(c) < 5: return None
    by = {k: (x[x.typ == 'that'].cls.eq('tai').values, x[x.typ == 'doi'].cls.eq('tai').values) for k, x in df.groupby(['sym', 'day'])}
    ks = list(by); rs = np.random.RandomState(seed); bs = []
    for _ in range(B_):
        s = [ks[i] for i in rs.randint(0, len(ks), len(ks))]
        a = np.concatenate([by[k][0] for k in s]); b = np.concatenate([by[k][1] for k in s])
        if len(a) and len(b): bs.append(a.mean() * 100 - b.mean() * 100)
    return dict(n=len(r), tai=r.cls.eq('tai').mean() * 100, tai_c=c.cls.eq('tai').mean() * 100,
                d=r.cls.eq('tai').mean() * 100 - c.cls.eq('tai').mean() * 100,
                lo=np.percentile(bs, 5), hi=np.percentile(bs, 95),
                som=r.cls.eq('som').mean() * 100, som_c=c.cls.eq('som').mean() * 100,
                pha=r.cls.eq('pha').mean() * 100, pha_c=c.cls.eq('pha').mean() * 100, w=r.w.mean())


def fmt(s):
    return '—' if s is None else '%+.1f (n%d)' % (s['d'], s['n'])


def line(label, dfs):
    """dfs: dict sym → df. In: NQ TRAIN, NQ TEST, GC, gộp."""
    xs = [x for x in dfs.values() if x is not None and len(x)]
    al = pd.concat(xs, ignore_index=True) if xs else None
    nq = dfs.get('nqy'); gc = dfs.get('gc')
    a = stat(nq[nq.tap == 'TRAIN']) if nq is not None and len(nq) else None
    b = stat(nq[nq.tap == 'TEST']) if nq is not None and len(nq) else None
    g = stat(gc) if gc is not None and len(gc) else None
    t = stat(al)
    if t is None:
        print('| %s | — |' % label); return t
    print('| %s | %.2f | %s | %s | %s | %.1f / %.1f / **%+.1f** [%+.1f, %+.1f] | %.0f/%.0f | %.0f/%.0f | %d |' % (
        label, t['w'], fmt(a), fmt(b), fmt(g), t['tai'], t['tai_c'], t['d'], t['lo'], t['hi'],
        t['som'], t['som_c'], t['pha'], t['pha_c'], t['n']))
    return t


HDR = ('| cách vẽ | rộng (U15) | NQ TRAIN Δ | NQ TEST Δ | GC Δ | gộp: tại vùng thật / đ.c / Δ [5–95 %] | sớm thật/đ.c | phá thật/đ.c | n |\n'
       '|---|---|---|---|---|---|---|---|---|')


def go(label, syms=('nqy', 'gc'), **kw):
    p = dict(P0, **kw)
    name = label.replace(' ', '_')
    dfs = {s: run(s, p, name) for s in syms}
    return line(label, dfs), dfs
