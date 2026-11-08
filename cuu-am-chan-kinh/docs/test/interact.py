import time
from cdp import B
BASE='file:///C:/Users/anhla/OneDrive/Documents/footprint-tpo/cuu-am-chan-kinh/'
b=B()
def tap(x,y):
    b.cmd('Input.dispatchTouchEvent',type='touchStart',touchPoints=[{'x':x,'y':y}]); b.cmd('Input.dispatchTouchEvent',type='touchEnd',touchPoints=[]); time.sleep(.6)
b.setup(390,844,False,True); b.cmd('Emulation.setTouchEmulationEnabled',enabled=True,maxTouchPoints=1); b.go(BASE+'index.html')
b.ev("window.__log=[];document.addEventListener('click',e=>__log.push(e.target.tagName+'.'+e.target.className),true)")
for i in [0,5,13,5]:
    b.ev(f"document.querySelectorAll('ul.ck label')[{i}].scrollIntoView({{block:'center',behavior:'instant'}})"); time.sleep(.5)
    r=b.ev(f"(()=>{{const r=document.querySelectorAll('ul.ck label')[{i}].getBoundingClientRect();return [r.x+4,r.y+4]}})()")
    hit=b.ev(f"(()=>{{const e=document.elementFromPoint({r[0]},{r[1]});return e.tagName+'.'+e.className}})()")
    tap(*r)
    print(i,r,hit,b.ev(f"[document.querySelectorAll('ul.ck input')[{i}].checked, document.getElementById('verdict').textContent, scrollY]"))
b.ev("document.getElementById('clear').scrollIntoView({block:'center',behavior:'instant'})"); time.sleep(.5)
r=b.ev("(()=>{const r=document.getElementById('clear').getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()")
tap(*r); print('clear',b.ev("[document.getElementById('verdict').textContent, document.querySelectorAll('ul.ck li.done').length]"))
print(b.ev('__log'))
# phán quyết: tick đủ ①3 + ②2 + ③2 + ④4 bằng click DOM
def verdict(idx):
    b.ev("document.getElementById('clear').click()")
    for i in idx: b.ev(f"document.querySelectorAll('ul.ck input')[{i}].click()")
    return b.ev("document.getElementById('verdict').textContent+' | '+document.getElementById('verdict').className")
print('V-du', verdict([0,1,2,3,4,5,6,10,11,12,13]))
print('V-thieu3', verdict([0,1,2,3,4,5,10,11,12,13]))
print('V-thieu-nen', verdict([0,1,2,3,4,5,6,11,12,13]))
print('V-rong', verdict([]))
# fresh-load hash on desktop
b.setup(1280,900,False,False)
for l in ['b1-range','b3-kietsuc','b4-nen','b4-ngay','khong-vao']:
    b.go('about:blank',wait=.3); b.go(BASE+'chi-tiet.html#'+l,wait=1.5)
    print(l,b.ev(f"[Math.round(document.getElementById('{l}').getBoundingClientRect().top),Math.round(document.querySelector('nav.toc').getBoundingClientRect().bottom)]"))
b.close()
