# -*- coding: utf-8 -*-
"""Benchmark LỌC VÙNG LỊCH SỬ (PLAN-LOC-VUNG.md) — đo trên khối VLichSu (port lich_su.track) của replay C# v5.

Mục đích: (1) mô tả phân phối khối lịch sử (sống, số lần chạm, kết cục, rộng, loại, khoảng cách lúc sinh);
(2) với từng BỘ LỌC ứng viên (lên hạng KHÔNG nhìn trước: khối chỉ "đủ điều kiện" từ nến t_q trở đi), đo: % khối còn lại,
khối/phiên, khối thấy trong 24 h, số khối đậm tại nến signal Benzo, phủ Display tại signal, khoảng cách tới khối gần nhất;
(3) "mạnh" có thật không: kết cục các lần chạm SAU t_q của khối thật so với khối giả KHỚP KHOẢNG CÁCH (gương qua giá đóng lúc tạo,
cùng rộng, cùng tuổi thọ) và khối giả dời bản đồ (Đ1, 3–15 giá) — TRAIN (phiên ≤ 2026-09-15) / TEST riêng.

Chạy:  python3 loc_vung_bench.py [--reps 10] [--fast]   (cần report/vcl5_cs_replay_v5.csv + _29d.csv — chạy lich_su.py trước)
In markdown ra màn hình; ghi report/loc_vung_zones.csv (bảng khối + lần chạm) để tái dùng."""
import os, sys, collections, time
import numpy as np
import pandas as pd
import lich_su as LS

HERE = os.path.dirname(os.path.abspath(__file__))
REP = os.path.join(HERE, 'report')
SIG_A = LS.SIGNALS
SIG_B = os.path.join(LS.REPO, 'benzo-trader', 'research', 'report', '_replay_cs_B3.csv')
SPLIT_END = '2026-09-15'
TAU, EXIT, GAP = LS.EP_TAU, LS.EP_EXIT, LS.EP_GAP
GAPM = LS.LS_GAP_MIN
REPS = 10
for k, a in enumerate(sys.argv):
    if a == '--reps':
        REPS = int(sys.argv[k + 1])
FAST = '--fast' in sys.argv
RNG = np.random.default_rng(20261023)


# ----------------------------------------------------------------------------------------------------------------- dữ liệu
def load_ext(base, replay):
    D = LS.load(base, replay)
    rep = pd.read_csv(replay, usecols=['bar_idx', 'zone_id', 'lo', 'hi', 'score'])
    D['score'] = {(int(b), int(z)): float(s) for b, z, s in zip(rep['bar_idx'], rep['zone_id'], rep['score'])}
    rec = os.path.join(REP, 'vcl5_records.csv.gz')
    D['mask'] = {}
    if os.path.exists(rec):
        r = pd.read_csv(rec, usecols=['bar', 'lo', 'hi', 'mask'])
        D['mask'] = {(int(b), round(float(lo), 4), round(float(hi), 4)): int(m) for b, lo, hi, m in zip(r['bar'], r['lo'], r['hi'], r['mask'])}
    D['mins'] = ((D['t'] - D['t'][0]) / np.timedelta64(1, 'm')).astype(float)
    dt = np.diff(D['mins'], prepend=D['mins'][0])
    D['new_sess'] = np.concatenate([[True], dt[1:] > LS.GAP_MINUTES])
    D['sess'] = np.cumsum(D['new_sess']) - 1
    D['cprev'] = np.where(D['new_sess'], D['O'], np.concatenate([[D['O'][0]], D['C'][:-1]]))
    return D


def track_ext(D):
    """= lich_su.track nhưng ghi thêm: nến giết (kill), điểm/slot/loại/khoảng cách lúc tạo. Kiểm: cùng số khối, cùng (start,end,lo,hi)."""
    allz, st, mins = LS.track(D)
    # nến giết = nến tracker chốt kết thúc (xuyên phá: i = end + G hoặc hơn nếu kẹp; hết hạn: nến đầu có mins − mins[last] > 60)
    for h in allz:
        if h['end'] < 0:
            h['kill'] = D['n'] - 1
        elif h['ly_do'] == 'xuyên phá':
            h['kill'] = h['end'] + GAP
        else:
            j = h['end'] + 1
            while j < D['n'] and mins[j] - mins[h['end']] <= GAPM:
                j += 1
            h['kill'] = min(j, D['n'] - 1)
        zid = None
        for (z, lo, hi, slot) in D['disp'].get(h['start'], ()):
            if lo == h['lo'] and hi == h['hi']:
                zid = z; h['slot0'] = slot
        h['score0'] = D['score'].get((h['start'], zid), np.nan) if zid is not None else np.nan
        h['mask0'] = D['mask'].get((h['start'], round(h['lo'], 4), round(h['hi'], 4)), -1)
        c = D['C'][h['start']]
        h['d0'] = max(h['lo'] - c, c - h['hi'], 0.0)
        h['sess'] = int(D['sess'][h['start']])
        h['split'] = 'TRAIN' if str(pd.Timestamp(D['t'][h['start']]).date()) <= SPLIT_END else 'TEST'
    return allz


# ------------------------------------------------------------------------------------------------------- máy lần chạm trên 1 dải
def simulate(D, lo, hi, start, kill, vai0=None):
    """Chạy máy lần chạm (τ, E, G như LichSuTracker) trên dải cố định [lo, hi] từ nến start tới nến kill (gồm cả).
    Trả (end, ly_do, vai, eps) — eps: list (bat, chot, ket, pen) với ket ∈ {'đảo','xuyên','chưa rõ'}, pen = độ sâu giá đóng vượt
    biên sau lưng vai (giá). Xuyên phá ⇒ end = max(start, i − G), dừng. Hết kill mà còn sống ⇒ end = kill_end (do bên gọi quyết)."""
    H, L, C, cprev, ns = D['H'], D['L'], D['C'], D['cprev'], D['new_sess']
    c0 = C[start]
    vai = (1 if c0 < lo else (-1 if c0 > hi else 0)) if vai0 is None else vai0
    ep = None; eps = []
    for i in range(start, kill + 1):
        if ns[i] and i > start and ep is not None:
            eps.append((ep[0], i, ('chưa rõ' if ep[1] == 0 else _ket(vai, ep[2])), ep[3])); ep = None
        if vai == 0:
            if C[i] < lo: vai = 1
            elif C[i] > hi: vai = -1
        cham = max(cprev[i], H[i]) >= lo - TAU and min(cprev[i], L[i]) <= hi + TAU
        neo = cham or (lo - EXIT <= C[i] <= hi + EXIT)
        if ep is None and cham:
            ep = [i, 0, 0, 0.0]                    # bat, dem, phia, pen
        if ep is not None:
            pen = (C[i] - hi) if vai == 1 else ((lo - C[i]) if vai == -1 else 0.0)
            if pen > ep[3]: ep[3] = pen
            if neo:
                ep[1] = 0; ep[2] = 0
            else:
                ep[2] = 1 if C[i] > hi else -1
                ep[1] += 1
                if ep[1] >= GAP:
                    k = _ket(vai, ep[2])
                    eps.append((ep[0], i, k, ep[3])); ep = None
                    if k == 'xuyên':
                        return max(start, i - GAP), 'xuyên phá', vai, eps
    if ep is not None:
        eps.append((ep[0], kill, ('chưa rõ' if ep[1] == 0 else _ket(vai, ep[2])), ep[3]))
    return -1, '', vai, eps


def _ket(vai, phia):
    if vai == 0:
        return 'chưa rõ'
    return 'xuyên' if (vai == 1 and phia == 1) or (vai == -1 and phia == -1) else 'đảo'


def zone_table(D, allz):
    rows = []
    for h in allz:
        end, ly, vai, eps = simulate(D, h['lo'], h['hi'], h['start'], h['kill'])
        if ly == 'xuyên phá':
            assert end == h['end'], (h['id'], end, h['end'])
        else:
            assert h['ly_do'] != 'xuyên phá'
            end = h['end'] if h['end'] >= 0 else D['n'] - 1
        rows.append(dict(id=h['id'], lo=h['lo'], hi=h['hi'], w=h['hi'] - h['lo'], vai=vai, start=h['start'], end=end, kill=h['kill'],
                         ly_do=h['ly_do'] or 'còn sống', dur=D['mins'][end] - D['mins'][h['start']], n_cham_lai=h['n_cham_lai'],
                         n_ep=len(eps), n_dao=sum(e[2] == 'đảo' for e in eps), n_xuyen=sum(e[2] == 'xuyên' for e in eps),
                         n_chuaro=sum(e[2] == 'chưa rõ' for e in eps), pen_max=max([e[3] for e in eps], default=0.0),
                         score0=h['score0'], slot0=h.get('slot0', '?'), mask0=h['mask0'], d0=h['d0'], sess=h['sess'], split=h['split'],
                         tung_gan=h['tung_gan'], start_utc=pd.Timestamp(D['t'][h['start']]), eps=eps))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------------------- lên hạng (t_q)
def t_bar_after(D, start, minutes):
    m = D['mins']
    j = int(np.searchsorted(m, m[start] + minutes, side='left'))
    return j


def t_q_of(D, Z, rule):
    """Trả mảng t_q (nến lên hạng, −1 = không bao giờ). Mọi luật chỉ dùng thông tin ≤ t_q."""
    n = len(Z); out = np.full(n, -1, int)
    for r, z in enumerate(Z.itertuples(index=False)):
        tq = _tq_one(D, z, rule)
        if tq is not None and z.start <= tq <= z.end:
            out[r] = tq
    return out


def _tq_one(D, z, rule):
    kind = rule[0]
    if kind == 'all':
        return z.start
    if kind == 'age':
        return t_bar_after(D, z.start, rule[1])
    if kind == 'touch':          # ≥ k lần chạm bắt đầu SAU nến tạo (= n_cham_lai của tracker); lên hạng tại nến bắt đầu lần thứ k
        k = rule[1]; c = 0
        for e in z.eps:
            if e[0] > z.start:
                c += 1
                if c == k:
                    return e[0]
        return None
    if kind == 'dao':            # ≥ k lần chạm đã CHỐT là đảo chiều; lên hạng tại nến chốt (trễ G nến)
        k = rule[1]; c = 0
        for e in sorted(z.eps, key=lambda e: e[1]):
            if e[2] == 'đảo':
                c += 1
                if c == k:
                    return e[1]
        return None
    if kind == 'gan':
        return z.start if z.tung_gan else None
    if kind == 'and':
        ts = [_tq_one(D, z, r) for r in rule[1:]]
        return None if any(t is None for t in ts) else max(ts)
    if kind == 'or':
        ts = [t for t in (_tq_one(D, z, r) for r in rule[1:]) if t is not None]
        return min(ts) if ts else None
    raise ValueError(rule)


# ----------------------------------------------------------------------------------------------------------------- số đo
def load_signals(D, paths):
    idx = []
    for p in paths:
        if not os.path.exists(p):
            continue
        s = pd.read_csv(p)
        tt = pd.to_datetime(s['time_utc']).to_numpy()
        tt = tt[(tt >= D['t'][0]) & (tt <= D['t'][-1])]
        idx.extend(np.searchsorted(D['t'], tt).tolist())
    return np.array(sorted(set(idx)), int)


def screen_metrics(D, Z, tq, sig):
    """Số đo "gọn": khối đủ điều kiện, khối/phiên, khối trong 24 h, số khối đậm tại signal, khoảng cách tới khối gần nhất, phủ Display."""
    ok = tq >= 0
    starts = tq[ok]; ends = Z['end'].to_numpy()[ok]; lo = Z['lo'].to_numpy()[ok]; hi = Z['hi'].to_numpy()[ok]
    m = D['mins']; sess = D['sess']
    R = dict(pct=ok.mean() * 100, n=int(ok.sum()))
    cnt = np.bincount(sess[starts], minlength=sess[-1] + 1) if len(starts) else np.zeros(1)
    R['k_phien'] = (cnt.mean(), np.percentile(cnt, 90))
    ms, me = m[starts], m[ends]
    win = [int(((ms < s + 1440) & (me >= s)).sum()) for s in range(0, int(m[-1]) - 1440, 360)]
    R['k_24h'] = (np.percentile(win, 50), np.percentile(win, 90))
    # tại signal
    at = []; near = []; within5 = 0; within10 = 0; cov = 0; totD = 0; up5 = 0; dn5 = 0
    for i in sig:
        al = (starts <= i) & (ends >= i)
        at.append(int(al.sum()))
        c = D['C'][i]
        if al.any():
            d = np.maximum(np.maximum(lo[al] - c, c - hi[al]), 0.0)
            near.append(d.min()); within5 += d.min() <= 5; within10 += d.min() <= 10
            up5 += ((lo[al] > c) & (lo[al] - c <= 5)).any(); dn5 += ((hi[al] < c) & (c - hi[al] <= 5)).any()
        else:
            near.append(np.nan)
        for (zid, zl, zh, slot) in D['disp'].get(int(i), ()):
            totD += 1
            o = np.minimum(hi[al], zh) - np.maximum(lo[al], zl)
            rel = o / np.maximum(1e-9, np.minimum(hi[al] - lo[al], zh - zl))
            cov += bool((rel >= LS.LS_OVERLAP).any())
    at = np.array(at)
    R['sig'] = (at.mean(), np.percentile(at, 10), np.percentile(at, 90), np.nanmedian(near) if len(near) else np.nan,
                within5 / len(sig) * 100, within10 / len(sig) * 100, cov / max(1, totD) * 100, up5 / len(sig) * 100, dn5 / len(sig) * 100)
    return R


def strength(Z, tq):
    """Kết cục các lần chạm bắt đầu SAU t_q của khối đủ điều kiện: mọi lần / chỉ lần kế tiếp. Trả dict theo split."""
    out = {}
    for sp in ('TRAIN', 'TEST', 'GỘP'):
        c = collections.Counter(); nxt = collections.Counter(); nz = 0; nq = 0
        for z, t in zip(Z.itertuples(index=False), tq):
            if sp != 'GỘP' and z.split != sp:
                continue
            nz += 1
            if t < 0:
                continue
            nq += 1
            later = [e for e in z.eps if e[0] > t]
            for e in later:
                c[e[2]] += 1
            if later:
                nxt[later[0][2]] += 1
        out[sp] = dict(nz=nz, nq=nq, c=c, nxt=nxt)
    return out


def pct(c, key):
    n = sum(c.values())
    return (c[key] / n * 100) if n else np.nan


def dao_cls(c):
    d = c['đảo'] + c['xuyên']
    return (c['đảo'] / d * 100) if d else np.nan


# ------------------------------------------------------------------------------------------------------------- đối chứng
def fake_table(D, Z, kind, rng):
    """Khối giả: cùng rộng, cùng nến tạo, sống tối đa tới nến giết của khối thật (xuyên phá riêng thì kết thúc sớm hơn).
    'guong' = gương qua giá đóng lúc tạo (+ nhiễu ±0,5 giá) ⇒ cùng khoảng cách tới giá lúc tạo; 'doi' = dời cả bộ δ ∈ [3, 15] giá, dấu ngẫu nhiên theo phiên."""
    rows = []
    delta = {}
    for z in Z.itertuples(index=False):
        c0 = D['C'][z.start]; w = z.w
        if kind == 'guong':
            ctr = 2 * c0 - (z.lo + z.hi) / 2 + rng.uniform(-0.5, 0.5)
        else:
            if z.sess not in delta:
                delta[z.sess] = rng.uniform(3, 15) * rng.choice([-1, 1])
            ctr = (z.lo + z.hi) / 2 + delta[z.sess]
        lo, hi = ctr - w / 2, ctr + w / 2
        end, ly, vai, eps = simulate(D, lo, hi, z.start, z.kill)
        if ly != 'xuyên phá':
            end = z.end
        else:
            end = min(end, z.end)
        rows.append(dict(id=z.id, lo=lo, hi=hi, w=w, vai=vai, start=z.start, end=end, kill=z.kill, split=z.split, sess=z.sess,
                         tung_gan=z.tung_gan, n_ep=len(eps), n_dao=sum(e[2] == 'đảo' for e in eps), eps=eps,
                         d0=max(lo - c0, c0 - hi, 0.0), dur=D['mins'][end] - D['mins'][z.start]))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------------------------ in
def f1(x):
    return ('%.1f' % x).replace('.', ',') if x == x else '—'


def describe(D, Z, name):
    print(f'\n## Phân phối khối lịch sử — {name}: {len(Z)} khối, {Z.sess.nunique()} phiên')
    dur = Z.dur
    print(f'- Sống (phút): p25 {f1(dur.quantile(.25))} · p50 {f1(dur.median())} · p75 {f1(dur.quantile(.75))} · p90 {f1(dur.quantile(.9))}; '
          f'< 15 phút {f1((dur < 15).mean() * 100)}% · < 30 {f1((dur < 30).mean() * 100)}% · < 60 {f1((dur < 60).mean() * 100)}% · ≥ 120 {f1((dur >= 120).mean() * 100)}%')
    vc = Z.n_cham_lai.clip(upper=4).value_counts(normalize=True).sort_index() * 100
    print('- Số lần chạm lại (sau nến tạo): ' + ' · '.join(f'{int(k)}{"+" if k == 4 else ""} → {f1(v)}%' for k, v in vc.items())
          + f' (TB {f1(Z.n_cham_lai.mean())})')
    vc2 = Z.n_ep.clip(upper=4).value_counts(normalize=True).sort_index() * 100
    print('- Tổng lần chạm (kể cả lần ở nến tạo): ' + ' · '.join(f'{int(k)}{"+" if k == 4 else ""} → {f1(v)}%' for k, v in vc2.items()))
    print(f'- Kết thúc: ' + ' · '.join(f'{k} {f1(v)}%' for k, v in (Z.ly_do.value_counts(normalize=True) * 100).items()))
    tot = Z[['n_dao', 'n_xuyen', 'n_chuaro']].sum()
    print(f'- Kết cục mọi lần chạm trên khối: đảo {f1(tot.n_dao / tot.sum() * 100)}% · xuyên {f1(tot.n_xuyen / tot.sum() * 100)}% · chưa rõ {f1(tot.n_chuaro / tot.sum() * 100)}% (n={int(tot.sum())})')
    print(f'- Rộng (giá): p50 {f1(Z.w.median())} · p90 {f1(Z.w.quantile(.9))}; = 2 giá {f1((Z.w <= 2.0001).mean() * 100)}%')
    print(f'- Khoảng cách giá đóng → biên gần lúc tạo (giá): = 0 (giá trong vùng) {f1((Z.d0 == 0).mean() * 100)}% · p50 {f1(Z.d0.median())} · p90 {f1(Z.d0.quantile(.9))}')
    print(f'- Slot lúc tạo: ' + ' · '.join(f'{k} {f1(v)}%' for k, v in (Z.slot0.value_counts(normalize=True) * 100).items())
          + f'; từng gần {f1(Z.tung_gan.mean() * 100)}%; điểm lúc tạo p50 {f1(Z.score0.median())} · p90 {f1(Z.score0.quantile(.9))}')
    if (Z.mask0 >= 0).any():
        m = Z.mask0[Z.mask0 >= 0]
        print(f'- Loại mốc lúc tạo (mask, {len(m)} khối có): B {f1(((m & 1) > 0).mean() * 100)}% · B15 {f1(((m & 2) > 0).mean() * 100)}% · '
              f'C {f1(((m & 4) > 0).mean() * 100)}% · D {f1(((m & 8) > 0).mean() * 100)}%; chỉ D {f1((m == 8).mean() * 100)}%')
    rac = (Z.n_cham_lai == 0)
    print(f'- "Rác" = 0 lần chạm lại: {f1(rac.mean() * 100)}%; trong đó sống < 30 phút {f1((rac & (dur < 30)).mean() * 100)}% (của tổng); '
          f'0 chạm lại VÀ sống < 60 phút {f1((rac & (dur < 60)).mean() * 100)}%')
    # sống theo số lần chạm lại
    g = Z.groupby(Z.n_cham_lai.clip(upper=3)).dur.median()
    print('- Sống trung vị theo số lần chạm lại: ' + ' · '.join(f'{int(k)}{"+" if k == 3 else ""} → {f1(v)} phút' for k, v in g.items()))
    # thời điểm lần chạm lại thứ 1/2 kể từ tạo
    for k in (1, 2):
        d = [D['mins'][[e[0] for e in z.eps if e[0] > z.start][k - 1]] - D['mins'][z.start] for z in Z.itertuples(index=False) if z.n_cham_lai >= k]
        if d:
            print(f'- Lần chạm lại thứ {k} đến sau khi tạo: p50 {f1(np.median(d))} · p90 {f1(np.percentile(d, 90))} phút (n={len(d)})')
    # kết cục theo lần chạm thứ k trên khối (hình học)
    kk = collections.defaultdict(collections.Counter)
    for z in Z.itertuples(index=False):
        for j, e in enumerate(sorted(z.eps, key=lambda e: e[0])):
            kk[min(j + 1, 3)][e[2]] += 1
    print('- % đảo theo lần chạm thứ k trên khối: ' + ' · '.join(f'k={k}{"+" if k == 3 else ""}: {f1(pct(c, "đảo"))}% (xuyên {f1(pct(c, "xuyên"))}%, n={sum(c.values())})' for k, c in sorted(kk.items())))


def volume_section(D, Z, F, base):
    """Khối lượng footprint trong dải [lo, hi] suốt lần chạm (nến bắt đầu → nến chốt), chia cho khối lượng trung vị 50 nến trước nến bắt đầu
    (không nhìn trước) ⇒ 'cường độ'. % đảo theo tam phân vị cường độ (mốc cắt theo TRAIN), khối thật vs khối giả gương."""
    lv = pd.read_csv(base + '.csv', usecols=['bar_idx', 'price', 'volume'])
    b = lv['bar_idx'].to_numpy(); pr = lv['price'].to_numpy(float); vo = lv['volume'].to_numpy(float)
    o = np.argsort(b, kind='stable'); b, pr, vo = b[o], pr[o], vo[o]
    off = np.searchsorted(b, np.arange(D['n'] + 1))
    bv = pd.read_csv(base + '_bars.csv', usecols=['volume'])['volume'].to_numpy(float)
    med50 = pd.Series(bv).rolling(50, min_periods=10).median().shift(1).to_numpy()
    def inten(lo, hi, a, bb):
        s0, s1 = off[a], off[min(bb, D['n'] - 1) + 1]
        m = (pr[s0:s1] >= lo) & (pr[s0:s1] <= hi)
        base_v = med50[a] if med50[a] == med50[a] else np.nan
        return vo[s0:s1][m].sum() / max(1, bb - a + 1) / base_v if base_v and base_v > 0 else np.nan
    rows = []
    for tag, T in (('thật', Z), ('gương', F)):
        for z in T.itertuples(index=False):
            for e in z.eps:
                rows.append(dict(tag=tag, split=z.split, inten=inten(z.lo, z.hi, e[0], e[1]), ket=e[2]))
    E = pd.DataFrame(rows).dropna()
    cut = E[(E.tag == 'thật') & (E.split == 'TRAIN')].inten.quantile([1 / 3, 2 / 3]).to_numpy()
    E['terc'] = np.digitize(E.inten, cut)
    print(f'\n## Bảng D — khối lượng trong dải suốt lần chạm (÷ khối lượng trung vị 50 nến trước): mốc tam phân vị TRAIN {f1(cut[0])} / {f1(cut[1])}')
    print('| Tam phân vị cường độ | TRAIN thật % đảo (n) | TRAIN gương | TEST thật | TEST gương |')
    print('|---|---|---|---|---|')
    for t, name in ((0, 'thấp'), (1, 'giữa'), (2, 'cao')):
        cells = []
        for sp in ('TRAIN', 'TEST'):
            for tag in ('thật', 'gương'):
                g = E[(E.terc == t) & (E.split == sp) & (E.tag == tag)]
                c = collections.Counter(g.ket)
                cells.append(f'{f1(pct(c, "đảo"))} ({sum(c.values())})')
        print(f'| {name} | ' + ' | '.join(cells) + ' |')


def main():
    t0 = time.time()
    base, rp = LS.BASE90, os.path.join(REP, 'vcl5_cs_replay_v5.csv')
    D = load_ext(base, rp)
    allz = track_ext(D)
    Z = zone_table(D, allz)
    sigA = load_signals(D, [SIG_A]); sigAB = load_signals(D, [SIG_A, SIG_B])
    print(f'# loc_vung_bench — 90 ngày: {D["n"]} nến, {len(Z)} khối; signal A {len(sigA)} · A+B3 {len(sigAB)}; TRAIN {int((Z.split == "TRAIN").sum())} / TEST {int((Z.split == "TEST").sum())} khối')
    describe(D, Z, '90 ngày')
    for sp in ('TRAIN', 'TEST'):
        describe(D, Z[Z.split == sp].reset_index(drop=True), sp)
    Z.drop(columns=['eps']).assign(eps=Z.eps.apply(lambda e: ';'.join(f'{a}:{b}:{k[0]}:{p:.2f}' for a, b, k, p in e))).to_csv(
        os.path.join(REP, 'loc_vung_zones.csv'), index=False)

    rules = [
        ('tất cả (hiện nay)', ('all',)),
        ('từng gần (slot K/N)', ('gan',)),
        ('tuổi ≥ 30 phút', ('age', 30)),
        ('tuổi ≥ 60 phút', ('age', 60)),
        ('tuổi ≥ 120 phút', ('age', 120)),
        ('≥ 1 chạm lại', ('touch', 1)),
        ('≥ 2 chạm lại', ('touch', 2)),
        ('≥ 3 chạm lại', ('touch', 3)),
        ('≥ 1 đảo chiều đã chốt', ('dao', 1)),
        ('≥ 2 đảo chiều đã chốt', ('dao', 2)),
        ('≥ 1 chạm lại VÀ tuổi ≥ 30', ('and', ('touch', 1), ('age', 30))),
        ('≥ 1 chạm lại VÀ tuổi ≥ 60', ('and', ('touch', 1), ('age', 60))),
        ('≥ 2 chạm lại VÀ tuổi ≥ 60', ('and', ('touch', 2), ('age', 60))),
        ('≥ 2 chạm lại HOẶC tuổi ≥ 120', ('or', ('touch', 2), ('age', 120))),
        ('≥ 1 đảo chốt VÀ tuổi ≥ 60', ('and', ('dao', 1), ('age', 60))),
        ('≥ 1 chạm lại VÀ tuổi ≥ 45', ('and', ('touch', 1), ('age', 45))),
        ('≥ 1 đảo chốt HOẶC ≥ 2 chạm lại', ('or', ('dao', 1), ('touch', 2))),
        ('≥ 2 chạm lại HOẶC (≥ 1 chạm lại VÀ tuổi ≥ 120)', ('or', ('touch', 2), ('and', ('touch', 1), ('age', 120)))),
        ('≥ 1 chạm lại VÀ tuổi ≥ 60, HOẶC tuổi ≥ 180', ('or', ('and', ('touch', 1), ('age', 60)), ('age', 180))),
    ]
    TQ = {name: t_q_of(D, Z, r) for name, r in rules}

    age = []; nch = []
    for i in sigA:
        for z in Z.itertuples(index=False):
            if z.start <= i <= z.end:
                age.append(D['mins'][i] - D['mins'][z.start]); nch.append(sum(1 for e in z.eps if z.start < e[0] <= i))
    age = np.array(age); nch = np.array(nch)
    print(f'\n## Khối đang sống tại 163 nến signal A: {len(age)} khối-signal — tuổi p25 {f1(np.percentile(age, 25))} · p50 {f1(np.median(age))} · p75 {f1(np.percentile(age, 75))} phút; '
          f'tuổi < 30 phút {f1((age < 30).mean() * 100)}% · < 60 {f1((age < 60).mean() * 100)}%; số lần chạm lại đã có tới lúc đó: 0 → {f1((nch == 0).mean() * 100)}% · 1 → {f1((nch == 1).mean() * 100)}% · ≥ 2 → {f1((nch >= 2).mean() * 100)}%')
    print('\n## Bảng A — bộ lọc: gọn bao nhiêu, còn thấy gì tại signal (90 ngày; signal = 163 A; cột cuối = 163 A + 62 B3)')
    print('| Bộ lọc | % khối lên hạng | khối/phiên TB · p90 | khối/24 h p50 · p90 | khối đậm tại signal TB · p10 · p90 | phủ Display tại signal | cách khối gần nhất (p50, giá) | ≤ 5 giá / ≤ 10 giá | có KC ≤5 trên · HT ≤5 dưới | đậm tại signal A+B3 TB |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    SM = {}
    for name, r in rules:
        R = screen_metrics(D, Z, TQ[name], sigA); R2 = screen_metrics(D, Z, TQ[name], sigAB); SM[name] = R
        s = R['sig']
        print(f'| {name} | {f1(R["pct"])}% ({R["n"]}) | {f1(R["k_phien"][0])} · {R["k_phien"][1]:.0f} | {R["k_24h"][0]:.0f} · {R["k_24h"][1]:.0f} | '
              f'{f1(s[0])} · {s[1]:.0f} · {s[2]:.0f} | {f1(s[6])}% | {f1(s[3])} | {f1(s[4])}% / {f1(s[5])}% | {f1(s[7])}% · {f1(s[8])}% | {f1(R2["sig"][0])} |')

    # -------- đối chứng
    print(f'\n## Bảng B — "mạnh" có thật không: kết cục lần chạm SAU khi lên hạng, khối thật vs khối giả ({REPS} bản mỗi loại)')
    print('Khối giả GƯƠNG = cùng rộng, cùng nến tạo, cùng khoảng cách tới giá đóng lúc tạo (phản chiếu qua giá đóng, nhiễu ±0,5 giá), sống tối đa bằng khối thật;'
          ' khối giả DỜI = dời cả bộ 3–15 giá (dấu ngẫu nhiên theo phiên). Áp CÙNG bộ lọc cho khối giả.')
    rules_b = list(rules)
    if FAST:
        rules_b = rules[:1] + [r for r in rules if r[0] in ('≥ 1 chạm lại', '≥ 2 chạm lại', '≥ 1 đảo chiều đã chốt', '≥ 2 chạm lại VÀ tuổi ≥ 60')]
    real = {name: strength(Z, TQ[name]) for name, _ in rules_b}
    fakes = {'gương': [], 'dời': []}
    for kind, key in (('guong', 'gương'), ('doi', 'dời')):
        for rep in range(REPS):
            F = fake_table(D, Z, kind, RNG)
            fakes[key].append({name: strength(F, t_q_of(D, F, r)) for name, r in rules_b})
            print(f'  … đối chứng {key} bản {rep + 1}/{REPS} xong ({time.time() - t0:.0f} s)', file=sys.stderr)
    for sp in ('TRAIN', 'TEST'):
        print(f'\n### {sp}')
        print('| Bộ lọc | % khối lên hạng: thật · gương · dời | lần chạm sau lên hạng / khối: thật · gương · dời | % ĐẢO mọi lần sau: thật (n) · gương [5–95] · dời [5–95] | đảo/(đảo+xuyên): thật · gương · dời | % đảo LẦN KẾ TIẾP: thật (n) · gương · dời | % XUYÊN mọi lần sau: thật · gương · dời |')
        print('|---|---|---|---|---|---|---|')
        for name, _ in rules_b:
            r = real[name][sp]
            def agg(key, fn):
                v = np.array([fn(f[name][sp]) for f in fakes[key]], float)
                return v
            q = lambda v: f'{f1(np.nanmean(v))} [{f1(np.nanpercentile(v, 5))}–{f1(np.nanpercentile(v, 95))}]'
            fq = lambda s: s['nq'] / max(1, s['nz']) * 100
            fep = lambda s: sum(s['c'].values()) / max(1, s['nq'])
            print(f'| {name} | {f1(fq(r))} · {f1(agg("gương", fq).mean())} · {f1(agg("dời", fq).mean())} '
                  f'| {f1(fep(r))} · {f1(agg("gương", fep).mean())} · {f1(agg("dời", fep).mean())} '
                  f'| **{f1(pct(r["c"], "đảo"))}** ({sum(r["c"].values())}) · {q(agg("gương", lambda s: pct(s["c"], "đảo")))} · {q(agg("dời", lambda s: pct(s["c"], "đảo")))} '
                  f'| {f1(dao_cls(r["c"]))} · {q(agg("gương", lambda s: dao_cls(s["c"])))} · {q(agg("dời", lambda s: dao_cls(s["c"])))} '
                  f'| {f1(pct(r["nxt"], "đảo"))} ({sum(r["nxt"].values())}) · {q(agg("gương", lambda s: pct(s["nxt"], "đảo")))} · {q(agg("dời", lambda s: pct(s["nxt"], "đảo")))} '
                  f'| {f1(pct(r["c"], "xuyên"))} · {q(agg("gương", lambda s: pct(s["c"], "xuyên")))} · {q(agg("dời", lambda s: pct(s["c"], "xuyên")))} |')
    # mô tả khối giả gương: khớp khoảng cách & tuổi thọ?
    F = fake_table(D, Z, 'guong', np.random.default_rng(1))
    print(f'\nKiểm khớp đối chứng gương: d0 thật p50 {f1(Z.d0.median())} · giả {f1(F.d0.median())}; sống p50 thật {f1(Z.dur.median())} · giả {f1(F.dur.median())} phút; '
          f'chạm lại TB thật {f1(Z.n_ep.mean())} · giả {f1(F.n_ep.mean())} (mọi lần, kể cả nến tạo); ≥1 đảo thật {f1((Z.n_dao >= 1).mean() * 100)}% · giả {f1((F.n_dao >= 1).mean() * 100)}%')

    # -------- khối lượng tại vùng trong lần chạm (định nghĩa "mạnh" thứ 3)
    if not FAST:
        volume_section(D, Z, F, base)

    # -------- 29 ngày: chỉ bảng A cho vài bộ lọc
    rp29 = os.path.join(REP, 'vcl5_cs_replay_v5_29d.csv')
    if os.path.exists(rp29) and not FAST:
        D2 = load_ext(LS.BASE29, rp29); Z2 = zone_table(D2, track_ext(D2)); sig2 = load_signals(D2, [SIG_A])
        print(f'\n## Bảng C — đối chiếu file 29 ngày ({len(Z2)} khối, {len(sig2)} signal A)')
        print('| Bộ lọc | % khối lên hạng | khối/phiên TB | khối/24 h p50 · p90 | đậm tại signal TB · p90 | phủ Display tại signal | ≤ 5 giá |')
        print('|---|---|---|---|---|---|---|')
        for name, r in rules:
            R = screen_metrics(D2, Z2, t_q_of(D2, Z2, r), sig2); s = R['sig']
            print(f'| {name} | {f1(R["pct"])}% | {f1(R["k_phien"][0])} | {R["k_24h"][0]:.0f} · {R["k_24h"][1]:.0f} | {f1(s[0])} · {s[2]:.0f} | {f1(s[6])}% | {f1(s[4])}% |')
    print(f'\n(thời gian chạy {time.time() - t0:.0f} s)')


if __name__ == '__main__':
    main()
