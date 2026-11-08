import json,os,sys,time
from cdp import B
BASE='file:///C:/Users/anhla/OneDrive/Documents/footprint-tpo/cuu-am-chan-kinh/'
OUT='C:/Users/anhla/OneDrive/Documents/footprint-tpo/cuu-am-chan-kinh/docs/shots/'
os.makedirs(OUT,exist_ok=True)
shoot='--noshot' not in sys.argv
b=B(); R={}
MINFONT=r"""(()=>{const out={};const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
while(n=w.nextNode()){if(!n.textContent.trim())continue;const e=n.parentElement;const cs=getComputedStyle(e);if(cs.display=='none'||cs.visibility=='hidden')continue;
const r=e.getBoundingClientRect();if(r.width==0)continue;const f=parseFloat(cs.fontSize);if(f<14){const k=f+'px '+(e.className||e.tagName);out[k]=(out[k]||0)+1}}return out})()"""
for page in [p for p in ['index.html','chi-tiet.html'] if ('--only-index' not in sys.argv or p=='index.html')]:
  for (w,h,mob,dev) in [(1280,900,False,'desktop'),(390,844,True,'mobile')]:
    for dark in [False,True]:
      key=f"{page.split('.')[0]}-{dev}-{'dark' if dark else 'light'}"
      b.setup(w,h,dark,mob); b.go(BASE+page)
      r={}
      r['scrollW']=b.ev('document.documentElement.scrollWidth'); r['clientW']=b.ev('document.documentElement.clientWidth')
      r['wide']=b.ev("[...document.querySelectorAll('body *')].filter(e=>{const x=e.getBoundingClientRect();return x.right>document.documentElement.clientWidth+1 && getComputedStyle(e).position!='fixed' && !e.closest('nav.toc ol')}).slice(0,8).map(e=>e.tagName+'.'+e.className+' '+Math.round(e.getBoundingClientRect().right))")
      r['small']=b.ev(MINFONT)
      r['imgs_bad']=b.ev("[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src)")
      r['nimg']=b.ev("document.images.length")
      r['fail']=[e['params'].get('response',{}).get('url') for e in b.events if e.get('method')=='Network.responseReceived' and e['params']['response'].get('status',200)>=400]
      r['lfail']=[e['params'].get('errorText')+' '+str(e['params'].get('requestId')) for e in b.events if e.get('method')=='Network.loadingFailed']
      r['console']=[e['params']['entry']['text'] for e in b.events if e.get('method')=='Log.entryAdded' and e['params']['entry']['level']=='error']
      r['exc']=[e['params']['exceptionDetails'].get('text') for e in b.events if e.get('method')=='Runtime.exceptionThrown']
      H=b.ev('document.documentElement.scrollHeight'); r['H']=H
      if dark: r['bg']=b.ev("getComputedStyle(document.body).backgroundColor"); r['imgfilter']=b.ev("document.images[0]?getComputedStyle(document.images[0]).filter:''")
      if shoot:
        y=0;k=1
        while y<H:
          b.ev(f"window.scrollTo(0,{y})"); time.sleep(.25)
          sy=b.ev('window.scrollY')
          b.shot(OUT+f"{key}-{k}.png",sy,w,h); k+=1
          if sy+h>=H: break
          y+=h-60
        r['shots']=k-1
      R[key]=r; print(key,json.dumps(r,ensure_ascii=False)[:1500]); sys.stdout.flush()
b.close()
json.dump(R,open(os.path.join(__import__('tempfile').gettempdir(),'ui_result.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
