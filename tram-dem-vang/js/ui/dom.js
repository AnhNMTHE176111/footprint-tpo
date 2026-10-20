/* Trạm Đêm Vàng — tiện ích DOM dùng chung cho các tầng. */
(function (root) {
  'use strict';
  var TDV = root.TDV = root.TDV || {};
  var ui = TDV.ui = TDV.ui || {};
  var C = TDV.content, J = TDV.journal;

  // giờ trong chữ ({comex} {nyse} {real1} {real2} {fomcFlat}) lấy từ time.js theo mùa của đêm đang xem
  function fillTimes(s) {
    var a = TDV.app;
    if (typeof s !== 'string' || s.indexOf('{') < 0 || !a || !a.key || !TDV.time) return s;
    return C.fill(s, TDV.time.textVars(a.key, a.useDst));
  }
  function T(key, vars) {
    var s = C.ui[key];
    if (s === undefined) { if (root.console) console.warn('thiếu chữ: ' + key); return '⟦' + key + '⟧'; }
    if (vars) s = s.replace(/\{(\w+)\}/g, function (m, k) { return vars[k] === undefined ? m : vars[k]; });
    return fillTimes(s);
  }
  // chạy một bước commit (sự kiện change); vẽ lại do nó gây ra được hoãn tới khi cú bấm đang diễn ra xong (USER-TEST-2 mục 1)
  function held(fn) { var a = TDV.app; if (a && a.hold) a.hold(fn); else fn(); }

  function append(el, c) {
    if (c === null || c === undefined || c === false) return;
    if (Array.isArray(c)) { c.forEach(function (x) { append(el, x); }); return; }
    if (c.nodeType) { el.appendChild(c); return; }
    el.appendChild(document.createTextNode(String(c)));
  }
  function h(tag, attrs) {
    var el = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === 'class') el.className = v;
      else if (k === 'text') el.textContent = v;
      else if (k === 'value') el.value = v;
      else if (k === 'dataset') Object.keys(v).forEach(function (d) { el.dataset[d] = v[d]; });
      else if (k.slice(0, 2) === 'on') el.addEventListener(k.slice(2), v);
      else if (v === true) el.setAttribute(k, '');
      else el.setAttribute(k, v);
    });
    for (var i = 2; i < arguments.length; i++) append(el, arguments[i]);
    return el;
  }
  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); return el; }

  // nút "?" + khung trợ giúp (≤ 2 câu + liên kết đúng mục trang HT)
  function helpBtn(help, extraNote) {
    if (!help) return null;
    var pop = h('div', { class: 'pop', role: 'note', hidden: true },
      h('p', { text: fillTimes(help.text) }),
      extraNote ? h('p', { class: 'muted', text: fillTimes(extraNote) }) : null,
      help.ref ? h('a', { href: C.HT_BASE + help.ref, target: '_blank', rel: 'noopener', text: T('helpLink') }) : null,
      (TDV.app && TDV.app.state.settings.guideLevel === 'new') ? h('button', { type: 'button', class: 'btn small ghost glossbtn', text: T('openGlossary'), onclick: function (e) { e.stopPropagation(); TDV.app.openGlossary(help.gloss); } }) : null);
    var btn = h('button', { class: 'help', type: 'button', 'aria-label': T('helpLabel'), 'aria-expanded': 'false', text: '?',
      onclick: function (e) {
        e.stopPropagation();
        var open = pop.hasAttribute('hidden');
        document.querySelectorAll('.pop').forEach(function (p) { p.setAttribute('hidden', ''); });
        if (open) pop.removeAttribute('hidden');
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      } });
    return h('span', { class: 'helpwrap' }, btn, pop);
  }
  // bấm ra ngoài thì đóng mọi khung "?". Chạy ở pha bắt (trước các nút) để vẽ lại do cú bấm đó không khôi phục lại khung cũ (REVIEW-3 mục 3)
  document.addEventListener('click', function (e) {
    if (e.target && e.target.closest && e.target.closest('.help')) return;
    document.querySelectorAll('.pop').forEach(function (p) { p.setAttribute('hidden', ''); });
    document.querySelectorAll('.help[aria-expanded="true"]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
  }, true);

  // nhóm nút chọn (3 trạng thái); đáp án xấu tô đỏ khi được chọn; bấm lại để bỏ chọn
  function seg(options, value, onPick, opt) {
    opt = opt || {};
    var el = h('div', { class: 'seg' + (opt.cls ? ' ' + opt.cls : ''), role: 'group', 'aria-label': opt.label || null });
    options.forEach(function (o) {
      var sel = value === o.v;
      var disabled = opt.disabled && opt.disabled[o.v];
      var b = h('button', {
        type: 'button', class: 'opt' + (sel ? ' sel' : '') + (sel && o.bad ? ' bad' : '') + (disabled ? ' off' : ''), 'aria-pressed': sel ? 'true' : 'false',
        dataset: { v: o.v }, title: disabled ? disabled : null,
        onclick: function () { if (disabled && opt.onDisabled) { opt.onDisabled(o.v, disabled); return; } onPick(sel && !opt.noToggle ? null : o.v); }
      }, h('span', { class: 'opt-t', text: o.label }), o.sub ? h('span', { class: 'opt-s', text: o.sub }) : null);
      el.appendChild(b);
    });
    return el;
  }

  function fmtIn(v) { return v === null || v === undefined ? '' : String(v).replace('.', ','); }
  // ô nhập số: nhận cả dấu chấm lẫn dấu phẩy; hiển thị dấu phẩy
  function numInput(value, onInput, opt) {
    opt = opt || {};
    var inp = h('input', { type: 'text', inputmode: 'decimal', class: 'field num', autocomplete: 'off', placeholder: opt.placeholder || null, value: fmtIn(value),
      'aria-label': opt.label || null, dataset: opt.id ? { id: opt.id } : null,
      oninput: function () { var v = J.parseNum(inp.value); inp.classList.toggle('invalid', v === null && /\S/.test(inp.value) && inp.value.trim() !== '-'); onInput(v, inp); },
      onchange: function () { held(function () { var v = J.parseNum(inp.value); inp.classList.toggle('invalid', v === null && /\S/.test(inp.value)); if (v !== null) inp.value = fmtIn(v); if (opt.onCommit) opt.onCommit(v, inp); }); } });
    var wrap = h('span', { class: 'numwrap' }, inp, opt.unit ? h('span', { class: 'unit', text: opt.unit }) : null);
    wrap.input = inp;
    return wrap;
  }
  function textInput(value, onChange, opt) {
    opt = opt || {};
    return h('input', { type: 'text', class: 'field txt', value: value || '', placeholder: opt.placeholder || null, 'aria-label': opt.label || null, maxlength: opt.max || 200,
      onchange: function (e) { var v = e.target.value; held(function () { onChange(v); }); }, oninput: opt.onInput ? function (e) { opt.onInput(e.target.value); } : null });
  }

  // "?" của cảnh báo trước 20:30: QĐ-19 là quyết định của công cụ, chưa đo (REVIEW-2 mục 10)
  function qd19Help() { return helpBtn({ text: C.qd['QĐ-19'] + ' (' + C.unmeasured + ')', ref: 'thoi-gian', gloss: 'mo-ao' }); }

  // lý do giảm ½, có giờ theo mùa: "ngày có tin lớn, trước 20:30 (hay mở ảo)"
  function halfWhy(res) { return res.half.reasons.map(function (x) { return fillTimes(C.halfText[x]); }).join(', '); }

  function chip(text, cls, title) { return h('span', { class: 'chip' + (cls ? ' ' + cls : ''), title: title || null, text: text }); }
  function btn(text, onclick, cls, extra) {
    var a = { type: 'button', class: 'btn' + (cls ? ' ' + cls : ''), onclick: onclick, text: text };
    if (extra) Object.keys(extra).forEach(function (k) { a[k] = extra[k]; });
    return h('button', a);
  }
  function banner(text, cls) { return h('div', { class: 'banner ' + (cls || 'info'), role: cls === 'bad' ? 'alert' : null, text: text }); }
  function section(title, body, opt) {
    opt = opt || {};
    return h('section', { class: 'panel' + (opt.cls ? ' ' + opt.cls : '') },
      title ? h('h3', { class: 'ptitle' }, h('span', { text: title }), opt.help ? helpBtn(opt.help) : null) : null, body);
  }

  // màu theo hướng (không dùng đỏ/xanh lá của phán quyết): buy xanh dương, sell cam
  function dirCls(v) { return v === 'BUY' || v === 'buy' ? 'dir-buy' : v === 'SELL' || v === 'sell' ? 'dir-sell' : 'warn'; }
  function biasText(v) { return v === 'BUY' ? T('biasBuy') : v === 'SELL' ? T('biasSell') : v === 'KHÔNG' ? T('biasNone') : v === 'CHỜ' ? T('biasWait') : T('biasUnknown'); }
  function sideText(s) { return s === 'buy' ? 'buy' : s === 'sell' ? 'sell' : '—'; }
  function codeText(code, vars) {
    var c = C.codes[code];
    if (!c) return code;
    return fillTimes(c.text.replace(/\{(\w+)\}/g, function (m, k) { return vars && vars[k] !== undefined ? vars[k] : m; }));
  }
  // biến số cho chữ của mã luật: SL, biên độ nến, vốn, rủi ro, SL tối đa
  function codeVars(app) {
    var cc = app.res.calc, s = app.settings || {};
    return { sl: J.fmt(cc.slDist), c6: J.fmt(TDV.rules.num(app.night.setup.c6)), cap: s.capital, pct: String(s.riskPct).replace('.', ','),
      max: cc.maxSl === undefined ? '—' : J.fmt(cc.maxSl) };
  }
  function zoneLabel(z) {
    var t = C.zoneTypes[z.type];
    var p = z.price === null || z.price === undefined ? '' : J.fmt(z.price, 1) + (z.priceTo !== null && z.priceTo !== undefined && z.priceTo !== '' ? '–' + J.fmt(z.priceTo, 1) : '');
    var side = z.sideKind && TDV.content.zoneTypes[z.type] && (z.type === 'rangeEdge' || z.type === 'sp') ? ' ' + (z.sideKind === 'upper' ? T('sideUpper') : T('sideLower')) : '';
    return (t ? t.label.replace(/ \(.*\)$/, '') : z.type) + ' ' + p + side;
  }

  ui.T = T; ui.h = h; ui.clear = clear; ui.helpBtn = helpBtn; ui.seg = seg; ui.numInput = numInput; ui.textInput = textInput;
  ui.chip = chip; ui.btn = btn; ui.banner = banner; ui.section = section; ui.biasText = biasText; ui.dirCls = dirCls; ui.sideText = sideText;
  ui.codeText = codeText; ui.codeVars = codeVars; ui.fillTimes = fillTimes; ui.held = held; ui.qd19Help = qd19Help; ui.halfWhy = halfWhy; ui.zoneLabel = zoneLabel; ui.fmtIn = fmtIn;
})(this);
