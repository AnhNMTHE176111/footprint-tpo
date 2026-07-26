#!/bin/bash
# Build 2 indicator TPO tren Linux bang cach CONCAT ProfileEngine.cs vao dau moi file.
# Moi `using` trong cac file nam BEN TRONG namespace -> noi file hop le.
#   Usage: ./build-tpo.sh            (build ca 2)
#          ./build-tpo.sh daily      (chi DailyTpoBias)
#          ./build-tpo.sh m30        (chi M30SessionZones)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="$HERE/ProfileEngine.cs"
TMP="$(mktemp -d)"
QW="$HOME/quantower-libs/qw-build.sh"

build_one() {
  local src="$1" asm="$2"
  cat "$ENGINE" "$src" > "$TMP/$asm.cs"
  bash "$QW" "$TMP/$asm.cs" "$asm"
  # qw-build.sh xuat vao <dirname src>/dist; gom lai ve dist cua suite
  mkdir -p "$HERE/dist"
  cp "$TMP/dist/$asm.dll" "$HERE/dist/$asm.dll" 2>/dev/null || \
    cp "$(dirname "$TMP/$asm.cs")/dist/$asm.dll" "$HERE/dist/$asm.dll"
  echo "==> $HERE/dist/$asm.dll"
}

case "${1:-all}" in
  daily) build_one "$HERE/DailyTpoBias.cs" DailyTpoBias ;;
  m30)   build_one "$HERE/M30SessionZones.cs" M30SessionZones ;;
  *)     build_one "$HERE/DailyTpoBias.cs" DailyTpoBias
         build_one "$HERE/M30SessionZones.cs" M30SessionZones ;;
esac
rm -rf "$TMP"
