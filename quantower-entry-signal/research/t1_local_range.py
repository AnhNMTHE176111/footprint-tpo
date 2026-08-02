"""T1 — bat vung range cuc bo, xem hop luu tai 3 ca bo sot co len >=2 khong."""
import sys, copy
from datetime import datetime
sys.path.insert(0,"/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_replay_july as R
CASES=[(datetime(2026,7,31,7,59),4125.1,"ca1 SHORT"),(datetime(2026,7,31,12,36),4104.2,"ca2 SHORT"),
       (datetime(2026,7,31,15,38),4098.4,"ca3 LONG")]
B=R.load_bars(); lv=R.load_levels()
for bars,maxh in ((30,5.0),(30,8.0),(45,8.0),(60,10.0),(20,4.0)):
    R.ENABLE_LOCAL_RANGE=True; R.RANGE_BARS=bars; R.RANGE_MAX_H=maxh
    pool,vw=R.build_pool(B,lv)
    nr=len([z for z in pool if "range" in z["kind"]])
    print(f"=== RANGE_BARS={bars} RANGE_MAX_H={maxh}  -> them {nr} vung range (tong pool {len(pool)}) ===")
    for t,px,lbl in CASES:
        c=R.cluster_count(pool,t,px)
        near=sorted([z for z in pool if not z["is_vwap"] and z["ready"]<=t<=z["expire"] and abs(z["price"]-px)<=1.0],
                    key=lambda z:abs(z["price"]-px))
        s=", ".join(f"{z['kind']} {z['price']:.1f}" for z in near[:5])
        print(f"   {lbl} @{px}: cum={c}   [{s}]")
