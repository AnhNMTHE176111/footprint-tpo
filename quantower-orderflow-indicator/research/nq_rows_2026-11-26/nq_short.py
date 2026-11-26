exec(open(r'C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/ce3fca11-3030-4b09-9b13-33a6dd7ee683/scratchpad/nq_dots_cmp.py').read().split("print('CORVEN")[0])
import statistics as st
cf={'cua ban (1 tick, k2,0, moi muc gia, san9)':(1,0,2.0,0,2,9,False),
    'mac dinh (1 tick, k2,0, w=bien/6)':(1,0,2.0,0,2,9,True),
    'hang 2 diem (k1,6 w1)':(8,5,1.6,1,-1,9,False)}
outs={}
for n,(G,off,k,w,h,fl,ad) in cf.items():
  globals()['OFF']=off; outs[n]=run(G,k,w,h,fl,ad)
win=[vn(d) for d in keys if '2026-11-06 09:09'<=d<='2026-11-06 09:24']
print('gio  ', ' | '.join(cf.keys()))
for t in win: print(t, [len(outs[n].get(t,[])) for n in cf])
print('tong', [sum(len(outs[n].get(t,[])) for t in win) for n in cf])
# median baseline vs short bar cells (1 tick)
med=collections.deque(maxlen=20)
for d in keys:
  lv=rows(d,1) if True else None
  globals()['OFF']=0
  lv=rows(d,1); vols=[a+b for a,b in lv.values() if a+b>0]
  if '2026-11-06 09:12'<=d<='2026-11-06 09:20':
    B=sum(med)/len(med); mx=max(max(a,b) for a,b in lv.values())
    print(vn(d),'so tick',len(lv),'nen B=%.1f nguong=%.1f'%(B,max(2*B,9)),'o lon nhat',mx,'so o >= nguong',sum((a>=max(2*B,9))+(b>=max(2*B,9)) for a,b in lv.values()))
  med.append(st.median(vols))
