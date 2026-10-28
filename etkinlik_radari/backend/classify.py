"""Keyword based tagging (Turkish + English): categories, event kind and region."""
import re

from .dates import tr_lower
from .geo import country_code

# id, Turkish label, English label, icon, keywords (regex fragments, matched on word boundaries)
CATEGORIES = [
    ("ai", "Yapay Zekâ", "AI", "cpu", r"ai|a\.i\.|yapay zek[aâ]\w*|llms?|genai|gen ai|machine learning|ml|deep learning|"
     r"neural|nlp|computer vision|agents?|agentic|gpt\w*|openai|anthropic|claude|gemini|"
     r"artificial intelligence|data science|robotics|computer-vision|machine-learning|rag|mlops|"
     r"multimodal|diffusion|transformers?|inference|cvpr|neurips|iclr|icml|aaai|acl|emnlp|eccv|iccv"),
    ("startup", "Girişimcilik", "Startups", "rocket", r"startups?|girişim\w*|founders?|kurucu\w*|entrepreneur\w*|"
     r"incubat\w*|accelerat\w*|kuluçka|hızlandırma|scale-?ups?|yc|y combinator|techstars|"
     r"co-?founder\w*|bootstrapp\w*|unicorns?|ecosystem|ekosistem|innovation|inovasyon|slush|web summit"),
    ("invest", "Yatırım & VC", "Investing & VC", "trending", r"vc|vcs|venture\w*|investors?|investing|investment|yatırım\w*|"
     r"fundrais\w*|angels?|melek|capital|funds?|lps?|fon\w*|private equity|seed|series [abc]|"
     r"strictlyvc|limited partners?|term sheets?"),
    ("fintech", "Fintech", "Fintech", "card", r"fintech|finans\w*|finance|payments?|ödeme\w*|banks?|banka\w*|"
     r"banking|insurtech|wealthtech|regtech|lending|neobank\w*|money"),
    ("crypto", "Kripto & Web3", "Crypto & Web3", "bitcoin", r"crypto\w*|kripto\w*|web3|blockchain|defi|ethereum|eth|bitcoin|"
     r"btc|solana|nfts?|tokens?|onchain|on-chain|dao|stablecoins?|polkadot|zk"),
    ("dev", "Yazılım & Geliştirici", "Software & Dev", "code", r"developers?|dev|devs|yazılım\w*|software|coding|code|"
     r"programming|devops|cloud|kubernetes|k8s|javascript|typescript|python|java|golang|rust|react|"
     r"frontend|backend|api|apis|open source|açık kaynak|engineering|engineers?|mühendis\w*|"
     r"android|ios|mobile|flutter|kotlin|swift|dotnet|\.net|php|sql|database|data engineering|qa|"
     r"testing|architecture|sre|platform engineering|github|copilot|devcon|droidcon|pycon|jsconf"),
    ("security", "Siber Güvenlik", "Cybersecurity", "shield", r"security|siber|cyber\w*|güvenlik|infosec|appsec|ctf|"
     r"pentest\w*|zero trust|privacy"),
    ("product", "Ürün & Tasarım", "Product & Design", "layers", r"product|ürün|design|tasarım|ux|ui|figma|product management|"
     r"user research|prototyp\w*|no-?code|low-?code|vibe coding"),
    ("growth", "Büyüme & Pazarlama", "Growth & Marketing", "megaphone", r"marketing|pazarlama|growth|büyüme|sales|satış|gtm|"
     r"go-to-market|e-?ticaret|e-?commerce|ecommerce|ads|seo|brand\w*|marka|retail|perakende|cx|"
     r"customer|revenue|saas|b2b"),
    ("deeptech", "Deep Tech & Donanım", "Deep Tech & Hardware", "atom", r"deep ?tech|quantum|kuantum|hardware|donanım|space|uzay|"
     r"semiconductors?|chips?|robot\w*|drones?|defen[cs]e|savunma|iot|manufacturing|üretim|automotive|"
     r"otomotiv|mobility|mobilite|biotech"),
    ("health", "Sağlık & Biyotek", "Health & Biotech", "heart", r"health\w*|sağlık|medtech|biotech|bio|life sciences?|pharma|"
     r"medical|medikal|clinical|healthcare|wellness"),
    ("climate", "İklim & Enerji", "Climate & Energy", "leaf", r"climate|iklim|energy|enerji|sustainab\w*|sürdürülebilir\w*|"
     r"cleantech|green|yeşil|carbon|karbon|solar|agri\w*|tarım|food ?tech|foodhack"),
    ("research", "Akademik & Araştırma", "Academic & Research", "cap", r"research|araştırma|academic|akademik|papers?|"
     r"symposium|sempozyum|proceedings|research"),
    # ---- culture & arts ----
    ("music", "Müzik & Konser", "Music & Concerts", "music", r"konser\w*|concerts?|music|müzik\w*|caz|jazz|rock|"
     r"rap|hip-?hop|orkestra\w*|orchestra\w*|senfoni\w*|symphon\w*|resital|recital|dj|techno|live music|"
     r"canlı müzik|klasik müzik|classical music|choir|koro\w*|türkü\w*|fasıl|şarkı\w*|singer|şarkıcı|"
     r"album|albüm|gigs?|band"),
    ("stage", "Tiyatro & Sahne", "Theatre & Stage", "ticket", r"tiyatro\w*|theat(?:re|er)\w*|stand-?up|"
     r"komedi\w*|comedy|comedian|bale\w*|ballet|dans\w*|dance\w*|opera\w*|müzikal\w*|musicals?|"
     r"gösteri\w*|sahne\w*|performance art|circus|sirk\w*|improv\w*|doğaçlama|monolog\w*|kukla\w*|"
     r"puppet\w*|illüzyon\w*|magic show"),
    ("art", "Sanat & Sergi", "Art & Exhibitions", "palette", r"sergi\w*|exhibitions?|exhibit|art|arts|"
     r"sanat\w*|gallery|galleries|galeri\w*|müze\w*|museums?|bienal\w*|biennial|biennale|painting|"
     r"resim|fotoğraf\w*|photography|heykel\w*|sculpture|art fair|vernissage|contemporary art|"
     r"çağdaş sanat|seramik\w*|ceramics?|illustration|illüstrasyon\w*"),
    ("film", "Sinema & Film", "Film & Cinema", "film", r"film\w*|sinema\w*|cinema|movies?|screenings?|"
     r"gösterim\w*|belgesel\w*|documentar\w*|short film|kısa film"),
    ("lit", "Edebiyat & Söyleşi", "Books & Talks", "book", r"kitap\w*|edebiyat\w*|literature|literary|"
     r"şiir\w*|poetry|poets?|yazar\w*|authors?|imza günü|book launch|book club|novels?|romanı"),
    ("family", "Çocuk & Aile", "Kids & Family", "smile", r"çocuk\w*|children|kids|family-friendly|"
     r"family show|aile\w*|masal\w*|minik\w*|bebek\w*|toddlers?"),
]
CULTURE_CATS = {"music", "stage", "art", "film", "lit", "family"}
DOMAINS = [("tech", "Teknoloji & Girişim", "Tech & Startups", "briefcase"),
           ("culture", "Kültür & Sanat", "Culture & Arts", "palette")]
# where a source's events belong; sources missing here (Luma, a city mix) are decided per event
SOURCE_DOMAIN = {"biletix": "culture", "etkinlikio": "culture", "biletinial": "culture", "eventbrite": "culture", "izmir": "culture",
                 "foundercal": "tech", "techmeme": "tech", "dealroom": "tech", "cerebral": "tech",
                 "techcrunch": "tech", "slush": "tech", "websummit": "tech", "devpost": "tech",
                 "devevents": "tech", "aideadlines": "tech", "webrazzi": "tech", "itu": "tech"}
CAT_RX = {cid: re.compile(r"(?<![\w])(?:" + kw + r")(?![\w])", re.I) for cid, _, _, _, kw in CATEGORIES}

KINDS = [
    ("hackathon", "Hackathon", "Hackathon", "zap", r"hackathons?|hack|hacknight|buildathon|game jam|jam|ideathon|datathon|ctf"),
    ("demoday", "Demo Day & Pitch", "Demo Day & Pitch", "presentation", r"demo ?days?|pitch\w*|demo night|investor day|showcase"),
    ("workshop", "Workshop & Eğitim", "Workshop & Training", "wrench", r"workshops?|atölye\w*|masterclass|bootcamp|training|eğitim\w*|"
     r"course|kurs|office hours|clinic|lab|101|hands-on|tutorial"),
    ("webinar", "Webinar", "Webinar", "video", r"webinars?|online talk|livestream|canlı yayın|virtual summit"),
    ("concert", "Konser", "Concert", "music", r"konser\w*|concerts?|live music|canlı müzik|gigs?|resital|recital|"
     r"dj set|senfoni\w*|symphony"),
    ("show", "Gösteri & Oyun", "Show & Play", "ticket", r"tiyatro\w*|theat(?:re|er)|stand-?up|gösteri\w*|bale|"
     r"ballet|opera|müzikal|musical|comedy|komedi\w*|oyunu|sahne\w*"),
    ("exhibition", "Sergi & Müze", "Exhibition & Museum", "image", r"sergi\w*|exhibitions?|exhibit|müze\w*|"
     r"museums?|gallery|galeri\w*|bienal\w*|biennale|art fair"),
    ("screening", "Film Gösterimi", "Screening", "film", r"screenings?|gösterim\w*|film gösterimi|sinema\w*|cinema"),
    ("festival", "Festival", "Festival", "tent", r"festival\w*|fest|fests"),
    ("conference", "Konferans & Zirve", "Conference & Summit", "mic", r"conferences?|konferans\w*|summit|zirve\w*|forum|expo|"
     r"week|haftası|congress|kongre|con|devcon|world|days|fuar\w*|symposium|sempozyum|"
     r"conf|convention"),
    ("meetup", "Meetup & Networking", "Meetup & Networking", "users", r"meetups?|buluşma\w*|networking|happy hour|dinner|akşam yemeği|"
     r"breakfast|kahvaltı|coffee|kahve|brunch|lunch|mixer|social|party|run club|running club|"
     r"talks?|söyleşi|sohbet|panel|fireside|night|gathering|coworking|co-working|community"),
]
KIND_RX = {kid: re.compile(r"(?<![\w])(?:" + kw + r")(?![\w])", re.I) for kid, _, _, _, kw in KINDS}
CULTURE_KINDS = {"concert", "show", "exhibition", "screening", "festival"}

REGIONS = [("turkey", "Türkiye", "Türkiye", "flag:tr"), ("europe", "Avrupa", "Europe", "flag:eu"),
           ("namerica", "Kuzey Amerika", "North America", "flag:us+ca"), ("online", "Online", "Online", "globe"),
           ("other", "Diğer", "Elsewhere", "earth")]


def labels(table, lang="tr") -> dict:
    """id -> label in the UI language (tables hold Turkish at [1] and English at [2])."""
    return {row[0]: row[2 if lang == "en" else 1] for row in table}

TR_PLACES = {"türkiye", "turkey", "tr", "turkiye", "istanbul", "i̇stanbul", "ankara", "izmir", "bursa",
             "antalya", "kocaeli", "eskişehir", "konya", "kadıköy", "beşiktaş", "üsküdar", "şişli",
             "sarıyer", "maslak", "levent", "ataşehir", "beyoğlu", "gaziantep", "trabzon", "kayseri"}

def _places(s: str) -> set:
    return {p.strip() for p in s.split(",") if p.strip()}


EU_PLACES = _places("""
albania, andorra, austria, belgium, bulgaria, croatia, cyprus, czechia, czech republic, denmark, estonia,
finland, france, germany, greece, hungary, iceland, ireland, italy, latvia, lithuania, luxembourg, malta,
monaco, montenegro, netherlands, the netherlands, norway, poland, portugal, romania, serbia, slovakia,
slovenia, spain, sweden, switzerland, ukraine, uk, gb, de, fr, nl, es, it, pt, se, fi, dk, no, pl, ie, at,
ch, be, cz, gr, ro, hu, bg, hr, ee, lv, lt, united kingdom, england, scotland, wales, europe,
london, berlin, paris, amsterdam, munich, münchen, hamburg, frankfurt, cologne, köln, vienna, wien, zurich,
zürich, geneva, lisbon, porto, madrid, barcelona, valencia, milan, rome, turin, stockholm, copenhagen, oslo,
helsinki, tallinn, riga, vilnius, warsaw, krakow, kraków, prague, budapest, bucharest, sofia, athens,
thessaloniki, dublin, brussels, antwerp, rotterdam, utrecht, eindhoven, lyon, marseille, toulouse, nice,
bordeaux, lausanne, basel, edinburgh, manchester, cambridge, oxford, bristol, belgrade, zagreb, ljubljana,
malmö, gothenburg, aarhus, espoo, tampere, stuttgart, düsseldorf, leipzig, dresden, the hague, delft""")
NA_PLACES = _places("""
usa, us, united states, united states of america, canada, mexico, sf, nyc, san francisco, new york,
new york city, los angeles, seattle, boston, austin, chicago, miami, denver, atlanta, houston, dallas,
toronto, vancouver, montreal, montréal, las vegas, palo alto, mountain view, menlo park, san jose,
san diego, salt lake city, philadelphia, washington, washington dc, washington d.c., portland, detroit,
nashville, raleigh, durham, pittsburgh, minneapolis, phoenix, brooklyn, manhattan, oakland, berkeley,
santa clara, sunnyvale, redwood city, half moon bay, mexico city, ottawa, calgary, waterloo, bay area,
silicon valley, orlando, san mateo, burlingame, yountville, cupertino, new orleans, columbus, baltimore""")
US_STATE = re.compile(r",\s*(?:[A-Z]{2}|California|Texas|Florida|Nevada|Massachusetts|Washington|New York)\s*$")


def _place_tokens(*parts) -> set:
    out = set()
    for p in parts:
        if not p:
            continue
        low = tr_lower(p)
        out.add(low.strip())
        for piece in re.split(r"[,/|()·\-–]+", low):
            piece = piece.strip()
            if piece:
                out.add(piece)
    return out


def _title_rx(places, extra=()) -> re.Pattern:
    # skip 2-3 letter country codes ("de", "it", "us") which are ordinary words in titles
    names = sorted({p for p in places if len(p) > 3} | set(extra), key=len, reverse=True)
    return re.compile(r"(?<![\w])(?:" + "|".join(map(re.escape, names)) + r")(?![\w])")


TITLE_RX = [("turkey", _title_rx(TR_PLACES)), ("europe", _title_rx(EU_PLACES)),
            ("namerica", _title_rx(NA_PLACES, extra=("nyc", "sf", "usa")))]


EUROPE_CC = {"gb", "de", "fr", "nl", "es", "pt", "it", "ch", "at", "be", "ie", "se", "no", "dk", "fi", "ee", "lv",
             "lt", "pl", "cz", "sk", "hu", "ro", "bg", "gr", "hr", "si", "rs", "ua", "cy", "mt", "lu", "is"}


def region_of(ev) -> str:
    if ev.get("online"):
        return "online"
    cc = ev.get("cc") or country_code(ev)
    if cc:
        return "turkey" if cc == "tr" else "europe" if cc in EUROPE_CC else             "namerica" if cc in ("us", "ca", "mx") else "other"
    city = "" if (ev.get("city") or "").lower() in ("other", "tba", "tbd") else ev.get("city")
    tokens = _place_tokens(city, ev.get("country"), ev.get("venue"))
    if tokens & TR_PLACES:
        return "turkey"
    if tokens & EU_PLACES:
        return "europe"
    if tokens & NA_PLACES or US_STATE.search(city or ""):
        return "namerica"
    title = tr_lower(ev.get("title", ""))
    for region, rx in TITLE_RX:  # e.g. "StrictlyVC NYC 2026", "AI Week Frankfurt"
        if rx.search(title):
            return region
    if re.search(r"\b(online|virtual)\b", title):
        return "online"
    return "other"


def categorize(ev) -> list[str]:
    tags = [str(t) for t in ev.get("tags") or []]
    text = " ".join([ev.get("title", ""), ev.get("title", ""), ev.get("description", "")[:600],
                     " ".join(t for t in tags if not t.startswith("cat:")), ev.get("extra", {}).get("calendar", "")])
    text = text.replace("İ", "i")
    # a theatre play mentioning "girişim" is not a startup event, and vice versa
    domain = SOURCE_DOMAIN.get(ev.get("source"))
    allowed = (lambda c: c in CULTURE_CATS) if domain == "culture" else         (lambda c: c not in CULTURE_CATS) if domain == "tech" else (lambda c: True)
    cats = [t[4:] for t in tags if t.startswith("cat:")]  # set by the source itself
    cats += [cid for cid, rx in CAT_RX.items() if cid not in cats and allowed(cid) and rx.search(text)]
    if ev.get("source") == "aideadlines" and "research" not in cats:
        cats.append("research")
    return cats


def domain_of(ev) -> str:
    fixed = SOURCE_DOMAIN.get(ev.get("source"))
    if fixed:
        return fixed
    cats = ev.get("categories") or []
    if cats and all(c in CULTURE_CATS for c in cats):
        return "culture"
    return "culture" if not cats and ev.get("kind") in CULTURE_KINDS else "tech"


def kind_of(ev) -> str:
    hint = (ev.get("kind_hint") or "").lower()
    for kid, rx in KIND_RX.items():
        if hint == kid or rx.fullmatch(hint or "-"):
            return kid
    text = (ev.get("title", "") + " " + (ev.get("description", "") or "")[:200]).replace("İ", "i")
    title = ev.get("title", "").replace("İ", "i")
    for kid, rx in KIND_RX.items():  # title wins over description
        if rx.search(title):
            return kid
    for kid, rx in KIND_RX.items():
        if rx.search(text):
            return kid
    if SOURCE_DOMAIN.get(ev.get("source")) == "culture":
        return "show"
    return "conference" if ev.get("importance", 0) >= 70 else "meetup"


STOP = set("""the and for with from your you our are this that into about over what how why who all new
event events edition annual day days 2025 2026 2027 2028 ile için bir ve bu da de etkinliği etkinlik etkinliği
istanbul online meetup summit conference week talks night global world international vol part series
""".split())


def keywords(title: str) -> list[str]:
    words = re.findall(r"[a-zçğıöşü0-9][a-zçğıöşü0-9+.#-]{2,}", tr_lower(title))
    return sorted({w.strip(".-") for w in words if w not in STOP and not w.isdigit()})[:8]
