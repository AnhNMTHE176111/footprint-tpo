'use strict';
// Ma trận bias (HT 2.2): 14 ca + chốt lại sau nến M5 + ghi đè cần lý do
const test = require('node:test');
const assert = require('node:assert/strict');
const R = require('../js/rules.js');
const { ANS_BUY } = require('./helpers.js');

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
test('bias: thiếu câu trả lời ⇒ null; ghi đè cần lý do và phải khác bias tự động', () => {
  assert.equal(R.autoBias({ vwapW: 'above' }, {}), null);
  assert.equal(R.effectiveBias({ answers: ANS_BUY, bias: { override: 'SELL' } }).value, 'BUY');
  const e = R.effectiveBias({ answers: ANS_BUY, bias: { override: 'SELL', reason: 'đỉnh có tail' } });
  assert.equal(e.value, 'SELL'); assert.equal(e.overridden, true);
  assert.equal(R.effectiveBias({ answers: ANS_BUY, bias: { override: 'BUY', reason: 'x' } }).overridden, false);
});
test('ngược bias: BUY mà sell, SELL mà buy; KHÔNG và CHỜ không có ngược', () => {
  assert.equal(R.isCounter('BUY', 'sell'), true); assert.equal(R.isCounter('SELL', 'buy'), true);
  assert.equal(R.isCounter('BUY', 'buy'), false); assert.equal(R.isCounter('KHÔNG', 'sell'), false); assert.equal(R.isCounter('CHỜ', 'buy'), false);
});
