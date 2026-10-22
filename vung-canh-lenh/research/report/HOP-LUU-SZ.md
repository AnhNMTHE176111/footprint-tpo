# Hợp lưu Vùng Canh Lệnh × SessionZones — vùng VCL trùng mức SessionZones có MẠNH hơn không?

## 0. Định nghĩa ĐĂNG KÝ TRƯỚC (viết trước khi chạy, không đổi sau khi thấy TEST)

- **Câu hỏi:** vùng VCL v5 (rộng 2–5 giá, đang hiển thị) mà TRÙNG một mức SessionZones thì lần chạm của nó có đảo chiều nhiều hơn, xuyên phá ít hơn, "thắng 1:1" nhiều hơn vùng VCL không trùng không?
- **Lần chạm, đảo chiều, xuyên phá:** y hệt `PLAN-LAN-CHAM.md` mục 2 (τ = 0, E = 2 giá, G = 5 nến), máy `lan_cham.episodes`. Mẫu số %đảo/%xuyên = MỌI lần chạm đã chốt (gồm "chưa rõ", "không rõ phía"), như bảng chính LAN-CHAM.md.
- **Mức SessionZones** = những gì `SessionZones.cs` vẽ MẶC ĐỊNH (`ZonePolicy`): VWAP ngày, VWAP tuần, VAH/VAL phiên Âu, HVN ngày, HVN tuần, LVN ngày. Bản Python: `kernel.vwap_series` (VWAP), `kernel._zones` (va_eu, hvn_day, lvn_day, hvn_week). VA Âu chốt lúc 19:00 VN và **mang sang** tới khi phiên Âu kế tiếp chốt (đúng `VaEdgeSessionIndex` của C#). HVN ngày/tuần có **dải** = PeakSharpness 90% (port đúng C#: nới liên tục tới khi volume hàng < 90% hàng đỉnh); VAH/VAL, LVN là **điểm**. Mức tĩnh chỉ tính khi tâm cách giá đóng ≤ 12 giá (`ZoneRadiusPrices` — SessionZones chỉ vẽ trong bán kính này); VWAP luôn vẽ.
- **Hợp lưu:** vùng [lo, hi] giao [mức_lo − 0,5 ; mức_hi + 0,5] (mức điểm: lo = hi). **Mức tĩnh: cờ chốt ở nến vùng LẦN ĐẦU hiện** (biên lúc đó), gắn cho mọi lần chạm của vùng. **VWAP (mức động): cờ chốt ở NẾN BẮT ĐẦU từng lần chạm** (VWAP tại nến đó, biên vùng tại nến đó) — vì VWAP trôi suốt phiên, cờ lúc vùng mới hiện không nói gì về lúc giá tới. Nhóm **BẤT KỲ** = có ít nhất 1 cờ trong 6 nhóm. Độ nhạy dung sai 0 / 0,5 / 1,5 giá — chỉ báo, không chọn lại.
- **"Thắng 1:1" (mục 6, MÔ TẢ, chưa phải chiến lược — chưa phí, chưa trượt giá, chưa xét có vào được lệnh không):** tham chiếu = biên GẦN của vùng tại nến bắt đầu (như lệnh chờ ở biên). Thắng = giá đi đúng hướng đảo ≥ 4 giá trước khi đi ngược ≥ 4 giá, trong 30 nến cùng phiên. Nến bắt đầu: đã đi ngược ≥ 4 giá ⇒ thua; phần đi đúng hướng trong nến này không tính. Một nến chạm cả hai mốc ⇒ THUA (thận trọng). Số đo = thắng / (thắng + thua); "hết 30 nến" báo riêng. Lần chạm "không rõ phía" không tính.
- **Đ1 — dời mức:** mọi mức SessionZones (cả đường VWAP) dời δ, |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, cố định trong (phiên, bản), 100 bản; gắn cờ lại y hệt (kể cả lọc bán kính 12 giá). So **Δ = %(có cờ) − %(không cờ)** thật với dải 5–95% của Δ dưới mức dời.
- **Đ2 — khớp độ rộng × khoảng cách:** so lần chạm có cờ với lần chạm KHÔNG cờ **cùng ô** (bin rộng 2–3/3–4/4–5 giá × bin khoảng cách giá đóng → cạnh gần lúc vùng hiện ≤3/3–6/6–12/>12 giá), trọng số = số lần có cờ trong ô. "Dải đối chứng" Đ2 = % không cờ cùng ô ± 1,645 sai số (≈ 5–95%).
- **Ngưỡng "khác đối chứng" (`PLAN-LAN-CHAM.md` mục 5, dùng NGUYÊN, hàm `lan_cham.verdict`):** ngoài dải 5–95% ở CẢ TRAIN và TEST, cùng dấu, cùng dấu ở ≥ 2/3 tháng, VÀ |hiệu| > 2 sai số nhị thức ở cả TRAIN và TEST. Thiếu một ⇒ "≈ đối chứng". **Chỉ gọi là CÓ khi vượt CẢ Đ1 lẫn Đ2 cùng chiều VÀ Δ cùng dấu ở cả 3 mức dung sai.**
- **Số phép so:** 7 nhóm × 3 kết cục × 2 đối chứng = 42 phán quyết (+ mục 5a: 6 nhóm × 3 kết cục = 18). Với chừng ấy phép so, một vài ô "vượt" do ngẫu nhiên là chuyện bình thường (nếu mỗi phép so có ~5% vượt ngẫu nhiên thì kỳ vọng ~2 ô trong 42) — ngưỡng nhiều điều kiện ở trên chặt hơn 5% nhiều, nhưng vẫn phải đọc với cảnh giác đó.
- **Tự quyết (ghi rõ):** (a) VA Âu mang sang ngày sau như C#; (b) HVN/LVN ngày từ profile PHIÊN CME TRƯỚC (kernel), còn C# dùng 24 giờ cuối cập nhật mỗi khi block Á/Âu/Mỹ đóng — **khác C#**; (c) không mô phỏng trần 5 vùng / gộp vùng / mục tiêu xa của SessionZones; (d) mục 5a dùng vùng giả rộng 2 giá (tâm ± 1) cho MỌI mức (đề bài ghi cả "±0,5" lẫn "rộng 2 giá" — chọn 2 giá để cùng cỡ vùng VCL hẹp nhất); (e) Đ1 dời theo (phiên, bản), cùng δ cho mọi nhóm.

## 1. Dữ liệu

`fp_GCZ26_XCEC_Time_20260723-20261021_90d` (86333 nến M1, giờ UTC, một hợp đồng). Phiên đo **61** (TRAIN 35 đến 2026-09-15, TEST 26); loại 4 phiên đầu (phiên 0 + thin) như LAN-CHAM.md. Lần chạm đã chốt trong phiên đo: **4749** (TRAIN 2859, TEST 1890) — khớp LAN-CHAM.md (4749). Vùng (mã) có ≥ 1 lần chạm: 2287.
Mức SessionZones dựng được: VAH/VAL Âu 128, HVN ngày 62, HVN tuần 109, LVN ngày 127 (số mức-phiên; VA Âu = 2 mức mỗi phiên Âu). VWAP ngày/tuần: mỗi nến. Độ rộng dải HVN (p10 / trung vị / p90 / lớn nhất, giá): HVN ngày 0.4 / 2.6 / 5.6 / 12.8 · HVN tuần 1.6 / 3.6 / 5.6 / 6.8. (Trên chart có lúc thấy "mảng HVN tuần" ~20 giá: đó là 2–3 dải HVN tuần nằm sát nhau, không phải một dải.)
Thời gian: dựng + 100 bản dời 8s.

## 2. Còn bao nhiêu vùng nếu chỉ giữ vùng hợp lưu? (mục 5b)

Hai cách đếm: (i) **vùng mới** (mã vùng) hiện trong phiên đo, cờ tại nến vùng lần đầu hiện (VWAP: tại nến đó); (ii) **trên chart tại mỗi nến**: số vùng VCL đang hiển thị trùng mức SessionZones ĐANG có ở nến đó (VWAP tại nến đó, mức tĩnh trong bán kính 12 giá) — đây là con số người học sẽ thấy.

| Nhóm | vùng mới hợp lưu / tổng | % | vùng mới hợp lưu / phiên | vùng hợp lưu đang hiện / nến (TB) | % nến có ≥ 1 vùng hợp lưu |
|---|---|---|---|---|---|
| (mọi vùng VCL) | 4028 / 4028 | 100 | 66.0 | 6.44 | — |
| VWAP ngày | 181 / 4028 | 4.5 | 3.0 | 0.32 | 31 |
| VWAP tuần | 153 / 4028 | 3.8 | 2.5 | 0.26 | 25 |
| VAH/VAL Âu | 239 / 4028 | 5.9 | 3.9 | 0.29 | 26 |
| HVN ngày | 209 / 4028 | 5.2 | 3.4 | 0.22 | 15 |
| HVN tuần | 168 / 4028 | 4.2 | 2.8 | 0.19 | 12 |
| LVN ngày | 118 / 4028 | 2.9 | 1.9 | 0.13 | 11 |
| BẤT KỲ (gộp) | 867 / 4028 | 21.5 | 14.2 | 1.13 | 68 |

Ghi chú cấu tạo: VCL lấy chính VAH/VAL Âu làm mốc loại C (`vcl.gen_candidates`) ⇒ một phần hợp lưu VA Âu là **tự trùng do cấu tạo**: 60% vùng hợp lưu VA Âu có mốc loại C (so với 23% mọi vùng). VWAP và HVN/LVN KHÔNG nằm trong ứng viên VCL.

## 3. Kết quả chính — có cờ vs không cờ, thật vs Đ1 (dời mức) vs Đ2 (khớp rộng × khoảng cách)

Đọc: **Δ = % có cờ − % không cờ** (điểm %). Đ1 = Δ khi dời mức SessionZones 3–15 giá [5%–95%]. Đ2 = % có cờ (chỉ ô có cặp) so với % không cờ CÙNG ô. n = lần chạm. Sai số nhị thức đánh giá THẤP (nhiều lần chạm cùng một vùng).

### ĐẢO CHIỀU — GỘP TRAIN+TEST

| Nhóm | n có cờ (vùng) | % có cờ | % không cờ (n) | **Δ thật** ±se | Đ1: Δ dời TB [5–95] | Đ2: có cờ vs không cờ cùng ô (phủ) | Phán quyết Đ1 | Phán quyết Đ2 |
|---|---|---|---|---|---|---|---|---|
| VWAP ngày | 347 (213) | 49.0 | 51.2 (4402) | **-2.2** ±2.8 | +0.2 [-4.5; +4.9] | 49.0 vs 50.6 (100%) | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| VWAP tuần | 219 (117) | 53.4 | 50.9 (4530) | **+2.5** ±3.5 | -0.8 [-8.0; +5.7] | 53.4 vs 50.8 (100%) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) |
| VAH/VAL Âu | 373 (187) | 47.5 | 51.4 (4376) | **-3.9** ±2.7 | -1.4 [-6.0; +2.9] | 47.5 vs 49.3 (100%) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| HVN ngày | 285 (151) | 41.1 | 51.7 (4464) | **-10.6** ±3.0 | -2.9 [-7.4; +1.9] | 41.1 vs 50.3 (100%) | ≈ đối chứng (|hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) |
| HVN tuần | 196 (111) | 48.0 | 51.2 (4553) | **-3.2** ±3.6 | -3.4 [-9.1; +2.5] | 48.0 vs 50.4 (100%) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| LVN ngày | 159 (82) | 41.5 | 51.4 (4590) | **-9.9** ±4.0 | +0.2 [-5.2; +5.8] | 41.5 vs 51.4 (100%) | ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) |
| BẤT KỲ (gộp) | 1262 (678) | 47.1 | 52.5 (3487) | **-5.3** ±1.6 | -1.9 [-4.4; +0.9] | 47.1 vs 51.3 (100%) | ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) |

#### ĐẢO CHIỀU — Δ thật [dải Đ1] theo TRAIN / TEST / tháng

| Nhóm | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|
| VWAP ngày | +3.0 ±3.6 [-5; +7] (n=205) | -9.8 ±4.3 [-8; +8] (n=142) | +4.7 ±4.5 [-7; +9] (n=130) | -2.8 ±4.5 [-7; +11] (n=137) | -12.7 ±5.7 [-10; +9] (n=80) |
| VWAP tuần | +1.6 ±4.6 [-7; +9] (n=122) | +3.5 ±5.2 [-12; +6] (n=97) | +3.2 ±5.9 [-8; +11] (n=74) | +2.4 ±5.7 [-11; +9] (n=80) | +2.0 ±6.4 [-15; +6] (n=65) |
| VAH/VAL Âu | -2.3 ±3.7 [-8; +5] (n=201) | -5.9 ±4.0 [-9; +4] (n=172) | -3.2 ±4.2 [-10; +5] (n=152) | -3.0 ±4.9 [-9; +8] (n=113) | -5.7 ±5.1 [-9; +5] (n=108) |
| HVN ngày | -11.8 ±4.0 [-10; +2] (n=156) | -9.3 ±4.5 [-8; +8] (n=129) | -9.9 ±5.0 [-12; +3] (n=101) | -7.7 ±4.6 [-9; +3] (n=124) | -18.2 ±6.3 [-13; +13] (n=60) |
| HVN tuần | +0.2 ±7.4 [-16; +11] (n=47) | -4.7 ±4.3 [-13; +0] (n=149) | +0.5 ±8.8 [-26; +12] (n=33) | -1.5 ±13.4 [-12; +24] (n=14) | -4.1 ±4.4 [-14; +1] (n=149) |
| LVN ngày | -9.3 ±6.1 [-12; +4] (n=67) | -10.5 ±5.3 [-4; +12] (n=92) | -6.7 ±6.9 [-12; +5] (n=54) | -18.4 ±5.9 [-9; +10] (n=68) | +0.9 ±8.4 [-13; +17] (n=37) |
| BẤT KỲ (gộp) | -3.5 ±2.2 [-5; +2] (n=641) | -7.8 ±2.4 [-6; +2] (n=621) | -3.6 ±2.7 [-7; +2] (n=438) | -5.4 ±2.8 [-4; +4] (n=438) | -7.8 ±3.2 [-8; +2] (n=386) |

#### ĐẢO CHIỀU — Đ2 theo TRAIN / TEST / tháng: % có cờ vs % không cờ cùng ô

| Nhóm | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|
| VWAP ngày | 53.7 vs 50.2 | 42.3 vs 50.9 | 55.4 vs 49.9 | 48.9 vs 51.1 | 38.8 vs 47.3 |
| VWAP tuần | 52.5 vs 50.1 | 54.6 vs 51.3 | 54.1 vs 48.7 | 53.8 vs 50.9 | 52.3 vs 50.0 |
| VAH/VAL Âu | 48.8 vs 50.0 | 45.9 vs 47.9 | 48.0 vs 50.6 | 48.7 vs 49.0 | 45.4 vs 49.7 |
| HVN ngày | 39.7 vs 50.2 | 42.6 vs 50.5 | 41.6 vs 51.0 | 44.4 vs 49.4 | 33.3 vs 47.5 |
| HVN tuần | 51.1 vs 49.5 | 47.0 vs 51.0 | 51.5 vs 48.9 | 50.0 vs 53.0 | 47.0 vs 49.3 |
| LVN ngày | 41.8 vs 51.4 | 41.3 vs 52.3 | 44.4 vs 51.4 | 33.8 vs 50.2 | 51.4 vs 53.6 |
| BẤT KỲ (gộp) | 48.2 vs 50.6 | 46.1 vs 52.1 | 48.2 vs 50.9 | 47.5 vs 51.3 | 45.6 vs 51.0 |

### XUYÊN PHÁ — GỘP TRAIN+TEST

| Nhóm | n có cờ (vùng) | % có cờ | % không cờ (n) | **Δ thật** ±se | Đ1: Δ dời TB [5–95] | Đ2: có cờ vs không cờ cùng ô (phủ) | Phán quyết Đ1 | Phán quyết Đ2 |
|---|---|---|---|---|---|---|---|---|
| VWAP ngày | 347 (213) | 25.4 | 27.9 (4402) | **-2.6** ±2.4 | +0.1 [-4.0; +4.3] | 25.4 vs 27.0 (100%) | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |
| VWAP tuần | 219 (117) | 25.6 | 27.9 (4530) | **-2.3** ±3.0 | -0.6 [-5.8; +5.1] | 25.6 vs 27.6 (100%) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) |
| VAH/VAL Âu | 373 (187) | 26.3 | 27.9 (4376) | **-1.6** ±2.4 | -3.3 [-6.3; +0.5] | 26.3 vs 26.4 (100%) | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |
| HVN ngày | 285 (151) | 28.8 | 27.7 (4464) | **+1.1** ±2.8 | -3.1 [-7.1; +1.0] | 28.8 vs 25.9 (100%) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) |
| HVN tuần | 196 (111) | 24.0 | 27.9 (4553) | **-3.9** ±3.1 | -6.0 [-10.8; -1.3] | 24.0 vs 26.8 (100%) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |
| LVN ngày | 159 (82) | 32.1 | 27.6 (4590) | **+4.5** ±3.8 | -1.8 [-8.3; +3.8] | 32.1 vs 26.8 (100%) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) |
| BẤT KỲ (gộp) | 1262 (678) | 26.4 | 28.2 (3487) | **-1.9** ±1.5 | -2.3 [-4.1; -0.1] | 26.4 vs 27.0 (100%) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |

#### XUYÊN PHÁ — Δ thật [dải Đ1] theo TRAIN / TEST / tháng

| Nhóm | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|
| VWAP ngày | -5.7 ±3.1 [-6; +6] (n=205) | +2.1 ±3.9 [-6; +6] (n=142) | -7.1 ±3.8 [-8; +9] (n=130) | +2.6 ±4.1 [-6; +7] (n=137) | -3.7 ±4.8 [-7; +7] (n=80) |
| VWAP tuần | -4.3 ±4.0 [-9; +5] (n=122) | +0.6 ±4.6 [-7; +9] (n=97) | -4.8 ±5.1 [-13; +5] (n=74) | -0.8 ±5.1 [-7; +10] (n=80) | -0.0 ±5.5 [-7; +15] (n=65) |
| VAH/VAL Âu | +1.7 ±3.4 [-9; +2] (n=201) | -5.2 ±3.3 [-9; +2] (n=172) | +0.8 ±3.9 [-10; +3] (n=152) | -0.9 ±4.3 [-11; +3] (n=113) | -4.8 ±4.1 [-10; +4] (n=108) |
| HVN ngày | +1.5 ±3.8 [-8; +1] (n=156) | +1.0 ±4.1 [-11; +4] (n=129) | -4.4 ±4.4 [-11; +0] (n=101) | +7.8 ±4.4 [-9; +6] (n=124) | -3.2 ±5.5 [-13; +4] (n=60) |
| HVN tuần | +1.1 ±6.7 [-13; +9] (n=47) | -4.4 ±3.6 [-12; -3] (n=149) | -1.7 ±7.8 [-14; +19] (n=33) | +7.5 ±12.9 [-19; +5] (n=14) | -2.9 ±3.7 [-10; -1] (n=149) |
| LVN ngày | +5.7 ±5.9 [-9; +9] (n=67) | +4.4 ±4.9 [-11; +5] (n=92) | +4.5 ±6.5 [-12; +6] (n=54) | +13.4 ±6.1 [-11; +11] (n=68) | -11.5 ±5.8 [-14; +10] (n=37) |
| BẤT KỲ (gộp) | -1.3 ±2.0 [-5; +1] (n=641) | -1.9 ±2.1 [-6; +1] (n=621) | -2.5 ±2.4 [-7; +1] (n=438) | +2.8 ±2.5 [-5; +3] (n=438) | -5.5 ±2.7 [-7; +2] (n=386) |

#### XUYÊN PHÁ — Đ2 theo TRAIN / TEST / tháng: % có cờ vs % không cờ cùng ô

| Nhóm | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|
| VWAP ngày | 23.4 vs 28.3 | 28.2 vs 25.3 | 22.3 vs 28.6 | 30.7 vs 28.1 | 21.3 vs 24.0 |
| VWAP tuần | 24.6 vs 28.8 | 26.8 vs 27.3 | 24.3 vs 28.2 | 27.5 vs 30.0 | 24.6 vs 25.5 |
| VAH/VAL Âu | 30.3 vs 26.8 | 21.5 vs 25.2 | 29.6 vs 26.5 | 27.4 vs 27.3 | 20.4 vs 21.8 |
| HVN ngày | 30.1 vs 27.0 | 27.1 vs 24.8 | 24.8 vs 27.5 | 35.5 vs 26.6 | 21.7 vs 21.4 |
| HVN tuần | 29.8 vs 26.3 | 22.1 vs 26.7 | 27.3 vs 26.0 | 35.7 vs 27.3 | 22.1 vs 25.8 |
| LVN ngày | 34.3 vs 27.8 | 30.4 vs 24.5 | 33.3 vs 28.3 | 41.2 vs 27.6 | 13.5 vs 22.4 |
| BẤT KỲ (gộp) | 27.8 vs 27.5 | 25.0 vs 26.0 | 26.9 vs 27.7 | 30.4 vs 26.2 | 21.2 vs 26.2 |

### THẮNG 1:1 (4 giá trước −4 giá, 30 nến) = thắng/(thắng+thua) — GỘP TRAIN+TEST

| Nhóm | n có cờ (vùng) | % có cờ | % không cờ (n) | **Δ thật** ±se | Đ1: Δ dời TB [5–95] | Đ2: có cờ vs không cờ cùng ô (phủ) | Phán quyết Đ1 | Phán quyết Đ2 |
|---|---|---|---|---|---|---|---|---|
| VWAP ngày | 297 (189) | 44.4 | 46.8 (4018) | **-2.4** ±3.0 | +1.2 [-3.7; +5.8] | 44.4 vs 47.3 (100%) | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| VWAP tuần | 194 (107) | 45.4 | 46.7 (4121) | **-1.4** ±3.7 | -0.5 [-6.7; +5.8] | 45.4 vs 46.7 (100%) | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |
| VAH/VAL Âu | 336 (173) | 42.3 | 47.0 (3979) | **-4.8** ±2.8 | +0.5 [-3.8; +4.6] | 42.3 vs 46.3 (100%) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) |
| HVN ngày | 246 (131) | 40.7 | 47.0 (4069) | **-6.4** ±3.2 | +0.2 [-5.0; +6.7] | 40.7 vs 46.6 (100%) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) |
| HVN tuần | 163 (89) | 50.3 | 46.5 (4152) | **+3.8** ±4.0 | -0.4 [-6.2; +5.3] | 50.3 vs 47.6 (100%) | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| LVN ngày | 142 (75) | 43.0 | 46.8 (4173) | **-3.8** ±4.2 | +1.7 [-4.3; +7.4] | 43.0 vs 46.6 (100%) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) |
| BẤT KỲ (gộp) | 1103 (603) | 44.5 | 47.4 (3212) | **-2.9** ±1.7 | -0.1 [-2.9; +2.5] | 44.5 vs 47.2 (100%) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) |

#### THẮNG 1:1 (4 giá trước −4 giá, 30 nến) = thắng/(thắng+thua) — Δ thật [dải Đ1] theo TRAIN / TEST / tháng

| Nhóm | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|
| VWAP ngày | +2.4 ±3.8 [-5; +8] (n=181) | -9.8 ±4.7 [-7; +6] (n=116) | +3.0 ±4.8 [-7; +10] (n=115) | -3.3 ±4.8 [-8; +12] (n=118) | -11.1 ±6.3 [-10; +8] (n=64) |
| VWAP tuần | -5.7 ±4.8 [-6; +11] (n=109) | +4.0 ±5.6 [-14; +5] (n=85) | -7.2 ±5.9 [-8; +11] (n=71) | -4.1 ±6.2 [-9; +11] (n=68) | +9.1 ±6.9 [-19; +5] (n=55) |
| VAH/VAL Âu | -6.3 ±3.7 [-5; +6] (n=190) | -3.0 ±4.3 [-9; +6] (n=146) | -6.8 ±4.3 [-7; +8] (n=142) | -3.0 ±5.0 [-8; +10] (n=104) | -3.8 ±5.5 [-11; +6] (n=90) |
| HVN ngày | -7.3 ±4.3 [-5; +5] (n=136) | -5.6 ±4.9 [-11; +14] (n=110) | -8.9 ±5.4 [-7; +6] (n=85) | -1.1 ±4.8 [-6; +13] (n=115) | -16.0 ±7.1 [-21; +14] (n=46) |
| HVN tuần | -2.7 ±7.5 [-13; +13] (n=44) | +5.4 ±4.7 [-11; +6] (n=119) | +5.1 ±9.2 [-25; +16] (n=30) | -19.6 ±12.1 [-15; +33] (n=14) | +6.0 ±4.9 [-12; +6] (n=119) |
| LVN ngày | -9.0 ±6.2 [-10; +6] (n=62) | -0.5 ±5.7 [-2; +15] (n=80) | -12.7 ±6.8 [-9; +7] (n=49) | -2.8 ±6.4 [-11; +12] (n=64) | +7.6 ±9.4 [-3; +22] (n=29) |
| BẤT KỲ (gộp) | -4.4 ±2.3 [-4; +4] (n=577) | -1.7 ±2.6 [-5; +4] (n=526) | -6.4 ±2.8 [-3; +4] (n=393) | -1.4 ±2.9 [-4; +6] (n=396) | -1.1 ±3.5 [-9; +2] (n=314) |

#### THẮNG 1:1 (4 giá trước −4 giá, 30 nến) = thắng/(thắng+thua) — Đ2 theo TRAIN / TEST / tháng: % có cờ vs % không cờ cùng ô

| Nhóm | TRAIN | TEST | T8 | T9 | T10 |
|---|---|---|---|---|---|
| VWAP ngày | 48.1 vs 46.4 | 38.8 vs 48.3 | 47.8 vs 45.4 | 44.9 vs 48.4 | 37.5 vs 46.5 |
| VWAP tuần | 40.4 vs 45.5 | 51.8 vs 47.0 | 38.0 vs 44.5 | 44.1 vs 46.7 | 56.4 vs 46.8 |
| VAH/VAL Âu | 40.0 vs 46.3 | 45.2 vs 45.9 | 38.7 vs 45.7 | 45.2 vs 47.7 | 44.4 vs 46.8 |
| HVN ngày | 39.0 vs 45.4 | 42.7 vs 48.5 | 36.5 vs 44.4 | 47.0 vs 47.3 | 32.6 vs 47.6 |
| HVN tuần | 43.2 vs 45.8 | 52.9 vs 48.6 | 50.0 vs 44.8 | 28.6 vs 49.7 | 52.9 vs 47.2 |
| LVN ngày | 37.1 vs 45.3 | 47.5 vs 48.3 | 32.7 vs 44.7 | 45.3 vs 47.1 | 55.2 vs 47.5 |
| BẤT KỲ (gộp) | 42.5 vs 46.5 | 46.8 vs 48.1 | 39.9 vs 46.2 | 47.0 vs 47.1 | 47.1 vs 47.8 |

### Phần còn lại: % "chưa rõ" (vùng rời bộ/hết phiên khi giá còn neo) và % "hết 30 nến" — có cờ vs không cờ (GỘP, chỉ mô tả)

Cột cuối = đảo / (đảo + xuyên): bỏ "chưa rõ" và "không rõ phía" — THÊM SAU khi thấy "chưa rõ" chênh nhau, KHÔNG đăng ký trước, không phán quyết, chỉ để biết chênh %đảo có phải do "chưa rõ" không.

| Nhóm | chưa rõ % có cờ | chưa rõ % không cờ | hết 30 nến % có cờ | hết 30 nến % không cờ | đảo/(đảo+xuyên) % có cờ vs không cờ |
|---|---|---|---|---|---|
| VWAP ngày | 18.4 | 17.5 | 7.8 | 5.6 | 65.9 (n=258) vs 64.7 |
| VWAP tuần | 16.9 | 17.6 | 7.6 | 5.7 | 67.6 (n=173) vs 64.6 |
| VAH/VAL Âu | 23.6 | 17.1 | 7.4 | 5.6 | 64.4 (n=275) vs 64.8 |
| HVN ngày | 22.8 | 17.2 | 6.8 | 5.7 | 58.8 (n=199) vs 65.1 |
| HVN tuần | 20.4 | 17.5 | 9.9 | 5.6 | 66.7 (n=141) vs 64.7 |
| LVN ngày | 21.4 | 17.5 | 6.0 | 5.7 | 56.4 (n=117) vs 65.1 |
| BẤT KỲ (gộp) | 21.0 | 16.3 | 7.5 | 5.1 | 64.1 (n=928) vs 65.0 |

## 4. Độ nhạy dung sai hợp lưu (chỉ báo, không chọn lại) — Δ thật GỘP (TRAIN / TEST)

| Nhóm | Kết cục | tol 0 | **tol 0,5 (chốt)** | tol 1,5 |
|---|---|---|---|---|
| VWAP ngày | đảo | -2.6 (+3 / -10) n=253 | **-2.2 (+3 / -10) n=347** | +0.3 (+4 / -5) n=544 |
| VWAP ngày | xuyên | -2.2 (-3 / -1) n=253 | **-2.6 (-6 / +2) n=347** | -3.3 (-5 / -1) n=544 |
| VWAP ngày | thắng | -2.8 (-0 / -6) n=218 | **-2.4 (+2 / -10) n=297** | -1.3 (+1 / -5) n=475 |
| VWAP tuần | đảo | +1.7 (+0 / +3) n=165 | **+2.5 (+2 / +3) n=219** | +0.5 (+0 / +1) n=336 |
| VWAP tuần | xuyên | -1.1 (-3 / +2) n=165 | **-2.3 (-4 / +1) n=219** | -2.0 (-2 / -2) n=336 |
| VWAP tuần | thắng | -1.1 (-7 / +5) n=147 | **-1.4 (-6 / +4) n=194** | -4.0 (-7 / -0) n=296 |
| VAH/VAL Âu | đảo | -3.4 (-2 / -5) n=330 | **-3.9 (-2 / -6) n=373** | -3.8 (-3 / -4) n=568 |
| VAH/VAL Âu | xuyên | -2.5 (+1 / -6) n=330 | **-1.6 (+2 / -5) n=373** | -1.5 (+2 / -5) n=568 |
| VAH/VAL Âu | thắng | -5.4 (-8 / -2) n=298 | **-4.8 (-6 / -3) n=336** | -2.8 (-5 / -1) n=505 |
| HVN ngày | đảo | -8.9 (-10 / -7) n=251 | **-10.6 (-12 / -9) n=285** | -8.4 (-10 / -7) n=367 |
| HVN ngày | xuyên | +1.4 (+2 / +1) n=251 | **+1.1 (+1 / +1) n=285** | +1.2 (+1 / +1) n=367 |
| HVN ngày | thắng | -4.5 (-7 / -2) n=217 | **-6.4 (-7 / -6) n=246** | -3.8 (-4 / -4) n=320 |
| HVN tuần | đảo | +0.3 (+2 / -0) n=179 | **-3.2 (+0 / -5) n=196** | -2.6 (+3 / -5) n=212 |
| HVN tuần | xuyên | -2.7 (+2 / -3) n=179 | **-3.9 (+1 / -4) n=196** | -4.4 (+0 / -5) n=212 |
| HVN tuần | thắng | +5.5 (-1 / +7) n=154 | **+3.8 (-3 / +5) n=163** | +2.3 (-3 / +4) n=174 |
| LVN ngày | đảo | -12.9 (-12 / -14) n=117 | **-9.9 (-9 / -11) n=159** | -3.9 (-5 / -3) n=245 |
| LVN ngày | xuyên | +5.7 (+9 / +4) n=117 | **+4.5 (+6 / +4) n=159** | -0.9 (-2 / +1) n=245 |
| LVN ngày | thắng | -7.4 (-11 / -5) n=104 | **-3.8 (-9 / -0) n=142** | -2.2 (-9 / +3) n=222 |
| BẤT KỲ (gộp) | đảo | -4.8 (-4 / -6) n=1082 | **-5.3 (-3 / -8) n=1262** | -4.8 (-3 / -7) n=1671 |
| BẤT KỲ (gộp) | xuyên | -0.9 (-0 / -1) n=1082 | **-1.9 (-1 / -2) n=1262** | -2.7 (-2 / -2) n=1671 |
| BẤT KỲ (gộp) | thắng | -3.0 (-6 / -0) n=952 | **-2.9 (-4 / -2) n=1103** | -3.3 (-5 / -2) n=1472 |

## 5. Phán quyết theo luật đã đăng ký

| Nhóm | Kết cục | Đ1 | Đ2 | Δ cùng dấu ở 3 mức dung sai? | **KẾT LUẬN** |
|---|---|---|---|---|---|
| VWAP ngày | đảo | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | KHÔNG | ≈ đối chứng |
| VWAP ngày | xuyên | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| VWAP ngày | thắng | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| VWAP tuần | đảo | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| VWAP tuần | xuyên | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| VWAP tuần | thắng | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| VAH/VAL Âu | đảo | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| VAH/VAL Âu | xuyên | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| VAH/VAL Âu | thắng | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| HVN ngày | đảo | ≈ đối chứng (|hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| HVN ngày | xuyên | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| HVN ngày | thắng | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| HVN tuần | đảo | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | KHÔNG | ≈ đối chứng |
| HVN tuần | xuyên | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| HVN tuần | thắng | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | ≈ đối chứng (TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| LVN ngày | đảo | ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| LVN ngày | xuyên | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) | KHÔNG | ≈ đối chứng |
| LVN ngày | thắng | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| BẤT KỲ (gộp) | đảo | ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số) | ≈ đối chứng (|hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| BẤT KỲ (gộp) | xuyên | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |
| BẤT KỲ (gộp) | thắng | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) | có | ≈ đối chứng |

Số ô vượt Đ1: 0 / 21 · vượt Đ2: 0 / 21 · vượt cả hai + bền dung sai: **0 / 21**.

## 6. Bối cảnh (mục 5a): CHÍNH mức SessionZones một mình (không cần vùng VCL)

Mỗi mức = vùng giả rộng 2 giá (tâm ± 1), cùng máy lần chạm; đối chứng = cùng mức dời 3–15 giá (cùng δ theo phiên, 100 bản). Không lọc bán kính. Đây là "mức một mình", để biết hợp lưu có thêm gì so với từng mức riêng.

| Mức | n lần chạm | % đảo: thật · Đ1 TB [5–95] | % xuyên: thật · Đ1 TB [5–95] | thắng 1:1: thật · Đ1 TB [5–95] | phán quyết đảo · xuyên · thắng |
|---|---|---|---|---|---|
| VWAP ngày | 667 | **53.1** ±1.9 · Đ1 59.8 [57.0; 62.8] | **41.2** ±1.9 · Đ1 39.0 [35.7; 41.8] | **46.2** ±2.0 · Đ1 49.0 [45.7; 52.5] | ≈ đối chứng (trong dải 5–95% ở TRAIN; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95% ở TRAIN; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| VWAP tuần | 382 | **56.8** ±2.5 · Đ1 57.7 [53.3; 62.3] | **40.8** ±2.5 · Đ1 40.8 [36.5; 45.6] | **44.9** ±2.6 · Đ1 47.7 [43.3; 51.1] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) |
| VAH/VAL Âu | 721 | **55.6** ±1.9 · Đ1 56.2 [53.2; 59.1] | **41.9** ±1.8 · Đ1 40.7 [38.3; 43.3] | **45.4** ±1.9 · Đ1 48.4 [45.2; 51.0] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95% ở TEST; |hiệu| ≤ 2 sai số) |
| HVN ngày | 342 | **55.6** ±2.7 · Đ1 56.8 [52.9; 60.1] | **42.4** ±2.7 · Đ1 41.7 [38.5; 45.2] | **48.4** ±2.8 · Đ1 47.7 [43.8; 52.4] | ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| HVN tuần | 147 | **60.5** ±4.0 · Đ1 57.5 [52.5; 64.0] | **38.8** ±4.0 · Đ1 41.0 [34.8; 46.4] | **50.0** ±4.3 · Đ1 47.0 [41.1; 53.5] | ≈ đối chứng (trong dải 5–95%; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95%; TRAIN/TEST ngược dấu; < 2/3 tháng cùng dấu; |hiệu| ≤ 2 sai số) |
| LVN ngày | 332 | **55.1** ±2.7 · Đ1 58.2 [54.3; 62.3] | **43.1** ±2.7 · Đ1 40.4 [36.1; 44.1] | **45.2** ±2.8 · Đ1 48.3 [43.5; 52.5] | ≈ đối chứng (trong dải 5–95% ở TEST; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95% ở TEST; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) · ≈ đối chứng (trong dải 5–95% ở TEST; TRAIN/TEST ngược dấu; |hiệu| ≤ 2 sai số) |

TRAIN / TEST (thật · Đ1 trung bình [5–95]):

| Mức | Kết cục | TRAIN | TEST |
|---|---|---|---|
| VWAP ngày | dao | 55.6 · Đ1 59.1 [55.4; 63.2] (n=381) | 49.7 · Đ1 61.0 [56.2; 66.0] (n=286) |
| VWAP ngày | xuyen | 38.8 · Đ1 40.0 [35.7; 43.6] (n=381) | 44.4 · Đ1 37.5 [32.3; 42.7] (n=286) |
| VWAP ngày | win | 49.4 · Đ1 48.8 [44.0; 53.0] (n=346) | 41.8 · Đ1 49.4 [44.2; 55.0] (n=256) |
| VWAP tuần | dao | 56.0 · Đ1 57.8 [51.7; 63.1] (n=232) | 58.0 · Đ1 57.5 [52.3; 62.9] (n=150) |
| VWAP tuần | xuyen | 40.5 · Đ1 40.9 [35.9; 46.8] (n=232) | 41.3 · Đ1 40.8 [35.4; 45.7] (n=150) |
| VWAP tuần | win | 45.1 · Đ1 47.7 [42.3; 53.6] (n=213) | 44.8 · Đ1 47.6 [41.0; 54.1] (n=143) |
| VAH/VAL Âu | dao | 55.0 · Đ1 56.4 [52.4; 60.1] (n=404) | 56.5 · Đ1 56.0 [51.5; 61.4] (n=317) |
| VAH/VAL Âu | xuyen | 42.6 · Đ1 40.6 [37.2; 44.4] (n=404) | 41.0 · Đ1 40.7 [35.5; 45.3] (n=317) |
| VAH/VAL Âu | win | 44.5 · Đ1 48.7 [44.6; 53.1] (n=384) | 46.5 · Đ1 48.0 [44.4; 52.4] (n=297) |
| HVN ngày | dao | 52.6 · Đ1 57.3 [51.7; 63.0] (n=215) | 60.6 · Đ1 55.9 [50.8; 61.9] (n=127) |
| HVN ngày | xuyen | 45.1 · Đ1 41.7 [36.4; 47.2] (n=215) | 37.8 · Đ1 41.8 [36.3; 47.7] (n=127) |
| HVN ngày | win | 46.7 · Đ1 48.1 [42.5; 53.3] (n=199) | 51.3 · Đ1 47.1 [39.8; 53.5] (n=117) |
| HVN tuần | dao | 58.5 · Đ1 57.5 [48.2; 67.4] (n=53) | 61.7 · Đ1 57.4 [49.5; 64.6] (n=94) |
| HVN tuần | xuyen | 41.5 · Đ1 41.3 [32.5; 51.0] (n=53) | 37.2 · Đ1 40.9 [33.3; 47.6] (n=94) |
| HVN tuần | win | 46.2 · Đ1 47.7 [37.5; 57.4] (n=52) | 52.4 · Đ1 46.3 [37.8; 55.2] (n=84) |
| LVN ngày | dao | 49.4 · Đ1 57.8 [53.2; 62.8] (n=178) | 61.7 · Đ1 58.8 [52.7; 65.3] (n=154) |
| LVN ngày | xuyen | 50.0 · Đ1 41.0 [36.6; 45.7] (n=178) | 35.1 · Đ1 39.5 [32.2; 46.0] (n=154) |
| LVN ngày | win | 37.3 · Đ1 46.9 [41.3; 52.6] (n=169) | 54.6 · Đ1 50.3 [43.7; 55.6] (n=141) |

## 7. Hình minh hoạ

- TRAIN phiên 2026-07-29: [img/hop_luu_sz_TRAIN_2026-07-29.png](img/hop_luu_sz_TRAIN_2026-07-29.png)
- TEST phiên 2026-10-13: [img/hop_luu_sz_TEST_2026-10-13.png](img/hop_luu_sz_TEST_2026-10-13.png)

Chọn phiên có nhiều lần chạm của vùng hợp lưu nhất trong mỗi tách (chọn để minh hoạ, KHÔNG phải ca điển hình).

<!-- NHAN-XET -->
## Kết luận (viết tay sau khi chạy)

1. **Hợp lưu KHÔNG làm vùng mạnh hơn.** 0 / 21 ô vượt Đ1, 0 / 21 ô vượt Đ2 theo đúng ngưỡng đã đăng ký ⇒ mọi nhóm, mọi kết cục: **≈ đối chứng**.
2. Con số ước lượng còn **nghiêng về phía YẾU hơn**, không phải mạnh hơn: nhóm "bất kỳ" đảo chiều 47,1% so với 52,5% vùng không hợp lưu
   (Δ −5,3 ±1,6); cùng ô rộng × khoảng cách thì 47,1% so với 51,3%; "thắng 1:1" 44,5% so với 47,4%. Một phần chênh lệch này là do cơ chế:
   khi dời mức SessionZones đi 3–15 giá, Δ vẫn âm trung bình −1,9. Phần còn lại không qua được ngưỡng ở TRAIN.
3. Âm nhiều nhất là **HVN ngày** (đảo 41,1% so với 51,7%, Δ −10,6 ±3,0) và **LVN ngày** (41,5% so với 51,4%). Hai nhóm này **suýt** vượt ngưỡng
   nhưng hụt ít nhất một điều kiện (cả hai đều hụt "|hiệu| > 2 sai số" ở TRAIN hoặc TEST; LVN ngày còn nằm trong dải Đ1 ở TRAIN). Một phần do vùng hợp lưu bị "chưa rõ" nhiều hơn (22,8% so với 17,2%:
   vùng rời bộ hiển thị khi giá còn neo); bỏ "chưa rõ" ra thì đảo/(đảo+xuyên) vẫn thấp hơn (58,8% so với 65,1%, số liệu mô tả, không đăng ký
   trước). Hướng này khớp với phép đo cũ "HVN không phải mốc phản ứng, sau cú phá thì nghiêng đi tiếp" — nhưng ở đây **chưa đủ chắc để gọi là có**.
4. **VWAP tuần** là nhóm duy nhất có Δ đảo chiều dương ở cả TRAIN, TEST và 3 tháng (+2,5 ±3,5 gộp), nhưng nằm gọn trong dải đối chứng ⇒ nhiễu.
5. **Mức SessionZones một mình** (mục 6): cả 6 loại ≈ mức dời ngẫu nhiên; VWAP ngày còn đảo ÍT hơn mức dời (53,1% so với 59,8%). Không có
   bằng chứng mức nào là "mốc phản ứng" ⇒ hợp lưu với chúng không có gì để cộng thêm.
6. **Nếu chỉ giữ vùng hợp lưu:** trên chart trung bình còn **1,1 vùng** (thay vì 6,4); 68% thời gian có ít nhất 1 vùng; mỗi phiên ~14 vùng mới
   (21,5% tổng số). Nghĩa là lọc hợp lưu làm chart gọn hơn rất nhiều, nhưng **không** chọn ra vùng tốt hơn.

## Giới hạn
- **n nhỏ theo nhóm:** 159–373 lần chạm có cờ mỗi nhóm (gộp), chia TRAIN/TEST/tháng còn 14–205 ⇒ sai số ±4–13 điểm; chỉ hiệu ≥ ~8–10 điểm mới có cơ hội qua ngưỡng.
- **Mẫu chồng lấn:** nhiều lần chạm cùng một vùng, nhiều vùng cùng một cú giá ⇒ sai số nhị thức **đánh giá thấp**; dải thật rộng hơn bảng.
- **Đa so sánh:** 42 phán quyết chính + 18 ở mục 6. Có vài ô "suýt" là điều chờ đợi được do ngẫu nhiên; kể cả nếu có ô vượt cũng phải kiểm tiếp
  (đã đặt luật: phải vượt cả Đ1 và Đ2, bền ở 3 mức dung sai) — không ô nào tới bước đó.
- **Khác C#:** HVN/LVN ngày lấy từ profile phiên CME trước (kernel), C# dùng 24 giờ cuối cập nhật theo block; không mô phỏng trần 5 vùng, gộp vùng,
  mục tiêu xa của SessionZones. VA Âu: 60% vùng hợp lưu VA Âu là **tự trùng do cấu tạo** (VCL lấy chính VAH/VAL Âu làm mốc loại C).
- **"Thắng 1:1" chỉ là mô tả:** chưa phí, chưa trượt giá, giả định khớp lệnh chờ ở biên vùng; luật "một nến chạm cả hai = thua" làm số tuyệt đối thấp hơn 50%.
- **Một hợp đồng (GCZ26), một mùa (07-29 → 10-21), 61 phiên** — không ngoại suy sang giai đoạn khác.
