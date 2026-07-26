#!/bin/bash
# Build EntrySignal tren Linux: concat ProfileEngine.cs (tu quantower-tpo-suite) + EntrySignal.cs.
# Moi `using` nam BEN TRONG namespace de noi file hop le.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="$HERE/../quantower-tpo-suite/ProfileEngine.cs"
SRC="$HERE/EntrySignal.cs"
QW="$HOME/quantower-libs/qw-build.sh"
TMP="$(mktemp -d)"
cat "$ENGINE" "$SRC" > "$TMP/EntrySignal.cs"
bash "$QW" "$TMP/EntrySignal.cs" EntrySignal
mkdir -p "$HERE/dist"
cp "$TMP/dist/EntrySignal.dll" "$HERE/dist/EntrySignal.dll"
echo "==> $HERE/dist/EntrySignal.dll"
rm -rf "$TMP"
