#!/bin/bash
# Build "Position Planner": test lõi -> concat PlannerCore.cs + PositionPlanner.cs -> qw-build.sh -> dist/PositionPlanner.dll -> deploy Optimus Flow.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
QW="$HOME/quantower-libs/qw-build.sh"
dotnet run --project "$(cygpath -w "$HERE/tests" 2>/dev/null || echo "$HERE/tests")"
TMP="$(mktemp -d)"
cat "$HERE/PlannerCore.cs" "$HERE/PositionPlanner.cs" > "$TMP/PositionPlanner.cs"
LOG="$TMP/build.log"
bash "$QW" "$TMP/PositionPlanner.cs" PositionPlanner | tee "$LOG"
grep -qE "0 Warning\(s\)|0 cảnh báo" "$LOG" || { echo "build.sh: CÓ CẢNH BÁO hoặc lỗi" >&2; exit 1; }
mkdir -p "$HERE/dist"
cp "$TMP/dist/PositionPlanner.dll" "$HERE/dist/PositionPlanner.dll"
BASE="/c/OptimusFLOW/Settings/Scripts/Indicators"
if [ -d "$BASE" ] && [ -z "$NO_DEPLOY" ]; then
  mkdir -p "$BASE/PositionPlanner"; cp "$HERE/dist/PositionPlanner.dll" "$BASE/PositionPlanner/"
  echo "==> deployed: $BASE/PositionPlanner/PositionPlanner.dll"
  rm -rf "$BASE/VeLenh"   # bản cũ tên "Vẽ Lệnh" (cùng công cụ) — gỡ để không hiện 2 indicator
fi
rm -rf "$TMP"
