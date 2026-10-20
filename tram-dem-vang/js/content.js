/* Trạm Đêm Vàng — TOÀN BỘ chữ hiển thị: nhãn, tiêu chí, trợ giúp, lý do theo mã + htRef. Dữ liệu thuần.
 * Quy tắc chữ: tiếng Việt đủ dấu; giữ buy / sell / limit / market; cấm "bán", "mua", "lệnh chờ", "đập giá". */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else { root.TDV = root.TDV || {}; root.TDV.content = factory(); }
})(this, function () {
  'use strict';

  var HT_BASE = 'https://anhnmthe176111.github.io/he-thong-dem-vang/#';

  var scenarios = {
    A: { name: 'Phá hồi', short: 'A', img: 'img/kb-a-pha-hoi.png', anchor: 'kb-a', target: '3R', be: '+1,5R',
      blurb: 'Cú phá đã được công nhận, giá hồi hình U về cạnh vừa phá rồi đi tiếp theo chiều phá.' },
    B: { name: 'Hấp thụ', short: 'B', img: 'img/kb-b-hap-thu.png', anchor: 'kb-b', target: '3R', be: '+1,5R',
      blurb: 'Giá tới vùng hạng 1–2, một phe đánh mạnh mà giá không đi. Vào theo phe bị hấp thụ sau nến xác nhận.' },
    C: { name: 'Fade cạnh', short: 'C', img: 'img/kb-c-fade-canh.png', anchor: 'kb-c', target: '2R', be: '+1R',
      blurb: 'Giá phá hụt qua cạnh range rồi đóng lại trong. Vào ngược hướng phá hụt, cỡ nhỏ.' },
    D: { name: 'Trap', short: 'D', img: 'img/kb-d-trap.png', anchor: 'kb-d', target: '2R', be: '+1R',
      blurb: 'Sau một move rõ, phe hồi thử rồi thất bại ở đỉnh nhịp hồi. Vào theo chiều move cũ.' }
  };

  var modes = { balanced: 'cân bằng', pending: 'chờ công nhận', broken: 'vừa phá', thin: 'Trend thin' };
  var modeLabels = { balanced: 'Cân bằng', broken: 'Vừa phá', thin: 'Trend thin' };

  var zoneTypes = {
    vwapW: { label: 'VWAP tuần', rank: 'hạng 1' },
    vwapD: { label: 'VWAP ngày', rank: 'hạng 2' },
    hvnW: { label: 'HVN tuần', rank: 'hạng 2' },
    pocCluster: { label: 'Cụm POC (từ 2 POC, cách ≤ 1 giá)', rank: 'hạng 2' },
    vahEu: { label: 'VAH Âu', rank: 'cạnh' },
    valEu: { label: 'VAL Âu', rank: 'cạnh' },
    rangeEdge: { label: 'Cạnh range (chọn phía)', rank: 'cạnh' },
    ibHigh: { label: 'IB high', rank: 'cạnh' },
    ibLow: { label: 'IB low', rank: 'cạnh' },
    highY: { label: 'High hôm qua', rank: 'cạnh ngoài' },
    lowY: { label: 'Low hôm qua', rank: 'cạnh ngoài' },
    sp: { label: 'Single print (chọn phía)', rank: 'nợ' },
    poorHigh: { label: 'Poor high', rank: 'nợ' },
    poorLow: { label: 'Poor low', rank: 'nợ' },
    nakedPoc: { label: 'Naked POC', rank: 'chỉ mục tiêu' },
    hvnDay: { label: 'HVN ngày', rank: 'trung tính' },
    hvn3w: { label: 'HVN 3 tuần', rank: 'cấm fade' },
    lvn: { label: 'LVN', rank: 'cấm fade' }
  };
  var flagText = {
    r1: 'hạng 1', r2: 'hạng 2', edge: 'cạnh', edgeOuter: 'cạnh ngoài', tail: 'tail thật', sp: 'single print',
    noB: 'chặn hấp thụ', banned: 'cấm fade'
  };

  var tiers = [
    { id: 0, name: 'Trước', long: 'Trước khi mở chart' },
    { id: 1, name: 'Vùng', long: 'Kẻ vùng và chốt thẻ phiên' },
    { id: 2, name: 'Chế độ', long: 'Chế độ thị trường' },
    { id: 3, name: 'Kèo', long: 'Kèo trên M1' },
    { id: 4, name: 'Lệnh', long: 'Lệnh đang mở' },
    { id: 5, name: 'Sổ', long: 'Sổ và cài đặt' }
  ];

  // ===== Mã luật → chữ + htRef =====
  var codes = {
    OFF_RULE_BREAKS: { text: 'Đã 2 lệnh phá luật trong đêm — tắt máy đến hết đêm.', htRef: '7' },
    OFF_SL_STREAK: { text: 'Đã 3 SL liên tiếp — tắt máy đến hết đêm.', htRef: '7' },
    LOCK_OPEN_TRADE: { text: 'Đang có lệnh mở — chỉ một lệnh, không nhồi.', htRef: '6' },
    NO_NEWS_WINDOW: { text: 'Đang trong cửa sổ cấm tin.', htRef: '7' },
    DIS_LONGEST_BAR: { text: 'Ba nến sau nến dài nhất phiên: chưa bật kịch bản nào.', htRef: '5' },
    DIS_NO_CARD: { text: 'Chưa chốt thẻ phiên — không có thẻ thì không có lệnh.', htRef: '2' },
    DIS_BIAS_WAIT: { text: 'Bias đang CHỜ (giá sát VWAP tuần) — chưa bật kịch bản nào.', htRef: '2.2' },
    DIS_BIAS_NONE: { text: 'Bias KHÔNG — chỉ còn fade cạnh VA Âu (C).', htRef: '2.2' },
    DIS_NO_EDGE: { text: 'Thẻ chưa có vùng cạnh (VAH Âu, VAL Âu, IB, cạnh range) — không fade, không hấp thụ.', htRef: '3' },
    DIS_NOT_BROKEN: { text: 'Chưa có cú phá được công nhận — phá hồi chưa bật.', htRef: '3.1' },
    DIS_PENDING_ACCEPT: { text: 'Cú phá đang chờ công nhận (thiếu bước 2) — phá hồi chưa bật.', htRef: '3.1' },
    DIS_NO_MOVE: { text: 'Chưa có move rõ để gọi trap.', htRef: '5' },
    DIS_M5_OUTSIDE: { text: 'Đã có nến M5 đóng ngoài cạnh — fade cạnh tắt, chờ công nhận cú phá.', htRef: '5' },
    DIS_USE_D: { text: 'Trend thin: cùng chiều ở nhịp hồi thì dùng D; ngược chiều là cản tàu.', htRef: '3' },
    DIS_THIN_NO_FADE: { text: 'Trend thin: không fade đỉnh, không fade đáy.', htRef: '3' },
    DIS_BREAK_AGAINST_BIAS: { text: 'Chiều phá ngược bias — không phá hồi, không trap.', htRef: '2.2' },
    DIS_EARLY_BREAK: { text: 'Cú phá trong 18:00–{comex} hay là phá giả — nghi trước, tin sau.', htRef: '3.2' },
    NO_COUNTER_BIAS_SCENARIO: { text: 'Ngược bias — kịch bản này không được ngược bias.', htRef: '2.2' },
    NO_COUNTER_BIAS_ZONE: { text: 'Ngược bias chỉ được ở High / Low hôm qua có tail thật hoặc single print đúng phía.', htRef: '2.2' },
    NO_BIAS_NONE_EDGE: { text: 'Bias KHÔNG: chỉ fade hai cạnh VA Âu (VAH Âu, VAL Âu).', htRef: '2.2' },
    NO_ZONE_3RD: { text: 'Đã vào 2 lần ở vùng này — không có lần thứ ba.', htRef: '7' },
    NO_BANNED_ZONE: { text: 'Không hấp thụ ở HVN ngày, HVN 3 tuần hay LVN.', htRef: '2.3' },
    NO_MID_RANGE: { text: 'Giữa range không có lệnh — chỉ làm tại cạnh.', htRef: '7' },
    NO_C_NOT_EDGE: { text: 'Fade chỉ ở đúng cạnh VA Âu hoặc cạnh range (cách không quá 1 giá); vùng này không phải cạnh.', htRef: '5·C' },
    NO_PENDING_ACCEPT: { text: 'Cạnh vừa phá đang chờ công nhận — không fade, không hấp thụ ở đó.', htRef: '3.1' },
    NO_B_RANK: { text: 'Vùng này chưa đủ hạng cho hấp thụ (cần hạng 1–2, hoặc cạnh khi cân bằng).', htRef: '2.3' },
    NO_FIGHT_BREAK: { text: 'Hấp thụ ngược chiều phá là cản tàu.', htRef: '5' },
    NO_BUBBLE_AGAINST: { text: 'Bong bóng to gần nhất đứng phe ngược lại.', htRef: '4.3' },
    NO_UNCLEAR: { text: 'Có câu trả lời "không rõ" — không rõ thì không vào.', htRef: '4' },
    NO_BACK: { text: 'Giá đã đi từ 3 giá khỏi vùng — ở lưng, không vào.', htRef: '4.4' },
    NO_DMA_SLOPE: { text: 'DMA còn dốc — đà chưa cạn, không gọi hấp thụ.', htRef: '5' },
    NO_D_NO_MOVE: { text: 'Move chưa tới 5 giá — không gọi trap.', htRef: '5' },
    NO_D_DEEP: { text: 'Nhịp hồi đã quá 70 % move — không còn là hồi.', htRef: '5' },
    NO_V_PULLBACK: { text: 'Nhịp hồi hình V — phe hồi đang thắng.', htRef: '4.1' },
    NO_MOMENTUM: { text: 'Thân nến và delta tăng dần — đó là đà, không phải hấp thụ.', htRef: '4.2' },
    NO_SL_POS: { text: 'SL không đúng chỗ theo kịch bản.', htRef: '6' },
    NO_SL_SIDE: { text: 'SL nằm sai phía so với giá vào.', htRef: '6' },
    NO_SL_FLOOR: { text: 'SL {sl} nhỏ hơn nến {c6} — đẩy SL ra hoặc bỏ kèo.', htRef: '6' },
    NO_SL_CAP: { text: 'Khoảng SL quá 4 giá — bỏ kèo hoặc chờ hồi sâu hơn.', htRef: '6' },
    NO_RR: { text: 'R:R dưới 1:2 — bỏ kèo.', htRef: '6' },
    NO_TP_PAST_ZONE: { text: 'TP vượt vùng kế tiếp quá 0,5 giá — kéo TP về vùng đó.', htRef: '6' },
    NO_SIZE_ZERO: { text: 'Vốn × rủi ro chưa đủ 1 hợp đồng MGC với SL này. Với vốn {cap} $ · rủi ro {pct} %, SL tối đa {max} giá. Bỏ kèo, hoặc tăng vốn.', htRef: 'ST §6' },

    WAIT_SCENARIO: { text: 'Chọn kịch bản', ctl: 'c1', htRef: '5' },
    WAIT_ZONE: { text: 'Chọn vùng', ctl: 'c3', htRef: '5' },
    WAIT_SIDE: { text: 'Chọn hướng', ctl: 'c2', htRef: '5' },
    WAIT_REGIME_DIR: { text: 'Chọn hướng ở tầng 2', ctl: 'c2', htRef: '5' },
    WAIT_COUNTER_REASON: { text: 'Ghi lý do ngược bias', ctl: 'c2', htRef: '2.2' },
    WAIT_C4: { text: 'Bong bóng to gần nhất', ctl: 'c4', htRef: '4.3' },
    WAIT_C4_SAME: { text: 'Chờ bong bóng cùng phe', ctl: 'c4', htRef: '4.3' },
    WAIT_C5: { text: 'Giá cách vùng bao xa', ctl: 'c5', htRef: '4.4' },
    WAIT_C5_BACK: { text: 'Chờ hồi về cạnh', ctl: 'c5', htRef: '4.4' },
    WAIT_C6: { text: 'Biên độ nến M1 cao nhất 5 nến', ctl: 'c6', htRef: '6' },
    WAIT_C6_BIG: { text: 'Biên độ hơn 20 giá — gõ biên độ nến, không gõ mức giá', ctl: 'c6', htRef: '6' },
    WAIT_C7_DMA: { text: 'DMA ngang hay còn dốc', ctl: 'c7', htRef: '5' },
    WAIT_C7_MOVE: { text: 'Move vừa rồi bao nhiêu giá', ctl: 'c7', htRef: '5' },
    WAIT_C7_DEEP: { text: 'Nhịp hồi đã quá 70 % chưa', ctl: 'c7', htRef: '5' },
    WAIT_B1: { text: 'Nhịp hồi U hay V', ctl: 'b1', htRef: '4.1' },
    WAIT_B2: { text: 'Thân nến và delta 3 nến cuối', ctl: 'b2', htRef: '4.2' },
    WAIT_B2_MIXED: { text: 'Chưa đủ 3 nến giảm dần', ctl: 'b2', htRef: '4.2' },
    WAIT_B3: { text: 'Nến xác nhận', ctl: 'b3', htRef: '5' },
    WAIT_B3_NOT: { text: 'Chờ nến xác nhận đạt chuẩn', ctl: 'b3', htRef: '5' },
    WAIT_CALC: { text: 'Giá vào và SL', ctl: 'b4', htRef: '6' },
    WAIT_B5: { text: 'SL đúng chỗ', ctl: 'b5', htRef: '6' }
  };

  // mã → ô điều khiển để bấm vào xem / sửa (NO_UNCLEAR chọn theo ô đang "không rõ")
  var ctlMap = {
    NO_BUBBLE_AGAINST: 'c4', NO_BACK: 'c5', NO_DMA_SLOPE: 'c7', NO_D_NO_MOVE: 'c7', NO_D_DEEP: 'c7', NO_V_PULLBACK: 'b1', NO_MOMENTUM: 'b2',
    NO_SL_POS: 'b5', NO_SL_SIDE: 'b4', NO_SL_FLOOR: 'b4', NO_SL_CAP: 'b4', NO_RR: 'b4', NO_TP_PAST_ZONE: 'b4', NO_SIZE_ZERO: 'b4', NO_BIAS_NONE_EDGE: 'c3', NO_ZONE_3RD: 'c3', NO_BANNED_ZONE: 'c3',
    NO_MID_RANGE: 'c3', NO_C_NOT_EDGE: 'c3', NO_PENDING_ACCEPT: 'c3', NO_B_RANK: 'c3', NO_FIGHT_BREAK: 'c3', NO_COUNTER_BIAS_SCENARIO: 'c2', NO_COUNTER_BIAS_ZONE: 'c2',
    DIS_LONGEST_BAR: 'c1', DIS_NOT_BROKEN: 'c1', DIS_PENDING_ACCEPT: 'c1', DIS_NO_MOVE: 'c1', DIS_M5_OUTSIDE: 'c1', DIS_USE_D: 'c1', DIS_THIN_NO_FADE: 'c1',
    DIS_BREAK_AGAINST_BIAS: 'c1', DIS_EARLY_BREAK: 'c1', DIS_BIAS_NONE: 'c1', DIS_NO_EDGE: 'c1'
  };
  Object.keys(ctlMap).forEach(function (k) { codes[k].ctl = ctlMap[k]; });

  var halfText = {
    BIAS_NONE: 'bias KHÔNG', SCENARIO_C: 'fade cạnh (C)', COUNTER_BIAS: 'ngược bias', NEWS_DAY: 'ngày có tin lớn',
    B_RANK2: 'vùng hạng 2', BEFORE_2030: 'trước {nyse} (hay mở ảo)'
  };
  var warnText = {
    WARN_NYSE: 'NYSE mở — không đánh tin.',
    WARN_BEFORE_2030: 'Trước {nyse} vàng hay mở ảo (cú phá chưa đáng tin): cỡ ½.',
    WARN_FEW_ZONES: 'Thẻ có dưới 3 vùng — vẫn chốt được, nhưng ít chỗ để vào.'
  };

  // ===== Câu hỏi tầng 1 =====
  var shapes = [
    { v: 'D', label: 'D' }, { v: 'P', label: 'P' }, { v: 'b', label: 'b' },
    { v: 'B', label: 'B' }, { v: 'thin', label: 'thin' }, { v: 'rect', label: 'Chữ nhật' }
  ];
  var tailOpts = function (poor) {
    return [{ v: 'tail', label: 'Tail thật' }, { v: 'bait', label: 'Mồi' }, { v: poor, label: poor === 'poorHigh' ? 'Poor high' : 'Poor low' }, { v: 'normal', label: 'Bình thường' }];
  };
  var questions = [
    { id: 'q1', num: 'Q1', label: 'Hình dạng profile hôm qua', options: shapes, help: { text: 'D: đấu giá xong, chờ phá. P: cân bằng ở đỉnh, đuôi là hỗ trợ; b ngược lại. thin: mỏng, một chiều, không đánh ngược. Chữ nhật: cân bằng rộng, sẽ phá một đầu.', ref: 'sau-cau-hoi', gloss: 'hinh-dang' } },
    { id: 'q1w', num: 'Q1′', label: 'Hình dạng profile 3 tuần', options: shapes, help: { text: 'Cùng cách đọc như hôm qua nhưng trên TPO gộp 3 tuần.', ref: 'sau-cau-hoi', gloss: 'hinh-dang' } },
    { id: 'q2top', num: 'Q2a', label: 'Đỉnh hôm qua', options: tailOpts('poorHigh'), help: { text: 'Tail thật là 1 TPO với khối lượng thấp. Cực trị khối lượng dày là mồi, không coi là đỉnh.', ref: 'sau-cau-hoi', gloss: 'moi' } },
    { id: 'q2bot', num: 'Q2b', label: 'Đáy hôm qua', options: tailOpts('poorLow'), help: { text: 'Tail thật là 1 TPO với khối lượng thấp. Poor low (từ 2 TPO) là nợ, sẽ bị chạm lại. Cực trị khối lượng dày là mồi.', ref: 'sau-cau-hoi', gloss: 'moi' } },
    { id: 'q3', num: 'Q3', label: 'Nợ chưa lấp', options: [{ v: 'above', label: 'Phía trên' }, { v: 'below', label: 'Phía dưới' }, { v: 'both', label: 'Cả hai' }, { v: 'none', label: 'Không' }], help: { text: 'Single print chưa lấp là mục tiêu ưa thích. Nợ cũ trả trước.', ref: 'sau-cau-hoi' } },
    { id: 'q4', num: 'Q4', label: 'Giá hiện tại đang ở', options: [{ v: 'lvn', label: 'LVN' }, { v: 'hvn', label: 'HVN' }, { v: 'mid', label: 'Giữa' }], help: { text: 'Vào LVN thì giá chạy nhanh qua. Vào HVN thì đi ngang.', ref: 'sau-cau-hoi' } },
    { id: 'q5', num: 'Q5', label: 'Đóng hôm qua so với VA', options: [{ v: 'above', label: 'Trên' }, { v: 'in', label: 'Trong' }, { v: 'below', label: 'Dưới' }], help: { text: 'Ngoài VA là giá đang tìm giá trị mới. Trong VA là cân bằng còn hiệu lực.', ref: 'ma-tran-bias' } },
    { id: 'q6', num: 'Q6', label: 'Âu đã dựng range chưa', options: [{ v: 'yes', label: 'Rồi' }, { v: 'no', label: 'Chưa' }], help: { text: 'Âu dựng range cho phiên Mỹ. Cạnh VA Âu là cạnh mặc định để fade.', ref: 'sau-cau-hoi' } }
  ];
  var vwapOpts = [{ v: 'above', label: 'Trên' }, { v: 'below', label: 'Dưới' }, { v: 'near', label: 'Sát (±2 giá)' }];

  var drawItems = [
    'Chart A: TPO ngày neo phiên COMEX và TPO gộp 3 tuần',
    'Năm mức hôm qua: High, VAH, POC, VAL, Low. Ba VWAP tuần, VWAP ngày',
    'HVN và LVN của ngày và của 3 tuần',
    'Nợ: single print, poor high, poor low',
    'Naked POC',
    'VAH Âu, VAL Âu. IB high, IB low khi đã có'
  ];

  // ===== Điều khiển tầng 3: nhãn + lựa chọn + tiêu chí =====
  var controls = {
    c1: { label: 'Kịch bản', help: { text: 'Chỉ kịch bản đang bật mới chọn được; kịch bản tắt hiện lý do khi bấm.', ref: 'xung-dot' } },
    c3: { label: 'Vùng vào lệnh', help: { text: 'Chọn vùng trong thẻ phiên. Giá phải cách vùng không quá 1 giá.', ref: 'xep-hang-vung' } },
    c2: { label: 'Hướng lệnh', help: { text: 'A, C, D tự điền theo luật. Chỉ B tự chọn: buy hoặc sell.', ref: 'ma-tran-bias' },
      options: [{ v: 'buy', label: 'buy' }, { v: 'sell', label: 'sell' }] },
    c4: { label: 'Bong bóng to gần nhất (10 nến)', help: { text: 'Không vào ngược phe bong bóng khi mức còn giữ (vòng trắng). Mức vỡ (mờ) thì mới được vào ngược.', ref: 'bong-bong-phe', gloss: 'bong-bong' },
      options: [
        { v: 'same', label: 'Cùng phe' },
        { v: 'oppHold', label: 'Ngược phe, còn giữ', bad: true },
        { v: 'oppBroken', label: 'Ngược phe, đã vỡ' },
        { v: 'none', label: 'Không có / giữa move' },
        { v: 'unclear', label: 'Không rõ', bad: true }
      ] },
    c5: { label: 'Giá cách vùng', help: { text: 'Cạnh: cách vùng không quá 1 giá, hoặc râu chạm vùng. Lưng: đã đi từ 3 giá mà chưa hồi.', ref: 'canh-hay-lung' },
      options: [
        { v: 'near', label: 'Không quá 1 giá, hoặc râu chạm' },
        { v: 'mid', label: 'Hơn 1, chưa tới 3 giá' },
        { v: 'far', label: 'Từ 3 giá (ở lưng)', bad: true }
      ] },
    c6: { label: 'Biên độ nến M1 cao nhất trong 5 nến (giá)', unit: 'giá', help: { text: 'Gõ độ dài của nến (cao trừ thấp), không gõ mức giá. Đây là sàn nhiễu của SL: khoảng SL không được nhỏ hơn con số này.', ref: 'luat-sl' } },
    c7dma: { label: 'DMA', help: { text: 'DMA đi ngang khi giá còn chạy nghĩa là đà đang cạn.', ref: 'kb-b', gloss: 'dma' },
      options: [{ v: 'flat', label: 'Đi ngang' }, { v: 'sloped', label: 'Còn dốc', bad: true }] },
    c7move: { label: 'Move vừa rồi', unit: 'giá', help: { text: 'Trap cần một move rõ từ 5 giá trở lên cùng chiều bias.', ref: 'kb-d', gloss: 'trap' } },
    c7deep: { label: 'Nhịp hồi đã quá 70 % move', help: { text: 'Hồi quá 70 % thì không còn là hồi, không gọi trap.', ref: 'kb-d', gloss: 'trap' },
      options: [{ v: 'no', label: 'Chưa' }, { v: 'yes', label: 'Rồi', bad: true }] },
    b1: { label: 'Nhịp hồi là U hay V', help: { text: 'U là phe hồi yếu, nhịp hồi từ 3 nến, không nến nào dài bằng nến dài nhất của move. V là phe hồi đang thắng.', ref: 'v-hay-u' },
      options: [{ v: 'U', label: 'U' }, { v: 'V', label: 'V', bad: true }, { v: 'unclear', label: 'Không rõ', bad: true }],
      criteria: ['U: từ 3 nến M1, thoải, delta hồi yếu dần', 'V: bật dốc bằng lúc rơi, nến dài, delta ngược'] },
    b2: { label: 'Thân nến và delta 3 nến cuối', help: { text: 'Hấp thụ chỉ khi cả thân và độ lớn delta giảm dần qua 3 nến. Tăng dần là đà.', ref: 'than-delta' },
      options: [{ v: 'down', label: 'Giảm dần' }, { v: 'mixed', label: 'Lẫn lộn' }, { v: 'up', label: 'Tăng dần', bad: true }, { v: 'unclear', label: 'Không rõ', bad: true }] },
    b3: { label: 'Nến xác nhận đạt chuẩn', help: { text: 'Mỗi kịch bản có tiêu chí riêng ở dòng nhỏ bên dưới. Chưa đóng nến thì chọn chưa.', ref: 'xung-dot' },
      options: [{ v: 'ok', label: 'Đạt' }, { v: 'not', label: 'Chưa' }, { v: 'unclear', label: 'Không rõ', bad: true }],
      criteria: {
        A: ['Đóng theo chiều phá, thân từ nửa biên độ', 'Delta cùng dấu', 'Tại cạnh: delta cùng chiều phá, hoặc hấp thụ phe ngược'],
        B: ['Ngược chiều move', 'Delta đảo dấu, từ ½ delta nến lớn nhất của move'],
        C: ['Râu xuyên cạnh rồi đóng lại trong', 'Thân không ngắn, râu ngược không dài', 'Delta ủng hộ'],
        D: ['Đỉnh hồi có bong bóng hấp thụ phe hồi, hoặc nến hồi delta thuận đóng dưới nửa thân', 'Nến xác nhận đóng theo chiều cũ, thân dài, delta cùng dấu']
      } },
    b4: { label: 'Giá vào, SL, TP', help: { text: 'Gõ giá vào và SL. TP gợi ý sẵn theo R mục tiêu hoặc vùng kế tiếp, nếu gần hơn.', ref: 'tp-be' } },
    b5: { label: 'SL đúng chỗ', help: { text: 'SL lai: cấu trúc cộng 0,3 giá đệm. Sau đó kiểm sàn nhiễu và trần 4 giá.', ref: 'luat-sl' },
      options: [{ v: 'right', label: 'Đúng chỗ' }, { v: 'unsure', label: 'Chưa chắc' }, { v: 'wrong', label: 'Sai chỗ', bad: true }],
      criteria: {
        A: 'Sau râu nến xác nhận hoặc mép xa của vùng, cái nào xa hơn, cộng 0,3 giá',
        B: 'Sau cực trị cụm hấp thụ cộng 0,3 giá, không đặt ở giữa cụm',
        C: 'Sau râu phá hụt cộng 0,3 giá',
        D: 'Sau đỉnh nhịp hồi cộng 0,3 giá'
      } }
  };

  var closeReasons = [
    { v: 'absorb', label: 'Hấp thụ ngược đe dọa TP' },
    { v: 'flat', label: 'Đóng sạch trước tin' },
    { v: 'other', label: 'Khác (tính là phá luật)' }
  ];

  var qd = {
    'QĐ-1': 'Cân bằng thì hấp thụ chỉ tại vùng cạnh, hoặc vùng hạng 1–2 trùng cạnh (cách không quá 1 giá).',
    'QĐ-3': 'Hấp thụ cần vùng hạng 1–2; cụm POC là hạng 2 chưa đo.',
    'QĐ-9': 'Ngược bias chỉ được hấp thụ tại tail thật hoặc single print đúng phía, cỡ ½, TP 2R, kèm lý do.',
    'QĐ-19': 'Trước {nyse} không tắt kịch bản, chỉ cảnh báo và giảm cỡ còn ½.'
  };
  var unmeasured = 'quyết định của công cụ, chưa đo';

  var phases = { day: 'Ban ngày', prep: 'Chuẩn bị', comex: 'COMEX mở', news: 'Giờ tin', nyse: 'NYSE mở', core: 'Lõi giao thoa',
    ldnclose: 'London đóng', thin: 'Mỏng dần', settle: 'Chốt giá ngày', maint: 'Globex bảo trì', end: 'Ban ngày' };
  var bands = { fake: 'Phá giả', open: 'Mở ảo', real: 'Cú phá đáng tin' };
  var notices = {
    US_WINTER: 'Mỹ đang giờ mùa đông: các mốc ET muộn thêm 1 giờ (+1h).',
    US_SWITCH: 'Hôm nay Mỹ đổi giờ. Đổi neo session TPO / SessionZones từ 19:20 sang 20:20; IB = 20:20–21:20.',
    US_SWITCH_BACK: 'Hôm nay Mỹ trở lại giờ mùa hè. Đổi neo session TPO / SessionZones từ 20:20 về 19:20; IB = 19:20–20:20.',
    LDN_SWITCH: 'London đổi giờ mùa đông: mốc London đóng muộn thêm 1 giờ.',
    LDN_SWITCH_BACK: 'London trở lại giờ mùa hè: mốc London đóng về như cũ.'
  };
  var journal = {
    c4: { same: 'giữ', oppHold: 'NGƯỢC', oppBroken: 'vỡ', none: 'không có', unclear: '?' },
    b2: { down: 'giảm', mixed: 'lẫn', up: 'tăng', unclear: '?' },
    edgeNear: 'cạnh', edgeBack: 'lưng', strong: 'nến mạnh', paper: '(luyện mắt)',
    warnPrefix: 'phạm', and: 'và', slLaw: 'luật SL', section: 'mục',
    mdTitle: 'Sổ đêm', mdHead: '| giờ | hướng | tên | chế độ | 4 kiểm tra (V/U · bb · Δ · cạnh) | SL | R |', mdWarn: '⚠ dòng',
    mdCard: 'Thẻ phiên', mdBias: 'BIAS', mdVwap: 'VWAP tuần', mdClose: 'Đóng hôm qua so với VA', mdShape: 'Hình hôm qua', mdZones: 'Vùng', mdPlan1: 'Kế hoạch 1', mdPlan2: 'Kế hoạch 2', mdCancel: 'Hủy khi', mdMode: 'Chế độ',
    machine: 'Máy cộng', you: 'Bạn cộng', breaks: 'Lệnh phá luật', swept: 'SL bị quét rồi tới TP'
  };
  var errors = { BAD_JSON: 'Tệp không phải JSON hợp lệ.', NO_NIGHTS: 'Không thấy dữ liệu các đêm trong tệp.' };

  var ui = {
    // --- chung ---
    appTitle: 'Trạm Đêm Vàng', skip: 'Bỏ qua, tới nội dung chính', yes: 'Có', no: 'Không', notYet: 'Chưa', cancel: 'Hủy', confirm: 'Đồng ý', close: 'Đóng',
    on: 'Bật', off: 'Tắt', remove: 'Xóa', add: 'Thêm', helpLabel: 'Trợ giúp', helpLink: 'Mở mục này trong Hệ thống Đêm Vàng',
    biasBuy: 'BUY', biasSell: 'SELL', biasNone: 'KHÔNG', biasWait: 'CHỜ', biasUnknown: 'chưa đủ dữ liệu',
    sideUpper: 'phía trên', sideUpperOpt: 'Phía trên', sideLowerOpt: 'Phía dưới', sideLower: 'phía dưới', dirUp: 'lên', dirDown: 'xuống', thinUp: 'Trend lên', thinDown: 'Trend xuống', overridden: '(ghi đè)',
    unitGia: 'giá', newVersion: 'Có bản mới.', reload: 'Tải lại',
    // --- thanh trạng thái ---
    clock: '{hm} VN', nextWindow: 'Cửa sổ cấm kế: {hm} ({min}′)', inWindow: 'TRONG CỬA SỔ CẤM {hm} — còn {left}′', noWindow: 'Hết cửa sổ cấm trong đêm',
    biasChip: 'BIAS {v}', chipBreaks: 'Phá luật {n}/2', chipStreak: 'SL liên tiếp {n}/3', chipOpen: 'Lệnh mở {n}/1', chipOpenPaper: 'Lệnh mở {n}/1 (luyện mắt)', chipZone: 'Đã vào {n}/2 lần ở vùng này',
    // --- thẻ phiên ---
    cardTitle: 'Thẻ phiên', cardDate: 'Ngày', cardVwap: 'VWAP tuần', cardClose: 'Đóng hôm qua', cardShape: 'Hình hôm qua', cardBias: 'BIAS', cardMode: 'Chế độ',
    cardZones: 'VÙNG', cardDebt: 'NỢ', cardBanned: 'VÙNG CẤM', cardNote: 'Kịch bản nền', cardPlan1: 'Kế hoạch 1', cardPlan2: 'Kế hoạch 2', cardCancel: 'Hủy khi',
    cardNone: '—', cardLocked: 'Đã chốt lúc {hm}', cardNotLocked: 'Chưa chốt', cardEdits: '{n} lần sửa', cardToggle: 'Thẻ phiên',
    // --- tầng 0 ---
    t0Lead: 'Làm trước 18:00, khi chưa mở chart. Ba việc: tình trạng của bạn, cửa sổ cấm tối nay, kịch bản nền.',
    t0Title1: 'Tình trạng của bạn', t0Alert: 'Tỉnh táo, không bực dọc, không mệt rã rời',
    t0ViewOnly: 'Cả đêm chỉ xem: ENTRY hiện xám, không vào lệnh thật. Bạn vẫn ghi kèo luyện mắt để có số R.',
    t0Title2: 'Cửa sổ cấm tối nay', t0WinHelp: 'Cửa sổ cấm chặn mọi kịch bản. Giờ tự dịch +1h khi Mỹ hoặc London sang giờ mùa đông.',
    windowLabel: '{hm} (−{before}′ / +{after}′) · hạng {rank}', offAt: 'đã tắt lúc {hm}',
    offConfirmTitle: 'Tắt cửa sổ cấm?', offConfirmText: 'Tắt cửa sổ {hm} sẽ ghi vết giờ tắt. Chắc chắn?', offConfirmOk: 'Tắt cửa sổ',
    nyseRow: 'NYSE mở {hm} (±5′): chỉ cảnh báo, không đánh tin', alwaysOn: 'luôn bật',
    addWindow: 'Thêm cửa sổ', timePh: 'giờ VN (hh:mm)', rank1: 'Hạng 1', rank2: 'Hạng 2', minBefore: 'phút trước', minAfter: 'phút sau', addFomc: 'Thêm FOMC 01:00',
    badTime: 'Giờ chưa đúng dạng giờ:phút.', autoOn: '(tự bật)', t0WinNote: 'Mặc định: {b} ±5′ luôn bật. {a} ±15′ tự bật vào thứ Năm, ngày có tin lớn, hoặc khi chưa xong tầng 0. Có FOMC thì đóng sạch trước {fomcFlat}.',
    t0Title3: 'Ngày tin và kịch bản nền', newsDay: 'Hôm nay có tin lớn (NFP, CPI)', t0Note: 'Kịch bản nền ban ngày (tùy chọn)', t0NotePh: 'Một dòng',
    t0Done: 'Xong tầng 0 — sang kẻ vùng',
    // --- tầng 1 ---
    t1Lead: 'Kẻ vùng trên chart A rồi chốt thẻ phiên. Không có thẻ phiên thì không có lệnh.',
    t1Title1: '1a · Kẻ trên chart (tick khi đã kẻ xong)', t1Title2: '1b · Sáu câu hỏi trên chart A',
    vwapQ: 'Giá hiện tại so với VWAP tuần', vwapHelp: 'Sát nghĩa là cách VWAP tuần không quá 2 giá. Sát thì bias CHỜ.',
    recheck: 'Chốt lại bias: đã có 1 nến M5 đóng rõ', rcAbove: 'Phía trên', rcBelow: 'Phía dưới', editRecheck: 'Chốt lại bias sau nến M5',
    t1Title3: '1c · Bias', t1BiasHelp: 'Bias chỉ lấy từ VWAP tuần và giá đóng hôm qua so với VA. Ghi đè được nhưng phải có lý do.',
    biasIs: 'Bias', autoWas: '(tự động: {v})', overrideTitle: 'Ghi đè bias (cần lý do)', overridePh: 'Lý do ghi đè', overrideNeed: 'Chưa có lý do thì bias vẫn là bias tự động.',
    editOverride: 'Ghi đè bias', editOverrideReason: 'Lý do ghi đè bias',
    t1Title4: '1d · Vùng ({n}/5)', t1ZoneHelp: 'Chọn 3–5 vùng. Hạng và cờ của vùng tự suy theo loại.',
    price: 'Giá', priceTo: 'đến giá', zoneType: 'Loại vùng', addZone: 'Thêm vùng', needPrice: 'Nhập giá của vùng.', zonesFull: 'Đã đủ 5 vùng.',
    zonesFew: 'Dưới 3 vùng: vẫn chốt được, nhưng ít chỗ để vào.', noZones: 'Chưa có vùng nào.',
    addedZone: 'Thêm vùng {t}', editZone: 'Sửa vùng {z}', delZone: 'Xóa vùng {z}', editQ: '{q}: {v}',
    t1Title5: '1e · Kế hoạch và chốt thẻ', plan1: 'Kế hoạch 1 (nếu … thì …)', plan2: 'Kế hoạch 2', cancelWhen: 'Hủy kế hoạch khi …',
    t1CardHelp: 'Thẻ phiên chốt xong mới mở tầng 3. Sau {comex} mỗi lần sửa thẻ đều ghi vết.',
    lockCard: 'Chốt thẻ phiên', lockNeed: 'Còn thiếu: {list}', need_q1: 'Q1 (hình hôm qua)', need_q5: 'Q5 (đóng hôm qua so với VA)', need_q6: 'Q6 (Âu dựng range)', need_vwapW: 'VWAP tuần', need_zones: 'ít nhất 1 vùng',
    lockWhy: 'Chưa chốt thì tầng 3 khóa.', locked: 'Đã chốt thẻ phiên.', toTier2: 'Sang tầng 2', editAfterLock: 'Sau chốt vẫn sửa được; sửa sau {comex} sẽ ghi vết.',
    // --- tầng 2 ---
    t2Lead: 'Gọi tên chế độ trước khi gọi tên kịch bản. Cùng một tín hiệu M1 mang nghĩa trái ngược tùy chế độ.',
    t2Title1: 'Chế độ thị trường', t2Mode: 'Chế độ', t2ModeHelp: 'Phá chỉ được công nhận khi có nến M5 đóng ngoài cạnh và nhịp hồi giữ được. Thiếu bước 2 thì chỉ là chạm.',
    modeBalancedSub: 'fade cạnh, hấp thụ tại cạnh', modeBrokenSub: 'phá hồi, hấp thụ theo chiều', modeThinSub: 'không cản tàu',
    thinDir: 'Hướng Trend thin', thinDirNeed: 'Chọn hướng Trend thin.',
    boDir: 'Hướng phá', breakUp: 'Phá lên', breakDown: 'Phá xuống', boEdge: 'Cạnh vừa phá', boEdgeHelp: 'Chọn từ thẻ phiên. Phá hồi sẽ tự điền vùng này.',
    boAt: 'Giờ phá', boNth: 'Lần phá thứ {n}', boNthHint: 'Lần 1 chui lại ⇒ không đuổi, chờ lần 2.',
    boStep1: 'Bước 1: có 1 nến M5 đóng ngoài cạnh', acceptHelp: 'Công nhận cú phá cần hai bước: nến M5 đóng ngoài cạnh, rồi nhịp hồi về cạnh giữ được.',
    boStep2: 'Bước 2: nhịp hồi giữ được cạnh', needStep1: 'Cần bước 1 trước', boFailed: 'Chui lại trong (phá hụt)', boNeed: 'Chọn hướng phá và cạnh vừa phá.',
    effective: 'Chế độ hiệu lực',
    t2Title2: 'Nến dài nhất phiên', longestBar: 'Vừa có nến dài nhất phiên', reopenAt: 'Mở lại {hm}', clearLongest: 'Bỏ khóa',
    longestHint: 'Ba nến sau nến dài nhất: không kịch bản nào được bật. Chờ hồi; không hồi thì bỏ.',
    t2LongestHelp: 'Sau nến dài nhất phiên (bất kỳ chiều), công cụ khóa ba phút. Hết khóa mới xét kèo.',
    t2Title3: 'Kịch bản nào đang bật', enabled: 'bật', tableNote: 'Công cụ duyệt từng hàng của bảng bật kịch bản; mã đầu tiên tắt là mã hiển thị.',
    t2TableHelp: 'Mỗi kịch bản có điều kiện chế độ riêng. Cú phá chưa công nhận thì phá hồi chưa bật.', toTier3: 'Sang tầng 3 — kèo',
    lock_NO_CARD: 'Chưa chốt thẻ phiên — không có thẻ thì không có lệnh.', lock_BIAS_WAIT: 'Bias đang CHỜ — chốt lại bias ở tầng 1 trước.',
    lock_OPEN_TRADE: 'Đang có lệnh mở — tầng 3 khóa cho tới khi đóng lệnh.', lock_NO_OPEN: 'Chưa có lệnh nào đang mở.',
    lockGo_NO_CARD: 'Về tầng 1', lockGo_BIAS_WAIT: 'Về tầng 1', lockGo_OPEN_TRADE: 'Sang tầng 4',
    // --- tầng 3 ---
    tabLabel: 'Hai bước của kèo', tabCanh: 'Canh', tabBam: 'Bấm', canhHint: 'Trước khi nến xác nhận đóng.', bamHint: 'Sau khi nến xác nhận đóng.',
    newSetup: 'Kèo mới', newSetupDone: 'Đã xóa kèo, bắt đầu lại.', idleNote: 'Đã hơn 10′ không thao tác — nến M1 đã khác, kiểm lại.',
    offShort: 'tắt', pickScenario: 'Chọn một kịch bản đang bật để bắt đầu.', scenSummary: '{name} · mục tiêu {tp} · be {be}', scenImgAlt: 'Ví dụ kịch bản {name}',
    c3NoEdge: 'Chưa chọn cạnh vừa phá ở tầng 2', autoFilled: '(tự điền)', nthAt: 'Lần thứ {n} tại vùng', sideNone: 'chưa có hướng',
    counterBias: 'Ngược bias: {tp}', counterOk: 'được phép, cỡ ½, TP 2R', counterBad: 'không được phép', counterPh: 'Lý do ngược bias', c4numPh: '±số',
    entryL: 'Giá vào', slL: 'SL', tpL: 'TP', tpAuto: 'gợi ý', c6Again: 'Biên độ nến M1 cao nhất (sửa tại đây)',
    calcNone: 'Chọn kịch bản để tính SL và R:R.', calcNeed: 'Nhập giá vào và SL ở bước Bấm.', calcSl: 'SL {v} giá', calcRr: 'R:R 1:{v}', calcTpSug: 'TP gợi ý {v}',
    sizeTitle: 'Cỡ lệnh MGC', sizeNoCfg: 'chưa cài vốn', sizeZero: '0 hợp đồng', sizeN: '{n} hợp đồng',
    sizeCalc: 'Vốn {cap} $ · rủi ro {pct} % = {usd} $. Mỗi hợp đồng rủi ro {per} $ với SL này. Làm tròn xuống.', sizeHalf: 'Đã giảm ½ vì: {why}.',
    dotsLabel: '{n} trên 8 điều kiện đã đạt', vWait: 'CHỜ', missingLabel: 'thiếu:', vNo: 'KHÔNG VÀO', vOff: 'TẮT MÁY', vLocked: 'Có lệnh mở.', moreCodes: '(+{n} lý do nữa)',
    forceBtn: 'Tôi vẫn vào (phá luật)', forceNeed: 'Cần có hướng, giá vào và SL trước.', entryView: 'ENTRY (chỉ xem)', paperBtn: 'Ghi kèo luyện mắt', enterBtn: 'Vào lệnh',
    slGia: '{v} giá', sizeHalfShort: 'cỡ ½', sizeFull: 'cỡ đủ', counterTag: 'ngược bias · 2R · ½', halfNote: 'Cỡ ½ vì: {why}.',
    enterTitle: 'Vào lệnh', enterKind: 'Kiểu vào', enterPrice: 'Giá', enterMarketHint: 'market: khớp ngay, giá khớp thật là giá vào.',
    enterLimitHint: 'limit: để giá chờ; khi khớp bấm "Khớp rồi", giá bỏ đi thì hủy.', enterConfirm: 'Xác nhận vào lệnh',
    entered: 'Đã ghi lệnh vào sổ.', enteredPaper: 'Đã ghi kèo luyện mắt.', forcedToast: 'Đã ghi lệnh phá luật vào sổ.',
    forceTitle: 'Vào lệnh phá luật?', forceText: 'Phán quyết đang là: {list}.', forceCount: 'Lệnh này tính là phá luật; 2 lệnh phá luật thì tắt máy.',
    forcePaperNote: 'Đang ở chế độ chỉ xem nên không tính phá luật.', forceOk: 'Vẫn vào, chấp nhận phá luật',
    editWhileSetupTitle: 'Đang canh kèo', editWhileSetupText: 'Sửa thẻ lúc này là nắn kế hoạch theo kèo. Vẫn sửa và ghi vết?', editWhileSetupOk: 'Vẫn sửa',
    // --- tầng 4 ---
    t4None: 'Chưa có lệnh nào đang mở.', t4Last: 'Lệnh đóng gần nhất', t4Title: 'Lệnh đang mở', openPaper: 'luyện mắt', ruleBreakFlag: 'phá luật',
    kvEntry: 'Giá vào', kvPending: 'chờ khớp ở {v}', kvSl: 'SL', beDone: 'SL đã về hòa vốn (be)', beReminder: 'Đã dời SL về hòa vốn (be): kéo SL trên sàn về {entry} ngay, công cụ không tự sửa lệnh trên sàn.', beMoveTo: '{sl} → {entry}', kvTp: 'TP', kvRr: 'R:R dự kiến', kvSize: 'Số hợp đồng', kvTime: 'Giờ vào',
    noSlEdit: 'Sau khi vào không đổi SL. Chỉ dời SL về giá vào (hòa vốn, gọi tắt be) khi giá đạt mốc dưới đây.', flatBefore: 'Đóng sạch trước {hm} (còn {min}′).', maintNote: 'Tới giờ Globex bảo trì: đóng sạch lệnh.',
    t4Pending: 'Chờ khớp', fillPrice: 'Giá khớp thật', filled: 'Khớp rồi', cancelLimit: 'Hủy — giá bỏ đi', cancelledToast: 'Đã hủy limit, xóa dòng sổ.',
    t4Live: 'Đang chạy', curPrice: 'Giá hiện tại', rNow: 'R hiện tại {r}', rNowNone: 'Nhập giá hiện tại để thấy R', beRule: 'Mốc dời về hòa vốn (be): +{r}R, tại giá {price}.',
    outsideBar: 'Đã có 1 nến M1 đóng ngoài vùng vào', moveBe: 'Đã dời SL về hòa vốn', beNeedDone: 'Chỉ chọn "Về hòa" sau khi đã dời SL về hòa vốn.',
    t4BeHelp: 'Phá hồi và hấp thụ dời về hòa ở +1,5R; fade và trap ở +1R. Be sớm hơn thì lệnh thắng hay thành hòa.',
    t4Close: 'Đóng lệnh', closeTp: 'Chạm TP', closeSl: 'Chạm SL', closeBe: 'Về hòa vốn', closeManual: 'Đóng tay', exitPrice: 'Giá thoát', rSuggest: 'R gợi ý:',
    manualReason: 'Lý do đóng tay', manualHelp: 'Chỉ đóng tay khi hấp thụ ngược chiều đe dọa TP, hoặc để đóng sạch trước tin. Râu dài, sốt ruột không phải lý do.',
    manualBreak: 'Lý do "khác" tính là phá luật.', closeConfirm: 'Xác nhận đóng', closedToast: 'Đã đóng lệnh và cập nhật sổ.',
    swept: 'SL bị quét rồi giá tới TP', tradeNote: 'Ghi chú',
    // --- tầng 5 ---
    t5Tonight: 'Đêm {key}', t5Help: 'Sổ 7 cột ghi trước khi bấm. Dòng ⚠ nêu luật đã phạm.',
    jh1: 'giờ', jh2: 'hướng', jh3: 'tên', jh4: 'chế độ', jh5: '4 kiểm tra', jh6: 'SL', jh7: 'R',
    warnRow: '⚠ dòng {time} {w}', noTrades: 'Chưa có lệnh nào đêm nay.', machineSum: 'Máy cộng: {r} R', yourSum: 'Bạn cộng tay (để đối chiếu máy)', mismatch: 'Lệch so với máy cộng — kiểm lại từng lệnh',
    breaksN: 'Lệnh phá luật: {n}', sweptN: 'SL bị quét rồi tới TP: {n}', endNight: 'Kết phiên', endNeed: 'Cần nhập "Bạn cộng" trước.', endedToast: 'Đã kết phiên.',
    afterClose: 'Sau đóng lệnh: SL bị quét, ghi chú',
    t5Week: 'Cuối tuần: 4 con số', t5WeekHelp: 'Chỉ số theo dõi duy nhất của tuần là số lệnh phá luật. Lãi lỗ chỉ là hệ quả.',
    wBreaks: 'Phá luật / tổng lệnh', wSwept: 'SL bị quét rồi tới TP', wByScen: 'R theo kịch bản', wByZone: 'R theo loại vùng', wCounter: 'Lệnh ngược bias', wStreak: 'Chuỗi đêm 0 phá luật',
    pairFmt: '{name} {n} lệnh {r} R',
    t5Export: 'Xuất và nhập', exMd: 'Tải Markdown', exMdCopy: 'Sao chép Markdown', exJson: 'Tải JSON', exCsv: 'Tải CSV', copied: 'Đã sao chép.', copyFail: 'Không sao chép được.',
    importJson: 'Nhập JSON (gộp vào dữ liệu hiện có)', importDone: 'Nhập xong: {a} đêm mới, {b} đêm gộp, {c} lệnh thêm.', exportDue: 'Cuối tuần rồi — tải JSON về để giữ bản sao.',
    t5Settings: 'Cài đặt', setTheme: 'Giao diện', themeDark: 'Tối', themeLight: 'Sáng', setGuide: 'Mức hướng dẫn', guideNew: 'Mới', guideQuen: 'Quen',
    setCapital: 'Vốn', setRisk: 'Rủi ro mỗi lệnh', setDst: 'Mốc giờ dịch theo giờ mùa đông', setDstHelp: 'Tắt thì mọi mốc luôn theo giờ mùa hè.',
    setKeys: 'Phím tắt tầng 3', keysHelp: 'Bấm ? để xem danh sách phím tắt.', wipe: 'Xóa toàn bộ dữ liệu', wipeTitle: 'Xóa toàn bộ dữ liệu?',
    wipeText: 'Mọi đêm, thẻ phiên và sổ lệnh trên máy này sẽ mất. Nên tải JSON trước.', wipeOk: 'Xóa hết', wiped: 'Đã xóa dữ liệu.', version: 'Phiên bản {v}',
    keysTitle: 'Phím tắt (tầng 3)', key0: 'Chọn kịch bản A', key1: 'Chọn kịch bản B', key2: 'Chọn kịch bản C', key3: 'Chọn kịch bản D', key4: 'Chọn hướng buy / sell (chỉ B)',
    key5: 'Nhịp hồi U / V', key6: 'Nút chính (Vào lệnh)', key7: 'Kèo mới', key8: 'Rời ô nhập, đóng hộp thoại', key9: 'Mở bảng phím tắt',
    // --- vòng 2 ---
    zoneHasTrades: 'Vùng này đã có lệnh trong sổ nên không xóa được (đếm 2 lần mỗi vùng).',
    glossaryBtn: 'Từ điển', glossaryTitle: 'Từ điển', glossaryHint: 'Định nghĩa ngắn các từ hay gặp. Đầy đủ ở trang Hệ thống Đêm Vàng.', openGlossary: 'Mở Từ điển',
    qPrefix: '{n} · {label}',
    vwapNowL: 'Giá hiện tại (tùy chọn)', vwapPriceL: 'VWAP tuần (tùy chọn)', vwapAutoHint: 'Có đủ hai số: tự chọn "{v}".', vwapAutoNeed: 'Gõ cả hai số để tự chọn Trên / Dưới / Sát.',
    planConflict: 'Kế hoạch đang ngược bias {b}. Vẫn chốt được, nhưng vào lệnh ngược bias phải ghi lý do.', planConflictToast: 'Cảnh báo: kế hoạch ngược bias.',
    nightPick: 'Chọn đêm', editsOpen: '{n} lần sửa thẻ', boNeedTop: 'Chưa công nhận: chọn hướng phá, cạnh vừa phá rồi tới bước 1 và bước 2.',
    scenLocked: 'Kịch bản này đang tắt: {why}',
    storeFail: 'Không lưu được vào máy — tải JSON ngay để giữ dữ liệu.', storeFailBtn: 'Tải JSON', otherTab: 'Dữ liệu vừa đổi ở cửa sổ khác — đã tải lại.',
    unitGiaShort: 'giá'
  };

  // ===== Từ điển (định nghĩa ngắn, lấy từ trang Hệ thống Đêm Vàng; chỗ là luật của công cụ thì ghi rõ) =====
  var glossary = [
    { key: 'bias', term: 'bias', def: 'Chiều ưu tiên của đêm: BUY, SELL, KHÔNG hoặc CHỜ. Chỉ lấy từ VWAP tuần và giá đóng hôm qua so với VA hôm qua; ngược bias phải ghi lý do trước khi bấm.' },
    { key: 'no', term: 'nợ', def: 'Phần giá chưa được lấp lại (single print, poor high, poor low), giá hay trở lại chạm. Đây là "nợ giá", không phải nợ tiền.' },
    { key: 'moi', term: 'mồi', def: 'Cực trị có khối lượng dày: trông như đỉnh hoặc đáy nhưng không phải bị từ chối thật, nên không coi là đỉnh hay đáy. Ví dụ: đỉnh 4210,0 chỉ 1 TPO, khối lượng thấp ⇒ tail thật; đỉnh 4208,0 khối lượng dày ⇒ mồi.' },
    { key: 'tail', term: 'tail thật', def: 'Cực trị chỉ có 1 TPO với khối lượng thấp: giá bị từ chối thật ở đó. Chỉ tail thật mới cho phép hấp thụ ngược bias tại High / Low hôm qua.' },
    { key: 'poor', term: 'poor high / poor low', def: 'Đỉnh hoặc đáy có từ 2 TPO, tức giá chưa bị từ chối dứt khoát. Đó là nợ, sẽ bị chạm lại.' },
    { key: 'thin', term: 'thin', def: 'Profile mỏng, đi một chiều, chưa đấu giá xong: không đánh ngược. Chế độ "Trend thin" là không cản tàu, chỉ vào theo chiều ở nhịp hồi.' },
    { key: 'trap', term: 'trap (bẫy)', def: 'Một move rõ (từ 5 giá) cùng chiều bias, rồi nhịp hồi ngược tới một vùng. Ở đỉnh nhịp hồi phe hồi thử mà thất bại: bong bóng hấp thụ phe hồi, hoặc nến hồi có delta thuận mà đóng dưới nửa thân. Vào theo chiều move cũ, mục tiêu 2R. Ví dụ: sell, giá giảm từ 4200 xuống 4194 (6 giá), hồi lên 4197 (nửa move, dưới 70 %) rồi thất bại ⇒ sell, SL trên 4197 cộng 0,3 giá.' },
    { key: 'bong-bong', term: 'bong bóng', def: 'Vòng tròn trên chart M1 (chỉ báo hấp thụ và chỉ báo lệnh lớn). Tròn đặc là hấp thụ: một phe đánh market mạnh tại mức đó mà giá không đi; vòng trắng là mức còn giữ, mờ đi là mức đã vỡ. Tròn mờ có số từ 100 là lệnh lớn vừa vào; giá không rời mức thì mức đó thành vùng phòng thủ. Chỉ để kiểm tra, không phải tín hiệu vào lệnh.' },
    { key: 'dma', term: 'DMA', def: 'Chỉ báo đường trên chart M1 dùng để đọc đà (trang Hệ thống không ghi tên đầy đủ). Dốc cùng chiều move là đà còn; đi ngang khi giá còn chạy là đà đang cạn. Chỉ để kiểm tra, không phải tín hiệu vào lệnh.' },
    { key: 'be', term: 'be (hòa vốn)', def: 'Dời SL về giá vào để lệnh không lỗ nữa. Phá hồi và hấp thụ dời ở +1,5R sau 1 nến M1 đóng ngoài vùng vào; fade và trap dời ở +1R.' },
    { key: 'hang', term: 'hạng vùng', def: 'Mức ưu tiên của vùng theo phép đo. Hạng 1 là VWAP tuần; hạng 2 (VWAP ngày, HVN tuần, cụm POC) thì hấp thụ đi cỡ ½.' },
    { key: 'canh', term: 'cạnh', def: 'Mép của vùng giá trị Âu hoặc của range: VAH Âu, VAL Âu, IB, cạnh range. Ở câu hỏi "giá cách vùng", ở cạnh là cách vùng không quá 1 giá.' },
    { key: 'acceptance', term: 'acceptance (công nhận cú phá)', def: 'Giá đóng 1 nến M5 ngoài cạnh, rồi nhịp hồi về cạnh giữ được. Thiếu bước 2 thì chỉ là chạm, chưa phải phá.' },
    { key: 'hap-thu', term: 'hấp thụ', def: 'Một phe đánh market mạnh mà giá không đi: nỗ lực có, kết quả không. Chỉ gọi hấp thụ khi cả thân nến và độ lớn delta giảm dần qua 3 nến.' },
    { key: 'pha-hoi', term: 'phá hồi', def: 'Sau cú phá đã được công nhận, giá hồi hình U về cạnh vừa phá rồi đi tiếp theo chiều phá. Mục tiêu 3R.' },
    { key: 'fade', term: 'fade', def: 'Vào ngược hướng giá vừa xuyên cạnh rồi đóng lại trong (phá hụt). Là kịch bản C: cỡ nhỏ, mục tiêu 2R.' },
    { key: 'naked', term: 'naked POC', def: 'POC của phiên trước mà giá chưa chạm lại. Chỉ làm mục tiêu, không dùng để bắt đảo chiều.' },
    { key: 'hvn', term: 'HVN / LVN', def: 'HVN là nút khối lượng cao, giá hay đi ngang; LVN là nút khối lượng thấp, giá chạy nhanh qua. HVN 3 tuần và LVN là vùng cấm fade.' },
    { key: 'sp', term: 'single print', def: 'Mức giá chỉ có 1 TPO, tức giá đi qua rất nhanh. Nếu chưa lấp thì là nợ, và là mục tiêu ưa thích của phiên.' },
    { key: 'ib', term: 'IB', def: 'Biên độ giờ đầu của phiên Mỹ (19:20 đến 20:20 giờ VN khi Mỹ đang giờ mùa hè). IB high và IB low là hai cạnh.' },
    { key: 'vwap', term: 'VWAP tuần', def: 'Giá trung bình theo khối lượng tính từ đầu tuần, là đường mốc cả tuần. Giá cách VWAP tuần không quá 2 giá là "sát": bias CHỜ.' },
    { key: 'mo-ao', term: 'mở ảo', def: 'Hệ thống: khoảng {comex} đến {nyse} vàng hay chạy giả, cú phá chưa đáng tin; cú phá đáng tin thường rơi vào {real1} đến {real2}; trước {nyse} chỉ fade cạnh, cỡ nhỏ. Công cụ: không tắt kịch bản, chỉ giảm cỡ còn ½ (QĐ-19, quyết định của công cụ, chưa đo).' },
    { key: 'r', term: 'R', def: 'R là khoảng rủi ro của lệnh: giá vào trừ SL. Lãi 1R bằng đúng khoảng đó, 3R gấp ba. Ví dụ: sell 4193,0, SL 4195,4 (2,4 giá) thì 1R = 2,4 giá và TP 3R ở 4185,8.' },
    { key: 'hinh-dang', term: 'hình dạng profile (D, P, b, B, thin, chữ nhật)', def: 'D: đấu giá xong, chờ phá. P: cân bằng ở đỉnh, đuôi là hỗ trợ; b ngược lại. B: trang Hệ thống chưa mô tả riêng. thin: mỏng, một chiều, chưa xong, không đánh ngược. Chữ nhật: cân bằng rộng, sẽ phá một đầu.' }
  ];

  // thay {comex} {nyse} {real1} {real2} {fomcFlat} bằng giờ đã dịch theo mùa (xem time.textVars); biến lạ giữ nguyên
  function fill(s, vars) {
    if (!vars || typeof s !== 'string') return s;
    return s.replace(/\{(\w+)\}/g, function (m, k) { return vars[k] === undefined ? m : vars[k]; });
  }

  return {
    fill: fill, glossary: glossary, HT_BASE: HT_BASE, scenarios: scenarios, modes: modes, modeLabels: modeLabels, zoneTypes: zoneTypes, flagText: flagText, tiers: tiers,
    codes: codes, halfText: halfText, warnText: warnText, questions: questions, vwapOpts: vwapOpts, drawItems: drawItems,
    phases: phases, bands: bands, notices: notices, journal: journal, errors: errors,
    controls: controls, closeReasons: closeReasons, qd: qd, unmeasured: unmeasured, ui: ui
  };
});
