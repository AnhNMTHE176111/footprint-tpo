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
    var t = String(s === null || s === undefined ? '' : s).trim().replace(/\s+/g, '').replace(',', '.');
    if (t === '' || t === '-' || t === '.') return null;
    var v = Number(t);
    return isFinite(v) ? v : null;
  }
  function hm(ms) { var p = time.vnParts(+ms); return time.pad(p.hh) + ':' + time.pad(p.mm); }

  // ===== đêm mới =====
  function newNight() {
    return {
      t0: { alert: null, touched: false, windows: R.defaultWindows(), newsDay: false, note: '' },
      card: { answers: {}, bias: {}, zones: [], plan1: '', plan2: '', cancelWhen: '', lockedAt: null, edits: [], drawn: {} },
      regime: { mode: 'balanced', thinDir: null, breakout: { dir: null, edgeZoneId: null, at: null, nth: 1, step1: false, step2: false }, longestBarUntil: null, log: [] },
      setup: {}, open: null, trades: [], tally: { machine: 0, manual: null, closedAt: null }
    };
  }
  // điền các trường còn thiếu (dùng khi migrate / nhập JSON)
  function normalizeNight(n) {
    var d = newNight(), o = n || {};
    var out = {
      t0: Object.assign({}, d.t0, o.t0 || {}),
      card: Object.assign({}, d.card, o.card || {}),
      regime: Object.assign({}, d.regime, o.regime || {}),
      setup: o.setup || {}, open: o.open || null, trades: o.trades || [], tally: Object.assign({}, d.tally, o.tally || {})
    };
    out.t0.windows = (o.t0 && o.t0.windows) || R.defaultWindows();
    out.card.answers = (o.card && o.card.answers) || {};
    out.card.bias = (o.card && o.card.bias) || {};
    out.card.zones = (o.card && o.card.zones) || [];
    out.card.edits = (o.card && o.card.edits) || [];
    out.regime.breakout = Object.assign({}, d.regime.breakout, (o.regime && o.regime.breakout) || {});
    out.regime.log = (o.regime && o.regime.log) || [];
    return out;
  }
  function ensureNight(state, key) {
    if (!state.nights[key]) state.nights[key] = newNight();
    return state.nights[key];
  }

  // ===== thẻ phiên =====
  function newZoneId(card) {
    var max = 0;
    (card.zones || []).forEach(function (z) { var m = /^z(\d+)$/.exec(z.id); if (m) max = Math.max(max, +m[1]); });
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

  // ===== chế độ =====
  function setRegimeMode(night, mode, nowMs) {
    if (night.regime.mode === mode) return;
    night.regime.mode = mode;
    night.regime.log.push({ at: hm(nowMs), mode: mode });
  }
  // "Chui lại trong (phá hụt)": về Cân bằng, lần phá kế = 2
  function breakoutFailed(night, nowMs) {
    var bo = night.regime.breakout;
    bo.step1 = false; bo.step2 = false; bo.nth = 2;
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
    if (o.ruleBreak) codes = (res.reasons && res.reasons.length ? res.reasons : res.missing || []).slice();
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
    if (price === null) {
      if (o.kind === 'TP') price = t.tp;
      else if (o.kind === 'SL') price = t.sl;
      else if (o.kind === 'BE') price = t.entry;
    }
    t.exit = { kind: o.kind, price: price, reason: o.reason || null, at: time.fmtMin(o.nowMin) };
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
    night.tally.manual = R.num(value);
    if (nowMs) night.tally.closedAt = +nowMs;
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
      var label = /^4\.\d$/.test(ref) ? ref : W.section + ' ' + ref;
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

  function toMarkdown(night, key) {
    var lines = ['# ' + W.mdTitle + ' ' + key, '', W.mdHead, '|---|---|---|---|---|---|---|'];
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
    newZoneId: newZoneId, canLockCard: canLockCard, lockCard: lockCard, cardEditPolicy: cardEditPolicy, applyCardEdit: applyCardEdit,
    setRegimeMode: setRegimeMode, breakoutFailed: breakoutFailed, changeScenario: changeScenario,
    createTrade: createTrade, tradeById: tradeById, fillLimit: fillLimit, cancelLimit: cancelLimit,
    computeR: computeR, beStatus: beStatus, markBE: markBE, closeTrade: closeTrade, recomputeTally: recomputeTally,
    manualTally: manualTally, tallyMismatch: tallyMismatch, checksOf: checksOf, warnLine: warnLine, rowOf: rowOf,
    toMarkdown: toMarkdown, toCSV: toCSV, weekStats: weekStats, ruleBreakCount: ruleBreakCount, sweptCount: sweptCount
  };
});
