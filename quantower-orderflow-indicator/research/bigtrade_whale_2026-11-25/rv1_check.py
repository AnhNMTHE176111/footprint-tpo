"""Fable kiểm độc lập vòng 1 (không import bw1_*): chạy bw2_ref trên nhật ký gốc, đếm vòng theo ngày giao dịch / phiên.
python rv1_check.py  -> out_rv1_check.txt"""
import os, sys, statistics as S
from datetime import datetime, timedelta, date
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bw2_ref as R
LOGDIR = r'C:\Users\anhla\AppData\Roaming\OrderFlowBubbles\bigtrade-log'
LOGS = [('GCX_M1', '_GC_XCEC_Time_1Minute.csv', 1, 0.1), ('GCX_M5', '_GC_XCEC_Time_5Minute.csv', 5, 0.1),
        ('NQ_M1', '_NQZ26_XCME_Time_1Minute.csv', 1, 0.25), ('NQ_M15', '_NQZ26_XCME_Time_15Minute.csv', 15, 0.25),
        ('GCZ_M1', '_GCZ26_XCEC_Time_1Minute.csv', 1, 0.1)]
SEG = {'GCX': [('chon', date(2026, 9, 1), date(2026, 9, 11)), ('kiem', date(2026, 9, 14), date(2026, 9, 23))],
       'NQ': [('chon', date(2026, 10, 26), date(2026, 10, 28)), ('kiem', date(2026, 10, 29), date(2026, 11, 2))],
       'GCZ': [('ngoai', date(2026, 11, 9), date(2026, 11, 19))]}
DST_END = datetime(2026, 11, 1, 7)


def ct(t): return t + timedelta(hours=-5 if t < DST_END else -6)
def tday(t): return (ct(t) + timedelta(hours=7)).date()
def ses(t):
    c = ct(t); h = c.hour + c.minute / 60
    return 'A' if (h >= 17 or h < 2) else ('Au' if h < 8.5 else 'My')


out = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)

for key, fn, m, tick in LOGS:
    by = R.load_btlog(os.path.join(LOGDIR, fn))
    bars = [R.EPOCH + timedelta(microseconds=(tt - R.UNIX_TICKS) // 10) for tt in sorted(by)]
    daymin = defaultdict(int)
    for t in bars: daymin[tday(t)] += m
    for (D, Rr, W) in [(5, 8, 1380), (5, 6, 1380), (5, 10, 1380), (5, 8, 690), (3, 8, 1380), (10, 8, 1380)]:
        marks, trace, st = R.run(bars, m, tick, by, D=D, R=Rr, W=W, last_running=False)
        first = next((t for t, thr, n in trace if thr is not None), None)
        cnt = defaultdict(int); cs = defaultdict(int); thr_by = defaultdict(list)
        for mk in marks: cnt[tday(mk[0])] += 1; cs[(tday(mk[0]), ses(mk[0]))] += 1
        for t, thr, n in trace:
            if thr is not None: thr_by[(tday(t), ses(t))].append(thr)
        # ngày có ngưỡng từ nến đầu
        has_all = defaultdict(lambda: True)
        for t, thr, n in trace:
            if thr is None: has_all[tday(t)] = False
        P(f'== {key} D={D} R={Rr} W={W}: {len(marks)} vong; nguong dau tien luc {first}; vong nho nhat {min((x[2] for x in marks), default=None)}')
        for name, a, b in SEG[key.split("_")[0]]:
            lim = 1170 if key != 'GCZ_M1' else 400
            days = [d for d in sorted(daymin) if a <= d <= b and daymin[d] >= lim and has_all[d]]
            if not days: P(f'   {name}: khong co ngay danh gia'); continue
            v = [cnt[d] for d in days]
            sm = {s: S.median([cs[(d, s)] for d in days]) for s in ('A', 'Au', 'My')}
            tm = {s: S.median([x for d in days for x in thr_by[(d, s)]] or [float("nan")]) for s in ('A', 'Au', 'My')}
            P(f'   {name}: {len(days)} ngay; vong/ngay TV {S.median(v)} TB {sum(v)/len(v):.2f} ({min(v)}-{max(v)}) {v}; phien A/Au/My {sm["A"]}/{sm["Au"]}/{sm["My"]}; nguong TV A/Au/My {tm["A"]}/{tm["Au"]}/{tm["My"]}')
        if (D, Rr, W) == (5, 8, 1380):
            # mọi ngày có ngưỡng: trung bình dài hạn
            alld = [d for d in sorted(daymin) if daymin[d] >= (1170 if key != 'GCZ_M1' else 400) and has_all[d]]
            v = [cnt[d] for d in alld]
            if v: P(f'   moi ngay danh gia ({len(v)}): TB {sum(v)/len(v):.2f}, TV {S.median(v)}, max {max(v)}; tong phut nen co nguong {st["co"]*m}, vong / 1380 phut nen = {len(marks)/(st["co"]*m/1380):.2f}')
            # lệnh lớn nhất mỗi ngày đủ có nổ không; lệnh lớn nhất mỗi phiên
            big = defaultdict(int); bigs = defaultdict(int); thr_at = {}
            for t, thr, n in trace: thr_at[t] = thr
            hit = 0; tot = 0; miss = []
            mx = {}
            for t in bars:
                if thr_at.get(t) is None: continue
                c = R.cells_of(by[R.bar_ticks(t)], tick); mm = max(x[1] for x in c)
                k = (tday(t), ses(t))
                if k not in mx or mm > mx[k][0]: mx[k] = (mm, thr_at[t], t)
            for k, (mm, th, t) in sorted(mx.items()):
                if k[0] not in alld: continue
                tot += 1
                if mm > th: hit += 1
                else: miss.append(f'{k[0].day}/{k[0].month} {k[1]} lon nhat {mm:.0f} nguong {th}')
            P(f'   lenh lon nhat tung phien (moi phien, khong loc 5x): no {hit}/{tot}; sot: ' + '; '.join(miss))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_rv1_check.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
