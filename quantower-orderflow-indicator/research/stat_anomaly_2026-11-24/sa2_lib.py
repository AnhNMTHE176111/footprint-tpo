"""Vòng 2 "Không theo CORVEN" — thư viện dùng chung (r1_review.md mục 6). CHỈ nhìn quá khứ, không dùng giá.

CHẤM Bid/Ask, luật "thống kê" (6.1):
  - Giờ Chicago theo luật cố định: từ 08:00 UTC chủ nhật thứ hai tháng 3 tới 07:00 UTC chủ nhật đầu tiên tháng 11 là UTC-5, ngoài ra UTC-6.
  - Ngày giao dịch của luật = ngày của (giờ Chicago + 7 giờ). Khung giờ = floor(phút trong ngày Chicago / W), W = max(30, phút), số khung = ceil(1440 / W).
    (Biến thể "giờ UTC" = cách vòng 1: ngày = ngày của (UTC + 2 giờ), khung theo phút trong ngày UTC.)
  - Ngưỡng chính: gộp giá trị bên > 0 của khung giờ (và hai khung lân cận quay vòng nếu bật); mỗi khung lấy K lần xuất hiện (ngày giao dịch có
    ít nhất một nến đóng trong khung) gần nhất TRƯỚC hôm nay. Khung chính cần >= so_ngay_toi_thieu lần.
    K' = floor(p x n) (p tính bằng phần vạn), cần n x p >= 5 và n >= K'+1; ngưỡng = giá trị lớn thứ K'+1; nổ khi LỚN HƠN HẲN.
  - Dự phòng (khi ngưỡng chính chưa có): cùng công thức trên n = max(5, floor(T/phút + 0,5)) nến đóng gần nhất. Cả hai chưa có -> không nổ.
  - Chấm = vượt và lớn hơn hẳn cùng bên mọi tick khác trong ±w cùng nến (w như vòng 1). Không che, không sàn.
BIG TRADE (6.3): phân vị cuốn trên lệnh đơn, cửa sổ A / B / C, p 1% / 0,5%, T 120 / 240.
Chấm điểm: thước, đoạn, phiên, giờ như vòng 1 (UTC) để mọi cấu hình đo trên cùng một thước."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sa_common import (CAP, rhu, nb_window_kth, DotData, NQDIR, nbase, prev_mean, merge_w, ses_code, trading_day, SPLIT)  # noqa: E402
import sa_dot_rules as R1  # noqa: E402

SCR = r'C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad'


# ======================================================================= giờ Chicago
def _nth_sunday(y, mo, n):
    d = pd.Timestamp(year=y, month=mo, day=1)
    first = d + pd.Timedelta(days=(6 - d.weekday()) % 7)
    return first + pd.Timedelta(days=7 * (n - 1))


def ct_offset_hours(t):
    """Lệch giờ Chicago so với UTC (-5 hoặc -6) cho mảng thời điểm UTC."""
    t = pd.DatetimeIndex(t)
    out = np.full(len(t), -6, np.int64)
    for y in np.unique(t.year):
        a = _nth_sunday(int(y), 3, 2) + pd.Timedelta(hours=8)
        b = _nth_sunday(int(y), 11, 1) + pd.Timedelta(hours=7)
        out[(t >= a) & (t < b)] = -5
    return out


def rule_day_slot(t, m, tz='ct'):
    """(chỉ số ngày giao dịch của luật — số ngày kể từ 1970, khung giờ, số khung)."""
    t = pd.DatetimeIndex(t)
    W = max(30, m); nsl = -(-1440 // W)
    if tz == 'ct':
        loc = t + pd.to_timedelta(ct_offset_hours(t), unit='h')
        day = ((loc + pd.Timedelta(hours=7)).normalize().values.astype('datetime64[D]').astype(np.int64))
    else:
        loc = t
        day = ((loc + pd.Timedelta(hours=2)).normalize().values.astype('datetime64[D]').astype(np.int64))
    mod = np.asarray(loc.hour * 60 + loc.minute, np.int64)
    return day, mod // W, nsl


# ======================================================================= cấu hình chấm
BASE = dict(tz='ct', K=10, lc=1, mind=3, T=120, pbp=200)
VARIANTS = [('goc', {}), ('gio_utc', dict(tz='utc')), ('K5', dict(K=5)), ('K20', dict(K=20)), ('khong_lan_can', dict(lc=0)),
            ('toi_thieu_1_ngay', dict(mind=1)), ('toi_thieu_2_ngay', dict(mind=2)), ('T240', dict(T=240)), ('p1', dict(pbp=100)), ('p0.5', dict(pbp=50))]


def dot_configs():
    C = []
    for nm, ch in VARIANTS:
        c = dict(BASE); c.update(ch); c['name'] = nm; c['pa'] = 'thong_ke'; C.append(c)
    C += [dict(R1.BASELINES[0]), dict(R1.BASELINES[1])]
    return C


def K_p(n, pbp):
    n = np.asarray(n, np.int64)
    return np.where(n * pbp >= 50000, (pbp * n) // 10000, -1)


# ======================================================================= bản nhanh: chấm
_memo = {}


def _groups(ds, tz):
    """Nhóm (ngày luật, khung) liền nhau theo thời gian."""
    k = (ds.uid, 'grp', tz)
    if k in _memo: return _memo[k]
    day, slot, nsl = rule_day_slot(ds.t, ds.m, tz)
    gkey = day * 1000 + slot
    st = np.r_[0, np.nonzero(np.diff(gkey))[0] + 1] if ds.nb else np.zeros(0, np.int64)
    en = np.r_[st[1:], ds.nb]
    gid = np.repeat(np.arange(len(st)), en - st)
    V = int(min(CAP, ds.sval.max() if ds.ns else 0)) + 1
    # mảng đếm mỗi nhóm
    sg = gid[ds.sbar]
    H = np.zeros((len(st), V), np.int32)
    np.add.at(H, (sg, np.minimum(ds.sval, CAP)), 1)
    out = dict(day=day, slot=slot, nsl=nsl, st=st, en=en, gid=gid, gday=day[st], gslot=slot[st], H=H, V=V)
    _memo[k] = out
    return out


def main_threshold(ds, tz, K, lc, mind, pbp):
    """Ngưỡng chính theo nhóm -> theo nến: (thr[nb] (-1 = chưa có), gt[nb], nsamp[nb], ncen[nb])."""
    k = (ds.uid, 'main', tz, K, lc, mind, pbp)
    if k in _memo: return _memo[k]
    G = _groups(ds, tz)
    ng = len(G['st']); V = G['V']; nsl = G['nsl']
    gday, gslot, H = G['gday'], G['gslot'], G['H']
    # mỗi khung: danh sách nhóm theo thứ tự + tổng tích lũy
    per = {}
    for s in np.unique(gslot):
        idx = np.nonzero(gslot == s)[0]
        C = np.zeros((len(idx) + 1, V), np.int64); np.cumsum(H[idx], 0, out=C[1:])
        per[int(s)] = (idx, gday[idx], C)
    thr = np.full(ng, -1, np.int64); gt = np.zeros(ng, np.int64); nsamp = np.zeros(ng, np.int64); ncen = np.zeros(ng, np.int64)
    for g in range(ng):
        d, s = int(gday[g]), int(gslot[g])
        h = np.zeros(V, np.int64)
        for j, ss in enumerate([s] + ([(s - 1) % nsl, (s + 1) % nsl] if lc else [])):
            if ss not in per: continue
            idx, dd, C = per[ss]
            pos = int(np.searchsorted(dd, d, 'left'))
            a = max(0, pos - K)
            if j == 0: ncen[g] = pos - a
            h += C[pos] - C[a]
        if ncen[g] < mind: continue
        n = int(h.sum()); nsamp[g] = n
        KK = int(K_p(n, pbp))
        if KK < 0 or n < KK + 1: continue
        suf = np.cumsum(h[::-1])[::-1]
        t = int((suf >= KK + 1).sum()) - 1
        thr[g] = t; gt[g] = int(suf[t + 1]) if t + 1 < V else 0
    gid = G['gid']
    out = (thr[gid], gt[gid], nsamp[gid], ncen[gid])
    _memo[k] = out
    return out


def fallback_threshold(ds, T, pbp):
    k = (ds.uid, 'fb', T, pbp)
    if k in _memo: return _memo[k]
    n = max(5, rhu(T / ds.m))
    b = np.arange(ds.nb); lo = np.maximum(0, b - n); hi = b
    cs = np.r_[0, np.cumsum(ds.npos)]; ns = cs[hi] - cs[lo]
    Km = K_p(ns, pbp).astype(np.int64)[:, None]
    thr, gt = nb_window_kth(ds.sval, ds.s0, ds.s1, lo.astype(np.int64), hi.astype(np.int64), Km, CAP)
    out = (np.where(thr[:, 0] >= 0, thr[:, 0], -1).astype(np.int64), gt[:, 0], ns)
    _memo[k] = out
    return out


class Res:
    """Giao diện như sa_dot_rules.Res (has, thr, nom, exc, dot, kind, nom_decl, cfg) + src (1 chính, 2 dự phòng, 0 chưa có)."""

    def __init__(self, ds, cfg, has, thr, nom, exc, dot, src=None, kind='p', nom_decl=np.nan):
        self.cfg = cfg; self.kind = kind; self.has = has; self.thr = thr; self.nom = nom; self.exc = exc; self.dot = dot
        self.src = src; self.nom_decl = nom_decl


def eval_dot(ds, cfg):
    if cfg['pa'] != 'thong_ke':
        r = R1.evaluate(ds, cfg)
        return Res(ds, cfg, r.has, r.thr, r.nom, r.exc, r.dot, None, r.kind, r.nom_decl)
    tm, gm, nm, _ = main_threshold(ds, cfg['tz'], cfg['K'], cfg['lc'], cfg['mind'], cfg['pbp'])
    tf, gf, nf = fallback_threshold(ds, cfg['T'], cfg['pbp'])
    src = np.where(tm >= 0, 1, np.where(tf >= 0, 2, 0)).astype(np.int8)
    thr = np.where(src == 1, tm, np.where(src == 2, tf, -1))
    has = src > 0
    g = np.where(src == 1, gm, gf); n = np.where(src == 1, nm, nf)
    nom = np.where(has, g / np.maximum(n, 1), np.nan)
    exc = (ds.sval > np.where(has, thr, np.iinfo(np.int64).max)[ds.sbar]) & has[ds.sbar]
    dot = exc & ds.lmax
    return Res(ds, cfg, has, np.where(has, thr, np.nan).astype(float), nom, exc, dot, src, 'p', cfg['pbp'] / 10000.0)


def forget(ds):
    for k in [k for k in _memo if k[0] == ds.uid]:
        del _memo[k]
    R1.forget(ds)


# ======================================================================= khung lạ (dựng từ M1)
def build_tf_from_m1(sym, m):
    F1 = pd.read_pickle(os.path.join(NQDIR, f'F_{sym}_m1.pkl'))
    d = F1[['t', 'tk', 'bid', 'ask', 'vol']].copy()
    d['t'] = d.t.dt.floor(f'{m}min')
    F = d.groupby(['t', 'tk'], sort=True).agg(bid=('bid', 'sum'), ask=('ask', 'sum'), vol=('vol', 'sum')).reset_index()
    F = F[F.vol > 0]
    st = F.groupby('t').agg(med=('vol', 'median'), mean=('vol', 'mean'), hi=('tk', 'max'), lo=('tk', 'min'), nl=('tk', 'size'), tot=('vol', 'sum'))
    st['rng'] = st.hi - st.lo
    return DotData(sym, m, F, st, tag=sym)


# ======================================================================= Big Trade: cửa sổ A / B / C
BT_COMBOS = [(w, T, p) for w in ('A', 'B', 'C') for T in (120, 240) for p in (100, 50)]


def bt_name(w, T, p):
    return f'cuon_{w}_T{T}_p{p / 100:g}'


def bt_windows(bt, w, T, pbp):
    """lo[b] (chỉ số nến có số liệu) của cửa sổ; hi = b. Nến = nến có số liệu của BtData."""
    m = bt.m; nb = bt.nb
    n = max(5, rhu(T / m)); nmax = rhu(1380 / m)
    b = np.arange(nb)
    lo = np.maximum(0, b - n)
    if w == 'A':
        return lo
    cs = np.r_[0, np.cumsum(bt.npos)]
    need = -(-50000 // pbp)            # 5 / p mẫu (p tính bằng phần vạn): 500 với 1%, 1000 với 0,5%
    have = cs[b] - cs[lo]
    lomin = np.maximum(0, b - max(n, nmax))
    # lo nhỏ nhất cần thêm: chỉ số lớn nhất j <= lo với cs[b] - cs[j] >= need
    j = np.searchsorted(cs, cs[b] - need, 'right') - 1      # cs[j] <= cs[b] - need
    lob = np.where(have >= need, lo, np.maximum(lomin, np.minimum(lo, np.maximum(j, 0))))
    lob = np.where((have < need) & (j < 0), lomin, lob)
    if w == 'B':
        return lob
    tt = bt.t.values
    lt = np.searchsorted(tt, tt - np.timedelta64(720, 'm'), 'left')   # nến có t >= t_b - 720 phút
    return np.maximum(lob, lt)


def bt_eval(bt, w, T, pbp, gbar=None):
    """Trả Res: ngưỡng theo cửa sổ [lo, b), K = floor(p n) cần n p >= 5, n >= K+1; vượt khi mot > ngưỡng; gộp g (tham lam)."""
    from sa_bt_rules import merge_greedy
    lo = bt_windows(bt, w, T, pbp)
    V = int(min(CAP, bt.sval.max())) + 1
    Hb = np.zeros((bt.nb, V), np.int32); np.add.at(Hb, (bt.sbar, np.minimum(bt.sval, CAP)), 1)
    C = np.zeros((bt.nb + 1, V), np.int64); np.cumsum(Hb, 0, out=C[1:])
    b = np.arange(bt.nb)
    Hw = C[b] - C[lo]                                     # (nb, V)
    n = Hw.sum(1)
    KK = K_p(n, pbp)
    suf = np.cumsum(Hw[:, ::-1], 1)[:, ::-1]
    ok = (KK >= 0) & (n >= KK + 1)
    thr = np.where(ok, (suf >= (KK + 1)[:, None]).sum(1) - 1, -1)
    gt = np.where(ok, np.take_along_axis(np.c_[suf, np.zeros(bt.nb)], np.clip(thr + 1, 0, V)[:, None], 1)[:, 0], 0)
    has = thr >= 0
    nom = np.where(has, gt / np.maximum(n, 1), np.nan)
    exc = (bt.sval > np.where(has, thr, np.iinfo(np.int64).max)[bt.sbar]) & has[bt.sbar]
    dot = merge_greedy(bt, exc)
    cfg = dict(pa='cuon_bt', name=bt_name(w, T, pbp), w=w, T=T, pbp=pbp)
    r = Res(bt, cfg, has, np.where(has, thr, np.nan).astype(float), nom, exc, dot, None, 'p', pbp / 10000.0)
    r.lo = lo; r.n = n
    return r


# ======================================================================= thước "không sót" (dùng lại thước vòng 1, có chia lý do sót)
def top_sets_f(ds, bar_ok, day_ok_bars=None, ses_ok_bars=None):
    """Chỉ số mẫu của 20 lớn nhất mỗi ngày (chỉ các nến day_ok_bars) và 5 lớn nhất mỗi (ngày x phiên) (chỉ ses_ok_bars), trong nến bar_ok."""
    from sa_oracle_lib import top_sets
    m20 = bar_ok & (day_ok_bars if day_ok_bars is not None else True)
    m5 = bar_ok & (ses_ok_bars if ses_ok_bars is not None else True)
    t20, _ = top_sets(ds, np.asarray(m20, bool))
    _, t5 = top_sets(ds, np.asarray(m5, bool))
    return t20, t5


def oracle2(ds, res, Rr, mask_bars, wbar, tops):
    """Như sa_oracle_lib.oracle_row nhưng: top20/top5 truyền vào (đã lọc ngày/phiên đủ nến), tách sót vì chưa có ngưỡng / vì ngưỡng."""
    from sa_oracle_lib import near_dot
    ge_s, n_s, ge_a, n_a = Rr
    sm = mask_bars[ds.sbar]
    hs = sm & res.has[ds.sbar]
    p = res.exc[hs].sum() / max(hs.sum(), 1)
    out = dict(p_hat=p)
    strict_s = ge_s <= np.floor(p / 2 * n_s); strict_a = ge_a <= np.floor(p / 2 * n_a)
    loose_s = ge_s <= np.floor(2 * p * n_s); loose_a = ge_a <= np.floor(2 * p * n_a)
    t20, t5 = tops
    groups = {'top20': t20, 'top5': t5, 'cuc_tri': np.nonzero(sm & strict_s & strict_a)[0]}
    for g, idx in groups.items():
        out[f'{g}_so_o'] = len(idx)
        if len(idx) == 0:
            out[f'{g}'] = np.nan; out[f'{g}_sot_chua_nguong'] = 0; out[f'{g}_sot_vi_nguong'] = 0; continue
        hit = res.exc[idx] | near_dot(ds, res, idx, wbar)
        nothr = ~res.has[ds.sbar[idx]]
        out[g] = hit.mean(); out[f'{g}_sot_chua_nguong'] = int((~hit & nothr).sum()); out[f'{g}_sot_vi_nguong'] = int((~hit & ~nothr).sum())
        out[f'{g}_co_nguong'] = hit[~nothr].mean() if (~nothr).any() else np.nan
    dots = res.dot & sm; nd_ = dots.sum(); out['so_cham'] = int(nd_)
    if nd_:
        out['nhieu'] = (dots & ~loose_s & ~loose_a).sum() / nd_
        out['le3'] = (dots & (ds.sval <= 3)).sum() / nd_; out['le5'] = (dots & (ds.sval <= 5)).sum() / nd_
    else:
        out['nhieu'] = out['le3'] = out['le5'] = np.nan
    return out


if __name__ == '__main__':
    # tự kiểm nhỏ (tính tay)
    t = pd.DatetimeIndex(['2026-03-08 07:59', '2026-03-08 08:00', '2026-11-01 06:59', '2026-11-01 07:00', '2026-01-15 12:00'])
    assert list(ct_offset_hours(t)) == [-6, -5, -5, -6, -6], ct_offset_hours(t)
    # 2026-11-02 23:00 UTC = 17:00 Chicago (UTC-6) -> ngày giao dịch 03/11, khung 17:00/30 = 34
    d, s, n = rule_day_slot(pd.DatetimeIndex(['2026-11-02 23:00', '2026-10-27 22:00', '2026-10-27 21:59']), 5, 'ct')
    D = lambda x: int(np.datetime64(x, 'D').astype(np.int64))
    assert list(d) == [D('2026-11-03'), D('2026-10-28'), D('2026-10-27')] and list(s) == [34, 34, 33] and n == 48, (d, s)
    d, s, n = rule_day_slot(pd.DatetimeIndex(['2026-10-27 20:00']), 240, 'ct')   # 15:00 Chicago -> khung 900//240 = 3, 6 khung
    assert list(s) == [3] and n == 6
    assert rule_day_slot(pd.DatetimeIndex(['2026-10-27 20:00']), 45, 'utc')[2] == 32   # ceil(1440/45)
    assert list(K_p([249, 250, 999, 1000], 200)) == [-1, 5, 19, 20]
    print('sa2_lib tự kiểm: ĐẠT')
