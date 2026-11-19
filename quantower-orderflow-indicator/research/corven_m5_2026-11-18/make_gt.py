"""Build gt_corven_m5.csv from the pixel measurements (see README / results_iter.md for method).
Axis (fitted on 26 grid lines, max err 0.05): price = 3792.8228 - 0.0723329*y.  Offset vs our data = 0.00 (candle highs match to 0.03)."""
import csv, math
from pathlib import Path
HERE=Path(__file__).resolve().parent
price=lambda y:3792.8228-0.0723329*y
def tstr(k): m=15+5*k; return f"2026-11-18 {12+m//60:02d}:{m%60:02d}"
# big circles: (bar k, colour, cy px, radius px, confidence)
CIRC=[(0,'pink',253,12,'high'),(3,'pink',347,12,'high'),(4,'pink',441,22,'med'),(4,'pink',453,22,'med'),
(6,'pink',544,12,'high'),(6,'pink',568,17,'high'),(7,'pink',586,9,'med'),(8,'pink',616,10,'high'),
(9,'pink',501,13,'high'),(9,'lblue',525,11,'high'),(9,'lblue',592,14,'med'),(9,'lblue',613,14,'med'),
(10,'lblue',371,11,'high'),(11,'lblue',270,11,'high'),(11,'lblue',311,11,'high'),(12,'pink',289,18,'high'),(12,'lblue',348,11,'high'),
(13,'lblue',317,13,'high'),(14,'pink',264,10,'high'),(15,'pink',131,10,'med'),(15,'pink',148,20,'high'),(15,'lblue',181,11,'high'),
(19,'pink',24,15,'high'),(19,'pink',57,18,'high'),(25,'lblue',205,13,'high')]
# dot blobs: (k, colour, y0, y1)  [red=Bid, blue=Ask]
BLOB=[(0,'B',253,261),(2,'R',352,358),(3,'R',364,377),(3,'B',348,362),(4,'R',460,516),(5,'R',540,548),(6,'R',571,599),(6,'B',546,557),
(7,'R',605,624),(8,'R',651,660),(14,'B',225,248),(21,'B',81,93),(22,'B',78,84),(24,'B',174,191),(24,'R',194,198),(25,'R',194,203)]
D=9.5; SP=7.0
TOP=[4,6,7,15,18]; BOT=[0,11,13,17,18,19]
rows=[]
for k,c,cy,r,conf in CIRC: rows.append((tstr(k),'big',c,round(price(cy),2),r,'','',1,conf))
for k,c,a,b in BLOB:
    h=b-a+1; n=max(1,round((h-D)/SP)+1)
    rows.append((tstr(k),'dot',{'R':'red','B':'blue'}[c],round(price((a+b)/2),2),'',a,b,n,'med' if h>25 else 'high'))
for k in TOP: rows.append((tstr(k),'exh_top','orange','','','','',1,'high'))
for k in BOT: rows.append((tstr(k),'exh_bot','cyan','','','','',1,'high'))
for typ,have in (('big',{r[0] for r in rows if r[1]=='big'}),('dot',{r[0] for r in rows if r[1]=='dot'}),('exh_top',{r[0] for r in rows if r[1]=='exh_top'}),('exh_bot',{r[0] for r in rows if r[1]=='exh_bot'})):
    for k in range(26):
        if tstr(k) not in have: rows.append((tstr(k),'empty_'+typ,'','','','','',0,'high'))
rows.sort(key=lambda r:(r[0],r[1]))
with open(HERE/'gt_corven_m5.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow('bar_time,type,colour,price_centre,radius_px,blob_y0_px,blob_y1_px,n_est,confidence'.split(',')); w.writerows(rows)
for t in ('big','dot','exh_top','exh_bot'): print(t,sum(1 for r in rows if r[1]==t),'empty bars',sum(1 for r in rows if r[1]=='empty_'+t))
print('dot est n',sum(r[7] for r in rows if r[1]=='dot'))
