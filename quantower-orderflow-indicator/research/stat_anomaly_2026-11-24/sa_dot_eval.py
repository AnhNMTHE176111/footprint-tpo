"""Bước 3: lưới chấm Bid/Ask = 2 mã x 5 khung x 170 cấu hình (165 ứng viên + 5 mốc đối chứng) x 3 đoạn.
Ra:
  out_r1_dot_calib.csv   — (cấu hình, mã, khung, đoạn, phạm vi ∈ {tat_ca, phiên Á/Âu/Mỹ, giờ 0..23}): số nến, chưa có ngưỡng, số giá trị > 0, số vượt thô,
                           mức danh nghĩa, mức đạt được, tỉ lệ nổ thực, tỉ số khớp, ngưỡng trung vị; dòng tat_ca thêm p10/p50/p90 khớp theo ngày + ngày tệ nhất.
  out_r1_dot_density.csv — sau gộp: chấm/nến, chấm/giờ theo phạm vi; dòng tat_ca thêm tỉ lệ nến không chấm, p50/p95/max chấm 1 nến, tỉ lệ nến > 5 chấm,
                           nến đầu phiên / TB phiên, tỉ lệ đỏ, tương quan với volume ngày tương đối.
  out_r1_dot_summary.csv — mỗi (cấu hình, mã, khung) trên ĐOẠN KIỂM: ĐẠT / TRƯỢT từng tiêu chí có ngưỡng ở PLAN 4.1, 4.2 kèm số.
  out_r1_dot_pick.csv    — số liệu đoạn CHỌN (dùng để chọn cấu hình cho bước 4, không nhìn đoạn kiểm).
Chạy: python sa_dot_eval.py"""
import time, numpy as np, pandas as pd
from sa_common import load_dot, SYMS, TFS, DOANS, _cache
from sa_dot_rules import evaluate, all_configs, forget
from sa_eval_lib import calib_and_density, verdicts

CFGS = all_configs()
calib, dens, summ_rows, pick = [], [], [], []
t0 = time.time()
for sym in SYMS:
    for m in TFS:
        ds = load_dot(sym, m)
        for cfg in CFGS:
            res = evaluate(ds, cfg)
            for doan in DOANS:
                c, d, s = calib_and_density(ds, res, cfg['name'], doan)
                calib += c; dens += d
                if doan == 'kiem':
                    v = verdicts(s, res.kind)
                    summ_rows.append(dict(cau_hinh=cfg['name'], phuong_an=cfg['pa'], kieu=res.kind, ma=sym, khung=m, doan='kiem', ti_le_no_o=s['ti_le_no_o'],
                                          nen_chua_co_nguong=s['nen_chua_co_nguong'], cham_nen=s['cham_nen'], cham_nen_p95=s.get('p95'), cham_nen_max=s.get('max'),
                                          ti_le_nen_tren5=s.get('tren5'), **v))
                if doan == 'chon':
                    kp = s['khop_phien']
                    pick.append(dict(cau_hinh=cfg['name'], phuong_an=cfg['pa'], kieu=res.kind, ma=sym, khung=m, doan='chon', khop_chung=s['khop_chung'],
                                     khop_phien_A=kp[0], khop_phien_Au=kp[1], khop_phien_My=kp[2], ti_le_no_o=s['ti_le_no_o'], cham_nen=s['cham_nen']))
        forget(ds); del _cache[(sym, m)]
        print(f'{sym} M{m} xong ({time.time() - t0:.0f} s)', flush=True)

S = pd.DataFrame(summ_rows)
# Đều giữa các khung (λ và kỷ lục): chấm/nến lớn nhất / nhỏ nhất trên M1..H1, đoạn kiểm
for (cf, sym), G in S.groupby(['cau_hinh', 'ma']):
    v = G.cham_nen.values; r = v.max() / v.min() if v.min() > 0 else np.inf
    kind = G.kieu.iloc[0]
    txt = f'{r:.3g} (' + '/'.join(f'{x:.3g}' for x in v) + ')'
    S.loc[G.index, 'deu_khung'] = (('ĐẠT ' if r <= 2.5 else 'TRƯỢT ') if kind in ('lam', 'rec') else 'BÁO ') + txt
crit = ['khop_chung', 'khop_phien', 'khop_gio', 'khop_ngay', 'deu_phien', 'dau_phien', 'deu_khung']
S['so_truot_41_42'] = S[crit].apply(lambda r: sum(str(x).startswith('TRƯỢT') for x in r), axis=1)
S.to_csv('out_r1_dot_summary.csv', index=False, float_format='%.5g')
pd.DataFrame(calib).to_csv('out_r1_dot_calib.csv', index=False, float_format='%.5g')
pd.DataFrame(dens).to_csv('out_r1_dot_density.csv', index=False, float_format='%.5g')
pd.DataFrame(pick).to_csv('out_r1_dot_pick.csv', index=False, float_format='%.5g')
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500); pd.set_option('display.max_colwidth', 60)
X = S[S.khung.isin([1, 5, 15])]
print(X.groupby('cau_hinh').so_truot_41_42.sum().sort_values().head(40).to_string())
print(f'xong ({time.time() - t0:.0f} s)')
