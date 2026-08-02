import sys, copy
sys.path.insert(0,"/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_replay_july as R, entry_fixA_test as F
TICK=R.TICK
B=R.load_bars(); lv=R.load_levels(); pool,vw=R.build_pool(B,lv)
raw=R.scan(B,pool,lv,vw); R.MIN_CONFLUENCE=2
sig=R.dedup(copy.deepcopy(raw))
for s in sig: s["out"],s["r"],s["outt"]=R.simulate(B,s)
bad=[s for s in sig if F.body_dir(B[s["i"]])!=s["side"]]
print("SOI 7 LENH NGUOC MAU (gate>=2): 10 nen sau nen kich hoat, tim nen THUAN mau + VSA>=1.2 + delta thuan")
for s in bad:
    i=s["i"]; side=s["side"]; sd='LONG' if side>0 else 'SHORT'
    print("="*104)
    print(f"{s['time']:%Y-%m-%d %H:%M} {sd} entry {s['entry']:.1f} SL {s['sl']:.1f} TP {s['tp1']:.1f} -> KQ live {s['out']}   vung {s['zone']}")
    found=None
    for j in range(i+1,min(i+11,len(B)-1)):
        b=B[j]; d=F.body_dir(b)
        ok = d==side and b["vratio"]>=R.VSA_GATE and (b["delta"]>0 if side>0 else b["delta"]<0)
        mark = "  <== NEN XAC NHAN" if (ok and found is None) else ""
        if ok and found is None: found=j
        print(f"   +{j-i:>2} {b['time']:%H:%M} O={b['o']:.1f} C={b['c']:.1f} {'TANG' if d>0 else ('GIAM' if d<0 else 'doji'):<5} v={b['vol']:>4.0f} vr={b['vratio']:.1f} d={b['delta']:+.0f}{mark}")
    if found is None: print("   => KHONG co nen xac nhan trong 10 nen")
    else:
        b=B[found]; entry=b["c"]
        anchor=(s["sl"]+R.SL_BUF*TICK) if side>0 else (s["sl"]-R.SL_BUF*TICK)
        a=min(anchor,b["l"]) if side>0 else max(anchor,b["h"])
        sl=min(a-R.SL_BUF*TICK,entry-R.SL_FLOOR) if side>0 else max(a+R.SL_BUF*TICK,entry+R.SL_FLOOR)
        risk=abs(entry-sl)/TICK
        n=dict(s); n.update(i=found,entry=entry,sl=sl,risk_t=risk,
                            tp1=entry+R.RR*risk*TICK if side>0 else entry-R.RR*risk*TICK)
        o,r,t=R.simulate(B,n)
        cap = "  (VUOT SlCap -> live se BO LENH)" if risk*TICK > max(R.SL_CAP,R.SL_FLOOR)+1e-9 else ""
        print(f"   => vao lai tai {entry:.1f} SL {sl:.1f} (risk {risk*TICK:.1f} gia{cap}) TP {n['tp1']:.1f} => {o}")
