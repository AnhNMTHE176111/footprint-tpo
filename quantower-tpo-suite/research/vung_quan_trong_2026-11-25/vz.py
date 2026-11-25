#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vz.py — ĐO PHẢN ỨNG CỦA GIÁ TẠI VÙNG (không lệnh, không R). Opus, 2026-11-25.

Tại MỖI nến M30 j vừa đóng: một "cách vẽ" (builder) trả danh sách vùng {lo, hi, tag, ...} chỉ dùng dữ liệu tới j.
Vùng coi như hiện suốt nến M30 j+1. Chỉ xét vùng có mép gần cách giá đóng j ≤ RAD × U.

Trên nến M1 của các nến M30 vùng đang hiện:
  LẦN QUAY LẠI = giá vào dải TRIG × U ngoài mép gần, sau khi đã cách mép ≥ AWAY × U (lần sau ≥ REARM × U).
  ĐIỂM ĐẢO     = cực trị chạy tại lúc giá bật ngược ≥ B × U (tối đa HOR nến M1; không bật đủ = "phá").
  Phân loại theo vị trí điểm đảo so với vùng (dung sai TOL × U):
     TẠI VÙNG  : lo − tol ≤ điểm đảo ≤ hi + tol
     SỚM       : quay đầu trước mép gần quá tol
     PHÁ       : đi quá mép xa quá tol, hoặc không bật đủ B × U
ĐỐI CHỨNG: cùng vùng (cùng bề rộng) dời ± 1,5–4 U, 3 bản; với builder có "nới theo râu" thì dời LÕI rồi chạy lại đúng
luật nới tại chỗ mới (hàm builder nhận tham số dời) ⇒ đối chứng công bằng.
Chỉ số chính: Δ tại vùng = %TẠI VÙNG(thật) − %TẠI VÙNG(đối chứng); khoảng 5–95 % bootstrap theo phiên.
Phụ: ĐỘ PHỦ ĐIỂM ĐẢO LỚN = % đỉnh/đáy M30 (bật ≥ 1,5 U) nằm trong một vùng đã vẽ TRƯỚC nó, thật vs đối chứng.
"""
import os, sys, pickle, zlib, tempfile, importlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'vung_manh_2026-11-25'))
CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())
TRIG, AWAY, REARM, TOL, HOR, NSH, RAD = 0.6, 1.25, 1.0, 0.10, 1380, 3, 6.0
B = float(os.environ.get('VZ_B', 1.0))      # biên độ bật để coi là 'đảo' (× U)


def load(sym):
    os.environ['VM_CACHE'] = os.path.join(CDIR, 'vm1_%s.pkl' % sym)
    import vm
    importlib.reload(vm)
    vm.SPLICE_JUMP = 1e12              # một hợp đồng (NQZ26 / GCZ26): indicator tự tắt bộ chặn chỗ nối
    D = vm.Data(cache=os.environ['VM_CACHE'])
    if sym.startswith('nq'):           # NQ lưu giá /2,5; hàng profile = 2 bước giá thật (như vung_dem_lib)
        def rows_over_nq(self, a, b, row=vm.ROW):
            tk, v = self.ticks_over(a, b)
            if len(tk) == 0: return np.array([]), np.array([])
            rid = np.round((tk * 0.25) / 0.5).astype(np.int64)
            u, inv = np.unique(rid, return_inverse=True)
            return u * row, np.bincount(inv, weights=v)
        type(D).rows_over = rows_over_nq
    import vung_manh as V
    importlib.reload(V)
    D._sym = sym
    D._H, D._L, D._C = D.m1['h'].tolist(), D.m1['l'].tolist(), D.m1['c'].tolist()
    D._i30 = D.m1['i30'].tolist()
    return D, V


# ------------------------------------------------------------------ chạy một builder
def snapshots(D, builder, dl_fn=None):
    """builder(j, dl) → list vùng (dl = độ dời lõi, 0 = thật). Trả {khoá: obj(vis=[nến M30 hiện])}.
    Với đối chứng: dl_fn(key0, rep) cho độ dời cố định theo vùng thật; builder được gọi lại với dl."""
    objs = {}
    j0 = D.days[min(6, len(D.days) - 1)][0]
    for j in range(j0, D.n - 1):
        u = D.U[j + 1]
        if not np.isfinite(u): continue
        now = float(D.m30['c'][j])
        for z in builder(j, 0.0):
            dist = now - z['hi'] if now > z['hi'] else z['lo'] - now if now < z['lo'] else 0.0
            if dist > RAD * u: continue
            k = (z['tag'], round(z['lo'], 4), round(z['hi'], 4))
            o = objs.setdefault(k, dict(z, vis=[], first=j + 1, u0=u))
            o['vis'].append(j + 1)
    return objs


def turn(D, i0, side, u):
    H, Lw, C = D._H, D._L, D._C
    N = len(H); end = min(N, i0 + HOR)
    ext = Lw[i0] if side > 0 else H[i0]; iE = i0
    for k in range(i0, end):
        if side > 0:
            if Lw[k] < ext: ext, iE = Lw[k], k
            if (H[k] - ext >= B * u and k > iE) or (k == iE and C[k] - ext >= B * u): return ext, iE, True
        else:
            if H[k] > ext: ext, iE = H[k], k
            if (ext - Lw[k] >= B * u and k > iE) or (k == iE and ext - C[k] >= B * u): return ext, iE, True
    return ext, iE, False


def scan(D, vis, lo, hi):
    vs = set(vis); i30 = D._i30; U = D.U; H, Lw = D._H, D._L
    s0 = int(D.m1_ptr[vis[0]]); s1 = int(D.m1_ptr[vis[-1] + 1])
    ev = []; state, away, need = 0, 0.0, AWAY
    for i in range(s0, s1):
        j30 = i30[i]; u = U[j30]
        if Lw[i] > hi + TRIG * u:
            if state != 1: state, away = 1, 0.0
            away = max(away, (H[i] - hi) / u)
        elif H[i] < lo - TRIG * u:
            if state != -1: state, away = -1, 0.0
            away = max(away, (lo - Lw[i]) / u)
        else:
            if state != 0 and away >= need and j30 in vs:
                ext, iE, done = turn(D, i, state, u)
                near = hi if state > 0 else lo
                depth = ((near - ext) if state > 0 else (ext - near)) / u       # âm = chưa tới mép gần
                w = (hi - lo) / u
                c = 'pha' if not done else ('som' if depth < -TOL else ('tai' if depth <= w + TOL else 'pha'))
                ev.append(dict(i0=i, iE=iE, side=state, u=u, j30=j30, depth=depth, w=w, cls=c, first=(need == AWAY), away=away))
            if state != 0: need = REARM
            state, away = 0, 0.0
    return ev


def run(D, builder, name, shift_core=True):
    """Thật + đối chứng. shift_core=True: đối chứng gọi builder(j, dl) (dời lõi rồi nới lại tại chỗ mới);
    False: dời nguyên vùng thật."""
    objs = snapshots(D, builder)
    rows = []
    for k, o in objs.items():
        variants = [('that', 0.0, -1)]
        for rep in range(NSH):
            rs = np.random.RandomState(zlib.crc32(repr((k[0], round(k[1], 2), rep)).encode()) & 0x7fffffff)
            variants.append(('doi', float(rs.choice([-1, 1]) * rs.uniform(1.5, 4.0) * o['u0']), rep))
        for typ, dl, rep in variants:
            if typ == 'that' or not shift_core:
                lo, hi = o['lo'] + dl, o['hi'] + dl
            else:
                lo, hi = shifted_zone(D, builder, o, dl)
                if lo is None: continue
            for e in scan(D, o['vis'], lo, hi):
                e.update(typ=typ, rep=rep, key=k, tag=o['tag'], lo=lo, hi=hi, day=int(D.day_of[e['j30']]),
                         **{a: o[a] for a in o if a.startswith('a_')})
                rows.append(e)
    rows.sort(key=lambda e: (e['i0'], e['tag']))
    keep, seen = [], {}
    for e in rows:
        sk = (e['typ'], e['rep'], e['tag'], e['side'], e['iE'])
        if any(min(k2['hi'], e['hi']) - max(k2['lo'], e['lo']) > 0.5 * min(k2['hi'] - k2['lo'], e['hi'] - e['lo']) for k2 in seen.get(sk, [])): continue
        keep.append(e); seen.setdefault(sk, []).append(e)
    df = pd.DataFrame(keep)
    if len(df):
        nd = len(D.days)
        df['tap'] = np.where(df['day'] < int(nd * 0.6), 'TRAIN', 'TEST')
        df['sym'] = D._sym
    rec = recall(D, objs, builder, shift_core)
    name += os.environ.get('VZ_SFX', '')
    with open(os.path.join(CDIR, 'vz_%s_%s.pkl' % (D._sym, name)), 'wb') as f:
        pickle.dump(dict(df=df, rec=rec, nobj=len(objs), width=np.mean([o['hi'] - o['lo'] for o in objs.values()]) / np.nanmean(D.U) if objs else np.nan), f, protocol=4)
    return df, rec


_shift_cache = {}


def shifted_zone(D, builder, o, dl):
    """Vùng đối chứng: gọi builder tại nến xuất hiện đầu tiên với lõi dời dl, lấy vùng cùng tag gần (lõi thật + dl) nhất."""
    j = o['first'] - 1
    key = (id(builder), j, round(dl, 6))
    if key not in _shift_cache:
        if len(_shift_cache) > 20000: _shift_cache.clear()
        _shift_cache[key] = builder(j, dl)
    cand = [z for z in _shift_cache[key] if z['tag'] == o['tag'] and z.get('core') is not None]
    if o.get('core') is None: return o['lo'] + dl, o['hi'] + dl      # vùng không có lõi (vd vùng quét) ⇒ dời nguyên
    tgt = (o['core'][0] + o['core'][1]) / 2 + dl if o.get('core') else (o['lo'] + o['hi']) / 2 + dl
    if not cand: return None, None          # lõi dời không qua được luật (vd không có râu xác nhận) ⇒ không có vùng đối chứng
    z = min(cand, key=lambda z: abs((z['core'][0] + z['core'][1]) / 2 - tgt))
    if abs((z['core'][0] + z['core'][1]) / 2 - tgt) > 1e-6: return None, None
    return z['lo'], z['hi']


def recall(D, objs, builder, shift_core):
    """Độ phủ điểm đảo lớn: đỉnh/đáy M30 (k = 2, bật ≥ 1,5 U trong 6 nến) — có vùng nào hiện ở nến đó chứa giá đỉnh/đáy (± TOL)?"""
    import vm
    pv = vm.pivots(D, k=2, m=6, r=1.5)
    by_j = {}
    for k, o in objs.items():
        for j in o['vis']: by_j.setdefault(j, []).append(o)
    hit = np.zeros(len(pv), bool); hitc = np.zeros((len(pv), NSH), bool); ok = np.zeros(len(pv), bool)
    for n, (i, conf, price, kind) in enumerate(pv):
        if i not in by_j: continue
        u = D.U[i]; tol = TOL * u; ok[n] = True
        for o in by_j[i]:
            if o['lo'] - tol <= price <= o['hi'] + tol: hit[n] = True
            for rep in range(NSH):
                rs = np.random.RandomState(zlib.crc32(repr((o['tag'], round(o['lo'], 2), rep)).encode()) & 0x7fffffff)
                dl = float(rs.choice([-1, 1]) * rs.uniform(1.5, 4.0) * o['u0'])
                if o['lo'] + dl - tol <= price <= o['hi'] + dl + tol: hitc[n, rep] = True
    day = D.day_of[pv['idx']]
    return dict(n=int(ok.sum()), hit=hit[ok], hitc=hitc[ok], day=day[ok])


# ------------------------------------------------------------------ bảng
def cls_rates(g):
    return {c: (g['cls'] == c).mean() * 100 for c in ('tai', 'som', 'pha')}


def boot(df, B_=500, seed=3):
    by = {d: (x[x.typ == 'that']['cls'].eq('tai').values, x[x.typ == 'doi']['cls'].eq('tai').values) for d, x in df.groupby(['sym', 'day'])}
    keys = list(by); rs = np.random.RandomState(seed); out = []
    for _ in range(B_):
        ks = [keys[i] for i in rs.randint(0, len(keys), len(keys))]
        a = np.concatenate([by[k][0] for k in ks]); b = np.concatenate([by[k][1] for k in ks])
        if len(a) and len(b): out.append((a.mean() - b.mean()) * 100)
    return np.percentile(out, [5, 95]) if out else (np.nan, np.nan)


def table(names, tags=None, title=''):
    """names: list (nhãn, tên bộ kết quả). In bảng NQ TRAIN / NQ TEST / GC / gộp."""
    print('\n### ' + title)
    print('| cách vẽ | rộng TB (U) | n thật | NQ TRAIN Δ tại vùng | NQ TEST Δ | GC Δ | **gộp: tại vùng thật / đ.c / Δ [5–95 %]** | sớm thật / đ.c | phá thật / đ.c | độ phủ điểm đảo lớn thật / đ.c |')
    print('|' + '---|' * 10)
    for lab, nm in names:
        dfs, recs, wid, = [], [], []
        for s in ('nqy', 'gc'):
            p = os.path.join(CDIR, 'vz_%s_%s.pkl' % (s, nm))
            if not os.path.exists(p): continue
            r = pickle.load(open(p, 'rb'))
            if len(r['df']): dfs.append(r['df'])
            recs.append(r['rec']); wid.append(r['width'])
        if not dfs: print('| %s | — |' % lab); continue
        df = pd.concat(dfs, ignore_index=True)
        if tags: df = df[df.tag.isin(tags)]
        def d(m):
            g = df[m]; a = g[g.typ == 'that']; b = g[g.typ == 'doi']
            if len(a) < 5: return '—'
            return '%+.1f (n %d)' % ((a.cls.eq('tai').mean() - b.cls.eq('tai').mean()) * 100, len(a))
        a = df[df.typ == 'that']; b = df[df.typ == 'doi']
        ra, rb = cls_rates(a), cls_rates(b); lo, hi = boot(df)
        h = np.concatenate([r['hit'] for r in recs]); hc = np.concatenate([r['hitc'] for r in recs]) if recs else np.zeros((0, NSH))
        print('| %s | %.2f | %d | %s | %s | %s | %.1f / %.1f / **%+.1f** [%+.1f, %+.1f] | %.0f / %.0f | %.0f / %.0f | %.1f / %.1f |' % (
            lab, np.nanmean(wid), len(a), d((df.sym == 'nqy') & (df.tap == 'TRAIN')), d((df.sym == 'nqy') & (df.tap == 'TEST')), d(df.sym == 'gc'),
            ra['tai'], rb['tai'], ra['tai'] - rb['tai'], lo, hi, ra['som'], rb['som'], ra['pha'], rb['pha'], h.mean() * 100, hc.mean() * 100))
