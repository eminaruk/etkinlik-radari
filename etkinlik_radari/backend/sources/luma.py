"""lu.ma — public discover API. Slugs can be categories (tech, ai, crypto) or cities (istanbul, london)."""
import math

from ..dates import norm
from ..models import Event
from ..net import get_json

API = "https://api.lu.ma/discover/get-paginated-events"
MAX_PER_SLUG = 150


def _event(entry, slug) -> Event | None:
    ev = entry.get("event") or {}
    if not ev.get("url") or ev.get("visibility", "public") != "public":
        return None
    geo = ev.get("geo_address_info") or {}
    loc = (geo.get("localized") or {}).get("tr") or geo
    city = loc.get("region") if geo.get("country") in ("Türkiye", "Turkey") else geo.get("city")
    ticket = entry.get("ticket_info") or {}
    hosts = [h.get("name") for h in entry.get("hosts") or [] if h.get("name")]
    cal = entry.get("calendar") or {}
    guests = entry.get("guest_count") or 0
    return Event(
        source="luma",
        key=ev["api_id"],
        title=ev.get("name", "").strip(),
        url=f"https://lu.ma/{ev['url']}",
        start=norm(ev.get("start_at")),
        end=norm(ev.get("end_at")),
        description=(cal.get("description_short") or ""),
        city=city or geo.get("city_state") or "",
        country=geo.get("country", ""),
        venue=geo.get("address", ""),
        online=ev.get("location_type") == "online",
        image=ev.get("cover_url", ""),
        is_free=ticket.get("is_free"),
        organizer=", ".join(hosts[:3]) or cal.get("name", ""),
        guest_count=guests,
        tags=[slug],
        # 30 baseline, rising with log(guests): 50 guests ≈ 52, 500 ≈ 67, 3000 ≈ 79
        importance=min(85, int(30 + 6 * math.log1p(guests))),
        extra={"spots_remaining": ticket.get("spots_remaining"),
               "sold_out": ticket.get("is_sold_out"),
               "calendar": cal.get("name", "")},
    )


def fetch(settings) -> list[Event]:
    out, seen = [], set()
    # category slugs (tech/ai/crypto) are geolocated by IP, so city slugs add global coverage
    for slug in settings.get("luma_slugs") or ["tech", "ai", "istanbul"]:
        cursor, n = None, 0
        while n < MAX_PER_SLUG:
            params = {"slug": slug, "pagination_limit": 50}
            if cursor:
                params["pagination_cursor"] = cursor
            data = get_json(API, params=params)
            for entry in data.get("entries", []):
                e = _event(entry, slug)
                if e and e.key not in seen:
                    seen.add(e.key)
                    out.append(e)
                n += 1
            cursor = data.get("next_cursor")
            if not data.get("has_more") or not cursor:
                break
    return out
