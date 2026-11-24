"""Câu A: phân phối lệnh đơn theo phiên x khung; mật độ vòng với ngưỡng cố định 10 và 20."""
import sys, numpy as np, pandas as pd
from bt_common import *

TFS = (1, 5, 15, 30, 60)


def dens(hits, bars, m):
    """vòng/nến, vòng/giờ, tỉ lệ nến có vòng, nhiều nhất trong 1 nến; theo phiên + tất cả."""
    per = hits.groupby('t').size().reindex(bars.t.values, fill_value=0).values if len(hits) else np.zeros(len(bars))
    out = {}
    for s in SES + ['all']:
        k = (bars.ses.values == s) if s != 'all' else np.ones(len(bars), bool)
        out[s] = per[k].mean() if k.any() else np.nan
        out[s + '_h'] = out[s] * 60 / m
        out[s + '_p'] = (per[k] > 0).mean() if k.any() else np.nan
        out[s + '_mx'] = per[k].max() if k.any() else 0
        out[s + '_p95'] = np.quantile(per[k], .95) if k.any() else 0
    return out


if __name__ == '__main__':
    keys = sys.argv[1:] or ['NQ', 'GC']
    for key in keys:
        d = load_m1(key)
        print(f'\n################ {key}: {d.t.nunique()} nến M1, {d.t.min()} -> {d.t.max()}')
        print('--- (1) phân phối lệnh đơn lớn nhất của ô (mot) và của nến, theo phiên x khung')
        rows = []
        for m in TFS:
            c = to_tf(d, m); b = bars_of(c); c['ses'] = ses_of(pd.DatetimeIndex(c.t))
            for s in SES:
                cc = c[c.ses == s]; bb = b[b.ses == s]
                rows.append(dict(khung=f'M{m}', phien=SES_VN[s], nen=len(bb), o_moi_nen=round(len(cc) / len(bb), 1), bien_do_tick=bb.rng.median(), vol_nen=bb.vol.median(),
                                 mot_p50=cc.mot.median(), mot_p90=cc.mot.quantile(.9), mot_p99=cc.mot.quantile(.99), mot_p999=round(cc.mot.quantile(.999)), mot_max=cc.mot.max(),
                                 nen_max_p50=bb.mmax.median(), nen_max_p90=bb.mmax.quantile(.9),
                                 pct_o_ge10=round((cc.mot >= 10).mean() * 100, 2)))
        print(pd.DataFrame(rows).to_string(index=False))
        print('--- (2) ngưỡng CỐ ĐỊNH: vòng/nến (vòng/giờ) theo phiên; tỉ lệ nến có vòng Á/Âu/Mỹ; nhiều nhất trong 1 nến')
        rows = []
        for m in TFS:
            c = to_tf(d, m); b = bars_of(c)
            for T in (10, 20):
                r = dens(c[c.mot >= T], b, m)
                rows.append(dict(khung=f'M{m}', nguong=T, **{SES_VN[s]: f"{r[s]:.2f} ({r[s+'_h']:.1f}/h)" for s in SES}, tat_ca=round(r['all'], 2),
                                 nen_co_vong=f"{r['A_p']:.2f}/{r['Au_p']:.2f}/{r['My_p']:.2f}", max_1_nen=int(r['all_mx'])))
        print(pd.DataFrame(rows).to_string(index=False))
