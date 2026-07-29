#!/bin/bash
# Build WyckoffRunner tren Linux: concat ProfileEngine.cs (tu quantower-tpo-suite) + WyckoffRunner.cs.
# Moi `using` nam BEN TRONG namespace de noi file hop le.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="$HERE/../quantower-tpo-suite/ProfileEngine.cs"
SRC="$HERE/WyckoffRunner.cs"
QW="$HOME/quantower-libs/qw-build.sh"
TMP="$(mktemp -d)"
cat "$ENGINE" "$SRC" > "$TMP/WyckoffRunner.cs"
bash "$QW" "$TMP/WyckoffRunner.cs" WyckoffRunner
mkdir -p "$HERE/dist"
cp "$TMP/dist/WyckoffRunner.dll" "$HERE/dist/WyckoffRunner.dll"
echo "==> $HERE/dist/WyckoffRunner.dll"
rm -rf "$TMP"
