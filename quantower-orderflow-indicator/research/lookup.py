from bubble_common import *
S="C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/14112285-cd5a-4717-90f2-b4fe405421be/scratchpad"
import os
b=load_bars()
_P=S+'/lvl_sub.pkl'
if not os.path.exists(_P):   # tao lai tu file per-level (chi lay cac nen trong b)
    _L=pd.read_csv(LVL,usecols=['bar_idx','datetime','price','bid_vol','ask_vol','volume','delta'])
    _L=_L[(_L.bar_idx>=b.bar_idx.min())&(_L.bar_idx<=b.bar_idx.max())]; os.makedirs(S,exist_ok=True); _L.to_pickle(_P)
L=pd.read_pickle(_P)
L['p10']=(L.price*10).round().astype(int)
cells={k:g.set_index('p10') for k,g in L.groupby('bar_idx')}
def cell(idx,price,off=0):
    bi=int(b.bar_idx[idx]); g=cells.get(bi)
    p=int(round(price*10))+off
    if g is None or p not in g.index: return (0,0,0,0)
    r=g.loc[p]; return (int(r.bid_vol),int(r.ask_vol),int(r.volume),int(r.delta))
def barstats(idx):
    g=cells[int(b.bar_idx[idx])]
    vm=g.volume.max(); return dict(bar_max_vol=int(vm), bar_max_bid=int(g.bid_vol.max()), bar_max_ask=int(g.ask_vol.max()),
        bar_vol=int(g.volume.sum()), bar_delta=int(g.delta.sum()), bar_max_delta=int(g.delta.max()), bar_min_delta=int(g.delta.min()))
