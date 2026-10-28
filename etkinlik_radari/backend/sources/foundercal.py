"""foundercal.com — city pages list events (JSON-LD ItemList), each event page carries a JSON-LD Event.
Event pages are cached in the DB so a refresh only fetches new ones."""
from concurrent.futures import ThreadPoolExecutor

from ..dates import norm
from ..models import Event
from ..net import get, has_type, json_ld

MAX_PER_CITY = 60


def _detail(url, city_slug) -> Event | None:
    for obj in json_ld(get(url).text):
        if not has_type(obj, "Event"):
            continue
        loc = obj.get("location") or {}
        addr = loc.get("address") or {}
        online = "Online" in (obj.get("eventAttendanceMode") or "") or loc.get("@type") == "VirtualLocation"
        return Event(
            source="foundercal",
            key=url.rsplit("/", 1)[-1],
            title=obj.get("name", ""),
            url=url,
            start=norm(obj.get("startDate")),
            end=norm(obj.get("endDate")),
            description=obj.get("description", ""),
            city=addr.get("addressLocality") or city_slug.replace("-", " ").title(),
            country=addr.get("addressCountry", "") if isinstance(addr.get("addressCountry"), str) else "",
            venue=loc.get("name", ""),
            online=online,
            image=obj.get("image", "") if isinstance(obj.get("image"), str) else "",
            is_free=obj.get("isAccessibleForFree"),
            importance=58,
            extra={"external_url": obj.get("url", "")},
        )
    return None


def fetch(settings, cache=None) -> list[Event]:
    """cache: dict url -> previously stored event dict (to skip re-fetching detail pages)."""
    cache = cache or {}
    jobs = []
    for city in settings.get("foundercal_cities") or ["istanbul"]:
        page = get(f"https://foundercal.com/cities/{city}").text
        for obj in json_ld(page):
            if has_type(obj, "ItemList"):
                for item in obj.get("itemListElement", [])[:MAX_PER_CITY]:
                    if item.get("url"):
                        jobs.append((item["url"], city))
    out, todo = [], []
    for url, city in dict(jobs).items():
        if url in cache:
            out.append(Event(**{k: v for k, v in cache[url].items() if k in Event.__dataclass_fields__}))
        else:
            todo.append((url, city))
    with ThreadPoolExecutor(8) as pool:
        for e in pool.map(lambda j: _safe(_detail, *j), todo):
            if e:
                out.append(e)
    return out


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception:
        return None
