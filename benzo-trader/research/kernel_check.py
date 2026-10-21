"""Sinh report/KERNEL-CHECK.md: so phien, volume, 3 ngay mau, cho noi file 2 nam, thoi gian chay.
Chay: python kernel_check.py [--full2y]   (--full2y: doc ca file per-level 2 nam 583 MB de do thoi gian)."""
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
DD = os.path.join(ROOT, 'data-export', 'data-footprint')
D90 = os.path.join(DD, 'fp_GCZ26_XCEC_Time_20260723-20261021_90d')
D2Y = os.path.join(DD, 'fp_GC_XCEC_Time_20240801-20260819_748d9h')
L = []
T = {}
t0 = time.time()
df = K.load_bars(D90 + '_bars.csv')
T['load_bars 90d'] = time.time() - t0
t = time.time()
prof = K.build_profiles(df, D90 + '.csv')
T['build_profiles (per-level 1,5 trieu dong)'] = time.time() - t
t = time.time()
ctx = K._Ctx(df, prof)
zc = K.zone_columns(df, prof, ctx)
T['zone_columns'] = time.time() - t
t = time.time()
md = K.mode_frame(df, zc)
T['mode_frame (M5 + che do)'] = time.time() - t
t = time.time()
zz = K.zigzag(df)
T['zigzag 2 gia'] = time.time() - t
T['TONG pipeline 90d'] = time.time() - t0
st = K.session_table(df)
L += ['# KERNEL-CHECK (kernel.py, sinh boi kernel_check.py)', '',
      'File: `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (GCZ26, mot hop dong). Gio trong file = UTC; cot VN = UTC+7.', '',
      '## 1. So lieu co ban (file 90d)', '',
      '- So nen M1: **%d**; so phien (tach khi trong > 30 phut): **%d** (phien dau %d nen = du lieu bat dau giua phien; phien cuoi %d nen = dang chay)'
      % (len(df), len(st), st['n'].iloc[0], st['n'].iloc[-1]),
      '- Trung vi volume/phien: **%d** hop dong (plan ghi 133.471); trung vi nen/phien: %d' % (st['volume'].median(), st['n'].median()),
      '- Phien `thin` (volume < 20%% trung vi): **%d** -> %s. Du lieu tuan dau (07-23..07-28) rat mong (volume 2.672..21.081 so voi trung vi 133.471) nen profile/VA cua cac phien do khong dang tin.'
      % (st['thin'].sum(), ', '.join(st.loc[st['thin'], 'session_id'])),
      '- Phien dinh cho noi: %d (file 90d la mot hop dong nen = 0)' % st['splice'].sum(),
      '- Cac khoang trong > 30 phut: 61-62 phut (nghi 21:00-22:00 UTC) x49; cuoi tuan ~2941 phut x12; 3065 phut x1 (dau file, T6->T2); le Labor Day 2026-09-07 trong 211 phut (phien bi cat doi: phien 09-07 chi 1.220 nen); 72 phut ngay dau file.',
      '- Profile dung %s: %d phien (full), %d phien co cua so Au.' % ('tu per-level (that)' if not prof.approx else 'XAP XI tu nen', len(prof.full), len(prof.eu)),
      '- Che do M1 (phan bo): ' + ', '.join('%s=%d' % (k, v) for k, v in md['mode'].value_counts().items()),
      '  (`NA` chiem da so vi truoc 19:00 VN chua co band VA Au/IB.)', '',
      '## 2. Ba ngay mau tai 19:00 VN (nen dau tien co sm = 840, tuc 12:00 UTC)', '',
      'VA Au chot dung luc nay (cua so 12:30-19:00 VN). IB 19:20-20:20 chi chot sau 20:20 nen o day in gia tri CUOI kem gio chot. VWAP tuan/ngay = cong don den nen 19:00 (typical price x volume).', '']
vw = K.vwap_series(df)
for sid in ('2026-08-12', '2026-09-10', '2026-10-14'):
    sno = ctx.sid2no[sid]
    a, b = int(st['start_pos'].loc[sno]), int(st['end_pos'].loc[sno])
    p = a + int(np.flatnonzero(df['sm'].to_numpy()[a:b + 1] >= 840)[0])
    z = K.zones_for_session(df, sno, prof, as_of=p, ctx=ctx)
    zf = K.zones_for_session(df, sno, prof, ctx=ctx)
    L += ['### Phien %s (19:00 VN = %s UTC, pos %d)' % (sid, str(df['t_utc'].iloc[p])[:16], p), '',
          '| muc | POC | VAH | VAL |', '|---|---|---|---|',
          '| VA Au hom nay | %.1f | %.1f | %.1f |' % (z['va_eu']['poc'], z['va_eu']['vah'], z['va_eu']['val']),
          '| VA hom qua (%s) | %.1f | %.1f | %.1f |' % (z['yday']['session_id'], z['yday']['poc'], z['yday']['vah'], z['yday']['val']),
          '', '- IB 19:20-20:20 VN: cao **%.1f**, thap **%.1f** (chot luc %s UTC; luc 19:00 chua co => `as_of` tra None: %s)' %
          (zf['ib']['high'], zf['ib']['low'], str(df['t_utc'].iloc[zf['ib']['ready_pos']])[:16], z['ib'] is None),
          '- VWAP tuan **%.1f**, VWAP ngay **%.1f**, close nen 19:00 = %.1f' % (vw['vwap_w'].iloc[p], vw['vwap_d'].iloc[p], df['close'].iloc[p]),
          '- HVN ngay (tu profile hom qua): %s | LVN ngay: %s' % (', '.join('%.1f (x%.1f)' % x for x in z['hvn_day']) or 'khong co (khong du cong x2,5)', ', '.join('%.1f' % x[0] for x in z['lvn_day']) or 'khong co'),
          '- HVN tuan (gop 3 tuan da dong, %d phien): %s' % (z['hvn_week']['n_sessions'], ', '.join('%.1f (x%.1f)' % x for x in z['hvn_week']['hvn']) or 'khong co'),
          '- POC tran (chua bi cham) tai 19:00: %s' % (', '.join('%.1f (phien %s)' % (x['price'], x['session_id']) for x in z['naked']) or 'khong co'), '']
L += ['## 3. File 2 nam `fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv`', '']
p2 = D2Y + '_bars.csv'
if os.path.exists(p2):
    t = time.time()
    d2 = K.load_bars(p2)
    T['load_bars 2 nam'] = time.time() - t
    s2 = K.session_table(d2)
    jumps = d2[d2['splice_jump']]
    L += ['- So nen M1: %d; so phien: **%d**; trung vi volume/phien: %d' % (len(d2), len(s2), s2['volume'].median()),
          '- Cho noi hop dong phat hien (khoang nghi 30-150 phut va |open - close truoc| >= 20 gia): **%d**' % len(jumps),
          '- Phien dinh cho noi (+-2 phien quanh moi cho noi): **%d** phien bi loai, con **%d** phien sach (README cu ghi 529 phien / 474 sach)' % (s2['splice'].sum(), (~s2['splice']).sum()),
          '- Phien `thin` trong file 2 nam: %d' % s2['thin'].sum(), '',
          '| gio UTC (nen sau cho noi) | close truoc | open sau | nhay |', '|---|---|---|---|']
    for i in jumps.index:
        L.append('| %s | %.1f | %.1f | %+.1f |' % (str(d2['t_utc'].iloc[i])[:16], d2['close'].iloc[i - 1], d2['open'].iloc[i], d2['open'].iloc[i] - d2['close'].iloc[i - 1]))
    gp = d2['t_utc'].diff().dt.total_seconds() / 60
    jj = (d2['open'] - d2['close'].shift(1)).abs()
    near = ((gp >= 30) & (gp <= 150) & (jj >= 8) & (jj < K.CONST['splice_jump'])).sum()
    L += ['', '- Co them **%d** lan nhay 8-20 gia dung trong khoang nghi (2026-02 -> 2026-07, thi truong bien dong manh). KHONG coi la cho noi (nguong plan = 20 gia); nguong thap hon se ra ~%d cho noi, nhieu kha nang gom ca gap that. Tong 8 cho noi ro rang (+-24..+61 gia). README cu ghi 11 cho noi - khong tai lap duoc voi nguong 20.' % (near, near + len(jumps))]
    t = time.time()
    pr2 = K.build_profiles(d2)
    zc2 = K.zone_columns(d2, pr2)
    m2 = K.mode_frame(d2, zc2)
    T['pipeline 2 nam voi profile XAP XI (tu nen)'] = time.time() - t
    L += ['', '- Pipeline 2 nam (profile xap xi tu nen, chi de kiem toc do/do ben, KHONG dung ket luan): %.1f giay; che do M1: %s'
          % (T['pipeline 2 nam voi profile XAP XI (tu nen)'], ', '.join('%s=%d' % (k, v) for k, v in m2['mode'].value_counts().items()))]
    if os.path.exists(D2Y + '.csv') and '--full2y' in sys.argv:
        t = time.time()
        pr3 = K.build_profiles(d2, D2Y + '.csv')
        T['build_profiles 2 nam per-level (583 MB, doc chunk)'] = time.time() - t
        L += ['- build_profiles tu per-level 2 nam (doc chunk 2 trieu dong): %.1f giay, %d phien co profile'
              % (T['build_profiles 2 nam per-level (583 MB, doc chunk)'], len(pr3.full))]
else:
    L += ['(khong thay file 2 nam, bo qua)']
L += ['', '## 4. Thoi gian chay (may nay)', '', '| buoc | giay |', '|---|---|'] + ['| %s | %.2f |' % (k, v) for k, v in T.items()]
L += ['', '## 5. Gia dinh va quy uoc (hang so nam o `CONST` dau kernel.py)', '',
      '1. **VWAP = typical price (H+L+C)/3 x volume**, cong don; gom nen hien tai (nen da dong). Giong `ProfileEngine.VwapAt`, khong dung close x volume.',
      '2. **VWAP tuan neo phien dau tien sau khoang trong > 30 gio**; VWAP ngay reset moi phien CME (khoang trong > 30 phut).',
      '3. **datetime = gio MO nen M1.** M5 chi "da dong" khi `t5_end <= gio mo nen M1` dang xet, nen nen M1 thu 5 cua mot M5 chua thay M5 cua chinh no.',
      '4. **Profile**: hang = 2 tick (0,2 gia), snap `round(gia/0,2)` (lam tron banker giong C#); VA chay tren cac hang DANG CO (khong lap hang trong, giong ProfileEngine.ValueArea).',
      '5. **FindHvn/FindLvn port 1:1** (lam muot +-5 hang, gop dinh theo 8% do rong kep 20..120 tick, cong ti le 2,5, toi da 3 HVN / 2 LVN). KHAC `research/hap-thu-tai-vung.py` o find_lvn (script do dung nguong cach 2 gia co dinh; kernel theo ProfileEngine).',
      '6. **Phien hom qua** = phien truoc gan nhat co >= 300 nen M1 (bo manh vun nghi le) va khong co cho noi chen giua. **HVN tuan** = gop cac phien thuoc 3 tuan CME da dong (tuan = khoang trong > 30 gio); neu co cho noi trong cua so chi lay phan SAU cho noi (`partial=True`).',
      '7. **VA Au = nen co `sm` trong [450, 840)** (12:30-19:00 VN), chot tu sm >= 840, can >= 60 nen. **IB = sm [860, 920)** (19:20-20:20), can >= 30 nen, chot tu sm >= 920.',
      '8. **Gio neo My (`us_dst_shift=True`)**: khi My dung gio mua dong (EST), cac moc 05:00/19:00/IB lui +1h theo gio VN de van bam gio mo cua My. File 90d toan mua he nen khong anh huong; muon moc VN co dinh nhu plan thi dat `CONST["us_dst_shift"]=False`. Moc A/EU 12:30 khong doi theo DST.',
      '9. **Che do**: band = VA Au (sau 19:00), chua co thi IB (sau 20:20), truoc 19:00 VN = `NA` (gio A va EU chua co band, plan chua dinh nghia che do cho 2 phase nay). Nen M5 dong NGOAI roi dong LAI TRONG band => ve `BALANCE` (pha hut). `TREND` = >= 2 nen M5 lien tiep ngoai cung phia va nen gan nhat cach canh >= 3 gia; con lai co nen ngoai = `BREAK_*`.',
      '10. **naked POC**: POC (cua VA) cac phien trong 30 phien truoc chua bi gia cham (low <= POC <= high) sau khi phien do ket thuc; voi as_of -> toi da 3 gan nhat.',
      '11. **simulate**: vao o `entry` tai nen `idx`, xet tu nen idx+1; cung nen SL va TP => SL; thoat dung gia SL/TP (khong tinh gap qua phien/cho noi - phai loc `splice` truoc); `one_at_a_time` cho lenh moi khi `idx >= exit_idx` cua lenh truoc.',
      '12. **risk**: san = bien do nen M1 cao nhat 5 nen (gom nen vao), tran 4 gia => None; SL lam tron ra xa theo tick 0,1.',
      '13. **zigzag**: neu day va dinh nam cung mot nen (khong biet thu tu) thi khoi dong chan tiep theo tu nen sau (bao thu). Reset moi phien.',
      '14. Phien `thin` (volume < 20% trung vi) van duoc tra ve nhung co co `thin`; control_sample loai chung. Agent nen tu loc `thin` va `splice` khi do.']
open(os.path.join(HERE, 'report', 'KERNEL-CHECK.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
