/* Trạm Đêm Vàng — tầng 0 (trước), tầng 1 (vùng + thẻ phiên), tầng 2 (chế độ). */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules, time = TDV.time;
  var T = ui.T, h = ui.h, seg = ui.seg, chip = ui.chip, btn = ui.btn, numInput = ui.numInput, textInput = ui.textInput, section = ui.section, banner = ui.banner;

  var YESNO = [{ v: true, label: T('yes') }, { v: false, label: T('no'), bad: true }];
  var SIDE_OPTS = [{ v: 'upper', label: T('sideUpperOpt') }, { v: 'lower', label: T('sideLowerOpt') }];

  function lead(text) { return h('p', { class: 'lead', text: text }); }

  // ================= TẦNG 0 =================
  function tier0(app) {
    var night = app.night, t0 = night.t0, key = app.key, useDst = app.useDst;
    var el = h('div', { class: 'tier', 'data-tier': '0' });
    el.appendChild(lead(T('t0Lead')));

    var q1 = h('div', { class: 'ctl', 'data-ctl': 't0alert' },
      h('div', { class: 'ctl-label' }, h('span', { text: T('t0Alert') })),
      seg(YESNO, t0.alert === null || t0.alert === undefined ? null : t0.alert, function (v) { app.update(function (n) { n.t0.alert = v; }); }));
    el.appendChild(section(T('t0Title1'), [q1, t0.alert === false ? banner(T('t0ViewOnly'), 'warn') : null]));

    // cửa sổ cấm
    var list = h('div', { class: 'windows' });
    R.effectiveWindows(t0, key).forEach(function (w) {
      var r = time.windowRange(w, key, useDst);
      var isDefault = w.id === 'w1930' || w.id === 'w2100';
      var label = T('windowLabel', { hm: time.fmtMin(r.center), before: w.minutesBefore || 0, after: w.minutesAfter || 0, rank: w.rank });
      var row = h('div', { class: 'wrow' + (w.on ? '' : ' off') },
        h('span', { class: 'wlabel', text: label + (w.kind === 'fomc' ? ' · FOMC' : '') }),
        w.offAt ? h('span', { class: 'muted', text: T('offAt', { hm: w.offAt }) }) : null,
        w.auto ? h('span', { class: 'muted', text: T('autoOn') }) : null,
        btn(w.on ? T('on') : T('off'), function () {
          if (w.on) {
            app.confirm({ title: T('offConfirmTitle'), text: T('offConfirmText', { hm: time.fmtMin(r.center) }), ok: T('offConfirmOk'), danger: true }).then(function (ok) {
              if (ok) app.update(function (n) { var x = n.t0.windows.filter(function (z) { return z.id === w.id; })[0]; x.on = false; x.offAt = J.hm(app.nowMs); });
            });
          } else app.update(function (n) { var x = n.t0.windows.filter(function (z) { return z.id === w.id; })[0]; x.on = true; delete x.offAt; });
        }, 'sw ' + (w.on ? 'on' : 'off')),
        isDefault ? null : btn('✕', function () { app.update(function (n) { n.t0.windows = n.t0.windows.filter(function (z) { return z.id !== w.id; }); }); }, 'ghost small', { 'aria-label': T('remove') }));
      list.appendChild(row);
    });
    var nyse = time.windowRange(R.NYSE_WARN, key, useDst);
    list.appendChild(h('div', { class: 'wrow warnrow' }, h('span', { class: 'wlabel', text: T('nyseRow', { hm: time.fmtMin(nyse.center) }) }), chip(T('alwaysOn'), 'warn')));

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
      btn(T('addFomc'), function () {
        app.update(function (n) { n.t0.windows.push({ id: 'fomc' + Date.now().toString(36), kind: 'fomc', rank: 2, at: '01:00', tz: 'ET', minutesBefore: 0, minutesAfter: 30, on: true }); });
      }, 'ghost'));
    el.appendChild(section(T('t0Title2'), [list, form, banner(T('t0WinNote', { a: time.fmtMin(time.markMin({ at: '19:30', tz: 'ET' }, key, useDst)), b: time.fmtMin(time.markMin({ at: '21:00', tz: 'ET' }, key, useDst)) }), 'info')], { help: { text: T('t0WinHelp'), ref: 'xung-dot' } }));

    el.appendChild(section(T('t0Title3'), [
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('newsDay') }),
        seg(YESNO.map(function (o) { return { v: o.v, label: o.label }; }), !!t0.newsDay, function (v) { app.update(function (n) { n.t0.newsDay = !!v; }); }, { noToggle: true })),
      h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('t0Note') }),
        textInput(t0.note, function (v) { app.update(function (n) { n.t0.note = v; }, { keep: true }); }, { placeholder: T('t0NotePh'), max: 160 }))
    ]));

    el.appendChild(h('div', { class: 'actions' }, btn(T('t0Done'), function () { app.update(function (n) { n.t0.touched = true; }); app.go(1); }, 'primary')));
    return el;
  }

  // ================= TẦNG 1 =================
  function tier1(app) {
    var night = app.night, card = night.card, a = card.answers, res = app.res;
    var el = h('div', { class: 'tier', 'data-tier': '1' });
    el.appendChild(lead(T('t1Lead')));

    // 1a — kẻ trên chart
    var drawn = card.drawn || {};
    var list = h('ul', { class: 'ticks' });
    C.drawItems.forEach(function (txt, i) {
      var id = 'draw' + i;
      list.appendChild(h('li', {}, h('label', { class: 'tick', for: id }, h('input', { type: 'checkbox', id: id, checked: drawn[i] ? true : null,
        onchange: function (e) { app.update(function (n) { n.card.drawn = n.card.drawn || {}; n.card.drawn[i] = e.target.checked; }, { keep: true }); } }), h('span', { text: txt }))));
    });
    el.appendChild(section(T('t1Title1'), list, { cls: 'collapsible' }));

    // 1b — sáu câu hỏi
    var qbox = h('div', { class: 'qgrid' });
    C.questions.forEach(function (q, qi) {
      qbox.appendChild(h('div', { class: 'ctl', 'data-ctl': q.id },
        h('div', { class: 'ctl-label' }, h('span', { text: T('qPrefix', { n: q.num, label: q.label }) }), ui.helpBtn(q.help)),
        seg(q.options, a[q.id] === undefined ? null : a[q.id], function (v) {
          var lbl = v ? q.options.filter(function (o) { return o.v === v; })[0].label : '—';
          app.cardEdit(q.id, T('editQ', { q: q.label, v: lbl }), function (n) { if (v === null) delete n.card.answers[q.id]; else n.card.answers[q.id] = v; });
        })));
    });
    el.appendChild(section(T('t1Title2'), qbox));

    // 1c — bias
    var vw = h('div', { class: 'ctl', 'data-ctl': 'vwapW' },
      h('div', { class: 'ctl-label' }, h('span', { text: T('vwapQ') }), ui.helpBtn({ text: T('vwapHelp'), ref: 'ma-tran-bias' })),
      seg(C.vwapOpts, a.vwapW || null, function (v) {
        var lbl = v ? C.vwapOpts.filter(function (o) { return o.v === v; })[0].label : '—';
        app.cardEdit('vwapW', T('editQ', { q: T('vwapQ'), v: lbl }), function (n) { if (v === null) delete n.card.answers.vwapW; else n.card.answers.vwapW = v; });
      }));
    var vwapNums = h('div', { class: 'row wrap vwapnums' },
      h('label', { class: 'mini-l' }, T('vwapNowL'), numInput(a.priceNow === undefined ? null : a.priceNow, function () {}, { id: 'pricenow', label: T('vwapNowL'), onCommit: function (v) { setVwapNums(app, 'priceNow', v); } })),
      h('label', { class: 'mini-l' }, T('vwapPriceL'), numInput(a.vwapPrice === undefined ? null : a.vwapPrice, function () {}, { id: 'vwapprice', label: T('vwapPriceL'), onCommit: function (v) { setVwapNums(app, 'vwapPrice', v); } })),
      h('span', { class: 'muted', text: (typeof a.priceNow === 'number' && typeof a.vwapPrice === 'number') ? T('vwapAutoHint', { v: C.vwapOpts.filter(function (o) { return o.v === vwapSide(a.priceNow, a.vwapPrice); })[0].label }) : T('vwapAutoNeed') }));
    vw.appendChild(vwapNums);
    var biasBox = [vw];
    if (a.vwapW === 'near') {
      biasBox.push(h('div', { class: 'ctl', 'data-ctl': 'recheck' },
        h('div', { class: 'ctl-label', text: T('recheck') }),
        seg([{ v: 'above', label: T('rcAbove') }, { v: 'below', label: T('rcBelow') }], card.bias.rechecked || null, function (v) {
          app.cardEdit('bias', T('editRecheck'), function (n) { if (v === null) delete n.card.bias.rechecked; else n.card.bias.rechecked = v; });
        })));
    }
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
    el.appendChild(section(T('t1Title3'), biasBox, { help: { text: T('t1BiasHelp'), ref: 'ma-tran-bias' } }));

    // 1d — vùng
    var zbox = h('div', { class: 'zones' });
    res.zones.forEach(function (z) {
      var tdef = R.ZONE_TYPES[z.type] || {};
      var flags = z.flags.map(function (f) { return chip(C.flagText[f] || f, 'mini'); });
      var row = h('div', { class: 'zrow', 'data-zone': z.id },
        h('span', { class: 'zid', text: z.id }),
        h('span', { class: 'zname', text: C.zoneTypes[z.type] ? C.zoneTypes[z.type].label : z.type }),
        numInput(z.price, function () {}, { label: T('price'), onCommit: function (v) { app.cardEdit(z.type, T('editZone', { z: z.id }), function (n) { zoneOf(n, z.id).price = v; }); } }),
        numInput(z.priceTo === undefined ? null : z.priceTo, function () {}, { label: T('priceTo'), placeholder: T('priceTo'), onCommit: function (v) { app.cardEdit(z.type, T('editZone', { z: z.id }), function (n) { var zz = zoneOf(n, z.id); if (v === null) delete zz.priceTo; else zz.priceTo = v; }); } }),
        tdef.needSide ? seg(SIDE_OPTS, z.side || null, function (v) { app.cardEdit(z.type, T('editZone', { z: z.id }), function (n) { zoneOf(n, z.id).side = v; }); }, { cls: 'small', noToggle: true }) : null,
        h('span', { class: 'zflags' }, flags),
        btn('✕', function () {
          if (app.night.trades.some(function (t) { return t.zoneId === z.id && (t.flags || []).indexOf('paper') < 0; })) { app.toast(T('zoneHasTrades')); return; }
          app.cardEdit(z.type, T('delZone', { z: z.id }), function (n) { n.card.zones = n.card.zones.filter(function (q) { return q.id !== z.id; }); }); }, 'ghost small', { 'aria-label': T('remove') }));
      zbox.appendChild(row);
    });
    if (!res.zones.length) zbox.appendChild(h('p', { class: 'muted', text: T('noZones') }));

    var zf = app.ui.zoneForm = app.ui.zoneForm || { type: 'vwapW', price: null, priceTo: null, side: 'upper', note: '' };
    var needSide = (R.ZONE_TYPES[zf.type] || {}).needSide;
    var sel = h('select', { class: 'field', 'aria-label': T('zoneType'), onchange: function (e) { zf.type = e.target.value; app.render({ keep: false }); } },
      R.ZONE_ORDER.map(function (t) { return h('option', { value: t, selected: zf.type === t ? true : null, text: C.zoneTypes[t].label + ' · ' + C.zoneTypes[t].rank }); }));
    var full = res.zones.length >= R.T.zonesMax;
    var addRow = h('div', { class: 'zform' }, sel,
      numInput(zf.price, function (v) { zf.price = v; }, { placeholder: T('price'), label: T('price'), id: 'zprice' }),
      numInput(zf.priceTo, function (v) { zf.priceTo = v; }, { placeholder: T('priceTo'), label: T('priceTo') }),
      needSide ? seg(SIDE_OPTS, zf.side, function (v) { zf.side = v || 'upper'; app.render({ keep: false }); }, { noToggle: true, cls: 'small' }) : null,
      btn(T('addZone'), function () {
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
      }, 'primary', { disabled: full ? true : null }));
    var zcount = res.zones.length;
    // sao chép VWAP tuần, HVN 3 tuần và Q1′ từ đêm trước cùng tuần (USER-TEST-2 mục 5)
    var src = J.prevCardSource(app.state, app.key);
    var copyRow = src ? h('div', { class: 'row copyrow' },
      btn(T('copyPrev', { key: src }), function () {
        app.cardEdit('copyPrev', T('copyPrevEdit', { key: src }), function (n) {
          var cnt = J.copyFromPrev(n, app.state.nights[src]);
          app.toast(cnt ? T('copyPrevDone', { n: cnt }) : T('copyPrevNone'));
        });
      }, 'ghost', { 'data-testid': 'copy-prev' }), h('span', { class: 'muted', text: T('copyPrevHint') })) : null;
    el.appendChild(section(T('t1Title4', { n: zcount }), [zbox, addRow, copyRow, zcount > 0 && zcount < R.T.zonesMin ? banner(T('zonesFew'), 'warn') : null, full ? banner(T('zonesFull'), 'info') : null],
      { help: { text: T('t1ZoneHelp'), ref: 'xep-hang-vung' } }));

    // 1e — kế hoạch + chốt
    // cảnh báo kế hoạch ngược bias hiện NGAY khi gõ, nằm sát nút chốt (USER-TEST-2 mục 5)
    var planTxt = { plan1: card.plan1 || '', plan2: card.plan2 || '' };
    var conflictBox = h('div', { class: 'conflictslot', 'data-testid': 'plan-conflict-slot' });
    function paintConflict() { 
      ui.clear(conflictBox);
      if (J.planConflict(planTxt, app.res.bias)) conflictBox.appendChild(h('div', { class: 'banner warn strong', role: 'alert', 'data-testid': 'plan-conflict', text: T('planConflict', { b: ui.biasText(app.res.bias) }) }));
    }
    var plans = h('div', { class: 'plans' },
      planField(app, 'plan1', T('plan1'), function (v) { planTxt.plan1 = v; paintConflict(); }), planField(app, 'plan2', T('plan2'), function (v) { planTxt.plan2 = v; paintConflict(); }), planField(app, 'cancelWhen', T('cancelWhen')));
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
    el.appendChild(section(T('t1Title5'), [plans, lockBox], { help: { text: T('t1CardHelp'), ref: 'the-phien' } }));
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
  function planField(app, field, label, onTxt) {
    return h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: label }),
      textInput(app.night.card[field] || '', function (v) { app.update(function (n) { n.card[field] = v; }, { keep: true }); }, { max: 200, label: label, onInput: onTxt }));
  }

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
      if (!bo.dir || !bo.edgeZoneId || !bo.step1 || !bo.step2) body.push(banner(T('boNeedTop'), 'warn'));
      body.push(h('div', { class: 'panel inner' },
        h('div', { class: 'ctl', 'data-ctl': 'boDir' }, h('div', { class: 'ctl-label', text: T('boDir') }),
          seg([{ v: 'up', label: T('breakUp') }, { v: 'down', label: T('breakDown') }], bo.dir || null, function (v) { app.update(function (n) { n.regime.breakout.dir = v; }); }, { noToggle: true })),
        h('div', { class: 'ctl', 'data-ctl': 'boEdge' }, h('div', { class: 'ctl-label' }, h('span', { text: T('boEdge') }), ui.helpBtn({ text: T('boEdgeHelp'), ref: 'acceptance' })),
          zoneOpts.length ? seg(zoneOpts, bo.edgeZoneId || null, function (v) { app.update(function (n) { n.regime.breakout.edgeZoneId = v; }); }, { noToggle: true, cls: 'wrap' }) : h('span', { class: 'muted', text: T('noZones') })),
        h('div', { class: 'ctl' }, h('div', { class: 'ctl-label', text: T('boAt') }),
          textInput(bo.at || '', function (v) { app.update(function (n) { n.regime.breakout.at = v; }); }, { max: 5, placeholder: T('timePh') }),
          chip(T('boNth', { n: bo.nth || 1 }), ''), (bo.nth || 1) === 1 ? h('span', { class: 'muted', text: T('boNthHint') }) : null),
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
