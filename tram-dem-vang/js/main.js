/* Trạm Đêm Vàng — dây nối: trạng thái, vẽ lại, điều hướng tầng, hộp thoại, ghi lệnh, phím tắt, service worker. */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules, E = TDV.engine, S = TDV.store, time = TDV.time, N = TDV.news;
  var T = ui.T, h = ui.h, btn = ui.btn;

  var memory = {}, memStorage = { getItem: function (k) { return k in memory ? memory[k] : null; }, setItem: function (k, v) { memory[k] = String(v); } };
  var storage;
  try { storage = root.localStorage; storage.getItem('x'); } catch (e) { storage = memStorage; }

  var state = S.load(storage);
  // dữ liệu v1 cũ: lưu lại ngay dạng v2 (chỉ khi phiên bản khác, để không bắn sự kiện storage sang thẻ khác khi không đổi gì)
  try { var rawSaved = storage.getItem(S.KEY); if (rawSaved && JSON.parse(rawSaved).version !== S.VERSION) S.save(storage, state); } catch (e) { /* bỏ qua */ }
  var feed = N.loadStored(storage);   // lịch tin Forex Factory bản gần nhất (data/ff.json) — mở file:// vẫn có
  var app = { state: state, ui: {}, tier: null, _draft: null, _lastKey: null, panelEl: null };
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
    app.res = E.evaluate(app.night, app.nowMs, state.settings, app.news, { key: app.key, nights: nights });
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

  // ---------- ghi lệnh, nhảy khối ----------
  // Ghi một dòng vào Sổ từ khối scen. Bình thường chỉ khi khối đó là ENTRY; o.force = "Vẫn vào" (cờ phá luật + danh sách ô thiếu).
  app.writeTrade = function (scen, o) {
    o = o || {};
    compute();
    var res = app.res, bl = res.blocks[scen], e = res.entry;
    var forced = !!o.force;
    if (!bl || (!forced && !(e && e.scen === scen))) { render(); return; }
    if (forced && !bl.side) return;
    var missing = forced ? bl.missing.concat(res.common.filter(function (x) { return !x.ok; }).map(function (x) { return 'common:' + x.id; })) : [];
    var paper = res.paper;
    app.update(function (n) { J.createTrade(n, res, { scen: scen, ruleBreak: forced, paper: paper, missing: missing, nowMs: app.nowMs, nowMin: app.nowMin }); });
    app.toast(paper ? T('enteredPaper') : forced ? T('forcedToast') : T('entered'));
  };
  app.forceTrade = function (scen) {
    compute();
    var res = app.res, bl = res.blocks[scen];
    if (!bl || !bl.side || res.entry) return;
    var list = bl.missing.map(function (id) { return ui.fillTimes(C.itemLabel(scen, id)); })
      .concat(res.common.filter(function (x) { return !x.ok; }).map(function (x) { return C.itemLabel(scen, 'common:' + x.id); }));
    var paper = res.paper;
    app.confirm({ title: T('forceTitle'), text: T('forceText', { n: list.length, list: list.slice(0, 5).join(' · ') + (list.length > 5 ? ' …' : '') }) + (paper ? ' ' + T('forcePaperNote') : ' ' + T('forceCount')), ok: T('forceOk'), danger: true }).then(function (ok) {
      if (ok) app.writeTrade(scen, { force: true });
    });
  };
  // bỏ tick của khối (giữ hướng, vùng); dùng cho nút "Xóa tick" và phím N
  app.clearBlockTicks = function (scen) {
    if (!scen) return;
    app.update(function (n) { J.clearBlock(n, scen); });
    app.toast(T('clearBlockDone', { s: scen }));
  };
  function flash(t) { if (t) { t.classList.add('flash'); setTimeout(function () { t.classList.remove('flash'); }, 1200); } }
  // nhảy tới khối: mở khối đó, thu gọn các khối còn lại; focus vào tiêu đề khối để Tab đi tiếp vào trong khối
  app.jumpTo = function (scen) {
    if (app.tier !== 2) { app.tier = 2; render(); }
    var m = {}; m[scen] = true;
    if (app.panelEl && app.panelEl._setOpen) app.panelEl._setOpen(m, true);
    var t = document.getElementById('blk-' + scen);
    if (t) {
      t.scrollIntoView({ block: 'start' }); flash(t);
      var tg = t.querySelector('.blk-toggle'); if (tg) try { tg.focus({ preventScroll: true }); } catch (e) { /* bỏ qua */ }
    }
  };
  // id dạng "B:ctx2" hoặc "common:news": mở khối chứa ô, cuộn tới ô và nháy sáng
  app.focusItem = function (ref) {
    if (app.tier !== 2) { app.tier = 2; render(); }
    var mm = /^([A-D]):/.exec(ref);
    if (mm && app.panelEl && app.panelEl._setOpen) { var m = {}; m[mm[1]] = true; app.panelEl._setOpen(m, false); }
    var t = document.querySelector('[data-item="' + ref + '"]');
    if (t) { t.scrollIntoView({ block: 'center' }); flash(t); }
  };
  // bấm một vùng ở thẻ phiên: điền vào khối đang làm (khối chạm cuối, hoặc khối đang mở)
  app.pickZone = function (zid) {
    if (app.tier !== 2) return;
    var se = app.night.se, s = se.last;
    if (!s) s = R.SCENARIOS.filter(function (x) { return app.ui.blkOpen && app.ui.blkOpen[x]; })[0];
    if (!s) { app.toast(T('pickBlockFirst')); return; }
    app.update(function (n) { var b = J.block(n, s); if (!b.side && s !== 'C' && (app.res.bias === 'BUY' || app.res.bias === 'SELL')) b.side = app.res.bias.toLowerCase(); b.zoneId = zid; J.touchBlock(n, s); }, { keep: false });
  };
  // ghi kết quả lệnh đang mở từ thanh dưới (không phải sang Sổ). c = {kind, price, reason}
  app.closeOpen = function (o, c) {
    var t = o.trade, key = o.nightKey;
    app.update(function (n) {
      J.closeTrade(n, t.id, { kind: c.kind, r: c.r, reason: c.reason, nowMs: app.nowMs, nowMin: time.nightMinutes(app.nowMs, key) });
    }, { key: key });
    app.toast(T('closedToast'));
  };

  // ---------- điều hướng ----------
  app.go = function (i) {
    compute();
    app.tier = i;
    render();
    window.scrollTo(0, 0);
  };
  function suggestTier() {
    var n = app.night, res = app.res;
    if (!n.card.lockedAt) return n.t0.touched ? 1 : 0;
    return res.open ? 3 : 2;
  }

  // ---------- vẽ ----------
  function renderNav() {
    var nav = ui.clear($('tiers'));
    C.tiers.forEach(function (t) {
      var cls = 'tierbtn' + (app.tier === t.id ? ' active' : '');
      var done = (t.id === 1 && app.night.card.lockedAt) || (t.id === 0 && app.night.t0.touched);
      nav.appendChild(h('button', { type: 'button', class: cls, 'data-tier-btn': t.id, 'aria-current': app.tier === t.id ? 'step' : null, title: t.long, onclick: function () { app.go(t.id); } },
        h('span', { class: 'tnum', text: String(t.id) }), h('span', { class: 'tname', text: t.name }), done ? h('span', { class: 'tdone', text: '✓' }) : null));
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
    if (app.tier === 2) {
      // đang gõ giá thoát trong thanh dưới thì không dựng lại thanh (mất focus giữa chừng)
      var af = document.activeElement;
      if (!(app.ui.barClose && af && af.tagName === 'INPUT' && vb.contains(af))) ui.clear(vb).appendChild(ui.verdict.render(app));
      document.body.classList.add('has-vbar');
    } else { ui.clear(vb); document.body.classList.remove('has-vbar'); document.documentElement.style.setProperty('--jbh', '0px'); }

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

  // ---------- phím tắt (tầng 2) ----------
  function isTyping(t) { return t && ((t.tagName === 'INPUT' && !/^(checkbox|radio|button)$/.test(t.type)) || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable); }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (modalStack.length) { closeModal(false); return; }
      // khung "?" đang mở: Esc đóng và trả focus về nút "?"
      var po = document.querySelector('.pop:not([hidden])');
      if (po) {
        var hb = po.parentNode && po.parentNode.querySelector('.help');
        document.querySelectorAll('.pop').forEach(function (p) { p.setAttribute('hidden', ''); });
        document.querySelectorAll('.help[aria-expanded="true"]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
        if (hb) try { hb.focus(); } catch (x) { /* bỏ qua */ }
        return;
      }
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
    if (app.tier !== 2) return;
    if (k >= '1' && k <= '4') { app.jumpTo(R.SCENARIOS[+k - 1]); e.preventDefault(); }
    else if (k === 'Enter') { if (app.res.entry) { app.writeTrade(app.res.entry.scen, {}); e.preventDefault(); } }
    else if (k === 'n' || k === 'N') { app.clearBlockTicks(app.night.se.last); }
  });
  function openKeys() {
    var rows = ['1 – 4', 'Enter', 'N', 'Esc', '?'].map(function (k, i) { return h('div', { class: 'kv' }, h('span', { class: 'k' }, h('kbd', { text: k })), h('span', { class: 'v', text: T('key' + i) })); });
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
    var bd = openModal(h('div', { class: 'dlg glossarybox', 'data-testid': 'glossary' },
      h('div', { class: 'ghead' }, h('h3', { text: T('glossaryTitle') }), h('button', { type: 'button', class: 'gclose', 'aria-label': T('close'), text: '✕', onclick: function () { closeModal(false); } }),
        h('p', { class: 'muted', text: T('glossaryHint') }), search), dl, none));
    bd.classList.add('gloss-modal');
    var box = bd.querySelector('.glossarybox');
    search.focus();
    if (root.innerWidth <= 600) search.blur();   // điện thoại: không tự bật bàn phím che nửa danh sách
    box.scrollTop = 0; bd.querySelector('.modal').scrollTop = 0;
    var hit = key && items.filter(function (it) { return it.g.key === key; })[0];
    if (hit) {
      search.blur();
      hit.dt.classList.add('hl'); hit.dd.classList.add('hl');
      hit.dt.scrollIntoView({ block: 'start' });
    }
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
    if (!root.fetch) return;
    if (document.visibilityState === 'hidden') return;
    newsAt = Date.now();
    var base = root.location.protocol === 'file:' ? 'https://anhnmthe176111.github.io/tram-dem-vang/' : './';   // mở file local: lấy lịch từ Pages (có CORS *)
    root.fetch(base + 'data/ff.json?t=' + Date.now(), { cache: 'no-store' })
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
    fetchNews();
    setInterval(fetchNews, 300000);
    document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'visible' && Date.now() - newsAt > 60000) fetchNews(); });
    setInterval(function () {
      compute();
      var sig = JSON.stringify([!!app.res.newsHit, app.res.opens.length, !!app.night.card.lockedAt]);
      var typing = isTyping(document.activeElement);
      if (app._sig !== undefined && sig !== app._sig && !typing) render({ keep: false });
      else render({ keep: true });
      if (!typing) app._sig = sig;
    }, 15000);
    if (root.ResizeObserver) {
      new ResizeObserver(function () { document.documentElement.style.setProperty('--vbar-h', $('verdict').offsetHeight + 'px'); }).observe($('verdict'));
      new ResizeObserver(function () { document.documentElement.style.setProperty('--sbh', $('status').offsetHeight + 'px'); }).observe($('status'));   // thanh nhảy A·B·C·D dính ngay dưới thanh trạng thái
    }
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
