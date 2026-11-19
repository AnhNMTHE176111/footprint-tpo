import pandas as pd, numpy as np
from common import *
GT_BIG=gt_marks('big')
def marks_of(S):  # S dataframe of selected cells -> list (bar,tk,col)
    return list(zip(S.datetime,S.tk,S.col))
def score_big(S,tol=2,verbose=False):
    ours=marks_of(S); pairs=match(ours,GT_BIG,tol)
    h=len(pairs); return dict(n=len(ours),gt=len(GT_BIG),hit=h,extra=len(ours)-h,miss=len(GT_BIG)-h,f1=2*h/(len(ours)+len(GT_BIG)) if ours else 0)
def sample(F): return F[F.datetime.isin(SAMPLE)]
def label_cells(S,tol=2):
    lab=np.zeros(len(S),bool)
    for i,(d,tk,c) in enumerate(zip(S.datetime,S.tk,S.col)):
        for (t,tk2,c2) in GT_BIG:
            if t==d and c==c2 and abs(tk-tk2)<=tol: lab[i]=True
    return lab
def auc(y,x):
    from scipy.stats import rankdata
    y=np.asarray(y,bool); r=rankdata(x); n1=y.sum(); n0=(~y).sum()
    return (r[y].sum()-n1*(n1+1)/2)/(n1*n0)
