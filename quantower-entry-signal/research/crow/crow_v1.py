#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CROW v1 — engine backtest cho concept CROWCONCEP x DFT (momentum follow-trend, RR 1:2).
================================================================================
Nguon luat: data-export/messages-with-pro-trader/CROWCONCEP_DFT.md (X1..X9).

DAC TA CHOT TRUOC KHI CHAY (khong duoc sua sau khi xem ket qua — moi thay doi phai ghi log
o cuoi RESULTS_CROW.md nhu "vong 2/3" de dem so phep thu):

LOI (X1 + X2 + X9), khong gate nao:
  X1 IMPULSE tai nen i:  brat >= IMP_BODY (than to)  AND  rng >= IMP_K * median(rng, 100 nen TRUOC)
                         AND vratio >= IMP_VSA  AND  dung huong (up: c>o).
     -> "luc phat di du lon, nen than to it rau". median cuon 100 nen = chuan hoa bien dong (portable).
  X2 PULLBACK: base = lo cua nen impulse (LONG). peak = max hi tu i..j. leg = peak - base.
     retr_j = (peak - lo_j)/leg. Vao lenh tai nen j dau tien co:
        PMIN <= retr_j <= PMAX  AND  nen j thuan huong (up) AND brat_j >= RBODY.
     Neu retr_j > PMAX ("test qua sau") -> HUY luon setup nay (dung dac ta X2).
     Cua so cho: WAIT nen.
  ENTRY = close cua nen j (khop cach v5 do luong). SL = cuc tri nhip hoi -/+ BUF tick,
     kep trong [FLOOR..CAP] gia. TP = RR * risk (RR=2.0 theo X9).
  Gate thanh khoan: v >= VOLFLOOR_FROZEN (20) + since_gap >= 20 + vma >= 0.6*floor (giong v5/v6).
  Dedup: 1 lenh / 6 nen / phia (E.DEDUP_BARS). Cooldown COOL nen sau moi lenh.

GATE BAT TAT (moi cai test RIENG LE truoc, roi moi chong):
  X3  DMA      : DMA(delta, DMA_N) > 0 cho LONG (< 0 cho SHORT) tai nen VAO. Can feed co delta.
                 Bien the DMA_NARROW=True: chi ap khi range NARROW_N nen truoc <= NARROW_K*medrng.
  X5  BUBBLE   : vi tri o volume/ask lon nhat trong nen tin hieu, pos=(p-lo)/(hi-lo).
                 LONG can pos <= BUB_MAX ("khong duoc sat high"). Can per-level.
  X7  KEYLEVEL : veto neu entry nam trong +-KEY_T tick cua mot vung trong pool (POC/VAH/VAL/
                 dinh/day phien + D-1) HOAC cua VWAP phien.
  X8  WIDEBRK  : neu WIDE_N nen truoc co span >= WIDE_MIN gia (sideway bien rong) thi doi nen
                 impulse phai DONG ngoai bien do (break ro rang).
  TREND        : loc thuan xu huong kieu v5 (close vs close 480 nen, tol 1.0 gia).

CHAY:
  python3 crow_v1.py core     -> loi + sweep tham so cau truc (dxFeed, 05-07/2026)
  python3 crow_v1.py gates    -> tung gate rieng le (dxFeed: X7/X8/TREND)
  python3 crow_v1.py delta    -> merged feed (co delta + per-level): X3, X5
  python3 crow_v1.py null     -> null model cho cau hinh tot nhat
TRUNG THUC: dxFeed KHONG co delta -> moi ket qua X3/X5 chi tren merged (n nho hon), bao rieng.
"""
import sys, os, statistics as st
from collections import defaultdict, deque

R = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research"
sys.path.insert(0, R)
sys.path.insert(0, os.path.join(R, "wyckoff"))
sys.path.insert(0, os.path.join(R, "wyckoff", "v7"))
import entry_dxfeed as E
import cbr_v6
from v7 import report

TICK = E.TICK
MONTHS = ('2026-05', '2026-06', '2026-07')
VF = E.VOLFLOOR_FROZEN


# ---------------------------------------------------------------- config
def cfg(**kw):
    c = dict(
        # --- loi X1/X2/X9 ---
        IMP_BODY=0.60, IMP_K=1.5, IMP_VSA=1.5, MEDLB=100,
        WAIT=12, PMIN=0.15, PMAX=0.50, RBODY=0.35,
        FLOOR=20, CAP=50, BUF=2, RR=2.0, COOL=15,
        # --- gate ---
        TREND=False,
        DMA=False, DMA_N=9, DMA_NARROW=False, NARROW_N=10, NARROW_K=2.5,
        BUB=False, BUB_MAX=0.60, BUB_BAR='entry',   # 'entry' | 'impulse'
        BUB_SIDE='aggr',                            # 'aggr' = o ask lon nhat (LONG) | 'vol' = o volume lon nhat
        KEY=False, KEY_T=7,
        WIDE=False, WIDE_N=30, WIDE_MIN=100,
        # --- VONG 2 (them sau khi vong 1 cho LOI AM; 3 kha nang lech dac ta, xem RESULTS_CROW §3) ---
        # COMPRESS: nen impulse phai KHOI PHAT tu vung NEN (pha bien range CN nen truoc, span <= CSPAN gia)
        #   — anh 1/anh 7 deu ve "sideway roi phat luc"; vong 1 cho phep impulse o GIUA xu huong (chase).
        COMPRESS=False, CN=12, CSPAN=75,
        # CONFIRM: khong vao ngay nen thuan huong dau tien; doi nen sau DONG tren HIGH cua no
        #   (giong nhanh B arm->confirm cua KB4 da chung minh co gia tri).
        CONFIRM=False, CF_WAIT=6,
        # FADE: vao NGUOC huong impulse — chi de KIEM DAU tin hieu, khong phai de ship.
        FADE=False,
        # --- VONG 3: MODEL HAP THU lam entry (X6) + quan ly lenh ---
        # ABS: thay dieu kien "nen thuan huong + than>=RBODY" bang NEN HAP THU tai nhip hoi:
        #   aggressor NGUOC huong setup ap dao (ddom <= -ABS_DD cho LONG) NHUNG gia khong di
        #   theo no (dong nua tren than + rau nguoc >= ABS_WICK*rng). Can feed co delta.
        #   X6 noi ro "model Hap thu KHONG can big volume" -> khong doi vratio.
        ABS=False, ABS_DD=0.15, ABS_WICK=0.30, ABS_CPOS=0.50,
        # BE: dua SL ve entry sau khi da di duoc BE_AT * risk (0 = tat). Bi quan: chi doi tu NEN SAU.
        BE_AT=0.0,
    )
    c.update(kw)
    return c


# ---------------------------------------------------------------- prep
def prep(B):
    """Tinh median range CUON (100 nen truoc, KHONG gom nen hien tai -> khong look-ahead)
    + trend/liqratio theo cbr_v6.prepare (da sua 3 loi parity)."""
    cbr_v6.prepare(B)
    dq = deque()
    for b in B:
        b['medrng'] = st.median(dq) if len(dq) >= 20 else None
        dq.append(b['rng'])
        if len(dq) > 100:
            dq.popleft()
    # DMA cuon tren delta (chi bar co delta); None neu thieu
    dq2 = deque(); s = 0.0
    for b in B:
        d = b.get('delta')
        b['_dma_pre'] = (s / len(dq2)) if dq2 else None
        if d is not None:
            dq2.append(d); s += d
            if len(dq2) > 32:
                s -= dq2.popleft()
    return B


def dma_at(B, i, n):
    """DMA(delta, n) tinh tren n nen KET THUC tai nen i (nen i da dong khi ta vao lenh o close)."""
    vals = [B[j].get('delta') for j in range(max(0, i - n + 1), i + 1)]
    vals = [v for v in vals if v is not None]
    if len(vals) < max(3, n // 2):
        return None
    return sum(vals) / len(vals)


def bubble_pos(b, side, mode='aggr'):
    """Vi tri 'bong no' trong nen: mode 'aggr' = muc gia co ask_vol (LONG) / bid_vol (SHORT) lon nhat;
    mode 'vol' = muc gia co tong volume lon nhat (POC nen = HVN cell).
    ⚠ Feed KHONG cap max_one_trade (toan 0, DATA_CAPABILITY §3) -> day la PROXY cho 'lenh don lon',
    khong phai lenh don thuc su."""
    lv = b.get('levels') or {}
    if not lv or b['rng'] <= 0:
        return None
    if mode == 'vol':
        p = max(lv, key=lambda k: lv[k]['vol'])
    else:
        key = 'ask' if side == 'LONG' else 'bid'
        if max(lv[k][key] for k in lv) <= 0:
            return None
        p = max(lv, key=lambda k: lv[k][key])
    return (p - b['lo']) / b['rng']


# ---------------------------------------------------------------- gates
def _gate(b):
    return b['v'] >= VF and b['since_gap'] >= E.WARMUP_AFTER_GAP and b['vma'] >= VF * 0.6


def near_key(px, t, pool, vwap, tol_t):
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(px - z['price']) <= tol_t * TICK:
            return True
    return abs(px - vwap) <= tol_t * TICK


def compress_break(B, i, up, C):
    """VONG 2: nen impulse phai KHOI PHAT tu vung NEN — CN nen truoc co span <= CSPAN tick
    VA nen impulse dong ngoai bien vung do. Chinh la 'sideway roi phat luc' trong anh 1/anh 7."""
    win = B[i - C['CN']:i]
    if len(win) < C['CN']:
        return False
    hi = max(x['hi'] for x in win); lo = min(x['lo'] for x in win)
    if (hi - lo) / TICK > C['CSPAN']:
        return False
    return (B[i]['c'] > hi) if up else (B[i]['c'] < lo)


def wide_ok(B, i, up, C):
    """X8: neu WIDE_N nen truoc la sideway BIEN RONG (span >= WIDE_MIN tick) thi nen impulse
    phai DONG ngoai bien do. Range hep hoac trending -> khong ap dieu kien."""
    win = B[i - C['WIDE_N']:i]
    if len(win) < C['WIDE_N']:
        return True
    hi = max(x['hi'] for x in win); lo = min(x['lo'] for x in win)
    if (hi - lo) / TICK < C['WIDE_MIN']:
        return True
    return (B[i]['c'] > hi) if up else (B[i]['c'] < lo)


# ---------------------------------------------------------------- scan
def run(B, C, pool=None):
    raw = []; N = len(B); last = -10 ** 9
    for i in range(max(E.VSA_MA + 2, C['MEDLB']), N - 1):
        b = B[i]
        if i - last < C['COOL']:
            continue
        if not _gate(b) or b['medrng'] is None or b['rng'] <= 0:
            continue
        # ---- X1 impulse
        if b['brat'] < C['IMP_BODY'] or b['rng'] < C['IMP_K'] * b['medrng'] or b['vratio'] < C['IMP_VSA']:
            continue
        for up in (True, False):
            if up and not b['up']:
                continue
            if (not up) and not b['dn']:
                continue
            side = 'LONG' if up else 'SHORT'
            if C['TREND'] and b['trend'] != (1 if up else -1):
                continue
            if C['WIDE'] and not wide_ok(B, i, up, C):
                continue
            if C['COMPRESS'] and not compress_break(B, i, up, C):
                continue
            if C['BUB'] and C['BUB_BAR'] == 'impulse':
                bp = bubble_pos(b, side, C['BUB_SIDE'])
                if bp is None:
                    continue
                if (bp > C['BUB_MAX']) if up else (bp < 1 - C['BUB_MAX']):
                    continue
            base = b['lo'] if up else b['hi']
            peak = b['hi'] if up else b['lo']
            ext = peak            # cuc tri nhip hoi (de neo SL)
            for j in range(i + 1, min(N, i + 1 + C['WAIT'])):
                bj = B[j]
                if not _gate(bj):
                    break
                peak = max(peak, bj['hi']) if up else min(peak, bj['lo'])
                ext = min(ext, bj['lo']) if up else max(ext, bj['hi'])
                leg = (peak - base) if up else (base - peak)
                if leg <= 0:
                    break
                retr = ((peak - bj['lo']) / leg) if up else ((bj['hi'] - peak) / leg)
                if retr > C['PMAX']:
                    break                       # "test qua sau" -> huy
                if retr < C['PMIN']:
                    continue
                if C['ABS']:
                    dd = bj.get('ddom')
                    if dd is None:
                        continue
                    ddn = dd if up else -dd                      # ddn<0 = aggressor NGUOC setup
                    wick = (bj['lw'] if up else bj['uw']) / bj['rng']
                    cp = bj['cpos'] if up else 1 - bj['cpos']
                    if not (ddn <= -C['ABS_DD'] and wick >= C['ABS_WICK'] and cp >= C['ABS_CPOS']):
                        continue
                else:
                    if not ((bj['up'] and up) or (bj['dn'] and not up)):
                        continue
                    if bj['brat'] < C['RBODY']:
                        continue
                # ---- gate tai nen VAO
                if C['DMA']:
                    need = not C['DMA_NARROW']
                    if C['DMA_NARROW']:
                        # "sideway bien hep" = span NARROW_N nen truoc <= NARROW_K * range trung vi 1 nen
                        w = B[j - C['NARROW_N']:j]
                        mr = bj['medrng'] or 0
                        span = (max(x['hi'] for x in w) - min(x['lo'] for x in w)) if w else 0
                        need = len(w) == C['NARROW_N'] and mr > 0 and span <= C['NARROW_K'] * mr
                    if need:
                        d = dma_at(B, j, C['DMA_N'])
                        if d is None or ((d <= 0) if up else (d >= 0)):
                            continue
                if C['BUB'] and C['BUB_BAR'] == 'entry':
                    bp = bubble_pos(bj, side, C['BUB_SIDE'])
                    if bp is None:
                        continue
                    if (bp > C['BUB_MAX']) if up else (bp < 1 - C['BUB_MAX']):
                        continue
                # ---- CONFIRM: doi nen sau DONG vuot cuc tri thuan huong cua nen hoi (arm)
                k = j
                if C['CONFIRM']:
                    k = None
                    for m in range(j + 1, min(N, j + 1 + C['CF_WAIT'])):
                        bm = B[m]
                        if not _gate(bm):
                            break
                        ext = min(ext, bm['lo']) if up else max(ext, bm['hi'])
                        if (bm['c'] > bj['hi']) if up else (bm['c'] < bj['lo']):
                            k = m
                            break
                        if (bm['c'] < ext) if up else (bm['c'] > ext):
                            break
                    if k is None:
                        break
                bk = B[k]
                entry = bk['c']
                if C['KEY'] and pool is not None and near_key(entry, bk['dt'], pool, bk['vwap'], C['KEY_T']):
                    continue
                sl = (ext - C['BUF'] * TICK) if up else (ext + C['BUF'] * TICK)
                risk_t = abs(entry - sl) / TICK
                if risk_t < C['FLOOR']:
                    sl = entry - C['FLOOR'] * TICK if up else entry + C['FLOOR'] * TICK
                    risk_t = C['FLOOR']
                if risk_t > C['CAP']:
                    break
                if C['FADE']:      # KIEM DAU: vao nguoc huong, cung risk
                    side = 'SHORT' if up else 'LONG'
                    sl = entry + risk_t * TICK if up else entry - risk_t * TICK
                raw.append(dict(i=k, dt=bk['dt'], ym=bk['ym'], side=side, entry=entry, sl=sl,
                                risk_t=risk_t, retr=retr, imp=i, legt=leg / TICK))
                last = k
                break
    return raw


def hit(B, i, side, sl, tp, entry=None, be_at=0.0):
    """Bi quan: trong cung nen kiem SL TRUOC TP. BE (dua SL ve entry) chi ap tu NEN SAU khi
    nen truoc da dat be_at*risk — khong doc gia trong nen."""
    risk = abs(entry - sl) if (entry is not None and be_at > 0) else None
    moved = False
    for j in range(i + 1, len(B)):
        b = B[j]
        if (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl):
            return 'BE' if moved else 'SL'
        if (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp):
            return 'TP'
        if risk and not moved:
            reach = (b['hi'] - entry) if side == 'LONG' else (entry - b['lo'])
            if reach >= be_at * risk:
                sl = entry
                moved = True
    return 'open'


def evaluate(B, sig, C, cost_t=0.0):
    out = []
    for s in sig:
        r = s['risk_t'] * TICK
        tp = s['entry'] + C['RR'] * r if s['side'] == 'LONG' else s['entry'] - C['RR'] * r
        o = hit(B, s['i'], s['side'], s['sl'], tp, s['entry'], C.get('BE_AT', 0.0))
        if o == 'open':
            continue
        s2 = dict(s)
        base_r = C['RR'] if o == 'TP' else (0.0 if o == 'BE' else -1.0)
        s2['r'] = base_r - cost_t / s['risk_t']
        out.append(s2)
    return out


def dedup(raw):
    out = []
    for s in sorted(raw, key=lambda x: x['i']):
        if any(m['side'] == s['side'] and abs(s['i'] - m['i']) <= E.DEDUP_BARS for m in out):
            continue
        out.append(s)
    return out


def pipe(B, C, tag, pool=None, months=MONTHS, cost_t=0.0, quiet=False):
    S = evaluate(B, dedup(run(B, C, pool)), C, cost_t)
    if months:
        S = [s for s in S if s['ym'] in months]
    d = None if quiet else report.line(tag, S, months)
    return S, d
