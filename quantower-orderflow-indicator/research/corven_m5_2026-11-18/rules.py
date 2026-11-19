"""Final per-tick rules (no row grouping). All baselines use ONLY prior bars (shift 1)."""
import pandas as pd, numpy as np
def locmax(D,col,k):
    """True where D[col] is strictly greater than the same column at every other tick within +-k ticks of the same bar."""
    idx=D.set_index(['datetime','tk']); mx=np.zeros(len(D))
    for o in range(-k,k+1):
        if o==0: continue
        j=pd.MultiIndex.from_arrays([D.datetime,D.tk+o]); mx=np.maximum(mx,idx[col].reindex(j).fillna(0).values)
    return D[col].values>mx
def big_rule(F,k,w,rt):
    """BIG circle at tick p: dominant-side volume >= k * B20_mx (mean over the previous 20 bars of each bar's max dominant-side level),
    strictly the largest dominant side within +-w ticks, and dominant side >= rt * other side. colour = dominant side."""
    lm=locmax(F,'side',w)
    return F[(F.side>=k*F.B20_mx)&lm&(F.side>=rt*F.weak.clip(lower=1))]
def dot_rule(F,k,w):
    """DOT at tick p: trades(p) >= k * B20_m (mean per-level volume of previous 20 bars), strictly the largest trades count within +-w ticks. colour = dominant side."""
    lm=locmax(F,'trades',w) if w>0 else np.ones(len(F),bool)
    return F[(F.trades>=k*F.B20_m)&lm]

def dot_rule2(F,k,w):
    """FINAL DOT rule: trades(p) >= k * B20_m and side(p) strictly the largest dominant-side level within +-w ticks."""
    return F[(F.trades>=k*F.B20_m)&locmax(F,'side',w)]

def exh_rule(E,n,k,wick):
    """FINAL EXHAUSTION rule per bar/side. E rows from exh_feats.exh_table: s{n} = sum over the n extreme levels (top: Ask, bottom: Bid) starting at the bar high/low;
    mark when s{n} <= k * B20_m (B20_m = mean per-level volume of the previous 20 bars) and wick (high - max(open,close) or min(open,close) - low) >= wick ticks."""
    return E[(E['s%d'%n]<=k*E.B20_m)&(E.wick>=wick)]
