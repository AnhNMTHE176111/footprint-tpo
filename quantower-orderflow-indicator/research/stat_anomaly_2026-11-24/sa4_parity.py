"""Chạy toàn bộ bảng so C# = Python của SPEC.md mục 9 / 10.2 (chế độ "Không theo CORVEN (thống kê)").

python sa4_parity.py [--only <tên dòng>]   (chạy từ thư mục gốc repo hoặc bất kỳ đâu)

Với mỗi dòng: chạy `Golden.dll stophunt ... --set ThresholdMode=1 [--set ...] --marks <dấu C#>`, đọc số chấm đỏ / xanh / Big,
rồi so từng dấu với dấu Python của sa3_ref.py (file marks_r3_* đã có trong thư mục tạm; mức 0,5% thì chạy sa3_ref.py lấy số trước).
Ghi out_sa4_parity.csv. Kiểm sha1 file footprint / nhật ký với out_r3_chuan.csv trước khi so."""
import os, sys, re, csv, hashlib, subprocess, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
T = r'C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad'
G = os.path.join(ROOT, 'quantower-orderflow-indicator', 'perf', 'Golden', 'bin', 'Release', 'net10.0-windows', 'Golden.dll')
OUT = os.path.join(T, 'sa4')
TICK = {'GC': 0.1, 'NQ': 0.25}


def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def rows():
    R = []
    for ma in ('GC', 'NQ'):
        for k in (1, 5, 15, 60):
            fp = os.path.join(T, 'tf', f'fp_{ma}_m{k}.csv')
            R.append((f'{ma}_m{k}_mac_dinh', ma, k, fp, [], os.path.join(T, f'marks_r3_{ma}_m{k}_nen_moi.csv'), None, None))
            R.append((f'{ma}_m{k}_1pt', ma, k, fp, ['StatRarePbp=100'], os.path.join(T, f'marks_r3_{ma}_m{k}_p1.csv'), None, None))
            R.append((f'{ma}_m{k}_khong_lan_can', ma, k, fp, ['StatDotNeighbors=false'], os.path.join(T, f'marks_r3_{ma}_m{k}_khong_lan_can.csv'), None, None))
    R.append(('GC_m5_moi_muc_gia', 'GC', 5, os.path.join(T, 'tf', 'fp_GC_m5.csv'), ['CellDotAllLevels=true'], os.path.join(T, 'marks_r3_GC_m5_sel_all.csv'), None, None))
    R.append(('NQ_m15_moi_muc_gia', 'NQ', 15, os.path.join(T, 'tf', 'fp_NQ_m15.csv'), ['CellDotAllLevels=true'], os.path.join(T, 'marks_r3_NQ_m15_sel_all.csv'), None, None))
    R.append(('GC_m5_nap8', 'GC', 5, os.path.join(T, 'tf', 'fp_GC_m5_nap8.csv'), [], os.path.join(T, 'marks_r3_GC_m5_nap8ngay.csv'), None, None))
    R.append(('NQ_m15_nap8', 'NQ', 15, os.path.join(T, 'tf', 'fp_NQ_m15_nap8.csv'), [], os.path.join(T, 'marks_r3_NQ_m15_nap8ngay.csv'), None, None))
    for ma, k in (('GC', 5), ('NQ', 15)):
        fp = os.path.join(T, 'tf', f'fp_{ma}_m{k}.csv')
        R.append((f'{ma}_m{k}_0.5pt', ma, k, fp, ['StatRarePbp=50'], os.path.join(OUT, f'marks_r4_{ma}_m{k}_p05.csv'), ['pbp=50'], None))
    for ma, k in (('NQ', 1), ('NQ', 15), ('GC', 5), ('GC', 30)):
        fp = os.path.join(T, 'tf', f'fp_{ma}_m{k}.csv')
        R.append((f'bt_{ma}_M{k}', ma, k, fp, [], os.path.join(T, f'marks_r3_bt_{ma}_M{k}.csv'), None, os.path.join(T, f'btlog_{ma}_M{k}.csv')))
    return R


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--only'); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    chuan = {}
    with open(os.path.join(HERE, 'out_r3_chuan.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            chuan[os.path.basename(r['file_footprint'])] = r['sha1_footprint']
            if r['file_btlog']: chuan[os.path.basename(r['file_btlog'])] = r['sha1_btlog']
    res = []
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    for name, ma, k, fp, sets, pymarks, pyset, btlog in rows():
        if a.only and a.only != name: continue
        for p in (fp, btlog):
            if p and os.path.basename(p) in chuan and chuan[os.path.basename(p)] and sha1(p) != chuan[os.path.basename(p)]:
                print('SAI sha1', p); sys.exit(2)
        tick = TICK[ma]
        if pyset is not None:   # mức 0,5%: chạy Python lấy số
            cmd = [sys.executable, os.path.join(HERE, 'sa3_ref.py'), fp, str(k), str(tick), '--set', 'bt=0'] + sum((['--set', s] for s in pyset), []) + ['--marks', pymarks]
            print('  py:', subprocess.run(cmd, capture_output=True, text=True, env=env, encoding='utf-8').stdout.strip())
        csm = os.path.join(OUT, f'cs_{name}.csv')
        cmd = ['dotnet', G, 'stophunt', '--tick', str(tick), '--minutes', str(k), '--levels', fp, '--work', os.path.join(OUT, 'w_' + name), '--zeromot', '--marks', csm, '--set', 'ThresholdMode=1']
        if ma == 'NQ': cmd[5:5] = ['--symbol', 'NQZ26']
        if btlog: cmd += ['--btlog', btlog]
        for s in sets: cmd += ['--set', s]
        out = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8').stdout
        m = re.search(r'Big (\d+), Dot (\d+) = do (\d+) \+ xanh (\d+)', out)
        big, red, blue = (int(m.group(1)), int(m.group(3)), int(m.group(4))) if m else (-1, -1, -1)
        kinds = 'dotS,dotB,bt' if btlog else 'dotS,dotB'
        c = subprocess.run([sys.executable, os.path.join(HERE, 'sa4_cmp.py'), pymarks, csm, str(tick), '--kinds', kinds], capture_output=True, text=True, env=env, encoding='utf-8').stdout
        mp = re.search(r'chi co o Python: (\d+), chi co o C#: (\d+)', c)
        only_p, only_c = (int(mp.group(1)), int(mp.group(2))) if mp else (-1, -1)
        ok = 'TRUNG TUNG DAU' in c
        line = dict(dong=name, cs_do=red, cs_xanh=blue, cs_big=big, chi_python=only_p, chi_cs=only_c, ket_qua='TRUNG' if ok else 'LECH')
        print(line); res.append(line)
        if not ok: print(c)
    p = os.path.join(HERE, 'out_sa4_parity.csv' if not a.only else f'out_sa4_parity_{a.only}.csv')
    with open(p, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
    print('->', p, '| lech', sum(1 for r in res if r['ket_qua'] != 'TRUNG'))


if __name__ == '__main__':
    main()
