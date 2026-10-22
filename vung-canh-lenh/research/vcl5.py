# -*- coding: utf-8 -*-
"""
VÙNG CANH LỆNH — v5 = engine v4 (vcl4.py) + ĐÚNG MỘT luật mới: độ rộng vùng kẹp theo GIÁ TUYỆT ĐỐI [2, 5] giá
(PLAN-LAN-CHAM.md mục 1). Không sửa vcl.py … vcl4.py: `build_zones` mới viết ở đây và được thay vào engine bằng
monkey-patch CÓ KIỂM SOÁT (context manager `dung_build_zones`, trả lại hàm cũ khi xong — kể cả khi lỗi).

Khác v4 duy nhất ở bước kẹp:
  - rộng < WMIN (2,0 giá)                ⇒ nới đều quanh tâm tới 2,0 giá      (v4: < 1u ⇒ nới tới 1u)
  - rộng (đã đệm 0,5u) > WMAX (5,0 giá)  ⇒ tách tại khe lớn nhất, đệ quy      (v4: > 4u)
  - hai vùng kề chồng nhau               ⇒ cắt ở điểm giữa (như cũ — có thể làm vùng < 2 giá; được đo và báo)
  - MỚI (ca biên plan mục 1.4): mảnh không tách được nữa (1 mức, hoặc mọi mức trùng giá) mà vẫn > 5 giá (chỉ xảy ra khi u > 5)
    ⇒ kẹp đều quanh tâm về 5,0 giá; đếm số lần vào `CANH_BAO['kep_tran']`.
Đệm 0,5u, gộp đơn liên kết ≤ 1,0u, chọn bộ, chống nhấp nháy, điểm, BREAK_U: giữ nguyên v4.

Dữ liệu chính: fp_GCZ26_XCEC_Time_20260723-20261021_90d (UTC). TRAIN = phiên có ngày ≤ 2026-09-15 (kernel.split_train_end).
Chạy: python3 vcl5.py → report/vcl5_records.csv.gz (bộ vùng từng nến, dùng cho lan_cham.py, parity, vẽ).
"""
import os, time, functools, contextlib
import numpy as np
import pandas as pd
import vcl as V
import vcl3 as V3
import vcl4 as V4

K = V.K
REPORT = V.REPORT
DATA = os.path.join(V.ROOT, 'data-export', 'data-footprint')
BASE90 = os.path.join(DATA, 'fp_GCZ26_XCEC_Time_20260723-20261021_90d')
BASE29 = V.BASE                                   # fp_GCZ26_XCEC_Time_20260816-20260915_29d2h (chỉ để đối chiếu)
WMIN_GIA, WMAX_GIA = 2.0, 5.0
CANH_BAO = dict(kep_tran=0, goi=0, ung_vien=0, ngoai_vung=0)   # đếm ca biên (báo trong LAN-CHAM.md)


# ---------------------------------------------------------------------------------------------
# GỘP THÀNH VÙNG — kẹp theo giá
# ---------------------------------------------------------------------------------------------
def _split(ps, a, b, pad, wmax, out):
    """Tách cụm [a,b) tại khe lớn nhất cho tới khi rộng (đã đệm) ≤ wmax giá. Dừng nếu 1 mức hoặc mọi mức trùng giá
    (khe lớn nhất = 0 ⇒ tách vô nghĩa; mảnh đó sẽ bị kẹp trần quanh tâm)."""
    if b - a <= 1 or ps[b - 1] - ps[a] + 2 * pad <= wmax or ps[b - 1] == ps[a]:
        out.append((a, b))
        return
    g = a + 1 + int(np.argmax(np.diff(ps[a:b])))
    _split(ps, a, g, pad, wmax, out)
    _split(ps, g, b, pad, wmax, out)


def build_zones(p, u, link, wmin=WMIN_GIA, wmax=WMAX_GIA, chong='giu2'):
    """Như vcl.build_zones nhưng kẹp độ rộng theo GIÁ [wmin, wmax]. Trả (lab, lo, hi), vùng sắp tăng theo giá.
    Thứ tự bước (C# phải giữ y hệt): gộp ≤ link·u → tách khe lớn nhất nếu rộng+2·đệm > wmax → biên = min/max ± đệm
    → nới đều tới wmin → kẹp trần đều về wmax (chỉ mảnh không tách được) → xử lý chồng lấn.
    Chồng lấn — TỰ QUYẾT (plan mục 1 ghi "cắt giữa như cũ" nhưng cũng ghi "không bao giờ dưới 2 giá"; cắt giữa đo ra 11% vùng
    hiển thị < 2 giá, hẹp nhất 0,15 giá ⇒ hai câu mâu thuẫn; chọn giữ bất biến [2, 5]):
      chong='giu2' (chốt): quét trái→phải; hai vùng chồng nhau mà hợp < 2·wmin ⇒ GỘP thành một; ngược lại cắt ở điểm giữa
                     nhưng kẹp điểm cắt vào [lo_trái + wmin, hi_phải − wmin] ⇒ cả hai ≥ wmin. Không chồng ⇒ giữ nguyên.
      chong='giua': cắt ở giữa y như v4 (chỉ để báo so sánh)."""
    n = len(p)
    if n == 0:
        return np.zeros(0, int), np.zeros(0), np.zeros(0)
    pad = V.P['pad'] * u
    o = np.argsort(p, kind='stable')
    ps = p[o]
    brk = np.flatnonzero(np.diff(ps) > link * u) + 1
    st, en = np.r_[0, brk], np.r_[brk, n]
    big = (ps[en - 1] - ps[st]) + 2 * pad > wmax
    if big.any():
        pieces = []
        for a, b, bg in zip(st, en, big):
            if bg:
                _split(ps, a, b, pad, wmax, pieces)
            else:
                pieces.append((a, b))
        st = np.array([x[0] for x in pieces])
        en = np.array([x[1] for x in pieces])
    lo = ps[st] - pad
    hi = ps[en - 1] + pad
    short = (hi - lo) < wmin
    if short.any():
        c = (lo + hi) / 2
        lo = np.where(short, c - wmin / 2, lo)
        hi = np.where(short, c + wmin / 2, hi)
    wide = (hi - lo) > wmax
    if wide.any():
        CANH_BAO['kep_tran'] += int(wide.sum())
        c = (lo + hi) / 2
        lo = np.where(wide, c - wmax / 2, lo)
        hi = np.where(wide, c + wmax / 2, hi)
    zid = np.arange(len(st))                          # mảnh → chỉ số vùng cuối cùng
    if len(lo) > 1 and chong == 'giua':               # chồng lấn ⇒ cắt ở giữa (y như v4) — chỉ để so sánh
        ov = hi[:-1] > lo[1:]
        if ov.any():
            mid = (hi[:-1] + lo[1:]) / 2
            h2, l2 = hi.copy(), lo.copy()
            h2[:-1][ov] = mid[ov]
            l2[1:][ov] = mid[ov]
            hi, lo = h2, l2
    elif len(lo) > 1:                                 # 'giu2' (CHỐT): quét trái → phải, giữ mọi vùng trong [wmin, wmax]
        zl, zh = [lo[0]], [hi[0]]
        for z in range(1, len(lo)):
            if zh[-1] > lo[z]:
                if max(zh[-1], hi[z]) - zl[-1] < 2 * wmin:   # hợp < 4 giá: không cắt được thành 2 vùng ≥ 2 ⇒ GỘP (rộng < 4 ≤ 5)
                    zh[-1] = max(zh[-1], hi[z])
                    zid[z] = len(zl) - 1
                    continue
                m = (zh[-1] + lo[z]) / 2                     # cắt ở giữa, nhưng dời điểm cắt để cả hai còn ≥ wmin
                m = min(max(m, zl[-1] + wmin), hi[z] - wmin)
                zh[-1] = m
                zl.append(m)
                zh.append(hi[z])
            else:
                zl.append(lo[z])
                zh.append(hi[z])
            zid[z] = len(zl) - 1
        lo, hi = np.array(zl), np.array(zh)
    lab_s = np.repeat(zid, en - st)
    lab = np.empty(n, int)
    lab[o] = lab_s
    CANH_BAO['goi'] += 1
    CANH_BAO['ung_vien'] += n
    CANH_BAO['ngoai_vung'] += int(((p < lo[lab] - 1e-9) | (p > hi[lab] + 1e-9)).sum())
    return lab, lo, hi


@contextlib.contextmanager
def dung_build_zones(wmin=WMIN_GIA, wmax=WMAX_GIA, chong='giu2'):
    """Thay V.build_zones (engine v3/v4 gọi qua thuộc tính module) bằng bản kẹp theo giá, rồi TRẢ LẠI hàm cũ."""
    old = V.build_zones
    V.build_zones = functools.partial(build_zones, wmin=wmin, wmax=wmax, chong=chong)
    try:
        yield
    finally:
        V.build_zones = old


# ---------------------------------------------------------------------------------------------
# DỮ LIỆU
# ---------------------------------------------------------------------------------------------
def load(base=BASE90):
    bars = pd.read_csv(base + '_bars.csv', parse_dates=['datetime'])
    lv = pd.read_csv(base + '.csv', usecols=['bar_idx', 'price', 'volume', 'delta'])
    return bars, lv


def prepare(bars, lv):
    """vcl.prepare (kernel) rồi GHI ĐÈ split theo NGÀY phiên (≤ 2026-09-15 = TRAIN), không theo số phiên như vòng 1–4."""
    ctx = V.prepare(bars, lv)
    df = ctx['df']
    df['split'] = np.where(df['session_id'].str[:10] <= K.CONST['split_train_end'], 'TRAIN', 'TEST')
    st = ctx['st']
    st['split'] = np.where(st['session_id'].str[:10] <= K.CONST['split_train_end'], 'TRAIN', 'TEST')
    # tháng đo: 3 phiên cuối tháng 7 (07-29…07-31) gộp vào nhóm "T8" (plan chỉ nêu tháng 8/9/10)
    m = st['session_id'].str[5:7].astype(int).to_numpy()
    st['thang'] = np.where(m <= 8, 'T8', np.where(m == 9, 'T9', 'T10'))
    ctx['meas'] = do_duoc(st)
    return ctx


def do_duoc(st):
    """Phiên được ĐO: không thin, không splice, không phải phiên 0 (khởi động)."""
    s = np.arange(len(st))
    return (s >= 1) & ~st['thin'].to_numpy() & ~st['splice'].to_numpy()


def run_engine(ctx, cands=None, wmin=WMIN_GIA, wmax=WMAX_GIA, chong='giu2'):
    """Engine v4 với build_zones kẹp theo giá. Trả dict(rec, z10, n_recalc, kep_tran)."""
    cands = V3.gen_candidates(ctx) if cands is None else cands
    for k in CANH_BAO:
        CANH_BAO[k] = 0
    with dung_build_zones(wmin, wmax, chong):
        r = V4.run_engine(ctx, cands)
    r['kep_tran'] = CANH_BAO['kep_tran']
    r['canh_bao'] = dict(CANH_BAO)
    return r


# ---------------------------------------------------------------------------------------------
# VỆ SINH (theo split NGÀY, chỉ phiên đo được)
# ---------------------------------------------------------------------------------------------
def hygiene(ctx, rec):
    df, st = ctx['df'], ctx['st']
    C = df['close'].to_numpy(float)
    u = K.median_range(df).to_numpy()
    sno = df['session_no'].to_numpy()
    meas = ctx['meas']
    n = len(df)
    rr = rec.sort_values(['eid', 'bar'])
    g = rr.groupby('eid')['bar']
    firsts, lens = g.min().to_numpy(), g.size().to_numpy()
    rb = rec['bar'].to_numpy()
    lo, hi = rec['lo'].to_numpy(), rec['hi'].to_numpy()
    nxt = np.minimum(rb + 1, n - 1)
    ins = np.zeros(n, bool)
    np.logical_or.at(ins, nxt, (rb + 1 < n) & (C[nxt] >= lo) & (C[nxt] <= hi) & (sno[nxt] == sno[rb]))
    out = {}
    split = df['split'].to_numpy()
    for sp in ('TRAIN', 'TEST', 'GỘP'):
        bm = meas[sno] & ~np.isnan(u) & ((split == sp) if sp != 'GỘP' else True)
        bars = np.flatnonzero(bm)
        okset = np.zeros(n, bool)
        okset[bars] = True
        sel = okset[rb]
        w = (hi - lo)[sel]
        out[sp] = dict(cnt=np.bincount(rb, minlength=n)[bars].mean(), w_med=np.median(w), w_p90=np.quantile(w, .9),
                       w_gt4=(w > 4 + 1e-9).mean(), w_gt5=(w > 5 + 1e-9).mean(), w_eq2=(np.abs(w - 2) < 1e-6).mean(),
                       w_lt2=(w < 2 - 1e-6).mean(), inside=ins[bars[bars >= 1]].mean(),
                       chg=okset[firsts].sum() / (len(bars) / 60.0), life=np.median(lens[okset[firsts]]))
    return out


def main():
    t0 = time.time()
    bars, lv = load(BASE90)
    ctx = prepare(bars, lv)
    r = run_engine(ctx)
    os.makedirs(REPORT, exist_ok=True)
    r['rec'].to_csv(os.path.join(REPORT, 'vcl5_records.csv.gz'), index=False)
    h = hygiene(ctx, r['rec'])
    for sp, x in h.items():
        print(sp, {k: round(float(v), 3) for k, v in x.items()})
    print(f"kẹp trần (mảnh không tách được > 5 giá): {r['kep_tran']} lần · tính lại bộ {r['n_recalc']} · {time.time() - t0:.0f}s")


if __name__ == '__main__':
    main()
