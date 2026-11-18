from PIL import Image
import sys
im=Image.open(sys.argv[1]).convert('RGB'); W,H=im.size
px=im.load()
def cls(p):
    r,g,b=p
    if r>200 and g<205 and b<205 and r-g>22 and abs(g-b)<15 and g>140: return 'pink'
    if b>215 and b-r>18 and 160<r<210 and g<225 and b-g>8: return 'lblue'
    if r>170 and g<90 and b<90: return 'red'
    if b>170 and r<90 and g<170 and b-g>40: return 'blue'
    if r>220 and 120<g<200 and b<80: return 'orange'
    if r<110 and g>150 and b>220 and b-g>25: return 'cyan'
    return None
lab={}
for x in range(0,900):
    for y in range(H):
        c=cls(px[x,y])
        if c: lab[(x,y)]=c
seen=set(); comps=[]
for k,c in lab.items():
    if k in seen: continue
    st=[k]; seen.add(k); pts=[]
    while st:
        p=st.pop(); pts.append(p)
        for d in ((1,0),(-1,0),(0,1),(0,-1)):
            q=(p[0]+d[0],p[1]+d[1])
            if q not in seen and lab.get(q)==c: seen.add(q); st.append(q)
    if len(pts)<6: continue
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    comps.append((c,len(pts),min(xs),max(xs),min(ys),max(ys)))
def price(y): return 3792-(y-12)/14.1
for c,n,x0,x1,y0,y1 in sorted(comps,key=lambda t:(t[2],t[4])):
    xc=(x0+x1)/2; bar=round((xc-22)/33)
    print(f"{c:6s} n={n:4d} bar={bar:2d} x={x0}-{x1} y={y0}-{y1} p={price(y1):.1f}-{price(y0):.1f} pc={price((y0+y1)/2):.1f}")
