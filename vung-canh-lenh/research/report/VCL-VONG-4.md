# Vùng Canh Lệnh — vòng 4 phần 1: chống nhấp nháy

Dữ liệu, ứng viên, gộp, bảng tra: y như vòng 3. Thêm đúng 3 luật vệ sinh: (a) giữ vùng gần cũ nếu còn trong 3 gần nhất; (b) hành lang nới 1u ra ngoài cạnh xa vùng gần-1; (c) vùng có ID mới chỉ vào bộ khi ứng viên mạnh nhất đã sống ≥ 10 nến (vùng chứa giá hiện ngay). Đây là chọn luật vệ sinh, không phải tìm lợi thế.
Thời gian chạy `vcl4.py`: 21 giây (engine v4 9s).

### Vệ sinh v3 → v4 (mục tiêu: đổi vùng ≤ 4/giờ, tuổi thọ trung vị ≥ 30 phút)

| Chỉ số | v3 TRAIN | v3 TEST | v4 TRAIN | v4 TEST |
|---|---|---|---|---|
| vùng hiển thị TB | 6.32 | 6.35 | 6.38 | 6.39 |
| rộng trung vị (u) | 1.00 | 1.25 | 1.00 | 1.28 |
| rộng trung vị (USD) | 2.20 | 2.30 | 2.25 | 2.35 |
| % nến đóng trong vùng hiển thị | 35.3 | 33.9 | 32.4 | 30.7 |
| vùng sống trong ±10u | 6.3 | 6.0 | 6.3 | 6.0 |
| đổi vùng / giờ | 6.0 | 5.2 | 3.2 | 3.0 |
| tuổi thọ trung vị vùng hiển thị (phút) | 20 | 30 | 58 | 63 |

Số lần tính lại bộ: v3 2116 → v4 1014.

### Bảng tra trên v4 và |Δ| so với v3 (điểm %)

#### 6 · P(chạm) — Mọi pha: v4 (|Δ| so v3)

| d (u) | ≤15 | ≤30 | ≤60 | ≤120 |
|---|---|---|---|---|
| ≤1 | 84 (1) | 90 (1) | 92 (0) | 94 (0) |
| 1–2 | 60 (1) | 71 (0) | 79 (1) | 83 (0) |
| 2–3 | 39 (0) | 53 (1) | 65 (0) | 73 (0) |
| 3–4 | 22 (1) | 38 (1) | 51 (1) | 62 (0) |
| 4–6 | 12 (0) | 23 (1) | 38 (1) | 51 (2) |
| 6–8 | 6 (0) | 13 (0) | 27 (0) | 42 (1) |
| 8–12 | 2 (0) | 6 (1) | 15 (1) | 29 (1) |

#### 6 · P(chạm) — Á: v4 (|Δ| so v3)

| d (u) | ≤15 | ≤30 | ≤60 | ≤120 |
|---|---|---|---|---|
| ≤1 | 84 (0) | 88 (1) | 92 (0) | 95 (0) |
| 1–2 | 60 (2) | 72 (1) | 81 (0) | 86 (0) |
| 2–3 | 45 (1) | 57 (1) | 70 (1) | 78 (1) |
| 3–4 | 29 (0) | 46 (0) | 59 (1) | 73 (1) |
| 4–6 | 16 (0) | 30 (1) | 46 (1) | 59 (3) |
| 6–8 | 7 (0) | 17 (0) | 34 (1) | 50 (1) |
| 8–12 | 2 (1) | 9 (1) | 19 (4) ⚠ | 36 (6) ⚠ |

#### 6 · P(chạm) — Âu: v4 (|Δ| so v3)

| d (u) | ≤15 | ≤30 | ≤60 | ≤120 |
|---|---|---|---|---|
| ≤1 | 88 (1) | 92 (0) | 93 (1) | 96 (0) |
| 1–2 | 62 (1) | 72 (0) | 79 (0) | 85 (0) |
| 2–3 | 37 (1) | 54 (0) | 65 (1) | 75 (1) |
| 3–4 | 21 (1) | 37 (1) | 52 (0) | 64 (2) |
| 4–6 | 10 (1) | 20 (2) | 37 (1) | 53 (2) |
| 6–8 | 5 (1) | 12 (1) | 27 (2) | 45 (2) |
| 8–12 | 1 (0) | 4 (1) | 14 (1) | 33 (1) |

#### 6 · P(chạm) — Mỹ: v4 (|Δ| so v3)

| d (u) | ≤15 | ≤30 | ≤60 | ≤120 |
|---|---|---|---|---|
| ≤1 | 83 (0) | 89 (0) | 92 (1) | 93 (0) |
| 1–2 | 58 (0) | 69 (0) | 76 (1) | 80 (0) |
| 2–3 | 37 (0) | 50 (1) | 60 (1) | 68 (0) |
| 3–4 | 19 (1) | 33 (1) | 45 (0) | 53 (0) |
| 4–6 | 10 (0) | 20 (0) | 33 (1) | 44 (0) |
| 6–8 | 5 (0) | 11 (0) | 22 (1) | 35 (1) |
| 8–12 | 1 (1) | 5 (0) | 11 (2) | 19 (3) |

#### 7 · P(bị quét) v4 (|Δ| so v3)

| Pha | ≥0,25u | ≥0,5u | ≥1,0u |
|---|---|---|---|
| Á | 64 (2) | 57 (2) | 46 (1) |
| Âu | 63 (1) | 56 (2) | 42 (3) |
| Mỹ | 60 (0) | 53 (0) | 38 (0) |

#### 9 · Chạm rồi quay lại ≥2u v4 (|Δ| so v3)

| d (u) | ≤1 | 1–2 | 2–3 | 3–4 | 4–6 | 6–8 | 8–12 |
|---|---|---|---|---|---|---|---|
| % | 60 (0) | 61 (1) | 62 (0) | 65 (2) | 64 (0) | 68 (0) | 70 (1) |

**Ô đổi > 3 điểm:** bảng 6 Á d 8–12 ≤60 nến: v3 23 → v4 19; bảng 6 Á d 8–12 ≤120 nến: v3 42 → v4 36

### Bảng tra v4 nhúng C# (gộp TRAIN+TEST, %; −1 = thiếu mẫu)

```csharp
static readonly int[,] REACH_PHASE0 = {
    { 84, 88, 92, 95 },
    { 60, 72, 81, 86 },
    { 45, 57, 70, 78 },
    { 29, 46, 59, 73 },
    { 16, 30, 46, 59 },
    { 7, 17, 34, 50 },
    { 2, 9, 19, 36 }
};
static readonly int[,] REACH_PHASE1 = {
    { 88, 92, 93, 96 },
    { 62, 72, 79, 85 },
    { 37, 54, 65, 75 },
    { 21, 37, 52, 64 },
    { 10, 20, 37, 53 },
    { 5, 12, 27, 45 },
    { 1, 4, 14, 33 }
};
static readonly int[,] REACH_PHASE2 = {
    { 83, 89, 92, 93 },
    { 58, 69, 76, 80 },
    { 37, 50, 60, 68 },
    { 19, 33, 45, 53 },
    { 10, 20, 33, 44 },
    { 5, 11, 22, 35 },
    { 1, 5, 11, 19 }
};
static readonly int[,] REACH_ALL = {
    { 84, 90, 92, 94 },
    { 60, 71, 79, 83 },
    { 39, 53, 65, 73 },
    { 22, 38, 51, 62 },
    { 12, 23, 38, 51 },
    { 6, 13, 27, 42 },
    { 2, 6, 15, 29 }
};
static readonly int[,] SWEEP = {
    { 64, 57, 46 },
    { 63, 56, 42 },
    { 60, 53, 38 }
};
static readonly int[] REVERT2U = { 60, 61, 62, 65, 64, 68, 70 };
```

<!-- NHAN-XET -->
## Nhận xét phần 1
- **Đạt cả hai mục tiêu vệ sinh:** đổi vùng 6,0/5,2 → **3,2/3,0 lần/giờ** (≤ 4), tuổi thọ trung vị 20/30 → **58/63 phút** (≥ 30). Bộ tính lại giảm một nửa (2116 → 1014). % nến trong vùng hiển thị 32/31%, số vùng hiển thị 6,4 — gần như không đổi.
- **Bảng tra gần như không đổi:** 110 ô (bảng 6, 7, 9) có |Δ| ≤ 3, trừ 2 ô bảng 6 pha Á, d 8–12u: ≤60 nến 23 → 19, ≤120 nến 42 → 36. Đó là ô xa, ít mẫu, và đã nhạy giữa TRAIN/TEST ở v3 (|Δ| 7). Lý do có thể: luật (c) bỏ bớt vùng xa mới sinh nên tập mẫu đổi. **Bảng C# dùng số v4.**
- Không thêm luật nào ngoài (a), (b), (c).

## Phần 2 — port C# (Optimus Flow)
- **Code:**
  - `VclCore.cs`: lõi thuần, port 1-1 `vcl4.py`; bảng tra lấy từ v4.
  - `VungCanhLenh.cs`: lớp dán Quantower, tên hiển thị "Vùng Canh Lệnh".
  - `build.sh`: 0 cảnh báo; DLL ở `dist/VungCanhLenh.dll`.
- **Parity:** `research/report/PARITY-VCL.md` — **28 846/28 846 nến khớp tuyệt đối** (lo/hi lệch 0, mã vùng trùng, 1014 lần tính lại bộ ở cả hai bên).
- **Test C#:** `tests/` — 32 kiểm tra, 0 lỗi:
  - gộp / kẹp / tách khe;
  - chuyển vai & chết;
  - D không chết;
  - hành lang +1u;
  - KEEP khe gần;
  - tuổi tối thiểu;
  - bin bảng tra + pha;
  - không nhìn trước;
  - Value Area.
- **Chỗ tự quyết khi port:**
  - Bảng góc phải ghi tỉ lệ "SL bị quét" MỘT lần ở dòng đầu, vì bảng đó chỉ phụ thuộc pha, không phụ thuộc vùng. Mỗi dòng vùng ghi vai · lo–hi · d (u · USD) · chạm 15/30/60/120.
  - Vùng chứa giá ghi "giá đang trong vùng" thay cho xác suất chạm.
  - Chỉ vẽ bộ vùng HIỆN TẠI, từ lúc vùng vào bộ tới mép phải. Vùng đã rời bộ không vẽ lại.
  - Đổi "Lệch giờ" thì dựng lại lõi từ đầu.

## Vòng 5 (chốt) — sửa vận hành
- **Không còn chặn khi thiếu Volume Analysis.** Indicator vẫn chạy với footprint rỗng và ghi dòng "⚠ Chưa có Volume Analysis…" trong bảng. Khi footprint sẵn sàng (callback hoặc trạng thái Finished), `VclFeeder` dựng lại lõi TỪ ĐẦU có footprint, cờ `BuiltWithLevels`.
  - Test C#: trên dữ liệu giả lập, bộ vùng không có footprint khác bộ có footprint ở 1370/2900 nến. Sau khi dựng lại, bộ vùng giống hệt chạy thẳng có footprint.
- **Reset khi dữ liệu nạp lại khác:** giờ nến cuối không khớp nguồn, nến mới có giờ sớm hơn nến cuối, hoặc lịch sử ngắn đi. Mỗi trường hợp có test.
- **Kết quả:** build 0 cảnh báo · 40 kiểm tra C# xanh · parity vẫn 28 846/28 846 (100%, lệch 0).
