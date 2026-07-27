# Entry Signal — Runner (BẢN B, thử nghiệm)

Bản sao của [EntrySignal](../quantower-entry-signal/) để **cải tiến thuật toán nhắm mục tiêu lớn (2R–3R)** —
"ăn to, ít lệnh". Chạy **song song** bản 1.5R (class + DLL riêng nên add cả 2 lên Quantower cùng lúc).

## Khác gì bản A (1.5R)
| | Bản A (scalp 1.5R) | Bản B Runner (bản này) |
|---|---|---|
| Kịch bản | KB1 phá&hồi + KB2 chạm&đảo | **CHỈ KB1 phá&hồi** (momentum). KB2 tắt |
| Mục tiêu RR | 1.5 | **2.0** (đẩy 3.0 được, xem dưới) |
| Nới TP vùng kế | từ 2R | từ 3R |
| Hold-zone (giữ vùng) | BẬT | BẬT (giống A) |

**Lý do bỏ KB2:** đảo chiều tại vùng hay chốt sớm quanh 1.5R → cản mục tiêu lớn. Runner chỉ giữ
**momentum phá&hồi giữ vùng** (nhịp đi thuận đà, có dư địa chạy).

## Backtest (data thật, cùng harness `research/`)
KB1 momentum + hold-zone, cụm≥2, SL sàn 4 giá:

| target | 1 tháng (n=9) | 6 tháng (n=10) |
|---|---|---|
| 1.5R | 78% / +0.94R | 80% / +1.00R |
| **2.0R** | **44% / +0.33R** | **50% / +0.50R** |
| 3.0R | 22% / −0.11R | 30% / +0.20R |

- **2R = điểm ngọt đã validate** (dương ở CẢ hai cửa sổ).
- **3R còn ở ranh giới** (−0.11R một tháng / +0.20R sáu tháng, chênh nhau đúng 1 lệnh, n≈10) →
  **chưa chốt được**. Để đúng RR=3 và tinh chỉnh khi có data nhiều tháng.

## Điều đã LOẠI (test rồi, không dùng)
- **Vào nến XÁC NHẬN sau nhịp hồi** (thay vì vào ngay nhịp hồi): backtest **TỆ hơn** — cum≥2 chỉ
  14–24% @3R (âm). Vào **nhịp hồi giữ vùng** vẫn tốt hơn vào xác nhận. (2 lần đo đều vậy.)
- **Lọc "đủ chỗ chạy tới 3R" (clearance vs vùng):** vô dụng — vùng quá dày (POC/VAH/VAL ×3 phiên +
  D-1) nên 65/66 lệnh luôn có vùng cản trong 3R → lọc giết sạch.

## Việc cần làm cùng nhau (khi có data)
1. Data nhiều tháng **front-month đang lỏng** (không phải hợp đồng xa) → xác nhận 3R có thật dương không.
2. Thử phân loại "ngày xu hướng" (runner chạy xa) vs "ngày sideway" (mean-revert ở 1.5R).
3. Đo lại clearance theo **swing-high/low cấu trúc** (không theo vùng dày) — trả lời ca lệnh-1 (bị
   rejection trên đầu chặn ở 2R).

## Build
`./build-runner.sh` → `dist/EntrySignalRunner.dll` (net10.0-windows, cần `~/quantower-libs`). Deploy Windows.
