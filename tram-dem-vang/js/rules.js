/* Trạm Đêm Vàng — LUẬT: hằng số, ma trận bias, bảng vùng, mốc giờ có múi, danh sách luật CÓ THỨ TỰ.
 * Thuần dữ liệu + hàm kiểm tra. Chữ hiển thị nằm ở content.js. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(function (n) { return require('./' + n + '.js'); });
  else { root.TDV = root.TDV || {}; root.TDV.rules = factory(function (n) { return root.TDV[n]; }); }
})(this, function (dep) {
  'use strict';

  var APP_VERSION = '1.0.5';
  var EPS = 1e-9;

  var T = {
    c6Max: 20,         // biên độ nến M1 hơn 20 giá ⇒ nghi gõ nhầm mức giá
    slCap: 4,          // trần khoảng SL (giá)
    slPad: 0.3,        // đệm SL
    rrMin: 2,          // R:R sàn 1:2
    nearGap: 1,        // "cạnh": cách vùng ≤ 1 giá
    farGap: 3,         // "lưng": từ 3 giá
    tpPastTol: 0.5,    // TP vượt vùng kế tiếp quá 0,5 giá ⇒ NO_TP_PAST_ZONE
    moveMin: 5,        // move tối thiểu cho Trap (giá)
    vwapNear: 2,       // sát VWAP tuần ±2 giá
    breakLimit: 2,     // phá luật ⇒ TẮT MÁY
    slStreakLimit: 3,  // SL liên tiếp ⇒ TẮT MÁY
    zoneMax: 2,        // tối đa 2 lần mỗi vùng
    maxOpen: 1,
    idleMinutes: 10,   // sau 10′ không thao tác ⇒ nhắc kiểm lại
    tickValue: 10,     // MGC: 1 giá = 10 $ mỗi hợp đồng (tick 0,1 = 1 $)
    zonesMin: 3, zonesMax: 5
  };
  var TARGET_R = { A: 3, B: 3, C: 2, D: 2 };
  var BE_R = { A: 1.5, B: 1.5, C: 1, D: 1 };
  var HALF_ORDER = ['BIAS_NONE', 'SCENARIO_C', 'COUNTER_BIAS', 'NEWS_DAY', 'B_RANK2', 'BEFORE_2030'];
  var SCENARIOS = ['A', 'B', 'C', 'D'];

  // Mốc giờ có múi gốc (viết theo giờ VN khi Mỹ / London đang giờ mùa hè)
  var MARKS = {
    prep: { at: '18:00', tz: 'VN' }, comex: { at: '19:20', tz: 'ET' }, news1: { at: '19:30', tz: 'ET' },
    nyse: { at: '20:30', tz: 'ET' }, core: { at: '21:00', tz: 'ET' }, ldnClose: { at: '22:30', tz: 'LONDON' },
    thin: { at: '23:00', tz: 'VN' }, settle: { at: '00:30', tz: 'ET' }, globexMaint: { at: '04:00', tz: 'ET' }
  };

  // Khung giờ cấm mặc định (QĐ-6)
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
    if (news && news.status === 'ok' && news.newsDay) return true;
    return !!t.newsDay;
  }
  // Khung giờ áp dụng: khung nhập tay / mặc định + khung tự sinh từ lịch (news.windows, khi lịch còn mới).
  // 19:30 mặc định: bật khi w.on, hoặc (chưa bị tắt tay) khi chưa qua tầng 0 / ngày có tin lớn. Khi lịch có dữ liệu thì 19:30 mặc định
  // không còn tự bật (chỉ có khung riêng của tin có thật). Khung tự sinh tắt được: t0.newsOverrides[id] = { on: false, offAt }.
  function effectiveWindows(t0, key, news) {
    var t = t0 || {};
    var list = t.windows;
    if (!list) { var th = key ? dep('time').isThursday(key) : false; list = defaultWindows(th); }
    var ok = !!(news && news.status === 'ok');
    var nd = effectiveNewsDay(t, news);
    var out = list.filter(function (w) { return !(ok && w.id === 'w1930'); }).map(function (w) {
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
  // hạng 1–2 mà mép gần nhất cách mép một vùng `edge` ≤ 1 giá (QĐ-1)
  function coincidesEdge(c, z) {
    for (var i = 0; i < c.zones.length; i++) {
      var e = c.zones[i];
      if (e.id !== z.id && hasFlag(e, 'edge') && zoneGap(z, e) <= T.nearGap + EPS) return true;
    }
    return false;
  }

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

  // Chế độ đang áp dụng
  function effectiveRegime(regime) {
    var r = regime || {};
    var mode = r.mode || 'balanced';
    var bo = r.breakout || {};
    if (mode === 'thin') return { effective: 'thin', dir: r.thinDir || null };
    if (mode === 'broken') {
      if (bo.step1 && bo.step2) return { effective: 'broken', dir: bo.dir || null };
      if (bo.step1) return { effective: 'pending', dir: bo.dir || null };
    }
    return { effective: 'balanced', dir: null };
  }
  function dirToSide(dir) { return dir === 'up' ? 'buy' : dir === 'down' ? 'sell' : null; }
  function isCounter(bias, side) { return (bias === 'BUY' && side === 'sell') || (bias === 'SELL' && side === 'buy'); }
  function against(bias, dir) { return (bias === 'BUY' && dir === 'down') || (bias === 'SELL' && dir === 'up'); }

  function isScenIn(rule, s) { return rule.scope === 'ALL' || rule.scope.indexOf(s) >= 0; }
  function has(v) { return v !== null && v !== undefined && v !== ''; }

  // ===== DANH SÁCH LUẬT CÓ THỨ TỰ =====
  // effect: OFF (TẮT MÁY) · LOCK (có lệnh mở) · NO (KHÔNG VÀO) · WAIT (CHỜ) · DISABLE (tắt kịch bản) · HALF (cỡ ½)
  // when(c, s): c = ngữ cảnh do engine dựng; s = kịch bản đang xét (chỉ với DISABLE)
  var RULES = [
    { code: 'OFF_RULE_BREAKS', scope: 'ALL', effect: 'OFF', when: function (c) { return c.counts.ruleBreaks >= T.breakLimit; } },
    { code: 'OFF_SL_STREAK', scope: 'ALL', effect: 'OFF', when: function (c) { return c.counts.slStreak >= T.slStreakLimit; } },
    { code: 'LOCK_OPEN_TRADE', scope: 'ALL', effect: 'LOCK', when: function (c) { return !!c.open; } },
    { code: 'NO_NEWS_WINDOW', scope: 'ALL', effect: 'NO', when: function (c) { return !!c.newsHit; } },

    { code: 'DIS_LONGEST_BAR', scope: 'ABCD', effect: 'DISABLE', when: function (c) { return c.longestBarActive; } },
    { code: 'DIS_NO_CARD', scope: 'ABCD', effect: 'DISABLE', when: function (c) { return !c.card.lockedAt; } },
    { code: 'DIS_BIAS_WAIT', scope: 'ABCD', effect: 'DISABLE', when: function (c) { return !c.bias || c.bias === 'CHỜ'; } },
    { code: 'DIS_BIAS_NONE', scope: 'ABD', effect: 'DISABLE', when: function (c) { return c.bias === 'KHÔNG'; } },
    { code: 'DIS_NO_EDGE', scope: 'BC', effect: 'DISABLE', when: function (c) { return !c.hasEdge; } },
    { code: 'DIS_NOT_BROKEN', scope: 'A', effect: 'DISABLE', when: function (c) { return c.regime.effective === 'balanced'; } },
    { code: 'DIS_PENDING_ACCEPT', scope: 'A', effect: 'DISABLE', when: function (c) { return c.regime.effective === 'pending'; } },
    { code: 'DIS_NO_MOVE', scope: 'D', effect: 'DISABLE', when: function (c) { return c.regime.effective === 'balanced' || c.regime.effective === 'pending'; } },
    { code: 'DIS_M5_OUTSIDE', scope: 'C', effect: 'DISABLE', when: function (c) { return c.regime.effective === 'broken'; } },
    { code: 'DIS_USE_D', scope: 'B', effect: 'DISABLE', when: function (c) { return c.regime.effective === 'thin'; } },
    { code: 'DIS_THIN_NO_FADE', scope: 'C', effect: 'DISABLE', when: function (c) { return c.regime.effective === 'thin'; } },
    { code: 'DIS_BREAK_AGAINST_BIAS', scope: 'AD', effect: 'DISABLE', when: function (c) {
      // bias ghi đè thì để NO_COUNTER_BIAS_SCENARIO xử lý (xem docs/IMPL-1.md)
      var e = c.regime.effective;
      return !c.biasOverridden && (e === 'broken' || e === 'thin') && against(c.bias, c.regime.dir);
    } },
    { code: 'DIS_EARLY_BREAK', scope: 'A', effect: 'DISABLE', when: function (c) { return c.regime.effective === 'broken' && c.earlyBreak; } },

    { code: 'BIAS_NONE', scope: 'ALL', effect: 'HALF', when: function (c) { return c.bias === 'KHÔNG'; } },
    { code: 'SCENARIO_C', scope: 'ALL', effect: 'HALF', when: function (c) { return c.scen === 'C'; } },
    { code: 'COUNTER_BIAS', scope: 'ALL', effect: 'HALF', when: function (c) { return c.scen === 'B' && c.counter && c.exempt9; } },
    { code: 'NEWS_DAY', scope: 'ALL', effect: 'HALF', when: function (c) { return !!c.t0.newsDay; } },
    { code: 'B_RANK2', scope: 'ALL', effect: 'HALF', when: function (c) { return c.scen === 'B' && c.zone && hasFlag(c.zone, 'r2') && !hasFlag(c.zone, 'r1'); } },
    { code: 'BEFORE_2030', scope: 'ALL', effect: 'HALF', when: function (c) { return c.nowMin < c.nyseMin; } },

    { code: 'WAIT_SCENARIO', scope: 'ALL', effect: 'WAIT', when: function (c) { return !c.scen; } },
    { code: 'NO_COUNTER_BIAS_SCENARIO', scope: 'ACD', effect: 'NO', when: function (c) { return c.counter; } },
    { code: 'NO_COUNTER_BIAS_ZONE', scope: 'B', effect: 'NO', when: function (c) { return c.counter && !c.exempt9; } },
    { code: 'NO_BIAS_NONE_EDGE', scope: 'C', effect: 'NO', when: function (c) { return c.bias === 'KHÔNG' && !!c.zone && c.zone.type !== 'vahEu' && c.zone.type !== 'valEu'; } },
    { code: 'WAIT_COUNTER_REASON', scope: 'B', effect: 'WAIT', when: function (c) { return c.counter && c.exempt9 && !(c.setup.counterBiasReason && String(c.setup.counterBiasReason).trim()); } },
    { code: 'WAIT_ZONE', scope: 'ABCD', effect: 'WAIT', when: function (c) { return !c.zone; } },
    // A, D lấy hướng từ chế độ (tầng 2): thiếu hướng thì nói rõ phải về tầng 2, không bắt chọn ở tầng 3 (REVIEW-2 mục 13)
    { code: 'WAIT_REGIME_DIR', scope: 'AD', effect: 'WAIT', when: function (c) { return !c.side; } },
    { code: 'WAIT_SIDE', scope: 'BC', effect: 'WAIT', when: function (c) { return !c.side; } },
    { code: 'NO_ZONE_3RD', scope: 'ABCD', effect: 'NO', when: function (c) { return !!c.zone && c.counts.zoneN >= T.zoneMax; } },
    { code: 'NO_BANNED_ZONE', scope: 'B', effect: 'NO', when: function (c) { return !!c.zone && (hasFlag(c.zone, 'noB') || hasFlag(c.zone, 'banned')); } },
    // B: giữa range chỉ xét khi cân bằng (R8)
    { code: 'NO_MID_RANGE', scope: 'B', effect: 'NO', when: function (c) {
      var z = c.zone, e = c.regime.effective;
      if (!z || c.counter || e !== 'balanced') return false;
      if (hasFlag(z, 'edge')) return false;
      return (hasFlag(z, 'r1') || hasFlag(z, 'r2')) && !coincidesEdge(c, z);
    } },
    // C: chỉ ở đúng cạnh VA Âu / range (HT 5·C); xét ở MỌI chế độ còn bật C, kể cả đang chờ công nhận (REVIEW-2 mục 2)
    { code: 'NO_C_NOT_EDGE', scope: 'C', effect: 'NO', when: function (c) {
      var z = c.zone;
      return !!z && !hasFlag(z, 'edge') && !hasFlag(z, 'edgeOuter');
    } },
    { code: 'NO_PENDING_ACCEPT', scope: 'BC', effect: 'NO', when: function (c) {
      return !!c.zone && c.regime.effective === 'pending' && c.zone.id === c.breakout.edgeZoneId;
    } },
    { code: 'NO_B_RANK', scope: 'B', effect: 'NO', when: function (c) {
      var z = c.zone, e = c.regime.effective;
      if (!z || c.counter) return false;
      if (hasFlag(z, 'r1') || hasFlag(z, 'r2')) return false;
      if ((e === 'balanced' || e === 'pending') && (hasFlag(z, 'edge') || coincidesEdge(c, z))) return false;
      return true;
    } },
    { code: 'NO_FIGHT_BREAK', scope: 'B', effect: 'NO', when: function (c) {
      var z = c.zone;
      if (!z || c.regime.effective !== 'broken' || !c.side) return false;
      if (!against(c.side === 'buy' ? 'BUY' : 'SELL', c.regime.dir)) return false; // chỉ khi B ngược chiều phá
      var ok = (c.bias === 'BUY' && c.side === 'buy' || c.bias === 'SELL' && c.side === 'sell') && hasFlag(z, 'r1') && z.id !== c.breakout.edgeZoneId;
      return !ok;
    } },

    // C4 — bong bóng to gần nhất
    { code: 'NO_BUBBLE_AGAINST', scope: 'ABCD', effect: 'NO', when: function (c) { return !!c.side && (c.s.c4 === 'oppHold' || (c.scen === 'B' && c.s.c4 === 'oppBroken')); } },
    { code: 'NO_UNCLEAR', id: 'c4', scope: 'ABCD', effect: 'NO', when: function (c) { return c.s.c4 === 'unclear'; } },
    { code: 'WAIT_C4', scope: 'ABCD', effect: 'WAIT', when: function (c) { return !has(c.s.c4); } },
    { code: 'WAIT_C4_SAME', scope: 'B', effect: 'WAIT', when: function (c) { return c.s.c4 === 'none'; } },
    // C5 — cạnh hay lưng
    { code: 'WAIT_C5', scope: 'ABCD', effect: 'WAIT', when: function (c) { return !has(c.s.c5); } },
    { code: 'WAIT_C5_BACK', scope: 'ABCD', effect: 'WAIT', when: function (c) { return c.s.c5 === 'mid'; } },
    { code: 'NO_BACK', scope: 'ABCD', effect: 'NO', when: function (c) { return c.s.c5 === 'far'; } },
    // C6 — biên độ nến M1 cao nhất trong 5 nến
    { code: 'WAIT_C6', scope: 'ABCD', effect: 'WAIT', when: function (c) { return !(num(c.s.c6) > 0); } },
    { code: 'WAIT_C6_BIG', scope: 'ABCD', effect: 'WAIT', when: function (c) { return num(c.s.c6) > T.c6Max; } },
    // C7 — ô riêng
    { code: 'WAIT_C7_DMA', scope: 'B', effect: 'WAIT', when: function (c) { return !has((c.s.c7 || {}).dma); } },
    { code: 'NO_DMA_SLOPE', scope: 'B', effect: 'NO', when: function (c) { return (c.s.c7 || {}).dma === 'sloped'; } },
    { code: 'WAIT_C7_MOVE', scope: 'D', effect: 'WAIT', when: function (c) { return num((c.s.c7 || {}).moveSize) === null; } },
    { code: 'NO_D_NO_MOVE', scope: 'D', effect: 'NO', when: function (c) { var m = num((c.s.c7 || {}).moveSize); return m !== null && m < T.moveMin - EPS; } },
    { code: 'WAIT_C7_DEEP', scope: 'D', effect: 'WAIT', when: function (c) { return !has((c.s.c7 || {}).deep); } },
    { code: 'NO_D_DEEP', scope: 'D', effect: 'NO', when: function (c) { return (c.s.c7 || {}).deep === 'yes'; } },
    // B1 — nhịp hồi U / V
    { code: 'WAIT_B1', scope: 'ABD', effect: 'WAIT', when: function (c) { return !has(c.s.b1); } },
    { code: 'NO_V_PULLBACK', scope: 'ABD', effect: 'NO', when: function (c) { return c.s.b1 === 'V'; } },
    { code: 'NO_UNCLEAR', id: 'b1', scope: 'ABD', effect: 'NO', when: function (c) { return c.s.b1 === 'unclear'; } },
    // B2 — thân nến + |delta| (chỉ B)
    { code: 'WAIT_B2', scope: 'B', effect: 'WAIT', when: function (c) { return !has(c.s.b2); } },
    { code: 'WAIT_B2_MIXED', scope: 'B', effect: 'WAIT', when: function (c) { return c.s.b2 === 'mixed'; } },
    { code: 'NO_MOMENTUM', scope: 'B', effect: 'NO', when: function (c) { return c.s.b2 === 'up'; } },
    { code: 'NO_UNCLEAR', id: 'b2', scope: 'B', effect: 'NO', when: function (c) { return c.s.b2 === 'unclear'; } },
    // B3 — nến xác nhận
    { code: 'WAIT_B3', scope: 'ABCD', effect: 'WAIT', when: function (c) { return !has(c.s.b3); } },
    { code: 'WAIT_B3_NOT', scope: 'ABCD', effect: 'WAIT', when: function (c) { return c.s.b3 === 'not'; } },
    { code: 'NO_UNCLEAR', id: 'b3', scope: 'ABCD', effect: 'NO', when: function (c) { return c.s.b3 === 'unclear'; } },
    // B4 — giá vào / SL / TP
    { code: 'WAIT_CALC', scope: 'ABCD', effect: 'WAIT', when: function (c) { return !c.calc.numsOk; } },
    // B5 — SL đúng chỗ?
    { code: 'WAIT_B5', scope: 'ABCD', effect: 'WAIT', when: function (c) { return c.s.slPos !== 'right' && c.s.slPos !== 'wrong'; } },
    { code: 'NO_SL_POS', scope: 'ABCD', effect: 'NO', when: function (c) { return c.s.slPos === 'wrong'; } },
    { code: 'NO_SL_SIDE', scope: 'ABCD', effect: 'NO', when: function (c) { return c.calc.numsOk && !c.calc.slSideOk; } },
    { code: 'NO_SL_FLOOR', scope: 'ABCD', effect: 'NO', when: function (c) { return c.calc.numsOk && num(c.s.c6) > 0 && num(c.s.c6) <= T.c6Max && !c.calc.floorOk; } },
    { code: 'NO_SL_CAP', scope: 'ABCD', effect: 'NO', when: function (c) { return c.calc.numsOk && !c.calc.capOk; } },
    // R:R, TP, cỡ lệnh: luôn xét (QĐ-20) để ruleCodes đủ; chỉ cần số liệu hợp lệ
    { code: 'NO_RR', scope: 'ABCD', effect: 'NO', when: function (c) {
      if (!c.calc.numsOk || !c.calc.slSideOk || c.calc.rr === null) return false;
      return c.calc.rr < T.rrMin - EPS || (c.calc.nextZone && !c.calc.nextRRok);
    } },
    { code: 'NO_TP_PAST_ZONE', scope: 'ABCD', effect: 'NO', when: function (c) { return c.calc.numsOk && c.calc.slSideOk && c.calc.rr !== null && !c.calc.tpPastOk; } },
    // thiếu vốn hoặc % rủi ro: không tính được số hợp đồng ⇒ CHỜ, trỏ tới nút "Đổi vốn" (REVIEW-3 mục 6)
    { code: 'WAIT_CAPITAL', scope: 'ABCD', effect: 'WAIT', when: function (c) {
      return c.calc.numsOk && c.calc.slSideOk && !(num(c.settings.capital) > 0 && num(c.settings.riskPct) > 0);
    } },
    // thiếu vốn hoặc % rủi ro: không tính được số hợp đồng ⇒ CHỜ, trỏ tới nút "Đổi vốn" (REVIEW-3 mục 6)
    { code: 'WAIT_CAPITAL', scope: 'ABCD', effect: 'WAIT', when: function (c) {
      return c.calc.numsOk && c.calc.slSideOk && !(num(c.settings.capital) > 0 && num(c.settings.riskPct) > 0);
    } },
    // QĐ-21: chỉ khi CỠ CHUẨN (đủ, chưa giảm ½) dưới 1 hợp đồng; cỡ ½ không chia được thì 1 hợp đồng tối thiểu
    { code: 'NO_SIZE_ZERO', scope: 'ABCD', effect: 'NO', when: function (c) { return c.calc.numsOk && c.calc.slSideOk && c.sizeOf() !== null && c.calc.sizeFull === 0; } }
  ];
  var RULE_ORDER = RULES.map(function (r) { return r.code; }).filter(function (v, i, a) { return a.indexOf(v) === i; });

  return {
    APP_VERSION: APP_VERSION, T: T, EPS: EPS, TARGET_R: TARGET_R, BE_R: BE_R, HALF_ORDER: HALF_ORDER, SCENARIOS: SCENARIOS,
    MARKS: MARKS, NYSE_WARN: NYSE_WARN, defaultWindows: defaultWindows, effectiveWindows: effectiveWindows, effectiveNewsDay: effectiveNewsDay, ZONE_TYPES: ZONE_TYPES, ZONE_ORDER: ZONE_ORDER,
    RULES: RULES, RULE_ORDER: RULE_ORDER, enrichZone: enrichZone, zoneGap: zoneGap, hasFlag: hasFlag, coincidesEdge: coincidesEdge,
    autoBias: autoBias, effectiveBias: effectiveBias, effectiveRegime: effectiveRegime, dirToSide: dirToSide, isCounter: isCounter,
    against: against, isScenIn: isScenIn, num: num, round1: round1, round2: round2
  };
});
