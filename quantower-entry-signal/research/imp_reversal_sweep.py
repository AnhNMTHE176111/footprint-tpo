#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMP_REVERSAL_SWEEP — map count<->WR frontier for the QUAY_DAU (reversal-at-VWAP) branch.
Reuses reversal_vwap.py loaders/_finalize (VWAP/VSA/wick/body identical to RunnerSignal.cs).
Replicates ScanReversal + EmitRev + TrendOk + per-side cooldown EXACTLY (LIVE gate values),
then sweeps each gate one at a time. CORRECTION (2026-07-29): dxFeed 'Time left' is UTC, NOT
VN display time — proven in WYCKOFF_V6_PLAN.md Buoc 1 (hour 21 has 0 bars = CME break at
17:00 ET = 21:00 UTC; export filename timestamp is 22:56 but last row is 15:56 = 7h offset).
apply_dead()/dead_lo/dead_hi below take an UTC hour, matching WyckoffRunner.cs DeadUseUtc=true.

LIVE ground truth (RunnerSignal_signals.csv, C#): QUAY_DAU n=28 settled, WR 57%, EV +0.429R,
total +12.0R at RevRR=1.5 (16W/12L).
"""
import csv, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "wyckoff"))
import reversal_vwap as rv
import cbr_v6 as V6   # counter_sweep() for BUOC 6 test (BREAK SACH cho QUAY_DAU)
from collections import defaultdict, OrderedDict

TICK = rv.TICK
DX = ("/home/asl86/Documents/footprint-tpo/data-export/27-7/"
      "_GCQ26XCEC dxFeed, Time - Time - 1m, 11_3_2025 120000 AM-7_27_2026 105600 PM_8b750702-5f00-4836-bf74-81e2a0c4495f.csv")
LIVE_CSV = "/home/asl86/Documents/footprint-tpo/data-export/27-7/RunnerSignal_signals.csv"

# ---------------- LIVE gate values (from RunnerSignal.cs) ----------------
LIVE = dict(
    vol_floor=20, warmup=20,          # Gate()  VolFloor / WarmupBars
    vwap_tol_t=12,                    # VwapTolTicks
    approach_bars=6,                  # RevApproachBars
    wick_frac=0.50,                   # WickFrac
    cpos_h=0.05,                      # Cpos band: SHORT<=0.5-h, LONG>=0.5+h  (live 0.45/0.55)
    body_min=0.30,                    # b.Brat>=0.30 (hardcoded)
    vsa_conf=1.8,                     # RevVsaConf
    trend_filter=True, trend_bars=480, trend_tol_t=10,  # TrendFilter/TrendBars/TrendTolPts(1.0pt=10t)
    sl_buf_t=2, sl_cap_t=70, risk_min=5,               # SlBuf / SlCapPts(7.0=70t) / (risk<=5 reject)
    cooldown=15,                      # Cooldown
    rr=1.5,                           # RevRR
    dead=False, dead_lo=2, dead_hi=8, # SkipDeadSession / DeadStartHour / DeadEndHour
    clean_mode=None,                  # BUOC 6 (v6 plan Sec.7): None=tat, 'clean'=doi hoi SACH (nhu
                                       # CBR NoCounterSweep), 'dirty'=doi hoi CO quet nguoc gan do
    cl_look=20, cl_w=5, cl_close=0.50,  # tham so cho V6.counter_sweep(), khop CleanLook/CleanWin/CleanClosePos
)

# ---------------- data ----------------
_B = None
def bars():
    global _B
    if _B is None:
        _B = rv.load_dxfeed(DX)          # full history Nov2025..Jul2026 (vwap/vsa/wick/body computed)
    return _B

def trend_at(B, i, N, tol_t):
    if i < N: return 0
    d = B[i]['c'] - B[i-N]['c']
    t = tol_t*TICK
    return 1 if d > t else -1 if d < -t else 0

# ---------------- detector: exact ScanReversal + EmitRev replica ----------------
def detect(B, **kw):
    P = dict(LIVE); P.update(kw)
    vol_floor=P['vol_floor']; warmup=P['warmup']
    tol=P['vwap_tol_t']*TICK; appro=P['approach_bars']
    wick=P['wick_frac']; h=P['cpos_h']; body=P['body_min']; vsac=P['vsa_conf']
    tf=P['trend_filter']; tN=P['trend_bars']; ttol=P['trend_tol_t']
    buf=P['sl_buf_t']*TICK; cap=P['sl_cap_t']; rmin=P['risk_min']; cd=P['cooldown']
    cpos_lo=0.5-h; cpos_hi=0.5+h
    N=len(B); raw=[]
    start=max(rv.VSA_MA+2, tN if tf else 0)
    for i in range(start, N):
        b=B[i]
        if not (b['v']>=vol_floor and b['since_gap']>=warmup and b['vma']>=vol_floor*0.6): continue
        rng=b['rng']
        if rng<=0: continue
        vw=b['vwap']
        touch_up = b['hi'] >= vw - tol
        rej_short = (b['uw']>=wick*rng and b['cpos']<=cpos_lo and b['c']<vw and b['brat']>=body and b['vratio']>=vsac)
        touch_dn = b['lo'] <= vw + tol
        rej_long = (b['lw']>=wick*rng and b['cpos']>=cpos_hi and b['c']>vw and b['brat']>=body and b['vratio']>=vsac)
        appro_up=appro_dn=False
        for k in range(max(0,i-appro), i):
            if B[k]['c']<vw: appro_up=True
            if B[k]['c']>vw: appro_dn=True
        side=0; anchor=0.0
        if touch_up and rej_short and appro_up: side=-1; anchor=max(b['hi'],vw)
        elif touch_dn and rej_long and appro_dn: side=+1; anchor=min(b['lo'],vw)
        if side==0: continue
        if P['clean_mode'] is not None:
            # BUOC 6 (v6 plan Sec.7): approach direction = huong tiep can VWAP (nguoc voi side vi day
            # la reversal/fade). SHORT (side=-1) tiep can tu duoi len => up=True; LONG (side=+1) tiep
            # can tu tren xuong => up=False. Dung LAI ham V6.counter_sweep() cua CBR, KHONG viet lai.
            appro_up_dir = (side < 0)
            dirty = V6.counter_sweep(B, i, appro_up_dir, P['cl_look'], P['cl_w'], P['cl_close'])
            if P['clean_mode'] == 'clean' and dirty: continue
            if P['clean_mode'] == 'dirty' and not dirty: continue
        if tf and trend_at(B,i,tN,ttol)!=side: continue   # TrendOk (before cooldown, matches C#)
        entry=b['c']
        if side>0: sl=anchor-buf; risk=(entry-sl)/TICK
        else: sl=anchor+buf; risk=(sl-entry)/TICK
        if risk<=rmin or risk>cap: continue
        raw.append(dict(i=i, dt=b['dt'], side=('LONG' if side>0 else 'SHORT'),
                        entry=entry, sl=sl, risk_t=risk, vsa=b['vratio']))
    # per-side cooldown (matches Cooldown_)
    out=[]; last={}
    for s in sorted(raw, key=lambda x:x['i']):
        if s['i']-last.get(s['side'],-999) < cd: continue
        out.append(s); last[s['side']]=s['i']
    return out

def in_window(B, sigs, y=2026, m0=5, m1=7):
    return [s for s in sigs if s['dt'].year==y and m0<=s['dt'].month<=m1]

def apply_dead(sigs, lo=2, hi=8):
    return [s for s in sigs if not (lo <= s['dt'].hour < hi)]

# ---------------- backtest ----------------
def score(B, sigs, rr):
    """returns dict with n_sig, closed, tp, sl, amb, wr, ev, net, per-month cells."""
    bym=defaultdict(lambda:[0,0,0.0,0,0])  # closed, tp, net, sl, amb
    tot=[0,0,0.0,0,0]
    for s in sigs:
        r=s['risk_t']*TICK
        tgt = s['entry']+rr*r if s['side']=='LONG' else s['entry']-rr*r
        o=rv.hit(B, s['i'], s['side'], s['sl'], tgt)
        if o not in ('TP','SL','amb'): continue
        m=s['dt'].strftime('%Y-%m')
        win = (o=='TP')
        dr = rr if win else -1
        for agg in (bym[m], tot):
            agg[0]+=1; agg[1]+=win; agg[2]+=dr
            agg[3]+= (o=='SL'); agg[4]+=(o=='amb')
    closed,tp,net,sl,amb=tot
    return dict(n_sig=len(sigs), closed=closed, tp=tp, sl=sl, amb=amb,
                wr=(tp/closed if closed else 0), ev=(net/closed if closed else 0),
                net=net, bym={k:tuple(v) for k,v in bym.items()})

def allpos(res):
    b=res['bym']
    return len(b)>=2 and all(v[2]>=0 for v in b.values())

def fmt(res, label):
    cells="  ".join(f"{k[-2:]}:{v[2]:+.0f}R({v[1]}/{v[0]})" for k,v in sorted(res['bym'].items()))
    lown = "  LOWn" if res['closed']<20 else ""
    lowcell = " LOWcell" if any(v[0]<6 for v in res['bym'].values()) else ""
    ap = " ALL+" if allpos(res) else ""
    print(f"  {label:26s} nsig={res['n_sig']:3d} closed={res['closed']:3d} WR {res['wr']*100:3.0f}% "
          f"EV {res['ev']:+.3f} net {res['net']:+5.1f}R{ap}{lown}{lowcell}  [{cells}]")
    return res

# ============================================================================
def load_live_rev():
    rows=list(csv.DictReader(open(LIVE_CSV,encoding='utf-8-sig')))
    q=[r for r in rows if r['nhanh'].strip()=='QUAY_DAU']
    return q

def main():
    B=bars()
    print(f"data bars={len(B)}  range {B[0]['dt']} .. {B[-1]['dt']}")
    print("="*104)

    # ---- (0) RECONCILE offline detector vs live 28 ----
    live=load_live_rev()
    print(f"LIVE QUAY_DAU rows={len(live)} (all settled)")
    sig_live_params = in_window(B, detect(B))
    off_set = {(s['dt'].strftime('%Y-%m-%d %H:%M'), s['side']) for s in sig_live_params}
    live_set = {(r['ngay_gio'].strip(), 'LONG' if r['huong'].strip()=='LONG' else 'SHORT') for r in live}
    inter = off_set & live_set
    print(f"OFFLINE (LIVE params, May-Jul) nsig={len(sig_live_params)}  matched live entries={len(inter)}/{len(live_set)}")
    miss=sorted(live_set-off_set)
    print(f"  live-only (not reproduced offline): {len(miss)}  e.g. {miss[:6]}")
    extra=sorted(off_set-live_set)
    print(f"  offline-only (not in live): {len(extra)}  e.g. {extra[:6]}")
    print("="*104)

    # ---- (1) BASELINE ----
    print("(1) BASELINE — LIVE params, May-Jul 2026, RR=1.5")
    base=fmt(score(B, sig_live_params, LIVE['rr']), "LIVE baseline")
    print("="*104)

    # ---- (2) SWEEP each gate one at a time ----
    print("(2) SWEEP (one knob at a time; LIVE value marked *). loosen=more trades")
    def run(label, **kw):
        s=in_window(B, detect(B, **kw))
        return fmt(score(B, s, kw.get('rr', LIVE['rr'])), label)

    sweeps=OrderedDict([
      ("VSA_CONF (RevVsaConf)", [("vsa_conf",v) for v in (1.4,1.6,1.8,2.0,2.2,2.5)]),
      ("VWAP_TOL_T (VwapTolTicks)", [("vwap_tol_t",v) for v in (6,9,12,16,20,30)]),
      ("APPROACH_BARS (RevApproachBars)", [("approach_bars",v) for v in (3,4,6,8,12)]),
      ("WICK_FRAC (WickFrac)", [("wick_frac",v) for v in (0.35,0.40,0.45,0.50,0.60)]),
      ("BODY_MIN (Brat hardcoded .30)", [("body_min",v) for v in (0.20,0.25,0.30,0.40)]),
      ("CPOS band h (0.45/0.55)", [("cpos_h",v) for v in (0.0,0.05,0.10,0.15)]),
      ("TREND_TOL_T (TrendTolPts)", [("trend_tol_t",v) for v in (0,5,10,20)]),
      ("TREND_BARS (TrendBars)", [("trend_bars",v) for v in (240,360,480,720)]),
      ("SL_CAP_T (SlCapPts)", [("sl_cap_t",v) for v in (50,60,70,100,999)]),
      ("COOLDOWN (Cooldown)", [("cooldown",v) for v in (5,10,15,30)]),
      ("RR (RevRR) — count-invariant", [("rr",v) for v in (1.0,1.25,1.5,2.0,2.5)]),
    ])
    for grp,items in sweeps.items():
        print(f"\n-- {grp} --")
        for k,v in items:
            star="*" if abs(LIVE[k]-v)<1e-9 else " "
            run(f"{star}{k}={v}", **{k:v})

    # ---- TREND OFF (big loosen) ----
    print("\n-- TREND_FILTER OFF (drop THUAN-trend gate entirely) --")
    run(" trend_filter=OFF", trend_filter=False)

    # ---- (2b) COMBINED loosenings ----
    print("\n" + "="*104)
    print("(2b) COMBINED loosenings (promising knobs together)")
    combos=OrderedDict([
      ("C1 vsa1.6+tol16", dict(vsa_conf=1.6, vwap_tol_t=16)),
      ("C2 vsa1.6+appro8", dict(vsa_conf=1.6, approach_bars=8)),
      ("C3 vsa1.6+tol16+appro8", dict(vsa_conf=1.6, vwap_tol_t=16, approach_bars=8)),
      ("C4 vsa1.6+wick0.45", dict(vsa_conf=1.6, wick_frac=0.45)),
      ("C5 tol16+appro8+wick0.45", dict(vwap_tol_t=16, approach_bars=8, wick_frac=0.45)),
      ("C6 vsa1.6+trendtol5", dict(vsa_conf=1.6, trend_tol_t=5)),
      ("C7 vsa1.6+tol16+wick0.45+appro8", dict(vsa_conf=1.6, vwap_tol_t=16, wick_frac=0.45, approach_bars=8)),
    ])
    for name,kw in combos.items():
        run(name, **kw)

    # ---- (4) DEAD-SESSION cross-check ----
    print("\n" + "="*104)
    print("(4) DEAD-SESSION cross-check (drop entry-bar hour in [02,08) VN). base vs +dead")
    def run_dead(label, **kw):
        s=in_window(B, detect(B, **kw))
        sd=apply_dead(s, LIVE['dead_lo'], LIVE['dead_hi'])
        r0=score(B,s,kw.get('rr',LIVE['rr'])); r1=score(B,sd,kw.get('rr',LIVE['rr']))
        fmt(r0, label+" (base)")
        fmt(r1, label+" (+dead)")
        return r0,r1
    run_dead("LIVE")
    run_dead("C1 vsa1.6+tol16", vsa_conf=1.6, vwap_tol_t=16)
    run_dead("C3 vsa1.6+tol16+appro8", vsa_conf=1.6, vwap_tol_t=16, approach_bars=8)
    run_dead("trend_OFF", trend_filter=False)

if __name__=="__main__":
    main()
