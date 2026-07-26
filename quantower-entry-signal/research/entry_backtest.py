#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROTOTYPE + BACKTEST v2 — Entry Suggestion (footprint M1).
Muc dich: kiem tra LOGIC may tin hieu tren DU LIEU THAT (1.7 ngay) — KHONG phai chung minh edge.
v2 them: (1) gop confluence, (2) san SL + dat theo cau truc, (3) san volume + warm-up,
         (4) loc bias (EMA), (5) bao cao ca can bi quan (SL-truoc) lan lac quan (TP-truoc).
Trung thuc: offline THIEU footprint theo muc gia -> absorption/big-trade = PROXY per-bar (live moi that).
"""
import csv, statistics as st
from datetime import datetime, timedelta

DIR="/home/asl86/Documents/footprint-tpo/data-export/"; TICK=0.1
# --- tham so ---
ARM_DIST_T=20; BUF_T=2; RETEST_BARS=12; RETEST_TOL_T=4
VSA_HIGH=1.8; VSA_ABOVE=1.2; BODY_STRONG=0.55; DDOM_STRONG=0.25; DELTA_ABS_MIN=15
WICK_FRAC=0.50; CLOSEPOS_HI=0.55; CLOSEPOS_LO=0.45
SL_BUF_T=2; SL_MIN_T=20; SL_MAX_T=60; SL_IDEAL_T=40; RR=3.0
COOLDOWN_BARS=15; VSA_MA=20
VOL_FLOOR_ABS=20          # san volume tuyet doi (chong nen dem mong)
WARMUP_AFTER_GAP=20       # bo tin hieu 20 nen sau gap>30' (MA chua on)
DEDUP_BARS=6; DEDUP_TICKS=6  # gop tin hieu cung phia gan nhau

def load(path):
    with open(DIR+path,encoding='utf-8-sig') as f:
        r=csv.reader(f); h=next(r); rows=[x for x in r if x and x[0].strip()]
    return h,rows
def fnum(x):
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

def load_m1():
    h,rows=load("fp-m1.csv");ix={n:i for i,n in enumerate(h)}
    B=[]
    for x in rows:
        B.append(dict(dt=pdt(x[ix['DateTime']]),o=fnum(x[ix['Open']]),hi=fnum(x[ix['High']]),
            lo=fnum(x[ix['Low']]),c=fnum(x[ix['Close']]),v=fnum(x[ix['Volume']]),
            buy=fnum(x[ix['Buy (Ask) volume']]),sell=fnum(x[ix['Sell (Bid) volume']]),
            delta=fnum(x[ix['Delta']]),cum=fnum(x[ix['Cumulative delta']]),
            vsa=fnum(x[ix['VSA Volume_scale (ẩn)']])))
    ef=es=None; kf=2/(30+1); ks=2/(120+1)
    csum_pv=csum_v=0.0
    for i,b in enumerate(B):
        gap = i>0 and (b['dt']-B[i-1]['dt']).total_seconds()/60>30
        if gap: csum_pv=csum_v=0.0
        b['gap']=gap
        tp=(b['hi']+b['lo']+b['c'])/3.0; csum_pv+=tp*b['v']; csum_v+=b['v']
        b['vwap']=csum_pv/csum_v if csum_v>0 else b['c']
        prev=[B[j]['v'] for j in range(max(0,i-VSA_MA),i)]
        ma=sum(prev)/len(prev) if prev else b['v']
        b['vma']=ma; b['vratio']=b['v']/ma if ma>0 else 1.0
        ef=b['c'] if ef is None else ef+kf*(b['c']-ef)
        es=b['c'] if es is None else es+ks*(b['c']-es)
        b['ema_f']=ef; b['ema_s']=es
        b['bias']=1 if ef>es+3*TICK else -1 if ef<es-3*TICK else 0
        rng=b['hi']-b['lo']; b['rng']=rng; b['body']=abs(b['c']-b['o'])
        b['uw']=b['hi']-max(b['o'],b['c']); b['lw']=min(b['o'],b['c'])-b['lo']
        b['brat']=b['body']/rng if rng>0 else 0.0
        b['cpos']=(b['c']-b['lo'])/rng if rng>0 else 0.5
        b['ddom']=b['delta']/b['v'] if b['v']>0 else 0.0
        # so nen ke tu gap gan nhat (warm-up)
        b['since_gap']= 0 if gap else (B[i-1]['since_gap']+1 if i>0 else 999)
    return B

def daily_levels():
    h,rows=load("TPO-chart-daily.csv");ti=h.index('TPO')
    iDT,iH,iL=h.index('DateTime'),h.index('High'),h.index('Low');iVAH,iVAL,iPOC=ti+1,ti+2,ti+3
    profs=[];cur=None
    for x in rows:
        key=(x[iVAH],x[iVAL],x[iPOC])
        if key!=cur:profs.append([]);cur=key
        profs[-1].append(x)
    days=[dict(start=pdt(pr[0][iDT]),vah=fnum(pr[0][iVAH]),val=fnum(pr[0][iVAL]),poc=fnum(pr[0][iPOC]),
               hi=max(fnum(x[iH]) for x in pr),lo=min(fnum(x[iL]) for x in pr)) for pr in profs]
    days.sort(key=lambda d:d['start']);return days
def session_of(m):
    if 5*60<=m<12*60+30:return"A"
    if 12*60+30<=m<19*60:return"AU"
    return"MY"
def zone_pool():
    zones=[]
    h,rows=load("tpo-chart-m30.csv")
    iO,iH,iL,iC,iV,iDT=(h.index('Open'),h.index('High'),h.index('Low'),h.index('Close'),h.index('Volume'),h.index('DateTime'))
    bars=[dict(dt=pdt(x[iDT]),hi=fnum(x[iH]),lo=fnum(x[iL])) for x in rows]
    blocks=[];cur=None
    for b in bars:
        lab=session_of(b['dt'].hour*60+b['dt'].minute)
        new=(cur is None or lab!=cur['lab'] or (b['dt']-cur['bars'][-1]['dt'])>timedelta(minutes=40))
        if new:cur=dict(lab=lab,bars=[]);blocks.append(cur)
        cur['bars'].append(b)
    for blk in blocks:
        bb=blk['bars']
        if len(bb)<5:continue
        end=bb[-1]['dt'];poc,vah,val=value_area(tpo_counts([(x['lo'],x['hi']) for x in bb]))
        if poc is None:continue
        for nm,val_,strv in [(f"POC {blk['lab']}",poc,70),(f"VAH {blk['lab']}",vah,58),(f"VAL {blk['lab']}",val,58)]:
            zones.append(dict(price=val_,kind=nm,strength=strv,ready=end))
    days=daily_levels()
    for i in range(1,len(days)):
        d=days[i];p=days[i-1];rd=d['start']
        for nm,val_,strv in [("D-1 VAH",p['vah'],66),("D-1 VAL",p['val'],66),("D-1 POC",p['poc'],72),
                             ("D-1 High",p['hi'],60),("D-1 Low",p['lo'],60)]:
            zones.append(dict(price=val_,kind=nm,strength=strv,ready=rd))
    return zones

def long_sig(b):
    ur=b['lw']>=WICK_FRAC*b['rng'] and b['cpos']>=CLOSEPOS_HI and b['delta']>=0
    su=b['brat']>=BODY_STRONG and b['ddom']>=DDOM_STRONG and abs(b['delta'])>=DELTA_ABS_MIN and b['cpos']>=0.6
    if b['vratio']>=VSA_HIGH and(ur or su):
        w=(["rut rau duoi"] if ur else [])+(["than manh"] if su else [])+[f"D{b['delta']:+.0f}",f"VSA{b['vratio']:.1f}x"]
        return True,w
    return False,[]
def short_sig(b):
    dr=b['uw']>=WICK_FRAC*b['rng'] and b['cpos']<=CLOSEPOS_LO and b['delta']<=0
    sd=b['brat']>=BODY_STRONG and b['ddom']<=-DDOM_STRONG and abs(b['delta'])>=DELTA_ABS_MIN and b['cpos']<=0.4
    if b['vratio']>=VSA_HIGH and(dr or sd):
        w=(["rut rau tren"] if dr else [])+(["than manh"] if sd else [])+[f"D{b['delta']:+.0f}",f"VSA{b['vratio']:.1f}x"]
        return True,w
    return False,[]
def gate(b):  # san volume + warm-up
    return b['v']>=VOL_FLOOR_ABS and b['since_gap']>=WARMUP_AFTER_GAP and b['vma']>=VOL_FLOOR_ABS*0.6

def run(B,pool):
    raw=[]
    Z=[dict(z) for z in pool]
    for z in Z: z.update(state='idle',brk_bar=-999,cool=-999,prev_rel=None)
    for i in range(VSA_MA+2,len(B)):
        b=B[i];px=b['c']
        if not gate(b):
            for z in Z:
                if b['dt']>=z['ready']: z['prev_rel']='above' if px>z['price'] else 'below'
            continue
        for z in Z:
            if b['dt']<z['ready']:continue
            zp=z['price'];dist=abs(px-zp)/TICK
            rel='above' if b['c']>zp+BUF_T*TICK else 'below' if b['c']<zp-BUF_T*TICK else 'in'
            if(dist>ARM_DIST_T and z['state']=='idle') or i-z['cool']<COOLDOWN_BARS:
                z['prev_rel']=rel;continue
            zlo=zp-BUF_T*TICK;zhi=zp+BUF_T*TICK
            tagged=b['lo']<=zhi and b['hi']>=zlo
            up=z['prev_rel']=='below';dn=z['prev_rel']=='above'
            bu=b['c']>zhi and b['hi']>zp and b['brat']>=0.5 and b['delta']>0 and b['vratio']>=VSA_ABOVE and z['prev_rel'] in('below','in')
            bd=b['c']<zlo and b['lo']<zp and b['brat']>=0.5 and b['delta']<0 and b['vratio']>=VSA_ABOVE and z['prev_rel'] in('above','in')
            if bu:z['state']='broke_up';z['brk_bar']=i
            elif bd:z['state']='broke_dn';z['brk_bar']=i
            em=False
            if z['state']=='broke_up' and 0<i-z['brk_bar']<=RETEST_BARS:
                if b['c']<zp-BUF_T*TICK:z['state']='idle'
                elif b['lo']<=zp+RETEST_TOL_T*TICK:
                    ok,w=long_sig(b)
                    if ok and _emit(raw,B,i,z,'LONG','1 pha&hoi len',min(b['lo'],zp),w):em=True;z['cool']=i;z['state']='idle'
            elif z['state']=='broke_dn' and 0<i-z['brk_bar']<=RETEST_BARS:
                if b['c']>zp+BUF_T*TICK:z['state']='idle'
                elif b['hi']>=zp-RETEST_TOL_T*TICK:
                    ok,w=short_sig(b)
                    if ok and _emit(raw,B,i,z,'SHORT','1 pha&hoi xuong',max(b['hi'],zp),w):em=True;z['cool']=i;z['state']='idle'
            if not em and z['state'] in('idle','broke_up','broke_dn'):
                if up and tagged and b['c']<zhi:
                    ok,w=short_sig(b)
                    if ok and b['delta']<0 and _emit(raw,B,i,z,'SHORT','2 cham&dao xuong',max(b['hi'],zp),w+['hapthu:D<0']):z['cool']=i;z['state']='idle'
                elif dn and tagged and b['c']>zlo:
                    ok,w=long_sig(b)
                    if ok and b['delta']>0 and _emit(raw,B,i,z,'LONG','2 cham&dao len',min(b['lo'],zp),w+['hapthu:D>0']):z['cool']=i;z['state']='idle'
            z['prev_rel']=rel
    return raw

def _emit(raw,B,i,z,side,scen,anchor,why):
    b=B[i];entry=b['c']
    if side=='LONG':
        sl=min(anchor-SL_BUF_T*TICK, entry-SL_MIN_T*TICK); risk=(entry-sl)/TICK
    else:
        sl=max(anchor+SL_BUF_T*TICK, entry+SL_MIN_T*TICK); risk=(sl-entry)/TICK
    if risk<=0 or risk>SL_MAX_T:return False
    tp=entry+RR*(entry-sl) if side=='LONG' else entry-RR*(sl-entry)
    raw.append(dict(i=i,dt=b['dt'],side=side,scen=scen,zone=f"{z['kind']} {z['price']:.1f}",zstr=z['strength'],
        entry=entry,sl=sl,tp=tp,risk_t=risk,bias=b['bias'],vwap='tren' if entry>=b['vwap'] else 'duoi',
        vsa=b['vratio'],delta=b['delta'],why=";".join(why)))
    return True

def dedup(raw):
    raw=sorted(raw,key=lambda s:(s['i'],s['zone']));out=[]
    for s in raw:
        m=None
        for k in out:
            if k['side']==s['side'] and abs(s['i']-k['i'])<=DEDUP_BARS and abs(s['entry']-k['entry'])/TICK<=DEDUP_TICKS:
                m=k;break
        if m:
            m['confl']+=1; m['zones'].append(s['zone'])
            if s['zstr']>m['zstr']:  # giu vung manh nhat lam moc
                m.update(zone=s['zone'],zstr=s['zstr'])
        else:
            s=dict(s);s['confl']=1;s['zones']=[s['zone']];out.append(s)
    return out

def simulate(B,s):
    i=s['i'];side=s['side'];sl=s['sl'];tp=s['tp']
    op=pe='open'
    for j in range(i+1,len(B)):
        hb=B[j];hitSL=(hb['lo']<=sl) if side=='LONG' else (hb['hi']>=sl)
        hitTP=(hb['hi']>=tp) if side=='LONG' else (hb['lo']<=tp)
        if hitSL and hitTP:  # cung nen: bi quan=SL, lac quan=TP, danh dau ambiguous
            s['ambig']=True
            return ('SL',-1.0),('TP',RR)
        if hitSL:return('SL',-1.0),('SL',-1.0)
        if hitTP:return('TP',RR),('TP',RR)
    return('open',0.0),('open',0.0)

def evalset(B,sigs,label,bias_filter):
    S=[s for s in sigs if (not bias_filter) or (s['side']=='LONG' and s['bias']>=0) or (s['side']=='SHORT' and s['bias']<=0)]
    for s in S:
        s['ambig']=False;(s['out_p'],s['rr_p']),(s['out_o'],s['rr_o'])=[(a,b) for a,b in [simulate(B,s)]][0]
    resP=[s for s in S if s['out_p'] in('TP','SL')]
    tpP=sum(s['out_p']=='TP' for s in S);slP=sum(s['out_p']=='SL' for s in S);opn=sum(s['out_p']=='open' for s in S)
    rP=sum(s['rr_p'] for s in S);rO=sum(s['rr_o'] for s in S);amb=sum(s.get('ambig') for s in S)
    tpO=sum(s['out_o']=='TP' for s in S);resO=[s for s in S if s['out_o'] in('TP','SL')]
    print(f"\n### {label}  (n={len(S)}, confluence-merged)")
    if not S:print("   (khong co)");return S
    risks=[s['risk_t'] for s in S]
    print(f"   SL: med={st.median(risks)/10:.1f}d  <=4d:{sum(r<=SL_IDEAL_T for r in risks)}/{len(S)}  <=6d:{sum(r<=SL_MAX_T for r in risks)}/{len(S)}  | ambiguous(same-bar SL&TP):{amb}")
    print(f"   BI QUAN(SL-truoc): TP {tpP} SL {slP} open {opn} | WR {tpP/len(resP):.0%} | {rP:+.1f}R | exp {rP/len(resP):+.2f}R" if resP else "   (chua co ket qua)")
    if resO:print(f"   LAC QUAN(TP-truoc): TP {tpO} | WR {tpO/len(resO):.0%} | {rO:+.1f}R | exp {rO/len(resO):+.2f}R")
    for sc in ['1 pha&hoi len','1 pha&hoi xuong','2 cham&dao xuong','2 cham&dao len']:
        g=[s for s in S if s['scen']==sc]
        if g:
            gt=sum(s['out_p']=='TP' for s in g);gres=[s for s in g if s['out_p'] in('TP','SL')]
            print(f"     {sc:<18}: {len(g):2} | biquan {sum(s['rr_p'] for s in g):+.0f}R"+(f" WR{gt/len(gres):.0%}" if gres else "")+f" | lacquan {sum(s['rr_o'] for s in g):+.0f}R")
    return S

def detail(S):
    print("   --- chi tiet (bi quan|lac quan) ---")
    print(f"   {'time':<12}{'side':<6}{'scen':<16}{'zone':<16}{'cf':>3}{'bias':>5}{'entry':>8}{'SL':>7}{'TP':>7}{'risk':>6}{'P':>4}{'O':>4}  why")
    for s in sorted(S,key=lambda x:x['i']):
        print(f"   {s['dt'].strftime('%m/%d %H:%M'):<12}{s['side']:<6}{s['scen']:<16}{s['zone']:<16}{s['confl']:>3}"
              f"{('+' if s['bias']>0 else '-' if s['bias']<0 else '0'):>5}{s['entry']:>8.1f}{s['sl']:>7.1f}{s['tp']:>7.1f}{s['risk_t']/10:>5.1f}d"
              f"{s['out_p'][:2]:>4}{s['out_o'][:2]:>4}  {s['vwap']}VWAP;{s['why']}")

if __name__=='__main__':
    print("="*104);print("BACKTEST v2 — fp-m1 (7/23 09:58 -> 7/25 03:59, ~1.7 ngay). CHI kiem LOGIC, KHONG phai edge.")
    B=load_m1();pool=zone_pool();raw=run(B,pool);sig=dedup(raw)
    print(f"  M1={len(B)} | zones={len(pool)} | raw signals={len(raw)} | sau gop confluence={len(sig)}")
    S0=evalset(B,sig,"KHONG loc bias",False)
    S1=evalset(B,sig,"CO loc bias (chi trade cung chieu EMA30/120)",True)
    detail(S1)
    print("="*104);print("DONE")
