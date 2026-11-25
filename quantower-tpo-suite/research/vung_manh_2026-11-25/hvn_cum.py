#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_cum.py — BẢN THAM CHIẾU của "HVN dạng cụm" (PLAN-VUNG-MANH.md mục 10) + các phép đo trong HVN-CUM.md.

HVN dạng cụm = cả THÂN khối lượng quanh một đỉnh lớn của profile (như hộp người dùng vẽ tay),
không phải từng đỉnh nhọn. Thuật toán chỉ dùng SỐ NGUYÊN bước giá ⇒ C# ra y hệt Python:

  1. Dựng mảng khối lượng dày theo TỪNG BƯỚC GIÁ từ giá thấp nhất tới cao nhất của profile (chỗ trống = 0).
  2. Làm mượt: S[i] = tổng khối lượng trong cửa sổ ± h bước giá, h = max(1, floor(SM × up / tick + 0,5)),
     up = biên độ (High − Low) trung bình của CHÍNH các nến M30 trong profile. (Ngoài mép profile coi là 0.)
  3. "Bóc" từ cao xuống thấp: lấy chỗ cao nhất còn chưa dùng i*; nới hai phía khi S ≥ X × S[i*] và chưa dùng;
     đánh dấu đã dùng. Nếu khi dừng mà ô kề bên đã dùng và vẫn ≥ X × S[i*] ⇒ đó là VAI của khối trước, bỏ.
     Dừng khi S[i*] < PK2 × đỉnh lớn nhất, hoặc đã đủ MAXC cụm.
  4. Giữ cụm có khối lượng (thô) ≥ Y × tổng profile.

Lệnh:
  python hvn_cum.py scan gc|nq        bảng chọn thông số (số cụm/profile, bề rộng theo U, tỉ trọng)
  python hvn_cum.py ca nq 2026-11-23  in cụm mới + HVN cũ của một phiên (và tuần chứa nó)
  python hvn_cum.py ve                vẽ PNG vào hvn_cum/
  python hvn_cum.py fixture           ghi fixture/hvn_cum_cases.json (ca đối chiếu cho C#)
"""
import os, sys, tempfile
import numpy as np

HP = dict(
    SM=0.05,     # nửa cửa sổ làm mượt (× up)
    X=0.80,      # biên thân (= độ ĐỀU): mọi mức giá trong thân có S ≥ X × đỉnh của cụm
    PK2=0.50,    # cụm thứ hai: đỉnh ≥ PK2 × đỉnh lớn nhất
    Y=0.10,      # tỉ trọng khối lượng tối thiểu của một cụm so với cả profile (profile TUẦN dùng Y_W)
    Y_W=0.08,
    WMIN=0.20,   # bề rộng tối thiểu của thân (× up) — hẹp hơn là đỉnh nhọn, không phải cụm
    MAXC=2,      # tối đa bấy nhiêu cụm mỗi profile
)


def smooth_sum(w, h):
    """Tổng cửa sổ ± h ô (ngoài mép = 0). w: mảng float các số nguyên ⇒ kết quả chính xác."""
    cs = np.r_[0.0, np.cumsum(w)]
    n = len(w); i = np.arange(n)
    return cs[np.minimum(n, i + h + 1)] - cs[np.maximum(0, i - h)]


def half_window(up, tick, sm):
    return max(1, int(np.floor(sm * up / tick + 0.5)))


def clusters(tk, v, up_ticks, hp=HP):
    """
    tk: mảng số nguyên bước giá (tăng dần, không trùng); v: khối lượng; up_ticks = up / tick (số thực).
    Trả list dict (theo thứ tự tìm thấy = đỉnh cao trước): lo, hi, peak (bước giá), mass (tỉ trọng), rel (đỉnh / đỉnh lớn nhất),
    kèm 'S', 't0', 'h' ở phần tử phụ để vẽ.
    """
    if len(tk) == 0: return [], None
    t0 = int(tk[0]); n = int(tk[-1]) - t0 + 1
    w = np.zeros(n); w[np.asarray(tk, np.int64) - t0] = v
    tot = w.sum()
    if tot <= 0 or n < 3: return [], None
    h = max(1, int(np.floor(hp['SM'] * up_ticks + 0.5)))
    S = smooth_sum(w, h)
    used = np.zeros(n, bool)
    p1 = S.max()
    out = []
    for _ in range(200):
        cand = np.where(~used, S, -1.0)
        i = int(np.argmax(cand))                      # ô đầu tiên (giá thấp nhất) khi hoà
        if cand[i] <= 0 or cand[i] < hp['PK2'] * p1: break
        thr = hp['X'] * S[i]
        lo = hi = i
        while lo > 0 and not used[lo - 1] and S[lo - 1] >= thr: lo -= 1
        while hi < n - 1 and not used[hi + 1] and S[hi + 1] >= thr: hi += 1
        vai = (lo > 0 and used[lo - 1] and S[lo - 1] >= thr) or (hi < n - 1 and used[hi + 1] and S[hi + 1] >= thr)
        used[lo:hi + 1] = True
        if vai: continue
        mass = w[lo:hi + 1].sum() / tot
        if mass < hp['Y']: continue
        if (hi - lo) < hp['WMIN'] * up_ticks: continue
        out.append(dict(lo=t0 + lo, hi=t0 + hi, peak=t0 + i, mass=float(mass), rel=float(S[i] / p1)))
        if len(out) >= hp['MAXC']: break
    return out, dict(S=S, t0=t0, h=h, w=w)


# ------------------------------------------------------------------ dữ liệu
def load(sym):
    os.environ['VM_CACHE'] = os.path.join(os.environ.get('VM_CACHE_DIR', tempfile.gettempdir()), 'vm1_%s.pkl' % sym)
    import importlib, vm
    importlib.reload(vm)
    D = vm.Data(cache=os.environ['VM_CACHE'])
    if sym == 'nq':
        def rows_over_nq(self, a, b, row=vm.ROW):
            tk, v = self.ticks_over(a, b)
            if len(tk) == 0: return np.array([]), np.array([])
            rid = np.round((tk * 0.25) / 0.5).astype(np.int64)
            u, inv = np.unique(rid, return_inverse=True)
            return u * row, np.bincount(inv, weights=v)
        type(D).rows_over = rows_over_nq
    return D, vm


def up_of(D, a, b):
    """Biên độ M30 trung bình của chính các nến trong profile (đơn vị giá của D)."""
    return float((D.m30['h'][a:b + 1] - D.m30['l'][a:b + 1]).mean())


def prof_clusters(D, a, b, hp=HP):
    tk, v = D.ticks_over(a, b)
    return clusters(tk, v, up_of(D, a, b) / 0.1, hp)   # D luôn dùng bước giá 0,1 (NQ đã chia 2,5 — xem prep1.py)


SCALE = {'gc': 1.0, 'nq': 2.5}
TICK_REAL = {'gc': 0.1, 'nq': 0.25}


def spans(D, kind):
    if kind == 'd': return [(a, b) for a, b in D.days if b - a + 1 >= 20]
    return [(a, b) for a, b in D.weeks if b - a + 1 >= 60]


def scan(sym):
    import pandas as pd
    import vung_manh as V
    D, vm = load(sym)
    for kind, ten in (('d', 'NGÀY'), ('w', 'TUẦN')):
        sp = spans(D, kind)
        print('\n## %s — profile %s (%d profile)' % (sym.upper(), ten, len(sp)))
        # HVN cũ
        nold, wold = [], []
        for a, b in sp:
            st = V.profile_stats(D, a, b)
            res, _ = vm.find_hvn(st['pr'], st['w'])
            top = [r for r in res[:3] if r[2] >= 2.5]
            nold.append(len(top))
            for i, pk, r in top:
                lo, hi = V.peak_sharpness(st['pr'], st['w'], i); wold.append((hi - lo) / up_of(D, a, b))
        print('HVN CŨ: %.2f/profile · %% profile có ≥ 1: %.0f · bề rộng (×up) p10/50/90: %s'
              % (np.mean(nold), 100 * np.mean(np.array(nold) >= 1), np.round(np.percentile(wold, [10, 50, 90]), 2).tolist() if wold else '—'))
        print('| SM | X | PK2 | Y | cụm/profile | % có 0 / 1 / 2 | bề rộng (×up) p10 / 50 / 90 | tỉ trọng p10 / 50 / 90 | rộng cụm ÷ rộng VA 70 % (trung vị) | % cụm nằm trọn trong VA |')
        print('|---|---|---|---|---|---|---|---|---|---|')
        combos = [(0.05, 0.7, 0.5, 0.10)]
        combos += [(s, 0.7, 0.5, 0.10) for s in (0.02, 0.03, 0.08, 0.12)]
        combos += [(0.05, x, 0.5, 0.10) for x in (0.5, 0.6, 0.8)]
        combos += [(0.05, 0.7, k, 0.10) for k in (0.4, 0.6, 0.7)]
        combos += [(0.05, 0.7, 0.5, y) for y in (0.0, 0.05, 0.15, 0.20)]
        for sm, x, pk2, y in combos:
            hp = dict(HP, SM=sm, X=x, PK2=pk2, Y=y)
            nc, wd, ms, rva, inva = [], [], [], [], []
            for a, b in sp:
                cl, _ = prof_clusters(D, a, b, hp)
                nc.append(len(cl))
                st = V.profile_stats(D, a, b); up = up_of(D, a, b)
                for c in cl:
                    lo, hi = c['lo'] * 0.1, c['hi'] * 0.1
                    wd.append((hi - lo) / up); ms.append(c['mass'])
                    rva.append((hi - lo) / max(st['vah'] - st['val'], 1e-9))
                    inva.append(lo >= st['val'] - 1e-9 and hi <= st['vah'] + 1e-9)
            nc = np.array(nc)
            print('| %.2f | %.1f | %.1f | %.2f | %.2f | %.0f / %.0f / %.0f | %s | %s | %.2f | %.0f |'
                  % (sm, x, pk2, y, nc.mean(), 100 * (nc == 0).mean(), 100 * (nc == 1).mean(), 100 * (nc >= 2).mean(),
                     ' / '.join('%.2f' % q for q in np.percentile(wd, [10, 50, 90])), ' / '.join('%.0f %%' % (100 * q) for q in np.percentile(ms, [10, 50, 90])),
                     np.median(rva), 100 * np.mean(inva)))


def find_day(D, date):
    import pandas as pd
    t = pd.to_datetime(D.m30['t'])
    for k, (a, b) in enumerate(D.days):
        if str(t[b])[:10] == date: return k
    raise SystemExit('không có phiên ' + date)


def ca(sym, date):
    import pandas as pd
    import vung_manh as V
    D, vm = load(sym)
    sc, t = SCALE[sym], pd.to_datetime(D.m30['t'])
    k = find_day(D, date)
    wk = int(D.week_of[D.days[k][0]])
    for ten, (a, b) in (('phiên', D.days[k]), ('tuần (tới hết phiên này)', (D.weeks[wk][0], D.days[k][1]))):
        st = V.profile_stats(D, a, b); up = up_of(D, a, b)
        print('\n%s %s: %s → %s · %d nến M30 · up = %.2f · thấp–cao %.2f–%.2f · POC hàng %.2f · VA %.2f–%.2f (rộng %.2f)'
              % (sym.upper(), ten, t[a], t[b], b - a + 1, up * sc, st['pr'][0] * sc, st['pr'][-1] * sc, st['poc'] * sc, st['val'] * sc, st['vah'] * sc, (st['vah'] - st['val']) * sc))
        res, _ = vm.find_hvn(st['pr'], st['w'])
        for i, pk, r in res[:3]:
            lo, hi = V.peak_sharpness(st['pr'], st['w'], i)
            print('   HVN CŨ : %.2f–%.2f (rộng %.2f = %.2f up) đỉnh %.2f ×%.2f %s' % (lo * sc, hi * sc, (hi - lo) * sc, (hi - lo) / up, pk * sc, r, '' if r >= 2.5 else '(dưới 2,5 — bị loại)'))
        for x in (0.5, 0.6, 0.7, 0.8):
            cl, ex = prof_clusters(D, a, b, dict(HP, X=x))
            for c in cl:
                lo, hi, pk = c['lo'] * 0.1 * sc, c['hi'] * 0.1 * sc, c['peak'] * 0.1 * sc
                print('   CỤM X=%.1f: %.2f–%.2f (rộng %.2f = %.2f up) đỉnh mượt %.2f (cách mép dưới %.0f %%) · tỉ trọng %.1f %% · cao %.2f đỉnh lớn nhất · h = ±%d bước giá'
                      % (x, lo, hi, hi - lo, (hi - lo) / sc / up, pk, 100 * (pk - lo) / max(hi - lo, 1e-9), 100 * c['mass'], c['rel'], ex['h']))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    cmd = sys.argv[1]
    if cmd == 'scan': scan(sys.argv[2])
    elif cmd == 'ca': ca(sys.argv[2], sys.argv[3])
    elif cmd == 've':
        import hvn_cum_ve; hvn_cum_ve.main(sys.argv[2:])
    elif cmd == 'fixture':
        import hvn_cum_fixture; hvn_cum_fixture.main()
