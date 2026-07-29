# -*- coding: utf-8 -*-
"""Trich xuat co hoc (text + anh) bo bai giang Wyckoff.
Idempotent: kiem tra file/thu muc da co truoc khi tao lai.
Chi trich xuat, KHONG doc/giang noi dung.
"""
import os
import re
import subprocess
import sys
import zipfile
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(ROOT, "extracted")
TXT_DIR = os.path.join(EXT, "text")
IMG_DIR = os.path.join(EXT, "images")

PDFS = ["1.pdf", "2.pdf", "4.pdf", "5.pdf", "6.pdf", "7.pdf", "8.pdf", "12.pdf"]
# 9.pdf bi bo qua - trung md5 voi 8.pdf

MAX_IMG_BYTES = int(1.5 * 1024 * 1024 * 1024)  # nguong 1.5GB tong dung luong anh


def log(msg):
    print(msg, flush=True)


def ensure(d):
    os.makedirs(d, exist_ok=True)


def folder_size_bytes(path):
    tot = 0
    if not os.path.isdir(path):
        return 0
    for dp, _, files in os.walk(path):
        for fn in files:
            fp = os.path.join(dp, fn)
            try:
                tot += os.path.getsize(fp)
            except OSError:
                pass
    return tot


def run(cmd):
    log("  $ " + " ".join(cmd))
    subprocess.run(cmd, check=True)


# ---------- 1) PDF -> text ----------
def extract_pdf_text(name):
    base = os.path.splitext(name)[0]
    out_txt = os.path.join(TXT_DIR, f"{base}.txt")
    src = os.path.join(ROOT, name)
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 0:
        log(f"[skip-text] {name}: da co {out_txt}")
        return out_txt
    ensure(TXT_DIR)
    run(["pdftotext", "-layout", src, out_txt])
    log(f"[text] {name} -> {out_txt}")
    return out_txt


# ---------- 2) PDF -> anh ----------
def extract_pdf_images(name, dpi):
    base = os.path.splitext(name)[0]
    img_dir = os.path.join(IMG_DIR, base)
    src = os.path.join(ROOT, name)
    # kiem tra da render du chua: so sanh so file png voi so trang pdf
    n_pages = pdf_page_count(src)
    existing = 0
    if os.path.isdir(img_dir):
        existing = len([f for f in os.listdir(img_dir) if f.endswith(".png")])
    if existing >= n_pages and n_pages > 0:
        log(f"[skip-img] {name}: da co {existing} anh trong {img_dir}")
        return img_dir, existing
    ensure(img_dir)
    prefix = os.path.join(img_dir, "p")
    run(["pdftoppm", "-r", str(dpi), "-png", src, prefix])
    # pdftoppm dat ten p-1.png / p-01.png tuy so trang; chuan hoa ve p%03d.png
    normalize_pXXX(img_dir)
    n_after = len([f for f in os.listdir(img_dir) if f.endswith(".png")])
    log(f"[img] {name} (dpi={dpi}) -> {n_after} anh trong {img_dir}")
    return img_dir, n_after


def normalize_pXXX(img_dir):
    pat = re.compile(r"^p-?(\d+)\.png$")
    for fn in list(os.listdir(img_dir)):
        m = pat.match(fn)
        if not m:
            continue
        num = int(m.group(1))
        new_name = f"p{num:03d}.png"
        if fn != new_name:
            src = os.path.join(img_dir, fn)
            dst = os.path.join(img_dir, new_name)
            if not os.path.exists(dst):
                os.rename(src, dst)


def pdf_page_count(path):
    r = subprocess.run(["pdfinfo", path], capture_output=True, text=True, check=True)
    for line in r.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":")[1].strip())
    return 0


# ---------- 3) PPTX -> text ----------
def extract_pptx_text(pptx_name, out_name):
    out_txt = os.path.join(TXT_DIR, out_name)
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 0:
        log(f"[skip-text] {pptx_name}: da co {out_txt}")
        return out_txt
    ensure(TXT_DIR)
    src = os.path.join(ROOT, pptx_name)
    lines = []
    with zipfile.ZipFile(src) as z:
        names = z.namelist()
        slide_names = sorted(
            [n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)],
            key=lambda n: int(re.search(r"slide(\d+)\.xml$", n).group(1)),
        )
        notes_names = {
            int(re.search(r"notesSlide(\d+)\.xml$", n).group(1)): n
            for n in names
            if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", n)
        }
        for sn in slide_names:
            idx = int(re.search(r"slide(\d+)\.xml$", sn).group(1))
            xml = z.read(sn).decode("utf-8", errors="replace")
            texts = re.findall(r"<a:t>(.*?)</a:t>", xml, re.S)
            lines.append(f"=== SLIDE {idx} ===")
            lines.extend(t for t in texts if t.strip())
            if idx in notes_names:
                nxml = z.read(notes_names[idx]).decode("utf-8", errors="replace")
                ntexts = re.findall(r"<a:t>(.*?)</a:t>", nxml, re.S)
                ntexts = [t for t in ntexts if t.strip()]
                if ntexts:
                    lines.append(f"--- NOTES SLIDE {idx} ---")
                    lines.extend(ntexts)
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log(f"[text] {pptx_name} -> {out_txt}")
    return out_txt


def which(cmd):
    return shutil.which(cmd)


# ---------- 4) PPTX -> anh (libreoffice hoac fallback media) ----------
def extract_pptx_images(pptx_name, out_subdir, media_subdir, dpi):
    src = os.path.join(ROOT, pptx_name)
    img_dir = os.path.join(IMG_DIR, out_subdir)
    lo = which("libreoffice") or which("soffice")
    if lo:
        if os.path.isdir(img_dir) and any(f.endswith(".png") for f in os.listdir(img_dir)):
            n = len([f for f in os.listdir(img_dir) if f.endswith(".png")])
            log(f"[skip-img] {pptx_name}: da co {n} anh trong {img_dir}")
            return img_dir, n, "libreoffice"
        ensure(img_dir)
        tmp_pdf_dir = os.path.join(EXT, "_tmp_pptx_pdf")
        ensure(tmp_pdf_dir)
        run([lo, "--headless", "--convert-to", "pdf", "--outdir", tmp_pdf_dir, src])
        base = os.path.splitext(os.path.basename(src))[0]
        pdf_path = os.path.join(tmp_pdf_dir, base + ".pdf")
        if not os.path.exists(pdf_path):
            # ten file co the bi doi ky tu; tim file pdf moi nhat trong tmp
            cands = [f for f in os.listdir(tmp_pdf_dir) if f.endswith(".pdf")]
            if cands:
                pdf_path = os.path.join(tmp_pdf_dir, cands[0])
        prefix = os.path.join(img_dir, "s")
        run(["pdftoppm", "-r", str(dpi), "-png", pdf_path, prefix])
        normalize_sXXX(img_dir)
        n = len([f for f in os.listdir(img_dir) if f.endswith(".png")])
        log(f"[img] {pptx_name} -> {n} anh (libreoffice+pdftoppm) trong {img_dir}")
        return img_dir, n, "libreoffice"
    else:
        media_dir = os.path.join(IMG_DIR, media_subdir)
        if os.path.isdir(media_dir) and os.listdir(media_dir):
            n = len(os.listdir(media_dir))
            log(f"[skip-img] {pptx_name}: da co {n} file media trong {media_dir}")
            return media_dir, n, "media-fallback"
        ensure(media_dir)
        with zipfile.ZipFile(src) as z:
            media_names = [n for n in z.namelist() if n.startswith("ppt/media/")]
            for mn in media_names:
                data = z.read(mn)
                fn = os.path.basename(mn)
                with open(os.path.join(media_dir, fn), "wb") as f:
                    f.write(data)
        n = len(media_names)
        log(f"[img] {pptx_name} -> {n} anh media (fallback, KHONG co annotation) trong {media_dir}")
        return media_dir, n, "media-fallback"


def normalize_sXXX(img_dir):
    pat = re.compile(r"^s-?(\d+)\.png$")
    for fn in list(os.listdir(img_dir)):
        m = pat.match(fn)
        if not m:
            continue
        num = int(m.group(1))
        new_name = f"s{num:03d}.png"
        if fn != new_name:
            src = os.path.join(img_dir, fn)
            dst = os.path.join(img_dir, new_name)
            if not os.path.exists(dst):
                os.rename(src, dst)


def main():
    ensure(EXT)
    ensure(TXT_DIR)
    ensure(IMG_DIR)

    log("=== BAT DAU TRICH XUAT WYCKOFF ===")

    dpi_report = {}
    for name in PDFS:
        extract_pdf_text(name)

    for name in PDFS:
        cur_size = folder_size_bytes(IMG_DIR)
        dpi = 110 if cur_size < MAX_IMG_BYTES else 90
        dpi_report[name] = dpi
        extract_pdf_images(name, dpi)

    # PPTX
    extract_pptx_text("3.pptx", "pptx-3-slideNNN.txt")
    extract_pptx_text("Tổng hợp chart đẹp Journal.pptx", "pptx-journal-slideNNN.txt")

    pptx3_dpi = 110 if folder_size_bytes(IMG_DIR) < MAX_IMG_BYTES else 90
    dpi_report["3.pptx"] = pptx3_dpi
    extract_pptx_images("3.pptx", "pptx3", "pptx3-media", pptx3_dpi)

    journal_dpi = 110 if folder_size_bytes(IMG_DIR) < MAX_IMG_BYTES else 90
    dpi_report["Tổng hợp chart đẹp Journal.pptx"] = journal_dpi
    extract_pptx_images("Tổng hợp chart đẹp Journal.pptx", "journal", "journal-media", journal_dpi)

    tmp_pdf_dir = os.path.join(EXT, "_tmp_pptx_pdf")
    if os.path.isdir(tmp_pdf_dir):
        shutil.rmtree(tmp_pdf_dir)

    total_img_mb = round(folder_size_bytes(IMG_DIR) / 1024 / 1024, 1)
    total_txt_mb = round(folder_size_bytes(TXT_DIR) / 1024 / 1024, 2)
    log(f"\n=== XONG === anh: {total_img_mb} MB | text: {total_txt_mb} MB")
    log(f"DPI da dung: {dpi_report}")


if __name__ == "__main__":
    main()
