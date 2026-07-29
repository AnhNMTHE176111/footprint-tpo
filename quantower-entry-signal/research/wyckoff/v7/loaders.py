#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
loaders.py — v7 (SPEC_V7_3KB.md §2.3, §DATA_CAPABILITY §7.b/e).

Ha tang con thieu duoc viet moi o day:
  - sessions_from_m1()   : gom phien tu M1 (gap>45'), GIU bar-index range (khac
                            entry_dxfeed.daily_levels_from_m1 chi tra start/vah/val/poc/hi/lo,
                            khong tra i0/i1 -> khong du de tinh IB bar-by-bar).
  - ib_from_m1()          : IB (Initial Balance) tu M1, CHUA co trong entry_dxfeed.py (DATA_CAPABILITY §7.e).
  - load_fp_m1()          : wrap entry_dxfeed.load_fpm1 (fp-m1, CO delta) — dung rieng cho KB2 delta-confirm.
  - load_tpo_daily()      : doc TPO-chart-daily.csv CHI de doi chung (SPEC §2.2 — moi dong trong 1 phien
                            deu bi DAP gia tri CHOT, khong dung lam nguon chinh).

KHONG import/sua cbr_v6.py o day (frozen). Duoc phep import entry_dxfeed.py (ha tang dung chung, khong frozen).
"""
import sys, os
from datetime import timedelta
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_dxfeed as E

TICK = E.TICK


def sessions_from_m1(B, gap_min=45):
    """Gom B (da sort theo dt) thanh cac phien, gap > gap_min phut = phien moi (khop DayGapMin=45 cua C#).

    CHI doc B[0..cuoi]; ham nay khong tu no gay look-ahead — no la buoc GOM CAU TRUC tinh
    mot lan tren toan bo B da co san (giong cach cbr_v6.prepare() tinh truoc `trend`/`liqratio`
    roi engine chi doc gia tri tai time-of-decision). Cai bat buoc chong look-ahead nam o
    NGUOI GOI: chi duoc dung poc/vah/val/ib cua phien D[s-1]/D[s-2] (phien DA DONG) va IB cua
    phien D[s] CHI SAU ready_at — xem session_bias() trong features.py.

    Tra ve: list[dict(i0,i1,start,end,poc,vah,val,hi,lo)] — i0/i1 la INDEX trong B (inclusive).
    """
    out = []
    i0 = 0
    n = len(B)
    for i in range(1, n + 1):
        newsess = (i == n) or ((B[i]['dt'] - B[i - 1]['dt']) > timedelta(minutes=gap_min))
        if newsess:
            i1 = i - 1
            bb = B[i0:i1 + 1]
            if len(bb) >= 30:
                poc, vah, val = E.value_area(E.tpo_counts([(x['lo'], x['hi']) for x in bb]))
                if poc is not None:
                    out.append(dict(i0=i0, i1=i1, start=bb[0]['dt'], end=bb[-1]['dt'],
                                     poc=poc, vah=vah, val=val,
                                     hi=max(x['hi'] for x in bb), lo=min(x['lo'] for x in bb)))
            i0 = i
    return out


def ib_from_m1(B, sess, minutes=60):
    """IB (Initial Balance) = max/min cua cac nen trong [start, start+minutes) cua 1 phien.
    (DATA_CAPABILITY §7.e — chua co ham nay trong entry_dxfeed.py, viet moi.)

    Tra ve (None, None) neu phien KET THUC truoc khi du so phut IB (cua so IB chua kip dong
    trong chinh phien do) — CHU Y: day la kiem tra tinh trang TINH DUOC, khong phai kiem tra
    "da toi thoi diem hien tai chua" (do la viec cua session_bias(): chi doc ib_hi/ib_lo cho
    cac nen co dt >= ready_at = start + minutes).
    """
    end_of_ib = sess['start'] + timedelta(minutes=minutes)
    bars = [b for b in B[sess['i0']:sess['i1'] + 1] if b['dt'] < end_of_ib]
    if not bars or (sess['end'] < end_of_ib):
        return None, None
    return max(b['hi'] for b in bars), min(b['lo'] for b in bars)


# ⚠⚠ LOI DU LIEU DA XAC NHAN (AUDIT_V7 §G, do lai 2026-07-29):
# fp-m1-6-month.csv co cot Volume HONG trong 2026-06-04 -> 2026-06-26:
#   22.297 / 29.850 nen thang 6 (74,7%) co Volume=0 DU Ticks(from bar)>0 => chac chan hong,
#   khong phai phien vang. OHLC van DUNG (audit doi chieu gia khop tuyet doi voi dxFeed).
# HE QUA: moi feature dua tren volume (vma, vratio, VSA, gate volfloor, liqratio, VWAP) SAI
# trong khoang do. Bat ky ket luan nao chay tren thang 6 cua file NAY deu vo hieu.
# CACH DUNG DUNG: loai thang 6 (xem FPM1_VOLUME_BAD_FROM/TO) hoac chi dung OHLC + Delta.
FPM1_VOLUME_BAD_FROM = "2026-06-04"
FPM1_VOLUME_BAD_TO   = "2026-06-26"


def fpm1_volume_ok(b):
    """True neu nen b nam NGOAI vung Volume hong cua fp-m1-6-month.csv (AUDIT_V7 §G).
    Dung de loc truoc khi tinh bat ky thong ke nao co volume tren file nay."""
    d = b['dt'].strftime("%Y-%m-%d")
    return not (FPM1_VOLUME_BAD_FROM <= d <= FPM1_VOLUME_BAD_TO)


def _warn_fpm1_volume(B, path):
    bad = sum(1 for b in B if b['v'] == 0)
    if bad:
        print(f"⚠ {path}: {bad}/{len(B)} nen co Volume=0 (loi du lieu da biet, "
              f"{FPM1_VOLUME_BAD_FROM}->{FPM1_VOLUME_BAD_TO}, AUDIT_V7 §G). "
              f"MOI feature volume trong khoang do KHONG dung duoc — loc bang loaders.fpm1_volume_ok().")
    return B


def load_fp_m1(path="fp-m1-6-month.csv"):
    """fp-m1 (CO Delta/Delta%/Bid-Ask volume), nhan UTC+7. Dung rieng cho feature fp-only
    (SPEC §3 'Bo du lieu'). KHONG so truc tiep so voi dxFeed (n khac, mui gio khac).
    ⚠ Volume hong 2026-06 — xem ghi chu FPM1_VOLUME_BAD_* o tren."""
    return _warn_fpm1_volume(E.load_fpm1(path), path)


def load_fp_m1_full(path="fp-m1-6-month.csv"):
    """fp-m1 day du field nhu entry_dxfeed.load_fpm1 (vwap/vma/vratio/rng/uw/lw/brat/cpos/up/dn/
    since_gap/ym) + THEM cot 'Delta, %' (delta_pct) — E.load_fpm1 KHONG doc cot nay.
    Dung rieng cho KB2 delta-confirm (SPEC §5.4: '|Delta %| >= 20%'), CHAY tren imp_reversal_sweep.detect()
    (KHONG dung reversal_vwap.vwap_reversal() — file do tu ghi ro 'dung so tu detect() trong FILE NAY la SAI')."""
    h, rows = E.load(path)
    ix = {n: i for i, n in enumerate(h)}
    B = [dict(dt=E.pdt_fp(x[ix['DateTime']]), o=E.fn(x[ix['Open']]), hi=E.fn(x[ix['High']]),
              lo=E.fn(x[ix['Low']]), c=E.fn(x[ix['Close']]), v=E.fn(x[ix['Volume']]),
              delta=E.fn(x[ix['Delta']]), delta_pct=E.fn(x[ix['Delta, %']])) for x in rows]
    B.sort(key=lambda b: b['dt'])
    csum_pv = csum_v = 0.0
    for i, b in enumerate(B):
        gap = i > 0 and (b['dt'] - B[i - 1]['dt']).total_seconds() / 60 > 30
        if gap:
            csum_pv = csum_v = 0.0
        tp = (b['hi'] + b['lo'] + b['c']) / 3.0
        csum_pv += tp * b['v']; csum_v += b['v']
        b['vwap'] = csum_pv / csum_v if csum_v > 0 else b['c']
        win = [B[j]['v'] for j in range(max(0, i - E.VSA_MA + 1), i + 1)]
        sma = sum(win) / len(win) if win else b['v']
        b['vma'] = sma; b['vratio'] = b['v'] / sma if sma > 1e-9 else 0.0
        rng = b['hi'] - b['lo']; b['rng'] = rng; b['body'] = abs(b['c'] - b['o'])
        b['uw'] = b['hi'] - max(b['o'], b['c']); b['lw'] = min(b['o'], b['c']) - b['lo']
        b['brat'] = b['body'] / rng if rng > 0 else 0.0
        b['cpos'] = (b['c'] - b['lo']) / rng if rng > 0 else 0.5
        b['up'] = b['c'] > b['o']; b['dn'] = b['c'] < b['o']
        b['ddom'] = b['delta'] / b['v'] if b['v'] > 0 else 0.0
        b['since_gap'] = 0 if gap else (B[i - 1]['since_gap'] + 1 if i > 0 else 999)
        b['ym'] = b['dt'].strftime('%Y-%m')
    return _warn_fpm1_volume(B, path)


def load_tpo_daily(path="TPO-chart-daily.csv"):
    """Doc TPO-chart-daily.csv (thuc ra la nen 30 PHUT, ho so TPO theo NGAY — DATA_CAPABILITY §1.4).
    CHI dung de DOI CHUNG (22 phien, 2026-06-25->07-25) — SPEC §2.2: moi dong trong 1 phien
    deu bi DAP gia tri VAH/VAL/POC/IB CHOT cua phien, kho ca nen dau phien -> KHONG dung lam
    nguon chinh cho bias bar-by-bar."""
    h, rows = E.load(path)
    ix = {n: i for i, n in enumerate(h)}
    need = ['DateTime', 'IB High', 'IB Low', 'VAH', 'VAL', 'POC']
    for c in need:
        if c not in ix:
            raise KeyError(f"thieu cot {c} trong {path}")
    out = []
    for x in rows:
        out.append(dict(
            dt_str=x[ix['DateTime']],
            day=x[ix['DateTime']].split()[0],
            ib_hi=E.fn(x[ix['IB High']]), ib_lo=E.fn(x[ix['IB Low']]),
            vah=E.fn(x[ix['VAH']]), val=E.fn(x[ix['VAL']]), poc=E.fn(x[ix['POC']]),
        ))
    return out
