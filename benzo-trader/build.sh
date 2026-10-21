#!/bin/bash
# Build BenzoTrader: concat ProfileEngine.cs (tpo-suite) + BenzoCore.cs + BenzoZones.cs + BenzoDetectors.cs + BenzoTrader.cs -> qw-build.sh -> dist/BenzoTrader.dll
# Moi `using` nam BEN TRONG namespace nen noi file hop le. Sau do copy TRUC TIEP vao
# C:\OptimusFLOW\Settings\Scripts\Indicators\BenzoTrader (TAO thu muc neu chua co — khac qw-deploy.sh mac dinh).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="$HERE/../quantower-tpo-suite/ProfileEngine.cs"
QW="$HOME/quantower-libs/qw-build.sh"
TMP="$(mktemp -d)"
cat "$ENGINE" "$HERE/BenzoCore.cs" "$HERE/BenzoZones.cs" "$HERE/BenzoDetectors.cs" "$HERE/BenzoTrader.cs" > "$TMP/BenzoTrader.cs"
bash "$QW" "$TMP/BenzoTrader.cs" BenzoTrader
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
