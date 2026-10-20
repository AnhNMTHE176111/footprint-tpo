/* Trạm Đêm Vàng — tầng 4 (lệnh đang mở) và tầng 5 (sổ, xuất / nhập, cài đặt). */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules, time = TDV.time, S = TDV.store;
  var T = ui.T, h = ui.h, seg = ui.seg, chip = ui.chip, btn = ui.btn, numInput = ui.numInput, textInput = ui.textInput, section = ui.section, banner = ui.banner;

  function lead(text) { return h('p', { class: 'lead', text: text }); }
  function kv(label, value, cls) { return h('div', { class: 'kv' }, h('span', { class: 'k', text: label }), h('span', { class: 'v' + (cls ? ' ' + cls : ''), text: value })); }

  // "SL bị quét rồi giá tới TP?" + ghi chú, cho một dòng sổ
  function tradeExtras(app, trade, key) {
    return h('div', { class: 'extras' },
      h('label', { class: 'tick' }, h('input', { type: 'checkbox', checked: trade.sweptThenTP === true ? true : null,
        onchange: function (e) { app.update(function (n) { var t = J.tradeById(n, trade.id); if (t) t.sweptThenTP = e.target.checked; }, { key: key, keep: true }); } }), h('span', { text: T('swept') })),
      textInput(trade.notes || '', function (v) { app.update(function (n) { var t = J.tradeById(n, trade.id); if (t) t.notes = v; }, { key: key, keep: true }); }, { placeholder: T('tradeNote'), label: T('tradeNote'), max: 200 }));
  }

  // ================= TẦNG 4 =================
  function tier4(app) {
    var res = app.res, o = res.open;
    var el = h('div', { class: 'tier', 'data-tier': '4' });
    if (!o || !o.trade) {
      el.appendChild(h('div', { class: 'lockpanel' }, h('div', { class: 'lockicon', text: '○' }), h('p', { class: 'lead', text: T('t4None') })));
      var last = null, lastKey = null;
      Object.keys(app.state.nights).sort().forEach(function (k) { (app.state.nights[k].trades || []).forEach(function (t) { if (t.exit) { last = t; lastKey = k; } }); });
      if (last) {
        el.appendChild(section(T('t4Last'), [h('p', { text: J.rowOf(last).name + ' · ' + last.side + ' · R ' + J.fmtR(last.r) }), tradeExtras(app, last, lastKey)]));
      }
      el.appendChild(h('div', { class: 'actions' }, btn(T('toTier3'), function () { app.go(3); }, 'primary', { disabled: res.locks.tier3 ? true : null })));
      return el;
    }
    var t = o.trade, op = o.open, key = o.nightKey;
    var paper = t.flags.indexOf('paper') >= 0;
    var nightObj = app.state.nights[key];
    var nowMinO = time.nightMinutes(app.nowMs, key);

    var head = h('div', { class: 'ohead' }, chip(t.side, ui.dirCls(t.side)), h('b', { text: J.rowOf(t).name }), h('span', { class: 'muted', text: (t.zoneType ? C.zoneTypes[t.zoneType].label : '') + ' · ' + (C.modes[t.mode] || '') }),
      paper ? chip(T('openPaper'), 'warn') : null, t.flags.indexOf('RULE_BREAK') >= 0 ? chip(T('ruleBreakFlag'), 'bad') : null, t.flags.indexOf('HALF') >= 0 ? chip(T('sizeHalfShort'), 'warn') : null);
    var grid = h('div', { class: 'kvgrid' },
      kv(T('kvEntry'), t.entry === null ? T('kvPending', { v: J.fmt(op.limitPrice) }) : J.fmt(t.entry)),
      kv(T('kvSl'), op.beDone ? T('beMoveTo', { sl: J.fmt(t.sl), entry: J.fmt(t.entry) }) + ' · ' + T('beDone') : J.fmt(t.sl)),
      kv(T('kvTp'), J.fmt(t.tp)), kv(T('kvRr'), '1:' + J.fmtTrim(t.rrPlanned)),
      kv(T('kvSize'), t.size === null || t.size === undefined ? '—' : String(t.size)), kv(T('kvTime'), t.time));
    el.appendChild(section(T('t4Title'), [head, grid, h('p', { class: 'muted', text: T('noSlEdit') })]));

    if (op.beDone) el.appendChild(banner(T('beReminder', { entry: J.fmt(t.entry) }), 'warn'));
    var dl = time.flatDeadline(R.effectiveWindows(nightObj.t0, key), nowMinO, key, app.useDst);
    if (dl && !paper) el.appendChild(banner(T('flatBefore', { hm: time.fmtMin(dl.at), min: Math.max(0, Math.ceil(dl.at - nowMinO)) }), dl.at - nowMinO <= 15 ? 'bad' : 'warn'));
    if (nowMinO >= time.markMin(R.MARKS.globexMaint, key, app.useDst)) el.appendChild(banner(T('maintNote'), 'warn'));

    if (op.status === 'pending') {
      var fillP = app.ui.fillPrice === undefined ? op.limitPrice : app.ui.fillPrice;
      el.appendChild(section(T('t4Pending'), h('div', { class: 'row wrap' },
        h('label', { class: 'mini-l' }, T('fillPrice'), numInput(fillP, function (v) { app.ui.fillPrice = v; }, { id: 'fillprice', label: T('fillPrice') })),
        btn(T('filled'), function () { var p = app.ui.fillPrice === undefined ? op.limitPrice : app.ui.fillPrice; app.ui.fillPrice = undefined; app.update(function (n) { J.fillLimit(n, p); }, { key: key }); }, 'primary', { 'data-testid': 'btn-filled' }),
        btn(T('cancelLimit'), function () { app.update(function (n) { J.cancelLimit(n); }, { key: key }); app.toast(T('cancelledToast')); app.go(3); }, 'ghost', { 'data-testid': 'btn-cancel-limit' }))));
      return el;
    }

    // đã khớp: giá hiện tại → R hiện tại, mốc be
    var cur = app.ui.curPrice && app.ui.curPrice.id === t.id ? app.ui.curPrice.v : null;
    var live = h('span', { class: 'bigchip', 'data-testid': 'r-now' });
    var beLine = h('div', { class: 'beline' });
    function refreshLive() {
      var r = J.computeR(t, cur);
      live.textContent = r === null ? T('rNowNone') : T('rNow', { r: J.fmtR(r) });
      live.className = 'bigchip ' + (r === null ? '' : r > 0 ? 'good' : r < 0 ? 'bad' : '');
      var be = J.beStatus(t, op, cur);
      beLine.textContent = '';
      if (op.beDone) { beLine.appendChild(chip(T('beDone'), 'good')); return; }
      beLine.appendChild(h('span', { class: 'muted', text: T('beRule', { r: J.fmtTrim(be.target), price: J.fmt(be.priceAt) }) }));
      if (be.needBar) {
        beLine.appendChild(h('label', { class: 'tick' }, h('input', { type: 'checkbox', checked: op.outsideZoneBar ? true : null, onchange: function (e) {
          app.update(function (n) { n.open.outsideZoneBar = e.target.checked; }, { key: key, keep: true }); op.outsideZoneBar = e.target.checked; refreshLive(); } }), h('span', { text: T('outsideBar') })));
      }
      beLine.appendChild(btn(T('moveBe'), function () { app.update(function (n) { J.markBE(n); }, { key: key }); }, 'primary', { disabled: be.ready ? null : true, 'data-testid': 'btn-be' }));
    }
    el.appendChild(section(T('t4Live'), [
      h('div', { class: 'row wrap' }, h('label', { class: 'mini-l' }, T('curPrice'), numInput(cur, function (v) { app.ui.curPrice = { id: t.id, v: v }; cur = v; refreshLive(); }, { id: 'curprice', label: T('curPrice') })), live),
      beLine], { help: { text: T('t4BeHelp'), ref: 'tp-be' } }));
    refreshLive();

    // đóng lệnh
    var ck = app.ui.closeKind || null;
    if (ck === 'BE' && !op.beDone) ck = null;
    var kinds = [{ v: 'TP', label: T('closeTp') }, { v: 'SL', label: T('closeSl'), bad: true }, { v: 'BE', label: T('closeBe') }, { v: 'MANUAL', label: T('closeManual') }];
    var beOff = op.beDone ? null : { BE: T('beNeedDone') };
    var closeBody = [seg(kinds, ck, function (v) { app.ui.closeKind = v; app.ui.closePrice = undefined; app.ui.closeReason = null; app.render({ keep: false }); }, { cls: 'close', label: T('t4Close'), disabled: beOff, onDisabled: function (v, why) { app.toast(why); } })];
    if (ck) {
      var defPrice = ck === 'TP' ? t.tp : ck === 'SL' ? t.sl : ck === 'BE' ? t.entry : (cur !== null ? cur : null);
      var price = app.ui.closePrice === undefined ? defPrice : app.ui.closePrice;
      var rr = J.computeR(t, price);
      var reasonOk = ck !== 'MANUAL' || !!app.ui.closeReason;
      closeBody.push(h('div', { class: 'row wrap' },
        h('label', { class: 'mini-l' }, T('exitPrice'), numInput(price, function (v) { app.ui.closePrice = v; var r2 = J.computeR(t, v); rSug.textContent = r2 === null ? '—' : J.fmtR(r2); }, { id: 'exitprice', label: T('exitPrice') })),
        h('span', { class: 'muted', text: T('rSuggest') }), (function () { rSug = h('b', { class: 'rsug', text: rr === null ? '—' : J.fmtR(rr) }); return rSug; })()));
      if (ck === 'MANUAL') {
        closeBody.push(h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('manualReason') }), ui.helpBtn({ text: T('manualHelp'), ref: 'tp-be' }),
          seg(C.closeReasons.map(function (x) { return { v: x.v, label: x.label, bad: x.v === 'other' }; }), app.ui.closeReason || null, function (v) { app.ui.closeReason = v; app.render({ keep: false }); })));
        if (app.ui.closeReason === 'other') closeBody.push(banner(T('manualBreak'), 'bad'));
      }
      closeBody.push(btn(T('closeConfirm'), function () {
        var p = app.ui.closePrice === undefined ? defPrice : app.ui.closePrice;
        var reason = app.ui.closeReason;
        var kind = ck;
        app.ui.closeKind = null; app.ui.closePrice = undefined; app.ui.closeReason = null;
        app.update(function (n) { J.closeTrade(n, { kind: kind, price: p, reason: reason, nowMs: app.nowMs, nowMin: time.nightMinutes(app.nowMs, key) }); }, { key: key });
        app.toast(T('closedToast'));
        app.go(5);
      }, 'primary', { disabled: reasonOk && R.num(price) !== null ? null : true, 'data-testid': 'btn-close-confirm' }));
    }
    var rSug;
    el.appendChild(section(T('t4Close'), closeBody));
    return el;
  }

  // ================= TẦNG 5 =================
  function download(name, text, mime) {
    var blob = new Blob([text], { type: mime + ';charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  ui.download = download;

  function tier5(app) {
    var st = app.state, el = h('div', { class: 'tier', 'data-tier': '5' });
    // chọn đêm xem / nhập: các đêm có thẻ hoặc có lệnh, mới nhất trước (REVIEW-1 mục 20)
    var keys = Object.keys(st.nights).filter(function (k) { var n0 = st.nights[k]; return n0.card.lockedAt || (n0.trades || []).length; });
    if (keys.indexOf(app.key) < 0) keys.push(app.key);
    keys.sort().reverse();
    var key = app.ui.viewKey && keys.indexOf(app.ui.viewKey) >= 0 ? app.ui.viewKey : app.key;
    var night = key === app.key ? app.night : st.nights[key];
    var UO = { key: key, keep: true };
    if (keys.length > 1) el.appendChild(h('div', { class: 'ctl nightpick' }, h('div', { class: 'ctl-label', text: T('nightPick') }),
      seg(keys.map(function (k) { return { v: k, label: k + (k === app.key ? ' ·' : '') }; }), key, function (v) { app.ui.viewKey = v === app.key ? null : v; app.render({ keep: false }); }, { noToggle: true, cls: 'small wrap', label: T('nightPick') })));

    // --- đêm nay ---
    var rows = night.trades.map(J.rowOf);
    var tbl = h('table', { class: 'journal', 'data-testid': 'journal' });
    tbl.appendChild(h('thead', {}, h('tr', {}, ['jh1', 'jh2', 'jh3', 'jh4', 'jh5', 'jh6', 'jh7'].map(function (k) { return h('th', { text: T(k) }); }))));
    var tb = h('tbody');
    rows.forEach(function (r) {
      tb.appendChild(h('tr', { class: r.ruleBreak ? 'rb' : '', 'data-trade': r.id },
        h('td', { text: r.time }), h('td', { text: r.side }), h('td', { text: r.name }), h('td', { text: r.mode }), h('td', { text: r.checks }), h('td', { text: r.sl }), h('td', { class: 'r', text: r.r + (r.warn ? ' ⚠' : '') })));
      if (r.warn) tb.appendChild(h('tr', { class: 'warnrow' }, h('td', { colspan: '7', text: T('warnRow', { time: r.time, w: r.warn }) })));
    });
    if (!rows.length) tb.appendChild(h('tr', {}, h('td', { colspan: '7', class: 'muted', text: T('noTrades') })));
    tbl.appendChild(tb);

    var machine = night.tally.machine || 0;
    var manual = night.tally.manual;
    var mism = J.tallyMismatch(night);
    var foot = h('div', { class: 'jfoot' },
      chip(T('machineSum', { r: J.fmtR(machine) }), ''),
      h('label', { class: 'mini-l' }, T('yourSum'), numInput(manual === undefined ? null : manual, function (v) { app.update(function (n) { J.manualTally(n, v, app.nowMs); }, { key: key, keep: true }); }, { id: 'manual', unit: 'R', label: T('yourSum'),
        onCommit: function () { app.render({ keep: false }); } })),
      mism ? chip(T('mismatch'), 'bad') : null,
      chip(T('breaksN', { n: J.ruleBreakCount(night) }), J.ruleBreakCount(night) ? 'bad' : ''),
      chip(T('sweptN', { n: J.sweptCount(night) }), ''),
      btn(T('endNight'), function () { app.update(function (n) { n.tally.closedAt = app.nowMs; }, { key: key }); app.toast(T('endedToast')); }, 'primary', { disabled: manual === null || manual === undefined ? true : null, title: manual === null || manual === undefined ? T('endNeed') : null }));
    var tradeExtrasList = night.trades.filter(function (t) { return t.exit; }).map(function (t) { return h('div', { class: 'tx' }, h('span', { class: 'muted', text: t.time + ' ' + J.rowOf(t).name }), tradeExtras(app, t, key)); });
    el.appendChild(section(T('t5Tonight', { key: key }), [h('div', { class: 'tablewrap' }, tbl), foot, tradeExtrasList.length ? h('details', { class: 'fold' }, h('summary', { text: T('afterClose') }), tradeExtrasList) : null], { help: { text: T('t5Help'), ref: 'nhat-ky-lenh' } }));

    // --- tuần ---
    var w = J.weekStats(st, key);
    function pairsT(obj, names) {
      var ks = Object.keys(obj); if (!ks.length) return '—';
      return ks.map(function (k) { var nm = names && names[k] ? (names[k].name || names[k].label) : k; return T('pairFmt', { name: nm, n: obj[k].n, r: J.fmtR(obj[k].r) }); }).join(' · ');
    }
    el.appendChild(section(T('t5Week'), h('div', { class: 'kvgrid wide' },
      kv(T('wBreaks'), w.ruleBreaks + ' / ' + w.trades, w.ruleBreaks ? 'bad' : 'good'),
      kv(T('wSwept'), String(w.swept)),
      kv(T('wByScen'), pairsT(w.byScenario, C.scenarios)),
      kv(T('wByZone'), pairsT(w.byZone, C.zoneTypes)),
      kv(T('wCounter'), w.counter.n + ' · ' + J.fmtR(w.counter.r) + ' R'),
      kv(T('wStreak'), String(w.streak))), { help: { text: T('t5WeekHelp'), ref: 'cuoi-tuan' } }));

    // --- xuất / nhập ---
    var due = (time.dowOfKey(key) === 5 || time.dowOfKey(key) === 6 || time.dowOfKey(key) === 0) && (!st.settings.lastExportAt || app.nowMs - st.settings.lastExportAt > 5 * 86400000);
    var ex = [];
    if (due) ex.push(banner(T('exportDue'), 'warn'));
    ex.push(h('div', { class: 'row wrap' },
      btn(T('exMd'), function () { download('tram-dem-vang-' + key + '.md', J.toMarkdown(night, key), 'text/markdown'); }, '', { 'data-testid': 'ex-md' }),
      btn(T('exMdCopy'), function () { var tx = J.toMarkdown(night, key); if (navigator.clipboard) navigator.clipboard.writeText(tx).then(function () { app.toast(T('copied')); }, function () { app.toast(T('copyFail')); }); else app.toast(T('copyFail')); }),
      btn(T('exJson'), function () { download('tram-dem-vang.json', S.exportJSON(st), 'application/json'); app.updateState(function (s) { s.settings.lastExportAt = app.nowMs; }, { keep: true }); }, '', { 'data-testid': 'ex-json' }),
      btn(T('exCsv'), function () { download('tram-dem-vang.csv', J.toCSV(st), 'text/csv'); }, '', { 'data-testid': 'ex-csv' })));
    var fileIn = h('input', { type: 'file', accept: '.json,application/json', class: 'filein', 'aria-label': T('importJson'), 'data-testid': 'import-file',
      onchange: function (e) {
        var f = e.target.files && e.target.files[0]; if (!f) return;
        var rd = new FileReader();
        rd.onload = function () {
          var res = S.importMerge(app.state, String(rd.result));
          if (!res.ok) { app.toast(C.errors[res.error] || res.error); return; }
          app.updateState(function (s) { s.nights = res.state.nights; }, {});
          app.toast(T('importDone', { a: res.nightsNew, b: res.nightsMerged, c: res.tradesAdded }));
        };
        rd.readAsText(f);
      } });
    ex.push(h('div', { class: 'row wrap' }, h('span', { class: 'ctl-label', text: T('importJson') }), fileIn));
    el.appendChild(section(T('t5Export'), ex));

    // --- cài đặt ---
    var s0 = st.settings;
    function setS(fn) { app.updateState(fn, {}); }
    el.appendChild(section(T('t5Settings'), [
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('setTheme') }),
        seg([{ v: 'dark', label: T('themeDark') }, { v: 'light', label: T('themeLight') }], s0.theme, function (v) { setS(function (s) { s.settings.theme = v || 'dark'; }); }, { noToggle: true })),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('setGuide') }),
        seg([{ v: 'new', label: T('guideNew') }, { v: 'quen', label: T('guideQuen') }], s0.guideLevel, function (v) { setS(function (s) { s.settings.guideLevel = v || 'new'; }); }, { noToggle: true })),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('setCapital') }),
        numInput(s0.capital, function (v) { app.updateState(function (s) { s.settings.capital = v; }, { keep: true }); }, { unit: '$', id: 'capital', label: T('setCapital') })),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('setRisk') }),
        numInput(s0.riskPct, function (v) { app.updateState(function (s) { s.settings.riskPct = v; }, { keep: true }); }, { unit: '%', id: 'riskpct', label: T('setRisk') })),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label' }, h('span', { text: T('setDst') }), ui.helpBtn({ text: T('setDstHelp'), ref: 'thoi-gian' })),
        seg([{ v: true, label: T('yes') }, { v: false, label: T('no') }], s0.dstShift !== false, function (v) { setS(function (s) { s.settings.dstShift = !!v; }); }, { noToggle: true })),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('setKeys') }),
        seg([{ v: true, label: T('yes') }, { v: false, label: T('no') }], s0.shortcuts !== false, function (v) { setS(function (s) { s.settings.shortcuts = !!v; }); }, { noToggle: true })),
      h('p', { class: 'muted', text: T('keysHelp') }),
      h('div', { class: 'row' }, btn(T('wipe'), function () {
        app.confirm({ title: T('wipeTitle'), text: T('wipeText'), ok: T('wipeOk'), danger: true }).then(function (ok) {
          if (ok) { app.updateState(function (s) { s.nights = {}; }, {}); app.toast(T('wiped')); }
        });
      }, 'danger', { 'data-testid': 'wipe' }), h('span', { class: 'muted', text: T('version', { v: R.APP_VERSION }) }))
    ]));
    return el;
  }

  ui.tier4 = { render: tier4 }; ui.tier5 = { render: tier5 };
})(this);
