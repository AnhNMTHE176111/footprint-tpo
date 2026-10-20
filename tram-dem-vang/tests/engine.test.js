'use strict';
// Engine v2: ô dùng chung, đếm ô từng khối, ô tự kiểm, chọn ENTRY, ngắt mạch, cỡ lệnh + 5 ca thật A1–A5 thành ca tick tay
const test = require('node:test');
const assert = require('node:assert/strict');
const { mk, go, run, night, card, trade, closed, ticksAll, ANS_BUY, ANS_SELL, ANS_NONE, ANS_WAIT, engine, vn, DATE, SETTINGS } = require('./helpers.js');
const R = require('../js/rules.js');

const common = (r, id) => r.common.filter((x) => x.id === id)[0];
const auto = (r, scen, id) => r.blocks[scen].autoChecks.filter((x) => x.id === id)[0];

// ---------- khung xương ----------
test('đêm trống: bốn khối chưa đủ, số ô đúng theo hình dạng (A, B 18 · C, D 15), không ENTRY', () => {
  const r = engine.evaluate(night({ card: card({}, []) }), vn(DATE, '21:30'), SETTINGS, null, { key: DATE });
  assert.deepEqual(['A', 'B', 'C', 'D'].map((s) => r.blocks[s].total), [18, 18, 15, 15]);
  assert.deepEqual(['A', 'B', 'C', 'D'].map((s) => r.blocks[s].done), [0, 0, 0, 0]);
  assert.equal(r.entry, null); assert.equal(r.focus, null);
  assert.equal(R.SCENARIOS.every((s) => r.blocks[s].complete === false), true);
});
test('đêm nền: mỗi kịch bản ra ENTRY đúng khối, đủ done = total, missing rỗng', () => {
  ['A', 'B', 'C', 'D'].forEach((s) => {
    const r = go(s);
    assert.equal(r.entry && r.entry.scen, s, s);
    assert.equal(r.blocks[s].done, r.blocks[s].total, s);
    assert.deepEqual(r.blocks[s].missing, [], s);
    assert.equal(r.commonOk, true, s);
  });
});
test('thứ tự ô: hướng, vùng, ô tick theo nhóm, giá, ô tự kiểm', () => {
  const r = go('C');
  assert.deepEqual(r.blocks.C.order, ['side', 'zone', 'ctx1', 'ctx2', 'chk1', 'chk2', 'chk3', 'ent1', 'sl1', 'nums', 'zone2', 'slFloor', 'slCap', 'rr', 'size']);
});
test('bỏ một ô tick: missing đúng ô đó, done giảm 1, không ENTRY nhưng không khóa gì', () => {
  const r = go('A', (n) => { delete n.se.blocks.A.ticks.ctx2; });
  assert.deepEqual(r.blocks.A.missing, ['ctx2']);
  assert.equal(r.blocks.A.done, r.blocks.A.total - 1);
  assert.equal(r.entry, null);
});
test('thiếu hướng hoặc vùng: ô chọn tính là thiếu; thiếu giá: ô "nums" thiếu và ô tự kiểm chưa kiểm được (ok null)', () => {
  let r = go('B', (n) => { delete n.se.blocks.B.side; delete n.se.blocks.B.zoneId; });
  assert.deepEqual(r.blocks.B.missing.slice(0, 2), ['side', 'zone']);
  r = go('B', (n) => { delete n.se.blocks.B.entry; });
  assert.ok(r.blocks.B.missing.indexOf('nums') >= 0);
  assert.equal(auto(r, 'B', 'slFloor').ok, null); assert.equal(auto(r, 'B', 'rr').ok, null);
});
test('biên độ nến hơn 20 giá ⇒ nghi gõ nhầm mức giá: ô "nums" chưa đạt, SL chưa kiểm sàn', () => {
  const r = go('B', { block: { c6: 25 } });
  assert.ok(r.blocks.B.missing.indexOf('nums') >= 0);
  assert.equal(auto(r, 'B', 'slFloor').ok, null);
});

// ---------- ô dùng chung ----------
test('chung · Đã chốt thẻ phiên: chưa chốt ⇒ đỏ, ENTRY biến mất nhưng khối vẫn đủ', () => {
  const r = go('B', (n) => { n.card.lockedAt = null; });
  assert.equal(common(r, 'card').ok, false); assert.equal(common(r, 'card').reason, 'card'); assert.equal(common(r, 'card').auto, true);
  assert.equal(r.entry, null); assert.equal(r.blocks.B.complete, true);
});
test('chung · Không trong khung giờ cấm: 21:02 trong khung 21:00 ±5′; 21:06 ra khỏi', () => {
  let r = run(DATE, '21:02', mk('B'));
  assert.equal(common(r, 'news').ok, false); assert.equal(r.entry, null); assert.ok(r.newsHit);
  r = run(DATE, '21:06', mk('B'));
  assert.equal(common(r, 'news').ok, true); assert.equal(r.entry.scen, 'B');
});
test('chung · Chưa tắt máy: 2 lệnh phá luật hoặc 3 SL liên tiếp ⇒ đỏ kèm lý do; hòa / TP reset chuỗi; lệnh luyện mắt không tính', () => {
  const rb = (k, r) => closed(k, r, { flags: ['RULE_BREAK'] });
  let r = go('B', { trades: [rb('SL', -1), rb('TP', 3)] });
  assert.equal(common(r, 'breaker').ok, false); assert.equal(common(r, 'breaker').reason, 'breakerRule'); assert.equal(r.breaker.off, true); assert.equal(r.entry, null);
  assert.equal(go('B', { trades: [rb('TP', 3)] }).entry.scen, 'B');
  const sl = () => closed('SL', -1);
  r = go('B', { trades: [sl(), sl(), sl()] });
  assert.equal(common(r, 'breaker').reason, 'breakerSl'); assert.equal(r.counts.slStreak, 3);
  assert.equal(go('B', { trades: [sl(), sl(), closed('TP', 3), sl()] }).counts.slStreak, 1);
  assert.equal(go('B', { trades: [sl(), sl(), closed('BE', 0), sl()] }).counts.slStreak, 1);
  assert.equal(go('B', { trades: [sl(), sl()] }).common.every((x) => x.ok), true);
  const paper = (k) => closed(k, -1, { flags: ['paper', 'RULE_BREAK'] });
  r = go('B', { trades: [paper('SL'), paper('SL'), paper('SL')] });
  assert.equal(r.breaker.off, false); assert.equal(r.counts.slStreak, 0); assert.equal(r.counts.ruleBreaks, 0);
});
test('chung · Chưa tắt máy: đêm mới về 0', () => {
  const prev = mk('B', { trades: [closed('SL', -1), closed('SL', -1), closed('SL', -1), closed('SL', -1, { flags: ['RULE_BREAK'] }), closed('SL', -1, { flags: ['RULE_BREAK'] })] });
  const r = run('2026-10-14', '21:30', mk('B'), null, { '2026-10-13': prev });
  assert.equal(r.breaker.off, false); assert.equal(r.counts.slStreak, 0); assert.equal(r.counts.ruleBreaks, 0);
});
test('chung · Không có lệnh đang mở: dòng Sổ chưa có kết quả ⇒ đỏ; kể cả lệnh luyện mắt và lệnh qua đêm', () => {
  let r = go('B', { trades: [trade({})] });
  assert.equal(common(r, 'open').ok, false); assert.equal(common(r, 'open').reason, 'open'); assert.equal(r.entry, null); assert.equal(r.opens.length, 1);
  r = go('B', { trades: [trade({ flags: ['paper'] })] });
  assert.equal(common(r, 'open').ok, false);
  const prev = mk('B', { trades: [trade({ id: 'qua-dem' })] });
  r = run('2026-10-14', '21:30', mk('B'), null, { '2026-10-13': prev });
  assert.equal(common(r, 'open').ok, false); assert.equal(r.open.trade.id, 'qua-dem'); assert.equal(r.open.nightKey, '2026-10-13');
  assert.equal(go('B', { trades: [closed('TP', 3)] }).common.every((x) => x.ok), true);
});
test('chung · 3 nến M1 sau nến dài nhất phiên: ô người tick, chưa tick ⇒ chưa ENTRY', () => {
  const r = go('B', (n) => { n.se.common = {}; });
  assert.equal(common(r, 'longest').ok, false); assert.equal(common(r, 'longest').auto, false); assert.equal(r.entry, null);
});
test('ô chung sai không khóa khối: vẫn tick tiếp được, chỉ không có ENTRY', () => {
  const r = go('B', (n) => { n.card.lockedAt = null; n.se.common = {}; });
  assert.equal(r.commonOk, false); assert.equal(r.blocks.B.complete, true); assert.equal(r.entry, null);
});

// ---------- ô tự kiểm của khối ----------
test('tự kiểm · Lần ≤ 2 tại vùng: lần 2 vẫn đạt, lần 3 đỏ; lệnh luyện mắt không tính', () => {
  const at = (k) => closed('SL', -1, { zoneId: 'z1', scenario: 'B' });
  let r = go('B', { trades: [at()] });
  assert.equal(r.blocks.B.nth, 2); assert.equal(auto(r, 'B', 'zone2').ok, true);
  r = go('B', { trades: [at(), at()] });
  assert.equal(r.blocks.B.nth, 3); assert.equal(auto(r, 'B', 'zone2').ok, false); assert.equal(auto(r, 'B', 'zone2').reason, 'zone2'); assert.ok(r.blocks.B.missing.indexOf('zone2') >= 0);
  r = go('B', { trades: [closed('SL', -1, { zoneId: 'z1', flags: ['paper'] }), closed('SL', -1, { zoneId: 'z1', flags: ['paper'] })] });
  assert.equal(auto(r, 'B', 'zone2').ok, true);
  r = go('B', (n) => { delete n.se.blocks.B.zoneId; });
  assert.equal(auto(r, 'B', 'zone2').ok, null);
});
test('tự kiểm · SL ≥ biên độ nến M1 cao nhất 5 nến', () => {
  let r = go('B', { block: { c6: 2.3 } });                       // SL 2,3 = nến 2,3 ⇒ đạt
  assert.equal(auto(r, 'B', 'slFloor').ok, true);
  r = go('B', { block: { c6: 2.4 } });
  assert.equal(auto(r, 'B', 'slFloor').ok, false); assert.equal(auto(r, 'B', 'slFloor').reason, 'slFloor'); assert.equal(r.entry, null);
  r = go('B', { block: { sl: 4178.2 } });                        // buy mà SL trên giá vào
  assert.equal(auto(r, 'B', 'slFloor').ok, false); assert.equal(auto(r, 'B', 'slFloor').reason, 'slSide');
  assert.equal(auto(r, 'B', 'slCap').ok, null); assert.equal(auto(r, 'B', 'rr').ok, null);
});
test('tự kiểm · SL ≤ 4 giá: 4,0 đạt, 4,1 đỏ', () => {
  let r = go('B', { block: { sl: 4173.0, tp: 4189, c6: 2 } });
  assert.equal(auto(r, 'B', 'slCap').ok, true);
  r = go('B', { block: { sl: 4172.9, tp: 4189, c6: 2 } });
  assert.equal(auto(r, 'B', 'slCap').ok, false); assert.equal(auto(r, 'B', 'slCap').reason, 'slCap');
});
test('tự kiểm · R:R ≥ 1:2: TP gần ⇒ đỏ "rr"; vùng kế tiếp quá gần ⇒ đỏ "rrNext"; TP vượt vùng kế tiếp quá 0,5 ⇒ đỏ "tpPast"', () => {
  let r = go('B', { block: { tp: 4180 } });                      // 3/2,3 = 1,3
  assert.equal(auto(r, 'B', 'rr').ok, false); assert.equal(auto(r, 'B', 'rr').reason, 'rr');
  r = go('B', { block: { tp: 4181.7 } });                        // đúng 2R
  assert.equal(auto(r, 'B', 'rr').ok, true);
  r = go('B', (n) => { n.card.zones.push({ id: 'z4', type: 'hvnW', price: 4179 }); });
  assert.equal(auto(r, 'B', 'rr').ok, false); assert.equal(auto(r, 'B', 'rr').reason, 'rrNext');
  r = go('B', (n) => { n.card.zones[2].price = 4182; n.se.blocks.B.tp = 4185; });   // vah 4182: TP 4185 vượt 3
  assert.equal(auto(r, 'B', 'rr').ok, false); assert.equal(auto(r, 'B', 'rr').reason, 'tpPast');
});
test('tự kiểm · TP để trống: lấy TP gợi ý (3R cho A, B; 2R cho C, D; vùng kế tiếp nếu gần hơn)', () => {
  assert.equal(go('B', (n) => { delete n.se.blocks.B.tp; }).blocks.B.calc.tpSuggested, 4183.9);
  assert.equal(go('C', (n) => { delete n.se.blocks.C.tp; }).blocks.C.calc.tpSuggested, 4180.8);
  assert.equal(go('A', (n) => { delete n.se.blocks.A.tp; }).blocks.A.calc.tpSuggested, 4185.8);
  const near = go('B', (n) => { delete n.se.blocks.B.tp; n.card.zones[2].price = 4182.5; });   // vùng kế tiếp 4182,5 gần hơn 3R
  assert.equal(near.blocks.B.calc.tpSuggested, 4182.5);
  assert.equal(near.blocks.B.calc.rr, 2.39);
});
test('tự kiểm · LVN không phải vùng kế tiếp', () => {
  const r = go('A', (n) => { n.card.zones.push({ id: 'z5', type: 'lvn', price: 4190 }); });
  assert.equal(r.blocks.A.calc.nextZone.id, 'z3');
});
test('tự kiểm · đủ vốn cho 1 hợp đồng (QĐ-21): vốn 1000 $ ⇒ cỡ chuẩn 0 ⇒ đỏ; chưa cài vốn ⇒ chưa kiểm', () => {
  let r = run(DATE, '21:30', mk('B'), { dstShift: true, capital: 1000, riskPct: 2 });
  assert.equal(auto(r, 'B', 'size').ok, false); assert.equal(auto(r, 'B', 'size').reason, 'size'); assert.equal(r.blocks.B.calc.size, 0); assert.equal(r.entry, null);
  r = run(DATE, '21:30', mk('B'), { dstShift: true });
  assert.equal(auto(r, 'B', 'size').ok, null); assert.equal(auto(r, 'B', 'size').reason, 'noCapital'); assert.equal(r.blocks.B.calc.size, null);
});
test('ngược bias: hiện ô lý do (bắt buộc), thiếu lý do ⇒ chưa đủ; có lý do ⇒ đủ và cỡ ½', () => {
  const over = { block: { side: 'sell', entry: 4177, sl: 4179.3, tp: 4170.1 } };
  let r = go('B', over);
  assert.equal(r.blocks.B.counter, true); assert.deepEqual(r.blocks.B.missing, ['counter']);
  assert.equal(auto(r, 'B', 'counter').ok, false); assert.equal(auto(r, 'B', 'counter').reason, 'counter'); assert.equal(r.entry, null);
  r = go('B', { block: Object.assign({ reason: ' đỉnh có tail thật ' }, over.block) });
  assert.deepEqual(r.blocks.B.missing, []); assert.equal(r.entry.counter, true); assert.deepEqual(r.entry.halfs, ['COUNTER_BIAS']);
  // cùng chiều bias thì không có ô lý do
  assert.equal(go('B').blocks.B.autoChecks.some((x) => x.id === 'counter'), false);
});

// ---------- chọn ENTRY ----------
function twoBlocks(touchA, touchD) {
  const n = mk('A');
  n.se.blocks.D = { side: 'sell', zoneId: 'z2', entry: 4193.0, sl: 4195.4, tp: 4188.2, c6: 2.0, ticks: ticksAll('D') };
  n.se.touch = { A: touchA, D: touchD }; n.se.last = touchA > touchD ? 'A' : 'D';
  return n;
}
test('nhiều khối cùng đủ: ENTRY là khối người dùng chạm cuối', () => {
  assert.equal(run(DATE, '21:30', twoBlocks(1, 2)).entry.scen, 'D');
  assert.equal(run(DATE, '21:30', twoBlocks(3, 2)).entry.scen, 'A');
});
test('một khối đủ, khối khác đang làm dở ⇒ vẫn ENTRY của khối đủ; focus là khối chạm cuối', () => {
  const n = mk('A');
  n.se.blocks.C = { side: 'buy', ticks: { ctx1: true } }; n.se.touch.C = 5; n.se.last = 'C';
  const r = run(DATE, '21:30', n);
  assert.equal(r.entry.scen, 'A'); assert.equal(r.focus, 'C');
});
test('luyện mắt (cả đêm chỉ xem): ENTRY có cờ paper', () => {
  assert.equal(go('B', { t0: { alert: false } }).entry.paper, true);
  assert.equal(go('B').entry.paper, false);
});
test('ENTRY mang hướng, vùng, số: giá vào, SL, TP, R:R, cỡ lệnh', () => {
  const e = go('B').entry;
  assert.equal(e.side, 'buy'); assert.equal(e.zone.id, 'z1');
  assert.deepEqual([e.calc.entry, e.calc.sl, e.calc.tpUsed, e.calc.slDist, e.calc.rr, e.calc.size], [4177, 4174.7, 4183.9, 2.3, 3, 1]);
});

// ---------- cỡ ½ (QĐ-19, QĐ-21, bảng 2.3) ----------
test('cỡ ½: kịch bản C luôn ½; vùng hạng 2 ở B; bias KHÔNG; ngày có tin lớn; trước 20:30', () => {
  assert.deepEqual(go('C').entry.halfs, ['SCENARIO_C']);
  assert.deepEqual(go('B', (n) => { n.card.zones[0].type = 'hvnW'; }).entry.halfs, ['B_RANK2']);
  assert.deepEqual(go('B', (n) => { n.card.zones[0].type = 'vwapW'; }).entry.halfs, []);
  assert.deepEqual(go('B', { answers: ANS_NONE }).entry.halfs, ['BIAS_NONE']);
  assert.deepEqual(go('B', { t0: { newsDay: true } }).entry.halfs, ['NEWS_DAY']);
  assert.deepEqual(run(DATE, '20:10', mk('B')).entry.halfs, ['BEFORE_2030']);
});
test('cỡ ½ không chia được ⇒ 1 hợp đồng, rủi ro thật nói rõ; vốn lớn ⇒ chia được', () => {
  const r = run(DATE, '20:10', mk('B', (n) => { n.card.zones[0].type = 'hvnW'; }));
  const c = r.entry.calc;
  assert.equal(c.size, 1); assert.equal(c.sizeMinOne, true); assert.equal(c.sizeFull, 1); assert.equal(c.realUsd, 23);
  const big = run(DATE, '20:10', mk('B', (n) => { n.card.zones[0].type = 'hvnW'; }), { dstShift: true, capital: 20000, riskPct: 2 });
  assert.equal(big.entry.calc.size, 8); assert.equal(big.entry.calc.sizeMinOne, false);
});
test('giờ mùa đông: mốc 20:30 thành 21:30', () => {
  assert.deepEqual(run('2026-11-10', '21:29', mk('B')).entry.halfs, ['BEFORE_2030']);
  assert.deepEqual(run('2026-11-10', '21:31', mk('B')).entry.halfs, []);
});

// ---------- cảnh báo ----------
test('cảnh báo chung: trước 20:30 và thẻ ít vùng; không khóa gì', () => {
  const r = run(DATE, '20:10', mk('B', (n) => { n.card.zones = n.card.zones.slice(0, 2); }));
  assert.ok(r.warnings.indexOf('WARN_BEFORE_2030') >= 0); assert.ok(r.warnings.indexOf('WARN_FEW_ZONES') >= 0);
  assert.equal(r.entry.scen, 'B');
});

// ---------- 5 ca thật cũ A1–A5, thành ca tick tay ----------
test('A1 · 6/10 20:24 — A sell, tick đủ ⇒ ENTRY, cỡ ½ vì trước 20:30, R:R 3,33', () => {
  const n = night({ card: card({ q1: 'D', q1w: 'D', q5: 'below', q6: 'yes', vwapW: 'below' }, [
    { id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'pocCluster', price: 4195, priceTo: 4196 }, { id: 'z3', type: 'vahEu', price: 4199 }, { id: 'z4', type: 'valEu', price: 4185 }]) });
  n.se = { blocks: { A: { side: 'sell', zoneId: 'z2', entry: 4193.0, sl: 4195.4, tp: 4185.0, c6: 2.0, ticks: ticksAll('A') } }, common: { longest: true }, touch: { A: 1 }, last: 'A', n: 1 };
  const r = run('2026-10-06', '20:24', n);
  assert.equal(r.bias, 'SELL'); assert.equal(r.entry.scen, 'A'); assert.deepEqual(r.entry.halfs, ['BEFORE_2030']);
  assert.deepEqual([r.entry.calc.slDist, r.entry.calc.rr, r.entry.calc.tpSuggested], [2.4, 3.33, 4185.8]);
});
test('A2 · 12/10 21:27 — A sell hình V, bong bóng ngược: không tick "hồi U" và "bong bóng" ⇒ thiếu đúng 3 ô, không ENTRY', () => {
  const n = night({ card: card({ q1: 'b', q5: 'below', vwapW: 'below', q6: 'yes' }, [
    { id: 'z1', type: 'hvnW', price: 4190 }, { id: 'z2', type: 'valEu', price: 4186 }, { id: 'z3', type: 'vahEu', price: 4196 }]) });
  const t = ticksAll('A'); delete t.chk1; delete t.chk3;
  n.se = { blocks: { A: { side: 'sell', zoneId: 'z1', entry: 4188.0, sl: 4190.3, tp: 4181.0, c6: 2.0, ticks: t } }, common: { longest: true }, touch: { A: 1 }, last: 'A', n: 1 };
  const r = run('2026-10-12', '21:27', n);
  assert.equal(r.bias, 'SELL'); assert.equal(r.entry, null);
  assert.deepEqual(r.blocks.A.missing, ['chk1', 'chk3', 'rr']);
  assert.equal(auto(r, 'A', 'rr').reason, 'rrNext');
});
test('A3 · 1/10 20:47 — A sell, SL ngắn hơn nến 3,3 giá ⇒ thiếu đúng "SL ≥ biên độ nến" và "R:R"; không tick ô SL ⇒ thêm "sl1"', () => {
  const mkA3 = (t) => { const n = night({ card: card({ q1: 'D', q5: 'below', vwapW: 'below', q6: 'yes' }, [
    { id: 'z1', type: 'vwapW', price: 4194.8 }, { id: 'z2', type: 'hvnDay', price: 4193 }, { id: 'z3', type: 'valEu', price: 4188 }]) });
    n.se = { blocks: { A: { side: 'sell', zoneId: 'z2', entry: 4192.7, sl: 4194.8, tp: 4182.7, c6: 3.3, ticks: t } }, common: { longest: true }, touch: { A: 1 }, last: 'A', n: 1 };
    return n; };
  let r = run('2026-10-01', '20:47', mkA3(ticksAll('A')));
  assert.deepEqual(r.blocks.A.missing, ['slFloor', 'rr']);
  assert.equal(r.blocks.A.calc.slDist, 2.1); assert.equal(auto(r, 'A', 'rr').reason, 'tpPast');
  const t = ticksAll('A'); delete t.sl1;
  r = run('2026-10-01', '20:47', mkA3(t));
  assert.deepEqual(r.blocks.A.missing, ['sl1', 'slFloor', 'rr']);
});
test('A4 · 13/10 20:10 — B buy ở cụm POC, tick đủ ⇒ ENTRY ½ (vùng hạng 2 + trước 20:30), 1 hợp đồng', () => {
  const n = night({ card: card({ q1: 'D', q5: 'above', vwapW: 'above', q6: 'yes' }, [
    { id: 'z1', type: 'valEu', price: 4175 }, { id: 'z2', type: 'pocCluster', price: 4175.5 }, { id: 'z3', type: 'vahEu', price: 4184 }, { id: 'z4', type: 'lvn', price: 4172 }]) });
  n.se = { blocks: { B: { side: 'buy', zoneId: 'z2', entry: 4177.0, sl: 4174.7, tp: 4183.9, c6: 2.0, ticks: ticksAll('B') } }, common: { longest: true }, touch: { B: 1 }, last: 'B', n: 1 };
  const r = run('2026-10-13', '20:10', n);
  assert.equal(r.bias, 'BUY'); assert.equal(r.entry.scen, 'B'); assert.deepEqual(r.entry.halfs, ['B_RANK2', 'BEFORE_2030']);
  assert.equal(r.entry.calc.rr, 3); assert.equal(r.entry.calc.size, 1); assert.equal(r.entry.calc.sizeMinOne, true);
});
test('A5 · 5/10 19:25 — B buy, thân + delta "lẫn lộn" ⇒ không tick ô "3 nến giảm dần" ⇒ thiếu đúng 1 ô', () => {
  const n = night({ card: card({ q1: 'D', q5: 'above', vwapW: 'above', q6: 'yes' }, [
    { id: 'z1', type: 'vwapW', price: 4181 }, { id: 'z2', type: 'valEu', price: 4182 }, { id: 'z3', type: 'vahEu', price: 4192 }]) });
  const t = ticksAll('B'); delete t.chk1;
  n.se = { blocks: { B: { side: 'buy', zoneId: 'z1', entry: 4183.0, sl: 4180.5, tp: 4190.5, c6: 2.5, ticks: t } }, common: { longest: true }, touch: { B: 1 }, last: 'B', n: 1 };
  const r = run('2026-10-05', '19:25', n);
  assert.equal(r.entry, null); assert.deepEqual(r.blocks.B.missing, ['chk1']);
  assert.equal(r.blocks.B.done, r.blocks.B.total - 1); assert.deepEqual(r.blocks.B.halfs, ['BEFORE_2030']);
});

// ---------- định nghĩa SL, bias ----------
test('lệnh đóng tính là SL khi R ≤ −0,2 (kể cả đóng tay); hòa và thắng reset chuỗi', () => {
  const is = (k, r) => engine.isSLTrade(closed(k, r));
  assert.equal(is('SL', -1), true); assert.equal(is('MANUAL', -0.2), true); assert.equal(is('MANUAL', -0.1), false);
  assert.equal(is('BE', 0), false); assert.equal(is('TP', 3), false);
  assert.equal(engine.isSLTrade(trade({})), false);
  assert.equal(engine.isSLTrade(trade({ r: undefined, exit: { kind: 'SL' } })), true);   // dữ liệu cũ chưa có R
});
test('bias đi vào kết quả: BUY / SELL / KHÔNG / CHỜ theo thẻ phiên', () => {
  assert.equal(go('B').bias, 'BUY'); assert.equal(go('A').bias, 'SELL');
  assert.equal(go('B', { answers: ANS_NONE }).bias, 'KHÔNG'); assert.equal(go('B', { answers: ANS_WAIT }).bias, 'CHỜ');
});
