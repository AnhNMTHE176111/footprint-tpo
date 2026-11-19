import pandas as pd, numpy as np
def add_stack(F,R=3.0,minv=0,name=''):
    """diagonal imbalance flags and stack run length / position; per bar over contiguous ticks."""
    F=F.copy(); idx=F.set_index(['datetime','tk'])
    # buy imbalance: ask[p] >= R*bid[p-1]; sell imbalance: bid[p] >= R*ask[p+1]
    bb=pd.MultiIndex.from_arrays([F.datetime,F.tk-1]); aa=pd.MultiIndex.from_arrays([F.datetime,F.tk+1])
    bidb=idx.bid.reindex(bb).fillna(0).values; aska=idx.ask.reindex(aa).fillna(0).values
    F['bimb']=(F.ask>=R*np.maximum(bidb,0))&(F.ask>=max(minv,1))&(F.ask>bidb)
    F['simb']=(F.bid>=R*np.maximum(aska,0))&(F.bid>=max(minv,1))&(F.bid>aska)
    F['imb']=np.where(F.col=='B',F.bimb,F.simb)
    F['imb']=F.imb&(F.side>=max(minv,1))
    # run length of consecutive ticks sharing imb of same type
    out_len=np.zeros(len(F),int); out_pos=np.zeros(len(F),int)
    d={}
    for i,(dt,tk,c,im) in enumerate(zip(F.datetime,F.tk,F.col,F.imb)):
        d[(dt,tk,c)]=im
    for i,(dt,tk,c,im) in enumerate(zip(F.datetime,F.tk,F.col,F.imb)):
        if not im: continue
        a=0
        while d.get((dt,tk-a-1,c),False): a+=1
        b=0
        while d.get((dt,tk+b+1,c),False): b+=1
        out_len[i]=a+b+1; out_pos[i]=a
    F['stk']=out_len; F['stkpos']=out_pos
    return F
