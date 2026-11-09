# -*- coding: utf-8 -*-
"""
follow_newdata.py — chạy Follow F0…F10 + F7b với CẤU HÌNH ĐÓNG BĂNG trên dữ liệu MỚI (≥ 2026-10-22)
(plans/BENZO-FOLLOW-COMBO-plan.md mục 10.3-3; tiêu chí ĐẠT của F7b ở 10.2-1, đăng ký trước tại commit aa3d078).

Chạy (đầu vào DUY NHẤT là đường dẫn file Footprint Export; file `_bars.csv` cùng tên phải nằm cạnh):
    PYTHONIOENCODING=utf-8 python benzo-trader/research/follow_newdata.py data-export/data-footprint/fp_GCZ26_XCEC_Time_<...>.csv

Đầu ra: in Markdown ra màn hình + ghi `report/RESULTS-FOLLOW-NEWDATA_<tên file>.md`:
  0. đối chiếu ca ảnh gốc (mục 4.9 plan) — kiểm TRƯỚC khi đọc số;
  1. bảng chính F0…F10 + F7b (+ 3 dòng báo cáo) — C1, C1 F0∖combo, C2', nửa 1/2, hoán vị (family 11, ngưỡng ≥ 30);
  2. kiểm F7b theo 10.2-1, in ĐẠT / KHÔNG kèm từng điều kiện;
  3. bảng H1–H3.

Không có tham số nào khác. Mọi phiên có session_id < 2026-10-22 bị bỏ NGAY KHI NẠP (chỉ đọc cột datetime để tách phiên, không
đọc giá) ⇒ file 90d đã xuất (TEST 16/09–21/10 đang khoá) không thể lọt vào. Cấu hình = `follow_combo.FP()` mặc định + `eval_post`
(cùng hàm follow_combo.main dùng cho TRAIN) — không sửa gì ở đây khi có dữ liệu.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kernel as K                 # noqa: E402
import of_signals as OF            # noqa: E402
import follow_combo as FC          # noqa: E402

TICK = 0.1
NEW_FROM = '2026-10-22'
TEST_LOCK = ('2026-09-16', '2026-10-21')      # TEST của file 90d — khoá, không bao giờ nạp


def prefix_of(path: str) -> str:
    p = path
    for suf in ('_bars.csv', '.csv'):
        if p.endswith(suf):
            return p[: -len(suf)]
    return p


def session_names(t: pd.Series):
    """Tách phiên + đặt tên y như kernel._enrich (tên = ngày nến cuối, trùng thì thêm hậu tố) — chỉ cần cột datetime."""
    gap = t.diff().dt.total_seconds().div(60.0).to_numpy()
    gap = np.where(np.isnan(gap), 0.0, gap)
    sno = np.cumsum(gap > K.CONST['gap_min']).astype(np.int64)
    last_date = t.dt.strftime('%Y-%m-%d').groupby(sno).last()
    names, seen = [], {}
    for d in last_date.tolist():
        k = seen.get(d, 0)
        names.append(d if k == 0 else d + '-' + chr(ord('a') + k))
        seen[d] = k + 1
    return sno, np.asarray(names, dtype=object)


def load_segment(prefix: str, sess_lo: str, sess_hi: str | None = None):
    """Nạp các phiên có session_id[:10] ∈ [sess_lo, sess_hi] (sess_hi None = tới hết file). Trả (bars, df, info).
    Phiên trong cửa sổ TEST khoá 16/09–21/10 ⇒ AssertionError trước khi đọc bất kỳ giá nào."""
    ti = pd.read_csv(prefix + '_bars.csv', usecols=['bar_idx', 'datetime'], parse_dates=['datetime'])
    sno, names = session_names(ti['datetime'])
    day = np.array([s[:10] for s in names], dtype=object)
    keep_s = (day >= sess_lo) & ((day <= sess_hi) if sess_hi is not None else True)
    assert keep_s.any(), f'không có phiên nào trong [{sess_lo}, {sess_hi or "hết file"}]'
    bad = [names[s] for s in np.flatnonzero(keep_s) if TEST_LOCK[0] <= day[s] <= TEST_LOCK[1]]
    assert not bad, f'⛔ phiên thuộc TEST khoá {TEST_LOCK}: {bad[:3]}… — không nạp'
    pos = np.flatnonzero(keep_s[sno])
    p0, p1 = int(pos[0]), int(pos[-1])
    assert len(pos) == p1 - p0 + 1, 'các phiên chọn phải liền nhau'
    raw = pd.read_csv(prefix + '_bars.csv', parse_dates=['datetime'], float_precision='round_trip',
                      skiprows=lambda i: i > 0 and not (p0 + 1 <= i <= p1 + 1))
    assert len(raw) == p1 - p0 + 1
    b0 = int(raw['bar_idx'].iloc[0])
    assert (raw['bar_idx'].to_numpy() == np.arange(b0, b0 + len(raw))).all(), 'bar_idx phải liên tục'
    raw['bar_idx_goc'] = raw['bar_idx']
    raw['bar_idx'] = np.arange(len(raw))
    df = K._enrich(raw)
    o = np.round(raw['open'].to_numpy() / TICK).astype(np.int64)
    h = np.round(raw['high'].to_numpy() / TICK).astype(np.int64)
    lo = np.round(raw['low'].to_numpy() / TICK).astype(np.int64)
    c = np.round(raw['close'].to_numpy() / TICK).astype(np.int64)
    d = raw['delta'].to_numpy(float)
    mx = raw['max_delta'].to_numpy(float)
    mn = raw['min_delta'].to_numpy(float)
    bars = [OF.FpBar(i, int(o[i]), int(h[i]), int(lo[i]), int(c[i]), d[i], mx[i], mn[i], []) for i in range(len(raw))]
    b1 = b0 + len(raw) - 1
    for ch in K.iter_levels(prefix + '.csv', b0, b1, usecols=('bar_idx', 'price', 'bid_vol', 'ask_vol', 'volume')):
        bi = ch['bar_idx'].to_numpy() - b0
        k = np.round(ch['price'].to_numpy() / TICK).astype(np.int64)
        bv = ch['bid_vol'].to_numpy(float)
        av = ch['ask_vol'].to_numpy(float)
        v = ch['volume'].to_numpy(float)
        for j in range(len(bi)):
            bars[bi[j]].levels.append((int(k[j]), bv[j], av[j], v[j]))
    info = dict(prefix=prefix, bar_lo=b0, bar_hi=b1, t0=str(raw['datetime'].iloc[0])[:16], t1=str(raw['datetime'].iloc[-1])[:16])
    return bars, df, info


def run(prefix: str, sess_lo: str = NEW_FROM, sess_hi: str | None = None, n_perm: int = 2000):
    """Cấu hình đóng băng: FP() mặc định, good = phiên không mỏng, không dính chỗ nối hợp đồng."""
    bars, df, info = load_segment(prefix, sess_lo, sess_hi)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy())
    sess_good = sorted(set(df['session_id'].to_numpy()[good]))
    nd = len(sess_good)
    fp = FC.FP()
    m, d, f, eng_out = FC.build(bars, df, good, fp)
    if len(d) == 0:
        return dict(info=info, nd=nd, d=d, E=None, df=df)
    d = FC.add_halves(d, sess_good)
    E = FC.eval_post(d, f, df, fp, nd, n_perm=n_perm)
    return dict(info=info, nd=nd, d=d, E=E, df=df)


def photo_case(d: pd.DataFrame):
    """Mục 4.9: ca ảnh gốc GCZ26 M1 đầu 11/2026, ≈ 11:25–11:35 giờ máy người học; cạnh trên ≈ 4131; CF đóng 4132,2 (buy);
    SL 4129,1 · TP 4138,5. Trả (khớp chặt, khớp lỏng)."""
    if len(d) == 0:
        return d, d
    loose = d[(d['D'] == 1) & ((d['entry'] - 41322).abs() <= 2) & ((d['E'] - 41310).abs() <= 10)]
    hm = pd.to_datetime(loose['t_vn'])
    mins = hm.dt.hour * 60 + hm.dt.minute
    tight = loose[(loose['t_vn'].str[:7] == '2026-11') & (mins >= 11 * 60 + 15) & (mins <= 11 * 60 + 45)]
    return tight, loose


def report(R: dict) -> list:
    info, nd, d, E = R['info'], R['nd'], R['d'], R['E']
    L = [f"# Follow trên dữ liệu mới — `{os.path.basename(info['prefix'])}`", '',
         f"> `follow_newdata.py`, cấu hình đóng băng (plan BENZO-FOLLOW-COMBO mục 10.3-3, tiêu chí 10.2-1 đăng ký tại aa3d078). "
         f"Nến {info['t0']} → {info['t1']} UTC, {nd} phiên dày (bỏ phiên mỏng / chỗ nối hợp đồng); chỉ phiên ≥ {NEW_FROM}.", '']
    L += ['## 0. Ca ảnh gốc (mục 4.9 — kiểm TRƯỚC khi đọc số)', '']
    tight, loose = photo_case(d)
    if len(tight):
        L.append(f'**Máy bắt được ca ảnh gốc** ({len(tight)} dòng khớp chặt: buy, vào 4132,2 ± 0,2, cạnh ≈ 4131, 11:15–11:45 VN tháng 11):')
    elif len(loose):
        L.append('Không có dòng khớp chặt theo giờ; dòng khớp lỏng (buy, vào 4132,2 ± 0,2, cạnh ≈ 4131, bất kể giờ) — **Fable soi trước khi đọc số**:')
    else:
        L.append('**⛔ KHÔNG bắt được ca ảnh gốc** (không F0 buy nào vào 4132,2 ± 0,2 ở cạnh ≈ 4131). Theo 4.9: nếu ngày của ảnh nằm trong '
                 'file thì định nghĩa 2a–2c sai — **ĐỪNG đọc số bên dưới**, báo Fable sửa định nghĩa trước.')
    show = tight if len(tight) else loose
    if len(show):
        L += ['', '| t_vn | idx_c | vào | E | SL S2 | TP S2 | T | Bc | Dh | Hc | Vk | kết cục (độc lập) | R |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
        for r in show.itertuples():
            L.append(f"| {r.t_vn} | {r.idx_c} | {FC.f2(r.entry * TICK, 1)} | {FC.f2(r.E * TICK, 1)} | {FC.f2(r.sl_S2 * TICK, 1)} | "
                     f"{FC.f2(r.tp_S2 * TICK, 1)} | {r.T} | {r.Bc} | {r.Dh} | {r.Hc} | {r.Vk} | {r.outcome_alone} | {FC.f2(r.r_alone)} |")
        L += ['', 'Ảnh: SL 4129,1 · TP 4138,5 (2,03R) · chạm TP. Lệch SL/TP so với ảnh là do đệm/sàn 1 mbr của máy, không phải lỗi bắt ca.']
    L.append('')
    if E is None:
        L += ['Không có F0 nào ⇒ không có bảng.']
        return L
    L += ['## 1–3. Bảng chính F0…F10 + F7b, kiểm F7b (10.2-1), H1–H3', '']
    L += FC.render_post(E, nd)
    L += ['> Dòng F1…F10 trên dữ liệu mới **không** được dùng để chọn combo mới (đã chốt ở plan mục 4 / 10); chỉ F7b có tiêu chí ĐẠT đăng ký trước. '
          'H1–H3 chỉ đo, so với dự đoán ở `MO-SL-FOLLOW.md` mục 3.', '']
    return L


def main(argv):
    if len(argv) != 2:
        print('Cách chạy: python follow_newdata.py <đường dẫn fp_*.csv>   (file _bars.csv cùng tên phải nằm cạnh)')
        return 2
    prefix = prefix_of(os.path.abspath(argv[1]))
    assert os.path.exists(prefix + '.csv') and os.path.exists(prefix + '_bars.csv'), f'thiếu {prefix}.csv hoặc {prefix}_bars.csv'
    R = run(prefix)
    L = report(R)
    out = os.path.join(FC.REPORT, f'RESULTS-FOLLOW-NEWDATA_{os.path.basename(prefix)}.md')
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    if len(R['d']):
        R['d'].to_csv(os.path.join(FC.REPORT, f'_follow_cands_newdata_{os.path.basename(prefix)}.csv'), index=False, encoding='utf-8')
    print('\n'.join(L))
    print(f'\n→ {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
