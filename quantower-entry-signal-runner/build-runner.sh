#!/bin/bash
# Build EntrySignalRunner (BẢN B — momentum runner 2R+) tren Linux.
# Giong build-entry.sh: concat ProfileEngine.cs (tu quantower-tpo-suite) + EntrySignalRunner.cs.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="$HERE/../quantower-tpo-suite/ProfileEngine.cs"
SRC="$HERE/EntrySignalRunner.cs"
QW="$HOME/quantower-libs/qw-build.sh"
TMP="$(mktemp -d)"
cat "$ENGINE" "$SRC" > "$TMP/EntrySignalRunner.cs"
bash "$QW" "$TMP/EntrySignalRunner.cs" EntrySignalRunner
mkdir -p "$HERE/dist"
cp "$TMP/dist/EntrySignalRunner.dll" "$HERE/dist/EntrySignalRunner.dll"
echo "==> $HERE/dist/EntrySignalRunner.dll"
rm -rf "$TMP"
