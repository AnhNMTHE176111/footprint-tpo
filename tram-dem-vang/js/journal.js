/* Trạm Đêm Vàng — SỔ: tạo / đóng lệnh, ngắt mạch, thẻ phiên, thống kê, xuất Markdown / CSV. Thuần dữ liệu. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(function (n) { return require('./' + n + '.js'); });
  else { root.TDV = root.TDV || {}; root.TDV.journal = factory(function (n) { return root.TDV[n]; }); }
})(this, function (dep) {
  'use strict';
  var R = dep('rules'), time = dep('time'), C = dep('content');

  // ===== định dạng số: dấu phẩy =====
  function fmt(n, dp) {
    if (n === null || n === undefined || !isFinite(n)) return '—';
    return Number(n).toFixed(dp === undefined ? 1 : dp).replace('.', ',');
  }
  function fmtTrim(n) { // 3 → "3" · 1,5 → "1,5" · 3,33 → "3,33"
    if (n === null || n === undefined || !isFinite(n)) return '—';
    return String(R.round2(n)).replace('.', ',');
  }
  function fmtR(r) {
    if (r === null || r === undefined || !isFinite(r)) return '—';
    var v = R.round2(r);
    return (v > 0 ? '+' : '') + String(v).replace('.', ',');
  }
  function fmtSigned(n) { return (n > 0 ? '+' : '') + String(n).replace('.', ','); }
  // ô nhập nhận cả dấu chấm lẫn dấu phẩy
  function parseNum(s) {
    if (typeof s === 'number') return isFinite(s) ? s : null;
    var t = String(s === null || s === undefined ? '' : s).trim().replace(/\s+/g, '');
    if (t.indexOf('.') >= 0 && t.indexOf(',') >= 0) t = t.replace(/\./g, '').replace(',', '.');   // "4.193,5" ⇒ 4193.5
    else t = t.replace(',', '.');
    if (t === '' || t === '-' || t === '.') return null;
    var v = Number(t);
    return isFinite(v) ? v : null;
  }
  function hm(ms) { var p = time.vnParts(+ms); return time.pad(p.hh) + ':' + time.pad(p.mm); }

  // ===== đêm mới =====
  function newNight(key) {
    return {
      t0: { alert: null, touched: false, windows: R.defaultWindows(key ? time.isThursday(key) : false), newsDay: false, note: '' },
      card: { answers: {}, bias: {}, zones: [], zoneSeq: 0, plan1: '', plan2: '', cancelWhen: '', lockedAt: null, edits: [], drawn: {} },
      regime: { mode: 'balanced', thinDir: null, breakout: { dir: null, edgeZoneId: null, at: null, nth: 1, step1: false, step2: false }, longestBarUntil: null, log: [] },
      setup: {}, open: null, trades: [], tally: { machine: 0, manual: null, closedAt: null }
    };
  }
  // điền các trường còn thiếu (dùng khi migrate / nhập JSON)
  function normalizeNight(n, key) {
    var d = newNight(key), o = n || {};
    var out = {
      t0: Object.assign({}, d.t0, o.t0 || {}),
      card: Object.assign({}, d.card, o.card || {}),
      regime: Object.assign({}, d.regime, o.regime || {}),
      setup: o.setup || {}, open: o.open || null,
      trades: (o.trades || []).map(function (t) { return Object.assign({ flags: [], ruleCodes: [], tests: {}, exit: null, r: null }, t, { flags: (t && t.flags) || [], ruleCodes: (t && t.ruleCodes) || [], tests: (t && t.tests) || {} }); }),
      tally: Object.assign({}, d.tally, o.tally || {})
    };
    out.t0.windows = (o.t0 && o.t0.windows) || R.defaultWindows(key ? time.isThursday(key) : false);
    out.card.answers = (o.card && o.card.answers) || {};
    out.card.bias = (o.card && o.card.bias) || {};
    out.card.zones = ((o.card && o.card.zones) || []).map(function (z) {
      var o2 = Object.assign({}, z), p = parseNum(z.price), p2 = parseNum(z.priceTo);
      o2.price = p; if (z.priceTo === undefined || z.priceTo === null || z.priceTo === '') delete o2.priceTo; else o2.priceTo = p2;
      return o2;
    });
    var seq0 = out.card.zoneSeq || 0;
    out.card.zones.forEach(function (z) { var m = /^z(\d+)$/.exec(z.id); if (m) seq0 = Math.max(seq0, +m[1]); });
    out.card.zoneSeq = seq0;
    out.card.edits = (o.card && o.card.edits) || [];
    out.regime.breakout = Object.assign({}, d.regime.breakout, (o.regime && o.regime.breakout) || {});
    out.regime.log = (o.regime && o.regime.log) || [];
    return out;
  }
  function ensureNight(state, key) {
    if (!state.nights[key]) state.nights[key] = newNight(key);
    return state.nights[key];
  }

  // ===== thẻ phiên =====
  function newZoneId(card) {
    // số thứ tự chỉ tăng: xóa vùng rồi thêm lại không dùng lại mã cũ (REVIEW-1 mục 14)
    var max = card.zoneSeq || 0;
    (card.zones || []).forEach(function (z) { var m = /^z(\d+)$/.exec(z.id); if (m) max = Math.max(max, +m[1]); });
    card.zoneSeq = max + 1;
    return 'z' + (max + 1);
  }
  function canLockCard(card, biasValue) {
    var a = card.answers || {}, missing = [];
    if (!a.q1) missing.push('q1');
    if (!a.q5) missing.push('q5');
    if (!a.q6) missing.push('q6');
    if (!a.vwapW) missing.push('vwapW');
    if (!(card.zones || []).length) missing.push('zones');
    return { ok: missing.length === 0, missing: missing };
  }
  function lockCard(night, nowMs) { night.card.lockedAt = hm(nowMs); return night.card.lockedAt; }
  var FREE_EDITS = ['q6', 'vahEu', 'valEu', 'ibHigh', 'ibLow'];
  // Trước 19:20 (mùa đông 20:20): sửa Q6 / VA Âu / IB không để vết. Sau đó mỗi lần sửa ghi vết;
  // đang canh kèo thì phải xác nhận.
  function cardEditPolicy(night, what, nowMin, key, useDst) {
    if (!night.card.lockedAt) return { log: false, confirm: false };
    var early = nowMin < time.markMin(R.MARKS.comex, key, useDst);
    return {
      log: !(early && FREE_EDITS.indexOf(what) >= 0),
      confirm: !early && !!(night.setup && night.setup.scenario) && !night.open
    };
  }
  function applyCardEdit(night, what, label, nowMs, nowMin, key, useDst) {
    var p = cardEditPolicy(night, what, nowMin, key, useDst);
    if (p.log) night.card.edits.push({ at: hm(nowMs), what: label || what });
    return p;
  }

  // ===== sao chép từ đêm trước (USER-TEST-2 mục 5) =====
  // VWAP tuần và HVN 3 tuần thường giữ nguyên cả tuần; Q1′ (hình 3 tuần) cũng vậy. Không đổi luật, chỉ bớt gõ lại.
  var CARRY_ZONES = ['vwapW', 'hvn3w'];
  // đêm gần nhất TRƯỚC `key`, cùng tuần (thứ Hai là đầu tuần), đã chốt thẻ và có thứ để chép
  function prevCardSource(state, key) {
    var wk = time.weekKey(key), best = null;
    Object.keys(state.nights || {}).forEach(function (k) {
      if (k >= key || time.weekKey(k) !== wk) return;
      var c = state.nights[k] && state.nights[k].card;
      if (!c || !c.lockedAt) return;
      var has = (c.answers && c.answers.q1w) || (c.zones || []).some(function (z) { return CARRY_ZONES.indexOf(z.type) >= 0; });
      if (has && (!best || k > best)) best = k;
    });
    return best;
  }
  // chép Q1′ (nếu chưa trả lời) và các vùng CARRY_ZONES chưa có cùng loại; không vượt 5 vùng. Trả về số mục đã chép
  function copyFromPrev(night, src) {
    var card = night.card, n = 0, sc = (src && src.card) || {};
    if (sc.answers && sc.answers.q1w && !card.answers.q1w) { card.answers.q1w = sc.answers.q1w; n++; }
    (sc.zones || []).forEach(function (z) {
      if (CARRY_ZONES.indexOf(z.type) < 0 || card.zones.length >= R.T.zonesMax) return;
      if (card.zones.some(function (q) { return q.type === z.type; })) return;
      var c = { id: newZoneId(card), type: z.type, price: z.price, note: '' };
      if (z.priceTo !== undefined && z.priceTo !== null) c.priceTo = z.priceTo;
      card.zones.push(c); n++;
    });
    return n;
  }

  // ===== chế độ =====
  function setRegimeMode(night, mode, nowMs) {
    if (night.regime.mode === mode) return;
    // vào "Vừa phá" là một cú phá MỚI: xóa bước 1, bước 2, hướng, cạnh; giờ phá = lúc bấm (REVIEW-1 mục 1)
    if (mode === 'broken') {
      var old = night.regime.breakout || {};
      night.regime.breakout = { dir: null, edgeZoneId: null, at: hm(nowMs), nth: old.nth || 1, step1: false, step2: false };
    }
    night.regime.mode = mode;
    night.regime.log.push({ at: hm(nowMs), mode: mode });
  }
  // "Chui lại trong (phá hụt)": về Cân bằng, lần phá kế = 2
  function breakoutFailed(night, nowMs) {
    var bo = night.regime.breakout;
    bo.step1 = false; bo.step2 = false; bo.nth = 2; bo.dir = null; bo.edgeZoneId = null; bo.at = null;
    setRegimeMode(night, 'balanced', nowMs);
  }

  // ===== kèo =====
  // Đổi kịch bản: giữ C4–C6, tính lại C2/C3, xóa C7 và bước Bấm
  function changeScenario(setup, scen) {
    var keep = { scenario: scen, c4: setup.c4, c4num: setup.c4num, c5: setup.c5, c6: setup.c6, zoneId: setup.zoneId, updatedAt: setup.updatedAt };
    if (scen === 'B') keep.side = setup.side;
    Object.keys(keep).forEach(function (k) { if (keep[k] === undefined) delete keep[k]; });
    return keep;
  }

  var seq = 0;
  function newId(nowMs) { seq++; return 't' + (+nowMs).toString(36) + seq.toString(36); }

  // Tạo dòng sổ ngay lúc "Vào lệnh" / "Tôi vẫn vào (phá luật)" / "Ghi kèo luyện mắt"
  // res = kết quả engine.evaluate; o = {kind:'market'|'limit', price, ruleBreak, paper, nowMs, nowMin}
  function createTrade(night, res, o) {
    var s = night.setup || {}, cc = res.calc || {};
    var flags = [];
    if (o.paper) flags.push('paper');
    if (o.ruleBreak && !o.paper) flags.push('RULE_BREAK');
    if (res.counter) flags.push('COUNTER_BIAS');
    if (res.half && res.half.on) flags.push('HALF');
    var codes = [];
    if (o.ruleBreak) {
      // đủ mã luật thật: kể cả khi TẮT MÁY (reasons chỉ có OFF_*) thì vẫn ghi ruleReasons (REVIEW-2 mục 4)
      var add = function (c) { if (codes.indexOf(c) < 0) codes.push(c); };
      (res.reasons || []).forEach(add);
      (res.ruleReasons || []).forEach(add);
      if (!(res.ruleReasons || []).length) (res.missing || []).forEach(add);
    }
    var isMarket = o.kind !== 'limit';
    var fill = R.num(o.price);
    var trade = {
      id: o.id || newId(o.nowMs), time: time.fmtMin(o.nowMin), side: res.side, scenario: res.scenario, mode: res.regime.effective,
      zoneId: res.zone ? res.zone.id : null, zoneType: res.zone ? res.zone.type : null,
      tests: { b1: s.b1 || null, c4: s.c4 || null, c4num: R.num(s.c4num), b2: s.b2 || null, b3: s.b3 || null, c5: s.c5 || null },
      c6: R.num(s.c6), entryPlanned: cc.entry, entry: isMarket ? (fill !== null ? fill : cc.entry) : null, sl: cc.sl, tp: cc.tpUsed,
      size: cc.size, slDist: cc.slDist, slPos: s.slPos || null, rrPlanned: cc.rr, exit: null, r: null,
      flags: flags, counterBiasReason: res.counter ? (s.counterBiasReason || '') : '', ruleCodes: codes, sweptThenTP: null, notes: ''
    };
    night.trades.push(trade);
    night.setup = {}; // kèo đã ghi sổ ⇒ tầng 3 về "Kèo mới"; tải lại không hiện ENTRY cũ (USER-TEST mục 3)
    night.open = { tradeId: trade.id, status: isMarket ? 'filled' : 'pending', beAt: null, beDone: false, outsideZoneBar: false, limitPrice: isMarket ? null : fill };
    return trade;
  }
  function tradeById(night, id) { return (night.trades || []).filter(function (t) { return t.id === id; })[0] || null; }
  function fillLimit(night, price) {
    var t = night.open && tradeById(night, night.open.tradeId);
    if (!t) return null;
    var p = R.num(price);
    t.entry = p !== null ? p : (night.open.limitPrice !== null ? night.open.limitPrice : t.entryPlanned);
    night.open.status = 'filled';
    return t;
  }
  // Hủy limit: xóa dòng, không tăng đếm
  function cancelLimit(night) {
    if (!night.open) return;
    night.trades = night.trades.filter(function (t) { return t.id !== night.open.tradeId; });
    night.open = null;
    night.setup = {};
  }

  function computeR(trade, price) {
    if (!trade || trade.entry === null || trade.sl === null || price === null || price === undefined) return null;
    var risk = Math.abs(trade.entry - trade.sl);
    if (risk <= 0) return null;
    var dir = trade.side === 'buy' ? 1 : -1;
    var v = R.round2(dir * (price - trade.entry) / risk);
    return v === 0 ? 0 : v;
  }
  // Mốc dời SL về hòa: A/B +1,5R (cần 1 nến M1 đóng ngoài vùng vào); C/D +1R
  function beStatus(trade, open, currentPrice) {
    var target = R.BE_R[trade.scenario] || 1.5;
    var r = computeR(trade, currentPrice);
    var needBar = trade.scenario === 'A' || trade.scenario === 'B';
    var reached = r !== null && r >= target - 1e-9;
    return { r: r, target: target, reached: reached, needBar: needBar, ready: reached && (!needBar || !!(open && open.outsideZoneBar)),
      priceAt: trade.entry === null ? null : R.round1(trade.entry + (trade.side === 'buy' ? 1 : -1) * target * Math.abs(trade.entry - trade.sl)) };
  }
  function markBE(night) { if (night.open) { night.open.beDone = true; night.open.beAt = null; } }

  // Đóng lệnh. o = {kind:'TP'|'SL'|'BE'|'MANUAL', price, reason:'absorb'|'flat'|'other', nowMs, nowMin}
  function closeTrade(night, o) {
    if (!night.open) return null;
    var t = tradeById(night, night.open.tradeId);
    if (!t) { night.open = null; return null; }
    var price = R.num(o.price);
    var beStop = o.kind === 'SL' && !!night.open.beDone;   // SL đã dời về hòa vốn bị chạm ⇒ hòa, không phải thua (REVIEW-2 mục 3)
    if (price === null) {
      if (o.kind === 'TP') price = t.tp;
      else if (o.kind === 'SL') price = beStop ? t.entry : t.sl;
      else if (o.kind === 'BE') price = t.entry;
    }
    t.exit = { kind: o.kind, price: price, reason: o.reason || null, at: time.fmtMin(o.nowMin) };
    if (beStop) t.exit.beStop = true;
    t.r = computeR(t, price);
    if (o.kind === 'MANUAL' && o.reason === 'other' && t.flags.indexOf('paper') < 0) {
      if (t.flags.indexOf('RULE_BREAK') < 0) t.flags.push('RULE_BREAK');
      if (t.ruleCodes.indexOf('MANUAL_CLOSE') < 0) t.ruleCodes.push('MANUAL_CLOSE');
    }
    night.open = null;
    recomputeTally(night, o.nowMs);
    return t;
  }
  function recomputeTally(night, nowMs) {
    var sum = 0;
    (night.trades || []).forEach(function (t) {
      if (t.flags.indexOf('paper') >= 0 || !t.exit || typeof t.r !== 'number') return;
      sum += t.r;
    });
    night.tally.machine = R.round2(sum);
    if (nowMs) night.tally.closedAt = +nowMs;
    return night.tally.machine;
  }
  function manualTally(night, value, nowMs) {
    night.tally.manual = R.num(value); // gõ thử một số không làm bản này "mới hơn" khi gộp JSON (REVIEW-1 mục 30)
  }
  function tallyMismatch(night) {
    var t = night.tally || {};
    return t.manual !== null && t.manual !== undefined && Math.abs(R.round2(t.manual) - R.round2(t.machine || 0)) > 1e-9;
  }

  // ===== dòng sổ 7 cột =====
  var W = C.journal;
  var C4_TEXT = W.c4, B2_TEXT = W.b2;
  function checksOf(t) {
    var ts = t.tests || {};
    var b1 = t.scenario === 'C' ? '—' : (ts.b1 === 'unclear' ? '?' : (ts.b1 || '—'));
    var bb;
    if (!ts.c4) bb = 'bb —';
    else if (ts.c4 === 'none' || ts.c4 === 'unclear') bb = 'bb ' + C4_TEXT[ts.c4];
    else bb = 'bb ' + (typeof ts.c4num === 'number' ? fmtSigned(ts.c4num) + ' ' : '') + C4_TEXT[ts.c4];
    var delta = '—';
    if (t.scenario === 'B') delta = ts.b2 ? B2_TEXT[ts.b2] : '—';
    else if (t.scenario === 'A' || t.scenario === 'D') delta = ts.b3 === 'ok' ? W.strong : '—';
    var edge = ts.c5 === 'near' ? W.edgeNear : (ts.c5 ? W.edgeBack : '—');
    return [b1, bb, 'Δ ' + delta, edge].join(' · ');
  }
  // "phạm 4.1, 4.3 và luật SL" từ htRef của ruleCodes
  function warnLine(t) {
    var items = [], hasSL = false, seen = {};
    (t.ruleCodes || []).forEach(function (code) {
      var ref = C.codes[code] && C.codes[code].htRef;
      if (!ref) return;
      if (ref === '6') { hasSL = true; return; }
      var label = /^4\.\d$/.test(ref) || /^ST/.test(ref) ? ref : W.section + ' ' + ref;
      if (!seen[label]) { seen[label] = 1; items.push(label); }
    });
    if (!items.length && !hasSL) return '';
    var s = W.warnPrefix + ' ' + items.join(', ');
    if (hasSL) s = items.length ? s + ' ' + W.and + ' ' + W.slLaw : W.warnPrefix + ' ' + W.slLaw;
    return s;
  }
  function rowOf(t) {
    var name = (C.scenarios[t.scenario] ? C.scenarios[t.scenario].name : t.scenario || '').toLowerCase();
    if (t.flags.indexOf('paper') >= 0) name += ' ' + W.paper;
    var warn = warnLine(t);
    return { id: t.id, time: t.time, side: t.side, name: name, mode: (C.modes[t.mode] || t.mode || '').toLowerCase(), checks: checksOf(t),
      sl: fmt(t.slDist), r: t.exit ? fmtR(t.r) : '…', warn: warn, ruleBreak: t.flags.indexOf('RULE_BREAK') >= 0 };
  }

  function sweptCount(night) { return (night.trades || []).filter(function (t) { return t.sweptThenTP === true; }).length; }
  function ruleBreakCount(night) { return (night.trades || []).filter(function (t) { return t.flags.indexOf('RULE_BREAK') >= 0 && t.flags.indexOf('paper') < 0; }).length; }

  // khối thẻ phiên cho Markdown (bias, vùng, kế hoạch) để ôn lại đêm đó
  function cardLines(night) {
    var card = night.card || {}, a = card.answers || {};
    if (!card.lockedAt && !Object.keys(a).length && !(card.zones || []).length) return [];
    function opt(qid, v) { var q = C.questions.filter(function (x) { return x.id === qid; })[0]; var o = q && q.options.filter(function (x) { return x.v === v; })[0]; return o ? o.label : '—'; }
    var vw = C.vwapOpts.filter(function (o) { return o.v === a.vwapW; })[0];
    var bias = R.effectiveBias(card).value;
    var zones = (card.zones || []).map(function (z) {
      var t = C.zoneTypes[z.type];
      return z.id + ' ' + (t ? t.label.replace(/ \(.*\)$/, '') : z.type) + ' ' + fmt(z.price) + (z.priceTo !== undefined && z.priceTo !== null ? '–' + fmt(z.priceTo) : '');
    });
    var L = ['## ' + W.mdCard + (card.lockedAt ? ' (' + card.lockedAt + ')' : ''), '',
      '- ' + W.mdBias + ': ' + (bias || '—') + ' · ' + W.mdVwap + ': ' + (vw ? vw.label : '—') + ' · ' + W.mdClose + ': ' + opt('q5', a.q5) + ' · ' + W.mdShape + ': ' + opt('q1', a.q1),
      '- ' + W.mdMode + ': ' + (C.modes[R.effectiveRegime(night.regime).effective] || '—'),
      '- ' + W.mdZones + ': ' + (zones.length ? zones.join('; ') : '—')];
    if (card.plan1) L.push('- ' + W.mdPlan1 + ': ' + card.plan1);
    if (card.plan2) L.push('- ' + W.mdPlan2 + ': ' + card.plan2);
    if (card.cancelWhen) L.push('- ' + W.mdCancel + ': ' + card.cancelWhen);
    L.push('');
    return L;
  }
  function toMarkdown(night, key) {
    var lines = ['# ' + W.mdTitle + ' ' + key, ''].concat(cardLines(night)).concat([W.mdHead, '|---|---|---|---|---|---|---|']);
    var warns = [];
    (night.trades || []).forEach(function (t) {
      var r = rowOf(t);
      lines.push('| ' + [r.time, r.side, r.name, r.mode, r.checks, r.sl, r.r + (r.warn ? ' ⚠' : '')].join(' | ') + ' |');
      if (r.warn) warns.push(W.mdWarn + ' ' + r.time + ' ' + r.warn);
    });
    if (warns.length) { lines.push(''); warns.forEach(function (w) { lines.push(w); }); }
    var tl = night.tally || {};
    lines.push('');
    lines.push(W.machine + ': ' + fmtR(tl.machine || 0) + ' R · ' + W.you + ': ' + (tl.manual === null || tl.manual === undefined ? '—' : fmtR(tl.manual) + ' R') +
      ' · ' + W.breaks + ': ' + ruleBreakCount(night) + ' · ' + W.swept + ': ' + sweptCount(night));
    return lines.join('\n') + '\n';
  }

  function csvCell(v) {
    var s = v === null || v === undefined ? '' : String(v);
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  var CSV_HEAD = ['dem', 'gio', 'huong', 'kich_ban', 'che_do', 'loai_vung', 'b1', 'c4', 'c4_so', 'b2', 'b3', 'c5', 'c6', 'vao', 'sl', 'tp', 'khoang_sl', 'rr', 'size', 'thoat', 'gia_thoat', 'r', 'co', 'ma_luat', 'quet_roi_tp'];
  function toCSV(state) {
    var rows = [CSV_HEAD.join(',')];
    Object.keys(state.nights).sort().forEach(function (k) {
      (state.nights[k].trades || []).forEach(function (t) {
        var ts = t.tests || {};
        rows.push([k, t.time, t.side, t.scenario, t.mode, t.zoneType, ts.b1, ts.c4, ts.c4num, ts.b2, ts.b3, ts.c5, t.c6, t.entry, t.sl, t.tp, t.slDist, t.rrPlanned, t.size,
          t.exit ? t.exit.kind : '', t.exit ? t.exit.price : '', t.r, (t.flags || []).join('|'), (t.ruleCodes || []).join('|'), t.sweptThenTP === true ? 1 : 0].map(csvCell).join(','));
      });
    });
    return rows.join('\n') + '\n';
  }

  // ===== thống kê tuần (HT 8) =====
  function weekStats(state, key) {
    var wk = time.weekKey(key);
    var out = { week: wk, trades: 0, ruleBreaks: 0, swept: 0, byScenario: {}, byZone: {}, counter: { n: 0, r: 0 }, streak: 0 };
    Object.keys(state.nights).sort().forEach(function (k) {
      if (time.weekKey(k) !== wk) return;
      (state.nights[k].trades || []).forEach(function (t) {
        if (t.flags.indexOf('paper') >= 0) return;
        out.trades++;
        if (t.flags.indexOf('RULE_BREAK') >= 0) out.ruleBreaks++;
        if (t.sweptThenTP === true) out.swept++;
        var r = typeof t.r === 'number' ? t.r : 0;
        var sc = out.byScenario[t.scenario] || (out.byScenario[t.scenario] = { n: 0, r: 0 });
        sc.n++; sc.r = R.round2(sc.r + r);
        var zt = out.byZone[t.zoneType] || (out.byZone[t.zoneType] = { n: 0, r: 0 });
        zt.n++; zt.r = R.round2(zt.r + r);
        if (t.flags.indexOf('COUNTER_BIAS') >= 0) { out.counter.n++; out.counter.r = R.round2(out.counter.r + r); }
      });
    });
    // chuỗi đêm không phá luật (chỉ tính đêm có thẻ hoặc có lệnh), đếm lùi từ đêm hiện tại
    var keys = Object.keys(state.nights).sort().reverse();
    for (var i = 0; i < keys.length; i++) {
      if (keys[i] > key) continue;
      var n = state.nights[keys[i]];
      if (!n.card.lockedAt && !(n.trades || []).length) continue;
      if (ruleBreakCount(n) > 0) break;
      out.streak++;
    }
    return out;
  }

  return {
    fmt: fmt, fmtTrim: fmtTrim, fmtR: fmtR, fmtSigned: fmtSigned, parseNum: parseNum, hm: hm,
    newNight: newNight, normalizeNight: normalizeNight, ensureNight: ensureNight,
    prevCardSource: prevCardSource, copyFromPrev: copyFromPrev, newZoneId: newZoneId, canLockCard: canLockCard, lockCard: lockCard, cardEditPolicy: cardEditPolicy, applyCardEdit: applyCardEdit,
    setRegimeMode: setRegimeMode, breakoutFailed: breakoutFailed, changeScenario: changeScenario,
    createTrade: createTrade, tradeById: tradeById, fillLimit: fillLimit, cancelLimit: cancelLimit,
    computeR: computeR, beStatus: beStatus, markBE: markBE, closeTrade: closeTrade, recomputeTally: recomputeTally,
    manualTally: manualTally, tallyMismatch: tallyMismatch, checksOf: checksOf, warnLine: warnLine, rowOf: rowOf,
    toMarkdown: toMarkdown, toCSV: toCSV, weekStats: weekStats, ruleBreakCount: ruleBreakCount, sweptCount: sweptCount
  };
});
