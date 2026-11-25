#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vung_manh.py — BẢN THAM CHIẾU của thuật toán "vùng kháng cự / hỗ trợ mạnh" (PLAN-VUNG-MANH.md).
Opus port sang C# rồi so từng số với file này (xem parity_cases.py).

Đầu vào: nến M30 ĐÃ ĐÓNG tới chỉ số j + khối lượng từng mức giá của các nến đó. Không dùng gì của khung chart.
Đầu ra : danh sách vùng (lo, hi, số lần va đập, các mức hợp lưu, vàng hay không).
"""
import numpy as np
from vm import *
import hvn_cum as HC

P = dict(
    K=2,              # đỉnh/đáy cục bộ: so với K nến mỗi bên
    M=6,              # cửa sổ "đi tới" và "bật lại" (nến M30)
    R=1.0,            # bật lại tối thiểu (×U)
    LB=5,             # số phiên ĐÃ ĐÓNG nhìn lại (cộng thêm phiên đang chạy)
    WC=0.30,          # bề rộng tối đa của một cụm va đập (×U)
    NMIN=3,           # số lần va đập tối thiểu
    PAD=0.05,         # nới mỗi mép vùng (×U)
    WMIN=0.20,        # bề rộng vùng tối thiểu (×U)
    TOL=0.10,         # dung sai hợp lưu (×U) tính từ mép vùng
    HVN_DAYS=5,       # HVN ngày: lấy từ bao nhiêu phiên đã đóng
    HVN_RATIO=2.5,    # "lớn": đỉnh đã làm mượt >= 2,5 × trung bình hàng
    HVN_TOP=3,
    HVN_AWAY=2.0,     # "đã rời xa": sau khi profile chốt, giá từng cách đỉnh cụm >= 2 U
    D_ONLY=False,     # chỉ nhận HVN của profile hình chữ D (2026-11-25: TẮT — HVN dạng cụm tự mang tiêu chí "lớn và đều")
    HVN_MODE='cum',   # 'cum' = HVN dạng cụm v1 (hvn_cum.py, PLAN mục 10) · 'cum2' = v2 (hvn_cum2.py, PLAN mục 13; thông số ghi đè qua khoá HVN2) · 'dinh' = kiểu cũ (đỉnh nhọn + PeakSharpness 90 %), chỉ để so
    HVN_HL='giao',    # hợp lưu với hộp HVN: 'giao' = vùng va đập giao hộp (± TOL) · 'mep' = chỉ khi chạm MÉP hộp (± TOL)
    HVN_X=HC.HP['X'], HVN_SM=HC.HP['SM'], HVN_PK2=HC.HP['PK2'], HVN_Y=HC.HP['Y'], HVN_Y_W=HC.HP['Y_W'], HVN_WMIN=HC.HP['WMIN'], HVN_MAXC=HC.HP['MAXC'],
    D_POC_LO=0.30, D_POC_HI=0.70, D_VA_MAX=0.60,
    GOLD_MIN=3,       # vàng: >= 3 nhóm mức và có HVN
    GROUP_EDGES=True, # gộp VAH/VAL với VWAP ±1σ cùng kỳ thành một nhóm (False: mỗi tên mức là một nhóm)
    MIN_GROUP=1,      # hiển thị: cần ít nhất bấy nhiêu nhóm mức hợp lưu
    RADIUS=4.0,       # hiển thị: mép gần của vùng cách giá hiện tại tối đa (×U)
    MAX_SIDE=3,       # hiển thị: tối đa bấy nhiêu vùng mỗi phía giá
    SEP=0.15,         # hiển thị: hai vùng cách nhau dưới bấy nhiêu (×U) thì chỉ giữ vùng mạnh hơn
    HVN_RADIUS=8.0,   # hiển thị HỘP HVN (PLAN mục 13.5): mép gần cách giá tối đa (×U) — riêng cho hộp HVN, vùng mạnh vẫn RADIUS
    HVN_MAX_SIDE=2,   # hiển thị hộp HVN: tối đa bấy nhiêu hộp gần nhất mỗi phía giá (hộp đang chứa giá không tính)
)

# nhóm mức độc lập: VAH và VWAP+1σ của cùng một kỳ gần như trùng nhau do cấu tạo (vùng giá trị 70% ≈ ±1σ) ⇒ tính MỘT.
GROUP = {'vwap_d': 'giua_d', 'vah_d': 'tren_d', 'vwap_d_tren': 'tren_d', 'val_d': 'duoi_d', 'vwap_d_duoi': 'duoi_d',
         'vwap_w': 'giua_w', 'vah_w': 'tren_w', 'vwap_w_tren': 'tren_w', 'val_w': 'duoi_w', 'vwap_w_duoi': 'duoi_w',
         'hvn_d': 'hvn_d', 'hvn_w': 'hvn_w', 'lo_w1': 'bien_w1', 'hi_w1': 'bien_w1', 'lo_w0': 'bien_w0', 'hi_w0': 'bien_w0'}
TEN = {'vwap_d': 'VWAP hôm qua', 'vwap_d_tren': 'VWAP hôm qua +1σ', 'vwap_d_duoi': 'VWAP hôm qua −1σ',
       'vah_d': 'VAH hôm qua', 'val_d': 'VAL hôm qua',
       'vwap_w': 'VWAP tuần trước', 'vwap_w_tren': 'VWAP tuần trước +1σ', 'vwap_w_duoi': 'VWAP tuần trước −1σ',
       'vah_w': 'VAH tuần trước', 'val_w': 'VAL tuần trước', 'hvn_d': 'HVN ngày', 'hvn_w': 'HVN tuần',
       'lo_w1': 'đáy tuần trước', 'hi_w1': 'đỉnh tuần trước', 'lo_w0': 'đáy tuần này', 'hi_w0': 'đỉnh tuần này'}
THU_TU = ['hvn_w', 'hvn_d', 'vah_w', 'val_w', 'vwap_w', 'vwap_w_tren', 'vwap_w_duoi', 'vah_d', 'val_d', 'vwap_d', 'vwap_d_tren', 'vwap_d_duoi', 'lo_w1', 'hi_w1', 'lo_w0', 'hi_w0']


def peak_sharpness(pr, w, i, frac=0.90):
    """Port ProfileEngine.PeakSharpness: nới LIÊN TỤC từ hàng đỉnh trên khối lượng THÔ tới khi < frac × đỉnh."""
    thr = frac * w[i]
    lo = hi = i
    while lo > 0 and abs(pr[lo] - pr[lo - 1] - ROW) < 1e-6 and w[lo - 1] >= thr: lo -= 1
    while hi < len(w) - 1 and abs(pr[hi + 1] - pr[hi] - ROW) < 1e-6 and w[hi + 1] >= thr: hi += 1
    return pr[lo], pr[hi]


def profile_stats(D, a, b):
    pr, w = D.rows_over(a, b)
    if len(w) < 3: return None
    poc, vah, val = value_area(pr, w)
    rng = max(pr[-1] - pr[0], 1e-9)
    m, s = D.vwap_sigma(a, b)
    return dict(pr=pr, w=w, poc=poc, vah=vah, val=val, vwap=m, sigma=s, poc_pos=(poc - pr[0]) / rng, va_frac=(vah - val) / rng)


def is_d_shape(st, p=P):
    return p['D_POC_LO'] <= st['poc_pos'] <= p['D_POC_HI'] and st['va_frac'] <= p['D_VA_MAX']


def day_levels(D, d, p=P):
    """Mức hợp lưu của phiên d (chỉ từ phiên/tuần ĐÃ ĐÓNG trước phiên d; HVN tuần này tính tới hết hôm qua)."""
    out = []
    a0 = D.days[d][0]
    seg = D.seg_of[a0]
    last_sp = max([s for s in D.splices if s <= a0], default=0)

    def add_hvn(a, b, name, src):
        st = profile_stats(D, a, b)
        if st is None: return
        if p.get('HVN_MODE', 'dinh') == 'cum2':      # HVN dạng cụm v2 (hvn_cum2.py, PLAN mục 13)
            import hvn_cum2 as HC2
            tk, v = D.ticks_over(a, b)
            up = float((D.m30['h'][a:b + 1] - D.m30['l'][a:b + 1]).mean())
            hp = dict(HC2.HP2, **p.get('HVN2', {}))
            cl, ex = HC2.clusters(tk, v, up / TICK, b - a + 1, hp, hp['Y_W'] if name == 'hvn_w' else hp['Y'])
            import vung_dem as VD                       # vùng đệm (PLAN mục 14): chỉ để VẼ, không dùng trong hợp lưu / "rời xa"
            VD.add_buffers(cl, ex, up / TICK)
            for c in cl:
                out.append(dict(name=name, lo=round(c['lo'] * TICK, 6), hi=round(c['hi'] * TICK, 6), peak=round(c['peak'] * TICK, 6),
                                ratio=c['mass'], bars=c['bars'], con=c['con'], end=b, src=src, dshape=is_d_shape(st, p), cum=True,
                                blo=round(c['blo'] * TICK, 6), bhi=round(c['bhi'] * TICK, 6)))
            return
        if p.get('HVN_MODE', 'dinh') == 'cum':
            tk, v = D.ticks_over(a, b)
            up = float((D.m30['h'][a:b + 1] - D.m30['l'][a:b + 1]).mean())
            hp = dict(SM=p['HVN_SM'], X=p['HVN_X'], PK2=p['HVN_PK2'], Y=p['HVN_Y_W'] if name == 'hvn_w' else p['HVN_Y'], WMIN=p['HVN_WMIN'], MAXC=p['HVN_MAXC'])
            cl, _ = HC.clusters(tk, v, up / TICK, hp)
            for c in cl:
                out.append(dict(name=name, lo=round(c['lo'] * TICK, 6), hi=round(c['hi'] * TICK, 6), peak=round(c['peak'] * TICK, 6),
                                ratio=c['mass'], end=b, src=src, dshape=is_d_shape(st, p), cum=True))
            return
        res, sm = find_hvn(st['pr'], st['w'])
        dsh = is_d_shape(st, p)
        for i, pk, ratio in res[:p['HVN_TOP']]:
            if ratio < p['HVN_RATIO']: continue
            lo, hi = peak_sharpness(st['pr'], st['w'], i)
            out.append(dict(name=name, lo=lo, hi=hi, peak=pk, ratio=ratio, end=b, src=src, dshape=dsh))

    y = d - 1
    while y >= 0 and (D.days[y][1] - D.days[y][0] + 1) < MIN_DAY_BARS: y -= 1
    if y >= 0 and D.seg_of[D.days[y][0]] == seg:
        st = profile_stats(D, *D.days[y])
        if st is not None:
            for nm, v in (('vwap_d', st['vwap']), ('vwap_d_tren', st['vwap'] + st['sigma']), ('vwap_d_duoi', st['vwap'] - st['sigma']),
                          ('vah_d', st['vah']), ('val_d', st['val'])):
                out.append(dict(name=nm, lo=v, hi=v))
    cnt, yy = 0, d - 1
    while yy >= 0 and cnt < p['HVN_DAYS']:
        a, b = D.days[yy]
        if D.seg_of[a] != seg: break
        if b - a + 1 >= MIN_DAY_BARS:
            add_hvn(a, b, 'hvn_d', d - yy); cnt += 1
        yy -= 1
    w = D.week_of[a0]
    if w >= 1:
        a, b = D.weeks[w - 1]
        a = max(a, last_sp)
        if b - a + 1 >= 60:
            st = profile_stats(D, a, b)
            if st is not None:
                for nm, v in (('vwap_w', st['vwap']), ('vwap_w_tren', st['vwap'] + st['sigma']), ('vwap_w_duoi', st['vwap'] - st['sigma']),
                              ('vah_w', st['vah']), ('val_w', st['val'])):
                    out.append(dict(name=nm, lo=v, hi=v))
            add_hvn(a, b, 'hvn_w', 1)
    a = max(D.weeks[w][0], last_sp); b = a0 - 1
    if b - a + 1 >= 60:
        add_hvn(a, b, 'hvn_w', 0)
    if p.get('WK_EXT'):       # THỬ NGHIỆM (HVN-CUM-V2.md mục 4, chưa vào spec): đáy/đỉnh tuần trước và tuần này tới hết hôm qua
        if w >= 1:
            a, b = D.weeks[w - 1]; a = max(a, last_sp)
            if b - a + 1 >= 60:
                out.append(dict(name='lo_w1', lo=float(D.m30['l'][a:b + 1].min()), hi=float(D.m30['l'][a:b + 1].min())))
                out.append(dict(name='hi_w1', lo=float(D.m30['h'][a:b + 1].max()), hi=float(D.m30['h'][a:b + 1].max())))
        a = max(D.weeks[w][0], last_sp); b = a0 - 1
        if b - a + 1 >= MIN_DAY_BARS:
            out.append(dict(name='lo_w0', lo=float(D.m30['l'][a:b + 1].min()), hi=float(D.m30['l'][a:b + 1].min())))
            out.append(dict(name='hi_w0', lo=float(D.m30['h'][a:b + 1].max()), hi=float(D.m30['h'][a:b + 1].max())))
    return out


def hvn_ok(D, L, j, u, p=P):
    """HVN đủ điều kiện tại nến j: (tuỳ chọn) profile chữ D, và sau khi profile chốt giá đã từng cách đỉnh cụm >= HVN_AWAY × U."""
    if p['D_ONLY'] and not L['dshape']: return False
    a = L['end'] + 1
    if a > j: return False
    if L.get('cum'):      # hộp: đo từ MÉP hộp
        far = max(D.m30['h'][a:j + 1].max() - L['hi'], L['lo'] - D.m30['l'][a:j + 1].min())
    else:
        far = max(D.m30['h'][a:j + 1].max() - L['peak'], L['peak'] - D.m30['l'][a:j + 1].min())
    return far >= p['HVN_AWAY'] * u


def cluster_sorted(prices, wc):
    """prices tăng dần. Lặp: neo có nhiều điểm nhất trong [p, p + wc] (hoà → neo giá thấp hơn) → lấy nhóm → bỏ ra."""
    alive = np.ones(len(prices), bool)
    res = []
    while alive.any():
        ids = np.where(alive)[0]
        q = prices[ids]
        cnt = np.searchsorted(q, q + wc + 1e-9, side='right') - np.arange(len(q))
        a = int(np.argmax(cnt))
        mem = ids[a:a + cnt[a]]
        res.append(mem)
        alive[mem] = False
    return res


class Engine:
    def __init__(self, D, p=P):
        self.D, self.p = D, dict(p)
        pv = pivots(D, k=p['K'], m=p['M'], r=p['R'])
        self.pv = pv[np.argsort(pv['conf'], kind='stable')]
        self._lv = {}
        self._key, self._clusters = None, []

    def levels(self, d):
        if d not in self._lv:
            if len(self._lv) > 3: self._lv.clear()
            self._lv[d] = day_levels(self.D, d, self.p)
        return self._lv[d]

    def zones(self, j):
        """Vùng mạnh khi nến M30 j vừa đóng (nến j+1 là nến đang chạy, thuộc phiên 'hôm nay')."""
        D, p = self.D, self.p
        jn = min(j + 1, D.n - 1)
        d = int(D.day_of[jn]); u = D.U[jn]
        if not np.isfinite(u): return []
        hi_ptr = np.searchsorted(self.pv['conf'], j, side='right')
        lb_start = D.days[max(0, d - p['LB'])][0]
        key = (hi_ptr, lb_start, d)
        if key != self._key:
            self._key = key
            act = self.pv[:hi_ptr]
            act = act[(act['idx'] >= lb_start) & (D.seg_of[act['idx']] == D.seg_of[jn])]
            act = act[np.argsort(act['price'], kind='stable')]
            self._clusters = [act[m] for m in cluster_sorted(act['price'], p['WC'] * u)] if len(act) else []
        lv = self.levels(d)
        out = []
        for g in self._clusters:
            if len(g) < p['NMIN']: continue
            pmin, pmax = g['price'].min(), g['price'].max()
            lo, hi = pmin - p['PAD'] * u, pmax + p['PAD'] * u
            if hi - lo < p['WMIN'] * u:
                mid = (pmin + pmax) / 2; lo, hi = mid - p['WMIN'] * u / 2, mid + p['WMIN'] * u / 2
            lo, hi = np.floor(lo / TICK + 1e-6) * TICK, np.ceil(hi / TICK - 1e-6) * TICK
            names = []
            for L in lv:
                tol = p['TOL'] * u
                if L.get('cum') and p.get('HVN_HL', 'giao') == 'mep':
                    hit = (lo - tol <= L['lo'] <= hi + tol) or (lo - tol <= L['hi'] <= hi + tol)
                else:
                    hit = L['lo'] <= hi + tol and L['hi'] >= lo - tol
                if hit:
                    if L['name'].startswith('hvn') and not hvn_ok(D, L, j, u, p): continue
                    names.append(L['name'])
            names = [n for n in THU_TU if n in names]
            groups = set((GROUP[n] if p['GROUP_EDGES'] else n) for n in names)
            if p.get('HVN_ONE_GROUP'): groups = set('hvn' if g_.startswith('hvn') else g_ for g_ in groups)   # THỬ NGHIỆM (HVN-CUM-V2.md mục 5): HVN ngày + HVN tuần tính MỘT nhóm
            has_hvn = any(n.startswith('hvn') for n in names)
            out.append(dict(lo=lo, hi=hi, n=len(g), n_hi=int((g['kind'] > 0).sum()), pmin=pmin, pmax=pmax,
                            newest=int(g['idx'].max()), oldest=int(g['idx'].min()), names=names, ngroup=len(groups),
                            hvn=has_hvn, gold=(len(groups) >= p['GOLD_MIN'] and has_hvn), u=u,
                            ndays=len(set(D.day_of[g['idx']].tolist()))))
        return out


def side_of(D, z, j, back=400):
    """+1 = hỗ trợ (giá ở trên vùng), −1 = kháng cự. Giá đang trong vùng → lùi về nến M30 gần nhất đóng NGOÀI vùng."""
    c = D.m30['c']
    for i in range(j, max(j - back, -1), -1):
        if c[i] > z['hi']: return 1
        if c[i] < z['lo']: return -1
    return 0


def label(z, side):
    head = ('Hỗ trợ' if side > 0 else 'Kháng cự' if side < 0 else 'Vùng')
    if z['gold']: head = '★ ' + head + ' rất mạnh'
    seen, parts = set(), []
    for n in z['names']:
        if TEN[n] not in seen: seen.add(TEN[n]); parts.append(TEN[n])
    return '%s · %d lần · %s' % (head, z['n'], ' + '.join(parts)) if parts else '%s · %d lần' % (head, z['n'])


def display(D, zs, j, now, p=P):
    """Lọc hiển thị + gán phía/màu/nhãn. now = giá hiện tại. Trả list vùng ĐƯỢC VẼ (thêm side, color, label, dist).
    Thứ tự: (1) đủ nhóm hợp lưu → (2) vùng sát/chồng nhau chỉ giữ vùng mạnh hơn → (3) bán kính → (4) trần mỗi phía."""
    pool = sorted([dict(z) for z in zs if z['ngroup'] >= p['MIN_GROUP']],
                  key=lambda z: (not z['gold'], -z['ngroup'], -z['n'], -z['newest'], z['lo']))
    kept = []
    for z in pool:
        if all(max(z['lo'], k['lo']) - min(z['hi'], k['hi']) >= p['SEP'] * z['u'] for k in kept):
            kept.append(z)
    cand = []
    for z in kept:
        if now > z['hi']: z['side'], z['dist'], z['inside'] = 1, now - z['hi'], False
        elif now < z['lo']: z['side'], z['dist'], z['inside'] = -1, z['lo'] - now, False
        else: z['side'], z['dist'], z['inside'] = side_of(D, z, j), 0.0, True
        if z['dist'] > p['RADIUS'] * z['u']: continue
        z['color'] = 'vang' if z['gold'] else ('xanh' if z['side'] > 0 else 'do' if z['side'] < 0 else 'xam')
        z['label'] = label(z, z['side']) + (' (giá đang trong vùng)' if z['inside'] else '')
        cand.append(z)
    out = [z for z in cand if z['inside']]
    for sd in (1, -1):
        g = sorted([z for z in cand if not z['inside'] and z['side'] == sd], key=lambda z: (not z['gold'], z['dist']))
        out += g[:p['MAX_SIDE']]
    return sorted(out, key=lambda z: z['lo'])


def hvn_boxes(D, levels, j, now, p=P):
    """Hộp HVN ĐƯỢC VẼ (PLAN mục 13.5) = StrongZones.HvnBoxes: đủ "rời xa", trong HVN_RADIUS × U, bỏ hộp trùng > 50 %,
    rồi mỗi phía giá chỉ giữ HVN_MAX_SIDE hộp gần nhất. Trả list dict name, lo, hi, peak, mass, dist, label (sắp theo lo)."""
    u = D.U[min(j + 1, D.n - 1)]
    cand = []
    for L in levels:
        if not L['name'].startswith('hvn') or not hvn_ok(D, L, j, u, p): continue
        dist = now - L['hi'] if now > L['hi'] else L['lo'] - now if now < L['lo'] else 0.0
        if dist > p['HVN_RADIUS'] * u: continue
        # vùng đệm được vẽ (PLAN mục 14.3): chỉ phía giá đang đứng — giá ở trên/trong hộp ⇒ đệm trên, giá ở dưới/trong hộp ⇒ đệm dưới
        blo, bhi = L.get('blo', L['lo']), L.get('bhi', L['hi'])
        cand.append(dict(name=L['name'], lo=L['lo'], hi=L['hi'], peak=L['peak'], mass=L['ratio'], dist=dist, end=L['end'], src=L['src'],
                         label='HVN tuần' if L['name'] == 'hvn_w' else 'HVN ngày',
                         buf_lo=blo if now <= L['hi'] else L['lo'], buf_hi=bhi if now >= L['lo'] else L['hi']))
    out = []
    for c in sorted(cand, key=lambda x: (-x['end'], 0 if x['name'] == 'hvn_d' else 1, -x['mass'], x['lo'])):
        dup = None
        for k in out:
            inter = min(k['hi'], c['hi']) - max(k['lo'], c['lo']); small = min(k['hi'] - k['lo'], c['hi'] - c['lo'])
            if inter > 0 and inter > 0.5 * small: dup = k; break
        if dup is None: out.append(c)
        elif dup['name'] != c['name']: dup['label'] = 'HVN ngày + tuần'      # cùng một cụm thấy ở cả profile ngày lẫn tuần
    keep = [c for c in out if c['dist'] == 0]
    for below in (True, False):
        g = sorted([c for c in out if c['dist'] > 0 and (c['hi'] < now) == below], key=lambda c: (c['dist'], c['lo']))
        keep += g[:p['HVN_MAX_SIDE']]
    return sorted(keep, key=lambda c: c['lo'])
