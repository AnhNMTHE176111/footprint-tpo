# BENZO-A-V5-port — Đưa setup A "Phá hồi v5" (A-v4 + vùng Vùng Canh Lệnh) vào indicator Benzo Trader để chạy thử trên màn hình

Opus viết 2026-10-23 (vai: thiết kế + đặc tả). **Sonnet implement + test, làm ĐÚNG CHỮ.** Chỗ nào đặc tả không nói ⇒ xem mục 9
("quyết định mặc định"); vẫn không có ⇒ **dừng và báo**, không tự chế luật. **Nguồn chân lý thuật toán = Python**:
`benzo-trader/research/setup_a_v5.py::detect5` (+ `setup_a_v4.py`, `zones_a_v4.py`, `zones_a_v5.py`, `kernel.py`). C# phải ra **đúng từng tín hiệu** như Python.

**Vì sao làm:** người học xác nhận (2026-10-23) "update indicator Benzo Trader để tôi xem setup entry trực tiếp trên màn hình". Plan v5 ghi
"port C# chỉ khi người học xác nhận" — đây là xác nhận. **Trung thực bắt buộc:** A-v5 KHÔNG đạt T1 (R TB TEST −0,32 < −0,08), cả 6 phép đối chứng
"không hơn" ⇒ mọi chỗ hiển thị/README phải nói **"chưa có lợi thế đo được — chạy thử (forward test)"**, không quảng bá, không viết "tốt hơn bản cũ".

Đọc trước: `plans/BENZO-A-V4-plan.md` mục 2 · `plans/BENZO-A-V5-plan.md` mục 2 · `research/report/RESULTS-A-V4.md` (Q1–Q11) + `RESULTS-A-V5.md` (V1–V13) ·
`research/setup_a_v5.py` dòng 94–498 (`detect5`) · `zones_a_v4.py` · `kernel.py` (`find_hvn`, `_Ctx.week_hvn`, `_zones`, `simulate`) ·
`BenzoCore.cs` · `BenzoZones.cs` · `BenzoDetectors.cs` (`DetectorBase`, `DetectorA` = V3) · `BenzoTrader.cs` · `tools/ReplayCsv/Program.cs` ·
`tests/Program.cs` · `vung-canh-lenh/VclCore.cs` (chỉ `VBar`, `VLevel`, `VZone`, `VclCore.Push/Display/Idx`) · `vung-canh-lenh/research/parity_vcl.py`.

**Thuật ngữ:** *VCL* = indicator Vùng Canh Lệnh · *bộ hiển thị* = các vùng VCL đang vẽ tại nến i (`VclCore.Display`) · *eid* = mã vùng VCL (`VZone.Id`) ·
*đã trang bị* (armed) = cực trị cú phá đã cách cạnh ≥ 2 giá · *parity* = khớp từng tín hiệu C# ↔ Python · *raw* = tín hiệu thô của detector, TRƯỚC luật
"1 lệnh mở" · *mở ảo* = khung cấm phát tín hiệu 19:20–20:30 VN của engine C# · *forward test* = chạy thử thời gian thực để thu số.

---

## 0. TÓM TẮT QUYẾT ĐỊNH

| # | Câu hỏi | Chốt |
|---|---|---|
| 1 | Đưa VCL vào Benzo thế nào? | **Nối nguồn (concat)** `../vung-canh-lenh/VclCore.cs` vào bản build Benzo (như đang làm với `ProfileEngine.cs`). **Benzo vẫn là 1 DLL độc lập** — người học chỉ copy 1 thư mục. KHÔNG tham chiếu `VungCanhLenh.dll`. KHÔNG sửa `VclCore.cs`. Namespace giữ `VungCanhLenhNs`, Benzo gọi qua bí danh `using VclNs = VungCanhLenhNs;`. |
| 2 | Code A mới đặt đâu? | **File MỚI** `benzo-trader/BenzoSetupA5.cs` chứa toàn bộ: toán HVN, sổ HVN theo phiên, nguồn VCL, `DetectorA5`, ảnh chụp "đang canh". Không sửa `BenzoZones.cs`, **không sửa `BenzoDetectors.cs`** (phiên B đang sửa). Chỉ đụng tối thiểu `BenzoCore.cs`, `BenzoTrader.cs`, `build.sh`, csproj, 2 dòng trong `tests/Program.cs`. |
| 3 | Dữ liệu từng mức giá cho VCL + HVN | Một lần đọc `PriceLevels` mỗi nến (memo 1 nến trong `BenzoTrader.ReadLevels`). Ba bộ cộng dồn profile (BenzoZones, VclCore, sổ HVN) giữ riêng — mỗi cái chỉ là cộng dictionary ~50 mức/nến; KHÔNG tái cấu trúc code đã parity. Đo: VclCore chạy 86 333 nến hết **3,9 giây** (45 µs/nến) trên máy Linux. |
| 4 | HVN lấy từ đâu? | **Port `kernel.find_hvn` + `zones_a_v4.peak_sharpness/clamp_band` + cách chọn phiên của `_Ctx.week_hvn`/`_zones`** vào file mới, chạy trên profile của chính Benzo. **Không** dùng `ProfileEngine.FindHvn`/SessionZones (cùng thuật toán nhưng profile, mốc phiên/tuần khác ⇒ không parity được với `zones_a_v4.py`). |
| 5 | A cũ (V3) | **Thay hẳn trên chart** (`CreateDetectors` dùng `DetectorA5`). **Không thêm công tắc v5/V3.** Giữ nguyên class `DetectorA` trong `BenzoDetectors.cs` (không dùng live; để test hồi quy [11] + parity V3 cũ còn chạy). Lý do ở mục 2.6. |
| 6 | Settings | Thêm **đúng 1 ô tick** `Hiện vùng A đang canh` (mặc định BẬT). Không ngưỡng số nào (QĐ-1). Đổi nhãn `Bật setup A · Phá hồi v5`. |
| 7 | Hiển thị live | Ngoài mũi tên + hộp SL/TP sẵn có: vẽ **≤ 3 trạng thái ĐÃ TRANG BỊ gần giá nhất**: đường/dải vùng E từ nến phá tới mép phải, chấm cực trị cú phá, **1 nhãn tiếng Việt** ở mép phải. Tính 1 lần mỗi nến đóng, lúc vẽ chỉ đổi toạ độ. Mục 4. |
| 8 | Phiên bản logic | `BenzoCore.LogicVersion = "port-3-A-v5"` (cache niêm phong cũ bị bỏ). CSV log tách file theo phiên bản logic. |
| 9 | Parity | 4 tầng, **mục tiêu 100 %** trên toàn file 90d (kể cả 4 phiên mỏng, nhờ đưa danh sách "nến xấu" của Python vào C#): mức vùng mỗi phiên · tín hiệu raw · nhật ký trạng thái · lệnh sau "1 lệnh mở" (**218 / 324** không chặn mở ảo; **208 / 312** có chặn — đúng bản live). Mục 5. |
| 10 | Trung thực | Bảng: dòng A có đuôi `· chưa có lợi thế đo được (chạy thử)`; README ghi số thật (324 lệnh, WR 22,2 %, R −0,18, TEST −0,32, đối chứng không hơn, T1 trượt). Telegram giữ nguyên mẫu, tên `A Phá hồi v5`. |

---

## 1. KIẾN TRÚC

### 1.1 Một DLL, nối nguồn

`benzo-trader/build.sh` nối theo thứ tự:
```
../quantower-tpo-suite/ProfileEngine.cs  ../vung-canh-lenh/VclCore.cs  BenzoCore.cs  BenzoZones.cs  BenzoDetectors.cs  BenzoSetupA5.cs  BenzoTrader.cs
```
- Mọi file đều đặt `using` BÊN TRONG namespace ⇒ nối hợp lệ (VclCore.cs đã đúng quy ước này).
- Thêm kiểm cảnh báo y như `vung-canh-lenh/build.sh`: `tee` log, `grep -qE "0 Warning\(s\)|0 cảnh báo"` ⇒ có cảnh báo thì **thoát lỗi**.
  Nếu bản build HIỆN TẠI (trước khi Sonnet sửa) đã có cảnh báo từ file không phải của mình ⇒ KHÔNG sửa file người khác; ghi danh sách cảnh báo vào báo cáo và
  chỉ yêu cầu "không thêm cảnh báo mới" (so số cảnh báo trước/sau).
- **Tại sao không tham chiếu VungCanhLenh.dll:** Quantower nạp mỗi thư mục indicator riêng; DLL tham chiếu chéo phụ thuộc thứ tự nạp và phiên bản,
  người học phải copy 2 thư mục và giữ khớp ⇒ rủi ro cao hơn. Nối nguồn = 1 file DLL, phiên bản VCL bị "đóng băng" vào lúc build.
- **Trùng tên kiểu giữa 2 DLL** (`VungCanhLenhNs.VclCore` có trong cả `VungCanhLenh.dll` lẫn `BenzoTrader.dll`): đã có tiền lệ `TpoSuite.*`
  (ProfileEngine.cs) nằm trong nhiều DLL indicator chạy cùng lúc mà không lỗi ⇒ giữ nguyên tên. **Phương án dự phòng** (chỉ làm nếu người học báo Optimus Flow
  lỗi nạp): trong `build.sh`, sau khi nối, chạy `sed -i 's/\bVungCanhLenhNs\b/BenzoVclNs/g'` trên file nối tạm (đổi cả namespace lẫn bí danh), test/ReplayCsv giữ tên gốc.
- `tests/tests.csproj`: thêm `<Compile Include="../../vung-canh-lenh/VclCore.cs" />`, `../BenzoSetupA5.cs`, `TestsA5.cs`.
  `tools/ReplayCsv/ReplayCsv.csproj`: thêm `../../../vung-canh-lenh/VclCore.cs`, `../../BenzoSetupA5.cs`.

### 1.2 Không sửa engine — DetectorA5 tự mang mọi trạng thái

`DetectorA5 : DetectorBase` (lớp nền có sẵn trong `BenzoDetectors.cs`, chỉ kế thừa, không sửa). Engine đã gọi `Observe(ctx, i)` cho **mọi** nến đã đóng
theo thứ tự (kể cả khi có lệnh mở / setup tắt / nến đã niêm phong) ⇒ đó là chỗ duy nhất DetectorA5 cập nhật: sổ HVN, VclCore, máy trạng thái.
`Evaluate(ctx, i)`:
- `z = ctx.Zones; if (z == null || z.Idx != i) return null;`
- **Bảo vệ tuần tự:** `if (i <= _lastIdx) return null;` (gọi lại cùng nến ⇒ không đẩy VCL 2 lần); `if (i != _lastIdx + 1) throw InvalidOperationException` (bỏ sót nến). `_lastIdx = i` ở cuối.
- `var lv = ctx.GetLevels(i)` — đọc mức giá của nến i (live: trúng memo 1 nến, mục 1.3).

### 1.3 Cấp dữ liệu footprint (tránh đọc trùng)

- `BenzoTrader.ReadLevels(idx)`: thêm **memo 1 nến** (`_lvMemoIdx`, `_lvMemo`; trả lại cùng danh sách nếu `idx == _lvMemoIdx`; xoá memo khi dựng lại engine).
  Engine gọi `GetLevels(i)` cho `Zones.Push`, ngay sau đó DetectorA5 gọi `ctx.GetLevels(i)` ⇒ trúng memo, platform chỉ bị đọc 1 lần/nến.
- Đổi kiểu cho VCL: `VclNs.VLevel(lv.Price, lv.Vol)` (cùng trường `Volume` mà `VungCanhLenh.cs` dùng). `VBar{Time=b.Time, O,H,L,C, Vol=b.Vol}`.
- Sổ HVN cộng `lv.Vol` vào hàng `Vcl.RowOf(price)` (= `rint(price/0,2)` làm tròn nửa về chẵn, như `kernel.build_profiles`). **Chỉ dùng mức giá**, nến không có mức giá
  thì không cộng gì (đúng Python; khác `BenzoZones.AddProfile` có rải đều — không đụng BenzoZones, ghi vào README mục khác biệt; live có Volume Analysis nên không xảy ra).
- Nến giả (ô lịch sử không phải nến — `PlaceholderBar`): đẩy vào VclCore như mọi nến (O=H=L=C, Vol 0, không mức giá) — giống `VclFeeder`.

### 1.4 Hiệu năng (mục tiêu đo, ghi vào `PARITY-A5.md`)

| việc | ngân sách | ghi chú |
|---|---|---|
| ReplayCsv A5 toàn file 90d (86 333 nến) | ≤ 30 giây | VclCore riêng 3,9 s |
| Live lần nạp đầu, 30 ngày lịch sử | ≤ 5 giây | chạy trong `Process()` dưới khoá như hiện tại |
| Live mỗi nến đóng | ≤ 1 ms trung bình | VclCore ~45 µs + máy trạng thái ≤ 40 trạng thái |
| Vẽ | không tính toán, ≤ 3 mục | ảnh chụp tính sẵn trong `BuildRender` |
Vượt ngân sách ⇒ báo số, không tự tối ưu bằng cách đổi logic. Được phép: bỏ cấp phát thừa, mảng thay danh sách.

---

## 2. PORT A-v4 / A-v5 — ĐẶC TẢ C# (đối chiếu từng dòng `detect5`)

### 2.1 Hằng số (đặt trong `static class A5Const`, chỉ trong code)
`Rr = 3.0` · `ZoneHalf = 1.0` · `NMin = 3` · `LegLookback = 60` · `DMin = 2.0` · `THoi = 30` · `CancelDepth = ZoneHalf` · `Warm = 30` ·
`HvnMax = 3` · `HvnGate = 2.5` · `HvnMinRatio = 1.5` · `HvnSmooth = 5` · `HvnBandFrac = 0.90` · `HvnBandMax = 2.0` · `WeekLookback = 3` · `MinBarsProf = 300` ·
hạng: `VWAP_W 1, VWAP_D 2, HVN_W 3, HVN_D 4, VAH_D 5, VAL_D 5, VCL 7`. Dùng lại `BenzoKernel.Tick/RowStep/WeekGapMinutes`, `BenzoRisk.Calc`, `BenzoKernel.IsConfirmBar`.

### 2.2 Toán HVN — `static class HvnMath` (port nguyên `kernel.py`)
- `RowPricePy(long row) = Math.Round(row * BenzoKernel.RowStep * 1e6, MidpointRounding.ToEven) / 1e6` (= `np.round(rows*0,2, 6)`, như `Vcl.RowPrice`).
- `FindHvn(long[] rowsAsc, double[] vol) → List<(double price, double ratio)>` = `kernel.find_hvn` với `tick 0,1, smooth 5, min_ratio 1,5`:
  n < 3 ⇒ rỗng; `avg = Σvol/n`; avg ≤ 0 ⇒ rỗng; `minSep = min(120, max(20, (p[n−1] − p[0]) / 0,1 × 0,08))`;
  làm mượt **bằng tổng tích luỹ** đúng như `_smooth` (`cs[0]=0; cs[k+1]=cs[k]+w[k]; sm[i]=(cs[z+1]−cs[a])/(z−a+1)`, `a=max(0,i−5)`, `z=min(n−1,i+5)`);
  đỉnh `i ∈ [1, n−2]` với `sm[i] ≥ sm[i−1] && sm[i] ≥ sm[i+1] && sm[i] ≥ 1,5·avg`; sắp **giảm dần theo sm, ổn định** (giữ thứ tự chỉ số khi bằng);
  tham lam: nhận đỉnh nếu `|p − p_đã_nhận| / 0,1 ≥ minSep` với mọi đỉnh đã nhận; trả `(p, sm/avg)`.
  (Volume là số nguyên hợp đồng ⇒ mọi tổng là chính xác, không lo lệch dấu phẩy động giữa numpy và C#.)
- Lọc như kernel: `FindHvn(...)` **lấy 3 phần tử đầu RỒI** giữ phần tử có `ratio ≥ 2,5` (thứ tự: cắt trước, lọc sau).
- `PeakSharpness(Dictionary<long,double> prof, double peak)` = `zones_a_v4.peak_sharpness`: `pr = (long)Math.Round(peak / 0,2, ToEven)`; không có ⇒ `(peak, peak)`;
  `thr = 0,9 × prof[pr]`; nới `lo−1`/`hi+1` khi hàng kề TỒN TẠI và `≥ thr`; trả `(Math.Round(lo×0,2, 6, ToEven), Math.Round(hi×0,2, 6, ToEven))`.
- `ClampBand(lo, hi, peak) = (max(lo, peak − 1,0), min(hi, peak + 1,0))`.

### 2.3 Sổ HVN theo phiên — `sealed class HvnBook`
Gọi `Step(i, bar, lv, z)` ở **đầu** mỗi `Evaluate` (trước mọi phần khác).
- Đếm tuần riêng: `week` tăng 1 khi khoảng trống giữa 2 nến > `BenzoKernel.WeekGapMinutes` (> 30 giờ), nến đầu = tuần 0 (= `kernel` `week_no`).
- Khi `z.NewSession` và không phải nến đầu: **chốt phiên vừa xong** `{Week (tuần của nến đầu phiên), N (số nến), Prof (long→double)}` vào danh sách phiên đã đóng,
  RỒI tính mức cho phiên mới (tuần `W` = tuần của nến i):
  - `q` = phiên đã đóng **gần nhất** có `N ≥ 300` và `Prof` không rỗng ⇒ `HvnD = [p for (p, r) in FindHvn(q)[:3] if r ≥ 2,5]` (giá điểm). Không có q ⇒ rỗng.
  - `HvnW`: gộp `Prof` của mọi phiên đã đóng có `W−3 ≤ Week ≤ W−1` và `N ≥ 300` và `Prof` không rỗng (cộng theo hàng); rỗng ⇒ không có HVN tuần;
    ngược lại `peaks = FindHvn(gộp)[:3]` lọc `≥ 2,5`; mỗi đỉnh `p`: `(lr, hr) = PeakSharpness(gộp, p)`; `(lo, hi) = ClampBand(lr, hr, p)` ⇒ `HvnW = [(p, lo, hi)]`.
  - Không xét chỗ nối hợp đồng (splice) — file GCZ26 không có; ghi README.
- Cộng mức giá của nến i vào profile phiên hiện tại (sau khi chốt), `N++`.
- Tỉa: bỏ phiên có `Week < W − 3`, NHƯNG luôn giữ phiên `q` hiện dùng cho HvnD.
- **VAH_D / VAL_D KHÔNG tính ở đây:** đọc `z.YdVah` / `z.YdVal` của BenzoZones (đã parity qua A V3 nguồn "Y" và setup C). Cùng quy tắc chọn phiên `q` (phiên trước ≥ 300 nến).

### 2.4 Tập vùng E tại nến k (k = i, hoặc nến M5 trễ, mục 2.5)

Thứ tự vùng v4 cố định (chỉ số `Order` 0..9, **đúng thứ tự `zones_a_v4.build_zones('new')`**): `VWAP_W, VWAP_D, HVN_W1, HVN_W2, HVN_W3, HVN_D1, HVN_D2, HVN_D3, VAH_D, VAL_D`.

| Name (khoá đếm, = Python) | lo/hi tại k (NaN = không có) | dyn | band | slFar | rank | "thô" cho chân cú phá |
|---|---|---|---|---|---|---|
| `VWAP_W` | `z.PosInWeekAt(k) ≥ 30 ? z.VwapWAt(k) : NaN` (điểm) | có | không | không | 1 | `z.VwapWAt(k)` (không áp Warm) |
| `VWAP_D` | `z.PosInSessionAt(k) ≥ 30 ? z.VwapDAt(k) : NaN` (điểm) | có | không | không | 2 | `z.VwapDAt(k)` |
| `HVN_W1..3` | `HvnW[j].lo / .hi` của phiên (NaN nếu ít hơn j+1 HVN) | không | **có** | **có** | 3 | = lo/hi |
| `HVN_D1..3` | `HvnD[j]` (điểm) | không | không | không | 4 | = giá |
| `VAH_D` / `VAL_D` | `z.YdVah` / `z.YdVal` (điểm, NaN khi chưa có) | không | không | không | 5 | = giá |
| `VCL_<eid>` | `Lo/Hi` của `VZone` có `Id = eid` trong bộ hiển thị tại k; NaN nếu eid không có mặt | **có** | **có** | **có** | 7 | = lo/hi (cùng giá trị) |

Lịch sử vùng VCL: `Dictionary<int eid, EidHist{int First; List<double> Lo, Hi}>`; sau `VclCore.Push(i)`, với mỗi `VZone` trong `Display`: nếu eid chưa có
hoặc `First + Count != i` (đứt quãng — Python cấm, không nên xảy ra) ⇒ tạo lại `First = i`; nối `Lo, Hi`. `VclAt(eid, k)` trả `(Lo, Hi)` nếu `First ≤ k < First+Count`, ngược lại NaN.
**Tỉa** eid không còn trong `Display` ở **CUỐI** `Evaluate(i)` nhưng giữ thêm 1 nến (xoá khi vắng ở cả i và i−1) — để sự kiện M5 trễ dùng được bộ của nến i−1.
"Bộ hiển thị tại k" = các eid có `VclAt(eid, k)` khác NaN.

`UseVcl = false` (chế độ A-v4 để parity) ⇒ không có VclCore, tập vùng chỉ có 10 vùng v4.

### 2.5 Máy trạng thái — y chữ `detect5` (logic `mom`, `ban=False`, `after_inside=False`, `real_break=True`, `vcl_slfar=True`, `lock=True`, `drop_overlap=False`)

Trạng thái `A5St { ZoneKey; int S, P0, PkPos, BrkNo, KPos, NEnt; double E, ZLo, ZHi, L, PkVal, Pbmax; bool Armed; }`; khoá trạng thái `(ZoneKey, S)`.
`ZoneKey` = (IsVcl, Order|Eid). Từ điển phiên: `count[(name, S)]`, `bcount[(name, S)]`, `sigLog[S] = List<double E>`; reset tất cả khi `z.NewSession`
(bản Python kết thúc trạng thái lý do `end` ở cuối phiên — C# ghi nhật ký `end` cho mọi trạng thái còn sống ngay trước khi xoá).
`need_in`/`reopen` của Python **không ảnh hưởng tín hiệu** khi `after_inside=False` ⇒ KHÔNG port (không cần cho parity).

**Thứ tự trong `Evaluate(i)`:**
0. `NewSession` ⇒ ghi `end` + xoá trạng thái/đếm. 1. `HvnBook.Step`. 2. Nguồn VCL `Push(i)` + cập nhật lịch sử eid. 3. **Sự kiện M5**: `foreach (var m in z.NewM5)` theo thứ tự,
xử lý ở chỉ số `k = m.LastIdx` (bình thường `k == i`; `k == i−1` khi nến M5 thiếu phút cuối được đóng trễ — mọi giá trị vùng lấy TẠI k, `C = m.C`).
4. Quét nến i. 5. Bước 3–4 (cập nhật đà, hết hạn). 6. Tỉa lịch sử eid. Trả tín hiệu (nếu có).

**Sự kiện M5 tại k** (Python dòng 282–366), duyệt vùng: 10 vùng v4 (theo Order) rồi các eid **có mặt tại k ∪ đang có trạng thái**, eid tăng dần:
```
(lo, hi) = giá trị tại k; NaN ⇒ pop cả 2 chiều (v4: lý do 'reset_value'; VCL: 'roi_bo'); continue
vùng v4 KHÔNG dyn: trạng thái có ZLo != lo || ZHi != hi ⇒ pop 'reset_value'      (trong phiên không xảy ra; vẫn cài)
out = C > hi ? +1 : C < lo ? −1 : 0
cho S ∈ {+1, −1} có trạng thái x:
    canh = dyn ? (S>0 ? hi : lo) : x.E
    deep = S·(C − canh) < −CancelDepth ;  opp = band && out == −S
    deep || opp ⇒ pop 'cancel'
out ≠ 0 và chưa có (z, out) và KHÔNG có (z, −out) ⇒ s = OpenState(z, out, k) ; s != null ⇒ thêm
```
**OpenState(z, out, k)** (Python 201–273): `canh = out>0 ? hi(k) : lo(k)`; `a = z.SessionStartIdx`; `lim = max(a, k − 60)`; `kk = k`;
- VCL: `while kk > lim`: nếu eid vắng tại kk ⇒ dừng; nếu `out>0 ? C[kk] > hi(kk) : C[kk] < lo(kk)` ⇒ `kk−−` ngược lại dừng.
  **Luật cú phá thật:** tại kk eid phải CÓ MẶT và `out>0 ? C[kk] ≤ hi(kk) : C[kk] ≥ lo(kk)`; sai ⇒ trả `null` (kể cả khi vòng dừng vì `kk == lim`, như V1).
- v4 dyn (VWAP): `while kk > lim && (out>0 ? C[kk] > thô(kk) : C[kk] < thô(kk))) kk−−`.
- v4 cố định: `while kk > lim && (out>0 ? C[kk] > canh : C[kk] < canh)) kk−−`.
- `f = kk < k ? kk+1 : k`; `L = max(H−L)` trên `[f..k]`; cực trị: `out>0` ⇒ nến có `H` lớn nhất (**lấy nến SỚM nhất khi bằng** — so sánh `>`), `PkVal = H`; `out<0` gương với `L`;
  `Pbmax = max(H−L)` trên `(PkPos..k]` (rỗng ⇒ 0).
- `E = canh; ZLo = lo(k); ZHi = hi(k); P0 = k; KPos = kk; Armed = out·(PkVal − canh) ≥ 2,0; bcount[(name,out)]++ ⇒ BrkNo; NEnt = 0`.

**Quét nến i** (Python 370–471): bỏ qua trạng thái có `P0 ≥ i`.
```
okbar = !ctx.IsNewsBlocked(giờ đóng nến i) && z.Phase != "OFF" && !(1 ≤ z.BarsSinceBig ≤ 3)
        && !(VirtualOpenBlock && BenzoCore.InVirtualOpen(z.Sm))
cho mỗi trạng thái x (P0 < i):
    E = (VCL || dyn) ? (S>0 ? hi(i) : lo(i)) : x.E          ; lưu Ecache[x] = E
    near = |C_i − E| ≤ 1,0  ||  L_i ≤ E ≤ H_i                (E NaN ⇒ false)
    !(okbar && near) ⇒ bỏ ;  !(x.Armed && i − x.PkPos ≤ 30) ⇒ bỏ
    npb = i − 1 − x.PkPos ;  npb < 3 || !(x.Pbmax < x.L) || !IsConfirmBar(bar_i, S, z.Mad) ⇒ bỏ
    count[(name,S)] ≥ 2 ⇒ bỏ
    far = slFar ? (S>0 ? lo(i) : hi(i)) : E ;  struct = S>0 ? min(L_i, far − 1,0) : max(H_i, far + 1,0)
    r = BenzoRisk.Calc(bars, i, S, struct, 3.0, ctx.Tick) ; null ⇒ bỏ
    VCL: nếu ≥ 2 giá trị E0 trong sigLog[S] có |E0 − E| ≤ 1,0 ⇒ bỏ ('khoá mức')
    ứng viên (|C_i − E|, rank, thứ tự) — thứ tự: v4 = Order (0..9); VCL = 10 + vị trí eid trong thứ tự eid tăng ⇒ so (rank, isVcl, Order|eid)
chọn ứng viên nhỏ nhất theo (khoảng cách, rank, thứ tự). Có ⇒
    ghi LastInfo (E, ZLo, ZHi, P0, PkPos, PkVal, L, Pbmax, npb, BrkNo, NEnt+1, dist = S·(PkVal − E)) TRƯỚC khi đặt lại
    tín hiệu: Side=S, Entry/Sl/Tp = r, Zone = name, Reason (mục 2.7)
    count[(name,S)]++ ; sigLog[S].Add(E) ; x.NEnt++ ; x.PkPos = i ; x.PkVal = S>0 ? H_i : L_i ; x.Pbmax = 0
```
**Bước 3–4** (Python 473–494) cho mọi trạng thái `P0 < i`, trừ trạng thái vừa được chọn:
```
ext = S>0 ? H_i : L_i
S·(ext − PkVal) > 0 ⇒ PkPos = i; PkVal = ext; Pbmax = 0; L = max(L, H_i − L_i);
                      E = Ecache nếu có, không thì tính như trên; !Armed && S·(PkVal − E) ≥ 2,0 ⇒ Armed = true   (E NaN ⇒ không trang bị)
ngược lại         ⇒ Pbmax = max(Pbmax, H_i − L_i)
i − PkPos > 30    ⇒ pop 'expire'
```
- **Tín hiệu bị luật "1 lệnh mở" bỏ vẫn tiêu đếm, khoá mức và đặt lại cực trị** (đúng Python: `detect5` ghi mọi tín hiệu raw, `simulate` mới lọc). Trong C# điều này
  tự đúng vì `Observe` chạy mọi nến và `Evaluate` cập nhật trạng thái bất kể engine có nhận tín hiệu hay không.
- Nến xấu / tin tức / mở ảo / giờ OFF ⇒ `okbar = false` ⇒ **không tiêu gì** (khác V3 cũ là kiểm tin ở cuối). Đây chính là `vblock=True` của Python.
- `VirtualOpenBlock` (thuộc tính, mặc định **true** = bản live). ReplayCsv đặt `false` khi so với Python `vblock=False`.
- Nhãn "trùng" của Python chỉ để mô tả ⇒ KHÔNG port.

### 2.6 Lớp C# và vì sao không có công tắc V3/v5
```csharp
public interface IA5VclSource { void Push(int i, BarData b, IReadOnlyList<LevelVol> lv); IReadOnlyList<(int Id, double Lo, double Hi)> Display { get; } }
public sealed class VclCoreSource : IA5VclSource   // bọc VclNs.VclCore; Push: kiểm VclCore.Idx == i sau khi đẩy
public sealed class DetectorA5 : DetectorBase       // Setup => 'A'
{
    public DetectorA5(bool useVcl = true, IA5VclSource vcl = null);   // null + useVcl ⇒ new VclCoreSource()
    public bool VirtualOpenBlock = true;
    public A5Info LastInfo;                            // thông tin tín hiệu vừa phát (cho ReplayCsv)
    public List<A5StateLog> StateLog;                  // null mặc định; ReplayCsv gán list để ghi trạng thái kết thúc
    public void FlushEnd();                            // ghi 'end' cho trạng thái còn sống (cuối dữ liệu)
    public List<A5Watch> Watch(int lastIdx, BarData lastBar, bool tradeOpen);   // mục 4
    public A5Levels CurrentLevels { get; }             // HvnW/HvnD/VAH/VAL của phiên hiện tại (cho ReplayCsv A5LEVELS)
}
```
`IA5VclSource` để test máy trạng thái bằng vùng giả (không phải dựng VclCore). **Không công tắc v5/V3 trong Settings**, vì: (1) người học chỉ muốn thấy A mới;
(2) V3 thua rõ trên cùng dữ liệu (20 lệnh, R −0,68) nên không có lý do giữ để chọn; (3) **nguy hiểm thật**: cache niêm phong khoá theo `LogicVersion`, một công tắc đổi
logic mà không đổi phiên bản sẽ trả tín hiệu cũ của logic kia cho nến đã niêm phong ⇒ thống kê lẫn lộn; (4) QĐ-1 tối giản Settings.
`CreateDetectors()` ⇒ `{ new DetectorA5(), new DetectorB(), new DetectorD(), new DetectorC() }` (giữ ưu tiên A > B > D > C; nếu phiên B đã đổi tên detector B thì giữ tên của họ).

### 2.7 Tên vùng tiếng Việt + lý do (Reason)
Tên: `VWAP_W` "VWAP tuần" · `VWAP_D` "VWAP ngày" · `HVN_Wj` "HVN tuần j" · `HVN_Dj` "HVN ngày j" · `VAH_D` "VAH hôm qua" · `VAL_D` "VAL hôm qua" · `VCL_e` "vùng S/R".
Giá vùng: điểm ⇒ `4170,4`; dải ⇒ `4168,2–4170,4`. Reason (mẫu cố định, số kiểu Việt `BenzoCore.Num`):
`phá {lên|xuống} {tên} {giá} (M5 đóng ngoài {HH:mm VN của nến P0 + 1 phút}), {đỉnh|đáy} cách vùng {dist} giá sau {PkPos−P0} nến, hồi {npb} nến, nến xác nhận Δ{±}`
(dùng `Hm`, `Dl` của DetectorBase). Không có chữ tiếng Anh ngoài VWAP/HVN/VAH/VAL/S/R/M5/Δ (đã dạy).

### 2.8 Sửa tối thiểu file dùng chung
- `BenzoCore.cs`: `LogicVersion = "port-3-A-v5"`; `SetupName('A') = "Phá hồi v5"`; thêm `public static string SetupNote(char s) => s == 'A' ? "chưa có lợi thế đo được (chạy thử)" : "";`
  và trong `TableLines` nối `" · " + SetupNote` vào dòng setup khi khác rỗng. Không đổi gì khác.
- `BenzoTrader.cs`: `CreateDetectors`; nhãn Settings A; ô tick mới (mục 4); `RenderState.Watch`; `BuildRender` lấy `_engine.Detectors.OfType<DetectorA5>().FirstOrDefault()?.Watch(...)`;
  vẽ (mục 4); memo `ReadLevels`; `Description` thêm "A Phá hồi v5 chạy thử — chưa có lợi thế đo được"; `_csvPath = signals_{sym}_{LogicVersion}.csv`
  (tránh trộn dòng A V3 cũ với A v5 trong cùng file — file cũ để nguyên); tin gửi thử ghi "A Phá hồi v5".
- `tests/Program.cs`: chỉ (1) sửa kỳ vọng caption test [4] thành `"🟢 BUY · A Phá hồi v5 · GCZ26 · 20:24 VN"`, (2) thêm 1 dòng trong `Main`: `var (o, f) = TestsA5.Run(); _ok += o; _fail += f;`.
  Toàn bộ test A5 nằm ở file mới `tests/TestsA5.cs` (bộ đếm + `Check` riêng).
- `tools/ReplayCsv/Program.cs`: thêm chế độ mới (mục 5); **giữ nguyên** hành vi `A|B|C|D|ALL` cũ (A = V3) để `parity_check.py` cũ không phải sửa.

---

## 3. BẤT BIẾN (phải giữ, kiểm trước mỗi commit)
1. `git diff` của `vung-canh-lenh/VclCore.cs`, `BenzoZones.cs`, `BenzoDetectors.cs`, mọi file `research/*.py` có sẵn = **rỗng** (chỉ thêm file mới `parity_a5.py`).
2. Test hồi quy [11] cũ vẫn ra đúng **A 18 · B 12 · C 101 · D 32** (DetectorA V3 và B/C/D không đổi một tín hiệu).
3. `parity_check.py` cũ chạy lại vẫn A 18/18 · B 10/10 · C 99/99 · D 31/31 (ReplayCsv `A` vẫn là V3).
4. Không thêm ngưỡng số nào vào Settings; Settings chỉ thêm 1 ô tick.

## 4. HIỂN THỊ LIVE — "setup đang thế nào" ngay trên chart

**Nguyên tắc:** chỉ hiện cái người học dùng được để canh lệnh; không vẽ lịch sử trạng thái; không bảng ghim mới; bảng 5 dòng thống kê giữ nguyên (chỉ thêm đuôi trung thực ở dòng A).

### 4.1 Cái gì được vẽ (chỉ khi `EnableA && ShowA5Watch`)
`DetectorA5.Watch(lastIdx, lastBar, tradeOpen)` trả tối đa **3** mục, mỗi mục là một trạng thái thoả CẢ: đã trang bị · cùng phiên với nến cuối · `count[(name,S)] < 2` ·
E tại nến cuối khác NaN · `lastIdx − PkPos ≤ 30`. Sắp theo `|C_cuối − E|` tăng, lấy 3 đầu.
Mỗi mục vẽ:
1. **Vùng E:** dải (HVN tuần, VCL) ⇒ hình chữ nhật `[ZLo, ZHi]` **tại nến cuối** từ x(nến P0) tới mép phải, tô mờ (alpha 40): VCL tím `(150,110,220)`, HVN tuần cam `(230,150,60)`;
   mọi vùng ⇒ thêm **đường đứt nét tại E** (giá trị TẠI NẾN CUỐI; với VWAP là giá trị hiện tại — VWAP trôi theo thời gian nên nhãn có chữ "(động)"), màu theo chiều: chờ MUA xanh `(38,190,120)`, chờ BÁN đỏ `(235,80,80)`, dày 1,4.
2. **Cực trị cú phá:** vòng tròn rỗng bán kính 4 px tại (x(nến PkPos), y(PkVal)), màu theo chiều.
3. **Nhãn 1 dòng ở mép phải**, căn phải, nằm ngang y(E); nền tối `(170,14,16,22)`, font Consolas 8 (như bảng); chữ xanh `(120,220,150)` / đỏ `(255,125,125)`;
   **trạng thái "giá đang ở vùng" ⇒ chữ vàng `(230,200,120)` đậm** (sắp đủ điều kiện). Nhãn chồng nhau (cách < 14 px) ⇒ đẩy nhãn sau xuống 14 px.

### 4.2 Mẫu nhãn (chuỗi cố định, test được — hàm thuần `A5Text.Label`)
`A chờ {MUA|BÁN} · {tên vùng} {giá}{ (động) nếu VWAP} · {đỉnh|đáy} {PkVal} · {trạng thái} · còn {30 − (last − PkPos)}′{hậu tố}`
Trạng thái (xét theo thứ tự, lấy cái đầu tiên đúng; `npb = last − PkPos` = số nến từ cực trị tới nến cuối):
1. `Pbmax ≥ L` ⇒ `hồi quá mạnh, chờ {đỉnh|đáy} mới` (bỏ phần "còn …′")
2. `npb < 3` ⇒ `đà vừa dừng, hồi {npb}/3 nến`
3. không `near` tại nến cuối ⇒ `chờ giá hồi về vùng`
4. `near` ⇒ `giá đang ở vùng, chờ nến xác nhận`
Hậu tố: `okbar` tại nến cuối sai ⇒ ` · đang giờ không vào lệnh`; `tradeOpen` ⇒ ` · đang có lệnh mở`.
Ví dụ: `A chờ MUA · VWAP ngày 4170,4 (động) · đỉnh 4175,2 · chờ giá hồi về vùng · còn 24′` ·
`A chờ BÁN · vùng S/R 4180,0–4182,6 · đáy 4176,1 · đà vừa dừng, hồi 2/3 nến · còn 28′`.
(Ghi chú cho Sonnet: trạng thái 4 là "đủ điều kiện vị trí", KHÔNG phải tín hiệu; tín hiệu chỉ khi nến đóng là nến xác nhận — mũi tên như cũ.)

### 4.3 Hiệu năng vẽ
`Watch(...)` gọi **một lần** trong `BuildRender()` (đã chạy dưới khoá `_calc` sau mỗi lượt nến mới), lưu bản sao bất biến vào `RenderState.Watch`.
`OnPaintChart` chỉ: đổi ≤ 3 × 4 toạ độ, vẽ ≤ 3 hình chữ nhật + 3 đường + 3 vòng + 3 nhãn. Không đọc detector, không cấp phát lớn. Cull: mục có y ngoài vùng vẽ thì bỏ.
Settings mới: `[InputParameter("Hiện vùng A đang canh", 51)] public bool ShowA5Watch { get; set; } = true;`

---

## 5. PARITY C# ↔ Python

### 5.0 Tiên quyết (dừng nếu sai)
1. `cd vung-canh-lenh/research && python3 parity_vcl.py` ⇒ bộ vùng **100 %** trên file 90d với `VclCore.cs` HIỆN TẠI (commit `c15d278` vừa sửa phần vùng lịch sử — phải chắc
   `Display` không đổi). Lệch ⇒ dừng, báo (không sửa VclCore).
2. `python3 -m pytest test_setup_a_v5.py -q` xanh (Python chuẩn còn đúng).

### 5.1 Dụng cụ
**`tools/ReplayCsv`** — chế độ mới (giữ cú pháp cũ): `ReplayCsv <base> A5 <outprefix> [--novcl] [--bad <file>]`
- `--novcl` ⇒ `DetectorA5(useVcl:false)` (= A-v4). `--bad <file>` ⇒ đọc danh sách giờ MỞ nến UTC "xấu" (Python `P.bad` = splice | thin) và đặt
  `IsNewsBlocked = t => bad.Contains(t − 1 phút)` ⇒ đúng `okbar` của Python ⇒ so được **toàn file**, không phải cắt từ 29/7 như parity cũ.
- Ghi 5 file:
  - `<out>_levels.csv`: mỗi phiên (giờ UTC nến đầu): `hvn_w` (p:lo:hi nối bằng `;`), `hvn_d` (`;`), `vah_d`, `val_d`.
  - `<out>_raw.csv`: chạy tay `Zones.Push` → `det.Observe` → `det.TryDetect` từng nến (KHÔNG engine, `VirtualOpenBlock=false`); mỗi tín hiệu:
    `time_utc,pos,side,entry,sl,tp,zone,E,p0,pk_pos,pk_val,L,pbmax,npb,brk_no,ent_no`.
  - `<out>_states.csv`: nhật ký trạng thái kết thúc `zone,S,p0,pk_pos,pk_val,E,why,armed,n_ent,brk_no` (cuối dữ liệu gọi `FlushEnd`).
  - `<out>_sim.csv`: mô phỏng "1 lệnh mở" trên tín hiệu raw bằng vòng lặp y hệt `BenzoEngine.Advance` (StepBar trước, rảnh mới nhận) nhưng KHÔNG luật mở ảo.
  - `<out>_live.csv`: `BenzoEngine` thật, chỉ `DetectorA5` (`VirtualOpenBlock=true`), cache null, `IsNewsBlocked` như trên.
  Cột sim/live: `time_utc,side,entry,sl,tp,zone,outcome,exit_utc,r`. In thời gian chạy.
**`benzo-trader/research/parity_a5.py`** (file MỚI; KHÔNG sửa `parity_check.py`): `P, V = setup_a_v5.load5()`; ghi `report/_a5_bad_bars.csv` (giờ mở UTC của nến `P.bad`);
build + chạy ReplayCsv 2 lần (VCL bật / `--novcl`); phía Python: `P.slev` + `P.zones('new')` (mức), `detect5(P, Z, V|None, vblock=False, states_log=…)` (raw + trạng thái),
`A4.sim(P, ents)` (sim), `detect5(..., vblock=True)` + `A4.sim` (live). So khớp và ghi `report/PARITY-A5.md`.

### 5.2 Tiêu chí chấp nhận — tất cả phải đạt trước khi build DLL ship
| tầng | so cái gì | khớp khi | mục tiêu |
|---|---|---|---|
| L0 mức vùng | mỗi phiên: HVN tuần (đỉnh, lo, hi), HVN ngày, VAH/VAL hôm qua | sai số ≤ 1e-9 | 100 % phiên |
| L1 raw | (giờ, chiều) + entry/SL/TP ≤ 1e-6 + zone + E ≤ 1e-6 + p0/pk_pos/npb/brk_no | mọi trường | 100 % (cả VCL bật lẫn tắt) |
| L2 trạng thái | mỗi trạng thái kết thúc: zone, S, p0, why, armed, n_ent, brk_no, pk_pos | mọi trường | 100 % |
| L3 sim (không chặn) | từng lệnh + outcome + giờ thoát | mọi trường | **A-v4 = 218, A-v5 = 324 lệnh đã đóng** (+ lệnh OPEN cuối file nếu có, cũng phải khớp) |
| L4 live (có chặn mở ảo) | như L3 | mọi trường | **A-v4 = 208, A-v5 = 312 lệnh đã đóng** (RESULTS-A-V5 bảng 5.3 cột "CÓ chặn") |
- **Lệch nào cũng phải giải thích từng ca** trong `PARITY-A5.md` (nến, giá trị hai bên, nguyên nhân). Chỉ 2 loại được chấp nhận mà không sửa:
  (a) bằng nhau dấu phẩy động ở mép vùng VCL (chênh ≤ 1e-9, in 2 giá trị); (b) nến M5 thiếu phút cuối nên C# đóng trễ 1 nến (in 2 nến M1 liên quan).
  Tổng (a)+(b) **≤ 2 ca** ở mỗi tầng; nhiều hơn ⇒ coi là lỗi C#, phải sửa. Loại khác ⇒ lỗi C#, sửa tới khi hết.
- **Python là chuẩn.** Nếu thấy lỗi phía Python: KHÔNG sửa Python (kết quả đã công bố dựa trên nó) — dừng, báo, ghi vào PARITY-A5.md.
- Ghi vào `tests/TestsA5.cs` mục hồi quy (mục 6 test 22) đúng các số L3/L4 + số raw (đọc `_a5_bad_bars.csv` đã commit; thiếu file 90d hoặc file nến xấu ⇒ bỏ qua có in).

### 5.3 Chỗ live khác Python (ghi README, không sửa được bằng parity)
1. **Chỉ nến đã đóng** (`Count−2`): giống Python (Python cũng chỉ dùng nến i đã đóng). Không khác.
2. **Footprint từ Volume Analysis của platform** có thể lệch file export vài tick/hợp đồng ⇒ VA/HVN/ứng viên C của VCL lệch ⇒ tín hiệu live có thể khác chạy lại trên file.
   Kiểm sau 1–2 tuần: xuất footprint cùng khoảng bằng Footprint Export, chạy `ReplayCsv A5`, so với `signals_<sym>_port-3-A-v5.csv` (kiểu GD10).
3. **Độ dài lịch sử nạp:** HVN tuần cần 3 tuần đã đóng; VCL cần lịch sử (POC trần 30 phiên) ⇒ vùng của những ngày đầu lịch sử trên chart không giống Python ⇒ mũi tên cũ
   ở đầu chart không đáng tin. Khuyên nạp **≥ 30 ngày** M1.
4. **Một lệnh mở chung cho cả 4 setup** (engine): lệnh B/C/D đang mở sẽ chặn A (trạng thái A vẫn chạy). Python đo A đứng riêng ⇒ thống kê A trên bảng sẽ khác backtest.
5. **Tin USD ±15′** chặn A (như `okbar=false`) — Python không có.
6. Nến M5 thiếu phút cuối đóng trễ 1 nến; phiên kết thúc giữa nến M5 thì C# bỏ nến M5 dở (Python vẫn xử lý) — hiếm (phiên GC kết thúc phút :59).
7. Không có luật chỗ nối hợp đồng (splice) — khi đổi hợp đồng (GCZ26 → GCG27) phải đổi chart, không dùng mã nối liên tục.

---

## 6. TEST C# (`tests/TestsA5.cs`, chạy cả Debug lẫn Release; dữ liệu giả dùng `IA5VclSource` giả + nến dựng tay)

1. `HvnMath.FindHvn`: 2 profile nhỏ cố định — kỳ vọng lấy bằng cách chạy `kernel.find_hvn` trong Python một lần và chép số vào test (ghi lệnh Python trong chú thích).
2. `PeakSharpness` + `ClampBand`: bậc thang đều ⇒ dải đúng; dải rộng 3 giá ⇒ kẹp còn 2 giá đối xứng đỉnh; đỉnh không có ⇒ (đỉnh, đỉnh).
3. `HvnBook`: 5 tuần giả ⇒ HVN tuần của tuần 4 chỉ dùng tuần 1–3; phiên < 300 nến bị loại; HVN ngày lấy phiên ≥ 300 nến gần nhất; tỉa vẫn giữ q.
4. VWAP: E lúc vào = `VwapDAt(i)` (động); phiên < 30 nến ⇒ không mở trạng thái VWAP_D; chân cú phá dùng VWAP thô.
5. Mở trạng thái VCL [100,102]: giá trong vùng rồi M5 đóng 102,5 ⇒ mở S=+1, E=102; cực trị 103,5 ⇒ chưa trang bị; lên 104,1 ⇒ trang bị.
6. Cú phá thật: vùng xuất hiện ngay trong chân cú phá ⇒ không mở; giá ở dưới vùng > 60 nến rồi M5 đóng dưới ⇒ VCL không mở, cùng tình huống với VAL_D (điểm) ⇒ mở.
7. Hủy: M5 đóng lại trong 0,5 giá ⇒ giữ; 1,5 giá ⇒ hủy; M5 đóng dưới `lo` ⇒ hủy +1 và mở −1 cùng nến.
8. Hết hạn: 31 nến sau cực trị không có nến xác nhận ⇒ mất trạng thái; M5 ngoài kế tiếp ⇒ mở lại, `BrkNo = 2`.
9. Đà đi tiếp 40 nến (cực trị liên tục mới) rồi hồi ⇒ vẫn vào được (không bị cắt hạn tính từ nến phá như V3); `L` cập nhật theo nến đà lớn nhất sau nến phá.
10. Điều kiện vào: hồi 2 nến ⇒ không; nến hồi có biên độ ≥ L ⇒ không; thiếu nến xác nhận ⇒ không; chạm bằng râu ⇒ được.
11. SL/TP: MUA ở E = hi, SL = làm tròn xuống của `min(L_cf, lo − 1) − 0,3`, TP = 3R; vùng rộng 4 giá ⇒ SL > 4 ⇒ không vào.
12. Rời bộ: eid vắng ở nến quét ⇒ không vào; vắng ở M5 kế ⇒ trạng thái kết thúc lý do `roi_bo`.
13. Cùng nến: VCL và VWAP_D cùng khoảng cách ⇒ VWAP_D được chọn; khác khoảng cách ⇒ gần hơn thắng.
14. Đếm ≤ 2 lệnh/(phiên, vùng, chiều); khoá mức: tín hiệu VCL thứ 3 cùng mức (|ΔE| ≤ 1) bị khoá, tín hiệu v4 thứ 3 vẫn vào; khoá đếm theo `VCL_<eid>`.
15. Sau khi vào: cực trị đặt lại ⇒ lệnh 2 cần nhịp hồi mới ≥ 3 nến.
16. Hết phiên: mọi trạng thái/đếm/khoá mức về 0; nhật ký ghi `end`.
17. Mở ảo: `VirtualOpenBlock=true`, nến xác nhận trong sm 860..929 ⇒ không tín hiệu và **không tiêu đếm**; nến xác nhận sau 20:30 ⇒ có tín hiệu. `false` ⇒ có tín hiệu trong khung.
18. Không nhìn trước: chạy tới nến k và chạy cả chuỗi ⇒ tín hiệu ≤ k giống hệt, `Watch(k)` giống hệt; không ném lỗi `ClosedBars`.
19. Nạp lại: engine 1 chạy hết với SignalCache file tạm; engine 2 mới cùng nến + cùng cache ⇒ danh sách tín hiệu (Id, entry, SL, TP) giống, `Watch` giống;
    `LogicVersion` khác ⇒ cache cũ bị bỏ.
20. Có lệnh mở (engine bận) ⇒ `Observe` vẫn tiêu đếm/khoá mức như Python raw (so với chạy không engine).
21. `A5Text.Label` + `Watch`: đủ 4 trạng thái + 2 hậu tố đúng chuỗi mẫu 4.2; trạng thái chưa trang bị / đã đủ 2 lệnh / khác phiên bị ẩn; tối đa 3, gần nhất trước.
22. Hồi quy file 90d (bỏ qua nếu thiếu file): raw, sim (218 / 324), live (208 / 312) đúng số đã chốt ở 5.2; in thời gian chạy.
23. `VclCoreSource`: `Display` trùng `VclCore.Display` (Id, Lo, Hi) sau mỗi `Push`; đẩy sai thứ tự ⇒ ném lỗi; `Evaluate` gọi 2 lần cùng nến ⇒ lần 2 trả null, VclCore không bị đẩy lại.
Tất cả test cũ (`[1]`–`[13]`) vẫn xanh (riêng [4] đã đổi chuỗi kỳ vọng). `dotnet run --project tests` và `-c Release` đều 0 FAIL.

---

## 7. README + NHÃN TRUNG THỰC

`benzo-trader/README.md` — sửa đúng các chỗ sau, giữ phần khác:
- Bảng cấu trúc file: thêm `BenzoSetupA5.cs` và dòng "`../vung-canh-lenh/VclCore.cs` được nối vào khi build (bộ vùng S/R)".
- Settings: thêm ô "Hiện vùng A đang canh".
- Mục "Bốn setup": thay đoạn A bằng **A · Phá hồi v5** (mô tả ngắn: vùng = VWAP tuần/ngày, HVN tuần dải ≤ 2 giá, HVN ngày, VAH/VAL hôm qua, vùng S/R của Vùng Canh Lệnh;
  cú phá M5 đóng ngoài, đã trang bị khi cực trị cách cạnh ≥ 2 giá, hết hạn 30 nến từ cực trị cuối, hủy khi M5 đóng lại trong sâu > 1 giá hoặc đóng qua mép kia;
  vùng S/R phải có "cú phá thật"; hồi ≥ 3 nến không có nến hồi lớn hơn nến đà; nến xác nhận tại vùng; SL qua mép xa của dải ± 1 + 0,3, trần 4 giá; TP 3R;
  ≤ 2 lệnh/vùng/chiều/phiên; khoá mức cho vùng S/R).
- **Khối trạng thái bắt buộc, nguyên văn ý:** "A v5 **chưa có lợi thế đo được**. Trên 61 phiên (90 ngày GCZ26): 324 lệnh (5,3/ngày), WR 22,2 %, R TB −0,18
  [−0,36; +0,01]; TRAIN −0,07 / **TEST −0,32**; cả 6 phép đối chứng **không hơn** vào lệnh bừa; không đạt tiêu chí T1. Bản live có chặn 19:20–20:30: 312 lệnh, R −0,18.
  **Số lệnh tăng nhưng mỗi lệnh vẫn lỗ trung bình ⇒ tổng lỗ tăng theo số lệnh.** Bật để chạy thử và thu số thật, **không phải khuyến nghị vào lệnh**."
- "Cách đọc vùng A đang canh" (mục 4.2, 4 trạng thái, màu).
- Parity: tóm tắt `PARITY-A5.md`; ghi rõ `PARITY.md` cũ (A 18/18) là của **A V3** (class `DetectorA` vẫn trong mã, không chạy live); ReplayCsv `A` = V3, `A5` = bản live.
- Khác biệt live (mục 5.3), khuyên nạp ≥ 30 ngày, thời gian nạp đầu đo được.
- `LogicVersion = port-3-A-v5`; CSV log mới `signals_<symbol>_port-3-A-v5.csv` (file cũ là của logic trước).
- Quy tắc bảo trì: **sửa `vung-canh-lenh/VclCore.cs` ⇒ chạy lại `parity_vcl.py` + `parity_a5.py`, build lại Benzo, tăng `LogicVersion`** (vì Benzo đóng băng VCL vào lúc build).
- Telegram: mẫu giữ nguyên, ví dụ đổi thành `🟢 BUY · A Phá hồi v5 · GCZ26 · 20:24 VN`.

---

## 8. RỦI RO + QUY TRÌNH TRÁNH ĐÈ NHAU

### 8.1 Phiên song song đang sửa setup B (cùng thư mục làm việc)
1. **Trước MỖI lần sửa một file dùng chung** (`BenzoCore.cs`, `BenzoTrader.cs`, `build.sh`, `tests/Program.cs`, `tests/tests.csproj`, `tools/ReplayCsv/*`, `README.md`):
   `git status --short` + `git diff --stat <file>` + `git log --oneline -5`. File đang có thay đổi **chưa commit không phải của mình** ⇒ **KHÔNG sửa**, chờ phiên kia commit
   (kiểm lại sau), quá 2 lần vẫn bẩn ⇒ dừng, báo người điều phối. Không bao giờ `git stash`, `git checkout -- <file>`, `git reset` file người khác.
2. Sửa xong file dùng chung ⇒ **commit ngay** (cửa sổ va chạm ngắn), `git add <đường dẫn cụ thể>` — **cấm** `git add -A` / `git add .` / `git commit -a`.
   Trước `git add` chạy `git diff <file>`: chỉ có thay đổi của mình mới add.
3. `git push origin main` bị từ chối ⇒ `git pull --rebase origin main`; xung đột ở `LogicVersion` ⇒ đặt giá trị mới khác cả hai (vd `port-4-A5-B3`) rồi ghi chú trong commit;
   xung đột ở `CreateDetectors` ⇒ giữ detector B của họ + `DetectorA5` của mình; xung đột khác ⇒ dừng, báo.
4. Thiết kế đã né: code A5 ở file mới; **không đụng `BenzoDetectors.cs`, `BenzoZones.cs`, `parity_check.py`**.

### 8.2 Thứ tự commit (mỗi bước commit + push, message tiếng Việt, dòng cuối `Co-Authored-By: Claude Sonnet ...` theo nhắc của hệ thống)
- **C1** `BenzoSetupA5.cs` + `tests/TestsA5.cs` + 2 csproj (thêm Compile) + 2 dòng `tests/Program.cs` ⇒ test 1–21, 23 xanh.
- **C2** ReplayCsv chế độ A5 + `research/parity_a5.py` + `report/PARITY-A5.md` + `report/_a5_bad_bars.csv` ⇒ L0–L4 đạt; thêm test 22 với số đã chốt.
- **C3** `BenzoCore.cs` + `BenzoTrader.cs` (nối dây, vẽ, Settings, memo, CSV) + `build.sh` + `README.md` ⇒ `./build.sh` 0 cảnh báo mới ⇒ `dist/BenzoTrader.dll` ⇒ commit + push, báo hash.

### 8.3 Rủi ro khác
1. **Không có lợi thế** — rủi ro lớn nhất là người học hiểu "port = đã tốt". Mọi chỗ hiển thị đã có câu trung thực; Sonnet không được viết khác.
2. **VCL đổi về sau làm A đổi theo âm thầm** (VclCore.cs được nối lúc build) ⇒ quy tắc bảo trì ở README + tiên quyết 5.0.
3. **Trùng tên kiểu VCL giữa 2 DLL** ⇒ tiền lệ TpoSuite; có phương án `sed` dự phòng (mục 1.1).
4. **Đọc footprint live lệch file** ⇒ vùng/tín hiệu lệch (5.3-2); chỉ đối chiếu được bằng export sau.
5. **Lần nạp đầu đóng băng giao diện vài giây** với lịch sử dài (90 ngày ≈ 4–8 s ước tính) ⇒ đo, ghi README, khuyên 30–45 ngày.
6. **Đổi `LogicVersion` xoá niêm phong của cả B/C/D** ⇒ lịch sử B/C/D dò lại theo dữ liệu hiện có (có thể khác bản niêm phong cũ). Chấp nhận, ghi README.
7. **Nhiều tin Telegram hơn** (A ~5 tín hiệu/ngày) — cơ chế không đổi; người học tắt A nếu ồn.
8. **Chart rối** ⇒ tối đa 3 mục, chỉ trạng thái đã trang bị, có ô tắt.
9. **Engine dựng lại chỉ khi lịch sử ngắn đi** (giới hạn có sẵn của Benzo, VCL có `VclFeeder` kiểm kỹ hơn): nạp lại dữ liệu khác mà cùng độ dài thì trạng thái cũ còn — có sẵn từ trước, không sửa vòng này; ghi README "đổi mã/khung thì gỡ rồi thêm lại indicator".

### 8.4 Việc người học làm TAY trên Windows (Sonnet ghi đúng danh sách này vào báo cáo cuối)
1. `git pull` repo trên máy Windows (hoặc copy `benzo-trader/dist/BenzoTrader.dll`).
2. Tắt Optimus Flow (hoặc gỡ indicator Benzo khỏi chart) ⇒ chép đè `BenzoTrader.dll` vào `C:\OptimusFLOW\Settings\Scripts\Indicators\BenzoTrader\` ⇒ mở lại.
3. Chart **GCZ26, khung M1**, bật **Volume Analysis**, nạp **≥ 30 ngày** lịch sử ⇒ thêm indicator "Benzo Trader".
4. Kiểm: bảng có dòng `A Phá hồi v5 · … · chưa có lợi thế đo được (chạy thử)`; có vùng/nhãn "A chờ MUA/BÁN …" khi có trạng thái đã trang bị; bật "Telegram: gửi thử" thấy tin `A Phá hồi v5`.
5. (Tuỳ chọn) bật thêm Vùng Canh Lệnh trên cùng chart, cùng độ dài lịch sử: dải tím của nhãn "vùng S/R" phải trùng một vùng VCL đang vẽ.
6. Ghi lại thời gian nạp lần đầu và báo nếu Optimus Flow báo lỗi nạp DLL (⇒ phương án `sed` mục 1.1).

---

## 9. QUYẾT ĐỊNH MẶC ĐỊNH CHO CHỖ MƠ HỒ (Sonnet theo, không hỏi)
1. Thứ tự duyệt vùng/trạng thái không ảnh hưởng kết quả (mỗi trạng thái độc lập; tranh cùng nến có khoá sắp xếp đầy đủ) ⇒ dùng `Dictionary` tuỳ ý, nhưng **danh sách ứng viên phải sắp bằng khoá (khoảng cách, rank, isVcl, Order|eid)**.
2. So khoảng cách bằng `double` thô (không làm tròn), như Python.
3. `Phase` so chuỗi `"OFF"` của `BenzoKernel.PhaseOf`.
4. Giờ trong Reason/nhãn = giờ VN theo `ctx.TzOffset`.
5. `Watch` khi chưa có nến / engine chưa chạy ⇒ danh sách rỗng, không vẽ gì.
6. Eid đứt quãng (vắng rồi quay lại) — Python cấm nên không nên gặp; nếu gặp trong live: coi như vùng mới (lịch sử bắt đầu lại), không ném lỗi; trong ReplayCsv in cảnh báo.
7. `HvnBook` nến đầu dữ liệu: không có phiên đã đóng ⇒ không HVN; tuần đầu tiên = tuần 0.
8. `LastInfo` chỉ ghi khi có tín hiệu; `StateLog` null ⇒ không ghi (live không tốn bộ nhớ).
9. Không thêm bất kỳ ngưỡng số mới nào; không đổi hằng số Python; không lọc thêm "cho đẹp".
10. Gặp ca máy trạng thái không phủ ở trên hoặc lệch parity không thuộc 2 loại được phép ⇒ **dừng, báo**, không đoán.

## 10. GIAO NỘP
Mới: `benzo-trader/BenzoSetupA5.cs`, `benzo-trader/tests/TestsA5.cs`, `benzo-trader/research/parity_a5.py`, `benzo-trader/research/report/PARITY-A5.md`,
`benzo-trader/research/report/_a5_bad_bars.csv`. Sửa: `BenzoCore.cs`, `BenzoTrader.cs`, `build.sh`, `tests/Program.cs` (2 chỗ), `tests/tests.csproj`,
`tools/ReplayCsv/{Program.cs, ReplayCsv.csproj}`, `README.md`, `dist/BenzoTrader.dll`. Báo cáo cuối: bảng L0–L4, số test, số cảnh báo build, thời gian chạy,
hash 3 commit + kết quả push, danh sách việc tay 8.4.
