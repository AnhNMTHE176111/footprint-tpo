#!/bin/bash
# Build Benzo Trader (chuẩn setup CORVEN cho NQ M1, bản nq-corven-2) -> dist/BenzoTrader.dll, rồi copy vào Optimus Flow.
# NỐI NGUỒN (một nguồn, không copy tay):
#   quantower-orderflow-indicator/*.cs (lõi OrderFlowBubbles THẬT: chấm, Big Trade, kiệt sức, vùng stacked, stop hunt)
#       namespace OrderFlowBubbles -> BenzoOfLib, lớp indicator OrderFlowBubbles -> internal OfbCore (không hiện thành indicator thứ hai)
#   quantower-range/RangeLogic.cs (Range Box)  namespace RangeBox -> BenzoRangeLib
#   BenzoNq.cs (lõi thuần) + BenzoNqOfb.cs (cầu nối) + BenzoTrader.cs (lớp dán Quantower)
# Đổi tên để DLL này không trùng kiểu với OrderFlowBubbles.dll / RangeBox.dll cùng nạp trong Optimus Flow.
# Các file OrderFlowBubbles có `using` ở đầu file (ngoài namespace) => bỏ các dòng đó, đặt 1 khối `using` chung ở đầu file nối.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
OFB="$ROOT/quantower-orderflow-indicator"
QW="$HOME/quantower-libs/qw-build.sh"
TMP="$(mktemp -d)"
{
  echo "using System;"
  echo "using System.Collections.Generic;"
  echo "using System.Drawing;"
  echo "using System.IO;"
  echo "using System.Linq;"
  echo "using System.Text.Json;"
  echo "using System.Text.Json.Serialization;"
  echo "using TradingPlatform.BusinessLayer;"
  for f in OrderFlowBubbles SignalCache StackedImbalance ExhaustionLogic CellBigLogic StopHuntLogic RollingRobust StatThreshold; do
    sed -E '/^using [A-Za-z.]+;[[:space:]]*$/d' "$OFB/$f.cs"
  done
  cat "$ROOT/quantower-range/RangeLogic.cs"
  cat "$HERE/BenzoNq.cs" "$HERE/BenzoNqOfb.cs" "$HERE/BenzoTrader.cs"
} | sed -E 's/^namespace OrderFlowBubbles\b/namespace BenzoOfLib/;
            s/public class OrderFlowBubbles : Indicator/internal class OfbCore : Indicator/;
            s/public OrderFlowBubbles\(\) : base\(\)/public OfbCore() : base()/;
            s/using OfbCore = OrderFlowBubbles\.OrderFlowBubbles;/using OfbCore = BenzoOfLib.OfbCore;/;
            s/\bRangeBox\b/BenzoRangeLib/g' > "$TMP/BenzoTrader.cs"
LOG="$TMP/build.log"
bash "$QW" "$TMP/BenzoTrader.cs" BenzoTrader | tee "$LOG"
grep -qE "[1-9][0-9]* Error\(s\)" "$LOG" && { echo "build.sh: CÓ LỖI BIÊN DỊCH — xem log trên" >&2; exit 1; }
if grep -qE "warning CS" "$LOG"; then echo "build.sh: CÓ CẢNH BÁO — xem log trên" >&2; exit 1; fi
mkdir -p "$HERE/dist"
cp "$TMP/dist/BenzoTrader.dll" "$HERE/dist/BenzoTrader.dll"
echo "==> $HERE/dist/BenzoTrader.dll"
BASE="/c/OptimusFLOW/Settings/Scripts/Indicators"
if [ -n "$NO_DEPLOY" ]; then
  echo "build.sh: NO_DEPLOY — bỏ qua deploy"
elif [ -d "$BASE" ]; then
  mkdir -p "$BASE/BenzoTrader"
  cp "$HERE/dist/BenzoTrader.dll" "$BASE/BenzoTrader/"
  echo "==> deployed: $BASE/BenzoTrader/BenzoTrader.dll"
else
  echo "build.sh: khong thay $BASE (Optimus Flow chua cai?) — BO QUA deploy" >&2
fi
rm -rf "$TMP"
