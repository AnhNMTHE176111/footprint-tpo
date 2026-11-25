#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_cum2_do.py — đo ảnh hưởng của HVN dạng cụm v2 lên vùng mạnh (HVN-CUM-V2.md mục 5), so với v1.
Cách chấm, đối chứng, dữ liệu y như hvn_cum_do.py.
  python hvn_cum2_do.py gc|nq [lai]
"""
import sys
import hvn_cum_do as DO

DO.VARIANTS = [
    ('v1 (mục 10)', dict(HVN_MODE='cum', HVN_HL='giao', D_ONLY=False)),
    ('**v2 (mục 13)**', dict(HVN_MODE='cum2', HVN_HL='giao', D_ONLY=False)),
]
TAGS = ['hc_%s_1', 'hc2_%s_v2']


def main():
    import os
    D = DO.Data()
    dens, evs = [], []
    for (ten, over), tg in zip(DO.VARIANTS, TAGS):
        p = dict(DO.V.P); p.update(over)
        tag = tg % DO.sym
        if not os.path.exists(DO.final_eval.out_path(tag)) or 'lai' in sys.argv:
            DO.final_eval.run(tag, over)
        dens.append(DO.density(D, p)); evs.append(DO.events(tag))
    print('\n## %s — mật độ' % DO.sym.upper())
    print('| Bản | HVN xét / phiên | đủ điều kiện | bề rộng hộp (× U) p10 / 50 / 90 | % dải ± 4 U quanh giá nằm trong hộp HVN | % cụm va đập có hợp lưu | % cụm có HVN | vùng vẽ TB | % thời gian có vùng | % thời gian có vùng dính HVN | % thời gian có vàng |')
    print('|' + '---|' * 11)
    for (ten, _), d in zip(DO.VARIANTS, dens):
        print('| %s | %.1f | %.1f | %s | %.0f | %.0f | %.0f | %.2f | %.0f | %.0f | %.1f |'
              % (ten, d['nlev'], d['nok'], ' / '.join('%.2f' % q for q in d['wbox']), d['cover'], d['hl'], d['hvn'], d['ve'], d['co'], d['th'], d['tg']))
    print('\n## %s — kết quả chấm' % DO.sym.upper())
    print('| Bản | Nhóm | n | thắng 1:1 | Δ thắng (điểm %) | R 1:2 | ΔR 1:2 |')
    print('|---|---|---|---|---|---|---|')
    for (ten, _), df in zip(DO.VARIANTS, evs):
        base = df['typ'] == 'doi'; that = df['typ'] == 'that'
        s = df.loc[base, ['w1', 'R2']].mean()
        print('| %s | đối chứng (vùng dời) | %d | %.1f %% | — | %+.3f | — |' % (ten, base.sum(), 100 * s['w1'], s['R2']))
        for nm, m in (('vùng được vẽ', that & df['shown'].astype(bool)), ('cụm có HVN', that & df['hvn'].astype(bool)),
                      ('cụm không có HVN', that & ~df['hvn'].astype(bool)), ('hợp lưu ≥ 2 nhóm', that & (df['ngroup'] >= 2)), ('vàng', that & df['gold'].astype(bool))):
            print('| | %s | %s |' % (nm, DO.row(df, m, base)))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
