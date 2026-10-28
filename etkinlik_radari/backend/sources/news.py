"""News feeds for sites that have no event calendar (or block scraping)."""
import html
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from ..dates import norm
from ..models import NewsItem
from ..net import get, get_json, strip_html

FEEDS = {
    "swipeline": "https://swipeline.co/feed/",
    "webrazzi": "https://webrazzi.com/feed/",
    "techmeme": "https://www.techmeme.com/feed.xml",
    "techcrunch": "https://techcrunch.com/feed/",
    "crunchbase": "https://news.crunchbase.com/feed/",
}
MEDIA_NS = "{http://search.yahoo.com/mrss/}"


def _rss(source, url) -> list[NewsItem]:
    root = ET.fromstring(get(url).content)
    out = []
    for item in list(root.iter("item"))[:25]:
        pub = item.findtext("pubDate")
        try:
            pub = norm(parsedate_to_datetime(pub)) if pub else None
        except (TypeError, ValueError):
            pub = None
        desc = item.findtext("description") or ""
        img = ""
        media = item.find(MEDIA_NS + "content")
        if media is None:  # Element truthiness depends on children, so compare to None
            media = item.find(MEDIA_NS + "thumbnail")
        if media is not None:
            img = media.get("url", "")
        if not img:
            m = re.search(r'<img[^>]+src="([^"]+)"', desc)
            img = m.group(1) if m else ""
        out.append(NewsItem(source=source, title=html.unescape(item.findtext("title") or "").strip(),
                            url=(item.findtext("link") or "").strip(), published=pub,
                            summary=strip_html(desc, 260), image=img))
    return out


def _endeavor() -> list[NewsItem]:
    posts = get_json("https://endeavor.org.tr/wp-json/wp/v2/posts",
                     params={"per_page": 15, "_fields": "link,title,date,excerpt"})
    return [NewsItem(source="endeavor", title=html.unescape(p["title"]["rendered"]), url=p["link"],
                     published=norm(p.get("date")),
                     summary=strip_html((p.get("excerpt") or {}).get("rendered", ""), 260))
            for p in posts]


def fetch_all() -> tuple[list[NewsItem], dict]:
    items, errors = [], {}
    jobs = [(s, lambda s=s, u=u: _rss(s, u)) for s, u in FEEDS.items()] + [("endeavor", _endeavor)]
    for source, fn in jobs:
        try:
            items.extend(fn())
        except Exception as e:  # one broken feed must not hide the others
            errors[source] = f"{type(e).__name__}: {e}"[:200]
    return items, errors
