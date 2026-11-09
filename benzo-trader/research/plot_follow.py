# -*- coding: utf-8 -*-
"""
plot_follow.py — plans/BENZO-FOLLOW-COMBO-plan.md 9.3-B1 (mổ SL vòng 1, chế độ "khám phá, hậu kiểm").

Ảnh từng lệnh Follow → report/follow_shots/<combo>/SL_<idx_c>.png | TP_<idx_c>.png (| TIME_<idx_c>.png cho F1):
  · F7, F10: MỌI lệnh SL + 5 lệnh TP rải đều theo thời gian;  · F1: cả 11 lệnh (thắng lẫn thua) — chỉ để soi định nghĩa trap.
Vẽ bằng plot_corven.plot_trade (trước 40 / sau 30 nến), vẽ thêm: hộp range + cạnh E, nến ref (đóng ngoài), nến x (cực trị move),
nến hồi (dải xám), nến CF, mức SL/TP, ô trap / bóng / kiệt sức / stacked nếu cờ bật.
Tiêu đề: combo · idx · UTC + giờ VN · side · leg · cờ · R.  ⛔ KHÔNG in nhãn máy của mo_sl_follow lên ảnh (Fable gắn nhãn tay trước).

Nguồn: report/_follow_trades_<combo>.csv (do follow_combo.py ghi) + nến TRAIN (cắt tại nến cuối phiên 2026-09-15, không nạp TEST).
Chạy:  PYTHONIOENCODING=utf-8 python plot_follow.py
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from types import SimpleNamespace

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K               # noqa: E402
import plot_corven as PC         # noqa: E402

REPORT = os.path.join(HERE, 'report')
SHOTS = os.path.join(REPORT, 'follow_shots')
TICK = 0.1
FLAGS = ('T', 'Bc', 'K', 'S', 'Dh', 'Dc', 'Sh', 'Mv')


def load_bars_train():
    """Nến M1 TRAIN (chỉ OHLC/Δ/volume, không nạp mức giá) — cắt tại SC.train_cut() TRƯỚC khi làm gì."""
    import setup_corven as SC
    cut = SC.train_cut()
    raw = pd.read_csv(SC.D90 + '_bars.csv', parse_dates=['datetime'], float_precision='round_trip')
    raw = raw[raw['bar_idx'] <= cut].reset_index(drop=True)
    assert (raw['bar_idx'].to_numpy() == np.arange(len(raw))).all()
    df = K._enrich(raw)
    assert str(df['datetime'].iloc[-1])[:10] <= '2026-09-15'
    sno = df['session_no'].to_numpy()
    n = len(df)
    starts = np.r_[0, np.flatnonzero(np.diff(sno)) + 1]
    ends = np.r_[starts[1:] - 1, n - 1]
    r = lambda c: np.round(raw[c].to_numpy() / TICK).astype(np.int64)   # noqa: E731
    f = SimpleNamespace(O=r('open'), H=r('high'), L=r('low'), C=r('close'), Dl=raw['delta'].to_numpy(float),
                        V=raw['volume'].to_numpy(float), sm=df['sm'].to_numpy(),
                        sstart=np.repeat(starts, ends - starts + 1), send=np.repeat(ends, ends - starts + 1))
    return df, f


def flags_of(r) -> str:
    return '+'.join(k for k in FLAGS if int(getattr(r, k)) == 1) or '–'


def _signs(r):
    """Dấu hiệu cờ bật → định dạng c.signs của plot_corven (typ → (mô tả, nến neo, giá tick))."""
    D = int(r.D)
    s = {}
    if int(r.T):
        s['trap'] = (f"ô {'Bid' if D > 0 else 'Ask'} {r.T_vol:.0f} hđ (×{r.T_x_nen} nền) ở {r.T_gia:.1f}, nến hồi",
                     int(r.T_nen), round(r.T_gia / TICK))
    if int(r.Bc):
        s['bong'] = (f"{'buy' if D > 0 else 'sell'} ở CF {r.Bc_vol:.0f} hđ (×{r.Bc_x_nen} nền) ở {r.Bc_gia:.1f}",
                     int(r.idx_c), round(r.Bc_gia / TICK))
    if int(r.K):
        s['kiet_suc'] = (f"{'đáy' if D > 0 else 'đỉnh'} ở {r.K_gia:.1f}", int(r.K_nen), round(r.K_gia / TICK))
    if int(r.S):
        s['stacked'] = (f"{r.S_lo:.1f}–{r.S_hi:.1f} (sinh ở nến {int(r.S_nen)})", int(r.S_nen),
                        round((r.S_lo if D > 0 else r.S_hi) / TICK))
    if int(r.Dh):
        x = int(r.idx_x)
        pb = list(range(x + 1, int(r.idx_c)))
        s['delta'] = (f"ΣΔ nhịp hồi {r.sumD_hoi:+.0f} ngược giá hồi", pb[-1] if pb else x, None)
    return s


def plot_follow_trade(df, f, r, combo: str, outdir: str, kind: str) -> str:
    import matplotlib.pyplot as plt
    D = int(r.D)
    c = int(r.idx_c)
    x = int(r.idx_x)
    ref = int(r.idx_ref)
    pb = list(range(x + 1, c))
    sg = _signs(r)
    # neo giá cho dấu Δ: đáy/đỉnh nến hồi cuối
    if 'delta' in sg:
        desc, k, _ = sg['delta']
        sg['delta'] = (desc, k, int(f.L[k]) if D > 0 else int(f.H[k]))
    cc = SimpleNamespace(cf=c, ref=ref, inst=SimpleNamespace(top=int(r.top), bottom=int(r.bottom)), mocs=[], w0=x + 1,
                         signs=dict(sg),
                         S=D, the='F', moc_used='', r_avail=0.0, exhausted=bool(int(r.b_from_exhausted)))
    t = dict(exit_idx=int(r.exit_alone), entry=r.entry * TICK, sl=r.sl_S2 * TICK, tp=r.tp_S2 * TICK, outcome=r.outcome_alone,
             r=float(r.r_alone), t_utc=str(r.t_utc), t_vn=str(r.t_vn))
    # plot_corven.plot_trade lưu + đóng hình; giữ lại hình để vẽ thêm rồi lưu lại
    cap = {}
    orig_sub, orig_close = PC.plt.subplots, PC.plt.close

    def sub(*a, **kw):
        fig, ax = orig_sub(*a, **kw)
        cap['fig'], cap['ax'] = fig, ax
        return fig, ax
    tmp = tempfile.mkdtemp()
    try:
        PC.plt.subplots, PC.plt.close = sub, (lambda *a, **k: None)
        PC.plot_trade(df, f, t, cc, tmp, 'tmp')
    finally:
        PC.plt.subplots, PC.plt.close = orig_sub, orig_close
        shutil.rmtree(tmp, ignore_errors=True)
    fig, ax = cap['fig'], cap['ax']
    a0, a1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    top, bot, E = r.top * TICK, r.bottom * TICK, r.E * TICK
    # hộp range (vàng nhạt) tới nến đóng ngoài + cạnh E đậm kéo tới hết hình
    ax.add_patch(plt.Rectangle((a0, bot), ref - 0.5 - a0, top - bot, color='#f2c14e', alpha=0.22, zorder=0))
    ax.axhline(E, color='#8a6d00', lw=1.6, ls='-', alpha=.85, zorder=1)
    ax.text(a1 - 0.5, E, f"cạnh E {E:.1f}", fontsize=7.5, ha='right', va='bottom' if D > 0 else 'top', color='#8a6d00',
            fontweight='bold')
    # nến x (cực trị move) + chữ
    xe = (f.H[x] if D > 0 else f.L[x]) * TICK
    ax.plot([x], [xe + (0.15 if D > 0 else -0.15)], marker='v' if D > 0 else '^', ms=9, color='#9b27b0', zorder=5)
    ax.text(x, xe + (0.45 if D > 0 else -0.45), 'x', fontsize=9, ha='center', va='center', color='#9b27b0', fontweight='bold')
    # nến hồi (dải xám đã có từ w0) + chữ "hồi"
    for j in pb:
        yy = (f.L[j] if D > 0 else f.H[j]) * TICK
        ax.text(j, yy - (0.55 if D > 0 else -0.55), 'hồi', fontsize=6.5, ha='center', color='#555')
    # nến CF
    ce = (f.L[c] if D > 0 else f.H[c]) * TICK
    ax.annotate('CF', xy=(c, ce), xytext=(c, ce - (0.9 if D > 0 else -0.9)), fontsize=9, ha='center', color='#1f5fbf',
                fontweight='bold', arrowprops=dict(arrowstyle='->', color='#1f5fbf', lw=1.2))
    # ô trap / bóng / kiệt sức: ô vuông tại đúng mức giá
    for typ, (desc, k, pt) in sg.items():
        if pt is None or typ == 'delta':
            continue
        ax.add_patch(plt.Rectangle((k - 0.45, pt * TICK - 0.05), 0.9, 0.1, fill=False, ec=PC.SIGN_COLOR[typ], lw=2.0, zorder=6))
    if int(r.S):
        ax.add_patch(plt.Rectangle((int(r.S_nen) - 0.45, r.S_lo), c - int(r.S_nen) + 0.9, r.S_hi - r.S_lo, color='#1f5fbf',
                                   alpha=0.18, zorder=0))
    risk = (r.entry - r.sl_S2) * D * TICK
    ax.text(0.005, 0.99, f"vào {r.entry * TICK:.1f} · SL {r.sl_S2 * TICK:.1f} · TP {r.tp_S2 * TICK:.1f} · rủi ro {risk:.1f} giá "
            f"({risk / (r.mbr_c * TICK):.2f} mbr) · cạnh E {E:.1f} · range {bot:.1f}–{top:.1f}",
            transform=ax.transAxes, fontsize=8, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#999', alpha=0.9))
    side = 'BUY' if D > 0 else 'SELL'
    ax.set_title(f"{combo} · idx {c} · CF {str(r.t_utc)[:16]} UTC ({str(r.t_vn)[11:16]} VN) · {side} · leg {int(r.leg)} · "
                 f"cờ {flags_of(r)} · {r.outcome_alone} R={float(r.r_alone):+.2f}"
                 + (' · range DEAD-ngay' if int(r.b_from_exhausted) else ''), fontsize=9.5)
    # luôn thấy đủ SL / TP / cạnh E (plot_corven chỉ nới trục khi mức nằm trong 3 giá quanh nến)
    lv = [r.sl_S2 * TICK, r.tp_S2 * TICK, E]
    y0 = min([y0] + [v - 0.6 for v in lv])
    y1 = max([y1] + [v + 0.6 for v in lv])
    ax.set_ylim(y0, y1)
    fig.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    fn = os.path.join(outdir, f"{kind}_{c}.png")
    fig.savefig(fn, dpi=85)
    plt.close(fig)
    return fn


def spread(x: pd.DataFrame, k=5) -> pd.DataFrame:
    if len(x) <= k:
        return x
    return x.iloc[np.linspace(0, len(x) - 1, k).round().astype(int)]


def pick(combo: str, t: pd.DataFrame):
    """F7/F10: mọi SL + 5 TP rải đều; F1: cả 11 lệnh."""
    t = t.sort_values('idx_c')
    if combo == 'F1':
        return [(r, r.outcome_alone) for r in t.itertuples()]
    out = [(r, 'SL') for r in t[t['outcome_alone'] == 'SL'].itertuples()]
    out += [(r, 'TP') for r in spread(t[t['outcome_alone'] == 'TP']).itertuples()]
    return out


def main(combos=('F7', 'F10', 'F1')):
    df, f = load_bars_train()
    cnt = {}
    for combo in combos:
        t = pd.read_csv(os.path.join(REPORT, f'_follow_trades_{combo}.csv'))
        od = os.path.join(SHOTS, combo)
        if os.path.isdir(od):
            for old in os.listdir(od):
                if old.endswith('.png'):
                    os.remove(os.path.join(od, old))
        n = {}
        for r, kind in pick(combo, t):
            plot_follow_trade(df, f, r, combo, od, kind)
            n[kind] = n.get(kind, 0) + 1
        cnt[combo] = n
        print(combo, n, '→', od)
    return cnt


if __name__ == '__main__':
    main()
