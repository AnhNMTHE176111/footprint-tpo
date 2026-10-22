# -*- coding: utf-8 -*-
"""
VÙNG CANH LỆNH — VÒNG 3 (chốt thiết kế để port C#). Không tìm lợi thế vị trí nữa (3 lần đo đều ≈ đối chứng).
Indicator = (1) bản đồ MỐC ỔN ĐỊNH ít nhấp nháy + (2) BẢNG TRA khoảng cách → xác suất chạm / bị quét.

Ứng viên: B (swing M5 k=5, w2), B15 (swing M15 k=3, w3, sống 3 phiên), C (mốc phiên w2 + POC trần w3), D (bội 10/50/100 USD, w1/2/3).
Chọn bộ vùng: vùng CHỨA giá (đang kiểm tra) + 2 gần + 1 xa mỗi phía (tối đa 7). Chỉ tính lại khi một vùng hiển thị bị xuyên/chết
hoặc giá đóng ra ngoài HÀNH LANG [cạnh dưới vùng gần-1 phía dưới, cạnh trên vùng gần-1 phía trên].

Chạy: python3 vcl3.py → report/VCL-VONG-3.md (+ report/vcl3_records.csv.gz cho ve_vcl.py --vong 3)
"""
import os, sys, time, math
import numpy as np
import pandas as pd
import vcl as V
import vcl2 as V2

K = V.K
SESS, INF, N_TRAIN_SESS = V.SESS, V.INF, V.N_TRAIN_SESS
REPORT = V.REPORT
LINK = 1.0

P = dict(V2.P)
P.update(keep_bonus=1.5, corridor_fallback_u=4.0, sample_every=5, reach_w=(15, 30, 60, 120), rev_u=2.0, rev_w=30,
         sweep_x=(0.25, 0.5, 1.0), sweep_win=10, min_n=40,
         d_bins=(0, 1, 2, 3, 4, 6, 8, 12))
TYPES = ['B', 'B15', 'C', 'D']
BIT = {t: V2.BIT[t] for t in TYPES}
KIND = {1: 'B', 6: 'B15', 2: 'C', 3: 'C', 4: 'D'}
BREAK_KINDS = (1, 2, 3, 6)
PHASES = (('Á', 0, 450), ('Âu', 450, 840), ('Mỹ', 840, 100000))
BIN_LAB = ['≤1', '1–2', '2–3', '3–4', '4–6', '6–8', '8–12']


def gen_candidates(ctx):
    """Lấy ứng viên v2 và chỉ giữ B, B15, C, POC trần (bỏ E, F). D sinh động trong engine."""
    cd = V2.gen_candidates(ctx)
    cd = cd[cd['kind'].isin([1, 6, 2, 3])].reset_index(drop=True)
    return cd


# ---------------------------------------------------------------------------------------------
# CHỌN BỘ VÙNG THEO HÀNH LANG
# ---------------------------------------------------------------------------------------------
def fresh_select(lo, hi, score, d10, c, u, maxd, keep=frozenset()):
    """Trả [(z, slot, side)]: slot 'K' = vùng chứa giá (side 0), 'N' = 2 gần, 'F' = 1 xa mỗi phía.
    Gần phía trên = vùng có cạnh dưới > cạnh trên vùng chứa giá (hoặc > giá nếu không có). Xa = mạnh nhất trong
    [2u, maxd] tính từ cạnh ngoài vùng gần thứ 2; vùng thuộc keep (đang hiển thị) điểm ×1,5; vùng chỉ có D-10$ chỉ được
    chiếm khe xa khi không còn vùng nào khác."""
    out = []
    cont = np.flatnonzero((lo <= c) & (c <= hi))
    cz = int(cont[0]) if len(cont) else None
    if cz is not None:
        out.append((cz, 'K', 0))
    for side in (1, -1):
        if side > 0:
            ref = hi[cz] if cz is not None else c
            idx = np.flatnonzero(lo > ref)
            idx = idx[np.argsort(lo[idx], kind='stable')]
        else:
            ref = lo[cz] if cz is not None else c
            idx = np.flatnonzero(hi < ref)
            idx = idx[np.argsort(-hi[idx], kind='stable')]
        near = [int(z) for z in idx[:P['near_n']]]
        out += [(z, 'N', side) for z in near]
        outer = (hi[near[-1]] if side > 0 else lo[near[-1]]) if near else ref
        pool = []
        for z in idx[P['near_n']:]:
            d = (lo[z] - outer) if side > 0 else (outer - hi[z])
            if P['far_lo_u'] * u <= d <= maxd:
                pool.append(int(z))
        if pool:
            nd = [z for z in pool if not d10[z]]
            pool = nd if nd else pool
            far = max(pool, key=lambda z: score[z] * (P['keep_bonus'] if z in keep else 1.0))
            out.append((far, 'F', side))
    return out


def corridor_of(sel, lo, hi, anchor, u):
    """Hành lang = [cạnh dưới vùng gần-1 phía dưới, cạnh trên vùng gần-1 phía trên]; thiếu phía nào thì anchor ± 4u."""
    up = [z for z, s, sd in sel if s == 'N' and sd == 1]
    dn = [z for z, s, sd in sel if s == 'N' and sd == -1]
    top = hi[min(up, key=lambda z: lo[z])] if up else anchor + P['corridor_fallback_u'] * u
    bot = lo[max(dn, key=lambda z: hi[z])] if dn else anchor - P['corridor_fallback_u'] * u
    return bot, top


def corridor_update(lo, hi, score, d10, brk_zone, c, u, maxd, prev, anchor):
    """prev = [(lo, hi, eid, slot, side)]; anchor = giá lúc chốt bộ. brk_zone[z] = vùng z có ứng viên vừa bị xuyên ở nến này.
    Tính lại khi: chưa có bộ / vùng hiển thị biến mất hoặc nhập nhau / vùng hiển thị bị xuyên / giá đóng ra ngoài hành lang.
    Trả ([(z, slot, eid|None, side)], anchor, tính_lại?)."""
    js = V2.match_prev(lo, hi, prev)
    trig = (not prev) or any(j < 0 for j in js) or len(set(js)) < len(js)
    if not trig:
        trig = any(brk_zone[j] for j in js)
    if not trig:
        cur = [(j, p[3], p[4]) for p, j in zip(prev, js)]
        bot, top = corridor_of(cur, lo, hi, anchor, u)
        trig = c > top or c < bot
        if not trig:
            return [(j, p[3], p[2], p[4]) for p, j in zip(prev, js)], anchor, False
    emap = {j: p[2] for p, j in zip(prev, js) if j >= 0}
    sel = fresh_select(lo, hi, score, d10, c, u, maxd, keep=frozenset(emap))
    return [(z, s, emap.get(z), sd) for z, s, sd in sel], c, True


# ---------------------------------------------------------------------------------------------
# ENGINE
# ---------------------------------------------------------------------------------------------
REC_COLS = ['bar', 'lo', 'hi', 'score', 'mask', 'conf', 'ncand', 'eid', 'side', 'slot', 'd10']


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
    death = np.zeros(cap, np.int64)
    side = np.zeros(cap, int); breaks = np.zeros(cap, int); touch = np.zeros(cap, int); alive = np.zeros(cap, bool)
    bflag = np.zeros(cap, bool)
    cols = {c_: cands[c_].to_numpy() for c_ in ('price', 'kind', 'w', 'birth', 'death', 'half')}
    tbit_of = np.zeros(8, int)
    for k_, t in KIND.items():
        tbit_of[k_] = BIT[t]
    m = ptr = 0
    d_have = set()
    recs, prev, anchor, next_eid, n_recalc = [], [], 0.0, 0, 0
    z10 = np.full(n, np.nan)
    for i in range(n):
        while ptr < len(cands) and cols['birth'][ptr] <= i:
            price[m], kind[m], w[m] = cols['price'][ptr], cols['kind'][ptr], cols['w'][ptr]
            death[m], half[m] = cols['death'][ptr], cols['half'][ptr]
            alive[m] = True
            dd = C[i] - price[m]
            uu = u_all[i] if u_all[i] == u_all[i] else 1.0
            side[m] = 0 if abs(dd) < 0.5 * uu else (1 if dd > 0 else -1)
            m += 1
            ptr += 1
        for v in range(int(math.ceil((C[i] - P['d_window']) / 10.0)) * 10, int(C[i] + P['d_window']) + 1, 10):
            if v not in d_have:
                d_have.add(v)
                price[m], kind[m], death[m], half[m] = v, 4, INF, INF
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
        bflag[:m] = False
        if len(abc):
            s2, b2, x = V.break_update(side[abc], breaks[abc], C[i], zlo[lab[bm]], zhi[lab[bm]], u)
            side[abc], breaks[abc] = s2, b2
            bflag[abc[x]] = True
            alive[abc[b2 >= 2]] = False
        act = np.flatnonzero(alive[:m])
        lab, zlo, zhi = V.build_zones(price[act], u, link)
        nz = len(zlo)
        z10[i] = int(((zhi >= C[i] - P['z10_u'] * u) & (zlo <= C[i] + P['z10_u'] * u)).sum())
        val = w[act] * np.where(i >= half[act], 0.5, 1.0) * (1 + P['touch_k'] * np.minimum(touch[act], P['touch_cap'])) \
            * P['flip_mult'] ** breaks[act]
        score = np.bincount(lab, val, minlength=nz)
        mask = np.zeros(nz, int)
        np.bitwise_or.at(mask, lab, tbit_of[kind[act]])
        ncand = np.bincount(lab, minlength=nz)
        not_d10 = np.bincount(lab, ~((kind[act] == 4) & (w[act] == 1.0)), minlength=nz)
        d10 = not_d10 == 0
        brk_zone = np.bincount(lab, bflag[act], minlength=nz) > 0
        s = int(sno[i])
        if s >= 1:
            pr = srange[s - 1]
        else:
            a = int(s_start[s])
            pr = max(H[a:i + 1].max() - L[a:i + 1].min(), 10 * u)
        sel, anchor, rc = corridor_update(zlo, zhi, score, d10, brk_zone, C[i], u, P['far_range_k'] * pr, prev, anchor)
        n_recalc += rc
        prev = []
        for z, slot, eid, sd in sel:
            if eid is None:
                eid = next_eid
                next_eid += 1
            recs.append((i, zlo[z], zhi[z], score[z], int(mask[z]), bin(int(mask[z])).count('1'), int(ncand[z]), eid, sd, slot,
                         bool(d10[z])))
            prev.append((zlo[z], zhi[z], eid, slot, sd))
    rec = pd.DataFrame(recs, columns=REC_COLS)
    return dict(rec=rec, z10=z10, n_recalc=n_recalc)


# ---------------------------------------------------------------------------------------------
# ĐO / BẢNG TRA
# ---------------------------------------------------------------------------------------------
def _meas(ctx):
    st = ctx['st']
    thin = st['thin'].to_numpy()
    return np.array([(s >= 1) and not thin[s] for s in range(len(st))])


def phase_of(sm):
    return np.where(sm < 450, 0, np.where(sm < 840, 1, 2))


def reach_samples(ctx, rec):
    """Mẫu bảng tra: mỗi 5 nến, mỗi vùng hiển thị KHÔNG chứa giá; cạnh gần đóng băng; d = khoảng cách giá đóng → cạnh gần (u).
    Chạm = high/low chạm cạnh gần trong W nến sau (chỉ trong phiên). Quay lại = sau lần chạm đầu, trong 30 nến giá đi ngược ≥ 2u."""
    df, st = ctx['df'], ctx['st']
    H, L, C = df['high'].to_numpy(float), df['low'].to_numpy(float), df['close'].to_numpy(float)
    u = K.median_range(df).to_numpy()
    sno, sm = df['session_no'].to_numpy(), df['sm'].to_numpy()
    s_end = st['end_pos'].to_numpy()
    meas = _meas(ctx)
    n = len(df)
    r = rec[(rec['bar'] % P['sample_every'] == 0) & (rec['slot'] != 'K')]
    r = r[meas[sno[r['bar'].to_numpy()]]]
    W = P['reach_w']
    Wmax = max(W)
    out = []
    for b, lo, hi, sd, mk in zip(r['bar'].to_numpy(), r['lo'].to_numpy(), r['hi'].to_numpy(), r['side'].to_numpy(), r['mask'].to_numpy()):
        ne = lo if sd == 1 else hi
        d = (ne - C[b]) * sd / u[b]
        if d < 0 or d > 12:
            continue
        lim = min(b + 1 + Wmax + P['rev_w'], int(s_end[sno[b]]) + 1, n)
        hh, ll = H[b + 1:lim], L[b + 1:lim]
        t = (hh >= ne) if sd == 1 else (ll <= ne)
        tw = t[:Wmax]
        f = int(np.argmax(tw)) if tw.any() else 10 ** 9
        rev = np.nan
        if f < 10 ** 9:
            seg = slice(f + 1, min(f + 1 + P['rev_w'], len(hh)))
            rev = float((ll[seg] <= ne - P['rev_u'] * u[b]).any()) if sd == 1 else float((hh[seg] >= ne + P['rev_u'] * u[b]).any())
        out.append((b, d, int(phase_of(sm[b])), int(mk), *[float(f < w_) for w_ in W], rev,
                    'TRAIN' if sno[b] < N_TRAIN_SESS else 'TEST'))
    return pd.DataFrame(out, columns=['bar', 'd', 'phase', 'mask'] + [f'r{w_}' for w_ in W] + ['rev', 'split'])


def sweep_events(ctx, rec):
    """Giá đóng vào vùng hiển thị (từ ngoài) → trong 10 nến (gồm nến vào) râu vượt BIÊN XA thêm ≥ x·u? Mỗi vùng chỉ đếm lại sau khi
    giá đã đóng ra khỏi vùng."""
    df, st = ctx['df'], ctx['st']
    H, L, C = df['high'].to_numpy(float), df['low'].to_numpy(float), df['close'].to_numpy(float)
    u = K.median_range(df).to_numpy()
    sno, sm = df['session_no'].to_numpy(), df['sm'].to_numpy()
    s_end = st['end_pos'].to_numpy()
    meas = _meas(ctx)
    n = len(df)
    rr, cut = V2.episodes(rec)
    out = []
    bar_a, lo_a, hi_a = rr['bar'].to_numpy(), rr['lo'].to_numpy(), rr['hi'].to_numpy()
    for e in range(len(cut) - 1):
        a, b = cut[e], cut[e + 1]
        bars = bar_a[a:b]
        nb = np.minimum(bars + 1, n - 1)
        ok = (bars + 1 < n) & (sno[nb] == sno[bars]) & meas[sno[nb]]
        zl, zh = lo_a[a:b], hi_a[a:b]
        inside = (C[nb] >= zl) & (C[nb] <= zh)
        frm = np.where(C[bars] > zh, 1, np.where(C[bars] < zl, -1, 0))
        last = -1
        for t in np.flatnonzero(ok & inside & (frm != 0)):
            i = int(nb[t])
            if i <= last:
                continue
            l0, h0, hit = zl[t], zh[t], frm[t]
            w1 = min(i + P['sweep_win'], int(s_end[sno[i]]) + 1, n)
            ex = (l0 - L[i:w1].min()) if hit == 1 else (H[i:w1].max() - h0)
            out.append((i, int(phase_of(sm[i])), ex / u[i], 'TRAIN' if sno[i] < N_TRAIN_SESS else 'TEST'))
            # chờ giá đóng ra khỏi vùng mới đếm lại
            seg = C[i + 1:min(i + 1 + 600, n)]
            outz = np.flatnonzero((seg > h0) | (seg < l0))
            last = i + 1 + int(outz[0]) if len(outz) else n
    return pd.DataFrame(out, columns=['i', 'phase', 'ex_u', 'split'])


def generic_hygiene(ctx, rec, z10, with_k=False):
    """Chỉ số vệ sinh cho bất kỳ bộ record nào (v1/v2/v3), theo TRAIN/TEST."""
    df = ctx['df']
    C = df['close'].to_numpy(float)
    u = K.median_range(df).to_numpy()
    sno = df['session_no'].to_numpy()
    meas = _meas(ctx)
    n = len(df)
    rr, cut = V2.episodes(rec)
    firsts = rr['bar'].to_numpy()[cut[:-1]]
    lens = np.diff(cut)
    rb = rec['bar'].to_numpy()
    lo, hi = rec['lo'].to_numpy(), rec['hi'].to_numpy()
    nxt = np.minimum(rb + 1, n - 1)
    ins = np.zeros(n, bool)
    np.logical_or.at(ins, nxt, (rb + 1 < n) & (C[nxt] >= lo) & (C[nxt] <= hi))
    out = {}
    for sp in ('TRAIN', 'TEST'):
        bm = meas[sno] & ((sno < N_TRAIN_SESS) == (sp == 'TRAIN')) & ~np.isnan(u)
        bars = np.flatnonzero(bm)
        okset = np.zeros(n, bool)
        okset[bars] = True
        sel = okset[rb]
        widu = ((hi - lo) / u[rb])[sel]
        out[sp] = dict(cnt=np.bincount(rb, minlength=n)[bars].mean(), w_u=np.median(widu), w_usd=np.median((hi - lo)[sel]),
                       inside=ins[bars[bars >= 1]].mean(), z10=np.nanmean(z10[bars]),
                       chg=okset[firsts].sum() / (len(bars) / 60.0), life=np.median(lens[okset[firsts]]))
    return out


# ---------------------------------------------------------------------------------------------
# BẢNG
# ---------------------------------------------------------------------------------------------
def _bin(d):
    return np.digitize(d, P['d_bins'][1:-1], right=True)   # ≤1 →0, (1,2]→1, ... (8,12]→6


def _cell(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    return (x.mean() if len(x) else np.nan), len(x)


def reach_table(S, title, col_prefix='r', ws=None):
    ws = ws or P['reach_w']
    md = [title, '', '| d (u) | n gộp | ' + ' | '.join(f'≤{w_} nến: gộp (TRAIN/TEST, |Δ|)' for w_ in ws) + ' |',
          '|---|---|' + '---|' * len(ws)]
    arr = np.full((7, len(ws)), -1.0)
    for bi, lab in enumerate(BIN_LAB):
        s = S[S['bin'] == bi]
        cells = []
        for k, w_ in enumerate(ws):
            g, ng = _cell(s[f'{col_prefix}{w_}'])
            a, na = _cell(s[s['split'] == 'TRAIN'][f'{col_prefix}{w_}'])
            b, nb = _cell(s[s['split'] == 'TEST'][f'{col_prefix}{w_}'])
            if ng < P['min_n']:
                cells.append('—')
                continue
            arr[bi, k] = round(100 * g)
            ta = f'{100 * a:.0f}' if na >= P['min_n'] else '—'
            tb = f'{100 * b:.0f}' if nb >= P['min_n'] else '—'
            dd = f'{100 * abs(a - b):.0f}' if (na >= P['min_n'] and nb >= P['min_n']) else '—'
            cells.append(f'**{100 * g:.0f}** ({ta}/{tb}, {dd})')
        md.append(f'| {lab} | {len(s)} | ' + ' | '.join(cells) + ' |')
    md.append('')
    return md, arr


def sweep_table(E):
    md = ['### 7. P(bị quét) — sau khi giá đóng VÀO vùng từ ngoài, trong 10 nến râu vượt BIÊN XA thêm ≥ x·u (bảng đặt SL)', '',
          '| Pha | n gộp (TRAIN/TEST) | ≥0,25u gộp (TR/TE) | ≥0,5u | ≥1,0u |', '|---|---|---|---|---|']
    arr = np.full((3, 3), -1.0)
    for pi, (pn, _, _) in enumerate(PHASES):
        e = E[E['phase'] == pi]
        tr, te = e[e['split'] == 'TRAIN'], e[e['split'] == 'TEST']
        cells = []
        for k, x in enumerate(P['sweep_x']):
            g = (e['ex_u'] >= x).mean() if len(e) else np.nan
            arr[pi, k] = round(100 * g) if len(e) >= P['min_n'] else -1
            cells.append(f"**{100 * g:.0f}** ({100 * (tr['ex_u'] >= x).mean():.0f}/{100 * (te['ex_u'] >= x).mean():.0f})"
                         if len(e) >= P['min_n'] else '—')
        md.append(f'| {pn} | {len(e)} ({len(tr)}/{len(te)}) | ' + ' | '.join(cells) + ' |')
    e = E
    md.append(f"| Mọi pha | {len(e)} | " + ' | '.join(f"**{100 * (e['ex_u'] >= x).mean():.0f}** ({100 * (e[e['split'] == 'TRAIN']['ex_u'] >= x).mean():.0f}/"
                                                   f"{100 * (e[e['split'] == 'TEST']['ex_u'] >= x).mean():.0f})" for x in P['sweep_x']) + ' |')
    md += ['', 'Đọc: đặt SL cách biên xa x·u thì bảng cho tỉ lệ bị râu chạm trong 10 nến đầu. Đây là mô tả, không phải lợi thế (v2: vùng giả cùng cỡ ≈ như nhau).', '']
    return md, arr


def cs_array(name, arr, fmt='{:.0f}'):
    rows = ['    { ' + ', '.join(fmt.format(x) for x in r) + ' }' for r in arr]
    return [f'{name} = {{'] + [r + (',' if k < len(rows) - 1 else '') for k, r in enumerate(rows)] + ['};']


# ---------------------------------------------------------------------------------------------
def main():
    t0 = time.time()
    bars, lv = V.load_all()
    ctx = V.prepare(bars, lv)
    df, st = ctx['df'], ctx['st']
    cands = gen_candidates(ctx)
    t1 = time.time()
    run = run_engine(ctx, cands)
    t_eng = time.time() - t1
    rec = run['rec']
    os.makedirs(REPORT, exist_ok=True)
    rec.to_csv(os.path.join(REPORT, 'vcl3_records.csv.gz'), index=False)
    S = reach_samples(ctx, rec)
    S['bin'] = _bin(S['d'].to_numpy())
    E = sweep_events(ctx, rec)
    h3 = generic_hygiene(ctx, rec, run['z10'])
    r1 = V.run_engine(ctx, 1.0, V.gen_candidates(ctx))
    h1 = generic_hygiene(ctx, r1['rec'], r1['stats']['z10_bar'])
    r2 = V2.run_engine(ctx)
    h2 = generic_hygiene(ctx, r2['rec'], r2['z10'])
    t_all = time.time() - t0

    sid = st['session_id']
    thin = st['thin'].to_numpy()
    tr = [s for s in st.index if 1 <= s < N_TRAIN_SESS and not thin[s]]
    te = [s for s in st.index if s >= N_TRAIN_SESS and not thin[s]]
    md = ['# Vùng Canh Lệnh — vòng 3 (chốt thiết kế + bảng tra)', '',
          f'Dữ liệu như vòng 1–2: `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h` ({len(df)} nến M1, UTC). Gộp 1,0u, đệm 0,5u, kẹp [1u, 4u].',
          f'TRAIN đo {len(tr)} phiên ({sid.iloc[tr[0]]} → {sid.iloc[tr[-1]]}), TEST đo {len(te)} phiên ({sid.iloc[te[0]]} → {sid.iloc[te[-1]]}).',
          'Vòng này **không tìm lợi thế**: 3 lần đo (SR-KET-QUA 65 phiên, VCL v1, VCL v2) đều cho vị trí vùng ≈ đối chứng. Các bảng dưới là '
          '**bảng mô tả** (tần suất lịch sử) để hiển thị cạnh vùng, không phải tín hiệu.',
          f'Thời gian chạy `vcl3.py`: {t_all:.0f} giây (engine v3 {t_eng:.0f}s; còn lại = bảng tra + chạy lại engine v1, v2 để so vệ sinh).', '']
    # ---- vệ sinh v1/v2/v3
    md += ['### Vệ sinh chart — v1 / v2 / v3 (mục tiêu v3: đổi vùng ≤ 4/giờ, tuổi thọ trung vị ≥ 30 phút)', '',
           '| Chỉ số | v1 TRAIN | v1 TEST | v2 TRAIN | v2 TEST | v3 TRAIN | v3 TEST |', '|---|---|---|---|---|---|---|']
    for lab, k, f in (('vùng hiển thị TB', 'cnt', '{:.2f}'), ('rộng trung vị (u)', 'w_u', '{:.2f}'), ('rộng trung vị (USD)', 'w_usd', '{:.2f}'),
                      ('% nến đóng trong vùng hiển thị', 'inside', 'pct'), ('vùng sống trong ±10u', 'z10', '{:.1f}'),
                      ('đổi vùng / giờ', 'chg', '{:.1f}'), ('tuổi thọ trung vị vùng hiển thị (phút)', 'life', '{:.0f}')):
        cells = []
        for h in (h1, h2, h3):
            for sp in ('TRAIN', 'TEST'):
                x = h[sp][k]
                cells.append(f'{100 * x:.1f}' if f == 'pct' else f.format(x))
        md.append(f'| {lab} | ' + ' | '.join(cells) + ' |')
    md += ['', f'Số lần tính lại bộ vùng v3: {run["n_recalc"]} (≈ 1 lần / {len(df) / max(run["n_recalc"], 1):.0f} nến). '
           'v2: "% trong vùng" thấp do luật gỡ vùng chứa giá; v3 giữ vùng chứa giá nên chỉ số này có nghĩa trở lại.', '']
    # ---- bảng 6
    md += ['### 6. Bảng tra P(chạm cạnh gần) theo khoảng cách d × pha phiên', '',
           f'Mẫu: mỗi {P["sample_every"]} nến, mỗi vùng đang hiển thị (trừ vùng đang chứa giá); cạnh gần đóng băng tại lúc lấy mẫu; '
           'chạm = high/low chạm cạnh gần trong W nến sau, chỉ trong phiên. Ô **đậm** = gộp TRAIN+TEST; (TRAIN/TEST, |Δ|). n < 40 ⇒ "—". '
           'Mẫu chồng lấn (cùng vùng lấy mẫu nhiều lần) ⇒ n hiệu dụng nhỏ hơn n ghi.', '']
    arr_all = {}
    t, a = reach_table(S, '#### Mọi pha')
    md += t
    arr_all['all'] = a
    for pi, (pn, _, _) in enumerate(PHASES):
        t, a = reach_table(S[S['phase'] == pi], f'#### Pha {pn} (sm {PHASES[pi][1]}–{PHASES[pi][2] if pi < 2 else "…"})')
        md += t
        arr_all[pi] = a
    # ---- bảng 7
    t, sw_arr = sweep_table(E)
    md += t
    # ---- bảng 8
    md += ['### 8. Kiểm chứng "chỉ khoảng cách": P(chạm) theo loại ứng viên trong vùng (mọi pha, gộp)', '',
           '| d | Loại | n | ≤15 | ≤30 | ≤60 | ≤120 |', '|---|---|---|---|---|---|---|']
    for bi in (1, 3):
        s = S[S['bin'] == bi]
        rows = [('mọi vùng', np.ones(len(s), bool))] + [(t_, (s['mask'].to_numpy() & BIT[t_]) > 0) for t_ in TYPES] + \
               [('chỉ D', s['mask'].to_numpy() == BIT['D'])]
        for lab, msk in rows:
            x = s[msk]
            vals = []
            for w_ in P['reach_w']:
                p_, nn = _cell(x[f'r{w_}'])
                vals.append(f'{100 * p_:.0f} ±{100 * math.sqrt(max(p_ * (1 - p_), 0) / max(nn, 1)):.0f}' if nn >= P['min_n'] else '—')
            md.append(f'| {BIN_LAB[bi]} | {lab} | {len(x)} | ' + ' | '.join(vals) + ' |')
    md += ['', '± = sai số nhị thức (đánh giá thấp vì mẫu chồng lấn).', '']
    # ---- bảng 9
    S['rev_'] = S['rev']
    md += ['### 9. Chạm rồi quay lại ≥ 2u trong 30 nến (kỳ vọng "TP rồi đảo") — trong các mẫu ĐÃ chạm trong 120 nến', '',
           '| d (u) | n chạm gộp | gộp % | TRAIN % | TEST % | |Δ| |', '|---|---|---|---|---|---|']
    rev_arr = np.full(7, -1.0)
    for bi, lab in enumerate(BIN_LAB):
        s = S[(S['bin'] == bi) & S['rev'].notna()]
        g, ng = _cell(s['rev'])
        a, na = _cell(s[s['split'] == 'TRAIN']['rev'])
        b, nb = _cell(s[s['split'] == 'TEST']['rev'])
        if ng < P['min_n']:
            md.append(f'| {lab} | {ng} | — | — | — | — |')
            continue
        rev_arr[bi] = round(100 * g)
        md.append(f'| {lab} | {ng} | **{100 * g:.0f}** | {100 * a:.0f} | {100 * b:.0f} | {100 * abs(a - b):.0f} |')
    md.append('')
    md += ['<!-- NHAN-XET -->', '']

    # ---- ví dụ cụ thể: nến 20:35 VN có close gần 4440 và u gần 1,7
    u_all = K.median_range(df).to_numpy()
    tv = df['t_vn']
    cand = np.flatnonzero((tv.dt.hour == 20).to_numpy() & (tv.dt.minute == 35).to_numpy() & _meas(ctx)[df['session_no'].to_numpy()])
    sc = np.abs(df['close'].to_numpy()[cand] - 4440.0) / 5 + np.abs(u_all[cand] - 1.7)
    ex_i = int(cand[np.argmin(sc)])
    ctx_ex = dict(i=ex_i, t=str(tv.iloc[ex_i]), c=float(df['close'].iloc[ex_i]), u=float(u_all[ex_i]),
                  sm=int(df['sm'].iloc[ex_i]), sid=str(df['session_id'].iloc[ex_i]),
                  zones=rec[rec['bar'] == ex_i].copy())
    spec = spec_section(ctx_ex, arr_all, sw_arr, rev_arr)
    path = os.path.join(REPORT, 'VCL-VONG-3.md')
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    tail = old.split('<!-- NHAN-XET -->', 1)[1].split('<!-- DAC-TA -->', 1)[0] if '<!-- NHAN-XET -->' in old else '\n## Nhận xét\n(chưa viết)\n\n'
    open(path, 'w', encoding='utf-8').write('\n'.join(md[:-2]) + '\n<!-- NHAN-XET -->' + tail + '<!-- DAC-TA -->\n' + '\n'.join(spec) + '\n')
    print('\n'.join(md + spec))
    print(f'TỔNG THỜI GIAN: {t_all:.1f}s')


def types_of(mask):
    return '+'.join(t for t in TYPES if mask & BIT[t])


def spec_section(ex, arr_all, sw_arr, rev_arr):
    md = ['## ĐẶC TẢ PORT C# (vòng 4)', '',
          '### Hằng số', '',
          '| Tên | Giá trị | Ghi chú |', '|---|---|---|',
          '| TICK | 0,1 | 1 giá = 1 USD = 10 tick |',
          '| U_N | 50 | u = TRUNG VỊ (high−low) của 50 nến M1 gần nhất, GỒM nến vừa đóng; cần ≥ 10 nến; chạy xuyên phiên |',
          '| SESSION_GAP_MIN | 30 | khoảng trống > 30 phút giữa 2 nến M1 ⇒ phiên mới |',
          '| SESS_BARS | 1380 | 1 "phiên" khi tính tuổi ứng viên |',
          '| LINK_U | 1,0 | gộp đơn liên kết khi 2 mức liền kề cách ≤ 1,0u |',
          '| PAD_U | 0,5 | biên vùng = min/max mức trong cụm ± 0,5u |',
          '| WMIN_U / WMAX_U | 1,0 / 4,0 | rộng < 1u ⇒ nới đều quanh tâm; rộng > 4u ⇒ tách tại khe lớn nhất (đệ quy) |',
          '| Overlap | cắt giữa | 2 vùng kề chồng nhau ⇒ cả hai dùng điểm giữa đoạn chồng làm biên |',
          '| SWING_M5_K | 5 | đỉnh/đáy M5: cao/thấp nhất 5 nến M5 mỗi bên (đỉnh: 5 nến trước THẤP HƠN hẳn) |',
          '| SWING_M15_K | 3 | như trên với nến M15, 3 nến mỗi bên |',
          '| W_B / W_B15 / W_C / W_NPOC | 2 / 3 / 2 / 3 | trọng số loại |',
          '| W_D10 / W_D50 / W_D100 | 1 / 2 / 3 | số tròn bội 10 / 50 / 100 USD |',
          '| D_WINDOW | 40 USD | sinh mức D bội 10 trong [close−40, close+40] khi lần đầu lọt cửa sổ; D không chết, không suy giảm, không chuyển vai |',
          '| TOUCH_K / TOUCH_CAP | 0,3 / 5 | điểm ứng viên × (1 + 0,3 × min(số lần chạm, 5)); chạm = giá đóng vào vùng từ ngoài (cùng phiên) |',
          '| FLIP_MULT / BREAK_U | 0,7 / 1,0 | đóng xuyên qua CẢ vùng ≥ 1u ⇒ chuyển vai, điểm ×0,7; lần xuyên thứ 2 ⇒ chết (B, B15, C, POC trần) |',
          '| NEAR_N | 2 | 2 vùng gần mỗi phía |',
          '| FAR_LO_U / FAR_RANGE_K | 2,0 / 1,5 | khe xa: khoảng cách từ cạnh ngoài vùng gần-2 nằm trong [2u, 1,5 × biên độ phiên trước] |',
          '| KEEP_BONUS | 1,5 | khi tính lại bộ, vùng đang hiển thị được nhân điểm ×1,5 lúc tranh khe xa |',
          '| CORRIDOR_FALLBACK_U | 4,0 | thiếu vùng gần-1 ở phía nào thì biên hành lang phía đó = giá lúc chốt bộ ± 4u |', '',
          '### Pha phiên (sm = số phút kể từ 05:00 VN, khi Mỹ dùng giờ mùa đông thì các mốc lùi +1h theo giờ VN — như kernel)', '',
          '- Á: sm < 450 (05:00–12:30 VN) · Âu: 450 ≤ sm < 840 (12:30–19:00 VN) · Mỹ: sm ≥ 840 (19:00 VN → hết phiên).', '',
          '### Ứng viên — sinh / sống / chết', '',
          '- **B** (swing M5 k=5): nến M5 gộp theo mốc đồng hồ (UTC, floor 5 phút), không gộp xuyên phiên. Đỉnh xác nhận khi nến M5 thứ 5 sau nó ĐÓNG '
          '(theo đồng hồ: nến M1 cuối cùng là phút thứ 5; nếu thiếu phút thì đợi nến M1 kế tiếp). Sống 4 phiên (5520 nến M1); từ 2 phiên trở đi điểm ×0,5.',
          '- **B15** (swing M15 k=3): như B với nến M15, 3 nến mỗi bên. Sống 3 phiên (4140 nến), không suy giảm.',
          '- **C** (sống 1380 nến từ lúc sinh): đỉnh/đáy/đóng phiên trước (sinh ở nến đầu phiên); VAH/VAL/POC hôm qua (profile hàng 0,2 giá, VA 70%, '
          'phiên trước ≥ 300 nến); biên Á = đỉnh/đáy các nến sm < 450 (cần ≥ 60 nến), sinh ở nến đầu có sm ≥ 450; VAH/VAL Âu (cửa sổ 450 ≤ sm < 840, '
          'cần ≥ 60 nến), sinh ở nến đầu có sm ≥ 840.',
          '- **POC trần** (w3): POC các phiên trước (≤ 30 phiên) chưa bị chạm tính tới đầu phiên này; giữ 3 cái gần nhất; chết ở nến đầu tiên '
          'high ≥ POC ≥ low.',
          '- **D**: xem D_WINDOW. Vùng mà MỌI mức trong nó là D bội 10 (không 50/100, không loại khác) = "chỉ D-10$".',
          '- **Phía (side) của ứng viên** lúc sinh: close − giá ≥ 0,5u ⇒ +1 (hỗ trợ); ≤ −0,5u ⇒ −1 (kháng cự); còn lại 0, gán khi giá đóng ra khỏi vùng chứa nó.', '',
          '### Mỗi nến đóng (thứ tự)', '',
          '1. Nạp ứng viên sinh tại nến này + sinh D mới; bỏ ứng viên hết tuổi.',
          '2. Gộp → vùng (dùng u hiện tại). Đếm chạm (giá đóng vào vùng từ ngoài, nến trước cùng phiên).',
          '3. Luật xuyên cho B/B15/C/POC trần trong từng vùng: side +1 và close < lo − 1u, hoặc side −1 và close > hi + 1u ⇒ breaks+1, đổi side; '
          'breaks ≥ 2 ⇒ chết. Ghi cờ "vùng có ứng viên vừa bị xuyên".',
          '4. Gộp lại sau khi bỏ ứng viên chết. Điểm vùng = Σ w × (0,5 nếu quá mốc suy giảm) × (1 + 0,3·min(chạm,5)) × 0,7^breaks.',
          '5. Khớp từng vùng đang hiển thị với vùng mới chồng lấn nhiều nhất. **Tính lại bộ** nếu: chưa có bộ; có vùng hiển thị không khớp '
          '(biến mất) hoặc 2 vùng cũ nhập vào 1; vùng hiển thị có cờ vừa bị xuyên; hoặc close > cạnh trên vùng gần-1 phía trên, hoặc close < cạnh '
          'dưới vùng gần-1 phía dưới (hành lang, dùng biên HIỆN TẠI của các vùng đã khớp). Không tính lại ⇒ giữ nguyên bộ (biên cập nhật theo vùng khớp).',
          '6. Chọn bộ mới: vùng chứa close (lo ≤ close ≤ hi) = "đang kiểm tra"; 2 vùng gần phía trên = 2 vùng có lo > cạnh trên vùng chứa giá '
          '(hoặc > close), lo nhỏ nhất; gương phía dưới; khe xa mỗi phía như hằng số; ưu tiên vùng không phải "chỉ D-10$". Tối đa 7 vùng.',
          '7. Vùng giữ nguyên mã (ID) nếu khớp vùng cũ ⇒ đếm "đổi vùng" = số ID mới.', '',
          '### Bảng tra nhúng code (giá trị %, gộp TRAIN+TEST; −1 = không đủ mẫu, hiển thị "—")', '',
          'Bin khoảng cách d (u, tới cạnh gần): 0: ≤1 · 1: 1–2 · 2: 2–3 · 3: 3–4 · 4: 4–6 · 5: 6–8 · 6: 8–12 (> 12u: không hiển thị). '
          'Cột cửa sổ: 15 / 30 / 60 / 120 nến. Pha: 0 Á · 1 Âu · 2 Mỹ.', '', '```csharp']
    for pi in range(3):
        md += cs_array(f'static readonly int[,] REACH_PHASE{pi}', arr_all[pi])
    md += cs_array('static readonly int[,] REACH_ALL', arr_all['all'])
    md += cs_array('// pha × {≥0,25u, ≥0,5u, ≥1,0u}\nstatic readonly int[,] SWEEP', sw_arr)
    md += ['// theo bin d, mọi pha', 'static readonly int[] REVERT2U = { ' + ', '.join(f'{x:.0f}' for x in rev_arr) + ' };', '```', '']
    # ví dụ
    z = ex['zones']
    ph = int(phase_of(np.array([ex['sm']]))[0])
    pn = PHASES[ph][0]
    md += [f"### Ví dụ cụ thể (nến thật gần đề bài nhất): phiên {ex['sid']}, {ex['t'][11:16]} VN, close {ex['c']:.1f}, u = {ex['u']:.2f}, pha {pn}", '',
           '| # | vùng (lo–hi) | vai | loại · điểm | d tới cạnh gần (u) | dòng tra hiển thị |', '|---|---|---|---|---|---|']
    order = sorted(z.itertuples(), key=lambda r: -(r.lo + r.hi))
    for k, r in enumerate(order, 1):
        if r.slot == 'K':
            sw = SWEEP_TXT(sw_arr, ph)
            md.append(f"| {k} | {r.lo:.1f}–{r.hi:.1f} | đang kiểm tra | {types_of(r.mask)} · {r.score:.0f} | 0 (giá trong vùng) | {sw} |")
            continue
        ne = r.lo if r.side == 1 else r.hi
        d = (ne - ex['c']) * r.side / ex['u']
        vai = ('kháng cự' if r.side == 1 else 'hỗ trợ') + (' (xa)' if r.slot == 'F' else '')
        if d > 12:
            line = 'xa > 12u: không tra'
        else:
            bi = int(_bin(np.array([d]))[0])
            row = arr_all[ph][bi]
            line = 'chạm ≤15/30/60/120 nến: ' + ' / '.join('—' if x < 0 else f'{x:.0f}%' for x in row)
            if rev_arr[bi] >= 0:
                line += f'; chạm rồi quay ≥2u: {rev_arr[bi]:.0f}%'
        md.append(f"| {k} | {r.lo:.1f}–{r.hi:.1f} | {vai} | {types_of(r.mask)} · {r.score:.0f} | {d:.1f} | {line} |")
    md += ['', f'Ví dụ này có {len(z)} vùng (tối đa 7: 1 đang kiểm tra + 2 gần + 1 xa mỗi phía; thiếu vùng chứa giá hoặc thiếu khe xa thì ít hơn).', '']
    return md


def SWEEP_TXT(sw, ph):
    return 'bị quét quá biên xa ≥0,25/0,5/1,0u trong 10 nến: ' + ' / '.join('—' if x < 0 else f'{x:.0f}%' for x in sw[ph])


if __name__ == '__main__':
    main()
