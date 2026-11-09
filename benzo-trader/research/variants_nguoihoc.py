"""Đo 3 sửa đổi của người học (2026-11-09) trên TRAIN ≤ 15/9. Không đụng TEST, không dùng dữ liệu ≥ 22/10 để quyết."""
import sys, os, itertools
sys.path.insert(0, os.getcwd())
import numpy as np, pandas as pd
import setup_corven as SC, controls_corven as CC

ORIG = SC.Step2Machine._b_eval
OPEN = None
def b_eval_hoi(self, b, j):
    ORIG(self, b, j)
    if j in b.passed_edge:
        return
    H, L, C = self.eng.H, self.eng.L, self.eng.C; O = OPEN
    w0 = max(j - self.cp.win_b + 1, b.ref + 1)
    ks = list(range(w0, j))
    if not ks: return
    D, E = b.D, b.E
    Cj = C[j]
    if (Cj - E) * D <= 0: return
    if any((C[k] - E) * D <= 0 for k in ks): return
    pb = [k for k in ks if (C[k] - C[k - 1]) * D < 0 or (O is not None and (C[k] - O[k]) * D < 0)]
    if not pb: return
    lim = max(C[k] for k in pb) if D > 0 else min(C[k] for k in pb)
    if (Cj - lim) * D > 0:
        b.passed_edge.append(j)

def run(bars, df, good, hoi, no_qs, no_rmin_b):
    global OPEN
    OPEN = [b.o for b in bars]
    SC.Step2Machine._b_eval = b_eval_hoi if hoi else ORIG
    try:
        R = SC.run_gd1(bars, df, good)
    finally:
        SC.Step2Machine._b_eval = ORIG
    if no_qs or no_rmin_b:
        for c in R['cands']:
            c.gates = [g for g in c.gates if not (no_qs and g == 'v_quet_stop') and not (no_rmin_b and c.the == 'B' and g == 'r_nho')]
        tr, ch, why = SC.select_and_simulate(R['cands'], df, R['feat'], R['cp'])
        R.update(trades=tr, chosen=ch, why=why)
    return R

def summ(R, sess_good):
    t = R['trades']
    if len(t) == 0: return dict(n=0)
    r = t['r'].to_numpy(float)
    half = np.array([sess_good.index(s) < len(sess_good) // 2 for s in t['session_id']])
    c2df, _ = CC.c2(R, after_only=True)
    nb = int((t['setup'] == 'B').sum())
    rb = t.loc[t['setup'] == 'B', 'r'].mean() if nb else np.nan
    return dict(n=len(t), R=r.mean(), WR=(r > 0).mean(), sum=r.sum(), h1=r[half].mean(), h2=r[~half].mean(),
                nB=nb, RB=rb, C2p=c2df['r_c2_tb'].mean() if len(c2df) else np.nan)

if __name__ == '__main__':
    cut = SC.train_cut()
    bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    sg = sorted(set(df['session_id'].to_numpy()[good]))
    print('phien', len(sg))
    rows = []
    for hoi, qs, rm in itertools.product([0, 1], repeat=3):
        R = run(bars, df, good, hoi, qs, rm)
        s = summ(R, sg); s.update(hoi=hoi, bo_quet_stop=qs, bo_rmin_B=rm); rows.append(s)
        print(s, flush=True)
    out = pd.DataFrame(rows)
    print(out.round(3).to_string())
    out.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'var_user_train.csv'), index=False)
