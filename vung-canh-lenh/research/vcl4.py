# -*- coding: utf-8 -*-
"""
VÙNG CANH LỆNH — VÒNG 4 phần 1: chống nhấp nháy (luật VỆ SINH, không tìm lợi thế). Bản này là CHUẨN để port C#.
Khác v3 (vcl3.py) đúng 3 luật:
  (a) KEEP khe gần: khi tính lại bộ, vùng đang hiển thị ở khe gần được giữ nếu còn nằm trong 3 vùng gần nhất phía đó.
  (b) Hành lang nới 1u ra ngoài cạnh xa của vùng gần-1 mỗi phía.
  (c) Tuổi tối thiểu: vùng có ID MỚI chỉ được vào bộ khi ứng viên mạnh nhất của nó đã sống >= 10 nến (vùng chứa giá: hiện ngay).
Chạy: python3 vcl4.py → report/VCL-VONG-4.md (+ report/vcl4_records.csv.gz)
"""
import os, time, math
import numpy as np
import pandas as pd
import vcl as V
import vcl2 as V2
import vcl3 as V3

K = V.K
REPORT = V.REPORT
INF = V.INF
P = dict(V3.P)
P.update(keep_near_top=3, corridor_pad_u=1.0, min_age=10)
TYPES, BIT, KIND = V3.TYPES, V3.BIT, V3.KIND


def fresh_select(lo, hi, score, d10, eligible, c, u, maxd, keep=frozenset(), keep_near=frozenset()):
    """Như v3 + (a) giữ vùng gần cũ nếu còn trong 3 gần nhất, (c) chỉ vùng eligible (đã đủ tuổi hoặc đang hiển thị) mới được chọn
    vào khe gần/xa; vùng chứa giá luôn được hiện."""
    out = []
    cont = np.flatnonzero((lo <= c) & (c <= hi))
    cz = int(cont[0]) if len(cont) else None
    if cz is not None:
        out.append((cz, 'K', 0))
    for side in (1, -1):
        if side > 0:
            ref = hi[cz] if cz is not None else c
            idx = np.flatnonzero((lo > ref) & eligible)
            idx = idx[np.argsort(lo[idx], kind='stable')]
        else:
            ref = lo[cz] if cz is not None else c
            idx = np.flatnonzero((hi < ref) & eligible)
            idx = idx[np.argsort(-hi[idx], kind='stable')]
        top = [int(z) for z in idx[:P['keep_near_top']]]
        kept = [z for z in top if z in keep_near][:P['near_n']]
        near = kept + [z for z in top if z not in kept][:P['near_n'] - len(kept)]
        near = sorted(near, key=lambda z: lo[z] if side > 0 else -hi[z])
        out += [(z, 'N', side) for z in near]
        outer = (hi[near[-1]] if side > 0 else lo[near[-1]]) if near else ref
        pool = []
        for z in idx:
            z = int(z)
            if z in near:
                continue
            d = (lo[z] - outer) if side > 0 else (outer - hi[z])
            if P['far_lo_u'] * u <= d <= maxd:
                pool.append(z)
        if pool:
            nd = [z for z in pool if not d10[z]]
            pool = nd if nd else pool
            far = max(pool, key=lambda z: score[z] * (P['keep_bonus'] if z in keep else 1.0))
            out.append((far, 'F', side))
    return out


def corridor_of(sel, lo, hi, anchor, u):
    """(b) Hành lang = [cạnh dưới vùng gần-1 phía dưới − 1u, cạnh trên vùng gần-1 phía trên + 1u]."""
    up = [z for z, s, sd in sel if s == 'N' and sd == 1]
    dn = [z for z, s, sd in sel if s == 'N' and sd == -1]
    pad = P['corridor_pad_u'] * u
    top = hi[min(up, key=lambda z: lo[z])] + pad if up else anchor + P['corridor_fallback_u'] * u
    bot = lo[max(dn, key=lambda z: hi[z])] - pad if dn else anchor - P['corridor_fallback_u'] * u
    return bot, top


def corridor_update(lo, hi, score, d10, brk_zone, zage, c, u, maxd, prev, anchor):
    """Như v3.corridor_update + 3 luật. zage[z] = số nến ứng viên mạnh nhất của vùng z đã sống."""
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
    keep_near = frozenset(j for p, j in zip(prev, js) if j >= 0 and p[3] == 'N')
    eligible = zage >= P['min_age']
    for j in emap:
        eligible[j] = True
    sel = fresh_select(lo, hi, score, d10, eligible, c, u, maxd, keep=frozenset(emap), keep_near=keep_near)
    return [(z, s, emap.get(z), sd) for z, s, sd in sel], c, True


REC_COLS = V3.REC_COLS


def run_engine(ctx, cands=None, link=1.0):
    """Engine v4 (copy v3 + tuổi ứng viên mạnh nhất của mỗi vùng)."""
    df = ctx['df']
    cands = V3.gen_candidates(ctx) if cands is None else cands
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
    death = np.zeros(cap, np.int64); birth = np.zeros(cap, np.int64)
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
            death[m], half[m], birth[m] = cols['death'][ptr], cols['half'][ptr], cols['birth'][ptr]
            alive[m] = True
            dd = C[i] - price[m]
            uu = u_all[i] if u_all[i] == u_all[i] else 1.0
            side[m] = 0 if abs(dd) < 0.5 * uu else (1 if dd > 0 else -1)
            m += 1
            ptr += 1
        for v in range(int(math.ceil((C[i] - P['d_window']) / 10.0)) * 10, int(C[i] + P['d_window']) + 1, 10):
            if v not in d_have:
                d_have.add(v)
                price[m], kind[m], death[m], half[m], birth[m] = v, 4, INF, INF, i
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
        bm = np.isin(kk, V3.BREAK_KINDS)
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
        # tuổi ứng viên mạnh nhất mỗi vùng (hoà điểm ⇒ ứng viên SINH SỚM hơn, rồi giá thấp hơn)
        o = np.lexsort((-birth[act], val, lab))           # theo lab, rồi val tăng, rồi birth giảm ⇒ phần tử cuối mỗi nhóm = mạnh nhất, sinh sớm nhất
        last = np.r_[np.flatnonzero(np.diff(lab[o])), len(o) - 1]
        zage = np.zeros(nz, np.int64)
        zage[lab[o][last]] = i - birth[act][o][last]
        s = int(sno[i])
        if s >= 1:
            pr = srange[s - 1]
        else:
            a = int(s_start[s])
            pr = max(H[a:i + 1].max() - L[a:i + 1].min(), 10 * u)
        sel, anchor, rc = corridor_update(zlo, zhi, score, d10, brk_zone, zage, C[i], u, P['far_range_k'] * pr, prev, anchor)
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


def tables_for(ctx, rec):
    S = V3.reach_samples(ctx, rec)
    S['bin'] = V3._bin(S['d'].to_numpy())
    E = V3.sweep_events(ctx, rec)
    arr = {}
    _, arr['all'] = V3.reach_table(S, '')
    for pi in range(3):
        _, arr[pi] = V3.reach_table(S[S['phase'] == pi], '')
    _, sw = V3.sweep_table(E)
    rev = np.full(7, -1.0)
    for bi in range(7):
        s = S[(S['bin'] == bi) & S['rev'].notna()]
        if len(s) >= P['min_n']:
            rev[bi] = round(100 * s['rev'].mean())
    return S, E, arr, sw, rev


def main():
    t0 = time.time()
    bars, lv = V.load_all()
    ctx = V.prepare(bars, lv)
    cands = V3.gen_candidates(ctx)
    t1 = time.time()
    r4 = run_engine(ctx, cands)
    t_eng = time.time() - t1
    rec4 = r4['rec']
    os.makedirs(REPORT, exist_ok=True)
    rec4.to_csv(os.path.join(REPORT, 'vcl4_records.csv.gz'), index=False)
    r3 = V3.run_engine(ctx, cands)
    h3 = V3.generic_hygiene(ctx, r3['rec'], r3['z10'])
    h4 = V3.generic_hygiene(ctx, rec4, r4['z10'])
    S4, E4, a4, sw4, rv4 = tables_for(ctx, rec4)
    _, _, a3, sw3, rv3 = tables_for(ctx, r3['rec'])
    t_all = time.time() - t0
    md = ['# Vùng Canh Lệnh — vòng 4 phần 1: chống nhấp nháy', '',
          'Dữ liệu, ứng viên, gộp, bảng tra: y như vòng 3. Thêm đúng 3 luật vệ sinh: (a) giữ vùng gần cũ nếu còn trong 3 gần nhất; '
          '(b) hành lang nới 1u ra ngoài cạnh xa vùng gần-1; (c) vùng có ID mới chỉ vào bộ khi ứng viên mạnh nhất đã sống ≥ 10 nến '
          '(vùng chứa giá hiện ngay). Đây là chọn luật vệ sinh, không phải tìm lợi thế.',
          f'Thời gian chạy `vcl4.py`: {t_all:.0f} giây (engine v4 {t_eng:.0f}s).', '',
          '### Vệ sinh v3 → v4 (mục tiêu: đổi vùng ≤ 4/giờ, tuổi thọ trung vị ≥ 30 phút)', '',
          '| Chỉ số | v3 TRAIN | v3 TEST | v4 TRAIN | v4 TEST |', '|---|---|---|---|---|']
    for lab, k, f in (('vùng hiển thị TB', 'cnt', '{:.2f}'), ('rộng trung vị (u)', 'w_u', '{:.2f}'), ('rộng trung vị (USD)', 'w_usd', '{:.2f}'),
                      ('% nến đóng trong vùng hiển thị', 'inside', 'pct'), ('vùng sống trong ±10u', 'z10', '{:.1f}'),
                      ('đổi vùng / giờ', 'chg', '{:.1f}'), ('tuổi thọ trung vị vùng hiển thị (phút)', 'life', '{:.0f}')):
        cells = []
        for h in (h3, h4):
            for sp in ('TRAIN', 'TEST'):
                x = h[sp][k]
                cells.append(f'{100 * x:.1f}' if f == 'pct' else f.format(x))
        md.append(f'| {lab} | ' + ' | '.join(cells) + ' |')
    md += ['', f'Số lần tính lại bộ: v3 {r3["n_recalc"]} → v4 {r4["n_recalc"]}.', '']
    # bảng tra v4 + |Δ| so v3
    md += ['### Bảng tra trên v4 và |Δ| so với v3 (điểm %)', '']
    big = []
    for key, name in (('all', 'Mọi pha'), (0, 'Á'), (1, 'Âu'), (2, 'Mỹ')):
        md += [f'#### 6 · P(chạm) — {name}: v4 (|Δ| so v3)', '', '| d (u) | ≤15 | ≤30 | ≤60 | ≤120 |', '|---|---|---|---|---|']
        for bi, lab in enumerate(V3.BIN_LAB):
            cells = []
            for k in range(4):
                x4, x3 = a4[key][bi, k], a3[key][bi, k]
                if x4 < 0 or x3 < 0:
                    cells.append('—')
                    continue
                dd = abs(x4 - x3)
                if dd > 3:
                    big.append(f'bảng 6 {name} d {lab} ≤{P["reach_w"][k]} nến: v3 {x3:.0f} → v4 {x4:.0f}')
                cells.append(f'{x4:.0f} ({dd:.0f})' + (' ⚠' if dd > 3 else ''))
            md.append(f'| {lab} | ' + ' | '.join(cells) + ' |')
        md.append('')
    md += ['#### 7 · P(bị quét) v4 (|Δ| so v3)', '', '| Pha | ≥0,25u | ≥0,5u | ≥1,0u |', '|---|---|---|---|']
    for pi, (pn, _, _) in enumerate(V3.PHASES):
        cells = []
        for k in range(3):
            dd = abs(sw4[pi, k] - sw3[pi, k])
            if dd > 3:
                big.append(f'bảng 7 pha {pn} cột {k}: v3 {sw3[pi, k]:.0f} → v4 {sw4[pi, k]:.0f}')
            cells.append(f'{sw4[pi, k]:.0f} ({dd:.0f})' + (' ⚠' if dd > 3 else ''))
        md.append(f'| {pn} | ' + ' | '.join(cells) + ' |')
    md += ['', '#### 9 · Chạm rồi quay lại ≥2u v4 (|Δ| so v3)', '', '| d (u) | ' + ' | '.join(V3.BIN_LAB) + ' |', '|---|' + '---|' * 7,
           '| % | ' + ' | '.join(f'{rv4[b]:.0f} ({abs(rv4[b] - rv3[b]):.0f})' + (' ⚠' if abs(rv4[b] - rv3[b]) > 3 else '') for b in range(7)) + ' |', '']
    for b in range(7):
        if abs(rv4[b] - rv3[b]) > 3:
            big.append(f'bảng 9 d {V3.BIN_LAB[b]}: v3 {rv3[b]:.0f} → v4 {rv4[b]:.0f}')
    md += ['**Ô đổi > 3 điểm:** ' + ('; '.join(big) if big else 'không có.'), '']
    md += ['### Bảng tra v4 nhúng C# (gộp TRAIN+TEST, %; −1 = thiếu mẫu)', '', '```csharp']
    for pi in range(3):
        md += V3.cs_array(f'static readonly int[,] REACH_PHASE{pi}', a4[pi])
    md += V3.cs_array('static readonly int[,] REACH_ALL', a4['all'])
    md += V3.cs_array('static readonly int[,] SWEEP', sw4)
    md += ['static readonly int[] REVERT2U = { ' + ', '.join(f'{x:.0f}' for x in rv4) + ' };', '```', '']
    md += ['<!-- NHAN-XET -->', '']
    path = os.path.join(REPORT, 'VCL-VONG-4.md')
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    tail = old.split('<!-- NHAN-XET -->', 1)[1] if '<!-- NHAN-XET -->' in old else '\n## Nhận xét\n(chưa viết)\n'
    open(path, 'w', encoding='utf-8').write('\n'.join(md[:-2]) + '\n<!-- NHAN-XET -->' + tail)
    np.savez(os.path.join(REPORT, 'vcl4_tables.npz'), r0=a4[0], r1=a4[1], r2=a4[2], ra=a4['all'], sw=sw4, rv=rv4)
    print('\n'.join(md))
    print(f'TỔNG THỜI GIAN: {t_all:.1f}s')


if __name__ == '__main__':
    main()
