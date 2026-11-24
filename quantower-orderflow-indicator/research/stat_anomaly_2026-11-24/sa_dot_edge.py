"""Bước 5: tám ca biên của PLAN 4.4 cho chấm, trên tối đa 10 cấu hình tốt nhất sau bước 4 (mỗi phương án ít nhất một) + mốc đối chứng.
Chọn "tốt nhất": ít tiêu chí TRƯỢT nhất (4.1 + 4.2 ở out_r1_dot_summary.csv và 4.3 ở out_r1_dot_oracle.csv), đoạn kiểm, (GC, NQ) x (M1, M5, M15).
Phương án không có cấu hình nào ở bước 4 (không đạt Khớp chung ở đoạn chọn) thì lấy cấu hình trượt ít nhất 4.1 + 4.2.
Ra: out_r1_dot_edge.csv (dạng dài: cấu hình, mã, khung, đoạn, ca biên, chỉ số, giá trị)."""
import time, numpy as np, pandas as pd
from sa_common import load_dot, load_nq_full, SYMS, TFS, _cache
from sa_dot_rules import evaluate, all_configs, forget
from sa_eval_lib import grouped, per_bar

BYNAME = {c['name']: c for c in all_configs()}
REF = ['dc_dang_chay_khong_sot', 'dc_dang_chay_it_nhieu', 'dc_pct10']


def pick(nmax=10):
    S = pd.read_csv('out_r1_dot_summary.csv'); O = pd.read_csv('out_r1_dot_oracle.csv')
    S = S[S.khung.isin([1, 5, 15]) & ~S.phuong_an.str.startswith('dc_')]
    O = O[(O.doan == 'kiem') & O.khung.isin([1, 5, 15]) & ~O.phuong_an.str.startswith('dc_')]
    f1 = S.groupby('cau_hinh').so_truot_41_42.sum()
    f2 = O.groupby('cau_hinh').so_truot_43.sum()
    T = pd.DataFrame(dict(f41_42=f1)).join(pd.DataFrame(dict(f43=f2)), how='left')
    T['co_buoc4'] = T.f43.notna(); T['tong'] = T.f41_42 + T.f43.fillna(0)
    T['pa'] = [BYNAME[n]['pa'] for n in T.index]
    T = T.sort_values(['co_buoc4', 'tong', 'f41_42'], ascending=[False, True, True])
    chosen = []
    for pa, G in T.groupby('pa', sort=False):
        chosen.append(G.index[0])
    for n in T.index:
        if len(chosen) >= nmax: break
        if n not in chosen: chosen.append(n)
    return chosen[:max(nmax, len(set(T.pa)))], T


def khop(ds, res, nexc, mask):
    G = grouped(ds, res, nexc, mask, np.zeros(ds.nb, np.int64), 1)
    return G['ti_so_khop'][0], G['nh'][0]


def dots_per_bar(res, ndot, mask):
    k = mask & res.has
    return ndot[k].mean() if k.any() else np.nan


def edge(ds, cfg, rows, extra_cases=True):
    res = evaluate(ds, cfg); nexc, ndot, nred = per_bar(ds, res)
    base = dict(cau_hinh=cfg['name'], phuong_an=cfg['pa'], ma=ds.tag, khung=ds.m, doan='tat_ca')
    add = lambda ca, cs, v: rows.append(dict(base, ca_bien=ca, chi_so=cs, gia_tri=v))
    allm = np.ones(ds.nb, bool)
    # 1 đầu chart
    first = int(np.argmax(res.has)) if res.has.any() else ds.nb
    add('1_dau_chart', 'so_nen_dau_chua_co_nguong', first)
    add('1_dau_chart', 'ti_le_nen_chua_co_nguong', 1 - res.has.mean())
    if not extra_cases:
        # NQ toàn bộ: ca 6 — khớp theo ngày 07/09..25/09 và số ngày để về 0,5–2
        nd = len(ds.days)
        G = grouped(ds, res, nexc, allm, ds.dayi.astype(np.int64), nd)
        kd = pd.Series(G['ti_so_khop'], index=ds.days)
        for d, v in kd['2026-09-07':'2026-09-25'].items():
            add('6_doi_hop_dong', f'khop_ngay_{d.date()}', v)
        good = ((kd >= 0.5) & (kd <= 2)).values
        start = int(np.searchsorted(ds.days.values, np.datetime64('2026-09-14')))
        days_needed = np.nan
        for i in range(start, nd - 2):
            if good[i] and good[i + 1] and good[i + 2]:
                days_needed = i - start; break
        add('6_doi_hop_dong', 'so_ngay_tu_1409_toi_khi_khop_ngay_trong_0.5_2_ba_ngay_lien', days_needed)
        s0 = int(np.searchsorted(ds.days.values, np.datetime64('2026-08-27')))
        for i in range(s0, nd - 2):
            if good[i] and good[i + 1] and good[i + 2]:
                add('6_doi_hop_dong', 'ngay_dau_tien_khop_trong_0.5_2_ba_ngay_lien', str(ds.days[i].date())); break
        return
    # 2 phụ thuộc lịch sử đã nạp: 5 ngày cuối, nạp thêm L ngày trước đó
    nd = len(ds.days)
    full_last = ds.dayi >= nd - 5
    key = lambda d, r, bm: set(zip(d.t.values[d.sbar[r.dot & bm[d.sbar]]], d.sside[r.dot & bm[d.sbar]], d.stk[r.dot & bm[d.sbar]]))
    A = key(ds, res, full_last)
    for L in (3, 7, 15):
        sub = ds.subset(ds.dayi >= nd - 5 - L)
        r2 = evaluate(sub, cfg)
        B = key(sub, r2, sub.dayi >= len(sub.days) - 5)
        add('2_lich_su_da_nap', f'trung_khi_nap_{L}_ngay_truoc', len(A & B) / max(len(A | B), 1))
        forget(sub)
    # 3 sau nghỉ cuối tuần: 20 nến đầu của ngày giao dịch thứ Hai (mở 22:00 chủ nhật) so với 20 nến đầu các ngày khác
    first_of_day = np.r_[True, ds.dayi[1:] != ds.dayi[:-1]]
    start_idx = np.nonzero(first_of_day)[0]
    pos = np.zeros(ds.nb, np.int64)
    for a, e in zip(start_idx, np.r_[start_idx[1:], ds.nb]): pos[a:e] = np.arange(e - a)
    head = pos < 20
    monday = ds.days.weekday[ds.dayi] == 0
    for lb, mk in (('thu_hai', head & monday), ('ngay_khac', head & ~monday)):
        k, n = khop(ds, res, nexc, mk)
        add('3_sau_cuoi_tuan', f'cham_nen_{lb}', dots_per_bar(res, ndot, mk)); add('3_sau_cuoi_tuan', f'khop_{lb}', k)
    # 4 quanh giờ nghỉ hằng ngày
    for h in (20, 21, 22, 23):
        mk = ds.hour == h
        if not mk.any(): continue
        add('4_gio_nghi', f'gio_{h}_ti_le_nen_chua_co_nguong', 1 - res.has[mk].mean())
        add('4_gio_nghi', f'gio_{h}_cham_nen', dots_per_bar(res, ndot, mk))
    # 5 tuần sau đổi giờ: khớp theo giờ
    wk = {'tuan_2610_3010': ('2026-10-26', '2026-10-30'), 'tuan_0211_0611': ('2026-11-02', '2026-11-06'), 'hai_tuan_truoc_1210_2310': ('2026-10-12', '2026-10-23')}
    for lb, (a, b) in wk.items():
        mk = (ds.tday >= a) & (ds.tday <= b)
        if not mk.any(): continue
        G = grouped(ds, res, nexc, mk, ds.hour.astype(np.int64), 24)
        kh = G['ti_so_khop']; pres = G['nh'] > 0
        good = int(np.sum(pres & (kh >= 0.5) & (kh <= 2)))
        add('5_doi_gio', f'{lb}_so_gio_khop_0.5_2', f'{good}/{int(pres.sum())}')
        lg = np.where(pres & (kh > 0), np.abs(np.log(np.where(kh > 0, kh, 1))), np.where(pres, 99, -1))
        wh = int(np.argmax(lg)); add('5_doi_gio', f'{lb}_gio_te_nhat', f'{wh:02d}: {kh[wh]:.3g}')
        for h in (6, 7, 12, 13, 14, 20, 21):
            add('5_doi_gio', f'{lb}_khop_gio_{h:02d}', kh[h] if pres[h] else np.nan)
    # 7 nến mỏng
    thin = (ds.nl <= 3) & res.has
    add('7_nen_mong', 'so_nen_mong', int(thin.sum()))
    if thin.any():
        add('7_nen_mong', 'ti_le_nen_mong_co_cham', (ndot[thin] > 0).mean())
        v = ds.sval[res.dot & thin[ds.sbar]]
        add('7_nen_mong', 'gia_tri_cham_trung_vi', np.median(v) if len(v) else np.nan)
        add('7_nen_mong', 'gia_tri_cham_le_3_ti_le', (v <= 3).mean() if len(v) else np.nan)
    # 8 ngày rất vắng
    dv = np.bincount(ds.dayi, weights=ds.tot, minlength=nd)
    prev = pd.Series(dv).shift(1).rolling(10, min_periods=5).mean().values
    low = np.nonzero(dv < 0.5 * prev)[0]
    add('8_ngay_vang', 'cac_ngay', ' '.join(str(ds.days[i].date()) for i in low))
    for lb, ids in (('ngay_vang', low), ('ngay_lien_sau', low + 1)):
        ids = ids[ids < nd]
        mk = np.isin(ds.dayi, ids)
        if mk.any():
            k, n = khop(ds, res, nexc, mk)
            add('8_ngay_vang', f'khop_{lb}', k); add('8_ngay_vang', f'cham_nen_{lb}', dots_per_bar(res, ndot, mk))
    allk, _ = khop(ds, res, nexc, allm)
    add('0_tham_chieu', 'khop_tat_ca', allk); add('0_tham_chieu', 'cham_nen_tat_ca', dots_per_bar(res, ndot, allm))


if __name__ == '__main__':
    names, T = pick()
    print('Chọn cho ca biên:'); print(T.loc[names].to_string())
    cfgs = [BYNAME[n] for n in names + REF]
    rows = []; t0 = time.time()
    for sym in SYMS:
        for m in TFS:
            ds = load_dot(sym, m)
            for cfg in cfgs:
                edge(ds, cfg, rows)
            forget(ds); del _cache[(sym, m)]
            print(f'{sym} M{m} xong ({time.time() - t0:.0f} s)', flush=True)
    for m in (1, 5):
        ds = load_nq_full(m)
        for cfg in cfgs:
            edge(ds, cfg, rows, extra_cases=False)
        forget(ds); del _cache[('NQfull', m)]
        print(f'NQ toàn bộ M{m} xong ({time.time() - t0:.0f} s)', flush=True)
    D = pd.DataFrame(rows)
    D.to_csv('out_r1_dot_edge.csv', index=False, float_format='%.5g')
    print(f'xong ({time.time() - t0:.0f} s)')
