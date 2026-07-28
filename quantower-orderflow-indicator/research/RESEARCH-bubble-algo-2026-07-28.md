# Research: vì sao chart toàn **Big Trade**, gần như không có **Absorption**?

Ngày 2026-07-28 · dữ liệu `data-export/fp-m1-6-month.csv` (GCQ26 dxFeed, lọc từ 05/2026 khi hợp
đồng đã lỏng → 74.974 nến M1) · code soi: [OrderFlowBubbles.cs](../OrderFlowBubbles.cs)

Kết luận ngắn: **cảm giác đúng**, và nguyên nhân nằm ở thuật toán chứ không ở thị trường.
Absorption là **tập con thực sự** của Big Trade trong code hiện tại — không tồn tại tình huống
absorption nổ mà big-trade không nổ.

---

## 1. Bằng chứng dữ liệu thật: feed KHÔNG có "lệnh đơn lớn"

| File export | nến | `Max one trade Vol.` khác 0 | `Max/Min delta` khác 0 | `Average buy/sell size` khác 0 | `Average size` |
|---|---:|---:|---:|---:|---|
| fp-m1.csv | 2.451 | **0,0 %** | 0,0 % | 0,0 % | med 1,07 |
| fp-m1-1-month | 28.071 | **0,0 %** | 0,0 % | 0,0 % | med 1,07 |
| fp-m1-6-month | 99.678 | **0,0 %** | 0,0 % | 0,0 % | med ~1 |
| tpo-chart-m30 | 3.016 | **0,0 %** | 0,0 % | 0,0 % | — |
| TPO-chart-daily | 952 | **0,0 %** | 0,0 % | 0,0 % | — |

Hệ quả trong code (`ComputeBar`, nhánh Big Trade):

```
motReady = ready && _rLvlMot.BarCount > 0 && _rLvlMot.Median > 0     // luôn FALSE với feed này
=> metric = vol (volume/mức), rr = _rLvlVol                          // fallback
```

→ **"Big Trade" đang không đo lệnh lớn.** Nó đo *volume của một ô footprint* — đúng cùng đại lượng
mà Absorption dùng. Hai tín hiệu chạy trên **một metric**, chỉ khác ngưỡng.

Phụ: `Average size` ≈ 1,07 và `Trades ≈ Volume` → feed cấp trade lẻ ~1 lot; kể cả khi Quantower
điền `MaxOneTradeVolume` thì "cú đánh lớn" cũng gần như không quan sát được trên dxFeed.

Cách tự kiểm 10 giây trên chart: rê chuột vào bubble → tooltip in nguồn.
`Big trade (vol/mức)` = đang fallback; `Big trade (lệnh đơn)` = feed có cấp.

## 2. Ngưỡng bất đối xứng — Big Trade có cửa hậu, Absorption có 4 khoá

| | Big Trade | Absorption |
|---|---|---|
| điều kiện | `z ≥ 4.5` **OR** `vol ≥ 3 × median` | `z ≥ 4.0` **AND** 1 phe ≥ 60 % **AND** cách cực trị ≤ 2 tick **AND** close lùi ≥ 1 tick |
| logic | 1 OR | 4 AND |

Baseline `_rLvlVol` gộp **mọi mức của 100 nến** (kể cả mức rìa 1–2 lot) → median ~3–4, MAD ~2.
Quy đổi: `z ≥ 4.5` ⇔ ~16 lot/mức, mà cửa OR `3 × median` ⇔ chỉ ~9–13 lot. Nến M1 median 43 volume
trải trên ~10–14 mức → **POC của một nến bình thường đã vượt cửa OR**.

## 3. Đo tần suất (mô phỏng per-level hiệu chỉnh theo V/H/L/Δ thật, 5.960 nến tháng 7)

Export không có per-level nên footprint được dựng lại 2 cách (`fire_rate_sim.py`): A = random-walk
phản xạ (phân bố phẳng), B = hình chuông quanh POC. Thực tế nằm giữa hai mô hình.

| | mô hình A | mô hình B |
|---|---:|---:|
| Big Trade nổ | **56,6 %** số nến | **17,2 %** số nến |
| — trong đó chỉ nhờ cửa OR `3×median` | 51,0 % | 70,8 % |
| Absorption nổ | 11,0 % | 1,0 % |
| **Tỷ lệ Big : Abs** | **5,1×** | **17×** |
| Khi Absorption nổ, Big Trade cũng nổ | **100 %** | **100 %** |
| …và nổ **đúng cùng mức giá** (đè lên nhau) | 71,4 % | 16,1 % |

Nút thắt của Absorption đo được: mức đạt `z ≥ 4` xuất hiện ở 33 %/7,2 % số nến, nhưng nằm trong
**≤ 2 tick của cực trị** chỉ còn 26,6 %/2,4 % — volume tụ ở giữa nến, cực trị thì mỏng.

Lớp thứ tư là **hiển thị**: `absCands` add trước, `bigTradeCands` add sau → halo Big Trade vẽ đè;
Absorption `UseBarWidth` nên chỉ to bằng bề rộng nến (~8 px khi zoom thường) còn halo tới 26 px.

## 4. Thị trường thật ở vùng đảo chiều trông thế nào (dữ liệu thật, không mô phỏng)

2.548 điểm đảo chiều M1 (cực trị ±15 nến, biên độ ≥ 2 USD cả hai phía) — `reversal_signature.py`:

| chữ ký tại nến cực trị | ĐỈNH | ĐÁY | mọi nến (baseline) |
|---|---:|---:|---:|
| ABSORPTION (phe thuận đà vẫn chủ động mà giá quay đầu) | 23,9 % | 24,5 % | 10,8 % |
| TWO-SIDED (volume lớn, delta ~0 — đúng định nghĩa ebook) | 23,7 % | 24,4 % | 17,8 % |
| AGGRESSIVE (phe ngược đập vào) | 12,2 % | 12,4 % | 6,6 % |
| QUIET (volume không bất thường) | 40,2 % | 38,8 % | 64,8 % |
| **volume/nến so với median** | **1,79×** | **1,92×** | 1,13× |

Hai điều quan trọng:
1. Ở đảo chiều thật, hấp thụ + hai phe (≈48 %) **phổ biến gấp 4 lần** phe-ngược-đập (12 %) → về
   bản chất thị trường, absorption *nên* xuất hiện nhiều hơn cái chart đang vẽ.
2. Volume ở đó chỉ ~**1,8× median**, không phải `z = 4–4,5`. Ngưỡng hiện tại **không nhắm vào vùng
   đảo chiều**, nó nhắm vào nến sôi động nhất.

## 5. Nhưng: chữ ký nào thật sự có EDGE? (`edge_test.py`, dữ liệu thật)

Tín hiệu tại cực trị cục bộ, thắng = đi ngược đà đủ TARGET trước khi đi tiếp đủ TARGET, 20 nến.

| chữ ký | M1 (1 USD) | M5 (2 USD) | M15 (3 USD) | M30 (4 USD) |
|---|---|---|---|---|
| BASE (không lọc) | 55,9 % (n=17960) | 59,1 % (n=3533) | 62,9 % (n=1180) | 64,2 % (n=562) |
| **volume ≥ 3× median** | **58,8 %** (n=4080) | **63,0 %** (n=657) | **68,6 %** (n=191) | **73,3 %** (n=105) |
| effort-vs-result (Δ thuận mạnh, close lùi) | 50,5 % (n=513) | 77,8 % (n=27) | 80,0 % (n=5) | 50,0 % (n=2) |
| ebook 2 phe (\|Δ%\|≤.10, range hẹp) | 58,4 % (n=125) | 48,8 % (n=43) | 27,8 % (n=18) | 75,0 % (n=8) |
| aggressive ngược đà | 56,5 % (n=888) | 44,9 % (n=49) | 0 mẫu | 0 mẫu |

Đọc bảng cho đúng — đây là chỗ dễ tự lừa mình:
- **"Volume bất thường" là chữ ký duy nhất có edge nhất quán và tăng dần theo khung** (+2,9 pp ở M1
  → +9,1 pp ở M30, n đủ lớn). Tức phần *lõi* của Big Trade không sai, chỉ bị đặt sai tên và bắn quá dày.
- Các biến thể absorption tinh vi hơn có n quá nhỏ (5–125) → sai số ±5–22 pp, **chưa chứng minh
  được gì**. Riêng effort-vs-result ở M1 còn **dưới base**.
- Nghịch lý mục 4 vs mục 5 là Bayes chuẩn: absorption *hay xuất hiện tại* đảo chiều (P(dấu hiệu|đảo
  chiều) cao) nhưng cũng xuất hiện đầy chỗ khác → P(đảo chiều|dấu hiệu) không tốt hơn.
- **Giới hạn:** delta ở đây là bar-level. Absorption thật là hiện tượng *per-level* (volume tại một
  ô giá, bid/ask tại chính ô đó) — export không có, nên phần 5 chưa phải phán quyết cuối cho
  absorption; nó chỉ nói: chưa có bằng chứng absorption bar-level ăn đứt volume-spike.

## 6. Đề xuất sửa (theo thứ tự lợi ích/công sức)

1. **Gọi đúng tên khi fallback.** MOT trống → tín hiệu là *ô volume cao (HVN cell)*, không phải
   Big Trade. Đổi nhãn + màu, hoặc tự tắt Big Trade khi `_rLvlMot` rỗng.
2. **Đóng cửa hậu OR.** `z ≥ BigZ` **AND** `vol ≥ k×median` (k≈4–6) thay cho OR — riêng việc này cắt
   ~51–71 % số lần bắn.
3. **Baseline so POC với POC.** Nạp `_rLvlVol` bằng top-2/3 mức mỗi nến thay vì mọi mức, để "bất
   thường" nghĩa là bất thường so với các ô đậm lịch sử, không phải so với ô rìa.
4. **Absorption v2** — bám ebook (`ebook/text/orderflow-full.md`, tr. 87–88) thay vì đòi 1 phe ≥60 %:
   volume ô lớn bất thường **trên cả bid lẫn ask** + **xác nhận trễ 1–3 nến**: giá không phá qua mức
   đó. Và gom **đa nến**: cùng mức ±2 tick tích lũy 2–5 nến → vẽ **vùng**, không vẽ bubble lẻ
   (ebook: hấp thụ "mất vài phút mới hình thành").
5. **Ưu tiên vẽ:** absorption vẽ sau cùng; nếu Big Trade trùng mức absorption thì bỏ hoặc hạ thành viền.
6. **Khung dùng:** bảng mục 5 cho thấy bubble đáng tin dần từ M5 lên M30; M1 nên để số delta + DMA,
   đừng kỳ vọng bubble lọc được vùng quan trọng.
7. **Nếu muốn Big Trade THẬT:** cần feed cấp size từng trade (Rithmic/CQG…) — kiểm tra bằng
   Time & Sales trong Quantower xem có trade size > 1 hay không.
