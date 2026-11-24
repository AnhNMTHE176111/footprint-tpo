"""Thước đo dùng chung cho chấm và Big Trade (PLAN mục 4.1, 4.2): độ khớp mức danh nghĩa và độ đều sau gộp.
Đầu vào: một bộ dữ liệu ds (nb, sbar, npos, ses, hour, dayi, days, mod, m, tot, doan_mask) và một Res (has, nom, exc, dot, thr, kind, nom_decl).
Tỉ lệ nổ thực (PLAN 4.1):
  kiểu p   = số vượt / số giá trị > 0 của các nến có ngưỡng;  so với mức danh nghĩa đạt được = TB theo nến của (mẫu tham chiếu > ngưỡng) / số mẫu
  kiểu λ   = số vượt / số nến có ngưỡng;                        so với TB theo nến của (mẫu tham chiếu > ngưỡng) / số nến tham chiếu
  kỷ lục   = số nến có ít nhất một ô vượt / số nến có ngưỡng;  so với TB theo nến của (số nến tham chiếu có max > ngưỡng + 1) / (n + 1)
             (không có giá trị bằng nhau thì đúng bằng r / (n + 1); cột muc_danh_nghia ghi TB của r / (n + 1))
  z_log    = số vượt / số giá trị > 0;  so với mức của phân phối chuẩn 0,62% / 0,135% / 0,023% (cột muc_dat_duoc vẫn ghi phần tham chiếu có z >= z0)
  đối chứng: chỉ báo tỉ lệ theo ô, không có tỉ số khớp."""
import numpy as np, pandas as pd

SES_LBL = ('A', 'Au', 'My')
OPEN_BARS = {'22:00': (1320, 0), '07:00': (420, 1), '13:30': (810, 2), '14:30': (870, 2)}


def per_bar(ds, res):
    nexc = np.bincount(ds.sbar[res.exc], minlength=ds.nb)
    ndot = np.bincount(ds.sbar[res.dot], minlength=ds.nb)
    if hasattr(ds, 'sside'):
        nred = np.bincount(ds.sbar[res.dot & (ds.sside == 0)], minlength=ds.nb)
    else:
        nred = np.zeros(ds.nb, np.int64)
    return nexc, ndot, nred


def grouped(ds, res, nexc, mask, gid, ng):
    """Theo nhóm (gid 0..ng-1) trên các nến mask & has: trả dict mảng (so_nen, chua_co_nguong, so_gia_tri, so_vuot, act, ach, decl, khop, thr_med)."""
    has = res.has & mask
    nb = np.bincount(gid[mask], minlength=ng)
    nh = np.bincount(gid[has], minlength=ng)
    npos = np.bincount(gid[has], weights=ds.npos[has], minlength=ng)
    nx = np.bincount(gid[has], weights=nexc[has], minlength=ng)
    nbx = np.bincount(gid[has], weights=(nexc[has] > 0), minlength=ng)
    nomv = np.where(np.isfinite(res.nom), res.nom, 0)
    nom_s = np.bincount(gid[has], weights=nomv[has], minlength=ng)
    with np.errstate(invalid='ignore', divide='ignore'):
        ach = nom_s / nh
        k = res.kind
        if k == 'p' or k == 'z' or k == 'base':
            act = nx / npos
        elif k == 'lam':
            act = nx / nh
        else:
            act = nbx / nh
        if k == 'rec':
            dv = np.where(np.isfinite(res.nom_decl_bar), res.nom_decl_bar, 0)
            decl = np.bincount(gid[has], weights=dv[has], minlength=ng) / nh
        else:
            decl = np.full(ng, res.nom_decl)
        if k in ('p', 'lam', 'rec'):
            khop = act / ach
        elif k == 'z':
            khop = act / res.nom_decl
        else:
            khop = np.full(ng, np.nan)
    return dict(so_nen=nb, chua_co_nguong=nb - nh, so_gia_tri=npos, so_vuot=nx, so_nen_co_vuot=nbx, muc_danh_nghia=decl, muc_dat_duoc=ach, ti_le_no=act, ti_so_khop=khop, nh=nh)


def thr_median(res, mask, gid, ng):
    out = np.full(ng, np.nan)
    has = res.has & mask & np.isfinite(res.thr)
    if not has.any(): return out
    s = pd.Series(res.thr[has]).groupby(gid[has]).median()
    out[s.index.values] = s.values
    return out


def calib_and_density(ds, res, name, doan, extra=None):
    """Trả (các dòng calib, các dòng density, dict tóm tắt) cho một cấu hình trên một đoạn."""
    mask = ds.doan_mask(doan)
    nexc, ndot, nred = per_bar(ds, res)
    base = dict(cau_hinh=name, phuong_an=res.cfg['pa'], kieu=res.kind, ma=ds.sym if getattr(ds, 'tag', ds.sym) in ('GC', 'NQ') else ds.tag, khung=ds.m, doan=doan)
    if extra: base.update(extra)
    scopes = [('tat_ca', np.zeros(ds.nb, np.int64), 1, ['tat_ca']),
              ('phien', ds.ses.astype(np.int64), 3, ['phien_' + s for s in SES_LBL]),
              ('gio', ds.hour.astype(np.int64), 24, [f'gio_{h:02d}' for h in range(24)])]
    crow, drow = [], []
    has = res.has & mask
    summ = {}
    for _, gid, ng, labels in scopes:
        G = grouped(ds, res, nexc, mask, gid, ng)
        tm = thr_median(res, mask, gid, ng)
        nh = G['nh']
        dsum = np.bincount(gid[has], weights=ndot[has], minlength=ng)
        rsum = np.bincount(gid[has], weights=nred[has], minlength=ng)
        for j, lb in enumerate(labels):
            if G['so_nen'][j] == 0: continue
            crow.append(dict(base, pham_vi=lb, so_nen=int(G['so_nen'][j]), chua_co_nguong=int(G['chua_co_nguong'][j]), so_gia_tri=int(G['so_gia_tri'][j]),
                             so_vuot=int(G['so_vuot'][j]), muc_danh_nghia=G['muc_danh_nghia'][j], muc_dat_duoc=G['muc_dat_duoc'][j], ti_le_no=G['ti_le_no'][j],
                             ti_so_khop=G['ti_so_khop'][j], nguong_trung_vi=tm[j]))
            cpb = dsum[j] / nh[j] if nh[j] else np.nan
            drow.append(dict(base, pham_vi=lb, so_nen_co_nguong=int(nh[j]), cham=int(dsum[j]), cham_nen=cpb, cham_gio=cpb * 60.0 / ds.m if nh[j] else np.nan,
                             ti_le_do=(rsum[j] / dsum[j]) if (dsum[j] and hasattr(ds, 'sside')) else np.nan))
        if labels[0] == 'tat_ca':
            summ['khop_chung'] = G['ti_so_khop'][0]; summ['ti_le_no_o'] = (G['so_vuot'][0] / G['so_gia_tri'][0]) if G['so_gia_tri'][0] else np.nan
            summ['nen_chua_co_nguong'] = G['chua_co_nguong'][0] / max(G['so_nen'][0], 1)
            summ['cham_nen'] = dsum[0] / nh[0] if nh[0] else np.nan
        elif labels[0].startswith('phien'):
            summ['khop_phien'] = G['ti_so_khop'].copy(); summ['cham_nen_phien'] = dsum / np.maximum(nh, 1)
            summ['cham_nen_phien'][nh == 0] = np.nan
        else:
            summ['khop_gio'] = np.where(G['so_nen'] > 0, G['ti_so_khop'], np.nan); summ['gio_co_nen'] = G['nh'] > 0
    # theo ngày
    nd = len(ds.days)
    G = grouped(ds, res, nexc, mask, ds.dayi.astype(np.int64), nd)
    kd = G['ti_so_khop'][(G['nh'] > 0)]
    days_ok = np.nonzero(G['nh'] > 0)[0]
    if len(kd) and np.isfinite(kd).any():
        q = np.nanquantile(kd, [.1, .5, .9])
        lg = np.abs(np.log(np.where(kd > 0, kd, 1e-6)))
        lg[~np.isfinite(lg)] = -1
        w = int(np.argmax(lg)); worst = (str(ds.days[days_ok[w]].date()), kd[w])
    else:
        q = [np.nan] * 3; worst = ('', np.nan)
    crow[0].update(khop_ngay_p10=q[0], khop_ngay_p50=q[1], khop_ngay_p90=q[2], ngay_te_nhat=worst[0], khop_ngay_te_nhat=worst[1])
    summ['khop_ngay'] = (q[0], q[2], worst)
    # mật độ: số liệu phụ ở dòng tat_ca
    d = ndot[has]
    dens0 = drow[0]
    if len(d):
        dens0.update(ti_le_nen_khong_cham=float((d == 0).mean()), cham_1nen_p50=float(np.quantile(d, .5)), cham_1nen_p95=float(np.quantile(d, .95)),
                     cham_1nen_max=int(d.max()), ti_le_nen_tren5=float((d > 5).mean()))
        summ['p95'] = float(np.quantile(d, .95)); summ['max'] = int(d.max()); summ['tren5'] = float((d > 5).mean())
    sesmean = summ['cham_nen_phien']
    worst_open = 0.0; opens = {}
    for lb, (mod, s) in OPEN_BARS.items():
        k = has & (ds.mod == mod)
        if k.any() and np.isfinite(sesmean[s]) and sesmean[s] > 0:
            r = ndot[k].mean() / sesmean[s]; opens[lb] = r; dens0[f'nen_{lb.replace(":", "")}_so_TB_phien'] = r
            worst_open = max(worst_open, r)
        else:
            dens0[f'nen_{lb.replace(":", "")}_so_TB_phien'] = np.nan
    summ['dau_phien'] = worst_open if opens else np.nan
    # tương quan (số chấm ngày) với (volume ngày / TB 10 ngày trước)
    dv = np.bincount(ds.dayi, weights=ds.tot, minlength=nd)
    prev = pd.Series(dv).shift(1).rolling(10, min_periods=5).mean().values
    rel = dv / prev
    dd = np.bincount(ds.dayi[has], weights=ndot[has], minlength=nd)
    dm = np.bincount(ds.dayi[mask], minlength=nd) > 0
    ok = dm & np.isfinite(rel)
    dens0['tuong_quan_cham_vol_ngay'] = float(np.corrcoef(dd[ok], rel[ok])[0, 1]) if ok.sum() > 3 and dd[ok].std() > 0 else np.nan
    summ['tuong_quan'] = dens0['tuong_quan_cham_vol_ngay']
    summ['ti_le_do'] = dens0.get('ti_le_do', np.nan)
    return crow, drow, summ


def verdicts(summ, kind):
    """Các tiêu chí có ngưỡng của PLAN 4.1, 4.2 (trên đoạn kiểm). Trả dict cột -> 'ĐẠT x' / 'TRƯỢT x' / 'BÁO x'."""
    out = {}

    def f(x): return 'nan' if x is None or not np.isfinite(x) else f'{x:.3g}'
    calib = kind in ('p', 'lam', 'rec', 'z')
    if calib:
        k = summ['khop_chung']
        out['khop_chung'] = ('ĐẠT ' if 0.8 <= k <= 1.25 else 'TRƯỢT ') + f(k)
        kp = summ['khop_phien']; kpv = kp[np.isfinite(kp)]
        ok = len(kpv) == 3 and np.all((kpv >= 0.67) & (kpv <= 1.5)) and kpv.max() / max(kpv.min(), 1e-12) <= 1.8
        out['khop_phien'] = ('ĐẠT ' if ok else 'TRƯỢT ') + '/'.join(f(x) for x in kp)
        kg = summ['khop_gio']; present = summ['gio_co_nen']
        good = int(np.sum(present & (kg >= 0.5) & (kg <= 2)))
        if present.any():
            lg = np.where(present & np.isfinite(kg) & (kg > 0), np.abs(np.log(np.where(kg > 0, kg, 1))), np.where(present, 99, -1))
            wh = int(np.argmax(lg)); wtxt = f' (giờ tệ nhất {wh:02d}: {f(kg[wh])})'
        else:
            wtxt = ''
        out['khop_gio'] = ('ĐẠT ' if good >= 20 else 'TRƯỢT ') + f'{good}/{int(present.sum())}' + wtxt
        p10, p90, worst = summ['khop_ngay']
        ok = np.isfinite(p10) and 0.5 <= p10 <= 2 and 0.5 <= p90 <= 2
        out['khop_ngay'] = ('ĐẠT ' if ok else 'TRƯỢT ') + f'p10 {f(p10)} p90 {f(p90)} (tệ nhất {worst[0]} {f(worst[1])})'
    else:
        for c in ('khop_chung', 'khop_phien', 'khop_gio', 'khop_ngay'): out[c] = 'KHÔNG ÁP DỤNG'
    cp = summ['cham_nen_phien']; cpv = cp[np.isfinite(cp)]
    ratio = cpv.max() / cpv.min() if len(cpv) and cpv.min() > 0 else np.inf
    txt = f'{f(ratio)} ({"/".join(f(x) for x in cp)})'
    if kind in ('lam', 'rec'):
        out['deu_phien'] = ('ĐẠT ' if ratio <= 2.0 else 'TRƯỢT ') + txt
    else:
        out['deu_phien'] = 'BÁO ' + txt
    dp = summ['dau_phien']
    out['dau_phien'] = ('ĐẠT ' if (np.isfinite(dp) and dp <= 3) else 'TRƯỢT ') + f(dp)
    rd = summ.get('ti_le_do', np.nan)
    out['do_xanh'] = ('BÁO lệch ' if (np.isfinite(rd) and (rd > 0.6 or rd < 0.4)) else 'BÁO ') + f(rd)
    out['tuong_quan_vol_ngay'] = 'BÁO ' + f(summ.get('tuong_quan', np.nan))
    return out
