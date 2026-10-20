// Kiểm thử đầu cuối vòng 5: lịch tin Forex Factory (QĐ-22), tầng 0 / 1 / 2 / 3 gọn (QĐ-23, 24, 25), Từ điển, USER-TEST-4.
import test from 'node:test';
import assert from 'node:assert/strict';
import { launch, openPage, buildState, seg, fillNum, verdict, openCanh, KEY } from './helpers.mjs';

let browser;
test.before(async () => { browser = await launch(); });
test.after(async () => { await browser.close(); });

async function withPage(state, opts, fn) {
  const o = await openPage(browser, state, opts);
  try { await fn(o); } finally { await o.context.close(); }
}
const stored = (page) => page.evaluate(() => JSON.parse(localStorage.getItem('tdv.v1')));

// 13/10/2026 (Mỹ giờ mùa hè, EDT = UTC−4): 08:30 EDT = 19:30 VN · 10:00 EDT = 21:00 VN · 14:00 EDT = 01:00 VN hôm sau
const FEED = {
  fetchedAt: '2026-10-13T14:20:00.000Z',
  events: [
    { title: 'CPI m/m', country: 'USD', date: '2026-10-13T08:30:00-04:00', impact: 'High', forecast: '0.3%', previous: '0.4%', actual: '' },
    { title: 'ISM Services PMI', country: 'USD', date: '2026-10-13T10:00:00-04:00', impact: 'Medium', forecast: '52.0', previous: '51.6', actual: '' },
    { title: 'ECB Press Conference', country: 'EUR', date: '2026-10-13T08:45:00-04:00', impact: 'High', forecast: '', previous: '', actual: '' },
    { title: 'Some Low Thing', country: 'USD', date: '2026-10-13T09:00:00-04:00', impact: 'Low', forecast: '', previous: '', actual: '' }
  ]
};

test('v5-1 · tầng 0 tối giản: Tin tối nay tự lấy từ lịch, ≤ 3 thao tác tới "Xong tầng 0"', async () => {
  const st = buildState('B', (n) => { n.t0.touched = false; n.t0.alert = null; });
  await withPage(st, { feed: FEED }, async ({ page, errors }) => {
    await page.click('[data-tier-btn="0"]');
    // chỉ còn: câu tỉnh táo · khối tin · ô kịch bản nền; không có đoạn "Mặc định", câu "tin lớn", form thêm khung giờ
    const txt = await page.innerText('[data-tier="0"]');
    assert.doesNotMatch(txt, /Mặc định: 21:00|Hôm nay có tin lớn|Thêm khung giờ|Ngày tin và kịch bản nền/);
    assert.match(txt, /Tin tối nay/); assert.match(txt, /cập nhật lúc 21:20/);
    const rows = await page.$$eval('[data-news]', (els) => els.map((e) => e.textContent));
    assert.equal(rows.length, 3);                                 // CPI, ISM, ECB; tin Low bị bỏ
    assert.match(rows[0] + rows[1] + rows[2], /19:30/); assert.match(rows.join('|'), /CPI m\/m.*cao.*dự báo 0\.3%.*kỳ trước 0\.4%/);
    assert.match(rows.join('|'), /ECB Press Conference.*chỉ cảnh báo/);
    assert.equal(await page.locator('[data-testid="newsday-tag"]').count(), 1);   // CPI ⇒ đêm có tin lớn (cỡ ½)
    assert.match(await page.textContent('[data-testid="newsday-tag"]'), /Đêm có tin lớn — cỡ ½/);
    assert.equal(await page.locator('.fold.manual[open]').count(), 0);            // "Thêm tay…" gập mặc định
    // 2 thao tác: Có, Xong
    await page.click('[data-ctl="t0alert"] [data-v="true"]');
    await page.click('button:has-text("Xong tầng 0")');
    await page.waitForSelector('[data-tier="1"]');
    assert.deepEqual(errors, []);
  });
});

test('v5-2 · tắt một khung giờ tự sinh ghi lại giờ tắt, giữ qua tải lại; khung giờ cấm chặn đúng lúc', async () => {
  // 19:20 VN: CPI 19:30 ±15′ ⇒ đang trong khung giờ cấm
  const now = '2026-10-13T12:20:00Z';
  const feed = Object.assign({}, FEED, { fetchedAt: '2026-10-13T12:10:00.000Z' });
  await withPage(buildState('B'), { feed, now }, async ({ page }) => {
    assert.match(await page.textContent('.statusbar'), /ĐANG TRONG KHUNG GIỜ CẤM 19:30/);
    await page.click('[data-tier-btn="0"]');
    await page.click('[data-news] .btn.sw >> nth=0');
    await page.click('[data-testid="dlg-ok"]');
    await page.waitForFunction(() => !/ĐANG TRONG KHUNG GIỜ CẤM/.test(document.querySelector('.statusbar').textContent));
    const ov = (await stored(page)).nights[KEY].t0.newsOverrides;
    const ids = Object.keys(ov);
    assert.equal(ids.length, 1); assert.equal(ov[ids[0]].on, false); assert.match(ov[ids[0]].offAt, /^\d\d:\d\d$/);
    await page.reload(); await page.waitForSelector('#main .tier');
    assert.doesNotMatch(await page.textContent('.statusbar'), /ĐANG TRONG KHUNG GIỜ CẤM/);   // id ổn định: trạng thái tắt còn nguyên
  });
});

test('v5-3 · đếm ngược tới tin kế ở thanh trạng thái; lịch cũ nhưng còn phủ đêm này vẫn dùng; lịch tuần trước ⇒ thanh đỏ và mặc định cũ', async () => {
  await withPage(buildState('B'), { feed: Object.assign({}, FEED, { fetchedAt: '2026-10-13T11:20:00.000Z' }), now: '2026-10-13T11:30:00Z' }, async ({ page }) => {
    assert.match(await page.textContent('.statusbar'), /Tin kế 19:30 · CPI m\/m · còn 60′/);
    assert.equal(await page.locator('[data-testid="news-stale"]').count(), 0);
  });
  const stale = Object.assign({}, FEED, { fetchedAt: '2026-10-13T08:00:00.000Z' });
  await withPage(buildState('B'), { feed: stale, now: '2026-10-13T11:30:00Z' }, async ({ page }) => {
    assert.equal(await page.locator('[data-testid="news-stale"]').count(), 0);       // cũ 3,5 giờ nhưng phủ đêm này: vẫn dùng
    assert.match(await page.textContent('.statusbar'), /Tin kế 19:30 · CPI m\/m/);
  });
  await withPage(buildState('B'), { feed: stale, now: '2026-10-21T11:30:00Z' }, async ({ page }) => {
    assert.equal(await page.locator('[data-testid="news-stale"]').count(), 1);       // lịch tuần trước: không phủ ⇒ đỏ
    assert.match(await page.textContent('[data-testid="news-stale"]'), /Không có lịch tin cho đêm nay — tự kiểm Forex Factory/);
    assert.doesNotMatch(await page.textContent('.statusbar'), /Tin kế/);
  });
  await withPage(buildState('B'), { feed: null, now: '2026-10-13T11:30:00Z' }, async ({ page }) => {
    assert.equal(await page.locator('[data-testid="news-stale"]').count(), 1);       // không có lịch cũng đỏ
  });
});

test('v5-4 · tầng 1 từ dữ liệu trống: 6 thao tác (Q1, Q5, hai ô giá, gõ nhanh bốn vùng, Chốt)', async () => {
  await withPage(null, null, async ({ page }) => {
    await page.click('[data-testid="cap-save"]');
    await page.click('[data-ctl="t0alert"] [data-v="true"]'); await page.click('button:has-text("Xong tầng 0")');
    await page.waitForSelector('[data-tier="1"]');
    assert.equal(await page.locator('.ticks input[type="checkbox"]').count(), 0);          // không còn 7 ô tick
    assert.match(await page.textContent('[data-tier="1"]'), /Kẻ trên chart A: High/);
    for (const q of ['q3', 'q4', 'q6', 'q1w', 'q2top', 'q2bot']) assert.equal(await page.locator(`[data-ctl="${q}"]`).count(), 0, q);
    let ops = 0;
    await page.click(seg('q1', 'D')); ops++;
    await page.click(seg('q5', 'below')); ops++;
    await fillNum(page, 'pricenow', '4200'); ops++;
    await fillNum(page, 'vwapprice', '4210'); ops++;
    await page.fill('[data-testid="quick-zones"]', 'vwapw 4205, hvn 4195, val 4185, vah 4199'); await page.press('[data-testid="quick-zones"]', 'Enter'); ops++;
    assert.equal(await page.locator('[data-zone]').count(), 4);
    await page.click('[data-testid="lock-card"]'); ops++;
    await page.waitForSelector('[data-tier="2"]');
    assert.ok(ops <= 10, 'thao tác ' + ops);
    const card = (await stored(page)).nights[KEY].card;
    assert.equal(card.answers.q6, 'yes');                                                   // Q6 suy từ vùng cạnh (VAH / VAL Âu)
    assert.deepEqual(card.zones.map((z) => z.type), ['vwapW', 'hvnW', 'valEu', 'vahEu']);
  });
});

test('v5-5 · tầng 1: hàng thêm nhanh có phía chỉ khi cần; "tail thật?" chỉ hiện ở dòng High / Low hôm qua; ghi chú một ô gập; thẻ phiên không có dòng "—"', async () => {
  await withPage(buildState('B', (n) => { n.card.lockedAt = null; }), null, async ({ page }) => {
    await page.click('[data-tier-btn="1"]');
    await page.selectOption('[data-testid="zone-type"]', 'sp');
    assert.equal(await page.locator('.zform .seg').count(), 1);                              // single print cần phía
    await page.selectOption('[data-testid="zone-type"]', 'vwapW');
    assert.equal(await page.locator('.zform .seg').count(), 0);
    assert.equal(await page.locator('.tailq').count(), 0);
    await page.fill('[data-testid="quick-zones"]', 'high 4210'); await page.press('[data-testid="quick-zones"]', 'Enter');
    assert.equal(await page.locator('.tailq').count(), 1);
    await page.click('.tailq [data-v="true"]');
    assert.equal((await stored(page)).nights[KEY].card.answers.q2top, 'tail');
    assert.equal(await page.locator('.plans[open]').count(), 0);
    const card = await page.textContent('#card');
    assert.doesNotMatch(card, /NỢ|VÙNG CẤM/);                                                // chỉ hiện khi có
    assert.doesNotMatch(card.replace(/—/g, '#'), /Kế hoạch 1|Hủy khi/);
    // sao chép vùng nằm ngay đầu khối vùng
    const first = await page.$eval('section:has(.zform) > *:nth-child(2)', (e) => e.className);
    assert.ok(/copyrow|quickrow/.test(first), first);
  });
});

async function setupState(kind, setup) { return buildState(kind, (n) => { n.setup = setup; }); }
const BAM = {
  A: { st: ['A', { scenario: 'A', c4: 'none', c5: 'near', c6: 2, b1: 'U' }], entry: '4193', sl: '4195.4' },
  B: { st: ['B', { scenario: 'B', zoneId: 'z1', side: 'buy', c4: 'same', c5: 'near', c6: 2, c7: { dma: 'flat' }, b1: 'U', b2: 'down', ext: 4175 }], entry: '4177', sl: '4174.7' },
  C: { st: ['B', { scenario: 'C', zoneId: 'z2', c4: 'none', c5: 'near', c6: 2 }], entry: '4176', sl: '4173.4' },
  D: { st: ['A', { scenario: 'D', zoneId: 'z2', c4: 'none', c5: 'near', c6: 2, c7: { moveSize: 6, deep: 'no' }, b1: 'U', ext: 4195 }], entry: '4193', sl: '4195.4' }
};
for (const k of ['A', 'B', 'C', 'D']) {
  test(`v5-6${k} · bước Bấm kịch bản ${k}: đúng 3 thao tác tới ENTRY; Enter ở ô SL = Vào lệnh; B5 tự kiểm`, async () => {
    const st = await setupState(BAM[k].st[0], BAM[k].st[1]);
    await withPage(st, null, async ({ page }) => {
      await page.click('[data-tier-btn="3"]');
      await page.waitForSelector('[data-testid="bam"]');
      assert.equal(await page.locator('[data-ctl="b5"]').count(), 0);                       // không còn nút 3 trạng thái B5
      assert.equal(await page.locator('[data-testid="canh"].closed').count(), (k === 'C' ? 1 : 1)); // Canh đã đủ ⇒ tự gập
      let ops = 0;
      await page.click(seg('b3', 'ok')); ops++;
      await fillNum(page, 'entry', BAM[k].entry); ops++;
      await page.fill('[data-id="sl"]', BAM[k].sl); ops++;
      await page.press('[data-id="sl"]', 'Enter');                                          // Enter ở ô SL khi ENTRY
      assert.equal(ops, 3);
      await page.waitForSelector('[data-testid="enter-confirm"]');
    });
  });
}

test('v5-7 · SL chưa qua mép vùng + 0,3 ⇒ KHÔNG VÀO đỏ, nói rõ; phím Đ = nến đạt chuẩn; N giữ vùng; ba nút phím hiện mờ', async () => {
  const st = await setupState('A', { scenario: 'A', c4: 'none', c5: 'near', c6: 2, b1: 'U' });
  await withPage(st, null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]');
    await page.evaluate(() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'đ', bubbles: true })));   // bàn phím Việt: Đ
    assert.equal(await page.getAttribute(seg('b3', 'ok'), 'aria-pressed'), 'true');
    await fillNum(page, 'entry', '4193'); await fillNum(page, 'sl', '4195.2');
    assert.equal(await verdict(page), 'NO');
    assert.match(await page.textContent('[data-testid="verdict"]'), /SL chưa qua mép vùng hoặc cực trị cộng 0,3 giá/);
    await fillNum(page, 'sl', '4195.4');
    assert.equal(await verdict(page), 'ENTRY');
    assert.match(await page.textContent('[data-testid="btn-entry"]'), /Enter/);
    assert.match(await page.textContent('[data-testid="new-setup"]'), /N/);
    await page.keyboard.press('Escape');
    await page.keyboard.press('n');
    const s = (await stored(page)).nights[KEY].setup;
    assert.equal(s.scenario, 'A'); assert.equal(s.c6, 2); assert.equal(s.c4, undefined); assert.equal(s.b3, undefined); assert.equal(s.calc, undefined);
  });
});

test('v5-8 · bấm thẻ kịch bản đang tắt: hiện lý do tắt ngay bên dưới, không im lặng', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]');
    await page.click(seg('c1', 'A'));                                  // A tắt: chưa có cú phá (chế độ cân bằng)
    await page.waitForSelector('[data-testid="off-pick"]');
    assert.match(await page.textContent('[data-testid="off-pick"]'), /A · .*Chưa có cú phá/);
  });
});

test('v5-9 · tầng 2: giờ phá tự lấy; sửa cạnh trước khi công nhận KHÔNG đổi giờ phá', async () => {
  await withPage(buildState('B', (n) => { n.regime = { mode: 'broken', thinDir: null, breakout: { dir: 'down', edgeZoneId: 'z1', at: '19:00', nth: 1, step1: false, step2: false }, longestBarUntil: null, log: [] }; }), null, async ({ page }) => {
    await page.click('[data-tier-btn="2"]');
    await page.click(seg('boEdge', 'z2'));
    assert.equal((await stored(page)).nights[KEY].regime.breakout.at, '19:00');
  });
});

test('v5-10 · nhập giá sai bậy bị chặn: limit "41824182" và giá khớp lệch xa báo đỏ, không ghi', async () => {
  await withPage(buildState('B', (n) => { n.setup = { scenario: 'B', zoneId: 'z1', side: 'buy', c4: 'same', c5: 'near', c6: 2, c7: { dma: 'flat' }, b1: 'U', b2: 'down', ext: 4175, b3: 'ok', calc: { entry: 4177, sl: 4174.7 } }; }), null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]');
    await page.click('[data-testid="btn-entry"]');
    await page.click('.modal [data-v="limit"]');
    await page.fill('[data-id="enterprice"]', '41824182');
    await page.click('[data-testid="enter-confirm"]');
    assert.match(await page.textContent('[data-testid="price-err"]'), /quá 6 chữ số/);
    await page.fill('[data-id="enterprice"]', '4177'); await page.click('[data-testid="enter-confirm"]');
    await page.waitForSelector('[data-tier="4"]');
    await page.fill('[data-id="fillprice"]', '4250');
    await page.click('[data-testid="btn-filled"]');
    assert.match(await page.textContent('[data-testid="fill-err"]'), /lệch quá 20 giá/);
    assert.equal((await stored(page)).nights[KEY].open.status, 'pending');
  });
});

test('v5-11 · "Kết phiên" ăn ngay cú bấm đầu sau khi gõ "Bạn cộng"', async () => {
  const st = buildState('B', (n) => { n.trades = []; });
  await withPage(st, null, async ({ page }) => {
    await page.click('[data-tier-btn="5"]');
    await page.fill('[data-id="manual"]', '0');
    await page.click('[data-testid="btn-end-night"]');                   // bấm ngay, không Tab
    await page.waitForFunction(() => document.getElementById('toast').textContent.includes('Đã kết phiên'));
    const n = (await stored(page)).nights[KEY];
    assert.equal(n.tally.manual, 0); assert.ok(n.tally.closedAt);
  });
});

test('v5-12 · không có chữ thô ⟦…⟧ ở cả sáu tầng, ở ca cỡ ½ SL 3 giá và ca chip', async () => {
  const st = buildState('B', (n) => { n.setup = { scenario: 'B', zoneId: 'z1', side: 'buy', c4: 'same', c5: 'near', c6: 2, c7: { dma: 'flat' }, b1: 'U', b2: 'down', ext: 4175, b3: 'ok', calc: { entry: 4177, sl: 4173.9 } }; });
  await withPage(st, { now: '2026-10-13T13:24:00Z' }, async ({ page, errors }) => {   // 20:24: trước 20:30 ⇒ cỡ ½
    for (const t of [0, 1, 2, 3, 5]) {
      await page.click(`[data-tier-btn="${t}"]`, { force: true });
      assert.doesNotMatch(await page.textContent('body'), /⟦/, 'tầng ' + t);
    }
    await page.click('[data-tier-btn="3"]');
    assert.match(await page.textContent('.vnotes'), /Cỡ ½ vì|Lẽ ra cỡ ½ vì/);
    assert.deepEqual(errors, []);
  });
});

test('v5-13 · Từ điển đẹp: thẻ có đệm, thanh cuộn mảnh, ô tìm dính trên, nút X, rộng 420 px; mục đang mở được tô', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await page.click('[data-testid="glossary-btn"]');
    const m = await page.evaluate(() => {
      const modal = document.querySelector('.gloss-modal .modal').getBoundingClientRect();
      const dt = getComputedStyle(document.querySelector('.glossary dt'));
      const dd = getComputedStyle(document.querySelector('.glossary dd'));
      const box = document.querySelector('.glossarybox');
      return { w: Math.round(modal.width), pad: dt.paddingLeft, dtSize: dt.fontSize, ddSize: dd.fontSize, lh: dd.lineHeight, sw: getComputedStyle(box).scrollbarWidth, x: !!document.querySelector('.gclose'), sticky: getComputedStyle(document.querySelector('.ghead')).position };
    });
    assert.equal(m.w, 420); assert.equal(m.dtSize, '15px'); assert.equal(m.ddSize, '14px'); assert.equal(m.sw, 'thin'); assert.equal(m.x, true); assert.equal(m.sticky, 'sticky');
    assert.ok(parseInt(m.pad, 10) >= 12 && parseInt(m.pad, 10) <= 14, m.pad);
    assert.equal(parseFloat(m.lh), 21);                                  // 14 px × 1,5
    const all = await page.$$eval('.glossary dt', (els) => els.map((e) => e.textContent));
    assert.ok(all.some((t) => /SL bị quét/.test(t)));
    assert.ok(all.some((t) => /khung giờ cấm/.test(t)));
    await page.click('.gclose');
    assert.equal(await page.locator('.gloss-modal').count(), 0);
  });
  await withPage(buildState('B'), { viewport: { width: 390, height: 844 } }, async ({ page }) => {
    await page.click('[data-testid="status-toggle"]'); await page.click('[data-testid="glossary-btn"]');
    const w = await page.$eval('.gloss-modal .modal', (e) => Math.round(e.getBoundingClientRect().width));
    assert.equal(w, 390);                                                 // toàn màn hình trên điện thoại
  });
});
