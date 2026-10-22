# -*- coding: utf-8 -*-
"""Parity C# (VclCore qua tools/ReplayCsv) ↔ Python (vcl5.py + lan_cham.py), TỪNG NẾN, trên file 90 ngày (nguồn chính) và file 29 ngày.
(1) Bộ vùng: khớp một nến = cùng số vùng, sắp theo lo thì từng cặp lệch lo/hi ≤ 0,05 giá, cùng vai (R/RF/S/SF/K); mã vùng cũng so.
(2) Lần chạm: trạng thái mỗi vùng mỗi nến (đang mở, vai, đếm thoát, lịch sử n/đảo/xuyên/chưa rõ/không rõ phía) và DANH SÁCH mọi lần chạm
    đã chốt (mã vùng, nến bắt đầu, nến chốt, vai, kết cục) — gồm cả ca chốt do vùng rời bộ / hết phiên.
Chạy:  python3 parity_vcl.py   (tự build + chạy ReplayCsv; engine Python lấy từ report/cache_lc nếu có)  → report/PARITY-VCL.md"""
import os, sys, subprocess, time, pickle
import numpy as np
import pandas as pd
import vcl5 as V5
import lan_cham as LC

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
TOL = 0.05
TR_COLS = ['ep_open', 'ep_vai', 'dem_thoat', 'n', 'dao', 'xuyen', 'chua_ro', 'khong_ro']


def role_py(slot, side):
    if slot == 'K':
        return 'K'
    return ('R' if side == 1 else 'S') + ('F' if slot == 'F' else '')


def py_rec(name, base):
    path = os.path.join(LC.CACHE, name + '.pkl')
    bars, lv = V5.load(base)
    ctx = V5.prepare(bars, lv)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            rec = pickle.load(f)['rec']
    else:
        rec = V5.run_engine(ctx)['rec']
    return ctx, rec.reset_index(drop=True)


def one(name, base, env):
    t0 = time.time()
    cs_path = os.path.join(HERE, 'report', f'vcl5_cs_replay_{name}.csv')
    subprocess.run(['dotnet', 'run', '-c', 'Release', '--project', os.path.join(ROOT, 'tools', 'ReplayCsv'), '--', base, cs_path], check=True, env=env)
    cs = pd.read_csv(cs_path)
    cse = pd.read_csv(cs_path[:-4] + '_episodes.csv')
    ctx, py = py_rec(name, base)
    py['role'] = [role_py(a, b) for a, b in zip(py['slot'].to_numpy(), py['side'].to_numpy())]
    # ---- (1) bộ vùng
    gp = {k: g.sort_values('lo') for k, g in py.groupby('bar')}
    gc = {k: g.sort_values('lo') for k, g in cs.groupby('bar_idx')}
    bars = sorted(set(gp) | set(gc))
    ok, bad, max_d, ids_same = 0, [], 0.0, True
    for b in bars:
        a, c = gp.get(b), gc.get(b)
        if a is None or c is None or len(a) != len(c):
            bad.append(b)
            continue
        dl = np.abs(a['lo'].to_numpy() - c['lo'].to_numpy())
        dh = np.abs(a['hi'].to_numpy() - c['hi'].to_numpy())
        if (dl <= TOL).all() and (dh <= TOL).all() and (a['role'].to_numpy() == c['role'].to_numpy()).all():
            ok += 1
            ids_same &= bool((a['eid'].to_numpy() == c['zone_id'].to_numpy()).all())
            max_d = max(max_d, dl.max(), dh.max())
        else:
            bad.append(b)
    # ---- (2) lần chạm
    B = LC.bar_arrays(ctx['df'])
    ep, r, tr = LC.episodes(B, py, trace=True)
    pt = pd.DataFrame({'bar_idx': r['bar'].to_numpy(), 'zone_id': r['eid'].to_numpy(), **{k: tr[k] for k in TR_COLS}})
    m = pt.merge(cs[['bar_idx', 'zone_id'] + TR_COLS], on=['bar_idx', 'zone_id'], how='outer', suffixes=('_py', '_cs'), indicator=True)
    both = m['_merge'] == 'both'
    eq = np.ones(len(m), bool)
    for k in TR_COLS:
        eq &= (m[k + '_py'] == m[k + '_cs']).to_numpy()
    row_ok = int((both & eq).sum())
    pe = ep[ep['ket'] != LC.HDL][['eid', 'bat_dau', 'chot', 'vai', 'ket']].rename(columns={'eid': 'zone_id'})
    key = ['zone_id', 'bat_dau', 'chot', 'vai', 'ket']
    a_ = set(map(tuple, pe[key].to_numpy().tolist()))
    c_ = set(map(tuple, cse[key].to_numpy().tolist()))
    # theo từng mã vùng: số lần chạm / đảo / xuyên
    def per_zone(d):
        g = d.groupby('zone_id')['ket']
        return pd.DataFrame({'n': g.size(), 'dao': g.apply(lambda x: (x == 0).sum()), 'xuyen': g.apply(lambda x: (x == 1).sum())})
    zp, zc = per_zone(pe), per_zone(cse)
    zall = zp.join(zc, how='outer', lsuffix='_py', rsuffix='_cs').fillna(-1)
    zok = int(((zall['n_py'] == zall['n_cs']) & (zall['dao_py'] == zall['dao_cs']) & (zall['xuyen_py'] == zall['xuyen_cs'])).sum())
    return dict(name=name, base=os.path.basename(base), n=len(ctx['df']), bars=len(bars), ok=ok, bad=bad, max_d=max_d, ids_same=ids_same,
                rows=len(m), row_ok=row_ok, only=int((~both).sum()), ep_py=len(a_), ep_cs=len(c_), ep_common=len(a_ & c_),
                zones=len(zall), zok=zok, sec=time.time() - t0)


def main():
    env = dict(os.environ, PATH=os.path.expanduser('~/.dotnet') + ':' + os.environ['PATH'], DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_NOLOGO='1')
    res = [one('v5', V5.BASE90, env), one('v5_29d', V5.BASE29, env)]
    md = ['# Parity Vùng Canh Lệnh: C# (VclCore) ↔ Python (vcl5.py + lan_cham.py)', '',
          'Yêu cầu: bộ vùng khớp ≥ 99% số nến VÀ lần chạm khớp (trạng thái từng nến + danh sách lần chạm đã chốt + đếm theo từng mã vùng).', '']
    for x in res:
        md += [f"## `{x['base']}` ({x['n']} nến)", '',
               f"- **Bộ vùng:** khớp {x['ok']} / {x['bars']} nến = **{100 * x['ok'] / x['bars']:.3f}%** (lo/hi lệch ≤ {TOL} giá, cùng vai). "
               f"Lệch lớn nhất {x['max_d']:.2e} giá. Mã vùng {'trùng hết' if x['ids_same'] else 'KHÔNG trùng hết'}." +
               (f" Nến lệch đầu tiên: {x['bad'][:5]}" if x['bad'] else ''),
               f"- **Trạng thái lần chạm từng vùng × nến:** {x['row_ok']} / {x['rows']} dòng = **{100 * x['row_ok'] / max(x['rows'], 1):.3f}%** "
               f"(dòng chỉ có ở một bên: {x['only']}).",
               f"- **Danh sách lần chạm đã chốt** (mã vùng, nến bắt đầu, nến chốt, vai, kết cục): Python {x['ep_py']}, C# {x['ep_cs']}, trùng "
               f"**{x['ep_common']}** ({100 * x['ep_common'] / max(x['ep_py'], 1):.3f}%).",
               f"- **Theo từng mã vùng** (số lần chạm / đảo / xuyên): khớp {x['zok']} / {x['zones']} mã = **{100 * x['zok'] / max(x['zones'], 1):.3f}%**.",
               f"- Thời gian {x['sec']:.0f}s.", '']
    md += ['<!-- NGUYEN-NHAN -->', '']
    out = os.path.join(HERE, 'report', 'PARITY-VCL.md')
    old = open(out, encoding='utf-8').read() if os.path.exists(out) else ''
    tail = old.split('<!-- NGUYEN-NHAN -->', 1)[1] if '<!-- NGUYEN-NHAN -->' in old else '\n## Ghi chú\n(chưa viết)\n'
    open(out, 'w', encoding='utf-8').write('\n'.join(md[:-2]) + '\n<!-- NGUYEN-NHAN -->' + tail)
    print('\n'.join(md))


if __name__ == '__main__':
    main()
