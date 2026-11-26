import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE + '/../exh_2026-11-26')
import data as D
ROWCFG = {'GC': (2, 1), 'NQ': (8, 4), 'GC18': (2, 1)}   # (so tick moi hang, pha): hang = (tk - pha) // n
def rows_of(bar, n, ph):
    """-> dict hang -> [bid, ask]"""
    r = (bar['tk'] - ph) // n; out = {}
    for k, b, a in zip(r, bar['bid'], bar['ask']):
        x = out.setdefault(int(k), [0.0, 0.0]); x[0] += b; x[1] += a
    return out
def load_rows(sym, t0, t1, n=None, ph=None, mins=1):
    bars, tick = D.load(sym, pd.Timestamp(t0), pd.Timestamp(t1), mins)
    n0, p0 = ROWCFG[sym]; n = n or n0; ph = p0 if ph is None else ph
    for b in bars: b['rows'] = rows_of(b, n, ph)
    return bars, tick, n, ph
def row_center_price(k, n, ph, tick): return (k * n + ph + (n - 1) / 2) * tick
