# -*- coding: utf-8 -*-
"""
BENZO × VÙNG CANH LỆNH (người học hỏi 2026-10-22): các setup và bias của Benzo Trader, nếu đặt vào vùng hỗ trợ/kháng cự
của Vùng Canh Lệnh (VCL v5, rộng 2–5 giá) thì có cải thiện không, cải thiện bao nhiêu, và số lệnh có tăng không?

KHÔNG sửa code Benzo (setup_*.py, kernel.py, C#) và KHÔNG sửa code VCL: chỉ import.
  - Tín hiệu gốc 4 setup = ô chính đã báo trong RESULTS-*.md / TONG-KET-VONG-1-2.md (A V3, B ô chính, C ô khởi điểm TP 2R,
    D V3). Điều kiện tiên quyết: khớp n / WR / R TB với báo cáo cũ (hàm `check_repro`).
  - Bộ vùng VCL = bộ vùng ĐANG HIỂN THỊ của engine v5 (vcl5.py; cache report/cache_lc/v5.pkl của lan_cham.py, thiếu thì
    tự chạy lại engine). Vùng tại nến i chỉ dùng nến <= i (đã chứng minh bằng test cắt dữ liệu trong test_vcl.py).
Mọi hằng số dưới đây ĐĂNG KÝ TRƯỚC khi nhìn kết quả (ghi lại ở mục 0 của report).

Chạy: python3 benzo_vcl.py  → report/BENZO-VCL.md + report/img/benzo_vcl_<split>_<phiên>.png
"""
from __future__ import annotations

import os
import sys
import math
import time
import pickle

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
VCLR = os.path.join(ROOT, 'vung-canh-lenh', 'research')
sys.path.insert(0, HERE)
sys.path.insert(1, VCLR)
import kernel as K  # noqa: E402
import setup_a_pha_hoi as SA  # noqa: E402
import setup_b_hap_thu as SB  # noqa: E402
import setup_c_fade_canh as SC  # noqa: E402
import setup_d_trap as SD  # noqa: E402

REPORT = os.path.join(HERE, 'report')
IMG = os.path.join(REPORT, 'img')
D90 = SA.D90

# ------------------------------------ HẰNG SỐ ĐĂNG KÝ TRƯỚC ------------------------------------
TOL = 1.0                       # "giá vào lệnh nằm trong vùng ±1 giá"
SHIFT_LO, SHIFT_HI = 3.0, 15.0  # đối chứng dời: |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, cố định trong (phiên, bản)
REPS, SEED = 100, 20261024      # 100 bản dời, CÙNG một ma trận δ cho mọi setup và mọi phép đo
CTRL_SEEDS = 200                # đối chứng "vào ngẫu nhiên tại vùng" (kernel.control_sample): 200 lần, 1 nến / lệnh thật
BOOT, BOOT_SEED = 10000, 0      # khoảng tin cậy 95% lấy mẫu lại (bootstrap) theo lệnh
ANCHOR_PAD, SL_MAX = 0.5, 4.0   # phép đo C: SL = biên xa vùng ± 0,5 giá; SL > 4 giá ⇒ bỏ lệnh
ANCHOR_RR = (1.5, 2.0)          # phép đo C: hai biến thể TP, báo cả hai
MIN_N = 10                      # phán quyết chỉ áp dụng khi MỖI nhóm so sánh có >= 10 lệnh ở CẢ TRAIN và TEST
SETUPS = ('A', 'B', 'C', 'D')
TEN = {'A': 'A Phá hồi', 'B': 'B Hấp thụ', 'C': 'C Fade cạnh', 'D': 'D Trap', 'ALL': 'GỘP 4 setup'}
# ô chính (đúng các báo cáo cũ) và bản NỚI = ô LỎNG NHẤT của lưới 3×3 đã đăng ký trong chính RESULTS-* của setup đó
MAIN = {'A': dict(n_min=3, body=0.5, expire=30, rr=3.0),
        'B': dict(theta=0.5, N=3),
        'C': dict(pen_ticks=2, min_width=6.0, tp_mode='fixed2'),
        'D': dict(min_move=5.0, max_retr=0.7, method='delta', use_zone=False, sideway=True)}
LOOSE = {'A': dict(n_min=2, body=0.4, expire=30, rr=3.0),
         'B': dict(theta=0.3, N=2),
         'C': dict(pen_ticks=1, min_width=4.0, tp_mode='fixed2'),
         'D': dict(min_move=4.0, max_retr=0.9, method='delta', use_zone=False, sideway=True)}
LOOSE_TXT = {'A': 'số nến hồi tối thiểu 3 → 2, thân nến xác nhận 0,5 → 0,4',
             'B': 'ngưỡng |delta| nến xác nhận 0,5 → 0,3 × max, cụm 3 → 2 nến',
             'C': 'độ xuyên cạnh 2 → 1 tick (độ rộng range không chặn lệnh nào ở 90d)',
             'D': 'move tối thiểu 5 → 4 giá, độ hồi tối đa 70% → 90%'}
EXPECT = {'A': (20, 0.100, -0.68), 'B': (11, 0.273, 0.00), 'C': (121, 0.273, -0.26), 'D': (31, 0.387, 0.08)}
CLOSED = ('TP', 'SL', 'TIME')
GROUPS = (('TRAIN', 'split', 'TRAIN'), ('TEST', 'split', 'TEST'), ('GỘP', None, None),
          ('T8', 'thang', 'T8'), ('T9', 'thang', 'T9'), ('T10', 'thang', 'T10'))


# =============================================================================================
# 1. DỮ LIỆU
# =============================================================================================
def thang_of(session_id):
    m = int(str(session_id)[5:7])
    return 'T8' if m <= 8 else ('T9' if m == 9 else 'T10')


def load_rec(df):
    """Bộ vùng hiển thị VCL v5 (cache lan_cham). Thiếu cache ⇒ chạy lại engine vcl5 (vài phút) và lưu cache."""
    import vcl5 as V5
    import lan_cham as LC
    p = os.path.join(LC.CACHE, 'v5.pkl')
    if os.path.exists(p):
        with open(p, 'rb') as f:
            rec = pickle.load(f)['rec']
    else:
        bars, lv = V5.load(V5.BASE90)
        ctx = V5.prepare(bars, lv)
        r = V5.run_engine(ctx)
        os.makedirs(LC.CACHE, exist_ok=True)
        with open(p, 'wb') as f:
            pickle.dump(dict(rec=r['rec'], n_recalc=r['n_recalc'], kep_tran=r['kep_tran'], canh_bao=r.get('canh_bao'), sec=0), f)
        rec = r['rec']
    rec = rec.reset_index(drop=True)
    if int(rec['bar'].max()) >= len(df):
        raise ValueError('bộ vùng VCL không khớp file nến')
    return rec


class Data:
    """Nạp 1 lần: dữ liệu riêng của từng setup (đúng hàm chuẩn bị của chính setup đó) + bộ vùng VCL + bảng phiên."""

    def __init__(self):
        t0 = time.time()
        self.DA = SA.Data(D90)
        self.df = self.DA.df
        self.PB = SB.prepare(self.df, self.DA.prof)
        self.PC = SC.prepare(D90)
        self.PD = SD.Prep(D90 + '_bars.csv', D90 + '.csv')
        for d in (self.PC['df'], self.PD.df):            # 4 setup phải nhìn CÙNG một chuỗi nến (vị trí idx dùng chung)
            if len(d) != len(self.df) or not (d['datetime'].to_numpy() == self.df['datetime'].to_numpy()).all():
                raise ValueError('chuỗi nến giữa các setup không khớp')
        st = K.session_table(self.df)
        st['split'] = np.where(st['session_id'].str[:10] <= K.CONST['split_train_end'], 'TRAIN', 'TEST')
        st['thang'] = [thang_of(s) for s in st['session_id']]
        self.st = st
        clean = (~st['splice'].to_numpy()) & (~st['thin'].to_numpy()) & (st['n'].to_numpy() >= K.CONST['min_bars_prof'])
        self.clean = clean
        self.days = int(clean.sum())
        self.days_split = {sp: int((clean & (st['split'] == sp).to_numpy()).sum()) for sp in ('TRAIN', 'TEST')}
        self.sno = self.df['session_no'].to_numpy()
        self.close = self.df['close'].to_numpy(float)
        self.rec = load_rec(self.df)
        self.zm = ZoneMap(self.rec)
        rng = np.random.default_rng(SEED)
        nS = int(self.sno.max()) + 1
        # dsh[:, 0] = 0 (thật); dsh[:, 1..REPS] = bản dời
        d = rng.uniform(SHIFT_LO, SHIFT_HI, (nS, REPS)) * rng.choice([-1.0, 1.0], (nS, REPS))
        self.dsh = np.hstack([np.zeros((nS, 1)), d])
        self.bias19 = bias_1900(self.df)
        self.bias_ph = self.PD.bias                        # độ nhạy: bias theo đúng code setup D (đầu mỗi (phiên, pha))
        self.load_s = time.time() - t0


# =============================================================================================
# 2. VÙNG VCL TẠI NẾN VÀO LỆNH
# =============================================================================================
class ZoneMap:
    """Tra nhanh các vùng VCL đang hiển thị tại nến i (dòng rec có bar == i — tính từ nến <= i)."""

    def __init__(self, rec):
        r = rec.sort_values('bar', kind='stable')
        self.bar = r['bar'].to_numpy()
        self.lo = r['lo'].to_numpy(float)
        self.hi = r['hi'].to_numpy(float)
        self.eid = r['eid'].to_numpy()

    def match(self, i, side, e, delta=0.0, tol=TOL):
        """Vùng hợp lệ cho lệnh (nến i, chiều side, giá vào e), bản đồ dời delta giá. Vai theo phía vùng so với giá:
        vùng nằm DƯỚI giá = hỗ trợ, TRÊN giá = kháng cự, ôm giá = 'đang chứa giá'.
          MUA hợp lệ: vùng hỗ trợ hoặc chứa giá, giá vào trong vùng ±tol  ⇔  lo <= e <= hi + tol
          BÁN hợp lệ: vùng kháng cự hoặc chứa giá, giá vào trong vùng ±tol ⇔  lo − tol <= e <= hi
        Nhiều vùng hợp lệ ⇒ chọn vùng GẦN giá nhất (chứa giá = 0), hòa thì vùng hẹp hơn. Trả (lo, hi, khoảng cách, eid) | None."""
        a = np.searchsorted(self.bar, i, 'left')
        b = np.searchsorted(self.bar, i, 'right')
        if b <= a:
            return None
        lo = self.lo[a:b] + delta
        hi = self.hi[a:b] + delta
        eps = 1e-9
        if side > 0:
            ok = (lo <= e + eps) & (e <= hi + tol + eps)
            dist = np.maximum(e - hi, 0.0)
        else:
            ok = (lo - tol - eps <= e) & (e <= hi + eps)
            dist = np.maximum(lo - e, 0.0)
        if not ok.any():
            return None
        k = np.flatnonzero(ok)
        j = k[np.lexsort(((hi - lo)[k], dist[k]))[0]]
        return float(lo[j]), float(hi[j]), float(dist[j]), int(self.eid[a + j])


def flag(D, idx, side, entry, k=0):
    """Cờ 'tại vùng VCL' cho mảng lệnh, ở bản k (0 = thật). Trả (inz bool, zlo, zhi)."""
    n = len(idx)
    inz = np.zeros(n, bool)
    zlo = np.full(n, np.nan)
    zhi = np.full(n, np.nan)
    for t in range(n):
        i = int(idx[t])
        m = D.zm.match(i, int(side[t]), float(entry[t]), float(D.dsh[D.sno[i], k]))
        if m is not None:
            inz[t], zlo[t], zhi[t] = True, m[0], m[1]
    return inz, zlo, zhi


def bar_flags(D, k=0):
    """Mỗi nến: có vùng hợp lệ cho MUA (fb) / BÁN (fs) nếu vào ở giá đóng nến đó (bản k). Dùng cho đối chứng ngẫu nhiên + độ phủ."""
    zm, C = D.zm, D.close
    b = zm.bar
    dl = D.dsh[D.sno[b], k]
    lo, hi, c = zm.lo + dl, zm.hi + dl, C[b]
    n = len(C)
    fb = np.zeros(n, bool)
    fs = np.zeros(n, bool)
    np.logical_or.at(fb, b, (lo <= c + 1e-9) & (c <= hi + TOL + 1e-9))
    np.logical_or.at(fs, b, (lo - TOL - 1e-9 <= c) & (c <= hi + 1e-9))
    return fb, fs


# =============================================================================================
# 3. BIAS
# =============================================================================================
def bias_1900(df):
    """Bias phiên (plan Benzo 3-D): dấu (giá đóng − VWAP tuần) ở nến 19:00 VN (nến đầu tiên có sm >= 840, đã bù giờ Mỹ).
    Có hiệu lực TỪ chính nến đó (sau khi nó đóng) và MANG SANG các nến sau tới ảnh chụp 19:00 kế tiếp — chỉ trong cùng tuần CME
    (VWAP tuần reset đầu tuần). Trước ảnh chụp đầu tiên của tuần ⇒ NaN (không xếp thuận/ngược). Lệnh pha Á/Âu dùng bias 19:00
    của phiên TRƯỚC (cái duy nhất đã biết lúc đó). Không nhìn trước: giá trị tại nến i chỉ dùng nến <= i."""
    vw = K.vwap_series(df)['vwap_w'].to_numpy(float)
    cl = df['close'].to_numpy(float)
    sm = df['sm'].to_numpy()
    sno = df['session_no'].to_numpy()
    wk = df['week_no'].to_numpy()
    n = len(df)
    snap = np.full(n, np.nan)
    us = sm >= K.CONST['sm_us_start']
    first = us & ~np.r_[False, us[:-1] & (sno[1:] == sno[:-1])]       # nến đầu tiên sm >= 840 của mỗi phiên
    pos = np.flatnonzero(first)
    s = np.sign(cl[pos] - vw[pos])
    snap[pos] = np.where(s == 0, np.nan, s)
    snap[pos[s == 0]] = 0.0                                               # đánh dấu "đã chụp nhưng bằng nhau" để không mang bias cũ sang
    out = pd.Series(snap).groupby(wk).ffill().to_numpy()
    return np.where(out == 0, np.nan, out)


# =============================================================================================
# 4. TÍN HIỆU 4 SETUP (gọi đúng hàm detect của từng setup, không sửa)
# =============================================================================================
def raw_entries(D, s, kw):
    if s == 'A':
        return SA.detect(D.df, D.DA.zc, D.DA.m5, n_min=kw['n_min'], body=kw['body'], zobj=D.DA, expire=kw['expire'], rr=kw['rr'])
    if s == 'B':
        return SB.detect(D.PB, kw['theta'], kw['N'])
    if s == 'C':
        P = D.PC
        return SC.detect(P['df'], P['zc'], P['mf'], mad=P['mad'], **kw)
    return SD.detect(D.PD, **kw)


def closed(t):
    return t[t['outcome'].isin(CLOSED)] if len(t) else t


def sim(D, ents, one=True):
    t = K.simulate(D.df, ents, one_at_a_time=one)
    if len(t):
        t['thang'] = [thang_of(x) for x in t['session_id']]
    return t


def tag(D, t, s):
    """Thêm cột setup, cờ vùng (thật) và bias cho bảng lệnh đã mô phỏng."""
    t = t.copy()
    t['S'] = s
    if not len(t):
        return t
    idx = t['idx'].to_numpy()
    if not np.allclose(t['entry'].to_numpy(float), D.close[idx]):
        raise ValueError('giá vào khác giá đóng nến tín hiệu — cờ theo nến sẽ sai')
    inz, zlo, zhi = flag(D, idx, t['side'].to_numpy(), t['entry'].to_numpy(float))
    t['inz'], t['zlo'], t['zhi'] = inz, zlo, zhi
    t['bias19'] = D.bias19[idx]
    t['bias_ph'] = D.bias_ph[idx]
    return t


def check_repro(base):
    """Điều kiện tiên quyết: khớp báo cáo cũ (n, WR 1 chữ số %, R TB 2 chữ số)."""
    out = {}
    for s in SETUPS:
        c = closed(base[s])
        n, wr, r = len(c), float((c['r'] > 0).mean()), float(c['r'].mean())
        e = EXPECT[s]
        ok = n == e[0] and abs(wr - e[1]) < 0.0015 and abs(round(r, 2) - e[2]) < 1e-9
        out[s] = (n, wr, r, ok)
    return out


# =============================================================================================
# 5. THỐNG KÊ
# =============================================================================================
def rstat(r):
    r = np.asarray(r, float)
    n = len(r)
    if n == 0:
        return dict(n=0, wr=np.nan, m=np.nan, se=np.nan, lo=np.nan, hi=np.nan)
    se = float(r.std(ddof=1) / math.sqrt(n)) if n > 1 else np.nan
    if n > 1:
        bs = r[np.random.default_rng(BOOT_SEED).integers(0, n, (BOOT, n))].mean(1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
    else:
        lo = hi = np.nan
    return dict(n=n, wr=float((r > 0).mean()), m=float(r.mean()), se=se, lo=float(lo), hi=float(hi))


def gmask(t, col, val):
    return np.ones(len(t), bool) if col is None else (t[col] == val).to_numpy()


def band(v):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    if not len(v):
        return (np.nan, np.nan, np.nan)
    return (float(v.mean()), float(np.quantile(v, 0.05)), float(np.quantile(v, 0.95)))


def verdict(cmp, nmin_ok):
    """Ngưỡng ĐÚNG NGUYÊN PLAN-LAN-CHAM.md mục 5: ngoài dải 5–95% đối chứng ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở >= 2/3 tháng,
    |hiệu| > 2 sai số (ở cả TRAIN và TEST). cmp[nhóm] = (giá trị thật, sai số, n, TB đối chứng, q5, q95).
    nmin_ok = False ⇒ không áp dụng (n nhỏ)."""
    if not nmin_ok:
        return 'không áp dụng (n < %d ở TRAIN hoặc TEST)' % MIN_N
    tr, te = cmp['TRAIN'], cmp['TEST']
    if any(np.isnan(x) for x in (tr[0], te[0], tr[3], te[3], tr[1], te[1])):
        return 'không áp dụng (thiếu số)'
    out_tr = tr[0] < tr[4] or tr[0] > tr[5]
    out_te = te[0] < te[4] or te[0] > te[5]
    s_tr, s_te = np.sign(tr[0] - tr[3]), np.sign(te[0] - te[3])
    ms = [np.sign(cmp[m][0] - cmp[m][3]) for m in ('T8', 'T9', 'T10') if m in cmp and not np.isnan(cmp[m][0]) and not np.isnan(cmp[m][3])]
    same_m = sum(1 for x in ms if x == s_tr) >= 2
    big = abs(tr[0] - tr[3]) > 2 * tr[1] and abs(te[0] - te[3]) > 2 * te[1]
    if out_tr and out_te and s_tr == s_te and same_m and big:
        return 'KHÁC đối chứng ' + ('▲' if s_tr > 0 else '▼')
    miss = []
    if not (out_tr and out_te):
        miss.append('trong dải 5–95%' + (' ở TRAIN' if (not out_tr and out_te) else ' ở TEST' if (out_tr and not out_te) else ''))
    if s_tr != s_te:
        miss.append('TRAIN/TEST ngược dấu')
    if not same_m:
        miss.append('< 2/3 tháng cùng dấu')
    if not big:
        miss.append('|hiệu| ≤ 2 sai số')
    return '≈ đối chứng (' + '; '.join(miss) + ')'


def diff_stat(a, b):
    """Hiệu R TB a − b và sai số (độc lập)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    return float(a.mean() - b.mean()), float(math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)))


# =============================================================================================
# 6. PHÉP ĐO A — lọc theo vùng; đối chứng dời + vào ngẫu nhiên tại vùng
# =============================================================================================
def shifted_flags(D, t):
    """Ma trận cờ (REPS+1, n): hàng 0 = thật, hàng k = bản dời k. Kèm zlo/zhi theo bản (để neo SL)."""
    n = len(t)
    F = np.zeros((REPS + 1, n), bool)
    ZL = np.full((REPS + 1, n), np.nan)
    ZH = np.full((REPS + 1, n), np.nan)
    if n == 0:
        return F, ZL, ZH
    idx, side, ent = t['idx'].to_numpy(), t['side'].to_numpy(), t['entry'].to_numpy(float)
    for k in range(REPS + 1):
        F[k], ZL[k], ZH[k] = flag(D, idx, side, ent, k)
    return F, ZL, ZH


def measure_A(t, F):
    """t = lệnh đã đóng; F = cờ (REPS+1, n). Trả dict nhóm → số đo + phán quyết hiệu (trong − ngoài) vs dời."""
    r = t['r'].to_numpy(float)
    res = {}
    for g, col, val in GROUPS:
        m = gmask(t, col, val)
        fi, fo = F[0] & m, ~F[0] & m
        d, se = diff_stat(r[fi], r[fo])
        dk, rin_k, nin_k = [], [], []
        for k in range(1, REPS + 1):
            a, b = F[k] & m, ~F[k] & m
            dk.append(r[a].mean() - r[b].mean() if a.sum() and b.sum() else np.nan)
            rin_k.append(r[a].mean() if a.sum() else np.nan)
            nin_k.append(a.sum())
        res[g] = dict(all=rstat(r[m]), inz=rstat(r[fi]), out=rstat(r[fo]), d=d, se=se, dband=band(dk), rin_band=band(rin_k),
                      nin_shift=float(np.mean(nin_k)))
    ok = all(res[g]['inz']['n'] >= MIN_N and res[g]['out']['n'] >= MIN_N for g in ('TRAIN', 'TEST'))
    v = verdict({g: (x['d'], x['se'], x['inz']['n'], *x['dband']) for g, x in res.items()}, ok)
    return res, v


def ctrl_codes(D, fb, fs):
    """Mã ghép cho kernel.control_sample: (chế độ kernel | có vùng cho MUA | có vùng cho BÁN | TRAIN/TEST | tháng); pha OFF ⇒ 'OFF'.
    control_sample chỉ rút nến CÙNG mã với nến vào thật ⇒ cùng chế độ, cùng điều kiện 'tại vùng' theo chiều lệnh, cùng nửa, cùng tháng."""
    mode = D.DA.mode.to_numpy()
    sp = D.df['split'].to_numpy()
    th = np.array([thang_of(s) for s in D.st['session_id']])[D.sno]
    ph = D.df['phase'].to_numpy()
    code = np.char.add(np.char.add(np.char.add(np.char.add(mode.astype(str), '|'), np.where(fb, 'b', '-')), np.where(fs, 's', '-')),
                       np.char.add(np.char.add('|', sp.astype(str)), np.char.add('|', th)))
    code = np.where(ph == 'OFF', 'OFF', code)
    return pd.Series(pd.factorize(code)[0], index=D.df.index)       # mã số nguyên: so sánh nhanh, cùng nghĩa


def random_at_zone(D, t, codes):
    """Vào NGẪU NHIÊN tại vùng VCL (kernel.control_sample, không sửa): mỗi lệnh thật tại vùng rút 1 nến cùng mã (ctrl_codes), cùng
    chiều, SL = râu nến đó + 0,3 (kernel.risk), cùng R:R với lệnh thật. 200 lần. Trả dict nhóm → (TB, q5, q95) của R TB đối chứng."""
    ti = t[t['inz']]
    if not len(ti):
        return {}
    recs = [dict(idx=int(x.idx), side=int(x.side), entry=float(x.entry), sl=float(x.sl), tp=float(x.tp), setup=str(x.S), zone='VCL')
            for x in ti.itertuples()]
    grp = {int(x.idx): (x.split, x.thang) for x in ti.itertuples()}
    per = {g: [] for g, _, _ in GROUPS}
    for sd in range(CTRL_SEEDS):
        ce = K.control_sample(D.df, D.DA.zc, codes, entries=recs, n_random=1, seed=sd)
        if not ce:
            continue
        c = closed(K.simulate(D.df, ce, one_at_a_time=False))
        if not len(c):
            continue
        src = c['note'].str.extract(r'idx (\d+)')[0].astype(int).map(grp)
        spv = np.array([x[0] for x in src])
        thv = np.array([x[1] for x in src])
        rv = c['r'].to_numpy(float)
        for g, col, val in GROUPS:
            m = np.ones(len(c), bool) if col is None else (spv == val if col == 'split' else thv == val)
            per[g].append(rv[m].mean() if m.any() else np.nan)
    return {g: band(v) for g, v in per.items()}


def verdict_vs_band(t, sel, bands):
    """R TB thật của t[sel] so với dải đối chứng theo nhóm (TRAIN/TEST/tháng)."""
    r = t['r'].to_numpy(float)
    cmp, ns = {}, {}
    for g, col, val in GROUPS:
        m = sel & gmask(t, col, val)
        s = rstat(r[m])
        ns[g] = s['n']
        b = bands.get(g, (np.nan,) * 3)
        cmp[g] = (s['m'], s['se'], s['n'], *b)
    ok = ns['TRAIN'] >= MIN_N and ns['TEST'] >= MIN_N
    return verdict(cmp, ok), cmp


# =============================================================================================
# 7. PHÉP ĐO B — bias
# =============================================================================================
def measure_bias(t, F, col='bias19'):
    """Trong lệnh TẠI VÙNG: THUẬN bias (chiều lệnh = bias) vs NGƯỢC. Đối chứng: cùng phép tách trên lệnh 'tại vùng' của bản đồ dời."""
    r = t['r'].to_numpy(float)
    side = t['side'].to_numpy()
    b = t[col].to_numpy(float)
    th, ng = side == b, side == -b
    res = {}
    for g, c_, v_ in GROUPS:
        m = gmask(t, c_, v_)
        fi = F[0] & m
        d, se = diff_stat(r[fi & th], r[fi & ng])
        dk = []
        for k in range(1, REPS + 1):
            a = F[k] & m
            dk.append(r[a & th].mean() - r[a & ng].mean() if (a & th).sum() and (a & ng).sum() else np.nan)
        res[g] = dict(th=rstat(r[fi & th]), ng=rstat(r[fi & ng]), na=int((fi & np.isnan(b)).sum()), d=d, se=se, dband=band(dk),
                      all_th=rstat(r[m & th]), all_ng=rstat(r[m & ng]))
    ok = all(res[g]['th']['n'] >= MIN_N and res[g]['ng']['n'] >= MIN_N for g in ('TRAIN', 'TEST'))
    v = verdict({g: (x['d'], x['se'], x['th']['n'], *x['dband']) for g, x in res.items()}, ok)
    return res, v


def zone_only(D, rr_list=ANCHOR_RR):
    """'Bias CHỈ BẰNG vùng' (không cần setup Benzo): mỗi LẦN CHẠM VCL (máy lan_cham: τ=0, E=2 giá, G=5) có vai rõ, tại nến bắt đầu
    lần chạm: nếu giá đóng nằm trong vùng ±1 giá đúng phía (hỗ trợ ⇒ MUA: lo <= C <= hi+1; kháng cự ⇒ BÁN: lo−1 <= C <= hi) thì vào
    ở giá đóng, chiều theo vai vùng; SL = biên xa vùng ± 0,5 giá (SL > 4 giá ⇒ bỏ); TP 1,5R và 2R; 1 lệnh mở cùng lúc; chỉ phiên đo
    được (không thin/splice/phiên 0), không pha OFF. Thật = bản 0, đối chứng = cùng máy trên bản đồ dời (cùng ma trận δ).
    Trả {rr: (bảng lệnh thật, {nhóm: dải R TB dời}, {nhóm: dải lệnh/ngày dời})}."""
    import lan_cham as LC
    import vcl5 as V5
    df, st = D.df, D.st
    meas = V5.do_duoc(st)
    B = LC.bar_arrays(df)
    rec = D.rec
    rsno = D.sno[rec['bar'].to_numpy()]
    r_sorted = rec.sort_values(['eid', 'bar'], kind='stable')   # đúng thứ tự dòng `r` mà LC.episodes trả srow
    lo_s, hi_s = r_sorted['lo'].to_numpy(float), r_sorted['hi'].to_numpy(float)
    sno_s = D.sno[r_sorted['bar'].to_numpy()]
    eps_all = []
    for a in range(0, REPS + 1, 26):                            # chia lô bản để giữ bộ nhớ vừa phải
        cols = np.arange(a, min(REPS + 1, a + 26))
        ep, _, _ = LC.episodes(B, rec, D.dsh[rsno][:, cols])    # dời theo dòng rec gốc (LC.episodes tự sắp lại)
        ep['rep'] = cols[ep['rep'].to_numpy()]
        eps_all.append(ep)
    ep = pd.concat(eps_all, ignore_index=True)
    ep = ep[ep['vai'].isin([LC.KC, LC.HT]) & (ep['ket'] != LC.HDL)]
    t0 = ep['bat_dau'].to_numpy()
    ep = ep[meas[D.sno[t0]] & (df['phase'].to_numpy()[t0] != 'OFF')]
    sr, rp = ep['srow'].to_numpy(), ep['rep'].to_numpy()
    lo = lo_s[sr] + D.dsh[sno_s[sr], rp]
    hi = hi_s[sr] + D.dsh[sno_s[sr], rp]
    t0 = ep['bat_dau'].to_numpy()
    c = D.close[t0]
    side = np.where(ep['vai'].to_numpy() == LC.HT, 1, -1)
    ok = np.where(side > 0, (lo <= c + 1e-9) & (c <= hi + TOL + 1e-9), (lo - TOL - 1e-9 <= c) & (c <= hi + 1e-9))
    tick = K.CONST['tick']
    raw_sl = np.where(side > 0, lo - ANCHOR_PAD, hi + ANCHOR_PAD)
    sl = np.where(side > 0, np.floor(raw_sl / tick + 1e-9), np.ceil(raw_sl / tick - 1e-9)) * tick
    sl = np.round(sl, 6)
    risk = (c - sl) * side
    ok &= (risk > 0) & (risk <= SL_MAX + 1e-9)
    E = pd.DataFrame(dict(rep=rp[ok], idx=t0[ok], side=side[ok], entry=c[ok], sl=sl[ok], risk=risk[ok]))
    out = {}
    for rr in rr_list:
        per = {g: [] for g, _, _ in GROUPS}
        pday = []
        real = None
        for k, g_ in E.groupby('rep', sort=True):
            ents = [dict(idx=int(x.idx), side=int(x.side), entry=float(x.entry), sl=float(x.sl),
                         tp=round(float(x.entry) + x.side * rr * float(x.risk), 6), setup='Z', zone='VCL') for x in g_.itertuples()]
            tr = closed(sim(D, ents, one=True))
            if k == 0:
                real = tr
                continue
            pday.append(len(tr) / D.days)
            for g, col, val in GROUPS:
                m = gmask(tr, col, val)
                per[g].append(tr['r'].to_numpy(float)[m].mean() if m.any() else np.nan)
        out[rr] = (real, {g: band(v) for g, v in per.items()}, band(pday))
    return out


# =============================================================================================
# 8. PHÉP ĐO C — neo SL/TP theo vùng
# =============================================================================================
def anchor_entries(t, zlo, zhi, sel, rr):
    """Cùng tín hiệu, SL = biên xa vùng ± 0,5 (MUA: lo − 0,5; BÁN: hi + 0,5), làm tròn ra xa theo tick; SL > 4 giá ⇒ bỏ.
    TP = rr × khoảng SL. Trả list entry + mảng chỉ số lệnh giữ lại."""
    tick = K.CONST['tick']
    ents, keep = [], []
    for j in np.flatnonzero(sel):
        x = t.iloc[j]
        s, e = int(x['side']), float(x['entry'])
        raw = zlo[j] - ANCHOR_PAD if s > 0 else zhi[j] + ANCHOR_PAD
        sl = (math.floor(raw / tick + 1e-9) if s > 0 else math.ceil(raw / tick - 1e-9)) * tick
        sl = round(sl, 6)
        d = (e - sl) * s
        if d <= 0 or d > SL_MAX + 1e-9:
            continue
        ents.append(dict(idx=int(x['idx']), side=s, entry=e, sl=sl, tp=round(e + s * rr * d, 6), setup='ANC-' + str(x['S']),
                         zone='VCL', src=int(j)))
        keep.append(j)
    return ents, np.array(keep, int)


def measure_C(D, t, F, ZL, ZH, rr):
    """Thật: lệnh tại vùng, neo SL/TP theo vùng thật; so (i) R gốc của CHÍNH các lệnh đó (cặp), (ii) R neo theo vùng dời."""
    ents, keep = anchor_entries(t, ZL[0], ZH[0], F[0], rr)
    ta = closed(sim(D, ents, one=False))
    if len(ta):
        src = ta['src'].to_numpy()
        ta['split'] = t['split'].to_numpy()[src]
        ta['thang'] = t['thang'].to_numpy()[src]
        ta['r_goc'] = t['r'].to_numpy(float)[src]
    per = {g: [] for g, _, _ in GROUPS}
    for k in range(1, REPS + 1):
        e2, _ = anchor_entries(t, ZL[k], ZH[k], F[k], rr)
        tk = closed(sim(D, e2, one=False))
        if not len(tk):
            for g in per:
                per[g].append(np.nan)
            continue
        src = tk['src'].to_numpy()
        spv, thv = t['split'].to_numpy()[src], t['thang'].to_numpy()[src]
        rv = tk['r'].to_numpy(float)
        for g, col, val in GROUPS:
            m = np.ones(len(tk), bool) if col is None else (spv == val if col == 'split' else thv == val)
            per[g].append(rv[m].mean() if m.any() else np.nan)
    bands = {g: band(v) for g, v in per.items()}
    n_drop = int(F[0].sum() - len(keep))
    if not len(ta):
        return ta, bands, 'không có lệnh', {}, n_drop
    v, cmp = verdict_vs_band(ta, np.ones(len(ta), bool), bands)
    return ta, bands, v, cmp, n_drop


# =============================================================================================
# 9. PHÉP ĐO D — số lệnh: lọc, nới cổng tại vùng
# =============================================================================================
def raw_flagged(D, ents):
    """Cờ vùng cho list entry thô (chưa mô phỏng), mọi bản. Trả ma trận (REPS+1, n)."""
    n = len(ents)
    F = np.zeros((REPS + 1, n), bool)
    if not n:
        return F
    idx = np.array([e['idx'] for e in ents])
    side = np.array([e['side'] for e in ents])
    ent = np.array([e['entry'] for e in ents], float)
    for k in range(REPS + 1):
        F[k] = flag(D, idx, side, ent, k)[0]
    return F


def rarr(t):
    return t['r'].to_numpy(float) if len(t) else np.zeros(0)


def measure_D(D, s):
    """(a) lọc tín hiệu gốc THÔ theo vùng rồi mới mô phỏng (1 lệnh mở) — chiến lược 'chỉ vào tại vùng VCL' thực tế;
    (b) bản NỚI: mọi nơi / chỉ tại vùng VCL / chỉ tại vùng dời; hỗn hợp = gốc ∪ (nới tại vùng)."""
    e0 = raw_entries(D, s, MAIN[s])
    e1 = raw_entries(D, s, LOOSE[s])
    F0 = raw_flagged(D, e0)
    F1 = raw_flagged(D, e1)
    idx0 = {e['idx'] for e in e0}

    def pick(es, f):
        return [e for e, x in zip(es, f) if x]

    def hybrid(f1):
        add = [e for e, x in zip(e1, f1) if x and e['idx'] not in idx0]
        return e0 + add

    out = dict(raw0=len(e0), raw1=len(e1))
    out['orig'] = closed(sim(D, e0))
    out['filt'] = closed(sim(D, pick(e0, F0[0])))
    out['loose_all'] = closed(sim(D, e1))
    out['loose_vcl'] = closed(sim(D, pick(e1, F1[0])))
    out['hyb'] = closed(sim(D, hybrid(F1[0])))
    sh = {'filt': [], 'loose_vcl': [], 'hyb': []}
    shr = {'filt': {g: [] for g, _, _ in GROUPS}, 'loose_vcl': {g: [] for g, _, _ in GROUPS}, 'hyb': {g: [] for g, _, _ in GROUPS}}
    for k in range(1, REPS + 1):
        for key, ents in (('filt', pick(e0, F0[k])), ('loose_vcl', pick(e1, F1[k])), ('hyb', hybrid(F1[k]))):
            tk = closed(sim(D, ents))
            sh[key].append(len(tk) / D.days)
            for g, col, val in GROUPS:
                m = gmask(tk, col, val) if len(tk) else np.zeros(0, bool)
                shr[key][g].append(tk['r'].to_numpy(float)[m].mean() if m.any() else np.nan)
    out['shift_pday'] = {k: band(v) for k, v in sh.items()}
    out['shift_r'] = {k: {g: band(v) for g, v in d.items()} for k, d in shr.items()}
    for key in ('filt', 'loose_vcl'):
        t = out[key]
        if len(t):
            out['v_' + key] = verdict_vs_band(t, np.ones(len(t), bool), out['shift_r'][key])[0]
        else:
            out['v_' + key] = 'không có lệnh'
    return out


# =============================================================================================
# 10. ẢNH MINH HOẠ
# =============================================================================================
def draw(D, T, sid, split, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection, LineCollection
    df, st = D.df, D.st
    s = int(st.index[st['session_id'] == sid][0])
    a, b = int(st.loc[s, 'start_pos']), int(st.loc[s, 'end_pos'])
    ts = T[(T['idx'] >= a) & (T['idx'] <= b)].sort_values('idx')
    W_ = 330                                               # cửa sổ 330 nến chứa NHIỀU lệnh tại vùng nhất (rồi nhiều lệnh nhất)
    ii, iz = ts['idx'].to_numpy(), ts['inz'].to_numpy()
    best, w0 = (-1, -1), a
    for x0 in range(a, max(a + 1, b - W_ + 2), 5):
        m_ = (ii >= x0 + 15) & (ii < x0 + W_ - 30)
        sc = (int((m_ & iz).sum()), int(m_.sum()))
        if sc > best:
            best, w0 = sc, x0
    w1 = min(b + 1, w0 + W_)
    d = df.iloc[w0:w1]
    x = np.arange(len(d))
    O, H, L, C = (d[c].to_numpy(float) for c in ('open', 'high', 'low', 'close'))
    INK, MUTED = '#0b0b0b', '#52514e'
    fig, ax = plt.subplots(figsize=(22, 10), dpi=110)
    fig.patch.set_facecolor('#fcfcfb')
    ax.set_facecolor('#fcfcfb')
    zm = D.zm
    m = (zm.bar >= w0) & (zm.bar < w1)
    polys = [[(bb - w0 - .5, lo), (bb - w0 + .5, lo), (bb - w0 + .5, hi), (bb - w0 - .5, hi)]
             for bb, lo, hi in zip(zm.bar[m], zm.lo[m], zm.hi[m])]
    ax.add_collection(PolyCollection(polys, facecolors='#2a78d6', edgecolors='none', alpha=0.13))
    ax.add_collection(LineCollection([[(xx, l), (xx, h)] for xx, l, h in zip(x, L, H)], colors=INK, linewidths=0.6))
    up = C >= O
    ax.bar(x[up], (C - O)[up], bottom=O[up], width=0.7, color='white', edgecolor=INK, linewidth=0.5)
    ax.bar(x[~up], (O - C)[~up], bottom=C[~up], width=0.7, color=INK, edgecolor=INK, linewidth=0.5)
    shown = ts[(ts['idx'] >= w0) & (ts['idx'] < w1)]
    lastx, lvl = -999, 0
    for tr in shown.itertuples():
        xi = tr.idx - w0
        lvl = lvl + 1 if xi - lastx < 70 else 0             # nhãn gần nhau ⇒ đẩy so le để không chồng chữ
        lastx = xi
        xe = min(tr.exit_idx, w1 - 1) - w0
        col = '#1baf7a' if tr.side > 0 else '#d63a2a'
        ax.annotate('', xy=(xi, tr.entry), xytext=(xi, tr.entry - tr.side * 3.0),
                    arrowprops=dict(arrowstyle='-|>', color=col, lw=2.4 if tr.inz else 1.4, alpha=1.0 if tr.inz else 0.6))
        ax.plot([xi, xe], [tr.sl, tr.sl], color='#d63a2a', lw=1.6, ls='--')
        ax.plot([xi, xe], [tr.tp, tr.tp], color='#1baf7a', lw=1.6, ls='--')
        ax.plot([xi, xe], [tr.entry, tr.exit_price], color=MUTED, lw=1.0, ls=':')
        ax.plot([xe], [tr.exit_price], marker='X', ms=11, color='#1baf7a' if tr.r > 0 else '#d63a2a', mec=INK)
        if tr.inz:
            ax.add_patch(plt.Rectangle((xi - 2.5, tr.zlo), 5, tr.zhi - tr.zlo, fill=False, edgecolor='#2a78d6', lw=2.4))
        lab = '%s %s %s · vào %.1f · SL %.1f · TP %.1f · %s %+.2fR · %s' % (
            tr.S, 'MUA' if tr.side > 0 else 'BÁN', str(tr.t_vn)[11:16], tr.entry, tr.sl, tr.tp, tr.outcome, tr.r,
            'TẠI VÙNG VCL %.1f–%.1f' % (tr.zlo, tr.zhi) if tr.inz else 'ngoài vùng VCL')
        yy = tr.entry - tr.side * (3.6 + 2.2 * lvl)
        ax.text(xi + 1, yy, lab, fontsize=9, fontweight='bold', color=INK, va='top' if tr.side > 0 else 'bottom',
                bbox=dict(facecolor='#fcfcfb', edgecolor='none', alpha=0.85, pad=1.5))
    ax.set_xlim(-2, len(d) + 1)
    lo_y = min(L.min(), shown['sl'].min() if len(shown) else L.min()) - 3
    hi_y = max(H.max(), shown['tp'].max() if len(shown) else H.max()) + 3
    ax.set_ylim(lo_y, hi_y)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
    ax.grid(True, which='major', color='#e6e5e0', linewidth=0.6)
    tv = d['t_vn'].dt.strftime('%H:%M').to_numpy()
    tick = np.flatnonzero(d['t_vn'].dt.minute.to_numpy() % 30 == 0)
    ax.set_xticks(tick)
    ax.set_xticklabels([tv[k] for k in tick], fontsize=9, color=MUTED)
    ax.tick_params(axis='y', labelsize=9, labelright=True, colors=MUTED)
    ax.set_xlabel('giờ VN (UTC+7)', color=MUTED)
    ax.set_title('Benzo Trader × Vùng Canh Lệnh · GCZ26 M1 · phiên %s (%s)\n'
                 'Xanh nhạt = vùng VCL đang hiển thị (v5, rộng 2–5 giá). Mũi tên = lệnh Benzo (xanh MUA, đỏ BÁN; đậm = tại vùng VCL, '
                 'khung xanh = vùng được dùng). Gạch đỏ = SL, gạch xanh = TP gốc của setup, X = chỗ thoát.' % (sid, split),
                 fontsize=11, loc='left', color=INK)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


# =============================================================================================
# 11. ĐỊNH DẠNG
# =============================================================================================
def f2(x, p=2, sign=False):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return '—'
    return ('%+.*f' if sign else '%.*f') % (p, x)


def pc(x):
    return '—' if x is None or (isinstance(x, float) and np.isnan(x)) else '%.0f%%' % (100 * x)


def scell(s):
    """n · WR · R TB [KTC 95%]"""
    if s['n'] == 0:
        return 'n=0'
    return 'n=%d · WR %s · **%s** [%s; %s]' % (s['n'], pc(s['wr']), f2(s['m'], sign=True), f2(s['lo'], sign=True), f2(s['hi'], sign=True))


def bcell(b):
    return '%s [%s; %s]' % (f2(b[0], sign=True), f2(b[1], sign=True), f2(b[2], sign=True))


# =============================================================================================
# 12. MAIN
# =============================================================================================
def main():
    t00 = time.time()
    D = Data()
    print('nạp %.0fs' % D.load_s, flush=True)
    base, tags = {}, {}
    for s in SETUPS:
        base[s] = sim(D, raw_entries(D, s, MAIN[s]))
    rep = check_repro(base)
    if not all(v[3] for v in rep.values()):
        raise SystemExit('KHÔNG khớp báo cáo cũ: %r' % rep)
    for s in SETUPS:
        tags[s] = closed(tag(D, base[s], s)).reset_index(drop=True)
    T = pd.concat([tags[s] for s in SETUPS], ignore_index=True)
    tags['ALL'] = T
    KEYS = list(SETUPS) + ['ALL']
    # ---------- cờ dời
    FL = {}
    for s in SETUPS:
        FL[s] = shifted_flags(D, tags[s])
    FL['ALL'] = tuple(np.hstack([FL[s][j] for s in SETUPS]) for j in range(3))
    print('cờ dời %.0fs' % (time.time() - t00), flush=True)
    # ---------- độ phủ: % nến có vùng hợp lệ (thật vs dời)
    fb0, fs0 = bar_flags(D, 0)
    measm = D.clean[D.sno] & (D.df['phase'].to_numpy() != 'OFF')
    cov = (fb0[measm].mean(), fs0[measm].mean())
    covk = [bar_flags(D, k) for k in (1, 2, 3)]
    cov_s = (np.mean([c[0][measm].mean() for c in covk]), np.mean([c[1][measm].mean() for c in covk]))
    codes = ctrl_codes(D, fb0, fs0)
    # ---------- phép A
    RA, VA, RZ, VZ = {}, {}, {}, {}
    for s in KEYS:
        RA[s], VA[s] = measure_A(tags[s], FL[s][0])
        RZ[s] = random_at_zone(D, tags[s], codes)
        t = tags[s]
        VZ[s] = verdict_vs_band(t, t['inz'].to_numpy(), RZ[s])[0] if len(RZ[s]) else 'không có lệnh'
    print('phép A %.0fs' % (time.time() - t00), flush=True)
    # ---------- phép B
    RB, VB, RBp = {}, {}, {}
    for s in KEYS:
        RB[s], VB[s] = measure_bias(tags[s], FL[s][0], 'bias19')
        RBp[s], _ = measure_bias(tags[s], FL[s][0], 'bias_ph')
    ZO = zone_only(D)
    VZO = {rr: verdict_vs_band(ZO[rr][0], np.ones(len(ZO[rr][0]), bool), ZO[rr][1])[0] for rr in ANCHOR_RR}
    print('phép B %.0fs' % (time.time() - t00), flush=True)
    # ---------- phép C
    RC = {}
    for s in KEYS:
        RC[s] = {rr: measure_C(D, tags[s], *FL[s], rr) for rr in ANCHOR_RR}
    print('phép C %.0fs' % (time.time() - t00), flush=True)
    # ---------- phép D
    RD = {s: measure_D(D, s) for s in SETUPS}
    print('phép D %.0fs' % (time.time() - t00), flush=True)
    # ---------- ảnh
    os.makedirs(IMG, exist_ok=True)
    imgs = []
    for sp in ('TRAIN', 'TEST'):
        ti = T[(T['split'] == sp) & T['inz']]
        cnt = ti.groupby('session_id').size().sort_values(ascending=False, kind='stable')
        sid = cnt.index[0]
        p = os.path.join(IMG, 'benzo_vcl_%s_%s.png' % (sp, sid))
        draw(D, T, sid, sp, p)
        imgs.append((sp, sid, os.path.basename(p), int(cnt.iloc[0])))
    md = report(D, rep, tags, RA, VA, RZ, VZ, RB, VB, RBp, ZO, VZO, RC, RD, cov, cov_s, imgs, time.time() - t00)
    path = os.path.join(REPORT, 'BENZO-VCL.md')
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    tail = old.split('<!-- NHAN-XET -->', 1)[1] if '<!-- NHAN-XET -->' in old else '\n## Kết luận\n(chưa viết)\n'
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(md + '\n<!-- NHAN-XET -->' + tail)
    print(md)
    print('TỔNG %.0fs' % (time.time() - t00))


def report(D, rep, tags, RA, VA, RZ, VZ, RB, VB, RBp, ZO, VZO, RC, RD, cov, cov_s, imgs, sec):
    KEYS = list(SETUPS) + ['ALL']
    L = ['# Benzo Trader × Vùng Canh Lệnh — đặt setup và bias vào vùng VCL có cải thiện không?', '']
    L += ['## 0. Quy tắc ĐĂNG KÝ TRƯỚC (viết và chốt trong code `benzo_vcl.py` trước khi chạy lần đầu; không đổi sau khi thấy TEST)', '',
          '- **Dữ liệu (QĐ-6):** chỉ `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (giờ UTC). TRAIN = phiên ≤ 2026-09-15, TEST từ 2026-09-16. '
          'Phiên sạch (không thin/splice, ≥ 300 nến) = **%d** (TRAIN %d, TEST %d) — chia "lệnh/ngày" cho số này. Chi phí 0,2 giá/lệnh; '
          'nến chạm cả SL lẫn TP ⇒ tính SL (đều là `kernel.simulate`).' % (D.days, D.days_split['TRAIN'], D.days_split['TEST']),
          '- **Tín hiệu gốc** = đúng ô chính đã báo: A V3 (hồi ≥ 3 nến, thân CF 0,5, hết hạn 30 nến, TP 3R) · B (θ 0,5, cụm 3 nến, TP 3R) · '
          'C (xuyên ≥ 2 tick, TP 2R cố định) · D V3 (move ≥ 5, hồi ≤ 70%, không cần Z, TP 2R). Gọi thẳng `detect` của từng `setup_*.py`, không sửa.',
          '- **Vùng VCL** = bộ vùng ĐANG HIỂN THỊ của VCL v5 tại nến vào lệnh (rộng 2–5 giá; vùng tại nến i chỉ dùng nến ≤ i — test cắt dữ liệu '
          'trong `vung-canh-lenh/research/test_vcl.py`). Lệnh vào ở giá đóng nến tín hiệu, cùng thời điểm vùng được tính.',
          '- **"Tại vùng VCL"** (phép đo A): có ít nhất một vùng mà giá vào nằm trong vùng ±1 giá ĐÚNG PHÍA. Vai theo phía vùng so với giá '
          '(không dùng vai chốt): vùng dưới giá = hỗ trợ, trên giá = kháng cự, ôm giá = "đang chứa giá". MUA hợp lệ khi lo ≤ giá vào ≤ hi + 1 '
          '(vùng hỗ trợ hoặc chứa giá); BÁN hợp lệ khi lo − 1 ≤ giá vào ≤ hi. Nhiều vùng hợp lệ ⇒ lấy vùng gần nhất, hòa thì vùng hẹp hơn.',
          '- **Đối chứng dời:** toàn bộ bản đồ vùng VCL của mỗi phiên dời δ, |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, cố định trong (phiên, bản), '
          '**%d bản, CÙNG một ma trận δ cho mọi setup và mọi phép đo** (hạt giống %d); gắn cờ lại y hệt. '
          '**Đối chứng "vào ngẫu nhiên tại vùng":** `kernel.control_sample` (không sửa), mỗi lệnh thật tại vùng rút 1 nến cùng chế độ kernel, '
          'cùng điều kiện "tại vùng" theo chiều lệnh, cùng TRAIN/TEST, cùng tháng, cùng chiều, cùng R:R; SL = râu nến đó + 0,3; %d lần.' % (REPS, SEED, CTRL_SEEDS),
          '- **Bias (phép đo B):** dấu (giá đóng − VWAP tuần) ở nến 19:00 VN (đã bù giờ Mỹ), có hiệu lực từ nến đó và **mang sang** tới ảnh '
          'chụp 19:00 kế tiếp trong cùng tuần CME (lệnh pha Á/Âu dùng bias 19:00 của phiên trước — thứ duy nhất đã biết lúc đó; đầu tuần chưa '
          'có ảnh chụp ⇒ không xếp). THUẬN = chiều lệnh trùng bias. Độ nhạy (chỉ báo): bias đúng như code setup D (dấu ở nến đầu mỗi (phiên, pha)). '
          '**"Bias chỉ bằng vùng":** mỗi lần chạm VCL (máy `lan_cham`: τ = 0, E = 2 giá, G = 5) có vai rõ, nếu giá đóng nến bắt đầu nằm trong '
          'vùng ±1 giá đúng phía ⇒ vào theo vai (hỗ trợ ⇒ MUA), SL/TP như phép đo C, 1 lệnh mở; đối chứng = cùng máy trên bản đồ dời.',
          '- **Neo SL/TP theo vùng (phép đo C):** cùng tín hiệu tại vùng, SL = biên xa của vùng ± 0,5 giá (MUA: lo − 0,5; BÁN: hi + 0,5), '
          'làm tròn ra xa theo tick, **SL > 4 giá ⇒ bỏ lệnh**; TP = 1,5R và 2R — báo cả hai, không chọn. Mô phỏng không chặn chồng lệnh để giữ '
          'đúng cặp tín hiệu với lệnh gốc. Đối chứng = neo theo vùng dời.',
          '- **Số lệnh (phép đo D):** (a) lọc tín hiệu THÔ theo vùng rồi mới mô phỏng (1 lệnh mở) = chiến lược "chỉ vào tại vùng"; '
          '(b) bản NỚI = **ô lỏng nhất của lưới 3×3 đã đăng ký trong RESULTS của chính setup đó** (A: %s; B: %s; C: %s; D: %s) — '
          'chạy ở mọi nơi / chỉ tại vùng VCL / chỉ tại vùng dời; "hỗn hợp" = tín hiệu gốc ∪ tín hiệu nới tại vùng.' % (
              LOOSE_TXT['A'], LOOSE_TXT['B'], LOOSE_TXT['C'], LOOSE_TXT['D']),
          '- **Ngưỡng "khác đối chứng có ý nghĩa" (NGUYÊN `PLAN-LAN-CHAM.md` mục 5):** giá trị thật ngoài dải 5–95%% đối chứng ở CẢ TRAIN và TEST, '
          'cùng dấu, cùng dấu ở ≥ 2/3 tháng (T8/T9/T10), VÀ |hiệu| > 2 sai số ở cả TRAIN và TEST. Thiếu một ⇒ "≈ đối chứng". '
          '**Chỉ áp dụng khi mỗi nhóm so sánh có ≥ %d lệnh ở CẢ TRAIN và TEST**, nếu không ghi "không áp dụng (n nhỏ)".' % MIN_N,
          '- **Số phép so có phán quyết:** A: 5 (hiệu trong−ngoài vs dời) + 5 (tại vùng vs vào ngẫu nhiên tại vùng); B: 5 (thuận−ngược vs dời) '
          '+ 2 (chỉ bằng vùng 1,5R/2R); C: 10 (5 nhóm × 2 TP); D: 8 (lọc + nới tại vùng, 4 setup) ⇒ **35 phép so**. Nếu mỗi phép có ~5% '
          'vượt ngưỡng do ngẫu nhiên thì kỳ vọng ~2 ô "vượt" mà không có thật; ngưỡng nhiều điều kiện chặt hơn 5% nhiều, nhưng vẫn phải đọc với cảnh giác.',
          '- **Khoảng tin cậy 95%%:** lấy mẫu lại (bootstrap) theo lệnh, %d lần, hạt giống %d. Sai số đánh giá thấp vì lệnh cùng phiên không độc lập.' % (BOOT, BOOT_SEED), '']
    # 1. tái tạo
    L += ['## 1. Điều kiện tiên quyết — tái tạo tín hiệu gốc', '', '| Setup | n (cũ → nay) | WR (cũ → nay) | R TB (cũ → nay) | khớp |', '|---|---|---|---|---|']
    for s in SETUPS:
        n, wr, r, ok = rep[s]
        e = EXPECT[s]
        L.append('| %s | %d → %d | %.1f%% → %.1f%% | %+.2f → %+.2f | %s |' % (TEN[s], e[0], n, 100 * e[1], 100 * wr, e[2], r, 'CÓ' if ok else 'KHÔNG'))
    L += ['', 'Cả 4 khớp đúng báo cáo cũ ⇒ mọi số dưới đây đo trên đúng tín hiệu đã báo. Thời gian chạy toàn bộ: %.0f giây.' % sec, '']
    L += ['**Độ phủ của vùng VCL (để hiểu "tại vùng" chọn lọc tới đâu):** trong các nến của phiên sạch (không pha OFF), vào lệnh ở giá đóng '
          'thì **%s nến có vùng hợp lệ cho MUA, %s cho BÁN** (bản đồ dời 3–15 giá: %s / %s). Tức là "tại vùng VCL" là điều kiện khá rộng: '
          'gần một nửa số nến đã thỏa.' % (pc(cov[0]), pc(cov[1]), pc(cov_s[0]), pc(cov_s[1])), '']
    # 2. bảng chính
    L += ['## 2. BẢNG CHÍNH (gộp TRAIN+TEST)', '',
          'R TB sau phí, [khoảng tin cậy 95%%]. "Dời" = cùng phép đo trên bản đồ vùng dời 3–15 giá: TB [5%%; 95%%] của 100 bản. '
          'Lệnh/ngày chia %d phiên sạch.' % D.days, '',
          '| Setup | Lệnh gốc | TẠI vùng VCL | NGOÀI vùng | Hiệu trong − ngoài (thật ± sai số) | Hiệu khi DỜI vùng | R tại vùng DỜI | Vào NGẪU NHIÊN tại vùng VCL |',
          '|---|---|---|---|---|---|---|---|']
    for s in KEYS:
        x = RA[s]['GỘP']
        rz = RZ[s].get('GỘP', (np.nan,) * 3)
        L.append('| %s | %s · %.2f/ngày | %s · %.2f/ngày | %s | **%s** ± %s | %s | %s | %s |' % (
            TEN[s], scell(x['all']), x['all']['n'] / D.days, scell(x['inz']), x['inz']['n'] / D.days, scell(x['out']),
            f2(x['d'], sign=True), f2(x['se']), bcell(x['dband']), bcell(x['rin_band']), bcell(rz)))
    L += ['', '**Phán quyết (ngưỡng mục 0):**', '', '| Setup | Hiệu trong − ngoài vs dời | Tại vùng vs vào ngẫu nhiên tại vùng |', '|---|---|---|']
    for s in KEYS:
        L.append('| %s | %s | %s |' % (TEN[s], VA[s], VZ[s]))
    L += ['']
    L += ['### 2.1 Theo TRAIN / TEST / tháng (R TB tại vùng · ngoài vùng · hiệu [dải dời 5–95%])', '',
          '| Setup | TRAIN | TEST | T8 | T9 | T10 |', '|---|---|---|---|---|---|']
    for s in KEYS:
        cells = []
        for g in ('TRAIN', 'TEST', 'T8', 'T9', 'T10'):
            x = RA[s][g]
            cells.append('%s (n%d) · %s (n%d) · %s [%s; %s]' % (f2(x['inz']['m'], sign=True), x['inz']['n'], f2(x['out']['m'], sign=True),
                                                             x['out']['n'], f2(x['d'], sign=True), f2(x['dband'][1], sign=True), f2(x['dband'][2], sign=True)))
        L.append('| %s | %s |' % (TEN[s], ' | '.join(cells)))
    L += ['']
    L += ['### 2.2 Công suất thống kê (khả năng phát hiện) — đọc trước khi tin bất kỳ con số nào ở trên', '',
          'Hiệu nhỏ nhất phát hiện được với xác suất 80% (mức 5%, hai phía) ≈ 2,8 × độ lệch chuẩn R × √(1/n_trong + 1/n_ngoài):', '',
          '| Setup | độ lệch chuẩn R | n trong / ngoài | hiệu nhỏ nhất phát hiện được |', '|---|---|---|---|']
    for s in KEYS:
        t = tags[s]
        sd = float(t['r'].std(ddof=1))
        ni, no = int(t['inz'].sum()), int((~t['inz']).sum())
        mde = 2.8 * sd * math.sqrt(1 / max(ni, 1) + 1 / max(no, 1)) if ni and no else np.nan
        L.append('| %s | %.2f | %d / %d | **%s R** |' % (TEN[s], sd, ni, no, f2(mde)))
    L += ['', 'Với A, B, D (n ≈ 10–30) chỉ một chênh lệch rất lớn (≥ 1R) mới thấy được; chênh < ~0,5R là KHÔNG THỂ phát hiện trên 90 ngày.', '']
    # 3. bias
    L += ['## 3. Phép đo B — bias (giá vs VWAP tuần lúc 19:00 VN)', '',
          '### 3.1 Trong các lệnh TẠI vùng VCL: THUẬN vs NGƯỢC bias (gộp)', '',
          '| Setup | THUẬN bias | NGƯỢC bias | chưa có bias | Hiệu thuận − ngược ± sai số | Hiệu khi dời vùng | Phán quyết | Bối cảnh: MỌI lệnh, thuận / ngược |',
          '|---|---|---|---|---|---|---|---|']
    for s in KEYS:
        x = RB[s]['GỘP']
        L.append('| %s | %s | %s | %d | **%s** ± %s | %s | %s | %s / %s |' % (
            TEN[s], scell(x['th']), scell(x['ng']), x['na'], f2(x['d'], sign=True), f2(x['se']), bcell(x['dband']), VB[s],
            f2(x['all_th']['m'], sign=True) + ' (n%d)' % x['all_th']['n'], f2(x['all_ng']['m'], sign=True) + ' (n%d)' % x['all_ng']['n']))
    L += ['', 'TRAIN / TEST (thuận · ngược, R TB và n, lệnh tại vùng):', '', '| Setup | TRAIN | TEST |', '|---|---|---|']
    for s in KEYS:
        L.append('| %s | %s |' % (TEN[s], ' | '.join('%s (n%d) · %s (n%d)' % (f2(RB[s][g]['th']['m'], sign=True), RB[s][g]['th']['n'],
                                                                             f2(RB[s][g]['ng']['m'], sign=True), RB[s][g]['ng']['n']) for g in ('TRAIN', 'TEST'))))
    L += ['', 'Độ nhạy định nghĩa bias (đúng code setup D: dấu ở nến đầu mỗi (phiên, pha)) — lệnh tại vùng, gộp, chỉ báo:', '',
          '| Setup | THUẬN | NGƯỢC | hiệu |', '|---|---|---|---|']
    for s in KEYS:
        x = RBp[s]['GỘP']
        L.append('| %s | %s | %s | %s |' % (TEN[s], scell(x['th']), scell(x['ng']), f2(x['d'], sign=True)))
    L += ['', '### 3.2 "Bias chỉ bằng vùng" — không cần setup: chạm vùng VCL là vào theo vai vùng (hỗ trợ ⇒ MUA)', '',
          '| TP | Thật: lệnh/ngày · %s | TRAIN | TEST | Dời: R TB [5–95] | Dời: lệnh/ngày | Phán quyết |' % 'n · WR · R TB [KTC]',
          '|---|---|---|---|---|---|---|']
    for rr in ANCHOR_RR:
        tr, bd, pdb = ZO[rr]
        r = tr['r'].to_numpy(float)
        a = rstat(r)
        L.append('| %.1fR | %.2f · %s | %s | %s | %s | %s | %s |' % (
            rr, len(tr) / D.days, scell(a), scell(rstat(r[(tr['split'] == 'TRAIN').to_numpy()])), scell(rstat(r[(tr['split'] == 'TEST').to_numpy()])),
            bcell(bd['GỘP']), '%.2f [%.2f; %.2f]' % pdb, VZO[rr]))
    L += ['']
    # 4. neo
    L += ['## 4. Phép đo C — "đặt setup vào vùng": neo SL/TP theo vùng VCL', '',
          'Cùng tín hiệu tại vùng; SL = biên xa vùng ± 0,5 giá (bỏ nếu > 4 giá); so với R GỐC của chính các lệnh đó (hiệu theo cặp) và với neo theo vùng dời.', '',
          '| Setup | TP | n (bỏ vì SL > 4) | SL TB (giá) | R neo: WR · R TB [KTC] | R gốc cùng lệnh | Hiệu neo − gốc [KTC theo cặp] | Neo theo vùng DỜI | Phán quyết |',
          '|---|---|---|---|---|---|---|---|---|']
    for s in KEYS:
        for rr in ANCHOR_RR:
            ta, bands, v, cmp, nd = RC[s][rr]
            if not len(ta):
                L.append('| %s | %.1fR | 0 (%d) | — | — | — | — | %s | %s |' % (TEN[s], rr, nd, bcell(bands['GỘP']), v))
                continue
            a = rstat(ta['r'].to_numpy(float))
            g = rstat(ta['r_goc'].to_numpy(float))
            dd = rstat(ta['r'].to_numpy(float) - ta['r_goc'].to_numpy(float))
            L.append('| %s | %.1fR | %d (%d) | %.2f | %s | %s | %s [%s; %s] | %s | %s |' % (
                TEN[s], rr, a['n'], nd, float(ta['risk_pts'].mean()), scell(a), f2(g['m'], sign=True), f2(dd['m'], sign=True),
                f2(dd['lo'], sign=True), f2(dd['hi'], sign=True), bcell(bands['GỘP']), v))
    L += ['', 'TRAIN / TEST (R neo · n):', '', '| Setup | TP | TRAIN | TEST |', '|---|---|---|---|']
    for s in KEYS:
        for rr in ANCHOR_RR:
            ta = RC[s][rr][0]
            if not len(ta):
                continue
            r = ta['r'].to_numpy(float)
            L.append('| %s | %.1fR | %s | %s |' % (TEN[s], rr, scell(rstat(r[(ta['split'] == 'TRAIN').to_numpy()])),
                                                  scell(rstat(r[(ta['split'] == 'TEST').to_numpy()]))))
    L += ['']
    # 5. số lệnh
    L += ['## 5. Phép đo D — SỐ LỆNH', '',
          '### 5.1 Lọc theo vùng chỉ có thể GIẢM số lệnh', '',
          '| Setup | Gốc: lệnh/ngày · R TB | Chỉ vào tại vùng VCL (lọc tín hiệu thô rồi mô phỏng): lệnh/ngày · %s | Tại vùng DỜI: lệnh/ngày · R TB [5–95] | Phán quyết |' % 'n · WR · R TB [KTC]',
          '|---|---|---|---|---|']
    tot0 = tot1 = 0
    for s in SETUPS:
        o = RD[s]
        a0, a1 = rstat(rarr(o['orig'])), rstat(rarr(o['filt']))
        tot0 += a0['n']
        tot1 += a1['n']
        L.append('| %s | %.2f · %s | %.2f · %s | %.2f · %s | %s |' % (TEN[s], a0['n'] / D.days, f2(a0['m'], sign=True), a1['n'] / D.days, scell(a1),
                                                          o['shift_pday']['filt'][0], bcell(o['shift_r']['filt']['GỘP']), o['v_filt']))
    L += ['| **Cộng 4 setup** | **%.2f** | **%.2f** | | |' % (tot0 / D.days, tot1 / D.days), '']
    L += ['### 5.2 Nới cổng chỉ khi tại vùng VCL (vùng thay vai trò cổng) — số lệnh có TĂNG không?', '',
          'Bản nới = ô lỏng nhất của lưới 3×3 đã đăng ký của mỗi setup (không chọn theo kết quả). "Hỗn hợp" = tín hiệu gốc ở mọi nơi + tín hiệu '
          'nới chỉ khi tại vùng (đây là cách duy nhất để vùng làm TĂNG số lệnh mà không bỏ lệnh gốc).', '',
          '| Setup | Cổng được nới | Gốc: lệnh/ngày · R TB | Nới MỌI nơi: lệnh/ngày · R TB | Nới CHỈ tại vùng VCL: lệnh/ngày · %s | Nới tại vùng DỜI: lệnh/ngày · R TB [5–95] | Hỗn hợp: lệnh/ngày · R TB | Hỗn hợp với vùng DỜI: lệnh/ngày · R TB [5–95] | Phán quyết (nới tại VCL vs dời) |' % 'n · WR · R TB [KTC]',
          '|---|---|---|---|---|---|---|---|---|']
    for s in SETUPS:
        o = RD[s]
        a0, al, av, ah = (rstat(rarr(o[k])) for k in ('orig', 'loose_all', 'loose_vcl', 'hyb'))
        L.append('| %s | %s | %.2f · %s | %.2f · %s | %.2f · %s | %.2f · %s | %.2f · %s | %.2f · %s | %s |' % (
            TEN[s], LOOSE_TXT[s], a0['n'] / D.days, f2(a0['m'], sign=True), al['n'] / D.days, f2(al['m'], sign=True),
            av['n'] / D.days, scell(av), o['shift_pday']['loose_vcl'][0], bcell(o['shift_r']['loose_vcl']['GỘP']),
            ah['n'] / D.days, f2(ah['m'], sign=True), o['shift_pday']['hyb'][0], bcell(o['shift_r']['hyb']['GỘP']), o['v_loose_vcl']))
    cat = {k: pd.concat([RD[s][k] for s in SETUPS if len(RD[s][k])], ignore_index=True) for k in ('orig', 'loose_all', 'loose_vcl', 'hyb')}
    cs = {k: rstat(rarr(v)) for k, v in cat.items()}
    L.append('| **Cộng 4 setup** | | **%.2f** · %s | **%.2f** · %s | **%.2f** · %s | %.2f | **%.2f** · %s | %.2f | |' % (
        cs['orig']['n'] / D.days, f2(cs['orig']['m'], sign=True), cs['loose_all']['n'] / D.days, f2(cs['loose_all']['m'], sign=True),
        cs['loose_vcl']['n'] / D.days, scell(cs['loose_vcl']), sum(RD[s]['shift_pday']['loose_vcl'][0] for s in SETUPS),
        cs['hyb']['n'] / D.days, scell(cs['hyb']), sum(RD[s]['shift_pday']['hyb'][0] for s in SETUPS)))
    L += ['', 'Tín hiệu thô (trước luật 1 lệnh mở): ' + '; '.join('%s gốc %d → nới %d' % (s, RD[s]['raw0'], RD[s]['raw1']) for s in SETUPS) + '.', '',
          'Không nới được sạch (ghi rõ, không đo): các luật loại cứng trong code — A: cấm 18:00–19:20 VN, loại hình V; B: loại khi đang phá VA/TREND '
          'cùng chiều; C: chỉ chế độ CÂN BẰNG (không có công tắc); D: bias + chế độ ≠ CÂN BẰNG — đều không có tham số trong `detect`, bỏ chúng '
          'phải sửa logic setup, nằm ngoài phạm vi "không sửa code Benzo".', '']
    L += ['## 6. Hình minh hoạ', '']
    L += ['- %s, phiên %s (%d lệnh tại vùng — phiên NHIỀU lệnh tại vùng nhất của %s, chọn để minh hoạ, KHÔNG phải ca điển hình): '
          '[img/%s](img/%s)' % (sp, sid, n, sp, fn, fn) for sp, sid, fn, n in imgs]
    L += ['']
    return '\n'.join(L)


if __name__ == '__main__':
    main()
