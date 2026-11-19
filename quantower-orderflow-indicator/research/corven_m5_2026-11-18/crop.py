import sys
from PIL import Image, ImageEnhance
x0,y0,x1,y1,s,out=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
enh=float(sys.argv[7]) if len(sys.argv)>7 else 1
im=Image.open('corven-m5-2026-11-18.png').convert('RGB').crop((x0,y0,x1,y1))
if enh!=1: im=ImageEnhance.Color(im).enhance(enh)
im=im.resize(((x1-x0)*s,(y1-y0)*s),Image.LANCZOS); im.save(out)
