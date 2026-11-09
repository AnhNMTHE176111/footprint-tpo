import sys, os, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.argv=['x']
import kernel as K
from _dissect import BASE
OUT=r"C:\Users\anhla\AppData\Local\Temp\claude\c--Users-anhla-OneDrive-Documents-footprint-tpo\bcfa2f0c-e665-455f-9235-2f428bc8a04f\scratchpad\benzo\charts"
os.makedirs(OUT, exist_ok=True)
def plot_trade(df, e, zc, tag, before=45, after=30):
    i=int(e['idx']); ex=int(e['exit_idx']); a=max(0,i-before); b=min(len(df), max(ex, i)+after)
    seg=df.iloc[a:b]; x=np.arange(len(seg))
    fig,ax=plt.subplots(figsize=(16,8))
    for k,(_,r) in enumerate(seg.iterrows()):
        col='k' if r.close>=r.open else 'r'
        ax.plot([k,k],[r.low,r.high],color=col,lw=1)
        ax.add_patch(plt.Rectangle((k-0.3,min(r.open,r.close)),0.6,max(abs(r.close-r.open),0.05),color=col,fill=(r.close<r.open)))
        ax.text(k, r.low-0.25, f"{int(r.delta):+d}", ha='center', va='top', fontsize=6, color=('g' if r.delta>0 else 'r'))
        ax.text(k, r.high+0.15, f"{int(r.volume)}", ha='center', va='bottom', fontsize=5, color='gray')
    ei=i-a; xi=ex-a
    ax.axhline(e['entry'],color='b',lw=1,ls='--'); ax.axhline(e['sl'],color='r',lw=1); ax.axhline(e['tp'],color='g',lw=1)
    ax.axvline(ei,color='b',lw=0.8,alpha=.5); ax.axvline(xi,color='m',lw=0.8,alpha=.5)
    # zones at entry bar
    zrow=zc.iloc[i] if zc is not None else None
    if zrow is not None:
        for c in zc.columns:
            v=zrow[c]
            if isinstance(v,(int,float,np.floating)) and not np.isnan(v) and seg.low.min()-2<v<seg.high.max()+2:
                ax.axhline(v,color='orange',lw=0.6,ls=':'); ax.text(len(seg)-1, v, c, fontsize=6, color='orange', va='bottom', ha='right')
    ticks=list(range(0,len(seg),5)); ax.set_xticks(ticks); ax.set_xticklabels([str(seg['t_vn'].iloc[t])[5:16] for t in ticks], rotation=60, fontsize=6)
    side='BUY' if e['side']>0 else 'SELL'
    ax.set_title(f"{tag} {side} {e['outcome']} r={e['r']:+.2f} | vao {str(e.get('t_vn',''))[:16]} VN | entry {e['entry']:.1f} SL {e['sl']:.1f} TP {e['tp']:.1f} | {e.get('note','')}", fontsize=9)
    ax.set_ylim(seg.low.min()-0.8, seg.high.max()+0.8); ax.grid(alpha=.2)
    fn=os.path.join(OUT, f"{tag}_{str(e.get('t_vn',''))[:16].replace(':','').replace(' ','_')}_{e['outcome']}.png")
    fig.tight_layout(); fig.savefig(fn, dpi=80); plt.close(fig); return fn
if __name__=='__main__':
    which=sys.argv[1] if len(sys.argv)>1 else 'C'
