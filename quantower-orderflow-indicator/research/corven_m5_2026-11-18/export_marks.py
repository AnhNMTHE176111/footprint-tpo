"""Xuat dau do luat chot (final_eval.py) ra marks_python_26bars.csv de tests/CorvenM5ParityTests.cs doi chieu C#.
Cot: bar (HH:MM), tick (gia x 10), type (dot/exh; vong mo da bo 2026-11-19: nay la Big Trade tu lenh don, lich su khong co so lieu), colour (B = buy/xanh, S = sell/do; exh: T = dinh, B = day).
Chay: python export_marks.py   (tu sinh F_m5.pkl / E_m5.pkl neu chua co). Them --floor N de thu san side>=N (mac dinh 9 nhu C#)."""
import sys; sys.path.insert(0,'.')
import os, pandas as pd
from common import *
from feats import build; from exh_feats import exh_table
from score import sample; from rules import *
from final_eval import P
floor=9
if '--floor' in sys.argv: floor=float(sys.argv[sys.argv.index('--floor')+1])
D,B=load()
if not os.path.exists('F_m5.pkl'): build(D,B).to_pickle('F_m5.pkl'); exh_table(D,B).to_pickle('E_m5.pkl')
F=pd.read_pickle('F_m5.pkl'); S=sample(F); E=pd.read_pickle('E_m5.pkl'); Es=E[E.t.isin(SAMPLE)]
dot=dot_rule2(S,**P['dot']); exh=exh_rule(Es,**P['exh'])
print('no floor: dot',len(dot),'exh',len(exh))
dotf=dot[dot.side>=floor]
print('floor',floor,': dot',len(dotf))
rows=[]
for r in dotf.itertuples(): rows.append((r.datetime[11:],r.tk,'dot',r.col))
for r in exh.itertuples():
    b=B.loc[r.t]; ext=round(b.high*10) if r.side=='T' else round(b.low*10)
    rows.append((r.t[11:],int(ext),'exh',r.side))
out=pd.DataFrame(rows,columns=['bar','tick','type','colour']).sort_values(['bar','type','tick','colour'])
out.to_csv('marks_python_26bars.csv',index=False)
print(out.type.value_counts().to_dict())
