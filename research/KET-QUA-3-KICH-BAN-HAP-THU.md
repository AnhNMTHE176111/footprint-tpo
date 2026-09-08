# Đo tần số 3 kịch bản sau cụm bán tháo (delta cực đoan + khối lượng cực lớn ở đáy mới)

**Dữ liệu:** `data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv`
— 724.279 nến M1, 2024-08-01 → 2026-08-19 (nguồn chuẩn, 101k HĐ/phiên).
**Script:** `research/kich-ban-hap-thu.py` (bản 1), `research/kich-ban-hap-thu2.py` (bản 2, có xác nhận).

## Định nghĩa ca (bằng số)
- Nến sự kiện: **đáy thấp nhất 20 nến** + `volume ≥ 3× trung vị 50 nến` + `delta ≤ −4× trung vị |delta| 50 nến`.
- Loại bỏ mọi cửa sổ vắt qua nghỉ phiên / chỗ nối hợp đồng (yêu cầu 81 nến liên tục từng phút).
- Không đếm trùng: sau 1 ca nhảy 30 nến.
- Phân loại trong **30 nến kế tiếp**, với `R = biên độ nến sự kiện`, `L = đáy nến sự kiện`:
  - **K3** = giá xuyên xuống dưới `L − ngưỡng` trước khi lên tới đích ⇒ hấp thụ thất bại.
  - **K1** = lên tới `L + 2R` mà **chưa** quay về sát L (trong 0,5 giá) ⇒ đảo chiều thẳng.
  - **K2** = quay về sát L (không xuyên) rồi mới lên tới `L + 2R` ⇒ thử lại rồi lên.
  - **K0** = không lên đích, cũng không xuyên ⇒ đi ngang.

## Kết quả — KHÔNG lọc xác nhận (n = 4.458)
| Ngưỡng xuyên đáy | K1 | K2 | K3 | K0 | K1:K2 |
|---|---|---|---|---|---|
| 3 tick (0,3 giá) | 8,0% | 10,8% | **75,9%** | 5,2% | 43:57 |
| 1,0 giá | 8,1% | 17,0% | **65,7%** | 9,3% | 32:68 |
| 0,5× biên nến | 8,1% | 17,9% | **61,7%** | 12,4% | 31:69 |
| 1,0× biên nến | 8,1% | 23,2% | **45,5%** | 23,2% | 26:74 |

⇒ **K3 áp đảo.** Cụm bán tháo trơ trọi (chưa có nến xác nhận) phần lớn bị xuyên tiếp.
⇒ Trong hai kịch bản thắng thì **K2 phổ biến hơn K1** (57–74% số ca thắng).

## Kết quả — CÓ lọc xác nhận: nến kế tiếp delta đảo dấu, độ lớn ≥ 50% delta nến bán tháo (n = 534)
| Ngưỡng xuyên đáy | K1 | K2 | K3 | K0 | K1:K2 |
|---|---|---|---|---|---|
| 3 tick | **25,3%** | 8,2% | 59,0% | 7,5% | 75:25 |
| 0,5× biên nến | **25,3%** | 14,8% | 44,9% | 15,0% | 63:37 |
| 1,0× biên nến | **25,3%** | 19,5% | 31,1% | 24,2% | 56:44 |

Lọc nhẹ (nến kế tiếp chỉ cần delta > 0, n = 2.382): K1 18,8% · K2 17,4% · K3 37,4% · K0 26,4%.

⇒ Nến xác nhận đổi cục diện thật: K1 từ 8,0% lên **25,3%** (×3,2), K3 từ 61,7% xuống 44,9%.
⇒ **Có xác nhận thì K1 phổ biến hơn K2** (đảo ngược so với khi không có xác nhận).

## Mức bằng chứng — CHƯA đủ để code thành signal
Vào lệnh theo ca có xác nhận, dừng lỗ dưới `L − 0,5R` (tức 1,5R), đích 2R (tỷ lệ 1,33):
thắng 40,1% · thua 44,9% · 15,0% treo ⇒ kỳ vọng ≈ **+0,08 đơn vị rủi ro/ca**, chưa trừ phí và
trượt giá. Gần như hòa ⇒ **chỉ dùng đọc chart, không code thành signal** (theo quy tắc trong
`tpo/EVIDENCE-DRILLS.md`). Cần thêm điều kiện lọc bối cảnh (VWAP, vùng giá trị, khung lớn) rồi đo lại.

## Lưu ý cách đọc con số
"K3" nghĩa là **đáy bị xuyên**, KHÔNG đồng nghĩa "phóng mạnh xuống" — nhiều ca chỉ xuyên vài tick rồi
lình xình (thấy rõ ở chỗ nới ngưỡng xuyên: K3 tụt từ 75,9% xuống 45,5%, phần lớn chuyển sang K0/K2).

---

# Bổ sung (cùng ngày): CHIA THEO VÙNG + đo kỳ vọng từng kiểu vào lệnh

Script: `research/kich-ban-hap-thu3.py`, `research/kich-ban-hap-thu4.py`. Vùng tính từ chính file bars
(UTC, phiên CME mốc 22:00 UTC).

## Vùng KHÔNG đổi được kết quả
| Điều kiện vùng | K1 | K2 | K3 | n |
|---|---|---|---|---|
| tất cả (không xác nhận) | 8,1% | 17,9% | 61,9% | 4.368 |
| dưới VWAP ngày | 8,2% | 17,7% | 62,3% | 2.934 |
| trên VWAP ngày | 7,9% | 18,5% | 61,0% | 1.434 |
| là đáy PHIÊN mới | 9,6% | 16,9% | 58,8% | 1.031 |
| chỉ là đáy 20 nến | 7,6% | 18,2% | 62,8% | 3.337 |
| trùng đáy phiên trước ±5 | 6,6% | 18,3% | 63,8% | 257 |
| trùng đáy phiên trước ±10 | 7,5% | 18,9% | 62,8% | 545 |
| trong giờ pit COMEX | 8,2% | 16,5% | 60,4% | 886 |

Có xác nhận (n=526): dưới VWAP K1 26,3% vs trên VWAP 22,1%; đáy phiên mới 28,0% vs 24,3%.
⇒ **Chênh lệch nhỏ, không đủ tách khỏi nhiễu.** Trùng đáy phiên trước còn **hơi kém hơn** nền.

## Kỳ vọng từng kiểu vào lệnh (đích 2R, tối đa 60 nến)
| Kiểu vào | n | thắng | thua | kỳ vọng |
|---|---|---|---|---|
| V0 vào ngay nến xác nhận, lỗ dưới đáy bán tháo | 494 | 24,9% | 59,3% | −0,008R |
| V0t vào ngay, lỗ sát dưới đáy nến xác nhận | 498 | 26,1% | 68,1% | −0,119R |
| V2 chờ 2 nến đi ngang rồi vào nến tăng, lỗ dưới đáy bán tháo | 1.127 | 14,5% | 51,2% | −0,060R |
| **V2t chờ 2 nến đi ngang, lỗ SÁT dưới cụm đi ngang** | 1.127 | 27,7% | 60,9% | **+0,007R** |
| V3t chờ 3 nến đi ngang, lỗ sát cụm đi ngang | 1.046 | 26,0% | 59,8% | −0,009R |
| V3 đi ngang rồi xuyên đáy → BÁN | 384 | 25,3% | 54,7% | +0,023R |

⇒ **Tất cả nằm trong khoảng −0,12R đến +0,02R = KHÔNG có lợi thế**, chưa trừ phí.
⇒ Chờ đi ngang **không** cải thiện gì nếu vẫn để dừng lỗ dưới đáy nến bán tháo (−0,060R):
tỷ lệ thắng tụt từ 24,9% xuống 14,5% vì vào cao hơn ⇒ đích 2R xa hơn theo giá.
Chờ đi ngang **chỉ có ích khi kéo dừng lỗ lên sát cụm đi ngang** (−0,060R → +0,007R).

## Giới hạn của phép đo
"Khối lượng cực lớn" ở đây là `≥ 3× trung vị 50 nến`, **không phải công thức cột tím của
VSA Volume** — nếu chỉ báo đó dùng ngưỡng khác thì tập ca sẽ khác. Đo trên M1, đích 2R, chân
trời 60 nến; chưa thử khung lớn hơn.
