# -*- coding: utf-8 -*-
"""
LẦN CHẠM (episode) cho Vùng Canh Lệnh — đúng đặc tả PLAN-LAN-CHAM.md mục 2.6 + mọi phép đo mục 5.

Một lần chạm = giá tới vùng (râu/"cầu" C₋→nến chạm vùng), NEO lại trong lân cận [lo − E, hi + E] bao nhiêu nến cũng được,
rồi đi chỗ khác: G nến LIÊN TIẾP đóng ngoài lân cận và không nến nào chạm lại vùng ⇒ chốt. Kết cục theo phía thoát cuối so với
phía tới: về phía cũ = ĐẢO CHIỀU, sang phía kia = XUYÊN PHÁ. Hằng số chốt trước (giá USD): τ = 0, E = 2,0, G = 5.

Máy trạng thái (một bản cho Python và C#):
  mỗi nến đóng t, mọi vùng đang hiển thị (lo, hi HIỆN TẠI):
    cham = max(C₋,H) ≥ lo−τ và min(C₋,L) ≤ hi+τ ;  trongLanCan = lo−E ≤ C ≤ hi+E       (C₋ = đóng nến trước cùng phiên, đầu phiên = O)
    NGOAI: cham ⇒ MO(vai = C₋<lo ? KHÁNG CỰ : C₋>hi ? HỖ TRỢ : KHÔNG RÕ, batDau = t), xử lý tiếp nến này như MO
    MO: cham hoặc trongLanCan ⇒ demThoat = 0 ; ngược lại phiaThoat = C>hi ? +1 : −1, demThoat += 1 ; demThoat == G ⇒ CHỐT
  hết phiên / vùng rời bộ: demThoat > 0 ⇒ chốt theo phiaThoat ; demThoat == 0 ⇒ CHƯA RÕ. Hết dữ liệu ⇒ bỏ.
TỰ QUYẾT (ghi trong report): vai KHÔNG RÕ ⇒ kết cục luôn "không rõ phía" kể cả khi chốt do hết phiên/rời bộ (4 nhóm rời nhau,
tổng = 100%); `chot` của ca hết phiên/rời bộ = nến PHÁT HIỆN (nến đầu phiên mới / nến đầu tiên vùng vắng mặt) ⇒ không nhìn trước.

Chạy: python3 lan_cham.py [--tinh-lai]  → report/LAN-CHAM.md + report/lan_cham_episodes.csv.gz
(engine các biến thể được cache ở report/cache_lc/; --tinh-lai = chạy lại engine)
"""
import os, sys, time, math, pickle
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import vcl as V
import vcl3 as V3
import vcl4 as V4
import vcl5 as V5

K = V.K
REPORT = V.REPORT
CACHE = os.path.join(REPORT, 'cache_lc')
TAU, EXIT_E, GAP_G = 0.0, 2.0, 5           # chốt trước khi nhìn TEST (plan mục 2)
REPS, SEED = 50, 20261022
DAO, XUYEN, CHUA_RO, KRP, HDL = 0, 1, 2, 3, 4
KET_TEN = {DAO: 'đảo chiều', XUYEN: 'xuyên phá', CHUA_RO: 'chưa rõ', KRP: 'không rõ phía', HDL: 'hết dữ liệu'}
KC, HT, KR = 0, 1, 2
VAI_TEN = {KC: 'kháng cự', HT: 'hỗ trợ', KR: 'không rõ'}
LD_G, LD_HP, LD_RB, LD_HDL = 0, 1, 2, 3
PHA = ['Á', 'Âu', 'Mỹ']
WBIN_LAB = ['2–3 giá', '3–4 giá', '4–5 giá']
THANG = ['T8', 'T9', 'T10']
MIN_N_TABLE, MIN_N_57 = 100, 40
CHUNK = 40000


def wbin(w):
    """Bin độ rộng (giá): [.., 3) → 0, [3, 4) → 1, [4, ..] → 2. C# dùng đúng công thức này."""
    w = np.asarray(w, float)
    return np.where(w < 3, 0, np.where(w < 4, 1, 2))


# ---------------------------------------------------------------------------------------------
# 1. MÁY TRẠNG THÁI
# ---------------------------------------------------------------------------------------------
def bar_arrays(df):
    O, H, L, C = (df[c].to_numpy(float) for c in ('open', 'high', 'low', 'close'))
    sno = df['session_no'].to_numpy()
    new = np.r_[True, sno[1:] != sno[:-1]]
    Cp = np.where(new, O, np.r_[O[:1], C[:-1]])
    return dict(O=O, H=H, L=L, C=C, Cp=Cp, new=new, sno=sno, n=len(df))


def _ket(vai, phia, dem):
    """Kết cục khi chốt (vector)."""
    dao = ((vai == KC) & (phia == -1)) | ((vai == HT) & (phia == 1))
    k = np.where(dao, DAO, XUYEN)
    k = np.where(dem == 0, CHUA_RO, k)
    return np.where(vai == KR, KRP, k)


def episodes(B, rec, off=None, tau=TAU, E=EXIT_E, G=GAP_G, ext_w=False, trace=False, follow=False):
    """Chạy máy 2.6 trên bộ vùng hiển thị `rec` (cột bar, lo, hi, eid; index 0..nr−1).
    off: (nr, R) dời biên từng dòng cho R bản (None ⇒ R = 1, thật). tau/E/G: số hoặc mảng (R,) (độ nhạy).
    ext_w: biến thể "quãng đi đối xứng" (rủi ro 2): phía đảo phải đi thêm cả độ rộng vùng (lân cận phía tới = biên − E − rộng).
    follow: kiểm tra độ vững — lần chạm đang mở khi vùng rời bộ được theo tiếp với biên cuối (không dùng cho nhãn live).
    Trả (ep DataFrame, r = rec đã sắp theo (eid, bar), trace dict | None). ep.srow/erow = chỉ số dòng trong r."""
    r = rec.sort_values(['eid', 'bar'], kind='stable')
    order = r.index.to_numpy()
    r = r.reset_index(drop=True)
    bar = r['bar'].to_numpy()
    eid = r['eid'].to_numpy()
    lo0, hi0 = r['lo'].to_numpy(float), r['hi'].to_numpy(float)
    nr = len(r)
    off = np.zeros((nr, 1)) if off is None else np.asarray(off)[order]
    R = off.shape[1]
    tau = np.broadcast_to(np.asarray(tau, float), (R,))
    E = np.broadcast_to(np.asarray(E, float), (R,))
    G = np.broadcast_to(np.asarray(G, np.int64), (R,))
    n = B['n']
    newb = B['new'][bar]
    gstart = np.flatnonzero(np.r_[True, eid[1:] != eid[:-1]])
    gend = np.r_[gstart[1:], nr]
    out = {k_: [] for k_ in ('rep', 'eid', 'vai', 'bat_dau', 'srow', 'erow', 'thoat_cuoi', 'chot', 'dwell', 'ket', 'ly_do')}
    reps = np.arange(R)
    if trace:
        assert R == 1
        tr = {k_: np.zeros(nr, np.int64) for k_ in ('ep_open', 'ep_vai', 'dem_thoat', 'n', 'dao', 'xuyen', 'chua_ro', 'khong_ro')}

    def emit(mask, vai, s0, srow, dem, phia, last, lrow, chot, ld, e, hist):
        idx = np.flatnonzero(mask)
        if not len(idx):
            return
        k = _ket(vai[idx], phia[idx], dem[idx])
        if ld == LD_HDL:
            k = np.full(len(idx), HDL)
        d = dem[idx]
        tc = np.where(d > 0, last - d + 1, -1)
        dw = np.where(d > 0, tc - s0[idx], last - s0[idx] + 1)
        out['rep'].append(reps[idx]); out['eid'].append(np.full(len(idx), e)); out['vai'].append(vai[idx].copy())
        out['bat_dau'].append(s0[idx].copy()); out['srow'].append(srow[idx].copy()); out['erow'].append(np.full(len(idx), lrow))
        out['thoat_cuoi'].append(tc); out['chot'].append(np.full(len(idx), chot)); out['dwell'].append(dw)
        out['ket'].append(k); out['ly_do'].append(np.full(len(idx), ld))
        if hist is not None and ld != LD_HDL:                              # lịch sử riêng của eid (chỉ khi trace, R = 1)
            hist[0] += 1
            hist[{DAO: 1, XUYEN: 2, CHUA_RO: 3, KRP: 4}[int(k[0])]] += 1

    ci = 0
    while ci < len(gstart):
        # khối gồm trọn nhóm eid
        cj = ci
        while cj < len(gstart) and gend[cj] - gstart[ci] <= CHUNK:
            cj += 1
        cj = max(cj, ci + 1)
        a0, a1 = gstart[ci], gend[cj - 1]
        sl = slice(a0, a1)
        b = bar[sl]
        lo = lo0[sl, None] + off[sl]
        hi = hi0[sl, None] + off[sl]
        Cp, H, L, C = B['Cp'][b, None], B['H'][b, None], B['L'][b, None], B['C'][b, None]
        cham = (np.maximum(Cp, H) >= lo - tau) & (np.minimum(Cp, L) <= hi + tau)
        inl = (C >= lo - E) & (C <= hi + E)
        if ext_w:
            w = (hi0[sl] - lo0[sl])[:, None]
            inl_kc = (C >= lo - E - w) & (C <= hi + E)
            inl_ht = (C >= lo - E) & (C <= hi + E + w)
        up = C > hi
        vnew = np.where(Cp < lo, KC, np.where(Cp > hi, HT, KR)).astype(np.int8)
        del lo, hi
        for g in range(ci, cj):
            a, z = gstart[g], gend[g]
            e = int(eid[a])
            op = np.zeros(R, bool)
            vai = np.zeros(R, np.int8)
            s0 = np.zeros(R, np.int64)
            srow = np.zeros(R, np.int64)
            dem = np.zeros(R, np.int64)
            phia = np.zeros(R, np.int8)
            hist = [0, 0, 0, 0, 0] if trace else None
            for j in range(a, z):
                jj = j - a0
                t = int(bar[j])
                if j > a and newb[j] and op.any():                        # hết phiên (phát hiện ở nến đầu phiên mới)
                    emit(op, vai, s0, srow, dem, phia, t - 1, j - 1, t, LD_HP, e, hist)
                    op[:] = False
                m = cham[jj] & ~op
                if m.any():
                    op |= m
                    vai[m] = vnew[jj][m]
                    s0[m] = t
                    srow[m] = j
                    dem[m] = 0
                    phia[m] = 0
                if op.any():
                    if ext_w:
                        anc = cham[jj] | np.where(vai == KC, inl_kc[jj], np.where(vai == HT, inl_ht[jj], inl[jj]))
                    else:
                        anc = cham[jj] | inl[jj]
                    dem = np.where(anc | ~op, 0, dem + 1)
                    phia = np.where(anc | ~op, 0, np.where(up[jj], 1, -1)).astype(np.int8)
                    c = op & (dem >= G)
                    if c.any():
                        emit(c, vai, s0, srow, dem, phia, t, j, t, LD_G, e, hist)
                        op &= ~c
                        dem[c] = 0
                        phia[c] = 0
                if trace:
                    tr['ep_open'][j] = int(op[0]); tr['ep_vai'][j] = int(vai[0]) if op[0] else -1; tr['dem_thoat'][j] = int(dem[0])
                    tr['n'][j], tr['dao'][j], tr['xuyen'][j], tr['chua_ro'][j], tr['khong_ro'][j] = hist
            last = int(bar[z - 1])
            if op.any() and follow and last < n - 1:
                # KIỂM TRA ĐỘ VỮNG (không phải định nghĩa live): vùng rời bộ khi lần chạm đang mở ⇒ đi tiếp với biên CUỐI CÙNG
                # (đóng băng) tới khi chốt G hoặc hết phiên; không mở lần chạm mới.
                lf, hf = lo0[z - 1] + off[z - 1], hi0[z - 1] + off[z - 1]
                t = last + 1
                while op.any() and t < n:
                    if B['new'][t]:
                        emit(op, vai, s0, srow, dem, phia, t - 1, z - 1, t, LD_HP, e, None)
                        op[:] = False
                        break
                    cp_, h_, l_, c_ = B['Cp'][t], B['H'][t], B['L'][t], B['C'][t]
                    anc = ((max(cp_, h_) >= lf - tau) & (min(cp_, l_) <= hf + tau)) | ((c_ >= lf - E) & (c_ <= hf + E))
                    dem = np.where(anc | ~op, 0, dem + 1)
                    phia = np.where(anc | ~op, 0, np.where(c_ > hf, 1, -1)).astype(np.int8)
                    c = op & (dem >= G)
                    if c.any():
                        emit(c, vai, s0, srow, dem, phia, t, z - 1, t, LD_G, e, None)
                        op &= ~c
                    t += 1
                if op.any():
                    emit(op, vai, s0, srow, dem, phia, n - 1, z - 1, -1, LD_HDL, e, None)
                    op[:] = False
            if op.any():
                if last < n - 1:                                            # vùng rời bộ (phát hiện ở nến last+1)
                    emit(op, vai, s0, srow, dem, phia, last, z - 1, last + 1, LD_RB, e, None)
                else:
                    emit(op, vai, s0, srow, dem, phia, last, z - 1, -1, LD_HDL, e, None)
        ci = cj
    cols = {k_: (np.concatenate(v) if v else np.zeros(0, np.int64)) for k_, v in out.items()}
    ep = pd.DataFrame(cols)
    return ep, r, (tr if trace else None)


# ---------------------------------------------------------------------------------------------
# 2. LÀM GIÀU + ĐỐI CHỨNG
# ---------------------------------------------------------------------------------------------
def enrich(ep, ctx, r, off=None):
    """Thêm pha/tháng/split/đo được/rộng/điểm/k/lịch sử trước. Bỏ ca hết dữ liệu khỏi phép đo (meas=False)."""
    df, st = ctx['df'], ctx['st']
    sno = df['session_no'].to_numpy()
    sm = df['sm'].to_numpy()
    s = sno[ep['bat_dau'].to_numpy()]
    ep['sno'] = s
    ep['pha'] = V3.phase_of(sm[ep['bat_dau'].to_numpy()])
    ep['split'] = st['split'].to_numpy()[s]
    ep['thang'] = st['thang'].to_numpy()[s]
    ep['meas'] = ctx['meas'][s] & (ep['ket'].to_numpy() != HDL)
    sr = ep['srow'].to_numpy()
    w = (r['hi'].to_numpy() - r['lo'].to_numpy())[sr]
    ep['w_gia'] = w
    ep['wbin'] = wbin(w)
    ep['score'] = r['score'].to_numpy()[sr]
    # ca hết dữ liệu luôn là ca cuối của eid (chot = −1 sắp đầu ⇒ đẩy xuống cuối)
    ep['_o'] = np.where(ep['ket'].to_numpy() == HDL, np.iinfo(np.int64).max, ep['chot'].to_numpy())
    ep = ep.sort_values(['rep', 'eid', '_o', 'bat_dau'], kind='stable').drop(columns='_o').reset_index(drop=True)
    g = ep.groupby(['rep', 'eid'], sort=False)
    ep['k'] = g.cumcount() + 1                                   # lần chạm thứ k của vùng (theo thứ tự chốt)
    nd = (ep['ket'].to_numpy() != DAO).astype(np.int64)
    ep['_nd'] = nd
    ep['n_khong_dao_truoc'] = ep.groupby(['rep', 'eid'], sort=False)['_nd'].cumsum().to_numpy() - nd
    ep['ket_truoc'] = g['ket'].shift(1).fillna(-1).astype(int)
    ep = ep.drop(columns='_nd')
    ep.loc[ep['ket'] == HDL, 'k'] = -1
    return ep


def offsets_d1(ctx, r_rec, reps=REPS, seed=SEED):
    """Đ1 — dời NGUYÊN bộ vùng của mỗi phiên cùng δ, |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, cố định trong phiên (MAP15)."""
    sno = ctx['df']['session_no'].to_numpy()
    nS = int(sno.max()) + 1
    rng = np.random.default_rng(seed)
    d = rng.uniform(3, 15, (nS, reps)) * rng.choice([-1.0, 1.0], (nS, reps))
    return d[sno[r_rec['bar'].to_numpy()]]


def offsets_d2(ctx, r_rec, reps=REPS, seed=SEED + 1):
    """Đ2 — vùng giả cùng độ rộng, tâm ~ U[đáy phiên trước − 2, đỉnh phiên trước + 2], cố định suốt đời vùng (eid)."""
    df, st = ctx['df'], ctx['st']
    H, L = df['high'].to_numpy(float), df['low'].to_numpy(float)
    sno = df['session_no'].to_numpy()
    s_start, s_end = st['start_pos'].to_numpy(), st['end_pos'].to_numpy()
    rng = np.random.default_rng(seed)
    first = r_rec.sort_values(['eid', 'bar']).groupby('eid').head(1)
    offe = {}
    for e, b0, lo, hi in zip(first['eid'].to_numpy(), first['bar'].to_numpy(), first['lo'].to_numpy(), first['hi'].to_numpy()):
        s = int(sno[b0])
        if s >= 1:
            pa, pe = s_start[s - 1], s_end[s - 1]
            plo, phi = L[pa:pe + 1].min(), H[pa:pe + 1].max()
        else:
            plo, phi = L[s_start[s]:b0 + 1].min(), H[s_start[s]:b0 + 1].max()
        offe[int(e)] = rng.uniform(plo - 2, phi + 2, reps) - (lo + hi) / 2
    return np.stack([offe[int(e)] for e in r_rec['eid'].to_numpy()])


D_BINS = (1, 2, 3, 4, 6, 8, 12)


def zone_cells(ctx, rec, off):
    """Ô cân lại Đ2 cho mỗi (eid, bản): (bin khoảng cách giá đóng → cạnh gần tại nến vùng hiện [bin v3 + 'trong' + '>12'],
    bin rộng). Trả DataFrame eid × rep → cell, nhóm (split, tháng) theo nến đầu."""
    df, st = ctx['df'], ctx['st']
    C = df['close'].to_numpy(float)
    u = K.median_range(df).to_numpy()
    sno = df['session_no'].to_numpy()
    r = rec.sort_values(['eid', 'bar'])
    fi = r.groupby('eid').head(1)
    idx = fi.index.to_numpy()
    b0 = fi['bar'].to_numpy()
    R = off.shape[1]
    lo = fi['lo'].to_numpy()[:, None] + off[idx]
    hi = fi['hi'].to_numpy()[:, None] + off[idx]
    c = C[b0][:, None]
    d = np.where(c < lo, lo - c, np.where(c > hi, c - hi, -1.0)) / u[b0][:, None]
    db = np.where(d < 0, 0, 1 + np.digitize(d, D_BINS, right=True))          # 0 trong, 1 ≤1, …, 7 (8,12], 8 > 12
    wb = wbin(fi['hi'].to_numpy() - fi['lo'].to_numpy())
    cell = db * 3 + wb[:, None]
    s = sno[b0]
    return pd.DataFrame(dict(eid=np.repeat(fi['eid'].to_numpy(), R), rep=np.tile(np.arange(R), len(fi)), cell=cell.ravel(),
                             meas=np.repeat(ctx['meas'][s], R), split=np.repeat(st['split'].to_numpy()[s], R),
                             thang=np.repeat(st['thang'].to_numpy()[s], R)))


# ---------------------------------------------------------------------------------------------
# 3. TỈ LỆ, ĐỐI CHỨNG, PHÁN QUYẾT
# ---------------------------------------------------------------------------------------------
def rate(x):
    x = np.asarray(x, float)
    n = len(x)
    if n == 0:
        return np.nan, np.nan, 0
    p = x.mean()
    return p, math.sqrt(max(p * (1 - p), 0) / n), n


def ctrl_rates(ep, x, w=None, reps=REPS):
    """x: bool cần tính tỉ lệ trên các dòng ep (đã lọc); w: trọng số. Trả mảng tỉ lệ theo từng bản (rep 0..reps−1)."""
    rep = ep['rep'].to_numpy()
    w = np.ones(len(ep)) if w is None else w
    num = np.bincount(rep, w * x, minlength=reps)
    den = np.bincount(rep, w, minlength=reps)
    with np.errstate(invalid='ignore', divide='ignore'):
        return num / den


def band(v):
    v = v[~np.isnan(v)]
    if not len(v):
        return (np.nan, np.nan, np.nan)
    return (v.mean(), np.quantile(v, .05), np.quantile(v, .95))


def d2_weights(cells, ep2, group_col=None):
    """Trọng số cân Đ2 theo ô (khoảng cách × rộng) để phân bố ô của vùng GIẢ (gộp 50 bản) khớp vùng THẬT, trong từng nhóm."""
    real = cells[(cells['rep'] == -1) & cells['meas']]
    fake_all = cells[cells['rep'] >= 0]
    fake = fake_all[fake_all['meas']]
    w = np.zeros(len(ep2))
    groups = [None] if group_col is None else sorted(real[group_col].unique())
    key = ep2[['eid', 'rep']].merge(fake_all[['eid', 'rep', 'cell']], on=['eid', 'rep'], how='left')['cell'].to_numpy()
    for gv in groups:
        rr = real if gv is None else real[real[group_col] == gv]
        ff = fake if gv is None else fake[fake[group_col] == gv]
        pr = rr['cell'].value_counts(normalize=True)
        pf = ff['cell'].value_counts(normalize=True)
        ratio = (pr / pf).replace([np.inf], 0).fillna(0)
        sel = np.ones(len(ep2), bool) if gv is None else (ep2[group_col].to_numpy() == gv)
        w[sel] = pd.Series(key[sel]).map(ratio).fillna(0).to_numpy()
    return w


def verdict(cmp):
    """cmp[nhóm] = (p, se, n, mean_ctrl, q5, q95). Ngưỡng CHỐT TRƯỚC (plan mục 5): thật ngoài dải 5–95% của đối chứng ở CẢ TRAIN và TEST,
    cùng dấu, cùng dấu ở ≥ 2/3 tháng, |hiệu| > 2 sai số nhị thức của thật (ở cả TRAIN và TEST). Thiếu một ⇒ '≈ đối chứng'."""
    try:
        tr, te = cmp['TRAIN'], cmp['TEST']
    except KeyError:
        return '—'
    if tr[2] == 0 or te[2] == 0 or np.isnan(tr[3]) or np.isnan(te[3]):
        return '— (thiếu mẫu)'
    out_tr = tr[0] < tr[4] or tr[0] > tr[5]
    out_te = te[0] < te[4] or te[0] > te[5]
    s_tr, s_te = np.sign(tr[0] - tr[3]), np.sign(te[0] - te[3])
    ms = [np.sign(cmp[m][0] - cmp[m][3]) for m in THANG if m in cmp and cmp[m][2] > 0 and not np.isnan(cmp[m][3])]
    same_m = sum(1 for x in ms if x == s_tr) >= 2
    big = abs(tr[0] - tr[3]) > 2 * tr[1] and abs(te[0] - te[3]) > 2 * te[1]
    if out_tr and out_te and s_tr == s_te and same_m and big:
        return 'KHÁC đối chứng ' + ('▲' if s_tr > 0 else '▼')
    miss = []
    if not (out_tr and out_te):
        miss.append('trong dải 5–95%' + (' ở TRAIN' if not out_tr and out_te else ' ở TEST' if out_tr and not out_te else ''))
    if s_tr != s_te:
        miss.append('TRAIN/TEST ngược dấu')
    if not same_m:
        miss.append('< 2/3 tháng cùng dấu')
    if not big:
        miss.append('|hiệu| ≤ 2 sai số')
    return '≈ đối chứng (' + '; '.join(miss) + ')'


GROUPS = [('TRAIN', 'split', 'TRAIN'), ('TEST', 'split', 'TEST'), ('GỘP', None, None),
          ('T8', 'thang', 'T8'), ('T9', 'thang', 'T9'), ('T10', 'thang', 'T10')]


def compare(R_, D1, D2, w2, sel_r, sel_1, sel_2, what):
    """So 1 thước đo (what = mã kết cục) cho các nhóm. sel_* = hàm(df) → bool. w2 = dict nhóm → trọng số Đ2 (theo dòng D2)."""
    res = {}
    for name, col, val in GROUPS:
        mr = sel_r(R_) & (True if col is None else (R_[col] == val).to_numpy())
        p, se, n = rate(R_['ket'].to_numpy()[mr] == what)
        m1 = sel_1(D1) & (True if col is None else (D1[col] == val).to_numpy())
        b1 = band(ctrl_rates(D1[m1], D1['ket'].to_numpy()[m1] == what))
        m2 = sel_2(D2) & (True if col is None else (D2[col] == val).to_numpy())
        b2 = band(ctrl_rates(D2[m2], D2['ket'].to_numpy()[m2] == what, w2[name][m2]))
        res[name] = dict(real=(p, se, n), d1=b1, d2=b2)
    v1 = verdict({k: (*x['real'], *x['d1']) for k, x in res.items()})
    v2 = verdict({k: (*x['real'], *x['d2']) for k, x in res.items()})
    return res, v1, v2


def pc(x):
    return '—' if x is None or (isinstance(x, float) and np.isnan(x)) else f'{100 * x:.1f}'


def fmt_cmp(res, name):
    x = res[name]
    p, se, n = x['real']
    if n == 0:
        return '— (n=0)', '—', '—'
    b1, b2 = x['d1'], x['d2']
    return (f'**{pc(p)}** ±{pc(se)} (n={n})', f'{pc(b1[0])} [{pc(b1[1])}–{pc(b1[2])}]', f'{pc(b2[0])} [{pc(b2[1])}–{pc(b2[2])}]')


# ---------------------------------------------------------------------------------------------
# 4. ENGINE CÁC BIẾN THỂ (song song, cache)
# ---------------------------------------------------------------------------------------------
VARIANTS = {
    'v5': ('90', dict(wmin=2.0, wmax=5.0, chong='giu2')),
    'v4': ('90', None),
    'v5_giua': ('90', dict(wmin=2.0, wmax=5.0, chong='giua')),
    'v5_15_4': ('90', dict(wmin=1.5, wmax=4.0, chong='giu2')),
    'v5_2_6': ('90', dict(wmin=2.0, wmax=6.0, chong='giu2')),
    'v5_29d': ('29', dict(wmin=2.0, wmax=5.0, chong='giu2')),
}


def _run_variant(name):
    src, kw = VARIANTS[name]
    t0 = time.time()
    bars, lv = V5.load(V5.BASE90 if src == '90' else V5.BASE29)
    ctx = V5.prepare(bars, lv)
    cands = V3.gen_candidates(ctx)
    if kw is None:
        r = V4.run_engine(ctx, cands)
        r['kep_tran'] = 0
    else:
        r = V5.run_engine(ctx, cands, **kw)
    res = dict(rec=r['rec'], n_recalc=r['n_recalc'], kep_tran=r['kep_tran'], canh_bao=r.get('canh_bao'), sec=time.time() - t0)
    with open(os.path.join(CACHE, name + '.pkl'), 'wb') as f:
        pickle.dump(res, f)
    return name, res['sec']


def engines(force=False):
    os.makedirs(CACHE, exist_ok=True)
    todo = [k for k in VARIANTS if force or not os.path.exists(os.path.join(CACHE, k + '.pkl'))]
    if todo:
        with ProcessPoolExecutor(max_workers=min(len(todo), 6)) as ex:
            for name, sec in ex.map(_run_variant, todo):
                print(f'engine {name}: {sec:.0f}s', flush=True)
    out = {}
    for k in VARIANTS:
        with open(os.path.join(CACHE, k + '.pkl'), 'rb') as f:
            out[k] = pickle.load(f)
    return out, todo


# ---------------------------------------------------------------------------------------------
# 5. PHÉP ĐO PHỤ
# ---------------------------------------------------------------------------------------------
def old_counts(ctx, B, r, ep):
    """5.2: (a) đếm 'chạm 1 nến' kiểu vcl4 (giá đóng vào vùng từ ngoài, cùng phiên) trên cùng bộ vùng; (b) sự kiện kiểu MAP15
    (vào vùng bằng giá đóng → BẢO VỆ = đóng cách cạnh gần ≥ 2u về phía cũ trước khi đóng xuyên cạnh xa, ≤ 120 nến, trong phiên)."""
    df, st = ctx['df'], ctx['st']
    C = B['C']
    sno = B['sno']
    u = K.median_range(df).to_numpy()
    s_end = st['end_pos'].to_numpy()
    bar = r['bar'].to_numpy()
    lo, hi = r['lo'].to_numpy(), r['hi'].to_numpy()
    eid = r['eid'].to_numpy()
    pb = np.maximum(bar - 1, 0)
    ent = (bar > 0) & (sno[bar] == sno[pb]) & (C[bar] >= lo) & (C[bar] <= hi) & ((C[pb] < lo) | (C[pb] > hi))
    meas_row = ctx['meas'][sno[bar]]
    cum = np.r_[0, np.cumsum(ent)]
    inside = cum[ep['erow'].to_numpy() + 1] - cum[ep['srow'].to_numpy()]
    ev = []
    gstart = np.flatnonzero(np.r_[True, eid[1:] != eid[:-1]])
    gend = np.r_[gstart[1:], len(r)]
    for a, z in zip(gstart, gend):
        last_k = -1
        for j in np.flatnonzero(ent[a:z] & meas_row[a:z]) + a:
            t = int(bar[j])
            if t <= last_k:
                continue
            sd = 1 if C[t - 1] > hi[j] else -1
            l0, h0, uu = lo[j], hi[j], u[t]
            lim = min(t + 1 + 120, int(s_end[sno[t]]) + 1)
            seg = C[t + 1:lim]
            prot = (seg >= h0 + 2 * uu) if sd == 1 else (seg <= l0 - 2 * uu)
            brk = (seg < l0) if sd == 1 else (seg > h0)
            fp = int(np.argmax(prot)) if prot.any() else 10 ** 9
            fb = int(np.argmax(brk)) if brk.any() else 10 ** 9
            if fp == fb == 10 ** 9:
                res, k = np.nan, lim - 1
            else:
                res, k = float(fp < fb), t + 1 + min(fp, fb)
            ev.append((int(eid[j]), t, sd, res, ctx['st']['split'].to_numpy()[sno[t]]))
            last_k = k
    return int((ent & meas_row).sum()), inside, pd.DataFrame(ev, columns=['eid', 'i', 'side', 'bao_ve', 'split'])


def engine_disagree(ctx, B, r, ep):
    """5.1c: luật xuyên của engine ở cấp vùng (giá đóng vượt biên XA ≥ 1u, phía theo vai lần chạm) có xảy ra trong lần chạm không."""
    u = K.median_range(ctx['df']).to_numpy()
    bar = r['bar'].to_numpy()
    lo, hi = r['lo'].to_numpy(), r['hi'].to_numpy()
    C = B['C'][bar]
    cu = np.r_[0, np.cumsum(C > hi + u[bar])]
    cd = np.r_[0, np.cumsum(C < lo - u[bar])]
    s, e = ep['srow'].to_numpy(), ep['erow'].to_numpy() + 1
    vai = ep['vai'].to_numpy()
    return np.where(vai == KC, cu[e] - cu[s] > 0, np.where(vai == HT, cd[e] - cd[s] > 0, False))


def bound_shift(r, ep):
    """Rủi ro 7: tỉ lệ nến (sau nến bắt đầu) của lần chạm đang mở mà biên vùng đổi so với nến trước."""
    lo, hi, eid = r['lo'].to_numpy(), r['hi'].to_numpy(), r['eid'].to_numpy()
    ch = np.r_[False, ((np.abs(np.diff(lo)) > 1e-9) | (np.abs(np.diff(hi)) > 1e-9)) & (eid[1:] == eid[:-1])]
    cum = np.r_[0, np.cumsum(ch)]
    s, e = ep['srow'].to_numpy(), ep['erow'].to_numpy()
    nch = cum[e + 1] - cum[s + 1]
    nrow = e - s
    return nch.sum() / max(nrow.sum(), 1), (nch > 0).mean()


def lost_eid(r, gap=60):
    """Rủi ro 5: % vùng mới (eid mới) có biên chồng lên một vùng vừa rời bộ ≤ 60 nến trước (lịch sử riêng bị reset)."""
    g = r.groupby('eid')
    f = g.head(1).set_index('eid')
    l = g.tail(1).set_index('eid')
    fb, flo, fhi = f['bar'].to_numpy(), f['lo'].to_numpy(), f['hi'].to_numpy()
    lb, llo, lhi = l['bar'].to_numpy(), l['lo'].to_numpy(), l['hi'].to_numpy()
    o = np.argsort(lb)
    lb, llo, lhi = lb[o], llo[o], lhi[o]
    hit = 0
    for b0, a, b in zip(fb, flo, fhi):
        i0, i1 = np.searchsorted(lb, b0 - gap), np.searchsorted(lb, b0)
        if i1 > i0 and ((np.minimum(lhi[i0:i1], b) - np.maximum(llo[i0:i1], a)) > 0).any():
            hit += 1
    return hit / max(len(fb), 1), hit, len(fb)


# ---------------------------------------------------------------------------------------------
# 6. MAIN
# ---------------------------------------------------------------------------------------------
def tdisp(ctx, b):
    return str(ctx['df']['t_utc'].iloc[int(b)])[:16]


def main():
    t0 = time.time()
    force = '--tinh-lai' in sys.argv
    ENG, ran = engines(force)
    t_eng = time.time() - t0
    bars, lv = V5.load(V5.BASE90)
    ctx = V5.prepare(bars, lv)
    df, st = ctx['df'], ctx['st']
    B = bar_arrays(df)
    meas = ctx['meas']
    rec = ENG['v5']['rec'].reset_index(drop=True)
    t1 = time.time()
    # ---- thật + 2 đối chứng
    ep_r, r, _ = episodes(B, rec)
    R_ = enrich(ep_r, ctx, r)
    off1 = offsets_d1(ctx, rec)
    off2 = offsets_d2(ctx, rec)
    e1, _, _ = episodes(B, rec, off1)
    D1 = enrich(e1, ctx, r)
    e2, _, _ = episodes(B, rec, off2)
    D2 = enrich(e2, ctx, r)
    t_ep = time.time() - t1
    cells = pd.concat([zone_cells(ctx, rec, np.zeros((len(rec), 1))).assign(rep=-1), zone_cells(ctx, rec, off2)], ignore_index=True)
    Rm, D1m, D2m = R_[R_['meas']].reset_index(drop=True), D1[D1['meas']].reset_index(drop=True), D2[D2['meas']].reset_index(drop=True)
    w2 = {'GỘP': d2_weights(cells, D2m)}
    wsp, wth = d2_weights(cells, D2m, 'split'), d2_weights(cells, D2m, 'thang')
    for nm in ('TRAIN', 'TEST'):
        w2[nm] = wsp
    for nm in THANG:
        w2[nm] = wth
    cover = (w2['GỘP'] > 0).mean()
    ALL = lambda d: np.ones(len(d), bool)
    os.makedirs(REPORT, exist_ok=True)
    out = R_.copy()
    out['t_bat_dau_utc'] = df['t_utc'].to_numpy()[out['bat_dau'].to_numpy()]
    out['session_id'] = st['session_id'].to_numpy()[out['sno'].to_numpy()]
    out['ket_ten'] = out['ket'].map(KET_TEN)
    out['vai_ten'] = out['vai'].map(VAI_TEN)
    out.drop(columns=['rep']).to_csv(os.path.join(REPORT, 'lan_cham_episodes.csv.gz'), index=False)

    sid = st['session_id']
    flag = [f"{sid.iloc[s]} ({'phiên 0' if s == 0 else ''}{'thin' if st['thin'].iloc[s] else ''}{' splice' if st['splice'].iloc[s] else ''})"
            for s in range(len(st)) if not meas[s]]
    ntr = int((meas & (st['split'] == 'TRAIN').to_numpy()).sum())
    nte = int((meas & (st['split'] == 'TEST').to_numpy()).sum())
    md = ['# Lần chạm (neo nhiều nến) + độ rộng vùng [2, 5] giá — Vùng Canh Lệnh v5', '',
          f'Đặc tả: `PLAN-LAN-CHAM.md`. Dữ liệu chính: `fp_GCZ26_XCEC_Time_20260723-20261021_90d` ({len(df)} nến M1, {len(st)} phiên, giờ UTC, '
          'một hợp đồng GCZ26).',
          f'**Phiên bị loại ({len(flag)}):** ' + ', '.join(flag) + f'. Cờ splice: {int(st["splice"].sum())} phiên (không có chỗ nối). '
          f'**Còn {int(meas.sum())} phiên đo**: TRAIN {ntr} ({sid[(meas & (st["split"] == "TRAIN").to_numpy())].iloc[0]} → '
          f'{sid[(meas & (st["split"] == "TRAIN").to_numpy())].iloc[-1]}), TEST {nte} ({sid[(meas & (st["split"] == "TEST").to_numpy())].iloc[0]} → '
          f'{sid.iloc[-1]}, phiên cuối chưa trọn {int(st["n"].iloc[-1])} nến). Tháng: T8 gồm 3 phiên cuối tháng 7 (07-29…07-31).',
          f'Hằng số chốt TRƯỚC khi nhìn TEST: τ = {TAU} · E = {EXIT_E} giá · G = {GAP_G} nến; vùng [2, 5] giá. Đối chứng {REPS} bản mỗi loại.',
          '**Ngưỡng "khác đối chứng" (chốt trước, plan mục 5):** thật nằm NGOÀI dải 5–95% của đối chứng ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở '
          '≥ 2/3 tháng, VÀ |hiệu| > 2 sai số nhị thức của thật ở cả TRAIN và TEST. Thiếu một điều kiện ⇒ "≈ đối chứng".',
          'Đ1 = dời nguyên bộ vùng của phiên 3–15 giá (dấu ngẫu nhiên, cố định trong phiên). Đ2 = vùng giả cùng độ rộng, tâm ngẫu nhiên trong '
          f'biên phiên trước ±2 giá, cân lại theo ô (khoảng cách giá đóng → cạnh gần lúc vùng hiện × bin rộng); {100 * cover:.0f}% lần chạm giả rơi vào ô có vùng thật.',
          f'Thời gian chạy: engine {t_eng:.0f}s ({"chạy lại " + ", ".join(ran) if ran else "đọc cache"}), máy trạng thái thật + 2×50 đối chứng {t_ep:.0f}s.', '']

    # ======== BẢNG CHÍNH
    md += ['## A. Kết quả chính — % đảo chiều / % xuyên phá: thật vs đối chứng', '',
           'Mẫu số = mọi lần chạm đã chốt (đảo + xuyên + chưa rõ + không rõ phía = 100%). Thật: % ± sai số nhị thức (n). Đối chứng: trung bình '
           '[5%–95%] của 50 bản. Sai số nhị thức đánh giá THẤP vì nhiều lần chạm cùng một vùng.', '']
    VERD = {}
    for what, nm in ((DAO, 'ĐẢO CHIỀU'), (XUYEN, 'XUYÊN PHÁ')):
        res, v1, v2 = compare(Rm, D1m, D2m, w2, ALL, ALL, ALL, what)
        VERD[what] = (res, v1, v2)
        md += [f'### % {nm}', '', '| Nhóm | Thật | Đ1 dời bản đồ | Đ2 khớp khoảng cách × rộng |', '|---|---|---|---|']
        for name, _, _ in GROUPS:
            md.append(f'| {name} | ' + ' | '.join(fmt_cmp(res, name)) + ' |')
        md += ['', f'- So Đ1: **{v1}**', f'- So Đ2: **{v2}**', '']
    # theo bin rộng
    md += ['### Theo độ rộng vùng (hình học: vùng hẹp ⇒ xuyên dễ hơn)', '',
           '| Rộng | Kết cục | Thật GỘP | Đ1 GỘP | Đ2 GỘP | phán quyết Đ1 | phán quyết Đ2 |', '|---|---|---|---|---|---|---|']
    BINRES = {}
    for b in range(3):
        sb = lambda d, b=b: (d['wbin'] == b).to_numpy()
        for what, nm in ((DAO, 'đảo'), (XUYEN, 'xuyên')):
            res, v1, v2 = compare(Rm, D1m, D2m, w2, sb, sb, sb, what)
            BINRES[(b, what)] = res
            a, c1, c2 = fmt_cmp(res, 'GỘP')
            md.append(f'| {WBIN_LAB[b]} | {nm} | {a} | {c1} | {c2} | {v1} | {v2} |')
    md.append('')

    # ======== A2 — kiểm tra độ vững (thêm SAU khi thấy kết quả)
    def lydo_tab(d):
        k, l_ = d['ket'].to_numpy(), d['ly_do'].to_numpy()
        reps = max(d['rep'].nunique(), 1)
        return (len(d) / reps, 100 * ((k == CHUA_RO) & (l_ == LD_RB)).mean(), 100 * ((k == CHUA_RO) & (l_ == LD_HP)).mean(),
                100 * ((k == XUYEN) & (l_ == LD_G)).mean(), 100 * ((k == XUYEN) & (l_ != LD_G)).mean())
    md += ['## A2. Kiểm tra độ vững — THÊM SAU khi thấy kết quả (không đăng ký trước)', '',
           'Vì sao: "chưa rõ" của vùng thật cao hơn hẳn đối chứng. Gần hết "chưa rõ" là **vùng rời bộ hiển thị khi giá còn neo ở đó**. Vùng thật '
           'bị engine bỏ/dựng lại đúng lúc giá đang ở nó (mốc chết khi bị chạm/xuyên, vùng đổi hình — xem ngay dưới bảng); vùng giả (dời) sống đúng '
           'chừng ấy nến nhưng giá không "đụng" vào cơ chế sống/chết của nó. Nếu phần bị cắt nghiêng về '
           'ca sắp xuyên thì % xuyên thật thấp hơn đối chứng là **do cơ chế hiển thị**, không phải vì vùng giữ giá tốt hơn — (ii) dưới đây kiểm điều đó.', '',
           '| Bộ | lần chạm / bản | chưa rõ do rời bộ % | chưa rõ do hết phiên % | xuyên chốt tự nhiên % | xuyên chốt do rời bộ/hết phiên % |',
           '|---|---|---|---|---|---|']
    for nm_, d_ in (('Thật', Rm), ('Đ1', D1m), ('Đ2 (chưa cân)', D2m)):
        x = lydo_tab(d_)
        md.append(f'| {nm_} | {x[0]:.0f} | {x[1]:.1f} | {x[2]:.1f} | {x[3]:.1f} | {x[4]:.1f} |')
    # bằng chứng cơ chế: lần chạm thật "chưa rõ do rời bộ" — ở nến vùng biến mất, có vùng hiển thị MỚI chồng lên chỗ cũ không?
    cr_rb = Rm[(Rm['ket'] == CHUA_RO) & (Rm['ly_do'] == LD_RB)]
    byb = {b_: g_ for b_, g_ in rec.groupby('bar')}
    lo_e, hi_e = r['lo'].to_numpy()[cr_rb['erow'].to_numpy()], r['hi'].to_numpy()[cr_rb['erow'].to_numpy()]
    repl = 0
    for cb_, a_, h_ in zip(cr_rb['chot'].to_numpy(), lo_e, hi_e):
        g_ = byb.get(int(cb_))
        if g_ is not None and ((np.minimum(g_['hi'].to_numpy(), h_) - np.maximum(g_['lo'].to_numpy(), a_)) > 0).any():
            repl += 1
    mk_ = r['mask'].to_numpy()[Rm['srow'].to_numpy()]
    konly = Rm['ket'].to_numpy() == CHUA_RO
    donly = mk_ == 8
    md += ['', f'Cơ chế: trong {len(cr_rb)} lần chạm thật "chưa rõ do rời bộ", chỉ **{100 * repl / max(len(cr_rb), 1):.0f}%** có một vùng hiển thị MỚI '
           '(mã khác) chồng lên chỗ cũ ngay nến vùng cũ biến mất (vùng bị dựng lại thành mã mới); phần lớn còn lại vùng biến mất hẳn khỏi bộ. '
           f'Vùng CHỈ có số tròn (mốc không bao giờ chết) có "chưa rõ" **{100 * konly[donly].mean():.0f}%**, vùng có swing/mốc phiên (mốc chết khi bị '
           f'xuyên 2 lần, POC trần chết khi bị chạm, mốc phiên hết hạn) **{100 * konly[~donly].mean():.0f}%** ⇒ khớp giả thuyết "mốc chết/đổi đúng '
           'lúc giá đang ở vùng". Chưa tách riêng từng nguyên nhân.']
    md += ['', '**(i) % đảo chiều trong các lần đã phân loại** = đảo / (đảo + xuyên) — bỏ "chưa rõ" và "không rõ phía" ở cả hai bên:', '',
           '| Nhóm | Thật | Đ1 | Đ2 |', '|---|---|---|---|']
    CL = lambda d: np.isin(d['ket'].to_numpy(), (DAO, XUYEN))
    res, v1, v2 = compare(Rm, D1m, D2m, w2, CL, CL, CL, DAO)
    for name, _, _ in GROUPS:
        md.append(f'| {name} | ' + ' | '.join(fmt_cmp(res, name)) + ' |')
    md += ['', f'- So Đ1: **{v1}** · So Đ2: **{v2}**.',
           '- Lưu ý: số đo (i) vẫn THIÊN về vùng thật — chính các lần xuyên bị cắt thành "chưa rõ" (bảng trên: xuyên chốt do rời bộ thật thấp hơn '
           'đối chứng), nên bỏ "chưa rõ" vẫn để lại mẫu ít xuyên hơn.', '']
    # (ii) theo tiếp khi vùng rời bộ
    ef, rf, _ = episodes(B, rec, follow=True)
    Rf = enrich(ef, ctx, rf)
    Rf = Rf[Rf['meas']].reset_index(drop=True)
    ef1, _, _ = episodes(B, rec, off1, follow=True)
    D1f = enrich(ef1, ctx, rf)
    D1f = D1f[D1f['meas']].reset_index(drop=True)
    ef2, _, _ = episodes(B, rec, off2, follow=True)
    D2f = enrich(ef2, ctx, rf)
    D2f = D2f[D2f['meas']].reset_index(drop=True)
    w2f = {'GỘP': d2_weights(cells, D2f)}
    wspf, wthf = d2_weights(cells, D2f, 'split'), d2_weights(cells, D2f, 'thang')
    for nm_ in ('TRAIN', 'TEST'):
        w2f[nm_] = wspf
    for nm_ in THANG:
        w2f[nm_] = wthf
    md += ['**(ii) Theo tiếp lần chạm khi vùng rời bộ** (biên đóng băng ở nến cuối vùng còn hiển thị, tới khi 5 nến yên hoặc hết phiên) — áp y hệt '
           'cho thật và đối chứng, cắt đứt ảnh hưởng của cơ chế chọn bộ lên kết cục:', '',
           '| Kết cục | Nhóm | Thật | Đ1 | Đ2 |', '|---|---|---|---|---|']
    FOLLOW = {}
    for what, nm_ in ((DAO, 'đảo'), (XUYEN, 'xuyên'), (CHUA_RO, 'chưa rõ')):
        res, v1, v2 = compare(Rf, D1f, D2f, w2f, ALL, ALL, ALL, what)
        FOLLOW[what] = (res, v1, v2)
        for name in ('TRAIN', 'TEST', 'GỘP'):
            md.append(f'| {nm_} | {name} | ' + ' | '.join(fmt_cmp(res, name)) + ' |')
    md += ['', f"- % đảo: Đ1 **{FOLLOW[DAO][1]}** · Đ2 **{FOLLOW[DAO][2]}**",
           f"- % xuyên: Đ1 **{FOLLOW[XUYEN][1]}** · Đ2 **{FOLLOW[XUYEN][2]}**", '']

    # ======== 5.1a
    md += ['## B. Đếm theo định nghĩa mới (5.1a)', '']
    nz = R_.groupby('eid').size()
    zon = r.groupby('eid')['bar'].min()
    zmeas = zon[meas[B['sno'][zon.to_numpy()]]].index
    cnt = Rm.groupby('eid').size().reindex(zmeas, fill_value=0)
    dist = [(cnt == k).mean() for k in (0, 1, 2, 3)] + [(cnt >= 4).mean()]
    dw = Rm['dwell'].to_numpy()
    md += [f'- Lần chạm đã chốt (phiên đo): **{len(Rm)}** (TRAIN {int((Rm["split"] == "TRAIN").sum())}, TEST {int((Rm["split"] == "TEST").sum())}); '
           f'≈ {len(Rm) / meas.sum():.0f} lần/phiên. Bỏ {int((R_["ket"] == HDL).sum())} ca hết dữ liệu.',
           f'- Vùng hiển thị (mã vùng mới trong phiên đo): {len(zmeas)}. Số lần chạm mỗi vùng: 0 → {100 * dist[0]:.0f}% · 1 → {100 * dist[1]:.0f}% · '
           f'2 → {100 * dist[2]:.0f}% · 3 → {100 * dist[3]:.0f}% · ≥4 → {100 * dist[4]:.0f}%.',
           f'- Số nến neo (từ nến bắt đầu tới nến thoát cuối): p50 **{np.quantile(dw, .5):.0f}** · p85 {np.quantile(dw, .85):.0f} · '
           f'p95 {np.quantile(dw, .95):.0f} · > 120 nến {100 * (dw > 120).mean():.1f}%. Lần chạm chỉ 1 nến (râu quét rồi đi): {100 * (dw == 1).mean():.0f}%.', '',
           '| Nhóm | n | đảo % | xuyên % | chưa rõ % | không rõ phía % |', '|---|---|---|---|---|---|']

    def brk(d):
        k = d['ket'].to_numpy()
        return f'{len(d)} | ' + ' | '.join(f'{100 * (k == x).mean():.1f}' for x in (DAO, XUYEN, CHUA_RO, KRP))
    rows = [('GỘP', Rm)] + [(n_, Rm[Rm['split'] == n_]) for n_ in ('TRAIN', 'TEST')] + [(m, Rm[Rm['thang'] == m]) for m in THANG] + \
           [('vai kháng cự (tới từ dưới)', Rm[Rm['vai'] == KC]), ('vai hỗ trợ (tới từ trên)', Rm[Rm['vai'] == HT])] + \
           [(f'pha {PHA[p]}', Rm[Rm['pha'] == p]) for p in range(3)] + [(f'rộng {WBIN_LAB[b]}', Rm[Rm['wbin'] == b]) for b in range(3)]
    for nm, d in rows:
        md.append(f'| {nm} | {brk(d)} |')
    md += ['', '### Bảng toàn cục pha × độ rộng (GỘP TRAIN+TEST) — số hiện trên nhãn', '',
           '| Pha | Rộng | n | đảo % | xuyên % | chưa rõ % | không rõ phía % |', '|---|---|---|---|---|---|---|']
    EP = np.full((3, 3, 3), -1, int)
    EPA = np.full((3, 3), -1, int)
    for b in range(3):
        d = Rm[Rm['wbin'] == b]
        k = d['ket'].to_numpy()
        if len(d) >= MIN_N_TABLE:
            EPA[b] = [int(round(100 * (k == x).mean())) for x in (DAO, XUYEN, CHUA_RO)]
        for p in range(3):
            dd = d[d['pha'] == p]
            kk = dd['ket'].to_numpy()
            if len(dd) >= MIN_N_TABLE:
                EP[p, b] = [int(round(100 * (kk == x).mean())) for x in (DAO, XUYEN, CHUA_RO)]
            md.append(f'| {PHA[p]} | {WBIN_LAB[b]} | {brk(dd)} |' + ('' if len(dd) >= MIN_N_TABLE else ' (n < 100 ⇒ dùng "mọi pha")'))
        md.append(f'| mọi pha | {WBIN_LAB[b]} | {brk(d)} |')
    md += ['', 'Nhúng C# (`VclTables.Episode[pha, bin rộng, {đảo, xuyên, chưa rõ}]`, % nguyên; −1 = n < 100 ⇒ dùng `EpisodeAll`):', '', '```csharp',
           'public static readonly int[,,] Episode = {']
    for p in range(3):
        md.append('    { ' + ', '.join('{ ' + ', '.join(str(x) for x in EP[p, b]) + ' }' for b in range(3)) + ' }' + (',' if p < 2 else ''))
    md += ['};', 'public static readonly int[,] EpisodeAll = { ' + ', '.join('{ ' + ', '.join(str(x) for x in EPA[b]) + ' }' for b in range(3)) + ' };',
           '```', '']
    np.savez(os.path.join(REPORT, 'lan_cham_tables.npz'), ep=EP, epa=EPA)

    # ======== 5.1b độ rộng + vệ sinh + sàn/trần
    md += ['## C. Độ rộng vùng và vệ sinh chart (5.1b)', '',
           'Đo trên mọi dòng (vùng × nến) hiển thị ở phiên đo. v5 = chốt (chồng lấn: giữ ≥ 2 giá); v5 "cắt giữa" = làm đúng chữ plan '
           '(chồng lấn cắt ở giữa như v4) — chỉ để thấy vì sao tự quyết.', '',
           '| Chỉ số | v4 (kẹp [1u,4u]) | v5 cắt giữa | **v5 chốt** | v5 sàn/trần 1,5–4 | v5 2–6 |', '|---|---|---|---|---|---|']
    HY = {k: V5.hygiene(ctx, ENG[k]['rec']) for k in ('v4', 'v5_giua', 'v5', 'v5_15_4', 'v5_2_6')}
    for lab, k, f in (('vùng hiển thị TB', 'cnt', '{:.2f}'), ('rộng trung vị (giá)', 'w_med', '{:.2f}'), ('rộng p90 (giá)', 'w_p90', '{:.2f}'),
                      ('% vùng > 4 giá', 'w_gt4', 'pct'), ('% vùng > 5 giá', 'w_gt5', 'pct'), ('% vùng = 2 giá (do nới)', 'w_eq2', 'pct'),
                      ('% vùng < 2 giá', 'w_lt2', 'pct'), ('% nến đóng trong vùng', 'inside', 'pct'), ('đổi vùng / giờ', 'chg', '{:.2f}'),
                      ('tuổi thọ trung vị (phút)', 'life', '{:.0f}')):
        cells_ = []
        for kk in ('v4', 'v5_giua', 'v5', 'v5_15_4', 'v5_2_6'):
            x = HY[kk]['GỘP'][k]
            cells_.append(f'{100 * x:.1f}' if f == 'pct' else f.format(x))
        md.append(f'| {lab} | ' + ' | '.join(cells_) + ' |')
    md += ['', '| v5 chốt theo tách | vùng TB | rộng TV | % > 4 | đổi/giờ | tuổi thọ |', '|---|---|---|---|---|---|']
    for sp in ('TRAIN', 'TEST'):
        h = HY['v5'][sp]
        md.append(f"| {sp} | {h['cnt']:.2f} | {h['w_med']:.2f} | {100 * h['w_gt4']:.1f} | {h['chg']:.2f} | {h['life']:.0f} |")
    cb = ENG['v5'].get('canh_bao') or {}
    md += ['', f"Ca biên engine v5 (đếm trên MỌI vùng, mọi lần gộp — không chỉ vùng hiển thị): kẹp trần mảnh không tách được (u > 5) "
           f"{ENG['v5']['kep_tran']} lần (u > 5 ở 577 nến = 0,7%, 12 phiên); ứng viên nằm NGOÀI biên vùng của chính nó sau khi dời điểm cắt: "
           f"{cb.get('ngoai_vung', '?')} / {cb.get('ung_vien', '?')} lượt.", '']
    # % đảo trên các biến thể engine
    md += ['### Độ nhạy sàn/trần (chỉ báo, không chọn lại) — % kết cục trên chính bộ vùng của biến thể (GỘP)', '',
           '| Biến thể | n lần chạm | đảo % | xuyên % | chưa rõ % | không rõ phía % | đảo % theo rộng 2–3 / 3–4 / 4–5 |', '|---|---|---|---|---|---|---|']
    VAR_EP = {}
    for kk, nm in (('v4', 'v4 [1u, 4u]'), ('v5_giua', 'v5 cắt giữa'), ('v5', '**v5 chốt 2–5**'), ('v5_15_4', 'v5 1,5–4'), ('v5_2_6', 'v5 2–6')):
        if kk == 'v5':
            d = Rm
        else:
            rr = ENG[kk]['rec'].reset_index(drop=True)
            e_, r_, _ = episodes(B, rr)
            d = enrich(e_, ctx, r_)
            d = d[d['meas']]
        VAR_EP[kk] = d
        bins = ' / '.join(f"{100 * (d[d['wbin'] == b]['ket'] == DAO).mean():.0f}" if (d['wbin'] == b).sum() else '—' for b in range(3))
        md.append(f'| {nm} | {brk(d)} | {bins} |')
    md += ['', 'Ghi chú: v4 có vùng < 2 và > 5 giá; bin 2–3 của v4/1,5–4 gộp cả vùng < 2 giá (bin "< 3").', '']

    # ======== 5.1c
    ex = engine_disagree(ctx, B, r, R_)
    R_['eng_x'] = ex
    Rm2 = R_[R_['meas']]
    k_ = Rm2['ket'].to_numpy()
    cl = (k_ == DAO) | (k_ == XUYEN)
    dis_a = ((k_ == DAO) & Rm2['eng_x'].to_numpy()).sum()
    dis_b = ((k_ == XUYEN) & ~Rm2['eng_x'].to_numpy()).sum()
    dis = (dis_a + dis_b) / max(cl.sum(), 1)
    md += ['## D. Bất đồng với luật xuyên của engine (5.1c)', '',
           'Luật engine (`BREAK_U`): giá đóng vượt biên XA ≥ 1u. Đo ở cấp vùng trong suốt lần chạm (phía theo vai lần chạm).', '',
           f'- Lần chạm ĐẢO mà engine đã coi là xuyên (phá giả ≥ 1u rồi quay về): {dis_a} / {int((k_ == DAO).sum())} = {100 * dis_a / max((k_ == DAO).sum(), 1):.1f}%',
           f'- Lần chạm XUYÊN mà engine chưa coi là xuyên (đi quá biên xa 2 giá nhưng chưa tới 1u, khi u > 2): {dis_b} / {int((k_ == XUYEN).sum())} = '
           f'{100 * dis_b / max((k_ == XUYEN).sum(), 1):.1f}%',
           f'- **Tỉ lệ bất đồng chung: {100 * dis:.1f}%** (ngưỡng plan: > 15% ⇒ đề xuất vòng sau đổi BREAK_U thành 2 giá tuyệt đối).', '']

    # ======== 5.1d đối chiếu file 29 ngày
    rec29 = ENG['v5_29d']['rec'].reset_index(drop=True)
    b29, l29 = V5.load(V5.BASE29)
    ctx29 = V5.prepare(b29, l29)
    B29 = bar_arrays(ctx29['df'])
    e29, r29, _ = episodes(B29, rec29)
    E29 = enrich(e29, ctx29, r29)
    E29 = E29[E29['meas']]
    s29 = set(ctx29['st']['session_id'].to_numpy()[E29['sno'].unique()])
    sid90 = st['session_id'].to_numpy()
    R90 = Rm[np.isin(sid90[Rm['sno'].to_numpy()], list(s29))]
    s29_9 = set(sid90[R90['sno'].unique()])
    E29c = E29[np.isin(ctx29['st']['session_id'].to_numpy()[E29['sno'].to_numpy()], list(s29_9))]
    md += ['## E. Đối chiếu file 29 ngày (5.1d)', '',
           f'Chạy y hệt trên `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h` (engine khởi động lại từ 08-16 nên tuần đầu thiếu ứng viên cũ). '
           f'So trên {len(s29_9)} phiên chung.', '', '| Nguồn | n | đảo % | xuyên % | chưa rõ % | không rõ phía % | nến neo p50 |', '|---|---|---|---|---|---|---|',
           f'| file 90 ngày (các phiên chung) | {brk(R90)} | {np.median(R90["dwell"]):.0f} |',
           f'| file 29 ngày | {brk(E29c)} | {np.median(E29c["dwell"]):.0f} |', '']

    # ======== 5.2 so với đếm 1 nến
    n_old, inside_old, mev = old_counts(ctx, B, r, R_)
    Rmask = R_['meas'].to_numpy()
    io = inside_old[Rmask]
    mv = mev[mev['bao_ve'].notna()]
    md += ['## F. So với cách đếm cũ "chạm = 1 nến" (5.2), trên CÙNG bộ vùng v5', '',
           f'- (a) Kiểu vcl4 (giá đóng vào vùng từ ngoài, mỗi nến tính 1 lần): **{n_old}** lần · cách mới: **{len(Rm)}** lần ⇒ tỉ số cũ/mới = **{n_old / len(Rm):.2f}**.',
           f'- Trung bình mỗi lần chạm mới chứa **{io.mean():.2f}** lần "chạm 1 nến" cũ (p50 {np.median(io):.0f}, p90 {np.quantile(io, .9):.0f}); '
           f'{100 * (io >= 2).mean():.0f}% lần chạm mới bị đếm cũ tính ≥ 2 lần (đúng chỗ người học phản đối); {100 * (io == 0).mean():.0f}% lần chạm mới '
           'cách cũ KHÔNG đếm (râu chạm/nến nhảy qua mà giá đóng không nằm trong vùng).',
           f'- (b) Kiểu MAP15 (vào vùng bằng giá đóng → bảo vệ ≥ 2u trước khi đóng xuyên cạnh xa, ≤ 120 nến): {len(mev)} sự kiện, '
           f'{len(mv)} có kết cục · **% bảo vệ {100 * mv["bao_ve"].mean():.1f}%** (TRAIN {100 * mv[mv["split"] == "TRAIN"]["bao_ve"].mean():.1f} / '
           f'TEST {100 * mv[mv["split"] == "TEST"]["bao_ve"].mean():.1f}) · so với cách mới % đảo **{100 * (Rm["ket"] == DAO).mean():.1f}%**.',
           '  Hai con số KHÔNG cùng thước: MAP15 cần đi 2u (≈ 3,4 giá ở u trung vị) và tính "phá" ngay khi đóng qua cạnh xa 1 tick; cách mới cần đi 2 giá '
           'và chịu được phá giả.', '']

    # ======== 5.3 độ nhạy τ × E × G
    combos = [(ta, ee, gg) for ta in (0.0, 0.5) for ee in (1.0, 2.0, 3.0) for gg in (5, 10, 20)]
    es, _, _ = episodes(B, rec, np.zeros((len(rec), len(combos))), tau=[c[0] for c in combos], E=[c[1] for c in combos], G=[c[2] for c in combos])
    es = es[(es['ket'] != HDL) & meas[B['sno'][es['bat_dau'].to_numpy()]]]
    md += ['## G. Độ nhạy τ × E × G (5.3, GỘP, chỉ thật)', '', '| τ (giá) | E (giá) | G (nến) | n | nến neo p50 | đảo % | xuyên % | chưa rõ % | không rõ phía % |',
           '|---|---|---|---|---|---|---|---|---|']
    base = None
    sens_flag = []
    for ci_, (ta, ee, gg) in enumerate(combos):
        d = es[es['rep'] == ci_]
        k = d['ket'].to_numpy()
        pdao = 100 * (k == DAO).mean()
        if (ta, ee, gg) == (TAU, EXIT_E, GAP_G):
            base = pdao
        b_ = '**' if (ta, ee, gg) == (TAU, EXIT_E, GAP_G) else ''
        md.append(f'| {b_}{ta}{b_} | {b_}{ee}{b_} | {b_}{gg}{b_} | {len(d)} | {np.median(d["dwell"]):.0f} | {pdao:.1f} | {100 * (k == XUYEN).mean():.1f} | '
                  f'{100 * (k == CHUA_RO).mean():.1f} | {100 * (k == KRP).mean():.1f} |')
    for ci_, (ta, ee, gg) in enumerate(combos):
        d = es[es['rep'] == ci_]
        pdao = 100 * (d['ket'] == DAO).mean()
        if abs(pdao - base) > 5:
            sens_flag.append(f'τ={ta}, E={ee}, G={gg}: {pdao:.1f}% (Δ {pdao - base:+.1f})')
    md += ['', '**Tổ hợp làm % đảo lệch > 5 điểm so với chốt:** ' + ('; '.join(sens_flag) if sens_flag else 'không có.'), '']
    # biến thể quãng đi đối xứng (rủi ro 2)
    esym, _, _ = episodes(B, rec, np.hstack([np.zeros((len(rec), 1)), off1]), ext_w=True)
    esym = esym[(esym['ket'] != HDL) & meas[B['sno'][esym['bat_dau'].to_numpy()]]]
    sr_ = esym[esym['rep'] == 0]
    sc_ = esym[esym['rep'] >= 1].copy()
    sc_['rep'] -= 1
    bd = band(ctrl_rates(sc_, sc_['ket'].to_numpy() == DAO))
    bx = band(ctrl_rates(sc_, sc_['ket'].to_numpy() == XUYEN))
    md += ['### Minh hoạ hình học (rủi ro 2): biến thể "quãng đi đối xứng"', '',
           'Đảo chiều phải đi thêm cả độ rộng vùng (thoát phía tới khi cách biên GẦN ≥ rộng + 2 giá), để đảo và xuyên cần cùng một quãng đi. '
           '(Chữ plan "cách TÂM ≥ rộng/2 + 2" trùng hệt định nghĩa chính nên không minh hoạ được gì; đây là cách hiểu tự quyết.)', '',
           f'| | đảo % | xuyên % |', '|---|---|---|',
           f'| định nghĩa chính (thật) | {100 * (Rm["ket"] == DAO).mean():.1f} | {100 * (Rm["ket"] == XUYEN).mean():.1f} |',
           f'| quãng đi đối xứng — thật | {100 * (sr_["ket"] == DAO).mean():.1f} | {100 * (sr_["ket"] == XUYEN).mean():.1f} |',
           f'| quãng đi đối xứng — Đ1 | {pc(bd[0])} [{pc(bd[1])}–{pc(bd[2])}] | {pc(bx[0])} [{pc(bx[1])}–{pc(bx[2])}] |', '']

    # ======== 5.6 lần thứ k
    md += ['## H. Lần chạm thứ k (5.6) — "tôn trọng tới khi bị phá"?', '', '| k | Thật đảo % | Đ1 | Đ2 | phán quyết Đ1 | phán quyết Đ2 |', '|---|---|---|---|---|---|']
    for lab, f_ in (('1', lambda d: (d['k'] == 1).to_numpy()), ('2', lambda d: (d['k'] == 2).to_numpy()), ('≥3', lambda d: (d['k'] >= 3).to_numpy())):
        res, v1, v2 = compare(Rm, D1m, D2m, w2, f_, f_, f_, DAO)
        md.append(f'| {lab} | ' + ' | '.join(fmt_cmp(res, 'GỘP')) + f' | {v1} | {v2} |')
    # tiêu chí đăng ký: Δ = %đảo(k≥2 & mọi lần trước đều đảo) − %đảo(mọi lần)
    md += ['', '**Tiêu chí đăng ký trước (mục 3) để đổi nhãn sang lịch sử riêng:** Δ = %đảo(lần k ≥ 2 mà mọi lần trước của vùng đều đảo) − %đảo(mọi lần). '
           'Thật phải vượt dải 5–95% của Δ đối chứng ở CẢ TRAIN và TEST, cùng dấu ở ≥ 2/3 tháng.', '',
           '| Nhóm | n | Δ thật (điểm %) | Δ Đ1 [5–95] | Δ Đ2 [5–95] |', '|---|---|---|---|---|']
    sub = lambda d: ((d['k'] >= 2) & (d['n_khong_dao_truoc'] == 0)).to_numpy()
    cmp1, cmp2 = {}, {}
    for name, col, val in GROUPS:
        g_ = lambda d: (np.ones(len(d), bool) if col is None else (d[col] == val).to_numpy())
        mr = g_(Rm)
        x = Rm['ket'].to_numpy() == DAO
        pa, se_a, na = rate(x[mr & sub(Rm)])
        pb_, _, _ = rate(x[mr])
        dr = pa - pb_
        bands = []
        for D, w in ((D1m, None), (D2m, w2[name])):
            m = g_(D)
            xx = D['ket'].to_numpy() == DAO
            ww = np.ones(len(D)) if w is None else w
            v = ctrl_rates(D[m & sub(D)], xx[m & sub(D)], ww[m & sub(D)]) - ctrl_rates(D[m], xx[m], ww[m])
            bands.append(band(v))
        cmp1[name] = (dr, se_a, na, *bands[0])
        cmp2[name] = (dr, se_a, na, *bands[1])
        md.append(f'| {name} | {na} | {100 * dr:+.1f} ±{100 * se_a:.1f} | {100 * bands[0][0]:+.1f} [{100 * bands[0][1]:+.1f}; {100 * bands[0][2]:+.1f}] | '
                  f'{100 * bands[1][0]:+.1f} [{100 * bands[1][1]:+.1f}; {100 * bands[1][2]:+.1f}] |')
    vk1, vk2 = verdict(cmp1), verdict(cmp2)
    md += ['', f'- So Đ1: **{vk1}** · So Đ2: **{vk2}** ⇒ ' + ('ĐẠT — cân nhắc lịch sử riêng ở vòng sau.' if vk1.startswith('KHÁC') and vk2.startswith('KHÁC')
                                                             else '**không đạt ⇒ giữ bảng toàn cục (phương án A)**.'), '']

    # ======== 5.7 sau xuyên phá
    s_after = lambda d: (d['ket_truoc'] == XUYEN).to_numpy()
    res, v1, v2 = compare(Rm, D1m, D2m, w2, s_after, s_after, s_after, DAO)
    n57 = res['GỘP']['real'][2]
    p1, se1, n1 = rate((Rm['ket'] == DAO).to_numpy()[(Rm['k'] == 1).to_numpy()])
    md += ['## I. Lần chạm ngay sau một lần xuyên phá cùng vùng (5.7) — "đổi vai"', '',
           f'| | Thật đảo % | Đ1 | Đ2 |', '|---|---|---|---|', f'| ngay sau xuyên | ' + ' | '.join(fmt_cmp(res, 'GỘP')) + ' |',
           f'| lần đầu của vùng (k = 1) | {100 * p1:.1f} ±{100 * se1:.1f} (n={n1}) | | |', '',
           ('**Không đủ mẫu** (n < 40).' if n57 < MIN_N_57 else f'Phán quyết: Đ1 {v1} · Đ2 {v2}.'), '']

    # ======== 5.8 điểm
    q = np.quantile(Rm[Rm['split'] == 'TRAIN']['score'], [1 / 3, 2 / 3])
    md += ['## J. Điểm vùng có dự báo không? (5.8) — % đảo theo tam phân vị điểm (cắt theo TRAIN: '
           f'{q[0]:.1f} / {q[1]:.1f})', '', '| Điểm | Số đo | Thật | Đ1 | Đ2 | phán quyết Đ1 | phán quyết Đ2 |', '|---|---|---|---|---|---|---|']
    mask_r = r['mask'].to_numpy()
    for lab, lo_, hi_ in (('thấp', -1e9, q[0]), ('giữa', q[0], q[1]), ('cao', q[1], 1e9)):
        f_ = lambda d, lo_=lo_, hi_=hi_: ((d['score'] > lo_) & (d['score'] <= hi_)).to_numpy()
        g_ = lambda d, f_=f_: f_(d) & CL(d)
        res, v1, v2 = compare(Rm, D1m, D2m, w2, f_, f_, f_, DAO)
        md.append(f'| {lab} | % đảo (mọi lần) | ' + ' | '.join(fmt_cmp(res, 'GỘP')) + f' | {v1} | {v2} |')
        res, v1, v2 = compare(Rm, D1m, D2m, w2, g_, g_, g_, DAO)
        md.append(f'| {lab} | đảo/(đảo+xuyên) | ' + ' | '.join(fmt_cmp(res, 'GỘP')) + f' | {v1} | {v2} |')
    lowm = (Rm['score'] <= q[0]).to_numpy()
    md += ['', f'Tam phân vị thấp: {100 * (mask_r[Rm["srow"].to_numpy()[lowm]] == 8).mean():.0f}% là vùng CHỈ có số tròn (không bao giờ chết/đổi hình) '
           f'⇒ "chưa rõ" chỉ {100 * (Rm["ket"].to_numpy()[lowm] == CHUA_RO).mean():.0f}% (hai nhóm kia {100 * (Rm["ket"].to_numpy()[~lowm] == CHUA_RO).mean():.0f}%). '
           '% đảo (mọi lần) cao hơn là do ít bị cắt '
           'thành "chưa rõ" (xem A2), không phải vùng điểm thấp mạnh hơn. **Điểm KHÔNG phải độ mạnh** — chỉ là thứ tự xếp hạng để chọn vùng.', '']

    # ======== rủi ro
    k_all = Rm['ket'].to_numpy()
    krp = Rm[k_all == KRP]
    cr = Rm[k_all == CHUA_RO]
    zfirst = r.groupby('eid').head(1).index.to_numpy()
    krp_new = np.isin(krp['srow'].to_numpy(), zfirst).mean() if len(krp) else np.nan
    sh_rows, sh_eps = bound_shift(r, Rm)
    lo_s, hi_s = r['lo'].to_numpy()[Rm['srow'].to_numpy()], r['hi'].to_numpy()[Rm['srow'].to_numpy()]
    Cs = B['C'][Rm['bat_dau'].to_numpy()]
    jump = ((Rm['vai'] == KC).to_numpy() & (Cs > hi_s + EXIT_E)) | ((Rm['vai'] == HT).to_numpy() & (Cs < lo_s - EXIT_E))
    same_start = Rm.groupby('bat_dau')['eid'].transform('size').to_numpy() > 1
    lost, lost_n, lost_tot = lost_eid(r)
    longest = Rm.sort_values('dwell', ascending=False).head(3)
    ex_k = krp.sample(3, random_state=1) if len(krp) >= 3 else krp
    ex_c = cr.sample(3, random_state=1) if len(cr) >= 3 else cr
    h5 = HY['v5']['GỘP']
    md += ['## K. Mười ba rủi ro của plan (mục 7) — đã gặp hay chưa', '',
           f"1. **Kết quả ≈ đối chứng:** % đảo — Đ1 {VERD[DAO][1]}; Đ2 {VERD[DAO][2]}. % xuyên — Đ1 {VERD[XUYEN][1]}; Đ2 {VERD[XUYEN][2]}.",
           f"2. **Hình học E × độ rộng:** xem bảng theo bin rộng (mục A) và biến thể quãng đi đối xứng (mục G).",
           f"3. **Vệ sinh sau kẹp [2,5]:** đổi vùng {h5['chg']:.2f}/giờ (ngưỡng báo > 4), tuổi thọ trung vị {h5['life']:.0f} phút (ngưỡng báo < 30) ⇒ "
           + ('KHÔNG vượt ngưỡng.' if h5['chg'] <= 4 and h5['life'] >= 30 else '**VƯỢT NGƯỠNG**.'),
           f"4. **Không rõ phía {100 * (k_all == KRP).mean():.1f}% · chưa rõ {100 * (k_all == CHUA_RO).mean():.1f}%** "
           + ('(> 10% ⇒ lỗ hổng định nghĩa)' if max((k_all == KRP).mean(), (k_all == CHUA_RO).mean()) > 0.10 else '(cả hai ≤ 10%)') +
           f". Chưa rõ: {100 * (cr['ly_do'] == LD_RB).mean():.0f}% do vùng rời bộ khi giá còn neo (lỗ hổng = mã vùng chỉ sống khi còn hiển thị, "
           'gắn với rủi ro 5), còn lại do hết phiên; mục A2 cho thấy lỗ hổng này làm % xuyên thật thấp giả tạo' +
           f". Không rõ phía: {100 * krp_new:.0f}% xảy ra ngay nến vùng mới hiện (vùng mới dựng lên trùm giá), còn lại do biên dịch trùm giá đóng trước. "
           'Ví dụ không rõ phía (UTC): ' + '; '.join(f"{tdisp(ctx, b)}" for b in ex_k['bat_dau']) +
           '. Ví dụ chưa rõ (UTC, hết phiên/rời bộ khi đang neo): ' + '; '.join(f"{tdisp(ctx, b)}" for b in ex_c['bat_dau']) + '.',
           f"5. **Mất mã vùng khi rời bộ:** {100 * lost:.0f}% vùng mới ({lost_n}/{lost_tot}) chồng lên một vùng vừa rời bộ ≤ 60 nến trước ⇒ lịch sử riêng "
           'của những vùng này bị đếm lại từ 0. Gợi ý vòng sau: khoá lịch sử theo mức giá làm tròn 0,5.',
           '6. **Hai quy ước side ngược nhau:** máy lần chạm KHÔNG dùng `side` nào; vai riêng {kháng cự, hỗ trợ, không rõ} theo phía giá tới. Test '
           '`test_xuyen_pha_va_doi_vai`, `test_nen_nhay_qua_vung` kiểm vai.',
           f"7. **Biên dịch khi lần chạm đang mở:** {100 * sh_rows:.1f}% nến-đang-mở có biên khác nến trước; {100 * sh_eps:.0f}% lần chạm có ít nhất 1 lần dịch biên.",
           f"8. **Nến nhảy qua vùng** (nến bắt đầu đóng quá lân cận phía bên kia): {int(jump.sum())} ca ({100 * jump.mean():.1f}%); kết cục: "
           + ', '.join(f"{KET_TEN[x]} {int((Rm['ket'].to_numpy()[jump] == x).sum())}" for x in (DAO, XUYEN, CHUA_RO)) + '.',
           f"9. **Neo rất dài:** p95 = {np.quantile(dw, .95):.0f} nến; 3 lần dài nhất: " +
           '; '.join(f"{tdisp(ctx, x.bat_dau)} UTC, {x.dwell} nến, {KET_TEN[x.ket]}" for x in longest.itertuples()) + '.',
           f"10. **Hai định nghĩa xuyên / chạm cùng tồn tại:** bất đồng {100 * dis:.1f}% (mục D); điểm vùng vẫn dùng 'chạm 1 nến' (mục F: {n_old / len(Rm):.2f} lần cũ / 1 lần mới).",
           f"11. **Một nến chạm 2 vùng kề:** {100 * same_start.mean():.1f}% lần chạm bắt đầu cùng nến với lần chạm của vùng khác (± đánh giá thấp).",
           '12. **Dữ liệu không đồng nhất:** 4 phiên thin đầu file bị loại (danh sách ở đầu); không có chỗ nối; phiên 10-21 chưa trọn; một hợp đồng, '
           'một mùa (07-29 → 10-21) — không ngoại suy.',
           '13. **Ca chưa phủ trong máy 2.6 — tự quyết, KHÔNG dừng:** (a) vai không rõ chốt do hết phiên/rời bộ khi đang neo ⇒ vẫn "không rõ phía" '
           '(giữ 4 nhóm rời nhau); (b) nến chốt của ca hết phiên/rời bộ = nến PHÁT HIỆN; (c) "cầu" C₋→nến làm nến đi từ TRONG vùng ra xa vẫn tính là '
           'chạm ⇒ đếm thoát bắt đầu từ nến sau (đúng công thức plan, test ghi rõ); (d) chồng lấn vùng: giữ [2, 5] thay vì cắt giữa (mục C).', '']
    md += ['<!-- NHAN-XET -->', '']
    path = os.path.join(REPORT, 'LAN-CHAM.md')
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    tail = old.split('<!-- NHAN-XET -->', 1)[1] if '<!-- NHAN-XET -->' in old else '\n## Nhận xét\n(chưa viết)\n'
    open(path, 'w', encoding='utf-8').write('\n'.join(md[:-2]) + '\n<!-- NHAN-XET -->' + tail)
    print('\n'.join(md))
    print(f'TỔNG THỜI GIAN: {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
