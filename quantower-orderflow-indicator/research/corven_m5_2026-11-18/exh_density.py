import pandas as pd, numpy as np, sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]   # chay duoc tu bat ky thu muc nao
# cach dung: python exh_density.py [tien_to_file_khong_co_.csv] [ngay]   (mac dinh: file M5 9d16h, ngay 2026-11-17)
DEF=str(REPO/'data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h')
F=sys.argv[1] if len(sys.argv)>1 else DEF; day=sys.argv[2] if len(sys.argv)>2 else '2026-11-17'
D=pd.read_csv(F+'.csv'); B=pd.read_csv(F+'_bars.csv')
D=D[D.datetime.str.startswith(day)]; B=B[B.datetime.str.startswith(day)]
D['tk']=(D.price*10).round().astype(int)
G={t:g.set_index('tk') for t,g in D.groupby('datetime')}
n_old=n_new=0
for b in B.itertuples():
    L=G.get(b.datetime); 
    if L is None: continue
    hi=round(b.high*10); lo=round(b.low*10); o=round(b.open*10); c=round(b.close*10); mean=L.volume[L.volume>0].mean()
    for top in (True,False):
        ext=hi if top else lo; st=-1 if top else 1; col='ask_vol' if top else 'bid_vol'
        seq=[float(L[col].get(ext+st*j,0)) for j in range(3)]
        wick=(hi-max(o,c)) if top else (min(o,c)-lo)
        if wick>=1 and seq[0]<=0.1*mean: n_old+=1
        if wick>=3 and sum(seq)<=0.5*mean: n_new+=1
print(day,len(B),'old/bar',n_old/len(B),'new/bar',n_new/len(B))
