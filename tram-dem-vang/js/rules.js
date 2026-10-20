/* Trạm Đêm Vàng — LUẬT: hằng số, ma trận bias, bảng vùng, mốc giờ có múi, hình dạng 4 khối Setup Entry.
 * Thuần dữ liệu + hàm kiểm tra. Chữ hiển thị nằm ở content.js. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(function (n) { return require('./' + n + '.js'); });
  else { root.TDV = root.TDV || {}; root.TDV.rules = factory(function (n) { return root.TDV[n]; }); }
})(this, function (dep) {
  'use strict';

  var APP_VERSION = '2.1.0';
  var EPS = 1e-9;

  var T = {
    c6Max: 20,         // biên độ nến M1 hơn 20 giá ⇒ nghi gõ nhầm mức giá
    slCap: 4,          // trần khoảng SL (giá)
    rrMin: 2,          // R:R sàn 1:2
    nearGap: 1,        // vùng cùng cụm: cách nhau ≤ 1 giá
    tpPastTol: 0.5,    // TP vượt vùng kế tiếp quá 0,5 giá ⇒ R:R chưa đạt
    vwapNear: 2,       // sát VWAP tuần ±2 giá
    breakLimit: 2,     // phá luật ⇒ TẮT MÁY
    slStreakLimit: 3,  // SL liên tiếp ⇒ TẮT MÁY
    zoneMax: 2,        // tối đa 2 lần mỗi vùng
    nearOk: 1,         // giá vào cách vùng ≤ 1 giá (HT 4.4)
    nearBack: 3,       // cách vùng > 3 giá: ở lưng, bỏ kèo (HT 4.4; mục 7 thiết kế v2)
    tickValue: 10,     // MGC: 1 giá = 10 $ mỗi hợp đồng (tick 0,1 = 1 $)
    zonesMin: 3, zonesMax: 5
  };
  var TARGET_R = { A: 3, B: 3, C: 2, D: 2 };
  var TARGET_R_COUNTER_B = 2;   // HT 2.2 / QĐ-16: hấp thụ ngược bias chỉ 2R
  var BE_R = { A: 1.5, B: 1.5, C: 1, D: 1 };
  var HALF_ORDER = ['BIAS_NONE', 'SCENARIO_C', 'COUNTER_BIAS', 'NEWS_DAY', 'B_RANK2', 'BEFORE_2030'];
  var SCENARIOS = ['A', 'B', 'C', 'D'];
  // số checkbox từng nhóm của mỗi khối (id ô = ctx1.., chk1.., ent1, sl1); chữ ở content.js → blocks.
  // Các ô máy tính được (bias, giờ phá, giá cách vùng) KHÔNG còn là ô tick: chúng là ô tự kiểm trong engine.
  var BLOCK_SHAPE = {
    A: { ctx: 2, chk: 3, ent: 1, sl: 1 },
    B: { ctx: 5, chk: 4, ent: 1, sl: 1 },
    C: { ctx: 3, chk: 3, ent: 1, sl: 1 },
    D: { ctx: 3, chk: 3, ent: 1, sl: 1 }
  };
  var GROUPS = ['ctx', 'chk', 'ent', 'sl'];
  function tickIds(scen) {
    var s = BLOCK_SHAPE[scen], out = [];
    GROUPS.forEach(function (g) { for (var i = 1; i <= s[g]; i++) out.push({ id: g + i, group: g }); });
    return out;
  }

  // Mốc giờ có múi gốc (viết theo giờ VN khi Mỹ / London đang giờ mùa hè)
  var MARKS = {
    prep: { at: '18:00', tz: 'VN' }, comex: { at: '19:20', tz: 'ET' }, news1: { at: '19:30', tz: 'ET' },
    nyse: { at: '20:30', tz: 'ET' }, core: { at: '21:00', tz: 'ET' }, ldnClose: { at: '22:30', tz: 'LONDON' },
    thin: { at: '23:00', tz: 'VN' }, settle: { at: '00:30', tz: 'ET' }, globexMaint: { at: '04:00', tz: 'ET' }
  };

  // Khung giờ cấm mặc định (QĐ-6) — chỉ dùng khi KHÔNG có lịch tin; có lịch thì chỉ tin thật tạo khung (QĐ-22, sửa 20/10)
  // 19:30 mặc định chỉ bật thứ Năm (on1930); ngoài ra engine tự coi là bật khi chưa qua tầng 0 hoặc ngày có tin (effectiveWindows)
  function defaultWindows(on1930) {
    return [
      { id: 'w1930', kind: 'news', rank: 1, at: '19:30', tz: 'ET', minutesBefore: 15, minutesAfter: 15, on: !!on1930 },
      { id: 'w2100', kind: 'news', rank: 2, at: '21:00', tz: 'ET', minutesBefore: 5, minutesAfter: 5, on: true }
    ];
  }
  // newsDay hiệu lực: người dùng đã chọn tay (newsDaySet) thì theo tay; không thì theo lịch Forex Factory khi lịch còn mới (QĐ-22)
  function effectiveNewsDay(t0, news) {
    var t = t0 || {};
    if (t.newsDaySet) return !!t.newsDay;
    if (news && (news.status === 'ok' || news.status === 'stale') && news.newsDay) return true;
    return !!t.newsDay;
  }
  // Khung giờ áp dụng: khung nhập tay / mặc định + khung tự sinh từ lịch (news.windows, khi lịch còn mới).
  // 19:30 mặc định: bật khi w.on, hoặc (chưa bị tắt tay) khi chưa qua tầng 0 / ngày có tin lớn. Khi lịch có dữ liệu thì 19:30 mặc định
  // không còn tự bật (chỉ có khung riêng của tin có thật). Khung tự sinh tắt được: t0.newsOverrides[id] = { on: false, offAt }.
  function effectiveWindows(t0, key, news) {
    var t = t0 || {};
    var list = t.windows;
    if (!list) { var th = key ? dep('time').isThursday(key) : false; list = defaultWindows(th); }
    var ok = !!(news && (news.status === 'ok' || news.status === 'stale'));
    var nd = effectiveNewsDay(t, news);
    var out = list.filter(function (w) { return !(ok && (w.id === 'w1930' || w.id === 'w2100')); }).map(function (w) {
      if (w.id !== 'w1930') return w;
      var on = !!w.on || (!w.offAt && (!t.touched || !!nd));
      if (on === !!w.on) return w;
      var o = {}; for (var k in w) o[k] = w[k]; o.on = on; o.auto = true; return o;
    });
    if (ok) {
      var ov = t.newsOverrides || {};
      news.windows.forEach(function (w) {
        var x = {}; for (var k in w) x[k] = w[k];
        var o = ov[w.id];
        if (o && o.on === false) { x.on = false; if (o.offAt) x.offAt = o.offAt; }
        out.push(x);
      });
    }
    return out;
  }
  var NYSE_WARN = { at: '20:30', tz: 'ET', minutesBefore: 5, minutesAfter: 5 };

  // Bảng loại vùng: cờ, phía
  var ZONE_TYPES = {
    vwapW: { flags: ['r1'] },
    vwapD: { flags: ['r2'] },
    hvnW: { flags: ['r2'] },
    pocCluster: { flags: ['r2'] },
    vahEu: { flags: ['edge'], side: 'upper' },
    valEu: { flags: ['edge'], side: 'lower' },
    rangeEdge: { flags: ['edge'], needSide: true },
    ibHigh: { flags: ['edge'], side: 'upper' },
    ibLow: { flags: ['edge'], side: 'lower' },
    highY: { flags: ['edgeOuter'], side: 'upper', tailFrom: 'q2top' },
    lowY: { flags: ['edgeOuter'], side: 'lower', tailFrom: 'q2bot' },
    sp: { flags: ['sp'], needSide: true },
    poorHigh: { flags: [], side: 'upper' },
    poorLow: { flags: [], side: 'lower' },
    nakedPoc: { flags: [] },
    hvnDay: { flags: ['noB'] },
    hvn3w: { flags: ['banned'] },
    lvn: { flags: ['banned'] }
  };
  var ZONE_ORDER = ['vwapW', 'vwapD', 'hvnW', 'pocCluster', 'vahEu', 'valEu', 'rangeEdge', 'ibHigh', 'ibLow', 'highY', 'lowY', 'sp', 'poorHigh', 'poorLow', 'nakedPoc', 'hvnDay', 'hvn3w', 'lvn'];

  function num(v) { return (typeof v === 'number' && isFinite(v)) ? v : null; }
  function round1(x) { return Math.round(x * 10) / 10; }
  function round2(x) { return Math.round(x * 100) / 100; }

  // Làm giàu vùng: lo/hi, cờ, phía
  function enrichZone(z, answers) {
    var t = ZONE_TYPES[z.type] || { flags: [] };
    var flags = (t.flags || []).slice();
    var sideKind = t.side || (t.needSide ? (z.side === 'upper' || z.side === 'lower' ? z.side : null) : null);
    if (t.tailFrom && answers && answers[t.tailFrom] === 'tail') flags.push('tail');
    var a = num(z.price), b = num(z.priceTo);
    if (a === null && b !== null) { a = b; b = null; }
    var lo = a, hi = a;
    if (a !== null && b !== null) { lo = Math.min(a, b); hi = Math.max(a, b); }
    var out = {}; for (var k in z) out[k] = z[k];
    out.flags = flags; out.sideKind = sideKind; out.lo = lo; out.hi = hi;
    return out;
  }
  function zoneGap(a, b) {
    if (a.lo === null || b.lo === null) return Infinity;
    return Math.max(0, Math.max(a.lo, b.lo) - Math.min(a.hi, b.hi));
  }
  function hasFlag(z, f) { return !!z && z.flags.indexOf(f) >= 0; }

  // Ma trận bias (HT 2.2 + QĐ-12). answers: {vwapW, q5, q1}; bias: {rechecked}
  function autoBias(answers, biasState) {
    var a = answers || {};
    var w = a.vwapW;
    if (w === 'near' && biasState && (biasState.rechecked === 'above' || biasState.rechecked === 'below')) w = biasState.rechecked;
    if (!w) return null;
    if (w === 'near') return 'CHỜ';
    if (!a.q5) return null;
    if (w === 'above') {
      if (a.q5 === 'below') return 'KHÔNG';
      if (!a.q1) return null;
      return a.q1 === 'b' ? 'KHÔNG' : 'BUY';
    }
    if (a.q5 === 'above') return 'KHÔNG';
    if (!a.q1) return null;
    return a.q1 === 'P' ? 'KHÔNG' : 'SELL';
  }
  // Bias hiệu lực: ghi đè (cần lý do) hoặc tự động
  function effectiveBias(card) {
    var b = (card && card.bias) || {};
    var auto = autoBias(card && card.answers, b);
    // ghi đè bằng đúng bias tự động không phải là ghi đè (REVIEW-3 mục 7)
    if (b.override && b.reason && String(b.reason).trim() && b.override !== auto) return { value: b.override, auto: auto, overridden: true };
    return { value: auto, auto: auto, overridden: false };
  }
  function isCounter(bias, side) { return (bias === 'BUY' && side === 'sell') || (bias === 'SELL' && side === 'buy'); }

  return {
    APP_VERSION: APP_VERSION, T: T, EPS: EPS, TARGET_R: TARGET_R, TARGET_R_COUNTER_B: TARGET_R_COUNTER_B, BE_R: BE_R, HALF_ORDER: HALF_ORDER, SCENARIOS: SCENARIOS,
    BLOCK_SHAPE: BLOCK_SHAPE, GROUPS: GROUPS, tickIds: tickIds,
    MARKS: MARKS, NYSE_WARN: NYSE_WARN, defaultWindows: defaultWindows, effectiveWindows: effectiveWindows, effectiveNewsDay: effectiveNewsDay,
    ZONE_TYPES: ZONE_TYPES, ZONE_ORDER: ZONE_ORDER,
    enrichZone: enrichZone, zoneGap: zoneGap, hasFlag: hasFlag,
    autoBias: autoBias, effectiveBias: effectiveBias, isCounter: isCounter, num: num, round1: round1, round2: round2
  };
});
