/* Trạm Đêm Vàng — dây nối: trạng thái, vẽ lại, điều hướng tầng, hộp thoại, phím tắt, service worker. */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules, E = TDV.engine, S = TDV.store, time = TDV.time;
  var T = ui.T, h = ui.h, btn = ui.btn;

  var memory = {}, memStorage = { getItem: function (k) { return k in memory ? memory[k] : null; }, setItem: function (k, v) { memory[k] = String(v); } };
  var storage;
  try { storage = root.localStorage; storage.getItem('x'); } catch (e) { storage = memStorage; }

  var state = S.load(storage);
  var app = { state: state, ui: { sub: 'canh' }, tier: null, _draft: null, _lastKey: null, panelEl: null };
  TDV.app = app;

  var $ = function (id) { return document.getElementById(id); };

  // ---------- tính toán ----------
  function compute() {
    app.nowMs = Date.now();
    app.settings = state.settings;
    app.useDst = state.settings.dstShift !== false;
    app.key = time.nightKey(app.nowMs, app.useDst);
    if (state.nights[app.key]) { app.night = state.nights[app.key]; app._draft = null; }
    else {
      if (!app._draft || app._draft.key !== app.key) app._draft = { key: app.key, n: J.newNight(app.key) };
      app.night = app._draft.n;
    }
    app.nowMin = time.nightMinutes(app.nowMs, app.key);
    var nights = state.nights;
    if (!nights[app.key]) { nights = Object.assign({}, nights); nights[app.key] = app.night; }
    app.res = E.evaluate({ nights: nights, nightKey: app.key, now: app.nowMs, settings: state.settings });
  }
  function persist() { S.save(storage, state); }

  // ---------- cập nhật ----------
  app.update = function (fn, opts) {
    opts = opts || {};
    compute();
    var key = opts.key || app.key;
    if (!state.nights[key]) { state.nights[key] = key === app.key ? app.night : J.newNight(key); app._draft = null; }
    fn(state.nights[key], state);
    persist();
    app.render(opts);
  };
  app.updateState = function (fn, opts) { compute(); fn(state); persist(); app.render(opts || {}); };

  // sửa thẻ phiên: ghi vết sau 19:20, hỏi xác nhận khi đang canh kèo
  app.cardEdit = function (what, label, fn) {
    compute();
    var pol = J.cardEditPolicy(app.night, what, app.nowMin, app.key, app.useDst);
    function doit() {
      app.update(function (n) { fn(n); J.applyCardEdit(n, what, label, app.nowMs, app.nowMin, app.key, app.useDst); });
    }
    if (pol.confirm) app.confirm({ title: T('editWhileSetupTitle'), text: T('editWhileSetupText'), ok: T('editWhileSetupOk'), danger: true }).then(function (ok) { if (ok) doit(); });
    else doit();
  };

  // ---------- hộp thoại ----------
  var modalStack = [];
  function closeModal(result) {
    var m = modalStack.pop();
    if (!m) return;
    m.backdrop.remove();
    if (m.prevFocus && m.prevFocus.focus) try { m.prevFocus.focus(); } catch (e) { /* bỏ qua */ }
    if (m.onClose) m.onClose(result);
  }
  function openModal(content, onClose) {
    var backdrop = h('div', { class: 'backdrop', onclick: function (e) { if (e.target === backdrop) closeModal(false); } },
      h('div', { class: 'modal', role: 'dialog', 'aria-modal': 'true' }, content));
    modalStack.push({ backdrop: backdrop, onClose: onClose, prevFocus: document.activeElement });
    $('overlay').appendChild(backdrop);
    var first = backdrop.querySelector('input, button.primary, button.danger, button');
    if (first) first.focus();
    return backdrop;
  }
  app.openModal = openModal; app.closeModal = closeModal;
  app.confirm = function (o) {
    return new Promise(function (resolve) {
      var content = h('div', { class: 'dlg' },
        h('h3', { text: o.title }), h('p', { text: o.text }),
        h('div', { class: 'actions' },
          btn(o.cancel || T('cancel'), function () { closeModal(false); }, 'ghost', { 'data-testid': 'dlg-cancel' }),
          btn(o.ok || T('confirm'), function () { closeModal(true); }, o.danger ? 'danger' : 'primary', { 'data-testid': 'dlg-ok' })));
      openModal(content, function (r) { resolve(!!r); });
    });
  };
  app.toast = function (text) {
    var t = h('div', { class: 'toast-item', role: 'status', text: text });
    $('toast').appendChild(t);
    setTimeout(function () { t.classList.add('out'); setTimeout(function () { t.remove(); }, 400); }, 3600);
  };

  // ---------- vào lệnh ----------
  function freshEnterCtx() { compute(); return app.res; }
  app.openEnter = function () {
    var res = freshEnterCtx();
    if (res.verdict !== 'ENTRY') { render(); return; }
    var kind = 'market', price = res.calc.entry;
    var priceWrap = ui.numInput(price, function (v) { price = v; }, { id: 'enterprice', label: T('enterPrice') });
    var segEl = ui.seg([{ v: 'market', label: 'market' }, { v: 'limit', label: 'limit' }], kind, function (v) { kind = v || 'market'; refreshHint(); markSel(); }, { noToggle: true, label: T('enterKind') });
    function markSel() { segEl.querySelectorAll('.opt').forEach(function (b) { var on = b.dataset.v === kind; b.classList.toggle('sel', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); }); }
    var hint = h('p', { class: 'muted' });
    function refreshHint() { hint.textContent = kind === 'market' ? T('enterMarketHint') : T('enterLimitHint'); }
    refreshHint();
    var content = h('div', { class: 'dlg' }, h('h3', { text: T('enterTitle') }),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('enterKind') }), segEl),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('enterPrice') }), priceWrap), hint,
      h('div', { class: 'actions' }, btn(T('cancel'), function () { closeModal(false); }, 'ghost'),
        btn(T('enterConfirm'), function () { closeModal(true); app.enter({ kind: kind, price: price }); }, 'primary big', { 'data-testid': 'enter-confirm' })));
    openModal(content);
  };
  app.enter = function (o) {
    var res = freshEnterCtx();
    if (res.verdict !== 'ENTRY') { render(); return; }
    app.update(function (n) { J.createTrade(n, res, { kind: o.kind, price: o.price, paper: !!o.paper || res.paper, ruleBreak: false, nowMs: app.nowMs, nowMin: app.nowMin }); });
    app.ui.curPrice = null; app.ui.fillPrice = undefined; app.ui.closeKind = null;
    app.go(4);
    app.toast(o.paper || res.paper ? T('enteredPaper') : T('entered'));
  };
  app.forceEnter = function () {
    var res = freshEnterCtx();
    if (!res.side || !res.calc.numsOk || res.verdict === 'ENTRY' || res.verdict === 'LOCKED') return;
    var codes = (res.reasons.length ? res.reasons : res.missing).map(function (c) { return ui.codeText(c, { sl: J.fmt(res.calc.slDist), c6: J.fmt(R.num(app.night.setup.c6)) }); });
    var paper = res.paper;
    app.confirm({ title: T('forceTitle'), text: T('forceText', { list: codes.join(' · ') }) + (paper ? ' ' + T('forcePaperNote') : ' ' + T('forceCount')), ok: T('forceOk'), danger: true }).then(function (ok) {
      if (!ok) return;
      compute();
      var r2 = app.res;
      app.update(function (n) { J.createTrade(n, r2, { kind: 'market', price: r2.calc.entry, paper: paper, ruleBreak: true, nowMs: app.nowMs, nowMin: app.nowMin }); });
      app.ui.curPrice = null; app.ui.closeKind = null;
      app.go(4);
      app.toast(paper ? T('enteredPaper') : T('forcedToast'));
    });
  };
  app.focusCtl = function (id) {
    if (!id) return;
    app.ui.sub = /^b/.test(id) ? 'bam' : 'canh';
    app.tier = 3;
    render();
    var t = document.querySelector('[data-ctl="' + id + '"]');
    if (t) { t.scrollIntoView({ block: 'center', behavior: 'smooth' }); t.classList.add('flash'); setTimeout(function () { t.classList.remove('flash'); }, 1200); }
  };

  // ---------- điều hướng ----------
  function tierLock(i) {
    if (i === 3) return app.res.locks.tier3;
    if (i === 4) return app.res.open ? null : 'NO_OPEN';
    return null;
  }
  app.go = function (i) {
    compute();
    var lock = tierLock(i);
    if (lock) { app.toast(T('lock_' + lock)); return; }
    app.tier = i;
    render();
    window.scrollTo(0, 0);
  };
  function suggestTier() {
    var n = app.night, res = app.res;
    if (res.open) return 4;
    if (!n.card.lockedAt) return n.t0.touched ? 1 : 0;
    return res.locks.tier3 ? 1 : 3;
  }

  // ---------- vẽ ----------
  function renderNav() {
    var nav = ui.clear($('tiers'));
    C.tiers.forEach(function (t) {
      var lock = tierLock(t.id);
      var cls = 'tierbtn' + (app.tier === t.id ? ' active' : '') + (lock ? ' locked' : '');
      var done = (t.id === 1 && app.night.card.lockedAt) || (t.id === 0 && app.night.t0.touched);
      nav.appendChild(h('button', { type: 'button', class: cls, 'data-tier-btn': t.id, 'aria-current': app.tier === t.id ? 'step' : null, 'aria-disabled': lock ? 'true' : null,
        title: lock ? T('lock_' + lock) : t.long, onclick: function () { app.go(t.id); } },
        h('span', { class: 'tnum', text: String(t.id) }), h('span', { class: 'tname', text: t.name }), done ? h('span', { class: 'tdone', text: '✓' }) : null, lock ? h('span', { class: 'tlock', text: '🔒' }) : null));
    });
  }

  function render(opts) {
    opts = opts || {};
    compute();
    if (app._lastKey !== null && app._lastKey !== app.key) opts.keep = false;
    app._lastKey = app.key;
    if (app.tier === null) app.tier = suggestTier();
    document.documentElement.setAttribute('data-theme', state.settings.theme === 'light' ? 'light' : 'dark');

    ui.clear($('status')).appendChild(ui.status.render(app));
    renderNav();
    ui.clear($('card')).appendChild(ui.card.render(app));

    var vb = $('verdict');
    if (app.tier === 3 && !app.res.locks.tier3) {
      ui.clear(vb).appendChild(ui.verdict.render(app));
      document.body.classList.add('has-vbar');
    } else { ui.clear(vb); document.body.classList.remove('has-vbar'); }

    if (opts.keep && app.panelEl && app.panelEl.isConnected) {
      if (app.panelEl._live) app.panelEl._live(app);
      return;
    }
    var main = $('main');
    var sy = window.scrollY;
    ui.clear(main);
    var mod = ui['tier' + app.tier];
    var node = mod.render(app);
    app.panelEl = node;
    main.appendChild(h('div', { class: 'tierhead' }, h('h2', { text: C.tiers[app.tier].long })));
    main.appendChild(node);
    if (opts.keepScroll !== false) window.scrollTo(0, sy);
  }
  app.render = render;

  // ---------- phím tắt (tầng 3) ----------
  function isTyping(t) { return t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable); }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (modalStack.length) { closeModal(false); return; }
      if (isTyping(e.target)) e.target.blur();
      return;
    }
    if (isTyping(e.target) || e.ctrlKey || e.metaKey || e.altKey) return;
    if (modalStack.length) return;
    if (state.settings.shortcuts === false) return;
    var k = e.key;
    if (k === '?') { openKeys(); e.preventDefault(); return; }
    if (app.tier !== 3 || app.res.locks.tier3) return;
    var res = app.res, st = app.night.setup;
    function setSetup(fn) { app.update(function (n) { fn(n.setup, n); n.setup.updatedAt = app.nowMs; }); }
    if (k >= '1' && k <= '4') {
      var s = R.SCENARIOS[+k - 1];
      if (res.enabled[s] && s !== res.scenario) { app.toast(ui.codeText(res.enabled[s])); return; }
      setSetup(function (s0, n) { n.setup = res.scenario === s ? Object.assign({}, s0) : J.changeScenario(s0, s); });
    } else if ((k === 'b' || k === 'B' || k === 's' || k === 'S') && res.scenario === 'B') {
      var side = (k === 'b' || k === 'B') ? 'buy' : 'sell';
      setSetup(function (s0) { s0.side = s0.side === side ? undefined : side; if (s0.side === undefined) delete s0.side; });
    } else if ((k === 'u' || k === 'U' || k === 'v' || k === 'V') && res.scenario && res.scenario !== 'C') {
      var v = (k === 'u' || k === 'U') ? 'U' : 'V';
      app.ui.sub = 'bam';
      setSetup(function (s0) { if (s0.b1 === v) delete s0.b1; else s0.b1 = v; });
    } else if (k === 'Enter') {
      if (res.verdict === 'ENTRY') { if (res.paper) app.enter({ kind: 'market', paper: true }); else app.openEnter(); e.preventDefault(); }
    } else if (k === 'n' || k === 'N') {
      app.ui.sub = 'canh'; app.update(function (n) { n.setup = {}; }); app.toast(T('newSetupDone'));
    }
  });
  function openKeys() {
    var rows = ['1', '2', '3', '4', 'B / S', 'U / V', 'Enter', 'N', 'Esc', '?'].map(function (k, i) { return h('div', { class: 'kv' }, h('span', { class: 'k' }, h('kbd', { text: k })), h('span', { class: 'v', text: T('key' + i) })); });
    openModal(h('div', { class: 'dlg' }, h('h3', { text: T('keysTitle') }), rows, h('div', { class: 'actions' }, btn(T('close'), function () { closeModal(false); }, 'primary'))));
  }

  // ---------- khởi động ----------
  function boot() {
    compute();
    app.tier = suggestTier();
    $('cardtoggle').textContent = T('cardToggle');
    $('cardtoggle').addEventListener('click', function () { $('card').classList.toggle('open'); });
    document.title = T('appTitle');
    $('skip').textContent = T('skip');
    render();
    setInterval(function () { render({ keep: true }); }, 15000);

    if (/^https?:$/.test(location.protocol)) {
      var link = document.createElement('link'); link.rel = 'manifest'; link.href = 'manifest.webmanifest'; document.head.appendChild(link);
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js').then(function (reg) {
          var hadController = !!navigator.serviceWorker.controller;
          navigator.serviceWorker.addEventListener('controllerchange', function () {
            if (!hadController) return;
            var t = h('div', { class: 'toast-item sticky', role: 'status' }, h('span', { text: T('newVersion') + ' ' }), btn(T('reload'), function () { location.reload(); }, 'primary small'));
            $('toast').appendChild(t);
          });
        }, function () { /* không đăng ký được: vẫn chạy bình thường */ });
      }
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})(this);
