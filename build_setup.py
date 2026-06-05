# -*- coding: utf-8 -*-
"""Trich xuat text + render anh tu 2 PDF de phuc vu hoc Footprint/Order Flow."""
import fitz, os, re, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
FP = os.path.join(ROOT, "Foot Print Vietsub.pdf")
OF = os.path.join(ROOT, "Oder Flow vietsub.pdf")

NOISE = ("Machine Translated by Google", "onlinedoctranslator",
         "Translated from English to Vietnamese")

def clean_lines(text):
    out = []
    for ln in text.split("\n"):
        ln = " ".join(ln.split())            # gop khoang trang thua
        if not ln:
            continue
        if any(n in ln for n in NOISE):
            continue
        out.append(ln)
    return out

def ensure(d):
    os.makedirs(d, exist_ok=True)

def log(msg):
    print(msg, flush=True)

# ---------- 1) KHOA HOC FOOTPRINT (5 bai) ----------
LESSONS = [
    (1, 1, 41,  "bai-1-delta-giai-thich",      "Bai 1 — Delta Giai thich (Delta Explained)"),
    (2, 42, 68, "bai-2-cach-doc-delta",          "Bai 2 — Cach doc Delta (How to Read Delta)"),
    (3, 69, 117,"bai-3-so-delta",                "Bai 3 — So Delta (Delta Numbers)"),
    (4, 118,197,"bai-4-thiet-lap-delta-trade",   "Bai 4 — Thiet lap Delta Trade (Delta Trade Setups)"),
    (5, 198,229,"bai-5-bai-tap-tom-tat",         "Bai 5 — Bai tap Delta & Tom tat (Exercises & Summary)"),
]

def build_footprint():
    doc = fitz.open(FP)
    mat = fitz.Matrix(3.7, 3.7)             # khop anh goc 2666px de net toi da
    img_root = os.path.join(ROOT, "course", "images")
    txt_root = os.path.join(ROOT, "course", "text")
    ensure(txt_root)
    for num, p_start, p_end, slug, title in LESSONS:
        img_dir = os.path.join(img_root, f"bai-{num}")
        ensure(img_dir)
        md = [f"# {title}",
              f"> Nguon: Foot Print Vietsub.pdf, trang {p_start}–{p_end} "
              f"(khoa hoc Delta Order Flow, dang slide).\n"]
        for pg in range(p_start, p_end + 1):
            page = doc[pg - 1]
            img_name = f"p{pg:03d}.png"
            page.get_pixmap(matrix=mat).save(os.path.join(img_dir, img_name))
            lines = clean_lines(page.get_text())
            md.append(f"\n## Trang {pg}")
            md.append(f"![Trang {pg}](../images/bai-{num}/{img_name})\n")
            md.extend(lines if lines else ["*(slide chi co hinh, khong co text)*"])
        with open(os.path.join(txt_root, f"{slug}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(md))
        log(f"[footprint] {slug}: trang {p_start}-{p_end} -> {p_end-p_start+1} anh + text DONE")
    doc.close()

# ---------- 2) EBOOK ORDER FLOW ----------
def build_ebook():
    doc = fitz.open(OF)
    n = doc.page_count
    mat = fitz.Matrix(2.5, 2.5)
    img_dir = os.path.join(ROOT, "ebook", "images")
    txt_dir = os.path.join(ROOT, "ebook", "text")
    ensure(img_dir); ensure(txt_dir)

    # 2a) Muc luc (trang 3-7 pdf thuong chua TOC)
    toc = ["# Order Flow eBook — Muc luc (Table of Contents)",
           "> Trich tu Oder Flow vietsub.pdf. So trang ben phai la so trang trong SACH (co the lech vai trang so voi so trang PDF).\n"]
    for i in range(2, 7):
        for ln in clean_lines(doc[i].get_text()):
            ln = re.sub(r"\.{3,}", " ", ln)       # bo dau cham noi
            ln = re.sub(r"\s+", " ", ln).strip()
            if ln and ln.lower() != "noi dung":
                toc.append(f"- {ln}")
    with open(os.path.join(txt_dir, "00-muc-luc.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(toc))

    # 2b) Toan van theo tung trang + anh
    full = ["# Order Flow eBook — Toan van (theo trang PDF)",
            "> Tai lieu ly thuyet bo tro. Moi muc la 1 trang PDF kem anh.\n"]
    for pg in range(1, n + 1):
        page = doc[pg - 1]
        img_name = f"p{pg:03d}.png"
        page.get_pixmap(matrix=mat).save(os.path.join(img_dir, img_name))
        full.append(f"\n## Trang {pg}")
        full.append(f"![Trang {pg}](../images/{img_name})\n")
        lines = clean_lines(page.get_text())
        full.extend(lines if lines else ["*(trang chi co hinh)*"])
        if pg % 40 == 0:
            log(f"[ebook] da render {pg}/{n} trang")
    with open(os.path.join(txt_dir, "orderflow-full.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(full))
    log(f"[ebook] {n} anh + muc luc + toan van DONE")
    doc.close()

def folder_size_mb(path):
    tot = 0
    for dp, _, files in os.walk(path):
        for fn in files:
            tot += os.path.getsize(os.path.join(dp, fn))
    return round(tot / 1024 / 1024, 1)

if __name__ == "__main__":
    t0 = time.time()
    log("=== BAT DAU DUNG SETUP ===")
    build_footprint()
    build_ebook()
    log(f"\n=== XONG trong {round(time.time()-t0)}s ===")
    log(f"course/  = {folder_size_mb(os.path.join(ROOT,'course'))} MB")
    log(f"ebook/   = {folder_size_mb(os.path.join(ROOT,'ebook'))} MB")
