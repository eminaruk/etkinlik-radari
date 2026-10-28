"""Personal relevance + importance scoring with human readable reasons.

Learned weights are recomputed from the interactions table every time, so un-liking an
event fully reverts its effect."""
import math
from collections import defaultdict

from .classify import CATEGORIES, KINDS, REGIONS, labels

REGION_LOCATIVE = {
    "tr": {"turkey": "Türkiye'de", "europe": "Avrupa'da", "namerica": "Kuzey Amerika'da",
           "online": "Online katılım", "other": "Dünyada"},
    "en": {"turkey": "In Türkiye", "europe": "In Europe", "namerica": "In North America",
           "online": "Join online", "other": "Worldwide"},
}
REASONS = {
    "tr": {"cat": "{} ilgini çekiyor", "kind": "{} seviyorsun", "similar": "Beğendiklerine benziyor",
           "flagship": "Amiral etkinlik", "curated": "Küratörlü / büyük etkinlik", "guests": "{} katılımcı",
           "prize": "{} ödül"},
    "en": {"cat": "You're into {}", "kind": "You like {}", "similar": "Similar to what you liked",
           "flagship": "Flagship event", "curated": "Curated / major event", "guests": "{} attendees",
           "prize": "{} in prizes"},
}

ACTION_VALUE = {"like": 1.0, "save": 0.7, "attended": 1.2, "dislike": -1.3}
FEATURE_SCALE = {"cat": 0.9, "kind": 0.6, "region": 0.5, "src": 0.35, "kw": 0.4}
LEVEL_WEIGHT = {"cat": 1.3, "kind": 0.9, "region": 1.1}  # explicit profile sliders (-1..2)
TECH_FLAGSHIP = ("slush", "web summit", "disrupt", "websummit", "webrazzi summit", "founder summit",
                 "neurips", "icml", "iclr", "cvpr", "y combinator", "a16z", "sequoia", "techcrunch")
CULTURE_FLAGSHIP = ("film festivali", "caz festivali", "müzik festivali", "tiyatro festivali", "istanbul bienali",
                    "i̇stanbul bienali", "contemporary istanbul", "art basel", "frieze", "biennale", "documenta",
                    "filmekimi", "berlinale", "glastonbury", "primavera sound", "sónar", "salzburg festival",
                    "edinburgh festival", "fringe festival", "istanbul modern", "senfoni orkestrası")


def features(ev) -> list[str]:
    f = [f"cat:{c}" for c in ev["categories"]] + [f"kind:{ev['kind']}", f"region:{ev['region']}",
                                                  f"src:{ev['source']}"]
    return f + [f"kw:{k}" for k in ev["keywords"]]


def learned_weights(events_by_id: dict, interactions: list[tuple[str, str]]) -> dict:
    w = defaultdict(float)
    for event_id, action in interactions:
        ev = events_by_id.get(event_id)
        val = ACTION_VALUE.get(action)
        if ev is None or val is None:
            continue
        for feat in features(ev):
            w[feat] += val
    return dict(w)


# major Turkish stages and arenas; a show booked there is usually a big one
BIG_VENUES = ("zorlu psm", "harbiye", "cemil topuzlu", "volkswagen arena", "ülker sports", "küçükçiftlik",
              "atatürk kültür merkezi", "akm", "cso ada", "süreyya operası", "crr konser", "ankara arena",
              "kültürpark", "uniq hall", "life park", "if performance", "congresium", "bostancı gösteri")


def importance(ev) -> int:
    imp = ev.get("importance", 40)
    title = ev["title"].lower()
    culture = ev.get("domain") == "culture"
    if any(w in title for w in (CULTURE_FLAGSHIP if culture else TECH_FLAGSHIP)):
        imp = max(imp, 88)
    if culture:
        # ticketing sources rate every show the same; popularity shows up as cross-listing, venue size and runs
        x = ev.get("extra") or {}
        imp += min(12, 6 * len(ev.get("also") or []))
        if any(v in (ev.get("venue") or "").lower() for v in BIG_VENUES):
            imp += 14
        if (x.get("performances") or 0) >= 8:
            imp += 6
        if x.get("sold_out"):
            imp += 8
    return max(0, min(100, imp))


def score(ev, profile: dict, learned: dict, lang: str = "tr") -> tuple[int, int, list[str]]:
    """Returns (score 0-100, importance 0-100, reasons in the UI language)."""
    lang = lang if lang in REASONS else "tr"
    say = REASONS[lang]
    cat_label, kind_label, region_label = labels(CATEGORIES, lang), labels(KINDS, lang), labels(REGIONS, lang)
    contrib = []  # (value, reason or None)
    levels = profile.get("interests", {})
    for c in ev["categories"]:
        lvl = levels.get(c, 0)
        if lvl:
            contrib.append((lvl * LEVEL_WEIGHT["cat"], say["cat"].format(cat_label[c]) if lvl > 0 else None))
    lvl = profile.get("kinds", {}).get(ev["kind"], 0)
    if lvl:
        contrib.append((lvl * LEVEL_WEIGHT["kind"], say["kind"].format(kind_label[ev["kind"]]) if lvl > 0 else None))
    lvl = profile.get("regions", {}).get(ev["region"], 0)
    if lvl:
        where = REGION_LOCATIVE[lang][ev["region"]]
        contrib.append((lvl * LEVEL_WEIGHT["region"], where if lvl > 0 else None))

    learned_total = 0.0
    best_learned = (0.0, None)
    for feat in features(ev):
        w = learned.get(feat)
        if not w:
            continue
        kind, _, val = feat.partition(":")
        v = FEATURE_SCALE[kind] * 2 * math.tanh(w / 3)
        learned_total += v
        if v > best_learned[0]:
            label = {"cat": cat_label.get(val), "kind": kind_label.get(val),
                     "region": region_label.get(val), "src": None, "kw": f"“{val}”"}.get(kind)
            best_learned = (v, f"{say['similar']} ({label})" if label else say["similar"])
    if learned_total:
        contrib.append((learned_total, best_learned[1] if best_learned[0] > 0.3 else None))

    pref = sum(v for v, _ in contrib)
    pref_score = 50 + 50 * math.tanh(pref / 3.5)
    imp = importance(ev)
    total = round(0.6 * pref_score + 0.4 * imp)

    reasons = [r for v, r in sorted(contrib, key=lambda x: -x[0]) if r and v > 0][:2]
    if imp >= 85:
        reasons.insert(0, say["flagship"])
    elif imp >= 70:
        reasons.append(say["curated"])
    if (ev.get("guest_count") or 0) >= 150 and ev["source"] == "luma":
        reasons.append(say["guests"].format(ev["guest_count"]))
    if ev.get("extra", {}).get("prize"):
        reasons.append(say["prize"].format(ev["extra"]["prize"]))
    return max(0, min(100, total)), imp, reasons[:3]
