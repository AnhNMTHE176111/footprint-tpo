# -*- coding: utf-8 -*-
"""Mổ SL Follow vòng 1 — phần đo SỐ của Fable (plan BENZO-FOLLOW-COMBO mục 5.4 + 9.3-B, hậu kiểm, chỉ TRAIN).

Ba việc:
  1. Nhãn TAY (report/_mo_sl_fable_tay.csv — Fable + 2 fork gắn trước khi đọc nhãn máy) so với nhãn MÁY
     (report/_mo_sl_follow.csv): bảng khớp + ma trận nhầm.
  2. Đặc điểm BIẾT ĐƯỢC TẠI NẾN CF, so SL vs TP trên TOÀN BỘ lệnh thật của F7 / F10 / F0 (không chỉ ảnh):
     rủi ro tuyệt đối, khoảng vào−E theo mbr, move_h / chiều cao range, move xuyên range, depth_frac,
     n_hoi, thân CF, leg, phiên, xu hướng 1 giờ.
  3. Giả thuyết "SL sát cạnh bị quét rồi giá đi đúng hướng": % lệnh SL mà sau khi dính SL giá chạm mức TP
     trong N nến, so với nền = nến ngẫu nhiên cùng phiên, cùng khoảng cách (3R), cùng hướng / ngược hướng.
     Thêm: MFE trước khi dính SL (đã đi được bao nhiêu R rồi mới quay).

Chạy từ benzo-trader/research:  python mo_sl_fable.py   → in Markdown ra stdout, ghi report/_mo_sl_fable_feats.csv.
Không sửa file nào khác. Không mở TEST (dùng plot_follow.load_bars_train — cắt tại 2026-09-15).
"""
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, '.')
from plot_follow import load_bars_train, REPORT  # noqa: E402

TICK = 0.1
NS = (15, 30, 60)
RNG = np.random.default_rng(0)


def f2(x, p=2):
    return '–' if x is None or (isinstance(x, float) and not np.isfinite(x)) else f'{x:.{p}f}'.replace('.', ',')


def pct(a, b):
    return '–' if b == 0 else f'{100.0 * a / b:.0f} %'


def load_trades(df):
    m = pd.read_csv(REPORT + '/_mo_sl_follow.csv')
    out = {}
    for cb in ('F7', 'F10', 'F0'):
        t = pd.read_csv(REPORT + f'/_follow_trades_{cb}.csv')
        mm = m[m['combo'] == cb].set_index('idx_c')[['outcome', 'r', 'nhan']]
        t = t.set_index('idx_c').join(mm).reset_index()
        assert t['outcome'].notna().all(), cb
        out[cb] = add_feats(t, df)
    return out


def add_feats(t: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    o, h, l, c = (df[k].to_numpy(float) for k in ('open', 'high', 'low', 'close'))
    sno = df['session_no'].to_numpy()
    n = len(df)
    rows = []
    for r in t.itertuples(index=False):
        D = int(r.D); ic = int(r.idx_c); iref = int(r.idx_ref); ix = int(r.idx_x)
        E = r.E / 10.0; top = r.top / 10.0; bot = r.bottom / 10.0
        entry = r.entry / 10.0; sl = r.sl_S2 / 10.0; tp = r.tp_S2 / 10.0
        risk = abs(entry - sl)
        rng_h = max(top - bot, TICK)
        mbr = r.mbr_c / 10.0 if r.mbr_c > 0 else np.nan
        # --- biết được tại CF ---
        vao_E_mbr = (entry - E) * D / mbr if mbr > 0 else np.nan
        move_h = r.move_h / 10.0
        move_x_rng = move_h / rng_h
        a = max(0, iref - 15)
        opp = (l[a:iref + 1].min() <= bot + TICK) if D > 0 else (h[a:iref + 1].max() >= top - TICK)
        body = abs(c[ic] - o[ic]); span = max(h[ic] - l[ic], TICK)
        cf_body = body / span
        cf_close_ext = ((h[ic] - c[ic]) if D > 0 else (c[ic] - l[ic])) / span
        j = ic - 60
        tr1h = ((c[ic] - c[j]) * D / mbr) if (j >= 0 and sno[j] == sno[ic] and mbr > 0) else np.nan
        # --- sau khi vào lệnh (chẩn đoán) ---
        ex = int(r.exit_alone) if pd.notna(r.exit_alone) else -1
        mfe = np.nan; sl_wick = np.nan; tp_after = {N: np.nan for N in NS}
        if ex > ic:
            seg_h = h[ic + 1:ex + 1]; seg_l = l[ic + 1:ex + 1]
            mfe = ((seg_h.max() - entry) if D > 0 else (entry - seg_l.min())) / risk
        if r.outcome == 'SL' and ex > ic:
            sl_wick = ((sl - l[ex]) if D > 0 else (h[ex] - sl)) / TICK  # tick vượt quá SL ở nến dính SL
            for N in NS:
                b = min(n, ex + 1 + N)
                seg = h[ex + 1:b] if D > 0 else l[ex + 1:b]
                tp_after[N] = int(len(seg) > 0 and ((seg.max() >= tp) if D > 0 else (seg.min() <= tp)))
        rows.append(dict(idx_c=ic, combo=None, outcome=r.outcome, r=r.r, nhan_may=r.nhan, D=D, leg=int(r.leg),
                         phase=r.phase, t_vn=r.t_vn, risk_gia=risk, risk_mbr=risk / mbr if mbr > 0 else np.nan,
                         vao_E_mbr=vao_E_mbr, move_h=move_h, move_x_rng=move_x_rng, xuyen_range=int(opp),
                         depth_frac=r.depth_frac, n_hoi=int(r.n_hoi), cf_body=cf_body, cf_close_ext=cf_close_ext,
                         tr1h_mbr=tr1h, mfe_R=mfe, sl_wick_tick=sl_wick,
                         **{f'tp_sau_sl_{N}': tp_after[N] for N in NS}, exit=ex, sl=sl, tp=tp, sno=int(sno[ic])))
    return pd.DataFrame(rows)


def baseline_tp_after(df: pd.DataFrame, t: pd.DataFrame, draws: int = 20):
    """Nền: với mỗi lệnh SL, rút `draws` nến j ngẫu nhiên cùng phiên, j > idx_c (và j+1 còn trong phiên);
    đích = close[j] + D·(|tp−sl|) (= 3R từ SL, đúng khoảng cách cần đi sau SL). Đo cả cùng hướng lẫn ngược hướng."""
    h, l, c = (df[k].to_numpy(float) for k in ('high', 'low', 'close'))
    sno = df['session_no'].to_numpy(); n = len(df)
    s_end = pd.Series(np.arange(n)).groupby(sno).max().to_dict()
    res = {('same', N): [] for N in NS}; res.update({('opp', N): [] for N in NS})
    for r in t[t['outcome'] == 'SL'].itertuples(index=False):
        dist = abs(r.tp - r.sl); e = s_end[r.sno]
        lo = r.idx_c + 1
        if e - lo < 5:
            continue
        js = RNG.integers(lo, e, size=draws)
        for j in js:
            for sign, key in ((r.D, 'same'), (-r.D, 'opp')):
                tgt = c[j] + sign * dist
                for N in NS:
                    b = min(n, j + 1 + N)
                    seg = h[j + 1:b] if sign > 0 else l[j + 1:b]
                    hit = len(seg) > 0 and ((seg.max() >= tgt) if sign > 0 else (seg.min() <= tgt))
                    res[(key, N)].append(int(hit))
    return {k: (np.mean(v) if v else np.nan) for k, v in res.items()}


def table_hand_vs_machine(tay: pd.DataFrame, feats: dict):
    out = []
    labels = ['MOVE_GIA', 'SL_QUET', 'HOI_SAU', 'CF_YEU', 'NGUOC_1H', 'PHIEN_MONG', 'KHONG_RO']
    for bo, cb in (('F7', 'F7'), ('F10', 'F10')):
        # bộ ảnh F10 = 34 SL riêng + 39 SL trùng F7 (nhãn tay lấy từ bộ F7, cùng lệnh) + 5 TP
        ht = tay[tay['bo_anh'] == bo].set_index('idx_c')['nhan_tay']
        if bo == 'F10':
            h7 = tay[tay['bo_anh'] == 'F7'].set_index('idx_c')['nhan_tay']
            ht = pd.concat([ht, h7[~h7.index.isin(ht.index)]])
        f = feats[cb].set_index('idx_c')
        j = f.join(ht, how='inner')
        j = j[j['outcome'].isin(['SL', 'TP'])]
        agree = (j['nhan_tay'] == j['nhan_may'])
        out.append(f"### {cb} — {len(j)} lệnh có nhãn tay (SL {int((j.outcome == 'SL').sum())} · TP {int((j.outcome == 'TP').sum())}); "
                   f"khớp tay = máy: **{int(agree.sum())}/{len(j)} = {pct(agree.sum(), len(j))}** "
                   f"(SL: {pct(agree[j.outcome == 'SL'].sum(), (j.outcome == 'SL').sum())}, TP: {pct(agree[j.outcome == 'TP'].sum(), (j.outcome == 'TP').sum())})\n")
        out.append('| nhãn | tay (SL) | máy (SL) | tay (TP) | máy (TP) |\n|---|---|---|---|---|')
        for lb in labels:
            s = j[j.outcome == 'SL']; p = j[j.outcome == 'TP']
            out.append(f"| {lb} | {int((s.nhan_tay == lb).sum())} | {int((s.nhan_may == lb).sum())} | {int((p.nhan_tay == lb).sum())} | {int((p.nhan_may == lb).sum())} |")
        out.append('\nMa trận nhầm (hàng = tay, cột = máy), chỉ lệnh SL:\n')
        s = j[j.outcome == 'SL']
        cm = pd.crosstab(s['nhan_tay'], s['nhan_may']).reindex(index=labels, columns=labels, fill_value=0)
        out.append('| tay \\ máy | ' + ' | '.join(labels) + ' |\n|---|' + '---|' * len(labels))
        for lb in labels:
            out.append(f'| {lb} | ' + ' | '.join(str(int(cm.loc[lb, m])) for m in labels) + ' |')
        out.append('')
    return '\n'.join(out)


def table_feats(feats: dict):
    cols = [('risk_gia', 'rủi ro S2 (giá)', 'median'), ('risk_mbr', 'rủi ro S2 (mbr)', 'median'),
            ('vao_E_mbr', 'vào − E (mbr)', 'median'), ('move_h', 'move_h (giá)', 'median'),
            ('move_x_rng', 'move_h / chiều cao range', 'median'), ('xuyen_range', '% move xuyên range (chạm cạnh đối diện ≤ 15 nến trước ref)', 'pct'),
            ('depth_frac', 'depth_frac (hồi / move)', 'median'), ('n_hoi', '% nhịp hồi đúng 1 nến', 'pct1'),
            ('cf_body', 'thân CF / biên độ', 'median'), ('cf_close_ext', 'CF đóng cách cực trị / biên độ', 'median'),
            ('tr1h_mbr', 'xu hướng 1 giờ theo hướng lệnh (mbr)', 'median'), ('leg', '% leg 2', 'pct2'),
            ('phase', '% phiên Á', 'pctA')]
    out = []
    for cb in ('F7', 'F10', 'F0'):
        f = feats[cb]; s = f[f.outcome == 'SL']; p = f[f.outcome == 'TP']
        out.append(f'### {cb} — SL n {len(s)} · TP n {len(p)} (lệnh thật, đặc điểm biết được tại nến CF)\n')
        out.append('| đặc điểm | SL | TP | ghi chú |\n|---|---|---|---|')
        for k, name, how in cols:
            if how == 'median':
                a, b = s[k].median(), p[k].median()
                q = f'p25–p75 SL {f2(s[k].quantile(.25))}–{f2(s[k].quantile(.75))} · TP {f2(p[k].quantile(.25))}–{f2(p[k].quantile(.75))}'
                out.append(f'| {name} (trung vị) | {f2(a)} | {f2(b)} | {q} |')
            elif how == 'pct':
                out.append(f'| {name} | {pct(s[k].sum(), len(s))} | {pct(p[k].sum(), len(p))} | |')
            elif how == 'pct1':
                out.append(f'| {name} | {pct((s[k] == 1).sum(), len(s))} | {pct((p[k] == 1).sum(), len(p))} | |')
            elif how == 'pct2':
                out.append(f'| {name} | {pct((s[k] == 2).sum(), len(s))} | {pct((p[k] == 2).sum(), len(p))} | |')
            elif how == 'pctA':
                out.append(f'| {name} | {pct((s[k] == "A").sum(), len(s))} | {pct((p[k] == "A").sum(), len(p))} | |')
        out.append('')
    # cắt theo ngưỡng — chỉ báo, hậu kiểm
    out.append('### Cắt theo ngưỡng (hậu kiểm, CHỈ BÁO — không có sức chọn): R TB (n) hai phía\n')
    cuts = [('risk_gia', 5.0, 'rủi ro S2 ≥ 5 giá'), ('risk_gia', 7.0, 'rủi ro S2 ≥ 7 giá'), ('risk_mbr', 2.5, 'rủi ro S2 ≥ 2,5 mbr'),
            ('vao_E_mbr', 2.0, 'vào − E ≥ 2 mbr'), ('vao_E_mbr', 3.0, 'vào − E ≥ 3 mbr'), ('move_x_rng', 1.0, 'move_h ≥ 1 × range'),
            ('move_x_rng', 2.0, 'move_h ≥ 2 × range'), ('depth_frac', 0.7, 'depth_frac > 0,7'), ('cf_body', 0.4, 'thân CF < 0,4 (đảo dấu)')]
    out.append('| ngưỡng | F7 đạt | F7 không | F10 đạt | F10 không | F0 đạt | F0 không |\n|---|---|---|---|---|---|---|')
    for k, th, name in cuts:
        cells = []
        for cb in ('F7', 'F10', 'F0'):
            f = feats[cb][feats[cb].outcome.isin(['SL', 'TP'])]
            if k == 'cf_body':
                m = f[k] < th
            elif k == 'depth_frac':
                m = f[k] > th
            else:
                m = f[k] >= th
            a = f[m]['r']; b = f[~m]['r']
            cells += [f'{f2(a.mean())} ({len(a)})', f'{f2(b.mean())} ({len(b)})']
        out.append(f'| {name} | ' + ' | '.join(cells) + ' |')
    out.append('')
    return '\n'.join(out)


def table_sl_then_tp(feats: dict, df: pd.DataFrame):
    out = ['| combo | n SL | SL chỉ râu (≤ 2 tick quá SL) | MFE ≥ 1R trước SL | MFE ≥ 1,5R | '
           + ' | '.join(f'chạm TP sau SL ≤ {N} nến' for N in NS) + ' | nền cùng hướng (15/30/60) | nền ngược hướng (15/30/60) |',
           '|---|---|---|---|---|' + '---|' * len(NS) + '---|---|']
    for cb in ('F7', 'F10', 'F0'):
        f = feats[cb]; s = f[f.outcome == 'SL']
        base = baseline_tp_after(df, f)
        cells = [cb, str(len(s)), pct((s.sl_wick_tick <= 2).sum(), len(s)), pct((s.mfe_R >= 1.0).sum(), len(s)), pct((s.mfe_R >= 1.5).sum(), len(s))]
        cells += [pct(s[f'tp_sau_sl_{N}'].sum(), len(s)) for N in NS]
        cells.append(' / '.join(f'{100 * base[("same", N)]:.0f} %' for N in NS))
        cells.append(' / '.join(f'{100 * base[("opp", N)]:.0f} %' for N in NS))
        out.append('| ' + ' | '.join(cells) + ' |')
    out.append('')
    # riêng: SL râu & sau đó chạm TP ≤ 30 nến (đúng định nghĩa SL_QUET của máy) + nhóm SL "đã đi ≥ 1R"
    for cb in ('F7', 'F10'):
        s = feats[cb][feats[cb].outcome == 'SL']
        q = s[(s.sl_wick_tick <= 2) & (s.tp_sau_sl_30 == 1)]
        out.append(f'- {cb}: SL râu ≤ 2 tick VÀ chạm TP ≤ 30 nến: {len(q)}/{len(s)} = {pct(len(q), len(s))} (idx: {", ".join(str(i) for i in q.idx_c)}). '
                   f'Chạm TP ≤ 30 nến bất kể râu: {int(s.tp_sau_sl_30.sum())}/{len(s)}.')
    return '\n'.join(out)


def main():
    df, _ = load_bars_train()
    feats = load_trades(df)
    for cb, f in feats.items():
        f['combo'] = cb
    allf = pd.concat(feats.values(), ignore_index=True)
    allf.to_csv(REPORT + '/_mo_sl_fable_feats.csv', index=False)
    tay = pd.read_csv(REPORT + '/_mo_sl_fable_tay.csv')
    print('## A. Nhãn tay vs nhãn máy\n')
    print(table_hand_vs_machine(tay, feats))
    print('## B. Đặc điểm tại CF — SL vs TP (toàn bộ lệnh thật)\n')
    print(table_feats(feats))
    print('## C. Sau khi dính SL — giá có đi đúng hướng tới TP không (so với nền)\n')
    print(table_sl_then_tp(feats, df))


if __name__ == '__main__':
    main()
