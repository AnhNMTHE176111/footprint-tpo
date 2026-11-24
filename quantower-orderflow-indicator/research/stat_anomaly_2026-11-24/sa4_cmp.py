"""So từng dấu Python (sa3_ref.py --marks) với C# (Golden.dll stophunt --marks).

python sa4_cmp.py <dấu Python> <dấu C#> <tick> [--kinds dotS,dotB,bt]

Khóa so: (giờ nến 'yyyy-MM-dd HH:mm', loại dotS / dotB / bt, làm tròn(giá / tick)). Bỏ các loại dấu khác (exhT, exhB...).
In số dấu từng loại hai bên, số dấu chỉ có ở một bên và 10 dấu lệch đầu tiên. Thoát 0 khi trùng hết."""
import sys, argparse, csv
from collections import Counter


def load(path, tick, kinds):
    c = Counter()
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['kind'] not in kinds: continue
            c[(r['t'], r['kind'], int(round(float(r['price']) / tick)))] += 1
    return c


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('py'); ap.add_argument('cs'); ap.add_argument('tick', type=float)
    ap.add_argument('--kinds', default='dotS,dotB,bt')
    a = ap.parse_args(argv)
    kinds = set(a.kinds.split(','))
    P = load(a.py, a.tick, kinds); C = load(a.cs, a.tick, kinds)
    def per(cn): return {k: sum(v for kk, v in cn.items() if kk[1] == k) for k in sorted(kinds)}
    only_p = P - C; only_c = C - P
    print('Python:', per(P), '| C#:', per(C))
    print(f'chi co o Python: {sum(only_p.values())}, chi co o C#: {sum(only_c.values())}')
    diffs = sorted([('py',) + k for k in only_p] + [('cs',) + k for k in only_c], key=lambda x: (x[1], x[2], x[3]))
    for d in diffs[:10]: print('  lech', d)
    ok = not only_p and not only_c
    print('TRUNG TUNG DAU' if ok else 'LECH')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
