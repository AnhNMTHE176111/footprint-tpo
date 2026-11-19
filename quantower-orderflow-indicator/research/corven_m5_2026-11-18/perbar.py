import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np
from score import *; from score_dots import *
def perbar_dots(S):
    ours=list(zip(S.datetime,S.tk,S.col)); ob=blobs_of(ours)
    lines=[]
    for t in SAMPLE:
        o=[(c,[(round(tk_of_y(b[1])/10,1),round(tk_of_y(b[0])/10,1)) for b in bl]) for (tt,c),bl in ob.items() if tt==t]
        g=[(c,round(tk_of_y(y1+1)/10,1),round(tk_of_y(y0)/10,1)) for (tt,tk,c,y0,y1,n) in GT_DOT if tt==t]
        mine=' '.join(f"{c}{a}-{b}" for c,bl in o for a,b in bl)
        lines.append(f"{t[11:]} ours: {mine or '-'} | CORVEN: {' '.join(f'{c}{a}-{b}' for c,a,b in g) or '-'}")
    return '\n'.join(lines)
def perbar_big(S,tol=2):
    ours=marks_of(S); pairs=match(ours,GT_BIG,tol); uo={i for i,j in pairs}; ug={j for i,j in pairs}
    lines=[]
    for t in SAMPLE:
        o=' '.join(f"{c}{tk/10:.1f}{'*' if i in uo else ''}" for i,(tt,tk,c) in enumerate(ours) if tt==t)
        g=' '.join(f"{c}{tk/10:.1f}{'*' if j in ug else ''}" for j,(tt,tk,c) in enumerate(GT_BIG) if tt==t)
        lines.append(f"{t[11:]} ours: {o or '-'} | CORVEN: {g or '-'}")
    return '\n'.join(lines)
