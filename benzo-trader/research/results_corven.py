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
                         rui_ro_mbr=round(c.risk / f.mbr[c.cf], 2), r_san=round(c.r_avail, 2), neo_sl=c.anchor,
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


# =====================================================================================================
# GĐ2 vòng 1 (plan mục 7.3): A2 tắt, SL cú thủng đúng, hai neo SL song song, mức nền "SL rồi vẫn chạm TP"
# =====================================================================================================
SHOTS2 = os.path.join(REPORT, 'corven_gd2v1_shots')
ANCHOR_VN = dict(cu_thung='neo cú thủng / mốc (4b)', pivot='neo "đáy/đỉnh mới quét" (pivot 1 nến)')
NAN = float('nan')


def section(R, nd, num, label, shots_prefix):
    """Đủ bảng GĐ1 (mục 3.5 + phễu + theo thế/số dấu hiệu/tổ hợp/giờ/phiên/tháng + nhóm tách + C1/C2/C3 + 5/5 ảnh)."""
    df, cp = R['df'], R['cp']
    t, ch = R['trades'], R['chosen']
    the = np.array([c.the for c in ch])
    exh = np.array([c.exhausted for c in ch], bool)
    nsg = np.array([len(c.types) for c in ch])
    combos = np.array(['+'.join(TYPE_VN[x] for x in c.types) for c in ch])
    s_all = stats(t, nd)
    H = f'{num}.'
    L = [f'### {H}1 Tổng — {label}', ''] + table([('Tất cả', t)], nd)
    rr = [c.risk * SC.TICK for c in ch]
    if rr:
        L += [f"Đóng `TIME` cuối phiên: {s_all.get('n_time', 0)} · rủi ro trung vị {f2(float(np.median(rr)))} giá "
              f"({f2(float(np.median([c.risk / R['feat'].mbr[c.cf] for c in ch])))} mbr) · giữ lệnh trung vị {int(t['hold_bars'].median())} nến · "
              f"hoà vốn ở TP 2R cần WR ≈ {f2(100 * (1 + 0.2 / float(np.median(rr))) / 3, 1)} %.", '']
        per_day = pd.Series(1, index=t['session_id']).groupby(level=0).sum().reindex(
            sorted(set(df['session_id'].to_numpy()[R['good']])), fill_value=0)
        L += [f"Lệnh/ngày: trung vị {int(per_day.median())}, min {int(per_day.min())}, max {int(per_day.max())}.", '']
    L += [f'### {H}2 Phễu (hàng "lần 2" = nhóm báo cáo, tắt khi chọn lệnh)', ''] + funnel(R)
    L += table([('A (fail break)', t[the == 'A']), ('B — tất cả', t[the == 'B']), ('B — range còn BROKEN', t[(the == 'B') & ~exh]),
                ('B — `b_from_exhausted`', t[(the == 'B') & exh])], nd, f'{H}3 Theo thế')
    L += table([(f'{k} loại', t[nsg == k]) for k in sorted(set(nsg))], nd, f'{H}4 Theo số dấu hiệu khác loại')
    cmb = Counter(combos)
    L += table([(k, t[combos == k]) for k, _ in cmb.most_common()], nd, f'{H}5 Theo tổ hợp dấu hiệu')
    if len(t):
        hrs = pd.to_datetime(t['t_vn']).dt.hour.to_numpy()
        L += table([(f'{h:02d}h', t[hrs == h]) for h in sorted(set(hrs))], nd, f'{H}6 Theo giờ VN (giờ mở nến CF)')
        ph = t['phase'].to_numpy()
        L += table([(p, t[ph == p]) for p in ('A', 'EU', 'US', 'OFF') if (ph == p).any()], nd,
                   f'{H}7 Theo phiên (A 05:00–12:30 · EU 12:30–19:00 · US 19:00–04:00 VN, neo Mỹ)')
        mo = t['month'].to_numpy()
        L += table([(x, t[mo == x]) for x in sorted(set(mo))], nd, f'{H}8 Theo tháng')
    tr_us, _, _ = SC.select_and_simulate(R['cands'], df, R['feat'], cp, block_us=False)
    tr_noexh, _, _ = SC.select_and_simulate(R['cands'], df, R['feat'], cp, keep=lambda c: not c.exhausted)
    cpa2 = replace(cp, a2_on=True)
    tr_a2, ch_a2, _ = SC.select_and_simulate(R['cands'], df, R['feat'], cpa2)
    a2m = np.array([c.the == 'A2' for c in ch_a2], bool)
    tr_a2only = tr_a2[a2m] if len(tr_a2) else tr_a2
    L += table([('Mặc định (A2 tắt, chặn 19:20–20:30 bật, có `b_from_exhausted`)', t), ('Chặn 19:20–20:30 TẮT', tr_us),
                ('Bỏ `b_from_exhausted`', tr_noexh), ('BẬT "lần 2" (định nghĩa siết G1/G2) — tất cả lệnh', tr_a2),
                ('… trong đó riêng lệnh "lần 2"', tr_a2only)], nd, f'{H}9 Nhóm tách riêng')
    t1 = CC.c1(R)
    d2, all2 = CC.c2(R)
    t3 = CC.c3(R)
    L += [f'### {H}10 Đối chứng (cùng SL/TP/chi phí, cùng neo)', '', HDR, row('**CORVEN (≥ 2 dấu hiệu)**', s_all),
          row('C1 — bỏ ③', stats(t1, nd))]
    c2m = None
    if len(d2):
        r2 = d2['r_c2_tb'].to_numpy()
        bs = np.random.default_rng(0).choice(r2, size=(10000, len(r2))).mean(axis=1)
        c2m = float(r2.mean())
        L.append(f"| C2 — ngẫu nhiên cùng phiên/giờ ±30′/hướng/rủi ro mbr ({len(all2)} lệnh giả) | {len(d2)} | – | "
                 f"{f2(100 * (all2 > 0).mean(), 1)} % | **{f2(c2m)}** | [{f2(np.percentile(bs, 2.5))}; {f2(np.percentile(bs, 97.5))}] | – | – | – |")
    for k in SC.SIGN_TYPES:
        L.append(row(f'C3 — chỉ đòi {TYPE_VN[k]}', stats(t3[k], nd)))
    L.append('')
    if len(d2):
        L += [f"C2 theo cặp: R thật − R đối chứng = {f2((d2['r_that'] - d2['r_c2_tb']).mean())} trên {len(d2)} lệnh. "
              f"Stacked có mặt ở {f2(100 * float(np.mean(['stacked' in c.types for c in ch])), 1)} % số lệnh.", '']
    st = CC.sl_then_tp(R)
    L += [f'### {H}11 "SL rồi vẫn chạm TP" so với mức nền (plan 7.3.4)', '',
          '| | 30 nến | 60 nến |', '|---|---|---|',
          f"| lệnh SL thật: sau nến dính SL, giá chạm TP gốc (n = {st['n_sl']}) | {f2(100 * st['real'][30], 1)} % | {f2(100 * st['real'][60], 1)} % |",
          f"| mức nền: nến ngẫu nhiên cùng phiên ±30′ quanh nến dính SL, giá đi 3R đúng hướng (n = {st['n_base']}) | "
          f"{f2(100 * st['base'][30], 1)} % | {f2(100 * st['base'][60], 1)} % |", '']
    wins, losses = pick_examples(t, ch)
    L += [f'### {H}12 5 thắng + 5 thua (rải đều theo thời gian)', '',
          '| | UTC | VN | thế | side | mốc / neo SL | dấu hiệu | vào | SL | TP | R sẵn | kết cục | R | ảnh |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for tag, lst in (('THANG', wins), ('THUA', losses)):
        for n, (i, c) in enumerate(lst):
            tt = t.iloc[i]
            fn = PC.plot_trade(df, R['feat'], tt, c, SHOTS2, f'{shots_prefix}_{tag}{n + 1}')
            L.append(f"| {tag.lower()} {n + 1} | {str(tt['t_utc'])[:16]} | {str(tt['t_vn'])[11:16]} | {c.the} | {'buy' if c.S > 0 else 'sell'} | "
                     f"{c.moc_used} / {c.anchor} | {'; '.join(v[0] for v in c.signs.values())} | {tt['entry']:.1f} | {tt['sl']:.1f} | {tt['tp']:.1f} | "
                     f"{f2(c.r_avail)} | {tt['outcome']} | {f2(float(tt['r']))} | [ảnh](corven_gd2v1_shots/{os.path.basename(fn)}) |")
    L.append('')
    p3 = [c for c in R['cands'] if R['good'][c.cf] and c.the != 'A2' and len(c.types) >= cp.need_signs]
    summ = dict(s=s_all, c1=stats(t1, nd), c2=c2m, st=st, n_p3=len(p3),
                r_nho=sum(1 for c in p3 if 'r_nho' in c.gates) / max(1, len(p3)),
                tran=sum(1 for c in p3 if 'tran_sl' in c.gates) / max(1, len(p3)),
                fb=sum(1 for c in p3 if c.anchor == 'pivot_fallback') / max(1, len(p3)),
                risk=float(np.median([c.risk / R['feat'].mbr[c.cf] for c in ch])) if ch else NAN,
                a2=stats(tr_a2only, nd), byA=stats(t[the == 'A'], nd), byB=stats(t[the == 'B'], nd),
                bysig={k: stats(t[nsg == k], nd) for k in sorted(set(nsg))})
    return L, summ


def _g(s, k, p=2, mult=1.0):
    v = s.get(k, NAN)
    return f2(v * mult, p) if v == v else '–'


def main():
    cut = SC.train_cut()
    bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    nd = len(set(df['session_id'].to_numpy()[good]))
    os.makedirs(SHOTS2, exist_ok=True)
    for old in os.listdir(SHOTS2):
        if old.endswith('.png'):
            os.remove(os.path.join(SHOTS2, old))
    runs = {}
    for anc in ('cu_thung', 'pivot'):
        runs[anc] = SC.run_gd1(bars, df, good, replace(SC.CP(), sl_anchor=anc))
    trades_csv(runs['cu_thung'], os.path.join(REPORT, '_corven_trades.csv'))
    trades_csv(runs['pivot'], os.path.join(REPORT, '_corven_trades_neo_pivot.csv'))
    secs, summ = {}, {}
    for anc, num, pre in (('cu_thung', 2, 'NEO1-CUTHUNG'), ('pivot', 3, 'NEO2-PIVOT')):
        secs[anc], summ[anc] = section(runs[anc], nd, num, ANCHOR_VN[anc], pre)
    L = ['# Benzo CORVEN — kết quả trên TRAIN', '',
         f'> Opus, 2026-11-09. **Chỉ TRAIN**: {nd} phiên dày, nến bar_idx 0…{cut} (tới {str(df["datetime"].iloc[-1])[:16]} UTC). '
         'TEST chưa chạy, chưa đọc. `kernel.simulate` (phí 0,2 giá/lệnh, chạm SL+TP cùng nến = SL, vào giá đóng CF, 1 lệnh mở), '
         'lệnh còn mở tới nến cuối phiên đóng `TIME`.',
         '> ⚠️ Mẫu TRAIN, chưa kiểm định ngoài mẫu — không dùng để vào lệnh thật.', '',
         '# GĐ2 vòng 1 — sửa định nghĩa theo plan mục 7.3 (không tính vào 3 vòng tinh chỉnh)', '',
         '- **A2 "lần 2" tắt mặc định** (G1); định nghĩa báo cáo siết: y = nến lập cực trị cú thủng (và là "lần 1"), x quét cực trị y '
         '≥ 1 tick và đóng về phía S ≥ tol so với cực trị y; CF = x hoặc 1–2 nến sau (G2).',
         '- **SL "lần 2" = cực trị toàn bộ cú thủng** (nến đóng ngoài → CF) + đệm (7.3.2). Thế A ở GĐ1 đã neo đúng như vậy '
         '(min/max từ nến đóng ngoài tới CF); lỗi neo ở ảnh THUA1 là của nhánh A2 (neo râu x) — nay sửa.',
         '- **Hai neo SL đo song song** (7.3.3): (1) neo cú thủng / mốc như 4b; (2) neo "đáy/đỉnh mới quét" = pivot 1 nến ngược S '
         'gần nhất trong [nến đóng ngoài − 10, CF] nằm phía −S của giá vào, + đệm; R_sẵn tính lại, sàn 1 mbr và trần 4 mbr giữ; '
         'không có pivot ⇒ dùng neo (1).', '',
         '## 1. So sánh hai neo SL', '',
         '| Neo SL | n | lệnh/ngày | WR | R TB | KTC 95 % | ΣR | max DD | C1 | C2 | A | B | rủi ro trung vị (mbr) | CF qua ③ bị loại vì R < 1,7 | bị trần SL | không có pivot (dùng neo 1) | SL rồi chạm TP 30/60 | mức nền 30/60 |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for anc in ('cu_thung', 'pivot'):
        u = summ[anc]
        s = u['s']
        L.append(f"| {ANCHOR_VN[anc]} | {s.get('n', 0)} | {_g(s, 'per_day')} | {_g(s, 'wr', 1, 100)} % | **{_g(s, 'avg')}** | "
                 f"[{_g(s, 'lo')}; {_g(s, 'hi')}] | {_g(s, 'sum', 1)} | {_g(s, 'dd', 1)} | {_g(u['c1'], 'avg')} | "
                 f"{f2(u['c2']) if u['c2'] is not None else '–'} | {_g(u['byA'], 'avg')} (n={u['byA'].get('n', 0)}) | "
                 f"{_g(u['byB'], 'avg')} (n={u['byB'].get('n', 0)}) | {f2(u['risk'])} | {f2(100 * u['r_nho'], 1)} % | {f2(100 * u['tran'], 1)} % | "
                 f"{'–' if anc == 'cu_thung' else f2(100 * u['fb'], 1) + ' %'} | {f2(100 * u['st']['real'][30], 0)} % / {f2(100 * u['st']['real'][60], 0)} % | "
                 f"{f2(100 * u['st']['base'][30], 0)} % / {f2(100 * u['st']['base'][60], 0)} % |")
    L += ['', 'Theo số dấu hiệu khác loại: ' + ' · '.join(
        f"{ANCHOR_VN[anc]}: " + ', '.join(f"{k} loại {_g(v, 'avg')} (n={v.get('n', 0)})" for k, v in summ[anc]['bysig'].items())
        for anc in ('cu_thung', 'pivot')), '',
          f"Nhóm báo cáo \"lần 2\" (bật A2): neo 1 → {summ['cu_thung']['a2'].get('n', 0)} lệnh \"lần 2\", R TB {_g(summ['cu_thung']['a2'], 'avg')}; "
          f"neo 2 → {summ['pivot']['a2'].get('n', 0)} lệnh, R TB {_g(summ['pivot']['a2'], 'avg')}.", '']
    L += [f'## 2. Bảng đầy đủ — {ANCHOR_VN["cu_thung"]}', ''] + secs['cu_thung']
    L += [f'## 3. Bảng đầy đủ — {ANCHOR_VN["pivot"]}', ''] + secs['pivot']
    L += open(os.path.join(REPORT, '_corven_gd2v1_notes.md'), encoding='utf-8').read().splitlines() + ['']
    old = open(os.path.join(REPORT, 'RESULTS-CORVEN-GD1.md'), encoding='utf-8').read().splitlines()
    L += ['---', '', '# (Lưu để so) GĐ1 — bản đầy đủ ở `RESULTS-CORVEN-GD1.md` (commit 47a531a): A2 bật, neo SL A2 theo râu x', '']
    L += ['#' + x if x.startswith('#') else x for x in old[1:]]
    with open(os.path.join(REPORT, 'RESULTS-CORVEN.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('\n'.join(L[:34]))
    return runs, summ


if __name__ == '__main__':
    main()
