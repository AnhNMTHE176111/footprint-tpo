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

SCRATCH = "/tmp/claude-1000/-home-asl86-Documents-footprint-tpo/5aedb1ee-2e24-4fe9-80ad-7c0820903a41/scratchpad"

W_IMG, H_IMG = 1900, 900
PAD_L, PAD_R, PAD_T, PAD_B = 70, 140, 40, 40
BG = (18, 18, 22)
GRID = (40, 40, 46)
UP_C = (0x26, 0xC6, 0xDA)
DN_C = (0xEF, 0x53, 0x50)
RANGE_C = (0xFF, 0xB3, 0x00)
PHASE_C = (150, 150, 220)
TXT = (235, 235, 235)


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
    y_top = yp(r.high)
    y_bot = yp(r.low)
    for ph, ps, pe in r.phases:
        xps = xk(k_of(ps))
        dash = 6
        yy = y_top
        while yy < y_bot:
            d.line([(xps, yy), (xps, min(yy + dash, y_bot))], fill=PHASE_C, width=2)
            yy += dash * 2
        d.text((xps + 3, y_top - 22), f"Phase {ph}", fill=PHASE_C, font=font)

    # ---- nhan su kien ----
    for ev in r.events:
        k = k_of(ev['i'])
        if k < 0 or k >= n:
            continue
        x = xk(k)
        y = yp(ev['price'])
        above = ev['label'] in ('SOS', 'AR', 'ST', 'UT', 'UTAD', 'BCLX')
        ty = y - 26 if above else y + 12
        d.ellipse([x - 3, y - 3, x + 3, y + 3], outline=(255, 255, 255))
        d.text((x - 10, ty), ev['label'], fill=(255, 230, 150), font=font)

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
