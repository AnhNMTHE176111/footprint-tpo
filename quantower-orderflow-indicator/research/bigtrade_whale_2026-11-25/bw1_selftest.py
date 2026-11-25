"""Tự kiểm vòng 1 (PLAN.md mục 6.2). python bw1_selftest.py -> out_bw1_selftest.txt"""
import os, sys, io
from collections import deque
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bw1_common as C

out = io.StringIO()
fails = []


def P(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); out.write(s + '\n')


def check(name, ok, extra=''):
    P(('DAT ' if ok else 'ROT ') + name + (' | ' + extra if extra else ''))
    if not ok: fails.append(name)


# 1. hàm hạng
check('K(R=10, 1380 phut) = 10', C.rank_K(10, 1380) == 10)
check('K(R=10, 690 phut) = 5', C.rank_K(10, 690) == 5)
check('K(R=10, 60 phut) = 1 (khong bao gio 0)', C.rank_K(10, 60) == 1, f'rhu(10*60/1380)={C.rhu(10*60/1380)}')
check('K(R=10, 0 phut) = 1', C.rank_K(10, 0) == 1)

# 2. lớn hơn hẳn: 12 lệnh cỡ 100, K = 10 -> ngưỡng 100; 100 không nổ, 101 nổ
H = np.zeros(C.CAP + 1, np.int64); H[100] = 12; H[3] = 50
c = np.cumsum(H[::-1]); thr = C.WinHist.kth(c, 10)
check('12 lenh 100, K=10 -> nguong 100', thr == 100, f'nguong={thr}')
k = C.gop(np.array([0, 50]), np.array([100, 101]), thr, 2)
check('lenh 100 khong no, 101 no', k == [1], f'giu={k}')
check('gop tham lam: cach <= g bi bo, bang nhau tick thap truoc',
      C.gop(np.array([10, 12, 13, 30]), np.array([50, 60, 60, 55]), 20, 2) == [1, 3],
      str(C.gop(np.array([10, 12, 13, 30]), np.array([50, 60, 60, 55]), 20, 2)))
check('gia tri > 4095 don o cuoi, so sanh dung gia tri that',
      C.gop(np.array([0]), np.array([5000]), 4095.0, 2) == [0])

# 3. Ứng viên A (D=5, R=10, tắt gộp, khởi động 1 ngày nến) tái lập bw0_quick ('rank', 5, 10)
def bw0_run(name, m, days=5, R=10):
    """Chép nguyên logic bw0_quick.py (không gộp) để so trên dữ liệu HIỆN TẠI."""
    d = pd.read_csv(C.LOGDIR + '/' + name).drop_duplicates(['time_ticks', 'price'], keep='last')
    d['t'] = pd.to_datetime(d.time_iso.str[:19]); d = d.sort_values(['t', 'price'])
    bars = [(t, g.mot.values.astype(int)) for t, g in d.groupby('t')]
    Hh = np.zeros(4096, int); q = deque(); o = []
    nb = max(5, round(days * 1380 / m))
    for i, (t, v) in enumerate(bars):
        if len(q) >= round(1380 / m):
            K = max(1, int(np.floor(R * len(q) * m / 1380 + .5))); cc = np.cumsum(Hh[::-1]); th = 4095 - int(np.searchsorted(cc, K))
            for x in v[v > th]: o.append((t, int(x), th))
        q.append(v); np.add.at(Hh, np.minimum(v, 4095), 1)
        if len(q) > nb:
            oo = q.popleft(); np.add.at(Hh, np.minimum(oo, 4095), -1)
    o = pd.DataFrame(o, columns=['t', 'mot', 'thr'])
    return o, len(bars) * m / 1380


def line(o, nd):
    return (f"vong/ngay {len(o)/nd:7.1f}  nguong p10/p50/p90 {o.thr.quantile(.1):.0f}/{o.thr.quantile(.5):.0f}/{o.thr.quantile(.9):.0f}"
            f"  co vong p10/p50 {o.mot.quantile(.1):.0f}/{o.mot.quantile(.5):.0f}  nho nhat {o.mot.min()}")


ref = {}
for ln in open(os.path.join(C.HERE, 'out_bw0_quick.txt'), encoding='utf-8'):
    if "('rank', 5, 10)" in ln: ref[ln[:22].strip()] = ln.split("('rank', 5, 10)")[1].strip()
for key, name in (('GCX_M1', '_GC_XCEC_Time_1Minute.csv'), ('GCX_M5', '_GC_XCEC_Time_5Minute.csv'),
                  ('NQ_M1', '_NQZ26_XCME_Time_1Minute.csv'), ('NQ_M15', '_NQZ26_XCME_Time_15Minute.csv')):
    log = C.load(key)
    cand = C.CandA(log, 5, [10]); th, mn, fu, src = C.run_multi(cand, log)
    warm = len(log.t)  # khởi động 1 ngày nến: >= rhu(1380/m) nến
    nq = np.array([min(i, cand.cap) for i in range(log.nb)])
    thr = np.where(nq >= round(1380 / log.m), th[0], np.nan)
    rr = C.select_rounds(log, thr, merge=False)
    rr = rr.rename(columns={'bar': 'b'})
    mine = line(rr, log.nb * log.m / 1380)
    o, nd = bw0_run(name, log.m)
    theirs = line(o, nd)
    check(f'A(D=5,R=10) = logic bw0_quick tren du lieu hien tai [{key}]', mine == theirs and len(rr) == len(o), f'{mine} || {theirs}')
    fileline = ref.get(name[:22])
    same_file = fileline == mine
    P(f'   so voi dong trong out_bw0_quick.txt: {"TRUNG" if same_file else "KHAC"} | file: {fileline}')
    if key.startswith('GC'):
        check(f'A(D=5,R=10) tai lap dong out_bw0_quick.txt [{key}] (nhat ky vang khong doi tu 10/11)', same_file)
    else:
        P(f'   (NQ: nhat ky {name} da ghi them sau khi chay bw0_quick (sua luc 08:15-08:17), nen chi doi chieu logic tren du lieu hien tai)')

# 4. Không nhìn trước: xáo dữ liệu sau nến i -> ngưỡng và vòng tới nến i không đổi
def shuffled(log, i, seed=1):
    rng = np.random.default_rng(seed)
    a = log.off[i + 1]
    mot = log.cmot.copy(); vol = log.cvol.copy(); tk = log.ctk.copy()
    p = rng.permutation(len(mot) - a)
    mot[a:] = mot[a:][p]; vol[a:] = vol[a:][p]; tk[a:] = tk[a:][p] + rng.integers(-50, 50, len(p))
    return C.Log(log.key, log.m, log.tick, log.sym, log.t, log.cb.copy(), tk, mot, vol)


def cands(log):
    return {
        'A': lambda: C.CandA(log, 5, [10]), 'B': lambda: C.CandB(log, 5, [10]), 'C': lambda: C.CandC(log, [(15, 3)]),
        'Cx': lambda: C.CandCwrong(log, [5]), 'D': lambda: C.CandHill(log, [(100, 10)]), 'E': lambda: C.CandE(log, [50]),
        'F': lambda: C.CandF(log, 240), 'G': lambda: C.CandG(log, 1380, [2]),
    }


for key in ('NQ_M15', 'GCX_M5'):
    log = C.load(key)
    i = int(log.nb * 0.6)
    sh = shuffled(log, i)
    for nm, mk in cands(log).items():
        th1 = C.run_multi(mk(), log)[0][0]
        th2 = C.run_multi(cands(sh)[nm](), sh)[0][0]
        if nm == 'F': th1 = np.floor(3 * th1 + 0.5); th2 = np.floor(3 * th2 + 0.5)
        same_thr = np.array_equal(th1[:i + 1], th2[:i + 1], equal_nan=True)
        r1 = C.select_rounds(log, th1); r2 = C.select_rounds(sh, th2)
        r1 = r1[r1.bar <= i].reset_index(drop=True); r2 = r2[r2.bar <= i].reset_index(drop=True)
        changed_after = not np.array_equal(th1[i + 1:], th2[i + 1:], equal_nan=True) or nm == 'E'
        check(f'khong nhin truoc [{key}] ung vien {nm} (nen i={i}/{log.nb})', same_thr and r1.values.tolist() == r2.values.tolist(),
              f'vong <= i: {len(r1)}; nguong sau i doi (chung to co xao): {changed_after}')
    for nm, fn in (('CUR', C.thr_current), ('ADAPT', C.thr_adaptive)):
        a, b = fn(log), fn(sh)
        check(f'khong nhin truoc [{key}] moc {nm}', np.array_equal(a[:i + 1], b[:i + 1], equal_nan=True))
    g1, g2 = log.gvec(), sh.gvec()
    check(f'khong nhin truoc [{key}] g gop vong', np.array_equal(g1[:i + 1], g2[:i + 1]))

# 5. g và ngày đủ
log = C.load('GCX_M1')
check('ngay du GCX M1 = 16', len(log.full_days) == 16, str(len(log.full_days)))
log = C.load('NQ_M1')
check('ngay du NQ M1 = 6 (dem lai)', len(log.full_days) == 6, str([C.fmt_day(d) for d in log.full_days]))
P('KET QUA:', 'DAT HET' if not fails else f'ROT {len(fails)}: {fails}')
with open(os.path.join(C.HERE, 'out_bw1_selftest.txt'), 'w', encoding='utf-8') as f:
    f.write(out.getvalue())
