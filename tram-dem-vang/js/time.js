/* Trạm Đêm Vàng — giờ Việt Nam, giờ mùa đông Mỹ / London, pha, khung giờ cấm, nightKey.
 * Mọi mốc của luật viết theo "giờ VN khi Mỹ đang giờ mùa hè". Mốc mang múi gốc:
 *  ET (Mỹ): +1h khi Mỹ giờ mùa đông · LONDON: +1h khi London giờ mùa đông · VN: không đổi.
 * Phút trong đêm = số phút kể từ 00:00 giờ VN của ngày nightKey (có thể > 1440 sau nửa đêm). */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(function (n) { return require('./' + n + '.js'); });
  else { root.TDV = root.TDV || {}; root.TDV.time = factory(function (n) { return root.TDV[n]; }); }
})(this, function (dep) {
  'use strict';
  var H = 3600000, MIN = 60000, VN = 7 * H;

  function pad(n) { return (n < 10 ? '0' : '') + n; }

  function vnParts(ms) {
    var d = new Date(ms + VN);
    return { y: d.getUTCFullYear(), m: d.getUTCMonth() + 1, d: d.getUTCDate(), hh: d.getUTCHours(), mm: d.getUTCMinutes(), ss: d.getUTCSeconds(), dow: d.getUTCDay() };
  }
  function dateStr(p) { return p.y + '-' + pad(p.m) + '-' + pad(p.d); }
  function parseKey(key) { var a = key.split('-'); return { y: +a[0], m: +a[1], d: +a[2] }; }
  function addDays(key, n) {
    var p = parseKey(key);
    var d = new Date(Date.UTC(p.y, p.m - 1, p.d + n));
    return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
  }

  // Chủ nhật thứ n của tháng (monthIdx 0-11) → ngày trong tháng
  function nthSunday(y, monthIdx, n) {
    var first = new Date(Date.UTC(y, monthIdx, 1)).getUTCDay();
    var firstSun = 1 + ((7 - first) % 7);
    return firstSun + (n - 1) * 7;
  }
  function lastSunday(y, monthIdx) {
    var last = new Date(Date.UTC(y, monthIdx + 1, 0));
    return last.getUTCDate() - last.getUTCDay();
  }
  // Mỹ: bắt đầu giờ mùa hè CN thứ 2 của tháng 3 lúc 02:00 EST (07:00 UTC); kết thúc CN đầu tháng 11 lúc 02:00 EDT (06:00 UTC)
  function usDstRange(y) { return { start: Date.UTC(y, 2, nthSunday(y, 2, 2), 7), end: Date.UTC(y, 10, nthSunday(y, 10, 1), 6) }; }
  // London: CN cuối tháng 3 và CN cuối tháng 10, lúc 01:00 UTC
  function londonDstRange(y) { return { start: Date.UTC(y, 2, lastSunday(y, 2), 1), end: Date.UTC(y, 9, lastSunday(y, 9), 1) }; }

  function isUsSummer(ms) { var y = new Date(ms).getUTCFullYear(), r = usDstRange(y); return ms >= r.start && ms < r.end; }
  function isLondonSummer(ms) { var y = new Date(ms).getUTCFullYear(), r = londonDstRange(y); return ms >= r.start && ms < r.end; }
  // useDst === false: luôn dùng đồng hồ mùa hè (công tắc settings.dstShift)
  function usShift(ms, useDst) { return useDst === false ? 0 : (isUsSummer(ms) ? 0 : 1); }
  function londonShift(ms, useDst) { return useDst === false ? 0 : (isLondonSummer(ms) ? 0 : 1); }

  // nightKey: hôm nay nếu đã qua 18:00 ET (05:00 VN hè / 06:00 VN đông), ngược lại hôm qua
  function nightKey(ms, useDst) {
    ms = +ms;
    var p = vnParts(ms);
    var cutoff = 5 * 60 + usShift(ms, useDst) * 60;
    var key = dateStr(p);
    return (p.hh * 60 + p.mm >= cutoff) ? key : addDays(key, -1);
  }
  function nightStartMs(key) { var p = parseKey(key); return Date.UTC(p.y, p.m - 1, p.d) - VN; }
  function nightMinutes(ms, key) { return (+ms - nightStartMs(key)) / MIN; }
  function shiftsForNight(key, useDst) {
    var inst = nightStartMs(key) + 18 * H;
    return { us: usShift(inst, useDst), ldn: londonShift(inst, useDst) };
  }
  function dowOfKey(key) { var p = parseKey(key); return new Date(Date.UTC(p.y, p.m - 1, p.d)).getUTCDay(); }
  function isThursday(key) { return dowOfKey(key) === 4; }

  function parseHM(s) {
    var m = /^(\d{1,2})[:h.](\d{2})$/.exec(String(s || '').trim());
    if (!m) return null;
    return +m[1] * 60 + +m[2];
  }
  // "01:00" → sau nửa đêm của đêm này (1500). Từ 00:00 đến 05:59 tính là sáng hôm sau
  function baseMinute(hm) {
    var v = parseHM(hm);
    if (v === null) return null;
    return v < 6 * 60 ? v + 1440 : v;
  }
  function fmtMin(min) {
    var v = ((Math.round(min) % 1440) + 1440) % 1440;
    return pad(Math.floor(v / 60)) + ':' + pad(v % 60);
  }
  // mốc {at, tz} → phút trong đêm, đã cộng giờ mùa đông
  function markMin(mark, key, useDst) {
    var b = baseMinute(mark.at);
    if (b === null) return null;
    var s = shiftsForNight(key, useDst), add = 0;
    if (mark.tz === 'ET') add = s.us * 60;
    else if (mark.tz === 'LONDON') add = s.ldn * 60;
    return b + add;
  }

  function windowRange(w, key, useDst) {
    var c = markMin({ at: w.at, tz: w.tz || 'ET' }, key, useDst);
    if (c === null) return null;
    return { from: c - (w.minutesBefore || 0), to: c + (w.minutesAfter || 0), center: c };
  }
  // khung giờ cấm đang trúng (biên bao gồm hai đầu); rank: 1/2 hoặc bỏ trống = mọi hạng
  function hitWindow(windows, nowMin, key, useDst, rank) {
    var list = windows || [];
    for (var i = 0; i < list.length; i++) {
      var w = list[i];
      if (!w.on) continue;
      if (rank && w.rank !== rank) continue;
      var r = windowRange(w, key, useDst);
      if (r && nowMin >= r.from - 1e-9 && nowMin <= r.to + 1e-9) return w;
    }
    return null;
  }
  // khung giờ kế tiếp (chưa bắt đầu) → {w, from, startsIn}
  function nextWindow(windows, nowMin, key, useDst) {
    var best = null;
    (windows || []).forEach(function (w) {
      if (!w.on) return;
      var r = windowRange(w, key, useDst);
      if (!r || r.from <= nowMin) return;
      if (!best || r.from < best.from) best = { w: w, from: r.from, to: r.to, startsIn: r.from - nowMin };
    });
    return best;
  }

  // phút nhỏ nhất "đóng sạch trước" cho lệnh còn mở: 19:15 (khung giờ hạng 1 19:30 trừ 15') và 00:45 (FOMC)
  function flatDeadline(windows, nowMin, key, useDst) {
    var best = null;
    (windows || []).forEach(function (w) {
      if (!w.on) return;
      var r = windowRange(w, key, useDst);
      if (!r) return;
      var isFomc = w.kind === 'fomc';
      if (w.rank !== 1 && !isFomc) return;
      var dl = r.from - (isFomc ? 15 : 0);
      if (dl > nowMin - 1e-9 && (!best || dl < best.at)) best = { at: dl, w: w };
    });
    return best;
  }

  // phút tròn kế tiếp + 3 phút (khóa sau nến dài nhất phiên). Trả về epoch ms
  function longestBarUntil(ms) { return (Math.floor(+ms / MIN) + 1) * MIN + 3 * MIN; }

  var PHASES = [
    { id: 'prep', at: '18:00', tz: 'VN' }, { id: 'comex', at: '19:20', tz: 'ET' }, { id: 'news', at: '19:30', tz: 'ET' },
    { id: 'nyse', at: '20:30', tz: 'ET' }, { id: 'core', at: '21:00', tz: 'ET' }, { id: 'ldnclose', at: '22:30', tz: 'LONDON' },
    { id: 'thin', at: '23:00', tz: 'VN' }, { id: 'settle', at: '00:30', tz: 'ET' }, { id: 'maint', at: '04:00', tz: 'ET' },
    { id: 'end', at: '05:00', tz: 'ET' }
  ];
  function phaseAt(nowMin, key, useDst) {
    var list = PHASES.map(function (p) { return { id: p.id, min: markMin(p, key, useDst) }; });
    list.sort(function (a, b) { return a.min - b.min; });
    var cur = { id: 'day', min: -Infinity };
    for (var i = 0; i < list.length; i++) if (nowMin >= list[i].min) cur = list[i];
    return cur;
  }

  // dải giờ HT 3.2 (không chồng nhau): phá giả · mở ảo · cú phá đáng tin
  function bandAt(nowMin, key, useDst) {
    var b1 = 18 * 60, b2 = markMin({ at: '19:20', tz: 'ET' }, key, useDst), b3 = markMin({ at: '20:20', tz: 'ET' }, key, useDst), b4 = markMin({ at: '21:30', tz: 'ET' }, key, useDst);
    if (nowMin >= b1 && nowMin < b2) return { id: 'fake' };
    if (nowMin >= b2 && nowMin < b3) return { id: 'open' };
    if (nowMin >= b3 && nowMin < b4) return { id: 'real' };
    return null;
  }

  // thẻ thông báo giờ mùa đông
  function notices(key, useDst) {
    var out = [], s = shiftsForNight(key, useDst), prev = shiftsForNight(addDays(key, -1), useDst);
    if (s.us === 1) out.push({ id: 'US_WINTER' });
    if (s.us === 1 && prev.us === 0) out.push({ id: 'US_SWITCH' });
    if (s.us === 0 && prev.us === 1) out.push({ id: 'US_SWITCH_BACK' });
    if (s.ldn === 1 && prev.ldn === 0) out.push({ id: 'LDN_SWITCH' });
    if (s.ldn === 0 && prev.ldn === 1) out.push({ id: 'LDN_SWITCH_BACK' });
    return out;
  }

  // giờ dùng trong chữ hiển thị, đã cộng giờ mùa đông: {comex} {nyse} {real1} {real2} {fomcFlat}
  function textVars(key, useDst) {
    var f = function (at, tz) { return fmtMin(markMin({ at: at, tz: tz }, key, useDst)); };
    return { comex: f('19:20', 'ET'), nyse: f('20:30', 'ET'), real1: f('20:20', 'ET'), real2: f('21:30', 'ET'), news1: f('19:30', 'ET'), core: f('21:00', 'ET'),
      fomcFlat: fmtMin(markMin({ at: '01:00', tz: 'ET' }, key, useDst) - 15) };
  }

  function weekKey(key) {
    // tuần bắt đầu thứ Hai: trả về nightKey của thứ Hai
    var dow = dowOfKey(key);
    return addDays(key, -((dow + 6) % 7));
  }

  return {
    pad: pad, vnParts: vnParts, dateStr: dateStr, parseKey: parseKey, addDays: addDays,
    nthSunday: nthSunday, lastSunday: lastSunday, usDstRange: usDstRange, londonDstRange: londonDstRange,
    isUsSummer: isUsSummer, isLondonSummer: isLondonSummer, usShift: usShift, londonShift: londonShift,
    nightKey: nightKey, nightStartMs: nightStartMs, nightMinutes: nightMinutes, shiftsForNight: shiftsForNight,
    dowOfKey: dowOfKey, isThursday: isThursday, parseHM: parseHM, baseMinute: baseMinute, fmtMin: fmtMin,
    markMin: markMin, windowRange: windowRange, hitWindow: hitWindow, nextWindow: nextWindow, flatDeadline: flatDeadline,
    longestBarUntil: longestBarUntil, phaseAt: phaseAt, bandAt: bandAt, notices: notices, weekKey: weekKey, textVars: textVars,
    PHASES: PHASES, MIN: MIN
  };
});
