"""Cover images for events/news that the source lists without one: read the page's og:image.
Results (including misses) are cached in the DB so each page is fetched at most once a week."""
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

from .net import session

META_RX = [
    re.compile(r'<meta[^>]+(?:property|name)=["\'](?:og:image(?::secure_url)?|twitter:image(?::src)?)["\'][^>]*'
               r'content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\'](?:og:image|twitter:image)', re.I),
]
REFRESH_RX = re.compile(r'http-equiv=["\']refresh["\'][^>]*url=([^"\'>]+)', re.I)
RETRY_MISSES_AFTER = timedelta(days=7)


def _head_html(url: str, limit=400_000) -> tuple[str, str]:
    with session().get(url, timeout=8, stream=True) as r:
        if "html" not in r.headers.get("content-type", "html"):
            return r.url, ""
        buf = b""
        for chunk in r.iter_content(32_768):
            buf += chunk
            if len(buf) >= limit or b"</head>" in buf:
                break
        return r.url, buf.decode(r.encoding or "utf-8", "replace")


def og_image(url: str) -> str:
    try:
        final, html = _head_html(url)
        m = REFRESH_RX.search(html[:3000])
        if m:  # Techmeme '/r2/' links are meta-refresh hops to the real site
            final, html = _head_html(urljoin(final, m.group(1).strip()))
        for rx in META_RX:
            m = rx.search(html)
            if m:
                img = urljoin(final, m.group(1).strip().replace("&amp;", "&"))
                return img if img.startswith("http") else ""
    except Exception:
        pass
    return ""


def enrich(db, urls: list[str], limit: int, workers: int = 16) -> int:
    """Fetch og:image for up to `limit` uncached urls (in the given priority order)."""
    cache = db.image_cache()
    cutoff = (datetime.now(timezone.utc) - RETRY_MISSES_AFTER).strftime("%Y-%m-%dT%H:%M:%SZ")
    todo, seen = [], set()
    for u in urls:
        if not u or u in seen:
            continue
        seen.add(u)
        hit = cache.get(u)
        if hit is None or (not hit[0] and hit[1] < cutoff):
            todo.append(u)
    todo = todo[:limit]
    if not todo:
        return 0
    with ThreadPoolExecutor(workers) as pool:
        found = dict(zip(todo, pool.map(og_image, todo)))
    db.put_images(found)
    return sum(1 for v in found.values() if v)
