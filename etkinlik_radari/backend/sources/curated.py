"""Curated lists: Techmeme, Dealroom, Cerebral Valley, TechCrunch, Slush, Web Summit."""
import html
import re

from ..dates import norm, parse_range
from ..models import Event
from ..net import get, get_json, has_type, json_ld, strip_html


def _ld_event(obj, source, importance, kind_hint="") -> Event | None:
    if not obj.get("name") or not obj.get("startDate"):
        return None
    loc = obj.get("location") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = loc.get("address") or {}
    if isinstance(addr, str):
        addr = {"name": addr}
    online = "Online" in (obj.get("eventAttendanceMode") or "") or loc.get("@type") == "VirtualLocation"
    img = obj.get("image")
    if isinstance(img, list):
        img = img[0] if img else ""
    org = obj.get("organizer")
    if isinstance(org, list):
        org = ", ".join(o.get("name", "") for o in org[:3] if isinstance(o, dict))
    elif isinstance(org, dict):
        org = org.get("name", "")
    url = obj.get("url") or obj.get("@id") or ""
    types = obj.get("@type") if isinstance(obj.get("@type"), list) else [obj.get("@type")]
    return Event(
        source=source,
        key=url or obj["name"],
        title=html.unescape(obj["name"]).strip(),
        url=url,
        start=norm(obj["startDate"]),
        end=norm(obj.get("endDate")),
        description=strip_html(obj.get("description", ""), 600),
        city=addr.get("addressLocality", "") if not online else "",
        country=addr.get("addressCountry", "") if isinstance(addr.get("addressCountry"), str) else "",
        venue=loc.get("name", "") if not online else "",
        online=online,
        image=img or "",
        organizer=org or "",
        importance=importance,
        kind_hint="hackathon" if "Hackathon" in types else kind_hint,
    )


def techmeme(settings) -> list[Event]:
    page = get("https://www.techmeme.com/events").text
    page = page[page.find("All Tech Events"):]
    out = []
    for m in re.finditer(r'<a href="(/r2/[^"]+)"><div>(.*?)</div><div>(.*?)</div><div>(.*?)</div></a>', page, re.S):
        href, when, name, place = m.groups()
        start, end = parse_range(strip_html(when))
        if not start:
            continue
        place = strip_html(place)
        title = strip_html(name)
        online = place.lower() in ("online", "virtual")
        out.append(Event(
            source="techmeme", key=href, title=title, url="https://www.techmeme.com" + href,
            start=start, end=end, city="" if online else place, online=online,
            importance=72, kind_hint="conference",
        ))
    return out


def dealroom(settings) -> list[Event]:
    out = []
    for obj in json_ld(get("https://dealroom.co/events", timeout=60).text):
        if has_type(obj, "ItemList"):
            for it in obj.get("itemListElement", []):
                e = _ld_event(it.get("item") or {}, "dealroom", 70, "conference")
                if e:
                    out.append(e)
    return out


def cerebral(settings) -> list[Event]:
    out = []
    for obj in json_ld(get("https://cerebralvalley.ai/events").text):
        if has_type(obj, "ItemList"):
            for it in obj.get("itemListElement", []):
                e = _ld_event(it.get("item") or {}, "cerebral", 66)
                if e:
                    e.tags.append("ai")
                    out.append(e)
    return out


def techcrunch(settings) -> list[Event]:
    items = get_json("https://techcrunch.com/wp-json/wp/v2/tc_event",
                     params={"per_page": 30, "_fields": "id,link,title,meta,excerpt"})
    out = []
    for it in items:
        meta = it.get("meta") or {}
        start = norm(meta.get("tc_event_start"))
        if not start:
            continue
        title = html.unescape(it["title"]["rendered"])
        big = any(k in title.lower() for k in ("disrupt", "founder summit", "sessions"))
        out.append(Event(
            source="techcrunch", key=str(it["id"]), title=title, url=it["link"],
            start=start, end=norm(meta.get("tc_event_end")),
            description=strip_html((it.get("excerpt") or {}).get("rendered", ""), 500),
            city=meta.get("tc_event_city", "") or "",
            organizer="TechCrunch", importance=92 if big else 78, kind_hint="conference",
        ))
    return out


def flagships(settings) -> list[Event]:
    """Slush + Web Summit family. Each site describes only its own next edition."""
    out = []
    try:
        page = get("https://slush.org").text
        m = re.search(r"<title>Slush (\d{4}) \| ([^,<]+), ([^<]+)</title>", page)
        if m:
            year, city, when = m.groups()
            start, end = parse_range(f"{when} {year}")
            og = re.search(r'property="og:image" content="([^"]+)"', page)
            desc = re.search(r'name="description" content="([^"]+)"', page)
            out.append(Event(
                source="slush", key=f"slush-{year}", title=f"Slush {year}", url="https://slush.org",
                start=start, end=end, city=city.strip(), country="Finland",
                description=html.unescape(desc.group(1)) if desc else "",
                image=og.group(1) if og else "", organizer="Slush",
                importance=97, kind_hint="conference", tags=["startup", "invest"],
            ))
    except Exception:
        pass
    for host in ("websummit.com", "vancouver.websummit.com", "qatar.websummit.com", "rio.websummit.com"):
        try:
            for obj in json_ld(get(f"https://{host}", timeout=20).text):
                if has_type(obj, "Event"):
                    e = _ld_event(obj, "websummit", 95, "conference")
                    if e:
                        e.url = e.url or f"https://{host}"
                        e.key = f"{host}-{e.start}"
                        e.organizer = "Web Summit"
                        e.tags += ["startup", "invest"]
                        if not e.city and "," in e.title:
                            e.city = e.title.split(",")[-1].strip()
                        out.append(e)
        except Exception:
            continue
    return out
