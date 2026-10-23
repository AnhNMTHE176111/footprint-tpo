#!/bin/bash
# Build BenzoTrader: concat ProfileEngine.cs (tpo-suite) + VclCore.cs (vung-canh-lenh) + BenzoCore.cs + BenzoSr.cs + BenzoLayers.cs + BenzoZones.cs + BenzoDetectors.cs + BenzoSetupA5.cs + BenzoTrader.cs -> qw-build.sh -> dist/BenzoTrader.dll
# VCLCORE=<file> (tuỳ chọn): dùng bản VclCore.cs khác (vd `git show HEAD:vung-canh-lenh/VclCore.cs`) khi bản trong cây làm việc đang sửa dở.
# Moi `using` nam BEN TRONG namespace nen noi file hop le. Sau do copy TRUC TIEP vao
# C:\OptimusFLOW\Settings\Scripts\Indicators\BenzoTrader (TAO thu muc neu chua co — khac qw-deploy.sh mac dinh).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="$HERE/../quantower-tpo-suite/ProfileEngine.cs"
QW="$HOME/quantower-libs/qw-build.sh"
TMP="$(mktemp -d)"
VCL="${VCLCORE:-$HERE/../vung-canh-lenh/VclCore.cs}"
cat "$ENGINE" "$VCL" "$HERE/BenzoCore.cs" "$HERE/BenzoSr.cs" "$HERE/BenzoLayers.cs" "$HERE/BenzoZones.cs" "$HERE/BenzoDetectors.cs" "$HERE/BenzoSetupA5.cs" "$HERE/BenzoTrader.cs" > "$TMP/BenzoTrader.cs"
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
