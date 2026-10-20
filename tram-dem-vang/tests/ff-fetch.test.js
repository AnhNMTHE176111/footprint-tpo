'use strict';
// Script Action: .github/scripts/ff-fetch.mjs — chạy với máy chủ giả (FF_URLS), kiểm ghi file / giữ bản cũ khi 429
const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFile } = require('node:child_process');

const SCRIPT = path.resolve(__dirname, '../.github/scripts/ff-fetch.mjs');
const sample = (n) => Array.from({ length: n }, (_, i) => ({ title: 'CPI m/m ' + i, country: 'USD', date: '2026-10-21T08:30:00-04:00', impact: 'High', forecast: '0.3%', previous: '0.4%' }));

function serve(handler) {
  return new Promise((resolve) => { const s = http.createServer(handler); s.listen(0, '127.0.0.1', () => resolve(s)); });
}
function run(urls, out) {
  return new Promise((resolve) => {
    execFile(process.execPath, [SCRIPT, out], { env: Object.assign({}, process.env, { FF_URLS: urls.join(','), FF_RETRIES: '2', FF_WAIT_MS: '10' }) }, (err, stdout) => resolve({ code: err ? err.code : 0, stdout }));
  });
}
const tmp = () => path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'ff-')), 'data', 'ff.json');

test('tải được: ghi { fetchedAt, events } gộp hai feed, sắp theo giờ', async () => {
  const srv = await serve((req, res) => { res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(req.url === '/a' ? sample(2) : [{ title: 'NFP', country: 'USD', date: '2026-10-28T08:30:00-04:00', impact: 'High' }])); });
  const base = 'http://127.0.0.1:' + srv.address().port;
  const out = tmp();
  const r = await run([base + '/a', base + '/b'], out);
  srv.close();
  assert.equal(r.code, 0);
  const j = JSON.parse(fs.readFileSync(out, 'utf8'));
  assert.equal(j.events.length, 3);
  assert.ok(Date.parse(j.fetchedAt) > Date.now() - 60000);
  assert.deepEqual(Object.keys(j.events[0]).sort(), ['actual', 'country', 'date', 'forecast', 'impact', 'previous', 'title']);
});

test('429: giữ nguyên bản cũ, thoát 0', async () => {
  const srv = await serve((req, res) => { res.statusCode = 429; res.end('Rate Limited'); });
  const base = 'http://127.0.0.1:' + srv.address().port;
  const out = tmp(); fs.mkdirSync(path.dirname(out), { recursive: true });
  const old = JSON.stringify({ fetchedAt: '2026-10-21T00:00:00.000Z', events: sample(1) });
  fs.writeFileSync(out, old);
  const r = await run([base + '/a', base + '/b'], out);
  srv.close();
  assert.equal(r.code, 0);
  assert.equal(fs.readFileSync(out, 'utf8'), old);
});

test('một feed lỗi: giữ tin cũ nằm ngoài khoảng của phần tải được', async () => {
  const srv = await serve((req, res) => { if (req.url === '/a') { res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(sample(1))); } else { res.statusCode = 404; res.end('no'); } });
  const base = 'http://127.0.0.1:' + srv.address().port;
  const out = tmp(); fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify({ fetchedAt: '2026-10-21T00:00:00.000Z', events: [{ title: 'NFP', country: 'USD', date: '2026-10-28T08:30:00-04:00', impact: 'High', forecast: '', previous: '', actual: '' }] }));
  await run([base + '/a', base + '/b'], out);
  srv.close();
  const j = JSON.parse(fs.readFileSync(out, 'utf8'));
  assert.deepEqual(j.events.map((e) => e.title).sort(), ['CPI m/m 0', 'NFP']);
});

test('tin không đổi và bản cũ còn mới (< 45′): không ghi lại', async () => {
  const srv = await serve((req, res) => { res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(sample(1))); });
  const base = 'http://127.0.0.1:' + srv.address().port;
  const out = tmp();
  await run([base + '/a'], out);
  const first = fs.readFileSync(out, 'utf8');
  const r = await run([base + '/a'], out);
  srv.close();
  assert.equal(fs.readFileSync(out, 'utf8'), first);
  assert.match(r.stdout, /không ghi/);
});
