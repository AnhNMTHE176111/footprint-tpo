/* Trạm Đêm Vàng — tầng 0 (trước), tầng 1 (vùng + thẻ phiên), tầng 2 (chế độ). */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules, time = TDV.time;
  var T = ui.T, h = ui.h, seg = ui.seg, chip = ui.chip, btn = ui.btn, numInput = ui.numInput, textInput = ui.textInput, section = ui.section, banner = ui.banner;

  var YESNO = [{ v: true, label: T('yes') }, { v: false, label: T('no'), bad: true }];
  var SIDE_OPTS = [{ v: 'upper', label: T('sideUpperOpt') }, { v: 'lower', label: T('sideLowerOpt') }];

  function lead(text) { return h('p', { class: 'lead', text: text }); }

  // ================= TẦNG 0 =================
  // Tối giản (QĐ-22): một câu tỉnh táo · khối "Tin tối nay" tự lấy từ Forex Factory (kèm các dòng mờ mặc định) · một ô kịch bản nền.
  // Thêm khung giờ tay / FOMC / ngày tin lớn ghi tay gập trong "Thêm tay…".
  function impChip(imp) { return h('span', { class: 'imp ' + (imp === 'High' ? 'high' : 'med'), text: imp === 'High' ? T('impHigh') : T('impMed') }); }
  function toggleWin(app, w, hmShown) {
    function setOn(n, on) {
      if (w.src === 'ff') {
        n.t0.newsOverrides = n.t0.newsOverrides || {};
        if (on) delete n.t0.newsOverrides[w.id]; else n.t0.newsOverrides[w.id] = { on: false, offAt: J.hm(app.nowMs) };
      } else {
        var x = n.t0.windows.filter(function (z) { return z.id === w.id; })[0];
        if (!x) return;
        x.on = on; if (on) delete x.offAt; else x.offAt = J.hm(app.nowMs);
      }
    }
    if (w.on) {
      app.confirm({ title: T('offConfirmTitle'), text: T('offConfirmText', { hm: hmShown }), ok: T('offConfirmOk'), danger: true }).then(function (ok) {
        if (ok) app.update(function (n) { setOn(n, false); });
      });
    } else app.update(function (n) { setOn(n, true); });
  }

  function tier0(app) {
    var night = app.night, t0 = night.t0, key = app.key, useDst = app.useDst, news = app.news || { status: 'none', events: [], skipped: [] };
    var el = h('div', { class: 'tier t0min', 'data-tier': '0' });
    el.appendChild(lead(T('t0Lead')));

    el.appendChild(h('div', { class: 'ctl', 'data-ctl': 't0alert' },
      h('div', { class: 'ctl-label' }, h('span', { text: T('t0Alert') })),
      seg(YESNO, t0.alert === null || t0.alert === undefined ? null : t0.alert, function (v) { app.update(function (n) { n.t0.alert = v; }); })));
    if (t0.alert === false) el.appendChild(banner(T('t0ViewOnly'), 'warn'));

    // ----- Tin tối nay -----
    var ok = news.status === 'ok';
    var wins = R.effectiveWindows(t0, key, news);
    var winById = {}; wins.forEach(function (w) { winById[w.id] = w; });
    var rows = [];
    news.events.forEach(function (e) {
      var w = ok ? winById[e.id] : null;
      var nums = h('span', { class: 'nnums muted', text: T('newsNums', { f: e.forecast || '—', p: e.previous || '—', a: e.actual || '—' }) });
      var ctl = e.warnOnly ? h('span', { class: 'muted small', text: T('warnOnlyTag') })
        : (w ? btn(w.on ? T('on') : T('off'), function () { toggleWin(app, w, e.hm); }, 'sw ' + (w.on ? 'on' : 'off'), { 'aria-label': e.title + ' ' + e.hm }) : null);
      rows.push({ nm: e.nightMin, el: h('div', { class: 'nrow' + (w && !w.on ? ' off' : '') + (ok ? '' : ' dim'), 'data-news': e.id },
        h('span', { class: 'ntime', text: e.hm }),
        h('span', { class: 'nname' }, h('span', { class: 'ntitle', text: e.title }), e.warnOnly ? h('span', { class: 'ccy', text: e.country }) : null, impChip(e.impact)),
        nums, ctl) });
    });
    // dòng mờ: mặc định (21:00, 19:30 nếu có), khung thêm tay, NYSE
    wins.filter(function (w) { return w.src !== 'ff'; }).forEach(function (w) {
      var r = time.windowRange(w, key, useDst);
      var name = w.id === 'w2100' ? T('rowCore') : w.id === 'w1930' ? T('row1930') : w.kind === 'fomc' ? T('rowFomc') : T('rowCustom');
      var isDefault = w.id === 'w1930' || w.id === 'w2100';
      rows.push({ nm: r.center, el: h('div', { class: 'nrow dim' + (w.on ? '' : ' off') },
        h('span', { class: 'ntime', text: time.fmtMin(r.center) }),
        h('span', { class: 'nname' }, h('span', { class: 'ntitle', text: name }), h('span', { class: 'muted small', text: T('winShort', { n: w.minutesBefore || 0 }) })),
        h('span', { class: 'nnums muted', text: w.offAt ? T('offAt', { hm: w.offAt }) : '' }),
        h('span', { class: 'nctl' },
          btn(w.on ? T('on') : T('off'), function () { toggleWin(app, w, time.fmtMin(r.center)); }, 'sw ' + (w.on ? 'on' : 'off'), { 'aria-label': name + ' ' + time.fmtMin(r.center) }),
          isDefault ? null : btn('✕', function () { app.update(function (n) { n.t0.windows = n.t0.windows.filter(function (z) { return z.id !== w.id; }); }); }, 'ghost small', { 'aria-label': T('remove') }))) });
    });
    var ny = time.windowRange(R.NYSE_WARN, key, useDst);
    rows.push({ nm: ny.center, el: h('div', { class: 'nrow dim' }, h('span', { class: 'ntime', text: time.fmtMin(ny.center) }),
      h('span', { class: 'nname' }, h('span', { class: 'ntitle', text: T('nyseRow') })), h('span', { class: 'nnums' }), chip(T('alwaysOn'), 'mini')) });
    rows.sort(function (a, b) { return a.nm - b.nm; });

    var hm = news.fetchedAt ? J.hm(Date.parse(news.fetchedAt)) : null;
    var head = h('div', { class: 'nhead' }, h('h3', { class: 'ptitle' }, h('span', { text: T('newsTitle') })),
      hm ? h('span', { class: 'muted small', 'data-testid': 'news-updated', text: T('newsUpdated', { hm: hm }) }) : h('span', { class: 'muted small', text: T('newsNoFeed') }));
    var nd = app.res.newsDay, ndRow = null;
    if (nd) ndRow = h('div', { class: 'ndrow', 'data-testid': 'newsday-tag' }, chip(T('newsDayTag'), 'warn'),
      btn(T('newsDayOffBtn'), function () { app.update(function (n) { n.t0.newsDaySet = true; n.t0.newsDay = false; }); }, 'ghost small'));
    else if (t0.newsDaySet && ok && news.newsDay) ndRow = h('div', { class: 'ndrow' }, h('span', { class: 'muted small', text: T('newsDayOff') }),
      btn(T('newsDayOnBtn'), function () { app.update(function (n) { n.t0.newsDaySet = false; n.t0.newsDay = false; }); }, 'ghost small'));
    var list = h('div', { class: 'nlist', 'data-testid': 'news-list' }, rows.map(function (r) { return r.el; }));
    var body = [head, ndRow];
    if (news.status === 'stale') body.push(h('p', { class: 'muted small', text: T('newsStaleNote', { min: news.ageMin }) }));
    if (ok && !news.events.length) body.push(h('p', { class: 'muted small', text: T('newsNone') }));
    if (news.skipped && news.skipped.length) body.push(h('p', { class: 'muted small', text: T('newsSkipped', { list: news.skipped.join(', ') }) }));
    body.push(list);

    // gập: thêm khung giờ tay, FOMC, ngày tin lớn ghi tay
    var f = app.ui.winForm = app.ui.winForm || { at: '', rank: 2, before: 5, after: 5 };
    var form = h('div', { class: 'wform' },
      h('span', { class: 'ctl-label', text: T('addWindow') }),
      textInput(f.at, function (v) { f.at = v; }, { placeholder: T('timePh'), label: T('timePh'), max: 5 }),
      seg([{ v: 1, label: T('rank1') }, { v: 2, label: T('rank2') }], f.rank, function (v) { f.rank = v || 2; app.render({ keep: false }); }, { noToggle: true }),
      numInput(f.before, function (v) { f.before = v === null ? 0 : v; }, { unit: T('minBefore'), label: T('minBefore') }),
      numInput(f.after, function (v) { f.after = v === null ? 0 : v; }, { unit: T('minAfter'), label: T('minAfter') }),
      btn(T('add'), function () {
        var m = time.parseHM(f.at);
        if (m === null) { app.toast(T('badTime')); return; }
        app.update(function (n) { n.t0.windows.push({ id: 'w' + Date.now().toString(36), kind: 'custom', rank: f.rank, at: time.fmtMin(m), tz: 'VN', minutesBefore: f.before || 0, minutesAfter: f.after || 0, on: true }); });
        f.at = '';
      }),
      btn(T('addFomc', { fomc: time.fmtMin(time.markMin({ at: '01:00', tz: 'ET' }, key, useDst)) }), function () {
        app.update(function (n) { n.t0.windows.push({ id: 'fomc' + Date.now().toString(36), kind: 'fomc', rank: 2, at: '01:00', tz: 'ET', minutesBefore: 0, minutesAfter: 30, on: true }); });
      }, 'ghost'),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('newsDay') }),
        seg(YESNO.map(function (o) { return { v: o.v, label: o.label }; }), !!app.res.newsDay, function (v) { app.update(function (n) { n.t0.newsDaySet = true; n.t0.newsDay = !!v; }); }, { noToggle: true })));
    body.push(h('details', { class: 'fold manual' }, h('summary', { text: T('addManual') }), form));
    el.appendChild(h('section', { class: 'panel news' }, body));

    el.appendChild(h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('t0Note') }),
      textInput(t0.note, function (v) { app.update(function (n) { n.t0.note = v; }, { keep: true }); }, { placeholder: T('t0NotePh'), max: 160 })));

    el.appendChild(h('div', { class: 'actions' }, btn(T('t0Done'), function () { app.update(function (n) { n.t0.touched = true; }); app.go(1); }, 'primary')));
    return el;
  }

  // ================= TẦNG 1 =================
  // Thu gọn (QĐ-23): một dòng gợi ý kẻ chart · ba câu (hình hôm qua, đóng so với VA, giá so với VWAP tuần) · bias · vùng thêm nhanh · một ô ghi chú · chốt.
  // Q6 suy từ vùng cạnh (engine không dùng Q6); Q3 nợ suy từ vùng single print / poor high-low; Q2 "tail thật?" nằm ngay trên dòng vùng High / Low hôm qua.
  var QUICK_ZONES = ['vwapW', 'vwapD', 'vahEu', 'valEu', 'pocCluster', 'hvnW', 'hvn3w', 'lvn', 'highY', 'lowY', 'sp', 'nakedPoc', 'ibHigh', 'ibLow', 'rangeEdge', 'poorHigh', 'poorLow'];
  function zoneOrder() { return QUICK_ZONES.concat(R.ZONE_ORDER.filter(function (t) { return QUICK_ZONES.indexOf(t) < 0; })); }
  var TAIL_FROM = { highY: 'q2top', lowY: 'q2bot' };

  function tier1(app) {
    var night = app.night, card = night.card, a = card.answers, res = app.res;
    var el = h('div', { class: 'tier t1min', 'data-tier': '1' });
    el.appendChild(lead(T('t1Lead')));
    el.appendChild(h('p', { class: 'muted small drawhint', text: T('t1Draw') }));

    // ----- ba câu hỏi -----
    var qbox = h('div', { class: 'qgrid' });
    ['q1', 'q5'].forEach(function (qid) {
      var q = C.questions.filter(function (x) { return x.id === qid; })[0];
      qbox.appendChild(h('div', { class: 'ctl', 'data-ctl': q.id },
        h('div', { class: 'ctl-label' }, h('span', { text: T('qPrefix', { n: q.num, label: q.label }) }), ui.helpBtn(q.help)),
        seg(q.options, a[q.id] === undefined ? null : a[q.id], function (v) {
          var lbl = v ? q.options.filter(function (o) { return o.v === v; })[0].label : '—';
          app.cardEdit(q.id, T('editQ', { q: q.label, v: lbl }), function (n) { if (v === null) delete n.card.answers[q.id]; else n.card.answers[q.id] = v; });
        })));
    });
    var vw = h('div', { class: 'ctl', 'data-ctl': 'vwapW' },
      h('div', { class: 'ctl-label' }, h('span', { text: T('vwapQ') }), ui.helpBtn({ text: T('vwapHelp'), ref: 'ma-tran-bias' })),
      h('div', { class: 'row wrap vwapnums' },
        h('label', { class: 'mini-l' }, T('vwapNowL'), numInput(a.priceNow === undefined ? null : a.priceNow, function () {}, { id: 'pricenow', label: T('vwapNowL'), onCommit: function (v) { setVwapNums(app, 'priceNow', v); } })),
        h('label', { class: 'mini-l' }, T('vwapPriceL'), numInput(a.vwapPrice === undefined ? null : a.vwapPrice, function () {}, { id: 'vwapprice', label: T('vwapPriceL'), onCommit: function (v) { setVwapNums(app, 'vwapPrice', v); } })),
        seg(C.vwapOpts, a.vwapW || null, function (v) {
          var lbl = v ? C.vwapOpts.filter(function (o) { return o.v === v; })[0].label : '—';
          app.cardEdit('vwapW', T('editQ', { q: T('vwapQ'), v: lbl }), function (n) { if (v === null) delete n.card.answers.vwapW; else n.card.answers.vwapW = v; });
        }, { cls: 'small' })));
    qbox.appendChild(vw);
    if (a.vwapW === 'near') {
      qbox.appendChild(h('div', { class: 'ctl', 'data-ctl': 'recheck' },
        h('div', { class: 'ctl-label', text: T('recheck') }),
        seg([{ v: 'above', label: T('rcAbove') }, { v: 'below', label: T('rcBelow') }], card.bias.rechecked || null, function (v) {
          app.cardEdit('bias', T('editRecheck'), function (n) { if (v === null) delete n.card.bias.rechecked; else n.card.bias.rechecked = v; });
        })));
    }
    var biasBox = [qbox];
    biasBox.push(h('div', { class: 'biasline' }, h('span', { class: 'ctl-label', text: T('biasIs') }),
      h('span', { class: 'bigchip ' + ui.dirCls(res.bias), 'data-testid': 'bias-big', text: ui.biasText(res.bias) }),
      res.biasOverridden ? chip(T('overridden'), 'warn') : null,
      res.biasAuto && res.biasOverridden ? h('span', { class: 'muted', text: T('autoWas', { v: ui.biasText(res.biasAuto) }) }) : null));
    biasBox.push(h('details', { class: 'fold' }, h('summary', { text: T('overrideTitle') }),
      h('div', { class: 'ctl' },
        seg([{ v: 'BUY', label: 'BUY' }, { v: 'SELL', label: 'SELL' }, { v: 'KHÔNG', label: T('biasNone') }], card.bias.override || null, function (v) {
          app.cardEdit('bias', T('editOverride'), function (n) { if (v === null) { delete n.card.bias.override; delete n.card.bias.reason; } else n.card.bias.override = v; });
        }),
        card.bias.override ? textInput(card.bias.reason || '', function (v) { app.cardEdit('bias', T('editOverrideReason'), function (n) { n.card.bias.reason = v; }); }, { placeholder: T('overridePh'), label: T('overridePh') }) : null,
        card.bias.override && !(card.bias.reason && card.bias.reason.trim()) ? banner(T('overrideNeed'), 'warn') : null)));
    el.appendChild(section(T('t1Title2'), biasBox, { help: { text: T('t1BiasHelp'), ref: 'ma-tran-bias' } }));

    // ----- vùng: hàng thêm nhanh + danh sách gọn -----
    var zf = app.ui.zoneForm = app.ui.zoneForm || { type: 'vwapW', price: null, priceTo: null, side: 'upper', note: '' };
    var needSide = (R.ZONE_TYPES[zf.type] || {}).needSide;
    var full = res.zones.length >= R.T.zonesMax;
    function addZone() {
      if (zf.price === null) { app.toast(T('needPrice')); return; }
      if (full) { app.toast(T('zonesFull')); return; }
      var type = zf.type, side = (R.ZONE_TYPES[type] || {}).needSide ? zf.side : undefined, zp = zf.price, zpTo = zf.priceTo;
      zf.price = null; zf.priceTo = null;
      app.cardEdit(type, T('addedZone', { t: C.zoneTypes[type].label }), function (n) {
        var z = { id: J.newZoneId(n.card), type: type, price: zp, note: '' };
        if (zpTo !== null) z.priceTo = zpTo;
        if (side) z.side = side;
        n.card.zones.push(z);
      });
    }
    var sel = h('select', { class: 'field', 'aria-label': T('zoneType'), 'data-testid': 'zone-type', onchange: function (e) { zf.type = e.target.value; app.render({ keep: false }); } },
      zoneOrder().map(function (t) { return h('option', { value: t, selected: zf.type === t ? true : null, text: C.zoneTypes[t].label + ' · ' + C.zoneTypes[t].rank }); }));
    var priceIn = numInput(zf.price, function (v) { zf.price = v; }, { placeholder: T('price'), label: T('price'), id: 'zprice', onEnter: addZone });
    var addRow = h('div', { class: 'zform' }, sel, priceIn,
      numInput(zf.priceTo, function (v) { zf.priceTo = v; }, { placeholder: T('priceTo'), label: T('priceTo'), onEnter: addZone }),
      needSide ? seg(SIDE_OPTS, zf.side, function (v) { zf.side = v || 'upper'; app.render({ keep: false }); }, { noToggle: true, cls: 'small' }) : null,
      btn(T('addZone'), addZone, 'primary', { disabled: full ? true : null, 'data-testid': 'add-zone' }));

    var zbox = h('div', { class: 'zones' });
    res.zones.forEach(function (z) {
      var tdef = R.ZONE_TYPES[z.type] || {}, tf = TAIL_FROM[z.type];
      var row = h('div', { class: 'zrow', 'data-zone': z.id },
        h('span', { class: 'zid', text: z.id }),
        h('span', { class: 'zname', text: C.zoneTypes[z.type] ? C.zoneTypes[z.type].label : z.type }),
        numInput(z.price, function () {}, { label: T('price'), onCommit: function (v) { app.cardEdit(z.type, T('editZone', { z: z.id }), function (n) { zoneOf(n, z.id).price = v; }); } }),
        z.priceTo !== undefined && z.priceTo !== null ? numInput(z.priceTo, function () {}, { label: T('priceTo'), placeholder: T('priceTo'), onCommit: function (v) { app.cardEdit(z.type, T('editZone', { z: z.id }), function (n) { var zz = zoneOf(n, z.id); if (v === null) delete zz.priceTo; else zz.priceTo = v; }); } }) : null,
        tdef.needSide ? seg(SIDE_OPTS, z.side || null, function (v) { app.cardEdit(z.type, T('editZone', { z: z.id }), function (n) { zoneOf(n, z.id).side = v; }); }, { cls: 'small', noToggle: true }) : null,
        h('span', { class: 'zrank', text: C.zoneTypes[z.type] ? C.zoneTypes[z.type].rank : '' }),
        tf ? h('span', { class: 'tailq', 'data-ctl': tf }, h('span', { class: 'muted small', text: T('tailQ') }), ui.helpBtn(C.questions.filter(function (x) { return x.id === tf; })[0].help),
          seg([{ v: true, label: T('yes') }, { v: false, label: T('no') }], a[tf] === 'tail' ? true : (a[tf] ? false : null), function (v) {
            app.cardEdit(tf, T('editQ', { q: T('tailQ'), v: v === null ? '—' : v ? T('yes') : T('no') }), function (n) { if (v === null) delete n.card.answers[tf]; else n.card.answers[tf] = v ? 'tail' : 'normal'; });
          }, { cls: 'small' })) : null,
        btn('✕', function () {
          if (app.night.trades.some(function (t) { return t.zoneId === z.id && (t.flags || []).indexOf('paper') < 0; })) { app.toast(T('zoneHasTrades')); return; }
          app.cardEdit(z.type, T('delZone', { z: z.id }), function (n) { n.card.zones = n.card.zones.filter(function (q) { return q.id !== z.id; }); }); }, 'ghost small', { 'aria-label': T('remove') }));
      zbox.appendChild(row);
    });
    if (!res.zones.length) zbox.appendChild(h('p', { class: 'muted', text: T('noZones') }));
    var zcount = res.zones.length;
    var src = J.prevCardSource(app.state, app.key);
    var copyRow = src ? h('div', { class: 'row copyrow' },
      btn(T('copyPrev', { key: src }), function () {
        app.cardEdit('copyPrev', T('copyPrevEdit', { key: src }), function (n) {
          var det = J.copyFromPrevDetail(n, app.state.nights[src]);
          app.toast(det.n ? T('copyPrevDone', { list: det.items.join(' · ') }) : T('copyPrevNone'));
        });
      }, 'ghost small', { 'data-testid': 'copy-prev' })) : null;
    el.appendChild(section(T('t1Title4', { n: zcount }), [copyRow, addRow, zbox, zcount > 0 && zcount < R.T.zonesMin ? banner(T('zonesFew'), 'warn') : null, full ? banner(T('zonesFull'), 'info') : null],
      { help: { text: T('t1ZoneHelp'), ref: 'xep-hang-vung' } }));

    // ----- ghi chú kế hoạch (một ô, gập) + chốt -----
    // cảnh báo kế hoạch ngược bias hiện NGAY khi gõ, nằm sát nút chốt (USER-TEST-2 mục 5)
    var noteOld = [card.plan1, card.plan2, card.cancelWhen].filter(Boolean).join('\n');
    var noteTxt = card.planNote !== undefined ? card.planNote : noteOld;
    var planTxt = { plan1: noteTxt, plan2: '' };
    var conflictBox = h('div', { class: 'conflictslot', 'data-testid': 'plan-conflict-slot' });
    function paintConflict() {
      ui.clear(conflictBox);
      if (J.planConflict(planTxt, app.res.bias)) conflictBox.appendChild(h('div', { class: 'banner warn strong', role: 'alert', 'data-testid': 'plan-conflict', text: T('planConflict', { b: ui.biasText(app.res.bias) }) }));
    }
    var ta = h('textarea', { class: 'field txt plannote', rows: '3', maxlength: '600', 'aria-label': T('planNote'), 'data-testid': 'plan-note', placeholder: T('planNotePh'), value: noteTxt,
      oninput: function (e) { planTxt.plan1 = e.target.value; paintConflict(); },
      onchange: function (e) { var v = e.target.value; app.hold(function () { app.update(function (n) { n.card.planNote = v; }, { keep: true }); }); } });
    var notes = h('details', { class: 'fold plans', open: noteTxt ? true : null }, h('summary', { text: T('addNote') }), h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('planNote') }), ta));
    var chk = J.canLockCard(card);
    var lockBox = h('div', { class: 'lockbox' });
    lockBox.appendChild(conflictBox);
    paintConflict();
    if (!card.lockedAt) {
      lockBox.appendChild(btn(T('lockCard'), function () {
        if (J.planConflict(planTxt, app.res.bias)) app.toast(T('planConflictToast'));
        app.update(function (n) { J.lockCard(n, app.nowMs); });
        app.toast(T('locked'));
        app.go(2);
      }, 'primary big', { disabled: chk.ok ? null : true, 'data-testid': 'lock-card' }));
      if (!chk.ok) lockBox.appendChild(h('span', { class: 'muted', text: T('lockNeed', { list: chk.missing.map(function (m) { return T('need_' + m); }).join(', ') }) }));
      lockBox.appendChild(h('p', { class: 'muted', text: T('lockWhy') }));
    } else {
      lockBox.appendChild(chip(T('cardLocked', { hm: card.lockedAt }), 'good'));
      lockBox.appendChild(btn(T('toTier2'), function () { app.go(2); }, 'primary'));
      lockBox.appendChild(h('span', { class: 'muted', text: T('editAfterLock') }));
    }
    el.appendChild(section(T('t1Title5'), [notes, lockBox], { help: { text: T('t1CardHelp'), ref: 'the-phien' } }));
    return el;
  }
  // VWAP tuần: giá hiện tại so với VWAP tuần ⇒ Trên / Dưới / Sát (±2 giá)
  function vwapSide(now, vw) { var d = now - vw; return Math.abs(d) <= R.T.vwapNear + R.EPS ? 'near' : d > 0 ? 'above' : 'below'; }
  function setVwapNums(app, field, v) {
    app.cardEdit('vwapW', T('editQ', { q: T('vwapQ'), v: '' + (v === null ? '—' : J.fmt(v)) }), function (n) {
      var a = n.card.answers;
      if (v === null) delete a[field]; else a[field] = v;
      if (typeof a.priceNow === 'number' && typeof a.vwapPrice === 'number') a.vwapW = vwapSide(a.priceNow, a.vwapPrice);
    });
  }
  function zoneOf(n, id) { return n.card.zones.filter(function (z) { return z.id === id; })[0]; }

  // ================= TẦNG 2 =================
  function tier2(app) {
    var night = app.night, rg = night.regime, bo = rg.breakout, res = app.res;
    var el = h('div', { class: 'tier', 'data-tier': '2' });
    el.appendChild(lead(T('t2Lead')));

    var modes = [
      { v: 'balanced', label: C.modeLabels.balanced, sub: T('modeBalancedSub') },
      { v: 'broken', label: C.modeLabels.broken, sub: T('modeBrokenSub') },
      { v: 'thin', label: C.modeLabels.thin, sub: T('modeThinSub') }
    ];
    var modeSeg = seg(modes, rg.mode, function (v) {
      if (!v) return;
      app.update(function (n) {
        J.setRegimeMode(n, v, app.nowMs);
      });
    }, { cls: 'big', noToggle: true, label: T('t2Mode') });
    var body = [modeSeg];

    if (rg.mode === 'thin') {
      body.push(h('div', { class: 'ctl', 'data-ctl': 'thinDir' }, h('div', { class: 'ctl-label', text: T('thinDir') }),
        seg([{ v: 'up', label: T('thinUp') }, { v: 'down', label: T('thinDown') }], rg.thinDir || null, function (v) { app.update(function (n) { n.regime.thinDir = v; }); }, { noToggle: true })));
      if (!rg.thinDir) body.push(banner(T('thinDirNeed'), 'warn'));
    }
    if (rg.mode === 'broken') {
      var zoneOpts = res.zones.map(function (z) { return { v: z.id, label: z.id + ' · ' + ui.zoneLabel(z) }; });
      // đổi hướng / cạnh sau khi đã công nhận = cú phá khác: công nhận lại từ bước 1 (REVIEW-3 mục 2)
      var setBo = function (field, v) {
        var reset = false;
        app.update(function (n) { reset = J.setBreakoutField(n, field, v, app.nowMs); });
        if (reset) app.toast(T('boReset'));
      };
      var atBase = time.baseMinute(bo.at || '');
      if (!bo.dir || !bo.edgeZoneId || !bo.step1 || !bo.step2) body.push(banner(T('boNeedTop'), 'warn'));
      body.push(h('div', { class: 'panel inner' },
        h('div', { class: 'ctl', 'data-ctl': 'boDir' }, h('div', { class: 'ctl-label', text: T('boDir') }),
          seg([{ v: 'up', label: T('breakUp') }, { v: 'down', label: T('breakDown') }], bo.dir || null, function (v) { setBo('dir', v); }, { noToggle: true })),
        h('div', { class: 'ctl', 'data-ctl': 'boEdge' }, h('div', { class: 'ctl-label' }, h('span', { text: T('boEdge') }), ui.helpBtn({ text: T('boEdgeHelp'), ref: 'acceptance' })),
          zoneOpts.length ? seg(zoneOpts, bo.edgeZoneId || null, function (v) { setBo('edgeZoneId', v); }, { noToggle: true, cls: 'wrap' }) : h('span', { class: 'muted', text: T('noZones') })),
        h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('boAt') }),
          textInput(bo.at || '', function (v) { app.update(function (n) { n.regime.breakout.at = v; }); }, { max: 5, placeholder: T('timePh') }),
          chip(T('boNth', { n: bo.nth || 1 }), ''), (bo.nth || 1) === 1 ? h('span', { class: 'muted', text: T('boNthHint') }) : null,
          h('div', { class: 'muted boathint', text: T('boAtHint') }),
          atBase !== null && atBase < 18 * 60 ? banner(T('boAtOutside', { hm: bo.at }), 'warn') : null),
        h('div', { class: 'ctl', 'data-ctl': 'boStep1' }, h('div', { class: 'ctl-label' }, h('span', { text: T('boStep1') }), ui.helpBtn({ text: T('acceptHelp'), ref: 'acceptance' })),
          seg([{ v: true, label: T('yes') }, { v: false, label: T('notYet') }], !!bo.step1, function (v) { app.update(function (n) { n.regime.breakout.step1 = !!v; if (!v) n.regime.breakout.step2 = false; }); },
            { noToggle: true, disabled: bo.dir && bo.edgeZoneId ? null : { true: T('needDirEdge') }, onDisabled: function (v, why) { app.toast(why); } })),
        h('div', { class: 'ctl', 'data-ctl': 'boStep2' }, h('div', { class: 'ctl-label', text: T('boStep2') }),
          seg([{ v: true, label: T('yes') }, { v: false, label: T('notYet') }], !!bo.step2, function (v) { app.update(function (n) { n.regime.breakout.step2 = !!v; }); }, { noToggle: true, disabled: bo.step1 ? null : { true: T('needStep1') }, onDisabled: function (v, why) { app.toast(why); } })),
        btn(T('boFailed'), function () { app.update(function (n) { J.breakoutFailed(n, app.nowMs); }); }, 'ghost', { 'data-testid': 'bo-failed' })));
    }
    var eff = res.regime.effective;
    body.push(h('div', { class: 'effline' }, h('span', { class: 'ctl-label', text: T('effective') }),
      h('span', { class: 'bigchip ' + (eff === 'broken' ? 'good' : eff === 'pending' ? 'warn' : ''), 'data-testid': 'regime-eff', text: C.modes[eff] + (res.regime.dir ? ' · ' + (res.regime.dir === 'up' ? T('dirUp') : T('dirDown')) : '') })));
    el.appendChild(section(T('t2Title1'), body, { help: { text: T('t2ModeHelp'), ref: 'acceptance' } }));

    // nến dài nhất phiên
    var until = rg.longestBarUntil;
    var active = until && app.nowMs < until;
    el.appendChild(section(T('t2Title2'), [
      h('div', { class: 'row' },
        btn(T('longestBar'), function () { app.update(function (n) { n.regime.longestBarUntil = time.longestBarUntil(app.nowMs); }); }, 'danger', { 'data-testid': 'longest-bar' }),
        active ? chip(T('reopenAt', { hm: J.hm(until) }), 'bad') : null,
        active ? btn(T('clearLongest'), function () { app.update(function (n) { n.regime.longestBarUntil = null; }); }, 'ghost small') : null),
      h('p', { class: 'muted', text: T('longestHint') })
    ], { help: { text: T('t2LongestHelp'), ref: 'xung-dot' } }));

    // bảng bật kịch bản
    var tbl = h('div', { class: 'scen-table', role: 'table' });
    R.SCENARIOS.forEach(function (s) {
      var code = res.enabled[s], sc = C.scenarios[s];
      tbl.appendChild(h('div', { class: 'srow ' + (code ? 'off' : 'on'), role: 'row', 'data-scen': s },
        h('span', { class: 'sname' }, h('b', { text: s }), ' ', sc.name),
        code ? h('span', { class: 'sstat bad', text: '✖ ' + ui.codeText(code) }) : h('span', { class: 'sstat good', text: '✔ ' + T('enabled') })));
    });
    var tbox = [tbl];
    if (res.warnings.indexOf('WARN_BEFORE_2030') >= 0) tbox.push(h('div', { class: 'banner warn', 'data-testid': 'warn-2030' }, h('span', { text: ui.fillTimes(C.warnText.WARN_BEFORE_2030) + ' ' }), ui.qd19Help()));
    if (res.warnings.indexOf('WARN_NYSE') >= 0) tbox.push(banner(C.warnText.WARN_NYSE, 'warn'));
    tbox.push(h('p', { class: 'muted', text: T('tableNote') }));
    el.appendChild(section(T('t2Title3'), tbox, { help: { text: T('t2TableHelp'), ref: 'xung-dot' } }));

    var can3 = !res.locks.tier3;
    el.appendChild(h('div', { class: 'actions' }, btn(T('toTier3'), function () { app.go(3); }, 'primary', { disabled: can3 ? null : true }),
      can3 ? null : h('span', { class: 'muted', text: T('lock_' + res.locks.tier3) })));
    return el;
  }

  ui.tier0 = { render: tier0 }; ui.tier1 = { render: tier1 }; ui.tier2 = { render: tier2 };
})(this);
