import sys,json
from bubble_common import *
from PIL import ImageDraw
S="C:/Users/anhla/AppData/Local/Temp/claude/39bcbe610c8d657f/14112285-cd5a-4717-90f2-b4fe405421be/scratchpad"
def overlay(n,box,scale=2.0,out=None,raw='bubbles_raw.csv'):
    df=pd.read_csv(raw); df=df[df.frame==n]
    im=Image.open(S+'/hi/%s.png'%n).convert('RGB')
    c=im.crop(box).resize((int((box[2]-box[0])*scale),int((box[3]-box[1])*scale)),Image.LANCZOS)
    d=ImageDraw.Draw(c)
    for _,r in df.iterrows():
        if box[0]<=r.x<=box[2] and box[1]<=r.y<=box[3]:
            X=(r.x-box[0])*scale;Y=(r.y-box[1])*scale;R=r.r*scale+4
            d.ellipse((X-R,Y-R,X+R,Y+R),outline=(0,160,0),width=1)
    c.save(out or S+'/ov_%s.png'%n)
if __name__=='__main__':
    n=sys.argv[1]; box=tuple(int(v) for v in sys.argv[2:6]); overlay(n,box,float(sys.argv[6]) if len(sys.argv)>6 else 2.0)
