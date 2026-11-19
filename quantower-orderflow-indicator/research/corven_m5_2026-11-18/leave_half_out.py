import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools
from score import *; from rules import *; from exh_feats import *; from final_eval import P, exh_score
import score_dots as sd
F=pd.read_pickle('F_m5.pkl'); E=pd.read_pickle('E_m5.pkl')
SPL={'first13|last13':(SAMPLE[:13],SAMPLE[13:]),'last13|first13':(SAMPLE[13:],SAMPLE[:13]),'even|odd':(SAMPLE[0::2],SAMPLE[1::2]),'odd|even':(SAMPLE[1::2],SAMPLE[0::2])}
def with_gt(bars):
    sd.GT_DOT=[g for g in GT_DOT_ALL if g[0] in bars]
GT_DOT_ALL=list(sd.GT_DOT)
# ---------- BIG
def big_f1(bars,k,w,rt,lm):
    S=F[F.datetime.isin(bars)]; m=(S.side>=k*S.B20_mx)&lm[w].loc[S.index]&(S.side>=rt*S.weak.clip(lower=1))
    ours=marks_of(S[m]); gtb=[g for g in GT_BIG if g[0] in bars]; h=len(match(ours,gtb,2)); n=len(ours)
    return (2*h/(n+len(gtb)) if n else 0),n,h,len(gtb)
LM={w:pd.Series(locmax(F,'side',w),index=F.index) for w in (2,3,5,8)}
def fit_big(bars):
    res=[]
    for k in np.arange(0.3,1.21,0.05):
        for w in (2,3,5,8):
            for rt in (2,3,4,5):
                f,n,h,g=big_f1(bars,k,w,rt,LM); pen=0 if abs(n-g)<=3 else 0.03*(abs(n-g)-3); res.append((f-pen,round(k,2),w,rt))
    res.sort(reverse=True); return res[0]
# ---------- DOT
def dot_sel(S,k,w): return S[(S.trades>=k*S.B20_m)&LM[w].loc[S.index]]
LM[1]=pd.Series(locmax(F,'side',1),index=F.index)
def fit_dot(bars):
    S=F[F.datetime.isin(bars)]; with_gt(bars); res=[]
    for k in np.arange(1.5,4.01,0.1):
        for w in (1,2,3,5):
            sel=dot_sel(S,k,w); n=len(sel)
            if not 1.0*len(bars)<=n<=1.5*len(bars): continue
            r=sd.score_dots(sel); res.append((r['pix_f1'],round(k,1),w))
    sd.GT_DOT=GT_DOT_ALL; res.sort(reverse=True); return res[0]
# ---------- EXH
def exh_pick(bars,n,k,wick):
    S=E[E.t.isin(bars)]; sel=exh_rule(S,n,k,wick)
    gt={(t,'T') for t in TOP if t in bars}|{(t,'B') for t in BOT if t in bars}; ours={(r.t,r.side) for r in sel.itertuples()}
    h=len(ours&gt); return (2*h/(len(ours)+len(gt)) if len(ours)+len(gt) else 0),len(ours),h,len(gt)
def fit_exh(bars):
    res=[]
    for n in (4,5,6):
        for wk in (2,3,4):
            for k in np.arange(0.4,2.01,0.1):
                f,no,h,g=exh_pick(bars,n,round(k,1),wk); pen=0 if abs(no-g)<=3 else 0.03*(abs(no-g)-3); res.append((f-pen,n,round(k,1),wk))
    res.sort(reverse=True); return res[0]
if __name__=='__main__':
    for name,(tr,te) in SPL.items():
        fb=fit_big(tr); fd=fit_dot(tr); fe=fit_exh(tr)
        bt=big_f1(te,fb[1],fb[2],fb[3],LM)
        with_gt(te); dt=sd.score_dots(dot_sel(F[F.datetime.isin(te)],fd[1],fd[2])); sd.GT_DOT=GT_DOT_ALL
        et=exh_pick(te,fe[1],fe[2],fe[3])
        bf=big_f1(te,P['big']['k'],P['big']['w'],P['big']['rt'],LM)
        with_gt(te); df=sd.score_dots(dot_sel(F[F.datetime.isin(te)],P['dot']['k'],P['dot']['w'])); sd.GT_DOT=GT_DOT_ALL
        ef=exh_pick(te,P['exh']['n'],P['exh']['k'],P['exh']['wick'])
        print(f"== fit on {tr[0][11:]}.. | test {te[0][11:]}.. ({name})")
        print('  BIG fitted',fb[1:],'-> test f1/n/hit/gt',tuple(round(x,3) for x in bt),'| final params on same test',tuple(round(x,3) for x in bf))
        print('  DOT fitted',fd[1:],'-> test n',dt['n'],'blob_hit',dt['blob_hit'],'/',dt['gt_blobs'],'pix_f1',dt['pix_f1'],'| final params n',df['n'],'blob_hit',df['blob_hit'],'pix_f1',df['pix_f1'])
        print('  EXH fitted',fe[1:],'-> test f1/n/hit/gt',tuple(round(x,3) for x in et),'| final params',tuple(round(x,3) for x in ef))
