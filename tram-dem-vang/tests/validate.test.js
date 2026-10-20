'use strict';
// Test cho từng mục của VALIDATE-v2 (SAI 1–4, THIẾU 5–11, chữ 12–43) và mục 7 của thiết kế v2:
// ô tự kiểm mới (bias, giá cách vùng, giờ phá), ngược bias chỉ B (tail + 2R), B có ô U/V, D có ô bong bóng, trend thin, 8 câu HT mục 9.
const test = require('node:test');
const assert = require('node:assert/strict');
const { mk, go, run, ANS_NONE, ANS_WAIT, ANS_BUY, ANS_SELL, DATE } = require('./helpers.js');
const C = require('../js/content.js');
const R = require('../js/rules.js');
const engine = require('../js/engine.js');

const auto = (r, scen, id) => r.blocks[scen].autoChecks.filter((x) => x.id === id)[0];
const missing = (r, s) => r.blocks[s].missing;

// ---------- SAI ----------
test('V1 · khối B: chữ nói vào NGƯỢC phe bị hấp thụ (theo phe đang hấp thụ)', () => {
  assert.match(C.scenarios.B.blurb, /Vào ngược phe bị hấp thụ \(theo phe đang hấp thụ\) sau nến xác nhận/);
  assert.doesNotMatch(C.scenarios.B.blurb, /theo phe bị hấp thụ/);
});
test('V2 · công nhận cú phá cần ba bước, ở trợ giúp và Từ điển', () => {
  const g = C.glossary.filter((x) => x.key === 'acceptance')[0];
  [g.def, C.blocks.A.ctx[1].help.text, C.blocks.C.ctx[1].help.text].forEach((t) => {
    assert.match(t, /ba bước/); assert.match(t, /\(1\) nến M5 đóng ngoài cạnh/); assert.match(t, /\(2\) nhịp hồi về cạnh giữ được, không nến M5 nào đóng ngược vào/);
    assert.match(t, /\(3\) tại cú test lại trên M1 có delta cùng chiều phá, hoặc hấp thụ ngược chiều phá/); assert.match(t, /Thiếu bước 2 thì chỉ là chạm/);
  });
  assert.match(C.blocks.A.chk[1].help.text, /Bước 3 của công nhận cú phá/);           // V35
  assert.match(C.blocks.A.ctx[0].help.text, /mở rộng của công cụ theo ca 6\/10/);    // V12, V34
});
test('V3 · B ngược bias: R mục tiêu 2R (không phải 3R), cỡ ½, chữ "ngược bias (2R)"; B cùng chiều bias vẫn 3R; A ngược bias không đổi 3R', () => {
  const over = { block: { side: 'sell', reason: 'tail', tail: true } };
  const r = go('B', over);
  assert.equal(r.blocks.B.targetR, 2); assert.equal(r.entry.targetR, 2);
  assert.deepEqual(r.blocks.B.halfs, ['COUNTER_BIAS']);
  assert.equal(go('B').entry.targetR, 3);
  assert.equal(R.TARGET_R_COUNTER_B, 2);
  assert.match(C.halfText.COUNTER_BIAS, /ngược bias \(2R\)/);
  assert.equal(go('A', { block: { side: 'buy' } }).blocks.A.targetR, 3);   // A ngược bias: ô bias đỏ, R mục tiêu vẫn theo A
  assert.match(C.helps.sl.text, /B ngược bias: 2R/);
});

test('V4 · Từ điển "khung giờ cấm": lịch thật (FOMC sau 30′, lịch cũ vẫn dùng) và mặc định chỉ khi không có lịch', () => {
  const g = C.glossary.filter((x) => x.key === 'khung-gio-cam')[0].def;
  assert.match(g, /họp báo FOMC sau 30′/); assert.match(g, /Lịch cũ hơn 2 giờ mà còn phủ đêm nay thì vẫn dùng/);
  assert.match(g, /Không có lịch thì dùng mặc định: \{news1\} ±15′ vào thứ Năm và \{core\} ±5′/);
  assert.doesNotMatch(g, /Luôn có thêm/);
});

// ---------- THIẾU ----------
test('V5 · giá cách vùng ≤ 1 giá, không ở lưng: ô người tick có mặt ở cả bốn khối (nhóm Kiểm tra, ô cuối)', () => {
  ['A', 'B', 'C', 'D'].forEach((s) => {
    const n = R.BLOCK_SHAPE[s].chk;
    assert.match(C.blocks[s].chk[n - 1].t, /Giá cách vùng ≤ 1 giá, không ở lưng \(hoặc râu nến xác nhận chạm vùng\)/);
    assert.equal(C.blocks[s].chk[n - 1].short, 'cạnh');
    assert.ok(go(s).blocks[s].order.indexOf('chk' + n) >= 0);
  });
  assert.match(C.helps.edge.text, /Đi từ 3 giá trở lên khỏi vùng mà chưa hồi là ở lưng: bỏ kèo/);   // V14
});

test('V6 · khối D có ô bong bóng (chk3) và ô giá cách vùng; thiếu ô thì thiếu đúng ô đó', () => {
  assert.equal(C.blocks.D.chk.length, 4); assert.match(C.blocks.D.chk[2].t, /Bong bóng to gần nhất \(10 nến, ở cực trị\) không đứng phe ngược lệnh, hoặc mức đó đã vỡ/);
  assert.deepEqual(missing(go('D', (n) => { delete n.se.blocks.D.ticks.chk3; }), 'D'), ['chk3']);
});

test('V7 · khối B: ô "đang cân bằng thì vùng ở cạnh range / VA Âu, không ở giữa range"', () => {
  assert.match(C.blocks.B.ctx[3].t, /Nếu đang cân bằng: vùng ở cạnh range \/ VA Âu \(≤ 1 giá\), không ở giữa range/);
  assert.deepEqual(missing(go('B', (n) => { delete n.se.blocks.B.ticks.ctx4; }), 'B'), ['ctx4']);
});
test('V8 · trend thin: ô "không cản tàu" ở B và C (không ở A, D)', () => {
  [['B', 4], ['C', 2]].forEach(([s, i]) => {
    assert.match(C.blocks[s].ctx[i].t, /Không phải trend thin đi ngược lệnh \(không cản tàu\)/);
    assert.deepEqual(missing(go(s, (n) => { delete n.se.blocks[s].ticks['ctx' + (i + 1)]; }), s), ['ctx' + (i + 1)]);
  });
  assert.equal(C.blocks.A.ctx.concat(C.blocks.D.ctx).some((x) => /trend thin/.test(x.t)), false);
});
test('V9 · ô tự kiểm "Bias cho phép kịch bản này": KHÔNG ⇒ chỉ C; CHỜ ⇒ cả bốn đỏ; không khóa khối', () => {
  ['A', 'B', 'D'].forEach((s) => {
    const r = go(s, { answers: ANS_NONE });
    const a = auto(r, s, 'bias');
    // ANS_NONE là bias KHÔNG; hướng của fixture không liên quan vì KHÔNG đỏ trước
    assert.equal(a.ok, false, s); assert.equal(a.reason, 'biasNone', s); assert.equal(r.entry, null, s); assert.equal(r.blocks[s].done, r.blocks[s].total - 1, s);
  });
  let r = go('C', { answers: ANS_NONE });
  assert.equal(auto(r, 'C', 'bias').ok, true); assert.equal(r.entry.scen, 'C');
  ['A', 'B', 'C', 'D'].forEach((s) => {
    r = go(s, { answers: ANS_WAIT });
    assert.equal(auto(r, s, 'bias').ok, false, s); assert.equal(auto(r, s, 'bias').reason, 'biasWait', s); assert.equal(r.entry, null, s);
    assert.equal(r.blocks[s].complete, false, s);
  });
  assert.match(C.autoBad.biasNone, /chỉ fade hai cạnh VA Âu \(khối C\), mục tiêu 2R, cỡ ½\. Không phá hồi/);
  assert.match(C.ui.biasNoneNote, /mục tiêu 2R, cỡ ½\. Không phá hồi/);
});
test('V10 · ngược bias chỉ B, kèm ô tail + lý do; A, C, D ngược bias ⇒ ô bias đỏ "biasCounter"', () => {
  const flip = { A: { side: 'buy', entry: 4194.5, sl: 4192.1 }, C: { side: 'sell', entry: 4176, sl: 4178.4 }, D: { side: 'buy', entry: 4194.5, sl: 4192.1 } };
  ['A', 'C', 'D'].forEach((s) => {
    const r = go(s, { block: Object.assign({ reason: 'lý do' }, flip[s]) });
    assert.equal(r.blocks[s].counter, true, s);
    assert.equal(auto(r, s, 'bias').ok, false, s); assert.equal(auto(r, s, 'bias').reason, 'biasCounter', s); assert.equal(r.entry, null, s);
    assert.equal(r.blocks[s].order.indexOf('tail') >= 0, false, s);
  });
  const b = { side: 'sell', entry: 4177, sl: 4179.3, tp: undefined, reason: 'lý do' };
  let r = go('B', { block: b });
  assert.equal(auto(r, 'B', 'bias').ok, true); assert.deepEqual(missing(r, 'B'), ['tail']); assert.equal(r.entry, null);
  r = go('B', { block: Object.assign({ tail: true }, b) });
  assert.deepEqual(missing(r, 'B'), []); assert.equal(r.entry.counter, true); assert.deepEqual(r.entry.halfs, ['COUNTER_BIAS']);
  assert.match(C.zoneTypes.highY.use, /tail thật hoặc single print cũ đúng phía, cỡ ½, 2R/); assert.match(C.zoneTypes.lowY.use, /tail thật hoặc single print cũ đúng phía, cỡ ½, 2R/);   // V21
});
test('V11 · khối B có ô "Cú test lại hình U, không phải V"', () => {
  assert.match(C.blocks.B.chk[3].t, /Cú test lại hình U, không phải V/);
  assert.deepEqual(missing(go('B', (n) => { delete n.se.blocks.B.ticks.chk4; }), 'B'), ['chk4']);
});

// ---------- ô tự kiểm giờ cú phá (A) ----------
test('mục 7 · giờ phá: tick ô nến M5 lúc 18:30 (trước COMEX) ⇒ đỏ; 19:25 ⇒ đạt; chưa tick ⇒ chưa kiểm; không tick ô giờ nữa', () => {
  const at = (hm) => { const [h, m] = hm.split(':').map(Number); return h * 60 + m; };
  const t = (min) => go('A', (n) => { n.se.blocks.A.ctx1At = min; });
  assert.equal(auto(t(at('18:30')), 'A', 'breakHours').ok, false); assert.equal(auto(t(at('18:30')), 'A', 'breakHours').reason, 'breakHours');
  assert.equal(auto(t(at('19:25')), 'A', 'breakHours').ok, true);
  assert.equal(auto(t(at('18:00')), 'A', 'breakHours').ok, false); assert.equal(auto(t(at('19:20')), 'A', 'breakHours').ok, true);
  assert.equal(auto(go('A', (n) => { delete n.se.blocks.A.ticks.ctx1; }), 'A', 'breakHours').ok, null);
  assert.equal(go('B').blocks.B.autoChecks.some((x) => x.id === 'breakHours'), false);
  // không có ctx1At thì lấy giờ hiện tại: 18:40 ⇒ đỏ
  const n = mk('A'); const r = run(DATE, '18:40', n);
  assert.equal(auto(r, 'A', 'breakHours').ok, false);
});

// ---------- khác ----------
test('B ngược bias hay không: ô "Không ngay sau nến dài nhất" của B bỏ (trùng ô chung); ô chung đảo nghĩa', () => {
  assert.equal(C.blocks.B.ctx.some((x) => /sau nến dài nhất/.test(x.t)), false);
});
test('V20 + SL: luật SL chỉ còn ở Từ điển và nút "?" cạnh thanh ENTRY (C: TP về cạnh đối diện hoặc POC); không có ô SL nào trong khối', () => {
  const g = C.glossary.filter((x) => x.key === 'luat-sl')[0].def;
  assert.match(g, /không chặn ENTRY/); assert.match(g, /sàn nhiễu: SL không ngắn hơn nến M1 lớn nhất trong 5 nến/); assert.match(g, /trần: SL không quá 4 giá/);
  assert.match(g, /R:R ít nhất 1:2/); assert.match(g, /C: cạnh đối diện hoặc POC/); assert.match(g, /B ngược bias: 2R/);
  assert.match(C.helps.sl.text, /không chặn ENTRY/);
  ['A', 'B', 'C', 'D'].forEach((s0) => { assert.equal(C.blocks[s0].sl.length, 0); assert.equal(R.BLOCK_SHAPE[s0].sl, 0); });
});

// ---------- 8 câu HT mục 9 → ô phủ ----------
const HT9 = {
  1: { cover: ['common:card', 'bias', 'counter', 'tail'] },
  2: { cover: ['B:chk5', 'B:ctx1', 'B:ctx4', 'C:ctx1', 'D:chk4', 'A:chk4', 'C:chk4'] },
  3: { cover: ['bias', 'A:ctx1', 'A:ctx2', 'B:ctx2', 'B:ctx5', 'C:ctx2', 'C:ctx3'] },
  4: { cover: ['A:chk1', 'B:chk4', 'D:chk2'] },
  5: { cover: ['A:chk3', 'B:chk2', 'C:chk3', 'D:chk3'] },
  6: { cover: ['B:chk1', 'A:ent1', 'B:ent1', 'C:ent1', 'D:ent1'] },
  7: { cover: ['A:ent1', 'common:longest'] },
  8: { cover: ['zone2', 'glossary:luat-sl', 'help:sl'] }
};
test('8 câu HT mục 9 đều có ô phủ thật trong engine / nội dung (mỗi mã ô trong bảng phải tồn tại)', () => {
  const idsA = go('A').blocks.A.order, idsB = go('B').blocks.B.order, idsC = go('C').blocks.C.order, idsD = go('D').blocks.D.order;
  const all = { A: idsA, B: idsB, C: idsC, D: idsD };
  const b = go('B', { block: { side: 'sell', entry: 4177, sl: 4179.3 } }).blocks.B.order;            // có ô counter + tail
  Object.keys(HT9).forEach((q) => {
    assert.ok(HT9[q].cover.length >= 1);
    HT9[q].cover.forEach((ref) => {
      if (/^glossary:/.test(ref)) { assert.ok(C.glossary.some((x) => x.key === ref.slice(9)), ref); return; }
      if (/^help:/.test(ref)) { assert.ok(C.helps[ref.slice(5)], ref); return; }
      if (/^common:/.test(ref)) { assert.ok(go('B').common.some((x) => 'common:' + x.id === ref), 'câu ' + q + ' ' + ref); return; }
      const m = /^([A-D]):(.+)$/.exec(ref);
      if (m) { assert.ok(all[m[1]].indexOf(m[2]) >= 0, 'câu ' + q + ' ' + ref); return; }
      // mã không kèm khối: phải có ở ít nhất một khối (hoặc ở khối B ngược bias)
      assert.ok(['A', 'B', 'C', 'D'].some((s) => all[s].indexOf(ref) >= 0) || b.indexOf(ref) >= 0, 'câu ' + q + ' ' + ref);
    });
  });
  // ô cuối (nến xác nhận) và ô SL đủ trong mọi khối
  ['A', 'B', 'C', 'D'].forEach((s) => ['ent1', 'bias', 'zone2'].forEach((id) => assert.ok(all[s].indexOf(id) >= 0, s + ' ' + id)));
});

// ---------- chữ LỆCH NHẸ / CHỮ (12–43) ----------
test('V13–V43 · chữ theo đề xuất của biên bản', () => {
  const T = (path, re) => { const v = path.split('.').reduce((o, k) => (o === undefined ? o : o[k]), C); assert.match(String(v), re, path); };
  T('blocks.A.chk.2.t', /Bong bóng to gần nhất \(10 nến, ở cực trị\) không đứng phe ngược lệnh, hoặc mức đó đã vỡ/);       // 13
  T('blocks.A.chk.2.help.text', /Bong bóng ở giữa move: bỏ qua/);
  T('blocks.A.chk.3.t', /hoặc râu nến xác nhận chạm vùng/);                                                                 // 14
  T('blocks.A.chk.1.t', /Tại cạnh: delta cùng chiều phá/);
  assert.match(C.blocks.B.ctx[0].help.text, /Cụm POC xếp hạng 2 theo QĐ-3, quyết định của công cụ, chưa đo/);             // 15
  assert.match(C.glossary.filter((x) => x.key === 'hang')[0].def, /QĐ-3, quyết định của công cụ, chưa đo/);
  T('zoneTypes.hvnDay.rank', /chặn hấp thụ/);                                                                              // 16
  T('zoneTypes.hvnDay.use', /QĐ-15, quyết định của công cụ, chưa đo/); T('zoneTypes.hvnDay.use', /phép đo 1 nghiêng về đi tiếp, phép đo 2 trung tính/);
  T('zoneTypes.hvnW.use', /Hạng 2 \(chưa chắc\): chỉ phép đo 1 ủng hộ, phép đo 2 trung tính/);                              // 17
  T('zoneTypes.vwapW.use', /ô duy nhất dương ở cả hai phép đo/); assert.doesNotMatch(C.zoneTypes.vwapW.use, /tốt nhất đã đo/);   // 18
  T('blocks.B.ent.0.help.text', /Luật cơ chế/); T('blocks.B.ent.0.t', /delta đổi dấu, độ lớn ≥ ½ \|delta\| của nến lớn nhất trong move/);   // 19, 36
  T('zoneTypes.sp.def', /nằm giữa profile/); T('zoneTypes.sp.use', /ngày tăng thì nợ phía trên trả trước/);                // 22
  T('zoneTypes.poorHigh.use', /nên dùng làm mục tiêu/); assert.doesNotMatch(C.zoneTypes.poorLow.use, /Không phải chỗ bắt đảo chiều/);   // 23
  T('zoneTypes.ibHigh.use', /Fade ở IB là quyết định của công cụ, chưa đo/);                                               // 24
  T('ui.manualHelp', /đóng sạch trước tin: quyết định của công cụ theo QĐ-22/);                                           // 25
  T('halfText.NEWS_DAY', /quyết định của công cụ/);                                                                        // 26
  // 27: ngưỡng 0,5 giá của máy tính TP không còn (không có ô số); mục này không còn áp dụng
  assert.match(C.glossary.filter((x) => x.key === 'sl-bi-quet')[0].def, /SL \(hoặc SL đã dời về hòa\) bị chạm/);           // 28
  T('ui.biasNoneNote', /mục tiêu 2R, cỡ ½\. Không phá hồi/);                                                               // 29
  T('blocks.D.chk.0.t', /nến hồi delta theo chiều hồi mà đóng ở nửa ngược chiều hồi/);                                    // 37
  T('blocks.D.chk.1.t', /Hồi hình U, ≥ 3 nến, không phải V/);                                                              // 38
  T('blocks.D.ctx.2.t', /chưa quá 70% move/);                                                                              // 39
  assert.match(C.glossary.filter((x) => x.key === 'fade')[0].def, /^Vào ngược chiều giá vừa chạy \(bắt đảo chiều\)\. Kịch bản C là fade cạnh/);   // 40
  ['move', 'range', 'test-lai'].forEach((k) => assert.equal(C.glossary.filter((x) => x.key === k).length, 1, k));          // 41
  T('zoneTypes.vahEu.def', /vùng quanh POC chứa khoảng 70% khối lượng/); assert.match(C.glossary.filter((x) => x.key === 'va')[0].def, /^VA là vùng quanh POC chứa khoảng 70% khối lượng \(hoặc TPO\) của phiên/);   // 42
  T('zoneTypes.poorHigh.def', /Đỉnh phẳng: mức giá cao nhất có từ 2 TPO, không có tail/);                                  // 43
  // không còn "70 %" kiểu cũ ở bất kỳ chuỗi nào
  assert.equal(/\d %/.test(JSON.stringify(C)), false);
});
