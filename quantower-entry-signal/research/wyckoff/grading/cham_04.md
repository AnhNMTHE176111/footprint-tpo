# Chấm bài #04 — Phân phối (DIST) · 2026-01-28 23:41 → 2026-01-29 17:05 (183 nến M1)

**Điểm: 5/10** — khung phase và tên range đúng, nhưng nhãn BCLX rơi vào nửa dưới range và LPSY[D] không phải nhịp retest. Sửa nhãn, giữ cấu trúc.

## Lỗi (nặng → nhẹ)

### 1. Nhãn BCLX nằm ở NỬA DƯỚI range, cách biên trên 100 giá — luật vi phạm: L3
- **Thuật toán gắn:** BCLX tại **23:23**, giá **5595.8** (VSA 6.53x). Biên chính trên = **5696.0**.
- **Đúng phải là:** nhãn "cao trào mua" phải nằm tại đỉnh 5696.0 (nến 23:41). 5595.8 nằm ở **26% chiều cao range** tính từ đáy — tức nhãn BCLX đang ngồi ở **nửa dưới** vùng phân phối.
- **Dấu hiệu quyết định trên chart:** chấm đỏ BCLX vẽ **bên trái vạch tím Phase A**, thấp hơn cả nhãn AR không bao nhiêu. Nhìn bằng mắt thì không ai hiểu được đó là biên trên.
- **Nghi phạm trong thuật toán:** cùng nhánh với bài #01/#03/#05 — nhãn climax được phép nhảy về cây VSA cao nhất **trước** nến mở range. Sửa #4 của v7 (kẹp theo nến mở range cố định) **không có tác dụng**: 4/6 bài trong lô nhãn vẫn nằm ngoài khung về phía trái.

### 2. Nến mở range VSA 1.13x — dưới ngưỡng climax của chính thuật toán — luật vi phạm: mục 3 spec
- **Thuật toán gắn:** nến 23:41, VSA **1.13x** (volume 3), biên độ 20.6 giá.
- **Đúng phải là:** ngưỡng mở range là VSA ≥ 2.2x. Nến này chỉ qua được vế biên độ. Cây thoả VSA thật (23:23, 6.53x) lại không phải cực trị.
- **Dấu hiệu quyết định:** giá nhảy từ 5595.8 (23:23) lên 5696.0 (23:41) trong 18 phút với tổng volume dưới 30 lot — đây là **khe giá phiên đêm**, không phải cao trào mua có người tham gia.
- **Nghi phạm:** như lỗi 1 — mức climax được dời sang cực trị bất kể nến đó có tính chất climax hay không.

### 3. LPSY[D] không phải nhịp retest biên — luật vi phạm: L10
- **Thuật toán gắn:** LPSY[D] tại **5417.0** (16:32), trong khi SOW ở 5410.0 và biên chính dưới ở **5560.0**.
- **Đúng phải là:** LPS[D]/LPSY[D] là nhịp **hồi về retest biên vừa phá nhưng giữ được ở ngoài**. 5417 cách biên chính dưới **143 giá** — nó chỉ là một pivot nhỏ 7 giá ngay cạnh đáy cú sụp, không test lại gì cả.
- **Dấu hiệu quyết định trên chart:** hai nhãn SOW và LPSY[D] dính sát nhau ở góc dưới, cách đường nét liền 5560 rất xa.
- **Nghi phạm:** LPS[D] đo bằng "swing pivot ngược hướng đầu tiên xác nhận 5 nến, ≥1.5× ATR" (v5 lỗi J). Trên một cú sụp mạnh, pivot đầu tiên luôn nằm ngay sát đáy. Cần thêm ràng buộc: nhịp hồi phải đi **về phía biên** một tỉ lệ tối thiểu (ví dụ ≥30% quãng từ cực trị phá tới biên chính).

### 4. Phase E chỉ 2 nến — luật vi phạm: L10
- **Thuật toán gắn:** E = 17:01 → 17:05 = 2 nến.
- **Đúng phải là:** Phase E là giai đoạn giá đi tìm vùng giá mới. Trên ảnh giá sau đó còn dao động 5400–5560 suốt phần còn lại; 2 nến là bị cắt ngay khi vừa chạm mốc "đi xa 2× chiều cao".
- **Nghi phạm:** giống bài #02 — mốc đóng E theo bội số chiều cao range bắn quá sớm khi cú phá đi rất mạnh (SOW đã đi 150 giá / chiều cao 136 giá ngay tại nến phá).

### 5. UT[B] gán trên nến VSA 0.19x — lỗi Effort vs Result (nhẹ)
- **Thuật toán gắn:** UT[B] 5700.0, **VSA 0.19x**, thân 0.00 — vượt biên chính đúng 4.0 giá (40 tick).
- **Đúng phải là:** một cú thăm dò biên trên trên nến 1 lot thì không nói lên điều gì về cung/cầu; ghi nhận biên phụ được, nhưng không nên treo nhãn sự kiện.
- Ghi nhận tích cực: 40 tick đã **vượt** ngưỡng mới 30 tick — không còn ca "phá vài tick" của v6.

### 6. Chỉ số er lại in "hiệu quả" — lỗi thang đo (xem bài #02 lỗi 4)
- effort=1.42x, result=17.42, er=0.08. Nhãn đã đổi theo dấu (vá đúng), nhưng thang đo khiến er không bao giờ ≥1.

## Đạt
- **Tỉ lệ phase đúng (L8, L9):** A=34 · **B=116 (dài nhất)** · **C=10 (ngắn nhất)** · D=22 · E=2. Đây là bài thứ hai trong lô làm đúng cả hai luật tỉ lệ.
- **ST[A] chấp nhận được (L2):** 5660.0 = **73.5% chiều cao**, nằm ở 1/3 nửa trên — theo THEORY §5 đó là "phe mua rất mạnh", hợp lệ cho một cấu trúc phân phối dốc lên. Chặt hơn hẳn ngưỡng cũ.
- **Tên range đúng (L4):** BCLX + phá xuống thật = Phân phối.
- **LPSY[C] đúng chỗ (L8):** 5663.2 nằm **trong range**, đúng **nửa trên**, ngay trước SOW — cách gán ngược hợp lý, đúng "có Phase D rồi mới xác định Phase C".
- **SOW là cây phá thật (mục 8):** VSA 3.67x, thân 1.00, đóng cửa vượt xa cả biên phụ 5560 → thoả L3.
- **Biên (L3):** biên chính cố định đúng climax+AR; đúng 1 biên phụ trên (5700.0) do UT[B] tạo, tỷ lệ 1.03x.
- **SOT phía dưới đo được n=4, cạn kiệt (0.77)** — đọc effort↔result đúng chiều cho một cấu trúc sắp phá xuống.
