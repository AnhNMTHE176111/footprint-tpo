#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wyckoffrunner_sl_review.py — xuat MD liet ke TAT CA lenh DINH SL cua nhanh CBR (WyckoffRunner.cs,
config dang SHIP: CleanBreak=true, PullMax=1.00, RR=4.0), dxFeed 3 thang 5-7/2026, de nguoi dung
doi chieu tung lenh voi chart that. Hoc theo FORMAT/STYLE cua
v8/entry/sl_review.py -> rule-entry/EntrySignal-lenh-dinh-SL.md (doc-only, KHONG sua file do).

Dung lai KHONG SUA: cbr_v6.py (cfg/prepare/scan/run), entry_dxfeed.py (load_m1/calc_volfloor/
build_zones/cluster_count/VSA_CLIMAX/CONFLUENCE_TOL_T).

Chay: python3 wyckoffrunner_sl_review.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # .../wyckoff/v8/wyckoff
V8 = os.path.dirname(HERE)                                  # .../wyckoff/v8
WYCK = os.path.dirname(V8)                                  # .../research/wyckoff
RESEARCH = os.path.dirname(WYCK)                            # .../research
QES = os.path.dirname(RESEARCH)                             # .../quantower-entry-signal
ROOT = os.path.dirname(QES)                                 # repo root (footprint-tpo)
sys.path.insert(0, WYCK)
sys.path.insert(0, RESEARCH)

import cbr_v6 as V           # noqa: E402
import entry_dxfeed as E     # noqa: E402

CFG_TAG = "CleanBreak=true, PullMax=1.00, RR=4.0 (khớp mặc định WyckoffRunner.cs — xem BASELINE.md)"


def sim_time(B, s, tp, rr):
    """Nhu cbr_v6.evaluate() nhung tra THEM gio nen dinh SL/TP de doi chieu chart, va tach rieng
    ca 'amb' (1 nen cham CA SL lan TP, khong phan dinh duoc thu tu)."""
    i, side, sl = s['i'], s['side'], s['sl']
    for j in range(i + 1, len(B)):
        b = B[j]
        hitSL = (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl)
        hitTP = (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp)
        if hitSL and hitTP:
            return 'amb', -1.0, b['dt']
        if hitSL:
            return 'SL', -1.0, b['dt']
        if hitTP:
            return 'TP', rr, b['dt']
    return 'open', 0.0, None


def build():
    B = E.load_m1()
    vf = E.calc_volfloor(B)
    E.VOLFLOOR_AUTO = vf
    V.prepare(B)
    C = V.cfg(CLEAN=True, PMAX=1.00, RR=4.0)
    TICK = V.TICK

    raw = V.post(V.cooldown(V.dedup(V.run(B, C, vf, None)), C['COOL']), C)
    pool = E.build_zones(B)

    sig = []
    for s in sorted(raw, key=lambda x: x['i']):
        r = s['risk_t'] * TICK
        tp = s['entry'] + C['RR'] * r if s['side'] == 'LONG' else s['entry'] - C['RR'] * r
        o, rr_out, outdt = sim_time(B, s, tp, C['RR'])
        if o == 'open':
            continue
        s2 = dict(s)
        s2['tp'] = tp
        s2['outcome'] = o
        s2['r'] = rr_out
        s2['outdt'] = outdt
        s2['confl'] = E.cluster_count(dict(dt=s['dt'], entry=s['entry']), pool)
        climax = s['brk_vsa'] >= E.VSA_CLIMAX
        s2['climax'] = climax
        win = B[s['brk_i'] - C['RANGE_LEN']:s['brk_i']]
        edge = max(x['hi'] for x in win) if s['side'] == 'LONG' else min(x['lo'] for x in win)
        s2['edge'] = edge
        why = [f"phá {edge:.1f} (span {s['span']:.1f}tick)", f"hồi {s['retr']*100:.0f}%",
               f"VSA{s['brk_vsa']:.2f}x" + ("(tim)" if climax else "")]
        s2['why'] = ";".join(why)
        sig.append(s2)
    return sig


def fmt_dt(dt):
    return dt.strftime('%Y-%m-%d %H:%M') if dt else '(chưa chạm SL/TP)'


def main():
    sig = build()
    sl_list = [s for s in sig if s['outcome'] == 'SL']
    amb_list = [s for s in sig if s['outcome'] == 'amb']
    tp_n = sum(1 for s in sig if s['outcome'] == 'TP')

    out = []
    out.append("# Danh sách lệnh DÍNH SL — WyckoffRunner nhánh CBR (M1), config đang ship\n")
    out.append(f"Nguồn: dxFeed `_GCQ26XCEC` 1 phút, cửa sổ 05-07/2026. Cấu hình: {CFG_TAG}. Nhánh CBR "
               f"là nhánh DUY NHẤT đang bắn tín hiệu mặc định (nhánh QUAY ĐẦU VWAP đang TẮT — "
               f"`EnableReversal=false`, xem `wyckoffrunner-setup-va-kich-ban.md`).")
    out.append(f"Tổng {len(sig)} lệnh: {len(sl_list)} dính SL, {tp_n} chạm TP, {len(amb_list)} nến "
               f"chạm CẢ SL lẫn TP cùng lúc (không phân định được thứ tự trong nến — liệt kê riêng ở cuối).\n")
    out.append("Giờ ghi theo cột `Time left` gốc dxFeed (UTC) — khớp trực tiếp giờ mở nến trên chart nếu "
               "chart cùng feed; nếu chart hiển thị giờ khác (vd Quantower TzOffset=+7 = giờ VN), "
               "cộng/trừ theo lệch múi giờ sàn của bạn.\n")
    out.append("Cách đọc cột **Cạnh vùng co (phá)**: giá cạnh range nội bộ (8 nến trước) bị phá — CBR "
               "neo theo range nội bộ, KHÔNG phải zone volume-profile như EntrySignal; cột **Hợp lưu** "
               "vẫn là số vùng POC/VAH/VAL/Đỉnh/Đáy (phiên Á/Âu/Mỹ + D-1) chồng lấp quanh giá vào "
               "(ConfluenceTol=7 tick) — CHỈ hiển thị (Grade A/B), KHÔNG lọc/chặn lệnh nào.\n")
    out.append("| STT | Giờ vào lệnh | Kịch bản | Hướng | Cạnh vùng co (phá) | Entry | SL | TP (4R) | Giờ dính SL | Hợp lưu | VSA | Climax | Lý do nến vào |")
    out.append("|---:|---|---|:---:|---:|---:|---:|---:|---|:---:|---:|:---:|---|")
    for k, s in enumerate(sl_list, 1):
        out.append(
            f"| {k} | {fmt_dt(s['dt'])} | CBR phá→hồi→tiếp diễn | {s['side']} | {s['edge']:.1f} | "
            f"{s['entry']:.1f} | {s['sl']:.1f} | {s['tp']:.1f} | {fmt_dt(s['outdt'])} | "
            f"{s['confl']} | {s['brk_vsa']:.2f}x | {'có' if s['climax'] else 'không'} | {s['why']} |"
        )

    if amb_list:
        out.append("\n## Nến chạm CẢ SL lẫn TP cùng lúc (mơ hồ — cần xem chart để biết SL hay TP tới trước)\n")
        out.append("| STT | Giờ vào lệnh | Kịch bản | Hướng | Cạnh vùng co (phá) | Entry | SL | TP (4R) | Giờ chạm | Hợp lưu | VSA |")
        out.append("|---:|---|---|:---:|---:|---:|---:|---:|---|:---:|---:|")
        for k, s in enumerate(amb_list, 1):
            out.append(
                f"| {k} | {fmt_dt(s['dt'])} | CBR phá→hồi→tiếp diễn | {s['side']} | {s['edge']:.1f} | "
                f"{s['entry']:.1f} | {s['sl']:.1f} | {s['tp']:.1f} | {fmt_dt(s['outdt'])} | "
                f"{s['confl']} | {s['brk_vsa']:.2f}x |"
            )

    out.append(f"\n## Tổng kết\n")
    out.append(f"- n={len(sig)}, TP={tp_n}, SL={len(sl_list)}, amb={len(amb_list)} "
               f"→ WR={100*tp_n/len(sig):.1f}%, tổng={4.0*tp_n - 1.0*len(sl_list):+.1f}R "
               f"(khớp BASELINE.md nếu amb=0).")

    RULE_DIR = os.path.normpath(os.path.join(ROOT, 'rule-entry'))
    os.makedirs(RULE_DIR, exist_ok=True)
    path = os.path.join(RULE_DIR, 'WyckoffRunner-lenh-dinh-SL.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print(f"da ghi {path} | SL={len(sl_list)} TP={tp_n} amb={len(amb_list)} tong={len(sig)}")


if __name__ == '__main__':
    main()
