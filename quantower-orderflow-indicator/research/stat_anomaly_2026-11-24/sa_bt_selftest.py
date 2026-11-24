"""Tự kiểm phần Big Trade (PLAN bước 6). In ĐẠT / TRƯỢT từng mục và ghi out_r1_bt_selftest.txt.
(a) ví dụ nhỏ tính tay; (b) bản nhanh = bản chuẩn từng nến (bản chuẩn được nạp CẢ nến không có số liệu, chèn vào mọi chỗ trống của lưới thời gian);
(c) không nhìn tương lai; (d) nến không có số liệu không được nộp; (e) số nến nhật ký: GC 22.948, NQ 8.340 nến M1.
Chạy: python sa_bt_selftest.py"""
import sys, numpy as np, pandas as pd
from sa_common import load_dot
import sa_dot_rules as R
from sa_bt_rules import BtData, evaluate_bt, ref_run_bt, bt_configs, attach_L, merge_greedy
from bt_common import load_m1, to_tf

LOG = []


def say(s):
    print(s, flush=True); LOG.append(s)


def check(name, ok, detail=''):
    say(f'{"ĐẠT  " if ok else "TRƯỢT"} {name}{(" — " + detail) if detail else ""}')
    return ok


def mkc(rows):
    """rows: list (thời điểm, tick, mot). Trả DataFrame ô nhật ký."""
    c = pd.DataFrame(rows, columns=['t', 'tk', 'mot']); c['t'] = pd.to_datetime(c.t); c['buy'] = c.mot; c['sell'] = 0
    return c


def rings(bt, res, b):
    i = np.nonzero(res.dot[bt.s0[b]:bt.s1[b]])[0] + bt.s0[b]
    return sorted((int(bt.stk[k]), int(bt.sval[k])) for k in i)


def ref_bars(bt, with_empty=True):
    """Danh sách nến cho bản chuẩn: mọi mốc thời gian trên lưới khung từ nến đầu tới nến cuối; nến không có trong nhật ký = rỗng."""
    grid = pd.date_range(bt.t[0], bt.t[-1], freq=f'{bt.m}min') if with_empty else bt.t
    pos = {t: i for i, t in enumerate(bt.t)}
    out, Ls, idx = [], {k: [] for k in bt.Lb}, []
    for t in grid:
        tday = (t + pd.Timedelta(hours=2)).normalize()
        day = int(np.searchsorted(bt.days.values, tday.to_datetime64()))
        slot = (t.hour * 60 + t.minute) // bt.W
        if t in pos:
            b = pos[t]; cells = list(zip(bt.stk[bt.s0[b]:bt.s1[b]].tolist(), bt.sval[bt.s0[b]:bt.s1[b]].tolist()))
            for k in bt.Lb: Ls[k].append(None if not np.isfinite(bt.Lb[k][b]) else float(bt.Lb[k][b]))
            idx.append(b)
        else:
            cells = [(0, 0)] if (len(out) % 2) else []        # nến rỗng: hoặc không có ô, hoặc có ô mot = 0
            for k in bt.Lb: Ls[k].append(3.0)               # L có giá trị nhưng nến rỗng vẫn không được nộp
            idx.append(-1)
        out.append((day, slot, cells))
    return out, Ls, idx


allok = True
say('=== (a) ví dụ nhỏ, kết quả tính tay ===')
# cuốn T 5 (n 5), λ 0,25 -> K 1. Năm nến có số liệu mot 2 4 6 8 10 (xen nến rỗng ở bản chuẩn) -> ngưỡng = lớn thứ 2 = 8.
# Nến 6: 9 (100) 12 (101) 7 (104) 11 (110) -> vượt 9, 12, 11; gộp g = 2: giữ 12 (101), 11 (110); 9 (100) cách 101 là 1 -> bỏ.
rows = [(f'2026-09-01 10:{2 * i:02d}', 100, v) for i, v in enumerate([2, 4, 6, 8, 10])] + [('2026-09-01 10:10', t, v) for t, v in ((100, 9), (101, 12), (104, 7), (110, 11))]
bt = BtData('TEST', 1, mkc(rows)); cfg = dict(pa='cuon', T=5, lk='lam', lx=1, name='t')
r = evaluate_bt(bt, cfg); bars, _, idx = ref_bars(bt); rr = ref_run_bt(bars, cfg, 1)
allok &= check('cuon: ngưỡng 8, vòng {101: 12, 110: 11}; bản chuẩn có 5 nến rỗng xen giữa vẫn ra ngưỡng 8 (nến rỗng không nộp, không tính vào 5 nến)',
               r.thr[5] == 8 and rings(bt, r, 5) == [(101, 12), (110, 11)] and rr[-1][0] == 8 and sorted(rr[-1][1]) == [(101, 12), (110, 11)] and len(bars) == 11)
# kỷ lục T 5 -> n 8; lớn nhất 3..17; q 0,25 -> r 2 -> ngưỡng 15. Nến 9: 16 (100), 20 (102), 5 (110): vượt 16, 20; gộp g 2: 100 cách 102 là 2 -> bỏ.
rows = [(f'2026-09-01 10:{i:02d}', 100, 3 + 2 * i) for i in range(8)] + [('2026-09-01 10:08', t, v) for t, v in ((100, 16), (102, 20), (110, 5))]
bt = BtData('TEST', 1, mkc(rows)); cfg = dict(pa='ky_luc', rk='T', rv=5, q=0.25, name='t')
r = evaluate_bt(bt, cfg)
allok &= check('ky_luc: ngưỡng 15, vòng {102: 20}', r.thr[8] == 15 and rings(bt, r, 8) == [(102, 20)])
# cùng giờ: ngày 1..3 lúc 14:00/14:01 mot {10,2} {8,3} {12,1}; ngày 4 14:00: 11 (100), 9 (120). 6 nến, λ 0,25 -> K 1 -> ngưỡng 10.
rows = []
for i, (a, b) in enumerate([(10, 2), (8, 3), (12, 1)]):
    rows += [(f'2026-09-0{i + 1} 14:00', 100, a), (f'2026-09-0{i + 1} 14:01', 100, b)]
rows += [('2026-09-04 14:00', 100, 11), ('2026-09-04 14:00', 120, 9)]
bt = BtData('TEST', 1, mkc(rows)); cfg = dict(pa='cung_gio', K=5, lc=0, lk='lam', lx=1, name='t')
r = evaluate_bt(bt, cfg)
allok &= check('cung_gio: ngày 4 ngưỡng 10, vòng {100: 11}; ba ngày đầu chưa có ngưỡng', r.thr[6] == 10 and rings(bt, r, 6) == [(100, 11)] and not r.has[:6].any())
# lai tích lũy: L = 2 ở 5 nến đầu, mot 2 4 6 8 10 -> tỉ số 1..5; λ 0,25 -> K 1 -> ngưỡng tỉ số 4. Nến 6: L = 2,5; 11 / 2,5 = 4,4 > 4 vượt; 10 / 2,5 = 4 không.
rows = [(f'2026-09-01 10:{i:02d}', 100, v) for i, v in enumerate([2, 4, 6, 8, 10])] + [('2026-09-01 10:05', 100, 11), ('2026-09-01 10:05', 105, 10)]
bt = BtData('TEST', 1, mkc(rows)); bt.Lb['med'] = np.array([2, 2, 2, 2, 2, 2.5]); cfg = dict(pa='lai', L='med', ref='cum', lk='lam', lx=1, name='t')
r = evaluate_bt(bt, cfg); bars, Ls, idx = ref_bars(bt); rr = ref_run_bt(bars, cfg, 1, Ls['med'])
allok &= check('lai: ngưỡng tỉ số 4 (hiển thị 10), vòng {100: 11}', abs(r.thr[5] - 10) < 1e-12 and rings(bt, r, 5) == [(100, 11)] and abs(rr[-1][0] - 10) < 1e-12)
# gộp: hòa thì tick thấp trước
bt = BtData('TEST', 1, mkc([('2026-09-01 10:00', 105, 9), ('2026-09-01 10:00', 100, 9), ('2026-09-01 10:00', 103, 9)]))
keep = merge_greedy(bt, np.ones(3, bool))
allok &= check('gộp vòng: ba ô mot 9 ở 100, 103, 105, g 2 -> giữ 100 và 103, bỏ 105', sorted(bt.stk[keep].tolist()) == [100, 103])

say('=== (e) số nến nhật ký M1 ===')
ng = load_m1('GC').t.nunique(); nn = load_m1('NQ').t.nunique(); nl = load_m1('GClive').t.nunique()
allok &= check(f'GC {ng} (chuẩn 22.948), NQ {nn} (chuẩn 8.340), GClive {nl}', ng == 22948 and nn == 8340)

say('=== (b)+(d) bản nhanh = bản chuẩn từng nến (bản chuẩn có chèn nến rỗng) ===')
for key, m, days in (('GC', 5, 10), ('NQ', 15, 99)):
    c = to_tf(load_m1(key), m)
    bt = BtData(key, m, c)
    keep_t = bt.t[bt.dayi < days]
    bt = BtData(key, m, c[c.t.isin(keep_t)])
    attach_L(bt, load_dot(key, m))
    bars, Ls, idx = ref_bars(bt)
    K1 = 5 if key == 'GC' else 3
    CF = [dict(pa='cuon', T=120, lk='p', lx=50, name='cuon_T120_p0.5'), dict(pa='cuon', T=60, lk='lam', lx=2, name='cuon_T60_lam0.5'),
          dict(pa='cung_gio', K=K1, lc=1, lk='lam', lx=4, name=f'cung_gio_K{K1}_lc_lam1'), dict(pa='cung_gio', K=K1, lc=0, lk='p', lx=100, name=f'cung_gio_K{K1}_p1'),
          dict(pa='ky_luc', rk='T', rv=240, q=0.25, name='ky_luc_T240_q0.25'),
          dict(pa='lai', L='med', ref='cum', lk='p', lx=100, name='lai_med_tichluy_p1'), dict(pa='lai', L='p90_120', ref='day', lk='lam', lx=2, name='lai_p90_120_ngay_lam0.5')]
    for cfg in CF:
        r = evaluate_bt(bt, cfg)
        rr = ref_run_bt(bars, cfg, m, Ls.get(cfg.get('L', 'med')))
        bad = 0; nring = 0; empty_bad = 0
        for k, b in enumerate(idx):
            if b < 0:
                if rr[k][1] or rr[k][2]: empty_bad += 1
                continue
            t_ref = rr[k][0]
            okthr = (t_ref is None and not r.has[b]) or (t_ref is not None and r.has[b] and abs(t_ref - r.thr[b]) <= 1e-9 * max(1, abs(t_ref)))
            rg = rings(bt, r, b); nring += len(rg)
            if not okthr or rg != sorted(rr[k][1]) or int(r.exc[bt.s0[b]:bt.s1[b]].sum()) != rr[k][2]: bad += 1
        allok &= check(f'{key} M{m} {cfg["name"]}: {bt.nb} nến có số liệu (+{idx.count(-1)} nến rỗng ở bản chuẩn), {int(r.has.sum())} có ngưỡng, {nring} vòng; nến lệch {bad}; nến rỗng có vòng {empty_bad}',
                       bad == 0 and empty_bad == 0 and nring > 0)

say('=== (c) không nhìn tương lai ===')
for key, m in (('GC', 5), ('NQ', 15), ('GClive', 5)):
    c = to_tf(load_m1(key), m); full = BtData(key, m, c)
    lai_ok = key != 'GClive'
    if lai_ok: attach_L(full, load_dot(key[:2], m))
    cfgs = [x for x in bt_configs(key, ('med', 'p90_120') if lai_ok else ()) if not x['pa'].startswith('dc_')]
    for cut in (full.nb // 3, 2 * full.nb // 3):
        part = BtData(key, m, c[c.t < full.t[cut]])
        if lai_ok: attach_L(part, load_dot(key[:2], m))
        nbad = 0
        for cfg in cfgs:
            a = evaluate_bt(full, cfg); b = evaluate_bt(part, cfg); ns = part.ns
            same = (np.array_equal(a.has[:cut], b.has) and np.array_equal(np.nan_to_num(a.thr[:cut], nan=-7), np.nan_to_num(b.thr, nan=-7))
                    and np.array_equal(a.exc[:ns], b.exc) and np.array_equal(a.dot[:ns], b.dot))
            if not same: nbad += 1; say('   lệch ' + cfg['name'])
        allok &= check(f'{key} M{m} cắt tại nến {cut}/{full.nb}: {len(cfgs)} cấu hình, lệch {nbad}', nbad == 0)

say('TẤT CẢ: ' + ('ĐẠT' if allok else 'TRƯỢT'))
open('out_r1_bt_selftest.txt', 'w', encoding='utf-8').write('\n'.join(LOG) + '\n')
sys.exit(0 if allok else 1)
