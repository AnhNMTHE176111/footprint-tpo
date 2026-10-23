# Lọc khối lịch sử — 2 hạng (nghiệm thu PLAN-LOC-VUNG)

Đặc tả: [PLAN-LOC-VUNG.md](../../PLAN-LOC-VUNG.md). Lõi C#: `LichSuTracker` (`VLichSu.TQ/TQTime`, `Vcl.LsRankTouch = 1`, `Vcl.LsRankAgeMin = 60`,
`LichSuTracker.VeTai`) trong `VclCore.cs`; vẽ: `PaintLichSu` trong `VungCanhLenh.cs`; port Python: `research/lich_su.py` (`tq`, hàm `loc_vung`).
Dữ liệu: replay C# v5 (`tools/ReplayCsv`, chạy lại 2026-10-23) trên `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (86 333 nến, 4 107 khối, 163 signal A)
và `…20260816-20260915_29d2h` (28 856 nến, 1 445 khối, 54 signal A). Bộ Display, `_episodes.csv` và 9 cột cũ của `_lichsu.csv` **trùng từng byte**
với bản trước khi sửa — chỉ thêm cột `tq_utc`.

**Hạng 1** = khối đã có ít nhất một lần giá quay lại chạm và đã hiện ≥ 60 phút; vẽ suốt lịch sử (≈ 23 khối/24 giờ). Khối còn lại chỉ hiện khi rê chuột tới
nến đang soi. **Đây là lọc để chart gọn, không phải lọc vùng mạnh**: đã đo (LOC-VUNG-BENCH.md) — sau khi lên hạng, khối hạng 1 không bật giá nhiều hơn
khối giả cùng cỡ, cùng khoảng cách; vùng được chạm nhiều lần là vùng giá đang đi ngang quanh đó, lần sau còn hay bị xuyên hơn.

## Bảng tiêu chí (mục 4 của kế hoạch)

| # | Tiêu chí | Ngưỡng | 90 ngày | 29 ngày | Kết quả |
|---|---|---|---|---|---|
| 1 | % khối lên hạng 1 | 38–42% | 39,7% (1 629 / 4 107) | 39,7% (574 / 1 445) | **đạt** |
| 2 | khối hạng 1 trong cửa sổ 24 h p50 · p90 | ≤ 25 · ≤ 35 | 23 · 32 | 25 · 33 | **đạt** |
| 3 | khối hạng 1 / phiên TB · p90 | ≤ 27 · ≤ 35 | 25,1 · 32 | 26,1 · 32 | **đạt** |
| 4 | tại signal: khối hạng 1 đang hiệu lực TB · p90 | 2,0–2,5 · ≤ 4 | 2,2 · 4 (p10 1) | 2,0 · 4 | **đạt** |
| 5 | tại signal: đậm + viền mảnh = khối sống (= LICH-SU tiêu chí 9) | TB 6,7 | 2,2 + 4,5 = 6,7 (p90 8); bằng nhau ở **163/163** signal | 2,0 + 4,7 = 6,8; 54/54 | **đạt** ¹ |
| 6 | % signal có khối hạng 1 cách giá ≤ 5 / ≤ 10 giá | ≥ 70% / ≥ 80% | 73,6% / 84,0% | **63,0% / 77,8%** | **đạt trên 90 ngày** (ngưỡng chốt); **29 ngày dưới ngưỡng** ² |
| 7 | không nhìn trước | 100% | cắt ở nến 21 583 / 43 166 / 64 749: `tq` < cắt y hệt 402 / 826 / 1 255 khối; `tq` ≥ cắt ⇒ −1: 2 / 1 / 3; sai **0** | cắt 7 214 / 14 428 / 21 642: y hệt 142 / 292 / 425; ⇒ −1: 0 / 2 / 2; sai **0** | **đạt** ³ |
| 8 | lên hạng không hồi tố (`TQTime ≥ Start + 60`, `NChamLai ≥ 1` tại `TQ`, `TQ ≤ End`) | 100% | 1 629 / 1 629 | 574 / 574 | **đạt** (+ test [16] mục 9: `TQ` = đúng nến ĐẦU TIÊN thoả, hạng 2 không bỏ sót) |
| 9 | parity Python ↔ C# từng dòng `_lichsu.csv` kể cả `tq_utc` | 100% | **4 107 / 4 107** | **1 445 / 1 445** | **đạt** |
| 10 | thời gian `Push` | ≤ +5% | cùng harness, bản cũ (HEAD) vs bản mới, 4 lượt × 5 lần, min: cũ 4,234 · 4,160 · 3,832 · 3,899 s; mới 4,273 · 3,955 · 3,952 · 3,866 s ⇒ min chung **+0,9%** (từng lượt −4,9…+3,1%, trong nhiễu) | — | **đạt** ⁴ |
| 11 | ảnh thật Optimus Flow (1 ngày đi ngang + 1 ngày xu hướng: hạng 1 trong 24 h ≤ 35; rê chuột tới signal ≤ 4 khối đậm + viền mảnh) | đạt | **chưa kiểm** — cần người học chạy trên Optimus Flow | — | **chưa đo** |

¹ Python đếm trên `_lichsu.csv` do C# xuất, cùng luật `LichSuTracker.VeTai` (đậm = `TQTime ≤ tF ≤ End`; viền mảnh = sống tại tF mà chưa lên hạng tại tF).
Test [16] kiểm thêm trên lõi: đậm + viền mảnh = khối sống tại mọi nến.
² Đúng như kế hoạch dự báo (rủi ro 7: 29 ngày ≤ 5 giá ≈ 63%, engine khởi động lại từ 08-16). **Không chỉnh ngưỡng/hằng** cho khớp.
³ "Tạm lên hạng rồi reset": khối còn sống lúc cắt đã đủ điều kiện, về sau kết thúc với `End` < `TQ` (hết hạn lùi `End` về lần hiện cuối, hoặc xuyên phá
lùi 5 nến) ⇒ bản đủ có `TQ = −1`. Gặp 0 lần (90 ngày) và 1 lần (29 ngày) ở các điểm cắt. Khi đang live, khối đó có hiện hạng 1 trong vài nến rồi trở lại
hạng 2 khi kết thúc — chỉ xảy ra với phần sau `End` của khối, không có thông tin tương lai nào lọt vào nến ≤ `End`.
⁴ Thời gian tuyệt đối chậm hơn LICH-SU.md (2,9 s) vì máy đang tải khác; so sánh chỉ có nghĩa trong cùng một lần đo.

## Chỗ lệch so với đặc tả — báo lại
1. Test 5 của kế hoạch ("xuyên phá chốt nến 70, End 65; chạm lại lần đầu nến 68") **không dựng được**: khi xuyên phá, lần chạm cuối bắt đầu ≤ `i − G` = `End`
   và trong lúc nó còn mở không lần chạm mới nào bắt đầu được ⇒ lên hạng do CHẠM LẠI không bao giờ > `End`. Chỉ TUỔI mới vượt `End` được. Test dùng:
   chạm lại lần đầu nến 57 rồi vượt lên, chốt nến 62, `End` = 57, tuổi đủ ở nến 60 ⇒ `TQ` = 60 lúc còn sống ⇒ reset −1. Thêm ca đối chứng: chạm lại nến 65
   rồi xuyên phá (`End` = 65) ⇒ `TQ = 65` được giữ; và ca hết hạn có lần chạm lại sau `End`.
2. Vẽ khối hạng 1 khi tiêu điểm còn trước `TQTime`: đoạn [Start, TQ) viền mảnh như hạng 2; đoạn [TQ, End] vẫn tô nhạt (35) như mọi khối hạng 1 ngoài
   tiêu điểm (phần đó nằm bên phải tiêu điểm, cùng chỗ với các khối tương lai khác) — không tô đậm.
3. Khối hạng 2 còn sống nhưng tiêu điểm đang ở nến cũ (khối bị ẩn): vùng Display nó đang khớp vẽ bằng viền đứt + nhãn live từ nến hiện tại (dùng chung
   đường vẽ với vùng "bị chặn"), để vùng live không biến mất.

## Ảnh mẫu (mô phỏng lớp vẽ 2 hạng, tiêu điểm = signal Benzo đầu tiên của phiên)
- [Đi ngang, 2026-10-04](img/loc_vung_di-ngang_2026-10-04.png): 26 khối hạng 1 trong phiên (bản cũ 57 khối); tiêu điểm 22:13 UTC: 2 đậm + 6 viền mảnh.
- [Xu hướng, 2026-09-27](img/loc_vung_xu-huong_2026-09-27.png): 29 khối hạng 1 (bản cũ 72); tiêu điểm: 1 đậm + 6 viền mảnh.

## Nhận xét
- Tiêu chí 1–10 đo bằng số đều đạt trên 90 ngày; số Python port khớp từng con số với bench của Fable (39,7% · 23/32 · 25,1/32 · 2,2/4 · 73,6/84,0).
- Tiêu chí 6 trên 29 ngày dưới ngưỡng (63% / 78%) — đánh đổi gọn ↔ thấy đã nói trước trong kế hoạch, không chỉnh.
- Không có tiêu chí "mạnh": bảng B của LOC-VUNG-BENCH.md cho thấy khối hạng 1 đảo chiều **thấp hơn** đối chứng gương khớp khoảng cách (TRAIN −2,9 · TEST −6,6 điểm).
- Chưa kiểm: vẽ trên Optimus Flow thật (tiêu chí 11).

Tái lập: `cd vung-canh-lenh/research && python3 lich_su.py && python3 ve_lich_su.py` (bench: `python3 loc_vung_bench.py --reps 10`).
