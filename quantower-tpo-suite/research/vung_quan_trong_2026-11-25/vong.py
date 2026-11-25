#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vong.py — các vòng đo "vùng quan trọng → nới theo râu / điểm quay đầu" (chỉ đo phản ứng giá, không lệnh).

  python vong.py <vòng> [nqy|gc ...]      chạy rồi in bảng (mặc định cả nqy và gc)
Bộ đệm: vm1_nqy.pkl (prep_nqy.py), vm1_gc.pkl (../vung_manh_2026-11-25/prep1.py gc).
"""
import os, sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import vz

LINE_W = 0.10      # lõi dạng đường (VWAP, VAH…) = giá ± 0,10 U


class Ctx:
    def __init__(self, sym):
        self.D, self.V = vz.load(sym)
        self.p = dict(self.V.P, HVN_MODE='cum2', HVN_HL='giao', D_ONLY=False)
        self.eng = self.V.Engine(self.D, self.p)
        self._lv = {}
        self._extra = {}

    def levels(self, d):
        if d not in self._lv: self._lv[d] = self.V.day_levels(self.D, d, self.p)
        return self._lv[d]

    def extra(self, d):
        """POC hôm qua / tuần trước, cao-thấp hôm qua, cao-thấp tuần trước (bổ sung để so)."""
        if d in self._extra: return self._extra[d]
        D, V = self.D, self.V
        out = []
        a0 = D.days[d][0]
        y = d - 1
        while y >= 0 and (D.days[y][1] - D.days[y][0] + 1) < 20: y -= 1
        if y >= 0:
            a, b = D.days[y]
            st = V.profile_stats(D, a, b)
            if st: out.append(dict(name='poc_d', lo=st['poc'], hi=st['poc']))
            out.append(dict(name='hi_d', lo=float(D.m30['h'][a:b + 1].max()), hi=float(D.m30['h'][a:b + 1].max())))
            out.append(dict(name='lo_d', lo=float(D.m30['l'][a:b + 1].min()), hi=float(D.m30['l'][a:b + 1].min())))
        w = D.week_of[a0]
        if w >= 1:
            a, b = D.weeks[w - 1]
            if b - a + 1 >= 60:
                st = V.profile_stats(D, a, b)
                if st: out.append(dict(name='poc_w', lo=st['poc'], hi=st['poc']))
                out.append(dict(name='hi_w', lo=float(D.m30['h'][a:b + 1].max()), hi=float(D.m30['h'][a:b + 1].max())))
                out.append(dict(name='lo_w', lo=float(D.m30['l'][a:b + 1].min()), hi=float(D.m30['l'][a:b + 1].min())))
        self._extra[d] = out
        return out

    def cores(self, j, names=None, hvn_ok=True):
        """Lõi tại nến j (mức của phiên chứa nến j+1). Mỗi lõi: name, lo, hi (đường: lo = hi)."""
        D = self.D
        d = int(D.day_of[j + 1]); u = D.U[j + 1]
        out = []
        for L in self.levels(d) + self.extra(d):
            if names and L['name'] not in names: continue
            if L['name'].startswith('hvn') and hvn_ok and not self.V.hvn_ok(D, L, j, u, self.p): continue
            out.append(L)
        return out


# ------------------------------------------------------------------ builders
def b_hien_tai(cx):
    """Vòng 1 (gốc): đúng những gì indicator đang vẽ — vùng mạnh (display) + hộp HVN (hvn_boxes)."""
    D, V, eng, p = cx.D, cx.V, cx.eng, cx.p
    def f(j, dl):
        now = float(D.m30['c'][j]); d = int(D.day_of[j + 1])
        out = [dict(tag='manh', lo=z['lo'], hi=z['hi'], a_gold=z['gold'], a_ng=z['ngroup'], a_n=z['n']) for z in V.display(D, eng.zones(j), j, now, p)]
        out += [dict(tag='hop_hvn', lo=b['lo'], hi=b['hi']) for b in V.hvn_boxes(D, eng.levels(d), j, now, p)]
        return out
    return f


def b_loi(cx, names=None):
    """Vòng 2: từng loại lõi riêng lẻ, mỏng (đường ± 0,10 U; hộp HVN giữ nguyên). tag = tên mức."""
    D = cx.D
    def f(j, dl):
        u = D.U[j + 1]; out = []
        for L in cx.cores(j, names):
            lo, hi = (L['lo'], L['hi']) if L['lo'] < L['hi'] else (L['lo'] - LINE_W * u, L['hi'] + LINE_W * u)
            out.append(dict(tag=L['name'], lo=lo + dl, hi=hi + dl, core=(lo + dl, hi + dl)))
        return out
    return f


def b_cum(cx):
    """Vòng 2: cụm va đập (≥ 3 đỉnh/đáy M30 bật ≥ 1 U trong 0,30 U) KHÔNG cần hợp lưu — lõi 'giá đã quay đầu nhiều lần'."""
    D, eng = cx.D, cx.eng
    def f(j, dl):
        return [dict(tag='cum', lo=z['lo'] + dl, hi=z['hi'] + dl) for z in eng.zones(j)]
    return f


ALL = ['vwap_d', 'vwap_d_tren', 'vwap_d_duoi', 'vah_d', 'val_d', 'poc_d', 'hi_d', 'lo_d',
       'vwap_w', 'vwap_w_tren', 'vwap_w_duoi', 'vah_w', 'val_w', 'poc_w', 'hi_w', 'lo_w', 'hvn_d', 'hvn_w']
USER = ['vwap_d', 'vwap_d_tren', 'vwap_d_duoi', 'vah_d', 'val_d', 'vwap_w', 'vwap_w_tren', 'vwap_w_duoi', 'vah_w', 'val_w', 'hvn_d', 'hvn_w']


class Piv:
    """Đỉnh/đáy M30 đã xác nhận (Engine.pv: bật ≥ 1 U trong 6 nến), tra nhanh theo nến j."""
    def __init__(self, cx):
        pv = cx.eng.pv
        self.idx, self.conf, self.price, self.kind = pv['idx'], pv['conf'], pv['price'], pv['kind']
        self.D = cx.D

    def at(self, j, lb):
        d = int(self.D.day_of[j + 1]); a = self.D.days[max(0, d - lb)][0]
        m = (self.conf <= j) & (self.idx >= a)
        return self.price[m], self.kind[m], self.idx[m]


def b_rau(cx, names=ALL, R=0.5, LB=5, mmin=1, pad=0.05, keep_thin=False, tagger=None):
    """Vòng 3: lõi → nới theo các điểm quay đầu M30 (đỉnh/đáy bật ≥ 1 U) trong ± R × U quanh lõi, LB phiên gần nhất.
    vùng = [min(lõi, các điểm) − pad, max(lõi, các điểm) + pad] × U. Cần ≥ mmin điểm; thiếu thì bỏ (keep_thin: giữ lõi mỏng)."""
    D = cx.D; P = Piv(cx)
    def f(j, dl):
        u = D.U[j + 1]; out = []
        pr, kd, ix = P.at(j, LB)
        for L in cx.cores(j, names):
            cl, ch = (L['lo'], L['hi']) if L['lo'] < L['hi'] else (L['lo'] - LINE_W * u, L['hi'] + LINE_W * u)
            cl += dl; ch += dl
            m = (pr >= cl - R * u) & (pr <= ch + R * u)
            n = int(m.sum())
            if n < mmin:
                if not keep_thin: continue
                lo, hi = cl, ch
            else:
                lo = min(cl, pr[m].min()) - pad * u; hi = max(ch, pr[m].max()) + pad * u
            out.append(dict(tag=tagger(L) if tagger else L['name'], lo=lo, hi=hi, core=(cl, ch), a_n=n, a_xn=n >= mmin))
        return out
    return f


ROUNDS = {}


def vong(name):
    def deco(fn): ROUNDS[name] = fn; return fn
    return deco


@vong('1')
def r1(cx):
    return [('hien_tai', b_hien_tai(cx), False)]


@vong('2')
def r2(cx):
    names = ['vwap_d', 'vwap_d_tren', 'vwap_d_duoi', 'vah_d', 'val_d', 'poc_d', 'hi_d', 'lo_d',
             'vwap_w', 'vwap_w_tren', 'vwap_w_duoi', 'vah_w', 'val_w', 'poc_w', 'hi_w', 'lo_w', 'hvn_d', 'hvn_w']
    return [('loi_tat_ca', b_loi(cx, names), False), ('cum', b_cum(cx), False)]


@vong('3')
def r3(cx):
    return [('rau_R05_m1', b_rau(cx, R=0.5, mmin=1), True), ('rau_R05_m2', b_rau(cx, R=0.5, mmin=2), True),
            ('rau_R03_m1', b_rau(cx, R=0.3, mmin=1), True), ('rau_R08_m2', b_rau(cx, R=0.8, mmin=2), True)]


def pivot_table(cx, k=2, m=12):
    """Mọi đỉnh/đáy M30 cục bộ (k nến mỗi bên) + biên độ bật: đáy → max(h) sau đó tới khi có đáy thấp hơn (tối đa m nến), / U.
    Trả mảng: idx, conf (nến xác nhận = khi bật đạt 1 U lần đầu, ≥ i+k), price, kind, bounce (×U, đo tới m nến), body (mép thân phía trong), vol (khối lượng nến / TB phiên trước)."""
    D = cx.D; h, l, o, c, v, U = D.m30['h'], D.m30['l'], D.m30['o'], D.m30['c'], D.m30['v'], D.U
    out = []
    for i in range(k, D.n - k):
        u = U[i]
        if not np.isfinite(u): continue
        for kind in (-1, 1):
            if kind < 0 and not (l[i] < l[i - k:i].min() and l[i] <= l[i + 1:i + k + 1].min()): continue
            if kind > 0 and not (h[i] > h[i - k:i].max() and h[i] >= h[i + 1:i + k + 1].max()): continue
            best, conf = 0.0, None
            for jj in range(i + 1, min(D.n, i + m + 1)):
                if (kind < 0 and l[jj] < l[i]) or (kind > 0 and h[jj] > h[i]): break
                ex = (h[jj] - l[i]) if kind < 0 else (h[i] - l[jj])
                if ex >= u and conf is None: conf = max(i + k, jj)
                best = max(best, ex)
            if conf is None: continue
            d = int(D.day_of[i]); a, b = D.days[max(0, d - 1)]
            vm = v[a:b + 1].mean() if b >= a else np.nan
            out.append((i, conf, l[i] if kind < 0 else h[i], kind, best / u,
                        min(o[i], c[i]) if kind < 0 else max(o[i], c[i]), v[i] / vm if vm > 0 else np.nan))
    return np.array(out, dtype=[('idx', 'i4'), ('conf', 'i4'), ('price', 'f8'), ('kind', 'i1'), ('bounce', 'f8'), ('body', 'f8'), ('vol', 'f8')])


def b_pivot(cx, PT, bmin=1.0, LB=5, mode='rau', minw=0.10, maxw=0.5, tagfn=None):
    """Vòng 4: vùng = một ĐIỂM QUAY ĐẦU M30 (bật ≥ bmin × U). mode 'rau': từ đầu râu tới mép thân (tối thiểu minw, tối đa maxw × U);
    'mong': đầu râu ± 0,10 U. Đáy → vùng hỗ trợ tiềm năng, đỉnh → kháng cự."""
    D = cx.D
    def f(j, dl):
        u = D.U[j + 1]; d = int(D.day_of[j + 1]); a = D.days[max(0, d - LB)][0]
        m = (PT['conf'] <= j) & (PT['idx'] >= a) & (PT['bounce'] >= bmin)
        out = []
        for r in PT[m]:
            p, bd = r['price'], r['body']
            if mode == 'mong': lo, hi = p - 0.1 * u, p + 0.1 * u
            elif r['kind'] < 0: lo, hi = p, min(max(bd, p + minw * u), p + maxw * u)
            else: lo, hi = max(min(bd, p - minw * u), p - maxw * u), p
            out.append(dict(tag=tagfn(r) if tagfn else 'pv', lo=lo + dl, hi=hi + dl, a_b=float(r['bounce']), a_v=float(r['vol']), a_k=int(r['kind'])))
        return out
    return f


def bb(x):
    return 'bật %s' % ('1–1,5U' if x < 1.5 else '1,5–2,5U' if x < 2.5 else '2,5–4U' if x < 4 else '≥4U')


@vong('4')
def r4(cx):
    PT = pivot_table(cx)
    return [('pv_rau', b_pivot(cx, PT, tagfn=lambda r: bb(r['bounce'])), False),
            ('pv_mong', b_pivot(cx, PT, mode='mong', tagfn=lambda r: bb(r['bounce'])), False)]


def b_oracle(cx, PT, H=48):
    """KIỂM DỤNG CỤ (nhìn trước — KHÔNG phải cách vẽ): vùng tại các đỉnh/đáy M30 sẽ xảy ra trong H nến TỚI. Phải ra Δ rất dương."""
    D = cx.D
    def f(j, dl):
        u = D.U[j + 1]
        m = (PT['idx'] > j) & (PT['idx'] <= j + H) & (PT['bounce'] >= 1.5)
        return [dict(tag='oracle', lo=r['price'] - 0.1 * u + dl, hi=r['price'] + 0.1 * u + dl) for r in PT[m]]
    return f


@vong('kiem')
def rk(cx):
    return [('oracle', b_oracle(cx, pivot_table(cx)), False)]


EDGE = ['vah_d', 'val_d', 'vwap_d_tren', 'vwap_d_duoi', 'vah_w', 'val_w', 'vwap_w_tren', 'vwap_w_duoi']


def b_hop_luu(cx, names, gap=0.3, tagby='n'):
    """Vòng 5: gom các lõi (đường ± 0,1 U, hộp HVN nguyên) cách nhau ≤ gap × U thành MỘT vùng (bao trọn các lõi).
    tag = số lõi trong vùng (1, 2, 3+), hoặc 'nhom' = số nhóm độc lập (cạnh trên/dưới ngày, tuần)."""
    D = cx.D
    def f(j, dl):
        u = D.U[j + 1]; iv = []
        for L in cx.cores(j, names):
            lo, hi = (L['lo'], L['hi']) if L['lo'] < L['hi'] else (L['lo'] - LINE_W * u, L['hi'] + LINE_W * u)
            iv.append([lo, hi, {L['name']}])
        iv.sort(key=lambda x: x[0]); out = []
        for x in iv:
            if out and x[0] <= out[-1][1] + gap * u: out[-1][1] = max(out[-1][1], x[1]); out[-1][2] |= x[2]
            else: out.append(list(x))
        res = []
        for lo, hi, nm in out:
            n = len(nm); t = '1 mức' if n == 1 else '2 mức' if n == 2 else '3+ mức'
            res.append(dict(tag=t, lo=lo + dl, hi=hi + dl, a_names='+'.join(sorted(nm))))
        return res
    return f


def b_quet(cx, a=0.3, b=0.8, names=('hi_d', 'lo_d', 'hi_w', 'lo_w')):
    """Vòng 5: vùng QUÉT QUA đỉnh/đáy cũ: đỉnh H → [H + a·U, H + b·U]; đáy L → [L − b·U, L − a·U]."""
    D = cx.D
    def f(j, dl):
        u = D.U[j + 1]; out = []
        for L in cx.cores(j, list(names)):
            x = L['lo']
            lo, hi = (x + a * u, x + b * u) if L['name'].startswith('hi') else (x - b * u, x - a * u)
            out.append(dict(tag=L['name'], lo=lo + dl, hi=hi + dl))
        return out
    return f


@vong('5')
def r5(cx):
    return [('hl_canh', b_hop_luu(cx, EDGE), False), ('hl_user', b_hop_luu(cx, USER), False),
            ('quet_0_03', b_quet(cx, 0.0, 0.3), False), ('quet_03_08', b_quet(cx, 0.3, 0.8), False), ('quet_02_06', b_quet(cx, 0.2, 0.6), False)]


def b_quet_pv(cx, PT, a=0.3, b=0.8, bmin=2.5, LB=5, untested=True):
    """Vòng 6: vùng quét qua ĐỈNH/ĐÁY M30 cũ (bật ≥ bmin U, LB phiên) — đỉnh P → [P + a·U, P + b·U]. untested: chỉ đỉnh/đáy
    chưa bị giá vượt qua từ khi hình thành tới nến j (còn 'nguyên', thanh khoản stop còn nằm đó)."""
    D = cx.D; h, l = D.m30['h'], D.m30['l']
    def f(j, dl):
        u = D.U[j + 1]; d = int(D.day_of[j + 1]); a0 = D.days[max(0, d - LB)][0]
        m = (PT['conf'] <= j) & (PT['idx'] >= a0) & (PT['bounce'] >= bmin)
        out = []
        for r in PT[m]:
            i, p = int(r['idx']), r['price']
            if untested and r['conf'] < j:
                if r['kind'] > 0 and h[i + 1:j + 1].max() > p: continue
                if r['kind'] < 0 and l[i + 1:j + 1].min() < p: continue
            lo, hi = (p + a * u, p + b * u) if r['kind'] > 0 else (p - b * u, p - a * u)
            out.append(dict(tag='dinh' if r['kind'] > 0 else 'day', lo=lo + dl, hi=hi + dl))
        return out
    return f


@vong('6')
def r6(cx):
    PT = pivot_table(cx)
    return [('quet_02_05', b_quet(cx, 0.2, 0.5), False), ('quet_04_10', b_quet(cx, 0.4, 1.0), False), ('quet_05_12', b_quet(cx, 0.5, 1.2), False),
            ('pvq_b25', b_quet_pv(cx, PT, bmin=2.5), False), ('pvq_b15', b_quet_pv(cx, PT, bmin=1.5), False),
            ('pvq_b25_all', b_quet_pv(cx, PT, bmin=2.5, untested=False), False),
            ('canh_rau', b_rau(cx, names=EDGE, R=0.5, mmin=1), True), ('canh_mong', b_loi(cx, EDGE), False)]


@vong('7')
def r7(cx):
    return [('canh_R03_m1', b_rau(cx, names=EDGE, R=0.3, mmin=1), True), ('canh_R05_m2', b_rau(cx, names=EDGE, R=0.5, mmin=2), True),
            ('canh_R05_m1_giu', b_rau(cx, names=EDGE, R=0.5, mmin=1, keep_thin=True), True), ('canh_R08_m1', b_rau(cx, names=EDGE, R=0.8, mmin=1), True),
            ('user_R05_m1', b_rau(cx, names=USER, R=0.5, mmin=1), True)]


def b_ghep(*bs):
    def f(j, dl):
        out = []
        for t, b in bs: out += [dict(z, tag=t + ':' + z['tag']) if False else dict(z, tag=t) for z in b(j, dl)]
        return out
    return f


@vong('8')
def r8(cx):
    xn = lambda L: None
    return [('canh_R03_giu', b_rau(cx, names=EDGE, R=0.3, mmin=1, keep_thin=True), True),
            ('canh_R03_xacnhan', b_rau(cx, names=EDGE, R=0.3, mmin=1, keep_thin=True, tagger=None), True),
            ('ban_do', b_ghep(('canh', b_rau(cx, names=EDGE, R=0.3, mmin=1, keep_thin=True)), ('quet', b_quet(cx, 0.3, 0.8))), True)]


@vong('9')
def r9(cx):
    return [('canh_R03_LB3', b_rau(cx, names=EDGE, R=0.3, mmin=1, LB=3), True), ('canh_R03_LB10', b_rau(cx, names=EDGE, R=0.3, mmin=1, LB=10), True),
            ('canh_R02', b_rau(cx, names=EDGE, R=0.2, mmin=1), True), ('canh_R03_pad0', b_rau(cx, names=EDGE, R=0.3, mmin=1, pad=0.0), True),
            ('canh_R03_pad10', b_rau(cx, names=EDGE, R=0.3, mmin=1, pad=0.10), True)]


def b_final(cx, R=0.3, LB=5, rad=4.0, maxside=3, merge=True):
    """Vòng 10: bản đồ vùng đề xuất như indicator sẽ vẽ — lõi cạnh (VAH/VAL, VWAP ±1σ ngày + tuần) có ≥ 1 điểm quay đầu M30
    trong ± R·U, nới bao các điểm đó (+0,05 U); vùng chồng nhau gộp; chỉ giữ vùng cách giá ≤ rad·U, tối đa maxside mỗi phía."""
    D = cx.D; base = b_rau(cx, names=EDGE, R=R, mmin=1, LB=LB)
    def f(j, dl):
        u = D.U[j + 1]; now = float(D.m30['c'][j])
        zs = sorted(base(j, dl), key=lambda z: z['lo']); m = []
        for z in zs:
            if merge and m and z['lo'] <= m[-1]['hi']: m[-1]['hi'] = max(m[-1]['hi'], z['hi']); m[-1]['k'] += 1
            else: m.append(dict(lo=z['lo'], hi=z['hi'], k=1))
        out = []
        for sd in (1, -1):
            g = [z for z in m if (z['hi'] < now if sd > 0 else z['lo'] > now)]
            g = sorted(g, key=lambda z: abs(now - (z['hi'] if sd > 0 else z['lo'])))
            out += [z for z in g if abs(now - (z['hi'] if sd > 0 else z['lo'])) <= rad * u][:maxside]
        out += [z for z in m if z['lo'] <= now <= z['hi']]
        return [dict(tag='ban_do', lo=z['lo'], hi=z['hi'], a_k=z['k']) for z in out]
    return f


@vong('10')
def r10(cx):
    return [('final', b_final(cx), False), ('hien_tai', b_hien_tai(cx), False)]


@vong('10c')
def r10c(cx):
    return [('gop_khong_loc', b_final(cx, rad=99, maxside=99), False), ('loc_khong_gop', b_final(cx, merge=False), False)]


@vong('10b')
def r10b(cx):
    return [('canh_R03_doinguyen', b_rau(cx, names=EDGE, R=0.3, mmin=1), False), ('final_doilai', b_final(cx), True)]


def main():
    rd = sys.argv[1]
    syms = sys.argv[2:] or ['nqy', 'gc']
    for s in syms:
        cx = Ctx(s)
        for nm, bld, sc in ROUNDS[rd](cx):
            df, rec = vz.run(cx.D, bld, 'v%s_%s' % (rd, nm), shift_core=sc)
            print(s, rd, nm, 'sự kiện', len(df), flush=True)


if __name__ == '__main__':
    main()
