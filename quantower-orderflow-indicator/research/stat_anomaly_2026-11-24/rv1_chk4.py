import sys, os, numpy as np, pandas as pd
R = r'c:/Users/anhla/OneDrive/Documents/footprint-tpo/quantower-orderflow-indicator/research/stat_anomaly_2026-11-24'
sys.path.insert(0, R); os.chdir(R)
import sa_dot_rules as RR
from sa_bt_rules import BtData, evaluate_bt, bt_configs
from sa_oracle_lib import rulers, oracle_row
from bt_common import load_m1, to_tf
for key in ('GC', 'NQ', 'GClive'):
    M1 = load_m1(key)
    b1 = pd.DatetimeIndex(sorted(set(M1.t))); d1 = (b1 + pd.Timedelta(hours=2)).normalize()
    cnt = pd.Series(1, index=d1).groupby(level=0).size(); full = set(cnt[cnt >= 400].index)
    for m in (1, 5, 15):
        bt = BtData(key, m, to_tf(M1, m)); Rr = rulers(bt)
        allc = {c['name']: c for c in bt_configs(key)}
        base = bt.doan_mask('kiem') if key != 'NQ' else np.ones(bt.nb, bool)
        mask = base & np.isin(bt.tday.values, np.array(list(full), dtype='datetime64[ns]'))
        for cn in ('cuon_T120_p1', 'cuon_T240_p1', 'cuon_T480_p1', 'cuon_T240_p0.5', 'ky_luc_T240_q0.5', 'dc_codinh10', 'dc_dang_chay_thich_nghi'):
            res = evaluate_bt(bt, allc[cn]); o = oracle_row(bt, res, Rr, mask, bt.g)
            hs = mask & res.has; nd = np.bincount(bt.sbar[res.dot], minlength=bt.nb); nx = np.bincount(bt.sbar[res.exc], minlength=bt.nb)
            ses = [f"{nd[hs & (bt.ses == s)].sum() / max((hs & (bt.ses == s)).sum(), 1):.2f}" for s in range(3)]
            pr = [f"{nx[hs & (bt.ses == s)].sum() / max(bt.npos[hs & (bt.ses == s)].sum(), 1) * 100:.2f}" for s in range(3)]
            thr = res.thr[hs]
            print(f"{key:6s} M{m:<2d} {cn:24s} ngay du {len(full)} co nguong {hs.sum()/max(mask.sum(),1):.3f} p^ {o['p_hat']*100:.2f}% vong/nen A/Au/My {'/'.join(ses)} | %o vuot A/Au/My {'/'.join(pr)} | top20 {o['top20_ngay_gop']:.3f} top5 {o['top5_phien_gop']:.3f} cuc tri {o['chat_ca_hai_gop']:.3f} nhieu {o['nhieu_ngoai_ca_hai']:.3f} | nguong p10/p50/p90 {np.nanquantile(thr,.1):.0f}/{np.nanquantile(thr,.5):.0f}/{np.nanquantile(thr,.9):.0f}")
        RR._memo.clear()
