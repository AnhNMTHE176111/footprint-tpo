"""Dùng chung cho đo SÀN tuyệt đối của chấm Bid/Ask (2026-11-24).
Luật (đã khớp C# từng chấm, xem ../adaptive_2026-11-24/dot_rule.py):
  B, R = TB trung vị volume mỗi ô / TB biên độ (tick) trên N nến đã đóng trước, N = min(20, max(5, round(120/phút)))
  w = max(4, round(R/6))  (bật "nổ ở mọi mức giá" -> điều kiện lớn nhất dùng w = 0, nhưng che vẫn tính theo w thật, như UnifiedDots.Apply)
  ngưỡng = max(k x B, SÀN);  che chấm xanh cách chấm đỏ <= h tick, h = max(hide_min, round(hide_ratio x w))
Cách tính nhanh cho nhiều sàn: tìm một lần mọi ô "lớn nhất trong ±w" đạt k x B (sàn 0, chưa che) -> cands();
  rồi với từng sàn f: giữ ô có v >= f, bỏ chấm xanh có chấm đỏ CÒN SỐNG (v đỏ >= f) trong ±h tick -> apply_floor().
  (đỏ còn sống ở sàn f <=> v đỏ >= f, nên chỉ cần nhớ v lớn nhất của các chấm đỏ trong ±h quanh mỗi chấm xanh.)"""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
AD = os.path.join(HERE, '..', 'adaptive_2026-11-24'); NQDIR = os.path.join(HERE, '..', 'nq_calib_2026-11-24')
sys.path.insert(0, AD); sys.path.insert(0, NQDIR)
from dot_rule import dots_fast, MIN_BARS, evaluate_bar, run_reference, unified
from common_window import nbase
from bt_common import ses_of, SES, SES_VN

FLOORS = [0, 5, 7, 9, 10, 12, 15, 18, 20, 25, 30]
TFS = (1, 5, 15, 30, 60)
PRESETS = {  # tên: (k, hide_ratio, hide_min)
    'Không sót': (2.0, 0.0, 2),
    'Trung gian': (2.4, 0.0, 2),
    'Ít nhiễu': (2.8, 0.75, 6),
}
_c = {}
def load(sym, m):
    if (sym, m) not in _c:
        _c[(sym, m)] = (pd.read_pickle(os.path.join(NQDIR, f'F_{sym}_m{m}.pkl')), pd.read_pickle(os.path.join(NQDIR, f'S_{sym}_m{m}.pkl')))
    return _c[(sym, m)]

def base(S, m, N=None):
    """B, R, w theo nến (NaN = chưa đủ nền)."""
    N = N or nbase(m)
    B = S.med.shift(1).rolling(N, min_periods=MIN_BARS).mean()
    R = S.rng.shift(1).rolling(N, min_periods=MIN_BARS).mean()
    ok = B.notna() & (B > 0)
    w = np.maximum(4, np.floor(R / 6 + 0.5)).where(ok)
    return B.where(ok), R.where(ok), w

def cands(F, S, m, preset, all_levels=False, N=None):
    """Mọi ô đạt k x B và (lớn nhất trong ±w | mọi mức giá), CHƯA sàn, CHƯA che. Cột: t, tk, col, v, kB, h, rmax (chỉ chấm xanh: v đỏ lớn nhất trong ±h, 0 nếu không có)."""
    k, hr, hm = PRESETS[preset]
    B, R, w = base(S, m, N)
    thr = k * B
    h = np.maximum(hm, np.floor(hr * w + 0.5))
    D = dots_fast(F, thr, w * 0 if all_levels else w, w * 0 - 1)        # h = -1: chưa che
    D['kB'] = D.t.map(thr).values; D['h'] = D.t.map(h).values.astype(int); D['rmax'] = 0.0
    red = D[D.col == 'S'][['t', 'tk', 'v']].rename(columns={'tk': 'rtk', 'v': 'rv'})
    b = D[D.col == 'B'].reset_index()[['index', 't', 'tk', 'h']].merge(red, on='t', how='inner')
    b = b[(b.rtk - b.tk).abs() <= b.h]
    if len(b):
        mx = b.groupby('index').rv.max(); D.loc[mx.index, 'rmax'] = mx.values
    return D, thr

def apply_floor(D, f):
    """Chấm còn lại với sàn f (ngưỡng = max(k x B, f)) sau luật che."""
    X = D[D.v >= f]
    return X[(X.col == 'S') | (X.rmax < f) | (X.rmax <= 0)] if f > 0 else X[(X.col == 'S') | (X.rmax <= 0)]

def per_session(D, idx):
    """chấm/nến theo phiên + tất cả; idx = các nến đủ nền."""
    per = D.groupby('t').size().reindex(idx, fill_value=0); ses = ses_of(idx)
    return {s: per.values[ses == s].mean() if (ses == s).any() else np.nan for s in SES} | {'all': per.mean()}
