#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
features.py — v7: tang BIAS phien (SPEC §2) + tang DO LUC (SPEC §3, mot phan: WY04).
MOI ham chi doc du lieu TOI NEN i (hoac phien DA DONG) — ghi ro trong tung docstring.
"""
import sys, os
from datetime import timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loaders

# ===================================================================== §2 — BIAS PHIEN
TOL = 0.5          # gia — dung sai so sanh POC (SPEC §2.4: DE XUAT, sweep 0.2/0.5/1.0)
MIN_SCORE = 2       # |score| >= 2 moi coi la co bias (SPEC §2.4: DE XUAT, sweep 1/2/3)


def session_bias(D, s, B, ib_minutes=60, tol=None, min_score=None):
    """1 LAN/phien, KHOA lai het phien (R5: 'bias khong dao giua phien').

    D    = loaders.sessions_from_m1(B) — CHI phien DA DONG duoc dung o day la D[s-1], D[s-2].
    s    = chi so phien HIEN TAI trong D (>=2, de co D[s-1] va D[s-2]).
    B    = M1 bars goc — CHI dung de doc close nen dau phien s (open_px) va cho ib_from_m1
           (ca hai deu la du lieu cua CHINH phien s, khong phai phien tuong lai).

    Look-ahead: c1/c2 dung D[s-1]/D[s-2] (VA/POC da CHOT, phien da dong) -> AN TOAN.
    c3 dung ib_from_m1() -> tra (None,None) neu cua so IB (ib_minutes phut dau phien s) CHUA
    dong -> nguoi goi (session_bias_series) PHAI tu kiem dt cua nen hien tai so voi ready_at
    truoc khi doc bias — ham nay CHI tinh 1 gia tri "sau khi IB da du du lieu trong D", khong
    tu gate theo thoi gian.
    """
    tol = TOL if tol is None else tol
    min_score = MIN_SCORE if min_score is None else min_score
    d1, d2 = D[s - 1], D[s - 2]
    sess = D[s]
    open_px = B[sess['i0']]['c']
    c1 = 1 if d1['poc'] > d2['poc'] + tol else (-1 if d1['poc'] < d2['poc'] - tol else 0)
    c2 = 1 if open_px > d1['vah'] else (-1 if open_px < d1['val'] else 0)
    ib_hi, ib_lo = loaders.ib_from_m1(B, sess, ib_minutes)
    c3 = 0 if ib_hi is None else (1 if ib_lo > d1['poc'] else (-1 if ib_hi < d1['poc'] else 0))
    score = c1 + c2 + c3
    bias = 1 if score >= min_score else (-1 if score <= -min_score else 0)
    return dict(score=score, c1=c1, c2=c2, c3=c3, bias=bias, conf=abs(score) / 3.0,
                ready_at=sess['start'] + timedelta(minutes=ib_minutes))


def session_bias_series(B, ib_minutes=60, tol=None, min_score=None):
    """Tra ve bias_at[i] (mang dai len(B)) — bias cua PHIEN chua nen i, DA GATE theo thoi gian:

    ⟦QUYET DINH GD6 — xem 'can quyet' trong RESULTS_KB12.md⟧: TRUOC ready_at (IB chua dong),
    bias_at = 0 (KHONG dung bias lam gate trong khoang nay), thay vi dung ban score=c1+c2
    (MIN_SCORE-1) ma SPEC §2.4 de xuat nhu mot lua chon khac — chon phuong an don gian nhat,
    an toan hon ve overfit (khong them 1 nhanh logic nua chi de dung <=60 phut dau moi phien).

    SAU ready_at: bias KHOA nguyen gia tri toi het phien (dung 1 lan, khong tinh lai) — dung
    dinh R5. 2 phien dau tien (s=0,1) khong co D[s-2] -> bias=0 ca phien.

    Chi doc D (da tach phien DA DONG) va B[i]['dt'] (thoi diem cua CHINH nen i) — khong nhin
    truoc: bias cua nen i KHONG BAO GIO phu thuoc bar j>i.
    """
    D = loaders.sessions_from_m1(B)
    bias_at = [0] * len(B)
    log = []
    for s in range(2, len(D)):
        sess = D[s]
        info = session_bias(D, s, B, ib_minutes, tol=tol, min_score=min_score)
        for i in range(sess['i0'], sess['i1'] + 1):
            bias_at[i] = info['bias'] if B[i]['dt'] >= info['ready_at'] else 0
        log.append(dict(s=s, start=sess['start'], ready_at=info['ready_at'],
                         score=info['score'], bias=info['bias'], conf=info['conf']))
    return bias_at, log


# ===================================================================== §3 — TANG DO LUC (WY04)
def no_supply(B, i):
    """WY04 'No Supply' — nen giam (c<o) nhung CAN KIET nguon cung: rng VA volume deu nho hon
    2 nen lien truoc. Chi doc B[i], B[i-1], B[i-2] (nhan-qua tuyet doi, khong nhin tuong lai)."""
    if i < 2:
        return False
    b, b1, b2 = B[i], B[i - 1], B[i - 2]
    return (b['c'] < b['o'] and b['rng'] < b1['rng'] and b['rng'] < b2['rng']
            and b['v'] < b1['v'] and b['v'] < b2['v'])


def no_demand(B, i):
    """WY04 'No Demand' — guong lai no_supply, nen tang (c>o) nhung yeu dan. Chi doc B[i-2..i]."""
    if i < 2:
        return False
    b, b1, b2 = B[i], B[i - 1], B[i - 2]
    return (b['c'] > b['o'] and b['rng'] < b1['rng'] and b['rng'] < b2['rng']
            and b['v'] < b1['v'] and b['v'] < b2['v'])


# ===================================================================== §4.3 — RANGE STATE MACHINE
DEFAULT_P = dict(FORM=30, TOUCH=2, SEP=3, TOLF=0.15, TOLMIN=0.3,
                  WMIN=2.0, WMAX=6.0, MAXBARS=120, BUF=0.2)


def _new_range(i, b):
    return dict(state='FORMING', rhi=b['hi'], rlo=b['lo'], i0=i,
                tu=[], td=[], brk_dir=None, brk_bar=None, valid_bar=None)


def _range_step(R, B, i, P):
    """1 buoc cua state machine range theo cau truc (SPEC §4.3, y het pseudocode — THU TU la
    mot phan cua dac ta). Chi doc B[i] (nen HIEN TAI) va R (trang thai da tich luy tu B[0..i-1])
    — khong nhin B[i+1:]. Tra ve (R_moi, just_validated: bool)."""
    b = B[i]
    if b['since_gap'] == 0:
        return _new_range(i, b), False
    if R is None or R['state'] == 'NONE':
        return _new_range(i, b), False
    buf = P['BUF']
    if b['c'] > R['rhi'] + buf or b['c'] < R['rlo'] - buf:
        if R['state'] == 'VALID':
            R = dict(R)
            R['state'] = 'BREAKING'
            R['brk_dir'] = 1 if b['c'] > R['rhi'] else -1
            R['brk_bar'] = i
            return R, False
        return _new_range(i, b), False          # range CHUA hop le -> vuot bien KHONG phai break
    R = dict(R)
    if R['state'] == 'BREAKING':
        # dong lai TRONG bien trong <=2 nen => pha THAT BAI (quet hut / spring)
        R['state'] = 'VALID' if (i - R['brk_bar']) <= 2 else 'DEAD'
        if R['state'] == 'DEAD':
            return R, False
    nhi, nlo = max(R['rhi'], b['hi']), min(R['rlo'], b['lo'])
    if nhi - nlo > P['WMAX']:
        return _new_range(i, b), False           # loang ra => khong con la vung nen
    R['rhi'], R['rlo'] = nhi, nlo
    if i - R['i0'] + 1 > P['MAXBARS']:
        R['state'] = 'DEAD'
        return R, False
    tol = max(P['TOLMIN'], P['TOLF'] * (R['rhi'] - R['rlo']))
    if b['hi'] >= R['rhi'] - tol and (not R['tu'] or i - R['tu'][-1] >= P['SEP']):
        R['tu'] = R['tu'] + [i]
    if b['lo'] <= R['rlo'] + tol and (not R['td'] or i - R['td'][-1] >= P['SEP']):
        R['td'] = R['td'] + [i]
    just_validated = False
    if (R['state'] == 'FORMING' and i - R['i0'] + 1 >= P['FORM']
            and len(R['tu']) >= P['TOUCH'] and len(R['td']) >= P['TOUCH']
            and P['WMIN'] <= R['rhi'] - R['rlo'] <= P['WMAX']):
        R['state'] = 'VALID'
        R['valid_bar'] = i
        just_validated = True
    return R, just_validated


def range_struct_scan(B, P=None):
    """Quet toan bo B mot lan (bar-by-bar, KHONG quet cua so trung lap — khac probe cu).

    Tra ve:
      states : list[dict|None] dai len(B) — trang thai R SAU khi xu ly nen i (de debug).
      arms   : list[dict(i,up,edge,width,valid_bar)] — moi lan mot range DA VALID vua chuyen
               sang BREAKING tai dung nen i (day la dieu kien ARM cua KB1, SPEC §4.4).
      valids : list[dict(i,rhi,rlo,i0,width)] — moi lan mot range MOI dat VALID lan dau (dung
               de dem n_range doi chieu voi probe §11.B).
    """
    P = dict(DEFAULT_P, **(P or {}))
    R = dict(state='NONE')
    states = [None] * len(B)
    arms, valids = [], []
    for i in range(len(B)):
        prev_state = R.get('state')
        prev_rhi, prev_rlo = R.get('rhi'), R.get('rlo')
        R2, just_validated = _range_step(R, B, i, P)
        if R2['state'] == 'BREAKING' and R2.get('brk_bar') == i and prev_state == 'VALID':
            up = R2['brk_dir'] == 1
            arms.append(dict(i=i, up=up, edge=(prev_rhi if up else prev_rlo),
                              width=prev_rhi - prev_rlo, valid_bar=R2.get('valid_bar')))
        if just_validated:
            valids.append(dict(i=i, rhi=R2['rhi'], rlo=R2['rlo'], i0=R2['i0'],
                                width=R2['rhi'] - R2['rlo']))
        states[i] = R2
        R = R2
    return states, arms, valids
