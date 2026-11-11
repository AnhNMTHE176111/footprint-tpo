"""Do bong CORVEN tren anh: tim cham tron xanh/do/tim, doi sang (nen UTC, gia) bang calib.json."""
import json
from bubble_common import *
from scipy import ndimage as ndi
S="C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/14112285-cd5a-4717-90f2-b4fe405421be/scratchpad"
PROTO={'xanh':(100,100,250),'do':(214,4,0),'tim':(204,98,236)}
def blobs(a, color, x0=60,x1=1375,y0=275,y1=712, tol=70, rmin=1.9):
    p=np.array(PROTO[color])
    d=np.sqrt(((a-p)**2).sum(axis=2))
    m=d<tol
    m[:y0]=False; m[y1:]=False; m[:, :x0]=False; m[:, x1:]=False
    dt=ndi.distance_transform_edt(m)
    mx=ndi.maximum_filter(dt,size=5)
    pk=(dt==mx)&(dt>=rmin)
    lab,n=ndi.label(pk)
    out=[]
    for i in range(1,n+1):
        ys,xs=np.where(lab==i)
        cx,cy,r=xs.mean(),ys.mean(),dt[ys[0],xs[0]]
        # loai net ngang dai (duong vien hop chu nhat): chay ngang qua tam > 3.2*duong kinh
        row=m[int(round(cy)),:]; xi=int(round(cx)); l=xi; rr=xi
        while l>0 and row[l-1]: l-=1
        while rr<len(row)-1 and row[rr+1]: rr+=1
        col_=m[:,xi]; u=int(round(cy)); dn=u
        while u>0 and col_[u-1]: u-=1
        while dn<len(col_)-1 and col_[dn+1]: dn+=1
        w=rr-l+1; h=dn-u+1
        if w>3.0*max(h,6): continue
        out.append((cx,cy,r))
    # NMS: drop peaks closer than 0.8*max radius to a bigger one
    out.sort(key=lambda t:-t[2]); keep=[]
    for q in out:
        if all((q[0]-k[0])**2+(q[1]-k[1])**2 > (0.9*max(q[2],k[2]))**2 for k in keep): keep.append(q)
    return keep
if __name__=='__main__':
    cal=json.load(open('calib.json')); b=load_bars(); _,_,_,ROW=minute_grid(b)
    rows=[]
    for n,c in cal.items():
        a=np.asarray(Image.open(S+'/hi/%s.png'%n).convert('RGB')).astype(int)
        for col in PROTO:
            for x,y,r in blobs(a,col,y1=c['y1']):
                k=int(round((x-c['x0'])/c['s']))
                if abs(x-(c['x0']+c['s']*k))>c['s']*0.35: continue
                idx=slot_row(c,k,ROW)
                if idx is None: continue
                price=(y-c['a'])/c['bb']
                rows.append(dict(frame=n,color=col,x=round(x,1),y=round(y,1),r=round(r,2),slot=k,idx=idx,utc=str(b.datetime[idx]),price=round(price,2)))
    df=pd.DataFrame(rows); df.to_csv('bubbles_raw.csv',index=False)
    print(len(df)); print(df.groupby(['frame','color']).size().unstack(fill_value=0))
    print(df.r.describe()); print(np.histogram(df.r,bins=[2.4,3,3.5,4,5,6,7,8,10,12,15,30]))
