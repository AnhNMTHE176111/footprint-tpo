/* Trạm Đêm Vàng — thanh trạng thái (luôn thấy) + thẻ phiên (cột phải). */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules, time = TDV.time, N = TDV.news;
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
    var next = time.nextWindow(R.effectiveWindows(night.t0, key, app.news), app.nowMin, key, useDst);
    var bar = h('div', { class: 'statusbar' + (hit ? ' bad' : warn ? ' warn' : '') });
    // điện thoại: hàng đầu chỉ có giờ, bias và nút "Trạng thái"; mọi chip còn lại nằm trong khung mở xuống (USER-TEST-3 d1).
    // Máy tính: hai khung này là display: contents nên bố cục như cũ.
    var top = h('div', { class: 'sbmain' }), more = h('div', { class: 'sbmore' });
    var open = !!app.ui.statusOpen;
    var wrap = h('div', { class: 'statuswrap' + (open ? ' open' : '') }, bar);
    top.appendChild(h('strong', { class: 'clock', 'data-testid': 'clock', text: T('clock', { hm: J.hm(app.nowMs) }) }));
    top.appendChild(chip(T('biasChip', { v: ui.biasText(res.bias) }), 'bias ' + ui.dirCls(res.bias)));
    top.appendChild(h('button', { type: 'button', class: 'btn small ghost sbtoggle', 'data-testid': 'status-toggle', 'aria-expanded': open ? 'true' : 'false', text: T('statusToggle') + ' ▾',
      onclick: function (e) { e.stopPropagation(); app.ui.statusOpen = !app.ui.statusOpen; wrap.classList.toggle('open', app.ui.statusOpen); e.currentTarget.setAttribute('aria-expanded', app.ui.statusOpen ? 'true' : 'false'); } }));
    bar.appendChild(top); bar.appendChild(more);
    bar = more;
    // 20:20–20:30: dải "đáng tin" bắt đầu nhưng cảnh báo trước 20:30 còn hiệu lực ⇒ không in hai điều ngược nhau (REVIEW-2 mục 11)
    var early = res.warnings.indexOf('WARN_BEFORE_2030') >= 0;
    bar.appendChild(h('span', { class: 'phase', text: C.phases[phase.id] + (band && !(early && band.id === 'real') ? ' · ' + C.bands[band.id] : '') }));
    if (hit) {
      var r = time.windowRange(hit, key, useDst);
      bar.appendChild(chip(T('inWindow', { hm: time.fmtMin(r.center), left: Math.max(0, Math.ceil(r.to - app.nowMin)) }), 'bad'));
    } else if (res.warnings.indexOf('WARN_NYSE') >= 0) {
      bar.appendChild(chip(C.warnText.WARN_NYSE, 'warn'));
    } else if (res.fxNews) {
      bar.appendChild(chip(T('fxChip', { ccy: res.fxNews.country, hm: time.fmtMin(res.fxNews.center) }), 'warn'));
    } else if (app.news && app.news.status === 'ok' && N.nextEvent(app.news, app.nowMin)) {
      var ne = N.nextEvent(app.news, app.nowMin);
      bar.appendChild(chip(T('newsChip', { hm: ne.hm, name: ne.title, min: Math.ceil(ne.nightMin - app.nowMin) }), '', null));
    } else if (next) {
      var rr = time.windowRange(next.w, key, useDst);
      bar.appendChild(chip(T('nextWindow', { hm: time.fmtMin(rr.center), min: Math.ceil(next.startsIn) }), ''));
    } else {
      bar.appendChild(chip(T('noWindow'), ''));
    }
    if (app.news && app.news.fetchedAt) bar.appendChild(chip(T('newsAgeChip', { hm: J.hm(Date.parse(app.news.fetchedAt)) }), 'zero'));
    // chữ ngắn trên thanh; câu đầy đủ nằm trong "?" (REVIEW-2 mục 12, mục 10)
    if (early && !hit) { bar.appendChild(chip(T('warnShort'), 'warn')); bar.appendChild(ui.qd19Help()); }

    var rb = res.counts.ruleBreaks, ss = res.counts.slStreak;
    bar.appendChild(chip(T('chipBreaks', { n: rb }), rb >= 2 ? 'bad' : rb ? 'warn' : 'zero', T('chipBreaksTip')));
    bar.appendChild(chip(T('chipStreak', { n: ss }), ss >= 3 ? 'bad' : ss ? 'warn' : 'zero', T('chipStreakTip')));
    var paper = res.open && res.open.trade && res.open.trade.flags.indexOf('paper') >= 0;
    bar.appendChild(chip(T(paper ? 'chipOpenPaper' : 'chipOpen', { n: res.open ? 1 : 0 }), res.open ? 'warn' : 'zero', T('chipOpenTip')));
    if (res.zone && res.counts.zoneN > 0) bar.appendChild(chip(T('chipZone', { n: res.counts.zoneN }), res.counts.zoneN >= 2 ? 'bad' : 'zero', T('chipZoneTip')));
    // giờ mùa đông Mỹ: mỗi đêm chỉ một chip ngắn, câu đầy đủ trong "?"; dòng dài chỉ hiện đúng ngày đổi giờ (REVIEW-3 mục 13)
    var notes = time.notices(key, useDst);
    if (notes.some(function (n) { return n.id === 'US_WINTER'; })) { bar.appendChild(chip(T('winterChip'), 'warn')); bar.appendChild(ui.helpBtn({ text: C.notices.US_WINTER, ref: 'thoi-gian' })); }

    bar.appendChild(h('button', { type: 'button', class: 'btn small ghost glossary-btn', 'data-testid': 'glossary-btn', text: T('glossaryBtn'), onclick: function () { app.openGlossary(); } }));
    if (!app.news || app.news.status !== 'ok') wrap.appendChild(h('div', { class: 'notice bad', role: 'alert', 'data-testid': 'news-stale', text: T('newsStaleBar') }));
    notes.forEach(function (n) { if (n.id !== 'US_WINTER') wrap.appendChild(h('div', { class: 'notice', text: C.notices[n.id] })); });
    return wrap;
  }
  // bấm ra ngoài khung "Trạng thái" thì đóng lại (điện thoại)
  document.addEventListener('click', function (e) {
    var a = TDV.app;
    if (!a || !a.ui.statusOpen || (e.target.closest && e.target.closest('#status'))) return;
    a.ui.statusOpen = false;
    var w = document.querySelector('#status .statuswrap'); if (w) w.classList.remove('open');
    var t = document.querySelector('#status .sbtoggle'); if (t) t.setAttribute('aria-expanded', 'false');
  });

  function renderCard(app) {
    var res = app.res, night = app.night, card = night.card, a = card.answers || {};
    var p = time.parseKey(app.key);
    var root_ = h('div', { class: 'cardbox' });
    root_.appendChild(h('h3', { class: 'ptitle' }, h('span', { text: T('cardTitle') }), h('button', { type: 'button', class: 'cardclose', 'aria-label': T('close'), text: '✕', onclick: function () { app.toggleCard(false); } })));
    function row(label, value, cls) {
      return h('div', { class: 'crow' }, h('span', { class: 'clabel', text: label }), h('span', { class: 'cval' + (cls ? ' ' + cls : '') }, value));
    }
    root_.appendChild(row(T('cardDate'), time.pad(p.d) + '/' + time.pad(p.m) + '/' + p.y));
    if (a.vwapW) root_.appendChild(row(T('cardVwap'), C.vwapOpts.filter(function (o) { return o.v === a.vwapW; })[0].label));
    if (a.q5) root_.appendChild(row(T('cardClose'), optLabel('q5', a.q5)));
    if (a.q1) root_.appendChild(row(T('cardShape'), optLabel('q1', a.q1)));
    root_.appendChild(row(T('cardBias'), h('span', { class: 'cardbias ' + ui.dirCls(res.bias), 'data-testid': 'card-bias', text: ui.biasText(res.bias) + (res.biasOverridden ? ' ' + T('overridden') : '') })));
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
    // NỢ và VÙNG CẤM chỉ hiện khi có; nợ suy từ vùng single print / poor high-low / naked POC (Q3 cũ chỉ còn đọc từ dữ liệu cũ)
    if (debts.length) root_.appendChild(row(T('cardDebt'), debts.map(ui.zoneLabel).join(' · ')));
    else if (a.q3 && a.q3 !== 'none') root_.appendChild(row(T('cardDebt'), optLabel('q3', a.q3)));
    var banned = res.zones.filter(function (z) { return z.flags.indexOf('banned') >= 0; });
    if (banned.length) root_.appendChild(row(T('cardBanned'), banned.map(ui.zoneLabel).join(' · ')));
    if (night.t0.note) root_.appendChild(row(T('cardNote'), night.t0.note));
    if (card.planNote) root_.appendChild(row(T('cardPlanNote'), card.planNote));
    if (card.plan1) root_.appendChild(row(T('cardPlan1'), card.plan1));
    if (card.plan2) root_.appendChild(row(T('cardPlan2'), card.plan2));
    if (card.cancelWhen) root_.appendChild(row(T('cardCancel'), card.cancelWhen));
    root_.appendChild(h('div', { class: 'cfoot' },
      card.lockedAt ? chip(T('cardLocked', { hm: card.lockedAt }), 'good') : chip(T('cardNotLocked'), 'warn'),
      null));
    if (card.edits.length) root_.appendChild(h('details', { class: 'fold edits' }, h('summary', { text: T('editsOpen', { n: card.edits.length }) }),
      h('ul', { class: 'editlist' }, card.edits.map(function (e) { return h('li', { text: e.at + ' · ' + e.what }); }))));
    return root_;
  }

  ui.status = { render: renderStatus };
  ui.card = { render: renderCard, optLabel: optLabel };
})(this);
