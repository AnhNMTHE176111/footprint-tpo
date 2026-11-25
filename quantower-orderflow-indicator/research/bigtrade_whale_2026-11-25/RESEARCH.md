# RESEARCH — các nền tảng và tài liệu định nghĩa "lệnh lớn / big trade / block" thế nào

> Fable tra ngày 2026-11-25. Dùng làm **căn cứ chọn ứng viên và khoảng tham số**, không dùng làm con số chốt: con số chốt phải đo trên nhật ký lệnh đơn của chính người học (`PLAN.md`).
> Chỗ nào không mở được trang gốc thì ghi rõ "chưa kiểm được", không suy ra.

## 1. Kết luận rút ra (5 ý)

1. **Không nền tảng nào công bố một con số mặc định dùng chung.** ATAS, NinjaTrader, Sierra Chart, Quantower, MotiveWave, Bookmap đều để người dùng tự đặt cỡ tối thiểu, và đều nói ngưỡng phải theo từng mã. Lời khuyên duy nhất có tính quy tắc: "thấy quá nhiều dấu thì nâng ngưỡng lên" (NinjaTrader). Tức là định nghĩa thực tế của "lệnh lớn" ở mọi nơi là **theo ngân sách số dấu trên màn hình**, không phải theo một lý thuyết.
2. **Hai nền tảng có bộ lọc tự động (ATAS Auto Filter, Deepcharts Big Trades Analysis) đều tính ngưỡng theo từng mã từ lịch sử dài**, không theo vài giờ gần nhất: Deepcharts nói phân tích "chỉ cần chạy một lần mỗi tuần hoặc mỗi tháng". Không bên nào công bố công thức. Điều này ủng hộ cửa sổ tham chiếu **nhiều ngày**, trái với cửa sổ 240 phút đang dùng.
3. **Con số tuyệt đối người trong nghề hay nêu** (chỉ để đối chiếu bậc độ lớn):
   - NQ: khoảng **50 hợp đồng** để lọc nhiễu, ví dụ 65 và 165 (bài blog Bookmap về TraderMap Pro; đây là lệnh chờ trên sổ, không phải lệnh khớp).
   - Ví dụ duy nhất trong tài liệu Deepcharts: Min = **30** hợp đồng. Ví dụ của hỗ trợ Sierra Chart: **30**.
   - Scott Pulcini (iceberg / quét stop, tính trên **tổng khối lượng đã gộp**, không phải một lệnh đơn): NQ **150**, vàng **150**, dầu 150, ES 700.
   - CME: ngưỡng tối thiểu để được giao dịch thỏa thuận ngoài sổ (block) của vàng GC là **25 hợp đồng** (bảng ngưỡng kim loại của CME; bản tìm thấy là bản 2012 và một PDF không ghi ngày — **chưa kiểm được bản hiện hành**). Nghĩa của con số này: sàn giao dịch coi từ 25 hợp đồng vàng trở lên là cỡ "tổ chức".
   - NQ: hợp đồng tương lai E-mini Nasdaq-100 có vẻ **không được phép block** (bảng tóm tắt của CME ghi "INELIGIBLE" ở dòng NQ; **chưa mở được trang để xác nhận cột**); quyền chọn trên NQ có ngưỡng block 20 hợp đồng mỗi chân.
4. **"Một lệnh" phải là lệnh đã gộp theo người chủ động.** Bookmap (Large Trades Alert) và Jigsaw (Reconstructed Tape) đều gộp các lần khớp của cùng một lệnh market thành một: lệnh 10 khớp với 5 + 3 + 2 được tính là một lệnh 10. Cột lệnh đơn của Quantower (`MaxOneTradeVolume`) dùng đúng nghĩa này hay không thì **chưa kiểm được**; nếu nó chỉ là từng lần khớp thì lệnh cá mập bị cắt nhỏ sẽ không hiện. Đây là giới hạn của dữ liệu, không sửa được bằng ngưỡng.
5. **Cỡ lệnh có đuôi dài kiểu lũy thừa.** Nghiên cứu trên cổ phiếu Mỹ: mật độ đuôi của cỡ lệnh giảm theo lũy thừa với số mũ khoảng 1,5 (Gopikrishnan và cộng sự 2000; Plerou và Stanley 2008), nhưng có tranh luận là số mũ bị ước lượng thấp (Rácz, Eisler, Kertész 2009). Với đuôi như vậy **không có một "điểm gãy" tự nhiên** tách lệnh thường khỏi cá mập: mọi ngưỡng đều là một lựa chọn về mức hiếm. Vì thế ứng viên "tìm điểm gãy đuôi" chỉ nên dùng để chẩn đoán. Chưa tìm thấy nghiên cứu nào ước lượng số mũ đuôi riêng cho GC hay NQ.
6. **Cỡ lệnh đổi theo giờ trong ngày.** Andersen, Bondarenko, Kyle, Obizhaeva (E-mini S&P 500, 2008–2011) cho thấy cỡ lệnh trung bình đổi có hệ thống theo giờ và theo biên độ dao động. Vì thế phải đo cả hai hướng: ngưỡng chung cả ngày (cá mập theo nghĩa tuyệt đối) và ngưỡng theo khung giờ (cá mập so với giờ đó).

## 2. Bảng nguồn

| Nguồn | Họ định nghĩa thế nào | Con số | URL |
|---|---|---|---|
| ATAS Big Trades | Hai chế độ: gộp lệnh (Cumulative) và từng lệnh (Separate). Auto Filter chỉ có ở chế độ gộp, "tự chọn ngưỡng theo mã và hoạt động thị trường", ba mức Weak / Medium / Strong. Tắt Auto thì tự nhập Min / Max Volume | Không công bố mặc định hay công thức | https://help.atas.net/en/support/solutions/articles/72000602332-big-trades · https://atas.net/blog/4-useful-tricks-of-the-big-trades-indicator/ |
| Deepcharts Big Trades | Lọc tay Min / Max, hoặc "Big Trades Analysis" tự đặt ngưỡng theo hành vi giá và biên độ của mã, ba mức Low / Medium / Strong; phân tích chạy một lần mỗi tuần hoặc tháng | Ví dụ Min = 30 | https://www.deepcharts.com/helpcenter/article/big-trades |
| NinjaTrader Order Flow Trade Detector | Ba chế độ; chế độ Block: mỗi lần khớp có volume ≥ "Minimum volume for marker" thì vẽ. Hướng dẫn: nhiều dấu quá thì nâng ngưỡng | Không có mặc định | https://static.ninjatrader.com/support/helpGuides/nt8/order_flow_trade_detector.htm |
| Sierra Chart Large Volume Trade Indicator | Một lần khớp từ feed ≥ Volume Threshold; có chế độ "Based on Max Volume Above Threshold" = lệnh lớn nhất tại mỗi mức giá (giống cột lệnh đơn của ta) | Ví dụ của hỗ trợ: 30 | https://www.sierrachart.com/SupportBoard.php?ThreadID=102404 |
| Quantower Power Trades | Min / Max Trade Volume do người dùng đặt | Không có mặc định | https://help.quantower.com/quantower/analytics-panels/chart/power-trades |
| MotiveWave Big Trades | Tối đa 5 bậc cỡ lệnh do người dùng đặt; tùy chọn gộp các lần khớp cùng giá, cùng phía trong một khoảng mili-giây | Không có mặc định | https://docs.motivewave.com/user-guide/volume-order-flow-analysis-guide/big-trades |
| Bookmap Large Trades Alert | Gộp theo mã người chủ động thành một lệnh; báo khi lệnh ≥ cỡ người dùng đặt | Ví dụ minh họa 10 = 5 + 3 + 2 | https://bookmap.com/knowledgebase/docs/Addons-Large-Trades-Alert |
| Bookmap Large Lot Tracker | Theo dõi **lệnh chờ** lớn trên sổ: lô ≥ 20% tổng cỡ tại mức giá và ≥ 10% thanh lớn nhất. Định nghĩa **tương đối**, không phải số hợp đồng | 20% / 10% | https://www.bookmap.com/knowledgebase/docs/KB-Indicators-LLT |
| Blog Bookmap, TraderMap Pro | "Cỡ lệnh theo từng chỉ số": ES khoảng 100, NQ và RTY khoảng 50 để lọc nhiễu; khung dài thì ngưỡng cao hơn | ES 100; NQ 50 (ví dụ 65, 165) | https://bookmap.com/blog/4-ways-to-trade-with-tradermap-pro/ |
| Scott Pulcini (qua TradeZella) | Iceberg / quét stop đủ cỡ tổ chức, tính trên tổng đã gộp, và phải ở vùng giá quan trọng | ES 700 / 500; NQ 150; vàng 150; dầu 150 | https://www.tradezella.com/strategies/institutional-order-flow-iceberg-trading-strategy |
| Jigsaw Reconstructed Tape | Gộp các lần khớp của một lệnh market; có ô "Block Trade Size" do người dùng đặt | Không tìm thấy số khuyến nghị | https://www.scribd.com/doc/241941842/Jigsaw-Product-Manual |
| CME, ngưỡng block kim loại | Cỡ tối thiểu để giao dịch thỏa thuận ngoài sổ | GC 25 hợp đồng, báo trong 5 phút (bản 2012 / PDF không ngày; **chưa kiểm bản hiện hành**) | https://www.cmegroup.com/trading/metals/files/nymex-and-comex-metals-trade-minimum-thresholds.pdf · danh sách hiện hành: https://www.cmegroup.com/clearing/trading-practices/files/block-minimum-thresholds-list.xlsx |
| CME, block chỉ số cổ phiếu | Dòng NQ ghi "INELIGIBLE" (chưa xác nhận cột); quyền chọn NQ: 20 hợp đồng mỗi chân | — | https://www.cmegroup.com/markets/equities/files/block-trade-cheat-sheet.pdf · https://www.cmegroup.com/education/articles-and-reports/e-mini-equity-index-options-block-quick-reference-guide.html |
| Gopikrishnan, Plerou, Gabaix, Stanley (2000); Plerou và Stanley (2008) | Cỡ lệnh cổ phiếu có đuôi lũy thừa | Số mũ đuôi 1,53 ± 0,07 | https://www.math.nyu.edu/faculty/avellane/Plerou2008.pdf |
| Rácz, Eisler, Kertész (2009) | Phản biện: số mũ trên bị ước lượng thấp, bộ ước lượng hội tụ chậm | — | https://dx.doi.org/10.1103/physreve.79.068102 |
| Andersen, Bondarenko, Kyle, Obizhaeva | E-mini S&P 500: cỡ lệnh đổi có hệ thống theo giờ trong ngày và theo biên độ dao động | — | https://www.nes.ru/files/Preprints-resh/WP272.pdf |

## 3. Đối chiếu nhanh với nhật ký của người học (số đếm từ `out_bw0_profile.txt`, chưa phải kết quả đo chính thức)

| | Vàng GC, M1, 16 ngày đủ (1–23/9) | NQ, M1, 6 ngày đủ (26/10–2/11) |
|---|---|---|
| Trung vị lệnh đơn của một ô | 1 | 1 |
| Mức 1% lớn nhất | 9 | 9 |
| Mức 0,1% lớn nhất | 25 | 28 |
| Số ô có lệnh đơn ≥ 30 mỗi ngày | 7–33 (thường 15–25) | 45–98 |
| ≥ 50 mỗi ngày | 1–18 (thường 4–12) | 19–40 |
| ≥ 100 mỗi ngày | 0–4 | 0–11 |
| Lệnh lớn nhất | 500 | 581 |

Đọc bảng: mốc "25 của CME" và "30 của Deepcharts / Sierra" trên vàng vẫn cho 15–25 vòng mỗi ngày, mốc "50 của Bookmap" trên NQ cho 19–40 vòng mỗi ngày. Con số chép từ internet **không tự cho ra mật độ hợp lý**; phải đo.

## 4. Chưa kiểm được

- Bản hiện hành của ngưỡng block GC, MGC và tình trạng block của NQ, MNQ (trang CME quá thời gian chờ khi mở). Con số 25 chỉ được dùng làm mốc đối chiếu.
- Công thức Auto Filter của ATAS và Big Trades Analysis của Deepcharts (không công bố).
- Cỡ lệnh trung bình mỗi lần khớp của GC, NQ, MGC, MNQ do CME công bố: không tìm thấy.
- Cỡ lệnh điển hình của MGC và MNQ: nhật ký chưa có hai mã này, nên thuật toán chốt phải **tự co theo mã**, không dùng hằng số theo mã.
