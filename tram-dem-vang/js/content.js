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

  // Loại vùng: nhãn, vai (bảng 2.3 của Hệ thống), định nghĩa 1–2 câu, "dùng thế nào" 1 câu.
  // Một nguồn duy nhất: ô chọn loại vùng ở tầng 1 và Từ điển đều đọc từ đây.
  var zoneTypes = {
    vwapW: { label: 'VWAP tuần', rank: 'hạng 1',
      def: 'Giá trung bình theo khối lượng, tính từ đầu tuần. Đây là đường mốc cả tuần.',
      use: 'Hạng 1: vùng bắt đảo chiều và hấp thụ tốt nhất đã đo. Giá cách không quá 2 giá là "sát": bias CHỜ.' },
    vwapD: { label: 'VWAP ngày', rank: 'hạng 2',
      def: 'Giá trung bình theo khối lượng, tính từ đầu phiên ngày.',
      use: 'Hạng 2: chỉ một phép đo ủng hộ, hấp thụ ở đây đi cỡ ½.' },
    hvnW: { label: 'HVN tuần', rank: 'hạng 2',
      def: 'Nút khối lượng cao của tuần: mức giá giao dịch dày, giá hay đi ngang quanh đó.',
      use: 'Hạng 2: phép đo coi như trung tính, hấp thụ ở đây đi cỡ ½.' },
    pocCluster: { label: 'Cụm POC (từ 2 POC, cách ≤ 1 giá)', rank: 'hạng 2',
      def: 'Từ hai POC (mức giao dịch nhiều nhất của mỗi phiên) nằm cách nhau không quá 1 giá, gộp thành một cụm.',
      use: 'Hạng 2, chưa đo: hấp thụ ở đây đi cỡ ½.' },
    vahEu: { label: 'VAH Âu', rank: 'cạnh',
      def: 'Mép trên của vùng giá trị (VA, nơi giao dịch phần lớn khối lượng) của phiên Âu.',
      use: 'Cạnh mặc định để fade khi đang cân bằng. Có 1 nến M5 đóng ngoài thì tắt fade, chờ công nhận cú phá.' },
    valEu: { label: 'VAL Âu', rank: 'cạnh',
      def: 'Mép dưới của vùng giá trị (VA, nơi giao dịch phần lớn khối lượng) của phiên Âu.',
      use: 'Cạnh mặc định để fade khi đang cân bằng. Có 1 nến M5 đóng ngoài thì tắt fade, chờ công nhận cú phá.' },
    rangeEdge: { label: 'Cạnh range (chọn phía)', rank: 'cạnh',
      def: 'Mép trên hoặc mép dưới của khoảng giá đi ngang mà phiên Á hoặc Âu đã dựng.',
      use: 'Cạnh để fade khi cân bằng; giữa range không có lệnh. Chọn phía trên hay phía dưới.' },
    ibHigh: { label: 'IB high', rank: 'cạnh',
      def: 'Mép trên của IB, biên độ giờ đầu của phiên Mỹ.',
      use: 'Cạnh: dùng để fade khi cân bằng, hoặc để công nhận cú phá bằng nến M5 đóng ngoài.' },
    ibLow: { label: 'IB low', rank: 'cạnh',
      def: 'Mép dưới của IB, biên độ giờ đầu của phiên Mỹ.',
      use: 'Cạnh: dùng để fade khi cân bằng, hoặc để công nhận cú phá bằng nến M5 đóng ngoài.' },
    highY: { label: 'High hôm qua', rank: 'cạnh ngoài',
      def: 'Mức giá cao nhất của phiên hôm qua.',
      use: 'Cạnh ngoài. Ngược bias chỉ được hấp thụ ở đây khi đuôi là tail thật, cỡ ½, ghi lý do trước.' },
    lowY: { label: 'Low hôm qua', rank: 'cạnh ngoài',
      def: 'Mức giá thấp nhất của phiên hôm qua.',
      use: 'Cạnh ngoài. Ngược bias chỉ được hấp thụ ở đây khi đuôi là tail thật, cỡ ½, ghi lý do trước.' },
    sp: { label: 'Single print (chọn phía)', rank: 'nợ',
      def: 'Mức giá chỉ có 1 TPO, tức giá đi qua rất nhanh. Chưa lấp lại thì là nợ.',
      use: 'Nợ chưa lấp là mục tiêu ưa thích của phiên; nợ cũ trả trước. Chọn phía trên hay phía dưới.' },
    poorHigh: { label: 'Poor high', rank: 'nợ',
      def: 'Đỉnh có từ 2 TPO: giá chưa bị từ chối dứt khoát ở đó.',
      use: 'Là nợ: giá hay quay lại chạm. Không phải chỗ bắt đảo chiều.' },
    poorLow: { label: 'Poor low', rank: 'nợ',
      def: 'Đáy có từ 2 TPO: giá chưa bị từ chối dứt khoát ở đó.',
      use: 'Là nợ: giá hay quay lại chạm. Không phải chỗ bắt đảo chiều.' },
    nakedPoc: { label: 'Naked POC', rank: 'chỉ mục tiêu',
      def: 'POC của phiên trước mà giá chưa chạm lại.',
      use: 'Chỉ làm nam châm mục tiêu, không dùng để bắt đảo chiều.' },
    hvnDay: { label: 'HVN ngày', rank: 'trung tính',
      def: 'Nút khối lượng cao của ngày: mức giá giao dịch dày trong phiên.',
      use: 'Trung tính. Không hấp thụ ở đây ngay sau cú phá cực trị: phép đo nghiêng về đi tiếp.' },
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
    { id: 'longest', label: 'Không trong 3 nến M1 sau nến dài nhất phiên', auto: false,
      help: { text: 'Sau nến dài nhất phiên (bất kỳ chiều) không vào lệnh trong 3 nến kế tiếp. Chờ hồi; không hồi thì bỏ.', ref: 'xung-dot' } }
  ];
  // lý do khi ô dùng chung chưa đạt (có {biến})
  var commonBad = {
    card: 'Chưa chốt thẻ phiên — không có thẻ thì không có lệnh.',
    news: 'Đang trong khung giờ cấm {hm} — còn {left}′.',
    breakerRule: 'Đã 2 lệnh phá luật trong đêm — tắt máy đến hết đêm.',
    breakerSl: 'Đã 3 SL liên tiếp — tắt máy đến hết đêm. Lệnh đóng lỗ từ 0,2R trở lên tính là SL, kể cả đóng tay (quyết định của công cụ, chưa đo).',
    open: 'Đang có lệnh mở — nhập kết quả ở Sổ trước khi vào lệnh mới.',
    longest: 'Chưa tick: vừa có nến dài nhất phiên thì chờ 3 nến M1.'
  };
  // nhãn các ô còn lại của mỗi khối (dùng trong danh sách thiếu và dòng Sổ)
  var itemLabels = {
    side: 'Hướng', zone: 'Vùng', nums: 'Giá vào, SL, biên độ nến', counter: 'Lý do ngược bias',
    zone2: 'Lần ≤ 2 tại vùng', slFloor: 'SL ≥ biên độ nến M1 cao nhất 5 nến', slCap: 'SL ≤ 4 giá', rr: 'R:R ≥ 1:2', size: 'Đủ vốn cho 1 hợp đồng'
  };
  var autoBad = {
    zone2: 'Đã vào 2 lần ở vùng này — không có lần thứ ba.',
    slFloor: 'SL {sl} giá nhỏ hơn nến {c6} giá — đẩy SL ra hoặc bỏ kèo.',
    slSide: 'SL nằm sai phía so với giá vào.',
    slCap: 'Khoảng SL {sl} giá, quá 4 giá — bỏ kèo hoặc chờ hồi sâu hơn.',
    rr: 'R:R 1:{rr} dưới 1:2 — bỏ kèo.',
    rrNext: 'Vùng kế tiếp quá gần: R:R tới vùng đó dưới 1:2 — bỏ kèo.',
    tpPast: 'TP vượt vùng kế tiếp quá 0,5 giá — kéo TP về vùng đó.',
    counter: 'Ngược bias {bias}: ghi lý do ở ô bên dưới trước khi vào (luật cứng, mục 2.2).',
    size: 'Vốn × rủi ro chưa đủ 1 hợp đồng MGC với SL này. Với vốn {cap} $ · rủi ro {pct} %, SL tối đa {max} giá. Bỏ kèo, hoặc tăng vốn.',
    noCapital: 'Cài vốn và % rủi ro để tính số hợp đồng.'
  };

  var halfText = {
    BIAS_NONE: 'bias KHÔNG', SCENARIO_C: 'fade cạnh (C)', COUNTER_BIAS: 'ngược bias', NEWS_DAY: 'ngày có tin lớn',
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
    accept: { text: 'Công nhận cú phá cần hai bước: nến M5 đóng ngoài cạnh, rồi nhịp hồi về cạnh giữ được. Thiếu bước 2 thì chỉ là chạm.', ref: 'acceptance', gloss: 'acceptance' },
    uv: { text: 'U là phe hồi yếu: từ 3 nến M1, thoải, delta hồi yếu dần, không nến nào dài bằng nến dài nhất của move. V là phe hồi đang thắng.', ref: 'v-hay-u', gloss: 'hinh-dang' },
    bubble: { text: 'Không vào ngược phe bong bóng khi mức còn giữ (vòng trắng). Mức vỡ (mờ) thì mới được vào ngược.', ref: 'bong-bong-phe', gloss: 'bong-bong' },
    absorb: { text: 'Hấp thụ chỉ khi cả thân nến và độ lớn delta giảm dần qua 3 nến. Tăng dần là đà.', ref: 'than-delta', gloss: 'hap-thu' },
    dma: { text: 'DMA đi ngang khi giá còn chạy nghĩa là đà đang cạn.', ref: 'kb-b', gloss: 'dma' },
    trap: { text: 'Phe hồi thử ở đỉnh nhịp hồi mà thất bại: bong bóng hấp thụ phe hồi, hoặc nến hồi có delta thuận nhưng đóng dưới nửa thân.', ref: 'kb-d', gloss: 'trap' },
    edge: { text: 'Cạnh là mép của VA Âu hoặc của range. Ở cạnh là cách vùng không quá 1 giá, hoặc râu chạm vùng.', ref: 'canh-hay-lung', gloss: 'canh' },
    sl: { text: 'SL lai: cấu trúc cộng 0,3 giá đệm. Sau đó máy kiểm sàn nhiễu (SL không nhỏ hơn nến M1 cao nhất 5 nến) và trần 4 giá.', ref: 'luat-sl' },
    fadeWick: { text: 'Phá hụt: râu xuyên cạnh rồi nến đóng lại trong. Không có nến đóng lại thì không vào.', ref: 'kb-c', gloss: 'fade' }
  };
  var blocks = {
    A: { title: 'Phá hồi', target: '3R', note: 'Phá khỏi cân bằng rồi hồi về cạnh vừa phá.',
      ctx: [
        { t: 'Có 1 nến M5 đóng ngoài cạnh (VA Âu, IB hoặc vùng đã kẻ)', help: HELP.accept },
        { t: 'Nhịp hồi về cạnh giữ được, không nến M5 nào đóng ngược vào trong', help: HELP.accept },
        { t: 'Bias cùng chiều phá' },
        { t: 'Cú phá không rơi vào 18:00–{comex}', help: { text: 'Từ 18:00 đến giờ COMEX mở hay có phá giả ngay trước giờ COMEX. Thấy phá giờ này: nghi trước, tin sau.', ref: 'thoi-gian', gloss: 'pha-gia' } }
      ],
      chk: [
        { t: 'Hồi hình U, ≥ 3 nến, không phải V', short: 'U', help: HELP.uv },
        { t: 'Tại cạnh: delta cùng chiều phá hoặc bong bóng hấp thụ phe ngược', short: 'Δ', help: HELP.bubble },
        { t: 'Bong bóng to gần nhất không ngược phe còn giữ', short: 'bb', help: HELP.bubble },
        { t: 'Giá cách cạnh ≤ 1 giá', short: 'cạnh', help: HELP.edge }
      ],
      ent: [{ t: 'Nến M1 đóng theo chiều phá, thân ≥ nửa biên độ, delta cùng dấu' }],
      sl: [{ t: 'SL sau râu nến xác nhận hoặc mép xa vùng (cái xa hơn) + 0,3 giá', help: HELP.sl }] },
    B: { title: 'Hấp thụ', target: '3R', note: 'Vùng hạng 2 thì cỡ ½.',
      ctx: [
        { t: 'Giá tại VWAP tuần, VWAP ngày, HVN tuần, cụm POC, hoặc cạnh VA Âu khi đang cân bằng', help: { text: 'VWAP tuần là hạng 1 (tốt nhất). VWAP ngày, HVN tuần, cụm POC là hạng 2: cỡ ½. Cạnh VA Âu chỉ khi đang cân bằng.', ref: 'xep-hang-vung', gloss: 'hang' } },
        { t: 'Không phải HVN 3 tuần, LVN, HVN ngày', help: { text: 'HVN 3 tuần và LVN là vùng cấm fade. HVN ngày ngay sau cú phá cực trị: phép đo nghiêng về đi tiếp.', ref: 'xep-hang-vung', gloss: 'hvn' } },
        { t: 'Không đang phá VWAP / cạnh theo chiều move (nếu có là phá hồi — dùng A)', help: { text: 'Hấp thụ và phá hồi cùng lúc thì theo phá hồi. Không cản tàu khi tàu vừa qua cạnh.', ref: 'xung-dot', gloss: 'pha-hoi' } },
        { t: 'Không ngay sau nến dài nhất phiên' }
      ],
      chk: [
        { t: '3 nến cuối: thân và |delta| giảm dần, không cực trị mới', short: 'giảm dần', help: HELP.absorb },
        { t: 'Bong bóng ở cực trị cùng phe với lệnh', short: 'bb', help: HELP.bubble },
        { t: 'DMA đi ngang', short: 'DMA', help: HELP.dma },
        { t: 'Giá cách vùng ≤ 1 giá', short: 'cạnh', help: HELP.edge }
      ],
      ent: [{ t: 'Nến xác nhận ngược chiều move, delta đảo dấu ≥ ½ delta nến lớn nhất của move', help: HELP.absorb }],
      sl: [{ t: 'SL sau cực trị của cụm hấp thụ + 0,3 giá, không ở giữa cụm', help: HELP.sl }] },
    C: { title: 'Fade cạnh', target: '2R', note: 'Luôn cỡ ½.',
      ctx: [
        { t: 'Giá ở đúng cạnh VA Âu / range (≤ 1 giá), không ở giữa range', help: HELP.edge },
        { t: 'Chưa có nến M5 nào đóng ngoài cạnh', help: HELP.accept }
      ],
      chk: [
        { t: 'Phá hụt: râu xuyên cạnh rồi đóng lại trong', short: 'phá hụt', help: HELP.fadeWick },
        { t: 'Delta ủng hộ chiều vào', short: 'Δ' },
        { t: 'Bong bóng to gần nhất không ngược phe còn giữ', short: 'bb', help: HELP.bubble }
      ],
      ent: [{ t: 'Nến M1 đóng lại trong range; thân không ngắn, râu ngược không dài', help: HELP.fadeWick }],
      sl: [{ t: 'SL sau râu phá hụt + 0,3 giá', help: HELP.sl }] },
    D: { title: 'Trap', target: '2R', note: 'Sau move rõ, phe hồi thử rồi thất bại.',
      ctx: [
        { t: 'Có move rõ ≥ 5 giá cùng chiều bias' },
        { t: 'Không đang đi ngang' },
        { t: 'Nhịp hồi ngược tới một vùng, chưa quá 70 % move' }
      ],
      chk: [
        { t: 'Đỉnh hồi có bong bóng hấp thụ phe hồi, hoặc nến hồi delta thuận mà đóng dưới nửa thân', short: 'bẫy', help: HELP.trap },
        { t: 'Hồi hình U, không phải V', short: 'U', help: HELP.uv }
      ],
      ent: [{ t: 'Nến M1 đóng theo chiều move cũ, thân dài, delta cùng dấu' }],
      sl: [{ t: 'SL sau đỉnh nhịp hồi + 0,3 giá', help: HELP.sl }] }
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
    // --- chung ---
    appTitle: 'Trạm Đêm Vàng', skip: 'Bỏ qua, tới nội dung chính', yes: 'Có', no: 'Không', notYet: 'Chưa', cancel: 'Hủy', confirm: 'Đồng ý', close: 'Đóng',
    on: 'Bật', off: 'Tắt', remove: 'Xóa', add: 'Thêm', helpLabel: 'Trợ giúp', helpLink: 'Mở mục này trong Hệ thống Đêm Vàng',
    biasBuy: 'BUY', biasSell: 'SELL', biasNone: 'KHÔNG', biasWait: 'CHỜ', biasUnknown: 'chưa đủ dữ liệu',
    sideUpper: 'phía trên', sideUpperOpt: 'Phía trên', sideLowerOpt: 'Phía dưới', sideLower: 'phía dưới', dirUp: 'lên', dirDown: 'xuống', thinUp: 'Trend lên', thinDown: 'Trend xuống', overridden: '(đổi tay)',
    unitGia: 'giá', newVersion: 'Có bản mới.', reload: 'Tải lại',
    // --- thanh trạng thái ---
    clock: '{hm} VN', nextWindow: 'Khung giờ cấm kế tiếp: {hm} ({min}′)', inWindow: 'ĐANG TRONG KHUNG GIỜ CẤM {hm} — còn {left}′', noWindow: 'Đêm nay không còn khung giờ cấm',
    biasChip: 'BIAS {v}', chipBreaks: 'Phá luật {n} trên 2', chipStreak: 'SL liên tiếp {n} trên 3', chipOpen: 'Lệnh mở {n} trên 1', chipOpenPaper: 'Lệnh mở {n} trên 1 (luyện mắt)', chipZone: 'Vùng này {n} trên 2 lần',
    chipBreaksTip: 'Số lệnh phá luật trong đêm. Đủ 2 lệnh thì tắt máy đến hết đêm.', chipStreakTip: 'Số SL liên tiếp ở cuối sổ. Đủ 3 thì tắt máy đến hết đêm. Lệnh đóng lỗ từ 0,2R trở lên tính là SL, kể cả đóng tay (quyết định của công cụ, chưa đo).',
    chipOpenTip: 'Chỉ được một lệnh mở cùng lúc.', chipZoneTip: 'Mỗi vùng chỉ vào tối đa 2 lần.',
    statusToggle: 'Trạng thái', winterChip: 'Mỹ mùa đông +1h',
    // --- thẻ phiên ---
    cardTitle: 'Thẻ phiên', cardDate: 'Ngày', cardVwap: 'VWAP tuần', cardClose: 'Đóng hôm qua', cardShape: 'Hình hôm qua', cardBias: 'BIAS', cardMode: 'Chế độ',
    cardZones: 'VÙNG', cardDebt: 'NỢ', cardBanned: 'VÙNG CẤM', cardNote: 'Kịch bản nền', cardPlanNote: 'Ghi chú', cardPlan1: 'Kế hoạch 1', cardPlan2: 'Kế hoạch 2', cardCancel: 'Hủy khi',
    cardNone: '—', halfNote: 'Cỡ ½ vì: {why}.', halfNoteMin: 'Lẽ ra cỡ ½ vì: {why}; không chia được.', copyShape: 'hình 3 tuần', cardLocked: 'Đã chốt lúc {hm}', cardNotLocked: 'Chưa chốt', cardToggle: 'Thẻ phiên',
    // --- tầng 0 ---
    t0Lead: 'Làm trước 18:00, xong trong một phút.',
    t0Alert: 'Tỉnh táo, không bực dọc?',
    t0ViewOnly: 'Cả đêm chỉ xem: ENTRY hiện xám, không vào lệnh thật. Bạn vẫn ghi kèo luyện mắt để có số R.',
    newsTitle: 'Tin tối nay', newsUpdated: 'cập nhật lúc {hm}', newsNone: 'Tối nay không có tin USD mức cao hoặc vừa.', newsNoFeed: 'Chưa tải được lịch tin — đang dùng mốc mặc định.',
    newsStaleBar: 'Không có lịch tin cho đêm nay — tự kiểm Forex Factory. Đang dùng khung giờ mặc định.',
    newsStaleNote: 'Lịch tải cách đây {min}′: giờ tin vẫn đúng, số thực tế có thể chậm.',
    impHigh: 'cao', impMed: 'vừa', warnOnlyTag: 'chỉ cảnh báo', newsNums: 'dự báo {f} · kỳ trước {p} · thực tế {a}',
    rowCore: 'Mặc định: giờ mở chính', row1930: 'Mặc định: tin 19:30', rowCustom: 'Thêm tay', rowFomc: 'FOMC (thêm tay)',
    newsDayTag: 'Đêm có tin lớn — cỡ ½', newsDayOff: 'Đêm có tin lớn: đã tắt tay', newsDayOffBtn: 'Tắt', newsDayOnBtn: 'Bật lại',
    newsSkipped: 'Tin chưa có giờ, bỏ qua: {list}.',
    offAt: 'đã tắt lúc {hm}', winShort: '±{n}′',
    offConfirmTitle: 'Tắt khung giờ cấm?', offConfirmText: 'Tắt khung giờ {hm} sẽ ghi lại giờ tắt. Chắc chắn?', offConfirmOk: 'Tắt khung giờ',
    nyseRow: 'NYSE mở (±5′): chỉ cảnh báo', alwaysOn: 'luôn bật',
    addManual: 'Thêm tay…', addWindow: 'Thêm khung giờ', timePh: 'giờ VN (hh:mm)', rank1: 'Hạng 1', rank2: 'Hạng 2', minBefore: 'phút trước', minAfter: 'phút sau', addFomc: 'Thêm FOMC {fomc}',
    badTime: 'Giờ chưa đúng dạng giờ:phút.', newsDay: 'Hôm nay có tin lớn (NFP, CPI)',
    t0Note: 'Kịch bản nền (tùy chọn)', t0NotePh: 'Một dòng',
    t0Done: 'Xong tầng 0 — sang kẻ vùng',
    priceFar: 'Giá lệch quá {n} giá so với giá vào dự kiến {ref}. Kiểm lại, có thể bạn gõ đè lên số cũ.', priceDigits: 'Giá có quá 6 chữ số. Kiểm lại, có thể bạn gõ đè lên số cũ.',
    quickPh: 'Gõ nhanh: vwapw 4205, vah 4199, val 4185, hvn 4195', quickHint: 'Enter để thêm. Mã: vwapw vwapd vah val poc hvn hvn3 lvn high low npoc ibh ibl ph pl; spu spl reu rel (u trên, l dưới); hvn 4195-4197 cho vùng.',
    quickBad: 'Không hiểu: {list}.', quickFull: 'Chỉ còn chỗ cho {n} vùng.',
    newsChip: 'Tin kế {hm} · {name} · còn {min}′', fxChip: 'Tin {ccy} mức cao {hm}',
    // --- tầng 1 ---
    t1Lead: 'Kẻ vùng trên chart A rồi chốt thẻ phiên. Không có thẻ phiên thì không có lệnh.',
    t1Draw: 'Kẻ trên chart A: High · VAH · POC · VAL · Low hôm qua · VWAP tuần và ngày · HVN / LVN · nợ (single print, poor high / low) · VAH Âu, VAL Âu.',
    t1Title2: 'Ba câu hỏi và bias', tailQ: 'Tail thật?', planNote: 'Ghi chú kế hoạch (tùy chọn)', planNotePh: 'Nếu … thì … ; hủy khi …', addNote: 'Thêm ghi chú',
    vwapQ: 'Giá hiện tại so với VWAP tuần', vwapHelp: 'Sát nghĩa là cách VWAP tuần không quá 2 giá. Sát thì bias CHỜ.',
    recheck: 'Chốt lại bias: đã có 1 nến M5 đóng rõ', rcAbove: 'Phía trên', rcBelow: 'Phía dưới', editRecheck: 'Chốt lại bias sau nến M5',
    t1BiasHelp: 'Bias chỉ lấy từ VWAP tuần và giá đóng hôm qua so với VA. Đổi bằng tay được nhưng phải có lý do.',
    biasIs: 'Bias', autoWas: '(tự động: {v})', overrideTitle: 'Đổi bias bằng tay (cần lý do)', overridePh: 'Lý do đổi bias', overrideNeed: 'Chưa có lý do thì bias vẫn là bias tự động.',
    editOverride: 'Đổi bias bằng tay', editOverrideReason: 'Lý do đổi bias',
    t1Title4: 'Vùng ({n}/5)', t1ZoneHelp: 'Chọn 3–5 vùng. Hạng và cờ của vùng tự suy theo loại.',
    price: 'Giá', priceTo: 'đến giá', zoneType: 'Loại vùng', addZone: 'Thêm vùng', needPrice: 'Nhập giá của vùng.', zonesFull: 'Đã đủ 5 vùng.',
    zonesFew: 'Dưới 3 vùng: vẫn chốt được, nhưng ít chỗ để vào.', noZones: 'Chưa có vùng nào.',
    addedZone: 'Thêm vùng {t}', editZone: 'Sửa vùng {z}', delZone: 'Xóa vùng {z}', editQ: '{q}: {v}',
    t1Title5: 'Chốt thẻ phiên', 
    t1CardHelp: 'Thẻ phiên chốt xong mới mở tầng 3. Sau {comex} mỗi lần sửa thẻ đều ghi lại giờ sửa.',
    lockCard: 'Chốt thẻ phiên', lockNeed: 'Còn thiếu: {list}', need_q1: 'Q1 (hình hôm qua)', need_q5: 'Q5 (đóng hôm qua so với VA)', need_q6: 'Q6 (Âu dựng range)', need_vwapW: 'VWAP tuần', need_zones: 'ít nhất 1 vùng',
    lockWhy: 'Chưa chốt thì tầng 3 khóa.', locked: 'Đã chốt thẻ phiên.', toTier2: 'Sang tầng 2', editAfterLock: 'Sau chốt vẫn sửa được; sửa sau {comex} sẽ ghi lại giờ sửa.',
    // --- tầng 2 ---
    t2Lead: 'Gọi tên chế độ trước khi gọi tên kịch bản. Cùng một tín hiệu M1 mang nghĩa trái ngược tùy chế độ.',
    t2Title1: 'Chế độ thị trường', t2Mode: 'Chế độ', t2ModeHelp: 'Phá chỉ được công nhận khi có nến M5 đóng ngoài cạnh và nhịp hồi giữ được. Thiếu bước 2 thì chỉ là chạm.',
    modeBalancedSub: 'fade cạnh, hấp thụ tại cạnh', modeBrokenSub: 'phá hồi, hấp thụ theo chiều', modeThinSub: 'không cản tàu',
    thinDir: 'Hướng Trend thin', thinDirNeed: 'Chọn hướng Trend thin.',
    boDir: 'Hướng phá', breakUp: 'Phá lên', breakDown: 'Phá xuống', boEdge: 'Cạnh vừa phá', boEdgeHelp: 'Chọn từ thẻ phiên. Phá hồi sẽ tự điền vùng này.',
    boFailedNote: 'Đã phá hụt {n} lần — không đuổi, chờ lần {next}.',
    boStep1: '1 nến M5 đóng ngoài cạnh', acceptHelp: 'Công nhận cú phá cần hai bước: nến M5 đóng ngoài cạnh, rồi nhịp hồi về cạnh giữ được.',
    boStep2: 'Hồi về cạnh giữ được', needStep1: 'Cần bước 1 trước', boFailed: 'Chui lại trong (phá hụt)', 
    effective: 'Chế độ đang áp dụng',
    t2Title2: 'Nến dài nhất phiên', longestBar: 'Vừa có nến dài nhất phiên', reopenAt: 'Mở lại {hm}', clearLongest: 'Bỏ khóa',
    
    t2LongestHelp: 'Sau nến dài nhất phiên (bất kỳ chiều), công cụ khóa ba phút. Hết khóa mới xét kèo.',
    t2Title3: 'Kịch bản nào đang bật', enabled: 'bật', 
    t2TableHelp: 'Mỗi kịch bản có điều kiện chế độ riêng. Cú phá chưa công nhận thì phá hồi chưa bật.', toTier3: 'Sang tầng 3 — kèo',
    lock_NO_CARD: 'Chưa chốt thẻ phiên — không có thẻ thì không có lệnh.', lock_BIAS_WAIT: 'Bias đang CHỜ — chốt lại bias ở tầng 1 trước.',
    lock_OPEN_TRADE: 'Đang có lệnh mở — tầng 3 khóa cho tới khi đóng lệnh.', lock_NO_OPEN: 'Chưa có lệnh nào đang mở.',
    lockGo_NO_CARD: 'Về tầng 1', lockGo_BIAS_WAIT: 'Về tầng 1', lockGo_OPEN_TRADE: 'Sang tầng 4',
    // --- tầng 3 ---
    t3Hint: 'Canh trước khi nến xác nhận đóng; Bấm sau khi nến đóng.', canhTitle: 'Canh', bamTitle: 'Bấm', canhHint: 'Làm lúc còn thời gian.', bamHint: 'Ba việc: nến xác nhận, giá vào, SL.',
    canhSummary: '{scen} · {zone} · {side}', clearAll: 'Xóa hết', clearAllDone: 'Đã xóa cả kèo.',
    newSetup: 'Kèo mới', newSetupDone: 'Kèo mới: giữ kịch bản, vùng, C6; đã xóa các câu quan sát.', idleNote: 'Đã hơn 10′ không thao tác — nến M1 đã khác, kiểm lại.',
    offShort: 'tắt', pickScenario: 'Chọn một kịch bản đang bật để bắt đầu.', scenSummary: '{name} · mục tiêu {tp} · be {be}', scenImgAlt: 'Ví dụ kịch bản {name}',
    c3NoEdge: 'Chưa chọn cạnh vừa phá ở tầng 2', autoFilled: '(tự điền)', nthAt: 'Lần thứ {n} tại vùng', 
    counterBias: 'Ngược bias: {tp}', counterOk: 'được phép, cỡ ½, TP 2R', counterBad: 'không được phép', counterPh: 'Lý do ngược bias', c4numPh: '±số',
    entryL: 'Giá vào', slL: 'SL', tpL: 'TP', tpAuto: 'gợi ý', c6Again: 'Biên độ nến M1 cao nhất (sửa tại đây)',
    calcNone: 'Chọn kịch bản để tính SL và R:R.', calcNeed: 'Nhập giá vào và SL ở bước Bấm.', calcSl: 'SL {v} giá', calcRr: 'R:R 1:{v}', calcTpSug: 'TP gợi ý {v}',
    sizeTitle: 'Cỡ lệnh MGC', sizeNoCfg: 'chưa cài vốn', sizeZero: '0 hợp đồng', sizeN: '{n} hợp đồng',
    sizeCalc: 'Vốn {cap} $ · rủi ro {pct} % = {full} $. Mỗi hợp đồng rủi ro {per} $ với SL này. Làm tròn xuống.', sizeHalf: 'Cỡ ½ vì: {why}, nên chỉ rủi ro {usd} $.',
    sizeHalfMin: 'Cỡ ½ ({why}) không chia được: vào 1 hợp đồng, rủi ro thật {real} $ (hơn ½ kế hoạch).',
    dotsLabel: '{n} trên 8 điều kiện đã đạt', vWait: 'CHỜ', missingLabel: 'thiếu:', vNo: 'KHÔNG VÀO', vOff: 'TẮT MÁY', vLocked: 'Có lệnh mở.', moreCodes: '(+{n} lý do nữa)',
    forceBtn: 'Tôi vẫn vào (phá luật)', forceNeed: 'Cần có hướng, giá vào và SL trước.', entryView: 'ENTRY (chỉ xem)', paperBtn: 'Ghi kèo luyện mắt', enterBtn: 'Vào lệnh',
    slGia: '{v} giá', sizeHalfShort: 'cỡ ½', sizeFull: 'cỡ đủ', counterTag: 'ngược bias · 2R · ½', 
    enterTitle: 'Vào lệnh', enterKind: 'Kiểu vào', enterPrice: 'Giá', enterMarketHint: 'market: khớp ngay, giá khớp thật là giá vào.',
    enterLimitHint: 'limit: để giá chờ; khi khớp bấm "Khớp rồi", giá bỏ đi thì hủy.', enterConfirm: 'Xác nhận vào lệnh',
    entered: 'Đã ghi lệnh vào sổ.', enteredPaper: 'Đã ghi kèo luyện mắt.', forcedToast: 'Đã ghi lệnh phá luật vào sổ.',
    forceTitle: 'Vào lệnh phá luật?', forceText: 'Phán quyết đang là: {list}.', forceCount: 'Lệnh này tính là phá luật; 2 lệnh phá luật thì tắt máy.',
    forcePaperNote: 'Đang ở chế độ chỉ xem nên không tính phá luật.', forceOk: 'Vẫn vào, chấp nhận phá luật',
    editWhileSetupTitle: 'Đang canh kèo', editWhileSetupText: 'Sửa thẻ lúc này là nắn kế hoạch theo kèo. Vẫn sửa và ghi lại giờ sửa?', editWhileSetupOk: 'Vẫn sửa',
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
    wBreaks: 'Phá luật / tổng lệnh', wSwept: 'SL bị quét rồi tới TP', wByScen: 'R theo kịch bản', wByZone: 'R theo loại vùng', wCounter: 'Lệnh ngược bias', wStreak: 'Số đêm liên tiếp không phá luật',
    pairFmt: '{name} {n} lệnh {r} R',
    t5Export: 'Xuất và nhập', exMd: 'Tải Markdown', exMdCopy: 'Sao chép Markdown', exJson: 'Tải JSON', exCsv: 'Tải CSV', copied: 'Đã sao chép.', copyFail: 'Không sao chép được.',
    importJson: 'Nhập JSON (gộp vào dữ liệu hiện có)', importDone: 'Nhập xong: {a} đêm mới, {b} đêm gộp, {c} lệnh thêm.', exportDue: 'Cuối tuần rồi — tải JSON về để giữ bản sao.',
    t5Settings: 'Cài đặt', setTheme: 'Giao diện', themeDark: 'Tối', themeLight: 'Sáng', setGuide: 'Mức hướng dẫn', guideNew: 'Mới', guideQuen: 'Quen',
    setCapital: 'Vốn', setRisk: 'Rủi ro mỗi lệnh', setDst: 'Mốc giờ dịch theo giờ mùa đông', setDstHelp: 'Tắt thì mọi mốc luôn theo giờ mùa hè.',
    setKeys: 'Phím tắt tầng 3', keysHelp: 'Bấm ? để xem danh sách phím tắt.', wipe: 'Xóa toàn bộ dữ liệu', wipeTitle: 'Xóa toàn bộ dữ liệu?',
    wipeText: 'Mọi đêm, thẻ phiên và sổ lệnh trên máy này sẽ mất. Nên tải JSON trước.', wipeOk: 'Xóa hết', wiped: 'Đã xóa dữ liệu.', version: 'Phiên bản {v}',
    keysTitle: 'Phím tắt (tầng 3)', key0: 'Chọn kịch bản A', key1: 'Chọn kịch bản B', key2: 'Chọn kịch bản C', key3: 'Chọn kịch bản D', key4: 'Chọn hướng buy / sell (chỉ B)',
    key5: 'Nhịp hồi U / V', key6: 'Nến xác nhận đạt chuẩn', key7: 'Nút chính (Vào lệnh); Enter ở ô SL cũng vào lệnh khi ENTRY', key8: 'Kèo mới (giữ vùng, hướng, C6)', key9: 'Rời ô nhập, đóng hộp thoại', key10: 'Mở bảng phím tắt',
    // --- vòng 2 ---
    zoneHasTrades: 'Vùng này đã có lệnh trong sổ nên không xóa được (đếm 2 lần mỗi vùng).',
    glossaryBtn: 'Từ điển', glossaryTitle: 'Từ điển', glossaryHint: 'Định nghĩa ngắn các từ hay gặp. Đầy đủ ở trang Hệ thống Đêm Vàng.', openGlossary: 'Mở Từ điển',
    qPrefix: '{n} · {label}',
    vwapNowL: 'Giá hiện tại (tùy chọn)', vwapPriceL: 'VWAP tuần (tùy chọn)', 
    planConflict: 'Kế hoạch đang ngược bias {b}. Vẫn chốt được, nhưng vào lệnh ngược bias phải ghi lý do.', planConflictToast: 'Cảnh báo: kế hoạch ngược bias.',
    nightPick: 'Chọn đêm', editsOpen: '{n} lần sửa thẻ', boNeedTop: 'Chưa công nhận: chọn hướng, cạnh, rồi hai công tắc.',
    scenLocked: 'Kịch bản này đang tắt: {why}',
    storeFail: 'Không lưu được vào máy — tải JSON ngay để giữ dữ liệu.', storeFailBtn: 'Tải JSON', otherTab: 'Dữ liệu vừa đổi ở thẻ trình duyệt khác — đã tải lại.',
    
    // --- vòng 3 ---
    warnShort: 'trước {nyse} · cỡ ½', sizeMinOne: '1 hợp đồng = cỡ đủ, rủi ro {usd} $', 
    capTitle: 'Vốn và rủi ro mỗi lệnh', capText: 'Công cụ dùng hai số này để tính số hợp đồng MGC. Mặc định 2000 $ và 2 %. Đổi lại được ở tầng Sổ, mục Cài đặt.',
    capLater: 'Để sau', capSave: 'Lưu', capBad: 'Vốn và % rủi ro phải là số lớn hơn 0.', capChange: 'Đổi vốn',
    glossarySearch: 'Tìm từ…', glossaryNone: 'Không có mục nào khớp.',
    copyPrev: 'Sao chép vùng từ đêm {key}', copyPrevEdit: 'Sao chép vùng từ đêm {key}', copyPrevDone: 'Đã chép: {list}.', 
    copyPrevNone: 'Không có gì mới để chép.', 
    goTier1: 'Về tầng 1', goTier2: 'Về tầng 2',
    sideNeedZone: 'Vùng này chưa có phía (trên hay dưới). Chọn phía ở tầng 1.', sideAfterZone: 'Chọn vùng ở trên: hướng tự điền theo phía của vùng.',
    sideNeedRegime: 'Hướng lấy từ chế độ: chọn hướng phá hoặc hướng Trend thin ở tầng 2.',
    closeSlBe: 'Chạm SL (đã ở hòa vốn)', needDirEdge: 'Chọn hướng phá và cạnh vừa phá trước.',
    // --- vòng 4 ---
    
    boReset: 'Đổi hướng hoặc cạnh là một cú phá mới: công nhận lại từ bước 1.',

    sideNoneZone: 'Vùng này không có phía nên không fade được; C chỉ làm ở cạnh.'
  };

  // ===== Từ điển (định nghĩa ngắn, lấy từ trang Hệ thống Đêm Vàng; chỗ là luật của công cụ thì ghi rõ) =====
  var glossaryBase = [
    { key: 'bias', term: 'bias', def: 'Chiều ưu tiên của đêm: BUY, SELL, KHÔNG hoặc CHỜ. Chỉ lấy từ VWAP tuần và giá đóng hôm qua so với VA hôm qua; ngược bias phải ghi lý do trước khi bấm.' },
    { key: 'no', term: 'nợ', def: 'Phần giá chưa được lấp lại (single print, poor high, poor low), giá hay trở lại chạm. Đây là "nợ giá", không phải nợ tiền.' },
    { key: 'moi', term: 'mồi', def: 'Cực trị có khối lượng dày: trông như đỉnh hoặc đáy nhưng không phải bị từ chối thật, nên không coi là đỉnh hay đáy. Ví dụ: đỉnh 4210,0 chỉ 1 TPO, khối lượng thấp ⇒ tail thật; đỉnh 4208,0 khối lượng dày ⇒ mồi (ví dụ minh họa, không phải ca thật).' },
    { key: 'tail', term: 'tail thật', def: 'Cực trị chỉ có 1 TPO với khối lượng thấp: giá bị từ chối thật ở đó. Chỉ tail thật mới cho phép hấp thụ ngược bias tại High / Low hôm qua.' },
    { key: 'thin', term: 'thin', def: 'Profile mỏng, đi một chiều, chưa đấu giá xong: không đánh ngược. Chế độ "Trend thin" là không cản tàu, chỉ vào theo chiều ở nhịp hồi.' },
    { key: 'trap', term: 'trap (bẫy)', def: 'Một move rõ (từ 5 giá) cùng chiều bias, rồi nhịp hồi ngược tới một vùng. Ở đỉnh nhịp hồi phe hồi thử mà thất bại: bong bóng hấp thụ phe hồi, hoặc nến hồi có delta thuận mà đóng dưới nửa thân. Vào theo chiều move cũ, mục tiêu 2R. Ví dụ: sell, giá giảm từ 4200 xuống 4194 (6 giá), hồi lên 4197 (nửa move, dưới 70 %) rồi thất bại ⇒ sell, SL trên 4197 cộng 0,3 giá (ví dụ minh họa, không phải ca thật).' },
    { key: 'bong-bong', term: 'bong bóng', def: 'Vòng tròn trên chart M1 (chỉ báo hấp thụ và chỉ báo lệnh lớn). Tròn đặc là hấp thụ: một phe đánh market mạnh tại mức đó mà giá không đi; vòng trắng là mức còn giữ, mờ đi là mức đã vỡ. Tròn mờ có số từ 100 là lệnh lớn vừa vào; giá không rời mức thì mức đó thành vùng phòng thủ. Chỉ để kiểm tra, không phải tín hiệu vào lệnh.' },
    { key: 'dma', term: 'DMA', def: 'Chỉ báo đường trên chart M1 dùng để đọc đà (trang Hệ thống không ghi tên đầy đủ). Dốc cùng chiều move là đà còn; đi ngang khi giá còn chạy là đà đang cạn. Chỉ để kiểm tra, không phải tín hiệu vào lệnh.' },
    { key: 'be', term: 'be (hòa vốn)', def: 'Dời SL về giá vào để lệnh không lỗ nữa. Phá hồi và hấp thụ dời ở +1,5R sau 1 nến M1 đóng ngoài vùng vào; fade và trap dời ở +1R.' },
    { key: 'hang', term: 'hạng vùng', def: 'Mức ưu tiên của vùng theo phép đo. Hạng 1 là VWAP tuần; hạng 2 (VWAP ngày, HVN tuần, cụm POC) thì hấp thụ đi cỡ ½.' },
    { key: 'canh', term: 'cạnh', def: 'Mép của vùng giá trị Âu hoặc của range: VAH Âu, VAL Âu, IB, cạnh range. Ở câu hỏi "giá cách vùng", ở cạnh là cách vùng không quá 1 giá.' },
    { key: 'acceptance', term: 'acceptance (công nhận cú phá)', def: 'Giá đóng 1 nến M5 ngoài cạnh, rồi nhịp hồi về cạnh giữ được. Thiếu bước 2 thì chỉ là chạm, chưa phải phá.' },
    { key: 'hap-thu', term: 'hấp thụ', def: 'Một phe đánh market mạnh mà giá không đi: nỗ lực có, kết quả không. Chỉ gọi hấp thụ khi cả thân nến và độ lớn delta giảm dần qua 3 nến.' },
    { key: 'pha-hoi', term: 'phá hồi', def: 'Sau cú phá đã được công nhận, giá hồi hình U về cạnh vừa phá rồi đi tiếp theo chiều phá. Mục tiêu 3R.' },
    { key: 'fade', term: 'fade', def: 'Vào ngược hướng giá vừa xuyên cạnh rồi đóng lại trong (phá hụt). Là kịch bản C: cỡ nhỏ, mục tiêu 2R.' },
    { key: 'hvn', term: 'HVN / LVN', def: 'HVN là nút khối lượng cao, giá hay đi ngang; LVN là nút khối lượng thấp, giá chạy nhanh qua. HVN 3 tuần và LVN là vùng cấm fade.' },
    { key: 'mo-ao', term: 'mở ảo', def: 'Hệ thống: khoảng {comex} đến {nyse} vàng hay chạy giả, cú phá chưa đáng tin; cú phá đáng tin thường rơi vào {real1} đến {real2}; trước {nyse} chỉ fade cạnh, cỡ nhỏ. Công cụ: không tắt kịch bản, chỉ giảm cỡ còn ½ (QĐ-19, quyết định của công cụ, chưa đo).' },
    { key: 'r', term: 'R', def: 'R là khoảng rủi ro của lệnh: giá vào trừ SL. Lãi 1R bằng đúng khoảng đó, 3R gấp ba. Ví dụ: sell 4193,0, SL 4195,4 (2,4 giá) thì 1R = 2,4 giá và TP 3R ở 4185,8.' },
    { key: 'hinh-dang', term: 'hình dạng profile (D, P, b, B, thin, chữ nhật)', def: 'D: đấu giá xong, chờ phá. P: cân bằng ở đỉnh, đuôi là hỗ trợ; b ngược lại. B: hai phân phối (hai cụm khối lượng); trang Hệ thống không định nghĩa hình B. thin: mỏng, một chiều, chưa xong, không đánh ngược. Chữ nhật: cân bằng rộng, sẽ phá một đầu.' },
    { key: 'va', term: 'VA / VAH / VAL / POC', def: 'VA là vùng giá trị của một phiên. VAH là mép trên, VAL là mép dưới, POC là mức giá giao dịch nhiều nhất. Giá đóng hôm qua ngoài VA hôm qua là giá đang tìm giá trị mới; trong VA là cân bằng còn hiệu lực. VAH Âu và VAL Âu là hai cạnh mặc định để fade. (Định nghĩa TPO chuẩn; trang Hệ thống không định nghĩa.)' },
    { key: 'pha-gia', term: 'phá giả', def: 'Từ 18:00 đến {comex} hay có cú phá VA ngay trước giờ COMEX mà không đi tiếp. Thấy phá giờ này: nghi trước, tin sau. Công cụ chỉ nhắc: ở khối A có ô "Cú phá không rơi vào 18:00–{comex}" để bạn tự tick.' },
    { key: 'khung-gio-cam', term: 'khung giờ cấm (còn gọi cửa sổ cấm)', def: 'Khoảng quanh giờ tin lớn, tự lấy từ lịch Forex Factory: tin USD mức cao trước 15′ sau 15′ (hạng 1), mức vừa trước 5′ sau 5′ (hạng 2). Luôn có thêm {core} ±5′. Lịch cũ hơn 2 giờ thì dùng mặc định: {news1} ±15′ vào thứ Năm. Trong khoảng đó mọi kịch bản đều KHÔNG VÀO; lệnh đang mở thì đóng sạch trước khung giờ hạng 1.' },
    { key: 'sl-bi-quet', term: 'SL bị quét', def: 'SL bị chạm rồi giá quay lại chạy tới TP. Sổ đếm số lệnh như vậy để biết SL có đặt quá sát không (HT mục 6, 8). Lệnh vẫn tính là SL, không đổi kết quả.' }
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
    fill: fill, glossary: glossary, HT_BASE: HT_BASE, scenarios: scenarios, zoneTypes: zoneTypes, flagText: flagText, tiers: tiers,
    common: common, commonBad: commonBad, itemLabels: itemLabels, autoBad: autoBad, blocks: blocks, groupTitles: groupTitles, itemLabel: itemLabel,
    halfText: halfText, warnText: warnText, questions: questions, vwapOpts: vwapOpts,
    phases: phases, bands: bands, notices: notices, journal: journal, errors: errors,
    closeReasons: closeReasons, qd: qd, unmeasured: unmeasured, ui: ui
  };
});
