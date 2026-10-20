'use strict';
// QĐ-22: lịch Forex Factory → tin tối nay + khung giờ cấm tự sinh; dự phòng khi lịch cũ; REVIEW-4 mục 3
const test = require('node:test');
const assert = require('node:assert/strict');
const N = require('../js/news.js');
const R = require('../js/rules.js');
const time = require('../js/time.js');
const J = require('../js/journal.js');
const engine = require('../js/engine.js');
const { vn, mk, SETTINGS } = require('./helpers.js');

const KEY = '2026-10-21';   // thứ Tư, Mỹ còn giờ mùa hè (EDT = UTC−4)
const ev = (title, country, date, impact, extra) => Object.assign({ title, country, date, impact, forecast: '', previous: '' }, extra || {});
const feedOf = (events, fetchedAt) => ({ fetchedAt: fetchedAt || '2026-10-21T10:00:00Z', events });
const NOW = vn(KEY, '18:30').getTime();   // 11:30Z, lịch lấy 10:00Z ⇒ 90′ ⇒ còn mới
const night = (events, fetchedAt, now) => N.forNight(feedOf(events, fetchedAt), KEY, now || NOW, true);

test('USD High ⇒ hạng 1 ±15′, giờ đổi sang VN, ngày tin lớn tự bật (CPI)', () => {
  const n = night([ev('CPI m/m', 'USD', '2026-10-21T08:30:00-04:00', 'High', { forecast: '0.3%', previous: '0.4%' })]);
  assert.equal(n.status, 'ok');
  assert.equal(n.windows.length, 1);
  const w = n.windows[0];
  assert.deepEqual([w.at, w.tz, w.rank, w.minutesBefore, w.minutesAfter, w.on], ['19:30', 'VN', 1, 15, 15, true]);
  assert.equal(n.newsDay, true);
  assert.deepEqual([n.events[0].hm, n.events[0].forecast, n.events[0].previous], ['19:30', '0.3%', '0.4%']);
});

test('USD Medium ⇒ hạng 2 ±5′, không bật ngày tin lớn; Low / Holiday bỏ qua', () => {
  const n = night([
    ev('ISM Services PMI', 'USD', '2026-10-21T10:00:00-04:00', 'Medium'),
    ev('Some Low Thing', 'USD', '2026-10-21T09:00:00-04:00', 'Low'),
    ev('Bank Holiday', 'USD', '2026-10-21T09:00:00-04:00', 'Holiday')
  ]);
  assert.equal(n.windows.length, 1);
  assert.deepEqual([n.windows[0].at, n.windows[0].rank, n.windows[0].minutesBefore, n.windows[0].minutesAfter], ['21:00', 2, 5, 5]);
  assert.equal(n.newsDay, false);
  assert.equal(n.events.length, 1);
});

test('EUR / GBP High ⇒ chỉ cảnh báo, không có khung giờ cấm; EUR Medium bỏ qua', () => {
  const n = night([ev('ECB Press Conference', 'EUR', '2026-10-21T08:45:00-04:00', 'High'), ev('German Ifo', 'EUR', '2026-10-21T04:00:00-04:00', 'Medium')]);
  assert.equal(n.windows.length, 0);
  assert.equal(n.events.length, 1);
  assert.equal(n.events[0].warnOnly, true);
  assert.equal(N.hitWarn(n, time.baseMinute('19:45')).country, 'EUR');
  assert.equal(N.hitWarn(n, time.baseMinute('19:00')), null);
});

test('FOMC Statement / Press Conference / Fed Chair ⇒ hạng 1 + đóng sạch trước giờ tin 15′, ngày tin lớn', () => {
  const n = night([ev('FOMC Statement', 'USD', '2026-10-21T14:00:00-04:00', 'High'), ev('FOMC Press Conference', 'USD', '2026-10-21T14:30:00-04:00', 'High')]);
  const [s, p] = n.windows;
  assert.deepEqual([s.at, s.kind, s.rank, s.flatBefore], ['01:00', 'fomc', 1, 15]);
  assert.deepEqual([p.at, p.minutesAfter], ['01:30', 30]);
  assert.equal(n.newsDay, true);
  const dl = time.flatDeadline(R.effectiveWindows({ windows: [] }, KEY, n), time.baseMinute('19:00'), KEY, true);
  assert.equal(time.fmtMin(dl.at), '00:45');
});

test('Non-Farm Employment Change và Core CPI bật ngày tin lớn; FOMC Member Speaks thì không', () => {
  assert.equal(night([ev('Non-Farm Employment Change', 'USD', '2026-10-21T08:30:00-04:00', 'High')]).newsDay, true);
  assert.equal(night([ev('Core CPI m/m', 'USD', '2026-10-21T08:30:00-04:00', 'High')]).newsDay, true);
  assert.equal(night([ev('Unemployment Claims', 'USD', '2026-10-21T08:30:00-04:00', 'High')]).newsDay, false);
  assert.equal(night([ev('FOMC Member Williams Speaks', 'USD', '2026-10-21T10:00:00-04:00', 'Medium')]).newsDay, false);
});

test('đổi múi: cùng 08:30 giờ New York, mùa đông ra 20:30 VN (đúng múi trong feed, không cộng thủ công)', () => {
  const key = '2026-11-04';
  const f = feedOf([ev('CPI m/m', 'USD', '2026-11-04T08:30:00-05:00', 'High')], '2026-11-04T10:00:00Z');
  const n = N.forNight(f, key, vn(key, '18:30').getTime(), true);
  assert.equal(n.windows[0].at, '20:30');
  const z = N.forNight(feedOf([ev('CPI m/m', 'USD', '2026-10-21T12:30:00Z', 'High')]), KEY, NOW, true);   // cùng khoảnh khắc viết theo UTC
  assert.equal(z.windows[0].at, '19:30');
});

test('id ổn định: cùng tin ⇒ cùng id dù số liệu / cách viết múi đổi; khác giờ ⇒ id khác', () => {
  const a = night([ev('CPI m/m', 'USD', '2026-10-21T08:30:00-04:00', 'High')]).windows[0].id;
  const b = night([ev('CPI m/m', 'USD', '2026-10-21T12:30:00Z', 'High', { actual: '0.4%' })]).windows[0].id;
  const c = night([ev('CPI m/m', 'USD', '2026-10-21T08:45:00-04:00', 'High')]).windows[0].id;
  assert.equal(a, b);
  assert.notEqual(a, c);
});

test('tin Tentative / All Day (00:00 hoặc không có giờ) bị bỏ qua và ghi chú nếu là tin USD mạnh', () => {
  const n = night([
    ev('Treasury Secretary Speaks', 'USD', '2026-10-21T00:00:00-04:00', 'High'),
    ev('Fed Chair Tentative', 'USD', '2026-10-21T15:00:00-04:00', 'High'),
    ev('Something', 'USD', '2026-10-21', 'High')
  ]);
  assert.equal(n.windows.length, 0);
  assert.deepEqual(n.skipped.slice().sort(), ['Fed Chair Tentative', 'Something', 'Treasury Secretary Speaks']);
});

test('trạng thái lịch: mới ⇒ ok; cũ hơn 2 giờ ⇒ stale; hỏng ⇒ none; khung giờ tự sinh chỉ dùng khi ok', () => {
  const e = [ev('CPI m/m', 'USD', '2026-10-21T08:30:00-04:00', 'High')];
  assert.equal(night(e, '2026-10-21T10:00:00Z', vn(KEY, '19:00').getTime()).status, 'ok');           // 12:00Z − 10:00Z = 2h đúng ⇒ chưa quá
  assert.equal(night(e, '2026-10-21T09:59:00Z', vn(KEY, '19:00').getTime()).status, 'stale');
  assert.equal(N.forNight(null, KEY, NOW, true).status, 'none');
  assert.equal(N.forNight({ events: 'x' }, KEY, NOW, true).status, 'none');
  const stale = night(e, '2026-10-21T01:00:00Z');
  const wins = R.effectiveWindows({ touched: true, windows: R.defaultWindows(true) }, KEY, stale);
  assert.deepEqual(wins.map((w) => w.id), ['w1930', 'w2100']);   // dự phòng: mặc định cũ, 19:30 thứ Năm
});

test('khi lịch ok: 19:30 mặc định không tự bật nữa; khung tự sinh nối vào; tắt từng khung bằng newsOverrides', () => {
  const n = night([ev('CPI m/m', 'USD', '2026-10-21T08:30:00-04:00', 'High')]);
  const t0 = { touched: true, windows: R.defaultWindows(true) };
  let wins = R.effectiveWindows(t0, KEY, n);
  assert.deepEqual(wins.map((w) => w.id).filter((x) => x === 'w1930'), []);
  assert.equal(wins.length, 2);
  const id = n.windows[0].id;
  wins = R.effectiveWindows(Object.assign({ newsOverrides: { [id]: { on: false, offAt: '19:10' } } }, t0), KEY, n);
  const w = wins.filter((x) => x.id === id)[0];
  assert.deepEqual([w.on, w.offAt], [false, '19:10']);
});

test('engine: CPI 19:30 ⇒ 19:20 trong khung giờ cấm (NO_NEWS_WINDOW) + cỡ ½ vì ngày tin lớn; tắt khung ⇒ hết chặn', () => {
  const n = night([ev('CPI m/m', 'USD', '2026-10-21T08:30:00-04:00', 'High')]);
  const base = () => mk('A', (x) => { x.t0.windows = R.defaultWindows(false); });
  const run = (nightObj, hm, news) => engine.evaluate({ nights: { [KEY]: nightObj }, nightKey: KEY, now: vn(KEY, hm), settings: SETTINGS, news });
  let r = run(base(), '19:20', n);
  assert.ok(r.newsHit && r.newsHit.src === 'ff');
  assert.ok(r.reasons.indexOf('NO_NEWS_WINDOW') >= 0);
  assert.equal(r.newsDay, true);
  assert.ok(r.half.reasons.indexOf('NEWS_DAY') >= 0);
  r = run(base(), '19:10', n);   // trước 19:15 (−15′)
  assert.equal(r.newsHit, null);
  const off = base(); off.t0.newsOverrides = { [n.windows[0].id]: { on: false, offAt: '18:50' } };
  r = run(off, '19:20', n);
  assert.equal(r.newsHit, null);
  // người dùng tắt ngày tin lớn (ghi lại)
  const nd = base(); nd.t0.newsDaySet = true; nd.t0.newsDay = false;
  r = run(nd, '19:10', n);
  assert.equal(r.newsDay, false);
  // không có lịch: không chặn
  r = run(base(), '19:20', null);
  assert.equal(r.newsHit, null);
  assert.equal(r.newsDay, false);
});

test('engine: lịch cũ ⇒ dùng mặc định cũ (thứ Năm 19:30 bật); tin EUR trong khung cảnh báo ⇒ WARN_FX_NEWS', () => {
  const thu = '2026-10-22';
  const stale = N.forNight(feedOf([ev('CPI m/m', 'USD', '2026-10-22T08:30:00-04:00', 'High')], '2026-10-21T01:00:00Z'), thu, vn(thu, '19:20').getTime(), true);
  const x = mk('A', (m) => { m.t0.windows = R.defaultWindows(true); });
  let r = engine.evaluate({ nights: { [thu]: x }, nightKey: thu, now: vn(thu, '19:20'), settings: SETTINGS, news: stale });
  assert.ok(r.newsHit && r.newsHit.id === 'w1930');
  const fx = night([ev('ECB Press Conference', 'EUR', '2026-10-21T08:45:00-04:00', 'High')]);
  r = engine.evaluate({ nights: { [KEY]: mk('A') }, nightKey: KEY, now: vn(KEY, '19:40'), settings: SETTINGS, news: fx });
  assert.ok(r.warnings.indexOf('WARN_FX_NEWS') >= 0);
  assert.equal(r.newsHit, null);
});

test('lưu / đọc bản gần nhất ở localStorage; chọn bản mới hơn', () => {
  const mem = {}; const st = { getItem: (k) => (k in mem ? mem[k] : null), setItem: (k, v) => { mem[k] = String(v); } };
  assert.equal(N.loadStored(st), null);
  const f1 = feedOf([], '2026-10-21T10:00:00Z'), f2 = feedOf([], '2026-10-21T10:15:00Z');
  N.saveStored(st, f1);
  assert.equal(N.loadStored(st).fetchedAt, f1.fetchedAt);
  assert.equal(N.newer(f1, f2), f2);
  assert.equal(N.newer(f2, f1), f2);
  mem[N.KEY_STORE] = '{xxx';
  assert.equal(N.loadStored(st), null);
});

test('REVIEW-4 mục 3 · sửa cạnh / hướng TRƯỚC khi công nhận giữ nguyên giờ phá đã gõ; sau công nhận mới là cú phá mới', () => {
  const now = Date.UTC(2026, 9, 13, 14, 30);   // 21:30 VN
  const n = mk('A', (m) => { m.regime.breakout = { dir: 'down', edgeZoneId: 'z2', at: '19:00', nth: 1, step1: false, step2: false }; });
  assert.equal(J.setBreakoutField(n, 'edgeZoneId', 'z3', now), false);
  assert.deepEqual([n.regime.breakout.edgeZoneId, n.regime.breakout.at], ['z3', '19:00']);
  assert.equal(J.setBreakoutField(n, 'dir', 'up', now), false);
  assert.equal(n.regime.breakout.at, '19:00');
  n.regime.breakout.step1 = true;
  assert.equal(J.setBreakoutField(n, 'dir', 'down', now), true);
  assert.equal(n.regime.breakout.at, '21:30');
});
