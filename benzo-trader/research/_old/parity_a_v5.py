# -*- coding: utf-8 -*-
"""PARITY C# (BenzoSetupA5.DetectorA5 qua tools/ReplayA5) <-> Python (setup_a_v5.detect5 + zones_a_v4 + A4.sim) cho setup A "Phá hồi v5" / A-v4.
Plan: plans/BENZO-A-V5-port-plan.md mục 5.  KHÔNG sửa Python chuẩn; chỉ thêm file này.

Chạy:  python3 parity_a_v5.py [--no-run] [--out DIR]          → report/PARITY-A5.md  + report/_a5_bad_bars.csv
Bốn tầng, mỗi tầng chạy 2 lần (A-v5 có VCL · A-v4 `--novcl`):
  L0 mức vùng mỗi phiên: HVN tuần (đỉnh, lo, hi), HVN ngày, VAH/VAL hôm qua  (sai số ≤ 1e-9)
  L1 tín hiệu RAW (chưa lọc "1 lệnh mở"): (nến, chiều) + entry/SL/TP + vùng + E + p0/pk_pos/npb/brk_no/ent_no
  L2 nhật ký trạng thái kết thúc: zone, S, p0, pk_pos, why, armed, n_ent, brk_no
  L3 "1 lệnh mở" KHÔNG chặn mở ảo (Python vblock=False)  : A-v4 = 218 lệnh, A-v5 = 324 lệnh đã đóng
  L4 "1 lệnh mở" CÓ chặn mở ảo 19:20–20:30 (bản live, vblock=True): A-v4 = 208, A-v5 = 312
Nến "xấu" của Python (P.bad = chỗ nối hợp đồng | phiên mỏng) được ghi ra _a5_bad_bars.csv và đưa vào C# qua IsNewsBlocked ⇒ so TOÀN file."""
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import setup_a_v4 as A4  # noqa: E402
import setup_a_v5 as A5  # noqa: E402

BT = os.path.dirname(HERE)
REPORT = os.path.join(HERE, 'report')
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else REPORT
EXE = os.path.join(BT, 'tools', 'ReplayA5', 'bin', 'Release', 'net10.0', 'ReplayA5.dll')
BAD_FILE = os.path.join(REPORT, '_a5_bad_bars.csv')
TOL = 1e-6
TOL_LV = 1e-9
EXPECT = {('v5', 'sim'): 324, ('v5', 'live'): 312, ('v4', 'sim'): 218, ('v4', 'live'): 208}
LOG = []


def say(s=''):
    print(s, flush=True)
    LOG.append(s)


def run_cs(novcl, tag):
    env = dict(os.environ, PATH=os.path.expanduser('~/.dotnet') + ':' + os.environ['PATH'], DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_NOLOGO='1')
    os.makedirs(OUT, exist_ok=True)
    cmd = ['dotnet', EXE, A4.D90, os.path.join(OUT, '_a5_cs_' + tag), '--bad', BAD_FILE] + (['--novcl'] if novcl else [])
    t0 = time.time()
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return time.time() - t0, r.stderr.strip()


def fnum(x):
    return '' if x is None or (isinstance(x, float) and np.isnan(x)) else '%.4f' % x


def cmp_levels(P, tag):
    """L0"""
    cs = pd.read_csv(os.path.join(OUT, '_a5_cs_%s_levels.csv' % tag), dtype=str, keep_default_na=False)
    cs_by = {r['session_start_utc']: r for _, r in cs.iterrows()}
    t_start = P.df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S').to_numpy()
    bad, ok, maxd = [], 0, 0.0
    for s, a, b in P.sessions:
        rec = P.slev[s]
        key = t_start[a]
        r = cs_by.get(key)
        if r is None:
            bad.append((key, 'khong co dong C#'))
            continue
        hw = [tuple(float(v) for v in x.split(':')) for x in r['hvn_w'].split(';') if x]
        hd = [float(v) for v in r['hvn_d'].split(';') if v]
        vah = float(r['vah_d']) if r['vah_d'] else np.nan
        val = float(r['val_d']) if r['val_d'] else np.nan
        pyw = [(x[0], x[1], x[2]) for x in rec['hvn_w']]
        pyd = list(rec['hvn_d'])
        why = None
        d = 0.0
        if len(hw) != len(pyw):
            why = 'so HVN tuan %d vs %d' % (len(pyw), len(hw))
        elif len(hd) != len(pyd):
            why = 'so HVN ngay %d vs %d' % (len(pyd), len(hd))
        else:
            for u, v in zip(pyw, hw):
                d = max(d, max(abs(u[i] - v[i]) for i in range(3)))
            for u, v in zip(pyd, hd):
                d = max(d, abs(u - v))
            for u, v in ((rec['vah_d'], vah), (rec['val_d'], val)):
                if np.isnan(u) != np.isnan(v):
                    why = 'VAH/VAL co/khong'
                elif not np.isnan(u):
                    d = max(d, abs(u - v))
            if why is None and d > TOL_LV:
                why = 'lech %.3g' % d
        if why:
            bad.append((key, why))
        else:
            ok += 1
            maxd = max(maxd, d)
    return dict(n=len(P.sessions), ok=ok, bad=bad, maxd=maxd, n_c=len(cs))


def cmp_raw(P, ents, tag):
    """L1"""
    cs = pd.read_csv(os.path.join(OUT, '_a5_cs_%s_raw.csv' % tag))
    py = pd.DataFrame([dict(pos=e['idx'], side=e['side'], entry=e['entry'], sl=e['sl'], tp=e['tp'], zone=e['zone'], E=e['E'], p0=e['p0'],
                            pk_pos=e['pk_pos'], npb=e['npb'], brk_no=e['brk_no'], ent_no=e['ent_no'], pk_val=e['pk_val'], L=e['L'],
                            pbmax=e['pbmax']) for e in ents])
    m = py.merge(cs, on=['pos', 'side'], how='outer', suffixes=('_py', '_cs'), indicator=True)
    both = m[m['_merge'] == 'both']
    bad = []
    for _, r in m[m['_merge'] != 'both'].iterrows():
        bad.append(('chi co o %s' % ('Python' if r['_merge'] == 'left_only' else 'C#'), int(r['pos']), int(r['side']),
                    r['zone_py'] if r['_merge'] == 'left_only' else r['zone_cs']))
    ok = 0
    for _, r in both.iterrows():
        why = []
        for c in ('entry', 'sl', 'tp', 'E', 'pk_val', 'L', 'pbmax'):
            if abs(r[c + '_py'] - r[c + '_cs']) > TOL:
                why.append('%s %.4f/%.4f' % (c, r[c + '_py'], r[c + '_cs']))
        if r['zone_py'] != r['zone_cs']:
            why.append('zone %s/%s' % (r['zone_py'], r['zone_cs']))
        for c in ('p0', 'pk_pos', 'npb', 'brk_no', 'ent_no'):
            if int(r[c + '_py']) != int(r[c + '_cs']):
                why.append('%s %d/%d' % (c, r[c + '_py'], r[c + '_cs']))
        if why:
            bad.append(('lech', int(r['pos']), int(r['side']), '; '.join(why)))
        else:
            ok += 1
    return dict(n_py=len(py), n_cs=len(cs), ok=ok, bad=bad)


def cmp_states(slog, tag, Z, vcl, P):
    """L2"""
    cs = pd.read_csv(os.path.join(OUT, '_a5_cs_%s_states.csv' % tag))
    nz = len(Z)
    py = pd.DataFrame(slog)
    py['zone'] = [Z[zi]['name'] if zi < nz else 'VCL_%d' % int(vcl.eid_of[zi - nz]) for zi in py['zi']]
    cols = ['zone', 'S', 'p0', 'pk_pos', 'why', 'armed', 'n_ent', 'brk_no']
    py['armed'] = py['armed'].astype(int)
    a = py[cols].sort_values(cols).reset_index(drop=True)
    b = cs[cols].sort_values(cols).reset_index(drop=True)
    ka = [tuple(x) for x in a.to_numpy().tolist()]
    kb = [tuple(x) for x in b.to_numpy().tolist()]
    from collections import Counter
    ca, cb = Counter(ka), Counter(kb)
    only_py = list((ca - cb).elements())
    only_cs = list((cb - ca).elements())
    # phiên mỏng / chỗ nối (P.bad ở cả phiên): C# đóng nến M5 TRỄ 1 nến khi M1 thưa (không biết nến M5 đã đóng đến khi có nến sau) ⇒ trạng thái lệch ở đó
    badses = set(int(x) for x in P.st.index[(P.st['thin'].to_numpy() | P.st['splice'].to_numpy())])
    in_bad = lambda t: int(P.sno[t[2]]) in badses
    n_py_norm = sum(1 for k in ka if not in_bad(k))
    diff_norm = [k for k in only_py + only_cs if not in_bad(k)]
    diff_ent = [k for k in only_py + only_cs if k[6] > 0]
    return dict(n_py=len(ka), n_cs=len(kb), ok=len(ka) - len(only_py), only_py=only_py, only_cs=only_cs,
                n_norm=n_py_norm, diff_norm=diff_norm, diff_ent=diff_ent, n_badses=len(badses))


def trades_py(P, tr):
    df = P.df
    rows = []
    for _, t in tr.iterrows():
        ex = int(t['exit_idx'])
        rows.append(dict(time_utc=df['datetime'].iloc[int(t['idx'])].strftime('%Y-%m-%d %H:%M:%S'), side=int(t['side']), entry=float(t['entry']),
                         sl=float(t['sl']), tp=float(t['tp']), zone=t['zone'], outcome=t['outcome'],
                         exit_utc=(df['datetime'].iloc[ex].strftime('%Y-%m-%d %H:%M:%S') if t['outcome'] in ('TP', 'SL') else ''), r=float(t['r'])))
    return pd.DataFrame(rows)


def cmp_trades(pyt, tag, mode):
    """L3 / L4"""
    cs = pd.read_csv(os.path.join(OUT, '_a5_cs_%s_%s.csv' % (tag, mode)), keep_default_na=False)
    m = pyt.merge(cs, on=['time_utc', 'side'], how='outer', suffixes=('_py', '_cs'), indicator=True)
    bad = []
    ok = 0
    for _, r in m.iterrows():
        if r['_merge'] != 'both':
            bad.append(('chi co o %s' % ('Python' if r['_merge'] == 'left_only' else 'C#'), r['time_utc'], int(r['side']),
                        r['zone_py'] if r['_merge'] == 'left_only' else r['zone_cs']))
            continue
        why = []
        for c in ('entry', 'sl', 'tp'):
            if abs(r[c + '_py'] - r[c + '_cs']) > TOL:
                why.append('%s %.4f/%.4f' % (c, r[c + '_py'], r[c + '_cs']))
        if r['zone_py'] != r['zone_cs']:
            why.append('zone %s/%s' % (r['zone_py'], r['zone_cs']))
        if r['outcome_py'] != r['outcome_cs']:
            why.append('outcome %s/%s' % (r['outcome_py'], r['outcome_cs']))
        elif r['outcome_py'] in ('TP', 'SL'):
            if r['exit_utc_py'] != r['exit_utc_cs']:
                why.append('exit %s/%s' % (r['exit_utc_py'], r['exit_utc_cs']))
            if abs(float(r['r_py']) - float(r['r_cs'])) > TOL:
                why.append('r %.5f/%.5f' % (r['r_py'], float(r['r_cs'])))
        if why:
            bad.append(('lech', r['time_utc'], int(r['side']), '; '.join(why)))
        else:
            ok += 1
    n_closed_py = int(pyt['outcome'].isin(['TP', 'SL']).sum())
    n_closed_cs = int(cs['outcome'].isin(['TP', 'SL']).sum())
    return dict(n_py=len(pyt), n_cs=len(cs), closed_py=n_closed_py, closed_cs=n_closed_cs, ok=ok, bad=bad)


def main():
    t0 = time.time()
    say('# PARITY A5: C# (DetectorA5) ↔ Python (setup_a_v5.detect5) — file 90d GCZ26')
    say('')
    P, V = A5.load5()
    bad_mask = P.bad
    pd.Series(P.df['datetime'][bad_mask].dt.strftime('%Y-%m-%d %H:%M:%S')).to_csv(BAD_FILE, index=False, header=False)
    say('Nến xấu của Python (chỗ nối hợp đồng | phiên mỏng): %d nến, ghi ra `report/_a5_bad_bars.csv` (giờ MỞ nến UTC) và đưa vào C# qua `IsNewsBlocked`.' % int(bad_mask.sum()))
    say('Số nến %d · phiên %d · nạp Python %.0fs.' % (len(P.df), len(P.sessions), time.time() - t0))
    mn = P.df['datetime'].dt.minute.to_numpy()
    late = np.flatnonzero(P.m5c & (mn % 5 != 4))
    bad_ses = set(int(x) for x in P.st.index[(P.st['thin'].to_numpy() | P.st['splice'].to_numpy())])
    n_late_bad = sum(1 for t in late if int(P.sno[t]) in bad_ses)
    say('Sự kiện M5 mà C# chỉ biết trễ 1 nến (nến M1 cuối của nến M5 không phải phút :4 vì M1 thưa): %d / %d, trong đó %d nằm ở %d phiên mỏng/chỗ nối, %d ở phiên bình thường.' % (
        len(late), int(P.m5c.sum()), n_late_bad, len(bad_ses), len(late) - n_late_bad))
    say('')
    Z = P.zones('new')
    res = {}
    for tag, vcl, novcl in (('v5', V, False), ('v4', None, True)):
        say('## %s' % ('A-v5 (có VCL)' if tag == 'v5' else 'A-v4 (`--novcl`)'))
        say('')
        if '--no-run' not in sys.argv:
            sec, err = run_cs(novcl, tag)
            say('ReplayA5: %.0fs. ```%s```' % (sec, err.replace('\n', ' | ')))
            say('')
        slog = []
        ents0 = A5.detect5(P, Z, vcl, vblock=False, states_log=slog)
        tr0 = A4.sim(P, ents0)
        ents1 = A5.detect5(P, Z, vcl, vblock=True)
        tr1 = A4.sim(P, ents1)
        c0, c1 = A4.closed(tr0), A4.closed(tr1)
        say('Python: raw %d · 1 lệnh mở không chặn mở ảo %d đã đóng (%d tổng) · có chặn mở ảo %d đã đóng (%d tổng).' % (len(ents0), len(c0), len(tr0), len(c1), len(tr1)))
        L0 = cmp_levels(P, tag)
        L1 = cmp_raw(P, ents0, tag)
        L2 = cmp_states(slog, tag, Z, vcl, P)
        L3 = cmp_trades(trades_py(P, tr0), tag, 'sim')
        L4 = cmp_trades(trades_py(P, tr1), tag, 'live')
        res[tag] = (L0, L1, L2, L3, L4)
        say('')
        say('| tầng | Python | C# | khớp | % | mục tiêu |')
        say('|---|---|---|---|---|---|')
        say('| L0 mức vùng (phiên) | %d | %d | %d | %.2f%% | 100%% (lệch lớn nhất %.2e) |' % (L0['n'], L0['n_c'], L0['ok'], 100 * L0['ok'] / L0['n'], L0['maxd']))
        say('| L1 tín hiệu raw | %d | %d | %d | %.2f%% | 100%% |' % (L1['n_py'], L1['n_cs'], L1['ok'], 100 * L1['ok'] / max(L1['n_py'], 1)))
        say('| L2 trạng thái kết thúc | %d | %d | %d | %.2f%% | 100%% |' % (L2['n_py'], L2['n_cs'], L2['ok'], 100 * L2['ok'] / max(L2['n_py'], 1)))
        say('| L2 ngoài phiên mỏng/chỗ nối | %d | | %d | %.2f%% | 100%% |' % (L2['n_norm'], L2['n_norm'] - len(L2['diff_norm']), 100 * (L2['n_norm'] - len(L2['diff_norm'])) / max(L2['n_norm'], 1)))
        say('| L3 lệnh không chặn mở ảo | %d (đóng %d) | %d (đóng %d) | %d | %.2f%% | đóng = %d |' % (
            L3['n_py'], L3['closed_py'], L3['n_cs'], L3['closed_cs'], L3['ok'], 100 * L3['ok'] / max(L3['n_py'], 1), EXPECT[(tag, 'sim')]))
        say('| L4 lệnh có chặn mở ảo (live) | %d (đóng %d) | %d (đóng %d) | %d | %.2f%% | đóng = %d |' % (
            L4['n_py'], L4['closed_py'], L4['n_cs'], L4['closed_cs'], L4['ok'], 100 * L4['ok'] / max(L4['n_py'], 1), EXPECT[(tag, 'live')]))
        say('')
        for name, d in (('L0', L0), ('L1', L1), ('L3', L3), ('L4', L4)):
            if d['bad']:
                say('Ca lệch %s (%d):' % (name, len(d['bad'])))
                for x in d['bad'][:25]:
                    say('- %s' % (x,))
                say('')
        if L2['only_py'] or L2['only_cs']:
            say('Ca lệch L2: chỉ Python %d, chỉ C# %d.' % (len(L2['only_py']), len(L2['only_cs'])))
            for x in L2['only_py'][:15]:
                say('- chỉ Python: %s' % (x,))
            for x in L2['only_cs'][:15]:
                say('- chỉ C#: %s' % (x,))
            say('Trong ca lệch L2: ngoài phiên mỏng/chỗ nối %d · có lệnh vào (n_ent>0) %d.' % (len(L2['diff_norm']), len(L2['diff_ent'])))
            say('')
    say('Tổng thời gian %.0fs.' % (time.time() - t0))
    out = os.path.join(REPORT, 'PARITY-A5.md')
    old = open(out, encoding='utf-8').read() if os.path.exists(out) else ''
    tail = old.split('<!-- NGUYEN-NHAN -->', 1)[1] if '<!-- NGUYEN-NHAN -->' in old else '\n## Giải thích ca lệch\n(chưa viết)\n'
    open(out, 'w', encoding='utf-8').write('\n'.join(LOG) + '\n\n<!-- NGUYEN-NHAN -->' + tail)


if __name__ == '__main__':
    main()
