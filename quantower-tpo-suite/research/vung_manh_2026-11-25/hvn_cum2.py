#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_cum2.py — BẢN THAM CHIẾU v2 của "HVN dạng cụm" (PLAN-VUNG-MANH.md mục 13, HVN-CUM-V2.md).

Khác v1 (hvn_cum.py) ở ba chỗ, đều để tiêu chí KHÔNG phụ thuộc biên độ (cao − thấp) của profile:
  1. "Nhiều cụm": đỉnh phải là đỉnh CAO NHẤT trong ± DOM × up quanh nó (v1: ≥ 50 % đỉnh lớn nhất cả profile).
  2. "Đủ lớn": (a) hộp chứa ≥ Y × tổng profile như v1, HOẶC (b) "nổi bật tại chỗ": khối lượng hộp ≥ B × khối lượng
     trung bình một nến M30 của profile VÀ mật độ hộp ≥ CK × mật độ phần profile trong ± DOM × up ngoài hộp.
     (b) không phụ thuộc biên độ profile ⇒ bắt được cụm rõ trong ngày/tuần chạy rộng.
  3. Hộp: lõi 80 % như v1; nếu lõi hẹp hơn WT × up thì nới dần về phía còn dày hơn, tới khi đủ rộng,
     không xuống dưới XMIN × đỉnh và không leo sang bướu bên cạnh (VD).
  Số hộp tối đa tăng theo biên độ profile (max_boxes).

Chỉ dùng số nguyên bước giá + so sánh double như v1 ⇒ C# ra y hệt.

Lệnh:
  python hvn_cum2.py ca nq 2026-11-20      in hộp v1 / v2 của phiên và tuần chứa nó
  python hvn_cum2.py scan nq|gc            bảng số hộp / bề rộng trước–sau và lưới thông số
"""
import os, sys
import numpy as np
import hvn_cum as H1

HP2 = dict(
    SM=0.05,      # nửa cửa sổ làm mượt (× up) — như v1
    X=0.80,       # lõi: S ≥ X × đỉnh — như v1
    WT=0.45,      # bề rộng đích của hộp (× up): lõi hẹp hơn thì nới
    XMIN=0.50,    # khi nới không lấy ô có S < XMIN × đỉnh
    VD=0.05,      # khi nới không lấy ô cao hơn (đáy đã đi qua ở phía đó + VD × đỉnh) — không leo sang bướu bên cạnh
    DOM=3.0,      # 'vùng xung quanh' = ± DOM × up: dùng cho cả luật đỉnh cục bộ lẫn luật nổi bật
    PK2=1.0,      # đỉnh ≥ PK2 × đỉnh lớn nhất trong cửa sổ; 1,0 = phải là đỉnh CAO NHẤT trong ± DOM × up (spec chốt 1,0, không còn là thông số)
    CK=2.0,       # nổi bật tại chỗ: mật độ hộp ≥ CK × mật độ phần profile trong ± DOM × up ngoài hộp
    B=4.5,        # … và khối lượng hộp ≥ B nến M30 trung bình của profile (ngày và tuần dùng chung)
    Y=0.12,       # HOẶC hộp chứa ≥ Y khối lượng cả profile NGÀY (v1: 0,10 trên lõi; hộp v2 rộng hơn ~1,2 lần)
    Y_W=0.08,     # … profile TUẦN (như v1)
    WMIN=0.20,    # hộp (sau khi nới) vẫn hẹp hơn WMIN × up ⇒ bỏ
    MAXC=2, MAXC_STEP=6.0, MAXC_CAP=4,   # số hộp tối đa = min(CAP, max(MAXC, floor(biên độ profile / (STEP × up))))
    FLOOR=0.10,   # dừng khi đỉnh còn lại < FLOOR × đỉnh lớn nhất (chặn vòng lặp)
)


def max_boxes(n_ticks, up_ticks, hp):
    return int(min(hp['MAXC_CAP'], max(hp['MAXC'], np.floor(n_ticks / (hp['MAXC_STEP'] * up_ticks)))))


def clusters(tk, v, up_ticks, nbars, hp=HP2, mass_min=None):
    """tk: bước giá nguyên tăng dần; v: khối lượng; up_ticks = up / tick; nbars = số nến M30 của profile.
    Trả (list dict lo, hi, peak, clo, chi (lõi), mass, bars (khối lượng hộp tính bằng số nến M30 trung bình), rel), phụ)."""
    if len(tk) == 0: return [], None
    B = hp['B']; Y = hp['Y'] if mass_min is None else mass_min
    t0 = int(tk[0]); n = int(tk[-1]) - t0 + 1
    w = np.zeros(n); w[np.asarray(tk, np.int64) - t0] = v
    tot = w.sum()
    if tot <= 0 or n < 3: return [], None
    h = max(1, int(np.floor(hp['SM'] * up_ticks + 0.5)))
    S = H1.smooth_sum(w, h)
    dn = max(1, int(np.floor(min(hp['DOM'] * up_ticks, 1e9) + 0.5)))
    wt = hp['WT'] * up_ticks
    maxc = max_boxes(n - 1, up_ticks, hp)
    used = np.zeros(n, bool)
    p1 = S.max()
    out = []
    for _ in range(2000):
        cand = np.where(~used, S, -1.0)
        i = int(np.argmax(cand))
        P = cand[i]
        if P <= 0 or P < hp['FLOOR'] * p1: break
        thr = hp['X'] * P
        lo = hi = i
        while lo > 0 and not used[lo - 1] and S[lo - 1] >= thr: lo -= 1
        while hi < n - 1 and not used[hi + 1] and S[hi + 1] >= thr: hi += 1
        vai = (lo > 0 and used[lo - 1] and S[lo - 1] >= thr) or (hi < n - 1 and used[hi + 1] and S[hi + 1] >= thr)
        if vai:
            used[lo:hi + 1] = True; continue
        if P < hp['PK2'] * S[max(0, i - dn):min(n, i + dn + 1)].max():
            used[lo:hi + 1] = True; continue
        clo, chi = lo, hi
        # nới tới bề rộng đích
        fl = hp['XMIN'] * P; vd = hp['VD'] * P
        mL = S[lo:i + 1].min(); mR = S[i:hi + 1].min()
        while (hi - lo) < wt:
            okL = lo > 0 and not used[lo - 1] and S[lo - 1] >= fl and S[lo - 1] <= mL + vd
            okR = hi < n - 1 and not used[hi + 1] and S[hi + 1] >= fl and S[hi + 1] <= mR + vd
            if not okL and not okR: break
            if okL and (not okR or S[lo - 1] >= S[hi + 1]):
                lo -= 1; mL = min(mL, S[lo])
            else:
                hi += 1; mR = min(mR, S[hi])
        used[lo:hi + 1] = True
        mass = w[lo:hi + 1].sum() / tot
        bars = mass * nbars
        if (hi - lo) < hp['WMIN'] * up_ticks: continue
        # nổi bật tại chỗ: mật độ hộp so với mật độ phần profile trong ± DOM × up ngoài hộp
        A, Z = max(0, lo - dn), min(n - 1, hi + dn)
        n_out = (lo - A) + (Z - hi)
        v_out = w[A:lo].sum() + w[hi + 1:Z + 1].sum()
        v_in = w[lo:hi + 1].sum(); n_in = hi - lo + 1
        con = (v_in * n_out) / (v_out * n_in) if v_out > 0 else float('inf')
        lon = v_in >= Y * tot                                                             # (a) lớn so với cả profile
        noi = v_in * nbars >= B * tot and v_in * n_out >= hp['CK'] * v_out * n_in        # (b) nổi bật tại chỗ
        if not (lon or noi): continue
        out.append(dict(lo=t0 + lo, hi=t0 + hi, peak=t0 + i, clo=t0 + clo, chi=t0 + chi, mass=float(mass), bars=float(bars), rel=float(P / p1), con=float(min(con, 999.0)), lon=bool(lon), noi=bool(noi)))
        if len(out) >= maxc: break
    return out, dict(S=S, t0=t0, h=h, w=w, maxc=maxc, n=n)


def prof_clusters(D, a, b, hp=HP2, kind='d'):
    tk, v = D.ticks_over(a, b)
    return clusters(tk, v, H1.up_of(D, a, b) / 0.1, b - a + 1, hp, hp['Y_W'] if kind == 'w' else hp['Y'])


def prof_v1(D, a, b, kind='d'):
    return H1.prof_clusters(D, a, b, dict(H1.HP, Y=H1.HP['Y_W'] if kind == 'w' else H1.HP['Y']))


def ca(sym, date, hp=HP2):
    import pandas as pd
    D, vm = H1.load(sym)
    sc, t = H1.SCALE[sym] * 0.1, pd.to_datetime(D.m30['t'])
    k = H1.find_day(D, date)
    wk = int(D.week_of[D.days[k][0]])
    for ten, (a, b), kind in (('phiên', D.days[k], 'd'), ('tuần', D.weeks[wk], 'w')):
        up = H1.up_of(D, a, b) * H1.SCALE[sym]
        tk, _ = D.ticks_over(a, b)
        print('\n%s %s %s → %s · %d nến · up %.2f · thấp–cao %.2f–%.2f (%.1f up)' % (sym.upper(), ten, t[a], t[b], b - a + 1, up, tk[0] * sc, tk[-1] * sc, (tk[-1] - tk[0]) * sc / up))
        for c in prof_v1(D, a, b, kind)[0]:
            print('   v1: %.2f–%.2f (rộng %.2f = %.2f up) đỉnh %.2f · %.1f %%' % (c['lo'] * sc, c['hi'] * sc, (c['hi'] - c['lo']) * sc, (c['hi'] - c['lo']) * sc / up, c['peak'] * sc, 100 * c['mass']))
        cl, ex = prof_clusters(D, a, b, hp, kind)
        for c in cl:
            print('   v2: %.2f–%.2f (rộng %.2f = %.2f up) lõi %.2f–%.2f đỉnh %.2f · %.1f %% = %.1f nến · dày gấp %.2f xung quanh · %s · cao %.2f đỉnh lớn nhất · tối đa %d hộp'
                  % (c['lo'] * sc, c['hi'] * sc, (c['hi'] - c['lo']) * sc, (c['hi'] - c['lo']) * sc / up, c['clo'] * sc, c['chi'] * sc, c['peak'] * sc, 100 * c['mass'], c['bars'], c['con'], '+'.join(x for x, y in (('lớn', c['lon']), ('nổi bật', c['noi'])) if y), c['rel'], ex['maxc']))


def stat(D, kind, fn):
    nc, wd, ms, br = [], [], [], []
    for a, b in H1.spans(D, kind):
        cl, _ = fn(a, b); up = H1.up_of(D, a, b) / 0.1
        nc.append(len(cl))
        for c in cl:
            wd.append((c['hi'] - c['lo']) / up); ms.append(c['mass']); br.append(c['mass'] * (b - a + 1))
    nc = np.array(nc)
    q = lambda x: ' / '.join('%.2f' % z for z in np.percentile(x, [10, 50, 90])) if len(x) else '—'
    return '%.2f | %s | %s | %s | %s' % (nc.mean(), ' / '.join('%.0f' % (100 * (nc == k).mean()) for k in range(0, 5)), q(wd),
                                          ' / '.join('%.0f %%' % (100 * z) for z in np.percentile(ms, [10, 50, 90])) if ms else '—', q(br))


def scan(sym, grid=True):
    D, vm = H1.load(sym)
    for kind, ten in (('d', 'NGÀY'), ('w', 'TUẦN')):
        sp = H1.spans(D, kind)
        rr = []
        for a, b in sp:
            tk, _ = D.ticks_over(a, b); rr.append((tk[-1] - tk[0]) / (H1.up_of(D, a, b) / 0.1))
        print('\n## %s — profile %s (%d profile) · biên độ profile ÷ up p10/50/90/max: %s' % (sym.upper(), ten, len(sp), np.round(np.percentile(rr, [10, 50, 90, 100]), 1).tolist()))
        print('| Bản | hộp/profile | % profile có 0 / 1 / 2 / 3 / 4 hộp | bề rộng (× up) p10 / 50 / 90 | tỉ trọng p10 / 50 / 90 | số nến M30 tương đương p10 / 50 / 90 |')
        print('|---|---|---|---|---|---|')
        print('| v1 | %s |' % stat(D, kind, lambda a, b: prof_v1(D, a, b, kind)))
        print('| **v2** | %s |' % stat(D, kind, lambda a, b: prof_clusters(D, a, b, HP2, kind)))
        if not grid: continue
        for nm, over in GRID:
            print('| v2 · %s | %s |' % (nm, stat(D, kind, lambda a, b: prof_clusters(D, a, b, dict(HP2, **over), kind))))


GRID = [('WT 0,40', dict(WT=0.40)), ('WT 0,50', dict(WT=0.50)), ('không nới (WT 0)', dict(WT=0.0)),
        ('B 3,5', dict(B=3.5)), ('B 4', dict(B=4.0)), ('B 5', dict(B=5.0)), ('B 6', dict(B=6.0)),
        ('chỉ luật nổi bật (bỏ nhánh ≥ Y)', dict(Y=9.0, Y_W=9.0)), ('chỉ luật ≥ Y (bỏ nhánh nổi bật)', dict(CK=1e9)), ('Y 0,10 / 0,08', dict(Y=0.10)), ('Y 0,15 / 0,10', dict(Y=0.15, Y_W=0.10)),
        ('CK 0', dict(CK=0.0)), ('CK 1,8', dict(CK=1.8)), ('CK 2,2', dict(CK=2.2)), ('CK 2,5', dict(CK=2.5)),
        ('DOM 2', dict(DOM=2.0)), ('DOM 4', dict(DOM=4.0)),
        ('đỉnh ≥ 50 % đỉnh cục bộ (thay vì cao nhất)', dict(PK2=0.5)), ('đỉnh ≥ 80 % đỉnh cục bộ', dict(PK2=0.8)),
        ('số hộp tối đa luôn 2', dict(MAXC_CAP=2)), ('số hộp tối đa 6', dict(MAXC_CAP=6, MAXC_STEP=4.0)),
        ('XMIN 0,6', dict(XMIN=0.6)), ('XMIN 0,4', dict(XMIN=0.4)), ('VD 0,02', dict(VD=0.02)), ('VD 0,10', dict(VD=0.10)), ('FLOOR 0', dict(FLOOR=0.0)), ('FLOOR 0,2', dict(FLOOR=0.2))]

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    cmd = sys.argv[1]
    if cmd == 'ca': ca(sys.argv[2], sys.argv[3])
    elif cmd == 'scan': scan(sys.argv[2])
