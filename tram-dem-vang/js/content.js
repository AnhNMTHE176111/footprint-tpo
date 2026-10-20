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
      blurb: 'Giá tới vùng hạng 1–2, một phe đánh mạnh mà giá không đi. Vào ngược phe bị hấp thụ (theo phe đang hấp thụ) sau nến xác nhận.' },
    C: { name: 'Fade cạnh', short: 'C', img: 'img/kb-c-fade-canh.png', anchor: 'kb-c', target: '2R', be: '+1R',
      blurb: 'Giá phá hụt qua cạnh range rồi đóng lại trong. Vào ngược hướng phá hụt, cỡ nhỏ.' },
    D: { name: 'Trap', short: 'D', img: 'img/kb-d-trap.png', anchor: 'kb-d', target: '2R', be: '+1R',
      blurb: 'Sau một move rõ, phe hồi thử rồi thất bại ở đỉnh nhịp hồi. Vào theo chiều move cũ.' }
  };

  // Loại vùng: nhãn, vai (bảng 2.3 của Hệ thống), định nghĩa 1–2 câu, "dùng thế nào" 1 câu.
  // Một nguồn duy nhất: ô chọn loại vùng ở tầng 1 và Từ điển đều đọc từ đây.
  var zoneTypes = {
    vwapW: { label: 'VWAP tuần', rank: 'hạng 1',
      def: 'Giá trung bình theo khối lượng, tính từ đầu tuần. Đây là đường mốc cả tuần.',
      use: 'Hạng 1: ô duy nhất dương ở cả hai phép đo (khoảng 54%, lệch nhỏ so với 50%). Giá cách không quá 2 giá là "sát": bias CHỜ.' },
    vwapD: { label: 'VWAP ngày', rank: 'hạng 2',
      def: 'Giá trung bình theo khối lượng, tính từ đầu phiên ngày.',
      use: 'Hạng 2: chỉ một phép đo ủng hộ, hấp thụ ở đây đi cỡ ½.' },
    hvnW: { label: 'HVN tuần', rank: 'hạng 2',
      def: 'Nút khối lượng cao của tuần: mức giá giao dịch dày, giá hay đi ngang quanh đó.',
      use: 'Hạng 2 (chưa chắc): chỉ phép đo 1 ủng hộ, phép đo 2 trung tính. Hấp thụ ở đây đi cỡ ½.' },
    pocCluster: { label: 'Cụm POC (từ 2 POC, cách ≤ 1 giá)', rank: 'hạng 2',
      def: 'Từ hai POC (mức giao dịch nhiều nhất của mỗi phiên) nằm cách nhau không quá 1 giá, gộp thành một cụm.',
      use: 'Hạng 2 theo QĐ-3, quyết định của công cụ, chưa đo (Hệ thống không có cụm POC): hấp thụ ở đây đi cỡ ½.' },
    vahEu: { label: 'VAH Âu', rank: 'cạnh',
      def: 'Mép trên của vùng giá trị (VA: vùng quanh POC chứa khoảng 70% khối lượng) của phiên Âu.',
      use: 'Cạnh mặc định để fade khi đang cân bằng. Có 1 nến M5 đóng ngoài thì tắt fade, chờ công nhận cú phá.' },
    valEu: { label: 'VAL Âu', rank: 'cạnh',
      def: 'Mép dưới của vùng giá trị (VA: vùng quanh POC chứa khoảng 70% khối lượng) của phiên Âu.',
      use: 'Cạnh mặc định để fade khi đang cân bằng. Có 1 nến M5 đóng ngoài thì tắt fade, chờ công nhận cú phá.' },
    rangeEdge: { label: 'Cạnh range (chọn phía)', rank: 'cạnh',
      def: 'Mép trên hoặc mép dưới của khoảng giá đi ngang mà phiên Á hoặc Âu đã dựng.',
      use: 'Cạnh để fade khi cân bằng; giữa range không có lệnh. Chọn phía trên hay phía dưới.' },
    ibHigh: { label: 'IB high', rank: 'cạnh',
      def: 'Mép trên của IB, biên độ giờ đầu của phiên Mỹ.',
      use: 'Cạnh dùng để công nhận cú phá (nến M5 đóng ngoài IB). Fade ở IB là quyết định của công cụ, chưa đo.' },
    ibLow: { label: 'IB low', rank: 'cạnh',
      def: 'Mép dưới của IB, biên độ giờ đầu của phiên Mỹ.',
      use: 'Cạnh dùng để công nhận cú phá (nến M5 đóng ngoài IB). Fade ở IB là quyết định của công cụ, chưa đo.' },
    highY: { label: 'High hôm qua', rank: 'cạnh ngoài',
      def: 'Mức giá cao nhất của phiên hôm qua.',
      use: 'Cạnh ngoài. Ngược bias chỉ hấp thụ ở đỉnh có tail thật hoặc single print cũ đúng phía, cỡ ½, 2R, ghi lý do trước.' },
    lowY: { label: 'Low hôm qua', rank: 'cạnh ngoài',
      def: 'Mức giá thấp nhất của phiên hôm qua.',
      use: 'Cạnh ngoài. Ngược bias chỉ hấp thụ ở đáy có tail thật hoặc single print cũ đúng phía, cỡ ½, 2R, ghi lý do trước.' },
    sp: { label: 'Single print (chọn phía)', rank: 'nợ',
      def: 'Dãy mức giá chỉ có 1 TPO nằm giữa profile (ở cực trị thì là tail): giá đi qua rất nhanh. Chưa lấp lại thì là nợ.',
      use: 'Nợ chưa lấp là mục tiêu ưa thích của phiên; nợ cũ trả trước, ngày tăng thì nợ phía trên trả trước. Chọn phía trên hay phía dưới.' },
    poorHigh: { label: 'Poor high', rank: 'nợ',
      def: 'Đỉnh phẳng: mức giá cao nhất có từ 2 TPO, không có tail. Giá chưa bị từ chối dứt khoát ở đó.',
      use: 'Là nợ: giá hay quay lại chạm, nên dùng làm mục tiêu.' },
    poorLow: { label: 'Poor low', rank: 'nợ',
      def: 'Đáy phẳng: mức giá thấp nhất có từ 2 TPO, không có tail. Giá chưa bị từ chối dứt khoát ở đó.',
      use: 'Là nợ: giá hay quay lại chạm, nên dùng làm mục tiêu.' },
    nakedPoc: { label: 'Naked POC', rank: 'chỉ mục tiêu',
      def: 'POC của phiên trước mà giá chưa chạm lại.',
      use: 'Chỉ làm nam châm mục tiêu, không dùng để bắt đảo chiều.' },
    hvnDay: { label: 'HVN ngày', rank: 'chặn hấp thụ',
      def: 'Nút khối lượng cao của ngày: mức giá giao dịch dày trong phiên.',
      use: 'Hệ thống: không gọi hấp thụ ở HVN ngày ngay sau cú phá cực trị (phép đo 1 nghiêng về đi tiếp, phép đo 2 trung tính). Công cụ chặn hấp thụ ở mọi HVN ngày (QĐ-15, quyết định của công cụ, chưa đo).' },
    hvn3w: { label: 'HVN 3 tuần', rank: 'cấm fade',
      def: 'Nút khối lượng cao trên TPO gộp 3 tuần.',
      use: 'Cấm fade và cấm hấp thụ: chỉ làm mục tiêu hoặc vùng phá hồi.' },
    lvn: { label: 'LVN', rank: 'cấm fade',
      def: 'Nút khối lượng thấp: mức giá ít giao dịch, giá chạy nhanh qua.',
      use: 'Cấm fade và cấm hấp thụ ở đây: giá không dừng lại.' }
  };
  var flagText = {
    r1: 'hạng 1', r2: 'hạng 2', edge: 'cạnh', edgeOuter: 'cạnh ngoài', tail: 'tail thật', sp: 'single print',
    noB: 'chặn hấp thụ', banned: 'cấm fade'
  };

  var tiers = [
    { id: 0, name: 'Trước', long: 'Trước khi mở chart' },
    { id: 1, name: 'Vùng', long: 'Kẻ vùng và chốt thẻ phiên' },
    { id: 2, name: 'Setup Entry', long: 'Setup Entry: bốn danh sách kiểm' },
    { id: 3, name: 'Sổ', long: 'Sổ, kết quả lệnh và cài đặt' }
  ];

  // ===== Ô dùng chung cho cả 4 khối =====
  // auto: máy tự điền; ngược lại người tick.
  var common = [
    { id: 'card', label: 'Đã chốt thẻ phiên', auto: true },
    { id: 'news', label: 'Không trong khung giờ cấm', auto: true },
    { id: 'breaker', label: 'Chưa tắt máy', auto: true },
    { id: 'open', label: 'Không có lệnh đang mở', auto: true },
    { id: 'longest', label: 'Không trong 3 nến M1 sau nến dài nhất phiên', tickLabel: 'Vừa có nến dài nhất phiên (3 nến M1 gần nhất)', auto: false,
      help: { text: 'Mặc định tắt. Bật khi vừa có nến dài nhất phiên (bất kỳ chiều): không vào lệnh trong 3 nến M1 kế tiếp. Chờ hồi; không hồi thì bỏ.', ref: 'xung-dot' } }
  ];
  // lý do khi ô dùng chung chưa đạt (có {biến})
  var commonBad = {
    card: 'Chưa chốt thẻ phiên — không có thẻ thì không có lệnh.',
    news: 'Đang trong khung giờ cấm {hm} — còn {left}′.',
    breakerRule: 'Đã 2 lệnh phá luật trong đêm — tắt máy đến hết đêm.',
    breakerSl: 'Đã 3 SL liên tiếp — tắt máy đến hết đêm. Lệnh đóng lỗ từ 0,2R trở lên tính là SL, kể cả đóng tay (quyết định của công cụ, chưa đo).',
    open: 'Đang có lệnh mở — nhập kết quả ở Sổ trước khi vào lệnh mới.',
    longest: 'Vừa có nến dài nhất phiên: chờ 3 nến M1, không hồi thì bỏ.'
  };
  // nhãn các ô còn lại của mỗi khối (dùng trong danh sách thiếu và dòng Sổ)
  var itemLabels = {
    side: 'Hướng', zone: 'Vùng', counter: 'Lý do ngược bias', tail: 'Vùng có tail thật hoặc single print cũ đúng phía',
    bias: 'Bias cho phép kịch bản này', breakHours: 'Cú phá không rơi vào 18:00–{comex}',
    zone2: 'Lần ≤ 2 tại vùng'
  };
  var autoBad = {
    zone2: 'Đã vào 2 lần ở vùng này — không có lần thứ ba.',
    counter: 'Ngược bias {bias}: ghi lý do ở ô bên dưới trước khi vào (luật cứng, mục 2.2).',
    biasNone: 'Bias KHÔNG: chỉ fade hai cạnh VA Âu (khối C), mục tiêu 2R, cỡ ½. Không phá hồi.',
    biasWait: 'Bias CHỜ: chờ 1 nến M5 đóng rõ một phía rồi chốt lại bias ở tầng 1. Chưa khối nào vào được.',
    biasCounter: 'Ngược bias {bias}: chỉ khối B được ngược, tại tail thật hoặc single print cũ đúng phía, 2R, cỡ ½.',
    breakHours: 'Cú phá lúc {hm} rơi vào 18:00–{comex}: hay là phá giả. Nghi trước, tin sau.',
  };

  var halfText = {
    BIAS_NONE: 'bias KHÔNG', SCENARIO_C: 'fade cạnh (C)', COUNTER_BIAS: 'ngược bias (2R)', NEWS_DAY: 'ngày có tin lớn (quyết định của công cụ)',
    B_RANK2: 'vùng hạng 2', BEFORE_2030: 'trước {nyse} (hay mở ảo)'
  };
  var warnText = {
    WARN_NYSE: 'NYSE mở — không đánh tin.',
    WARN_BEFORE_2030: 'Trước {nyse} vàng hay mở ảo (cú phá chưa đáng tin): cỡ ½.',
    WARN_FEW_ZONES: 'Thẻ có dưới 3 vùng — vẫn chốt được, nhưng ít chỗ để vào.',
    WARN_FX_NEWS: 'Tin EUR / GBP mức cao — vàng có thể giật, không đánh tin.'
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

  // ===== Bốn khối Setup Entry: chữ checkbox bám Hệ thống mục 3.1, 4, 5, 6 =====
  // t: câu hiển thị (một dòng) · short: chữ rất ngắn cho cột "4 kiểm tra" của Sổ · help: định nghĩa khi bấm "?"
  var HELP = {
    accept: { text: 'Công nhận cú phá cần ba bước: (1) nến M5 đóng ngoài cạnh; (2) nhịp hồi về cạnh giữ được, không nến M5 nào đóng ngược vào; (3) tại cú test lại trên M1 có delta cùng chiều phá, hoặc hấp thụ ngược chiều phá. Thiếu bước 2 thì chỉ là chạm.', ref: 'acceptance', gloss: 'acceptance' },
    step1: { text: 'Bước 1 của công nhận cú phá: nến M5 đóng ngoài cạnh VA Âu hoặc IB. "Hoặc vùng đã kẻ" là mở rộng của công cụ theo ca 6/10 (phá cụm POC), chưa đo.', ref: 'acceptance', gloss: 'acceptance' },
    step3: { text: 'Bước 3 của công nhận cú phá: tại cú test lại, delta cùng chiều phá, hoặc phe ngược đánh mạnh mà bị hấp thụ.', ref: 'acceptance', gloss: 'acceptance' },
    uv: { text: 'U là phe hồi yếu: từ 3 nến M1, thoải, delta hồi yếu dần, không nến nào dài bằng nến dài nhất của move. V là phe hồi đang thắng.', ref: 'v-hay-u', gloss: 'hinh-dang' },
    bubble: { text: 'Bong bóng đặc, hoặc mờ có số từ 100, ở cực trị gần nhất trong 10 nến. Không vào ngược phe bong bóng khi mức còn giữ (vòng trắng); mức vỡ (mờ) thì mới được vào ngược. Bong bóng ở giữa move: bỏ qua.', ref: 'bong-bong-phe', gloss: 'bong-bong' },
    absorb: { text: 'Hấp thụ chỉ khi cả thân nến và độ lớn delta giảm dần qua 3 nến. Tăng dần là đà.', ref: 'than-delta', gloss: 'hap-thu' },
    confirmB: { text: 'Nến xác nhận có delta ngược dấu, độ lớn từ ½ |delta| của nến lớn nhất trong move. Luật cơ chế để không vào ở lưng, chưa đo (HT mục 10).', ref: 'than-delta', gloss: 'hap-thu' },
    dma: { text: 'DMA đi ngang khi giá còn chạy nghĩa là đà đang cạn.', ref: 'kb-b', gloss: 'dma' },
    trap: { text: 'Phe hồi thử ở đỉnh nhịp hồi mà thất bại: bong bóng hấp thụ phe hồi, hoặc nến hồi có delta theo chiều hồi nhưng đóng ở nửa ngược chiều hồi (hồi lên thì đóng ở nửa dưới).', ref: 'kb-d', gloss: 'trap' },
    edge: { text: 'Cạnh là mép của VA Âu hoặc của range. Ở cạnh là cách vùng không quá 1 giá, hoặc râu nến xác nhận chạm vùng. Đi từ 3 giá trở lên khỏi vùng mà chưa hồi là ở lưng: bỏ kèo.', ref: 'canh-hay-lung', gloss: 'canh' },
    near: { text: 'Giá không quá 1 giá cách vùng là đạt. Từ 1 đến 3 giá chỉ đạt khi râu nến xác nhận chạm vùng. Từ 3 giá trở lên là ở lưng: bỏ kèo.', ref: 'canh-hay-lung', gloss: 'canh' },
    sl: { text: 'Luật SL (HT mục 6), bạn tự kiểm, công cụ không tính và không chặn ENTRY: (1) vị trí: sau cấu trúc của kịch bản cộng 0,3 giá; (2) sàn nhiễu: SL không ngắn hơn nến M1 lớn nhất trong 5 nến; (3) trần: SL không quá 4 giá. R:R ít nhất 1:2 tính trước; TP 3R cho A, B (B ngược bias: 2R), 2R cho C, D, hoặc vùng kế tiếp nếu gần hơn (C: cạnh đối diện hoặc POC).', ref: 'luat-sl', gloss: 'luat-sl' },
    fadeWick: { text: 'Phá hụt: râu xuyên cạnh rồi nến đóng lại trong. Không có nến đóng lại thì không vào.', ref: 'kb-c', gloss: 'fade' },
    thin: { text: 'Trend thin là profile mỏng đi một chiều: không cản tàu, chỉ vào theo chiều ở nhịp hồi. Hấp thụ và fade ngược chiều thin là cản tàu.', ref: 'cau-truc', gloss: 'thin' },
    balance: { text: 'Giữa range không có lệnh. Khi đang cân bằng thì hấp thụ chỉ ở vùng nằm sát cạnh range hoặc cạnh VA Âu (không quá 1 giá).', ref: 'cau-truc', gloss: 'canh' },
    tail: { text: 'Ngược bias chỉ được ở khối B, tại đỉnh hoặc đáy có tail thật, hoặc single print cũ đúng phía, cỡ ½, 2R. Tick ô này khi vùng đã chọn đúng như vậy.', ref: 'ma-tran-bias', gloss: 'tail' }
  };
  var blocks = {
    A: { title: 'Phá hồi', target: '3R',
      ctx: [
        { t: 'Có 1 nến M5 đóng ngoài cạnh (VA Âu, IB hoặc vùng đã kẻ)', help: HELP.step1 },
        { t: 'Nhịp hồi về cạnh giữ được, không nến M5 nào đóng ngược vào trong', help: HELP.accept }
      ],
      chk: [
        { t: 'Hồi hình U, ≥ 3 nến, không phải V', short: 'U', help: HELP.uv },
        { t: 'Tại cạnh: delta cùng chiều phá hoặc bong bóng hấp thụ phe ngược', short: 'Δ', help: HELP.step3 },
        { t: 'Bong bóng to gần nhất (10 nến, ở cực trị) không đứng phe ngược lệnh, hoặc mức đó đã vỡ', short: 'bb', help: HELP.bubble },
        { t: 'Giá cách vùng ≤ 1 giá, không ở lưng (hoặc râu nến xác nhận chạm vùng)', short: 'cạnh', help: HELP.near }
      ],
      ent: [{ t: 'Nến M1 đóng theo chiều phá, thân ≥ nửa biên độ, delta cùng dấu' }],
      sl: [] },
    B: { title: 'Hấp thụ', target: '3R', sizeNote: 'Vùng hạng 2 thì cỡ ½. Ngược bias: 2R, cỡ ½.',
      ctx: [
        { t: 'Giá tại VWAP tuần, VWAP ngày, HVN tuần, cụm POC, hoặc cạnh VA Âu khi đang cân bằng', help: { text: 'VWAP tuần là hạng 1 (tốt nhất). VWAP ngày, HVN tuần là hạng 2: cỡ ½. Cụm POC xếp hạng 2 theo QĐ-3, quyết định của công cụ, chưa đo. Cạnh VA Âu chỉ khi đang cân bằng.', ref: 'xep-hang-vung', gloss: 'hang' } },
        { t: 'Không phải HVN 3 tuần, LVN, HVN ngày', help: { text: 'HVN 3 tuần và LVN là vùng cấm fade. HVN ngày: Hệ thống chỉ cấm ngay sau cú phá cực trị (phép đo 1 nghiêng về đi tiếp, phép đo 2 trung tính); công cụ chặn mọi HVN ngày theo QĐ-15 (quyết định của công cụ, chưa đo).', ref: 'xep-hang-vung', gloss: 'hvn' } },
        { t: 'Không đang phá VWAP / cạnh theo chiều move (nếu có là phá hồi — dùng A)', help: { text: 'Hấp thụ và phá hồi cùng lúc thì theo phá hồi. Không cản tàu khi tàu vừa qua cạnh.', ref: 'xung-dot', gloss: 'pha-hoi' } },
        { t: 'Nếu đang cân bằng: vùng ở cạnh range / VA Âu (≤ 1 giá), không ở giữa range', help: HELP.balance },
        { t: 'Không phải trend thin đi ngược lệnh (không cản tàu)', help: HELP.thin }
      ],
      chk: [
        { t: '3 nến cuối: thân và |delta| giảm dần, không cực trị mới', short: 'giảm dần', help: HELP.absorb },
        { t: 'Bong bóng ở cực trị cùng phe với lệnh', short: 'bb', help: HELP.bubble },
        { t: 'DMA đi ngang', short: 'DMA', help: HELP.dma },
        { t: 'Cú test lại hình U, không phải V', short: 'U', help: HELP.uv },
        { t: 'Giá cách vùng ≤ 1 giá, không ở lưng (hoặc râu nến xác nhận chạm vùng)', short: 'cạnh', help: HELP.near }
      ],
      ent: [{ t: 'Nến xác nhận ngược chiều move, delta đổi dấu, độ lớn ≥ ½ |delta| của nến lớn nhất trong move', help: HELP.confirmB }],
      sl: [] },
    C: { title: 'Fade cạnh', target: '2R', sizeNote: 'Luôn cỡ ½.',
      ctx: [
        { t: 'Vùng là cạnh VA Âu / range, không ở giữa range', help: HELP.edge },
        { t: 'Chưa có nến M5 nào đóng ngoài cạnh', help: HELP.accept },
        { t: 'Không phải trend thin đi ngược lệnh (không cản tàu)', help: HELP.thin }
      ],
      chk: [
        { t: 'Phá hụt: râu xuyên cạnh rồi đóng lại trong', short: 'phá hụt', help: HELP.fadeWick },
        { t: 'Delta ủng hộ chiều vào', short: 'Δ' },
        { t: 'Bong bóng to gần nhất (10 nến, ở cực trị) không đứng phe ngược lệnh, hoặc mức đó đã vỡ', short: 'bb', help: HELP.bubble },
        { t: 'Giá cách vùng ≤ 1 giá, không ở lưng (hoặc râu nến xác nhận chạm vùng)', short: 'cạnh', help: HELP.near }
      ],
      ent: [{ t: 'Nến M1 đóng lại trong range; thân không ngắn, râu ngược không dài', help: HELP.fadeWick }],
      sl: [] },
    D: { title: 'Trap', target: '2R',
      ctx: [
        { t: 'Có move rõ ≥ 5 giá cùng chiều bias' },
        { t: 'Không đang đi ngang' },
        { t: 'Nhịp hồi ngược tới một vùng, chưa quá 70% move' }
      ],
      chk: [
        { t: 'Đỉnh hồi có bong bóng hấp thụ phe hồi, hoặc nến hồi delta theo chiều hồi mà đóng ở nửa ngược chiều hồi', short: 'bẫy', help: HELP.trap },
        { t: 'Hồi hình U, ≥ 3 nến, không phải V', short: 'U', help: HELP.uv },
        { t: 'Bong bóng to gần nhất (10 nến, ở cực trị) không đứng phe ngược lệnh, hoặc mức đó đã vỡ', short: 'bb', help: HELP.bubble },
        { t: 'Giá cách vùng ≤ 1 giá, không ở lưng (hoặc râu nến xác nhận chạm vùng)', short: 'cạnh', help: HELP.near }
      ],
      ent: [{ t: 'Nến M1 đóng theo chiều move cũ, thân dài, delta cùng dấu' }],
      sl: [] }
  };
  var groupTitles = { ctx: 'Bối cảnh', chk: 'Kiểm tra', ent: 'Điểm vào', sl: 'SL' };
  // chữ của một ô theo mã: ô tick của khối ('ctx1'), ô tự kiểm hoặc ô chọn ('zone2'), ô dùng chung ('common:news')
  function itemLabel(scen, id) {
    if (/^common:/.test(id)) { var c = common.filter(function (x) { return 'common:' + x.id === id; })[0]; return c ? c.label : id; }
    var m = /^(ctx|chk|ent|sl)(\d+)$/.exec(id);
    if (m) { var b = blocks[scen]; var it = b && b[m[1]][+m[2] - 1]; return it ? it.t : id; }
    return itemLabels[id] || id;
  }

  var closeReasons = [
    { v: 'absorb', label: 'Hấp thụ ngược đe dọa TP' },
    { v: 'flat', label: 'Đóng sạch trước tin' },
    { v: 'other', label: 'Khác (tính là phá luật)' }
  ];

  var qd = {
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
    paper: '(luyện mắt)', warnPrefix: 'phá luật', manualClose: 'đóng tay lý do khác',
    mdTitle: 'Sổ đêm', mdHead: '| giờ | hướng | tên | vùng | 4 kiểm tra | SL | R |', mdWarn: '⚠ dòng',
    mdLegend: 'Cột "4 kiểm tra": các ô kiểm tra đã tick lúc ghi lệnh (U nhịp hồi · bb bong bóng · Δ delta · cạnh · DMA).',
    mdCard: 'Thẻ phiên', mdBias: 'BIAS', mdVwap: 'VWAP tuần', mdClose: 'Đóng hôm qua so với VA', mdShape: 'Hình hôm qua', mdZones: 'Vùng', mdPlan1: 'Kế hoạch 1', mdPlan2: 'Kế hoạch 2', mdCancel: 'Hủy khi',
    machine: 'Máy cộng', you: 'Bạn cộng', breaks: 'Lệnh phá luật', swept: 'SL bị quét rồi tới TP'
  };
  var errors = { BAD_JSON: 'Tệp không phải JSON hợp lệ.', NO_NIGHTS: 'Không thấy dữ liệu các đêm trong tệp.' };

  var ui = {
    appTitle: 'Trạm Đêm Vàng', skip: 'Bỏ qua, tới nội dung chính', yes: 'Có', no: 'Không', cancel: 'Hủy', confirm: 'Đồng ý', close: 'Đóng', on: 'Bật',
    off: 'Tắt', remove: 'Xóa', add: 'Thêm', helpLabel: 'Trợ giúp', helpLink: 'Mở mục này trong Hệ thống Đêm Vàng', biasBuy: 'BUY', biasSell: 'SELL',
    biasNone: 'KHÔNG', biasWait: 'CHỜ', biasUnknown: 'chưa đủ dữ liệu', sideUpper: 'phía trên', sideUpperOpt: 'Phía trên', sideLowerOpt: 'Phía dưới',
    sideLower: 'phía dưới', overridden: '(đổi tay)', unitGia: 'giá', newVersion: 'Có bản mới.', reload: 'Tải lại', clock: '{hm} VN',
    nextWindow: 'Khung giờ cấm kế tiếp: {hm} ({min}′)', inWindow: 'ĐANG TRONG KHUNG GIỜ CẤM {hm} — còn {left}′',
    noWindow: 'Không còn khung giờ cấm đã biết đêm nay', biasChip: 'BIAS {v}', chipBreaks: 'Phá luật {n} trên 2', chipStreak: 'SL liên tiếp {n} trên 3',
    chipOpen: 'Lệnh mở {n}', chipOpenPaper: 'Lệnh mở {n} (luyện mắt)',
    chipBreaksTip: 'Số lệnh phá luật trong đêm. Đủ 2 lệnh thì tắt máy đến hết đêm.',
    chipStreakTip: 'Số SL liên tiếp ở cuối sổ. Đủ 3 thì tắt máy đến hết đêm. Lệnh đóng lỗ từ 0,2R trở lên tính là SL, kể cả đóng tay (quyết định của công cụ, chưa đo).',
    chipOpenTip: 'Còn lệnh chưa nhập kết quả trong Sổ.', statusToggle: 'Trạng thái', winterChip: 'Mỹ mùa đông +1h', cardTitle: 'Thẻ phiên',
    cardDate: 'Ngày', cardVwap: 'VWAP tuần', cardClose: 'Đóng hôm qua', cardShape: 'Hình hôm qua', cardBias: 'BIAS', cardZones: 'VÙNG',
    cardDebt: 'NỢ', cardBanned: 'VÙNG CẤM', cardNote: 'Kịch bản nền', cardPlanNote: 'Ghi chú', cardPlan1: 'Kế hoạch 1', cardPlan2: 'Kế hoạch 2',
    cardCancel: 'Hủy khi', cardNone: '—', halfNote: 'Cỡ ½ vì: {why}.', halfNoteMin: 'Lẽ ra cỡ ½ vì: {why}; không chia được.',
    copyShape: 'hình 3 tuần', cardLocked: 'Đã chốt lúc {hm}', cardNotLocked: 'Chưa chốt', cardToggle: 'Thẻ phiên',
    t0Lead: 'Làm trước 18:00, xong trong một phút.', t0Alert: 'Tỉnh táo, không bực dọc?',
    t0ViewOnly: 'Cả đêm chỉ xem: ENTRY hiện xám, không vào lệnh thật. Bạn vẫn ghi kèo luyện mắt để có số R.', newsTitle: 'Tin tối nay',
    newsUpdated: 'cập nhật lúc {hm}', newsNone: 'Tối nay không có tin USD mức cao hoặc vừa.',
    newsNoFeed: 'Chưa tải được lịch tin — đang dùng mốc mặc định.',
    newsStaleBar: 'Không có lịch tin cho đêm nay — tự kiểm Forex Factory. Đang dùng khung giờ mặc định.',
    newsStaleNote: 'Lịch tải cách đây {min}′: giờ tin vẫn đúng, số thực tế có thể chậm.', impHigh: 'cao', impMed: 'vừa', warnOnlyTag: 'chỉ cảnh báo',
    newsNums: 'dự báo {f} · kỳ trước {p} · thực tế {a}', rowCore: 'Mặc định: giờ mở chính', row1930: 'Mặc định: tin 19:30', rowCustom: 'Thêm tay',
    rowFomc: 'FOMC (thêm tay)', newsDayTag: 'Đêm có tin lớn — cỡ ½', newsDayOff: 'Đêm có tin lớn: đã tắt tay', newsDayOffBtn: 'Tắt',
    newsDayOnBtn: 'Bật lại', newsSkipped: 'Tin chưa có giờ, bỏ qua: {list}.', offAt: 'đã tắt lúc {hm}', winShort: '±{n}′',
    offConfirmTitle: 'Tắt khung giờ cấm?', offConfirmText: 'Tắt khung giờ {hm} sẽ ghi lại giờ tắt. Chắc chắn?', offConfirmOk: 'Tắt khung giờ',
    nyseRow: 'NYSE mở (±5′): chỉ cảnh báo', alwaysOn: 'luôn bật', addManual: 'Thêm tay…', addWindow: 'Thêm khung giờ', timePh: 'giờ VN (hh:mm)',
    rank1: 'Hạng 1', rank2: 'Hạng 2', minBefore: 'phút trước', minAfter: 'phút sau', addFomc: 'Thêm FOMC {fomc}',
    badTime: 'Giờ chưa đúng dạng giờ:phút.', newsDay: 'Hôm nay có tin lớn (NFP, CPI)', t0Note: 'Kịch bản nền (tùy chọn)', t0NotePh: 'Một dòng',
    t0Done: 'Xong tầng 0 — sang kẻ vùng', quickPh: 'Gõ nhanh: vwapw 4205, vah 4199, val 4185, hvn 4195',
    quickHint: 'Enter để thêm. Mã: vwapw vwapd vah val poc hvn hvn3 lvn high low npoc ibh ibl ph pl; spu spl reu rel (u trên, l dưới); hvn 4195-4197 cho vùng.',
    quickBad: 'Không hiểu: {list}.', quickFull: 'Chỉ còn chỗ cho {n} vùng.', newsChip: 'Tin kế {hm} · {name} · còn {min}′',
    fxChip: 'Tin {ccy} mức cao {hm}', t1Lead: 'Kẻ vùng trên chart A rồi chốt thẻ phiên. Không có thẻ phiên thì không có lệnh.',
    t1Draw: 'Kẻ trên chart A: High · VAH · POC · VAL · Low hôm qua · VWAP tuần và ngày · HVN / LVN · nợ (single print, poor high / low) · VAH Âu, VAL Âu.',
    t1Title2: 'Câu hỏi chốt bias', tailQ: 'Tail thật?', planNote: 'Ghi chú kế hoạch (tùy chọn)', planNotePh: 'Nếu … thì … ; hủy khi …',
    addNote: 'Thêm ghi chú', vwapQ: 'Giá hiện tại so với VWAP tuần', vwapHelp: 'Sát nghĩa là cách VWAP tuần không quá 2 giá. Sát thì bias CHỜ.',
    recheck: 'Chốt lại bias: đã có 1 nến M5 đóng rõ', rcAbove: 'Phía trên', rcBelow: 'Phía dưới', editRecheck: 'Chốt lại bias sau nến M5',
    t1BiasHelp: 'Bias chỉ lấy từ VWAP tuần và giá đóng hôm qua so với VA. Đổi bằng tay được nhưng phải có lý do.', biasIs: 'Bias',
    autoWas: '(tự động: {v})', overrideTitle: 'Đổi bias bằng tay (cần lý do)', overridePh: 'Lý do đổi bias',
    overrideNeed: 'Chưa có lý do thì bias vẫn là bias tự động.', editOverride: 'Đổi bias bằng tay', editOverrideReason: 'Lý do đổi bias',
    t1Title4: 'Vùng ({n}/5)', t1ZoneHelp: 'Chọn 3–5 vùng. Hạng và cờ của vùng tự suy theo loại.', price: 'Giá', priceTo: 'đến giá',
    zoneType: 'Loại vùng', addZone: 'Thêm vùng', needPrice: 'Nhập giá của vùng.', zonesFull: 'Đã đủ 5 vùng.',
    zonesFew: 'Dưới 3 vùng: vẫn chốt được, nhưng ít chỗ để vào.', noZones: 'Chưa có vùng nào.', addedZone: 'Thêm vùng {t}', editZone: 'Sửa vùng {z}',
    delZone: 'Xóa vùng {z}', editQ: '{q}: {v}', t1Title5: 'Chốt thẻ phiên',
    t1CardHelp: 'Thẻ phiên phải chốt trước khi có ENTRY. Sau {comex} mỗi lần sửa thẻ đều ghi lại giờ sửa.', lockCard: 'Chốt thẻ phiên',
    lockNeed: 'Còn thiếu: {list}', need_q1: 'Q1 (hình hôm qua)', need_q5: 'Q5 (đóng hôm qua so với VA)', need_q6: 'Q6 (Âu dựng range)',
    need_vwapW: 'VWAP tuần', need_zones: 'ít nhất 1 vùng', lockWhy: 'Chưa chốt thẻ phiên thì chưa có ENTRY.', locked: 'Đã chốt thẻ phiên.',
    toTier2: 'Sang Setup Entry', editAfterLock: 'Sau chốt vẫn sửa được; sửa sau {comex} sẽ ghi lại giờ sửa.',
    t2Lead: 'Bốn danh sách mở sẵn. Tick đủ một khối là vào lệnh; không khối nào bị khóa.', scenImgAlt: 'Ví dụ kịch bản {name}',
    nthAt: 'Lần thứ {n} tại vùng', counterPh: 'Lý do ngược bias', entryL: 'Giá vào', slL: 'SL', tpL: 'TP', tpAuto: 'gợi ý',
    calcNeed: 'Nhập hướng, giá vào và SL để tính R:R và cỡ lệnh.', calcSl: 'SL {v} giá', calcRr: 'R:R 1:{v}', calcTpSug: 'TP gợi ý {v}',
    sizeTitle: 'Cỡ lệnh MGC', sizeNoCfg: 'chưa cài vốn', sizeZero: '0 hợp đồng', sizeN: '{n} hợp đồng', vWait: 'CHỜ',
    forceBtn: 'Vẫn vào (thiếu {n} ô — tính phá luật)', forceNeed: 'Cần có hướng, giá vào và SL trước.', entryView: 'ENTRY (chỉ xem)',
    paperBtn: 'Ghi kèo luyện mắt', slGia: '{v} giá', sizeHalfShort: 'cỡ ½', sizeFull: 'cỡ đủ', entered: 'Đã ghi lệnh vào sổ.',
    enteredPaper: 'Đã ghi kèo luyện mắt.', forcedToast: 'Đã ghi lệnh phá luật vào sổ.', forceTitle: 'Vào lệnh phá luật?',
    forceText: 'Còn thiếu {n} ô: {list}.', forceCount: 'Lệnh này tính là phá luật; 2 lệnh phá luật thì tắt máy.',
    forcePaperNote: 'Đang ở chế độ chỉ xem nên không tính phá luật.', forceOk: 'Vẫn vào, chấp nhận phá luật', editWhileSetupTitle: 'Đang canh kèo',
    editWhileSetupText: 'Sửa thẻ lúc này là nắn kế hoạch theo kèo. Vẫn sửa và ghi lại giờ sửa?', editWhileSetupOk: 'Vẫn sửa', t4Title: 'Lệnh đang mở',
    openPaper: 'luyện mắt', ruleBreakFlag: 'phá luật', kvEntry: 'Giá vào', kvSl: 'SL', kvTp: 'TP', kvRr: 'R:R dự kiến', kvSize: 'Số hợp đồng',
    kvTime: 'Giờ vào', t4Close: 'Kết quả lệnh', closeTp: 'Chạm TP', closeSl: 'Chạm SL', closeBe: 'Hòa', closeManual: 'Đóng tay',
    exitPrice: 'Giá thoát', manualReason: 'Lý do đóng tay',
    manualHelp: 'Chỉ đóng tay khi hấp thụ ngược chiều đe dọa TP (đóng sạch trước tin: quyết định của công cụ theo QĐ-22). Râu dài, sốt ruột không phải lý do.',
    manualBreak: 'Lý do "khác" tính là phá luật.', closeConfirm: 'Ghi kết quả', closedToast: 'Đã ghi kết quả vào Sổ.',
    swept: 'SL bị quét rồi giá tới TP', tradeNote: 'Ghi chú', t5Tonight: 'Đêm {key}', t5Help: 'Sổ 7 cột ghi trước khi bấm. Dòng ⚠ nêu luật đã phạm.',
    jh1: 'giờ', jh2: 'hướng', jh3: 'tên', jh4: 'vùng', jh5: '4 kiểm tra', jh6: 'SL', jh7: 'R', warnRow: '⚠ dòng {time} {w}',
    noTrades: 'Chưa có lệnh nào đêm nay.', machineSum: 'Máy cộng: {r} R', yourSum: 'Bạn cộng tay (để đối chiếu máy)',
    mismatch: 'Lệch so với máy cộng — kiểm lại từng lệnh', breaksN: 'Lệnh phá luật: {n}', sweptN: 'SL bị quét rồi tới TP: {n}', endNight: 'Kết phiên',
    endNeed: 'Cần nhập "Bạn cộng" trước.', endedToast: 'Đã kết phiên.', afterClose: 'Sau đóng lệnh: SL bị quét, ghi chú',
    t5Week: 'Cuối tuần: 4 con số', t5WeekHelp: 'Chỉ số theo dõi duy nhất của tuần là số lệnh phá luật. Lãi lỗ chỉ là hệ quả.',
    wBreaks: 'Phá luật / tổng lệnh', wSwept: 'SL bị quét rồi tới TP', wByScen: 'R theo kịch bản', wByZone: 'R theo loại vùng',
    wCounter: 'Lệnh ngược bias', wStreak: 'Số đêm liên tiếp không phá luật', pairFmt: '{name} {n} lệnh {r} R', t5Export: 'Xuất và nhập',
    exMd: 'Tải Markdown', exMdCopy: 'Sao chép Markdown', exJson: 'Tải JSON', exCsv: 'Tải CSV', copied: 'Đã sao chép.',
    copyFail: 'Không sao chép được.', importJson: 'Nhập JSON (gộp vào dữ liệu hiện có)',
    importDone: 'Nhập xong: {a} đêm mới, {b} đêm gộp, {c} lệnh thêm.', exportDue: 'Cuối tuần rồi — tải JSON về để giữ bản sao.',
    t5Settings: 'Cài đặt', setTheme: 'Giao diện', themeDark: 'Tối', themeLight: 'Sáng', setGuide: 'Mức hướng dẫn', guideNew: 'Mới', guideQuen: 'Quen',
    setCapital: 'Vốn', setRisk: 'Rủi ro mỗi lệnh', setDst: 'Mốc giờ dịch theo giờ mùa đông', setDstHelp: 'Tắt thì mọi mốc luôn theo giờ mùa hè.',
    setKeys: 'Phím tắt Setup Entry', keysHelp: 'Bấm ? để xem danh sách phím tắt.', wipe: 'Xóa toàn bộ dữ liệu', wipeTitle: 'Xóa toàn bộ dữ liệu?',
    wipeText: 'Mọi đêm, thẻ phiên và sổ lệnh trên máy này sẽ mất. Nên tải JSON trước.', wipeOk: 'Xóa hết', wiped: 'Đã xóa dữ liệu.',
    version: 'Phiên bản {v}', keysTitle: 'Phím tắt (Setup Entry)', key0: 'Nhảy tới khối A, B, C, D', key1: 'Ghi lệnh khi thanh ENTRY xanh',
    key2: 'Xóa tick khối đang làm', key3: 'Rời ô nhập, đóng hộp thoại', key4: 'Mở bảng phím tắt',
    zoneHasTrades: 'Vùng này đã có lệnh trong sổ nên không xóa được (đếm 2 lần mỗi vùng).', glossaryBtn: 'Từ điển', glossaryTitle: 'Từ điển',
    glossaryHint: 'Định nghĩa ngắn các từ hay gặp. Đầy đủ ở trang Hệ thống Đêm Vàng.', openGlossary: 'Mở Từ điển', qPrefix: '{n} · {label}',
    vwapNowL: 'Giá hiện tại (tùy chọn)', vwapPriceL: 'VWAP tuần (tùy chọn)',
    planConflict: 'Kế hoạch đang ngược bias {b}. Vẫn chốt được, nhưng vào lệnh ngược bias phải ghi lý do.',
    planConflictToast: 'Cảnh báo: kế hoạch ngược bias.', nightPick: 'Chọn đêm', editsOpen: '{n} lần sửa thẻ',
    storeFail: 'Không lưu được vào máy — tải JSON ngay để giữ dữ liệu.', storeFailBtn: 'Tải JSON',
    otherTab: 'Dữ liệu vừa đổi ở thẻ trình duyệt khác — đã tải lại.', warnShort: 'trước {nyse} · cỡ ½',
    sizeMinOne: '1 hợp đồng = cỡ đủ, rủi ro {usd} $', capTitle: 'Vốn và rủi ro mỗi lệnh',
    capText: 'Công cụ dùng hai số này để tính số hợp đồng MGC. Mặc định 2000 $ và 2%. Đổi lại được ở tầng Sổ, mục Cài đặt.', capLater: 'Để sau',
    capSave: 'Lưu', capBad: 'Vốn và % rủi ro phải là số lớn hơn 0.', capChange: 'Đổi vốn', glossarySearch: 'Tìm từ…',
    glossaryNone: 'Không có mục nào khớp.', copyPrev: 'Sao chép vùng từ đêm {key}', copyPrevEdit: 'Sao chép vùng từ đêm {key}',
    copyPrevDone: 'Đã chép: {list}.', copyPrevNone: 'Không có gì mới để chép.', goTier1: 'Về tầng 1', clearBlockDone: 'Đã bỏ tick khối {s}.',
    autoTag: 'tự kiểm', openJournal: 'Mở Sổ', commonTitle: 'Ô chung cho cả bốn khối',
    commonHelp: 'Bốn ô máy tự kiểm và một ô bạn tick. Ô nào đỏ thì chưa có ENTRY ở khối nào, nhưng bạn vẫn tick được các ô còn lại để luyện mắt.',
    jumpLabel: 'Nhảy tới khối', scenImgOpen: 'Phóng to ảnh ca thật {name}', clearBlock: 'Xóa tick', sideL: 'Hướng', zoneL: 'Vùng',
    zoneHelp: 'Chọn vùng trong thẻ phiên. Giá phải cách vùng không quá 1 giá.', numsTitle: 'Giá vào, SL, TP, biên độ nến',
    numsHelp: 'Gõ giá vào, SL, TP (để trống thì lấy TP gợi ý) và biên độ nến M1 cao nhất 5 nến (cao trừ thấp, không gõ mức giá). Biên độ nến là sàn nhiễu của SL.',
    c6L: 'Biên độ nến M1 cao nhất 5 nến', autoWait: 'chờ đủ số liệu', biasNoneNote: 'Bias KHÔNG: chỉ fade hai cạnh VA Âu, mục tiêu 2R, cỡ ½. Không phá hồi.',
    biasWaitNote: 'Bias CHỜ: chờ 1 nến M5 đóng rõ một phía rồi chốt lại bias ở tầng 1.', biasUnknownNote: 'Chưa có bias: điền thẻ phiên ở tầng 1.',
    scenTag: 'kịch bản {s}', writeBtn: 'Ghi lệnh', waitPick: 'chọn một khối và tick các ô.', waitBlock: 'khối {s} còn thiếu:',
    waitCommon: 'khối {s} đủ ô, nhưng ô chung chưa đạt:', moreItems: '(+{n} ô nữa)', exitR: 'R thực tế',
    exitRHint: 'Bấm nhanh hoặc gõ số R.', needReason: 'Chọn lý do đóng tay.', needExit: 'Chọn hoặc gõ R kết quả.',
    beRemind: 'Nhắc be: dời SL về hòa vốn (be) khi giá đạt +{r}R.',
    beRemindBar: 'Nhắc be: dời SL về hòa vốn (be) khi giá đạt +{r}R và có 1 nến M1 đóng ngoài vùng vào.',
    barOpen: 'Lệnh đang mở:', barBe: 'be +{r}R', entryBar: 'ENTRY {side} · khối {s} · vùng {zone} · mục tiêu {r}R', rQuick: 'R kết quả', rQuickHint: 'Bấm nhanh hoặc gõ số R.', kvSide: 'Hướng', kvScen: 'Kịch bản', kvZone: 'Vùng', c6Night: 'Biên độ nến M1 cao nhất 5 nến (cả đêm)', commonSum: '{n}/{m} máy kiểm đạt: thẻ phiên · giờ cấm · tắt máy · lệnh mở',
    wickL: 'Râu nến xác nhận chạm vùng', autosTitle: 'Máy tự kiểm', scenImgZoom: 'Bấm ảnh để mở ảnh gốc và phóng to.', counterTag: 'ngược bias · 2R · cỡ ½',
    slAbove: 'SL phải cao hơn giá vào (sell).', slBelow: 'SL phải thấp hơn giá vào (buy).', badNum: 'Không đọc được số "{v}" — đã xóa.',
    pickBlockFirst: 'Mở một khối trước, rồi bấm vùng.', zonePickTip: 'Bấm để chọn vùng này cho khối đang làm', zoneTap: 'Chạm lần nữa để chọn',
    zoneFilter: 'Gõ để lọc loại vùng…', zonePh: 'Chọn loại vùng', zoneUse: 'Dùng thế nào:', zoneNone: 'Không có loại vùng nào khớp.'
  };

  // ===== Từ điển (định nghĩa ngắn, lấy từ trang Hệ thống Đêm Vàng; chỗ là luật của công cụ thì ghi rõ) =====
  var glossaryBase = [
    { key: 'bias', term: 'bias', def: 'Chiều ưu tiên của đêm: BUY, SELL, KHÔNG hoặc CHỜ. Chỉ lấy từ VWAP tuần và giá đóng hôm qua so với VA hôm qua; ngược bias phải ghi lý do trước khi bấm.' },
    { key: 'no', term: 'nợ', def: 'Phần giá chưa được lấp lại (single print, poor high, poor low), giá hay trở lại chạm. Đây là "nợ giá", không phải nợ tiền.' },
    { key: 'moi', term: 'mồi', def: 'Cực trị có khối lượng dày: trông như đỉnh hoặc đáy nhưng không phải bị từ chối thật, nên không coi là đỉnh hay đáy. Ví dụ: đỉnh 4210,0 chỉ 1 TPO, khối lượng thấp ⇒ tail thật; đỉnh 4208,0 khối lượng dày ⇒ mồi (ví dụ minh họa, không phải ca thật).' },
    { key: 'tail', term: 'tail thật', def: 'Cực trị chỉ có 1 TPO với khối lượng thấp: giá bị từ chối thật ở đó. Ngược bias chỉ hấp thụ ở đỉnh hoặc đáy có tail thật hoặc single print cũ đúng phía, cỡ ½, 2R.' },
    { key: 'thin', term: 'thin', def: 'Profile mỏng, đi một chiều, chưa đấu giá xong: không đánh ngược. Chế độ "Trend thin" là không cản tàu, chỉ vào theo chiều ở nhịp hồi.' },
    { key: 'trap', term: 'trap (bẫy)', def: 'Một move rõ (từ 5 giá) cùng chiều bias, rồi nhịp hồi ngược tới một vùng. Ở đỉnh nhịp hồi phe hồi thử mà thất bại: bong bóng hấp thụ phe hồi, hoặc nến hồi có delta thuận mà đóng dưới nửa thân. Vào theo chiều move cũ, mục tiêu 2R. Ví dụ: sell, giá giảm từ 4200 xuống 4194 (6 giá), hồi lên 4197 (nửa move, dưới 70%) rồi thất bại ⇒ sell, SL trên 4197 cộng 0,3 giá (ví dụ minh họa, không phải ca thật).' },
    { key: 'bong-bong', term: 'bong bóng', def: 'Vòng tròn trên chart M1 (chỉ báo hấp thụ và chỉ báo lệnh lớn). Tròn đặc là hấp thụ: một phe đánh market mạnh tại mức đó mà giá không đi; vòng trắng là mức còn giữ, mờ đi là mức đã vỡ. Tròn mờ có số từ 100 là lệnh lớn vừa vào; giá không rời mức thì mức đó thành vùng phòng thủ. Chỉ để kiểm tra, không phải tín hiệu vào lệnh.' },
    { key: 'dma', term: 'DMA', def: 'Chỉ báo đường trên chart M1 dùng để đọc đà (trang Hệ thống không ghi tên đầy đủ). Dốc cùng chiều move là đà còn; đi ngang khi giá còn chạy là đà đang cạn. Chỉ để kiểm tra, không phải tín hiệu vào lệnh.' },
    { key: 'be', term: 'be (hòa vốn)', def: 'Dời SL về giá vào để lệnh không lỗ nữa. Phá hồi và hấp thụ dời ở +1,5R sau 1 nến M1 đóng ngoài vùng vào; fade và trap dời ở +1R.' },
    { key: 'hang', term: 'hạng vùng', def: 'Mức ưu tiên của vùng theo phép đo. Hạng 1 là VWAP tuần; hạng 2 (VWAP ngày, HVN tuần) thì hấp thụ đi cỡ ½. Cụm POC xếp hạng 2 theo QĐ-3, quyết định của công cụ, chưa đo.' },
    { key: 'canh', term: 'cạnh', def: 'Mép của vùng giá trị Âu hoặc của range: VAH Âu, VAL Âu, IB, cạnh range. Ở câu hỏi "giá cách vùng", ở cạnh là cách vùng không quá 1 giá.' },
    { key: 'acceptance', term: 'acceptance (công nhận cú phá)', def: 'Công nhận cú phá cần ba bước: (1) nến M5 đóng ngoài cạnh; (2) nhịp hồi về cạnh giữ được, không nến M5 nào đóng ngược vào; (3) tại cú test lại trên M1 có delta cùng chiều phá, hoặc hấp thụ ngược chiều phá. Thiếu bước 2 thì chỉ là chạm.' },
    { key: 'hap-thu', term: 'hấp thụ', def: 'Một phe đánh market mạnh mà giá không đi: nỗ lực có, kết quả không. Chỉ gọi hấp thụ khi cả thân nến và độ lớn delta giảm dần qua 3 nến.' },
    { key: 'pha-hoi', term: 'phá hồi', def: 'Sau cú phá đã được công nhận, giá hồi hình U về cạnh vừa phá rồi đi tiếp theo chiều phá. Mục tiêu 3R.' },
    { key: 'fade', term: 'fade', def: 'Vào ngược chiều giá vừa chạy (bắt đảo chiều). Kịch bản C là fade cạnh: vào ngược hướng giá vừa xuyên cạnh rồi đóng lại trong (phá hụt), cỡ nhỏ, mục tiêu 2R.' },
    { key: 'hvn', term: 'HVN / LVN', def: 'HVN là nút khối lượng cao, giá hay đi ngang; LVN là nút khối lượng thấp, giá chạy nhanh qua. HVN 3 tuần và LVN là vùng cấm fade.' },
    { key: 'mo-ao', term: 'mở ảo', def: 'Hệ thống: khoảng {comex} đến {nyse} vàng hay chạy giả, cú phá chưa đáng tin; cú phá đáng tin thường rơi vào {real1} đến {real2}; trước {nyse} chỉ fade cạnh, cỡ nhỏ. Công cụ: không tắt kịch bản, chỉ giảm cỡ còn ½ (QĐ-19, quyết định của công cụ, chưa đo).' },
    { key: 'r', term: 'R', def: 'R là khoảng rủi ro của lệnh: giá vào trừ SL. Lãi 1R bằng đúng khoảng đó, 3R gấp ba. Ví dụ: sell 4193,0, SL 4195,4 (2,4 giá) thì 1R = 2,4 giá và TP 3R ở 4185,8.' },
    { key: 'hinh-dang', term: 'hình dạng profile (D, P, b, B, thin, chữ nhật)', def: 'D: đấu giá xong, chờ phá. P: cân bằng ở đỉnh, đuôi là hỗ trợ; b ngược lại. B: hai phân phối (hai cụm khối lượng); trang Hệ thống không định nghĩa hình B. thin: mỏng, một chiều, chưa xong, không đánh ngược. Chữ nhật: cân bằng rộng, sẽ phá một đầu.' },
    { key: 'va', term: 'VA / VAH / VAL / POC', def: 'VA là vùng quanh POC chứa khoảng 70% khối lượng (hoặc TPO) của phiên. VAH là mép trên, VAL là mép dưới, POC là mức giá giao dịch nhiều nhất. Giá đóng hôm qua ngoài VA hôm qua là giá đang tìm giá trị mới; trong VA là cân bằng còn hiệu lực. VAH Âu và VAL Âu là hai cạnh mặc định để fade. (Định nghĩa TPO chuẩn; trang Hệ thống không định nghĩa.)' },
    { key: 'pha-gia', term: 'phá giả', def: 'Từ 18:00 đến {comex} hay có cú phá VA ngay trước giờ COMEX mà không đi tiếp. Thấy phá giờ này: nghi trước, tin sau. Công cụ chỉ nhắc: ở khối A có ô "Cú phá không rơi vào 18:00–{comex}" để bạn tự tick.' },
    { key: 'khung-gio-cam', term: 'khung giờ cấm (còn gọi cửa sổ cấm)', def: 'Khoảng quanh giờ tin, tự lấy từ lịch Forex Factory: tin USD mức cao trước 15′ sau 15′ (hạng 1; họp báo FOMC sau 30′), mức vừa trước 5′ sau 5′ (hạng 2). Lịch cũ hơn 2 giờ mà còn phủ đêm nay thì vẫn dùng. Không có lịch thì dùng mặc định: {news1} ±15′ vào thứ Năm và {core} ±5′. Trong khoảng đó mọi kịch bản đều KHÔNG VÀO; lệnh đang mở thì đóng sạch trước khung giờ hạng 1.' },
    { key: 'move', term: 'move', def: 'Đợt giá chạy rõ một chiều, từ lúc bắt đầu tới lúc dừng. Nhịp hồi là đoạn giá quay ngược lại sau move.' },
    { key: 'range', term: 'range', def: 'Khoảng giá đi ngang có hai mép (cạnh trên và cạnh dưới). Giữa range không có lệnh.' },
    { key: 'test-lai', term: 'test lại (retest)', def: 'Giá quay lại chạm mức vừa phá. Giữ được thì cú phá có thể là thật; không giữ thì chỉ là chạm.' },
    { key: 'luat-sl', term: 'luật SL (3 điều kiện)', def: 'Luật SL (HT mục 6), bạn tự kiểm, công cụ không tính và không chặn ENTRY: (1) vị trí: sau cấu trúc của kịch bản (râu nến xác nhận, cực trị cụm hấp thụ, râu phá hụt, đỉnh nhịp hồi) cộng 0,3 giá; (2) sàn nhiễu: SL không ngắn hơn nến M1 lớn nhất trong 5 nến; (3) trần: SL không quá 4 giá. R:R ít nhất 1:2 tính trước; TP 3R cho A, B (B ngược bias: 2R), 2R cho C, D, hoặc vùng kế tiếp nếu gần hơn (C: cạnh đối diện hoặc POC).' },
    { key: 'sl-bi-quet', term: 'SL bị quét', def: 'SL (hoặc SL đã dời về hòa) bị chạm rồi giá quay lại chạy tới TP. Sổ đếm số lệnh như vậy để biết SL có đặt quá sát không (HT mục 6, 8). Lệnh vẫn tính là SL, không đổi kết quả.' }
  ];

  // Từ điển = các mục chung + một mục cho mỗi loại vùng (cùng nguồn với ô chọn loại vùng ở tầng 1)
  var glossary = glossaryBase.concat(Object.keys(zoneTypes).map(function (k) {
    var z = zoneTypes[k];
    return { key: 'z-' + k, term: z.label.replace(/ \(.*\)$/, '') + ' (' + z.rank + ')', def: z.def + ' ' + z.use };
  }));

  // thay {comex} {nyse} {real1} {real2} {fomcFlat} bằng giờ đã dịch theo mùa (xem time.textVars); biến lạ giữ nguyên
  function fill(s, vars) {
    if (!vars || typeof s !== 'string') return s;
    return s.replace(/\{(\w+)\}/g, function (m, k) { return vars[k] === undefined ? m : vars[k]; });
  }

  return {
    fill: fill, helps: HELP, glossary: glossary, HT_BASE: HT_BASE, scenarios: scenarios, zoneTypes: zoneTypes, flagText: flagText, tiers: tiers,
    common: common, commonBad: commonBad, itemLabels: itemLabels, autoBad: autoBad, blocks: blocks, groupTitles: groupTitles, itemLabel: itemLabel,
    halfText: halfText, warnText: warnText, questions: questions, vwapOpts: vwapOpts,
    phases: phases, bands: bands, notices: notices, journal: journal, errors: errors,
    closeReasons: closeReasons, qd: qd, unmeasured: unmeasured, ui: ui
  };
});
