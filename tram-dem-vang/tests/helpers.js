'use strict';
// Dựng dữ liệu test dùng chung. Giờ viết theo giờ VN (UTC+7).
const time = require('../js/time.js');
const engine = require('../js/engine.js');
const R = require('../js/rules.js');

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
  return Object.assign({ t0: t0Default(), card: {}, se: { blocks: {}, common: {}, touch: {}, last: null, n: 0 }, trades: [], tally: {} }, o);
}
function card(answers, zones, extra) {
  return Object.assign({ answers, bias: {}, zones, lockedAt: '19:00', edits: [] }, extra || {});
}
// chạy engine cho đêm `n` vào ngày `date` lúc `hm`; `nights` = các đêm khác (để tìm lệnh mở qua đêm)
function run(date, hm, n, settings, nights, news) {
  const all = Object.assign({}, nights || {}, { [date]: n });
  return engine.evaluate(n, vn(date, hm), settings || SETTINGS, news || null, { key: date, nights: all });
}
let seq = 0;
function trade(o) {
  seq++;
  return Object.assign({ id: 't' + seq, time: '20:00', side: 'sell', scenario: 'A', zoneId: 'z1', zoneType: 'vwapW',
    ticks: {}, missing: [], flags: [], ruleCodes: [], exit: null, r: null }, o);
}
const closed = (kind, r, o) => trade(Object.assign({ exit: { kind, price: 0, at: '20:30' }, r }, o || {}));
const ANS_BUY = { q1: 'D', q5: 'above', vwapW: 'above', q6: 'yes' };
const ANS_SELL = { q1: 'D', q5: 'below', vwapW: 'below', q6: 'yes' };
const ANS_NONE = { q1: 'D', q5: 'below', vwapW: 'above', q6: 'yes' };   // bias KHÔNG
const ANS_WAIT = { q1: 'D', q5: 'below', vwapW: 'near', q6: 'yes' };    // bias CHỜ
function clone(o) { return JSON.parse(JSON.stringify(o)); }
function ticksAll(scen) { const t = {}; R.tickIds(scen).forEach((x) => { t[x.id] = true; }); return t; }

// ===== đêm nền: một khối đủ ô ⇒ ENTRY (mỗi test sửa đúng một chỗ) =====
function mk(scen, over) {
  over = over || {};
  let n, bs;
  if (scen === 'B') {
    n = night({ card: card(clone(ANS_BUY), [
      { id: 'z1', type: 'vwapW', price: 4175 }, { id: 'z2', type: 'valEu', price: 4175.5 }, { id: 'z3', type: 'vahEu', price: 4184 }]) });
    bs = { side: 'buy', zoneId: 'z1', entry: 4177.0, sl: 4174.7, tp: 4183.9, c6: 2.0 };
  } else if (scen === 'C') {
    n = night({ card: card(clone(ANS_BUY), [
      { id: 'z1', type: 'valEu', price: 4175 }, { id: 'z2', type: 'vahEu', price: 4190 }, { id: 'z3', type: 'vwapW', price: 4182 }]) });
    bs = { side: 'buy', zoneId: 'z1', entry: 4176.0, sl: 4173.6, tp: 4180.8, c6: 2.0 };
  } else {
    n = night({ card: card(clone(ANS_SELL), [
      { id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'hvnW', price: 4195 }, { id: 'z3', type: 'valEu', price: 4185 }, { id: 'z4', type: 'vahEu', price: 4199 }]) });
    bs = scen === 'D' ? { side: 'sell', zoneId: 'z2', entry: 4193.0, sl: 4195.4, tp: 4188.2, c6: 2.0 }
      : { side: 'sell', zoneId: 'z2', entry: 4193.0, sl: 4195.4, tp: 4185.8, c6: 2.0 };
  }
  bs.ticks = ticksAll(scen);
  n.se = { blocks: { [scen]: bs }, common: { longest: true }, touch: { [scen]: 1 }, last: scen, n: 1 };
  if (typeof over === 'function') over(n); else {
    if (over.answers) n.card.answers = over.answers;
    if (over.zones) n.card.zones = over.zones;
    if (over.block) Object.assign(n.se.blocks[scen], over.block);
    if (over.t0) Object.assign(n.t0, over.t0);
    if (over.trades) n.trades = over.trades;
  }
  return n;
}
const DATE = '2026-10-13';
// chạy đêm nền ở 21:30 (sau khung giờ 21:00, sau 20:30 ⇒ không có nửa cỡ)
function go(scen, over, hmStr, date) { return run(date || DATE, hmStr || '21:30', mk(scen, over)); }

module.exports = { mk, go, DATE, ANS_BUY, ANS_SELL, ANS_NONE, ANS_WAIT, clone, vn, SETTINGS, t0Default, night, card, run, trade, closed, ticksAll, time, engine };
