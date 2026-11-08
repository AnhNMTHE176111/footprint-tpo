import json,subprocess,time,urllib.request,base64,os,sys,itertools
import websocket
CH=r"C:/Program Files/Google/Chrome/Application/chrome.exe"
PORT=9333
SCR=os.path.dirname(os.path.abspath(__file__))
class B:
    def __init__(s):
        s.p=subprocess.Popen([CH,'--headless=new',f'--remote-debugging-port={PORT}','--user-data-dir='+os.path.join(__import__('tempfile').gettempdir(),'cuu-am-chprof'),'--no-first-run','--hide-scrollbars','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                tabs=json.load(urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json')); break
            except Exception: time.sleep(.2)
        t=[x for x in tabs if x['type']=='page'][0]
        s.ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=60,suppress_origin=True); s.i=itertools.count(1); s.events=[]
        s.cmd('Page.enable'); s.cmd('Runtime.enable'); s.cmd('Network.enable'); s.cmd('Log.enable')
    def cmd(s,m,**p):
        i=next(s.i); s.ws.send(json.dumps({'id':i,'method':m,'params':p}))
        while True:
            r=json.loads(s.ws.recv())
            if r.get('id')==i:
                if 'error' in r: raise RuntimeError(r['error'])
                return r.get('result',{})
            s.events.append(r)
    def ev(s,expr):
        r=s.cmd('Runtime.evaluate',expression=expr,returnByValue=True,awaitPromise=True)
        if 'exceptionDetails' in r: raise RuntimeError(r['exceptionDetails'])
        return r['result'].get('value')
    def setup(s,w,h,dark,mobile):
        s.cmd('Emulation.setDeviceMetricsOverride',width=w,height=h,deviceScaleFactor=1,mobile=mobile)
        s.cmd('Emulation.setEmulatedMedia',features=[{'name':'prefers-color-scheme','value':'dark' if dark else 'light'}])
    def go(s,url,wait=2.5):
        s.events=[]; s.cmd('Page.navigate',url=url); time.sleep(wait)
        s.ev("document.fonts.ready.then(()=>1)")
        # force lazy images
        s.ev("Promise.all([...document.images].map(i=>{i.loading='eager'; return i.complete?1:new Promise(r=>{i.onload=i.onerror=r})})).then(()=>1)")
    def shot(s,path,y,w,h):
        r=s.cmd('Page.captureScreenshot',format='png',captureBeyondViewport=True,clip={'x':0,'y':y,'width':w,'height':h,'scale':1})
        open(path,'wb').write(base64.b64decode(r['data']))
    def close(s):
        try: s.ws.close()
        except: pass
        s.p.kill()
