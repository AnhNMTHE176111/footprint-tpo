#!/usr/bin/env python3
"""QUÉT ĐẶC TRƯNG PER-LEVEL — không thiên vị, có kiểm chứng out-of-sample.

Ý tưởng: thay vì tin vào một tín hiệu (absorption) rồi tinh chỉnh, ta tính ~40 đặc trưng
per-level cho MỌI nến M1, chia nhóm theo quantile (ngưỡng lấy TỪ IN-SAMPLE), rồi đo edge
với 2 outcome. Chia thời gian: tháng 5-6 = in-sample, tháng 7 = out-of-sample.

Chạy:  python3 feature_hunt.py [--pkl data-export/27-7/perlevel_m1.pkl]

Outcome:
  A) REVERSAL (chỉ trên nến là cực trị cục bộ 10 nến): giá đi NGƯỢC đà cũ 1.0 USD
     trước khi đi tiếp 1.0 USD, trong 20 nến, ref = close nến tín hiệu. Timeout = miss.
  B) DIR20 trên MỌI nến: close[i+20] > close[i] ? (đo P(up); short = 1 - P(up))
  C) REV20 trên nến cực trị: close[i+20] đi ngược đà cũ ?
"""
import pickle, sys, math, os, statistics as st
from bisect import bisect_right
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARGS = sys.argv[1:]
PKL = (ARGS[ARGS.index('--pkl') + 1] if '--pkl' in ARGS
       else os.path.join(REPO, 'data-export/27-7/perlevel_m1_clean.pkl'))
SPLIT = ARGS[ARGS.index('--split') + 1] if '--split' in ARGS else 'mon'   # 'mon' | 'half'
MINVOL_ABS = 10.0          # nến mỏng hơn → per-level vô nghĩa
MINVOL_REL = 0.3           # ... hoặc < 0.3x median vol 100 nến
TICK = 0.1
TARGET_TICKS = 10          # 1.0 USD
HORIZON = 20
EXT_LOOKBACK = 10          # cực trị cục bộ 10 nến (nhân quả: 9 nến trước + nến hiện tại)
BASE_BARS = 100
MAX_GAP_S = 60 * 60        # bỏ tín hiệu nếu 20 nến tới vượt 60' (cắt qua nghỉ phiên)
MIN_N = 100

print(f"# nạp {PKL}")
bars = pickle.load(open(PKL, 'rb'))
N = len(bars)
for b in bars:
    b['ts'] = datetime.strptime(b['t'], '%Y-%m-%d %H:%M:%S').timestamp()
    b['mon'] = b['t'][:7]
print(f"  {N} nến, {bars[0]['t']} → {bars[-1]['t']}")

# CACHE SẠCH: chỉ thg 6-7 (thg 5 GCQ26 chưa là hợp đồng chính: median 5 lot/nến,
# 63% nến vol<10 → rác, và nó lại chính là nhóm "biến động thấp" → sinh edge giả).
# Chia kỳ: 'mon' = IS thg6 / OOS thg7.  'half' = nửa đầu / nửa sau chuỗi (thg6 hơi ít mẫu).
IS_MON = ('2026-06',)
OOS_MON = ('2026-07',)


# ────────────────────────────────────── CHẾ ĐỘ BIẾN ĐỘNG (chuẩn hoá target)
# Vol/nến TB: thg5≈26, thg6≈20, thg7≈73 → biến động chênh 3-4x. Target CỐ ĐỊNH 1 USD
# biến mọi đặc trưng dính biến động thành "có edge" giả. → target theo biến động.
mr100 = [None] * N              # median range (tick) của 100 nến TRƯỚC
mv100 = [None] * N              # median volume của 100 nến TRƯỚC
_rh, _vh = [], []
for i in range(N):
    mr100[i] = st.median(_rh) if len(_rh) >= 40 else None
    mv100[i] = st.median(_vh) if len(_vh) >= 40 else None
    _rh.append(max(1, bars[i]['hi_t'] - bars[i]['lo_t']))
    _vh.append(bars[i]['vol'])
    if len(_rh) > BASE_BARS:
        _rh.pop(0); _vh.pop(0)

# lọc nến quá mỏng — per-level không có nghĩa
elig = [False] * N
for i in range(N):
    if mv100[i] is None:
        continue
    elig[i] = bars[i]['vol'] >= max(MINVOL_ABS, MINVOL_REL * mv100[i])

if SPLIT == 'half':
    _cut = N // 2
    insample = [i < _cut for i in range(N)]
    oos = [i >= _cut for i in range(N)]
    SPLIT_DESC = f"nửa đầu (tới {bars[_cut-1]['t'][:10]}) vs nửa sau"
else:
    insample = [bars[i]['mon'] in IS_MON for i in range(N)]
    oos = [bars[i]['mon'] in OOS_MON for i in range(N)]
    SPLIT_DESC = "IS = thg6 / OOS = thg7"
print(f"  chia kỳ: {SPLIT_DESC};  nến đủ thanh khoản: {sum(elig)}/{N} "
      f"({sum(elig)/N*100:.0f}%)")


# ─────────────────────────────────────────────────────────── OUTCOME
def first_touch(i, up_first_target, dn_first_target):
    """Trả 'up' / 'dn' / 'both' / None: rào nào bị chạm TRƯỚC trong HORIZON nến.
    'both' = cùng một nến chạm cả hai → không biết thứ tự (đây chính là nguồn thiên lệch:
    nến biến động cao dễ 'both' → tỷ lệ đảo chiều bị DÌM xuống nếu coi both = miss)."""
    for j in range(i + 1, min(i + 1 + HORIZON, N)):
        hi_up = bars[j]['h'] >= up_first_target
        lo_dn = bars[j]['l'] <= dn_first_target
        if hi_up and lo_dn:
            return 'both'
        if hi_up:
            return 'up'
        if lo_dn:
            return 'dn'
    return None


ext = [0] * N          # +1 = đỉnh cục bộ, -1 = đáy cục bộ, 0 = không
for i in range(EXT_LOOKBACK - 1, N):
    win = bars[i - EXT_LOOKBACK + 1:i + 1]
    h, l = bars[i]['h'], bars[i]['l']
    is_top = h >= max(x['h'] for x in win)
    is_bot = l <= min(x['l'] for x in win)
    if is_top and not is_bot:
        ext[i] = 1
    elif is_bot and not is_top:
        ext[i] = -1

ok_fwd = [False] * N
for i in range(N):
    j = i + HORIZON
    if j < N and bars[j]['ts'] - bars[i]['ts'] <= MAX_GAP_S:
        ok_fwd[i] = True

outA = [None] * N        # target CỐ ĐỊNH 1 USD, both/timeout = miss  (cách đo CŨ, có thiên lệch)
outN = [None] * N        # target CHUẨN HOÁ 2x median-range-100, both/timeout = miss
outNc = [None] * N       # target chuẩn hoá, CHỈ tính ca phân định rõ (both/timeout = loại)
outB = [None] * N        # P(up) sau 20 nến (mọi nến)
outC = [None] * N        # close sau 20 nến đi ngược đà cũ? (nến cực trị)
res = [None] * N         # 'up'/'dn'/'both'/None với target chuẩn hoá
tgt_fix = TARGET_TICKS * TICK
for i in range(N):
    if not ok_fwd[i]:
        continue
    c = bars[i]['c']
    outB[i] = 1 if bars[i + HORIZON]['c'] > c else 0
    if ext[i] == 0 or mr100[i] is None:
        continue
    tg = max(2.0, 2.0 * mr100[i]) * TICK          # 2x biến động thường
    t_fix = first_touch(i, c + tgt_fix, c - tgt_fix)
    t_nrm = first_touch(i, c + tg, c - tg)
    res[i] = t_nrm
    rev = 'dn' if ext[i] == 1 else 'up'
    outA[i] = 1 if t_fix == rev else 0
    outN[i] = 1 if t_nrm == rev else 0
    if t_nrm in ('up', 'dn'):
        outNc[i] = 1 if t_nrm == rev else 0
    outC[i] = 1 if ((bars[i + HORIZON]['c'] < c) if ext[i] == 1
                    else (bars[i + HORIZON]['c'] > c)) else 0

print(f"  cực trị 10 nến: {sum(1 for x in ext if x)} nến "
      f"(đỉnh {sum(1 for x in ext if x == 1)}, đáy {sum(1 for x in ext if x == -1)})")


# ─────────────────────────────────────────────────────────── BASELINE ROBUST
def med_mad(vals):
    m = st.median(vals)
    mad = st.median([abs(v - m) for v in vals]) or 1e-9
    return m, 1.4826 * mad


cellvols_all, cellvols_top3 = [], []      # deque thủ công theo nến
hist_all, hist_top3 = [], []              # list[list[float]] mỗi nến 1 phần tử
base_all = [None] * N                     # (med, sd) từ 100 nến TRƯỚC
base_top3 = [None] * N
barvol_hist, barrange_hist = [], []
base_barvol = [None] * N
base_range = [None] * N

cache_all = cache_top3 = None
flat_all, flat_top3 = [], []
for i in range(N):
    if len(hist_all) >= 40:
        if i % 10 == 0 or cache_all is None:
            flat_all = [v for L in hist_all for v in L]
            flat_top3 = [v for L in hist_top3 for v in L]
            cache_all = med_mad(flat_all) if len(flat_all) >= 50 else None
            cache_top3 = med_mad(flat_top3) if len(flat_top3) >= 50 else None
        base_all[i], base_top3[i] = cache_all, cache_top3
        bv = [v for v in barvol_hist if v > 0]
        if i % 10 == 0 or base_barvol[i - 1] is None:
            _bvm = st.median(bv) if bv else None
            _rgm = st.median(barrange_hist) if barrange_hist else None
        else:
            _bvm, _rgm = base_barvol[i - 1], base_range[i - 1]
        base_barvol[i], base_range[i] = _bvm, _rgm
    lv = sorted((l[4] for l in bars[i]['lvls']), reverse=True)
    hist_all.append(lv)
    hist_top3.append(lv[:3])
    barvol_hist.append(bars[i]['vol'])
    barrange_hist.append(max(1, bars[i]['hi_t'] - bars[i]['lo_t']))
    if len(hist_all) > BASE_BARS:
        hist_all.pop(0); hist_top3.pop(0); barvol_hist.pop(0); barrange_hist.pop(0)
        cache_all = None if i % 10 else cache_all


# ─────────────────────────────────────────────────────────── ĐẶC TRƯNG
F = [dict() for _ in range(N)]

for i in range(N):
    b = bars[i]
    f = F[i]
    lvls = b['lvls']
    if not lvls:
        continue
    vol = b['vol'] or sum(l[4] for l in lvls)
    rng = b['hi_t'] - b['lo_t']
    n_lv = len(lvls)
    lo_t, hi_t = b['lo_t'], b['hi_t']
    sgn = 1 if ext[i] == 1 else (-1 if ext[i] == -1 else 0)

    # ---- hình dạng phân bố
    poc = max(lvls, key=lambda l: l[4])
    vols = sorted((l[4] for l in lvls), reverse=True)
    if rng > 0:
        pocpos = (poc[0] - lo_t) / rng
        f['poc_pos'] = pocpos
        if sgn:                                  # khoảng cách POC tới CỰC TRỊ của nến
            f['poc_dist_ext'] = (hi_t - poc[0]) / rng if sgn == 1 else (poc[0] - lo_t) / rng
    if vol > 0:
        f['poc_share'] = poc[4] / vol
    f['poc_prom'] = vols[0] / vols[1] if n_lv >= 2 and vols[1] > 0 else None
    tot = sum(vols) or 1.0
    p = [v / tot for v in vols if v > 0]
    ent = -sum(x * math.log(x) for x in p)
    f['entropy'] = ent
    f['entropy_norm'] = ent / math.log(n_lv) if n_lv >= 2 else None
    acc, n70 = 0.0, 0
    for v in vols:
        acc += v; n70 += 1
        if acc >= 0.7 * tot:
            break
    f['n70'] = n70
    f['n70_frac'] = n70 / n_lv
    f['n_lv'] = n_lv
    f['fill'] = n_lv / (rng + 1) if rng >= 0 else None      # mật độ ô có khớp

    # ---- imbalance chéo (ask[k] vs bid[k-1]) trên các ô liên tiếp về giá
    by_t = {l[0]: l for l in lvls}
    ticks = sorted(by_t)
    MINV = 4.0
    run_b = best_b = run_s = best_s = 0
    imb_b_pos, imb_s_pos = [], []
    for k in range(1, len(ticks)):
        t_hi, t_lo = ticks[k], ticks[k - 1]
        if t_hi - t_lo != 1:
            run_b = run_s = 0
            continue
        a_hi, b_lo = by_t[t_hi][3], by_t[t_lo][2]
        a_lo, b_hi = by_t[t_lo][3], by_t[t_hi][2]
        if a_hi >= 3 * b_lo and a_hi >= MINV:          # mua áp đảo
            run_b += 1; best_b = max(best_b, run_b)
            imb_b_pos.append((t_hi - lo_t) / rng if rng else 0.5)
        else:
            run_b = 0
        if b_lo >= 3 * a_hi and b_lo >= MINV:          # bán áp đảo (nhìn ngược chéo)
            run_s += 1; best_s = max(best_s, run_s)
            imb_s_pos.append((t_lo - lo_t) / rng if rng else 0.5)
        else:
            run_s = 0
    f['imb_buy_run'] = best_b
    f['imb_sell_run'] = best_s
    f['imb_run_max'] = max(best_b, best_s)
    f['imb_n'] = len(imb_b_pos) + len(imb_s_pos)
    if sgn:
        # run NGƯỢC đà (đỉnh → run bán; đáy → run mua) = tín hiệu đảo chiều
        f['imb_run_against'] = best_s if sgn == 1 else best_b
        f['imb_run_with'] = best_b if sgn == 1 else best_s
        pos_w = imb_b_pos if sgn == 1 else imb_s_pos
        f['imb_with_pos'] = st.mean(pos_w) if pos_w else None

    # ---- unfinished business tại cực trị
    hl, ll = by_t.get(hi_t), by_t.get(lo_t)
    if hl:
        f['ub_hi_both'] = 1 if (hl[2] > 0 and hl[3] > 0) else 0
        f['ub_hi_bid'] = 1 if hl[2] > 0 else 0              # đỉnh soi Bid (đ/n gốc)
        f['dlt_hi'] = (hl[3] - hl[2]) / hl[4] if hl[4] > 0 else None
        f['vol_hi_share'] = hl[4] / vol if vol > 0 else None
    if ll:
        f['ub_lo_both'] = 1 if (ll[2] > 0 and ll[3] > 0) else 0
        f['ub_lo_ask'] = 1 if ll[3] > 0 else 0              # đáy soi Ask (đ/n gốc)
        f['dlt_lo'] = (ll[3] - ll[2]) / ll[4] if ll[4] > 0 else None
        f['vol_lo_share'] = ll[4] / vol if vol > 0 else None
    if hl and ll:
        f['ub_any'] = 1 if (f.get('ub_hi_both') or f.get('ub_lo_both')) else 0
    if sgn and hl and ll:
        e = hl if sgn == 1 else ll
        f['dlt_ext'] = (e[3] - e[2]) / e[4] if e[4] > 0 else None   # delta ô cực trị
        f['ub_ext_both'] = 1 if (e[2] > 0 and e[3] > 0) else 0
        f['ub_ext_orig'] = 1 if ((e[2] > 0) if sgn == 1 else (e[3] > 0)) else 0
        f['vol_ext_share'] = e[4] / vol if vol > 0 else None

    # ---- ô delta ngược dấu nến (hấp thụ cục bộ)
    d_bar = b['delta']
    s_bar = 1 if d_bar > 0 else (-1 if d_bar < 0 else 0)
    if s_bar and vol > 0:
        opp = 0.0; mx = 0.0
        for l in lvls:
            d = l[3] - l[2]
            if d * s_bar < 0:
                opp += abs(d); mx = max(mx, abs(d))
        f['opp_share'] = opp / vol
        f['opp_max_share'] = mx / vol
    f['delta_ratio'] = d_bar / vol if vol > 0 else None
    if sgn:
        f['delta_against'] = (-d_bar / vol * sgn) if vol > 0 else None   # >0 = delta ngược đà

    # ---- cường độ
    ba, bt = base_all[i], base_top3[i]
    if ba:
        m, sd = ba
        f['zmax_all'] = (vols[0] - m) / sd if sd > 0 else None
        f['zcnt3_all'] = sum(1 for v in vols if sd > 0 and (v - m) / sd >= 3)
        if sgn and hl and ll:
            e = hl if sgn == 1 else ll
            f['z_ext_all'] = (e[4] - m) / sd if sd > 0 else None
            f['z_poc_at_ext'] = 1 if poc[0] == (hi_t if sgn == 1 else lo_t) else 0
    if bt:
        m, sd = bt
        f['zmax_top3'] = (vols[0] - m) / sd if sd > 0 else None
        f['zcnt3_top3'] = sum(1 for v in vols if sd > 0 and (v - m) / sd >= 3)
    if base_barvol[i]:
        f['barvol_rel'] = vol / base_barvol[i]
    if base_range[i]:
        f['range_rel'] = max(1, rng) / base_range[i]
    if vol > 0:
        f['impact'] = abs(b['c'] - b['o']) / vol * 100
        f['rng_per_vol'] = rng / vol
        f['effort_result'] = vol / max(1, rng)               # nhiều vol ít range = hấp thụ
    if rng > 0:
        f['close_pos'] = (b['c'] - b['l']) / (rng * TICK)
        if sgn:
            f['close_rej'] = (1 - (b['c'] - b['l']) / (rng * TICK)) if sgn == 1 \
                             else (b['c'] - b['l']) / (rng * TICK)   # close xa cực trị
            f['wick_ext'] = (b['h'] - max(b['o'], b['c'])) / (rng * TICK) if sgn == 1 \
                            else (min(b['o'], b['c']) - b['l']) / (rng * TICK)

    # ---- vị trí ngữ cảnh
    if i >= 60:
        w = bars[i - 60:i]
        h60 = max(x['h'] for x in w); l60 = min(x['l'] for x in w)
        f['dist_ext60'] = (b['h'] - h60) / TICK if sgn == 1 else (l60 - b['l']) / TICK if sgn == -1 else None
        f['pos_in_60'] = (b['c'] - l60) / (h60 - l60) if h60 > l60 else None
    if i >= 8 and i + 8 < N:
        pass   # swing 9 tâm cần tương lai → bỏ (không nhân quả)
    f['is_ext'] = 1 if ext[i] else 0


    f['volreg'] = mr100[i]                 # chế độ biến động (median range 100 nến)
    if mr100[i]:
        f['n_lv_rel'] = n_lv / mr100[i]    # số ô CHUẨN HOÁ theo biến động


# ══════════════════════════════════════════════════════════════════════════════
#  ĐO EDGE — 3 tầng chống nhiễu
#   T1: target CHUẨN HOÁ theo biến động (2x median-range-100) + tách ca 'both'
#   T2: bin/quantile n>=500, kiểm ĐƠN ĐIỆU, không đi tìm ngưỡng đẹp
#   T3: khớp nhóm biến động — chia 4 quartile volreg, bin LẠI TRONG từng nhóm,
#       đặc trưng chỉ đáng tin nếu dấu edge giữ ở >=3/4 nhóm ở CẢ IS và OOS
# ══════════════════════════════════════════════════════════════════════════════
def se(n):
    return math.sqrt(0.25 / n) * 100


def rate(idxs, out):
    v = [out[i] for i in idxs if out[i] is not None]
    if not v:
        return 0, float('nan'), float('nan')
    return len(v), sum(v) / len(v) * 100, se(len(v))


def qcuts(vals, k):
    v = sorted(vals)
    cs = []
    for j in range(1, k):
        c = v[int(len(v) * j / k)]
        if not cs or c > cs[-1]:
            cs.append(c)
    return cs


def binify(idxs, feat, k):
    """chia idxs thành <=k bin theo quantile của CHÍNH idxs (dùng cho IS hoặc trong-quartile)"""
    vals = [F[i][feat] for i in idxs]
    cs = qcuts(vals, k)
    out = [[] for _ in range(len(cs) + 1)]
    for i in idxs:
        out[bisect_right(cs, F[i][feat])].append(i)
    return cs, out


samples_ext = [i for i in range(N) if outN[i] is not None and elig[i]]
samples_all = [i for i in range(N) if outB[i] is not None and elig[i]]
IS_ext = [i for i in samples_ext if insample[i]]
OO_ext = [i for i in samples_ext if oos[i]]
IS_all = [i for i in samples_all if insample[i]]
OO_all = [i for i in samples_all if oos[i]]

print(f"\n  mẫu cực trị đủ điều kiện: {len(samples_ext)} (IS {len(IS_ext)} / OOS {len(OO_ext)})")
print(f"  mẫu mọi nến: {len(samples_all)} (IS {len(IS_all)} / OOS {len(OO_all)})")
print("\n  BASE RATE theo cách đo:")
for nm, o, s in (('REV 1USD cố định (cũ)', outA, samples_ext),
                 ('REV chuẩn hoá 2xATR', outN, samples_ext),
                 ('REV chuẩn hoá, ca rõ', outNc, samples_ext),
                 ('REV20 theo close', outC, samples_ext),
                 ('P(up) 20 nến', outB, samples_all)):
    r = rate(s, o)
    r1 = rate([i for i in s if insample[i]], o)
    r2 = rate([i for i in s if oos[i]], o)
    print(f"    {nm:24s} n={r[0]:6d} {r[1]:5.1f}%  | IS {r1[1]:5.1f}% ({r1[0]}) OOS {r2[1]:5.1f}% ({r2[0]})")
print("  biến động (median range tick 100 nến): "
      + " ".join(f"{m}={st.median([mr100[i] for i in samples_ext if bars[i]['mon']==m]):.0f}"
                 for m in ('2026-06', '2026-07')))

# ─────────────────── PHẦN 0: CHỨNG MINH THIÊN LỆCH CỦA TARGET CỐ ĐỊNH
print(f"\n{'='*118}\nPHẦN 0 — TARGET CỐ ĐỊNH 1 USD TẠO EDGE GIẢ NHƯ THẾ NÀO (bin theo n_lv, cả mẫu)\n{'='*118}")
print(f"{'bin n_lv':14s} {'n':>6s} {'REV_1USD':>9s} {'both%':>7s} {'timeout%':>9s} "
      f"{'REV_norm':>9s} {'both_n%':>8s} {'to_n%':>7s} {'REV_ca_rõ':>10s} {'volreg':>7s}")
cs, bins = binify([i for i in samples_ext if F[i].get('n_lv')], 'n_lv', 6)
for k, bn in enumerate(bins):
    if len(bn) < 200:
        continue
    lo = f"{cs[k-1]:g}" if k else "min"
    hi = f"{cs[k]:g}" if k < len(cs) else "max"
    both_f = sum(1 for i in bn if first_touch(i, bars[i]['c'] + tgt_fix, bars[i]['c'] - tgt_fix) == 'both')
    to_f = sum(1 for i in bn if first_touch(i, bars[i]['c'] + tgt_fix, bars[i]['c'] - tgt_fix) is None)
    both_n = sum(1 for i in bn if res[i] == 'both')
    to_n = sum(1 for i in bn if res[i] is None)
    print(f"[{lo:>5s},{hi:>5s})  {len(bn):6d} {rate(bn,outA)[1]:8.1f}% {both_f/len(bn)*100:6.1f}% "
          f"{to_f/len(bn)*100:8.1f}% {rate(bn,outN)[1]:8.1f}% {both_n/len(bn)*100:7.1f}% "
          f"{to_n/len(bn)*100:6.1f}% {rate(bn,outNc)[1]:9.1f}% "
          f"{st.median([mr100[i] for i in bn]):7.0f}")

# ─────────────────── PHẦN 1: QUÉT BIN + ĐƠN ĐIỆU + OOS
OUTCOMES = [('REVnorm', outN, 'ext'), ('REVrõ', outNc, 'ext'),
            ('REV20c', outC, 'ext'), ('P(up)20', outB, 'all')]
MINBIN = 500
SCAN = []
FEATS = sorted({k for f in F for k in f})

for feat in FEATS:
    for lab, out, dom in OUTCOMES:
        base_is = IS_ext if dom == 'ext' else IS_all
        base_oo = OO_ext if dom == 'ext' else OO_all
        I = [i for i in base_is if F[i].get(feat) is not None and out[i] is not None]
        O = [i for i in base_oo if F[i].get(feat) is not None and out[i] is not None]
        if len(I) < 3 * MINBIN or len(O) < 3 * MINBIN:
            continue
        k = max(2, min(5, len(I) // MINBIN, len(O) // MINBIN))
        cs, bI = binify(I, feat, k)
        if len(bI) < 2:
            continue
        bO = [[] for _ in bI]
        for i in O:
            bO[bisect_right(cs, F[i][feat])].append(i)
        rI = [rate(b, out) for b in bI]
        rO = [rate(b, out) for b in bO]
        if any(r[0] < 200 for r in rI) or any(r[0] < 200 for r in rO):
            continue
        bs_i, bs_o = rate(I, out), rate(O, out)
        sp_i = rI[-1][1] - rI[0][1]
        sp_o = rO[-1][1] - rO[0][1]
        z_i = sp_i / math.sqrt(rI[-1][2] ** 2 + rI[0][2] ** 2)
        z_o = sp_o / math.sqrt(rO[-1][2] ** 2 + rO[0][2] ** 2)
        steps = [rI[j + 1][1] - rI[j][1] for j in range(len(rI) - 1)]
        viol = sum(1 for s_ in steps if s_ * sp_i < 0)
        SCAN.append(dict(feat=feat, out=lab, cs=cs, rI=rI, rO=rO, bi=bs_i, bo=bs_o,
                         sp_i=sp_i, sp_o=sp_o, z_i=z_i, z_o=z_o, viol=viol, k=len(rI)))


def prof(r):
    return " ".join(f"{x[1]:4.1f}" for x in r)


def show(rows, title):
    print(f"\n{'='*118}\n{title}\n{'='*118}")
    if not rows:
        print("  (không có)"); return
    print(f"{'feature':16s} {'outcome':8s} {'hit theo bin IS (thấp→cao)':27s} {'base':>5s} "
          f"{'zsp':>5s} | {'hit theo bin OOS':27s} {'base':>5s} {'zsp':>5s} {'viol':>4s}")
    for r in rows:
        print(f"{r['feat']:16s} {r['out']:8s} {prof(r['rI']):27s} {r['bi'][1]:5.1f} {r['z_i']:+5.2f} | "
              f"{prof(r['rO']):27s} {r['bo'][1]:5.1f} {r['z_o']:+5.2f} {r['viol']:4d}")


cand = [r for r in SCAN if r['z_i'] * r['z_o'] > 0
        and min(abs(r['z_i']), abs(r['z_o'])) >= 2.0 and r['viol'] <= 1]
cand.sort(key=lambda r: -min(abs(r['z_i']), abs(r['z_o'])))
show(cand, "PHẦN 1 — ỨNG VIÊN: spread bin cùng dấu, |z|>=2 CẢ IS+OOS, gần đơn điệu (<=1 vi phạm)")

nope = [r for r in SCAN if r not in cand]
nope.sort(key=lambda r: -max(abs(r['z_i']), abs(r['z_o'])))
show([r for r in nope if max(abs(r['z_i']), abs(r['z_o'])) >= 2.5][:22],
     "PHẦN 1b — TỰ LOẠI: mạnh 1 phía nhưng đổi dấu / không đơn điệu ở phía kia (top 22)")

# ─────────────────── PHẦN 2: KHỚP NHÓM BIẾN ĐỘNG (T3)
print(f"\n{'='*118}\nPHẦN 2 — KHỚP NHÓM BIẾN ĐỘNG: bin lại TRONG từng quartile volreg (4 bin/nhóm)\n"
      f"         báo spread (bin cao - bin thấp) từng nhóm. Đáng tin = cùng dấu >=3/4 nhóm ở CẢ 2 kỳ.\n{'='*118}")
vq = qcuts([mr100[i] for i in samples_ext if mr100[i]], 4)
print(f"  ngưỡng quartile biến động (tick): {[f'{c:g}' for c in vq]}")
print(f"\n{'feature':16s} {'outcome':8s} {'spread IS theo Q1..Q4':28s} {'spread OOS theo Q1..Q4':28s} {'kết luận'}")
CONF = []
for r in cand:
    feat, lab = r['feat'], r['out']
    out = dict((o[0], o[1]) for o in OUTCOMES)[lab]
    dom = dict((o[0], o[2]) for o in OUTCOMES)[lab]
    sp = {'IS': [], 'OOS': []}
    for tag, base in (('IS', IS_ext if dom == 'ext' else IS_all),
                      ('OOS', OO_ext if dom == 'ext' else OO_all)):
        for q in range(4):
            sub = [i for i in base if F[i].get(feat) is not None and out[i] is not None
                   and mr100[i] is not None and bisect_right(vq, mr100[i]) == q]
            if len(sub) < 600:
                sp[tag].append(None); continue
            _, bb = binify(sub, feat, 4)
            if len(bb) < 2 or min(len(x) for x in bb) < 100:
                sp[tag].append(None); continue
            sp[tag].append(rate(bb[-1], out)[1] - rate(bb[0], out)[1])
    ok = 0
    for tag in ('IS', 'OOS'):
        good = sum(1 for x in sp[tag] if x is not None and x * r['sp_i'] > 0)
        tot = sum(1 for x in sp[tag] if x is not None)
        ok += 1 if tot >= 3 and good >= max(3, tot - 1) else 0
    verdict = "GIỮ (đứng vững mọi chế độ)" if ok == 2 else ("một phía" if ok == 1 else "LOẠI (chỉ do biến động)")
    if ok == 2:
        CONF.append(r)
    f_ = lambda L: " ".join((f"{x:+5.1f}" if x is not None else "  n/a") for x in L)
    print(f"{feat:16s} {lab:8s} {f_(sp['IS']):28s} {f_(sp['OOS']):28s} {verdict}")

print(f"\n{'='*118}\nKẾT LUẬN\n{'='*118}")
print(f"  đo {len(SCAN)} cặp (đặc trưng × outcome) bằng bin lớn; "
      f"{len(cand)} qua tầng OOS+đơn điệu; {len(CONF)} qua tiếp tầng khớp biến động.")
if CONF:
    for r in CONF:
        print(f"   ★ {r['feat']:16s} {r['out']:8s} bin IS {prof(r['rI'])} (base {r['bi'][1]:.1f}) | "
              f"OOS {prof(r['rO'])} (base {r['bo'][1]:.1f})")
else:
    print("   ★ KHÔNG đặc trưng nào qua đủ 3 tầng.")
dead = sorted({f_ for f_ in FEATS} - {r['feat'] for r in cand})
print(f"\n  KHÔNG CÓ EDGE ({len(dead)}): " + ", ".join(dead))


# ══════════════════════════════════════════════════════════════════════════════
# PHẦN 3 — SOI KỸ ỨNG VIÊN DUY NHẤT QUA CẢ 2 KIỂU CHIA KỲ: zmax_top3
#   zmax_top3 = (volume ô lớn nhất của nến − median) / (1.4826·MAD)
#               với median/MAD lấy từ TOP-3 ô của 100 nến trước.
#   Kiểm: (a) ngưỡng thật + n, (b) ổn định qua 3 block thời gian,
#         (c) còn tác dụng TRONG từng tercile volume nến? (per-level thêm gì ngoài OHLCV)
#         (d) đỉnh vs đáy, (e) so với zmax_all / z_ext_all (họ hàng).
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n\n{'#'*118}\n# PHẦN 3 — SOI KỸ zmax_top3\n{'#'*118}")
BLOCKS = [('thg6', lambda i: bars[i]['mon'] == '2026-06'),
          ('thg7-đầu', lambda i: bars[i]['mon'] == '2026-07' and bars[i]['t'][8:10] <= '13'),
          ('thg7-cuối', lambda i: bars[i]['mon'] == '2026-07' and bars[i]['t'][8:10] > '13')]

for feat in ('zmax_top3', 'zmax_all', 'z_ext_all'):
    S = [i for i in samples_ext if F[i].get(feat) is not None]
    cs, bins = binify(S, feat, 5)
    print(f"\n--- {feat}: ngưỡng quintile = {[f'{c:.2f}' for c in cs]}")
    print(f"{'bin':16s} {'n':>5s} {'REVnorm':>8s} {'±se':>5s} {'REVrõ':>7s} "
          + " ".join(f"{b[0]:>11s}" for b in BLOCKS))
    for k, bn in enumerate(bins):
        lo = f"{cs[k-1]:.2f}" if k else "-inf"
        hi = f"{cs[k]:.2f}" if k < len(cs) else "+inf"
        r = rate(bn, outN)
        rc = rate(bn, outNc)
        blk = []
        for nm, pr in BLOCKS:
            rb = rate([i for i in bn if pr(i)], outN)
            blk.append(f"{rb[1]:5.1f}%({rb[0]:4d})" if rb[0] >= 100 else "     n/a   ")
        print(f"[{lo:>6s},{hi:>6s}) {r[0]:5d} {r[1]:7.1f}% {r[2]:5.1f} {rc[1]:6.1f}% " + " ".join(blk))
    bb = rate(S, outN)
    print(f"  base toàn mẫu: {bb[1]:.1f}% (n={bb[0]});  " + "  ".join(
        f"{nm}: {rate([i for i in S if pr(i)], outN)[1]:.1f}%" for nm, pr in BLOCKS))

print("\n--- (c) zmax_top3 CÒN TÁC DỤNG TRONG TỪNG TERCILE volume nến? (REVnorm)")
S = [i for i in samples_ext if F[i].get('zmax_top3') is not None and F[i].get('barvol_rel') is not None]
vc = qcuts([F[i]['barvol_rel'] for i in S], 3)
zc = qcuts([F[i]['zmax_top3'] for i in S], 3)
print(f"    ngưỡng barvol_rel: {[f'{c:.2f}' for c in vc]} | ngưỡng zmax_top3: {[f'{c:.2f}' for c in zc]}")
print(f"    {'':14s}" + "".join(f"{'z_low':>14s}{'z_mid':>14s}{'z_high':>14s}"[:42] for _ in range(1)))
for q in range(3):
    row = []
    for z in range(3):
        g_ = [i for i in S if bisect_right(vc, F[i]['barvol_rel']) == q
              and bisect_right(zc, F[i]['zmax_top3']) == z]
        r = rate(g_, outN)
        row.append(f"{r[1]:5.1f}%(n={r[0]:4d})")
    print(f"    vol_t{q+1:d}      " + " ".join(row))

print("\n--- (d) tách ĐỈNH / ĐÁY, nhóm zmax_top3 cao nhất (>= quintile 4) vs base")
zq = qcuts([F[i]['zmax_top3'] for i in samples_ext if F[i].get('zmax_top3') is not None], 5)
TH = zq[-1]
print(f"    ngưỡng dùng: zmax_top3 >= {TH:.2f}")
for side, lab in ((1, 'ĐỈNH'), (-1, 'ĐÁY')):
    for nm, pr in BLOCKS:
        s_ = [i for i in samples_ext if ext[i] == side and pr(i) and F[i].get('zmax_top3') is not None]
        hi = rate([i for i in s_ if F[i]['zmax_top3'] >= TH], outN)
        print(f"    {lab:5s} {nm:10s} nhóm cao n={hi[0]:4d} {hi[1]:5.1f}%±{hi[2]:.1f} "
              f"| base {rate(s_, outN)[1]:5.1f}% (n={rate(s_, outN)[0]})")

print("\n--- (e) NGƯỠNG THỰC DỤNG cho indicator: zmax_top3 >= X → REVnorm, mọi block")
for X in (2, 3, 4, 5, 6, 8):
    row = []
    for nm, pr in BLOCKS:
        s_ = [i for i in samples_ext if pr(i) and F[i].get('zmax_top3') is not None]
        g_ = [i for i in s_ if F[i]['zmax_top3'] >= X]
        r = rate(g_, outN)
        b_ = rate(s_, outN)
        row.append(f"{nm} n={r[0]:4d} {r[1]:5.1f}% (base {b_[1]:4.1f}%, +{r[1]-b_[1]:+4.1f}pp)")
    print(f"  X={X:<2d} " + " | ".join(row))


# ══════════════════════════════════════════════════════════════════════════════
# PHẦN 4 — GIÁ TRỊ TĂNG THÊM so với VOLUME NẾN (OHLCV thuần)
#   Trong TỪNG quintile barvol_rel: spread (tercile cao − tercile thấp) của đặc trưng.
#   Nếu spread teo lại gần 0 → đặc trưng chỉ là proxy của volume nến, per-level vô ích.
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n\n{'#'*118}\n# PHẦN 4 — PER-LEVEL CÓ THÊM GÌ NGOÀI VOLUME NẾN?\n{'#'*118}")
for feat, out, lab, dom in (('zmax_top3', outN, 'REVnorm', 'ext'),
                            ('zmax_all', outN, 'REVnorm', 'ext'),
                            ('entropy', outB, 'P(up)20', 'all'),
                            ('n_lv', outB, 'P(up)20', 'all'),
                            ('poc_share', outN, 'REVnorm', 'ext')):
    S = [i for i in (samples_ext if dom == 'ext' else samples_all)
         if F[i].get(feat) is not None and F[i].get('barvol_rel') is not None and out[i] is not None]
    vq5 = qcuts([F[i]['barvol_rel'] for i in S], 5)
    print(f"\n--- {feat} → {lab} (n={len(S)}); ngưỡng barvol_rel: {[f'{c:.2f}' for c in vq5]}")
    for tag, sel in (('IS ', insample), ('OOS', oos)):
        cells = []
        for q in range(5):
            sub = [i for i in S if sel[i] and bisect_right(vq5, F[i]['barvol_rel']) == q]
            if len(sub) < 400:
                cells.append("      n/a  "); continue
            tc = qcuts([F[i][feat] for i in sub], 3)
            lo_ = [i for i in sub if bisect_right(tc, F[i][feat]) == 0]
            hi_ = [i for i in sub if bisect_right(tc, F[i][feat]) == len(tc)]
            if min(len(lo_), len(hi_)) < 120:
                cells.append("      n/a  "); continue
            d = rate(hi_, out)[1] - rate(lo_, out)[1]
            cells.append(f"{d:+6.1f}pp(n{min(len(lo_),len(hi_)):4d})")
        print(f"    {tag} theo quintile vol: " + " ".join(cells))
