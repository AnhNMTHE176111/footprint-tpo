'use strict';
// Sổ (cộng R, lệch máy/tay, 4 con số tuần, Markdown, dòng ⚠) + store (migrate, nhập JSON gộp)
const test = require('node:test');
const assert = require('node:assert/strict');
const J = require('../js/journal.js');
const S = require('../js/store.js');
const { trade, closed } = require('./helpers.js');

function sampleNight() {
  const n = J.newNight();
  n.trades = [
    trade({ id: 'a1', time: '20:25', side: 'sell', scenario: 'A', mode: 'broken', zoneType: 'hvnW', tests: { b1: 'U', c4: 'same', c4num: -129, b2: null, b3: 'ok', c5: 'near' }, slDist: 2.4, exit: { kind: 'TP', price: 4185.8, at: '20:50' }, r: 3 }),
    trade({ id: 'a2', time: '20:48', side: 'sell', scenario: 'B', mode: 'balanced', zoneType: 'vwapW', tests: { b1: 'V', c4: 'oppHold', c4num: 29, b2: null, b3: 'ok', c5: 'near' }, slDist: 1.2,
      exit: { kind: 'SL', price: 0, at: '20:55' }, r: -1, flags: ['RULE_BREAK'], ruleCodes: ['NO_V_PULLBACK', 'NO_BUBBLE_AGAINST', 'NO_SL_FLOOR'] })
  ];
  return n;
}

test('sổ: máy cộng R, lệch tay ⇒ mismatch', () => {
  const n = sampleNight();
  assert.equal(J.recomputeTally(n, 1000), 2);
  assert.equal(n.tally.closedAt, 1000);
  assert.equal(J.tallyMismatch(n), false);          // chưa nhập tay
  J.manualTally(n, 2, 2000); assert.equal(J.tallyMismatch(n), false);
  J.manualTally(n, 3, 3000); assert.equal(J.tallyMismatch(n), true);
});
test('sổ: lệnh luyện mắt và lệnh chưa đóng không vào máy cộng', () => {
  const n = sampleNight();
  n.trades.push(closed('TP', 3, { flags: ['paper'] }), trade({ exit: null }));
  assert.equal(J.recomputeTally(n), 2);
});
test('sổ: dòng ⚠ từ htRef — "phạm 4.1, 4.3 và luật SL" đúng mẫu HT', () => {
  assert.equal(J.warnLine({ ruleCodes: ['NO_V_PULLBACK', 'NO_BUBBLE_AGAINST', 'NO_SL_FLOOR'] }), 'phạm 4.1, 4.3 và luật SL');
  assert.equal(J.warnLine({ ruleCodes: ['NO_BUBBLE_AGAINST', 'NO_V_PULLBACK'] }), 'phạm 4.3, 4.1');
  assert.equal(J.warnLine({ ruleCodes: ['NO_SL_POS'] }), 'phạm luật SL');
  assert.equal(J.warnLine({ ruleCodes: ['NO_ZONE_3RD'] }), 'phạm mục 7');
  assert.equal(J.warnLine({ ruleCodes: [] }), '');
  assert.equal(J.warnLine({ ruleCodes: ['WAIT_B2'] }), 'phạm 4.2');                 // mã CHỜ cũng có htRef (REVIEW-1 mục 18)
  assert.equal(J.warnLine({ ruleCodes: ['WAIT_B3_NOT'] }), 'phạm mục 5');
  assert.equal(J.warnLine({ ruleCodes: ['NO_SIZE_ZERO'] }), 'phạm ST §6');
});
test('sổ: 7 cột cho 4 kịch bản — cột V/U và Δ', () => {
  const base = { time: '20:00', side: 'sell', mode: 'broken', slDist: 2.4, exit: { kind: 'TP' }, r: 3, flags: [], ruleCodes: [] };
  const row = (scenario, tests) => J.rowOf(trade(Object.assign({}, base, { scenario, tests })));
  assert.equal(row('A', { b1: 'U', c4: 'none', b3: 'ok', c5: 'near' }).checks, 'U · bb không có · Δ nến mạnh · cạnh');
  assert.equal(row('B', { b1: 'U', c4: 'same', c4num: -51, b2: 'down', b3: 'ok', c5: 'near' }).checks, 'U · bb -51 giữ · Δ giảm · cạnh');
  assert.equal(row('C', { b1: null, c4: 'same', c4num: 12, b3: 'ok', c5: 'near' }).checks, '— · bb +12 giữ · Δ — · cạnh');
  assert.equal(row('D', { b1: 'V', c4: 'oppBroken', c4num: 40, b3: 'ok', c5: 'far' }).checks, 'V · bb +40 vỡ · Δ nến mạnh · lưng');
  assert.equal(row('C', { b1: 'U', c4: 'same', b3: 'ok', c5: 'near' }).checks.startsWith('— '), true);
  assert.equal(row('A', { b1: 'U', c4: 'same', b3: 'ok', c5: 'near' }).name, 'phá hồi');
  assert.equal(row('B', {}).name, 'hấp thụ'); assert.equal(row('C', {}).name, 'fade cạnh'); assert.equal(row('D', {}).name, 'trap');
});
test('sổ: Markdown đúng mẫu (so chuỗi)', () => {
  const n = sampleNight();
  J.recomputeTally(n, 5000); J.manualTally(n, 2, 6000);
  const want = [
    '# Sổ đêm 2026-10-06',
    '',
    '| giờ | hướng | tên | chế độ | 4 kiểm tra (V/U · bb · Δ · cạnh) | SL | R |',
    '|---|---|---|---|---|---|---|',
    '| 20:25 | sell | phá hồi | vừa phá | U · bb -129 giữ · Δ nến mạnh · cạnh | 2,4 | +3 |',
    '| 20:48 | sell | hấp thụ | cân bằng | V · bb +29 NGƯỢC · Δ — · cạnh | 1,2 | -1 ⚠ |',
    '',
    '⚠ dòng 20:48 phạm 4.1, 4.3 và luật SL',
    '',
    'Máy cộng: +2 R · Bạn cộng: +2 R · Lệnh phá luật: 1 · SL bị quét rồi tới TP: 0',
    ''
  ].join('\n');
  assert.equal(J.toMarkdown(n, '2026-10-06'), want);
});
test('sổ: Markdown khi chưa nhập "Bạn cộng"', () => {
  const n = J.newNight();
  assert.match(J.toMarkdown(n, '2026-10-06'), /Máy cộng: 0 R · Bạn cộng: — · Lệnh phá luật: 0/);
});
test('sổ: định dạng số dấu phẩy, ô nhập nhận cả dấu chấm', () => {
  assert.equal(J.fmt(2.4), '2,4'); assert.equal(J.fmt(null), '—'); assert.equal(J.fmtR(1.5), '+1,5'); assert.equal(J.fmtR(-1), '-1'); assert.equal(J.fmtR(0), '0');
  assert.equal(J.fmtTrim(3.333), '3,33');
  assert.equal(J.parseNum('4193.5'), 4193.5); assert.equal(J.parseNum('4193,5'), 4193.5); assert.equal(J.parseNum(' 2,4 '), 2.4);
  assert.equal(J.parseNum(''), null); assert.equal(J.parseNum('abc'), null); assert.equal(J.parseNum('-'), null);
});
test('sổ: CSV có đủ cột và thoát dấu phẩy', () => {
  const st = S.defaultState(); st.nights['2026-10-06'] = sampleNight();
  const lines = J.toCSV(st).trim().split('\n');
  assert.equal(lines.length, 3);
  assert.equal(lines[0].split(',').length, 25);
  assert.match(lines[2], /RULE_BREAK/); assert.match(lines[2], /NO_V_PULLBACK\|NO_BUBBLE_AGAINST\|NO_SL_FLOOR/);
});
test('tuần: 4 con số HT 8 + chuỗi đêm 0 phá luật', () => {
  const st = S.defaultState();
  const night = (key, trades, locked) => { const n = J.newNight(); n.trades = trades; n.card.lockedAt = locked ? '19:00' : null; st.nights[key] = n; };
  night('2026-10-12', [closed('TP', 3, { scenario: 'A', zoneType: 'vwapW' }), closed('SL', -1, { scenario: 'B', zoneType: 'vwapW', sweptThenTP: true })], true);
  night('2026-10-13', [closed('SL', -1, { scenario: 'A', zoneType: 'hvnW', flags: ['RULE_BREAK'] }), closed('TP', 2, { scenario: 'B', zoneType: 'highY', flags: ['COUNTER_BIAS'] }), closed('TP', 5, { flags: ['paper'] })], true);
  night('2026-10-14', [closed('TP', 3, { scenario: 'A', zoneType: 'vwapW' })], true);
  night('2026-10-19', [closed('TP', 3, { scenario: 'A' })], true);                 // tuần khác
  const w = J.weekStats(st, '2026-10-14');
  assert.equal(w.week, '2026-10-12');
  assert.equal(w.trades, 5); assert.equal(w.ruleBreaks, 1); assert.equal(w.swept, 1);
  assert.deepEqual(w.byScenario.A, { n: 3, r: 5 }); assert.deepEqual(w.byScenario.B, { n: 2, r: 1 });
  assert.deepEqual(w.byZone.vwapW, { n: 3, r: 5 }); assert.deepEqual(w.counter, { n: 1, r: 2 });
  assert.equal(w.streak, 1);   // đêm 14 sạch; đêm 13 có phá luật ⇒ dừng
  assert.equal(J.weekStats(st, '2026-10-12').streak, 1);
  assert.equal(J.weekStats(st, '2026-10-19').streak, 2); // đêm 19 sạch + đêm 14 sạch, rồi đêm 13 phá luật
});

// ---------- store ----------
function fakeStorage(init) {
  const m = Object.assign({}, init || {});
  return { getItem: (k) => (k in m ? m[k] : null), setItem: (k, v) => { m[k] = v; }, _m: m };
}
test('store: không có dữ liệu ⇒ trạng thái mặc định; lưu rồi tải lại giữ nguyên', () => {
  const st = fakeStorage();
  const s0 = S.load(st);
  assert.equal(s0.version, 1); assert.equal(s0.settings.theme, 'dark'); assert.deepEqual(s0.nights, {});
  s0.nights['2026-10-06'] = sampleNight();
  assert.equal(S.save(st, s0), true);
  const s1 = S.load(st);
  assert.deepEqual(s1, s0);
});
test('store: migrate dữ liệu cũ không có version, thiếu trường', () => {
  const m = S.migrate({ nights: { '2026-10-01': { trades: [{ id: 'x', flags: [] }], card: { zones: [{ id: 'z1' }] } } }, settings: { capital: 3000 } });
  assert.equal(m.version, 1); assert.equal(m.settings.capital, 3000); assert.equal(m.settings.riskPct, 2); assert.equal(m.settings.dstShift, true);
  const n = m.nights['2026-10-01'];
  assert.equal(n.trades.length, 1); assert.deepEqual(n.card.answers, {}); assert.equal(n.t0.windows.length, 2); assert.equal(n.regime.mode, 'balanced');
  assert.equal(n.card.zones[0].id, 'z1');
});
test('store: JSON hỏng ⇒ mặc định, bản hỏng được giữ lại', () => {
  const st = fakeStorage({ 'tdv.v1': '{khong phai json' });
  const s = S.load(st);
  assert.deepEqual(s.nights, {}); assert.equal(st._m['tdv.v1.hong'], '{khong phai json');
});
test('store: localStorage ném lỗi ⇒ vẫn chạy', () => {
  const bad = { getItem() { throw new Error('chặn'); }, setItem() { throw new Error('chặn'); } };
  assert.deepEqual(S.load(bad).nights, {}); assert.equal(S.save(bad, S.defaultState()), false);
});
test('store: nhập JSON gộp theo trades.id, đêm trùng giữ bản có closedAt mới hơn', () => {
  const local = S.defaultState();
  const a = J.newNight(); a.trades = [closed('TP', 3, { id: 'a1', time: '20:25' })]; J.recomputeTally(a, 1000);
  local.nights['2026-10-06'] = a;
  const inc = S.defaultState();
  const b = J.newNight(); b.trades = [closed('TP', 3, { id: 'a1', time: '20:25' }), closed('SL', -1, { id: 'b2', time: '21:10' })]; J.recomputeTally(b, 2000); b.tally.manual = 2;
  inc.nights['2026-10-06'] = b;
  const c = J.newNight(); c.trades = [closed('TP', 2, { id: 'c3' })]; inc.nights['2026-10-07'] = c;
  const res = S.importMerge(local, S.exportJSON(inc));
  assert.equal(res.ok, true); assert.equal(res.nightsNew, 1); assert.equal(res.nightsMerged, 1); assert.equal(res.tradesAdded, 2);
  const n = res.state.nights['2026-10-06'];
  assert.deepEqual(n.trades.map((t) => t.id), ['a1', 'b2']);
  assert.equal(n.tally.manual, 2);              // lấy từ bản mới hơn
  assert.equal(n.tally.machine, 2);
  assert.equal(res.state.nights['2026-10-07'].trades[0].id, 'c3');
  // nhập lại lần nữa không nhân đôi
  const again = S.importMerge(res.state, S.exportJSON(inc));
  assert.equal(again.tradesAdded, 0); assert.equal(again.state.nights['2026-10-06'].trades.length, 2);
});
test('store: bản cũ hơn không đè bản mới; lệnh thiếu vẫn được bổ sung', () => {
  const local = S.defaultState(); const a = J.newNight(); a.trades = [closed('TP', 3, { id: 'a1' })]; J.recomputeTally(a, 5000); local.nights.k = a;
  const inc = S.defaultState(); const b = J.newNight(); b.trades = [closed('SL', -1, { id: 'zz', time: '23:00' })]; J.recomputeTally(b, 1000); inc.nights.k = b;
  const res = S.importMerge(local, S.exportJSON(inc));
  assert.equal(res.state.nights.k.tally.closedAt, 5000);
  assert.deepEqual(res.state.nights.k.trades.map((t) => t.id).sort(), ['a1', 'zz']);
});
test('store: tệp nhập sai ⇒ báo lỗi, không đụng dữ liệu', () => {
  const st = S.defaultState();
  assert.equal(S.importMerge(st, 'xx').ok, false);
  assert.equal(S.importMerge(st, '{"a":1}').ok, false);
});
