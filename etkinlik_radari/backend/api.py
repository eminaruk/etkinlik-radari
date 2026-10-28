"""Bridge exposed to the web UI via pywebview (window.pywebview.api.*)."""
import copy
import re
import threading
import time
import traceback
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from collections import Counter

from .. import LINKS, __author__, __email__, __version__, paths
from . import classify, geo, images, scoring
from .db import DB, now
from .sources import BY_ID, LABELS, SOURCES, culture, foundercal, news

DEFAULT_SETTINGS = {
    "profile": {
        "interests": {"ai": 2, "startup": 2, "invest": 2, "fintech": 1, "dev": 1, "music": 1, "stage": 1, "art": 1},
        "kinds": {"conference": 1, "demoday": 1},
        "regions": {"turkey": 2, "europe": 1, "online": 1},
    },
    "luma_slugs": ["tech", "ai", "crypto", "arts", "istanbul", "london", "berlin", "sf", "nyc"],
    "foundercal_cities": ["istanbul", "london", "berlin"],
    "eventbrite_places": list(culture.EVENTBRITE_DEFAULT),
    "disabled_sources": [],
    "onboarded": False,
    "theme": "dark",
    "auto_refresh_hours": 6,
    "lang": "tr",             # tr | en
    "personalize": True,      # False: plain chronological list, no fit scores
    "domains": ["tech", "culture"],
    "settings_version": 2,
}
STATE_LABELS = {"tr": {"news": "Haberler", "images": "Kapak görselleri"},
                "en": {"news": "News", "images": "Cover images"}}
STALE_ACTIONS = ("like", "dislike", "save", "attended")


_ENRICHED: dict = {}  # (id, title, start) -> derived fields; tagging every event on every request is slow


def _enrich(d: dict) -> dict:
    key = (d["id"], d["title"], d.get("start"), len(d.get("description") or ""))
    cached = _ENRICHED.get(key)
    if cached is None:
        cached = {"categories": classify.categorize(d)}
        d.update(cached)
        cached["kind"] = d["kind"] = classify.kind_of(d)
        cached["cc"] = d["cc"] = geo.country_code(d)
        cached["region"] = d["region"] = classify.region_of(d)
        cached["domain"] = d["domain"] = classify.domain_of(d)
        cached["keywords"] = classify.keywords(d["title"])
        _ENRICHED[key] = cached
    d.update({k: list(v) if isinstance(v, list) else v for k, v in cached.items()})
    return d


def _title_core(title: str) -> str:
    t = classify.tr_lower(re.split(r"\s[|—–:]\s|,", title)[0])
    t = re.sub(r"register now|\b20\d\d\b", "", t)
    return re.sub(r"[^a-z0-9çğıöşü]", "", t)


def _same_place(a: dict, b: dict) -> bool:
    ca, cb = geo.fold(a.get("city") or "")[:5], geo.fold(b.get("city") or "")[:5]
    return not ca or not cb or ca == cb


def _group_duplicates(events: list[dict]) -> list[list[dict]]:
    """Same event listed by several sources: start within ±1 day and one title core prefixes the other
    ('SLUSH' / 'Slush 2026', 'Web Summit' / 'Web Summit, Lisbon'). A touring show playing İstanbul and
    Ankara on consecutive days stays two events, and a source never duplicates itself."""
    groups, buckets = [], {}  # buckets: (day, first 5 letters of the core) -> [(core, group index)]
    for e in sorted(events, key=lambda x: x.get("start") or ""):
        core = _title_core(e["title"])
        day = datetime.fromisoformat((e.get("start") or "1970-01-01")[:10]).date()
        match = None
        if len(core) >= 5:
            for delta in (-1, 0, 1):
                for other_core, gi in buckets.get((day + timedelta(days=delta), core[:5]), []):
                    short, long_ = sorted((core, other_core), key=len)
                    first = groups[gi][0]
                    if long_.startswith(short) and first["source"] != e["source"] and _same_place(first, e):
                        match = gi
                        break
                if match is not None:
                    break
        if match is None:
            groups.append([e])
            match = len(groups) - 1
        else:
            groups[match].append(e)
        buckets.setdefault((day, core[:5]), []).append((core, match))
    return groups


class Api:
    def __init__(self, data_dir: Path):
        data_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir = data_dir
        self._db = DB(str(data_dir / "radar.db"))
        self._state = {"running": False, "sources": {}, "started": None, "finished": None}
        self._lock = threading.Lock()
        self._db.delete_events_where(geo.is_excluded)  # purge anything stored before the filter existed

    # ---------- settings ----------
    def _settings(self) -> dict:
        s = self._db.get_setting("settings")
        if not s:
            return copy.deepcopy(DEFAULT_SETTINGS)
        if s.get("settings_version", 1) < 2:  # 1.0 profiles: add the culture side the user never had a chance to pick
            s["luma_slugs"] = list(dict.fromkeys([*s.get("luma_slugs", []), "arts"]))
            interests = s.setdefault("profile", {}).setdefault("interests", {})
            for cat in ("music", "stage", "art"):
                interests.setdefault(cat, 1)
            s["settings_version"] = 2
            self._db.set_setting("settings", s)
        return {**DEFAULT_SETTINGS, **s}

    def save_settings(self, settings: dict):
        merged = {**self._settings(), **settings}
        self._db.set_setting("settings", merged)
        return merged

    def bootstrap(self):
        st = self._db.statuses()
        last = max((v["last_run"] for v in st.values()), default=None)
        settings = self._settings()
        hours = settings.get("auto_refresh_hours", 6)  # 0 = only when the user presses refresh
        stale = bool(hours) and (not last or datetime.fromisoformat(last.replace("Z", "+00:00")) <
                                 datetime.now(timezone.utc) - timedelta(hours=hours))
        # sources added by an update have never run; fetch them now instead of waiting for the next refresh
        disabled = set(settings.get("disabled_sources", []))
        missing = [s.id for s in SOURCES if s.status == "events" and s.id not in disabled and s.id not in st]
        en = settings.get("lang") == "en"
        culture_dom = lambda cid, culture_set: "culture" if cid in culture_set else "tech"
        return {
            "settings": settings,
            "meta": {
                "categories": [{"id": c[0], "label": c[2 if en else 1], "icon": c[3],
                                "domain": culture_dom(c[0], classify.CULTURE_CATS)} for c in classify.CATEGORIES],
                "kinds": [{"id": k[0], "label": k[2 if en else 1], "icon": k[3],
                           "domain": culture_dom(k[0], classify.CULTURE_KINDS)} for k in classify.KINDS],
                "regions": [{"id": r[0], "label": r[2 if en else 1], "icon": r[3]} for r in classify.REGIONS],
                "domains": [{"id": d[0], "label": d[2 if en else 1], "icon": d[3]} for d in classify.DOMAINS],
                "source_labels": LABELS,
            },
            "sources": self.sources(),
            "last_refresh": last,
            "needs_refresh": stale,
            "missing_sources": missing,
            "version": __version__,
            "about": {"author": __author__, "email": __email__, "links": LINKS},
            "data_dir": str(self._data_dir),
        }

    def sources(self):
        st = self._db.statuses()
        settings = self._settings()
        disabled, en = set(settings.get("disabled_sources", [])), settings.get("lang") == "en"
        return [{"id": s.id, "label": s.label, "home": s.home, "status": s.status, "domain": s.domain,
                 "note": s.note_en if en else s.note, "enabled": s.id not in disabled,
                 "run": st.get(s.id if s.fetch else "news")} for s in SOURCES]

    # ---------- events ----------
    def get_events(self):
        settings = self._settings()
        raw = [e for e in self._db.all_events() if not geo.is_excluded(e)]
        self._attach_og_images(raw, key=lambda e: e.get("url"))
        by_id = {}
        for e in raw:
            _enrich(e)  # always re-tag so classifier improvements apply to stored events
            by_id[e["id"]] = e
        inter = self._db.interactions()
        learned = scoring.learned_weights(by_id, inter)
        states = {}
        for eid, action in inter:
            states.setdefault(eid, []).append(action)

        out = []
        for group in _group_duplicates(raw):
            group.sort(key=lambda x: (-x.get("importance", 0), -len(x.get("description") or "")))
            primary = dict(group[0])
            primary["also"] = [{"source": g["source"], "url": g["url"]} for g in group[1:]]
            st = set(states.get(primary["id"], []))
            for g in group[1:]:
                st |= set(states.get(g["id"], []))
                primary["image"] = primary.get("image") or g.get("image")
                primary["guest_count"] = primary.get("guest_count") or g.get("guest_count")
            primary["state"] = sorted(st)
            primary["score"], primary["imp"], primary["reasons"] = scoring.score(
                primary, settings["profile"], learned, settings.get("lang", "tr"))
            out.append(primary)
        return {"events": out, "learned": self._learned_summary(learned, settings.get("lang", "tr"))}

    def _attach_og_images(self, items, key):
        """Fill missing images from the og:image cache. An image shared by 3+ items is a site logo
        (e.g. every Dealroom event page uses the Dealroom banner), so it is ignored."""
        cache = self._db.image_cache()
        found = {id(i): (cache.get(key(i)) or ("",))[0] for i in items if not i.get("image")}
        freq = Counter(v for v in found.values() if v)
        for i in items:
            img = found.get(id(i))
            if img and freq[img] < 3:
                i["image"] = img

    def _learned_summary(self, learned, lang="tr"):
        labels = {"cat": classify.labels(classify.CATEGORIES, lang), "kind": classify.labels(classify.KINDS, lang),
                  "region": classify.labels(classify.REGIONS, lang), "src": LABELS}
        rows = []
        for feat, w in learned.items():
            kind, _, val = feat.partition(":")
            name = labels.get(kind, {}).get(val, val) if kind != "kw" else f"“{val}”"
            rows.append({"feature": feat, "type": kind, "label": name, "weight": round(w, 2)})
        rows.sort(key=lambda r: -abs(r["weight"]))
        return rows[:40]

    def interact(self, event_id: str, action: str, on: bool):
        if on and action in ("like", "dislike"):
            self._db.set_interaction(event_id, "dislike" if action == "like" else "like", False)
        self._db.set_interaction(event_id, action, on)
        return True

    def factory_reset(self):
        """Back to a fresh install: settings, likes and lists are wiped; cached events are kept."""
        self._db.clear_interactions(list(STALE_ACTIONS))
        self._db.set_setting("settings", None)
        return self._settings()

    def reset_learning(self):
        self._db.clear_interactions(["like", "dislike"])
        return True

    # ---------- refresh ----------
    def refresh(self, only=None):
        with self._lock:
            if self._state["running"]:
                return False
            settings = self._settings()
            disabled = set(settings.get("disabled_sources", []))
            todo = [s for s in SOURCES if s.fetch and s.id not in disabled and (not only or s.id in only)]
            self._state = {"running": True, "started": now(), "finished": None,
                           "sources": {s.id: {"label": s.label, "state": "waiting"} for s in todo}}
            names = STATE_LABELS.get(settings.get("lang"), STATE_LABELS["tr"])
            if not only or "news" in only:
                self._state["sources"]["news"] = {"label": names["news"], "state": "waiting"}
            if todo:
                self._state["sources"]["images"] = {"label": names["images"], "state": "waiting"}
        threading.Thread(target=self._run_refresh, args=(todo, settings, not only or "news" in only),
                         daemon=True).start()
        return True

    def _run_one(self, src, settings):
        st = self._state["sources"][src.id]
        st["state"] = "running"
        t = time.time()
        try:
            if src.id == "foundercal":
                evs = foundercal.fetch(settings, cache=self._db.cached_by_url("foundercal"))
            else:
                evs = src.fetch(settings)
            dicts = [_enrich(e.to_dict()) for e in evs if e.start and e.title]
            dicts = [d for d in dicts if not geo.is_excluded(d)]
            ids = sorted({d["source"] for d in dicts} | {src.id} | ({"websummit"} if src.id == "slush" else set()))
            self._db.replace_source_events(ids, dicts)
            self._db.set_status(src.id, True, len(dicts), round(time.time() - t, 1))
            st.update(state="done", count=len(dicts))
        except Exception as e:
            traceback.print_exc()
            msg = f"{type(e).__name__}: {e}"[:300]
            self._db.set_status(src.id, False, 0, round(time.time() - t, 1), msg)
            st.update(state="error", error=msg)

    def _run_refresh(self, todo, settings, with_news):
        try:
            with ThreadPoolExecutor(6) as pool:
                futures = [pool.submit(self._run_one, s, settings) for s in todo]
                if with_news:
                    futures.append(pool.submit(self._run_news))
                for f in futures:
                    f.result()
            if "images" in self._state["sources"]:
                self._run_images()
        finally:
            self._state["running"] = False
            self._state["finished"] = now()

    def _run_images(self):
        """Upcoming events without a cover, most important first (Techmeme, TechCrunch, AI conferences…)."""
        st = self._state["sources"]["images"]
        st["state"] = "running"
        today = datetime.now(timezone.utc).date().isoformat()
        evs = [e for e in self._db.all_events()
               if not e.get("image") and (e.get("end") or e.get("start") or "")[:10] >= today]
        evs.sort(key=lambda e: -e.get("importance", 0))
        n = images.enrich(self._db, [e["url"] for e in evs], limit=300)
        st.update(state="done", count=n)

    def _run_news(self):
        st = self._state["sources"]["news"]
        st["state"] = "running"
        t = time.time()
        items, errors = news.fetch_all()
        items = [i for i in items if not geo.EXCLUDED.search(i.title)]
        self._db.replace_news([i.to_dict() for i in items])
        images.enrich(self._db, [i.url for i in items if not i.image], limit=150)
        err = "; ".join(f"{k}: {v}" for k, v in errors.items())
        self._db.set_status("news", bool(items), len(items), round(time.time() - t, 1), err)
        st.update(state="done" if items else "error", count=len(items), error=err)

    def refresh_status(self):
        return self._state

    # ---------- news ----------
    def get_news(self):
        items = [n for n in self._db.news() if not geo.EXCLUDED.search(n["title"])]
        self._attach_og_images(items, key=lambda n: n.get("url"))
        for n in items:
            # Techmeme summaries start with "Author / Outlet : …" — split that into a byline
            m = re.match(r"^([^:\n]{3,80}?) / ([^:\n]{2,40}?)\s*:\s*(.*)$", n.get("summary") or "", re.S)
            if m:
                n["byline"], n["outlet"], n["summary"] = m.group(1), m.group(2), m.group(3)
        return items

    # ---------- misc ----------
    def log(self, msg: str):
        print("[ui]", msg, flush=True)
        return True

    def open_url(self, url: str):
        if url and url.startswith(("http://", "https://", "mailto:")):
            webbrowser.open(url)
        return True

    def open_data_dir(self):
        paths.open_with_default_app(self._data_dir)
        return str(self._data_dir)

    def export_ics(self, ev: dict):
        def fmt(v, end=False):
            if not v:
                return None
            if "T" in v:
                return ":" + v.replace("-", "").replace(":", "")
            d = datetime.fromisoformat(v) + (timedelta(days=1) if end else timedelta())
            return ";VALUE=DATE:" + d.strftime("%Y%m%d")

        def esc(s):
            return (s or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

        start = fmt(ev.get("start"))
        end = fmt(ev.get("end") or ev.get("start"), end=True)
        where = ", ".join(x for x in (ev.get("venue"), ev.get("city"), ev.get("country")) if x) or \
            ("Online" if ev.get("online") else "")
        body = "\r\n".join([
            "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Etkinlik Radari//TR", "BEGIN:VEVENT",
            f"UID:{re.sub(r'[^A-Za-z0-9]', '', ev['id'])[:60]}@etkinlik-radari",
            f"DTSTAMP:{now().replace('-', '').replace(':', '')}",
            f"DTSTART{start}", f"DTEND{end}", f"SUMMARY:{esc(ev['title'])}",
            f"DESCRIPTION:{esc((ev.get('description') or '')[:900] + chr(10) + ev.get('url', ''))}",
            f"LOCATION:{esc(where)}", f"URL:{ev.get('url', '')}", "END:VEVENT", "END:VCALENDAR", ""])
        folder = paths.downloads_dir()
        name = re.sub(r"[^\w\-]+", "_", ev["title"])[:60] + ".ics"
        path = folder / name
        path.write_text(body, encoding="utf-8", newline="")  # body already uses CRLF
        paths.open_with_default_app(path)  # hands the event to the default calendar app
        return str(path)
