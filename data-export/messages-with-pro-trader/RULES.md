# Luật giao dịch chưng cất từ CORVEN → dạng CÓ THỂ CODE

> ⚠️ **ĐỌC KÈM [TRUONG_LINH_3_KICH_BAN.md](TRUONG_LINH_3_KICH_BAN.md)** — CORVEN chạy **3 kịch bản**
> (vùng tuần→hold dài / scalp VWAP-TPO ngày / scalp follow order flow). Bảng dưới là danh sách **phẳng**;
> mỗi luật thực ra chỉ thuộc MỘT kịch bản. Áp luật của kịch bản này sang kịch bản khác là sai
> (vd R7 "SL 2-4 giá" chỉ dành cho nhánh scalp, không dành cho nhánh hold dài theo vùng tuần).
> Ánh xạ luật → kịch bản: xem §3b file đó. ("Trương Linh" trên Messenger = CORVEN, cùng một người.)
>
> Nguồn: [TRANSCRIPT.md](TRANSCRIPT.md). Mỗi luật ghi rõ **nguyên văn** → **cơ chế** → **feature code được**.
> Cột "data" = có backtest offline được không với data hiện có.
> `perlevel_m1_clean.pkl` + `sample.csv` (2026-06-01 → 07-27) CÓ bid/ask từng mức giá + `max_one_trade` → test được lớp footprint.

| # | Luật (nguyên văn) | Cơ chế | Feature code | Data? |
|---|---|---|---|---|
| R1 | "một nhịp tang chú phải phân tích xem nó tang nhờ lệnh gì"; "đẩy nhờ **limit buy** kê cao dần → **không bền**"; "khác với **buy market** chủ động bơm vào" | BID = sell-market đập buy-limit; ASK = buy-market nhấc sell-limit. Giá lên mà BID áp đảo = limit-driven = giả | **`leg_aggression`** = Σdelta của leg / Σvolume leg. LONG cần `ddom_leg ≥ +τ`; SHORT cần `≤ −τ` | ✅ có delta thật |
| R2 | "buy limit ở **chân** con song tang (sau một nhịp giảm) thì **ngon**; ở **đỉnh** là **lỏ**" | Hấp thụ thụ động chỉ có giá trị ở cực trị, không phải giữa/đỉnh xu hướng | **`absorb_at_extreme`**: chỉ tính điểm hấp thụ khi mức giá đó nằm trong 25% dưới (LONG) / trên (SHORT) của range gần | ✅ per-level |
| R3 | "di chuyển nhờ **quét stoploss** … **chạy mạnh nhưng k đi được xa** — hành vi khác chủ đích buy" | Stop-run = thanh khoản một lần, hết là hết → **giết runner** (nhưng scalp vẫn ăn) | **`stoprun_leg`**: leg khởi phát bằng cây phá **swing extreme ≤N nến trước** + VSA spike + đóng ngược ≥50% → **loại khỏi nhánh RUNNER** | ✅ OHLCV |
| R4 | "đỉnh thấp hơn phải **nhìn sang cả delta** nữa" | Cấu trúc giá không đủ, phải có xác nhận delta | **`structure_delta_agree`**: LH/LL phải kèm CVD cùng hướng | ✅ |
| R5 | "**mỗi phiên sẽ có một bias** … xem bên nào đang kiểm soát thì theo bên đó … **bias tang thì chỉ canh mua** … xong **vào low tìm entry**" | Bias khoá theo PHIÊN (không đảo giữa phiên), entry là hồi về đáy phiên | **`session_bias`** tính 1 lần đầu phiên (Á/Âu/Mỹ) rồi KHOÁ; thay filter rolling-480 hiện tại | ✅ |
| R6 | "**sáng entry time là 8h**"; "sáng tầm 7h chạy mạnh"; "chiều sideway nhiều"; "t chơi **RR theo entrytime**" | Giờ quyết định biên độ → quyết định RR khả thi | **`rr_by_hour`**: RR mục tiêu thay đổi theo giờ (giờ động → 5–6R; giờ chết → bỏ lệnh) | ✅ |
| R7 | "**bóp sl thì mới có cơ sở gồng dài**"; "**Sl càng ngắn thì tỉ lệ lệnh tp 5-6R càng nhiều**"; "**từ 2–4 giá**"; "**khoảng dưới cây m1 thôi**"; "đừng ngắn quá vì lỗ phí" | Tight SL là ĐIỀU KIỆN của RR cao, không phải hệ quả | **SL floor 2.0 / cap 4.0 giá** (hiện 3.0/7.0), neo **dưới cây M1 vào lệnh** thay vì cực trị nhịp hồi; **RR 5.0** | ✅ |
| R8 | "**t check data xác nhận t mới vào**"; "mọi thứ đề chuẩn chỉ rồi, **thiếu mỗi xác nhận trong m5, m1**" | Không có nến xác nhận = không vào, dù bias/vùng đẹp | **`m5_confirm`**: nến M5 đang hình thành phải cùng phía (close>open cho LONG) | ✅ |
| R9 | "**Chú xem cây giảm vol có ngon k / Đóng có đẹp k / Mấy cây giảm đóng râu dưới vẫn rút kìa**" | Muốn SHORT thì chính cây GIẢM phải chất lượng: vol tốt, đóng sát đáy, không râu dưới | **`leg_bar_quality`** = tỉ lệ nến thuận hướng trong leg có `cpos` đúng phía + râu ngược `< 35%` range | ✅ |
| R10 | "Đi lên **k có ai bán** thì nó vẫn lên mà chú" | Volume thấp KHÔNG phải tín hiệu đảo. Cạn cung ≠ có cầu | **BỎ** mọi logic "volume thấp → fade". Chỉ fade khi có **cây từ chối có volume** | ✅ |
| W1 | "**Tìm biên m1 xong et m1 luôn cũng đc**" | Range xác định trên chính M1, không cần lên M5 | Range builder trên M1 (đã có) — giữ | ✅ |
| W2 | "Biên của chú **to thế** =))" (TR 15 giá) | TR chuẩn của CORVEN nhỏ hơn nhiều | Giữ `RangeMaxPts` hẹp (hiện 7.5) — **xác nhận đúng hướng** | ✅ |
| W3 | "**đừng đánh UT sớm**"; "**Sang D chú mới đánh thì đc**" | Không đánh cú phá đầu tiên (UT/spring = Phase C = bẫy). Chỉ đánh khi đã sang Phase D (LPS/LPSY) | **`phase_c_then_d`**: bắt buộc có **1 lần phá HỤT** cạnh đối diện *trong range* trước, rồi mới nhận break + retest | ✅ |
| W4 | "**k cần nhãn nhiếc đâu. Xác định range thôi là đc. Rồi nhìn phân tích vol trong range**" | Bỏ gán nhãn Wyckoff; chỉ cần range + phân tích volume trong range | **`range_vol_profile`**: so Σvolume nửa trên vs nửa dưới range + delta tại 2 cạnh → bias tích luỹ/phân phối | ✅ per-level |
| W5 | "**Đánh break thôi chú**"; "SL 5 giá ổn" | Chỉ giao dịch breakout của range (không mean-revert trong range) | Nhánh CBR = đúng hướng. ⚠️ **SỬA 2026-07-31:** trước đây ghi "nhánh QUAY_DAU (fade tại VWAP) đi ngược lời khuyên này" — **đọc quá rộng**. W5 nói về *range M1 của kịch bản scalp follow order flow*, cấm fade **biên range M1**; nó KHÔNG cấm fade tại **VWAP/TPO khung ngày** — đó là kịch bản khác trong cùng hệ CORVEN. Xem [TRUONG_LINH_3_KICH_BAN.md](TRUONG_LINH_3_KICH_BAN.md) §3b | ✅ |
| C1 | "**pass tầm 70% checklist thì vào**" (Benzo) — "**Hợp lý đấy chú**" (CORVEN) | Không phải AND-gate cứng; là **điểm số** | Đổi kiến trúc: **score có trọng số, ngưỡng ~70%** thay cho chuỗi AND | ✅ |
| C2 | "WR **65–70%**", "RR theo entrytime, có khi **1:5, 1:6**", "SL dài thì **ít lệnh RR cao**" | Mục tiêu hệ: WR trung bình + đuôi phải dài | Không tối ưu WR đơn lẻ; tối ưu **tổng R** với SL chặt + RR cao | ✅ |
| C3 | "**nhồi hay quét vl** / vào một phát to mẹ luôn" | Bỏ nhồi lệnh (pyramiding) | Không thêm nhồi lệnh vào v6 | — |

## Ba đòn bẩy lớn nhất (Claude xếp hạng)

1. **W3 — Phase C rồi mới Phase D.** Đây là thay đổi cấu trúc mạnh nhất và cũng là điều Runner v5 hoàn toàn thiếu: hiện chỉ cần "phá → hồi → tiếp diễn", không đòi hỏi range trước đó đã **quét hụt cạnh đối diện**. Cú break đầu tiên chính là cú CORVEN bảo "đừng đánh".
2. **R7 — bóp SL 2–4 giá + RR cao.** Đổi hai hằng số, đổi hẳn phân phối lợi nhuận. Rẻ để test, tác động lớn.
3. **R1 — leg phải do lệnh CHỦ ĐỘNG đẩy (delta-dominant), không phải limit kê.** Có data per-level để test thật, không phải suy đoán.
