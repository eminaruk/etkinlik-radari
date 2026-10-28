"""Turkish ecosystem: Webrazzi events page and İTÜ Çekirdek (WordPress 'eventer' post type)."""
import html
import re
from datetime import date, timedelta

from ..dates import parse_range
from ..models import Event
from ..net import get, get_json, strip_html

TR_DATE = (r"\d{1,2}(?:\s*[-–]\s*\d{1,2})?\s+(?:Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|"
           r"Ağustos|Eylül|Ekim|Kasım|Aralık)(?:\s*[-–]\s*\d{1,2}\s+\w+)?\s+\d{4}")


def webrazzi(settings) -> list[Event]:
    page = get("https://webrazzi.com/etkinlik/").text
    out = []
    for block in page.split('class="events-listing-item"')[1:]:
        title = re.search(r"<h3>(.*?)</h3>", block, re.S)
        when = re.search(r'class="elb-date-city">(.*?)<span', block, re.S)
        if not title or not when:
            continue
        start, end = parse_range(strip_html(when.group(1)), "tr")
        # the page also archives every past edition back to 2020
        if not start or start < (date.today() - timedelta(days=365)).isoformat():
            continue
        href = re.search(r'class="elb-title">\s*<a href="([^"]+)"', block)
        url = href.group(1) if href else "https://webrazzi.com/etkinlik/"
        if url.startswith("/"):
            url = "https://webrazzi.com" + url
        city = re.search(r'pin-map-before">(.*?)</span>', block, re.S)
        img = re.search(r"background-image:\s*url\(([^)]+)\)", block)
        desc = re.search(r'class="elb-desc">(.*?)</div>', block, re.S)
        venue = strip_html(city.group(1)) if city else ""
        out.append(Event(
            source="webrazzi", key=url, title=strip_html(title.group(1)), url=url,
            start=start, end=end,
            city="İstanbul", country="Türkiye", venue=venue if venue != "İstanbul" else "",
            description=strip_html(desc.group(1)) if desc else "",
            image=img.group(1).strip("'\"") if img else "", organizer="Webrazzi",
            importance=86, kind_hint="conference",
        ))
    return out


def itu(settings) -> list[Event]:
    items = get_json("https://itucekirdek.com/wp-json/wp/v2/eventer",
                     params={"per_page": 30, "_embed": "wp:featuredmedia"})
    oldest = (date.today() - timedelta(days=400)).isoformat()
    out = []
    for it in items:
        if it.get("date", "") < oldest:
            continue
        title = html.unescape(it["title"]["rendered"])
        body = strip_html(it["content"]["rendered"])
        m = re.search(TR_DATE, body) or re.search(TR_DATE, title)
        if not m:
            continue
        start, end = parse_range(m.group(0), "tr")
        if not start:
            continue
        media = (it.get("_embedded") or {}).get("wp:featuredmedia") or [{}]
        online = bool(re.search(r"\b(online|zoom|çevrim ?içi)\b", body, re.I))
        out.append(Event(
            source="itu", key=str(it["id"]), title=title, url=it["link"],
            start=start, end=end, description=body[:700],
            city="" if online else "İstanbul", country="Türkiye", online=online,
            venue="İTÜ Ayazağa" if not online else "",
            image=media[0].get("source_url", "") if isinstance(media[0], dict) else "",
            organizer="İTÜ Çekirdek", importance=64, tags=["startup"],
        ))
    return out
