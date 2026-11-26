import csv,collections,math
NOZ=False
OFF=0
T=0.25
raw=collections.defaultdict(list); bars={}
for r in csv.DictReader(open('fp_NQZ26_XCME_Time_20260826-20261124_90d.csv')):
  d=r['datetime']
  if '2026-11-06 07:25'<=d<='2026-11-06 09:10': raw[d].append((float(r['price']),float(r['ask_vol']),float(r['bid_vol'])))
for r in csv.DictReader(open('fp_NQZ26_XCME_Time_20260826-20261124_90d_bars.csv')):
  d=r['datetime']
  if '2026-11-06 07:25'<=d<='2026-11-06 09:10': bars[d]=(float(r['high']),float(r['low']),float(r['close']))
keys=sorted(raw)
def run(G,ratio,mv,rn=3):
  out=[]
  for d in keys:
    lv=collections.defaultdict(lambda:[0,0])
    for p,a,b in raw[d]:
      k=math.floor((p/T-OFF)/G+1e-9); lv[k][0]+=a; lv[k][1]+=b
    lo=min(lv); hi=max(lv); n=hi-lo+1
    ask=[lv[t][0] if t in lv else 0 for t in range(lo,hi+1)]; bid=[lv[t][1] if t in lv else 0 for t in range(lo,hi+1)]
    for side in (1,-1):
      f=[False]*n
      for i in range(n):
        if side>0 and i>0: dom,opp=ask[i],bid[i-1]
        elif side<0 and i<n-1: dom,opp=bid[i],ask[i+1]
        else: continue
        f[i]=dom>0 and dom>=mv and dom>=ratio*opp-1e-9 and (opp>0 or not NOZ)
      s=None
      for i in range(n+1):
        on=i<n and f[i]
        if on and s is None: s=i
        if not on and s is not None:
          if i-s>=rn:
            zl=((lo+s)*G+OFF)*T; zh=((lo+i)*G+OFF)*T  # row bottom..top
            k=keys.index(d); life=0
            for d2 in keys[k+1:]:
              h,l,c=bars[d2]; life+=1
              if h>=zl and l<=zh-T: break
            out.append((d,side,zl,zh,i-s,life))
          s=None
  return out
import sys
for G,ratio,mv in [(4,2.5,1),(4,2.5,5),(4,3,1),(2,2.5,5),(8,2.5,5)]:
  z=[x for x in run(G,ratio,mv) if '2026-11-06 07:35'<=x[0]<='2026-11-06 09:01']
  print(f'== gop {G} tick/hang, {ratio*100:.0f}%, san {mv}: {len(z)} vung')
  for x in z: print('  VN %02d:%s'%(int(x[0][11:13])+7,x[0][14:16]),'BUY ' if x[1]>0 else 'SELL',x[2],'-',x[3],x[4],'hang, keo',x[5])
print('=====')
C=[('14:45',1,26966,26970),('14:49',1,27008,27012),('14:51',-1,27000,27004),('14:53',1,26985,26988),('14:55',1,27000,27004),
   ('15:07',-1,26998,27004),('15:12',1,26965,26968),('15:11',1,26982,26986),('15:19',1,27016,27022),('15:30',1,26988,26992)]
def vnm(d): return (int(d[11:13])+7)*60+int(d[14:16])
for G in (4,):
 for ratio in (2.5,3.0):
  for mv in (1,2,3,4,5,8):
    z=[x for x in run(G,ratio,mv) if '2026-11-06 07:39'<=x[0]<='2026-11-06 09:01']
    hit=0
    for t,s,lo,hi in C:
      tm=int(t[:2])*60+int(t[3:])
      if any(x[1]==s and abs(vnm(x[0])-tm)<=1 and x[2]<=hi+1 and x[3]>=lo-1 for x in z): hit+=1
    print(f'G{G} {ratio*100:.0f}% san{mv}: {len(z)} vung, khop {hit}/{len(C)} vung CORVEN, vung song >=2 nen {sum(1 for x in z if x[5]>=2)}')
print('== bo ca x vs 0 ==')
NOZ=True
for ratio in (2.5,3.0):
  for mv in (1,2,3,5):
    z=[x for x in run(4,ratio,mv) if '2026-11-06 07:39'<=x[0]<='2026-11-06 09:01']
    hit=0
    for t,s,lo,hi in C:
      tm=int(t[:2])*60+int(t[3:])
      if any(x[1]==s and abs(vnm(x[0])-tm)<=1 and x[2]<=hi+1 and x[3]>=lo-1 for x in z): hit+=1
    print(f'{ratio*100:.0f}% san{mv} (bo x vs 0): {len(z)} vung, khop {hit}/10, song>=2 {sum(1 for x in z if x[5]>=2)}')
print('== dac trung ==')
NOZ=False
OFF=0
z=[x for x in run(4,2.5,1) if '2026-11-06 07:39'<=x[0]<='2026-11-06 09:01']
for x in z:
  tm=vnm(x[0]); lab=any(x[1]==s and abs(tm-(int(t[:2])*60+int(t[3:])))<=1 and x[2]<=hi+1 and x[3]>=lo-1 for t,s,lo,hi in C)
  h,l,c=bars[x[0]]
  # life with "close through" end
  k=keys.index(x[0]); life2=0
  for d2 in keys[k+1:]:
    h2,l2,c2=bars[d2]; life2+=1
    if (x[1]>0 and c2<x[2]) or (x[1]<0 and c2>x[3]-0.25): break
  pos=(( (x[2]+x[3])/2)-l)/max(0.25,h-l)
  print('%s %s %s %.0f-%.0f rows%d life_touch%d life_close%d pos%.2f'%('**' if lab else '  ','%02d:%02d'%(tm//60,tm%60),'B' if x[1]>0 else 'S',x[2],x[3],x[4],x[5],life2,pos))
print('== lech moc ==')
for G in (4,5,6,8):
 for OFF in range(G):
  for mv in (1,3):
    z=[x for x in run(G,2.5,mv) if '2026-11-06 07:39'<=x[0]<='2026-11-06 09:01']
    hit=0
    for t,s,lo,hi in C:
      tm=int(t[:2])*60+int(t[3:])
      if any(x[1]==s and abs(vnm(x[0])-tm)<=1 and x[2]<=hi+1 and x[3]>=lo-1 for x in z): hit+=1
    print(f'G{G} lech{OFF} san{mv}: {len(z)} vung, khop {hit}/10, song>=5 {sum(1 for x in z if x[5]>=5)}')
print('== G8 lech4 ==')
OFF=4
for x in run(8,2.5,1):
  if '2026-11-06 07:39'<=x[0]<='2026-11-06 09:01':
    tm=vnm(x[0]); lab=any(x[1]==s and abs(tm-(int(t[:2])*60+int(t[3:])))<=1 and x[2]<=hi+1 and x[3]>=lo-1 for t,s,lo,hi in C)
    print('**' if lab else '  ','%02d:%02d'%(tm//60,tm%60),'B' if x[1]>0 else 'S',x[2],x[3],x[4],'hang keo',x[5])
