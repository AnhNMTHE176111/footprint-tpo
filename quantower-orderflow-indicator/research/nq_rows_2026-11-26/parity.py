exec(open(r'C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/ce3fca11-3030-4b09-9b13-33a6dd7ee683/scratchpad/nq_dots_cmp.py').read().split("print('CORVEN")[0])
OFF=4
py=run(8,1.8,1,-1,9)
cs=collections.defaultdict(list)
for r in csv.DictReader(open(SP+'/nq_marks.csv')):
  if r['kind'] in('dotB','dotS') and '2026-11-06 07:39'<=r['t']<='2026-11-06 09:24':
    cs[vn(r['t']+':00')].append(('B' if r['kind']=='dotB' else 'R',float(r['price'])))
win=[vn(d) for d in keys if '2026-11-06 07:39'<=d<='2026-11-06 09:24']
diff=0
for t in win:
  a=sorted(k for k,_ in py.get(t,[])); b=sorted(k for k,_ in cs.get(t,[]))
  if a!=b: diff+=1; print('lech',t,a,b)
print('so nen lech',diff,'/',len(win),'| tong py',sum(len(py.get(t,[])) for t in win),'cs',sum(len(cs[t]) for t in win))
print('C# vs CORVEN (14:39-16:01):',score(cs,2.0))
print('16:12-16:22 C#:',sum(len(cs[t]) for t in win if '16:12'<=t<='16:22'))
