# -*- coding: utf-8 -*-
"""
results_corven.py — GĐ1: chạy setup CORVEN đủ ①–④ + ⛔ trên TRAIN, bộ mặc định (không tinh chỉnh), viết
report/RESULTS-CORVEN.md (bảng plan mục 3.5 + phễu + nhóm tách + 3 đối chứng), report/_corven_trades.csv,
ảnh 5 thắng + 5 thua ở report/corven_gd1_shots/.

Chạy:  PYTHONIOENCODING=utf-8 python results_corven.py      (≈ 1–2 phút)
⛔ CHỈ TRAIN: setup_corven.load_train cắt file tại nến cuối phiên 2026-09-15 trước khi tính bất cứ gì.
"""
from __future__ import annotations

import os
import sys
from collections import Counter
from dataclasses import asdict, replace

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import setup_corven as SC        # noqa: E402
import controls_corven as CC     # noqa: E402
import plot_corven as PC         # noqa: E402

REPORT = os.path.join(HERE, 'report')
SHOTS = os.path.join(REPORT, 'corven_gd1_shots')
TYPE_VN = dict(delta='Δ', bong='bóng', kiet_suc='kiệt sức', stacked='stacked', trap='trap')
THE_VN = dict(A='A (fail break)', A2='A "lần 2"', B='B (phá giữ được)')


# ------------------------------------------------------------------ thống kê
def stats(t: pd.DataFrame, n_days: int, seed: int = 0) -> dict:
    if t is None or len(t) == 0:
        return dict(n=0)
    c = t[t['outcome'].isin(['TP', 'SL', 'TIME'])]
    r = c['r'].to_numpy(float)
    n = len(r)
    if n == 0:
        return dict(n=0)
    rng = np.random.default_rng(seed)
    bs = rng.choice(r, size=(10000, n), replace=True).mean(axis=1)
    cum = np.cumsum(r)
    dd = float(np.max(np.maximum.accumulate(np.r_[0, cum]) - np.r_[0, cum]))
    streak = best = 0
    for x in r:
        streak = streak + 1 if x <= 0 else 0
        best = max(best, streak)
    return dict(n=n, per_day=n / n_days, wr=float((r > 0).mean()), avg=float(r.mean()), lo=float(np.percentile(bs, 2.5)),
                hi=float(np.percentile(bs, 97.5)), sum=float(r.sum()), dd=dd, streak=best,
                n_open=int((t['outcome'] == 'OPEN').sum()), n_time=int((c['outcome'] == 'TIME').sum()))


def f2(x, p=2):
    return ('%.*f' % (p, x)).replace('.', ',') if x == x else '–'


HDR = '| | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD (R) | chuỗi thua |\n|---|---|---|---|---|---|---|---|---|'


def row(name, s):
    if s.get('n', 0) == 0:
        return f'| {name} | 0 | – | – | – | – | – | – | – |'
    return (f"| {name} | {s['n']} | {f2(s['per_day'])} | {f2(100 * s['wr'], 1)} % | **{f2(s['avg'])}** | "
            f"[{f2(s['lo'])}; {f2(s['hi'])}] | {f2(s['sum'], 1)} | {f2(s['dd'], 1)} | {s['streak']} |")


def table(groups, n_days, title=None):
    L = ([f'### {title}', ''] if title else []) + [HDR]
    for k, t in groups:
        L.append(row(k, stats(t, n_days)))
    return L + ['']


# ------------------------------------------------------------------ phễu
def funnel(R) -> list:
    good = R['good']
    m = R['m']
    cands = [c for c in R['cands'] if good[c.cf]]
    cp = R['cp']
    chosen_ids = {id(c.inst) for c in R['chosen']}
    insts = {'A': [a for a in m.A if good[a.fb]], 'A2': [x for x in m.EXC if good[x.bar]], 'B': [b for b in m.B if good[b.bc]]}
    by_inst = {}
    for c in cands:
        by_inst.setdefault(id(c.inst), []).append(c)
    L = ['| Thế | số thế | qua ② | qua ③ (≥ 2 loại) | qua ④ + ⛔ + giờ | thành lệnh |', '|---|---|---|---|---|---|']
    for th, lst in insts.items():
        n = len(lst)
        n2 = sum(1 for x in lst if by_inst.get(id(x)))
        n3 = sum(1 for x in lst if any(len(c.types) >= cp.need_signs for c in by_inst.get(id(x), [])))
        n4 = sum(1 for x in lst if any(len(c.types) >= cp.need_signs and not c.gates for c in by_inst.get(id(x), [])))
        n5 = sum(1 for x in lst if id(x) in chosen_ids)
        L.append(f'| {THE_VN[th]} | {n} | {n2} | {n3} | {n4} | {n5} |')
    L.append('')
    # theo CF ứng viên
    p3 = [c for c in cands if len(c.types) >= cp.need_signs]
    L += [f'Theo **CF ứng viên** (nến): {len(cands)} qua ② → {len(p3)} qua ③ ({f2(100 * len(p3) / max(1, len(cands)), 1)} %) → '
          f'{sum(1 for c in p3 if not c.gates)} qua ④/⛔/giờ → {len(R["chosen"])} lệnh '
          f'(bỏ vì đang có lệnh mở {R["why"].get("dang_co_lenh", 0)}, vì thế/khoá đã có lệnh {R["why"].get("the_da_co_lenh", 0)}).', '',
          'Số dấu hiệu khác loại trên CF qua ②: ' + ', '.join(f'{k} loại: {v}' for k, v in sorted(Counter(len(c.types) for c in cands).items())), '',
          'Có mặt từng loại trên CF qua ②: ' + ', '.join(f'{TYPE_VN[t]} {sum(1 for c in cands if t in c.signs)} '
                                                         f'({f2(100 * sum(1 for c in cands if t in c.signs) / max(1, len(cands)), 1)} %)'
                                                         for t in SC.SIGN_TYPES), '',
          '**Cổng bị trượt** trên các CF đã qua ③ (cổng ĐẦU TIÊN theo thứ tự kiểm / tỷ lệ trượt độc lập từng cổng):', '',
          '| Cổng | trượt đầu tiên | % | trượt (độc lập) | % |', '|---|---|---|---|---|']
    first = Counter(c.gates[0] for c in p3 if c.gates)
    anyg = Counter(g for c in p3 for g in c.gates)
    for g in SC.GATES:
        L.append(f'| {SC.GATE_VN[g]} | {first.get(g, 0)} | {f2(100 * first.get(g, 0) / max(1, len(p3)), 1)} | {anyg.get(g, 0)} | '
                 f'{f2(100 * anyg.get(g, 0) / max(1, len(p3)), 1)} |')
    L.append(f'| **qua hết** | {sum(1 for c in p3 if not c.gates)} | {f2(100 * sum(1 for c in p3 if not c.gates) / max(1, len(p3)), 1)} | | |')
    L.append('')
    return L


def trades_csv(R, path):
    rows = []
    f = R['feat']
    for c, (_, t) in zip(R['chosen'], R['trades'].iterrows()):
        rows.append(dict(idx=c.cf, t_utc=str(t['t_utc'])[:16], t_vn=str(t['t_vn'])[:16], the=c.the,
                         side='buy' if c.S > 0 else 'sell', range_id=c.rid, b_from_exhausted=int(c.exhausted),
                         moc=c.moc_used, so_dau_hieu=len(c.types), loai=('+'.join(TYPE_VN[x] for x in c.types)),
                         dau_hieu=' | '.join(f"{TYPE_VN[k]}: {v[0]} (nến {v[1]})" for k, v in c.signs.items()),
                         entry=t['entry'], sl=t['sl'], tp=t['tp'], rui_ro_gia=round(c.risk * SC.TICK, 2),
                         rui_ro_mbr=round(c.risk / f.mbr[c.cf], 2), r_san=round(c.r_avail, 2),
                         ket_cuc=t['outcome'], r=round(float(t['r']), 3), exit_idx=int(t['exit_idx']),
                         giu_nen=int(t['hold_bars']), phien=t['session_id']))
    d = pd.DataFrame(rows)
    d.to_csv(path, index=False, encoding='utf-8')
    return d


def pick_examples(t: pd.DataFrame, chosen, k=5):
    cl = [(i, c) for i, c in enumerate(chosen) if t.iloc[i]['outcome'] in ('TP', 'SL', 'TIME')]
    w = [(i, c) for i, c in cl if t.iloc[i]['r'] > 0]
    l_ = [(i, c) for i, c in cl if t.iloc[i]['r'] <= 0]

    def spread(x):
        if len(x) <= k:
            return x
        idx = np.linspace(0, len(x) - 1, k).round().astype(int)
        return [x[j] for j in idx]
    return spread(w), spread(l_)


def main():
    cut = SC.train_cut()
    bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    nd = len(set(df['session_id'].to_numpy()[good]))
    cp = SC.CP()
    R = SC.run_gd1(bars, df, good, cp)
    t = R['trades']
    ch = R['chosen']
    os.makedirs(REPORT, exist_ok=True)
    tcsv = trades_csv(R, os.path.join(REPORT, '_corven_trades.csv'))
    the = np.array([c.the for c in ch])
    exh = np.array([c.exhausted for c in ch])
    combos = np.array(['+'.join(TYPE_VN[x] for x in c.types) for c in ch])
    L = ['# Benzo CORVEN — GĐ1: đủ ①–④ + ⛔ trên TRAIN, bộ mặc định (chưa tinh chỉnh)', '',
         f'> Opus, 2026-11-09, theo `plans/BENZO-CORVEN-plan.md` (bản sau quyết định Q1–Q15). **Chỉ TRAIN**: {nd} phiên dày, '
         f'nến bar_idx 0…{cut} (tới {str(df["datetime"].iloc[-1])[:16]} UTC). TEST chưa chạy, chưa đọc. Mô phỏng `kernel.simulate` '
         '(phí 0,2 giá/lệnh, chạm SL+TP cùng nến = SL, vào giá đóng CF, 1 lệnh mở), lệnh còn mở tới nến cuối phiên đóng `TIME`.',
         '> ⚠️ Kết quả trên một mẫu TRAIN, chưa kiểm định ngoài mẫu — không dùng để vào lệnh thật.', '']
    s_all = stats(t, nd)
    L += ['## 1. Tổng', ''] + table([('Tất cả', t)], nd)
    L += [f"Lệnh còn mở cuối file: {s_all.get('n_open', 0)} · đóng `TIME` cuối phiên: {s_all.get('n_time', 0)} · "
          f"hoà vốn ở TP 2R cần WR ≈ {f2(100 * (1 + 0.2 / tcsv['rui_ro_gia'].median()) / 3, 1) if len(tcsv) else '–'} % "
          f"(phí 0,2 giá trên rủi ro trung vị {f2(tcsv['rui_ro_gia'].median()) if len(tcsv) else '–'} giá).", '']
    per_day = pd.Series(1, index=t['session_id']).groupby(level=0).sum().reindex(sorted(set(df['session_id'].to_numpy()[good])), fill_value=0) if len(t) else pd.Series(dtype=int)
    if len(per_day):
        L += [f"Lệnh/ngày: trung vị {int(per_day.median())}, min {int(per_day.min())}, max {int(per_day.max())}; "
              f"phân bố {dict(sorted(Counter(per_day.tolist()).items()))}.", '']
    L += ['## 2. Phễu thế → ② → ③ → ④ → lệnh', ''] + funnel(R)
    L += ['## 3. Theo thế', ''] + table([('A (fail break)', t[the == 'A']), ('A "lần 2"', t[the == 'A2']),
                                          ('B (phá giữ được) — tất cả', t[the == 'B']),
                                          ('B — range còn BROKEN', t[(the == 'B') & ~exh]),
                                          ('B — `b_from_exhausted` (range DEAD ngay)', t[(the == 'B') & exh])], nd)
    cmb = Counter(combos)
    L += ['## 4. Theo tổ hợp dấu hiệu', ''] + table([(k, t[combos == k]) for k, _ in cmb.most_common()], nd)
    if len(t):
        hrs = pd.to_datetime(t['t_vn']).dt.hour.to_numpy()
        L += ['## 5. Theo giờ VN (giờ mở nến CF)', ''] + table([(f'{h:02d}h', t[hrs == h]) for h in sorted(set(hrs))], nd)
        ph = t['phase'].to_numpy()
        L += ['## 6. Theo phiên (A 05:00–12:30 · EU 12:30–19:00 · US 19:00–04:00 VN, neo Mỹ)', ''] + \
            table([(p, t[ph == p]) for p in ('A', 'EU', 'US', 'OFF') if (ph == p).any()], nd)
        mo = t['month'].to_numpy()
        L += ['## 7. Theo tháng', ''] + table([(x, t[mo == x]) for x in sorted(set(mo))], nd)
    # ---- nhóm tách ----
    tr_us, _, _ = SC.select_and_simulate(R['cands'], df, R['feat'], cp, block_us=False)
    tr_noa2, _, _ = SC.select_and_simulate(R['cands'], df, R['feat'], cp, keep=lambda c: c.the != 'A2')
    tr_noexh, _, _ = SC.select_and_simulate(R['cands'], df, R['feat'], cp, keep=lambda c: not c.exhausted)
    L += ['## 8. Nhóm tách riêng (chạy lại chọn lệnh, cùng ứng viên)', ''] + table([
        ('Mặc định (chặn 19:20–20:30 BẬT, có "lần 2", có `b_from_exhausted`)', t),
        ('Chặn 19:20–20:30 TẮT', tr_us), ('Bỏ "lần 2"', tr_noa2), ('Bỏ `b_from_exhausted`', tr_noexh)], nd)
    L += [f"Luật ⛔ range chồng range loại {f2(100 * R['chong_rate'], 1)} % thế A (≤ 30 % ⇒ **giữ luật**)." if R['use_chong'] else
          f"Luật ⛔ range chồng range loại {f2(100 * R['chong_rate'], 1)} % thế A (> 30 % ⇒ **đã bỏ luật** theo plan).", '']
    # ---- đối chứng ----
    t1 = CC.c1(R)
    d2, all2 = CC.c2(R)
    t3 = CC.c3(R)
    L += ['## 9. Đối chứng (cùng SL/TP/chi phí)', '', HDR, row('**CORVEN (≥ 2 dấu hiệu)**', s_all), row('C1 — bỏ ③ (mọi CF hợp lệ tại mốc)', stats(t1, nd))]
    if len(d2):
        rr = d2['r_c2_tb'].to_numpy()
        bs = np.random.default_rng(0).choice(rr, size=(10000, len(rr))).mean(axis=1)
        L.append(f"| C2 — ngẫu nhiên cùng phiên/giờ ±30′/hướng/rủi ro mbr (20 nến mỗi lệnh, {len(all2)} lệnh giả) | {len(d2)} | – | "
                 f"{f2(100 * (all2 > 0).mean(), 1)} % | **{f2(rr.mean())}** | [{f2(np.percentile(bs, 2.5))}; {f2(np.percentile(bs, 97.5))}] | – | – | – |")
    for k in SC.SIGN_TYPES:
        L.append(row(f'C3 — chỉ đòi {TYPE_VN[k]}', stats(t3[k], nd)))
    L.append('')
    if len(d2):
        L += [f"C2 theo cặp: R thật − R đối chứng trung bình = {f2((d2['r_that'] - d2['r_c2_tb']).mean())} trên {len(d2)} lệnh.", '']
    sd_share = float(np.mean(['stacked' in c.types for c in ch])) if ch else 0
    L += [f"Dấu hiệu stacked có mặt ở {f2(100 * sd_share, 1)} % số lệnh "
          + ("(> 50 % ⇒ GĐ2 quét run 4 theo plan ③d)." if sd_share > 0.5 else "(≤ 50 % ⇒ chưa phải nâng run 4)."), '']
    # ---- ví dụ + ảnh ----
    wins, losses = pick_examples(t, ch)
    L += ['## 10. 5 thắng + 5 thua (rải đều theo thời gian) — ảnh ở `corven_gd1_shots/`', '',
          '| | UTC | VN | thế | side | mốc | dấu hiệu | vào | SL | TP | R sẵn | kết cục | R | ảnh |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    os.makedirs(SHOTS, exist_ok=True)
    for old in os.listdir(SHOTS):
        if old.endswith('.png'):
            os.remove(os.path.join(SHOTS, old))
    for tag, lst in (('THANG', wins), ('THUA', losses)):
        for n, (i, c) in enumerate(lst):
            tt = t.iloc[i]
            fn = PC.plot_trade(df, R['feat'], tt, c, SHOTS, f'{tag}{n + 1}')
            L.append(f"| {tag.lower()} {n + 1} | {str(tt['t_utc'])[:16]} | {str(tt['t_vn'])[11:16]} | {c.the} | {'buy' if c.S > 0 else 'sell'} | "
                     f"{c.moc_used} | {'; '.join(v[0] for v in c.signs.values())} | {tt['entry']:.1f} | {tt['sl']:.1f} | {tt['tp']:.1f} | "
                     f"{f2(c.r_avail)} | {tt['outcome']} | {f2(float(tt['r']))} | [ảnh](corven_gd1_shots/{os.path.basename(fn)}) |")
    L.append('')
    L += ['## 11. Tham số (bộ mặc định, chưa tinh chỉnh)', '', '```', str(asdict(cp)), '```', '']
    L += open(os.path.join(HERE, 'report', '_corven_gd1_notes.md'), encoding='utf-8').read().splitlines()
    with open(os.path.join(REPORT, 'RESULTS-CORVEN.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('\n'.join(L[:60]))
    return R


if __name__ == '__main__':
    main()
