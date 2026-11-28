#!/bin/bash
# Build "Vẽ Lệnh": test lõi -> concat VeLenhCore.cs + VeLenh.cs -> qw-build.sh -> dist/VeLenh.dll -> deploy Optimus Flow.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
QW="$HOME/quantower-libs/qw-build.sh"
dotnet run --project "$(cygpath -w "$HERE/tests" 2>/dev/null || echo "$HERE/tests")"
TMP="$(mktemp -d)"
cat "$HERE/VeLenhCore.cs" "$HERE/VeLenh.cs" > "$TMP/VeLenh.cs"
LOG="$TMP/build.log"
bash "$QW" "$TMP/VeLenh.cs" VeLenh | tee "$LOG"
grep -qE "0 Warning\(s\)|0 cảnh báo" "$LOG" || { echo "build.sh: CÓ CẢNH BÁO hoặc lỗi" >&2; exit 1; }
mkdir -p "$HERE/dist"
cp "$TMP/dist/VeLenh.dll" "$HERE/dist/VeLenh.dll"
BASE="/c/OptimusFLOW/Settings/Scripts/Indicators"
if [ -d "$BASE" ] && [ -z "$NO_DEPLOY" ]; then
  mkdir -p "$BASE/VeLenh"; cp "$HERE/dist/VeLenh.dll" "$BASE/VeLenh/"
  echo "==> deployed: $BASE/VeLenh/VeLenh.dll"
fi
rm -rf "$TMP"
