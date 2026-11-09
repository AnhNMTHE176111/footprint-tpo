# -*- coding: utf-8 -*-
"""
parity_of_signals.py — đối chiếu of_signals.py (Python) với mã C# sản phẩm (StackedImbalance.cs, ExhaustionLogic.cs)
trên các nến TRAIN của file chuẩn 90d (plan BENZO-CORVEN GĐ0, mục 2: "Python phải khớp 100 %").

Chạy:  PYTHONIOENCODING=utf-8 python parity_of_signals.py [--no-build]
  1. dotnet run tools/OfSignalsDump (C#) → CSV các vùng stacked (3 cấu hình) + kiệt sức, kèm Follow/IsSwept 300 nến sau
  2. Python tính đúng các dòng đó bằng of_signals
  3. so từng dòng (khoá = loại + cấu hình + nến + phía), in số khớp/lệch và 10 dòng lệch đầu
Kết quả ghi report/PARITY-OF-SIGNALS.md.
"""
from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import of_signals as OF          # noqa: E402
import setup_corven as SC        # noqa: E402

TOOL = os.path.join(os.path.dirname(HERE), 'tools', 'OfSignalsDump')
CFGS = [('250_3_1', 250, 3, 1), ('250_4_5', 250, 4, 5), ('300_3_1', 300, 3, 1)]
HORIZON = 300
T = 0.1


def R(x: float) -> str:
    return 'inf' if x == float('inf') else repr(float(x))


def python_rows(prefix: str, cut: int):
    # nến: đọc giá thô bằng float() (round-trip, như double.Parse của C#)
    oP, hP, lP, cP = [], [], [], []
    with open(prefix + '_bars.csv', newline='', encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd)
        for row in rd:
            bi = int(row[0])
            if bi > cut:
                break
            oP.append(float(row[2])); hP.append(float(row[3])); lP.append(float(row[4])); cP.append(float(row[5]))
    n = len(oP)
    o = [round(x / T) for x in oP]; h = [round(x / T) for x in hP]; l = [round(x / T) for x in lP]; c = [round(x / T) for x in cP]
    lv = [[] for _ in range(n)]
    with open(prefix + '.csv', newline='', encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd)
        for row in rd:
            bi = int(row[0])
            if bi > cut:
                break
            lv[bi].append((round(float(row[2]) / T), float(row[3]), float(row[4]), float(row[5])))
    rows = {}
    ex = OF.ExhSettings()
    for i in range(n):
        if h[i] > l[i]:
            m = h[i] - l[i] + 1
            ask = [0.0] * m; bid = [0.0] * m
            for (k, b, a, v) in lv[i]:
                if l[i] <= k <= h[i]:
                    ask[k - l[i]] += a; bid[k - l[i]] += b
            after = [(hP[j], lP[j], cP[j]) for j in range(i + 1, min(n, i + HORIZON + 1))]
            for (name, pct, run, mv) in CFGS:
                for z in OF.detect_stacked(l[i] * T, T, ask, bid, pct, run, mv):
                    OF.classify(z, oP[i], cP[i])
                    ft = OF.follow(z.side, z.lo, z.hi, after, OF.MODE_TOUCH, 0)
                    fc = OF.follow(z.side, z.lo, z.hi, after, OF.MODE_CLOSE, 0)
                    key = ('Z', name, i, z.side, z.lo_idx)
                    rows[key] = [z.lo_idx, z.hi_idx, R(z.lo), R(z.hi), z.levels, R(z.min_ratio), R(z.dom_volume),
                                 R(z.opp_volume), z.position, int(z.weak), ft[0], ft[1], fc[0], fc[1]]
        for top in (True, False):
            r = OF.detect_exhaustion(top, o[i], h[i], l[i], c[i], lv[i], ex)
            if not r.hit:
                continue
            swept = -1
            for j in range(i + 1, min(n, i + HORIZON + 1)):
                if OF.is_swept(r.top, r.tick, h[j], l[j], 1):
                    swept = j - i
                    break
            rows[('E', i, int(top))] = [r.kind, r.tick, R(r.extreme_vol), R(r.mean_level_vol),
                                         ';'.join(R(x) for x in r.seq), swept]
    return n, rows


def cs_rows(path: str):
    rows = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            p = line.rstrip('\n').split(',')
            if p[0] == 'Z':
                name, i, side, lo_idx = p[1], int(p[2]), int(p[3]), int(p[4])
                vals = [int(p[4]), int(p[5]), p[6], p[7], int(p[8]), p[9], p[10], p[11], int(p[12]), int(p[13]),
                        int(p[14]), int(p[15]), int(p[16]), int(p[17])]
                rows[('Z', name, i, side, lo_idx)] = vals
            elif p[0] == 'E':
                rows[('E', int(p[1]), int(p[2]))] = [int(p[3]), int(p[4]), p[5], p[6], p[7], int(p[8])]
    return rows


def _norm(v):
    """So số thực theo GIÁ TRỊ (chuỗi 'R' của C# và repr của Python đều round-trip; '1' vs '1.0' cùng giá trị)."""
    out = []
    for x in v:
        if isinstance(x, str) and x != '' and ';' not in x:
            out.append(float(x))
        elif isinstance(x, str) and ';' in x:
            out.append(tuple(float(y) for y in x.split(';')))
        else:
            out.append(x)
    return out


def main():
    prefix = SC.D90
    cut = SC.train_cut(prefix)
    out = os.path.join(tempfile.gettempdir(), 'of_signals_cs.csv')
    if '--no-build' not in sys.argv or not os.path.exists(out):
        cmd = ['dotnet', 'run', '--project', TOOL, '-c', 'Release', '--', prefix + '.csv', prefix + '_bars.csv', str(cut), out]
        print(' '.join(cmd))
        subprocess.run(cmd, check=True)
    cs = cs_rows(out)
    n, py = python_rows(prefix, cut)
    keys = set(cs) | set(py)
    only_cs = [k for k in keys if k in cs and k not in py]
    only_py = [k for k in keys if k in py and k not in cs]
    diff = [k for k in keys if k in cs and k in py and _norm(cs[k]) != _norm(py[k])]
    cnt = {}
    for k in py:
        g = k[0] + ('_' + k[1] if k[0] == 'Z' else ('_dinh' if k[2] == 1 else '_day'))
        cnt[g] = cnt.get(g, 0) + 1
    ok = not only_cs and not only_py and not diff
    lines = [
        '# Parity of_signals.py ↔ C# (StackedImbalance.cs + ExhaustionLogic.cs) — GĐ0',
        '',
        f'- Dữ liệu: `fp_GCZ26_XCEC_Time_20260723-20261021_90d` — **{n} nến** bar_idx 0…{cut} (toàn bộ TRAIN, không đụng TEST).',
        '- C#: `benzo-trader/tools/OfSignalsDump` biên dịch thẳng 2 file nguồn sản phẩm (không sửa dòng nào).',
        '- So từng dòng: vùng stacked (Lo/Hi, số mức, tỷ lệ yếu nhất, volume 2 bên, vị trí, Weak, Follow chế độ Touch và',
        '  CloseThrough 300 nến sau) ở 3 cấu hình (250 %/3/1 = plan, 250 %/4/5, 300 %/3/1); kiệt sức đỉnh/đáy (loại, mức,',
        '  volume cực trị, TB/mức, chuỗi tooltip, nến đầu tiên bị râu quét qua ≤ 300 nến).',
        '',
        '| Nhóm | Số dòng Python |',
        '|---|---|',
    ] + [f'| {g} | {v} |' for g, v in sorted(cnt.items())] + [
        '',
        f'- Tổng dòng: C# {len(cs)} · Python {len(py)} · chỉ có ở C# **{len(only_cs)}** · chỉ có ở Python **{len(only_py)}** · '
        f'khác giá trị **{len(diff)}**.',
        f'- **Kết luận: {"KHỚP 100 %" if ok else "CÓ LỆCH"}.**',
    ]
    if not ok:
        lines += ['', '10 dòng lệch đầu:', '']
        for k in (sorted(only_cs)[:5] + sorted(only_py)[:5] + sorted(diff)[:10])[:10]:
            lines.append(f'- `{k}` C#={cs.get(k)} Py={py.get(k)}')
    txt = '\n'.join(lines) + '\n'
    with open(os.path.join(HERE, 'report', 'PARITY-OF-SIGNALS.md'), 'w', encoding='utf-8') as f:
        f.write(txt)
    print(txt)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
