# Benzo Trader — chuẩn setup CORVEN cho NQ M1 (nq-corven-2)

Làm lại từ đầu ngày 2026-11-26 theo yêu cầu người học: **"follow theo CORVEN 100%"**. Nguồn luật chỉ là lời CORVEN và chart CORVEN:
- [THU-THAP-1-van-ban.md](research/nq_setup_2026-11-26/THU-THAP-1-van-ban.md): chat, văn bản, 36 ảnh.
- [THU-THAP-2-meet-chart.md](research/nq_setup_2026-11-26/THU-THAP-2-meet-chart.md): buổi Meet 07/11 và chart.

Hai file trên được gom thành [SPEC-SETUP-NQ.md](research/nq_setup_2026-11-26/SPEC-SETUP-NQ.md). Setup cũ corven-1…8 của vàng nằm ở [_old_corven8/](_old_corven8/): không build, không test.

## Setup (bản 2: người học bỏ Fail Break, chỉ đánh Break và follow trend)
- **Cấu trúc:** đỉnh/đáy 1 nến mỗi bên; gãy cấu trúc tính bằng nến **đóng cửa**, râu không tính.
- **Range:** Range Box M1. Khi đang có range thì không đánh.
  - **Break:** range vừa bị phá (≤ 30 nến); giá retest về cạnh vừa phá; nến tín hiệu đóng ngoài range, cùng hướng cấu trúc, không ngược bias phiên.
- **Follow trend (Test vùng stacked):** khi không có range.
  - Vùng stacked imbalance gần (≤ 30 nến) nằm ở thân nến; giá đã rời vùng rồi chạm lại lần đầu.
  - Cấu trúc giữ cùng hướng từ lúc sinh vùng; không ngược bias phiên.
- **Xác nhận ở nến tín hiệu:**
  - Nến đóng cùng màu và ở nửa biên độ phía hướng lệnh.
  - Delta cùng phe, |delta| ≥ trung bình |delta| của 20 nến trước.
  - Có bóng cùng phe (chấm hoặc Big Trade).
  - Thêm ≥ 1 tín hiệu cùng phe: kiệt sức còn hiệu lực, stop hunt, hoặc stacked mới. Với Test vùng stacked, chính vùng đang test được tính là tín hiệu này.
  - Có kiệt sức ngược phe chưa bị quét trong 5 nến thì không vào.
- **Lệnh:**
  - Vào market ở giá mở nến kế.
  - SL đặt sau mốc + 2 điểm, sàn 5 điểm. SL > 3 × biên độ nến trung vị thì bỏ lệnh.
  - TP 2R. Chỉ 1 lệnh mở tại một lúc.
  - Không vào sau 16:45 New York; lệnh còn mở thì đóng lúc 16:59 New York.
- **Nhãn kịch bản** (chỉ ghi nhãn, không lọc): nếu giá vào cách VWAP ngày/tuần hoặc POC TPO hôm trước/tuần trước ≤ 10 điểm.

## Backtest NQ M1, tháng 2026-10-26 → 11-25 (chi phí 1 điểm/lệnh)
| Bản | Lệnh | WR | R/lệnh sau phí | So với vào ngẫu nhiên |
|---|---|---|---|---|
| Bản 1 (có Fail Break), chạy mù một lần | 116 | 34 % | −0,049 | ngang (phần trăm 47) |
| Bản 2 (bỏ Fail Break), đang chạy | 81 | 35 % | −0,019 | ngang (phần trăm 46) |

Bản 2 được chọn **sau khi** đã xem tháng kiểm tra, nên số của bản 2 không còn là kiểm tra mù. Cần dữ liệu sau 25/11 để kiểm lại.

Chi tiết: [KET-QUA-THANG-KIEM-TRA.md](research/nq_setup_2026-11-26/KET-QUA-THANG-KIEM-TRA.md) (bản 1) · [KET-QUA-THANG-KIEM-TRA-ban2.md](research/nq_setup_2026-11-26/KET-QUA-THANG-KIEM-TRA-ban2.md) (bản 2).

## Cấu trúc file
| File | Vai trò |
|---|---|
| `BenzoNq.cs` | lõi thuần, port y chữ `research/nq_setup_2026-11-26/nq_setup.py`, chạy tăng dần `Step(i)` |
| `BenzoNqOfb.cs` | cầu nối: chạy lõi OrderFlowBubbles **thật** qua khe TEST, đọc dấu nến đã đóng (`ExportBar`), rồi gọi `Step` |
| `BenzoTrader.cs` | lớp dán Quantower: chỉ chạy chart NQ/MNQ M1; vẽ hộp range, mũi tên, SL/TP, nhãn; bảng thống kê |
| `tools/ReplayNq` | chạy bản C# trên file Footprint Export để đối chiếu với Python |
| `research/nq_setup_2026-11-26/` | spec, Python tham chiếu, pytest, backtest, parity, tín hiệu OrderFlowBubbles đã trích (`signals/`) |

## Build / test
```bash
cd benzo-trader
python -m pytest -q research/nq_setup_2026-11-26/test_nq_setup.py   # 16 ca
bash research/nq_setup_2026-11-26/run_parity.sh   # C# = Python 100 % (bản 2: 137 lệnh, bản 1: 200 lệnh) + C# nạp nguội = tăng dần
bash build.sh                                     # dist/BenzoTrader.dll → C:\OptimusFLOW\...\Indicators\BenzoTrader\ (NO_DEPLOY=1 để không copy)
```
- Tín hiệu order flow là chính lõi OrderFlowBubbles với tham số mặc định "Theo CORVEN". `build.sh` nối nguồn và đổi tên namespace/lớp, nên DLL này không trùng với OrderFlowBubbles.dll và không hiện thành indicator thứ hai.
- Lõi OrderFlowBubbles niêm phong dấu vào `%LOCALAPPDATA%\BenzoTrader\ofb_<mã>_m1.jsonl`.
- Settings chỉ có 3 ô hiển thị: Hiện entry · Hiện range · Hiện bảng thống kê. Không có ô tham số nào.
- Python lấy tín hiệu từ `perf/Golden stophunt --marks` (lệnh tạo ghi ở `prep_signals.py`).
- Khi đổi luật: sửa Python trước, đo lại, rồi sửa C#, tăng `NqCfg.Version` và chạy lại parity.
