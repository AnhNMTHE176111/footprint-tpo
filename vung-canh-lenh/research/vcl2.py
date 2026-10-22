# -*- coding: utf-8 -*-
"""
VÙNG CANH LỆNH — VÒNG 2 (theo review của Fable sau vòng 1). Dùng lại hàm gộp/chuyển vai/thống kê của vcl.py (vòng 1 giữ nguyên).

Khác vòng 1:
  A. Thưa ứng viên: bỏ A (swing M1); B = swing M5 k=5; thêm B15 = swing M15 k=3 (trọng số 3, sống 3 phiên);
     E chỉ giữ TOP 5 mức/phiên theo |delta| (= volume × |delta|/volume), xếp hạng CHẠY trong phiên (không nhìn trước), có VAI
     (delta>0 ⇒ kháng cự, delta<0 ⇒ hỗ trợ); thêm F = đỉnh/đáy bằng nhau (≥2 swing B/B15 cùng phía, cách ≥30 nến, lệch ≤0,3u).
     Vùng chứa giá (hoặc cách < 0,5u) KHÔNG được tính là "gần nhất". Chống nhấp nháy theo "ô": chỉ tính lại bộ vùng khi giá đóng
     vượt cạnh gần của một vùng đang hiển thị, đi ≥ 2u so với giá lúc chốt bộ, hoặc có vùng chết.
  B. Đối chứng KHỚP KHOẢNG CÁCH: vùng giả đặt ở khoảng cách d' (theo u) bốc ngẫu nhiên từ phân phối d của mọi vùng thật cùng phía,
     cùng tách TRAIN/TEST.
  C. Thêm phép đo "tới được" (nam châm), quét thanh khoản cho F, TP/SL trừ phí 0,2.

Chạy:  python3 vcl2.py   → report/VCL-VONG-2.md (+ report/vcl2_records.csv.gz cho ve_vcl.py --vong 2)
"""
import os, sys, time, math, heapq
import numpy as np
import pandas as pd
import vcl as V

K = V.K
SESS = V.SESS
INF = V.INF
N_TRAIN_SESS = V.N_TRAIN_SESS
REPS, SEED = V.REPS, V.SEED
LINK = 1.0
REPORT = V.REPORT

P = dict(V.P)
P.update(swing_k_m5=5, swing_k_m15=3, e_top=5, f_sep=30, f_tol_u=0.3, near_gap_u=0.5, cell_move_u=2.0, cost=0.2,
         sweep_win=10, sweep_max_u=1.5, mag_w=(30, 60, 120), mag_rev_u=2.0, mag_rev_w=30, z10_u=10.0)
V.P.update({k: P[k] for k in ('pad', 'wmin', 'wmax', 'break_u')})      # build_zones/break_update đọc V.P (giá trị không đổi)

TYPES = ['B', 'B15', 'C', 'D', 'E', 'F']
BIT = {t: 1 << k for k, t in enumerate(TYPES)}
KIND = {1: 'B', 6: 'B15', 2: 'C', 3: 'C', 4: 'D', 5: 'E', 7: 'F'}     # 3 = POC trần
BREAK_KINDS = (1, 2, 3, 6, 7)                                          # áp luật chuyển vai/chết (D, E không)


# ---------------------------------------------------------------------------------------------
# 1. ỨNG VIÊN
# ---------------------------------------------------------------------------------------------
def agg_bars(df, minutes):
    """Gộp M1 → N phút theo mốc đồng hồ UTC, không gộp xuyên phiên. avail = vị trí nến M1 mà tại lúc nó đóng thì nến N phút
    chắc chắn đã đóng (chưa hết N phút ⇒ phải chờ nến M1 kế tiếp)."""
    t = df['t_utc'].dt.floor(f'{minutes}min')
    key = [df['session_no'].to_numpy(), t.to_numpy()]
    g = df.groupby(key, sort=True)
    m = pd.DataFrame({'high': g['high'].max(), 'low': g['low'].min()})
    gp = pd.Series(np.arange(len(df))).groupby(key, sort=True)
    m['first_pos'], m['last_pos'] = gp.first().to_numpy(), gp.last().to_numpy()
    m = m.reset_index(names=['session_no', 't_start'])
    t_end = (m['t_start'] + pd.Timedelta(minutes=minutes)).to_numpy()
    t1 = df['t_utc'].to_numpy()
    lp = m['last_pos'].to_numpy()
    m['avail'] = np.where(t1[lp] + np.timedelta64(1, 'm') >= t_end, lp, lp + 1)
    return m


def swings(m, k):
    """Đỉnh/đáy k nến mỗi bên trên nến gộp; birth = avail của nến thứ k sau đỉnh."""
    h, l = m['high'].to_numpy(float), m['low'].to_numpy(float)
    fp, av = m['first_pos'].to_numpy(), m['avail'].to_numpy()
    out = []
    for j in range(k, len(m) - k):
        b = int(av[j + k])
        if h[j] == h[j - k:j + k + 1].max() and (h[j - k:j] < h[j]).all():
            out.append(dict(price=float(h[j]), hl=1, pivot=int(fp[j]), birth=b))
        if l[j] == l[j - k:j + k + 1].min() and (l[j - k:j] > l[j]).all():
            out.append(dict(price=float(l[j]), hl=-1, pivot=int(fp[j]), birth=b))
    return out


def find_equal(sw_all, H, L, u, n):
    """F: đỉnh/đáy bằng nhau. sw_all = [{price, hl, pivot, birth, death}] (B và B15). Với mỗi swing mới, tìm swing cũ cùng phía còn
    sống, cách >= f_sep nến, lệch giá <= f_tol_u·u (u tại lúc xác nhận), và giữa hai đỉnh giá CHƯA vượt qua (đỉnh: không high nào
    > max hai đỉnh + tol; đáy: gương). Trả [{price, hl, birth}] — chỉ dùng dữ liệu <= birth."""
    sw_all = sorted(sw_all, key=lambda s: (s['birth'], s['pivot']))
    out, prev = [], []
    for s in sw_all:
        b = s['birth']
        if b >= n or not (u[b] == u[b]):
            prev.append(s)
            continue
        tol = P['f_tol_u'] * u[b]
        best = None
        for p in prev:
            if p['hl'] != s['hl'] or p['death'] <= b or s['pivot'] - p['pivot'] < P['f_sep'] or abs(p['price'] - s['price']) > tol:
                continue
            a0, a1 = p['pivot'] + 1, s['pivot']
            if s['hl'] == 1 and a1 > a0 and H[a0:a1].max() > max(p['price'], s['price']) + tol:
                continue
            if s['hl'] == -1 and a1 > a0 and L[a0:a1].min() < min(p['price'], s['price']) - tol:
                continue
            if best is None or abs(p['price'] - s['price']) < abs(best['price'] - s['price']):
                best = p
        if best is not None:
            pr = (best['price'] + s['price']) / 2
            dup = any(f['hl'] == s['hl'] and abs(f['price'] - pr) <= tol and f['birth'] + 4 * SESS > b for f in out)
            if not dup:
                out.append(dict(price=pr, hl=s['hl'], birth=b))
        prev.append(s)
    return out


def gen_candidates(ctx):
    """Bảng ứng viên v2: price, kind, w, birth, death, half, erole (+1 hỗ trợ / -1 kháng cự / 0)."""
    df, st = ctx['df'], ctx['st']
    H, L = df['high'].to_numpy(float), df['low'].to_numpy(float)
    n = len(df)
    u = K.median_range(df).to_numpy()
    rows = []

    def add(price, kind, w, birth, death, half=INF, erole=0):
        if birth < n:
            rows.append([float(price), kind, float(w), int(birth), int(death), int(half), int(erole)])
            return len(rows) - 1
        return None

    sw_all = []
    for s in swings(agg_bars(df, 5), P['swing_k_m5']):                     # B
        add(s['price'], 1, 2, s['birth'], s['birth'] + 4 * SESS, s['birth'] + 2 * SESS)
        sw_all.append(dict(s, death=s['birth'] + 4 * SESS))
    for s in swings(agg_bars(df, 15), P['swing_k_m15']):                   # B15
        add(s['price'], 6, 3, s['birth'], s['birth'] + 3 * SESS)
        sw_all.append(dict(s, death=s['birth'] + 3 * SESS))
    f_list = find_equal(sw_all, H, L, u, n)                                # F
    for f in f_list:
        add(f['price'], 7, 2, f['birth'], f['birth'] + 4 * SESS, f['birth'] + 2 * SESS)
    # C (+POC trần): lấy y nguyên từ vòng 1
    c1 = V.gen_candidates(ctx)
    for r in c1[c1['kind'].isin([2, 3])].itertuples():
        add(r.price, r.kind, r.w, r.birth, r.death, r.half)
    # E: >= p99 volume (3 phiên trước) & |delta|/volume >= 0,6; giữ TOP 5 |delta| CHẠY trong phiên, mức bị đẩy khỏi top 5 thì chết
    lv = ctx['lv']
    lpos = pd.Index(df['bar_idx'].to_numpy()).get_indexer(lv['bar_idx'].to_numpy())
    ok = lpos >= 0
    lpos = lpos[ok]
    lvol, ldel, lpr = lv['volume'].to_numpy(float)[ok], lv['delta'].to_numpy(float)[ok], lv['price'].to_numpy(float)[ok]
    lses = df['session_no'].to_numpy()[lpos]
    e_raw, e_born = {}, {}
    for s in st.index:
        prev = (lses >= s - P['e_lookback']) & (lses <= s - 1)
        if not prev.any():
            continue
        thr = np.quantile(lvol[prev], P['e_q'])
        m = np.flatnonzero((lses == s) & (lvol >= thr) & (np.abs(ldel) >= P['e_imb'] * np.maximum(lvol, 1)))
        e_raw[int(s)] = len(m)
        m = m[np.lexsort((-np.abs(ldel[m]), lpos[m]))]                   # theo nến, trong nến |delta| lớn trước
        heap, born = [], 0
        for j in m:
            key = abs(ldel[j])
            if len(heap) >= P['e_top'] and key <= heap[0][0]:
                continue
            ridx = add(lpr[j], 5, 2, lpos[j], lpos[j] + 4 * SESS, lpos[j] + 2 * SESS, -1 if ldel[j] > 0 else 1)
            if ridx is None:
                continue
            born += 1
            if len(heap) >= P['e_top']:
                _, old = heapq.heappop(heap)
                rows[old][4] = min(rows[old][4], int(lpos[j]))            # bị đẩy khỏi top 5 ⇒ chết
            heapq.heappush(heap, (key, ridx))
        e_born[int(s)] = born
    cd = pd.DataFrame(rows, columns=['price', 'kind', 'w', 'birth', 'death', 'half', 'erole'])
    cd = cd.sort_values('birth', kind='stable').reset_index(drop=True)
    cd.attrs.update(e_raw=e_raw, e_born=e_born, n_f=len(f_list))
    return cd


# ---------------------------------------------------------------------------------------------
# 2. CHỌN VÙNG THEO "Ô"
# ---------------------------------------------------------------------------------------------
def match_prev(lo, hi, prev):
    """Khớp vùng hiển thị cũ ↔ vùng hiện tại theo chồng lấn lớn nhất. Trả list chỉ số (-1 = vùng cũ đã chết)."""
    js = []
    for p in prev:
        if len(lo) == 0:
            js.append(-1)
            continue
        ov = np.minimum(p[1], hi) - np.maximum(p[0], lo)
        j = int(np.argmax(ov))
        js.append(j if ov[j] > 0 else -1)
    return js


def fresh_select(lo, hi, score, c, u, maxd):
    """Chọn mới: gần nhất phía trên = vùng đầu tiên có cạnh dưới >= c + 0,5u (gương phía dưới); 2 gần + 1 xa vừa phải mỗi phía."""
    out = []
    g = P['near_gap_u'] * u
    for side in (1, -1):
        if side > 0:
            idx = np.flatnonzero(lo >= c + g)
            d = lo[idx] - c
        else:
            idx = np.flatnonzero(hi <= c - g)
            d = c - hi[idx]
        if len(idx) == 0:
            continue
        o = np.argsort(d, kind='stable')
        near = [int(idx[t]) for t in o[:P['near_n']]]
        pool = [int(idx[t]) for t in o[P['near_n']:] if P['far_lo_u'] * u <= d[t] <= maxd]
        out += [(z, 'N', side) for z in near]
        if pool:
            out.append((max(pool, key=lambda z: score[z]), 'F', side))
    return out


def cell_update(lo, hi, score, c, u, maxd, prev, anchor):
    """prev = [(lo, hi, eid, slot, side)], anchor = giá đóng lúc chốt bộ. Trả (danh sách [(z, slot, eid|None, side)], anchor, tính_lại?).
    Chỉ tính lại khi: chưa có bộ, có vùng cũ chết/nhập nhau, giá đóng vượt cạnh gần của một vùng đang hiển thị, hoặc |c-anchor| >= 2u."""
    js = match_prev(lo, hi, prev)
    trig = (not prev) or any(j < 0 for j in js) or len(set(js)) < len(js) or abs(c - anchor) >= P['cell_move_u'] * u
    if not trig:
        for p, j in zip(prev, js):
            if (p[4] == 1 and c >= lo[j]) or (p[4] == -1 and c <= hi[j]):
                trig = True
                break
    if not trig:
        return [(j, p[3], p[2], p[4]) for p, j in zip(prev, js)], anchor, False
    emap = {j: p[2] for p, j in zip(prev, js) if j >= 0}
    sel = fresh_select(lo, hi, score, c, u, maxd)
    return [(z, slot, emap.get(z), side) for z, slot, side in sel], c, True


# ---------------------------------------------------------------------------------------------
# 3. ENGINE
# ---------------------------------------------------------------------------------------------
REC_COLS = ['bar', 'lo', 'hi', 'score', 'mask', 'conf', 'ncand', 'eid', 'side', 'slot', 'erole']


def run_engine(ctx, cands=None, link=LINK):
    df = ctx['df']
    cands = gen_candidates(ctx) if cands is None else cands
    H, L, C = df['high'].to_numpy(float), df['low'].to_numpy(float), df['close'].to_numpy(float)
    u_all = K.median_range(df).to_numpy()
    sno = df['session_no'].to_numpy()
    st = ctx['st']
    n = len(df)
    srange = {int(s): H[int(r.start_pos):int(r.end_pos) + 1].max() - L[int(r.start_pos):int(r.end_pos) + 1].min()
              for s, r in st.iterrows()}
    s_start = st['start_pos'].to_dict()
    cap = len(cands) + 400
    price = np.zeros(cap); kind = np.zeros(cap, int); w = np.zeros(cap); half = np.zeros(cap, np.int64)
    death = np.zeros(cap, np.int64); erole = np.zeros(cap, int)
    side = np.zeros(cap, int); breaks = np.zeros(cap, int); touch = np.zeros(cap, int); alive = np.zeros(cap, bool)
    cols = {c_: cands[c_].to_numpy() for c_ in ('price', 'kind', 'w', 'birth', 'death', 'half', 'erole')}
    tbit = {k: BIT[t] for k, t in KIND.items()}
    tbit_of = np.zeros(8, int)
    for k_, b_ in tbit.items():
        tbit_of[k_] = b_
    m = ptr = 0
    d_have = set()
    recs, prev, anchor, next_eid = [], [], 0.0, 0
    z10 = np.full(n, np.nan)
    in_any = np.zeros(n, bool)
    n_recalc = 0
    alive_cnt = np.zeros(8)
    n_ok = 0
    for i in range(n):
        while ptr < len(cands) and cols['birth'][ptr] <= i:
            price[m], kind[m], w[m] = cols['price'][ptr], cols['kind'][ptr], cols['w'][ptr]
            death[m], half[m], erole[m] = cols['death'][ptr], cols['half'][ptr], cols['erole'][ptr]
            alive[m] = True
            dd = C[i] - price[m]
            uu = u_all[i] if u_all[i] == u_all[i] else 1.0
            side[m] = 0 if abs(dd) < 0.5 * uu else (1 if dd > 0 else -1)
            m += 1
            ptr += 1
        for v in range(int(math.ceil((C[i] - P['d_window']) / 10.0)) * 10, int(C[i] + P['d_window']) + 1, 10):
            if v not in d_have:
                d_have.add(v)
                price[m], kind[m], death[m], half[m], erole[m] = v, 4, INF, INF, 0
                w[m] = 3.0 if v % 100 == 0 else (2.0 if v % 50 == 0 else 1.0)
                alive[m] = True
                m += 1
        al = alive[:m]
        al &= death[:m] > i
        u = u_all[i]
        if not (u == u) or u <= 0:
            prev = []
            continue
        act = np.flatnonzero(al)
        lab, zlo, zhi = V.build_zones(price[act], u, link)
        if i > 0 and sno[i] == sno[i - 1] and len(act):
            ent = (C[i] >= zlo) & (C[i] <= zhi) & ((C[i - 1] < zlo) | (C[i - 1] > zhi))
            touch[act[ent[lab]]] += 1
        kk = kind[act]
        bm = np.isin(kk, BREAK_KINDS)
        abc = act[bm]
        if len(abc):
            la = lab[bm]
            s2, b2, _ = V.break_update(side[abc], breaks[abc], C[i], zlo[la], zhi[la], u)
            side[abc], breaks[abc] = s2, b2
            alive[abc[b2 >= 2]] = False
        ee = act[kk == 5]
        if len(ee):
            dd = C[i] - price[ee]
            s0 = side[ee] == 0
            side[ee[s0 & (dd >= 0.5 * u)]] = 1
            side[ee[s0 & (dd <= -0.5 * u)]] = -1
            dead = ((side[ee] == 1) & (dd <= -P['e_cross_u'] * u)) | ((side[ee] == -1) & (dd >= P['e_cross_u'] * u))
            alive[ee[dead]] = False
        act = np.flatnonzero(alive[:m])
        np.add.at(alive_cnt, kind[act], 1)
        n_ok += 1
        lab, zlo, zhi = V.build_zones(price[act], u, link)
        nz = len(zlo)
        z10[i] = int(((zhi >= C[i] - P['z10_u'] * u) & (zlo <= C[i] + P['z10_u'] * u)).sum())
        in_any[i] = bool(((C[i] >= zlo) & (C[i] <= zhi)).any())
        val = w[act] * np.where(i >= half[act], 0.5, 1.0) * (1 + P['touch_k'] * np.minimum(touch[act], P['touch_cap'])) \
            * P['flip_mult'] ** breaks[act]
        score = np.bincount(lab, val, minlength=nz)
        mask = np.zeros(nz, int)
        np.bitwise_or.at(mask, lab, tbit_of[kind[act]])
        ncand = np.bincount(lab, minlength=nz)
        erz = np.sign(np.bincount(lab, erole[act] * (kind[act] == 5) * w[act], minlength=nz)).astype(int)
        s = int(sno[i])
        if s >= 1:
            pr = srange[s - 1]
        else:
            a = int(s_start[s])
            pr = max(H[a:i + 1].max() - L[a:i + 1].min(), 10 * u)
        sel, anchor, rc = cell_update(zlo, zhi, score, C[i], u, P['far_range_k'] * pr, prev, anchor)
        n_recalc += rc
        prev = []
        for z, slot, eid, sd in sel:
            if eid is None:
                eid = next_eid
                next_eid += 1
            recs.append((i, zlo[z], zhi[z], score[z], int(mask[z]), bin(int(mask[z])).count('1'), int(ncand[z]), eid, sd, slot,
                         int(erz[z])))
            prev.append((zlo[z], zhi[z], eid, slot, sd))
    rec = pd.DataFrame(recs, columns=REC_COLS)
    am = {t: 0.0 for t in TYPES}
    for k_, t in KIND.items():
        am[t] += alive_cnt[k_] / max(n_ok, 1)
    return dict(rec=rec, z10=z10, in_any=in_any, alive_mean=am, n_recalc=n_recalc)


# ---------------------------------------------------------------------------------------------
# 4. ĐỐI CHỨNG + ĐO
# ---------------------------------------------------------------------------------------------
def episodes(rec):
    rec = rec.sort_values(['eid', 'bar']).reset_index(drop=True)
    e = rec['eid'].to_numpy()
    cut = np.r_[0, np.flatnonzero(np.diff(e)) + 1, len(e)]
    return rec, cut


def make_offsets(ctx, rec, cut, mode, reps=REPS, seed=SEED):
    """off[e, 0] = 0 (thật), off[e, 1..reps] = dời vùng giả.
    mode='dist': khoảng cách cạnh gần d' (theo u) bốc từ phân phối d thật cùng phía, cùng TRAIN/TEST.
    mode='range': tâm ~ U[đáy phiên trước-2, đỉnh phiên trước+2] (đối chứng vòng 1)."""
    df, st = ctx['df'], ctx['st']
    H, L, C = df['high'].to_numpy(float), df['low'].to_numpy(float), df['close'].to_numpy(float)
    u = K.median_range(df).to_numpy()
    sno = df['session_no'].to_numpy()
    rng = np.random.default_rng(seed)
    n_ep = len(cut) - 1
    a = cut[:-1]
    b0 = rec['bar'].to_numpy()[a]
    lo0, hi0, sd = rec['lo'].to_numpy()[a], rec['hi'].to_numpy()[a], rec['side'].to_numpy()[a]
    c0, u0 = C[b0], u[b0]
    dist_u = np.where(sd == 1, lo0 - c0, c0 - hi0) / u0
    off = np.zeros((n_ep, reps + 1))
    if mode == 'dist':
        tr = sno[b0] < N_TRAIN_SESS
        for s_ in (1, -1):
            for t_ in (True, False):
                g = np.flatnonzero((sd == s_) & (tr == t_))
                if len(g) == 0:
                    continue
                dd = rng.choice(dist_u[g], size=(len(g), reps)) * u0[g, None]
                if s_ == 1:
                    off[g, 1:] = c0[g, None] + dd - lo0[g, None]
                else:
                    off[g, 1:] = c0[g, None] - dd - hi0[g, None]
    else:
        s_start, s_end = st['start_pos'].to_numpy(), st['end_pos'].to_numpy()
        for e in range(n_ep):
            s = int(sno[b0[e]])
            if s >= 1:
                pa, pe = s_start[s - 1], s_end[s - 1]
                plo, phi = L[pa:pe + 1].min(), H[pa:pe + 1].max()
            else:
                plo, phi = L[s_start[s]:b0[e] + 1].min(), H[s_start[s]:b0[e] + 1].max()
            off[e, 1:] = rng.uniform(plo - 2, phi + 2, reps) - (lo0[e] + hi0[e]) / 2
    return off, dist_u


EV_COLS = ['rep', 'ep', 'i', 'k', 'hit', 'bounce', 'lo', 'hi', 'u', 'mask', 'conf', 'erole', 'sweep',
           'pen', 'tp_u', 'tp_res', 'r_plan', 'r_real', 'r_cost', 't_tp']


def measure(ctx, rec, mode='dist', reps=REPS, magnet=True):
    df, st = ctx['df'], ctx['st']
    H, L, C = df['high'].to_numpy(float), df['low'].to_numpy(float), df['close'].to_numpy(float)
    u_all = K.median_range(df).to_numpy()
    sno = df['session_no'].to_numpy()
    n = len(df)
    s_end = st['end_pos'].to_numpy()
    thin = st['thin'].to_numpy()
    meas_sess = np.array([(s >= 1) and not thin[s] for s in range(len(st))])
    rec, cut = episodes(rec)
    off, dist_u = make_offsets(ctx, rec, cut, mode, reps)
    n_ep = len(cut) - 1
    ep_of_eid = {int(rec['eid'].iat[cut[e]]): e for e in range(n_ep)}
    rb = rec.sort_values('bar', kind='stable')
    rb_bar, rb_lo, rb_hi = rb['bar'].to_numpy(), rb['lo'].to_numpy(), rb['hi'].to_numpy()
    rb_ep = np.array([ep_of_eid[int(x)] for x in rb['eid'].to_numpy()])
    bstart = np.searchsorted(rb_bar, np.arange(n + 1))
    lo_all, hi_all, bar_all = rec['lo'].to_numpy(), rec['hi'].to_numpy(), rec['bar'].to_numpy()
    mask_all, conf_all, er_all = rec['mask'].to_numpy(), rec['conf'].to_numpy(), rec['erole'].to_numpy()
    events = []
    for e in range(n_ep):
        a, b = cut[e], cut[e + 1]
        bars = bar_all[a:b]
        nb = bars + 1
        nb_c = np.minimum(nb, n - 1)
        okb = (nb < n) & (sno[nb_c] == sno[bars]) & meas_sess[sno[nb_c]]
        if not okb.any():
            continue
        lo_e, hi_e = lo_all[a:b], hi_all[a:b]
        pc, cc = C[bars], C[nb_c]
        for r in range(reps + 1):
            o = off[e, r]
            zl, zh = lo_e + o, hi_e + o
            inside = (cc >= zl) & (cc <= zh)
            frm = np.where(pc > zh, 1, np.where(pc < zl, -1, 0))
            cand = np.flatnonzero(okb & inside & (frm != 0))
            last_exit = -1
            for t in cand:
                i = int(nb[t])
                if i <= last_exit:
                    continue
                hit = int(frm[t]); l0, h0 = float(zl[t]), float(zh[t]); ui = float(u_all[i])
                send = int(s_end[sno[i]]) + 1
                # quét: trong 10 nến (gồm nến vào), râu vượt biên xa (0, 1,5u] rồi có nến đóng lại về phía cũ (ngoài cạnh gần)
                w1 = min(i + 1 + P['sweep_win'], send, n)
                if hit == 1:
                    pv = l0 - L[i:w1]
                    back = C[i:w1] > h0
                else:
                    pv = H[i:w1] - h0
                    back = C[i:w1] < l0
                sweep = 0
                if (pv > 0).any():
                    f0 = int(np.argmax(pv > 0))
                    if pv.max() <= P['sweep_max_u'] * ui and back[f0 + 1:].any():
                        sweep = 1
                lim = min(i + P['chung_max'], send, n)
                seg = C[i + 1:lim]
                outu, outd = seg > h0, seg < l0
                anyo = outu | outd
                base = (r - 1, e, i)
                meta = (int(mask_all[a + t]), int(conf_all[a + t]), int(er_all[a + t]), sweep)
                if not anyo.any():
                    events.append(base + (-1, hit, np.nan, l0, h0, ui) + meta + (np.nan,) * 7)
                    break                       # chỉ lần vào dải ĐẦU TIÊN: vùng thật bị gỡ khỏi chart ngay khi giá vào nó
                q = int(np.argmax(anyo))
                k = i + 1 + q
                bounce = int((outu[q] and hit == 1) or (outd[q] and hit == -1))
                last_exit = k
                pen = tpd = tpres = rplan = rreal = rcost = ttp = np.nan
                if bounce:
                    pen = (max(0.0, l0 - L[i:k + 1].min()) if hit == 1 else max(0.0, H[i:k + 1].max() - h0)) / ui
                    j0, j1 = bstart[k], bstart[k + 1]
                    if j1 > j0:
                        oo = off[rb_ep[j0:j1], r]
                        zlo_k, zhi_k = rb_lo[j0:j1] + oo, rb_hi[j0:j1] + oo
                        ent = C[k]
                        if hit == 1:
                            cdt = zlo_k[zlo_k > ent]
                            tp = cdt.min() if len(cdt) else np.nan
                            sl = l0 - P['sl_pad'] * ui
                        else:
                            cdt = zhi_k[zhi_k < ent]
                            tp = cdt.max() if len(cdt) else np.nan
                            sl = h0 + P['sl_pad'] * ui
                        if tp == tp and (ent - sl) * hit > 0:
                            risk = abs(ent - sl)
                            tpd = abs(tp - ent) / ui
                            rplan = abs(tp - ent) / risk
                            lim2 = min(k + 1 + P['tp_max'], int(s_end[sno[k]]) + 1, n)
                            hh, ll = H[k + 1:lim2], L[k + 1:lim2]
                            slh, tph = (ll <= sl, hh >= tp) if hit == 1 else (hh >= sl, ll <= tp)
                            fs = int(np.argmax(slh)) if slh.any() else 10 ** 9
                            ft = int(np.argmax(tph)) if tph.any() else 10 ** 9
                            if fs == ft == 10 ** 9:
                                tpres = 0.5
                                endp = C[lim2 - 1] if lim2 - 1 > k else ent
                                rreal = (endp - ent) * hit / risk
                            elif ft < fs:
                                tpres, rreal, ttp = 1.0, rplan, ft + 1
                            else:
                                tpres, rreal = 0.0, -1.0
                            rcost = rreal - P['cost'] / risk
                events.append(base + (k, hit, bounce, l0, h0, ui) + meta + (pen, tpd, tpres, rplan, rreal, rcost, ttp))
                break                           # (áp y hệt cho vùng giả để công bằng)
    ev = pd.DataFrame(events, columns=EV_COLS)
    ev['split'] = np.where(sno[ev['i'].to_numpy()] < N_TRAIN_SESS, 'TRAIN', 'TEST')

    mag = None
    if magnet:
        # "tới được": mỗi vùng hiển thị (lúc xuất hiện), cạnh gần đóng băng; chạm bằng high/low trong 30/60/120 nến (cùng phiên)
        mrows = []
        W = P['mag_w']
        for e in range(n_ep):
            a = cut[e]
            b0 = int(bar_all[a])
            if not meas_sess[sno[b0]] or b0 + 1 >= n:
                continue
            sd = int(rec['side'].iat[a])
            u0 = u_all[b0]
            ne = (lo_all[a] if sd == 1 else hi_all[a]) + off[e]          # (reps+1,)
            c0 = C[b0]
            dd = (ne - c0) * sd / u0
            send = int(s_end[sno[b0]]) + 1
            lim = min(b0 + 1 + max(W) + P['mag_rev_w'], send, n)
            hh, ll = H[b0 + 1:lim], L[b0 + 1:lim]
            T = len(hh)
            touch = (hh[None, :] >= ne[:, None]) if sd == 1 else (ll[None, :] <= ne[:, None])
            tmax = min(T, max(W))
            if tmax == 0:
                first = np.full(len(ne), 10 ** 9)
            else:
                first = np.where(touch[:, :tmax].any(1), np.argmax(touch[:, :tmax], 1), 10 ** 9)
            for r in range(len(ne)):
                f = first[r]
                rev = np.nan
                if f < 10 ** 9:
                    s2 = slice(f + 1, min(f + 1 + P['mag_rev_w'], T))
                    if sd == 1:
                        rev = float((ll[s2] <= ne[r] - P['mag_rev_u'] * u0).any()) if s2.start < s2.stop else 0.0
                    else:
                        rev = float((hh[s2] >= ne[r] + P['mag_rev_u'] * u0).any()) if s2.start < s2.stop else 0.0
                mrows.append((r - 1, e, b0, sd, dd[r], *[float(f < w_) for w_ in W], rev, T))
        mag = pd.DataFrame(mrows, columns=['rep', 'ep', 'b0', 'side', 'd_u'] + [f'reach{w_}' for w_ in W] + ['rev', 'T'])
        mag['split'] = np.where(sno[mag['b0'].to_numpy()] < N_TRAIN_SESS, 'TRAIN', 'TEST')
    return ev, mag, off, (rec, cut, rb, rb_bar, rb_lo, rb_hi, rb_ep, meas_sess)


def hygiene(ctx, run, off, aux, reps=REPS):
    df = ctx['df']
    C = df['close'].to_numpy(float)
    u_all = K.median_range(df).to_numpy()
    sno = df['session_no'].to_numpy()
    n = len(df)
    rec, cut, rb, rb_bar, rb_lo, rb_hi, rb_ep, meas_sess = aux
    firsts = rec['bar'].to_numpy()[cut[:-1]]
    lens = np.diff(cut)
    hy = {}
    for sp in ('TRAIN', 'TEST'):
        bm = meas_sess[sno] & ((sno < N_TRAIN_SESS) == (sp == 'TRAIN')) & ~np.isnan(u_all)
        bars_ok = np.flatnonzero(bm)
        cnt = np.bincount(rb_bar, minlength=n)[bars_ok]
        sel = np.isin(rb_bar, bars_ok)
        wid = (rb_hi - rb_lo)[sel]
        widu = wid / u_all[rb_bar[sel]]
        okset = np.zeros(n, bool)
        okset[bars_ok] = True
        nxt = rb_bar + 1
        use = (nxt < n) & okset[np.minimum(nxt, n - 1)]
        cc = C[np.minimum(nxt, n - 1)]
        ins_r = use & (cc >= rb_lo) & (cc <= rb_hi)
        oo = off[rb_ep, 1:]
        raw_c = (nxt < n)[:, None] & (cc[:, None] >= rb_lo[:, None] + oo) & (cc[:, None] <= rb_hi[:, None] + oo)
        # vùng thật bị gỡ ngay khi giá đóng vào nó ⇒ vùng giả cũng chỉ được tính tới lần giá đóng vào ĐẦU TIÊN
        o_ = np.lexsort((rb_bar, rb_ep))
        rc_ = raw_c[o_].astype(np.int64)
        cs = np.cumsum(rc_, 0)
        st_ = np.r_[0, np.flatnonzero(np.diff(rb_ep[o_])) + 1]
        base_ = np.zeros_like(cs)
        seg_id = np.repeat(np.arange(len(st_)), np.diff(np.r_[st_, len(o_)]))
        prev_cs = np.vstack([np.zeros((1, cs.shape[1]), np.int64), cs])[st_]
        base_ = prev_cs[seg_id]
        first_c = np.zeros_like(raw_c)
        first_c[o_] = (rc_ == 1) & ((cs - base_) == 1)
        ins_c = use[:, None] & first_c
        tgt = bars_ok[bars_ok >= 1]
        ir = np.zeros(n, bool)
        ic = np.zeros((n, reps), bool)
        np.logical_or.at(ir, nxt[use], ins_r[use])
        np.logical_or.at(ic, nxt[use], ins_c[use])
        up = np.bincount(rb_bar[rb['side'].to_numpy() == 1], minlength=n)[bars_ok]
        dn = np.bincount(rb_bar[rb['side'].to_numpy() == -1], minlength=n)[bars_ok]
        new_cnt = okset[firsts].sum()
        life = lens[okset[firsts]]
        hy[sp] = dict(n_bars=len(bars_ok), mean_cnt=cnt.mean(), med_w_u=np.median(widu), med_w_usd=np.median(wid),
                      p90_w_u=np.quantile(widu, .9), inside=ir[tgt].mean(), inside_ctrl=ic[tgt].mean(),
                      inside_any=run['in_any'][bars_ok].mean(), z10=np.nanmean(run['z10'][bars_ok]),
                      chg_per_h=new_cnt / (len(bars_ok) / 60.0), life_med=np.median(life),
                      both1=((up >= 1) & (dn >= 1)).mean(), both3=((up >= 3) & (dn >= 3)).mean())
    return hy


# ---------------------------------------------------------------------------------------------
# 5. BẢNG
# ---------------------------------------------------------------------------------------------
_p, rate = V._p, V.rate


def cmp_cell(real, ctrl):
    return V.cmp_cell(real, ctrl)


def has(d, t):
    return (d['mask'].to_numpy() & BIT[t]) > 0


GROUPS = [('Mọi vùng hiển thị', lambda d: np.ones(len(d), bool))] + \
    [(f'Có loại {t}', (lambda t: lambda d: has(d, t))(t)) for t in TYPES] + [
    ('E đúng vai (giá tới từ phía khớp vai)', lambda d: (d['erole'].to_numpy() != 0) & (d['hit'].to_numpy() == d['erole'].to_numpy())),
    ('E ngược vai', lambda d: (d['erole'].to_numpy() != 0) & (d['hit'].to_numpy() == -d['erole'].to_numpy())),
    ('Hợp lưu 1 loại', lambda d: d['conf'].to_numpy() == 1),
    ('Hợp lưu 2 loại', lambda d: d['conf'].to_numpy() == 2),
    ('Hợp lưu ≥3 loại', lambda d: d['conf'].to_numpy() >= 3),
    ('Hợp lưu ≥2 loại, có C hoặc E', lambda d: (d['conf'].to_numpy() >= 2) & (has(d, 'C') | has(d, 'E'))),
]


def tab_bounce(ev):
    R = ev[(ev['rep'] == -1) & ev['bounce'].notna()]
    G = ev[(ev['rep'] >= 0) & ev['bounce'].notna()]
    md = ['### 1. Bật / xuyên (Chung&Bellotti, vào dải bằng giá đóng) — đối chứng khớp khoảng cách', '',
          '| Nhóm vùng | TRAIN bật % ±se (n) | giả % | hiệu | TEST bật % ±se (n) | giả % | hiệu |', '|---|---|---|---|---|---|---|']
    for name, f in GROUPS:
        row = [name]
        for sp in ('TRAIN', 'TEST'):
            r, g = R[R['split'] == sp], G[G['split'] == sp]
            row += cmp_cell(r[f(r)]['bounce'], g[f(g)]['bounce'])
        md.append('| ' + ' | '.join(row) + ' |')
    md += ['', '≈ = |hiệu| ≤ 2 sai số; ▲/▼ = vượt 2 sai số. "giả %" = cùng nhóm (theo loại của vùng thật được dời) trên vùng giả.', '']
    md += ['### 1b. Quét thanh khoản (giả thuyết F): trong 10 nến từ lúc vào dải, râu vượt biên xa ≤ 1,5u rồi đóng lại về phía cũ', '',
           '| Nhóm vùng | TRAIN quét % ±se (n) | giả % | hiệu | TEST quét % ±se (n) | giả % | hiệu |', '|---|---|---|---|---|---|---|']
    R2, G2 = ev[ev['rep'] == -1], ev[ev['rep'] >= 0]
    for name, f in [GROUPS[0], GROUPS[1], GROUPS[2], GROUPS[6]]:
        row = [name]
        for sp in ('TRAIN', 'TEST'):
            r, g = R2[R2['split'] == sp], G2[G2['split'] == sp]
            row += cmp_cell(r[f(r)]['sweep'], g[f(g)]['sweep'])
        md.append('| ' + ' | '.join(row) + ' |')
    md.append('')
    return md


def tab_pen(ev):
    R = ev[(ev['rep'] == -1) & (ev['bounce'] == 1)]
    G = ev[(ev['rep'] >= 0) & (ev['bounce'] == 1)]
    md = ['### 2. Độ rộng vs nhiễu — râu xuyên quá biên xa ở các ca BẬT (đơn vị u)', '',
          '| | n bật | p50 | p85 | p95 | % > 0,5u (SL biên xa+0,5u bị quét) |', '|---|---|---|---|---|---|']
    for sp in ('TRAIN', 'TEST'):
        for lab, d in (('Vùng thật', R[R['split'] == sp]), ('Vùng giả', G[G['split'] == sp])):
            x = d['pen'].to_numpy()
            if len(x) == 0:
                md.append(f'| {sp} · {lab} | 0 | – | – | – | – |')
                continue
            q = np.quantile(x, [.5, .85, .95])
            p5, se5, _ = rate(x > 0.5)
            md.append(f'| {sp} · {lab} | {len(x)} | {q[0]:.2f} | {q[1]:.2f} | {q[2]:.2f} | {_p(p5)} ±{_p(se5)} |')
    md.append('')
    return md


def tab_tp(ev):
    R = ev[(ev['rep'] == -1) & (ev['bounce'] == 1) & ev['tp_res'].notna()]
    G = ev[(ev['rep'] >= 0) & (ev['bounce'] == 1) & ev['tp_res'].notna()]
    md = ['### 3. TP = cạnh gần vùng kế tiếp cùng hướng, SL = biên xa + 0,5u, vào ở giá đóng nến bật, tối đa 240 nến, **trừ phí 0,2 giá**', '',
          '| Tách | Khoảng TP | n thật | TP trước SL % ±se | giả % | R kế hoạch TB (thật/giả) | R sau phí TB (thật/giả) | ± R thật | phút tới TP (trung vị) |',
          '|---|---|---|---|---|---|---|---|---|']
    for sp in ('TRAIN', 'TEST'):
        for blab, lo_, hi_ in (('tất cả', -1, 1e9), ('≤3u', -1, 3), ('3–6u', 3, 6), ('>6u', 6, 1e9)):
            r = R[(R['split'] == sp) & (R['tp_u'] > lo_) & (R['tp_u'] <= hi_)]
            g = G[(G['split'] == sp) & (G['tp_u'] > lo_) & (G['tp_u'] <= hi_)]
            p, se, nn = rate((r['tp_res'] == 1).astype(float))
            q, _, _ = rate((g['tp_res'] == 1).astype(float))
            ser = r['r_cost'].std() / math.sqrt(max(len(r), 1)) if len(r) > 1 else np.nan
            md.append(f"| {sp} | {blab} | {nn} | {_p(p)} ±{_p(se)} | {_p(q)} | {r['r_plan'].mean():.2f} / {g['r_plan'].mean():.2f} | "
                      f"{r['r_cost'].mean():+.2f} / {g['r_cost'].mean():+.2f} | ±{ser:.2f} | {r['t_tp'].median():.0f} |")
    md += ['', 'R sau phí: thắng = +R kế hoạch, thua = −1, hết giờ = lãi/lỗ tạm; trừ 0,2 giá / khoảng SL. Không có vùng kế tiếp ⇒ bỏ.', '']
    return md


def tab_magnet(mag):
    md = ['### 8. "Tới được" (nam châm) — mỗi vùng lúc xuất hiện, cạnh gần đóng băng, chạm bằng high/low, chỉ trong phiên', '',
          '| Tách | Khoảng cách d | n thật | chạm ≤30 nến % thật / giả | ≤60 nến | ≤120 nến | chạm rồi quay lại ≥2u trong 30 nến % thật / giả (n chạm) |',
          '|---|---|---|---|---|---|---|']
    for sp in ('TRAIN', 'TEST'):
        for lab, lo_, hi_ in (('≤3u', -1, 3), ('3–6u', 3, 6), ('6–12u', 6, 12)):
            r = mag[(mag['rep'] == -1) & (mag['split'] == sp) & (mag['d_u'] > lo_) & (mag['d_u'] <= hi_)]
            g = mag[(mag['rep'] >= 0) & (mag['split'] == sp) & (mag['d_u'] > lo_) & (mag['d_u'] <= hi_)]
            cells = []
            for w_ in P['mag_w']:
                a, b, d = cmp_cell(r[f'reach{w_}'], g[f'reach{w_}'])
                cells.append(f"{a.split(' (')[0]} / {b} ({d})")
            a, b, d = cmp_cell(r['rev'], g['rev'])
            cells.append(f"{a} / {b} ({d})")
            md.append(f"| {sp} | {lab} | {len(r)} | " + ' | '.join(cells) + ' |')
    md += ['', 'Giả = cùng nhóm khoảng cách d (theo khoảng cách của chính vùng giả). Hết phiên trước khi chạm ⇒ tính "không chạm".', '']
    return md


def tab_contrib(ev):
    R = ev[(ev['rep'] == -1) & ev['bounce'].notna()]
    G = ev[(ev['rep'] >= 0) & ev['bounce'].notna()]
    md = ['### 5. Đóng góp từng loại ứng viên (vùng có chứa loại đó)', '',
          '| Loại | Tách | n | bật % − giả % | xâm nhập p85 (u) thật / giả | TP % thật / giả | R sau phí TB thật / giả |',
          '|---|---|---|---|---|---|---|']
    for name, f in GROUPS[1:9]:
        for sp in ('TRAIN', 'TEST'):
            r, g = R[(R['split'] == sp)], G[(G['split'] == sp)]
            r, g = r[f(r)], g[f(g)]
            _, _, d = cmp_cell(r['bounce'], g['bounce'])
            rb_, gb_ = r[r['bounce'] == 1], g[g['bounce'] == 1]
            p85r = np.quantile(rb_['pen'], .85) if len(rb_) else np.nan
            p85g = np.quantile(gb_['pen'], .85) if len(gb_) else np.nan
            rt, gt = rb_[rb_['tp_res'].notna()], gb_[gb_['tp_res'].notna()]
            pr, sr, _ = rate((rt['tp_res'] == 1).astype(float))
            pg, _, _ = rate((gt['tp_res'] == 1).astype(float))
            md.append(f"| {name.replace('Có loại ', '')} | {sp} | {len(r)} | {d} | {p85r:.2f} / {p85g:.2f} | {_p(pr)} ±{_p(sr)} / {_p(pg)} | "
                      f"{rt['r_cost'].mean():+.2f} / {gt['r_cost'].mean():+.2f} |")
    md.append('')
    return md


def tab_hyg(hy):
    md = ['### 4. Vệ sinh chart (v2)', '',
          '| Tách | vùng hiển thị TB | rộng trung vị (u / USD) | p90 rộng (u) | % nến đóng trong vùng HIỂN THỊ (thật / giả) | % nến đóng trong BẤT KỲ vùng sống nào | '
          'vùng sống trong ±10u | đổi vùng / giờ | tuổi thọ trung vị vùng hiển thị (phút) | % có ≥1 vùng cả 2 phía | % đủ 3+3 |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for sp in ('TRAIN', 'TEST'):
        h = hy[sp]
        md.append(f"| {sp} | {h['mean_cnt']:.2f} | {h['med_w_u']:.2f} / {h['med_w_usd']:.2f} | {h['p90_w_u']:.2f} | "
                  f"{_p(h['inside'])} / {_p(h['inside_ctrl'])} | {_p(h['inside_any'])} | {h['z10']:.1f} | {h['chg_per_h']:.1f} | "
                  f"{h['life_med']:.0f} | {_p(h['both1'])} | {_p(h['both3'])} |")
    md.append('')
    return md


def v1_hygiene(ctx, cands1):
    """Chạy lại engine vòng 1 (gộp 1,0u) để lấy 3 chỉ số 'trước' theo TRAIN/TEST."""
    run = V.run_engine(ctx, 1.0, cands1)
    rec = run['rec']
    df = ctx['df']
    C = df['close'].to_numpy(float)
    sno = df['session_no'].to_numpy()
    u_all = K.median_range(df).to_numpy()
    st = ctx['st']
    thin = st['thin'].to_numpy()
    meas = np.array([(s >= 1) and not thin[s] for s in range(len(st))])
    n = len(df)
    out = {}
    rb_bar, lo, hi = rec['bar'].to_numpy(), rec['lo'].to_numpy(), rec['hi'].to_numpy()
    nxt = np.minimum(rb_bar + 1, n - 1)
    ins = np.zeros(n, bool)
    np.logical_or.at(ins, nxt, (C[nxt] >= lo) & (C[nxt] <= hi) & (rb_bar + 1 < n))
    firsts = rec.groupby('eid')['bar'].min().to_numpy()
    for sp in ('TRAIN', 'TEST'):
        bm = meas[sno] & ((sno < N_TRAIN_SESS) == (sp == 'TRAIN')) & ~np.isnan(u_all)
        bars_ok = np.flatnonzero(bm)
        okset = np.zeros(n, bool)
        okset[bars_ok] = True
        out[sp] = dict(inside=ins[bars_ok[bars_ok >= 1]].mean(), z10=np.nanmean(run['stats']['z10_bar'][bars_ok]),
                       chg=okset[firsts].sum() / (len(bars_ok) / 60.0))
    return out


# ---------------------------------------------------------------------------------------------
def main():
    t0 = time.time()
    bars, lv = V.load_all()
    ctx = V.prepare(bars, lv)
    st = ctx['st']
    cands = gen_candidates(ctx)
    t1 = time.time()
    run = run_engine(ctx, cands)
    t_eng = time.time() - t1
    rec = run['rec']
    os.makedirs(REPORT, exist_ok=True)
    rec.to_csv(os.path.join(REPORT, 'vcl2_records.csv.gz'), index=False)
    ev, mag, off, aux = measure(ctx, rec, 'dist')
    hy = hygiene(ctx, run, off, aux)
    ev_old, _, _, _ = measure(ctx, rec, 'range', magnet=False)
    v1h = v1_hygiene(ctx, V.gen_candidates(ctx))
    t_all = time.time() - t0
    print(f'engine {t_eng:.1f}s, tổng {t_all:.1f}s', flush=True)

    thin = st['thin'].to_numpy()
    sid = st['session_id']
    tr = [s for s in st.index if 1 <= s < N_TRAIN_SESS and not thin[s]]
    te = [s for s in st.index if s >= N_TRAIN_SESS and not thin[s]]
    kc = cands['kind'].value_counts()
    am = run['alive_mean']
    er, eb = cands.attrs['e_raw'], cands.attrs['e_born']
    md = ['# Vùng Canh Lệnh — kết quả vòng 2', '',
          f'Dữ liệu như vòng 1: `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h` ({len(ctx["df"])} nến M1, {len(st)} phiên, UTC). Gộp 1,0u.',
          f'**TRAIN đo {len(tr)} phiên** ({sid.iloc[tr[0]]} → {sid.iloc[tr[-1]]}; {sid.iloc[0]} chỉ khởi động), '
          f'**TEST đo {len(te)} phiên** ({sid.iloc[te[0]]} → {sid.iloc[te[-1]]}; bỏ mẩu {sid.iloc[-1]}).',
          '**Đối chứng (mới, dùng cho mọi bảng trừ khi ghi khác):** với mỗi lần một vùng thật xuất hiện cách giá đóng d (cạnh gần, theo u, '
          'phía trên/dưới), tạo 50 vùng giả cùng độ rộng, cùng thời gian hiển thị, đặt cạnh gần ở khoảng cách d\' bốc ngẫu nhiên từ phân phối d '
          'của MỌI vùng thật cùng phía và cùng TRAIN/TEST (không dùng chính d của nó). Vùng giả đi theo đúng chuyển động biên của vùng thật.',
          'Không tham số nào chọn bằng TEST: mọi tham số lấy từ PLAN + review vòng 2 của Fable.',
          f'Thời gian chạy `vcl2.py`: {t_all:.0f} giây (engine v2 {t_eng:.0f}s; còn lại = đo 2 kiểu đối chứng + chạy lại engine v1 để so).', '']
    md += ['### Trước (v1) / sau (v2) — 3 chỉ số vệ sinh ở mục A', '',
           '| Chỉ số | mục tiêu | v1 TRAIN | v1 TEST | v2 TRAIN | v2 TEST |', '|---|---|---|---|---|---|',
           f"| % nến đóng trong vùng hiển thị | ≤ 25% | {_p(v1h['TRAIN']['inside'])} | {_p(v1h['TEST']['inside'])} | {_p(hy['TRAIN']['inside'])} | {_p(hy['TEST']['inside'])} |",
           f"| số vùng sống trong ±10u | ≤ 8 | {v1h['TRAIN']['z10']:.1f} | {v1h['TEST']['z10']:.1f} | {hy['TRAIN']['z10']:.1f} | {hy['TEST']['z10']:.1f} |",
           f"| đổi vùng / giờ | ≤ 4 | {v1h['TRAIN']['chg']:.1f} | {v1h['TEST']['chg']:.1f} | {hy['TRAIN']['chg_per_h']:.1f} | {hy['TEST']['chg_per_h']:.1f} |",
           f"| (tham khảo) % nến đóng trong BẤT KỲ vùng sống nào | – | – | – | {_p(hy['TRAIN']['inside_any'])} | {_p(hy['TEST']['inside_any'])} |",
           '']
    md += tab_magnet(mag)
    md += tab_bounce(ev)
    md += tab_pen(ev)
    md += tab_tp(ev)
    md += tab_hyg(hy)
    md += tab_contrib(ev)
    # so 2 kiểu đối chứng
    md += ['### So 2 kiểu đối chứng (mọi vùng hiển thị)', '',
           '| Tách | bật % thật | giả khớp khoảng cách (hiệu) | giả cũ: biên phiên trước (hiệu) | TP % thật | TP % giả khớp k/c | TP % giả cũ |',
           '|---|---|---|---|---|---|---|']
    for sp in ('TRAIN', 'TEST'):
        R = ev[(ev['rep'] == -1) & ev['bounce'].notna() & (ev['split'] == sp)]
        G = ev[(ev['rep'] >= 0) & ev['bounce'].notna() & (ev['split'] == sp)]
        G2 = ev_old[(ev_old['rep'] >= 0) & ev_old['bounce'].notna() & (ev_old['split'] == sp)]
        a, b, d = cmp_cell(R['bounce'], G['bounce'])
        _, b2, d2 = cmp_cell(R['bounce'], G2['bounce'])
        tpr = lambda X: _p((X[(X['bounce'] == 1) & X['tp_res'].notna()]['tp_res'] == 1).mean())
        md.append(f"| {sp} | {a} | {b} ({d}) | {b2} ({d2}) | {tpr(R)} | {tpr(G)} | {tpr(G2)} |")
    md.append('')
    md += ['### Ứng viên v2', '', '| Loại | số sinh ra cả file | sống TB mỗi nến |', '|---|---|---|',
           f"| B swing M5 k=5 | {int(kc.get(1, 0))} | {am['B']:.1f} |",
           f"| B15 swing M15 k=3 | {int(kc.get(6, 0))} | {am['B15']:.1f} |",
           f"| C mốc phiên (+POC trần) | {int(kc.get(2, 0))} (+{int(kc.get(3, 0))}) | {am['C']:.1f} |",
           f"| D số tròn | sinh động | {am['D']:.1f} |",
           f"| E top-5 chạy | {int(kc.get(5, 0))} (đủ điều kiện thô TB {np.mean(list(er.values())):.0f}/phiên; sinh ra TB {np.mean(list(eb.values())):.1f}/phiên, "
           f"max {max(eb.values())}) | {am['E']:.1f} |",
           f"| F đỉnh/đáy bằng nhau | {int(kc.get(7, 0))} | {am['F']:.1f} |",
           f"| (số lần tính lại bộ vùng) | {run['n_recalc']} | |", '']
    md += ['<!-- NHAN-XET -->', '']
    path = os.path.join(REPORT, 'VCL-VONG-2.md')
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    tail = old.split('<!-- NHAN-XET -->', 1)[1] if '<!-- NHAN-XET -->' in old else '\n## Nhận xét\n(chưa viết)\n'
    open(path, 'w', encoding='utf-8').write('\n'.join(md[:-2]) + '\n<!-- NHAN-XET -->' + tail)
    print('\n'.join(md))
    print(f'TỔNG THỜI GIAN: {t_all:.1f}s')


if __name__ == '__main__':
    main()
