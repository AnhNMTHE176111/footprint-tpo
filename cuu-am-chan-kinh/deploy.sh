#!/usr/bin/env bash
# Deploy Cửu Âm Chân Kinh lên GitHub Pages: https://anhnmthe176111.github.io/cuu-am-chan-kinh/
#  - lần đầu: tạo repo công khai + bật Pages (bỏ qua lỗi nếu đã có)
#  - clone repo Pages vào $HOME/.cuu-am-chan-kinh-pages, chép index.html chi-tiet.html style.css img/ .nojekyll
#  - commit + push nhánh main
# Dùng:  DEPLOY_DIR=/đường/dẫn/clone ./deploy.sh      (mặc định: $HOME/.cuu-am-chan-kinh-pages)
set -euo pipefail
cd "$(dirname "$0")"

REPO="${REPO:-AnhNMTHE176111/cuu-am-chan-kinh}"
DEST="${DEPLOY_DIR:-$HOME/.cuu-am-chan-kinh-pages}"

if ! gh repo view "$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public --description "Cửu Âm Chân Kinh — 3 kịch bản đánh vàng theo CORVEN"
fi

if [ ! -d "$DEST/.git" ]; then
  git clone "https://github.com/$REPO.git" "$DEST"
fi
git -C "$DEST" checkout -B main >/dev/null 2>&1 || true
git -C "$DEST" pull --ff-only origin main >/dev/null 2>&1 || true

# xóa bản cũ (giữ .git) rồi chép bản mới
find "$DEST" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -r index.html chi-tiet.html style.css "$DEST/"
mkdir -p "$DEST/img" && cp img/*.jpg "$DEST/img/"
touch "$DEST/.nojekyll"

cd "$DEST"
git add -A
if git diff --cached --quiet; then
  echo "Không có thay đổi để deploy."
else
  git commit -q -m "Deploy Cửu Âm Chân Kinh $(date +%Y-%m-%d_%H%M)"
  git push -u origin main
  echo "Đã push."
fi

# bật Pages (nhánh main, thư mục gốc); đã bật rồi thì bỏ qua lỗi
gh api -X POST "repos/$REPO/pages" -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 || true
echo "Đợi 1–2 phút rồi mở: https://anhnmthe176111.github.io/cuu-am-chan-kinh/"
