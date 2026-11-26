# Benzo Trader — chuẩn setup CORVEN cho NQ M1 (nq-corven-3)

Làm lại từ đầu ngày 2026-11-26 theo yêu cầu người học: **"follow theo CORVEN 100%"**. Nguồn luật chỉ là lời CORVEN và chart CORVEN:
- [THU-THAP-1-van-ban.md](research/nq_setup_2026-11-26/THU-THAP-1-van-ban.md): chat, văn bản, 36 ảnh.
- [THU-THAP-2-meet-chart.md](research/nq_setup_2026-11-26/THU-THAP-2-meet-chart.md): buổi Meet 07/11 và chart.

Hai file trên được gom thành [SPEC-SETUP-NQ.md](research/nq_setup_2026-11-26/SPEC-SETUP-NQ.md). Setup cũ corven-1…8 của vàng nằm ở [_old_corven8/](_old_corven8/): không build, không test.

## Setup bản 3 (người học chốt 2026-11-26)
Người học đã chốt ba điều: bỏ Fail Break; follow trend không cần stacked imbalance, chỉ theo một move đang đi; bỏ bias, đánh theo cấu trúc và bối cảnh.

**Cấu trúc:** đỉnh/đáy 1 nến mỗi bên; gãy cấu trúc tính bằng nến **đóng cửa**, râu không tính.

**Bối cảnh:** Range Box M1. Khi đang có range thì không đánh.

**Break:** range vừa bị phá (≤ 30 nến). Trong 3 nến gần nhất giá retest về cạnh vừa phá, và nến tín hiệu đóng ngoài range, cùng hướng cấu trúc.

**Follow trend:** khi không có range. Số trong ngoặc là số agent chọn.
- Trong 30 nến trước có một move theo hướng cấu trúc, dài ≥ 2 × biên độ nến trung vị ("để ý momentum").
- Sau đỉnh (hoặc đáy) của move, giá hồi 1–10 nến và không hồi quá 50 % move ("không được test quá sâu").
- Mỗi move chỉ vào một lần.

**Xác nhận ở nến tín hiệu:**
- Nến đóng cùng màu và ở nửa biên độ phía hướng lệnh.
- Delta cùng phe, |delta| ≥ trung bình |delta| của 20 nến trước.
- Có bóng cùng phe (chấm hoặc Big Trade).
- Thêm ≥ 1 tín hiệu cùng phe trong 3 nến: kiệt sức còn hiệu lực, stop hunt, hoặc stacked mới. Với Break, giá thò qua cạnh range kèm bóng cũng được tính là stop hunt.
- Có kiệt sức ngược phe chưa bị quét trong 5 nến thì không vào.

**Lệnh:**
- Vào market ở giá mở nến kế.
- SL đặt sau mốc + 2 điểm. Mốc là cạnh vừa phá (Break) hoặc đáy/đỉnh nhịp hồi (Follow trend).
- SL sàn 5 điểm; SL > 3 × biên độ nến trung vị thì bỏ lệnh.
- TP 2R. Chỉ 1 lệnh mở tại một lúc.
- Không vào sau 16:45 New York; lệnh còn mở thì đóng lúc 16:59 New York.

## Backtest NQ M1 (chi phí 1 điểm/lệnh)
| Bản | 26/10–25/11 | 14/09–23/10 (đoạn trước, chưa dùng để chọn luật bản 3) |
|---|---|---|
| Bản 1 (Fail Break + Break + Test vùng stacked + bias), chạy mù một lần | 116 lệnh, −0,049R/lệnh, ngang vào ngẫu nhiên | — |
| Bản 2 (bỏ Fail Break) | 81 lệnh, −0,019R/lệnh, ngang vào ngẫu nhiên | 55 lệnh, −0,40R/lệnh |
| **Bản 3 (hiện tại)** | 179 lệnh, WR 37 %, **+0,092R/lệnh**; vào ngẫu nhiên phần trăm 86, chưa tới 95 | 111 lệnh, WR 31 %, **−0,147R/lệnh** |

Bản 2 và bản 3 được chọn sau khi đã xem tháng 26/10–25/11, nên số của tháng đó không còn là kiểm tra mù. Đoạn 14/09–23/10 cho bản 3 ra âm, vì vậy **chưa thấy lợi thế ổn định**.

Chi tiết: [KET-QUA-THANG-KIEM-TRA-ban3.md](research/nq_setup_2026-11-26/KET-QUA-THANG-KIEM-TRA-ban3.md) · bản 2: [KET-QUA-THANG-KIEM-TRA-ban2.md](research/nq_setup_2026-11-26/KET-QUA-THANG-KIEM-TRA-ban2.md) · bản 1: [KET-QUA-THANG-KIEM-TRA.md](research/nq_setup_2026-11-26/KET-QUA-THANG-KIEM-TRA.md).

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
python -m pytest -q research/nq_setup_2026-11-26/test_nq_setup.py   # 20 ca
bash research/nq_setup_2026-11-26/run_parity.sh   # C# = Python 100 % (bản 3: 290 lệnh, bản 2: 137, bản 1: 200 từ 14/09) + C# nạp nguội = tăng dần
bash build.sh                                     # dist/BenzoTrader.dll → C:\OptimusFLOW\...\Indicators\BenzoTrader\ (NO_DEPLOY=1 để không copy)
```
- Tín hiệu order flow là chính lõi OrderFlowBubbles với tham số mặc định "Theo CORVEN". `build.sh` nối nguồn và đổi tên namespace/lớp, nên DLL này không trùng với OrderFlowBubbles.dll và không hiện thành indicator thứ hai.
- Lõi OrderFlowBubbles niêm phong dấu vào `%LOCALAPPDATA%\BenzoTrader\ofb_<mã>_m1.jsonl`.
- Settings chỉ có 3 ô hiển thị: Hiện entry · Hiện range · Hiện bảng thống kê. Không có ô tham số nào.
- Python lấy tín hiệu từ `perf/Golden stophunt --marks` (lệnh tạo ghi ở `prep_signals.py`).
- Khi đổi luật: sửa Python trước, đo lại, rồi sửa C#, tăng `NqCfg.Version` và chạy lại parity.
