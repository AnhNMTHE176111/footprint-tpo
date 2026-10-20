/* Trạm Đêm Vàng — ô chọn loại vùng tự vẽ (combobox): rê chuột hoặc phím ↑↓ lên một dòng thì hiện định nghĩa + "dùng thế nào".
 * Lý do không dùng <select>: chữ chú thích không hiện được khi rê chuột lên option của trình duyệt.
 * Phím: ↑ ↓ Home End chọn dòng · Enter chọn · Esc đóng · gõ chữ để lọc · Tab đóng. Định nghĩa lấy từ content.zoneTypes (cùng nguồn với Từ điển). */
(function (root) {
  'use strict';
  var TDV = root.TDV, ui = TDV.ui, C = TDV.content;
  var T = ui.T, h = ui.h;
  var seq = 0;

  function plain(s) { return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd'); }
  function shortLabel(t) { return C.zoneTypes[t].label.replace(/ \(.*\)$/, ''); }

  // opts: {types:[mã loại], value, onPick(mã), label}
  function zonePick(opts) {
    var id = 'zp' + (++seq), listId = id + '-list';
    var value = opts.value, query = '', active = -1, shown = [], touchMode = false;
    var btn = h('button', { type: 'button', class: 'field zpick-btn', role: 'combobox', 'aria-haspopup': 'listbox', 'aria-expanded': 'false', 'aria-controls': listId, 'aria-label': opts.label || T('zoneType'), 'data-testid': 'zone-type' });
    var q = h('input', { type: 'text', class: 'field zpick-q', role: 'combobox', 'aria-autocomplete': 'list', 'aria-expanded': 'true', 'aria-controls': listId, 'aria-label': T('zoneFilter'), placeholder: T('zoneFilter'), autocomplete: 'off', 'data-testid': 'zone-filter' });
    var list = h('ul', { class: 'zpick-list', role: 'listbox', id: listId, 'aria-label': T('zoneType'), 'data-testid': 'zone-list' });
    var aside = h('aside', { class: 'zpick-def', 'data-testid': 'zone-def', 'aria-live': 'polite' });
    var pop = h('div', { class: 'zpick-pop', hidden: true }, q, h('div', { class: 'zpick-body' }, list, aside));
    var root_ = h('div', { class: 'zpick' }, btn, pop);

    function paintBtn() {
      ui.clear(btn);
      var z = C.zoneTypes[value];
      btn.appendChild(h('span', { class: 'zpick-name', text: z ? shortLabel(value) : T('zonePh') }));
      if (z) btn.appendChild(h('span', { class: 'zrank', text: z.rank }));
      btn.appendChild(h('span', { class: 'caret', 'aria-hidden': 'true', text: '▾' }));
    }
    function defNodes(t, cls) {
      var z = C.zoneTypes[t];
      return [h('p', { class: cls + '-def', text: ui.fillTimes(z.def) }), h('p', { class: cls + '-use' }, h('b', { text: T('zoneUse') + ' ' }), ui.fillTimes(z.use))];
    }
    function paintAside() {
      ui.clear(aside);
      var t = shown[active];
      if (!t) { aside.appendChild(h('p', { class: 'muted', text: T('zoneNone') })); return; }
      aside.appendChild(h('div', { class: 'zpick-def-head' }, h('b', { text: shortLabel(t) }), h('span', { class: 'zrank', text: C.zoneTypes[t].rank })));
      defNodes(t, 'zd').forEach(function (n) { aside.appendChild(n); });
    }
    function setActive(i, scroll) {
      if (!shown.length) { active = -1; paintAside(); q.removeAttribute('aria-activedescendant'); return; }
      active = (i + shown.length) % shown.length;
      [].forEach.call(list.children, function (li, k) {
        var on = k === active;
        li.classList.toggle('active', on);
        li.setAttribute('aria-selected', on ? 'true' : 'false');
        if (on) { q.setAttribute('aria-activedescendant', li.id); if (scroll) { try { li.scrollIntoView({ block: 'nearest' }); } catch (e) { /* bỏ qua */ } } }
      });
      paintAside();
    }
    function paintList() {
      ui.clear(list);
      var f = plain(query.trim());
      shown = opts.types.filter(function (t) { return !f || plain(shortLabel(t) + ' ' + C.zoneTypes[t].rank + ' ' + t).indexOf(f) >= 0; });
      shown.forEach(function (t, k) {
        var z = C.zoneTypes[t];
        var li = h('li', { role: 'option', id: id + '-o' + k, 'aria-selected': 'false', 'data-type': t,
          // chuột thật di chuyển mới đổi dòng (không dùng mouseenter: danh sách cuộn dưới con trỏ đứng yên sẽ giành lại dòng đang chọn bằng phím)
          onmousemove: function () { if (!touchMode && k !== active) setActive(k, false); },
          onpointerdown: function (e) { touchMode = e.pointerType !== 'mouse'; },
          onmousedown: function (e) { e.preventDefault(); },        // giữ focus ở ô lọc để phím tiếp tục chạy
          // điện thoại: chạm lần đầu chỉ hiện định nghĩa, chạm lần hai mới chọn
          onclick: function () { if (touchMode && k !== active) { setActive(k, false); return; } pick(t); } },
          h('span', { class: 'zname', text: shortLabel(t) }), h('span', { class: 'zrank', text: z.rank }),
          h('div', { class: 'zpick-inline' }, defNodes(t, 'zi'), h('p', { class: 'zpick-tap', text: T('zoneTap') })));      // điện thoại: định nghĩa hiện ngay dưới dòng đang chọn
        list.appendChild(li);
      });
      if (!shown.length) list.appendChild(h('li', { class: 'zpick-empty muted', role: 'presentation', text: T('zoneNone') }));
      var cur = shown.indexOf(value);
      setActive(f ? 0 : (cur >= 0 ? cur : 0), true);
    }
    function open(initial) {
      if (!pop.hasAttribute('hidden')) return;
      touchMode = false;
      document.querySelectorAll('.zpick-pop:not([hidden])').forEach(function (p) { p.setAttribute('hidden', ''); });
      query = initial || ''; q.value = query;
      pop.removeAttribute('hidden'); btn.setAttribute('aria-expanded', 'true');
      paintList();
      q.focus();
      try { pop.scrollIntoView({ block: 'nearest' }); } catch (e) { /* bỏ qua */ }   // mở sát đáy màn hình thì cuộn trang cho vừa
    }
    function close(refocus) {
      if (pop.hasAttribute('hidden')) return;
      pop.setAttribute('hidden', ''); btn.setAttribute('aria-expanded', 'false');
      if (refocus) btn.focus();
    }
    function pick(t) { value = t; paintBtn(); close(true); if (opts.onPick) opts.onPick(t); }

    btn.addEventListener('click', function () { if (pop.hasAttribute('hidden')) open(''); else close(true); });
    btn.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); open(''); }
      else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey && e.key !== ' ') { e.preventDefault(); open(e.key); }
    });
    q.addEventListener('input', function () { query = q.value; paintList(); });
    q.addEventListener('keydown', function (e) {
      var k = e.key;
      if (k === 'ArrowDown') { e.preventDefault(); setActive(active + 1, true); }
      else if (k === 'ArrowUp') { e.preventDefault(); setActive(active - 1, true); }
      else if (k === 'Home') { e.preventDefault(); setActive(0, true); }
      else if (k === 'End') { e.preventDefault(); setActive(shown.length - 1, true); }
      else if (k === 'Enter') { e.preventDefault(); e.stopPropagation(); if (shown[active]) pick(shown[active]); }
      else if (k === 'Escape') { e.preventDefault(); e.stopPropagation(); close(true); }
      else if (k === 'Tab') close(false);
    });
    paintBtn();
    root_.open = open; root_.close = close;
    return root_;
  }

  // bấm ra ngoài thì đóng mọi ô chọn đang mở
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.zpick-pop:not([hidden])').forEach(function (p) {
      if (e.target && e.target.closest && p.parentNode && p.parentNode.contains(e.target)) return;
      p.setAttribute('hidden', '');
      var b = p.parentNode && p.parentNode.querySelector('.zpick-btn'); if (b) b.setAttribute('aria-expanded', 'false');
    });
  }, true);

  ui.zonePick = zonePick;
})(this);
