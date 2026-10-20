// Kiểm thử đầu cuối vòng 4 (REVIEW-3 + USER-TEST-3): click bằng CHUỘT THẬT (mouse.down, giữ 90 ms, mouse.up) như người dùng.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { launch, openPage, buildState, seg, fillNum, verdict, KEY } from './helpers.mjs';

const require = createRequire(import.meta.url);
const J = require('../js/journal.js');

let browser;
test.before(async () => { browser = await launch(); });
test.after(async () => { await browser.close(); });

async function withPage(state, opts, fn) {
  const o = await openPage(browser, state, opts);
  try { await fn(o); } finally { await o.context.close(); }
}
const NOW_2024 = '2026-10-13T13:24:00Z';       // 20:24 VN (hè): trước 20:30 ⇒ cỡ ½
const NOW_WINTER = '2026-11-03T14:00:00Z';     // 21:00 VN, Mỹ đã sang giờ mùa đông (đêm 03/11)
const stored = (page) => page.evaluate(() => JSON.parse(localStorage.getItem('tdv.v1')));
const wait = (page, ms) => page.waitForTimeout(ms);

// bấm bằng chuột thật: di chuột, nhấn, giữ 90 ms, thả
async function mclick(page, sel) {
  const loc = page.locator(sel).first();
  await loc.scrollIntoViewIfNeeded();
  const b = await loc.boundingBox();
  assert.ok(b, 'không thấy ' + sel);
  await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2);
  await page.mouse.down(); await wait(page, 90); await page.mouse.up();
}
async function toB(page) {   // tầng 3, chọn B, vùng, hướng
  await page.click('[data-tier-btn="3"]');
  await mclick(page, seg('c1', 'B')); await mclick(page, seg('c3', 'z1')); await mclick(page, seg('c2', 'buy'));
}
async function walkB(page) {
  await page.click(seg('c1', 'B'));
  await page.click(seg('c3', 'z1'));
  await page.click(seg('c2', 'buy'));
  await page.click(seg('c4', 'same'));
  await page.click(seg('c5', 'near'));
  await page.click('[data-ctl="c7"] [data-v="flat"]');
  await fillNum(page, 'c6', '2');
  await page.waitForSelector('[data-ctl="b3"]');
  await page.click(seg('b1', 'U'));
  await page.click(seg('b2', 'down'));
  await page.click(seg('b3', 'ok'));
  await fillNum(page, 'entry', '4177');
  await fillNum(page, 'sl', '4174.7');
  await page.click(seg('b5', 'right'));
}
const settle = (page) => page.waitForFunction(() => parseInt(getComputedStyle(document.documentElement).getPropertyValue('--vbar-h'), 10) === document.getElementById('verdict').offsetHeight);

test('v4-1 · gõ số rồi bấm "?" bằng chuột thật: khung "?" còn mở sau 400 ms (không bị vẽ lại làm mất)', async () => {
  await withPage(buildState('B'), null, async ({ page, errors }) => {
    await toB(page);
    await page.fill('[data-id="c6"]', '1,8');                       // gõ, KHÔNG rời ô
    await mclick(page, '[data-ctl="c4"] .help');
    await wait(page, 400);
    assert.equal(await page.locator('[data-ctl="c4"] .pop:not([hidden])').count(), 1);
    assert.equal(await page.getAttribute('[data-ctl="c4"] .help', 'aria-expanded'), 'true');
    assert.equal((await stored(page)).nights[KEY].setup.c6, 1.8);   // số vẫn được lưu
    await mclick(page, '[data-ctl="c4"] .help');                    // bấm lại thì đóng
    await wait(page, 300);
    assert.equal(await page.locator('.pop:not([hidden])').count(), 0);
    assert.deepEqual(errors, []);
  });
});
test('v4-2 · gõ số rồi mở mục thu gọn bằng chuột thật: <details> còn mở sau 400 ms', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await toB(page);
    assert.equal(await page.locator('details.scenfold').count(), 1);
    await page.fill('[data-id="c6"]', '1,8');
    await mclick(page, 'details.scenfold summary');
    await wait(page, 400);
    assert.equal(await page.locator('details.scenfold[open]').count(), 1);
    await mclick(page, 'details.scenfold summary');                  // bấm lại thì đóng
    await wait(page, 300);
    assert.equal(await page.locator('details.scenfold[open]').count(), 0);
  });
});
test('v4-3 · "?" ở thanh trên còn mở khi trang vẽ lại; bấm ra ngoài thì đóng', async () => {
  await withPage(buildState('B'), { now: NOW_2024 }, async ({ page }) => {
    await mclick(page, '.statusbar .help');
    assert.equal(await page.locator('.statusbar .pop:not([hidden])').count(), 1);
    await page.evaluate(() => window.TDV.app.render({ keep: true }));
    await page.evaluate(() => window.TDV.app.render({ keep: false }));
    assert.equal(await page.locator('.statusbar .pop:not([hidden])').count(), 1);
    await mclick(page, '#main .tierhead');
    assert.equal(await page.locator('.pop:not([hidden])').count(), 0);
  });
});
test('v4-4 · thông báo nổi không chặn click: bấm "Kèo mới" rồi bấm NGAY C4 / C1 bằng chuột thật vẫn ăn', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await toB(page);
    await mclick(page, '[data-testid="new-setup"]');
    await page.waitForSelector('.toast-item');
    assert.equal(await page.$eval('.toast-item', (e) => getComputedStyle(e).pointerEvents), 'none');
    const r = await page.$eval('.toast-item', (e) => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; });
    const main = await page.$eval('#main', (e) => { const b = e.getBoundingClientRect(); return b.right; });
    assert.ok(r[0] >= main - 1 || r[3] < 100, 'thông báo nằm giữa vùng nút: ' + r.join(','));   // ở góc, không đè cột nút
    await mclick(page, seg('c1', 'B'));                               // bấm ngay, không chờ toast tắt
    assert.equal((await stored(page)).nights[KEY].setup.scenario, 'B');
    await mclick(page, seg('c4', 'none'));
    assert.equal((await stored(page)).nights[KEY].setup.c4, 'none');
  });
});
test('v4-5 · gõ số rồi nhấn chuột xuống chỗ trống, bấm phím số trước khi nhả: không đổi kịch bản (phím tắt tắt khi vẽ lại hoãn)', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await toB(page);
    await page.fill('[data-id="c6"]', '2');
    await page.mouse.move(20, 400); await page.mouse.down();          // ô c6 mất focus, state ghi, vẽ lại hoãn
    await page.keyboard.press('3');
    await page.keyboard.press('1');
    await page.mouse.up(); await wait(page, 300);
    const s = (await stored(page)).nights[KEY].setup;
    assert.equal(s.scenario, 'B'); assert.equal(s.c6, 2);
    await page.fill('[data-id="c6"]', '2,5');
    await page.keyboard.press('4');                                    // đang ở ô nhập: không chạy phím tắt
    assert.equal(await page.inputValue('[data-id="c6"]'), '2,54');
    assert.equal((await stored(page)).nights[KEY].setup.scenario, 'B');
  });
});

test('v4-6 · tầng 2: đổi hướng phá sau khi công nhận ⇒ bước 1, bước 2 về "Chưa", chế độ không còn "vừa phá"', async () => {
  await withPage(buildState('A'), null, async ({ page }) => {
    await page.click('[data-tier-btn="2"]');
    assert.equal(await page.getAttribute(seg('boStep2', 'true'), 'aria-pressed'), 'true');
    await mclick(page, seg('boDir', 'up'));
    assert.equal(await page.getAttribute(seg('boStep1', 'true'), 'aria-pressed'), 'false');
    assert.equal(await page.getAttribute(seg('boStep2', 'true'), 'aria-pressed'), 'false');
    assert.doesNotMatch(await page.textContent('[data-testid="regime-eff"]'), /vừa phá/);
    const bo = (await stored(page)).nights[KEY].regime.breakout;
    assert.deepEqual([bo.dir, bo.step1, bo.step2, bo.at], ['up', false, false, '21:30']);
    // công nhận lại rồi đổi cạnh: cũng xóa
    await mclick(page, seg('boStep1', 'true')); await mclick(page, seg('boStep2', 'true'));
    assert.match(await page.textContent('[data-testid="regime-eff"]'), /vừa phá/);
    await mclick(page, seg('boEdge', 'z4'));
    assert.equal(await page.getAttribute(seg('boStep2', 'true'), 'aria-pressed'), 'false');
    assert.doesNotMatch(await page.textContent('[data-testid="regime-eff"]'), /vừa phá/);
  });
});

test('v4-7 · Canh đủ ⇒ tự sang Bấm đúng một lần; có nút "Quay lại Canh"; sửa Canh sau đó không nhảy nữa', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]');
    await page.click(seg('c1', 'B')); await page.click(seg('c3', 'z1')); await page.click(seg('c2', 'buy'));
    await page.click(seg('c4', 'same')); await page.click(seg('c5', 'near'));
    await fillNum(page, 'c6', '2');
    await page.click('[data-ctl="c7"] [data-v="flat"]');
    await page.waitForSelector('[data-ctl="b3"]');
    assert.equal(await page.locator('[data-testid="back-canh"]').count(), 1);
    await mclick(page, '[data-testid="back-canh"]');
    await page.waitForSelector('[data-ctl="c4"]');
    await fillNum(page, 'c6', ''); await fillNum(page, 'c6', '3');    // Canh thiếu rồi đủ lại
    await wait(page, 200);
    assert.equal(await page.locator('[data-ctl="c4"]').count(), 1);
    assert.equal(await page.locator('[data-ctl="b3"]').count(), 0);
  });
});

test('v4-8 · tầng 5: xóa trắng ô Vốn hoặc Rủi ro ⇒ trả lại số cũ; ô trống không làm mất số hợp đồng', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await page.click('[data-tier-btn="5"]');
    await page.fill('[data-id="capital"]', ''); await page.press('[data-id="capital"]', 'Tab');
    assert.equal(await page.inputValue('[data-id="capital"]'), '2000');
    await page.fill('[data-id="riskpct"]', '0'); await page.press('[data-id="riskpct"]', 'Tab');
    assert.equal(await page.inputValue('[data-id="riskpct"]'), '2');
    const st = await stored(page);
    assert.equal(st.settings.capital, 2000); assert.equal(st.settings.riskPct, 2);
    await page.fill('[data-id="capital"]', '3000'); await page.press('[data-id="capital"]', 'Tab');
    assert.equal((await stored(page)).settings.capital, 3000);
  });
});

test('v4-9 · tầng 0: nút FOMC lấy giờ từ time.js (01:00 hè, 02:00 đông)', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await page.click('[data-tier-btn="0"]');
    assert.match(await page.textContent('.wform'), /Thêm FOMC 01:00/);
  });
  const st = buildState('B'); st.nights['2026-11-03'] = st.nights[KEY];
  await withPage(st, { now: NOW_WINTER }, async ({ page }) => {
    await page.click('[data-tier-btn="0"]');
    assert.match(await page.textContent('.wform'), /Thêm FOMC 02:00/);
  });
});

test('v4-10 · mùa đông (03/11 21:00): bước Bấm đã điền đủ vừa một màn 1366×768; chip "Mỹ mùa đông +1h" thay dòng dài', async () => {
  const st = buildState('B'); st.nights['2026-11-03'] = st.nights[KEY]; delete st.nights[KEY];
  await withPage(st, { now: NOW_WINTER }, async ({ page }) => {
    assert.match(await page.textContent('.statusbar'), /Mỹ mùa đông \+1h/);
    assert.equal(await page.locator('.notice').count(), 0);
    await page.click('[data-tier-btn="3"]'); await walkB(page);
    assert.equal(await verdict(page), 'ENTRY');
    await settle(page);
    const [sh, ih, sbh] = await page.evaluate(() => [document.documentElement.scrollHeight, window.innerHeight, document.getElementById('status').offsetHeight]);
    const parts = await page.evaluate(() => ['#status', '#tiers', '#main', '.vbar', '.vnotes'].map((s) => { const e = document.querySelector(s); return s + '=' + (e ? e.offsetHeight : '-'); }).join(' '));
    assert.ok(sh <= ih, `đông: scrollHeight ${sh} > innerHeight ${ih} ${parts}`);
    assert.ok(sbh <= 60, 'thanh trên mùa đông ' + sbh);
  });
});

test('v4-11 · ENTRY: chữ ≥ 32 px trên máy tính, vẫn vừa một màn; cỡ ½ không chia được nói rủi ro thật', async () => {
  await withPage(buildState('B'), { now: NOW_2024 }, async ({ page }) => {
    await page.click('[data-tier-btn="3"]'); await walkB(page);
    await settle(page);
    const fs = await page.$eval('.ebig', (e) => parseFloat(getComputedStyle(e).fontSize));
    assert.ok(fs >= 32, 'cỡ chữ ENTRY ' + fs);
    assert.match(await page.textContent('[data-testid="entry-text"]'), /1 hợp đồng = cỡ đầy, rủi ro 23 \$/);
    const [sh, ih] = await page.evaluate(() => [document.documentElement.scrollHeight, window.innerHeight]);
    assert.ok(sh <= ih, `scrollHeight ${sh} > innerHeight ${ih}`);
  });
});

test('v4-12 · điện thoại 390 px: thanh trên ≤ 60 px, nút "Trạng thái" mở chip xuống; thanh dưới ENTRY ≤ 120 px; "?" ≥ 40 px', async () => {
  for (const now of [undefined, NOW_2024]) {
    await withPage(buildState('B'), { viewport: { width: 390, height: 844 }, now }, async ({ page }) => {
      const top = await page.$eval('#status', (e) => e.offsetHeight);
      assert.ok(top <= 60, 'thanh trên ' + top + ' (now=' + now + ')');
      assert.equal(await page.locator('.sbmore .chip:visible').count(), 0);
      await mclick(page, '[data-testid="status-toggle"]');
      assert.ok(await page.locator('.sbmore .chip:visible').count() >= 3);
      assert.equal(await page.$eval('#status', (e) => e.offsetHeight), top);   // khung mở xuống đè lên, không đẩy nội dung
      await mclick(page, '[data-testid="status-toggle"]');
      assert.equal(await page.locator('.sbmore .chip:visible').count(), 0);
      await page.click('[data-tier-btn="3"]'); await walkB(page);
      assert.equal(await verdict(page), 'ENTRY');
      await settle(page);
      const bottom = await page.$eval('#verdict', (e) => e.offsetHeight);
      assert.ok(bottom <= 120, 'thanh dưới ' + bottom + ' (now=' + now + ')');
      const hb = (await page.locator('#main .help').first().boundingBox()).width;
      assert.ok(hb >= 40, 'nút ? ' + hb);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth) <= 390);
    });
  }
});

test('v4-13 · sao chép vùng nằm đầu khối vùng, tự điền giá VWAP tuần vào ô bias, thông báo chỉ nêu mục đã chép', async () => {
  const st = buildState('B', (n) => { n.card.lockedAt = null; n.card.zones = []; n.card.answers = { q1: 'D', q5: 'above', q6: 'yes' }; });
  const prev = J.newNight('2026-10-12'); prev.card.lockedAt = '19:00'; prev.card.answers = {};
  prev.card.zones = [{ id: 'z1', type: 'vwapW', price: 4181 }, { id: 'z2', type: 'hvn3w', price: 4200 }];
  st.nights['2026-10-12'] = prev;
  await withPage(st, null, async ({ page }) => {
    await page.click('[data-tier-btn="1"]');
    const before = await page.evaluate(() => { const c = document.querySelector('[data-testid="copy-prev"]'), z = document.querySelector('.zform'); return !!(c.compareDocumentPosition(z) & Node.DOCUMENT_POSITION_FOLLOWING); });
    assert.equal(before, true);
    await mclick(page, '[data-testid="copy-prev"]');
    assert.equal(await page.inputValue('[data-id="vwapprice"]'), '4181');
    const toast = await page.textContent('.toast-item');
    assert.match(toast, /VWAP tuần 4181,0/); assert.doesNotMatch(toast, /3 tuần \(|Q1/);
  });
});

test('v4-14 · "Giờ phá" có chú thích; trước 18:00 chỉ cảnh báo, không tắt A', async () => {
  await withPage(buildState('A'), null, async ({ page }) => {
    await page.click('[data-tier-btn="2"]');
    assert.equal(await page.locator('.boathint').count(), 1);
    await page.fill('.panel.inner input.field.txt', '14:05'); await page.keyboard.press('Tab');
    await page.waitForSelector('.banner.warn:has-text("ngoài giờ giao dịch")');
    assert.equal(await page.locator('[data-scen="A"].on').count(), 1);
  });
});

test('v4-15 · Sổ: chú giải cột "4 kiểm tra" dưới bảng; chip đủ chữ; Từ điển có VA / VAH / VAL / POC, phá giả, cửa sổ cấm', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    const bar = await page.textContent('.statusbar');
    assert.match(bar, /Phá luật 0 trên 2/); assert.match(bar, /SL liên tiếp 0 trên 3/); assert.match(bar, /Lệnh mở 0 trên 1/);
    await page.click('[data-tier-btn="5"]');
    assert.match(await page.textContent('.legend'), /V\/U nhịp hồi · bb bong bóng/);
    assert.match(await page.textContent('#main'), /Số đêm liên tiếp không phá luật/);
    await page.click('[data-testid="glossary-btn"]');
    await page.fill('[data-testid="glossary-search"]', 'vah');
    assert.ok((await page.$$eval('.glossary dt:not([hidden])', (els) => els.map((e) => e.textContent))).includes('VA / VAH / VAL / POC'));
    await page.fill('[data-testid="glossary-search"]', 'pha gia');
    assert.ok((await page.$$eval('.glossary dt:not([hidden])', (els) => els.map((e) => e.textContent))).includes('phá giả'));
    await page.fill('[data-testid="glossary-search"]', 'cua so cam');
    assert.match(await page.textContent('.glossary dd:not([hidden])'), /19:30.*21:00/);
  });
});

test('v4-16 · thiếu vốn ⇒ CHỜ "Cài vốn", bấm vào mở hộp vốn', async () => {
  const st = buildState('B'); st.settings.capital = null;
  await withPage(st, null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]'); await walkB(page);
    assert.equal(await verdict(page), 'WAIT');
    assert.equal(await page.locator('[data-testid="btn-capital"]').count(), 1);   // nút "Đổi vốn" cũng có ở trạng thái CHỜ
    await mclick(page, '[data-code="WAIT_CAPITAL"]');
    await page.waitForSelector('[data-testid="capital-dlg"]');
    await page.fill('[data-id="cap-dlg"]', '2000'); await mclick(page, '[data-testid="cap-save"]');
    assert.equal(await verdict(page), 'ENTRY');
  });
});
