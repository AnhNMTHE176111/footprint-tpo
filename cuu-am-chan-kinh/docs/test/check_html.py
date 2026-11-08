# HTML hợp lệ (html5lib, strict) + mọi link chi-tiet#id có đích + mọi ảnh tồn tại — vòng 2.
import html5lib,re,os
D=r"C:/Users/anhla/OneDrive/Documents/footprint-tpo/cuu-am-chan-kinh/"
for f in ['index.html','chi-tiet.html']:
    p=html5lib.HTMLParser(strict=False); p.parse(open(D+f,encoding='utf-8').read())
    print(f,'html5lib errors:',len(p.errors),p.errors[:3])
ct=open(D+'chi-tiet.html',encoding='utf-8').read(); ix=open(D+'index.html',encoding='utf-8').read()
ids=re.findall(r'id="([^"]+)"',ct); print('dup ids',[i for i in set(ids) if ids.count(i)>1])
miss=[a for a in re.findall(r'chi-tiet\.html#([^"]+)"',ix)+re.findall(r'href="#([^"]+)"',ct) if a not in ids]
print('links',len(re.findall(r'chi-tiet\.html#',ix)),'index +',len(re.findall(r'href="#',ct)),'toc/in-page; missing',miss)
imgs=set(re.findall(r'src="(img/[^"]+)"',ct)); print('imgs',len(imgs),'missing',[i for i in imgs if not os.path.exists(D+i)])
