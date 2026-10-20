/* Trạm Đêm Vàng — tầng 3: kèo trên M1 (Canh rồi Bấm) + thanh phán quyết dính đáy. */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules, time = TDV.time;
  var T = ui.T, h = ui.h, seg = ui.seg, chip = ui.chip, btn = ui.btn, numInput = ui.numInput, textInput = ui.textInput, banner = ui.banner;

  var CANH_CTLS = ['c1', 'c3', 'c2', 'c4', 'c5', 'c6', 'c7'];
  function ctlGroup(id) { return /^b/.test(id) ? 'bam' : 'canh'; }
  // ô điều khiển ứng với một mã (NO_UNCLEAR: ô đầu tiên đang "không rõ")
  function ctlOf(code, st) {
    if (code === 'NO_UNCLEAR') {
      st = st || {};
      return st.c4 === 'unclear' ? 'c4' : st.b1 === 'unclear' ? 'b1' : st.b2 === 'unclear' ? 'b2' : 'b3';
    }
    return C.codes[code] && C.codes[code].ctl;
  }
  // Canh đã điền đủ ⇒ tự chuyển sang Bấm (không tính là thao tác)
  function canhFilled(res, st) {
    var s = res.scenario;
    if (!s || !res.zone || !res.side || !st.c4 || !st.c5 || !(R.num(st.c6) > 0)) return false;
    if (s === 'B' && !(st.c7 && st.c7.dma)) return false;
    if (s === 'D' && !(st.c7 && st.c7.moveSize !== null && st.c7.moveSize !== undefined && st.c7.deep)) return false;
    if (res.counter && !(st.counterBiasReason && String(st.counterBiasReason).trim())) return false;
    return true;
  }

  function ctl(id, label, help, body, extra) {
    return h('div', { class: 'ctl' + (extra && extra.cls ? ' ' + extra.cls : ''), 'data-ctl': id },
      h('div', { class: 'ctl-label' }, h('span', { text: label }), help ? ui.helpBtn(help) : null), body);
  }

  // tô sáng ô còn thiếu đầu tiên
  function applyNeed(el, res) {
    el.querySelectorAll('.ctl.need').forEach(function (n) { n.classList.remove('need'); });
    var first = res.missing[0];
    var id = first && C.codes[first] && C.codes[first].ctl;
    if (id) { var t = el.querySelector('[data-ctl="' + id + '"]'); if (t) t.classList.add('need'); }
  }

  function calcBox(app) {
    var res = app.res, cc = res.calc, box = h('div', { class: 'calcbox', 'data-testid': 'calc' });
    if (!res.scenario) { box.appendChild(h('span', { class: 'muted', text: T('calcNone') })); return box; }
    var st = app.night.setup, c6 = R.num(st.c6);
    if (!cc.numsOk) { box.appendChild(h('span', { class: 'muted', text: T('calcNeed') })); return box; }
    var line = h('div', { class: 'calcline' });
    line.appendChild(chip(T('calcSl', { v: J.fmt(cc.slDist) }), cc.slSideOk && cc.floorOk && cc.capOk ? 'good' : 'bad'));
    line.appendChild(chip(T('calcRr', { v: J.fmtTrim(cc.rr) }), cc.rr >= R.T.rrMin - 1e-9 ? 'good' : 'bad'));
    if (cc.tpSuggested !== null) line.appendChild(chip(T('calcTpSug', { v: J.fmt(cc.tpSuggested) }), ''));
    box.appendChild(line);
    var probs = [];
    if (!cc.slSideOk) probs.push(ui.codeText('NO_SL_SIDE'));
    if (!cc.floorOk && c6 > 0) probs.push(ui.codeText('NO_SL_FLOOR', { sl: J.fmt(cc.slDist), c6: J.fmt(c6) }));
    if (!cc.capOk) probs.push(ui.codeText('NO_SL_CAP'));
    if (cc.slSideOk && cc.floorOk && cc.capOk) {
      if (cc.rr < R.T.rrMin - 1e-9 || (cc.nextZone && !cc.nextRRok)) probs.push(ui.codeText('NO_RR'));
      if (!cc.tpPastOk) probs.push(ui.codeText('NO_TP_PAST_ZONE'));
    }
    probs.forEach(function (p) { box.appendChild(h('div', { class: 'prob', text: '⚠ ' + p })); });
    var s = app.settings;
    var half = res.half.on;
    var sizeTxt = cc.size === null ? T('sizeNoCfg') : (cc.size === 0 ? T('sizeZero') : T('sizeN', { n: cc.size }));
    box.appendChild(h('details', { class: 'fold' }, h('summary', { text: T('sizeTitle') + ' · ' + sizeTxt }),
      h('p', { class: 'muted', text: T('sizeCalc', { cap: s.capital, pct: String(s.riskPct).replace('.', ','), usd: cc.riskUsd === undefined ? '—' : String(cc.riskUsd).replace('.', ','), per: J.fmt(cc.slDist * R.T.tickValue, 0) }) + (half ? ' ' + T('sizeHalf', { why: res.half.reasons.map(function (x) { return C.halfText[x]; }).join(', ') }) : '') })));
    return box;
  }

  function tier3(app) {
    var night = app.night, st = night.setup, res = app.res, scen = res.scenario;
    var lv = app.settings.guideLevel;
    var el = h('div', { class: 'tier t3', 'data-tier': '3' });

    if (res.locks.tier3) {
      var code = res.locks.tier3;
      el.appendChild(h('div', { class: 'lockpanel', 'data-testid': 'locked-3' }, h('div', { class: 'lockicon', text: '🔒' }), h('p', { class: 'lead', text: T('lock_' + code) }),
        btn(T('lockGo_' + code), function () { app.go(code === 'OPEN_TRADE' ? 4 : code === 'NO_CARD' ? 1 : 1); }, 'primary')));
      return el;
    }

    function set(fn, keep) { app.update(function (n) { fn(n.setup, n); n.setup.updatedAt = app.nowMs; }, { keep: !!keep }); }
    var filled = canhFilled(res, st);
    if (filled && !app.ui.canhDone) { app.ui.sub = 'bam'; }
    app.ui.canhDone = filled;
    var sub = app.ui.sub || 'canh';

    // ----- đầu trang: tab Canh / Bấm + kèo mới -----
    var missCanh = 0, missBam = 0;
    res.missing.concat(res.reasons).forEach(function (c) { var id = ctlOf(c, st); if (id) { if (ctlGroup(id) === 'bam') missBam++; else missCanh++; } });
    el.appendChild(h('div', { class: 't3head' },
      seg([{ v: 'canh', label: T('tabCanh') }, { v: 'bam', label: T('tabBam') }], sub, function (v) { app.ui.sub = v || sub; app.render({ keep: false }); }, { noToggle: true, cls: 'tabs', label: T('tabLabel') }),
      h('span', { class: 'muted', text: sub === 'canh' ? T('canhHint') : T('bamHint') }),
      btn(T('newSetup'), function () { app.ui.sub = 'canh'; app.update(function (n) { n.setup = {}; }); app.toast(T('newSetupDone')); }, 'ghost', { 'data-testid': 'new-setup', title: 'N' })));

    if (scen && st.updatedAt && app.nowMs - st.updatedAt > R.T.idleMinutes * 60000) el.appendChild(banner(T('idleNote'), 'warn'));

    // ----- C1 kịch bản (luôn hiện) -----
    var disabledMap = {};
    R.SCENARIOS.forEach(function (s) { if (res.enabled[s] && s !== scen) disabledMap[s] = ui.codeText(res.enabled[s]); });
    var scenOpts = R.SCENARIOS.map(function (s) { return { v: s, label: s + ' · ' + C.scenarios[s].name, sub: disabledMap[s] ? T('offShort') : C.scenarios[s].target }; });
    var c1 = ctl('c1', C.controls.c1.label, C.controls.c1.help, seg(scenOpts, scen || null, function (v) {
      set(function (s0, n) { var next = v ? J.changeScenario(s0, v) : (function () { var c = Object.assign({}, s0); delete c.scenario; return c; })(); n.setup = next; });
    }, { disabled: disabledMap, onDisabled: function (v, why) { app.toast(why); }, cls: 'scen', label: C.controls.c1.label }));
    if (sub === 'canh') el.appendChild(c1);

    if (!scen) {
      if (sub === 'canh') el.appendChild(h('p', { class: 'muted pick', text: T('pickScenario') }));
      else el.appendChild(h('p', { class: 'muted pick', text: T('pickScenario') }));
      applyNeed(el, res);
      el._live = function (a2) { };
      return el;
    }

    var sc = C.scenarios[scen];
    // ----- CANH -----
    if (sub === 'canh') {
      if (lv === 'new') {
        el.appendChild(h('details', { class: 'fold scenfold' }, h('summary', { text: T('scenSummary', { name: sc.name, tp: sc.target, be: sc.be }) }),
          h('p', { text: sc.blurb }), h('img', { src: sc.img, alt: T('scenImgAlt', { name: sc.name }), loading: 'lazy', class: 'scenimg' })));
      }
      // C3 vùng
      var autoA = scen === 'A' && res.regime.effective === 'broken';
      var c3body;
      if (autoA) {
        c3body = h('div', { class: 'autochip' }, res.zone ? chip(ui.zoneLabel(res.zone), 'good') : h('span', { class: 'muted', text: T('c3NoEdge') }), h('span', { class: 'muted', text: T('autoFilled') }));
      } else {
        var zopts = res.zones.map(function (z) { return { v: z.id, label: z.id + ' · ' + ui.zoneLabel(z), sub: z.flags.map(function (f) { return C.flagText[f] || f; }).join(' · ') || null }; });
        c3body = zopts.length ? seg(zopts, st.zoneId || null, function (v) { set(function (s0) { if (v) s0.zoneId = v; else delete s0.zoneId; }); }, { cls: 'wrap', label: C.controls.c3.label }) : h('span', { class: 'muted', text: T('noZones') });
      }
      var c3 = ctl('c3', C.controls.c3.label, C.controls.c3.help, c3body);
      if (res.zone) {
        var nth = res.counts.zoneN + 1;
        c3.appendChild(h('div', { class: 'zinfo' },
          res.zone.flags.map(function (f) { return chip(C.flagText[f] || f, 'mini'); }),
          chip(T('nthAt', { n: nth }), nth > 2 ? 'bad' : nth === 2 ? 'warn' : '')));
      }
      el.appendChild(c3);

      // C2 hướng
      var c2body;
      if (scen === 'B') {
        c2body = seg(C.controls.c2.options, st.side || null, function (v) { set(function (s0) { if (v) s0.side = v; else delete s0.side; }); }, { label: C.controls.c2.label });
      } else {
        c2body = h('div', { class: 'autochip' }, res.side ? chip(ui.sideText(res.side), res.side === 'buy' ? 'good' : 'bad') : h('span', { class: 'muted', text: T('sideNone') }), h('span', { class: 'muted', text: T('autoFilled') }));
      }
      var c2 = ctl('c2', C.controls.c2.label, C.controls.c2.help, c2body);
      if (res.counter) {
        c2.appendChild(h('div', { class: 'counter' }, chip(T('counterBias', { tp: res.exempt9 ? T('counterOk') : T('counterBad') }), res.exempt9 ? 'warn' : 'bad'),
          textInput(st.counterBiasReason || '', function (v) { set(function (s0) { s0.counterBiasReason = v; }); }, { placeholder: T('counterPh'), label: T('counterPh') })));
      }
      el.appendChild(c2);

      // C4
      var c4ctl = C.controls.c4;
      var c4 = ctl('c4', c4ctl.label, c4ctl.help, h('div', { class: 'row wrap' },
        seg(c4ctl.options, st.c4 || null, function (v) { set(function (s0) { if (v) s0.c4 = v; else delete s0.c4; }); }, { label: c4ctl.label }),
        numInput(st.c4num === undefined ? null : st.c4num, function (v) { set(function (s0) { s0.c4num = v; }, true); }, { placeholder: T('c4numPh'), label: T('c4numPh'), id: 'c4num' })));
      el.appendChild(c4);
      // C5
      el.appendChild(ctl('c5', C.controls.c5.label, C.controls.c5.help, seg(C.controls.c5.options, st.c5 || null, function (v) { set(function (s0) { if (v) s0.c5 = v; else delete s0.c5; }); }, { label: C.controls.c5.label })));
      // C6
      el.appendChild(ctl('c6', C.controls.c6.label, C.controls.c6.help, numInput(st.c6 === undefined ? null : st.c6, function (v) { set(function (s0) { s0.c6 = v; }, true); }, { unit: T('unitGia'), placeholder: '0,0', label: C.controls.c6.label, id: 'c6', onCommit: function () { app.render({ keep: false }); } })));
      // C7
      if (scen === 'B') {
        el.appendChild(ctl('c7', C.controls.c7dma.label, C.controls.c7dma.help, seg(C.controls.c7dma.options, (st.c7 || {}).dma || null, function (v) { set(function (s0) { s0.c7 = Object.assign({}, s0.c7); if (v) s0.c7.dma = v; else delete s0.c7.dma; }); }, { label: C.controls.c7dma.label })));
      } else if (scen === 'D') {
        el.appendChild(ctl('c7', C.controls.c7move.label, C.controls.c7move.help, h('div', { class: 'row wrap' },
          numInput((st.c7 || {}).moveSize === undefined ? null : st.c7.moveSize, function (v) { set(function (s0) { s0.c7 = Object.assign({}, s0.c7); s0.c7.moveSize = v; }, true); }, { unit: T('unitGia'), label: C.controls.c7move.label, id: 'c7move', onCommit: function () { app.render({ keep: false }); } }),
          h('span', { class: 'ctl-label inline', text: C.controls.c7deep.label }), ui.helpBtn(C.controls.c7deep.help),
          seg(C.controls.c7deep.options, (st.c7 || {}).deep || null, function (v) { set(function (s0) { s0.c7 = Object.assign({}, s0.c7); if (v) s0.c7.deep = v; else delete s0.c7.deep; }); }, { label: C.controls.c7deep.label }))));
      }
    }

    // ----- BẤM -----
    if (sub === 'bam') {
      if (scen !== 'C') {
        el.appendChild(ctl('b1', C.controls.b1.label, C.controls.b1.help, seg(C.controls.b1.options, st.b1 || null, function (v) { set(function (s0) { if (v) s0.b1 = v; else delete s0.b1; }); }, { label: C.controls.b1.label }), {}));
        if (lv === 'new') el.lastChild.appendChild(h('ul', { class: 'criteria' }, C.controls.b1.criteria.map(function (t) { return h('li', { text: t }); })));
      }
      if (scen === 'B') {
        el.appendChild(ctl('b2', C.controls.b2.label, C.controls.b2.help, seg(C.controls.b2.options, st.b2 || null, function (v) { set(function (s0) { if (v) s0.b2 = v; else delete s0.b2; }); }, { label: C.controls.b2.label })));
      }
      var b3 = ctl('b3', C.controls.b3.label, C.controls.b3.help, seg(C.controls.b3.options, st.b3 || null, function (v) { set(function (s0) { if (v) s0.b3 = v; else delete s0.b3; }); }, { label: C.controls.b3.label }));
      if (lv === 'new') b3.appendChild(h('ul', { class: 'criteria' }, C.controls.b3.criteria[scen].map(function (t) { return h('li', { text: t }); })));
      el.appendChild(b3);

      var cc0 = st.calc || {};
      function setCalc(k, v) { set(function (s0) { s0.calc = Object.assign({}, s0.calc); s0.calc[k] = v; }, true); }
      var b4 = ctl('b4', C.controls.b4.label, C.controls.b4.help, h('div', { class: 'row wrap' },
        h('label', { class: 'mini-l' }, T('entryL'), numInput(cc0.entry === undefined ? null : cc0.entry, function (v) { setCalc('entry', v); }, { label: T('entryL'), placeholder: '0000,0', id: 'entry' })),
        h('label', { class: 'mini-l' }, T('slL'), numInput(cc0.sl === undefined ? null : cc0.sl, function (v) { setCalc('sl', v); }, { label: T('slL'), placeholder: '0000,0', id: 'sl' })),
        h('label', { class: 'mini-l' }, T('tpL'), numInput(cc0.tp === undefined ? null : cc0.tp, function (v) { setCalc('tp', v); }, { label: T('tpL'), placeholder: res.calc.tpSuggested !== null ? J.fmt(res.calc.tpSuggested) : T('tpAuto'), id: 'tp' })),
        h('label', { class: 'mini-l' }, T('c6Again'), numInput(st.c6 === undefined ? null : st.c6, function (v) { set(function (s0) { s0.c6 = v; }, true); }, { label: T('c6Again'), unit: T('unitGia'), id: 'c6b' }))));
      el.appendChild(b4);

      var b5 = ctl('b5', C.controls.b5.label, C.controls.b5.help, seg(C.controls.b5.options, st.slPos || null, function (v) { set(function (s0) { if (v) s0.slPos = v; else delete s0.slPos; }); }, { label: C.controls.b5.label }));
      if (lv === 'new') b5.appendChild(h('p', { class: 'criteria one', text: C.controls.b5.criteria[scen] }));
      el.appendChild(b5);
    }

    var calc = calcBox(app);
    el.appendChild(calc);
    applyNeed(el, res);
    el._live = function (a2) {
      var nb = calcBox(a2);
      calc.replaceWith(nb); calc = nb;
      applyNeed(el, a2.res);
    };
    return el;
  }

  // ===== thanh phán quyết (dính đáy) =====
  function verdictBar(app) {
    var res = app.res, v = res.verdict, cc = res.calc;
    var bar = h('div', { class: 'vbar v-' + v.toLowerCase() + (v === 'ENTRY' && res.paper ? ' paper' : ''), 'data-verdict': v, 'data-testid': 'verdict', role: 'status', 'aria-live': 'polite' });
    var dots = h('div', { class: 'dots', 'aria-label': T('dotsLabel', { n: res.dotsLit }) });
    res.dots.forEach(function (d) { dots.appendChild(h('span', { class: 'dot' + (d ? ' lit' : '') })); });
    var main = h('div', { class: 'vmain' });
    var actions = h('div', { class: 'vact' });
    var half = res.half.on;

    if (v === 'ENTRY') {
      var big = (res.paper ? T('entryView') : 'ENTRY') + ' ' + (res.side ? res.side.toUpperCase() : '');
      var rest = ' ' + J.fmt(cc.entry) + ' · SL ' + J.fmt(cc.sl) + ' (' + T('slGia', { v: J.fmt(cc.slDist) }) + ') · TP ' + J.fmt(cc.tpUsed) + ' · 1:' + J.fmtTrim(cc.rr) + ' · ' + (half ? T('sizeHalfShort') : T('sizeFull')) + (cc.size === null || cc.size === undefined ? '' : ' · ' + T('sizeN', { n: cc.size }));
      if (res.counter) rest += ' · ' + T('counterTag');
      main.appendChild(h('div', { class: 'vtext entry', 'data-testid': 'entry-text' }, h('span', { class: 'ebig', text: big }), h('span', { class: 'erest', text: rest })));
      if (res.paper) actions.appendChild(btn(T('paperBtn'), function () { app.enter({ kind: 'market', paper: true }); }, 'primary big', { 'data-testid': 'btn-paper' }));
      else actions.appendChild(btn(T('enterBtn'), function () { app.openEnter(); }, 'primary big', { 'data-testid': 'btn-entry', title: 'Enter' }));
    } else if (v === 'WAIT') {
      var items = res.missing.slice(0, 3);
      var list = h('span', { class: 'vlist' });
      items.forEach(function (c, i) {
        var ctlId = C.codes[c] && C.codes[c].ctl;
        list.appendChild(h('button', { type: 'button', class: 'vitem', 'data-code': c, onclick: function () { app.focusCtl(ctlId); }, text: C.codes[c] ? C.codes[c].text : c }));
        if (i < items.length - 1) list.appendChild(document.createTextNode(' · '));
      });
      main.appendChild(h('div', { class: 'vtext' }, h('b', { text: T('vWait') }), ' ', T('missingLabel'), ' ', list));
    } else if (v === 'NO' || v === 'OFF') {
      var rl = h('span', { class: 'vlist' });
      res.reasons.slice(0, 2).forEach(function (c, i) {
        var cid = v === 'OFF' ? null : ctlOf(c, app.night.setup);
        var label = ui.codeText(c, { sl: J.fmt(cc.slDist), c6: J.fmt(R.num(app.night.setup.c6)) });
        rl.appendChild(cid ? h('button', { type: 'button', class: 'vitem', 'data-code': c, onclick: function () { app.focusCtl(cid); }, text: label }) : h('span', { 'data-code': c, text: label }));
        if (i < Math.min(2, res.reasons.length) - 1) rl.appendChild(document.createTextNode(' · '));
      });
      main.appendChild(h('div', { class: 'vtext' }, h('b', { text: v === 'OFF' ? T('vOff') : T('vNo') }), ' — ', rl, res.reasons.length > 2 ? h('span', { class: 'moremuted', text: ' ' + T('moreCodes', { n: res.reasons.length - 2 }) }) : null));
    } else {
      main.appendChild(h('div', { class: 'vtext', text: T('vLocked') }));
    }
    if (v === 'NO' || v === 'OFF' || v === 'WAIT') {
      var can = !!res.side && cc.numsOk;
      actions.appendChild(btn(T('forceBtn'), function () { app.forceEnter(); }, 'danger', { 'data-testid': 'btn-force', disabled: can ? null : true, title: can ? null : T('forceNeed') }));
    }
    var notes = h('div', { class: 'vnotes' });
    if (half && v !== 'OFF') notes.appendChild(chip(T('halfNote', { why: res.half.reasons.map(function (x) { return C.halfText[x]; }).join(', ') }), 'warn'));
    if (res.warnings.indexOf('WARN_NYSE') >= 0) notes.appendChild(chip(C.warnText.WARN_NYSE, 'warn'));
    bar.appendChild(dots); bar.appendChild(main); bar.appendChild(actions);
    return h('div', { class: 'vwrap' }, bar, notes.childNodes.length ? notes : null);
  }

  ui.tier3 = { render: tier3 };
  ui.verdict = { render: verdictBar };
})(this);
