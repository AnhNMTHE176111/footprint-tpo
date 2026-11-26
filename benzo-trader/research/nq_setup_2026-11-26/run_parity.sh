#!/bin/bash
# Parity Python (nq_setup.py) ↔ C# (tools/ReplayNq, lõi OrderFlowBubbles thật): bản 2 (mặc định) + bản 1 (--failbreak),
# và C# nạp NGUỘI = chạy TĂNG DẦN từng nến (không nhìn trước). Tất cả phải KHỚP 100 %.
set -e
cd "$(dirname "$0")"
B=../..; L=../../../data-export/data-footprint/fp_NQZ26_XCME_Time_20260204-20261125_293d16h.csv; W="$(mktemp -d)"
export PYTHONIOENCODING=utf-8
dotnet build -c Release "$B/tools/ReplayNq" > /dev/null
R="dotnet run -c Release --no-build --project $B/tools/ReplayNq --"
$R --levels $L --out $W/cold.csv --cold
$R --levels $L --out $W/inc.csv
cmp $W/cold.csv $W/inc.csv && echo "C# nạp nguội = tăng dần"
python parity_nq.py $W/cold.csv
$R --levels $L --out $W/fb.csv --cold --failbreak
python parity_nq.py $W/fb.csv --failbreak
rm -rf "$W"
