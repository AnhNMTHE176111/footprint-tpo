import sys; which=sys.argv[1]; sys.argv=['x']
import numpy as np, pandas as pd
import kernel as K
from _dissect import BASE
from _plot_sl import plot_trade
def dump(t, df, zc, tag, k=12):
    t=t[t.outcome.isin(['SL','TP'])].copy()
    if 't_vn' not in t: t['t_vn']=[df['t_vn'].iloc[int(i)] for i in t['idx']]
    sl=t[t.outcome=='SL'].sample(min(k,(t.outcome=='SL').sum()), random_state=1) if (t.outcome=='SL').sum()>k else t[t.outcome=='SL']
    tp=t[t.outcome=='TP'].head(4)
    for _,e in pd.concat([sl,tp]).iterrows(): print(plot_trade(df,e,zc,tag))
if which=='C':
    import setup_c_fade_canh as C
    P=C.prepare(BASE); _,t=C.run(P,pen_ticks=2,min_width=6.0,tp_mode='fixed2'); dump(t,P['df'],P['zc'],'C')
elif which=='A':
    import setup_a_pha_hoi as A
    D=A.Data(BASE); _,t=A.run(D,n_min=3,body=0.5,expire=30); dump(t,D.df,D.zc,'A',k=18)
elif which=='B':
    import setup_b_hap_thu as B
    df=K.load_bars(BASE+'_bars.csv'); P=B.prepare(df,K.build_profiles(df,BASE+'.csv'))
    ent=B.detect(P,theta=0.5,N=3,mono='ends'); t=K.simulate(df,ent); dump(t,df,None,'B',k=11)
