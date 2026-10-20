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
    if (s !== 'C' && !st.b1) return false;
    if (s === 'B' && !st.b2) return false;
    if ((s === 'B' || s === 'D') && R.num(st.ext) === null) return false;
    if (s === 'B' && !(st.c7 && st.c7.dma)) return false;
    if (s === 'D' && !(st.c7 && st.c7.moveSize !== null && st.c7.moveSize !== undefined && st.c7.deep)) return false;
    if (res.counter && !(st.counterBiasReason && String(st.counterBiasReason).trim())) return false;
    return true;
  }

  function ctl(id, label, help, body, extra) {
    return h('div', { class: 'ctl' + (extra && extra.cls ? ' ' + extra.cls : ''), 'data-ctl': id },
      h('div', { class: 'ctl-label' }, h('span', { text: label }), help ? ui.helpBtn(help, extra && extra.note) : null), body);
  }

  // tô sáng ô còn thiếu đầu tiên
  function applyNeed(el, res, scroll) {
    el.querySelectorAll('.ctl.need').forEach(function (n) { n.classList.remove('need'); });
    var first = res.missing[0];
    var id = first && C.codes[first] && C.codes[first].ctl;
    if (id) {
      var t = el.querySelector('[data-ctl="' + id + '"]');
      if (t) {
        t.classList.add('need');
        // ô cần làm nằm dưới thanh phán quyết cố định thì cuộn nó lên trên thanh (REVIEW-3 mục 14)
        if (scroll && t.isConnected) {
          var vb = document.getElementById('verdict'), top = vb ? vb.getBoundingClientRect().top : window.innerHeight;
          var r = t.getBoundingClientRect();
          if (r.bottom > top - 4 && r.top < window.innerHeight) { try { t.scrollIntoView({ block: 'nearest' }); } catch (e) { /* bỏ qua */ } }
        }
      }
    }
  }

  function calcBox(app) {
    var res = app.res, cc = res.calc, box = h('div', { class: 'calcbox', 'data-testid': 'calc' });
    // ENTRY: thanh phán quyết đã in SL, R:R, số hợp đồng ⇒ ẩn hộp tính để bước Bấm vừa một màn (REVIEW-2 mục 12)
    if (res.verdict === 'ENTRY') { box.hidden = true; return box; }
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
    var sizeTxt = cc.size === null ? T('sizeNoCfg') : (cc.size === 0 ? T('sizeZero') : cc.sizeMinOne ? T('sizeMinOne', { usd: J.fmtTrim(cc.realUsd) }) : T('sizeN', { n: cc.size }));
    var money = function (v) { return v === undefined ? '—' : String(v).replace('.', ','); };
    box.appendChild(h('details', { class: 'fold' }, h('summary', { text: T('sizeTitle') + ' · ' + sizeTxt }),
      h('p', { class: 'muted', text: T('sizeCalc', { cap: s.capital, pct: String(s.riskPct).replace('.', ','), full: money(cc.fullUsd), per: J.fmt(cc.slDist * R.T.tickValue, 0) }) + (half ? ' ' + (cc.sizeMinOne ? T('sizeHalfMin', { why: ui.halfWhy(res), real: J.fmtTrim(cc.realUsd) }) : T('sizeHalf', { why: ui.halfWhy(res), usd: money(cc.riskUsd) })) : '') })));
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
    // Canh đủ ⇒ tự sang Bấm ĐÚNG MỘT LẦN cho mỗi kèo; sửa Canh sau đó không nhảy nữa (USER-TEST-3 d8)
    var filled = canhFilled(res, st);
    if (!scen || app.ui.jumpScen !== scen) { app.ui.jumpDone = false; app.ui.jumpNote = false; app.ui.canhOpen = true; }
    app.ui.jumpScen = scen || null;
    if (filled && !app.ui.jumpDone) { app.ui.canhOpen = false; app.ui.jumpDone = true; }

    // ----- đầu trang: Kèo mới (giữ C1–C3, C6) · Xóa hết -----
    el.appendChild(h('div', { class: 't3head' },
      h('span', { class: 'muted small', text: T('t3Hint') }),
      (function () { var nb = btn(T('newSetup'), function () { app.newSetup(); }, 'ghost small', { 'data-testid': 'new-setup', title: 'N' }); nb.appendChild(h('kbd', { class: 'keyhint', text: 'N' })); return nb; })(),
      btn(T('clearAll'), function () { app.clearSetup(); }, 'ghost small', { 'data-testid': 'clear-setup' })));

    if (scen && st.updatedAt && app.nowMs - st.updatedAt > R.T.idleMinutes * 60000) el.appendChild(banner(T('idleNote'), 'warn'));

    // ----- C1 kịch bản (luôn hiện) -----
    var disabledMap = {};
    R.SCENARIOS.forEach(function (s) { if (res.enabled[s] && s !== scen) disabledMap[s] = ui.codeText(res.enabled[s]); });
    var scenOpts = R.SCENARIOS.map(function (s) { return { v: s, label: s + ' · ' + C.scenarios[s].name, sub: disabledMap[s] ? T('offShort') : C.scenarios[s].target }; });
    var c1 = ctl('c1', C.controls.c1.label, C.controls.c1.help, seg(scenOpts, scen || null, function (v) {
      set(function (s0, n) { var next = v ? J.changeScenario(s0, v) : (function () { var c = Object.assign({}, s0); delete c.scenario; return c; })(); n.setup = next; });
    }, { disabled: disabledMap, onDisabled: function (v, why) { app.pickOff(v, why); }, cls: 'scen', label: C.controls.c1.label }));
    // bấm thẻ kịch bản đang tắt: không im lặng, hiện ngay lý do tắt (USER-TEST-4)
    var offPick = app.ui.offPick && app.ui.offPick.scen !== scen && res.enabled[app.ui.offPick.scen] ? app.ui.offPick : null;
    el.appendChild(c1);
    if (offPick) el.appendChild(h('div', { class: 'offpick', 'data-testid': 'off-pick' }, h('b', { text: offPick.scen + ' · ' + C.scenarios[offPick.scen].name + ': ' }), h('span', { text: ui.codeText(res.enabled[offPick.scen], ui.codeVars(app)) })));
    if (scen && res.enabled[scen]) { el.appendChild(banner(T('scenLocked', { why: ui.codeText(res.enabled[scen]) }), 'warn')); c1.classList.add('locked-sel'); }

    if (!scen) {
      el.appendChild(h('p', { class: 'muted pick', text: T('pickScenario') }));
      applyNeed(el, res);
      el._live = function (a2) { };
      return el;
    }

    var sc = C.scenarios[scen];
    // ===== CANH (nhìn được trước khi nến xác nhận đóng): C2–C7, B1, B2, cực trị =====
    var canhEls = [];
    function C_(x) { canhEls.push(x); }
    if (lv === 'new') {
      C_(h('details', { class: 'fold scenfold' }, h('summary', { text: T('scenSummary', { name: sc.name, tp: sc.target, be: sc.be }) }),
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
    var c3note = null;
    if (scen === 'B') c3note = C.qd['QĐ-1'] + ' (' + C.unmeasured + ')';
    if (scen === 'B' && res.zone && res.zone.type === 'pocCluster') c3note = C.qd['QĐ-3'] + ' (' + C.unmeasured + ')';
    var c3 = ctl('c3', C.controls.c3.label, C.controls.c3.help, c3body, { note: c3note });
    if (res.zone) {
      var nth = res.counts.zoneN + 1;
      c3.appendChild(h('div', { class: 'zinfo' },
        res.zone.flags.map(function (f) { return chip(C.flagText[f] || f, 'mini'); }),
        chip(T('nthAt', { n: nth }), nth > 2 ? 'bad' : nth === 2 ? 'warn' : '')));
    }
    C_(c3);

    // C2 hướng
    var c2body;
    if (scen === 'B') {
      c2body = seg(C.controls.c2.options, st.side || null, function (v) { set(function (s0) { if (v) s0.side = v; else delete s0.side; }); }, { label: C.controls.c2.label });
    } else {
      if (res.side) c2body = h('div', { class: 'autochip' }, chip(ui.sideText(res.side), ui.dirCls(res.side)), h('span', { class: 'muted', text: T('autoFilled') }));
      else {
        // hướng của A, D lấy từ chế độ (tầng 2); của C lấy từ phía của vùng (tầng 1): luôn chỉ đường tới ô chọn thật (REVIEW-2 mục 2, 13)
        var toTier = scen === 'C' ? 1 : 2;
        var noSideEver = scen === 'C' && res.zone && !(R.ZONE_TYPES[res.zone.type] || {}).needSide;   // vd HVN: không bao giờ có phía
        c2body = h('div', { class: 'autochip' }, h('span', { class: 'muted', text: scen === 'C' ? (res.zone ? (noSideEver ? T('sideNoneZone') : T('sideNeedZone')) : T('sideAfterZone')) : T('sideNeedRegime') }),
          (scen === 'C' && !res.zone) || noSideEver ? null : btn(toTier === 1 ? T('goTier1') : T('goTier2'), function () { app.go(toTier); }, 'small', { 'data-testid': 'go-tier-' + toTier }));
      }
    }
    var c2 = ctl('c2', C.controls.c2.label, C.controls.c2.help, c2body, { note: res.counter ? C.qd['QĐ-9'] + ' (' + C.unmeasured + ')' : null });
    if (res.counter) {
      c2.appendChild(h('div', { class: 'counter' }, chip(T('counterBias', { tp: res.exempt9 ? T('counterOk') : T('counterBad') }), res.exempt9 ? 'warn' : 'bad'),
        res.exempt9 ? textInput(st.counterBiasReason || '', function (v) { set(function (s0) { s0.counterBiasReason = v; }); }, { placeholder: T('counterPh'), label: T('counterPh') }) : null));
    }
    C_(c2);

    // C4
    var c4ctl = C.controls.c4;
    C_(ctl('c4', c4ctl.label, c4ctl.help, h('div', { class: 'row wrap' },
      seg(c4ctl.options, st.c4 || null, function (v) { set(function (s0) { if (v) s0.c4 = v; else delete s0.c4; }); }, { label: c4ctl.label }),
      numInput(st.c4num === undefined ? null : st.c4num, function (v) { set(function (s0) { s0.c4num = v; }, true); }, { placeholder: T('c4numPh'), label: T('c4numPh'), id: 'c4num' }))));
    // C5
    C_(ctl('c5', C.controls.c5.label, C.controls.c5.help, seg(C.controls.c5.options, st.c5 || null, function (v) { set(function (s0) { if (v) s0.c5 = v; else delete s0.c5; }); }, { label: C.controls.c5.label })));
    // C6
    C_(ctl('c6', C.controls.c6.label, C.controls.c6.help, numInput(st.c6 === undefined ? null : st.c6, function (v) { set(function (s0) { s0.c6 = v; }, true); }, { unit: T('unitGia'), placeholder: '0,0', label: C.controls.c6.label, id: 'c6', onCommit: function () { app.render({ keep: false }); } })));
    // C7
    if (scen === 'B') {
      C_(ctl('c7', C.controls.c7dma.label, C.controls.c7dma.help, seg(C.controls.c7dma.options, (st.c7 || {}).dma || null, function (v) { set(function (s0) { s0.c7 = Object.assign({}, s0.c7); if (v) s0.c7.dma = v; else delete s0.c7.dma; }); }, { label: C.controls.c7dma.label })));
    } else if (scen === 'D') {
      C_(ctl('c7', C.controls.c7move.label, C.controls.c7move.help, h('div', { class: 'row wrap' },
        numInput((st.c7 || {}).moveSize === undefined ? null : st.c7.moveSize, function (v) { set(function (s0) { s0.c7 = Object.assign({}, s0.c7); s0.c7.moveSize = v; }, true); }, { unit: T('unitGia'), label: C.controls.c7move.label, id: 'c7move', onCommit: function () { app.render({ keep: false }); } }),
        h('span', { class: 'ctl-label inline', text: C.controls.c7deep.label }), ui.helpBtn(C.controls.c7deep.help),
        seg(C.controls.c7deep.options, (st.c7 || {}).deep || null, function (v) { set(function (s0) { s0.c7 = Object.assign({}, s0.c7); if (v) s0.c7.deep = v; else delete s0.c7.deep; }); }, { label: C.controls.c7deep.label }))));
    }
    // B1 (A, B, D) và B2 (B): nhìn được trên nhịp hồi trước khi nến xác nhận đóng ⇒ hỏi ở Canh (QĐ-25)
    if (scen !== 'C') {
      var b1 = ctl('b1', C.controls.b1.label, C.controls.b1.help, seg(C.controls.b1.options, st.b1 || null, function (v) { set(function (s0) { if (v) s0.b1 = v; else delete s0.b1; }); }, { label: C.controls.b1.label }), {});
      if (lv === 'new' && !st.b1) b1.appendChild(h('ul', { class: 'criteria' }, C.controls.b1.criteria.map(function (t) { return h('li', { text: t }); })));
      C_(b1);
    }
    if (scen === 'B') {
      C_(ctl('b2', C.controls.b2.label, C.controls.b2.help, seg(C.controls.b2.options, st.b2 || null, function (v) { set(function (s0) { if (v) s0.b2 = v; else delete s0.b2; }); }, { label: C.controls.b2.label })));
    }
    // cực trị cụm hấp thụ (B) / đỉnh nhịp hồi (D): nhìn được trước; máy tự kiểm SL ở bước Bấm (B5 tự kiểm)
    if (scen === 'B' || scen === 'D') {
      var c8 = C.controls[scen === 'B' ? 'c8B' : 'c8D'];
      C_(ctl('c8', c8.label, c8.help, numInput(st.ext === undefined ? null : st.ext, function (v) { set(function (s0) { if (v === null) delete s0.ext; else s0.ext = v; }, true); }, { label: c8.label, placeholder: '0000,0', id: 'ext', onCommit: function () { app.render({ keep: false }); } })));
    }

    // Canh: một khối; đủ rồi thì tự gập thành một dòng tóm tắt (đúng một lần cho mỗi kèo), bấm để mở lại
    var canhOpen = app.ui.canhOpen !== false;
    var summary = T('canhSummary', { scen: scen, zone: res.zone ? ui.zoneLabel(res.zone) : '—', side: res.side ? ui.sideText(res.side).toUpperCase() : '—' });
    var canhBox = h('section', { class: 'panel canh' + (canhOpen ? ' open' : ' closed'), 'data-testid': 'canh' },
      h('button', { type: 'button', class: 'canhhead', 'aria-expanded': canhOpen ? 'true' : 'false', 'data-testid': 'canh-toggle',
        onclick: function () { app.ui.canhOpen = !canhOpen; app.render({ keep: false }); } },
        h('b', { text: T('canhTitle') }), h('span', { class: 'muted', text: canhOpen ? T('canhHint') : (filled ? '✓ ' : '') + summary }), h('span', { class: 'caret', text: canhOpen ? '▾' : '▸' })),
      h('div', { class: 'canhbody', hidden: canhOpen ? null : true }, canhEls));
    el.appendChild(canhBox);

    // ===== BẤM (sau khi nến xác nhận đóng): nến xác nhận, giá vào, SL — luôn hiện, tối đa 3 thao tác =====
    var bamEls = [];
    var b3 = ctl('b3', C.controls.b3.label, C.controls.b3.help, seg(C.controls.b3.options, st.b3 || null, function (v) { set(function (s0) { if (v) s0.b3 = v; else delete s0.b3; }); }, { label: C.controls.b3.label }));
    b3.querySelector('.ctl-label').appendChild(h('kbd', { class: 'keyhint', text: 'Đ' }));
    if (lv === 'new' && !st.b3) b3.appendChild(h('ul', { class: 'criteria' }, C.controls.b3.criteria[scen].map(function (t) { return h('li', { text: t }); })));
    bamEls.push(b3);

    var cc0 = st.calc || {};
    function setCalc(k, v) { set(function (s0) { s0.calc = Object.assign({}, s0.calc); s0.calc[k] = v; }, true); }
    // Enter ở ô SL khi phán quyết là ENTRY = bấm "Vào lệnh" (QĐ-25)
    function enterIfEntry() { if (app.res.verdict === 'ENTRY') { if (app.res.paper) app.enter({ kind: 'market', paper: true }); else app.openEnter(); } }
    var b4 = ctl('b4', C.controls.b4.label, C.controls.b4.help, h('div', { class: 'row wrap' },
      h('label', { class: 'mini-l' }, T('entryL'), numInput(cc0.entry === undefined ? null : cc0.entry, function (v) { setCalc('entry', v); }, { label: T('entryL'), placeholder: '0000,0', id: 'entry' })),
      h('label', { class: 'mini-l' }, T('slL'), numInput(cc0.sl === undefined ? null : cc0.sl, function (v) { setCalc('sl', v); }, { label: T('slL'), placeholder: '0000,0', id: 'sl', onEnter: function (v) { setCalc('sl', v); enterIfEntry(); } })),
      h('label', { class: 'mini-l' }, T('tpL'), numInput(cc0.tp === undefined ? null : cc0.tp, function (v) { setCalc('tp', v); }, { label: T('tpL'), placeholder: res.calc.tpSuggested !== null ? J.fmt(res.calc.tpSuggested) : T('tpAuto'), id: 'tp' })),
      h('label', { class: 'mini-l' }, T('c6Again'), numInput(st.c6 === undefined ? null : st.c6, function (v) { set(function (s0) { s0.c6 = v; }, true); }, { label: T('c6Again'), unit: T('unitGia'), id: 'c6b' }))));
    bamEls.push(b4);
    el.appendChild(h('section', { class: 'panel bam', 'data-testid': 'bam' }, h('div', { class: 'canhhead static' }, h('b', { text: T('bamTitle') }), h('span', { class: 'muted', text: T('bamHint') })), bamEls));

    var calc = calcBox(app);
    el.appendChild(calc);
    applyNeed(el, res);
    el._needScroll = function () { applyNeed(el, app.res, true); };
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
      var sizePart = cc.sizeMinOne ? T('sizeMinOne', { usd: J.fmtTrim(cc.realUsd) }) : (half ? T('sizeHalfShort') : T('sizeFull')) + (cc.size === null || cc.size === undefined ? '' : ' · ' + T('sizeN', { n: cc.size }));
      var rest = ' ' + J.fmt(cc.entry) + ' · SL ' + J.fmt(cc.sl) + ' (' + T('slGia', { v: J.fmt(cc.slDist) }) + ') · TP ' + J.fmt(cc.tpUsed) + ' · 1:' + J.fmtTrim(cc.rr) + ' · ' + sizePart;
      if (res.counter) rest += ' · ' + T('counterTag');
      main.appendChild(h('div', { class: 'vtext entry', 'data-testid': 'entry-text' }, h('span', { class: 'ebig', text: big }), h('span', { class: 'erest', text: rest })));
      if (res.paper) actions.appendChild(btn(T('paperBtn'), function () { app.enter({ kind: 'market', paper: true }); }, 'primary big', { 'data-testid': 'btn-paper' }));
      else { var eb = btn(T('enterBtn'), function () { app.openEnter(); }, 'primary big', { 'data-testid': 'btn-entry', title: 'Enter' }); eb.appendChild(h('kbd', { class: 'keyhint', text: 'Enter' })); actions.appendChild(eb); }
    } else if (v === 'WAIT') {
      var items = res.missing.slice(0, 3);
      var list = h('span', { class: 'vlist' });
      items.forEach(function (c, i) {
        var ctlId = C.codes[c] && C.codes[c].ctl;
        list.appendChild(h('button', { type: 'button', class: 'vitem', 'data-code': c, onclick: function () { if (c === 'WAIT_REGIME_DIR') app.go(2); else if (c === 'WAIT_CAPITAL') app.openCapital(false); else app.focusCtl(ctlId); }, text: ui.codeText(c) }));
        if (i < items.length - 1) list.appendChild(document.createTextNode(' · '));
      });
      main.appendChild(h('div', { class: 'vtext' }, h('b', { text: T('vWait') }), ' ', T('missingLabel'), ' ', list));
    } else if (v === 'NO' || v === 'OFF') {
      var rl = h('span', { class: 'vlist' });
      res.reasons.slice(0, 2).forEach(function (c, i) {
        var cid = v === 'OFF' ? null : ctlOf(c, app.night.setup);
        var label = ui.codeText(c, ui.codeVars(app));
        rl.appendChild(cid ? h('button', { type: 'button', class: 'vitem', 'data-code': c, onclick: function () { app.focusCtl(cid); }, text: label }) : h('span', { 'data-code': c, text: label }));
        if (i < Math.min(2, res.reasons.length) - 1) rl.appendChild(document.createTextNode(' · '));
      });
      main.appendChild(h('div', { class: 'vtext' }, h('b', { text: v === 'OFF' ? T('vOff') : T('vNo') }), ' — ', rl, res.reasons.length > 2 ? h('span', { class: 'moremuted', text: ' ' + T('moreCodes', { n: res.reasons.length - 2 }) }) : null));
    } else {
      main.appendChild(h('div', { class: 'vtext', text: T('vLocked') }));
    }
    // KHÔNG VÀO vì 0 hợp đồng: có nút mở thẳng hộp chỉnh vốn (QĐ-21)
    if ((v === 'NO' && res.reasons.indexOf('NO_SIZE_ZERO') >= 0) || (v === 'WAIT' && res.missing.indexOf('WAIT_CAPITAL') >= 0)) actions.appendChild(btn(T('capChange'), function () { app.openCapital(false); }, 'ghost', { 'data-testid': 'btn-capital' }));
    if (v === 'NO' || v === 'OFF' || v === 'WAIT') {
      var can = !!res.side && cc.numsOk;
      actions.appendChild(btn(T('forceBtn'), function () { app.forceEnter(); }, 'danger', { 'data-testid': 'btn-force', disabled: can ? null : true, title: can ? null : T('forceNeed') }));
    }
    var notes = h('div', { class: 'vnotes' });
    if (half && v !== 'OFF') {
      notes.appendChild(chip(T(cc.sizeMinOne ? 'halfNoteMin' : 'halfNote', { why: ui.halfWhy(res) }), 'warn'));
      if (res.half.reasons.indexOf('BEFORE_2030') >= 0) notes.appendChild(ui.qd19Help());
    }
    if (res.warnings.indexOf('WARN_NYSE') >= 0) notes.appendChild(chip(C.warnText.WARN_NYSE, 'warn'));
    bar.appendChild(dots); bar.appendChild(main); bar.appendChild(actions);
    return h('div', { class: 'vwrap' }, bar, notes.childNodes.length ? notes : null);
  }

  ui.tier3 = { render: tier3 };
  ui.verdict = { render: verdictBar };
})(this);
