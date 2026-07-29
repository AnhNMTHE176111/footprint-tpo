#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHASE 0 — Feature-lift tren 140 lenh RUNNER THAT (CBR 112 / QUAY_DAU 28,
RunnerSignal_signals.csv, C# sinh). (So dung la 140, khong phai 148 — sua 2026-07-29.)
Muc tieu: tim subset nao co ky vong (EV) am/duong manh -> ung vien BO LOC.
Trung thuc: bao ca kich thuoc cell (n) — cell nho = khong tin duoc, chi la gia thuyet."""
import csv, re, statistics as st
from collections import defaultdict

CSV="/home/asl86/Documents/footprint-tpo/data-export/27-7/RunnerSignal_signals.csv"
rows=list(csv.DictReader(open(CSV,encoding="utf-8-sig")))

def rr_of(r):
    try:return float(r['RR'])
    except:return 3.0
def rval(r):
    kq=r['KQ'].strip().upper()
    if kq=='WIN':return rr_of(r)
    if kq=='LOSS':return -1.0
    return None  # open/chua dong

# ---- parse them feature tu text chi_tiet ----
def parse(r):
    d=r['chi_tiet']
    f={}
    m=re.search(r'hồi\s+(\d+)%',d); f['retr']=int(m.group(1)) if m else None
    m=re.search(r'leg\s+([\d.]+)giá',d); f['leg']=float(m.group(1)) if m else None
    m=re.search(r'VSA\s+([\d.]+)x',d); f['vsa_txt']=float(m.group(1)) if m else None
    f['absorb']='hấp thụ' in d
    f['wick']='rút râu' in d
    f['vuong_vung']='vướng vùng' in d or (r['tp_vuong_vung'].strip() not in('-','',))
    f['color']='tím' if 'tím' in d else ('xanh' if 'xanh' in d else ('đỏ' if 'đỏ' in d else '?'))
    # hour tu ngay_gio
    try:f['hour']=int(r['ngay_gio'].split()[1].split(':')[0])
    except:f['hour']=None
    try:f['vsa']=float(r['VSA'])
    except:f['vsa']=None
    f['climax']=r['climax'].strip()
    f['confl']=int(r['co_vung']) if r['co_vung'].strip().lstrip('-').isdigit() else 0
    f['grade']=r['grade'].strip()
    f['branch']=r['nhanh'].strip()
    f['side']=r['huong'].strip()
    f['ym']=r['ngay_gio'][:7]
    return f

for r in rows: r['_f']=parse(r); r['_r']=rval(r)
S=[r for r in rows if r['_r'] is not None]  # settled

def stats(rs):
    if not rs:return (0,0.0,0.0)
    n=len(rs);wr=sum(x['_r']>0 for x in rs)/n;ev=sum(x['_r'] for x in rs)/n
    return (n,wr,ev)

n,wr,ev=stats(S)
print("="*78)
print(f"BASELINE — {len(rows)} lenh, settled {n} (WIN/LOSS), open {len(rows)-n}")
print(f"  WR {wr*100:.0f}% · EV {ev:+.3f}R/lenh · tong {sum(x['_r'] for x in S):+.1f}R")
print("="*78)

# ---- phan bo + WR theo cot chinh ----
def group(keyfn,title,minn=4):
    print(f"\n### {title}")
    print(f"  {'gia tri':<16}{'n':>5}{'WR':>6}{'EV':>9}{'tongR':>9}")
    g=defaultdict(list)
    for r in S:g[keyfn(r)].append(r)
    for k in sorted(g,key=lambda k:-stats(g[k])[2]):
        nn,ww,ee=stats(g[k]); tag=' ⚠ncell nho' if nn<minn else ''
        print(f"  {str(k):<16}{nn:>5}{ww*100:>5.0f}%{ee:>+9.3f}{sum(x['_r'] for x in g[k]):>+9.1f}{tag}")

group(lambda r:r['_f']['branch'],"NHANH (CBR RR3 vs QUAY_DAU RR1.5)")
group(lambda r:r['_f']['side'],"HUONG")
group(lambda r:r['_f']['confl'],"HOP LUU (so vung)")
group(lambda r:r['_f']['grade'],"GRADE")
group(lambda r:r['_f']['climax'],"CLIMAX (cot)")
group(lambda r:r['_f']['color'],"MAU VSA (text)")
group(lambda r:r['_f']['absorb'],"HAP THU (text 'hấp thụ ✓')")
group(lambda r:r['_f']['wick'],"RUT RAU (text)")
group(lambda r:r['_f']['vuong_vung'],"TP VUONG VUNG")
group(lambda r:r['_f']['ym'],"THANG")
def vsabk(r):
    v=r['_f']['vsa']
    if v is None:return '?'
    return '<1.5' if v<1.5 else('1.5-2.0' if v<2.0 else('2.0-3.0' if v<3.0 else '>=3.0'))
group(vsabk,"VSA muc")
def retrbk(r):
    v=r['_f']['retr']
    if v is None:return 'n/a(rev)'
    return '<50%' if v<50 else('50-70%' if v<70 else('70-90%' if v<90 else '>=90%'))
group(retrbk,"RETRACE (CBR)")
def legbk(r):
    v=r['_f']['leg']
    if v is None:return 'n/a(rev)'
    return '<3' if v<3 else('3-6' if v<6 else '>=6')
group(legbk,"LEG size (gia)")
def hourbk(r):
    h=r['_f']['hour']
    if h is None:return '?'
    if 7<=h<14:return 'A(07-14)'
    if 14<=h<19:return 'Au(14-19)'
    if 19<=h<24 or h<2:return 'My(19-02)'
    return 'dem(02-07)'
group(hourbk,"PHIEN (theo gio hien thi)")

# ---- filter lift: bo subset xau -> ky vong toan tap tang bao nhieu ----
print("\n"+"="*78)
print("LIFT khi BO tung subset (chi giu subset con lai) — sort theo EV moi")
print("="*78)
print(f"  {'BO subset':<34}{'con_n':>6}{'WR':>6}{'EV':>9}{'d_tongR':>9}")
tests={
 "bo CBR retrace>=90%":       lambda r:not(r['_f']['branch']=='CBR' and (r['_f']['retr'] or 0)>=90),
 "bo CBR retrace<50%":        lambda r:not(r['_f']['branch']=='CBR' and (r['_f']['retr'] or 99)<50),
 "bo TP vuong vung":          lambda r:not r['_f']['vuong_vung'],
 "bo VSA<1.5":                lambda r:not((r['_f']['vsa'] or 9)<1.5),
 "bo VSA>=3.0 (climax qua)":  lambda r:not((r['_f']['vsa'] or 0)>=3.0),
 "chi giu co absorption":     lambda r:r['_f']['absorb'],
 "chi giu grade A":           lambda r:r['_f']['grade']=='A',
 "bo hop luu 0":              lambda r:r['_f']['confl']>=1,
 "chi giu CBR (bo reversal)": lambda r:r['_f']['branch']=='CBR',
 "chi giu reversal":          lambda r:r['_f']['branch']=='QUAY_DAU',
 "bo phien dem":              lambda r:hourbk(r)!='dem(02-07)',
 "bo leg>=6 (CBR)":           lambda r:not(r['_f']['branch']=='CBR' and (r['_f']['leg'] or 0)>=6),
 "chi giu co wick(rut rau)":  lambda r:r['_f']['wick'],
}
base_tot=sum(x['_r'] for x in S)
res=[]
for name,pred in tests.items():
    keep=[r for r in S if pred(r)]
    nn,ww,ee=stats(keep)
    res.append((name,nn,ww,ee,sum(x['_r'] for x in keep)-base_tot))
for name,nn,ww,ee,dR in sorted(res,key=lambda x:-x[3]):
    tag=' ⚠it lenh' if nn<max(20,0.4*n) else ''
    print(f"  {name:<34}{nn:>6}{ww*100:>5.0f}%{ee:>+9.3f}{dR:>+9.1f}{tag}")
print(f"\n  (baseline giu HET: n={n}, EV {ev:+.3f}, tong {base_tot:+.1f}R)")
