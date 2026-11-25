#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vs.py — CHỌN MỐC BẤT KỲ → VẼ SẴN MỌI VÙNG CỤM KHỐI LƯỢNG → GIÁ CHẠM VÙNG THÌ ĐẢO HAY XUYÊN?  (M15, chỉ phản ứng giá)
Opus, 2026-11-25.

Vùng được XÁC ĐỊNH TRƯỚC, chỉ từ dữ liệu trước mốc:
  · 'ngay' : cụm khối lượng của profile cố định từng phiên ngày đã đóng (LBD phiên gần nhất)
  · 'tuan' : cụm của profile tuần trước
  · 'rot'  : vùng đi ngang (rotation) rồi bứt mạnh — kiểu Trader Dale, tự dò trên M15; cụm = đỉnh khối lượng của đoạn đi ngang
Mỗi vùng được chạy bộ máy trạng thái trên M1 từ lúc hình thành; MỖI LẦN GIÁ TỚI GẦN (vào dải TRIG × U15 ngoài mép gần,
sau khi đã cách ≥ AWAY / lần sau ≥ REARM) là một "lần chạm" mang theo trạng thái của vùng NGAY TRƯỚC lúc chạm:
cú rời đi mạnh cỡ nào (imp2/imp4/imp8 = đi xa nhất trong 2/4/8 nến M15 sau khi rời dải), là lần tới gần thứ mấy (nt),
vùng bao nhiêu tuổi, giá lao tới nhanh hay chậm, cùng hay ngược xu hướng…
⇒ "Chọn mốc T bất kỳ, vẽ hết vùng, xem lần chạm đầu tiên sau T" = đúng tập các lần chạm này (vùng không đổi trạng thái
giữa T và lần chạm). Các vòng cải thiện = lọc bảng lần chạm theo luật xác định trước, so với ĐỐI CHỨNG (cùng vùng dời
± 1,5–4 U15, chạy y hệt bộ máy, lọc y hệt luật). Hàm snapshot() làm đúng nghĩa đen để kiểm tra.
Kết cục (điểm đảo = cực trị khi giá bật ngược ≥ B × U15, dung sai TOL × U15):
  ĐẢO TẠI VÙNG · QUAY ĐẦU SỚM (trước mép gần) · XUYÊN QUA (quá mép xa, hoặc không bật nổi).
"""
import os, sys, zlib, pickle
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
import vz, vc

TRIG, AWAY, REARM, TOL, HOR, NSH = 0.6, 1.25, 1.0, 0.10, 1380, 3
G0 = dict(SM=0.10, RATIO=1.5, SEP=1.0, TOP=2, FRAC=0.70, B=1.0, LBD=3, WEEK=False, ROT=False, NGAY=True,
          MERGE=True, GAPM=0.10, PAD=0.0,
          RN=6, RR=2.5, RX=3.0, RK=4, RLB=3)          # rotation: ≥ RN nến M15, biên độ ≤ RR U15, bứt ≥ RX U15 trong ≤ RK nến


class Sym(vc.Sym):
    def __init__(self, sym):
        super().__init__(sym)
        m = self.D.m1
        t = self.t
        key = t // 900
        brk = np.r_[0, np.where(np.diff(key) != 0)[0] + 1]
        self.q_s = brk                                              # nến M1 đầu của mỗi nến M15
        self.q_e = np.r_[brk[1:], len(t)]
        self.q_h = np.maximum.reduceat(np.asarray(m['h']), brk)
        self.q_l = np.minimum.reduceat(np.asarray(m['l']), brk)
        self.q_d = self.dayi[brk]
        self.i30 = np.asarray(m['i30'])
        # cao / thấp phiên trước (để gắn cờ 'đỉnh/đáy cũ đã bị phá')
        D = self.D
        self.pdh = np.full(len(D.days), np.nan); self.pdl = np.full(len(D.days), np.nan)
        for d in range(1, len(D.days)):
            a, b = D.days[d - 1]
            self.pdh[d] = D.m30['h'][a:b + 1].max(); self.pdl[d] = D.m30['l'][a:b + 1].min()
        self.Cn = np.asarray(self.C)
        self.cC = np.r_[0, np.cumsum(self.Cn)]
        self._rot = {}

    # ------------------------------------------------ vùng đi ngang rồi bứt (Trader Dale, tự dò)
    def rotations(self, p):
        k = (p['RN'], p['RR'], p['RX'], p['RK'], p['SM'], p['FRAC'])
        if k in self._rot: return self._rot[k]
        qh, ql, qd = self.q_h, self.q_l, self.q_d
        n = len(qh); out = []; e = p['RN'] - 1; last_end = -1
        while e < n - 1:
            u = self.u15[qd[e]]
            if not np.isfinite(u): e += 1; continue
            s = e; hi, lo = qh[e], ql[e]
            while s - 1 > last_end and max(hi, qh[s - 1]) - min(lo, ql[s - 1]) <= p['RR'] * u and qd[s - 1] == qd[e]:
                s -= 1; hi = max(hi, qh[s]); lo = min(lo, ql[s])
            if e - s + 1 >= p['RN']:
                # bứt: nến kế tiếp ra khỏi hộp, và trong RK nến đi xa ≥ RX × U15
                f = min(n, e + 1 + p['RK'])
                up = qh[e + 1:f].max() - hi; dn = lo - ql[e + 1:f].min()
                if max(up, dn) >= p['RX'] * u and (qh[e + 1] > hi or ql[e + 1] < lo):
                    a30, b30 = int(self.i30[self.q_s[s]]), int(self.i30[self.q_e[e] - 1])
                    cl = self.clusters(a30, b30, u, dict(p, TOP=1, RATIO=1.0))
                    if cl:
                        c = cl[0]
                        out.append(dict(lo=c['lo'], hi=c['hi'], peak=c['peak'], ratio=c['ratio'], s=int(self.q_s[s]),
                                        ready=int(self.q_e[min(n - 1, e + p['RK'])]), day=int(qd[e]), dirn=1 if up >= dn else -1))
                    last_end = e; e += p['RK']; continue
            e += 1
        self._rot[k] = out
        return out

    # ------------------------------------------------ danh sách vùng hiện trong phiên d
    def zones(self, d, p):
        D = self.D; u = self.u15[d]
        if not np.isfinite(u): return []
        src = []
        if p['NGAY']:
            y, got = d - 1, 0
            while y >= 0 and got < p['LBD']:
                a, b = D.days[y]
                if b - a + 1 >= 20:
                    for r, c in enumerate(self.clusters(a, b, u, p)):
                        src.append(dict(c, src='ngay', lag=got + 1, rank=r + 1, s=self.dstart[y]))
                    got += 1
                y -= 1
        if p['WEEK']:
            w = D.week_of[D.days[d][0]]
            if w >= 1:
                a, b = D.weeks[w - 1]
                if b - a + 1 >= 60:
                    for r, c in enumerate(self.clusters(a, b, u, p)):
                        src.append(dict(c, src='tuan', lag=9, rank=r + 1, s=self.wstart[w - 1]))
        if p['ROT']:
            for z in self.rotations(p):
                if z['ready'] < self.dend[d] and d - p['RLB'] < z['day'] <= d:
                    src.append(dict(z, src='rot', lag=d - z['day'], rank=1))
        for z in src:
            z['lo'] -= p['PAD'] * u; z['hi'] += p['PAD'] * u; z['srcs'] = {z['src']}; z['nm'] = 1
        if p['MERGE']:
            src.sort(key=lambda z: z['lo']); mg = []
            for z in src:
                if mg and z['lo'] <= mg[-1]['hi'] + p['GAPM'] * u:
                    m = mg[-1]
                    m['hi'] = max(m['hi'], z['hi']); m['s'] = min(m['s'], z['s']); m['srcs'] |= z['srcs']
                    m['nm'] += 1; m['lag'] = min(m['lag'], z['lag']); m['rank'] = min(m['rank'], z['rank'])
                    m['ratio'] = max(m['ratio'], z['ratio'])
                else: mg.append(dict(z, srcs=set(z['srcs'])))
            src = mg
        return src

    # ------------------------------------------------ bộ máy trạng thái: mọi lần chạm + trạng thái vùng trước lúc chạm
    def sim(self, lo, hi, s0, e0, e1, p):
        H, L, C, U = self.H, self.L, self.C, self.U
        ev = []
        last_in, side, imp2, imp4, imp8, dmax, nt, aw, ready = -1, 0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, False
        for i in range(s0, e1):
            u = U[i]
            if u != u: continue
            if L[i] <= hi and H[i] >= lo:
                last_in, side, imp2, imp4, imp8, dmax, nt, aw, ready = i, 0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, False
                continue
            cs = 1 if L[i] > hi else -1
            if side != cs:
                if side != 0: last_in = i
                side, imp2, imp4, imp8, dmax, nt, aw, ready = cs, 0.0, 0.0, 0.0, 0.0, 0, 0.0, False
            near = (L[i] - hi) if cs > 0 else (lo - H[i])
            far = (H[i] - hi) if cs > 0 else (lo - L[i])
            if near <= TRIG * u:
                if ready and i >= e0 and last_in >= 0:
                    e = self.score(i, cs, lo, hi, u, p)
                    j0 = max(0, i - 60)
                    spd = ((C[j0] - hi) if cs > 0 else (lo - C[j0])) / u        # cách mép bao xa 60 phút trước
                    j1 = max(0, i - 1380)
                    mean_c = (self.cC[i] - self.cC[j1]) / max(1, i - j1)
                    tr = ((C[i] - mean_c) if cs > 0 else (mean_c - C[i])) / u   # + = giá vẫn ở phía xu hướng của vùng
                    e.update(imp2=imp2 / u, imp4=imp4 / u, imp8=imp8 / u, dmax=dmax / u, nt=nt + 1,
                             since=(i - last_in) / 60.0, spd=spd, tr=tr, hour=int((self.t[i] // 3600) % 24))
                    ev.append(e)
                if ready: nt += 1
                ready, aw = False, 0.0
                continue
            dmax = max(dmax, far); aw = max(aw, far)
            k = i - last_in
            if last_in >= 0:
                if k <= 30: imp2 = max(imp2, far)
                if k <= 60: imp4 = max(imp4, far)
                if k <= 120: imp8 = max(imp8, far)
            if not ready and aw >= (AWAY if nt == 0 else REARM) * u: ready = True
        return ev

    def score(self, i0, side, lo, hi, u, p):
        return vc.Sym.score(self, i0, side, lo, hi, u, p)


SYMS = {}
_CACHE = {}


def gen(sym, **kw):
    """Bảng mọi lần chạm (thật + 3 đối chứng) cho một cấu hình vẽ vùng."""
    p = dict(G0, **kw)
    key = (sym, tuple(sorted(p.items())))
    if key in _CACHE: return _CACHE[key]
    S = SYMS.get(sym) or SYMS.setdefault(sym, Sym(sym))
    D = S.D; rows = []; nd = len(D.days)
    for d in range(6, nd):
        e0, e1 = S.dstart[d], S.dend[d]
        for z in S.zones(d, p):
            u0 = S.u15[d]
            var = [('that', 0.0, -1)]
            for rep in range(NSH):
                rs = np.random.RandomState(zlib.crc32(repr((sym, d, round(z['lo'], 2), rep)).encode()) & 0x7fffffff)
                var.append(('doi', float(rs.choice([-1, 1]) * rs.uniform(1.5, 4.0) * u0), rep))
            lv_h, lv_l = S.pdh[d], S.pdl[d]
            for typ, dl, rep in var:
                lo, hi = z['lo'] + dl, z['hi'] + dl
                # cờ 'đỉnh/đáy phiên trước đã bị phá' nằm trong vùng (± 0,3 U15)
                brk = int((lo - 0.3 * u0 <= lv_h <= hi + 0.3 * u0) or (lo - 0.3 * u0 <= lv_l <= hi + 0.3 * u0))
                for e in S.sim(lo, hi, z['s'], e0, e1, p):
                    e.update(typ=typ, rep=rep, day=d, lo=lo, hi=hi, src='+'.join(sorted(z['srcs'])), nm=z['nm'],
                             lag=z['lag'], rank=z['rank'], ratio=z['ratio'], brk=brk)
                    rows.append(e)
    df = pd.DataFrame(rows)
    if len(df):
        df = df.sort_values(['i0']).drop_duplicates(['typ', 'rep', 'side', 'iE'])
        df['tap'] = np.where(df['day'] < int(nd * 0.6), 'TRAIN', 'TEST')
        df['sym'] = sym
    _CACHE[key] = df
    return df


def snapshot(sym, n_moc=400, seed=11, **kw):
    """Đúng nghĩa đen: chọn n_moc mốc ngẫu nhiên; tại mỗi mốc lấy MỌI vùng đang vẽ, xem LẦN CHẠM ĐẦU TIÊN sau mốc (trong phiên)."""
    df = gen(sym, **kw)
    S = SYMS[sym]; rs = np.random.RandomState(seed); out = []
    nd = len(S.D.days)
    for _ in range(n_moc):
        d = rs.randint(6, nd); T = rs.randint(S.dstart[d], S.dend[d])
        x = df[(df.day == d) & (df.i0 >= T)]
        if len(x): out.append(x.sort_values('i0').groupby(['typ', 'rep', 'lo', 'hi'], as_index=False).first())
    return pd.concat(out, ignore_index=True) if out else df.iloc[:0]


# ------------------------------------------------ thống kê
def stat(df, B_=400, seed=3):
    if df is None or not len(df): return None
    r = df[df.typ == 'that']; c = df[df.typ == 'doi']
    if len(r) < 8 or len(c) < 8: return None
    by = {k: (x[x.typ == 'that'].cls.eq('tai').values, x[x.typ == 'doi'].cls.eq('tai').values) for k, x in df.groupby(['sym', 'day'])}
    ks = list(by); rs = np.random.RandomState(seed); bs = []
    for _ in range(B_):
        s = [ks[i] for i in rs.randint(0, len(ks), len(ks))]
        a = np.concatenate([by[k][0] for k in s]); b = np.concatenate([by[k][1] for k in s])
        if len(a) and len(b): bs.append(a.mean() * 100 - b.mean() * 100)
    f = lambda x, c: x.cls.eq(c).mean() * 100
    reach = r[r.cls != 'som']; reach_c = c[c.cls != 'som']
    return dict(n=len(r), tai=f(r, 'tai'), tai_c=f(c, 'tai'), d=f(r, 'tai') - f(c, 'tai'),
                lo=np.percentile(bs, 5), hi=np.percentile(bs, 95), som=f(r, 'som'), pha=f(r, 'pha'),
                som_c=f(c, 'som'), pha_c=f(c, 'pha'),
                giu=reach.cls.eq('tai').mean() * 100 if len(reach) else np.nan,
                giu_c=reach_c.cls.eq('tai').mean() * 100 if len(reach_c) else np.nan, w=r.w.mean())


HDR = ('| # | luật vẽ / lọc | rộng U15 | NQ TRAIN Δ | NQ TEST Δ | GC Δ | đảo tại vùng: thật / đ.c / **Δ** [5–95 %] | '
       'sớm | xuyên | giữ khi đã chạm: thật / đ.c | n |\n|---|---|---|---|---|---|---|---|---|---|---|')


def fmt(s):
    return '—' if s is None else '%+.1f (%d)' % (s['d'], s['n'])


def line(no, label, dfs, q=None):
    xs = []
    for s, x in dfs.items():
        if x is None or not len(x): continue
        xs.append(x.query(q) if q else x)
    al = pd.concat(xs, ignore_index=True) if xs else None
    sub = lambda sym, tap=None: None if al is None else al[(al.sym == sym) & ((al.tap == tap) if tap else True)]
    t = stat(al)
    if t is None:
        print('| %s | %s | — |' % (no, label)); return None
    print('| %s | %s | %.2f | %s | %s | %s | %.1f / %.1f / **%+.1f** [%+.1f, %+.1f] | %.0f | %.0f | %.0f / %.0f | %d |' % (
        no, label, t['w'], fmt(stat(sub('nqy', 'TRAIN'))), fmt(stat(sub('nqy', 'TEST'))), fmt(stat(sub('gc'))),
        t['tai'], t['tai_c'], t['d'], t['lo'], t['hi'], t['som'], t['pha'], t['giu'], t['giu_c'], t['n']))
    return t


def both(**kw):
    return {s: gen(s, **kw) for s in ('nqy', 'gc')}
