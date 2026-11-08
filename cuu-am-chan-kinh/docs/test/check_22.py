# So khớp 2.2 (bản rút gọn, plan mục 2b) giữa plan, cửu âm chân kinh.md và index.html — vòng 2.
import re,html,unicodedata
R=r"C:/Users/anhla/OneDrive/Documents/footprint-tpo/"
def n(s):
    s=unicodedata.normalize('NFC',s); s=re.sub(r'<(span|a) class="go"[^>]*>.*?</(span|a)>','',s)
    s=re.sub(r'<[^>]+>','',s); s=html.unescape(s); s=s.replace('**','').replace('*','')
    s=re.sub(r'^\s*>\s*','',s); s=re.sub(r'^\s*-\s*(\[ \]\s*)?','',s)
    return re.sub(r'\s+',' ',s).strip()
def lines(txt):
    out=[]
    for l in txt.splitlines():
        if not l.strip(): continue
        x=n(l)
        if out and out[-1].startswith('⛔') and not x.startswith(('①','②','③','④')): out[-1]+=' '+x; continue
        out.append(x)
    return out
plan=open(R+'plans/CUU-AM-CHAN-KINH-plan.md',encoding='utf-8').read()
sec=plan.split('### 2b')[1].split('**2.2 Follow theo Orderflow (không cản tàu)**')[1].split('Thay bộ đếm')[0]
P=lines(sec)
md=open(R+'cửu âm chân kinh.md',encoding='utf-8').read()
M=lines(md.split('2.2 Follow theo Orderflow (không cản tàu)')[1].split('Khi đấu giá xong')[0])
h=open(R+'cuu-am-chan-kinh/index.html',encoding='utf-8').read()
hs=h.split('id="h-22"')[1].split('<div class="tools">')[0]
H=[n(m.group(1) or m.group(2) or m.group(3)) for m in re.finditer(r'<p class="(?:grp|corven)">(.*?)</p>|<li>(.*?)</li>|<p class="stop">(.*?)</p>',hs,re.S)]
print(len(P),len(M),len(H)); bad=0
for i in range(max(len(P),len(M),len(H))):
    p=P[i] if i<len(P) else None; mm=M[i] if i<len(M) else None; hh=H[i] if i<len(H) else None
    ok=p==mm==hh; bad+=not ok
    print('OK ' if ok else 'DIFF',i,p)
    if not ok: print('   MD:',mm,'\n   HT:',hh)
print('ticks',h.count('type="checkbox"'),'diff',bad)
