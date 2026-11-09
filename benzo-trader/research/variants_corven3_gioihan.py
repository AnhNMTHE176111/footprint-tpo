import sys, os, dataclasses
sys.path.insert(0, os.getcwd())
import numpy as np, pandas as pd, setup_corven as SC, controls_corven as CC
ORIG = SC.Step2Machine._hoi_ok
CFG = {}
def hoi2(self, b, j, w0):
    if not ORIG(self, b, j, w0): return False
    if 'k' in CFG and (self.eng.C[j] - b.E) * b.D > CFG['k'] * self.mbr[j] + 1e-9: return False
    if 'n' in CFG and j - b.ref > CFG['n']: return False
    return True
SC.Step2Machine._hoi_ok = hoi2
cut = SC.train_cut(); bars, df = SC.load_train(cut=cut)
good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
sg = sorted(set(df['session_id'].to_numpy()[good]))
rows = []
for name, cfg, cap in [('corven-3', {}, 4.0), ('k2', {'k': 2.0}, 4.0), ('k2.5', {'k': 2.5}, 4.0), ('k3', {'k': 3.0}, 4.0),
                       ('n10', {'n': 10}, 4.0), ('n15', {'n': 15}, 4.0), ('cap3', {}, 3.0), ('k2.5+n10', {'k': 2.5, 'n': 10}, 4.0)]:
    CFG.clear(); CFG.update(cfg)
    R = SC.run_gd1(bars, df, good, dataclasses.replace(SC.cp_live(), sl_cap_mbr=cap)); t = R['trades']; c2, _ = CC.c2(R, after_only=True)
    h = t['session_id'].map(lambda s: sg.index(s) < len(sg)//2)
    rows.append(dict(bien_the=name, n=len(t), R=t['r'].mean(), WR=(t['r']>0).mean(), h1=t.loc[h,'r'].mean(), h2=t.loc[~h,'r'].mean(), C2p=c2['r_c2_tb'].mean()))
    print(rows[-1], flush=True)
print(pd.DataFrame(rows).round(3).to_string())
