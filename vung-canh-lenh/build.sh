#!/bin/bash
# Build "Vùng Canh Lệnh": concat VclCore.cs + VungCanhLenh.cs -> qw-build.sh -> dist/VungCanhLenh.dll
# Mọi `using` nằm BÊN TRONG namespace nên nối file hợp lệ. Có Optimus Flow (Windows/Git Bash) thì copy thẳng vào
# C:\OptimusFLOW\Settings\Scripts\Indicators\VungCanhLenh (tạo thư mục nếu chưa có).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
QW="$HOME/quantower-libs/qw-build.sh"
for f in "$QW" "$HOME/quantower-libs/TradingPlatform.BusinessLayer.dll" "$HOME/quantower-libs/System.Drawing.Common.dll"; do
  [ -f "$f" ] || { echo "build.sh: THIẾU $f — không build được" >&2; exit 1; }
done
TMP="$(mktemp -d)"
cat "$HERE/VclCore.cs" "$HERE/VungCanhLenh.cs" > "$TMP/VungCanhLenh.cs"
LOG="$TMP/build.log"
bash "$QW" "$TMP/VungCanhLenh.cs" VungCanhLenh | tee "$LOG"
grep -qE "0 Warning\(s\)|0 cảnh báo" "$LOG" || { echo "build.sh: CÓ CẢNH BÁO hoặc lỗi — xem log trên" >&2; exit 1; }
mkdir -p "$HERE/dist"
cp "$TMP/dist/VungCanhLenh.dll" "$HERE/dist/VungCanhLenh.dll"
echo "==> $HERE/dist/VungCanhLenh.dll"
BASE="/c/OptimusFLOW/Settings/Scripts/Indicators"
if [ -d "$BASE" ]; then
  mkdir -p "$BASE/VungCanhLenh"
  cp "$HERE/dist/VungCanhLenh.dll" "$BASE/VungCanhLenh/"
  echo "==> deployed: $BASE/VungCanhLenh/VungCanhLenh.dll"
else
  echo "build.sh: không thấy $BASE (máy này không có Optimus Flow) — bỏ qua deploy" >&2
fi
rm -rf "$TMP"
