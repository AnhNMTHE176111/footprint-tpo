#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_range_for_grading.py — xuat MOI range do wyckoff_schematic.detect() tim ra thanh:
  (1) mot anh PNG "bai lam" (nen + khoi luong + bien chinh/phu + phase + nhan su kien)
  (2) mot file .md "phieu so lieu" di kem (so that, khong phai doc tu pixel)
de agent GIANG VIEN (.claude/agents/wyckoff-giao-vien.md) cham nhu cham bai hoc vien.

Khac render_schematic_preview.py: da cap nhat cho v4 (bien CHINH net lien = climax+AR co dinh,
bien PHU net dut = cuc tri xa nhat), co PANEL KHOI LUONG (giang vien Wyckoff cham effort-vs-result
bat buoc phai thay volume), va luon ve du context BEN TRAI de thay ca MOVE truoc climax.

Chay:
  python3 render_range_for_grading.py            -> xuat toan bo range ra thu muc mac dinh
  python3 render_range_for_grading.py 2026-07    -> chi range bat dau trong thang do
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
sys.path.insert(0, HERE)
sys.path.insert(0, RESEARCH)

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
import entry_dxfeed as E  # noqa: E402
import wyckoff_schematic as W  # noqa: E402

OUT_DIR = os.path.join(WYCK, "grading")

W_IMG, H_IMG = 2000, 1120
PAD_L, PAD_R, PAD_T = 78, 150, 58
VOL_H = 190              # chieu cao panel khoi luong
GAP_PANEL = 26
PAD_B = 34
BG = (18, 18, 22)
GRID = (40, 40, 46)
UP_C = (0x26, 0xC6, 0xDA)
DN_C = (0xEF, 0x53, 0x50)
SOLID_C = (0xFF, 0xB3, 0x00)     # bien CHINH
DASH_C = (0xB0, 0x86, 0x2E)      # bien PHU
PHASE_C = (150, 150, 220)
VWAP_C = (120, 130, 160)
TXT = (235, 235, 235)
DIM = (150, 150, 158)
BOX_BG = (26, 26, 32)

CAT = {
    "SC": "climax", "BCLX": "climax", "SC?": "climax", "BCLX?": "climax", "AR": "ar",
    "ST[A]": "st", "UT[B]": "st", "ST[B]": "st",
    "Spring": "shake", "Shakeout": "shake", "UTAD": "shake",
    "SOS": "break", "SOW": "break", "mSOS": "minor", "mSOW": "minor",
    "LPS[C]": "lpsc", "LPSY[C]": "lpsc",
    "LPS[D]": "lpsd", "LPSY[D]": "lpsd",
}
CAT_COLOR = {
    "climax": (255, 82, 82), "ar": (129, 199, 132), "st": (176, 190, 197),
    "shake": (255, 202, 40), "break": (66, 165, 245), "minor": (255, 167, 38),
    "lpsc": (38, 198, 168), "lpsd": (186, 104, 200),
}


def cat_of(label):
    base = label.split("(")[0].strip()
    return CAT.get(label) or CAT.get(base) or "st"


def _font(size, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    try:
        return ImageFont.truetype(p, size)
    except Exception:
        return ImageFont.load_default()


def render(B, r, out_png):
    end_i = r.end_i if r.end_i is not None else min(len(B) - 1, r.start_i + 2000)
    # context ben trai phai du thay CA MOVE truoc climax (luat "move xu huong truoc climax")
    left_ctx = 40 if r.move_i is None else max(40, (r.start_i - r.move_i) + 25)
    lo_i = max(0, r.start_i - left_ctx)
    hi_i = min(len(B) - 1, end_i + 45)
    win = B[lo_i:hi_i + 1]
    n = len(win)

    ymin = min(x['lo'] for x in win)
    ymax = max(x['hi'] for x in win)
    ypad = (ymax - ymin) * 0.06
    ymin -= ypad
    ymax += ypad
    vmax = max(x['v'] for x in win) or 1.0

    price_top = PAD_T
    price_bot = H_IMG - PAD_B - VOL_H - GAP_PANEL
    vol_top = H_IMG - PAD_B - VOL_H
    vol_bot = H_IMG - PAD_B

    img = Image.new("RGB", (W_IMG, H_IMG), BG)
    d = ImageDraw.Draw(img)
    f = _font(15, True)
    fs = _font(12)
    ft = _font(17, True)

    def xk(k):
        return PAD_L + (W_IMG - PAD_L - PAD_R) * k / max(1, n - 1)

    def yp(p):
        return price_top + (price_bot - price_top) * (1 - (p - ymin) / (ymax - ymin))

    def yv(v):
        return vol_bot - (vol_bot - vol_top) * (v / vmax)

    def k_of(i):
        return i - lo_i

    boxes = []

    def label_box(x, y, text, color, fo=None, dash=False):
        fo = fo or f
        bb = d.textbbox((0, 0), text, font=fo)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        pad = 3
        bx0, by0 = x, y
        bw, bh = tw + 2 * pad, th + 2 * pad + 3
        g = 0
        while g < 60 and any(not (bx0 + bw < ox or ox + ow < bx0 or by0 + bh < oy or oy + oh < by0)
                             for (ox, oy, ow, oh) in boxes):
            by0 -= bh + 2
            g += 1
        boxes.append((bx0, by0, bw, bh))
        d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=4, fill=BOX_BG,
                            outline=color, width=1)
        d.text((bx0 + pad, by0 + pad - 1), text, fill=color, font=fo)
        return bx0, by0, bw, bh

    def hline(y, x0, x1, color, dashed=False, width=2):
        if not dashed:
            d.line([(x0, y), (x1, y)], fill=color, width=width)
            return
        x = x0
        while x < x1:
            d.line([(x, y), (min(x + 9, x1), y)], fill=color, width=width)
            x += 18

    # ---- luoi gia ----
    for gi in range(7):
        p = ymin + (ymax - ymin) * gi / 6
        y = yp(p)
        d.line([(PAD_L, y), (W_IMG - PAD_R, y)], fill=GRID, width=1)
        d.text((W_IMG - PAD_R + 6, y - 6), f"{p:.1f}", fill=DIM, font=fs)

    # ---- moc thoi gian ----
    step = max(1, n // 12)
    for k in range(0, n, step):
        x = xk(k)
        d.line([(x, price_top), (x, price_bot)], fill=(30, 30, 36), width=1)
        d.text((x - 26, vol_bot + 6), win[k]['dt'].strftime("%m-%d %H:%M"), fill=DIM, font=fs)

    # ---- nen + volume ----
    bw_px = max(1.6, (W_IMG - PAD_L - PAD_R) / max(1, n) * 0.36)
    for k, b in enumerate(win):
        x = xk(k)
        col = UP_C if b['c'] >= b['o'] else DN_C
        d.line([(x, yp(b['hi'])), (x, yp(b['lo']))], fill=col, width=1)
        yo, yc = yp(b['o']), yp(b['c'])
        top, bot = min(yo, yc), max(yo, yc)
        if bot - top < 1:
            bot = top + 1
        d.rectangle([x - bw_px, top, x + bw_px, bot], fill=col)
        # volume
        vy = yv(b['v'])
        vcol = col if b['vratio'] < E.VSA_CLIMAX else (255, 235, 59)
        d.rectangle([x - bw_px, vy, x + bw_px, vol_bot], fill=vcol)

    d.rectangle([PAD_L, vol_top, W_IMG - PAD_R, vol_bot], outline=(50, 50, 58), width=1)
    # duong TB khoi luong 20 nen
    pts = [(xk(k), yv(min(vmax, b['vma']))) for k, b in enumerate(win)]
    d.line(pts, fill=(200, 170, 90), width=1)
    d.text((PAD_L + 6, vol_top + 4), "KHOI LUONG (vang = VSA >= 2.2x, duong = TB 20 nen)",
           fill=DIM, font=fs)

    # ---- bien chinh (net lien) + bien phu (net dut) ----
    x0 = xk(k_of(r.start_i))
    x1 = xk(k_of(min(end_i, hi_i)))
    if r.solid_low is not None:
        for p, lab in ((r.solid_low, "bien CHINH duoi"), (r.solid_high, "bien CHINH tren")):
            hline(yp(p), x0, x1, SOLID_C, dashed=False, width=2)
            d.text((x1 + 5, yp(p) - 7), f"{lab} {p:.1f}", fill=SOLID_C, font=fs)
    for p, lab, ref in ((r.low, "bien phu duoi", r.solid_low), (r.high, "bien phu tren", r.solid_high)):
        if ref is None or abs(p - ref) < 1e-9:
            continue
        hline(yp(p), x0, x1, DASH_C, dashed=True, width=2)
        d.text((x1 + 5, yp(p) - 7), f"{lab} {p:.1f}", fill=DASH_C, font=fs)

    # ---- move truoc climax ----
    if r.move_i is not None and r.move_i >= lo_i:
        mx = xk(k_of(r.move_i))
        my = yp(B[r.move_i]['hi'] if r.origin == 'DOWN' else B[r.move_i]['lo'])
        cx = xk(k_of(r.start_i))
        cy = yp(r.climax_price)
        d.line([(mx, my), (cx, cy)], fill=(110, 110, 130), width=1)
        label_box(mx - 10, my - 24 if r.origin == 'DOWN' else my + 8,
                  f"chan MOVE ({r.move_len:.1f} gia, hieu suat {r.move_eff:.2f})", (140, 140, 165), fo=fs)

    # ---- duong doc chia phase (chi trong pham vi gia cua range) ----
    ytop = yp(r.high if r.high is not None else ymax)
    ybot = yp(r.low if r.low is not None else ymin)
    for ph, ps, pe in sorted(r.phases, key=lambda p: p[1]):
        xp = xk(k_of(max(lo_i, min(hi_i, ps))))
        y = ytop
        while y < ybot:
            d.line([(xp, y), (xp, min(y + 6, ybot))], fill=PHASE_C, width=2)
            y += 12
        nb = (pe - ps + 1) if pe else 0
        label_box(xp + 3, ytop - 26, f"Phase {ph} ({nb}n)", PHASE_C, fo=fs)

    # ---- nhan su kien ----
    for ev in sorted(r.events, key=lambda e: e['i']):
        k = k_of(ev['i'])
        if k < 0 or k >= n:
            continue
        x, y = xk(k), yp(ev['price'])
        c = CAT_COLOR[cat_of(ev['label'])]
        grey = ev.get('status') == 'failed'
        mc = (140, 140, 140) if grey else c
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=mc, outline=(255, 255, 255), width=1)
        above = cat_of(ev['label']) in ('ar', 'st', 'break')
        bx, by, bbw, bbh = label_box(x - 9, y - 26 if above else y + 8, ev['label'], mc, fo=f)
        if abs(by + bbh / 2 - y) > 30:
            d.line([(x, y), (bx + bbw / 2, by + bbh / 2)], fill=(95, 95, 95), width=1)

    # ---- tieu de + hop thong tin ----
    title = (f"{r.kind_vn} ({r.kind})   {B[r.start_i]['dt']} -> {B[end_i]['dt']}   "
             f"{end_i - r.start_i} nen M1   [{r.status}]")
    d.text((PAD_L, 12), title, fill=TXT, font=ft)
    hh = (r.solid_high - r.solid_low) if r.solid_low is not None else 0.0
    outer_h = r.high - r.low
    ratio = outer_h / hh if hh > 1e-9 else 0.0
    born = "  [SINH TU CU PHA, khong co climax that]" if r.born_from_break else ""
    sub = (f"climax {r.origin}  VSA_nhan={r.climax_vsa:.2f}x   "
           f"cao bien chinh={hh:.1f} gia ({hh / B[r.start_i]['c'] * 100:.2f}%)   "
           f"cao bien phu={outer_h:.1f} gia (ty le {ratio:.2f}x)   "
           f"bias={r.bias:+d}   SOT-up={r.sot_up['state']}(n={r.sot_up['n']})  "
           f"SOT-dn={r.sot_dn['state']}(n={r.sot_dn['n']}){born}")
    d.text((PAD_L, 34), sub, fill=DIM, font=fs)

    img.save(out_png)
    return out_png


def facts(B, r, idx):
    """Phieu so lieu di kem anh — de giang vien khong phai doc so tu pixel."""
    end_i = r.end_i if r.end_i is not None else len(B) - 1
    L = []
    L.append(f"# Bai lam #{idx:02d} — {r.kind_vn} ({r.kind})")
    L.append("")
    L.append(f"- Anh: `range_{idx:02d}.png`")
    L.append(f"- Khung: M1 (GCQ26, gio UTC). Range: **{B[r.start_i]['dt']} -> {B[end_i]['dt']}** "
             f"= {end_i - r.start_i} nen.")
    L.append(f"- Climax mo range: **{'SC (move GIAM bi chan)' if r.origin == 'DOWN' else 'BCLX (move TANG bi chan)'}** "
             f"tai gia {r.climax_price:.1f}, VSA={B[r.start_i]['vratio']:.2f}x, "
             f"bien do nen={B[r.start_i]['rng']:.1f} gia.")
    if r.move_i is not None:
        L.append(f"- MOVE truoc climax: dai {r.move_len:.1f} gia, {r.start_i - r.move_i} nen, "
                 f"hieu suat huong {r.move_eff:.2f}.")
    if r.solid_low is not None:
        h = r.solid_high - r.solid_low
        L.append(f"- Bien CHINH (net lien, climax+AR): {r.solid_low:.1f} - {r.solid_high:.1f} "
                 f"= {h:.1f} gia ({h / B[r.start_i]['c'] * 100:.2f}% gia).")
    L.append(f"- Bien PHU (net dut, cuc tri xa nhat): {r.low:.1f} - {r.high:.1f} "
             f"= {r.high - r.low:.1f} gia.")
    if r.solid_low is not None:
        hh0 = r.solid_high - r.solid_low
        ratio0 = (r.high - r.low) / hh0 if hh0 > 1e-9 else 0.0
        L.append(f"- Ty le bien phu/bien chinh: **{ratio0:.2f}x** (guard huy range khi > "
                 f"{W.MAX_OUTER_RATIO}x).")
    L.append(f"- Nhan climax mang VSA={r.climax_vsa:.2f}x (cay volume cao nhat trong cum, "
             f"KHONG can trung voi cuc tri gia).")
    L.append(f"- Trang thai range: **{r.status}**" +
             (" (bi thay the boi mot range moi sinh tu cu pha, khong dat ten 4 mau hinh)"
              if r.status == 'superseded' else "") +
             (" — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su." if r.born_from_break else "") + ".")
    L.append("")
    L.append("## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)")
    L.append("")
    L.append(f"- **Bias bat doi xung test bien**: `{r.bias:+d}` "
             f"(+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, "
             f"0 = test CA HAI bien — ca THUONG).")
    for name, sot in (("TREN", r.sot_up), ("DUOI", r.sot_dn)):
        L.append(f"- **SOT phia {name}**: trang thai=`{sot['state']}`, n={sot['n']} nhip lien tiep "
                 f"rut ngan, ty le thrust cuoi/dau={sot['ratio']:.2f}, "
                 f"ty le volume nhip cuoi/dau={sot['effort']:.2f} "
                 f"({'HAP THU (volume >= nhip dau, canh giu vung)' if sot['effort'] >= 1.0 and sot['n'] >= 2 else 'can kiet' if sot['n'] >= 2 else '-'}).")
    if r.er_legs:
        top = max(r.er_legs, key=lambda x: x['er'])
        # v7 muc 13.1 (cham_24 #4): cau dien giai truoc day HARD-CODE "hap thu NGHI VAN" bat ke er
        # that (in y het voi er=0.18 lan er=1.54) — er=effort/result nen er<1 nghia la KET QUA NHIEU
        # HON no luc (nhip hieu qua, khong phai hap thu); chi er>=1 (no luc >= ket qua) moi dang ngo
        # hap thu that su. Doi cau chu theo dung dau cua er.
        tag = ("vung hap thu NGHI VAN (volume nhieu, ket qua it)" if top['er'] >= 1.0
               else "nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu)")
        L.append(f"- **Nhip no luc/ket qua cao nhat** trong Phase B: nen {top['i0']}..{top['i1']} "
                 f"({B[top['i1']]['dt']}), effort(VSA TB)={top['effort']:.2f}x, "
                 f"result(bien do/ATR)={top['result']:.2f}, ty le er={top['er']:.2f} — {tag}.")
    L.append("")
    L.append("## Phase (do dai tinh bang nen M1)")
    L.append("")
    L.append("| Phase | Bat dau | Ket thuc | So nen |")
    L.append("|---|---|---|---|")
    for ph, ps, pe in r.phases:
        pe2 = pe if pe is not None else end_i
        L.append(f"| {ph} | {B[ps]['dt']} | {B[pe2]['dt']} | {pe2 - ps + 1} |")
    L.append("")
    L.append("## Su kien da gan nhan")
    L.append("")
    L.append("| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |")
    L.append("|---|---|---|---|---|---|---|")
    for ev in sorted(r.events, key=lambda e: e['i']):
        b = B[ev['i']]
        L.append(f"| {ev['label']} | {b['dt']} | {ev['price']:.1f} | {ev['phase']} | "
                 f"{ev.get('status') or '-'} | {b['vratio']:.2f}x | {b['brat']:.2f} |")
    L.append("")
    L.append("## 12 nen quanh climax (kiem dieu kien mo range)")
    L.append("")
    L.append("| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for j in range(max(0, r.start_i - 6), min(len(B), r.start_i + 6)):
        b = B[j]
        mk = " **<- climax**" if j == r.start_i else ""
        L.append(f"| {j - r.start_i:+d}{mk} | {b['dt']} | {b['o']:.1f} | {b['hi']:.1f} | {b['lo']:.1f} | "
                 f"{b['c']:.1f} | {b['v']:.0f} | {b['vratio']:.2f}x | {b['brat']:.2f} |")
    return "\n".join(L) + "\n"


def main():
    only_month = sys.argv[1] if len(sys.argv) > 1 else None
    B = E.load_m1()
    ranges = W.detect(B)
    if only_month:
        ranges = [r for r in ranges if B[r.start_i]['dt'].strftime('%Y-%m') == only_month]
    os.makedirs(OUT_DIR, exist_ok=True)
    for old in os.listdir(OUT_DIR):
        if old.startswith("range_"):
            os.remove(os.path.join(OUT_DIR, old))
    index = []
    for idx, r in enumerate(sorted(ranges, key=lambda r: r.start_i), 1):
        png = os.path.join(OUT_DIR, f"range_{idx:02d}.png")
        render(B, r, png)
        md = os.path.join(OUT_DIR, f"range_{idx:02d}.md")
        with open(md, "w") as fh:
            fh.write(facts(B, r, idx))
        end_i = r.end_i if r.end_i is not None else len(B) - 1
        index.append(dict(idx=idx, kind=r.kind, kind_vn=r.kind_vn,
                          start=str(B[r.start_i]['dt']), end=str(B[end_i]['dt']),
                          bars=end_i - r.start_i, png=png, md=md,
                          phases=[[p[0], p[1], p[2]] for p in r.phases],
                          events=[ev['label'] for ev in sorted(r.events, key=lambda e: e['i'])]))
        print(f"#{idx:02d} {r.kind:8s} {B[r.start_i]['dt']} .. {B[end_i]['dt']} "
              f"({end_i - r.start_i} nen)")
    with open(os.path.join(OUT_DIR, "index.json"), "w") as fh:
        json.dump(index, fh, indent=1, ensure_ascii=False)
    print(f"\n{len(index)} bai lam -> {OUT_DIR}")


if __name__ == '__main__':
    main()
