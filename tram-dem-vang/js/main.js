/* Trạm Đêm Vàng — dây nối: trạng thái, vẽ lại, điều hướng tầng, hộp thoại, phím tắt, service worker. */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules, E = TDV.engine, S = TDV.store, time = TDV.time, N = TDV.news;
  var T = ui.T, h = ui.h, btn = ui.btn;

  var memory = {}, memStorage = { getItem: function (k) { return k in memory ? memory[k] : null; }, setItem: function (k, v) { memory[k] = String(v); } };
  var storage;
  try { storage = root.localStorage; storage.getItem('x'); } catch (e) { storage = memStorage; }

  var state = S.load(storage);
  var feed = N.loadStored(storage);   // lịch tin Forex Factory bản gần nhất (data/ff.json) — mở file:// vẫn có
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
    app.feed = feed;
    app.news = N.forNight(feed, app.key, app.nowMs, app.useDst);
    app.res = E.evaluate({ nights: nights, nightKey: app.key, now: app.nowMs, settings: state.settings, news: app.news });
  }
  function persist() {
    var ok = S.save(storage, state);
    app.saveFailed = !ok;
    return ok;
  }

  // ---------- hoãn vẽ lại khi đang bấm (USER-TEST-2 mục 1) ----------
  // Gõ số rồi bấm nút ngay: mousedown làm ô mất focus ⇒ sự kiện change ⇒ ghi state ⇒ vẽ lại cả tầng, nút bị thay trước khi nhả chuột
  // nên cú bấm đầu bị nuốt. Cách sửa: state vẫn ghi ngay trong change, còn VẼ LẠI do change gây ra được hoãn tới sau cú bấm
  // (cú bấm tự vẽ lại và gộp phần hoãn) hoặc sau 0 ms nếu không có chuột (phím Tab). Ô đang focus được giữ lại sau khi vẽ.
  var hold = { depth: 0, ptr: false, pending: null, t: null };
  function queueRender(opts) {
    if (!hold.pending) hold.pending = Object.assign({}, opts);
    else { var keep = !!(hold.pending.keep && opts.keep); Object.assign(hold.pending, opts); hold.pending.keep = keep; }
  }
  function flushHold() { if (hold.pending && hold.depth === 0) render({}); }
  app.hold = function (fn) {
    var ptr = hold.ptr;
    hold.depth++;
    try { fn(); } finally { hold.depth--; }
    if (hold.pending && hold.depth === 0 && !ptr) setTimeout(flushHold, 0);
  };
  function pointerUp() { hold.ptr = false; clearTimeout(hold.t); hold.t = setTimeout(flushHold, 100); }   // nếu không có click thì vẽ bù sau 100 ms
  ['pointerdown', 'mousedown', 'touchstart'].forEach(function (ev) { document.addEventListener(ev, function () { clearTimeout(hold.t); hold.ptr = true; }, true); });
  ['pointerup', 'mouseup', 'pointercancel', 'touchend', 'touchcancel'].forEach(function (ev) { document.addEventListener(ev, pointerUp, true); });
  document.addEventListener('click', function () { setTimeout(flushHold, 0); });
  // phím Tab: ô kế tiếp nhận focus ngay sau change ⇒ vẽ lại tại đó (ô mới đã focus nên được giữ lại), xong trước khi người dùng gõ tiếp
  document.addEventListener('focusin', function () { if (!hold.ptr) flushHold(); }, true);

  // ----- giữ trạng thái mở / đóng của khung "?" và mục thu gọn qua mỗi lần vẽ lại (REVIEW-3 mục 3) -----
  // Cú bấm "?" hoặc tiêu đề mục thu gọn ngay sau khi gõ số xảy ra TRƯỚC lần vẽ bù (hoãn), nên DOM bị thay làm mất trạng thái.
  var UI_ROOTS = ['status', 'main', 'verdict', 'card'];
  function rootOf(el) { for (var i = 0; i < UI_ROOTS.length; i++) { var r = $(UI_ROOTS[i]); if (r && r.contains(el)) return r; } return null; }
  function uiKey(el, sel) { var r = rootOf(el); if (!r) return null; return r.id + ':' + [].slice.call(r.querySelectorAll(sel)).indexOf(el); }
  function snapUi() {
    var s = { pops: [], details: [], panel: app.panelEl && app.panelEl.getAttribute ? app.panelEl.getAttribute('data-tier') : null, key: app._lastKey };
    document.querySelectorAll('.pop:not([hidden])').forEach(function (p) { var k = uiKey(p, '.pop'); if (k) s.pops.push(k); });
    document.querySelectorAll('details[open]').forEach(function (d) {
      var k = uiKey(d, 'details'), sm = d.querySelector('summary');
      if (k) s.details.push({ k: k, t: sm ? sm.textContent.slice(0, 8) : '' });
    });
    return s;
  }
  function restoreUi(s) {
    // chỉ khôi phục khi vẫn đang ở cùng tầng và cùng đêm: đổi tầng thì để mọi thứ đóng
    var cur = app.panelEl && app.panelEl.getAttribute ? app.panelEl.getAttribute('data-tier') : null;
    if (s.panel !== cur || s.key !== app.key) return;
    function find(k, sel) { var m = /^(\w+):(\d+)$/.exec(k); if (!m) return null; var r = $(m[1]); return r ? r.querySelectorAll(sel)[+m[2]] || null : null; }
    s.pops.forEach(function (k) {
      var p = find(k, '.pop'); if (!p) return;
      p.removeAttribute('hidden');
      var b = p.parentNode && p.parentNode.querySelector('.help'); if (b) b.setAttribute('aria-expanded', 'true');
    });
    s.details.forEach(function (x) {
      var d = find(x.k, 'details'), sm = d && d.querySelector('summary');
      if (d && (!sm || sm.textContent.slice(0, 8) === x.t)) d.setAttribute('open', '');
    });
  }
  // nút đang focus bằng bàn phím (Tab): khóa = ô điều khiển gần nhất + data-v / data-testid / chữ (REVIEW-3 mục 15)
  function btnKey(b) {
    var c = b.closest('[data-ctl]');
    return JSON.stringify([c ? c.getAttribute('data-ctl') : '', b.getAttribute('data-v') || '', b.getAttribute('data-testid') || '', b.textContent.slice(0, 20)]);
  }
  function snapFocus() {
    var a = document.activeElement, main = $('main');
    if (a && a.tagName === 'BUTTON' && main && main.contains(a)) {
      var vis = false; try { vis = a.matches(':focus-visible'); } catch (e) { /* trình duyệt cũ */ }
      return vis ? { btn: btnKey(a) } : null;
    }
    if (!a || !main.contains(a) || !/^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)) return null;
    var all = [].slice.call(main.querySelectorAll('input, textarea, select'));
    var s = { i: all.indexOf(a), id: a.dataset ? a.dataset.id || null : null, label: a.getAttribute('aria-label'), start: null, end: null };
    try { s.start = a.selectionStart; s.end = a.selectionEnd; } catch (e) { /* ô không có vùng chọn */ }
    return s;
  }
  function restoreFocus(s) {
    if (!s) return;
    var main = $('main'), el = null;
    if (s.btn) {
      var bs = main.querySelectorAll('button');
      for (var bi = 0; bi < bs.length; bi++) if (btnKey(bs[bi]) === s.btn) { try { bs[bi].focus({ preventScroll: true }); } catch (e) { /* bỏ qua */ } return; }
      return;
    }
    if (s.id) el = main.querySelector('[data-id="' + s.id + '"]');
    if (!el) { var c = main.querySelectorAll('input, textarea, select')[s.i]; if (c && c.getAttribute('aria-label') === s.label) el = c; }
    if (!el) return;
    try { el.focus({ preventScroll: true }); if (s.start !== null && el.setSelectionRange) el.setSelectionRange(s.start, s.end); } catch (e) { /* bỏ qua */ }
  }

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

  // sửa thẻ phiên: ghi lại giờ sửa sau 19:20, hỏi xác nhận khi đang canh kèo
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
    app.ui.curPrice = null; app.ui.fillPrice = undefined; app.ui.closeKind = null; app.ui.sub = 'canh'; app.ui.jumpDone = false; app.ui.jumpNote = false;
    app.go(4);
    app.toast(o.paper || res.paper ? T('enteredPaper') : T('entered'));
  };
  app.forceEnter = function () {
    var res = freshEnterCtx();
    if (!res.side || !res.calc.numsOk || res.verdict === 'ENTRY' || res.verdict === 'LOCKED') return;
    var vars = ui.codeVars(app);
    var codes = J.forceCodes(res).map(function (c) { return ui.codeText(c, vars).replace(/[.\s]+$/, ''); });
    var paper = res.paper;
    app.confirm({ title: T('forceTitle'), text: T('forceText', { list: codes.join(' · ') }) + (paper ? ' ' + T('forcePaperNote') : ' ' + T('forceCount')), ok: T('forceOk'), danger: true }).then(function (ok) {
      if (!ok) return;
      compute();
      var r2 = app.res;
      app.update(function (n) { J.createTrade(n, r2, { kind: 'market', price: r2.calc.entry, paper: paper, ruleBreak: true, nowMs: app.nowMs, nowMin: app.nowMin }); });
      app.ui.curPrice = null; app.ui.closeKind = null; app.ui.sub = 'canh'; app.ui.jumpDone = false; app.ui.jumpNote = false;
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
    // scroll-padding-bottom của html chừa chỗ cho thanh phán quyết khi cuộn tới ô
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
    if (hold.depth > 0) { queueRender(opts); return; }
    if (hold.pending) { var p = hold.pending; hold.pending = null; var keep = !!(p.keep && opts.keep); opts = Object.assign({}, p, opts); opts.keep = keep; }
    var snap = snapUi();
    paint(opts);
    restoreUi(snap);
  }
  function paint(opts) {
    compute();
    if (app._lastKey !== null && app._lastKey !== app.key) opts.keep = false;
    app._lastKey = app.key;
    if (app.tier === null) app.tier = suggestTier();
    document.documentElement.setAttribute('data-theme', state.settings.theme === 'light' ? 'light' : 'dark');

    ui.clear($('status')).appendChild(ui.status.render(app));
    if (app.saveFailed) {
      $('status').appendChild(h('div', { class: 'banner bad savefail', role: 'alert' }, h('span', { text: T('storeFail') + ' ' }),
        btn(T('storeFailBtn'), function () { ui.download('tram-dem-vang.json', S.exportJSON(state), 'application/json'); }, 'small')));
    }
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
    var focus = snapFocus();
    ui.clear(main);
    var mod = ui['tier' + app.tier];
    var node = mod.render(app);
    app.panelEl = node;
    main.appendChild(h('div', { class: 'tierhead' }, h('h2', { text: C.tiers[app.tier].long })));
    main.appendChild(node);
    if (opts.keepScroll !== false) window.scrollTo(0, sy);
    restoreFocus(focus);
    if (node._needScroll) node._needScroll();
  }
  app.render = render;

  // ---------- phím tắt (tầng 3) ----------
  function isTyping(t) { return t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable); }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (modalStack.length) { closeModal(false); return; }
      if ($('card').classList.contains('open')) { app.toggleCard(false); return; }
      if (isTyping(e.target)) e.target.blur();
      return;
    }
    // không chạy phím tắt khi đang ở bất kỳ ô nhập nào, kể cả lúc ô vừa bị thay do vẽ lại hoãn (REVIEW-3 mục 4)
    // đang nhấn giữ chuột (ô nhập vừa mất focus, vẽ lại còn hoãn): bỏ qua phím; hết nhấn thì vẽ nốt phần hoãn rồi mới xét phím
    if (hold.ptr) return;
    if (hold.pending) flushHold();
    if (isTyping(e.target) || isTyping(document.activeElement) || e.ctrlKey || e.metaKey || e.altKey) return;
    if (modalStack.length) return;
    if (e.key === 'Enter' && e.target && e.target.tagName === 'BUTTON') return;   // nút đang focus tự xử lý Enter
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
      setSetup(function (s0) { s0.side = side; });
    } else if ((k === 'u' || k === 'U' || k === 'v' || k === 'V') && res.scenario && res.scenario !== 'C') {
      var v = (k === 'u' || k === 'U') ? 'U' : 'V';
      app.ui.sub = 'bam';
      setSetup(function (s0) { s0.b1 = v; });
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

  // ---------- Từ điển ----------
  // Từ điển: xếp theo chữ cái, có ô tìm; mở từ nút "?" thì cuộn tới đúng mục và tô sáng (USER-TEST-2 mục 3)
  function plain(s) { return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd'); }
  app.openGlossary = function (key) {
    var list = C.glossary.slice().sort(function (a, b) { return a.term.localeCompare(b.term, 'vi'); });
    var dl = h('dl', { class: 'glossary' }), items = [];
    list.forEach(function (g) {
      var dt = h('dt', { text: g.term, 'data-gloss': g.key }), dd = h('dd', { text: ui.fillTimes(g.def) });
      dl.appendChild(dt); dl.appendChild(dd);
      items.push({ g: g, dt: dt, dd: dd, hay: plain(g.term + ' ' + g.def) });
    });
    var none = h('p', { class: 'muted', hidden: true, text: T('glossaryNone') });
    var search = h('input', { type: 'search', class: 'field gsearch', placeholder: T('glossarySearch'), 'aria-label': T('glossarySearch'), 'data-testid': 'glossary-search',
      oninput: function () {
        var q = plain(search.value.trim()), any = false;
        items.forEach(function (it) { var show = !q || it.hay.indexOf(q) >= 0; it.dt.hidden = !show; it.dd.hidden = !show; if (show) any = true; });
        none.hidden = any;
      } });
    document.querySelectorAll('.pop').forEach(function (p) { p.setAttribute('hidden', ''); });
    var bd = openModal(h('div', { class: 'dlg glossarybox', 'data-testid': 'glossary' }, h('h3', { text: T('glossaryTitle') }), h('p', { class: 'muted', text: T('glossaryHint') }), search, dl, none,
      h('div', { class: 'actions' }, btn(T('close'), function () { closeModal(false); }, 'primary'))));
    var box = bd.querySelector('.glossarybox');
    if (root.innerWidth <= 600) search.blur();   // điện thoại: không tự bật bàn phím che nửa danh sách
    box.scrollTop = 0; bd.querySelector('.modal').scrollTop = 0;
    var hit = key && items.filter(function (it) { return it.g.key === key; })[0];
    if (hit) {
      search.blur();
      hit.dt.classList.add('hl'); hit.dd.classList.add('hl');
      hit.dt.scrollIntoView({ block: 'start' });
    }
  };

  // vốn và % rủi ro: hỏi lần đầu mở (có "để sau") và mở lại từ thông báo NO_SIZE_ZERO (QĐ-21)
  app.openCapital = function (first) {
    var cap = state.settings.capital, pct = state.settings.riskPct;
    var capIn = ui.numInput(cap, function (v) { cap = v; }, { id: 'cap-dlg', label: T('setCapital'), unit: '$' });
    var pctIn = ui.numInput(pct, function (v) { pct = v; }, { id: 'risk-dlg', label: T('setRisk'), unit: '%' });
    var content = h('div', { class: 'dlg', 'data-testid': 'capital-dlg' }, h('h3', { text: T('capTitle') }), h('p', { text: T('capText') }),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('setCapital') }), capIn),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('setRisk') }), pctIn),
      h('div', { class: 'actions' },
        btn(T('capLater'), function () { closeModal(false); }, 'ghost', { 'data-testid': 'cap-later' }),
        btn(T('capSave'), function () {
          if (!(cap > 0) || !(pct > 0)) { app.toast(T('capBad')); return; }
          app.updateState(function (s) { s.settings.capital = cap; s.settings.riskPct = pct; s.settings.sizeAsked = true; });
          closeModal(true);
        }, 'primary', { 'data-testid': 'cap-save' })));
    openModal(content, function () {
      if (first && !state.settings.sizeAsked) app.updateState(function (s) { s.settings.sizeAsked = true; });
    });
  };

  // ngăn thẻ phiên trên điện thoại: mở / đóng bằng nút, nút ✕, chạm ra ngoài, Esc (REVIEW-1 mục 2)
  app.toggleCard = function (open) {
    var el = $('card');
    var on = open === undefined ? !el.classList.contains('open') : !!open;
    el.classList.toggle('open', on);
    $('cardscrim').classList.toggle('on', on);
    $('cardtoggle').textContent = on ? T('close') : T('cardToggle');
    $('cardtoggle').setAttribute('aria-expanded', on ? 'true' : 'false');
  };

  // ---------- lịch tin Forex Factory (QĐ-22): tải ./data/ff.json lúc mở và mỗi 5′ khi tab hiện ----------
  var newsAt = 0;
  function fetchNews() {
    if (!root.fetch || root.location.protocol === 'file:') return;
    if (document.visibilityState === 'hidden') return;
    newsAt = Date.now();
    root.fetch('./data/ff.json?t=' + Date.now(), { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (f) {
        if (!N.validFeed(f)) return;
        var nf = N.newer(f, feed);
        if (JSON.stringify(nf) === JSON.stringify(feed)) return;
        feed = nf; N.saveStored(storage, nf);
        render({ keep: true });
      })
      .catch(function () { /* mất mạng: giữ bản đã lưu */ });
  }
  app.fetchNews = fetchNews;

  // ---------- khởi động ----------
  function boot() {
    compute();
    app.tier = suggestTier();
    $('cardtoggle').textContent = T('cardToggle');
    $('cardtoggle').addEventListener('click', function () { app.toggleCard(); });
    $('cardscrim').addEventListener('click', function () { app.toggleCard(false); });
    document.title = T('appTitle');
    $('skip').textContent = T('skip');
    render();
    if (!state.settings.sizeAsked) app.openCapital(true);
    fetchNews();
    setInterval(fetchNews, 300000);
    document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'visible' && Date.now() - newsAt > 60000) fetchNews(); });
    setInterval(function () {
      compute();
      var sig = JSON.stringify([app.res.enabled, !!app.res.newsHit, app.res.longestBarActive, app.res.locks.tier3]);
      var typing = isTyping(document.activeElement);
      if (app._sig !== undefined && sig !== app._sig && !typing) render({ keep: false });
      else render({ keep: true });
      if (!typing) app._sig = sig;
    }, 15000);
    if (root.ResizeObserver) new ResizeObserver(function () { document.documentElement.style.setProperty('--vbar-h', $('verdict').offsetHeight + 'px'); }).observe($('verdict'));
    window.addEventListener('storage', function (e) {
      if (e.key !== S.KEY) return;
      state = S.load(storage); app.state = state; app._draft = null; render({ keep: false });
      app.toast(T('otherTab'));
    });

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
