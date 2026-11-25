#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_cum2_bien.py — THỬ NGHIỆM (HVN-CUM-V2.md mục 4): thêm đáy/đỉnh tuần trước và tuần này (tới hết hôm qua) làm mức hợp lưu.
Chỉ đo, CHƯA vào spec.   python hvn_cum2_bien.py gc|nq [lai]
"""
import os, sys
import hvn_cum_do as DO

OVER = dict(HVN_MODE='cum2', HVN_HL='giao', D_ONLY=False, WK_EXT=True)


def main():
    tag = 'hc2_%s_bien' % DO.sym
    if not os.path.exists(DO.final_eval.out_path(tag)) or 'lai' in sys.argv: DO.final_eval.run(tag, OVER)
    D = DO.Data(); p = dict(DO.V.P); p.update(OVER)
    d0 = DO.density(D, dict(p, WK_EXT=False)); d1 = DO.density(D, p)
    print('\n## %s — thêm đáy/đỉnh tuần' % DO.sym.upper())
    print('| | %% cụm va đập có hợp lưu | vùng vẽ TB | %% thời gian có vùng | %% thời gian có vàng |\n|---|---|---|---|---|')
    for nm, d in (('v2', d0), ('v2 + đáy/đỉnh tuần', d1)):
        print('| %s | %.0f | %.2f | %.0f | %.1f |' % (nm, d['hl'], d['ve'], d['co'], d['tg']))
    df = DO.events(tag)
    base = df['typ'] == 'doi'; that = df['typ'] == 'that'
    has = lambda keys: df['names'].apply(lambda s: any(k in s.split('+') for k in keys))
    print('\n| Nhóm | n | thắng 1:1 | Δ thắng (điểm %) | R 1:2 | ΔR 1:2 |\n|---|---|---|---|---|---|')
    s = df.loc[base, ['w1', 'R2']].mean()
    print('| đối chứng (vùng dời) | %d | %.1f %% | — | %+.3f | — |' % (base.sum(), 100 * s['w1'], s['R2']))
    for nm, m in (('cụm trùng đáy/đỉnh tuần trước', that & has(['lo_w1', 'hi_w1'])), ('cụm trùng đáy/đỉnh tuần này', that & has(['lo_w0', 'hi_w0'])),
                  ('cụm trùng đáy/đỉnh tuần (bất kỳ)', that & has(['lo_w1', 'hi_w1', 'lo_w0', 'hi_w0'])),
                  ('… mà không có mức nào khác', that & has(['lo_w1', 'hi_w1', 'lo_w0', 'hi_w0']) & (df['ngroup'] == 1)),
                  ('cụm không trùng đáy/đỉnh tuần', that & ~has(['lo_w1', 'hi_w1', 'lo_w0', 'hi_w0']))):
        print('| %s | %s |' % (nm, DO.row(df, m, base)))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
