import sys,json
from PIL import Image, ImageDraw, ImageEnhance
from pathlib import Path
HERE=Path(__file__).resolve().parent
def render(circles,out,box,s=3,enh=4,dots=(),tris=()):
    im=Image.open(HERE/'corven-m5-2026-11-18.png').convert('RGB')
    im=ImageEnhance.Color(im).enhance(enh)
    x0,y0,x1,y1=box
    im=im.crop(box).resize(((x1-x0)*s,(y1-y0)*s),Image.LANCZOS)
    d=ImageDraw.Draw(im)
    for k,col,cy,r in circles:
        xc=22+33*k
        c={'pink':(0,160,0),'lblue':(255,0,255)}[col]
        d.ellipse([(xc-r-x0)*s,(cy-r-y0)*s,(xc+r-x0)*s,(cy+r-y0)*s],outline=c,width=1)
        d.ellipse([(xc-1-x0)*s,(cy-1-y0)*s,(xc+1-x0)*s,(cy+1-y0)*s],fill=c)
    im.save(out)
if __name__=='__main__':
    c=json.load(open(HERE/sys.argv[1]))
    render(c,HERE/sys.argv[2],tuple(map(int,sys.argv[3:7])),int(sys.argv[7]))
