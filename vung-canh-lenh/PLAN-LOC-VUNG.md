# PLAN-LOC-VUNG — lọc bớt khối trong chế độ "Hiện TẤT CẢ vùng trong lịch sử" (2 hạng, không nhìn trước)

Fable viết 2026-10-23 cho Opus implement. Đọc trước: `PLAN-LICH-SU.md` (khối `VLichSu`, `LichSuTracker`), `README.md` mục chế độ lịch sử,
`research/lich_su.py`, `research/report/LICH-SU.md`, **`research/loc_vung_bench.py` + `research/report/LOC-VUNG-BENCH.md`** (số đo của kế hoạch này).

**Nhu cầu (người học):** chế độ lịch sử hiện ~60 khối/24 giờ — vẫn quá nhiều. Muốn chỉ giữ khối "vừa đủ dài, mạnh, có nhiều lần chạm" để
xem lại signal Benzo Trader: tại nến signal có những kháng cự/hỗ trợ nào.

## 0. Kết luận trước (đọc 6 dòng này là đủ)

1. **Bộ lọc đề xuất là bộ lọc để GỌN / dễ đọc, KHÔNG phải lọc chất lượng dự báo.** Đã đo 19 bộ lọc ứng viên với đối chứng khớp khoảng cách
   (mục 2.3): khối thật sau khi "lên hạng" **không** đảo chiều nhiều hơn khối giả cùng cỡ, cùng khoảng cách, cùng tuổi thọ — ở cả TRAIN lẫn TEST,
   nhiều bộ lọc còn **thấp hơn** đối chứng. README phải viết đúng câu này.
2. Chọn **hạng 1 = khối đã có ≥ 1 lần chạm lại VÀ sống ≥ 60 phút** (lên hạng tại nến đầu tiên thoả cả hai, không hồi tố). Trên 90 ngày:
   giữ **39,7%** khối ⇒ **23 khối/24 h (p90 32)** thay vì 60 (p90 81); file 29 ngày: 25 (p90 33).
3. Tại 163 nến signal Benzo: TB **2,2 khối hạng 1** đang hiệu lực (p90 4); **74%** signal có khối hạng 1 cách giá ≤ 5 giá (84% ≤ 10 giá).
   Phần còn lại của bộ vùng lúc signal (TB 6,7 khối sống) **không mất**: lớp tiêu điểm theo chuột vẫn vẽ mọi khối sống tại nến đó bằng viền mảnh (hạng 2).
4. Không thể vừa "≈ 15–25 khối/24 h" vừa "thấy đủ 6–7 vùng tại signal" bằng một bộ lọc theo bằng chứng quá khứ: tại nến signal, **58% khối đang sống
   chưa có lần chạm lại nào** và 31% mới sống < 60 phút (mục 1.4). Vì vậy thiết kế **2 hạng**: hạng 1 vẽ suốt lịch sử, hạng 2 chỉ hiện tại nến tiêu điểm.
5. Hai chế độ phải tách bạch: **(a) xem lại signal** = chỉ khối có `t_q ≤ t` (chart và mọi số đo dùng cái này); **(b) trang trí hồi tố** (vẽ cả phần
   trước `t_q`) chỉ dùng cho phần đuôi mờ của khối hạng 1 để người học thấy lần chạm đã đưa nó lên hạng — ghi rõ, không đếm vào số nào.
6. 0 cài đặt mới. Hằng mới: `LsRankTouch = 1`, `LsRankAgeMin = 60` (= `LsGapMin`, dùng lại).

---

## 1. Chẩn đoán — khối lịch sử gồm những gì (90 ngày GCZ26, 4 107 khối, 65 phiên; TRAIN 2 567 / TEST 1 540)

Số từ `LOC-VUNG-BENCH.md` (khối = `VLichSu` theo đúng `LichSuTracker`; lần chạm = máy τ 0 · E 2 · G 5 chạy trên dải cố định của khối).

### 1.1 Phân phối
| Chỉ số | 90 ngày | TRAIN | TEST |
|---|---|---|---|
| sống (phút) p25 · p50 · p75 · p90 | 30 · 73 · 172 · 343 | 28 · 71 · 165 · 339 | 32 · 78 · 182 · 346 |
| < 15 phút · < 30 · < 60 · ≥ 120 | 13% · 25% · 44% · 35% | 14 · 26 · 45 · 33 | 12 · 23 · 42 · 37 |
| số lần chạm lại (sau nến tạo) 0 · 1 · 2 · 3 · ≥4 | **36%** · 35% · 17% · 7% · 5% | 37 · 34 · 18 · 7 · 5 | 36 · 35 · 16 · 7 · 6 |
| kết thúc: hết hạn · xuyên phá | 53% · 46% | 53 · 47 | 54 · 45 |
| kết cục mọi lần chạm: đảo · xuyên · chưa rõ | 59% · 38% · 3% (n 5 071) | 59 · 39 · 3 | 61 · 37 · 3 |
| rộng p50 · p90 (giá); = 2 giá | 2,1 · 3,8; 47% | 2,2 · 3,9 | 2,0 · 3,7 |
| khoảng cách giá đóng → biên gần lúc tạo p50 · p90 (giá); giá trong vùng | 6,6 · 20,4; 6% | 6,9 · 23,6 | 6,1 · 17,5 |
| slot lúc tạo N · K · F; từng gần | 78% · 11% · 11%; 92% | | |
| loại mốc lúc tạo (mask) B · B15 · C · D; **chỉ số tròn (D)** | 55% · 36% · 19% · 58%; **38%** | 53 · 35 · 18 · 61; 41 | 58 · 38 · 22 · 54; 33 |

### 1.2 "Rác"
- **36,4% khối không bao giờ được chạm lại** sau nến tạo; **20%** vừa 0 chạm lại vừa sống < 60 phút; 13% sống < 15 phút.
- Điểm gãy tự nhiên: sống trung vị theo số lần chạm lại **0 → 50 phút · 1 → 52 · 2 → 108 · 3+ → 226**. Khối có 1 chạm lại không sống lâu hơn
  khối 0 chạm lại; từ 2 chạm lại trở lên tuổi thọ nhân đôi.
- Lần chạm lại thứ 1 đến sau khi tạo: p50 **22 phút** (p90 140); lần thứ 2: p50 **79 phút** (p90 253).

### 1.3 Hình học của "nhiều lần chạm"
% đảo chiều theo lần chạm thứ k trên khối: k=1 **61,7%** · k=2 58,4% · k≥3 **53,5%** (xuyên 36 → 38 → 42%). Càng nhiều lần chạm, lần sau càng
hay bị xuyên — giống LAN-CHAM mục H và giống đối chứng (mục 2.3). "Nhiều lần chạm" chọn ra **vùng giá đang đi ngang quanh đó**, không phải vùng "giữ giá tốt".

### 1.4 Khối sống tại nến signal Benzo (163 signal A ⇒ 1 096 khối-signal)
Tuổi p25 · p50 · p75 = 44 · 125 · 341 phút; **17% mới < 30 phút, 31% < 60 phút**; số lần chạm lại đã có tới lúc signal: **0 → 58%**, 1 → 24%, ≥2 → 18%.
⇒ Bộ vùng tại signal phần lớn là vùng **chưa có bằng chứng** gì ngoài việc đang hiện; bộ lọc nào theo bằng chứng quá khứ cũng sẽ ẩn hơn nửa.

---

## 2. Benchmark bộ lọc (không nhìn trước: khối chỉ "lên hạng" từ nến `t_q` khi đã thoả tiêu chí bằng dữ liệu ≤ `t_q`)

Định nghĩa `t_q`: **tuổi ≥ A** ⇒ nến đầu có `thời gian − StartTime ≥ A` (nếu còn sống); **≥ k chạm lại** ⇒ nến **bắt đầu** lần chạm thứ k sau nến tạo
(= lúc `NChamLai` đạt k); **≥ k đảo chốt** ⇒ nến **chốt** (sau G nến yên) của lần đảo chiều thứ k; VÀ = max, HOẶC = min. `t_q > End` ⇒ không bao giờ lên hạng.

### 2.1 Gọn bao nhiêu, còn thấy gì tại signal (90 ngày; cột 29 ngày để đối chiếu)
| Bộ lọc | % khối lên hạng | khối/24 h p50 · p90 | hạng 1 đang hiệu lực tại signal TB · p90 | signal có khối hạng 1 ≤ 5 giá / ≤ 10 giá | phủ Display tại signal | 29 ngày: khối/24 h · ≤ 5 giá |
|---|---|---|---|---|---|---|
| tất cả (hiện nay) | 100% | 60 · 81 | 6,7 · 8 | 98% / 99% | 97% | 65 · 96% |
| tuổi ≥ 30 | 75% | 46 · 60 | 5,6 · 7 | 93 / 96 | 81% | 49 · 91% |
| tuổi ≥ 60 | 56% | 36 · 45 | 4,6 · 6 | 80 / 90 | 67% | 38 · 72% |
| tuổi ≥ 120 | 35% | 22 · 29 | 3,5 · 6 | 56 / 68 | 50% | 22 · 48% |
| ≥ 1 chạm lại | 62% | 35 · 50 | 2,8 · 4 | 91 / 95 | 41% | 39 · 87% |
| ≥ 2 chạm lại | 27% | 15 · 23 | 1,2 · 2 | 55 / 62 | 17% | 17 · 57% |
| ≥ 3 chạm lại | 11% | 6 · 10 | 0,5 · 1 | 29 / 34 | 8% | 6 · 32% |
| ≥ 1 đảo chốt | 37% | 22 · 31 | 2,4 · 4 | 69 / 79 | 34% | 24 · 65% |
| ≥ 2 đảo chốt | 16% | 9 · 14 | 1,0 · 2 | 32 / 45 | 14% | 10 · 32% |
| ≥ 1 chạm lại VÀ tuổi ≥ 30 | 51% | 30 · 41 | 2,6 · 4 | 86 / 92 | 38% | 32 · 83% |
| ≥ 1 chạm lại VÀ tuổi ≥ 45 | 45% | 27 · 36 | 2,4 · 4 | 79 / 86 | 34% | 29 · 69% |
| **≥ 1 chạm lại VÀ tuổi ≥ 60 (chọn)** | **39,7%** | **23 · 32** | **2,2 · 4** | **74 / 84** | **32%** | **25 · 63%** |
| ≥ 2 chạm lại VÀ tuổi ≥ 60 | 23% | 13 · 19 | 1,1 · 2 | 49 / 57 | 16% | 15 · 46% |
| ≥ 2 chạm lại HOẶC tuổi ≥ 120 | 46% | 29 · 37 | 3,7 · 6 | 72 / 80 | 54% | 30 · 70% |
| ≥ 1 đảo chốt VÀ tuổi ≥ 60 | 30% | 18 · 25 | 2,0 · 4 | 58 / 72 | 29% | 19 · 52% |
| ≥ 2 chạm lại HOẶC (≥ 1 chạm lại VÀ tuổi ≥ 120) | 36% | 21 · 29 | 1,9 · 3 | 68 / 76 | 28% | 23 · 65% |
| (≥ 1 chạm lại VÀ tuổi ≥ 60) HOẶC tuổi ≥ 180 | 46% | 29 · 38 | 3,7 · 6 | 74 / 85 | 53% | 30 · 65% |

Phủ Display = % vùng Display live tại nến signal có khối hạng 1 cùng dải. Thêm 62 signal B v3 (213 signal) cho cùng số (cột "A+B3" trong bench).

### 2.2 Cách đọc bảng
- Hàng nào cũng là **đánh đổi gọn ↔ thấy**: mọi bộ lọc xuống ≤ 25 khối/24 h đều mất ≥ 25% signal không còn khối hạng 1 trong 5 giá, và chỉ phủ ≈ 30% bộ
  vùng live tại signal. Đó là hệ quả của 1.4, không chỉnh tham số mà hết được.
- Tuổi đơn thuần (≥ 120) giữ nhiều khối tại signal hơn (3,5) nhưng là những khối **xa giá** (cách khối gần nhất trung vị 3,1 giá; ≤ 5 giá chỉ 56%) và
  không đụng gì tới "lần chạm". Lọc theo chạm lại giữ khối **sát giá** (trung vị 0,1–0,9 giá).

### 2.3 "Mạnh" có thật không — kết cục lần chạm SAU khi lên hạng, khối thật vs khối giả (10 bản/loại)
Đối chứng **GƯƠNG (khớp khoảng cách)**: cùng rộng, cùng nến tạo, **cùng khoảng cách tới giá đóng lúc tạo** (phản chiếu qua giá đóng, nhiễu ±0,5 giá),
sống tối đa bằng khối thật (xuyên phá riêng thì ngắn hơn), **áp cùng bộ lọc**. Đối chứng **DỜI** = Đ1 của LAN-CHAM (dời cả bộ 3–15 giá).
Số = % đảo chiều của các lần chạm bắt đầu sau `t_q`; đối chứng ghi trung bình [5–95%].

| Bộ lọc | TRAIN: thật (n) · gương · dời | TEST: thật (n) · gương · dời | đảo/(đảo+xuyên) TRAIN thật · gương | TEST thật · gương |
|---|---|---|---|---|
| tất cả | 57,9 (2 886) · 56,5 [56,1–57,1] · 51,6 | 59,9 (1 786) · 58,8 [58,6–59,0] · 52,1 | 59,5 · 59,4 | 61,8 · 62,0 |
| ≥ 1 chạm lại | 55,2 (1 243) · 57,3 [56,6–57,8] · 53,7 | 56,9 (803) · 60,8 [59,6–62,1] · 54,1 | 57,0 · 58,9 | 59,7 · 64,1 |
| ≥ 2 chạm lại | **53,7** (501) · 58,4 [57,1–60,5] · 53,8 | **54,2** (354) · 60,2 [58,6–61,8] · 56,3 | 55,6 · 59,8 | 57,5 · 64,3 |
| ≥ 3 chạm lại | 56,2 (210) · 61,0 [57,7–64,4] · 53,3 | **50,0** (162) · 64,9 [63,3–67,1] · 59,1 | 57,8 · 62,4 | 53,6 · 67,4 |
| ≥ 1 đảo chốt | 55,8 (1 312) · 58,5 [57,7–59,1] · 54,8 | 56,6 (822) · 61,5 [60,1–62,5] · 55,8 | 57,2 · 60,2 | 58,8 · 64,2 |
| **≥ 1 chạm lại VÀ tuổi ≥ 60** | **55,8** (895) · 58,7 [57,9–59,5] · 52,1 | **54,7** (594) · 61,3 [60,2–62,5] · 54,2 | 58,0 · 61,0 | 58,1 · 65,2 |
| tuổi ≥ 120 | 56,4 (759) · 54,9 [53,7–55,7] · 46,3 | 56,0 (514) · 60,4 [59,3–61,5] · 48,8 | 58,1 · 58,5 | 58,5 · 65,1 |

Phán quyết (ngưỡng đăng ký ở LAN-CHAM: phải vượt dải 5–95% của đối chứng cùng dấu ở cả TRAIN và TEST):
- **Không bộ lọc nào làm khối thật đảo chiều nhiều hơn đối chứng khớp khoảng cách.** Với bộ lọc chọn, khối thật **thấp hơn** gương ở cả hai tập
  (TRAIN −2,9 · TEST −6,6 điểm, ngoài dải 5–95% của gương về phía **xấu**). Lọc "≥ 2/3 chạm lại" còn xấu hơn (TEST 54 và 50 vs 60 và 65).
- Giải thích cơ chế (không phải "vùng thật yếu"): khối thật sống chừng nào engine còn hiện nó = giá còn **quanh** nó; khối gương cùng tuổi thọ nhưng giá
  không "đeo bám" ⇒ lần chạm của gương ít hơn (0,7 vs 0,9/khối) và dễ là lần quét-rồi-đi (đảo nhanh). Cùng bẫy đã ghi ở LAN-CHAM A2. Khối thật
  đủ điều kiện ở vùng giá đi ngang ⇒ lần chạm sau hay thành xuyên. Tỉ lệ lên hạng thật 40% vs gương 25% cũng do cơ chế này, **không** phải bằng chứng gì.
- Khối lượng footprint trong dải suốt lần chạm (÷ trung vị 50 nến trước) — định nghĩa "mạnh" thứ ba: % đảo theo tam phân vị thấp · giữa · cao =
  **75 · 53 · 49%** ở khối thật, **75 · 52 · 47%** ở khối gương (TRAIN; TEST 75 · 57 · 49 vs 76 · 54 · 52). Giống hệt ⇒ là hình học (chạm ngắn = ít khối
  lượng = đảo nhanh), không phải độ mạnh. **Không dùng khối lượng làm tiêu chí.**
- Điểm vùng (`Score`): LAN-CHAM mục J đã kết luận không phải độ mạnh; không đo lại.

⇒ **Bộ lọc là để gọn.** Mọi chữ trên UI/README: "khối đã được chạm lại và sống ≥ 1 giờ" — không "mạnh", không "được tôn trọng".

### 2.4 Phương án đã loại
| Phương án | Lý do |
|---|---|
| ≥ 2 chạm lại (điểm gãy tuổi thọ 52 → 108 phút) | 15 khối/24 h đúng mục tiêu dưới, nhưng tại signal chỉ 1,2 khối, 45% signal không có khối nào trong 5 giá; và lần chạm sau xấu hơn đối chứng rõ nhất |
| ≥ 1 đảo chốt | gần bằng phương án chọn (22/24 h, 69% ≤ 5 giá) nhưng lên hạng trễ G nến sau khi giá rời đi, và lần chạm ở nến tạo cũng tính ⇒ khối chưa từng được *quay lại* vẫn lên hạng — trái ý "nhiều lần chạm" |
| tuổi ≥ 120 đơn thuần | giữ khối xa giá (≤ 5 giá 56%), không liên quan lần chạm |
| ≥ 1 chạm lại đơn thuần | 35/24 h — chưa đủ gọn (còn 58% khối) |
| HOẶC tuổi ≥ 180 | thêm 6 khối/24 h toàn khối xa (phủ 53% nhưng ≤ 5 giá không đổi 74%) |
| lọc theo loại mốc (bỏ "chỉ số tròn" 38%) | mốc D nằm đúng chỗ giá đi; LAN-CHAM: vùng chỉ-D "chưa rõ" ít hơn, không yếu hơn; bỏ là bỏ theo niềm tin |
| lọc theo điểm / khối lượng | đã đo không phải độ mạnh (2.3, LAN-CHAM J) |
| **xoá hẳn** khối không lên hạng | mất 6,7 → 2,2 khối tại signal — mất chính thứ người học muốn xem; thay bằng hạng 2 tại tiêu điểm |
| lên hạng hồi tố từ `Start` (vẽ đậm cả phần trước `t_q`) | nhìn trước; chỉ cho phép ở phần đuôi mờ (2.5), không đếm |
| thêm cài đặt "mức lọc" | 0 cài đặt mới là nguyên tắc của bộ; muốn chặt hơn thì đổi hằng (`LsRankTouch = 2`) và chạy lại bench |

---

## 3. Thiết kế

### 3.1 Lên hạng (trong `LichSuTracker.Step`, sau bước (2) máy lần chạm, trước (3) hết hạn)
```
VLichSu: int TQ = −1; DateTime TQTime;           // nến lên hạng; −1 = chưa
mỗi nến i, với khối đang sống h có TQ < 0:
    if (h.NChamLai >= Vcl.LsRankTouch && (bar.Time − h.StartTime).TotalMinutes >= Vcl.LsRankAgeMin) { h.TQ = i; h.TQTime = bar.Time; }
hằng: public const int LsRankTouch = 1; public const double LsRankAgeMin = 60.0;   // = LsGapMin
```
- `NChamLai` tăng ở **nến bắt đầu** lần chạm (đã có) ⇒ không nhìn trước. Tuổi dùng `>=` (Python `searchsorted(..., 'left')` cùng nghĩa).
- Khối kết thúc ở chính nến i (xuyên phá/hết hạn) vẫn có thể lên hạng ở nến đó nếu `TQ ≤ End`; để đơn giản: đặt TQ **trước** khi xét kết thúc, rồi khi
  kết thúc nếu `TQ > End` (xuyên phá kẹp `End = i − G`) ⇒ `TQ = −1` (chưa từng đủ điều kiện lúc còn hiệu lực). Test riêng.
- **Không xuống hạng**: hạng 1 giữ tới `End`. Kết thúc khối như cũ (xuyên phá, hết hạn). Dải, vai, `NChamLai`, `TungGan` không đổi.
- `_lichsu.csv` thêm cột `tq_utc` (rỗng nếu −1). `lich_su.py` port thêm `tq`, parity từng dòng gồm cột này.

### 3.2 Vẽ (`PaintLichSu`)
Hai hạng, một đối tượng:
| | Hạng 1 (`TQ ≥ 0`) | Hạng 2 (`TQ < 0`) |
|---|---|---|
| Ngoài tiêu điểm | vẽ từ **`TQTime`** tới `EndTime`/mép phải: tô alpha 35, viền 110, nhãn `lo–hi` ở mép trái (từ `TQTime`) nếu vừa | **không vẽ** |
| Phần `[StartTime, TQTime)` | **đuôi mờ**: không tô, viền alpha 40 (trang trí hồi tố — cho thấy lần chạm đã đưa nó lên hạng; ghi README) | — |
| Sống tại `tF` (nến tiêu điểm) | tô alpha 55, viền 150, nhãn (như hiện nay) — **chỉ khi `TQTime ≤ tF`**; nếu `StartTime ≤ tF < TQTime` ⇒ vẽ như hạng 2 | **viền mảnh** alpha 90, không tô, nhãn `lo–hi` nếu `ShowLabels` — chỉ đoạn `[StartTime, EndTime]` |
| Vùng Live (`End < 0`) | như trên; nhãn live mép phải như hiện nay | nếu là vùng live hiện tại: viền đứt + nhãn live (gộp với cơ chế `BiChan` hiện có) |
- Tiêu điểm `tF` theo chuột/mép phải như PLAN-LICH-SU 2.5. **Số khối đậm tại `tF` = khối có `TQTime ≤ tF ≤ EndTime`** (TB 2,2 tại signal);
  số khối viền mảnh tại `tF` = khối sống khác (TB 4,5) ⇒ tổng vẫn 6,7 như LICH-SU.md tiêu chí 9.
- Đường dọc tại `tF` giữ. `ShowFar` tắt ⇒ ẩn khối `!TungGan` như cũ. Không nhãn trong khối < 15 phút (hằng cũ).
- Chế độ gọn (tắt `ShowAllHistory`) không đổi.

### 3.3 Chữ trên README (bắt buộc)
"Khối **hạng 1** = khối đã có ít nhất một lần giá quay lại chạm và đã hiện ≥ 60 phút; vẽ suốt lịch sử (≈ 23 khối/24 giờ). Khối còn lại chỉ hiện khi
rê chuột tới nến đang soi. **Đây là lọc để chart gọn, không phải lọc vùng mạnh**: đã đo (LOC-VUNG-BENCH.md) — sau khi lên hạng, khối hạng 1 không bật
giá nhiều hơn khối giả cùng cỡ, cùng khoảng cách; vùng được chạm nhiều lần là vùng giá đang đi ngang quanh đó, lần sau còn hay bị xuyên hơn."

---

## 4. Tiêu chí nghiệm thu (đo trên replay 90 ngày, in vào `report/LOC-VUNG.md`; cột 29 ngày đối chiếu)
| # | Tiêu chí | Ngưỡng | Đã đo (Python) |
|---|---|---|---|
| 1 | % khối lên hạng 1 | 38–42% | 39,7% (29 ngày 39,7%) |
| 2 | khối hạng 1 thấy trong cửa sổ 24 h p50 · p90 | ≤ 25 · ≤ 35 | 23 · 32 (29 ngày 25 · 33) |
| 3 | khối hạng 1 / phiên TB · p90 | ≤ 27 · ≤ 35 | 25,1 · 32 |
| 4 | tại 163 signal: khối hạng 1 đang hiệu lực TB · p90 | 2,0–2,5 · ≤ 4 | 2,2 · 4 |
| 5 | tại signal: tổng khối đậm + viền mảnh = khối sống | = số LICH-SU.md tiêu chí 9 (TB 6,7) | — (C#) |
| 6 | % signal có khối hạng 1 cách giá ≤ 5 giá / ≤ 10 giá | ≥ 70% / ≥ 80% | 73,6 / 84,0 |
| 7 | **không nhìn trước**: chạy lõi tới nến i ⇒ `TQ` của mọi khối có `TQ < i` y hệt chạy đủ; khối có `TQ ≥ i` lúc cắt đều `TQ = −1` | 100% | — |
| 8 | lên hạng không hồi tố: `TQTime ≥ StartTime + 60 phút` và `NChamLai ≥ 1 tại nến TQ` với mọi khối hạng 1; `TQ ≤ End` | 100% | — |
| 9 | parity Python ↔ C# từng dòng `_lichsu.csv` kể cả `tq_utc` | 100% (4 107 / 1 445) | — |
| 10 | thời gian `Push` | ≤ +5% so với LICH-SU.md | — |
| 11 | ảnh thật Optimus Flow: 1 ngày đi ngang + 1 ngày xu hướng, đếm khối hạng 1 trong 24 h ≤ 35; rê chuột tới 1 signal thấy ≤ 4 khối đậm + các khối viền mảnh | đạt | chưa (người học) |

Tiêu chí 1–6 là **số đếm mô tả**; không có tiêu chí nào về "đảo chiều nhiều hơn" — vì đã đo là không.

---

## 5. Test (`tests/Program.cs`, thêm mục [16] "Lên hạng khối lịch sử"; giữ [15])
1. Khối tạo nến 0, chạm lại ở nến 10 (NChamLai = 1), 60 phút tại nến 60 ⇒ `TQ = 60` (tuổi quyết định).
2. Khối tạo nến 0, không chạm lại tới nến 90, chạm lại lần đầu nến 100 ⇒ `TQ = 100` (chạm lại quyết định); nến 99 `TQ = −1`.
3. Chạm lại đúng nến 60 (tuổi vừa đủ, `>=`) ⇒ `TQ = 60`.
4. Khối hết hạn ở nến 50 (End = 50) rồi không bao giờ đủ tuổi ⇒ `TQ = −1`.
5. Xuyên phá chốt ở nến 70, `End = 65`; chạm lại lần đầu nến 68 và tuổi ≥ 60 ⇒ `TQ` đặt 68 > End ⇒ reset `TQ = −1`.
6. Lần chạm mở ở nến tạo (giá đang ở vùng) rồi đi, quay lại nến 30 ⇒ `NChamLai = 1` (lần ở nến tạo không tính) — xác nhận `TQ` tính theo lần quay lại.
7. Hết phiên đóng lần chạm đang mở; lần mới ở phiên sau tính là chạm lại ⇒ `TQ` có thể đặt ở phiên sau.
8. Không nhìn trước (`Synthetic(3000)` cắt 2000 — tiêu chí 7).
9. Bất biến tiêu chí 8 trên `Synthetic(3000)`.
10. `Clone()` giữ `TQ/TQTime`; `VclFeeder` reset ⇒ `TQ` dựng lại từ đầu.

Python: `lich_su.py` — thêm `tq` vào `track()`, parity, và in tiêu chí 1–6 (hàm đo lấy từ `loc_vung_bench.screen_metrics`). `test_lich_su` nếu có: thêm ca 1–5.

---

## 6. Việc cho Opus theo thứ tự
1. `VclCore.cs`: hằng `LsRankTouch`, `LsRankAgeMin`; `VLichSu.TQ/TQTime`; đặt trong `Step` (3.1) + reset khi `TQ > End`. **Không** đổi luật khớp/kết thúc.
2. `tests/Program.cs` [16]; `dotnet run --project vung-canh-lenh/tests` xanh.
3. `tools/ReplayCsv`: cột `tq_utc`; chạy 90 ngày + 29 ngày.
4. `research/lich_su.py`: port `tq`, parity từng dòng, in tiêu chí 1–6 ⇒ `report/LOC-VUNG.md` (bảng 4 + ≤ 8 dòng nhận xét, chép câu 3.3). `ve_lich_su.py`: vẽ lại 2 phiên mẫu
   với 2 hạng (hạng 1 tô, hạng 2 chỉ viền tại tiêu điểm) ⇒ `report/img/loc_vung_*.png`.
5. `VungCanhLenh.cs`: `PaintLichSu` theo 3.2. Build `./build.sh`, 0 cảnh báo.
6. `README.md`: mục chế độ lịch sử — thêm đoạn 3.3; sửa câu "~60 khối/24 giờ là bình thường" thành "≈ 23 khối hạng 1/24 giờ; khối khác hiện khi rê chuột".
7. Commit + push từng bước, báo hash. Người học chụp 2 ảnh (tiêu chí 11).

---

## 7. Rủi ro / chỗ dễ sai
1. **Nhìn trước lén qua vẽ**: nếu vẽ đậm từ `StartTime` thay vì `TQTime`, người học sẽ thấy khối "đã mạnh" trước khi nó đủ điều kiện. Đuôi `[Start, TQ)` phải mờ rõ rệt và tiêu điểm phải dùng `TQTime`.
2. **`TQ` đặt rồi khối kết thúc cùng nến với `End < TQ`** (xuyên phá kẹp 5 nến): phải reset −1 (test 5). Python và C# cùng thứ tự: máy → đặt TQ → hết hạn → reset.
3. **Tuổi tính theo thời gian nến, không theo số nến**: qua khoảng nghỉ phiên (gap > 30 phút) tuổi nhảy; chấp nhận (hết hạn 60 phút cũng theo thời gian).
4. **Khối hạng 2 tại tiêu điểm vẽ viền chồng lên khối hạng 1** là chuyện bình thường (hai khối không chồng dải theo thiết kế LICH-SU, nên viền không đè).
5. **Người học kỳ vọng "mạnh"**: chữ UI chỉ nói "đã chạm lại · ≥ 60 phút"; không dùng từ mạnh/yếu/tôn trọng. Nếu người học hỏi "khối hạng 1 có giữ giá tốt hơn không" ⇒ trả lời: không, đã đo (mục 2.3).
6. **Đối chứng gương không khớp "giá từng tới đó chưa"**: gương có thể rơi ngoài dải giá đã giao dịch ⇒ ít lần chạm hơn. Vì thế so sánh **tỉ lệ lên hạng** thật/giả không có nghĩa; chỉ so **kết cục sau lên hạng** (đã làm) — và kể cả vậy khối thật vẫn không hơn. Muốn chặt hơn: thêm Đ2 (đặt trong biên phiên trước, cân lại theo bin khoảng cách) như LAN-CHAM — không đổi kết luận được kỳ vọng.
7. **Số đo 29 ngày hơi khác** (25/24 h, ≤ 5 giá 63%) — engine khởi động lại từ 08-16; ngưỡng chốt theo 90 ngày.
8. **Muốn gọn hơn nữa** ⇒ đổi `LsRankTouch = 2` cho 13 khối/24 h (bảng 2.1), nhưng chỉ 1,1 khối tại signal — nói trước để người học tự chọn; không thêm cài đặt.
9. Ca chưa phủ ⇒ dừng và hỏi; **không** thêm tiêu chí "mạnh" nào khác.

Tái chạy số đo: `cd vung-canh-lenh/research && python3 loc_vung_bench.py --reps 10 > report/LOC-VUNG-BENCH.md` (41 s; `--fast` để thử nhanh).
Bảng khối + lần chạm: `report/loc_vung_zones.csv` (cột `eps` = `bắt đầu:chốt:kết cục:độ sâu` cách nhau `;`).
