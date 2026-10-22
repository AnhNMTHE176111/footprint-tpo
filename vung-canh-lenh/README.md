# Vùng Canh Lệnh — indicator Optimus Flow (Quantower)

Vẽ **bản đồ vùng hỗ trợ/kháng cự ổn định** trên chart vàng M1:
- 1 vùng đang chứa giá ("đang kiểm tra", cam);
- 2 vùng gần + 1 vùng xa vừa phải mỗi phía (đỏ = kháng cự, xanh = hỗ trợ).

Kèm **bảng tra** cho biết, theo lịch sử, giá cách vùng d (đơn vị u) thì bao nhiêu % chạm vùng trong 15/30/60/120 nến, và SL đặt ngoài biên xa bao nhiêu thì hay bị râu quét.

Thiết kế và số đo: `research/report/VCL-VONG-1..4.md`. Khớp C# ↔ Python: `research/report/PARITY-VCL.md` (100%).

## Cài đặt
1. Trên máy Linux: `bash vung-canh-lenh/build.sh` → ra `vung-canh-lenh/dist/VungCanhLenh.dll`. Cần `~/quantower-libs` và .NET ở `~/.dotnet`.
2. Copy DLL vào `C:\OptimusFLOW\Settings\Scripts\Indicators\VungCanhLenh\`. Nếu chạy build.sh trên máy Windows có Optimus Flow (Git Bash) thì script tự copy.
3. Mở chart **M1** có **Volume Analysis** (cần footprint từng mức giá để tính VA/POC hôm qua và VA Âu), rồi add indicator **"Vùng Canh Lệnh"**.
4. Cài đặt chỉ có:
   - lệch giờ VN (mặc định 7);
   - hiện bảng tra / hiện nhãn / hiện vùng xa;
   - 3 màu.

   Không có ngưỡng số nào để chỉnh.

## Đọc chart
- **u** = trung vị biên độ 50 nến M1 gần nhất (≈ 1,5–2,5 USD). Mọi khoảng cách tính bằng u.
- **Nhãn cạnh vùng**, ví dụ `B+B15+C · 68 · 2,3u · chạm 30′≈51% · quay ≥2u≈62%`, gồm:
  - loại mốc trong vùng: B = swing M5, B15 = swing M15, C = mốc phiên/POC trần, D = số tròn;
  - điểm của vùng;
  - khoảng cách từ giá tới cạnh gần;
  - % lịch sử giá chạm cạnh đó trong 30 nến;
  - % lịch sử đã chạm rồi quay lại ≥ 2u trong 30 nến.
- **Bảng góc trên-phải**:
  - dòng đầu: pha hiện tại (Á / Âu / Mỹ), u, và % bị râu quét quá biên xa ≥ 0,25 / 0,5 / 1,0u trong 10 nến sau khi giá đóng vào vùng (bảng đặt SL);
  - mỗi dòng sau là một vùng: vai · lo–hi · d (u và USD) · % chạm trong 15/30/60/120 nến.
- Bộ vùng chỉ đổi khi:
  - giá đóng ra ngoài "hành lang" (vượt cạnh xa của vùng gần nhất thêm 1u), hoặc
  - một vùng bị xuyên.

  Trung bình đổi ~3 lần/giờ, mỗi vùng sống ~1 giờ.

## Cảnh báo trung thực
1. **Vị trí vùng ≈ ngẫu nhiên.** Ba lần đo độc lập (65 phiên SR-KET-QUA, VCL vòng 1, vòng 2 có đối chứng khớp khoảng cách) đều cho thấy: vùng không bật, không hút giá, không cho TP tốt hơn một vùng giả cùng khoảng cách. Indicator chỉ để **tổ chức việc quan sát**, không phải tín hiệu vào lệnh.
2. **Bảng tra là tần suất lịch sử của 20 phiên GCZ26** (2026-08-17 → 09-14). TRAIN/TEST lệch nhau phần lớn ≤ 3–5 điểm, nhưng vẫn là mẫu nhỏ. Thị trường đổi tính thì số sẽ đổi.
3. **Pha Mỹ, cửa sổ 60/120 nến bị cắt cuối phiên** (chạm chỉ tính trong phiên), nên các ô đó thấp hơn thực tế.

## Cấu trúc
- `VclCore.cs` — lõi thuần (ứng viên, gộp, chọn bộ, bảng tra). Không dùng SDK, test được trên Linux.
- `VungCanhLenh.cs` — lớp dán Quantower: Settings, chỉ xử lý nến **đã đóng**, vẽ.
- `tests/` — `dotnet run --project vung-canh-lenh/tests` (32 kiểm tra).
- `tools/ReplayCsv` — chạy lõi C# trên file footprint export, để đối chiếu Python (`research/parity_vcl.py`).
- `research/` — Python các vòng 1–4. `vcl4.py` là bản chuẩn đã port.
