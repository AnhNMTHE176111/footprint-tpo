#!/usr/bin/env bash
# Deploy Trạm Đêm Vàng lên GitHub Pages: https://anhnmthe176111.github.io/tram-dem-vang/
#  - tăng APP_VERSION (rules.js + sw.js) để service worker đổi cache; đặt BUMP=0 để bỏ qua
#  - sao chép toàn bộ app (KHÔNG chép tests, e2e, node_modules, docs, scripts) + .github (workflow lịch tin Forex Factory) + .nojekyll vào bản clone repo Pages
#  - KHÔNG ghi đè data/ (data/ff.json do GitHub Actions tạo, QĐ-22)
#  - commit + push nhánh main
# Dùng:  DEPLOY_DIR=/đường/dẫn/clone ./deploy.sh      (mặc định: $HOME/.tram-dem-vang-pages)
set -euo pipefail
cd "$(dirname "$0")"

REPO="${REPO:-AnhNMTHE176111/tram-dem-vang}"
DEST="${DEPLOY_DIR:-$HOME/.tram-dem-vang-pages}"

if [ "${BUMP:-1}" != "0" ]; then
  node -e '
    const fs = require("fs");
    const m = /APP_VERSION = \x27(\d+)\.(\d+)\.(\d+)\x27/.exec(fs.readFileSync("js/rules.js", "utf8"));
    if (!m) { console.error("không thấy APP_VERSION trong js/rules.js"); process.exit(1); }
    const next = `${m[1]}.${m[2]}.${+m[3] + 1}`;
    for (const f of ["js/rules.js", "sw.js"]) {
      const t = fs.readFileSync(f, "utf8").replace(/APP_VERSION = \x27[\d.]+\x27/, `APP_VERSION = \x27${next}\x27`);
      fs.writeFileSync(f, t);
    }
    console.log("APP_VERSION ->", next);
  '
fi

if [ ! -d "$DEST/.git" ]; then
  git clone "https://github.com/$REPO.git" "$DEST"
fi
git -C "$DEST" checkout -B main >/dev/null 2>&1 || true
git -C "$DEST" pull --ff-only origin main >/dev/null 2>&1 || true

# xóa bản cũ (giữ .git) rồi chép bản mới
find "$DEST" -mindepth 1 -maxdepth 1 ! -name .git ! -name data -exec rm -rf {} +
cp -r index.html manifest.webmanifest sw.js css js icons img "$DEST/"
rm -rf "$DEST/.github" && cp -r .github "$DEST/.github"
touch "$DEST/.nojekyll"

cd "$DEST"
git add -A
if git diff --cached --quiet; then
  echo "Không có thay đổi để deploy."
else
  VER="$(sed -n "s/.*APP_VERSION = '\([0-9.]*\)'.*/\1/p" js/rules.js | head -1)"
  git commit -q -m "Deploy Trạm Đêm Vàng $VER"
  git push -u origin main
  echo "Đã push phiên bản $VER. Đợi 1–2 phút rồi mở: https://anhnmthe176111.github.io/tram-dem-vang/"
fi
