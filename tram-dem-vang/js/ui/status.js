/* Trạm Đêm Vàng — thanh trạng thái (luôn thấy) + thẻ phiên (cột phải). */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules, time = TDV.time;
  var T = ui.T, h = ui.h, chip = ui.chip;

  function optLabel(qid, v) {
    var q = C.questions.filter(function (x) { return x.id === qid; })[0];
    var o = q && q.options.filter(function (x) { return x.v === v; })[0];
    return o ? o.label : '—';
  }

  function renderStatus(app) {
    var res = app.res, night = app.night, key = app.key, useDst = app.useDst;
    var hit = res.newsHit;
    var warn = res.warnings.indexOf('WARN_NYSE') >= 0 || res.warnings.indexOf('WARN_BEFORE_2030') >= 0;
    var phase = time.phaseAt(app.nowMin, key, useDst);
    var band = time.bandAt(app.nowMin, key, useDst);
    var next = time.nextWindow(R.effectiveWindows(night.t0, key), app.nowMin, key, useDst);
    var bar = h('div', { class: 'statusbar' + (hit ? ' bad' : warn ? ' warn' : '') });

    bar.appendChild(h('strong', { class: 'clock', 'data-testid': 'clock', text: T('clock', { hm: J.hm(app.nowMs) }) }));
    bar.appendChild(h('span', { class: 'phase', text: C.phases[phase.id] + (band ? ' · ' + C.bands[band.id] : '') }));
    if (hit) {
      var r = time.windowRange(hit, key, useDst);
      bar.appendChild(chip(T('inWindow', { hm: time.fmtMin(r.center), left: Math.max(0, Math.ceil(r.to - app.nowMin)) }), 'bad'));
    } else if (res.warnings.indexOf('WARN_NYSE') >= 0) {
      bar.appendChild(chip(C.warnText.WARN_NYSE, 'warn'));
    } else if (next) {
      var rr = time.windowRange(next.w, key, useDst);
      bar.appendChild(chip(T('nextWindow', { hm: time.fmtMin(rr.center), min: Math.ceil(next.startsIn) }), ''));
    } else {
      bar.appendChild(chip(T('noWindow'), ''));
    }
    if (res.warnings.indexOf('WARN_BEFORE_2030') >= 0 && !hit) bar.appendChild(chip(C.warnText.WARN_BEFORE_2030, 'warn'));

    bar.appendChild(chip(T('biasChip', { v: ui.biasText(res.bias) }), 'bias ' + (res.bias === 'BUY' ? 'good' : res.bias === 'SELL' ? 'bad' : 'warn')));
    var rb = res.counts.ruleBreaks, ss = res.counts.slStreak;
    bar.appendChild(chip(T('chipBreaks', { n: rb }), rb >= 2 ? 'bad' : rb ? 'warn' : ''));
    bar.appendChild(chip(T('chipStreak', { n: ss }), ss >= 3 ? 'bad' : ss ? 'warn' : ''));
    var paper = res.open && res.open.trade && res.open.trade.flags.indexOf('paper') >= 0;
    bar.appendChild(chip(T(paper ? 'chipOpenPaper' : 'chipOpen', { n: res.open ? 1 : 0 }), res.open ? 'warn' : ''));
    if (res.zone) bar.appendChild(chip(T('chipZone', { n: res.counts.zoneN }), res.counts.zoneN >= 2 ? 'bad' : ''));

    var wrap = h('div', { class: 'statuswrap' }, bar);
    var notes = time.notices(key, useDst);
    notes.forEach(function (n) { wrap.appendChild(h('div', { class: 'notice', text: C.notices[n.id] })); });
    return wrap;
  }

  function renderCard(app) {
    var res = app.res, night = app.night, card = night.card, a = card.answers || {};
    var p = time.parseKey(app.key);
    var root_ = h('div', { class: 'cardbox' });
    root_.appendChild(h('h3', { class: 'ptitle', text: T('cardTitle') }));
    function row(label, value, cls) {
      return h('div', { class: 'crow' }, h('span', { class: 'clabel', text: label }), h('span', { class: 'cval' + (cls ? ' ' + cls : '') }, value));
    }
    root_.appendChild(row(T('cardDate'), time.pad(p.d) + '/' + time.pad(p.m) + '/' + p.y));
    root_.appendChild(row(T('cardVwap'), a.vwapW ? C.vwapOpts.filter(function (o) { return o.v === a.vwapW; })[0].label : '—'));
    root_.appendChild(row(T('cardClose'), optLabel('q5', a.q5)));
    root_.appendChild(row(T('cardShape'), optLabel('q1', a.q1)));
    root_.appendChild(row(T('cardBias'), h('span', { class: 'cardbias ' + (res.bias === 'BUY' ? 'good' : res.bias === 'SELL' ? 'bad' : 'warn'), 'data-testid': 'card-bias', text: ui.biasText(res.bias) + (res.biasOverridden ? ' ' + T('overridden') : '') })));
    root_.appendChild(row(T('cardMode'), C.modes[res.regime.effective] + (res.regime.dir ? ' ' + (res.regime.dir === 'up' ? T('dirUp') : T('dirDown')) : '')));

    var zonesBox = h('div', { class: 'czones' });
    var zs = res.zones.filter(function (z) { return z.flags.indexOf('banned') < 0; });
    if (!zs.length) zonesBox.appendChild(h('span', { class: 'muted', text: T('cardNone') }));
    zs.forEach(function (z) {
      var flagChips = z.flags.map(function (f) { return chip(C.flagText[f] || f, 'mini'); });
      zonesBox.appendChild(h('div', { class: 'czone' }, h('span', { class: 'zid', text: z.id }), h('span', { text: ui.zoneLabel(z) }), flagChips));
    });
    root_.appendChild(h('div', { class: 'cblock' }, h('div', { class: 'clabel', text: T('cardZones') }), zonesBox));

    var debts = res.zones.filter(function (z) { return z.type === 'sp' || z.type === 'poorHigh' || z.type === 'poorLow' || z.type === 'nakedPoc'; });
    root_.appendChild(row(T('cardDebt'), debts.length ? debts.map(ui.zoneLabel).join(' · ') : (a.q3 ? optLabel('q3', a.q3) : '—')));
    var banned = res.zones.filter(function (z) { return z.flags.indexOf('banned') >= 0; });
    root_.appendChild(row(T('cardBanned'), banned.length ? banned.map(ui.zoneLabel).join(' · ') : '—'));
    if (night.t0.note) root_.appendChild(row(T('cardNote'), night.t0.note));
    if (card.plan1) root_.appendChild(row(T('cardPlan1'), card.plan1));
    if (card.plan2) root_.appendChild(row(T('cardPlan2'), card.plan2));
    if (card.cancelWhen) root_.appendChild(row(T('cardCancel'), card.cancelWhen));
    root_.appendChild(h('div', { class: 'cfoot' },
      card.lockedAt ? chip(T('cardLocked', { hm: card.lockedAt }), 'good') : chip(T('cardNotLocked'), 'warn'),
      card.edits.length ? chip(T('cardEdits', { n: card.edits.length }), 'warn', card.edits.map(function (e) { return e.at + ' ' + e.what; }).join('\n')) : null));
    return root_;
  }

  ui.status = { render: renderStatus };
  ui.card = { render: renderCard, optLabel: optLabel };
})(this);
