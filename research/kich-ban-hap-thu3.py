"""Ban 3: (A) 3 kich ban CHIA THEO VUNG, (B) do ky vong cua tung kieu vao lenh.

Vung tinh tu chinh file bars (UTC, phien CME bat dau 22:00 UTC):
  - tren/duoi VWAP ngay
  - co phai day PHIEN (thap nhat tu dau phien) khong
  - co dinh vao vung day/dinh PHIEN TRUOC (+-1.0 va +-2.0 gia) khong
  - trong gio pit COMEX (13:20-18:30 UTC) hay ngoai gio
"""
import os, sys, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kich_ban_hap_thu_load import load
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
W, LOOK, FWD = 50, 20, 30

def sessions(t):
    """session id = so ngay, moc 22:00 UTC"""
    return [(x + 120) // 1440 for x in t]

def context(t, o, h, l, c, v):
    sid = sessions(t)
    n = len(t)
    vwap = [0.0]*n; sess_low = [0.0]*n; sess_high = [0.0]*n
    prev_low = [None]*n; prev_high = [None]*n
    pv = 0.0; pvol = 0.0; slo = 1e18; shi = -1e18
    cur = sid[0]; done = {}
    for i in range(n):
        if sid[i] != cur:
            done[cur] = (slo, shi)
            cur = sid[i]; pv = pvol = 0.0; slo = 1e18; shi = -1e18
        tp = (h[i]+l[i]+c[i])/3.0
        pv += tp*v[i]; pvol += v[i]
        vwap[i] = pv/pvol if pvol > 0 else c[i]
        slo = min(slo, l[i]); shi = max(shi, h[i])
        sess_low[i] = slo; sess_high[i] = shi
        p = done.get(sid[i]-1)
        if p: prev_low[i], prev_high[i] = p
    return sid, vwap, sess_low, sess_high, prev_low, prev_high

def find_events(t, o, h, l, c, v, dl, vol_mult=3.0, dlt_mult=4.0):
    n = len(t); out = []; i = W+LOOK
    while i < n-FWD-31:
        if l[i] > min(l[i-LOOK:i]): i += 1; continue
        seg = t[i-W:i+FWD+31]
        if seg[-1]-seg[0] != len(seg)-1: i += 1; continue
        mv = st.median(v[i-W:i]); md = st.median([abs(x) for x in dl[i-W:i]])
        if mv <= 0 or md <= 0: i += 1; continue
        if v[i] < vol_mult*mv or dl[i] > -dlt_mult*md: i += 1; continue
        if h[i]-l[i] <= 0: i += 1; continue
        out.append(i); i += FWD
    return out

def classify(i, h, l, up_R=2.0, brk_rel=0.5, retest=0.5, start=1):
    R = h[i]-l[i]; L = l[i]; bt = brk_rel*R; tgt = L+up_R*R; rt = False
    for j in range(i+start, i+1+FWD):
        if l[j] <= L-bt: return "K3"
        if h[j] >= tgt: return "K2" if rt else "K1"
        if l[j] <= L+retest: rt = True
    return "K0"

def pct(res):
    tot = sum(res.values()) or 1
    return " ".join(f"{k} {100.0*res[k]/tot:4.1f}%" for k in ("K1","K2","K3","K0")) + f"  n={sum(res.values())}"

def split_report(name, ev, cond, h, l, confirmed_only, dl):
    buckets = {}
    for i in ev:
        if confirmed_only and dl[i+1] < 0.5*abs(dl[i]): continue
        b = cond(i)
        if b is None: continue
        buckets.setdefault(b, {"K1":0,"K2":0,"K3":0,"K0":0})
        buckets[b][classify(i, h, l, start=2 if confirmed_only else 1)] += 1
    print(f"\n  [{name}]")
    for b in sorted(buckets, key=lambda x: str(x)):
        if sum(buckets[b].values()) < 25: 
            print(f"    {str(b):28s} (n<25, bo qua)"); continue
        print(f"    {str(b):28s} {pct(buckets[b])}")

# ---------- B. do ky vong tung kieu vao lenh ----------
def trade(entry, stop, i, h, l, c, jstart, horizon=60, rr=2.0, longside=True):
    risk = (entry-stop) if longside else (stop-entry)
    if risk <= 0: return None
    tgt = entry + rr*risk if longside else entry - rr*risk
    for j in range(jstart, min(i+horizon, len(h)-1)):
        if longside:
            if l[j] <= stop: return -1.0
            if h[j] >= tgt: return rr
        else:
            if h[j] >= stop: return -1.0
            if l[j] <= tgt: return rr
    j = min(i+horizon, len(h)-1)
    return ((c[j]-entry)/risk) if longside else ((entry-c[j])/risk)

def variants(ev, t, o, h, l, c, v, dl):
    out = {}
    def add(k, r):
        if r is not None: out.setdefault(k, []).append(r)
    for i in ev:
        L = l[i]; R = h[i]-l[i]
        # V0: vao ngay tai dong nen xac nhan (delta dao >=50%)
        if dl[i+1] >= 0.5*abs(dl[i]):
            add("V0 vao ngay nen xac nhan", trade(c[i+1], L-0.5*R, i, h, l, c, i+2))
        # V1/V2: cho k nen KHONG tao day moi (di ngang), roi vao nen tang dau tien co delta>0
        for k in (2, 3):
            if min(l[i+1:i+1+k]) <= L: continue
            e = None
            for j in range(i+1+k, i+1+k+8):
                if j >= len(h)-1: break
                if l[j] <= L: e = None; break
                if c[j] > o[j] and dl[j] > 0: e = j; break
            if e:
                add(f"V{1 if k==2 else 2} cho {k} nen di ngang roi vao nen tang",
                    trade(c[e], L-0.5*R, i, h, l, c, e+1))
        # V3: sau 2 nen di ngang ma xuyen day -> BAN
        if min(l[i+1:i+3]) > L:
            hi = max(h[i+1:i+3]); e = None
            for j in range(i+3, i+3+8):
                if j >= len(h)-1: break
                if l[j] <= L-0.5*R: e = j; break
            if e:
                add("V3 di ngang roi xuyen day -> BAN", trade(c[e], hi+0.3, i, h, l, c, e+1, longside=False))
    return out

if __name__ == "__main__":
    t,o,h,l,c,v,dl = load(PATH); print("so nen:", len(t), flush=True)
    sid,vwap,slo,shi,plo,phi = context(t,o,h,l,c,v)
    ev = find_events(t,o,h,l,c,v,dl); print("so ca ban thao:", len(ev), flush=True)

    for tag, conf in (("KHONG loc xac nhan", False), ("CO loc xac nhan (delta dao >=50%)", True)):
        print(f"\n=== A. {tag} ===")
        split_report("tat ca", ev, lambda i: "chung", h, l, conf, dl)
        split_report("so voi VWAP ngay", ev,
            lambda i: "duoi VWAP" if c[i] < vwap[i] else "tren VWAP", h, l, conf, dl)
        split_report("co phai day PHIEN", ev,
            lambda i: "day phien moi" if l[i] <= slo[i]+1e-9 else "chi la day 20 nen", h, l, conf, dl)
        for d in (1.0, 2.0):
            split_report(f"dinh vung day phien truoc +-{d}", ev,
                lambda i, d=d: None if plo[i] is None else
                    (f"TRUNG day phien truoc" if abs(l[i]-plo[i]) <= d else "khong trung"),
                h, l, conf, dl)
        split_report("gio pit COMEX (13:20-18:30 UTC)", ev,
            lambda i: "trong gio pit" if 800 <= (t[i] % 1440) <= 1110 else "ngoai gio pit",
            h, l, conf, dl)

    print("\n=== B. ky vong tung kieu vao lenh (dung lo duoi day 0,5 bien nen; dich 2R; toi da 60 nen) ===")
    res = variants(ev,t,o,h,l,c,v,dl)
    for k in sorted(res):
        a = res[k]; n = len(a)
        win = sum(1 for x in a if x >= 1.99); loss = sum(1 for x in a if x <= -0.99)
        print(f"  {k:46s} n={n:5d}  thang {100.0*win/n:4.1f}%  thua {100.0*loss/n:4.1f}%  "
              f"ky vong {st.mean(a):+.3f}R  trung vi {st.median(a):+.2f}R")
