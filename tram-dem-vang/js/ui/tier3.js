/* Trạm Đêm Vàng — tầng 3: Sổ (lệnh đang mở + nhập kết quả, bảng 7 cột, tuần, xuất / nhập, cài đặt). */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules, time = TDV.time, S = TDV.store;
  var T = ui.T, h = ui.h, seg = ui.seg, chip = ui.chip, btn = ui.btn, numInput = ui.numInput, textInput = ui.textInput, section = ui.section, banner = ui.banner;

  function kv(label, value, cls) { return h('div', { class: 'kv' }, h('span', { class: 'k', text: label }), h('span', { class: 'v' + (cls ? ' ' + cls : ''), text: value })); }

  // "SL bị quét rồi giá tới TP?" + ghi chú, cho một dòng sổ
  function tradeExtras(app, trade, key) {
    return h('div', { class: 'extras' },
      h('label', { class: 'tick' }, h('input', { type: 'checkbox', checked: trade.sweptThenTP === true ? true : null,
        onchange: function (e) { app.update(function (n) { var t = J.tradeById(n, trade.id); if (t) t.sweptThenTP = e.target.checked; }, { key: key, keep: true }); } }), h('span', { text: T('swept') })),
      textInput(trade.notes || '', function (v) { app.update(function (n) { var t = J.tradeById(n, trade.id); if (t) t.notes = v; }, { key: key, keep: true }); }, { placeholder: T('tradeNote'), label: T('tradeNote'), max: 200 }));
  }

  // ================= LỆNH ĐANG MỞ: dòng Sổ chưa có kết quả, nhập kết quả ngay tại đây =================
  function openCard(app, o) {
    var t = o.trade, key = o.nightKey;
    var all = app.ui.closing = app.ui.closing || {};
    var st = all[t.id] = all[t.id] || {};
    var paper = t.flags.indexOf('paper') >= 0;
    var row = J.rowOf(t);
    var be = J.beInfo(t);
    var head = h('div', { class: 'ohead' }, chip(t.side, ui.dirCls(t.side)), h('b', { text: row.name }), h('span', { class: 'muted', text: row.zone + ' · ' + t.time + (key !== app.key ? ' · ' + key : '') }),
      paper ? chip(T('openPaper'), 'warn') : null, t.flags.indexOf('RULE_BREAK') >= 0 ? chip(T('ruleBreakFlag'), 'bad') : null, t.flags.indexOf('HALF') >= 0 ? chip(T('sizeHalfShort'), 'warn') : null);
    var grid = h('div', { class: 'kvgrid' }, kv(T('kvSide'), t.side), kv(T('kvScen'), row.name), kv(T('kvZone'), row.zone), kv(T('kvTime'), t.time));
    var remind = h('p', { class: 'beline muted', 'data-testid': 'be-remind', text: T(be.needBar ? 'beRemindBar' : 'beRemind', { r: J.fmtTrim(be.target) }) });
    var warn = row.warn ? h('p', { class: 'prob', text: '⚠ ' + row.warn }) : null;

    var kinds = [{ v: 'TP', label: T('closeTp') }, { v: 'SL', label: T('closeSl'), bad: true }, { v: 'BE', label: T('closeBe') }, { v: 'MANUAL', label: T('closeManual') }];
    var body = [seg(kinds, st.kind || null, function (v) { st.kind = v; st.r = v ? J.defaultR(t, v) : undefined; st.reason = null; app.render({ keep: false }); }, { cls: 'close', label: T('t4Close') })];
    if (st.kind) {
      var rIn;
      var quick = [3, 2, 1, 0, -1].map(function (q) {
        return btn((q > 0 ? '+' : q < 0 ? '−' : '') + Math.abs(q), function () { st.r = q; if (rIn) rIn.input.value = ui.fmtIn(q); app.render({ keep: false }); }, 'small rq' + (st.r === q ? ' sel' : ''), { 'data-testid': 'rq-' + q, 'aria-pressed': st.r === q ? 'true' : 'false' });
      });
      rIn = numInput(st.r === undefined ? null : st.r, function (v) { st.r = v === null ? undefined : v; }, { id: 'exitr', label: T('exitR'), unit: 'R' });
      body.push(h('div', { class: 'row wrap' }, h('label', { class: 'mini-l' }, T('exitR'), rIn), h('div', { class: 'row rqrow' }, quick), h('span', { class: 'muted small', text: T('rQuickHint') })));
      if (st.kind === 'MANUAL') {
        body.push(h('div', { class: 'ctl' }, h('div', { class: 'ctl-label' }, h('span', { text: T('manualReason') }), ui.helpBtn({ text: T('manualHelp'), ref: 'tp-be' })),
          seg(C.closeReasons.map(function (x) { return { v: x.v, label: x.label, bad: x.v === 'other' }; }), st.reason || null, function (v) { st.reason = v; app.render({ keep: false }); })));
        if (st.reason === 'other') body.push(banner(T('manualBreak'), 'bad'));
      }
      body.push(h('label', { class: 'tick36 sweptrow' }, h('input', { type: 'checkbox', 'data-testid': 'open-swept', checked: st.swept ? true : null, onchange: function (e) { st.swept = e.target.checked; } }), h('span', { class: 'tt', text: T('swept') })));
      body.push(btn(T('closeConfirm'), function () {
        var rv = R.num(st.r);
        if (st.kind === 'MANUAL' && !st.reason) { app.toast(T('needReason')); return; }
        if (rv === null) { app.toast(T('needExit')); return; }
        var kind = st.kind, reason = st.reason, swept = !!st.swept;
        delete all[t.id];
        app.update(function (n) {
          var tr = J.tradeById(n, t.id); if (!tr) return;
          J.closeTrade(n, t.id, { kind: kind, r: rv, reason: reason, nowMs: app.nowMs, nowMin: time.nightMinutes(app.nowMs, key) });
          if (swept) tr.sweptThenTP = true;
        }, { key: key });
        app.toast(T('closedToast'));
      }, 'primary', { 'data-testid': 'btn-close-confirm' }));
    }
    return h('section', { class: 'panel opentrade', 'data-testid': 'open-trade', 'data-trade-open': t.id },
      h('h3', { class: 'ptitle' }, h('span', { text: T('t4Title') })), head, grid, warn, remind, h('div', { class: 'ptitle2', text: T('t4Close') }), body);
  }

  // ================= SỔ =================
  function download(name, text, mime) {
    var blob = new Blob([text], { type: mime + ';charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  ui.download = download;

  function tier3(app) {
    var st = app.state, el = h('div', { class: 'tier', 'data-tier': '3' });
    // dòng lệnh đang mở nằm trên cùng, kèm nút kết quả
    (app.res.opens || []).forEach(function (o) { el.appendChild(openCard(app, o)); });
    // chọn đêm xem / nhập: các đêm có thẻ hoặc có lệnh, mới nhất trước (REVIEW-1 mục 20)
    var keys = Object.keys(st.nights).filter(function (k) { var n0 = st.nights[k]; return n0.card.lockedAt || (n0.trades || []).length; });
    if (keys.indexOf(app.key) < 0) keys.push(app.key);
    keys.sort().reverse();
    var key = app.ui.viewKey && keys.indexOf(app.ui.viewKey) >= 0 ? app.ui.viewKey : app.key;
    var night = key === app.key ? app.night : st.nights[key];
    if (keys.length > 1) el.appendChild(h('div', { class: 'ctl nightpick' }, h('div', { class: 'ctl-label', text: T('nightPick') }),
      seg(keys.map(function (k) { return { v: k, label: k + (k === app.key ? ' ·' : '') }; }), key, function (v) { app.ui.viewKey = v === app.key ? null : v; app.render({ keep: false }); }, { noToggle: true, cls: 'small wrap', label: T('nightPick') })));

    // --- đêm nay ---
    var rows = night.trades.map(J.rowOf);
    var tbl = h('table', { class: 'journal', 'data-testid': 'journal' });
    tbl.appendChild(h('thead', {}, h('tr', {}, ['jh1', 'jh2', 'jh3', 'jh4', 'jh5', 'jh6', 'jh7'].map(function (k) { return h('th', { text: T(k) }); }))));
    var tb = h('tbody');
    rows.forEach(function (r) {
      tb.appendChild(h('tr', { class: r.ruleBreak ? 'rb' : '', 'data-trade': r.id },
        h('td', { text: r.time }), h('td', { text: r.side }), h('td', { text: r.name }), h('td', { text: r.zone }), h('td', { text: r.checks }), h('td', { text: r.sl }), h('td', { class: 'r', text: r.r + (r.warn ? ' ⚠' : '') })));
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
      // Nút luôn bấm được (USER-TEST-4 b1): nút xám nuốt cú bấm đầu sau khi gõ "Bạn cộng". Đọc thẳng giá trị trong ô lúc bấm, không chờ sự kiện change.
      btn(T('endNight'), function () {
        var inp = document.querySelector('[data-id="manual"]');
        var typed = inp && /\S/.test(inp.value) ? J.parseNum(inp.value) : null;
        var v = typed !== null ? typed : (manual === undefined ? null : manual);
        if (v === null) { app.toast(T('endNeed')); if (inp) inp.focus(); return; }
        app.update(function (n) { if (typed !== null) J.manualTally(n, typed, app.nowMs); n.tally.closedAt = app.nowMs; }, { key: key });
        app.toast(T('endedToast'));
      }, 'primary', { 'data-testid': 'btn-end-night' }));
    var tradeExtrasList = night.trades.filter(function (t) { return t.exit; }).map(function (t) { return h('div', { class: 'tx' }, h('span', { class: 'muted', text: t.time + ' ' + J.rowOf(t).name }), tradeExtras(app, t, key)); });
    el.appendChild(section(T('t5Tonight', { key: key }), [h('div', { class: 'tablewrap' }, tbl), h('p', { class: 'muted legend', text: C.journal.mdLegend }), foot, tradeExtrasList.length ? h('details', { class: 'fold' }, h('summary', { text: T('afterClose') }), tradeExtrasList) : null], { help: { text: T('t5Help'), ref: 'nhat-ky-lenh' } }));

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

  ui.tier3 = { render: tier3 };
})(this);
