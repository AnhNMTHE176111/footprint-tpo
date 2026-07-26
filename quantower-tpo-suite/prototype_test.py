#!/usr/bin/env python3
# Prototype + test cho 2 indicator TPO (bias ngay + phien/vung) tren DU LIEU THAT.
# Muc tieu: chung minh thuat toan chay ra so hop ly TRUOC khi viet plan.
import csv, statistics as st
from datetime import datetime, timedelta

DIR = "/home/asl86/Documents/footprint-tpo/data-export/"
TICK = 0.1

def load(path):
    with open(DIR+path, encoding='utf-8-sig') as f:
        r = csv.reader(f); header = next(r)
        rows = [x for x in r if x and x[0].strip()]
    return header, rows

def pdt(s): return datetime.strptime(s.strip(), "%m/%d/%Y %I:%M:%S %p")

def fnum(x):
    try: return float(x)
    except: return 0.0

# ---------- gia tri area tu dict price->weight (rule 2 hang, 70%) ----------
def value_area(rows, frac=0.70):
    if not rows: return (None,None,None)
    prices = sorted(rows); w = [rows[p] for p in prices]
    tot = sum(w)
    if tot<=0: return (None,None,None)
    poc = max(range(len(w)), key=lambda i: w[i])
    acc = w[poc]; lo=hi=poc; target=tot*frac
    while acc < target and (lo>0 or hi<len(w)-1):
        up   = (w[hi+1] if hi<len(w)-1 else 0)+(w[hi+2] if hi<len(w)-2 else 0)
        down = (w[lo-1] if lo>0 else 0)+(w[lo-2] if lo>1 else 0)
        if hi>=len(w)-1: acc+=down; lo=max(0,lo-2)
        elif lo<=0:      acc+=up;   hi=min(len(w)-1,hi+2)
        elif up>=down:   acc+=up;   hi=min(len(w)-1,hi+2)
        else:            acc+=down; lo=max(0,lo-2)
    return (prices[poc], prices[hi], prices[lo])   # POC, VAH, VAL

def tpo_counts(bars, grid=TICK):
    # bars = list of (low,high). Moi bar +1 cho moi hang gia no phu.
    c={}
    for lo,hi in bars:
        a=round(lo/grid); b=round(hi/grid)
        for r in range(a,b+1):
            p=round(r*grid,4); c[p]=c.get(p,0)+1
    return c

# ================================================================
# PART 1 — DUNG LAI PROFILE M30 vs DAP AN NEN TANG
# ================================================================
def part1():
    print("="*72); print("PART 1 — Dung lai POC/VA (TPO) tu 1-phut vs cot nen tang (m30)")
    h, rows = load("tpo-chart-m30.csv")
    ti = h.index('TPO')
    iO,iH,iL = h.index('Open'),h.index('High'),h.index('Low')
    iVAH,iVAL,iPOC = ti+1,ti+2,ti+3
    # gom theo profile (khoi profile-block giong nhau)
    profs=[]; cur=None
    for x in rows:
        key=(x[iVAH],x[iVAL],x[iPOC],x[ti+17],x[ti+18])
        if key!=cur: profs.append([]); cur=key
        profs[-1].append(x)
    poc_hit=[0,0,0]; vah_hit=[0,0]; val_hit=[0,0]; n=0
    for pr in profs:
        if len(pr)<25: continue
        bars=[(fnum(x[iL]),fnum(x[iH])) for x in pr]
        c=tpo_counts(bars)
        poc,vah,val = value_area(c)
        ppoc,pvah,pval = fnum(pr[0][iPOC]),fnum(pr[0][iVAH]),fnum(pr[0][iVAL])
        n+=1
        dp=abs(poc-ppoc)/TICK; dh=abs(vah-pvah)/TICK; dl=abs(val-pval)/TICK
        poc_hit[0]+=dp==0; poc_hit[1]+=dp<=3; poc_hit[2]+=dp<=5
        vah_hit[0]+=dh<=3; vah_hit[1]+=dh<=5
        val_hit[0]+=dl<=3; val_hit[1]+=dl<=5
    print(f"  n profile day du = {n}")
    print(f"  POC: exact {poc_hit[0]/n:.0%} | <=3t {poc_hit[1]/n:.0%} | <=5t {poc_hit[2]/n:.0%}")
    print(f"  VAH: <=3t {vah_hit[0]/n:.0%} | <=5t {vah_hit[1]/n:.0%}")
    print(f"  VAL: <=3t {val_hit[0]/n:.0%} | <=5t {val_hit[1]/n:.0%}")

# ================================================================
# PART 2 — ENGINE BIAS NGAY tren 21 profile day (gia tri chot)
# ================================================================
def daily_profiles():
    h, rows = load("TPO-chart-daily.csv")
    ti=h.index('TPO')
    idx={k:h.index(k) for k in ['DateTime','High','Low','Close','Open']}
    col=lambda name: ti+['TPO','VAH','VAL','POC','Midpoint','RF','Volume','Delta','Trades',
        'TPO Up','TPO Down','POC Count','VA Volume','Range','Range (ticks)','VA range',
        'VA range (ticks)','IB High','IB Low','IB range','IB range (ticks)','IB Volume','Open Interest'].index(name)
    profs=[]; cur=None
    for x in rows:
        key=x[ti+1:ti+7]
        if key!=cur: profs.append([]); cur=key
        profs[-1].append(x)
    out=[]
    for pr in profs:
        f=pr[0]; last=pr[-1]
        hi=max(fnum(x[idx['High']]) for x in pr); lo=min(fnum(x[idx['Low']]) for x in pr)
        out.append(dict(
            date=pdt(f[idx['DateTime']]), nbars=len(pr),
            open=fnum(pr[0][idx['Open']]), close=fnum(last[idx['Close']]),
            high=hi, low=lo,
            VAH=fnum(f[col('VAH')]), VAL=fnum(f[col('VAL')]), POC=fnum(f[col('POC')]),
            IBH=fnum(f[col('IB High')]), IBL=fnum(f[col('IB Low')]),
            rng=fnum(f[col('Range (ticks)')]), va=fnum(f[col('VA range (ticks)')]),
            ibr=fnum(f[col('IB range (ticks)')]), delta=fnum(f[col('Delta')]),
            vol=fnum(f[col('Volume')]),
        ))
    return out

def value_rel(d, p, RangeTypical):
    gap = 0.03*RangeTypical*TICK  # ~27t in $
    if d['VAL'] > p['VAH']+gap: return ("cao hon", +1.0)
    if d['VAH'] < p['VAL']-gap: return ("thap hon", -1.0)
    if d['VAH']>p['VAH'] and d['VAL']>p['VAL']: return ("chong len cao hon", +0.5)
    if d['VAH']<p['VAH'] and d['VAL']<p['VAL']: return ("chong len thap hon", -0.5)
    if d['VAH']<=p['VAH'] and d['VAL']>=p['VAL']: return ("nam trong", 0.0)
    return ("bao trum", 0.15*(1 if d['close']>p['POC'] else -1))

def part2():
    print("="*72); print("PART 2 — Engine bias NGAY (gia tri chot) + kiem huong ngay ke tiep")
    P=daily_profiles()
    full=[d for d in P if d['nbars']>=38]  # bo profile cut
    ranges=[d['rng'] for d in full]
    ibs=[d['ibr'] for d in full]
    deltas=[abs(d['delta']) for d in full]
    def roll_med(vals,i,w=20):
        s=vals[max(0,i-w):i]; return st.median(s) if s else st.median(vals)
    print(f"  RangeTypical(med)={st.median(ranges):.0f}t  IBTypical={st.median(ibs):.0f}t  DeltaTypical={st.median(deltas):.0f}")
    hits=0; scored=0; rows_out=[]
    for i in range(1,len(full)):
        d=full[i]; p=full[i-1]
        RT=roll_med(ranges,i); IT=roll_med(ibs,i); DT=roll_med(deltas,i)
        # Signal A value relationship
        rel,sA = value_rel(d,p,RT)
        # Signal B poc migration
        sB=max(-1,min(1,((d['POC']-p['POC'])/(RT*TICK))/0.10))
        # Signal C one-sided RE
        RE_up=(d['high']-d['IBH'])/TICK; RE_dn=(d['IBL']-d['low'])/TICK
        ib=max(1,d['ibr'])
        one=( (RE_up>0.5*ib) != (RE_dn>0.5*ib) )
        sC=0
        if one and RE_up>RE_dn: sC=min(1,RE_up/ib)
        elif one and RE_dn>RE_up: sC=-min(1,RE_dn/ib)
        # Signal E delta (de-skew -0.7%)
        dpct=100*d['delta']/max(1,d['vol'])
        sE=max(-1,min(1,(dpct-(-0.7))/1.5))
        S = sA*25 + sB*15 + sC*15 + sE*10
        label = ("Tang manh" if S>=45 else "Tang" if S>=18 else "Trung tinh" if S>-18 else "Giam" if S>-45 else "Giam manh")
        rows_out.append((d['date'].strftime('%m/%d'), rel, f"{S:+.0f}", label))
        # sanity: bias huong co khop POC ngay ke tiep khong?
        if i+1<len(full) and abs(S)>=18:
            nxt=full[i+1]; moved=nxt['POC']-d['POC']
            scored+=1; hits+= (1 if (S>0)==(moved>0) else 0)
    print("  vd 8 ngay:  date | value-rel | score | bias")
    for r in rows_out[-8:]: print("   ",r[0],"|",r[1],"|",r[2],"|",r[3])
    if scored: print(f"  [sanity] bias co huong (|S|>=18) khop dau POC ngay ke tiep: {hits}/{scored} = {hits/scored:.0%}  (chi la check logic, KHONG phai backtest)")

# ================================================================
# PART 3 — GOP PHIEN A/AU/MY + VUNG (m30)
# ================================================================
def session_of(tod_min):
    # tod_min = phut trong ngay (gio VN)
    if 5*60 <= tod_min < 12*60+30: return "A"
    if 12*60+30 <= tod_min < 19*60: return "AU"
    return "MY"  # 19:00-04:00 (wrap)

def part3():
    print("="*72); print("PART 3 — Gop phien A/Au/My + summary + vung (m30 + reconstruct)")
    h, rows = load("tpo-chart-m30.csv")
    iO,iH,iL,iC,iV = h.index('Open'),h.index('High'),h.index('Low'),h.index('Close'),h.index('Volume')
    iD=h.index('Delta'); iDT=h.index('DateTime')
    bars=[]
    for x in rows:
        dt=pdt(x[iDT])
        bars.append(dict(dt=dt, o=fnum(x[iO]),h=fnum(x[iH]),l=fnum(x[iL]),c=fnum(x[iC]),
                         v=fnum(x[iV]),d=fnum(x[iD])))
    # gop thanh block phien: break khi doi label hoac gap thoi gian > 40'
    blocks=[]; cur=None
    for b in bars:
        lab=session_of(b['dt'].hour*60+b['dt'].minute)
        newblk = (cur is None or lab!=cur['lab'] or (b['dt']-cur['bars'][-1]['dt'])>timedelta(minutes=40))
        if newblk:
            cur=dict(lab=lab,bars=[]); blocks.append(cur)
        cur['bars'].append(b)
    def summ(blk):
        bb=blk['bars']
        o=bb[0]['o']; c=bb[-1]['c']; hi=max(x['h'] for x in bb); lo=min(x['l'] for x in bb)
        rng=(hi-lo)/TICK; delta=sum(x['d'] for x in bb); vol=sum(x['v'] for x in bb)
        c_tpo=tpo_counts([(x['l'],x['h']) for x in bb])
        poc,vah,val=value_area(c_tpo)
        cp=(c-lo)/(hi-lo) if hi>lo else 0.5
        vaw=(vah-val)/TICK if vah else 0
        bal="ROT" if vaw/max(1,rng)>=0.55 else "TREND" if vaw/max(1,rng)<=0.35 else "INT"
        return dict(lab=blk['lab'],start=bb[0]['dt'],end=bb[-1]['dt'],n=len(bb),o=o,c=c,hi=hi,lo=lo,
            rng=rng,poc=poc,vah=vah,val=val,vaw=vaw,delta=delta,vol=vol,
            dirn=("UP" if c>o else "DOWN" if c<o else "FLAT"),
            close_state=("MANH" if cp>=0.70 else "YEU" if cp<=0.30 else "TB"),
            balance=bal)
    S=[summ(b) for b in blocks if len(b['bars'])>=5]
    print(f"  So block phien >=5 nen: {len(S)}")
    print("  phien | start | dir | rng(t) | POC | VA(VAL-VAH) | delta | close | balance | vs-truoc")
    def accept(b,a):
        ovl=max(0,min(a['vah'],b['vah'])-max(a['val'],b['val']))
        uni=max(a['vah'],b['vah'])-min(a['val'],b['val'])
        frac=ovl/uni if uni>0 else 0
        mig=(b['poc']-a['poc'])/TICK
        tag="ACCEPT" if frac>=0.5 else "REJECT" if frac<0.2 else "PARTIAL"
        return f"{tag} POC{mig:+.0f}t"
    for i,s in enumerate(S):
        vs = accept(s,S[i-1]) if i>0 else "-"
        thuan = "thuan" if (s['delta']>0)==(s['dirn']=="UP") else "NGHICH"
        print(f"   {s['lab']:3} | {s['start'].strftime('%m/%d %H:%M')} | {s['dirn']:4} | {s['rng']:4.0f} | {s['poc']:.1f} | {s['val']:.1f}-{s['vah']:.1f} | {s['delta']:+5.0f}({thuan}) | {s['close_state']:4} | {s['balance']:5} | {vs}")
    # VUNG: naked POC + POC clustering
    print("  --- VUNG (zones) ---")
    # naked POC: POC phien s chua bi nen phien SAU (sau khi phien do KET THUC) cham lai
    for k,s in enumerate(S):
        later=[b for b in bars if b['dt']>s['end']]
        touched=any(b['l']<=s['poc']<=b['h'] for b in later)
        if not touched:
            print(f"   NAKED POC {s['poc']:.1f}  (phien {s['lab']} {s['start'].strftime('%m/%d %H:%M')}) — chua kiem dinh (nam cham)")
    # 2 tang: (a) confluence CHAT <=7t  (b) bang tich luy gia trong <=25t
    def cluster(pocs, tol_t, minn):
        pocs=sorted(pocs); out=[]; c=[pocs[0]]
        for p in pocs[1:]:
            if (p-c[-1])/TICK <= tol_t: c.append(p)
            else:
                if len(c)>=minn: out.append((c[0],c[-1],len(c)))
                c=[p]
        if len(c)>=minn: out.append((c[0],c[-1],len(c)))
        return out
    pocs=[s['poc'] for s in S]
    tight=cluster(pocs,7,2); band=cluster(pocs,25,3)
    for a,b_,n in tight: print(f"   CUM POC chat {a:.1f}-{b_:.1f} ({n} POC, <=7t) -> S/R rat manh")
    for a,b_,n in band:  print(f"   BANG tich luy gia tri {a:.1f}-{b_:.1f} ({n} POC, <=25t) -> vung S/R")

part1(); part2(); part3()
print("="*72); print("DONE")
