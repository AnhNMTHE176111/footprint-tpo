"""Vòng 1 — chạy lưới ứng viên A, B, C (+ biến thể cố ý sai), D, E, F, G và 2 mốc (luật hiện tại 1%/240', BigTradeAdaptive mặc định).
python bw1_rules.py  ->  out_bw1_grid.csv (trong thư mục này) + SCRATCH/bw1_runs.pkl (ngưỡng + vòng mọi cấu hình) + SCRATCH/marks_<nhật ký>.csv.gz

Chế độ khởi động (mọi ứng viên có cửa sổ):
  du    = đủ cửa sổ đầy (D ngày nến; với F/G là T phút; với B là khung chính đủ D ngày) mới có ngưỡng;
  W240 / W690 / W1380 = cửa sổ lớn dần: có ngưỡng khi phút nến tham chiếu >= min(W_min, phút của cửa sổ đầy); K co theo phút đã có.
  E và hai mốc: tu_nhien (không có khởi động riêng; mốc giữ đúng khởi động của C#).
Ngày đánh giá của một đoạn = ngày đủ (>= 1170 phút nến) trong đoạn mà MỌI nến của ngày đều có ngưỡng.
_GCZ26 M1 không có ngày đủ nào -> đoạn 'ngoai' dùng ngày phần có >= 400 phút nến (ghi rõ trong R1-KET-QUA.md).
F: f hiệu chỉnh trên đoạn chọn của nhật ký M1 từng mã (chế độ du) để TRUNG BÌNH vòng/ngày = 6 / 10 / 15, rồi giữ nguyên cho khung khác và đoạn kiểm.
"""
import os, sys, time, pickle, math
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bw1_common as C

RUN_LOGS = ['GCX_M1', 'GCX_M5', 'NQ_M1', 'NQ_M15', 'GCZ_M1']
WARMS = ['du', 'W240', 'W690', 'W1380']
A_D = [3, 5, 10]; A_R = [3, 4, 6, 8, 10, 15, 20]
B_D = [5, 10]; B_R = [4, 6, 10, 15]
C_QK = [(q, k) for q in (5, 15, 30) for k in (2, 3, 4, 5)]
CX_K = [3, 5, 8]
D_K0R = [(k0, R) for k0 in (100, 200) for R in (6, 10)]
E_FL = [20, 25, 30, 40, 50, 75, 100, 150]
F_T = [120, 240]; F_TARGET = [6, 10, 15]
G_T = [240, 480, 1380]; G_K = [1, 2, 3]
GCZ_PART_MIN = 400


def families(log):
    """Trả list (tên cấu hình, mã, tham số, thr, refmin, full, src, phút cửa sổ đầy)."""
    out = []
    for Dd in A_D:
        c = C.CandA(log, Dd, A_R); th, mn, fu, src = C.run_multi(c, log)
        for j, R in enumerate(A_R): out.append((f'A_D{Dd}_R{R}', 'A', f'D={Dd} R={R}', th[j], mn, fu, src, c.full_minutes))
    for Dd in B_D:
        c = C.CandB(log, Dd, B_R); th, mn, fu, src = C.run_multi(c, log)
        for j, R in enumerate(B_R): out.append((f'B_D{Dd}_R{R}', 'B', f'D={Dd} R={R}', th[j], mn, fu, src, c.full_minutes))
    c = C.CandC(log, C_QK); th, mn, fu, src = C.run_multi(c, log)
    for j, (q, k) in enumerate(C_QK): out.append((f'C_q{q}_k{k}', 'C', f'q={q} k={k} D=5', th[j], mn, fu, src, c.full_minutes))
    c = C.CandCwrong(log, CX_K); th, mn, fu, src = C.run_multi(c, log)
    for j, k in enumerate(CX_K): out.append((f'Cx_k{k}', 'Cx', f'k={k} x muc1%/240p', th[j], mn, fu, src, c.full_minutes))
    c = C.CandHill(log, D_K0R); th, mn, fu, src = C.run_multi(c, log)
    for j, (k0, R) in enumerate(D_K0R): out.append((f'D_k{k0}_R{R}', 'D', f'k0={k0} R={R} D=5', th[j], mn, fu, src, c.full_minutes))
    for fl in E_FL:
        out.append((f'E_{fl}', 'E', f'san={fl}', np.full(log.nb, float(fl)), np.zeros(log.nb), np.ones(log.nb, bool), None, 0))
    for T in F_T:
        c = C.CandF(log, T); th, mn, fu, src = C.run_multi(c, log)
        out.append((f'F_T{T}_V', 'FV', f'T={T}', th[0], mn, fu, src, c.full_minutes))   # V (chưa nhân f)
    for T in G_T:
        c = C.CandG(log, T, G_K); th, mn, fu, src = C.run_multi(c, log)
        for j, K in enumerate(G_K): out.append((f'G_T{T}_K{K}', 'G', f'T={T} K={K}', th[j], mn, fu, src, c.full_minutes))
    return out


def avail_mask(warm, code, refmin, full, src, fullmin):
    if code == 'E': return np.ones(len(refmin), bool)
    if warm == 'du': return full.astype(bool)
    W = int(warm[1:])
    a = refmin >= min(W, fullmin)
    if code == 'B': a = a | (src == 'B')
    return a & (refmin > 0)


def seg_days(log, seg):
    sym = log.sym
    if log.key.startswith('GCZ'):
        return [d for d, v in sorted(log.daymin.items()) if v >= GCZ_PART_MIN] if seg == 'ngoai' else []
    S = C.SEGMENTS[sym]
    if seg == 'chon':
        a, b = S['chon']; return [d for d in log.full_days if a <= d <= b]
    if seg == 'kiem':
        if 'kiem_list' in S: return [d for d in log.full_days if d in S['kiem_list']]
        a, b = S['kiem']; return [d for d in log.full_days if a <= d <= b]
    return []


def segs_of(log):
    return ['ngoai'] if log.key.startswith('GCZ') else ['chon', 'kiem']


def eval_days(log, days, thr):
    """Ngày trong days mà mọi nến có ngưỡng."""
    ok = []
    for d in days:
        b = log.day == d
        if b.any() and not np.isnan(thr[b]).any(): ok.append(d)
    return ok


def summarize(log, cfg, code, params, warm, seg, days, thr, rounds, full):
    r = rounds
    rday = log.day[r.bar.values] if len(r) else np.array([])
    rses = log.ses[r.bar.values] if len(r) else np.array([])
    per = np.array([int(np.sum(rday == d)) for d in days]) if days else np.array([])
    ses_med = {}
    for s in ('A', 'Au', 'My'):
        ses_med[s] = float(np.median([np.sum((rday == d) & (rses == s)) for d in days])) if days else np.nan
    bm = np.isin(log.day, days)
    tv = thr[bm]
    dmed = [np.nanmedian(thr[log.day == d]) for d in days]
    cv = float(np.std(dmed) / np.mean(dmed)) if len(dmed) >= 2 and np.mean(dmed) > 0 else np.nan
    rin = r[np.isin(rday, days)] if len(r) else r
    notfull = [d for d in days if not full[log.day == d].all()]
    per_nf = [int(np.sum(rday == d)) for d in notfull]
    return dict(nhat_ky=log.key, khung=f'M{log.m}', ung_vien=code, cau_hinh=cfg, tham_so=params, khoi_dong=warm, doan=seg,
                so_ngay=len(days), vong_ngay_min=per.min() if len(per) else np.nan, vong_ngay_tv=float(np.median(per)) if len(per) else np.nan,
                vong_ngay_max=per.max() if len(per) else np.nan, vong_tb=float(per.mean()) if len(per) else np.nan,
                tv_A=ses_med['A'], tv_Au=ses_med['Au'], tv_My=ses_med['My'],
                ngay_khong_vong=int(np.sum(per == 0)) if len(per) else np.nan,
                nguong_p10=float(np.nanpercentile(tv, 10)) if len(tv) else np.nan, nguong_p50=float(np.nanpercentile(tv, 50)) if len(tv) else np.nan,
                nguong_p90=float(np.nanpercentile(tv, 90)) if len(tv) else np.nan, nguong_cv=cv,
                co_vong_min=int(rin.mot.min()) if len(rin) else np.nan, co_vong_tv=float(rin.mot.median()) if len(rin) else np.nan,
                ngay_chua_du_D=len(notfull), vong_tv_ngay_chua_du=float(np.median(per_nf)) if per_nf else np.nan)


def calibrate_f(log, V, days, target):
    """f sao cho trung bình vòng/ngày trên days (chế độ du) = target. Tìm nhị phân trên log f."""
    lo, hi = 0.01, 200.0
    def rate(f):
        thr = np.where(np.isnan(V), np.nan, np.floor(f * V + 0.5))
        r = C.select_rounds(log, thr)
        rd = log.day[r.bar.values] if len(r) else np.array([])
        return np.mean([np.sum(rd == d) for d in days])
    for _ in range(40):
        mid = math.sqrt(lo * hi)
        if rate(mid) > target: lo = mid
        else: hi = mid
    return round(hi, 4), rate(hi)


def main():
    t0 = time.time()
    logs = {k: C.load(k) for k in RUN_LOGS}
    fam = {}
    for k, log in logs.items():
        t = time.time(); fam[k] = families(log); print(k, 'ngưỡng xong', round(time.time() - t, 1), 's', flush=True)
    # hiệu chỉnh f trên M1 từng mã, đoạn chọn, chế độ du
    fcal = {}
    calib_txt = []
    for sym, k in (('GC', 'GCX_M1'), ('NQ', 'NQ_M1')):
        log = logs[k]
        for (name, code, params, th, mn, fu, src, fm) in fam[k]:
            if code != 'FV': continue
            T = int(name.split('_')[1][1:])
            V = np.where(fu, th, np.nan)
            days = eval_days(log, seg_days(log, 'chon'), V)
            for tg in F_TARGET:
                f, rt = calibrate_f(log, V, days, tg)
                fcal[(sym, T, tg)] = f
                calib_txt.append(f'{sym} T={T} muc tieu {tg}/ngay: f = {f} (trung binh dat {rt:.2f} vong/ngay tren {len(days)} ngay chon)')
                print(calib_txt[-1], flush=True)
    rows = []; store = {}
    for k, log in logs.items():
        allc = []
        for (name, code, params, th, mn, fu, src, fm) in fam[k]:
            if code == 'FV':
                T = int(name.split('_')[1][1:])
                for tg in F_TARGET:
                    f = fcal[(log.sym, T, tg)]
                    allc.append((f'F_T{T}_n{tg}', 'F', f'T={T} f={f} (muc tieu {tg}/ngay)', np.where(np.isnan(th), np.nan, np.floor(f * th + 0.5)), mn, fu, src, fm))
            else:
                allc.append((name, code, params, th, mn, fu, src, fm))
        # mốc
        thc = C.thr_current(log)
        allc.append(('CUR', 'CUR', '1% cua 240 phut (luat hien tai, thong ke)', thc, None, None, None, None))
        tha = C.thr_adaptive(log)
        allc.append(('ADAPT', 'ADAPT', 'BigTradeAdaptive mac dinh (Theo CORVEN): N=BarsFor, K=N, san 5, >=, toi da 3', tha, None, None, None, None))
        marks = []
        for (name, code, params, th, mn, fu, src, fm) in allc:
            warms = ['tu_nhien'] if code in ('E', 'CUR', 'ADAPT') else WARMS
            for w in warms:
                if code in ('CUR', 'ADAPT', 'E'):
                    thr = th.copy(); full = np.ones(log.nb, bool)
                else:
                    a = avail_mask(w, code, mn, fu, src, fm)
                    thr = np.where(a, th, np.nan); full = fu.astype(bool)
                if code == 'ADAPT':
                    rr = C.select_rounds(log, thr, strict=False, cap=3)
                else:
                    rr = C.select_rounds(log, thr)
                store[(k, name, w)] = dict(code=code, params=params, thr=thr.astype(np.float32), full=full, rounds=rr)
                for seg in segs_of(log):
                    days = eval_days(log, seg_days(log, seg), thr)
                    rows.append(summarize(log, name, code, params, w, seg, days, thr, rr, full))
                if len(rr):
                    mk = rr.copy(); mk['t'] = pd.to_datetime(log.t[rr.bar.values]).strftime('%Y-%m-%d %H:%M')
                    mk['price'] = (mk.tick * log.tick).round(2); mk['cfg'] = name; mk['warm'] = w
                    marks.append(mk[['cfg', 'warm', 't', 'price', 'mot', 'thr']])
        if marks:
            pd.concat(marks).to_csv(os.path.join(C.SCRATCH, f'marks_{k}.csv.gz'), index=False)
        print(k, 'xong', round(time.time() - t0, 1), 's', flush=True)
    grid = pd.DataFrame(rows)
    grid.to_csv(os.path.join(C.HERE, 'out_bw1_grid.csv'), index=False, float_format='%.4g')
    with open(os.path.join(C.SCRATCH, 'bw1_runs.pkl'), 'wb') as f:
        pickle.dump({'store': store, 'fcal': fcal, 'logs': logs}, f)
    with open(os.path.join(C.HERE, 'out_bw1_fcal.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(calib_txt) + '\n')
    print('tong', round(time.time() - t0, 1), 's; dong luoi', len(grid))


if __name__ == '__main__':
    main()
