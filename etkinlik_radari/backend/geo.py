"""Country detection (ISO-3166 alpha-2, lower case) for flags, plus the excluded-country filter."""
import re

from .dates import tr_lower

COUNTRIES = {
    "tr": "türkiye, turkey, turkiye, tr",
    "us": "united states, united states of america, usa, us, u.s., america",
    "ca": "canada",
    "mx": "mexico, méxico",
    "gb": "united kingdom, uk, gb, great britain, england, scotland, wales, northern ireland",
    "de": "germany, deutschland, almanya, de",
    "fr": "france, fransa, fr",
    "nl": "netherlands, the netherlands, holland, hollanda, nl",
    "es": "spain, españa, ispanya, es",
    "pt": "portugal, portekiz, pt",
    "it": "italy, italia, italya, it",
    "ch": "switzerland, isviçre, schweiz, suisse, ch",
    "at": "austria, avusturya, österreich, at",
    "be": "belgium, belçika, be",
    "ie": "ireland, irlanda, ie",
    "se": "sweden, isveç, se",
    "no": "norway, norveç",
    "dk": "denmark, danimarka, dk",
    "fi": "finland, finlandiya, fi",
    "ee": "estonia, estonya, ee",
    "lv": "latvia, letonya, lv",
    "lt": "lithuania, litvanya, lt",
    "pl": "poland, polonya, pl",
    "cz": "czechia, czech republic, çekya, cz",
    "sk": "slovakia, slovakya",
    "hu": "hungary, macaristan, hu",
    "ro": "romania, romanya, ro",
    "bg": "bulgaria, bulgaristan, bg",
    "gr": "greece, yunanistan, gr",
    "hr": "croatia, hırvatistan, hr",
    "si": "slovenia, slovenya",
    "rs": "serbia, sırbistan",
    "ua": "ukraine, ukrayna, ua",
    "cy": "cyprus, kıbrıs",
    "mt": "malta",
    "lu": "luxembourg, lüksemburg",
    "is": "iceland, izlanda",
    "ae": "united arab emirates, uae, birleşik arap emirlikleri, bae",
    "sa": "saudi arabia, suudi arabistan, ksa",
    "qa": "qatar, katar",
    "eg": "egypt, mısır",
    "ma": "morocco, fas",
    "ng": "nigeria, nijerya",
    "ke": "kenya",
    "za": "south africa, güney afrika",
    "in": "india, hindistan",
    "sg": "singapore, singapur",
    "jp": "japan, japonya",
    "kr": "south korea, korea, güney kore",
    "cn": "china, çin",
    "hk": "hong kong",
    "tw": "taiwan, tayvan",
    "id": "indonesia, endonezya",
    "my": "malaysia, malezya",
    "th": "thailand, tayland",
    "vn": "vietnam",
    "ph": "philippines, filipinler",
    "au": "australia, avustralya",
    "nz": "new zealand, yeni zelanda",
    "br": "brazil, brasil, brezilya",
    "ar": "argentina, arjantin",
    "cl": "chile, şili",
    "co": "colombia, kolombiya",
    "az": "azerbaijan, azerbaycan",
    "ge": "georgia, gürcistan",
    "kz": "kazakhstan, kazakistan",
    "pk": "pakistan",
}
CITIES = {
    "tr": "istanbul, ankara, izmir, bursa, antalya, kocaeli, eskişehir, konya, kadıköy, beşiktaş, üsküdar, "
          "şişli, sarıyer, maslak, levent, ataşehir, beyoğlu, gaziantep, trabzon, kayseri, mersin, adana",
    "us": "san francisco, sf, new york, nyc, new york city, los angeles, seattle, boston, austin, chicago, miami, "
          "denver, atlanta, houston, dallas, las vegas, palo alto, mountain view, menlo park, san jose, san diego, "
          "salt lake city, philadelphia, washington, washington dc, washington d.c., portland, detroit, nashville, "
          "raleigh, durham, pittsburgh, minneapolis, phoenix, brooklyn, manhattan, oakland, berkeley, santa clara, "
          "sunnyvale, redwood city, half moon bay, orlando, san mateo, burlingame, yountville, cupertino, "
          "new orleans, columbus, baltimore, bay area, silicon valley",
    "ca": "toronto, vancouver, montreal, montréal, ottawa, calgary, waterloo",
    "mx": "mexico city, guadalajara, monterrey",
    "gb": "london, manchester, cambridge, oxford, bristol, edinburgh, birmingham, leeds, glasgow",
    "de": "berlin, munich, münchen, hamburg, frankfurt, cologne, köln, stuttgart, düsseldorf, leipzig, dresden",
    "fr": "paris, lyon, marseille, toulouse, nice, bordeaux, nantes",
    "nl": "amsterdam, rotterdam, utrecht, eindhoven, the hague, delft",
    "es": "madrid, barcelona, valencia, málaga, malaga, seville, bilbao",
    "pt": "lisbon, lisboa, porto",
    "it": "milan, milano, rome, roma, turin, torino",
    "ch": "zurich, zürich, geneva, lausanne, basel",
    "at": "vienna, wien",
    "be": "brussels, antwerp",
    "ie": "dublin",
    "se": "stockholm, malmö, gothenburg",
    "no": "oslo",
    "dk": "copenhagen, aarhus",
    "fi": "helsinki, espoo, tampere",
    "ee": "tallinn",
    "lv": "riga",
    "lt": "vilnius",
    "pl": "warsaw, krakow, kraków",
    "cz": "prague",
    "hu": "budapest",
    "ro": "bucharest, cluj-napoca",
    "bg": "sofia",
    "gr": "athens, thessaloniki",
    "hr": "zagreb",
    "si": "ljubljana",
    "rs": "belgrade",
    "ae": "dubai, abu dhabi",
    "sa": "riyadh, jeddah",
    "qa": "doha",
    "eg": "cairo",
    "ng": "lagos",
    "ke": "nairobi",
    "za": "johannesburg, cape town",
    "in": "bangalore, bengaluru, mumbai, delhi, new delhi, hyderabad, pune, chennai",
    "sg": "singapore",
    "jp": "tokyo, osaka, fukuoka, kyoto",
    "kr": "seoul",
    "cn": "beijing, shanghai, shenzhen",
    "hk": "hong kong",
    "tw": "taipei",
    "id": "jakarta, bali",
    "th": "bangkok",
    "au": "sydney, melbourne, brisbane",
    "br": "são paulo, sao paulo, rio, rio de janeiro",
    "ar": "buenos aires",
    "co": "bogotá, bogota, medellín, medellin",
    "az": "baku, bakü",
}

# Kept out of the app entirely, by country, city or title mention.
EXCLUDED = re.compile(
    r"(?<![\w])(?:israel|israil|i̇srail|tel[ -]?aviv|tel aviv-yafo|jerusalem|kudüs|haifa|hayfa|herzliya|"
    r"ramat gan|be'?er sheva|beersheba|petah tikva|netanya|rehovot|ra'?anana|yokneam|caesarea)(?![\w])", re.I)


def fold(s: str) -> str:
    """Lower-case for lookups: 'Istanbul', 'İSTANBUL' and 'istanbul' all become 'istanbul'."""
    return tr_lower(s).replace("ı", "i")


def _index(table) -> dict:
    out = {}
    for code, names in table.items():
        for n in names.split(","):
            if n.strip():
                out[fold(n.strip())] = code
    return out


COUNTRY_INDEX = _index(COUNTRIES)
CITY_INDEX = _index(CITIES)
_CITY_RX = re.compile(r"(?<![\w])(" + "|".join(sorted(map(re.escape, (c for c in CITY_INDEX if len(c) > 3 or c in ("nyc", "rio"))),
                                                         key=len, reverse=True)) + r")(?![\w])")

_COUNTRY_RX = re.compile(r"(?<![\w])(" + "|".join(sorted(map(re.escape, (c for c in COUNTRY_INDEX if len(c) > 4)),
                                                            key=len, reverse=True)) + r")(?![\w])")


def _pieces(*parts):
    for p in parts:
        if not p:
            continue
        low = fold(str(p)).strip()
        yield low
        for piece in re.split(r"[,/|()·\-–]+", low):
            if piece.strip():
                yield piece.strip()


def country_code(ev: dict) -> str:
    if ev.get("online"):
        return ""
    country = ev.get("country") or ""
    if len(country) == 2 and country.isalpha() and country.lower() in COUNTRIES:  # 'TR', 'DE'
        return country.lower()
    for p in _pieces(country):
        if p in COUNTRY_INDEX:
            return COUNTRY_INDEX[p]
    for p in _pieces(ev.get("city"), ev.get("venue")):
        if p in CITY_INDEX:
            return CITY_INDEX[p]
        if p in COUNTRY_INDEX and len(p) > 2:
            return COUNTRY_INDEX[p]
    title = fold(ev.get("title") or "")
    m = _CITY_RX.search(title)  # "StrictlyVC NYC", "AI Week Frankfurt"
    if m:
        return CITY_INDEX[m.group(1)]
    m = _COUNTRY_RX.search(title)  # "Web Summit Qatar"
    return COUNTRY_INDEX[m.group(1)] if m else ""


def is_excluded(ev: dict) -> bool:
    text = " ".join(str(ev.get(k) or "") for k in ("title", "city", "country", "venue"))
    return bool(EXCLUDED.search(text)) or (ev.get("country") or "").upper() == "IL"
