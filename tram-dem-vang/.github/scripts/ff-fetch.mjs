// Tải lịch Forex Factory (thisweek + nextweek) và ghi data/ff.json = { fetchedAt, events }. Không phụ thuộc gói ngoài (Node >= 18).
// Lỗi hoặc 429 ⇒ giữ nguyên data/ff.json cũ và thoát 0 (Action không đỏ, app tự báo "lịch chưa cập nhật" khi cũ quá 2 giờ).
// Chỉ ghi file khi danh sách tin đổi, hoặc bản cũ đã quá 45 phút (để fetchedAt không bị cũ khi lịch đứng yên).
// Dùng:  node .github/scripts/ff-fetch.mjs [đường dẫn ra, mặc định data/ff.json]
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';

const URLS = process.env.FF_URLS ? process.env.FF_URLS.split(',') : [
  'https://nfs.faireconomy.media/ff_calendar_thisweek.json',
  'https://nfs.faireconomy.media/ff_calendar_nextweek.json'
];
const OUT = process.argv[2] || 'data/ff.json';
const RETRIES = Number(process.env.FF_RETRIES || 3);
const WAIT_MS = Number(process.env.FF_WAIT_MS || 20000);
const REFRESH_MS = 45 * 60000;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function get(url) {
  for (let i = 1; i <= RETRIES; i++) {
    try {
      const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0 (tram-dem-vang)', Accept: 'application/json' } });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length) return data;
        console.log(`${url}: rỗng hoặc sai dạng`);
      } else console.log(`${url}: HTTP ${res.status} (lần ${i}/${RETRIES})`);
    } catch (e) { console.log(`${url}: ${e.message} (lần ${i}/${RETRIES})`); }
    if (i < RETRIES) await sleep(WAIT_MS);
  }
  return null;
}

const clean = (e) => ({
  title: String(e.title || ''), country: String(e.country || ''), date: String(e.date || ''), impact: String(e.impact || ''),
  forecast: e.forecast == null ? '' : String(e.forecast), previous: e.previous == null ? '' : String(e.previous), actual: e.actual == null ? '' : String(e.actual)
});
const key = (e) => `${e.country}|${e.title}|${Date.parse(e.date) || e.date}`;

let old = null;
if (existsSync(OUT)) { try { old = JSON.parse(readFileSync(OUT, 'utf8')); } catch { old = null; } }

const got = [];
for (const u of URLS) got.push(await get(u));
if (got.every((g) => !g)) { console.log('Không tải được feed nào — giữ data/ff.json cũ.'); process.exit(0); }

const fresh = new Map();
let lo = Infinity, hi = -Infinity;
got.forEach((g) => (g || []).forEach((raw) => {
  const e = clean(raw); const t = Date.parse(e.date);
  if (!e.title || !isFinite(t)) return;
  fresh.set(key(e), e); lo = Math.min(lo, t); hi = Math.max(hi, t);
}));
// feed nào lỗi: giữ tin cũ nằm ngoài khoảng thời gian của phần vừa tải được
if (got.some((g) => !g) && old && Array.isArray(old.events)) {
  old.events.forEach((e) => { const t = Date.parse(e.date); if (isFinite(t) && (t < lo || t > hi) && !fresh.has(key(e))) fresh.set(key(e), clean(e)); });
}
const events = [...fresh.values()].sort((a, b) => Date.parse(a.date) - Date.parse(b.date) || (a.title < b.title ? -1 : 1));
if (!events.length) { console.log('Feed không có tin hợp lệ — giữ bản cũ.'); process.exit(0); }

const sameEvents = old && JSON.stringify(old.events) === JSON.stringify(events);
const oldAge = old && Date.parse(old.fetchedAt) ? Date.now() - Date.parse(old.fetchedAt) : Infinity;
if (sameEvents && oldAge < REFRESH_MS) { console.log('Tin không đổi, bản cũ còn mới — không ghi.'); process.exit(0); }

mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, JSON.stringify({ fetchedAt: new Date().toISOString(), events }, null, 1) + '\n');
console.log(`Đã ghi ${OUT}: ${events.length} tin (${got.map((g) => (g ? 'ok' : 'lỗi')).join(', ')}).`);
