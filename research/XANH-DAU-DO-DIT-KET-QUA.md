# "Xanh đầu đỏ đít" (CORVEN) — đo trên dữ liệu THEO MỨC GIÁ

**Nguồn:** `data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h.csv` (583 MB,
per-level bid/ask) + file `_bars.csv` cùng tên. **724.279 nến M1**, 2024-08-01 → 2026-08-19.

**Cách dịch hình sang số** (đọc được ngay khi nến đóng, không nhìn trước):
- band **30% TRÊN** của nến: `ask > bid` ⇒ *xanh đầu* (mua chủ động đẩy lên đỉnh nến)
- band **30% DƯỚI** của nến: `bid > ask` ⇒ *đỏ đít* (bán chủ động đẩy xuống đáy nến)

Hình này **không phụ thuộc chiều** — nó nói "hai đầu nến đều do lệnh CHỦ ĐỘNG tạo ra rồi bị hấp thụ"
⇒ dùng y nguyên cho cả hấp thụ bán (ở đáy) và hấp thụ mua (ở đỉnh).

**Thước đo:** rào chắn đối xứng ±2×(trung vị biên độ 50 nến) từ giá đóng nến sự kiện, 60 nến,
bên nào chạm trước. Nền chuẩn = **50%**. Tách đôi thời gian: ngưỡng lấy từ nửa đầu.

## 1. Vấn đề lớn nhất: hình này KHÔNG HIẾM — nó là mặc định của gần như mọi nến

| Hình | tần suất trên MỌI nến |
|---|---|
| **xanh đầu + đỏ đít** | **47,5%** |
| xanh cả hai đầu | 19,2% |
| đỏ cả hai đầu | 19,2% |
| đỏ đầu + xanh đít | 5,1% |
| bản "đúng cực trị" (ask>bid tại giá cao nhất, bid>ask tại giá thấp nhất) | **67,4%** |
| imbalance xếp tầng ≥2 ở cả hai đầu | 2,3% |

Bản "đúng cực trị" chiếm 67,4% vì nó gần như là **hằng đúng cơ học**: giá cao nhất của nến được tạo
bởi một lệnh mua khớp ask, giá thấp nhất bởi một lệnh bán khớp bid. Một dấu hiệu xuất hiện ở
một nửa số nến thì không thể mang thông tin phân biệt.

## 2. Kết quả — mọi kiểu sắp xếp màu (để không thể nói là "dịch sai hình")

Tập **mọi nến** (nhãn = giá chạm +2u trước −2u):

| Hình | nửa đầu | nửa sau |
|---|---|---|
| **xanh đầu + đỏ đít (CORVEN)** | 50,2% (n=5.104) | 50,3% (n=5.066) |
| đỏ đầu + xanh đít | 52,6% (n=546) | 47,8% (n=552) |
| xanh cả hai đầu | 50,7% | 49,8% |
| đỏ cả hai đầu | 50,5% | 49,6% |
| đúng cực trị | 50,4% (n=7.163) | 50,0% (n=7.265) |
| xếp tầng ≥2 hai đầu | 48,2% | 53,0% |

Tập **cụm khối lượng lớn + delta lệch hẳn** (nhãn = THUẬN chiều hấp thụ):

| Hình | nửa đầu | nửa sau |
|---|---|---|
| **xanh đầu + đỏ đít (CORVEN)** | 50,7% (n=2.876) | 51,8% (n=2.582) |
| đỏ đầu + xanh đít (hình NGƯỢC) | 51,2% | **52,6%** |
| xếp tầng ≥3 hai đầu | 40,0% (n=40) | 50,0% (n=100) |

⇒ **Hình ngược lại còn nhẹ nhàng hơn hình CORVEN.** Không có tách biệt nào.

## 3. Test mạnh nhất: chia ngũ phân vị theo ĐỘ MẠNH của hình

Điểm hình = (delta band trên / khối lượng band trên) − (delta band dưới / khối lượng band dưới).
Q1 = đỏ đầu xanh đít · Q5 = xanh đầu đỏ đít rõ nhất. Ngưỡng lấy từ nửa đầu.

| Tập | lệch Q5−Q1 nửa đầu | lệch Q5−Q1 nửa sau |
|---|---|---|
| tất cả cụm vol lớn (n=9.100 / 8.471) | **+0,1** | **+0,1** |
| chỉ combo B — hấp thụ đúng nghĩa (n=174 / 132) | −5,7 | +22,8 |
| chỉ tại VWAP ngày ±2 giá (n=2.060 / 904) | +10,0 | −3,7 |

Ô có n lớn cho **đúng 0**. Hai ô còn lại **đổi dấu** giữa hai nửa (mỗi ô chỉ ~35 ca) ⇒ nhiễu.

## 4. Cách đọc thứ hai — "nến DELTA có bóng dưới đỏ, thân xanh" — KHÔNG đo được từ export này

Kiểm trực tiếp cột trong `_bars.csv`: `max_delta == min_delta == delta` ở **724.260/724.279 nến
(99,997%)**. Tức export không lưu đường đi của delta trong nến ⇒ bóng nến delta là không thể phục hồi.
Muốn đo cách đọc này phải xuất thêm dữ liệu **tick/trade-by-trade**, hoặc để indicator ghi
max/min delta trong lúc chạy live.

## 5. Kết luận
1. Ở định nghĩa **theo mức giá**, "xanh đầu đỏ đít" **không phải tín hiệu** trên GC khung M1:
   50,2–51,8% ở mọi cách cắt, lệch ngũ phân vị **+0,1** trên mẫu 17.500 ca.
2. Lý do có thể giải thích được: hình này xuất hiện ở **47,5% mọi nến** (bản cực trị: 67,4%) —
   nó là hệ quả cơ học của việc giá chạm được hai đầu biên độ, không phải dấu vết của hấp thụ.
3. Điều này **không chứng minh CORVEN sai** — có thể ý anh ấy là cách đọc ở §4, mà export hiện tại
   không đo được. Nhưng ở cách đọc đo được thì kết quả là bằng không.
4. ⚠️ Theo luật trong CLAUDE.md: **không được code hình này thành signal**, và không được nói
   như thể đã kiểm định thuận lợi.

**Script:** `research/perlevel_extract.py` (quét 583 MB → `research/perlevel_feats.csv`),
`research/xanh-dau-do-dit.py`, `-2.py`, `-3.py`.
