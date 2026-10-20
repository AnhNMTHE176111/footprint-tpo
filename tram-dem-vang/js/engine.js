/* Trạm Đêm Vàng — ENGINE thuần (v2): (night, now, settings, news) → checklist.
 * Không đụng DOM, không đọc đồng hồ máy. Không khóa gì: chỉ chấm ô tự kiểm, đếm ô đã tick, tính SL / R:R / cỡ lệnh.
 * Thứ tự ô trong mỗi khối: hướng, vùng, (lý do ngược bias), bối cảnh, kiểm tra, điểm vào, giá, ô SL, ô tự kiểm. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(function (n) { return require('./' + n + '.js'); });
  else { root.TDV = root.TDV || {}; root.TDV.engine = factory(function (n) { return root.TDV[n]; }); }
})(this, function (dep) {
  'use strict';
  var R = dep('rules'), time = dep('time'), N = dep('news');
  var T = R.T, EPS = R.EPS, num = R.num;

  // Lệnh đóng có tính là SL (cộng chuỗi) không? Một định nghĩa duy nhất:
  //  · R ≤ −0,2 ⇒ SL (kể cả đóng tay) · R trong (−0,2; +0,2) ⇒ hòa, reset chuỗi · R ≥ +0,2 ⇒ thắng, reset chuỗi
  //  · chưa có R (dữ liệu cũ): kind SL ⇒ SL
  var SL_R = -0.2;
  function isSLTrade(t) {
    var ex = t.exit;
    if (!ex) return false;
    if (typeof t.r === 'number') return t.r <= SL_R + 1e-9;
    return ex.kind === 'SL' && !ex.beStop;
  }
  function isPaper(t) { return (t.flags || []).indexOf('paper') >= 0; }

  function countTrades(night) {
    var trades = (night && night.trades) || [];
    var ruleBreaks = 0;
    trades.forEach(function (t) { if (!isPaper(t) && (t.flags || []).indexOf('RULE_BREAK') >= 0) ruleBreaks++; });
    // chuỗi SL: đếm từ cuối, bỏ lệnh luyện mắt và lệnh chưa đóng; chỉ SL cộng chuỗi, TP / hòa reset (QĐ-10)
    var streak = 0;
    for (var i = trades.length - 1; i >= 0; i--) {
      var t = trades[i];
      if (isPaper(t) || !t.exit) continue;
      if (isSLTrade(t)) streak++; else break;
    }
    return { ruleBreaks: ruleBreaks, slStreak: streak };
  }

  // mọi dòng Sổ chưa nhập kết quả, ở mọi đêm (lệnh qua đêm vẫn chặn đêm sau), cũ trước
  function findOpen(nights) {
    var out = [];
    Object.keys(nights || {}).sort().forEach(function (k) {
      ((nights[k] && nights[k].trades) || []).forEach(function (t) { if (!t.exit) out.push({ nightKey: k, trade: t }); });
    });
    return out;
  }

  // vùng kế tiếp theo hướng lệnh; bỏ vùng vào, vùng cùng cụm (cách vùng vào ≤ 1 giá) và LVN (QĐ-20).
  // fadeOnly (khối C, HT 5·C): TP = cạnh đối diện hoặc POC, cái nào gần hơn ⇒ chỉ xét vùng cạnh và cụm POC; không có thì xét mọi vùng.
  function nextZoneFor(zones, side, entry, entryZone, fadeOnly) {
    function find(accept) {
      var best = null;
      zones.forEach(function (z) {
        if (z.lo === null || z.type === 'lvn') return;
        if (accept && !accept(z)) return;
        if (entryZone && (z.id === entryZone.id || R.zoneGap(z, entryZone) <= T.nearGap + EPS)) return;
        if (side === 'sell' && z.hi < entry - EPS) { if (!best || z.hi > best.edge) best = { zone: z, edge: z.hi }; }
        if (side === 'buy' && z.lo > entry + EPS) { if (!best || z.lo < best.edge) best = { zone: z, edge: z.lo }; }
      });
      return best;
    }
    if (fadeOnly) {
      var fz = find(function (z) { return R.hasFlag(z, 'edge') || z.type === 'pocCluster'; });
      if (fz) return fz;
    }
    return find(null);
  }

  // o = {scen, side, zone, zones, entry, sl, tp, c6, counter}  (B ngược bias ⇒ TP gợi ý 2R, HT 2.2)
  function computeCalc(o) {
    var entry = num(o.entry), sl = num(o.sl), tp = num(o.tp), c6 = num(o.c6);
    var out = { entry: entry, sl: sl, tp: tp, numsOk: false, slDist: null, risk: null, slSideOk: true, floorOk: true, capOk: true,
      rr: null, tpSuggested: null, tpUsed: null, nextZone: null, nextRRok: true, tpPastOk: true, size: null,
      targetR: (o.scen === 'B' && o.counter) ? R.TARGET_R_COUNTER_B : (R.TARGET_R[o.scen] || 3) };
    if (entry === null || sl === null || !o.side) return out;
    out.numsOk = true;
    var risk = Math.abs(entry - sl);
    out.risk = risk;
    out.slDist = R.round1(risk);
    out.slSideOk = o.side === 'buy' ? sl < entry - EPS : sl > entry + EPS;
    out.floorOk = !(c6 > 0) || c6 > T.c6Max || out.slDist >= c6 - EPS;
    out.capOk = out.slDist <= T.slCap + EPS;
    if (risk <= EPS) { out.slSideOk = false; return out; }
    var nz = nextZoneFor(o.zones || [], o.side, entry, o.zone, o.scen === 'C');
    var dirMul = o.side === 'buy' ? 1 : -1;
    var sug = entry + dirMul * out.targetR * risk;
    if (nz) {
      var dist = Math.abs(nz.edge - entry);
      out.nextZone = nz.zone;
      out.nextRRok = dist / risk >= T.rrMin - EPS;
      if (dist < out.targetR * risk - EPS) sug = nz.edge;
    }
    out.tpSuggested = R.round1(sug);
    out.tpUsed = tp !== null ? tp : out.tpSuggested;
    var reward = dirMul * (out.tpUsed - entry);
    out.rr = R.round2(reward / risk);
    if (nz) {
      var over = o.side === 'buy' ? out.tpUsed - nz.edge : nz.edge - out.tpUsed;
      out.tpPastOk = R.round2(over) <= T.tpPastTol + EPS;
    }
    return out;
  }

  // khoảng cách từ giá vào tới vùng (0 nếu nằm trong vùng); null khi thiếu số
  function gapToZone(entry, zone) {
    if (entry === null || !zone || zone.lo === null) return null;
    if (entry >= zone.lo - EPS && entry <= zone.hi + EPS) return 0;
    return Math.min(Math.abs(entry - zone.lo), Math.abs(entry - zone.hi));
  }

  // cỡ lệnh MGC (làm tròn xuống); null khi chưa cài vốn / rủi ro
  // QĐ-21: cỡ chuẩn = floor(vốn × % / (SL × 10 $)); cỡ ½ = floor(½ × số $ / (SL × 10 $)),
  // nhưng cỡ chuẩn ≥ 1 mà ½ ra 0 thì lấy 1 hợp đồng (sizeMinOne). Cỡ chuẩn < 1 ⇒ 0 (không đủ vốn).
  function sizeFor(cl, half, settings) {
    if (!cl || !cl.numsOk || !(cl.slDist > 0)) return null;
    var cap = num(settings.capital), rp = num(settings.riskPct);
    if (!(cap > 0 && rp > 0)) return null;
    var per = cl.slDist * T.tickValue;
    var fullUsd = cap * rp / 100;
    var riskUsd = fullUsd * (half ? 0.5 : 1);
    var full = Math.floor(fullUsd / per + 1e-9);
    var n = Math.floor(riskUsd / per + 1e-9);
    cl.fullUsd = R.round2(fullUsd);
    cl.riskUsd = R.round2(riskUsd);
    cl.sizeFull = full;
    cl.maxSl = R.round1(Math.floor(fullUsd / T.tickValue * 10 + 1e-9) / 10);   // SL tối đa cho 1 hợp đồng ở cỡ chuẩn
    cl.sizeMinOne = false;
    cl.realUsd = R.round2(per);   // rủi ro thật của 1 hợp đồng với SL này
    if (half && full >= 1 && n < 1) { n = 1; cl.sizeMinOne = true; }
    return n;
  }

  function evalBlock(id, c) {
    var bs = (c.se.blocks && c.se.blocks[id]) || {};
    var ticks = bs.ticks || {};
    var side = bs.side === 'buy' || bs.side === 'sell' ? bs.side : null;
    var zone = bs.zoneId ? (c.zoneById[bs.zoneId] || null) : null;
    var counter = !!side && R.isCounter(c.bias, side);
    var reasonOk = !!(bs.reason && String(bs.reason).trim());
    var zoneN = zone ? c.trades.filter(function (t) { return t.zoneId === zone.id && !isPaper(t); }).length : 0;
    // biên độ nến M1 cao nhất 5 nến: nhập một lần cho cả đêm (se.c6); số riêng của khối (dữ liệu cũ, test) thắng nếu có
    var c6 = num(bs.c6) !== null ? num(bs.c6) : num(c.se.c6);
    var cl = computeCalc({ scen: id, side: side, zone: zone, zones: c.zones, entry: bs.entry, sl: bs.sl, tp: bs.tp, c6: c6, counter: counter });
    var c6ok = c6 !== null && c6 > 0 && c6 <= T.c6Max;

    // cỡ ½: lý do theo QĐ-19 / QĐ-21 và bảng 2.3
    var halfs = [];
    if (c.bias === 'KHÔNG') halfs.push('BIAS_NONE');
    if (id === 'C') halfs.push('SCENARIO_C');
    if (counter) halfs.push('COUNTER_BIAS');
    if (c.newsDay) halfs.push('NEWS_DAY');
    if (id === 'B' && zone && R.hasFlag(zone, 'r2') && !R.hasFlag(zone, 'r1')) halfs.push('B_RANK2');
    if (c.nowMin < c.nyseMin) halfs.push('BEFORE_2030');
    halfs = R.HALF_ORDER.filter(function (x) { return halfs.indexOf(x) >= 0; });
    cl.size = sizeFor(cl, halfs.length > 0, c.settings);

    // ô tự kiểm: ok true / false / null (chưa đủ số liệu để kiểm)
    var autos = [];
    // bias cho phép kịch bản này (HT 2.2 + mục 7): KHÔNG ⇒ chỉ C; CHỜ ⇒ chưa khối nào; ngược bias ⇒ chỉ B (kèm ô tail + lý do)
    var bz = { id: 'bias', ok: null, reason: null };
    if (c.bias && side) {
      if (c.bias === 'CHỜ') { bz.ok = false; bz.reason = 'biasWait'; }
      else if (c.bias === 'KHÔNG') { bz.ok = id === 'C'; bz.reason = id === 'C' ? null : 'biasNone'; }
      else if (counter) { bz.ok = id === 'B'; bz.reason = id === 'B' ? null : 'biasCounter'; }
      else bz.ok = true;
    } else if (c.bias === 'CHỜ') { bz.ok = false; bz.reason = 'biasWait'; }
    autos.push(bz);
    // giờ cú phá (chỉ khối A): ô "nến M5 đóng ngoài cạnh" đã tick thì giờ lúc tick không được rơi vào 18:00–giờ COMEX mở
    if (id === 'A') {
      var bh = { id: 'breakHours', ok: null, reason: null };
      if (ticks.ctx1) {
        var at = num(bs.ctx1At) !== null ? num(bs.ctx1At) : c.nowMin;
        var fake = at >= c.prepMin - EPS && at < c.comexMin - EPS;
        bh.ok = !fake; bh.reason = fake ? 'breakHours' : null; bh.at = at;
      }
      autos.push(bh);
    }
    // giá vào cách vùng (HT 4.4): ≤ 1 giá đạt; 1–3 giá chỉ đạt khi râu nến xác nhận chạm vùng; > 3 giá là ở lưng
    var gap = gapToZone(num(bs.entry), zone);
    var nr = { id: 'near', ok: null, reason: null, gap: gap, needWick: false };
    if (gap !== null) {
      if (gap <= T.nearOk + EPS) nr.ok = true;
      else if (gap > T.nearBack + EPS) { nr.ok = false; nr.reason = 'nearBack'; }
      else { nr.needWick = true; nr.ok = !!bs.wick; nr.reason = bs.wick ? null : 'nearFar'; }
    }
    autos.push(nr);
    autos.push({ id: 'zone2', ok: zone ? zoneN < T.zoneMax : null, reason: zone && zoneN >= T.zoneMax ? 'zone2' : null });
    var slKnown = cl.numsOk && cl.slDist > 0;
    var floor = { id: 'slFloor', ok: null, reason: null };
    if (slKnown && !cl.slSideOk) { floor.ok = false; floor.reason = 'slSide'; }
    else if (slKnown && c6ok) { floor.ok = cl.floorOk; floor.reason = cl.floorOk ? null : 'slFloor'; }
    autos.push(floor);
    var cap = { id: 'slCap', ok: null, reason: null };
    if (slKnown && cl.slSideOk) { cap.ok = cl.capOk; cap.reason = cl.capOk ? null : 'slCap'; }
    autos.push(cap);
    var rr = { id: 'rr', ok: null, reason: null };
    if (slKnown && cl.slSideOk && cl.rr !== null) {
      if (cl.rr < T.rrMin - EPS) { rr.ok = false; rr.reason = 'rr'; }
      else if (cl.nextZone && !cl.nextRRok) { rr.ok = false; rr.reason = 'rrNext'; }
      else if (!cl.tpPastOk) { rr.ok = false; rr.reason = 'tpPast'; }
      else rr.ok = true;
    }
    autos.push(rr);
    var size = { id: 'size', ok: null, reason: null };
    if (slKnown && cl.slSideOk) {
      if (cl.size === null) size.reason = 'noCapital';
      else { size.ok = cl.sizeFull >= 1; size.reason = size.ok ? null : 'size'; }
    }
    autos.push(size);
    if (counter) autos.push({ id: 'counter', ok: reasonOk, reason: reasonOk ? null : 'counter' });
    var tailOk = !!bs.tail;

    var items = [];
    items.push({ id: 'side', group: 'pick', ok: !!side });
    items.push({ id: 'zone', group: 'pick', ok: !!zone });
    if (counter) items.push({ id: 'counter', group: 'pick', ok: reasonOk });
    if (counter && id === 'B') items.push({ id: 'tail', group: 'pick', ok: tailOk });
    R.tickIds(id).forEach(function (t) { items.push({ id: t.id, group: t.group, ok: !!ticks[t.id] }); });
    items.push({ id: 'nums', group: 'num', ok: num(bs.entry) !== null && num(bs.sl) !== null && c6ok });
    autos.forEach(function (a) { if (a.id !== 'counter') items.push({ id: a.id, group: 'auto', ok: a.ok === true }); });

    var done = items.filter(function (i) { return i.ok; }).length;
    var missing = items.filter(function (i) { return !i.ok; }).map(function (i) { return i.id; });
    return {
      id: id, done: done, total: items.length, complete: missing.length === 0, missing: missing, order: items.map(function (i) { return i.id; }), items: items,
      autoChecks: autos, side: side, zone: zone, counter: counter, tailOk: tailOk, c6: c6, zoneN: zoneN, nth: zoneN + 1, calc: cl, c6ok: c6ok,
      halfs: halfs, half: halfs.length > 0, touch: (c.se.touch && c.se.touch[id]) || 0,
      active: Object.keys(ticks).some(function (k) { return ticks[k]; }) || !!side || !!zone
    };
  }

  function evaluate(night, now, settings, news, extra) {
    extra = extra || {};
    settings = settings || {};
    night = night || {};
    var useDst = settings.dstShift !== false;
    var nowMs = +now;
    var key = extra.key || time.nightKey(nowMs, useDst);
    var t0 = night.t0 || {}, card = night.card || {}, se = night.se || {};
    var nowMin = time.nightMinutes(nowMs, key);

    var b = R.effectiveBias(card);
    var zones = (card.zones || []).map(function (z) { return R.enrichZone(z, card.answers); });
    var zoneById = {}; zones.forEach(function (z) { zoneById[z.id] = z; });
    var trades = night.trades || [];
    var cnt = countTrades(night);
    var opens = findOpen(extra.nights || (night.trades ? { x: night } : {}));
    t0 = Object.assign({}, t0, { newsDay: R.effectiveNewsDay(t0, news) });
    var windows = R.effectiveWindows(t0, key, news);
    var newsHit = time.hitWindow(windows, nowMin, key, useDst);
    var nyseMin = time.markMin(R.MARKS.nyse, key, useDst);
    var comexMin = time.markMin(R.MARKS.comex, key, useDst);
    var breakerOff = cnt.ruleBreaks >= T.breakLimit || cnt.slStreak >= T.slStreakLimit;

    var common = [
      { id: 'card', auto: true, ok: !!card.lockedAt, reason: card.lockedAt ? null : 'card' },
      { id: 'news', auto: true, ok: !newsHit, reason: newsHit ? 'news' : null },
      { id: 'breaker', auto: true, ok: !breakerOff, reason: !breakerOff ? null : (cnt.ruleBreaks >= T.breakLimit ? 'breakerRule' : 'breakerSl') },
      { id: 'open', auto: true, ok: opens.length === 0, reason: opens.length ? 'open' : null },
      // người bật khi VỪA có nến dài nhất phiên; mặc định tắt ⇒ đạt (TEST-UX-v2 mục 5)
      { id: 'longest', auto: false, ok: !(se.common && se.common.justLongest), reason: se.common && se.common.justLongest ? 'longest' : null }
    ];
    var commonOk = common.every(function (x) { return x.ok; });

    var prepMin = time.markMin(R.MARKS.prep, key, useDst);
    var c = { se: se, zones: zones, zoneById: zoneById, trades: trades, bias: b.value, newsDay: t0.newsDay, nowMin: nowMin, nyseMin: nyseMin, prepMin: prepMin, comexMin: comexMin, settings: settings };
    var blocks = {};
    R.SCENARIOS.forEach(function (s) { blocks[s] = evalBlock(s, c); });

    // ENTRY: khối đủ ô (và ô chung đạt); nhiều khối cùng đủ thì lấy khối người dùng chạm cuối
    var entry = null;
    var cands = R.SCENARIOS.filter(function (s) { return blocks[s].complete; });
    if (commonOk && cands.length) {
      cands.sort(function (x, y) { return blocks[y].touch - blocks[x].touch || R.SCENARIOS.indexOf(x) - R.SCENARIOS.indexOf(y); });
      var eb = blocks[cands[0]];
      entry = { scen: eb.id, side: eb.side, zone: eb.zone, calc: eb.calc, half: eb.half, halfs: eb.halfs, counter: eb.counter, paper: t0.alert === false };
    }
    // khối đang làm (cho dòng CHỜ): khối chạm cuối, không có thì khối nhiều ô nhất đã đụng tới
    var focus = null, best = -1;
    R.SCENARIOS.forEach(function (s) {
      var bl = blocks[s];
      if (!bl.active) return;
      var score = bl.touch * 1000 + bl.done;
      if (score > best) { best = score; focus = s; }
    });
    if (se.last && blocks[se.last] && blocks[se.last].active) focus = se.last;

    var warnings = [];
    var nyseRange = time.windowRange(R.NYSE_WARN, key, useDst);
    if (!(news && (news.status === 'ok' || news.status === 'stale')) && nowMin >= nyseRange.from - EPS && nowMin <= nyseRange.to + EPS) warnings.push('WARN_NYSE');
    if (nowMin >= time.markMin(R.MARKS.prep, key, useDst) && nowMin < nyseMin) warnings.push('WARN_BEFORE_2030');
    if (card.lockedAt && zones.length < T.zonesMin) warnings.push('WARN_FEW_ZONES');
    var fxHit = N.hitWarn(news, nowMin);
    if (fxHit) warnings.push('WARN_FX_NEWS');

    return {
      common: common, commonOk: commonOk, blocks: blocks, entry: entry, focus: focus,
      breaker: { off: breakerOff, ruleBreaks: cnt.ruleBreaks, slStreak: cnt.slStreak },
      counts: { ruleBreaks: cnt.ruleBreaks, slStreak: cnt.slStreak },
      bias: b.value, biasAuto: b.auto, biasOverridden: b.overridden, zones: zones,
      open: opens[0] || null, opens: opens, warnings: warnings, paper: t0.alert === false,
      newsHit: newsHit, fxNews: fxHit, newsDay: t0.newsDay, nowMin: nowMin, nyseMin: nyseMin, comexMin: comexMin
    };
  }

  return { evaluate: evaluate, countTrades: countTrades, isSLTrade: isSLTrade, findOpen: findOpen, computeCalc: computeCalc, nextZoneFor: nextZoneFor, sizeFor: sizeFor, gapToZone: gapToZone };
});
