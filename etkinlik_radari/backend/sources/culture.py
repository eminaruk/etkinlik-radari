"""Culture & arts: Biletix (Solr search), etkinlik.io (RSS), Biletinial (JSON-LD), Eventbrite city pages
(JSON-LD), İzmir open data.

Ticketing sites list every performance separately, so performances of the same show in the same city are
folded into one event that starts at the next performance and remembers how many dates there are."""
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime

from ..dates import norm, tr_lower
from ..models import Event
from ..net import get, get_json, has_type, json_ld, strip_html
from .curated import _ld_event

DAYS_AHEAD = 90

# Biletix "subcategory$CATEGORY" -> (category tag, kind hint)
BILETIX_MAP = {
    "tiyatro": ("stage", "show"), "stand_up": ("stage", "show"), "gosteri": ("stage", "show"),
    "bale_dans": ("stage", "show"), "musical": ("stage", "show"), "sinema": ("film", "screening"),
    "atolye": ("art", "workshop"), "egitim": ("art", "workshop"), "mebonayliegitim": ("family", "workshop"),
    "muze": ("art", "exhibition"), "sergi": ("art", "exhibition"), "konferans": ("lit", "conference"),
    "attractioncenter": ("family", "exhibition"),
}


def _fold(events: list[Event]) -> list[Event]:
    """One event per (title, city): earliest performance first, the rest counted in extra."""
    groups: dict[tuple, list[Event]] = {}
    for e in events:
        groups.setdefault((e.title.casefold(), e.city.casefold()), []).append(e)
    out = []
    for evs in groups.values():
        evs.sort(key=lambda e: e.start or "")
        first = evs[0]
        if len(evs) > 1:
            first.extra["performances"] = len(evs)
            first.extra["dates"] = [e.start for e in evs[:6]]
            venues = {e.venue for e in evs if e.venue}
            if len(venues) > 1:
                first.extra["venues"] = len(venues)
        out.append(first)
    return out


def biletix(settings) -> list[Event]:
    params = {"q": "*:*", "wt": "json", "rows": 1000, "sort": "start asc",
              "fq": ["type:event", "end:[NOW TO *]", f"start:[* TO NOW+{DAYS_AHEAD}DAYS]", "-category:SPORT",
                     "-status:s05_postponed"],
              "fl": "id,sname,svenue,city,start,end,description,category,subcategory,image_url,status,region"}
    docs, offset = [], 0
    while True:
        page = get_json("https://www.biletix.com/solr/tr/select/", params={**params, "start": offset})["response"]
        docs += page["docs"]
        offset += len(page["docs"])
        if not page["docs"] or offset >= min(page["numFound"], 5000):
            break
    out = []
    for d in docs:
        sub, _, cat = (d.get("subcategory") or "").partition("$")
        tag, kind = BILETIX_MAP.get(sub, ("music", "concert") if cat == "MUSIC" else ("family", "show")
                                    if cat == "FAMILY" else ("stage", "show"))
        tags = [f"cat:{tag}"] + (["cat:family"] if cat == "FAMILY" and tag != "family" else [])
        start, end = norm(d.get("start")), norm(d.get("end"))
        # exhibitions and residencies run for weeks; single performances report end == start + a few hours
        if end and start and end[:10] <= start[:10]:
            end = None
        desc = d.get("description") or ""
        desc = " ".join(desc) if isinstance(desc, list) else desc
        city = (d.get("city") or [""])[0]
        out.append(Event(
            source="biletix", key=d["id"], title=(d.get("sname") or d["id"]).strip(),
            url=f"https://www.biletix.com/etkinlik/{d['id']}/TURKIYE/tr",
            start=start, end=end,
            description=strip_html(desc.strip("[]'\"").replace("\\r\\n", "\n"), 600),
            city=city, country="Türkiye", venue=d.get("svenue") or "",
            image=f"https://www.biletix.com/static/images/live/event/eventimages/{d['image_url']}"
            if d.get("image_url") else "",
            tags=tags, kind_hint=kind, importance=50,
            extra={"sold_out": True} if d.get("status") == "s02_soldout" else {},
        ))
    return _fold(out)


BILETINIAL_SECTIONS = ["tiyatro", "muzik", "opera-bale"]
BILETINIAL_PER_SECTION = 80
BILETINIAL_KIND = {"tiyatro": ("stage", "show"), "muzik": ("music", "concert"), "opera-bale": ("stage", "show")}


def _biletinial_detail(url, section):
    """Each show page carries one JSON-LD Event per upcoming performance."""
    tag, kind = BILETINIAL_KIND[section]
    evs = []
    for obj in json_ld(get(url).text):
        if not has_type(obj, "Event"):
            continue
        e = _ld_event(obj, "biletinial", 48, kind)
        if e and e.start:
            e.url, e.key = url, f"{url}#{e.start}"
            e.end = None if (e.end or "")[:10] == e.start[:10] else e.end
            e.tags, e.country = [f"cat:{tag}"], "Türkiye"
            evs.append(e)
    return evs


def biletinial(settings) -> list[Event]:
    jobs = []
    for section in BILETINIAL_SECTIONS:
        for obj in json_ld(get(f"https://biletinial.com/tr-tr/{section}").text):
            if has_type(obj, "ItemList"):
                jobs += [(it["url"], section) for it in obj.get("itemListElement", [])[:BILETINIAL_PER_SECTION]
                         if it.get("url")]
    today, limit = date.today().isoformat(), (date.today() + timedelta(days=DAYS_AHEAD)).isoformat()
    out = []
    with ThreadPoolExecutor(8) as pool:
        for evs in pool.map(lambda j: _safe(_biletinial_detail, *j) or [], dict(jobs).items()):
            out += [e for e in evs if today <= e.start[:10] <= limit]
    return _fold(out)


EVENTBRITE_CATEGORIES = ["performing-arts", "music", "arts"]
EVENTBRITE_DEFAULT = ["turkey--istanbul", "united-kingdom--london", "ny--new-york", "germany--berlin", "france--paris"]


def _eventbrite_page(place, cat):
    out = []
    for obj in json_ld(get(f"https://www.eventbrite.com/d/{place}/{cat}/").text):
        if has_type(obj, "ItemList"):
            for it in obj.get("itemListElement", []):
                e = _ld_event(it.get("item") or {}, "eventbrite", 45,
                              {"music": "concert", "arts": "exhibition"}.get(cat, "show"))
                if e:
                    e.tags = [{"music": "cat:music", "arts": "cat:art"}.get(cat, "cat:stage")]
                    e.key = e.url.split("?")[0]
                    out.append(e)
    return out


def eventbrite(settings) -> list[Event]:
    places = settings.get("eventbrite_places") or EVENTBRITE_DEFAULT
    jobs = [(p, c) for p in places for c in EVENTBRITE_CATEGORIES]
    seen, out = set(), []
    with ThreadPoolExecutor(6) as pool:
        for evs in pool.map(lambda j: _safe(_eventbrite_page, *j) or [], jobs):
            for e in evs:
                if e.key not in seen:
                    seen.add(e.key)
                    out.append(e)
    return out


def izmir(settings) -> list[Event]:
    """İzmir Metropolitan Municipality open data (kultursanat.izmir.bel.tr)."""
    r = get("https://openapi.izmir.bel.tr/api/ibb/kultursanat/etkinlikler")
    r.encoding = "utf-8"
    out = []
    for it in r.json():
        tur = (it.get("Tur") or "").casefold()
        tag, kind = (("art", "exhibition") if "sergi" in tur else ("music", "concert") if "konser" in tur
                     else ("film", "screening") if "sinema" in tur or "film" in tur else ("stage", "show"))
        out.append(Event(
            source="izmir", key=str(it["Id"]), title=it.get("Adi", ""),
            url=f"https://kultursanat.izmir.bel.tr/Etkinlikler/{it.get('EtkinlikUrl', '')}/{it['Id']}",
            start=norm(it.get("EtkinlikBaslamaTarihi")), end=norm(it.get("EtkinlikBitisTarihi")),
            description=strip_html(it.get("KisaAciklama") or ""), city="İzmir", country="Türkiye",
            venue=it.get("EtkinlikMerkezi") or "", image=it.get("Resim") or "",
            is_free=it.get("UcretsizMi"), organizer="İzmir Büyükşehir Belediyesi",
            tags=[f"cat:{tag}"], kind_hint=kind, importance=46,
        ))
    return out


# etkinlik.io publishes an RSS query service (etkinlik.io/rss/bilgi). Each query returns the 50 nearest events,
# so the country is covered as city × format, and the busiest cities again per sub-genre to reach further ahead.
ETKINLIKIO_CITIES = {
    40: "İstanbul", 7: "Ankara", 41: "İzmir", 8: "Antalya", 32: "Eskişehir", 21: "Bursa", 53: "Konya",
    33: "Gaziantep", 58: "Mersin", 1: "Adana", 52: "Kocaeli", 66: "Sakarya", 28: "Edirne", 59: "Muğla",
    12: "Balıkesir", 47: "Kayseri", 67: "Samsun", 26: "Diyarbakır", 25: "Denizli", 73: "Tekirdağ",
    61: "Nevşehir", 81: "Zonguldak", 75: "Trabzon", 11: "Aydın",
}
# format id -> (category tag, kind)
ETKINLIKIO_FORMATS = {7: ("stage", "show"), 19: ("music", "concert"), 1: ("art", "exhibition"),
                      21: ("music", "festival"), 14: ("lit", "conference"), 28: ("art", "workshop")}
ETKINLIKIO_DEEP_CITIES = [40, 7, 41, 8]
ETKINLIKIO_GENRES = [3964, 88, 3974, 63, 300, 1423, 291, 170, 3975, 3985, 3984, 75, 3805, 3796]
# etkinlik.io interest label -> our category tag; workshops tagged only with hobby/cooking labels are skipped
ETKINLIKIO_CATS = {
    "çocuk tiyatrosu": "family", "çocuk gelişimi": "family", "sinema-film": "film", "dil ve edebiyat": "lit",
    "tarih": "lit", "sanat": "art", "fotoğrafçılık": "art", "tiyatro ve gösteriler": "stage",
    "dans ve müzikal gösteriler": "stage", "kültür & din": "stage",
}
ETKINLIKIO_OFFTOPIC = {"aşçılık ve mutfak", "hobi & yaşam tarzı", "kişisel gelişim", "gıda", "seyahat", "turizm",
                       "spor", "sağlık-tıp", "eğitim - öğretim", "yabancı dil", "kariyer"}


def _etkinlikio_feed(query, city, fmt):
    root = ET.fromstring(get(f"https://etkinlik.io/rss/sorgu?{query}").content)
    out = []
    for item in root.iter("item"):
        link = (item.findtext("link") or "").strip()
        m = re.search(r"/etkinlik/(\d+)/", link)
        when = item.findtext("pubDate")
        if not m or not when:
            continue
        labels = [(c.text or "").strip() for c in item.findall("category")]
        low = {tr_lower(l) for l in labels}
        cats = {ETKINLIKIO_CATS[l] for l in low if l in ETKINLIKIO_CATS} | {"music" for l in low if "müzik" in l}
        if not cats and low & ETKINLIKIO_OFFTOPIC:
            continue
        tag, kind = ETKINLIKIO_FORMATS[fmt]
        if not cats:
            cats = {tag}
        enc = item.find("enclosure")
        out.append(Event(
            source="etkinlikio", key=m.group(1), title=strip_html(item.findtext("title") or ""), url=link,
            start=norm(parsedate_to_datetime(when)), description=strip_html(item.findtext("description") or "", 600),
            city=city, country="Türkiye", image=enc.get("url", "") if enc is not None else "",
            tags=[f"cat:{c}" for c in sorted(cats)], kind_hint=kind, importance=46,
        ))
    return out


def etkinlikio(settings) -> list[Event]:
    jobs = [(f"sehirIds={cid}&turIds={fmt}", city, fmt) for cid, city in ETKINLIKIO_CITIES.items()
            for fmt in ETKINLIKIO_FORMATS]
    jobs += [(f"sehirIds={cid}&kategoriIds={g}", ETKINLIKIO_CITIES[cid], 19 if g in (63, 300, 1423, 291, 170, 3975,
             3985, 3984) else 1 if g == 75 else 7) for cid in ETKINLIKIO_DEEP_CITIES for g in ETKINLIKIO_GENRES]
    seen, out = set(), []
    with ThreadPoolExecutor(8) as pool:
        for evs in pool.map(lambda j: _safe(_etkinlikio_feed, *j) or [], jobs):
            for e in evs:
                if e.key not in seen:
                    seen.add(e.key)
                    out.append(e)
    if not out:
        raise RuntimeError("etkinlik.io RSS returned no events")
    return _fold(out)


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception:
        return None
