import re,html,sys,unicodedata
R=r"C:/Users/anhla/OneDrive/Documents/footprint-tpo/"
def norm(s):
    s=unicodedata.normalize('NFC',s)
    s=re.sub(r'<[^>]+>','',s); s=html.unescape(s)
    s=s.replace('**','').replace('“','"').replace('”','"')
    return re.sub(r'\s+',' ',s).strip()
tr={}
for line in open(R+'corven-meet/2026-11-07/transcript.md',encoding='utf-8'):
    m=re.match(r'\s*-\s*\[(\d:\d\d:\d\d)\]\s*(.*)',line)
    if m: tr.setdefault(m.group(1),[]).append(norm(m.group(2)))
src=open(R+'cuu-am-chan-kinh/chi-tiet.html',encoding='utf-8').read()
TR2=norm(open(R+'data-export/messages-with-pro-trader/TRANSCRIPT.md',encoding='utf-8').read())
ok=bad=0
for m in re.finditer(r'<p><span class="ts">([^<]+)</span>(.*?)</p>',src,re.S):
    ts,q=m.group(1),norm(m.group(2))
    if re.fullmatch(r'\d:\d\d:\d\d',ts):
        cands=tr.get(ts)
        if not cands: print('NO-TS',ts,q[:60]); bad+=1; continue
        if any(q==c for c in cands): ok+=1; continue
        # allow HV: prefix stripping or substring
        if any(q in c or c in q for c in cands): print('SUBSTR',ts,'\n  WEB:',q,'\n  TR :',cands[0]); ok+=1; continue
        print('DIFF',ts,'\n  WEB:',q,'\n  TR :',cands); bad+=1
    else:
        parts=[p.strip() for p in re.split(r' / ',re.sub(r'chú thích ảnh.*','',q))]
        miss=[p for p in parts if p and p not in TR2]
        print('MSG',ts,'parts missing:' ,miss if miss else 'none')
print('ok',ok,'bad',bad)
