"""Tự kiểm vòng 2 (r1_review.md 6.4): (a) ví dụ tính tay; (b) bản chuẩn sa2_ref.py (đọc CSV của Golden) = bản nhanh sa2_lib.py từng dấu
trên GC M5, GC H1, NQ M1, NQ M15 (chấm) và trên nhật ký btlog_{NQ_M1, NQ_M15, GC_M5, GC_M30} (Big Trade); (c) không nhìn tương lai (cắt dữ liệu);
(d) chart nạp ít ngày: bản chuẩn đọc từ ngày thứ 8 kể từ cuối = bản nhanh trên bộ dữ liệu cắt.
Ghi out_r2_selftest.txt. Chạy: python sa2_selftest.py"""
import os, sys, time, numpy as np, pandas as pd
import sa2_lib as L, sa2_ref as RF
from sa_common import DotData, load_dot, _cache
from sa_bt_rules import BtData

SCR = L.SCR
OUT = []
t0 = time.time()


def say(ok, msg):
    s = ('ĐẠT  ' if ok else 'TRƯỢT ') + msg
    print(s, flush=True); OUT.append(s)
    return ok


def mk_ds(rows, m):
    """rows: list (thời điểm UTC, list (tick, bid, ask))."""
    F = pd.DataFrame([(pd.Timestamp(t), tk, b, a, b + a) for t, cells in rows for tk, b, a in cells], columns=['t', 'tk', 'bid', 'ask', 'vol'])
    F = F[F.vol > 0]
    st = F.groupby('t').agg(med=('vol', 'median'), mean=('vol', 'mean'), hi=('tk', 'max'), lo=('tk', 'min'), nl=('tk', 'size'), tot=('vol', 'sum'))
    st['rng'] = st.hi - st.lo
    return DotData('GC', m, F, st)


def cfg_of(**kw):
    c = dict(L.BASE); c.update(kw); c['pa'] = 'thong_ke'; c['name'] = 'x'; return c


# ---------------- (a) ví dụ tính tay ----------------
# Ngưỡng chính: 4 ngày, mỗi ngày một nến M30 lúc 14:00 UTC (09:00 Chicago, khung 18), Bid 1..100 ở tick 1..100.
rows = [(f'2026-10-0{d} 14:00', [(i, i, 0) for i in range(1, 101)]) for d in (5, 6, 7, 8)]
ds = mk_ds(rows, 30)
for lc in (0, 1):
    r = L.eval_dot(ds, cfg_of(lc=lc))
    # ngày 1–3: chính chưa đủ 3 ngày; dự phòng n = 5 nến: 0 / 100 / 200 mẫu -> 2% x n < 5 -> chưa có. Ngày 4: 300 mẫu, K' = 6, giá trị lớn thứ 7 = 98.
    ok = list(r.has) == [False, False, False, True] and r.thr[3] == 98 and list(r.src) == [0, 0, 0, 1]
    dots = [int(x) for x in sorted(ds.stk[r.dot])]; exc = [int(x) for x in sorted(ds.sval[r.exc])]
    ok &= dots == [100] and exc == [99, 100]
    say(ok, f'tính tay ngưỡng chính (lân cận={lc}): có ngưỡng {[bool(x) for x in r.has]}, ngưỡng ngày 4 = {r.thr[3]:g} (tay: 98), vượt {[int(x) for x in exc]} (tay: 99, 100), chấm ở tick {[int(x) for x in dots]} (tay: 100)')
    mk, st = RF.run([(pd.Timestamp(t), np.array([c[0] * 0.1 for c in cl]), np.array([c[1] for c in cl], float), np.array([c[2] for c in cl], float),
                      np.array([c[1] + c[2] for c in cl], float), np.zeros(len(cl))) for t, cl in rows], 30, 0.1, RF.parse_set([f'lc={lc}', 'bt=0']))
    say([(x[1], x[2]) for x in mk] == [('dotS', 100)] and st['chinh'] == 1, f'tính tay, bản chuẩn: dấu {[(str(x[0]), x[1], x[2]) for x in mk]}')
# Dự phòng: 6 nến M1 liền nhau, Bid 1..60. Nến thứ 6: 5 nến trước = 300 mẫu, K' = 6, lớn thứ 7 = 59, vượt = 60. Nến thứ 5: 240 mẫu -> 4,8 < 5 -> chưa có.
rows = [(pd.Timestamp('2026-10-05 14:00') + pd.Timedelta(minutes=i), [(j, j, 0) for j in range(1, 61)]) for i in range(6)]
ds = mk_ds(rows, 1); r = L.eval_dot(ds, cfg_of())
say(list(r.src) == [0, 0, 0, 0, 0, 2] and r.thr[5] == 59 and sorted(ds.sval[r.exc]) == [60],
    f'tính tay dự phòng: nguồn ngưỡng {[int(x) for x in r.src]} (tay 0,0,0,0,0,2), ngưỡng nến 6 = {r.thr[5]:g} (tay 59)')
# "lớn hơn hẳn" + gộp ±w: hai ô bằng nhau cạnh nhau không ô nào thành chấm
rows = [(pd.Timestamp('2026-10-05 14:00') + pd.Timedelta(minutes=i), [(j, j, 0) for j in range(1, 61)]) for i in range(5)]
rows.append((pd.Timestamp('2026-10-05 14:05'), [(1, 70, 0), (3, 70, 0), (20, 65, 0)]))
ds = mk_ds(rows, 1); r = L.eval_dot(ds, cfg_of())
say(sorted(ds.stk[r.dot]) == [20] and sorted(ds.sval[r.exc]) == [65, 70, 70], f'tính tay gộp: hai ô 70 cách 2 tick (w = 4) đều không thành chấm, ô 65 ở tick 20 là chấm -> {[int(x) for x in sorted(ds.stk[r.dot])]}')
# Big Trade cửa sổ B và C: M1, mỗi nến 100 lệnh đơn; p 1% cần 500 mẫu.
c = pd.DataFrame([(pd.Timestamp('2026-10-05 00:00') + pd.Timedelta(minutes=i * (1 if i < 10 else 800)), j, (j % 50) + 1, 1, 0)
                  for i in range(12) for j in range(100)], columns=['t', 'tk', 'mot', 'buy', 'sell'])
bt = BtData('GC', 1, c)
loA = L.bt_windows(bt, 'A', 120, 100); loB = L.bt_windows(bt, 'B', 120, 100); loC = L.bt_windows(bt, 'C', 120, 100)
# Nến 0..9 ở phút 0..9, nến 10 ở phút 8000, nến 11 ở phút 8800. n = 120 nến (A lấy hết nến trước); B giống A (đã lấy hết);
# C: nến 10 cách nến 9 tới 7.991 phút > 720 -> bỏ hết (lo = 10); nến 11 cách nến 10 800 phút > 720 -> bỏ hết (lo = 11).
say(list(loA) == [0] * 12 and list(loB) == [0] * 12 and loC[9] == 0 and loC[10] == 10 and loC[11] == 11,
    f'tính tay cửa sổ Big Trade: lo A {[int(x) for x in loA]}, C {[int(x) for x in loC]} (tay C: 0 x 10, 10, 11)')
bt2 = BtData('GC', 60, c.assign(t=pd.Timestamp('2026-10-05 00:00') + pd.to_timedelta(np.repeat(np.arange(12) * 60, 100), unit='m')))
# H1: n = max(5, 2) = 5 nến = 500 mẫu (đủ); với p 0,5% cần 1000 mẫu -> B lấy thêm tới 10 nến (tối đa 23)
loB5 = L.bt_windows(bt2, 'B', 120, 50)
say(loB5[11] == 1 and loB5[6] == 0 and L.bt_windows(bt2, 'A', 120, 50)[11] == 6, f'tính tay cửa sổ B (H1, p 0,5%): lo nến 11 = {loB5[11]} (tay 1), nến 6 = {loB5[6]} (tay 0)')

# ---------------- (b) bản chuẩn = bản nhanh ----------------
def fast_dot_marks(ds, cfg, keep=None):
    r = L.eval_dot(ds, cfg)
    i = np.nonzero(r.dot)[0]
    return set(zip(ds.t.values[ds.sbar[i]].astype('datetime64[m]'), np.where(ds.sside[i] == 0, 'dotS', 'dotB'), ds.stk[i].tolist())), r


def ref_marks(mk, kinds):
    return set((np.datetime64(t, 'm'), k, tk) for t, k, tk, _ in mk if k in kinds)


SETS = {'goc': [], 'p1': ['pbp=100'], 'gio_utc': ['tz=utc'], 'toi_thieu_1_ngay': ['mind=1'], 'T240': ['T=240'], 'khong_lan_can': ['lc=0'], 'K5': ['K=5']}
CFG = {c['name']: c for c in L.dot_configs()}
for sym, m, tick, names in (('GC', 5, 0.1, list(SETS)), ('GC', 60, 0.1, list(SETS)), ('NQ', 1, 0.25, ['goc', 'p1']), ('NQ', 15, 0.25, list(SETS))):
    bars, nonint = RF.load_csv(os.path.join(SCR, 'tf', f'fp_{sym}_m{m}.csv'))
    ds = load_dot(sym, m)
    say(len(bars) == ds.nb and nonint == 0, f'{sym} M{m}: CSV Golden {len(bars)} nến = bảng nhanh {ds.nb} nến; giá trị bên không nguyên: {nonint}')
    for nm in names:
        F_, r = fast_dot_marks(ds, CFG[nm])
        mk, st = RF.run(bars, m, tick, RF.parse_set(SETS[nm] + ['bt=0']))
        Rm = ref_marks(mk, ('dotS', 'dotB'))
        say(F_ == Rm and st['chinh'] == int((r.src == 1).sum()) and st['du_phong'] == int((r.src == 2).sum()),
            f'{sym} M{m} {nm}: chấm bản chuẩn {len(Rm)} = bản nhanh {len(F_)} (lệch {len(F_ ^ Rm)}); nến ngưỡng chính {st["chinh"]}, dự phòng {st["du_phong"]}, chưa có {st["chua"]}')
        if nm == 'goc' and m in (5, 15):
            # (d) nạp ít ngày: bản chuẩn đọc từ đầu ngày giao dịch thứ 8 kể từ cuối = bản nhanh trên bộ dữ liệu cắt
            day, _, _ = L.rule_day_slot(ds.t, m, 'ct'); ud = np.unique(day); keep = day >= ud[-8]
            sub = ds.subset(keep)
            F2, r2 = fast_dot_marks(sub, CFG[nm])
            mk2, st2 = RF.run([b for b in bars if b[0] >= ds.t[keep][0]], m, tick, RF.parse_set(['bt=0']))
            R2 = ref_marks(mk2, ('dotS', 'dotB'))
            say(F2 == R2, f'{sym} M{m} nạp 8 ngày cuối (từ {ds.t[keep][0]}): bản chuẩn {len(R2)} = bản nhanh {len(F2)} chấm; nến dự phòng {st2["du_phong"]}, chưa có {st2["chua"]}')
            L.forget(sub)
    # (c) không nhìn tương lai: cắt ở 60% số nến
    cut = int(ds.nb * 0.6); keep = np.arange(ds.nb) < cut
    sub = ds.subset(keep)
    for nm in ('goc', 'T240'):
        ra = L.eval_dot(ds, CFG[nm]); rb = L.eval_dot(sub, CFG[nm])
        same_thr = np.array_equal(np.nan_to_num(ra.thr[:cut], nan=-9), np.nan_to_num(rb.thr, nan=-9)) and np.array_equal(ra.src[:cut], rb.src)
        A = set(np.nonzero(ra.dot & keep[ds.sbar])[0]); idx = np.nonzero(keep[ds.sbar])[0]
        B = set(idx[np.nonzero(rb.dot)[0]])
        say(same_thr and A == B, f'{sym} M{m} {nm}: cắt dữ liệu ở nến {cut}: ngưỡng và chấm trước điểm cắt y hệt')
    L.forget(sub); L.forget(ds); _cache.pop((sym, m), None)

# Big Trade: bản chuẩn đọc footprint + nhật ký như Golden (--zeromot) = bản nhanh trên các nến có trong footprint
for key, m, tick, combos in (('NQ', 1, 0.25, [('A', 240, 100), ('B', 240, 100), ('C', 240, 100)]), ('GC', 5, 0.1, [('A', 240, 100), ('B', 120, 50), ('C', 120, 50)]),
                             ('NQ', 15, 0.25, [('A', 240, 100), ('B', 240, 100), ('C', 120, 50)]), ('GC', 30, 0.1, [('A', 240, 100), ('B', 120, 50), ('C', 240, 50)])):
    logf = os.path.join(SCR, f'btlog_{key}_M{m}.csv')
    bars, _ = RF.load_csv(os.path.join(SCR, 'tf', f'fp_{key}_m{m}.csv'), zeromot=True)
    by = RF.load_btlog(logf)
    d = pd.read_csv(logf)
    d['t'] = pd.to_datetime(d.time_iso, utc=True).dt.tz_localize(None); d['tk'] = np.round(d.price / tick).astype(np.int64)
    have = set(b[0] for b in bars)
    d = d[d.t.isin(have)]
    d = d.sort_values('mot', ascending=False, kind='stable').drop_duplicates(['t', 'tk']).sort_values(['t', 'tk'])
    bt = BtData(key, m, d[['t', 'tk', 'mot', 'buy', 'sell']].reset_index(drop=True))
    for w, T, p in combos:
        r = L.bt_eval(bt, w, T, p)
        i = np.nonzero(r.dot)[0]
        Fm = set(zip(bt.t.values[bt.sbar[i]].astype('datetime64[m]'), ['bt'] * len(i), bt.stk[i].tolist()))
        mk, st = RF.run(bars, m, tick, RF.parse_set(['dots=0', f'bt_w={w}', f'bt_T={T}', f'bt_pbp={p}']), by)
        Rm = ref_marks(mk, ('bt',))
        say(Fm == Rm and st['bt_co'] == int(r.has.sum()), f'Big Trade {key} M{m} {L.bt_name(w, T, p)}: vòng bản chuẩn {len(Rm)} = bản nhanh {len(Fm)} (lệch {len(Fm ^ Rm)}); '
            f'nến có số liệu {bt.nb}, có ngưỡng {st["bt_co"]}')
    # không nhìn tương lai
    cut = bt.t[int(bt.nb * 0.6)]
    bt2 = BtData(key, m, d[d.t < cut][['t', 'tk', 'mot', 'buy', 'sell']].reset_index(drop=True))
    for w, T, p in combos:
        ra = L.bt_eval(bt, w, T, p); rb = L.bt_eval(bt2, w, T, p)
        k = bt2.nb
        say(np.array_equal(np.nan_to_num(ra.thr[:k], nan=-9), np.nan_to_num(rb.thr, nan=-9)) and np.array_equal(ra.dot[:bt2.ns], rb.dot),
            f'Big Trade {key} M{m} {L.bt_name(w, T, p)}: cắt dữ liệu ở {cut}: ngưỡng và vòng trước điểm cắt y hệt')

open('out_r2_selftest.txt', 'w', encoding='utf-8').write('\n'.join(OUT) + f'\nTỔNG: {sum(x.startswith("ĐẠT") for x in OUT)}/{len(OUT)} ĐẠT ({time.time() - t0:.0f} s)\n')
print(f'TỔNG: {sum(x.startswith("ĐẠT") for x in OUT)}/{len(OUT)} ĐẠT')
sys.exit(0 if all(x.startswith('ĐẠT') for x in OUT) else 1)
