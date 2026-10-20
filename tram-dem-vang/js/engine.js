/* Trạm Đêm Vàng — ENGINE thuần: (nights, nightKey, now, settings) → phán quyết.
 * Không đụng DOM, không đọc đồng hồ máy. Danh sách luật nằm ở rules.js. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(function (n) { return require('./' + n + '.js'); });
  else { root.TDV = root.TDV || {}; root.TDV.engine = factory(function (n) { return root.TDV[n]; }); }
})(this, function (dep) {
  'use strict';
  var R = dep('rules'), time = dep('time');
  var T = R.T, EPS = R.EPS, num = R.num;

  function countTrades(night) {
    var trades = (night && night.trades) || [];
    var ruleBreaks = 0;
    trades.forEach(function (t) {
      if ((t.flags || []).indexOf('paper') >= 0) return;
      if ((t.flags || []).indexOf('RULE_BREAK') >= 0) ruleBreaks++;
    });
    // chuỗi SL: đếm từ cuối, bỏ lệnh luyện mắt và lệnh chưa đóng; chỉ SL cộng chuỗi, TP / hòa reset (QĐ-10)
    var streak = 0;
    for (var i = trades.length - 1; i >= 0; i--) {
      var t = trades[i];
      if ((t.flags || []).indexOf('paper') >= 0) continue;
      if (!t.exit) continue;
      var isSL = t.exit.kind === 'SL' || (t.exit.kind === 'MANUAL' && typeof t.r === 'number' && t.r < 0);
      if (isSL) streak++; else break;
    }
    return { ruleBreaks: ruleBreaks, slStreak: streak };
  }

  function findOpen(nights) {
    var found = null;
    Object.keys(nights || {}).sort().forEach(function (k) {
      var n = nights[k];
      if (n && n.open) {
        var tr = (n.trades || []).filter(function (t) { return t.id === n.open.tradeId; })[0] || null;
        found = { nightKey: k, open: n.open, trade: tr };
      }
    });
    return found;
  }

  function nextZoneFor(zones, side, entry, entryZoneId) {
    var best = null;
    zones.forEach(function (z) {
      if (z.lo === null || z.id === entryZoneId) return;
      if (side === 'sell' && z.hi < entry - EPS) { if (!best || z.hi > best.edge) best = { zone: z, edge: z.hi }; }
      if (side === 'buy' && z.lo > entry + EPS) { if (!best || z.lo < best.edge) best = { zone: z, edge: z.lo }; }
    });
    return best;
  }

  function computeCalc(c) {
    var s = c.setup, cc = s.calc || {};
    var entry = num(cc.entry), sl = num(cc.sl), tp = num(cc.tp);
    var out = { entry: entry, sl: sl, tp: tp, numsOk: false, slDist: null, risk: null, slSideOk: true, floorOk: true, capOk: true,
      rr: null, tpSuggested: null, tpUsed: null, nextZone: null, nextRRok: true, tpPastOk: true, targetR: null, size: null };
    out.targetR = (c.scen === 'B' && c.counter && c.exempt9) ? 2 : (R.TARGET_R[c.scen] || 3);
    if (entry === null || sl === null || !c.side) return out;
    out.numsOk = true;
    var risk = Math.abs(entry - sl);
    out.risk = risk;
    out.slDist = R.round1(risk);
    out.slSideOk = c.side === 'buy' ? sl < entry - EPS : sl > entry + EPS;
    var c6 = num(c.s.c6);
    out.floorOk = !(c6 > 0) || out.slDist >= c6 - EPS;
    out.capOk = out.slDist <= T.slCap + EPS;
    if (risk <= EPS) { out.slSideOk = false; return out; }
    var nz = nextZoneFor(c.zones, c.side, entry, c.zone && c.zone.id);
    var dirMul = c.side === 'buy' ? 1 : -1;
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
      var over = c.side === 'buy' ? out.tpUsed - nz.edge : nz.edge - out.tpUsed;
      out.tpPastOk = R.round2(over) <= T.tpPastTol + EPS;
    }
    return out;
  }

  function evaluate(input) {
    var settings = input.settings || {};
    var useDst = settings.dstShift !== false;
    var nights = input.nights || {};
    var key = input.nightKey;
    var nowMs = +input.now;
    var night = nights[key] || {};
    var t0 = night.t0 || {}, card = night.card || {}, setup = night.setup || {}, regimeSt = night.regime || {};
    var nowMin = time.nightMinutes(nowMs, key);

    var b = R.effectiveBias(card);
    var reg = R.effectiveRegime(regimeSt);
    var breakout = regimeSt.breakout || {};
    var zones = (card.zones || []).map(function (z) { return R.enrichZone(z, card.answers); });
    var zoneById = {}; zones.forEach(function (z) { zoneById[z.id] = z; });
    var scen = R.SCENARIOS.indexOf(setup.scenario) >= 0 ? setup.scenario : null;
    var zoneId = setup.zoneId;
    if (scen === 'A' && reg.effective === 'broken' && breakout.edgeZoneId) zoneId = breakout.edgeZoneId;
    var zone = zoneId ? (zoneById[zoneId] || null) : null;

    var side = null;
    if (scen === 'A' || scen === 'D') side = R.dirToSide(reg.dir);
    else if (scen === 'C') side = zone ? (zone.sideKind === 'upper' ? 'sell' : zone.sideKind === 'lower' ? 'buy' : null) : null;
    else if (scen === 'B') side = setup.side === 'buy' || setup.side === 'sell' ? setup.side : null;

    var counter = !!side && R.isCounter(b.value, side);
    var exempt9 = false;
    if (scen === 'B' && counter && zone) {
      var need = side === 'sell' ? 'upper' : 'lower';
      exempt9 = (R.hasFlag(zone, 'tail') || R.hasFlag(zone, 'sp')) && zone.sideKind === need;
    }

    var trades = night.trades || [];
    var cnt = countTrades(night);
    var zoneN = zoneId ? trades.filter(function (t) { return t.zoneId === zoneId && (t.flags || []).indexOf('paper') < 0; }).length : 0;
    var openInfo = findOpen(nights);

    var windows = t0.windows || R.defaultWindows();
    var newsHit = time.hitWindow(windows, nowMin, key, useDst);
    var untilMs = num(regimeSt.longestBarUntil);
    var nyseMin = time.markMin(R.MARKS.nyse, key, useDst);
    var comexMin = time.markMin(R.MARKS.comex, key, useDst);
    var breakMin = breakout.at ? time.baseMinute(breakout.at) : null;

    var c = {
      key: key, nowMs: nowMs, nowMin: nowMin, useDst: useDst, settings: settings,
      night: night, t0: t0, card: card, setup: setup, s: setup, trades: trades,
      bias: b.value, biasAuto: b.auto, biasOverridden: b.overridden,
      regime: reg, breakout: breakout, zones: zones, zone: zone, hasEdge: zones.some(function (z) { return R.hasFlag(z, 'edge'); }),
      scen: scen, side: side, counter: counter, exempt9: exempt9,
      counts: { ruleBreaks: cnt.ruleBreaks, slStreak: cnt.slStreak, zoneN: zoneN },
      open: openInfo, newsHit: newsHit,
      longestBarActive: untilMs !== null && nowMs < untilMs,
      nyseMin: nyseMin, comexMin: comexMin, breakMin: breakMin,
      earlyBreak: breakMin !== null && breakMin >= 18 * 60 && breakMin < comexMin,
      reasons: [], missing: [], halfs: [], offs: [], blocked: false
    };
    c.calc = computeCalc(c);

    var enabled = { A: null, B: null, C: null, D: null };
    var locked = false;
    function push(list, code) { if (list.indexOf(code) < 0) list.push(code); }

    R.RULES.forEach(function (rule) {
      var e = rule.effect;
      if (e === 'DISABLE') {
        R.SCENARIOS.forEach(function (s) {
          if (rule.scope.indexOf(s) < 0 || enabled[s]) return;
          if (rule.when(c, s)) {
            enabled[s] = rule.code;
            if (scen === s && !c.blocked) { push(c.reasons, rule.code); c.blocked = true; }
          }
        });
      } else if (e === 'OFF') {
        if (rule.when(c)) push(c.offs, rule.code);
      } else if (e === 'LOCK') {
        if (rule.when(c)) locked = true;
      } else if (e === 'HALF') {
        if (rule.when(c)) push(c.halfs, rule.code);
      } else if (e === 'NO' || e === 'WAIT') {
        if (c.blocked) return;
        if (rule.scope !== 'ALL' && (!scen || rule.scope.indexOf(scen) < 0)) return;
        if (rule.when(c)) push(e === 'NO' ? c.reasons : c.missing, rule.code);
      }
    });

    // cỡ lệnh MGC
    var half = c.halfs.length > 0;
    if (c.calc.numsOk && c.calc.slDist > 0) {
      var cap = num(settings.capital), rp = num(settings.riskPct);
      if (cap > 0 && rp > 0) {
        var riskUsd = cap * rp / 100 * (half ? 0.5 : 1);
        c.calc.riskUsd = R.round2(riskUsd);
        c.calc.size = Math.floor(riskUsd / (c.calc.slDist * T.tickValue) + 1e-9);
      }
    }

    // tám chấm (HT 9)
    var cl = c.calc, s = setup;
    var zoneGroup = ['NO_BANNED_ZONE', 'NO_MID_RANGE', 'NO_PENDING_ACCEPT', 'NO_B_RANK', 'NO_FIGHT_BREAK'];
    var c4ok = scen === 'B' ? s.c4 === 'same' : (s.c4 === 'same' || s.c4 === 'none' || s.c4 === 'oppBroken');
    var dots = [false, false, false, false, false, false, false, false];
    if (scen) {
      var counterOk = !counter || (scen === 'B' && exempt9 && !!(s.counterBiasReason && String(s.counterBiasReason).trim()));
      dots[0] = !!card.lockedAt && !!side && (b.value === 'BUY' || b.value === 'SELL' || (b.value === 'KHÔNG' && scen === 'C')) && counterOk;
      dots[1] = !!zone && s.c5 === 'near' && !zoneGroup.some(function (code) { return c.reasons.indexOf(code) >= 0; });
      dots[2] = enabled[scen] === null;
      dots[3] = scen === 'C' ? true : s.b1 === 'U';
      dots[4] = c4ok;
      dots[5] = scen === 'B' ? s.b2 === 'down' : s.b3 === 'ok';
      dots[6] = s.b3 === 'ok' && !c.longestBarActive;
      dots[7] = s.slPos === 'right' && cl.numsOk && cl.slSideOk && cl.floorOk && num(s.c6) > 0 && cl.capOk && cl.rr !== null && cl.rr >= T.rrMin - EPS && cl.nextRRok && cl.tpPastOk && zoneN < T.zoneMax;
    }

    var verdict, reasons;
    if (c.offs.length) { verdict = 'OFF'; reasons = c.offs.slice(); }
    else if (locked) { verdict = 'LOCKED'; reasons = ['LOCK_OPEN_TRADE']; }
    else if (c.reasons.length) { verdict = 'NO'; reasons = c.reasons.slice(); }
    else if (c.missing.length) { verdict = 'WAIT'; reasons = []; }
    else { verdict = 'ENTRY'; reasons = []; }

    var l3 = null;
    if (openInfo) l3 = 'OPEN_TRADE';
    else if (!card.lockedAt) l3 = 'NO_CARD';
    else if (!b.value || b.value === 'CHỜ') l3 = 'BIAS_WAIT';

    var warnings = [];
    var nyseRange = time.windowRange(R.NYSE_WARN, key, useDst);
    if (nowMin >= nyseRange.from - EPS && nowMin <= nyseRange.to + EPS) warnings.push('WARN_NYSE');
    if (nowMin < nyseMin) warnings.push('WARN_BEFORE_2030');
    if (card.lockedAt && zones.length < T.zonesMin) warnings.push('WARN_FEW_ZONES');

    return {
      verdict: verdict, reasons: reasons, missing: c.missing.slice(), dots: dots, dotsLit: dots.filter(Boolean).length,
      order: R.RULE_ORDER, enabled: enabled, half: { on: half, reasons: c.halfs.slice() },
      regime: { effective: reg.effective, dir: reg.dir }, bias: b.value, biasAuto: b.auto, biasOverridden: b.overridden,
      scenario: scen, side: side, zone: zone, zones: zones, counter: counter, exempt9: exempt9, calc: cl,
      counts: c.counts, open: openInfo, locks: { tier3: l3 }, warnings: warnings,
      paper: t0.alert === false, newsHit: newsHit, longestBarActive: c.longestBarActive,
      nowMin: nowMin, nyseMin: nyseMin, comexMin: comexMin
    };
  }

  return { evaluate: evaluate, countTrades: countTrades, findOpen: findOpen, computeCalc: computeCalc, nextZoneFor: nextZoneFor };
});
