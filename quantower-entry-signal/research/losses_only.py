#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tach RIENG 64 lenh THUA ngoai phien chet -> file gon de user tag tay.
Chi giu cot can NHIN + 2 cot dien. Sort theo thoi gian."""
import csv
SRC="/home/asl86/Documents/footprint-tpo/data-export/27-7/runner_review.csv"
OUT="/home/asl86/Documents/footprint-tpo/data-export/27-7/runner_LOSS_can_review.csv"
rows=list(csv.DictReader(open(SRC,encoding="utf-8-sig")))
# residual = KQ LOSS va KHONG bi loc phien chet
keep=[r for r in rows if r['KQ']=='LOSS' and not r['loc_phien_chet'].strip()]
cols=["stt","ngay_gio","phien","nhanh","huong","entry","SL","TP","VSA","hop_luu",
      "grade","retrace","leg_gia","hap_thu","rut_rau","tp_vuong_vung","chi_tiet",
      "diem_1_5(dien)","ly_do(dien)"]
with open(OUT,"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore"); w.writeheader()
    for r in keep: w.writerow(r)
print(f"Da xuat {len(keep)} lenh THUA -> {OUT}")
# phan bo theo nhanh + phien de user biet nhom nao nhieu
from collections import Counter
print("  theo nhanh:", dict(Counter(r['nhanh'] for r in keep)))
print("  theo phien:", dict(Counter(r['phien'] for r in keep)))
