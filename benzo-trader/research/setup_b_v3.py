# -*- coding: utf-8 -*-
"""Setup B-v3 "Hấp thụ" = 8 loại vùng v2 + vùng S/R (đỉnh/đáy phiên trước + Vùng Canh Lệnh v5) — plan `plans/BENZO-B-v3-plan.md`.
Pipeline đo đầy đủ → report/RESULTS-B-v3.md + report/_eval_b_v3.txt (+ report/img/b_v3_*.png).

Chạy: python3 setup_b_v3.py      (chỉ file 90d GCZ26 — KHÔNG chạy file 2 năm; KHÔNG sửa kernel.py)

Mọi hằng số / ngưỡng / kỳ vọng dưới đây ĐĂNG KÝ TRƯỚC khi chạy lần đầu (commit riêng, trước khi có kết quả). Không chỉnh theo kết quả.
Quy ước đã chốt trước khi chạy (chỗ plan để mở):
  * "Lệnh chỉ-v3" = lệnh B-v3 mà idx KHÔNG có trong danh sách lệnh thô của B-v2 (so ở mức detect, cùng một P).
  * Tiêu chí 3.5-1 đọc ĐÚNG CHỮ plan v3: B-v3 trong dải 5–95 % ĐC1 về WR **hoặc** R TB ở TRAIN **hoặc** TEST (nới hơn B-v2 dùng "và");
    báo cáo in thêm biến thể "và" chỉ để tham khảo, KHÔNG dùng để quyết.
  * "Tệ đi" 3.5-2 (c): mất >= 3 lệnh v2 THẮNG do lệnh vùng mới chặn (one_at_a_time).
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ------------------------------------ HẰNG SỐ ĐĂNG KÝ TRƯỚC (plan mục 2.3) ------------------------------------
MAIN = (0.5, 3)                                   # θ 0,5 · N 3 (ô chính, như v2; không chọn theo kết quả)
RR = 3.0                                          # TP 3R
SHIFT_LO, SHIFT_HI, REPS, SHIFT_SEED = 3.0, 15.0, 100, 20261024   # ĐC1: cùng ma trận δ với BENZO-VCL / B-v2
CTRL_DRAWS = 200                                  # ĐC2: 200 lần rút
BOOT, BOOT_SEED = 10000, 0                        # KTC 95 % bootstrap
MIN_N = 10                                        # phán quyết chỉ khi >= 10 lệnh ở CẢ TRAIN và TEST
EXPECT_OLD = (11, 0.273, 0.00)                    # B cũ ô chính trên 90d
EXPECT_V2 = (25, 0.320, 0.19)                     # B v2 ô chính trên 90d
EXPECT_N_V3 = (40, 100)                           # kỳ vọng đăng ký trước cho n(B-v3)
BREAKEVEN_WR = 0.27                               # hoà vốn xấp xỉ ở 3R sau chi phí
VCL_WARM = 4                                      # khe VCL phải giữ cùng một eid >= 4 nến
EXPECT_TXT = [
    'n(B-v3): 25 → **40–100** (cạnh VCL bị chạm ~33 000 cặp (nến, vùng) mỗi vai trên 90d so với ~20 000 lượt chạm của 12 mức v2; trần 2/phiên chặn trên ở ~122 lệnh VCL; '
    'PDHL đóng góp 0–5 lệnh). n không tăng ≥ 1,6× ⇒ bộ lọc cụm/θ/chế độ là nút thắt, không phải vùng.',
    'WR ở 3R: **24–33 %**, trôi về hoà vốn ~27 %. **B-v3 ≈ dải ĐC1; lệnh chỉ-v3 ≈ ĐC2** (ba lần đo S/R trước — SR-KET-QUA, HVN 474 phiên, VCL 5 vòng — đều ra như vậy: '
    'vị trí vùng không mang thông tin, xác suất chạm chỉ phụ thuộc khoảng cách).',
    'Không ép: không chọn ô độ nhạy đẹp; không chọn biến thể "tâm"; TP 2R không chạy; không thêm bộ lọc giữa chừng.',
]
