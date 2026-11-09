# -*- coding: utf-8 -*-
"""
ĐO HỖ TRỢ / KHÁNG CỰ trên GCZ26 M1 (65 phiên) theo đúng 2 định nghĩa đã công bố:
  (O) Osler 2000  : "chạm" = giá tới trong ±g của mức từ một phía; "bật" = 15 nến sau, giá đóng vẫn ở phía cũ.
  (C) Chung&Bellotti 2021: dải [L-g, L+g]; vào từ một phía; "bật" = thoát ra cùng phía, "xuyên" = thoát phía kia (đóng nến),
      giới hạn 120 nến; không thoát = bỏ.
g = trung vị biên độ nến M1 50 nến (u) tại lúc chạm. Mọi mức tính KHÔNG nhìn trước.
Loại mức: swing (đỉnh/đáy k nến hai bên, hiệu lực 1 phiên = 1380 nến), đỉnh/đáy/đóng phiên trước, VA hôm qua (VAH/VAL/POC),
VA Âu (sau 19:00 VN), VWAP ngày/tuần, số tròn (bội 10 và 5 USD), ĐỐI CHỨNG = mức ngẫu nhiên trong biên phiên trước (50 lần).
Thêm: swing theo số lần bật trước đó (0/1/2+) và theo tuổi mức.
Chạy: python sr_measure.py  → in bảng + ghi report/SR-KET-QUA.md
"""
import sys, os, numpy as np, pandas as pd
sys.argv = ['x']
import kernel as K

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, '..', '..', 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260723-20261021_90d')
SWING_K = 5          # đỉnh/đáy: cao/thấp nhất trong k nến mỗi bên
LEVEL_LIFE = 1380    # nến (≈1 phiên)
OSLER_H = int(os.environ.get('SR_H', 15))         # nến
CHUNG_MAX = 120      # nến
RNG_REPS = 50
TOL_MULT = float(os.environ.get('SR_TOL', 1.0))       # g = TOL_MULT × u

df = K.load_bars(BASE + '_bars.csv')
prof = K.build_profiles(df, BASE + '.csv')
ctx = K._Ctx(df, prof)
zc = K.zone_columns(df, prof, ctx)
vw = K.vwap_series(df)
u = K.median_range(df).to_numpy()
n = len(df)
H, L, C, O = df['high'].to_numpy(), df['low'].to_numpy(), df['close'].to_numpy(), df['open'].to_numpy()
sess = df['session_no'].to_numpy()
ok_sess = ~(df['splice'].to_numpy() | df['thin'].to_numpy())
split = df['split'].to_numpy() if 'split' in df else np.array(['TRAIN'] * n)


def events_for_level(Lv, a, b, extra=None):
    """Tìm các lần CHẠM mức Lv trong [a,b): trả list (i, side, osler_bounce, chung_out, age). side=+1 mức là HỖ TRỢ (chạm từ trên)."""
    out = []
    i = max(a, 1)
    while i < min(b, n - 1):
        g = u[i] * TOL_MULT
        if g <= 0: i += 1; continue
        pc = C[i - 1]
        hit = None
        # VÀO DẢI BẰNG GIÁ ĐÓNG (Chung&Bellotti): nến trước đóng ngoài dải một phía, nến này đóng TRONG dải
        inside = abs(C[i] - Lv) <= g
        if inside and pc > Lv + g: hit = +1      # tới từ trên = mức làm HỖ TRỢ
        elif inside and pc < Lv - g: hit = -1    # tới từ dưới = KHÁNG CỰ
        if hit is None: i += 1; continue
        # Osler: 15 nến sau, đóng vẫn phía cũ (so với chính mức)
        j = i + OSLER_H
        os_b = None if j >= n else (C[j] > Lv if hit > 0 else C[j] < Lv)
        # Chung: thoát dải bằng giá đóng (cùng phía = bật, phía kia = xuyên)
        ch = None; k = i; react = np.nan
        for k in range(i + 1, min(i + CHUNG_MAX, n)):
            if sess[k] != sess[i]: break
            if hit > 0:
                if C[k] > Lv + g: ch = 1; break
                if C[k] < Lv - g: ch = 0; break
            else:
                if C[k] < Lv - g: ch = 1; break
                if C[k] > Lv + g: ch = 0; break
        if ch == 1:   # cỡ phản ứng: trong 30 nến sau khi bật, giá đi xa mức tối đa bao nhiêu u (theo chiều bật)
            seg = H[k:k + 30] if hit > 0 else L[k:k + 30]
            if len(seg): react = ((seg.max() - Lv) if hit > 0 else (Lv - seg.min())) / g
        out.append((i, hit, os_b, ch, i - a, react))
        # dedup: nhảy tới sau khi thoát dải
        i = max(k, i) + 1
    return out


def summarize(evts):
    o = [e[2] for e in evts if e[2] is not None]; c = [e[3] for e in evts if e[3] is not None]
    r = [e[5] for e in evts if e[3] == 1 and not np.isnan(e[5])]
    return dict(n_hit=len(evts), n_os=len(o), osler=np.mean(o) if o else np.nan, n_ch=len(c), chung=np.mean(c) if c else np.nan,
                react2u=np.mean(np.array(r) >= 2) if r else np.nan)


# ---------- 1. swing levels
piv = []  # (idx_confirm, level, kind)
for i in range(SWING_K, n - SWING_K):
    if H[i] == H[i - SWING_K:i + SWING_K + 1].max() and (H[i - SWING_K:i] < H[i]).all(): piv.append((i + SWING_K, H[i], 'high'))
    if L[i] == L[i - SWING_K:i + SWING_K + 1].min() and (L[i - SWING_K:i] > L[i]).all(): piv.append((i + SWING_K, L[i], 'low'))
swing_ev = []; swing_by_prev = {0: [], 1: [], 2: []}; swing_age = {'<=120': [], '121-480': [], '>480': []}
for (ic, Lv, kind) in piv:
    ev = events_for_level(Lv, ic + 1, min(n, ic + 1 + LEVEL_LIFE))
    prev_b = 0
    for e in ev:
        if not ok_sess[e[0]]: continue
        swing_ev.append(e)
        swing_by_prev[min(prev_b, 2)].append(e)
        age = e[4]; swing_age['<=120' if age <= 120 else ('121-480' if age <= 480 else '>480')].append(e)
        if e[3] == 1: prev_b += 1

# ---------- 2. mức theo phiên (prior session H/L/C, VA hôm qua, VA Âu, VWAP, số tròn)
st = K.session_table(df)
sess_ids = sorted(set(sess))
bounds = {s: (np.where(sess == s)[0][0], np.where(sess == s)[0][-1] + 1) for s in sess_ids}
prev_hlc = {}
for s in sess_ids:
    a, b = bounds[s]; prev_hlc[s] = (H[a:b].max(), L[a:b].min(), C[b - 1])
named = {k: [] for k in ['Đỉnh phiên trước', 'Đáy phiên trước', 'Đóng phiên trước', 'VAH hôm qua', 'VAL hôm qua', 'POC hôm qua',
                         'VAH Âu', 'VAL Âu', 'Số tròn 10$', 'Số tròn 5$']}
rand_ev = []
rng = np.random.default_rng(7)
for si, s in enumerate(sess_ids):
    if si == 0: continue
    a, b = bounds[s]
    if not ok_sess[a]: continue
    ph, pl, pcl = prev_hlc[sess_ids[si - 1]]
    for name, Lv in (('Đỉnh phiên trước', ph), ('Đáy phiên trước', pl), ('Đóng phiên trước', pcl)):
        named[name] += events_for_level(Lv, a, b)
    row = zc.iloc[a + 5] if a + 5 < b else zc.iloc[a]
    for name, col in (('VAH hôm qua', 'yd_vah'), ('VAL hôm qua', 'yd_val'), ('POC hôm qua', 'yd_poc')):
        v = row.get(col, np.nan)
        if pd.notna(v): named[name] += events_for_level(float(v), a, b)
    # VA Âu: chỉ sau khi chốt (cột eu_* có giá trị từ 19:00 VN)
    eu = zc.iloc[a:b]
    for name, col in (('VAH Âu', 'eu_vah'), ('VAL Âu', 'eu_val')):
        if col in eu:
            vals = eu[col].to_numpy(); valid = np.where(~np.isnan(vals))[0]
            if len(valid):
                named[name] += events_for_level(float(vals[valid[0]]), a + valid[0], b)
    # số tròn trong biên phiên trước ± 10
    lo, hi = pl - 10, ph + 10
    for Lv in np.arange(np.ceil(lo / 10) * 10, hi, 10): named['Số tròn 10$'] += events_for_level(float(Lv), a, b)
    for Lv in np.arange(np.ceil(lo / 5) * 5, hi, 5):
        if Lv % 10 != 0: named['Số tròn 5$'] += events_for_level(float(Lv), a, b)
    # đối chứng: mức ngẫu nhiên trong [pl-2, ph+2], 10 mức/phiên × RNG_REPS
    for _ in range(RNG_REPS):
        for Lv in rng.uniform(pl - 2, ph + 2, 10): rand_ev += events_for_level(float(Lv), a, b)

# VWAP động: mức đổi mỗi nến → chạm = low ≤ vwap+g khi đóng trước > vwap+g (gương cho kháng cự)
def dyn_events(series):
    v = series.to_numpy(); ev = []; i = 1
    while i < n - 1:
        if np.isnan(v[i]) or not ok_sess[i]: i += 1; continue
        g = u[i]; pc = C[i - 1]; hit = None
        inside = abs(C[i] - v[i]) <= g
        if inside and pc > v[i - 1] + g: hit = 1
        elif inside and pc < v[i - 1] - g: hit = -1
        if hit is None: i += 1; continue
        j = i + OSLER_H; os_b = None if j >= n or np.isnan(v[j]) else (C[j] > v[j] if hit > 0 else C[j] < v[j])
        ch = None; k = i
        for k in range(i + 1, min(i + CHUNG_MAX, n)):
            if sess[k] != sess[i] or np.isnan(v[k]): break
            if hit > 0:
                if C[k] > v[k] + u[k]: ch = 1; break
                if C[k] < v[k] - u[k]: ch = 0; break
            else:
                if C[k] < v[k] - u[k]: ch = 1; break
                if C[k] > v[k] + u[k]: ch = 0; break
        ev.append((i, hit, os_b, ch, 0, np.nan)); i = max(k, i) + 1
    return ev
named['VWAP ngày'] = dyn_events(vw['vwap_d']); named['VWAP tuần'] = dyn_events(vw['vwap_w'])

# ---------- bảng
rows = []
def add(name, ev):
    s = summarize(ev); rows.append(dict(Mức=name, **s))
add('Swing k=5 (tất cả)', swing_ev)
for k_, lab in ((0, 'Swing · chưa bật lần nào'), (1, 'Swing · đã bật 1 lần'), (2, 'Swing · đã bật ≥2 lần')): add(lab, swing_by_prev[k_])
for lab in ('<=120', '121-480', '>480'): add(f'Swing · tuổi {lab} nến', swing_age[lab])
for name in named: add(name, named[name])
add('ĐỐI CHỨNG mức ngẫu nhiên', rand_ev)
sm = df['sm'].to_numpy()
add('ĐỐI CHỨNG ngẫu nhiên · chỉ 19:00–04:00 VN', [e for e in rand_ev if sm[e[0]] >= 840 or sm[e[0]] < 0])
add('VAH+VAL Âu gộp', named['VAH Âu'] + named['VAL Âu'])
tab = pd.DataFrame(rows)
tab['osler'] = (tab['osler'] * 100).round(1); tab['chung'] = (tab['chung'] * 100).round(1); tab['react2u'] = (tab['react2u'] * 100).round(1)
# sai số chuẩn xấp xỉ cho Chung
tab['±(Chung)'] = (100 * np.sqrt(0.25 / tab['n_ch'].clip(lower=1))).round(1)

# tách TRAIN/TEST cho swing + đối chứng (Chung)
def half(ev, name):
    r = {}
    for h in ('TRAIN', 'TEST'):
        c = [e[3] for e in ev if e[3] is not None and split[e[0]] == h]
        r[h] = (len(c), round(100 * np.mean(c), 1) if c else np.nan)
    return name, r
halves = [half(swing_ev, 'Swing'), half(rand_ev, 'Ngẫu nhiên'), half(named['VWAP ngày'], 'VWAP ngày'), half(named['VWAP tuần'], 'VWAP tuần'),
          half(named['Đỉnh phiên trước'] + named['Đáy phiên trước'], 'Đỉnh/đáy phiên trước'), half(named['Số tròn 10$'], 'Số tròn 10$')]

md = ['# Hỗ trợ / kháng cự — đo trên GCZ26 M1, 65 phiên (2026-07-23 → 10-21)', '',
      'Định nghĩa đo (xem docstring `sr_measure.py`): **Osler** = 15 nến sau khi chạm, giá đóng vẫn phía cũ; **Chung** = vào dải ±u rồi thoát '
      'cùng phía (bật) hay phía kia (xuyên), theo giá đóng, tối đa 120 nến. u = trung vị biên độ M1 50 nến. Đối chứng = 10 mức ngẫu nhiên/phiên '
      f'trong biên phiên trước ±2 giá, lặp {RNG_REPS} lần. Nến ngẫu nhiên lý thuyết: Chung ≈ 50%.', '',
      '| Mức | n vào dải | Osler bật % | n (Chung) | Chung bật % | ± | bật rồi đi ≥2u % |', '|---|---|---|---|---|---|---|']
for _, r in tab.iterrows():
    md.append(f"| {r['Mức']} | {r['n_hit']} | {r['osler']} | {r['n_ch']} | {r['chung']} | {r['±(Chung)']} | {r['react2u']} |")
md += ['', '## Tách đôi thời gian (Chung bật %, n)', '', '| Mức | TRAIN ≤ 09-15 | TEST ≥ 09-16 |', '|---|---|---|']
for name, r in halves: md.append(f"| {name} | {r['TRAIN'][1]} (n={r['TRAIN'][0]}) | {r['TEST'][1]} (n={r['TEST'][0]}) |")
open(os.path.join(HERE, 'report', os.environ.get('SR_OUT', 'SR-KET-QUA.md')), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print('\n'.join(md))
