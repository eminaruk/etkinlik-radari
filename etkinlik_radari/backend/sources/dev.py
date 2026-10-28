"""Developer & research sources: Devpost, dev.events, AI conference deadlines."""
import math
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

import yaml

from ..dates import norm, parse_range
from ..models import Event
from ..net import get, get_json, strip_html


def devpost(settings) -> list[Event]:
    out, page = [], 1
    while page <= 6:
        data = get_json("https://devpost.com/api/hackathons",
                        params={"status[]": ["upcoming", "open"], "per_page": 40, "page": page})
        items = data.get("hackathons") or []
        for h in items:
            start, end = parse_range(h.get("submission_period_dates", ""))
            if not start:
                continue
            prize_txt = strip_html(h.get("prize_amount") or "")
            prize = int(re.sub(r"[^\d]", "", prize_txt) or 0)
            regs = h.get("registrations_count") or 0
            loc = (h.get("displayed_location") or {}).get("location", "")
            online = loc.lower() == "online"
            thumb = h.get("thumbnail_url") or ""
            out.append(Event(
                source="devpost", key=str(h["id"]), title=h["title"], url=h["url"],
                start=start, end=end, city="" if online else loc, online=online,
                image=("https:" + thumb) if thumb.startswith("//") else thumb,
                organizer=h.get("organization_name") or "",
                guest_count=regs, is_free=True,
                tags=[t["name"] for t in h.get("themes") or []],
                kind_hint="hackathon",
                importance=min(85, int(30 + 5 * math.log10(prize + 1) + 2.5 * math.log10(regs + 1))),
                extra={"prize": prize_txt, "time_left": h.get("time_left_to_submission", ""),
                       "state": h.get("open_state", "")},
            ))
        if len(items) < 40:
            break
        page += 1
    return out


def devevents(settings) -> list[Event]:
    root = ET.fromstring(get("https://dev.events/rss.xml").content)
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = item.findtext("link") or ""
        desc = item.findtext("description") or ""
        # "... happening on December 3, 2026, Online." / "... on November 16, 2026 in San Francisco, United States, North America."
        m = re.search(r"happening on (.+?\d{4})(?:,\s*|\s+in\s+)(.+?)\.\s*More information", desc)
        if not m:
            continue
        start, end = parse_range(m.group(1))
        place = m.group(2).strip()
        online = place.lower() == "online"
        parts = [p.strip() for p in place.split(",")]
        if len(parts) >= 3:  # drop trailing continent
            parts = parts[:-1]
        enc = item.find("enclosure")
        cats = [c.text for c in item.findall("category") if c.text]
        out.append(Event(
            source="devevents", key=item.findtext("guid") or link, title=title, url=link,
            start=start, end=end, online=online,
            city="" if online else parts[0], country="" if online or len(parts) < 2 else parts[-1],
            image=enc.get("url") if enc is not None else "",
            tags=cats, kind_hint=cats[1] if len(cats) > 1 else "conference",
            importance=50,
        ))
    return out


ERA = {"a*": 88, "a": 80, "b": 64, "c": 52}


def ai_deadlines(settings) -> list[Event]:
    """aideadlin.es is frozen since 2025; huggingface/ai-deadlines is its maintained successor."""
    listing = get_json("https://api.github.com/repos/huggingface/ai-deadlines/contents/src/data/conferences")
    urls = [f["download_url"] for f in listing if f["name"].endswith(".yml")]
    today = date.today()
    cutoff = (today - timedelta(days=7)).isoformat()

    def load(u):
        try:
            return yaml.safe_load(get(u).text) or []
        except Exception:
            return []

    out = []
    with ThreadPoolExecutor(12) as pool:
        for confs in pool.map(load, urls):
            for c in confs if isinstance(confs, list) else []:
                start = norm(str(c.get("start") or "")) or None
                end = norm(str(c.get("end") or "")) or start
                deadlines = sorted(
                    (str(d.get("date", ""))[:10], d.get("label") or d.get("type", ""))
                    for d in c.get("deadlines") or [] if d.get("date"))
                upcoming = [d for d in deadlines if d[0] >= today.isoformat()]
                if not ((end and end >= cutoff) or upcoming):
                    continue
                if not start:
                    if not upcoming:
                        continue
                    start = end = upcoming[0][0]
                nd = upcoming[0] if upcoming else None
                title = f"{c.get('title', '')} {c.get('year', '')}".strip()
                out.append(Event(
                    source="aideadlines", key=str(c.get("id") or title), title=title,
                    url=c.get("link", ""), start=start, end=end,
                    description=(c.get("full_name") or "")
                    + (f"\nSıradaki son tarih: {nd[1]} — {nd[0]}" if nd else ""),
                    city=c.get("city") or "", country=c.get("country") or "",
                    venue=c.get("venue") or "",
                    tags=["research"] + list(c.get("tags") or []), kind_hint="conference",
                    importance=ERA.get(str(c.get("era_rating", "")).lower(), 56),
                    extra={"next_deadline": {"date": nd[0], "label": nd[1]} if nd else None},
                ))
    return out
