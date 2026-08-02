#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_schematic_preview.py — ve 1 range da phat hien (wyckoff_schematic.detect) ra PNG bang
Pillow de KIEM TRUC QUAN truoc khi port sang C#. Mo phong DUNG rang buoc render nguoi dung yeu
cau cho WyckoffRunner.cs: duong ngang bien range CHI ve trong pham vi thoi gian cua range (khong
keo het chart), duong doc chia phase net dut CHI ve trong pham vi gia cua range (khong keo het
chieu cao chart).

Chay: python3 render_schematic_preview.py [chi_so_range]   (mac dinh: range dai nhat)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, HERE)
sys.path.insert(0, RESEARCH)

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
import entry_dxfeed as E  # noqa: E402
import wyckoff_schematic as W  # noqa: E402

SCRATCH = "/tmp/claude-1000/-home-asl86-Documents-footprint-tpo/385f4fcf-16db-40f8-9295-6f45fba09fa4/scratchpad"

W_IMG, H_IMG = 1900, 900
PAD_L, PAD_R, PAD_T, PAD_B = 70, 140, 40, 40
BG = (18, 18, 22)
GRID = (40, 40, 46)
UP_C = (0x26, 0xC6, 0xDA)
DN_C = (0xEF, 0x53, 0x50)
RANGE_C = (0xFF, 0xB3, 0x00)
PHASE_C = (150, 150, 220)
TXT = (235, 235, 235)
BOX_BG = (26, 26, 32)

# UI/UX — mỗi HỌ sự kiện 1 màu riêng để đọc nhanh trên chart bận nến (yêu cầu "show chữ rõ ràng"):
# Climax = đỏ cam mạnh (biến cố khởi đầu), AR = xanh lá (phản ứng đầu tiên), ST/UA/DA = xám xanh (test
# trung tính — UA/DA là test cạnh "kia", spec §1.10), Spring/Shakeout/UT/UTAD = vàng (cú rung — quan
# trọng nhất, dễ hiểu lầm nhất), SOS/SOW = xanh dương (xác nhận phá vỡ), LPS[C]/LPSY[C] = tím nhạt
# (test trong lúc chờ xác nhận shock — spec CR-M), LPS[D]/LPSY[D] = tím đậm (pullback sau SOS/SOW).
EVENT_CATEGORY = {
    "SC": "climax", "BCLX": "climax",
    "AR": "ar",
    "ST": "st", "UA": "st", "DA": "st",
    "Spring": "shake", "Shakeout": "shake", "UT": "shake", "UTAD": "shake",
    "SOS": "break", "SOW": "break",
    "LPS[C]": "lpsc", "LPSY[C]": "lpsc",
    "LPS[D]": "lpsd", "LPSY[D]": "lpsd",
}
CAT_COLOR = {
    "climax": (255, 82, 82),
    "ar": (129, 199, 132),
    "st": (176, 190, 197),
    "shake": (255, 202, 40),
    "break": (66, 165, 245),
    # giang vien-agent cham: LPS[C] (tim nhat) vs LPS[D] (tim dam) qua giong mau mat thuong, mat tac
    # dung phan biet — day la tinh nang su pham CHINH cua CR-M (dung 1 sac do KHAC HAN thay vi dam/nhat).
    "lpsc": (38, 198, 168),       # xanh ngoc (LPS[C] — con dang cho xac nhan, Phase C)
    "lpsd": (186, 104, 200),      # tim (LPS[D] — da xac nhan, Phase D)
}
CAT_LEGEND = [
    ("climax", "SC / BCLX — Climax"),
    ("ar", "AR — phản ứng"),
    ("st", "ST/UA/DA — test"),
    ("shake", "Spring/Shakeout/UT/UTAD"),
    ("break", "SOS/SOW — phá vỡ"),
    ("lpsc", "LPS[C] — test chờ xác nhận"),
    ("lpsd", "LPS[D] — vào lại sau phá"),
]
# Trạng thái shock (chỉ Spring/Shakeout/UT/UTAD có, spec §3.8 điểm 4): Confirmed=viền đặc dày,
# Pending=viền đứt nét, Failed=rỗng/xám kèm hậu tố "(thất bại)" đã có sẵn trong label.
STATUS_STYLE = {
    "confirmed": dict(width=3, dash=False, grey=False),
    "pending": dict(width=1, dash=True, grey=False),
    "failed": dict(width=1, dash=False, grey=True),
}


def cat_of(label):
    base = label.split("(")[0].strip()
    return EVENT_CATEGORY.get(label) or EVENT_CATEGORY.get(base) or "st"


def render(B, r, pad_bars=40, out_path=None):
    end_i = r.end_i if r.end_i is not None else min(len(B) - 1, r.start_i + 2000)
    lo_i = max(0, r.start_i - pad_bars)
    hi_i = min(len(B) - 1, end_i + pad_bars)
    win = B[lo_i:hi_i + 1]
    n = len(win)

    ymin = min(x['lo'] for x in win)
    ymax = max(x['hi'] for x in win)
    ypad = (ymax - ymin) * 0.08
    ymin -= ypad
    ymax += ypad

    img = Image.new("RGB", (W_IMG, H_IMG), BG)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except Exception:
        font = ImageFont.load_default()
        font_s = font

    def xk(k):  # k = index trong win
        return PAD_L + (W_IMG - PAD_L - PAD_R) * k / max(1, n - 1)

    def yp(price):
        return PAD_T + (H_IMG - PAD_T - PAD_B) * (1 - (price - ymin) / (ymax - ymin))

    # UI/UX: nhãn LUÔN có nền hộp bo góc (không vẽ chữ trần lên nến) + né chồng lấp theo cả x lẫn y.
    _placed_boxes = []

    def label_box(x, y, text, color, f=None, anchor_left=True):
        f = f or font
        bbox = d.textbbox((0, 0), text, font=f)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad = 3
        bx0 = x if anchor_left else x - tw - 2 * pad
        by0 = y
        bw, bh = tw + 2 * pad, th + 2 * pad + 2
        guard = 0
        while guard < 40 and any(not (bx0 + bw < ox or ox + ow < bx0 or by0 + bh < oy or oy + oh < by0)
                                  for (ox, oy, ow, oh) in _placed_boxes):
            by0 -= bh + 2
            guard += 1
        _placed_boxes.append((bx0, by0, bw, bh))
        d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=4, fill=BOX_BG, outline=color, width=1)
        d.text((bx0 + pad, by0 + pad - 1), text, fill=color, font=f)
        return bx0, by0, bw, bh

    # gridlines gia
    for gi in range(6):
        price = ymin + (ymax - ymin) * gi / 5
        yy = yp(price)
        d.line([(PAD_L, yy), (W_IMG - PAD_R, yy)], fill=GRID, width=1)
        d.text((W_IMG - PAD_R + 6, yy - 6), f"{price:.1f}", fill=TXT, font=font_s)

    # nen
    for k, b in enumerate(win):
        x = xk(k)
        col = UP_C if b['c'] >= b['o'] else DN_C
        d.line([(x, yp(b['hi'])), (x, yp(b['lo']))], fill=col, width=1)
        yo, yc = yp(b['o']), yp(b['c'])
        top, bot = min(yo, yc), max(yo, yc)
        if bot - top < 1:
            bot = top + 1
        d.rectangle([x - 2.2, top, x + 2.2, bot], fill=col)

    def k_of(i):
        return i - lo_i

    # ---- duong ngang bien range: CHI trong pham vi [start_i .. end_i] cua CHINH range nay ----
    x0 = xk(k_of(r.start_i))
    x1 = xk(k_of(min(end_i, hi_i)))
    for price, lab in ((r.low, "Range Low"), (r.high, "Range High")):
        yy = yp(price)
        d.line([(x0, yy), (x1, yy)], fill=RANGE_C, width=2)
        d.text((x1 + 4, yy - 7), lab, fill=RANGE_C, font=font_s)

    # ---- duong doc chia PHASE: net dut, CHI trong pham vi GIA [range.low..range.high] ----
    # CR-W: ranh gioi Phase qua gan nhau (<= PHASE_LABEL_COLLISION_BARS) -> gop 1 nhan "B→C→D" thay
    # vi ve chong nhieu chuoi text (van ve DAY DU tung duong net dut rieng, chi gop CHU).
    PHASE_LABEL_COLLISION_BARS = 2
    y_top = yp(r.high)
    y_bot = yp(r.low)
    phases_sorted = sorted(r.phases, key=lambda p: p[1])
    clusters = []
    for ph, ps, pe in phases_sorted:
        xps = xk(k_of(ps))
        dash = 6
        yy = y_top
        while yy < y_bot:
            d.line([(xps, yy), (xps, min(yy + dash, y_bot))], fill=PHASE_C, width=2)
            yy += dash * 2
        if clusters and (ps - clusters[-1][-1][1]) <= PHASE_LABEL_COLLISION_BARS:
            clusters[-1].append((ph, ps))
        else:
            clusters.append([(ph, ps)])
    for cluster in clusters:
        xps = xk(k_of(cluster[0][1]))
        text = "→".join(ph for ph, _ in cluster)
        label_box(xps + 3, y_top - 24, f"Phase {text}", PHASE_C, f=font)

    # ---- nhan su kien: mau theo HO su kien + hop nen + ne chong lap (yeu cau UI/UX "show chu ro rang") ----
    for ev in sorted(r.events, key=lambda e: e['i']):
        k = k_of(ev['i'])
        if k < 0 or k >= n:
            continue
        x = xk(k)
        y = yp(ev['price'])
        cat = cat_of(ev['label'])
        color = CAT_COLOR[cat]
        above = cat in ('ar', 'st', 'break')
        ty = y - 24 if above else y + 8
        # marker theo trang thai shock (Confirmed/Pending/Failed — spec §3.8 diem 4)
        style = STATUS_STYLE.get(ev.get('status'), None)
        mcolor = (140, 140, 140) if (style and style['grey']) else color
        if style and style['dash']:
            # vien dut cho Pending: ve 4 cung ngan thay vi vien lien
            for a0 in (0, 90, 180, 270):
                d.arc([x - 4, y - 4, x + 4, y + 4], a0, a0 + 45, fill=(255, 255, 255), width=1)
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=mcolor)
        else:
            w = style['width'] if style else 1
            d.ellipse([x - 3.5, y - 3.5, x + 3.5, y + 3.5], fill=mcolor, outline=(255, 255, 255), width=w)
        bx, by, bw, bh = label_box(x - 9, ty, ev['label'], color if not (style and style['grey']) else mcolor, f=font)
        # leader line: nhan bi day xa khoi diem su kien (do ne chong lap) -> ve duong noi mong de biet
        # nhan nao thuoc su kien nao (CR-W)
        by_mid = by + bh / 2
        if abs(by_mid - ty - (font.size / 2 if hasattr(font, "size") else 7)) > 18 or abs(bx + bw / 2 - x) > 40:
            d.line([(x, y), (bx + bw / 2, by_mid)], fill=(100, 100, 100), width=1)

    # ---- chu giai mau theo ho su kien (goc tren phai) ----
    # giang vien-agot cham: legend khong co nen -> bi nen chart de len, kho doc. Them nen duc mo.
    lx, ly = W_IMG - PAD_R - 260, PAD_T + 4
    legend_h = 18 * len(CAT_LEGEND) + 4
    d.rectangle([lx - 6, ly - 4, W_IMG - PAD_R + 4, ly + legend_h], fill=(16, 16, 19))
    for cat, desc in CAT_LEGEND:
        d.ellipse([lx, ly + 3, lx + 8, ly + 11], fill=CAT_COLOR[cat])
        d.text((lx + 14, ly), desc, fill=TXT, font=font_s)
        ly += 18

    title = f"{r.kind}  {B[r.start_i]['dt']} -> {B[end_i]['dt']}  ({r.status})"
    d.text((PAD_L, 10), title, fill=TXT, font=font)

    if out_path is None:
        out_path = os.path.join(SCRATCH, "wyckoff_schematic_preview.png")
    img.save(out_path)
    print(f"da ve -> {out_path}  ({n} nen, range={r.start_i}..{end_i})")
    return out_path


def main():
    B = E.load_m1()
    ranges = W.detect(B)
    if not ranges:
        print("khong phat hien range nao")
        return
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if idx is None:
        r = max(ranges, key=lambda r: (r.end_i or len(B) - 1) - r.start_i)
    else:
        r = ranges[idx]
    render(B, r)


if __name__ == '__main__':
    main()
