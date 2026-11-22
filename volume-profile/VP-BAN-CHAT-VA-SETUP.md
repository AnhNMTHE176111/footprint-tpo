# Volume Profile — bản chất, hành vi và các setup mạnh (tổng hợp nguồn công khai, 2026-11-22)

> Nguồn: Dalton *Mind over Markets* / *Markets in Profile* (qua trích dẫn), CBOT guide, LuxAlgo, Quantower, NexusFi, Jigsaw,
> Bookmap, Axia, Trader Dale, FTMO, Keenbase, EV-Labs (TradingView), tradingstats.net, Indicatr, dvcap backtest, SSRN.
> Hai agent research, ~110 lượt tìm/đọc. Reddit và NexusFi forum bị chặn, không lấy được kinh nghiệm cá nhân.

## PHẦN 1 — BẢN CHẤT

**Volume Profile là gì.** Biểu đồ khối lượng theo **giá** (không phải theo thời gian). Mỗi dòng ngang = số hợp đồng đã khớp ở giá đó.
TPO (Market Profile) đếm **thời gian** ở giá; Volume Profile đếm **hợp đồng** ở giá. Sierra Chart: "thời gian ở giá chưa chắc là chấp nhận, khối lượng mới là".

**Ba khái niệm lõi** (tất cả nguồn thống nhất):
- **POC** — giá có khối lượng lớn nhất. Trên ngày có 2 đỉnh gần bằng nhau, POC không ổn định (Keenbase: ~1/5 số ngày vàng, POC M1 và M15 lệch > 10% biên độ).
- **Value Area (VA) 70%** — vùng chứa 70% khối lượng quanh POC. 70% chỉ là làm tròn của 68% (1 độ lệch chuẩn) — "quy ước, không phải định luật"; profile thật hiếm khi phân phối chuẩn. Mỗi phần mềm mở rộng VA hơi khác nhau ⇒ VAH/VAL lệch vài tick giữa các nền tảng.
- **HVN / LVN** — nút dày = giá được chấp nhận, đấu giá hai chiều; nút mỏng = giá bị từ chối, đi qua nhanh. Phải so **tương đối** với cả profile.

**Các cấu trúc khác**: đuôi đơn (single prints) ở mép = từ chối sạch (excess); đỉnh/đáy phẳng ≥ 2 TPO không có đuôi = **poor high/low**
(đấu giá dừng mà chưa có bằng chứng từ chối); **naked POC** = POC phiên cũ chưa bị giá chạm lại; **double distribution** = 2 HVN nối
bằng một đoạn mỏng; **IB** = 1 giờ đầu phiên; dịch chuyển VA ngày sau so với ngày trước = cân bằng (chồng lên) hay mất cân bằng (dịch hẳn).

**Tiên đề của Dalton**: mục đích của thị trường là **tạo điều kiện giao dịch**. Giá là "quảng cáo", thời gian "điều tiết", khối lượng "đo mức
độ thành công" của quảng cáo đó. Giá đi lên/xuống để tìm nơi có người sell và người buy cùng đồng ý — nơi đó khối lượng phình ra
(HVN). Giá chạy nhanh qua nơi không ai đồng ý (LVN). **Đây là cách giải thích, không phải định luật đo được.**

## PHẦN 2 — HÀNH VI: cái gì được dạy, cái gì có số

| Hành vi được dạy | Số đo công khai | Kết luận |
|---|---|---|
| Giá chạy nhanh qua LVN, chậm ở HVN | Không có kiểm định | Giai thoại. Cùng một LVN được dạy vừa là "đường cao tốc" vừa là "chỗ bật" — mâu thuẫn chưa giải. |
| Naked POC là nam châm, giá sẽ quay về | EV-Labs 1.432 phiên ES/NQ + XAUUSD: chạm lại 55–67% trong 1 phiên, 88–94% trong 20 phiên — **bằng hệt mức đối chứng (trung điểm phiên)**. Indicatr (có GC): chạm trong 2 phiên 62% nếu cách < 0,5 biên độ ngày, 39% nếu 0,5–1, 11–16% nếu 1–2. | **Khoảng cách quyết định, không phải POC.** Khớp với 3 lần đo trong repo (SR-KET-QUA, HVN, Vùng Canh Lệnh). |
| Luật 80%: mở ngoài VA, vào lại 2 bracket ⇒ 80% đi hết VA | Keenbase 6 thị trường × 500 ngày: 42–53% (vàng 43%). TeamLBR ES: 40%. dvcap: ~50%, bằng khoảng cách dự báo. | **Bị bác ở mức 80%.** Chính Dalton 2016: "luật 80% và failed auction không thực sự hoạt động". |
| Poor high/low sẽ được "sửa" (chạm lại) | Không có số có phương pháp; FTMO nói 70–80% nhưng không nguồn | Giai thoại. Dùng làm **mục tiêu** chứ không làm tường. |
| Single prints / gap sẽ được lấp | Không có số. Dalton: gap càng lớn càng ít lấp | Giai thoại. |
| **Hai vùng đã đấu giá xong thì giá quay về đấu giá đoạn giữa** (ví dụ của người học) | **Không nguồn nào nói vậy.** Tài liệu nói ngược: đoạn mỏng giữa 2 HVN là "đường quyết định", giá **đi qua nhanh** và **phản ứng tại đó** khi quay lại; nếu giữ được thì giá xoay giữa 2 VA. Trader Dale có dạy "double distribution sẽ lấp thành chữ D" nhưng là nhà bán khoá học, không có số. | Ví dụ của người học thuộc loại **có thể đúng nhưng chưa ai đo**. Đáng để tự đếm trên GCZ26. |
| Thị trường cân bằng 70–85% thời gian | Không nguồn | Folklore. |
| VA dịch chuyển liên tiếp một chiều = xu hướng | Không số | "Xác nhận, không dự báo". |
| Mở cửa so với VA hôm qua (Keenbase, vàng n=501) | Mở trong VA → chạm POC cũ 83%; mở ngoài VA → vào lại VA 78%, chạm POC 46%. Khoảng cách mở cửa tới mức: < 0,25 ATR chạm 84%, 0,5–1 ATR 26%, 1–2 ATR 17%. | Có số nhưng từ volume tick của broker CFD, không phải volume thật. |

**Chấp nhận vs từ chối** (quan trọng nhất về cơ chế): Dalton đo bằng **giá + thời gian + khối lượng cùng lúc**. Giá vượt VAH chưa phải
chấp nhận; khối lượng bắt đầu **dày lên** ở vùng mới mới là chấp nhận. Không nguồn nào cho ngưỡng cố định (bao nhiêu nến, bao nhiêu
hợp đồng). Quantower: "chấp nhận hay từ chối không phải thuộc tính vĩnh viễn của mức giá".

## PHẦN 3 — CÁC SETUP, xếp theo số nguồn độc lập đồng ý và bằng chứng

| # | Setup | Luật cốt lõi | Bối cảnh bắt buộc | Bằng chứng |
|---|---|---|---|---|
| 1 | **Luật 80% (vào lại VA)** | Mở ngoài VA hôm qua → giá vào lại VA và được chấp nhận (2 bracket 30 phút, hoặc 2 nến 15 phút) → vào theo hướng xuyên VA, SL ngoài mép vừa xuyên, TP mép đối diện, chốt một phần ở POC | Mở cửa kiểu không có niềm tin (open-auction); không dùng khi open-drive | Đã đo: **42–53%**, không hơn khoảng cách |
| 2 | **Phá / mở rộng / retest IB** | Phá IB sau giờ đầu → chờ **retest** mép IB vừa phá → vào theo hướng phá; râu từ chối ở retest tăng xác suất tiếp diễn | IB hẹp (so với 14 ngày) tốt hơn; nhịp nhanh tốt hơn; **cuối phiên tiếp diễn chỉ 23%** | tradingstats ES/NQ ~3.000 ngày: retest 90%, tiếp diễn 77% ở mức 1,1× IB. **Chưa có cho vàng.** |
| 3 | **Naked POC làm mục tiêu** | Dùng làm **TP / chốt bớt** khi giá rời cân bằng về phía nó; không dùng làm điểm vào | Chỉ tính POC gần (< 0,5 biên độ ngày) | Chạm = đối chứng ngẫu nhiên; **không có lợi thế vào lệnh**, chỉ có giá trị làm mục tiêu |
| 4 | **Pullback về HVN trong xu hướng** (Trader Dale, FT71) | Xu hướng rõ → vẽ profile riêng đoạn xu hướng → mức = **mép đầu** của cụm dày → chờ giá kéo về, vào chạm đầu, mỗi mức dùng 1 lần; SL sau cụm dày, TP trước cụm dày kế | Chỉ xu hướng đã thành lập; mức < 1 tháng | Không có số. Jigsaw phản bác: "profile không có trí nhớ, khoảng cách là vua" |
| 5 | **Fade mép VA / mép HVN trong cân bằng** (Jigsaw, Bookmap) | Ngày xoay vòng: buy đáy dải HVN, sell đỉnh dải; sau 3–4 lần test mép thì chờ **headfake** (phá giả) và đọc order flow thấy người phá giả thoát | POC phẳng sau ~45 phút đầu = cân bằng; **tuyệt đối không fade ngày xu hướng** | Không số. dvcap: chạm VAH/POC hôm qua trên SPY **âm** ở một số mức |
| 6 | **Phá HVN vào LVN** | Đóng nến xuyên HVN vào LVN + delta cùng chiều → TP HVN kế, SL quay lại trong HVN | Thất bại trong ngày cân bằng; nguồn mâu thuẫn (futureshive: không bao giờ vào giữa LVN) | Không số |
| 7 | **Look above and fail / failed auction** | Phá đỉnh cân bằng, hút buy, rồi rơi lại dưới mức có tốc độ → sell sau khi vào lại được xác nhận; SL ngoài đỉnh giả; TP mép đối diện | Trong cân bằng; không mechanic | Không số |
| 8 | Poor high/low | Dùng làm **mục tiêu**, không sell vào poor high | Vùng mỏng qua đêm = thị trường vắng, không phải từ chối | Không số, tác giả từ chối đưa % |
| 9 | Loại mở cửa (Dalton) | Open-drive không quay về giá mở → trade pullback theo hướng; open-auction → chờ xong IB | — | Không số |
| 10 | POC phiên dịch chuyển | POC trôi đều một chiều = xu hướng, buy pullback về POC đang hình thành; POC phẳng = cân bằng | — | Ngưỡng tùy tiện |

**Điều chỉnh cho scalp M1 (tổng hợp các nguồn, không có nguồn nào chuyên M1 có số):**
- Mức lấy từ khung lớn, kích hoạt ở khung nhỏ: Trader Dale lấy mức ở profile 30 phút, kích hoạt bằng footprint 5 phút. Playbook M1 của
  TheForexGeek: composite 15 phút + profile phiên + đỉnh/đáy/POC hôm qua; kích hoạt M1 = Bid/Ask tăng vọt hoặc nến nhấn chìm trên
  khối lượng cao tại mép VAL/dưới HVN; SL ngoài mép xa; TP HVN gần nhất; **dừng lệnh sau 3–5 nến M1 nếu không chạy**.
- Kích hoạt order flow tại vùng (Dale): **hấp thụ** = Bid và Ask cùng nặng bất thường trong vùng mà giá đứng; **delta đảo** chiều trong
  vùng; **lệnh đơn lớn**. Tín hiệu ngoài vùng = nhiễu.
- Jigsaw: profile trong ngày = bản đồ **người đang kẹt**; càng xa càng mất ý nghĩa; luôn cần order flow xác nhận.
- Không nguồn nào ghi phương pháp "composite 2–4 giờ" có số.

## PHẦN 4 — Cảnh báo lặp lại ở nhiều nguồn
1. Mức là **vùng**, không phải đường. 2. **Khoảng cách** chi phối mọi xác suất chạm. 3. Không fade ngày xu hướng, không breakout ngày
cân bằng. 4. Đổi định nghĩa (68/70%, TPO/volume, RTH/ETH, 1 hay 2 bracket) đổi kết quả. 5. Tiếp diễn cuối phiên rơi mạnh. 6. Vàng 23h:
profile qua đêm mỏng gây hiểu nhầm. 7. Mọi con số của người bán khoá học (80%, 80–90% lấp NPOC, WR 62%) đều không kiểm toán.

**Đối chiếu với repo**: 3 lần đo độc lập trên GCZ26 (SR-KET-QUA, HVN, Vùng Canh Lệnh) cho cùng kết luận với Internet: vị trí VA/POC/HVN
không bật nhiều hơn đối chứng khớp khoảng cách. ⇒ Volume Profile dùng để **đọc bối cảnh** (cân bằng hay mất cân bằng, giá đang ở đâu
so với giá trị, mục tiêu ở đâu), **không** dùng làm điểm vào tự động. Điểm vào vẫn phải lấy từ footprint/hấp thụ tại vùng.

## PHẦN 5 — Bài săn bằng chứng (Optimus Flow, GCZ26, profile phiên)
1. **Nhận dạng**: tìm 1 phiên double distribution (2 HVN + đoạn mỏng giữa). Chụp ảnh có mã · khung · ngày giờ · số.
2. **Đếm** (kiểm tra ví dụ của người học): 20 phiên liên tiếp không chọn lọc. Với mỗi phiên có double distribution trong 2 giờ đầu, ghi:
   giá có quay về đoạn mỏng giữa trước cuối phiên không? Khi quay về, nó **đi xuyên nhanh** hay **dừng/bật** tại đó? Ghi phán đoán trước,
   Claude đếm bằng số từ `data-export/data-footprint/fp_GCZ26_*_90d.csv` sau.
3. **Phản chứng**: tìm 1 phiên mà luật "giá chạy nhanh qua LVN" sai (giá dừng và dày lên ngay trong LVN cũ).
