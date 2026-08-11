#!/usr/bin/env python3
"""Lịch tin Forex Factory cho XAUUSD — dùng trong bản tín hiệu đầu ngày.

Nguồn: feed JSON công khai của Forex Factory (nfs.faireconomy.media).
Lọc: tin USD (đồng tiền định giá vàng) + các tin có tác động mạnh lên vàng.
Giờ in ra: giờ Việt Nam (UTC+7).

Dùng:
    python3 ff_news.py            # tin hôm nay
    python3 ff_news.py --week     # cả tuần
    python3 ff_news.py --date 2026-08-13
"""
import argparse
import datetime as dt
import json
import os
import time
import urllib.request

URL_WEEK = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
VN = dt.timezone(dt.timedelta(hours=7))

# Tiền tệ quan tâm khi trade vàng: USD là chính, EUR/GBP tin đỏ cũng làm vàng động.
CCY_MAIN = {"USD"}
CCY_SUB = {"EUR", "GBP"}

# Tin USD nào cũng đỏ nhưng mức nguy hiểm khác nhau -> gắn nhãn riêng.
TOP_TIER = ("Non-Farm", "Federal Funds", "FOMC Statement", "CPI m/m", "CPI y/y",
            "Core CPI", "FOMC Press Conference", "Fed Chair")


CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ff_cache.json")
CACHE_TTL = 3600  # giây — feed chặn 429 nếu gọi dày, nên cache 1 tiếng


def fetch(url=URL_WEEK):
    """Tải lịch tuần, có cache đĩa; nếu bị 429 thì dùng cache cũ."""
    if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < CACHE_TTL:
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        if os.path.exists(CACHE):
            with open(CACHE, encoding="utf-8") as f:
                return json.load(f)
        raise
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return data


def to_vn(item):
    """Trả về datetime giờ VN, hoặc None nếu tin kiểu 'All Day'."""
    try:
        t = dt.datetime.fromisoformat(item["date"])
    except ValueError:
        return None
    return t.astimezone(VN)


def relevant(item):
    c, imp = item.get("country"), item.get("impact")
    if c in CCY_MAIN:
        return imp in ("High", "Medium")
    if c in CCY_SUB:
        return imp == "High"
    return False


def label(item):
    imp = item.get("impact")
    if item.get("country") == "USD" and imp == "High":
        if any(k.lower() in item["title"].lower() for k in TOP_TIER):
            return "🔴🔴 CỰC MẠNH"
        return "🔴 MẠNH"
    if imp == "High":
        return "🔴 mạnh (ngoài USD)"
    return "🟠 vừa"


def report(events, day_label):
    if not events:
        return f"📅 {day_label}: KHÔNG có tin USD đáng kể → giá chạy theo dòng lệnh, tự do vào lệnh."
    lines = [f"📅 {day_label} — {len(events)} tin cần né:"]
    for e in events:
        t = to_vn(e)
        hhmm = t.strftime("%H:%M") if t else "cả ngày"
        fc = e.get("forecast") or "-"
        pv = e.get("previous") or "-"
        lines.append(f"  {hhmm}  {label(e)}  {e['country']} · {e['title']}  (dự báo {fc} / trước {pv})")
    lines.append("  ⚠ Trước/sau mốc tin 15 phút: không vào lệnh mới, siết SL hoặc đứng ngoài.")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", action="store_true", help="in cả tuần")
    ap.add_argument("--date", help="ngày cụ thể YYYY-MM-DD (giờ VN)")
    a = ap.parse_args()

    data = [e for e in fetch() if relevant(e)]
    data.sort(key=lambda e: e["date"])

    if a.week:
        by_day = {}
        for e in data:
            t = to_vn(e)
            key = t.date() if t else dt.date.fromisoformat(e["date"][:10])
            by_day.setdefault(key, []).append(e)
        for d in sorted(by_day):
            print(report(by_day[d], d.strftime("%a %d/%m")))
            print()
        return

    target = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(VN).date()
    today = []
    for e in data:
        t = to_vn(e)
        d = t.date() if t else dt.date.fromisoformat(e["date"][:10])
        if d == target:
            today.append(e)
    print(report(today, target.strftime("%a %d/%m/%Y")))


if __name__ == "__main__":
    main()
