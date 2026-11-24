"""Vòng 3, mục 6.3: SỐ CHUẨN (bản chuẩn sa3_ref.py đọc đúng file của Golden trong thư mục tạm) để so với C#.
  - Chấm: tf/fp_{GC,NQ}_m{1,5,15,60}.csv cho nen_moi (sel nms), sel lmax, p 1%, không lân cận.
  - sel all trên GC M5 và NQ M15.
  - Nạp ít ngày: --from đầu ngày giao dịch thứ 8 tính từ cuối (ngày của luật, giờ Chicago), GC M5 và NQ M15, nền mới.
  - Big Trade cuon_A_T240_p1 trên btlog_{NQ_M1, NQ_M15, GC_M5, GC_M30}.csv (--zeromot; chấm chạy cùng theo nền mới). Phải ra lại 3.330 / 864 / 1.913 / 788.
Ghi out_r3_chuan.csv (lệnh, sha1, số nến ngưỡng), out_r3_chuan_ngay.csv (mỗi dòng số chuẩn x ngày UTC), dấu trong thư mục tạm (marks_r3_*.csv).
Chạy: python sa3_numbers.py"""
import os, time, hashlib, numpy as np, pandas as pd
import sa3_ref as RF
from sa3_lib import SCR, rule_day_slot

t0 = time.time()


def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


rows, days = [], []
TICK = {'GC': 0.1, 'NQ': 0.25}
BT_EXPECT = {('NQ', 1): 3330, ('NQ', 15): 864, ('GC', 5): 1913, ('GC', 30): 788}


def add(rid, loai, sym, m, nm, sets, f, bars, mk, st, nonint, lg=None, frm=None):
    out = os.path.join(SCR, f'marks_r3_{rid}.csv'); RF.write_marks(out, mk)
    cmd = f'python sa3_ref.py {f} {m} {TICK[sym]}' + (f' --btlog {lg} --zeromot' if lg else '') + ''.join(' --set ' + s for s in sets) + \
          f' --marks {out}'
    r = dict(dong=rid, loai=loai, ma=sym, khung=m, cau_hinh=nm, tu=frm or '', so_nen=len(bars), cham_do_Bid=sum(x[1] == 'dotS' for x in mk),
             cham_xanh_Ask=sum(x[1] == 'dotB' for x in mk), big_trade=sum(x[1] == 'bt' for x in mk) if lg else None,
             nen_nguong_chinh=st['chinh'], nen_du_phong=st['du_phong'], nen_chua_co=st['chua'], nen_rong=st.get('nen_rong', 0),
             nen_bt_co_nguong=st['bt_co'] if lg else None, nen_bt_chua_co=st['bt_chua'] if lg else None, gia_tri_khong_nguyen=nonint,
             file_footprint=f, sha1_footprint=sha1(f), sha1_bars=sha1(f.replace('.csv', '_bars.csv')), file_btlog=lg or '', sha1_btlog=sha1(lg) if lg else '',
             lenh=cmd, file_dau=out)
    rows.append(r)
    d = pd.DataFrame([(x[0].strftime('%Y-%m-%d'), x[1]) for x in mk], columns=['ngay', 'k'])
    if len(d):
        g = d.groupby(['ngay', 'k']).size().unstack(fill_value=0)
        for k in ('dotS', 'dotB', 'bt'):
            if k not in g: g[k] = 0
        for ngay, x in g.iterrows():
            days.append(dict(dong=rid, ma=sym, khung=m, cau_hinh=nm, ngay_utc=ngay, cham_do_Bid=int(x.dotS), cham_xanh_Ask=int(x.dotB), big_trade=int(x.bt) if lg else None))
    print(rid, r['cham_do_Bid'], r['cham_xanh_Ask'], r['big_trade'], f'({time.time() - t0:.0f} s)', flush=True)


CF = (('nen_moi', []), ('sel_lmax', ['sel=lmax']), ('p1', ['pbp=100']), ('khong_lan_can', ['lc=0']))
for sym in ('GC', 'NQ'):
    for m in (1, 5, 15, 60):
        f = os.path.join(SCR, 'tf', f'fp_{sym}_m{m}.csv')
        bars, nonint = RF.load_csv(f)
        for nm, sets in CF:
            mk, st = RF.run(bars, m, TICK[sym], RF.parse_set(sets + ['bt=0']))
            add(f'{sym}_m{m}_{nm}', 'cham', sym, m, nm, sets + ['bt=0'], f, bars, mk, st, nonint)
        if (sym, m) in (('GC', 5), ('NQ', 15)):
            mk, st = RF.run(bars, m, TICK[sym], RF.parse_set(['sel=all', 'bt=0']))
            add(f'{sym}_m{m}_sel_all', 'cham', sym, m, 'sel_all', ['sel=all', 'bt=0'], f, bars, mk, st, nonint)
            # nạp 8 ngày: đầu ngày giao dịch thứ 8 tính từ cuối (ngày của luật)
            t = pd.DatetimeIndex([b[0] for b in bars])
            day, _, _ = rule_day_slot(t, m, 'ct'); ud = np.unique(day)
            frm = t[day >= ud[-8]][0]
            frm_s = frm.strftime('%Y-%m-%d %H:%M')
            bars8, nonint8 = RF.load_csv(f, from_day=frm_s)
            mk, st = RF.run(bars8, m, TICK[sym], RF.parse_set(['bt=0']))
            # Golden chưa có --from: ghi sẵn cặp file đã cắt (giữ nguyên bar_idx và dòng gốc) để C# chạy thẳng bằng --levels
            f8 = os.path.join(SCR, 'tf', f'fp_{sym}_m{m}_nap8.csv')
            Bd = pd.read_csv(f.replace('.csv', '_bars.csv')); Bd = Bd[pd.to_datetime(Bd.datetime) >= frm]
            Ld = pd.read_csv(f, dtype=str); Ld = Ld[Ld.bar_idx.astype(int).isin(Bd.bar_idx)]
            Bd.to_csv(f8.replace('.csv', '_bars.csv'), index=False); Ld.to_csv(f8, index=False)
            bars8b, _ = RF.load_csv(f8)
            mk8b, _ = RF.run(bars8b, m, TICK[sym], RF.parse_set(['bt=0']))
            assert [(x[0], x[1], x[2]) for x in mk8b] == [(x[0], x[1], x[2]) for x in mk], 'file cắt sẵn cho Golden khác --from'
            add(f'{sym}_m{m}_nap8ngay', 'cham_nap_it', sym, m, 'nen_moi, nạp 8 ngày', ['bt=0'], f8, bars8, mk, st, nonint8, frm=frm_s)
            rows[-1]['lenh'] += f'   (tương đương: python sa3_ref.py {f} {m} {TICK[sym]} --set bt=0 --from "{frm_s}" ...)'
        del bars
for key, m in (('NQ', 1), ('NQ', 15), ('GC', 5), ('GC', 30)):
    f = os.path.join(SCR, 'tf', f'fp_{key}_m{m}.csv'); lg = os.path.join(SCR, f'btlog_{key}_M{m}.csv')
    bars, nonint = RF.load_csv(f, zeromot=True); by = RF.load_btlog(lg)
    sets = ['bt_w=A', 'bt_T=240', 'bt_pbp=100']
    mk, st = RF.run(bars, m, TICK[key], RF.parse_set(sets), by)
    add(f'bt_{key}_M{m}', 'big_trade', key, m, 'chấm nen_moi + Big Trade cuon_A_T240_p1', sets, f, bars, mk, st, nonint, lg=lg)
    rows[-1]['big_trade_vong2'] = BT_EXPECT[(key, m)]; rows[-1]['big_trade_khop_vong2'] = rows[-1]['big_trade'] == BT_EXPECT[(key, m)]
pd.DataFrame(rows).to_csv('out_r3_chuan.csv', index=False)
pd.DataFrame(days).to_csv('out_r3_chuan_ngay.csv', index=False)
print(f'xong ({time.time() - t0:.0f} s)')
