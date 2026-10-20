'use strict';
// Thời gian (giờ mùa đông, nightKey, khung giờ, pha) + thẻ phiên
const test = require('node:test');
const assert = require('node:assert/strict');
const time = require('../js/time.js');
const R = require('../js/rules.js');
const J = require('../js/journal.js');
const C = require('../js/content.js');
const { vn, mk } = require('./helpers.js');

const nk = (date, hm) => time.nightKey(vn(date, hm).getTime(), true);

test('nightKey ngày hè: 00:30 và 04:59 là đêm cũ; 05:00 và 10:00 là đêm mới', () => {
  assert.equal(nk('2026-10-14', '00:30'), '2026-10-13');
  assert.equal(nk('2026-10-14', '04:59'), '2026-10-13');
  assert.equal(nk('2026-10-14', '05:00'), '2026-10-14');
  assert.equal(nk('2026-10-14', '10:00'), '2026-10-14');
  assert.equal(nk('2026-10-14', '23:59'), '2026-10-14');
});
test('nightKey mùa đông: 05:30 ngày 02/11/2026 vẫn là đêm cũ; 06:00 là đêm mới', () => {
  assert.equal(nk('2026-11-02', '05:30'), '2026-11-01');
  assert.equal(nk('2026-11-02', '05:59'), '2026-11-01');
  assert.equal(nk('2026-11-02', '06:00'), '2026-11-02');
});
test('nightKey qua ranh tháng / năm', () => {
  assert.equal(nk('2026-11-01', '02:00'), '2026-10-31');
  assert.equal(nk('2027-01-01', '01:00'), '2026-12-31');
});
test('nightKey khi tắt công tắc giờ mùa đông: luôn mốc 05:00', () => {
  assert.equal(time.nightKey(vn('2026-11-02', '05:30').getTime(), false), '2026-11-02');
});

// ET, LONDON → dịch giờ theo ngày (tính tại 18:00 VN của đêm đó)
const SHIFT_CASES = [
  ['2026-10-24', 0, 0], ['2026-10-25', 0, 1], ['2026-10-31', 0, 1], ['2026-11-01', 1, 1],
  ['2027-03-13', 1, 1], ['2027-03-14', 0, 1], ['2027-03-27', 0, 1], ['2027-03-28', 0, 0]
];
SHIFT_CASES.forEach(([key, us, ldn]) => {
  test('mốc giờ tại ' + key + ': Mỹ +' + us + 'h, London +' + ldn + 'h', () => {
    const s = time.shiftsForNight(key, true);
    assert.equal(s.us, us); assert.equal(s.ldn, ldn);
    assert.equal(time.fmtMin(time.markMin(R.MARKS.nyse, key, true)), us ? '21:30' : '20:30');
    assert.equal(time.fmtMin(time.markMin(R.MARKS.ldnClose, key, true)), ldn ? '23:30' : '22:30');
    assert.equal(time.fmtMin(time.markMin(R.MARKS.thin, key, true)), '23:00');   // múi VN không dịch
    assert.equal(time.fmtMin(time.markMin(R.MARKS.prep, key, true)), '18:00');
    assert.equal(time.fmtMin(time.markMin(R.MARKS.comex, key, true)), us ? '20:20' : '19:20');
    assert.equal(time.markMin(R.MARKS.settle, key, true), 1470 + us * 60);        // 00:30 ET sau nửa đêm
  });
});
test('công tắc dstShift = false: không dịch', () => {
  assert.equal(time.shiftsForNight('2026-11-10', false).us, 0);
  assert.equal(time.fmtMin(time.markMin(R.MARKS.nyse, '2026-11-10', false)), '20:30');
});
test('ngày chuyển giờ: hiện thẻ thông báo', () => {
  const ids = (k) => time.notices(k, true).map((n) => n.id);
  assert.deepEqual(ids('2026-10-24'), []);
  assert.deepEqual(ids('2026-10-25'), ['LDN_SWITCH']);
  assert.deepEqual(ids('2026-11-01'), ['US_WINTER', 'US_SWITCH', 'LDN_SWITCH']);
  assert.deepEqual(ids('2026-11-02'), ['US_WINTER', 'US_SWITCH']);   // thứ Hai: đêm giao dịch đầu tiên sau khi Mỹ đổi giờ (REVIEW-4 mục 1)
  assert.deepEqual(ids('2026-11-08'), ['US_WINTER', 'US_SWITCH']);   // còn hiện suốt tuần đầu mùa đông
  assert.deepEqual(ids('2026-11-09'), ['US_WINTER']);
  assert.deepEqual(ids('2027-03-15'), ['US_SWITCH_BACK']);
  assert.deepEqual(ids('2027-03-14'), ['US_SWITCH_BACK']);
  assert.deepEqual(ids('2027-03-28'), ['LDN_SWITCH_BACK']);
  assert.match(C.notices.US_SWITCH, /19:20 sang 20:20/);
  assert.match(C.notices.US_SWITCH, /IB = 20:20–21:20/);
});
test('khung giờ ±15′ (19:30) và ±5′ (21:00); mùa đông +1h', () => {
  const w = R.defaultWindows(true);
  const hit = (key, hm) => !!time.hitWindow(w, time.nightMinutes(vn(key, hm).getTime(), key), key, true);
  assert.equal(hit('2026-10-13', '19:14'), false);
  assert.equal(hit('2026-10-13', '19:15'), true);
  assert.equal(hit('2026-10-13', '19:45'), true);
  assert.equal(hit('2026-10-13', '19:46'), false);
  assert.equal(hit('2026-10-13', '20:55'), true);
  assert.equal(hit('2026-10-13', '21:06'), false);
  assert.equal(hit('2026-11-10', '19:30'), false);
  assert.equal(hit('2026-11-10', '20:30'), true);
  assert.equal(hit('2026-11-10', '22:03'), true);
});
test('thứ Năm', () => { assert.equal(time.isThursday('2026-10-15'), true); assert.equal(time.isThursday('2026-10-14'), false); });
test('khung giờ kế tiếp và đếm ngược', () => {
  const key = '2026-10-13', w = R.defaultWindows(true);
  const nw = time.nextWindow(w, 20 * 60 + 14, key, true);
  assert.equal(nw.w.id, 'w2100'); assert.equal(nw.startsIn, 41);
  assert.equal(time.nextWindow(w, 22 * 60, key, true), null);
});
test('pha trong đêm (mùa hè)', () => {
  const key = '2026-10-13';
  const ph = (hm) => { const m = time.baseMinute(hm) === null ? 0 : time.baseMinute(hm); return C.phases[time.phaseAt(m, key, true).id]; };
  assert.equal(ph('12:00'), 'Ban ngày');
  assert.equal(ph('18:30'), 'Chuẩn bị');
  assert.equal(ph('19:25'), 'COMEX mở');
  assert.equal(ph('19:40'), 'Giờ tin');
  assert.equal(ph('20:40'), 'NYSE mở');
  assert.equal(ph('21:10'), 'Lõi giao thoa');
  assert.equal(ph('22:40'), 'London đóng');
  assert.equal(ph('23:30'), 'Mỏng dần');
  assert.equal(ph('00:40'), 'Chốt giá ngày');
  assert.equal(ph('04:30'), 'Globex bảo trì');
});
test('dải giờ HT 3.2 không chồng nhau', () => {
  const key = '2026-10-13';
  const b = (hm) => { const x = time.bandAt(time.baseMinute(hm), key, true); return x && C.bands[x.id]; };
  assert.equal(b('18:30'), 'Phá giả'); assert.equal(b('19:19'), 'Phá giả');
  assert.equal(b('19:20'), 'Mở ảo'); assert.equal(b('20:19'), 'Mở ảo');
  assert.equal(b('20:20'), 'Cú phá đáng tin'); assert.equal(b('21:29'), 'Cú phá đáng tin');
  assert.equal(b('21:30'), null); assert.equal(b('17:00'), null);
  const bw = (hm) => { const x = time.bandAt(time.baseMinute(hm), '2026-11-10', true); return x && C.bands[x.id]; };
  assert.equal(bw('19:30'), 'Phá giả'); assert.equal(bw('20:20'), 'Mở ảo'); assert.equal(bw('21:20'), 'Cú phá đáng tin');
});
test('parse và định dạng giờ', () => {
  assert.equal(time.parseHM('20:05'), 1205); assert.equal(time.parseHM('xx'), null);
  assert.equal(time.fmtMin(1500), '01:00'); assert.equal(time.fmtMin(-30), '23:30');
  assert.equal(time.baseMinute('01:00'), 1500);
});

// ---------- thẻ phiên ----------
test('thẻ phiên: chốt cần Q1, Q5, Q6, VWAP tuần, ≥ 1 vùng', () => {
  const card = J.newNight().card;
  assert.deepEqual(J.canLockCard(card).missing, ['q1', 'q5', 'q6', 'vwapW', 'zones']);
  Object.assign(card.answers, { q1: 'D', q5: 'in', q6: 'yes', vwapW: 'above' });
  card.zones.push({ id: 'z1', type: 'vwapW', price: 4180 });
  assert.equal(J.canLockCard(card).ok, true);
});
test('thẻ phiên: vết trước / sau 19:20 (mùa hè)', () => {
  const key = '2026-10-13', n = mk('B');
  const pol = (what, hm) => J.cardEditPolicy(n, what, time.nightMinutes(vn(key, hm).getTime(), key), key, true);
  assert.deepEqual(pol('q6', '19:19'), { log: false, confirm: false });
  assert.equal(pol('vahEu', '19:00').log, false);
  assert.equal(pol('q1', '19:00').log, true);
  assert.equal(pol('q6', '19:20').log, true);
  assert.equal(pol('q6', '19:21').log, true);
});
test('thẻ phiên: mùa đông mốc 20:20', () => {
  const key = '2026-11-10', n = mk('B');
  const pol = (hm) => J.cardEditPolicy(n, 'q6', time.nightMinutes(vn(key, hm).getTime(), key, true), key, true);
  assert.equal(pol('19:30').log, false);
  assert.equal(pol('20:21').log, true);
});
test('thẻ phiên: sửa khi đang canh kèo (sau 19:20) ⇒ cần xác nhận; chưa canh ⇒ không', () => {
  const key = '2026-10-13';
  const n = mk('B');
  const late = time.nightMinutes(vn(key, '20:40').getTime(), key);
  assert.equal(J.cardEditPolicy(n, 'q1', late, key, true).confirm, true);
  n.setup = {};
  assert.equal(J.cardEditPolicy(n, 'q1', late, key, true).confirm, false);
  const early = time.nightMinutes(vn(key, '19:00').getTime(), key);
  assert.equal(J.cardEditPolicy(mk('B'), 'q1', early, key, true).confirm, false);
  n.card.lockedAt = null;
  assert.deepEqual(J.cardEditPolicy(n, 'q1', late, key, true), { log: false, confirm: false });
});
test('thẻ phiên: applyCardEdit ghi lại giờ sửa đúng', () => {
  const key = '2026-10-13', n = mk('B'); n.setup = {};
  const at = vn(key, '20:40');
  J.applyCardEdit(n, 'q1', 'Q1 đổi thành b', at.getTime(), time.nightMinutes(at.getTime(), key), key, true);
  assert.deepEqual(n.card.edits, [{ at: '20:40', what: 'Q1 đổi thành b' }]);
  const early = vn(key, '19:00');
  J.applyCardEdit(n, 'q6', 'Q6', early.getTime(), time.nightMinutes(early.getTime(), key), key, true);
  assert.equal(n.card.edits.length, 1);
});
test('chế độ: đổi chế độ ghi regime.log; chui lại trong ⇒ cân bằng, lần phá kế = 2', () => {
  const n = J.newNight(); const at = vn('2026-10-13', '20:40').getTime();
  J.setRegimeMode(n, 'broken', at);
  n.regime.breakout.step1 = true; n.regime.breakout.step2 = true;
  J.breakoutFailed(n, at + 60000);
  assert.equal(n.regime.mode, 'balanced'); assert.equal(n.regime.breakout.nth, 2); assert.equal(n.regime.breakout.step1, false);
  assert.deepEqual(n.regime.log.map((x) => x.mode), ['broken', 'balanced']);
  J.setRegimeMode(n, 'balanced', at);
  assert.equal(n.regime.log.length, 2);
});
test('đổi kịch bản: giữ C4–C6, xóa C7 và bước Bấm', () => {
  const s = { scenario: 'B', zoneId: 'z1', side: 'buy', c4: 'same', c4num: 5, c5: 'near', c6: 2, c7: { dma: 'flat' }, b1: 'U', b2: 'down', b3: 'ok', slPos: 'right', calc: { entry: 1 } };
  const t = J.changeScenario(s, 'A');
  assert.deepEqual(t, { scenario: 'A', zoneId: 'z1', c4: 'same', c4num: 5, c5: 'near', c6: 2 });
});
