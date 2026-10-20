/* Trạm Đêm Vàng — lịch tin Forex Factory (QĐ-22): đổi bản ghi của feed thành tin tối nay + khung giờ cấm tự sinh.
 * Thuần dữ liệu: không đụng DOM, không gọi mạng (phần tải nằm ở main.js). Nguồn feed: data/ff.json do GitHub Actions ghi:
 *   { fetchedAt: ISO, events: [ { title, country, date (ISO có múi), impact, forecast, previous, actual } ] }
 * Giờ của tin luôn lấy từ ISO có múi rồi đổi sang giờ VN; không có chuyện mùa đông / mùa hè thủ công cho tin. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(function (n) { return require('./' + n + '.js'); });
  else { root.TDV = root.TDV || {}; root.TDV.news = factory(function (n) { return root.TDV[n]; }); }
})(this, function (dep) {
  'use strict';
  var time = dep('time');
  var MIN = 60000, STALE_MS = 2 * 3600000;
  var KEY_STORE = 'tdv.ff.v1';

  // tin USD mức cao làm "ngày có tin lớn" (cỡ ½)
  var RE_NEWSDAY = /non-farm|\bnfp\b|\bcpi\b|fomc|federal funds/i;
  // FOMC / họp báo / Chủ tịch Fed: hạng 1 và đóng sạch lệnh trước giờ − 15′
  var RE_FOMC = /fomc statement|fomc press conference|fed chair|federal funds/i;
  var RE_PRESS = /press conference|fed chair/i;

  function hash(s) {
    var h1 = 5381;
    for (var i = 0; i < s.length; i++) h1 = ((h1 * 33) ^ s.charCodeAt(i)) >>> 0;
    return h1.toString(36);
  }
  // id ổn định theo mã tiền + tên + giờ tuyệt đối (không phụ thuộc cách feed viết múi giờ)
  function eventId(country, title, ms) { return 'ff-' + hash(country + '|' + title + '|' + ms); }

  // Bản ghi feed → { ok, ev | reason }. Tin "Tentative" / "All Day" không có giờ thật: feed ghi 00:00 theo múi của nó ⇒ bỏ qua, ghi chú.
  function parseEvent(raw) {
    if (!raw || typeof raw !== 'object' || typeof raw.title !== 'string' || typeof raw.date !== 'string') return { ok: false, reason: 'bad' };
    var m = /T(\d\d):(\d\d)(?::\d\d)?(?:\.\d+)?(Z|[+-]\d\d:?\d\d)?$/.exec(raw.date);
    if (!m || !m[3]) return { ok: false, reason: 'notime', title: raw.title };
    if (m[1] === '00' && m[2] === '00') return { ok: false, reason: 'notime', title: raw.title };
    var ms = Date.parse(raw.date);
    if (!isFinite(ms)) return { ok: false, reason: 'bad' };
    if (/tentative|all day/i.test(raw.title + ' ' + (raw.time || ''))) return { ok: false, reason: 'notime', title: raw.title };
    var country = String(raw.country || '').toUpperCase();
    return { ok: true, ev: {
      id: eventId(country, raw.title, ms), title: raw.title, country: country, impact: String(raw.impact || ''), ms: ms,
      forecast: raw.forecast || '', previous: raw.previous || '', actual: raw.actual || ''
    } };
  }

  // Luật chuyển tin → khung giờ (QĐ-22). Trả về null nếu tin không sinh khung giờ cũng không cần hiển thị.
  function classify(ev) {
    var hi = ev.impact === 'High', med = ev.impact === 'Medium';
    if (ev.country === 'USD' && hi) {
      var fomc = RE_FOMC.test(ev.title);
      return { kind: fomc ? 'fomc' : 'news', rank: 1, before: 15, after: RE_PRESS.test(ev.title) ? 30 : 15, flatBefore: fomc ? 15 : null, newsDay: RE_NEWSDAY.test(ev.title), listed: true };
    }
    if (ev.country === 'USD' && med) return { kind: 'news', rank: 2, before: 5, after: 5, flatBefore: null, newsDay: false, listed: true };
    if ((ev.country === 'EUR' || ev.country === 'GBP') && hi) return { kind: 'warn', rank: 0, before: 15, after: 5, flatBefore: null, newsDay: false, listed: true, warnOnly: true };
    return null;
  }

  function validFeed(feed) {
    return !!feed && typeof feed === 'object' && Array.isArray(feed.events) && typeof feed.fetchedAt === 'string' && isFinite(Date.parse(feed.fetchedAt));
  }

  // Tin của một đêm giao dịch + khung giờ tự sinh. status: 'ok' | 'stale' (cũ hơn 2 giờ nhưng còn phủ đêm này — vẫn dùng) | 'none' (không có / không phủ / hỏng)
  function forNight(feed, key, nowMs, useDst) {
    var out = { status: 'none', fetchedAt: null, ageMin: null, events: [], windows: [], warns: [], newsDay: false, skipped: [] };
    if (!validFeed(feed)) return out;
    var fetched = Date.parse(feed.fetchedAt);
    out.fetchedAt = feed.fetchedAt;
    out.ageMin = Math.round((nowMs - fetched) / MIN);
    out.status = (nowMs - fetched) > STALE_MS ? 'stale' : 'ok';
    // lịch cũ hơn 2 giờ vẫn DÙNG ĐƯỢC nếu phủ tới đêm này (giờ tin trong tuần không đổi, chỉ số "thực tế" có thể chậm);
    // không phủ (lịch tuần trước, hoặc cũ hơn 8 ngày) ⇒ 'none' ⇒ về mốc mặc định
    var lo = Infinity, hi = -Infinity;
    feed.events.forEach(function (r) { var t = Date.parse(r && r.date); if (isFinite(t)) { if (t < lo) lo = t; if (t > hi) hi = t; } });
    var covers = lo === Infinity ? out.status === 'ok' : (nowMs >= lo - 86400000 && nowMs <= hi + 86400000);   // lịch rỗng: chỉ tin khi còn mới
    if (!covers || (nowMs - fetched) > 8 * 86400000) { out.status = 'none'; return out; }
    var seen = {};
    feed.events.forEach(function (raw) {
      var p = parseEvent(raw);
      if (!p.ok) {
        if (p.reason === 'notime' && raw && (raw.country === 'USD' && (raw.impact === 'High' || raw.impact === 'Medium'))) {
          var sk = time.nightKey(Date.parse(raw.date) || 0, useDst);
          if (sk === key) out.skipped.push(raw.title);
        }
        return;
      }
      var ev = p.ev;
      if (time.nightKey(ev.ms, useDst) !== key) return;
      var cls = classify(ev);
      if (!cls) return;
      var nm = time.nightMinutes(ev.ms, key);
      if (nm < 17 * 60 || nm >= 30 * 60) return;
      if (seen[ev.id]) return; seen[ev.id] = true;
      var hm = time.fmtMin(nm);
      var e = { id: ev.id, title: ev.title, country: ev.country, impact: ev.impact, hm: hm, nightMin: nm, forecast: ev.forecast, previous: ev.previous, actual: ev.actual,
        kind: cls.kind, rank: cls.rank, warnOnly: !!cls.warnOnly };
      out.events.push(e);
      if (cls.warnOnly) out.warns.push({ id: ev.id, title: ev.title, country: ev.country, from: nm - cls.before, to: nm + cls.after, center: nm });
      else {
        var w = { id: ev.id, kind: cls.kind, rank: cls.rank, at: hm, tz: 'VN', minutesBefore: cls.before, minutesAfter: cls.after, on: true, src: 'ff', title: ev.title, country: ev.country };
        if (cls.flatBefore !== null) w.flatBefore = cls.flatBefore;
        out.windows.push(w);
      }
      if (cls.newsDay) out.newsDay = true;
    });
    out.events.sort(function (a, b) { return a.nightMin - b.nightMin || (a.title < b.title ? -1 : 1); });
    out.windows.sort(function (a, b) { return time.baseMinute(a.at) - time.baseMinute(b.at); });
    return out;
  }

  // tin kế tiếp chưa tới (cho đếm ngược); chỉ tin USD có khung giờ và tin cảnh báo
  function nextEvent(news, nowMin) {
    var best = null;
    ((news && news.events) || []).forEach(function (e) { if (e.nightMin > nowMin && (!best || e.nightMin < best.nightMin)) best = e; });
    return best;
  }
  // tin cảnh báo (EUR / GBP) đang trúng
  function hitWarn(news, nowMin) {
    var list = (news && (news.status === 'ok' || news.status === 'stale') && news.warns) || [];
    for (var i = 0; i < list.length; i++) if (nowMin >= list[i].from - 1e-9 && nowMin <= list[i].to + 1e-9) return list[i];
    return null;
  }

  // Đọc / ghi bản gần nhất ở localStorage để mở file:// hoặc mất mạng vẫn có lịch
  function loadStored(storage) {
    try { var f = JSON.parse(storage.getItem(KEY_STORE)); return validFeed(f) ? f : null; } catch (e) { return null; }
  }
  function saveStored(storage, feed) {
    try { storage.setItem(KEY_STORE, JSON.stringify(feed)); return true; } catch (e) { return false; }
  }
  // chọn bản mới hơn giữa bản vừa tải và bản đã lưu
  function newer(a, b) {
    if (!validFeed(a)) return validFeed(b) ? b : null;
    if (!validFeed(b)) return a;
    return Date.parse(a.fetchedAt) >= Date.parse(b.fetchedAt) ? a : b;
  }

  return {
    parseEvent: parseEvent, classify: classify, forNight: forNight, nextEvent: nextEvent, hitWarn: hitWarn, eventId: eventId, validFeed: validFeed,
    loadStored: loadStored, saveStored: saveStored, newer: newer, STALE_MS: STALE_MS, KEY_STORE: KEY_STORE
  };
});
