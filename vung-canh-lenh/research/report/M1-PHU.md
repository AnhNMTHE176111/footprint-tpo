# Đỉnh/đáy M1 làm mốc phụ — có làm vùng được bảo vệ nhiều hơn không?

Dữ liệu `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h`. 401 vùng v4 (B, B15, C, D). Cờ "có M1" = có ≥1 đỉnh/đáy M1 (k=5, sống 2 phiên) trong biên vùng lúc vùng hiện. Có M1: **339** vùng (85%). BẢO VỆ = giá đóng quay ≥2u về phía cũ trước khi xuyên qua cạnh xa. Đối chứng: dời toàn bộ đỉnh/đáy M1 ngẫu nhiên 3–8 giá, 100 lần.

| Tách | vùng CÓ M1: bảo vệ % (n lần chạm) | vùng KHÔNG M1: bảo vệ % (n) | hiệu (thật) | hiệu với M1 dời: trung bình [5%–95%] | thật vượt đối chứng? |
|---|---|---|---|---|---|
| TRAIN | 37% (1468) | 31% (194) | +5.3 điểm | +5.5 [+2.8; +7.9] | không (≈ M1 dời) |
| TEST | 32% (427) | 19% (43) | +13.0 điểm | +10.2 [+4.2; +16.4] | không (≈ M1 dời) |
| GỘP | 36% (1895) | 29% (237) | +6.5 điểm | +5.6 [+3.3; +7.7] | không (≈ M1 dời) |
