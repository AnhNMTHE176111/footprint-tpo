#!/bin/bash
# Build RunnerSignal tren Linux: concat ProfileEngine.cs (tu quantower-tpo-suite) + RunnerSignal.cs.
# Moi `using` nam BEN TRONG namespace de noi file hop le.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="$HERE/../quantower-tpo-suite/ProfileEngine.cs"
SRC="$HERE/RunnerSignal.cs"
QW="$HOME/quantower-libs/qw-build.sh"
TMP="$(mktemp -d)"
cat "$ENGINE" "$SRC" > "$TMP/RunnerSignal.cs"
bash "$QW" "$TMP/RunnerSignal.cs" RunnerSignal
mkdir -p "$HERE/dist"
cp "$TMP/dist/RunnerSignal.dll" "$HERE/dist/RunnerSignal.dll"
echo "==> $HERE/dist/RunnerSignal.dll"
rm -rf "$TMP"
