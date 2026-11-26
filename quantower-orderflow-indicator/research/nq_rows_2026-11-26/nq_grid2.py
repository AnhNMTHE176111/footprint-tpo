exec(open(r'C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/ce3fca11-3030-4b09-9b13-33a6dd7ee683/scratchpad/nq_dots_cmp.py').read().split("print('CORVEN")[0])
res=[]
for G,offs in ((4,range(4)),(8,range(8))):
 for OFF in offs:
  for k in (1.6,2.0,2.4,2.8,3.2):
   for w in (0,1,2,4):
    for h in (-1,0,2,6):
      tol=1.25 if G==4 else 2.0
      o=run(G,k,w,h,9); tp,fp,fn=score(o,tol)
      res.append((2*tp/(2*tp+fp+fn),tp,fp,fn,G,OFF,k,w,h))
res.sort(reverse=True)
for G in (4,8):
  print('--- G',G)
  for r in [x for x in res if x[4]==G][:6]: print('F1 %.3f khop %d thua %d sot %d | G%d lech%d k%.1f w%d che%d'%r)
