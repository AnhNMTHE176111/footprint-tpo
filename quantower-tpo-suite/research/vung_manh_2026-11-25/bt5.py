#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bt5.py — backtest "tại MỘT thời điểm bất kỳ" của SessionZones (vùng mạnh + hộp HVN + vùng đệm), 5 vòng cải tiến.

Cách chấm (Opus, 2026-11-25):
  1. Mỗi nến M30 j vừa đóng → chạy đúng bản tham chiếu (vung_manh.Engine + display + hvn_boxes) với giá đóng của j
     ⇒ danh sách vùng / hộp ĐANG ĐƯỢC VẼ trong suốt nến M30 j+1 (như indicator, độc lập khung chart).
  2. Trên nến M1 của các nến M30 mà vùng đang được vẽ: một LẦN QUAY LẠI = giá vào "dải tiếp cận" (mép gần ± TRIG × U
     phía ngoài) sau khi đã ở xa mép >= AWAY × U (lần sau: REARM × U). Phía tiếp cận = phía giá đứng trước đó.
  3. Điểm đảo = cực trị chạy tại lúc giá bật ngược >= B × U. depth = (mép gần − điểm đảo) theo hướng đi tới, đơn vị U:
     âm = đảo TRƯỚC khi chạm vùng; 0..rộng = đảo trong vùng; > rộng + 0,25 = phá.
  4. Lệnh limit ở mép gần (và ở mép gần nới ra e × U), dừng lỗ = mép xa + SLP × U, chốt 1R / 2R, tối đa HOR nến M1.
  5. Đối chứng: cùng vùng dời ± 1,5–4 U (3 bản), cùng thời gian được vẽ, cùng cách chấm.
  6. Lý do đảo sớm: điểm đảo trùng (± 0,10 U) râu/đỉnh-đáy M30 cũ, vùng/hộp/đệm khác đang vẽ, cao/thấp hôm qua,
     số tròn — so tỉ lệ với đối chứng (đối chứng cũng "trùng" ngẫu nhiên).

  python bt5.py run nqy|gc [VONG]     → <đệm>/bt5_<sym>_<VONG>.pkl
  python bt5.py bang nqy|gc [VONG ...] → bảng so sánh (TRAIN = 60 % phiên đầu, TEST = 40 % sau)
"""
import os, sys, pickle, zlib, tempfile, importlib
import numpy as np
import pandas as pd

CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())
TRIG, AWAY, REARM, B, SLP, HOR, NSH = 0.6, 1.25, 1.0, float(os.environ.get('BT5_B', 1.0)), float(os.environ.get('BT5_SLP', 0.15)), 1380, 3
EXTS = (0.0, 0.1, 0.2, 0.3)
TOLR = 0.10                       # "trùng" khi cách <= 0,10 U
ROUND = {'nqy': 50 / 2.5, 'nq': 50 / 2.5, 'gc': 10.0}      # số tròn: NQ 50 điểm, GC 10 USD (giá đã chia SCALE)

# ---------------- các vòng (biến thể thuật toán) ----------------
# mỗi vòng = dict ghi đè: P (thông số vung_manh), ZEXT (nới mép gần vùng mạnh × U), BOX_EDGE ('hop' | 'dem'),
# WICK (nới vùng mạnh tới râu M30 cũ), ...
VONG = {
    'v0': dict(),
    'v1': dict(PAD_B=0.2),                       # vòng 1: hộp HVN có dải chờ 0,2 U phía giá
    'v3a': dict(PAD_B=0.2, P=dict(HVN_AWAY=3.0), zones_post=lambda D, eng, zs, j, p: [z for z in zs if z['hvn']]),
    'v3b': dict(PAD_B=0.2, P=dict(HVN_AWAY=4.0), zones_post=lambda D, eng, zs, j, p: [z for z in zs if z['hvn']]),
    'v3c': dict(PAD_B=0.2, P=dict(HVN_AWAY=5.0), zones_post=lambda D, eng, zs, j, p: [z for z in zs if z['hvn']]),
    'v3d': dict(PAD_B=0.2, P=dict(HVN_AWAY=6.0), zones_post=lambda D, eng, zs, j, p: [z for z in zs if z['hvn']]),
    'v4a': dict(PAD_B=0.2, P=dict(HVN_AWAY=4.0, HVN_DAYS=3), zones_post=lambda D, eng, zs, j, p: [z for z in zs if z['hvn']]),
    'v4b': dict(PAD_B=0.2, P=dict(HVN_AWAY=4.0, HVN_DAYS=8), zones_post=lambda D, eng, zs, j, p: [z for z in zs if z['hvn']]),
    'v5': dict(PAD_B=0.2, P=dict(HVN_AWAY=4.0), zones_post=lambda D, eng, zs, j, p: [z for z in zs if z['hvn']]),   # chốt = v3b
    'moi': dict(PAD_B=0.2, P=dict(HVN_AWAY=4.0, REQ_HVN=True)),   # kiểm: mặc định MỚI của vung_manh.P cho ra y hệt v5
    'v2': dict(PAD_B=0.2, zones_post=lambda D, eng, zs, j, p: [z for z in zs if z['hvn']]),   # vòng 2: vùng mạnh bắt buộc hợp lưu HVN
}


def load(sym):
    import vung_dem_lib as L
    D, vm, V = L.load(sym)
    if sym == 'gc':                       # một hợp đồng GCZ26: indicator tự tắt bộ chặn chỗ nối
        vm.SPLICE_JUMP = 1e12
        D = vm.Data(cache=os.environ['VM_CACHE'])
    return D, vm, V


def snapshots(D, V, cfg):
    """{khoá: obj} — obj: kind 'z' (vùng mạnh) | 'b' (hộp HVN), lo, hi, blo, bhi, vis (list nến M30 được vẽ), thuộc tính."""
    # gốc = thuật toán TRƯỚC 5 vòng (HVN rời xa 2 U, vùng mạnh không bắt buộc HVN); vòng nào đổi thì ghi đè trong P
    p = dict(V.P, HVN_MODE='cum2', HVN_HL='giao', D_ONLY=False, HVN_AWAY=2.0, REQ_HVN=False, HVN_BAND=0.0)
    p.update(cfg.get('P', {}))
    eng = V.Engine(D, p)
    if 'zone_hook' in cfg: cfg['zone_hook'](D, V, eng, p)
    objs = {}
    j0 = D.days[min(6, len(D.days) - 1)][0]
    for j in range(j0, D.n - 1):
        if not np.isfinite(D.U[j + 1]): continue
        now = float(D.m30['c'][j])
        zs = eng.zones(j)
        if 'zones_post' in cfg: zs = cfg['zones_post'](D, eng, zs, j, p)
        shown = V.display(D, zs, j, now, p)
        gmap = {(round(float(g['price'].min()), 6), round(float(g['price'].max()), 6)): g for g in eng._clusters}
        for z in shown:
            g = gmap.get((round(float(z['pmin']), 6), round(float(z['pmax']), 6)))
            z['blo'], z['bhi'] = wick_ext(D, g, z['lo'], z['hi'], z['u'], cfg.get('WICK_CAP', 0.5), cfg.get('WICK_Q', 50))
        d = int(D.day_of[j + 1]); lv = eng.levels(d)
        full = {(L_['name'], L_['end'], L_['lo'], L_['hi']): L_ for L_ in lv if L_['name'].startswith('hvn')}
        boxes = V.hvn_boxes(D, lv, j, now, p)
        for z in shown:
            k = ('z', round(z['lo'], 4), round(z['hi'], 4))
            o = objs.setdefault(k, dict(kind='z', lo=z['lo'], hi=z['hi'], blo=z.get('blo', z['lo']), bhi=z.get('bhi', z['hi']), vis=[],
                                        gold=z['gold'], ngroup=z['ngroup'], n=z['n'], hvn=z['hvn'], names=tuple(z['names']),
                                        first=j + 1))
            o['vis'].append(j + 1)
        for b in boxes:
            Lf = full.get((b['name'], b['end'], b['lo'], b['hi']), {})
            k = ('b', b['name'], b['end'], b['lo'], b['hi'])
            o = objs.setdefault(k, dict(kind='b', lo=b['lo'], hi=b['hi'], blo=Lf.get('blo', b['lo']), bhi=Lf.get('bhi', b['hi']), vis=[],
                                        name=b['name'], mass=b['mass'], both=(b['label'] == 'HVN ngày + tuần'), first=j + 1))
            o['vis'].append(j + 1)
    return objs, eng


def wick_ext(D, g, lo, hi, u, cap, q):
    """Phần RÂU của các lần va đập cũ: hỗ trợ (dùng các đáy) → mép trên nới tới phân vị q của đáy thân nến (min(o,c));
    kháng cự (các đỉnh) → mép dưới nới tới phân vị (100 − q) của đỉnh thân nến (max(o,c)). Tối đa cap × U."""
    if g is None: return lo, hi
    o, c = D.m30['o'], D.m30['c']
    lows = g['idx'][g['kind'] < 0]; highs = g['idx'][g['kind'] > 0]
    bhi, blo = hi, lo
    if len(lows):
        bb = np.minimum(o[lows], c[lows])
        bhi = min(max(hi, float(np.percentile(bb, q))), hi + cap * u)
    if len(highs):
        bt = np.maximum(o[highs], c[highs])
        blo = max(min(lo, float(np.percentile(bt, 100 - q))), lo - cap * u)
    return blo, bhi


def turn_and_trades(D, i0, side, u, lo, hi, offb=0.0, slo=None, shi=None):
    """Cực trị / điểm đảo + lệnh limit ở mép gần nới e×U. side +1 = hỗ trợ (đi xuống chạm), −1 = kháng cự."""
    H, Lw, C = D._H, D._L, D._C
    N = len(H)
    end = min(N, i0 + HOR)
    ext = Lw[i0] if side > 0 else H[i0]; iE = i0; kT = None
    for k in range(i0, end):
        if side > 0:
            if Lw[k] < ext: ext, iE = Lw[k], k
            if (H[k] - ext >= B * u and k > iE) or (k == iE and C[k] - ext >= B * u): kT = k; break
        else:
            if H[k] > ext: ext, iE = H[k], k
            if (ext - Lw[k] >= B * u and k > iE) or (k == iE and ext - C[k] >= B * u): kT = k; break
    win_end = kT if kT is not None else end - 1
    near = hi if side > 0 else lo
    far = (lo if slo is None else slo) if side > 0 else (hi if shi is None else shi)
    stop = far - side * SLP * u
    res = {}
    for e in EXTS + ('b',):
        entry = near + side * (offb if e == 'b' else e * u)
        f = None
        for k in range(i0, win_end + 1):
            if (side > 0 and Lw[k] <= entry) or (side < 0 and H[k] >= entry): f = k; break
        if f is None: res[e] = (0, np.nan, np.nan); continue
        R = abs(entry - stop)
        out = {}
        for tgt in (1.0, 2.0):
            tp = entry + side * tgt * R
            r = None
            for k in range(f, min(N, f + HOR)):
                hs = (Lw[k] <= stop) if side > 0 else (H[k] >= stop)
                ht = (H[k] >= tp) if side > 0 else (Lw[k] <= tp)
                if k == f:            # nến khớp lệnh: chỉ tính lỗ nếu chạm dừng (không biết thứ tự trong nến) — thận trọng
                    if hs: r = -1.0; break
                    if ht and ((C[k] - entry) * side >= tgt * R): r = tgt; break
                    continue
                if hs: r = -1.0; break
                if ht: r = tgt; break
            if r is None:
                k = min(N, f + HOR) - 1
                r = (C[k] - entry) * side / R
            out[tgt] = r
        res[e] = (1, out[1.0], out[2.0])
    depth = ((near - ext) if side > 0 else (ext - near)) / u
    return dict(ext=ext, iE=iE, done=kT is not None, depth=depth, tr=res)


def scan(D, o, lo0, hi0, pad=0.0):
    """pad (× U): dải chờ vẽ thêm ngoài hộp/vùng — mép gần = mép vùng ± pad × U; dừng lỗ vẫn tính từ mép xa của vùng gốc."""
    vis = o['vis']; vs = set(vis)
    i30 = D._i30; U = D.U
    s0 = int(D.m1_ptr[vis[0]]); s1 = int(D.m1_ptr[vis[-1] + 1])
    H, Lw = D._H, D._L
    ev = []
    state, away, need = 0, 0.0, AWAY
    for i in range(s0, s1):
        j30 = i30[i]; u = U[j30]
        lo, hi = lo0 - pad * u, hi0 + pad * u
        zl, zh = lo - TRIG * u, hi + TRIG * u
        if Lw[i] > zh:
            if state != 1: state, away = 1, 0.0
            away = max(away, (H[i] - hi) / u)
        elif H[i] < zl:
            if state != -1: state, away = -1, 0.0
            away = max(away, (lo - Lw[i]) / u)
        else:
            if state != 0 and away >= need and j30 in vs:
                offb = (o['bhi'] - o['hi']) if state > 0 else (o['lo'] - o['blo'])
                r = turn_and_trades(D, i, state, u, lo, hi, max(0.0, offb - pad * u), lo0, hi0)
                r['w'] = (hi - lo) / u
                r.update(i0=i, side=state, u=u, j30=j30, first=(need == AWAY), age=j30 - o['first'])
                ev.append(r)
            if state != 0: need = REARM
            state, away = 0, 0.0
    return ev


def context(D, eng, objs_by_j, i, side, u, ext, self_key):
    """Lý do có thể của điểm đảo ext (giá đã chia SCALE)."""
    j30 = int(D._i30[i])
    tol = TOLR * u
    r = {}
    # râu / đỉnh-đáy M30 cũ đã xác nhận (pivot) trong 5 phiên trước, cùng loại (đáy nếu hỗ trợ)
    pv = eng.pv
    d = int(D.day_of[j30]); a = D.days[max(0, d - 5)][0]
    m = (pv['conf'] < j30) & (pv['idx'] >= a) & (pv['kind'] == (-1 if side > 0 else 1))
    r['pivot'] = bool(np.any(np.abs(pv['price'][m] - ext) <= tol))
    # mọi cực trị M30 (râu) trong 5 phiên trước, không cần bật 1U
    hl = D.m30['l'][a:j30] if side > 0 else D.m30['h'][a:j30]
    r['rau'] = bool(np.any(np.abs(hl - ext) <= tol)) if len(hl) else False
    # vùng / hộp / đệm khác đang vẽ
    oth = False
    for k, o in objs_by_j.get(j30, []):
        if k == self_key: continue
        if o['blo'] - tol <= ext <= o['bhi'] + tol: oth = True; break
    r['vung_khac'] = oth
    # cao / thấp phiên trước, mở cửa phiên
    if d >= 1:
        ya, yb = D.days[d - 1]
        r['hl_homqua'] = bool(min(abs(D.m30['h'][ya:yb + 1].max() - ext), abs(D.m30['l'][ya:yb + 1].min() - ext)) <= tol)
    else:
        r['hl_homqua'] = False
    rn = ROUND[D._sym]
    r['so_tron'] = bool(abs(ext - np.round(ext / rn) * rn) <= tol)
    # VWAP đang chạy của phiên hiện tại
    da = D.days[d][0]
    if j30 > da:
        mu, _ = D.vwap_sigma(da, j30 - 1)
        r['vwap_nay'] = bool(np.isfinite(mu) and abs(mu - ext) <= tol)
    else:
        r['vwap_nay'] = False
    return r


def feats(D, i0, side, u):
    """Bối cảnh lúc giá vào dải: tốc độ đi tới (30 / 120 nến M1, × U, dương = đang lao về vùng), giá so VWAP phiên
    đang chạy (× U, dương = phía 'đúng' của lệnh: hỗ trợ mà giá trên VWAP), giờ UTC."""
    C = D._C
    sp30 = (C[max(0, i0 - 30)] - C[i0]) * side / u
    sp120 = (C[max(0, i0 - 120)] - C[i0]) * side / u
    j30 = D._i30[i0]; d = int(D.day_of[j30]); da = D.days[d][0]
    mu = D.vwap_sigma(da, j30 - 1)[0] if j30 > da else np.nan
    vw = (C[i0] - mu) * side / u if np.isfinite(mu) else np.nan
    hr = pd.Timestamp(D.m1['t'][i0]).hour
    return dict(sp30=sp30, sp120=sp120, vw=vw, hour=hr)


def run(sym, vong):
    D, vm, V = load(sym)
    D._sym = sym
    D._H, D._L, D._C = D.m1['h'].tolist(), D.m1['l'].tolist(), D.m1['c'].tolist()
    D._i30 = D.m1['i30'].tolist()
    cfg = VONG[vong]
    objs, eng = snapshots(D, V, cfg)
    objs_by_j = {}
    for k, o in objs.items():
        for j in o['vis']: objs_by_j.setdefault(j, []).append((k, o))
    print(sym, vong, 'vật thể:', len(objs), ' vùng mạnh', sum(o['kind'] == 'z' for o in objs.values()),
          ' hộp', sum(o['kind'] == 'b' for o in objs.values()), flush=True)
    rows = []
    for k, o in objs.items():
        variants = [('that', 0.0, -1)]
        u_ref = D.U[o['vis'][0]]
        for rep in range(NSH):
            rs = np.random.RandomState(zlib.crc32(repr((k, rep)).encode()) & 0x7fffffff)
            variants.append(('doi', float(rs.choice([-1, 1]) * rs.uniform(1.5, 4.0) * u_ref), rep))
        for typ, dl, rep in variants:
            edge_lo, edge_hi = o['lo'] + dl, o['hi'] + dl
            if cfg.get('BOX_EDGE') == 'dem' and o['kind'] == 'b':
                edge_lo, edge_hi = o['blo'] + dl, o['bhi'] + dl
            pad = cfg.get('PAD_B', 0.0) if o['kind'] == 'b' else cfg.get('PAD_Z', 0.0)
            for e in scan(D, o, edge_lo, edge_hi, pad):
                e.update(typ=typ, rep=rep, key=k, kind=o['kind'], lo=edge_lo, hi=edge_hi,
                         gold=o.get('gold', False), ngroup=o.get('ngroup', 0), hvn=o.get('hvn', False), npv=o.get('n', 0),
                         names=o.get('names', ()), bname=o.get('name', ''), both=o.get('both', False),
                         blo=o['blo'] + dl, bhi=o['bhi'] + dl, t0=D.m1['t'][e['i0']], day=int(D.day_of[e['j30']]))
                e.update(context(D, eng, objs_by_j, e['iE'], e['side'], e['u'], e['ext'], k if typ == 'that' else None))
                e.update(feats(D, e['i0'], e['side'], e['u']))
                rows.append(e)
    # gộp trùng: cùng typ/rep/kind/phía/điểm đảo, vùng chồng > 50 % ⇒ giữ lần vào dải sớm nhất
    rows.sort(key=lambda e: (e['i0'], e['kind']))
    keep = []
    seen = {}
    for e in rows:
        sk = (e['typ'], e['rep'], e['kind'], e['side'], e['iE'])
        dup = False
        for k2 in seen.get(sk, []):
            inter = min(k2['hi'], e['hi']) - max(k2['lo'], e['lo']); small = min(k2['hi'] - k2['lo'], e['hi'] - e['lo'])
            if inter > 0.5 * small: dup = True; break
        if not dup:
            keep.append(e); seen.setdefault(sk, []).append(e)
    df = pd.DataFrame([{kk: vv for kk, vv in e.items() if kk != 'tr'} for e in keep])
    for ex in EXTS + ('b',):
        df['fill%s' % (ex if ex == 'b' else '%g' % ex)] = [e['tr'][ex][0] for e in keep]
        nm = ex if ex == 'b' else '%g' % ex
        df['r1_%s' % nm] = [e['tr'][ex][1] for e in keep]
        df['r2_%s' % nm] = [e['tr'][ex][2] for e in keep]
    nd = len(D.days)
    df['tap'] = np.where(df['day'] < int(nd * 0.6), 'TRAIN', 'TEST')
    sfx = os.environ.get('BT5_SFX', '')
    df.to_pickle(os.path.join(CDIR, 'bt5_%s_%s%s.pkl' % (sym, vong, sfx)))
    # độ ổn định: số lần một vùng bật/tắt
    flick = []
    for o in objs.values():
        v = np.array(o['vis']); flick.append(int((np.diff(v) > 1).sum()))
    with open(os.path.join(CDIR, 'bt5_%s_%s_objs.pkl' % (sym, vong)), 'wb') as f:
        pickle.dump(dict(objs=objs, flick=flick, ndays=nd), f, protocol=4)
    print('sự kiện thật', int((df['typ'] == 'that').sum()), ' đối chứng', int((df['typ'] == 'doi').sum()))


def cls(df):
    w = df['w']
    c = np.where(~df['done'], 'chua_xong', np.where(df['depth'] < 0, 'som', np.where(df['depth'] <= w + 0.25, 'trong', 'pha')))
    return pd.Series(c, index=df.index)


def summary(df, label=''):
    out = []
    for typ in ('that', 'doi'):
        g = df[df['typ'] == typ]
        if len(g) == 0: continue
        c = cls(g)
        row = dict(nhom=label, typ=typ, n=len(g))
        for k in ('som', 'trong', 'pha', 'chua_xong'): row[k] = (c == k).mean() * 100
        row['som_gan'] = ((g['depth'] < 0) & (g['depth'] >= -0.3)).mean() * 100
        for ex in EXTS:
            f = g['fill%g' % ex] == 1
            row['khop%g' % ex] = f.mean() * 100
            row['R1_%g' % ex] = g.loc[f, 'r1_%g' % ex].mean()
            row['R2_%g' % ex] = g.loc[f, 'r2_%g' % ex].mean()
            row['tong2_%g' % ex] = g.loc[f, 'r2_%g' % ex].sum()
        out.append(row)
    return out


def boot_delta(df, col, B_=1000, seed=3):
    """Khoảng 5–95 % của (thật − đối chứng) theo phiên (bootstrap theo ngày)."""
    rs = np.random.RandomState(seed)
    days = df['day'].unique()
    by = {d: g for d, g in df.groupby('day')}
    vals = []
    for _ in range(B_):
        s = pd.concat([by[d] for d in rs.choice(days, len(days))])
        a = s.loc[s['typ'] == 'that', col].mean(); b = s.loc[s['typ'] == 'doi', col].mean()
        vals.append(a - b)
    return np.nanpercentile(vals, [5, 95])


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    cmd, sym = sys.argv[1], sys.argv[2]
    if cmd == 'run':
        run(sym, sys.argv[3] if len(sys.argv) > 3 else 'v0')
