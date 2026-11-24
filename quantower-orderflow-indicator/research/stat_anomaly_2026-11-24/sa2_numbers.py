"""Vòng 2, mục 6.4: bảng SỐ CHUẨN (bản chuẩn sa2_ref.py đọc đúng file của Golden) để vòng sau so với C#.
  - Chấm: tf/fp_{GC,NQ}_m{1,5,15,60}.csv, cấu hình gốc và p = 1%: tổng chấm đỏ (Bid) / xanh (Ask).
  - Big Trade: btlog_{NQ_M1, NQ_M15, GC_M5, GC_M30}.csv với footprint cùng khung, --zeromot, luật A T = 240 p = 1% (= luật thắng mục 6.3),
    chấm cấu hình gốc chạy cùng lúc (như Golden chạy cả hai).
Ghi out_r2_chuan.csv (kèm sha1 từng file đầu vào và lệnh tương đương) và các file dấu trong thư mục tạm (marks_r2_*.csv).
Chạy: python sa2_numbers.py"""
import os, time, hashlib, pandas as pd
import sa2_ref as RF
from sa2_lib import SCR

t0 = time.time()


def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


rows = []
TICK = {'GC': 0.1, 'NQ': 0.25}
for sym in ('GC', 'NQ'):
    for m in (1, 5, 15, 60):
        f = os.path.join(SCR, 'tf', f'fp_{sym}_m{m}.csv')
        bars, nonint = RF.load_csv(f)
        for nm, sets in (('goc', []), ('p1', ['pbp=100'])):
            mk, st = RF.run(bars, m, TICK[sym], RF.parse_set(sets + ['bt=0']))
            out = os.path.join(SCR, f'marks_r2_{sym}_m{m}_{nm}.csv'); RF.write_marks(out, mk)
            rows.append(dict(loai='cham', ma=sym, khung=m, cau_hinh=nm, so_nen=len(bars), cham_do_Bid=sum(x[1] == 'dotS' for x in mk), cham_xanh_Ask=sum(x[1] == 'dotB' for x in mk),
                             big_trade=None, nen_nguong_chinh=st['chinh'], nen_du_phong=st['du_phong'], nen_chua_co=st['chua'], gia_tri_khong_nguyen=nonint,
                             file_footprint=f, sha1_footprint=sha1(f), sha1_bars=sha1(f.replace('.csv', '_bars.csv')), file_btlog='', sha1_btlog='',
                             lenh=f'python sa2_ref.py {f} {m} {TICK[sym]} ' + ' '.join('--set ' + s for s in sets + ['bt=0']) + f' --marks {out}'))
            print(rows[-1]['ma'], m, nm, rows[-1]['cham_do_Bid'], rows[-1]['cham_xanh_Ask'], f'({time.time() - t0:.0f} s)', flush=True)
        del bars
for key, m in (('NQ', 1), ('NQ', 15), ('GC', 5), ('GC', 30)):
    f = os.path.join(SCR, 'tf', f'fp_{key}_m{m}.csv'); lg = os.path.join(SCR, f'btlog_{key}_M{m}.csv')
    bars, nonint = RF.load_csv(f, zeromot=True); by = RF.load_btlog(lg)
    sets = ['bt_w=A', 'bt_T=240', 'bt_pbp=100']
    mk, st = RF.run(bars, m, TICK[key], RF.parse_set(sets), by)
    out = os.path.join(SCR, f'marks_r2_bt_{key}_M{m}.csv'); RF.write_marks(out, mk)
    rows.append(dict(loai='big_trade', ma=key, khung=m, cau_hinh='cham goc + Big Trade cuon_A_T240_p1', so_nen=len(bars), cham_do_Bid=sum(x[1] == 'dotS' for x in mk),
                     cham_xanh_Ask=sum(x[1] == 'dotB' for x in mk), big_trade=sum(x[1] == 'bt' for x in mk), nen_nguong_chinh=st['chinh'], nen_du_phong=st['du_phong'],
                     nen_chua_co=st['chua'], nen_bt_co_nguong=st['bt_co'], nen_bt_chua_co=st['bt_chua'], gia_tri_khong_nguyen=nonint,
                     file_footprint=f, sha1_footprint=sha1(f), sha1_bars=sha1(f.replace('.csv', '_bars.csv')), file_btlog=lg, sha1_btlog=sha1(lg),
                     lenh=f'python sa2_ref.py {f} {m} {TICK[key]} --btlog {lg} --zeromot ' + ' '.join('--set ' + s for s in sets) + f' --marks {out}'))
    print(key, m, 'bt', rows[-1]['big_trade'], f'({time.time() - t0:.0f} s)', flush=True)
pd.DataFrame(rows).to_csv('out_r2_chuan.csv', index=False)
print(f'xong ({time.time() - t0:.0f} s)')
