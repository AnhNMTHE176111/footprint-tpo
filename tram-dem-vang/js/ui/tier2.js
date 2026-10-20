/* Trạm Đêm Vàng — tầng 2 "Setup Entry": ô dùng chung + bốn khối A–D xếp dọc (khối đang làm mở, khối khác thu gọn một dòng);
 * thanh nhảy A·B·C·D dính đầu; thanh ENTRY / kết quả lệnh dính đáy. Không khóa gì: người dùng tự tick, máy chỉ chấm ô tự kiểm và đếm. */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content, J = TDV.journal, R = TDV.rules;
  var T = ui.T, h = ui.h, seg = ui.seg, chip = ui.chip, btn = ui.btn, numInput = ui.numInput, textInput = ui.textInput;

  var SIDE_OPTS = [{ v: 'buy', label: 'buy' }, { v: 'sell', label: 'sell' }];
  var TICK_GROUPS = ['ctx', 'chk', 'ent'];
  function autoIds(s) { return s === 'A' ? ['bias', 'breakHours', 'near', 'slFloor', 'slCap', 'rr', 'size'] : ['bias', 'near', 'slFloor', 'slCap', 'rr', 'size']; }   // zone2 nằm cạnh ô Vùng

  function mark(ok) { return ok === true ? '✓' : ok === false ? '✕' : '…'; }
  function stateCls(ok) { return ok === true ? 'ok' : ok === false ? 'bad' : 'wait'; }
  function focusEl(sel) { var e = document.querySelector(sel); if (e) { try { e.focus(); if (e.select) e.select(); } catch (x) { /* bỏ qua */ } } }

  function tier2(app) {
    var night = app.night, se = night.se, res0 = app.res;
    var el = h('div', { class: 'tier t2', 'data-tier': '2' });
    var refs = { blocks: {}, common: {}, jump: {} };
    app.ui.blkOpen = app.ui.blkOpen || {};

    // hướng mặc định theo bias ở lần chạm đầu (trừ khối C: fade có thể cả hai chiều); noDefault khi chính là ô chọn hướng
    function setBlock(scen, fn, keep, noDefault) {
      app.update(function (n) {
        var bs = J.block(n, scen);
        if (!noDefault && !bs.side && scen !== 'C') { var b = app.res.bias; if (b === 'BUY' || b === 'SELL') bs.side = b.toLowerCase(); }
        fn(bs, n); J.touchBlock(n, scen);
      }, { keep: !!keep });
    }
    function isOpen(s) { var v = app.ui.blkOpen[s]; return v === undefined ? se.last === s : !!v; }
    function paintOpen(s) {
      var r = refs.blocks[s], on = isOpen(s);
      r.sec.classList.toggle('collapsed', !on); r.body.hidden = !on; r.toggle.setAttribute('aria-expanded', on ? 'true' : 'false');
    }
    // map {A:true,...}: mở / đóng các khối mà không dựng lại tầng
    el._setOpen = function (map, only) {
      R.SCENARIOS.forEach(function (s) { if (map[s] !== undefined) app.ui.blkOpen[s] = !!map[s]; else if (only) app.ui.blkOpen[s] = false; paintOpen(s); });
    };

    el.appendChild(h('p', { class: 'lead', text: T('t2Lead') }));

    // ----- ô dùng chung -----
    var biasLine = h('div', { class: 'biasline2', 'data-testid': 'bias-line' });
    var sum = h('div', { class: 'cm-sum', 'data-testid': 'common-sum' });
    var cmList = h('div', { class: 'cm-list' });
    var ctrls = h('div', { class: 'cm-ctrls' });
    C.common.forEach(function (c) {
      var row = h('div', { class: 'cm', 'data-item': 'common:' + c.id, 'data-common': c.id });
      var mk = h('span', { class: 'cm-mark', 'aria-hidden': 'true' });
      var why = h('span', { class: 'cm-why' });
      if (c.auto) {
        row.appendChild(mk); row.appendChild(h('span', { class: 'cm-label', text: c.label })); row.appendChild(h('span', { class: 'cm-auto', text: T('autoTag') }));
        if (c.id === 'open') row.appendChild(btn(T('openJournal'), function () { app.go(3); }, 'small', { 'data-testid': 'go-journal' }));
        row.appendChild(why);
        cmList.appendChild(row);
      } else {
        // nút "vừa có nến dài nhất phiên": mặc định tắt (đạt); bật thì 3 nến M1 tới không vào lệnh
        var cb = h('input', { type: 'checkbox', checked: (se.common || {}).justLongest ? true : null, 'data-testid': 'tick-common-' + c.id, 'data-id': 'tick-common-' + c.id, 'aria-label': c.tickLabel,
          onchange: function (e) { var on = e.target.checked; app.update(function (n) { n.se.common = n.se.common || {}; if (on) n.se.common.justLongest = true; else delete n.se.common.justLongest; }, { keep: true }); } });
        row.classList.add('manual');
        row.appendChild(h('label', { class: 'tick36' }, cb, h('span', { class: 'tt', text: c.tickLabel })));
        if (c.help) row.appendChild(ui.helpBtn(c.help));
        row.appendChild(why);
        ctrls.appendChild(row);
      }
      refs.common[c.id] = { row: row, mark: mk, why: why };
    });
    // biên độ nến M1 cao nhất 5 nến: nhập một lần cho cả đêm, đổi khi cần
    var c6In = numInput(se.c6 === undefined ? null : se.c6, function (v) { app.update(function (n) { if (v === null) delete n.se.c6; else n.se.c6 = v; }, { keep: true }); },
      { label: T('c6L'), id: 'c6', placeholder: '0,0', unit: T('unitGia') });
    ctrls.appendChild(h('div', { class: 'cm-c6' }, h('label', { class: 'mini-l' }, T('c6Night'), c6In), ui.helpBtn({ text: T('numsHelp'), ref: 'luat-sl' })));
    el.appendChild(h('section', { class: 'panel commonbox', 'data-testid': 'common' },
      h('h3', { class: 'ptitle' }, h('span', { text: T('commonTitle') }), ui.helpBtn({ text: T('commonHelp'), ref: 'ngat-mach' })), biasLine, sum, cmList, ctrls));

    // ----- thanh nhảy A · B · C · D (dính đầu) -----
    var jump = h('nav', { class: 'jumpbar', 'aria-label': T('jumpLabel'), 'data-testid': 'jumpbar' });
    R.SCENARIOS.forEach(function (s, i) {
      var b = h('button', { type: 'button', class: 'jbtn', 'data-jump': s, title: C.blocks[s].title + ' (' + (i + 1) + ')', onclick: function () { app.jumpTo(s); } },
        h('b', { class: 'jl', text: s }), h('span', { class: 'jn', text: C.blocks[s].title }), h('span', { class: 'jp', 'data-testid': 'jump-prog-' + s }));
      refs.jump[s] = b; jump.appendChild(b);
    });
    el.appendChild(jump);
    if (root.ResizeObserver) new ResizeObserver(function () { document.documentElement.style.setProperty('--jbh', jump.offsetHeight + 'px'); }).observe(jump);

    // ----- bốn khối -----
    R.SCENARIOS.forEach(function (s) { el.appendChild(blockSection(s)); });
    R.SCENARIOS.forEach(paintOpen);

    function blockSection(s) {
      var def = C.blocks[s], sc = C.scenarios[s], bs = (se.blocks || {})[s] || {}, ticks = bs.ticks || {};
      var sec = h('section', { class: 'blk', id: 'blk-' + s, 'data-block': s, 'data-testid': 'block-' + s });
      var r = refs.blocks[s] = {};
      r.prog = h('span', { class: 'bprog', 'data-testid': 'prog-' + s });
      r.sum = h('span', { class: 'blk-sum', 'data-testid': 'sum-' + s });
      r.toggle = h('button', { type: 'button', class: 'blk-toggle', 'aria-controls': 'blkb-' + s, 'data-testid': 'toggle-' + s,
        onclick: function () { app.ui.blkOpen[s] = !isOpen(s); paintOpen(s); } },
        h('span', { class: 'bletter', text: s }), h('span', { class: 'bt' }, h('span', { class: 'bttl', text: def.title + ' — ' + def.target }), r.sum), r.prog, h('span', { class: 'caret', 'aria-hidden': 'true', text: '▾' }));
      sec.appendChild(h('h3', { class: 'blk-head' }, r.toggle));
      var body = r.body = h('div', { class: 'blk-body', id: 'blkb-' + s });
      sec.appendChild(body);

      // mô tả + ảnh ca thật thu nhỏ (bấm để phóng) + xóa tick
      var thumb = h('button', { type: 'button', class: 'blk-thumbbtn', 'aria-label': T('scenImgOpen', { name: sc.name }), 'data-testid': 'thumb-' + s,
        onclick: function () {
          app.openModal(h('div', { class: 'dlg imgdlg' }, h('h3', { text: s + ' · ' + sc.name }),
            h('a', { href: sc.img, target: '_blank', rel: 'noopener', title: T('scenImgZoom') }, h('img', { class: 'scenimg full', src: sc.img, alt: T('scenImgAlt', { name: sc.name }) })),
            h('p', { class: 'muted small', text: T('scenImgZoom') }),
            h('div', { class: 'actions' }, btn(T('close'), function () { app.closeModal(false); }, 'primary'))));
        } }, h('img', { class: 'blk-thumb', src: sc.img, alt: T('scenImgAlt', { name: sc.name }), loading: 'lazy' }));
      body.appendChild(h('div', { class: 'blk-intro' },
        h('div', { class: 'bt' }, h('p', { class: 'muted', text: sc.blurb }), def.sizeNote ? h('p', { class: 'sizenote', text: def.sizeNote }) : null),
        h('div', { class: 'blk-side' }, btn(T('clearBlock'), function () { app.clearBlockTicks(s); }, 'ghost small', { 'data-testid': 'clear-' + s, title: 'N' }), thumb)));

      // hướng + vùng
      var zopts = res0.zones.map(function (z) { return { v: z.id, label: z.id + ' · ' + ui.zoneLabel(z), sub: z.flags.map(function (f) { return C.flagText[f] || f; }).join(' · ') || null }; });
      r.zinfo = h('div', { class: 'zinfo2', 'data-item': s + ':zone2' });
      body.appendChild(h('div', { class: 'blk-pick' },
        h('div', { class: 'ctl', 'data-item': s + ':side' }, h('div', { class: 'ctl-label', text: T('sideL') }),
          seg(SIDE_OPTS, bs.side || null, function (v) { setBlock(s, function (b) { if (v) b.side = v; else delete b.side; }, false, true); }, { cls: 'big2', label: T('sideL') })),
        h('div', { class: 'ctl', 'data-item': s + ':zone' }, h('div', { class: 'ctl-label' }, h('span', { text: T('zoneL') }), ui.helpBtn({ text: T('zoneHelp'), ref: 'xep-hang-vung' })),
          zopts.length ? seg(zopts, bs.zoneId || null, function (v) { setBlock(s, function (b) { if (v) b.zoneId = v; else delete b.zoneId; }, false); }, { cls: 'wrap', label: T('zoneL') })
            : h('span', { class: 'muted', text: T('noZones') + ' ' }, btn(T('goTier1'), function () { app.go(1); }, 'small')), r.zinfo)));

      // ô lý do ngược bias (chỉ hiện khi ngược bias) + ô tail (chỉ khối B)
      r.counter = h('div', { class: 'ctl counterbox', 'data-item': s + ':counter', hidden: true });
      r.counterChip = h('div', { class: 'counterwhy' });
      r.counter.appendChild(r.counterChip);
      r.counter.appendChild(textInput(bs.reason || '', function (v) { setBlock(s, function (b) { b.reason = v; }, true); }, { placeholder: T('counterPh'), label: T('counterPh'),
        onInput: function (v) { setBlock(s, function (b) { b.reason = v; }, true); } }));
      if (s === 'B') {
        r.tail = h('div', { class: 'tickrow', 'data-item': 'B:tail' },
          h('label', { class: 'tick36' }, h('input', { type: 'checkbox', checked: bs.tail ? true : null, 'data-testid': 'tick-B-tail', 'data-id': 'tick-B-tail', 'aria-label': C.itemLabels.tail,
            onchange: function (e) { var on = e.target.checked; setBlock('B', function (b) { if (on) b.tail = true; else delete b.tail; }, true); } }), h('span', { class: 'tt', text: C.itemLabels.tail })),
          ui.helpBtn(C.helps.tail));
        r.counter.appendChild(r.tail);
      }
      body.appendChild(r.counter);

      // hai cột: Bối cảnh | Kiểm tra, rồi Điểm vào | SL
      function group(g) {
        var grp = h('div', { class: 'grp', 'data-group': g }, h('h4', { class: 'grp-title', text: C.groupTitles[g] }));
        def[g].forEach(function (it, i) { grp.appendChild(tickRow(s, g + (i + 1), it, ticks)); });
        return grp;
      }
      body.appendChild(h('div', { class: 'blk-groups' }, group('ctx'), group('chk')));
      var slg = h('div', { class: 'grp', 'data-group': 'sl' }, h('h4', { class: 'grp-title', text: C.groupTitles.sl }));
      def.sl.forEach(function (it, i) { slg.appendChild(tickRow(s, 'sl' + (i + 1), it, ticks)); });
      body.appendChild(h('div', { class: 'blk-groups' }, group('ent'), slg));

      // giá vào · SL · TP (Enter nhảy ô kế; biên độ nến nằm ở ô chung)
      var numRow = h('div', { class: 'ctl numgrp', 'data-item': s + ':nums' });
      r.tpIn = numInput(bs.tp === undefined ? null : bs.tp, function (v) { setBlock(s, function (b) { if (v === null) delete b.tp; else b.tp = v; }, true); }, { label: T('tpL'), placeholder: T('tpAuto'), id: 'tp-' + s });
      function numField(label, key, id, onEnter) {
        var o = { label: label, id: id + '-' + s, placeholder: '0000,0', onEnter: onEnter };
        return h('label', { class: 'mini-l' }, label, numInput(bs[key] === undefined ? null : bs[key], function (v) { setBlock(s, function (b) { if (v === null) delete b[key]; else b[key] = v; }, true); }, o));
      }
      numRow.appendChild(h('div', { class: 'ctl-label' }, h('span', { text: T('numsTitle') }), ui.helpBtn({ text: T('numsHelp'), ref: 'luat-sl' })));
      numRow.appendChild(h('div', { class: 'row wrap' },
        numField(T('entryL'), 'entry', 'entry', function () { focusEl('[data-id="sl-' + s + '"]'); }),
        numField(T('slL'), 'sl', 'sl', function () { focusEl('[data-id="tick-' + s + '-sl1"]'); }),
        h('label', { class: 'mini-l' }, T('tpL'), r.tpIn)));
      r.calc = h('div', { class: 'calcslot', 'data-testid': 'calc-' + s });
      numRow.appendChild(r.calc);
      body.appendChild(numRow);

      // ô tự kiểm của khối: chip gọn khi đạt, hàng đầy đủ + lý do khi đỏ
      r.autos = h('div', { class: 'autos', 'aria-label': T('autosTitle') });
      autoIds(s).forEach(function (id) {
        var row = h('div', { class: 'auto wait', 'data-item': s + ':' + id, 'data-auto': id });
        var o = { row: row, mk: h('span', { class: 'cm-mark', 'aria-hidden': 'true' }), lab: h('span', { class: 'cm-label' }), why: h('span', { class: 'cm-why' }) };
        row.appendChild(o.mk); row.appendChild(o.lab); row.appendChild(o.why);
        if (id === 'near') {
          o.wick = h('label', { class: 'wickbox', hidden: true }, h('input', { type: 'checkbox', checked: bs.wick ? true : null, 'data-testid': 'wick-' + s, 'data-id': 'wick-' + s, 'aria-label': T('wickL'),
            onchange: function (e) { var on = e.target.checked; setBlock(s, function (b) { if (on) b.wick = true; else delete b.wick; }, true); } }), h('span', { text: T('wickL') }));
          row.appendChild(o.wick); row.appendChild(ui.helpBtn(C.helps.near));
        }
        if (id === 'size') { o.cap = btn(T('capChange'), function () { app.openCapital(false); }, 'small', { 'data-testid': 'btn-capital', hidden: true }); row.appendChild(o.cap); }
        r['auto_' + id] = o; r.autos.appendChild(row);
      });
      body.appendChild(h('div', { class: 'autowrap' }, h('div', { class: 'grp-title', text: T('autosTitle') }), r.autos));
      r.sec = sec;
      return sec;
    }

    function tickRow(s, id, it, ticks) {
      var cb = h('input', { type: 'checkbox', checked: ticks[id] ? true : null, 'data-testid': 'tick-' + s + '-' + id, 'data-id': 'tick-' + s + '-' + id, 'aria-label': ui.fillTimes(it.t),
        onchange: function (e) {
          var on = e.target.checked;
          setBlock(s, function (b) {
            if (on) b.ticks[id] = true; else delete b.ticks[id];
            if (s === 'A' && id === 'ctx1') { if (on) b.ctx1At = app.nowMin; else delete b.ctx1At; }   // giờ cú phá = lúc tick ô nến M5
          }, true);
          // vừa tick nến xác nhận: nhảy sẵn vào ô Giá vào để gõ luôn
          if (on && id === 'ent1') { var inp = document.querySelector('[data-id="entry-' + s + '"]'); if (inp && !inp.value) setTimeout(function () { try { inp.focus(); } catch (x) { /* bỏ qua */ } }, 0); }
        } });
      return h('div', { class: 'tickrow', 'data-item': s + ':' + id },
        h('label', { class: 'tick36' }, cb, h('span', { class: 'tt', text: ui.fillTimes(it.t) })), it.help ? ui.helpBtn(it.help) : null);
    }

    // ----- phần "sống": cập nhật tại chỗ, không dựng lại ô nhập -----
    function autoRow(r, id, a, bl, a2) {
      var o = r['auto_' + id], ok = a ? a.ok : null;
      o.row.className = 'auto ' + stateCls(ok);
      o.mk.textContent = mark(ok);
      o.lab.textContent = ui.fillTimes(C.itemLabels[id]);
      var why = '';
      if (a && a.reason) why = ui.autoReason(a.reason, bl, a2);
      else if (ok === null) why = T('autoWait');
      o.why.textContent = why;
      o.why.classList.toggle('muted', ok === null);
      if (o.wick) { o.wick.hidden = !(a && a.needWick); if (a && a.needWick) o.wick.querySelector('input').checked = !!bl.wick; }
      if (o.cap) o.cap.hidden = !(a && (a.reason === 'size' || a.reason === 'noCapital'));
    }
    function fillLive(a2) {
      var res = a2.res;
      // bias
      ui.clear(biasLine);
      biasLine.appendChild(chip(T('biasChip', { v: ui.biasText(res.bias) }), 'bias ' + ui.dirCls(res.bias)));
      var bn = res.bias === 'KHÔNG' ? T('biasNoneNote') : res.bias === 'CHỜ' ? T('biasWaitNote') : res.bias ? null : T('biasUnknownNote');
      if (bn) biasLine.appendChild(h('span', { class: 'muted small', text: bn }));
      // ô chung: bốn ô máy kiểm gộp một dòng khi đạt hết; ô nào đỏ mới hiện hàng riêng
      var autoOk = 0, autoN = 0;
      res.common.forEach(function (c) {
        var rf = refs.common[c.id];
        rf.row.classList.toggle('ok', c.ok); rf.row.classList.toggle('bad', !c.ok);
        rf.mark.textContent = c.auto ? mark(c.ok) : '';
        rf.why.textContent = c.ok ? '' : ui.commonReason(c.reason, a2);
        if (c.auto) { autoN++; if (c.ok) autoOk++; rf.row.hidden = c.ok; }
        var go = rf.row.querySelector('[data-testid="go-journal"]'); if (go) go.hidden = c.ok;
      });
      sum.textContent = T('commonSum', { n: autoOk, m: autoN });
      sum.classList.toggle('ok', autoOk === autoN); sum.classList.toggle('bad', autoOk !== autoN);
      var lc = refs.common.longest; lc.row.querySelector('input').checked = !!(a2.night.se.common || {}).justLongest;
      // bốn khối
      R.SCENARIOS.forEach(function (s) {
        var bl = res.blocks[s], r = refs.blocks[s];
        r.prog.textContent = bl.done + '/' + bl.total;
        r.sec.classList.toggle('complete', bl.complete);
        r.sum.textContent = [bl.side || '', bl.zone ? bl.zone.id : ''].filter(Boolean).join(' · ');
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
        if (bl.counter) {
          r.counterChip.appendChild(h('span', { class: 'cm-why', text: ui.autoReason('counter', bl, a2) }));
          if (s === 'B') r.counterChip.appendChild(chip(T('counterTag'), 'warn'));
        }
        if (r.tail) r.tail.querySelector('input').checked = !!bl.tailOk;
        // số + cỡ lệnh
        var cc = bl.calc;
        ui.clear(r.calc);
        r.tpIn.input.placeholder = cc.tpSuggested !== null ? J.fmt(cc.tpSuggested) : T('tpAuto');
        if (cc.numsOk && cc.slSideOk) {
          var line = h('div', { class: 'calcline' });
          line.appendChild(chip(T('calcSl', { v: J.fmt(cc.slDist) }), ''));
          line.appendChild(chip(T('calcRr', { v: J.fmtTrim(cc.rr) }), cc.rr >= R.T.rrMin - 1e-9 ? 'good' : 'bad'));
          if (cc.tpSuggested !== null) line.appendChild(chip(T('calcTpSug', { v: J.fmt(cc.tpSuggested) }) + ' (' + J.fmtTrim(cc.targetR) + 'R)', ''));
          var sizeTxt = cc.size === null ? T('sizeNoCfg') : cc.size === 0 ? T('sizeZero') : cc.sizeMinOne ? T('sizeMinOne', { usd: J.fmtTrim(cc.realUsd) }) : T('sizeN', { n: cc.size });
          line.appendChild(chip(T('sizeTitle') + ': ' + sizeTxt, bl.half ? 'warn' : ''));
          if (bl.half) line.appendChild(chip(T(cc.sizeMinOne ? 'halfNoteMin' : 'halfNote', { why: bl.halfs.map(function (x) { return ui.fillTimes(C.halfText[x]); }).join(', ') }), 'warn'));
          r.calc.appendChild(line);
        } else if (cc.numsOk && !cc.slSideOk) {
          r.calc.appendChild(h('span', { class: 'prob', role: 'alert', text: bl.side === 'sell' ? T('slAbove') : T('slBelow') }));   // SL sai phía: nói đúng nghĩa
        } else r.calc.appendChild(h('span', { class: 'muted small', text: T('calcNeed') }));
        // ô tự kiểm của khối
        autoIds(s).forEach(function (id) {
          var a = bl.autoChecks.filter(function (x) { return x.id === id; })[0];
          autoRow(r, id, a, bl, a2);
        });
      });
    }
    fillLive(app);
    el._live = fillLive;
    return el;
  }

  // ===== thanh dính đáy: ENTRY / CHỜ / kết quả lệnh đang mở =====
  function verdictBar(app) {
    var res = app.res, e = res.entry, op = res.open;
    var bc = app.ui.barClose && op && app.ui.barClose.id === op.trade.id ? app.ui.barClose : null;
    var cls = op ? 'v-open' : e ? 'v-entry' + (e.paper ? ' paper' : '') : 'v-wait';
    var bar = h('div', { class: 'vbar ' + cls, 'data-verdict': op ? 'OPEN' : e ? 'ENTRY' : 'WAIT', 'data-testid': 'verdict', role: 'status', 'aria-live': 'polite' });
    var main = h('div', { class: 'vmain' }), actions = h('div', { class: 'vact' }), notes = h('div', { class: 'vnotes' });
    var half = null;
    if (op) {
      // lệnh đang mở: nút kết quả ngay trên thanh, không phải sang Sổ
      var t = op.trade, row = J.rowOf(t), be = J.beInfo(t);
      main.appendChild(h('div', { class: 'vtext open', 'data-testid': 'open-text' },
        h('b', { text: T('barOpen') }), ' ', h('span', { class: 'ebig2', text: t.side + ' ' + row.name + ' ' + J.fmt(t.entry) }),
        h('span', { class: 'erest', text: ' · SL ' + J.fmt(t.sl) + ' · TP ' + J.fmt(t.tp) + ' · ' + T('barBe', { r: J.fmtTrim(be.target), price: J.fmt(be.priceAt) }) })));
      if (!bc) {
        [{ v: 'TP', l: T('closeTp') }, { v: 'SL', l: T('closeSl') }, { v: 'BE', l: T('closeBe') }, { v: 'MANUAL', l: T('closeManual') }].forEach(function (k) {
          actions.appendChild(btn(k.l, function () { app.ui.barClose = { id: t.id, kind: k.v }; app.render({ keep: true }); }, 'barres', { 'data-testid': 'bar-' + k.v }));
        });
      } else {
        var def = bc.kind === 'TP' ? t.tp : bc.kind === 'SL' ? t.sl : bc.kind === 'BE' ? t.entry : null;
        var price = bc.price === undefined ? def : bc.price;
        var rEl = h('span', { class: 'rnow', 'data-testid': 'bar-r' });
        function paintR() { var r = J.computeR(t, price); rEl.textContent = r === null ? '' : 'R ' + J.fmtR(r); }
        var pIn = numInput(price, function (v) { price = v; bc.price = v; paintR(); }, { id: 'barprice', label: T('exitPrice'),
          onEnter: function () { confirmClose(); } });
        function confirmClose() {
          if (bc.kind === 'MANUAL' && !bc.reason) { app.toast(T('needReason')); return; }
          if (R.num(price) === null) { app.toast(T('needExit')); return; }
          app.ui.barClose = null;
          app.closeOpen(op, { kind: bc.kind, price: price, reason: bc.reason });
        }
        paintR();
        if (bc.kind === 'MANUAL') {
          C.closeReasons.forEach(function (x) {
            actions.appendChild(btn(x.label, function () { bc.reason = x.v; app.render({ keep: true }); }, 'barres' + (bc.reason === x.v ? ' sel' : '') + (x.v === 'other' ? ' bad' : ''), { 'data-testid': 'bar-reason-' + x.v, 'aria-pressed': bc.reason === x.v ? 'true' : 'false' }));
          });
        }
        actions.appendChild(h('label', { class: 'mini-l barprice' }, T('exitPrice'), pIn));
        actions.appendChild(rEl);
        actions.appendChild(btn(T('closeConfirm'), confirmClose, 'primary', { 'data-testid': 'bar-confirm' }));
        actions.appendChild(btn(T('cancel'), function () { app.ui.barClose = null; app.render({ keep: true }); }, 'ghost', { 'data-testid': 'bar-cancel' }));
      }
      // vẫn vào kèo khác khi đang có lệnh mở (tính phá luật)
      var f0 = res.focus, bl0 = f0 ? res.blocks[f0] : null;
      if (bl0 && bl0.side && bl0.calc.numsOk && bl0.complete) {
        actions.appendChild(btn(T('forceBtn', { n: res.common.filter(function (x) { return !x.ok; }).length }), function () { app.forceTrade(f0); }, 'danger small', { 'data-testid': 'btn-force' }));
      }
    } else if (e) {
      var cc = e.calc;
      half = e.half ? e : null;
      var sizePart = cc.sizeMinOne ? T('sizeMinOne', { usd: J.fmtTrim(cc.realUsd) }) : (e.half ? T('sizeHalfShort') : T('sizeFull')) + (cc.size === null || cc.size === undefined ? '' : ' · ' + T('sizeN', { n: cc.size }));
      main.appendChild(h('div', { class: 'vtext entry', 'data-testid': 'entry-text' },
        h('span', { class: 'ebig', text: (e.paper ? T('entryView') : 'ENTRY') + ' ' + e.side.toUpperCase() + ' · ' + T('scenTag', { s: e.scen }) }),
        h('span', { class: 'erest', text: ' ' + J.fmt(cc.entry) + ' · SL ' + J.fmt(cc.sl) + ' (' + T('slGia', { v: J.fmt(cc.slDist) }) + ') · TP ' + J.fmt(cc.tpUsed) + ' · 1:' + J.fmtTrim(cc.rr) + ' · ' + sizePart + (e.counter && e.scen === 'B' ? ' · ' + T('counterTag') : '') })));
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
