"""Tự kiểm vòng 3 (r2_review.md 6.1):
 (a) ví dụ tính tay cho sel = nms (bằng nhau giữ tick thấp; chuỗi 20/15/12 cách 3 tick với w = 4 -> chấm ở tick 0 và 6), cả bản nhanh lẫn bản chuẩn;
     khung lân cận bỏ trùng (khung 12 giờ, khung ngày); nến rỗng bị bỏ hẳn ở bản chuẩn;
 (b) bản chuẩn sa3_ref.py (đọc CSV của Golden) = bản nhanh sa3_lib.py từng dấu trên GC M5, GC H1, NQ M1, NQ M15 cho sel = nms và sel = lmax
     (thêm sel = all, không lân cận, p = 1% trên GC M5 và NQ M15);
 (c) không nhìn tương lai: cắt dữ liệu ở 60% số nến;
 (d) nạp 8 ngày cuối: bản chuẩn đọc từ đầu ngày giao dịch thứ 8 kể từ cuối = bản nhanh trên bộ dữ liệu cắt.
Ghi out_r3_selftest.txt. Chạy: python sa3_selftest.py"""
import os, sys, time, numpy as np, pandas as pd
import sa3_lib as L, sa3_ref as RF
from sa_common import DotData, load_dot, _cache

SCR = L.SCR
OUT = []
t0 = time.time()


def say(ok, msg):
    s = ('ĐẠT  ' if ok else 'TRƯỢT ') + msg
    print(s, flush=True); OUT.append(s)
    return ok


def mk_ds(rows, m):
    F = pd.DataFrame([(pd.Timestamp(t), tk, b, a, b + a) for t, cells in rows for tk, b, a in cells], columns=['t', 'tk', 'bid', 'ask', 'vol'])
    F = F[F.vol > 0]
    st = F.groupby('t').agg(med=('vol', 'median'), mean=('vol', 'mean'), hi=('tk', 'max'), lo=('tk', 'min'), nl=('tk', 'size'), tot=('vol', 'sum'))
    st['rng'] = st.hi - st.lo
    return DotData('GC', m, F, st)


def ref_bars(rows, tick=0.1):
    return [(pd.Timestamp(t), np.array([c[0] * tick for c in cl]), np.array([c[1] for c in cl], float), np.array([c[2] for c in cl], float),
             np.array([c[1] + c[2] for c in cl], float), np.zeros(len(cl))) for t, cl in rows]


def fast_set(ds, r):
    i = np.nonzero(r.dot)[0]
    return set(zip(ds.t.values[ds.sbar[i]].astype('datetime64[m]'), np.where(ds.sside[i] == 0, 'dotS', 'dotB'), ds.stk[i].tolist()))


def ref_set(mk, kinds=('dotS', 'dotB')):
    return set((np.datetime64(t, 'm'), k, tk) for t, k, tk, _ in mk if k in kinds)


# ---------------- (a) tính tay ----------------
# 7 nến M1 trước: Bid j, Ask j+20 ở tick 1..20 -> 40 mẫu/nến, 280 mẫu; K' = floor(2% x 280) = 5; giá trị 40 có 7 bản -> ngưỡng (lớn thứ 6) = 40.
# Biên độ 19 tick -> w = max(4, floor(19/6 + 0,5)) = 4. Nến thứ 8 (dự phòng, vì chưa có ngày trước):
#   Bid 50 ở tick 100 và 50 ở tick 101 (bằng nhau, cách 1 tick)    -> nms: chấm ở tick 100; lmax: không chấm nào.
#   Ask 20 ở tick 200, 15 ở tick 203, 12 ở tick 206 (+ 40 để vượt ngưỡng 40: 60, 55, 52) -> nms: tick 200 và 206; lmax: chỉ 200; all: cả ba.
prev = [(pd.Timestamp('2026-10-05 14:00') + pd.Timedelta(minutes=i), [(j, j, j + 20) for j in range(1, 21)]) for i in range(7)]
test = (pd.Timestamp('2026-10-05 14:07'), [(100, 50, 0), (101, 50, 0), (200, 0, 60), (203, 0, 55), (206, 0, 52)])
rows = prev + [test]
ds = mk_ds(rows, 1)
exp = {'nms': {('dotS', 100), ('dotB', 200), ('dotB', 206)}, 'lmax': {('dotB', 200)},
       'all': {('dotS', 100), ('dotS', 101), ('dotB', 200), ('dotB', 203), ('dotB', 206)}}
for sel in ('nms', 'lmax', 'all'):
    r = L.eval_dot(ds, L.cfg_new(sel=sel))
    got = {(k, t) for _, k, t in fast_set(ds, r)}
    ok = r.thr[7] == 40 and r.src[7] == 2 and ds.w[7] == 4 and got == exp[sel]
    say(ok, f'tính tay sel={sel}, bản nhanh: ngưỡng nến 8 = {r.thr[7]:g} (tay 40), w = {ds.w[7]} (tay 4), chấm {sorted(got)} (tay {sorted(exp[sel])})')
    mk, st = RF.run(ref_bars(rows), 1, 0.1, RF.parse_set([f'sel={sel}', 'bt=0']))
    got = {(x[1], x[2]) for x in mk}
    say(got == exp[sel] and st['du_phong'] == 1, f'tính tay sel={sel}, bản chuẩn: chấm {sorted(got)}')
L.forget(ds)
# Chuỗi đúng như review: 20 ở tick 0, 15 ở tick 3, 12 ở tick 6, w = 4 (hàm chọn trực tiếp)
k = L.nb_nms(np.zeros(3, np.int64), np.array([0, 3, 6]), np.array([20, 15, 12]), np.array([4, 4, 4]), np.ones(3, bool))
k2 = L.nb_nms(np.zeros(2, np.int64), np.array([0, 1]), np.array([12, 12]), np.array([4, 4]), np.ones(2, bool))
say(list(k) == [True, False, True] and list(k2) == [True, False], f'tính tay hàm chọn: 20/15/12 ở tick 0/3/6 -> giữ {list(k)} (tay T,F,T); 12/12 ở tick 0/1 -> {list(k2)} (tay T,F)')

# Khung lân cận bỏ trùng: H12 (2 khung/ngày) và D1 (1 khung/ngày). 4 ngày, mỗi khung một nến Bid 1..100.
for m, hrs in ((720, (2, 14)), (1440, (14,))):
    rows = [(pd.Timestamp(f'2026-10-0{d} {h:02d}:00'), [(i, i, 0) for i in range(1, 101)]) for d in (5, 6, 7, 8) for h in hrs]
    ds = mk_ds(rows, m)
    r = L.eval_dot(ds, L.cfg_new())
    _, _, ns, nc = L.main_threshold(ds, 'ct', 5, 1, 2, 200)
    # nến ngày thứ 3 (2 ngày trước): khung chính 200 mẫu + (H12) khung kia 200 mẫu = 400; D1 chỉ 200 (không cộng chính nó 3 lần)
    i3 = len(hrs) * 2
    expn = 400 if m == 720 else 200
    F = fast_set(ds, r)
    mk, st = RF.run(ref_bars(rows), m, 0.1, RF.parse_set(['bt=0']))
    say(ns[i3] == expn and F == ref_set(mk) and st['chinh'] == int((r.src == 1).sum()),
        f'khung lân cận bỏ trùng (khung {m} phút, {-(-1440 // m)} khung/ngày): số mẫu ngưỡng chính nến ngày 3 = {ns[i3]} (tay {expn}); bản chuẩn = bản nhanh ({len(F)} chấm)')
    L.forget(ds)

# Nến rỗng (bản chuẩn): chèn nến không có ô volume > 0 (một nến có ô volume 0, một nến không có ô) — dấu và số nến ngưỡng y hệt khi không chèn.
rows = prev + [test]
rows_e = prev[:3] + [(pd.Timestamp('2026-10-05 14:03:30'), [(5, 0, 0)])] + prev[3:] + [(pd.Timestamp('2026-10-05 14:06:30'), [])] + [test]
a, sa = RF.run(ref_bars(rows), 1, 0.1, RF.parse_set(['bt=0']))
b, sb = RF.run(ref_bars(rows_e), 1, 0.1, RF.parse_set(['bt=0']))
say(a == b and (sa['chinh'], sa['du_phong'], sa['chua']) == (sb['chinh'], sb['du_phong'], sb['chua']) and sb.get('nen_rong') == 2,
    f'nến rỗng bị bỏ hẳn: dấu {len(a)} = {len(b)}, nến chính/dự phòng/chưa có {sa["chinh"]}/{sa["du_phong"]}/{sa["chua"]} = {sb["chinh"]}/{sb["du_phong"]}/{sb["chua"]}, nến rỗng {sb.get("nen_rong")}')

# Ngẫu nhiên nhỏ: bản chuẩn = bản nhanh trên dữ liệu giả có nhiều bằng nhau (giá trị nhỏ), 3 khung và 3 cách chọn
rs = np.random.RandomState(7)
for m in (1, 30, 720):
    t0_ = pd.Timestamp('2026-10-01 00:00'); rows = []
    nbars = {1: 4000, 30: 600, 720: 30}[m]
    for i in range(nbars):
        t = t0_ + pd.Timedelta(minutes=m * i)
        if t.weekday() == 5: continue
        lo = rs.randint(0, 30); nlv = rs.randint(3, 25) if m == 1 else rs.randint(80, 160)
        rows.append((t, [(lo + j, int(rs.geometric(.25)) - 1, int(rs.geometric(.25)) - 1) for j in range(nlv)]))
    rows = [(t, [c for c in cl if c[1] + c[2] > 0]) for t, cl in rows]
    rows = [x for x in rows if x[1]]
    ds = mk_ds(rows, m)
    for sel in ('nms', 'lmax', 'all'):
        for lc in (0, 1):
            r = L.eval_dot(ds, L.cfg_new(sel=sel, lc=lc))
            mk, st = RF.run(ref_bars(rows), m, 0.1, RF.parse_set([f'sel={sel}', f'lc={lc}', 'bt=0']))
            F = fast_set(ds, r); Rm = ref_set(mk)
            say(F == Rm and st['chinh'] == int((r.src == 1).sum()) and st['du_phong'] == int((r.src == 2).sum()),
                f'dữ liệu giả M{m} sel={sel} lân cận={lc}: bản chuẩn {len(Rm)} = bản nhanh {len(F)} chấm (lệch {len(F ^ Rm)})')
    L.forget(ds)

# ---------------- (b), (c), (d) trên dữ liệu thật ----------------
SETS = {'nen_moi': ([], {}), 'sel_lmax': (['sel=lmax'], dict(sel='lmax')), 'sel_all': (['sel=all'], dict(sel='all')),
        'khong_lan_can': (['lc=0'], dict(lc=0)), 'p1': (['pbp=100'], dict(pbp=100))}
for sym, m, tick, names in (('GC', 5, 0.1, list(SETS)), ('GC', 60, 0.1, ['nen_moi', 'sel_lmax']), ('NQ', 1, 0.25, ['nen_moi', 'sel_lmax']),
                            ('NQ', 15, 0.25, list(SETS))):
    bars, nonint = RF.load_csv(os.path.join(SCR, 'tf', f'fp_{sym}_m{m}.csv'))
    ds = load_dot(sym, m)
    nempty = sum(1 for b in bars if not (b[4] > 0).any())
    say(len(bars) - nempty == ds.nb and nonint == 0, f'{sym} M{m}: CSV Golden {len(bars)} nến (rỗng {nempty}) = bảng nhanh {ds.nb} nến; giá trị bên không nguyên: {nonint}')
    for nm in names:
        sets, ch = SETS[nm]
        r = L.eval_dot(ds, L.cfg_new(nm, **ch)); F = fast_set(ds, r)
        mk, st = RF.run(bars, m, tick, RF.parse_set(sets + ['bt=0'])); Rm = ref_set(mk)
        say(F == Rm and st['chinh'] == int((r.src == 1).sum()) and st['du_phong'] == int((r.src == 2).sum()),
            f'{sym} M{m} {nm}: chấm bản chuẩn {len(Rm)} = bản nhanh {len(F)} (lệch {len(F ^ Rm)}); nến ngưỡng chính {st["chinh"]}, dự phòng {st["du_phong"]}, chưa có {st["chua"]}')
        if nm == 'nen_moi' and m in (5, 15):
            day, _, _ = L.rule_day_slot(ds.t, m, 'ct'); ud = np.unique(day); keep = day >= ud[-8]
            sub = ds.subset(keep)
            r2 = L.eval_dot(sub, L.cfg_new()); F2 = fast_set(sub, r2)
            mk2, st2 = RF.run([b for b in bars if b[0] >= ds.t[keep][0]], m, tick, RF.parse_set(['bt=0'])); R2 = ref_set(mk2)
            say(F2 == R2, f'{sym} M{m} nạp 8 ngày cuối (từ {ds.t[keep][0]}): bản chuẩn {len(R2)} = bản nhanh {len(F2)} chấm; nến chính {st2["chinh"]}, dự phòng {st2["du_phong"]}, chưa có {st2["chua"]}')
            L.forget(sub)
    cut = int(ds.nb * 0.6); keep = np.arange(ds.nb) < cut
    sub = ds.subset(keep)
    for nm in ('nen_moi', 'sel_lmax'):
        ch = SETS[nm][1]
        ra = L.eval_dot(ds, L.cfg_new(nm, **ch)); rb = L.eval_dot(sub, L.cfg_new(nm, **ch))
        same_thr = np.array_equal(np.nan_to_num(ra.thr[:cut], nan=-9), np.nan_to_num(rb.thr, nan=-9)) and np.array_equal(ra.src[:cut], rb.src)
        A = set(np.nonzero(ra.dot & keep[ds.sbar])[0]); idx = np.nonzero(keep[ds.sbar])[0]
        B = set(idx[np.nonzero(rb.dot)[0]])
        say(same_thr and A == B, f'{sym} M{m} {nm}: cắt dữ liệu ở nến {cut}: ngưỡng và chấm trước điểm cắt y hệt ({len(B)} chấm)')
    L.forget(sub); L.forget(ds); _cache.pop((sym, m), None)
    del bars

open('out_r3_selftest.txt', 'w', encoding='utf-8').write('\n'.join(OUT) + f'\nTỔNG: {sum(x.startswith("ĐẠT") for x in OUT)}/{len(OUT)} ĐẠT ({time.time() - t0:.0f} s)\n')
print(f'TỔNG: {sum(x.startswith("ĐẠT") for x in OUT)}/{len(OUT)} ĐẠT')
sys.exit(0 if all(x.startswith('ĐẠT') for x in OUT) else 1)
