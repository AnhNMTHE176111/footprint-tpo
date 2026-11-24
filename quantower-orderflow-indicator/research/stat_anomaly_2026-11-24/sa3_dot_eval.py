"""Vòng 3, mục 6.2 (r2_review.md): bảng điểm chấm Bid/Ask, 8 cấu hình, GC và NQ x M1…H1, đoạn chọn + đoạn kiểm.
Cấu hình: nen_moi (giờ Chicago, K 5, có lân cận, tối thiểu 2 ngày, T 120, p 2%, sel nms); mỗi lần đổi một yếu tố: sel_lmax, khong_lan_can, p1, p0.5,
toi_thieu_1_ngay; hai mốc đối chứng luật đang chạy (dc_dang_chay_khong_sot, dc_dang_chay_it_nhieu).
Tiêu chí: Khớp chung 0,8–1,25; Khớp theo phiên; Khớp theo giờ; 20 ô lớn nhất ngày >= 99%; 5 ô lớn nhất phiên >= 97%; cực trị rõ >= 97% (ba tiêu chí này
  tính trên số "NHÌN THẤY" = có chấm cùng nến, cùng bên, cách <= w tick; số cũ "vượt thô hoặc gần chấm" báo kèm); nhiễu <= 5%; chấm <= 3 hợp đồng <= 2%.
Ra: out_r3_dot_score.csv, out_r3_dot_t5gio.csv (ô "5 lớn nhất phiên" bị sót theo giờ UTC, NQ M15/M30), out_r3_dot_short.csv (nạp 3 / 8 / 15 ngày).
Chạy: python sa3_dot_eval.py"""
import time, numpy as np, pandas as pd
from sa_common import load_dot, _cache
from sa_eval_lib import calib_and_density, verdicts
from sa_oracle_lib import rulers
import sa3_lib as L

t0 = time.time()
CFGS = L.dot_configs()
SCORE, T5, SHORT = [], [], []
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
    v = verdicts(s, res.kind)
    o = L.oracle3(ds, res, Rr, mask, ds.w, tops[doan])
    nexc = np.bincount(ds.sbar[res.exc], minlength=ds.nb); ndot = np.bincount(ds.sbar[res.dot], minlength=ds.nb)
    hs = mask & res.has
    row = dict(cau_hinh=cfg['name'], ma=ds.sym, khung=ds.m, doan=doan, so_nen=int(mask.sum()), ti_le_nen_co_nguong=hs.sum() / max(mask.sum(), 1))
    if res.src is not None:
        for k, nm in ((1, 'chinh'), (2, 'du_phong'), (0, 'chua_co')):
            row[f'ti_le_nen_{nm}'] = (mask & (res.src == k)).sum() / max(mask.sum(), 1)
    row.update(khop_chung=s['khop_chung'], ti_le_no_o=s['ti_le_no_o'])
    kp = s['khop_phien']
    row.update(khop_A=kp[0], khop_Au=kp[1], khop_My=kp[2])
    for k in ('khop_chung', 'khop_phien', 'khop_gio'):
        row['v_' + k] = v[k]
    for g in ('top20', 'top5', 'cuc_tri'):
        row[f'{g}_cu'] = o[g]; row[f'{g}_nt'] = o[f'{g}_nt']; row[f'{g}_so_o'] = o[f'{g}_so_o']
        row[f'{g}_nt_sot'] = o[f'{g}_nt_sot']; row[f'{g}_nt_sot_vuot'] = o.get(f'{g}_nt_sot_vuot', 0)
        row[f'{g}_sot_chua_nguong'] = o[f'{g}_sot_chua_nguong']
    row.update(nhieu=o['nhieu'], le3=o['le3'], le5=o['le5'], p_hat=o['p_hat'], so_cham=o['so_cham'])
    row['v_top20'] = ('ĐẠT ' if o['top20_nt'] >= 0.99 else 'TRƯỢT ') + fmt(o['top20_nt'])
    row['v_top5'] = ('ĐẠT ' if o['top5_nt'] >= 0.97 else 'TRƯỢT ') + fmt(o['top5_nt'])
    row['v_cuc_tri'] = (('ĐẠT ' if o['cuc_tri_nt'] >= 0.97 else 'TRƯỢT ') + fmt(o['cuc_tri_nt'])) if np.isfinite(o['cuc_tri_nt']) else 'TRƯỢT nan'
    row['v_nhieu'] = ('ĐẠT ' if np.isfinite(o['nhieu']) and o['nhieu'] <= 0.05 else 'TRƯỢT ') + fmt(o['nhieu'])
    row['v_ti_hon'] = ('ĐẠT ' if np.isfinite(o['le3']) and o['le3'] <= 0.02 else 'TRƯỢT ') + fmt(o['le3'])
    if res.kind != 'p':
        for k in ('v_khop_chung', 'v_khop_phien', 'v_khop_gio'): row[k] = 'KHÔNG ÁP DỤNG'
    row['so_truot'] = sum(str(row[k]).startswith('TRƯỢT') for k in CRIT)
    row['truot_gi'] = '; '.join(f'{k[2:]} {str(row[k]).split(" ", 1)[1]}' for k in CRIT if str(row[k]).startswith('TRƯỢT'))
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
    row.update(per_day_stats(ds, res, mask, ndot))
    # ô "5 lớn nhất phiên" bị sót (nhìn thấy) theo giờ UTC — chỉ NQ M15 / M30, nền mới và không lân cận
    if ds.sym == 'NQ' and ds.m in (15, 30) and cfg['name'] in ('nen_moi', 'khong_lan_can'):
        t5 = tops[doan][1]; vis = o['_t5_vis']
        miss = t5[~vis]
        hh = pd.Series(ds.t[ds.sbar[miss]].strftime('%H:%M')).value_counts()
        tot = pd.Series(ds.t[ds.sbar[t5]].strftime('%H:%M')).value_counts()
        for h, n in hh.items():
            T5.append(dict(cau_hinh=cfg['name'], khung=ds.m, doan=doan, gio_utc=h, o_sot=int(n), o_top5_gio_nay=int(tot.get(h, 0)), tong_sot=int(len(miss)), tong_o=int(len(t5))))
        if not len(miss):
            T5.append(dict(cau_hinh=cfg['name'], khung=ds.m, doan=doan, gio_utc='', o_sot=0, o_top5_gio_nay=0, tong_sot=0, tong_o=int(len(t5))))
    return row


def dot_keys(ds, res, keep=None):
    k = res.dot if keep is None else (res.dot & keep[ds.sbar])
    i = np.nonzero(k)[0]
    return set(zip(ds.t.values[ds.sbar[i]].astype('datetime64[m]').astype(np.int64), ds.sside[i], ds.stk[i]))


for sym in ('GC', 'NQ'):
    for m in (1, 5, 15, 30, 60):
        ds = load_dot(sym, m); Rr = rulers(ds)
        tops = {d: L.L2.top_sets_f(ds, ds.doan_mask(d)) for d in ('chon', 'kiem')}
        for cfg in CFGS:
            res = L.eval_dot(ds, cfg)
            for doan in ('chon', 'kiem'):
                SCORE.append(score_one(ds, res, Rr, tops, doan, cfg))
        L.forget(ds)
        # chart nạp ít ngày: cắt còn 3 / 8 / 15 ngày giao dịch cuối (ngày của luật, giờ Chicago); nền mới và tối thiểu 1 ngày (cho luật chọn C)
        if m in (1, 5, 15):
            day, _, _ = L.rule_day_slot(ds.t, m, 'ct'); ud = np.unique(day)
            dmap = dict(zip(ds.t.values.astype('datetime64[m]').astype(np.int64), day))
            for nd in (3, 8, 15):
                keep = day >= ud[-nd]; sub = ds.subset(keep)
                for nm in ('nen_moi', 'toi_thieu_1_ngay', 'sel_lmax'):
                    cfg = [c for c in CFGS if c['name'] == nm][0]
                    A = dot_keys(ds, L.eval_dot(ds, cfg), keep); B = dot_keys(sub, L.eval_dot(sub, cfg))
                    per = {}
                    for x in A | B:
                        c = per.setdefault(dmap[x[0]], [0, 0]); c[1] += 1; c[0] += (x in A and x in B)
                    j = {str(np.datetime64(int(dd), 'D')): c[0] / c[1] for dd, c in sorted(per.items())}
                    SHORT.append(dict(cau_hinh=nm, ma=sym, khung=m, so_ngay_nap=nd, cham_toan_bo=len(A), cham_nap_it=len(B), chung=len(A & B), hop=len(A | B),
                                      trung=len(A & B) / max(len(A | B), 1), theo_ngay=' '.join(f'{k[5:]}:{v:.3f}' for k, v in j.items()),
                                      ngay_thap_nhat=min(j.values()) if j else np.nan))
                L.forget(sub)
        _cache.pop((sym, m), None); L.forget(ds)
        print(f'{sym} M{m} xong ({time.time() - t0:.0f} s)', flush=True)

pd.DataFrame(SCORE).to_csv('out_r3_dot_score.csv', index=False, float_format='%.5g')
pd.DataFrame(T5).to_csv('out_r3_dot_t5gio.csv', index=False)
pd.DataFrame(SHORT).to_csv('out_r3_dot_short.csv', index=False, float_format='%.5g')
print(f'xong ({time.time() - t0:.0f} s)')
