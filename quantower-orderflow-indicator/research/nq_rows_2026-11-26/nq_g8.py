exec(open(r'C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/ce3fca11-3030-4b09-9b13-33a6dd7ee683/scratchpad/nq_dots_cmp.py').read().split("print('CORVEN")[0])
for off in (4,5):
  OFF=off; r=[]
  for k in (1.4,1.6,1.8,2.0):
    for w in (0,1,2):
      for h in (-1,0,1):
        tp,fp,fn=score(run(8,k,w,h,9),2.0); r.append((2*tp/(2*tp+fp+fn),tp,fp,fn,k,w,h))
  r.sort(reverse=True)
  for x in r[:4]: print('lech',off,'F1 %.3f khop %d thua %d sot %d k%.1f w%d che%d'%x)
