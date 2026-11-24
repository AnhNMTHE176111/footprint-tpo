"""Bước 6 (Big Trade): mô tả, mặt bằng cho phương án lai, độ khớp + độ đều, tỉ lệ nến có ngưỡng trên nhật ký sống.
Dữ liệu (nhật ký lệnh đơn, chỉ nến có số liệu): GC 31/08 -> 23/09 (16 phiên: 10 đầu = đoạn chọn, 6 cuối = đoạn kiểm);
NQ 25/10 -> 02/11 (6 phiên, KHÔNG có đoạn kiểm: chỉ đoạn tat_ca); GClive 09/11 -> 24/11 đứt quãng (đoạn kiểm thứ hai, chỉ cuon và ky_luc).
Ra: out_r1_bt_profile.csv, out_r1_bt_level.csv, out_r1_bt_calib.csv, out_r1_bt_density.csv, out_r1_bt_summary.csv, out_r1_bt_avail.csv, out_r1_bt_pick.csv
Chạy: python sa_bt_eval.py"""
import time, numpy as np, pandas as pd
from sa_common import load_dot, TFS, SES_NAMES, _cache
import sa_dot_rules as R
from sa_bt_rules import BtData, evaluate_bt, bt_configs, attach_L, LAI_L
from sa_eval_lib import calib_and_density, verdicts
from bt_common import load_m1, to_tf

KEYS = ('GC', 'NQ', 'GClive')
DOANS_OF = {'GC': ('chon', 'kiem', 'tat_ca'), 'NQ': ('tat_ca',), 'GClive': ('kiem', 'tat_ca')}
SUMMARY_DOAN = {'GC': 'kiem', 'NQ': 'tat_ca', 'GClive': 'kiem'}
NOTE = {'GC': '', 'NQ': '6 phiên, không có đoạn kiểm', 'GClive': 'nhật ký sống đứt quãng, đoạn kiểm thứ hai'}
t0 = time.time()
M1 = {k: load_m1(k) for k in KEYS}
BT = {}
for k in KEYS:
    for m in TFS:
        bt = BtData(k, m, to_tf(M1[k], m))
        if k != 'GClive':
            attach_L(bt, load_dot(k, m)); _cache.pop((k, m), None)
        BT[(k, m)] = bt
for k in ('GC', 'NQ'):
    for m in TFS:
        _cache.pop((k, m), None)
print(f'nạp xong ({time.time() - t0:.0f} s)', flush=True)

# ---------------- mô tả ----------------
rows = []
for (k, m), bt in BT.items():
    for doan in DOANS_OF[k]:
        dm = bt.doan_mask(doan)
        scopes = [('tat_ca', dm)] + [('phien_' + s, dm & (bt.ses == i)) for i, s in enumerate(SES_NAMES)] + [(f'gio_{h:02d}', dm & (bt.hour == h)) for h in range(24)]
        for lb, bm in scopes:
            sm = bm[bt.sbar]; v = bt.sval[sm]
            if bm.sum() == 0 or len(v) == 0: continue
            q = np.quantile(v, [.5, .9, .99, .995, .999])
            day = bt.dayi[bt.sbar[sm]]
            s = pd.Series(v).groupby(day); p = s.quantile(.99)[s.size() >= 100]
            dq = np.quantile(p.values, [.1, .5, .9]) if len(p) else [np.nan] * 3
            rows.append(dict(ma=k, khung=m, doan=doan, ghi_chu=NOTE[k], pham_vi=lb, so_nen=int(bm.sum()), o_moi_nen=len(v) / bm.sum(), p50=q[0], p90=q[1], p99=q[2], p995=q[3], p999=q[4],
                             lon_nhat_nen_p50=np.median(bt.bmax[bm]), so_ngay=len(p), p99_ngay_p10=dq[0], p99_ngay_p50=dq[1], p99_ngay_p90=dq[2]))
pd.DataFrame(rows).to_csv('out_r1_bt_profile.csv', index=False, float_format='%.5g')
print(f'mô tả xong ({time.time() - t0:.0f} s)', flush=True)

# ---------------- mặt bằng cho lai ----------------
rows = []; lai_ok = {}
for k in ('GC', 'NQ'):
    for m in TFS:
        bt = BT[(k, m)]
        okb = np.all([np.isfinite(bt.Lb[L]) for L in LAI_L], 0)
        sm = okb[bt.sbar]
        g = bt.dayi[bt.sbar[sm]] * 3 + bt.ses[bt.sbar[sm]]
        ses = bt.ses[bt.sbar[sm]]
        base = None; lai_ok[(k, m)] = []
        for L in ('mot_tho',) + LAI_L:
            x = bt.sval[sm].astype(float) if L == 'mot_tho' else bt.sval[sm] / bt.Lb[L][bt.sbar[sm]]
            s = pd.Series(x).groupby(g)
            p = s.quantile(.99)[s.size() >= 100]
            cv = p.std(ddof=0) / p.mean()
            my = np.quantile(x[ses == 2], .99); a = np.quantile(x[ses == 0], .99)
            if L == 'mot_tho': base = cv
            ok = (L != 'mot_tho') and cv <= 0.7 * base
            if ok: lai_ok[(k, m)].append(L)
            rows.append(dict(ma=k, khung=m, doan='tat_ca', mat_bang=L, so_o=int(sm.sum()), so_nhom_ngay_phien=len(p), p99_tb=p.mean(), he_so_bien_thien=cv,
                             so_voi_mot_tho=cv / base if base else np.nan, ti_so_My_A=my / a, dat_giam_30=('ĐẠT' if ok else ('—' if L == 'mot_tho' else 'KHÔNG'))))
LV = pd.DataFrame(rows); LV.to_csv('out_r1_bt_level.csv', index=False, float_format='%.5g')
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
print(LV.to_string(index=False))
print('L đạt giảm hệ số biến thiên >= 30%:', {f'{k}M{m}': v for (k, m), v in lai_ok.items()}, flush=True)
# lai chỉ đo tiếp với L đạt ở ít nhất một (mã, khung); chạy L đó trên mọi khung của mã để có so sánh giữa các khung
LAI_RUN = sorted({L for v in lai_ok.values() for L in v}, key=LAI_L.index)
print('lai đo tiếp với:', LAI_RUN)

# ---------------- khớp + độ đều ----------------
calib, dens, summ, pick, avail = [], [], [], [], []
for (k, m), bt in BT.items():
    cfgs = bt_configs(k, LAI_RUN if k != 'GClive' else ())
    for cfg in cfgs:
        res = evaluate_bt(bt, cfg)
        if k == 'GClive':
            avail.append(dict(cau_hinh=cfg['name'], phuong_an=cfg['pa'], ma=k, khung=m, doan='tat_ca', so_nen=bt.nb, ti_le_nen_co_nguong=res.has.mean(),
                              ti_le_nen_co_nguong_phien='/'.join(f'{res.has[bt.ses == i].mean():.3f}' for i in range(3))))
            if cfg['pa'] not in ('cuon', 'ky_luc') and not cfg['pa'].startswith('dc_'):
                continue
        for doan in DOANS_OF[k]:
            c, d, s = calib_and_density(bt, res, cfg['name'], doan, extra=dict(ghi_chu=NOTE[k]))
            calib += c; dens += d
            if doan == SUMMARY_DOAN[k]:
                v = verdicts(s, res.kind)
                summ.append(dict(cau_hinh=cfg['name'], phuong_an=cfg['pa'], kieu=res.kind, ma=k, khung=m, doan=doan, ghi_chu=NOTE[k], ti_le_no_o=s['ti_le_no_o'],
                                 nen_chua_co_nguong=s['nen_chua_co_nguong'], vong_nen=s['cham_nen'], vong_nen_p95=s.get('p95'), vong_nen_max=s.get('max'), ti_le_nen_tren5=s.get('tren5'), **v))
            if k == 'GC' and doan == 'chon':
                kp = s['khop_phien']
                pick.append(dict(cau_hinh=cfg['name'], phuong_an=cfg['pa'], kieu=res.kind, ma=k, khung=m, doan='chon', khop_chung=s['khop_chung'],
                                 khop_phien_A=kp[0], khop_phien_Au=kp[1], khop_phien_My=kp[2], ti_le_no_o=s['ti_le_no_o'], vong_nen=s['cham_nen']))
    R._memo.clear()
    print(f'{k} M{m} xong ({time.time() - t0:.0f} s)', flush=True)

S = pd.DataFrame(summ)
for (cf, k), G in S.groupby(['cau_hinh', 'ma']):
    v = G.vong_nen.values; r = v.max() / v.min() if v.min() > 0 else np.inf
    kind = G.kieu.iloc[0]
    S.loc[G.index, 'deu_khung'] = (('ĐẠT ' if r <= 2.5 else 'TRƯỢT ') if kind in ('lam', 'rec') else 'BÁO ') + f'{r:.3g} (' + '/'.join(f'{x:.3g}' for x in v) + ')'
crit = ['khop_chung', 'khop_phien', 'khop_gio', 'khop_ngay', 'deu_phien', 'dau_phien', 'deu_khung']
S['so_truot_41_42'] = S[crit].apply(lambda r: sum(str(x).startswith('TRƯỢT') for x in r), axis=1)
S.to_csv('out_r1_bt_summary.csv', index=False, float_format='%.5g')
pd.DataFrame(calib).to_csv('out_r1_bt_calib.csv', index=False, float_format='%.5g')
pd.DataFrame(dens).rename(columns=lambda c: c.replace('cham', 'vong')).to_csv('out_r1_bt_density.csv', index=False, float_format='%.5g')
pd.DataFrame(pick).to_csv('out_r1_bt_pick.csv', index=False, float_format='%.5g')
pd.DataFrame(avail).to_csv('out_r1_bt_avail.csv', index=False, float_format='%.5g')
print(f'xong ({time.time() - t0:.0f} s)')
