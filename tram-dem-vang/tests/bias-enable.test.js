'use strict';
// Ma trận bias (14 ca) + bảng bật kịch bản (≥ 28 ca) + acceptance + giờ
const test = require('node:test');
const assert = require('node:assert/strict');
const R = require('../js/rules.js');
const { mk, run, ANS_BUY, ANS_SELL, ANS_NONE, ANS_WAIT, clone, time, vn } = require('./helpers.js');

// ---------- bias ----------
const BIAS_CASES = [
  // [vwapW, q5, q1, bias]
  ['above', 'above', 'D', 'BUY'], ['above', 'in', 'P', 'BUY'], ['above', 'in', 'b', 'KHÔNG'], ['above', 'above', 'b', 'KHÔNG'],
  ['above', 'below', 'D', 'KHÔNG'], ['above', 'below', 'b', 'KHÔNG'],
  ['below', 'below', 'D', 'SELL'], ['below', 'in', 'b', 'SELL'], ['below', 'in', 'P', 'KHÔNG'], ['below', 'below', 'P', 'KHÔNG'],
  ['below', 'above', 'D', 'KHÔNG'], ['below', 'above', 'P', 'KHÔNG'],
  ['near', 'above', 'D', 'CHỜ'], ['near', 'below', 'b', 'CHỜ']
];
BIAS_CASES.forEach(([w, q5, q1, want], i) => {
  test('bias #' + (i + 1) + ': VWAP tuần ' + w + ', Q5 ' + q5 + ', Q1 ' + q1 + ' ⇒ ' + want, () => {
    assert.equal(R.autoBias({ vwapW: w, q5, q1 }, {}), want);
  });
});
test('bias: sát VWAP tuần rồi 1 nến M5 đóng rõ một phía ⇒ tính lại với vwapW mới', () => {
  assert.equal(R.autoBias({ vwapW: 'near', q5: 'above', q1: 'D' }, { rechecked: 'above' }), 'BUY');
  assert.equal(R.autoBias({ vwapW: 'near', q5: 'below', q1: 'D' }, { rechecked: 'below' }), 'SELL');
});
test('bias: thiếu câu trả lời ⇒ null; ghi đè cần lý do', () => {
  assert.equal(R.autoBias({ vwapW: 'above' }, {}), null);
  assert.equal(R.effectiveBias({ answers: ANS_BUY, bias: { override: 'SELL' } }).value, 'BUY');
  const e = R.effectiveBias({ answers: ANS_BUY, bias: { override: 'SELL', reason: 'đỉnh có tail' } });
  assert.equal(e.value, 'SELL'); assert.equal(e.overridden, true);
});

// ---------- bảng bật kịch bản ----------
const NOEDGE_ZONES = [{ id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'hvnW', price: 4195 }, { id: 'z3', type: 'hvnDay', price: 4185 }];
function enabledFor(ans, regime, extra) {
  const n = mk('A', { answers: clone(ans), regime });
  if (extra) extra(n);
  return run('2026-10-13', '21:40', n).enabled;
}
const BRK = (dir, step2) => ({ mode: 'broken', breakout: { dir, edgeZoneId: 'z2', at: '20:40', nth: 1, step1: true, step2: step2 !== false } });
const THIN = (dir) => ({ mode: 'thin', thinDir: dir });
const BAL = { mode: 'balanced' };
const exp = (A, B, C, D) => ({ A, B, C, D });

const TABLE = [
  // [tên, ans, regime, expected]
  ['BUY · cân bằng', ANS_BUY, BAL, exp('DIS_NOT_BROKEN', null, null, 'DIS_NO_MOVE')],
  ['BUY · chờ công nhận (thiếu bước 2)', ANS_BUY, BRK('up', false), exp('DIS_PENDING_ACCEPT', null, null, 'DIS_NO_MOVE')],
  ['BUY · vừa phá lên (cùng bias)', ANS_BUY, BRK('up'), exp(null, null, 'DIS_M5_OUTSIDE', null)],
  ['BUY · vừa phá xuống (ngược bias)', ANS_BUY, BRK('down'), exp('DIS_BREAK_AGAINST_BIAS', null, 'DIS_M5_OUTSIDE', 'DIS_BREAK_AGAINST_BIAS')],
  ['BUY · Trend thin lên', ANS_BUY, THIN('up'), exp(null, 'DIS_USE_D', 'DIS_THIN_NO_FADE', null)],
  ['BUY · Trend thin xuống ⇒ D DIS_BREAK_AGAINST_BIAS', ANS_BUY, THIN('down'), exp('DIS_BREAK_AGAINST_BIAS', 'DIS_USE_D', 'DIS_THIN_NO_FADE', 'DIS_BREAK_AGAINST_BIAS')],
  ['SELL · cân bằng', ANS_SELL, BAL, exp('DIS_NOT_BROKEN', null, null, 'DIS_NO_MOVE')],
  ['SELL · vừa phá xuống (cùng bias)', ANS_SELL, BRK('down'), exp(null, null, 'DIS_M5_OUTSIDE', null)],
  ['SELL · vừa phá lên ⇒ A DIS_BREAK_AGAINST_BIAS', ANS_SELL, BRK('up'), exp('DIS_BREAK_AGAINST_BIAS', null, 'DIS_M5_OUTSIDE', 'DIS_BREAK_AGAINST_BIAS')],
  ['SELL · Trend thin xuống', ANS_SELL, THIN('down'), exp(null, 'DIS_USE_D', 'DIS_THIN_NO_FADE', null)],
  ['KHÔNG · cân bằng ⇒ chỉ C bật', ANS_NONE, BAL, exp('DIS_BIAS_NONE', 'DIS_BIAS_NONE', null, 'DIS_BIAS_NONE')],
  ['KHÔNG · vừa phá', ANS_NONE, BRK('down'), exp('DIS_BIAS_NONE', 'DIS_BIAS_NONE', 'DIS_M5_OUTSIDE', 'DIS_BIAS_NONE')],
  ['KHÔNG · Trend thin', ANS_NONE, THIN('up'), exp('DIS_BIAS_NONE', 'DIS_BIAS_NONE', 'DIS_THIN_NO_FADE', 'DIS_BIAS_NONE')],
  ['CHỜ · cân bằng', ANS_WAIT, BAL, exp('DIS_BIAS_WAIT', 'DIS_BIAS_WAIT', 'DIS_BIAS_WAIT', 'DIS_BIAS_WAIT')],
  ['CHỜ · vừa phá', ANS_WAIT, BRK('down'), exp('DIS_BIAS_WAIT', 'DIS_BIAS_WAIT', 'DIS_BIAS_WAIT', 'DIS_BIAS_WAIT')]
];
TABLE.forEach(([name, ans, regime, want]) => {
  test('bật kịch bản: ' + name, () => assert.deepEqual(enabledFor(ans, regime), want));
});

test('bật kịch bản: thẻ không có vùng edge ⇒ B, C DIS_NO_EDGE (A, D không ảnh hưởng)', () => {
  const e = enabledFor(ANS_SELL, BRK('down'), (n) => { n.card.zones = clone(NOEDGE_ZONES); });
  assert.equal(e.B, 'DIS_NO_EDGE'); assert.equal(e.C, 'DIS_NO_EDGE'); assert.equal(e.A, null); assert.equal(e.D, null);
});
test('bật kịch bản: High / Low hôm qua là edgeOuter, không phải edge ⇒ vẫn DIS_NO_EDGE', () => {
  const e = enabledFor(ANS_BUY, BAL, (n) => { n.card.zones = [{ id: 'z1', type: 'highY', price: 4200 }, { id: 'z2', type: 'lowY', price: 4170 }]; });
  assert.equal(e.B, 'DIS_NO_EDGE'); assert.equal(e.C, 'DIS_NO_EDGE');
});
test('bật kịch bản: thẻ chưa chốt ⇒ DIS_NO_CARD cho cả bốn', () => {
  const e = enabledFor(ANS_BUY, BAL, (n) => { n.card.lockedAt = null; });
  assert.deepEqual(e, exp('DIS_NO_CARD', 'DIS_NO_CARD', 'DIS_NO_CARD', 'DIS_NO_CARD'));
});
test('bật kịch bản: khóa 3′ sau nến dài nhất đứng trên mọi hàng', () => {
  const e = enabledFor(ANS_BUY, BRK('up'), (n) => { n.regime.longestBarUntil = vn('2026-10-13', '21:43').getTime(); });
  assert.deepEqual(e, exp('DIS_LONGEST_BAR', 'DIS_LONGEST_BAR', 'DIS_LONGEST_BAR', 'DIS_LONGEST_BAR'));
});

// ---------- acceptance ----------
test('acceptance đủ 3 bước (2 bước M5) ⇒ A bật', () => assert.equal(enabledFor(ANS_SELL, BRK('down')).A, null));
test('acceptance thiếu bước 2 ⇒ pending, A DIS_PENDING_ACCEPT', () => assert.equal(enabledFor(ANS_SELL, BRK('down', false)).A, 'DIS_PENDING_ACCEPT'));
test('acceptance: chưa có nến M5 đóng ngoài (bước 1) ⇒ vẫn cân bằng', () => {
  const r = run('2026-10-13', '21:40', mk('A', { regime: { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z2', at: '21:30', step1: false, step2: false } } }));
  assert.equal(r.regime.effective, 'balanced');
  assert.equal(r.enabled.A, 'DIS_NOT_BROKEN');
});
test('phá lúc 18:30 (phá giả) ⇒ A DIS_EARLY_BREAK; 19:19 vẫn sớm; 19:20 không còn', () => {
  const at = (hm) => enabledFor(ANS_SELL, { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z2', at: hm, nth: 1, step1: true, step2: true } }).A;
  assert.equal(at('18:30'), 'DIS_EARLY_BREAK');
  assert.equal(at('19:19'), 'DIS_EARLY_BREAK');
  assert.equal(at('19:20'), null);
  assert.equal(at('17:59'), null);
});
test('phá lúc 18:30 mùa đông: mốc 19:20 dịch thành 20:20', () => {
  const run1 = (hm) => run('2026-11-10', '21:40', mk('A', { regime: { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z2', at: hm, step1: true, step2: true } } })).enabled.A;
  assert.equal(run1('20:19'), 'DIS_EARLY_BREAK');
  assert.equal(run1('20:20'), null);
});

// ---------- giờ: chỉ đổi half ----------
function halfAt(date, hm) {
  const r = run(date, hm, mk('A', { regime: BRK('down') }));
  return { enabled: r.enabled, half: r.half.reasons };
}
test('20:29 / 20:31 hè: enabled không đổi, chỉ half đổi', () => {
  const a = halfAt('2026-10-13', '20:29'), b = halfAt('2026-10-13', '20:31');
  assert.deepEqual(a.enabled, b.enabled);
  assert.deepEqual(a.half, ['BEFORE_2030']);
  assert.deepEqual(b.half, []);
});
test('21:29 / 21:31 mùa đông: enabled không đổi, chỉ half đổi (nửa cỡ tới 21:30)', () => {
  const a = halfAt('2026-11-10', '21:29'), b = halfAt('2026-11-10', '21:31');
  assert.deepEqual(a.enabled, b.enabled);
  assert.deepEqual(a.half, ['BEFORE_2030']);
  assert.deepEqual(b.half, []);
  assert.deepEqual(halfAt('2026-11-10', '20:31').half, ['BEFORE_2030']);
});
test('cùng chiều / ngược bias ghi đè: không còn DIS_BREAK_AGAINST_BIAS (để NO_COUNTER_BIAS_SCENARIO)', () => {
  const n = mk('A', { regime: BRK('down') });
  n.card.bias = { override: 'BUY', reason: 'thử' };
  const r = run('2026-10-13', '21:40', n);
  assert.equal(r.enabled.A, null);
  assert.equal(r.verdict, 'NO');
  assert.deepEqual(r.reasons, ['NO_COUNTER_BIAS_SCENARIO']);
});
