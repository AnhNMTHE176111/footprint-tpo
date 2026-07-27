#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST v3 — Entry Suggestion tren 28 NGAY M1 (fp-m1-1-month-data.csv).
Sua theo phan hoi user:
 - VSA ratio = vol / SMA20(GOM ca nen hien tai)  == dung indicator VsaVolume -> khop man hinh.
   tiers: >=2.2 tim(climax) / >=1.8 do / >=1.2 CAM=High / >=0.8 la / >=0.4 xanh / <0.4 xam.
   Cong toi thieu = High(1.2). Climax(2.2)=co xac nhan manh.
 - VWAP = vung DONG (bounce + break-retest) — dung ca 2 vi du cua user.
 - Vung dung tu chinh M1 ca thang (session A/Au/My) + muc D-1 (daily file). Co han (expire).
 - TP: do CA 3R lan "toi vung ke" (mo rong RR nhu vi du Entry2 -> Dinh A ~1:4).
Trung thuc: offline THIEU footprint tung muc -> hap thu = proxy (VSA>=High + delta nguoc). Live moi that.
"""
import csv, statistics as st
from datetime import datetime, timedelta
DIR="/home/asl86/Documents/footprint-tpo/data-export/"; TICK=0.1
ARM_DIST_T=20; BUF_T=2; RETEST_BARS=12; RETEST_TOL_T=4
RETEST_HOLD_T=0   # KB1: retest phai GIU vung (low>=zp-HOLD cho LONG / hi<=zp+HOLD cho SHORT). 0=strict.
                  # Backtest: hoi giu goc pha (retrace<=100%) -> 1.5R +0.44->+1.00R, 3R -0.08->+0.20R.
VSA_GATE=1.2; VSA_CLIMAX=2.2; VSA_BREAK=1.2
BODY_STRONG=0.55; DDOM_STRONG=0.25; DELTA_ABS_MIN=15
WICK_FRAC=0.50; CLOSEPOS_HI=0.55; CLOSEPOS_LO=0.45
SL_BUF_T=2; SL_MIN_T=20; SL_MAX_T=60; SL_IDEAL_T=40; RR=3.0
COOLDOWN_BARS=15; VSA_MA=20; VOL_FLOOR_ABS=20; WARMUP_AFTER_GAP=20
DEDUP_BARS=6; DEDUP_TICKS=6; ZONE_EXPIRE_DAYS=3; NEXTZONE_MINR=3.0

def load(path,sep=','):
    with open(DIR+path,encoding='utf-8-sig') as f:
        r=csv.reader(f,delimiter=sep); h=next(r); rows=[x for x in r if x and x[0].strip()]
    return h,rows
def fn(x):
    try:return float(x)
    except:return 0.0
def pdt(s):return datetime.strptime(s.strip(),"%m/%d/%Y %I:%M:%S %p")
def value_area(rows,frac=0.70):
    if not rows:return(None,None,None)
    prices=sorted(rows);w=[rows[p] for p in prices];tot=sum(w)
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

def load_m1():
    h,rows=load("fp-m1-1-month-data.csv");ix={n:i for i,n in enumerate(h)}
    B=[dict(dt=pdt(x[ix['DateTime']]),o=fn(x[ix['Open']]),hi=fn(x[ix['High']]),lo=fn(x[ix['Low']]),
            c=fn(x[ix['Close']]),v=fn(x[ix['Volume']]),delta=fn(x[ix['Delta']]),cum=fn(x[ix['Cumulative delta']]))
        for x in rows]
    ef=es=None;kf=2/(30+1);ks=2/(120+1);csum_pv=csum_v=0.0
    for i,b in enumerate(B):
        gap=i>0 and (b['dt']-B[i-1]['dt']).total_seconds()/60>30
        if gap:csum_pv=csum_v=0.0
        tp=(b['hi']+b['lo']+b['c'])/3.0;csum_pv+=tp*b['v'];csum_v+=b['v']
        b['vwap']=csum_pv/csum_v if csum_v>0 else b['c']
        # VSA ratio khop indicator: SMA20 GOM ca nen hien tai
        win=[B[j]['v'] for j in range(max(0,i-VSA_MA+1),i+1)]
        sma=sum(win)/len(win) if win else b['v']
        b['vma']=sma; b['vratio']=b['v']/sma if sma>1e-9 else 0.0
        ef=b['c'] if ef is None else ef+kf*(b['c']-ef)
        es=b['c'] if es is None else es+ks*(b['c']-es)
        b['bias']=1 if ef>es+3*TICK else -1 if ef<es-3*TICK else 0
        rng=b['hi']-b['lo'];b['rng']=rng;b['body']=abs(b['c']-b['o'])
        b['uw']=b['hi']-max(b['o'],b['c']);b['lw']=min(b['o'],b['c'])-b['lo']
        b['brat']=b['body']/rng if rng>0 else 0.0
        b['cpos']=(b['c']-b['lo'])/rng if rng>0 else 0.5
        b['ddom']=b['delta']/b['v'] if b['v']>0 else 0.0
        b['since_gap']=0 if gap else (B[i-1]['since_gap']+1 if i>0 else 999)
    return B

def daily_levels():
    h,rows=load("TPO-chart-daily.csv");ti=h.index('TPO')
    iDT,iH,iL=h.index('DateTime'),h.index('High'),h.index('Low');iVAH,iVAL,iPOC=ti+1,ti+2,ti+3
    profs=[];cur=None
    for x in rows:
        key=(x[iVAH],x[iVAL],x[iPOC])
        if key!=cur:profs.append([]);cur=key
        profs[-1].append(x)
    days=[dict(start=pdt(pr[0][iDT]),vah=fn(pr[0][iVAH]),val=fn(pr[0][iVAL]),poc=fn(pr[0][iPOC]),
               hi=max(fn(x[iH]) for x in pr),lo=min(fn(x[iL]) for x in pr)) for pr in profs]
    days.sort(key=lambda d:d['start']);return days

def build_zones(B):
    # session blocks tu chinh M1
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
    days=daily_levels()
    for i in range(1,len(days)):
        d=days[i];p=days[i-1];rd=d['start'];exp=rd+timedelta(days=1,hours=6)
        for nm,val_,strv in [("D-1 VAH",p['vah'],66),("D-1 VAL",p['val'],66),("D-1 POC",p['poc'],72),
                             ("D-1 High",p['hi'],60),("D-1 Low",p['lo'],60)]:
            zones.append(dict(price=val_,kind=nm,strength=strv,ready=rd,expire=exp))
    return zones

def long_sig(b):
    ur=b['lw']>=WICK_FRAC*b['rng'] and b['cpos']>=CLOSEPOS_HI and b['delta']>=0
    su=b['brat']>=BODY_STRONG and b['ddom']>=DDOM_STRONG and abs(b['delta'])>=DELTA_ABS_MIN and b['cpos']>=0.6
    if b['vratio']>=VSA_GATE and(ur or su):
        w=(["rau duoi"] if ur else [])+(["than manh"] if su else [])+[f"D{b['delta']:+.0f}",f"VSA{b['vratio']:.1f}x"+("(tim)" if b['vratio']>=VSA_CLIMAX else "")]
        return True,w
    return False,[]
def short_sig(b):
    dr=b['uw']>=WICK_FRAC*b['rng'] and b['cpos']<=CLOSEPOS_LO and b['delta']<=0
    sd=b['brat']>=BODY_STRONG and b['ddom']<=-DDOM_STRONG and abs(b['delta'])>=DELTA_ABS_MIN and b['cpos']<=0.4
    if b['vratio']>=VSA_GATE and(dr or sd):
        w=(["rau tren"] if dr else [])+(["than manh"] if sd else [])+[f"D{b['delta']:+.0f}",f"VSA{b['vratio']:.1f}x"+("(tim)" if b['vratio']>=VSA_CLIMAX else "")]
        return True,w
    return False,[]
def gate(b):return b['v']>=VOL_FLOOR_ABS and b['since_gap']>=WARMUP_AFTER_GAP and b['vma']>=VOL_FLOOR_ABS*0.6

def run(B,pool):
    raw=[]
    vwapz=dict(price=0.0,kind="VWAP",strength=64,ready=B[0]['dt'],expire=B[-1]['dt']+timedelta(days=1),is_vwap=True)
    Z=[dict(z) for z in pool]+[vwapz]
    for z in Z:z.update(state='idle',brk_bar=-999,cool=-999,prev_rel=None)
    for i in range(VSA_MA+2,len(B)):
        b=B[i];px=b['c'];vwapz['price']=b['vwap']
        active=[z for z in Z if z['ready']<=b['dt']<=z['expire']]
        if not gate(b):
            for z in active:z['prev_rel']='above' if px>z['price'] else 'below'
            continue
        for z in active:
            zp=z['price'];dist=abs(px-zp)/TICK
            rel='above' if b['c']>zp+BUF_T*TICK else 'below' if b['c']<zp-BUF_T*TICK else 'in'
            if(dist>ARM_DIST_T and z['state']=='idle') or i-z['cool']<COOLDOWN_BARS:
                z['prev_rel']=rel;continue
            zlo=zp-BUF_T*TICK;zhi=zp+BUF_T*TICK;tagged=b['lo']<=zhi and b['hi']>=zlo
            up=z['prev_rel']=='below';dn=z['prev_rel']=='above'
            bu=b['c']>zhi and b['hi']>zp and b['brat']>=0.5 and b['delta']>0 and b['vratio']>=VSA_BREAK and z['prev_rel'] in('below','in')
            bd=b['c']<zlo and b['lo']<zp and b['brat']>=0.5 and b['delta']<0 and b['vratio']>=VSA_BREAK and z['prev_rel'] in('above','in')
            if bu:z['state']='broke_up';z['brk_bar']=i
            elif bd:z['state']='broke_dn';z['brk_bar']=i
            em=False
            if z['state']=='broke_up' and 0<i-z['brk_bar']<=RETEST_BARS:
                if b['c']<zp-BUF_T*TICK:z['state']='idle'
                elif b['lo']<=zp+RETEST_TOL_T*TICK and b['lo']>=zp-RETEST_HOLD_T*TICK:  # GIU vung
                    ok,w=long_sig(b)
                    if ok and _emit(raw,B,i,z,'LONG','1 pha&hoi len',min(b['lo'],zp),w,pool):em=True;z['cool']=i;z['state']='idle'
            elif z['state']=='broke_dn' and 0<i-z['brk_bar']<=RETEST_BARS:
                if b['c']>zp+BUF_T*TICK:z['state']='idle'
                elif b['hi']>=zp-RETEST_TOL_T*TICK and b['hi']<=zp+RETEST_HOLD_T*TICK:  # GIU vung
                    ok,w=short_sig(b)
                    if ok and _emit(raw,B,i,z,'SHORT','1 pha&hoi xuong',max(b['hi'],zp),w,pool):em=True;z['cool']=i;z['state']='idle'
            if not em and z['state'] in('idle','broke_up','broke_dn'):
                if up and tagged and b['c']<zhi:
                    ok,w=short_sig(b)
                    if ok and b['delta']<0 and _emit(raw,B,i,z,'SHORT','2 cham&dao xuong',max(b['hi'],zp),w+['hapthu:D<0'],pool):z['cool']=i;z['state']='idle'
                elif dn and tagged and b['c']>zlo:
                    ok,w=long_sig(b)
                    if ok and b['delta']>0 and _emit(raw,B,i,z,'LONG','2 cham&dao len',min(b['lo'],zp),w+['hapthu:D>0'],pool):z['cool']=i;z['state']='idle'
            z['prev_rel']=rel
    return raw

def next_zone(entry,side,t,pool):
    cands=[z['price'] for z in pool if z['ready']<=t<=z['expire']]
    if side=='LONG':
        up=[p for p in cands if p>entry+5*TICK]
        return min(up) if up else None
    else:
        dn=[p for p in cands if p<entry-5*TICK]
        return max(dn) if dn else None

def _emit(raw,B,i,z,side,scen,anchor,why,pool):
    b=B[i];entry=b['c']
    if side=='LONG':sl=min(anchor-SL_BUF_T*TICK,entry-SL_MIN_T*TICK);risk=(entry-sl)/TICK
    else:sl=max(anchor+SL_BUF_T*TICK,entry+SL_MIN_T*TICK);risk=(sl-entry)/TICK
    if risk<=0 or risk>SL_MAX_T:return False
    r_dollar=risk*TICK
    tp3=entry+RR*r_dollar if side=='LONG' else entry-RR*r_dollar
    # TP mo rong toi vung ke (nhu Entry2 -> Dinh A)
    nz=next_zone(entry,side,b['dt'],pool)
    tpx=tp3;rx=RR
    if nz is not None:
        if side=='LONG':cand=nz-2*TICK
        else:cand=nz+2*TICK
        rr_cand=abs(cand-entry)/r_dollar
        if rr_cand>=NEXTZONE_MINR:tpx=cand;rx=rr_cand
    raw.append(dict(i=i,dt=b['dt'],side=side,scen=scen,zone=f"{z['kind']} {z['price']:.1f}",zstr=z['strength'],
        entry=entry,sl=sl,tp3=tp3,tpx=tpx,rx=rx,risk_t=risk,bias=b['bias'],climax=b['vratio']>=VSA_CLIMAX,
        vwap='tren' if entry>=b['vwap'] else 'duoi',vsa=b['vratio'],why=";".join(why)))
    return True

def dedup(raw):
    raw=sorted(raw,key=lambda s:(s['i'],s['zone']));out=[]
    for s in raw:
        m=None
        for k in out:
            if k['side']==s['side'] and abs(s['i']-k['i'])<=DEDUP_BARS and abs(s['entry']-k['entry'])/TICK<=DEDUP_TICKS:m=k;break
        if m:
            m['confl']+=1;m['zones'].append(s['zone'])
            if s['zstr']>m['zstr']:m.update(zone=s['zone'],zstr=s['zstr'])
        else:
            s=dict(s);s['confl']=1;s['zones']=[s['zone']];out.append(s)
    return out

def sim(B,s,tpkey):
    i=s['i'];side=s['side'];sl=s['sl'];tp=s[tpkey]
    for j in range(i+1,len(B)):
        hb=B[j]
        hitSL=(hb['lo']<=sl) if side=='LONG' else (hb['hi']>=sl)
        hitTP=(hb['hi']>=tp) if side=='LONG' else (hb['lo']<=tp)
        if hitSL and hitTP:return 'amb',-1.0,(s['rx'] if tpkey=='tpx' else RR)
        if hitSL:return 'SL',-1.0,-1.0
        if hitTP:return 'TP',(s['rx'] if tpkey=='tpx' else RR),(s['rx'] if tpkey=='tpx' else RR)
    return 'open',0.0,0.0

def evalset(B,S,label):
    print(f"\n### {label}  (n={len(S)})")
    if not S:print("   (khong co)");return
    for s in S:
        s['o3'],s['r3p'],_=sim(B,s,'tp3')
        s['ox'],s['rxp'],_=sim(B,s,'tpx')
    res=[s for s in S if s['o3'] in('TP','SL','amb')]
    tp=sum(s['o3'] in('TP',) for s in S);amb=sum(s['o3']=='amb' for s in S)
    r3=sum(s['r3p'] for s in S);rx=sum(s['rxp'] for s in S)
    risks=[s['risk_t'] for s in S];clx=sum(s['climax'] for s in S)
    print(f"   SL: med={st.median(risks)/10:.1f}d <=4d:{sum(r<=SL_IDEAL_T for r in risks)*100//len(S)}% <=6d:100% | climax(tim):{clx}/{len(S)} | ambiguous:{amb}")
    winr=[s for s in S if s['o3'] in('TP','SL')]
    if winr:print(f"   TP@3R: WR {tp/len(winr):.0%} ({tp}/{len(winr)}) | tong {r3:+.0f}R | exp {r3/len(winr):+.2f}R/lenh")
    print(f"   TP@vung-ke: tong {rx:+.0f}R (RR trung binh {st.mean([s['rx'] for s in S]):.1f})")
    for sc in ['1 pha&hoi len','1 pha&hoi xuong','2 cham&dao xuong','2 cham&dao len']:
        g=[s for s in S if s['scen']==sc];gr=[s for s in g if s['o3'] in('TP','SL')]
        if g:print(f"     {sc:<18}: {len(g):3} | 3R {sum(s['r3p'] for s in g):+4.0f}R"+(f" WR{sum(s['o3']=='TP' for s in g)/len(gr):.0%}" if gr else "")+f" | climax {sum(s['climax'] for s in g)}")

def climax_only(S):return [s for s in S if s['climax']]

if __name__=='__main__':
    print("="*100);print("BACKTEST v3 — 28 ngay M1 (6/26 -> 7/25). VSA khop indicator (SMA20 incl current).")
    B=load_m1();pool=build_zones(B)
    raw=run(B,pool);sig=dedup(raw)
    print(f"  M1={len(B)} | zones={len(pool)} | raw={len(raw)} | sau gop confluence={len(sig)}")
    evalset(B,sig,"A) Cong VSA>=High(1.2) — KHONG loc bias")
    Sb=[s for s in sig if (s['side']=='LONG' and s['bias']>=0) or (s['side']=='SHORT' and s['bias']<=0)]
    evalset(B,Sb,"B) VSA>=1.2 + loc bias EMA30/120")
    evalset(B,climax_only(sig),"C) CHI nen climax tim (VSA>=2.2) — nhu 2 vi du that cua user")
    Sbc=climax_only(Sb)
    evalset(B,Sbc,"D) climax tim + loc bias")
    # soi 7/24 (khung 2 vi du user)
    print("\n### SOI vung 2 vi du 7/24 (12:00-22:00) — co bat duoc khong?")
    for s in sorted(sig,key=lambda x:x['i']):
        if s['dt'].strftime('%m/%d')=='07/24' and 12<=s['dt'].hour<=22 and s['side']=='LONG':
            print(f"   {s['dt'].strftime('%H:%M')} {s['side']} {s['scen']:<16} {s['zone']:<16} cf{s['confl']} entry{s['entry']:.1f} SL{s['sl']:.1f} TP3{s['tp3']:.1f} TPx{s['tpx']:.1f}(RR{s['rx']:.1f}) {'CLIMAX' if s['climax'] else ''} out3={s['o3']} outx={s['ox']} | {s['why']}")
    print("="*100);print("DONE")
