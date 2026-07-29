#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST EntrySignal (ban A scalp) tren DATA MOI dxFeed 9 thang (data-export/27-7/).
================================================================================
KHAC entry_month.py:
  - Data dxFeed CHI co OHLCV, KHONG co Delta / Buy-Sell volume / VSA-decompose.
    => THAY moi gate delta bang HUONG NEN (close>open) + drop ddom/|delta|.
       Edge da chung minh (memory) = HOP LUU>=2 + RETEST-GIU-VUNG + VSA; delta chi la
       cong huong nho => bo delta van test dung SPINE. Live giu nguyen delta.
  - KB2 cham&dao can HAP THU per-level (chi live) => o day chi giu nhanh
    S2-CLIMAX-OVERRIDE (VSA>=climax tai cum) = delta-free, do rieng.
  - Daily levels: TPO-daily chi phu 1 thang => DUNG daily profile TU M1.
  - Bar open time = 'Time left' (UTC). Bao cao THEO THANG => tach May (OOS that,
    khong nam trong 28 ngay fp-m1 6/26-7/25).
  - Filters "goc nhin moi" (RUNNER v5) bat/tat bang CONFIG:
    trend-proxy (close vs close 480 nen), VWAP-align, liquidity-ratio.
Trung thuc: day la XAP XI cho data khong-delta; cross-check bang entry_dxfeed_xcheck.
"""
import csv, statistics as st
from datetime import datetime, timedelta
DIR="/home/asl86/Documents/footprint-tpo/data-export/"; TICK=0.1
DXFILE="27-7/_GCQ26XCEC dxFeed, Time - Time - 1m, 11_3_2025 120000 AM-7_27_2026 105600 PM_8b750702-5f00-4836-bf74-81e2a0c4495f.csv"

# ---- fixed structure params (khop shipped EntrySignal.cs) ----
ARM_DIST_T=20; BUF_T=2; RETEST_BARS=12; RETEST_TOL_T=4
VSA_GATE=1.2; VSA_CLIMAX=2.2; VSA_BREAK=1.2
BODY_STRONG=0.55; WICK_FRAC=0.50; CLOSEPOS_HI=0.55; CLOSEPOS_LO=0.45
SL_BUF_T=2; VSA_MA=20; WARMUP_AFTER_GAP=20
DEDUP_BARS=6; DEDUP_TICKS=6; ZONE_EXPIRE_DAYS=3
CONFLUENCE_TOL_T=7   # cum-gan (shipped ConfluenceTol=7)

# ---- default CONFIG (co the override tung run) ----
BASE=dict(
    RETEST_HOLD_T=0,      # retrace<=100% (low>=zp)
    SL_FLOOR_T=40, SL_CAP_T=60, RR=1.5, NEXTZONE_MINR=2.0, EXTEND=True,
    MIN_CONFL=2, COOLDOWN=15,
    VOL_FLOOR=None,       # None => tu tinh theo percentile lien-thong
    # filters goc nhin moi:
    TREND_ON=False, TREND_LB=480,
    VWAP_ON=False, VWAP_MARGIN=0.0,   # bias VWAP: long chi khi entry>vwap+margin, short khi entry<vwap-margin (gia)
    LIQ_ON=False, LIQ_LB=1000, LIQ_MIN=0.75,
    KB2_CLIMAX=True,      # nhanh cham&dao climax-override (delta-free)
    # feedback user 2026-07-28:
    HOVER_H=None,         # KB1: dai "loanh quanh vung" (gia). None=chat cu; >0 = cho gia dao quanh vung, chi huy khi close pha xa HOVER_H
    SWEEP_ON=False, SWEEP_SPIKE=0.3, SWEEP_REJECT=0.3,  # KB2b: quet qua vung roi rut manh nguoc lai (gia)
    SWEEP_STRICT=False,   # chi bat khi nen TRUOC DA DONG han qua vung (pha that bai) + nen sau rut than manh
    VWAP_KB1ONLY=False,   # bias VWAP CHI ap cho pha&hoi (momentum); tha reversal (fade)
    MONTHS=None,          # None=tat ca; hoac set {'2026-05',...}
)

def load(path,sep=','):
    with open(DIR+path,encoding='utf-8-sig') as f:
        r=csv.reader(f,delimiter=sep); h=next(r); rows=[x for x in r if x and x[0].strip()]
    return h,rows

def fn(x):
    try:return float(x)
    except:return 0.0

def value_area(counts,frac=0.70):
    if not counts:return(None,None,None)
    prices=sorted(counts);w=[counts[p] for p in prices];tot=sum(w)
    if tot<=0:return(None,None,None)
    poc=max(range(len(w)),key=lambda i:w[i]);acc=w[poc];lo=hi=poc;target=tot*frac
    while acc<target and(lo>0 or hi<len(w)-1):
        up=(w[hi+1] if hi<len(w)-1 else 0)+(w[hi+2] if hi<len(w)-2 else 0)
        dn=(w[lo-1] if lo>0 else 0)+(w[lo-2] if lo>1 else 0)
        if hi>=len(w)-1:acc+=dn;lo=max(0,lo-2)
        elif lo<=0:acc+=up;hi=min(len(w)-1,hi+2)
        elif up>=dn:acc+=up;hi=min(len(w)-1,hi+2)
        else:acc+=dn;lo=max(0,lo-2)
    return(prices[poc],prices[hi],prices[lo])

def tpo_counts(bars,grid=TICK):
    c={}
    for lo,hi in bars:
        a=round(lo/grid);b=round(hi/grid)
        for r in range(a,b+1):p=round(r*grid,4);c[p]=c.get(p,0)+1
    return c

def sess_of(m):
    if 5*60<=m<12*60+30:return"A"
    if 12*60+30<=m<19*60:return"AU"
    return"MY"

def pdt_dx(s):
    # '2025-11-02 23:22:00.000'
    return datetime.strptime(s.strip()[:19],"%Y-%m-%d %H:%M:%S")

def load_m1():
    h,rows=load(DXFILE,sep=';');ix={n:i for i,n in enumerate(h)}
    iTL,iO,iH,iL,iC,iV=ix['Time left'],ix['Open'],ix['High'],ix['Low'],ix['Close'],ix['Volume']
    B=[dict(dt=pdt_dx(x[iTL]),o=fn(x[iO]),hi=fn(x[iH]),lo=fn(x[iL]),c=fn(x[iC]),v=fn(x[iV]))
       for x in rows]
    B.sort(key=lambda b:b['dt'])
    csum_pv=csum_v=0.0
    for i,b in enumerate(B):
        gap=i>0 and (b['dt']-B[i-1]['dt']).total_seconds()/60>30
        if gap:csum_pv=csum_v=0.0
        tp=(b['hi']+b['lo']+b['c'])/3.0;csum_pv+=tp*b['v'];csum_v+=b['v']
        b['vwap']=csum_pv/csum_v if csum_v>0 else b['c']
        win=[B[j]['v'] for j in range(max(0,i-VSA_MA+1),i+1)]
        sma=sum(win)/len(win) if win else b['v']
        b['vma']=sma; b['vratio']=b['v']/sma if sma>1e-9 else 0.0
        rng=b['hi']-b['lo'];b['rng']=rng;b['body']=abs(b['c']-b['o'])
        b['uw']=b['hi']-max(b['o'],b['c']);b['lw']=min(b['o'],b['c'])-b['lo']
        b['brat']=b['body']/rng if rng>0 else 0.0
        b['cpos']=(b['c']-b['lo'])/rng if rng>0 else 0.5
        b['up']=b['c']>b['o']; b['dn']=b['c']<b['o']
        b['since_gap']=0 if gap else (B[i-1]['since_gap']+1 if i>0 else 999)
        b['ym']=b['dt'].strftime('%Y-%m')
    # trend proxy + liquidity long-baseline (O(1) rolling)
    for i,b in enumerate(B):
        j=i-BASE['TREND_LB']
        b['trend']=(1 if b['c']>B[j]['c'] else -1 if b['c']<B[j]['c'] else 0) if j>=0 else 0
    return B

def pdt_fp(s):return datetime.strptime(s.strip(),"%m/%d/%Y %I:%M:%S %p")
def load_fpm1(path="fp-m1-1-month-data.csv"):
    # loader fp-m1 (CO delta) cho cross-check; tra B cung shape + them delta/ddom
    h,rows=load(path);ix={n:i for i,n in enumerate(h)}
    B=[dict(dt=pdt_fp(x[ix['DateTime']]),o=fn(x[ix['Open']]),hi=fn(x[ix['High']]),lo=fn(x[ix['Low']]),
            c=fn(x[ix['Close']]),v=fn(x[ix['Volume']]),delta=fn(x[ix['Delta']])) for x in rows]
    B.sort(key=lambda b:b['dt'])
    csum_pv=csum_v=0.0
    for i,b in enumerate(B):
        gap=i>0 and (b['dt']-B[i-1]['dt']).total_seconds()/60>30
        if gap:csum_pv=csum_v=0.0
        tp=(b['hi']+b['lo']+b['c'])/3.0;csum_pv+=tp*b['v'];csum_v+=b['v']
        b['vwap']=csum_pv/csum_v if csum_v>0 else b['c']
        win=[B[j]['v'] for j in range(max(0,i-VSA_MA+1),i+1)]
        sma=sum(win)/len(win) if win else b['v']
        b['vma']=sma; b['vratio']=b['v']/sma if sma>1e-9 else 0.0
        rng=b['hi']-b['lo'];b['rng']=rng;b['body']=abs(b['c']-b['o'])
        b['uw']=b['hi']-max(b['o'],b['c']);b['lw']=min(b['o'],b['c'])-b['lo']
        b['brat']=b['body']/rng if rng>0 else 0.0
        b['cpos']=(b['c']-b['lo'])/rng if rng>0 else 0.5
        b['up']=b['c']>b['o']; b['dn']=b['c']<b['o']
        b['ddom']=b['delta']/b['v'] if b['v']>0 else 0.0
        b['since_gap']=0 if gap else (B[i-1]['since_gap']+1 if i>0 else 999)
        b['ym']=b['dt'].strftime('%Y-%m'); b['trend']=0
    return B

def daily_levels_from_m1(B):
    # gom NGAY theo gap>45' (khop DayGapMin), profile tu M1
    days=[];cur=None
    for b in B:
        new=(cur is None or (b['dt']-cur['bars'][-1]['dt'])>timedelta(minutes=45))
        if new:cur=dict(bars=[]);days.append(cur)
        cur['bars'].append(b)
    out=[]
    for d in days:
        bb=d['bars']
        if len(bb)<30:continue
        poc,vah,val=value_area(tpo_counts([(x['lo'],x['hi']) for x in bb]))
        if poc is None:continue
        out.append(dict(start=bb[0]['dt'],vah=vah,val=val,poc=poc,
                        hi=max(x['hi'] for x in bb),lo=min(x['lo'] for x in bb)))
    out.sort(key=lambda d:d['start'])
    return out

def build_zones(B):
    zones=[];blocks=[];cur=None
    for b in B:
        lab=sess_of(b['dt'].hour*60+b['dt'].minute)
        new=(cur is None or lab!=cur['lab'] or (b['dt']-cur['bars'][-1]['dt'])>timedelta(minutes=40))
        if new:cur=dict(lab=lab,bars=[]);blocks.append(cur)
        cur['bars'].append(b)
    for blk in blocks:
        bb=blk['bars']
        if len(bb)<10:continue
        end=bb[-1]['dt'];poc,vah,val=value_area(tpo_counts([(x['lo'],x['hi']) for x in bb]))
        if poc is None:continue
        hi=max(x['hi'] for x in bb);lo=min(x['lo'] for x in bb)
        exp=end+timedelta(days=ZONE_EXPIRE_DAYS)
        for nm,val_,strv in [(f"POC {blk['lab']}",poc,70),(f"VAH {blk['lab']}",vah,58),(f"VAL {blk['lab']}",val,58),
                             (f"Dinh {blk['lab']}",hi,52),(f"Day {blk['lab']}",lo,52)]:
            zones.append(dict(price=val_,kind=nm,strength=strv,ready=end,expire=exp))
    days=daily_levels_from_m1(B)
    for i in range(1,len(days)):
        d=days[i];p=days[i-1];rd=d['start'];exp=rd+timedelta(days=1,hours=6)
        for nm,val_,strv in [("D-1 VAH",p['vah'],66),("D-1 VAL",p['val'],66),("D-1 POC",p['poc'],72),
                             ("D-1 High",p['hi'],60),("D-1 Low",p['lo'],60)]:
            zones.append(dict(price=val_,kind=nm,strength=strv,ready=rd,expire=exp))
    return zones

# ---- signal gates. USE_DELTA=True => dung delta that (fp-m1 cross-check); False => delta-free proxy
USE_DELTA=False
DDOM_STRONG=0.25; DELTA_ABS_MIN=15
def long_sig(b):
    ur=b['lw']>=WICK_FRAC*b['rng'] and b['cpos']>=CLOSEPOS_HI
    if USE_DELTA:
        ur=ur and b['delta']>=0
        su=b['brat']>=BODY_STRONG and b['ddom']>=DDOM_STRONG and abs(b['delta'])>=DELTA_ABS_MIN and b['cpos']>=0.6
    else:
        su=b['brat']>=BODY_STRONG and b['cpos']>=0.6 and b['up']
    if b['vratio']>=VSA_GATE and(ur or su):
        w=(["rau duoi"] if ur else [])+(["than manh"] if su else [])+[f"VSA{b['vratio']:.1f}x"+("(tim)" if b['vratio']>=VSA_CLIMAX else "")]
        return True,w
    return False,[]
def short_sig(b):
    dr=b['uw']>=WICK_FRAC*b['rng'] and b['cpos']<=CLOSEPOS_LO
    if USE_DELTA:
        dr=dr and b['delta']<=0
        sd=b['brat']>=BODY_STRONG and b['ddom']<=-DDOM_STRONG and abs(b['delta'])>=DELTA_ABS_MIN and b['cpos']<=0.4
    else:
        sd=b['brat']>=BODY_STRONG and b['cpos']<=0.4 and b['dn']
    if b['vratio']>=VSA_GATE and(dr or sd):
        w=(["rau tren"] if dr else [])+(["than manh"] if sd else [])+[f"VSA{b['vratio']:.1f}x"+("(tim)" if b['vratio']>=VSA_CLIMAX else "")]
        return True,w
    return False,[]

def run(B,pool,C):
    volfloor=C['VOL_FLOOR']
    raw=[]
    vwapz=dict(price=0.0,kind="VWAP",strength=64,ready=B[0]['dt'],expire=B[-1]['dt']+timedelta(days=1),is_vwap=True)
    Z=[dict(z) for z in pool]+[vwapz]
    for z in Z:z.update(state='idle',brk_bar=-999,cool=-999,prev_rel=None)
    def gate(b):return b['v']>=volfloor and b['since_gap']>=WARMUP_AFTER_GAP and b['vma']>=volfloor*0.6
    def liq_ok(b):
        if not C['LIQ_ON']:return True
        return b.get('liqbase',0)>0 and b['vma']>=C['LIQ_MIN']*b['liqbase']
    for i in range(VSA_MA+2,len(B)):
        b=B[i];px=b['c'];vwapz['price']=b['vwap']
        active=[z for z in Z if z['ready']<=b['dt']<=z['expire']]
        if not gate(b):
            for z in active:z['prev_rel']='above' if px>z['price'] else 'below'
            continue
        for z in active:
            zp=z['price'];dist=abs(px-zp)/TICK
            rel='above' if b['c']>zp+BUF_T*TICK else 'below' if b['c']<zp-BUF_T*TICK else 'in'
            if(dist>ARM_DIST_T and z['state']=='idle') or i-z['cool']<C['COOLDOWN']:
                z['prev_rel']=rel;continue
            zlo=zp-BUF_T*TICK;zhi=zp+BUF_T*TICK;tagged=b['lo']<=zhi and b['hi']>=zlo
            up=z['prev_rel']=='below';dn=z['prev_rel']=='above'
            # BREAK: delta>0 (neu co) hoac c>o (delta-free)
            bull=(b['delta']>0) if USE_DELTA else b['up']
            bear=(b['delta']<0) if USE_DELTA else b['dn']
            bu=b['c']>zhi and b['hi']>zp and b['brat']>=0.5 and bull and b['vratio']>=VSA_BREAK and z['prev_rel'] in('below','in')
            bd=b['c']<zlo and b['lo']<zp and b['brat']>=0.5 and bear and b['vratio']>=VSA_BREAK and z['prev_rel'] in('above','in')
            if bu:z['state']='broke_up';z['brk_bar']=i
            elif bd:z['state']='broke_dn';z['brk_bar']=i
            em=False
            hv=C['HOVER_H']
            cancel_up = (b['c']<zp-hv) if hv is not None else (b['c']<zp-BUF_T*TICK)
            cancel_dn = (b['c']>zp+hv) if hv is not None else (b['c']>zp+BUF_T*TICK)
            hold_lo = zp-(hv if hv is not None else C['RETEST_HOLD_T']*TICK)   # low duoc phep cham toi day (LONG)
            hold_hi = zp+(hv if hv is not None else C['RETEST_HOLD_T']*TICK)   # hi duoc phep cham toi day (SHORT)
            if z['state']=='broke_up' and 0<i-z['brk_bar']<=RETEST_BARS:
                if cancel_up:z['state']='idle'
                elif b['lo']<=zp+RETEST_TOL_T*TICK and b['lo']>=hold_lo:
                    ok,w=long_sig(b)
                    if ok and liq_ok(b) and _emit(raw,B,i,z,'LONG','1 pha&hoi len',min(b['lo'],zp),w,pool,C):em=True;z['cool']=i;z['state']='idle'
            elif z['state']=='broke_dn' and 0<i-z['brk_bar']<=RETEST_BARS:
                if cancel_dn:z['state']='idle'
                elif b['hi']>=zp-RETEST_TOL_T*TICK and b['hi']<=hold_hi:
                    ok,w=short_sig(b)
                    if ok and liq_ok(b) and _emit(raw,B,i,z,'SHORT','1 pha&hoi xuong',max(b['hi'],zp),w,pool,C):em=True;z['cool']=i;z['state']='idle'
            # KB2 cham&dao — chi giu nhanh CLIMAX-override (delta-free)
            if not em and C['KB2_CLIMAX'] and z['state'] in('idle','broke_up','broke_dn') and b['vratio']>=VSA_CLIMAX:
                if up and tagged and b['c']<zhi:
                    ok,w=short_sig(b)
                    if ok and liq_ok(b) and _emit(raw,B,i,z,'SHORT','2 cham&dao xuong',max(b['hi'],zp),w+['climax-abs'],pool,C):z['cool']=i;z['state']='idle'
                elif dn and tagged and b['c']>zlo:
                    ok,w=long_sig(b)
                    if ok and liq_ok(b) and _emit(raw,B,i,z,'LONG','2 cham&dao len',min(b['lo'],zp),w+['climax-abs'],pool,C):z['cool']=i;z['state']='idle'
            z['prev_rel']=rel
    return raw

def scan_sweep(B,pool,C):
    # KB2b: QUET qua vung roi RUT manh nguoc lai (false-break / bull-bear trap).
    # short sweep: nen(A) pha/gai LEN qua vung >= SWEEP_SPIKE, nen(B) dong HAN duoi vung <= -SWEEP_REJECT,
    #              than manh, dut khoat. SL tren dinh gai. (long sweep = doi xung)
    volfloor=C['VOL_FLOOR']; SP=C['SWEEP_SPIKE']; RJ=C['SWEEP_REJECT']
    raw=[]
    def gate(b):return b['v']>=volfloor and b['since_gap']>=WARMUP_AFTER_GAP and b['vma']>=volfloor*0.6
    def liq_ok(b):
        if not C['LIQ_ON']:return True
        return b.get('liqbase',0)>0 and b['vma']>=C['LIQ_MIN']*b['liqbase']
    for i in range(VSA_MA+3,len(B)):
        b=B[i];bp=B[i-1]
        if not gate(b) or not liq_ok(b) or b['brat']<0.5 or b['vratio']<VSA_GATE:continue
        spike_hi=max(bp['hi'],b['hi']); spike_lo=min(bp['lo'],b['lo'])
        for z in pool:
            if z['ready']>b['dt'] or b['dt']>z['expire']:continue
            zp=z['price']
            if abs(zp-b['c'])>8.0:continue     # sweep la cuc bo
            strict=C['SWEEP_STRICT']; sb=b['brat']>=(0.6 if strict else 0.5)
            # SHORT: gai len qua vung roi dong han duoi. strict: nen truoc DA DONG tren vung (pha that bai)
            okS=(bp['c']>zp) if strict else True
            if b['dn'] and sb and spike_hi>=zp+SP and b['c']<=zp-RJ and okS:
                _emit(raw,B,i,z,'SHORT','sweep dao xuong',spike_hi,[f"quet {SP:.1f}g roi rut","dut khoat",f"VSA{b['vratio']:.1f}x"],pool,C)
            # LONG: gai xuong qua vung roi dong han tren
            okL=(bp['c']<zp) if strict else True
            if b['up'] and sb and spike_lo<=zp-SP and b['c']>=zp+RJ and okL:
                _emit(raw,B,i,z,'LONG','sweep dao len',spike_lo,[f"quet {SP:.1f}g roi rut","dut khoat",f"VSA{b['vratio']:.1f}x"],pool,C)
    return raw

def next_zone(entry,side,t,pool):
    cands=[z['price'] for z in pool if z['ready']<=t<=z['expire']]
    if side=='LONG':
        up=[p for p in cands if p>entry+5*TICK]
        return min(up) if up else None
    dn=[p for p in cands if p<entry-5*TICK]
    return max(dn) if dn else None

def _emit(raw,B,i,z,side,scen,anchor,why,pool,C):
    b=B[i];entry=b['c']
    fl=C['SL_FLOOR_T']*TICK
    if side=='LONG':sl=min(anchor-SL_BUF_T*TICK,entry-fl);risk=(entry-sl)/TICK
    else:sl=max(anchor+SL_BUF_T*TICK,entry+fl);risk=(sl-entry)/TICK
    if risk<=0 or risk>C['SL_CAP_T']:return False
    r_dollar=risk*TICK; RR=C['RR']
    tp3=entry+RR*r_dollar if side=='LONG' else entry-RR*r_dollar
    tpx=tp3;rx=RR
    if C['EXTEND']:
        nz=next_zone(entry,side,b['dt'],pool)
        if nz is not None:
            cand=nz-2*TICK if side=='LONG' else nz+2*TICK
            rr_cand=abs(cand-entry)/r_dollar
            if rr_cand>=C['NEXTZONE_MINR']:tpx=cand;rx=rr_cand
    raw.append(dict(i=i,dt=b['dt'],ym=b['ym'],side=side,scen=scen,zone=f"{z['kind']} {z['price']:.1f}",zstr=z['strength'],
        entry=entry,sl=sl,tp3=tp3,tpx=tpx,rx=rx,risk_t=risk,climax=b['vratio']>=VSA_CLIMAX,
        vwap_side='tren' if entry>=b['vwap'] else 'duoi',vwap_dist=entry-b['vwap'],trend=b['trend'],vsa=b['vratio'],why=";".join(why)))
    return True

def cluster_count(s,pool):
    # dem so vung (KHONG ke VWAP) trong CONFLUENCE_TOL quanh entry, dedup theo gia
    seen=set();n=0
    for z in pool:
        if z['ready']<=s['dt']<=z['expire'] and abs(z['price']-s['entry'])/TICK<=CONFLUENCE_TOL_T:
            k=round(z['price']/TICK)
            if k not in seen:seen.add(k);n+=1
    return n

def dedup(raw,pool,C):
    raw=sorted(raw,key=lambda s:(s['i'],s['zone']));out=[]
    for s in raw:
        m=None
        for k in out:
            if k['side']==s['side'] and abs(s['i']-k['i'])<=DEDUP_BARS and abs(s['entry']-k['entry'])/TICK<=DEDUP_TICKS:m=k;break
        if m:
            if s['zstr']>m['zstr']:m.update(zone=s['zone'],zstr=s['zstr'])
        else:
            s=dict(s);out.append(s)
    for s in out:s['confl']=cluster_count(s,pool)
    # ap filters cum + trend + vwap
    res=[]
    for s in out:
        if s['confl']<C['MIN_CONFL']:continue
        if C['TREND_ON']:
            if s['side']=='LONG' and s['trend']<0:continue
            if s['side']=='SHORT' and s['trend']>0:continue
        if C['VWAP_ON'] and not (C['VWAP_KB1ONLY'] and not s['scen'].startswith('1')):
            m=C['VWAP_MARGIN']
            if s['side']=='LONG' and not (s['vwap_dist'] > m):continue
            if s['side']=='SHORT' and not (s['vwap_dist'] < -m):continue
        res.append(s)
    return res

def sim(B,s,tpkey,RR_fallback):
    i=s['i'];side=s['side'];sl=s['sl'];tp=s[tpkey]
    rr=s['rx'] if tpkey=='tpx' else RR_fallback
    for j in range(i+1,len(B)):
        hb=B[j]
        hitSL=(hb['lo']<=sl) if side=='LONG' else (hb['hi']>=sl)
        hitTP=(hb['hi']>=tp) if side=='LONG' else (hb['lo']<=tp)
        if hitSL and hitTP:return 'amb',-1.0
        if hitSL:return 'SL',-1.0
        if hitTP:return 'TP',rr
    return 'open',0.0

def evalset(B,S,label,C,by_month=True):
    print(f"\n### {label}  (n={len(S)})")
    if not S:print("   (khong co lenh)");return
    for s in S:
        s['o3'],s['r3p']=sim(B,s,'tp3',C['RR'])
        s['ox'],s['rxp']=sim(B,s,'tpx',C['RR'])
    def stats(SS,tag):
        settled=[s for s in SS if s['o3'] in('TP','SL')]
        if not settled:print(f"   {tag:<10} n={len(SS):3} (chua settle)");return
        tp=sum(s['o3']=='TP' for s in settled)
        r3=sum(s['r3p'] for s in SS);rx=sum(s['rxp'] for s in SS)
        risks=[s['risk_t'] for s in SS]
        print(f"   {tag:<10} n={len(SS):3} WR {tp/len(settled):>4.0%} ({tp}/{len(settled)}) | 3R {r3:+6.0f}R exp {r3/len(settled):+.2f} | TPx {rx:+6.0f}R | SLmed {st.median(risks)/10:.1f}g")
    stats(S,"TONG")
    if by_month:
        for ym in sorted(set(s['ym'] for s in S)):
            stats([s for s in S if s['ym']==ym],ym)
    # theo kich ban (dong: liet ke moi scen xuat hien)
    for sc in sorted(set(s['scen'] for s in S)):
        g=[s for s in S if s['scen']==sc]
        if g:
            gs=[s for s in g if s['o3'] in('TP','SL')]
            wr=f"WR{sum(s['o3']=='TP' for s in g)/len(gs):.0%}" if gs else "-"
            print(f"     {sc:<18} n={len(g):3} 3R {sum(s['r3p'] for s in g):+5.0f}R {wr}")

# AUDIT_V7 §1.2: calc_volfloor() la LOOK-AHEAD — percentile-30 tinh tren TOAN BO du lieu
# >=2026-05 roi dung o MOI nen (ke ca nen dau chuoi). Phep cat chuoi cho 5.0/5.0/6.0/12.0/16.0
# thay vi 17.0 o 5/5 diem cat. Ban va da duoc audit chung minh KHONG doi mot con so nao:
# chot cung 20.0 cho khop RunnerSignal.cs => KB1 van n=33 WR=48.5% +47.0R EV=+1.424.
# DUNG calc_volfloor() cho code moi. Hang so duoi day la duong nhan-qua duy nhat.
VOLFLOOR_FROZEN=20.0

def calc_volfloor(B):
    # ⚠ LOOK-AHEAD — GIU LAI CHI DE TAI LAP script research cu (research/*.py truoc 2026-07-29).
    # Code moi phai dung VOLFLOOR_FROZEN. Xem AUDIT_V7.md §1.2.
    # lien-thong: percentile-30 cua volume tren cac nen 'day du' (liquid) => portable floor
    liq=[b['v'] for b in B if b['ym']>='2026-05']
    liq.sort()
    p30=liq[int(len(liq)*0.30)] if liq else 20
    return max(5.0,p30)

def add_liqbase(B,lb):
    # rolling mean vma window lb (O(n))
    from collections import deque
    dq=deque();s=0.0
    for b in B:
        dq.append(b['vma']);s+=b['vma']
        if len(dq)>lb:s-=dq.popleft()
        b['liqbase']=s/len(dq)

def make(**kw):
    c=dict(BASE);c.update(kw);return c

def prep(C):
    if C['VOL_FLOOR'] is None:C['VOL_FLOOR']=VOLFLOOR_AUTO
    if C['LIQ_ON']:add_liqbase(B,C['LIQ_LB'])
    return C

def pipeline(C,label,months=('2026-05','2026-06','2026-07')):
    C=prep(dict(C))
    raw=run(B,pool,C)
    if C['SWEEP_ON']:raw=raw+scan_sweep(B,pool,C)
    sig=dedup(raw,pool,C)
    if months:sig=[s for s in sig if s['ym'] in months]
    evalset(B,sig,label,C)
    return sig

if __name__=='__main__':
    print("="*100)
    print("ENTRY-SIGNAL (scalp) tren dxFeed 9 thang — DELTA-FREE adaptation")
    B=load_m1();pool=build_zones(B)
    VOLFLOOR_AUTO=calc_volfloor(B)
    print(f"  M1={len(B)} nen | {B[0]['dt']} -> {B[-1]['dt']} | zones={len(pool)} | volfloor auto={VOLFLOOR_AUTO:.0f}")
    # phan bo volume theo thang (xac dinh cua so thanh khoan)
    from collections import Counter
    volmed={}
    for ym in sorted(set(b['ym'] for b in B)):
        vs=sorted(b['v'] for b in B if b['ym']==ym)
        volmed[ym]=vs[len(vs)//2]
    print("  vol median/thang:", " ".join(f"{k[5:]}={v:.0f}" for k,v in volmed.items()))

    print("\n"+"#"*100+"\n# BASELINE = config SHIPPED (cluster>=2, SL floor4-cap6, RR1.5, KB2-climax, extend TP2)\n"+"#"*100)
    pipeline(make(), "BASELINE shipped (5-7/2026)")

    print("\n"+"#"*100+"\n# GRID CAI TIEN — goc nhin moi (trend / VWAP / liquidity) + tia bucket thua\n"+"#"*100)
    pipeline(make(TREND_ON=True),                          "F1  +trend (close vs 480 nen)")
    pipeline(make(VWAP_ON=True),                           "F2  +vwap-align")
    pipeline(make(LIQ_ON=True),                            "F3  +liquidity (vma>=0.75x TB1000)")
    pipeline(make(TREND_ON=True,VWAP_ON=True),             "F4  +trend +vwap")
    pipeline(make(TREND_ON=True,LIQ_ON=True),              "F5  +trend +liq")
    pipeline(make(TREND_ON=True,VWAP_ON=True,LIQ_ON=True), "F6  +trend +vwap +liq")
    pipeline(make(KB2_CLIMAX=False),                       "F7  TAT KB2 (chi KB1 pha&hoi)")
    pipeline(make(KB2_CLIMAX=False,TREND_ON=True),         "F8  KB1-only +trend")
    pipeline(make(KB2_CLIMAX=False,TREND_ON=True,VWAP_ON=True,LIQ_ON=True),"F9  KB1-only +trend+vwap+liq")
    pipeline(make(MIN_CONFL=3),                            "F10 cluster>=3")
    pipeline(make(TREND_ON=True,VWAP_ON=True,LIQ_ON=True,MIN_CONFL=3),"F11 cluster>=3 +tat ca filter")
