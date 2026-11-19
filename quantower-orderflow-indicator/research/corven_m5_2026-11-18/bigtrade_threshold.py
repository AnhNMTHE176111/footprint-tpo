"""Hieu chinh nguong Big Trade (vong tron mo = MOT lenh don chu dong lon) tu nhat ky song cua indicator.

Nguon: %APPDATA%/OrderFlowBubbles/bigtrade-log/_GCZ26_XCEC_Time_1Minute.csv (cot time_ticks,time_iso,price,mot,buy,sell).
Moi dong = 1 (nen M1, muc gia) co lenh don thuc (mot = MaxOneTradeVolume, chi feed SONG moi cap; lich su luon = 0).
Chi ghi khi nen M1 da dong, nen file chi co cac nen indicator da thay luc dang chay song.

Bang in ra, voi nguong T = 10, 20, 60 (va them vai moc):
  - M1: so (nen, muc gia) co mot >= T chia cho so nen M1 trong nhat ky.
  - M5: moi nen M5 day du (du ca 5 nen M1 :00,:01,..,:04 sau khi lam tron ve boi cua 5 phut) lay MAX theo gia cua mot tren 5 nen M1,
        roi dem so muc gia co max >= T, chia cho so nen M5 day du.
  - phan vi 50 / 99 / 99,9 va gia tri lon nhat cua mot.

Chay: python bigtrade_threshold.py [--log DUONG_DAN.csv] [--since 2026-11-10] [--until 2026-11-20]
"""
import os, sys
import pandas as pd

def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

default_log = os.path.join(os.environ.get('APPDATA', ''), 'OrderFlowBubbles', 'bigtrade-log', '_GCZ26_XCEC_Time_1Minute.csv')
path = arg('--log', default_log)
since = pd.Timestamp(arg('--since', '2026-11-10'), tz='UTC')
until = pd.Timestamp(arg('--until', '2100-01-01'), tz='UTC')

d = pd.read_csv(path)
d['t'] = pd.to_datetime(d['time_iso'], utc=True)
d = d[(d.t >= since) & (d.t < until)].copy()
bars_m1 = d['t'].nunique()
print(f'nhat ky: {path}')
print(f'{since.date()} .. {d.t.max()}: {len(d)} dong (nen, muc gia), {bars_m1} nen M1 co lenh don thuc')

q = d['mot'].quantile([0.5, 0.99, 0.999]).tolist()
print(f'lenh don: trung vi {q[0]:g}, phan vi 99 {q[1]:g}, phan vi 99,9 {q[2]:g}, lon nhat {d["mot"].max():g}')

# M5: gom theo bucket 5 phut; chi giu bucket day du 5 nen M1
d['b5'] = d['t'].dt.floor('5min')
n_per = d.groupby('b5')['t'].nunique()
full = n_per[n_per == 5].index
m5 = d[d.b5.isin(full)].groupby(['b5', 'price'])['mot'].max().reset_index()
bars_m5 = len(full)
print(f'nen M5 day du (du 5 nen M1): {bars_m5} (bo {len(n_per) - bars_m5} bucket thieu nen)')
print()
print(f'{"T":>4} {"M1 / nen M1":>12} {"M5 / nen M5":>12} {"M5 so muc gia":>14} {"M5: 1 lan / ... gio":>20}')
for T in (5, 8, 9, 10, 12, 15, 20, 30, 40, 60, 100):
    r1 = (d['mot'] >= T).sum() / bars_m1
    cnt5 = int((m5['mot'] >= T).sum())
    r5 = cnt5 / bars_m5
    gio = (5.0 / 60) / r5 if r5 > 0 else float('inf')   # trung binh bao nhieu gio moi co 1 vong
    print(f'{T:>4} {r1:>12.3f} {r5:>12.3f} {cnt5:>14d} {gio:>20.1f}')
print()
print('Ghi chu: CORVEN ve khoang 0,96 vong mo moi nen M5 tren chart 18/11 (25 vong / 26 nen).')
