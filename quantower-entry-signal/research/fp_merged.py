#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FEED GHEP: dxFeed OHLC (co Open/Close) + footprint sample.csv (delta/bid-ask tung muc + max_one_trade).
Khop datetime CHINH XAC 99%, gia footprint 100% nam trong range dxFeed => cung instrument (vang), 6 thang.
Cho ra B (list bar) CUNG SHAPE nhu entry_dxfeed + cac truong DELTA THAT:
   b['delta']  = tong delta bar (ask_vol - bid_vol cong don) — THAT, khong proxy
   b['ddom']   = delta / volume_footprint  (do ap dao delta, [-1,1])
   b['bid'],b['ask'] = tong bid_vol / ask_vol bar
   b['mot']    = max_one_trade lon nhat trong bar (lenh don lon nhat) — de loc BIG TRADE
   b['levels'] = {price: dict(bid,ask,vol,delta,mot,trades)}  — cho absorption/imbalance tung muc
   b['v_fp']   = tong volume footprint (dung cho ty le delta; 'v' van la volume dxFeed cho VSA)
Derived (vma/vratio/vwap/since_gap/trend/brat/cpos...) TINH LAI tren chuoi da loc (6 thang) cho nhat quan.
USE_DELTA cua entry_dxfeed = True se kich hoat gate delta THAT."""
import csv,sys
from datetime import datetime,timedelta
sys.path.insert(0,"/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_dxfeed as E
TICK=E.TICK
SAMPLE="/home/asl86/Documents/footprint-tpo/data-export/27-7/sample.csv"
VSA_MA=E.VSA_MA; TREND_LB=480

def load_footprint():
    """Gom footprint sample.csv theo bar -> {dt: dict(vol,delta,bid,ask,mot,trades,levels)}."""
    perbar={}
    for row in csv.DictReader(open(SAMPLE,encoding='utf-8-sig')):
        dt=datetime.strptime(row['datetime'],'%Y-%m-%d %H:%M:%S')
        p=round(float(row['price']),1)
        bid=float(row['bid_vol']);ask=float(row['ask_vol']);vol=float(row['volume'])
        dl=float(row['delta']);tr=float(row['trades']);mot=float(row['max_one_trade'])
        fb=perbar.get(dt)
        if fb is None:fb=perbar[dt]=dict(vol=0.0,delta=0.0,bid=0.0,ask=0.0,mot=0.0,trades=0.0,levels={})
        fb['vol']+=vol;fb['delta']+=dl;fb['bid']+=bid;fb['ask']+=ask;fb['trades']+=tr
        fb['mot']=max(fb['mot'],mot)
        lv=fb['levels'].get(p)
        if lv is None:lv=fb['levels'][p]=dict(bid=0.0,ask=0.0,vol=0.0,delta=0.0,mot=0.0,trades=0.0)
        lv['bid']+=bid;lv['ask']+=ask;lv['vol']+=vol;lv['delta']+=dl;lv['trades']+=tr;lv['mot']=max(lv['mot'],mot)
    return perbar

def load_merged():
    """Giu CHUOI dxFeed DAY (lien tuc) trong khoang co footprint; DINH delta vao bar nao co footprint.
    Bar khong co footprint: has_delta=False, delta=None (tin hieu van ban binh thuong tren nen;
    cac loc dua-tren-delta chi ap khi has_delta). Tranh gap gia -> giu du so luong lenh."""
    D=E.load_m1()
    perbar=load_footprint()
    lo_dt=min(perbar);hi_dt=max(perbar)
    B=[b for b in D if lo_dt<=b['dt']<=hi_dt]     # dxFeed day trong cua so footprint (giu derived goc)
    got=0
    for b in B:
        fb=perbar.get(b['dt'])
        if fb:
            got+=1
            b['delta']=fb['delta'];b['v_fp']=fb['vol'];b['bid']=fb['bid'];b['ask']=fb['ask']
            b['mot']=fb['mot'];b['trades_fp']=fb['trades'];b['levels']=fb['levels']
            b['ddom']=fb['delta']/fb['vol'] if fb['vol']>0 else 0.0
            b['has_delta']=True
        else:
            b['delta']=None;b['v_fp']=None;b['bid']=None;b['ask']=None;b['mot']=0.0
            b['trades_fp']=None;b['levels']={};b['ddom']=None;b['has_delta']=False
    print(f"[fp_merged] dxFeed day {len(B)} bar trong [{lo_dt}..{hi_dt}], co delta {got} ({100*got/len(B):.0f}%)")
    return B

if __name__=='__main__':
    B=load_merged()
    from collections import Counter
    print(f"merged bars={len(B)} | {B[0]['dt']} -> {B[-1]['dt']}")
    print("theo thang:",dict(sorted(Counter(b['ym'] for b in B).items())))
    # sanity delta (chi bar co delta)
    import statistics as st
    Bd=[b for b in B if b['has_delta'] and b['v_fp']>0]
    dd=[b['ddom'] for b in Bd]
    print(f"ddom: trung vi {st.median(dd):+.2f} | |ddom|>0.25: {100*sum(abs(x)>0.25 for x in dd)/len(dd):.0f}% | |ddom|>0.5: {100*sum(abs(x)>0.5 for x in dd)/len(dd):.0f}%")
    nmot=sum(1 for b in Bd if b['mot']>0)
    print(f"'mot'>0: {100*nmot/len(Bd):.0f}% bar co delta | #levels trung binh {st.mean(len(b['levels']) for b in Bd):.1f}")
    agree=sum(1 for b in Bd if (b['delta']>0)==(b['c']>=b['o']));print(f"delta cung dau nen: {100*agree/len(Bd):.0f}%")
