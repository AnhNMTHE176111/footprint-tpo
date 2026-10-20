// Trợ giúp cho kiểm thử đầu cuối: mở trang bằng file://, đặt giờ cố định, gieo dữ liệu.
import { createRequire } from 'node:module';
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const J = require('../js/journal.js');
const R = require('../js/rules.js');
const here = dirname(fileURLToPath(import.meta.url));
export const ROOT = resolve(here, '..');
export const URL_INDEX = pathToFileURL(resolve(ROOT, 'index.html')).href;
export const KEY = '2026-10-13';
export const NOW = '2026-10-13T14:30:00Z';   // 21:30 giờ VN (hè): sau khung giờ 21:00, sau 20:30 ⇒ cỡ đủ

export async function launch() { return chromium.launch(); }

const SETTINGS = { theme: 'dark', guideLevel: 'new', capital: 2000, riskPct: 2, dstShift: true, shortcuts: true, lastExportAt: null, sizeAsked: true };

export function ticksAll(scen) { const t = {}; R.tickIds(scen).forEach((x) => { t[x.id] = true; }); return t; }

// kind: 'A' (bias SELL, vùng cho khối A) · 'B' (bias BUY) · 'nocard' · 'wait' (bias CHỜ)
// extra(n): sửa đêm trước khi lưu. Ô chung "nến dài nhất" mặc định chưa tick (e2e tick bằng chuột khi cần)
export function buildState(kind, extra) {
  const n = J.newNight();
  n.t0.touched = true; n.t0.alert = true;
  const sell = { q1: 'D', q5: 'below', vwapW: 'below', q6: 'yes' };
  const buy = { q1: 'D', q5: 'above', vwapW: 'above', q6: 'yes' };
  if (kind === 'A') {
    n.card.answers = sell;
    n.card.zones = [{ id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'hvnW', price: 4195 }, { id: 'z3', type: 'valEu', price: 4185 }, { id: 'z4', type: 'vahEu', price: 4199 }];
    n.card.lockedAt = '19:00';
  } else if (kind === 'B') {
    n.card.answers = buy;
    n.card.zones = [{ id: 'z1', type: 'vwapW', price: 4175 }, { id: 'z2', type: 'valEu', price: 4175.5 }, { id: 'z3', type: 'vahEu', price: 4184 }];
    n.card.lockedAt = '19:00';
  } else if (kind === 'wait') {
    n.card.answers = { q1: 'D', q5: 'below', vwapW: 'near', q6: 'yes' };
    n.card.zones = [{ id: 'z1', type: 'vwapW', price: 4175 }, { id: 'z2', type: 'valEu', price: 4175.5 }];
    n.card.lockedAt = '19:00';
  } else if (kind === 'nocard') {
    n.card.answers = { q1: 'D', q5: 'below', vwapW: 'below', q6: 'yes' };
    n.card.zones = [{ id: 'z1', type: 'vwapW', price: 4175 }];
  }
  if (extra) extra(n);
  return { version: 2, settings: Object.assign({}, SETTINGS), nights: { [KEY]: n } };
}

// khối đã điền sẵn gần đủ (mọi ô tick, đủ số) để test tick nốt bằng chuột
export function blockB(over) {
  return Object.assign({ side: 'buy', zoneId: 'z1', entry: 4177.0, sl: 4174.7, tp: 4183.9, c6: 2.0, ticks: ticksAll('B') }, over || {});
}

// Mở một trang mới với giờ cố định và dữ liệu gieo sẵn (chỉ gieo khi chưa có, để tải lại giữ nguyên)
export async function openPage(browser, state, opts) {
  opts = opts || {};
  const context = await browser.newContext({ viewport: opts.viewport || { width: 1366, height: 768 } });
  await context.route('**/data/ff.json*', (r) => r.fulfill({ status: 200, contentType: 'application/json', body: 'null' }));   // e2e không gọi lịch thật trên Pages; lịch gieo qua localStorage
  const page = await context.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errors.push(m.type() + ': ' + m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  await page.clock.setFixedTime(new Date(opts.now || NOW));
  // lịch tin Forex Factory: mặc định một bản mới, rỗng (không tin) để thanh trạng thái không đỏ; opts.feed = null ⇒ không có lịch; hoặc truyền sự kiện
  const nowMs = new Date(opts.now || NOW).getTime();
  const feed = opts.feed === null ? null : (opts.feed || { fetchedAt: new Date(nowMs - 10 * 60000).toISOString(), events: [] });
  if (feed) await context.addInitScript((f) => { try { localStorage.setItem('tdv.ff.v1', f); } catch (e) { /* bỏ qua */ } }, JSON.stringify(feed));
  if (state) {
    await context.addInitScript((s) => { try { if (!localStorage.getItem('tdv.v1')) localStorage.setItem('tdv.v1', s); } catch (e) { /* bỏ qua */ } }, JSON.stringify(state));
  }
  await page.goto(URL_INDEX);
  await page.waitForSelector('#main .tier');
  return { context, page, errors };
}

export const tick = (scen, id) => `[data-testid="tick-${scen}-${id}"]`;
export const prog = async (page, scen) => (await page.textContent(`[data-testid="prog-${scen}"]`)).trim();

// điền ô số rồi bấm Tab để "chốt" (sự kiện change)
export async function fillNum(page, id, value) {
  const sel = `[data-id="${id}"]`;
  await page.fill(sel, value);
  await page.press(sel, 'Tab');
}
export async function verdict(page) { return page.getAttribute('[data-testid="verdict"]', 'data-verdict'); }
export const seg = (ctl, v) => `[data-ctl="${ctl}"] [data-v="${v}"]`;
export const segIn = (item, v) => `[data-item="${item}"] [data-v="${v}"]`;
