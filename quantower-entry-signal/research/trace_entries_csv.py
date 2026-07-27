#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xuat CSV chi tiet TUNG lenh (win/loss) de user SOI CACH ENTRY. Chi 1 thang.
2 file (cung 1 lan chay, cung harness):
  trades_1thang_1.5R.csv  = BAN A  (KB1 pha&hoi + KB2 cham&dao, cum>=2, TP 1.5R)  -- ban dang chay live
  trades_1thang_3R.csv    = BAN B Runner (CHI KB1 momentum + giu vung, cum>=2, TP 3R)
Ban B la TAP CON KB1 cua ban A, chi khac muc tieu (1.5R -> 3R) -> so sanh truc tiep cung entry.

COT then chot de danh gia ENTRY:
  pha_gia    : cu pha di bao nhieu gia (do manh nhip pha)                      (KB1)
  pha_rau%   : rau tu choi tai DINH nhip pha (vd lenh1 63% = bi ban manh)      (KB1)
  nen_hoi    : so nen tu nen pha den nen entry (nhip hoi dai/ngan)             (KB1)
  retrace%   : nhip hoi sau bao nhieu % so voi vung (<=100 = GIU goc pha)      (KB1)
  giu_vung   : GIU (low>=vung) hay THUNG (choc qua = bat dao roi)              (KB1)
  VSA/than%/delta/cpos : chat luong NEN entry
  MFE_R      : gia chay xa nhat (R) TRUOC KHI cham SL -- bo qua TP.
               >>> tra loi thang "3R co kha thi khong": MFE_R>=3 thi 3R moi an duoc.
  MAE_R      : thut sau nhat (R) truoc khi dong (winner chiu drawdown bao nhieu)
"""
import sys, csv, statistics as st
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
DIRR = "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research/"
CONFL_TOL = 7

# ---- cau hinh SHIPPED (khop indicator dang chay) ----
em.SL_MIN_T = 40; em.SL_MAX_T = 60; em.RR = 1.5; em.NEXTZONE_MINR = 2.0; em.RETEST_HOLD_T = 0


def cluster_of(pool, t, zp):
    seen = set()
    for z in pool:
        if z['ready'] <= t <= z['expire'] and abs(z['price'] - zp) / TICK <= CONFL_TOL:
            seen.add(round(z['price'] / TICK))
    return len(seen)


def outcome(B, i, side, sl, tp):
    """Khop y het research.hit_target: cung nen cham ca 2 -> SL (bi quan). Tra (KQ, so_nen)."""
    for j in range(i + 1, len(B)):
        b = B[j]
        s = (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl)
        t = (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp)
        if s: return 'SL', j - i
        if t: return 'TP', j - i
    return 'open', len(B) - 1 - i


HORIZON = 480   # ~8h M1: gioi han cua so do MFE trong phien (khong tinh trend nhieu ngay)


def ceiling_mfe(B, i, side, entry, sl, rdollar):
    """MFE (R) toi da TRUOC khi cham SL (bo qua TP), trong <=HORIZON nen = tran chay that su."""
    mfe = 0.0
    for j in range(i + 1, min(len(B), i + 1 + HORIZON)):
        b = B[j]
        if side == 'LONG':
            mfe = max(mfe, (b['hi'] - entry) / rdollar)
            if b['lo'] <= sl: break
        else:
            mfe = max(mfe, (entry - b['lo']) / rdollar)
            if b['hi'] >= sl: break
    return mfe


def mae_to_close(B, i, side, entry, sl, tp, rdollar):
    """MAE (R) thut sau nhat truoc khi dong (cham SL hoac TP)."""
    mae = 0.0
    for j in range(i + 1, len(B)):
        b = B[j]
        if side == 'LONG':
            mae = max(mae, (entry - b['lo']) / rdollar)
            if b['lo'] <= sl or b['hi'] >= tp: break
        else:
            mae = max(mae, (b['hi'] - entry) / rdollar)
            if b['hi'] >= sl or b['lo'] <= tp: break
    return mae


def kb1_entry_shape(B, s):
    """Dung lai cu PHA + nhip HOI cho tin hieu KB1. Tra dict cac cot (blank neu KB2)."""
    i = s['i']; side = s['side']
    zp = s.get('zp_break', float(s['zone'].split()[-1]))   # vung THUC bi pha (khong phai nhan hop luu)
    bk = s.get('brk_bar', -999)
    if not str(s['scen']).startswith('1') or bk is None or bk <= 0 or bk >= i:
        return dict(pha_gia='', pha_rau='', nen_hoi='', retrace='', giu='')
    seg = B[bk:i]  # tu nen pha den truoc nen entry (nen entry = nhip hoi)
    if not seg:
        seg = [B[bk]]
    if side == 'LONG':
        pk = max(seg, key=lambda x: x['hi']); peak = pk['hi']; retest = B[i]['lo']
        pha_gia = (peak - zp)
        rau = pk['uw'] / pk['rng'] * 100 if pk['rng'] > 0 else 0.0
        retrace = (peak - retest) / (peak - zp) * 100 if peak > zp else 0.0
        giu = 'GIU' if retest >= zp - 1e-9 else 'THUNG'
    else:
        pk = min(seg, key=lambda x: x['lo']); trough = pk['lo']; retest = B[i]['hi']
        pha_gia = (zp - trough)
        rau = pk['lw'] / pk['rng'] * 100 if pk['rng'] > 0 else 0.0
        retrace = (retest - trough) / (zp - trough) * 100 if zp > trough else 0.0
        giu = 'GIU' if retest <= zp + 1e-9 else 'THUNG'
    return dict(pha_gia=f"{pha_gia:.1f}", pha_rau=f"{rau:.0f}", nen_hoi=str(i - bk),
                retrace=f"{retrace:.0f}", giu=giu)


HEAD = ['ngay_gio', 'huong', 'kich_ban', 'vung', 'hop_luu',
        'pha_gia', 'pha_rau%', 'nen_hoi', 'retrace%', 'giu_vung',
        'entry', 'VSA', 'than%', 'delta', 'cpos',
        'SL', 'risk_gia', 'TP', 'KQ', 'R', 'MFE_R', 'MAE_R', 'nen_KQ', 'mo_ta']


def row_of(B, s, rr):
    i = s['i']; side = s['side']; r = s['risk_t'] * TICK
    tp = s['entry'] + rr * r if side == 'LONG' else s['entry'] - rr * r
    kq, nkq = outcome(B, i, side, s['sl'], tp)
    Rr = rr if kq == 'TP' else (-1.0 if kq == 'SL' else 0.0)
    mfe = ceiling_mfe(B, i, side, s['entry'], s['sl'], r)
    mae = mae_to_close(B, i, side, s['entry'], s['sl'], tp, r)
    sh = kb1_entry_shape(B, s)
    b = B[i]
    kqvn = 'WIN' if kq == 'TP' else ('LOSS' if kq == 'SL' else 'open')
    return [s['dt'].strftime('%Y-%m-%d %H:%M'), side,
            'KB1 pha&hoi' if str(s['scen']).startswith('1') else 'KB2 cham&dao',
            s['zone'], s.get('confl', 1),
            sh['pha_gia'], sh['pha_rau'], sh['nen_hoi'], sh['retrace'], sh['giu'],
            f"{s['entry']:.1f}", f"{s['vsa']:.2f}", f"{b['brat']*100:.0f}", f"{b['delta']:+.0f}",
            f"{b['cpos']:.2f}", f"{s['sl']:.1f}", f"{s['risk_t']/10:.1f}", f"{tp:.1f}",
            kqvn, f"{Rr:+.1f}", f"{mfe:.2f}", f"{mae:.2f}", nkq, s['why']]


def write_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(HEAD); w.writerows(rows)


def brief(tag, rows, rr):
    win = sum(1 for r in rows if r[HEAD.index('KQ')] == 'WIN')
    loss = sum(1 for r in rows if r[HEAD.index('KQ')] == 'LOSS')
    op = sum(1 for r in rows if r[HEAD.index('KQ')] == 'open')
    closed = win + loss
    totR = sum(float(r[HEAD.index('R')]) for r in rows)
    mfes = [float(r[HEAD.index('MFE_R')]) for r in rows]
    reach3 = sum(1 for m in mfes if m >= 3.0)
    reach15 = sum(1 for m in mfes if m >= 1.5)
    print(f"\n{tag}: {len(rows)} lenh | WIN {win} LOSS {loss} open {op} | "
          f"WR {win/closed*100 if closed else 0:.0f}% | tong {totR:+.1f}R @ {rr}R")
    print(f"   MFE_R (tran chay that): trung vi {st.median(mfes):.2f}R | "
          f"cham >=1.5R: {reach15}/{len(rows)} | cham >=3R: {reach3}/{len(rows)}")
    # kiem nhat quan: WIN nao dong SAU cua so do MFE -> MFE co the < R (canh bao)
    bad = [r for r in rows if r[HEAD.index('KQ')] == 'WIN' and int(r[HEAD.index('nen_KQ')]) > HORIZON]
    thung = [r for r in rows if r[HEAD.index('giu_vung')] == 'THUNG']
    if bad: print(f"   !! {len(bad)} WIN dong sau {HORIZON} nen (MFE co the thieu)")
    if thung: print(f"   !! {len(thung)} dong KB1 con THUNG (filter le?) — CAN xem")


# ================= CHAY =================
B = em.load_m1(); pool = em.build_zones(B)
raw = em.run(B, pool)
for s in raw:
    s['cluster'] = cluster_of(pool, s['dt'], float(s['zone'].split()[-1]))
sig = em.dedup(raw)
for s in sig:
    s.setdefault('cluster', 1)
sig = [s for s in sig if s['cluster'] >= 2]          # GATE cum>=2 (shipped ca 2 ban)

# --- BAN A: KB1+KB2, TP 1.5R ---
rowsA = [row_of(B, s, 1.5) for s in sorted(sig, key=lambda x: x['dt'])]
write_csv(DIRR + "trades_1thang_1.5R.csv", rowsA)

# --- BAN B Runner: CHI KB1 momentum, TP 3R ---
sigB = [s for s in sig if str(s['scen']).startswith('1')]
rowsB = [row_of(B, s, 3.0) for s in sorted(sigB, key=lambda x: x['dt'])]
write_csv(DIRR + "trades_1thang_3R.csv", rowsB)

print("=" * 78)
print("Xuat 2 file CSV (1 thang, 6/26 -> 7/25/2026):")
print("  " + DIRR + "trades_1thang_1.5R.csv   (BAN A: KB1+KB2, TP 1.5R)")
print("  " + DIRR + "trades_1thang_3R.csv     (BAN B: chi KB1 momentum, TP 3R)")
brief("BAN A @1.5R", rowsA, 1.5)
brief("BAN B @3R  ", rowsB, 3.0)
print("\n(MFE_R = gia chay xa nhat truoc khi cham SL, BO QUA TP -> tran that su cua tung lenh.")
print(" 1 lenh WIN o ban A (1.5R) van co the LOSS o ban B (3R) neu MFE_R < 3.)")
print("=" * 78)
