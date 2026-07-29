#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_review.py — dung bo file REVIEW cho nguoi dung cham tay.

Chay tu goc repo:  python3 need-review/build_review.py

NGUON DU LIEU (chi 2/3 indicator co export — xem 00-DOC-TRUOC-KHI-REVIEW.md):
  v5 RunnerSignal  -> data-export/27-7/runner_review.csv          (CBR + QUAY_DAU)
  v7 WyckoffRunner -> git show e7d4cde:data-export/28-7/...csv    (CBR + QUAY_DAU, luc con BAT)
  EntrySignal      -> KHONG CO EXPORT (chua bao gio xuat CSV)

Sinh ra 5 file review + 1 file doc truoc.
"""
import csv, io, os, re, subprocess
from collections import Counter, defaultdict
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'need-review')
V5P = os.path.join(ROOT, 'data-export/27-7/runner_review.csv')
V7_COMMIT = 'e7d4cde:data-export/28-7/WyckoffRunner_signals.csv'

dtp = lambda s: datetime.strptime(s.strip()[:16], '%Y-%m-%d %H:%M')


def load_v5():
    return list(csv.DictReader(open(V5P, encoding='utf-8-sig')))


def load_v7():
    raw = subprocess.run(['git', 'show', V7_COMMIT], capture_output=True, text=True,
                         cwd=ROOT).stdout
    if not raw.strip():
        raise SystemExit(f'Khong doc duoc {V7_COMMIT}')
    return list(csv.DictReader(io.StringIO(raw.lstrip('﻿'))))


def _from_ct(ct, pat):
    """Rut so tu cot chi_tiet, vd 'hoi 96%' -> '96%', 'leg 2.5gia' -> '2.5'.
    File v7 de trong cot retrace/leg_gia, nhung so nam trong chi_tiet."""
    m = re.search(pat, ct or '')
    return m.group(1) if m else ''


def norm(rows, src):
    out = []
    for r in rows:
        kq = (r.get('KQ') or '').strip().upper()
        if kq not in ('WIN', 'LOSS'):
            continue
        try:
            rr = float(r['RR'])
        except (ValueError, TypeError, KeyError):
            continue
        ct = r.get('chi_tiet', '') or ''
        retrace = (r.get('retrace') or '').strip() or _from_ct(ct, r'hồi\s+(\d+)%')
        leg = (r.get('leg_gia') or '').strip() or _from_ct(ct, r'leg\s+([\d.]+)\s*giá')
        pha = _from_ct(ct, r'phá\s+([\d.]+)')
        out.append(dict(
            dt=dtp(r['ngay_gio']), kb=r['nhanh'].strip(), huong=r['huong'].strip(),
            entry=r.get('entry', ''), sl=r.get('SL', ''), tp=r.get('TP', ''),
            rr=rr, kq=kq, r=(rr if kq == 'WIN' else -1.0),
            vsa=r.get('VSA', ''), climax=r.get('climax', ''),
            covung=r.get('hop_luu', r.get('co_vung', '')), grade=r.get('grade', ''),
            retrace=retrace, leg=leg, pha=pha,
            block=r.get('tp_vuong_vung', ''), ct=ct,
            ketthuc=r.get('ket_thuc_luc', ''), src=src))
    return sorted(out, key=lambda x: x['dt'])


COLS = ['stt', 'ngay_gio', 'gio_VN', 'ban', 'kich_ban', 'huong', 'entry', 'SL', 'TP',
        'RR', 'KQ', 'R', 'giu_bao_lau', 'VSA', 'climax', 'hop_luu', 'grade',
        'gia_pha', 'retrace_%', 'leg_gia', 'tp_vuong_vung', 'ket_thuc_luc', 'chi_tiet',
        'CHAM_1_5', 'LOI_GI', 'CO_CHE_NGHI_NGO', 'GHI_CHU']


def held(x):
    """Giu lenh bao lau (phut) — doc tu ket_thuc_luc."""
    try:
        d = dtp(x['ketthuc']) - x['dt']
    except Exception:
        return ''
    m = int(d.total_seconds() // 60)
    return f'{m//60}h{m%60:02d}' if m >= 60 else f'{m}p'


def write(path, rows, note_lines):
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        for ln in note_lines:
            f.write('# ' + ln + '\n')
        w = csv.writer(f)
        w.writerow(COLS)
        for i, x in enumerate(rows, 1):
            w.writerow([i, x['dt'].strftime('%Y-%m-%d %H:%M'),
                        (x['dt'] + timedelta(hours=7)).strftime('%H:%M'),
                        x['src'], x['kb'], x['huong'], x['entry'], x['sl'], x['tp'],
                        x['rr'], x['kq'], f"{x['r']:+.1f}", held(x), x['vsa'],
                        x['climax'], x['covung'], x['grade'], x['pha'], x['retrace'],
                        x['leg'], x['block'], x['ketthuc'], x['ct'], '', '', '', ''])
    print(f'  {os.path.basename(path):46} {len(rows):3} dong')


def stat(rs):
    if not rs:
        return 'n=0'
    n = len(rs)
    w = sum(1 for x in rs if x['kq'] == 'WIN')
    s = sum(x['r'] for x in rs)
    return f'n={n} WR={100*w/n:.1f}% tong={s:+.1f}R EV={s/n:+.3f}'


A, B = norm(load_v5(), 'v5-RunnerSignal'), norm(load_v7(), 'v7-WyckoffRunner')
lo, hi = max(A[0]['dt'], B[0]['dt']), min(A[-1]['dt'], B[-1]['dt'])
Aw = [x for x in A if lo <= x['dt'] <= hi]
Bw = [x for x in B if lo <= x['dt'] <= hi]
a_cbr = [x for x in Aw if x['kb'] == 'CBR']
b_cbr = [x for x in Bw if x['kb'] == 'CBR']
kb_key = {(x['dt'], x['huong']) for x in b_cbr}

print(f'Cua so giao nhau: {lo} -> {hi}')
print('Dang ghi:')

W = '⚠ Cot CHAM_1_5 / LOI_GI / CO_CHE_NGHI_NGO / GHI_CHU de TRONG cho ban dien.'
G = ('⚠ QUY TAC VANG: tim CO CHE lap lai duoc, KHONG phai "le nay dang le thang". '
     'Moi quy tac rut ra tu day chi la GIA THUYET, phai kiem tren du lieu thang 8 '
     'moi duoc sua cau hinh dong bang.')

# 1 — 19 lenh v7 DA VAO ma THUA  (uu tien cao nhat)
r1 = [x for x in b_cbr if x['kq'] == 'LOSS']
write(os.path.join(OUT, '1-v7-CBR-DA-VAO-ma-THUA.csv'), r1, [
    'FILE 1/5 — UU TIEN CAO NHAT. v7 WyckoffRunner, kich ban CBR, cac lenh DA VAO va THUA.',
    'Day la TIEN THAT se mat. Tim co che o day => TANG EV, khong phai them lenh.',
    f'Thong ke nhom nay: {stat(r1)}', W, G])

# 2 — 89 lenh v5 co ma v7 KHONG bat
r2 = [x for x in a_cbr if (x['dt'], x['huong']) not in kb_key]
write(os.path.join(OUT, '2-v7-CBR-BO-SOT-(v5-co-v7-khong).csv'), r2, [
    'FILE 2/5 — nhung lenh v5 CBR bat ma v7 KHONG bat ("lenh sot" cua v7).',
    f'Thong ke ca nhom: {stat(r2)}  <= v7 loai nhom nay la DUNG (EV am).',
    'BAY: trong nhom co lenh WIN. Chi ra chung khi DA BIET ket qua la con so AO.',
    'Chi ghi nhan neu ban tim duoc DAU HIEU NHAN DIEN TRUOC KHI VAO LENH.', W, G])

# 3 — v7 CBR toan bo 34 lenh
write(os.path.join(OUT, '3-v7-CBR-toan-bo.csv'), b_cbr, [
    'FILE 3/5 — TOAN BO lenh CBR cua v7 trong cua so giao nhau (ca WIN va LOSS).',
    f'Thong ke: {stat(b_cbr)}', W, G])

# 4 — QUAY_DAU (giong het o 2 ban)
r4 = [x for x in Bw if x['kb'] == 'QUAY_DAU']
write(os.path.join(OUT, '4-QUAY_DAU-(v5-va-v7-GIONG-HET).csv'), r4, [
    'FILE 4/5 — kich ban QUAY DAU. v5 va v7 GIONG HET NHAU (cung 28 lenh, cung +12.0R):',
    'v6/v7 chi nang cap CBR, khong sua QUAY DAU.',
    f'Thong ke: {stat(r4)}',
    'LUU Y: kich ban nay dang TAT trong DLL — AUDIT_V7 phan quyet FAIL (p=0.072,',
    'chet sau Bonferroni, LONG EV chi +0.154R, OOS n=9 EV -0.167R).',
    'Review de hieu vi sao no yeu, KHONG phai de bat lai.', W, G])

# 5 — v5 CBR toan bo
write(os.path.join(OUT, '5-v5-CBR-toan-bo.csv'), a_cbr, [
    'FILE 5/5 — TOAN BO lenh CBR cua v5 RunnerSignal (de doi chieu).',
    f'Thong ke: {stat(a_cbr)}',
    'v5 dung RR 3.0, v7 dung RR 4.0 — khong phai tao-voi-tao.', W, G])

print()
print('Thong ke tong:')
print(f'  v7 CBR toan bo   : {stat(b_cbr)}')
print(f'  v7 CBR THUA      : {stat(r1)}')
print(f'  v7 bo sot (89)   : {stat(r2)}')
print(f'  QUAY_DAU         : {stat(r4)}')
print(f'  v5 CBR toan bo   : {stat(a_cbr)}')
