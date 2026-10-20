/* Trạm Đêm Vàng — service worker: chạy không mạng. Cache theo APP_VERSION; deploy.sh tự tăng số phiên bản. */
const APP_VERSION = '2.1.0';
const CACHE = 'tdv-' + APP_VERSION;
const ASSETS = [
  './', 'index.html', 'manifest.webmanifest', 'css/app.css',
  'js/rules.js', 'js/time.js', 'js/news.js', 'js/content.js', 'js/engine.js', 'js/journal.js', 'js/store.js',
  'js/ui/dom.js', 'js/ui/status.js', 'js/ui/zonepick.js', 'js/ui/tier01.js', 'js/ui/tier2.js', 'js/ui/tier3.js', 'js/main.js',
  'icons/icon.svg', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/icon-maskable-512.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS.map((u) => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k.startsWith('tdv-') && k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  if (new URL(req.url).pathname.endsWith('/data/ff.json')) return;   // lịch tin luôn lấy từ mạng, không qua cache của service worker
  e.respondWith(caches.match(req, { ignoreSearch: true }).then((hit) => {
    if (hit) return hit;
    return fetch(req).then((res) => {
      if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
      return res;
    }).catch(() => (req.mode === 'navigate' ? caches.match('index.html') : Response.error()));
  }));
});
