# -*- coding: utf-8 -*-
"""So bộ vùng của C# (VclCore qua tools/ReplayCsv) với engine Python v4 (vcl4.py) TỪNG NẾN.
Khớp một nến = cùng số vùng, sắp theo lo thì từng cặp lệch lo/hi ≤ 0,05 giá và cùng vai (R/RF/S/SF/K).
Chạy:  python3 parity_vcl.py [cs.csv]   (không đưa file ⇒ tự build + chạy ReplayCsv)  → report/PARITY-VCL.md"""
import os, sys, subprocess, time
import numpy as np
import pandas as pd
import vcl as V

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
TOL = 0.05


def role_py(r):
    if r['slot'] == 'K':
        return 'K'
    return ('R' if r['side'] == 1 else 'S') + ('F' if r['slot'] == 'F' else '')


def main():
    t0 = time.time()
    if len(sys.argv) > 1:
        cs_path = sys.argv[1]
    else:
        cs_path = os.path.join(HERE, 'report', 'vcl_cs_replay.csv')
        env = dict(os.environ, PATH=os.path.expanduser('~/.dotnet') + ':' + os.environ['PATH'], DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_NOLOGO='1')
        subprocess.run(['dotnet', 'run', '-c', 'Release', '--project', os.path.join(ROOT, 'tools', 'ReplayCsv'), '--', V.BASE, cs_path],
                       check=True, env=env)
    cs = pd.read_csv(cs_path)
    path = os.path.join(HERE, 'report', 'vcl4_records.csv.gz')
    if os.path.exists(path):
        py = pd.read_csv(path)
    else:
        import vcl4
        b, l = V.load_all()
        py = vcl4.run_engine(V.prepare(b, l))['rec']
    py['role'] = [role_py(r) for r in py[['slot', 'side']].to_dict('records')]
    n = int(max(py['bar'].max(), cs['bar_idx'].max())) + 1
    gp = {k: g.sort_values('lo') for k, g in py.groupby('bar')}
    gc = {k: g.sort_values('lo') for k, g in cs.groupby('bar_idx')}
    bars = sorted(set(gp) | set(gc))
    ok = 0
    bad = []
    max_dlo = 0.0
    ids_same = True
    for b in bars:
        a, c = gp.get(b), gc.get(b)
        if a is None or c is None:
            bad.append((b, 'chỉ một bên có vùng', a, c))
            continue
        if len(a) != len(c):
            bad.append((b, f'số vùng {len(a)} (Py) ≠ {len(c)} (C#)', a, c))
            continue
        dl = np.abs(a['lo'].to_numpy() - c['lo'].to_numpy())
        dh = np.abs(a['hi'].to_numpy() - c['hi'].to_numpy())
        same_role = (a['role'].to_numpy() == c['role'].to_numpy()).all()
        if (dl <= TOL).all() and (dh <= TOL).all() and same_role:
            ok += 1
            ids_same = ids_same and (a['eid'].to_numpy() == c['zone_id'].to_numpy()).all()
            max_dlo = max(max_dlo, dl.max(), dh.max())
        else:
            bad.append((b, 'lo/hi lệch' if same_role else 'khác vai', a, c))
    rate = ok / len(bars)
    md = ['# Parity Vùng Canh Lệnh: C# (VclCore) ↔ Python (vcl4.py)', '',
          f'File: `{os.path.basename(V.BASE)}` ({n} nến). So từng nến có vùng hiển thị ở ít nhất một bên: **{len(bars)} nến**.',
          f'Khớp (cùng số vùng, lo/hi lệch ≤ {TOL} giá, cùng vai): **{ok} / {len(bars)} = {100 * rate:.3f}%** (yêu cầu ≥ 99%).',
          f'Lệch lo/hi lớn nhất trong các nến khớp: {max_dlo:.2e} giá. Mã vùng (ID) cũng được so: '
          f'{"trùng hết" if ids_same else "KHÔNG trùng hết"} ở các nến khớp.', '']
    if bad:
        md += [f'## {len(bad)} nến lệch — {min(10, len(bad))} ca đầu', '']
        for b, why, a, c in bad[:10]:
            md.append(f'- nến {b}: {why}')
            if a is not None:
                md.append('  - Py: ' + '; '.join(f"{r.role} {r.lo:.2f}–{r.hi:.2f}" for r in a.itertuples()))
            if c is not None:
                md.append('  - C#: ' + '; '.join(f"{r.role} {r.lo:.2f}–{r.hi:.2f}" for r in c.itertuples()))
        md.append('')
    else:
        md += ['Không có nến nào lệch.', '']
    md += ['<!-- NGUYEN-NHAN -->', '']
    out = os.path.join(HERE, 'report', 'PARITY-VCL.md')
    old = open(out, encoding='utf-8').read() if os.path.exists(out) else ''
    tail = old.split('<!-- NGUYEN-NHAN -->', 1)[1] if '<!-- NGUYEN-NHAN -->' in old else '\n## Nguyên nhân / ghi chú\n(chưa viết)\n'
    open(out, 'w', encoding='utf-8').write('\n'.join(md[:-2]) + '\n<!-- NGUYEN-NHAN -->' + tail)
    print('\n'.join(md))
    print(f'({time.time() - t0:.0f}s)')


if __name__ == '__main__':
    main()
