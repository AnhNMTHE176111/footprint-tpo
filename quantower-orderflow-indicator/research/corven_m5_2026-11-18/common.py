import pandas as pd, numpy as np
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO=HERE.parents[2]
M5=REPO/'data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h'
M1=REPO/'data-export/data-footprint/fp_GCZ26_XCEC_Time_20260811-20261109_90d'
def load(path=M5):
    D=pd.read_csv(str(path)+'.csv'); B=pd.read_csv(str(path)+'_bars.csv')
    D=D[D.volume>0].copy(); D['tk']=(D.price*10).round().astype(int); D['datetime']=D.datetime.str[:16]; B['datetime']=B.datetime.str[:16]
    D=D.rename(columns={'bid_vol':'bid','ask_vol':'ask','volume':'vol'})
    D['side']=D[['bid','ask']].max(axis=1); D['weak']=D[['bid','ask']].min(axis=1)
    D['col']=np.where(D.ask>D.bid,'B','S')   # B = Ask dominant (blue), S = Bid dominant (red/pink)
    return D.sort_values(['datetime','tk']).reset_index(drop=True), B.set_index('datetime')
SAMPLE=[f"2026-11-18 {12+(15+5*k)//60:02d}:{(15+5*k)%60:02d}" for k in range(26)]
def gt():
    G=pd.read_csv(HERE/'gt_corven_m5.csv'); return G
def gt_marks(typ):
    G=gt(); G=G[G.type==typ]
    if typ=='big': return [(r.bar_time,int(round(r.price_centre*10)),'S' if r.colour=='pink' else 'B') for r in G.itertuples()]
    if typ=='dot': return [(r.bar_time,int(round(r.price_centre*10)),'S' if r.colour=='red' else 'B',int(r.blob_y0_px),int(r.blob_y1_px),int(r.n_est)) for r in G.itertuples()]
    return [(r.bar_time,) for r in G.itertuples()]
def match(ours,theirs,tol):
    """one-to-one, same bar and colour, |tick diff|<=tol, greedy by distance. ours/theirs: list of (bar,tk,col). returns hits,extras,misses"""
    from collections import defaultdict
    cand=[]
    for i,o in enumerate(ours):
        for j,t in enumerate(theirs):
            if o[0]==t[0] and o[2]==t[2] and abs(o[1]-t[1])<=tol: cand.append((abs(o[1]-t[1]),i,j))
    cand.sort(); ui=set(); uj=set(); pairs=[]
    for d,i,j in cand:
        if i in ui or j in uj: continue
        ui.add(i); uj.add(j); pairs.append((i,j))
    return pairs
def py_price(y): return 3792.8228-0.0723329*y
def tk_of_y(y): return (3792.8228-0.0723329*y)*10
