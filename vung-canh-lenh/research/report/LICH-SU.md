# Vùng lịch sử (chế độ "Hiện TẤT CẢ vùng trong lịch sử") — nghiệm thu

Đặc tả: [PLAN-LICH-SU.md](../../PLAN-LICH-SU.md). Lõi C#: `LichSuTracker` trong `VclCore.cs`; port Python: `research/lich_su.py`.
Dữ liệu: replay C# v5 (`tools/ReplayCsv`, chạy lại 2026-10-23, bộ Display trùng từng byte với replay 2026-10-22) trên
`fp_GCZ26_XCEC_Time_20260723-20261021_90d` (86 333 nến M1, 65 phiên) và `…20260816-20260915_29d2h` (28 856 nến, 22 phiên).
Signal: `benzo-trader/research/report/_replay_cs.csv` (163 signal; nến tiêu điểm = nến đầu tiên có giờ mở ≥ giờ signal).

## Bảng tiêu chí (mục 3 của kế hoạch)

| # | Tiêu chí | Ngưỡng | 90 ngày | 29 ngày | Kết quả |
|---|---|---|---|---|---|
| 1 | khối/phiên TB · p90 | ≤ 65 · ≤ 85 | 63,2 · 81 (max 93) | 65,7 · 83 | **đạt** (29 ngày sát ngưỡng TB) |
| 2 | khối thấy trong cửa sổ 24 h p50 · p90 | ≤ 65 · ≤ 85 | 60 · 81 (max 123) | 65 · 83 | **đạt** |
| 3 | diện tích chồng giữa các khối (xét MỌI cặp, không chỉ cùng phiên) | 0% | 0,000% · 0 cặp giao | 0,000% · 0 cặp | **đạt** |
| 4 | chồng giữa lớp live và lớp lịch sử | 0 | lớp live không còn vẽ Display từ `FirstTime`; vùng live = khối còn sống (cùng đối tượng) | — | **đạt**, ghi chú ¹ |
| 5 | phủ Display (vùng-nến live có khối sống cùng dải ≥ 50%) | ≥ 97% | 97,8% | 97,7% | **đạt** |
| 6 | bắc cầu | ≤ 8% | 6,2% | 6,7% | **đạt** |
| 7 | khối < 3 phút | ≤ 3% | 1,9% | 1,9% | **đạt** |
| 8 | khối/khoá giá (tâm làm tròn 1 giá)/phiên TB | ≤ 2 | 1,89 (max 13) | 1,96 | **đạt** (29 ngày sát ngưỡng) |
| 9 | vùng sống tại nến signal Benzo TB · p90 | TB 6–8, p90 ≤ 9 | 6,7 · p90 8 (p10 6, max 10; Display live TB 6,5) | 6,8 · 8 (54 signal) | **đạt** |
| 10 | không nhìn trước | 100% | test [15]: cắt ở nến 2000 ⇒ vùng đã kết thúc y hệt, vùng sống cùng (Lo, Hi, Start), vai đã chốt không đổi | — | **đạt** (dữ liệu giả lập 3000 nến) |
| 11 | tái lập + parity Python ↔ C# từng dòng | 100% | 2 lần chạy `_lichsu.csv` trùng byte; Python 4 107 / C# 4 107 / trùng **4 107** | 1 445 / 1 445 / trùng **1 445** | **đạt** |
| 12 | thời gian `Push` | ≤ +10% | cùng harness, 4 lượt × 5 lần, min: cũ 2,896–2,911 s, mới 2,885–2,953 s ⇒ ≈ +0,4% (trong nhiễu) | — | **đạt** |
| 13 | ảnh thật Optimus Flow (đi ngang + xu hướng, rê chuột tới signal ≤ 9 khối đậm) | đạt | **chưa kiểm** — cần người học chạy trên Optimus Flow | — | **chưa đo** |

¹ Ngoại lệ có chủ đích theo kế hoạch 2.6: vùng Display bị chặn (chồng một phần với khối sống) vẽ **viền đứt, không tô** từ nến hiện tại tới mép phải —
viền này chồng giá với khối sống theo định nghĩa. Tần suất: 7 493 / 554 102 vùng-nến = 1,35% (90 ngày).

## Số đo phụ (90 ngày)
- 4 107 khối: kết thúc **xuyên phá 1 903 · hết hạn 2 195 · còn sống 9**. Thời lượng p50 73 phút, p90 343. < 15 phút (không nhãn) 13,2%.
- Vùng sống mỗi nến TB 6,7 · p90 8 · max 12. Tạo khi giá trong vùng (vai 0) 255/4 107 = 6%, chốt vai trễ p50 1 phút, p90 5; không khối nào giữ vai 0 tới cuối.
- 63,6% khối có ≥ 1 lần chạm lại; 92,4% khối từng là vùng gần (K/N). Kẹp `End = max(Start, i − G)` không lần nào phải dùng (về lý thuyết không xảy ra:
  lần chạm mở ở nến neo ≥ Start nên nến chốt − G ≥ Start; giữ kẹp làm phòng vệ).
- **Rủi ro 9** (dải khối cố định, vùng hiện tại rộng/hẹp khác > 1 giá lúc khớp): **102 957 / 542 502 lần khớp = 19,0%** (29 ngày: 20,5%) — nhiều hơn kế hoạch dự kiến.
  Nhãn mép phải khi đó nói độ rộng của vùng hiện tại, khác dải khối đang vẽ. Đã ghi README; không đổi luật (dải cố định là quyết định của kế hoạch).

## Chỗ lệch so với đặc tả — báo lại
1. Kế hoạch 2.2 viết "một vùng lịch sử chỉ khớp một vùng Display mỗi nến (Display không chồng nhau nên tự nhiên thoả)". **Tiền đề không đúng:** khối rộng
   (vd 5 giá) có thể chồng ≥ 50% với HAI vùng Display hẹp liền kề. Gặp **1 701 vùng-nến (0,31%)** trên 90 ngày. C# và Python cùng xử lý: vùng Display thứ hai
   **không khớp lại** khối đã khớp, cũng **không tạo** khối (sẽ chồng) ⇒ vào danh sách "bị chặn" (viền đứt + nhãn live). Cách này **không đổi danh sách khối**
   so với cho khớp nhiều lần (khớp lần hai chỉ đặt lại `Last = i` đã bằng i) — chỉ quyết định vùng thứ hai được vẽ ra sao.
2. Vùng Display mà khối của nó vừa kết thúc ngay ở nến đó (xuyên phá/hết hạn chốt sau bước khớp): 1 248 lần (90 ngày). Cũng đưa vào "bị chặn" ở nến đó để
   không mất vùng live nào; nến sau nó tạo khối mới theo 2.2.

## Ảnh mẫu (mô phỏng lớp tiêu điểm tại signal Benzo đầu tiên của phiên)
- [Phiên đi ngang nhất có signal, 2026-10-04](img/lich_su_di-ngang_2026-10-04.png): 57 khối trong phiên, tiêu điểm 22:13 UTC có 8 khối sống.
- [Phiên xu hướng mạnh nhất có signal, 2026-09-27](img/lich_su_xu-huong_2026-09-27.png): 72 khối, tiêu điểm có 7 khối sống.

## Nhận xét
- Mọi tiêu chí đo bằng số (1–12) đạt; 63 khối/phiên là **sàn vật lý** khi vẫn vẽ mọi vùng live từng hiện, không phải "vài khối". Muốn màn hình gọn thì dùng tiêu điểm chuột.
- Tiêu chí 1 và 8 trên file 29 ngày sát ngưỡng (65,7 và 1,96) — ngưỡng chốt trên 90 ngày; không chỉnh tham số.
- Đây là công cụ quan sát lại bộ vùng tại một thời điểm; **không** nói gì về việc vùng nào giữ giá tốt hơn.
- Chưa kiểm: sự kiện chuột `MouseMove`/`MouseLeave` và cách vẽ trên Optimus Flow thật (tiêu chí 13). Nếu chuột không chạy, tiêu điểm luôn là mép phải.

Tái lập: `cd vung-canh-lenh/research && python3 lich_su.py && python3 ve_lich_su.py`.
