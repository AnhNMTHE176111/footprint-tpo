# Lần chạm (neo nhiều nến) + độ rộng vùng [2, 5] giá — Vùng Canh Lệnh v5

Đặc tả: `PLAN-LAN-CHAM.md`. Dữ liệu chính: `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (86333 nến M1, 65 phiên, giờ UTC, một hợp đồng GCZ26).
**Phiên bị loại (4):** 2026-07-23 (phiên 0thin), 2026-07-24 (thin), 2026-07-27 (thin), 2026-07-28 (thin). Cờ splice: 0 phiên (không có chỗ nối). **Còn 61 phiên đo**: TRAIN 35 (2026-07-29 → 2026-09-15), TEST 26 (2026-09-16 → 2026-10-21, phiên cuối chưa trọn 865 nến). Tháng: T8 gồm 3 phiên cuối tháng 7 (07-29…07-31).
Hằng số chốt TRƯỚC khi nhìn TEST: τ = 0.0 · E = 2.0 giá · G = 5 nến; vùng [2, 5] giá. Đối chứng 50 bản mỗi loại.
**Ngưỡng "khác đối chứng" (chốt trước, plan mục 5):** thật nằm NGOÀI dải 5–95% của đối chứng ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở ≥ 2/3 tháng, VÀ |hiệu| > 2 sai số nhị thức của thật ở cả TRAIN và TEST. Thiếu một điều kiện ⇒ "≈ đối chứng".
Đ1 = dời nguyên bộ vùng của phiên 3–15 giá (dấu ngẫu nhiên, cố định trong phiên). Đ2 = vùng giả cùng độ rộng, tâm ngẫu nhiên trong biên phiên trước ±2 giá, cân lại theo ô (khoảng cách giá đóng → cạnh gần lúc vùng hiện × bin rộng); 100% lần chạm giả rơi vào ô có vùng thật.
Thời gian chạy: engine 0s (đọc cache), máy trạng thái thật + 2×50 đối chứng 27s.

## A. Kết quả chính — % đảo chiều / % xuyên phá: thật vs đối chứng

Mẫu số = mọi lần chạm đã chốt (đảo + xuyên + chưa rõ + không rõ phía = 100%). Thật: % ± sai số nhị thức (n). Đối chứng: trung bình [5%–95%] của 50 bản. Sai số nhị thức đánh giá THẤP vì nhiều lần chạm cùng một vùng.

### % ĐẢO CHIỀU

| Nhóm | Thật | Đ1 dời bản đồ | Đ2 khớp khoảng cách × rộng |
|---|---|---|---|
| TRAIN | **50.9** ±0.9 (n=2859) | 51.2 [50.1–52.5] | 49.0 [46.5–51.4] |
| TEST | **51.3** ±1.1 (n=1890) | 51.5 [49.6–53.5] | 48.3 [45.4–52.2] |
| GỘP | **51.1** ±0.7 (n=4749) | 51.3 [50.2–52.5] | 48.8 [46.7–51.4] |
| T8 | **51.0** ±1.1 (n=1996) | 51.4 [49.7–53.1] | 48.3 [44.6–51.6] |
| T9 | **51.5** ±1.2 (n=1734) | 51.2 [49.7–52.9] | 49.6 [46.4–54.2] |
| T10 | **50.4** ±1.6 (n=1019) | 51.1 [48.7–53.3] | 48.1 [44.0–52.0] |

- So Đ1: **≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số)**
- So Đ2: **≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số)**

### % XUYÊN PHÁ

| Nhóm | Thật | Đ1 dời bản đồ | Đ2 khớp khoảng cách × rộng |
|---|---|---|---|
| TRAIN | **28.8** ±0.8 (n=2859) | 31.7 [30.3–32.9] | 30.7 [27.9–33.9] |
| TEST | **26.2** ±1.0 (n=1890) | 29.8 [28.5–31.4] | 30.5 [26.9–33.7] |
| GỘP | **27.8** ±0.6 (n=4749) | 31.0 [30.0–32.0] | 30.6 [28.0–32.9] |
| T8 | **28.9** ±1.0 (n=1996) | 31.8 [30.1–33.4] | 31.0 [27.7–34.2] |
| T9 | **28.3** ±1.1 (n=1734) | 30.5 [29.0–31.9] | 29.9 [26.7–34.5] |
| T10 | **24.6** ±1.3 (n=1019) | 29.9 [28.2–31.6] | 31.0 [27.1–35.4] |

- So Đ1: **KHÁC đối chứng ▼**
- So Đ2: **≈ đối chứng (trong dải 5–95% ở TRAIN)**

### Theo độ rộng vùng (hình học: vùng hẹp ⇒ xuyên dễ hơn)

| Rộng | Kết cục | Thật GỘP | Đ1 GỘP | Đ2 GỘP | phán quyết Đ1 | phán quyết Đ2 |
|---|---|---|---|---|---|---|
| 2–3 giá | đảo | **49.6** ±0.9 (n=3209) | 50.6 [49.3–52.0] | 48.3 [45.9–51.3] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| 2–3 giá | xuyên | **28.3** ±0.8 (n=3209) | 32.4 [31.1–33.6] | 32.1 [29.3–35.1] | KHÁC đối chứng ▼ | ≈ đối chứng (trong dải 5–95% ở TRAIN) |
| 3–4 giá | đảo | **53.8** ±1.5 (n=1144) | 52.6 [50.3–55.1] | 49.0 [45.6–52.7] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST) |
| 3–4 giá | xuyên | **25.3** ±1.3 (n=1144) | 28.1 [26.1–29.9] | 27.8 [23.4–31.3] | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| 4–5 giá | đảo | **55.1** ±2.5 (n=396) | 52.9 [49.2–56.3] | 51.0 [45.0–56.9] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| 4–5 giá | xuyên | **30.1** ±2.3 (n=396) | 27.9 [24.5–30.2] | 26.8 [22.4–32.0] | ≈ đối chứng (trong dải 5–95% ở TEST; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |

## A2. Kiểm tra độ vững — THÊM SAU khi thấy kết quả (không đăng ký trước)

Vì sao: "chưa rõ" của vùng thật cao hơn hẳn đối chứng. Gần hết "chưa rõ" là **vùng rời bộ hiển thị khi giá còn neo ở đó**. Vùng thật bị engine bỏ/dựng lại đúng lúc giá đang ở nó (mốc chết khi bị chạm/xuyên, vùng đổi hình — xem ngay dưới bảng); vùng giả (dời) sống đúng chừng ấy nến nhưng giá không "đụng" vào cơ chế sống/chết của nó. Nếu phần bị cắt nghiêng về ca sắp xuyên thì % xuyên thật thấp hơn đối chứng là **do cơ chế hiển thị**, không phải vì vùng giữ giá tốt hơn — (ii) dưới đây kiểm điều đó.

| Bộ | lần chạm / bản | chưa rõ do rời bộ % | chưa rõ do hết phiên % | xuyên chốt tự nhiên % | xuyên chốt do rời bộ/hết phiên % |
|---|---|---|---|---|---|
| Thật | 4749 | 16.8 | 0.8 | 25.6 | 2.2 |
| Đ1 | 3891 | 9.9 | 0.8 | 27.2 | 3.8 |
| Đ2 (chưa cân) | 1640 | 12.4 | 0.8 | 26.6 | 3.7 |

Cơ chế: trong 796 lần chạm thật "chưa rõ do rời bộ", chỉ **11%** có một vùng hiển thị MỚI (mã khác) chồng lên chỗ cũ ngay nến vùng cũ biến mất (vùng bị dựng lại thành mã mới); phần lớn còn lại vùng biến mất hẳn khỏi bộ. Vùng CHỈ có số tròn (mốc không bao giờ chết) có "chưa rõ" **6%**, vùng có swing/mốc phiên (mốc chết khi bị xuyên 2 lần, POC trần chết khi bị chạm, mốc phiên hết hạn) **24%** ⇒ khớp giả thuyết "mốc chết/đổi đúng lúc giá đang ở vùng". Chưa tách riêng từng nguyên nhân.

**(i) % đảo chiều trong các lần đã phân loại** = đảo / (đảo + xuyên) — bỏ "chưa rõ" và "không rõ phía" ở cả hai bên:

| Nhóm | Thật | Đ1 | Đ2 |
|---|---|---|---|
| TRAIN | **63.9** ±1.0 (n=2277) | 61.8 [60.5–63.2] | 61.5 [58.4–64.7] |
| TEST | **66.2** ±1.2 (n=1466) | 63.4 [61.5–65.3] | 61.3 [57.5–65.1] |
| GỘP | **64.8** ±0.8 (n=3743) | 62.4 [61.4–63.4] | 61.5 [58.9–64.5] |
| T8 | **63.8** ±1.2 (n=1595) | 61.8 [60.3–63.5] | 60.9 [57.3–64.2] |
| T9 | **64.6** ±1.3 (n=1383) | 62.6 [60.9–64.3] | 62.4 [58.2–66.7] |
| T10 | **67.2** ±1.7 (n=765) | 63.1 [61.2–64.9] | 60.8 [56.6–64.6] |

- So Đ1: **KHÁC đối chứng ▲** · So Đ2: **≈ đối chứng (trong dải 5–95% ở TRAIN)**.
- Lưu ý: số đo (i) vẫn THIÊN về vùng thật — chính các lần xuyên bị cắt thành "chưa rõ" (bảng trên: xuyên chốt do rời bộ thật thấp hơn đối chứng), nên bỏ "chưa rõ" vẫn để lại mẫu ít xuyên hơn.

**(ii) Theo tiếp lần chạm khi vùng rời bộ** (biên đóng băng ở nến cuối vùng còn hiển thị, tới khi 5 nến yên hoặc hết phiên) — áp y hệt cho thật và đối chứng, cắt đứt ảnh hưởng của cơ chế chọn bộ lên kết cục:

| Kết cục | Nhóm | Thật | Đ1 | Đ2 |
|---|---|---|---|---|
| đảo | TRAIN | **57.0** ±0.9 (n=2859) | 55.2 [54.0–56.7] | 54.0 [51.9–56.2] |
| đảo | TEST | **57.7** ±1.1 (n=1890) | 55.7 [54.0–57.3] | 53.2 [50.2–56.9] |
| đảo | GỘP | **57.3** ±0.7 (n=4749) | 55.4 [54.6–56.4] | 53.7 [51.8–56.3] |
| xuyên | TRAIN | **38.8** ±0.9 (n=2859) | 37.3 [36.2–38.3] | 38.2 [35.5–40.8] |
| xuyên | TEST | **37.0** ±1.1 (n=1890) | 35.6 [33.9–37.1] | 38.0 [34.0–40.8] |
| xuyên | GỘP | **38.1** ±0.7 (n=4749) | 36.6 [35.7–37.5] | 38.1 [35.7–40.3] |
| chưa rõ | TRAIN | **0.9** ±0.2 (n=2859) | 0.9 [0.7–1.1] | 0.7 [0.3–1.2] |
| chưa rõ | TEST | **1.3** ±0.3 (n=1890) | 1.1 [0.8–1.3] | 1.2 [0.5–1.9] |
| chưa rõ | GỘP | **1.0** ±0.1 (n=4749) | 1.0 [0.8–1.1] | 1.0 [0.6–1.3] |

- % đảo: Đ1 **≈ đối chứng (|hiệu| ≤ 2 sai số)** · Đ2 **KHÁC đối chứng ▲**
- % xuyên: Đ1 **≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số)** · Đ2 **≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số)**

## B. Đếm theo định nghĩa mới (5.1a)

- Lần chạm đã chốt (phiên đo): **4749** (TRAIN 2859, TEST 1890); ≈ 78 lần/phiên. Bỏ 1 ca hết dữ liệu.
- Vùng hiển thị (mã vùng mới trong phiên đo): 4028. Số lần chạm mỗi vùng: 0 → 43% · 1 → 30% · 2 → 13% · 3 → 6% · ≥4 → 8%.
- Số nến neo (từ nến bắt đầu tới nến thoát cuối): p50 **10** · p85 30 · p95 52 · > 120 nến 0.2%. Lần chạm chỉ 1 nến (râu quét rồi đi): 8%.

| Nhóm | n | đảo % | xuyên % | chưa rõ % | không rõ phía % |
|---|---|---|---|---|---|
| GỘP | 4749 | 51.1 | 27.8 | 17.6 | 3.6 |
| TRAIN | 2859 | 50.9 | 28.8 | 17.0 | 3.3 |
| TEST | 1890 | 51.3 | 26.2 | 18.4 | 4.0 |
| T8 | 1996 | 51.0 | 28.9 | 16.7 | 3.4 |
| T9 | 1734 | 51.5 | 28.3 | 17.1 | 3.1 |
| T10 | 1019 | 50.4 | 24.6 | 20.0 | 4.9 |
| vai kháng cự (tới từ dưới) | 2298 | 52.7 | 29.5 | 17.8 | 0.0 |
| vai hỗ trợ (tới từ trên) | 2280 | 53.2 | 28.0 | 18.7 | 0.0 |
| pha Á | 1470 | 49.6 | 28.4 | 17.4 | 4.6 |
| pha Âu | 1151 | 53.6 | 26.8 | 16.2 | 3.4 |
| pha Mỹ | 2128 | 50.7 | 27.8 | 18.5 | 3.0 |
| rộng 2–3 giá | 3209 | 49.6 | 28.3 | 19.0 | 3.1 |
| rộng 3–4 giá | 1144 | 53.8 | 25.3 | 15.8 | 5.1 |
| rộng 4–5 giá | 396 | 55.1 | 30.1 | 11.1 | 3.8 |

### Bảng toàn cục pha × độ rộng (GỘP TRAIN+TEST) — số hiện trên nhãn

| Pha | Rộng | n | đảo % | xuyên % | chưa rõ % | không rõ phía % |
|---|---|---|---|---|---|---|
| Á | 2–3 giá | 1052 | 49.0 | 28.5 | 18.6 | 3.8 |
| Âu | 2–3 giá | 880 | 51.4 | 28.9 | 16.8 | 3.0 |
| Mỹ | 2–3 giá | 1277 | 48.9 | 27.8 | 20.8 | 2.5 |
| mọi pha | 2–3 giá | 3209 | 49.6 | 28.3 | 19.0 | 3.1 |
| Á | 3–4 giá | 333 | 51.4 | 25.8 | 15.9 | 6.9 |
| Âu | 3–4 giá | 213 | 60.1 | 20.7 | 15.0 | 4.2 |
| Mỹ | 3–4 giá | 598 | 52.8 | 26.8 | 16.1 | 4.3 |
| mọi pha | 3–4 giá | 1144 | 53.8 | 25.3 | 15.8 | 5.1 |
| Á | 4–5 giá | 85 | 49.4 | 36.5 | 8.2 | 5.9 | (n < 100 ⇒ dùng "mọi pha")
| Âu | 4–5 giá | 58 | 63.8 | 19.0 | 10.3 | 6.9 | (n < 100 ⇒ dùng "mọi pha")
| Mỹ | 4–5 giá | 253 | 54.9 | 30.4 | 12.3 | 2.4 |
| mọi pha | 4–5 giá | 396 | 55.1 | 30.1 | 11.1 | 3.8 |

Nhúng C# (`VclTables.Episode[pha, bin rộng, {đảo, xuyên, chưa rõ}]`, % nguyên; −1 = n < 100 ⇒ dùng `EpisodeAll`):

```csharp
public static readonly int[,,] Episode = {
    { { 49, 29, 19 }, { 51, 26, 16 }, { -1, -1, -1 } },
    { { 51, 29, 17 }, { 60, 21, 15 }, { -1, -1, -1 } },
    { { 49, 28, 21 }, { 53, 27, 16 }, { 55, 30, 12 } }
};
public static readonly int[,] EpisodeAll = { { 50, 28, 19 }, { 54, 25, 16 }, { 55, 30, 11 } };
```

## C. Độ rộng vùng và vệ sinh chart (5.1b)

Đo trên mọi dòng (vùng × nến) hiển thị ở phiên đo. v5 = chốt (chồng lấn: giữ ≥ 2 giá); v5 "cắt giữa" = làm đúng chữ plan (chồng lấn cắt ở giữa như v4) — chỉ để thấy vì sao tự quyết.

| Chỉ số | v4 (kẹp [1u,4u]) | v5 cắt giữa | **v5 chốt** | v5 sàn/trần 1,5–4 | v5 2–6 |
|---|---|---|---|---|---|
| vùng hiển thị TB | 6.39 | 6.47 | 6.44 | 6.39 | 6.44 |
| rộng trung vị (giá) | 2.00 | 2.00 | 2.25 | 2.00 | 2.30 |
| rộng p90 (giá) | 5.00 | 3.80 | 3.90 | 3.25 | 4.32 |
| % vùng > 4 giá | 16.1 | 7.3 | 7.5 | 0.0 | 12.7 |
| % vùng > 5 giá | 9.8 | 0.0 | 0.0 | 0.0 | 4.8 |
| % vùng = 2 giá (do nới) | 2.4 | 41.7 | 43.2 | 2.7 | 42.3 |
| % vùng < 2 giá | 47.8 | 11.3 | 0.0 | 48.0 | 0.0 |
| % nến đóng trong vùng | 30.9 | 36.1 | 37.2 | 31.7 | 37.9 |
| đổi vùng / giờ | 3.03 | 3.12 | 2.92 | 3.36 | 2.86 |
| tuổi thọ trung vị (phút) | 61 | 59 | 60 | 51 | 61 |

| v5 chốt theo tách | vùng TB | rộng TV | % > 4 | đổi/giờ | tuổi thọ |
|---|---|---|---|---|---|
| TRAIN | 6.44 | 2.35 | 8.3 | 3.05 | 58 |
| TEST | 6.44 | 2.10 | 6.4 | 2.75 | 65 |

Ca biên engine v5 (đếm trên MỌI vùng, mọi lần gộp — không chỉ vùng hiển thị): kẹp trần mảnh không tách được (u > 5) 109883 lần (u > 5 ở 577 nến = 0,7%, 12 phiên); ứng viên nằm NGOÀI biên vùng của chính nó sau khi dời điểm cắt: 34282 / 28376995 lượt.

### Độ nhạy sàn/trần (chỉ báo, không chọn lại) — % kết cục trên chính bộ vùng của biến thể (GỘP)

| Biến thể | n lần chạm | đảo % | xuyên % | chưa rõ % | không rõ phía % | đảo % theo rộng 2–3 / 3–4 / 4–5 |
|---|---|---|---|---|---|---|
| v4 [1u, 4u] | 4562 | 50.2 | 28.3 | 18.5 | 3.0 | 47 / 58 / 58 |
| v5 cắt giữa | 4927 | 49.8 | 27.3 | 18.7 | 4.3 | 48 / 57 / 54 |
| **v5 chốt 2–5** | 4749 | 51.1 | 27.8 | 17.6 | 3.6 | 50 / 54 / 55 |
| v5 1,5–4 | 5092 | 49.0 | 28.6 | 19.3 | 3.0 | 47 / 58 / 56 |
| v5 2–6 | 4642 | 51.3 | 27.9 | 17.0 | 3.8 | 49 / 54 / 55 |

Ghi chú: v4 có vùng < 2 và > 5 giá; bin 2–3 của v4/1,5–4 gộp cả vùng < 2 giá (bin "< 3").

## D. Bất đồng với luật xuyên của engine (5.1c)

Luật engine (`BREAK_U`): giá đóng vượt biên XA ≥ 1u. Đo ở cấp vùng trong suốt lần chạm (phía theo vai lần chạm).

- Lần chạm ĐẢO mà engine đã coi là xuyên (phá giả ≥ 1u rồi quay về): 263 / 2425 = 10.8%
- Lần chạm XUYÊN mà engine chưa coi là xuyên (đi quá biên xa 2 giá nhưng chưa tới 1u, khi u > 2): 26 / 1318 = 2.0%
- **Tỉ lệ bất đồng chung: 7.7%** (ngưỡng plan: > 15% ⇒ đề xuất vòng sau đổi BREAK_U thành 2 giá tuyệt đối).

## E. Đối chiếu file 29 ngày (5.1d)

Chạy y hệt trên `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h` (engine khởi động lại từ 08-16 nên tuần đầu thiếu ứng viên cũ). So trên 20 phiên chung.

| Nguồn | n | đảo % | xuyên % | chưa rõ % | không rõ phía % | nến neo p50 |
|---|---|---|---|---|---|---|
| file 90 ngày (các phiên chung) | 1665 | 51.1 | 29.3 | 16.6 | 2.9 | 10 |
| file 29 ngày | 1654 | 51.1 | 29.6 | 16.4 | 2.8 | 10 |

## F. So với cách đếm cũ "chạm = 1 nến" (5.2), trên CÙNG bộ vùng v5

- (a) Kiểu vcl4 (giá đóng vào vùng từ ngoài, mỗi nến tính 1 lần): **10933** lần · cách mới: **4749** lần ⇒ tỉ số cũ/mới = **2.30**.
- Trung bình mỗi lần chạm mới chứa **2.30** lần "chạm 1 nến" cũ (p50 2, p90 5); 51% lần chạm mới bị đếm cũ tính ≥ 2 lần (đúng chỗ người học phản đối); 20% lần chạm mới cách cũ KHÔNG đếm (râu chạm/nến nhảy qua mà giá đóng không nằm trong vùng).
- (b) Kiểu MAP15 (vào vùng bằng giá đóng → bảo vệ ≥ 2u trước khi đóng xuyên cạnh xa, ≤ 120 nến): 6912 sự kiện, 6868 có kết cục · **% bảo vệ 35.3%** (TRAIN 34.3 / TEST 36.7) · so với cách mới % đảo **51.1%**.
  Hai con số KHÔNG cùng thước: MAP15 cần đi 2u (≈ 3,4 giá ở u trung vị) và tính "phá" ngay khi đóng qua cạnh xa 1 tick; cách mới cần đi 2 giá và chịu được phá giả.

## G. Độ nhạy τ × E × G (5.3, GỘP, chỉ thật)

| τ (giá) | E (giá) | G (nến) | n | nến neo p50 | đảo % | xuyên % | chưa rõ % | không rõ phía % |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 1.0 | 5 | 5414 | 8 | 54.4 | 28.5 | 13.9 | 3.2 |
| 0.0 | 1.0 | 10 | 4250 | 11 | 49.1 | 29.3 | 17.6 | 4.0 |
| 0.0 | 1.0 | 20 | 3474 | 16 | 44.9 | 28.8 | 21.4 | 4.9 |
| **0.0** | **2.0** | **5** | 4749 | 10 | 51.1 | 27.8 | 17.6 | 3.6 |
| 0.0 | 2.0 | 10 | 3902 | 14 | 46.3 | 27.9 | 21.4 | 4.4 |
| 0.0 | 2.0 | 20 | 3259 | 19 | 41.9 | 27.3 | 25.7 | 5.1 |
| 0.0 | 3.0 | 5 | 4223 | 13 | 47.5 | 27.3 | 21.3 | 4.0 |
| 0.0 | 3.0 | 10 | 3585 | 17 | 42.9 | 27.4 | 25.0 | 4.7 |
| 0.0 | 3.0 | 20 | 3086 | 22 | 39.1 | 26.3 | 29.2 | 5.4 |
| 0.5 | 1.0 | 5 | 5761 | 8 | 57.9 | 25.0 | 14.3 | 2.9 |
| 0.5 | 1.0 | 10 | 4469 | 12 | 51.7 | 26.3 | 18.2 | 3.7 |
| 0.5 | 1.0 | 20 | 3611 | 17 | 46.7 | 26.3 | 22.4 | 4.6 |
| 0.5 | 2.0 | 5 | 5128 | 10 | 54.3 | 25.5 | 16.9 | 3.3 |
| 0.5 | 2.0 | 10 | 4148 | 14 | 49.2 | 25.9 | 20.9 | 4.0 |
| 0.5 | 2.0 | 20 | 3415 | 20 | 44.0 | 25.8 | 25.4 | 4.8 |
| 0.5 | 3.0 | 5 | 4525 | 13 | 50.6 | 25.3 | 20.4 | 3.6 |
| 0.5 | 3.0 | 10 | 3789 | 17 | 45.6 | 25.8 | 24.4 | 4.3 |
| 0.5 | 3.0 | 20 | 3234 | 22 | 41.3 | 25.0 | 28.6 | 5.0 |

**Tổ hợp làm % đảo lệch > 5 điểm so với chốt:** τ=0.0, E=1.0, G=20: 44.9% (Δ -6.1); τ=0.0, E=2.0, G=20: 41.9% (Δ -9.2); τ=0.0, E=3.0, G=10: 42.9% (Δ -8.2); τ=0.0, E=3.0, G=20: 39.1% (Δ -12.0); τ=0.5, E=1.0, G=5: 57.9% (Δ +6.8); τ=0.5, E=2.0, G=20: 44.0% (Δ -7.0); τ=0.5, E=3.0, G=10: 45.6% (Δ -5.5); τ=0.5, E=3.0, G=20: 41.3% (Δ -9.8)

### Minh hoạ hình học (rủi ro 2): biến thể "quãng đi đối xứng"

Đảo chiều phải đi thêm cả độ rộng vùng (thoát phía tới khi cách biên GẦN ≥ rộng + 2 giá), để đảo và xuyên cần cùng một quãng đi. (Chữ plan "cách TÂM ≥ rộng/2 + 2" trùng hệt định nghĩa chính nên không minh hoạ được gì; đây là cách hiểu tự quyết.)

| | đảo % | xuyên % |
|---|---|---|
| định nghĩa chính (thật) | 51.1 | 27.8 |
| quãng đi đối xứng — thật | 39.4 | 32.8 |
| quãng đi đối xứng — Đ1 | 40.4 [39.5–41.1] | 36.3 [35.2–37.3] |

## H. Lần chạm thứ k (5.6) — "tôn trọng tới khi bị phá"?

| k | Thật đảo % | Đ1 | Đ2 | phán quyết Đ1 | phán quyết Đ2 |
|---|---|---|---|---|---|
| 1 | **48.1** ±1.0 (n=2285) | 46.1 [44.5–48.0] | 43.0 [39.6–45.8] | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST) |
| 2 | **54.7** ±1.5 (n=1068) | 56.1 [53.9–58.4] | 53.6 [48.3–58.0] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| ≥3 | **53.1** ±1.3 (n=1396) | 56.2 [54.4–58.1] | 54.0 [50.1–58.5] | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |

**Tiêu chí đăng ký trước (mục 3) để đổi nhãn sang lịch sử riêng:** Δ = %đảo(lần k ≥ 2 mà mọi lần trước của vùng đều đảo) − %đảo(mọi lần). Thật phải vượt dải 5–95% của Δ đối chứng ở CẢ TRAIN và TEST, cùng dấu ở ≥ 2/3 tháng.

| Nhóm | n | Δ thật (điểm %) | Δ Đ1 [5–95] | Δ Đ2 [5–95] |
|---|---|---|---|---|
| TRAIN | 655 | +2.5 ±1.9 | +4.3 [+1.4; +7.7] | +5.5 [+0.5; +9.4] |
| TEST | 422 | +4.4 ±2.4 | +5.7 [+2.9; +9.3] | +4.6 [-3.9; +11.8] |
| GỘP | 1077 | +3.3 ±1.5 | +4.8 [+2.8; +6.7] | +5.2 [+1.2; +8.4] |
| T8 | 456 | +3.2 ±2.3 | +4.0 [-0.0; +8.3] | +5.7 [-0.2; +10.3] |
| T9 | 380 | +0.9 ±2.6 | +5.3 [+1.9; +8.5] | +4.5 [-2.7; +12.4] |
| T10 | 241 | +7.2 ±3.2 | +5.5 [+0.5; +9.7] | +4.9 [-3.5; +13.5] |

- So Đ1: **≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số)** · So Đ2: **≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số)** ⇒ **không đạt ⇒ giữ bảng toàn cục (phương án A)**.

## I. Lần chạm ngay sau một lần xuyên phá cùng vùng (5.7) — "đổi vai"

| | Thật đảo % | Đ1 | Đ2 |
|---|---|---|---|
| ngay sau xuyên | **54.9** ±1.8 (n=798) | 57.2 [54.1–60.7] | 54.0 [48.7–61.8] |
| lần đầu của vùng (k = 1) | 48.1 ±1.0 (n=2285) | | |

Phán quyết: Đ1 ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) · Đ2 ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số).

## J. Điểm vùng có dự báo không? (5.8) — % đảo theo tam phân vị điểm (cắt theo TRAIN: 2.5 / 7.5)

| Điểm | Số đo | Thật | Đ1 | Đ2 | phán quyết Đ1 | phán quyết Đ2 |
|---|---|---|---|---|---|---|
| thấp | % đảo (mọi lần) | **55.7** ±1.3 (n=1475) | 51.6 [49.9–52.9] | 48.3 [45.0–51.7] | KHÁC đối chứng ▲ | KHÁC đối chứng ▲ |
| thấp | đảo/(đảo+xuyên) | **61.5** ±1.3 (n=1336) | 60.7 [59.1–62.0] | 60.0 [56.1–65.5] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| giữa | % đảo (mọi lần) | **48.5** ±1.3 (n=1586) | 51.0 [49.4–53.2] | 47.1 [43.6–51.6] | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| giữa | đảo/(đảo+xuyên) | **65.9** ±1.4 (n=1167) | 62.8 [61.2–64.6] | 62.0 [57.3–67.1] | ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%) |
| cao | % đảo (mọi lần) | **49.4** ±1.2 (n=1688) | 51.3 [49.8–53.2] | 50.2 [47.1–52.7] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |
| cao | đảo/(đảo+xuyên) | **67.3** ±1.3 (n=1240) | 63.9 [62.0–66.3] | 62.0 [59.2–65.8] | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TRAIN) |

Tam phân vị thấp: 88% là vùng CHỈ có số tròn (không bao giờ chết/đổi hình) ⇒ "chưa rõ" chỉ 9% (hai nhóm kia 22%). % đảo (mọi lần) cao hơn là do ít bị cắt thành "chưa rõ" (xem A2), không phải vùng điểm thấp mạnh hơn. **Điểm KHÔNG phải độ mạnh** — chỉ là thứ tự xếp hạng để chọn vùng.

## K. Mười ba rủi ro của plan (mục 7) — đã gặp hay chưa

1. **Kết quả ≈ đối chứng:** % đảo — Đ1 ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số); Đ2 ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số). % xuyên — Đ1 KHÁC đối chứng ▼; Đ2 ≈ đối chứng (trong dải 5–95% ở TRAIN).
2. **Hình học E × độ rộng:** xem bảng theo bin rộng (mục A) và biến thể quãng đi đối xứng (mục G).
3. **Vệ sinh sau kẹp [2,5]:** đổi vùng 2.92/giờ (ngưỡng báo > 4), tuổi thọ trung vị 60 phút (ngưỡng báo < 30) ⇒ KHÔNG vượt ngưỡng.
4. **Không rõ phía 3.6% · chưa rõ 17.6%** (> 10% ⇒ lỗ hổng định nghĩa). Chưa rõ: 95% do vùng rời bộ khi giá còn neo (lỗ hổng = mã vùng chỉ sống khi còn hiển thị, gắn với rủi ro 5), còn lại do hết phiên; mục A2 cho thấy lỗ hổng này làm % xuyên thật thấp giả tạo. Không rõ phía: 78% xảy ra ngay nến vùng mới hiện (vùng mới dựng lên trùm giá), còn lại do biên dịch trùm giá đóng trước. Ví dụ không rõ phía (UTC): 2026-09-14 22:00; 2026-09-28 22:00; 2026-08-04 09:00. Ví dụ chưa rõ (UTC, hết phiên/rời bộ khi đang neo): 2026-10-20 19:12; 2026-08-24 17:08; 2026-08-21 01:02.
5. **Mất mã vùng khi rời bộ:** 36% vùng mới (1550/4262) chồng lên một vùng vừa rời bộ ≤ 60 nến trước ⇒ lịch sử riêng của những vùng này bị đếm lại từ 0. Gợi ý vòng sau: khoá lịch sử theo mức giá làm tròn 0,5.
6. **Hai quy ước side ngược nhau:** máy lần chạm KHÔNG dùng `side` nào; vai riêng {kháng cự, hỗ trợ, không rõ} theo phía giá tới. Test `test_xuyen_pha_va_doi_vai`, `test_nen_nhay_qua_vung` kiểm vai.
7. **Biên dịch khi lần chạm đang mở:** 19.2% nến-đang-mở có biên khác nến trước; 60% lần chạm có ít nhất 1 lần dịch biên.
8. **Nến nhảy qua vùng** (nến bắt đầu đóng quá lân cận phía bên kia): 92 ca (1.9%); kết cục: đảo chiều 17, xuyên phá 58, chưa rõ 17.
9. **Neo rất dài:** p95 = 52 nến; 3 lần dài nhất: 2026-09-22 22:01 UTC, 152 nến, đảo chiều; 2026-10-12 14:16 UTC, 146 nến, xuyên phá; 2026-08-17 01:35 UTC, 143 nến, đảo chiều.
10. **Hai định nghĩa xuyên / chạm cùng tồn tại:** bất đồng 7.7% (mục D); điểm vùng vẫn dùng 'chạm 1 nến' (mục F: 2.30 lần cũ / 1 lần mới).
11. **Một nến chạm 2 vùng kề:** 8.2% lần chạm bắt đầu cùng nến với lần chạm của vùng khác (± đánh giá thấp).
12. **Dữ liệu không đồng nhất:** 4 phiên thin đầu file bị loại (danh sách ở đầu); không có chỗ nối; phiên 10-21 chưa trọn; một hợp đồng, một mùa (07-29 → 10-21) — không ngoại suy.
13. **Ca chưa phủ trong máy 2.6 — tự quyết, KHÔNG dừng:** (a) vai không rõ chốt do hết phiên/rời bộ khi đang neo ⇒ vẫn "không rõ phía" (giữ 4 nhóm rời nhau); (b) nến chốt của ca hết phiên/rời bộ = nến PHÁT HIỆN; (c) "cầu" C₋→nến làm nến đi từ TRONG vùng ra xa vẫn tính là chạm ⇒ đếm thoát bắt đầu từ nến sau (đúng công thức plan, test ghi rõ); (d) chồng lấn vùng: giữ [2, 5] thay vì cắt giữa (mục C).

<!-- NHAN-XET -->
## Nhận xét (viết tay, trung thực)

1. **Kết luận theo ngưỡng đăng ký trước:** % đảo chiều của vùng thật (51,1% ±0,7) **≈ cả hai đối chứng** (Đ1 51,3% · Đ2 48,8%) ở TRAIN, TEST và cả 3 tháng. % xuyên phá thật (27,8%) thấp hơn Đ1 (31,0%) đạt đủ điều kiện "khác", nhưng ≈ Đ2.
2. **Phần "xuyên thấp hơn" là do cơ chế hiển thị, không phải vùng giữ giá tốt hơn** (mục A2, kiểm thêm sau): vùng thật hay bị engine bỏ khỏi bộ đúng lúc giá đang neo (mốc chết khi bị chạm/xuyên) ⇒ 16,8% lần chạm thành "chưa rõ" (đối chứng 10–12%). Theo tiếp các lần chạm đó tới khi chốt thì % xuyên thật 38,1% ≈ Đ1 36,6% ≈ Đ2 38,1%.
3. Cùng phép kiểm thêm sau, % đảo thật 57,3% vs Đ1 55,4% (≈, sát ngưỡng 2 sai số) và Đ2 53,7% (đạt "khác ▲"). Đây là phép đo KHÔNG đăng ký trước và hai đối chứng không đồng thuận ⇒ **không được coi là lợi thế**; chỉ là gợi ý cần đăng ký trước và kiểm lại trên dữ liệu mới.
4. **Nhãn tuyệt đối phần lớn là HÌNH HỌC:** đảo cần đi 2 giá từ biên gần, xuyên cần đi hết vùng + 2 giá. Vùng giả cùng cỡ cũng đảo ~49–51%. Khi bắt đảo và xuyên đi cùng quãng (biến thể đối xứng) thì % đảo rơi từ 51% xuống 39% (Đ1 40%). Vùng rộng 4–5 giá đảo 55% vs vùng 2–3 giá 50% — đối chứng cùng bin cũng tăng như vậy (53% vs 51%).
5. **Một lần chạm theo quan điểm "neo nhiều nến":** 4 749 lần trên 61 phiên (~78/phiên), neo trung vị 10 nến (p85 30, p95 52). Cách đếm cũ "1 nến" ra 10 933 lần = 2,3 lần nhiều hơn; 51% lần chạm mới bị cách cũ đếm ≥ 2 lần.
6. **Độ rộng [2, 5] giá:** v4 có 48% vùng < 2 giá và 10% > 5 giá; v5 0% ngoài [2, 5], trung vị 2,25 giá, p90 3,9; 43% vùng đúng 2 giá (nới). Vệ sinh không xấu đi: 2,9 lần đổi vùng/giờ, tuổi thọ 60 phút. Làm đúng chữ plan (cắt giữa) thì 11% vùng < 2 giá (hẹp nhất 0,15) ⇒ tự quyết giữ sàn 2 giá.
7. **Lịch sử riêng từng vùng không dự báo** (tiêu chí mục 3 không đạt) ⇒ giữ bảng toàn cục pha × độ rộng. **Điểm vùng không phải độ mạnh.** Lần chạm thứ k, lần ngay sau xuyên phá: ≈ đối chứng.
8. Lỗ hổng còn lại: 17,6% "chưa rõ" (≥ 10% ⇒ nhãn phải hiện "chưa rõ ≈z%") vì mã vùng chỉ sống khi còn hiển thị; 36% vùng mới chồng lên vùng vừa rời bộ ⇒ lịch sử riêng bị reset. Vòng sau: khoá lịch sử/lần chạm theo mức giá.
9. Độ nhạy: G là tham số nhạy nhất (G = 20 làm % đảo giảm 9 điểm, % chưa rõ tăng 8) — nhãn là tần suất của ĐỊNH NGHĨA đã chốt (τ 0, E 2, G 5), đổi định nghĩa là đổi số.
10. Đối chiếu file 29 ngày trên 20 phiên chung: 51,1/29,6% vs 51,1/29,3% — khớp. Bất đồng với luật xuyên của engine 7,7% (< 15%) ⇒ chưa cần đổi BREAK_U.

Ảnh minh hoạ: [TRAIN 2026-09-08](img/lan_cham_TRAIN_2026-09-08.png) · [TEST 2026-10-14](img/lan_cham_TEST_2026-10-14.png) (vẽ bằng `ve_lan_cham.py`).
