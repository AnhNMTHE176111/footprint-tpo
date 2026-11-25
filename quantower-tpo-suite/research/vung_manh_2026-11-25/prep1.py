#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prep1.py — dựng bộ đệm MỘT HỢP ĐỒNG (GCZ26 hoặc NQZ26) cho phép đo lại "vùng mạnh" + kiểm chất lượng dữ liệu.

  python prep1.py gc     → GCZ26 2026-07-23 → 2026-11-18 (ghép 3 file, cắt theo mốc giờ, không trùng)
  python prep1.py nq     → NQZ26 2026-08-26 → 2026-11-24

Cùng định dạng pickle với prep.py (m1, m30, lv) nên vm.py / vung_manh.py / final_eval.py chạy nguyên.

NQ: bước giá 0,25. vm.py viết cứng TICK = 0,1 và ROW = 0,2 (2 bước giá). Để KHÔNG sửa bản tham chiếu, giá NQ được
chia SCALE = 2,5 khi lưu (0,25 → 0,1). Mọi ngưỡng của thuật toán tính theo U hoặc theo số bước giá nên phép chia này
cho đúng kết quả C# sẽ ra với tick = 0,25: hàng profile = 2 bước giá = 0,5 điểm; ngưỡng chỗ nối
MinSpliceJumpPrices × 10 × tick = 50 điểm (= 20 sau khi chia). Khi in ra điểm NQ thì nhân lại 2,5.

Bộ đệm lưu ở thư mục tạm (đặt VM_CACHE_DIR để đổi), KHÔNG nằm trong repo.
"""
import os, pickle, sys, tempfile
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
FP = os.path.join(ROOT, 'data-export', 'data-footprint')
CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())

CFG = {
    # t_min = phiên đầu tiên hợp đồng đã là hợp đồng chính (khối lượng đủ dày); trước đó chỉ kiểm chất lượng, không đo.
    # File fp_GCZ26_..._20261108-20261118_9d16h là nến M5 (276 nến/phiên), không ghép được vào chuỗi M1 để chấm đường đi → không dùng.
    'gc': dict(scale=1.0, tick=0.1, t_min='2026-07-28 21:30:00', src=[
        ('fp_GCZ26_XCEC_Time_20260723-20261021_90d', None, '2026-10-21 00:00:00'),
        ('fp_GCZ26_XCEC_Time_20260811-20261109_90d', '2026-10-21 00:00:00', None)]),
    'nq': dict(scale=2.5, tick=0.25, t_min='2026-09-13 21:30:00', src=[
        ('fp_NQZ26_XCME_Time_20260826-20261124_90d', None, None)]),
    # file 293 ngày (xuất 2026-11-25): cả phần NQZ26 còn là hợp đồng phụ (tháng 2–9) để kiểm chất lượng; t_min đặt lại sau khi xem bảng.
    'nqy': dict(scale=2.5, tick=0.25, t_min=os.environ.get('NQY_TMIN', '2026-02-01 00:00:00'), src=[
        ('fp_NQZ26_XCME_Time_20260204-20261125_293d16h', None, None)]),
}


def cache_path(sym):
    return os.path.join(CDIR, 'vm1_%s.pkl' % sym)


def load_one(stem, t_from, t_to, tick):
    bars = pd.read_csv(os.path.join(FP, stem + '_bars.csv'),
                       usecols=['bar_idx', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'levels'],
                       parse_dates=['datetime'])
    n_raw = len(bars)
    dup = int(bars['datetime'].duplicated().sum())
    bars = bars.sort_values('datetime').drop_duplicates('datetime', keep='last')
    keep = np.ones(len(bars), bool)
    if t_from: keep &= (bars['datetime'] >= pd.Timestamp(t_from)).values
    if t_to: keep &= (bars['datetime'] < pd.Timestamp(t_to)).values
    bars = bars[keep].reset_index(drop=True)
    idx2t = pd.Series(bars['datetime'].values, index=bars['bar_idx'].values)
    parts, m1sum = [], []
    for ch in pd.read_csv(os.path.join(FP, stem + '.csv'), usecols=['bar_idx', 'price', 'volume'], chunksize=3_000_000):
        t = idx2t.reindex(ch['bar_idx'].values).values
        ok = ~pd.isna(t)
        if not ok.any(): continue
        g = pd.DataFrame({'t': t[ok], 'tick': np.round(ch['price'].values[ok] / tick).astype(np.int64),
                          'vol': ch['volume'].values[ok].astype(np.float64)})
        m1sum.append(g.groupby('t', sort=False).agg(lv_vol=('vol', 'sum'), lv_n=('vol', 'size'), lv_zero=('vol', lambda x: (x <= 0).sum())).reset_index())
        g['t30'] = pd.DatetimeIndex(g['t']).floor('30min')
        parts.append(g.groupby(['t30', 'tick'], sort=False)['vol'].sum().reset_index())
    lv = pd.concat(parts).groupby(['t30', 'tick'], sort=True)['vol'].sum().reset_index()
    ms = pd.concat(m1sum).groupby('t').sum().reset_index()
    bars = bars.merge(ms, left_on='datetime', right_on='t', how='left').drop(columns='t')
    print('  %s: %d dòng nến (trùng giờ %d), giữ %d' % (stem, n_raw, dup, len(bars)), flush=True)
    return bars, lv


def quality(sym, bars, tick):
    """Kiểm theo tháng: nến M1 volume 0, nến không có / thiếu khối lượng theo giá, lỗ thời gian, phiên mỏng."""
    b = bars.copy()
    b['lv_vol'] = b['lv_vol'].fillna(0); b['lv_n'] = b['lv_n'].fillna(0)
    b['thang'] = b['datetime'].dt.strftime('%Y-%m')
    b['v0'] = b['volume'] <= 0
    b['no_lv'] = b['lv_n'] == 0
    b['lech'] = (b['lv_vol'] - b['volume']).abs() > 0.5            # tổng khối lượng theo giá ≠ khối lượng nến
    b['thieu_muc'] = b['lv_n'] != b['levels']                       # số mức giá trong file footprint ≠ cột levels của nến
    b['hl_bad'] = (b['high'] < b['low']) | (b['open'] > b['high']) | (b['open'] < b['low']) | (b['close'] > b['high']) | (b['close'] < b['low'])
    off = np.abs(np.round(b[['open', 'high', 'low', 'close']].values / tick) * tick - b[['open', 'high', 'low', 'close']].values).max(axis=1)
    b['lech_tick'] = off > 1e-6
    gap = b['datetime'].diff().dt.total_seconds().div(60).fillna(1)
    b['gap'] = gap.values
    # phiên theo nghỉ > 75 phút (trên M1 thì nghỉ 60 phút của CME = gap 61 phút) → dùng > 55 phút để tách phiên M1
    b['phien'] = (b['gap'] > 55).cumsum()
    print('\n### %s — chất lượng theo tháng (nến M1)' % sym.upper())
    print('| Tháng | nến M1 | volume = 0 | không có khối lượng theo giá | tổng theo giá ≠ volume nến | số mức giá ≠ cột levels | OHLC sai | giá lệch bước giá | lỗ 6–55 phút trong phiên | khối lượng (hợp đồng) |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for th, g in b.groupby('thang'):
        lo = int(((g['gap'] > 5) & (g['gap'] <= 55)).sum())
        print('| %s | %d | %d | %d | %d | %d | %d | %d | %d | %s |' % (th, len(g), g['v0'].sum(), g['no_lv'].sum(), g['lech'].sum(), g['thieu_muc'].sum(),
                                                                g['hl_bad'].sum(), g['lech_tick'].sum(), lo, format(int(g['volume'].sum()), ',').replace(',', '.')))
    g = b
    print('| **cả kỳ** | %d | %d | %d | %d | %d | %d | %d | %d | %s |' % (len(g), g['v0'].sum(), g['no_lv'].sum(), g['lech'].sum(), g['thieu_muc'].sum(), g['hl_bad'].sum(),
                                                                  g['lech_tick'].sum(), int(((g['gap'] > 5) & (g['gap'] <= 55)).sum()), format(int(g['volume'].sum()), ',').replace(',', '.')))
    # các loại khoảng nghỉ
    gg = b.loc[b['gap'] > 5, ['datetime', 'gap']]
    cls = pd.cut(gg['gap'], [5, 55, 75, 150, 1800, 1e9], labels=['6–55 phút', '56–75 phút (nghỉ ngày CME)', '76–150 phút', '2,5–30 giờ', '> 30 giờ (cuối tuần)'])
    print('\nKhoảng nghỉ giữa hai nến M1 (> 5 phút):', cls.value_counts().sort_index().to_dict())
    odd = gg[(gg['gap'] > 5) & (gg['gap'] <= 55) | (gg['gap'] > 75) & (gg['gap'] <= 1800)]
    if len(odd):
        print('Các khoảng nghỉ KHÔNG phải nghỉ ngày / cuối tuần (nến mở lại lúc, số phút):')
        for _, r in odd.iterrows():
            print('   %s  %.0f phút (%s)' % (r['datetime'], r['gap'], r['datetime'].day_name()))
    # giờ bắt đầu nghỉ ngày
    prev = b['datetime'].shift(1)
    dd = b[(b['gap'] > 55) & (b['gap'] <= 75)]
    print('Nghỉ ngày: nến cuối trước nghỉ (giờ UTC) →', prev.loc[dd.index].dt.strftime('%H:%M').value_counts().to_dict(),
          '| nến đầu sau nghỉ →', dd['datetime'].dt.strftime('%H:%M').value_counts().to_dict())
    # phiên
    ph = b.groupby('phien').agg(bat_dau=('datetime', 'first'), ket_thuc=('datetime', 'last'), nen=('volume', 'size'), vol=('volume', 'sum'),
                                v0=('v0', 'sum'))
    ph['thang'] = ph['bat_dau'].dt.strftime('%Y-%m')
    print('\n| Tháng | số phiên | nến M1/phiên (trung vị) | hợp đồng/phiên: nhỏ nhất | trung vị | lớn nhất |')
    print('|---|---|---|---|---|---|')
    for th, g in ph.groupby('thang'):
        print('| %s | %d | %d | %s | %s | %s |' % (th, len(g), g['nen'].median(), format(int(g['vol'].min()), ',').replace(',', '.'),
                                              format(int(g['vol'].median()), ',').replace(',', '.'), format(int(g['vol'].max()), ',').replace(',', '.')))
    return ph


def main(sym):
    cfg = CFG[sym]
    B, L = [], []
    for stem, a, b in cfg['src']:
        bars, lv = load_one(stem, a, b, cfg['tick'])
        B.append(bars); L.append(lv)
    bars = pd.concat(B).sort_values('datetime').reset_index(drop=True)
    assert not bars['datetime'].duplicated().any()
    lv = pd.concat(L).groupby(['t30', 'tick'], sort=True)['vol'].sum().reset_index()
    print(); print('## TOÀN BỘ FILE')
    ph = quality(sym, bars, cfg['tick'])
    ph.to_csv(os.path.join(CDIR, 'vm1_%s_phien.csv' % sym), index=False)
    bars = bars[bars['datetime'] >= pd.Timestamp(cfg['t_min'])].reset_index(drop=True)
    lv = lv[lv['t30'] >= pd.Timestamp(cfg['t_min'])].reset_index(drop=True)
    print(); print('## PHẦN DÙNG ĐỂ ĐO (từ %s)' % cfg['t_min'])
    quality(sym, bars, cfg['tick'])
    sc = cfg['scale']
    bars['t30'] = bars['datetime'].dt.floor('30min')
    g = bars.groupby('t30', sort=True)
    m30 = pd.DataFrame({'o': g['open'].first(), 'h': g['high'].max(), 'l': g['low'].min(),
                        'c': g['close'].last(), 'v': g['volume'].sum()}).reset_index()
    pos = pd.Series(np.arange(len(m30)), index=m30['t30'].values)
    # nến M30 không có khối lượng theo giá
    has = np.zeros(len(m30), bool); has[pos.reindex(lv['t30'].values).values.astype(int)] = True
    print('\nNến M30: %d · volume = 0: %d · không có khối lượng theo giá: %d' % (len(m30), int((m30['v'] <= 0).sum()), int((~has).sum())))
    out = dict(
        m1=dict(t=bars['datetime'].values.astype('datetime64[ns]'), o=bars['open'].values / sc, h=bars['high'].values / sc,
                l=bars['low'].values / sc, c=bars['close'].values / sc, v=bars['volume'].values.astype(float),
                i30=pos.reindex(bars['t30'].values).values.astype(np.int32)),
        m30=dict(t=m30['t30'].values.astype('datetime64[ns]'), o=m30['o'].values / sc, h=m30['h'].values / sc,
                 l=m30['l'].values / sc, c=m30['c'].values / sc, v=m30['v'].values.astype(float)),
        # vm.py coi tick lưu = giá × 10 với bước 0,1 ⇒ lưu số bước giá (giá thật / tick thật)
        lv=(pos.reindex(lv['t30'].values).values.astype(np.int32), lv['tick'].values.astype(np.int32),
            lv['vol'].values.astype(np.float32)),
        scale=sc, sym=sym,
    )
    with open(cache_path(sym), 'wb') as f:
        pickle.dump(out, f, protocol=4)
    print('xong:', cache_path(sym), 'M1', len(bars), 'M30', len(m30), 'mức giá', len(lv))


if __name__ == '__main__':
    main(sys.argv[1])
