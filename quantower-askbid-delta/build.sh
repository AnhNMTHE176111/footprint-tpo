#!/bin/bash
# Build 2 indicator nến delta: concat DeltaCore.cs + DeltaFeed.cs + DeltaIndicatorBase.cs + <indicator>.cs -> qw-build.sh.
# Moi `using` nam BEN TRONG namespace nen noi file hop le.
#   Usage: bash build.sh            (build ca 2)   |   bash build.sh cum   |   bash build.sh bars
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
QW="$HOME/quantower-libs/qw-build.sh"
TMP="$(mktemp -d)"
build_one() {
  local src="$1" asm="$2"
  cat "$HERE/DeltaCore.cs" "$HERE/DeltaFeed.cs" "$HERE/DeltaIndicatorBase.cs" "$HERE/$src" > "$TMP/$asm.cs"
  local log="$TMP/$asm.log"
  bash "$QW" "$TMP/$asm.cs" "$asm" | tee "$log"
  grep -qE "[1-9][0-9]* Error\(s\)" "$log" && { echo "build.sh: CO LOI BIEN DICH ($asm)" >&2; exit 1; }
  if grep -E "warning CS" "$log" | grep -q .; then echo "build.sh: CO CANH BAO ($asm) — xem log tren" >&2; exit 1; fi
  mkdir -p "$HERE/dist"
  cp "$TMP/dist/$asm.dll" "$HERE/dist/$asm.dll"
  echo "==> $HERE/dist/$asm.dll"
}
case "${1:-all}" in
  cum)  build_one CumDeltaCandles.cs CumDeltaCandles ;;
  bars) build_one AskBidDeltaBars.cs AskBidDeltaBars ;;
  *)    build_one CumDeltaCandles.cs CumDeltaCandles; build_one AskBidDeltaBars.cs AskBidDeltaBars ;;
esac
rm -rf "$TMP"
