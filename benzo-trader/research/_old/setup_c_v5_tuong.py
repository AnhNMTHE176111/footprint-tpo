"""Setup C vong 3 - V5 'tuong limit' tai rau do (per-level cua chinh nen pha hut) va V5-nghich. CHI file 90d (QD-6).

Chay: python setup_c_v5_tuong.py [reps=200]  -> report/RESULTS-C.round3.md, roi ghep RESULTS-C.md (vong 3 + 2 + 1).

Tuong (wall) tai nen pha hut j, huong do d (+1 do len / -1 do xuong), cuc tri X = high (len) / low (xuong):
  muc = cac muc gia cua nen j trong <= 3 tick tinh tu X (len: price >= X-0,3 ; xuong: price <= X+0,3)
  (a) sum(volume muc) >= kV * trung vi volume/muc cua 50 nen TRUOC (gop top-3 muc dam nhat moi nen, giong OrderFlowBubbles)
  (b) delta nguoc chieu do (theo dung de bai): do len => sum(bid_vol) >= kD * sum(ask_vol) ; do xuong => sum(ask_vol) >= kD * sum(bid_vol)
      (them dieu kien tong ben 'nhieu' > 0 de khong thanh cong khi ca hai = 0).
Gio: bo 19:20-20:30 VN (sm 860..930) = LUAT GIO cua He thong muc 3.2, khong phai tham so.
V5: chi fade (vao tai close nen j, SL = rau, TP 2R co dinh / canh-POC>=2R) khi CO tuong.
V5-nghich: cung nen pha hut nhung KHONG co tuong => dat STOP ngoai rau (rau +-0,1), khop trong 10 nen sau, theo chieu PHA,
  SL = canh E lui vao trong 0,5u, TP 2R, tran SL 4 gia (giong _dissect3 cua agent chinh).
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv = sys.argv
sys.argv = ['x']
import kernel as K  # noqa: E402
import setup_c_fade_canh as C  # noqa: E402
sys.argv = _argv

EXCL = (860, 930)                       # 19:20-20:30 VN theo sm
GRID = [(1.5, 2.0), (1.5, 3.0), (2.0, 2.0), (2.0, 3.0)]   # (kV, kD)
BASE_KW = dict(pen_ticks=C.CENTER[0], min_width=C.CENTER[1])
f, pct, srow, HDR, closed, S = C.f, C.pct, C.srow, C.HDR, C.closed, C.S


class Wall:
    """Thong ke per-level quanh cuc tri rau cua tung nen (tinh theo nen, khong nhin truoc: chi dung nen j va 50 nen truoc j)."""

    def __init__(self, P, path):
        df = P['df']
        lv = K.load_levels(path)
        pos = pd.Index(df['bar_idx'].to_numpy()).get_indexer(lv['bar_idx'].to_numpy())
        ok = pos >= 0
        lv = lv[ok].copy()
        lv['pos'] = pos[ok]
        lv = lv.sort_values(['pos', 'price']).reset_index(drop=True)
        self.n = len(df)
        self.pos = lv['pos'].to_numpy()
        self.price = lv['price'].to_numpy(float)
        self.vol = lv['volume'].to_numpy(float)
        self.bid = lv['bid_vol'].to_numpy(float)
        self.ask = lv['ask_vol'].to_numpy(float)
        self.start = np.searchsorted(self.pos, np.arange(self.n + 1))
        # top-3 muc dam nhat moi nen
        t3 = np.zeros((self.n, 3))
        for j in range(self.n):
            a, b = self.start[j], self.start[j + 1]
            if b > a:
                v = np.sort(self.vol[a:b])[::-1][:3]
                t3[j, :len(v)] = v
        self.top3 = t3
        self.df = df
        self.hi = df['high'].to_numpy(float)
        self.lo = df['low'].to_numpy(float)
        self.cache = {}

    def stats(self, j, d):
        """(sum_vol, sum_bid, sum_ask, median_top3_50) quanh cuc tri; d=+1 do len."""
        k = (j, d)
        if k in self.cache:
            return self.cache[k]
        a, b = self.start[j], self.start[j + 1]
        pr = self.price[a:b]
        if d > 0:
            m = pr >= self.hi[j] - 0.3 - 1e-9
        else:
            m = pr <= self.lo[j] + 0.3 + 1e-9
        sv, sb, sa = self.vol[a:b][m].sum(), self.bid[a:b][m].sum(), self.ask[a:b][m].sum()
        seg = self.top3[max(0, j - 50):j]
        seg = seg[seg > 0]
        med = float(np.median(seg)) if (j >= 10 and len(seg) >= 30) else float('nan')
        r = (float(sv), float(sb), float(sa), med)
        self.cache[k] = r
        return r

    def wall(self, j, d, kV, kD, mirror=False):
        sv, sb, sa, med = self.stats(j, d)
        if med != med:
            return False
        if sv < kV * med:
            return False
        h, o = (sb, sa) if d > 0 else (sa, sb)       # h = ben 'ung ho tuong' theo de bai
        if mirror:
            h, o = o, h
        return bool(h > 0 and h >= kD * o)


def v5_entries(P, W, kV, kD, tp_mode, want_wall=True, mirror=False):
    gate = lambda i, j, side: W.wall(j, -side, kV, kD, mirror) == want_wall      # side=-1 (sell) <=> do len (d=+1)
    return C.detect(P['df'], P['zc'], P['mf'], mad=P['mad'], tp_mode=tp_mode, excl=EXCL, gate=gate, **BASE_KW)


def sim(P, ent):
    t = K.simulate(P['df'], ent)
    if len(t):
        t['half'] = 'NA'
    return t


def nghich(P, ent, rr=2.0, slk=0.5, expire=10):
    """Chuyen su kien fade (da qua loc 'khong tuong') thanh lenh stop theo chieu pha."""
    df, u = P['df'], P['u']
    hi, lo = df['high'].to_numpy(float), df['low'].to_numpy(float)
    out = []
    for e in ent:
        s = -int(e['side'])
        E = e['edge']
        i, j = int(e['idx']), int(e['poke_idx'])
        trig = (hi[j] + 0.1) if s > 0 else (lo[j] - 0.1)
        uu = float(u.iloc[i])
        if uu != uu:
            continue
        fill = None
        for q in range(i + 1, min(i + 1 + expire, len(df))):
            if (s > 0 and hi[q] >= trig) or (s < 0 and lo[q] <= trig):
                fill = q
                break
        if fill is None:
            continue
        sl = E - s * slk * uu
        d = (trig - sl) * s
        if d <= 0 or d > 4.0:
            continue
        out.append(dict(idx=int(fill), side=s, entry=round(trig, 6), sl=round(sl, 6), tp=round(trig + s * rr * d, 6), setup='C-nghich',
                        zone=e['zone'], edge=E, poke_idx=j, note='stop ngoai rau'))
    return out


def block(P, t, title, reps, ctrl=True):
    c = closed(t)
    L = ['### ' + title, '']
    if len(c) == 0:
        return L + ['Khong co lenh.', '']
    L += ['Lenh/ngay **%s** (%s)' % (f(S(t)['n'] / P['days'], 3), C.per_phase_day(t, P['days'])), '', HDR, srow('Tong', S(t))]
    for k in ('TRAIN', 'TEST'):
        L.append(srow(k, S(c[c['split'] == k])))
    L += [srow('phase ' + p, S(c[c['phase'] == p])) for p in K.PHASES]
    L += ['', '- ' + C.ci_txt(t, 'tong'), '- ' + C.ci_txt(t[t['split'] == 'TEST'], 'TEST'), '']
    if ctrl:
        L += [C.ctrl_md(C.control(P, t, reps)), '']
    return L


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 200
    P = C.prepare(C.D90)
    df = P['df']
    W = Wall(P, C.D90 + '.csv')
    L = ['# VONG 3 - Setup C: V5 "tuong limit" tai rau do + V5-nghich - CHI file 90d (QD-6)', '',
         'TRAIN <= 2026-09-15, TEST tu 2026-09-16; cung seed doi chung (%d lan); bootstrap 95%% 10.000 lan. Tuong dinh nghia o docstring `setup_c_v5_tuong.py`: '
         'muc <= 3 tick tu cuc tri rau; (a) tong volume >= kV x trung vi top-3-muc/nen cua 50 nen truoc; (b) delta ngu chieu do theo dung de bai '
         '(do len: sum bid >= kD x sum ask; do xuong: gương). **Bo 19:20-20:30 VN la luat gio cua He thong 3.2, khong phai tham so.** O khoi diem xuyen 2 tick, rong >= 6.' % reps, '']

    # ---------- A. Chan doan 121 lenh co ban (fixed2, khong bo gio) ----------
    ent0, t0 = C.run(P, **dict(BASE_KW, tp_mode='fixed2'))
    c0 = closed(t0)
    u = P['u']
    cls = []
    for e in c0.itertuples():
        if e.outcome != 'SL':
            cls.append('TP')
            continue
        after = df.iloc[int(e.exit_idx) + 1: int(e.exit_idx) + 21]
        uu = float(u.iloc[int(e.idx)])
        cls.append('PHA_THAT' if (((e.edge - after['close']) * int(e.side)) >= uu).any() else 'QUET')
    c0 = c0.assign(cls=cls)
    L += ['## A. Bai kiem tra co tach duoc 72 ca PHA THAT khong? (121 lenh co ban TP 2R, khong loc, chua bo gio 19:20-20:30)', '',
          'Co ban: n %d, SL %d (PHA THAT %d / QUET RAU %d), TP %d. Phan loai PHA THAT = trong 20 nen sau SL co nen dong ngoai canh E >= 1u (nhu agent chinh).' % (
              len(c0), (c0.outcome == 'SL').sum(), (c0.cls == 'PHA_THAT').sum(), (c0.cls == 'QUET').sum(), (c0.cls == 'TP').sum()), '',
          '| kV | kD | quy tac | co tuong: n | WR co tuong | SL co tuong | PHA_THAT co tuong / 72 | QUET co tuong / 16 | TP co tuong / 33 | khong tuong: n | WR khong tuong |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for mirror in (False, True):
        for kV, kD in GRID:
            wm = np.array([W.wall(int(e.poke_idx), -int(e.side), kV, kD, mirror) for e in c0.itertuples()])
            nw = ~wm
            def cnt(m, k): return int((m & (c0['cls'].to_numpy() == k)).sum())
            wr_w = float((c0['r'].to_numpy()[wm] > 0).mean()) if wm.any() else float('nan')
            wr_n = float((c0['r'].to_numpy()[nw] > 0).mean()) if nw.any() else float('nan')
            L.append('| %.1f | %.0f | %s | %d | %s | %d | %d | %d | %d | %d | %s |' % (
                kV, kD, 'dung de bai (do len: bid>=kD*ask)' if not mirror else 'GUONG (do len: ask>=kD*bid) - doi chung quy uoc', int(wm.sum()), pct(wr_w),
                cnt(wm, 'PHA_THAT') + cnt(wm, 'QUET'), cnt(wm, 'PHA_THAT'), cnt(wm, 'QUET'), cnt(wm, 'TP'), int(nw.sum()), pct(wr_n)))
    L += ['', '(cot "SL co tuong" = so lenh SL co tuong trong 88; cot PHA_THAT/QUET/TP tinh trong tung nhom 72/16/33. Dong GUONG la phep thu quy uoc bid/ask, khong phai de bai.)', '']

    # ---------- B. V5 ----------
    L += ['## B. V5: chi fade khi CO tuong (bo 19:20-20:30 VN)', '',
          'B1 = quy tac DUNG DE BAI (do len: bid >= kD x ask). Vi quy tac nay hiem (xem muc A), them B2 = quy tac GUONG (do len: ask >= kD x bid = lenh buy market bi limit sell hap thu) '
          'chay NGUYEN luoi 4 o, bao ca bang, de khong chon o dep. Tieu chuan ket luan chinh thuc ap cho B1; B2 ghi them.', '']
    cells = {False: [], True: []}
    for mirror in (False, True):
        L += ['## B%d. %s' % (2 if mirror else 1, 'V5 GUONG (ask >= kD x bid khi do len)' if mirror else 'V5 DUNG DE BAI (bid >= kD x ask khi do len)'), '']
        for kV, kD in GRID:
            for tm in ('fixed2', 'poc'):
                ent = v5_entries(P, W, kV, kD, tm, True, mirror)
                t = sim(P, ent)
                title = 'V5%s kV=%.1f kD=%.0f, TP %s' % ('-guong' if mirror else '', kV, kD, 'co dinh 2R' if tm == 'fixed2' else 'canh/POC >= 2R')
                L += block(P, t, title, reps, ctrl=(tm == 'fixed2'))
                ct = closed(t)
                tr = S(ct[ct['split'] == 'TRAIN']) if len(ct) else S(ct)
                te = S(ct[ct['split'] == 'TEST']) if len(ct) else S(ct)
                cells[mirror].append((title, S(t)['n'], tr['n'], tr['avg_r'], te['n'], te['avg_r']))
                print(title, flush=True)
    passed = False
    for mirror in (False, True):
        L += ['### Luoi V5%s (tong hop)' % (' GUONG' if mirror else ' DUNG DE BAI'), '', '| o | n | n TRAIN | R TB TRAIN | n TEST | R TB TEST | dat (R TRAIN>0, R TEST>0, n TEST>=20)? |', '|---|---|---|---|---|---|---|']
        for t_, n, ntr, rtr, nte, rte in cells[mirror]:
            ok = nte >= 20 and rtr == rtr and rte == rte and rtr > 0 and rte > 0
            if not mirror:
                passed |= ok
            L.append('| %s | %d | %d | %s | %d | %s | %s |' % (t_, n, ntr, f(rtr), nte, f(rte), 'CO' if ok else 'khong'))
        L += ['']
    # fade khong tuong (kiem tra: bo loc co tach gi khong)
    L += ['### Doi chieu: fade khi KHONG co tuong (quy tac de bai, kV=2,0 kD=2, TP 2R co dinh, bo 19:20-20:30)', '']
    en = v5_entries(P, W, 2.0, 2.0, 'fixed2', False)
    L += block(P, sim(P, en), 'fade khong tuong', reps, ctrl=False)

    # ---------- C. V5-nghich ----------
    L += ['## C. V5-nghich: cung nen pha hut nhung KHONG co tuong => stop ngoai rau, SL = E lui vao 0,5u, TP 2R, het han 10 nen (bo 19:20-20:30)', '']
    nres = []
    for kV, kD in GRID:
        en = v5_entries(P, W, kV, kD, 'fixed2', False)
        ee = nghich(P, en)
        t = sim(P, ee)
        title = 'V5-nghich (khong tuong: kV=%.1f kD=%.0f)' % (kV, kD)
        L += block(P, t, title, reps, ctrl=False)
        ct = closed(t)
        tr = S(ct[ct['split'] == 'TRAIN']) if len(ct) else S(ct)
        te = S(ct[ct['split'] == 'TEST']) if len(ct) else S(ct)
        nres.append((title, S(t)['n'], tr['n'], tr['avg_r'], te['n'], te['avg_r']))
    # tham chieu: ban tho khong loc per-level, co bo gio
    en = C.detect(df, P['zc'], P['mf'], mad=P['mad'], tp_mode='fixed2', excl=EXCL, **BASE_KW)
    L += block(P, sim(P, nghich(P, en)), 'V5-nghich ban tho (khong loc tuong, bo 19:20-20:30) - tham chieu', reps, ctrl=False)
    L += ['### Tong hop V5-nghich', '', '| o | n | n TRAIN | R TB TRAIN | n TEST | R TB TEST |', '|---|---|---|---|---|---|']
    for t_, n, ntr, rtr, nte, rte in nres:
        L.append('| %s | %d | %d | %s | %d | %s |' % (t_, n, ntr, f(rtr), nte, f(rte)))
    L += ['']

    # ---------- D. Ket luan ----------
    L += ['## D. Ket luan vong 3', '',
          ('**Co o V5 dat tieu chuan (R TB duong ca TRAIN va TEST, n TEST >= 20): xem luoi tong hop, can kiem KTC bootstrap truoc khi tin.**' if passed else
           '**Khong o V5 nao duong ca TRAIN lan TEST voi n TEST >= 20 => ket luan cuoi: C tat mac dinh.**'), '']
    ev = os.path.join(HERE, 'report', 'RESULTS-C.round3.danhgia.md')
    if os.path.exists(ev):
        L += [open(ev, encoding='utf-8').read()]
    with open(os.path.join(HERE, 'report', 'RESULTS-C.round3.md'), 'w', encoding='utf-8') as fh:
        fh.write(chr(10).join(L) + chr(10))
    C.compose()
    print('xong')


if __name__ == '__main__':
    main()
