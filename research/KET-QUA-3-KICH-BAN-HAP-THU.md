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
