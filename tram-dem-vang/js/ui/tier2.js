/* Trạm Đêm Vàng — tầng 2 "Setup Entry": ô dùng chung + bốn khối A–D xếp dọc, luôn mở; thanh nhảy A·B·C·D dính đầu;
 * thanh ENTRY dính đáy. Không khóa gì: người dùng tự tick, máy chỉ chấm ô tự kiểm và đếm. */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules;
  var T = ui.T, h = ui.h, seg = ui.seg, chip = ui.chip, btn = ui.btn, numInput = ui.numInput, textInput = ui.textInput;

  var SIDE_OPTS = [{ v: 'buy', label: 'buy' }, { v: 'sell', label: 'sell' }];
  var TICK_GROUPS = ['ctx', 'chk', 'ent'];
  var AUTO_ROWS = ['slFloor', 'slCap', 'rr', 'size'];   // các ô tự kiểm nằm trong nhóm SL (zone2 nằm cạnh ô Vùng)

  function mark(ok) { return ok === true ? '✓' : ok === false ? '✕' : '…'; }
  function stateCls(ok) { return ok === true ? 'ok' : ok === false ? 'bad' : 'wait'; }

  function tier2(app) {
    var night = app.night, se = night.se, res0 = app.res;
    var el = h('div', { class: 'tier t2', 'data-tier': '2' });
    var refs = { blocks: {}, common: {}, jump: {} };

    function setBlock(scen, fn, keep) {
      app.update(function (n) { var bs = J.block(n, scen); fn(bs, n); J.touchBlock(n, scen); }, { keep: !!keep });
    }

    el.appendChild(h('p', { class: 'lead', text: T('t2Lead') }));

    // ----- ô dùng chung -----
    var biasLine = h('div', { class: 'biasline2', 'data-testid': 'bias-line' });
    var cmList = h('div', { class: 'cm-list' });
    C.common.forEach(function (c) {
      var row = h('div', { class: 'cm', 'data-item': 'common:' + c.id, 'data-common': c.id });
      var mk = h('span', { class: 'cm-mark', 'aria-hidden': 'true' });
      var why = h('span', { class: 'cm-why' });
      var extra = null;
      if (c.auto) {
        row.appendChild(mk); row.appendChild(h('span', { class: 'cm-label', text: c.label })); row.appendChild(h('span', { class: 'cm-auto', text: T('autoTag') }));
        if (c.id === 'open') extra = btn(T('openJournal'), function () { app.go(3); }, 'small', { 'data-testid': 'go-journal' });
        if (extra) row.appendChild(extra);
        row.appendChild(why);
      } else {
        var cb = h('input', { type: 'checkbox', checked: (se.common || {}).longest ? true : null, 'data-testid': 'tick-common-' + c.id, 'data-id': 'tick-common-' + c.id, 'aria-label': c.label,
          onchange: function (e) { var on = e.target.checked; app.update(function (n) { n.se.common = n.se.common || {}; if (on) n.se.common[c.id] = true; else delete n.se.common[c.id]; }, { keep: true }); } });
        row.classList.add('manual');
        row.appendChild(h('label', { class: 'tick36' }, cb, h('span', { class: 'tt', text: c.label })));
        if (c.help) row.appendChild(ui.helpBtn(c.help));
        row.appendChild(why);
      }
      refs.common[c.id] = { row: row, mark: mk, why: why };
      cmList.appendChild(row);
    });
    el.appendChild(h('section', { class: 'panel commonbox', 'data-testid': 'common' },
      h('h3', { class: 'ptitle' }, h('span', { text: T('commonTitle') }), ui.helpBtn({ text: T('commonHelp'), ref: 'ngat-mach' })), biasLine, cmList));

    // ----- thanh nhảy A · B · C · D (dính đầu) -----
    var jump = h('nav', { class: 'jumpbar', 'aria-label': T('jumpLabel'), 'data-testid': 'jumpbar' });
    R.SCENARIOS.forEach(function (s, i) {
      var b = h('button', { type: 'button', class: 'jbtn', 'data-jump': s, title: C.blocks[s].title + ' (' + (i + 1) + ')', onclick: function () { app.jumpTo(s); } },
        h('b', { class: 'jl', text: s }), h('span', { class: 'jn', text: C.blocks[s].title }), h('span', { class: 'jp', 'data-testid': 'jump-prog-' + s }));
      refs.jump[s] = b; jump.appendChild(b);
    });
    el.appendChild(jump);

    // ----- bốn khối -----
    R.SCENARIOS.forEach(function (s) { el.appendChild(blockSection(s)); });

    function blockSection(s) {
      var def = C.blocks[s], sc = C.scenarios[s], bs = (se.blocks || {})[s] || {}, ticks = bs.ticks || {};
      var sec = h('section', { class: 'blk', id: 'blk-' + s, 'data-block': s, 'data-testid': 'block-' + s });
      var r = refs.blocks[s] = {};
      // đầu khối: chữ cái, tên, mục tiêu, tiến độ, ảnh ca thật
      r.prog = h('span', { class: 'bprog', 'data-testid': 'prog-' + s });
      var thumb = h('button', { type: 'button', class: 'blk-thumbbtn', 'aria-label': T('scenImgOpen', { name: sc.name }), 'data-testid': 'thumb-' + s,
        onclick: function () {
          app.openModal(h('div', { class: 'dlg imgdlg' }, h('h3', { text: s + ' · ' + sc.name }), h('img', { class: 'scenimg full', src: sc.img, alt: T('scenImgAlt', { name: sc.name }) }),
            h('div', { class: 'actions' }, btn(T('close'), function () { app.closeModal(false); }, 'primary'))));
        } }, h('img', { class: 'blk-thumb', src: sc.img, alt: T('scenImgAlt', { name: sc.name }), loading: 'lazy' }));
      sec.appendChild(h('header', { class: 'blk-head' },
        h('div', { class: 'blk-title' }, h('span', { class: 'bletter', text: s }), h('div', { class: 'bt' }, h('h3', { text: def.title + ' — ' + def.target }), h('p', { class: 'muted', text: sc.blurb }),
          def.sizeNote ? h('p', { class: 'sizenote', text: def.sizeNote }) : null)),
        h('div', { class: 'blk-side' }, r.prog,
          btn(T('clearBlock'), function () { app.clearBlockTicks(s); }, 'ghost small', { 'data-testid': 'clear-' + s, title: 'N' })),
        thumb));

      // hướng + vùng
      var zopts = res0.zones.map(function (z) { return { v: z.id, label: z.id + ' · ' + ui.zoneLabel(z), sub: z.flags.map(function (f) { return C.flagText[f] || f; }).join(' · ') || null }; });
      r.zinfo = h('div', { class: 'zinfo2', 'data-item': s + ':zone2' });
      var pick = h('div', { class: 'blk-pick' },
        h('div', { class: 'ctl', 'data-item': s + ':side' }, h('div', { class: 'ctl-label', text: T('sideL') }),
          seg(SIDE_OPTS, bs.side || null, function (v) { setBlock(s, function (b) { if (v) b.side = v; else delete b.side; }, false); }, { cls: 'big2', label: T('sideL') })),
        h('div', { class: 'ctl', 'data-item': s + ':zone' }, h('div', { class: 'ctl-label' }, h('span', { text: T('zoneL') }), ui.helpBtn({ text: T('zoneHelp'), ref: 'xep-hang-vung' })),
          zopts.length ? seg(zopts, bs.zoneId || null, function (v) { setBlock(s, function (b) { if (v) b.zoneId = v; else delete b.zoneId; }, false); }, { cls: 'wrap', label: T('zoneL') })
            : h('span', { class: 'muted', text: T('noZones') + ' ' }, btn(T('goTier1'), function () { app.go(1); }, 'small')), r.zinfo));
      sec.appendChild(pick);

      // ô lý do ngược bias (chỉ hiện khi ngược bias)
      r.counter = h('div', { class: 'ctl counterbox', 'data-item': s + ':counter', hidden: true });
      r.counterChip = h('div', { class: 'counterwhy' });
      r.counter.appendChild(r.counterChip);
      r.counter.appendChild(textInput(bs.reason || '', function (v) { setBlock(s, function (b) { b.reason = v; }, true); }, { placeholder: T('counterPh'), label: T('counterPh'),
        onInput: function (v) { setBlock(s, function (b) { b.reason = v; }, true); } }));
      sec.appendChild(r.counter);

      // ba nhóm checkbox
      TICK_GROUPS.forEach(function (g) {
        var grp = h('div', { class: 'grp', 'data-group': g }, h('h4', { class: 'grp-title', text: C.groupTitles[g] }));
        def[g].forEach(function (it, i) { grp.appendChild(tickRow(s, g + (i + 1), it, ticks)); });
        sec.appendChild(grp);
      });

      // giá vào · SL · TP · biên độ nến
      var numRow = h('div', { class: 'ctl numgrp', 'data-item': s + ':nums' });
      r.tpIn = numInput(bs.tp === undefined ? null : bs.tp, function (v) { setBlock(s, function (b) { if (v === null) delete b.tp; else b.tp = v; }, true); }, { label: T('tpL'), placeholder: T('tpAuto'), id: 'tp-' + s });
      function numField(label, key, id, unit, extra) {
        var o = { label: label, id: id + '-' + s, placeholder: '0000,0', unit: unit || null };
        if (extra) Object.keys(extra).forEach(function (k) { o[k] = extra[k]; });
        return h('label', { class: 'mini-l' }, label, numInput(bs[key] === undefined ? null : bs[key], function (v) { setBlock(s, function (b) { if (v === null) delete b[key]; else b[key] = v; }, true); }, o));
      }
      numRow.appendChild(h('div', { class: 'ctl-label' }, h('span', { text: T('numsTitle') }), ui.helpBtn({ text: T('numsHelp'), ref: 'luat-sl' })));
      numRow.appendChild(h('div', { class: 'row wrap' }, numField(T('entryL'), 'entry', 'entry'), numField(T('slL'), 'sl', 'sl'),
        h('label', { class: 'mini-l' }, T('tpL'), r.tpIn), numField(T('c6L'), 'c6', 'c6', T('unitGia'), { placeholder: '0,0' })));
      r.calc = h('div', { class: 'calcslot', 'data-testid': 'calc-' + s });
      numRow.appendChild(r.calc);
      sec.appendChild(numRow);

      // SL: một ô tick vị trí + các ô tự kiểm
      var slg = h('div', { class: 'grp', 'data-group': 'sl' }, h('h4', { class: 'grp-title', text: C.groupTitles.sl }));
      def.sl.forEach(function (it, i) { slg.appendChild(tickRow(s, 'sl' + (i + 1), it, ticks)); });
      r.autos = h('div', { class: 'autos' });
      AUTO_ROWS.forEach(function (id) {
        var row = h('div', { class: 'auto', 'data-item': s + ':' + id, 'data-auto': id });
        r.autos.appendChild(row); r['auto_' + id] = row;
      });
      slg.appendChild(r.autos);
      sec.appendChild(slg);
      r.sec = sec;
      return sec;
    }

    function tickRow(s, id, it, ticks) {
      var cb = h('input', { type: 'checkbox', checked: ticks[id] ? true : null, 'data-testid': 'tick-' + s + '-' + id, 'data-id': 'tick-' + s + '-' + id, 'aria-label': ui.fillTimes(it.t),
        onchange: function (e) {
          var on = e.target.checked;
          setBlock(s, function (b) { if (on) b.ticks[id] = true; else delete b.ticks[id]; }, true);
        } });
      return h('div', { class: 'tickrow', 'data-item': s + ':' + id },
        h('label', { class: 'tick36' }, cb, h('span', { class: 'tt', text: ui.fillTimes(it.t) })), it.help ? ui.helpBtn(it.help) : null);
    }

    // ----- phần "sống": cập nhật tại chỗ, không dựng lại ô nhập -----
    function autoRow(row, a, bl, a2) {
      ui.clear(row);
      var ok = a ? a.ok : null;
      row.className = 'auto ' + stateCls(ok);
      row.appendChild(h('span', { class: 'cm-mark', 'aria-hidden': 'true', text: mark(ok) }));
      row.appendChild(h('span', { class: 'cm-label', text: C.itemLabels[row.getAttribute('data-auto')] }));
      row.appendChild(h('span', { class: 'cm-auto', text: T('autoTag') }));
      if (a && a.reason) {
        row.appendChild(h('span', { class: 'cm-why', text: ui.autoReason(a.reason, bl, a2) }));
        if (a.reason === 'size' || a.reason === 'noCapital') row.appendChild(btn(T('capChange'), function () { a2.openCapital(false); }, 'small', { 'data-testid': 'btn-capital' }));
      } else if (ok === null) row.appendChild(h('span', { class: 'cm-why muted', text: T('autoWait') }));
    }
    function fillLive(a2) {
      var res = a2.res;
      // bias
      ui.clear(biasLine);
      biasLine.appendChild(chip(T('biasChip', { v: ui.biasText(res.bias) }), 'bias ' + ui.dirCls(res.bias)));
      var bn = res.bias === 'KHÔNG' ? T('biasNoneNote') : res.bias === 'CHỜ' ? T('biasWaitNote') : res.bias ? null : T('biasUnknownNote');
      if (bn) biasLine.appendChild(h('span', { class: 'muted small', text: bn }));
      // ô chung
      res.common.forEach(function (c) {
        var rf = refs.common[c.id];
        rf.row.classList.toggle('ok', c.ok); rf.row.classList.toggle('bad', !c.ok);
        rf.mark.textContent = c.auto ? mark(c.ok) : '';
        rf.why.textContent = c.ok ? '' : ui.commonReason(c.reason, a2);
        var go = rf.row.querySelector('[data-testid="go-journal"]'); if (go) go.hidden = c.ok;
      });
      // bốn khối
      R.SCENARIOS.forEach(function (s) {
        var bl = res.blocks[s], r = refs.blocks[s];
        r.prog.textContent = bl.done + '/' + bl.total;
        r.sec.classList.toggle('complete', bl.complete);
        var jb = refs.jump[s]; jb.classList.toggle('complete', bl.complete);
        jb.querySelector('.jp').textContent = bl.done + '/' + bl.total;
        // vùng: cờ + lần thứ n (lần ≥ 3 đỏ)
        ui.clear(r.zinfo);
        if (bl.zone) {
          var z2 = bl.autoChecks.filter(function (x) { return x.id === 'zone2'; })[0];
          bl.zone.flags.forEach(function (f) { r.zinfo.appendChild(chip(C.flagText[f] || f, 'mini')); });
          r.zinfo.appendChild(chip(T('nthAt', { n: bl.nth }), z2 && z2.ok === false ? 'bad' : bl.nth === 2 ? 'warn' : ''));
          if (z2 && z2.ok === false) r.zinfo.appendChild(h('span', { class: 'cm-why', text: ui.autoReason('zone2', bl, a2) }));
        }
        // ngược bias
        r.counter.hidden = !bl.counter;
        r.counter.classList.toggle('bad', bl.counter && bl.autoChecks.some(function (x) { return x.id === 'counter' && !x.ok; }));
        ui.clear(r.counterChip);
        if (bl.counter) r.counterChip.appendChild(h('span', { class: 'cm-why', text: ui.autoReason('counter', bl, a2) }));
        // số + cỡ lệnh
        var cc = bl.calc;
        ui.clear(r.calc);
        r.tpIn.input.placeholder = cc.tpSuggested !== null ? J.fmt(cc.tpSuggested) : T('tpAuto');
        if (cc.numsOk && cc.slSideOk) {
          var line = h('div', { class: 'calcline' });
          line.appendChild(chip(T('calcSl', { v: J.fmt(cc.slDist) }), ''));
          line.appendChild(chip(T('calcRr', { v: J.fmtTrim(cc.rr) }), cc.rr >= R.T.rrMin - 1e-9 ? 'good' : 'bad'));
          if (cc.tpSuggested !== null) line.appendChild(chip(T('calcTpSug', { v: J.fmt(cc.tpSuggested) }), ''));
          var sizeTxt = cc.size === null ? T('sizeNoCfg') : cc.size === 0 ? T('sizeZero') : cc.sizeMinOne ? T('sizeMinOne', { usd: J.fmtTrim(cc.realUsd) }) : T('sizeN', { n: cc.size });
          line.appendChild(chip(T('sizeTitle') + ': ' + sizeTxt, bl.half ? 'warn' : ''));
          if (bl.half) line.appendChild(chip(T(cc.sizeMinOne ? 'halfNoteMin' : 'halfNote', { why: bl.halfs.map(function (x) { return ui.fillTimes(C.halfText[x]); }).join(', ') }), 'warn'));
          r.calc.appendChild(line);
        } else r.calc.appendChild(h('span', { class: 'muted small', text: T('calcNeed') }));
        // ô tự kiểm trong nhóm SL
        AUTO_ROWS.forEach(function (id) {
          var a = bl.autoChecks.filter(function (x) { return x.id === id; })[0];
          autoRow(r['auto_' + id], a, bl, a2);
        });
      });
    }
    fillLive(app);
    el._live = fillLive;
    return el;
  }

  // ===== thanh ENTRY dính đáy =====
  function verdictBar(app) {
    var res = app.res, e = res.entry;
    var bar = h('div', { class: 'vbar ' + (e ? 'v-entry' + (e.paper ? ' paper' : '') : 'v-wait'), 'data-verdict': e ? 'ENTRY' : 'WAIT', 'data-testid': 'verdict', role: 'status', 'aria-live': 'polite' });
    var main = h('div', { class: 'vmain' }), actions = h('div', { class: 'vact' }), notes = h('div', { class: 'vnotes' });
    var half = null;
    if (e) {
      var cc = e.calc;
      half = e.half ? e : null;
      var sizePart = cc.sizeMinOne ? T('sizeMinOne', { usd: J.fmtTrim(cc.realUsd) }) : (e.half ? T('sizeHalfShort') : T('sizeFull')) + (cc.size === null || cc.size === undefined ? '' : ' · ' + T('sizeN', { n: cc.size }));
      main.appendChild(h('div', { class: 'vtext entry', 'data-testid': 'entry-text' },
        h('span', { class: 'ebig', text: (e.paper ? T('entryView') : 'ENTRY') + ' ' + e.side.toUpperCase() + ' · ' + T('scenTag', { s: e.scen }) }),
        h('span', { class: 'erest', text: ' ' + J.fmt(cc.entry) + ' · SL ' + J.fmt(cc.sl) + ' (' + T('slGia', { v: J.fmt(cc.slDist) }) + ') · TP ' + J.fmt(cc.tpUsed) + ' · 1:' + J.fmtTrim(cc.rr) + ' · ' + sizePart })));
      if (e.paper) actions.appendChild(btn(T('paperBtn'), function () { app.writeTrade(e.scen, {}); }, 'primary big', { 'data-testid': 'btn-paper' }));
      else { var eb = btn(T('writeBtn'), function () { app.writeTrade(e.scen, {}); }, 'primary big', { 'data-testid': 'btn-entry', title: 'Enter' }); eb.appendChild(h('kbd', { class: 'keyhint', text: 'Enter' })); actions.appendChild(eb); }
    } else {
      var f = res.focus, bl = f ? res.blocks[f] : null;
      var fails = res.common.filter(function (x) { return !x.ok; });
      var list = h('span', { class: 'vlist' });
      if (!bl) {
        main.appendChild(h('div', { class: 'vtext' }, h('b', { text: T('vWait') }), ' — ', T('waitPick')));
      } else {
        var ids = bl.missing.slice(), extra = 0;
        var useCommon = !ids.length;
        var items = useCommon ? fails.map(function (x) { return { id: 'common:' + x.id, label: C.itemLabel(f, 'common:' + x.id) }; })
          : ids.map(function (id) { return { id: f + ':' + id, label: ui.fillTimes(C.itemLabel(f, id)) }; });
        extra = Math.max(0, items.length - 3);
        items.slice(0, 3).forEach(function (it, i) {
          list.appendChild(h('button', { type: 'button', class: 'vitem', 'data-item-ref': it.id, onclick: function () { app.focusItem(it.id); }, text: it.label }));
          if (i < Math.min(3, items.length) - 1) list.appendChild(document.createTextNode(' · '));
        });
        main.appendChild(h('div', { class: 'vtext', 'data-testid': 'wait-text' }, h('b', { text: T('vWait') }), ' — ',
          useCommon ? T('waitCommon', { s: f }) : T('waitBlock', { s: f }), ' ', list, extra ? h('span', { class: 'moremuted', text: ' ' + T('moreItems', { n: extra }) }) : null));
        half = bl.half ? { halfs: bl.halfs, calc: bl.calc } : null;
        var can = !!bl.side && bl.calc.numsOk;
        var nMiss = bl.missing.length + fails.length;
        actions.appendChild(btn(T('forceBtn', { n: nMiss }), function () { app.forceTrade(f); }, 'danger', { 'data-testid': 'btn-force', disabled: can ? null : true, title: can ? null : T('forceNeed') }));
      }
    }
    if (half) {
      notes.appendChild(chip(T(half.calc.sizeMinOne ? 'halfNoteMin' : 'halfNote', { why: half.halfs.map(function (x) { return ui.fillTimes(C.halfText[x]); }).join(', ') }), 'warn'));
      if (half.halfs.indexOf('BEFORE_2030') >= 0) notes.appendChild(ui.qd19Help());
    }
    if (res.warnings.indexOf('WARN_NYSE') >= 0) notes.appendChild(chip(C.warnText.WARN_NYSE, 'warn'));
    bar.appendChild(main); bar.appendChild(actions);
    return h('div', { class: 'vwrap' }, bar, notes.childNodes.length ? notes : null);
  }

  ui.tier2 = { render: tier2 };
  ui.verdict = { render: verdictBar };
})(this);
