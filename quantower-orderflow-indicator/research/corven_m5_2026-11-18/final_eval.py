import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np
from score import *; from score_dots import *; from rules import *; from perbar import *; from exh_feats import *
P=dict(big=dict(k=0.5,w=5,rt=4), dot=dict(k=2.4,w=3), exh=dict(n=6,k=1.1,wick=3))
def exh_score(E,sel):
    key=lambda r:(r.t,r.side)
    gt={(t,'T') for t in TOP}|{(t,'B') for t in BOT}
    ours={(r.t,r.side) for r in sel.itertuples()}
    h=len(ours&gt); return dict(n=len(ours),gt=len(gt),hit=h,extra=len(ours)-h,miss=len(gt)-h,f1=round(2*h/(len(ours)+len(gt)),3))
if __name__=='__main__':
    F=pd.read_pickle('F_m5.pkl'); S=sample(F)
    big=big_rule(S,**P['big']); dot=dot_rule2(S,**P['dot'])
    E=pd.read_pickle('E_m5.pkl'); Es=E[E.t.isin(SAMPLE)]; exh=exh_rule(Es,**P['exh'])
    for tol in (1,2,4):
        print('tol',tol,'BIG',score_big(big,tol)); print('   DOT',score_dots(dot,tol))
    print('EXH',exh_score(Es,exh))
    print('--- BIG per bar (* = hit at +-2)'); print(perbar_big(big))
    print('--- DOT per bar'); print(perbar_dots(dot))
    print('--- EXH per bar')
    for t in SAMPLE:
        o=''.join(r.side for r in exh[exh.t==t].itertuples()); g=('T' if t in TOP else '')+('B' if t in BOT else '')
        print(t[11:],'ours:',o or '-','| CORVEN:',g or '-', '' if set(o)==set(g) else '  <-- differs')
