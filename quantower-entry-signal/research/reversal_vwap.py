#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REVERSAL v1 — thiet ke lai nhanh QUAY_DAU theo 4 setup that cua user (27-7).
Bai hoc tu live CSV (98 lenh QUAY_DAU, net -6R, WR 23%):
  - climax tim (22%) ~ hap thu (26%)  -> gate climax VO NGHIA
  - VSA bucket phang (VSA>=2.2 -> 23%, VSA<1.0 -> 32%)  -> VSA khong phan biet
  - co_vung NGUOC: 0 zone=33%, 1=16%, 2=17%, 3=0%  -> "confluence" auto = nhieu
=> nhanh cu ban sai tieu chi. 4 setup that deu neo vao VWAP (3/4) + PHA HUT (failed break)
   + 1 nen xac nhan manh (rau tu choi + dong manh + VSA cao). Xay lai quanh VWAP.

Data: GCQ26 chi THANH KHOAN tu ~thang 5 (med vol thang: 11/25=1 ... 5=5 6=55 7=43).
  => backtest CHINH tren cua so 6-7/2026 (front-month). Truoc do la hop dong deferred mong.
Trung thuc: offline THIEU footprint tung muc -> stacked imbalance / big-trade absorption =
  gate LIVE-only. O day test bo xuong (VWAP + rau + dong + climax + delta), do edge THUC.
"""
import csv, statistics as st
from datetime import datetime, timedelta
TICK = 0.1
VSA_MA = 20

# ---------------- loaders ----------------
def _finalize(B):
    """tinh vwap phien (reset khi gap>30'), VSA ratio (SMA20 incl current), wick/body, bias EMA30/120."""
    csum_pv = csum_v = 0.0
    ef = es = None; kf = 2/(30+1); ks = 2/(120+1)
    for i, b in enumerate(B):
        gap = i > 0 and (b['dt'] - B[i-1]['dt']).total_seconds()/60 > 30
        if gap or i == 0:
            csum_pv = csum_v = 0.0
        # reset VWAP theo phien lich (moc 5:00 / 12:30 / 19:00 gio VN) — dung ranh gioi ngay + gap
        tp = (b['hi'] + b['lo'] + b['c'])/3.0
        csum_pv += tp*b['v']; csum_v += b['v']
        b['vwap'] = csum_pv/csum_v if csum_v > 0 else b['c']
        win = [B[j]['v'] for j in range(max(0, i-VSA_MA+1), i+1)]
        sma = sum(win)/len(win) if win else b['v']
        b['vma'] = sma; b['vratio'] = b['v']/sma if sma > 1e-9 else 0.0
        rng = b['hi']-b['lo']; b['rng'] = rng; b['body'] = abs(b['c']-b['o'])
        b['uw'] = b['hi']-max(b['o'], b['c']); b['lw'] = min(b['o'], b['c'])-b['lo']
        b['brat'] = b['body']/rng if rng > 0 else 0.0
        b['cpos'] = (b['c']-b['lo'])/rng if rng > 0 else 0.5
        b['since_gap'] = 0 if (gap or i == 0) else B[i-1]['since_gap']+1
        b['ddom'] = b['delta']/b['v'] if b['v'] > 0 else 0.0
        ef = b['c'] if ef is None else ef+kf*(b['c']-ef)
        es = b['c'] if es is None else es+ks*(b['c']-es)
        b['bias'] = 1 if ef > es+3*TICK else -1 if ef < es-3*TICK else 0
    return B

def load_dxfeed(path):
    """dxFeed 9-thang: ';' Time left;...;Open;High;Median;Low;Close;...;Volume  (KHONG co delta)."""
    with open(path, encoding='utf-8-sig') as f:
        r = csv.reader(f, delimiter=';'); h = next(r); ix = {n: i for i, n in enumerate(h)}
        B = []
        for x in r:
            if not x or not x[0].strip(): continue
            B.append(dict(dt=datetime.strptime(x[ix['Time left']].strip()[:19], "%Y-%m-%d %H:%M:%S"),
                          o=float(x[ix['Open']]), hi=float(x[ix['High']]), lo=float(x[ix['Low']]),
                          c=float(x[ix['Close']]), v=float(x[ix['Volume']]), delta=0.0, maxd=0.0, mind=0.0))
    return _finalize(B)

def load_fp6(path):
    """fp-m1-6-month: ',' co DateTime(M/D/YYYY h:MM:SS AM/PM), OHLC, Volume, Delta, Max/Min delta."""
    with open(path, encoding='utf-8-sig') as f:
        r = csv.reader(f); h = next(r); ix = {n: i for i, n in enumerate(h)}
        def fn(s):
            try: return float(s)
            except: return 0.0
        B = []
        for x in r:
            if not x or not x[0].strip(): continue
            B.append(dict(dt=datetime.strptime(x[ix['DateTime']].strip(), "%m/%d/%Y %I:%M:%S %p"),
                          o=fn(x[ix['Open']]), hi=fn(x[ix['High']]), lo=fn(x[ix['Low']]),
                          c=fn(x[ix['Close']]), v=fn(x[ix['Volume']]), delta=fn(x[ix['Delta']]),
                          maxd=fn(x[ix['Max delta']]), mind=fn(x[ix['Min delta']])))
    return _finalize(B)

# ---------------- gate thanh khoan ----------------
VOL_FLOOR = 20
def gate(b): return b['v'] >= VOL_FLOOR and b['since_gap'] >= 20 and b['vma'] >= VOL_FLOOR*0.6

# ---------------- VWAP reversal ----------------
VWAP_TOL_T   = 12     # nen coi la "cham VWAP" khi rau xuyen vwap trong +-1.2 gia
APPROACH_BARS = 6     # nhip day vao VWAP trong 6 nen truoc
WICK_FRAC    = 0.45   # rau tu choi >= 45% range
CPOS_HI      = 0.55   # LONG: dong o nua tren
CPOS_LO      = 0.45   # SHORT: dong o nua duoi
BODY_MIN     = 0.30   # than toi thieu
VSA_CONF     = 1.8    # nen xac nhan VSA cao (KHONG bat buoc climax 2.2 — bai hoc: climax vo nghia,
                      #   nhung 'no luc' can du lon; thu 1.8)
SL_CAP_T     = 60     # tran 6 gia (user: "ko thi dat max 6 gia")
SL_BUF_T     = 2
RR           = 3.0
COOLDOWN     = 15
USE_DELTA    = False  # gate delta xac nhan (chi co tren fp6). test ca 2.

def vwap_reversal(B, use_delta=False):
    raw = []; N = len(B); last = {}
    for i in range(VSA_MA+2, N):
        b = B[i]
        if not gate(b): continue
        vw = b['vwap']
        rng = b['rng']
        if rng <= 0: continue
        # --- SHORT: VWAP la KHANG CU. gia day len cham vwap roi bi tu choi ---
        touch_up = b['hi'] >= vw - VWAP_TOL_T*TICK          # rau/than cham vwap tu duoi (hoac vuot)
        rej_short = (b['uw'] >= WICK_FRAC*rng and b['cpos'] <= CPOS_LO and b['c'] < vw
                     and b['brat'] >= BODY_MIN and b['vratio'] >= VSA_CONF)
        appro_up = any(B[k]['c'] < vw for k in range(max(0, i-APPROACH_BARS), i))  # den tu duoi VWAP
        dOK_s = (b['delta'] < 0) if use_delta else True
        # --- LONG: VWAP la HO TRO. gia dap xuong cham vwap roi bat len ---
        touch_dn = b['lo'] <= vw + VWAP_TOL_T*TICK
        rej_long = (b['lw'] >= WICK_FRAC*rng and b['cpos'] >= CPOS_HI and b['c'] > vw
                    and b['brat'] >= BODY_MIN and b['vratio'] >= VSA_CONF)
        appro_dn = any(B[k]['c'] > vw for k in range(max(0, i-APPROACH_BARS), i))
        dOK_l = (b['delta'] > 0) if use_delta else True

        side = None
        if touch_up and rej_short and appro_up and dOK_s:
            side = 'SHORT'; anchor = max(b['hi'], vw)
        elif touch_dn and rej_long and appro_dn and dOK_l:
            side = 'LONG'; anchor = min(b['lo'], vw)
        if side is None: continue
        if i - last.get(side, -999) < COOLDOWN: continue
        entry = b['c']
        if side == 'LONG':
            sl = anchor - SL_BUF_T*TICK; risk = (entry-sl)/TICK
        else:
            sl = anchor + SL_BUF_T*TICK; risk = (sl-entry)/TICK
        if risk <= 5 or risk > SL_CAP_T: continue
        last[side] = i
        raw.append(dict(i=i, dt=b['dt'], side=side, entry=entry, sl=sl, risk_t=risk,
                        vsa=b['vratio'], climax=b['vratio'] >= 2.2, vw=vw))
    return raw

def hit(B, i, side, sl, tp):
    for j in range(i+1, len(B)):
        b = B[j]
        hs = (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl)
        ht = (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp)
        if hs and ht: return 'amb'
        if hs: return 'SL'
        if ht: return 'TP'
    return 'open'

def bt(B, sigs, rm=RR, label=""):
    tp = sl = amb = 0; net = 0.0
    for s in sigs:
        r = s['risk_t']*TICK
        tgt = s['entry'] + rm*r if s['side'] == 'LONG' else s['entry'] - rm*r
        o = hit(B, s['i'], s['side'], s['sl'], tgt)
        if o == 'TP': tp += 1; net += rm
        elif o == 'SL': sl += 1; net -= 1
        elif o == 'amb': amb += 1; net -= 1  # bi quan: SL truoc
    n = tp+sl+amb
    wr = tp/n if n else 0
    print(f"   {label:30s} n={len(sigs):3d} closed={n:3d} WR {wr:.0%} net {net:+.1f}R  (amb {amb})")
    return net, wr, len(sigs)

def by_month(B, sigs, rm=RR):
    from collections import defaultdict
    m = defaultdict(list)
    for s in sigs: m[s['dt'].strftime('%Y-%m')].append(s)
    for k in sorted(m):
        bt(B, m[k], rm, f"  {k}")
