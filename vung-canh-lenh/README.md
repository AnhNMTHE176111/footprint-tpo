# Vùng Canh Lệnh — indicator cho Optimus Flow

Vẽ trên chart vàng M1 **vài vùng hỗ trợ/kháng cự ổn định** quanh giá, mỗi vùng rộng **2 đến 5 giá**:
- 1 vùng đang chứa giá (cam, "đang kiểm tra");
- 2 vùng gần + 1 vùng xa vừa phải mỗi phía (đỏ = kháng cự, xanh = hỗ trợ).

## 1. Cài đặt
1. Copy `dist/VungCanhLenh.dll` vào `C:\OptimusFLOW\Settings\Scripts\Indicators\VungCanhLenh\` (chưa có thì tạo thư mục).
2. Mở lại Optimus Flow, mở chart **GCZ26, khung M1**, bật **Volume Analysis**.
3. Add indicator **"Vùng Canh Lệnh"**. Cài đặt chỉ gồm: lệch giờ VN (để 7), hiện nhãn, hiện lịch sử riêng của vùng, hiện vùng xa, **hiện TẤT CẢ vùng trong lịch sử** (xem bên dưới), 3 màu.
   Không có ngưỡng số nào để chỉnh.
4. Nếu góc dưới-phải hiện **"⚠ Chưa có Volume Analysis…"**: vẫn vẽ nhưng thiếu VA/POC hôm qua, VA Âu, POC trần. Bật Volume Analysis; tính xong thì indicator tự dựng lại.

## 2. Đọc nhãn
Nhãn thật (phiên 2026-09-08, 20:35 VN, giá đóng 4442,0):

```
4,4 giá · 46 điểm · đảo chiều ≈55% · xuyên phá ≈30% · chưa rõ ≈12% · đang chạm (lần 2)
```

| Phần | Nghĩa |
|---|---|
| `4,4 giá` | độ rộng của vùng tính bằng giá (USD); biên trên/dưới nhìn trên chart |
| `46 điểm` | điểm xếp hạng của vùng (dùng để chọn vùng hiển thị) — **không phải độ mạnh** |
| `đảo chiều ≈55%` | trong lịch sử, bao nhiêu % **lần chạm** kết thúc bằng việc giá quay về phía cũ, cách biên ≥ 2 giá |
| `xuyên phá ≈30%` | bao nhiêu % lần chạm kết thúc bằng việc giá đi sang phía kia, cách biên xa ≥ 2 giá |
| `chưa rõ ≈12%` | lần chạm bị cắt ngang (hết phiên, hoặc vùng biến mất khỏi chart) khi giá còn neo ở vùng |
| `đang chạm (lần 2)` / `chưa chạm` / `đã chạm 3 lần (đảo 2 · xuyên 1)` | lịch sử THẬT của riêng vùng này kể từ khi nó hiện trên chart |

**Một lần chạm** = giá tới vùng (râu chạm biên là đủ), **neo lại** trong vùng hoặc cách biên ≤ 2 giá bao nhiêu nến cũng được, rồi **đi chỗ khác**:
5 nến liền đóng xa hơn 2 giá và không nến nào chạm lại vùng. Râu quét qua rồi quay lại, hay phá giả vài nến rồi về, vẫn là **cùng một lần chạm**.
Vì phải chờ 5 nến yên mới chốt, **nhãn cập nhật trễ 5 nến**.

> ⚠ **Cảnh báo trung thực:** % đảo chiều / xuyên phá là tần suất của ~61 phiên GCZ26 theo pha phiên và độ rộng vùng, **giống nhau cho mọi vùng cùng
> pha, cùng cỡ**. Vùng giả cùng cỡ đặt ngẫu nhiên cũng cho ≈ chừng ấy (xem [LAN-CHAM.md](research/report/LAN-CHAM.md)). Con số cao phần lớn do
> **hình học**: đảo chiều chỉ cần đi 2 giá, xuyên phá phải đi hết bề rộng vùng + 2 giá — nên vùng rộng trông "giữ" tốt hơn vùng hẹp mà không mạnh hơn.
> Phần "đã chạm…" mới là chuyện thật của riêng vùng.

## 3. Dùng đúng cách
- **Vùng là MỐC để canh lệnh, đặt TP, đặt SL** — đỡ phải tự kẻ. Vùng 2–3 giá (phần lớn các vùng) cho phép SL đặt ngoài biên xa mà vẫn trong ~4 giá;
  vùng 4–5 giá thì SL ngoài biên xa sẽ vượt 4 giá — tự cân nhắc.
- **KHÔNG coi "giá tới vùng" là tín hiệu vào lệnh.** Quyết định vào vẫn phải dựa vào đọc order flow tại vùng (footprint, delta, hấp thụ…).
- Bộ vùng chỉ đổi khi giá ra khỏi hành lang hoặc một vùng bị xuyên: ~3 lần/giờ, mỗi vùng sống ~1 giờ.

## 4. Việc cần làm
Chạy indicator **10 phiên** trên Optimus Flow, chụp **3 ảnh** gửi lại (thấy rõ vùng, nhãn, giờ, giá). Mục đích: xem nhãn có đè nhau hoặc quá dài không,
và đếm bằng mắt vài lần chạm để đối chiếu với máy (đếm khác nhau = một bên hiểu sai định nghĩa "một lần chạm").

## 5. Bằng chứng
- [Lần chạm + độ rộng [2, 5] giá — backtest 61 phiên có đối chứng](research/report/LAN-CHAM.md) · ảnh minh hoạ:
  [phiên 2026-09-08](research/report/img/lan_cham_TRAIN_2026-09-08.png), [phiên 2026-10-14](research/report/img/lan_cham_TEST_2026-10-14.png)
- [Parity C# ↔ Python (khớp 100%)](research/report/PARITY-VCL.md)
- Các vòng trước: [1](research/report/VCL-VONG-1.md) · [2](research/report/VCL-VONG-2.md) · [3](research/report/VCL-VONG-3.md) · [4](research/report/VCL-VONG-4.md)
  · [bản đồ 15 ngày](research/report/MAP15.md) · [quay lại vùng](research/report/QUAY-LAI.md)

## Cho người sửa code
- `VclCore.cs`: lõi thuần (ứng viên, gộp + kẹp [2, 5] giá, chọn bộ, máy "lần chạm" `EpisodeTracker`, vùng lịch sử `LichSuTracker`, bảng `VclTables.Episode`, `VclFeeder`).
- `VungCanhLenh.cs`: lớp dán Quantower (đọc nến + footprint, vẽ vùng + nhãn).
- `build.sh`: build, 0 cảnh báo. `tests/`: `dotnet run --project vung-canh-lenh/tests`.
- `research/vcl5.py` + `lan_cham.py` (backtest), `test_lan_cham.py`, `parity_vcl.py` (tự build + chạy `tools/ReplayCsv`).
- `research/lich_su.py`: port Python của vùng lịch sử (`LichSuTracker`) + parity từng dòng với `_lichsu.csv` của C# + đo tiêu chí; `ve_lich_su.py`: vẽ 2 phiên mẫu.

## Chế độ "Hiện TẤT CẢ vùng trong lịch sử"
Bật tuỳ chọn này để xem lại các vùng từng hiện trên chart (dùng khi review signal Benzo Trader: tại nến signal có những kháng cự/hỗ trợ nào).
Đây là **công cụ quan sát**: không có vùng "mạnh/yếu", không lọc gì theo độ mạnh (đã đo: vị trí vùng không có lợi thế dự báo).

- **Một khối = một dải giá cố định** lấy từ lần đầu vùng hiện ra. Vùng hiện lại ở gần như cùng dải (chồng ≥ 50% dải hẹp hơn) được coi là cùng khối,
  dù engine đổi mã vùng hay biên vùng rung vài xu. Vùng mới chồng một phần (< 50%) lên khối đang sống thì **không** tạo khối mới — nên các khối không bao giờ đè nhau.
- **Màu = vai, một vai suốt đời:** đỏ = kháng cự (lúc tạo giá đóng dưới vùng), xanh = hỗ trợ (giá đóng trên vùng). Tạo khi giá đang nằm trong vùng ⇒
  xám vài phút, rồi chốt màu ở nến đầu tiên đóng ra ngoài (≈6% khối; màu này "biết trước" vài phút — chỉ ở màu).
- **Khối kết thúc khi:** (a) **xuyên phá** — một lần chạm kết thúc bằng 5 nến liền đóng xa hơn 2 giá ở phía sau lưng vai (kháng cự bị vượt lên,
  hỗ trợ bị thủng xuống); khối dừng ở nến cuối còn neo, nên khi chốt **khối co lại 5 nến** (giống nhãn trễ 5 nến); dải đó với vai mới là một khối mới;
  (b) **hết hạn** — vùng không còn hiện trên chart quá 60 phút; khối dừng ở lần hiện cuối. Khối còn hiện ở nến mới nhất kéo tới mép phải.
- **Tiêu điểm theo chuột:** rê chuột tới một nến (vd nến signal) ⇒ các khối còn hiệu lực tại nến đó vẽ **đậm + nhãn thấp–cao**, các khối khác mờ, không nhãn;
  một đường dọc mảnh đánh dấu nến đang soi. Chuột ra ngoài chart ⇒ tiêu điểm là nến ở mép phải. Trên dữ liệu 90 ngày, tại 163 nến signal Benzo có
  trung bình **6,7 khối đậm** (p90: 8).
- Khối sống < 15 phút không có nhãn. Nhãn đầy đủ của vùng hiện tại (độ rộng, điểm, % lần chạm…) vẫn ở mép phải như chế độ gọn.
- Vùng hiện tại chồng một phần lên một khối đang sống (≈1% thời gian) vẽ bằng **viền đứt**, không tô, từ nến hiện tại tới mép phải, kèm nhãn của nó.
- **Giới hạn nói trước:** khoảng **60 khối/24 giờ là bình thường** (đo 90 ngày: TB 63 khối/phiên, p90 81). Giá vàng đi qua 30–50 giá mỗi ngày, mỗi dải có thể
  là kháng cự rồi hỗ trợ, nên không thể chỉ còn "vài khối" mà không bỏ bớt vùng thật — vì vậy mới có tiêu điểm theo chuột.
  Dải khối cố định: khi vùng hiện tại rộng hơn/hẹp hơn khối > 1 giá (≈19% lần khớp), nhãn mép phải nói độ rộng của vùng hiện tại, không phải của khối.
- Tắt tuỳ chọn ⇒ về chế độ gọn y như cũ. Số đo đầy đủ: [LICH-SU.md](research/report/LICH-SU.md).
