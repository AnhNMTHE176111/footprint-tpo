# Luật giao dịch chưng cất từ CORVEN → dạng CÓ THỂ CODE

> 📘 **Muốn HỌC (không phải code) thì đọc [BAI_GIANG_CORVEN.md](BAI_GIANG_CORVEN.md)** — xâu chuỗi toàn
> bộ hệ thành 7 tầng nhân–quả, có câu hỏi kiểm tra.

> 🔴 **BẢN CHỐT ĐỂ CODE LÀ [CORVEN_SPEC_V1.md](CORVEN_SPEC_V1.md)** (2026-07-31), không phải file này.
> File này là luật vi mô thô; SPEC đã sửa mấy chỗ diễn giải sai và bổ khung 3 kịch bản + RR/WR chốt.
>
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
| R1 | "một nhịp tang chú phải phân tích xem nó tang nhờ lệnh gì"; "đẩy nhờ **limit buy** kê cao dần → **không bền**"; "khác với **buy market** chủ động bơm vào" | BID = sell-market đập buy-limit; ASK = buy-market nhấc sell-limit. Giá lên mà BID áp đảo = limit-driven | **`leg_aggression`** = Σdelta của leg / Σvolume leg. LONG cần `ddom_leg ≥ +τ`; SHORT cần `≤ −τ` | ✅ có delta thật |
| | ⚠️ **R1 KHÔNG VÔ ĐIỀU KIỆN — sửa 2026-08-10 theo §13.5:** "tăng mà delta âm" chỉ là **suy yếu** khi ở **cuối sóng / nhịp hồi**. Ở **đầu sóng ngay sau một balance** thì nó **báo nhịp squeeze sắp tới** (đảo dấu delta), tức là tín hiệu THUẬN. Luật `ddom_leg ≥ +τ` hiện tại đang chặn cả hai ca ⇒ đó chính là lý do "delta-gate làm tệ nhánh reversal". | | | |
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
| W5 | "**Đánh break thôi chú**"; "SL 5 giá ổn" | ⚠️ **SỬA LẠI 2026-07-31 (người học chốt):** "break" = **giá phá ra khỏi VÙNG (HVN), chờ HỒI về + có tín hiệu rồi đánh** — tức **break-retest**, KHÔNG phải "chỉ đánh breakout của range" | Đây là **một trong HAI play tại cùng một vùng HVN**; play kia là **chạm → đảo chiều tại HVN**. CORVEN dùng **cả hai** → **không có luật nào cấm fade**. Hai lần diễn giải trước của tôi (①"cấm mean-revert trong range" ②"cấm fade tại VWAP") **đều sai**. Xem [CORVEN_SPEC_V1.md](CORVEN_SPEC_V1.md) §3 | ✅ |
| C1 | "**pass tầm 70% checklist thì vào**" (Benzo) — "**Hợp lý đấy chú**" (CORVEN) | Không phải AND-gate cứng; là **điểm số** | Đổi kiến trúc: **score có trọng số, ngưỡng ~70%** thay cho chuỗi AND | ✅ |
| C2 | "WR **65–70%**", "RR theo entrytime, có khi **1:5, 1:6**", "SL dài thì **ít lệnh RR cao**" | Mục tiêu hệ: WR trung bình + đuôi phải dài | Không tối ưu WR đơn lẻ; tối ưu **tổng R** với SL chặt + RR cao | ✅ |
| C3 | "**nhồi hay quét vl** / vào một phát to mẹ luôn" | Bỏ nhồi lệnh (pyramiding) | Không thêm nhồi lệnh vào v6 | — |
| **R11** | "**limit order là chặn đc sóng**"; "**Move là nhờ market order**"; "**Market buy > sell thì move tăng lên**"; "limit vẫn làm giá tăng đc nhưng **dí limit sát theo giá**" (§13.3–13.4) | Hai cơ chế đẩy giá khác nhau hẳn: (a) market buy áp đảo → delta dương, ASK trội; (b) nâng dần buy-limit sát giá → giá vẫn lên nhưng **khớp vào BID** → **delta âm trong khi giá tăng**. Đây là lời giải cho hiện tượng người học quan sát cả tuần | **`limit_driven_leg`** = leg có `price_change > 0` **và** `Σdelta < 0` (hoặc ngược lại cho giảm). Là một **cờ ngữ cảnh**, KHÔNG phải cờ loại-bỏ — ý nghĩa do R12 quyết định | ✅ per-level |
| **R12** ⭐ | "**Đầu sóng là dự kiến cho move mới** / **Cuối sóng là suy yếu** / **Nhịp hồi là suy yếu**"; "chưa phải squeeze vì tăng delta vẫn âm… **nó ở đầu sóng** thì dự sau đó có một nhịp mạnh… squeeze delta dương" (§13.5) | **Cùng một phân kỳ delta mang 3 ý nghĩa trái ngược tuỳ vị trí trong sóng.** Đầu sóng: limit kê giữ giá + short chưa thoát ⇒ nhiên liệu cho squeeze. Cuối sóng / nhịp hồi: không còn lực chủ động ⇒ hết đà | **`wave_pos` ∈ {DAU_SONG, GIUA, CUOI_SONG, NHIP_HOI}** — thêm feature này rồi **nhân** với `limit_driven_leg`: `DAU_SONG × limit_driven` → tín hiệu THUẬN (chờ squeeze); `CUOI_SONG/NHIP_HOI × limit_driven` → tín hiệu NGƯỢC (yếu) | ✅ suy được từ OHLCV + range |
| **R13** | "điều kiện là move đấy phải nằm ngay sau đấu giá xong à — **Uh, sau một balance**"; "**Trong balance thì chop** / xác định range rồi **2 cạnh mà vả** thôi / thì cứ tăng mà delta âm **là yếu**" (§13.6) | "Đầu sóng" có **định nghĩa vận hành**: leg đầu tiên **ngay sau một BALANCE (range đấu giá xong)**. Còn **đang trong** balance thì mọi phân kỳ delta chỉ là yếu, không dự báo gì | **`post_balance_leg`**: phải phát hiện balance (range co, TPO cân) rồi mới cho `wave_pos = DAU_SONG`. Trong balance ⇒ chỉ bật engine "vả 2 cạnh", tắt engine follow-đà | ✅ đã có range builder |
| **R14** | "**Day scap nhìn tpo daily**"; "**Gộp 3 week / 1 preiod vẫn là 30p**"; "**Giờ break ra là follow theo**"; "**Check tail các thứ xem ổn hết chưa**" (§13.7–13.8) | Hai tầng profile: **TPO daily** cho scalp ngày, **TPO gộp 3 TUẦN (period 30 phút)** cho vùng lớn/bao quát. Chất lượng đấu giá kiểm bằng **tail** (đuôi profile) | M30SessionZones: đổi cửa sổ profile lớn thành **rolling 3 tuần, bucket 30 phút**; thêm phát hiện **tail / single print**. ⚠️ Đây là **cấu hình mới, chưa đo** | ✅ có M30 data |

## Ba đòn bẩy lớn nhất (Claude xếp hạng)

> 🆕 **Cập nhật 2026-08-10:** đòn bẩy số 1 bây giờ là **R12 (vị trí trong sóng × phân kỳ delta)**, vì nó
> giải thích tại sao delta-gate hiện tại vừa cứu nhánh follow-đà lại vừa giết nhánh quay đầu: hai nhánh
> đó nằm ở **hai vị trí sóng khác nhau**, mà code đang dùng **một** ngưỡng delta cho cả hai. Ba mục dưới
> giữ nguyên thứ tự cũ.

1. **W3 — Phase C rồi mới Phase D.** Đây là thay đổi cấu trúc mạnh nhất và cũng là điều Runner v5 hoàn toàn thiếu: hiện chỉ cần "phá → hồi → tiếp diễn", không đòi hỏi range trước đó đã **quét hụt cạnh đối diện**. Cú break đầu tiên chính là cú CORVEN bảo "đừng đánh".
2. **R7 — bóp SL 2–4 giá + RR cao.** Đổi hai hằng số, đổi hẳn phân phối lợi nhuận. Rẻ để test, tác động lớn.
3. **R1 — leg phải do lệnh CHỦ ĐỘNG đẩy (delta-dominant), không phải limit kê.** Có data per-level để test thật, không phải suy đoán.
