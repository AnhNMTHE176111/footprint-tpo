"""Tự kiểm phần chấm (PLAN bước 2). In ĐẠT / TRƯỢT từng mục và ghi out_r1_dot_selftest.txt.
(a) ví dụ nhỏ tự dựng cho từng phương án, kết quả tính tay ghi ngay trong script;
(b) bản nhanh (evaluate) = bản chuẩn từng nến (ref_run) trên GC M5 và NQ M15, 10 ngày giao dịch đầu, mỗi phương án ít nhất một cấu hình;
(c) không nhìn tương lai: cắt dữ liệu tại một nến rồi chạy lại, mọi ngưỡng / vượt / chấm trước điểm cắt phải y hệt;
(d) mốc đối chứng "luật đang chạy" ra lại đúng số chuẩn cũ (GC M1 Không sót sàn 5 = 80.386; Ít nhiễu sàn 9 = 39.918; Không sót sàn 9 = 62.768).
Chạy: python sa_dot_selftest.py"""
import sys, numpy as np, pandas as pd
from sa_common import DotData, load_dot, rhu
from sa_dot_rules import evaluate, ref_run, bars_from, all_configs, running_rule, K_of, kyluc_r

LOG = []


def say(s):
    print(s, flush=True); LOG.append(s)


def check(name, ok, detail=''):
    say(f'{"ĐẠT  " if ok else "TRƯỢT"} {name}{(" — " + detail) if detail else ""}')
    return ok


def mk(bars, m=1):
    """bars: list (thời điểm, [(tick, bid, ask)]). Dựng DotData giống load.py (vol = bid + ask)."""
    rows = [(pd.Timestamp(t), tk, b, a, b + a) for t, cells in bars for tk, b, a in cells]
    F = pd.DataFrame(rows, columns=['t', 'tk', 'bid', 'ask', 'vol'])
    F = F[F.vol > 0].sort_values(['t', 'tk']).reset_index(drop=True)
    S = F.groupby('t').agg(med=('vol', 'median'), mean=('vol', 'mean'), hi=('tk', 'max'), lo=('tk', 'min'), nl=('tk', 'size'), tot=('vol', 'sum'))
    S['rng'] = S.hi - S.lo
    return DotData('GC', m, F, S, tag='test')


def dots_of(ds, res, b):
    i = np.nonzero(res.dot[ds.s0[b]:ds.s1[b]])[0] + ds.s0[b]
    return {(int(ds.stk[k]), int(ds.sside[k])) for k in i}


allok = True
say('=== (a) ví dụ nhỏ, kết quả tính tay ===')
# K theo kiểu p / λ (phần vạn / phần tư)
allok &= check('K kiểu p: 1% của 500 mẫu = 5; 1% của 499 mẫu = chưa có ngưỡng (cần >= 500)', K_of('p', 100, 500, 1) == 5 and K_of('p', 100, 499, 1) == -1)
allok &= check('K kiểu λ: 0,25 x 5 nến = 1; 0,25 x 4 nến = chưa có (cần >= 5 nến); 0,25 x 7 = 1', K_of('lam', 1, 0, 5) == 1 and K_of('lam', 1, 0, 4) == -1 and K_of('lam', 1, 0, 7) == 1)
allok &= check('r kỷ lục: q 0,25, n 8 -> floor(2,25 + 0,5) = 2; q 0,1, n 8 -> max(1, 1) = 1; q 0,5 n 20 -> 11', list(kyluc_r(0.25, [8])) == [2] and list(kyluc_r(0.1, [8])) == [1] and list(kyluc_r(0.5, [20])) == [11])

# (a1) cuốn: 5 nến M1 một ô Bid 1..5, nến 6 có Bid 6 (tick 100), Bid 4 (101), Ask 5 (110). λ 0,25 -> K = floor(5/4) = 1 -> ngưỡng = lớn thứ 2 = 4.
B = [(f'2026-09-01 10:0{i}', [(100, i + 1, 0)]) for i in range(5)] + [('2026-09-01 10:05', [(100, 6, 0), (101, 4, 0), (110, 0, 5)])]
ds = mk(B); cfg = dict(pa='cuon', T=5, lk='lam', lx=1, name='t')
r = evaluate(ds, cfg); rr = ref_run(bars_from(ds), cfg, 1)
allok &= check('cuon: nến 6 ngưỡng 4, chấm {Bid 100, Ask 110}; nến 1..5 chưa có ngưỡng',
               r.thr[5] == 4 and dots_of(ds, r, 5) == {(100, 0), (110, 1)} and not r.has[:5].any() and rr[5][0] == 4 and rr[5][1] == {(100, 0), (110, 1)})
cfgp = dict(pa='cuon', T=5, lk='p', lx=100, name='t')
allok &= check('cuon kiểu p 1% với 5 mẫu: chưa có ngưỡng (cần 500 mẫu)', not evaluate(ds, cfgp).has.any())

# (a2) cùng giờ: M1, khung 30 phút. Ngày 1..3 lúc 14:00/14:01 có Bid {10,2} {8,3} {12,1}; ngày 4 14:00 Bid 11 (100), Ask 9 (120).
# Tham chiếu 6 giá trị / 6 nến, λ 0,25 -> K = 1 -> ngưỡng 10 -> chỉ Bid 11 vượt. Lân cận ±1: thêm 14:30 mỗi ngày Bid 20 -> 9 nến, K = 2 -> ngưỡng 20 -> không vượt.
d1 = [(10, 2), (8, 3), (12, 1)]
B = []
for i, (a, b) in enumerate(d1):
    day = f'2026-09-0{i + 1}'
    B += [(f'{day} 14:00', [(100, a, 0)]), (f'{day} 14:01', [(100, b, 0)])]
B2 = B + [('2026-09-04 14:00', [(100, 11, 0), (120, 0, 9)]), ('2026-09-04 15:00', [(100, 50, 0)])]
ds = mk(B2); cfg = dict(pa='cung_gio', K=5, lc=0, lk='lam', lx=1, name='t')
r = evaluate(ds, cfg); rr = ref_run(bars_from(ds), cfg, 1)
allok &= check('cung_gio: ngày 4 14:00 ngưỡng 10, chấm {Bid 100}; 15:00 chưa có ngưỡng (0 lần xuất hiện); ba ngày đầu chưa có ngưỡng',
               r.thr[6] == 10 and dots_of(ds, r, 6) == {(100, 0)} and not r.has[7] and not r.has[:6].any() and rr[6][0] == 10 and rr[6][1] == {(100, 0)} and rr[7][0] is None)
B3 = list(B) + [(f'2026-09-0{i + 1} 14:30', [(100, 20, 0)]) for i in range(3)]
B3 = sorted(B3) + [('2026-09-04 14:00', [(100, 11, 0), (120, 0, 9)])]
ds = mk(B3); cfg = dict(pa='cung_gio', K=5, lc=1, lk='lam', lx=1, name='t')
r = evaluate(ds, cfg); rr = ref_run(bars_from(ds), cfg, 1)
cfg0 = dict(cfg, lc=0); r0 = evaluate(ds, cfg0)
allok &= check('cung_gio lân cận ±1: ngưỡng 20, không chấm; không lân cận vẫn ngưỡng 10',
               r.thr[-1] == 20 and dots_of(ds, r, ds.nb - 1) == set() and rr[-1][0] == 20 and r0.thr[-1] == 10)

# (a3) lai, mặt bằng trung vị, cuốn 1.380 phút. Mỗi nến 3 ô: (100: Bid 1 Ask 1), (101: Bid 2), (102: Bid X) -> trung vị volume ô = 2 -> L = 2 từ nến thứ 6.
# Nến 0..4 X = 3 (chưa có L, không nộp tỉ số); nến 5..9 X = 4, 6, 8, 10, 12 -> tỉ số: 0,5 0,5 1 X/2. Nến 10: 20 tỉ số của 5 nến, λ 0,25 -> K = 1
# -> ngưỡng tỉ số = lớn thứ 2 = 5 (X 10) -> nến 10 có X = 11: 11/2 = 5,5 > 5 -> chấm Bid 102; ngưỡng hiển thị 5 x 2 = 10.
X = [3] * 5 + [4, 6, 8, 10, 12, 11]
B = [(f'2026-09-01 10:{i:02d}', [(100, 1, 1), (101, 2, 0), (102, x, 0)]) for i, x in enumerate(X)]
ds = mk(B); cfg = dict(pa='lai', L='med', ref='r1380', lk='lam', lx=1, name='t')
r = evaluate(ds, cfg); rr = ref_run(bars_from(ds), cfg, 1)
allok &= check('lai: nến 10 ngưỡng tỉ số 5 (hiển thị 10), chấm {Bid 102}; nến 0..9 chưa có ngưỡng',
               abs(r.thr[10] - 10) < 1e-12 and dots_of(ds, r, 10) == {(102, 0)} and not r.has[:10].any() and abs(rr[10][0] - 10) < 1e-12 and rr[10][1] == {(102, 0)})

# (a4) z_log, T = 5 phút (n = 5). Tham chiếu: 1 x3, 2 x4, 4 x3 -> m = ln2, d = ln2 -> z >= 3 khi ln v >= ln2 x (1 + 3 x 1,4826) -> v >= 2^5,4478 = 43,6 -> v >= 44.
B = [('2026-09-01 10:00', [(100, 1, 1), (101, 1, 0)]), ('2026-09-01 10:01', [(100, 2, 2)]), ('2026-09-01 10:02', [(100, 2, 2)]),
     ('2026-09-01 10:03', [(100, 4, 4)]), ('2026-09-01 10:04', [(100, 4, 0)]), ('2026-09-01 10:05', [(100, 44, 43)])]
ds = mk(B); cfg = dict(pa='z_log', T=5, z0=3.0, name='t')
r = evaluate(ds, cfg); rr = ref_run(bars_from(ds), cfg, 1)
allok &= check('z_log: nến 6 ngưỡng 2^5,4478 = 43,64; Bid 44 vượt, Ask 43 không',
               abs(r.thr[5] - 2 ** (1 + 3 * 1.4826)) < 1e-9 and dots_of(ds, r, 5) == {(100, 0)} and rr[5][1] == {(100, 0)} and abs(rr[5][0] - r.thr[5]) < 1e-9)

# (a5) kỷ lục cuốn, T = 5 -> n = max(8, 5) = 8. Lớn nhất nến 0..7: 3 5 7 ... 17; q 0,25 -> r = 2 -> ngưỡng = 15.
B = [(f'2026-09-01 10:{i:02d}', [(100, 3 + 2 * i, 0)]) for i in range(8)] + [('2026-09-01 10:08', [(100, 16, 0), (110, 0, 20), (111, 0, 5)])]
ds = mk(B); cfg = dict(pa='ky_luc', rk='T', rv=5, q=0.25, name='t')
r = evaluate(ds, cfg); rr = ref_run(bars_from(ds), cfg, 1)
allok &= check('ky_luc: nến 9 ngưỡng 15, chấm {Bid 100, Ask 110}; 8 nến đầu chưa có ngưỡng',
               r.thr[8] == 15 and dots_of(ds, r, 8) == {(100, 0), (110, 1)} and not r.has[:8].any() and rr[8][0] == 15)
# gộp: hai ô Bid 30 (tick 100) và 25 (tick 103) cách 3 <= w 4 -> chỉ giữ 30; Bid 30 bằng nhau ở 100 và 104 -> không ô nào lớn hơn hẳn -> không chấm
B = [(f'2026-09-01 10:{i:02d}', [(100, 2, 0)]) for i in range(8)] + [('2026-09-01 10:08', [(100, 30, 0), (103, 25, 0), (120, 0, 30), (124, 0, 30)])]
ds = mk(B); r = evaluate(ds, dict(pa='ky_luc', rk='T', rv=5, q=0.25, name='t'))
allok &= check('gộp ±w: Bid 30 giữ, Bid 25 cách 3 tick bỏ; hai Ask 30 bằng nhau cách 4 tick -> không chấm nào', dots_of(ds, r, 8) == {(100, 0)} and r.exc[ds.s0[8]:ds.s1[8]].sum() == 4)

say('=== (d) mốc đối chứng luật đang chạy ra lại số chuẩn cũ (GC M1) ===')
g1 = load_dot('GC', 1)
n5 = int(running_rule(g1, 'khong_sot', 5).dot.sum()); n9 = int(running_rule(g1, 'it_nhieu', 9).dot.sum()); n59 = int(running_rule(g1, 'khong_sot', 9).dot.sum())
allok &= check(f'GC M1 Không sót sàn 5 = {n5} (chuẩn 80.386); Ít nhiễu sàn 9 = {n9} (chuẩn 39.918); Không sót sàn 9 = {n59} (chuẩn 62.768)', (n5, n9, n59) == (80386, 39918, 62768))
allok &= check(f'Số nến: GC M1 {g1.nb} (chuẩn 87.362), NQ M1 {load_dot("NQ", 1).nb} (chuẩn 71.047)', g1.nb == 87362 and load_dot('NQ', 1).nb == 71047)

say('=== (b) bản nhanh = bản chuẩn từng nến, 10 ngày giao dịch đầu ===')
CF = [dict(pa='cuon', T=120, lk='p', lx=100, name='cuon_T120_p1'), dict(pa='cuon', T=60, lk='lam', lx=2, name='cuon_T60_lam0.5'),
      dict(pa='cung_gio', K=5, lc=1, lk='lam', lx=2, name='cung_gio_K5_lc_lam0.5'), dict(pa='cung_gio', K=10, lc=0, lk='p', lx=50, name='cung_gio_K10_p0.5'),
      dict(pa='lai', L='med', ref=5, lk='p', lx=100, name='lai_med_K5_p1'), dict(pa='lai', L='mean', ref='r1380', lk='lam', lx=4, name='lai_mean_cuon1380_lam1'),
      dict(pa='z_log', T=120, z0=3.0, name='z_log_T120_z3'), dict(pa='ky_luc', rk='T', rv=240, q=0.25, name='ky_luc_T240_q0.25'),
      dict(pa='ky_luc', rk='K', rv=10, q=0.1, name='ky_luc_K10_q0.1')]
for sym, m in (('GC', 5), ('NQ', 15)):
    full = load_dot(sym, m)
    ds = full.subset(full.dayi < 10)
    bars = bars_from(ds)
    for cfg in CF:
        r = evaluate(ds, cfg); rr = ref_run(bars, cfg, m)
        bad_thr = 0; bad_dot = 0; bad_exc = 0; ndot = 0
        for b in range(ds.nb):
            t_ref = rr[b][0]
            if (t_ref is None) != (not r.has[b]): bad_thr += 1
            elif t_ref is not None and not (abs(t_ref - r.thr[b]) <= 1e-9 * max(1, abs(t_ref))): bad_thr += 1
            dd = dots_of(ds, r, b); ndot += len(dd)
            if dd != rr[b][1]: bad_dot += 1
            if int(r.exc[ds.s0[b]:ds.s1[b]].sum()) != rr[b][2]: bad_exc += 1
        allok &= check(f'{sym} M{m} {cfg["name"]}: {ds.nb} nến, {int(r.has.sum())} nến có ngưỡng, {ndot} chấm; lệch ngưỡng {bad_thr}, lệch vượt {bad_exc}, lệch chấm {bad_dot}',
                       bad_thr == 0 and bad_dot == 0 and bad_exc == 0 and ndot > 0)

say('=== (c) không nhìn tương lai: cắt tại một nến, chạy lại ===')
rs = np.random.RandomState(7)
for sym, m, cfgs in (('GC', 15, [c for c in all_configs() if not c['pa'].startswith('dc_')]), ('GC', 5, CF), ('NQ', 15, CF)):
    full = load_dot(sym, m)
    for cut in rs.randint(full.nb // 4, full.nb - 10, 2):
        part = full.subset(np.arange(full.nb) < cut)
        nbad = 0
        for cfg in cfgs:
            a = evaluate(full, cfg); b = evaluate(part, cfg)
            ns = part.ns
            same = (np.array_equal(a.has[:cut], b.has) and np.allclose(np.nan_to_num(a.thr[:cut], nan=-7), np.nan_to_num(b.thr, nan=-7), rtol=0, atol=0)
                    and np.array_equal(a.exc[:ns], b.exc) and np.array_equal(a.dot[:ns], b.dot))
            if not same: nbad += 1; say(f'   lệch: {cfg["name"]}')
        allok &= check(f'{sym} M{m} cắt tại nến {cut}/{full.nb}: {len(cfgs)} cấu hình, lệch {nbad}', nbad == 0)

say('TẤT CẢ: ' + ('ĐẠT' if allok else 'TRƯỢT'))
open('out_r1_dot_selftest.txt', 'w', encoding='utf-8').write('\n'.join(LOG) + '\n')
sys.exit(0 if allok else 1)
