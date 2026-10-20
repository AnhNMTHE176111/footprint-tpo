/* Trạm Đêm Vàng — SỔ: ghi / đóng lệnh, thẻ phiên, trạng thái 4 khối, thống kê, xuất Markdown / CSV. Thuần dữ liệu. */
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
  // se: trạng thái Setup Entry. blocks[A..D] = {side, zoneId, ticks:{ctx1:true..}, entry, sl, tp, c6, reason};
  // common.longest = ô người tick dùng chung; last / touch[X] = khối chạm cuối (chọn ENTRY, phím tắt N)
  function newSe() { return { blocks: {}, common: {}, last: null, touch: {}, n: 0 }; }
  function newNight(key) {
    return {
      t0: { alert: null, touched: false, windows: R.defaultWindows(key ? time.isThursday(key) : false), newsDay: false, newsDaySet: false, newsOverrides: {}, note: '' },
      card: { answers: {}, bias: {}, zones: [], zoneSeq: 0, plan1: '', plan2: '', cancelWhen: '', lockedAt: null, edits: [], drawn: {} },
      se: newSe(), trades: [], tally: { machine: 0, manual: null, closedAt: null }
    };
  }
  function normalizeTrade(t) {
    var o = Object.assign({ flags: [], ruleCodes: [], missing: [], ticks: {}, exit: null, r: null }, t);
    o.flags = (t && t.flags) || []; o.ruleCodes = (t && t.ruleCodes) || []; o.missing = (t && t.missing) || []; o.ticks = (t && t.ticks) || {};
    if (o.entry === null || o.entry === undefined) o.entry = R.num(o.entryPlanned);   // lệnh limit chờ khớp của bản cũ: lấy giá dự kiến
    return o;
  }
  // điền các trường còn thiếu (dùng khi migrate / nhập JSON). Bản v1 → v2: giữ thẻ phiên, vùng, sổ; bỏ chế độ, kèo cũ, lệnh mở cũ
  // (lệnh mở cũ chính là dòng sổ chưa có kết quả, nên tự thành "lệnh đang mở" của v2)
  function normalizeNight(n, key) {
    var d = newNight(key), o = n || {};
    var out = {
      t0: Object.assign({}, d.t0, o.t0 || {}),
      card: Object.assign({}, d.card, o.card || {}),
      se: Object.assign(newSe(), o.se || {}),
      trades: (o.trades || []).map(normalizeTrade),
      tally: Object.assign({}, d.tally, o.tally || {})
    };
    out.se.blocks = (o.se && o.se.blocks) || {};
    out.se.common = (o.se && o.se.common) || {};
    out.se.touch = (o.se && o.se.touch) || {};
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
    return out;
  }
  function ensureNight(state, key) {
    if (!state.nights[key]) state.nights[key] = newNight(key);
    return state.nights[key];
  }

  // kế hoạch gõ ngược bias: chỉ cảnh báo, không chặn. Khớp theo từ (\bb) để "buy" / "sell" đứng giữa câu tiếng Việt vẫn bắt được
  function planConflict(card, bias) {
    if (bias !== 'BUY' && bias !== 'SELL') return false;
    var txt = ((card.plan1 || '') + ' ' + (card.plan2 || '')).toLowerCase();
    var hasBuy = /\bbuy\b/.test(txt), hasSell = /\bsell\b/.test(txt);
    return bias === 'SELL' ? (hasBuy && !hasSell) : (hasSell && !hasBuy);
  }

  // ===== trạng thái 4 khối =====
  function block(night, scen) {
    var bl = night.se.blocks;
    if (!bl[scen]) bl[scen] = { ticks: {} };
    if (!bl[scen].ticks) bl[scen].ticks = {};
    return bl[scen];
  }
  // đánh dấu khối vừa được chạm: dùng để chọn ENTRY khi nhiều khối cùng đủ và cho phím N
  function touchBlock(night, scen) {
    night.se.n = (night.se.n || 0) + 1;
    night.se.touch[scen] = night.se.n;
    night.se.last = scen;
  }
  // bỏ tick và số của một khối, giữ hướng và vùng
  function clearBlock(night, scen) {
    var bs = block(night, scen);
    bs.ticks = {};
    ['entry', 'sl', 'tp', 'c6', 'reason', 'wick', 'tail', 'ctx1At'].forEach(function (k) { delete bs[k]; });
  }
  // sau "Ghi lệnh" (mục 7 thiết kế v2): giữ hướng, vùng, tick Bối cảnh và Kiểm tra, ô lý do / tail; chỉ xóa nhóm Điểm vào, ô SL và giá
  function clearAfterTrade(night, scen) {
    var bs = block(night, scen);
    Object.keys(bs.ticks).forEach(function (k) { if (/^(ent|sl)\d+$/.test(k)) delete bs.ticks[k]; });
    ['entry', 'sl', 'tp', 'wick'].forEach(function (k) { delete bs[k]; });
  }
  function setupActive(night) {
    var bl = (night.se && night.se.blocks) || {};
    return Object.keys(bl).some(function (k) { var t = bl[k].ticks || {}; return Object.keys(t).some(function (x) { return t[x]; }); });
  }

  // ===== thẻ phiên =====
  function newZoneId(card) {
    // số thứ tự chỉ tăng: xóa vùng rồi thêm lại không dùng lại mã cũ (REVIEW-1 mục 14)
    var max = card.zoneSeq || 0;
    (card.zones || []).forEach(function (z) { var m = /^z(\d+)$/.exec(z.id); if (m) max = Math.max(max, +m[1]); });
    card.zoneSeq = max + 1;
    return 'z' + (max + 1);
  }
  function canLockCard(card) {
    var a = card.answers || {}, missing = [];
    if (!a.q1) missing.push('q1');
    if (!a.q5) missing.push('q5');
    if (!a.vwapW) missing.push('vwapW');
    if (!(card.zones || []).length) missing.push('zones');
    return { ok: missing.length === 0, missing: missing };
  }
  // Chốt thẻ: Q6 (Âu đã dựng range) không còn hỏi; suy từ việc thẻ có vùng cạnh hay không, giữ trong dữ liệu cho tương thích
  function lockCard(night, nowMs) {
    var zs = (night.card.zones || []).map(function (z) { return R.enrichZone(z, night.card.answers); });
    if (!night.card.answers.q6) night.card.answers.q6 = zs.some(function (z) { return R.hasFlag(z, 'edge'); }) ? 'yes' : 'no';
    night.card.lockedAt = hm(nowMs); return night.card.lockedAt;
  }
  var FREE_EDITS = ['q6', 'vahEu', 'valEu', 'ibHigh', 'ibLow'];
  // Trước 19:20 (mùa đông 20:20): sửa Q6 / VA Âu / IB không để vết. Sau đó mỗi lần sửa ghi lại giờ sửa;
  // đang canh kèo (đã tick ô nào đó, chưa có lệnh mở) thì phải xác nhận.
  function cardEditPolicy(night, what, nowMin, key, useDst) {
    if (!night.card.lockedAt) return { log: false, confirm: false };
    var early = nowMin < time.markMin(R.MARKS.comex, key, useDst);
    var hasOpen = (night.trades || []).some(function (t) { return !t.exit; });
    return {
      log: !(early && FREE_EDITS.indexOf(what) >= 0),
      confirm: !early && setupActive(night) && !hasOpen
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
  // chép Q1′ (nếu chưa trả lời) và các vùng CARRY_ZONES chưa có cùng loại; không vượt 5 vùng.
  // VWAP tuần chép sang thì giá của nó cũng điền luôn vào ô "VWAP tuần" của bias (nếu ô đó còn trống) — USER-TEST-3 (b) 1
  // Trả về {n, items}: items là chữ ngắn từng mục đã chép (không nhắc mục không có)
  function copyFromPrevDetail(night, src) {
    var card = night.card, items = [], sc = (src && src.card) || {};
    if (sc.answers && sc.answers.q1w && !card.answers.q1w) { card.answers.q1w = sc.answers.q1w; items.push(C.ui.copyShape); }
    (sc.zones || []).forEach(function (z) {
      if (CARRY_ZONES.indexOf(z.type) < 0 || card.zones.length >= R.T.zonesMax) return;
      if (card.zones.some(function (q) { return q.type === z.type; })) return;
      var c = { id: newZoneId(card), type: z.type, price: z.price, note: '' };
      if (z.priceTo !== undefined && z.priceTo !== null) c.priceTo = z.priceTo;
      card.zones.push(c);
      items.push(C.zoneTypes[z.type].label + ' ' + fmt(z.price));
      if (z.type === 'vwapW' && R.num(z.price) !== null && R.num(card.answers.vwapPrice) === null) {
        card.answers.vwapPrice = z.price;
        var pn = R.num(card.answers.priceNow);
        if (pn !== null && !card.answers.vwapW) { var d = pn - z.price; card.answers.vwapW = Math.abs(d) <= R.T.vwapNear + R.EPS ? 'near' : d > 0 ? 'above' : 'below'; }
      }
    });
    return { n: items.length, items: items };
  }

  // Gõ nhanh nhiều vùng một lần (QĐ-23 ≤ 10 thao tác cho 4 vùng): "vwapw 4205, vah 4199, val 4185, hvn 4195-4197".
  // Mỗi mục = mã loại + giá (+ "-giá" cho vùng có khoảng). Loại cần phía thêm u (trên) hoặc l (dưới) sau mã: spu 4210, rel 4170.
  var QUICK_ALIAS = {
    vwapw: 'vwapW', vwapt: 'vwapW', vwapd: 'vwapD', vwapn: 'vwapD', vah: 'vahEu', vaheu: 'vahEu', val: 'valEu', valeu: 'valEu',
    poc: 'pocCluster', pocc: 'pocCluster', hvn: 'hvnW', hvnw: 'hvnW', hvn3: 'hvn3w', hvn3w: 'hvn3w', hvnd: 'hvnDay', lvn: 'lvn',
    high: 'highY', hy: 'highY', low: 'lowY', ly: 'lowY', npoc: 'nakedPoc', naked: 'nakedPoc', ibh: 'ibHigh', ibl: 'ibLow', ph: 'poorHigh', pl: 'poorLow'
  };
  var QUICK_SIDED = { sp: 'sp', re: 'rangeEdge' };
  // → { zones: [{type, price, priceTo?, side?}], bad: ['mục không hiểu', ...] }
  function parseQuickZones(text) {
    var out = { zones: [], bad: [] };
    String(text || '').split(/[,;\n]+/).forEach(function (part) {
      var t = part.trim().toLowerCase();
      if (!t) return;
      var m = /^([a-z0-9]+)\s*[:=]?\s*(-?\d+(?:[.,]\d+)?)(?:\s*[-–]\s*(\d+(?:[.,]\d+)?))?$/.exec(t);
      if (!m) { out.bad.push(part.trim()); return; }
      var code = m[1], type = QUICK_ALIAS[code], side;
      if (!type) {
        var base = code.slice(0, -1), sd = code.slice(-1);
        if (QUICK_SIDED[base] && (sd === 'u' || sd === 'l')) { type = QUICK_SIDED[base]; side = sd === 'u' ? 'upper' : 'lower'; }
      }
      if (!type) { out.bad.push(part.trim()); return; }
      var z = { type: type, price: parseNum(m[2]) };
      if (m[3]) z.priceTo = parseNum(m[3]);
      if (side) z.side = side;
      if (z.price === null) { out.bad.push(part.trim()); return; }
      out.zones.push(z);
    });
    return out;
  }

  var seq = 0;
  function newId(nowMs) { seq++; return 't' + (+nowMs).toString(36) + seq.toString(36); }

  // Ghi một dòng Sổ từ khối `o.scen` (lấy số từ kết quả engine `res`), rồi xóa Điểm vào + giá của khối đó (giữ hướng, vùng, bối cảnh, kiểm tra).
  // o = {scen, ruleBreak, paper, missing:[mã ô thiếu], nowMs, nowMin}
  function createTrade(night, res, o) {
    var scen = o.scen, bl = res.blocks[scen], bs = block(night, scen), cc = bl.calc;
    var flags = [];
    if (o.paper) flags.push('paper');
    if (o.ruleBreak && !o.paper) flags.push('RULE_BREAK');
    if (bl.counter) flags.push('COUNTER_BIAS');
    if (bl.half) flags.push('HALF');
    var trade = {
      id: o.id || newId(o.nowMs), time: time.fmtMin(o.nowMin), side: bl.side, scenario: scen,
      zoneId: bl.zone ? bl.zone.id : null, zoneType: bl.zone ? bl.zone.type : null,
      ticks: Object.assign({}, bs.ticks), c6: R.num(bl.c6), entry: cc.entry, sl: cc.sl, tp: cc.tpUsed,
      size: cc.size, slDist: cc.slDist, rrPlanned: cc.rr, exit: null, r: null,
      flags: flags, counterBiasReason: bl.counter ? (bs.reason || '') : '', missing: (o.missing || []).slice(), ruleCodes: [], sweptThenTP: null, notes: ''
    };
    night.trades.push(trade);
    clearAfterTrade(night, scen);
    return trade;
  }
  function tradeById(night, id) { return (night.trades || []).filter(function (t) { return t.id === id; })[0] || null; }

  function computeR(trade, price) {
    if (!trade || trade.entry === null || trade.sl === null || price === null || price === undefined) return null;
    var risk = Math.abs(trade.entry - trade.sl);
    if (risk <= 0) return null;
    var dir = trade.side === 'buy' ? 1 : -1;
    var v = R.round2(dir * (price - trade.entry) / risk);
    return v === 0 ? 0 : v;
  }
  // Mốc dời SL về hòa (nhắc trên dòng lệnh đang mở): A/B +1,5R và cần 1 nến M1 đóng ngoài vùng vào; C/D +1R
  function beInfo(trade) {
    var target = R.BE_R[trade.scenario] || 1.5;
    return { target: target, needBar: trade.scenario === 'A' || trade.scenario === 'B',
      priceAt: trade.entry === null || trade.sl === null ? null : R.round1(trade.entry + (trade.side === 'buy' ? 1 : -1) * target * Math.abs(trade.entry - trade.sl)) };
  }

  // Nhập kết quả ngay trên dòng Sổ. o = {kind:'TP'|'SL'|'BE'|'MANUAL', price, r, reason:'absorb'|'flat'|'other', nowMs, nowMin}
  // R mặc định tự tính từ giá thoát; o.r (số) ghi đè khi người dùng sửa tay.
  function closeTrade(night, tradeId, o) {
    var t = tradeById(night, tradeId);
    if (!t) return null;
    var price = R.num(o.price);
    if (price === null) {
      if (o.kind === 'TP') price = t.tp;
      else if (o.kind === 'SL') price = t.sl;
      else if (o.kind === 'BE') price = t.entry;
    }
    t.exit = { kind: o.kind, price: price, reason: o.reason || null, at: time.fmtMin(o.nowMin) };
    t.r = R.num(o.r) !== null ? R.round2(o.r) : computeR(t, price);
    if (o.kind === 'MANUAL' && o.reason === 'other' && t.flags.indexOf('paper') < 0) {
      if (t.flags.indexOf('RULE_BREAK') < 0) t.flags.push('RULE_BREAK');
      if (t.ruleCodes.indexOf('MANUAL_CLOSE') < 0) t.ruleCodes.push('MANUAL_CLOSE');
    }
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
  function manualTally(night, value) {
    night.tally.manual = R.num(value); // gõ thử một số không làm bản này "mới hơn" khi gộp JSON (REVIEW-1 mục 30)
  }
  function tallyMismatch(night) {
    var t = night.tally || {};
    return t.manual !== null && t.manual !== undefined && Math.abs(R.round2(t.manual) - R.round2(t.machine || 0)) > 1e-9;
  }

  // ===== dòng sổ 7 cột: giờ · hướng · tên · vùng · 4 kiểm tra · SL · R =====
  var W = C.journal;
  function zoneName(t) {
    var z = C.zoneTypes[t.zoneType];
    return z ? z.label.replace(/ \(.*\)$/, '') : '—';
  }
  // các ô kiểm tra đã tick lúc ghi lệnh, in chữ ngắn
  function checksOf(t) {
    var b = C.blocks[t.scenario], ticks = t.ticks || {}, out = [];
    if (!b) return '—';
    b.chk.forEach(function (it, i) { if (ticks['chk' + (i + 1)] && it.short) out.push(it.short); });
    return out.length ? out.join(' · ') : '—';
  }
  // "phá luật, thiếu 2 ô: …" từ danh sách ô thiếu lúc "Vẫn vào" và từ lý do đóng tay
  function warnLine(t) {
    var parts = [], miss = t.missing || [];
    if (miss.length) {
      var labels = miss.map(function (id) { return C.itemLabel(t.scenario, id); });
      parts.push('thiếu ' + miss.length + ' ô: ' + labels.slice(0, 3).join('; ') + (labels.length > 3 ? ' (+' + (labels.length - 3) + ')' : ''));
    }
    if ((t.ruleCodes || []).indexOf('MANUAL_CLOSE') >= 0) parts.push(W.manualClose);
    return parts.length ? W.warnPrefix + ': ' + parts.join('; ') : '';
  }
  function rowOf(t) {
    var name = (C.scenarios[t.scenario] ? C.scenarios[t.scenario].name : t.scenario || '').toLowerCase();
    if (t.flags.indexOf('paper') >= 0) name += ' ' + W.paper;
    return { id: t.id, time: t.time, side: t.side, name: name, zone: zoneName(t), checks: checksOf(t),
      sl: fmt(t.slDist), r: t.exit ? fmtR(t.r) : '…', warn: warnLine(t), ruleBreak: t.flags.indexOf('RULE_BREAK') >= 0 };
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
      lines.push('| ' + [r.time, r.side, r.name, r.zone, r.checks, r.sl, r.r + (r.warn ? ' ⚠' : '')].join(' | ') + ' |');
      if (r.warn) warns.push(W.mdWarn + ' ' + r.time + ' ' + r.warn);
    });
    lines.push(''); lines.push(W.mdLegend);   // chú giải một dòng dưới bảng
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
  var CSV_HEAD = ['dem', 'gio', 'huong', 'kich_ban', 'loai_vung', 'kiem_tra', 'c6', 'vao', 'sl', 'tp', 'khoang_sl', 'rr', 'size', 'thoat', 'gia_thoat', 'r', 'co', 'o_thieu', 'quet_roi_tp'];
  function toCSV(state) {
    var rows = [CSV_HEAD.join(',')];
    Object.keys(state.nights).sort().forEach(function (k) {
      (state.nights[k].trades || []).forEach(function (t) {
        rows.push([k, t.time, t.side, t.scenario, t.zoneType, checksOf(t), t.c6, t.entry, t.sl, t.tp, t.slDist, t.rrPlanned, t.size,
          t.exit ? t.exit.kind : '', t.exit ? t.exit.price : '', t.r, (t.flags || []).join('|'), (t.missing || []).join('|'), t.sweptThenTP === true ? 1 : 0].map(csvCell).join(','));
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
    fmt: fmt, fmtTrim: fmtTrim, fmtR: fmtR, parseNum: parseNum, hm: hm,
    newNight: newNight, normalizeNight: normalizeNight, ensureNight: ensureNight,
    block: block, touchBlock: touchBlock, clearBlock: clearBlock, clearAfterTrade: clearAfterTrade, setupActive: setupActive,
    planConflict: planConflict, prevCardSource: prevCardSource, copyFromPrevDetail: copyFromPrevDetail, newZoneId: newZoneId, canLockCard: canLockCard,
    lockCard: lockCard, cardEditPolicy: cardEditPolicy, applyCardEdit: applyCardEdit, parseQuickZones: parseQuickZones,
    createTrade: createTrade, tradeById: tradeById, computeR: computeR, beInfo: beInfo, closeTrade: closeTrade, recomputeTally: recomputeTally,
    manualTally: manualTally, tallyMismatch: tallyMismatch, checksOf: checksOf, warnLine: warnLine, rowOf: rowOf,
    toMarkdown: toMarkdown, toCSV: toCSV, weekStats: weekStats, ruleBreakCount: ruleBreakCount, sweptCount: sweptCount
  };
});
