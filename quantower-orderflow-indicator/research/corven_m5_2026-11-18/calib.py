from PIL import Image
import numpy as np, pandas as pd
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO=HERE.parents[2]
im=np.array(Image.open(HERE/'corven-m5-2026-11-18.png').convert('RGB')).astype(int)
B=pd.read_csv(REPO/'data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h_bars.csv')
B=B[B.datetime.str.startswith('2026-11-18')]; B['t']=B.datetime.str[11:16]; B=B.set_index('t')
P=lambda y:3792.8228-0.0723329*y
dark=lambda p:(p.sum(axis=-1)<150)
rows=[]
for k in range(26):
    xc=22+33*k; t=f"{12+(15+5*k)//60:02d}:{(15+5*k)%60:02d}"
    col=im[:,xc,:]; d=np.where(dark(col))[0]
    d=d[(d>3)&(d<720)]
    if len(d)==0: continue
    top,bot=d.min(),d.max()
    b=B.loc[t]
    rows.append((t,P(top),b.high,P(top)-b.high,P(bot),b.low,P(bot)-b.low))
df=pd.DataFrame(rows,columns='t cH dH dh cL dL dl'.split()); print(df.round(2).to_string())
print(df.dh.median(),df.dl.median())
