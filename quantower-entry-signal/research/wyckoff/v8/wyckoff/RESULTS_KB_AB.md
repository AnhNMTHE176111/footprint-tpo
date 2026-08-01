# RESULTS — KB-A / KB-B trên vùng CORVEN (HVN tuần/ngày) — Session 3, 2026-08-01

> Kết luận cuối: **KB-A KILL ở P4 (đối chứng ngẫu nhiên)** → theo đúng luật đã chốt trước
> (`PLAN_KB_ABC.md` §5 P4), toàn bộ nhánh cấp vốn dừng ở đây. P5/P6 vẫn được chạy đủ (đã có sẵn
> hạ tầng, chi phí thấp) để có bức tranh đầy đủ, nhưng **không có cấu hình nào được port sang
> C#** — P7 bị bỏ qua đúng theo cổng của plan ("chỉ port nếu P4/P5/P6 qua").
>
> Đây là **kết quả hợp lệ**, không phải thất bại của quá trình đo — xem `PLAN_KB_ABC.md` §6.4 và
> bài học `BACKTEST-ZONES-V2.md` (bộ vùng "nghe rất hợp lý" theo lời pro trader vẫn có thể không
> hơn ngẫu nhiên).

---

## 0. Tái lập

```bash
cd quantower-entry-signal/research/wyckoff/v8/wyckoff
python3 check_p1_zones.py     # P1 — kiem zone provider (13 moc tuan, causal, sweep min_ratio)
python3 probe_p2_mfe.py       # P2 — probe MFE PLAY1, chot RR
python3 run_ab.py             # P3-P6 — KB-A, KB-B, doi chung ngau nhien, quet chi phi
python3 portfolio_calc.py     # so portfolio KB-A+KB-B gop (dung cho bang cuoi)
```
Nguồn dữ liệu: dxFeed GCQ26 9 tháng (`entry_dxfeed.load_m1()`), lọc in-sample 5-7/2026 (13 tuần,
~52k nến qua gate) — **cùng nguồn/cửa sổ với `BASELINE.md`**, không dùng `fp-m1-6-month.csv` (cột
Volume hỏng 04/06→26/06). `VOLFLOOR_FROZEN=20.0` (không look-ahead).

---

## 1. Bốn bảng chính

### KB-A / PLAY1 (chạm → đảo chiều, vùng TUẦN, HVN W_CLOSED)

| Thông số | TRƯỚC (v7, KB2/QUAY_DAU — play tương ứng) | SAU (PLAY1 @ HVN tuần) | Δ |
|---|---:|---:|---:|
| Nguồn dữ liệu + cửa sổ | dxFeed 5-7/2026 | dxFeed 5-7/2026 | giống nhau |
| Neo vùng | VWAP phiên | HVN tuần (W_CLOSED) | đổi tầng |
| Chế độ nhân quả | — | W_CLOSED | — |
| n (số lệnh) | 27 | 71 | +44 |
| n / tuần | ~2.1 | ~5.5 | — |
| WR % | 55.6% | 18.3% | **−37.3 điểm ↓** |
| Tổng R | +10.5R | −19.0R | **−29.5R ↓** |
| EV / lệnh (R) | +0.389 | −0.268 | **−0.657 ↓** |
| MDD (R) | 5.0R | 21.0R | **+16.0R ↑ (xấu)** |
| Tháng 5 (R) | +2.0 | −6.0 | ↓ |
| Tháng 6 (R) | +2.5 | −4.0 | ↓ |
| Tháng 7 (R) | +6.0 | −9.0 | ↓ |
| Nửa kỳ 1 (R,n) | +4.5R(n13) | −11.0R(n35) | ↓ |
| Nửa kỳ 2 (R,n) | +6.0R(n14) | −8.0R(n36) | ↓ |
| LONG: n/WR/EV | n13 46% +0.154 | n30 23.3% −0.067 | ↓ |
| SHORT: n/WR/EV | n14 64% +0.607 | n41 14.6% −0.415 | ↓ |
| RR đang dùng | 1.5 | 3.0 (chốt theo Q9 + probe P2) | đổi |
| KẾT LUẬN | PASS có điều kiện (v7) | **KILL** (âm mọi mặt) | |

### KB-A / PLAY2 (phá → hồi → tiếp, vùng TUẦN, HVN W_CLOSED)

| Thông số | TRƯỚC (v7, KB1/CBR — play tương ứng) | SAU (PLAY2 @ HVN tuần) | Δ |
|---|---:|---:|---:|
| Neo vùng | range co hẹp 8 nến nội bộ | mép HVN tuần (W_CLOSED) | đổi tầng |
| n | 33 | 57 | +24 |
| WR % | 48.5% | 28.1% | **−20.4 điểm ↓** |
| Tổng R | +47.0R | +4.6R | ↓ mạnh |
| EV / lệnh (R) | +1.424 | +0.081 | **−1.343 ↓** |
| MDD (R) | 3.0R | 11.0R | +8.0R ↑ (xấu) |
| Tháng 5/6/7 (R) | +5.0/+22.0/+20.0 ✓ | −9.0/+5.6/+8.0 ✗ | đảo dấu tháng 5 |
| Nửa kỳ 1/2 | +14.0R(n16)/+33.0R(n17) | +1.6R(n28)/+3.0R(n29) | ↓ |
| LONG: n/WR/EV | n14 42.9% +1.143 | n21 19.0% −0.238 | ↓ |
| SHORT: n/WR/EV | n19 52.6% +1.632 | n36 33.3% +0.268 | ↓ (còn dương, yếu) |
| RR đang dùng | 4.0 (v6) / 3.0 (v7 xét lại) | 3.0 | — |
| ConfirmOn (EV tắt→bật) | — (chưa có ở v7) | tắt +0.010 → **bật −0.112** (cả gộp KB-A) | bật làm TỆ HƠN |
| KẾT LUẬN | PASS có điều kiện (v7) | **yếu, gần hòa vốn, không đạt PASS** | |

### KB-B (gộp PLAY1+PLAY2, vùng NGÀY, HVN D_CLOSED)

| Thông số | TRƯỚC (v7, portfolio KB1+KB2) | SAU (KB-B @ HVN ngày) | Δ |
|---|---:|---:|---:|
| n | 60 | 215 | +155 |
| n / tuần | ~4.6 | ~16.5 | — |
| WR % | 51.7% | 25.1% | **−26.6 điểm ↓** |
| Tổng R | +57.5R | +1.0R | ↓ mạnh |
| EV / lệnh (R) | +0.958 | +0.005 | **−0.953 ↓** |
| MDD (R) | 5.0R | 33.0R | **+28.0R ↑ (rất xấu)** |
| Tháng 5/6/7 (R) | +7.0/+24.5/+26.0 ✓ | +1.0/−18.0/+18.0 ✗ | tháng 6 âm nặng |
| Nửa kỳ 1/2 | +17.5R(n30)/+40.0R(n30) | −15.0R(n107)/+16.0R(n108) | đảo dấu nửa 1 |
| PLAY1 (ngày): n/WR/EV | — | n140 WR22.1% EV−0.114 | LONG rất âm (−0.405), SHORT dương nhẹ (+0.212) |
| PLAY2 (ngày): n/WR/EV | — | n75 WR30.7% EV+0.227 | SHORT khá (+0.622, dương cả 3 tháng), LONG âm (−0.158) |
| EV @ phí 1 tick | — | −0.028 (đã âm) | chết ngay ở 1 tick |
| EV @ phí 2 tick | — | −0.061 | |
| KẾT LUẬN | PASS có điều kiện (v7) | **KILL** (EV~0, MDD quá lớn, chết ở phí 1 tick) | |

### Portfolio gộp (KB-A + KB-B, cộng gộp theo thời gian — CHƯA router 1-vị-thế)

| Thông số | TRƯỚC (v7, portfolio KB1+KB2) | SAU (KB-A+KB-B gộp) | Δ |
|---|---:|---:|---:|
| n | 60 | 343 | +283 |
| WR % | 51.7% | 24.2% | **−27.5 điểm ↓** |
| Tổng R | +57.5R | −13.4R | **đảo dấu ↓** |
| EV / lệnh (R) | +0.958 | −0.039 | **−0.997 ↓** |
| MDD (R) | 5.0R | 55.4R | **+50.4R ↑ (rất xấu)** |
| LONG: n/WR/EV | n14+13=27 (KB1+KB2 gộp) | n163 WR18.4% EV−0.264 | LONG là nguồn thua chính |
| SHORT: n/WR/EV | n19+14=33 (KB1+KB2 gộp) | n180 WR29.4% EV+0.165 | SHORT còn dương nhẹ |
| EV @ phí 1 tick | — | −0.071 (đã âm) | chết ngay ở 1 tick |
| EV @ phí 2 tick | — | −0.103 | chết sâu |
| Số cấu hình đã thử | — | KB-A: 3/10 (ConfirmOn ×2, W_CLOSED/RUNNING) · KB-B: 1/10 | trong hạn mức |
| KẾT LUẬN | PASS có điều kiện (v7) | **KILL** | |

### So KB-A vs KB-B (kiểm chứng đặc tả CORVEN — §6.3)

| Phép thử | Mốc CORVEN | Đo được | Kết quả |
|---|---|---|---|
| Tần suất KB-A | ~10 lệnh/tuần (~130/13 tuần) | 128 lệnh / 13 tuần = **9.8 lệnh/tuần** | **PASS conformance** — rất khớp, cho thấy định nghĩa vùng/trigger bám đúng quy mô lời CORVEN mô tả |
| Thứ tự WR | WR(KB-A) > WR(KB-B) | WR(KB-A)=22.7% **<** WR(KB-B)=25.1% | **NGƯỢC** |

Diễn giải phép thử "ngược": vì tần suất khớp gần như tuyệt đối (9.8≈10) mà thứ tự WR lại sai, khả
năng cao nhất là **cơ chế PLAY1/PLAY2 tại một mức giá đơn (HVN) không mang lại lợi thế "vùng tuần
ổn định hơn vùng ngày"** như CORVEN mô tả — chứ không phải do đếm sai tần suất. Cũng có thể lời
CORVEN không đúng trên đúng cửa sổ 3 tháng, 1 regime này. Cả hai khả năng đều được báo, không chọn
cái nào dễ nghe hơn.

---

## 2. Bảng lịch sử vòng lặp (đổi gì → kết quả → giữ/bỏ)

| # | Đổi gì | n / WR / EV / MDD (KB-A gộp) | Giữ hay bỏ | Vì sao |
|---|---|---|---|---|
| 1 | ConfirmOn=True (mặc định spec) | n=128 WR=22.7% EV=−0.112 MDD=24.4 | Giữ làm cấu hình chính (đúng đặc tả "bắt buộc nến xác nhận M1") | Đây là yêu cầu spec, không phải tham số tự do để chọn theo số đẹp hơn |
| 2 | ConfirmOn=False (A/B bắt buộc) | n=151 WR=25.8% EV=+0.010 MDD=15.0 | Thông tin — KHÔNG chuyển mặc định | EV vẫn ~0, không đủ để đảo kết luận; nhưng cho thấy confirm_m1 KHÔNG phải bộ lọc có ích trên cửa sổ này (bật làm EV giảm 0.122R) |
| 3 | W_CLOSED (mặc định, an toàn nhân quả) | n=128 EV=−0.112 MDD=24.4 | Giữ làm cấu hình chính | An toàn tuyệt đối, không nhìn tương lai |
| 4 | W_RUNNING (A/B) | n=182 EV=−0.011 MDD=22.0 | Thông tin — không chuyển mặc định | Khá hơn W_CLOSED nhưng vẫn âm/gần 0; không đủ để cứu KB-A, và W_RUNNING có rủi ro cơ chế phức tạp hơn không đáng đánh đổi cho lợi ích nhỏ này |
| 5 | Đối chứng ngẫu nhiên (dịch vùng ±3 giá, 5 seed, P4) | thật EV=−0.112 vs ngẫu nhiên TB=−0.070 (gap=−0.042) | **KILL — dừng cả plan** | Gap < +0.10R (ngưỡng KILL của chính plan) |

Tổng cộng KB-A: **3/10** cấu hình đã thử (ConfirmOn×2 + RangeCausal×2, trong đó ConfirmOn=True +
W_CLOSED là 1 cấu hình chung) — trong hạn mức, không cần Bonferroni nặng.

---

## 3. Mọi mặc định C# đã đổi

**Không có** — P7 (port sang `WyckoffRunner.cs` v8) bị bỏ qua vì P4 KILL. `WyckoffRunner.cs` giữ
nguyên y hệt trạng thái trước phiên này (KB1/CBR v6 vẫn là nhánh duy nhất cấp vốn, KB2/QUAY_DAU vẫn
tắt mặc định — không đụng vào).

---

## 4. Cái gì KHÔNG đo được / giới hạn phạm vi của lần đo này

1. **VWAP tuần/ngày CHƯA được đưa vào làm mức neo.** `CORVEN_SPEC_V1.md` §2 liệt kê vùng CORVEN
   gồm **cả HVN lẫn VWAP** ("HVN tuần, VWAP tuần" cho KB-A). Lần đo này **chỉ test HVN** — VWAP mới
   dừng ở việc tính sẵn trong `zones_corven.vwap_series()` (đã kiểm ở P1) nhưng chưa được nối vào
   `play_touch.py`/`play_breakret.py` làm mức neo thứ hai. Đây là **giới hạn phạm vi**, không phải
   bằng chứng phủ định VWAP — nếu muốn kết luận đầy đủ về "vùng CORVEN" phải làm thêm biến thể có
   VWAP, đây sẽ là hạng mục đầu tiên nếu có phiên tiếp theo.
2. **Không có một điểm out-of-sample nào** — kế thừa giới hạn của toàn dự án (`AUDIT_V7.md` §7):
   100% số liệu từ 1 cửa sổ 3 tháng, 1 regime (vàng tạo đỉnh), 1 hợp đồng GCQ26. Cửa sổ OOS cũ
   (2025-11→2026-04) vẫn không chạy được (thanh khoản quá mỏng). GCQ26 vừa qua First Notice Day
   31/07 → cần GCZ26/continuous mới có OOS thật cho bất kỳ biến thể nào ở đây.
3. **Định nghĩa `confirm_m1` là đề xuất tự suy, chưa kiểm chứng với CORVEN thật** — spec đánh dấu
   `⟦CẦN KIỂM⟧`. A/B cho thấy nó không giúp ích (mục 2 bảng lịch sử) nhưng không loại trừ khả năng
   một định nghĩa "nến xác nhận" khác sẽ cho kết quả khác.
4. **Gate R2 ("vùng bị chạm phải ở 25% biên của range gần")** — cách cài đặt cụ thể (range 60 nến,
   ngưỡng 25%) là diễn giải riêng, chưa có nguồn số để kiểm chứng độc lập.
5. **Router 1-vị-thế cho portfolio KB-A+KB-B** — số portfolio ở mục 1 là **cộng gộp theo thời gian**
   (không dedup/loại chồng lấn), cùng kiểu cận-trên-gần-đúng như `BASELINE.md` §1 đã làm cho
   KB1+KB2 — không mô phỏng router thật.
6. **Rủi ro carry-over trạng thái zone giữa các tuần/ngày khác nhau trong `play_breakret.py`** —
   trạng thái break/hold được lưu theo khoá `round(giá_vùng, 1)`; nếu hai tuần khác nhau tình cờ có
   HVN trùng đúng 1 chữ số thập phân, trạng thái cũ có thể bị tái sử dụng nhầm. Xác suất thấp (giá
   vàng dao động hàng trăm điểm qua các tuần) và không đủ lớn để đổi kết luận KILL, nhưng ghi nhận
   để không lặp lại nếu code này được dùng tiếp.
7. **Chi phí giao dịch là mô hình cố định theo tick**, không có spread/slippage thật (giống mọi pha
   trước của dự án — `DATA_CAPABILITY.md` §6).

---

## 5. Câu trả lời thẳng

**Vùng CORVEN (HVN tuần/ngày) làm KB-A/KB-B tốt hơn v7 không?** — **Không những không tốt hơn, mà
tệ đi rõ rệt trên mọi chỉ số** (EV, WR, MDD đều xấu hơn v7 nhiều lần), và quan trọng nhất: kết quả
"thật" (HVN tuần) **không phân biệt được với việc dịch cả vùng ngẫu nhiên ±3 giá** (gap=−0.042,
thậm chí âm — vùng thật còn tệ hơn trung bình vùng ngẫu nhiên một chút). Điều duy nhất khớp đúng ý
CORVEN là **tần suất giao dịch** (9.8 ≈ 10 lệnh/tuần) — tức việc dựng vùng/trigger đúng ĐỘ LỚN quy
mô anh ấy mô tả, nhưng bản thân cơ chế "chạm vùng đảo chiều" / "phá vùng hồi tiếp diễn" tại **một
mức giá HVN đơn lẻ** không sinh ra lợi thế thống kê trên cửa sổ 3 tháng này. Đây là kết luận âm có
giá trị: nó không nói vùng tuần/ngày CORVEN sai hoàn toàn, mà nói riêng cách vận hành 2 play tại
**riêng vùng HVN** (chưa cộng VWAP, xem mục 4.1) chưa chứng minh được bằng số.
