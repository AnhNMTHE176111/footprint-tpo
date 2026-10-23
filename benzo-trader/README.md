# Benzo Trader — 4 setup A/B/C/D trên nến M1 đã đóng

Trục thiết kế: `plans/BENZO-TRADER-plan.md` (mục 2, 2.2, 2.3, 6). Đường ống: nhận nến M1 đã đóng → vùng/VWAP/chế độ M5
(`BenzoZones`) → 4 detector (`BenzoDetectors`) → mô phỏng SL/TP → thống kê → bảng + mũi tên → Telegram kèm ảnh → CSV log.
Logic 4 setup là bản port C# của `research/setup_*.py` ở "ô chính", đối chiếu từng tín hiệu với Python (xem mục Parity).

> **Trạng thái kiểm chứng (QĐ-5/QĐ-6):** cả 4 setup **chưa có lợi thế đo được** trong backtest 65 phiên (file 90 ngày GCZ26).
> Vẫn để 4 công tắc **BẬT mặc định** để chạy forward test và thu thống kê live — **đây không phải khuyến nghị vào lệnh**.

## Build / deploy / test
```bash
cd benzo-trader
bash build.sh         # concat ProfileEngine.cs + VclCore.cs (vung-canh-lenh) + BenzoCore.cs + BenzoSr.cs + BenzoLayers.cs + BenzoZones.cs + BenzoDetectors.cs + BenzoSetupA5.cs + BenzoTrader.cs → dist/BenzoTrader.dll
                      # (VCLCORE=<file> để dùng bản VclCore.cs khác; báo lỗi nếu có cảnh báo MỚI — 2 cảnh báo CS0649 của ProfileEngine.cs là có sẵn, không phải của Benzo)
dotnet run --project tests            # unit test (Debug, gồm test DemoDetector)
dotnet run -c Release --project tests # bản ship: không có DemoDetector (mục [11] chạy hồi quy trên file 90d nếu có trong repo)
python research/parity_check.py       # parity C# ↔ Python (chạy tools/ReplayCsv rồi so tín hiệu), ghi research/report/PARITY.md
python research/parity_b_v3.py        # parity riêng setup B cũ / v2 / v3 (mảng vùng từng nến + lệnh), ghi research/report/PARITY-B-v3.md
python research/parity_check.py --c-layers  # parity riêng setup C + các lớp mới (C0 / C4 / C6, TP chính và TP 2R), ghi research/report/PARITY-C-LAYERS.md
python research/parity_a_v5.py        # parity setup A v5 / A-v4 (4 tầng: mức vùng · tín hiệu raw · trạng thái · lệnh không chặn / có chặn mở ảo), chạy tools/ReplayA5, ghi research/report/PARITY-A5.md
```
- `build.sh` copy thẳng vào `C:\OptimusFLOW\Settings\Scripts\Indicators\BenzoTrader\` (TẠO thư mục nếu chưa có).
- Cần `~/quantower-libs/{TradingPlatform.BusinessLayer,System.Drawing.Common,System.Private.Windows.Core}.dll`.
  `System.Private.Windows.Core.dll` lấy từ `C:\OptimusFLOW\TradingPlatform\v*\bin\System\` (cần để dùng `Bitmap`/`Graphics.FromImage`
  khi chụp ảnh); `qw-build.sh` tự thêm tham chiếu nếu file này có mặt.
- Add indicator vào **chart M1 có Volume Analysis**.

## Cấu trúc file
| File | Vai trò |
|---|---|
| `BenzoCore.cs` | Logic thuần, KHÔNG phụ thuộc SDK: `Signal`, `BarData`, `ISetupDetector`/`IObservingDetector`, `SetupContext`, `BenzoCore` (Simulate, thống kê, caption, mốc reset), `SignalCache`, `BenzoEngine`, `SignalCsv`, `TeleClient`, `DemoDetector` (chỉ DEBUG) |
| `BenzoSr.cs` | Vùng thêm cho B: `BenzoSr` (HVN/POC/VAH/VAL ngày-tuần, PDH/PDL tính ở nến đầu phiên từ phiên/tuần đã đóng; gán 7 khe VCL theo mã vùng), `BenzoZoneNames` (nhãn tiếng Việt). Dùng lõi `vung-canh-lenh/VclCore.cs` nguyên văn (không viết lại) |
| `BenzoLayers.cs` | Lớp vùng mới của setup C (chỉ chạy khi bật): `TpoShape`/`TpoAcc` (hình dạng profile TPO hôm qua D/P/b + vùng dày), `ChochFrame` (VA nhỏ từ 3 lần đổi hành vi), `SrFrame` (hành lang S/R từ vùng VCL, dùng chung lõi VCL với B), `CLayerOptions` |
| `BenzoZones.cs` | Port `kernel.py`: tách phiên (khoảng trống > 30′), VA 70% hôm qua / VA Âu chốt 19:00 VN / IB 19:20–20:20 VN, VWAP ngày + tuần, chế độ M5, trung vị 50 nến, nến dài nhất phiên, zigzag 2 giá, `IsConfirmBar`; `BenzoRisk` (SL lai) |
| `BenzoDetectors.cs` | `DetectorA` (= **A V3 cũ**, giữ cho test hồi quy, KHÔNG chạy live) và `DetectorB/C/D` (chạy theo dòng: `Observe` mỗi nến đóng, `TryDetect` trả kết quả của nến đó) |
| `BenzoSetupA5.cs` | Setup **A Phá hồi v5**: `DetectorA5` (máy trạng thái y chữ `setup_a_v5.detect5`), `HvnMath` (port `kernel.find_hvn` + `peak_sharpness` + kẹp dải), `HvnBook` (sổ HVN theo phiên, không nhìn trước), `VclCoreSource` (bọc `VclCore.cs` — nguồn vùng S/R), `A5Watch`/`A5Text` (dữ liệu + nhãn tiếng Việt của vùng đang canh) |
| `../vung-canh-lenh/VclCore.cs` | Không nằm trong thư mục này nhưng được **nối nguồn vào bản build** (lõi vùng S/R của indicator Vùng Canh Lệnh; Benzo vẫn là 1 DLL độc lập) |
| `BenzoTrader.cs` | Lớp dán Quantower: Settings, vòng đời, vẽ, chụp ảnh Win32, điều phối Telegram |
| `tests/` | Test chạy thật trên chính `BenzoCore/Zones/Detectors` |
| `tools/ReplayCsv/` | Console chạy detector trên file footprint export (không cần Quantower) — dùng cho parity. `A` ở đây là **A V3 cũ** (class `DetectorA`, không còn chạy live) |
| `tools/ReplayA5/` | Console chạy `DetectorA5` (A v5 / A-v4 `--novcl`) cho `research/parity_a_v5.py` |

## Settings (plan 2.3 — không có ngưỡng số nào)
Lệch giờ (7) · Telegram bật · bot token · chat id · **gửi thử** · bật setup A/B/C/D · **B · thêm vùng v2 (HVN/VA/POC)** · **B · thêm vùng S/R (VCL, PDH/PDL)** · **C · cổng hình D / vùng dày P-b / VA nhỏ CHoCH / hành lang S/R / TP về cạnh-POC** · **đặt lại thống kê** · Hiện bảng · **Hiện vùng A đang canh** (mặc định BẬT; chỉ bật/tắt phần vẽ vùng + nhãn của A, không đổi logic).
Năm công tắc của C (xem mục "C · các lớp vùng mới") mặc định **BẬT** nhưng chỉ có tác dụng khi setup C bật; đổi công tắc ⇒ engine dựng lại, cache niêm phong bị bỏ.
Hai công tắc vùng của B mặc định **BẬT** (theo yêu cầu người học) — xem mục "B · thêm vùng" bên dưới; đổi công tắc ⇒ cache niêm phong bị bỏ và dò lại từ đầu lịch sử (cả 4 setup).
Hai "nút" là ô tick: **bật lên = bấm** (bắt cạnh lên; muốn bấm lần nữa thì tắt rồi bật lại).
Token/chat id điền tay, không có trong code.

## Vòng đời & chống tính lại
- Chỉ xử lý nến **đã đóng** (`Count−2`), mỗi nến dò **một lần**. `ClosedBars` chặn detector nhìn nến sau `closedIdx` (ném lỗi).
- **Niêm phong** `%LOCALAPPDATA%\BenzoTrader\cache_<symbol>_<khung>.jsonl`: dòng `sig` (tín hiệu) + dòng `rng` (khoảng thời gian đã dò).
  Nến trong khoảng đã dò **không dò lại** dù reload; kết quả TP/SL luôn tính lại từ nến. Đổi `BenzoCore.LogicVersion` (khi sửa logic detector)
  ⇒ cache cũ bị bỏ. Đổi công tắc A/B/C/D **không** dò lại lịch sử đã niêm phong (xoá file cache nếu muốn dò lại).
- 1 lệnh mở cùng lúc: khi còn lệnh mở thì không dò. Mô phỏng: chạm cả SL lẫn TP cùng nến ⇒ SL; chi phí 0,2 giá/lệnh.
- Mặc định thống kê đếm từ đầu lịch sử chart đã nạp; "Đặt lại thống kê" ghi mốc UTC vào `reset_<symbol>.txt`, chỉ đếm lệnh sau mốc; "Hiện lại toàn bộ thống kê" xoá mốc đó (lệnh không mất, nằm trong cache). Bảng chỉ hiện setup đang bật, dưới mỗi setup liệt kê từng lệnh: ngày giờ VN (giờ vào), TP/SL, R.

## Telegram
- Tin mở = `sendPhoto` (ảnh + caption), tin đóng = `sendMessage`:
```
🟢 BUY · A Phá hồi v5 · GCZ26 · 20:24 VN
Lý do: <Reason>
Vào 4193,1 · SL 4190,6 (2,5 giá) · TP 4200,6 (3R)

✅ A Phá hồi v5 +2,8R · 20:24→20:51        (R đã trừ chi phí 0,2)
🛑 A Phá hồi v5 −1,1R · 20:24→20:31
```
- Chống trùng: lần quét đầu sau reload chỉ nạp id; chỉ bắn khi tín hiệu ở **nến vừa đóng** và tuổi ≤ 90 giây; khoá file nguyên tử
  `%LOCALAPPDATA%\BenzoTrader\sent\` để nhiều chart cùng symbol chỉ gửi 1 lần mỗi id.
- Ảnh (`WinShot`) chỉ chụp **vùng chart** (nến + volume + delta, như ảnh mẫu), không chụp cả cửa sổ Optimus Flow. Thứ tự thử:
  (1) handle cửa sổ chart lấy từ DC lúc vẽ (`WindowFromDC` trong `OnPaintChart`) → `GetWindowRect`;
  (2) không có thì duyệt cửa sổ con của cửa sổ chính, chọn cái nhỏ nhất vẫn ≥ kích thước vùng chart (`BenzoCore.PickChartRect`, có test);
  (3) không được nữa ⇒ cả cửa sổ chính ⇒ toàn màn hình chính ⇒ gửi text không ảnh. Mỗi lần chụp ghi cách chụp vào `tele_log.txt`.
  Trước khi chụp: vẽ lại chart + chờ 1,2 giây để hộp SL/TP của lệnh mới đã hiện. Rộng > 1600px thì thu nhỏ. Chụp + gửi chạy `Task.Run`, gửi tối đa 10 giây.
  **Giới hạn:** chụp từ màn hình thật nên cửa sổ Optimus Flow phải đang **hiện, không thu nhỏ, không bị cửa sổ khác che**.
- Log `%LOCALAPPDATA%\BenzoTrader\tele_log.txt` (token được che bằng `***`). Lỗi code ghi `error_log.txt`.

## CSV log
`%LOCALAPPDATA%\BenzoTrader\signals_<symbol>_<LogicVersion>.csv` (nay `signals_<symbol>_port-5-A-v5.csv`; file `signals_<symbol>.csv` cũ là của logic trước, để nguyên) — header:
`time_utc,setup,side,entry,sl,tp,zone,reason,outcome,exit_time,r`. Ghi khi mở, cập nhật dòng đó khi đóng (khoá = time_utc+setup+side;
dòng cũ không còn trong bộ nhớ vẫn được giữ). `side` = BUY/SELL, `outcome` = OPEN/TP/SL, `exit_time`/`r` rỗng khi còn mở.

## A v5 — khác biệt giữa live và Python, bảo trì
- **Chỉ nến đã đóng** (như Python). **Footprint lấy từ Volume Analysis của platform** có thể lệch file export vài tick/hợp đồng ⇒ HVN/VA/vùng S/R lệch ⇒ tín hiệu live có thể khác khi chạy lại trên file. Sau 1–2 tuần nên xuất footprint cùng khoảng bằng Footprint Export, chạy `ReplayA5`, so với `signals_<symbol>_port-5-A-v5.csv`.
- **Nạp ≥ 30 ngày lịch sử M1**: HVN tuần cần 3 tuần đã đóng; VCL cần lịch sử để dựng vùng ⇒ mũi tên/vùng ở những ngày đầu lịch sử không đáng tin. Thời gian nạp lần đầu (ước từ đo 90 ngày ≈ 4 giây trên Linux) — ghi lại số đo thật trên Windows.
- **Một lệnh mở chung cho cả 4 setup** (engine): lệnh B/C/D đang mở chặn A (trạng thái A vẫn chạy) ⇒ thống kê A trên bảng khác backtest (Python đo A đứng riêng). Tin USD ±15′ chặn A (Python không có).
- Nến M5 thiếu phút cuối đóng trễ 1 nến; phiên kết thúc giữa nến M5 thì C# bỏ nến M5 dở (Python vẫn xử lý) — hiếm. Sổ HVN chỉ cộng theo **mức giá** (nến không có mức giá thì không cộng gì, như Python; live có Volume Analysis nên không xảy ra).
- Không có luật chỗ nối hợp đồng (splice): đổi hợp đồng (GCZ26 → GCG27) phải đổi chart, **không dùng mã nối liên tục**. Đổi mã/khung thì gỡ rồi thêm lại indicator.
- **Đổi `LogicVersion` xoá niêm phong của cả B/C/D** (lịch sử B/C/D dò lại theo dữ liệu hiện có, có thể khác bản niêm phong cũ).
- **Quy tắc bảo trì:** Benzo đóng băng `VclCore.cs` vào lúc build. Sửa `vung-canh-lenh/VclCore.cs` ⇒ chạy lại `vung-canh-lenh/research/parity_vcl.py` + `research/parity_a_v5.py`, build lại Benzo, tăng `LogicVersion`.
- Nếu Optimus Flow báo lỗi nạp DLL vì trùng tên kiểu `VungCanhLenhNs.VclCore` với DLL Vùng Canh Lệnh chạy cùng lúc: trong `build.sh`, sau khi nối, chạy `sed -i 's/\bVungCanhLenhNs\b/BenzoVclNs/g'` trên file nối tạm (đổi cả namespace lẫn bí danh).

## Lịch tin
`NewsCalendar` (Forex Factory, trong `ProfileEngine.cs`) tải nền, cache 1 giờ. Đã thêm `NewsCalendar.IsBlocked(utc, tz, minutes)`;
indicator expose `IsNewsBlocked(DateTime utc)` (±15′ tin USD mức cao) và đưa vào `SetupContext.IsNewsBlocked`.
Giới hạn: feed chỉ phủ **tuần hiện tại** ⇒ với nến lịch sử cũ hơn luôn trả `false`.

## Bốn setup (điều kiện CHỐT; mọi hằng nằm trong code, không có trong Settings)
Chung: chỉ nến M1 đã đóng, vào ở **giá đóng nến xác nhận (CF)**; CF theo chiều S = đóng theo chiều S, thân ≥ 50% biên độ, Δ cùng dấu,
|Δ| ≥ trung vị |Δ| 50 nến. **SL lai** = cấu trúc ∓ 0,3 giá, sàn = biên độ nến cao nhất 5 nến, **trần 4 giá ⇒ bỏ lệnh**.
Không phát tín hiệu trong ±15′ tin USD mức cao (`IsNewsBlocked`). Mỗi lần chỉ 1 lệnh mở; ưu tiên A > B > D > C.
**Luật chung "mở ảo" (Hệ thống 3.2, đo trên C: R TB −0,26 → −0,06, 85% SL trong khung này):** KHÔNG phát tín hiệu khi giờ VN theo mốc neo Mỹ nằm trong **19:20–20:30** (sm 860..929; sau 1/11 là 20:20–21:30 VN). Đặt MỘT chỗ trong `BenzoEngine.Advance` trước `TryDetect` (`BenzoCore.InVirtualOpen`); `Observe` vẫn chạy nên trạng thái detector liên tục. `LogicVersion = port-5-A-v5` (A thay bằng A v5; B có bộ vùng v2/v3; C có các lớp mới).
Giờ neo theo giờ Mỹ như `kernel.py` (mùa đông Mỹ thì mọi mốc 19:00/19:20/20:20 VN lùi +1 giờ).

- **A · Phá hồi v5 (TP 3R) — chạy thử, CHƯA CÓ LỢI THẾ ĐO ĐƯỢC.** (= A-v4 + các vùng hỗ trợ/kháng cự của Vùng Canh Lệnh; port `research/setup_a_v5.py::detect5`.)
  *Vùng canh* (mỗi vùng một trạng thái riêng cho mỗi chiều): **VWAP tuần, VWAP ngày** (cần ≥ 30 nến), **HVN tuần 1-3** (dải ≤ 2 giá), **HVN ngày 1-3**, **VAH/VAL hôm qua**, và mọi **vùng S/R đang hiển thị của Vùng Canh Lệnh**.
  *Cú phá:* một nến M5 đóng ngoài vùng ⇒ mở trạng thái; **đã trang bị** khi cực trị của cú phá cách cạnh ≥ 2 giá (cực trị tiếp tục lập mới thì cập nhật); **hết hạn 30 nến M1 tính từ cực trị CUỐI** (không phải từ nến phá);
  **huỷ** khi M5 đóng lại trong sâu > 1 giá, hoặc (vùng dải) M5 đóng ngoài mép đối diện. Vùng S/R phải có **"cú phá thật"**: trong chân cú phá phải có một nến M1 mà vùng đang hiển thị và giá đóng ở phía trong.
  *Vào lệnh:* hồi ≥ 3 nến từ cực trị, không nến hồi nào có biên độ ≥ nến đà lớn nhất, nến xác nhận (CF) gần vùng (≤ 1 giá hoặc râu chạm). **SL** = (mép xa của dải — HVN tuần và vùng S/R; các vùng khác dùng cạnh E) ∓ 1,0 rồi ∓ 0,3, **trần 4 giá ⇒ bỏ**; **TP 3R**.
  Tối đa **2 lệnh/(phiên, vùng, chiều)**; vùng S/R có thêm **khoá mức** (đã có 2 tín hiệu cùng phiên + chiều trong ±1 giá quanh E thì khoá). Không vào lệnh khi: 1–3 nến sau nến dài nhất phiên · phase OFF · tin USD ±15′ · khung "mở ảo" 19:20–20:30 VN.
  Bản cũ `DetectorA` (A V3: chỉ VA Âu/IB/hôm qua, hết hạn 30 nến từ nến phá) vẫn nằm trong mã để test hồi quy nhưng **không chạy live**.
  > **Số đo 90 ngày GCZ26 (61 phiên sạch):** A v5 **324 lệnh (5,3/ngày), WR 22,2%, R TB −0,18** [−0,36; +0,01]; TRAIN −0,07 (175 lệnh) / **TEST −0,32** (149 lệnh); cả **6 phép đối chứng "không hơn"** vào lệnh bừa; **không đạt tiêu chí T1** (trượt điều kiện R TEST ≥ −0,08).
  > Bản live (có chặn 19:20–20:30): 312 lệnh, WR 22,4%, R TB −0,18. A-v4 (không VCL): 218 lệnh, WR 19,7%, R TB −0,30.
  > **Số lệnh tăng nhưng mỗi lệnh vẫn lỗ trung bình ⇒ tổng lỗ tăng theo số lệnh.** Hoà vốn cần WR ≈ 27% ở 3R. **Bật để chạy thử và thu số thật — không phải khuyến nghị vào lệnh.** Chi tiết: `research/report/RESULTS-A-V5.md`, `RESULTS-A-V4.md`.
- **B · Hấp thụ (TP 3R).** Giá tới VWAP tuần hoặc VWAP ngày (VWAP đủ 30 nến) bằng move ≥ 3 giá (tìm cực trị trong 20 nến trước cụm);
  cụm 3 nến cuối đều chạm Z với thân và |Δ| của nến cuối cụm nhỏ hơn nến đầu cụm, cực trị cụm không vượt Z + 0,5; nến CF ngược chiều move với
  |Δ_CF| ≥ 50% |Δ| lớn nhất của move. SL = cực trị cụm 3 nến ∓ 0,3.
  Loại: chế độ TREND cùng chiều move · đang phá VA Âu/IB theo chiều move · nến dài nhất phiên nằm trong 3 nến cuối · tối đa 2 lệnh/(loại vùng, phiên).
  **Vùng B canh (thứ tự ƯU TIÊN khi trùng nến; một nến xác nhận = tối đa một lệnh, lệnh gắn vùng đứng trước):**
  VWAP tuần, VWAP ngày → *nhóm v2* → *nhóm S/R*. Chi tiết ở mục "B · thêm vùng" dưới đây.
- **C · Fade cạnh (TP 2R cố định).** Chế độ CÂN BẰNG (chưa có nến M5 đóng ngoài band; band = VA hôm qua trước 19:00 VN, sau đó VA Âu / IB, rộng ≥ 6 giá).
  Nến M1 có râu xuyên cạnh `E` ≥ 2 tick rồi đóng lại **trong** range, Δ nến ủng hộ chiều vào, râu ngược không dài hơn thân ⇒ vào. SL = râu xuyên ∓ 0,3.
  Loại: 18:00–19:20 VN · nến xuyên là nến dài nhất phiên · đã 2 lệnh ở cùng `E` trong phiên.
- **D · Trap (TP 2R).** Move ≥ 5 giá (zigzag 2 giá, không nhìn trước) trong ≤ 30 nến theo chiều S **cùng bias** (dấu close − VWAP tuần ở nến đầu mỗi phase),
  hồi ngược ≥ 1 giá và ≤ 70% move; nến cực trị của nhịp hồi có Δ thuận chiều hồi nhưng đóng ở nửa phía S (phe hồi thử và thất bại); CF theo S trong 3 nến sau,
  không phá cực trị hồi. **Không cần vùng Z** (bản V3). SL = cực trị nhịp hồi ∓ 0,3.
  Loại: chế độ CÂN BẰNG · 3 nến sau nến dài nhất phiên · phase OFF · ngược bias · (A/Âu) biên độ 60 nến < 2u (bộ lọc này gần như không loại ca nào).

### Kết quả backtest (CHỈ file 90 ngày GCZ26, 65 phiên; TRAIN ≤ 15/9, TEST từ 16/9; R đã trừ chi phí 0,2 giá)
| Setup | n | WR | R TB | TRAIN (n) | TEST (n) | Nhận định |
|---|---|---|---|---|---|---|
| A V3 (3R, cũ — không còn chạy live) | 20 | 10% | −0,68 | −1,08 (12) | −0,08 (8) | âm; khoảng tin cậy 95% [−1,09; −0,08] |
| **A v5 (3R, đang chạy)** | 324 | 22,2% | −0,18 | −0,07 (175) | −0,32 (149) | âm; 6 đối chứng đều không hơn; T1 trượt |
| B (3R) | 11 | 27% | 0,00 | +0,04 (7) | −0,07 (4) | n quá nhỏ, không khác ngẫu nhiên |
| C (2R) | 121 | 27% | −0,26 | −0,36 (63) | −0,14 (58) | âm cả hai nửa (hòa vốn WR ~36%) |
| D (2R) | 31 | 39% | +0,08 | +0,42 (16) | −0,29 (15) | TRAIN dương nhờ ít lệnh, TEST âm; đối chứng ngẫu nhiên −0,05 |

Cả 4 **chưa có lợi thế đo được** (QĐ-5). Dòng A V3 là bản cũ (chỉ để so); indicator nay chạy **A v5**. Công tắc vẫn BẬT mặc định để thu thống kê forward test; tắt setup nào là việc của người dùng khi nhìn số live.
Chi tiết: `research/report/RESULTS-{A,B,C,D}.md`. Tần suất (A v5 ~5,3 · B ~0,2 · C ~2 · D ~0,5 lệnh/ngày; A V3 cũ ~0,3) — xa mục tiêu 10–20 lệnh/ngày.

**Vòng A-v4 (2026-10-22, `plans/BENZO-A-V4-plan.md`, đứng riêng chỉ Python; nay là lõi của A v5):** đổi cạnh sang vùng trader chuyên nghiệp canh
(VWAP tuần/ngày, HVN tuần dải ≤ 2 giá, HVN ngày, VAH/VAL của phiên trước), cú phá phải có đà (cực trị cách cạnh ≥ 2 giá, hết hạn 30 nến tính
từ cực trị cuối, chỉ hủy khi M5 đóng lại trong sâu > 1 giá) và bỏ cấm 18:00–19:20. Kết quả trên 61 phiên: **218 lệnh (3,57/ngày), WR 19,7%,
R TB −0,30** [−0,50; −0,07]; TRAIN −0,11 (119) / **TEST −0,52** (99). Cả 3 đối chứng (vào ngẫu nhiên cùng trạng thái, vào ngẫu nhiên ở vùng,
dời bản đồ vùng 3–15 giá) đều ≈; vùng dời vẫn cho 3,2 lệnh/ngày, R −0,13. Không đạt tiêu chí port T1 (R TEST thấp hơn −0,08 của bản gốc)
⇒ A-v4 **chưa có lợi thế đo được** (A-v4 đứng riêng không được port; nó là một phần của A v5, xem mục A ở trên). Lưu ý đối chiếu chart: "VAH/VAL ngày" của A-v4 là VA của PHIÊN TRƯỚC;
đường VAH/VAL trên SessionZones là của phiên Âu đã đóng gần nhất (đó là "cạnh VA Âu" của bản A-v4+). Chi tiết: `research/report/RESULTS-A-V4.md`.

**Vòng C-v6 (2026-10-22, `research/PLAN-C-v2.md`, chỉ Python — KHÔNG port):** C + cổng hình dạng profile TPO hôm qua (ngày D: VA hôm qua;
ngày P/b: cạnh vùng dày) + VA nhỏ từ 3 lần đổi hành vi (climax → AR → ST). Gộp C4 trên 61 phiên: **191 lệnh (3,13/ngày, C cũ 1,69),
WR 12,6% (= C cũ), R TB −0,31** (C cũ −0,43) nhưng tổng R −58,8 (C cũ −44,7); TEST −0,15 kém C cũ −0,12 ⇒ không đạt T0/T1, mọi đối chứng ≈,
hoán vị nhãn cổng D p = 0,30 ⇒ **C vẫn tắt, chưa chứng minh**. Chi tiết: `research/report/RESULTS-C-V6.md`.

### B · thêm vùng (B v2 + B v3, port 2026-10-23)
Mọi vùng có cùng một cơ chế hấp thụ ở trên (move ≥ 3 giá tới vùng, cụm 3 nến chạm, thân/Δ giảm, CF ngược chiều…); chỉ khác danh sách vùng.
Nhãn vùng hiện trên chart, trong lý do và tin Telegram bằng tiếng Việt ngắn; cột `zone` của CSV giữ tên mã (VWAP_W, POC_D, VCL_S2…).

| Nhóm (công tắc, mặc định BẬT) | Vùng (nhãn → mã) | Chiều |
|---|---|---|
| (luôn có) | VWAP tuần → `VWAP_W` · VWAP ngày → `VWAP_D` | cả hai |
| **B · thêm vùng v2 (HVN/VA/POC)** | POC ngày `POC_D` · VAH ngày `VAH_D` · VAL ngày `VAL_D` (VA 70% phiên đầy đủ gần nhất đã đóng) · HVN ngày 1-3 `HVN_D1..3` · POC tuần `POC_W` · HVN tuần 1-3 `HVN_W1..3` | cả hai |
| **B · thêm vùng S/R (VCL, PDH/PDL)** | đỉnh phiên trước `PDH` · đáy phiên trước `PDL` · "VCL kháng cự (cạnh dưới)" `VCL_R1..7` · "VCL hỗ trợ (cạnh trên)" `VCL_S1..7` | PDH/PDL cả hai · R chỉ giá đi LÊN tới (sell) · S chỉ giá đi XUỐNG tới (buy) |

- **VCL = Vùng Canh Lệnh** (indicator riêng, `vung-canh-lenh/`): vùng S/R rộng 2-5 giá, tối đa 7 vùng hiển thị mỗi nến. B dùng **cạnh gần** của vùng: cạnh dưới của vùng phía trên (sell limit chờ giá lên) và cạnh trên của vùng phía dưới (buy limit chờ giá xuống). Khe VCL phải giữ cùng một vùng ≥ 4 nến liên tiếp mới tính (cạnh trôi theo vùng, giống VWAP trôi). Lõi VCL chạy trong cùng DLL (`VclCore.cs`); chỉ bật khi setup B bật nhóm S/R.
- **Trần 2 lệnh/(loại vùng, phiên):** loại = `VWAP_W`, `VWAP_D`, `POC_D`, `VAH_D`, `VAL_D`, `HVN_D`, `POC_W`, `HVN_W`, `PDHL` (PDH+PDL), `VCL` (14 cạnh chung một trần).
- Mức ngày/tuần chỉ lấy từ phiên/tuần **đã đóng** (không nhìn trước): HVN tuần = gộp tuần CME W−3..W−1; POC tuần = tuần W−1, cần ≥ 3 phiên đủ nến, không "mỏng" (volume < 20% trung vị).
- Công tắc B v2 tắt + S/R tắt ⇒ B cũ (chỉ 2 VWAP). Mỗi nhóm bật/tắt độc lập; thứ tự ưu tiên giữ nguyên (VWAP → v2 → PDH/PDL → VCL R → VCL S).

> ⚠ **Số đo 90 ngày GCZ26 (61 phiên sạch, ô θ 0,5 · N 3 · TP 3R, hòa vốn ≈ 27%):** B cũ 11 lệnh / WR 27,3% / R TB 0,00 · **B v2 25 lệnh / WR 32,0% / R TB +0,19** · **B v3 (v2 + S/R) 58 lệnh / WR 24,1% / R TB −0,12**
> — dưới hòa vốn; 33 lệnh chỉ có ở v3 thắng 18,2%; PDH/PDL gần như không sinh lệnh; **0/9 phép so khác đối chứng** (vị trí vùng S/R không mang thông tin, xác suất chạm chỉ phụ thuộc khoảng cách).
> Nhóm v2 cũng chỉ "tăng số lượng" (TRAIN −0,09 / TEST +0,45 ngược dấu, nằm trong dải đối chứng). **Cả hai nhóm đang BẬT theo yêu cầu người học để chạy forward test — không phải khuyến nghị vào lệnh.**
> Muốn B bớt lệnh nhiễu: **tắt "B · thêm vùng S/R" trước** (S/R là nhóm làm WR tụt dưới hòa vốn). Chi tiết: `research/report/RESULTS-B-v2.md`, `RESULTS-B-v3.md`, `plans/BENZO-B-v3-plan.md`.

## Cách đọc vùng A đang canh (A v5)
Khi bật "Hiện vùng A đang canh", chart vẽ **tối đa 3** trạng thái **đã trang bị** (cực trị cú phá cách vùng ≥ 2 giá) gần giá đóng nến cuối nhất, mỗi cái gồm:
- **dải vùng** (chỉ vùng có bề rộng): tím = vùng S/R của Vùng Canh Lệnh, cam = HVN tuần, từ nến phá tới mép phải;
- **đường đứt nét tại E** (xanh = đang chờ MUA, đỏ = đang chờ BÁN); VWAP trôi theo thời gian nên đường là giá trị hiện tại, nhãn có chữ "(động)";
- **vòng tròn rỗng** ở cực trị của cú phá;
- **1 nhãn ở mép phải**: `A chờ MUA · vùng S/R 4168,2–4170,4 · đáy/đỉnh … · <trạng thái> · còn N′`. Bốn trạng thái (theo thứ tự ưu tiên): (1) `hồi quá mạnh, chờ đỉnh/đáy mới` · (2) `đà vừa dừng, hồi k/3 nến` · (3) `chờ giá hồi về vùng` · (4) **`giá đang ở vùng, chờ nến xác nhận`** (chữ vàng đậm).
  Hậu tố ` · đang giờ không vào lệnh` (nến cuối đang bị chặn: 1–3 nến sau nến dài nhất phiên, phase OFF, tin USD, khung mở ảo) và ` · đang có lệnh mở`.
- **Trạng thái (4) là "đủ vị trí", KHÔNG phải tín hiệu.** Tín hiệu chỉ có khi nến đóng là nến xác nhận — mũi tên + hộp SL/TP như mọi setup.
Vùng/nhãn chỉ tính 1 lần mỗi nến đóng; lúc vẽ chỉ đổi toạ độ. Nhãn không nói gì về lợi thế của setup (xem khối trạng thái ở mục A).

## Cách đọc bảng trên chart
5 dòng: dòng tổng `BENZO · Tổng N lệnh · thắng · thua · WR% · ΣR` rồi 4 dòng A/B/C/D `n · thắng/thua · WR% · ΣR`; dòng A có thêm đuôi `· chưa có lợi thế đo được (chạy thử)`; setup đang tắt có đuôi `(tắt)`.
R đã trừ chi phí 0,2 giá/lệnh (TP = (lời − 0,2)/rủi ro, SL ≈ −1,1R). **Hòa vốn**: WR ≈ 27% ở 3R, ≈ 36% ở 2R. Mũi tên = nến vào; đường SL/TP vẽ theo tín hiệu.
Nhớ: n nhỏ (< 30 lệnh/setup) thì WR và ΣR chỉ là nhiễu.

## Parity C# ↔ Python
**Setup A v5** (`research/parity_a_v5.py` → `research/report/PARITY-A5.md`, toàn file 90 ngày gồm 4 phiên thưa, nến "xấu" của Python được đưa vào C# nên so được toàn file): tín hiệu raw **387/387** (A-v4: 245/245), lệnh sau luật "1 lệnh mở" không chặn mở ảo **324/324** (A-v4 218/218), có chặn mở ảo (bản live) **312/312** (A-v4 208/208), mức vùng từng phiên (HVN tuần/ngày, VAH/VAL) **65/65**, đều khớp từng trường (giờ, chiều, entry/SL/TP, vùng, kết cục, giờ thoát, R).
Nhật ký trạng thái kết thúc khớp **100% ngoài 4 phiên mỏng đầu file** (ở đó C# đóng nến M5 trễ 1 nến vì M1 thưa — giải thích trong báo cáo; không trạng thái nào có lệnh vào). Thời gian: ReplayA5 toàn file ≈ 4 giây (A-v5, Release).
`PARITY.md` cũ (A 18/18 …) là của **A V3** (class `DetectorA`); `ReplayCsv A` vẫn là V3, `ReplayA5` mới là bản live.
`research/parity_check.py` chạy `tools/ReplayCsv` (C#) và Python `setup_*.py` (ô chính) trên file 90d, mỗi setup độc lập (1 lệnh mở/setup), từ phiên 29/7
(4 phiên đầu file là "thin": Python loại, C# không biết). Kết quả (`research/report/PARITY.md`): **A 18/18 · B 10/10 · C 99/99 · D 31/31 khớp hoàn toàn** sau khi loại ở phía Python các lệnh rơi vào khung mở ảo (A −2, B −1, C −22, D −0 so với 20/11/121/31 trước luật)
(giờ, chiều, entry, SL, TP, kết quả TP/SL), không có lệch. **Parity nay lệch CÓ CHỦ ĐÍCH đúng số lệnh trong 19:20–20:30** (luật mở ảo chỉ có ở C#). Số tín hiệu trên toàn file 90d (gồm 4 phiên thin), trước → sau luật: A 20→18, B 13→12, C 123→101, D 33→32; hồi quy trong `tests/` (mục [11]) giữ số sau.
**Setup B cũ / v2 / v3** (`research/parity_b_v3.py` → `research/report/PARITY-B-v3.md`): mảng vùng từng nến (12 mức cố định + 7 khe VCL × lo/hi/runlen, 86.333 nến) **lệch 0 ô**; lệnh C# chạy thô (tắt luật mở ảo) = Python **11/11, 25/25, 58/58 khớp hoàn toàn** (giờ, chiều, entry, SL, TP, tên vùng); bản chạy thật (có luật mở ảo) = Python bỏ lệnh trong 19:20-20:30: **10/10, 24/24, 57/57**. Hồi quy trong `tests/` mục [11] giữ các số này.
Sai khác đã biết (không xảy ra trên dữ liệu thử): (1) nến M5 thiếu nến phút cuối được đóng muộn một nến; (2) D chọn nhịp hồi sớm nhất theo thời gian thực,
Python nhìn trước cả cửa sổ nên có thể chọn khác ở ca hiếm; (3) bộ lọc "splice/thin" của Python không có trong live; (4) bộ lọc tin USD là mới, không có trong Python.
**Setup C + các lớp mới** (`research/parity_check.py --c-layers` → `research/report/PARITY-C-LAYERS.md`), từ phiên 29/7, Python bỏ entry trong 19:20–20:30 trước khi mô phỏng: **C0 90/90 · C4 175/175 · C6 531/531 (TP chính) và C0 99/99 · C4 193/193 · C6 652/652 (2R cố định) khớp hoàn toàn** (giờ, chiều, entry, SL, TP, kết quả); số Python chưa loại luật mở ảo = 103 / 191 / 555 như đã báo. Máy vùng trên cả file (gồm 4 phiên thin): VA CHoCH 240 VA / 33686 nến = Python; hành lang S/R 1426 sinh / 981 chết TREND / 401 mất vùng = Python khi bỏ bộ lọc thin (Python thật: 1379 / 951 / 386). Hồi quy trong `tests/` mục [14].

## C · các lớp vùng mới (PLAN-C-v2 / PLAN-C-v3)
Setup C "Fade cạnh" cũ (C0): râu chọc qua cạnh VA hôm qua (Á/Âu) hoặc VA Âu/IB (Mỹ) ≥ 2 tick rồi đóng lại trong, Δ cùng chiều. Thêm 4 lớp nguồn vùng (mỗi lớp một công tắc, nhãn tiếng Việt trong Settings):
- **Cổng hình D** (`C · cổng hình D`): pha Á/Âu chỉ fade VA hôm qua khi profile TPO (bracket 30′) hôm qua có hình D (|bất đối xứng| ≤ 0,25, đóng trong VA, không hai vòm, không mỏng). Zone `VAH_Y_D`/`VAL_Y_D`.
- **Vùng dày P/b** (`C · vùng dày P/b`): ngày hình P hoặc b fade cạnh vùng dày T (hàng kề ≥ 50% TPO của POC). Zone `T_HI_P`/`T_LO_P`/`T_HI_B`/`T_LO_B`.
- **VA nhỏ CHoCH** (`C · VA nhỏ từ 3 lần đổi hành vi`): climax → AR → ST sinh VA [min(L1,L2), H1], nới tối đa 25% chiều cao, chết khi chế độ M5 trên band đó là TREND. Zone `CHOCH_DN_*`/`CHOCH_UP_*`.
- **Hành lang S/R** (`C · hành lang hỗ trợ/kháng cự`): khoảng giữa mặt dưới kháng cự gần nhất và mặt trên hỗ trợ gần nhất của bộ vùng VCL, đóng băng từ lúc sinh, rộng ≥ 6. Zone `SR_HI`/`SR_LO`. Bật lớp này sẽ chạy lõi VCL (dùng chung với B).
- `C · TP về cạnh đối diện / POC (≥ 2R)`: MẶC ĐỊNH TẮT (người học chốt 2026-10-23: fade cạnh chỉ TP 2R cố định); bật = TP về cạnh/POC (không đủ 2R ⇒ bỏ lệnh). **Tắt cả 4 lớp + tắt TP này = đúng C0 cũ** (101 tín hiệu trên 90 ngày).
Ghép lớp: cùng nến lớp nền và CHoCH cùng bắn ⇒ lấy cạnh gần giá đóng hơn (hoà ⇒ CHoCH); S/R chỉ thêm khi các lớp kia không bắn; 1 lệnh mở cùng lúc. Mỗi lớp có bộ đếm "≤ 2 lệnh/(phiên, cạnh)" riêng. Lý do của mỗi tín hiệu ghi rõ nguồn vùng.
Backtest 90 ngày (Python, 61 phiên sạch): C0 103 lệnh WR 12,6% R TB −0,43 · C4 (cổng D + P/b + CHoCH) 191 lệnh −0,31 · C6 (C4 + S/R) 555 lệnh (9,1/ngày) WR 21,3% R TB −0,09 — **vẫn âm, chưa có lợi thế đo được; không đạt S1 của PLAN-C-v3**; bật chỉ để thu thống kê live. Chưa kiểm ngoài mẫu.
Tổ hợp "không cổng D nhưng bật vùng dày P/b" chưa được đo ở Python (C# xử lý: ngày D/khác dùng VA hôm qua như C0, ngày P/b dùng vùng dày).

## Viết detector mới
1. Kế thừa `DetectorBase` (hoặc `IObservingDetector`): `Evaluate(ctx, i)` nhìn `ctx.Bars[0..i]` + `ctx.Zones` (đã cập nhật tới nến i), trả `Signal{Side,Entry,Sl,Tp,Reason,Zone}` hoặc `null`.
   `Observe` được gọi cho MỌI nến (kể cả khi đang có lệnh mở / setup tắt) nên trạng thái nội bộ luôn liên tục; `TryDetect` chỉ gọi khi rảnh lệnh và setup bật.
2. Thêm vào `BenzoTrader.CreateDetectors()` theo thứ tự ưu tiên (hiện A v5, B, D, C); thêm file vào `build.sh`, `tests.csproj`, `tools/ReplayCsv`, `tools/ReplayA5`.
3. Sửa logic ⇒ tăng `BenzoCore.LogicVersion` (hiện `port-5-A-v5`) để cache niêm phong cũ bị bỏ.

`SetupContext`: `Symbol, Tick, TzOffset, BarMinutes, Bars (ClosedBars), Signals, Zones, GetLevels(idx) → LevelVol{Price,Bid,Ask,Vol}`, `IsNewsBlocked(utc)`, `ToVn(utc)`.
`BarData`: `Idx, Time (giờ MỞ, UTC), O,H,L,C, Vol, BuyVol, SellVol, Delta`.
Chưa port: LVN, naked POC. HVN ngày/tuần, POC/VAH/VAL ngày, POC tuần, PDH/PDL đã port ở `BenzoSr.cs` cho setup B (định nghĩa B-v2: chỉ tuần trước, loại phiên mỏng); HVN tuần dải ≤ 2 giá / HVN ngày của A-v4 port riêng ở `BenzoSetupA5.cs` (gộp 3 tuần, không loại phiên mỏng — **khác định nghĩa của B**, nên A không dùng lại `BenzoSr`). VA/IB/VWAP tự tính trong `BenzoZones` (không gọi `ProfileEngine`)
để test được không cần SDK.
