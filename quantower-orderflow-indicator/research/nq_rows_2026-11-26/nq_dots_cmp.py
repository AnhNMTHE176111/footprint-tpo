import csv,collections,math,statistics as st,sys
SP=r'C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/ce3fca11-3030-4b09-9b13-33a6dd7ee683/scratchpad'
F=r'c:/Users/anhla/OneDrive/Documents/footprint-tpo/data-export/data-footprint/fp_NQZ26_XCME_Time_20260826-20261124_90d.csv'
T=0.25
OFF=0
raw=collections.defaultdict(list)
for r in csv.DictReader(open(F)):
  d=r['datetime']
  if '2026-11-06 05:00'<=d<='2026-11-06 09:40': raw[d].append((round(float(r['price'])/T),float(r['ask_vol']),float(r['bid_vol'])))
keys=sorted(raw)
def vn(d): return '%02d:%s'%(int(d[11:13])+7,d[14:16])
cor=collections.defaultdict(list)
for x in csv.DictReader(open(SP+'/corven_nq_dots.csv')): cor[x['vn']].append((x['kind'],float(x['price'])))
def rows(d,G):
  lv=collections.defaultdict(lambda:[0.0,0.0])
  for t,a,b in raw[d]:
    k=math.floor((t-OFF)/G); lv[k][0]+=a; lv[k][1]+=b
  return lv
def run(G,k,wfix,hide,floor,adaptive=False):
  med=collections.deque(maxlen=20); rng=collections.deque(maxlen=20); out={}
  for d in keys:
    lv=rows(d,G)
    vols=[a+b for a,b in lv.values() if a+b>0]
    if len(med)>=5:
      B=sum(med)/len(med); thr=max(k*B,floor)
      w=max(4,round(sum(rng)/len(rng)/6)) if adaptive else wfix
      ask={t:v[0] for t,v in lv.items()}; bid={t:v[1] for t,v in lv.items()}
      def lm(side,t,v): return all(side.get(t+o,0)<v and side.get(t-o,0)<v for o in range(1,w+1))
      reds=[t for t in lv if bid[t]>0 and bid[t]>=thr and lm(bid,t,bid[t])]
      blues=[t for t in lv if ask[t]>0 and ask[t]>=thr and lm(ask,t,ask[t])]
      blues=[t for t in blues if not any(abs(t-r)<=hide for r in reds)]
      # price of row = center
      c=lambda t:(t*G+OFF+(G-1)/2)*T
      out[vn(d)]=[('B',c(t)) for t in blues]+[('R',c(t)) for t in reds]
    med.append(st.median(vols) if vols else 0); rng.append(max(lv)-min(lv) if lv else 0)
  return out
def score(ours,tol):
  tp=fp=fn=0
  win=[vn(d) for d in keys if '2026-11-06 07:39'<=d<='2026-11-06 09:01']
  for t in win:
    c=list(cor.get(t,[])); o=list(ours.get(t,[]))
    used=set()
    for kind,p in c:
      best=None
      for i,(k2,p2) in enumerate(o):
        if i in used: continue
        if (kind=='V' or kind==k2) and abs(p-p2)<=tol: best=i; break
      if best is None: fn+=1
      else: used.add(best); tp+=1
    fp+=len(o)-len(used)
  return tp,fp,fn
print('CORVEN cham trong cua so:',sum(len(cor[t]) for t in cor if '14:39'<=t<='16:01'))
cfg=[('1 tick, bo co dan (k2,0 w=bien/6 che2 san9) = mac dinh',1,2.0,0,2,9,True),
     ('1 tick, bo Nasdaq (k3,5 w8 che12 san9)',1,3.5,8,12,9,False),
     ('4 tick/hang, luat CORVEN vang (k2,8 w4 che6 san9)',4,2.8,4,6,9,False),
     ('4 tick/hang, bo co dan (k2,0 w=bien/6 che2 san9)',4,2.0,0,2,9,True),
     ('4 tick/hang, k2,4 w4 che2 san9',4,2.4,4,2,9,False),
     ('4 tick/hang, k2,0 w4 che2 san9',4,2.0,4,2,9,False),
     ('4 tick/hang, k2,8 w4 che6 san5',4,2.8,4,6,5,False),
     ('2 tick/hang, k2,8 w4 che6 san9',2,2.8,4,6,9,False)]
for name,G,k,w,h,fl,ad in cfg:
  o=run(G,k,w,h,fl,ad)
  for tol in (2.0,):
    tp,fp,fn=score(o,tol)
    print(f'{name}: khop {tp}, thua {fp}, sot {fn}  (recall {tp/(tp+fn):.2f}, precision {tp/max(1,tp+fp):.2f})')
