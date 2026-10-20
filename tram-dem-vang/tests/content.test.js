'use strict';
// Chữ: mỗi ô có chữ, mỗi loại vùng có định nghĩa (cùng nguồn với Từ điển), lint chữ chạy sạch
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const C = require('../js/content.js');
const R = require('../js/rules.js');

test('mỗi ô tick của mỗi khối có chữ; số ô khớp hình dạng trong rules', () => {
  R.SCENARIOS.forEach((s) => {
    const shape = R.BLOCK_SHAPE[s];
    R.GROUPS.forEach((g) => assert.equal(C.blocks[s][g].length, shape[g], s + '.' + g));
    R.tickIds(s).forEach((t) => assert.ok(C.itemLabel(s, t.id) && C.itemLabel(s, t.id) !== t.id, s + ' ' + t.id));
    C.blocks[s].chk.forEach((c) => assert.ok(c.short, s + ' thiếu chữ ngắn cho Sổ'));
  });
});
test('mọi ô chọn, ô tự kiểm, ô dùng chung có nhãn; mọi lý do có chữ', () => {
  ['side', 'zone', 'nums', 'counter', 'zone2', 'slFloor', 'slCap', 'rr', 'size'].forEach((id) => assert.ok(C.itemLabels[id], id));
  ['zone2', 'slFloor', 'slSide', 'slCap', 'rr', 'rrNext', 'tpPast', 'counter', 'size', 'noCapital'].forEach((c) => assert.ok(C.autoBad[c], c));
  ['card', 'news', 'breakerRule', 'breakerSl', 'open', 'longest'].forEach((c) => assert.ok(C.commonBad[c], c));
  C.common.forEach((c) => assert.ok(C.itemLabel('A', 'common:' + c.id) === c.label));
  Object.keys(C.ui).forEach((k) => assert.ok(!/⟦/.test(C.ui[k]), k));
});
test('mỗi loại vùng trong bảng luật có nhãn, vai, định nghĩa và cách dùng; Từ điển có đúng một mục cho mỗi loại, cùng chữ', () => {
  assert.deepEqual(Object.keys(C.zoneTypes).sort(), R.ZONE_ORDER.slice().sort());
  assert.equal(R.ZONE_ORDER.length, 18);
  R.ZONE_ORDER.forEach((t) => {
    const z = C.zoneTypes[t];
    assert.ok(z.label && z.rank && z.def.length > 20 && z.use.length > 20, t);
    const g = C.glossary.filter((x) => x.key === 'z-' + t);
    assert.equal(g.length, 1, t);
    assert.ok(g[0].def.indexOf(z.def) === 0 && g[0].def.indexOf(z.use) > 0, t);
  });
  assert.equal(new Set(C.glossary.map((g) => g.key)).size, C.glossary.length);
});
test('nhãn vai giữ đúng bảng 2.3 của Hệ thống', () => {
  const rank = (t) => C.zoneTypes[t].rank;
  assert.equal(rank('vwapW'), 'hạng 1'); assert.equal(rank('vwapD'), 'hạng 2'); assert.equal(rank('hvn3w'), 'cấm fade'); assert.equal(rank('lvn'), 'cấm fade');
  assert.equal(rank('nakedPoc'), 'chỉ mục tiêu'); assert.equal(rank('poorHigh'), 'nợ'); assert.equal(rank('vahEu'), 'cạnh');
});
test('chạy lint:vi: 0 lỗi, không thiếu khóa chữ', () => {
  const out = execFileSync(process.execPath, [path.resolve(__dirname, '../scripts/lint-vi.mjs')], { encoding: 'utf8' });
  assert.match(out, /Kết quả: 0 lỗi/); assert.doesNotMatch(out, /thiếu khóa chữ/);
});
