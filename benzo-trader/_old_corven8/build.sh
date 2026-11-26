#!/bin/bash
# Build BenzoTrader (setup CORVEN, corven-1) -> dist/BenzoTrader.dll, rồi copy vào Optimus Flow.
# NỐI NGUỒN (một nguồn, không copy tay — plan BENZO-CORVEN mục 2/10):
#   quantower-tpo-suite/ProfileEngine.cs          (chỉ vì NewsCalendar — tách sau)
#   quantower-orderflow-indicator/StackedImbalance.cs + ExhaustionLogic.cs   (namespace OrderFlowBubbles → BenzoOfLib)
#   quantower-range/RangeLogic.cs                  (namespace RangeBox → BenzoRangeLib)
#   BenzoCore.cs + BenzoZones.cs + BenzoOrderFlow.cs + BenzoCorven.cs + BenzoMt5.cs + BenzoTrader.cs
# Đổi namespace bằng sed để DLL này không trùng tên kiểu với OrderFlowBubbles.dll / RangeBox.dll cùng nạp trong Optimus Flow.
# Hai file order flow có `using` ở đầu file (ngoài namespace) ⇒ bỏ các dòng đó và đặt 1 khối `using` ở đầu file nối.
# Sau build: copy TRỰC TIẾP vào C:\OptimusFLOW\Settings\Scripts\Indicators\BenzoTrader (tạo thư mục nếu chưa có).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
QW="$HOME/quantower-libs/qw-build.sh"
TMP="$(mktemp -d)"
{
  echo "using System;"
  echo "using System.Collections.Generic;"
  cat "$ROOT/quantower-tpo-suite/ProfileEngine.cs"
  sed -E '/^using [A-Za-z.]+;[[:space:]]*$/d' "$ROOT/quantower-orderflow-indicator/StackedImbalance.cs"
  sed -E '/^using [A-Za-z.]+;[[:space:]]*$/d' "$ROOT/quantower-orderflow-indicator/ExhaustionLogic.cs"
  cat "$ROOT/quantower-range/RangeLogic.cs"
  cat "$HERE/BenzoCore.cs" "$HERE/BenzoZones.cs" "$HERE/BenzoOrderFlow.cs" "$HERE/BenzoCorven.cs" "$HERE/BenzoMt5.cs" "$HERE/BenzoTrader.cs"
} | sed -E 's/\bOrderFlowBubbles\b/BenzoOfLib/g; s/\bRangeBox\b/BenzoRangeLib/g' > "$TMP/BenzoTrader.cs"
LOG="$TMP/build.log"
bash "$QW" "$TMP/BenzoTrader.cs" BenzoTrader | tee "$LOG"
# 2 cảnh báo CS0649 (TeleReport.Enabled / TestNow) nằm sẵn trong ProfileEngine.cs của tpo-suite (không phải file của Benzo) — chỉ chặn cảnh báo MỚI và lỗi
grep -qE "[1-9][0-9]* Error\(s\)" "$LOG" && { echo "build.sh: CÓ LỖI BIÊN DỊCH — xem log trên" >&2; exit 1; }
if grep -E "warning CS" "$LOG" | grep -vq "TeleReport"; then echo "build.sh: CÓ CẢNH BÁO MỚI (ngoài 2 cảnh báo có sẵn của ProfileEngine.cs) — xem log trên" >&2; exit 1; fi
mkdir -p "$HERE/dist"
cp "$TMP/dist/BenzoTrader.dll" "$HERE/dist/BenzoTrader.dll"
echo "==> $HERE/dist/BenzoTrader.dll"
BASE="/c/OptimusFLOW/Settings/Scripts/Indicators"
if [ -d "$BASE" ]; then
  mkdir -p "$BASE/BenzoTrader"
  cp "$HERE/dist/BenzoTrader.dll" "$BASE/BenzoTrader/"
  echo "==> deployed: $BASE/BenzoTrader/BenzoTrader.dll"
else
  echo "build.sh: khong thay $BASE (Optimus Flow chua cai?) — BO QUA deploy" >&2
fi
rm -rf "$TMP"
