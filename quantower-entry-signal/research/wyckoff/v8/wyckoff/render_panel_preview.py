"""Mô phỏng BẢNG TƯƠNG TÁC mới của WyckoffRunner (2 danh sách cuộn được + kính lúp).

Không phải test logic — chỉ dựng lại ĐÚNG công thức layout trong WyckoffRunner.cs (UiPanel.Draw)
bằng Pillow để soi UI/UX trước khi mang lên Quantower (máy Linux không chạy System.Drawing được).

Chạy:  python3 render_panel_preview.py [thu-muc-xuat]
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1500, 900                      # kích thước "chart"
BG = (22, 24, 28)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

f = ImageFont.truetype(MONO, 12)      # ~ Consolas 9pt
fb = ImageFont.truetype(MONOB, 12)
fsmall = ImageFont.truetype(SANS, 11)
ftitle = ImageFont.truetype(SANSB, 13)

LINE_H = 17.0                          # f.Height + 2
ROW_H = 2 * LINE_H + 3                 # khớp UiPanel.Draw
TITLE_H = LINE_H + 6
PAD = 6.0
PANEL_W = 640

LONG = (0x26, 0xC6, 0xDA)
SHORT = (0xEF, 0x53, 0x50)
ACC = (0x4C, 0xAF, 0x50)
DIST = (0xE5, 0x39, 0x35)

HEADER = [
    ("WYCKOFF RUNNER CBR+VWAP v6 (M1)   ▶38 ↩12 · ✓19 ✗23 •8 · WR 45%  [CBR 3R · quay đầu 1.5R]", (255, 255, 255)),
    ("Lời/lỗ: +48.0R (1 lot) · TB +1.14R/lệnh (42 lệnh đóng)", (120, 230, 150)),
    ("📨 Tele: đã gửi 3 tin (mới nhất 14:02)", (150, 210, 255)),
    ("🧭 Bấm 1 dòng = nhảy chart tới đó · nháy đúp dòng Range = kính lúp · nhảy chart: OK (RightOffset)",
     (170, 195, 225)),
]

ENTRIES = [
    ("✓ ▶ 31/07 14:22 LONG A · E 4102.3 SL 4098.1 (4.2giá) TP 4114.9 (3.0R)",
     "     phá vùng co · nền SẠCH · hồi 72% · VWAP dưới · VSA 1.4", LONG),
    ("✗ ↩ 31/07 09:05 SHORT B · E 4131.8 SL 4136.0 (4.2giá) TP 4125.5 (1.5R)",
     "     quay đầu tại VWAP · hợp lưu ×2 · VSA 2.3 climax", SHORT),
    ("• ▶ 30/07 22:41 LONG A · E 4088.6 SL 4084.9 (3.7giá) TP 4099.7 (3.0R)",
     "     phá vùng co · thuận xu hướng · thanh khoản 0.91", LONG),
    ("✓ ▶ 30/07 16:10 SHORT A · E 4144.2 SL 4148.8 (4.6giá) TP 4130.4 (3.0R)",
     "     phá vùng co · nền SẠCH · hồi 64%", SHORT),
    ("✗ ↩ 30/07 11:58 LONG C · E 4071.0 SL 4067.2 (3.8giá) TP 4076.7 (1.5R)",
     "     quay đầu tại VWAP · ngược xu hướng ngày · VSA 1.2", LONG),
]

RANGES = [
    ("▼ PHÂN PHỐI · 29/07 18:30 → 31/07 07:15 (1245 nến)  ⏳ đang chạy",
     "     4118.4–4152.9 (34.5 giá) · Phase A→B→C→D · 9 mốc: BCLX AR ST UT DA UTAD SOW LPSY[D] …", DIST),
    ("▲ TÍCH LUỸ · 24/07 03:05 → 27/07 21:40 (2210 nến)",
     "     4042.1–4079.8 (37.7 giá) · Phase A→B→C→D→E · 11 mốc: SC AR ST UA Spring LPS[C] SOS LPS[D] …", ACC),
    ("▼ PHÂN PHỐI · 18/07 12:00 → 21/07 05:25 (1890 nến)",
     "     4160.0–4193.6 (33.6 giá) · Phase A→B→D→E · 7 mốc: BCLX AR ST DA SOW LPSY[D]", DIST),
    ("▲ TÍCH LUỸ · 11/07 07:45 → 14/07 19:10 (2044 nến)",
     "     3998.5–4031.2 (32.7 giá) · Phase A→B→C · 8 mốc: SC AR ST UA Shakeout LPS[C] ST", ACC),
    ("▼ PHÂN PHỐI · 04/07 20:15 → 08/07 02:50 (1702 nến)",
     "     4205.3–4240.1 (34.8 giá) · Phase A→B→C→D→E · 12 mốc: BCLX AR ST DA UT UTAD SOW LPSY[D] …", DIST),
    ("▲ TÍCH LUỸ · 30/06 05:00 → 02/07 23:35 (1415 nến)",
     "     3960.8–3992.4 (31.6 giá) · Phase A→B → bỏ (vượt trần chiều cao)", ACC),
]


def fit(d, text, font, max_w):
    if d.textlength(text, font=font) <= max_w:
        return text
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if d.textlength(text[:mid] + "…", font=font) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo] + "…"


def rr(d, box, fill=None, outline=None, width=1):
    d.rectangle(box, fill=fill, outline=outline, width=width)


def draw_section(d, x, y, bw, title, hint, rows, scroll, vis, hover, sel):
    """Trả về y mới. Khớp 1-1 với vòng lặp section trong UiPanel.Draw."""
    rr(d, [x + 1, y, x + bw - 1, y + TITLE_H], fill=(46, 46, 52))
    d.line([x + 1, y, x + bw - 1, y], fill=(70, 70, 78))
    t = ("▾ " + title + f"  ({len(rows)})" +
         (f"   ⇕ lăn chuột {scroll+1}-{min(len(rows), scroll+vis)}" if len(rows) > vis else ""))
    d.text((x + 6, y + 2), fit(d, t, fb, bw * 0.62), font=fb, fill=(235, 235, 245))
    if hint:
        d.text((x + bw * 0.64, y + 3), fit(d, hint, fsmall, bw * 0.36 - 10), font=fsmall, fill=(140, 150, 165))
    y += TITLE_H

    bar = len(rows) > vis
    view = [x + 2, y, x + bw - 2, y + vis * ROW_H]
    list_w = (view[2] - view[0]) - (11 if bar else 4)
    for k in range(vis):
        ri = scroll + k
        if ri >= len(rows):
            break
        l1, l2, col = rows[ri]
        ry = y + k * ROW_H
        box = [view[0], ry, view[0] + list_w, ry + ROW_H]
        is_hover, is_sel = (ri == hover), (ri == sel)
        if is_sel:
            rr(d, box, fill=tuple(int(c * 0.27 + 20) for c in col))
            rr(d, [box[0], ry, box[0] + 3, ry + ROW_H], fill=col)
        elif is_hover:
            rr(d, box, fill=(52, 54, 60))
            rr(d, [box[0], ry, box[0] + 3, ry + ROW_H], fill=tuple(int(c * 0.6) for c in col))
        d.text((box[0] + 8, ry + 2), fit(d, l1, f, list_w - 14), font=f, fill=col)
        c2 = (220, 220, 220) if (is_hover or is_sel) else (190, 190, 190)
        d.text((box[0] + 8, ry + 2 + LINE_H), fit(d, l2, f, list_w - 14), font=f, fill=c2)
        d.line([box[0] + 4, ry + ROW_H - 1, box[2] - 4, ry + ROW_H - 1], fill=(44, 46, 50))

    if bar:
        tx = view[2] - 9
        d.rectangle([tx, y + 1, tx + 7, view[3] - 1], fill=(46, 48, 54))
        th = max(20, (view[3] - y - 2) * vis / len(rows))
        pos = scroll / max(1, len(rows) - vis)
        ty = y + 1 + (view[3] - y - 2 - th) * pos
        d.rectangle([tx, ty, tx + 7, ty + th], fill=(150, 160, 180))
    return view[3] + 4


def main(outdir):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # nền giả lập nến cho thấy bảng đè lên chart
    import random
    random.seed(7)
    px = 4020.0
    for i in range(0, W, 6):
        px += random.uniform(-4, 4)
        yv = H / 2 - (px - 4020) * 6
        d.line([i, yv - random.uniform(4, 22), i, yv + random.uniform(4, 22)], fill=(58, 62, 70))

    n_head = len(HEADER)
    head_h = PAD + n_head * LINE_H
    e_vis, r_vis = 4, 5
    bh = head_h + PAD + (TITLE_H + e_vis * ROW_H + 4) + (TITLE_H + r_vis * ROW_H + 4)
    x, y0 = 8, 8
    rr(d, [x, y0, x + PANEL_W, y0 + bh], fill=(18, 18, 22), outline=(110, 110, 118))

    y = y0 + PAD
    for text, col in HEADER:
        d.text((x + PAD, y), fit(d, text, f, PANEL_W - 2 * PAD - 19), font=f, fill=col)
        y += LINE_H
    # nút thu gọn
    tg = [x + PANEL_W - 18, y0 + 3, x + PANEL_W - 3, y0 + 18]
    rr(d, tg, fill=(55, 55, 60), outline=(120, 120, 128))
    cx, cy = (tg[0] + tg[2]) / 2, (tg[1] + tg[3]) / 2
    d.line([cx - 4, cy - 2.5, cx, cy + 3], fill=(220, 220, 220), width=2)
    d.line([cx, cy + 3, cx + 4, cy - 2.5], fill=(220, 220, 220), width=2)

    y = draw_section(d, x, y, PANEL_W, "LỆNH", "bấm = nhảy chart", ENTRIES, 0, e_vis, hover=2, sel=-1)
    y = draw_section(d, x, y, PANEL_W, "WYCKOFF RANGE", "bấm = nhảy · nháy đúp = kính lúp",
                     RANGES, 0, r_vis, hover=-1, sel=1)

    # ---- KÍNH LÚP (khung bên phải, mô phỏng bố cục DrawInspector) ----
    ix, iy = 700, 120
    iw, ih = 760, 430
    rr(d, [ix, iy, ix + iw, iy + ih], fill=(14, 14, 17), outline=ACC, width=2)
    rr(d, [ix + 1, iy + 1, ix + iw - 1, iy + 27], fill=(40, 70, 45))
    d.text((ix + 8, iy + 5), "🔍 TÍCH LUỸ · 24/07 03:05 → 27/07 21:40 · 4042.1–4079.8 · 11 mốc · 2210 nến",
           font=ftitle, fill=(255, 255, 255))
    cb = [ix + iw - 24, iy + 4, ix + iw - 6, iy + 22]
    rr(d, cb, fill=(70, 70, 70))
    d.line([cb[0] + 5, cb[1] + 5, cb[2] - 5, cb[3] - 5], fill=(255, 255, 255), width=2)
    d.line([cb[2] - 5, cb[1] + 5, cb[0] + 5, cb[3] - 5], fill=(255, 255, 255), width=2)

    plot = [ix + 10, iy + 30, ix + iw - 72, iy + ih - 24]
    for k in range(5):
        yy = plot[3] - (plot[3] - plot[1]) * k / 4
        d.line([plot[0], yy, plot[2], yy], fill=(48, 50, 56))
        d.text((plot[2] + 4, yy - 7), f"{4038 + k*11:.1f}", font=fsmall, fill=(170, 180, 190))
    random.seed(3)
    pxx = 4055.0
    n = 160
    bw_ = (plot[2] - plot[0]) / n
    for i in range(n):
        pxx += random.uniform(-2.2, 2.2)
        o = pxx
        c = pxx + random.uniform(-1.6, 1.6)
        hi_ = max(o, c) + random.uniform(0.2, 1.4)
        lo_ = min(o, c) - random.uniform(0.2, 1.4)
        def yy(p):
            return plot[3] - (p - 4036) / (4082 - 4036) * (plot[3] - plot[1])
        xx = plot[0] + (i + 0.5) * bw_
        up = c >= o
        colc = (90, 200, 130) if up else (220, 100, 100)
        d.line([xx, yy(hi_), xx, yy(lo_)], fill=colc)
        d.rectangle([xx - bw_ * 0.35, yy(max(o, c)), xx + bw_ * 0.35, yy(min(o, c))], fill=colc)
        pxx = c

    def yy(p):
        return plot[3] - (p - 4036) / (4082 - 4036) * (plot[3] - plot[1])
    d.line([plot[0] + 20, yy(4042.1), plot[2] - 20, yy(4042.1)], fill=ACC, width=3)
    d.line([plot[0] + 20, yy(4079.8), plot[2] - 20, yy(4079.8)], fill=ACC, width=3)
    d.text((plot[2] - 16, yy(4079.8) - 8), "Tích luỹ", font=ftitle, fill=ACC)

    CAT = {"SC": (255, 82, 82), "AR": (129, 199, 132), "ST": (176, 190, 197), "UA": (176, 190, 197),
           "Spring": (255, 202, 40), "LPS[C]": (38, 198, 168), "SOS": (66, 165, 245), "LPS[D]": (186, 104, 200)}
    marks = [(0.06, 4042.1, "SC"), (0.14, 4074.0, "AR"), (0.24, 4045.5, "ST"), (0.36, 4071.2, "UA"),
             (0.50, 4038.4, "Spring"), (0.60, 4050.0, "LPS[C]"), (0.72, 4080.5, "SOS"), (0.84, 4072.6, "LPS[D]")]
    placed = []
    for fx, price, lab in marks:
        mx = plot[0] + (plot[2] - plot[0]) * fx
        my = yy(price)
        col = CAT[lab]
        d.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill=col, outline=(255, 255, 255))
        above = lab in ("AR", "ST", "UA", "SOS")
        ty = my - 22 if above else my + 8
        tw = d.textlength(lab, font=fb) + 6
        boxr = [mx - 9, ty, mx - 9 + tw, ty + 16]
        while any(not (boxr[2] < p[0] or boxr[0] > p[2] or boxr[3] < p[1] or boxr[1] > p[3]) for p in placed):
            boxr[1] -= 18
            boxr[3] -= 18
        placed.append(list(boxr))
        rr(d, boxr, fill=(20, 20, 24), outline=col)
        d.text((boxr[0] + 3, boxr[1] + 1), lab, font=fb, fill=col)
    for fx, ph in [(0.02, "A"), (0.18, "B"), (0.46, "C"), (0.68, "D"), (0.9, "E")]:
        mx = plot[0] + (plot[2] - plot[0]) * fx
        for seg in range(int(yy(4079.8)), int(yy(4042.1)), 9):
            d.line([mx, seg, mx, seg + 5], fill=(150, 150, 220))
        d.text((mx + 3, yy(4079.8) - 24), f"Phase {ph}", font=ftitle, fill=(150, 150, 220))
    d.text((plot[0], iy + ih - 20), "24/07 03:05", font=fsmall, fill=(160, 170, 185))
    d.text((plot[2] - 78, iy + ih - 20), "27/07 21:40", font=fsmall, fill=(160, 170, 185))
    d.text((plot[0] + (plot[2] - plot[0]) * 0.36, iy + ih - 20),
           "nháy đúp lại dòng trong bảng (hoặc ✕) để đóng", font=fsmall, fill=(160, 170, 185))

    out = Path(outdir) / "panel_preview.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
