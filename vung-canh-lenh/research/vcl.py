# -*- coding: utf-8 -*-
"""
VÙNG CANH LỆNH (VCL) — vòng 1: thuật toán + 5 phép đo (xem ../PLAN.md mục 2, 3, 4).

Nguyên tắc cứng: KHÔNG NHÌN TRƯỚC. Vùng hiển thị sau khi nến i đóng chỉ dùng nến <= i
(test_vcl.py chứng minh: cắt dữ liệu tại i, vùng tại i không đổi).

Chạy:  python3 vcl.py   → report/VCL-VONG-1.md  (+ report/vcl_records_<link>.npz cho ve_vcl.py)
"""
import os, sys, time, math
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'benzo-trader', 'research'))
import kernel as K  # noqa: E402

BASE = os.path.join(ROOT, 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260816-20260915_29d2h')
REPORT = os.path.join(HERE, 'report')

SESS = 1380                 # nến M1 / phiên
N_TRAIN_SESS = 14           # TRAIN = 14 phiên đầu (session_no 0..13), TEST = còn lại
LINKS = (0.7, 1.0, 1.5)     # ngưỡng gộp single-linkage (×u)
MAIN_LINK = 1.0
REPS = 50                   # số lần lặp vùng giả
SEED = 7

P = dict(pad=0.5, wmin=1.0, wmax=4.0,             # đệm, kẹp độ rộng vùng (×u)
         touch_k=0.3, touch_cap=5,                 # điểm ×(1+0,3×min(chạm,5))
         flip_mult=0.7, break_u=1.0,               # đóng xuyên cả vùng ≥1u ⇒ chuyển vai ×0,7; 2 lần ⇒ chết
         e_q=0.99, e_imb=0.6, e_lookback=3, e_cross_u=2.0,
         near_n=2, far_lo_u=2.0, far_range_k=1.5, flicker_k=1.2,
         d_window=40.0, swing_k_m1=5, swing_k_m5=3,
         chung_max=120, tp_max=240, sl_pad=0.5)

# loại ứng viên: kind -> (chữ loại, trọng số)
KINDS = {0: 'A', 1: 'B', 2: 'C', 3: 'C', 4: 'D', 5: 'E'}     # 3 = POC trần (loại C, trọng số 3)
TYPES = 'ABCDE'
BIT = {t: 1 << k for k, t in enumerate(TYPES)}
INF = np.iinfo(np.int64).max // 2


# ---------------------------------------------------------------------------------------------
# 1. DỮ LIỆU
# ---------------------------------------------------------------------------------------------
def prepare(raw_bars: pd.DataFrame, raw_levels: pd.DataFrame) -> dict:
    """Từ dữ liệu THÔ (có thể đã cắt) dựng mọi thứ engine cần. Không dùng gì ngoài dữ liệu đưa vào."""
    df = K._enrich(raw_bars.sort_values('datetime'))
    sno = df['session_no'].to_numpy()
    df['split'] = np.where(sno < N_TRAIN_SESS, 'TRAIN', 'TEST')      # ghi đè split ngày của kernel
    lv = raw_levels[raw_levels['bar_idx'] <= df['bar_idx'].max()]
    prof = K.build_profiles(df, lv[['bar_idx', 'price', 'volume']])
    return dict(df=df, lv=lv, prof=prof, st=K.session_table(df))


def load_all():
    bars = pd.read_csv(BASE + '_bars.csv', parse_dates=['datetime'])
    lv = pd.read_csv(BASE + '.csv', usecols=['bar_idx', 'price', 'volume', 'delta'])
    return bars, lv


# ---------------------------------------------------------------------------------------------
# 2. ỨNG VIÊN (trừ D: sinh động trong engine)
# ---------------------------------------------------------------------------------------------
def gen_candidates(ctx: dict) -> pd.DataFrame:
    """Trả bảng ứng viên: price, kind, w, birth (nến được phép dùng từ khi đóng), death, half (mốc ×0,5)."""
    df, st, prof = ctx['df'], ctx['st'], ctx['prof']
    H, L, C = df['high'].to_numpy(float), df['low'].to_numpy(float), df['close'].to_numpy(float)
    n = len(df)
    rows = []

    def add(price, kind, w, birth, death, half=INF):
        if birth < n:
            rows.append((float(price), kind, float(w), int(birth), int(death), int(half)))

    # A. swing M1 k=5: đỉnh/đáy cao/thấp nhất k nến mỗi bên, xác nhận khi nến i+k đóng; sống 2 phiên
    k = P['swing_k_m1']
    for i in range(k, n - k):
        if H[i] == H[i - k:i + k + 1].max() and (H[i - k:i] < H[i]).all():
            add(H[i], 0, 1, i + k, i + k + 2 * SESS)
        if L[i] == L[i - k:i + k + 1].min() and (L[i - k:i] > L[i]).all():
            add(L[i], 0, 1, i + k, i + k + 2 * SESS)

    # B. swing M5 k=3 từ nến M5 gộp; nến M5 chỉ "đóng" theo đồng hồ (không biết trước nến M1 sau)
    m5 = K.m5_bars(df)
    t1 = df['t_utc'].to_numpy()
    lp = m5['last_pos'].to_numpy()
    closed_now = (t1[lp] + np.timedelta64(1, 'm')) >= m5['t5_end'].to_numpy()
    avail = np.where(closed_now, lp, lp + 1)              # chưa hết 5 phút ⇒ chỉ biết đóng khi nến M1 kế tiếp tới
    h5, l5 = m5['high'].to_numpy(float), m5['low'].to_numpy(float)
    k5 = P['swing_k_m5']
    for j in range(k5, len(m5) - k5):
        b = avail[j + k5]
        if h5[j] == h5[j - k5:j + k5 + 1].max() and (h5[j - k5:j] < h5[j]).all():
            add(h5[j], 1, 2, b, b + 4 * SESS, b + 2 * SESS)
        if l5[j] == l5[j - k5:j + k5 + 1].min() and (l5[j - k5:j] > l5[j]).all():
            add(l5[j], 1, 2, b, b + 4 * SESS, b + 2 * SESS)

    # C. mốc phiên
    kctx = K._Ctx(df, prof)
    sm = df['sm'].to_numpy()
    for s in st.index:
        a, e = int(st.loc[s, 'start_pos']), int(st.loc[s, 'end_pos'])
        if s >= 1:
            pa, pe = int(st.loc[s - 1, 'start_pos']), int(st.loc[s - 1, 'end_pos'])
            for v in (H[pa:pe + 1].max(), L[pa:pe + 1].min(), C[pe]):      # đỉnh/đáy/đóng phiên trước
                add(v, 2, 2, a, a + SESS)
        z = K._zones(kctx, int(s), None, naked=True)
        if z['yday']:
            for key in ('vah', 'val', 'poc'):
                add(z['yday'][key], 2, 2, a, a + SESS)
        # POC trần: chưa bị chạm trước đầu phiên, giữ 3 cái gần nhất; chết khi bị chạm (touch_pos)
        nk = [x for x in (z['naked'] or []) if x['touch_pos'] is None or x['touch_pos'] >= a][-3:]
        for x in nk:
            add(x['price'], 3, 3, a, x['touch_pos'] if x['touch_pos'] is not None else INF)
        # biên Á (sm < 450): chốt khi có nến sm >= 450
        sms = sm[a:e + 1]
        asia = np.flatnonzero(sms < K.CONST['sm_eu_start'])
        rd = np.flatnonzero(sms >= K.CONST['sm_eu_start'])
        if len(asia) >= 60 and len(rd):
            b = a + int(rd[0])
            add(H[a + asia].max(), 2, 2, b, b + SESS)
            add(L[a + asia].min(), 2, 2, b, b + SESS)
        # VA Âu sau khi chốt (19:00 VN)
        if z['va_eu']:
            b = int(z['va_eu']['ready_pos'])
            add(z['va_eu']['vah'], 2, 2, b, b + SESS)
            add(z['va_eu']['val'], 2, 2, b, b + SESS)

    # E. mức lệnh lớn từ footprint: volume >= p99 của mức-giá trong 3 phiên trước VÀ |delta|/volume >= 0,6
    lv = ctx['lv']
    pos_of = pd.Index(df['bar_idx'].to_numpy())
    lpos = pos_of.get_indexer(lv['bar_idx'].to_numpy())
    ok = lpos >= 0
    lpos = lpos[ok]
    lvol = lv['volume'].to_numpy(float)[ok]
    ldel = lv['delta'].to_numpy(float)[ok]
    lpr = lv['price'].to_numpy(float)[ok]
    lses = df['session_no'].to_numpy()[lpos]
    e_count = {}
    for s in st.index:
        prev = (lses >= s - P['e_lookback']) & (lses <= s - 1)
        if not prev.any():
            continue
        thr = np.quantile(lvol[prev], P['e_q'])
        m = (lses == s) & (lvol >= thr) & (np.abs(ldel) >= P['e_imb'] * np.maximum(lvol, 1))
        e_count[int(s)] = int(m.sum())
        for b, pr in zip(lpos[m], lpr[m]):
            add(pr, 5, 2, b, b + 4 * SESS, b + 2 * SESS)

    cd = pd.DataFrame(rows, columns=['price', 'kind', 'w', 'birth', 'death', 'half'])
    cd = cd.sort_values('birth', kind='stable').reset_index(drop=True)
    cd.attrs['e_count'] = e_count
    return cd


# ---------------------------------------------------------------------------------------------
# 3. GỘP THÀNH VÙNG
# ---------------------------------------------------------------------------------------------
def _split(ps, a, b, u, out):
    """Tách cụm [a,b) tại khe lớn nhất cho tới khi độ rộng (đã đệm) <= wmax·u."""
    if b - a <= 1 or ps[b - 1] - ps[a] + 2 * P['pad'] * u <= P['wmax'] * u:
        out.append((a, b))
        return
    g = a + 1 + int(np.argmax(np.diff(ps[a:b])))
    _split(ps, a, g, u, out)
    _split(ps, g, b, u, out)


def build_zones(p, u, link):
    """Gộp đơn liên kết theo khoảng cách <= link·u; biên = min/max ± 0,5u; kẹp độ rộng [1u, 4u].
    Trả (lab: chỉ số vùng của từng ứng viên, lo, hi) — vùng sắp tăng theo giá."""
    n = len(p)
    if n == 0:
        return np.zeros(0, int), np.zeros(0), np.zeros(0)
    o = np.argsort(p, kind='stable')
    ps = p[o]
    brk = np.flatnonzero(np.diff(ps) > link * u) + 1
    st, en = np.r_[0, brk], np.r_[brk, n]
    big = (ps[en - 1] - ps[st]) + 2 * P['pad'] * u > P['wmax'] * u
    if big.any():
        pieces = []
        for a, b, bg in zip(st, en, big):
            if bg:
                _split(ps, a, b, u, pieces)
            else:
                pieces.append((a, b))
        st = np.array([x[0] for x in pieces])
        en = np.array([x[1] for x in pieces])
    lo = ps[st] - P['pad'] * u
    hi = ps[en - 1] + P['pad'] * u
    short = (hi - lo) < P['wmin'] * u
    if short.any():
        c = (lo + hi) / 2
        lo = np.where(short, c - P['wmin'] * u / 2, lo)
        hi = np.where(short, c + P['wmin'] * u / 2, hi)
    if len(lo) > 1:                                   # chồng lấn ⇒ cắt ở giữa
        ov = hi[:-1] > lo[1:]
        if ov.any():
            mid = (hi[:-1] + lo[1:]) / 2
            h2, l2 = hi.copy(), lo.copy()
            h2[:-1][ov] = mid[ov]
            l2[1:][ov] = mid[ov]
            hi, lo = h2, l2
    lab_s = np.repeat(np.arange(len(st)), en - st)
    lab = np.empty(n, int)
    lab[o] = lab_s
    return lab, lo, hi


def break_update(side, breaks, close, zlo, zhi, u):
    """Chuyển vai (vector): side +1 = giá ở trên (hỗ trợ), -1 = giá ở dưới (kháng cự), 0 = chưa rõ.
    Đóng xuyên qua CẢ vùng >= 1u ⇒ breaks+1, đổi vai. Trả (side_mới, breaks_mới, bị_xuyên)."""
    side = side.copy()
    breaks = breaks.copy()
    z0 = side == 0
    side[z0 & (close > zhi)] = 1
    side[z0 & (close < zlo)] = -1
    brk = ((side == 1) & (close < zlo - P['break_u'] * u)) | ((side == -1) & (close > zhi + P['break_u'] * u))
    breaks[brk] += 1
    side[brk] = -side[brk]
    return side, breaks, brk


# ---------------------------------------------------------------------------------------------
# 4. CHỌN VÙNG HIỂN THỊ (2 gần + 1 xa vừa phải mỗi phía, chống nhấp nháy)
# ---------------------------------------------------------------------------------------------
def select_display(lo, hi, score, c, u, maxd, prev):
    """prev = [(lo, hi, eid, slot)] vùng hiển thị ở nến trước. Trả [(chỉ_số_vùng, slot, eid_cũ|None, side)]."""
    nz = len(lo)
    if nz == 0:
        return []
    zmap = {}
    for plo, phi, eid, slot in prev:                     # khớp vùng cũ ↔ vùng hiện tại theo độ chồng lấn
        ov = np.minimum(phi, hi) - np.maximum(plo, lo)
        j = int(np.argmax(ov))
        if ov[j] > 0 and (j not in zmap or ov[j] > zmap[j][2]):
            zmap[j] = (eid, slot, ov[j])
    above = (lo + hi) / 2 > c
    out = []
    for side in (1, -1):
        idx = np.flatnonzero(above if side > 0 else ~above)
        if len(idx) == 0:
            continue
        d = np.maximum((lo[idx] - c) if side > 0 else (c - hi[idx]), 0.0)
        dist = dict(zip(idx.tolist(), d.tolist()))
        order = idx[np.argsort(d, kind='stable')].tolist()
        near_t = order[:P['near_n']]
        chosen = [z for z in near_t if z in zmap]
        news = [z for z in near_t if z not in zmap]
        olds = sorted([z for z in idx.tolist() if z in zmap and zmap[z][1] == 'N' and z not in near_t],
                      key=lambda z: score[z])
        for _ in range(P['near_n'] - len(chosen)):
            if news and olds:
                if score[news[0]] > P['flicker_k'] * score[olds[0]]:
                    chosen.append(news.pop(0))
                else:
                    chosen.append(olds.pop(0))
            elif news:
                chosen.append(news.pop(0))
            elif olds:
                chosen.append(olds.pop(0))
        pool = [z for z in idx.tolist() if z not in chosen and P['far_lo_u'] * u <= dist[z] <= maxd]
        far_t = max(pool, key=lambda z: score[z]) if pool else None
        prev_far = [z for z in idx.tolist() if z in zmap and zmap[z][1] == 'F' and z not in chosen]
        far = None
        if far_t is not None and far_t in zmap:
            far = far_t
        elif prev_far:
            o = max(prev_far, key=lambda z: score[z])
            if far_t is not None and (score[far_t] > P['flicker_k'] * score[o] or dist[o] > maxd):
                far = far_t
            elif dist[o] <= maxd:
                far = o
            else:
                far = far_t
        else:
            far = far_t
        for z in chosen:
            out.append((z, 'N', zmap[z][0] if z in zmap else None, side))
        if far is not None:
            out.append((far, 'F', zmap[far][0] if far in zmap else None, side))
    return out


# ---------------------------------------------------------------------------------------------
# 5. ENGINE: chạy từng nến
# ---------------------------------------------------------------------------------------------
REC_COLS = ['bar', 'lo', 'hi', 'score', 'mask', 'conf', 'ncand', 'eid', 'side', 'slot']


def run_engine(ctx: dict, link: float, cands: pd.DataFrame = None, stop: int = None):
    """Trả dict: rec (DataFrame vùng hiển thị theo nến), stats (số ứng viên sống trung bình theo loại)."""
    df = ctx['df']
    cands = gen_candidates(ctx) if cands is None else cands
    H, L, C = df['high'].to_numpy(float), df['low'].to_numpy(float), df['close'].to_numpy(float)
    u_all = K.median_range(df).to_numpy()
    sno = df['session_no'].to_numpy()
    st = ctx['st']
    n = len(df) if stop is None else min(len(df), stop + 1)
    # biên độ phiên trước (để chọn vùng xa vừa phải)
    srange = {int(s): H[int(r.start_pos):int(r.end_pos) + 1].max() - L[int(r.start_pos):int(r.end_pos) + 1].min()
              for s, r in st.iterrows()}
    s_start = st['start_pos'].to_dict()

    cap = len(cands) + 400
    price = np.zeros(cap); kind = np.zeros(cap, int); w = np.zeros(cap); birth = np.zeros(cap, np.int64)
    death = np.zeros(cap, np.int64); half = np.zeros(cap, np.int64)
    side = np.zeros(cap, int); breaks = np.zeros(cap, int); touch = np.zeros(cap, int); alive = np.zeros(cap, bool)
    cp, ck, cw = cands['price'].to_numpy(), cands['kind'].to_numpy(), cands['w'].to_numpy()
    cb, cde, cha = cands['birth'].to_numpy(), cands['death'].to_numpy(), cands['half'].to_numpy()
    m = 0          # số ứng viên đã nạp
    ptr = 0
    d_have = set()
    tbit_of = np.array([BIT[KINDS[k]] for k in range(6)])
    recs = []
    prev = []
    next_eid = 0
    alive_cnt = np.zeros(6)
    n_alive_bars = 0
    nz_sum = 0.0
    cov_sum = 0.0
    z10_sum = 0
    z10_bar = np.full(len(df), np.nan)

    def init_side(j, i):
        dd = C[i] - price[j]
        uu = u_all[i] if u_all[i] == u_all[i] else 1.0
        side[j] = 0 if abs(dd) < 0.5 * uu else (1 if dd > 0 else -1)

    for i in range(n):
        # nạp ứng viên sinh tại i
        while ptr < len(cands) and cb[ptr] <= i:
            price[m], kind[m], w[m], birth[m], death[m], half[m] = cp[ptr], ck[ptr], cw[ptr], cb[ptr], cde[ptr], cha[ptr]
            alive[m] = True
            init_side(m, i)
            m += 1
            ptr += 1
        # D: số tròn bội 10 trong close ± 40, sinh khi lần đầu lọt cửa sổ, không chết, không suy giảm
        for v in range(int(math.ceil((C[i] - P['d_window']) / 10.0)) * 10, int(C[i] + P['d_window']) + 1, 10):
            if v not in d_have:
                d_have.add(v)
                if m >= cap:
                    raise RuntimeError('tràn bộ nhớ ứng viên')
                price[m], kind[m], birth[m], death[m], half[m] = v, 4, i, INF, INF
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
        lab, zlo, zhi = build_zones(price[act], u, link)
        # --- cập nhật chạm / chuyển vai / E bị xuyên
        if i > 0 and sno[i] == sno[i - 1] and len(act):
            ent = (C[i] >= zlo) & (C[i] <= zhi) & ((C[i - 1] < zlo) | (C[i - 1] > zhi))
            touch[act[ent[lab]]] += 1
        kk = kind[act]
        abc = act[(kk <= 3)]
        if len(abc):
            la = lab[kk <= 3]
            s2, b2, _ = break_update(side[abc], breaks[abc], C[i], zlo[la], zhi[la], u)
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
        # --- dựng lại vùng sau khi loại ứng viên chết
        act = np.flatnonzero(alive[:m])
        np.add.at(alive_cnt, kind[act], 1)
        n_alive_bars += 1
        lab, zlo, zhi = build_zones(price[act], u, link)
        nz = len(zlo)
        nz_sum += nz
        z10_bar[i] = int(((zhi >= C[i] - 10 * u) & (zlo <= C[i] + 10 * u)).sum())
        z10_sum += z10_bar[i]   # số vùng sống trong dải ±10u (để so v2)
        a5, b5 = C[i] - 5 * u, C[i] + 5 * u                 # độ phủ: phần của [giá ±5u] nằm trong vùng (mọi vùng, chưa lọc hiển thị)
        cov_sum += np.clip(np.minimum(zhi, b5) - np.maximum(zlo, a5), 0, None).sum() / (10 * u)
        val = w[act] * np.where(i >= half[act], 0.5, 1.0) * (1 + P['touch_k'] * np.minimum(touch[act], P['touch_cap'])) \
            * P['flip_mult'] ** breaks[act]
        score = np.bincount(lab, val, minlength=nz)
        mask = np.zeros(nz, int)
        np.bitwise_or.at(mask, lab, tbit_of[kind[act]])
        ncand = np.bincount(lab, minlength=nz)
        s = int(sno[i])
        if s >= 1:
            pr = srange[s - 1]
        else:
            a = int(s_start[s])
            pr = max(H[a:i + 1].max() - L[a:i + 1].min(), 10 * u)
        sel = select_display(zlo, zhi, score, C[i], u, P['far_range_k'] * pr, prev)
        prev = []
        for z, slot, eid, sd in sel:
            if eid is None:
                eid = next_eid
                next_eid += 1
            conf = bin(int(mask[z])).count('1')
            recs.append((i, zlo[z], zhi[z], score[z], int(mask[z]), conf, int(ncand[z]), eid, sd, slot))
            prev.append((zlo[z], zhi[z], eid, slot))
    rec = pd.DataFrame(recs, columns=REC_COLS)
    stats = dict(alive_mean={t: 0.0 for t in TYPES}, e_count=cands.attrs.get('e_count', {}),
                 zones_mean=nz_sum / max(n_alive_bars, 1), cover5u=cov_sum / max(n_alive_bars, 1),
                 z10_mean=z10_sum / max(n_alive_bars, 1), z10_bar=z10_bar)
    for k_, t in KINDS.items():
        stats['alive_mean'][t] += alive_cnt[k_] / max(n_alive_bars, 1)
    return dict(rec=rec, stats=stats)


# ---------------------------------------------------------------------------------------------
# 6. ĐO
# ---------------------------------------------------------------------------------------------
def measure(ctx: dict, rec: pd.DataFrame, reps: int = REPS, seed: int = SEED):
    """Phát hiện sự kiện trên vùng THẬT (rep=-1) và vùng GIẢ (rep 0..reps-1, mỗi lần hiển thị = 1 vùng dời ngẫu nhiên
    cùng độ rộng, tâm lúc xuất hiện ~ U[đáy phiên trước-2, đỉnh phiên trước+2]). Trả (events DataFrame, hygiene dict)."""
    df, st = ctx['df'], ctx['st']
    H, L, C = df['high'].to_numpy(float), df['low'].to_numpy(float), df['close'].to_numpy(float)
    u_all = K.median_range(df).to_numpy()
    sno = df['session_no'].to_numpy()
    n = len(df)
    s_end = st['end_pos'].to_numpy()
    s_start = st['start_pos'].to_numpy()
    thin = st['thin'].to_numpy()
    meas_sess = np.array([(s >= 1) and not thin[s] for s in range(len(st))])
    rng = np.random.default_rng(seed)

    rec = rec.sort_values(['eid', 'bar']).reset_index(drop=True)
    eids = rec['eid'].to_numpy()
    cut = np.r_[0, np.flatnonzero(np.diff(eids)) + 1, len(eids)]
    n_ep = len(cut) - 1
    # offset mỗi episode × rep
    off = np.zeros((n_ep, reps + 1))
    ep_of_eid = {}
    for e in range(n_ep):
        a = cut[e]
        b0 = int(rec['bar'].iat[a])
        s = int(sno[b0])
        if s >= 1:
            pa, pe = s_start[s - 1], s_end[s - 1]
            plo, phi = L[pa:pe + 1].min(), H[pa:pe + 1].max()
        else:
            plo, phi = L[s_start[s]:b0 + 1].min(), H[s_start[s]:b0 + 1].max()
        c0 = (rec['lo'].iat[a] + rec['hi'].iat[a]) / 2
        off[e, 1:] = rng.uniform(plo - 2, phi + 2, reps) - c0
        ep_of_eid[int(eids[a])] = e
    # tra cứu vùng hiển thị theo nến (cho TP)
    rb = rec.sort_values('bar', kind='stable')
    rb_bar = rb['bar'].to_numpy()
    rb_lo, rb_hi = rb['lo'].to_numpy(), rb['hi'].to_numpy()
    rb_ep = np.array([ep_of_eid[int(x)] for x in rb['eid'].to_numpy()])
    bstart = np.searchsorted(rb_bar, np.arange(n + 1))

    lo_all, hi_all = rec['lo'].to_numpy(), rec['hi'].to_numpy()
    bar_all, mask_all, conf_all = rec['bar'].to_numpy(), rec['mask'].to_numpy(), rec['conf'].to_numpy()
    events = []
    for e in range(n_ep):
        a, b = cut[e], cut[e + 1]
        bars = bar_all[a:b]
        # nến vào dải = bars+1, cùng phiên, phiên được đo
        nb = bars + 1
        okb = (nb < n)
        nb_c = np.minimum(nb, n - 1)
        okb &= (sno[nb_c] == sno[bars]) & meas_sess[sno[nb_c]]
        if not okb.any():
            continue
        lo_e, hi_e = lo_all[a:b], hi_all[a:b]
        for r in range(reps + 1):
            o = off[e, r]
            zl, zh = lo_e + o, hi_e + o
            pc, cc = C[bars], C[nb_c]
            inside = (cc >= zl) & (cc <= zh)
            frm = np.where(pc > zh, 1, np.where(pc < zl, -1, 0))
            cand = np.flatnonzero(okb & inside & (frm != 0))
            last_exit = -1
            for t in cand:
                i = int(nb[t])
                if i <= last_exit:
                    continue
                hit = int(frm[t]); l0, h0 = float(zl[t]), float(zh[t]); ui = float(u_all[i])
                lim = min(i + P['chung_max'], int(s_end[sno[i]]) + 1, n)
                seg = C[i + 1:lim]
                outu = seg > h0
                outd = seg < l0
                anyo = outu | outd
                if not anyo.any():
                    events.append((r - 1, e, i, -1, hit, np.nan, l0, h0, ui, int(mask_all[a + t]), int(conf_all[a + t]),
                                   np.nan, np.nan, np.nan, np.nan, np.nan, np.nan))
                    last_exit = lim - 1
                    continue
                q = int(np.argmax(anyo))
                k = i + 1 + q
                bounce = int((outu[q] and hit == 1) or (outd[q] and hit == -1))
                last_exit = k
                pen = tpd = tpres = rplan = rreal = ttp = np.nan
                if bounce:
                    if hit == 1:
                        pen = max(0.0, l0 - L[i:k + 1].min()) / ui
                    else:
                        pen = max(0.0, H[i:k + 1].max() - h0) / ui
                    # TP = cạnh gần vùng hiển thị kế tiếp cùng hướng (bộ vùng cùng rep tại nến k)
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
                            if hit == 1:
                                slh, tph = ll <= sl, hh >= tp
                            else:
                                slh, tph = hh >= sl, ll <= tp
                            fs = int(np.argmax(slh)) if slh.any() else 10 ** 9
                            ft = int(np.argmax(tph)) if tph.any() else 10 ** 9
                            if fs == ft == 10 ** 9:
                                tpres = 0.5          # hết giờ
                                endp = C[lim2 - 1] if lim2 - 1 > k else ent
                                rreal = (endp - ent) * hit / risk
                            elif ft < fs:
                                tpres, rreal, ttp = 1.0, rplan, ft + 1
                            else:
                                tpres, rreal = 0.0, -1.0
                events.append((r - 1, e, i, k, hit, bounce, l0, h0, ui, int(mask_all[a + t]), int(conf_all[a + t]),
                               pen, tpd, tpres, rplan, rreal, ttp))
    ev = pd.DataFrame(events, columns=['rep', 'ep', 'i', 'k', 'hit', 'bounce', 'lo', 'hi', 'u', 'mask', 'conf',
                                       'pen', 'tp_u', 'tp_res', 'r_plan', 'r_real', 't_tp'])
    ev['split'] = np.where(sno[ev['i'].to_numpy()] < N_TRAIN_SESS, 'TRAIN', 'TEST')

    # ---- vệ sinh chart (mục 4)
    hy = {}
    for sp in ('TRAIN', 'TEST'):
        bm = meas_sess[sno] & ((sno < N_TRAIN_SESS) == (sp == 'TRAIN')) & ~np.isnan(u_all)
        bars_ok = np.flatnonzero(bm)
        cnt = np.bincount(rb_bar, minlength=n)[bars_ok]
        rr = rb[np.isin(rb_bar, bars_ok)]
        wid = (rr['hi'] - rr['lo']).to_numpy()
        widu = wid / u_all[rr['bar'].to_numpy()]
        # trong vùng: close[i] nằm trong vùng hiển thị ở nến i-1 (thật và giả)
        prv = bars_ok[bars_ok >= 1] - 1
        ins_real = np.zeros(len(prv), bool)
        ins_ctrl = np.zeros((len(prv), reps), bool)
        pidx = {b: t for t, b in enumerate(prv)}
        for j in range(len(rb_bar)):
            t = pidx.get(rb_bar[j])
            if t is None:
                continue
            cc = C[rb_bar[j] + 1]
            if rb_lo[j] <= cc <= rb_hi[j]:
                ins_real[t] = True
            oo = off[rb_ep[j], 1:]
            ins_ctrl[t] |= (cc >= rb_lo[j] + oo) & (cc <= rb_hi[j] + oo)
        # đổi vùng/giờ: số eid mới xuất hiện
        firsts = rec.groupby('eid')['bar'].min().to_numpy()
        new_cnt = np.isin(firsts, bars_ok).sum()
        up = rb[(rb['side'] == 1) & np.isin(rb_bar, bars_ok)].groupby('bar').size().reindex(bars_ok, fill_value=0).to_numpy()
        dn = rb[(rb['side'] == -1) & np.isin(rb_bar, bars_ok)].groupby('bar').size().reindex(bars_ok, fill_value=0).to_numpy()
        hy[sp] = dict(n_bars=len(bars_ok), n_sess=int(len(np.unique(sno[bars_ok]))), mean_cnt=cnt.mean(),
                      med_w_u=np.median(widu), med_w_usd=np.median(wid), p90_w_u=np.quantile(widu, .9),
                      inside=ins_real.mean(), inside_ctrl=ins_ctrl.mean(),
                      chg_per_h=new_cnt / (len(bars_ok) / 60.0),
                      both1=((up >= 1) & (dn >= 1)).mean(), both3=((up >= 3) & (dn >= 3)).mean())
    return ev, hy


# ---------------------------------------------------------------------------------------------
# 7. BẢNG
# ---------------------------------------------------------------------------------------------
def _p(x):
    return f'{100 * x:.1f}' if x == x else '–'


def rate(v):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return np.nan, np.nan, 0
    p = v.mean()
    return p, math.sqrt(p * (1 - p) / len(v)), len(v)


def cmp_cell(real, ctrl):
    """'bật% ±se (n) | giả% | hiệu ±'"""
    p, se, nn = rate(real)
    q, sq, nq = rate(ctrl)
    if nn == 0:
        return '– (n=0)', '–', '–'
    d = p - q
    sd = math.sqrt(se ** 2 + (sq if sq == sq else 0) ** 2)
    flag = ' ≈' if abs(d) <= 2 * sd else (' ▲' if d > 0 else ' ▼')
    return f'{_p(p)} ±{_p(se)} (n={nn})', f'{_p(q)}', f'{100 * d:+.1f} ±{100 * sd:.1f}{flag}'


def has(ev, t):
    return (ev['mask'].to_numpy() & BIT[t]) > 0


def tables(ev, hy, link):
    md = []
    R = ev[ev['rep'] == -1]
    G = ev[ev['rep'] >= 0]
    Rb, Gb = R[R['bounce'].notna()], G[G['bounce'].notna()]
    # ---- 1. bật/xuyên
    md += [f'### 1. Bật / xuyên (Chung&Bellotti, vào dải bằng giá đóng) — gộp {link}u', '',
           '| Nhóm vùng | TRAIN bật % ±se (n) | giả % | hiệu | TEST bật % ±se (n) | giả % | hiệu |', '|---|---|---|---|---|---|---|']
    groups = [('Mọi vùng hiển thị', lambda d: np.ones(len(d), bool))]
    groups += [(f'Có loại {t}', (lambda t: lambda d: has(d, t))(t)) for t in TYPES]
    groups += [('Hợp lưu 1 loại', lambda d: d['conf'].to_numpy() == 1), ('Hợp lưu 2 loại', lambda d: d['conf'].to_numpy() == 2),
               ('Hợp lưu ≥3 loại', lambda d: d['conf'].to_numpy() >= 3)]
    for name, f in groups:
        row = [name]
        for sp in ('TRAIN', 'TEST'):
            r, g = Rb[Rb['split'] == sp], Gb[Gb['split'] == sp]
            row += cmp_cell(r[f(r)]['bounce'], g[f(g)]['bounce'])
        md.append('| ' + ' | '.join(row) + ' |')
    md += ['', '“giả %” = cùng nhóm nhưng trên vùng giả (50 lần dời ngẫu nhiên). ≈ = |hiệu| ≤ 2 sai số; ▲/▼ = vượt 2 sai số.', '']
    # ---- 2. xâm nhập quá biên xa
    md += ['### 2. Độ rộng vs nhiễu — râu xuyên quá biên xa ở các ca BẬT (đơn vị u)', '',
           '| | n bật | p50 | p85 | p95 | % > 0,5u (SL biên xa+0,5u bị quét) | % = 0 (không chạm biên xa) |', '|---|---|---|---|---|---|---|']
    for sp in ('TRAIN', 'TEST'):
        for lab, d in (('Vùng thật', Rb[(Rb['split'] == sp) & (Rb['bounce'] == 1)]),
                       ('Vùng giả', Gb[(Gb['split'] == sp) & (Gb['bounce'] == 1)])):
            x = d['pen'].to_numpy()
            if len(x) == 0:
                md.append(f'| {sp} · {lab} | 0 | – | – | – | – | – |')
                continue
            q = np.quantile(x, [.5, .85, .95])
            p5, se5, _ = rate(x > 0.5)
            md.append(f'| {sp} · {lab} | {len(x)} | {q[0]:.2f} | {q[1]:.2f} | {q[2]:.2f} | {_p(p5)} ±{_p(se5)} | {_p((x == 0).mean())} |')
    md.append('')
    # ---- 3. TP tới vùng kế tiếp
    md += ['### 3. TP = cạnh gần vùng kế tiếp cùng hướng, SL = biên xa + 0,5u, vào ở giá đóng nến bật, tối đa 240 nến, không phí', '',
           '| Nhóm | Khoảng TP | n thật | TP trước SL % ±se | giả % | R kế hoạch TB (thật/giả) | R thực TB (thật/giả) | phút tới TP (trung vị) |',
           '|---|---|---|---|---|---|---|---|']
    for sp in ('TRAIN', 'TEST'):
        for blab, lo_, hi_ in (('tất cả', -1, 1e9), ('≤3u', -1, 3), ('3–6u', 3, 6), ('>6u', 6, 1e9)):
            r = Rb[(Rb['split'] == sp) & (Rb['bounce'] == 1) & Rb['tp_res'].notna() & (Rb['tp_u'] > lo_) & (Rb['tp_u'] <= hi_)]
            g = Gb[(Gb['split'] == sp) & (Gb['bounce'] == 1) & Gb['tp_res'].notna() & (Gb['tp_u'] > lo_) & (Gb['tp_u'] <= hi_)]
            p, se, nn = rate((r['tp_res'] == 1).astype(float))
            q, _, _ = rate((g['tp_res'] == 1).astype(float))
            md.append(f"| {sp} | {blab} | {nn} | {_p(p)} ±{_p(se)} | {_p(q)} | {r['r_plan'].mean():.2f} / {g['r_plan'].mean():.2f} | "
                      f"{r['r_real'].mean():+.2f} / {g['r_real'].mean():+.2f} | {r['t_tp'].median():.0f} |")
    md += ['', 'R thực: thắng = +R kế hoạch, thua = −1, hết 240 nến = lãi/lỗ tạm theo giá đóng. Ca bật không có vùng kế tiếp cùng hướng thì bỏ.', '']
    return md


def hygiene_table(hys):
    md = ['### 4. Vệ sinh chart', '',
          '| Gộp | Tách | vùng hiển thị TB | độ rộng trung vị (u / USD) | p90 rộng (u) | % nến đóng TRONG vùng (thật / giả) | đổi vùng / giờ | % thời gian có ≥1 vùng cả 2 phía | % đủ 3+3 |',
          '|---|---|---|---|---|---|---|---|---|']
    for link, hy in hys.items():
        for sp in ('TRAIN', 'TEST'):
            h = hy[sp]
            md.append(f"| {link}u | {sp} | {h['mean_cnt']:.2f} | {h['med_w_u']:.2f} / {h['med_w_usd']:.2f} | {h['p90_w_u']:.2f} | "
                      f"{_p(h['inside'])} / {_p(h['inside_ctrl'])} | {h['chg_per_h']:.1f} | {_p(h['both1'])} | {_p(h['both3'])} |")
    md.append('')
    return md


def contrib_table(ev):
    R = ev[(ev['rep'] == -1) & ev['bounce'].notna()]
    G = ev[(ev['rep'] >= 0) & ev['bounce'].notna()]
    md = ['### 5. Đóng góp từng loại ứng viên (gộp 1,0u; vùng có chứa loại đó)', '',
          '| Loại | Tách | n | bật % − giả % | xâm nhập p85 (u) thật / giả | TP % thật / giả | R thực TB thật / giả |', '|---|---|---|---|---|---|---|']
    for t in TYPES:
        for sp in ('TRAIN', 'TEST'):
            r, g = R[(R['split'] == sp) & has(R, t)], G[(G['split'] == sp) & has(G, t)]
            _, _, d = cmp_cell(r['bounce'], g['bounce'])
            rb, gb = r[r['bounce'] == 1], g[g['bounce'] == 1]
            p85r = np.quantile(rb['pen'], .85) if len(rb) else np.nan
            p85g = np.quantile(gb['pen'], .85) if len(gb) else np.nan
            rt, gt = rb[rb['tp_res'].notna()], gb[gb['tp_res'].notna()]
            pr, sr, nr = rate((rt['tp_res'] == 1).astype(float))
            pg, _, _ = rate((gt['tp_res'] == 1).astype(float))
            md.append(f"| {t} | {sp} | {len(r)} | {d} | {p85r:.2f} / {p85g:.2f} | {_p(pr)} ±{_p(sr)} / {_p(pg)} | "
                      f"{rt['r_real'].mean():+.2f} / {gt['r_real'].mean():+.2f} |")
    md.append('')
    return md


def summary_links(evs):
    md = ['### Tóm tắt 3 ngưỡng gộp (mọi vùng hiển thị)', '',
          '| Gộp | Tách | n vào dải | bật % thật / giả (hiệu) | p85 xâm nhập thật / giả | TP % thật / giả | R thực TB thật / giả |', '|---|---|---|---|---|---|---|']
    for link, ev in evs.items():
        R = ev[(ev['rep'] == -1) & ev['bounce'].notna()]
        G = ev[(ev['rep'] >= 0) & ev['bounce'].notna()]
        for sp in ('TRAIN', 'TEST'):
            r, g = R[R['split'] == sp], G[G['split'] == sp]
            a, b, d = cmp_cell(r['bounce'], g['bounce'])
            rb, gb = r[r['bounce'] == 1], g[g['bounce'] == 1]
            rt, gt = rb[rb['tp_res'].notna()], gb[gb['tp_res'].notna()]
            md.append(f"| {link}u | {sp} | {len(r)} | {a.split(' (')[0]} / {b} ({d}) | {np.quantile(rb['pen'], .85):.2f} / "
                      f"{np.quantile(gb['pen'], .85):.2f} | {_p((rt['tp_res'] == 1).mean())} / {_p((gt['tp_res'] == 1).mean())} | "
                      f"{rt['r_real'].mean():+.2f} / {gt['r_real'].mean():+.2f} |")
    md.append('')
    return md


# ---------------------------------------------------------------------------------------------
def main():
    t0 = time.time()
    bars, lv = load_all()
    ctx = prepare(bars, lv)
    st = ctx['st']
    cands = gen_candidates(ctx)
    t_prep = time.time() - t0
    os.makedirs(REPORT, exist_ok=True)
    evs, hys, runs = {}, {}, {}
    for link in LINKS:
        t1 = time.time()
        run = run_engine(ctx, link, cands)
        runs[link] = run
        rec = run['rec']
        rec.to_csv(os.path.join(REPORT, f'vcl_records_{link}.csv.gz'), index=False)
        ev, hy = measure(ctx, rec)
        evs[link], hys[link] = ev, hy
        print(f'gộp {link}u: {len(rec)} dòng vùng, {ev["ep"].nunique()} vùng có sự kiện, {time.time() - t1:.1f}s', flush=True)
    t_all = time.time() - t0

    # ---- report
    thin = st['thin'].to_numpy()
    tr = [s for s in st.index if 1 <= s < N_TRAIN_SESS and not thin[s]]
    te = [s for s in st.index if s >= N_TRAIN_SESS and not thin[s]]
    sid = st['session_id']
    ecount = cands.attrs['e_count']
    e_mean = np.mean([ecount[s] for s in ecount]) if ecount else 0
    cnt_kind = cands['kind'].value_counts().sort_index()
    n_s = len(st)
    am = runs[MAIN_LINK]['stats']['alive_mean']
    md = ['# Vùng Canh Lệnh — kết quả vòng 1', '',
          f'Dữ liệu: `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h` ({len(ctx["df"])} nến M1, {n_s} phiên, giờ UTC). '
          f'u = trung vị biên độ M1 50 nến (trung vị toàn file {np.nanmedian(K.median_range(ctx["df"])):.2f} USD).',
          f'**TRAIN** = 14 phiên đầu ({sid.iloc[0]} → {sid.iloc[13]}); phiên đầu ({sid.iloc[0]}) chỉ để khởi động (chưa có phiên trước) '
          f'⇒ **đo trên {len(tr)} phiên** ({sid.iloc[tr[0]]} → {sid.iloc[tr[-1]]}). '
          f'**TEST** = {len(te)} phiên ({sid.iloc[te[0]]} → {sid.iloc[te[-1]]}); bỏ mẩu cuối {sid.iloc[-1]} ({int(st["n"].iloc[-1])} nến, phiên mỏng).',
          'Không tham số nào được chọn bằng TEST: mọi tham số lấy nguyên từ PLAN (trọng số, đệm 0,5u, kẹp [1u,4u], 2+1 vùng mỗi phía, 1,2×).',
          f'Đối chứng: mỗi lần một vùng xuất hiện trên chart, tạo {REPS} bản sao dời ngẫu nhiên (cùng độ rộng, cùng thời gian hiển thị, '
          'tâm lúc xuất hiện ~ đều trong [đáy phiên trước −2, đỉnh phiên trước +2]); mọi phép đo chạy y hệt trên bản sao.',
          f'Thời gian chạy `vcl.py`: {t_all:.0f} giây (chuẩn bị {t_prep:.0f}s).', '']
    md += summary_links(evs)
    md += tables(evs[MAIN_LINK], hys[MAIN_LINK], MAIN_LINK)
    md += hygiene_table(hys)
    md += contrib_table(evs[MAIN_LINK])
    md += ['### Ứng viên (gộp 1,0u)', '',
           '| Loại | số ứng viên sinh ra cả file | sống trung bình mỗi nến |', '|---|---|---|',
           f"| A swing M1 k=5 | {int(cnt_kind.get(0, 0))} | {am['A']:.0f} |",
           f"| B swing M5 k=3 | {int(cnt_kind.get(1, 0))} | {am['B']:.0f} |",
           f"| C mốc phiên (+POC trần) | {int(cnt_kind.get(2, 0))} (+{int(cnt_kind.get(3, 0))}) | {am['C']:.0f} |",
           f"| D số tròn | sinh động | {am['D']:.0f} |",
           f"| E lệnh lớn footprint | {int(cnt_kind.get(5, 0))} (TB {e_mean:.0f}/phiên, min {min(ecount.values())}, max {max(ecount.values())}) | {am['E']:.0f} |",
           '']
    md += ['| Gộp | tổng số vùng (trước khi lọc hiển thị) TB mỗi nến | % của dải [giá ±5u] bị vùng phủ |', '|---|---|---|']
    for link in LINKS:
        sx = runs[link]['stats']
        md.append(f"| {link}u | {sx['zones_mean']:.0f} | {100 * sx['cover5u']:.0f}% |")
    md.append('')
    md += ['<!-- NHAN-XET -->', '']
    path = os.path.join(REPORT, 'VCL-VONG-1.md')
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    # giữ phần nhận xét viết tay (sau marker) nếu đã có
    tail = old.split('<!-- NHAN-XET -->', 1)[1] if '<!-- NHAN-XET -->' in old else '\n## Nhận xét\n(chưa viết)\n'
    open(path, 'w', encoding='utf-8').write('\n'.join(md[:-2]) + '\n<!-- NHAN-XET -->' + tail)
    print('\n'.join(md))
    print(f'TỔNG THỜI GIAN: {t_all:.1f}s')


if __name__ == '__main__':
    main()
