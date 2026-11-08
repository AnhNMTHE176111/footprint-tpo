# Vòng 2: 8 ảnh tiêu biểu vào docs/shots, 4 ảnh vào docs/shots-impl, đo khối 2.2 ở 390×844.
import sys,os,time,io
sys.path.insert(0,os.path.dirname(__file__))
from cdp import B
from PIL import Image
BASE='file:///C:/Users/anhla/OneDrive/Documents/footprint-tpo/cuu-am-chan-kinh/'
D='C:/Users/anhla/OneDrive/Documents/footprint-tpo/cuu-am-chan-kinh/docs/'
b=B()
def save(path,y,w,h):
    tmp=path+'.png'; b.shot(tmp,y,w,h); Image.open(tmp).convert('RGB').save(path,'JPEG',quality=78); os.remove(tmp)
for page,H in [('index',None),('chi-tiet',2400)]:
  for (w,vh,mob,dev) in [(1280,900,False,'desktop'),(390,844,True,'mobile')]:
    for dark in [False,True]:
      b.setup(w,vh,dark,mob); b.go(BASE+page+'.html')
      full=b.ev('document.documentElement.scrollHeight')
      save(D+f"shots/{page}-{dev}-{'dark' if dark else 'light'}.jpg",0,w,min(full,H or full))
# đo trên điện thoại
b.setup(390,844,False,True); b.go(BASE+'index.html')
r=b.ev("(()=>{const k=document.getElementById('kb22').getBoundingClientRect();const ul=[...document.querySelectorAll('ul.ck a')].map(a=>Math.round(a.getBoundingClientRect().height));return {top:Math.round(k.top+scrollY),h:Math.round(k.height),items:ul,scrollW:document.documentElement.scrollWidth}})()")
print('kb22',r,'= %.2f màn hình 844'%(r['h']/844))
save(D+'shots-impl/index-mobile-khoi22.jpg',r['top'],390,r['h'])
for i in [0,1,2,3,4,5,6,10,11,12,13]: b.ev(f"document.querySelectorAll('ul.ck input')[{i}].click()")
y=b.ev("Math.round(document.querySelector('.tools').getBoundingClientRect().top+scrollY)-500")
save(D+'shots-impl/index-mobile-du-dieu-kien.jpg',y,390,700)
# cuối trang: nút dính đáy vs dòng cuối
b.ev("window.scrollTo(0,document.documentElement.scrollHeight)"); time.sleep(.4)
print('cuoi', b.ev("(()=>{const c=document.querySelector('.cta').getBoundingClientRect(),s=document.querySelector('.src').getBoundingClientRect(),w=getComputedStyle(document.querySelector('.wrap')).paddingBottom;return {cta:[Math.round(c.top),Math.round(c.bottom)],src:[Math.round(s.top),Math.round(s.bottom)],padBottom:w,ctaH:Math.round(c.height),vh:innerHeight}})()"))
save(D+'shots-impl/index-mobile-cuoi-trang.jpg',b.ev('scrollY'),390,844)
b.setup(390,844,True,True); b.go(BASE+'chi-tiet.html#b4-nen')
save(D+'shots-impl/chi-tiet-mobile-b4-nen-dark.jpg',b.ev('scrollY'),390,844)
# cỡ chữ nhỏ nhất
for pg in ['index','chi-tiet']:
    b.setup(390,844,False,True); b.go(BASE+pg+'.html')
    print(pg,'min font',b.ev("Math.min(...[...document.querySelectorAll('body *')].filter(e=>[...e.childNodes].some(n=>n.nodeType==3&&n.textContent.trim())).map(e=>parseFloat(getComputedStyle(e).fontSize)))"),'scrollW',b.ev('document.documentElement.scrollWidth'))
b.close()
