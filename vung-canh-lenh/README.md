# Vùng Canh Lệnh — indicator cho Optimus Flow

Vẽ trên chart vàng M1 **vài vùng hỗ trợ/kháng cự ổn định** quanh giá:
- 1 vùng đang chứa giá (cam, "đang kiểm tra");
- 2 vùng gần + 1 vùng xa vừa phải mỗi phía (đỏ = kháng cự, xanh = hỗ trợ).

Kèm **bảng tra**: theo lịch sử, giá cách vùng bao xa thì bao nhiêu % chạm vùng, và đặt SL ngoài vùng bao xa thì hay bị râu quét.

## 1. Cài đặt
1. Copy file `dist/VungCanhLenh.dll` vào thư mục `C:\OptimusFLOW\Settings\Scripts\Indicators\VungCanhLenh\` (chưa có thì tạo thư mục).
2. Mở lại Optimus Flow, mở chart **GCZ26, khung M1**, bật **Volume Analysis** (để có footprint từng mức giá).
3. Add indicator **"Vùng Canh Lệnh"**. Cài đặt chỉ gồm:
   - lệch giờ VN (để 7);
   - hiện bảng tra / hiện nhãn / hiện vùng xa;
   - 3 màu.

   Không có ngưỡng số nào để chỉnh.
4. Nếu bảng ghi **"⚠ Chưa có Volume Analysis…"**: indicator vẫn vẽ nhưng chỉ có swing và số tròn, thiếu VA/POC hôm qua, VA Âu, POC trần. Bật Volume Analysis lên; khi footprint tính xong, indicator tự dựng lại từ đầu.

## 2. Đọc bảng (góc trên-phải)
Dòng đầu: `pha Mỹ · u = 2,50 · SL quét ≥0,25/0,5/1,0u: 60%/53%/38%`
- **pha**: Á (05:00–12:30 VN), Âu (12:30–19:00), Mỹ (19:00 → hết phiên).
- **u**: trung vị biên độ 50 nến M1 gần nhất, tính bằng USD. Mọi khoảng cách đo bằng u.
- **SL quét**: sau khi giá đóng VÀO một vùng, trong 10 nến có bao nhiêu % râu vượt biên xa của vùng thêm 0,25u / 0,5u / 1,0u. Ví dụ đặt SL cách biên xa 1u thì ~38% bị chạm trong 10 nến.

Một dòng thật (phiên 2026-09-08, 20:35 VN, giá đóng 4442,0):

```
kháng cự     4447,6 – 4455,2   2,3u · 5,7$    37%/50%/60%/68%
```

| Cột | Nghĩa |
|---|---|
| `kháng cự` | vai của vùng: nằm trên giá. "(xa)" = vùng xa vừa phải; "đang kiểm tra" = giá đang ở trong vùng |
| `4447,6 – 4455,2` | biên dưới – biên trên của vùng (USD) |
| `2,3u · 5,7$` | khoảng cách từ giá đóng tới cạnh gần của vùng: 2,3 lần u = 5,7 USD |
| `37%/50%/60%/68%` | theo lịch sử, giá chạm cạnh gần trong 15 / 30 / 60 / 120 nến tiếp theo |

Nhãn cạnh phải của chính vùng đó: `B+B15+C+D · 68 · 2,3u · chạm 30′≈50% · quay ≥2u≈62%`.
- **Loại mốc**: B = swing M5, B15 = swing M15, C = mốc phiên/POC trần, D = số tròn.
- **68** = điểm của vùng.
- **Quay ≥2u ≈ 62%**: trong các lần đã chạm, 62% sau đó quay ngược lại ít nhất 2u trong 30 nến.

## 3. Dùng đúng cách
- **Vùng là MỐC để đặt lệnh chờ, TP, SL**, để khỏi phải tự kẻ vùng. Đặt SL ra ngoài biên xa, xem bảng "SL quét" để biết đặt xa bao nhiêu thì đỡ bị quét oan.
- **Bảng tra là kỳ vọng theo KHOẢNG CÁCH**, không theo "độ mạnh" của vùng. Vùng nào ở cùng khoảng cách cũng cho số gần như nhau. Dùng để hỏi "TP ở vùng này có thực tế trong 30 phút không".
- **KHÔNG coi "giá tới vùng" là tín hiệu vào lệnh.** Quyết định vào lệnh vẫn phải dựa vào đọc order flow tại vùng (footprint, delta, hấp thụ…).
- Bộ vùng chỉ đổi khi giá đóng ra ngoài hành lang (quá vùng gần nhất thêm 1u) hoặc một vùng bị xuyên. Trung bình ~3 lần/giờ, mỗi vùng sống ~1 giờ.

## 4. Cảnh báo trung thực
1. **Vị trí vùng ≈ ngẫu nhiên.** Ba lần đo độc lập đều cho kết quả này: 65 phiên trong SR-KET-QUA, vòng 1, và vòng 2 có đối chứng khớp khoảng cách. Vùng không bật nhiều hơn, không hút giá, không cho TP tốt hơn một vùng giả đặt cùng khoảng cách.
2. **Bảng tra là tần suất lịch sử của 20 phiên GCZ26** (2026-08-17 → 09-14). TRAIN và TEST lệch nhau phần lớn ≤ 3–5 điểm, nhưng mẫu vẫn nhỏ; thị trường đổi tính thì số sẽ đổi.
3. **Pha Mỹ, cửa sổ 60/120 nến bị cắt cuối phiên** (chạm chỉ tính trong phiên), nên các ô đó thấp hơn thực tế.

## 5. Việc cần làm
Chạy indicator **10 phiên** trên Optimus Flow, rồi chụp **3 ảnh** gửi lại. Ảnh phải thấy rõ cả vùng tô màu, nhãn và bảng góc phải, đọc được giờ và giá. Mục đích là hiệu chỉnh cách vẽ: chữ có đè nhau không, màu có rõ không, bảng có che nến không.

## 6. Bằng chứng
- [Vòng 1 — thuật toán gốc + 5 phép đo](research/report/VCL-VONG-1.md)
- [Vòng 2 — thưa ứng viên, đối chứng khớp khoảng cách, phép đo "tới được"](research/report/VCL-VONG-2.md)
- [Vòng 3 — chốt thiết kế, bảng tra, đặc tả C#](research/report/VCL-VONG-3.md)
- [Vòng 4 — chống nhấp nháy + port C#](research/report/VCL-VONG-4.md)
- [Parity C# ↔ Python (khớp 100%)](research/report/PARITY-VCL.md)

## Cho người sửa code
- `VclCore.cs`: lõi thuần (ứng viên, gộp, chọn bộ, bảng tra, `VclFeeder` giữ lõi đồng bộ với lịch sử).
- `VungCanhLenh.cs`: lớp dán Quantower.
- `build.sh`: build, 0 cảnh báo.
- `tests/`: `dotnet run --project vung-canh-lenh/tests`.
- `tools/ReplayCsv` + `research/parity_vcl.py`: đối chiếu C# ↔ Python.
