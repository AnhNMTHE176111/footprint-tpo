# -*- coding: utf-8 -*-
"""PARITY C# (BenzoDetectors.DetectorB + BenzoSr + VclCore, qua tools/ReplayCsv) <-> Python (setup_b_hap_thu.detect + zones_b_v3) cho setup B,
ba cấu hình: B cũ (2 VWAP) · B v2 (+ HVN/VA/POC ngày-tuần) · B v3 (+ PDH/PDL + 14 cạnh VCL), file 90 ngày GCZ26, ô chính (θ 0,5 · N 3 · TP 3R).

Chạy:  python3 parity_b_v3.py [--no-run] [--from 2026-07-29]      -> report/PARITY-B-v3.md
  1. Mảng vùng: C# `LEVELS` (12 mức cố định + 7 khe VCL mỗi nến) so với `zones_b_v3.build_extra3` từng nến.
  2. Lệnh: C# chạy THÔ (BENZO_NO_VOPEN=1: bỏ luật mở ảo 19:20-20:30 vốn chỉ có ở C#) rồi so với `kernel.simulate` của Python.
     Chỉ so từ phiên --from (4 phiên đầu file là "thin": Python loại, C# không biết).
Khớp = cùng (giờ mở nến vào, chiều) VÀ entry/SL/TP/tên vùng giống nhau."""
import os
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402
import setup_b_hap_thu as SB  # noqa: E402
import zones_b_v2 as ZB  # noqa: E402
import zones_b_v3 as Z3  # noqa: E402
import benzo_vcl as BV  # noqa: E402

BT = os.path.dirname(HERE)
REPORT = os.path.join(HERE, 'report')
FROM = sys.argv[sys.argv.index('--from') + 1] if '--from' in sys.argv else '2026-07-29'
EXE = os.path.join(BT, 'tools', 'ReplayCsv', 'bin', 'Release', 'net10.0', 'ReplayCsv.dll')
CFG = [('B cũ', 'B', Z3.ZONES_OLD, 11), ('B v2', 'B2', Z3.ZONES_V2, 25), ('B v3', 'B3', Z3.ZONES_V3, 58)]
FX = ['POC_D', 'VAH_D', 'VAL_D', 'HVN_D1', 'HVN_D2', 'HVN_D3', 'POC_W', 'HVN_W1', 'HVN_W2', 'HVN_W3', 'PDH', 'PDL']


def run_cs():
    env = dict(os.environ, PATH=os.path.expanduser('~/.dotnet') + ':' + os.environ['PATH'], DOTNET_CLI_TELEMETRY_OPTOUT='1', BENZO_NO_VOPEN='1')
    subprocess.check_call(['dotnet', 'build', '-c', 'Release', os.path.join(BT, 'tools', 'ReplayCsv'), '-v', 'q', '-nologo'], env=env)
    for tag in ('B', 'B2', 'B3'):
        subprocess.check_call(['dotnet', EXE, SB.D90, tag, os.path.join(REPORT, '_replay_cs_%s.csv' % tag)], env=env)
    env2 = dict(env)
    env2.pop('BENZO_NO_VOPEN')
    for tag in ('B', 'B2', 'B3'):       # bản chạy thật (có luật mở ảo)
        subprocess.check_call(['dotnet', EXE, SB.D90, tag, os.path.join(REPORT, '_replay_cs_%s_live.csv' % tag)], env=env2)
    subprocess.check_call(['dotnet', EXE, SB.D90, 'LEVELS', os.path.join(REPORT, '_replay_cs_levels.csv')], env=env)


def main():
    if '--no-run' not in sys.argv:
        run_cs()
    raw = pd.read_csv(SB.D90 + '_bars.csv', parse_dates=['datetime'])
    lvl = pd.read_csv(SB.D90 + '.csv', usecols=['bar_idx', 'price', 'volume'])
    df = K._enrich(raw)
    prof = K.build_profiles(df, lvl)
    ctx = K._Ctx(df, prof)
    lev = ZB.session_table_b(df, prof, ctx)
    rec = BV.load_rec(df)
    slots = Z3.vcl_slots(rec, len(df))
    extra3 = Z3.build_extra3(df, prof, ctx, lev, rec, slots)
    P = SB.prepare(df, prof, extra3)
    sess = pd.Series(df['session_id'].to_numpy(), index=df['t_utc'])
    L = ['# PARITY B (cũ / v2 / v3): C# ↔ Python — file 90d GCZ26', '',
         'Ô chính: θ 0,5 · N 3 · TP 3R. C# chạy THÔ (`BENZO_NO_VOPEN=1`, không luật mở ảo 19:20-20:30) nên so được với `kernel.simulate` của Python. '
         'So từ phiên %s (4 phiên đầu file là "thin": Python loại, C# không biết).' % FROM, '']
    # ---- 1. mảng vùng
    cs = pd.read_csv(os.path.join(REPORT, '_replay_cs_levels.csv'))
    assert len(cs) == len(df)
    sno = df['session_no'].to_numpy()
    bad_fx = {}
    for nm in FX:
        a, b = extra3[nm][0], cs[nm].to_numpy(float)
        bad_fx[nm] = int((~((np.isnan(a) & np.isnan(b)) | (np.abs(a - b) < 1e-9))).sum())
    bad_sl = 0
    for k in range(Z3.VCL_SLOTS_MAX):
        for key in ('lo', 'hi'):
            a, b = slots[key][k], cs['%s%d' % (key, k + 1)].to_numpy(float)
            bad_sl += int((~((np.isnan(a) & np.isnan(b)) | (np.abs(a - b) < 1e-9))).sum())
        bad_sl += int((slots['runlen'][k] != cs['run%d' % (k + 1)].to_numpy()).sum())
    nfx = sum(int((~np.isnan(extra3[nm][0])).sum()) for nm in FX)
    L += ['## 1. Mảng vùng (từng nến, %d nến)' % len(df), '',
          '- 12 mức cố định (POC/VAH/VAL ngày, HVN ngày 1-3, POC tuần, HVN tuần 1-3, PDH, PDL): ô có giá trị %d · **lệch %d ô**.' % (nfx, sum(bad_fx.values())),
          '- 7 khe VCL × (cạnh dưới, cạnh trên, số nến liên tiếp): **lệch %d ô**.' % bad_sl, '']
    # ---- 2. lệnh
    L += ['## 2. Lệnh', '', '| cấu hình | Python | C# | khớp hoàn toàn | khớp giờ+chiều nhưng khác giá/vùng | chỉ Python | chỉ C# |', '|---|---|---|---|---|---|---|']
    allok = bad_sl == 0 and sum(bad_fx.values()) == 0
    for name, tag, zones, expect in CFG:
        py = K.simulate(df, SB.detect(P, 0.5, 3, zones=zones))
        py = py[py['session_id'] >= FROM]
        c = pd.read_csv(os.path.join(REPORT, '_replay_cs_%s.csv' % tag), parse_dates=['time_utc'])
        c['sid'] = [sess.get(t, '') for t in c['time_utc']]
        c = c[c['sid'] >= FROM]
        pk = {(pd.Timestamp(r.t_utc), int(r.side)): r for r in py.itertuples()}
        ck = {(r.time_utc, int(r.side)): r for r in c.itertuples()}
        both = sorted(set(pk) & set(ck))
        exact = [k for k in both if abs(pk[k].entry - ck[k].entry) < 1e-6 and abs(pk[k].sl - ck[k].sl) < 1e-6 and abs(pk[k].tp - ck[k].tp) < 1e-6
                 and pk[k].zone == ck[k].zone]
        only_py, only_cs = sorted(set(pk) - set(ck)), sorted(set(ck) - set(pk))
        L.append('| %s (kỳ vọng %d) | %d | %d | **%d** | %d | %d | %d |' % (name, expect, len(pk), len(ck), len(exact), len(both) - len(exact), len(only_py), len(only_cs)))
        allok &= len(pk) == expect and len(ck) == expect and len(exact) == expect
        if len(both) != len(exact) or only_py or only_cs:
            for k in only_py[:5]:
                L.append('|  ↳ chỉ Python | %s | side %d | zone %s | | | |' % (k[0], k[1], pk[k].zone))
            for k in only_cs[:5]:
                L.append('|  ↳ chỉ C# | %s | side %d | zone %s | | | |' % (k[0], k[1], ck[k].zone))
    # ---- 3. bản chạy thật: C# có luật mở ảo 19:20-20:30 = Python bỏ các lệnh trong khung đó
    smv = dict(zip(df['t_utc'], df['sm']))
    L += ['', '## 3. Bản chạy thật (C# có luật mở ảo 19:20-20:30) so với Python bỏ các lệnh trong khung đó', '',
          '| cấu hình | Python (trừ khung mở ảo) | C# chạy thật | khớp hoàn toàn |', '|---|---|---|---|']
    for name, tag, zones, expect in CFG:
        py = K.simulate(df, SB.detect(P, 0.5, 3, zones=zones))
        py = py[(py['session_id'] >= FROM).to_numpy() & np.array([not (860 <= smv[t] < 930) for t in py['t_utc']], bool)]
        c = pd.read_csv(os.path.join(REPORT, '_replay_cs_%s_live.csv' % tag), parse_dates=['time_utc'])
        c['sid'] = [sess.get(t, '') for t in c['time_utc']]
        c = c[c['sid'] >= FROM]
        pk = {(pd.Timestamp(r.t_utc), int(r.side)): r for r in py.itertuples()}
        ck = {(r.time_utc, int(r.side)): r for r in c.itertuples()}
        exact = [k for k in set(pk) & set(ck) if abs(pk[k].entry - ck[k].entry) < 1e-6 and abs(pk[k].sl - ck[k].sl) < 1e-6 and abs(pk[k].tp - ck[k].tp) < 1e-6 and pk[k].zone == ck[k].zone]
        L.append('| %s | %d | %d | **%d** |' % (name, len(pk), len(ck), len(exact)))
        allok &= len(pk) == len(ck) == len(exact)
    L += ['', '**KẾT LUẬN: %s**' % ('KHỚP HOÀN TOÀN — C# ra đúng 11 / 25 / 58 lệnh của Python, từng lệnh trùng giờ, chiều, entry, SL, TP, tên vùng.' if allok else 'CÓ LỆCH — xem bảng trên.'),
          '', '## Ghi chú', '',
          '- Luật mở ảo 19:20-20:30 (chỉ có ở C#) bị tắt khi đối chiếu; khi chạy thật nó loại thêm các lệnh nằm trong khung đó (số lệnh live nhỏ hơn).',
          '- Chưa port (không ảnh hưởng file 90d, một hợp đồng): luật loại phiên dính chỗ nối hợp đồng (splice); "phiên mỏng" của POC tuần dùng trung vị volume các phiên đã biết tới lúc đó '
          '(Python dùng trung vị cả file) — trên file này cho cùng kết quả.',
          '- Footprint live từ Volume Analysis có thể lệch vài tick so với file export ⇒ HVN/VA/POC và vùng VCL loại VA có thể lệch nhẹ.']
    out = os.path.join(REPORT, 'PARITY-B-v3.md')
    open(out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main())
