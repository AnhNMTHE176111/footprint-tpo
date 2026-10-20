// Kiểm thử đầu cuối: tầng 0 (lịch tin Forex Factory) và tầng 1 (6 thao tác dựng thẻ phiên).
import test from 'node:test';
import assert from 'node:assert/strict';
import { launch, openPage, buildState, seg, fillNum, KEY } from './helpers.mjs';

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

