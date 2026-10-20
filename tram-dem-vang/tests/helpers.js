'use strict';
// Dựng dữ liệu test dùng chung. Giờ viết theo giờ VN (UTC+7).
const time = require('../js/time.js');
const engine = require('../js/engine.js');

function vn(date, hm) { // '2026-10-06', '20:24' → Date
  const [y, m, d] = date.split('-').map(Number);
  const [h, mi] = hm.split(':').map(Number);
  return new Date(Date.UTC(y, m - 1, d, h - 7, mi));
}
const SETTINGS = { dstShift: true, capital: 2000, riskPct: 2 };
function t0Default(over) {
  return Object.assign({ alert: true, touched: true, newsDay: false, windows: [
    { id: 'w1930', kind: 'news', rank: 1, at: '19:30', tz: 'ET', minutesBefore: 15, minutesAfter: 15, on: false },
    { id: 'w2100', kind: 'news', rank: 2, at: '21:00', tz: 'ET', minutesBefore: 5, minutesAfter: 5, on: true }
  ] }, over || {});
}
function night(o) {
  return Object.assign({ t0: t0Default(), card: {}, regime: { mode: 'balanced' }, setup: {}, open: null, trades: [], tally: {} }, o);
}
function card(answers, zones, extra) {
  return Object.assign({ answers, bias: {}, zones, lockedAt: '19:00', edits: [] }, extra || {});
}
function run(date, hm, n, settings, nights) {
  const now = vn(date, hm);
  const key = date;
  return engine.evaluate({ nights: Object.assign({ [key]: n }, nights || {}), nightKey: key, now, settings: settings || SETTINGS });
}
let seq = 0;
function trade(o) {
  seq++;
  return Object.assign({ id: 't' + seq, time: '20:00', side: 'sell', scenario: 'A', mode: 'broken', zoneId: 'z1', zoneType: 'vwapW',
    tests: {}, flags: [], ruleCodes: [], exit: null, r: null }, o);
}
const closed = (kind, r, o) => trade(Object.assign({ exit: { kind, price: 0, at: '20:30' }, r }, o || {}));
// ===== đêm nền cho 4 kịch bản (đều ra ENTRY) — mỗi test sửa đúng một chỗ =====
const ANS_BUY = { q1: 'D', q5: 'above', vwapW: 'above', q6: 'yes' };
const ANS_SELL = { q1: 'D', q5: 'below', vwapW: 'below', q6: 'yes' };
const ANS_NONE = { q1: 'D', q5: 'below', vwapW: 'above', q6: 'yes' };   // bias KHÔNG
const ANS_WAIT = { q1: 'D', q5: 'below', vwapW: 'near', q6: 'yes' };    // bias CHỜ
function clone(o) { return JSON.parse(JSON.stringify(o)); }
function mk(scen, over) {
  over = over || {};
  let n;
  if (scen === 'B') {
    n = night({ card: card(clone(ANS_BUY), [
      { id: 'z1', type: 'vwapW', price: 4175 }, { id: 'z2', type: 'valEu', price: 4175.5 }, { id: 'z3', type: 'vahEu', price: 4184 }]),
      regime: { mode: 'balanced' },
      setup: { scenario: 'B', zoneId: 'z1', side: 'buy', c4: 'same', c4num: -49, c5: 'near', c6: 2.0, c7: { dma: 'flat' }, b1: 'U', b2: 'down', b3: 'ok', slPos: 'right', calc: { entry: 4177.0, sl: 4174.7, tp: 4183.9 } } });
  } else if (scen === 'C') {
    n = night({ card: card(clone(ANS_BUY), [
      { id: 'z1', type: 'valEu', price: 4175 }, { id: 'z2', type: 'vahEu', price: 4190 }, { id: 'z3', type: 'vwapW', price: 4182 }]),
      regime: { mode: 'balanced' },
      setup: { scenario: 'C', zoneId: 'z1', c4: 'none', c5: 'near', c6: 2.0, b3: 'ok', slPos: 'right', calc: { entry: 4176.0, sl: 4173.6, tp: 4180.8 } } });
  } else {
    n = night({ card: card(clone(ANS_SELL), [
      { id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'hvnW', price: 4195 }, { id: 'z3', type: 'valEu', price: 4185 }, { id: 'z4', type: 'vahEu', price: 4199 }]),
      regime: { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z2', at: '20:40', nth: 1, step1: true, step2: true } },
      setup: scen === 'D'
        ? { scenario: 'D', zoneId: 'z2', c4: 'none', c5: 'near', c6: 2.0, c7: { moveSize: 6, deep: 'no' }, b1: 'U', b3: 'ok', slPos: 'right', calc: { entry: 4193.0, sl: 4195.4, tp: 4188.2 } }
        : { scenario: 'A', zoneId: 'z2', c4: 'none', c5: 'near', c6: 2.0, b1: 'U', b3: 'ok', slPos: 'right', calc: { entry: 4193.0, sl: 4195.4, tp: 4185.8 } } });
  }
  if (typeof over === 'function') over(n); else {
    if (over.answers) n.card.answers = over.answers;
    if (over.zones) n.card.zones = over.zones;
    if (over.regime) n.regime = over.regime;
    if (over.setup) Object.assign(n.setup, over.setup);
    if (over.t0) Object.assign(n.t0, over.t0);
    if (over.trades) n.trades = over.trades;
  }
  return n;
}
const DATE = '2026-10-13';
// chạy đêm nền ở 21:30 (sau cửa sổ 21:00, sau 20:30 ⇒ không có nửa cỡ)
function go(scen, over, hmStr, date) { return run(date || DATE, hmStr || '21:30', mk(scen, over)); }

module.exports = { mk, go, DATE, ANS_BUY, ANS_SELL, ANS_NONE, ANS_WAIT, clone, vn, SETTINGS, t0Default, night, card, run, trade, closed, time, engine };
