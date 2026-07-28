#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TASK C — xuat bang REVIEW cho user tag tay (Phase 1 human-in-the-loop).
Nguon: RunnerSignal_signals.csv (148 lenh THAT). Them: phien, co-bi-loc-phien-chet,
cac feature da parse (retrace/leg/absorb/wick), + 2 cot TRONG de user dien: diem_1_5, ly_do.
Xuat UTF-8-BOM de Excel hien tieng Viet dung. Sort theo thoi gian."""
import csv, re
SRC="/home/asl86/Documents/footprint-tpo/data-export/27-7/RunnerSignal_signals.csv"
OUT="/home/asl86/Documents/footprint-tpo/data-export/27-7/runner_review.csv"
rows=list(csv.DictReader(open(SRC,encoding="utf-8-sig")))

def rr(r):
    try:return float(r['RR'])
    except:return 3.0
def rval(r):
    k=r['KQ'].strip().upper()
    return (f"{rr(r):+.1f}" if k=='WIN' else ("-1.0" if k=='LOSS' else ""))
def hour(r):
    try:return int(r['ngay_gio'].split()[1].split(':')[0])
    except:return -1
def phien(h):
    # nhan phien khop khung loc [02,08): DEM = phien chet
    if 2<=h<8:return "DEM"
    if 8<=h<14:return "A"
    if 14<=h<19:return "Au"
    if (19<=h<24) or 0<=h<2:return "My"
    return "?"
def parse(r):
    d=r['chi_tiet']
    m=re.search(r'hồi\s+(\d+)%',d); retr=m.group(1)+'%' if m else ''
    m=re.search(r'leg\s+([\d.]+)giá',d); leg=m.group(1) if m else ''
    return retr,leg,('✓' if 'hấp thụ' in d else ''),('✓' if 'rút râu' in d else '')

hdr=["stt","ngay_gio","phien","loc_phien_chet","nhanh","huong","entry","SL","TP","RR",
     "KQ","R","VSA","climax","hop_luu","grade","retrace","leg_gia","hap_thu","rut_rau",
     "tp_vuong_vung","chi_tiet","diem_1_5(dien)","ly_do(dien)"]
rows.sort(key=lambda r:r['ngay_gio'])
out=[]
for i,r in enumerate(rows,1):
    h=hour(r); ph=phien(h); retr,leg,absb,wick=parse(r)
    dead="BỎ(phiên chết)" if 2<=h<8 else ""
    tvv=r['tp_vuong_vung'].strip(); tvv='' if tvv=='-' else tvv
    out.append([i,r['ngay_gio'],ph,dead,r['nhanh'].strip(),r['huong'].strip(),
        r['entry'],r['SL'],r['TP'],r['RR'],r['KQ'].strip(),rval(r),r['VSA'],
        r['climax'].strip(),r['co_vung'].strip(),r['grade'].strip(),retr,leg,absb,wick,
        tvv,r['chi_tiet'],"",""])

with open(OUT,"w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(hdr); w.writerows(out)

n=len(out); dead=sum(1 for x in out if x[3]); settled=sum(1 for x in out if x[10] in('WIN','LOSS'))
loss=[x for x in out if x[10]=='LOSS' and not x[3]]  # loss NGOAI phien chet = residual quan trong
print(f"Da xuat {n} lenh -> {OUT}")
print(f"  settled {settled} | bi loc phien chet: {dead} | con lai review: {n-dead}")
print(f"  LOSS ngoai phien chet (residual can hieu nhat): {len(loss)} lenh")
print(f"\nHUONG DAN cho user: mo bang trong Excel, chi can dien 2 cot cuoi:")
print(f"  - diem_1_5: 1=setup rac, 5=setup dep (danh gia CHAT LUONG luc vao, KHONG nhin ket qua)")
print(f"  - ly_do: vi sao (vd 'vao giua vung khong co S/R', 'nguoc trend HTF', 'rau dai= hap thu that')")
print(f"  Uu tien tag {len(loss)} lenh LOSS ngoai phien chet truoc — do la cho may KHONG giai thich duoc.")
