#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v8/entry/sl_review.py — xuat MD liet ke TAT CA lenh dinh SL cua EntrySignal (config
dang SHIP, pool cu, dxFeed 3 thang 5-7/2026) de nguoi dung doi chieu tung lenh voi
chart that. Dung LAI harness.py (P0 TRUOC) + entry_dxfeed.py, KHONG sua file goc.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, RESEARCH)
sys.path.insert(0, HERE)

import entry_dxfeed as E             # noqa: E402
from harness import load_dx, warmup_cutoff, MONTHS  # noqa: E402

SCEN_VN = {
    '1 pha&hoi len': 'KB1 phá&hồi LÊN',
    '1 pha&hoi xuong': 'KB1 phá&hồi XUỐNG',
    '2 cham&dao len': 'KB2 chạm&đảo LÊN',
    '2 cham&dao xuong': 'KB2 chạm&đảo XUỐNG',
}


def sim_time(B, s, tpkey, RR_fallback):
    """Giong entry_dxfeed.sim() nhung tra THEM gio nen dinh SL/TP (OutTime) de doi
    chieu chart. Khong sua entry_dxfeed.py (READ-ONLY)."""
    i = s['i']; side = s['side']; sl = s['sl']; tp = s[tpkey]
    rr = s['rx'] if tpkey == 'tpx' else RR_fallback
    for j in range(i + 1, len(B)):
        hb = B[j]
        hitSL = (hb['lo'] <= sl) if side == 'LONG' else (hb['hi'] >= sl)
        hitTP = (hb['hi'] >= tp) if side == 'LONG' else (hb['lo'] <= tp)
        if hitSL and hitTP:
            return 'amb', -1.0, hb['dt']
        if hitSL:
            return 'SL', -1.0, hb['dt']
        if hitTP:
            return 'TP', rr, hb['dt']
    return 'open', 0.0, None


def build():
    B, pool = load_dx()
    C = E.make(VOL_FLOOR=E.VOLFLOOR_FROZEN)
    raw = E.run(B, pool, C)
    sig = E.dedup(raw, pool, C)
    sig = [s for s in sig if s['ym'] in MONTHS]
    cutoff = warmup_cutoff(B)
    if cutoff is not None:
        sig = [s for s in sig if s['dt'].date() >= cutoff]
    for s in sig:
        o, r, outdt = sim_time(B, s, 'tp3', C['RR'])
        s['outcome'] = o; s['r'] = r; s['outdt'] = outdt
    sig.sort(key=lambda s: s['dt'])
    return sig


def fmt_dt(dt):
    return dt.strftime('%Y-%m-%d %H:%M') if dt else '(chưa chạm SL/TP)'


def main():
    sig = build()
    sl_list = [s for s in sig if s['outcome'] == 'SL']
    amb_list = [s for s in sig if s['outcome'] == 'amb']
    tp_n = sum(1 for s in sig if s['outcome'] == 'TP')

    out = []
    out.append("# Danh sách lệnh DÍNH SL — EntrySignal (M1), config đang ship\n")
    out.append(f"Nguồn: dxFeed `_GCQ26XCEC` 1 phút, cửa sổ 05-07/2026 (sau warm-up 5 ngày đầu tháng 5).")
    out.append(f"Tổng {len(sig)} lệnh: {len(sl_list)} dính SL, {tp_n} chạm TP, {len(amb_list)} nến "
                f"chạm CẢ SL lẫn TP cùng lúc (không phân định được thứ tự trong nến — liệt kê riêng ở cuối).\n")
    out.append("Giờ ghi theo cột `Time left` gốc dxFeed (UTC) — khớp trực tiếp giờ mở nến trên chart nếu "
                "chart cùng feed; nếu chart hiển thị giờ khác, cộng/trừ theo lệch múi giờ sàn của bạn.\n")
    out.append("Cách đọc cột **Vùng kích hoạt**: là vùng đã bắn KB1/KB2 (không phải toàn bộ vùng hợp lưu); "
                "cột **Hợp lưu** là số vùng khác nhau chồng lấp quanh giá vào (điều kiện MinConfluence≥2).\n")
    out.append("| STT | Giờ vào lệnh | Kịch bản | Hướng | Vùng kích hoạt | Entry | SL | TP (1.5R) | Giờ dính SL | Hợp lưu | VSA | Climax | Lý do nến vào |")
    out.append("|---:|---|---|:---:|---|---:|---:|---:|---|:---:|---:|:---:|---|")
    for k, s in enumerate(sl_list, 1):
        out.append(
            f"| {k} | {fmt_dt(s['dt'])} | {SCEN_VN.get(s['scen'], s['scen'])} | {s['side']} | "
            f"{s['zone']} | {s['entry']:.1f} | {s['sl']:.1f} | {s['tp3']:.1f} | {fmt_dt(s['outdt'])} | "
            f"{s['confl']} | {s['vsa']:.2f}x | {'có' if s['climax'] else 'không'} | {s['why']} |"
        )

    if amb_list:
        out.append("\n## Nến chạm CẢ SL lẫn TP cùng lúc (mơ hồ — cần xem chart để biết SL hay TP tới trước)\n")
        out.append("| STT | Giờ vào lệnh | Kịch bản | Hướng | Vùng kích hoạt | Entry | SL | TP (1.5R) | Giờ chạm | Hợp lưu | VSA |")
        out.append("|---:|---|---|:---:|---|---:|---:|---:|---|:---:|---:|")
        for k, s in enumerate(amb_list, 1):
            out.append(
                f"| {k} | {fmt_dt(s['dt'])} | {SCEN_VN.get(s['scen'], s['scen'])} | {s['side']} | "
                f"{s['zone']} | {s['entry']:.1f} | {s['sl']:.1f} | {s['tp3']:.1f} | {fmt_dt(s['outdt'])} | "
                f"{s['confl']} | {s['vsa']:.2f}x |"
            )

    RULE_DIR = os.path.normpath(os.path.join(RESEARCH, '..', '..', 'rule-entry'))  # repo-root/rule-entry (shared voi RunnerSignal)
    os.makedirs(RULE_DIR, exist_ok=True)
    path = os.path.join(RULE_DIR, 'EntrySignal-lenh-dinh-SL.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print(f"da ghi {path} | SL={len(sl_list)} TP={tp_n} amb={len(amb_list)} tong={len(sig)}")


if __name__ == '__main__':
    main()
