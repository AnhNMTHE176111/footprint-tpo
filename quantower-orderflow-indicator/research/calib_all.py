import json, sys
from bubble_common import *
S="C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/14112285-cd5a-4717-90f2-b4fe405421be/scratchpad"
names='0-19-30 0-24-15 0-28-00 0-31-20 0-33-55 0-34-18 0-35-50 0-40-40 0-41-55 0-46-05 0-50-25 0-53-30 0-54-45 0-58-35 0-59-50 1-02-20 1-04-00 1-05-45 1-07-55'.split()
b=load_bars()
res={}
for n in names:
    im=Image.open(S+'/hi/%s.png'%n)
    out=[]
    for y1 in (614,712):
        c=candles(im,60,1375,275,y1,minlen=6)
        try:
            x0,s,d=slots(c)
            best,kmin=fit(d,b,275,y1)
        except Exception as e:
            print(n,y1,'ERR',e); continue
        out.append((best[0][0],y1,x0,s,len(d),best[0][1],kmin,best[0][2],best[0][3],best[1][0]))
    out.sort()
    o=out[0]
    t0=b.datetime.iloc[0]+pd.Timedelta(minutes=int(o[5]))
    print(n,'cost %.2f next %.2f y1=%d x0=%.1f s=%.2f nslots=%d n0=%d kmin=%d first=%s'%(o[0],o[9],o[1],o[2],o[3],o[4],o[5],o[6],t0))
    res[n]=dict(cost=o[0],y1=o[1],x0=o[2],s=o[3],n0=int(o[5]),kmin=int(o[6]),a=o[7],bb=o[8])
json.dump(res,open('calib.json','w'))
