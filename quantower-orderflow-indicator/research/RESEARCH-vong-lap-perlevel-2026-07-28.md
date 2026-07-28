# Vòng lặp cải tiến trên footprint PER-LEVEL thật — nhật ký và kết quả

Dữ liệu: `data-export/27-7/sample.csv` (761.199 ô, 77.672 nến M1, 01→07/2026) + OHLC ghép từ file
dxFeed 1m (98,6% khớp). Cache: `perlevel_m1.pkl` (từ 05/2026) và **`perlevel_m1_clean.pkl`
(từ 06/2026 — bản dùng để kết luận)**.

> **Kết luận trước, chi tiết sau:** sau khi sửa hai lỗi phương pháp của chính mình (target không
> chuẩn hoá theo biến động; giữ dữ liệu rác tháng 5), **không còn đặc trưng footprint per-level nào
> cho edge dự báo đảo chiều trên vàng M1**. Base rate tụt về ~50,6% ≈ ngẫu nhiên. Bộ điểm
> Absorption v3 mà tôi vừa cài phải tháo phần lớn: 4/7 thành phần vô giá trị hoặc gây hại.

---

## Vòng 1 — chạy calibrate lần đầu (`calibrate_perlevel.py`)

`max_one_trade > 0` ở **0,00%** trong 761.199 ô → xác nhận lần thứ hai, trên per-level thật, rằng
feed không cấp lệnh đơn. Kết luận "Big Trade thực chất là HVN cell" là đúng.

Bộ điểm v3 (baseline top-3 ô, EFFORT z 2,5), target 1 USD, horizon 20:

| mức điểm | n | hit | base 55,8% |
|---|---|---|---|
| ≥6 | 1.997 | 52,9% | −2,9pp |
| ≥8 | 773 | 53,3% | −2,5pp |
| ≥10 | 115 | 46,1% | −9,7pp |
| ≥11 | 14 | 35,7% | — |

**Điểm càng cao càng tệ.** Thành phần: `swing` +4,6pp là duy nhất có ích; `prominent` −5,2pp,
`noResult` −3,4pp, `multi` −2,0pp, `twoSided` −1,9pp, `divergence` +0,7pp.

## Vòng 2 — ablation (`ablation_m1.py`) → tưởng tìm ra vàng

Bỏ `prominent` + `noResult` cho **65,2%** (n=316) so base 55,8%; "POC không ở cực trị" 65,0%
(n=237). Cơ chế nghe rất hợp lý: giá chạm mức, bị chặn, nhưng khối lượng chính của nến ở XA mức đó
→ cực trị bị *từ chối*; nếu POC nằm ngay cực trị thì thị trường đang *chấp nhận* giá đó.
Kiểm OOS (`refine_pocfar.py`, IS = T5-6, OOS = T7): IS +6,4pp (1,2σ), OOS +10,2pp (2,5σ).

## Vòng 3 — đo lại bằng bin liên tục (`pocpos_monotonic.py`) → sụp

Thay ngưỡng rời rạc bằng đặc trưng liên tục `pocRel` trên **toàn bộ 16.877 mẫu**:

| pocRel (0 = POC xa cực trị, 1 = POC ngay cực trị) | n | hit | T5 | T6 | T7 |
|---|---|---|---|---|---|
| [0; 0,2) | 2.879 | 54,5% | 54,5 | 53,0 | 54,9 |
| [0,4; 0,6) | 3.127 | 57,4% | 58,2 | 58,0 | 56,9 |
| [0,8; 1) | 4.687 | 55,8% | 55,1 | 56,3 | 56,4 |

Không đơn điệu, dao động ±1,5pp quanh base 56,1%, không nhất quán theo tháng.
**Hiệu ứng 65% ở vòng 2 là nhiễu do lọc nhiều tầng trên n nhỏ.**

Nhưng bảng phụ lộ ra thứ khác: nến cực trị **range ≥20 tick** hit ~59,4% (n=8.072) còn range
5–10 tick ~50,5% — chênh 9pp thuần theo biến động. Đó là lỗi phương pháp: **target cố định 1 USD**
trong khi biến động tháng 5 và tháng 7 chênh 3–4×.

## Vòng 4 — chuẩn hoá target theo biến động (`volnorm_test.py`)

`TARGET_i = 2,0 × median(range 100 nến trước i)`, mọi bảng chia theo quartile biến động.
Base tụt **55,8% → 51,2%**. Kết quả (dữ liệu đã bỏ tháng 5, n=10.289, base 50,6%):

| đặc trưng | n | hit | σ so base |
|---|---|---|---|
| volume nến ≥3× median | 2.313 | 50,7% | +0,1 |
| range nến ≥2× median | 2.164 | 51,4% | +0,7 |
| có ô z≥2,5 tại cực trị | 558 | 53,6% | +1,4 |
| ô z≥2,5 + delta divergence | 489* | 51,1% | −0,0 |
| ô z≥2,5 + twoSided | 102* | 45,1% | −1,2 |
| price impact thấp (Kyle λ, z≤−1) | 712* | 48,7% | −1,3 |
| swing 9 nến | 15.986* | 51,2% | +0,0 |
| swing 20 nến | 10.871* | 52,2% | +2,1 |

(*) đo trên cache có tháng 5. Sau khi bỏ tháng 5, mọi con số trong bảng A/B đều tụt về ≤+1,4σ.

**Cái chết đáng chú ý nhất:** "volume nến ≥3× median" từng cho 58,6% (+3,5σ) ở đo bar-level lượt
trước — sau chuẩn hoá còn **+0,1σ**. Nó chỉ là proxy của biến động.

## Vòng 4b — chất lượng dữ liệu

| tháng | nến | volume median/nến | ô/nến | % nến vol<10 |
|---|---|---|---|---|
| 2026-05 | 19.944 | **5** | **3** | **63,3%** |
| 2026-06 | 7.671 | 48 | 15 | 5,5% |
| 2026-07 | 25.016 | 44 | 13 | 7,2% |

Tháng 5 là **dữ liệu rác** (GCQ26 chưa là hợp đồng chính) nhưng chiếm 38% mẫu, và nó chính là
quartile biến động thấp nơi mọi "edge" tụ lại. → tạo `perlevel_m1_clean.pkl` (từ 06/2026).

## Kiểm chứng độc lập (nhánh song song)

Đo bằng **LEVEL HOLD** (mức có bị xuyên bằng close trong N nến, buffer chuẩn hoá) và **E[R] thật**
(SL = mức ±2 tick), so với đối chứng ghép cặp:

| nhóm | hold N=20 | E[R] (TP 2R) |
|---|---|---|
| absorption mọi tín hiệu (n=2.769) | **24,7%** ±1,0 | +0,041 |
| đối chứng cực trị cục bộ (n=16.041) | **27,5%** ±0,4 | +0,041 |
| absorption điểm ≥8 (n=771) | 20,9% (−6,6pp, **3,7σ**) | −0,024 |

Absorption **giữ mức kém hơn** đối chứng, và **điểm càng cao mức càng dễ vỡ** — đơn điệu, nhất quán
cả 3 tháng. E[R] bằng đối chứng đúng đến 3 chữ số; MFE/R của absorption chỉ "đẹp" vì SL hẹp hơn
(0,60 vs 0,80). Ma trận target chuẩn hoá × horizon: không ô nào vượt 1σ.

## Hàm ý cho indicator

1. **Tháo bộ điểm.** `noResult`, `prominent`, `twoSided` phải về trọng số **0** (đo được là gây
   hại: −7,2pp, −5,8pp, −1,2σ). `divergence` về 0–1 (−0,0σ). `swing` giữ nhưng đổi period 9 → **20**.
2. **Đổi vai trò.** Bubble không phải tín hiệu vào lệnh — dữ liệu không cho nó quyền đó. Nó là
   công cụ ĐÁNH DẤU để đọc bằng mắt. Điểm phải được hiểu là "độ đậm hiển thị", không phải xác suất.
3. **Hiệu ứng duy nhất vững lại là NGƯỢC DẤU:** tổ hợp "ô đậm tại cực trị + range hẹp + POC nổi bật
   ngay đó" báo mức **sắp bị xuyên**, không phải hấp thụ. Đây có lẽ chính là lý do người dùng thấy
   bubble mọc đầy ở "vùng quan trọng" — chúng đánh dấu vùng bị xuyên qua. Chiều tiếp diễn chưa đủ
   mẫu (n<500) để giao dịch, nhưng đủ để **đổi nhãn cảnh báo**.
4. **Chuẩn đo cho mọi thí nghiệm sau:** LEVEL HOLD (close, N=20, buffer = max(2 tick,
   0,2×medRange100), so đối chứng ghép cặp) + E[R] với SL thật. **Bỏ hẳn target USD cố định.**
5. **Muốn tiến xa hơn thì cần dữ liệu khác, không phải thuật toán khéo hơn**: front-month liên tục
   (CCPA) để tăng n, và tick-level (absorption run, gộp lệnh) — tầng thông tin mà bar/level không có.
