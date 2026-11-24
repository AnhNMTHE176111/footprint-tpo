"""Vòng 2, mục 6.2: bảng điểm chấm Bid/Ask của luật "thống kê" (12 cấu hình) trên GC, NQ, M1…H1, đoạn chọn + đoạn kiểm.
Ra: out_r2_dot_score.csv (mỗi cấu hình × mã × khung × đoạn một dòng: mọi tiêu chí + mật độ + theo ngày + ngưỡng theo phiên),
    out_r2_dot_calib.csv (độ khớp theo phạm vi), out_r2_dot_dst.csv (tuần đổi giờ), out_r2_dot_short.csv (chart nạp ít ngày),
    out_r2_dot_roll.csv (chuyển hợp đồng NQ), out_r2_dot_oddtf.csv (M3, M10, H4).
Tiêu chí có ngưỡng (giữ nguyên vòng 1): Khớp chung 0,8–1,25; Khớp theo phiên (cả ba 0,67–1,5, cao/thấp <= 1,8); Khớp theo giờ (>= 20 giờ trong 0,5–2);
  20 ô lớn nhất ngày >= 99%; 5 ô lớn nhất phiên >= 97%; cực trị rõ >= 97%; nhiễu <= 5%; chấm <= 3 hợp đồng <= 2%.
  "Khớp theo ngày" và "Nến đầu phiên" chỉ báo cáo.
Chạy: python sa2_dot_eval.py   (khoảng 20–30 phút)"""
import time, numpy as np, pandas as pd
from sa_common import load_dot, load_nq_full, _cache
from sa_eval_lib import calib_and_density, verdicts
from sa_oracle_lib import rulers
import sa2_lib as L

t0 = time.time()
CFGS = L.dot_configs()
SCORE, CALIB, DST, SHORT, ODD = [], [], [], [], []
CRIT = ['v_khop_chung', 'v_khop_phien', 'v_khop_gio', 'v_top20', 'v_top5', 'v_cuc_tri', 'v_nhieu', 'v_ti_hon']


def fmt(x):
    return 'nan' if x is None or not np.isfinite(x) else f'{x:.3f}'


def per_day_stats(ds, res, mask, ndot):
    hs = mask & res.has
    if not hs.any(): return {}
    s = pd.DataFrame(dict(d=ds.dayi[hs], c=ndot[hs], b=1)).groupby('d').sum()
    r = (s.c / s.b)
    q = np.quantile(r.values, [.1, .5, .9])
    return dict(ngay_cham_nen_min=r.min(), ngay_cham_nen_p10=q[0], ngay_cham_nen_p50=q[1], ngay_cham_nen_p90=q[2], ngay_cham_nen_max=r.max(),
                ngay_it_nhat=str(ds.days[r.idxmin()].date()), ngay_nhieu_nhat=str(ds.days[r.idxmax()].date()))


def score_one(ds, res, Rr, tops, doan, cfg):
    mask = ds.doan_mask(doan)
    c, d, s = calib_and_density(ds, res, cfg['name'], doan)
    for x in c: x['ma'] = ds.sym
    CALIB.extend(c)
    v = verdicts(s, res.kind)
    o = L.oracle2(ds, res, Rr, mask, ds.w, tops[doan])
    nexc = np.bincount(ds.sbar[res.exc], minlength=ds.nb); ndot = np.bincount(ds.sbar[res.dot], minlength=ds.nb)
    hs = mask & res.has
    row = dict(cau_hinh=cfg['name'], ma=ds.sym, khung=ds.m, doan=doan, so_nen=int(mask.sum()), ti_le_nen_co_nguong=hs.sum() / max(mask.sum(), 1))
    if res.src is not None:
        for k, nm in ((1, 'chinh'), (2, 'du_phong'), (0, 'chua_co')):
            row[f'ti_le_nen_{nm}'] = (mask & (res.src == k)).sum() / max(mask.sum(), 1)
    row.update(khop_chung=s['khop_chung'], ti_le_no_o=s['ti_le_no_o'])
    kp = s['khop_phien']
    row.update(khop_A=kp[0], khop_Au=kp[1], khop_My=kp[2])
    for k in ('khop_chung', 'khop_phien', 'khop_gio', 'khop_ngay', 'dau_phien'):
        row['v_' + k] = v[k]
    row['v_khop_ngay'] = 'BÁO ' + v['khop_ngay'].split(' ', 1)[1] if v['khop_ngay'] != 'KHÔNG ÁP DỤNG' else v['khop_ngay']
    row['v_dau_phien'] = 'BÁO ' + v['dau_phien'].split(' ', 1)[1]
    for g in ('top20', 'top5', 'cuc_tri'):
        row[g] = o[g]; row[f'{g}_so_o'] = o[f'{g}_so_o']; row[f'{g}_sot_chua_nguong'] = o[f'{g}_sot_chua_nguong']; row[f'{g}_sot_vi_nguong'] = o[f'{g}_sot_vi_nguong']
    row.update(nhieu=o['nhieu'], le3=o['le3'], le5=o['le5'], p_hat=o['p_hat'], so_cham=o['so_cham'])
    row['v_top20'] = ('ĐẠT ' if o['top20'] >= 0.99 else 'TRƯỢT ') + fmt(o['top20'])
    row['v_top5'] = ('ĐẠT ' if o['top5'] >= 0.97 else 'TRƯỢT ') + fmt(o['top5'])
    row['v_cuc_tri'] = (('ĐẠT ' if o['cuc_tri'] >= 0.97 else 'TRƯỢT ') + fmt(o['cuc_tri'])) if np.isfinite(o['cuc_tri']) else 'TRƯỢT nan'
    row['v_nhieu'] = ('ĐẠT ' if np.isfinite(o['nhieu']) and o['nhieu'] <= 0.05 else 'TRƯỢT ') + fmt(o['nhieu'])
    row['v_ti_hon'] = ('ĐẠT ' if np.isfinite(o['le3']) and o['le3'] <= 0.02 else 'TRƯỢT ') + fmt(o['le3'])
    if res.kind != 'p':
        for k in ('v_khop_chung', 'v_khop_phien', 'v_khop_gio'): row[k] = 'KHÔNG ÁP DỤNG'
    row['so_truot'] = sum(str(row[k]).startswith('TRƯỢT') for k in CRIT)
    row['truot_gi'] = ';'.join(k[2:] for k in CRIT if str(row[k]).startswith('TRƯỢT'))
    # mật độ
    dpb = ndot[hs]; xpb = nexc[hs]
    row['cham_nen'] = dpb.mean() if hs.any() else np.nan
    for i, sn in enumerate(('A', 'Au', 'My')):
        k = hs & (ds.ses == i); row[f'cham_nen_{sn}'] = ndot[k].mean() if k.any() else np.nan
    if hs.any():
        row.update(cham_1nen_p50=np.quantile(dpb, .5), cham_1nen_p95=np.quantile(dpb, .95), cham_1nen_max=int(dpb.max()),
                   vuot_tho_nen=xpb.mean(), vuot_tho_1nen_p95=np.quantile(xpb, .95), vuot_tho_1nen_max=int(xpb.max()))
        th = res.thr
        for i, sn in enumerate(('A', 'Au', 'My')):
            k = hs & (ds.ses == i)
            if k.any():
                q = np.quantile(th[k], [.1, .5, .9]); row[f'nguong_{sn}_p10'], row[f'nguong_{sn}_p50'], row[f'nguong_{sn}_p90'] = q
        row['ti_le_nen_nguong_duoi5'] = (th[hs] < 5).mean()
    row['ti_le_do'] = d[0].get('ti_le_do', np.nan); row['tuong_quan_vol_ngay'] = d[0].get('tuong_quan_cham_vol_ngay', np.nan)
    row.update(per_day_stats(ds, res, mask, ndot))
    return row


def hour_ok(ds, res, bar_sel):
    hs = bar_sel & res.has
    nexc = np.bincount(ds.sbar[res.exc], minlength=ds.nb)
    df = pd.DataFrame(dict(h=ds.hour[hs], x=nexc[hs], n=ds.npos[hs], a=np.where(np.isfinite(res.nom), res.nom, 0)[hs], b=1)).groupby('h').sum()
    if not len(df): return 0, 0, ''
    r = (df.x / df.n) / (df.a / df.b)
    ok = int(((r >= .5) & (r <= 2)).sum())
    bad = ' '.join(f'{h:02d}:{v:.2f}' for h, v in r.items() if not (.5 <= v <= 2))
    return ok, len(r), bad


def dot_keys(ds, res, keep=None):
    k = res.dot if keep is None else (res.dot & keep[ds.sbar])
    i = np.nonzero(k)[0]
    return set(zip(ds.t.values[ds.sbar[i]].astype('datetime64[m]').astype(np.int64), ds.sside[i], ds.stk[i]))


for sym in ('GC', 'NQ'):
    for m in (1, 5, 15, 30, 60):
        ds = load_dot(sym, m); Rr = rulers(ds)
        tops = {d: L.top_sets_f(ds, ds.doan_mask(d)) for d in ('chon', 'kiem')}
        for cfg in CFGS:
            res = L.eval_dot(ds, cfg)
            for doan in ('chon', 'kiem'):
                SCORE.append(score_one(ds, res, Rr, tops, doan, cfg))
            # tuần đổi giờ (theo ngày chấm điểm 26–30/10 và 02–06/11) + hai tuần trước mỗi tuần
            if m in (1, 5, 15) and res.kind == 'p':
                for lab, a, b in (('26-30/10', '2026-10-26', '2026-10-30'), ('02-06/11', '2026-11-02', '2026-11-06'),
                                  ('2 tuần trước 26/10', '2026-10-12', '2026-10-23'), ('2 tuần trước 02/11', '2026-10-19', '2026-10-30')):
                    sel = (ds.tday >= a) & (ds.tday <= b)
                    if not sel.any(): continue
                    ok, nh, bad = hour_ok(ds, res, np.asarray(sel))
                    DST.append(dict(cau_hinh=cfg['name'], ma=sym, khung=m, tuan=lab, so_gio_dat=ok, so_gio_co_nen=nh, gio_lech=bad))
            L.forget(ds)
        # chart nạp ít ngày: cắt còn 8 ngày giao dịch cuối (ngày của luật, giờ Chicago)
        if m in (1, 5, 15):
            day, _, _ = L.rule_day_slot(ds.t, m, 'ct')
            ud = np.unique(day); keep = day >= ud[-8]
            sub = ds.subset(keep)
            for mind in (1, 2, 3):
                for T in (120, 240):
                    cfg = dict(L.BASE); cfg.update(mind=mind, T=T, name=f'toi_thieu_{mind}_T{T}', pa='thong_ke')
                    rf = L.eval_dot(ds, cfg); rs = L.eval_dot(sub, cfg)
                    A = dot_keys(ds, rf, keep); B = dot_keys(sub, rs)
                    dA = pd.Series([x[0] for x in A]); dB = pd.Series([x[0] for x in B])
                    # theo ngày
                    dmap = dict(zip(ds.t.values.astype('datetime64[m]').astype(np.int64), day))
                    per = {}
                    for x in A | B:
                        dd = dmap[x[0]]; c = per.setdefault(dd, [0, 0]); c[1] += 1; c[0] += (x in A and x in B)
                    j = {str(np.datetime64(int(dd), 'D')): c[0] / c[1] for dd, c in sorted(per.items())}
                    SHORT.append(dict(ma=sym, khung=m, toi_thieu=mind, T=T, cham_toan_bo=len(A), cham_nap_it=len(B), chung=len(A & B), hop=len(A | B),
                                      trung=len(A & B) / max(len(A | B), 1), theo_ngay=' '.join(f'{k[5:]}:{v:.3f}' for k, v in j.items()),
                                      ngay_thap_nhat=min(j.values()) if j else np.nan))
                    L.forget(sub)
            L.forget(sub)
        _cache.pop((sym, m), None); L.forget(ds)
        print(f'{sym} M{m} xong ({time.time() - t0:.0f} s)', flush=True)

pd.DataFrame(SCORE).to_csv('out_r2_dot_score.csv', index=False, float_format='%.5g')
pd.DataFrame(CALIB).to_csv('out_r2_dot_calib.csv', index=False, float_format='%.5g')
pd.DataFrame(DST).to_csv('out_r2_dot_dst.csv', index=False)
pd.DataFrame(SHORT).to_csv('out_r2_dot_short.csv', index=False, float_format='%.5g')

# chuyển hợp đồng: NQ toàn bộ file, M1 / M5, cấu hình gốc
ROLL = []
base = CFGS[0]
for m in (1, 5):
    ds = load_nq_full(m); res = L.eval_dot(ds, base)
    nexc = np.bincount(ds.sbar[res.exc], minlength=ds.nb); ndot = np.bincount(ds.sbar[res.dot], minlength=ds.nb)
    k = res.has & (ds.tday >= '2026-09-07') & (ds.tday <= '2026-09-25')
    dd = pd.DataFrame(dict(d=ds.tday[k].strftime('%Y-%m-%d'), x=nexc[k], n=ds.npos[k], c=ndot[k], b=1,
                           a=res.nom[k], s1=(res.src[k] == 1))).groupby('d').sum()
    for d_, r in dd.iterrows():
        ROLL.append(dict(ma='NQ_toan_bo', khung=m, ngay=d_, cham_nen=r.c / r.b, ti_so_khop=(r.x / r.n) / (r.a / r.b), ti_le_nen_nguong_chinh=r.s1 / r.b))
    L.forget(ds)
pd.DataFrame(ROLL).to_csv('out_r2_dot_roll.csv', index=False, float_format='%.4g')
print(f'chuyển hợp đồng xong ({time.time() - t0:.0f} s)', flush=True)

# khung lạ
for sym in ('GC', 'NQ'):
    for m in (3, 10, 240):
        ds = L.build_tf_from_m1(sym, m)
        res = L.eval_dot(ds, base)
        for doan in ('chon', 'kiem', 'tat_ca'):
            mask = ds.doan_mask(doan)
            c, d, s = calib_and_density(ds, res, base['name'], doan)
            hs = mask & res.has
            ODD.append(dict(ma=sym, khung=m, doan=doan, so_nen=int(mask.sum()), ti_le_nen_co_nguong=hs.sum() / max(mask.sum(), 1),
                            ti_le_nen_chinh=(mask & (res.src == 1)).sum() / max(mask.sum(), 1), ti_le_nen_du_phong=(mask & (res.src == 2)).sum() / max(mask.sum(), 1),
                            cham_nen=s['cham_nen'], khop_chung=s['khop_chung'], khop_A=s['khop_phien'][0], khop_Au=s['khop_phien'][1], khop_My=s['khop_phien'][2]))
        L.forget(ds)
        print(f'{sym} M{m} (khung lạ) xong ({time.time() - t0:.0f} s)', flush=True)
pd.DataFrame(ODD).to_csv('out_r2_dot_oddtf.csv', index=False, float_format='%.5g')
print(f'xong ({time.time() - t0:.0f} s)')
