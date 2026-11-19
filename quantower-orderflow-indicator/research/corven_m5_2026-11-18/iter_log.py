import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np
from score import *; from score_dots import *; from rules import *; from stackfeat import *; from exh_feats import *; from final_eval import exh_score
F=pd.read_pickle('F_m5.pkl'); S=sample(F).reset_index(drop=True); E=pd.read_pickle('E_m5.pkl'); Es=E[E.t.isin(SAMPLE)]
def B(name,sel):
    r=score_big(sel,2); r1=score_big(sel,1); r4=score_big(sel,4)
    print(f"| BIG | {name} | {r['n']} | {r['hit']} / {r['extra']} / {r['miss']} | {r1['hit']} | {r4['hit']} | {r['f1']:.2f} |")
def Dt(name,sel):
    r=score_dots(sel,2)
    print(f"| DOT | {name} | {r['n']} | {r['blobs']} | {r['blob_hit']} / {r['blob_extra']} / {r['blob_miss']} | {r['dot_hit']} | {r['pix_rec']} / {r['pix_prec']} / {r['pix_f1']} |")
def X(name,sel):
    r=exh_score(Es,sel); print(f"| EXH | {name} | {r['n']} | {r['hit']} / {r['extra']} / {r['miss']} | {r['f1']} |")
print('BIG: | type | rule | n | hit/extra/miss @2 | hits @1 | hits @4 | F1 |')
B('B0 per-tick port of old rule: side>=1.25*B20_m, side>=3*weak, side>=9',S[(S.side>=1.25*S.B20_m)&(S.side>=3*S.weak)&(S.side>=9)])
B('B1 top-25 by vol/bar_max, local max +-3, ratio>=3 (best generic feature scan)',S[(S.vol/S.bar_max>=0.6)&S.locmax3&(S.ratio>=3)&(S.side>=15)])
B('B2 diag imbalance 300% any (stack>=1) AND trades>=1.6*bar_mean',S[add_stack(S,4).imb&(S.trades>=1.6*S.bar_mean)])
B('B3 side>=0.5*B20_mx, local max +-5, ratio>=3',big_rule(S,0.5,5,3))
B('B4 FINAL side>=0.5*B20_mx, local max +-5, ratio>=4',big_rule(S,0.5,5,4))
print('DOT: | type | rule | n dots | n blobs (CORVEN 16) | blob hit/extra/miss | dot hits | pixel recall/prec/F1 |')
Dt('D0 per-tick port of old rule: side>=1.5*B20_m, >=9',S[(S.side>=1.5*S.B20_m)&(S.side>=9)])
Dt('D1 side>=2.0*B20_m, >=9',S[(S.side>=2*S.B20_m)&(S.side>=9)])
Dt('D2 best F1 any count: trades>=2.34*B20_m, trades local max +-2',dot_rule(S,2.34,2))
Dt('D3 trades>=2.34*B20_m & side local max +-2',S[(S.trades>=2.34*S.B20_m)&S.locmax2])
Dt('D4 FINAL trades>=2.4*B20_m & side local max +-3',dot_rule2(S,2.4,3))
print('EXH: | type | rule | n | hit/extra/miss | F1 |')
X('E0 old style: wick>=3 only',Es[Es.wick>=3])
X('E1 s3<=9 (abs) wick>=3',Es[(Es.s3<=9)&(Es.wick>=3)])
X('E2 s5<=13 (abs) wick>=3 range>=30',Es[(Es.s5<=13)&(Es.wick>=3)&(Es.rng>=30)])
X('E3 s6<=1.2*B20_m wick>=3',exh_rule(Es,6,1.2,3))
X('E4 FINAL s6<=1.1*B20_m wick>=3',exh_rule(Es,6,1.1,3))
